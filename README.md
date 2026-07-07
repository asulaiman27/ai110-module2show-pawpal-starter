# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Terminal output from running the logic-layer test script (`python main.py`):

```
Today's Schedule (sorted by time)
================================================
    07:30  Litter box  [Biscuit · medium]
    08:00  Morning walk  [Mochi · high]
    08:00  Breakfast  [Biscuit · high]
    18:00  Evening walk  [Mochi · high]
  anytime  Brush coat  [Mochi · low]
================================================

Conflict check
------------------------------------------------
  ⚠️  Conflict at 08:00: Morning walk (Mochi), Breakfast (Biscuit)

Filtering
------------------------------------------------
  Mochi's tasks: ['Evening walk', 'Morning walk', 'Brush coat']
  Pending everywhere: ['Evening walk', 'Morning walk', 'Brush coat', 'Breakfast', 'Litter box']

Recurring tasks
------------------------------------------------
  Completing 'Morning walk' (due 2026-07-07)...
  -> auto-created next occurrence due 2026-07-08 (completed=False)

5 pending · 1 done · 6 total across 2 pet(s)
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

These are the "smart" behaviors in the logic layer and the method that implements each.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.daily_schedule()`, `Task.sort_key()` | Sorts tasks chronologically by their `"HH:MM"` time (a lambda key; untimed tasks map to `"99:99"` so they sink to the end); `daily_schedule()` breaks ties by priority. |
| Filtering | `Scheduler.filter_by_pet()`, `Scheduler.filter_by_status()` | Return the tasks for one pet by name, or all `(pet, task)` pairs matching a completion status. |
| Conflict handling | `Scheduler.detect_conflicts()` | Lightweight, non-crashing check that flags pending tasks sharing the same exact time and returns warning strings (exact-match only — see reflection 2b). |
| Recurring tasks | `Task.next_occurrence()`, `Scheduler.mark_task_complete()` | Completing a `daily`/`weekly` task auto-creates its next occurrence, advancing `due_date` with `timedelta` (+1 day / +1 week); one-off tasks return `None`. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
