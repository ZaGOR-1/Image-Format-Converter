"""Batch conversion result tracking."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class JobError:
    """A failed file and the reason it failed."""

    file_path: Path
    reason: str


@dataclass
class JobResult:
    """Track aggregate results for a conversion batch."""

    total_found: int = 0
    converted: int = 0
    failed: int = 0
    skipped: int = 0
    errors: list[JobError] = field(default_factory=list)

    def record_success(self) -> None:
        """Record one successfully converted file."""
        self.converted += 1

    def record_failure(self, file_path: Path, reason: str) -> None:
        """Record one failed file with a human-readable reason."""
        self.failed += 1
        self.errors.append(JobError(file_path=file_path, reason=reason))

    def record_skip(self) -> None:
        """Record one skipped file."""
        self.skipped += 1

    @property
    def has_failures(self) -> bool:
        """Return whether the batch has any failed files."""
        return self.failed > 0

    def summary(self) -> str:
        """Return a concise final summary for console output."""
        lines = [
            f"Total files found: {self.total_found}",
            f"Converted: {self.converted}",
            f"Failed: {self.failed}",
            f"Skipped: {self.skipped}",
        ]

        if self.errors:
            lines.append("Failed files:")
            lines.extend(
                f"- {error.file_path}: {error.reason}" for error in self.errors
            )

        return "\n".join(lines)
