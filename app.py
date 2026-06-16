from pathlib import Path
import datetime as dt

import numpy as np
import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth


# Récupération des secrets
config = {
    "cookie": {
        "name": st.secrets["auth"]["cookie_name"],
        "key": st.secrets["auth"]["cookie_key"],
        "expiry_days": st.secrets["auth"]["cookie_expiry_days"]
    },
    "credentials": {
        "usernames": st.secrets["auth"]["credentials"]["usernames"].to_dict()
    }
}

# Initialisation de l'authenticator
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

try:
    authenticator.login()
except Exception as e:
    st.error(e)

if st.session_state.get('authentication_status'):
    pass
elif st.session_state.get('authentication_status') is False:
    st.error('Username/password is incorrect')
elif st.session_state.get('authentication_status') is None:
    st.warning('Veuillez vous connecter')


if st.session_state.authentication_status:

    progress_bar = st.progress(0, text="Chargement des fichiers")
    percent_complete = 0
    n_files_to_load = 5

    # define if the app runs locally or on the server
    is_local = False
    if is_local:
        st.session_state.is_local = True
    else:
        st.session_state.is_local = False
        from utils.gsheets import connection_gsheets
        connection_gsheets()

    from utils.compute_points import compute_points
    from utils.data import parse_player
    from utils.persistence import save_tasks

    # load css file
    with open('./assets/style.css') as f:
        css = f.read()
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

    # TODO: instead of loading each file one after the other -> multi-thread loading (possible with streamlit community ?)

    def load_tasks():
        if st.session_state.is_local:
            df = pd.read_csv(Path(__file__).parent / "resources" / "tasks.csv")
        else:
            df = st.session_state.gsheets_connection.read(worksheet="tasks")
        df["Done"] = df["Done"].astype(bool)
        df["Points"] = df["Points"].astype(int)
        try:
            df["Due_date"] = pd.to_datetime(df["Due_date"], format='%d/%m/%Y %H:%M:%S')
        except:
            df["Due_date"] = pd.to_datetime(df["Due_date"], format='%d/%m/%Y')
        df = df.replace({np.nan: None})
        new_rows = []
        for _, row in df.iterrows():
            # if a task is flagged as Recurrent & flagged as Done & not already re-scheduled -> need to be rescheduled
            if (row["Recurrent"] is not None) & row["Done"]:
                # checking that the task has not been rescheduled so far
                if df[df["Name"] == row["Name"]]["Due_date"].max() == row["Due_date"]:
                    new_row = row.copy()
                    new_row["Due_date"] += dt.timedelta(days=row["Recurrent"])
                    new_row["Done"] = False
                    new_row["Done_by"] = None
                    new_rows.append(new_row)
        df = pd.concat([df, pd.DataFrame(new_rows)])
        return df, len(new_rows) > 0

    if 'user' not in st.session_state:
        st.session_state.user = st.session_state.username.capitalize()
        st.session_state.other_user = "Alice" if st.session_state.username == "florian" else "Florian"
        

    if 'df_tasks' not in st.session_state:
        df_tasks, rescheduled = load_tasks()
        percent_complete += 1. / n_files_to_load
        progress_bar.progress(value=percent_complete)
        st.session_state.df_tasks = df_tasks
        if rescheduled:
            save_tasks()

    # necessary to compute points
    if 'points' not in st.session_state:
        if st.session_state.is_local:
            st.session_state.df_users = pd.read_csv(Path(__file__).parent / "resources" / "players.csv")
        else:
            st.session_state.df_users = st.session_state.gsheets_connection.read(worksheet="players")
        percent_complete += 1. / n_files_to_load
        progress_bar.progress(value=percent_complete)

        st.session_state['users'] = list(st.session_state.df_users["Name"].unique())
        st.session_state['points'] = {user: 0 for user in st.session_state.users}
        st.session_state['players'] = {row["Name"]: parse_player(row) for _, row in st.session_state.df_users.iterrows()}
        st.session_state["gender"] = {row["Name"]: row["Gender"] for _, row in st.session_state.df_users.iterrows()}

    # necessary to compute points
    if "list_challenges_and_dares" not in st.session_state:
        if st.session_state.is_local:
            list_challenges_and_dares = pd.read_csv(Path(__file__).parent / "resources" / "liste_defis_et_gages.csv")
        else:
            list_challenges_and_dares = st.session_state.gsheets_connection.read(worksheet="liste_defis_et_gages")
        percent_complete += 1. / n_files_to_load
        progress_bar.progress(value=percent_complete)            
        list_challenges_and_dares = list_challenges_and_dares.replace(np.nan, None)
        st.session_state.list_challenges_and_dares = list_challenges_and_dares

    # necessary to compute points
    if "action_df" not in st.session_state:
        if st.session_state.is_local:
            actions_df = pd.read_csv(Path(__file__).parent / "resources" / "defis_et_gages.csv")
        else:
            actions_df = st.session_state.gsheets_connection.read(worksheet="defis_et_gages")
        percent_complete += 1. / n_files_to_load
        progress_bar.progress(value=percent_complete)            
        actions_df["Sent_date"] = pd.to_datetime(actions_df["Sent_date"])
        actions_df["Validate_date"] = pd.to_datetime(actions_df["Validate_date"])
        actions_df = actions_df.replace(np.nan, None)
        st.session_state.actions_df = actions_df

    compute_points()

    if "settings" not in st.session_state:
        if st.session_state.is_local:
            settings = pd.read_csv(Path(__file__).parent / "resources" / "settings.csv")
        else:
            settings = st.session_state.gsheets_connection.read(worksheet="settings")
        percent_complete += 1. / n_files_to_load
        progress_bar.progress(value=percent_complete)            
        settings["Value"] = settings["Value"].astype(int).astype(bool)
        st.session_state.settings = settings

    # load pages that are activated in settings
    available_pages = {}
    for _, row in st.session_state.settings.iterrows():
        if row["Value"] is True:
            if row["Category"] in available_pages.keys():
                available_pages[row["Category"]].append(st.Page(f"./pages_hidden/{row['Name']}.py", title=row["Title"], icon=row["Icon"]))
            else:
                available_pages[row["Category"]] = [st.Page(f"./pages_hidden/{row['Name']}.py", title=row["Title"], icon=row["Icon"])]


    if "admin" in st.session_state.roles:
        available_pages["⚙️ Paramètres"] = [st.Page("./pages_hidden/settings.py", title="Pages", icon="⚙️")]

    pg = st.navigation(available_pages)
    progress_bar.empty()


    st.markdown("""
        <style>
        .points-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 12px 24px;
            padding: 24px 0;
            align-items: center;
        }
        .points-card {
            background: white;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 4px 14px rgba(0,0,0,0.1);
            width: 100px;
            text-align: center;
            transition: transform 0.15s;
        }
        .points-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        }
        .points-name-container {
            position: relative;
            height: 60px;
            background: white;
            border-radius: 16px;
            width: 90px;
        }
        .points-player-name {
            font-size: 1.5rem;
            font-weight: 700;
            margin: 6px 0 12px;
            position: relative;
            z-index: 1;
        }
        .player-points {
            font-size: 1.5rem;
            font-weight: 700;
            margin: 6px 0 0px;
            position: relative;
            z-index: 1;
        }
        .card-point-bottom {
            background: #ec4899;
            color: white;
            padding: 0px 6px 6px;
            position: relative;
        }
        .card-point-bottom::before {
            content: "";
            position: absolute;
            top: -014px;
            left: 0;
            right: 0;
            height: 28px;
            background: #ec4899;
            border-radius: 60% 60% 0 0;
        }
        """, unsafe_allow_html=True)
    with st.sidebar:
        # todo: centrer les points, ajouter du css/html pour faire un joli visuel
        cols_points = st.columns(2)
        for i_, (user, points) in enumerate(st.session_state.points.items()):
            cols_points[i_].markdown(f"""
                                <div class="points-container">
                                    <div class="points-card">
                                            <div class="points-player-name">{user}</div>
                                        <div class="card-point-bottom">
                                            <div class="player-points">{int(points)}</div>
                                        </div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
        authenticator.logout(f"Se déconnecter de {st.session_state.username}")
        st.divider()

    pg.run()
