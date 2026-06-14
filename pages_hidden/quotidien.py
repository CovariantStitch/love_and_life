import datetime

import pandas as pd
import streamlit as st

from utils.compute_points import on_tasks_changed
from utils.css import custom_container, custom_button, task_card


def show_task(task: pd.Series, task_index: int, period: str, col_task):
    with col_task.container(border=True, key=f"task_{task_index}_{period}"):
        col1, col2 = st.columns([3, 1])

        # show information of the task
        with col1:
            due_date = task.Due_date
            html_card = task_card(name=task.Name, overdue=(due_date < datetime.datetime.now() and not task.Done),
                                  due_text=due_date.strftime("%d/%m/%Y"), points=task.Points,
                                  description=task.Description)

            with open('./assets/style.css') as f:
                css_card = f.read()
            css_card = f"""<style>{css_card}</style>"""
            js_card = """
            export default function(component) {
                const { data, setTriggerValue, parentElement } = component;    
                parentElement.innerHTML = data;                
                const dots = parentElement.querySelector('.task-dots');
                if (dots) {
                    dots.addEventListener('click', (e) => {
                        e.preventDefault();
                        e.stopPropagation();                        
                        setTriggerValue('title_clicked', Date.now());
                    });
                }
            }
            """
            html_card = css_card + html_card

            modify_task_component = st.components.v2.component(
                f"change_task_{task.Name}_component",
                css=css_card,
                js=js_card,
            )

            res = modify_task_component(data=html_card, key=f"card_{task_index}_{period}",
                                        on_clicked_change=lambda: None)

            if hasattr(res, "title_clicked") and res.title_clicked:
                if res.title_clicked:
                    edit_task(task, task_index)

        # allows interactions: is the dask done ? By who ?
        with col2:
            current_done = task.Done
            # st.checkbox("Fait", value=current_done, key=f"done_{task_index}_{period}")

            # options = list(st.session_state.points.keys()) + ["Ensemble"]
            # index = None if task.Done_by is None else options.index(task.Done_by)
            # done_by = st.selectbox(label="Fait par", options=options,
            #                        key=task.Name + f"_{task_index}_user_{period}",
            #                        disabled=not task.Done, index=index
            #                        )

            if current_done:
                default_value_pills = st.session_state.df_tasks.loc[task_index, "Done_by"]
            else:
                default_value_pills = "Pas fait"

            #todo: think of a better option as the one just below to do everything with a single click
            st.pills(options=["Pas fait", "Florian", "Alice", "Ensemble"], label="Fait par ...",
                     default=default_value_pills, key=f"task_{task_index}_{period}_toggle", label_visibility="collapsed")

            # deal with a task marked as down on the screen, but not in data base
            if (st.session_state[f"task_{task_index}_{period}_toggle"] != "Pas fait") & (not task.Done):
                st.session_state.df_tasks.loc[task_index, "Done"] = True
                st.session_state.df_tasks.loc[task_index, "Done_by"] = st.session_state[f"task_{task_index}_{period}_toggle"]
                on_tasks_changed()
                st.rerun()
            # deal with a task marked as not down on the screen, but down in database
            elif (st.session_state[f"task_{task_index}_{period}_toggle"] == "Pas fait") & (task.Done):
                st.session_state.df_tasks.loc[task_index, "Done"] = False
                st.session_state.df_tasks.loc[task_index, "Done_by"] = None
                on_tasks_changed()
                st.rerun()
            # deal with a task marked as down on the screen, but with a different user
            if st.session_state[f"task_{task_index}_{period}_toggle"] != "Pas fait":
                if st.session_state.df_tasks.loc[task_index, "Done_by"] != st.session_state[f"task_{task_index}_{period}_toggle"]:
                    st.session_state.df_tasks.loc[task_index, "Done_by"] = st.session_state[f"task_{task_index}_{period}_toggle"]
                    on_tasks_changed()
                    st.rerun()

        if current_done:
            card_color = 'rgba(114, 219, 153,0.1)'
        elif due_date < datetime.datetime.now():
            card_color = 'rgba(219, 135, 116,0.1)'
        else:
            card_color = 'rgba(237, 207, 138,0.1)'


        # apply the container CSS
        css = custom_container(container_id=f"task_{task_index}_{period}", container_color=card_color)
        st.markdown(css, unsafe_allow_html=True)

# add a card to add some tasks
def add_card_for_task(col, kind):
    with col.container(border=True, key=f"action_add_task_{kind}"):
        card_color = 'rgba(255, 255, 255, 0.1)'
        css_container = custom_container(container_id=f"action_add_task_{kind}", container_color=card_color)
        st.markdown(css_container, unsafe_allow_html=True)

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
            margin: 5px;
            cursor: pointer;
            height: 100px;
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
        add_task_button = st.components.v2.component(
            "add_task_button",
            css=CSS,
            js=JS,
        )
        result = add_task_button(on_clicked_change=lambda: None)

        if result.clicked:
            add_task()

@st.dialog("Ajouter une nouvelle tâche")
def add_task():
    name = st.text_input("Titre de la tâche")
    description = st.text_input("Description")
    date_points_cols = st.columns(2)
    due_date = date_points_cols[0].datetime_input("Date d'échéance")
    points = date_points_cols[1].number_input("Nombre de points", min_value=0, max_value=100, value=10, step=1)
    recurrent_cols = st.columns([1, 2])
    recurrent_cols[0].write("")
    recurrent = recurrent_cols[0].checkbox("Tâche recurrente")
    recurrent_delay = recurrent_cols[1].number_input("Tous les X jours", value=7, min_value=1, max_value=120, step=1)
    if st.button("Ajouter"):
        due_date = pd.to_datetime(due_date)
        if not recurrent:
            recurrent_delay = None
        st.session_state.df_tasks.loc[len(st.session_state.df_tasks)] = [name, False, points, due_date, None,
                                                                         description, recurrent_delay]
        on_tasks_changed()
        st.rerun()



@st.dialog("Editer une tâche")
def edit_task(task_, id_):
    name = st.text_input("Titre de la tâche", value=task_.Name)
    description = st.text_input("Description", value=task_.Description)
    date_points_cols = st.columns(2)
    due_date = date_points_cols[0].datetime_input("Date d'échéance", task_.Due_date)
    points = date_points_cols[1].number_input("Nombre de points", min_value=0, max_value=100, value=task_.Points,
                                              step=1)
    recurrent_cols = st.columns([1, 2])
    recurrent_cols[0].write("")
    recurrent = recurrent_cols[0].checkbox("Tâche recurrente", value=True if task_.Recurrent else False)
    recurrent_delay = recurrent_cols[1].number_input("Tous les X jours", min_value=1, max_value=120, step=1,
                                                     value=int(task_.Recurrent) if task_.Recurrent else 1,)
    if st.button("Modifier"):
        due_date = pd.to_datetime(due_date)
        if not recurrent:
            recurrent_delay = None
        st.session_state.df_tasks.loc[id_] = [name, False, points, due_date, None, description, recurrent_delay]
        on_tasks_changed()
        st.rerun()

# page config
st.set_page_config(page_title="Au quotidien", page_icon="📈", layout="wide")

# create tabs
all, day, week, month, late = st.tabs(["Toutes les tâches", "Tâches du jour", "Tâches de la semaine", "Tâches du mois",
                                       "Tâches en retard"])

# get some useful data
current_day = datetime.date.today()
df_data = st.session_state.df_tasks


# add task + filter tasks (first load the CSS for the button and apply for the page)
css_button = custom_button()
st.markdown(css_button, unsafe_allow_html=True)
# not useful so far
# with st.sidebar:
#     if st.button("Ajouter une tâche", type="primary", use_container_width=True):
#         add_task()

with all:
    with st.container(border=True):
        cols_filters = st.columns(3)
        show_done = cols_filters[0].checkbox("Afficher les tâches terminées", value=False)
        show_not_done = cols_filters[0].checkbox("Afficher les tâches non terminées", value=True)
        min_points = cols_filters[1].slider("Points minimum", min_value=0,
                               max_value=int(df_data['Points'].max()) if 'Points' in df_data else 100, value=0)
        date_filter = cols_filters[2].slider("Filtrer par date", min_value=current_day - datetime.timedelta(days=15),
                                             max_value = current_day + datetime.timedelta(days=15),
                                             value=(current_day, current_day + datetime.timedelta(days=5)))
    # filter with navigation filters
    df_ = df_data.copy()
    if not show_done:
        df_ = df_[df_['Done'] != True]
    if not show_not_done:
        df_ = df_[df_['Done'] != False]
    df_ = df_[df_['Points'] >= min_points]
    df_ = df_[(df_['Due_date'] >= pd.to_datetime(date_filter[0])) & (df_['Due_date'] <= pd.to_datetime(date_filter[1]))]

    cols_task = st.columns(3)
    i_ = 0
    for i_, (task_index, task) in enumerate(df_.iterrows()):
        show_task(task, task_index, "all", cols_task[i_ % len(cols_task)])
    add_card_for_task(col=cols_task[(i_+1) % len(cols_task)], kind="all")

with day:
    cols_task = st.columns(3)
    df_ = df_data[df_data["Due_date"].dt.date == current_day]
    for i_, (task_index, task) in enumerate(df_.iterrows()):
        show_task(task, task_index, "day", cols_task[i_ % len(cols_task)])

with week:
    cols_task = st.columns(3)
    filter1 = df_data["Due_date"].dt.date - current_day <= datetime.timedelta(days=7)
    filter2 = df_data["Due_date"].dt.date - current_day >= datetime.timedelta(days=0)
    df_ = df_data[filter1 & filter2]
    for i_, (task_index, task) in enumerate(df_.iterrows()):
        show_task(task, task_index, "week", cols_task[i_ % len(cols_task)])

with month:
    cols_task = st.columns(3)
    filter1 = df_data["Due_date"].dt.date - current_day < datetime.timedelta(days=30)
    filter2 = df_data["Due_date"].dt.date - current_day >= datetime.timedelta(days=0)
    df_ = df_data[filter1 & filter2]
    for i_, (task_index, task) in enumerate(df_.iterrows()):
        show_task(task, task_index, "mois", cols_task[i_ % len(cols_task)])

with late:
    cols_task = st.columns(3)
    filter1 = df_data["Due_date"].dt.date < current_day
    filter2 = df_data["Done"] == False
    df_ = df_data[filter1 & filter2]
    for i_, (task_index, task) in enumerate(df_.iterrows()):
        show_task(task, task_index, "late", cols_task[i_ % len(cols_task)])
