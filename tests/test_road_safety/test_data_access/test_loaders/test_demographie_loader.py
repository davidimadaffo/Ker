"""Tests for the French demographic data loader and CSV builder."""

import pandas as pd
import pytest

from road_safety.data_access.loaders.demographie_loader import (
    build_demographie_dataframe,
    load_demographie_csv,
    save_demographie_csv,
)
from road_safety.data_access.schemas.demographie_schemas import (
    EXPECTED_COLUMNS,
    NUM_ROWS,
    YEAR_RANGE,
)


class TestBuildDemographieDataframe:

    def test_returns_dataframe(self):
        df = build_demographie_dataframe()
        assert isinstance(df, pd.DataFrame)

    def test_row_count(self):
        df = build_demographie_dataframe()
        assert len(df) == NUM_ROWS

    def test_columns_present(self):
        df = build_demographie_dataframe()
        assert list(df.columns) == EXPECTED_COLUMNS

    def test_year_range(self):
        df = build_demographie_dataframe()
        assert df["annee"].min() == YEAR_RANGE[0]
        assert df["annee"].max() == YEAR_RANGE[1]

    def test_no_missing_values(self):
        df = build_demographie_dataframe()
        assert df.isnull().sum().sum() == 0

    def test_solde_naturel_equals_births_minus_deaths(self):
        df = build_demographie_dataframe()
        expected = df["naissances"] - df["deces"]
        pd.testing.assert_series_equal(
            df["solde_naturel"], expected, check_names=False
        )

    def test_solde_naturel_decreases_over_time(self):
        df = build_demographie_dataframe()
        first_5 = df["solde_naturel"].head(5).mean()
        last_5 = df["solde_naturel"].tail(5).mean()
        assert last_5 < first_5

    def test_population_positive(self):
        df = build_demographie_dataframe()
        assert (df["population"] > 0).all()

    def test_percentages_in_range(self):
        df = build_demographie_dataframe()
        for col in [
            "part_population_65_plus_pct",
            "part_population_15_49_pct",
            "taux_chomage_pct",
            "taux_emploi_feminin_pct",
        ]:
            assert (df[col] >= 0).all(), f"{col} has negative values"
            assert (df[col] <= 100).all(), f"{col} exceeds 100%"

    def test_fertility_rate_positive(self):
        df = build_demographie_dataframe()
        assert (df["taux_fecondite_total"] > 0).all()

    def test_qualitative_columns_not_empty(self):
        df = build_demographie_dataframe()
        for col in [
            "politique_conge_parental",
            "acces_pma",
            "crise_sanitaire",
            "reforme_retraites",
            "plan_natalite",
        ]:
            assert (df[col].str.len() > 0).all(), f"{col} has empty strings"


class TestSaveAndLoadDemographieCsv:

    def test_save_creates_file(self, tmp_path):
        out = tmp_path / "test_demo.csv"
        result = save_demographie_csv(out)
        assert result.exists()

    def test_load_returns_dataframe(self, tmp_path):
        out = tmp_path / "test_demo.csv"
        save_demographie_csv(out)
        df = load_demographie_csv(out)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == NUM_ROWS

    def test_round_trip_preserves_data(self, tmp_path):
        out = tmp_path / "test_demo.csv"
        save_demographie_csv(out)
        df = load_demographie_csv(out)
        assert list(df.columns) == EXPECTED_COLUMNS
        assert df["annee"].min() == YEAR_RANGE[0]
        assert df["annee"].max() == YEAR_RANGE[1]

    def test_load_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_demographie_csv(tmp_path / "nonexistent.csv")
