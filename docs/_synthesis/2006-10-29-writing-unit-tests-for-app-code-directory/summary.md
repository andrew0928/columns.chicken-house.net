---
layout: synthesis
title: "替 App_Code 目錄下的 code 寫單元測試 ?"
synthesis_type: summary
source_post: /2006/10/29/writing-unit-tests-for-app-code-directory/
redirect_from:
  - /2006/10/29/writing-unit-tests-for-app-code-directory/summary/
---

# 替 App_Code 目錄下的 code 寫單元測試 ?

## 摘要提示
- App_Code 動態編譯: ASP.NET 2.0 會自動編譯 ~/App_Code 下的原始碼，省去手動編譯但也帶來測試上的麻煩
- 缺乏穩定 DLL: App_Code 沒有固定對應的實體 DLL，使以傳統測試框架載入測試目標變得困難
- Hosting 依賴: App_Code 內程式常依賴 HttpContext 等 Hosting 環境，與獨立 AppDomain 執行的測試衝突
- NUnit 侷限: NUnit Test Runner 嚴謹地以獨立 AppDomain 載入與執行，難以測試依賴 web 環境的程式
- 微軟測試框架不適用: Microsoft 自家 Unit Test Framework 同樣難以處理此情境
- 尋找替代方案: 作者嘗試修改 NUnit 核心後放棄，改以搜尋更輕量的測試框架
- 發現 NUnitLite: 找到 NUnitLite，主打輕量、無 GUI、無多執行緒、無獨立 AppDomain
- 嵌入式與特殊環境: NUnitLite 專為資源受限或需在特殊環境中執行的測試而生
- 適合 ASP.NET 網站: ASP.NET 網站類似 add-in，難以脫離宿主環境，NUnitLite 更能貼合
- 後續實作待續: 雖然當時版本 0.1.0.0 且最新 release 尚無法建置，但已足以解決問題，實作細節留待下篇

## 全文重點
本文探討在 ASP.NET 2.0 的 App_Code 目錄下撰寫之程式碼如何進行單元測試的難題。ASP.NET 2.0 提供便利的動態編譯機制，將 ~/App_Code 內的原始碼視為網站的一部分於 Hosting 環境自動編譯並執行，免去手動產出 DLL。然而此機制造成兩大測試困境：首先，App_Code 並無穩定對應的實體 DLL，僅能在 Temporary ASP.NET Files 目錄中找到經編碼的動態產物，路徑常變、不便引用；其次，App_Code 的程式常依賴 HttpContext 等宿主資源，而主流測試工具（如 NUnit Test Runner）會在獨立 AppDomain 執行測試，導致與 web Hosting 環境脫鉤，無法涵蓋大量依賴環境的程式碼。作者嘗試 Microsoft 自家測試框架與深入研究 NUnit 原始碼，發現其設計本就強調隔離、可延伸與嚴謹的執行模型，難以在不分叉維護自訂版本的情況下改造以貼合 App_Code 測試需求。

在持續搜集資訊後，作者發現 NUnitLite。NUnitLite 的願景是提供一個輕量級（source-only）的測試框架，去除了 GUI、外掛延伸、多執行緒與獨立 AppDomain 等重量特性，讓測試能直接嵌入並在受限或特殊的執行環境中運作，例如嵌入式開發、外掛測試或需要與宿主緊密結合的情境。這些特性恰好契合 ASP.NET 網站的本質：網站像是 IIS 的 add-in，許多核心邏輯與 HttpContext、Session、Request/Response 等強耦合，若強行抽離環境就無法有效驗證真實執行路徑。作者因此採納 NUnitLite 作為解方，即使當時版本尚早（0.1.0.0）且最新發行版未必能直接建置，仍足以解決主要痛點，讓測試可以在網站宿主中運行，避免 DLL 載入與 AppDomain 隔離的障礙。文末作者表示實際用法與範例將於下篇補充。

## 段落重點
### 背景：JUnit/NUnit 與 .NET 的測試生態
作者首先回顧單元測試框架的脈絡：NUnit 源自 JUnit，理念相近，但在移植至 .NET 時善用 .NET 平台優勢與特性。此鋪陳旨在說明：在 .NET 世界已有成熟且普及的測試工具，被廣泛應用於日常開發。然而，當應用場景轉至 ASP.NET 網站的 App_Code 目錄，這些工具的預設運作模型未必貼合，埋下後文問題。

### ASP.NET 2.0 的 App_Code 動態編譯機制
ASP.NET 2.0 引入 ~/App_Code 作為網站原始碼集中地，會於 Hosting 環境中自動編譯並執行，開發者無需手動產出 DLL。此機制極大簡化部署與更新，程式碼置入即可生效。但這樣的便利性也反向造成測試與組件引用的障礙：由於少了明確且固定的組件產物，傳統以「引用 DLL → 載入測試目標」的測試流程難以套用。

### 兩大測試難題：無穩定 DLL 與宿主依賴
作者具體點出兩點痛處。其一，App_Code 沒有對應實體 DLL；雖可在 Temporary ASP.NET Files 中找到動態產物，但路徑與名稱經過編碼且不穩定，不適合自動化測試流程。其二，App_Code 內碼常依賴 ASP.NET Hosting 提供的資源（如 HttpContext、Application、Session、Request、Response），而常見測試跑器會在獨立 AppDomain 執行，缺乏網站宿主環境，導致大量邏輯無法被有效測試。此二者合併，讓一般單元測試策略難以覆蓋實務上最需要驗證的部分。

### 傳統框架的限制與修改嘗試的放棄
作者試用微軟官方單元測試框架與 NUnit，皆告失敗。進一步閱讀 NUnit 原始碼與追蹤其執行流程後發現，NUnit 的設計相當嚴謹：為每個測試準備獨立 AppDomain，從指定 assembly 載入測試類別再隔離執行，這對通用性與穩定性是加分，卻與需要在 Web Hosting 環境中連動的測試需求相衝突。雖考慮修改 NUnit 核心來移除隔離，但這不但工程成本高，還會導致自有分支的維護負擔，違背作者只想「執行單元測試而不分叉框架」的初衷，故選擇放棄此路徑。

### 轉機：NUnitLite 的願景與特性
作者最終在搜尋中發現 NUnitLite，並引述其願景重點：NUnitLite 僅實作 NUnit 的精簡子集，以最小資源運作，且以原始碼形式直接嵌入測試專案，不提供 GUI、多執行緒、外掛擴充或獨立 AppDomain 等重量級功能。這種「去重量化」使其能在資源受限或需在特殊宿主環境中執行的情境發揮效果，例如嵌入式系統、其他軟體之外掛測試等。就作者需求而言，這意味著可以避免 AppDomain 隔離、貼近網站宿主執行，從而測試依賴 HttpContext 等資源的程式碼。

### 為何特別適合 ASP.NET 網站與 App_Code
作者進一步闡述 ASP.NET 網站的本質：其運作更像是掛載在 IIS 上的 add-in，許多邏輯天然地與宿主耦合。若強行將邏輯抽離以求可在傳統 Runner 下測試，不僅成本高，實際可測覆蓋率也會偏低；反觀在宿主中執行的輕量測試框架，能以較低摩擦貼近真實行為，提升測試的實用價值與可信度。這正是 NUnitLite 對此問題空缺的對應。

### 結語與後續計畫
雖然 NUnitLite 當時僅 0.1.0.0 且最新發行版尚無法直接建置，作者仍評估其已足以解決現階段痛點，作為在 App_Code 內撰寫單元測試的可行解。文末作者以樂觀語氣收束，表示「實際用法」將於後續文章補充，預示會分享整合方式與實作細節，協助他人重現此解法。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 基本 .NET/ASP.NET 2.0 架構與專案結構（特別是 App_Code 目錄的動態編譯機制）
   - 單元測試基本概念與常見框架（JUnit/NUnit 的基本用法與觀念）
   - ASP.NET Hosting 環境與 HttpContext（Request/Response/Session/Application）
   - .NET AppDomain 的概念與測試執行流程

2. 核心概念：
   - App_Code 動態編譯：ASP.NET 在 Hosting 環境下自動編譯 App_Code，無固定輸出 DLL
   - 測試框架執行模型：NUnit 等以獨立 AppDomain 載入測試，與 Hosting 情境脫鉤
   - Hosting 依賴問題：依賴 HttpContext 等環境物件的程式難以在傳統測試 Runner 中執行
   - 輕量化內嵌測試（NUnitLite）：以原始碼內嵌、無多 AppDomain/GUI 的輕量 Runner，能在特殊/受限環境執行
   - 權衡與覆蓋率：抽離 Hosting 相依程式碼困難，覆蓋率受限，需換框架/策略

3. 技術依賴：
   - ASP.NET 2.0 Web Site 模型 → 提供 App_Code 動態編譯與 Hosting 生命週期
   - HttpContext 等系統類型 → 綁定 Hosting 環境
   - 傳統 NUnit/MS Test Runner → 依賴獨立 AppDomain 載入測試 DLL
   - NUnitLite → 原始碼納入測試專案，省去多餘特性（AppDomain/GUI/多執行緒），可在 Web 應用內執行
   - 執行平台 → .NET / Mono / .NET Compact Framework

4. 應用場景：
   - 為 App_Code 下依賴 Hosting 的程式碼撰寫並執行單元測試
   - 在無法或不便產生獨立組件（DLL）的情況進行測試
   - 受限或特殊執行環境（嵌入式、外掛/附加元件、無 GUI、資源有限）中執行測試
   - 在 Web 應用程式內嵌自我測試機制（例如經由頁面/Handler 觸發）

### 學習路徑建議
1. 入門者路徑：
   - 理解單元測試與測試框架基本概念（測試方法、斷言、測試夾具）
   - 認識 ASP.NET App_Code 的動態編譯與無固定 DLL 的特性
   - 安裝並嘗試簡單 NUnit 測試（不含 Hosting 相依的程式碼）

2. 進階者路徑：
   - 了解 NUnit Runner 的執行模型（AppDomain、從 DLL 載入）與限制
   - 認識 HttpContext 等 Hosting 相依 API，區分可抽象與不可抽象之處
   - 研究 NUnitLite 的設計理念與限制，嘗試將其以原始碼方式納入專案

3. 實戰路徑：
   - 將 NUnitLite 內嵌至 ASP.NET 專案（含 App_Code），建立最小可行測試入口（例如 .aspx/.ashx 觸發）
   - 將需測試程式碼與 Hosting 邏輯適度分層（盡量降低直接對 HttpContext 的耦合）
   - 建立與執行測試、收集結果，逐步擴大覆蓋率與用例複雜度

### 關鍵要點清單
- App_Code 動態編譯：ASP.NET 會在 Hosting 環境自動編譯 App_Code 內的程式碼，不會輸出固定 DLL（優先級: 高）
- 無固定 DLL 的測試難題：傳統 Runner 需要 DLL 目標，App_Code 沒有穩定輸出導致不便（優先級: 高）
- Hosting 相依性：HttpContext/Request/Response/Session 等使程式碼難以在獨立 Runner 中執行（優先級: 高）
- NUnit 執行模型限制：NUnit 以獨立 AppDomain 載入測試，脫離 ASP.NET Hosting 環境（優先級: 高）
- 覆蓋率現實：強行抽離 Hosting 相依程式碼通常導致覆蓋率偏低（優先級: 中）
- NUnitLite 核心理念：以原始碼內嵌、去除 AppDomain/GUI/擴充機制，適合受限或特殊環境（優先級: 高）
- 在 Web 站內跑測試：以 NUnitLite 於 ASP.NET 站台內啟動測試，避免環境落差（優先級: 高）
- 減少耦合的分層策略：將業務邏輯與 HttpContext 介面隔離以提升可測性（優先級: 中）
- 執行平台相容性：NUnitLite 支援 .NET/Mono/.NET CF，適用多種裝置與情境（優先級: 低）
- 不改動框架原始碼：避免自行修改 NUnit 核心以免維運風險，改採合適框架（優先級: 中）
- 測試入口設計：以頁面/Handler/自訂端點作為測試觸發器並輸出結果（優先級: 中）
- 環境準備與資源限制：輕量化 Runner 減少資源需求，適合 CI 或嵌入式場景（優先級: 低）
- 升級與維護風險：NUnitLite 版本早期可能無法直接建置，需因應與維護（優先級: 低）
- 觀念對齊：單元測試在 Web 環境需接受與桌面/類庫不同的執行與隔離策略（優先級: 中）
- 實務取捨：在可測性、覆蓋率與系統耦合間取得平衡，選擇合適工具（優先級: 中）