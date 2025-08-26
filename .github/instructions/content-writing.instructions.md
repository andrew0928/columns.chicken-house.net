---
applyTo: 'docs/_posts/*/*.md'
---

# 部落格內容撰寫規範

## 文章結構規範

### 標題層級
使用標準的 Markdown 標題層級：
```markdown
# 文章主標題（自動從 front matter 生成，不要在內文重複）
## 主要段落標題 (H2)
### 子段落標題 (H3)  
#### 細節說明 (H4)
```

### 建議文章架構
```markdown
## 前言/背景
- 說明文章動機和背景
- 定義問題或需求

## 主要內容
### 方法/概念說明
### 實作步驟/範例
### 進階應用

## 總結
- 重點整理
- 延伸思考
- 相關資源

## 參考資源
- 官方文件連結
- 相關文章連結
```

## 內容撰寫原則

### 1. 開頭引導
- 在文章開頭簡潔說明讀者將學到什麼
- 提及適用的技術背景或前置知識
- 預告文章的主要價值

### 2. 技術內容規範
- **程式碼區塊**：必須指定語言類型
  ```csharp
  // C# 範例
  public class Example {
      // 程式碼內容
  }
  ```

- **指令操作**：使用 bash 或適當的 shell 類型
  ```bash
  # 安裝相依套件
  npm install express
  ```

- **設定檔案**：指定正確的檔案類型
  ```yaml
  # docker-compose.yml
  version: '3.8'
  services:
    app:
      image: node:16
  ```

### 3. 圖片和多媒體
- 圖片放置在 `/wp-content/images/{year}-{month}-{day}-{post-slug}/` 目錄
- 檔名使用 `image-{sequence}.{ext}` 格式
- 必須提供 alt 文字描述
- 範例：`![Docker 容器架構圖](/wp-content/images/2024-08-02-docker-setup/image-1.png)`

### 4. 連結規範
- **內部連結**：使用站內的絕對路徑，格式 `[文字](/yyyy/mm/dd/post-title/)`
- **外部連結**：使用完整 URL，重要連結建議標示為新視窗開啟
- **錨點連結**：同頁內跳轉使用 `[文字](#section-id)`


## 特殊內容處理

### 系列文章
- 在 front matter 中標示 series
- 在文章開頭或結尾加入系列導航
- 使用統一的標籤和分類

### 更新和修正
- 重大更新在文章開頭加入更新說明
- 過時內容加入警告提示
- 保留原始發布日期，另外標示最後更新時間

### 程式碼範例
- 提供完整可執行的範例
- 重要檔案提供完整路徑
- 複雜設定提供 GitHub 專案連結

## 語言和風格

### 中文撰寫規範
- 使用繁體中文
- 專業術語優先使用英文（如：Docker、Kubernetes）
- 中英文之間加入適當空格

### 術語使用
- 建立並維護術語表的一致性
- 第一次出現的縮寫要完整說明
- 重要概念提供簡潔定義

## 範例模板

```markdown
---
layout: post
title: "如何使用 Docker 建立 Node.js 開發環境"
published: true
date: 2024-08-02 10:00:00 +0800
tags: 
  - docker
  - nodejs
  - development-environment
categories:
  - development
excerpt: "完整介紹使用 Docker 建立 Node.js 開發環境的步驟，包含資料庫整合和 Docker Compose 設定。"
---

## 前言

在現代軟體開發中，環境一致性是確保專案順利進行的關鍵因素。本文將介紹如何使用 Docker 建立標準化的 Node.js 開發環境。

讀者將學會：
- Docker 容器化 Node.js 應用程式
- 使用 Docker Compose 整合資料庫
- 設定開發環境的最佳實踐

## 環境準備

### 安裝需求
- Docker Desktop 4.0+
- Node.js 16+ （本機測試用）
- Visual Studio Code（建議）

### 專案結構
```
project/
├── docker-compose.yml
├── Dockerfile
├── package.json
└── src/
    └── app.js
```

## 實作步驟

### 建立 Dockerfile
```dockerfile
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

[繼續詳細步驟...]

## 總結

透過 Docker 容器化，我們實現了：
- 開發環境的標準化
- 團隊協作的一致性  
- 部署流程的簡化

## 參考資源
- [Docker 官方文件](https://docs.docker.com/)
- [Node.js 最佳實踐](/2024/01/15/nodejs-best-practices/)
```
