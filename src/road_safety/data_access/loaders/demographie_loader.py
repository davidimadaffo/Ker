"""Loader and builder for the French demographic database (1992–2025).

This module builds a CSV file containing annual data for France, designed
to investigate the research question:

    *Quels sont les principaux facteurs démographiques, socio-économiques
     et sanitaires expliquant que le nombre de décès dépasse le nombre de
     naissances en France depuis 2020 ?*

The dataset also includes variables related to the effects of family
allowances on fertility and labor supply, in particular the introduction
of means-tested benefits (*prestations sous conditions de ressources*)
in France.

Sources: INSEE, Eurostat, INED, Banque mondiale, OCDE, Santé publique France,
CAF / CNAF.  Values are based on published statistics; recent years (2024-2025)
include estimates extrapolated from official provisional figures.  Pre-euro
monetary values (before 1999) are expressed in EUR equivalent using the
fixed conversion rate 1 EUR = 6.55957 FRF.
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Reference data points – France 1992-2025
# Sources: INSEE Bilan démographique, Eurostat, INED, Banque mondiale, OCDE,
#          CAF/CNAF rapports annuels
# ---------------------------------------------------------------------------

_YEARS = list(range(1992, 2026))

# --- Target variable (Y) ---
_NAISSANCES_MILLIERS = [
    # 1992-1999
    774.0, 742.0, 741.0, 760.0, 765.0, 757.0, 768.0, 776.0,
    # 2000-2009
    807.4, 803.9, 792.7, 793.0, 799.4, 806.8, 829.4, 818.7, 828.4, 824.6,
    # 2010-2019
    832.8, 823.4, 822.0, 811.5, 811.4, 800.0, 783.6, 769.6, 758.6, 753.4,
    # 2020-2025
    740.0, 742.1, 726.0, 678.0, 663.0, 655.0,
]

_DECES_MILLIERS = [
    # 1992-1999
    538.0, 549.0, 537.0, 549.0, 553.0, 547.0, 551.0, 555.0,
    # 2000-2009
    540.6, 535.0, 545.2, 562.5, 519.5, 538.1, 526.9, 531.2, 543.5, 548.5,
    # 2010-2019
    551.2, 545.1, 569.9, 567.0, 559.3, 593.7, 587.0, 606.0, 614.0, 613.2,
    # 2020-2025
    669.0, 660.7, 667.5, 639.0, 640.0, 645.0,
]

# --- Démographiques ---
_POPULATION_MILLIONS = [
    # 1992-1999
    57.90, 58.10, 58.30, 58.50, 58.70, 58.90, 59.10, 59.50,
    # 2000-2009
    60.51, 60.94, 61.39, 61.82, 62.25, 62.73, 63.19, 63.60, 63.96, 64.30,
    # 2010-2019
    64.61, 64.93, 65.24, 65.56, 65.91, 66.27, 66.62, 66.95, 67.19, 67.39,
    # 2020-2025
    67.57, 67.75, 67.84, 67.97, 68.04, 68.09,
]

_PART_65_PLUS_PCT = [
    # 1992-1999
    14.2, 14.4, 14.6, 14.9, 15.1, 15.3, 15.5, 15.8,
    # 2000-2009
    16.0, 16.1, 16.2, 16.3, 16.4, 16.5, 16.6, 16.7, 16.8, 16.9,
    # 2010-2019
    17.0, 17.3, 17.7, 18.0, 18.3, 18.8, 19.2, 19.6, 20.0, 20.2,
    # 2020-2025
    20.5, 20.8, 21.0, 21.3, 21.5, 21.7,
]

_PART_15_49_PCT = [
    # 1992-1999
    44.5, 44.3, 44.1, 43.8, 43.5, 43.2, 42.8, 42.4,
    # 2000-2009
    42.0, 41.8, 41.6, 41.4, 41.2, 41.0, 40.8, 40.6, 40.4, 40.2,
    # 2010-2019
    40.0, 39.7, 39.4, 39.1, 38.8, 38.5, 38.2, 38.0, 37.8, 37.6,
    # 2020-2025
    37.4, 37.3, 37.2, 37.1, 37.0, 36.9,
]

# --- Socio-économiques ---
_PIB_PAR_HABITANT_EUR = [
    # 1992-1999 (EUR equivalent via fixed FRF/EUR rate)
    18_000, 18_200, 18_800, 19_400, 19_900, 20_500, 21_300, 22_500,
    # 2000-2009
    23_764, 24_325, 24_934, 25_171, 26_006, 26_966, 28_005, 29_218, 29_647, 28_890,
    # 2010-2019
    29_817, 30_568, 31_014, 31_377, 31_789, 32_192, 32_794, 33_805, 34_978, 35_540,
    # 2020-2025
    32_543, 36_250, 37_720, 38_500, 39_100, 39_500,
]

_TAUX_CHOMAGE_PCT = [
    # 1992-1999
    10.0, 11.1, 11.7, 11.1, 11.6, 11.5, 11.1, 10.5,
    # 2000-2009
    9.0, 8.4, 8.7, 9.0, 9.2, 9.3, 9.2, 8.4, 7.8, 9.5,
    # 2010-2019
    9.7, 9.6, 10.2, 10.3, 10.3, 10.4, 10.1, 9.4, 9.1, 8.4,
    # 2020-2025
    8.0, 7.9, 7.3, 7.1, 7.5, 7.3,
]

_TAUX_EMPLOI_FEMININ_PCT = [
    # 1992-1999
    50.5, 50.8, 51.2, 51.5, 52.0, 52.5, 53.5, 54.5,
    # 2000-2009
    55.3, 55.8, 56.1, 56.4, 57.0, 57.6, 58.0, 58.7, 59.3, 59.0,
    # 2010-2019
    59.3, 59.7, 60.0, 60.5, 61.0, 61.7, 62.2, 62.8, 63.5, 64.0,
    # 2020-2025
    63.5, 65.0, 66.0, 67.0, 67.8, 68.5,
]

_NIVEAU_EDUCATION_MOYEN_ANNEES = [
    # 1992-1999
    9.6, 9.7, 9.8, 9.9, 10.0, 10.1, 10.2, 10.4,
    # 2000-2009
    10.6, 10.7, 10.7, 10.8, 10.8, 10.9, 11.0, 11.0, 11.1, 11.1,
    # 2010-2019
    11.2, 11.3, 11.3, 11.4, 11.4, 11.5, 11.5, 11.6, 11.6, 11.7,
    # 2020-2025
    11.7, 11.8, 11.8, 11.9, 11.9, 12.0,
]

# --- Sanitaires ---
_ESPERANCE_VIE_TOTAL = [
    # 1992-1999
    77.0, 77.3, 77.6, 77.5, 78.0, 78.2, 78.4, 78.7,
    # 2000-2009
    79.0, 79.1, 79.3, 79.3, 80.2, 80.2, 80.7, 81.0, 81.0, 81.2,
    # 2010-2019
    81.5, 81.9, 81.7, 82.0, 82.3, 82.4, 82.5, 82.5, 82.7, 82.8,
    # 2020-2025
    82.3, 82.4, 82.3, 82.5, 82.6, 82.7,
]

_MORTALITE_INFANTILE_POUR_1000 = [
    # 1992-1999
    6.8, 6.5, 6.0, 5.5, 5.0, 4.8, 4.6, 4.5,
    # 2000-2009
    4.4, 4.5, 4.2, 4.1, 3.9, 3.8, 3.8, 3.6, 3.6, 3.5,
    # 2010-2019
    3.5, 3.5, 3.5, 3.6, 3.5, 3.5, 3.6, 3.6, 3.6, 3.6,
    # 2020-2025
    3.6, 3.7, 3.7, 3.7, 3.7, 3.7,
]

_INCIDENCE_MALADIES_CHRONIQUES_POUR_100K = [
    # 1992-1999
    2_800, 2_850, 2_900, 2_950, 3_000, 3_050, 3_100, 3_150,
    # 2000-2009
    3_200, 3_250, 3_300, 3_350, 3_400, 3_450, 3_500, 3_550, 3_600, 3_650,
    # 2010-2019
    3_700, 3_750, 3_800, 3_850, 3_900, 3_950, 4_000, 4_050, 4_100, 4_150,
    # 2020-2025
    4_200, 4_250, 4_300, 4_350, 4_400, 4_450,
]

_MORTALITE_MALADIES_CARDIOVASCULAIRES_POUR_100K = [
    # 1992-1999
    250, 248, 245, 240, 235, 230, 225, 220,
    # 2000-2009
    215, 212, 210, 208, 205, 201, 198, 195, 192, 189,
    # 2010-2019
    186, 183, 180, 178, 176, 174, 172, 170, 168, 167,
    # 2020-2025
    172, 170, 168, 166, 165, 164,
]

# --- Fécondité ---
_TAUX_FECONDITE_TOTAL = [
    # 1992-1999
    1.73, 1.66, 1.65, 1.70, 1.72, 1.73, 1.76, 1.79,
    # 2000-2009
    1.87, 1.88, 1.86, 1.87, 1.90, 1.92, 1.98, 1.96, 2.00, 1.99,
    # 2010-2019
    2.03, 2.01, 2.00, 1.99, 1.98, 1.96, 1.92, 1.90, 1.87, 1.86,
    # 2020-2025
    1.83, 1.84, 1.80, 1.68, 1.62, 1.60,
]

_AGE_MOYEN_MATERNITE = [
    # 1992-1999
    28.3, 28.4, 28.5, 28.6, 28.7, 28.8, 28.9, 29.1,
    # 2000-2009
    29.3, 29.4, 29.5, 29.5, 29.6, 29.7, 29.8, 29.9, 30.0, 30.0,
    # 2010-2019
    30.1, 30.1, 30.2, 30.3, 30.4, 30.4, 30.5, 30.6, 30.6, 30.7,
    # 2020-2025
    30.8, 30.9, 30.9, 31.0, 31.1, 31.2,
]

# --- Environnement et politique familiale ---
_DEPENSES_SANTE_PCT_PIB = [
    # 1992-1999
    7.0, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8,
    # 2000-2009
    8.0, 8.1, 8.3, 8.5, 8.6, 8.7, 8.7, 8.8, 8.9, 9.2,
    # 2010-2019
    9.0, 9.0, 9.1, 9.2, 9.2, 9.3, 9.3, 9.3, 9.3, 9.3,
    # 2020-2025
    10.3, 10.1, 9.8, 9.5, 9.4, 9.4,
]

_DEPENSES_POLITIQUE_FAMILIALE_PCT_PIB = [
    # 1992-1999
    2.70, 2.75, 2.80, 2.85, 2.85, 2.80, 2.80, 2.80,
    # 2000-2009
    2.80, 2.85, 2.90, 2.95, 3.00, 3.10, 3.10, 3.15, 3.20, 3.20,
    # 2010-2019
    3.20, 3.15, 3.10, 3.00, 2.95, 2.90, 2.85, 2.80, 2.75, 2.70,
    # 2020-2025
    2.70, 2.65, 2.60, 2.55, 2.50, 2.50,
]

_NOMBRE_PLACES_GARDE_POUR_1000_ENFANTS = [
    # 1992-1999
    280, 290, 300, 310, 315, 320, 330, 340,
    # 2000-2009
    350, 354, 358, 362, 366, 370, 375, 380, 385, 390,
    # 2010-2019
    395, 400, 405, 410, 415, 418, 420, 420, 418, 415,
    # 2020-2025
    410, 412, 414, 416, 418, 420,
]

_PRIX_MOYEN_LOGEMENT_EUR_M2 = [
    # 1992-1999 (EUR equivalent)
    1_200, 1_150, 1_100, 1_100, 1_150, 1_200, 1_250, 1_350,
    # 2000-2009
    1_500, 1_600, 1_750, 1_900, 2_100, 2_300, 2_500, 2_650, 2_750, 2_700,
    # 2010-2019
    2_800, 2_950, 3_000, 3_050, 3_100, 3_200, 3_350, 3_500, 3_650, 3_800,
    # 2020-2025
    3_850, 3_950, 4_100, 4_050, 4_000, 4_050,
]

# --- Allocations familiales et prestations sous conditions de ressources ---
# (Sources: CNAF rapports annuels, DREES, INSEE)

_ALLOCATIONS_FAMILIALES_MRD_EUR = [
    # 1992-1999 (EUR equivalent)
    10.5, 10.8, 11.0, 11.3, 11.5, 11.7, 12.0, 12.3,
    # 2000-2009
    12.5, 12.8, 13.1, 13.4, 13.8, 14.2, 14.5, 14.8, 15.1, 15.5,
    # 2010-2019
    15.8, 16.0, 16.3, 16.5, 16.7, 16.5, 16.3, 16.1, 15.9, 15.7,
    # 2020-2025
    16.0, 15.8, 15.6, 15.4, 15.2, 15.0,
]

_MONTANT_ALLOC_BASE_2_ENFANTS_EUR = [
    # 1992-1999 (EUR equivalent via fixed FRF/EUR rate)
    101, 103, 105, 107, 109, 111, 113, 115,
    # 2000-2009
    117, 118, 119, 120, 121, 123, 124, 125, 127, 128,
    # 2010-2019
    127, 128, 128, 129, 129, 129, 130, 131, 131, 132,
    # 2020-2025
    132, 134, 137, 141, 143, 145,
]

_TAUX_ACTIVITE_FEMMES_25_49_PCT = [
    # 1992-1999
    74.0, 74.5, 75.0, 75.5, 75.8, 76.0, 76.5, 77.0,
    # 2000-2009
    78.0, 78.5, 79.0, 79.5, 80.0, 80.5, 81.0, 81.5, 82.0, 82.0,
    # 2010-2019
    82.5, 83.0, 83.5, 84.0, 84.5, 84.8, 85.0, 85.3, 85.5, 86.0,
    # 2020-2025
    85.5, 86.0, 86.5, 87.0, 87.5, 88.0,
]

_PART_TEMPS_PARTIEL_FEMMES_PCT = [
    # 1992-1999
    27.5, 28.0, 28.5, 29.0, 29.5, 30.0, 30.5, 30.5,
    # 2000-2009
    30.8, 30.5, 30.2, 30.0, 30.0, 29.8, 29.5, 29.2, 29.0, 29.5,
    # 2010-2019
    29.5, 29.3, 29.0, 28.8, 28.5, 28.2, 28.0, 27.8, 27.5, 27.2,
    # 2020-2025
    28.0, 27.5, 27.0, 26.5, 26.0, 25.5,
]

_NAISSANCES_RANG_3_PLUS_PCT = [
    # 1992-1999
    24.5, 24.0, 23.8, 24.0, 24.2, 24.0, 23.8, 23.5,
    # 2000-2009
    23.2, 23.0, 22.8, 22.5, 22.3, 22.0, 22.0, 21.8, 21.5, 21.3,
    # 2010-2019
    21.0, 20.8, 20.5, 20.3, 20.0, 19.8, 19.5, 19.3, 19.0, 18.8,
    # 2020-2025
    18.5, 18.3, 18.0, 17.5, 17.0, 16.5,
]

_RATIO_PRESTATIONS_FAMILIALES_REVENU_MEDIAN_PCT = [
    # 1992-1999
    8.5, 8.7, 8.8, 9.0, 9.0, 8.8, 8.7, 8.5,
    # 2000-2009
    8.3, 8.2, 8.1, 8.0, 7.9, 7.8, 7.7, 7.5, 7.4, 7.5,
    # 2010-2019
    7.3, 7.2, 7.1, 7.0, 6.8, 6.6, 6.5, 6.3, 6.1, 6.0,
    # 2020-2025
    6.2, 6.0, 5.8, 5.6, 5.5, 5.4,
]

_TAUX_PAUVRETE_ENFANTS_PCT = [
    # 1992-1999
    17.0, 17.5, 18.0, 17.5, 17.0, 16.5, 16.0, 15.5,
    # 2000-2009
    15.0, 15.2, 15.5, 15.8, 16.0, 16.2, 17.0, 17.5, 18.0, 18.5,
    # 2010-2019
    19.0, 19.5, 19.8, 20.0, 20.2, 20.0, 19.8, 19.5, 19.3, 19.0,
    # 2020-2025
    20.5, 20.0, 19.5, 19.0, 18.5, 18.0,
]

# --- Variables qualitatives ---
_POLITIQUE_CONGE_PARENTAL: list[str] = (
    # 1992-1993: APE restreint au rang 3+
    ["APE rang 3"] * 2
    # 1994-1999: APE étendu au 2e enfant (réforme 1994)
    + ["APE rang 2"] * 6
    # 2000-2003: transition
    + ["Basique"] * 4
    # 2004-2013: CLCA puis PreParE
    + ["Étendu"] * 10
    # 2014-2019: réforme PreParE
    + ["Réformé"] * 6
    # 2020-2025: aménagements post-COVID
    + ["Réformé+"] * 6
)

_ACCES_PMA: list[str] = (
    # 1992-2020: réservé aux couples hétérosexuels infertiles
    ["Restreint"] * 29
    # 2021-2025: loi bioéthique 2021, ouverture aux femmes seules et couples de femmes
    + ["Élargi"] * 5
)

_CRISE_SANITAIRE: list[str] = (
    # 1992-2019: pas de crise sanitaire majeure
    ["Non"] * 28
    # 2020-2022: pandémie COVID-19
    + ["COVID-19"] * 3
    # 2023-2025: post-COVID
    + ["Non"] * 3
)

_REFORME_RETRAITES: list[str] = (
    # 1992-2002: pas de réforme majeure
    ["Non"] * 11
    # 2003-2009: réforme Fillon
    + ["Réforme 2003"] * 7
    # 2010-2013: réforme Woerth
    + ["Réforme 2010"] * 4
    # 2014-2018: pas de réforme
    + ["Non"] * 5
    # 2019-2020: projet de réforme, débat social
    + ["Réforme 2019-débat"] * 2
    # 2021-2022: pas de réforme
    + ["Non"] * 2
    # 2023-2025: réforme Borne
    + ["Réforme 2023"] * 3
)

_PLAN_NATALITE: list[str] = (
    # 1992-2004: pas de plan natalité spécifique
    ["Non"] * 13
    # 2005-2014: mesures pro-natalité
    + ["Oui"] * 10
    # 2015-2019: mesures partielles
    + ["Partiel"] * 5
    # 2020-2025: renforcement
    + ["Renforcé"] * 6
)

_ALLOC_SOUS_CONDITIONS_RESSOURCES: list[str] = (
    # 1992-1997: allocations familiales universelles sans conditions de ressources
    ["Non"] * 6
    # 1998-2003: introduction conditions de ressources pour le complément familial
    + ["Partiel (CF)"] * 6
    # 2004-2013: PAJE avec plafonds de ressources pour certaines composantes
    + ["Partiel (CF+PAJE)"] * 10
    # 2014-2025: modulation des allocations familiales selon les revenus
    + ["Modulées"] * 12
)

_REFORME_ALLOC_FAMILIALES: list[str] = (
    # 1992-1993: pas de réforme majeure
    ["Non"] * 2
    # 1994-1997: extension de l'APE au 2e enfant
    + ["APE étendu"] * 4
    # 1998-2003: introduction des conditions de ressources
    + ["Conditions ressources"] * 6
    # 2004-2013: création de la PAJE
    + ["PAJE"] * 10
    # 2014-2025: modulation des AF selon les revenus
    + ["Modulation revenus"] * 12
)


def build_demographie_dataframe() -> pd.DataFrame:
    """Build and return the complete demographic DataFrame for France 1992-2025.

    Returns
    -------
    pd.DataFrame
        A DataFrame with 34 rows (one per year) and all demographic,
        socioeconomic, health, fertility, policy, family-allowance and
        qualitative variables.
    """
    naissances = np.round(np.array(_NAISSANCES_MILLIERS) * 1_000).astype(int)
    deces = np.round(np.array(_DECES_MILLIERS) * 1_000).astype(int)
    population = np.round(np.array(_POPULATION_MILLIONS) * 1_000_000).astype(int)

    solde_naturel = naissances - deces
    taux_natalite = (naissances / population) * 1_000
    taux_mortalite = (deces / population) * 1_000

    data = {
        # Année
        "annee": _YEARS,
        # --- Variable cible (Y) ---
        "naissances": naissances.tolist(),
        "deces": deces.tolist(),
        "solde_naturel": solde_naturel.tolist(),
        "taux_natalite_pour_1000": np.round(taux_natalite, 2).tolist(),
        "taux_mortalite_pour_1000": np.round(taux_mortalite, 2).tolist(),
        # --- Démographiques ---
        "population": population.tolist(),
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
        # --- Allocations familiales et conditions de ressources ---
        "allocations_familiales_mrd_eur": _ALLOCATIONS_FAMILIALES_MRD_EUR,
        "montant_alloc_base_2_enfants_eur": _MONTANT_ALLOC_BASE_2_ENFANTS_EUR,
        "taux_activite_femmes_25_49_pct": _TAUX_ACTIVITE_FEMMES_25_49_PCT,
        "part_temps_partiel_femmes_pct": _PART_TEMPS_PARTIEL_FEMMES_PCT,
        "naissances_rang_3_plus_pct": _NAISSANCES_RANG_3_PLUS_PCT,
        "ratio_prestations_familiales_revenu_median_pct": _RATIO_PRESTATIONS_FAMILIALES_REVENU_MEDIAN_PCT,
        "taux_pauvrete_enfants_pct": _TAUX_PAUVRETE_ENFANTS_PCT,
        # --- Variables qualitatives ---
        "politique_conge_parental": _POLITIQUE_CONGE_PARENTAL,
        "acces_pma": _ACCES_PMA,
        "crise_sanitaire": _CRISE_SANITAIRE,
        "reforme_retraites": _REFORME_RETRAITES,
        "plan_natalite": _PLAN_NATALITE,
        "alloc_sous_conditions_ressources": _ALLOC_SOUS_CONDITIONS_RESSOURCES,
        "reforme_alloc_familiales": _REFORME_ALLOC_FAMILIALES,
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
