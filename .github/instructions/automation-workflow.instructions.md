---
applyTo: 'docs/_posts/*/*.md'
---

# 自動化 Embedding 生成工作流程

本規範定義了如何自動化處理原始文章並生成對應的 embedding 內容。

## 觸發條件

### 手動觸發
- 使用 GitHub Copilot 處理單篇文章
- 批次處理指定範圍的文章
- 更新現有 embedding 內容

### 自動觸發（未來規劃）
- 當 `docs/_posts/` 目錄有新文章時
- 當現有文章被修改時
- 定期批次更新所有 embedding 內容

## 工作流程步驟

### 步驟 1：檔案掃描和驗證
1. 掃描 `docs/_posts/{year}/` 目錄找出待處理文章
2. 檢查對應的 `_embedding/{year}/` 是否已存在
3. 比較原始檔案和 embedding 檔案的修改時間
4. 建立處理清單

### 步驟 2：內容分析和生成
對每個需要處理的檔案：
1. 讀取並解析原始文章
2. 應用 `generate-embedding.prompt.md` 規範
3. 生成結構化的 embedding 內容
4. 驗證生成內容的格式和完整性

### 步驟 3：檔案管理
1. 確保目標目錄存在（自動建立 `_embedding/{year}/`）
2. 寫入生成的 embedding 檔案
3. 更新處理記錄和統計資訊

### 步驟 4：品質檢查
1. 驗證生成檔案的格式正確性
2. 檢查是否遺漏必要的區塊
3. 確認技術術語和連結的準確性

## 批次處理規範

### 處理優先順序
1. **新增檔案**: 沒有對應 embedding 的原始文章
2. **更新檔案**: 原始文章比 embedding 新的檔案  
3. **補強檔案**: embedding 格式不完整的檔案

### 批次大小控制
- 單次處理不超過 10 篇文章（避免 API 限制）
- 長文章（>2000字）和短文章分開處理
- 複雜技術文章需要更多處理時間

### 錯誤處理
- 記錄處理失敗的檔案和原因
- 提供重試機制
- 建立錯誤報告和統計

## 目錄結構管理

### 自動建立目錄
```bash
# 確保年份目錄存在
mkdir -p "_embedding/2004"
mkdir -p "_embedding/2016"  
mkdir -p "_embedding/2024"
```

### 檔案對應檢查
```
原始檔案: _posts/2024/2024-07-15-docker-setup.md
目標檔案: _embedding/2024/2024-07-15-docker-setup.md
狀態: [新增|更新|已存在]
```

## 資料結構化存儲（可選）

為了更好的檢索和分析，可以將部分資訊存儲為結構化資料：

### Metadata 集中存儲
```yaml
# _data/embeddings/metadata/2024-07-15-docker-setup.yml
source_file: "_posts/2024/2024-07-15-docker-setup.md"
title: "Docker 環境建置指南"
keywords:
  primary: ["docker", "container", "development"]
  secondary: ["nodejs", "environment", "setup"]
tech_stack:
  languages: ["javascript"]
  tools: ["docker", "docker-compose"]
content_metrics:
  word_count: 1500
  reading_time: "7 分鐘"
  difficulty: "中級"
```

### Q&A 資料庫
```yaml  
# _data/embeddings/qa-pairs/2024-07-15-docker-setup.yml
- q: "什麼是 Docker？"
  a: "Docker 是一個開源的容器化平台..."
  category: "concept"
  
- q: "如何建立 Docker 映像檔？"  
  a: "使用 docker build 命令..."
  category: "operation"
```

## 監控和統計

### 處理統計
- 每日/週/月處理的文章數量
- 成功率和失敗率
- 平均處理時間

### 內容統計  
- 各年份文章和 embedding 的對應狀況
- 技術標籤和關鍵字的分佈
- 內容複雜度和長度分析

## 維護和優化

### 定期維護任務
- 清理格式不正確的 embedding 檔案
- 更新過時的技術資訊和連結
- 統一術語和標籤的使用

### 持續優化
- 改進關鍵字提取的準確性
- 優化摘要生成的品質
- 增強問答對的實用性

## 實作建議

### 使用 GitHub Copilot
1. 建立 workspace 設定，讓 Copilot 了解專案結構
2. 使用 prompts 目錄中的提示詞模板
3. 善用 instructions 目錄的規範檔案

### 工具整合
- VS Code 擴充套件協助檔案管理
- GitHub Actions 進行自動化處理
- 自定義腳本處理批次任務

### 品質控制
- 人工檢核關鍵內容的準確性
- 建立模板和範例供參考
- 定期審查和更新處理規範
