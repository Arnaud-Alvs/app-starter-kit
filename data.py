import pandas as pd
from datetime import date, timedelta
import random

STATUTS = {
    "Opérationnel": "#22C55E",
    "En maintenance": "#F59E0B",
    "Hors service": "#EF4444",
    "Inspection requise": "#8B5CF6",
}

MARQUES = ["Otis", "Schindler", "KONE", "ThyssenKrupp", "Mitsubishi", "Orona", "Fujitec"]

BATIMENTS = [
    "Tour Centrale A", "Tour Centrale B", "Résidence Les Pins",
    "Centre Commercial Nord", "Hôpital Saint-Louis", "Immeuble Horizon",
    "Parking Souterrain P1", "Mairie Annexe", "Lycée Jean Moulin",
    "Clinique du Parc",
]

TYPES = ["Traction", "Hydraulique", "À vis"]


def _generer_donnees() -> pd.DataFrame:
    random.seed(42)
    today = date.today()
    rows = []
    for i in range(1, 47):
        marque = random.choice(MARQUES)
        annee_fab = random.randint(1982, 2020)
        age = today.year - annee_fab
        statut = random.choices(
            list(STATUTS.keys()),
            weights=[65, 18, 8, 9],
        )[0]
        derniere_maintenance = today - timedelta(days=random.randint(10, 365))
        periodicite = random.choice([90, 180, 365])
        prochaine_maintenance = derniere_maintenance + timedelta(days=periodicite)
        jours_restants = (prochaine_maintenance - today).days
        nb_etages = random.choice([3, 5, 8, 10, 12, 15, 18, 20])
        capacite_kg = random.choice([480, 630, 800, 1000, 1275, 1600])
        nb_incidents = random.randint(0, 8) if age > 20 else random.randint(0, 3)
        rows.append({
            "ID": f"ASC-{i:03d}",
            "Bâtiment": random.choice(BATIMENTS),
            "Marque": marque,
            "Modèle": f"{marque[:3].upper()}-{random.randint(100, 999)}",
            "Type": random.choice(TYPES),
            "Année de fabrication": annee_fab,
            "Âge (ans)": age,
            "Statut": statut,
            "Étages desservis": nb_etages,
            "Capacité (kg)": capacite_kg,
            "Dernière maintenance": derniere_maintenance,
            "Prochaine maintenance": prochaine_maintenance,
            "Jours avant maintenance": jours_restants,
            "Incidents (12 mois)": nb_incidents,
            "Technicien responsable": random.choice(["M. Dupont", "Mme. Martin", "M. Bernard", "Mme. Leroy"]),
        })
    return pd.DataFrame(rows)


def charger_donnees() -> pd.DataFrame:
    return _generer_donnees()


def couleur_statut(statut: str) -> str:
    return STATUTS.get(statut, "#6B7280")


def badge_statut(statut: str) -> str:
    couleur = couleur_statut(statut)
    return f'<span style="background:{couleur};color:white;padding:2px 10px;border-radius:12px;font-size:0.82em;font-weight:600">{statut}</span>'
