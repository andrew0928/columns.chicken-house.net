---
applyTo: 'docs/_posts/*/*.md'
---

# Jekyll Metadata 規範

## Front Matter 基本結構

所有部落格文章的 front matter 必須包含以下基本欄位：

```yaml
---
layout: post
title: "文章標題"
published: true
date: YYYY-MM-DD HH:MM:SS +0800
tags: 
  - tag1
  - tag2
categories:
  - category1
excerpt: "文章摘要，建議 100-200 字"
---
```

## 必要欄位說明

### 基本欄位
- `layout`: 固定使用 `post`
- `title`: 文章標題，使用雙引號包覆
- `published`: 布林值，控制文章是否發布
- `date`: 發布日期時間，格式 `YYYY-MM-DD HH:MM:SS +0800`
- `tags`: 標籤陣列，每個標籤獨立一行
- `categories`: 分類陣列，通常只有一個主分類
- `excerpt`: 文章摘要，用於首頁和 RSS feed

### 可選欄位
- `series`: 系列文章標識，例如 `"TDD 系列"`
- `image`: 文章封面圖片路徑
- `redirect_from`: 舊網址重新導向
- `permalink`: 自訂永久連結（不建議使用）

## 標籤和分類規範

### 標籤 (Tags)
- 使用小寫英文，多個單字用 `-` 連接
- 技術標籤優先使用官方名稱：`asp-net`, `docker`, `azure`
- 概念標籤使用通用術語：`architecture`, `testing`, `devops`
- 避免過度細分，控制在 3-5 個標籤內

### 分類 (Categories)  
- 使用主要技術領域分類
- 建議分類：`development`, `architecture`, `devops`, `tools`, `thoughts`
- 每篇文章只使用一個主分類

## 範例

```yaml
---
layout: post
title: "使用 Docker 建立 ASP.NET Core 開發環境"
published: true
date: 2024-07-15 10:30:00 +0800
tags: 
  - docker
  - asp-net-core
  - development-environment
categories:
  - development
series: "容器化開發系列"
excerpt: "介紹如何使用 Docker 快速建立 ASP.NET Core 開發環境，包含資料庫和相依服務的完整配置。"
image: "/assets/images/2024/docker-aspnet-setup.png"
---
```
