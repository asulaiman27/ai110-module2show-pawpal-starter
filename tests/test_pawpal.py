"""Tests for the PawPal+ logic layer.

Covers the core behaviors of the system:
- task completion and addition (basic object behavior)
- chronological sorting (happy path + untimed-task edge case)
- recurring-task logic (daily rolls forward; one-off does not)
- conflict detection (duplicate times flagged; distinct times are not)
- filtering and empty-schedule edge cases
"""

import os
import sys
from datetime import date

# Make the project root importable when tests run from the tests/ directory.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pawpal_system import Owner, Pet, Task, Scheduler


# ---------------------------------------------------------------------------
# Basic object behavior
# ---------------------------------------------------------------------------
def test_mark_complete_changes_status():
    """mark_complete() should flip a task from not-done to done."""
    task = Task("Morning walk", time="08:00")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    """Adding a task to a Pet should grow that pet's task list by one."""
    pet = Pet("Mochi", "dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task("Feed", time="07:30"))

    assert len(pet.tasks) == 1


# ---------------------------------------------------------------------------
# Sorting correctness
# ---------------------------------------------------------------------------
def test_daily_schedule_is_chronological():
    """Tasks added out of order should come back sorted by time."""
    owner = Owner("Jordan")
    pet = owner.add_pet(Pet("Mochi", "dog"))
    pet.add_task(Task("Evening walk", time="18:00"))
    pet.add_task(Task("Breakfast", time="07:30"))
    pet.add_task(Task("Lunch", time="12:00"))

    scheduler = Scheduler(owner)
    times = [task.time for _, task in scheduler.daily_schedule()]

    assert times == ["07:30", "12:00", "18:00"]


def test_untimed_tasks_sort_after_timed_ones():
    """A task with no set time should appear after all timed tasks."""
    owner = Owner("Jordan")
    pet = owner.add_pet(Pet("Mochi", "dog"))
    pet.add_task(Task("Brush coat"))           # no time
    pet.add_task(Task("Morning walk", time="08:00"))

    scheduler = Scheduler(owner)
    ordered = [task.description for _, task in scheduler.daily_schedule()]

    assert ordered == ["Morning walk", "Brush coat"]


# ---------------------------------------------------------------------------
# Recurrence logic
# ---------------------------------------------------------------------------
def test_completing_daily_task_creates_next_day_occurrence():
    """Marking a daily task complete should queue one due the next day."""
    owner = Owner("Jordan")
    pet = owner.add_pet(Pet("Mochi", "dog"))
    task = pet.add_task(
        Task("Walk", time="08:00", frequency="daily", due_date=date(2026, 7, 7))
    )
    scheduler = Scheduler(owner)

    nxt = scheduler.mark_task_complete(task)

    assert task.completed is True                    # original done
    assert nxt is not None                           # a follow-up was created
    assert nxt.completed is False                    # follow-up is fresh
    assert nxt.due_date == date(2026, 7, 8)          # exactly one day later
    assert nxt in pet.tasks                           # added to the same pet
    assert len(pet.tasks) == 2


def test_completing_weekly_task_advances_one_week():
    """A weekly task should roll forward by seven days."""
    owner = Owner("Jordan")
    pet = owner.add_pet(Pet("Mochi", "dog"))
    task = pet.add_task(
        Task("Nail trim", frequency="weekly", due_date=date(2026, 7, 7))
    )

    nxt = Scheduler(owner).mark_task_complete(task)

    assert nxt.due_date == date(2026, 7, 14)


def test_one_off_task_does_not_recur():
    """A 'once' task should not create a follow-up when completed."""
    owner = Owner("Jordan")
    pet = owner.add_pet(Pet("Mochi", "dog"))
    task = pet.add_task(Task("Vet visit", time="10:00", frequency="once"))

    nxt = Scheduler(owner).mark_task_complete(task)

    assert nxt is None
    assert len(pet.tasks) == 1


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------
def test_detects_duplicate_time_conflict():
    """Two pending tasks at the same time should raise one warning."""
    owner = Owner("Jordan")
    mochi = owner.add_pet(Pet("Mochi", "dog"))
    biscuit = owner.add_pet(Pet("Biscuit", "cat"))
    mochi.add_task(Task("Morning walk", time="08:00"))
    biscuit.add_task(Task("Breakfast", time="08:00"))

    conflicts = Scheduler(owner).detect_conflicts()

    assert len(conflicts) == 1
    assert "08:00" in conflicts[0]


def test_no_conflict_when_times_differ():
    """Distinct times should produce no conflict warnings."""
    owner = Owner("Jordan")
    pet = owner.add_pet(Pet("Mochi", "dog"))
    pet.add_task(Task("Morning walk", time="08:00"))
    pet.add_task(Task("Evening walk", time="18:00"))

    assert Scheduler(owner).detect_conflicts() == []


def test_completed_tasks_do_not_conflict():
    """A completed task should not clash with a pending one at the same time."""
    owner = Owner("Jordan")
    pet = owner.add_pet(Pet("Mochi", "dog"))
    done = pet.add_task(Task("Morning walk", time="08:00"))
    pet.add_task(Task("Breakfast", time="08:00"))
    done.mark_complete()

    assert Scheduler(owner).detect_conflicts() == []


# ---------------------------------------------------------------------------
# Filtering and empty-schedule edge cases
# ---------------------------------------------------------------------------
def test_pet_with_no_tasks_yields_empty_schedule():
    """An owner whose pet has no tasks should have an empty schedule."""
    owner = Owner("Jordan")
    owner.add_pet(Pet("Mochi", "dog"))

    scheduler = Scheduler(owner)

    assert scheduler.daily_schedule() == []
    assert scheduler.detect_conflicts() == []


def test_filter_by_status_and_pet():
    """Filtering should separate pending from done and scope to one pet."""
    owner = Owner("Jordan")
    mochi = owner.add_pet(Pet("Mochi", "dog"))
    biscuit = owner.add_pet(Pet("Biscuit", "cat"))
    walk = mochi.add_task(Task("Walk", time="08:00"))
    mochi.add_task(Task("Brush", time="09:00"))
    biscuit.add_task(Task("Feed", time="08:00"))
    walk.mark_complete()

    scheduler = Scheduler(owner)

    pending = [t.description for _, t in scheduler.filter_by_status(completed=False)]
    completed = [t.description for _, t in scheduler.filter_by_status(completed=True)]
    assert pending == ["Brush", "Feed"]
    assert completed == ["Walk"]
    assert [t.description for t in scheduler.filter_by_pet("Mochi")] == ["Walk", "Brush"]
