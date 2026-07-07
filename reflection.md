# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

These are the three core things a user should be able to do in PawPal+:

1. **Add a pet care task.** The user records something their pet needs — a walk, a feeding, medication, grooming, or enrichment — along with how long it takes and how important it is (its priority). This is how the owner tells PawPal+ what needs to happen during the day.

2. **Generate a daily plan.** The user asks PawPal+ to turn their list of tasks into an ordered schedule for the day. The app weighs the owner's constraints (such as how much time is available) and each task's priority to decide which tasks to include and in what order.

3. **View today's plan and why it was chosen.** The user sees the resulting schedule laid out clearly — what happens, when, and for how long — together with a short explanation of the reasoning, so they understand why each task was placed the way it was.

---

**a. Initial design**

My initial UML had six classes, each with a single clear responsibility:

- **Owner** — the entry point for the user. Holds the owner's name and their planning constraints (`available_minutes`, `preferred_window`), plus the lists of pets and tasks. Responsible for registering pets (`add_pet`) and collecting care tasks (`add_task`).
- **Pet** — a plain data object for the animal being cared for (name, species, breed). It has no behavior of its own; it exists so tasks can be associated with a specific pet.
- **CareTask** — one thing that needs doing (walk, feed, meds, grooming, enrichment). Holds its title, category, duration, priority, and the pet it belongs to. Its one behavior is `priority_score()`, which turns the priority into a number the scheduler can sort by.
- **Scheduler** — a stateless engine whose sole job is to turn a set of tasks and constraints into a plan (`generate_plan`). Keeping it stateless means scheduling logic lives in one place and is easy to test in isolation.
- **DailyPlan** — the output of scheduling. Holds the ordered scheduled items and a reasoning explanation, and can report `total_minutes()` and produce an `explain()` string.
- **ScheduledTask** — a small wrapper pairing a `CareTask` with the `start_time` it was placed at in the plan.

I deliberately kept it lean: constraints and preferences live as simple fields on `Owner` rather than in a separate `Constraint` class, and priority is a string interpreted by `priority_score()` rather than its own type. The relationships are: an Owner owns many Pets and creates many CareTasks, each CareTask is for one Pet, the Scheduler reads CareTasks and produces a DailyPlan, and a DailyPlan contains many ScheduledTasks that each wrap one CareTask.

**b. Design changes**

After drafting the skeleton I asked my AI assistant to review `pawpal_system.py` for missing relationships and logic bottlenecks. Two pieces of feedback led me to change the design:

1. **The owner's preferences couldn't reach the scheduler.** `Owner` stored both `available_minutes` and `preferred_window`, but `Scheduler.generate_plan()` only accepted `available_minutes` — so the preferred time window had no way into the engine. I added a `preferred_window` parameter to `generate_plan()` so all of the owner's constraints actually flow into the scheduling logic, closing the gap between what the Owner holds and what the Scheduler can use.

2. **There was no way to explain what got left out.** When the total task time exceeds the available minutes, the scheduler has to drop tasks, but `DailyPlan` had nowhere to record them — which would make it impossible for `explain()` to justify *why* a task wasn't included. I added a `skipped: list[CareTask]` field to `DailyPlan` so dropped tasks are tracked and the explanation can account for them. This directly supports the "explain the plan" core action.

I did **not** adopt every suggestion. The reviewer also flagged that `priority` is a free-form string and that `start_time` as a string makes time arithmetic awkward. I chose to leave both for the implementation phase rather than add types/enums now, to avoid locking in complexity before I know exactly how the scheduling loop needs the data. (UML will be reconciled with these changes in Phase 6.)

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers two constraints: **time of day** and **priority**. `daily_schedule()` sorts pending tasks chronologically by their `"HH:MM"` time, places untimed ("anytime") tasks last, and uses priority (high → medium → low) as the tiebreaker when two tasks share a time. A third dimension, **frequency** (daily / weekly / once), drives recurrence rather than ordering.

I decided time mattered most because a pet owner reads a daily plan like a clock — what's next is more useful than what's most important in the abstract. Priority only earns its place as a tiebreaker, for the realistic case of two things booked at the same moment. I deliberately left out heavier constraints like total available minutes or per-task duration: they'd force the scheduler to *drop* tasks, which adds complexity (and the risk of silently hiding care the pet needs) without clearly helping the core "what do I do today, in what order" question.

**b. Tradeoffs**

My conflict detector (`Scheduler.detect_conflicts()`) only flags **exact "HH:MM" time matches** — it does not account for task *durations* or overlapping windows. If a 30-minute walk starts at 08:00 and feeding starts at 08:15, they overlap in real life, but the detector says nothing because their start strings differ.

I chose this on purpose. Tasks don't currently carry a duration, and true overlap detection would mean parsing times into minutes, adding a duration field, and comparing intervals — more moving parts and more ways to be subtly wrong. Exact-match detection is a handful of lines, never crashes, and returns a plain warning string the UI can show. For a busy pet owner, catching "you've scheduled two things at 8:00" already covers the most common and most confusing collision, so the simpler check buys most of the value at a fraction of the complexity. If durations become important later, the detector is the single place I'd extend to compare intervals instead of exact times.

---

## 3. AI Collaboration

**a. How you used AI**

I used my AI coding assistant across every phase but for different jobs: **brainstorming** the initial class list and relationships, **generating** the skeleton and then the real method bodies, **reviewing** the skeleton for missing relationships, **drafting the test suite** (including edge cases I hadn't thought of), and **refactoring/documenting** (docstrings, the README Features table).

The most effective features were:
- **Multi-file, whole-repo context** — the assistant could read `pawpal_system.py`, `app.py`, and the tests together, so wiring the UI to the logic layer and keeping the UML in sync with the code were reliable rather than guesswork.
- **Running code to verify itself** — instead of just claiming the wiring worked, it ran `main.py`, `pytest`, and a headless Streamlit `AppTest` and showed me the actual output. That caught a real ordering bug (see below).
- **Chat-style "explain then change"** — asking targeted questions ("how do I use a lambda key to sort `HH:MM` strings?", "how does `timedelta` give me today + 1 day?") produced small, understandable changes I could evaluate rather than large opaque rewrites.

The most helpful prompts were **specific and scoped**: naming the method to change, the behavior I wanted, and the constraint ("lightweight, returns a warning instead of crashing"). Vague prompts produced over-built answers; precise ones produced clean, minimal code.

**b. Judgment and verification**

The clearest example: after adding time sorting, the "Today's Schedule" still sorted by **priority first**, so a 07:30 task showed up *after* an 18:00 one. The original `sort_key()` returned `(has_time, priority_rank, time)`. I rejected keeping that "smart priority-first" ordering because it contradicted what a schedule is supposed to communicate, and changed the key to `(has_time, time, priority_rank)` — chronological, with priority only as a tiebreaker.

I verified suggestions three ways rather than trusting them on sight: (1) running `main.py` and reading the actual ordering, (2) the automated `pytest` suite (`test_daily_schedule_is_chronological` would now fail loudly if the order regressed), and (3) a headless `AppTest` that drove the real UI to confirm the conflict banner and table rendered. I also rejected two AI suggestions from the review pass — adding a priority *enum* and converting `time` to a typed object — because they added structure before the code needed it; I noted them as future work instead of locking in complexity early.

---

## 4. Testing and Verification

**a. What you tested**

The suite in `tests/test_pawpal.py` (12 tests) covers: basic object behavior (marking a task complete flips its status; adding a task grows a pet's list), **sorting** (chronological order; untimed tasks placed last), **recurrence** (a daily task rolls forward exactly one day, a weekly task seven days, and a `once` task does not recur or duplicate), **conflict detection** (duplicate times raise exactly one warning; distinct times and already-completed tasks raise none), and **edge cases** (a pet with no tasks yields an empty schedule and no conflicts; filtering separates pending vs. done and scopes to one pet).

These mattered because they are the behaviors a pet owner actually relies on and the ones most likely to break silently — a mis-sorted schedule or a recurring task that quietly stops reappearing would erode trust in the whole app, and an exception on an empty schedule would break a brand-new user's first screen.

**b. Confidence**

I'm confident — about **4 out of 5** — that the core logic is correct: every core behavior has a passing test, and the ordering, recurrence, and conflict paths are exercised end-to-end (unit tests, `main.py`, and a headless UI test). I held back the last point because conflict detection only catches exact time matches, not overlapping durations, and because time strings aren't validated for format.

With more time I'd test: malformed or edge-value times (`"8:00"` vs `"08:00"`, `"25:00"`, empty strings), duplicate/whitespace-only pet names in `get_pet()`, repeatedly completing the same recurring task to confirm the chain of due dates stays correct, and (once durations exist) genuinely overlapping intervals rather than exact-time clashes.

---

## 5. Reflection

**a. What went well**

I'm most satisfied with the clean separation between the logic layer (`pawpal_system.py`) and the UI (`app.py`). Because the `Scheduler` reads everything from the `Owner` and holds no state of its own, I could test all the "smart" behavior from the terminal and with `pytest` before the UI existed, then wire the UI up in one pass with confidence. The recurrence feature also came together neatly: `Task.next_occurrence()` does the date math and `Scheduler.mark_task_complete()` places the new task, so the same one method powers both the CLI demo and the UI's Done button.

**b. What you would improve**

I'd upgrade conflict detection from exact-time matching to real interval overlap, which means giving `Task` a duration and comparing time ranges. I'd also replace the free-form `time` and `priority` strings with validated types (a parsed time and a priority enum), so bad input is caught at creation instead of quietly mis-sorting. On the UI side, I'd add editing and deleting of tasks and support persisting data beyond a single session.

**c. Key takeaway**

The biggest lesson was what it means to be the **lead architect** rather than a passenger: the AI was fastest and most reliable at *local* work — writing a method, drafting tests, explaining a lambda — but the *global* decisions (tasks belong to `Pet` not `Owner`; a schedule should sort by time not priority; conflict detection should stay exact-match on purpose) had to come from me. Its confident suggestions were sometimes cleaner-looking but wrong for the design, so my job was to hold the mental model of the whole system, verify claims by actually running the code, and accept, modify, or reject each suggestion against that model.

**On working with separate chat sessions.** Keeping a dedicated session per phase — design, algorithms, testing — kept each conversation's context focused on one concern, so the assistant wasn't distracted by earlier tangents and I could attach just the files that mattered. The testing session, for instance, stayed centered on edge cases without re-litigating design decisions, which made its suggestions sharper and easier to review.
