import streamlit as st
import pandas as pd
import plotly.express as px
from data import charger_donnees, couleur_statut

st.set_page_config(page_title="Maintenance", page_icon="🔧", layout="wide")


@st.cache_data
def get_data():
    return charger_donnees()


df = get_data()

st.title("🔧 Planification des maintenances")

col_filtre, col_vide = st.columns([2, 3])
with col_filtre:
    horizon = st.slider("Horizon (jours)", min_value=7, max_value=180, value=60, step=7)

st.divider()

df_agenda = df.copy()
df_agenda["Urgence"] = df_agenda["Jours avant maintenance"].apply(
    lambda j: "En retard" if j < 0 else "Urgent (< 14j)" if j <= 14 else "Bientôt (14-30j)" if j <= 30 else "Planifié"
)

df_horizon = df_agenda[df_agenda["Jours avant maintenance"] <= horizon].sort_values("Jours avant maintenance")

palette = {
    "En retard": "#EF4444",
    "Urgent (< 14j)": "#F97316",
    "Bientôt (14-30j)": "#F59E0B",
    "Planifié": "#3B82F6",
}

col1, col2, col3, col4 = st.columns(4)
for statut_u, col in zip(["En retard", "Urgent (< 14j)", "Bientôt (14-30j)", "Planifié"], [col1, col2, col3, col4]):
    n = len(df_horizon[df_horizon["Urgence"] == statut_u])
    couleur = palette[statut_u]
    col.markdown(f"""<div style="background:white;border-radius:10px;padding:16px;
        border-left:5px solid {couleur};box-shadow:0 1px 4px rgba(0,0,0,.08);margin-bottom:8px">
        <p style="font-size:.8rem;color:#6B7280;margin:0">{statut_u}</p>
        <p style="font-size:1.8rem;font-weight:700;color:{couleur};margin:0">{n}</p>
        </div>""", unsafe_allow_html=True)

st.subheader(f"Ascenseurs à traiter dans les {horizon} prochains jours ({len(df_horizon)})")

if df_horizon.empty:
    st.success("Aucune maintenance prévue dans cet horizon.")
else:
    cols_aff = ["ID", "Bâtiment", "Marque", "Statut", "Urgence",
                "Prochaine maintenance", "Jours avant maintenance", "Technicien responsable"]

    def color_urgence(row):
        c = palette.get(row["Urgence"], "")
        if not c:
            return [""] * len(row)
        alpha = "33"
        bg = c + alpha
        return [f"background-color:{bg}"] * len(row)

    st.dataframe(
        df_horizon[cols_aff].style.apply(color_urgence, axis=1),
        use_container_width=True,
        hide_index=True,
    )

st.divider()
st.subheader("Charge de travail par technicien (horizon sélectionné)")

charge = df_horizon.groupby("Technicien responsable").size().reset_index(name="Interventions")
fig = px.bar(charge, x="Technicien responsable", y="Interventions",
             color="Technicien responsable", text="Interventions")
fig.update_traces(textposition="outside")
fig.update_layout(showlegend=False, margin=dict(t=20, b=20))
st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("Calendrier des maintenances (prochains 90 jours)")

df_cal = df_agenda[df_agenda["Jours avant maintenance"].between(0, 90)].copy()
df_cal["Prochaine maintenance"] = pd.to_datetime(df_cal["Prochaine maintenance"])
df_cal["Fin"] = df_cal["Prochaine maintenance"] + pd.Timedelta(hours=4)

if not df_cal.empty:
    fig_gantt = px.timeline(
        df_cal.sort_values("Prochaine maintenance"),
        x_start="Prochaine maintenance",
        x_end="Fin",
        y="ID",
        color="Marque",
        hover_data=["Bâtiment", "Technicien responsable"],
        labels={"ID": "Ascenseur"},
    )
    fig_gantt.update_yaxes(autorange="reversed")
    fig_gantt.update_layout(margin=dict(t=20, b=20), height=500)
    st.plotly_chart(fig_gantt, use_container_width=True)
else:
    st.info("Aucune maintenance planifiée dans les 90 prochains jours.")
