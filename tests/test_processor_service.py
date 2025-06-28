from services.processor_service import process_data
import pandas as pd # 根據 conftest.py 的 mock_raw_data 和 process_data 的返回類型添加
import numpy as np # 用於 np.isclose 進行浮點數比較

# conftest.py 中的 mock_raw_data fixture 會被 pytest 自動發現和注入

def test_process_data(mock_raw_data: pd.DataFrame): # 添加類型提示
    """
    測試 process_data 函數是否能正確計算移動平均線。
    - mock_raw_data: 來自 conftest.py 的假數據。
    """
    # 執行待測函數
    processed_df = process_data(mock_raw_data)

    # 驗證結果
    # 1. 檢查新的欄位是否存在
    assert 'MA20' in processed_df.columns
    assert 'MA60' in processed_df.columns

    # 2. 檢查因 dropna() 導致的行數減少
    # 由於 MA60 需要 60 個數據點，前 59 行會是 NaN，dropna() 會移除它們
    assert len(processed_df) == len(mock_raw_data) - 59

    # 3. 抽樣檢查計算是否正確
    # 檢查最後一筆 MA20 是否等於原始數據 (dropna 前的) 最後 20 筆 'Close' 的平均值
    # 注意：mock_raw_data 是未經 dropna 處理的原始數據模擬
    # process_data 內部會 dropna，所以我們比較的是基於原始數據計算的 MA

    # 重新計算 mock_raw_data 的 MA20 和 MA60 以進行比較
    # 因為 process_data 內部的 dropna 是基於所有 NaN 值，
    # 而不僅僅是 MA60 產生的 NaN。如果 MA20 在某些點也是 NaN (雖然在這個 mock 中不太可能，因為窗口小於數據長度)
    # dropna() 會一併移除。

    # 為了精確比較，我們在 mock_raw_data 上計算 MA，然後取與 processed_df 對應的部分
    temp_df_for_ma_calculation = mock_raw_data.copy()
    temp_df_for_ma_calculation['MA20_expected'] = temp_df_for_ma_calculation['Close'].rolling(window=20).mean()
    temp_df_for_ma_calculation['MA60_expected'] = temp_df_for_ma_calculation['Close'].rolling(window=60).mean()

    # 取 MA60 計算後非 NaN 的部分，這與 processed_df 的索引應該對應
    # MA60 窗口為 60，所以前 59 個值為 NaN
    valid_expected_ma_df = temp_df_for_ma_calculation.iloc[59:]

    # 檢查最後一筆 MA20
    # actual_ma20 是 processed_df (已經 dropna) 的最後一筆 MA20
    actual_ma20 = processed_df['MA20'].iloc[-1]
    # expected_ma20 是在原始數據上計算的 MA20，並且對應到 processed_df 的最後一個索引
    expected_ma20 = valid_expected_ma_df['MA20_expected'].iloc[-1]
    assert np.isclose(actual_ma20, expected_ma20), f"MA20 mismatch: Actual {actual_ma20}, Expected {expected_ma20}"

    # 檢查最後一筆 MA60
    actual_ma60 = processed_df['MA60'].iloc[-1]
    expected_ma60 = valid_expected_ma_df['MA60_expected'].iloc[-1]
    assert np.isclose(actual_ma60, expected_ma60), f"MA60 mismatch: Actual {actual_ma60}, Expected {expected_ma60}"

    # 也可以檢查某個特定點（例如 processed_df 的第一行，它對應原始數據的第 60 行，索引 59）
    # processed_df.iloc[0] 對應於 mock_raw_data.iloc[59] 計算出的 MA 值

    first_valid_actual_ma20 = processed_df['MA20'].iloc[0]
    first_valid_expected_ma20 = valid_expected_ma_df['MA20_expected'].iloc[0] # mock_raw_data['Close'].iloc[40:60].mean()
    assert np.isclose(first_valid_actual_ma20, first_valid_expected_ma20)

    first_valid_actual_ma60 = processed_df['MA60'].iloc[0]
    first_valid_expected_ma60 = valid_expected_ma_df['MA60_expected'].iloc[0] # mock_raw_data['Close'].iloc[0:60].mean()
    assert np.isclose(first_valid_actual_ma60, first_valid_expected_ma60)
