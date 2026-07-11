"""ZYNTH's flagship owned-IP project — context every agent should be aware of.

Unlike client work, this isn't passed in via ``client_brief``; it's a fixed
piece of business context (like brand voice) that every agent should have
in mind by default, since sponsor pipeline and vendor sourcing for it cut
across nearly every department (BD, Events, Operations, Marketing).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FlagshipProject:
    """Structured description of a ZYNTH-owned flagship project."""

    name: str
    date: str
    location: str
    funding_model: str
    current_priorities: list[str]

    def as_system_prompt_block(self) -> str:
        """Render the flagship project as a reusable system-prompt fragment."""
        return (
            f"ZYNTH flagship project: {self.name} — {self.date}, {self.location}. "
            f"Funding model: {self.funding_model}. "
            f"Current priorities: {', '.join(self.current_priorities)}."
        )


IGNITE_MYANMAR_SUMMIT = FlagshipProject(
    name="IGNITE Myanmar Business Summit",
    date="14 Nov 2026",
    location="Yangon, Myanmar",
    funding_model="sponsorship-funded, ZYNTH-owned IP",
    current_priorities=["sponsor pipeline", "vendor database"],
)

__all__ = ["FlagshipProject", "IGNITE_MYANMAR_SUMMIT"]
