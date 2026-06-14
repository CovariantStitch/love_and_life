import streamlit as st

def update_value(name):
    idx = st.session_state.settings.index[st.session_state.settings["Name"] == name][0]
    st.session_state.settings.at[idx, "Value"] = not st.session_state.settings.at[idx, "Value"]

# list of the pages and show if the page is visible or not
col1, col2 = st.columns([0.9, 0.1])
for _, row in st.session_state.settings.iterrows():
    col1.write(row["Title"])
    col2.toggle(label="Activé", value=row["Value"], key=f"settings_toggle_{row['Name']}", on_change=update_value, args=(row["Name"],))

if st.button("Sauvegarder"):
    st.session_state.gsheets_connection.update(worksheet="settings", data=st.session_state.settings)