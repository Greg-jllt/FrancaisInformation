
import streamlit as st
import os
import sys
import base64

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def get_base64_of_bin_file(bin_file):
    base_path = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_path, bin_file)
    with open(full_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def custom_global():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Oswald&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Bangers&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Pirata+One&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=IM+Fell+Great+Primer+SC&family=Pirata+One&display=swap');

        .stApp {{
            # background-image: url("data:image/png;base64,{get_base64_of_bin_file('./img/tele3.png')}"); /* Image de fond */
            background-size: contain; /* Étend l'image pour qu'elle couvre tout l'écran */
            background-position: center; /* Centre l'image */
            background-repeat: no-repeat; /* Empêche la répétition de l'image */
            margin: 0; /* Supprime les marges autour du conteneur */
            padding: 0; /* Supprime les espacements internes */
            height: 100vh; /* Fixe la hauteur à 100% de la fenêtre */
            width: 100vw; /* Fixe la largeur à 100% de la fenêtre */
            overflow: hidden; /* Empêche tout débordement de l'image */
            box-sizing: border-box; /* Inclut le padding et les bordures dans la taille totale */
        }}

        # .st-key-container1,
        # .st-key-container2
        # {{
        #     background-color: rgba(0, 0, 0, 0.8) !important;
        #     border-radius: 10px;
        #     padding: 10px;
        # }}

        # .stVegaLiteChart .chart-wrapper {{
        #     background-color: transparent !important;
        # }}
        # .stVegaLiteChart canvas {{
        #     background-color: transparent !important;
        # }}

        # </style>

        """,
        unsafe_allow_html=True,
    )


def init_pages():
    st.set_page_config(
        layout="wide",
        # initial_sidebar_state="collapsed",
    )

    custom_global()