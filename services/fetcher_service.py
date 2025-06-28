import argparse
import yfinance as yf
import duckdb
from datetime import datetime
import os

def fetch_data(symbol: str, start_date: str, end_date: str) -> 'pandas.DataFrame':
    """從 yfinance API 獲取股價數據"""
    print(f"Fetching data for {symbol} from {start_date} to {end_date}...")
    df = yf.download(symbol, start=start_date, end=end_date)
    if df.empty:
        raise ValueError("No data fetched. Check symbol or date range.")
    print("Data fetched successfully.")
    return df

def save_to_duckdb(df: 'pandas.DataFrame', symbol: str, db_path: str):
    """將 DataFrame 存儲到 DuckDB 資料庫"""
    # 確保目錄存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    table_name = symbol.lower().replace('-', '_')
    print(f"Saving data to table '{table_name}' in '{db_path}'...")
    con = duckdb.connect(db_path)
    con.execute("CREATE OR REPLACE TABLE {} AS SELECT * FROM df".format(table_name))
    con.close()
    print("Data saved successfully.")

def main():
    """主執行函數，解析命令列參數並協調流程"""
    parser = argparse.ArgumentParser(description="Fetch stock data and save to DuckDB.")
    parser.add_argument("--symbol", type=str, required=True, help="Stock symbol (e.g., SPY)")
    parser.add_argument("--start-date", type=str, required=True, help="Start date in YYYY-MM-DD format")
    parser.add_argument("--db-path", type=str, required=True, help="Path to the output DuckDB file")

    args = parser.parse_args()

    # 結束日期設為今天
    end_date = datetime.now().strftime('%Y-%m-%d')

    # 1. 獲取數據
    raw_df = fetch_data(args.symbol, args.start_date, end_date)

    # 2. 儲存數據
    save_to_duckdb(raw_df, args.symbol, args.db_path)

if __name__ == "__main__":
    main()
