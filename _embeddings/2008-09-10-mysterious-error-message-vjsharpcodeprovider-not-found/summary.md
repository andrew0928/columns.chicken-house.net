# 莫明奇妙的錯誤訊息: 找不到 VJSharpCodeProvider ?

## 摘要提示
- 開發背景: 升級與擴充 BlogEngine.NET 後，在 VS2008 建置網站時遇到怪異錯誤。
- 錯誤現象: Build 時出現找不到 VJSharpCodeProvider 的 CodeDom provider，沒有檔名與行號。
- 影響範圍: 專案可執行但無法編譯，導致無法設中斷點用 F5 直接除錯。
- 初步判斷: 未安裝 Visual J#；但專案未顯示使用 J# 相關設定或引用。
- 排查方向: 檢查 web.config 與 VS 專案設定、尋找可疑來源檔。
- 關鍵線索: 在 ~/App_Data/files 發現舊的 .java 檔案，觸發 VS 嘗試用 J# 編譯。
- 解決方法: 刪除 ~/App_Data 內的 .java 檔後，建置恢復正常。
- 問題根因: VS 在網站建置時會掃描並嘗試處理特定副檔名，即使位於 App_Data。
- 錯誤訊息不足: 訊息未指明來源檔與行號，增加排查難度。
- 實務建議: App_Data 也不宜隨意存放原始碼類型檔案，以免被建置流程波及。

## 全文重點
作者在將 BlogEngine.NET 升級到 1.4.5.0 並撰寫/修改多個擴充元件（如 SecurePost 與 PostViewCounter）時，為建立完整的測試環境，將網站原始碼搬入開發專案並補齊資料檔。建置過程中，Visual Studio 2008 回報「The CodeDom provider type 'Microsoft.VJSharp.VJSharpCodeProvider…' could not be located」的錯誤，且訊息沒有檔名與行號，僅顯示為 (0)，導致編譯失敗、無法以 F5 設斷點直接除錯，只能以手動 Attach Process 方式繞行，影響開發效率。

作者初步懷疑與 Visual J# 有關，但專案中並未設定使用 J#，web.config 亦無 CodeDom 或 CodeProvider 的相關設定，VS 專案也未引用 J# 程式庫，表面上不應觸發 J# 需求。由於錯誤訊息缺乏指向性，作者轉而以關鍵字與副檔名搜尋專案，意外在 ~/App_Data/files 中找到研究所時期的舊 Java Applet 原始碼（.java）。刪除該 .java 檔後，建置隨即恢復正常，問題迎刃而解。

從行為推測，VS 在網站專案建置時，會掃描專案內特定型別的程式碼檔並嘗試透過對應的 CodeDom provider 處理，即便檔案位於一般認為「不參與編譯」的 App_Data 資料夾。當專案中出現 .java 檔而系統未安裝 J# 對應的 CodeDom provider 時，即拋出找不到 VJSharpCodeProvider 的錯誤。然而錯誤訊息未包含來源檔資訊，使得問題定位困難。

作者最後總結：App_Data 也不是完全隔離於建置流程之外，放置原始碼類型的檔案（如 .java）可能觸發非預期的編譯行為；遇到類似無頭緒的 CodeDom provider 錯誤時，除了檢查設定，也應檢視專案中是否混入了其他語言的原始碼檔。更希望工具能提供更明確的錯誤內容（如檔名），以利快速除錯。

## 段落重點
### 問題背景與情境
作者在升級 BlogEngine.NET 至 1.4.5.0 並撰寫 SecurePost、修改 PostViewCounter 等 extension 的過程中，需要建立完整的開發與測試環境。從官方取得原始碼後編譯正常，再將網站專案移入（初期不含 App_Data），也可正常建置。為進行計數器相關測試，作者補入實際資料檔，準備進一步調整與除錯。

### 錯誤訊息與影響
在補入資料後，VS2008 出現建置錯誤：「The CodeDom provider type 'Microsoft.VJSharp.VJSharpCodeProvider…' could not be located」，且資訊貧乏，僅顯示 (0) 沒有檔名、行號。雖然網站仍可執行，但編譯失敗導致無法以 F5 方式直接除錯與設斷點，只能以 Attach Process 替代，嚴重降低開發效率，也讓問題溯源更加困難。

### 初步假設與設定檢查
作者聯想到自己未安裝 Visual J#，若專案確實用到 J#，錯誤情理之中；但檢查 web.config 並無 CodeDom 或 CodeProvider 指定，VS 專案設定也無 J# 相關引用。由於錯誤沒有具體檔案線索，判斷範圍偏向全域設定或建置流程層級的觸發，初期難以聚焦，可用的診斷資訊明顯不足。

### 排查過程與關鍵線索
在「死馬當活馬醫」的思路下，作者改以內容搜尋切入，檢索專案中是否有 .java 檔。結果在 ~/App_Data/files 找到過去的 Java Applet 原始碼。推測 VS 於網站建置時掃描到 .java，進而嘗試以 J# CodeDom provider 處理，但系統未安裝對應 provider，因而報錯。刪除該 .java 檔後，建置即恢復正常，證實根因。

### 反思與結論
此案例顯示 App_Data 並非完全隔離於建置與分析流程之外，原始碼類型檔案（如 .java）可能被 VS 視為需處理的來源，引發跨語言 provider 依賴。錯誤訊息未揭示來源檔，顯著增加排查難度。實務上應避免在 App_Data 放置會被建置流程誤判的檔案；遇到類似 CodeDom provider 錯誤時，除檢查設定外，也要全域搜尋可疑副檔名。作者對工具訊息表達不足提出批評，期望能包含檔名以利快速定位與修復。

## 資訊整理

### 知識架構圖
1. 前置知識：學習本主題前需要掌握什麼？
- 基本 ASP.NET Web Site 專案結構（App_Code、App_Data 等資料夾的用途）
- Visual Studio 編譯流程與 CodeDom/Build Provider 概念
- BlogEngine.NET 專案結構與部署方式
- 基本除錯技巧（F5、Attach to Process）

2. 核心概念：本文的 3-5 個核心概念及其關係
- CodeDom Provider：VS/ASP.NET 會依據檔案副檔名決定使用哪個語言提供者（如 VJSharpCodeProvider 對應 .java）
- Build/Compile 掃描範圍：即使在 App_Data，特定情境下也可能被掃描判斷需要編譯
- 依賴缺失導致的建置錯誤：未安裝 Visual J# 時遇到 .java 檔會觸發「找不到 VJSharpCodeProvider」
- 訊息可診斷性不足：錯誤沒有檔名與行號，追查需從全域設定與專案內容著手
- 專案內容清潔度：在 Web 專案中放入非目標語言的原始碼檔案，可能導致非預期的建置流程

3. 技術依賴：相關技術之間的依賴關係
- VS2008/ASP.NET 的建置系統依賴 CodeDom Provider 以對應各語言檔案
- .java 檔案觸發對 VJSharpCodeProvider 的需求；系統未安裝 Visual J# 即報錯
- BlogEngine.NET 為 Web Site 型專案，受 ASP.NET 建置/掃描行為影響
- web.config 的 compilation/codeDom 設定可影響語言提供者的解析（本文案例未顯示設定但需理解其影響）

4. 應用場景：適用於哪些實際場景？
- 升級或合併 Web 專案時搬移 App_Data 與歷史檔案
- 專案建置出現「找不到 CodeDom Provider」且無檔名行號的錯誤排查
- 清理專案中非必要或異質語言原始碼檔案以避免建置衝突
- 在無法 F5 的情況下以 Attach 方式暫時除錯並並行排錯

### 學習路徑建議
1. 入門者路徑：零基礎如何開始？
- 認識 ASP.NET Web Site 專案結構與各資料夾的用途
- 理解 VS 建置流程與錯誤訊息閱讀方法
- 熟悉 BlogEngine.NET 的基本部署與編譯步驟
- 練習從錯誤訊息反推可能的全域設定或檔案來源

2. 進階者路徑：已有基礎如何深化？
- 研究 ASP.NET Build Providers 與 CodeDom Provider 的運作機制
- 理解 web.config compilation/codeDom 的自訂與覆蓋行為
- 建立專案檔案治理策略（檔案型別白名單、資料夾隔離、CI 驗證）
- 掌握診斷無檔名/無行號錯誤的系統化流程（從全域至區域）

3. 實戰路徑：如何應用到實際專案？
- 在專案導入或升級時，先清查 App_Data 與非程式資源的檔案型別
- 設定 CI/檔案掃描工具避免將 .java 等非預期原始碼入庫
- 若需保留異質語言檔案，將其移至不被掃描的路徑或改壓縮封存
- 規劃降級替代方案（安裝相依 Provider 或移除觸發源），並撰寫 Runbook

### 關鍵要點清單
- CodeDom Provider 解析機制: VS/ASP.NET 會依副檔名選擇對應語言提供者進行建置或分析 (優先級: 高)
- VJSharpCodeProvider 依賴: .java 檔可能觸發對 Visual J# 提供者的需求，未安裝即報錯 (優先級: 高)
- App_Data 非完全免掃描: 在特定情境下 App_Data 也可能被掃描導致建置影響 (優先級: 高)
- 無檔名無行號錯誤診斷: 需從全域設定、檔案型別與專案結構進行回溯排查 (優先級: 高)
- BlogEngine.NET 專案特性: 為 Web Site 型，受 ASP.NET 建置/掃描行為影響較大 (優先級: 中)
- web.config 與 CodeDom 設定: 雖本例未設，但需理解其可覆蓋/指定 Provider 的能力 (優先級: 中)
- 檔案治理策略: 勿將異質語言原始碼（如 .java）直接置入 Web 專案內容 (優先級: 高)
- 升級/搬移風險控管: 搬移來源資料（含 App_Data）前先檢視與清理檔案型別 (優先級: 中)
- 除錯替代方案: 建置失敗時可用 Attach to Process 臨時除錯，但根因仍需修正 (優先級: 低)
- 快速修復手法: 移除觸發檔（.java）或安裝對應 Provider（Visual J#）均可解除 (優先級: 高)
- 訊息可用性不足的因應: 為不可行錯誤訊息建立排錯清單（掃描檔案型別→檢查 Provider→查 web.config） (優先級: 中)
- 專案資料夾用途界線: 理解並尊重各資料夾的預期用途，避免擴充到非預期內容 (優先級: 中)
- 測試資料管理: Sample data 應盡量以非原始碼形式存在（如 JSON/XML/壓縮包） (優先級: 中)
- CI/自動化檢查: 加入檔案型別規則與掃描，防止異質原始碼入庫或佈署 (優先級: 中)
- 文件化教訓: 將此類隱性建置風險納入團隊開發規範與導入手冊 (優先級: 低)