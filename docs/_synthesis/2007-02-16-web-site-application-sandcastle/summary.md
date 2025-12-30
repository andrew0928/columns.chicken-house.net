---
layout: synthesis
title: "Web Site Application + Sandcastle"
synthesis_type: summary
source_post: /2007/02/16/web-site-application-sandcastle/
redirect_from:
  - /2007/02/16/web-site-application-sandcastle/summary/
---

# Web Site Application + Sandcastle

## 摘要提示
- 目標: 在 ASP.NET Web Site 專案中產出可供 Sandcastle/NDoc 使用的 DLL 與 XML 文件
- 難點: Web Site 的 App_Code 動態編譯，預設無法直接取得組件與註解 XML
- 文件需求: Sandcastle/NDoc 同時需要 Assembly 檔與編譯器輸出的 XML 文件
- web.config 編譯選項: 可產生 XML，但多層目錄會反覆覆寫同名檔案而失敗
- Web Deployment Project: 可合併 DLL，仍無法解決 XML 文件輸出
- MSBuild 自寫 Task: 可行但成本高、流程複雜且需熟悉 MSBuild
- 直接用 csc.exe: 以命令列遞迴編譯 App_Code 成 DLL 與 XML，成功生成文件
- Sandcastle 性能: 支援 .NET 2.0 特性但建置極慢，相較 NDoc 明顯耗時
- 方案限制: 無法涵蓋 wsdl/xsd 自動產生碼與 .aspx/.ascx partial 類別
- 折衷結論: 聚焦可重用 class library 的文件，暫時放棄難以自動化的頁面相關部分

## 全文重點
作者想在 ASP.NET 2.0 的 Web Site 模型中製作文檔注釋（XML）與 DLL，以便交給 NDoc 或 Sandcastle 產生說明文件。然而 Web Site 模型以 App_Code 動態編譯，預設既不輸出組件也不輸出 XML 註解，與傳統類庫不同，導致文件工具的兩大需求（Assembly 與 XML doc）無法同時取得。作者逐一嘗試多種方法：先試在 web.config 加 compilerOptions 產生 XML，測試環境可行但在實際站台失敗，原因是 ASP.NET 以目錄為單位多次編譯，導致同一路徑的 XML 檔被反覆覆蓋與刪除；且 compilerOptions 需指定固定檔名，無法使用萬用字元或自動分散輸出。

改用 Visual Studio 的 Web Deployment Project 則可把 aspnet_compiler 輸出的多個組件再併成單一 DLL，解決組件面向，但仍無法產生對應 XML 文件。進一步思考以 MSBuild 撰寫自訂 Task，集合所有 .cs 交給 Csc 任務，雖可行但代價高，且與作者既有建置流程不符。最終採取務實路徑：直接呼叫 csc.exe，以 /target:library、/out、/doc 與 /recurse 參數對 App_Code 內的 .cs 遞迴編譯，成功一次產出 DLL 與 XML，之後即可提供給 NDoc/Sandcastle 建置說明文件。此法達成核心目標，但 Sandcastle 的建置速度遠慢於過往 NDoc（60 分鐘對 20 分鐘），屬可接受但需心理預期的成本。

作者也誠實列出此法的侷限：App_Code 內除 .cs 還可能含 wsdl/xsd 等會觸發工具自動產生的來源碼，單靠 csc.exe 無法涵蓋；.aspx/.ascx 的後置碼屬 partial class，另一半由 ASP.NET 執行階段自動解析範本產生，亦非單純 csc 能處理。若要完整涵蓋，勢必複製一套類似 aspnet_compiler 的管線，工程過大不划算。於是作者採取折衷，將文件產出聚焦於可重用的 class library 部分，暫時放棄頁面與自動產生碼的覆蓋，待未來工具更便利時再行補強。

## 段落重點
### 問題背景與文件工具需求
作者希望像在一般 C# 類庫那樣，從註解提取 XML 文件並結合組件交給 NDoc/Sandcastle 產生說明。但 ASP.NET 2.0 的 Web Site（非 Web Application Project）以 App_Code 動態編譯，通常不會產出 DLL 與 XML 文件，與文件工具同時需要「Assembly 檔」與「編譯時輸出的 XML 文件」的前提相衝突。目標是找到在不改寫兩份程式碼的前提下，為 Web Site 取得這兩個產物。

### 在 web.config 裡加上 compiler option 輸出 XML
利用 system.codedom 的 compilerOptions 加入 /doc: 路徑，可在開發環境成功生成 XML 文件。然而部署到正式站時失敗：ASP.NET 以目錄為單位多次編譯 App_Code，每層編譯都產生並覆寫相同路徑的 XML，最後還可能被清除。由於 /doc 參數需要固定檔名，無法以萬用字元或自動分層輸出，當 App_Code 有多層或多專區時便無解。除非目錄非常扁平，否則不具可行性。

### Web Deployment Project 的嘗試
Visual Studio 的 Web Deployment Project 在 SP1 已內建，可先用 aspnet_compiler 輸出多個組件，再以合併工具聚合為單一 DLL。這能方便取得 DLL，符合文件工具的 Assembly 要求。但其流程並未連帶生成 XML 文件，導致仍然缺乏 Sandcastle/NDoc 需要的另一半要件。結論是解決了組件輸出，卻無法補齊 XML，仍不足以完成文件建置。

### 使用 MSBuild 自訂 Csc Task 的可能性
社群上有做法是撰寫 MSBuild 專案與自訂 Task，將所有 .cs 蒐集後交給 Csc 任務編譯並輸出 /doc。技術上可行且彈性最大，但代價是需要導入 MSBuild 流程、撰寫與維護建置腳本，對既有未採用 MSBuild 的流程而言成本偏高。對作者來說學習與整合成本不小，與既定目標「快速拿到 DLL + XML 用於文件工具」不成比例，暫列次選。

### 直接以 csc.exe 編譯與其限制
最終採取命令列編譯：csc.exe /out:App_Code.dll /doc:App_Code.xml /target:library /recurse:App_Code\*.cs，一次產出 DLL 與 XML，順利交付給 NDoc/Sandcastle。雖然 Sandcastle 支援 .NET 2.0 特性（如泛型），但建置速度較慢。此法的限制包括：App_Code 內的 wsdl/xsd 會在 ASP.NET 管線中自動產生程式碼，單純 csc 無法涵蓋；.aspx/.ascx 的 partial 類別另一半須由引擎解析範本後產生，亦非 csc 所能處理。若要完全自動化等同重寫 aspnet_compiler，工程過大。作者因此折衷，專注為可重用的 class library 產生說明文件，對頁面與自動產生碼先不處理，等待更便利的工具再完善。

## 資訊整理

### 知識架構圖
1. 前置知識：學習本主題前需要掌握什麼？
- C# XML 文件註解與編譯器 /doc 參數的概念
- .NET 組件與反射（Assembly、metadata）
- ASP.NET 2.0 Web Site 模型（App_Code、動態編譯）與 Web Application 模型差異
- Sandcastle/NDoc 的工作流程與輸入需求
- 基本命令列工具：csc.exe、aspnet_compiler.exe；VS Web Deployment Project 概念

2. 核心概念：本文的 3-5 個核心概念及其關係
- 文件生成條件：需要「Assembly」與「XML 文件註解」兩者 → 供 NDoc/Sandcastle 使用
- Web Site 的動態編譯特性：App_Code 依資料夾分批編譯、非單一 DLL → 使 XML 文件與 DLL 難以直接取得
- 方案比較：web.config compilerOptions、Web Deployment Project、MSBuild Csc Task、自行呼叫 csc.exe
- 取捨與限制：用 csc.exe 可快速產出 DLL+XML，但無法覆蓋由 ASP.NET 引擎或設計工具動態生成的部分（ascx/aspx partial、wsdl/xsd）

3. 技術依賴：相關技術之間的依賴關係
- Sandcastle/NDoc ← 依賴 Assembly + XML Doc
- Assembly 來源 ← aspnet_compiler.exe 或 csc.exe 或 Web Deployment Project（再做 ILMerge/合併）
- XML Doc 來源 ← C# 編譯器 /doc 選項（web.config compilerOptions 或 csc.exe 參數）
- Web Site 編譯流程 ← ASP.NET 編譯器以資料夾為單位動態產生中繼碼與 partial 類別

4. 應用場景：適用於哪些實際場景？
- 為 ASP.NET Web Site 專案生成 API 說明文件（CHM/網站版）
- 持續整合中自動產出文件供團隊或客戶使用
- 需要對共用類別庫提供註解對應的正式文件
- 需要在沒有完整專案檔（csproj）下，臨時導出 DLL+XML

### 學習路徑建議
1. 入門者路徑：零基礎如何開始？
- 了解 C# XML 註解格式與 /doc 參數如何輸出 XML
- 認識 Sandcastle/NDoc 需要的輸入檔（.dll + .xml）
- 嘗試以 csc.exe 編譯簡單類別庫：csc /target:library /doc:out.xml input.cs
- 在本機為小型 Web Site 的 App_Code 下所有 .cs 執行 csc /recurse 先拿到 DLL+XML

2. 進階者路徑：已有基礎如何深化？
- 探索 web.config 的 system.codedom/compilers compilerOptions 設定與其限制
- 使用 aspnet_compiler.exe 產出多個組件，再了解 Web Deployment Project 的合併流程
- 研究 MSBuild 自訂 Target/Task（Csc Task）自動化收集來源檔並輸出 XML
- 評估 Sandcastle 的建置時間與管線最佳化（例如只針對變更的組件生成）

3. 實戰路徑：如何應用到實際專案？
- 在 CI 中加入「臨時文件輸出」步驟：以 csc.exe 針對 App_Code/*.cs 產出 App_Code.dll + App_Code.xml
- 將輸出餵給 Sandcastle 建置文件；記錄生成時間與錯誤
- 對無法由 csc 處理的來源（ascx/aspx、wsdl、xsd 生成碼）納入限制清單並標註文件缺口
- 如需更完整覆蓋，改採 Web Application 專案或以 aspnet_compiler + 合併工具補齊

### 關鍵要點清單
- 文件工具輸入需求：Sandcastle/NDoc 需要 DLL 與對應的 XML 文件註解才可生成（優先級: 高）
- Web Site 模型難點：App_Code 由 ASP.NET 依資料夾分批編譯，預設不產生單一 DLL（優先級: 高）
- web.config compilerOptions 限制：/doc 需指定固定檔名，且多目錄編譯會相互覆蓋（優先級: 高）
- Web Deployment Project 作用：可合併多個輸出組件為單一 DLL，但仍無法直接得到 XML（優先級: 中）
- 直接用 csc.exe：csc /out:App_Code.dll /doc:App_Code.xml /target:library /recurse:App_Code\*.cs 可快速產出（優先級: 高）
- aspnet_compiler.exe：能為 Web Site 預編譯產出多個組件，適合後續再合併（優先級: 中）
- ascx/aspx partial 類別缺口：由 ASP.NET 引擎動態產生的 partial 類別，csc 單獨無法覆蓋（優先級: 高）
- wsdl/xsd 自動生成碼：Web Site 放入 wsdl/xsd 會觸發自動產碼，csc 無法直接處理該流程（優先級: 中）
- 取捨策略：若文件重點在共用 class library，可接受忽略 ascx/aspx/wsdl/xsd 部分（優先級: 中）
- Sandcastle 效能：相較 NDoc，Sandcastle 生成速度明顯較慢，需預留建置時間（優先級: 中）
- MSBuild 自動化可能路徑：以 Csc Task 收集所有 .cs 自動化輸出，但學習與維護成本較高（優先級: 低）
- 命名與輸出位置管理：避免 /doc 文件被覆蓋，需規劃唯一檔名與分目錄輸出（優先級: 中）
- 專案型別選擇：若長期需完整文件，評估改用 Web Application 模型較易產出 DLL+XML（優先級: 中）
- CI/部署整合：將 csc 或 aspnet_compiler + 合併流程納入 CI，穩定產出文件工件（優先級: 中）
- 文件範圍說明：明確在文件中標註哪些 API 來自共用庫、哪些 UI/動態生成部分未涵蓋（優先級: 低）