import streamlit as st

st.header("🛒 Liste de courses")

with st.sidebar:
    st.title("Liens utiles vers des applis")
    st.link_button(label="Super U Drive", url="https://www.coursesu.com/drive-superu-chateaubourg",
                   icon="🚚", use_container_width=True)

st.write("Voir ce qu'on peut faire ici")
st.write("Idées en vrac : "
         "  - des cartes par catégories"
         "  - des liens API vers d'autres applis pour centraliser"
         "  - un lien avec les tasks et les recettes pour ajouter directement les produits")