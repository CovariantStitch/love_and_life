from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Kinklist", page_icon="💘", layout="wide")

KINKLIST_SAVE_DIR = Path(__file__).parent.parent / "resources" / "kinklist_save"
KINKLIST_XLSX = Path(__file__).parent.parent / "resources" / "kinklist.xlsx"

IRRELEVANT_COL0_CATS = {"Corps", "Vêtements"}
IRRELEVANT_COL1_CATS = {"Préférence et fréquence", "Jeux", "Extérieur", "Autres", "Vision"}

CHOICES = ["😈", "🔥", "👍", "🤔", "❌"]
DEFAULT_CHOICE_IDX = 2  # 👍


def _default_entry(category: str) -> list[int]:
    col0 = -1 if category in IRRELEVANT_COL0_CATS else DEFAULT_CHOICE_IDX
    col1 = -1 if category in IRRELEVANT_COL1_CATS else DEFAULT_CHOICE_IDX
    return [col0, col1]


def _build_default_res(df: pd.DataFrame) -> dict:
    res = {}
    for category in df.columns:
        res[category] = {}
        for kink in df[category].dropna().tolist():
            kink = str(kink).strip()
            if kink:
                res[category][kink] = _default_entry(category)
    return res


def _load_from_file(res: dict, user: str) -> dict:
    path = KINKLIST_SAVE_DIR / f"{user}.txt"
    if not path.exists():
        return res
    with open(path) as f:
        for line in f:
            parts = line.strip().split("/")
            if len(parts) < 4:
                continue
            cat, subcat = parts[0], parts[1]
            v1, v2 = int(parts[2]), int(parts[3])
            if cat not in res:
                res[cat] = {}
            if subcat not in res[cat]:
                res[cat][subcat] = _default_entry(cat)
            if v1 != -1:
                res[cat][subcat][0] = v1
            if v2 != -1:
                res[cat][subcat][1] = v2
    return res


def _save_to_file(res: dict, user: str) -> None:
    KINKLIST_SAVE_DIR.mkdir(parents=True, exist_ok=True)
    path = KINKLIST_SAVE_DIR / f"{user}.txt"
    lines = []
    for cat, subcats in res.items():
        for subcat, values in subcats.items():
            lines.append(f"{cat}/{subcat}/{values[0]}/{values[1]}/")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        if lines:
            f.write("\n")


def _init_kinklist_state(df: pd.DataFrame) -> None:
    if "kinklist_items" not in st.session_state:
        st.session_state.kinklist_items = df
    if "kinklist_res" not in st.session_state or not isinstance(st.session_state.kinklist_res, dict):
        res = _build_default_res(df)
        st.session_state.kinklist_res = _load_from_file(res, st.session_state.user)


if "kinklist_items" not in st.session_state:
    st.session_state.kinklist_items = pd.read_excel(KINKLIST_XLSX)
df = st.session_state.kinklist_items
_init_kinklist_state(df)
kinklist_res = st.session_state.kinklist_res

st.title("Kinklist 💘")


def render_column(items: list[str], col_index: int, col_name: str, category: str) -> None:
    col = left_right_cols[col_index]
    with col:
        st.subheader(col_name)

        for kink in items:
            row_col_text, row_col_choice = st.columns([2, 2])

            with row_col_text:
                st.write(f"- {kink}")

            with row_col_choice:
                if category not in kinklist_res:
                    kinklist_res[category] = {}
                if kink not in kinklist_res[category]:
                    kinklist_res[category][kink] = _default_entry(category)

                current_idx = kinklist_res[category][kink][col_index]
                widget_key = f"kink_{col_name}_{category}_{kink}"

                st.segmented_control(
                    label="choices",
                    options=CHOICES,
                    default=CHOICES[current_idx],
                    key=widget_key,
                    label_visibility="collapsed",
                )

                selected_idx = CHOICES.index(st.session_state[widget_key])
                if kinklist_res[category][kink][col_index] != selected_idx:
                    kinklist_res[category][kink][col_index] = selected_idx
                    st.session_state.kinklist_res = kinklist_res
                    _save_to_file(kinklist_res, st.session_state.user)


tabs = st.tabs(list(df.columns))
for i_, category in enumerate(df.columns):
    irrelevant = [False, False]
    if category in [
        "Corps", "Vêtements", "Préférence et fréquence", "Vision", "Bruits",
        "Jeux", "Extérieur", "Situation (consentie !)", "Autres",
    ]:
        text1 = "Moi"
        text2 = "Partenaire"
        if category in IRRELEVANT_COL0_CATS:
            irrelevant[0] = True
        if category in IRRELEVANT_COL1_CATS:
            irrelevant[1] = True
    else:
        text1 = "Donner"
        text2 = "Recevoir"
    left_right_cols = tabs[i_].columns(2)
    items = df[category].dropna().tolist()
    if not irrelevant[0]:
        render_column(items=items, col_index=0, col_name=text1, category=category)
    if not irrelevant[1]:
        render_column(items=items, col_index=1, col_name=text2, category=category)
