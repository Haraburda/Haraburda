import pandas as pd
import numpy as np
import pytest
# Imports the core dashboard logic to validate calculations during CI/CD checks
from demand_sensing.forecast_engine import SIOPDemandForecaster

@pytest.fixture
def mock_erp_inventory_data():
    data = {
        "part_id": ["P-101", "P-102", "P-103", "P-104"],
        "site_id": ["SITE-A", "SITE-A", "SITE-B", "SITE-C"],
        "quantity_on_hand":,
        "unit_cost": [45.50, 120.00, 12.75, 310.00],
        "lead_time_days": [14, 30, 7, 45]
    }
    return pd.DataFrame(data)

@pytest.fixture
def mock_historical_demand_data():
    # Provides a structured sequence to test forecasting bounds
    data = {
        "month":,
        "site_id": ["SITE-A", "SITE-A", "SITE-A", "SITE-A", "SITE-B", "SITE-B", "SITE-B", "SITE-B"],
        "part_id": ["P-101", "P-101", "P-101", "P-101", "P-202", "P-202", "P-202", "P-202"],
        "actual_demand": [100, 120, 110, 130, 45, 50, 48, 52]
    }
    return pd.DataFrame(data)

# --- Original ERP Layer Tests ---
def test_inventory_non_negative(mock_erp_inventory_data):
    assert (mock_erp_inventory_data["quantity_on_hand"] >= 0).all()

def test_critical_fields_not_null(mock_erp_inventory_data):
    assert mock_erp_inventory_data["part_id"].notnull().all()
    assert mock_erp_inventory_data["site_id"].notnull().all()

def test_lead_time_bounds(mock_erp_inventory_data):
    assert (mock_erp_inventory_data["lead_time_days"] > 0).all()
    assert (mock_erp_inventory_data["lead_time_days"] <= 365).all()

# --- New Mathematical Engine Layer Tests ---
def test_forecast_rolling_average(mock_historical_demand_data):
    forecaster = SIOPDemandForecaster(mock_historical_demand_data)
    result_df = forecaster.calculate_rolling_average(window_size=3)
    
    assert f'rolling_avg_3m' in result_df.columns
    # Verifies that values are mathematically bounded and not returning empty arrays
    assert not result_df[f'rolling_avg_3m'].isna().all()

def test_forecast_metrics_structure(mock_historical_demand_data):
    forecaster = SIOPDemandForecaster(mock_historical_demand_data)
    forecaster.calculate_exponential_smoothing(alpha=0.4)
    metrics = forecaster.compute_forecast_error_metrics()
    
    # Ensures the pipeline metrics dictionary structure hasn't changed
    expected_keys = ["Mean_Absolute_Error_Units", "Root_Mean_Squared_Error_Units", "Forecast_Bias_Percentage"]
    for key in expected_keys:
        assert key in metrics
        assert isinstance(metrics[key], float)

def test_insufficient_data_handling():
    # Verifies the engine gracefully handles empty datasets without a crash dump
    empty_df = pd.DataFrame(columns=["month", "site_id", "part_id", "actual_demand"])
    forecaster = SIOPDemandForecaster(empty_df)
    metrics = forecaster.compute_forecast_error_metrics()
    
    assert metrics == {"Status": "Insufficient data"}
