"""Tests for Fluent solution-data validation."""

from types import SimpleNamespace

import numpy as np
import pytest

from simulation.validation import (
    ValidationError,
    validate_linear_conduction,
)


class FakeSolutionVariableInfo:
    def __init__(self, dimension: int = 3) -> None:
        self.dimension = dimension

    def get_variables_info(
        self,
        *,
        zone_names: list[str],
        domain_name: str,
    ) -> dict[str, SimpleNamespace]:
        assert zone_names == ["solid_zone"]
        assert domain_name == "mixture"
        return FakeVariableMetadata(self.dimension)


class FakeVariableMetadata:
    def __init__(self, dimension: int) -> None:
        self.solution_variables = ["SV_CENTROID", "SV_T"]
        self.variables = {
            "SV_CENTROID": SimpleNamespace(
                dimension=dimension
            ),
            "SV_T": SimpleNamespace(),
        }

    def __getitem__(self, variable_name: str) -> SimpleNamespace:
        return self.variables[variable_name]


class FakeSolutionVariableData:
    def __init__(
        self,
        temperatures: np.ndarray | None = None,
        centroids: np.ndarray | None = None,
    ) -> None:
        self.requests: list[tuple[str, list[str], str]] = []
        self.temperatures = (
            np.array([375.0, 325.0])
            if temperatures is None
            else temperatures
        )
        self.centroids = (
            np.array(
                [[0.25, 0.0, 0.0], [0.75, 0.0, 0.0]]
            )
            if centroids is None
            else centroids
        )

    def get_data(
        self,
        solution_variable_name: str,
        zone_names: list[str],
        domain_name: str = "mixture",
    ) -> dict[str, np.ndarray]:
        self.requests.append(
            (solution_variable_name, zone_names, domain_name)
        )

        values = {
            "SV_T": self.temperatures,
            "SV_CENTROID": self.centroids,
        }
        return {zone_names[0]: values[solution_variable_name]}


def _make_case(
    *,
    axis: str = "x",
) -> SimpleNamespace:
    return SimpleNamespace(
        validation=SimpleNamespace(
            type="linear_conduction",
            start_boundary="hot",
            end_boundary="cold",
            axis=axis,
            start_coordinate=0.0,
            end_coordinate=1.0,
            tolerance=0.1,
        ),
        boundary_conditions=(
            SimpleNamespace(
                name="hot",
                type="temperature",
                value=400.0,
            ),
            SimpleNamespace(
                name="cold",
                type="temperature",
                value=300.0,
            ),
        ),
        domain=SimpleNamespace(zone="solid_zone"),
    )


def _make_session(
    *,
    temperatures: np.ndarray | None = None,
    centroids: np.ndarray | None = None,
    dimension: int = 3,
) -> tuple[SimpleNamespace, FakeSolutionVariableData]:
    solution_data = FakeSolutionVariableData(
        temperatures=temperatures,
        centroids=centroids,
    )
    session = SimpleNamespace(
        fields=SimpleNamespace(
            solution_variable_info=FakeSolutionVariableInfo(
                dimension=dimension
            ),
            solution_variable_data=solution_data,
        )
    )
    return session, solution_data


def test_exact_linear_temperature_field_passes() -> None:
    session, _ = _make_session()

    result = validate_linear_conduction(session, _make_case())

    assert result.sample_count == 2
    assert result.passed
    assert result.max_abs_error == pytest.approx(0.0)


def test_temperature_field_outside_tolerance_fails() -> None:
    session, _ = _make_session(
        temperatures=np.array([390.0, 325.0])
    )

    result = validate_linear_conduction(session, _make_case())

    assert not result.passed
    assert result.max_abs_error == pytest.approx(15.0)


def test_reads_temperature_and_centroids_using_pyfluent_api() -> None:
    session, solution_data = _make_session()

    validate_linear_conduction(session, _make_case())

    assert solution_data.requests == [
        ("SV_T", ["solid_zone"], "mixture"),
        ("SV_CENTROID", ["solid_zone"], "mixture"),
    ]


def test_invalid_centroid_dimension_raises_validation_error() -> None:
    session, _ = _make_session(dimension=4)

    with pytest.raises(
        ValidationError,
        match="Unsupported centroid dimension",
    ):
        validate_linear_conduction(session, _make_case())


def test_axis_unavailable_for_centroid_dimension_raises_validation_error() -> None:
    session, _ = _make_session(
        centroids=np.array([[0.25, 0.0], [0.75, 0.0]]),
        dimension=2,
    )

    with pytest.raises(
        ValidationError,
        match="not available for 2D centroid data",
    ):
        validate_linear_conduction(
            session,
            _make_case(axis="z"),
        )


def test_unknown_validation_axis_raises_validation_error() -> None:
    session, _ = _make_session()

    with pytest.raises(
        ValidationError,
        match="Unsupported validation axis",
    ):
        validate_linear_conduction(
            session,
            _make_case(axis="q"),
        )