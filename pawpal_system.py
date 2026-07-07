"""PawPal+ logic layer.

Backend classes for the pet-care planning assistant:

- ``Task``      — a single care activity (description, time, frequency, done?).
- ``Pet``       — a pet's details plus the list of tasks it needs.
- ``Owner``     — a person who manages one or more pets.
- ``Scheduler`` — the "brain" that retrieves, organizes, and manages tasks
                  across all of an owner's pets.
"""

from __future__ import annotations

from datetime import date, timedelta

# Lower rank sorts earlier / is more important.
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}

# How far ahead the next occurrence of a recurring task lands.
FREQUENCY_STEP = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


class Task:
    """A single care activity for a pet."""

    def __init__(
        self,
        description: str,
        time: str = "",
        frequency: str = "daily",
        priority: str = "medium",
        completed: bool = False,
        due_date: date | None = None,
    ) -> None:
        """Create a care task with its description, timing, and priority."""
        self.description = description
        # Scheduled time of day as "HH:MM" (empty string = no fixed time).
        self.time = time
        # How often the task recurs, e.g. "daily", "weekly", "once".
        self.frequency = frequency
        self.priority = priority
        self.completed = completed
        # Calendar day the task is due; used to roll recurring tasks forward.
        self.due_date = due_date

    def mark_complete(self) -> None:
        """Mark the task as done."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Reset the task to not-done."""
        self.completed = False

    def toggle(self) -> bool:
        """Flip completion status and return the new value."""
        self.completed = not self.completed
        return self.completed

    def priority_rank(self) -> int:
        """Return a sortable rank for this task's priority (lower = higher)."""
        return PRIORITY_ORDER.get(self.priority, PRIORITY_ORDER["medium"])

    def is_recurring(self) -> bool:
        """Return True if this task repeats (daily or weekly)."""
        return self.frequency in FREQUENCY_STEP

    def next_occurrence(self) -> "Task | None":
        """Return a fresh, uncompleted copy due on the next cycle.

        Advances ``due_date`` by one day (daily) or one week (weekly) using
        ``timedelta``; returns None for one-off tasks. If no due date was set,
        the next occurrence is measured from today.
        """
        step = FREQUENCY_STEP.get(self.frequency)
        if step is None:
            return None
        base = self.due_date or date.today()
        return Task(
            self.description,
            time=self.time,
            frequency=self.frequency,
            priority=self.priority,
            due_date=base + step,
        )

    def sort_key(self) -> tuple[int, str, int]:
        """Sort key: chronological by time, then by priority as a tiebreaker.

        Tasks with no set time sort after timed ones so the day leads with its
        fixed appointments; among tasks at the same time, higher priority wins.
        """
        has_time = 0 if self.time else 1
        return (has_time, self.time, self.priority_rank())

    def __repr__(self) -> str:
        """Return a compact, readable one-line view of the task."""
        status = "x" if self.completed else " "
        when = self.time or "anytime"
        return f"[{status}] {when} — {self.description} ({self.priority}, {self.frequency})"


class Pet:
    """A pet's details and the list of care tasks it needs."""

    def __init__(self, name: str, species: str = "", breed: str = "") -> None:
        """Create a pet with its details and an empty task list."""
        self.name = name
        self.species = species
        self.breed = breed
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> Task:
        """Attach a task to this pet and return it."""
        self.tasks.append(task)
        return task

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet if present."""
        if task in self.tasks:
            self.tasks.remove(task)

    def pending_tasks(self) -> list[Task]:
        """Return this pet's not-yet-completed tasks."""
        return [t for t in self.tasks if not t.completed]

    def completed_tasks(self) -> list[Task]:
        """Return this pet's completed tasks."""
        return [t for t in self.tasks if t.completed]

    def __repr__(self) -> str:
        """Return a one-line summary of the pet and its task count."""
        label = self.species or "pet"
        return f"{self.name} ({label}): {len(self.tasks)} task(s)"


class Owner:
    """A person who manages one or more pets."""

    def __init__(self, name: str) -> None:
        """Create an owner with an empty list of pets."""
        self.name = name
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> Pet:
        """Register a pet under this owner and return it."""
        self.pets.append(pet)
        return pet

    def get_pet(self, name: str) -> Pet | None:
        """Look up a pet by name (case-insensitive), or None if not found."""
        for pet in self.pets:
            if pet.name.lower() == name.lower():
                return pet
        return None

    def all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        tasks: list[Task] = []
        for pet in self.pets:
            tasks.extend(pet.tasks)
        return tasks

    def all_tasks_with_pet(self) -> list[tuple[Pet, Task]]:
        """Return (pet, task) pairs so callers know which pet a task is for."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]

    def __repr__(self) -> str:
        """Return a one-line summary of the owner's pets and tasks."""
        return f"{self.name}: {len(self.pets)} pet(s), {len(self.all_tasks())} task(s)"


class Scheduler:
    """The brain: retrieves, organizes, and manages tasks across pets.

    It reads its data from an ``Owner`` so it always reflects the current set
    of pets and their tasks — it holds no task list of its own.
    """

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler that reads its tasks from the given owner."""
        self.owner = owner

    def all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every (pet, task) pair across the owner's pets."""
        return self.owner.all_tasks_with_pet()

    def pending_tasks(self) -> list[tuple[Pet, Task]]:
        """Return the (pet, task) pairs that still need doing."""
        return [(pet, task) for pet, task in self.all_tasks() if not task.completed]

    def daily_schedule(self) -> list[tuple[Pet, Task]]:
        """Return pending tasks ordered for the day.

        Ordering leads with fixed-time tasks (earliest first), then fills in
        untimed tasks by priority — so the owner sees appointments before
        flexible chores.
        """
        return sorted(self.pending_tasks(), key=lambda pair: pair[1].sort_key())

    def sort_by_time(self, tasks: list[Task] | None = None) -> list[Task]:
        """Return tasks sorted by their "HH:MM" time (untimed tasks last).

        Zero-padded "HH:MM" strings sort correctly with a plain string compare,
        so a lambda key is all we need; empty times map to "99:99" to sink them
        to the end.
        """
        if tasks is None:
            tasks = self.owner.all_tasks()
        return sorted(tasks, key=lambda t: t.time or "99:99")

    def filter_by_status(self, completed: bool = False) -> list[tuple[Pet, Task]]:
        """Return (pet, task) pairs whose completion matches ``completed``."""
        return [(pet, task) for pet, task in self.all_tasks() if task.completed == completed]

    def filter_by_pet(self, pet_name: str) -> list[Task]:
        """Return the tasks belonging to a single pet by name."""
        pet = self.owner.get_pet(pet_name)
        return list(pet.tasks) if pet else []

    # Kept as an alias so older callers using tasks_for() still work.
    tasks_for = filter_by_pet

    def _owning_pet(self, task: Task) -> Pet | None:
        """Find which of the owner's pets holds this task, if any."""
        for pet in self.owner.pets:
            if task in pet.tasks:
                return pet
        return None

    def mark_task_complete(self, task: Task) -> "Task | None":
        """Mark a task done and, if it recurs, queue its next occurrence.

        Returns the newly created next-occurrence task (added to the same pet),
        or None for one-off tasks.
        """
        task.mark_complete()
        nxt = task.next_occurrence()
        if nxt is not None:
            pet = self._owning_pet(task)
            if pet is not None:
                pet.add_task(nxt)
        return nxt

    # Backwards-compatible alias for the UI/earlier callers.
    def mark_complete(self, task: Task) -> "Task | None":
        """Alias for :meth:`mark_task_complete`."""
        return self.mark_task_complete(task)

    def detect_conflicts(self) -> list[str]:
        """Return warning strings for pending tasks that share the same time.

        This is a lightweight, non-crashing check: it flags exact "HH:MM"
        collisions (across any pets) and returns human-readable warnings rather
        than raising. See reflection 2b for the tradeoff versus true overlap
        detection.
        """
        by_time: dict[str, list[tuple[Pet, Task]]] = {}
        for pet, task in self.pending_tasks():
            if task.time:
                by_time.setdefault(task.time, []).append((pet, task))

        warnings: list[str] = []
        for time_str in sorted(by_time):
            group = by_time[time_str]
            if len(group) > 1:
                labels = ", ".join(f"{task.description} ({pet.name})" for pet, task in group)
                warnings.append(f"⚠️  Conflict at {time_str}: {labels}")
        return warnings

    def summary(self) -> dict[str, int]:
        """Return counts the UI can show at a glance."""
        pairs = self.all_tasks()
        done = sum(1 for _, task in pairs if task.completed)
        return {
            "pets": len(self.owner.pets),
            "total_tasks": len(pairs),
            "completed": done,
            "pending": len(pairs) - done,
        }
