# 從 Intent 到 Assertion #1, 聊聊 Vibe Testing 實驗心得  

## 摘要提示
- Function Calling: 利用 LLM 的 Function Calling/Tool Use 能力，把「意圖→斷言」過程全自動化。  
- AI Ready API: API 若以領域行為封裝且具完整規格，AI 才能精準調用。  
- Test Runner: 以 .NET + Semantic Kernel 打通 PoC，50 行內程式即能驅動測試。  
- Domain Test Case: 測試腳本採 Given/When/Then，只描述商業情境不落實作細節。  
- OpenAPI Plugin: 將 Swagger 一鍵匯入 Kernel，瞬間產生 16 支可供 LLM 呼叫的工具。  
- Prompt Engineering: 多段系統/使用者提示明確規範測試流程與報告格式。  
- Structured Output: 同步輸出 Markdown 與 JSON，便於人工閱讀與系統整合。  
- 認證處理: 以獨立 Plugin 取得 OAuth2 access-token，屏蔽測試腳本對登入細節的依賴。  
- 擴充想像: 相同 Domain Case 搭配不同 Runner，可驗證 API/UI/Web/APP 多介面行為。  
- 技術門檻: 無標準化 API、規格與 CICD，自動化測試將加速技術債，而非產能。

## 全文重點
作者延續「安德魯小舖」經驗，嘗試把 LLM 的 Function Calling 能力移植到 API 自動化測試領域。核心構想是讓 AI 從「測試意圖」直接推理出應呼叫的 API、組裝參數、執行請求並完成斷言，工程師僅需提供 Domain-Level Test Case。為驗證可行性，他以 .NET Console 結合 Microsoft Semantic Kernel，透過 `ImportPluginFromOpenApiAsync` 將 Andrew Shop 的 Swagger 轉成 Plugin，並撰寫 System/User Prompts 規範 Given / When / Then 流程與報告格式。測試時 AI 先建立空購物車、搜尋「可口可樂」商品，再嘗試一次加入 11 件並檢查限制，最終自動產出 Markdown 與 JSON 雙版本報告，結果如預期呈現失敗。

實驗證實：在 API「領域化設計」與「完整規格」前提下，AI 能可靠地完成跨步驟參數串接與結果判讀；反之若 API 僅 CRUD、規格缺失或認證分散，AI 便難以處理。作者並提出規模化時需處理的四大議題：1) API 須依領域封裝行為；2) 規格文件要與程式自動同步；3) 認證/環境應由 Runner 標準化；4) 測試結果須結構化收斂至管控平台。整體而言，開發者應把時間投資在「設定好 AI 能理解的環境」，並把繁瑣測試腳本與文書工作交給 LLM，未來更可想像同一套 Domain Case 透過不同 Runner 擴張到 Web UI、Mobile 等全通路驗證。

## 段落重點
### 1. 構想: 拿 Tool Use 來做自動化測試
作者觀察人類執行測試的流程：先掌握意圖(AC)→憑領域知識選 API→比對斷言。若把這個流程交給具 Tool Use 能力的 LLM，即可省去撰寫腳本與人工操作。理論上同一份高階案例可搭配不同 Runner 針對 API、Web、Android、iOS 等介面進行驗證，顯著提升測試產出效率並降低文書負擔。

### 2. 實作: 準備測試案例 (domain)
以「購物車同商品最多 10 件」為例，案例僅描述業務情境：先清空購物車、指定商品可口可樂，嘗試加入 11 件並檢查結果；Then 期望 API 回 400 且購物車維持空。案例故意設計為目前 API 無法通過，以驗證 Test Runner 能否正確偵測失敗。撰寫重點在「測什麼有意義」而非列舉所有步驟。

### 3. 實作: 準備 API 的規格 (spec)
Andrew Shop 已公開 Swagger，可讓 AI 查得所有端點與參數。對 Given 及 When 步驟，作者事先腦補應呼叫的 API 序列：CreateCart、GetProducts、AddItemToCart、GetCart。Then 僅比對回應。完整規格是 AI 能自動組裝請求的基礎，若缺乏將難以驅動。

### 4. 實作: 挑選對應技術來驗證
選用 .NET Console + Semantic Kernel。匯入 OpenAPI 為 Plugin 後，Kernel 能自動在對話中插入 Function Call。再用 Prompt Template 撰寫三段訊息：System-Prompt 定義流程與嚴禁臆測；User-Prompt 放入 Test Case；最終要求產出 Markdown 報告。`InvokePromptAsync` 執行約 1 分鐘即可完成測試與報告。

#### 4-1. 將 OpenAPI 匯入 Plugin
透過 `ImportPluginFromOpenApiAsync` 10 行程式把 16 支 API 全轉成可呼叫工具，並加入 OAuth2 AuthCallback，自動附帶 access-token。

#### 4-2. 準備 Prompts
System Prompt 詳述 Given/When/Then 執行規範及報告格式；第二段傳入 Test Case；第三段要求生成表格式 Markdown 報告。並在 Settings 設 `FunctionChoiceBehavior = Auto` 讓 Kernel 代理呼叫。

#### 4-3. 測試結果報告
AI 真正呼叫 API，過程與 Header/Token 全列印證明無快取。報告顯示 AddItemToCart 未回 400，判定 test_fail；同步輸出 JSON 供系統彙整。

### 5. 心得與建議
作者回顧實驗並提出推廣門檻與對策：  
1) API 必須領域化封裝行為，避免 CRUD 導致流程散亂。  
2) API 規格需由 CICD 自動生成，否則測試只會暴露文件落差。  
3) 認證/語系/幣別等環境變數宜以獨立 Plugin 控制，讓 AI 專注業務邏輯。  
4) 測試報告須結構化輸出以利集中管理與警示。  
5) 小結：LLM+Function Calling 已足以取代傳統腳本，開發者應思考如何把技術封裝成工具服務更多人，而非僅當生產力輔助。未來作者將續寫案例展開與大規模化議題。