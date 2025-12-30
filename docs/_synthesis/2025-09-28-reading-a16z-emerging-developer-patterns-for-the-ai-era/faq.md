---
layout: synthesis
title: "心得 - Emerging Developer Patterns for the AI Era"
synthesis_type: faq
source_post: /2025/09/28/reading-a16z-emerging-developer-patterns-for-the-ai-era/
redirect_from:
  - /2025/09/28/reading-a16z-emerging-developer-patterns-for-the-ai-era/faq/
---

# 心得 - Emerging Developer Patterns for the AI Era

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

Q1: 什麼是 AI-native Git？
- A簡: AI-native Git 重新定義「版控來源」，以文件與 prompt 為 source，程式碼視為產出。它追蹤意圖、測試與生成脈絡，並將生成與驗證整合進提交流程。
- A詳: AI-native Git 是針對 AI 生成時代重設版控意義的觀念與做法。傳統 Git 為手寫程式碼設計，關注行級異動與責任追溯；而在 AI 時代，主要創作來源轉為需求文件、設計說明、指令（prompt）與測試案例，程式碼則更像是「由意圖編譯」後的產出物（artifacts）。因此，AI-native Git 強調：1) 把文件與 prompt 當作真正的 source 管理；2) 在 commit 內記錄生成模型、agent、prompt 與關聯測試；3) 將生成（generate）與驗證（validate）內嵌進版控工作流；4) 引入語意 diff 與意圖追蹤，方便回溯「為什麼這麼改」。此轉變也讓 CI/CD「左移」，將驗證與審查更早前置在意圖層發生。收益包括更可解釋的歷史、可重放的生成上下文、與更貼近需求的審查點。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q3, B-Q1, B-Q2

Q2: 為什麼 AI 時代的「source」從程式碼轉向文件與 prompt？
- A簡: 因 AI 可將意圖轉譯為碼，需求文件與 prompt 成為真正的「來源」，程式碼更像「結果」。版控焦點因此轉為追蹤意圖與上下文。
- A詳: 當 LLM 與 coding agent 可高品質地把意圖（需求、設計、規格）翻譯為程式碼，source 的語意便從 code 位移到「能精準表達人類意圖的產出」——需求文件、規格、prompt、測試與驗證資料。這些內容決定了生成結果，且能被 AI 重複使用、驗證與回溯。相較之下，程式碼成為 artifacts：由意圖產生、可再生與可比較的結果物。因此版控應優先管理能穩定描述意圖的文檔與 prompt，並以語意 diff、關聯測試與生成脈絡輔助審查。此觀念也促成「文件即流程」，讓 CI/CD 從需求層就能啟動驗證，進而縮短迭代路徑與降低溝通成本。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q9, B-Q3

Q3: AI 時代「Source」與「Artifacts」差異是什麼？
- A簡: Source 是人類意圖的表達（文件、prompt、測試），Artifacts 是由 AI 生成的結果（程式碼、映像、可執行）。關鍵在於「意圖可回放」。
- A詳: 在 AI 主導生成的流程中，Source 是能驅動生成的穩定意圖載體，包含需求、設計與驗證（文件、prompt、測試）。Artifacts 則是根據該意圖產生的各式結果，例如程式碼、容器映像或可執行檔。差異在於：1) Source 具可重放性與可驗證性，能驅動生成與評估；2) Artifacts 可由 Source 隨時再生，不必成為唯一真相；3) 審查焦點移至意圖層（文件/測試），而非僅行級 diff；4) 管理上採「文件版控 + 產出物儲存（AM）」雙軌。此分工讓流程左移，提升可維護性、可回溯性與交付速度。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, B-Q3, C-Q1

Q4: 什麼是 vibe coding？
- A簡: Vibe coding 是以意圖敘述與文件驅動的生成式開發方法，由 AI 依需求合成起始專案與程式碼，再透過測試與審查漸進完善。
- A詳: Vibe coding 改變了「先選範本再改」的習慣，轉而以需求文件、系統敘述與具體範例（測試、接口）直接驅動生成。它通常包含：1) 撰寫明確需求/設計（instructions.md、spec、tests）；2) 讓 agent 依 context 生成起始專案與模組；3) 以 TDD/測試導向地迭代修正；4) 透過語意 diff、PR 與人類審查收斂結果。優點是高度客製、快速試不同 tech stack、降低範本鎖定與搬運成本；配合 SDK 封裝與 TDD 可大幅降低錯誤路徑與重工，並提升生產力與品質。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, A-Q17, B-Q10

Q5: 為什麼 Dashboard 會走向「Synthesis（動態生成）」？
- A簡: 因資訊需求高度情境化，AI 能依當下意圖合成UI與圖表，避免堆砌固定面板，讓人機互動更精準且可組態。
- A詳: 傳統 Dashboard 強調「一覽無遺」，卻將理解負擔轉嫁給使用者；不同角色、目標與時點需要的「視圖」差異極大。AI 驅動的 Synthesis 以對話與情境感知（context）理解需求，再動態組裝 Widget、查詢與可視化，呈現「此刻最有用」的圖表與行動。其核心是：1) UI 元件工具化（tool use）；2) LLM 解析意圖並參數化操作；3) 以 Markdown/Mermaid/可視化 DSL 快速渲染；4) 支援 Agent 自用與對人雙向；5) 回饋進一步優化上下文。這讓UI從「預配資訊牆」轉為「按需合成界面」，提升效率與體驗。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q5, B-Q6

Q6: 什麼是 AI-driven Interface？
- A簡: AI-driven Interface 由 LLM 依用戶意圖調度工具與UI元件，結合對話與操作，生成合適的畫面與流程。
- A詳: AI-driven Interface 是將 LLM 置於 MVC 控制核心的介面理念。Controller 透過函式呼叫與事件回報讓 AI 感知使用者行為（點擊、篩選、錯誤）、情境（角色、任務、狀態）與知識（KB），進而選擇合適的 UI 元件（tools）、配置參數並同步對話引導。其特徵：1) 對話+操作並存；2) 模組化 UI 可被AI編排；3) 以 Markdown、Mermaid 等通用標記快速生成內容；4) 可讀取與回寫文件做長期記憶；5) 可透過 Accessibility API 改善感知。結果是由「事前設計流程」轉向「當下意圖驅動」，可大幅提升複雜任務完成率與滿意度。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q7, C-Q5

Q7: 什麼是「Agent-ready Dashboard」？
- A簡: 兼顧人與 Agent 的面板設計：資訊可讀、操作可調用、語意可理解，讓 Agent 能消化、合成並代為行動。
- A詳: Agent-ready Dashboard 在介面與資料語意層為 LLM/Agent 最佳化。重點包括：1) 小元件工具化，具明確名稱、參數與預期輸出；2) 以語意化標記（ARIA、替代文字、結構化資料）讓 Agent 準確識別元素與狀態；3) 支援 Markdown/Mermaid 或 DSL 以文字合成圖表；4) 提供可被Agent存取的資料/查詢工具（如 Log/Metric 查詢）；5) 控制權限與安全邊界，確保「該做的更強、不該做的不能做」。結果是 Agent 可視覺解讀、可工具操作、可知識整合，達成「人-AI共用一個面板」。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q16, C-Q3

Q8: 什麼是 Context Engineering？
- A簡: Context Engineering 是為 LLM 精準規劃與投放上下文的工程方法，透過文件、工具、歷史、指令來提升推理效果。
- A詳: 與早期僅靠「好 Prompt」不同，Context Engineering 關注「把對的資訊放進對的上下文」。方法包含：1) 文件化意圖與規則（instructions.md、spec、KB）；2) RAG/MCP 檔案系統按需載入，像虛擬記憶體管理上下文；3) 對話歷史與角色設定；4) 任務清單與開發筆記作為長期記憶（tasks_md、dev-notes）；5) 工具呼叫回寫資料，形成循環。目標是讓模型即時擁有足夠、準確、最新的資訊，降低幻覺，支撐更長鏈推理與非同步作業。它是 vibe coding 與 Agent 工作流的關鍵能力。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q8, C-Q6

Q9: 為何文件正在進化為工具、索引與互動知識庫？
- A簡: 因文件既易被人讀也可被AI讀，能承載意圖、規格、任務與記憶，並透過工具索引與回寫，形成可互動的知識底座。
- A詳: 文件從「記錄」升級為「驅動」：1) 作為意圖來源（需求、規格、測試）、2) 作為上下文虛記憶（超過 context 時按需載入）、3) 作為互動知識庫（Agent 查詢、更新、註記）、4) 作為任務調度介面（todo/task-list），5) 作為評估與驗證容器（度量、回饋）。Markdown 與結構化段落利於 LLM解析，配合 MCP/RAG 工具可高效檢索與寫回；以 instructions.md 作為共享規則更可讓 IDE/Agent 一致遵循。這使「寫文件」轉為高投報：AI 會看、會照做、會更新，形成持續運轉的協作底座。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, B-Q8, C-Q6

Q10: 什麼是「Document as Code」？
- A簡: 將文件像程式碼一樣管理：用版本控制、PR、CI/CD 發佈，並作為生成與驗證的第一級資產。
- A詳: Document as Code 包含工具與流程兩面：1) 工具：以 Markdown/AsciiDoc 編寫，與程式共存於 Repo；2) 版控：同樣走分支、PR、審查；3) 發行：CI/CD 產出靜態站或 API 文檔；4) 互動：被 IDE/Agent 用來生成、測試與決策；5) 記憶：dev-notes、tasks_md 作為長期上下文。益處是需求-設計-測試-實作統一視圖，且可被 AI 直接取用、索引與回寫。當 vibe coding 成主流，文件就成為真正的「source」，而非附屬品，讓小團隊也能落實嚴謹工程。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, C-Q6, B-Q9

Q11: 為何 Accessibility 是 AI 的通用介面？
- A簡: 可及性標記讓 LLM 像「看得懂」UI 的語意與結構，便於定位元素與操作，顯著提升 Agent 使用應用的成功率。
- A詳: Agent 多以軟體方式「看」與「操控」介面，缺乏真實視覺與肢體。可及性（如 ARIA、替代文字、語意化結構）為其提供語意錨點，使工具如 Playwright MCP 能從 Accessibility Tree 精煉出可理解的 YAML 描述，讓 LLM 準確辨識「登入按鈕」「錯誤訊息」「表單欄位」。此外，OS 的 Accessibility API 也能作為感知通道，理解使用者操作脈絡，支援 AI-driven UI 的情境反應。結論：良好 a11y 不僅對人友善，也對 Agent 友善，成為「Apps through the eyes of an LLM」的基石。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q16, C-Q10, D-Q7

Q12: 什麼是 MCP（Model Context Protocol）？
- A簡: MCP 是為 Agent 標準化工具接入、檔案/檢索、採樣與授權的協定，等同於「AI 時代的通用工具介面」。
- A詳: MCP 由 Anthropic 牽頭，旨在以統一規格為 Agent 提供工具（Tools）、資源存取（FileSystem/Indexing）、授權（OAuth 2.1）、與採樣（Sampling，將模型使用回呼給客戶端）能力。它像是「LLM 的 USB」，將各式工具抽象為具結構的操作，並以安全可控的方式讓 Agent 調用，含：1) 工具描述與參數模式；2) 授權流程（OAuth 2.1）確保按需授權；3) 檔案/索引協定支援上下文裝載；4) 採樣讓 Token 使用集中管理與可視。MCP 正走向事實標準，形成「Agent + Tools」生態的關鍵黏著。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q14, B-Q13, C-Q9

Q13: 什麼是「非同步 Agent 工作流」？為何重要？
- A簡: 以 Issue/PR/任務隊列驅動，讓多個 Agent 背景長時間工作，人只在關鍵節點審查，最佳化規模與效率。
- A詳: 隨 LLM 推理鏈變長、可獨立處理任務變大，互動模式從「即時聊天」轉為「指派—背景執行—回報—審查」。非同步 Agent 工作流將任務寫入平台（Azure DevOps/GitHub Issues），以 Webhook 觸發 Agent 在沙盒工作區拉碼、改碼、測試、發 PR、更新 Issue。好處：1) 可水平擴展（多任務多 Agent 並行）；2) 人類時間花在審查/決策；3) 上下文與規則文件化，降低往返溝通；4) 與 CI/CD 無縫銜接。它讓「外包給 Agent」成為可營運化的開發模式。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, C-Q8, D-Q8

Q14: 什麼是「Beyond .env」的機密管理？為何需要？
- A簡: 單靠環境變數不符 Agent 場景。需改用 OAuth 2.1 等按需授權、可追蹤與可收回的安全流程。
- A詳: 在 Agent 世代，授權對象不再只有後端服務，還包含使用者、Agent 與第三方工具的串連；.env 事先植入金鑰的模式難以控權、追蹤與撤銷。最佳實踐是採 OAuth 2.1：1) 授權即時發生、最小權限、明確範圍；2) 令牌可失效與更新；3) 授權日誌可稽核；4) 配合 MCP 規範化工具授權；5) 與「Agent-Centric Secret Broker」流整合，於需要時索取憑證。這能避免 API Key 泄露、權限濫用與責任不清，滿足法規與安全需求。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q13, C-Q9, D-Q9

Q15: 什麼是 Agent 的「抽象基元」（auth、billing、storage）？
- A簡: 指 Agent 應用的共通基礎能力：認證授權、用量計費、持久化。預期由平台/標準協定提供通用封裝。
- A詳: 類比雲端時代的 PaaS，Agent 時代需要平台級基元：1) Auth：使用者/Agent/工具三方授權（OAuth 2.1）、範圍控制與審計；2) Billing/Usage：統一度量 Token/工具呼叫，用以計價、配額與成本控管（如 MCP Sampling 將採樣回呼到客戶端）；3) Storage：長期記憶、上下文緩存與產出物持久化；4) Commerce：如 OpenAI ACP，提供標準化結帳/支付協定；5) Tracking：行為追蹤與歸因。這些抽象基元將被平台產品化，讓開發者專注於業務 Agent 本身。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q14, B-Q15, C-Q8

Q16: IDE Pair Programming 與 CLI/伺服器端 Agent 有何差異？
- A簡: IDE 側重互動與即時協作；CLI/伺服器側重自動化、可擴展與流水線整合，適合大規模非同步外包。
- A詳: IDE（Copilot/Cursor）像與 AI 結對，開發者影響大，適合探索、局部修補與小步快跑；CLI/伺服器 Agent 則能在沙盒自動拉碼、改碼、測試與發 PR，易於整合 Issue/Webhook 與 CI/CD 形成端到端流程。差異：1) 互動密度：IDE 高、Agent 低；2) 可擴展性：Agent 容易平行化；3) 人工負載：IDE 佔用多，Agent 將人時移到審查；4) 上下文來源：IDE 來自當前編輯，Agent 依文件/任務。組合策略：前期需求/介面探索用 IDE，正式實作與回歸由 Agent 接棒。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q11, C-Q7

Q17: 為何 TDD 對 vibe coding 特別有效？
- A簡: TDD 把需求拆成介面與可執行驗證，能逐步引導 AI 產碼、降低幻覺與重工，並將審查移到測試層。
- A詳: Vibe coding 的弱點在一次性生成大量碼易偏離；TDD 以「介面→測試→實作→重構」節拍，將問題分期可測：1) 先生成 public API/介面，確認方向；2) 生成測試，讓期望行為具體化；3) 讓 AI 以紅綠燈節奏補實作；4) 測試即回歸門檻，減輕行級 review 壓力；5) 失敗時可精準回溯意圖。這種「測試即規格」的方式能明確界定目標，讓 AI 更穩定地收斂，並搭配 CI 持續把關品質。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q10, C-Q1, D-Q2

Q18: SDK 在 AI 時代的定位與價值是什麼？
- A簡: SDK 封裝複雜規範與基礎設施，降低 AI 需生成的碼量與錯誤面，並加速部署與一致性。
- A詳: 即使範本被生成取代，SDK 仍關鍵：1) 封裝雲資源命名/權限/佈署規則，避免生成層處處重複；2) 提供高層 API 與默認，減少 prompt/生成難度；3) 集中安全與合規，降低誤用；4) 配合 TDD 讓測試更穩定；5) 便於跨專案共用與治理。結果是 AI 可在更高抽象層生成較少且更正確的程式碼，縮短從意圖到可佈署的距離，並讓團隊標準化落地。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q4, B-Q3, C-Q4


### Q&A 類別 B: 技術原理類

Q1: AI-native Git 的 gen-commit 流程如何運作？
- A簡: 以 prompt 與測試為輸入，Agent 生成並驗證程式碼；提交中紀錄模型、bundle 與人審門檻，將生成與驗證前置到版控。
- A詳: 技術原理：1) CLI 擴充（如 git gen-commit）接受 --prompt 與 --tests 參數；2) 系統保存 prompt 與鏈結測試；3) 觸發 Agent 以 Repo＋prompt 生成修改；4) 自動跑測試驗證；5) 產出 bundle（意圖＋測試＋變更）並標記需人審檔案；6) 寫入提交訊息含語意摘要與追蹤元資料。關鍵步驟：收集上下文→生成→驗證→產物打包→提交。核心組件：CLI、生成 Agent、測試執行器、語意 diff、Artifacts 管理。效益是將 AI 開發納入嚴謹歷程，可回放可追溯。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q1, A-Q17, C-Q1

Q2: 文件/Prompt 的「語意 Diff」機制是什麼？
- A簡: 將版本差異透過檢索與 LLM 摘要，從文字差異上升到需求意義差異，如新增/刪除的規則與案例。
- A詳: 原理：1) 先做傳統字串/段落 diff 找出變動範圍；2) 以檢索技術定位相關章節與關聯測試；3) 投餵 LLM 生成語意變更摘要（新增兩條需求、刪除一案例、修改成功條件）；4) 連動影響分析（影響模組、需更新的測試、相依文件）；5) 產出可審查的語意差異報告。流程：文本差異→上下文擴展→LLM 解讀→影響映射。組件：Diff 工具、RAG/MCP 檔案、LLM 摘要、報表器。結果是從「改哪行」提升為「改了什麼規則」，更符合 AI 開發的審查需求。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q2, B-Q3, D-Q2

Q3: 「左移」後的 CI/CD 與 Artifacts 管理如何設計？
- A簡: 版控文件與測試為先，程式碼與映像視為 artifacts；管線前段驗證意圖、後段部署成果，雙軌管理與追溯。
- A詳: 設計重點：1) Repo 內文件/spec/tests 為一級資產，對其變更即觸發生成與單元/合約測試；2) 生成的 code/binary/image 進入 AM（Artifacts Manager），保留來源追蹤；3) PR Gate 包含語意差異審查、測試全綠、SCA/安全掃描；4) 部署管線可從 artifacts 重建環境；5) 回溯鏈：運行中版本→artifacts→對應 source（文件/prompt/測試）。核心組件：文件版控、測試執行器、生成 Agent、Artifacts 儲存、追蹤與簽章。此設計讓失敗易還原，成功可重放，滿足合規。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, C-Q7, D-Q2

Q4: AI 驅動 MVC 架構如何設計（Controller+LLM）？
- A簡: Controller 感知使用者事件並上報 LLM；LLM 以 function calling 協調工具與 UI 元件，雙向驅動對話與畫面。
- A詳: 原理：1) MVC 中的 Controller 增設 LLM Client；2) 事件匯報：將用戶操作（加入商品、切換篩選）轉為語意事件送入 LLM；3) LLM 以工具呼叫（function calling）選擇 UI 組件、設定參數（如載入某圖表、篩選條件），並回覆對話；4) View 層依指令渲染（可用 Markdown/Mermaid/DSL）；5) Model 層提供資料存取與校驗。流程：事件→意圖理解→工具決策→UI 重組→用戶回饋。組件：事件轉換器、LLM Client、工具目錄、渲染引擎、權限守門員。可實現「對話+點擊」協同體驗。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, C-Q5, D-Q3

Q5: 動態 Dashboard 合成的執行流程為何？
- A簡: 以對話捕捉需求，LLM 選擇合適 Widget 與查詢，設定參數並渲染；回饋循環修正與擴充視圖。
- A詳: 流程：1) 意圖擷取（對話/事件/角色）；2) 工具清單檢索（可用的 Widget 與查詢）；3) LLM 做映射：需求→Widget+Query+Viz；4) 生成配置（如 JSON/DSL）並渲染（Markdown/Mermaid/ECharts）；5) 後續提問觸發局部更新；6) 紀錄上下文與常用配置，逐步個人化。核心組件：Tool Registry（widget/catalog）、查詢模版、可視化引擎、Context Cache、權限控制。技術關鍵在工具語意化、可參數化與可驗證輸出，讓 Agent 能穩定操控 UI 與數據。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q6, C-Q3

Q6: Agent-ready Dashboard 的渲染機制與核心組件？
- A簡: 以語意標記的元件庫、可參數化查詢、Markdown/DSL 渲染與可寫回的上下文儲存，支撐人機共用。
- A詳: 核心組件：1) 元件庫：語意命名（如 KPICard、ErrorRateChart）、明確參數 schema；2) 查詢層：可參數化的 Log/Metric/事件查詢；3) 渲染層：Markdown/Mermaid/圖表 DSL；4) 可及性語意（ARIA/替代文字）利於 Agent 精準定位；5) 上下文儲存：常用視圖配置與說明可被 Agent 取用/更新；6) 安全：執行範圍控制與審計。流程：Agent 解析需求→組裝元件與查詢→渲染→回寫記錄。使 Agent 能「讀懂」「組裝」「操作」面板。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q7, B-Q5, C-Q4

Q7: 如何讓 AI 感知使用者意圖（Telemetry/Accessibility/Chat）？
- A簡: 同步彙報使用者事件與環境，結合對話上下文與可及性 API，讓 LLM 掌握當下狀態做出正確決策。
- A詳: 機制：1) 事件上報：將點擊、輸入、導航等事件轉語意訊息送入 LLM；2) 對話脈絡：保留 chat history 與用戶指令；3) 可及性：利用 OS/Web Accessibility API 取得 UI 結構與焦點狀態；4) 環境：載入使用者/租戶/任務背景（profile、role、case）；5) 監測：記錄重要里程碑（dev-notes）供後續推理；6) 安全：敏感事件過濾與最小曝光。整合以上可讓 LLM 做正確「下一步」，例如在結帳頻繁異常時觸發關懷或教學。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, C-Q5, D-Q4

Q8: 文件作為「虛擬長期記憶」的原理是什麼？
- A簡: 以文件替代超出 context 的長資料，透過 MCP/RAG 按需載入與回寫，使 Agent 體感擁有更大記憶。
- A詳: 原理：1) 將規格/任務/結果分門別類存檔（docs/、tasks_md、dev-notes）；2) 模型僅載入當前步驟必要片段；3) 以檔案索引/RAG 檢索關聯段落；4) Agent 完成階段任務後將摘要回寫（如 dev-notes）；5) 下次需要時再載入，形成「虛擬記憶體」。關鍵步驟：文件結構化→索引→檢索→投餵→回寫。核心組件：檔案系統 MCP、向量索引、Chunk 策略、上下文管理器。好處在延長推理鏈、降低幻覺與重複，並保留審計軌跡。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q8, A-Q10, C-Q6

Q9: Repo 級 instructions（如 instructions.md）如何被 IDE/Agent 使用？
- A簡: IDE/Agent 啟動時讀取 instructions.md，作為系統層規則，影響生成風格、約束與工具使用策略。
- A詳: 機制：1) 在 Repo 放置 instructions.md，明訂語言、風格、框架慣例、錯誤處理、測試原則、提交規範等；2) IDE（如 Copilot）啟動會讀取並注入為系統指令；3) Chat 時可 @ 該檔讓 LLM 參照；4) 生成器以其約束產碼、命名與結構；5) 與 CI/PR Gate 對應，確保一致；6) 搭配工具清單與範例提升命中率。此設計讓團隊規範在開發第一線生效，減少清潔成本並提升一致性。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q2, D-Q1, A-Q18

Q10: TDD 引導 vibe coding 的技術流程是什麼？
- A簡: 先定義介面，再生成測試，讓測試失敗，最後補實作至綠燈，並以小步快跑持續重構。
- A詳: 步驟：1) 以規格文件/對話生成介面（接口/DTO/契約）；2) 生成對應測試（含邊界情境）；3) 初跑必紅，建立預期；4) 讓 Agent 實作使單測轉綠；5) 重構改善結構與命名，再確保綠燈；6) 擴充整合測試/契約測試；7) PR 審查重點放測試語意與規格一致性。關鍵：單次變更小、可驗證、可回退；將審查重心從行級移到可執行規格，使 AI 生成更可控。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q17, C-Q1, D-Q2

Q11: 伺服器端 coding agent 的 Sandbox 與工作區如何設計？
- A簡: 提供可拉碼的工作區、依賴隔離的工具鏈、可部署測試的基礎設施與安全的憑證傳遞。
- A詳: 設計：1) 工作區：臨時目錄、可 Git 拉碼、快取依賴；2) 工具鏈：編譯器、測試框架、Linter、包管理工具；3) 基礎設施：容器/本機模擬（DB、Redis、Mock）、本地部署與回歸；4) 憑證：以 OAuth/臨時 Token 提供最小權限；5) 日誌追蹤：產出 run log、測試報告與差異報告；6) 安全：資源限額、網路隔離、檔案白名單。流程：Webhook→分派→拉碼→實作→測試→PR→清理。確保可擴展與可審計。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q16, C-Q7, D-Q8

Q12: 非同步 Agent 與 Issue/PR 工作流如何事件驅動？
- A簡: 以 Issue 建任務，Webhook 觸發 Agent，處理後發 PR 並更新 Issue，PR Gate 驗證通過再合併。
- A詳: 機制：1) Issue 建立任務與上下文（需求、測試、參考）；2) 平台 Webhook 觸發 Agent Runner；3) Runner 在 Sandbox 拉碼→執行改動→跑測試→生成報告；4) 發出 PR，標注關聯 Issue；5) PR Gate 驗證（單元/合約/安全/語意 diff）；6) 人工審查與回饋循環；7) 合併後 Pipeline 部署；8) Issue 自動轉換狀態。事件流：Issue.created→Agent.started→PR.opened→Checks.completed→PR.merged→Issue.closed。促成多人多 Agent 並行。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, C-Q8, D-Q8

Q13: OAuth 2.1 在 Agent/MCP 授權中如何運作？
- A簡: 以授權碼流程（含 PKCE）讓使用者對工具端授權，Agent 取得訪問令牌，確保最小權限與可撤銷。
- A詳: 流程：1) Agent 需要使用工具時，導引使用者到授權伺服器（含 PKCE）；2) 使用者同意範圍（scope）；3) 交換授權碼取得存取令牌（Access Token）與可能的刷新令牌；4) Agent 攜帶 Token 呼叫 MCP/後端；5) Token 到期需更新；6) 所有授權有審計紀錄，可撤銷。核心組件：Authorization Server、Client（Agent）、Resource Server（MCP/後端）。此機制取代硬植 .env 機密，滿足即時授權與安全管控。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, C-Q9, D-Q6

Q14: MCP Sampling 如何統一 Token 使用與計量？
- A簡: 透過採樣回呼，將模型推理委回到使用者端或平台端，集中控管 Token 使用量與計費歸屬。
- A詳: 原理：當 MCP 工具需執行模型推理時，不自行持有金鑰，而是把 Prompt 與要求以「採樣請求」回呼到 Agent/客戶端，由其執行模型推理並回傳結果。好處：1) Token 使用算在使用者訂閱下；2) 工具無需保管金鑰；3) 使用者可看見與控制採樣內容；4) 易做集中成本控管與配額；5) 減少供應鏈攻擊面。組件：MCP 客戶端/伺服器、採樣協定、審計與費用報表。讓跨工具的推理成本透明且可治理。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q15, D-Q10, C-Q9

Q15: Agentic Commerce Protocol（ACP）結帳/支付流程怎麼設計？
- A簡: 定義商家 Checkout、支付 Payment 與商品 Feed 的標準 API，使 ChatGPT 內可完成即時結帳。
- A詳: 結構：1) Product Feed：商家以標準格式提供商品資料；2) Checkout API：校驗購物車、配送、稅費與最終金額；3) Payment API：支付授權/扣款結果回傳；4) Agent 流程：對話推薦→組建購物車→呼叫 Checkout→引導付款→確認訂單；5) 安全：OAuth、簽章與審計；6) 體驗：全程在 Chat 內完成。此協定使 Agent 平台承接「商務基礎設施」，讓商家較低成本接入 Agent 生態。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q15, C-Q8, D-Q3

Q16: Playwright MCP 如何利用 Accessibility 樹提升操作準確度？
- A簡: 透過可及性樹將複雜 HTML 精煉成語意化節點 YAML，使 LLM 輕鬆定位按鈕/表單等元素。
- A詳: 機制：1) 爬取頁面可及性樹（角色、名稱、狀態）；2) 轉為精煉 YAML 結構供 LLM 理解；3) 依語意（如 role=button name=登入）選取元素進行點擊/輸入；4) 若頁面 a11y 做得好，定位準確且上下文清晰；5) 反之將難以找到正確元素、誤操作或反覆嘗試。關鍵：語意標注與可及性結構化比單純 DOM 更利於 LLM 操作，且 context 更省。最佳實踐是落實 ARIA 與語意 HTML。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q11, C-Q10, D-Q7

Q17: 設計 MCP 工具的原則有哪些（語意、情境、安全）？
- A簡: 工具需語意清晰、參數結構化、輸入輸出可驗證；貼合情境最小化步驟；以 OAuth 與範圍控權確保安全。
- A詳: 原則：1) 語意：名稱直觀（如 create_invoice）、參數 schema 明確、回應含狀態/錯誤；2) 情境：設計高階動作減少多步對話（最少化 Token）；3) 安全：OAuth 2.1、Scope 嚴格、審計與速率限制；4) 文件：示例豐富、邊界行為清楚；5) 可測：合約/端到端測試；6) 合規：對個資/金流等敏感領域提供合規證據。這些原則讓 Agent 更可靠地使用工具，降低幻覺與誤用風險，提升成功率。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q12, B-Q13, D-Q6


### Q&A 類別 C: 實作應用類（10題）

Q1: 如何實作一個簡化版「git gen-commit」流程？
- A簡: 以 CLI 包裝提交：讀取 prompt/測試→呼叫 Agent 生成→執行測試→產出語意訊息→提交並標註元資料。
- A詳: 步驟：1) 建 CLI（Node/TS 或 Python）接受 --prompt 與 --tests；2) 將 prompt/測試路徑寫入 .ai-commit/metadata.json；3) 呼叫 API/本地 Agent 生成變更；4) 執行單測（npm test/pytest），擷取結果；5) 用 LLM 產生語意型 commit message；6) git add/commit，訊息含模型/測試鏈結。程式碼片段（Node/TS 概念）：const prompt=fs.readFileSync(p); runAgent(prompt); runTests(); const msg=await summarizeDiff(); execSync(`git commit -m "${msg}"`); 注意：確保測試可重現、失敗即中斷；保存生成/驗證日誌。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q10, D-Q2

Q2: 如何設定 Repo 級 instructions.md 並與 IDE 整合？
- A簡: 在專案根目錄撰寫 instructions.md，定義規範與範例；於 IDE 啟動時自動載入，聊天可 @ 該檔。
- A詳: 步驟：1) 建立 instructions.md：包含命名、錯誤處理、日誌、測試原則、文件風格、提交規範、框架慣例；2) 放常見反例/範例；3) 安裝 Copilot/Cursor 外掛，確保其讀取 Repo 文件；4) 在提示中「@instructions.md」強化載入；5) PR Gate 對應規範（Lint/格式/測試覆蓋率）；6) 定期回收改進。片段：# Errors: 使用 Result<T,E>；# Tests: 每個 public 函式需單測。注意：保持簡潔可執行，避免冗長哲學；用範例勝過口號。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q9, D-Q1, A-Q18

Q3: 如何用 React + Chat 建構動態 Dashboard（LLM 選擇 Widget）？
- A簡: 將 Widget 註冊為 tools，Chat 決定用哪些 widget/參數；前端依返回配置渲染。
- A詳: 實作：1) Widget Registry：定義 name、props schema、render；2) Chat 後端提供 /compose API，輸入 user intent，輸出 {widgets:[{name,props}]}; 3) 前端接收配置動態渲染；4) 工具用法例：getErrorRate({service,window})；5) 最佳化：快取查詢、錯誤回退 UI。關鍵碼（概念）：const layout = await composeLLM(intent); return layout.widgets.map(w=>render(w.name,w.props)); 注意：限制可用 widget 白名單；為每個 widget 提供範例與安全檢查；以 Markdown/DSL 減少渲染複雜度。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q6, D-Q3

Q4: 如何用 Markdown + Mermaid 產出圖表型報表？
- A簡: 讓 Agent 輸出 Markdown 內含 Mermaid 區塊，前端/Docs 工具負責渲染成圖，支援可讀與可維護。
- A詳: 步驟：1) 提供資料查詢工具（metrics/log）；2) Prompt 指導輸出 Markdown＋```mermaid```圖；3) 前端/靜態站啟用 Mermaid 渲染；4) 提供範例模板（流程、序列、甘特、關聯圖）；5) 圖表旁輸出要點摘要。程式片段（Mermaid）：graph TD; A[API Gateway]-->B[Error 500升高]; 注意：控制長度、拆分多圖；對關鍵數據加上表格；確保渲染器安全設定（禁 JS 注入）。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q6, A-Q5, D-Q3

Q5: 如何在 MVC Controller 回報用戶事件給 LLM（function calling）？
- A簡: 將重要操作轉語意事件並呼叫 LLM 函式，返回對話與 UI 指令，同步驅動雙通道互動。
- A詳: 步驟：1) 定義事件 schema：action、entity、payload；2) 封裝 reportEvent() 呼叫 LLM tool：report_user_action；3) LLM 返回 actions：如 show_tip、render_widget、warn；4) Controller 依指令更新 UI 與對話；5) 設計保護：僅允許白名單動作。片段：await llm.call('report_user_action',{action:'add_to_cart',item:'cola',qty:5}); 注意：對個資/敏感資料脫敏；限制頻率與尺寸；為每種事件提供範例，讓 LLM 學會判斷時機。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q7, D-Q4

Q6: 如何搭建 Document-as-Code 工作區（含 tasks_md、dev-notes 自動化）？
- A簡: 建立 docs/、tasks_md、dev-notes 流程，讓 Agent 自動回寫摘要與任務，形成長期記憶。
- A詳: 步驟：1) 目錄：docs/spec、docs/design、docs/dev-notes、docs/tasks；2) 在 instructions.md 要求：遇里程碑或重大變更自動更新 dev-notes；3) 建 LLM tool：append_dev_note、update_task；4) 工作流：需求→建立 tasks_md→Agent 逐項完成並勾選→結束回寫筆記；5) CI 檢查：tasks_md 與 PR 內容一致性。注意：控制檔案大小與分頁；加上日期錨點；對較舊筆記用索引摘要避免載入爆量。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, A-Q9, D-Q5

Q7: 如何建立伺服器端 Coding Agent Runner（拉碼、測試、開 PR）？
- A簡: 以 Webhook 觸發容器化 Runner：git pull→生成→測試→PR→更新 Issue，並輸出完整報告。
- A詳: 步驟：1) 接 Issue/任務 Webhook；2) 啟動容器 Runner，掛載臨時工作區；3) 取得臨時 Token（OAuth/CI 憑證）；4) 拉碼與依賴；5) 呼叫 Agent 實作；6) 跑測試/靜態掃描；7) 生成差異與語意摘要；8) 開 PR、標注 Issue；9) 上傳報告；10) 清理環境。關鍵設定：最小權限、資源限額、可觀測性（log/trace）。最佳實踐：失敗重試策略、冪等設計、PR Gate 嚴格化。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q11, B-Q12, D-Q8

Q8: 如何在 GitHub/Azure DevOps 設定非同步 Agent 工作流？
- A簡: 以 Issue/Work Item 為入口，配置 Webhook/Service Hook 觸發 Runner，PR Gate 嚴格把關與自動關聯。
- A詳: 步驟（GitHub 為例）：1) 規劃 Issue 模板（需求/驗收/測試連結）；2) 設置 Webhook 至 Runner；3) 在 Actions 設 PR Gate（測試/安全/語意 diff）；4) 使用自動關聯關鍵字（fixes #123）；5) 建立 label/專案板追蹤進度；6) 將產生報告以 bot 評論附上。Azure DevOps 類似：Service Hook→Pipeline→Checks→Policies。注意：權限最小化、審計日誌、錯誤告警與手動干預入口。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, A-Q13, D-Q8

Q9: 如何為 MCP Server 實作 OAuth 2.1 授權（Auth Code + PKCE）？
- A簡: 實作授權端點、Token 交換與範圍檢查；Client（Agent）用 PKCE 流程取得 Access Token 呼叫工具。
- A詳: 步驟：1) 註冊 Client（Agent），啟用 PKCE；2) 實作 /authorize（同意畫面，回傳 code）；3) 實作 /token（code 換 token，驗 PKCE）；4) 在工具端驗 Scope；5) 設 Token 失效/刷新策略；6) 記錄審計與撤銷機制。設定片段（概念）：authorization_endpoint、token_endpoint、scopes=[read:calendar]。注意：精準 Scope、Redirect URI 白名單、避免機密落地；提供清楚同意文案與可視化審計。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q13, B-Q17, D-Q6

Q10: 如何改善網頁可及性以利 Playwright MCP 操作（ARIA/測試）？
- A簡: 為互動元素加語意角色與名稱，提供替代文字與表單關聯；用自動化測試驗證可定位度。
- A詳: 步驟：1) 使用語意 HTML（button、nav、form）；2) ARIA：為重要元素提供 role/name/state；3) 圖片加 alt、表格加 caption/headers；4) 表單以 label for 與 aria-describedby；5) 鍵盤可達性；6) 用 a11y 測試（axe/Playwright a11y snapshot）驗證；7) 以 Playwright MCP 嘗試定位與操作；8) 修復無法定位的元素。範例：<button aria-label="登入">🔒</button>。注意：避免僅圖示無名稱；用戶看得到、Agent 也要「讀得到」。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q16, D-Q7, A-Q11


### Q&A 類別 D: 問題解決類（10題）

Q1: 遇到 Agent 送來品質不佳的 PR 怎麼辦？
- A簡: 症狀：結構差、命名亂、風格不一。原因：規範缺失、上下文不足。解法：強化 instructions、導入 TDD 與 PR Gate。預防：文件化規則與範例。
- A詳: 症狀描述：PR 雖通過編譯但可讀性差、測試不足、與團隊風格不一致。可能原因：1) instructions.md 貧弱或不一致；2) 缺少介面/測試引導；3) Agent 工具/SDK 不完善；4) PR Gate 寬鬆。解決步驟：1) 先補齊介面與測試，要求紅綠燈迭代；2) 將命名/錯誤處理/日誌等規範寫入 instructions；3) 設 Lint/格式化與覆蓋率門檻；4) 以語意 diff 審查需求符合度。預防：提供豐富正反例、模版化測試、SDK 封裝複雜度，降低自由度造成的偏差。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q9, A-Q17, C-Q2

Q2: gen-commit 後驗證失敗怎麼排查？
- A簡: 症狀：測試紅燈/建置失敗。原因：上下文不足、測試/依賴不一致。解法：重跑測試、檢查語意 diff、補齊上下文。預防：TDD 與可重現環境。
- A詳: 症狀：CLI 回報 validate fail、CI 紅燈。原因：1) Prompt 少關鍵限制；2) 測試脫節或資料夾錯；3) 依賴/環境缺。排查：1) 本地可重現測試；2) 查語意 diff 是否與需求不符；3) 檢視 Agent log 與產出；4) 檢查 SDK/依賴版本；5) 必要時縮小變更面。解法：補充 instructions/測試案例、鎖定依賴、重走 TDD 流程。預防：標準化測試命令、固定版本、前置介面與契約測試。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q10, C-Q1

Q3: 動態 Dashboard 顯示錯誤圖表如何處理？
- A簡: 症狀：圖不對題或數據錯。原因：意圖解析錯、查詢參數誤。解法：檢查 compose 配置、加入範例與約束。預防：Widget schema 嚴格化。
- A詳: 症狀：顯示錯服務、時間窗不符或指標計算錯。原因：1) LLM 未抓到角色/情境；2) Widget/Query 參數設計含糊；3) 渲染 DSL 誤。解決：1) 設計更清晰的 Widget schema 與預設值；2) 在 Prompt/工具描述中加入用例；3) 對回傳配置做 JSON Schema 驗證；4) 加入「語意回饋」引導 LLM 調整；5) 比對查詢 SQL/PromQL 與期望。預防：用範例集測，將常見任務固化為模板。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q3, A-Q5

Q4: 用 LLM 推論 UX 滿意度出現「幻覺」怎麼降低？
- A簡: 症狀：評分不穩定或無依據。原因：上下文不足/標準模糊。解法：定義分級準則、提供操作脈絡、用多模型交叉。預防：結合傳統追蹤。
- A詳: 症狀：同行為評分波動、理由與事實不符。原因：1) 無明確打分標準；2) 缺操作序列/錯誤訊息上下文；3) 模型漂移。解法：1) 在 system 內定義 1~10 級準則與示例；2) 傳入關鍵事件/錯誤/用時；3) 以 CoT/多輪校核；4) 對關鍵樣本人審標註回灌；5) 設置信心水準閾值。預防：混合方法（LLM 推論＋行為指標），持續校準標籤品質。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q7, C-Q5, A-Q6

Q5: Context window 爆掉或回應脫題怎麼辦？
- A簡: 症狀：截斷、失焦。原因：投入過量或無結構。解法：文件分塊、RAG/MCP 按需載入、摘要回寫。預防：Context Engineering。
- A詳: 症狀：回答跳針、忽略關鍵。原因：1) 直接塞整本文件；2) 缺索引與檢索策略；3) 歷史拖泥帶水。解決：1) 文檔分章節與 Chunk；2) 使用檔案系統 MCP 與 RAG 根據查詢載入；3) 以「摘要→細節」兩段式；4) 管控歷史長度與主題切換；5) 任務完成即回寫 dev-notes。預防：建立 Context Policy、文檔結構化與檢索測試，確保「對的資訊在對的時機」。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, C-Q6, A-Q8

Q6: MCP 工具無法取得授權怎麼診斷？
- A簡: 症狀：401/403 或循環登入。原因：Redirect URI/Scope/PKCE 錯。解法：比對設定、查授權伺服器日誌。預防：範圍最小化與白名單。
- A詳: 症狀：授權畫面正常但呼叫被拒；或授權無法完成。原因：1) Redirect URI 不符註冊；2) 未送 PKCE；3) Scope 不正確；4) Token 過期或錯誤受眾（audience）。解決：1) 比對 Client 設定與 AS 註冊；2) 確認 Code+PKCE 流程；3) 驗 Scope 與資源伺服器要求；4) 讀 AS 與 Resource Server 日誌；5) 重新授權撤銷舊 Token。預防：自動測試授權流程、清晰文件範例、Fail-safe 錯誤訊息。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q13, C-Q9, A-Q14

Q7: Playwright MCP 找不到按鈕怎麼辦？
- A簡: 症狀：元素存在但無法定位。原因：缺 a11y 標記或語意。解法：補 ARIA/name/label。預防：a11y 自動檢測。
- A詳: 症狀：LLM 多次嘗試仍失敗。原因：1) 僅圖示無名稱；2) 自訂 DIV 當按鈕；3) 表單缺 label；4) 動態狀態無語意。解決：1) 使用語意元素（button/input）；2) 加 aria-label 或 accessible name；3) 為表單加 label for；4) 狀態用 aria-pressed/selected。驗證：a11y 自動化（axe）與 Playwright a11y snapshot。預防：a11y 規範入門檻與 PR Gate。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q16, C-Q10, A-Q11

Q8: 非同步 Agent 任務卡住或重複循環怎麼處理？
- A簡: 症狀：長時間無進展或無限重試。原因：上下文不足、錯誤未被辨識。解法：超時與斷路器、回寫狀態、人工介入。
- A詳: 症狀：Issue 長期停滯、Runner 無限重跑。原因：1) 需求模糊；2) 測試不 determinisitc；3) 錯誤類型未被工具化；4) 缺超時策略。解決：1) 設定任務超時與重試上限；2) 回寫 dev-notes 說明卡住原因；3) 以錯誤類型引導人機分工（需要人決策的自動轉單）；4) 引入斷路器與人工批准步驟。預防：規格化任務模板、測試穩定化、事件監控與告警。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, C-Q8, A-Q13

Q9: .env 洩漏導致 API Key 暴露怎麼辦？
- A簡: 症狀：非預期消費或被濫用。原因：秘鑰硬植/版本控制失誤。解法：立即撤銷、稽核與通報。預防：OAuth 與密鑰保管。
- A詳: 症狀：帳單暴增、外部呼叫異常。處置：1) 立即撤銷 Key 與輪替；2) 盤點使用處；3) 查版本控制/日誌；4) 通報影響方與法遵流程；5) 監控再發。根因：1) .env 入庫或誤傳；2) Shared 秘鑰擴散；3) 無最小權限。預防：OAuth 2.1 取代長期 Key、密鑰管理（Vault）、CI Secret 授權、檔案忽略規則、密鑰掃描工具、MCP Sampling 減少下游金鑰散佈。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q13, C-Q9

Q10: Token 成本暴增如何優化（Sampling/工具呼叫/上下文）？
- A簡: 症狀：月費飆升。原因：上下文冗長、工具多步、工具內再推理。解法：採樣回呼、上下文精簡、工具高階化。
- A詳: 症狀：同任務成本過高。原因：1) 投喂過多上下文；2) 工具過度原子化導致多輪；3) 工具內部自行推理持金鑰。解法：1) 用 MCP Sampling 將推理回返客戶端，集中計量；2) 設計高階工具減少輪數；3) 嚴控上下文（摘要、檔案按需載入）；4) 快取重複查詢；5) 以模型選擇策略（路由到性價比更高的模型）。預防：成本儀表板、配額與告警、預算上限與降級策略。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q14, B-Q5, C-Q3


### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 AI-native Git？
    - A-Q2: 為什麼 AI 時代的「source」從程式碼轉向文件與 prompt？
    - A-Q3: AI 時代「Source」與「Artifacts」差異是什麼？
    - A-Q4: 什麼是 vibe coding？
    - A-Q5: 為什麼 Dashboard 會走向「Synthesis（動態生成）」？
    - A-Q6: 什麼是 AI-driven Interface？
    - A-Q9: 為何文件正在進化為工具、索引與互動知識庫？
    - A-Q10: 什麼是「Document as Code」？
    - A-Q11: 為何 Accessibility 是 AI 的通用介面？
    - B-Q1: AI-native Git 的 gen-commit 流程如何運作？
    - B-Q5: 動態 Dashboard 合成的執行流程為何？
    - B-Q9: Repo 級 instructions 如何被 IDE/Agent 使用？
    - C-Q2: 如何設定 Repo 級 instructions.md 並與 IDE 整合？
    - C-Q4: 如何用 Markdown + Mermaid 產出圖表型報表？
    - D-Q7: Playwright MCP 找不到按鈕怎麼辦？

- 中級者：建議學習哪 20 題
    - A-Q7: 什麼是「Agent-ready Dashboard」？
    - A-Q8: 什麼是 Context Engineering？
    - A-Q12: 什麼是 MCP（Model Context Protocol）？
    - A-Q13: 什麼是「非同步 Agent 工作流」？為何重要？
    - A-Q14: 什麼是「Beyond .env」的機密管理？為何需要？
    - A-Q16: IDE Pair Programming 與 CLI/伺服器端 Agent 有何差異？
    - A-Q17: 為何 TDD 對 vibe coding 特別有效？
    - B-Q3: 「左移」後的 CI/CD 與 Artifacts 管理如何設計？
    - B-Q4: AI 驅動 MVC 架構如何設計（Controller+LLM）？
    - B-Q6: Agent-ready Dashboard 的渲染機制與核心組件？
    - B-Q7: 如何讓 AI 感知使用者意圖？
    - B-Q8: 文件作為「虛擬長期記憶」的原理是什麼？
    - B-Q10: TDD 引導 vibe coding 的技術流程是什麼？
    - B-Q16: Playwright MCP 如何利用 Accessibility 樹提升操作準確度？
    - C-Q1: 如何實作一個簡化版「git gen-commit」流程？
    - C-Q3: 如何用 React + Chat 建構動態 Dashboard？
    - C-Q5: 如何在 MVC Controller 回報用戶事件給 LLM？
    - C-Q6: 如何搭建 Document-as-Code 工作區？
    - D-Q2: gen-commit 後驗證失敗怎麼排查？
    - D-Q3: 動態 Dashboard 顯示錯誤圖表如何處理？

- 高級者：建議關注哪 15 題
    - A-Q15: 什麼是 Agent 的「抽象基元」（auth、billing、storage）？
    - B-Q11: 伺服器端 coding agent 的 Sandbox 與工作區如何設計？
    - B-Q12: 非同步 Agent 與 Issue/PR 工作流如何事件驅動？
    - B-Q13: OAuth 2.1 在 Agent/MCP 授權中如何運作？
    - B-Q14: MCP Sampling 如何統一 Token 使用與計量？
    - B-Q15: Agentic Commerce Protocol（ACP）結帳/支付流程怎麼設計？
    - B-Q17: 設計 MCP 工具的原則有哪些？
    - C-Q7: 如何建立伺服器端 Coding Agent Runner？
    - C-Q8: 如何在 GitHub/Azure DevOps 設定非同步 Agent 工作流？
    - C-Q9: 如何為 MCP Server 實作 OAuth 2.1 授權？
    - D-Q4: 用 LLM 推論 UX 滿意度出現「幻覺」怎麼降低？
    - D-Q5: Context window 爆掉或回應脫題怎麼辦？
    - D-Q6: MCP 工具無法取得授權怎麼診斷？
    - D-Q8: 非同步 Agent 任務卡住或重複循環怎麼處理？
    - D-Q10: Token 成本暴增如何優化？