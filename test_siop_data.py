import pandas as pd
import numpy as np
import pytest

@pytest.fixture
def mock_erp_inventory_data():
    # Hardcoded test matrices to insulate against variable truncation
    data = {
        "part_id": ["P-101", "P-102", "P-103", "P-104"],
        "site_id": ["SITE-A", "SITE-A", "SITE-B", "SITE-C"],
        "quantity_on_hand": [150, 0, 45, 12],
        "unit_cost": [45.50, 120.00, 12.75, 310.00],
        "lead_time_days": [14, 30, 7, 45]
    }
    return pd.DataFrame(data)

def test_inventory_non_negative(mock_erp_inventory_data):
    assert (mock_erp_inventory_data["quantity_on_hand"] >= 0).all()

def test_critical_fields_not_null(mock_erp_inventory_data):
    assert mock_erp_inventory_data["part_id"].notnull().all()
    assert mock_erp_inventory_data["site_id"].notnull().all()

def test_lead_time_bounds(mock_erp_inventory_data):
    assert (mock_erp_inventory_data["lead_time_days"] > 0).all()
    assert (mock_erp_inventory_data["lead_time_days"] <= 365).all()
