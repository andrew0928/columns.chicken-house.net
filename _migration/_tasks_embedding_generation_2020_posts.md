## 生成 2020 年度文章 Embedding - 2025-08-03

### 任務摘要
為 `_posts/2020/` 目錄下的所有部落格文章生成對應的 embedding 檔案，包含結構化摘要、問答對、解決方案等內容，以提升內容的可發現性和檢索性。

### 原始需求
generate embedding for _post/2020/* posts

### 處理清單
- [x] 2020-01-01-microservice13-event-sourcing.md (success)
- [x] 2020-02-09-process-pool.md (success)
- [x] 2020-03-10-interview-abstraction.md (success)
- [x] 2020-07-01-microservice14-database.md (success)
- [x] 2020-11-23-security-talk.md (success)

### 完成摘要
所有 2020 年度文章的 embedding 生成已完成，共處理 5 篇文章：
1. 微服務架構中的事件溯源模式
2. 程序池與隔離機制設計
3. 抽象化設計實戰 - 折扣規則系統
4. 微服務架構中的資料庫技術選擇
5. 資訊安全的根本思維與實作

每篇文章都已生成對應的 .md 和 .json 檔案，遵循既定的結構規範和生成原則。

### 處理原則
1. 每個檔案都需要生成對應的 `.md` 和 `.json` 檔案
2. 遵循 embedding-structure.instructions.md 的結構規範
3. 遵循 embedding-generation.instructions.md 的生成規範
4. 確保內容基於原始文章，不添加額外資訊

### 進度記錄
開始時間: 2025-08-03
完成時間: 2025-08-03

## Embedding 檔案結構升級 - 2025-08-03

### 任務摘要
針對已生成的 embedding 檔案進行結構升級，確保符合最新的 embedding-structure.instructions.md v1.1 規範。

### 處理範圍
- [x] 2020-03-10-interview-abstraction.md/.json - 重新生成 (v1.1)
- [x] 2020-11-23-security-talk.md/.json - 重新生成 (v1.1)  
- [x] 2020-07-01-microservice14-database.md/.json - 重新生成 (v1.1)

### 升級重點
1. **Front Matter 格式更新**: 加入 source_file, generated_date, version, tools, model 欄位
2. **摘要格式調整**: 改用第三人稱敘述，提升客觀性
3. **Q&A 結構優化**: 增強技術討論深度和實用性
4. **解決方案完善**: 提供具體實作範例和程式碼片段
5. **JSON 標籤標準化**: 12 個標準化標籤群組結構

### 完成檔案
1. **2020-03-10-interview-abstraction**: 抽象化設計與折扣規則系統
2. **2020-11-23-security-talk**: 資訊安全原則與思維
3. **2020-07-01-microservice14-database**: 微服務資料庫選擇策略

所有檔案已升級至 v1.1 規範，確保結構一致性和內容品質。

### 完成時間
2025-08-03 15:30:00 +0800