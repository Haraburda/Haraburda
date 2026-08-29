import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error

class SIOPDemandForecaster:
    def __init__(self, data: pd.DataFrame):
        self.df = data.copy()
        
    def calculate_rolling_average(self, window_size: int = 3) -> pd.DataFrame:
        self.df[f'rolling_avg_{window_size}m'] = self.df.groupby(['site_id', 'part_id'])['actual_demand'] \
                                                       .transform(lambda x: x.rolling(window=window_size, min_periods=1).mean())
        return self.df

    def calculate_exponential_smoothing(self, alpha: float = 0.3) -> pd.DataFrame:
        def ewma_calc(series):
            return series.ewm(alpha=alpha, adjust=False).mean()
            
        self.df[f'exp_smooth_forecast'] = self.df.groupby(['site_id', 'part_id'])['actual_demand'] \
                                                    .transform(ewma_calc)
        self.df[f'exp_smooth_forecast'] = self.df.groupby(['site_id', 'part_id'])['exp_smooth_forecast'].shift(1)
        return self.df

    def compute_forecast_error_metrics(self) -> dict:
        clean_df = self.df.dropna(subset=['exp_smooth_forecast'])
        if clean_df.empty:
            return {"Status": "Insufficient temporal steps to calculate error tracking vectors."}
            
        y_true = clean_df['actual_demand']
        y_pred = clean_df['exp_smooth_forecast']
        
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        total_bias = (y_pred.sum() - y_true.sum()) / y_true.sum()
        
        return {
            "Mean_Absolute_Error_Units": round(mae, 2),
            "Root_Mean_Squared_Error_Units": round(rmse, 2),
            "Forecast_Bias_Percentage": round(total_bias * 100, 2)
        }

if __name__ == "__main__":
    historical_records = {
        "month":,
        "site_id": ["SITE-A", "SITE-A", "SITE-A", "SITE-A", "SITE-B", "SITE-B", "SITE-B", "SITE-B"],
        "part_id": ["P-101", "P-101", "P-101", "P-101", "P-202", "P-202", "P-202", "P-202"],
        "actual_demand": [100, 120, 110, 130, 45, 50, 48, 55]
    }
    
    demand_df = pd.DataFrame(historical_records)
    forecaster = SIOPDemandForecaster(demand_df)
    forecaster.calculate_rolling_average(window_size=3)
    forecaster.calculate_exponential_smoothing(alpha=0.4)
    performance_metrics = forecaster.compute_forecast_error_metrics()
    
    print("=== Multi-Site Forecast Generation Matrix ===")
    print(forecaster.df.to_string(index=False))
    print("\n=== Supply Chain Network Performance KPIs ===")
    for k, v in performance_metrics.items():
        print(f"{k.replace('_', ' ')}: {v}")
