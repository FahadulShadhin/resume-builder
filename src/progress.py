from __future__ import annotations

from types import TracebackType


class ProgressBar:
    """A minimal single-line progress bar that updates in place."""

    def __init__(self, label: str, width: int = 30) -> None:
        self.label = label
        self.width = width
        self._finished = False

    def _render(self, fraction: float) -> None:
        fraction = min(max(fraction, 0.0), 1.0)
        filled = int(self.width * fraction)
        bar = "█" * filled + "-" * (self.width - filled)
        print(f"\r{self.label}: [{bar}]", end="", flush=True)

    def update(self, fraction: float = 1.0) -> None:
        if not self._finished:
            self._render(fraction)

    def finish(self) -> None:
        if self._finished:
            return
        self._render(1.0)
        print(" ✓", flush=True)
        self._finished = True

    def __enter__(self) -> ProgressBar:
        self._render(0.0)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if exc_type is None:
            self.finish()
