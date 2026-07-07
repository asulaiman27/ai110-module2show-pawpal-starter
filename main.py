"""Temporary testing ground for the PawPal+ logic layer.

Run with: python main.py

Builds a small owner/pets/tasks scenario and exercises the "smarter scheduling"
features from the terminal: time sorting, filtering, recurring tasks, and
conflict detection.
"""

from datetime import date

from pawpal_system import Owner, Pet, Task, Scheduler


def line(char: str = "=") -> None:
    print(char * 48)


def main() -> None:
    owner = Owner("Jordan")
    mochi = owner.add_pet(Pet("Mochi", "dog", "Corgi"))
    biscuit = owner.add_pet(Pet("Biscuit", "cat", "Tabby"))

    # Add tasks deliberately OUT OF ORDER to prove sorting works.
    mochi.add_task(Task("Evening walk", time="18:00", priority="high"))
    mochi.add_task(Task("Morning walk", time="08:00", frequency="daily", priority="high",
                        due_date=date(2026, 7, 7)))
    mochi.add_task(Task("Brush coat", frequency="weekly", priority="low"))  # no set time
    biscuit.add_task(Task("Breakfast", time="08:00", priority="high"))       # clashes with walk
    biscuit.add_task(Task("Litter box", time="07:30", priority="medium"))

    scheduler = Scheduler(owner)

    # --- Sorting -----------------------------------------------------------
    print("Today's Schedule (sorted by time)")
    line()
    for pet, task in scheduler.daily_schedule():
        when = task.time or "anytime"
        print(f"  {when:>7}  {task.description}  [{pet.name} · {task.priority}]")
    line()

    # --- Conflict detection ------------------------------------------------
    print("\nConflict check")
    line("-")
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            print(f"  {warning}")
    else:
        print("  No conflicts.")

    # --- Filtering ---------------------------------------------------------
    print("\nFiltering")
    line("-")
    print("  Mochi's tasks:", [t.description for t in scheduler.filter_by_pet("Mochi")])
    pending = [t.description for _, t in scheduler.filter_by_status(completed=False)]
    print("  Pending everywhere:", pending)

    # --- Recurring tasks ---------------------------------------------------
    print("\nRecurring tasks")
    line("-")
    morning = scheduler.filter_by_pet("Mochi")[1]  # the daily "Morning walk"
    print(f"  Completing '{morning.description}' (due {morning.due_date})...")
    nxt = scheduler.mark_task_complete(morning)
    print(f"  -> auto-created next occurrence due {nxt.due_date} (completed={nxt.completed})")

    # --- Summary -----------------------------------------------------------
    print()
    s = scheduler.summary()
    print(f"{s['pending']} pending · {s['completed']} done · "
          f"{s['total_tasks']} total across {s['pets']} pet(s)")


if __name__ == "__main__":
    main()
