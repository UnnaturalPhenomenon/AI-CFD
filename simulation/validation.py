"""Physics validation for Fluent reference cases."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from simulation.case_config import CaseConfig


class ValidationError(RuntimeError):
    """Raised when physics validation cannot be performed."""


@dataclass(frozen=True)
class ValidationResult:
    sample_count: int

    max_abs_error: float
    mean_abs_error: float
    rmse: float

    tolerance: float

    worst_coordinate: float
    worst_numerical_temperature: float
    worst_expected_temperature: float

    passed: bool


def _get_boundary_temperature(
    config: CaseConfig,
    boundary_name: str,
) -> float:
    """Return the temperature value for a named YAML boundary."""

    for boundary in config.boundary_conditions:
        if boundary.name != boundary_name:
            continue

        if boundary.type != "temperature":
            raise ValidationError(
                f"Boundary '{boundary_name}' "
                "is not a temperature boundary."
            )

        return boundary.value

    raise ValidationError(
        f"Boundary '{boundary_name}' "
        "was not found in the case configuration."
    )


def _reshape_centroids(
    centroid_data: Any,
    dimension: int,
) -> np.ndarray:
    """Normalize Fluent centroid data to shape (N, dimension)."""

    centroids = np.asarray(
        centroid_data,
        dtype=float,
    )

    if dimension not in {2, 3}:
        raise ValidationError(
            f"Unsupported centroid dimension: {dimension}"
        )

    if centroids.ndim == 1:
        if centroids.size % dimension != 0:
            raise ValidationError(
                "SV_CENTROID data size is not divisible "
                f"by its dimension ({dimension})."
            )

        centroids = centroids.reshape(
            -1,
            dimension,
        )

    elif centroids.ndim == 2:
        if centroids.shape[1] != dimension:
            raise ValidationError(
                "SV_CENTROID shape does not match "
                f"its dimension ({dimension})."
            )

    else:
        raise ValidationError(
            "Unexpected SV_CENTROID data shape."
        )

    return centroids


def _read_zone_solution(
    session: Any,
    zone_name: str,
) -> tuple[np.ndarray, np.ndarray]:
    """Read cell centroids and temperatures from a Fluent zone."""

    info = session.fields.solution_variable_info

    variables = info.get_variables_info(
        zone_names=[zone_name],
        domain_name="mixture",
    )

    available = set(
        variables.solution_variables
    )

    required = {
        "SV_CENTROID",
        "SV_T",
    }

    missing = required - available

    if missing:
        raise ValidationError(
            "Required Fluent solution variables "
            f"are unavailable: {sorted(missing)}"
        )

    centroid_info = variables["SV_CENTROID"]

    if centroid_info is None:
        raise ValidationError(
            "SV_CENTROID metadata is unavailable."
        )

    centroid_dimension = centroid_info.dimension
    print(
        "[VALIDATION] centroid dimension = "
        f"{centroid_dimension}"
    )

    data = session.fields.solution_variable_data

    temperature_data = data.get_data(
        solution_variable_name="SV_T",
        zone_names=[zone_name],
        domain_name="mixture",
    )

    centroid_data = data.get_data(
        solution_variable_name="SV_CENTROID",
        zone_names=[zone_name],
        domain_name="mixture",
    )

    temperatures = np.asarray(
        temperature_data[zone_name],
        dtype=float,
    ).reshape(-1)

    centroids = _reshape_centroids(
        centroid_data[zone_name],
        dimension=centroid_dimension,
    )

    if temperatures.size != centroids.shape[0]:
        raise ValidationError(
            "Temperature and centroid counts do not match: "
            f"{temperatures.size} temperatures vs "
            f"{centroids.shape[0]} centroids."
        )

    if temperatures.size == 0:
        raise ValidationError(
            "No temperature data was returned."
        )

    return centroids, temperatures


def validate_linear_conduction(
    session: Any,
    config: CaseConfig,
) -> ValidationResult:
    """Compare Fluent temperatures against the analytical 1-D solution."""

    validation = config.validation

    if validation.type != "linear_conduction":
        raise ValidationError(
            f"Unsupported validation type: "
            f"{validation.type}"
        )

    if validation.axis not in {"x", "y", "z"}:
        raise ValidationError(
            f"Unsupported validation axis: "
            f"{validation.axis}"
        )

    start_temperature = _get_boundary_temperature(
        config,
        validation.start_boundary,
    )

    end_temperature = _get_boundary_temperature(
        config,
        validation.end_boundary,
    )

    centroids, temperatures = _read_zone_solution(
        session=session,
        zone_name=config.domain.zone,
    )

    axis_index = {
        "x": 0,
        "y": 1,
        "z": 2,
    }.get(validation.axis)

    if axis_index is None:
        raise ValidationError(
            f"Unsupported validation axis: "
            f"{validation.axis}"
        )

    if axis_index >= centroids.shape[1]:
        raise ValidationError(
            f"Validation axis '{validation.axis}' "
            f"is not available for "
            f"{centroids.shape[1]}D centroid data."
        )
    
    coordinates = centroids[:, axis_index]

    length = (
        validation.end_coordinate
        - validation.start_coordinate
    )

    expected = (
        start_temperature
        + (
            end_temperature
            - start_temperature
        )
        * (
            coordinates
            - validation.start_coordinate
        )
        / length
    )

    errors = np.abs(
        temperatures - expected
    )

    max_index = int(
        np.argmax(errors)
    )

    max_abs_error = float(
        errors[max_index]
    )

    mean_abs_error = float(
        np.mean(errors)
    )

    rmse = float(
        np.sqrt(
            np.mean(
                (temperatures - expected) ** 2
            )
        )
    )

    return ValidationResult(
        sample_count=int(
            temperatures.size
        ),
        max_abs_error=max_abs_error,
        mean_abs_error=mean_abs_error,
        rmse=rmse,
        tolerance=validation.tolerance,
        worst_coordinate=float(
            coordinates[max_index]
        ),
        worst_numerical_temperature=float(
            temperatures[max_index]
        ),
        worst_expected_temperature=float(
            expected[max_index]
        ),
        passed=(
            max_abs_error
            <= validation.tolerance
        ),
    )


def print_validation_result(
    result: ValidationResult,
) -> None:
    """Print a compact physics-validation report."""

    status = (
        "PASS"
        if result.passed
        else "FAIL"
    )

    print()
    print("[VALIDATION]")
    print(
        f"  samples          : "
        f"{result.sample_count}"
    )
    print(
        f"  max abs error    : "
        f"{result.max_abs_error:.6e} K"
    )
    print(
        f"  mean abs error   : "
        f"{result.mean_abs_error:.6e} K"
    )
    print(
        f"  RMSE             : "
        f"{result.rmse:.6e} K"
    )
    print(
        f"  tolerance        : "
        f"{result.tolerance:.6e} K"
    )
    print(
        f"  worst coordinate : "
        f"{result.worst_coordinate:.6f} m"
    )
    print(
        f"  numerical T      : "
        f"{result.worst_numerical_temperature:.6f} K"
    )
    print(
        f"  analytical T     : "
        f"{result.worst_expected_temperature:.6f} K"
    )
    print(
        f"  status           : "
        f"{status}"
    )
    print()