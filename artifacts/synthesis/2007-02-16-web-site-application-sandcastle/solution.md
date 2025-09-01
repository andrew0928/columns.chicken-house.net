以下為依據文章內容重構的 16 個可教學、可演練、可評估的問題解決案例。每個案例均包含問題、根因、解法、關鍵程式碼/設定、實測或效益、學習要點與練習與評估。

## Case #1: 使用 csc.exe 產出 App_Code 的 DLL 與 XML Doc，餵給 NDoc/Sandcastle

### Problem Statement（問題陳述）
- 業務場景：ASP.NET 2.0 Web Site 專案多以 App_Code 放置共用類別，團隊希望把 C# 的 XML 註解生成 API 說明文件，供內部共用與交付客戶參考，並維持與實際程式碼同步。NDoc/Sandcastle 都需要 DLL 與對應 XML 文件，然而 Web Site 模型預設不產出這兩者。
- 技術挑戰：Web Site 非專案制，App_Code 以動態方式被編譯，沒有固定 DLL 與 XML Doc 輸出。
- 影響範圍：無法產生正式文件，開發與維運人員難以查詢 API，影響知識傳遞與維護效率。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. ASP.NET 2.0 Web Site 的 App_Code 採動態編譯，不預設輸出 DLL。
  2. XML 註解檔需在編譯時以 /doc 選項產出，但動態編譯流程未提供整站單一 XML。
  3. Sandcastle/NDoc 皆需「組件 + XML 註解」配對作為輸入。
- 深層原因：
  - 架構層面：Web Site 模型未以專案制的 Assembly 輸出為核心。
  - 技術層面：缺少可控的集中式編譯步驟來同時產出 DLL 與 XML。
  - 流程層面：沒有在 CI/Build 流程中納入 API 文件輸出。

### Solution Design（解決方案設計）
- 解決策略：以 csc.exe 直接對 App_Code 下的 .cs 進行命令列編譯，產出單一 DLL 與 XML Doc，作為文件工具的輸入。此法不改動站台執行模式，且保障「單一碼源」。
- 實施步驟：
  1. 收斂來源檔
     - 實作細節：確認 App_Code 內部僅含 C# 原始碼與可由 csc 直接編譯的檔案。
     - 所需資源：檔案管理權限
     - 預估時間：0.5 小時
  2. 命令列編譯
     - 實作細節：用 /recurse 遞迴收集 .cs，/target:library 產 DLL，/doc 產 XML。
     - 所需資源：.NET 2.0 csc.exe
     - 預估時間：0.5 小時
  3. 交給文件工具
     - 實作細節：將 DLL + XML 指定給 NDoc/Sandcastle 的建置流程。
     - 所需資源：NDoc 或 Sandcastle
     - 預估時間：0.5 小時
- 關鍵程式碼/設定：
```bat
:: 於解決方案根目錄執行
csc.exe /out:App_Code.dll ^
       /doc:App_Code.xml ^
       /target:library ^
       /recurse:App_Code\*.cs
```
- 實際案例：文中作者以此指令成功產生 DLL 與 XML，之後交給 NDoc/Sandcastle。
- 實作環境：Windows, .NET 2.0, ASP.NET 2.0 Web Site, csc.exe, Sandcastle/NDoc
- 實測數據：
  - 改善前：缺少 DLL/XML，文件工具無法運作
  - 改善後：成功產出 App_Code.dll + App_Code.xml，可餵給文件工具
  - 改善幅度：可用性由 0% 提升為可生成

Learning Points（學習要點）
- 核心知識點：
  - Web Site 的動態編譯與專案式編譯差異
  - csc.exe /recurse、/doc、/target 的用法
  - 文件工具對輸入的要求（DLL + XML）
- 技能要求：
  - 必備技能：C# 專案基本結構、命令列操作
  - 進階技能：建置腳本化與文件產線整合
- 延伸思考：
  - 可否將此步驟整合到 CI？
  - 缺少 wsdl/xsd/ascx 生成碼如何處理？
  - 是否需要拆分 class library 以提高覆蓋率？
- Practice Exercise：
  - 基礎：對示例網站執行指令，檢查輸出檔（30 分鐘）
  - 進階：將指令寫成可重複使用的批次檔（2 小時）
  - 專案：把生成步驟串入文件工具，輸出 CHM/HTML（8 小時）
- Assessment Criteria：
  - 功能完整性（40%）：是否成功輸出 DLL + XML 並可被工具使用
  - 程式碼品質（30%）：批次檔可維護、參數化
  - 效能優化（20%）：編譯時間可接受、無重工
  - 創新性（10%）：對不同環境/路徑的相容性設計

---

## Case #2: 在 web.config 設定 compilerOptions /doc 於多層 App_Code 導致 XML 被覆寫

### Problem Statement（問題陳述）
- 業務場景：嘗試在 Web Site 的 web.config 透過 <compiler compilerOptions="/doc:..."> 讓動態編譯同時輸出 XML Doc，期望在不改動編譯流程的前提下自動產生文件，便於快速上線與維運。
- 技術挑戰：在實際 production 環境中，XML 檔案不斷被產生又刪除，或最後結果被覆蓋，無法得到穩定完整的單一 XML 輸出。
- 影響範圍：文件生成不穩定且不可預期，甚至造成 I/O 擁塞與部署困擾。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. App_Code 以目錄為單位分次編譯，造成多次 /doc 寫入同一檔案。
  2. /doc 參數必須指定檔名，不支援萬用字元或自動合併。
  3. 動態編譯期間可能清理暫存，導致檔案被刪除。
- 深層原因：
  - 架構層面：目錄為顆粒度的動態編譯策略。
  - 技術層面：CodeDom /doc 缺少多輸出合併能力。
  - 流程層面：未分離「執行期動態編譯」與「文件產生」責任。

### Solution Design（解決方案設計）
- 解決策略：不在 production 使用此方法；若 App_Code 僅單層且檔案不多，可於開發或測試環境短期使用；長期改以離線 csc 方式生成。
- 實施步驟：
  1. 評估目錄深度
     - 實作細節：確認 App_Code 是否僅單層。若多層則不採此法。
     - 所需資源：檔案樹視圖
     - 預估時間：0.2 小時
  2. web.config 試行（僅單層）
     - 實作細節：設定 compilerOptions /doc 指向固定路徑。
     - 所需資源：web.config 編輯權限
     - 預估時間：0.3 小時
  3. 生產環境關閉
     - 實作細節：生產移除該設定，改用離線生成。
     - 所需資源：環境管理
     - 預估時間：0.3 小時
- 關鍵程式碼/設定：
```xml
<configuration>
  <system.codedom>
    <compilers>
      <compiler language="c#;cs;csharp"
                compilerOptions="/doc:c:\temp\AppCode.xml" />
    </compilers>
  </system.codedom>
</configuration>
```
- 實際案例：作者在範例網站可行，但上 production 後 XML 不斷被產生又刪除，最終放棄。
- 實作環境：ASP.NET 2.0 Web Site, CodeDom 編譯
- 實測數據：
  - 改善前：無法生成任何 XML Doc
  - 改善後（單層目錄）：可生成；多層：失敗/覆蓋
  - 改善幅度：僅限單層場景可用

Learning Points（學習要點）
- 核心知識點：App_Code 分目錄編譯行為；/doc 限制
- 技能要求：web.config/CodeDom 基本設定
- 延伸思考：是否能以離線方式避免動態編譯副作用？
- Practice Exercise：在單層 App_Code 專案測試 /doc 設定（30 分鐘）；觀察多層時的失效行為（2 小時）；撰寫回報（8 小時）
- Assessment Criteria：是否能清楚辨識該法的場景限制與風險

---

## Case #3: Production 環境 XML 檔反覆生成與刪除的穩定性問題

### Problem Statement（問題陳述）
- 業務場景：在生產站點套用 web.config /doc 後，監控發現目標 XML 文件被頻繁建立與刪除，導致磁碟 I/O 異常、部署檔遭到覆蓋，影響系統穩定。
- 技術挑戰：如何避免執行期動態編譯造成的文件波動，確保生產環境穩定，同時滿足文件產出需求。
- 影響範圍：生產站穩定性、部署正確性、觀測資料可靠性。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. App_Code 子目錄編譯多次觸發 /doc 寫入。
  2. 編譯過程的清理步驟刪除先前生成檔。
  3. 指定單一檔名導致覆蓋競爭。
- 深層原因：
  - 架構層面：動態編譯與運行交織，缺少明確分層。
  - 技術層面：/doc 不支援安全合併。
  - 流程層面：缺少「文件產出在離線建置」的規範。

### Solution Design（解決方案設計）
- 解決策略：將文件產生從生產環境抽離，統一在離線建置（例如開發機或打包機）使用 csc 生成；生產環境維持純執行。
- 實施步驟：
  1. 移除 production /doc
     - 實作細節：恢復 web.config，刪除 compilerOptions。
     - 所需資源：環境存取
     - 預估時間：0.2 小時
  2. 設置離線建置點
     - 實作細節：於建置機執行 csc 輸出 DLL + XML。
     - 所需資源：csc.exe, 檔案權限
     - 預估時間：0.5 小時
  3. 文件發佈
     - 實作細節：文件與網站部署解耦，按需上傳。
     - 所需資源：檔案佈署權限
     - 預估時間：0.5 小時
- 關鍵程式碼/設定：同 Case #1 的 csc 指令
- 實際案例：文中作者觀察 production 不穩定後，放棄於生產站生成 XML。
- 實作環境：ASP.NET 2.0 Web Site
- 實測數據：
  - 改善前：XML 檔反覆產生/刪除
  - 改善後：生產無文件生成 I/O；文件由離線建置提供
  - 改善幅度：穩定性顯著提升（避免競爭與覆蓋）

Learning Points：動態編譯不等於建置；生產與建置應隔離
- Practice：移除/還原 /doc 設定並驗證行為（30 分鐘）；撰寫離線建置腳本（2 小時）
- Assessment：能否避免生產 I/O 擾動且保留文件產出能力

---

## Case #4: Web Deployment Project 可得 DLL 但無 XML 的補救方案

### Problem Statement（問題陳述）
- 業務場景：使用 Visual Studio 2005 的 Web Deployment Project（WDP）打包 Web Site，可得到合併後的單一 DLL，方便部署；但文件工具仍需要 XML 註解檔，WDP 無法直接提供。
- 技術挑戰：如何在保留 WDP 優勢的前提下補齊 XML 註解輸入。
- 影響範圍：自動化部署流程、文件產線一致性。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. WDP 以 aspnet_compiler + 合併工具為核心，非 C# 編譯器，未輸出 XML Doc。
  2. NDoc/Sandcastle 需要 XML 才能包含註解內容。
- 深層原因：
  - 架構層面：部署打包與文件生成屬不同產線。
  - 技術層面：缺少一步產出 DLL+XML 的統一工具。
  - 流程層面：未建立 WDP 與 csc 的協同流程。

### Solution Design
- 解決策略：WDP 持續負責部署 DLL；另以 csc 對 App_Code 生成 XML 與（必要時）一個對應 DLL 給文件工具使用。
- 實施步驟：
  1. 執行 WDP 打包
     - 實作細節：產生單一合併 DLL 用於部署。
     - 所需資源：VS2005 SP1
     - 預估時間：依專案
  2. csc 生成文件輸入
     - 實作細節：對 App_Code 執行 Case #1 指令，產出 App_Code.xml（與 DLL 可不同名）。
     - 所需資源：csc.exe
     - 預估時間：0.5 小時
  3. 文件建置
     - 實作細節：用 csc 輸出的 DLL+XML 作文件輸入。
     - 所需資源：Sandcastle/NDoc
     - 預估時間：依工具
- 關鍵設定：同 Case #1 csc 指令
- 實際案例：作者指出 WDP 能出 DLL 但 XML 無解，最後以 csc 另行產出 XML 解決。
- 實作環境：VS2005 SP1, WDP, ASP.NET 2.0
- 實測數據：
  - 改善前：僅有 DLL，文件建置缺 XML
  - 改善後：DLL + XML 齊備，可建置文件
  - 改善幅度：文件產線恢復可用

Learning Points：部署產線與文件產線分工
- Practice：將 WDP 與 csc 兩步驟併入一個批次流（2 小時）
- Assessment：是否能穩定產出部署包與文件輸入

---

## Case #5: 以 MSBuild Csc Task 自動化 App_Code 編譯與 XML 生成

### Problem Statement（問題陳述）
- 業務場景：團隊想避免手動執行 csc 指令，改以 MSBuild 專案化，讓 CI 可重複執行且易於維護。
- 技術挑戰：Web Site 本身並無 csproj，需要手寫 MSBuild 專案檔，熟悉 Csc Task 與 ItemGroup。
- 影響範圍：CI/CD 整合、自動化程度與透明度。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. Web Site 模型沒有現成的 MSBuild 專案。
  2. 需以 Csc Task 自行指定 Sources 與輸出。
- 深層原因：
  - 架構層面：缺少專案制管理。
  - 技術層面：MSBuild 腳本能力不足。
  - 流程層面：尚未把文件生成納入 CI。

### Solution Design
- 解決策略：撰寫簡單的 MSBuild 專案檔，使用 Csc Task 收集 App_Code 下所有 .cs，輸出 DLL+XML；後續串接文件工具。
- 實施步驟：
  1. 建立 AppCode.proj
     - 實作細節：建立 ItemGroup 與 Csc Task。
     - 所需資源：MSBuild
     - 預估時間：1 小時
  2. 串接文件工具
     - 實作細節：建置後呼叫文件工具命令或腳本。
     - 所需資源：Sandcastle/NDoc
     - 預估時間：1 小時
- 關鍵程式碼/設定：
```xml
<Project ToolsVersion="2.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <ItemGroup>
    <Compile Include="App_Code\**\*.cs" />
  </ItemGroup>
  <Target Name="BuildAppCode">
    <Csc Sources="@(Compile)"
         TargetType="Library"
         OutputAssembly="App_Code.dll"
         DocumentationFile="App_Code.xml" />
  </Target>
</Project>
```
- 實際案例：文中提及老外以 Csc Task 解法；作者因成本未採用，但此為可行路徑。
- 實作環境：MSBuild, .NET 2.0
- 實測數據：
  - 改善前：需手動命令列
  - 改善後：一鍵/CI 即可生成
  - 改善幅度：自動化程度提升

Learning Points：MSBuild ItemGroup/Target/Csc Task 基本用法
- Practice：將 Csc Task 加上組態參數化（2 小時）；專案：串接 Sandcastle 腳本（8 小時）
- Assessment：腳本可維護、可重複、可在 CI 運行

---

## Case #6: 用 /recurse 遞迴收集 App_Code 子目錄 .cs，繞過分目錄編譯限制

### Problem Statement（問題陳述）
- 業務場景：App_Code 常含多層子目錄，動態編譯以目錄為單位造成 XML 輸出覆寫。希望在離線建置時，一次性收集所有 .cs 檔避免覆寫。
- 技術挑戰：需在不依賴動態編譯的情況下收集所有來源檔並一次輸出。
- 影響範圍：文件完整性與輸出穩定性。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 動態編譯的分目錄策略導致多次輸出。
  2. /doc 不支援合併。
- 深層原因：
  - 架構層面：網站執行期與建置期混用。
  - 技術層面：未集中收斂來源。
  - 流程層面：缺乏離線一次性建置。

### Solution Design
- 解決策略：在 csc 指令採用 /recurse:App_Code\*.cs 遞迴包含，集中一次性編譯，輸出單一 DLL 與 XML。
- 實施步驟：
  1. 清查來源
  2. 執行 csc /recurse
  3. 檢核輸出（DLL 與 XML）
- 關鍵程式碼：
```bat
csc.exe /out:App_Code.dll /doc:App_Code.xml /target:library /recurse:App_Code\*.cs
```
- 實際案例：作者以此成功一次性產出輸入檔。
- 實作環境：.NET 2.0
- 實測數據：
  - 改善前：XML 被覆寫/不完整
  - 改善後：單一完整 XML
  - 改善幅度：文件穩定性大幅提升

Learning Points：/recurse 的實務價值
- Practice：改寫現有腳本採 /recurse（30 分鐘）
- Assessment：輸出是否完整且穩定

---

## Case #7: App_Code 內含 wsdl/xsd 造成 csc 無法涵蓋的空缺管理

### Problem Statement（問題陳述）
- 業務場景：App_Code 放入 wsdl/xsd 檔，ASP.NET 會自動生成 Web Service Proxy、Typed DataSet；但 csc 直接編譯 App_Code\*.cs 無法觸發此類生成，導致文件缺漏。
- 技術挑戰：如何面對這些非 .cs 的來源造成的缺口。
- 影響範圍：文件覆蓋度、API 與文件一致性。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. wsdl/xsd 依賴 ASP.NET Build Providers 轉為 .cs 再編譯。
  2. csc 不會自動處理這些轉換。
- 深層原因：
  - 架構層面：站台建置流程含動態轉譯階段。
  - 技術層面：離線編譯與 Build Provider 不相容。
  - 流程層面：未定義對此類檔案的文件策略。

### Solution Design
- 解決策略：短期策略是接受文件不涵蓋此類自動生成碼（文中作者決策）；明確於文件範圍聲明；集中精力於有註解之共用類別。
- 實施步驟：
  1. 標注範圍
  2. 文件說明缺口
  3. 未來改進方案評估（另立專案或工具）
- 關鍵設定：無（範疇管理/流程決策）
- 實際案例：作者列為 csc 方法的缺點之一且選擇接受。
- 實作環境：ASP.NET 2.0 Web Site
- 實測數據：
  - 改善前：期待全面覆蓋但不可行
  - 改善後：明確範圍、降低落差
  - 改善幅度：預期管理改善

Learning Points：範圍管理與風險揭露
- Practice：撰寫文件「覆蓋說明」章節（30 分鐘）
- Assessment：是否清楚揭露與約束使用者期待

---

## Case #8: ascx/aspx 對應 partial class 無法由 csc 編譯的處理策略

### Problem Statement（問題陳述）
- 業務場景：.ascx/.aspx 的 code-behind 為 partial class，另一半由 ASP.NET 解析模板時動態生成，csc 無法單獨編譯完整類型，導致這些 UI 類型的 API 無法文件化。
- 技術挑戰：如何面對 UI 元件無法直接進入文件產線。
- 影響範圍：UI 層 API 文件缺失。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. partial class 的另一半由模板解析動態產生。
  2. csc 缺少這一半，編譯不完整。
- 深層原因：
  - 架構層面：UI 模板驅動生成。
  - 技術層面：離線編譯與動態生成斷裂。
  - 流程層面：未規劃 UI 文件化途徑。

### Solution Design
- 解決策略：短期接受 UI 類型不納入文件；聚焦可重用的業務/工具類別；待有更便利工具再補齊（文中作者選擇）。
- 實施步驟：
  1. 文件範圍定義
  2. 對使用者說明 UI 類型不在此版文件
  3. 追蹤工具演進（如未來更佳支援）
- 關鍵設定：無
- 實際案例：作者明確指出 .ascx 是很需要但暫時放棄。
- 實作環境：ASP.NET 2.0
- 實測數據：
  - 改善前：期待記錄 UI API，但工具不支援
  - 改善後：明確取捨，降低溝通成本
  - 改善幅度：可交付性提升

Learning Points：取捨與溝通管理
- Practice：撰寫一段「UI 類型文件後續計畫」說明（30 分鐘）
- Assessment：是否在限制下交付可用文件

---

## Case #9: 單一碼源原則：避免為文件另寫一份程式碼

### Problem Statement（問題陳述）
- 業務場景：文件生成若需要維護第二份來源或樣板，將導致同步困難與錯誤。目標是在不複製程式碼的前提下產生 API 文件。
- 技術挑戰：確保 csc 編譯來源即為網站實際使用的 App_Code 內容。
- 影響範圍：維護成本、錯誤率。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 文件與程式碼不同步會引發品質問題。
  2. 另寫一份碼源難以維護。
- 深層原因：
  - 架構層面：未建立單一碼源的產線。
  - 技術層面：工具鏈需指向同一來源。
  - 流程層面：文件產生須嵌入建置流。

### Solution Design
- 解決策略：csc 直接針對 App_Code\*.cs；不建立任何「文件專用」碼源。
- 實施步驟：
  1. 確認文件註解風格統一
  2. 建置腳本指向 App_Code
  3. 文件工具輸入採用建置輸出
- 關鍵程式碼：同 Case #1
- 實際案例：作者強調「不要寫兩份 code」的原則。
- 實作環境：.NET 2.0
- 實測數據：
  - 改善前：存在需維護第二份碼源的風險
  - 改善後：單一碼源產線
  - 改善幅度：同步風險降為最低

Learning Points：Single Source of Truth
- Practice：檢視 repo 是否存在文件專用副本並移除（30 分鐘）
- Assessment：產線是否僅以 App_Code 為唯一來源

---

## Case #10: 將 App_Code.dll + App_Code.xml 串接到 NDoc 的工作流程

### Problem Statement（問題陳述）
- 業務場景：既有文件工具 NDoc 可快速生成 CHM，但需要組件與 XML。團隊希望用 csc 的輸出直接生成傳統說明文件。
- 技術挑戰：整合輸入與工具，確保輸出格式與結構符合需求。
- 影響範圍：對外交付文件的可讀性與可檢索性。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. NDoc 需要匹配的 DLL 與 XML。
- 深層原因：
  - 架構層面：文件工具設計即依賴編譯產物。
  - 技術層面：需準備正確映射。
  - 流程層面：缺少自動化串接。

### Solution Design
- 解決策略：使用 csc 生成的 DLL + XML 作為 NDoc 專案輸入，按 NDoc 流程建立 CHM。
- 實施步驟：
  1. 生成 DLL + XML（Case #1）
  2. 建立 NDoc 專案（指定輸入）
  3. 執行生成
- 關鍵設定/範例：以工具 UI 或簡單批次整合（依團隊既有流程）
- 實際案例：作者過去以 NDoc 生成 CHM，約 20 分鐘完成。
- 實作環境：NDoc, .NET 2.0（注意版本相容性）
- 實測數據：
  - 改善前：無法輸入
  - 改善後：可生成 CHM
  - 改善幅度：可用性建立；時間參考 ~20 分鐘

Learning Points：輸入配對與輸出格式
- Practice：建立最小 NDoc 專案（30 分鐘）
- Assessment：CHM 是否完整含註解

---

## Case #11: 將 App_Code.dll + App_Code.xml 串接到 Sandcastle 的工作流程與成本

### Problem Statement（問題陳述）
- 業務場景：需要支援 .NET 2.0 新特性（如泛型）的文件生成，選擇 Sandcastle。團隊觀察到生成速度較慢。
- 技術挑戰：準備輸入與預期較長的生成時間，安排行程與資源。
- 影響範圍：建置時間、CI pipeline 佔用。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. Sandcastle 流程較複雜，支援新特性代價是耗時。
  2. 需要 DLL + XML 作輸入。
- 深層原因：
  - 架構層面：文件生成管線分多步。
  - 技術層面：泛型等符號處理成本高。
  - 流程層面：缺少時間/資源規劃。

### Solution Design
- 解決策略：以 csc 生成輸入檔，再交給 Sandcastle；預留較長生成時間並在非尖峰時段執行。
- 實施步驟：
  1. 生成 DLL + XML（Case #1）
  2. 執行 Sandcastle 建置（依工具指引）
  3. 排程與資源預留
- 關鍵設定：輸入對應（Assembly + XML）
- 實際案例：作者觀察 Sandcastle 約 60 分鐘，相較 NDoc 20 分鐘較慢。
- 實作環境：Sandcastle（當年 CTP/版本）
- 實測數據：
  - 改善前：無法支援泛型等特性
  - 改善後：可支援但耗時 ~60 分鐘
  - 改善幅度：功能覆蓋↑，時間成本↑

Learning Points：功能與建置時間的權衡
- Practice：在離峰時段執行一次完整生成（2 小時）
- Assessment：輸出正確性與時間預估能力

---

## Case #12: Sandcastle 與 NDoc 的速度差異帶來的工具選型

### Problem Statement（問題陳述）
- 業務場景：小型或非泛型專案可能偏好較快的 NDoc；需 2.0 新特性的專案則需 Sandcastle。團隊需在速度與功能間做選型。
- 技術挑戰：平衡功能覆蓋與建置時間。
- 影響範圍：交付節奏、CI 負載、開發者等待時間。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. Sandcastle 支援新特性，但耗時較長。
  2. NDoc 生成較快，功能較有限。
- 深層原因：
  - 架構層面：工具能力差異。
  - 技術層面：符號處理深度不同。
  - 流程層面：未定義選用準則。

### Solution Design
- 解決策略：按專案需求選擇工具；對於需要泛型等特性者用 Sandcastle；否則優先 NDoc 縮短時間。
- 實施步驟：
  1. 梳理需求（是否有泛型等）
  2. 選擇工具並記錄預估時間
  3. 在 CI 中設置對應 Job
- 關鍵設定：無
- 實際案例：文中數據 NDoc ~20 分鐘 vs Sandcastle ~60 分鐘。
- 實作環境：同上
- 實測數據：
  - 改善前：工具選型模糊
  - 改善後：依需求選擇工具
  - 改善幅度：建置時間可控

Learning Points：以需求導向工具選型
- Practice：對現有專案做一次選型評估（30 分鐘）
- Assessment：是否能以數據支持選型

---

## Case #13: App_Code 僅一層目錄時使用 web.config /doc 的可行方案

### Problem Statement（問題陳述）
- 業務場景：某些小型網站 App_Code 僅一層，欲快速讓動態編譯自動產生 XML Doc，避免額外腳本。
- 技術挑戰：確保輸出不被覆寫與刪除。
- 影響範圍：小型專案的敏捷性。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 單層目錄只會有一次 /doc 寫入。
- 深層原因：
  - 架構層面：目錄顆粒度與輸出穩定性相關。
  - 技術層面：/doc 只能單檔輸出。
  - 流程層面：針對小型站可用權衡。

### Solution Design
- 解決策略：在單層 App_Code 的前提下於 web.config 設定 /doc，限定於開發/測試環境使用。
- 實施步驟：
  1. 確認單層
  2. 設定 web.config（Case #2 設定）
  3. 限制環境適用
- 關鍵設定：同 Case #2
- 實際案例：作者指出單層情境可行。
- 實作環境：ASP.NET 2.0 Web Site
- 實測數據：
  - 改善前：無 XML 輸出
  - 改善後：可輸出（僅單層）
  - 改善幅度：建立快速道路

Learning Points：場景限定解
- Practice：建立只有單層 App_Code 的 Demo 測試（30 分鐘）
- Assessment：能否說明何時該改回離線 csc

---

## Case #14: 避免重造 aspnet_compiler：工程成本與收益權衡

### Problem Statement（問題陳述）
- 業務場景：理論上可用批次或 MSBuild 完整模擬 ASP.NET 動態編譯（含模板解析、Build Providers），產出完整文件輸入；但成本極高。
- 技術挑戰：工程投入可能接近重寫 aspnet_compiler，得不償失。
- 影響範圍：開發成本、風險、維護負擔。
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：
  1. 涉及模板解析、生成、合併等多步驟。
  2. 多種檔案型別需個別處理。
- 深層原因：
  - 架構層面：ASP.NET 建置管線複雜。
  - 技術層面：多工具協作與相依處理繁瑣。
  - 流程層面：非核心業務的過度工程化風險。

### Solution Design
- 解決策略：不重造；採取「必要可用」策略（Case #1 + Case #7 + Case #8 的取捨），先交付可用文件。
- 實施步驟：
  1. 明確最小可行文件範圍
  2. 以 csc 生成主體
  3. 將其餘檔案類型列為未來迭代目標
- 關鍵設定：無
- 實際案例：作者結論為「工程太大，不划算」。
- 實作環境：—
- 實測數據：
  - 改善前：企圖全面涵蓋導致進度停滯
  - 改善後：先達成可交付文件
  - 改善幅度：時程風險下降

Learning Points：MVP 思維與工程取捨
- Practice：撰寫一頁投資報酬分析（30 分鐘）
- Assessment：決策是否理性且可被團隊接受

---

## Case #15: 以批次檔封裝 csc 指令的最低成本自動化

### Problem Statement（問題陳述）
- 業務場景：團隊希望用最小投入讓開發者一鍵生成 DLL + XML，避免手動輸入命令出錯。
- 技術挑戰：兼顧路徑相對/絕對、錯誤處理與清理。
- 影響範圍：開發效率、一致性。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 手動輸入易誤。
  2. 開發者環境路徑各異。
- 深層原因：
  - 架構層面：缺少輕量工具鏈。
  - 技術層面：批次/腳本化不足。
  - 流程層面：未定義標準操作。

### Solution Design
- 解決策略：建立 build-docs.bat，封裝 csc 指令與輸出資料夾管理，供所有人共用。
- 實施步驟：
  1. 建立批次檔
  2. 統一輸出目錄（如 artifacts）
  3. 文檔指引與檢核
- 關鍵程式碼：
```bat
@echo off
setlocal
set SRC=App_Code\*.cs
set OUTDIR=artifacts
if not exist %OUTDIR% mkdir %OUTDIR%
csc.exe /out:%OUTDIR%\App_Code.dll ^
       /doc:%OUTDIR%\App_Code.xml ^
       /target:library ^
       /recurse:%SRC%
echo Output in %OUTDIR%
endlocal
```
- 實際案例：作者建議可放入批次或 MSBuild，但完整模擬引擎成本高；此為低成本版本。
- 實作環境：Windows
- 實測數據：
  - 改善前：手動操作耗時且易錯
  - 改善後：一鍵生成
  - 改善幅度：一致性與效率提升

Learning Points：可重用腳本設計
- Practice：加入錯誤碼與日誌輸出（2 小時）
- Assessment：腳本是否健壯且跨機器可用

---

## Case #16: 文件覆蓋範圍的取捨：聚焦可重用 Class Library

### Problem Statement（問題陳述）
- 業務場景：文件的主要價值在可重用的 Class Library；對 wsdl/xsd/ascx 類產物，當前工具鏈成本高且註解稀少。需明確聚焦，快速交付。
- 技術挑戰：在不完美覆蓋的現實下，保持高價值輸出。
- 影響範圍：文件使用體驗、團隊期待管理。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. UI/生成碼部分註解不足。
  2. 工具鏈無法低成本涵蓋。
- 深層原因：
  - 架構層面：不同層文件價值密度不同。
  - 技術層面：工具限制。
  - 流程層面：需要範圍治理。

### Solution Design
- 解決策略：文件首要覆蓋 App_Code 中有註解的共用類別；對其它區塊標註未覆蓋原因，避免誤解。
- 實施步驟：
  1. 列出高價值類別清單
  2. 專注註解質量與一致性
  3. 文檔中揭露覆蓋界線
- 關鍵設定：無
- 實際案例：作者表示「help file 主要就是為了能共用的 class library」，並選擇忽略其它。
- 實作環境：—
- 實測數據：
  - 改善前：覆蓋野心過大、進度慢
  - 改善後：快速交付核心文件
  - 改善幅度：交付效率提升

Learning Points：聚焦策略
- Practice：完成一份「文件覆蓋矩陣」（30 分鐘）
- Assessment：是否能有效聚焦且溝通清楚

========================
案例分類
========================

1) 按難度分類
- 入門級：Case 6, 9, 10, 13, 15, 16
- 中級：Case 1, 2, 3, 4, 5, 11, 12
- 高級：Case 7, 8, 14

2) 按技術領域分類
- 架構設計類：Case 3, 12, 14, 16
- 效能優化類：Case 11, 12
- 整合開發類：Case 1, 4, 5, 10, 11, 15
- 除錯診斷類：Case 2, 3, 6
- 安全防護類：—（本文未涉及安全）

3) 按學習目標分類
- 概念理解型：Case 2, 3, 12, 14, 16
- 技能練習型：Case 1, 5, 6, 10, 11, 15
- 問題解決型：Case 3, 4, 7, 8, 13
- 創新應用型：Case 5, 14

========================
案例關聯圖（學習路徑建議）
========================
- 建議先學：
  - Case 6（/recurse 與一次性離線編譯概念）
  - Case 1（用 csc 生成 DLL + XML 的核心技能）
  - Case 15（把核心技能封裝成批次）

- 依賴關係：
  - Case 1 是多數案例的前置（Case 4, 10, 11）
  - Case 2/3/13 說明使用 web.config /doc 的限制與可行場景，理解後更易決策採用 Case 1
  - Case 5（MSBuild）建立在 Case 1 的指令式經驗之上
  - Case 7/8/16 建立在你已有基本產線後的覆蓋度治理
  - Case 11/12 在有穩定輸入後選擇與優化文件工具
  - Case 14 作為整體工程化的取捨與上限認知

- 完整學習路徑：
  1) Case 6 → 1 → 15（掌握核心生成能力與最小自動化）
  2) Case 2 → 13 → 3（理解 web.config /doc 的可用邊界與生產環境風險）
  3) Case 5（進階自動化，以 MSBuild 專案化）
  4) Case 4（與 WDP 並行的文件補齊策略）
  5) Case 10 → 11 → 12（串接 NDoc/Sandcastle 並做工具選型）
  6) Case 7 → 8 → 16（文件覆蓋度的取捨與治理）
  7) Case 14（避免過度工程，形成長期策略）

以上各案例皆直接取材於原文敘述的問題、根因、解法與觀察數據（尤其文檔工具耗時對比），並整理為可教學、可演練且可評估的結構化內容。