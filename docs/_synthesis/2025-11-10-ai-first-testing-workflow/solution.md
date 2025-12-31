---
layout: synthesis
title: "AI-First Testing, 以 AI 為核心重新設計測試流程"
synthesis_type: solution
source_post: /2025/11/10/ai-first-testing-workflow/
redirect_from:
  - /2025/11/10/ai-first-testing-workflow/solution/
postid: 2025-11-10-ai-first-testing-workflow
---
以下內容依據文章抽取並重組為 18 個可教學、可實作、可評估的實戰解決方案案例。每個案例均涵蓋問題、根因、方案、關鍵程式碼/設定、實測成效與練習與評估要點。最後提供分類與學習路徑建議。

## Case #1: 從「AI代執行」到「AI探索+程式化執行」的工作流重構

### Problem Statement（問題陳述）
業務場景：團隊嘗試以 AI 全自動執行 API 測試以取代人力，期望降低人工成本並加速測試節奏。然而測試量體與頻率極大，一年需重複執行數萬次，造成 GPU token 花費與等待時間高漲，且結果具隨機性難以納入 CI/CD。
技術挑戰：AI 每次推理結果具變動性、執行成本高、測試不可重現且不穩定，難以充當回歸測試主力。
影響範圍：測試花費失控、回歸測試無法穩定自動化、釋出節奏與品質回饋延遲。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 把 AI 當「執行者」塞進舊流程，屬局部最佳化，未重構工作流。
2. GPU 成本與時間昂貴，AI 推理本質不穩定造成結果波動。
3. 未將探索與重複執行解耦，回歸測試仍仰賴 AI「即時推理」。
深層原因：
- 架構層面：未建立「探索→規格化→程式化」的可持續管線。
- 技術層面：未善用 CPU 穩定執行的自動化測試程式，過度依賴 GPU 推理。
- 流程層面：無左移文件與自動化策略，測試資產不可複用。

### Solution Design（解決方案設計）
解決策略：以 AI-First Testing 三段式工作流重構測試：1) 用 Decision Table 產生高價值 Test Cases；2) 用 AI 進行「探索」並記錄步驟（API/Web）；3) 依探索產物自動生成可重複執行的測試程式碼（CPU）。AI 專注探索，回歸由程式碼執行。

實施步驟：
1. 設計 Decision Table 與 Test Cases
- 實作細節：用 TestKit.GenTest 由 AC 展開 decision table 並評審。
- 所需資源：TestKit、AC、網域專家審查。
- 預估時間：0.5~1 人日/AC。

2. AI 探索測試步驟（API/Web）
- 實作細節：用 TestKit.API.Run / TestKit.WEB.Run 執行，MCP 記錄 session logs。
- 所需資源：MCP（ListOperations/CreateSession/RunStep、Playwright MCP）。
- 預估時間：每測項 10~30 分鐘探索。

3. 生成測試程式碼
- 實作細節：用 TestKit.API.GenCode（或 SpecKit）將 session logs + test cases 轉為自動化程式。
- 所需資源：.NET 9 + xUnit 或既有測試框架。
- 預估時間：每測項 10~20 分鐘。

關鍵程式碼/設定：
```bash
# 三段式命令
/testkit.gentest
/testkit.api.run
/testkit.api.gencode
```

實際案例：以「安得魯小舖」AC（購物車結帳）→ 14 條規則 → 探索 R1-R6 → 生成 .NET xUnit 測試。
實作環境：VSCode + GitHub Copilot（Claude Haiku 4.5）、MCP（內嵌 GPT-5-mini）、.NET 9、xUnit。
實測數據：
改善前：AI 直接執行 40,000 次/年；~2 分鐘/次；Token 約 NT$1/次；費用約 NT$40,000；55.56 天計算時間。
改善後：AI 探索 ~400 次 + 生成程式碼 ~400 次；回歸 40,000 次由 CPU 在 4~5 秒/套件完成。
改善幅度：GPU 任務量降為 (400+400)/40,000=2%；GPU Token 費用降至 <5%；回歸時間從分鐘級降至秒級且可重現。

Learning Points（學習要點）
核心知識點：
- 探索與回歸分離的 AI-First Testing 思路
- 左移文件與自動化（Decision Table / Codegen）
- GPU/CPU/Brain 資源分工與成本模型

技能要求：
- 必備技能：測試分析、Decision Table、基礎自動化框架
- 進階技能：MCP 設計、Context Engineering、Codegen/SpecKit

延伸思考：
- 能否擴展到安全/效能測試的規格化與自動化？
- 風險：探索品質低會污染後續程式碼；需設審查關卡。
- 優化：以 SpecKit/SDD 制式化規格與產物一致性。

Practice Exercise（練習題）
- 基礎：為一個簡單 AC 產出 Decision Table（30 分）
- 進階：完成 API 探索並輸出 session logs（2 小時）
- 專案：完成三段式工作流並在 CI 執行（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：三步驟產物可串接
- 程式碼品質（30%）：測試可重現、結構清晰
- 效能優化（20%）：GPU 任務明顯下降
- 創新性（10%）：工作流可移植性與可擴充性


## Case #2: 測試量體爆炸的解法—Decision Table 收斂與抽象化

### Problem Statement（問題陳述）
業務場景：同一 AC 在多操作介面（Web/Android/iOS/API）與多種 NFR（資安、授權、效能等）下組合激增，導致需維護數百份測試腳本與規格，審閱與更新成本飆升。
技術挑戰：測項重複、耦合操作細節、不可複用，難以統一管理與擴張。
影響範圍：文件維護成本、測試覆蓋率與品質、交付節奏。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 測試案例與操作介面綁死，抽象層級過低。
2. 缺乏條件組合的系統化展開，覆蓋率不可度量。
3. NFR 與功能測試混雜，維度未分離。
深層原因：
- 架構層面：缺少統一的測試知識表示（Decision Table）。
- 技術層面：無產物可被 AI 後續有效消費與擴展。
- 流程層面：文件與自動化未左移、未分層。

### Solution Design（解決方案設計）
解決策略：以 Decision Table 抽象描述條件與動作，將測試案例與操作介面解耦。僅維護 AC→Decision Table→抽象 Test Case，操作步驟在探索階段才展開。

實施步驟：
1. 建立 Decision Table
- 實作細節：以 TestKit.GenTest 從 AC 展開 C/A/R，審查邊界值。
- 所需資源：AC、網域專家、TestKit。
- 預估時間：0.5 人日/AC。

2. 產生抽象 Test Cases
- 實作細節：由 Decision Table 自動展測（14 規則→14 測項）。
- 所需資源：TestKit、範本。
- 預估時間：0.5 人日。

3. 介面化探索
- 實作細節：API/Web 各自探索步驟，引用同一測項。
- 所需資源：MCP、Playwright MCP。
- 預估時間：依測項難度 10~30 分鐘/項。

關鍵程式碼/設定：
```markdown
# 決策表示例（片段）
| 規則 | 啤酒 | 可樂 | 綠茶 | 總金額 | 總優惠 | 結帳金額 | 允許 |
| R6  | 10  | 0   | 0   | $650 | -$130 | $520 | ✅ |
```

實際案例：購物車 AC→14 規則（R1~R14）→14 份抽象測試檔案。
實作環境：VSCode + Copilot、TestKit。
實測數據：
改善前：需維護 4 操作方式 × 10 測項 × 10 NFR = 400 份文件/腳本。
改善後：Decision Table ×1 + Test Case ×10（示例）= 11 份。
改善幅度：維護量下降約 97.25%。

Learning Points（學習要點）
核心知識點：
- Decision Table 的條件/動作/規則結構
- 抽象測項的可複用性
- 覆蓋率與邊界值思維

技能要求：
- 必備技能：測試分析、邊界值分析
- 進階技能：用 AI 生成/校對 Decision Table

延伸思考：
- 可否自動標註風險與優先級？
- 風險：表設計錯誤將污染後續產物。
- 優化：建立審查清單與單位測試檢核表。

Practice Exercise（練習題）
- 基礎：為一組促銷規則建立 Decision Table（30 分）
- 進階：產生抽象測項並標註重要性（2 小時）
- 專案：將舊測項轉換為 Decision Table 流程（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：表涵蓋必要條件與邊界
- 程式碼品質（30%）：產出結構化一致
- 效能優化（20%）：維護量下降可量化
- 創新性（10%）：可複用與擴展策略


## Case #3: 修補 AI 生成 Decision Table 的語義與計算錯誤

### Problem Statement（問題陳述）
業務場景：AI 產生的第一版 Decision Table 雖格式正確，但條件/動作/規則設計過度簡化，且在「第二件六折」等商業規則與金額計算上出現誤解與錯算。
技術挑戰：AI 對網域規則理解偏差導致測項錯誤，後續自動化全線受影響。
影響範圍：測試正確性、覆蓋率、誤判成本。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. AI 將「第二件六折」誤解為「第二件之後都六折」。
2. 金額計算出錯（例：R14 計算從 $740 修正為 $690）。
3. 過度二元化（Y/N）條件導致邊界測項缺失。
深層原因：
- 架構層面：缺乏審查回路與範例單元測試校正。
- 技術層面：規則未具體化為可運算公式以便驗證。
- 流程層面：AI 輔助未配套人審機制。

### Solution Design（解決方案設計）
解決策略：建立「AI 生成→人審→回饋再生」循環，明確以公式指定動作欄位（如總金額、總優惠），並以樣例計算校驗規則正確性。

實施步驟：
1. 規則公式化
- 實作細節：以 floor(x/2) 定義優惠組數，公式化總金額/總優惠/結帳金額。
- 所需資源：網域專家、計算範例。
- 預估時間：1 小時。

2. 樣例校驗
- 實作細節：對 R3/R4/R5/R14 等規則手工計算核對。
- 所需資源：試算表/單元測試腳本。
- 預估時間：1~2 小時。

3. 修正與再生
- 實作細節：將錯誤回饋給 AI 再生表格，重跑校驗。
- 所需資源：TestKit.GenTest。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```markdown
# 動作欄位公式（納入表說明）
A1(優惠組數) = floor(啤酒數量 / 2)
A2(總金額)   = 啤酒×65 + 可樂×18 + 綠茶×25
A3(總優惠)   = A1 × -26
A4(結帳金額) = A2 + A3
```

實際案例：R14 由 $740 修正為 $690；奇偶數件的優惠組數校正（3 件=1 組）。
實作環境：VSCode + Copilot、試算表或小型 UT 腳本。
實測數據：
改善前：AI 產表含多處語義與計算錯誤，需人力逐項比對。
改善後：14 規則公式化後一致通過校驗。
改善幅度：決策表錯誤率趨近 0%，後續探索成功率顯著提升。

Learning Points（學習要點）
核心知識點：
- 將商業規則公式化提高可驗證性
- 人審回路對 AI 產物的必要性
- 邊界值與樣例檢驗方法

技能要求：
- 必備技能：需求拆解、基本數學與表達
- 進階技能：以 UT 腳本驗證表值

延伸思考：
- 可否以屬性化測試自動掃描組合？
- 風險：公式錯誤將放大影響。
- 優化：建立最小樣例集基準庫。

Practice Exercise（練習題）
- 基礎：為 5 個規則寫出金額/優惠公式驗算（30 分）
- 進階：寫 UT 校驗 Decision Table 每列（2 小時）
- 專案：為另一張決策表建立完整驗證管線（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：所有動作欄位可計算
- 程式碼品質（30%）：UT 涵蓋每條規則
- 效能優化（20%）：校驗自動化程度
- 創新性（10%）：公式化與驗證策略


## Case #4: 從 AC 到「可排序的測試清單」—優先級與類別化

### Problem Statement（問題陳述）
業務場景：測項眾多且針對不同風險與價值，若無優先順序，資源分配與回饋速度不佳，導致找不到最關鍵回饋。
技術挑戰：如何從 Decision Table 對測項分類並排序，先跑最有價值與風險的場景。
影響範圍：測試回饋速度、交付節奏、風險暴露延遲。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 測項等權處理，缺乏價值/風險導向排序。
2. 未形成可運行的「最小驗證集」（如 R1-R6）。
3. 缺乏分類（基礎/超限/混合/NFR）。
深層原因：
- 架構層面：測項缺少元資料（重要性、風險）。
- 技術層面：產品化/營運風險未映射到測試維度。
- 流程層面：未建立「最小可運行測試集」。

### Solution Design（解決方案設計）
解決策略：在生成 Test Cases 時，同步產生類別與優先級，先執行「正常結帳流程（R1-R6）」作為最小可運行集，再逐步擴張到超限與混合場景。

實施步驟：
1. 生成並標記分類
- 實作細節：AI 根據規則性質標記分類與重要性。
- 所需資源：TestKit.GenTest 後處理。
- 預估時間：0.5 小時。

2. 定義最小可運行集
- 實作細節：將 R1-R6 設為 smoke/regression baseline。
- 所需資源：測試模板與 CI 任務配置。
- 預估時間：1 小時。

3. 分層執行策略
- 實作細節：CI 中先跑 baseline，再跑其餘。
- 所需資源：CI 設定檔。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```yaml
# CI 中的測試分層
jobs:
  smoke:
    steps: dotnet test --filter Category=Baseline
  full:
    steps: dotnet test
```

實際案例：R1-R6 作為 baseline；R7-R14 分批加入。
實作環境：CI（GitHub Actions/Azure DevOps）。
實測數據：
改善前：全套 Web 探索約 20 分鐘才有第一波結果。
改善後：先跑 R1-R6，20 分鐘內取得核心回饋；其餘批次執行。
改善幅度：首波回饋時間從「未知/延後」降為「固定可預期」。

Learning Points（學習要點）
核心知識點：
- 基於風險與價值的測試排序
- 最小可運行測試集（baseline）
- CI 分層執行

技能要求：
- 必備技能：CI 配置、測項標籤化
- 進階技能：測試資源排程

延伸思考：
- 如何動態依據缺陷熱點調整排序？
- 風險：標註主觀偏差。
- 優化：引入缺陷與變更歷史權重。

Practice Exercise（練習題）
- 基礎：替 10 個測項標註分類與優先級（30 分）
- 進階：配置 CI smoke/full 任務（2 小時）
- 專案：建立依變更差異的測試選擇器（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：分層可執行
- 程式碼品質（30%）：標籤一致可維護
- 效能優化（20%）：回饋時間縮短
- 創新性（10%）：排序策略具適應性


## Case #5: 共用 Test Case，API 與 Web 一致覆蓋

### Problem Statement（問題陳述）
業務場景：系統同時提供 API 與 Web 介面，若各自維護測項會重工且不一致，導致覆蓋落差與知識碎片化。
技術挑戰：如何以同一套 Test Cases 駕馭不同介面探索與自動化？
影響範圍：文檔與腳本重複、測試結果不可比較、維護成本高。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 測項綁定操作介面，造成重複維護。
2. 缺乏抽象層與共享資料夾結構。
3. Web 與 API 各自演進，知識不同步。
深層原因：
- 架構層面：未以抽象測項為中心的測試知識庫。
- 技術層面：探索工具與路徑不同步。
- 流程層面：缺乏共用產物（session logs）累積。

### Solution Design（解決方案設計）
解決策略：以抽象 Test Cases 共享，API 探索用 TestKit.API.Run，Web 探索用 TestKit.WEB.Run；統一在同一測試目錄下維護，保留各自 session logs。

實施步驟：
1. 建立共享目錄
- 實作細節：tests/shopping-cart-checkout 下放 decision-table.md 與 tc-*.md。
- 所需資源：檔案約定與模板。
- 預估時間：0.5 小時。

2. 並行探索
- 實作細節：API/Web 各自探索與記錄 session logs。
- 所需資源：MCP、Playwright MCP。
- 預估時間：依測項而定。

3. 對齊校驗
- 實作細節：比較 API 與 Web 行為一致性（如空車 UI 阻擋 vs API 缺失）。
- 所需資源：審查會議。
- 預估時間：1 小時。

關鍵程式碼/設定：
```bash
# 同一測項，兩條探索命令
/testkit.api.run
/testkit.web.run
```

實際案例：R1-R6 同步探索；Web 對空車結帳 UI 阻擋測試通過，API 未阻擋測試失敗，成功揭示產品差異。
實作環境：VSCode + Copilot、MCP、Playwright MCP。
實測數據：
改善前：API/Web 測項各自維護與不一致。
改善後：共用測項，差異清晰可見（UI 通過、API 失敗）。
改善幅度：維護複本降為 1，缺陷定位效率提升。

Learning Points（學習要點）
核心知識點：
- 抽象測項可跨介面重用
- 差異檢測（API vs Web）
- 共享產物的檔案策略

技能要求：
- 必備技能：目錄規劃、版本管理
- 進階技能：差異分析與對齊流程

延伸思考：
- 可否產生跨介面差異報告？
- 風險：探索品質差導致錯誤比較。
- 優化：引入一致性的斷言模板。

Practice Exercise（練習題）
- 基礎：將兩介面測項收斂到同一資料夾（30 分）
- 進階：產出 API/Web 差異報告（2 小時）
- 專案：建立跨介面的共用斷言庫（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：同測項可覆蓋兩介面
- 程式碼品質（30%）：目錄與檔案清晰
- 效能優化（20%）：差異定位效率
- 創新性（10%）：共用斷言與模板設計


## Case #6: 避免 Context 爆炸—以 MCP 抽象 API 操作

### Problem Statement（問題陳述）
業務場景：直接把完整 OpenAPI/Swagger 丟給 Agent，導致上下文內雜訊過多、token 迅速塞滿、推理品質下降，探索頻繁失敗。
技術挑戰：在不暴露細節的前提下，讓 Agent 能穩定選擇正確操作並完成任務。
影響範圍：探索成功率、推理成本、可維護性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. API 規格細節冗長且充滿雜訊。
2. OAuth2 等機械化流程干擾主要推理。
3. Agent 無法聚焦「行動選擇」。
深層原因：
- 架構層面：缺少 API 操作層抽象（Operation 清單）。
- 技術層面：未建立 A2A（agent-to-agent）簡化協議。
- 流程層面：未分層處理規格解析與實際呼叫。

### Solution Design（解決方案設計）
解決策略：以 MCP 提供四工具：QuickStart、ListOperations（僅摘要操作）、CreateSession（隱藏 OAuth2）、RunStep（以 operation+action+context 指令驅動），由 MCP 內部 LLM 處理 text→param 映射。

實施步驟：
1. 工具化
- 實作細節：實作四工具封裝細節。
- 所需資源：MCP SDK、LLM function calling。
- 預估時間：2~3 人日。

2. 摘要化操作
- 實作細節：ListOperations 返回可用 operation 名稱+敘述。
- 所需資源：規格解析器。
- 預估時間：0.5~1 人日。

3. RunStep 協議化
- 實作細節：定義 operation/action/context 結構。
- 所需資源：JSON schema。
- 預估時間：0.5 人日。

關鍵程式碼/設定：
```json
{
  "operation": "CreateCart",
  "action": "create an empty cart",
  "context": "User andrew logged in. Create a new empty cart to test checkout with no items."
}
```

實際案例：Agent 先 QuickStart→ListOperations→CreateSession→RunStep，不需注入 Swagger 全文。
實作環境：MCP（GPT-5-mini 做內部 function calling）。
實測數據：
改善前：Context 容量快速耗盡、探索失敗率高。
改善後：上下文僅含必要操作摘要與 A2A 指令；探索穩定完成 R1-R6。
改善幅度：上下文 token 大幅下降；探索成功率顯著提升（質性觀察）。

Learning Points（學習要點）
核心知識點：
- Context rot 與雜訊控制
- MCP 分層與 A2A 協議
- Operation 抽象化

技能要求：
- 必備技能：API 規格理解、工具封裝
- 進階技能：Function Calling 設計

延伸思考：
- 能否自動生成 Operation 摘要？
- 風險：摘要過度導致資訊不足。
- 優化：漸進式揭露細節策略。

Practice Exercise（練習題）
- 基礎：為三個 API 寫 ListOperations 摘要（30 分）
- 進階：實作 RunStep 對一個 API 的參數映射（2 小時）
- 專案：完成四工具整合與日誌（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：四工具可運作
- 程式碼品質（30%）：協議簡潔一致
- 效能優化（20%）：上下文縮減
- 創新性（10%）：A2A 設計思路


## Case #7: OAuth2 等機械化流程下放 MCP，簡化探索

### Problem Statement（問題陳述）
業務場景：探索流程若讓 Agent 自己處理 OAuth2，需多輪提示與錯誤重試，耗時耗 token，且不穩定。
技術挑戰：在探索前完成登入與權杖取得，避免 Agent 被機械流程干擾。
影響範圍：探索時間、穩定性、token 花費。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 將 OAuth2 視為需推理的任務。
2. 認證流程瑣碎，易誤判與超時。
3. Token 管理雜訊充斥上下文。
深層原因：
- 架構層面：未清楚分離「流程性任務」與「決策性任務」。
- 技術層面：缺乏 session 與 secret 管理機制。
- 流程層面：無前置準備步驟。

### Solution Design（解決方案設計）
解決策略：在 CreateSession 內完成 OAuth2 流程與 token 儲存；RunStep 僅關注業務操作。

實施步驟：
1. Session 建立
- 實作細節：從 .env 或 Secret Store 載入憑證，發 OAuth2 flow 取得 access_token。
- 所需資源：MCP + HttpClient。
- 預估時間：0.5~1 人日。

2. Token 注入
- 實作細節：在 MCP 端將 token 注入每次 API 呼叫 header。
- 所需資源：MCP 攔截器。
- 預估時間：0.5 人日。

3. 日誌與錯誤處理
- 實作細節：001/002 步驟完整記載 OAuth 交換。
- 所需資源：檔案系統。
- 預估時間：0.5 人日。

關鍵程式碼/設定：
```csharp
// MCP 內部擬碼
var token = await OAuthClient.GetTokenAsync(clientId, secret);
_session.Set("access_token", token);
http.DefaultRequestHeaders.Authorization = new("Bearer", token);
```

實際案例：CreateSession 後所有 RunStep 自動帶入權杖，探索無需關心登入細節。
實作環境：MCP。
實測數據：
改善前：多輪提示卡關、重試頻繁。
改善後：探索步驟直接可用；OAuth2 成本近似 0 次推理。
改善幅度：探索時間縮短、失敗率下降（質性觀察）。

Learning Points（學習要點）
核心知識點：
- 前置化機械流程
- Secret/Token 管理最佳實踐
- Session 與攔截器設計

技能要求：
- 必備技能：OAuth2 流程
- 進階技能：中介層封裝與攔截

延伸思考：
- 多租戶 token 輪替策略？
- 風險：憑證外洩。
- 優化：結合雲端 Secret Manager。

Practice Exercise（練習題）
- 基礎：以 .env 載入憑證並取 token（30 分）
- 進階：完成攔截器自動帶 token（2 小時）
- 專案：建置多環境 token 切換（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：自動帶 token
- 程式碼品質（30%）：憑證不入庫、配置清晰
- 效能優化（20%）：探索耗時下降
- 創新性（10%）：通用化封裝


## Case #8: 用程式碼取代 AI 重複執行—穩定回歸測試

### Problem Statement（問題陳述）
業務場景：AI 執行每次結果略有差異，回歸測試無法保證一致與快速，CI/CD 難以採用。
技術挑戰：需將探索成果固化為可重複執行且穩定的測試程式碼。
影響範圍：回歸測試可靠度、交付節奏。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 回歸測試交給 AI 推理，結果具有隨機性。
2. 測試步驟未轉為確定性的指令與斷言。
3. 未善用 CPU 高效執行特性。
深層原因：
- 架構層面：探索與回歸混雜。
- 技術層面：缺少代碼生成與模板。
- 流程層面：無規格驅動的程式碼生成步驟。

### Solution Design（解決方案設計）
解決策略：以 TestKit.API.GenCode（或 SpecKit）將 Test Case + Session Logs + API Spec 轉為 .NET xUnit 測試，回歸由 CPU 執行。

實施步驟：
1. 蒐集產物
- 實作細節：整理 session-logs.md、openapi-spec.json、tc-*.md。
- 所需資源：TestKit。
- 預估時間：0.5 小時。

2. 生成測試碼
- 實作細節：以模板生成並加上必要斷言。
- 所需資源：.NET 9 + xUnit。
- 預估時間：10~20 分鐘/測項。

3. CI 集成
- 實作細節：dotnet test 並匯出報告。
- 所需資源：CI 平台。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
[Fact]
public async Task TC02_SingleBeer_NoDiscount()
{
  var cart = await _client.CreateCartAsync();
  await _client.AddItemAsync(cart.Id, "beer", 1);
  var total = await _client.EstimatePriceAsync(cart.Id);
  Assert.Equal(65m, total.TotalPrice);
}
```

實際案例：生成 TC01~TC03，總執行 4.3 秒；TC01（空車）失敗，TC02/TC03 成功。
實作環境：.NET 9、xUnit。
實測數據：
改善前：AI 執行約 2 分鐘/測項且不穩定。
改善後：CPU 執行 3 測項共 4.3 秒且可重現。
改善幅度：回歸速度飛躍、結果穩定性大幅提升。

Learning Points（學習要點）
核心知識點：
- 探索→程式化的轉換思維
- 測試斷言與可重現性
- CPU/CI 的優勢

技能要求：
- 必備技能：單元測試框架
- 進階技能：代碼生成模板化

延伸思考：
- 能否統一報告格式對接 Test Management？
- 風險：探索錯誤將固化到程式。
- 優化：導入 SpecKit/SDD 規格生成。

Practice Exercise（練習題）
- 基礎：把一個 session logs 轉為一支 xUnit（30 分）
- 進階：加入資料驅動多組斷言（2 小時）
- 專案：建立從 logs 到 code 的自動產生器（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：測試可執行通過
- 程式碼品質（30%）：斷言到位、可讀性佳
- 效能優化（20%）：執行時間顯著下降
- 創新性（10%）：生成器與模板設計


## Case #9: 把探索「步驟足跡」變成可再利用的規格資產

### Problem Statement（問題陳述）
業務場景：探索過程若不保留足跡，後續很難重現、審查與生成程式碼，造成知識流失。
技術挑戰：如何結構化記錄每一步操作及其 request/response？
影響範圍：審計追溯、程式碼生成、除錯效率。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 探索步驟資訊散落對話上下文。
2. 缺少統一檔案結構與命名。
3. 缺少抽象與具體雙層紀錄。
深層原因：
- 架構層面：無「規格化足跡」產物。
- 技術層面：未將 HTTP 細節快照化。
- 流程層面：無審查點與產物歸檔。

### Solution Design（解決方案設計）
解決策略：建立 session 資料夾，保存 openapi-spec.json、逐次 request/response（檔編號），session-logs.md 記錄抽象步驟與結果摘要。

實施步驟：
1. 檔案結構約定
- 實作細節：_session/00x-* 命名規則。
- 所需資源：MCP 內日誌器。
- 預估時間：0.5 天。

2. 雙層紀錄
- 實作細節：抽象（logs.md）+ 具體（HTTP 快照）。
- 所需資源：檔案 IO。
- 預估時間：0.5 天。

3. 導入生成
- 實作細節：codegen 讀取 logs 作為步驟依據。
- 所需資源：TestKit/API.GenCode。
- 預估時間：同 Case 8。

關鍵程式碼/設定：
```text
_session/
  001-oauth-request.txt
  002-oauth-response.txt
  005-api-request.txt
  005-api-response.txt
  openapi-spec.json
  session-logs.md
```

實際案例：R1~R6 探索生成完整 _session 供後續 codegen 使用。
實作環境：MCP、檔案系統。
實測數據：
改善前：探索步驟不可追溯，不利生成與審核。
改善後：3 測項一次生成、一次編譯可跑，審核足跡完整。
改善幅度：生成成功率與審計可見性顯著提升（質性）。

Learning Points（學習要點）
核心知識點：
- 抽象/具體雙軌紀錄
- 檔案結構與命名策略
- 規格化產物作為 codegen 輸入

技能要求：
- 必備技能：檔案管理、日誌設計
- 進階技能：生成器輸入規格設計

延伸思考：
- 可否標準化為「測試步驟 DSL」？
- 風險：紀錄不一致導致混亂。
- 優化：加簽/校驗與目錄守護。

Practice Exercise（練習題）
- 基礎：為兩步 API 呼叫存檔 request/response（30 分）
- 進階：把 logs.md 轉測試步驟清單（2 小時）
- 專案：做一個 logs→code 的小生成器（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：足跡完整可還原
- 程式碼品質（30%）：結構一致
- 效能優化（20%）：生成效率提升
- 創新性（10%）：DSL 化構想


## Case #10: 以無障礙（Accessibility）強化 Web 自動操作成功率

### Problem Statement（問題陳述）
業務場景：AI 以 Playwright 自動操作 Web 頻繁出現「看得到按不到」的問題，致使探索拖延甚至卡關。
技術挑戰：如何讓 Agent 穩定正確定位與操作 UI 元素？
影響範圍：Web 探索時間、成功率、token 花費。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 純影像辨識耗時且不穩定。
2. 直接解析 HTML 上下文肥大導致 token 爆炸。
3. 無障礙標記不足，Playwright 的可及性樹資訊不完整。
深層原因：
- 架構層面：未將 A11y 視為 AI 介接規格。
- 技術層面：缺乏 role/name/label 等語義。
- 流程層面：未在設計時導入 A11y 基準。

### Solution Design（解決方案設計）
解決策略：強化頁面無障礙：aria-label、role、name、labelledby；Playwright MCP 以可及性語義樹（精簡 YAML）供 Agent 推理與定位。

實施步驟：
1. A11y 標記補強
- 實作細節：為關鍵按鈕/輸入補 aria-*、role。
- 所需資源：前端代碼。
- 預估時間：1~2 人日/頁。

2. Playwright MCP 導入
- 實作細節：使用其精簡樹供推理定位。
- 所需資源：Playwright MCP。
- 預估時間：0.5 人日。

3. 測試與調整
- 實作細節：針對難點元素微調標記。
- 所需資源：瀏覽器 DevTools。
- 預估時間：1 人日。

關鍵程式碼/設定：
```html
<button role="button" aria-label="結帳" id="checkoutBtn">結帳</button>
<input aria-label="使用者名稱" />
```

實際案例：Web R1-R6 全數通過；空車時移除「結帳」按鈕，UI 層正確阻擋。
實作環境：React/NodeJS、Playwright MCP。
實測數據：
改善前：常見「找不到/按不到」；探索耗時高且不穩定。
改善後：6/6 測項通過；約 20 分鐘完成一輪探索。
改善幅度：成功率從不穩定到穩定成功（質性）；時間可預期化。

Learning Points（學習要點）
核心知識點：
- A11y 作為 AI 友好介面
- Playwright 的可及性樹策略
- UI 層防呆（移除按鈕）優於事後錯誤

技能要求：
- 必備技能：基本 HTML/A11y
- 進階技能：Playwright 選擇器策略

延伸思考：
- 能否產生 A11y 偵測報告做門檻？
- 風險：標記漂移/回歸。
- 優化：加入 A11y CI 掃描。

Practice Exercise（練習題）
- 基礎：替 3 個元素補齊 aria/role（30 分）
- 進階：用 Playwright 定位並點擊（2 小時）
- 專案：為頁面建立 A11y 基準並自動檢查（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：元素可定位可操作
- 程式碼品質（30%）：A11y 合規
- 效能優化（20%）：探索耗時可控
- 創新性（10%）：A11y 驅動測試策略


## Case #11: 工具選型權衡—Playwright MCP、Selenium MCP 與影像辨識

### Problem Statement（問題陳述）
業務場景：Web 自動化可選 Playwright（A11y 樹）、Selenium（完整 DOM）、視覺模型（影像），各有取捨。
技術挑戰：要兼顧上下文大小、定位精準度與執行效率。
影響範圍：探索成功率、token 使用、開發維護。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Selenium 提供完整 HTML，容易爆 context。
2. 視覺模型昂貴且緩慢。
3. Playwright 精簡資訊但仰賴 A11y 質量。
深層原因：
- 架構層面：未根據頁面特徵選擇策略。
- 技術層面：缺少多策略 fallback。
- 流程層面：無基準評測。

### Solution Design（解決方案設計）
解決策略：優先 Playwright MCP（A11y 樹），必要時針對局部採 Selenium 或視覺補強，建立上下文大小與成功率基準。

實施步驟：
1. 基準測試
- 實作細節：同頁面用三策略測試成功率與上下文大小。
- 所需資源：小型腳本。
- 預估時間：1~2 人日。

2. 策略切換
- 實作細節：一般情況用 Playwright，特例 fallback。
- 所需資源：工具封裝。
- 預估時間：1 人日。

3. A11y 改善
- 實作細節：針對失敗元素補標記。
- 所需資源：前端調整。
- 預估時間：依需求。

關鍵程式碼/設定：
```yaml
# Playwright MCP 導出可及性樹（示意）
- role: button
  name: 結帳
  id: checkoutBtn
```

實際案例：採 Playwright MCP 後，避免 100KB+ HTML 佔滿上下文，探索穩定。
實作環境：Playwright MCP、Selenium MCP（備援）。
實測數據：
改善前：Selenium 模式下上下文「爆肥」；視覺模式數十秒/步。
改善後：A11y 樹模式上下文縮至「幾 KB」量級，探索時間顯著下降。
改善幅度：上下文規模數量級縮減（質性）。

Learning Points（學習要點）
核心知識點：
- 上下文大小與策略選擇
- A11y 與可維護性
- 多策略 fallback 設計

技能要求：
- 必備技能：三工具基本用法
- 進階技能：封裝與策略路由

延伸思考：
- 能否自動依頁面特徵選擇策略？
- 風險：策略切換成本。
- 優化：策略結果回饋改版。

Practice Exercise（練習題）
- 基礎：用 Playwright 抽取 A11y 樹（30 分）
- 進階：對同頁比較三策略成功率（2 小時）
- 專案：做策略路由器（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：三策略均可執行
- 程式碼品質（30%）：封裝清晰
- 效能優化（20%）：上下文與時間下降
- 創新性（10%）：策略自動選擇


## Case #12: 負向測試找出邏輯缺陷—空購物車結帳

### Problem Statement（問題陳述）
業務場景：規格要求空購物車不得結帳；UI 已阻擋，但 API 未實作限制，造成邏輯漏洞。
技術挑戰：在探索階段精準重現並證明 API 缺陷。
影響範圍：錯誤訂單風險、營運風險、客訴。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. API 未做「空購物車」檢查。
2. UI 與 API 規則不一致。
3. 測試未涵蓋負向場景。
深層原因：
- 架構層面：缺少跨介面一致性校驗。
- 技術層面：缺少 API 層 guard。
- 流程層面：未以 Decision Table 包含拒絕條件。

### Solution Design（解決方案設計）
解決策略：以 TC01（空車）探索 API 流程：CreateCart→EstimatePrice→CreateCheckout；期待 4xx，若 2xx 則判為缺陷；並將此用例升級為回歸測試。

實施步驟：
1. 探索重現
- 實作細節：RunStep 三步並保存 HTTP 快照。
- 所需資源：MCP。
- 預估時間：10~20 分鐘。

2. 程式化
- 實作細節：生成 xUnit，對回應碼斷言 4xx。
- 所需資源：TestKit/API.GenCode。
- 預估時間：10 分鐘。

3. 跨介面對齊
- 實作細節：比對 UI 與 API 規則差異，提出修正建議。
- 所需資源：審查會議。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
var resp = await _client.TryCreateCheckoutAsync(cart.Id);
Assert.False(resp.IsSuccessStatusCode, "空購物車應被拒絕");
```

實際案例：TC01 API 探索顯示 2xx（缺陷），UI 測試通過（已移除按鈕）。
實作環境：MCP、.NET 9、xUnit。
實測數據：
改善前：缺陷未被發現。
改善後：以負向用例在探索階段即暴露；回歸固定檢查。
改善幅度：缺陷發現前移，降低風險。

Learning Points（學習要點）
核心知識點：
- 負向測試的重要性
- 跨介面一致性驗證
- 回歸測試升級策略

技能要求：
- 必備技能：HTTP 斷言
- 進階技能：缺陷報告與修正建議

延伸思考：
- 能否自動生成一致性對照表？
- 風險：回歸漏測。
- 優化：將負向測試納入 baseline。

Practice Exercise（練習題）
- 基礎：寫一個空資料拒絕的 API 測試（30 分）
- 進階：製作跨介面規則比對（2 小時）
- 專案：建立負向測試清單並自動執行（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：能重現並斷言缺陷
- 程式碼品質（30%）：斷言清晰、日誌齊全
- 效能優化（20%）：回歸自動化
- 創新性（10%）：一致性校驗方法


## Case #13: 以最小集優先跑—縮短「第一個訊號」時間

### Problem Statement（問題陳述）
業務場景：完整測套耗時長，團隊需要快速獲得「通關/失敗」的第一個訊號以決策是否繼續。
技術挑戰：如何在不犧牲品質前提下快速得到核心回饋？
影響範圍：研發節奏、風險控管、資源使用。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 全量測試一次跑完才出結果。
2. 無 smoke/baseline 階段。
3. 測試未分層。
深層原因：
- 架構層面：未定義「最小可運行集」。
- 技術層面：無標籤與 CI 過濾機制。
- 流程層面：無「快速止血」機制。

### Solution Design（解決方案設計）
解決策略：將 R1-R6 標記為 Baseline，先於 CI 執行；若失敗則停止 pipeline，否則再跑完整集。

實施步驟：
1. 標籤化
- 實作細節：將 R1-R6 標記 Category=Baseline。
- 所需資源：測試屬性。
- 預估時間：0.5 小時。

2. CI 過濾
- 實作細節：用 --filter 執行 baseline；失敗即終止。
- 所需資源：CI 設定。
- 預估時間：0.5 小時。

3. 分批佈署
- 實作細節：Pass 後再跑其餘測試。
- 所需資源：CI 兩階段 job。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```bash
dotnet test --filter "Category=Baseline"
```

實際案例：Web 探索 R1-R6 約 20 分鐘；作為第一訊號足夠決策。
實作環境：CI。
實測數據：
改善前：需等待完整集完成才有回饋。
改善後：在固定時間（20 分內）得到可用回饋。
改善幅度：決策等待時間大幅縮短。

Learning Points（學習要點）
核心知識點：
- Baseline/Smoke 測試
- CI 條件執行
- Fail-fast 策略

技能要求：
- 必備技能：測試標籤
- 進階技能：CI 決策控制

延伸思考：
- 可否動態選擇 baseline？
- 風險：baseline 過小。
- 優化：依缺陷熱點調整。

Practice Exercise（練習題）
- 基礎：標記三個 baseline 測項（30 分）
- 進階：配置 CI fail-fast（2 小時）
- 專案：動態 baseline 選擇器（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：分層執行
- 程式碼品質（30%）：標籤正確
- 效能優化（20%）：等待時間縮短
- 創新性（10%）：動態策略


## Case #14: A2A 協議化 RunStep—簡化 Agent 溝通

### Problem Statement（問題陳述）
業務場景：Agent 與 MCP 之間若傳遞大量細節（API spec/參數），溝通成本高且易錯。
技術挑戰：設計最小充分的指令介面支援探索。
影響範圍：推理穩定度、上下文大小、可移植性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 指令不一致、冗長。
2. 缺乏語義清晰的欄位。
3. Agent 難以聚焦任務。
深層原因：
- 架構層面：無輕量協議。
- 技術層面：未抽象操作語義。
- 流程層面：無標準化產物。

### Solution Design（解決方案設計）
解決策略：統一用 operation/action/context 三欄，以 JSON 指令傳遞；MCP 內部 LLM 做 text→param 映射與 HTTP 呼叫。

實施步驟：
1. 協議定義
- 實作細節：JSON schema 與欄位說明。
- 所需資源：設計文件。
- 預估時間：0.5 天。

2. MCP 實作
- 實作細節：解析 JSON 並呼叫對應 API。
- 所需資源：MCP SDK。
- 預估時間：1~2 天。

3. 記錄與回饋
- 實作細節：logs.md 記錄「抽象步驟/建議下一步」。
- 所需資源：檔案系統。
- 預估時間：0.5 天。

關鍵程式碼/設定：
```json
{ "operation": "EstimatePrice", "action": "estimate current cart", "context": "cartId=163; expect total=0" }
```

實際案例：CreateCart/EstimatePrice/CreateCheckout 皆以 RunStep 指令完成。
實作環境：MCP、內部 LLM（GPT-5-mini）。
實測數據：
改善前：冗長提示與高錯誤率。
改善後：以最小協議完成探索，多步驟穩定串接。
改善幅度：上下文與錯誤降低（質性）。

Learning Points（學習要點）
核心知識點：
- 協議設計三要素
- 文本到參數的映射
- 行動摘要與建議回饋

技能要求：
- 必備技能：API 操作抽象
- 進階技能：LLM Prompt-to-Param

延伸思考：
- 能否自動生成下一步計畫？
- 風險：欄位語義歧義。
- 優化：加入 schema 驗證。

Practice Exercise（練習題）
- 基礎：為兩個操作寫 RunStep JSON（30 分）
- 進階：實作映射器（2 小時）
- 專案：做一個 RunStep 模擬器（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：可運作的協議
- 程式碼品質（30%）：欄位語義清晰
- 效能優化（20%）：上下文縮減
- 創新性（10%）：回饋機制


## Case #15: 以 .NET xUnit 生成 API 自動化測試

### Problem Statement（問題陳述）
業務場景：需快速把探索產物生成為穩定可跑的 API 測試，納入 CI。
技術挑戰：要把 session logs、Test Case、Spec 合成高品質測試碼。
影響範圍：回歸自動化、持續交付。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 生成缺少模板與規則。
2. 欠缺環境設定（token）抽離。
3. 斷言不足。
深層原因：
- 架構層面：無標準化生成流程。
- 技術層面：未把 secrets 外部化。
- 流程層面：無審查與回饋。

### Solution Design（解決方案設計）
解決策略：以 TestKit.API.GenCode 生成 .NET 9 + xUnit 測試，token 以環境變數注入，斷言基於 session logs。

實施步驟：
1. 模板化
- 實作細節：建立 fixture、client、helper。
- 所需資源：.NET 專案模板。
- 預估時間：0.5 天。

2. 生成與審查
- 實作細節：生成後人審斷言與邊界。
- 所需資源：Code review。
- 預估時間：10~20 分鐘/測項。

3. CI 接入
- 實作細節：dotnet test，artifact 報告。
- 所需資源：CI。
- 預估時間：0.5 天。

關鍵程式碼/設定：
```csharp
public class ShopApiClient {
  public ShopApiClient() {
    var token = Environment.GetEnvironmentVariable("SHOP_API_TOKEN");
    http.DefaultRequestHeaders.Authorization = new("Bearer", token);
  }
}
```

實際案例：TC01~TC03 生成並執行；4.3 秒完成，結果與探索一致。
實作環境：.NET 9、xUnit。
實測數據：
改善前：無程式化回歸。
改善後：可在 CI 中秒級完成、可重現。
改善幅度：回歸自動化達成。

Learning Points（學習要點）
核心知識點：
- 測試專案模板化
- Token 外部化
- 斷言設計

技能要求：
- 必備技能：.NET、xUnit
- 進階技能：生成器模板維護

延伸思考：
- 對接 Test Management（報告/案例對映）。
- 風險：模板偏差導致品質不一。
- 優化：導入 SpecKit/SDD。

Practice Exercise（練習題）
- 基礎：寫一支 xUnit 測試（30 分）
- 進階：把 logs 轉兩支測試（2 小時）
- 專案：建立可擴充的測試專案模板（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：可跑通與斷言正確
- 程式碼品質（30%）：結構清晰、可維護
- 效能優化（20%）：執行時間
- 創新性（10%）：模板可擴展性


## Case #16: 文件與自動化「左移」—從 AC 到可重用測試資產

### Problem Statement（問題陳述）
業務場景：文件與自動化都在後期補，導致變更多、返工多、成本高。
技術挑戰：如何在前期就收斂文件與自動化方向？
影響範圍：需求清晰度、產出一致性、交付速度。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. AC 未結構化，測試方向模糊。
2. 測項與介面混雜。
3. 自動化晚期才介入。
深層原因：
- 架構層面：缺乏規格驅動。
- 技術層面：無可生成的高品質輸入。
- 流程層面：缺審查點。

### Solution Design（解決方案設計）
解決策略：在需求完成時即生成 Decision Table 與抽象 Test Cases；探索完成即保留 session logs；此三者成為後續 codegen 的可複用資產。

實施步驟：
1. AC→Decision Table
- 實作細節：TestKit.GenTest。
- 所需資源：網域專家。
- 預估時間：0.5 人日。

2. Decision Table→Test Cases
- 實作細節：自動展測項。
- 所需資源：模板。
- 預估時間：0.5 人日。

3. 探索→保留產物
- 實作細節：session logs、HTTP 快照。
- 所需資源：MCP。
- 預估時間：依測項。

關鍵程式碼/設定：
```bash
# 交付檔案最小清單
decision-table.md
tc-*.md
_session/*
```

實際案例：該流程成功產生 14 測項與探索產物，支撐後續 codegen。
實作環境：TestKit、MCP。
實測數據：
改善前：文件與自動化後期才齊備。
改善後：前期即準備好可生成的高品質輸入。
改善幅度：返工與溝通成本下降（質性）。

Learning Points（學習要點）
核心知識點：
- 左移策略
- 可生成輸入三件套
- 文檔與自動化耦合

技能要求：
- 必備技能：文檔結構化
- 進階技能：產物治理

延伸思考：
- 可否把這三件套納入 PR 檢核？
- 風險：早期投入但需求變動。
- 優化：版本化與審查節點。

Practice Exercise（練習題）
- 基礎：把一份 AC 結構化（30 分）
- 進階：產出 Test Cases 與審查清單（2 小時）
- 專案：建立左移模板與指引（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：三件套完整
- 程式碼品質（30%）：可生成性佳
- 效能優化（20%）：返工下降
- 創新性（10%）：治理策略


## Case #17: 資源配比—Brain/GPU/CPU 的成本與邊界

### Problem Statement（問題陳述）
業務場景：人力（Brain）昂貴且慢、AI 推理（GPU）昂貴、程序（CPU）廉價且穩定，需合理分配。
技術挑戰：如何讓每類任務落在最合適資源上？
影響範圍：總成本、可擴展性、交付速度。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 把重複任務丟給 GPU 而非 CPU。
2. 人審投入在非決策性任務。
3. 未建立資源邊界。
深層原因：
- 架構層面：未定義任務分類與邊界。
- 技術層面：缺 codegen 與自動化配套。
- 流程層面：未制定資源策略。

### Solution Design（解決方案設計）
解決策略：人負責判斷（AC/Decision Table 審查），AI 負責探索（GPU），重複執行交給程式（CPU）。以此重構流程與度量。

實施步驟：
1. 分類任務
- 實作細節：決策/探索/回歸 三類。
- 所需資源：流程文件。
- 預估時間：0.5 天。

2. 指定資源
- 實作細節：對應到 Brain/GPU/CPU。
- 所需資源：RACI 表。
- 預估時間：0.5 天。

3. 指標追蹤
- 實作細節：追蹤 GPU 任務次數、CPU 回歸耗時。
- 所需資源：儀表板。
- 預估時間：1 天。

關鍵程式碼/設定：
```text
任務→資源:
- 判斷 = Brain
- 探索 = GPU
- 回歸 = CPU
```

實際案例：GPU 任務由 40,000 次降至 800 次（探索+生成），回歸全部由 CPU 執行。
實作環境：TestKit、CI。
實測數據：
改善前：GPU 任務比例過高。
改善後：GPU 任務 ≈ 2%，CPU 負責 98% 回歸。
改善幅度：成本與時間大幅下降。

Learning Points（學習要點）
核心知識點：
- 任務分類與資源邊界
- 成本模型與指標
- 可擴展性思維

技能要求：
- 必備技能：流程設計
- 進階技能：成本/效能度量

延伸思考：
- 不同模型成本差異如何納入？
- 風險：分類不當造成瓶頸。
- 優化：動態調整比例。

Practice Exercise（練習題）
- 基礎：為三類任務畫 RACI（30 分）
- 進階：設計 GPU/CPU 指標（2 小時）
- 專案：上線成本儀表板（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：分類清楚
- 程式碼品質（30%）：指標可量測
- 效能優化（20%）：GPU 佔比下降
- 創新性（10%）：儀表設計


## Case #18: 合規與治理—以產物快照與外部化設定強化可審計性

### Problem Statement（問題陳述）
業務場景：測試探索與回歸需符合審計與合規要求，包含規格快照、步驟足跡、憑證管理。
技術挑戰：如何在不暴露敏感資訊下保有完整可追溯性？
影響範圍：合規、資安、審計。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 規格與行為未做快照。
2. 憑證硬編在程式碼中。
3. 無清楚產物生命週期。
深層原因：
- 架構層面：未定義治理產物。
- 技術層面：缺 Secret 外部化。
- 流程層面：無產物歸檔流程。

### Solution Design（解決方案設計）
解決策略：每次探索保存 openapi-spec.json、session-logs.md、HTTP 快照；以 .env/環境變數管理 secrets；建立產物歸檔與保留策略。

實施步驟：
1. 產物快照
- 實作細節：探索一開始即下載並保存 spec。
- 所需資源：MCP。
- 預估時間：0.5 天。

2. 憑證外部化
- 實作細節：.env 或 CI Secret 注入，程式讀取。
- 所需資源：Secret Manager。
- 預估時間：0.5 天。

3. 歸檔與保留
- 實作細節：每輪探索產物打包上傳 Artifact。
- 所需資源：CI Artifact。
- 預估時間：0.5 天。

關鍵程式碼/設定：
```bash
# .env
SHOP_API_TOKEN=******

# 程式讀取
var token = Environment.GetEnvironmentVariable("SHOP_API_TOKEN");
```

實際案例：_session 目錄保存 001/002 OAuth、005 API 呼叫、openapi-spec.json、session-logs.md。
實作環境：MCP、CI。
實測數據：
改善前：無足跡、憑證可能散落代碼。
改善後：產物可審計、憑證外部化、安全性提升。
改善幅度：合規風險顯著下降。

Learning Points（學習要點）
核心知識點：
- 產物治理與合規
- Secret 管理最佳實踐
- Artifact 歸檔

技能要求：
- 必備技能：環境變數、CI Artifact
- 進階技能：Retention Policy

延伸思考：
- 能否簽章產物防竄改？
- 風險：產物外洩。
- 優化：加密與權限隔離。

Practice Exercise（練習題）
- 基礎：改為環境變數讀取 token（30 分）
- 進階：將探索產物打包 Artifact（2 小時）
- 專案：建立治理與保留策略（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：產物完整可查
- 程式碼品質（30%）：Secret 不入庫
- 效能優化（20%）：治理自動化
- 創新性（10%）：安全與合規設計



——————————————
案例分類
——————————————

1) 按難度分類
- 入門級：Case 4, 7, 8, 9, 13, 15, 16, 18
- 中級：Case 2, 3, 5, 6, 10, 11, 12, 14, 17
- 高級：Case 1

2) 按技術領域分類
- 架構設計類：Case 1, 6, 11, 14, 16, 17
- 效能優化類：Case 8, 10, 11, 13
- 整合開發類：Case 5, 7, 9, 15, 18
- 除錯診斷類：Case 3, 6, 12, 14
- 安全防護類：Case 7, 18

3) 按學習目標分類
- 概念理解型：Case 1, 2, 16, 17
- 技能練習型：Case 8, 10, 11, 15
- 問題解決型：Case 3, 6, 7, 12, 14, 18
- 創新應用型：Case 4, 5, 9, 13

——————————————
案例學習路徑建議
——————————————
- 入門起點（理解與左移）：先學 Case 2（Decision Table 基礎）、Case 16（左移策略）、Case 4（優先級/分層思想）。
- 探索與抽象（API/Web）：進入 Case 6（MCP 抽象）、Case 7（OAuth2 前置化）、Case 10（A11y 強化）、Case 11（工具選型）。
- 問題診斷（品質與風險）：學 Case 3（AI 表格修補）、Case 12（負向測試）、Case 14（A2A 協議）。
- 自動化與回歸（程式碼化）：學 Case 8（CPU 回歸策略）、Case 15（xUnit 生成）、Case 9（足跡資產化）、Case 18（治理/合規）。
- 架構升維（整體化）：最後學 Case 1（整體工作流重構）、Case 17（資源配比）。

依賴關係：
- Case 2/16 → Case 4/5（需先有抽象測項與左移產物）
- Case 6/7/10/11 → Case 9/12/14（探索與工具成熟後，足跡與診斷更有效）
- Case 9 → Case 8/15（足跡是程式碼生成關鍵輸入）
- Case 1/17 橫跨全程（作為總結與策略指引）

完整路徑建議：
1) Case 2 → 16 → 4 → 5（建立抽象與左移思維）
2) Case 6 → 7 → 10 → 11（掌握探索與工具）
3) Case 3 → 12 → 14 → 9（診斷與規格化足跡）
4) Case 15 → 8 → 18（程式化回歸與治理）
5) Case 17 → 1（資源配比與工作流重構總結）

以上 18 個案例可直接用於實戰教學、專案實作與能力評估。每一案例皆可獨立演練，亦可串接為一條端到端的 AI-First Testing 實作路徑。