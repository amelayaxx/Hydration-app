import time
import streamlit as st
import pandas as pd
from datetime import date
import base64
import json
from google.oauth2 import service_account
import gspread

# 1. Configuration de la page (obligatoirement en tout premier)
st.set_page_config(page_title="Hydratation", page_icon="💧", layout="centered")

# --- CONNEXION SÉCURISÉE À GOOGLE SHEETS ---

# 1. On récupère la clé Base64 depuis les secrets
creds_b64 = st.secrets["connections"]["gsheets"]["gcs_json_base64"]

# 2. On la décode pour recréer le dictionnaire de connexion
creds_json = json.loads(base64.b64decode(creds_b64).decode("utf-8"))

# 3. On extrait l'URL du tableur
spreadsheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]

# 4. On crée les credentials Google et on initialise le client gspread
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = service_account.Credentials.from_service_account_info(creds_json, scopes=scopes)
gc = gspread.authorize(creds)

# Fonction pour lire les données du Google Sheet
def charger_donnees():
    try:
        sh = gc.open_by_url(spreadsheet_url)
        worksheet = sh.get_worksheet(0)
        records = worksheet.get_all_records()
        df = pd.DataFrame(records)
        
        # SÉCURITÉ : Vérification de la présence de la nouvelle colonne "Utilisateur"
        if df.empty or "Date" not in df.columns or "Utilisateur" not in df.columns or "Verres" not in df.columns:
            df = pd.DataFrame(columns=["Date", "Utilisateur", "Verres"])
            
        return df
    except Exception as e:
        st.error(f"Erreur de lecture : {type(e).__name__} - {e}")
        return pd.DataFrame(columns=["Date", "Utilisateur", "Verres"])

# Fonction pour sauvegarder les données
def sauvegarder_donnees(df):
    try:
        sh = gc.open_by_url(spreadsheet_url)
        worksheet = sh.get_worksheet(0)
        # On vide la feuille actuelle
        worksheet.clear()
        # On prépare les données (en-têtes + lignes)
        data_to_write = [df.columns.values.tolist()] + df.values.tolist()
        worksheet.update(values=data_to_write, range_name="A1")
    except Exception as e:
        st.error(f"Erreur d'écriture : {type(e).__name__} - {e}")

# --- SELECTION DE L'UTILISATEUR ---

# Liste des utilisateurs
utilisateurs = ["Amélie", "Iulia"]

st.sidebar.title("👤 Profil")
utilisateur_actif = st.sidebar.selectbox("Qui utilise l'application ?", utilisateurs)

# --- LOGIQUE DE L'APPLICATION ---

# Charger les données actuelles
df_historique = charger_donnees()

# S'assurer que les dates et utilisateurs sont bien lus comme du texte
df_historique["Date"] = df_historique["Date"].astype(str)
df_historique["Utilisateur"] = df_historique["Utilisateur"].astype(str)

aujourdhui = str(date.today())

# Filtre pour chercher la ligne de l'utilisateur pour aujourd'hui
masque = (df_historique["Date"] == aujourdhui) & (df_historique["Utilisateur"] == utilisateur_actif)

if masque.any():
    # Récupérer l'index de la ligne existante pour cet utilisateur aujourd'hui
    idx = df_historique[masque].index[0]
    nb_verres = int(df_historique.loc[idx, "Verres"])
else:
    # Si la ligne n'existe pas pour cet utilisateur aujourd'hui, on la crée
    nouveau_jour = pd.DataFrame([{"Date": aujourdhui, "Utilisateur": utilisateur_actif, "Verres": 0}])
    df_historique = pd.concat([df_historique, nouveau_jour], ignore_index=True)
    sauvegarder_donnees(df_historique)
    
    # Récupérer le nouvel index créé
    idx = df_historique[(df_historique["Date"] == aujourdhui) & (df_historique["Utilisateur"] == utilisateur_actif)].index[0]
    nb_verres = 0

# --- POP-UPS ---

@st.dialog("GG champion ! 🎉")
def afficher_pop_up_gif():
    st.write(f"{utilisateur_actif}, tu viens de boire un verre d'eau ! 💦")
    st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYTMyam80ZWZ5Njgzenh0amxsMWMwcW50ejF5bmF2cHo5bDdoNWU2dyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/TKJtXbgD1RlGHGJiXi/giphy.gif", width=300)
    time.sleep(3)
    st.rerun()

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

st.title(f"💧 Compteur d'Eau de {utilisateur_actif}")

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

st.write("---")

# Un affichage stylé connecté au Google Sheet
st.metric(
    label=f"Verres bus aujourd'hui par {utilisateur_actif}", 
    value=f"{nb_verres} / 8", 
    delta=f"{max(0, 8 - nb_verres)} restants",
    delta_color="inverse"
)

# Déclenchement de l'objectif atteint (8 verres ou plus)
if nb_verres >= 8:
    st.balloons()
    time.sleep(2)
    afficher_pop_up_gif4()

# Barre de progression visuelle
progression = min(nb_verres / 8, 1.0)
st.progress(progression)