import streamlit as st

from utils.persistence import save_actions, save_tasks


def compute_points() -> None:
    """Recalcule les points en mémoire à partir des tâches et des défis/gages."""
    for user in st.session_state["users"]:
        st.session_state.points[user] = 0

    for _, task in st.session_state.df_tasks.iterrows():
        if task.Done and task.Done_by is not None:
            if task.Done_by == "Ensemble":
                for user in st.session_state["users"]:
                    st.session_state.points[user] += task.Points // 2
            else:
                st.session_state.points[task.Done_by] += task.Points

    for _, action in st.session_state.actions_df.iterrows():
        if action.Points is not None and action.Status not in ("Refused", "Rejected"):
            payer = st.session_state["users"][
                (st.session_state["users"].index(action.Sent_to) + 1) % 2
            ]
            st.session_state.points[payer] -= action.Points
        elif action.Status == "Validated":
            st.session_state.points[action.Sent_to] += action.Reward


def on_tasks_changed() -> None:
    """Recalcule les points et persiste les tâches."""
    compute_points()
    save_tasks()


def on_actions_changed() -> None:
    """Recalcule les points et persiste les défis/gages."""
    compute_points()
    save_actions()
