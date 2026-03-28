"""Pandera schema for the French demographic CSV (demographie_france.csv).

Validates column presence, types, and value ranges.
"""

from dataclasses import dataclass


@dataclass
class DemographieSchema:
    """Describes one row of the demographie_france dataset."""

    annee: int
    # --- Target ---
    naissances: int
    deces: int
    solde_naturel: int
    taux_natalite_pour_1000: float
    taux_mortalite_pour_1000: float
    # --- Démographiques ---
    population: int
    part_population_65_plus_pct: float
    part_population_15_49_pct: float
    # --- Socio-économiques ---
    pib_par_habitant_eur: int
    taux_chomage_pct: float
    taux_emploi_feminin_pct: float
    niveau_education_moyen_annees: float
    # --- Sanitaires ---
    esperance_vie_totale: float
    mortalite_infantile_pour_1000: float
    incidence_maladies_chroniques_pour_100k: int
    mortalite_cardiovasculaire_pour_100k: int
    # --- Fécondité ---
    taux_fecondite_total: float
    age_moyen_maternite: float
    # --- Politique familiale ---
    depenses_sante_pct_pib: float
    depenses_politique_familiale_pct_pib: float
    places_garde_pour_1000_enfants: int
    prix_moyen_logement_eur_m2: int
    # --- Allocations familiales et conditions de ressources ---
    allocations_familiales_mrd_eur: float
    montant_alloc_base_2_enfants_eur: int
    taux_activite_femmes_25_49_pct: float
    part_temps_partiel_femmes_pct: float
    naissances_rang_3_plus_pct: float
    ratio_prestations_familiales_revenu_median_pct: float
    taux_pauvrete_enfants_pct: float
    # --- Qualitatives ---
    politique_conge_parental: str
    acces_pma: str
    crise_sanitaire: str
    reforme_retraites: str
    plan_natalite: str
    alloc_sous_conditions_ressources: str
    reforme_alloc_familiales: str


# Expected columns in the CSV
EXPECTED_COLUMNS = [
    "annee",
    "naissances",
    "deces",
    "solde_naturel",
    "taux_natalite_pour_1000",
    "taux_mortalite_pour_1000",
    "population",
    "part_population_65_plus_pct",
    "part_population_15_49_pct",
    "pib_par_habitant_eur",
    "taux_chomage_pct",
    "taux_emploi_feminin_pct",
    "niveau_education_moyen_annees",
    "esperance_vie_totale",
    "mortalite_infantile_pour_1000",
    "incidence_maladies_chroniques_pour_100k",
    "mortalite_cardiovasculaire_pour_100k",
    "taux_fecondite_total",
    "age_moyen_maternite",
    "depenses_sante_pct_pib",
    "depenses_politique_familiale_pct_pib",
    "places_garde_pour_1000_enfants",
    "prix_moyen_logement_eur_m2",
    "allocations_familiales_mrd_eur",
    "montant_alloc_base_2_enfants_eur",
    "taux_activite_femmes_25_49_pct",
    "part_temps_partiel_femmes_pct",
    "naissances_rang_3_plus_pct",
    "ratio_prestations_familiales_revenu_median_pct",
    "taux_pauvrete_enfants_pct",
    "politique_conge_parental",
    "acces_pma",
    "crise_sanitaire",
    "reforme_retraites",
    "plan_natalite",
    "alloc_sous_conditions_ressources",
    "reforme_alloc_familiales",
]

YEAR_RANGE = (1992, 2025)
NUM_ROWS = 34  # one per year
