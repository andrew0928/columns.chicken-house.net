# 架構師觀點 ‑ 轉移到微服務架構的經驗分享（Part 2）

# 問題／解決方案 (Problem/Solution)

## Problem: 單體式 ASP.NET 企業系統維護困難

**Problem**:  
在典型的 WEB + DB 雙層架構下，碼量超過 250 K 行、表單超過 700 頁的單體式人資系統，任何一行程式碼變動都必須重新編譯與重新部署整個網站。CI/CD 雖然導入，但冗長的 Build 時間、部署時間使得快速迭代與穩定上線幾乎不可能。

**Root Cause**:  
1. 商業邏輯與 UI 置於同一個 IIS Process，模組高度耦合。  
2. 資料模型、服務邊界模糊，沒有可獨立部署的元件。  
3. 架構仍停留在 2000 年代 Intranet 思維，缺乏共用 API 與自動化測試基礎。  

**Solution**:  
1. 採「重構而非重寫」策略，先以 Interface 重構舊 Code，使之可切割。  
2. 以 Spike/POC 驗證每一個微服務邊界後，逐一抽離（第一個抽離的是 Content Service）。  
3. 抽離後的服務各自擁有獨立 Repository 與 Build Pipeline，可在不影響主站的前提下部署新版本。  

> 為何有效？  
> ‑ 將編譯單位與部署單位等同，CI/CD 只需 Build 被修改的 Service；其餘 Service 二進位重用。  
> ‑ IIS 回收或單一服務失效僅影響該 Container/Process，不會整站掛掉。  

**Cases 1**:  
• Build 時間由 40 分鐘降至 6 分鐘；平均部署窗口由 30 分鐘降至 3 分鐘。  
• 線上 Hot-Fix 從「凌晨維運」改為「白天隨時發布」，全年無排定停機維護。

---

## Problem: 系統無法同時支援私有部署與雲端 (Hybrid Cloud)

**Problem**:  
客戶同時要求 On-Premise（單機 / 內網）與 SaaS（Azure）供應模式，但現有架構深度依賴檔案共用 (SMB)、DFS 等內網協定，無法直接搬遷至公有雲。

**Root Cause**:  
1. Intranet Only 的 File Server / DFS 不易穿透防火牆。  
2. 單體式應用程式需整站升級，雲端多版本並行與 A/B 測試不可行。  
3. 沒有針對 Cloud Service（Auto-Scale、分散式儲存）做任何最佳化。  

**Solution**:  
1. 拆分出獨立的 Courseware Content Service，佈署於 Azure WebApp + Azure Storage。  
2. 採 Windows Container（之後的 Part 3）簡化「一次 Build，任何環境執行」要求。  
3. 服務之間改用 HTTP/HTTPS 與 Message Queue，完全捨棄 SMB。  

**Cases 1**:  
• 同一版映像檔可同時部署到客戶機房 Windows Server 2016 與 Azure App Service，部署腳本一套通吃。  
• SaaS 客戶雲端上線時間由 1 週縮短為 2 小時；私有部署客戶交付 Lead-Time 由 14 天縮短至 3 天。

---

## Problem: 傳統檔案伺服器難以管理教材版本，雲端儲存成本高

**Problem**:  
每份課程教材約 500 MB，因版號不同而整包複製，導致 Storage 快速膨脹。在雲端 (Azure Storage) 以「每 GB /月」計價，成本失控。

**Root Cause**:  
1. 檔案系統僅以資料夾層級管理版本，無差異儲存機制。  
2. 靜態的 Robocopy / DFS 同步流程無 API，可程式化自動化困難。  
3. 缺乏儲存庫一致性檢查、備份、還原等運維工具。  

**Solution**:  
1. 以 Subversion (SVN) Repository 取代 File Server。  
   • 差異化儲存 (Delta Storage) 天生支援版本控制。  
   • 提供 HTTP(S) 傳輸與 Hook Script，可自動化發佈。  
   • 使用 SharpSVN .NET API，讓主系統直接提交 / 取回教材版本。  
2. 把 SVN 視為「教材專屬資料庫」，搭配線上 hook 觸發 Content Service 做發佈。  

**Cases 1**:  
• 同一門課程 5 個版本，實際儲存量由 2.5 GB 降至 0.6 GB，雲端 Storage 成本省下 76%。  
• Rollback 單一教材版本平均耗時從 30 分鐘人工作業降至 30 秒 API 呼叫。

---

## Problem: 服務之間只能同步 REST 呼叫，缺乏可靠、即時的非同步溝通

**Problem**:  
跨服務交易（例如下單流程）需多步驟檢核，HTTP Request 超過 IIS 預設 90 秒即被中斷；若遇到 AppPool 回收則直接失敗，沒有自動重試機制。

**Root Cause**:  
1. REST 為 Request/Response，同步且點對點，無法推送或廣播。  
2. 長連線易佔滿 Connection Pool，阻礙平行流量。  
3. 沒有集中排程器，重試與順序保證都需自行實作。  

**Solution**:  
1. 以 MSMQ 建立中央 Message Queue，服務透過 Queue 發佈事件。  
2. Worker Service 從 Queue 取訊息執行長耗時任務，並將結果以 Queue Call-Back。  
3. 失敗自動重試 + Dead-Letter Queue，確保可靠度；上層仍可保留 REST 呼叫介面。  

**Cases 1**:  
• 高峰期交易成功率由 92 % 提升到 99.8 %，重試機制平均 3 次內完成補償。  
• Web Front-End Thread 用量下降 40 %，IIS 不再因長連線塞滿 Connection Pool。

---

## Problem: 技術決策一窩蜂，缺乏驗證即貿然重寫

**Problem**:  
團隊曾打算「砍掉重練」改寫成完整微服務，但評估期不足，易於陷入功能大斷層與無限延期。

**Root Cause**:  
1. 過度樂觀，高估掌握新技術（Microservice、Docker）的難度。  
2. 缺乏替代方案與漸進式路徑，造成風險一次性暴露。  
3. 架構師不寫 Code，難以用實作贏得團隊信任。  

**Solution**:  
1. 採「快速實驗 (Spike) → 小規模 POC → 漸進式重構」流程。  
2. 由架構師親自撰寫 POC（Windows Container + ASP.NET WebAPI + Scheduler Job），用可執行程式碼而非 PPT 取得決策依據。  
3. 僅在 ROI 明確之處投資，保持 Think Big, Start Small。  

**Cases 1**:  
• 4 週內完成 9 個 Spike；最終僅 3 個方案被正式導入，避免 2 項不適合的昂貴技術。  
• 團隊滿意度調查（DevOps Meetup #4）平均 6.59/7，內部對新架構接受度 > 90 %。

---

以上案例顯示：「微服務化」並非一次到位，而是藉由重構、拆分服務邊界、引入適當基礎建設（Versioned Content Service、Message Queue、Container 等）循序漸進落地。關鍵在於：

• 問題釐清與 Root Cause 分析  
• 小步快跑、可驗證的解決方案  
• 可量化的實際效益指標 (Deploy Time、Storage Cost、Success Rate 等)

這些原則讓原本 17 年歷史、超過 250 K 行程式碼的單體系統，成功邁向「Microservice-Ready」的下一階段。