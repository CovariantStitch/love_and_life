from pathlib import Path

import streamlit as st

if st.session_state.is_local:
    RESOURCES_DIR = Path(__file__).parent.parent / "resources"
    TASKS_CSV = RESOURCES_DIR / "tasks.csv"
    ACTIONS_CSV = RESOURCES_DIR / "defis_et_gages.csv"
else:
    TASKS_CSV ="tasks"
    ACTIONS_CSV = "defis_et_gages"


def save_tasks() -> None:
    if st.session_state.is_local:
        st.session_state.df_tasks.to_csv(TASKS_CSV, index=False)
    else:
        st.session_state.gsheets_connection.update(worksheet=TASKS_CSV, data=st.session_state.df_tasks)


def save_actions() -> None:
    if st.session_state.is_local:
        st.session_state.actions_df.to_csv(ACTIONS_CSV, index=False)
    else:
        st.session_state.gsheets_connection.update(worksheet=ACTIONS_CSV, data=st.session_state.actions_df)
