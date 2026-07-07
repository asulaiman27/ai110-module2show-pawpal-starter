import streamlit as st

# Step 1: bring the logic-layer classes into the UI so buttons can call them.
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Plan care tasks for your pets. The UI drives the classes in pawpal_system.py.")

# ---------------------------------------------------------------------------
# Step 2: application memory.
#
# Streamlit re-runs this whole script on every interaction, so anything created
# at the top level is rebuilt from scratch each time. To keep our data alive we
# store the Owner in st.session_state (a dict that persists across re-runs) and
# only create a fresh one the first time — when the key is not already there.
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")

owner = st.session_state.owner  # the persisted instance, not a new one

# --- Owner info -------------------------------------------------------------
owner.name = st.text_input("Owner name", value=owner.name)

st.divider()

# --- Step 3a: Add a pet -----------------------------------------------------
st.subheader("Add a pet")
with st.form("add_pet", clear_on_submit=True):
    pet_name = st.text_input("Pet name", value="")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    breed = st.text_input("Breed (optional)", value="")
    add_pet = st.form_submit_button("Add pet")

if add_pet:
    if pet_name.strip():
        # The Owner class is responsible for registering a pet.
        owner.add_pet(Pet(pet_name.strip(), species, breed.strip()))
        st.success(f"Added {pet_name.strip()}.")
    else:
        st.warning("Please enter a pet name.")

if owner.pets:
    st.write("Your pets:", ", ".join(p.name for p in owner.pets))
else:
    st.info("No pets yet. Add one above to get started.")

st.divider()

# --- Step 3b: Add a task to a pet ------------------------------------------
st.subheader("Add a task")
if not owner.pets:
    st.info("Add a pet first, then you can add tasks for it.")
else:
    with st.form("add_task", clear_on_submit=True):
        target_pet_name = st.selectbox("For which pet?", [p.name for p in owner.pets])
        description = st.text_input("Task", value="Morning walk")
        col1, col2, col3 = st.columns(3)
        with col1:
            time = st.text_input("Time (HH:MM)", value="08:00")
        with col2:
            frequency = st.selectbox("Frequency", ["daily", "weekly", "once"])
        with col3:
            priority = st.selectbox("Priority", ["high", "medium", "low"])
        add_task = st.form_submit_button("Add task")

    if add_task:
        pet = owner.get_pet(target_pet_name)
        if pet and description.strip():
            # The Pet class is responsible for holding its own tasks.
            pet.add_task(
                Task(
                    description.strip(),
                    time=time.strip(),
                    frequency=frequency,
                    priority=priority,
                )
            )
            st.success(f"Added “{description.strip()}” for {pet.name}.")
        else:
            st.warning("Please enter a task description.")

st.divider()

# --- Today's schedule -------------------------------------------------------
st.subheader("Today's schedule")
scheduler = Scheduler(owner)
schedule = scheduler.daily_schedule()

if not schedule:
    st.info("Nothing pending. Add tasks above to build the schedule.")
else:
    for pet, task in schedule:
        cols = st.columns([5, 1])
        when = task.time or "anytime"
        cols[0].markdown(f"**{when}** — {task.description}  \n_{pet.name} · {task.priority} · {task.frequency}_")
        # Wiring the Task class's completion behaviour to a button.
        if cols[1].button("Done", key=f"done-{pet.name}-{task.description}-{task.time}"):
            scheduler.mark_complete(task)
            st.rerun()

    summary = scheduler.summary()
    st.caption(
        f"{summary['pending']} pending · {summary['completed']} done · "
        f"{summary['total_tasks']} total across {summary['pets']} pet(s)"
    )
