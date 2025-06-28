import argparse
import duckdb
import os
import pandas as pd # 根據使用情況添加 pandas 導入

def load_from_duckdb(symbol: str, db_path: str) -> 'pd.DataFrame': # 修改返回類型提示
    """從 DuckDB 加載數據到 DataFrame"""
    table_name = symbol.lower().replace('-', '_')
    print(f"Loading data from table '{table_name}' in '{db_path}'...")
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found at {db_path}")

    con = duckdb.connect(db_path)
    try:
        df = con.execute(f"SELECT * FROM {table_name}").fetchdf()
    finally:
        con.close()

    if df.empty:
        raise ValueError(f"No data found in table {table_name}.")
    print("Data loaded successfully.")
    return df

def process_data(df: 'pd.DataFrame') -> 'pd.DataFrame': # 修改參數和返回類型提示
    """計算技術指標（特徵工程）"""
    print("Processing data to calculate moving averages...")
    df_processed = df.copy()
    df_processed['MA20'] = df_processed['Close'].rolling(window=20).mean()
    df_processed['MA60'] = df_processed['Close'].rolling(window=60).mean()
    print("Processing completed.")
    return df_processed.dropna() # 丟棄因移動平均計算產生的空值

def save_features_to_duckdb(df: 'pd.DataFrame', symbol: str, db_path: str): # 修改參數類型提示
    """將處理過的特徵 DataFrame 存儲到 DuckDB"""
    # 確保目錄存在，如果 db_path 包含目錄
    if os.path.dirname(db_path):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    table_name = f"{symbol.lower().replace('-', '_')}_features"
    print(f"Saving features to table '{table_name}' in '{db_path}'...")
    con = duckdb.connect(db_path)
    # 使用 df 而不是 'df' 字串來創建表格
    con.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM df")
    con.close()
    print("Features saved successfully.")

def main():
    """主執行函數，解析命令列參數並協調流程"""
    parser = argparse.ArgumentParser(description="Process raw stock data and save features.")
    parser.add_argument("--input-db", type=str, required=True, help="Path to the input raw data DuckDB file")
    parser.add_argument("--output-db", type=str, required=True, help="Path to the output features DuckDB file")
    parser.add_argument("--symbol", type=str, required=True, help="Stock symbol to process")

    args = parser.parse_args()

    # 1. 加載原始數據
    raw_df = load_from_duckdb(args.symbol, getattr(args, 'input-db')) # 使用 getattr 處理帶有 '-' 的參數名稱

    # 2. 處理數據
    features_df = process_data(raw_df)

    # 3. 儲存特徵
    save_features_to_duckdb(features_df, args.symbol, getattr(args, 'output-db')) # 使用 getattr

if __name__ == "__main__":
    main()
