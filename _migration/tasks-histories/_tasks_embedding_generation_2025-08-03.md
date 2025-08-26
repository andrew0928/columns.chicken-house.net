# 批次作業任務清單

## 2019年文章 Embedding Content 生成 - 2025-08-03 14:30:00

### 原始需求
替 /docs/_posts/2019/*.md 的所有文件產生 embedding content，按照 embedding-generation.instructions.md 和 embedding-structure.instructions.md 規範。

### 參考規範檔案
- embedding-generation.instructions.md
- embedding-structure.instructions.md
- batch.instructions.md

### 處理檔案清單
- [x] 2019-01-01-microservice12-mqrpc.md (SUCCESS)
- [x] 2019-06-01-nested-query.md (SUCCESS)
- [x] 2019-06-15-netcli-pipeline.md (SUCCESS)
- [x] 2019-06-20-netcli-tips.md (SUCCESS)
- [x] 2019-07-06-pipeline-practices.md (SUCCESS)
- [x] 2019-08-30-scheduling-practices.md (SUCCESS)
- [x] 2019-12-12-home-networking.md (SUCCESS)

### 總計
總共 7 個檔案需要處理

### 處理規則
1. 每次只處理一個檔案
2. 為每個檔案在 `_embeddings/2019/` 目錄下建立對應的 embedding content (.md) 
3. 同時建立對應的 tags JSON 檔案 (.json)
4. 遵循 embedding-structure.instructions.md 的結構規範
5. 使用 embedding-generation.instructions.md 的生成流程
6. 每個檔案處理完成後更新此清單狀態

### 備註
按照 batch.instructions.md 規範，每次只處理一個檔案，完成後更新狀態再繼續下一個。
