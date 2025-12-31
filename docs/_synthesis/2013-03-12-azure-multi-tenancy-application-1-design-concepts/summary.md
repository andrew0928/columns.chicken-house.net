---
layout: synthesis
title: "[Azure] Multi-Tenancy Application #1, 設計概念"
synthesis_type: summary
source_post: /2013/03/12/azure-multi-tenancy-application-1-design-concepts/
redirect_from:
  - /2013/03/12/azure-multi-tenancy-application-1-design-concepts/summary/
postid: 2013-03-12-azure-multi-tenancy-application-1-design-concepts
---

# [Azure] Multi-Tenancy Application #1, 設計概念

## 摘要提示
- 多租戶概念: 一套應用服務多個客戶，核心挑戰在資料隔離與成本平衡
- 架構三分法: Separated DB、Separate Schema、Shared Schema 各有取捨
- 資料隔離: 隔離層級越低越仰賴程式正確性，風險越高
- 成本考量: 資料庫越分散成本越高，集中共享最便宜但風險最大
- 擴充性策略: Shared Schema 常需預留欄位或採用 Name-Value 模式，查詢複雜
- 工程風險: Shared Schema 中漏加 TenantID 條件可能造成客戶資料外洩
- SQL Server 對應: 微軟在不同模式下提供相應設計與管理建議
- 歷史脈絡: 2006 年 MSDN 經典文章提供基礎，但工具環境已大幅進步
- 現代技術: Azure 與 ASP.NET MVC4 降低大型 SaaS/Multi-Tenancy 開發門檻
- 系列預告: 本文為設計概念篇，實作與最佳實務留待下篇

## 全文重點
本文以輕鬆口吻開場，指向雲端與 SaaS 已成熟的時代背景，導入多租戶（Multi-Tenancy）設計的核心觀念：用一套應用服務多個客戶，並以資料隔離、成本、擴充與維運為主要設計考量。作者導讀一篇 2006 年 MSDN 經典文章，聚焦三種常見架構：Separated DB（每客戶一庫）、Separate Schema（共庫分 Schema/表）、Shared Schema（共庫共表以 TenantID 區分），對比其在安全隔離、成本、複雜度與工程風險的差異。

Separated DB 提供最高隔離與最低誤用風險，但成本與管理負擔最高；Separate Schema 在共用資料庫下保有結構級隔離，成本較可控，實作較辛苦但風險仍低；Shared Schema 成本與設計最簡單，卻高度依賴每次查詢正確加上租戶條件，任何遺漏都可能造成跨客戶資料外洩，是最大的營運風險。

文中亦提到 SQL Server 在三種模式下的對應策略（以圖表呈現），尤其在資料擴充（Extensibility）上：前兩者可透過一般加欄位方式演進，Shared Schema 則常仰賴預留欄位或 Name-Value 結構，但會讓查詢與維護變複雜。作者提醒，MSDN 文章對企業內部（Intranet）與 Windows/SQL 環境仍具參考價值，然而今日 Azure、ASP.NET MVC 等雲端與開發框架已成熟，能用更簡潔與自動化的方式落實多租戶應用。本文作為系列首篇，重點在觀念與取捨梳理，實作細節與現代化做法留待續篇。

## 段落重點
### 前言：從「微」潮到大型雲端應用
作者自嘲久未更新部落格，點出社群內容「微型化」趨勢，但同時強調雲端與 Web App 日益大型與成熟。以 Azure 作為 PaaS 降低大型應用門檻，並以 SaaS 與 Multi-Tenancy 為系列主題，打算透過實務導向的觀點分享設計經驗。

### Multi-Tenancy 概念與背景
多租戶即一套應用切割（分租）給多個客戶共同使用，與傳統一客戶一系統不同。受 Salesforce 成功案例帶動，成為 SaaS 核心設計。作者強調設計良好的多租戶應用具挑戰性，並回顧六年前自建框架的經驗，指出今日技術堆疊（Azure + ASP.NET MVC4）已能大幅簡化實作，卻少見中文討論，因此成文分享。

### 三種架構比較：Separated DB / Separate Schema / Shared Schema
- Separated DB：每客戶一個資料庫，隔離最佳、工程師誤用風險最低，但資料庫成本、維運與部署複雜度最高。
- Separate Schema：共享資料庫但為每客戶建立獨立資料表（或 Schema），成本較低仍具結構隔離，降低誤查風險；自 SQL Server 2005 起支援 Schema 後實作較容易，但仍需規劃命名、遷移與佈署策略。
- Shared Schema：同庫同表以 TenantID 區分，成本與設計最簡單；然而任何一次查詢遺漏租戶條件都可能造成跨客戶資料外洩，是營運與資安的最大風險，需要嚴格的開發準則與防呆機制。

### SQL Server 對應與擴充性策略
MSDN 表格歸納了三種模式在安全、擴充、報表、部署、維運等面向的建議做法。以擴充性為例：Separated DB/Separate Schema 可直接加欄位演進資料模型；Shared Schema 受限於共表結構，常需預留多個通用欄位或採 Name-Value（Entity-Attribute-Value）方式儲存彈性資料，但將導致查詢、索引與報表複雜化。此段提醒在選型時，須同時評估資料模型演進、查詢複雜度與測試成本。

### 時空背景與今日技術選擇
雖然 2006 年 MSDN 文章對企業內部、Windows + SQL Server 場景仍具高度參考價值，但當年缺乏 Azure 與成熟的 MVC 生態。今日雲端平台提供彈性資源、託管服務與自動化工具，能以更低成本與更高可靠性實作多租戶。作者以此鋪陳系列後續內容：在現代雲端環境中，如何結合 Azure 與 ASP.NET MVC4，將上述架構取捨落地為工程實務。

### 結語與後續預告
本文定位為設計概念導讀，重在建立選型思維：隔離與成本的平衡、工程風險與維運複雜度、資料模型擴充與查詢可維護性。作者表示下一篇將進一步說明在 Azure 環境中的具體實作與更「厲害」的武器與方法，協助讀者從概念走向落地。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 雲端服務基本觀念（SaaS、PaaS）
   - 資料庫基礎（Database、Schema、Table、Query/Index）
   - 多租戶（Multi-Tenancy）基本定義與租戶隔離概念
   - 相關技術背景：Microsoft Azure、ASP.NET MVC、SQL Server（含 Schema 支援）

2. 核心概念：
   - 多租戶隔離等級：Separated DB、Separate Schema、Shared Schema 三種模式與取捨
   - 成本與風險權衡：成本越低通常隔離越弱、開發維運風險越高
   - 擴充性（Extensibility）策略：不同模式在資料型別/欄位擴充的可行方式
   - 開發安全性與防呆：Shared Schema 易因漏加 TenantID 導致資料外洩
   - 時代背景與工具演進：早期僅 Windows/SQL 架構，現今可善用 Azure 與現代框架

3. 技術依賴：
   - 資料層：SQL Server（含 Schema 概念，SQL2005 起支援）是三種模式的關鍵
   - 應用層：ASP.NET MVC 作為 Web 應用框架，需承載租戶識別與資料存取邏輯
   - 平台層：Azure 作為 PaaS 提供部署、擴展與營運能力（相較 2006 年文章的純自建環境）
   - 指導資源：MSDN 文章作為設計要點與模式比較的依據

4. 應用場景：
   - SaaS 產品需同時服務多家客戶且控管成本
   - 企業內部（Intranet）多部門共用系統但需資料隔離
   - 對隔離要求極高（金融/醫療）與對成本敏感（新創/PoC）的不同情境
   - 需要隨時間擴展資料模型或快速上線的專案

### 學習路徑建議
1. 入門者路徑：
   - 了解 SaaS/PaaS 與 Multi-Tenancy 基本概念與案例
   - 複習資料庫隔離單位：DB、Schema、Table 與 Query 基礎
   - 比較三種模式的優缺點與典型風險（特別是 Shared Schema 的 TenantID 風險）

2. 進階者路徑：
   - 設計租戶識別機制（例如子網域/路徑/標頭解析 Tenant，應用層傳遞 Tenant Context）
   - 熟悉 SQL Server Schema 的使用與自動化部署（建立 per-tenant schema/table）
   - 規劃資料模型擴充策略（欄位擴充、保留欄位、Name-Value 結構的取捨）

3. 實戰路徑：
   - 依需求選型：高隔離用 Separated DB；折衷用 Separate Schema；成本優先用 Shared Schema
   - 建立防呆與測試：查詢必帶 TenantID 的靜態分析/單元測試/資料遮罩驗證
   - 自動化腳本與管線：建立/佈署租戶用 DB/Schema 的 Provisioning 流程
   - 監控與運維：隔離故障域、備援/備份策略、異常查詢告警（防止跨租戶資料外洩）

### 關鍵要點清單
- 三種多租戶模式：Separated DB / Separate Schema / Shared Schema 的取捨（優先級: 高）
- 隔離等級與成本關係：隔離越高成本越高、風險越低（優先級: 高）
- Separated DB 特性：每客戶一庫，最佳隔離、維運成本高（優先級: 高）
- Separate Schema 特性：同庫異 Schema，成本與隔離折衷（優先級: 高）
- Shared Schema 特性：同庫同表以 TenantID 區分，成本最低但風險最高（優先級: 高）
- 查詢安全風險：漏加 TenantID 條件恐致跨租戶資料外洩（優先級: 高）
- 擴充策略差異：Shared Schema 常需保留欄位或 Name-Value 結構，查詢複雜度上升（優先級: 中）
- SQL Server Schema 的作用：提供中階隔離與結構管理（優先級: 中）
- 開發框架承載：ASP.NET MVC 中需實作租戶解析與上下文傳遞（優先級: 中）
- 自動化部署與 Provisioning：針對 DB/Schema 的建立與版本化流程（優先級: 中）
- 測試與守門機制：靜態分析/單元測試確保所有查詢帶租戶條件（優先級: 高）
- 監控與稽核：查詢審計與異常偵測，避免跨租戶讀寫（優先級: 中）
- 場景選型指南：依安全、法規、成本、彈性選擇模式（優先級: 高）
- 歷史與工具演進：從 2006 年自建到今日可用 Azure/PaaS 降低門檻（優先級: 低）
- 擴展到營運面：備份、災難復原、移轉租戶（模式間遷移）的策略（優先級: 中）