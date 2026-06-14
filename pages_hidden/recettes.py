import datetime as dt
from math import e
from pathlib import Path
from typing import Dict, Tuple, Optional

import pandas as pd
import streamlit as st


st.set_page_config(page_title="Recettes de la semaine", page_icon="🍲", layout="wide")
st.header("🍲 Les recettes de la semaine")
st.caption("Planifiez vos repas midi et soir pour les 7 prochains jours.")


DAY_NAMES = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
MEALS = ["Midi", "Soir"]
SlotKey = Tuple[int, str]
Recipe = Dict[str, str]

if st.session_state.is_local:
    DATA_DIR = Path(__file__).parent.parent / "resources"
    RECIPES_WEEK_FILE = DATA_DIR / "recipes_week.csv"
    RECIPES_LIBRARY_FILE = DATA_DIR / "recipes_library.csv"
else:
    RECIPES_WEEK_FILE = "recipes_week"
    RECIPES_LIBRARY_FILE = "recipes_library"

def _default_week_state() -> Dict[SlotKey, Optional[Recipe]]:
    """Crée un dict de base pour les 14 créneaux (sans recettes)."""
    return {(i, meal): None for i in range(7) for meal in MEALS}


def _load_from_files():
    """Charge recipes_week et recipes_library depuis les fichiers si présents.

    On stocke l'historique complet dans les CSV, mais on ne recharge ici
    que les recettes du jour J à J+6 dans recipes_week.
    """
    recipes_library: list[Recipe] = []
    recipes_week: Dict[SlotKey, Optional[Recipe]] = _default_week_state()
    
    # Bibliothèque de recettes
    try:
        if st.session_state.is_local:
            df_lib = pd.read_csv(RECIPES_LIBRARY_FILE)
        else:
            df_lib = st.session_state.gsheets_connection.read(worksheet=RECIPES_LIBRARY_FILE)
        for _, row in df_lib.iterrows():
            title = str(row.get("title", "")).strip()
            source_raw = row.get("source", "")
            source = "" if pd.isna(source_raw) else str(source_raw).strip()
            if title:
                recipes_library.append({"title": title, "source": source})
    except Exception:
        recipes_library = []

    # Planning de la semaine (on ne recharge que la fenêtre courante J..J+6)
    try:
        if st.session_state.is_local:
            df_week = pd.read_csv(RECIPES_WEEK_FILE)
        else:
            df_week = st.session_state.gsheets_connection.read(worksheet=RECIPES_WEEK_FILE)
        if "date" in df_week.columns:
            today = dt.date.today()
            end = today + dt.timedelta(days=6)

            # Conversion en date (sans heure)
            dates_series = pd.to_datetime(df_week["date"], errors="coerce").dt.date
            df_week = df_week.assign(_date=dates_series)

            # Filtre sur la fenêtre courante
            mask = (df_week["_date"] >= today) & (df_week["_date"] <= end)
            df_week_window = df_week[mask]

            for _, row in df_week_window.iterrows():
                row_date = row["_date"]
                if pd.isna(row_date):
                    continue
                meal = str(row.get("meal", "")).strip()
                if meal not in MEALS:
                    continue
                title = str(row.get("title", "")).strip()
                source_raw = row.get("source", "")
                source = "" if pd.isna(source_raw) else str(source_raw).strip()
                if not title:
                    continue
                day_index = (row_date - today).days
                if 0 <= day_index <= 6:
                    recipes_week[(day_index, meal)] = {
                        "title": title,
                        "source": source,
                    }
    except Exception:
        recipes_week = _default_week_state()

    st.session_state.recipes_library = recipes_library
    st.session_state.recipes_week = recipes_week


def _save_library_to_file():
    """Sauvegarde la bibliothèque de recettes dans un CSV."""
    lib: list[Recipe] = st.session_state.get("recipes_library", [])
    if not lib:
        df = pd.DataFrame(columns=["title", "source"])
    else:
        df = pd.DataFrame(lib, columns=["title", "source"])
    if st.session_state.is_local:
        df.to_csv(RECIPES_LIBRARY_FILE, index=False)
    else:
        st.session_state.gsheets_connection.update(worksheet=RECIPES_LIBRARY_FILE, data=df)


def _save_week_to_file():
    """Sauvegarde le planning de la semaine dans un CSV.

    On conserve l'historique : les lignes hors de la fenêtre J..J+6 ne sont
    jamais modifiées. Pour la fenêtre courante, le fichier reflète exactement
    l'état actuel de recipes_week.
    """
    week: Dict[SlotKey, Optional[Recipe]] = st.session_state.get("recipes_week", {})

    # Charge l'existant (historique complet)
    if st.session_state.is_local:
        df_existing = pd.read_csv(RECIPES_WEEK_FILE)
    else:
        df_existing = st.session_state.gsheets_connection.read(worksheet=RECIPES_WEEK_FILE)

    # Définition de la fenêtre courante
    today = dt.date.today()
    window_dates = [(today + dt.timedelta(days=i)).isoformat() for i in range(7)]

    # On supprime d'abord toutes les lignes pour les dates de la fenêtre
    if "date" in df_existing.columns:
        df_outside = df_existing[~df_existing["date"].isin(window_dates)]
    else:
        df_outside = pd.DataFrame(columns=["date", "meal", "title", "source"])

    # Puis on reconstruit toutes les lignes de la fenêtre à partir de l'état courant
    rows_window = []
    for (day_index, meal), recipe in week.items():
        date_str = (today + dt.timedelta(days=day_index)).isoformat()
        if recipe:
            rows_window.append(
                {
                    "date": date_str,
                    "meal": meal,
                    "title": recipe.get("title", ""),
                    "source": recipe.get("source", ""),
                }
            )
        # Si recipe est None, on ne rajoute pas de ligne => suppression logique

    if rows_window:
        df_window = pd.DataFrame(rows_window, columns=["date", "meal", "title", "source"])
        df_final = pd.concat([df_outside, df_window], ignore_index=True)
    else:
        df_final = df_outside

    if st.session_state.is_local:
        df_final.to_csv(RECIPES_WEEK_FILE, index=False)
    else:
        st.session_state.gsheets_connection.update(worksheet=RECIPES_WEEK_FILE, data=df_final)


def _init_state():
    """Initialise les structures de base dans la session, en utilisant les fichiers si possibles."""
    if "recipes_library" in st.session_state and "recipes_week" in st.session_state:
        return
    _load_from_files()


_init_state()


def get_week_slots():
    """Retourne la liste des créneaux (jour, repas, date) pour les 7 prochains jours."""
    today = dt.date.today()
    slots = []
    for i in range(7):
        date = today + dt.timedelta(days=i)
        # Nom du jour en français (on mappe sur DAY_NAMES en partant de lundi)
        weekday_idx = (date.weekday()) % 7  # 0 = lundi
        label_day = DAY_NAMES[weekday_idx]
        for meal in MEALS:
            slots.append(
                {
                    "day_index": i,
                    "day_label": label_day,
                    "date": date,
                    "meal": meal,
                }
            )
    return slots


@st.dialog("Choisir une recette")
def recipe_dialog(day_index: int, meal: str):
    slots = get_week_slots()
    slot_info = next(
        s for s in slots if s["day_index"] == day_index and s["meal"] == meal
    )
    current_recipe = st.session_state.recipes_week[(day_index, meal)]

    st.subheader(
        f"{slot_info['day_label']} {slot_info['date'].strftime('%d/%m')} – {meal}"
    )

    col_existing, col_new = st.columns(2)
    use_existing = col_existing.radio(
        "Type de recette",
        options=["Depuis la sélection", "Nouvelle recette"],
        index=0 if st.session_state.recipes_library else 1,
        key=f"choice_type_{day_index}_{meal}",
    )

    selected_recipe: Optional[Recipe] = None

    if use_existing == "Depuis la sélection":
        if not st.session_state.recipes_library:
            st.info("Aucune recette enregistrée pour le moment. Ajoutez-en une nouvelle.")
        else:
            options = [
                f"{r['title']} – {r['source']}" if r.get("source") else r["title"]
                for r in st.session_state.recipes_library
            ]
            default_index = 0
            if current_recipe and current_recipe in st.session_state.recipes_library:
                default_index = st.session_state.recipes_library.index(current_recipe)

            idx = st.selectbox(
                "Sélectionnez une recette existante",
                options=list(range(len(options))),
                format_func=lambda i: options[i],
                index=default_index if st.session_state.recipes_library else 0,
                key=f"existing_recipe_{day_index}_{meal}",
            )
            selected_recipe = st.session_state.recipes_library[idx]
    else:
        st.markdown("---")

        st.markdown("#### Nouvelle recette")
        new_title = st.text_input(
            "Titre de la recette",
            value=current_recipe["title"] if current_recipe else "",
            key=f"title_{day_index}_{meal}",
        )
        new_source = st.text_input(
            "Où la trouver ? (lien, livre, page…)",
            value=current_recipe.get("source", "") if current_recipe else "",
            key=f"source_{day_index}_{meal}",
        )

    col_left, col_right, col_delete = st.columns([2, 2, 1])
    with col_left:
        if st.button("Enregistrer pour ce créneau", type="primary"):
            if use_existing == "Depuis la sélection" and selected_recipe is not None:
                recipe = selected_recipe
            else:
                if not new_title.strip():
                    st.warning("Merci de renseigner au minimum un titre de recette.")
                    st.stop()
                recipe = {"title": new_title.strip(), "source": new_source.strip()}
                # On ajoute en bibliothèque si elle n'existe pas déjà
                if recipe not in st.session_state.recipes_library:
                    st.session_state.recipes_library.append(recipe)
                    _save_library_to_file()

            st.session_state.recipes_week[(day_index, meal)] = recipe
            _save_week_to_file()
            st.rerun()

    with col_right:
        if st.button("Dupliquer sur toute la semaine"):
            if not new_title.strip() and not selected_recipe:
                st.warning("Choisissez ou créez d'abord une recette.")
                st.stop()
            if use_existing == "Depuis la sélection" and selected_recipe is not None:
                recipe = selected_recipe
            else:
                recipe = {"title": new_title.strip(), "source": new_source.strip()}
                if recipe not in st.session_state.recipes_library:
                    st.session_state.recipes_library.append(recipe)
                    _save_library_to_file()
            for key in st.session_state.recipes_week.keys():
                st.session_state.recipes_week[key] = recipe
            _save_week_to_file()
            st.rerun()

    with col_delete:
        if current_recipe and st.button("🗑️", help="Supprimer la recette de ce créneau"):
            st.session_state.recipes_week[(day_index, meal)] = None
            _save_week_to_file()
            st.rerun()


@st.dialog("Modifier la recette")
def edit_recipe_dialog(day_index: int, meal: str):
    slots = get_week_slots()
    slot_info = next(
        s for s in slots if s["day_index"] == day_index and s["meal"] == meal
    )
    current_recipe = st.session_state.recipes_week[(day_index, meal)]

    if not current_recipe:
        st.info("Aucune recette n'est associée à ce créneau pour le moment.")
        return

    st.subheader(
        f"{slot_info['day_label']} {slot_info['date'].strftime('%d/%m')} – {meal}"
    )

    title = st.text_input(
        "Titre de la recette",
        value=current_recipe.get("title", ""),
        key=f"edit_title_{day_index}_{meal}",
    )
    source = st.text_input(
        "Où la trouver ? (lien, livre, page…)",
        value=current_recipe.get("source", ""),
        key=f"edit_source_{day_index}_{meal}",
    )

    col_save, col_delete = st.columns([3, 1])
    with col_save:
        if st.button("Enregistrer les modifications", type="primary"):
            if not title.strip():
                st.warning("Merci de renseigner au minimum un titre de recette.")
                st.stop()

            updated = {"title": title.strip(), "source": source.strip()}
            st.session_state.recipes_week[(day_index, meal)] = updated

            # Met à jour ou ajoute dans la bibliothèque
            lib = st.session_state.recipes_library
            if current_recipe in lib:
                idx = lib.index(current_recipe)
                lib[idx] = updated
            elif updated not in lib:
                lib.append(updated)
            st.session_state.recipes_library = lib

            _save_library_to_file()
            _save_week_to_file()
            st.rerun()

    with col_delete:
        if st.button("🗑️ Supprimer ce créneau"):
            st.session_state.recipes_week[(day_index, meal)] = None
            _save_week_to_file()
            st.rerun()


def render_grid():
    """Affiche la grille des 7 jours x midi/soir avec un style sympa."""
    slots = get_week_slots()

    CSS = """
    <style>
    .meal-grid {
        display: grid;
        grid-template-columns: repeat(7, minmax(0, 1fr));
        gap: 12px;
        margin-top: 1.5rem;
    }
    .meal-card {
        border-radius: 14px;
        background: linear-gradient(135deg, #f9fafb, #eef2ff);
        padding: 10px 12px;
        box-shadow: 0 4px 12px rgba(15,23,42,0.08);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 100px;
        text-align: center;
    }
    .meal-card:hover {
        cursor: pointer;
    }
    .meal-card-empty {
        border: 2px dashed #e5e7eb;
        background: #f9fafb;
        align-items: center;
        text-align: center;
        border-radius: 8px;
    }
    .meal-card-header {
        font-size: 0.8rem;
        font-weight: 600;
        color: #6b7280;
        margin-bottom: 4px;
    }
    .meal-title {
        font-size: 0.98rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 4px;
    }
    .meal-source {
        font-size: 0.82rem;
        color: #4b5563;
    }
    .plus-big {
        font-size: 2rem;
        color: #9ca3af;
        cursor: pointer;
    }
    .meal-click-area {
        cursor: pointer;
    }
    .meal-click-area:hover .plus-big,
    .meal-click-area:hover .meal-title {
        color: #ec4899;
    }
    </style>
    """

    JS = """
    export default function(component) {
        const { data, setTriggerValue, parentElement } = component;    
        parentElement.innerHTML = data;                
        const clickable = parentElement.querySelector('.meal-click-area');
        if (clickable) {
            clickable.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                setTriggerValue('clicked', Date.now());
            });
        }
    }
    """

    # Inject CSS une fois pour la page
    st.markdown(CSS, unsafe_allow_html=True)

    # Composant custom pour rendre toute la carte (ou le "+") cliquable
    meal_slot_component = st.components.v2.component(
        "meal_slot_button",
        css=CSS,
        js=JS,
    )

    # Ligne d'en-tête : jours
    header_cols = st.columns(7)
    today = dt.date.today()
    for i in range(7):
        date = today + dt.timedelta(days=i)
        weekday_idx = (date.weekday()) % 7
        header_cols[i].markdown(
            f"**{DAY_NAMES[weekday_idx]}**\n\n"
            f"<span style='font-size:0.8rem;color:#6b7280;'>"
            f"{date.strftime('%d/%m')}</span>",
            unsafe_allow_html=True,
        )

    # Grille : d'abord tous les midis, puis tous les soirs
    for meal in MEALS:
        cols = st.columns(7)
        for day_index in range(7):
            slot_recipe = st.session_state.recipes_week[(day_index, meal)]
            with cols[day_index].container(border=False):
                if slot_recipe is None:
                    html = f"""
                    <div class="meal-card-empty">
                        <div class="meal-card-header">{meal}</div>
                        <div class="meal-click-area">
                            <div class="plus-big">+</div>
                        </div>
                    </div>
                    """
                else:
                    html = f"""
                    <div class="meal-card">
                        <div class="meal-click-area">
                            <div class="meal-card-header">{meal}</div>
                            <div class="meal-title">{slot_recipe.get('title','')}</div>
                            <div class="meal-source">
                                {slot_recipe.get('source', '')}
                            </div>
                        </div>
                    </div>
                    """


                res = meal_slot_component(
                    data=CSS + html,
                    key=f"meal_slot_{day_index}_{meal}",
                )

                if hasattr(res, "clicked") and res.clicked:
                    if slot_recipe is None:
                        recipe_dialog(day_index=day_index, meal=meal)
                    else:
                        edit_recipe_dialog(day_index=day_index, meal=meal)
                if slot_recipe is not None:
                    if st.button("🗑️", key=f"button_delete_{meal}_{day_index}", use_container_width=True):
                        st.session_state.recipes_week[(day_index, meal)] = None
                        _save_week_to_file()
                        st.rerun()

render_grid()
