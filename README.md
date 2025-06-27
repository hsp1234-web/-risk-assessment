# 全景市場分析儀 (Panoramic Market Analyzer)

本專案旨在建立一個半自動化的 AI 輔助交易策略研究系統。其核心任務是整合以「週」為單位的質化市場評論與跨越多個資產類別的量化市場數據，最終產出一份結構化、資訊豐富的「分析任務文本 (Prompt)」，以供大型語言模型 (LLM) 進行深度策略分析。

系統設計遵循增量處理、數據豐富度與效率平衡、以及系統穩健性的核心理念。

## 功能特性

*   **自動化報告處理**：掃描輸入資料夾中的市場評論週報 (特定檔名格式)。
*   **增量更新**：僅處理新的或內容已修改的報告檔案，避免重複勞動 (基於 SHA-256 雜湊值)。
*   **多源數據整合**：
    *   從 `yfinance` 獲取股票、ETF、指數、外匯等市場數據。
    *   從 `FRED (Federal Reserve Economic Data)` 獲取宏觀經濟指標數據 (無需 API 金鑰，透過直接 CSV 下載)。
    *   特別處理台指期貨，構建向後調整的連續近月合約數據。
*   **穩健的數據獲取**：
    *   內建客戶端快取 (`requests-cache`)，大幅減少重複的 API/數據請求，並在網路中斷時提供數據。快取檔案儲存於 `CACHE_Market_Data/`。
    *   實現延遲、抖動及指數退避重試機制，優雅處理網路波動和潛在的速率限制。
*   **結構化 Prompt 生成**：將質化評論與獲取的量化數據整合成結構清晰的文本檔案，儲存於 `OUT_Processed_Prompts/`，專為大型語言模型設計。
*   **AI 研究考量**：生成的 Prompt 中包含對後續 AI 數據預處理（缺失值、異常值、特徵工程等）的初步建議。

## 專案結構

```
.
├── IN_Source_Reports/          # 放置輸入的市場評論週報 (.txt 格式)
├── OUT_Processed_Prompts/      # 儲存處理完成後生成的分析任務文本 (.txt)
│   └── processed_files_manifest.json # 已處理檔案的清單與其雜湊值
├── CACHE_Market_Data/          # 儲存 yfinance 和 FRED 數據的快取檔案 (.sqlite)
├── file_utils.py               # 檔案處理、雜湊計算、manifest 管理工具
├── market_data_yfinance.py     # yfinance 數據獲取與處理模組 (含台指期貨、選擇權檢查)
├── market_data_fred.py         # FRED 經濟數據獲取模組 (無金鑰)
├── main_analyzer.py            # 主執行腳本，協調所有處理流程
├── requirements.txt            # Python 套件依賴列表
└── README.md                   # 本檔案
```

## 設定與執行

### 1. 環境準備

*   確保已安裝 Python (建議 3.9 或更高版本)。
*   克隆本專案或下載原始碼。

### 2. 安裝依賴套件

在專案根目錄下，執行以下命令安裝必要的 Python 套件：
```bash
pip install -r requirements.txt
```
主要依賴套件包括：`yfinance`, `requests-cache`, `pandas`, `requests`。

### 3. 準備輸入報告

*   將您的市場評論週報 (純文字 `.txt` 檔案) 放入 `IN_Source_Reports/` 資料夾。
*   **檔名格式要求**：檔名中必須包含年份和週數，格式為 `...YYYY年第WW週...txt`。
    *   `YYYY` 代表四位數年份 (例如 `2023`)。
    *   `WW` 代表一或兩位數的週數 (例如 `5` 或 `05` 或 `52`)。
    *   範例：
        *   `市場週評_2023年第5週_內部摘要.txt`
        *   `My Analysis for 2024年第18週.txt`
*   檔案內容應為 UTF-8 編碼。

### 4. 執行分析儀

在專案根目錄下，執行主腳本：
```bash
python main_analyzer.py
```

### 5. 檢查輸出

*   處理完成後，生成的「分析任務文本 (Prompt)」檔案會位於 `OUT_Processed_Prompts/` 資料夾中。
*   `OUT_Processed_Prompts/processed_files_manifest.json` 記錄了已處理的輸入檔案及其狀態。
*   日誌會輸出到控制台，顯示詳細的處理過程、數據獲取情況及任何潛在的錯誤或警告。
*   `CACHE_Market_Data/` 資料夾中會產生 `yfinance_cache.sqlite` 和 `fred_data_cache.sqlite` 等快取檔案。首次執行時，由於需要從網路獲取數據，耗時可能較長。後續執行因有快取會顯著加快。

## 數據獲取說明

*   **yfinance**：用於獲取股票、ETF、指數、外匯和台指期貨數據。請注意，`yfinance` 並非 Yahoo Finance 的官方 API，其穩定性可能受 Yahoo 網站結構變更影響。
*   **FRED (Federal Reserve Economic Data)**：用於獲取 VIXCLS (VIX 收盤價)、DGS10 (10年期美債殖利率)、FEDFUNDS (聯邦基金利率) 等經濟指標。本專案採用無需 API 金鑰的方式，直接從 FRED 網站下載 CSV 數據。
*   **台指期貨 (TAIFEX)**：系統會嘗試構建向後調整的連續近月合約數據。由於 `yfinance` 不直接提供此類標準化數據，其準確性依賴於各月份合約數據的可用性和調整邏輯的嚴謹性。
*   **台指選擇權 (TXO)**：`yfinance` **無法** 提供台指選擇權的歷史每日 OCHLV (開高低收量) 或希臘字母數據。它主要提供選擇權鏈的當前市場快照。任何需要詳細選擇權歷史數據的 AI 研究，都必須尋求 **TAIFEX 官方數據**（網站下載或付費購買）或**專業的商業數據提供商**。此提醒已整合到系統日誌和生成的 Prompt 中。

## AI 研究與數據考量 (於 Prompt 中提供)

生成的 Prompt 文本末尾包含一個「AI 研究與數據考量」小節，為後續使用大型語言模型進行分析時提供數據處理建議，包括：
*   數據儲存建議 (Parquet/CSV)
*   缺失值處理策略
*   異常值處理方法
*   數據標準化/歸一化需求
*   特徵工程思路

## 注意事項與限制

*   **網路連線**：首次運行或處理新報告（對應新的日期範圍）時，需要穩定的網路連線來獲取量化數據。
*   **數據準確性與延遲**：本專案依賴的免費數據源 (尤其是 `yfinance`) 可能存在數據延遲或不準確的情況。對於高度依賴即時性和精確性的交易決策，請務必謹慎使用並考慮付費數據源。
*   **錯誤處理**：系統已包含錯誤處理和重試機制，但對於某些特定 API 返回的非標準錯誤，可能仍需進一步完善。請留意控制台日誌輸出。
*   **資源消耗**：處理大量歷史報告或非常長的時間跨度時，可能會消耗較多時間和記憶體。

## 未來可能的改進方向

*   引入更正式的單元測試框架 (如 `pytest`)。
*   提供將獲取的量化數據直接儲存為 Parquet 或 CSV 檔案的選項。
*   整合更多無金鑰的公開數據源 (如部分政府統計數據 API)。
*   允許使用者更靈活地配置要獲取的金融商品列表和數據區間。
*   若有需求，可加入對專業時序資料庫 (如 TimescaleDB, InfluxDB) 的支援。

---

## API 深度測試與報告

本專案包含一個進階的 API 測試腳本 `api_deep_tester.py`，用於對所有集成的金融 API（包括 `yfinance`、付費 API 和免費公開 API）進行更詳細的功能探索和壓力測試。

### 執行深度測試

1.  **配置 API 金鑰**：確保您已在專案根目錄下創建了 `.env` 檔案，並填入了所有必要的 API 金鑰（詳見各 API 官方文檔以獲取金鑰，部分金鑰已在開發過程中由指揮官提供）。`api_deep_tester.py` 會從此檔案讀取金鑰。
    ```dotenv
    # .env 檔案範例
    FRED_API_KEY="YOUR_FRED_KEY"
    ALPHA_VANTAGE_API_KEY="YOUR_ALPHA_VANTAGE_KEY"
    FINNHUB_API_KEY="YOUR_FINNHUB_KEY" # 如果您有金鑰並希望測試
    NEWS_API_KEY="YOUR_NEWSAPI_KEY"
    FMP_API_KEY="YOUR_FMP_KEY"
    POLYGON_API_KEY="YOUR_POLYGON_KEY"
    # BEA_API_KEY="YOUR_BEA_USER_ID" # BEA API 需要 UserID
    ```

2.  **運行測試腳本**：
    ```bash
    python api_deep_tester.py
    ```
    **注意**：此腳本會對多個 API 進行大量請求，可能需要較長時間才能完成，並且可能會消耗您 API 金鑰的每日/每月請求配額。請謹慎執行，特別是對於有嚴格免費限制的 API。建議在開發和評估階段使用。

### 查閱測試報告

*   執行完畢後，詳細的測試報告將以 `.txt` 格式儲存在本專案的 `test_reports/` 資料夾中。
*   檔名格式為 `api_deep_test_report_YYYYMMDD_HHMMSS.txt`（包含執行時的時間戳）。
*   報告內容使用繁體中文，包含了對每個 API 的以下測試結果：
    *   連通性狀態。
    *   可查詢數據的大致範圍或查找方法。
    *   支持的時間週期（分鐘、小時、日、週、月等）及其限制。
    *   可獲取的歷史數據長度。
    *   API 主要返回的數據格式。
    *   速率限制的初步觀察結果。
    *   `yfinance` 的時間週期降級策略和速率限制緩解機制的詳細測試。
    *   測試過程中遇到的錯誤和警告。

這份報告可以幫助您了解各 API 的實際能力和限制，為「全景市場分析儀」的數據源選擇和使用策略提供參考。

---
指揮官，請審閱此 README 檔案。
