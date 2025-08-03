# 批次作業任務清單

## 2018年文章 Embedding Content 生成 - 2025-08-03 13:35:00

### 原始需求
替 /docs/_posts/2018/*.md 的所有文件產生 embedding content，按照 embedding-generation.instructions.md 和 embedding-structure.instructions.md 規範。

### 處理檔案清單
- [x] 2018-03-25-interview01-transaction.md (success)
- [x] 2018-04-01-interview02-stream-statistic.md (success)
- [x] 2018-05-10-tips-handle-shutdown-event.md (success)
- [x] 2018-05-12-msa-labs2-selfhost.md (success)
- [x] 2018-06-10-microservice10-throttle.md (success)
- [x] 2018-07-28-labs-LCOW-volume.md (success)
- [x] 2018-10-10-microservice11-devopsdays-servicediscovery.md
- [x] 2018-12-12-microservice11-lineup.md

### 總計
總共 8 個檔案需要處理

### 處理規則
1. 每次只處理一個檔案
2. 為每個檔案在 `_embeddings/2018/` 目錄下建立對應的 embedding content
3. 遵循 embedding-structure.instructions.md 的結構規範
4. 使用 embedding-generation.instructions.md 的生成流程
