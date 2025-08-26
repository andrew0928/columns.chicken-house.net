# API & SDK Design #3, API 的向前相容機制

## 摘要提示
- 向前相容: 以「只增不減」的介面原則，確保新 API 能與舊版 SDK 共存運作
- 版本策略: 採 Compatible Versioning，伺服器只保留最新版本但承諾向前相容
- 合約管理: 以 API contracts 明確界定介面，透過權限與版控追蹤異動
- 合約落地: 以 runtime ActionFilter 檢查 controller 是否實作 contract 介面
- 版本編碼: 採用 Major.Minor.Build.Revision，依 Microsoft 慣例定義相容與不相容
- 版本溝通: 以 OPTIONS/回傳值傳遞版本，或以 Header 攜帶 SDK 所需版本
- 初始化檢查: SDK 建構時讀取 API 版本，檢核 Major/Minor 是否符合相容準則
- 呼叫時檢查: 在每次 API 呼叫前，由 Server 端 ActionFilter 比對要求與實際版本
- 廢止策略: 以 [Obsolete] 宣示逾期 API，待下次 Major 升級正式移除
- 實務建議: 善用單元測試、快取與組建版號自動化，降低維運風險與成本

## 全文重點
本文聚焦在微服務情境下，如何建立 API 對舊版 SDK 的向前相容機制，避免「You shall NOT pass!」的毀滅性相容性失敗。作者採用 Compatible Versioning：伺服器只保留單一最新版本，但保證對過去發佈後的 SDK 版本相容。為達成此目標，他將工作拆為三個關鍵檢查點：API contracts、版本識別機制、相容性政策。三者互相依存：contracts 讓介面變更可追溯且可控；版本識別將變更具體化為號碼；相容性政策則界定承諾範圍與廢止流程，讓服務可持續演進。

在合約面，REST 相較 WCF 缺少天然的 contract 介面束縛。作者以一組 runtime 的 ActionFilter 來補強：定義 IApiContract 標記介面與對應的 IBirdsApiContract，並在 Action 執行前反射檢查 controller 是否實作 contract、被呼叫的 action 是否名列 contract。雖然這不如 compile-time 嚴密且有性能成本，但搭配快取與單元測試可成為有效的第二道防線。整體原則是「介面只增不減」：已存在的 endpoint、方法簽章與參數不可更動或刪除，新增功能以擴充為之，確保既有 SDK 無需更新也能持續運作。

版本識別方面，採用 System.Version 的四段式編碼：Major 不相容、Minor 向前相容、Build/Revision 可忽略或留給建置系統使用。對應規則為：contract 未變更則版本不動；只擴充不破壞相容時增加 Minor；有破壞性變更時增加 Major；擬廢止項目以 [Obsolete] 宣示，待下次 Major 再移除。版本傳遞與檢測有兩種路徑：一是在 SDK 初始化時以 OPTIONS 或回傳值取得 API 版本，比對期望版本；二是在每次呼叫時，由 SDK 透過自訂 Header（如 X-SDK-REQUIRED-VERSION）傳送最低需求版本，Server 端 ActionFilter 於 action 執行前比對組件版號，直接拒絕不相容請求，避免無用的業務執行與狀態變更。

SDK 初始化檢查示例中，SDK 先呼叫 /api/birds 的 Options 取得版本字串，轉為 Version 後比對：Major 必須相同、Server 的 Minor 不得低於 SDK 需求。若不相容則直接在建構過程丟出例外，提醒用戶端明確處置。然而在長生命週期的情境（如常駐的單例 SDK）中，僅初始化檢查不足，故示範了呼叫時檢查：SDK 為所有 HTTP 請求加上 X-SDK-REQUIRED-VERSION，Server 端在 ActionFilter 讀取 Header 與當前組件版本（AssemblyVersion）比對，若不符則拋出 InvalidOperationException，ASP.NET Web API 會將錯誤序列化為 JSON 返回 SDK，使 SDK 得以針對錯誤碼與訊息做更精準處理。

文末總結：只保留最新 API 版本的策略能顯著降低維運複雜度，但前提是嚴格落實 contract 管控、清楚的版本編碼與檢核、明確的相容性與廢止政策。配合單元測試將規格內化、以快取降低 runtime contract 檢查成本、讓建置系統接管版號，便能讓 API/SDK 擁有長期演進的韌性。下一步作者將示範當 API 升級與 SDK 最佳化時，如何以這套機制安全渡過過渡期，驗證設計在真實演進下的可靠性。相關範例源碼已公開於 GitHub 的 dev-VER 分支，與本文內容同步。

## 段落重點
### "You shall NOT pass!"
作者以甘道夫攔炎魔的畫面比喻「相容性守門」的重要：若 API 沒有妥善設計向前相容，使用你服務的 App 將在升級後直接失效。API 與 SDK 在「當下」能合作只是約定；關鍵在於「承諾」：新 API 要能與過去某時間點以後的所有 SDK 版本相容。為避免不經意的破壞性變更導致舊版 SDK 壞掉，作者提出三個檢查點：一是 API contracts，將介面視為可控資產，異動需授權並可追蹤；二是明確的版本識別機制，讓 SDK 能檢測自身可否安全呼叫 API；三是版本相容策略，因為不可能永久相容，故需事先定義承諾邊界與報廢程序，給用戶端充裕緩衝期。這些設計環環相扣，目的都是在變更頻繁、團隊合作與長期營運的真實環境中，把「不小心破壞相容性」的風險降到最低。

### 碎碎念: API 的版本策略
API 版本管理在全球唯一實例的 HTTP 服務尤其棘手。常見策略有三：無版本且只保留最新版（The Knot）、並行多版本（Point-to-Point）、以及只保留最新版但保證向前相容的 Compatible Versioning。作者採第三種：伺服器僅保留最新版本，但新版本須能服務舊 SDK。這降低多版本維護成本，同時以相容性承諾維持開發者信任。代價是對設計與流程的更高要求：一旦宣告過的介面就不得刪改，參數與行為變更需審慎，避免「手癢」的修改滲出到正式版本。為此，作者設定三個 check point（contract、版本識別、相容政策）作為制度化防線，並強調「只增不減」的演進哲學，必要時以 [Obsolete] 宣示未來廢止，讓升級具備可預期性。

### API Contracts
WCF 天生以 contracts 驅動，容易在編譯期保障介面穩定；但在 ASP.NET Web API/REST 環境，contract 的束縛不明顯。作者提出一套 runtime 檢查：以 IApiContract 作為標記介面，定義 IBirdsApiContract 列出對外可呼叫 action，controller 實作該介面，並以 ContractCheckActionFilter 在 action 執行前反射檢查 controller 是否有對應介面與方法。這雖非完美（非編譯期、每請求有成本），但可透過快取減少反射開銷、搭配單元測試形成雙重保障；測試可視為一種「活的規格」，但不適合作為唯一的版控依據，因為測試修正不等於規格變更。核心原則是將相容性問題化約為「介面集合」的管控：一旦介面被視為合約，後續演進就必須遵守「只增不減」；資料契約（如 BirdInfo）同理。當這些規則被制度化與工具化，團隊更能在多人協作下持續交付而不破壞既有用戶。

### API / SDK Versioning
本段分兩小節：版本編號的意義與標示方式。首先採用 System.Version（Major.Minor.Build.Revision）的語義：Major 不相容、Minor 保持向前相容、Build 代表重編譯、Revision 多用於安全/小修且可完全互換。對應到 contract 的規則為：未變更不改 Major/Minor；只擴充不破壞則加 Minor；破壞性變更加 Major；欲廢止則標記 [Obsolete]，待下個 Major 移除。標示方式上，作者提供兩種：一是提供 API 能回傳自身版本（例如 OPTIONS /api/birds 回傳「10.26.0.0」），使 SDK 在初始化時即可確認；二是在一般呼叫的回應內夾帶版本字串供參考。實作上可在 controller 加入 Options 方法並由 SDK 建構式呼叫，或讀取組件 AssemblyVersion 以利建置系統統一控管版號。這些手段讓版本成為一等公民，便於 SDK 做出精準判斷與保護性失敗。

### 版本編號的意義
作者引用 MSDN 對 Version 類型的定義，闡明相容性與版號之間的對映：Major 差異代表非相容、Minor 升級代表功能擴充但保持相容、Build 與 Revision 通常由建置系統生成並可忽略。以此建立團隊規約：contract 不變則 Major.Minor 不動；擴充不破壞加 Minor；破壞性改動加 Major；擬廢止以 [Obsolete] 宣示延後移除。這將抽象的「相容性」具體化為簡單可檢查的條件，有助於自動化檢核與開發者心智模型的對齊。配合原始碼版控記錄 contract 異動點，能清楚界定每次發佈的相容性承諾，減少溝通成本與誤用風險，也為 SDK 在執行前與執行時的機制提供判斷依據。

### 標示 API 版本編號的方式
除文件溝通外，版本須在執行期可被 SDK 機械化取得。作者示範兩種：透過 Options 端點明確取回版本字串；或在各 API 回傳值中夾帶版本。一般建議以第一種為主，以便 SDK 在初始化時先做硬性檢核，避免啟動後才發現不相容。配合 .NET 組件的 AssemblyVersion，可在 AssemblyInfo.cs 設定 Major.Minor.*.*，由 msbuild 產生 Build/Revision，方便建置伺服器統一控版，保證整組發佈組件版號一致。這些實務有助於將版本管理從手動、文書化工作轉為自動化流水線的一部分，降低人為疏失，並讓 SDK 有穩定的資訊來源判斷是否可安全運作。

### 版本相容性政策 (SDK init 時檢查)
此法於 SDK 建構時即檢核相容性：SDK 內部宣告所需最低 API 版本（_require_API_version），呼叫 API 取得實際版本（_actual_API_version），以 Major 必須相同、Server Minor >= SDK 需求為準則比對。若不符，直接在建構過程丟出 InvalidOperationException，讓客戶端在啟動早期就中止，避免後續誤操作。這種啟動前檢查對「短生命週期」的 SDK 特別有效，能明確提醒升級或切換環境。然而對「長生命週期」的常駐 SDK，僅初始化檢查不足以涵蓋期間可能發生的後端升級，需搭配呼叫時檢查作為冗餘保護，以避免 SDK 持有過期相容假設而在運行數月後才暴雷。

### 版本相容性政策 (呼叫 API 時檢查)
為解決長生命週期與「先執行後發現不相容」的問題，作者示範在每次呼叫時由 Server 端把關。SDK 以 HttpClient 預設標頭加入 X-SDK-REQUIRED-VERSION，攜帶自身所需最低 API 版本；Server 端用 SDKVersionCheckActionFilter 讀取 Header，取得當前組件版號，於 action 執行前比對 Major/Minor，不符即拋出 InvalidOperationException。ASP.NET Web API 會將例外序列化為 JSON 回傳，使 SDK 可以更精準處理錯誤。此法可避免業務邏輯已執行才發現不相容，並為未來「根據 SDK 版本降級回應」等策略預留空間。結合 contract 檢查與版本檢查兩個 ActionFilter，便形成「介面守門＋版本守門」的雙保險；再配合快取與良好錯誤處理，能在不大幅增加延遲的前提下顯著降低風險。

### 結語
採用「只保留最新版本＋向前相容」的策略，能在維運成本與開發者體驗之間取得良好平衡，但前提是制度化的 contract 管控、清楚的版號語義與自動化檢核，以及有紀律的廢止流程。本文提供的實作藍圖包括：runtime contract 檢查（可快取）、SDK 初始化與呼叫時的雙階段版本檢核、自訂 Header 傳遞需求版號、AssemblyVersion 統一控版與 [Obsolete] 宣告。搭配單元測試把規格內化，可讓 API/SDK 在長期演進中保持穩健。下一篇將實際演練 API 升級與 SDK 最佳化下的相容性過渡，驗證這套機制在真實版本演進中的可用性。本文所有程式碼同步於 GitHub dev-VER 分支，供讀者對照實作細節。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - RESTful API 基礎（HTTP 方法、狀態碼、Header/Body）
   - 版本號規範（Semantic-like：Major.Minor.Build.Revision 的意義）
   - .NET/ASP.NET Web API 基礎（Controller、Action、Filter）
   - SDK 基礎（HttpClient、序列化/反序列化、初始化流程）
   - 版本管理與組建（AssemblyInfo、CI/Build 產版流程）
2. 核心概念：
   - 向前相容策略：Server 只保留最新版本，但需相容舊版 SDK（Compatible Versioning）
   - API Contract 管控：以 contract 介面定義公開 API，配合 runtime 檢查與/或單元測試
   - 版本識別與檢查：SDK 取得 API 版本、標註自身需求版本，雙向驗證
   - 執行時檢查機制：ActionFilter 於 request 前檢查 contract 與版本
   - 廢止與演進：只增不減，標註 [Obsolete]，重大變更才提升 Major
   彼此關係：Contract 是規格基礎 → 版本號反映 contract 變化 → SDK/Server 檢查流程落實策略 → 確保升級時向前相容。
3. 技術依賴：
   - ASP.NET Web API ActionFilter（Contract/版本檢查點）
   - 自訂 HTTP Header（X-SDK-REQUIRED-VERSION）
   - Assembly Metadata（AssemblyVersion 供 Server 報版本）
   - HttpClient 預設 Header 與 OPTIONS 端點（SDK 啟動時取版）
   - 單元測試/CI（輔助 contract 與版本規範落實）
4. 應用場景：
   - 單一全域服務的 HTTP API，需要持續演進但不斷線或不強制客戶端同步升級
   - 微服務對外 API 與多版本 SDK 共存的長期營運
   - 需紀律控管 API 變更、避免回溯破壞性修改的團隊協作

### 學習路徑建議
1. 入門者路徑：
   - 了解 HTTP/REST 與版本號語意（Major/Minor/Build/Revision）
   - 學會 ASP.NET Web API 基本 Controller/Action
   - 在 SDK 端以 HttpClient 呼叫 API，處理 JSON 序列化
2. 進階者路徑：
   - 實作自訂 ActionFilter（前置檢查、錯誤回應）
   - 設計 contract 介面與 runtime contract 檢查（IApiContract + 反射）
   - 在 SDK 初始化時取 API 版本（OPTIONS 或專用端點）並核對相容性
3. 實戰路徑：
   - 在 SDK 每次呼叫加上 X-SDK-REQUIRED-VERSION，Server 端於 Filter 驗證 AssemblyVersion
   - 建立版本策略與廢止流程（[Obsolete]、Major/Minor 規則）
   - 導入 CI 產版與 AssemblyVersion 管控，增設單元測試作為 contract 補強與回歸驗證
   - 加入快取以降低 runtime 反射/檢查成本，並規劃錯誤處理/回報機制

### 關鍵要點清單
- Compatible Versioning 策略: 只保留最新 Server，但保證相容舊版 SDK（向前相容）(優先級: 高)
- API Contract 介面化: 以 IApiContract 標記並由 Controller 實作，界定公開 API (優先級: 高)
- Runtime Contract 檢查: 以 ActionFilter 反射確認 Action 必須存在於 contract 介面 (優先級: 高)
- 單元測試作為輔助合約: 以測試描述規格，輔助捕捉變更，但不可取代契約控管 (優先級: 中)
- 版本號語意: Major 不相容、Minor 相容、Build/Revision 可選用或由 Build 系統產生 (優先級: 高)
- 版本規則落實: 只增不減、不破壞既有參數與簽章，重大變更才調整 Major (優先級: 高)
- 廢止流程與 [Obsolete]: 需明確宣告廢止期，先標註再於下一個 Major 移除 (優先級: 中)
- 版本暴露方式一: 提供端點（如 OPTIONS/api/birds）回傳版本字串，供 SDK 啟動時檢查 (優先級: 中)
- 版本暴露方式二: SDK 在每次呼叫加上 X-SDK-REQUIRED-VERSION Header，Server 於 Filter 驗證 (優先級: 高)
- Server 端版本來源: 以 AssemblyVersion（AssemblyInfo）為單一真相，由 CI/Build 控制 (優先級: 中)
- SDK 相容性檢查邏輯: Major 必須相同、Server.Minor 必須 >= SDK.Require.Minor (優先級: 高)
- 執行時錯誤處理: Server 轉 JSON Error，SDK 需能解析與呈報，避免難以診斷 (優先級: 中)
- 效能與快取: 對 contract 與版本檢查結果做快取，避免高 QPS 情境下的反射成本 (優先級: 中)
- 權限與版控: 規格異動需受控並留痕，對應更新版本號與公告（如變更記錄）(優先級: 中)
- 文件與團隊紀律: 明確文件化版本策略與承諾範圍，落實 Code Review 與自動檢查 (優先級: 中)