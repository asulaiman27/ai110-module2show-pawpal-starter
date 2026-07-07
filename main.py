"""Temporary testing ground for the PawPal+ logic layer.

Run with: python main.py

Builds a small owner/pets/tasks scenario and prints today's schedule so we can
confirm the classes in pawpal_system.py behave correctly from the terminal.
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def main() -> None:
    # 1. Create an owner.
    owner = Owner("Jordan")

    # 2. Create at least two pets.
    mochi = owner.add_pet(Pet("Mochi", "dog", "Corgi"))
    biscuit = owner.add_pet(Pet("Biscuit", "cat", "Tabby"))

    # 3. Add at least three tasks with different times.
    mochi.add_task(Task("Morning walk", time="08:00", priority="high"))
    mochi.add_task(Task("Evening walk", time="18:00", priority="high"))
    biscuit.add_task(Task("Breakfast", time="07:30", priority="high"))
    biscuit.add_task(Task("Brush coat", frequency="weekly", priority="low"))

    # 4. Print today's schedule.
    scheduler = Scheduler(owner)

    print(f"Today's Schedule for {owner.name}")
    print("=" * 40)
    for pet, task in scheduler.daily_schedule():
        when = task.time or "anytime"
        print(f"  {when:>7}  {task.description}  [{pet.name} · {task.priority}]")
    print("=" * 40)

    summary = scheduler.summary()
    print(
        f"{summary['pending']} task(s) to go across "
        f"{summary['pets']} pet(s) — {summary['completed']} done."
    )


if __name__ == "__main__":
    main()
