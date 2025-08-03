---
applyTo: '_embedding/*/*.md'
---

# 生成內容 (Embedding) 結構規範

## 檔案結構

生成內容檔案必須遵循以下結構：

```yaml
---
source_file: "_posts/YYYY/YYYY-MM-DD-title.md"
generated_date: "YYYY-MM-DD HH:MM:SS +0800"
version: "1.0"
tools:
  - github_copilot
  - claude_sonnet_3_5
model: "claude-3-5-sonnet-20241022"
---

# {原始文章標題} - 生成內容

## 原始 Metadata
[從原始文章的 front matter 複製]

## 擴增 Metadata
[自動分析生成的額外資訊]

## 摘要 (Summaries)
[文章和段落層級摘要]

### 段落摘要1 (Section Summaries)
[每個段落的核心內容摘要]

### 段落摘要2 (Section Summaries)
[每個段落的核心內容摘要]

### 段落摘要 (Section Summaries)
[每個段落的核心內容摘要]

## 問答集 (Q&A Pairs)
[從內容提取的問答配對]

### Q1, [問題標題]
Q: [問題內容]
A: [回答內容]

### Q2, [問題標題]
Q: [問題內容]
A: [回答內容]

### Q3, [問題標題]
Q: [問題內容]
A: [回答內容]


## 解決方案 (Solutions)
[從內容整理的問題解決方案]

### P1, [問題標題]
Problem: [問題描述]
Root Cause: [問題根本原因]
Solution: [解決方案描述]
Example: [相關指令或程式碼片段]

### P2, [問題標題]
Problem: [問題描述]
Root Cause: [問題根本原因]
Solution: [解決方案描述]
Example: [相關指令或程式碼片段]

### P3, [問題標題]
Problem: [問題描述]
Root Cause: [問題根本原因]
Solution: [解決方案描述]
Example: [相關指令或程式碼片段]



```

## 各區塊詳細規範

### 1. 原始 Metadata
完整複製原始文章的 front matter，保持原始格式。

```yaml
## 原始 Metadata

```yaml
layout: post
title: "原始標題"
published: true
date: 2024-07-15 10:30:00 +0800
tags: 
  - tag1
  - tag2
categories:
  - category1
excerpt: "原始摘要"
```

### 2. 擴增 Metadata
系統自動分析生成的額外資訊：

```yaml
## 擴增 Metadata

### 自動識別關鍵字
keywords:
  primary:
    - 核心關鍵字1
    - 核心關鍵字2
  secondary:
    - 次要關鍵字1
    - 次要關鍵字2

### 技術堆疊分析
tech_stack:
  languages:
    - C#
    - JavaScript
  frameworks:
    - ASP.NET Core
    - React
  tools:
    - Docker
    - Visual Studio
  platforms:
    - Azure
    - Linux

### 參考資源
references:
  internal_links:
    - /2024/01/01/related-post/
  external_links:
    - https://docs.microsoft.com/...
  mentioned_tools:
    - Visual Studio Code
    - Git

### 內容特性
content_metrics:
  word_count: 1500
  reading_time: "7 分鐘"
  difficulty_level: "中級"
  content_type: "教學"  # 教學/心得/評論/工具介紹
```

### 3. 摘要 (Summaries)
提供多層級摘要：

```markdown
## 摘要 (Summaries)

### 文章摘要 (Article Summary)
用 8-10 行、約 500 字的完整段落概括整篇文章的核心內容和價值。
應包含文章的主要觀點、技術重點、實作成果、以及對讀者的價值。
摘要應該讓讀者能夠快速理解整篇文章的精髓，並判斷是否需要深入閱讀。
使用第三人稱「作者」來描述文章內容，保持客觀的敘述角度。

### 關鍵要點 (Key Points)
- 要點 1：簡潔描述主要概念
- 要點 2：重要的實作細節
- 要點 3：需要注意的限制或建議

### 段落摘要 (Section Summaries)
1. **段落標題 1**：用 8-10 行、約 500 字的完整段落摘要該段落的核心內容，包含主要概念、技術細節、實作重點和關鍵洞察。應詳細說明該段落在整體文章中的作用和價值。使用第三人稱「作者」來描述。

2. **段落標題 2**：用 8-10 行、約 500 字的完整段落摘要該段落的核心內容，包含主要概念、技術細節、實作重點和關鍵洞察。應詳細說明該段落在整體文章中的作用和價值。使用第三人稱「作者」來描述。

3. **段落標題 3**：用 8-10 行、約 500 字的完整段落摘要該段落的核心內容，包含主要概念、技術細節、實作重點和關鍵洞察。應詳細說明該段落在整體文章中的作用和價值。使用第三人稱「作者」來描述。
```

## 版本控制規範

當原始文章更新或指令規範變更時，需要更新版本資訊：
- 更新 `version` 欄位（例如：1.0 → 1.1 → 2.0）
- 在文件末尾附加版本變更記錄

```markdown
## Version Changes
- v1.1 (YYYY-MM-DD): 修正摘要格式，改用第三人稱敘述
- v1.0 (YYYY-MM-DD): 初始版本
```

### 4. 問答對 (Q&A Pairs)
從文章內容提取的問答配對：

```markdown
## 問答對 (Q&A Pairs)

### 基礎概念類
**Q1**: 什麼是 Docker？
**A1**: Docker 是一個開源的容器化平台...

**Q2**: 為什麼要使用容器化？
**A2**: 容器化提供了環境一致性...

### 實作操作類
**Q3**: 如何建立 Docker 映像檔？
**A3**: 使用 `docker build` 命令...

**Q4**: 如何設定環境變數？
**A4**: 在 Dockerfile 中使用 ENV 指令...

### 問題排除類
**Q5**: 遇到權限問題怎麼解決？
**A5**: 可以嘗試以下幾種方法...
```

### 5. 解決方案 (Solutions)
整理文章中提到的各種問題解決方案：

```markdown
## 解決方案 (Solutions)

### 問題：開發環境不一致
**情境**：團隊成員使用不同作業系統，導致開發環境差異
**解決方案**：
- 使用 Docker 容器統一開發環境
- 建立標準化的 docker-compose.yml
- 提供環境設定腳本

**相關指令**：
```bash
docker-compose up -d
docker exec -it app bash
```

### 問題：部署流程複雜
**情境**：手動部署容易出錯且耗時
**解決方案**：
- 建立 CI/CD 流水線
- 使用基礎設施即程式碼
- 自動化測試和部署

**相關工具**：GitHub Actions, Azure DevOps
```

## 檔案命名規範

生成內容檔案命名必須與原始文章一致：
- 原始：`_posts/2024/2024-07-15-docker-aspnet-setup.md`
- 生成：`_embedding/2024/2024-07-15-docker-aspnet-setup.md`

## 更新機制

當原始文章更新時，生成內容也應該重新產生：
- 更新 `generated_date` 欄位
- 增加 `version` 版本號
- 保留歷史版本的重要資訊
