import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from data import charger_donnees, couleur_statut, STATUTS

st.set_page_config(page_title="Statistiques", page_icon="📊", layout="wide")


@st.cache_data
def get_data():
    return charger_donnees()


df = get_data()

st.title("📊 Statistiques de la flotte")

st.subheader("Répartition par bâtiment")
by_bat = df.groupby(["Bâtiment", "Statut"]).size().reset_index(name="n")
fig1 = px.bar(by_bat, x="Bâtiment", y="n", color="Statut",
              color_discrete_map={s: couleur_statut(s) for s in STATUTS},
              labels={"n": "Ascenseurs", "Bâtiment": ""})
fig1.update_layout(xaxis_tickangle=-30, margin=dict(t=10, b=80))
st.plotly_chart(fig1, use_container_width=True)

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Âge moyen par marque")
    age_marque = df.groupby("Marque")["Âge (ans)"].mean().round(1).reset_index()
    age_marque = age_marque.sort_values("Âge (ans)", ascending=True)
    fig2 = px.bar(age_marque, x="Âge (ans)", y="Marque", orientation="h",
                  color="Âge (ans)", color_continuous_scale="RdYlGn_r",
                  labels={"Âge (ans)": "Âge moyen (ans)"})
    fig2.update_layout(margin=dict(t=10, b=10), coloraxis_showscale=False)
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.subheader("Incidents moyens par marque")
    inc_marque = df.groupby("Marque")["Incidents (12 mois)"].mean().round(2).reset_index()
    inc_marque = inc_marque.sort_values("Incidents (12 mois)", ascending=True)
    fig3 = px.bar(inc_marque, x="Incidents (12 mois)", y="Marque", orientation="h",
                  color="Incidents (12 mois)", color_continuous_scale="RdYlGn_r",
                  labels={"Incidents (12 mois)": "Incidents moyens / an"})
    fig3.update_layout(margin=dict(t=10, b=10), coloraxis_showscale=False)
    st.plotly_chart(fig3, use_container_width=True)

st.divider()

col3, col4 = st.columns(2)

with col3:
    st.subheader("Distribution des capacités")
    fig4 = px.histogram(df, x="Capacité (kg)", color="Type",
                        nbins=10, barmode="overlay",
                        labels={"Capacité (kg)": "Capacité (kg)", "count": "Nombre"})
    fig4.update_layout(margin=dict(t=10, b=10))
    st.plotly_chart(fig4, use_container_width=True)

with col4:
    st.subheader("Corrélation âge / incidents")
    fig5 = px.scatter(df, x="Âge (ans)", y="Incidents (12 mois)", color="Marque",
                      size="Capacité (kg)", hover_data=["ID", "Bâtiment", "Statut"],
                      labels={"Âge (ans)": "Âge (ans)", "Incidents (12 mois)": "Incidents / 12 mois"})
    fig5.update_layout(margin=dict(t=10, b=10))
    st.plotly_chart(fig5, use_container_width=True)

st.divider()

st.subheader("Résumé par statut")
resume = df.groupby("Statut").agg(
    Nombre=("ID", "count"),
    Age_moyen=("Âge (ans)", "mean"),
    Incidents_moyen=("Incidents (12 mois)", "mean"),
).round(1).reset_index()
resume.columns = ["Statut", "Nombre", "Âge moyen (ans)", "Incidents moyens"]
st.dataframe(resume, use_container_width=True, hide_index=True)
