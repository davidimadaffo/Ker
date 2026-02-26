import pytest
import pandas as pd
from src.road_safety.data_access.loaders import accident_loader

class TestAccidentLoader:
    
    def test_clean_string_value_corrects_nanterre(self):
        # Arrange
        input_val = "Non renseignee nterre"
        # Act
        result = accident_loader.clean_string_value(input_val)
        # Assert
        assert result == "Nanterre"

    def test_clean_string_value_corrects_luminosity(self):
        # Arrange
        input_val = "Nuit sanseclairage public"
        # Act
        result = accident_loader.clean_string_value(input_val)
        # Assert
        assert result == "Nuit sans eclairage public"

    def test_clean_string_value_handles_normal(self):
        # Arrange
        input_val = "Plein jour"
        # Act
        result = accident_loader.clean_string_value(input_val)
        # Assert
        assert result == "Plein jour"

    def test_safe_convert_int_valid(self):
        assert accident_loader.safe_convert_int("47") == 47

    def test_safe_convert_int_invalid(self):
        assert accident_loader.safe_convert_int("unknown") is None

    def test_prepare_data_for_insertion(self, sample_dataframe):
        # Act
        rows = accident_loader.prepare_data_for_insertion(sample_dataframe)
        
        # Assert
        assert len(rows) == 2
        # Verify Nanterre was corrected (second row of fixture)
        assert rows[1][3] == "Nanterre"
        # Verify luminosity was corrected
        assert rows[1][4] == "Nuit sans eclairage public"