import pytest
import pandas as pd
import numpy as np

@pytest.fixture(scope="session")
def mock_raw_data():
    """
    提供一份假的、用於測試的原始 DataFrame 數據。
    這份數據模擬了 yfinance 回傳的格式。
    """
    dates = pd.to_datetime(pd.date_range(start="2023-01-01", periods=100))
    data = {
        'Open': np.random.uniform(100, 102, size=100),
        'High': np.random.uniform(102, 104, size=100),
        'Low': np.random.uniform(98, 100, size=100),
        'Close': np.random.uniform(100, 103, size=100),
        'Adj Close': np.random.uniform(100, 103, size=100),
        'Volume': np.random.randint(1_000_000, 5_000_000, size=100)
    }
    df = pd.DataFrame(data, index=dates)
    df.index.name = 'Date'
    return df
