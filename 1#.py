import time
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date
import base64
import json

# 1. Configuration de la page (obligatoirement en tout premier avant le reste du code Streamlit)
st.set_page_config(page_title="Hydratation", page_icon="💧", layout="centered")

# --- CONNEXION SÉCURISÉE À GOOGLE SHEETS ---

# 1. On récupère la clé Base64 depuis les secrets
creds_b64 = st.secrets["connections"]["gsheets"]["gcs_json_base64"]

# 2. On la décode pour recréer le dictionnaire de connexion
creds_json = json.loads(base64.b64decode(creds_b64).decode("utf-8"))

# 3. On extrait l'URL du tableur
spreadsheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]

# 4. On appelle la connexion en lui injectant directement les paramètres décodés
conn = st.connection(
    "gsheets", 
    type=GSheetsConnection, 
    spreadsheet=spreadsheet_url, 
    **creds_json
)

# Fonction pour lire les données du Google Sheet
def charger_donnees():
    try:
        # On lit la feuille de calcul
        df = conn.read(ttl="0") # ttl="0" pour forcer la mise à jour immédiate à chaque lecture
        return df
    except Exception:
        # Si le tableau est vide, on renvoie un DataFrame de base
        return pd.DataFrame(columns=["Date", "Verres"])

# Fonction pour sauvegarder les données
def sauvegarder_donnees(df):
    # On met à jour le Google Sheet avec notre nouveau tableau
    conn.update(data=df)

# --- LOGIQUE DE L'APPLICATION ---

# Charger les données actuelles
df_historique = charger_donnees()

# S'assurer que les dates sont bien lues comme du texte pour éviter les bugs
df_historique["Date"] = df_historique["Date"].astype(str)

aujourdhui = str(date.today())

# Vérifier si aujourd'hui existe déjà dans notre tableau
if aujourdhui in df_historique["Date"].values:
    # Récupérer l'index de la ligne d'aujourd'hui
    idx = df_historique[df_historique["Date"] == aujourdhui].index[0]
    nb_verres = int(df_historique.loc[idx, "Verres"])
else:
    # Si la ligne n'existe pas, on l'ajoute avec 0 verre
    nouveau_jour = pd.DataFrame([{"Date": aujourdhui, "Verres": 0}])
    df_historique = pd.concat([df_historique, nouveau_jour], ignore_index=True)
    sauvegarder_donnees(df_historique)
    nb_verres = 0
    idx = df_historique[df_historique["Date"] == aujourdhui].index[0]

# --- POP-UPS ---

@st.dialog("GG champion ! 🎉")
def afficher_pop_up_gif():
    st.write("Tu viens de boire un verre et de l'eau ! 💦")
    st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYTMyam80ZWZ5Njgzenh0amxsMWMwcW50ejF5bmF2cHo5bDdoNWU2dyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/TKJtXbgD1RlGHGJiXi/giphy.gif", width=300)
    time.sleep(3) # Attend 3 secondes
    st.rerun()    # Relance l'application, ce qui ferme automatiquement le pop-up !

@st.dialog("Ohh lala...")
def afficher_pop_up_gif2():
    st.write("Tu confonds ta droite et ta gauche ?")
    st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYTMyam80ZWZ5Njgzenh0amxsMWMwcW50ejF5bmF2cHo5bDdoNWU2dyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/gtWPqMuppPgrQb25Oi/giphy.gif", width=300)
    time.sleep(3)
    st.rerun()

@st.dialog("Ah tu veux retourner en District ? ")
def afficher_pop_up_gif3():
    st.write("Muy, Muy,... So bad, So bad !")
    st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYTMyam80ZWZ5Njgzenh0amxsMWMwcW50ejF5bmF2cHo5bDdoNWU2dyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/joI9gJHWuZHed9UOqp/giphy.gif", width=300)
    time.sleep(3)
    st.rerun()

@st.dialog("FIUMMMM, ZOOMM")
def afficher_pop_up_gif4():
    st.write("Tiplé ou rien ! 💦")
    st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYTMyam80ZWZ5Njgzenh0amxsMWMwcW50ejF5bmF2cHo5bDdoNWU2dyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/OGkI5rcORf66tBQBB7/giphy.gif", width=300)
    time.sleep(3)
    st.rerun()

# --- INTERFACE UTILISATEUR ---

st.title("💧 Mon Compteur d'Eau")

# Organiser les boutons côte à côte avec des colonnes
col1, col2 = st.columns(2)

with col1:
    if st.button("➕ J'ai bu un verre", use_container_width=True):
        df_historique.loc[idx, "Verres"] = nb_verres + 1
        sauvegarder_donnees(df_historique)
        afficher_pop_up_gif()
        
    if st.button("🔄 Zéro", use_container_width=True):
        df_historique.loc[idx, "Verres"] = 0
        sauvegarder_donnees(df_historique)
        afficher_pop_up_gif3()

with col2:
    if st.button("➖ Oups un de trop", use_container_width=True):
        if nb_verres > 0:
            df_historique.loc[idx, "Verres"] = nb_verres - 1
            sauvegarder_donnees(df_historique)
            afficher_pop_up_gif2()

st.write("---") # Ligne de séparation

# Un affichage stylé façon "Tableau de bord" connecté au Google Sheet
st.metric(
    label="Verres bus aujourd'hui", 
    value=f"{nb_verres} / 8", 
    delta=f"{max(0, 8 - nb_verres)} restants",
    delta_color="inverse"
)

# Déclenchement de l'objectif atteint (8 verres ou plus)
if nb_verres >= 8:
    st.balloons()  # Fait tomber des ballons si l'objectif est atteint
    time.sleep(2)  # Attend 2 secondes
    afficher_pop_up_gif4()

# Barre de progression visuelle
progression = min(nb_verres / 8, 1.0)
st.progress(progression)