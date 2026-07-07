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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

My conflict detector (`Scheduler.detect_conflicts()`) only flags **exact "HH:MM" time matches** — it does not account for task *durations* or overlapping windows. If a 30-minute walk starts at 08:00 and feeding starts at 08:15, they overlap in real life, but the detector says nothing because their start strings differ.

I chose this on purpose. Tasks don't currently carry a duration, and true overlap detection would mean parsing times into minutes, adding a duration field, and comparing intervals — more moving parts and more ways to be subtly wrong. Exact-match detection is a handful of lines, never crashes, and returns a plain warning string the UI can show. For a busy pet owner, catching "you've scheduled two things at 8:00" already covers the most common and most confusing collision, so the simpler check buys most of the value at a fraction of the complexity. If durations become important later, the detector is the single place I'd extend to compare intervals instead of exact times.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
