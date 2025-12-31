---
layout: synthesis
title: "community server 改造工程"
synthesis_type: summary
source_post: /2005/04/04/community-server-customization-project/
redirect_from:
  - /2005/04/04/community-server-customization-project/summary/
postid: 2005-04-04-community-server-customization-project
---

# community server 改造工程

## 摘要提示
- 編輯器強化: 改寫 TextEditorProvider 以完整啟用 FTB 3.0 的進階編輯功能。
- 圖片藝廊整合: 開啟並修正 FTB 3.0 的 Insert Image From Gallery，支援 Blog 與 Forum。
- 表情符號支援: 啟用 FTB 3.0 的表情工具列，一鍵插入表情符號。
- 相簿批次上傳: 自建 Web Service 與命令列工具，支援相片縮圖與自動建立群組/相簿。
- 首頁改版: 以 ASP.NET 控制項重構首頁，聚焦 Gallery/Blogs/Forums。
- Blog 列表化: 將部落格首頁改為 Blog 清單，提升導覽效率。
- 文章顯示調整: Blog 內文改為僅顯示標題，需點入查看全文，符合使用者需求。
- 自訂化成就感: 多項改造完成後提升使用體驗，作者表達高度滿意。
- 系統版本: 基於 Community Server 1.0 RTM 展開的客製工程。
- 後續計畫: 準備將舊 ChickenHouse Forum 的資料轉移至 CS。

## 全文重點
作者在安裝 Community Server 1.0 RTM 之後，針對其預設功能與介面進行了多項客製化與改良，目標是在不破壞系統架構的前提下，補齊常用功能並改善實際使用體驗。首先，他改寫了 TextEditorProvider，完整啟用 FTB 3.0 原生具備但未開放的進階編輯功能，並進一步開通「Insert Image From Gallery」功能，讓使用者能像 Office 的多媒體藝廊般，先上傳圖片再直接插入至 Blog 與 Forum 貼文中。針對表達性需求，作者也開放了 FTB 3.0 的表情符號工具列，讓插入表情更直覺。

在媒體管理方面，針對 CS 缺乏相簿批次上傳的痛點，作者自建 Web Service，並依其 API 撰寫命令列工具，實現本地相片的批次縮圖與上傳，且能自動建立對應的群組與相簿，大幅降低管理成本。介面與瀏覽體驗上，他重構了網站首頁，改以 ASP.NET 控制項呈現 Gallery、Blogs、Forums，並將 Blog 首頁改為 Blog 列表模式，提升導覽效率。此外，依據家中使用者（太座）的需求，Blog HomePage 調整為只顯示標題、點入才見內文，讓閱讀流程更簡潔。

整體而言，這些改造大幅提升了 Community Server 在內容編輯、媒體處理、與介面導覽的實用性與易用性。作者對成效感到滿意，並規劃下一步將舊有 ChickenHouse Forum 的資料遷移至 Community Server，延續系統整合與升級的進程。

## 段落重點
### 改造項目總覽
作者基於 Community Server 1.0 RTM 展開多項功能與介面改造。核心在於強化編輯器與媒體能力：透過改寫 TextEditorProvider，全面啟用 FTB 3.0 的進階功能；開通「Insert Image From Gallery」讓使用者能先上傳、再從藝廊插圖到貼文；啟用 FTB 的表情符號工具列以增強表達力。在媒體管理上，針對相簿缺少批次上傳的缺陷，他自行設計 Web Service 並撰寫命令列工具，支援本地相片批次縮圖與上傳，並自動建立群組與相簿，改善大量內容上傳流程。介面方面，他以 ASP.NET 控制項重構首頁資訊架構，將重點聚合至 Gallery、Blogs、Forums；同時將 Blog 首頁改為清單式導覽，並把 Blog HomePage 調整為僅顯示標題、點入才看全文，符合實際使用者（太座）的閱讀喜好。整體改造使系統更貼合需求、使用體驗更順暢。

### 後續計畫與心得
完成上述改造後，作者表示使用起來更具成就感，系統的編輯、上傳、瀏覽各環節都有顯著提升。接下來的主要工作是資料面整合：計畫將既有 ChickenHouse Forum 的歷史資料轉入 Community Server，延伸此次工程的效益。這意味著未來不僅功能到位，資料也將集中於同一平台，利於維運與擴充。整體來看，本文是一份針對 Community Server 1.0 的實務改造紀錄，聚焦在補齊編輯器、媒體處理與導覽體驗的缺口，並以可維護的方式擴展原系統能力。

## 資訊整理

### 知識架構圖
1. 前置知識
   - ASP.NET 基礎與 WebForms 控制項使用
   - Community Server 1.0 架構與模組（Blogs/Forums/Gallery）
   - Provider 模式與自訂 Provider 的掛載方式
   - FTB 3.0 富文字編輯器（設定、外掛、功能）
   - Web Service（SOAP/HTTP）與指令列工具開發
   - 影像處理與批次上傳流程（縮圖、上傳、資料結構）

2. 核心概念
   - Community Server 可擴充性：透過 Provider、Control 與版面客製化進行功能擴充
   - FTB 3.0 整合：啟用隱藏功能（圖片藝廊、表情符號、進階工具列）
   - 自訂 TextEditorProvider：替換/擴充預設編輯器能力
   - 相簿批次上傳管線：Web Service API + CLI 工具 + 圖片處理與自動建構群組/相簿
   - UI/UX 客製化：首頁、Blog 列表與內容展示策略的調整

3. 技術依賴
   - CS 平台依賴 ASP.NET，模組（Blogs/Forums/Gallery）透過控制項組合
   - FTB 3.0 依賴 TextEditorProvider 正確掛載與設定，並能呼叫 Image Gallery
   - 圖片藝廊功能依賴後端儲存（檔案/DB）與權限設定
   - 批次上傳工具依賴自建 Web Service API；CLI 工具呼叫 API，內含影像縮放
   - UI 改版依賴頁面/控制項替換與路由（或頁面繼承）調整

4. 應用場景
   - 企業或社群站台將 CS 作為整合式部落格/論壇/相簿平台
   - 編輯器功能強化：提升貼文效率與媒體插入體驗
   - 大量照片管理：攝影社群、活動紀實的批次上傳與自動歸檔
   - 針對讀者體驗的首頁與內容展示調整（列表式、標題式、點擊展開）

### 學習路徑建議
1. 入門者路徑
   - 安裝與部署 Community Server 1.0（了解模組與資料結構）
   - 啟用並測試 FTB 3.0 基本功能（熟悉設定檔與資源）
   - 學會替換 TextEditorProvider 的基本流程（不改碼先換 Provider）

2. 進階者路徑
   - 自訂與擴充 TextEditorProvider，開啟進階工具列與 Image Gallery
   - 研究 FTB 3.0 插件（表情符號列、圖片插入對話框）與權限控制
   - 進行頁面與控制項客製化（首頁、Blog 列表、Blog 文章頁展示策略）

3. 實戰路徑
   - 設計與實作相簿批次上傳 Web Service（定義 API、權限、錯誤碼）
   - 開發 CLI 工具：本地縮圖、呼叫 API、建立群組/相簿與上傳
   - 規劃資料遷移：從舊論壇導入 CS（版面、附件、使用者對應）

### 關鍵要點清單
- 啟用 FTB 進階功能: 透過自訂 Provider 解鎖被關閉的編輯器功能（如圖片庫） (優先級: 高)
- TextEditorProvider 替換: 改寫並掛載自家 Provider 以掌控編輯體驗 (優先級: 高)
- Insert Image From Gallery: 利用 FTB 內建圖片藝廊達成貼文插圖流程 (優先級: 高)
- Emotion Icons 工具列: 啟用表情符號插入增進互動性 (優先級: 中)
- CS 相簿批次上傳 API: 自建 Web Service 提供批量照片處理入口 (優先級: 高)
- 指令列上傳工具: 以 CLI 工具實作縮圖與自動化上傳流程 (優先級: 高)
- 自動建立群組/相簿: 上傳流程中自動建立對應 Gallery 結構 (優先級: 中)
- 首頁控制項重構: 以 ASP.NET 控制項重做首頁呈現（Gallery/Blogs/Forums 匯總） (優先級: 中)
- Blog 列表首頁: 將 Blog 首頁改為列表式瀏覽提升導覽性 (優先級: 中)
- Blog 文章頁摘要化: 僅顯示標題，點擊後看全文以改善版面與閱讀速度 (優先級: 低)
- 權限與安全: 對圖片上傳與 Web Service 設定驗證與授權 (優先級: 高)
- 影像處理流程: 本地縮圖策略與伺服器端儲存規劃（尺寸、格式、品質） (優先級: 中)
- 模組整合測試: Blogs/Forums/Gallery 與編輯器、API 的整合性驗證 (優先級: 中)
- 部署與回滾策略: 客製化後之佈署流程與可回復機制 (優先級: 中)
- 舊站資料遷移: 規劃 ChickenHouse Forum 至 CS 的資料轉換 (優先級: 中)