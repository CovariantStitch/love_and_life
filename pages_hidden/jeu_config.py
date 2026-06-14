import streamlit as st
import pandas as pd
from pathlib import Path

from utils.data import Player, VETEMENTS, PRATIQUES, OBJETS, GameData

CLOTHES_EMOJI = "👕"
PRACTICES_EMOJI = "🔥"
SECRET_EMOJI = "🔒"

CSS_card = """
<style>
    .players-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 22px 24px;
        padding: 12px 0;
        align-items: center;
    }
    .player-card {
        background: white;
        border-radius: 16px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.1);
        width: 280px;
        text-align: center; 
        transition: transform 0.15s;
    }
    .player-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }
    .avatar-container {
        position: relative;
        height: 180px;
        background: linear-gradient(to bottom, #f1f5f9, #e2e8f0);
        border-radius: 16px;
    }
    .avatar-icon {
        position: absolute;
        top: 35px;
        left: 50%;
        transform: translateX(-50%);
        width: 100px;
        height: 100px;
        background: #cbd5e1;
        border-radius: 50%;
        border: 5px solid white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 48px;
        color: #475569;
    }
    .gender-badge {
        position: absolute;
        top: 12px;
        left: 12px;
        color: white;
        border-radius: 50%;
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        font-weight: bold;
    }
    .menu-dots {
        position: absolute;
        top: 16px;
        right: 16px;
        color: #64748b;
        font-size: 24px;
        cursor: pointer;
        z-index: 999;
    }
    .menu-dots:hover {
        color: #ec4899;
    }
    .card-bottom {
        background: #ec4899;
        color: white;
        padding: 20px 16px 16px;
        position: relative;
        border-radius: 16px;
    }
    .card-bottom::before {
        content: "";
        position: absolute;
        top: -24px;
        left: 0;
        right: 0;
        height: 48px;
        background: #ec4899;
        border-radius: 60% 60% 0 0;
    }
    .player-name {
        font-size: 1.5rem;
        font-weight: 700;
        margin: 6px 0 4px;
        position: relative;
        z-index: 1;
    }
    .player-gender {
        font-size: 1rem;
        opacity: 0.95;
        margin-bottom: 18px;
        position: relative;
        z-index: 1;
    }
    .stats-row {
        display: flex;
        justify-content: space-evenly;
        gap: 12px;
        position: relative;
        z-index: 1;
    }
    .stat-item {
        background: rgba(255,255,255,0.28);
        border-radius: 12px;
        padding: 10px 14px;
        min-width: 40px;
        font-size: 1.1rem;
        font-weight: 600;
        cursor: pointer;
    }
    .stat-item:hover {
        transform: translateY(-4px)
    }
</style>
"""


@st.dialog("Modification joueur")
def edit_player_details(player_: Player):
    st.subheader(player_.name)
    tab_vet, tab_prat = st.tabs(["👕 Vêtements", "🔥 Pratiques"])
    with tab_vet:
        st.caption("Cochez ce que le joueur porte encore")
        updated_clothes = []
        cols = st.columns(2)
        for i, item in enumerate(VETEMENTS):
            col = cols[i % 2]
            with col:
                checked = item in player_.clothes
                if st.checkbox(item, value=checked, key=f"cloth_{item}"):
                    updated_clothes.append(item)

    with tab_prat:
        st.caption("Cochez les pratiques déjà réalisées / autorisées")
        updated_practices = []
        cols = st.columns(2)
        for i, act in enumerate(PRATIQUES):
            col = cols[i % 2]
            with col:
                checked = act in player_.practices
                if st.checkbox(act, value=checked, key=f"prac_{act}"):
                    updated_practices.append(act)

    col_left, col_right = st.columns([3, 1])
    with col_left:
        secret = st.checkbox("Le joueur a un secret à révéler", value=player_.has_secret)
    with col_right:
        st.write("")  # espace

    if st.button("Enregistrer", type="primary", use_container_width=True):
        player_.clothes = updated_clothes
        player_.practices = updated_practices
        player_.has_secret = secret
        player_.process()
        st.session_state.players[player_.name] = player_
        st.success("Modifications enregistrées !")
        st.rerun()

@st.dialog("Modifier les paramètres")
def edit_game_parameters():
    # todo: add images for each objects

    st.subheader("Modifier les paramètres de la partie")
    game = st.session_state.game

    cols_game_edit = st.columns(2)
    intensity = cols_game_edit[0].slider("Intensité", min_value=1, max_value=5, value=game.intensity)
    duration = cols_game_edit[1].slider("Durée", min_value=15, max_value=60, value=game.duration, step=15)
    objects = []
    cols = st.columns(2)
    for i, item in enumerate(OBJETS):
        col = cols[i % 2]
        with col:
            checked = item in game.objects
            if st.checkbox(item, value=checked, key=f"object_{item}"):
                objects.append(item)

    if st.button("Enregistrer", type="primary", use_container_width=True):
        game.intensity = intensity
        game.duration = duration
        game.objects = objects
        game.process()
        st.session_state.game = game
        st.success("Modifications enregistrées !")
        st.rerun()


@st.dialog("Ajouter des actions et questions")
def add_action_question():
    game = st.session_state.game

    cols = st.columns([1, 2])
    type_ = cols[0].selectbox("Type", options=["Question", "Action"], index=1)
    title = cols[1].text_input("Titre")

    text = st.text_area("Description")

    possibilities = []

    cols = st.columns(2)
    level = cols[0].slider("Niveau", min_value=1, max_value=5, value=1)
    gender = cols[1].segmented_control(label="Sexe", options=["Fille", "Garçon", "Both"], default="Both")

    cols = st.columns(2)
    practices = cols[0].multiselect(label="Pratiques", options=PRATIQUES)
    objects = cols[1].multiselect(label="Accessoires", options=OBJETS)

    timer = ""
    cols = st.columns([1, 3])
    repitions_bool = cols[0].checkbox("Répétitions")
    repetitions = cols[1].slider("Min / Max", min_value=1, max_value=30, value=[0, 30])

    if st.button("Ajouter !"):
        gender_ = {"Fille": "F", "Garçon": "M", "Both": "B"}[gender]
        possibilities_ = "/".join(possibilities)
        practices_ = "/".join(practices)
        objects_ = "/".join(objects)
        if repitions_bool != False:
            repetitions_ = "/".join(repetitions)
        else:
            repetitions_ = ""
        new = [type_, title, text, possibilities_, level, gender_, practices_, objects_, timer, repetitions_]
        st.session_state.df_game_data.loc[len(st.session_state.df_game_data)] = new
        if st.session_state.is_local:
            st.session_state.df_game_data.to_csv(Path(__file__).parent.parent / "resources" / "game.csv", index=False)
        else:
            st.session_state.gsheets_connection.update(worksheet="game", data=st.session_state.df_game_data)
        st.session_state.game_data = GameData(st.session_state.df_game_data)
        st.rerun()


def view_action_question():
    df = st.session_state.df_game_data
    # filters
    with st.container(border=True):
        cols = st.columns(4)
        level = cols[0].slider("Niveau", min_value=1, max_value=5, value=1)
        gender = cols[1].segmented_control(label="Sexe", options=["Fille", "Garçon", "Both"], default="Both")
        practices = cols[2].multiselect(label="Pratiques", options=PRATIQUES)
        objects = cols[3].multiselect(label="Accessoires", options=OBJETS)

    filter_level = df["Level"] == level
    filter_gender = df["Gender"] == {"Fille": "F", "Garçon": "M", "Both": "B"}[gender] if gender != None else True
    filter_practices = df["Practices"].isin(practices) if practices != [] else True
    filter_objects = df["Objects"].isin(objects) if objects != [] else True
    df = df[filter_level & filter_gender & filter_practices & filter_objects]

    # --- Cartes visuelles pour les actions / questions ---
    if df.empty:
        st.info("Aucune carte ne correspond aux filtres sélectionnés pour le moment.")
        return

    st.markdown(
        """
        <style>
        .aq-card {
            background: linear-gradient(135deg, #fdf2f8, #eef2ff);
            border-radius: 18px;
            padding: 16px 18px 14px;
            box-shadow: 0 10px 25px rgba(15,23,42,0.12);
            position: relative;
            overflow: hidden;
            margin: 8px
        }
        .aq-card::before {
            content: "";
            position: absolute;
            inset: 0;
            background: radial-gradient(circle at top left, rgba(236,72,153,0.18), transparent 55%);
            opacity: 0.9;
            pointer-events: none;
        }
        .aq-header {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 8px;
            position: relative;
            z-index: 1;
        }
        .aq-title {
            font-weight: 700;
            font-size: 1.05rem;
            color: #0f172a;
        }
        .aq-pill {
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 0.8rem;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            background: rgba(15,23,42,0.08);
            color: #0f172a;
            white-space: nowrap;
        }
        .aq-pill-action {
            background: rgba(251, 113, 133, 0.22);
            color: #9f1239;
        }
        .aq-pill-question {
            background: rgba(59, 130, 246, 0.18);
            color: #1d4ed8;
        }
        .aq-body {
            margin-top: 8px;
            font-size: 0.93rem;
            color: #111827;
            line-height: 1.4;
            position: relative;
            z-index: 1;
        }
        .aq-meta-row {
            margin-top: 10px;
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            font-size: 0.78rem;
            position: relative;
            z-index: 1;
        }
        .aq-chip {
            padding: 2px 8px;
            border-radius: 999px;
            background: rgba(15,23,42,0.06);
            color: #0f172a;
        }
        .aq-chip-strong {
            background: rgba(15,23,42,0.9);
            color: white;
        }
        .aq-poss-title {
            margin-top: 10px;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #4b5563;
            position: relative;
            z-index: 1;
        }
        .aq-poss-list {
            margin-top: 4px;
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
            position: relative;
            z-index: 1;
        }
        .aq-poss-item {
            padding: 3px 8px;
            border-radius: 999px;
            background: rgba(255,255,255,0.75);
            border: 1px solid rgba(148,163,184,0.4);
            font-size: 0.78rem;
            color: #111827;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    cols_cards = st.columns(2)
    for i_, (_, row) in enumerate(df.iterrows()):
        is_action = row.Type == "Action"
        icon = "👉" if is_action else "❓"
        pill_class = "aq-pill-action" if is_action else "aq-pill-question"
        type_label = "Action" if is_action else "Question"

        # Possibilités (pour les questions)
        poss_html = ""
        if not is_action and hasattr(row, "Possibilities") and isinstance(row.Possibilities, str) and row.Possibilities:
            items = [p.strip() for p in row.Possibilities.split("/") if p.strip()]
            if items:
                poss_html = """<div class="aq-poss-title">Réponses possibles</div>
                <div class="aq-poss-list">"""
                for p in items:
                    poss_html += f"""<span class="aq-poss-item">{p}</span>"""
                poss_html += "</div>"
                
        # Badges pratiques / objets
        practices_txt = str(getattr(row, "Practices", ""))
        objects_txt = str(getattr(row, "Objects", ""))
        meta_row = f"""<span class="aq-chip aq-chip-strong">🔥 Niveau {row.Level}</span>
                <span class="aq-chip">👤 {row.Gender}</span>"""
        if practices_txt != "nan":
            meta_row += f'<span class="aq-chip">🔥 {practices_txt}</span>'
        if objects_txt != "nan":
            meta_row += f'<span class="aq-chip">🪀 {objects_txt}</span>'

        #todo: actuellement les balises {player} et {receiver} s'affichent -> afficher des noms
        cards_html = f"""
        <div class="aq-card">
            <div class="aq-header">
                <div class="aq-title">{row.Title}</div>
                <div class="aq-pill {pill_class}">{icon} {type_label}</div>
            </div>
            <div class="aq-body">
                {row.Text}
            </div>
            <div class="aq-meta-row">
                {meta_row}
            </div>
            {poss_html}
        </div>
        """

        cards_html += "</div>"
        cols_cards[i_%2].markdown(cards_html, unsafe_allow_html=True)


def config_tab():
    cols = st.columns([1, 1, 1])
    # player cards
    for i, (player_name, player) in enumerate(st.session_state.players.items()):
        col_idx = i
        with cols[col_idx]:
            html = CSS_card +  f"""
                    <div class="players-container">
                        <div class="player-card">
                            <div class="avatar-container">
                                <div class="gender-badge">{player.gender_emoji}</div>
                                <div class="avatar-icon">{player.avatar_emoji}</div>
                                <div class="menu-dots">⋯</div>
                            </div>
                            <div class="card-bottom">
                                <div class="player-name">{player.name}</div>
                                <div class="player-gender">{player.gender}</div>
                                <div class="stats-row">
                                    <div class="stat-item" data-id="clothes" title="Vêtements restants">{CLOTHES_EMOJI} {player.clothes_nb}</div>
                                    <div class="stat-item" data-id="practices" "title="Pratiques">{PRACTICES_EMOJI} {player.practices_nb}</div>
                                    <div class="stat-item" data-id="secret" title="Secret">{SECRET_EMOJI if player.has_secret else ' '}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    """
            JS = """
            export default function(component) {
                const { data, setTriggerValue, parentElement } = component;    
                parentElement.innerHTML = data;                
                const dots = parentElement.querySelector('.menu-dots');
                if (dots) {
                    dots.addEventListener('click', (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        setTriggerValue('menu_clicked', Date.now());
                    });
                }
                
                const statItems = parentElement.querySelectorAll('.stat-item');
                statItems.forEach(item => {
                    item.addEventListener('click', () => {
                        // On récupère l'identifiant stocké dans le data-id
                        const statId = item.getAttribute('data-id');
                        
                        // On envoie un objet contenant l'ID et un timestamp pour forcer l'update
                        setTriggerValue('item_clicked', {
                            id: statId,
                            time: Date.now()
                        });
                    });
                });
            }
            """
            add_player_component = st.components.v2.component(
                f"change_{player.name}_component",
                css=CSS_card,
                js=JS,
            )
            res = add_player_component(data=html, key=f"player_card_{player_name}", on_clicked_change=lambda: None)

            if hasattr(res, "menu_clicked") and res.menu_clicked:
                if res.menu_clicked:
                    edit_player_details(player)

            if hasattr(res, "item_clicked") and res.item_clicked:
                clicked_info = res.item_clicked
                stat_name = clicked_info['id']
                #todo: do a action specific to stat_name -> open a specific dialog, ...
                if res.item_clicked:
                    edit_player_details(player)

    # config card
    with cols[2]:
        game = st.session_state.game
        html = CSS_card + f"""
                <div class="players-container">
                    <div class="player-card">
                        <div class="avatar-container">
                            <div class="avatar-icon">⚙️</div>
                            <div class="menu-dots">⋯</div>
                        </div>
                        <div class="card-bottom">
                            <div class="player-name">Configuration</div>
                            <div class="player-gender"> ⚙️ </div>
                            <div class="stats-row">
                                <div class="stat-item">🔥 {game.intensity}</div>
                                <div class="stat-item">⏱️ {game.duration}</div>
                                <div class="stat-item">🪀 {game.objects_nb}</div>
                            </div>
                        </div>
                    </div>
                </div>
            """
        JS = """
            export default function(component) {
                const { data, setTriggerValue, parentElement } = component;    
                parentElement.innerHTML = data;                
                const dots = parentElement.querySelector('.menu-dots');
                if (dots) {
                    dots.addEventListener('click', (e) => {
                        // Empêche l'événement de remonter aux parents
                        e.preventDefault();
                        e.stopPropagation();

                        // Envoi de la valeur à Streamlit
                        setTriggerValue('menu_clicked', Date.now());
                    });
                }
            }
            """

        add_parameter_component = st.components.v2.component(
            f"change_parameter_component",
            css=CSS_card,
            js=JS,
        )
        res = add_parameter_component(data=html, key=f"parameter_card", on_clicked_change=lambda: None)

        if hasattr(res, "menu_clicked") and res.menu_clicked:
            if res.menu_clicked:
                edit_game_parameters()

        # if st.button(f"✏️ Modifier les paramètres", use_container_width=True):
        #     edit_game_parameters()

    # todo: add in style.css
    st.markdown("""
            <style>
            /* Cible TOUS les boutons, mais on va le rendre très spécifique après */
            button[kind] {
                transition: all 0.3s ease !important;
            }
    
            /* Gros bouton rose flashy */
            div[data-testid="stButton"] > button[kind="primary"] {
                width: 100% !important;
                max-width: 520px !important;
                min-height: 90px !important;
                font-size: 2.1rem !important;
                font-weight: 700 !important;
                padding: 1.2rem 3rem !important;
                border-radius: 999px !important;
                background: linear-gradient(135deg, #ec4899, #db2777) !important;
                color: white !important;
                border: none !important;
                box-shadow: 0 10px 30px rgba(236, 72, 153, 0.45) !important;
                margin: 2.5rem auto !important;
                display: block !important;
            }
    
            div[data-testid="stButton"] > button:hover {
                background: linear-gradient(135deg, #f472b6, #e11d48) !important;
                transform: translateY(-4px) scale(1.04) !important;
                box-shadow: 0 18px 45px rgba(236, 72, 153, 0.65) !important;
            }
    
            div[data-testid="stButton"] > button:active {
                transform: translateY(2px) !important;
                box-shadow: 0 6px 20px rgba(236, 72, 153, 0.4) !important;
            }
    
            /* Centrage du conteneur si besoin */
            .center-start-btn {
                text-align: center;
            }
            </style>
        """, unsafe_allow_html=True)

    #todo: modify this ugly button ...
    cols_buttons = st.columns([1, 1, 1, 1, 1])
    if cols_buttons[2].button(
            "🚀 START",
            key="start_the_game",
            use_container_width=False,
            type="primary"
    ):
        st.session_state.game_started = True
        st.rerun()


    if cols_buttons[4].button(
            "🚀 ADD QUESTIONS",
            key="add_question",
            use_container_width=False,
            type="primary"
    ):
        add_action_question()


def start_game_config():
    st.set_page_config(layout="wide")

    tab_config, tab_action_question_list = st.tabs(["Configuration", "Actions et questions"])

    with tab_config:
        config_tab()

    with tab_action_question_list:
        view_action_question()