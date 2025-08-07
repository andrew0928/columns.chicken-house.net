# API & SDK Design #3, API 的向前相容機制

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 什麼是「向前相容」(forward compatibility)？  
向前相容是指：最新版本的 API 必須能與「某個時間點之後發佈的所有舊版 SDK」正常協作。也就是說，只要開發者尚未升級 SDK，仍應能呼叫新版 API 而不產生破壞性錯誤。

## Q: 作者採用哪一種 API 版本策略來達成向前相容？  
作者選擇「Compatible Versioning 相容性版本策略」：Server 只保留最新版本的 API，但保證該版本必須相容於所有舊版 SDK。

## Q: 為了避免新版 API 破壞舊版 SDK，作者訂出了哪三個檢查點 (check points)？  
1. API contracts：以嚴格受控的介面 (interface) 定義 API 規格並追蹤異動。  
2. 明確的版本識別機制：API 必須能揭露自己的版本；SDK 必須宣告最低可接受版本。  
3. 版本相容性策略：明定何時必須調升 Major / Minor 版號，以及被棄用 (obsolete) 的 API 移除流程。

## Q: 在 ASP.NET WebAPI 裡如何實作「API contract」的約束？  
作者以 interface 方式描述 contract（例如 `IBirdsApiContract` 繼承 `IApiContract`），並在 Controller 上套用 `ActionFilter` (`ContractCheckActionFilter`) 於 runtime 反射檢查：  
1. Controller 是否實作 contract interface。  
2. 當前被呼叫的 Action 是否存在於此 contract。  
若檢查失敗即拋出 `NotSupportedException`。

## Q: .NET 四碼版本號 (major.minor.build.revision) 在本文中的意義是什麼？  
• Major 不同代表「不相容」的重大變更，可不保證向前相容。  
• Minor 不同但 Major 相同，表示有功能擴充且需「保持相容」。  
• Build 與 Revision 通常用於重新編譯或修補 (bug/security fix)，對相容性無影響，可視團隊需求彈性使用。

## Q: Contract 異動時，版本號應該如何調整？  
1. Contract 未變：Major、Minor 皆維持。  
2. 只新增 API、無破壞性變更：Major 不變，Minor 加 1。  
3. 有破壞性變更：必須調升 Major。  
4. 想廢除舊 API 又不立即破壞相容：先標記 `[Obsolete]`，待下一次調升 Major 時再移除。

## Q: API 與 SDK 之間如何傳遞版本資訊？  
常用兩種方式（可並用）：  
1. 提供專屬 API（例如 `OPTIONS /api/birds`）回傳版本字串。  
2. 在每次正常 API 呼叫的 Response 中一併帶回版本欄位，或由 SDK 將 `X-SDK-REQUIRED-VERSION` header 送給 Server 讓 Server 檢查。

## Q: SDK 初始化階段如何檢查版本相容？  
SDK 在 `constructor` 內：  
1. 透過 OPTIONS 或其他 API 取得 Server 實際版本。  
2. 與程式碼中寫死的 `_require_API_version` 比較：`Major` 必須相等，`Minor` 不得低於要求值。  
3. 不相容時立即丟出 `InvalidOperationException`。

## Q: 若 SDK 生命週期很長，如何在「每次」呼叫 API 時再做版本檢查？  
1. SDK 將 `_require_API_version` 寫入自訂 HTTP Header（例如 `X-SDK-REQUIRED-VERSION`）。  
2. Server 端以 `SDKVersionCheckActionFilter` 讀取此 Header，取得自身 Assembly 版本並比對。  
3. 檢查失敗即在 Server 端拋出 `InvalidOperationException`，由 WebAPI 轉為 JSON 回傳，Client 端可捕捉並處理。

## Q: 版本不相容時會發生什麼事？  
Server 端的 Filter 先丟出 `InvalidOperationException`，WebAPI 會把 Exception 轉為 JSON error response。SDK 端收到後，`HttpClient` 也會拋出例外，開發者可在 Catch 區塊或 Global Handler 內處理顯示、重試或強制升級提示。