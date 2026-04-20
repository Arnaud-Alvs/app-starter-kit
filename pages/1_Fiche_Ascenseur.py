import streamlit as st
import plotly.graph_objects as go
from data import charger_donnees, badge_statut, couleur_statut

st.set_page_config(page_title="Fiche ascenseur", page_icon="🛗", layout="wide")

st.markdown("""
<style>
.info-block { background:white; border-radius:10px; padding:16px 20px;
              box-shadow:0 1px 4px rgba(0,0,0,.08); margin-bottom:12px; }
.info-label { font-size:.8rem; color:#6B7280; margin:0; }
.info-value { font-size:1.05rem; font-weight:600; margin:0; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def get_data():
    return charger_donnees()


df = get_data()

st.title("Fiche ascenseur")

asc_id = st.selectbox("Sélectionner un ascenseur", options=df["ID"].tolist())
row = df[df["ID"] == asc_id].iloc[0]

st.markdown(f"### {row['ID']} — {row['Bâtiment']}")
st.markdown(badge_statut(row["Statut"]), unsafe_allow_html=True)
st.divider()

col1, col2, col3 = st.columns(3)

def info(label, value, col):
    col.markdown(f'<div class="info-block"><p class="info-label">{label}</p><p class="info-value">{value}</p></div>',
                 unsafe_allow_html=True)

info("Marque", row["Marque"], col1)
info("Modèle", row["Modèle"], col1)
info("Type", row["Type"], col1)
info("Année de fabrication", f"{row['Année de fabrication']} ({row['Âge (ans)']} ans)", col1)

info("Étages desservis", row["Étages desservis"], col2)
info("Capacité", f"{row['Capacité (kg)']} kg", col2)
info("Technicien responsable", row["Technicien responsable"], col2)
info("Incidents (12 mois)", row["Incidents (12 mois)"], col2)

info("Dernière maintenance", row["Dernière maintenance"].strftime("%d/%m/%Y"), col3)
info("Prochaine maintenance", row["Prochaine maintenance"].strftime("%d/%m/%Y"), col3)
jours = row["Jours avant maintenance"]
msg = f"En retard de {abs(jours)} jours" if jours < 0 else f"Dans {jours} jours"
info("Délai maintenance", msg, col3)

st.divider()

# Gauge incidents
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("Niveau d'incidents (12 mois)")
    incidents = row["Incidents (12 mois)"]
    color = "#22C55E" if incidents <= 2 else "#F59E0B" if incidents <= 5 else "#EF4444"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=incidents,
        gauge={
            "axis": {"range": [0, 10]},
            "bar": {"color": color},
            "steps": [
                {"range": [0, 3], "color": "#DCFCE7"},
                {"range": [3, 6], "color": "#FEF3C7"},
                {"range": [6, 10], "color": "#FEE2E2"},
            ],
        },
        title={"text": "Incidents"},
    ))
    fig.update_layout(margin=dict(t=30, b=10, l=20, r=20), height=250)
    st.plotly_chart(fig, use_container_width=True)

with col_g2:
    st.subheader("Âge de l'appareil")
    age = row["Âge (ans)"]
    color_age = "#22C55E" if age <= 10 else "#F59E0B" if age <= 25 else "#EF4444"
    fig2 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=age,
        number={"suffix": " ans"},
        gauge={
            "axis": {"range": [0, 50]},
            "bar": {"color": color_age},
            "steps": [
                {"range": [0, 10], "color": "#DCFCE7"},
                {"range": [10, 25], "color": "#FEF3C7"},
                {"range": [25, 50], "color": "#FEE2E2"},
            ],
        },
        title={"text": "Âge"},
    ))
    fig2.update_layout(margin=dict(t=30, b=10, l=20, r=20), height=250)
    st.plotly_chart(fig2, use_container_width=True)

st.divider()
st.subheader("Historique de maintenance simulé")

import pandas as pd
import random
random.seed(hash(asc_id) % 1000)
historique = []
base = row["Dernière maintenance"]
for k in range(6):
    d = base - pd.Timedelta(days=k * 180 + random.randint(-15, 15))
    types_op = ["Révision générale", "Remplacement câbles", "Lubrification", "Contrôle sécurité", "Remplacement pièces"]
    historique.append({
        "Date": d.strftime("%d/%m/%Y"),
        "Type d'opération": random.choice(types_op),
        "Technicien": row["Technicien responsable"],
        "Durée (h)": round(random.uniform(1.5, 6.0), 1),
        "Résultat": random.choice(["Conforme", "Conforme", "Conforme", "Anomalie mineure"]),
    })

st.dataframe(pd.DataFrame(historique), use_container_width=True, hide_index=True)
