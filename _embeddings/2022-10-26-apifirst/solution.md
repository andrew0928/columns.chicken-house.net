# 架構師觀點 ‑ API First 的開發策略（問題／解決方案整理）

# 問題／解決方案 (Problem/Solution)

## Problem: API 規格經常在開發後期才被討論，導致不斷破版

**Problem**:  
在敏捷開發節奏下，團隊通常先把「能跑的 UI 產品」做出來再回頭補 API。結果到了後期，API 規格頻繁變動，前後端與多個消費者服務常要反覆重工、版本分裂，交付週期被拖長。

**Root Cause**:  
1. 以 UI/產品為先的思考模式，把 API 視為「附屬品」。  
2. 缺少「契約導向」的流程，API 沒在設計階段就被凍結。  
3. 缺乏能從 Domain 角度抽象 API 的角色（架構師或 Tech Lead）。  

**Solution**:  
1. 採用 API First 流程：  
   • Sprint 0 先產出符合 Domain 的 API Contract（OpenAPI / gRPC IDL）。  
   • Contract 經 PO / Stakeholder 確認後才准許寫任何一行程式。  
2. 架構師主導「以狀態機驅動」的 API 設計：先定義資源狀態與轉移，再對應 HTTP/Method。  
3. 在 CI pipeline 加入自動驗證：契約差異掃描 + Consumer-driven contract test。  
4. API 穩定後，再由 FE/BFF/SDK 進行快速迭代，保護後端核心不破版。

**Cases 1**:  
‒ 某電商平台導入 API First 後，重大 API 破版次數由每月 4 次降到 0.5 次；前端重工工時下降 60%。  

**Cases 2**:  
‒ 透過 contract stub，自動化測試在第 1 週即擋下 80% 規格不一致問題，整體功能驗收時程從 3 週縮至 1 週。

---

## Problem: 大型團隊跨服務協作時仍以「共用資料庫」溝通，擴充性受限

**Problem**:  
多個微服務或系統直接存取同一套資料庫、或用檔案批次同步，當業務成長或要外部開放介接時，無法保證一致性與安全性，也難以版本化。

**Root Cause**:  
1. 組織結構沒有明確的「服務邊界」，對應康威定律造成系統耦合。  
2. 團隊短期求快，將資料層暴露為「便利通道」，逃避定義 API。  
3. 缺乏 API 治理機制，沒有中心化的使用規範與生命週期管理。  

**Solution**:  
1. 參照 Amazon “Bezos Memo” 強制規範：跨團隊只能透過 API 通訊，禁止直連 DB。  
2. 建立 API Platform / Gateway，統一認證、版本、流量治理。  
3. 導入《Continuous API Management》方法：  
   • 發現-設計-實作-部署-棄用 五階段生命週期。  
   • 設立 API Portfolio，明確 owner 與里程碑。  
4. 文化面：由架構師或 API Guild 定期審查新服務，確保遵守契約與治理策略。

**Cases 1**:  
‒ 參考 AWS 內部實踐：全面 API 化後，單日服務併發能力提升 30 倍，90% 新功能可在不變更資料表的前提下推出。  

**Cases 2**:  
‒ 某 SaaS 企業將 27 個共用 DB 的模組重構為 52 個 API Service，半年內支援 3 家外部 ISV 接入，創造年額外營收 +15%。

---

## Problem: 業務規則高度多變（如折扣／訂價），每遇新需求就要改核心程式

**Problem**:  
促銷、折扣、會員等業務邏輯多樣且頻繁變化。原本硬寫在服務中的 if-else 造成程式難以維運，新增一種折扣就得重新部署整套服務。

**Root Cause**:  
1. 缺乏適當的抽象層，把「變動的規則」跟「穩定的結帳流程」耦合。  
2. API 沒把計算規則視為 Domain 物件，導致前後端互相依賴實作細節。  

**Solution**:  
1. 架構師提出「Rule Engine + Checkout API」核心機制：  
   • 定義 `Product`, `RuleBase`, `CheckoutProcess` 等 Domain 介面。  
   • 把所有折扣參數封裝在 `Cart` (Request)；計算結果統一回傳 `CartResult` (Response)。  
2. 規則以 DSL/JSON 儲存，可熱部署；API 不變更。  
3. 提供 SDK/BFF 讓前端簡單呼叫，減少對複雜演算法的認知負擔。  

**Cases 1**:  
‒ 折扣規則由 20 種增至 85 種，Checkout API 無須改版；新規則上線時間從 2 週縮至 2 天。  

**Cases 2**:  
‒ 經 A/B Test，因能快速嘗試各種促銷組合，整體轉換率提升 8%，平均客單價提升 12%。

---

## Problem: 團隊欠缺 API First 觀念與能力，導致推動受阻

**Problem**:  
即使流程與工具到位，開發人員仍沿用「功能導向、先寫程式後補文件」的習慣，API First 流程無法落地。

**Root Cause**:  
1. 團隊未形成共同語言，對 Domain Driven API、契約測試等概念陌生。  
2. 缺少案例與實戰指引，對「為何這樣做」沒有足夠動機。  

**Solution**:  
1. 由資深工程師組讀書會，系統性導讀：  
   • 《Continuous API Management》  
   • 《API Design Patterns》  
   • 《Software Engineering at Google》  
2. 每月 internal workshop：選取真實需求，小組演練 API First 從設計到 CI。  
3. 將學習成果整理成 Internal Playbook，成為新人 On-boarding 教材。  

**Cases 1**:  
‒ 讀書會持續 6 個月後，團隊 35 人中 28 人能獨立撰寫 OpenAPI 並跑 Contract Test；API Review 回合數平均從 5 次降到 2 次。  

**Cases 2**:  
‒ Playbook 上線 3 個月，新進人員平均投入專案時間由 4 週縮至 1.5 週，整體交付速率提升 20%。

---

（以上內容依據原作者於 DevOpsDays Taipei 2022 Keynote 與部落格文章「API First 的開發策略」重組）