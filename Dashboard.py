import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
from collections import defaultdict
import plotly.express as px
import polars as pl
import duckdb as db
from fonctions_graph import make_donut
import altair as alt
from style import init_pages

# from streamlit_extras.stylable_container import stylable_container

# init_pages()

st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
            <style>
            .custom-metric {
                background: linear-gradient(135deg, #000000, #434343); /* Dégradé de noir */
                padding: 20px; /* Espacement interne */
                box-shadow: 20px 20px 10px rgba(0, 0, 0, 0.2); /* Ombre plus prononcée */
                text-align: center; /* Centrer le texte */
                font-family: 'Lato', sans-serif; /* Police personnalisée */
                color: white; /* Couleur du texte */
                transition: transform 0.3s ease, box-shadow 0.3s ease, background 0.3s ease; /* Animation fluide */
                position: relative; /* Position pour les effets supplémentaires */
                overflow: hidden; /* Masquer les débordements */
                width: 100%; /* S'adapte à la largeur disponible */
                height: 250px; /* Hauteur fixe pour uniformiser */
            }
            .custom-metric:hover {
                transform: scale(1.05) ; 
                box-shadow: 0px 12px 20px rgba(0, 0, 0, 0.3), 0px 0px 20px rgba(0, 198, 255, 0.5); /* Ombre plus intense et colorée */
                background: linear-gradient(135deg, #434343, #000000); /* Dégradé de noir */
            }
            .custom-metric::before {
                content: '';
                position: absolute;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, rgba(255, 255, 255, 0.2), transparent);
                opacity: 0;
                transition: opacity 0.5s ease;
                z-index: 0;
            }
            .custom-metric:hover::before {
                opacity: 1; /* Ajouter un effet lumineux au survol */
            }
            .custom-metric .metric-value {
                font-size: 42px; /* Taille de la valeur */
                font-weight: bold; /* Texte en gras */
                color: #ffffff; /* Couleur de la valeur */
                margin-bottom: 10px; /* Espacement sous la valeur */
                position: relative;
                z-index: 1; /* Assurer que le texte est au-dessus des effets */
                text-shadow: 0px 4px 6px rgba(0, 0, 0, 0.3); /* Ajouter une ombre au texte */
            }
            .custom-metric .metric-label {
                font-size: 20px; /* Taille de l'étiquette */
                color: #f0f2f6; /* Couleur de l'étiquette */
                position: relative;
                z-index: 1; /* Assurer que le texte est au-dessus des effets */
                text-shadow: 0px 2px 4px rgba(0, 0, 0, 0.2); /* Ajouter une ombre légère à l'étiquette */
            }
            .custom-metric .metric-icon {
                font-size: 50px; /* Taille de l'icône */
                margin-bottom: 10px; /* Espacement sous l'icône */
                color: #ffffff; /* Couleur de l'icône */
                position: relative;
                z-index: 1; /* Assurer que l'icône est au-dessus des effets */
            }
            .custom-metric .metric-note {
                font-size: 8px; /* Taille de la note */
                color: #cccccc; /* Couleur de la note */
                margin-top: 15px; /* Espacement au-dessus de la note */
                text-align: center; /* Centrer le texte */
                font-style: italic; /* Style italique pour la note */
            }
            </style>
            """,
    unsafe_allow_html=True,
)

########################################################################################


@st.cache_data
def load_data():
    return pd.read_csv(
        "Data/ina-barometre-jt-tv-donnees-quotidiennes-2000-2020-nbre-sujets-durees-202410.csv",
        encoding="utf-8",
        sep=";",
    )


ina = load_data()

#######################################################################################


@st.cache_data
def load_data_2():
    return pl.read_parquet(
        "./Data/les-francais-et-l-information-arcom-2024-base-anonymisee.parquet"
    )


data = load_data_2()

arcom = data.to_pandas()

########################################################################################


@st.cache_data
def load_data():
    return pd.read_json("Data/Part_audience.json")


Part_audience = load_data()

Part_audience["France 5"] = (
    Part_audience["France 5"].fillna(Part_audience["La 5"]).replace("", np.nan)
)

Part_audience.drop(columns=["La 5"], inplace=True)

Part_audience.replace("nd", np.nan, inplace=True)
Part_audience.replace("ns", np.nan, inplace=True)

Part_audience_long = pd.melt(
    Part_audience, id_vars=["Année"], var_name="Chaine", value_name="part_audience"
)
Part_audience_long["Chaine"] = Part_audience_long["Chaine"].apply(lambda x: x.strip())

########################################################################################


Durree_ecoute_age = pd.read_csv("Data/Audience_de_la_télévision_age.csv", sep=",")

Prog_TV = pd.read_csv("Data/Prog_TV_audience.csv", sep=",")


########################################################################################


def var_selection(var_obj):
    if var_obj == "Genre 🧑‍🤝‍🧑":
        liste_obj = arcom["RS1_R"].value_counts().keys().tolist()
        cols_data = ["Homme 🧑", "Femme 👩"]
        var = "RS1_R"
        title = "Préférences des répondants par genre"
    if var_obj == "Tranche d'âge 👵":
        liste_obj = arcom["RS2C_RECODE_AG_R"].value_counts().keys().tolist()
        cols_data = [
            "15-17 ans 🧒",
            "18-24 ans 👩‍🎓",
            "25-34 ans 👩‍💼",
            "35-44 ans 👩‍🔬",
            "45-59 ans 👩‍🚀",
            "60-69 ans 👵",
            "70 ans et plus 👴",
        ]
        var = "RS2C_RECODE_AG_R"
        title = "Préférences des répondants par tranche d'âge"
    elif var_obj == "Catégorie socio-professionnelle 👔":
        liste_obj = arcom["RS4_R"].value_counts().keys().tolist()
        cols_data = [
            "Agriculteur 🚜",
            "Artisan/Commercant 🛠️",
            "Cadre/Profession libérale 🏢",
            "Profession intermédiaire 📚",
            "Employé 🏢",
            "Ouvrier 🏭",
            "Je ne sais pas/Je ne réponds pas",
        ]
        var = "RS4_R"
        title = "Préférences des répondants par catégorie socio-professionnelle"
    elif var_obj == "Niveau d'étude 📚":
        liste_obj = arcom["RS5_R"].value_counts().keys().tolist()
        cols_data = [
            "Niveau Primaire 📚",
            "Secondaire 6°-3° 🏫",
            "Secondaire 2nd-terminale 🎒",
            "Technique court(CAP,BEP,...) 🛠️",
            "Baccalauréat  🎓",
            "Technique supérieur  🏢",
            "Supérieur 1er Cycle 📘",
            "Supérieur 2nd Cycle 📗",
            "Doctorat 🧑‍🔬",
        ]
        var = "RS5_R"
        title = "Préférences des répondants par niveau d'étude"
    elif var_obj == "Revenu 💸":
        liste_obj = arcom["RS14_R"].value_counts().keys().tolist()
        cols_data = [
            "Moins de 1500 net 💸",
            "Entre 1500 et 3000 net 💵",
            "Entre 3000 et 4500  💶",
            "Entre 4500 et 7500 💷",
            "7500 et plus 💰",
            "Ne souhaite pas répondre",
        ]
        var = "RS14_R"
        title = "Préférences des répondants par niveau de revenu"
    liste_obj.sort()
    return liste_obj, cols_data, var, title


########################################################################################
st.markdown(
    """
    <style>
    .stApp {
            margin-top: -40px; 
        }
    </style>
""",
    unsafe_allow_html=True,
)
st.sidebar.markdown("# ***Les Français et l'information*** 📊")
st.sidebar.markdown("---")

with st.sidebar:
    Choix = st.radio(
        "Selection de l'étude",
        [
            "Partie 1 - Analyse des performances des Chaines TV",
            "Partie 2 - Analyse du rapports des français à l'information",
        ],
    )


ina["Theme"] = ina["Theme"].replace(
    {
        "Soci�t�": "Société",
        "Sant�": "Santé",
    }
)

ina.sort_values(by="Date", inplace=True)

ina["Date"] = pd.to_datetime(ina["Date"], format="%d/%m/%Y")

ina["Year"] = ina["Date"].dt.year

if Choix == "Partie 1 - Analyse des performances des Chaines TV":
    with st.sidebar:
        options = ["Theme", "Chaine"]
        Var_ref_1 = st.radio(
            "Choix de la variable de référence",
            options,
        )
        Var_ref_2 = [opt for opt in options if opt != Var_ref_1][0]
        if Var_ref_1 == "Theme":
            gr_1_select = st.selectbox(
                "Choix du thème",
                ina["Theme"].unique(),
            )
            gr_1_mult = st.multiselect(
                "Choix de la chaîne", ina["Chaine"].unique(), ["TF1"]
            )
        else:
            gr_1_select = st.selectbox(
                "Choix de la chaîne",
                ina["Chaine"].unique(),
            )
            gr_1_mult = st.multiselect(
                "Choix du thème", ina["Theme"].unique(), ["Société"]
            )
        Var_select_prog = st.multiselect(
            "Choix du programme", Prog_TV["Prog"].unique(), ["autres"]
        )

if Choix == "Partie 2 - Analyse du rapports des français à l'information":
    selection = st.sidebar.selectbox(
        "Sous-parties",
        [
            "Vue générale",
            "Fiabilité des sources",
            "Attentes des sondés",
            "Analyse complémentaire",
        ],
    )

    if selection != "Vue générale":
        var_obj = st.sidebar.radio(
            "Choix de la variable d'analyse",
            [
                "Genre 🧑‍🤝‍🧑",
                "Tranche d'âge 👵",
                "Catégorie socio-professionnelle 👔",
                "Niveau d'étude 📚",
                "Revenu 💸",
            ],
        )
    if selection in ["Vue générale", "Fiabilité des sources"]:
        with st.sidebar:
            variables = [
                "Global",
                "Genre 🧑‍🤝‍🧑",
                "Âge 👵",
                "Revenus Net 💸",
                "Niveau d'étude 📚",
                "CSP 👔",
            ]
            choix_variable = st.selectbox("Sélectionnez une variable :", variables)

            modalité = "Choix de la modalité"

            if choix_variable == "Genre 🧑‍🤝‍🧑":
                genre = ["Homme 🧑", "Femme 👩"]
                choix_genre = st.radio(modalité, genre)

            if choix_variable == "Âge 👵":
                age = [
                    "15-17 ans 🧒",
                    "18-24 ans 👩‍🎓",
                    "25-34 ans 👩‍💼",
                    "35-44 ans 👩‍🔬",
                    "45-59 ans 👩‍🚀",
                    "60-69 ans 👵",
                    "70 ans et plus 👴",
                ]
                choix_age = st.radio(modalité, age)

            if choix_variable == "Revenus Net 💸":
                revenus = [
                    "< 1500€ 💸",
                    "1500€ - 3000€ 💵",
                    "3000€ - 4500€ 💶",
                    "4500€ - 7500€ 💷",
                    "> 7500€ 💰",
                ]
                choix_revenus = st.radio(modalité, revenus)

            if choix_variable == "Niveau d'étude 📚":
                diplome = [
                    "Niveau primaire 📚",
                    "Secondaire de la 6ème à la 3ème 🏫",
                    "Secondaire de la 2nde à la Terminale 🎒",
                    "Technique court (CAP, BEP) 🛠️",
                    "Bac, Bac professionnel, brevet professionnel 🎓",
                    "Technique Supérieur (BTS, DUT) 🏢",
                    "Supérieur 1er cycle 📘",
                    "Supérieur 2ème cycle 📗",
                    "Doctorat 🧑‍🔬",
                ]
                choix_diplome = st.radio(modalité, diplome)

            if choix_variable == "CSP 👔":
                csp = [
                    "Agriculteurs exploitants 🚜",
                    "Artisans, commerçants, chefs d'entreprise 🛠️",
                    "Cadres et professions intellectuelles supérieures 🏢",
                    "Professions intermédiaires 📚",
                    "Employés 💼",
                    "Ouvriers 🏭",
                ]
                choix_csp = st.radio(modalité, csp)

########################################################################################
#######################################################################################


doute = db.query(
    """
    SELECT
        CASE
            WHEN DOUTE_R = 1 THEN 'OUI'
            WHEN DOUTE_R = 2 THEN 'OUI'
            WHEN DOUTE_R = 3 THEN 'OUI'
            WHEN DOUTE_R = 4 THEN 'NON'
            ELSE NULL
        END AS DOUTE,
        RS1_R,
        RS2C_RECODE_AG_R,
        RS4_R,
        RS5_R,
        RS14_R
    fROM 
        data
"""
).to_df()

interet = db.query(
    """
    SELECT 
        CASE 
            WHEN INT1_R = 1 THEN 'Intéressé'
            WHEN INT1_R = 2 THEN 'Intéressé'
            WHEN INT1_R = 3 THEN 'Peu ou pas intéressé'
            WHEN INT1_R = 4 THEN 'Peu ou pas intéressé'
        END as Interet,
        RS1_R,
        RS2C_RECODE_AG_R,
        RS4_R,
        RS5_R,
        RS14_R
    FROM
        data
"""
).df()


ia = db.query(
    """
            SELECT
                CASE
                    WHEN IA1_R = 1 THEN 'OUI'
                    WHEN IA1_R = 2 THEN 'OUI'
                    WHEN IA1_R = 3 THEN 'OUI'
                    WHEN IA1_R = 4 THEN 'NON'
                    ELSE NULL
                END AS ia,
                RS1_R,
                RS2C_RECODE_AG_R,
                RS4_R,
                RS5_R,
                RS14_R
            fROM 
                data
        """
).to_df()

infofiable = db.query(
    """
            SELECT
                CASE
                    WHEN INFOFIABLE_R in (1,2) THEN 'OUI'
                    WHEN INFOFIABLE_R in (3,4) THEN 'NON'
                    ELSE NULL
                END as Infofiable,
                RS1_R,
                RS2C_RECODE_AG_R,
                RS4_R,
                RS5_R,
                RS14_R
            FROM
                data
        """
).df()

pay = db.query(
    """
            SELECT 
                CASE 
                    WHEN PAY_R_1 = 1 THEN 'OUI' 
                    WHEN PAY_R_1 = 2 THEN 'NON'
                    WHEN PAY_R_2 = 1 THEN 'OUI'
                    WHEN PAY_R_2 = 2 THEN 'NON'
                    WHEN PAY_R_3 = 1 THEN 'OUI'
                    WHEN PAY_R_3 = 2 THEN 'NON'
                    WHEN PAY_R_4 = 1 THEN 'OUI'
                    WHEN PAY_R_4 = 2 THEN 'NON'
                    WHEN PAY_R_5 = 1 THEN 'OUI'
                    WHEN PAY_R_5 = 2 THEN 'NON'
                    WHEN PAY_R_6 = 1 THEN 'OUI'
                    WHEN PAY_R_6 = 2 THEN 'NON'
                    WHEN PAY_R_7 = 1 THEN 'OUI'
                    ELSE NULL
                END as pay,
                RS1_R,
                RS2C_RECODE_AG_R,
                RS4_R,
                RS5_R,
                RS14_R
            FROM
                data
        """
).df()

reseaux = db.query(
    """
            SELECT 
                CASE 
                    WHEN RSINFO_2_LR_R_1 = 1 THEN 'OUI' 
                    WHEN RSINFO_2_LR_R_2 = 1 THEN 'OUI'
                    WHEN RSINFO_2_LR_R_3 = 1 THEN 'OUI'
                    WHEN RSINFO_2_LR_R_4 = 1 THEN 'OUI'
                    WHEN RSINFO_2_LR_R_5 = 1 THEN 'OUI'
                    WHEN RSINFO_2_LR_R_6 = 1 THEN 'OUI'
                    WHEN RSINFO_2_LR_R_7 = 1 THEN 'OUI'
                    WHEN RSINFO_2_LR_R_8 = 1 THEN 'OUI'
                    WHEN RSINFO_2_LR_R_9 = 1 THEN 'OUI'
                    WHEN RSINFO_2_LR_R_10 = 1 THEN 'OUI'
                    WHEN RSINFO_2_LR_R_11 = 1 THEN 'OUI'
                    WHEN RSINFO_2_LR_R_12 = 1 THEN 'OUI'
                    WHEN RSINFO_2_LR_R_13 = 1 THEN 'OUI'
                    ELSE 'Non'
                END as info_reseau,
                RS1_R,
                RS2C_RECODE_AG_R,
                RS4_R,
                RS5_R,
                RS14_R
            FROM
                data
        """
).df()

nb_source_media = db.query(
    """
            SELECT
                CASE
                    WHEN NBR_NEWS1SOURCES_R1 = 1 THEN 0
                    WHEN NBR_NEWS1SOURCES_R1 = 2 THEN 1
                    WHEN NBR_NEWS1SOURCES_R1 = 3 THEN 2
                    WHEN NBR_NEWS1SOURCES_R1 = 4 THEN 3
                    WHEN NBR_NEWS1SOURCES_R1 = 5 THEN 4
                    ELSE NULL
                END as nb_souce_media,
                RS1_R,
                RS2C_RECODE_AG_R,
                RS4_R,
                RS5_R,
                RS14_R
            FROM
                data
        """
).df()

nb_source = db.query(
    """
            SELECT
                CASE
                    WHEN NBR_NEWS1SOURCES_R3 = 1 THEN 0
                    WHEN NBR_NEWS1SOURCES_R3 = 2 THEN 1
                    WHEN NBR_NEWS1SOURCES_R3 = 3 THEN 2
                    WHEN NBR_NEWS1SOURCES_R3 = 4 THEN 3
                    WHEN NBR_NEWS1SOURCES_R3 = 5 THEN 4
                    ELSE NULL
                END as nb_source,
                RS1_R,
                RS2C_RECODE_AG_R,
                RS4_R,
                RS5_R,
                RS14_R
            FROM
                data
        """
).df()
nb_source_media = db.query(
    """
            SELECT
                CASE
                    WHEN NBR_NEWS1SOURCES_R1 = 1 THEN 0
                    WHEN NBR_NEWS1SOURCES_R1 = 2 THEN 1
                    WHEN NBR_NEWS1SOURCES_R1 = 3 THEN 2
                    WHEN NBR_NEWS1SOURCES_R1 = 4 THEN 3
                    WHEN NBR_NEWS1SOURCES_R1 = 5 THEN 4
                    ELSE NULL
                END as nb_souce_media,
                RS1_R,
                RS2C_RECODE_AG_R,
                RS4_R,
                RS5_R,
                RS14_R
            FROM
                data
        """
).df()

nb_source = db.query(
    """
            SELECT
                CASE
                    WHEN NBR_NEWS1SOURCES_R3 = 1 THEN 0
                    WHEN NBR_NEWS1SOURCES_R3 = 2 THEN 1
                    WHEN NBR_NEWS1SOURCES_R3 = 3 THEN 2
                    WHEN NBR_NEWS1SOURCES_R3 = 4 THEN 3
                    WHEN NBR_NEWS1SOURCES_R3 = 5 THEN 4
                    ELSE NULL
                END as nb_source,
                RS1_R,
                RS2C_RECODE_AG_R,
                RS4_R,
                RS5_R,
                RS14_R
            FROM
                data
        """
).df()


def generate_donnuts(variable, modalite):
    """
    Génère les graphiques et métriques pour une modalité donnée.

    Args:
        modalite (str): Nom de la modalité (par exemple, "Homme", "Femme").
        tab_interet (pd.DataFrame): Tableau croisé pour l'intérêt.
        tab_doute (pd.DataFrame): Tableau croisé pour les doutes.
        tab_ia (pd.DataFrame): Tableau croisé pour les IA.
        tab_infofiable (pd.DataFrame): Tableau croisé pour l'information fiable.
        tab_pay (pd.DataFrame): Tableau croisé pour le paiement.
        tab_reseaux (pd.DataFrame): Tableau croisé pour les réseaux sociaux.
        nb_source_media (pd.DataFrame): Données pour les sources médiatiques.
        nb_source (pd.DataFrame): Données pour les sources hors-médias.
    """

    tab_interet = pd.crosstab(
        interet["Interet"], interet[variable], normalize="columns"
    )
    tab_doute = pd.crosstab(doute["DOUTE"], doute[variable], normalize="columns")
    tab_infofiable = pd.crosstab(
        infofiable["Infofiable"], infofiable[variable], normalize="columns"
    )
    tab_ia = pd.crosstab(ia["ia"], ia[variable], normalize="columns")
    tab_pay = pd.crosstab(pay["pay"], pay[variable], normalize="columns")
    tab_reseaux = pd.crosstab(
        reseaux["info_reseau"], reseaux[variable], normalize="columns"
    )

    a, b, c = st.columns(3)
    st.markdown("---")
    d, e, f = st.columns(3)
    st.markdown("---")
    g, h, i = st.columns(3)

    with a:
        fig = make_donut(
            int(tab_interet[modalite]["Intéressé"].round(2) * 100),
            f"INTERET_{modalite}",
            "blue",
            ["Non", "Oui"],
            ["Oui", "Non"],
        )
        st.markdown("***Sont-ils intéressés par l'information en générale ?***")
        st.altair_chart(fig, use_container_width=True)

    with b:
        fig = make_donut(
            int(tab_doute[modalite]["OUI"].round(2) * 100),
            f"DOUTE_{modalite}",
            "red",
            ["Non", "Oui"],
            ["Oui", "Non"],
        )
        st.markdown("***Ont-ils des doutes sur la fiabilité des informations ?***")
        st.altair_chart(fig, use_container_width=True)

    with c:
        fig = make_donut(
            int(tab_ia[modalite]["OUI"].round(2) * 100),
            f"IA_{modalite}",
            "vert clair",
            ["Non", "Oui"],
            ["Oui", "Non"],
        )
        st.markdown(
            "***Sont-ils conscients que les IA peuvent générer des informations ?***"
        )
        st.altair_chart(fig, use_container_width=True)

    with d:
        fig = make_donut(
            int(tab_infofiable[modalite]["OUI"].round(2) * 100),
            f"INFOFIABLE_{modalite}",
            "blue",
            ["Non", "Oui"],
            ["Oui", "Non"],
        )
        st.markdown(
            "***Estiment-ils qu'il est simple d'accéder à une information fiable ?***"
        )
        st.altair_chart(fig, use_container_width=True)

    with e:
        fig = make_donut(
            int(tab_pay[modalite]["OUI"].round(2) * 100),
            f"PAY_{modalite}",
            "red",
            ["Non", "Oui"],
            ["Oui", "Non"],
        )
        st.markdown(
            "***Ont-ils payés lors de ces 12 derniers mois pour un accès à l'information ?***"
        )
        st.altair_chart(fig, use_container_width=True)

    with f:
        fig = make_donut(
            int(tab_reseaux[modalite]["OUI"].round(2) * 100),
            f"RESEAUX_{modalite}",
            "vert clair",
            ["Non", "Oui"],
            ["Oui", "Non"],
        )
        st.markdown("***Utilisent-ils les réseaux sociaux pour s'informer ?***")
        st.altair_chart(fig, use_container_width=True)


def afficher_confiances(
    variable, modalite, confiances, liste_modalites=["homme", "femme"]
):
    """
    Génère les colonnes pour les confiances en fonction des acteurs.

    Args:
        variable (str): Nom de la variable pour filtrer les modalités (par exemple, "RS1_R").
        modalite (int): Modalité spécifique (par exemple, 1 pour "Homme").
        confiances (list): Liste de dictionnaires contenant les colonnes, icônes et labels.
    """
    for i, moda in enumerate(liste_modalites):
        if moda[-1] != "s":
            liste_modalites[i] = moda + "s"

    st.markdown(
        f"#### Moyenne des notes données par les {liste_modalites[modalite - 1]}"
    )
    a, b, c = st.columns(3)
    st.markdown("---")
    e, f, g = st.columns(3)
    cols = [a, b, c, e, f, g]

    for col, confiance, acteur, icon in zip(
        cols,
        confiances,
        [
            "Journalistes",
            "Experts",
            "Politiciens",
            "Influenceurs",
            "Célébrités",
            "Anonymes",
        ],
        ["✍️", "🧠", "🏛️", "💻", "🌟", "🗨️"],
    ):
        with col:
            # Récupérer les données pour la modalité et la colonne de confiance
            data_modalite = db.query(
                f"""
                    SELECT
                        {confiance} as Confiance,
                        {variable}
                    FROM
                        data
                    """
            ).df()
            data_modalite = data_modalite[data_modalite[variable] == modalite]

            # Calculer la moyenne pondérée
            confiance_counts = data_modalite["Confiance"].value_counts()
            value = round(
                sum(
                    [
                        i * v
                        for i, v in zip(
                            [int(i) for i in confiance_counts.index.tolist()],
                            confiance_counts.values.tolist(),
                        )
                    ]
                )
                / sum(confiance_counts.values.tolist()),
                2,
            )

            st.markdown(
                f"""
                <div class="custom-metric">
                    <div class="metric-icon">{icon}</div> 
                    <div class="metric-value">{value} / 4</div>
                    <div class="metric-label">{acteur}</div>
                    {f"<div class='metric-note'>{confiance['note']}</div>" if 'note' in confiance else ""}
                </div>
                """,
                unsafe_allow_html=True,
            )


def generate_header(
    variable, modalite, nb_source_media, nb_source, liste_modalites=["homme", "femme"]
):
    st.markdown("Source : ARCOM - Etude du rapport des français à l'information - 2024")

    for i, moda in enumerate(liste_modalites):
        if moda[-1] != "s" and variable not in ["RS14_R", "RS5_R"]:
            liste_modalites[i] = (
                moda + "s"
            )  # on rajooute un s pour les modalités qui n'en ont pas sauve les revenus

    st.markdown(f"###### Métriques calculées pour les {liste_modalites[modalite - 1]}")
    a, b, c = st.columns(3)

    with a:
        st.markdown(
            f"""
                    <div class="custom-metric">
                        <div class="metric-icon">👤</div> 
                        <div class="metric-value">{data.filter(pl.col(variable) == modalite).shape[0]}</div>
                        <div class="metric-label">Répondants</div>
                    </div>
                    """,
            unsafe_allow_html=True,
        )

    with b:
        tab_nb_source_media = nb_source_media[nb_source_media[variable] == modalite][
            ["nb_souce_media"]
        ].value_counts()
        value = round(
            sum(
                [
                    i * v
                    for i, v in zip(
                        [int(i[0]) for i in tab_nb_source_media.index.tolist()],
                        tab_nb_source_media.values.tolist(),
                    )
                ]
            )
            / tab_nb_source_media.sum(),
            2,
        )
        st.markdown(
            f"""
            <div class="custom-metric">
                <div class="metric-icon">📰</div>
                <div class="metric-value">{value}</div>
                <div class="metric-label">Nombre moyen de sources d'information médiatiques</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c:
        tab_nb_source = nb_source[nb_source[variable] == modalite][
            ["nb_source"]
        ].value_counts()
        value = round(
            sum(
                [
                    i * v
                    for i, v in zip(
                        [int(i[0]) for i in tab_nb_source.index.tolist()],
                        tab_nb_source.values.tolist(),
                    )
                ]
            )
            / tab_nb_source.sum(),
            2,
        )
        st.markdown(
            f"""
            <div class="custom-metric">
                <div class="metric-icon">🔍</div>
                <div class="metric-value">{value}</div>
                <div class="metric-label">Nombre moyen de sources d'information hors-médias</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")


########################################################################################
def Introduction():
    if choix_variable == "Global":
        st.markdown(
            "Source : ARCOM - Etude sur le rapport des français à l'information - 2024"
        )
        a, b, c = st.columns(3)
        st.markdown("---")
        d, e, f = st.columns(3)
        st.markdown("---")
        g, h, i = st.columns(3)

        with a:
            st.markdown(
                f"""
                <div class="custom-metric">
                    <div class="metric-icon">👤</div>
                    <div class="metric-value">{data.shape[0]}</div>
                    <div class="metric-label">Répondants</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with b:
            value = round(
                sum(
                    [
                        i * v
                        for i, v in zip(
                            nb_source_media["nb_souce_media"]
                            .value_counts()
                            .index.tolist(),
                            nb_source_media["nb_souce_media"]
                            .value_counts()
                            .values.tolist(),
                        )
                    ]
                )
                / nb_source_media["nb_souce_media"].value_counts().sum(),
                2,
            )

            st.markdown(
                f"""
                <div class="custom-metric">
                    <div class="metric-icon">📰</div> <!-- Icône animée avec rotation -->
                    <div class="metric-value">{value}</div>
                    <div class="metric-label">Nombre moyen de sources d'information médiatiques</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with c:
            value = round(
                sum(
                    [
                        i * v
                        for i, v in zip(
                            nb_source["nb_source"].value_counts().index.tolist(),
                            nb_source["nb_source"].value_counts().values.tolist(),
                        )
                    ]
                )
                / nb_source["nb_source"].value_counts().sum(),
                2,
            )

            st.markdown(
                f"""
                <div class="custom-metric">
                    <div class="metric-icon">🔍</div> <!-- Icône au-dessus -->
                    <div class="metric-value">{value}</div> <!-- Valeur en bas -->
                    <div class="metric-label">Nombre moyen de sources d'information hors-médias</div> <!-- Texte en haut -->
                </div>
                """,
                unsafe_allow_html=True,
            )

        with d:
            interet = db.query(
                """
            SELECT 
                CASE 
                    WHEN INT1_R = 1 THEN 'Intéressé'
                    WHEN INT1_R = 2 THEN 'Intéressé'
                    WHEN INT1_R = 3 THEN 'Peu ou pas intéressé'
                    WHEN INT1_R = 4 THEN 'Peu ou pas intéressé'
                END as Interet
            FROM
                data
            """
            ).df()
            interet_counts = (
                interet["Interet"].value_counts(normalize=True).round(2) * 100
            )

            fig = make_donut(
                int(interet_counts[0]), "Doute", "blue", ["Non", "Oui"], ["Oui", "Non"]
            )
            st.markdown("***Sont-ils intéressés par l'information en générale ?***")
            st.altair_chart(fig, use_container_width=True)

        with e:
            doute_freq = doute["DOUTE"].value_counts(normalize=True).round(2) * 100

            fig = make_donut(
                int(doute_freq[0]), "Doute", "red", ["Non", "Oui"], ["Oui", "Non"]
            )
            st.markdown("***Ont-ils des doutes sur la fiabilité des informations ?***")
            st.altair_chart(fig, use_container_width=True)

        with f:
            ia_freq = ia["ia"].value_counts(normalize=True).round(2) * 100

            fig = make_donut(
                int(ia_freq[0]), "ia", "vert clair", ["Non", "Oui"], ["Oui", "Non"]
            )
            st.markdown(
                "***Sont-ils conscients que les IA peuvent générer des informations ?***"
            )
            st.altair_chart(fig, use_container_width=True)

        with g:
            infofiable_freq = (
                infofiable["Infofiable"].value_counts(normalize=True).round(2) * 100
            )

            fig = make_donut(
                int(infofiable_freq[0]), "Doute", "blue", ["Non", "Oui"], ["Oui", "Non"]
            )
            st.markdown(
                "***Estiment-ils qu'il est simple d'accéder à une information fiable ?***"
            )
            st.altair_chart(fig, use_container_width=True)

        with h:
            pay_freq = pay["pay"].value_counts(normalize=True).round(2) * 100

            fig = make_donut(
                int(pay_freq[1]), "pay", "red", ["Non", "Oui"], ["Oui", "Non"]
            )
            st.markdown(
                "***Ont-ils payés lors de ces 12 derniers mois pour un accès à l'information ?***"
            )
            st.altair_chart(fig, use_container_width=True)

        with i:
            reseaux_freq = (
                reseaux["info_reseau"].value_counts(normalize=True).round(2) * 100
            )

            fig = make_donut(
                int(reseaux_freq[0]),
                "reseaux",
                "vert clair",
                ["Non", "Oui"],
                ["Oui", "Non"],
            ).encode(
                tooltip=[
                    alt.Tooltip("Topic:N", title="Catégorie"),
                    alt.Tooltip("% value:Q", title="Pourcentage", format=".1f"),
                    alt.Tooltip("Autre_Colonne:N", title="Autre Information"),
                ]
            )
            st.markdown("***Utilisent-ils les réseaux sociaux pour s'informer ?***")
            st.altair_chart(fig, use_container_width=True)

    if choix_variable == "Genre 🧑‍🤝‍🧑":
        if choix_genre == "Homme 🧑":
            generate_header("RS1_R", 1, nb_source_media, nb_source, ["Homme", "Femme"])
            generate_donnuts("RS1_R", 1)

        if choix_genre == "Femme 👩":
            generate_header("RS1_R", 2, nb_source_media, nb_source, ["Homme", "Femme"])
            generate_donnuts("RS1_R", 2)


    if choix_variable == "Âge 👵":
        if choix_age == "15-17 ans 🧒":
            generate_header(
                "RS2C_RECODE_AG_R",
                1,
                nb_source_media,
                nb_source,
                [
                    "15-17 ans",
                    "18-24 ans",
                    "25-34 ans",
                    "35-44 ans",
                    "45-59 ans",
                    "60-69 ans",
                    "70 ans et plus",
                ],
            )
            generate_donnuts("RS2C_RECODE_AG_R", 1)

        if choix_age == "18-24 ans 👩‍🎓":
            generate_header(
                "RS2C_RECODE_AG_R",
                2,
                nb_source_media,
                nb_source,
                [
                    "15-17 ans",
                    "18-24 ans",
                    "25-34 ans",
                    "35-44 ans",
                    "45-59 ans",
                    "60-69 ans",
                    "70 ans et plus",
                ],
            )
            generate_donnuts("RS2C_RECODE_AG_R", 2)

        if choix_age == "25-34 ans 👩‍💼":
            generate_header(
                "RS2C_RECODE_AG_R",
                3,
                nb_source_media,
                nb_source,
                [
                    "15-17 ans",
                    "18-24 ans",
                    "25-34 ans",
                    "35-44 ans",
                    "45-59 ans",
                    "60-69 ans",
                    "70 ans et plus",
                ],
            )
            generate_donnuts("RS2C_RECODE_AG_R", 3)

        if choix_age == "35-44 ans 👩‍🔬":
            generate_header(
                "RS2C_RECODE_AG_R",
                4,
                nb_source_media,
                nb_source,
                [
                    "15-17 ans",
                    "18-24 ans",
                    "25-34 ans",
                    "35-44 ans",
                    "45-59 ans",
                    "60-69 ans",
                    "70 ans et plus",
                ],
            )
            generate_donnuts("RS2C_RECODE_AG_R", 4)

        if choix_age == "45-59 ans 👩‍🚀":
            generate_header(
                "RS2C_RECODE_AG_R",
                5,
                nb_source_media,
                nb_source,
                [
                    "15-17 ans",
                    "18-24 ans",
                    "25-34 ans",
                    "35-44 ans",
                    "45-59 ans",
                    "60-69 ans",
                    "70 ans et plus",
                ],
            )
            generate_donnuts("RS2C_RECODE_AG_R", 5)

        if choix_age == "60-69 ans 👵":
            generate_header(
                "RS2C_RECODE_AG_R",
                6,
                nb_source_media,
                nb_source,
                [
                    "15-17 ans",
                    "18-24 ans",
                    "25-34 ans",
                    "35-44 ans",
                    "45-59 ans",
                    "60-69 ans",
                    "70 ans et plus",
                ],
            )
            generate_donnuts("RS2C_RECODE_AG_R", 6)

        if choix_age == "70 ans et plus 👴":
            generate_header(
                "RS2C_RECODE_AG_R",
                7,
                nb_source_media,
                nb_source,
                [
                    "15-17 ans",
                    "18-24 ans",
                    "25-34 ans",
                    "35-44 ans",
                    "45-59 ans",
                    "60-69 ans",
                    "70 ans et plus",
                ],
            )
            generate_donnuts("RS2C_RECODE_AG_R", 7)

    if choix_variable == "Niveau d'étude 📚":
        if choix_diplome == "Niveau primaire 📚":
            generate_header(
                "RS5_R",
                1,
                nb_source_media,
                nb_source,
                [
                    "Niveau primaire",
                    "Secondaire de la 6ème à la 3ème",
                    "Secondaire de la 2nde à la Terminale",
                    "Technique court (CAP, BEP)",
                    "Bac, Bac professionnel, brevet professionnel",
                    "Technique Supérieur (BTS, DUT)",
                    "Supérieur 1er cycle",
                    "Supérieur 2ème cycle",
                    "Doctorat",
                ],
            )
            generate_donnuts("RS5_R", 1)

        if choix_diplome == "Secondaire de la 6ème à la 3ème 🏫":
            generate_header(
                "RS5_R",
                2,
                nb_source_media,
                nb_source,
                [
                    "Niveau primaire",
                    "Secondaire de la 6ème à la 3ème",
                    "Secondaire de la 2nde à la Terminale",
                    "Technique court (CAP, BEP)",
                    "Bac, Bac professionnel, brevet professionnel",
                    "Technique Supérieur (BTS, DUT)",
                    "Supérieur 1er cycle",
                    "Supérieur 2ème cycle",
                    "Doctorat",
                ],
            )
            generate_donnuts("RS5_R", 2)

        if choix_diplome == "Secondaire de la 2nde à la Terminale 🎒":
            generate_header(
                "RS5_R",
                3,
                nb_source_media,
                nb_source,
                [
                    "Niveau primaire",
                    "Secondaire de la 6ème à la 3ème",
                    "Secondaire de la 2nde à la Terminale",
                    "Technique court (CAP, BEP)",
                    "Bac, Bac professionnel, brevet professionnel",
                    "Technique Supérieur (BTS, DUT)",
                    "Supérieur 1er cycle",
                    "Supérieur 2ème cycle",
                    "Doctorat",
                ],
            )
            generate_donnuts("RS5_R", 3)

        if choix_diplome == "Technique court (CAP, BEP) 🛠️":
            generate_header(
                "RS5_R",
                4,
                nb_source_media,
                nb_source,
                [
                    "Niveau primaire",
                    "Secondaire de la 6ème à la 3ème",
                    "Secondaire de la 2nde à la Terminale",
                    "Technique court (CAP, BEP)",
                    "Bac, Bac professionnel, brevet professionnel",
                    "Technique Supérieur (BTS, DUT)",
                    "Supérieur 1er cycle",
                    "Supérieur 2ème cycle",
                    "Doctorat",
                ],
            )
            generate_donnuts("RS5_R", 4)

        if choix_diplome == "Bac, Bac professionnel, brevet professionnel 🎓":
            generate_header(
                "RS5_R",
                5,
                nb_source_media,
                nb_source,
                [
                    "Niveau primaire",
                    "Secondaire de la 6ème à la 3ème",
                    "Secondaire de la 2nde à la Terminale",
                    "Technique court (CAP, BEP)",
                    "Bac, Bac professionnel, brevet professionnel",
                    "Technique Supérieur (BTS, DUT)",
                    "Supérieur 1er cycle",
                    "Supérieur 2ème cycle",
                    "Doctorat",
                ],
            )
            generate_donnuts("RS5_R", 5)

        if choix_diplome == "Technique Supérieur (BTS, DUT) 🏢":
            generate_header(
                "RS5_R",
                6,
                nb_source_media,
                nb_source,
                [
                    "Niveau primaire",
                    "Secondaire de la 6ème à la 3ème",
                    "Secondaire de la 2nde à la Terminale",
                    "Technique court (CAP, BEP)",
                    "Bac, Bac professionnel, brevet professionnel",
                    "Technique Supérieur (BTS, DUT)",
                    "Supérieur 1er cycle",
                    "Supérieur 2ème cycle",
                    "Doctorat",
                ],
            )
            generate_donnuts("RS5_R", 6)

        if choix_diplome == "Supérieur 1er cycle 📘":
            generate_header(
                "RS5_R",
                7,
                nb_source_media,
                nb_source,
                [
                    "Niveau primaire",
                    "Secondaire de la 6ème à la 3ème",
                    "Secondaire de la 2nde à la Terminale",
                    "Technique court (CAP, BEP)",
                    "Bac, Bac professionnel, brevet professionnel",
                    "Technique Supérieur (BTS, DUT)",
                    "Supérieur 1er cycle",
                    "Supérieur 2ème cycle",
                    "Doctorat",
                ],
            )
            generate_donnuts("RS5_R", 7)

        if choix_diplome == "Supérieur 2ème cycle 📗":
            generate_header(
                "RS5_R",
                8,
                nb_source_media,
                nb_source,
                [
                    "Niveau primaire",
                    "Secondaire de la 6ème à la 3ème",
                    "Secondaire de la 2nde à la Terminale",
                    "Technique court (CAP, BEP)",
                    "Bac, Bac professionnel, brevet professionnel",
                    "Technique Supérieur (BTS, DUT)",
                    "Supérieur 1er cycle",
                    "Supérieur 2ème cycle",
                    "Doctorat",
                ],
            )
            generate_donnuts("RS5_R", 8)

        if choix_diplome == "Doctorat 🧑‍🔬":
            generate_header(
                "RS5_R",
                9,
                nb_source_media,
                nb_source,
                [
                    "Niveau primaire",
                    "Secondaire de la 6ème à la 3ème",
                    "Secondaire de la 2nde à la Terminale",
                    "Technique court (CAP, BEP)",
                    "Bac, Bac professionnel, brevet professionnel",
                    "Technique Supérieur (BTS, DUT)",
                    "Supérieur 1er cycle",
                    "Supérieur 2ème cycle",
                    "Doctorat",
                ],
            )
            generate_donnuts("RS5_R", 9)

    if choix_variable == "Revenus Net 💸":
        if choix_revenus == "< 1500€ 💸":
            generate_header(
                "RS14_R",
                1,
                nb_source_media,
                nb_source,
                [
                    "< 1500€",
                    "1500€ - 3000€",
                    "3000€ - 4500€",
                    "4500€ - 7500€",
                    "> 7500€",
                ],
            )
            generate_donnuts("RS14_R", 1)

        if choix_revenus == "1500€ - 3000€ 💵":
            generate_header(
                "RS14_R",
                2,
                nb_source_media,
                nb_source,
                [
                    "< 1500€",
                    "1500€ - 3000€",
                    "3000€ - 4500€",
                    "4500€ - 7500€",
                    "> 7500€",
                ],
            )
            generate_donnuts("RS14_R", 2)

        if choix_revenus == "3000€ - 4500€ 💶":
            generate_header(
                "RS14_R",
                3,
                nb_source_media,
                nb_source,
                [
                    "< 1500€",
                    "1500€ - 3000€",
                    "3000€ - 4500€",
                    "4500€ - 7500€",
                    "> 7500€",
                ],
            )
            generate_donnuts("RS14_R", 3)

        if choix_revenus == "4500€ - 7500€ 💷":
            generate_header(
                "RS14_R",
                4,
                nb_source_media,
                nb_source,
                [
                    "< 1500€",
                    "1500€ - 3000€",
                    "3000€ - 4500€",
                    "4500€ - 7500€",
                    "> 7500€",
                ],
            )
            generate_donnuts("RS14_R", 4)

        if choix_revenus == "> 7500€ 💰":
            generate_header(
                "RS14_R",
                5,
                nb_source_media,
                nb_source,
                [
                    "< 1500€",
                    "1500€ - 3000€",
                    "3000€ - 4500€",
                    "4500€ - 7500€",
                    "> 7500€",
                ],
            )
            generate_donnuts("RS14_R", 5)

    if choix_variable == "CSP 👔":
        if choix_csp == "Agriculteurs exploitants 🚜":
            generate_header(
                "RS4_R",
                1,
                nb_source_media,
                nb_source,
                [
                    "Agriculteurs exploitants",
                    "Artisans, commerçants, chefs d'entreprise",
                    "Cadres et professions intellectuelles supérieures",
                    "Professions intermédiaires",
                    "Employés",
                    "Ouvriers",
                ],
            )
            generate_donnuts("RS4_R", 1)

        if choix_csp == "Artisans, commerçants, chefs d'entreprise 🛠️":
            generate_header(
                "RS4_R",
                2,
                nb_source_media,
                nb_source,
                [
                    "Agriculteurs exploitants",
                    "Artisans, commerçants, chefs d'entreprise",
                    "Cadres et professions intellectuelles supérieures",
                    "Professions intermédiaires",
                    "Employés",
                    "Ouvriers",
                ],
            )
            generate_donnuts("RS4_R", 2)

        if choix_csp == "Cadres et professions intellectuelles supérieures 🏢":
            generate_header(
                "RS4_R",
                3,
                nb_source_media,
                nb_source,
                [
                    "Agriculteurs exploitants",
                    "Artisans, commerçants, chefs d'entreprise",
                    "Cadres et professions intellectuelles supérieures",
                    "Professions intermédiaires",
                    "Employés",
                    "Ouvriers",
                ],
            )
            generate_donnuts("RS4_R", 3)

        if choix_csp == "Professions intermédiaires 📚":
            generate_header(
                "RS4_R",
                4,
                nb_source_media,
                nb_source,
                [
                    "Agriculteurs exploitants",
                    "Artisans, commerçants, chefs d'entreprise",
                    "Cadres et professions intellectuelles supérieures",
                    "Professions intermédiaires",
                    "Employés",
                    "Ouvriers",
                ],
            )
            generate_donnuts("RS4_R", 4)

        if choix_csp == "Employés 💼":
            generate_header(
                "RS4_R",
                5,
                nb_source_media,
                nb_source,
                [
                    "Agriculteurs exploitants",
                    "Artisans, commerçants, chefs d'entreprise",
                    "Cadres et professions intellectuelles supérieures",
                    "Professions intermédiaires",
                    "Employés",
                    "Ouvriers",
                ],
            )
            generate_donnuts("RS4_R", 5)

        if choix_csp == "Ouvriers 🏭":
            generate_header(
                "RS4_R",
                6,
                nb_source_media,
                nb_source,
                [
                    "Agriculteurs exploitants",
                    "Artisans, commerçants, chefs d'entreprise",
                    "Cadres et professions intellectuelles supérieures",
                    "Professions intermédiaires",
                    "Employés",
                    "Ouvriers",
                ],
            )
            generate_donnuts("RS4_R", 6)


########################################################################################
def fiabilité_info():
    confiances = [
        "INF3_R_1",
        "INF3_R_2",
        "INF3_R_3",
        "INF3_R_6",
        "INF3_R_5",
        "INF3_R_8",
    ]
    if choix_variable == "Global":
        j, k, l = st.columns(3)
        st.markdown("---")
        m, n, o = st.columns(3)
        with j:
            confiance_journaux = (
                db.query(
                    """
                SELECT
                    INF3_R_1 as Confiance
                FROM
                    data
            """
                )
                .df()
                .value_counts()
            )
            
            liste_indices = []
            for i in confiance_journaux.index.tolist():
                if i[0] == 1:
                    liste_indices.append(4)
                elif i[0] == 2:
                    liste_indices.append(3)
                elif i[0] == 3:
                    liste_indices.append(2)
                elif i[0] == 4:
                    liste_indices.append(1)
            value = round(
                sum(
                    [
                        i * v
                        for i, v in zip(
                            liste_indices,
                            confiance_journaux.values.tolist(),
                        )
                    ]
                )
                / sum(confiance_journaux.values.tolist()),
                2,
            )
                    
            

            st.markdown(
                f"""
                <div class="custom-metric">
                    <div class="metric-icon">✍️</div> 
                    <div class="metric-value">{value} / 4</div>
                    <div class="metric-label">Journalistes</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with k:
            confiance_experts = (
                db.query(
                    """
                SELECT
                    INF3_R_2 as Confiance
                FROM
                    data
            """
                )
                .df()
                .value_counts()
            )

            liste_indices = []
            for i in confiance_experts.index.tolist():
                if i[0] == 1:
                    liste_indices.append(4)
                elif i[0] == 2:
                    liste_indices.append(3)
                elif i[0] == 3:
                    liste_indices.append(2)
                elif i[0] == 4:
                    liste_indices.append(1)
                    
            value = round(
                sum(
                    [
                        i * v
                        for i, v in zip(
                            liste_indices,
                            confiance_experts.values.tolist(),
                        )
                    ]
                )
                / sum(confiance_experts.values.tolist()),
                2,
            )

            st.markdown(
                f"""
                <div class="custom-metric">
                    <div class="metric-icon">🧠</div> 
                    <div class="metric-value">{value} / 4</div>
                    <div class="metric-label">Experts </div>
                    <div class="metric-note">Invités dans les médias</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with l:
            confiance_politiciens = (
                db.query(
                    """
                SELECT
                    INF3_R_3 as Confiance
                FROM
                    data
            """
                )
                .df()
                .value_counts()
            )

            liste_indices = []
            for i in confiance_politiciens.index.tolist():
                if i[0] == 1:
                    liste_indices.append(4)
                elif i[0] == 2:
                    liste_indices.append(3)
                elif i[0] == 3:
                    liste_indices.append(2)
                elif i[0] == 4:
                    liste_indices.append(1)
                    
            value = round(
                sum(
                    [
                        i * v
                        for i, v in zip(
                            liste_indices,
                            confiance_politiciens.values.tolist(),
                        )
                    ]
                )
                / sum(confiance_politiciens.values.tolist()),
                2,
            )

            st.markdown(
                f"""
                <div class="custom-metric">
                    <div class="metric-icon">🏛️</div> 
                    <div class="metric-value">{value} / 4</div>
                    <div class="metric-label">Politiciens </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with m:
            confiance_influenceurs = (
                db.query(
                    """
                SELECT
                    INF3_R_6 as Confiance
                FROM
                    data
            """
                )
                .df()
                .value_counts()
            )

            liste_indices = []
            
            for i in confiance_influenceurs.index.tolist():
                if i[0] == 1:
                    liste_indices.append(4)
                elif i[0] == 2:
                    liste_indices.append(3)
                elif i[0] == 3:
                    liste_indices.append(2)
                elif i[0] == 4:
                    liste_indices.append(1)
            value = round(
                sum(
                    [
                        i * v
                        for i, v in zip(
                            liste_indices,
                            confiance_influenceurs.values.tolist(),
                        )
                    ]
                )
                / sum(confiance_influenceurs.values.tolist()),
                2,
            )

            st.markdown(
                f"""
                <div class="custom-metric">
                    <div class="metric-icon">💻</div> 
                    <div class="metric-value">{value} / 4</div>
                    <div class="metric-label">Influenceurs </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with n:
            confiance_celeb = (
                db.query(
                    """
                SELECT
                    INF3_R_5 as Confiance
                FROM
                    data
            """
                )
                .df()
                .value_counts()
            )

            liste_indices = []
            for i in confiance_celeb.index.tolist():
                if i[0] == 1:
                    liste_indices.append(4)
                elif i[0] == 2:
                    liste_indices.append(3)
                elif i[0] == 3:
                    liste_indices.append(2)
                elif i[0] == 4:
                    liste_indices.append(1)
            value = round(
                sum(
                    [
                        i * v
                        for i, v in zip(
                            liste_indices,
                            confiance_celeb.values.tolist(),
                        )
                    ]
                )
                / sum(confiance_celeb.values.tolist()),
                2,
            )

            st.markdown(
                f"""
                <div class="custom-metric">
                    <div class="metric-icon">🌟</div> 
                    <div class="metric-value">{value} / 4</div>
                    <div class="metric-label">Célébrités </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with o:
            confiance_anonymes = (
                db.query(
                    """
                SELECT
                    INF3_R_8 as Confiance
                FROM
                    data
            """
                )
                .df()
                .value_counts()
            )

            liste_indices = []
            
            for i in confiance_anonymes.index.tolist():
                if i[0] == 1:
                    liste_indices.append(4)
                elif i[0] == 2:
                    liste_indices.append(3)
                elif i[0] == 3:
                    liste_indices.append(2)
                elif i[0] == 4:
                    liste_indices.append(1)
            value = round(
                sum(
                    [
                        i * v
                        for i, v in zip(
                            liste_indices,
                            confiance_anonymes.values.tolist(),
                        )
                    ]
                )
                / sum(confiance_anonymes.values.tolist()),
                2,
            )

            st.markdown(
                f"""
                <div class="custom-metric">
                    <div class="metric-icon">🗨️</div> 
                    <div class="metric-value">{value} / 4</div>
                    <div class="metric-label">Anonymes </div>
                    <div class="metric-note">Posts, Commentaires sur Internet</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("---")
    if choix_variable == "Genre 🧑‍🤝‍🧑":
        if choix_genre == "Homme 🧑":
            afficher_confiances("RS1_R", 1, confiances, ["homme", "femme"])
            st.markdown("---")

        if choix_genre == "Femme 👩":
            afficher_confiances("RS1_R", 2, confiances, ["homme", "femme"])
            st.markdown("---")

    if choix_variable == "Âge 👵":
        if choix_age == "15-17 ans 🧒":
            afficher_confiances(
                "RS2C_RECODE_AG_R",
                1,
                confiances,
                [
                    "15-17 ans",
                    "18-24 ans",
                    "25-34 ans",
                    "35-44 ans",
                    "45-59 ans",
                    "60-69 ans",
                    "70 ans et plus",
                ],
            )
            st.markdown("---")

        if choix_age == "18-24 ans 👩‍🎓":
            afficher_confiances(
                "RS2C_RECODE_AG_R",
                2,
                confiances,
                [
                    "15-17 ans",
                    "18-24 ans",
                    "25-34 ans",
                    "35-44 ans",
                    "45-59 ans",
                    "60-69 ans",
                    "70 ans et plus",
                ],
            )
            st.markdown("---")

        if choix_age == "25-34 ans 👩‍💼":
            afficher_confiances(
                "RS2C_RECODE_AG_R",
                3,
                confiances,
                [
                    "15-17 ans",
                    "18-24 ans",
                    "25-34 ans",
                    "35-44 ans",
                    "45-59 ans",
                    "60-69 ans",
                    "70 ans et plus",
                ],
            )
            st.markdown("---")

        if choix_age == "35-44 ans 👩‍🔬":
            afficher_confiances(
                "RS2C_RECODE_AG_R",
                4,
                confiances,
                [
                    "15-17 ans",
                    "18-24 ans",
                    "25-34 ans",
                    "35-44 ans",
                    "45-59 ans",
                    "60-69 ans",
                    "70 ans et plus",
                ],
            )
            st.markdown("---")

        if choix_age == "45-59 ans 👩‍🚀":
            afficher_confiances(
                "RS2C_RECODE_AG_R",
                5,
                confiances,
                [
                    "15-17 ans",
                    "18-24 ans",
                    "25-34 ans",
                    "35-44 ans",
                    "45-59 ans",
                    "60-69 ans",
                    "70 ans et plus",
                ],
            )
            st.markdown("---")

        if choix_age == "60-69 ans 👵":
            afficher_confiances(
                "RS2C_RECODE_AG_R",
                6,
                confiances,
                [
                    "15-17 ans",
                    "18-24 ans",
                    "25-34 ans",
                    "35-44 ans",
                    "45-59 ans",
                    "60-69 ans",
                    "70 ans et plus",
                ],
            )
            st.markdown("---")

        if choix_age == "70 ans et plus 👴":
            afficher_confiances(
                "RS2C_RECODE_AG_R",
                7,
                confiances,
                [
                    "15-17 ans",
                    "18-24 ans",
                    "25-34 ans",
                    "35-44 ans",
                    "45-59 ans",
                    "60-69 ans",
                    "70 ans et plus",
                ],
            )
            st.markdown("---")

    if choix_variable == "Niveau d'étude 📚":
        if choix_diplome == "Niveau primaire 📚":
            afficher_confiances(
                "RS5_R",
                1,
                confiances,
                [
                    "Niveau primaire",
                    "Secondaire de la 6ème à la 3ème",
                    "Secondaire de la 2nde à la Terminale",
                    "Technique court (CAP, BEP)",
                    "Bac, Bac professionnel, brevet professionnel",
                    "Technique Supérieur (BTS, DUT)",
                    "Supérieur 1er cycle",
                    "Supérieur 2ème cycle",
                    "Doctorat",
                ],
            )
            st.markdown("---")

        if choix_diplome == "Secondaire de la 6ème à la 3ème 🏫":
            afficher_confiances(
                "RS5_R",
                2,
                confiances,
                [
                    "Niveau primaire",
                    "Secondaire de la 6ème à la 3ème",
                    "Secondaire de la 2nde à la Terminale",
                    "Technique court (CAP, BEP)",
                    "Bac, Bac professionnel, brevet professionnel",
                    "Technique Supérieur (BTS, DUT)",
                    "Supérieur 1er cycle",
                    "Supérieur 2ème cycle",
                    "Doctorat",
                ],
            )
            st.markdown("---")

        if choix_diplome == "Secondaire de la 2nde à la Terminale 🎒":
            afficher_confiances(
                "RS5_R",
                3,
                confiances,
                [
                    "Niveau primaire",
                    "Secondaire de la 6ème à la 3ème",
                    "Secondaire de la 2nde à la Terminale",
                    "Technique court (CAP, BEP)",
                    "Bac, Bac professionnel, brevet professionnel",
                    "Technique Supérieur (BTS, DUT)",
                    "Supérieur 1er cycle",
                    "Supérieur 2ème cycle",
                    "Doctorat",
                ],
            )
            st.markdown("---")

        if choix_diplome == "Technique court (CAP, BEP) 🛠️":
            afficher_confiances(
                "RS5_R",
                4,
                confiances,
                [
                    "Niveau primaire",
                    "Secondaire de la 6ème à la 3ème",
                    "Secondaire de la 2nde à la Terminale",
                    "Technique court (CAP, BEP)",
                    "Bac, Bac professionnel, brevet professionnel",
                    "Technique Supérieur (BTS, DUT)",
                    "Supérieur 1er cycle",
                    "Supérieur 2ème cycle",
                    "Doctorat",
                ],
            )
            st.markdown("---")

        if choix_diplome == "Bac, Bac professionnel, brevet professionnel 🎓":
            afficher_confiances(
                "RS5_R",
                5,
                confiances,
                [
                    "Niveau primaire",
                    "Secondaire de la 6ème à la 3ème",
                    "Secondaire de la 2nde à la Terminale",
                    "Technique court (CAP, BEP)",
                    "Bac, Bac professionnel, brevet professionnel",
                    "Technique Supérieur (BTS, DUT)",
                    "Supérieur 1er cycle",
                    "Supérieur 2ème cycle",
                    "Doctorat",
                ],
            )
            st.markdown("---")

        if choix_diplome == "Technique Supérieur (BTS, DUT) 🏢":
            afficher_confiances(
                "RS5_R",
                6,
                confiances,
                [
                    "Niveau primaire",
                    "Secondaire de la 6ème à la 3ème",
                    "Secondaire de la 2nde à la Terminale",
                    "Technique court (CAP, BEP)",
                    "Bac, Bac professionnel, brevet professionnel",
                    "Technique Supérieur (BTS, DUT)",
                    "Supérieur 1er cycle",
                    "Supérieur 2ème cycle",
                    "Doctorat",
                ],
            )
            st.markdown("---")

        if choix_diplome == "Supérieur 1er cycle 📘":
            afficher_confiances(
                "RS5_R",
                7,
                confiances,
                [
                    "Niveau primaire",
                    "Secondaire de la 6ème à la 3ème",
                    "Secondaire de la 2nde à la Terminale",
                    "Technique court (CAP, BEP)",
                    "Bac, Bac professionnel, brevet professionnel",
                    "Technique Supérieur (BTS, DUT)",
                    "Supérieur 1er cycle",
                    "Supérieur 2ème cycle",
                    "Doctorat",
                ],
            )
            st.markdown("---")

        if choix_diplome == "Supérieur 2ème cycle 📗":
            afficher_confiances(
                "RS5_R",
                8,
                confiances,
                [
                    "Niveau primaire",
                    "Secondaire de la 6ème à la 3ème",
                    "Secondaire de la 2nde à la Terminale",
                    "Technique court (CAP, BEP)",
                    "Bac, Bac professionnel, brevet professionnel",
                    "Technique Supérieur (BTS, DUT)",
                    "Supérieur 1er cycle",
                    "Supérieur 2ème cycle",
                    "Doctorat",
                ],
            )
            st.markdown("---")

        if choix_diplome == "Doctorat 🧑‍🔬":
            afficher_confiances(
                "RS5_R",
                9,
                confiances,
                [
                    "Niveau primaire",
                    "Secondaire de la 6ème à la 3ème",
                    "Secondaire de la 2nde à la Terminale",
                    "Technique court (CAP, BEP)",
                    "Bac, Bac professionnel, brevet professionnel",
                    "Technique Supérieur (BTS, DUT)",
                    "Supérieur 1er cycle",
                    "Supérieur 2ème cycle",
                    "Doctorat",
                ],
            )
            st.markdown("---")

    if choix_variable == "Revenus Net 💸":
        if choix_revenus == "< 1500€ 💸":
            afficher_confiances(
                "RS14_R",
                1,
                confiances,
                [
                    "< 1500€",
                    "1500€ - 3000€",
                    "3000€ - 4500€",
                    "4500€ - 7500€",
                    "> 7500€",
                ],
            )
            st.markdown("---")

        if choix_revenus == "1500€ - 3000€ 💵":
            afficher_confiances(
                "RS14_R",
                2,
                confiances,
                [
                    "< 1500€",
                    "1500€ - 3000€",
                    "3000€ - 4500€",
                    "4500€ - 7500€",
                    "> 7500€",
                ],
            )
            st.markdown("---")

        if choix_revenus == "3000€ - 4500€ 💶":
            afficher_confiances(
                "RS14_R",
                3,
                confiances,
                [
                    "< 1500€",
                    "1500€ - 3000€",
                    "3000€ - 4500€",
                    "4500€ - 7500€",
                    "> 7500€",
                ],
            )
            st.markdown("---")

        if choix_revenus == "4500€ - 7500€ 💷":
            afficher_confiances(
                "RS14_R",
                4,
                confiances,
                [
                    "< 1500€",
                    "1500€ - 3000€",
                    "3000€ - 4500€",
                    "4500€ - 7500€",
                    "> 7500€",
                ],
            )
            st.markdown("---")

        if choix_revenus == "> 7500€ 💰":
            afficher_confiances(
                "RS14_R",
                5,
                confiances,
                [
                    "< 1500€",
                    "1500€ - 3000€",
                    "3000€ - 4500€",
                    "4500€ - 7500€",
                    "> 7500€",
                ],
            )
            st.markdown("---")

    if choix_variable == "CSP 👔":
        if choix_csp == "Agriculteurs exploitants 🚜":
            afficher_confiances(
                "RS4_R",
                1,
                confiances,
                [
                    "Agriculteurs exploitants",
                    "Artisans, commerçants, chefs d'entreprise",
                    "Cadres et professions intellectuelles supérieures",
                    "Professions intermédiaires",
                    "Employés",
                    "Ouvriers",
                ],
            )
            st.markdown("---")

        if choix_csp == "Artisans, commerçants, chefs d'entreprise 🛠️":
            afficher_confiances(
                "RS4_R",
                2,
                confiances,
                [
                    "Agriculteurs exploitants",
                    "Artisans, commerçants, chefs d'entreprise",
                    "Cadres et professions intellectuelles supérieures",
                    "Professions intermédiaires",
                    "Employés",
                    "Ouvriers",
                ],
            )
            st.markdown("---")

        if choix_csp == "Cadres et professions intellectuelles supérieures 👔":
            afficher_confiances(
                "RS4_R",
                3,
                confiances,
                [
                    "Agriculteurs exploitants",
                    "Artisans, commerçants, chefs d'entreprise",
                    "Cadres et professions intellectuelles supérieures",
                    "Professions intermédiaires",
                    "Employés",
                    "Ouvriers",
                ],
            )
            st.markdown("---")

        if choix_csp == "Professions intermédiaires 📚":
            afficher_confiances(
                "RS4_R",
                4,
                confiances,
                [
                    "Agriculteurs exploitants",
                    "Artisans, commerçants, chefs d'entreprise",
                    "Cadres et professions intellectuelles supérieures",
                    "Professions intermédiaires",
                    "Employés",
                    "Ouvriers",
                ],
            )
            st.markdown("---")

        if choix_csp == "Employés 💼":
            afficher_confiances(
                "RS4_R",
                5,
                confiances,
                [
                    "Agriculteurs exploitants",
                    "Artisans, commerçants, chefs d'entreprise",
                    "Cadres et professions intellectuelles supérieures",
                    "Professions intermédiaires",
                    "Employés",
                    "Ouvriers",
                ],
            )
            st.markdown("---")

        if choix_csp == "Ouvriers 🏭":
            afficher_confiances(
                "RS4_R",
                6,
                confiances,
                [
                    "Agriculteurs exploitants",
                    "Artisans, commerçants, chefs d'entreprise",
                    "Cadres et professions intellectuelles supérieures",
                    "Professions intermédiaires",
                    "Employés",
                    "Ouvriers",
                ],
            )
            st.markdown("---")


########################################################################################
########################################################################################


def Graphe_mots_clefs(ina, Var_ref_1, Var_ref_2, gr_1_select, gr_1_mult):
    sub_ina = ina[(ina[f"{Var_ref_1}"] == gr_1_select)]
    sub_ina = sub_ina[sub_ina[f"{Var_ref_2}"].isin(gr_1_mult)]
    sub_ina.sort_values(by="Date", ascending=True, inplace=True)

    sub_ina_theme = (
        sub_ina.groupby(["Year", f"{Var_ref_2}"])
        .agg({"Nb Mots clefs": "sum"})
        .reset_index()
    )

    chart = (
        alt.Chart(sub_ina_theme)
        .mark_point(opacity=1)
        .encode(
            x=alt.X("Year:O", title=None),
            color=alt.Color(f"{Var_ref_2}"),
        )
    )

    line = chart.mark_line().encode(
        y=alt.Y("mean(Nb Mots clefs):Q", title="Nombre de mots clés")  # A voir
    )

    # line = alt.Chart(sub_ina_theme).mark_area().encode(
    #     x=alt.X("Year:O", title=None),
    #     y=alt.Y("mean(Nb Mots clefs):Q", title="Nombre de mots clés"),
    #     color=alt.Color(f"{Var_ref_2}"),
    # )

    point_chart = (
        alt.Chart(sub_ina_theme)
        .mark_point(size=50, filled=True)
        .encode(
            x=alt.X("Year:O"),
            y=alt.Y("Nb Mots clefs:Q"),
            color=f"{Var_ref_2}",
            tooltip=[f"{Var_ref_2}", "Year", "Nb Mots clefs"],
        )
    )

    alt.theme.enable("carbong100")

    if Var_ref_1 == "Theme":
        title = f"Nombre moyen de mots clefs relié au lexique {gr_1_select} par chaîne par année"
    else:
        title = f"Themes les plus abordés pour {gr_1_select} par année"

    chart_final = (
        (line + point_chart)
        .configure_view(fill=None, stroke=None)
        .properties(
            width=700,
            height=450,
            title={
                "text": title,
                "subtitle": "Source : INA",
                "subtitleColor": "white",
            },
        )
    ).interactive()

    return chart_final


########################################################################################


def Graphe_audience(Data_long, Chaine):
    Data_long = Data_long[
        (Data_long["Chaine"].isin(Chaine))
        & (Data_long["Année"] >= 2000)
        & (Data_long["Année"] <= 2020)
    ]

    Chart = (
        alt.Chart(Data_long)
        .mark_line()
        .encode(
            x=alt.X("Année:O", title=None),
            y=alt.Y("part_audience:Q", title="Part de l'audience (%)"),
            color=alt.Color("Chaine:N"),
            tooltip=["Année", "part_audience", "Chaine"],
        )
    )

    point_chart = (
        alt.Chart(Data_long)
        .mark_point(filled=True)
        .encode(
            x=alt.X("Année:O"),
            y=alt.Y("part_audience:Q"),
            color=alt.Color("Chaine:N"),
            tooltip=["Année", "part_audience", "Chaine"],
        )
    )

    alt.theme.enable("carbong100")

    final_chart = (
        (Chart + point_chart)
        .configure_view(fill=None, stroke=None)
        .properties(
            width=700,
            height=450,
            title={
                "text": f"Part de l'audience des chaines de télévision en France de 2000 à 2020",  # {', '.join(Data_long['Chaine'].unique())}
                "subtitle": "Source : INA",
                "subtitleColor": "white",
            },
        )
        .interactive()
    )

    return final_chart


########################################################################################


def Graphe_prog_tv_audience(Prog_TV, var_select_TV):
    df_long = Prog_TV.melt(id_vars=["Prog"], var_name="Année", value_name="Audience")
    df_long["Année"] = df_long["Année"].astype(int)
    df_long = df_long[(df_long["Année"] >= 2000) & (df_long["Année"] <= 2020)]

    Chart = (
        alt.Chart(df_long[df_long["Prog"].isin(var_select_TV)])
        .mark_line()
        .encode(
            x=alt.X("Année:N", title=None),
            y=alt.Y("Audience:Q", title="Part de l'audience (%)"),
            color="Prog:N",
        )
    )

    point_chart = (
        alt.Chart(df_long[df_long["Prog"].isin(var_select_TV)])
        .mark_circle()
        .encode(x="Année:N", y="Audience:Q", color="Prog:N")
    )

    Final_Chart = (
        (Chart + point_chart)
        .properties(
            width=700,
            height=450,
            title="Audience des programmes télévisés en France de 2000 à 2020",
        )
        .configure_view(fill=None, stroke=None)
        .interactive()
    )

    return Final_Chart


########################################################################################


def Graphe_tranche_Age(Durree_ecoute_age):
    df_long = Durree_ecoute_age.melt(
        id_vars=["Année"], var_name="Age", value_name="Durée"
    )
    df_long["Durée"] = df_long["Durée"].astype(float)
    df_long = df_long[(df_long["Année"] >= 2000) & (df_long["Année"] <= 2020)]

    Chart = (
        alt.Chart(df_long)
        .mark_line()
        .encode(
            x=alt.X("Année:N", title=None),
            y=alt.Y("Durée:Q"),
            color=alt.Color("Age:N"),
        )
    )

    point = Chart.mark_circle().encode(
        x=alt.X("Année:N"),
        y=alt.Y("Durée:Q"),
        color=alt.Color("Age:N"),
        tooltip=["Année", "Durée", "Age"],
    )

    Final_Chart = (
        (Chart + point)
        .properties(
            width=800,
            height=400,
            title="Durée d'écoute quotidienne en minutes de la télévision par tranche d'âge de 2000 à 2020",
        )
        .configure_view(fill=None, stroke=None)
        .interactive()
    )

    return Final_Chart


#######################################################################################


def Graphe_conf_niv(arcom):
    cols_conf = arcom.filter(regex=r"INF3_R1_(\d)").columns

    liste_obj, cols_data, var, title = var_selection(var_obj)

    title += " en la confiance accordée aux sources d'information"

    columns_conf = defaultdict(dict)

    for item, ref in zip(liste_obj, cols_data):
        for col in cols_conf:
            columns_conf[ref][col] = {
                "Journalistes": (arcom[(arcom[var] == item)][col] == 1).sum(),
                "Experts Invités": (arcom[(arcom[var] == item)][col] == 2).sum(),
                "Perso° Politiques GVT": (arcom[(arcom[var] == item)][col] == 3).sum(),
                "Autres Perso° Politiques": (
                    arcom[(arcom[var] == item)][col] == 4
                ).sum(),
                "Célébrités": (arcom[(arcom[var] == item)][col] == 5).sum(),
                "Créateurs Contenu": (arcom[(arcom[var] == item)][col] == 6).sum(),
                "Associations/ACDT": (arcom[(arcom[var] == item)][col] == 7).sum(),
                "Anonymes": (arcom[(arcom[var] == item)][col] == 8).sum(),
                "Proches": (arcom[(arcom[var] == item)][col] == 9).sum(),
            }

    rows = []
    for ref, motiv_data in columns_conf.items():
        sum_motivations = {}
        total_sum = 0

        for _, motivations in motiv_data.items():
            for motivation, value in motivations.items():
                sum_motivations[motivation] = sum_motivations.get(motivation, 0) + value
                total_sum += value

        for motivation, total in sum_motivations.items():
            if total_sum > 0:
                valeur_norm = total / total_sum
            else:
                valeur_norm = 0
            rows.append(
                {"ref": ref, "Source": motivation, "Valeur": round(valeur_norm, 3)}
            )

    df = pd.DataFrame(rows)

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("ref:N", title=""),
            y=alt.Y("Valeur:Q", title="", stack="normalize"),
            color=alt.Color("Source:N", title="Source"),
            tooltip=["ref", "Source", "Valeur"],
        )
        .configure_view(fill=None, stroke=None)
        .properties(
            title={
                "text": title,
                "subtitle": "Source : Arcom 2024, base : 3356 répondants",
                "subtitleColor": "white",
            },
            width=700,
            height=400,
        )
    )

    return chart


########################################################################################


def Graphe_nb_sources(arcom):
    liste_obj, cols_data, var, title = var_selection(var_obj)

    res = pd.DataFrame()

    for item, ref in zip(liste_obj, cols_data):
        test = arcom[arcom[var] == item]
        colonnes = test.filter(regex=r"SOURCES1(\w)R_B(\d)_R_(\d)").columns
        distribution = test[colonnes].notna().sum(axis=1).value_counts().reset_index()

        distribution.columns = ["Nombre de sources", "Nb réponses"]
        distribution["ref"] = ref
        distribution_inf_25 = distribution[distribution["Nombre de sources"] < 25]
        distribution_25_plus = pd.DataFrame(
            {
                "ref": ref,
                "Nombre de sources": ["25+"],
                "Nb réponses": distribution["Nb réponses"][
                    distribution["Nombre de sources"] >= 25
                ].sum(),
            }
        )

        res = pd.concat(
            [res, pd.concat([distribution_inf_25, distribution_25_plus])],
            ignore_index=True,
        )

    res["Nombre de sources"] = res["Nombre de sources"].astype(str)
    nombres_sources = res["Nombre de sources"].unique()
    nombres_sources_sorted = sorted([x for x in nombres_sources if x != "25+"], key=int)
    nombres_sources_sorted.append("25+")
    res["réponse par classe"] = res.groupby("ref")["Nb réponses"].transform(
        lambda x: x / x.sum()
    )

    chart = (
        alt.Chart(res)
        .mark_area(
            interpolate="monotone", fillOpacity=0.8, stroke="lightgray", strokeWidth=0.5
        )
        .encode(
            x=alt.X("Nombre de sources:N", title=None, sort=nombres_sources_sorted),
            y=alt.Y("réponse par classe:Q", title=None, axis=None),
            color=alt.Color(
                "ref:N",
                scale=alt.Scale(scheme="spectral"),
                legend=alt.Legend(title="Catégorie des répondants"),
            ),
            tooltip=["ref", "Nombre de sources", "réponse par classe"],
        )
        .properties(
            width=700,
            height=375,
            title={
                "text": "Nombre de sources d'information consultées pour s'informer parmi 56 proposées (radio, réseaux sociaux, ...)",
                "subtitle": "Source : Arcom 2024, base : 2949 répondants, Les réponses sont exprimés en pourcentage de chaque classe.",
                "subtitleColor": "white",
            },
        )
        .configure_view(fill=None, stroke=None)
    )

    return chart


# colonnes = arcom.filter(regex=r"SOURCES1(\w)R_B(\d)_R_(\d)").columns
# distribution = pd.DataFrame({"Nb réponses": arcom[colonnes].notna().sum(axis=1).value_counts()})
# distribution = distribution.reset_index()
# distribution.columns = ['Nombre de sources', 'Nb réponses']

# distribution_inf_33 = distribution[distribution['Nombre de sources'] < 33]
# distribution_33_plus = pd.DataFrame({
#     'Nombre de sources': ['33+'],
#     'Nb réponses': distribution[distribution['Nombre de sources'] >= 33]['Nb réponses'].sum()
# })
# distribution = pd.concat([distribution_inf_33, distribution_33_plus], ignore_index=True)
# distribution['Nombre de sources'] = distribution['Nombre de sources'].astype(str)
# categories_ordre = list(distribution_inf_33['Nombre de sources'].astype(int).astype(str)) + ['33+']


########################################################################################
@st.cache_data
def Graphe_motivations(arcom, var_obj, level):
    _, cols_data, var, _ = var_selection(var_obj)

    df = (
        arcom.groupby(var)
        .apply(
            lambda g: g.filter(regex=r"MOTIV_R_(\d)").apply(
                lambda x: x.value_counts(normalize=True)
            )
        )
        .fillna(0)
    )
    cols = [f"MOTIV {i+1}" for i in range(14)]
    df.columns = cols

    df.reset_index(inplace=True)
    df["level_1"] = df["level_1"].astype(int).astype(str)
    df["Ref"] = df[f"{var}"].replace(
        dict(zip(sorted(df[f"{var}"].unique()), cols_data))
    )

    attentes_columns = df.filter(regex=r"MOTIV (\d+)").columns.tolist()

    df_long = df.melt(
        id_vars=["Ref", "level_1"],
        value_vars=attentes_columns,
        var_name="Motivation",
        value_name="% Réponses",
    )

    Chart = (
        alt.Chart(df_long[df_long["level_1"] == f"{level}"])
        .mark_rect()
        .encode(
            x=alt.X("Ref:N", title=None),
            y=alt.Y("Motivation:N", title=None, sort=alt.EncodingSortField(field="% Réponses", order="descending")),
            color=alt.Color("% Réponses:Q", scale=alt.Scale(scheme="spectral")),
            tooltip=["Motivation", "Ref", "% Réponses"],
        )
        .properties(
            width=800,
            height=400,
            title={
                "text": f"Classement des attentes des sondés par {var_obj}, niveau {level}",
                "subtitle": f"Source : ARCOM 2024, base 2949 répondants",
                "subtitleColor": "white",
            },
        )
        .interactive()
    )

    return Chart


########################################################################################


@st.cache_data
def Graphe_motivations_RS(arcom, var_obj):
    liste_obj, cols_data, var, title = var_selection(var_obj)

    title += " sur leurs motivations à s'informer sur les Réseaux Sociaux"

    liste_obj.sort()
    cols_motiv = arcom.filter(regex=r"MOTIVRS_R_(\d)").columns

    count_motivs = defaultdict(dict)
    for item, ref in zip(liste_obj, cols_data):
        for col in cols_motiv:
            count_motivs[ref][col] = {
                "Comprendre le monde qui m'entoure": (
                    arcom[(arcom[var] == item)][col] == 1
                ).sum(),
                "Rester informé des grands évènements": (
                    arcom[(arcom[var] == item)][col] == 2
                ).sum(),
                "Me faire ma propre opinion": (
                    arcom[(arcom[var] == item)][col] == 3
                ).sum(),
                "Prendre des décisions éclairées": (
                    arcom[(arcom[var] == item)][col] == 4
                ).sum(),
                "Pouvoir en discuter/débattre": (
                    arcom[(arcom[var] == item)][col] == 5
                ).sum(),
                "Me divertir": (arcom[(arcom[var] == item)][col] == 6).sum(),
                "Découvrir de nouvelles tendances culturelles": (
                    arcom[(arcom[var] == item)][col] == 7
                ).sum(),
                "Satisfaire ma curiosité": (
                    arcom[(arcom[var] == item)][col] == 8
                ).sum(),
                "Passer le temps": (arcom[(arcom[var] == item)][col] == 9).sum(),
                "M'instruire / me cultiver": (
                    arcom[(arcom[var] == item)][col] == 10
                ).sum(),
                "Progresser dans mon travail/mes études": (
                    arcom[(arcom[var] == item)][col] == 11
                ).sum(),
                "Connaître d'autres avis que le mien": (
                    arcom[(arcom[var] == item)][col] == 12
                ).sum(),
            }

    rows = []
    for ref, motiv_data in count_motivs.items():
        sum_motivations = {}
        total_sum = 0

        for _, motivations in motiv_data.items():
            for motivation, value in motivations.items():
                sum_motivations[motivation] = sum_motivations.get(motivation, 0) + value
                total_sum += value

        for motivation, total in sum_motivations.items():
            if total_sum > 0:
                valeur_norm = total / total_sum
            else:
                valeur_norm = 0
            rows.append(
                {
                    "ref": ref,
                    "Motivation": motivation,
                    "Pourcentage": round(valeur_norm, 3),
                }
            )

    df = pd.DataFrame(rows)

    chart = (
        alt.Chart(df)
        .mark_rect()
        .encode(
            x=alt.X("ref:O", title=" ", axis=alt.Axis(labelLimit=0)),
            y=alt.Y("Motivation:N", title=" ", axis=alt.Axis(labelLimit=0), sort=alt.EncodingSortField(field="Pourcentage", order="descending")),
            color=alt.Color(
                "Pourcentage:Q",
                scale=alt.Scale(scheme="spectral"),
                legend=alt.Legend(labelLimit=0),
            ),
            tooltip=["ref", "Motivation", "Pourcentage"],
        )
        .configure_view(fill=None, stroke=None)
        .properties(
            title={
                "text": title,
                "subtitle": "Source : Arcom 2024, base : 3356 répondants",
                "subtitleColor": "white",
            },
            width=700,
            height=400,
        )
    )

    return chart


########################################################################################


@st.cache_data
def Graphe_inf_fiable(arcom, var_obj):
    liste_obj, cols_data, var, title = var_selection(var_obj)

    title += " sur ce qu'ils considèrent comme une information fiable"

    liste_obj.sort()
    cols_fiable = arcom.filter(regex=r"INFOFIABLEDEF_R_(\d)").columns

    count = defaultdict(dict)

    for item, ref in zip(liste_obj, cols_data):
        for col in cols_fiable:
            count[ref][col] = {
                "Je connais l'auteur": (arcom[(arcom[var] == item)][col] == 1).sum(),
                "Elle est énoncée par un journaliste": (
                    arcom[(arcom[var] == item)][col] == 2
                ).sum(),
                "Elle vient d'un média très connu": (
                    arcom[(arcom[var] == item)][col] == 3
                ).sum(),
                "Elle est claire et détaillée": (
                    arcom[(arcom[var] == item)][col] == 4
                ).sum(),
                "Elle confirme mes opinions": (
                    arcom[(arcom[var] == item)][col] == 5
                ).sum(),
                "Elle vient d'un média indépendant": (
                    arcom[(arcom[var] == item)][col] == 6
                ).sum(),
                "Je vois qu'elle est reprise par un grand nombre de médias": (
                    arcom[(arcom[var] == item)][col] == 7
                ).sum(),
                "Je vois que l'information est récente": (
                    arcom[(arcom[var] == item)][col] == 8
                ).sum(),
                "Je peux vérifier facilement la source": (
                    arcom[(arcom[var] == item)][col] == 9
                ).sum(),
                "Je ne relève pas d'incohérences évidentes": (
                    arcom[(arcom[var] == item)][col] == 10
                ).sum(),
                "Mes proches m'en parlent": (
                    arcom[(arcom[var] == item)][col] == 11
                ).sum(),
                "Elle repose sur des preuves scientifiques": (
                    arcom[(arcom[var] == item)][col] == 12
                ).sum(),
                "Elle est accompagnée d'une vidéo montrant les événements sans filtre": (
                    arcom[(arcom[var] == item)][col] == 13
                ).sum(),
                "Je ne me soucie pas trop de la fiabilité des informations": (
                    arcom[(arcom[var] == item)][col] == 14
                ).sum(),
            }

    rows = []
    for ref, motiv_data in count.items():
        sum_motivations = {}
        total_sum = 0

        for _, motivations in motiv_data.items():
            for motivation, value in motivations.items():
                sum_motivations[motivation] = sum_motivations.get(motivation, 0) + value
                total_sum += value

        for motivation, total in sum_motivations.items():
            if total_sum > 0:
                valeur_norm = total / total_sum
            else:
                valeur_norm = 0
            rows.append(
                {"ref": ref, "Motivation": motivation, "Valeur": round(valeur_norm, 3)}
            )

    df = pd.DataFrame(rows)

    chart = (
        alt.Chart(df)
        .mark_rect()
        .encode(
            x=alt.X("ref:O", title=" "),
            y=alt.Y("Motivation:N", title=" ", axis=alt.Axis(labelLimit=250), sort=alt.EncodingSortField(field="Valeur", order="descending")),
            color=alt.Color(
                "Valeur:Q",
                scale=alt.Scale(scheme="spectral"),
                legend=alt.Legend(labelLimit=0),
            ),
            tooltip=["ref", "Motivation", "Valeur"],
        )
        .configure_view(fill=None, stroke=None)
        .properties(
            title={
                "text": title,
                "subtitle": "Source : Arcom 2024, base : 3356 répondants",
                "subtitleColor": "white",
            },
            width=700,
            height=375,
        )
    )

    return chart


# def Graphe_inf_fiable(arcom):
#     cols_fiable = arcom.filter(regex=r"INFOFIABLEDEF_R_(\d)").columns
#     sub_df = arcom[cols_fiable]

#     counts_per_column = {}

#     for col in sub_df.columns:
#         counts_per_column[col] = {
#             "Je connais l'auteur": (sub_df[col] == 1).sum(),
#             "Elle est enoncée par un journaliste": (sub_df[col] == 2).sum(),
#             "Elle vient d'un média très connu": (sub_df[col] == 3).sum(),
#             "Elle est claire est détaillé": (sub_df[col] == 4).sum(),
#             "Elle confirme mes opinions": (sub_df[col] == 5).sum(),
#             "Elle vient d'un média indépendant": (sub_df[col] == 6).sum(),
#             "Je vois qu'elle est reprise pas un grand nombre de média": (
#                 sub_df[col] == 7
#             ).sum(),
#             "Je vois que l'information est récente": (sub_df[col] == 8).sum(),
#             "Je peux vérifier facilement la source": (sub_df[col] == 9).sum(),
#             "Je ne relève pas d'incohérence évidentes": (sub_df[col] == 10).sum(),
#             "Mes proches m'en parlent": (sub_df[col] == 11).sum(),
#             "Elle repose sur des preuves scientifiques": (sub_df[col] == 12).sum(),
#             "Elle est accompagnée  d'une vidéo montrant les événements sans filtre": (
#                 sub_df[col] == 13
#             ).sum(),
#             "Je ne me soucie pas trop de la fiabilité des informations": (
#                 sub_df[col] == 14
#             ).sum(),
#         }

#     df_fiable = pd.DataFrame.from_dict(counts_per_column, orient="index")
#     df_fiable.reset_index(inplace=True)
#     df_fiable.rename(columns={"index": "SOURCES"}, inplace=True)

#     for _, clef in enumerate(df_fiable.columns[1:]):
#         df_fiable[f"r_{clef}"] = df_fiable[f"{clef}"] / 2955

#     totaux = df_fiable[
#         [f"{clef}" for _, clef in enumerate(df_fiable.columns[1:])]
#     ].sum()

#     df_fiable.loc["Total"] = totaux

#     sub_df = (
#         pd.DataFrame(df_fiable.iloc[0:15, 15:].iloc[14])
#         .reset_index()
#         .rename(columns={"index": "Sources"})
#     )
#     sub_df["Sources"] = sub_df["Sources"].apply(lambda x: x.split("_")[1])

#     Chart = (
#         alt.Chart(sub_df)
#         .mark_bar()
#         .encode(
#             x=alt.X("Sources:N", axis=alt.Axis(labels=False), title=None),
#             y=alt.Y("Total:Q", title="% de réponses"),
#             tooltip=["Sources:N", "Total"],
#             color="Sources:N",
#         )
#         .configure_view(fill=None, stroke=None)
#         .properties(
#             width=800,
#             height=450,
#             title={
#                 "text": "Réponses des sondès sur la question ' Qu'est ce qu'une information 'fiable' '",
#                 "subtitle": "Source : Arcom 2024, base : 2955 répondants",
#                 "subtitleColor": "white",
#             },
#         )
#     )

#     return Chart


########################################################################################


def Graphe_repartition_répondants(arcom, var_obj):
    _, cols_data, var, title = var_selection(var_obj)

    dict_values = arcom[var].value_counts().sort_index().to_dict()
    nb_rep = sum(dict_values.values())
    dict_values = dict(zip(cols_data, dict_values.values()))

    df = pd.DataFrame(
        {
            "Catégorie": list(dict_values.keys()),
            "Nombre": np.array(list(dict_values.values())) / nb_rep,
        }
    )

    title.split("par ")

    chart = (
        alt.Chart(df)
        .mark_arc()
        .encode(
            theta=alt.Theta("Nombre:Q"),
            color=alt.Color("Catégorie:N", scale=alt.Scale(scheme="spectral")),
            tooltip=["Catégorie", "Nombre"],
        )
        .properties(
            title=f"Répartition {title.split("Préférences ")[1]}", width=700, height=375
        )
    )
    return chart


########################################################################################


@st.cache_data
def Graphe_point_algo(arcom):
    cols = arcom.filter(regex=r"CONNAISSALGOA_R_(\d)").columns
    sub_df = arcom[cols]

    counts_per_column = {}

    for col in sub_df.columns:
        counts_per_column[col] = {
            "compte_1": (sub_df[col] == 1).sum(),
            "compte_2": (sub_df[col] == 2).sum(),
            "compte_3": (sub_df[col] == 3).sum(),
            "compte_4": (sub_df[col] == 4).sum(),
            "compte_5": (sub_df[col] == 5).sum(),
            "compte_6": (sub_df[col] == 6).sum(),
            "compte_7": (sub_df[col] == 7).sum(),
            "compte_8": (sub_df[col] == 8).sum(),
            "compte_9": (sub_df[col] == 9).sum(),
        }

    df = pd.DataFrame.from_dict(counts_per_column, orient="index")
    df.reset_index(inplace=True)
    df.rename(columns={"index": "Opinions"}, inplace=True)

    for i in range(1, 10):
        df[f"ratio_{i}"] = df[f"compte_{i}"] / 2173

    df.sort_values(by="ratio_1", ascending=False, inplace=True)

    df["Totaux"] = df["ratio_1"] + df["ratio_2"]

    df_ratio_1_A = df[["Opinions", "ratio_1"]]
    # df_ratio_2_A = df[["Opinions", "ratio_2"]]

    cols = arcom.filter(regex=r"CONNAISSALGOB_R_(\d)").columns
    sub_df = arcom[cols]

    counts_per_column = {}

    for col in sub_df.columns:
        counts_per_column[col] = {
            "compte_1": (sub_df[col] == 1).sum(),
            "compte_2": (sub_df[col] == 2).sum(),
            "compte_3": (sub_df[col] == 3).sum(),
            "compte_4": (sub_df[col] == 4).sum(),
            "compte_5": (sub_df[col] == 5).sum(),
            "compte_6": (sub_df[col] == 6).sum(),
            "compte_7": (sub_df[col] == 7).sum(),
            "compte_8": (sub_df[col] == 8).sum(),
            "compte_9": (sub_df[col] == 9).sum(),
        }

    df = pd.DataFrame.from_dict(counts_per_column, orient="index")
    df.reset_index(inplace=True)
    df.rename(columns={"index": "Opinions"}, inplace=True)

    for i in range(1, 10):
        df[f"ratio_{i}"] = df[f"compte_{i}"] / 2173

    df.sort_values(by="ratio_1", ascending=False, inplace=True)

    df["Totaux"] = df["ratio_1"] + df["ratio_2"] + df["ratio_3"]

    # df_ratio_1_B = df[["Opinions", "ratio_1"]]
    # df_ratio_2_B = df[["Opinions", "ratio_2"]]
    df_ratio_3_B = df[["Opinions", "ratio_3"]]

    temp_1 = df_ratio_1_A.sort_values(by="Opinions", ascending=False)
    temp_2 = df_ratio_3_B.sort_values(by="Opinions", ascending=False)

    temp_final = pd.concat([temp_1, temp_2.drop(columns=["Opinions"])], axis=1)
    temp_final["Opinions"] = [
        "Je peux signaler de fausses informations",
        "Les réseaux sociaux diffusent à la fois des informations vraies et fausses",
        "Les informations négatives ou anxiogènes y sont plus souvent diffusées",
        "Les informations dépendent de mon historique",
        "Les informations que je reçois varient selon les préférences des autres utilisateurs",
        "Les réseaux sociaux m'adressent certaines infos plutôt que d'autres",
    ]

    scatter = (
        alt.Chart(temp_final)
        .mark_circle(size=100)
        .encode(
            x=alt.X(
                "ratio_1:Q",
                title=None,
                axis=alt.Axis(ticks=False, labels=False),
                scale=alt.Scale(domain=[0.6, 1]),
            ),
            y=alt.Y(
                "ratio_3:Q",
                title=None,
                axis=alt.Axis(ticks=False, labels=False),
                scale=alt.Scale(domain=[0, 0.8]),
            ),
            tooltip=["Opinions:N"],
            color=alt.Color("Opinions:N", legend=alt.Legend(labelLimit=0)),
        )
    )

    annotations_grad_y = pd.DataFrame(
        {"x": [0.8, 0.8], "y": [0.02, 0.78], "text": ["0%", "80%"]}
    )

    annotations_grad_x = pd.DataFrame(
        {"x": [0.62, 0.98], "y": [0.4, 0.4], "text": ["60%", "100%"]}
    )

    lines = (
        alt.Chart(pd.DataFrame({"x": [0.8]}))
        .mark_rule(color="pink")
        .encode(
            x="x:Q",
            y=alt.datum(0.02),
            y2=alt.datum(0.78),
        )
        + alt.Chart(annotations_grad_y)
        .mark_text(fontSize=16, dx=-20, color="white")
        .encode(x="x:Q", y="y:Q", text="text:N")
        + alt.Chart(pd.DataFrame({"y": [0.4]}))
        .mark_rule(color="pink")
        .encode(
            y="y:Q",
            x=alt.datum(0.62),
            x2=alt.datum(0.98),
        )
        + alt.Chart(annotations_grad_x)
        .mark_text(fontSize=16, dy=10, color="white")
        .encode(x="x:Q", y="y:Q", text="text:N")
    )

    annotations = pd.DataFrame(
        {
            "x": [0.75, 0.95],
            "y": [0.75, 0.45],
            "text": ["Cela me dérange", "C'est exact"],
        }
    )

    quadrant_text = (
        alt.Chart(annotations)
        .mark_text(fontSize=16, color="#8b5cf6")
        .encode(x="x:Q", y="y:Q", text="text:N")
    )

    Final_chart = (
        (scatter + lines + quadrant_text)
        .configure_view(fill=None, stroke=None)
        .properties(
            width=400,
            height=400,
            title={
                "text": "Interaction croisée entre la 'lucidité' des répondants et leurs 'sentiments' à l'égard des informations sur les réseaux sociaux",
                "subtitle": "Source : Arcom 2024, base : 2173 répondants",
                "subtitleColor": "white",
            },
        )
        .interactive()
    )

    return Final_chart


########################################################################################


def Graphe_pref_algo(arcom, var_obj):
    liste_obj, cols_data, var, title = var_selection(var_obj)

    title += " sur la manière dont ils préfèrent être informés"

    liste_obj.sort()

    Count = {}
    for item in liste_obj:
        Count[item] = {
            "Par un Algorithme": len(
                arcom[(arcom["SELECT_R"] == 3) & (arcom[var] == item)]
            )
            / len(arcom[(arcom[var] == item) & (arcom["SELECT_R"].notna())]),
            "Ca m'est égal": len(arcom[(arcom["SELECT_R"] == 2) & (arcom[var] == item)])
            / len(arcom[(arcom[var] == item) & (arcom["SELECT_R"].notna())]),
            "Par une rédaction ou des journalistes": len(
                arcom[(arcom["SELECT_R"] == 1) & (arcom[var] == item)]
            )
            / len(arcom[(arcom[var] == item) & (arcom["SELECT_R"].notna())]),
        }

    data = pd.DataFrame(Count)
    data.columns = cols_data

    data_long = pd.melt(
        data.reset_index(),
        id_vars="index",
        var_name="ref",
        value_name="Pourcentage",
        value_vars=data.columns,
    )
    data_long.rename(columns={"index": "Préférences des sondès"}, inplace=True)

    Final_chart = (
        alt.Chart(data_long)
        .mark_bar()
        .encode(
            x=alt.X("ref:N", title=None),
            y=alt.Y("Pourcentage:Q", title=None),
            color=alt.Color(
                "Préférences des sondès:N",
                scale=alt.Scale(scheme="spectral"),
                legend=alt.Legend(labelLimit=0),
            ),
            tooltip=["ref", "Préférences des sondès", "Pourcentage"],
        )
        .configure_view(fill=None, stroke=None)
        .properties(
            width=500,
            height=375,
            title={
                "text": title,
                "subtitle": "Source : Arcom 2024, base : 2173 répondants",
                "subtitleColor": "white",
            },
        )
    )

    return Final_chart


########################################################################################


def similarite(rep, ref):
    matches = sum(1 for x, y in zip(rep, ref) if x == y)
    return (matches / len(rep)) * 100


def Graph_quizz_age(arcom, var_obj):
    liste_obj, cols_data, var, _ = var_selection(var_obj)

    title = "Pourcentage de bonnes réponses aux quizz"

    liste_obj.sort()

    Quizz = arcom.filter(regex=r"QUIZZ(\d)_R").columns
    b_reponses = [1, 1, 1, 1]
    Count = {}
    for item in liste_obj:
        objet = arcom[arcom[var] == item]
        Count[item] = {
            "0 réponses": sum(
                1
                for row in objet[Quizz].dropna().values
                if similarite(row, b_reponses) == 0.0
            )
            / len(objet.dropna(subset=Quizz)),
            "1 réponses": sum(
                1
                for row in objet[Quizz].dropna().values
                if similarite(row, b_reponses) == 25.0
            )
            / len(objet.dropna(subset=Quizz)),
            "2 réponses": sum(
                1
                for row in objet[Quizz].dropna().values
                if similarite(row, b_reponses) == 50.0
            )
            / len(objet.dropna(subset=Quizz)),
            "3 réponses": sum(
                1
                for row in objet[Quizz].dropna().values
                if similarite(row, b_reponses) == 75.0
            )
            / len(objet.dropna(subset=Quizz)),
            "4 réponses": sum(
                (row == b_reponses).all() for row in objet[Quizz].dropna().values
            )
            / len(objet.dropna(subset=Quizz)),
        }

    data = pd.DataFrame(Count)
    data.columns = cols_data

    data_long = pd.melt(
        data.reset_index(),
        id_vars="index",
        var_name="ref",
        value_name="Pourcentage",
        value_vars=data.columns,
    )
    data_long.rename(columns={"index": "Nombre de bonnes réponses"}, inplace=True)

    chart = (
        alt.Chart(data_long)
        .mark_bar()
        .encode(
            x=alt.X("ref:O", title=" "),
            y=alt.Y("Pourcentage:Q", title=" ", stack="normalize"),
            color=alt.Color("Nombre de bonnes réponses:N"),
            tooltip=["ref", "Nombre de bonnes réponses", "Pourcentage"],
        )
        .configure_view(fill=None, stroke=None)
        .properties(
            title={
                "text": title,
                "subtitle": "Source : Arcom 2024, base : 3356 répondants",
                "subtitleColor": "white",
            },
            width=700,
            height=450,
        )
    )

    # Final_Chart = (
    #     alt.Chart(data_long)
    #     .mark_bar()
    #     .encode(
    #         x=alt.X("Var_x:N", title=None),
    #         y=alt.Y("Pourcentage:Q", title=None, scale=alt.Scale(domain=[0, 1])),
    #         color="Nombre de bonnes réponses:N",
    #         tooltip=["Var_x", "Pourcentage"],
    #     )
    #     .properties(
    #         width=800,
    #         height=450,
    #         title={
    #             "text": title,
    #             "subtitle": "Source : Arcom 2024, base : 3356 répondants",
    #             "subtitleColor": "white",
    #         },
    #     )
    #     .configure_view(fill=None, stroke=None)
    #     .interactive()
    # )

    return chart


########################################################################################


@st.cache_data
def Graphe_type_source(arcom, var_source, var_obj):
    liste_obj, cols_data, var, title = var_selection(var_obj)

    if var_source == "Radio":
        cols = arcom.filter(regex=r"SOURCES1AR_B1_R_(\d)").columns
        sub_df = arcom[cols[:-1]]
        sub_title = " en termes de stations radios"
        liste_var = [
            "Europe 1",
            "France Bleu",
            "France Inter",
            "RMC",
            "RTL",
            "France info",
            "Radio Classique",
            "France Culture",
            "BFM Business",
            "Sud Radio",
            "RFI",
            "Radio Locale",
            "une autre radio",
            "Rien de tout cela",
        ]
    elif var_source == "Presse écrite":
        cols = arcom.filter(regex=r"SOURCES1BR_B2_R_(\d)").columns
        sub_df = arcom[cols[:-1]]
        sub_title = " en termes de journaux"
        liste_var = [
            "Le Monde",
            "Le Parisien",
            "Le Figaro",
            "Les Echos",
            "L'Equipe",
            "la Croix",
            "Libération",
            "L'Humanité",
            "Mediapart",
            "Huffington Post",
            "Un journal regional",
            "Un journal sortant le dimanche",
            "un joural satirique",
            "Un journal gratuit",
            "Un autre journal",
            "Rien de tout cela",
        ]
    elif var_source == "Chaines TV spécialisées":
        cols = arcom.filter(regex=r"SOURCES1ER_B4_R_(\d)").columns
        sub_df = arcom[cols[:-1]]
        sub_title = " en termes de chaines de télévision spécialisées"
        liste_var = [
            "France Info",
            "LCI",
            "BFM TV",
            "C News",
            "France 24",
            "Chaine d'information internationale (Al Jazeera, CNN, etc.)",
            "Une autre chaine d'information internationale",
            "Rien de tout cela",
        ]

    title += sub_title

    counts_per_column = defaultdict(dict)

    for item, ref in zip(liste_obj, cols_data):
        for col in sub_df.columns:
            counts_per_column[ref][col] = {
                f"{clef}": (arcom[arcom[var] == item][col] == i).sum()
                for i, clef in enumerate(liste_var, start=1)
                if clef in liste_var
            }

    rows = []
    for ref, motiv_data in counts_per_column.items():
        sum_sources = {}
        total_sum = 0

        for _, motivations in motiv_data.items():
            for Source, value in motivations.items():
                sum_sources[Source] = sum_sources.get(Source, 0) + value
                total_sum += value

        for Source, total in sum_sources.items():
            if total_sum > 0:
                valeur_norm = total / total_sum
            else:
                valeur_norm = 0
            rows.append({"ref": ref, "Source": Source, "Valeur": round(valeur_norm, 3)})

    df = pd.DataFrame(rows)

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("ref:N", title=""),
            y=alt.Y("Valeur:Q", title="", stack="normalize"),
            color=alt.Color("Source:N", title="Motivation"),
            tooltip=["ref", "Source", "Valeur"],
        )
        .configure_view(fill=None, stroke=None)
        .properties(
            title={
                "text": title,
                "subtitle": "Source : Arcom 2024, base : 3356 répondants",
                "subtitleColor": "white",
            },
            width=700,
            height=450,
        )
    )

    return chart


########################################################################################


def Graphe_Opinions_info(arcom, var_obj):
    _, cols_data, var, _ = var_selection(var_obj)

    data_info = arcom.dropna(subset=[var])
    data_info = data_info[[f"{var}", "VALEURJ_R_1", "INF1_R_1"]].dropna()

    data_scaled = pd.DataFrame(data_info, columns=data_info.columns)
    data_scaled["Source"] = data_info[var]
    data_scaled.rename(columns={"VALEURJ_R_1": "x", "INF1_R_1": "y"}, inplace=True)
    data_scaled["ref"] = data_scaled["Source"].replace(
        dict(zip(sorted(data_scaled["Source"].unique()), cols_data))
    )

    count_data = (
        data_scaled.groupby(["Source", "ref", "x", "y"])
        .size()
        .reset_index(name="count")
    )
    count_data["Pourcentage"] = count_data.groupby("Source")["count"].transform(
        lambda x: x / x.sum()
    )

    def create_chart(source):
        return (
            alt.Chart(count_data[count_data["Source"] == source])
            .mark_rect()
            .encode(
                alt.X("x:N", title=None),
                alt.Y("y:N", title=None),
                alt.Color(
                    "Pourcentage:Q",
                    title="Pourcentage",
                    scale=alt.Scale(scheme="blues"),
                ),
                tooltip=["ref", alt.Tooltip("Pourcentage:Q", format=".2f"), "x", "y"],
            )
            .properties(width=150, height=325)
            .configure_view(fill="black", stroke=None)
            .properties(
                title={
                    "text": f"Visualisation des opinions par {var_obj}, {count_data[count_data["Source"] == source]["ref"].unique()[0]} **",
                    "subtitle": f"Source : Arcom 2024, base : {len(data_info)} répondants",
                    "subtitleColor": "white",
                }
            )
        )

    sources = data_scaled["Source"].unique()
    charts = [create_chart(source) for source in sources]

    return charts

########################################################################################


def Graphe_attentes(arcom, var_obj, level):
    _, cols_data, var, _ = var_selection(var_obj)

    df = (
        arcom.groupby(var)
        .apply(
            lambda g: g.filter(regex=r"ATTENTESJ_R_(\d+)").apply(
                lambda x: x.value_counts(normalize=True)
            )
        )
        .fillna(0)
    )
    df.columns = [
        "ATTENTE 1",
        "ATTENTE 2",
        "ATTENTE 3",
        "ATTENTE 4",
        "ATTENTE 5",
        "ATTENTE 6",
        "ATTENTE 7",
        "ATTENTE 8",
        "ATTENTE 9",
    ]
    df.reset_index(inplace=True)
    df["level_1"] = df["level_1"].astype(int).astype(str)
    df["Ref"] = df[f"{var}"].replace(
        dict(zip(sorted(df[f"{var}"].unique()), cols_data))
    )

    attentes_columns = df.filter(regex=r"ATTENTE (\d+)").columns.tolist()

    df_long = df.melt(
        id_vars=["Ref", "level_1"],
        value_vars=attentes_columns,
        var_name="Attente",
        value_name="% Réponses",
    )

    Chart = (
        alt.Chart(df_long[df_long["level_1"] == f"{level}"])
        .mark_rect()
        .encode(
            x=alt.X("Ref:N", title=None),
            y=alt.Y("Attente:N", title=None, sort=alt.EncodingSortField(field="% Réponses", order="descending")),
            color=alt.Color("% Réponses:Q", scale=alt.Scale(scheme="spectral")),
            tooltip=["Attente", "Ref", "% Réponses"],
        )
        .properties(
            width=800,
            height=375,
            title={
                "text": f"Classement des attentes des sondés par {var_obj}, niveau {level}",
                "subtitle": f"Source : ARCOM 2024, base 2949 répondants",
                "subtitleColor": "white",
            },
        )
        .interactive()
    )

    return Chart


########################################################################################
@st.cache_data
def Graphe_3d(arcom, var_obj):
    liste_obj, cols_data, var, _ = var_selection(var_obj)

    cols_radio = arcom.filter(regex=r"SOURCES1AR_B1_R_(\d)").columns
    radio = {
        "Radio": [
            "Europe 1",
            "France Bleu",
            "France Inter",
            "RMC",
            "RTL",
            "France info",
            "Radio Classique",
            "France Culture",
            "BFM Business",
            "Sud Radio",
            "RFI",
            "Radio Locale",
            "une autre radio",
            "Rien de tout cela",
        ]
    }
    cols_journaux = arcom.filter(regex=r"SOURCES1BR_B2_R_(\d)").columns
    journaux = {
        "Journaux": [
            "Le Monde",
            "Le Parisien",
            "Le Figaro",
            "Les Echos",
            "L'Equipe",
            "la Croix",
            "Libération",
            "L'Humanité",
            "Mediapart",
            "Huffington Post",
            "Un journal regional",
            "Un journal sortant le dimanche",
            "un joural satirique",
            "Un journal gratuit",
            "Un autre journal",
            "Rien de tout cela",
        ]
    }
    cols_tv = arcom.filter(regex=r"SOURCES1ER_B4_R_(\d)").columns
    tv = {
        "TV": [
            "France Info",
            "LCI",
            "BFM TV",
            "C News",
            "France 24",
            "Chaine d'information internationale (Al Jazeera, CNN, etc.)",
            "Une autre chaine d'information internationale",
            "Rien de tout cela",
        ]
    }

    cols_radio, cols_journaux, cols_tv = (
        cols_radio[:-1],
        cols_journaux[:-1],
        cols_tv[:-1],
    )
    cols_tot = cols_radio.tolist() + cols_journaux.tolist() + cols_tv.tolist()

    dict_glob = radio | journaux | tv

    counts_per_column = defaultdict(dict)

    rows = []

    for item, ref in zip(liste_obj, cols_data):
        for col in cols_tot:
            counts_per_column[ref][col] = {
                f"{source}": {
                    f"{clef}": (arcom[arcom[var] == item][col] == i).sum()
                    for i, clef in enumerate(dict_glob[source], start=1)
                    if clef in dict_glob[source]
                }
                for source in dict_glob.keys()
            }

    rows = []

    for i, tranche in enumerate(counts_per_column.keys(), start=1):
        total_media_type = 0
        for media_type in ["Radio", "Journaux", "TV"]:
            for sous_clef in counts_per_column[tranche]:
                total_media_type = (
                    sum(counts_per_column[tranche][sous_clef][media_type].values())
                    + total_media_type
                )

            rows.append(
                {
                    "Catégorie": tranche,
                    "Type de média": media_type,
                    "Pourcentage": total_media_type,
                }
            )

    df = pd.DataFrame(rows)

    df["Pourcentage"] = df["Pourcentage"] / df.groupby("Catégorie")[
        "Pourcentage"
    ].transform("sum")
    df_large = df.pivot(
        index="Catégorie", columns="Type de média", values="Pourcentage"
    )
    df_large.reset_index(inplace=True)

    fig = px.scatter_3d(
        df_large,
        x="Journaux",
        y="Radio",
        z="TV",
        color="Catégorie",
        size_max=20,
        opacity=0.7,
    )

    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=0),
        xaxis=dict(showgrid=True, gridwidth=2, linewidth=2),
        scene=dict(
            xaxis=dict(
                backgroundcolor="rgba(0, 0, 0,0)",
                gridcolor="white",
                showbackground=True,
                zerolinecolor="white",
            ),
            yaxis=dict(
                backgroundcolor="rgba(0, 0, 0,0)",
                gridcolor="white",
                showbackground=True,
                zerolinecolor="white",
            ),
            zaxis=dict(
                backgroundcolor="rgba(0, 0, 0,0)",
                gridcolor="white",
                showbackground=True,
                zerolinecolor="white",
            ),
        ),
    )
    return fig


########################################################################################


def Graphe_RS(arcom, var_obj):

    _, cols_data, var, _ = var_selection(var_obj)

    sub_df = (
        arcom.groupby(var)
        .apply(
            lambda g: g.filter(regex=r"RSINFO_2_LR_R_(\d)").apply(
                lambda x: x.value_counts()
            )
        )
        .fillna(0)
    )

    sub_df.reset_index(inplace=True)
    sub_df["Ref"] = sub_df[f"{var}"].replace(
        dict(zip(sorted(sub_df[f"{var}"].unique()), cols_data))
    )

    col = [
        "Facebook",
        "Instagram",
        "X",
        "TikTok",
        "Snapchat",
        "LinkedIn",
        "WhatsApp",
        "Telegram",
        "Youtube",
        "Twitch",
        "Reddit",
        "Discord",
        "Autre réseau",
    ]

    df_long = sub_df.melt(
        id_vars=[var, "level_1", "Ref"], var_name="Variable", value_name="Réponses"
    )
    df_long["Variable"] = df_long["Variable"].replace(
        dict(zip(df_long["Variable"].unique(), col))
    )

    df_long["level_1"] = df_long["level_1"].astype(int)

    sorted_df_2 = (
        df_long[df_long["level_1"] == 2]
        .sort_values(by=["Ref", "Réponses"], ascending=[True, False])
        .groupby("Ref")
        .head(5)
    )

    sorted_df_1 = df_long[df_long["level_1"] == 1].merge(
        sorted_df_2[["Ref", "Variable"]], on=["Ref", "Variable"], how="inner"
    )

    sorted_df_1["Réponses Positives"] = sorted_df_1["Réponses"]
    sorted_df_1["Réponses"] = sorted_df_1["Réponses"].abs()

    sorted_df_1["level_1"] = sorted_df_1["level_1"].replace({1: "Non"})
    sorted_df_2["level_1"] = sorted_df_2["level_1"].replace({2: "Oui"})

    sorted_df_1.rename(columns={"level_1": "Utilisation"}, inplace=True)
    sorted_df_2.rename(columns={"level_1": "Utilisation"}, inplace=True)

    y_max_2 = sorted_df_2["Réponses"].max() + 50

    chart_top = (
        alt.Chart(sorted_df_2)
        .mark_bar()
        .encode(
            x=alt.X("Ref:N", title=None, axis=alt.Axis(labelFontSize=14)),
            y=alt.Y("Réponses:Q", title=None, scale=alt.Scale(domain=[0, y_max_2])),
            xOffset="Variable",
            color=alt.Color(
                "Variable", title="Réseau", scale=alt.Scale(scheme="spectral")
            ),
            tooltip=[
                alt.Tooltip("Ref:N", title="Catégorie"),
                alt.Tooltip("Utilisation:N"),
                alt.Tooltip("Variable:N", title="Réseau Social"),
                alt.Tooltip("Réponses:Q", title="Nombre d'utilisations"),
            ],
        )
        .properties(height=355)
    )

    chart_bottom = (
        alt.Chart(sorted_df_1)
        .mark_bar()
        .encode(
            x=alt.X("Ref:N", title=None, axis=alt.Axis(ticks=False, labels=False)),
            y=alt.Y("Réponses:Q", title=None, scale=alt.Scale(domain=[y_max_2, 0])),
            xOffset="Variable",
            color=alt.Color("Variable", title="Réseau"),
            tooltip=[
                alt.Tooltip("Ref:N", title="Catégorie"),
                alt.Tooltip("Utilisation:N"),
                alt.Tooltip("Variable:N", title="Réseau Social"),
                alt.Tooltip("Réponses Positives:Q", title="Nombre d'utilisations"),
            ],
        )
        .properties(height=355)
    )

    final_chart = (
        (chart_top & chart_bottom)
        .configure_view(fill=None, stroke=None)
        .properties(
            title={
                "text": f"Les 5 réseaux sociaux les plus utilisés par {var_obj}",
                "subtitle": "Source ARCOM 2024, base : 2949 répondants",
                "subtitleColor": "white",
            }
        )
    )

    return final_chart


########################################################################################


def Graphe_type_support(data, var_obj):
    _, cols_data, var, _ = var_selection(var_obj)

    format_r = db.query(
        f"""
        SELECT
            CASE
                WHEN FORMAT_R_1 = 1 THEN 'audio_son'
                WHEN FORMAT_R_1 = 2 THEN 'écrit'
                WHEN FORMAT_R_1 = 3 THEN 'vidéos'
                WHEN FORMAT_R_1 = 4 THEN 'photos_images'
                ELSE NULL
            END as format, 
            {var} as REF
        FROM
            data
        """
    ).df()

    format_counts = (
        format_r.groupby("REF")["format"].value_counts(normalize=True).reset_index()
    )
    format_counts.columns = ["REF", "format", "frequency"]
    format_counts["REF"] = format_counts["REF"].replace(
        dict(zip(sorted(format_counts["REF"].unique()), cols_data))
    )

    format_chart = (
        alt.Chart(format_counts)
        .mark_bar()
        .encode(
            x=alt.X(
                "REF:N",
                title="",
                sort="-y",
                # axis=alt.Axis(labelExpr="{'audio_son': 'Audio / Son', 'écrit': 'Écrit', 'vidéos': 'Vidéos', 'photos_images': 'Photos / Images'}[datum.value]", labelAngle=0)
            ),
            y=alt.Y("frequency:Q", title="", axis=alt.Axis(format="%")),
            xOffset="format:N",
            color=alt.Color("format:N", scale=alt.Scale(scheme="spectral")),
            tooltip=[
                "REF",
                alt.Tooltip("format:N", title="Format"),
                alt.Tooltip("frequency:Q", title="Fréquence", format=".2%"),
            ],
        )
        .properties(title="Formats privilégiés pour s'informer", width=600, height=375)
        .configure_view(stroke=None, fill=None)
    )

    return format_chart


########################################################################################


if Choix == "Partie 1 - Analyse des performances des Chaines TV":
    # b1, b2 = st.columns([1, 0.5])
    # with b1:
    #     with st.container(border=True):
    #         st.altair_chart(
    #             Graphe_tranche_Age(Durree_ecoute_age), use_container_width=True
    #         )
    # with b2:
    #     with st.container(border=True):
    #         st.write(
    #             "Cette étude vise à mettre en lumière le rapport qu'on les francais à l'information."
    #         )
    with st.container(border=True):
            st.altair_chart(
                Graphe_tranche_Age(Durree_ecoute_age), use_container_width=True
            )

    a1, a2, a3 = st.columns([1, 1, 1])
    with a1:
        with st.container(border=True):
            st.altair_chart(
                Graphe_mots_clefs(ina, Var_ref_1, Var_ref_2, gr_1_select, gr_1_mult),
                use_container_width=True,
            )

    with a2:
        with st.container(border=True):
            st.altair_chart(
                Graphe_prog_tv_audience(Prog_TV, Var_select_prog),
                use_container_width=True,
            )

    with a3:
        with st.container(border=True):
            if Var_ref_1 == "Theme":
                st.altair_chart(
                    Graphe_audience(Part_audience_long, gr_1_mult),
                    use_container_width=True,
                )


if Choix == "Partie 2 - Analyse du rapports des français à l'information":
    if selection == "Vue générale":
        Introduction()

    elif selection == "Fiabilité des sources":
        fiabilité_info()

        d1, d2 = st.columns([1, 1])

        with d1:
            with st.container(border=True):
                st.altair_chart(
                    Graphe_nb_sources(arcom),
                    use_container_width=True,
                )
                # st.altair_chart(
                #     Graphe_conf_niv(arcom),
                #     use_container_width=True,
                # )

        with d2:
            with st.container(border=True):
                st.altair_chart(
                    Graphe_inf_fiable(arcom, var_obj),
                    use_container_width=True,
                )

    if selection == "Attentes des sondés":
        a1, a2, a3 = st.columns([0.65, 0.80, 1])
        with a1:
            with st.container(border=True):
                st.altair_chart(
                    Graphe_repartition_répondants(arcom, var_obj),
                    use_container_width=True,
                )

        with a2:
            with st.container(border=True):
                st.altair_chart(
                    Graphe_pref_algo(arcom, var_obj),
                    use_container_width=True,
                )

        with a3:
            with st.container(border=True):
                st.altair_chart(
                    Graphe_type_support(arcom, var_obj),
                    use_container_width=True,
                )

        with st.container(border=True):
            o1, o2, o3 = st.columns([1, 1, 1])

            with o1:
                # with st.container(border=True):
                st.altair_chart(
                    Graphe_attentes(arcom, var_obj, 1),
                    use_container_width=True,
                )
            with o2:
                # with st.container(border=True):
                st.altair_chart(
                    Graphe_attentes(arcom, var_obj, 2),
                    use_container_width=True,
                )
            with o3:
                # with st.container(border=True):
                st.altair_chart(
                    Graphe_attentes(arcom, var_obj, 3),
                    use_container_width=True,
                )

            with st.expander("Informations liées aux attentes"):
                cols = [
                    "Le niveau indique le classsement (indispensable, important, pas important) de ce qu'attendent les sondés des journalistes",
                    "ATTENTE 1 : Sélectionner et hiérarchiser les informations les plus importantes",
                    "ATTENTE 2 : Fournir des informations fiables et vérifiées",
                    "ATTENTE 3 : Révéler les grands scandales politiques ou financiers",
                    "ATTENTE 4 : Rester neutres en toutes circonstances",
                    "ATTENTE 5 : Donner la parole à tout le monde y compris les minorités",
                    "ATTENTE 6 : Permettre que tous les points de vue s'expriment librement",
                    "ATTENTE 7 : Détecter les fausses nouvelles et lutter contre leur propagation",
                    "ATTENTE 8 : Apporter des solutions aux différents problèmes",
                    "ATTENTE 9 : Expliquer comment ils choisissent et fabriquent les informations",
                ]

                col1_items = "\n".join(
                    [f"<li>{cols[i]}</li>" for i in range(0, len(cols) // 2)]
                )
                col2_items = "\n".join(
                    [f"<li>{cols[i]}</li>" for i in range(len(cols) // 2, len(cols))]
                )

                st.markdown(
                    f"""
                <div style="display: flex;">
                    <div style="flex: 1; padding-right: 20px;">
                        <ul>{col1_items}</ul>
                    </div>
                    <div style="flex: 1; padding-left: 20px;">
                        <ul>{col2_items}</ul>
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

    elif selection == "Analyse complémentaire":
        c1, c2 = st.columns([0.80, 1])

        with c1:
            with st.container(border=True):
                st.altair_chart(
                    Graphe_RS(arcom, var_obj),
                    use_container_width=True,
                )

        with c2:
            with st.container(border=True):
                st.altair_chart(
                    Graphe_motivations_RS(arcom, var_obj),
                    use_container_width=True,
                )

            with st.container(border=True):
                st.altair_chart(
                    Graphe_point_algo(arcom),
                    use_container_width=True,
                )

        b1, b2, b3, b4 = st.columns([1, 1, 1, 1])
        with b1:
                with st.container(border=True):
                    st.altair_chart(
                        Graphe_motivations(arcom, var_obj, 1),
                        use_container_width=True,
                    )

        with b2:
                with st.container(border=True):
                    st.altair_chart(
                        Graphe_motivations(arcom, var_obj, 2),
                        use_container_width=True,
                    )

        with b3:
                with st.container(border=True):
                    st.altair_chart(
                        Graphe_motivations(arcom, var_obj, 3),
                        use_container_width=True,
                    )

        with b4:
                with st.container(border=True):
                    st.altair_chart(
                        Graphe_motivations(arcom, var_obj, 4),
                        use_container_width=True,
                    )

        with st.expander("Informations liées aux attentes"):
                cols = [
                        "Le niveau indique le classsement des motivations à s'informer des sondés, niveau 1 étant le plus important et niveau 4 le moins important",
                        "MOTIV 1 : Comprendre le monde qui m'entoure",
                        "MOTIV 2 : Rester informé des grands événements",
                        "MOTIV 3 : Me faire ma propre opinion",
                        "MOTIV 4 : Prendre des décisions éclairées",
                        "MOTIV 5 : Pouvoir en discuter avec mon entourage",
                        "MOTIV 6 : Me divertir",
                        "MOTIV 7 : Découvrir des nouvelles tendances ou cultures",
                        "MOTIV 8 : Satisfaire ma curiosité",
                        "MOTIV 9 : Passer le temps",
                        "MOTIV 10 : M'instruir, me cultiver",
                        "MOTIV 11 : Progresser dans mon travail ou mes études",
                        "MOTIV 12 : Connaitre d'autres avis que le mien", 
                        "MOTIV 13 : Par habitude",
                        "MOTIV 14 : Aucun"
                    ]

                col1_items = "\n".join(
                        [f"<li>{cols[i]}</li>" for i in range(0, len(cols) // 2)]
                    )
                col2_items = "\n".join(
                        [f"<li>{cols[i]}</li>" for i in range(len(cols) // 2, len(cols))]
                    )

                st.markdown(
                        f"""
                    <div style="display: flex;">
                        <div style="flex: 1; padding-right: 20px;">
                            <ul>{col1_items}</ul>
                        </div>
                        <div style="flex: 1; padding-left: 20px;">
                            <ul>{col2_items}</ul>
                        </div>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )
        if st.sidebar.checkbox("Résultats supplémentaires"):
            var_source = st.sidebar.radio(
                "Choix de la variable d'analyse",
                ["Radio", "Presse écrite", "Chaines TV spécialisées"],
            )

            textes = [
                "Qui a récemment attaqué Israël ?",
                "Comment s'appelle le premier ministre anglais ?",
                "Quand se termine le mandat d'Emmanuel Macron ?",
                "Quelle était en moyenne le taux d'inflation en France en 2023 ?",
            ]
            st.sidebar.markdown("#### * Questions posées dans le quizz :")
            st.sidebar.markdown("\n".join([f"- {text}" for text in textes]))
            st.sidebar.markdown("#### ** Opinions testées :")
            st.sidebar.markdown(
                "- Abscisse : Je pense que les infos partagées par les citoyens sont aussi importantes que celles des journalistes (1) -> L'information est un métier, celui des journalistes (6) \n \n"
                "- Ordonnée : Je vais cherhcer l'information de facon volontaire (1) -> L'information vient à moi sans que je la recherche (6)"
            )


            liste_obj, _, _, _ = var_selection(var_obj)
            num_columns = 3
            charts = Graphe_Opinions_info(arcom, var_obj)
            for i in range(0, len(charts), num_columns):
                columns = st.columns(num_columns)
                for j, chart in enumerate(charts[i : i + num_columns]):
                    with columns[j]:
                        with st.container(border=True):
                            st.altair_chart(chart, use_container_width=True)

            with st.container(border=True):
                st.altair_chart(
                    Graph_quizz_age(arcom, var_obj),
                    use_container_width=True,
                )

            with st.container(border=True):
                st.altair_chart(
                    Graphe_type_source(arcom, var_source, var_obj),
                    use_container_width=True,
                )
