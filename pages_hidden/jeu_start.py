import streamlit as st
import random

from utils.data import GameAction, GameQuestion

emojis_niveaux = [
    "🔥",     # N1 – échauffement / teasing
    "✋",     # N2 – baisers / zones sensibles
    "👄",     # N3 – caresses / mains
    "😈",     # N4 – plus intense / défis
    "💦"      # N5 – final / orgasme / climax
]

gender_mapper = {"M": "Garçon", "F": "Fille"}

markdown_questions = """
    <style>
    .question-container {
        background: white;
        border-radius: 16px;
        padding: 2rem 1.5rem;
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
        margin: 1.5rem 0;
        max-width: 700px;
    }
    .question-title {
        color: #831843;
        font-size: 1.55rem;
        font-weight: 700;
        margin-bottom: 1.8rem;
        line-height: 1.35;
    }
    </style>
"""
markdown_button = """
            <style>
            button[kind] {
                transition: all 0.3s ease !important;
            }
    
            /* Gros bouton rose flashy */
            div[data-testid="stButton"] > button[kind="primary"]{
                width: 100% !important;
                max-width: 520px !important;
                min-height: 50px !important;
                font-size: 2.1rem !important;
                font-weight: 500 !important;
                padding: 1.2rem 3rem !important;
                border-radius: 999px !important;
                background: linear-gradient(135deg, #ec4899, #db2777) !important;
                color: white !important;
                border: none !important;
                box-shadow: 0 10px 30px rgba(236, 72, 153, 0.45) !important;
                margin: 0.1rem auto !important;
                display: block !important;
            }
            
            div[data-testid="stButton"] > button[kind="secondary"]{
                width: 100% !important;
                max-width: 520px !important;
                min-height: 40px !important;
                font-size: 2.1rem !important;
                font-weight: 500 !important;
                padding: 0.02rem 0.1rem !important;
                border-radius: 999px !important;
                background: linear-gradient(135deg, #c986f0, #aa2af5) !important;
                color: white !important;
                border: none !important;
                margin: 0.01rem auto !important;
                display: block !important;
            }
    
            div[data-testid="stButton"] > button[kind="primary"]:hover {
                background: linear-gradient(135deg, #f472b6, #e11d48) !important;
                transform: translateY(-4px) scale(1.04) !important;
                box-shadow: 0 18px 45px rgba(236, 72, 153, 0.65) !important;
            }
            
            div[data-testid="stButton"] > button[kind="secondary"]:hover {
                background: linear-gradient(135deg, #e6c5fa, #9b02f5) !important;
                transform: translateY(-4px) scale(1.04) !important;
            }
    
            div[data-testid="stButton"] > button:active {
                transform: translateY(2px) !important;
                box-shadow: 0 6px 20px rgba(236, 72, 153, 0.4) !important;
            }
    
            .center-start-btn {
                text-align: center;
            }
            </style>
        """
markdown_text = """
<style>
    .player-name   { color: #6366f1; font-weight: bold; }
    .receiver-name { color: #ef7444; font-weight: bold; }
    .time-limit    { color: #ef4444; font-weight: bold; }
    .repetitions   { color: #ef7444; font-weight: bold; }
</style>
"""

# reduce the padding on top of streamlit app
st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                    padding-left: 1rem;
                    padding-right: 1rem;
                }
        </style>
        """, unsafe_allow_html=True)

def pick_question() -> GameQuestion|None:
    level = st.session_state.game.current_level
    questions_ = st.session_state.game_data.questions_per_level[level]
    # filter by gender
    questions_ = [q_ for q_ in questions_ if (q_.gender == "B" or gender_mapper[q_.gender] == st.session_state.gender[
        st.session_state.game.current_player])]
    # filter by already asked
    questions_ = [q_ for q_ in questions_ if q_.id_ not in st.session_state.already_asked["Questions"]]
    try:
        return random.choice(questions_)
    except IndexError:
        return None

def pick_action() -> GameAction|None:
    level = st.session_state.game.current_level
    actions_ = st.session_state.game_data.actions_per_level[level]
    # filter by gender
    actions_ = [q_ for q_ in actions_ if (q_.gender == "B" or gender_mapper[q_.gender] == st.session_state.gender[
        st.session_state.game.current_player])]
    # filter by already asked
    actions_ = [q_ for q_ in actions_ if q_.id_ not in st.session_state.already_asked["Actions"]]
    try:
        return random.choice(actions_)
    except IndexError:
        return None

def show_question(question: GameQuestion):
    st.session_state.game.current_action_question = ["Question", question.id_]
    text = question.text
    text = text.replace("{player}", f"""<span class="player-name">{st.session_state.game.current_player}</span>""")
    text = text.replace("{receiver}",
                        f"""<span class="receiver-name">{st.session_state.game.current_receiver}</span>""")

    st.markdown(f'<div class="question-container">'
                f'<div class="question-title">{question.title}</div>'
                f'{text}'
                f'</div>', unsafe_allow_html=True)

    key_selected = f"selected_{question.id_}"
    if key_selected not in st.session_state:
        st.session_state[key_selected] = None

    for opt in question.possibilities:
        is_selected = st.session_state[key_selected] == opt
        if st.button(opt, key=f"opt_{question.id_}_{opt.replace(' ', '_')}",
                     use_container_width=True, type="secondary" if not is_selected else "primary",
                     ):
            st.session_state[key_selected] = opt
            st.rerun()

def show_action(action: GameAction):
    st.session_state.game.current_action_question = ["Action", action.id_]
    text = action.text
    if action.timer is not None:
        timer = random.randint(action.timer[0], action.timer[1])
        text = text.replace("{time}", f"""<span class="time-limit">{timer}</span>""")
    if action.repetitions is not None:
        repetitions = random.randint(action.repetitions[0], action.repetitions[1])
        text = text.replace("{nb}", f"{repetitions}")
    # with st.container():
    text = text.replace("{player}", f"""<span class="player-name">{st.session_state.game.current_player}</span>""")
    text = text.replace("{receiver}", f"""<span class="receiver-name">{st.session_state.game.current_receiver}</span>""")
    st.markdown(f'<div class="question-container">'
                f'<div class="question-title">{action.title}</div>'
                f'{text}'
                f'</div>', unsafe_allow_html=True)

def show_progress():
    durations = [x_["n"] for _, x_ in st.session_state.game.levels_configs.items()]
    current_level = st.session_state.game.current_level
    current_level_idx = st.session_state.game.current_level_idx
    parts = [d / sum(durations) for d in durations]

    current_cursor = sum(parts[:current_level - 1]) + current_level_idx / durations[current_level - 1] * parts[current_level - 1]

    st.markdown(f"""
    <div style="
        display: flex;
        height: 52px;
        border-radius: 999px;
        overflow: hidden;
        background: #f1f5f9;
        margin: 0rem 0 1.0rem 0;
        position: relative;
        box-shadow: 0 3px 10px rgba(0,0,0,0.09);
        border: 1px solid #e2e8f0;
    ">
        {''.join(
                f'<div style="flex: {p:.3f}; background: {"linear-gradient(90deg, #c084fc, #ec4899)" if i+1 <= current_level else "#e2e8f0"}; '
                f'position: relative; border-right: 1px solid #cbd5e1;">'
                f'<div style="position:absolute; inset:0; display:flex; align-items:center; justify-content:center; color:{"white" if i+1 <= current_level else "#64748b"}; font-weight:bold; font-size:0.95rem;">'
                f'{emojis_niveaux[i]}'
                f'</div></div>'
                for i, p in enumerate(parts)
        )}
        <!-- Flèche positionnée au milieu du niveau actuel -->
        <div style="
            position: absolute;
            top: -22px;
            left: {current_cursor * 100:.1f}%;
            transform: translateX(-50%);
            font-size: 2.1rem;
            transition: left 0.6s ease;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.25));
        ">🔻</div>
    </div>
    """, unsafe_allow_html=True)

def start_game():
    with st.sidebar:
        if st.button("Recommencer le jeu", type="primary"):
            st.session_state.game_started = False
            st.rerun()

    if "pick_new" not in st.session_state:
        st.session_state.pick_new = True

    if "already_asked" not in st.session_state:
        st.session_state.already_asked = {"Questions": [], "Actions": []}

    st.set_page_config(layout="centered", initial_sidebar_state="collapsed")

    st.session_state.game.current_player = st.session_state.users[st.session_state.game.current_player_idx % 2]
    st.session_state.game.current_receiver = st.session_state.users[(st.session_state.game.current_player_idx + 1) % 2]

    # get current level
    current_level = st.session_state.game.current_level
    question_action_ratio = st.session_state.game.levels_configs[current_level]["question_action_ratio"]

    # load CSS
    st.markdown(markdown_questions, unsafe_allow_html=True)
    st.markdown(markdown_button, unsafe_allow_html=True)
    st.markdown(markdown_text, unsafe_allow_html=True)

    # progress bar
    show_progress()

    # pick a question or action
    if st.session_state.pick_new is True:
        question = pick_question()
        action = pick_action()
        st.session_state.pick_new = False
    else:
        if st.session_state.game.current_action_question[0] == "Action":
            action = st.session_state.game_data.actions_per_id[st.session_state.game.current_action_question[1]]
            question = None
        elif st.session_state.game.current_action_question[0] == "Question":
            question = st.session_state.game_data.questions_per_id[st.session_state.game.current_action_question[1]]
            action = None
        else:
            raise ValueError(f"Invalid {st.session_state.game.current_action}")


    if (question is None) and (action is None):
        raise ValueError(f"No question or action available at level {current_level}...")
    elif question is None:
        show_action(action)
        st.session_state.game.question_action = "Action"
    elif action is None:
        show_question(question)
        st.session_state.game.question_action = "Question"
    else:
        if random.uniform(0, 1) > question_action_ratio:
            show_action(action)
            st.session_state.game.question_action = "Action"
        else:
            show_question(question)
            st.session_state.game.question_action = "Question"

    # Barre d'actions
    col1, _, col2 = st.columns([1, 0.1, 1])
    with col1:
        if st.button("↻ Relancer", key="reroll", type="primary", use_container_width=True):
            st.session_state.pick_new = True
            st.rerun()

    with col2:
        if st.button("Valider →", key="next", type="primary", use_container_width=True):
            st.session_state.game.finish_step()
            st.session_state.pick_new = True
            # remove action/question
            if st.session_state.game.question_action == "Question":
                st.session_state.already_asked["Questions"].append(question.id_)
            else:
                st.session_state.already_asked["Actions"].append(action.id_)
            st.rerun()
