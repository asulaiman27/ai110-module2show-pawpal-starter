"""PawPal+ logic layer.

Backend classes for the pet-care planning assistant. This is the skeleton
generated from the UML draft (diagrams/uml.mmd) — attributes and method stubs
only, no logic yet. Implementation lands in a later phase.
"""

from __future__ import annotations


class Pet:
    """An animal being cared for. Plain data owned by an Owner."""

    def __init__(self, name: str, species: str, breed: str = "") -> None:
        self.name = name
        self.species = species
        self.breed = breed


class CareTask:
    """One thing that needs doing for a pet (walk, feed, meds, etc.)."""

    def __init__(
        self,
        title: str,
        category: str,
        duration_minutes: int,
        priority: str,
        pet: Pet | None = None,
    ) -> None:
        self.title = title
        self.category = category
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.pet = pet

    def priority_score(self) -> int:
        """Return a numeric weight for this task, used to order the plan."""
        raise NotImplementedError


class Owner:
    """The person using PawPal+. Entry point holding pets and tasks."""

    def __init__(
        self,
        name: str,
        available_minutes: int = 0,
        preferred_window: str = "",
    ) -> None:
        self.name = name
        self.available_minutes = available_minutes
        self.preferred_window = preferred_window
        self.pets: list[Pet] = []
        self.tasks: list[CareTask] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        raise NotImplementedError

    def add_task(self, task: CareTask) -> None:
        """Add a care task to this owner's task list."""
        raise NotImplementedError


class ScheduledTask:
    """A CareTask placed at a start time within a DailyPlan."""

    def __init__(self, task: CareTask, start_time: str) -> None:
        self.task = task
        self.start_time = start_time


class DailyPlan:
    """The result of scheduling: ordered items plus a reasoning explanation."""

    def __init__(self) -> None:
        self.items: list[ScheduledTask] = []
        self.explanation: str = ""

    def add_item(self, item: ScheduledTask) -> None:
        """Append a scheduled task to the plan."""
        raise NotImplementedError

    def total_minutes(self) -> int:
        """Return the total scheduled time across all items."""
        raise NotImplementedError

    def explain(self) -> str:
        """Return a human-readable explanation of why the plan looks this way."""
        raise NotImplementedError


class Scheduler:
    """Stateless planning engine that turns tasks + constraints into a DailyPlan."""

    def generate_plan(
        self,
        tasks: list[CareTask],
        available_minutes: int,
    ) -> DailyPlan:
        """Build a DailyPlan from the given tasks under the time constraint."""
        raise NotImplementedError
