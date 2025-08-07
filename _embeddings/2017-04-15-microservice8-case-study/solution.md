# 架構師觀點 - 轉移到微服務架構的經驗分享 (Part 1)

# 問題／解決方案 (Problem/Solution)

## Problem: 「為什麼」要做微服務？—組織盲目跟風、以技術為目標而非以問題為目標

**Problem**:  
許多團隊在還沒搞清楚自身痛點與目標前，就因「微服務很夯」而砍掉重練，導致專案進度嚴重拖延，甚至拖垮整個團隊。

**Root Cause**:  
1. 缺乏「微服務能解決什麼問題」的明確共識。  
2. 將「導入微服務」視為專案目標，而非達成業務敏捷、降低維運成本這些真正需求。  
3. 評估模型僅從技術角度出發，忽略商業流程、組織結構 (Conwayʼs Law)。

**Solution**:  
1. 以「問題驅動」而非「技術驅動」。先盤點系統痛點 (交付速度、維護成本、功能擴充瓶頸…)。  
2. 針對每一痛點，確認微服務能否帶來實質效益 (獨立部署、彈性擴充、異質技術共存)。  
3. 若答案為肯定，再進行服務邊界設計與拆解；若否，維持現況或採更簡單的重構手法。  
4. 資訊透明化：在 kick-off / sprint 0 期間，用工作坊方式讓開發、測試、Ops、PM 一起釐清「Why & What」。

**Cases 1**:  
• 在 DevOps Taipei #4 分享的企業內部 ERP 改版案中，先列出三大痛點：功能加載速度慢、跨 BU 修改風險高、發版需停機。  
• 檢視後發現只有「跨 BU 修改」與「停機發版」適合用微服務拆分；其餘功能沿用單體即可。  
• 方案落地 8 週後，發版停機時間由 4 小時降至 30 分鐘；跨 BU 需求 lead time 從 14 天降至 5 天。  

---

## Problem: 如何正確劃分服務邊界？—切太細、切錯點，兩種都會失敗

**Problem**:  
在拆分單體系統時，團隊經常無所適從：要切哪裡？要切多細？結果不是「切太細」造成維運爆量，就是「切錯」導致跨服務耦合度更高。

**Root Cause**:  
1. 未能將商業流程 (Domain) 與系統模組 (Module) 做一一對應。  
2. 只看「技術高內聚 / 低耦合」指標，忽略實際組織運作。  
3. 缺乏可量化的拆分準則，導致「切到不能再切」的迷思。

**Solution**:  
1. 從 Top-down 方式，先做 Use-Case / Domain Mapping。  
2. 運用 Conway’s Law 校正：「組織怎麼溝通，服務就怎麼劃分」。  
3. 以「足夠即可」為原則：先拆出對應不同 BU / Team 的 Context，保留程式碼健康以利日後再拆。  
4. 使用 UML Use-Case Diagram + 系統架構圖交叉比對，確保二圖可一一映射。  
5. 建立服務評估清單 (Bounded Context 對應、DB 擁有權、跨服務依賴數量、併發量…) 來量化切割點。

**Cases 1**:  
• 某訂票平台將「會員」、「訂單」、「票務」三大 bounded contexts 個別拆出，對應三個 squad。  
• 上線半年後，跨服務呼叫最密集路徑由原 8 hops 降到 3 hops，平均 Trace 完整率提到 98%。  

---

## Problem: 單體系統日益龐大，維護成本呈指數成長

**Problem**:  
現有 Monolith 已達 150 萬行程式碼，任何需求都需通盤測試； build & deploy 要 40 分鐘以上，導致交付週期被拖長。

**Root Cause**:  
1. 功能全部集中在單一程式集，模組間高度耦合。  
2. 發版只能「全或無」，必須重建整顆 artifact、停機更新。  
3. 測試套件龐大，CI pipeline 成本飆升。

**Solution**:  
分階段重構 (Refactoring Strategies)  
• 策略 #1：Freeze Monolith，所有新功能一律變成新服務，透過 Router / API Gateway 分流。  
• 策略 #2：將 Monolith 粗暴切成 Front-end 與 Back-end 兩個 deployable，由 API 做契約；逐步清理冗餘程式。  
• 策略 #3：挑選高變動、高 CPU 的內部模組 (X、Y、Z)，抽取成獨立 REST Service，原模組改呼叫 REST Client。  
• Glue Code 僅用於過渡期；API 契約穩定後，逐漸移除。  
• 以上每一步都能在不影響使用者的前提下，縮短 build/deploy，降低風險。

**Cases 1**:  
• 兩層式 Web+DB 系統重構為三層 (Web+API+DB)，平均 Deploy 時間由 40 分降到 12 分，Regression 測試 Case 量減少 35%。  
**Cases 2**:  
• 以策略 #3 抽離「報表模組」後，報表功能 CPU 最高佔用從 80% 掉到 25%，並支援單獨 scale-out 3 個 Pod。  

---

## Problem: .NET 團隊想用容器化，卻受限於 Linux 主導的 Docker 生態

**Problem**:  
.NET 團隊過去部署皆以 Windows Server / IIS 為主，看到容器化趨勢卻無法落地，擔心需整個 Stack 轉到 Linux。

**Root Cause**:  
1. Docker 生態早期以 Linux 為核心，Windows 缺乏對應鏡像與範例。  
2. IT 部門僅熟悉 IIS 與 MSBuild，對 Linux pipeline 缺乏掌控度。  
3. 認知誤區：「做容器就一定要 Linux」。

**Solution**:  
1. 研究 Windows Container / Hyper-V Container，保留 Windows Kernel 卻取得 Docker 相同 UX。  
2. 導入 .NET Core + Dockerfile，並在 Azure DevOps / Jenkins 建立 multi-stage build。  
3. 漸進策略：  
   - 先將 stateless API 移入 Windows Container；  
   - 再評估能否直接改為 .NET Core + Linux Container。  
4. 異質架構理念：選擇「最適合該服務」的技術棧 (.NET、Java、Redis、ElasticSearch…)，藉由容器隔離將維運複雜度降至最低。  

**Cases 1**:  
• 以 Windows Container 重新包裝 ASP.NET MVC 與 WCF 服務，單一開發分支即可在 Developer Laptop → Test → Prod 全容器化部署；回報「Works on my machine」事件下降到 0。  

---

## Problem: 微服務門檻高—團隊缺乏分散式系統、DevOps、營運自動化能力

**Problem**:  
即使成功拆成服務，因開發與運維流程跟不上，仍舊陷入「部署地獄」「版本地獄」「追 Log 地獄」。

**Root Cause**:  
1. 分散式系統的錯誤追蹤、效能監控、資料一致性處理是全新領域。  
2. 傳統手動部署無法應付瞬增的 Service Instances。  
3. 沒有 CI / CD、Auto Test、Tracing、集中 Log，導致故障 MTTR 大幅上升。

**Solution**:  
1. 架構面：導入 Service Mesh / Centralized Logging (EFK, ELK) / Distributed Tracing (Jaeger, Zipkin) 確保 Observability。  
2. 開發面：Pipeline as Code (Azure DevOps YAML / GitHub Actions) + Test Pyramid (Unit, Contract, E2E)。  
3. 營運面：  
   - 全面 Container Orchestration (K8s / Swarm) + Rolling Update。  
   - 建立 SLA / SLO，並以 Alerting & Auto-Scaling 對應。  
4. 建立「門檻清單」：團隊須先通過 CI 成功率 95%、自動化測試覆蓋 70%、平均發版週期 ≤ 1 週等指標後，才允許做微服務轉型。

**Cases 1**:  
• 實施 K8s + GitOps 後，日均 Deploy 次數由 1 次提升到 15 次；故障 MTTR 從 4 小時降至 20 分鐘。  
**Cases 2**:  
• 引入 ELK、Jaeger 之後，跨服務 Trace 完整率 98%，平均 Debug 時間從 3 小時縮短到 30 分鐘。  

---

以上為〈架構師觀點 - 轉移到微服務架構的經驗分享 (Part 1)〉中提及的主要難題、根因、對策與實績彙整，供讀者快速比對自身情境，擇取合適做法。