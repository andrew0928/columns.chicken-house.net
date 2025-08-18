# 從 Prompt 到 Product：AI 進入產品化過程的常見難題與對策

# 問題／解決方案 (Problem/Solution)

## Problem: 從 Playground 的「漂亮 Demo」進不到正式環境

**Problem**:  
Proof-of-concept 階段的 Prompt 在 OpenAI Playground / Notebook 上可以跑，但一旦要變成正式服務就會碰到版本不可控、沒有自動化評估、CI/CD 無法接軌等問題，結果 Demo 永遠停留在「看起來可行」。

**Root Cause**:  
1. Prompt 沒被視為「程式碼產物」，缺少 Git 版本控管、Code Review 與測試。  
2. 缺乏可重製的執行環境（Container / API GateWay / Vector DB）。  
3. 沒有明確離線評估或線上指標，導致無法進入產品發版流程。

**Solution**: PromptOps 工作流  
1. Treat Prompt as Code – 把 `.prompt`/`.md` 納入 Git Repo，配合 PR／Code Review。  
2. 建立自動化測試：  
   ```bash
   pytest -m prompt  # 每支 Prompt 對應 YAML 測試用例
   ```  
   以 BLEU / ROUGE / 自訂 regex 評分，PR 未達門檻即 fail。  
3. Containerize LLM Runtime & Vector DB，寫 `docker-compose`：  
   ```yaml
   services:
     inference:
       image: openai-proxy:latest
     vectordb:
       image: qdrant/qdrant
   ```  
4. CI/CD 佈署（GitHub Actions / ArgoCD） → Staging → Prod。  
5. 線上指標：Latency、Token per call、Business KPI（轉換率 / 工單結案率）。

為何有效：把 Prompt 納入標準軟體工程生命週期，就能解決「版本不可追」、「品質不可測」兩大根因。

**Cases 1**: 企業內 FAQ Chatbot  
• 60 條核心 Prompt 進 Git，30+ 測試樣例全自動驗收。  
• 兩週內上線，後續小改 Prompt PR Flow < 1 hr 完成交付。  
• 工單結案時間從 37 hrs → 12 hrs (-67%)。

**Cases 2**: MarTech 內容生成服務  
• Prompt 與 Template 一起上 CI，意外字詞偏差率 < 2%。  
• 版本發佈頻率從單月 1 次 → 每週 2 次 (x8)。

---

## Problem: 老闆／企業主看不到 AI 導入的量化效益

**Problem**:  
技術團隊導入 LLM，但 C-Level 只問「花錢租 GPU、買 Token，KPI 到底是什麼？」導致專案卡在預算審核。

**Root Cause**:  
1. 沒定義與業務直接連結的 North-Star Metric。  
2. 沒有對照組 → 無法量化 AI 帶來的增益。  
3. 評估週期過長，Decision Maker 無耐心等待。

**Solution**: 3-Step ROI 框架  
1. Mapping: 把 AI 能力對應到業務指標 (e.g. TTR, AHT, NPS, CAC)。  
2. Baseline: 蒐集「未使用 AI」的歷史數據當對照。  
3. Experiment: A/B 或 Shadow Deploy，搭配可視化 Dashboard。  
   ```sql
   SELECT
     AVG(handle_time) AS AHT,
     AVG(cs_sat)      AS CSAT
   FROM call_logs
   GROUP BY is_ai_enabled;
   ```  
4. 用「成本－效益」口語化：  
   - 減少 4 FTE × 12 個月 ≈ 480 萬 TWD  
   - Token Cost 60 萬 / 年 → ROI = 700%

**Cases**: 金融客服中心  
• AI Copilot 讓平均處理時長 AHT 由 420 秒降至 260 秒 (-38%)。  
• 同步提升 CSAT 9.2 → 9.6；Token 年成本 50 萬，節約人力 320 萬，ROI ≈ 540%。

---

## Problem: 高度 Domain-Specific 的企業系統，Vibe Coding 發揮有限

**Problem**:  
在醫療 / 保險 / 半導體製造等「行業黑話」極多的專案裡，直接讓 LLM 產生程式碼或文件，往往答非所問。

**Root Cause**:  
1. 基礎模型缺乏該領域資料。  
2. Context Window 受限，無法將龐大知識庫一次性餵入。  
3. 權限、敏感資料限制，阻礙 Fine-tune。

**Solution**: RAG + 專域微調  
1. Retrieval-Augmented Generation：向量化企業知識庫 (SOP、API Spec)。  
   ```python
   vectordb = Qdrant(...)
   retriever = vectordb.as_retriever(top_k=5)
   answer = llm.generate(question, context=retriever.docs)
   ```  
2. LoRA / p-tuning v2 針對關鍵流程細節做 Lightweight Fine-tune。  
3. Prompt Scaffold：把 Domain Term / JSON Schema 嵌入 system prompt。  
4. Data-Governance：敏感資料經 PII Masking 才進訓練管線。

為何有效：RAG 把 Domain Knowledge 壓縮到「檢索 → Context」路徑，Low-Rank Tuning 進一步校正專業措辭，兩者合併即可突破泛用 LLM 的知識邊界。

**Cases**: 保險理賠自動審核  
• Claim 成文檔 200+ 萬筆進向量庫；Hit@5 95%。  
• 理賠試算準確率 88 → 97%。  
• 審核人力減少 35%，三個月回本。

---

## Problem: 開發者只想寫程式，不想跟人溝通，面臨轉型焦慮

**Problem**:  
LLM 讓需求溝通、系統設計暴露在更大的跨域協作中，但部分工程師偏好「閉門造車」，拒絕參與 Prompt 設計／業務對話。

**Root Cause**:  
1. 傳統分工：只對接 Jira、寫 Code、交 PR。  
2. Prompt Driven Development 打破模組邊界，迫使開發者面向業務語境。  
3. 缺少軟技能培訓，害怕暴露知識盲區。

**Solution**: AI Pair-Programming + 角色化轉型路徑  
1. 強化「Architect / Prompt Engineer / SWE」三軸職能地圖，給明確成長階梯。  
2. 導入 AI Pair Programming (Copilot / Codeium) 讓工程師體會「講語言也算寫程式」。  
3. Workshop：業務 + 技術共寫 Prompt，練習 Structured Prompt。  
4. Kudo & Review 制度，把溝通貢獻納入績效。

**Cases**: SaaS 研發團隊  
• 20 名工程師中有 14 名在三個月內提交 ≥10 次 Prompt PR。  
• Pull Request 回合數從 4.1 次降到 2.3 次 (-44%)。  
• 員工滿意度 (eNPS) +12。

---

## Problem: 前後端分離專案，Prompt 零散難以維護

**Problem**:  
React + Go/Node 後端分離，Prompt 可能散落在前端呼叫函式、後端 Service Layer、甚至 Cloud Function，整合測試難以一致。

**Root Cause**:  
1. 缺少「中央 Prompt Registry」；多端各自 copy。  
2. Version Lock 不一致：前端升了 v2 Prompt，後端還在 v1。  
3. CI 測試只覆蓋 API，不覆蓋 Prompt。

**Solution**: 單獨 Package Prompt & Contracts  
1. 建立 `prompts/` 目錄，所有端點透過 SDK 讀取：  
   ```typescript
   import { getPrompt } from '@org/prompt-registry';
   const prompt = getPrompt('userOnboarding_v3');
   ```  
2. Prompt 與 JSON Schema 一起發布 NPM / Go Module。  
3. End-to-End Contract Test：CI 拉最新版 Prompt 跑整合測試。  
4. 在 Mono-Repo (Nx / Turborepo) 上統一版本號。

**Cases**: 電商網站  
• Prompt Registry 佈署後，前後端因 Prompt 不一致導致的 bug 由每月 7 件 → 0。  
• 新增語言版本只需改 Prompt，不動前後端程式碼，迭代時間 -80%。

---

## Problem: 既有功能的小修改，是否需要重開 Prompt File？

**Problem**:  
修改一行文案 / 新增一個欄位就得「整包重寫 Prompt」似乎過度開銷。

**Root Cause**:  
1. Prompt 與細節強耦合，沒有 Parameterization。  
2. 缺少分層與片段化 (Template / Partial Prompt)。

**Solution**: Prompt Modularization  
1. 使用 Mustache / Handlebars 將可變參數抽象化：  
   ```handlebars
   ## system
   You are a HR assistant ...

   ## user
   Generate a {{doc_type}} about {{topic}} with {{tone}} tone.
   ```  
2. 小修改只改 YAML / JSON Config，而非整支 Prompt。  
3. 建 Testing Matrix：Parameter × Locale × Tone，多維度覆蓋率。

**Cases**: HR 文件產生器  
• 74% 的變動從「改 Prompt」→「改參數」即可完成；PR Review 時間 -60%。  

---

## Problem: 維運／Incident 時，AI 可以做什麼？

**Problem**:  
示範多聚焦新功能，但生產環境 Hit Incident 時，工程師仍得手動翻 Log、排查。

**Root Cause**:  
1. Observability 資料量大，人工檢索慢。  
2. Runbook 靠 Confluence / PDF，查找效率低。

**Solution**: LLM-Driven SRE Copilot  
1. Log Summarizer：將 Elastic / Loki Log 送入 LLM，輸出 Top-K Anomaly。  
2. 自動比對 Runbook Knowledge Base (RAG)。  
3. ChatOps：Slash Command `/ai triage POD-123`。  
4. Incident Post-Mortem 自動草稿 + PR Review。

**Cases**: 金流平台  
• 平均修復時間 MTTR 92 min → 35 min (-62%)。  
• On-call Engineer 給出「AI Copilot 幫我先排除 40% 噪音告警」。

---

## Problem: AI 世代來臨，初學者學習曲線跟不上

**Problem**:  
新鮮人擔心「LLM 什麼都會寫」導致自己還沒學好就被取代。

**Root Cause**:  
1. 學習資源聚焦傳統語言基礎，未涵蓋 AI-Native 開發。  
2. 市場上職缺開始要求 Prompt 能力、評估指標經驗。

**Solution**: T-Shape Roadmap 2.0  
1. Deep：資料結構、演算法、網路基礎仍須扎根。  
2. Broad：LLM API、RAG、Prompt Engineering、觀念性數據科學。  
3. Build-in-Public：跑 Kaggle / Hackathon，生成公共作品集。  
4. 社群陪跑：Study4Love、DevOpsDays 等分享與 Co-Hack。

**Cases**: 大學專題生  
• 三個月完成「校園 FAQ Chatbot」並寫成部落格，引流面試 5 家新創。  
• 在面試環節以生成式 AI 實作獲 CTO 青睞，拿到年薪 22% above market offer。

---

🎯 總結  
從 Prompt → Product，不僅是技術落地，更牽涉到流程、指標與組織文化。以上八大常見問題與對策，可作為落地生成式 AI 的行動手冊，協助團隊避開坑洞、快速驗證、確實交付價值。