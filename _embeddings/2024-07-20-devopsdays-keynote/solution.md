```markdown
# 從 API First 到 AI First ─ 開發團隊在生成式 AI 時代的挑戰與實踐

# 問題／解決方案 (Problem/Solution)

## Problem: 既有 API 無法被 AI 安全、有效地重複利用  
**Problem**:  
‧ 想把 LLM 納入產品，但現有 API 都是「先寫前端，再補後端」或「只有內部人看得懂」的設計。  
‧ AI 在做 function calling 時，不易判斷可呼叫的端點、正確參數或狀態轉移，導致錯誤多、風險高、無法擴充。  

**Root Cause**:  
1. 檯面下靠口頭協議，文件不完整。  
2. API 過度迎合眼前 UI，一次性捷徑凌駕 Domain 邏輯。  
3. 欠缺狀態機、Scope、APIKey 等「可驗證」設計，AI DX 極差。  

**Solution**:  
‧ 回到「API First」：以 Domain-Service 為核心，用狀態機拆出 *基本* API。  
‧ 明確訂出 Scope╱權限，所有轉移皆為 *atom* 操作，例外用組合端點。  
‧ 以 OpenAPI/Swagger 公開規格 → 供 GPT s 或自家 Copilot 直接讀取。  
‧ 在 Prompt 中只需貼規格，不再額外寫長篇「使用說明」，即可讓 AI 自行判斷並呼叫。  

**Cases 1**: 安德魯小舖 GPTs  
‧ 將同樣的電商後端 API 用「正規化」+ OpenAPI 釋出，ChatGPT 能：  
　1) 自動挑商品 → 2) 呼叫 AddToCart → 3) 結帳，過程零 bug。  
‧ 去年曾用 CRUD 版 API 測試：AI 亂改欄位造成資料毀損，驗證「API 設計品質」的必要性。  

## Problem: UI/UX 改善遇到天花板，無法真正掌握使用者意圖  
**Problem**:  
‧ 傳統做法靠流程設計、AB Test、問卷或跳出率指標，仍無法「一次搞懂」使用者要什麼。  

**Root Cause**:  
‧ 本質上仍是「事前猜測＋事後統計」，只捕捉大多數行為，小眾需求被忽略。  

**Solution**:  
‧ 導入 LLM 作為「意圖解析器」：  
　1) 讓使用者以自然語言提出「目的」，AI 判斷並自動組合 API。  
　2) 於對話過程即時抓滿意度、情緒、偏好，寫回後端客戶註記或訂單備註。  
　3) 把滿意度量表、推薦模型移到 Prompt／Embedding 處理，不必再靠問卷誘導。  

**Cases 1**: DEMO #1「出一張嘴就能結帳」  
‧ 使用者只說「預算 600、我要啤酒」，AI 自動換算價格、走結帳 API。  

**Cases 2**: DEMO #2「偵測購買滿意度」  
‧ AI 從對話判斷用戶不滿意原因，自動寫入 `Order.FeedbackScore = 2`。  
‧ 下次再訪可讀 `Customer.Note = "專心時喝綠茶‧假日喝可樂"` 後給專屬建議。  

## Problem: 開發者缺乏 AI 基礎功，難以把 LLM 變成可維運的元件  
**Problem**:  
‧ 大多只會「在 ChatGPT 打字」，不會把 Prompt、Embedding、RAG、Copilot 等模式落地為程式碼。  

**Root Cause**:  
1. 把 LLM 當黑盒，不理解 Json Mode / Function Calling / Workflow。  
2. 架構仍停留在 MVC，沒有 Controller + Copilot 的雙駕駛思維。  
3. 不清楚向量資料庫、Embed 生成、Token 成本如何影響產品。  

**Solution**:  
‧ 建立「AI 時代基礎術」四件套：  
　1) API First（AI DX）  
　2) 架構放位：把 LLM 當副駕，Controller 掌主流程  
　3) Prompt Engineering：Json Mode、Function Calling、Workflow 範式  
　4) RAG：Embedding＋VectorDB 組裝企業知識庫  

**Cases 1**: DEMO #3 Copilot Console  
‧ .NET + Semantic Kernel → Controller 仍掌控指令流程，Copilot 只在用戶三次呼叫 `help` 時介入。  

**Cases 2**: DEMO #4 部落格 RAG  
‧ Microsoft Kernel Memory 建立向量索引，GPTs 只吃查詢 Top30 文章段落即可回答「這篇文章哪段講 State Machine？」  

## Problem: 傳統 CI/CD Pipeline 無法涵蓋資料、模型與算力的生命週期  
**Problem**:  
‧ 部署僅管理「程式碼、環境、組態」，缺少「資料 → 模型 → GPU/NPU 配置」流程。  

**Root Cause**:  
‧ GitOps、Infra-as-Code 成熟，卻沒把 Data / Model / AI Infra 視為同等資產。  

**Solution**:  
‧ 在「應用程式・環境・設定」三條 Pipeline 外，再增設「AI Pipeline」：  
　• Data ETL → Model Train / Fine-Tune → Model Package → 推論節點部署。  
‧ 同步納入 Git 版本控管，沿用 GitOps 觸發，避免模型與程式碼版本漂移。  

**Cases 1**: 架構藍圖  
‧ 將 GPT‐4o（雲端付費）與 LLaMA3（自管 GPU）並列可插拔 Provider，開發環境自動切到 SLM（Edge NPU），生產環境走高精度模型。  
‧ 單一 Pull Request 即可同時 Rollout 新功能與新模型。  
```