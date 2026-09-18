"""Small, safely managed entry point for PyFluent solver sessions."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Callable, Iterator


@dataclass(frozen=True)
class FluentLaunchConfig:
    """The intentionally small launch configuration used by the smoke test."""

    product_version: str = "24.2.0"
    version: str = "2d"
    precision: str = "double"
    processor_count: int = 1
    start_transcript: bool = False
    show_gui: bool = False
    mode: str = "solver"

    def launch_kwargs(self) -> dict[str, Any]:
        """Translate stable application settings to the installed PyFluent API."""
        if self.version != "2d":
            raise ValueError("Only the 2d solver session is supported by this smoke test.")
        return {
            "product_version": self.product_version,
            "dimension": 2,
            "precision": self.precision,
            "processor_count": self.processor_count,
            "ui_mode": "no_gui" if not self.show_gui else "gui",
            "mode": self.mode,
            "start_transcript": self.start_transcript,
        }


Launcher = Callable[..., Any]


def _default_launcher(**kwargs: Any) -> Any:
    """Import PyFluent lazily so unit tests never require or start Fluent."""
    from ansys.fluent.core import launch_fluent

    return launch_fluent(**kwargs)


def _terminate(session: Any) -> None:
    """Close a PyFluent session using its public shutdown method."""
    session.exit()


@contextmanager
def managed_solver_session(
    config: FluentLaunchConfig | None = None,
    *,
    launcher: Launcher | None = None,
) -> Iterator[Any]:
    """Launch a solver session and guarantee its termination on every exit path."""
    selected_config = config or FluentLaunchConfig()
    selected_launcher = launcher or _default_launcher
    session = selected_launcher(**selected_config.launch_kwargs())
    try:
        yield session
    finally:
        _terminate(session)
