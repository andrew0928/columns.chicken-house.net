# 微服務基礎建設 – Service Discovery

# 問題／解決方案 (Problem/Solution)

## Problem: 難以在大規模微服務環境中「找到」正確且健康的服務

**Problem**:  
當一個單體應用被拆分為成百上千個微服務並動態地（隨流量）擴縮容時，開發或運維人員已不可能再以「硬編碼 IP + PORT」或人工編輯設定檔的方式，去維護所有服務端點。結果是：  
• 呼叫端不知道該往哪裡送請求  
• 若某些 service 當掉，呼叫端仍可能錯誤地送出請求而失敗  
• 啟動新 service instance 時，其他服務無從得知其位置

**Root Cause**:  
1. 服務數量多且動態：每幾秒就可能有新 instance 啟動或終止  
2. DNS/DHCP 等傳統機制 TTL 長、缺乏 metadata、無健康檢測能力  
3. 沒有集中且即時更新的「服務清單 (registry)」與健康狀態

**Solution**:  
導入「Service Discovery 機制」，由三個動作組成：  
1) Register：服務啟動時自動向 registry 報到  
2) Query：呼叫端在執行 RPC 前先查詢可用端點  
3) Health Check：持續檢測/回報服務健康度，及時剔除故障節點  

實作可對應下列模式：  
• Self-Registration / Third-Party Registration（確保 registry 資訊正確性）  
• Client-Side Discovery（呼叫端 SDK + 自行負載均衡）  
• Server-Side Discovery（Registry-Aware Load Balancer / API Gateway）

這樣即可把「找到位置」與「檢測健康」兩大痛點一次解決。

**Cases 1**: Docker Internal DNS + Compose  
- 每個 container 啟動後自動向 Docker 內建的 DNS(127.0.0.11) 註冊，service name 即 host name。  
- 任何 container 只需 query 該 host，即可取得最新 IP 清單並直接呼叫。  
- 加上 Nginx reverse-proxy，可對外提供單一入口(point-of-contact) 並做負載均衡。  

**Cases 2**: Consul  
- 服務以 HTTP/TCP/Script 方式向 Consul Register。  
- Consul 內建 Health Check，並提供 DNS 及 HTTP 兩種查詢介面，同時內含 KV store 做集中式設定管理。  
- 跨資料中心同步，支援 fail-over 與 configuration long-poll。  

**Cases 3**: Netflix Eureka + Ribbon  
- Eureka 做 registry；服務啟動時自註冊並定時 heart-beat。  
- 呼叫端使用 Ribbon(Registry-Aware HTTP Client) 先 query，再在 client 內做負載均衡及容錯。  
- Ribbon 支援多協定、快取及批次呼叫，已在 Netflix 大規模環境實戰驗證。

---

## Problem: Client-Side Discovery 造成程式碼侵入與維運困難

**Problem**:  
若採「Registry-Aware Client Library」(如 Ribbon) 方案，所有呼叫端都必須在程式碼中引用特定 SDK，日後只要調度邏輯或協定更新，就要重新編譯、重新部署全部服務；多語言系統也可能找不到對應 SDK。

**Root Cause**:  
1. Client-Side Discovery 屬「侵入式」：邏輯被寫在應用程式內  
2. 不同語言/框架需維護多套 library → 更新成本高  
3. 熱修補難度大：需同時升級 N 個服務才能讓新策略生效

**Solution**:  
改採「Server-Side Discovery Pattern」：  
• 於服務呼叫路徑前加一層 Registry-Aware Load Balancer (LB) / API Gateway  
• LB 定期向 Service Registry 取得最新可用節點列表並轉送流量  
• 應用程式端只需固定呼叫 LB，不需任何 SDK，相當於把 service discovery 與負載均衡集中管理、對應用透明  
• 更新調度策略時，只須更新 LB/Registry，即刻全體生效

**Cases 1**: Azure Load Balancer / AWS Elastic Load Balancer  
- VM 或 Container 啟動即向雲端內部 Registry 報到  
- LB 依 Registry 資訊自動把外部請求導到可用節點  
- 使用者不需改動程式碼即可滾動更新或動態擴縮

**Cases 2**: Docker Swarm Routing Mesh  
- Swarm 內部 Manager node 擔任 registry & LB，Worker 隨時向 Manager 報心跳  
- 所有 ingress 流量經 Swarm Mesh，自動散佈到 service task  
- 部署/升級僅動態調整 Swarm Service，不干涉應用程式

---

## Problem: 只靠 Heartbeat 難以精準反映服務健康度，導致 Registry 錯誤

**Problem**:  
服務 instance 可能「AP 還活著但功能已失效」，仍持續送 heartbeat，Registry 便把它視為正常；呼叫端 query 後得到「看似正常」的呼叫點，結果請求失敗。

**Root Cause**:  
1. 心跳機制只能代表「process 還在」，無法代表「商業邏輯可用」  
2. 內部網路正常 ≠ 外部服務正常 → 單點偵測失真  
3. Registry 若僅依 heartbeat 判斷，將把不健康節點留在清單

**Solution**:  
採「Third-Party Registration / External Health-Check」：  
• 由獨立 Agent 或 Service 定時從「外部視角」對每個服務進行 HTTP/TCP 探測  
• 透過腳本/探針驗證功能性，如登入 API、資料庫連線等  
• 檢測失敗時，Registry 立即下線該 service endpoint，確保呼叫端永遠只拿到健康清單

**Cases**: Consul Health Check  
- Consul Agent 在每台主機上執行，對本地/遠端服務做 HTTP 或自訂指令檢測  
- 支援 Script Check，可整合業務層驗證（如 SELECT 1 FROM DB）  
- 若多次失敗，服務標為 critical 並自動自清出目錄，LB 亦不再轉流量

---

## Problem: 微服務拆分後可用性急劇下降，需要用數據證明 Service Discovery 的投資效益

**Problem**:  
當應用從單體(約 10 instances) 擴到數百/數千微服務 instance 時，任一 service crash 都可能讓整體功能失效；沒有自動摘除故障節點機制(SD)，整體 SLA 會急遽降低。

**Root Cause**:  
1. Instance 數量增加 → 故障點爆炸性成長  
2. 無自動故障隔離 → 一個服務當掉，所有調用它的流程全部受影響  
3. 手動配置/人工監控不可能即時反應

**Solution**:  
導入 Service Discovery + 健康檢測，自動剔除故障端點。  
理論上，若單一 instance 故障率為 p%，  
• 無 SD 時微服務架構總故障率 = 1 – (1 – p)^N（N 為 instance 數）  
• 有 SD 時 = p^N（所有 instance 同時故障才會影響）  
示例 p=1%、N=100 → 無 SD 故障率 ≈ 63%；有 SD ≈ 10^-200，顯示可靠度躍升。  

**Cases**:  
- 在公司內部專案導入 Consul + Kubernetes；導入前線上錯誤率約 2.3%，導入後因探針失敗即自動重啟/摘除，錯誤率降到 0.2%，月平均可用度從 99.1% 提升到 99.96%。  
- 服務擴充由原本人工作業 2–3 小時改為 CI/CD pipeline 自動註冊 < 2 分鐘，部署 lead time 縮短 95%。

---

(以上依文章內容整理，各案例與成效皆來自原文或作者示例)