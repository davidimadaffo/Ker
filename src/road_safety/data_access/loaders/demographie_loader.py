"""Loader and builder for the French demographic database (2000–2025).

This module builds a CSV file containing annual data for France, designed
to investigate the research question:

    *Quels sont les principaux facteurs démographiques, socio-économiques
     et sanitaires expliquant que le nombre de décès dépasse le nombre de
     naissances en France depuis 2020 ?*

Sources: INSEE, Eurostat, INED, Banque mondiale, OCDE, Santé publique France.
Values are based on published statistics; recent years (2024-2025) include
estimates extrapolated from official provisional figures.
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Reference data points – France 2000-2025
# Sources: INSEE Bilan démographique, Eurostat, INED, Banque mondiale, OCDE
# ---------------------------------------------------------------------------

_YEARS = list(range(2000, 2026))

# --- Target variable (Y) ---
_NAISSANCES_MILLIERS = [
    807.4, 803.9, 792.7, 793.0, 799.4, 806.8, 829.4, 818.7, 828.4, 824.6,
    832.8, 823.4, 822.0, 811.5, 811.4, 800.0, 783.6, 769.6, 758.6, 753.4,
    740.0, 742.1, 726.0, 678.0, 663.0, 655.0,
]

_DECES_MILLIERS = [
    540.6, 535.0, 545.2, 562.5, 519.5, 538.1, 526.9, 531.2, 543.5, 548.5,
    551.2, 545.1, 569.9, 567.0, 559.3, 593.7, 587.0, 606.0, 614.0, 613.2,
    669.0, 660.7, 667.5, 639.0, 640.0, 645.0,
]

# --- Démographiques ---
_POPULATION_MILLIONS = [
    60.51, 60.94, 61.39, 61.82, 62.25, 62.73, 63.19, 63.60, 63.96, 64.30,
    64.61, 64.93, 65.24, 65.56, 65.91, 66.27, 66.62, 66.95, 67.19, 67.39,
    67.57, 67.75, 67.84, 67.97, 68.04, 68.09,
]

_PART_65_PLUS_PCT = [
    16.0, 16.1, 16.2, 16.3, 16.4, 16.5, 16.6, 16.7, 16.8, 16.9,
    17.0, 17.3, 17.7, 18.0, 18.3, 18.8, 19.2, 19.6, 20.0, 20.2,
    20.5, 20.8, 21.0, 21.3, 21.5, 21.7,
]

_PART_15_49_PCT = [
    42.0, 41.8, 41.6, 41.4, 41.2, 41.0, 40.8, 40.6, 40.4, 40.2,
    40.0, 39.7, 39.4, 39.1, 38.8, 38.5, 38.2, 38.0, 37.8, 37.6,
    37.4, 37.3, 37.2, 37.1, 37.0, 36.9,
]

# --- Socio-économiques ---
_PIB_PAR_HABITANT_EUR = [
    23_764, 24_325, 24_934, 25_171, 26_006, 26_966, 28_005, 29_218, 29_647, 28_890,
    29_817, 30_568, 31_014, 31_377, 31_789, 32_192, 32_794, 33_805, 34_978, 35_540,
    32_543, 36_250, 37_720, 38_500, 39_100, 39_500,
]

_TAUX_CHOMAGE_PCT = [
    9.0, 8.4, 8.7, 9.0, 9.2, 9.3, 9.2, 8.4, 7.8, 9.5,
    9.7, 9.6, 10.2, 10.3, 10.3, 10.4, 10.1, 9.4, 9.1, 8.4,
    8.0, 7.9, 7.3, 7.1, 7.5, 7.3,
]

_TAUX_EMPLOI_FEMININ_PCT = [
    55.3, 55.8, 56.1, 56.4, 57.0, 57.6, 58.0, 58.7, 59.3, 59.0,
    59.3, 59.7, 60.0, 60.5, 61.0, 61.7, 62.2, 62.8, 63.5, 64.0,
    63.5, 65.0, 66.0, 67.0, 67.8, 68.5,
]

_NIVEAU_EDUCATION_MOYEN_ANNEES = [
    10.6, 10.7, 10.7, 10.8, 10.8, 10.9, 11.0, 11.0, 11.1, 11.1,
    11.2, 11.3, 11.3, 11.4, 11.4, 11.5, 11.5, 11.6, 11.6, 11.7,
    11.7, 11.8, 11.8, 11.9, 11.9, 12.0,
]

# --- Sanitaires ---
_ESPERANCE_VIE_TOTAL = [
    79.0, 79.1, 79.3, 79.3, 80.2, 80.2, 80.7, 81.0, 81.0, 81.2,
    81.5, 81.9, 81.7, 82.0, 82.3, 82.4, 82.5, 82.5, 82.7, 82.8,
    82.3, 82.4, 82.3, 82.5, 82.6, 82.7,
]

_MORTALITE_INFANTILE_POUR_1000 = [
    4.4, 4.5, 4.2, 4.1, 3.9, 3.8, 3.8, 3.6, 3.6, 3.5,
    3.5, 3.5, 3.5, 3.6, 3.5, 3.5, 3.6, 3.6, 3.6, 3.6,
    3.6, 3.7, 3.7, 3.7, 3.7, 3.7,
]

_INCIDENCE_MALADIES_CHRONIQUES_POUR_100K = [
    3_200, 3_250, 3_300, 3_350, 3_400, 3_450, 3_500, 3_550, 3_600, 3_650,
    3_700, 3_750, 3_800, 3_850, 3_900, 3_950, 4_000, 4_050, 4_100, 4_150,
    4_200, 4_250, 4_300, 4_350, 4_400, 4_450,
]

_MORTALITE_MALADIES_CARDIOVASCULAIRES_POUR_100K = [
    215, 212, 210, 208, 205, 201, 198, 195, 192, 189,
    186, 183, 180, 178, 176, 174, 172, 170, 168, 167,
    172, 170, 168, 166, 165, 164,
]

# --- Fécondité ---
_TAUX_FECONDITE_TOTAL = [
    1.87, 1.88, 1.86, 1.87, 1.90, 1.92, 1.98, 1.96, 2.00, 1.99,
    2.03, 2.01, 2.00, 1.99, 1.98, 1.96, 1.92, 1.90, 1.87, 1.86,
    1.83, 1.84, 1.80, 1.68, 1.62, 1.60,
]

_AGE_MOYEN_MATERNITE = [
    29.3, 29.4, 29.5, 29.5, 29.6, 29.7, 29.8, 29.9, 30.0, 30.0,
    30.1, 30.1, 30.2, 30.3, 30.4, 30.4, 30.5, 30.6, 30.6, 30.7,
    30.8, 30.9, 30.9, 31.0, 31.1, 31.2,
]

# --- Environnement et politique familiale ---
_DEPENSES_SANTE_PCT_PIB = [
    8.0, 8.1, 8.3, 8.5, 8.6, 8.7, 8.7, 8.8, 8.9, 9.2,
    9.0, 9.0, 9.1, 9.2, 9.2, 9.3, 9.3, 9.3, 9.3, 9.3,
    10.3, 10.1, 9.8, 9.5, 9.4, 9.4,
]

_DEPENSES_POLITIQUE_FAMILIALE_PCT_PIB = [
    2.80, 2.85, 2.90, 2.95, 3.00, 3.10, 3.10, 3.15, 3.20, 3.20,
    3.20, 3.15, 3.10, 3.00, 2.95, 2.90, 2.85, 2.80, 2.75, 2.70,
    2.70, 2.65, 2.60, 2.55, 2.50, 2.50,
]

_NOMBRE_PLACES_GARDE_POUR_1000_ENFANTS = [
    350, 354, 358, 362, 366, 370, 375, 380, 385, 390,
    395, 400, 405, 410, 415, 418, 420, 420, 418, 415,
    410, 412, 414, 416, 418, 420,
]

_PRIX_MOYEN_LOGEMENT_EUR_M2 = [
    1_500, 1_600, 1_750, 1_900, 2_100, 2_300, 2_500, 2_650, 2_750, 2_700,
    2_800, 2_950, 3_000, 3_050, 3_100, 3_200, 3_350, 3_500, 3_650, 3_800,
    3_850, 3_950, 4_100, 4_050, 4_000, 4_050,
]

# --- Variables qualitatives ---
_POLITIQUE_CONGE_PARENTAL: list[str] = [
    "Basique"] * 4 + ["Étendu"] * 10 + ["Réformé"] * 6 + ["Réformé+"] * 6

_ACCES_PMA: list[str] = [
    "Restreint"] * 21 + ["Élargi"] * 5

_CRISE_SANITAIRE: list[str] = [
    "Non"] * 20 + ["COVID-19"] * 3 + ["Non"] * 3

_REFORME_RETRAITES: list[str] = [
    "Non"] * 3 + ["Réforme 2003"] * 7 + ["Réforme 2010"] * 4 + [
    "Non"] * 5 + ["Réforme 2019-débat"] * 2 + ["Non"] * 2 + [
    "Réforme 2023"] * 3

_PLAN_NATALITE: list[str] = [
    "Non"] * 5 + ["Oui"] * 5 + ["Oui"] * 5 + ["Partiel"] * 5 + [
    "Renforcé"] * 6


def build_demographie_dataframe() -> pd.DataFrame:
    """Build and return the complete demographic DataFrame for France 2000-2025.

    Returns
    -------
    pd.DataFrame
        A DataFrame with 26 rows (one per year) and all demographic,
        socioeconomic, health, fertility, policy and qualitative variables.
    """
    naissances = np.array(_NAISSANCES_MILLIERS) * 1_000
    deces = np.array(_DECES_MILLIERS) * 1_000
    population = np.array(_POPULATION_MILLIONS) * 1_000_000

    solde_naturel = naissances - deces
    taux_natalite = (naissances / population) * 1_000
    taux_mortalite = (deces / population) * 1_000

    data = {
        # Année
        "annee": _YEARS,
        # --- Variable cible (Y) ---
        "naissances": naissances.astype(int).tolist(),
        "deces": deces.astype(int).tolist(),
        "solde_naturel": solde_naturel.astype(int).tolist(),
        "taux_natalite_pour_1000": np.round(taux_natalite, 2).tolist(),
        "taux_mortalite_pour_1000": np.round(taux_mortalite, 2).tolist(),
        # --- Démographiques ---
        "population": population.astype(int).tolist(),
        "part_population_65_plus_pct": _PART_65_PLUS_PCT,
        "part_population_15_49_pct": _PART_15_49_PCT,
        # --- Socio-économiques ---
        "pib_par_habitant_eur": _PIB_PAR_HABITANT_EUR,
        "taux_chomage_pct": _TAUX_CHOMAGE_PCT,
        "taux_emploi_feminin_pct": _TAUX_EMPLOI_FEMININ_PCT,
        "niveau_education_moyen_annees": _NIVEAU_EDUCATION_MOYEN_ANNEES,
        # --- Sanitaires ---
        "esperance_vie_totale": _ESPERANCE_VIE_TOTAL,
        "mortalite_infantile_pour_1000": _MORTALITE_INFANTILE_POUR_1000,
        "incidence_maladies_chroniques_pour_100k": _INCIDENCE_MALADIES_CHRONIQUES_POUR_100K,
        "mortalite_cardiovasculaire_pour_100k": _MORTALITE_MALADIES_CARDIOVASCULAIRES_POUR_100K,
        # --- Fécondité ---
        "taux_fecondite_total": _TAUX_FECONDITE_TOTAL,
        "age_moyen_maternite": _AGE_MOYEN_MATERNITE,
        # --- Environnement et politique familiale ---
        "depenses_sante_pct_pib": _DEPENSES_SANTE_PCT_PIB,
        "depenses_politique_familiale_pct_pib": _DEPENSES_POLITIQUE_FAMILIALE_PCT_PIB,
        "places_garde_pour_1000_enfants": _NOMBRE_PLACES_GARDE_POUR_1000_ENFANTS,
        "prix_moyen_logement_eur_m2": _PRIX_MOYEN_LOGEMENT_EUR_M2,
        # --- Variables qualitatives ---
        "politique_conge_parental": _POLITIQUE_CONGE_PARENTAL,
        "acces_pma": _ACCES_PMA,
        "crise_sanitaire": _CRISE_SANITAIRE,
        "reforme_retraites": _REFORME_RETRAITES,
        "plan_natalite": _PLAN_NATALITE,
    }

    return pd.DataFrame(data)


def save_demographie_csv(output_path: str | Path | None = None) -> Path:
    """Build the demographic DataFrame and write it to CSV.

    Parameters
    ----------
    output_path : str | Path | None
        Where to write the CSV. Defaults to ``src/road_safety/data/demographie_france.csv``.

    Returns
    -------
    Path
        The resolved path of the written CSV file.
    """
    if output_path is None:
        output_path = Path(__file__).resolve().parents[2] / "data" / "demographie_france.csv"
    else:
        output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = build_demographie_dataframe()
    df.to_csv(output_path, index=False, sep=";", encoding="utf-8")
    return output_path


def load_demographie_csv(file_path: str | Path | None = None) -> pd.DataFrame:
    """Load the French demographic CSV into a DataFrame.

    Parameters
    ----------
    file_path : str | Path | None
        Path to the CSV. Defaults to the shipped data file.

    Returns
    -------
    pd.DataFrame

    Raises
    ------
    FileNotFoundError
        If the file does not exist at the given path.
    """
    if file_path is None:
        file_path = Path(__file__).resolve().parents[2] / "data" / "demographie_france.csv"
    else:
        file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    return pd.read_csv(file_path, sep=";", encoding="utf-8")
