import time

import streamlit as st

import json
import os
from datetime import date

# Nom du fichier de sauvegarde
DATA_FILE = "suivi_eau.json"

# --- FONCTIONS DE PERSISTANCE ---

def charger_donnees():
    """Charge les données depuis le fichier JSON. Si le fichier n'existe pas, retourne un dictionnaire vide."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def sauvegarder_donnees(donnees):
    """Sauvegarde les données dans le fichier JSON."""
    with open(DATA_FILE, "w") as f:
        json.dump(donnees, f, indent=4)

# --- INITIALISATION ---

# Récupérer la date du jour au format texte (ex: "2026-07-15")
aujourdhui = str(date.today())

# Charger tout l'historique
historique = charger_donnees()

# Si aujourd'hui n'est pas encore enregistré, on commence à 0 verre
if aujourdhui not in historique:
    historique[aujourdhui] = 0
    sauvegarder_donnees(historique)

# 1. On définit la fonction qui va afficher le pop-up
@st.dialog("GG champion ! 🎉")
def afficher_pop_up_gif():
    st.write("Tu viens de boire un verre et de l'eau ! 💦")
    # Met ton GIF ici (il sera centré dans le pop-up)
    st.image ("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYTMyam80ZWZ5Njgzenh0amxsMWMwcW50ejF5bmF2cHo5bDdoNWU2dyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/TKJtXbgD1RlGHGJiXi/giphy.gif", width=300)
    time.sleep(3) # Attend 3 secondes
    st.rerun()    # Relance l'application, ce qui ferme automatiquement le pop-up !

@st.dialog("Ohh lala...")
def afficher_pop_up_gif2():
    st.write("Tu confonds ta droite et ta gauche ?")
    st.image ("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYTMyam80ZWZ5Njgzenh0amxsMWMwcW50ejF5bmF2cHo5bDdoNWU2dyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/gtWPqMuppPgrQb25Oi/giphy.gif", width=300)
    time.sleep(3)
    st.rerun()

@st.dialog("Ah tu veux retourner en District ? ")
def afficher_pop_up_gif3():
    st.write("Muy, Muy,... So bad, So bad !")
    st.image ("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYTMyam80ZWZ5Njgzenh0amxsMWMwcW50ejF5bmF2cHo5bDdoNWU2dyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/joI9gJHWuZHed9UOqp/giphy.gif", width=300)
    time.sleep(3)
    st.rerun()

@st.dialog("FIUMMMM, ZOOMM")
def afficher_pop_up_gif4():
    st.write("Tiplé ou rien ! 💦")
    st.image ("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYTMyam80ZWZ5Njgzenh0amxsMWMwcW50ejF5bmF2cHo5bDdoNWU2dyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/OGkI5rcORf66tBQBB7/giphy.gif", width=300)
    time.sleep(3)
    st.rerun()

# 1. Configuration de la page (titre dans l'onglet et icone)
st.set_page_config(page_title="Hydratation", page_icon="💧", layout="centered")

st.title("💧 Mon Compteur d'Eau")

# 2. Ajouter une image (tu peux mettre un lien ou le nom d'un fichier sur ton PC)
# st.image("https://images.unsplash.com/photo-1548839140-29a749e1bc4e", width=300)

# Initialisation du compteur en mémoire
if 'verres' not in st.session_state:
    st.session_state.verres = 0

# 3. Organiser les boutons côte à côte avec des colonnes
col1, col2 = st.columns(2)

with col1:
    # Le paramètre use_container_width permet au bouton de prendre toute la largeur de la colonne
    if st.button("➕ J'ai bu un verre", use_container_width=True):
        st.session_state.verres += 1
        afficher_pop_up_gif()
    if st.button("🔄 Zéro", use_container_width=True):
        st.session_state.verres = 0
        afficher_pop_up_gif3()


with col2:
    if st.button("➖ Oups un de trop", use_container_width=True):
         st.session_state.verres -= 1
         afficher_pop_up_gif2()

st.write("---") # Ajoute une ligne de séparation visuelle

# 4. Un affichage stylé façon "Tableau de bord"
st.metric(
    label="Verres bus aujourd'hui", 
    value=f"{st.session_state.verres} / 8", 
    delta=f"{8 - st.session_state.verres} restants",
    delta_color="inverse" # Met le delta en rouge s'il est positif, vert si négatif
)
if value := st.session_state.verres >= 8:
    st.balloons()  # Fait tomber des ballons si l'objectif est atteint
    time.sleep(2)  # Attend 2 secondes avant de continuer
    afficher_pop_up_gif4()
# 5. Ajouter une barre de progression visuelle
# Le calcul évite que la barre dépasse 100% (1.0) si tu bois plus de 8 verres
progression = min(st.session_state.verres / 8, 1.0)
st.progress(progression)