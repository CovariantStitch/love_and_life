import datetime as dt

import streamlit as st

from utils.compute_points import on_actions_changed
from utils.css import custom_container

st.set_page_config(layout="wide")

st.title("⚔️ Défis et gages reçus")
current_user = st.session_state.user
other_user = st.session_state.other_user
actions_df = st.session_state.actions_df


def render_card(row, id_, card_color, other_user, kind):
    css = custom_container(f"action_{kind}_{id_}", card_color)
    st.markdown(css, unsafe_allow_html=True)
    if row["Points"] is None:
        st.header(f"Défi : {row['Name']}", help="Complète le pour des points !")
    else:
        st.header(f"Gage : {row['Name']}", help=f"A été payé par {other_user}")
        st.caption(f"({int(row['Points'])} points dépensés par {other_user})")

    st.markdown(f'<div class="action-description">{row.get("Description", "")}</div>', unsafe_allow_html=True)
    if row["Reward"] is not None:
        st.markdown(f'<div class="action-description">Récompenses : {int(row.get("Reward", ""))} points</div>',
                    unsafe_allow_html=True)
    st.caption(f"Envoyé le {row['Sent_date'].strftime('%d/%m/%Y')}")
    if kind == "validated":
        st.caption(f"Validé le {row['Validate_date'].strftime('%d/%m/%Y')}")


pending_actions = actions_df[(actions_df['Sent_to'] == current_user) & (actions_df['Status'] == 'Sent')]
accepted_actions = actions_df[(actions_df['Sent_to'] == current_user) & (actions_df['Status'] == 'Accepted')]
validated_actions = actions_df[(actions_df['Sent_to'] == current_user) & (actions_df['Status'] == 'Validated')]

pending, accepted, validated = st.tabs(["En attentes", "En cours", "Validés"])

with pending:
    st.header("Défis en attentes de validation")
    cols_pending = st.columns(2)
    if pending_actions.empty:
        st.info("Aucun défi en attente de validation")
    else:
        for i_, (id_, row) in enumerate(pending_actions.iterrows()):
            with cols_pending[i_ % len(cols_pending)].container(key=f"action_pending_{id_}", border=True):
                render_card(row, id_, row.Color, other_user, kind="pending")
                col1, col2 = st.columns(2)
                if col1.button("Approuver", key=f"approve_{id_}"):
                    st.session_state.actions_df.loc[id_, "Status"] = "Accepted"
                    on_actions_changed()
                    st.rerun()
                if col2.button("Refuser", key=f"refuse_{id_}"):
                    st.session_state.actions_df.loc[id_, "Status"] = "Refused"
                    on_actions_changed()
                    st.rerun()

with accepted:
    st.header("Défis et gages en cours")
    cols_accepted = st.columns(2)
    if accepted_actions.empty:
        st.info("Aucun défi accepté en cours")
    else:
        for i_, (id_, row) in enumerate(accepted_actions.iterrows()):
            with cols_accepted[i_ % len(cols_accepted)].container(key=f"action_accepted_{id_}", border=True):
                render_card(row, id_, row.Color, other_user, kind="accepted")
                if st.button("Marquer comme validé", key=f"validate_{id_}", type="primary"):
                    st.session_state.actions_df.loc[id_, "Status"] = "Validated"
                    st.session_state.actions_df.loc[id_, "Validate_date"] = dt.datetime.now()
                    on_actions_changed()
                    st.rerun()

with validated:
    st.header("Défis et gages validés")
    cols_validated = st.columns(2)
    if validated_actions.empty:
        st.info("Aucun défi validés")
    else:
        for i_, (id_, row) in enumerate(validated_actions.iterrows()):
            with cols_validated[i_ % len(cols_validated)].container(key=f"action_validated_{id_}", border=True):
                render_card(row, id_, row.Color, other_user, kind="validated")
