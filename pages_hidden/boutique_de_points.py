from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
import datetime as dt

from utils.compute_points import on_actions_changed
from utils.css import custom_container, custom_button


st.set_page_config(layout="wide")

available_categories = ["Daily 📅", "Hot 🔥", "Naughty 😈", "Corvée 🧹"]

# get buttons css and apply the style for all the buttons pages (primary)
css_button = custom_button()
st.markdown(css_button, unsafe_allow_html=True)


def render_card(row, id_, card_color, other_user, kind):
    css = custom_container(f"chall_and_dares_{kind}_{id_}", card_color)
    st.markdown(css, unsafe_allow_html=True)

    name_points_cols = st.columns([2, 1])
    name_points_cols[0].subheader(f"{row['Name']}")
    name_points_cols[1].subheader(f"{int(row['Points'])} points")

    desc_cat_cols = st.columns([2, 1])
    desc_cat_cols[0].text(f"{row['Description']}")
    cat_cols = desc_cat_cols[1].columns(2)
    for i_, cat in enumerate(row.Categories.split("/")):
        cat_cols[i_%len(cat_cols)].markdown(f":violet-badge[:material/star: {cat[-2:]}]")


@st.dialog("Ajouter un nouveau gage")
def add_dare():
    name_points_cols = st.columns([0.7, 0.3])
    name = name_points_cols[0].text_input("Titre du gage")
    points = name_points_cols[1].number_input("Nombre de points", min_value=0, max_value=100, value=10, step=1)

    description = st.text_input("Description")
    cat_col_cols = st.columns([0.8, 0.2])
    categories = cat_col_cols[0].multiselect("Catégories", available_categories)
    color = cat_col_cols[1].color_picker("Couleur")
    if st.button("Ajouter", type="primary"):
        color = 'rgba' + str(tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.1, ))
        dare = [name, description, "/".join(categories), points, color]
        st.session_state.list_challenges_and_dares.loc[len(st.session_state.list_challenges_and_dares)] = dare
        if st.session_state.is_local:
            st.session_state.list_challenges_and_dares.to_csv(Path(__file__).parent.parent / 'resources' / 'liste_defis_et_gages.csv', index=False)
        else:
            st.session_state.gsheets_connection.update(worksheet="liste_defis_et_gages", data=st.session_state.list_challenges_and_dares)
        st.rerun()


@st.dialog("Envoyer un challenge")
def add_challenge():
    name_points_cols = st.columns([0.7, 0.3])
    name = name_points_cols[0].text_input("Titre du challenge")
    points = name_points_cols[1].number_input("Nombre de points à gagner",
                                              min_value=0, max_value=100, value=10, step=1)
    description = st.text_input("Description")

    if st.button("Envoyer"):
        challenge = [name, description, None, "Sent", st.session_state.other_user, dt.datetime.now(), None, points]
        st.session_state.actions_df.loc[len(st.session_state.actions_df)] = challenge
        on_actions_changed()


def add_card_for_new_dare(col, kind):
    with col.container(border=True, key=f"action_add_task_{kind}"):
        card_color = 'rgba(255, 255, 255, 0.1)'
        css = custom_container(f"action_add_task_{kind}", card_color)
        st.markdown(css, unsafe_allow_html=True)

        # 1. Définition du CSS (on l'intègre directement au composant)
        CSS = """
        .add-player-btn {
            border: 2px dashed #d1d5db;
            border-radius: 16px;
            background: #f9fafb;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 60px;
            color: #9ca3af;
            margin: 12px;
            cursor: pointer;
            height: 200px;
            transition: all 0.2s;
        }
        .add-player-btn:hover {
            border-color: #ec4899;
            color: #ec4899;
            background: #fdf2f8;
        }
        """

        # 2. Définition du JS
        JS = """
        export default function(component) {
            const { setTriggerValue, parentElement } = component;

            // On crée la div du bouton
            const btn = document.createElement('div');
            btn.className = 'add-player-btn';
            btn.innerHTML = '+';

            // On gère le clic
            btn.onclick = () => {
                // On envoie une valeur arbitraire ou un timestamp pour déclencher l'update
                setTriggerValue('clicked', Date.now());
            };

            parentElement.appendChild(btn);
        }
        """

        # 3. Création du composant
        add_player_component = st.components.v2.component(
            "add_player_button",
            css=CSS,
            js=JS,
        )
        result = add_player_component(on_clicked_change=lambda: None)

        if result.clicked:
            add_dare()


st.title("🏅 Boutique de Points")

# get some useful variables
points = st.session_state.points
current_user = st.session_state.user
other_user = st.session_state.other_user
actions_df = st.session_state.actions_df
list_challenges_and_dares = st.session_state.list_challenges_and_dares
categories = list_challenges_and_dares['Categories'].str.get_dummies(sep='/')
list_challenges_and_dares = pd.concat([list_challenges_and_dares, categories], axis=1)

# filters
filter_cols = st.columns([1, 3])
min_points = filter_cols[0].slider("Points minimum", min_value=0,
                                   max_value=int(list_challenges_and_dares['Points'].max()),
                                   value=(0, int(points[current_user])))
selected_categories = filter_cols[1].multiselect("Categories", categories.columns, default=categories.columns)
filter_points = (list_challenges_and_dares.Points >= min_points[0]) & (list_challenges_and_dares.Points <= min_points[1])
filter_categories = list_challenges_and_dares[selected_categories].any(axis=1)
list_challenges_and_dares = list_challenges_and_dares[filter_points & filter_categories]

# add cards
cols = st.columns(2)
kind = ""
for i_, (id_, row) in enumerate(list_challenges_and_dares.iterrows()):
    with cols[i_ % len(cols)].container(key=f"chall_and_dares_{kind}_{id_}", border=True):
        render_card(row, id_, row.Color, other_user, kind=kind)
        col1, col2 = st.columns(2)

        cols_button = st.columns([0.2, 0.6, 0.2])
        if cols_button[1].button("Envoyer le gage !", key=f"button_chall_and_dares_{kind}_{id_}", type="primary",
                       disabled=points[current_user]<int(row["Points"]), use_container_width=True):
            # sends the challenge
            new_challenge = [row.Name, row.Description, row.Points, "Accepted", other_user, dt.datetime.now(),
                             None, None, row.Color]
            st.session_state.actions_df.loc[len(st.session_state.actions_df)] = new_challenge
            on_actions_changed()

# add a card which enables the user to add a dare
try:
    add_card_for_new_dare(cols[(i_+1) % len(cols)], kind="all")
except NameError:
    add_card_for_new_dare(cols[0], kind="all")

with st.sidebar:
    if st.button("Ajouter un gage", type='primary', use_container_width=True):
        add_dare()

    if st.button("Envoyer un défi", type='primary', use_container_width=True):
        add_challenge()