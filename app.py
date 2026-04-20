import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data import charger_donnees, STATUTS, couleur_statut

st.set_page_config(
    page_title="Flotte Ascenseurs",
    page_icon="🛗",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.kpi-card {
    background: white;
    border-radius: 12px;
    padding: 20px 24px;
    box-shadow: 0 1px 4px rgba(0,0,0,.08);
    border-left: 5px solid;
    margin-bottom: 8px;
}
.kpi-value { font-size: 2.2rem; font-weight: 700; margin: 0; }
.kpi-label { font-size: 0.85rem; color: #6B7280; margin: 0; }
.alert-box {
    background: #FEF3C7;
    border: 1px solid #F59E0B;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 8px;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def get_data():
    return charger_donnees()


df = get_data()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🛗 Flotte Ascenseurs")
    st.divider()

    statut_filtre = st.multiselect(
        "Statut",
        options=list(STATUTS.keys()),
        default=list(STATUTS.keys()),
    )
    marque_filtre = st.multiselect(
        "Marque",
        options=sorted(df["Marque"].unique()),
        default=[],
    )
    batiment_filtre = st.multiselect(
        "Bâtiment",
        options=sorted(df["Bâtiment"].unique()),
        default=[],
    )
    st.divider()
    st.caption("Données simulées — mise à jour automatique")

df_f = df[df["Statut"].isin(statut_filtre)]
if marque_filtre:
    df_f = df_f[df_f["Marque"].isin(marque_filtre)]
if batiment_filtre:
    df_f = df_f[df_f["Bâtiment"].isin(batiment_filtre)]

# ── Header ───────────────────────────────────────────────────────────────────
st.title("Tableau de bord — Flotte d'ascenseurs")
st.caption(f"{len(df_f)} ascenseur(s) affiché(s) sur {len(df)} au total")

# ── KPI row ──────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
operationnels = len(df_f[df_f["Statut"] == "Opérationnel"])
en_maintenance = len(df_f[df_f["Statut"] == "En maintenance"])
hors_service = len(df_f[df_f["Statut"] == "Hors service"])
inspection = len(df_f[df_f["Statut"] == "Inspection requise"])
taux_dispo = round(operationnels / len(df_f) * 100) if len(df_f) else 0

with k1:
    st.markdown(f"""<div class="kpi-card" style="border-color:#1E3A5F">
    <p class="kpi-label">Total ascenseurs</p>
    <p class="kpi-value">{len(df_f)}</p></div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="kpi-card" style="border-color:#22C55E">
    <p class="kpi-label">Opérationnels</p>
    <p class="kpi-value" style="color:#22C55E">{operationnels}</p></div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class="kpi-card" style="border-color:#F59E0B">
    <p class="kpi-label">En maintenance</p>
    <p class="kpi-value" style="color:#F59E0B">{en_maintenance}</p></div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""<div class="kpi-card" style="border-color:#EF4444">
    <p class="kpi-label">Hors service</p>
    <p class="kpi-value" style="color:#EF4444">{hors_service}</p></div>""", unsafe_allow_html=True)
with k5:
    color = "#22C55E" if taux_dispo >= 80 else "#F59E0B" if taux_dispo >= 60 else "#EF4444"
    st.markdown(f"""<div class="kpi-card" style="border-color:{color}">
    <p class="kpi-label">Taux de disponibilité</p>
    <p class="kpi-value" style="color:{color}">{taux_dispo}%</p></div>""", unsafe_allow_html=True)

st.divider()

# ── Alertes ──────────────────────────────────────────────────────────────────
alertes = df_f[df_f["Jours avant maintenance"] <= 30].sort_values("Jours avant maintenance")
if len(alertes):
    with st.expander(f"⚠️ {len(alertes)} ascenseur(s) nécessitent une attention dans les 30 prochains jours", expanded=True):
        for _, row in alertes.iterrows():
            jours = row["Jours avant maintenance"]
            couleur = "#EF4444" if jours < 0 else "#F59E0B"
            msg = f"En retard de {abs(jours)}j" if jours < 0 else f"Dans {jours}j"
            st.markdown(
                f'<div class="alert-box"><b>{row["ID"]}</b> — {row["Bâtiment"]} ({row["Marque"]}) — '
                f'Maintenance prévue le {row["Prochaine maintenance"].strftime("%d/%m/%Y")} '
                f'<span style="color:{couleur};font-weight:600">({msg})</span></div>',
                unsafe_allow_html=True,
            )

# ── Charts row ───────────────────────────────────────────────────────────────
col_a, col_b, col_c = st.columns([1, 1, 1])

with col_a:
    st.subheader("Statuts")
    counts = df_f["Statut"].value_counts().reset_index()
    counts.columns = ["Statut", "Nombre"]
    colors = [couleur_statut(s) for s in counts["Statut"]]
    fig = px.pie(counts, names="Statut", values="Nombre", color="Statut",
                 color_discrete_map={s: couleur_statut(s) for s in STATUTS},
                 hole=0.45)
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=True,
                      legend=dict(orientation="h", y=-0.15))
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.subheader("Par marque")
    by_brand = df_f.groupby(["Marque", "Statut"]).size().reset_index(name="n")
    fig2 = px.bar(by_brand, x="Marque", y="n", color="Statut",
                  color_discrete_map={s: couleur_statut(s) for s in STATUTS},
                  labels={"n": "Ascenseurs", "Marque": ""})
    fig2.update_layout(margin=dict(t=10, b=10, l=10, r=10), legend_title="")
    st.plotly_chart(fig2, use_container_width=True)

with col_c:
    st.subheader("Âge de la flotte")
    fig3 = px.histogram(df_f, x="Âge (ans)", nbins=15, color_discrete_sequence=["#1E3A5F"])
    fig3.update_layout(margin=dict(t=10, b=10, l=10, r=10),
                       xaxis_title="Âge (ans)", yaxis_title="Nb ascenseurs")
    st.plotly_chart(fig3, use_container_width=True)

st.divider()

# ── Table ────────────────────────────────────────────────────────────────────
st.subheader("Liste de la flotte")

cols_affichees = ["ID", "Bâtiment", "Marque", "Modèle", "Type",
                  "Année de fabrication", "Âge (ans)", "Statut",
                  "Étages desservis", "Capacité (kg)",
                  "Dernière maintenance", "Prochaine maintenance",
                  "Jours avant maintenance", "Incidents (12 mois)", "Technicien responsable"]

search = st.text_input("Rechercher (ID, bâtiment, marque…)", placeholder="ex: ASC-012 ou Otis")
df_display = df_f[cols_affichees].copy()
if search:
    mask = df_display.apply(lambda col: col.astype(str).str.contains(search, case=False, na=False)).any(axis=1)
    df_display = df_display[mask]

def colorize_row(row):
    color = ""
    if row["Statut"] == "Hors service":
        color = "background-color: #FEE2E2"
    elif row["Statut"] == "En maintenance":
        color = "background-color: #FEF3C7"
    elif row["Statut"] == "Inspection requise":
        color = "background-color: #EDE9FE"
    return [color] * len(row)

st.dataframe(
    df_display.style.apply(colorize_row, axis=1),
    use_container_width=True,
    height=450,
    hide_index=True,
)
