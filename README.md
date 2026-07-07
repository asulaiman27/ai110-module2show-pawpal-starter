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

## ✨ Features

- **Multiple pets, per-pet tasks** — one owner manages many pets, and each pet keeps its own list of care tasks (walks, feeding, meds, grooming, enrichment).
- **Sorting by time** — the daily schedule lists tasks in chronological `"HH:MM"` order, with untimed "anytime" tasks placed last and priority as a tiebreaker (`Scheduler.daily_schedule()` / `sort_by_time()`).
- **Filtering** — view tasks scoped to a single pet, or split by completion status (`Scheduler.filter_by_pet()` / `filter_by_status()`).
- **Conflict warnings** — the scheduler flags pending tasks booked at the same time and surfaces a plain-language warning instead of failing (`Scheduler.detect_conflicts()`).
- **Daily / weekly recurrence** — completing a recurring task automatically queues its next occurrence, advancing the due date by a day or a week (`Task.next_occurrence()` / `Scheduler.mark_task_complete()`).
- **Live task completion** — mark tasks done in the UI; recurring tasks reschedule themselves and a summary tracks pending vs. completed counts.

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

Run the automated test suite from the project root:

```bash
python -m pytest
```

The suite (`tests/test_pawpal.py`, 12 tests) covers:

- **Basic behavior** — marking a task complete flips its status; adding a task grows a pet's task list.
- **Sorting** — `daily_schedule()` returns tasks in chronological order, with untimed tasks placed after timed ones.
- **Recurrence** — completing a `daily` task creates a follow-up due one day later; a `weekly` task advances seven days; a `once` task does not recur.
- **Conflict detection** — duplicate times raise exactly one warning; distinct times and already-completed tasks raise none.
- **Edge cases** — a pet with no tasks yields an empty schedule and no conflicts; filtering separates pending vs. completed and scopes to a single pet.

Successful run:

```
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0
collected 12 items

tests/test_pawpal.py ............                                        [100%]

============================== 12 passed in 0.01s ==============================
```

**Confidence level: ★★★★☆ (4/5).** The core logic — sorting, recurrence, filtering, and exact-time conflict detection — is well covered and passing. I held back the fifth star because conflict detection only catches exact time matches, not overlapping durations (see reflection 2b), and time strings aren't yet validated for format, so malformed input like `"8:00"` or `"25:00"` is untested.

## 📐 Smarter Scheduling

These are the "smart" behaviors in the logic layer and the method that implements each.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.daily_schedule()`, `Task.sort_key()` | Sorts tasks chronologically by their `"HH:MM"` time (a lambda key; untimed tasks map to `"99:99"` so they sink to the end); `daily_schedule()` breaks ties by priority. |
| Filtering | `Scheduler.filter_by_pet()`, `Scheduler.filter_by_status()` | Return the tasks for one pet by name, or all `(pet, task)` pairs matching a completion status. |
| Conflict handling | `Scheduler.detect_conflicts()` | Lightweight, non-crashing check that flags pending tasks sharing the same exact time and returns warning strings (exact-match only — see reflection 2b). |
| Recurring tasks | `Task.next_occurrence()`, `Scheduler.mark_task_complete()` | Completing a `daily`/`weekly` task auto-creates its next occurrence, advancing `due_date` with `timedelta` (+1 day / +1 week); one-off tasks return `None`. |

## 📸 Demo Walkthrough

### What the app lets you do

Launch the UI with `streamlit run app.py`. The single-page app has three areas:

- **Owner** — set the owner's name (persisted in `st.session_state` so it survives interactions).
- **Add a pet** — enter a name, species, and optional breed; the pet is registered under the owner.
- **Add a task** — pick a pet, then give the task a description, time (`HH:MM`), frequency (daily / weekly / once), and priority.
- **Today's schedule** — the pending tasks, sorted by time, shown as a table; a filter narrows to one pet; each task has a **Done** button; conflict warnings appear as banners above the plan.

### Example workflow

1. Set the owner name to **Jordan**.
2. **Add a pet:** `Mochi` (dog). Add a second pet: `Biscuit` (cat).
3. **Add tasks:** for Mochi, `Morning walk` at `08:00` (daily, high); for Biscuit, `Breakfast` at `08:00` (high) and `Litter box` at `07:30`.
4. **View Today's schedule** — tasks appear in chronological order (`07:30` before `08:00`), and because Mochi's walk and Biscuit's breakfast are both at `08:00`, a warning banner reads *"⚠️ Conflict at 08:00: Morning walk (Mochi), Breakfast (Biscuit)."*
5. **Filter** to just Mochi to see only that pet's tasks.
6. Click **Done** on the daily `Morning walk` — it's marked complete and its next occurrence is automatically queued for the following day.

### Key Scheduler behaviors shown

- **Sorting by time** — chronological order with untimed tasks last.
- **Conflict warnings** — same-time tasks flagged as a banner, not a crash.
- **Daily recurrence** — completing a daily task rolls it forward one day.
- **Filtering & summary** — per-pet filtering and a pending/done/total count.

### Sample CLI output (`python main.py`)

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

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
