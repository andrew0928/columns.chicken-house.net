---
- source_file: /docs/_posts/2024/2024-12-12-permission-design.md
- tools: BlogIndex.SyncPost 1.0.0
- model: o3, endpot: https://app-azureopenai.openai.azure.com/
---
# (TBD) 權限管理機制的設計

## Metadata
```yaml
# 原始 Front Matter:
layout: post
title: "(TBD) 權限管理機制的設計"
categories:
- "系列文章: 架構師的修練"
tags: ["系列文章", "架構師的修練", "架構師觀點", "刻意練習", "抽象化"]
published: false
comments_disqus: false
comments_facebook: false
comments_gitalk: false
redirect_from:
logo: 

# 自動識別關鍵字:
primary-keywords:
  - 權限管理
  - RBAC
  - ABAC
  - PBAC
  - Tag-Based Filter
  - 向量資料庫
  - RAG
  - Microsoft Kernel Memory
secondary-keywords:
  - Azure AI Search
  - Qdrant
  - Pinecone
  - Record-Level Permission
  - Metadata
  - 檢索安全
  - 相似性搜尋
  - 部門／角色授權

# 技術堆疊分析:
tech_stack:
  languages:
    - C#
  frameworks:
    - .NET
    - Microsoft Kernel Memory
  tools:
    - Azure AI Search
    - Qdrant
    - Pinecone
  platforms:
    - Azure
  concepts:
    - Retrieval-Augmented Generation (RAG)
    - Vector Database
    - Tag-Based Security Filter
    - RBAC / ABAC / PBAC

# 參考資源:
references:
  internal_links: []
  external_links:
    - https://github.com/microsoft/kernel-memory/blob/main/docs/security/security-filters.md
    - https://learn.microsoft.com/azure/ai-search/
    - https://qdrant.tech/
    - https://www.pinecone.io/
  mentioned_tools:
    - Microsoft Kernel Memory
    - Azure AI Search
    - Qdrant
    - Pinecone
    - Relational DB
    - NoSQL DB

# 內容特性:
content_metrics:
  word_count: 1200
  reading_time: "5 分鐘"
  difficulty_level: "中階"
  content_type: "技術文章草稿"
```

## 文章摘要
作者以在 .NET Conf 分享 RAG 經驗為開場，聚焦「向量資料庫缺乏 record-level 權限」這一常被忽視的問題。透過 Microsoft Kernel Memory 官方文件所提出的「Tags + Filter」策略，文章說明如何在不改變向量索引效能的前提下，仍能滿足部門、角色甚至個人層級的敏感資料控管需求。首先，作者拆解「大量文件＋多角色」組合帶來的爆炸性複雜度，透過 RBAC（角色式）、ABAC（屬性式）與 PBAC（原則式）三種模型逐步比較授權維度。接着以「100 人 × 5000 文件」為例展示：若把「人」歸類成 5 角色、「文件」分 20 類別，再將可讀規則下沉到一張小型對照表或多值 tags，查詢時僅需把當前使用者標籤帶入 filter，即可在 100 ms 內完成安全檢索，而不會洩漏未授權片段。文章最後提出「降維為 Tag」是各類資料庫都能落地的通用做法：在文件或使用者上預先貼標、於查詢時以 OR / AND 組合過濾，即能用極低成本完成動態個人化安全檢索。此設計亦能直接套用在 RAG Pipeline 中，確保向量召回的所有片段皆經過授權驗證，避免 AI 回答意外外洩機密。

## 段落摘要

### 1. 需求
說明企業在「萬份文件 × 多部門角色」情境下，既要全文檢索速度又要避免機密外露的兩難；同時指出預先索引與個人化安全需求間天生衝突。

### 2. 個人授權
簡介最基本的「每人一清單」做法雖直觀但不可維護，為後續引出分層模型鋪路。（段落內容尚在草稿階段）

### 3. RBAC：最常見的授權模型
以 100 人 × 5000 文件實例計算：若直接存 boolean 權限需 50 萬筆，而角色分群可把維度降到百餘筆；示範 SQL 與 NoSQL Tag 兩種實作，強調「查詢時帶入 role + category filter」即可高效過濾。

### 4. ABAC
提出將「時間、地點、文件敏感度」等屬性加入決策，可更彈性但需事先定義可索引欄位，否則查詢成本爆增。（草稿提及，細節待補）

### 5. PBAC
說明以政策語句（Policy）描述複雜條件，可動態演算但索引難度最高；實務常與 RBAC/ABAC 混用。（草稿節點）

### 6. 降維為 Tag 的通用策略
總結：無論採何模型，最終都需在資料與操作兩側貼上有限集合標籤；向量 DB 雖不支援 row-level ACL，但可透過 metadata.tags + filter API 完成同等防護。

## 問答集

Q1: 為何向量資料庫很少支援 record-level ACL？  
A1: 向量 DB 的核心優化在高維向量索引與近似搜尋，若對每筆向量再做 ACL 判斷，索引與查詢都會急遽變慢；因此改以 metadata + filter 將安全檢核外移，可在維持 100 ms 級效能下實現授權。

Q2: RBAC 如何有效降低授權維護成本？  
A2: 透過「角色」聚合使用者，把原本 N 人 × M 文件的二維組合轉為 R 角色 × C 分類，設定數量從數十萬降到百餘筆，加速設定與查詢，也方便快取。

Q3: Tag-Based Filter 與 ABAC/PBAC 的關係？  
A3: Tag-Based Filter 是資料庫層面的技術手段；ABAC/PBAC 是授權模型。只要能把 ABAC/PBAC 評估結果對映成有限 tag 集合，就能用同一套向量查詢 API 過濾。

Q4: 在 RAG 架構中，敏感片段會如何外洩？  
A4: 如果檢索階段未先做授權過濾，LLM 可能將未授權文件片段納入回答，形成「意外洩密」。因此必須在向量召回階段先以 tag filter 剔除不符權限的向量。

Q5: 在 .NET + Kernel Memory 要如何實作 tag filter？  
A5: 將每份 MemoryRecord 加入 metadata.Tags，如 `{ "dept": ["HR"], "role": ["R2"] }`，查詢時呼叫 `SearchAsync(query, filters: { "role": "R2" })`；Kernel Memory 會將 filter 傳遞到底層向量 DB 的 Where 子句完成安全過濾。

## 問題與解決方案

Problem: 向量資料庫對每位使用者回傳相同相似度結果，無法滿足敏感文件 record-level 授權。  
Root Cause: 向量索引僅依語義距離排序，沒有權限維度；傳統行列式 ACL 會破壞索引效能。  
Solution:  
1. 為文件與使用者事先貼上有限集合 Tag（部門、角色、敏感度）。  
2. 查詢時將當前使用者允許的 Tag 清單轉為 Filter 條件。  
3. 於向量檢索 API 加入 `filter` 參數，確保僅召回授權向量。  

Example (Kernel Memory):  
```csharp
var filters = new MemoryFilter().WithTag("role", "R2").WithTag("dept", "HR");
var search = await memory.SearchAsync("公司福利", minRelevance:0.8, filters);
```

## 版本異動紀錄
- 0.1.0 (2025-08-06)  首版摘要、Metadata、5 組 Q&A 與問題-解決方案整理。
