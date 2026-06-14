import ast

import streamlit as st
from streamlit_gsheets import GSheetsConnection


def connection_gsheets():
    conn = st.connection("gsheets", type=GSheetsConnection)
    st.session_state.gsheets_connection = conn
