import time
import random
import streamlit as st
import pandas as pd
from datetime import date
from google.oauth2 import service_account
import gspread
import plotly.express as px

# 1. Configuration de la page
st.set_page_config(page_title="Hydratation", page_icon="💧", layout="centered")

# --- INITIALISATION DE LA SESSION ---
if "utilisateur_actif" not in st.session_state:
    st.session_state["utilisateur_actif"] = None

# --- CONNEXION SÉCURISÉE À GOOGLE SHEETS (NATIVE TOML) ---
# Streamlit transforme directement le bloc [connections.gsheets.service_account] en dictionnaire Python
creds_json = dict(st.secrets["connections"]["gsheets"]["service_account"])
spreadsheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = service_account.Credentials.from_service_account_info(creds_json, scopes=scopes)
gc = gspread.authorize(creds)

def charger_donnees():
    try:
        sh = gc.open_by_url(spreadsheet_url)
        worksheet = sh.get_worksheet(0)
        records = worksheet.get_all_records()
        df = pd.DataFrame(records)
        if df.empty or "Date" not in df.columns or "Utilisateur" not in df.columns or "Verres" not in df.columns:
            df = pd.DataFrame(columns=["Date", "Utilisateur", "Verres"])
        return df
    except Exception as e:
        st.error(f"Erreur de lecture : {type(e).__name__} - {e}")
        return pd.DataFrame(columns=["Date", "Utilisateur", "Verres"])

def sauvegarder_donnees(df):
    try:
        sh = gc.open_by_url(spreadsheet_url)
        worksheet = sh.get_worksheet(0)
        worksheet.clear()
        data_to_write = [df.columns.values.tolist()] + df.values.tolist()
        worksheet.update(values=data_to_write, range_name="A1")
    except Exception as e:
        st.error(f"Erreur d'écriture : {type(e).__name__} - {e}")

utilisateurs = ["Amélie", "Iulia", "Ethan", "Sarah"]

# --- ÉCRAN DE SÉLECTION DU PROFIL (Si aucun profil n'est sélectionné) ---
if st.session_state["utilisateur_actif"] is None:
    st.title("💧 Bienvenue sur Hydratation accompagnée par Dembouz !")
    st.write("### Qui est là aujourd'hui ?")
    st.write("Sélectionne ton prénom pour accéder à ton compteur :")
    
    # Création de boutons bien visibles pour chaque utilisateur
    for user in utilisateurs:
        if st.button(f"👤 Je suis {user}", use_container_width=True):
            st.session_state["utilisateur_actif"] = user
            st.rerun()

# --- SI UN PROFIL EST SÉLECTIONNÉ : AFFICHAGE DE L'APPLICATION ---
else:
    # --- BARRE LATÉRALE ---
    st.sidebar.title("👤 Profil & Date 📅")

    # Synchronisation du menu déroulant avec la session
    index_defaut = utilisateurs.index(st.session_state["utilisateur_actif"]) if st.session_state["utilisateur_actif"] in utilisateurs else 0
    
    utilisateur_selectionne = st.sidebar.selectbox(
        "Qui me regarde ?", 
        utilisateurs, 
        index=index_defaut
    )
    
    # Si l'utilisateur change le prénom dans le menu déroulant, on met à jour la session
    if utilisateur_selectionne != st.session_state["utilisateur_actif"]:
        st.session_state["utilisateur_actif"] = utilisateur_selectionne
        st.rerun()

    utilisateur_actif = st.session_state["utilisateur_actif"]

    # Choix de la date (par défaut : aujourd'hui)
    date_selectionnee = st.sidebar.date_input("Date à modifier / consulter", date.today())
    date_str = str(date_selectionnee)

    if date_selectionnee != date.today():
        st.sidebar.info(f"📅 Modification de la journée du **{date_selectionnee.strftime('%d/%m/%Y')}**")

    # Bouton pour se déconnecter ou retourner à l'accueil
    if st.sidebar.button("🚪 Changer d'utilisateur"):
        st.session_state["utilisateur_actif"] = None
        st.rerun()

    # --- LOGIQUE DE L'APPLICATION ---
    df_historique = charger_donnees()
    df_historique["Date"] = df_historique["Date"].astype(str)
    df_historique["Utilisateur"] = df_historique["Utilisateur"].astype(str)

    masque = (df_historique["Date"] == date_str) & (df_historique["Utilisateur"] == utilisateur_actif)

    if masque.any():
        idx = df_historique[masque].index[0]
        nb_verres = int(df_historique.loc[idx, "Verres"])
    else:
        nouveau_jour = pd.DataFrame([{"Date": date_str, "Utilisateur": utilisateur_actif, "Verres": 0}])
        df_historique = pd.concat([df_historique, nouveau_jour], ignore_index=True)
        sauvegarder_donnees(df_historique)
        idx = df_historique[(df_historique["Date"] == date_str) & (df_historique["Utilisateur"] == utilisateur_actif)].index[0]
        nb_verres = 0

    # SONS DES POP-UPS
    sons_petite_victoire = ["Children Yay Sound Effect HD.mp3", "30 ans y en aura plus.mp3"]
    sons_retour_zero = ["Tuveuxretournerendis.m4a", "Muymuy.m4a"]
    sons_8verres = ["Alors_ces_F50_Mr_Dembele_foot_128kbps_1247649_cut.mp3", "Triple.mp3"]
    
    # --- POP-UPS ---
    @st.dialog("GG champion ! 🎉")
    def afficher_pop_up_gif():
        st.write(f"{utilisateur_actif}, tu viens de boire un verre d'eau ! 💦")
        st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYTMyam80ZWZ5Njgzenh0amxsMWMwcW50ejF5bmF2cHo5bDdoNWU2dyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/TKJtXbgD1RlGHGJiXi/giphy.gif", width=300)
        st.audio(random.choice(sons_petite_victoire), autoplay=True)
        time.sleep(5)
        st.rerun()

    @st.dialog("Ohh lala...")
    def afficher_pop_up_gif2():
        st.write("Tu confonds ta droite et ta gauche ?")
        st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYTMyam80ZWZ5Njgzenh0amxsMWMwcW50ejF5bmF2cHo5bDdoNWU2dyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/gtWPqMuppPgrQb25Oi/giphy.gif", width=300)
        st.audio("QUAND DEMBÉLÉ NE C’EST PAS SI IL EST DROITIER OU GAUCHER.mp3", autoplay=True)
        time.sleep(15)
        st.rerun()

    @st.dialog("Ah tu veux retourner en District ? ")
    def afficher_pop_up_gif3():
        st.write("Muy, Muy,... So bad, So bad !")
        st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYTMyam80ZWZ5Njgzenh0amxsMWMwcW50ejF5bmF2cHo5bDdoNWU2dyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/joI9gJHWuZHed9UOqp/giphy.gif", width=300)
        st.audio(random.choice(sons_retour_zero), autoplay=True)
        time.sleep(4)
        st.rerun()

    @st.dialog("FIUMMMM, ZOOMM")
    def afficher_pop_up_gif4():
        st.write("Tiplé ou rien ! 💦")
        st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYTMyam80ZWZ5Njgzenh0amxsMWMwcW50ejF5bmF2cHo5bDdoNWU2dyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/OGkI5rcORf66tBQBB7/giphy.gif", width=300)
        st.audio(random.choice(sons_8verres), autoplay=True)
        time.sleep(3)
        st.rerun()

    # --- STRUCTURE DE L'APPLICATION AVEC ONGLETS ---
    tab_saisie, tab_dashboard = st.tabs(["💧 Compteur", "📊 Statistiques & Tendances"])

    # --- ONGLET 1 : SAISIE DES VERRES ---
    with tab_saisie:
        if date_selectionnee == date.today():
            st.title(f"💧 Compteur d'Eau de {utilisateur_actif}")
        else:
            st.title(f"📅 Historique du {date_selectionnee.strftime('%d/%m/%Y')} ({utilisateur_actif})")

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

        libelle_metric = "Verres bus aujourd'hui" if date_selectionnee == date.today() else f"Verres bus le {date_selectionnee.strftime('%d/%m/%Y')}"

        st.metric(
            label=f"{libelle_metric} par {utilisateur_actif}", 
            value=f"{nb_verres} / 8", 
            delta=f"{max(0, 8 - nb_verres)} restants",
            delta_color="inverse"
        )

        if nb_verres >= 8:
            st.balloons()
            time.sleep(2)
            afficher_pop_up_gif4()

        progression = min(nb_verres / 8, 1.0)
        st.progress(progression)

    # --- ONGLET 2 : DASHBOARD / STATISTIQUES ---
    with tab_dashboard:
        st.title(f"📊 Dashboard de {utilisateur_actif}")
        
        df_user = df_historique[df_historique["Utilisateur"] == utilisateur_actif].copy()
        
        if df_user.empty:
            st.info("Aucune donnée disponible pour le moment.")
        else:
            df_user["Date"] = pd.to_datetime(df_user["Date"])
            df_user = df_user.sort_values("Date")
            
            st.subheader("📈 Évolution de la consommation")
            fig_line = px.line(
                df_user, 
                x="Date", 
                y="Verres", 
                markers=True,
                title=f"Nombre de verres bus par jour ({utilisateur_actif})",
                labels={"Verres": "Nombre de verres", "Date": "Date"}
            )
            fig_line.add_hline(y=8, line_dash="dot", line_color="green", annotation_text="Objectif (8 verres/2L)")
            st.plotly_chart(fig_line, use_container_width=True)
            
            st.write("---")
            
            st.subheader("✔ Réussite de l'objectif (8 verres/2L par jour)")
            df_user["Statut"] = df_user["Verres"].apply(lambda x: "Objectif atteint 🎉" if x >= 8 else "Sous l'objectif ❌")
            
            fig_pie = px.pie(
                df_user, 
                names="Statut", 
                title="Proportion de jours avec objectif atteint",
                color="Statut",
                color_discrete_map={"Objectif atteint 🎉": "#2ECC71", "Sous l'objectif ❌": "#E74C3C"},
                hole=0.4
            )
            st.plotly_chart(fig_pie, use_container_width=True)