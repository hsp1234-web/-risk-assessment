#!/bin/bash

# 當任何指令失敗時，立即終止腳本
set -e

# --- 環境設定 ---
# 讓 Python 能夠找到 'services' 目錄下的模組
export PYTHONPATH=$(pwd)
echo "PYTHONPATH set to: $PYTHONPATH"

# --- 參數定義 ---
SYMBOL="SPY"
RAW_DB_PATH="data/raw_data.db"
FEATURES_DB_PATH="data/features.db"
START_DATE="2023-01-01"

# --- 清理舊數據 ---
echo "Cleaning up old database files..."
rm -f $RAW_DB_PATH
rm -f $FEATURES_DB_PATH

# --- 步驟一：執行數據獲取服務 ---
echo "--- Running Fetcher Service ---"
python -m services.fetcher_service \
    --symbol $SYMBOL \
    --start-date $START_DATE \
    --db-path $RAW_DB_PATH

echo "Fetcher Service completed. Raw data saved to $RAW_DB_PATH"

# --- 步驟二：執行數據處理服務 ---
echo "--- Running Processor Service ---"
python -m services.processor_service \
    --input-db $RAW_DB_PATH \
    --output-db $FEATURES_DB_PATH \
    --symbol $SYMBOL

echo "Processor Service completed. Features saved to $FEATURES_DB_PATH"

# --- 流程結束 ---
echo "Pipeline executed successfully!"
