# 微服務基礎建設 - Service Discovery

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 什麼是 Service Discovery？它在微服務架構中要解決什麼問題？
Service Discovery 是一套讓服務「自動被發現、被定位並確認健康狀態」的基礎建設。當系統被拆分成大量微服務且動態擴縮時，最大的挑戰就是「我要呼叫的服務在哪？它現在能正常提供服務嗎？」Service Discovery 透過統一的註冊、查詢與健康檢查機制，讓所有服務隨時都能找到彼此並在故障時快速隔離，因而被稱為微服務架構的靈魂。

## Q: 一套完整的 Service Discovery 機制通常包含哪三個核心動作？
1. Register：服務啟動時向 registry 登記自己的存在。  
2. Query：其他服務透過 registry 查詢可用的服務位置與相關資訊。  
3. Healthy Check：持續回報或被探測以確認服務是否仍健康，並於失效時自動從清單移除。

## Q: 為什麼單用傳統 DNS + DHCP 無法滿足微服務下的服務發現需求？
DNS 在微服務場景有四大限制：  
1. 記錄快取 (TTL) 粒度只到分鐘/小時，無法即時反映秒級的動態擴縮。  
2. 缺乏標準化健康檢查，死節點無法自動剔除。  
3. 只支援簡單的 round-robin，無法依負載做精準流量分配。  
4. 只能回傳位址，由 Client 自行挑節點，無法代替客戶端做轉送或路由。

## Q: Service Registration 有哪兩種常見模式？差異是什麼？
1. Self-Registration：服務自己向 registry 註冊並傳送 heartbeat；實作簡單但完全倚賴服務本身回報。  
2. Third-Party Registration：改由外部探針或 Sidecar 主動健康檢查並寫入/更新 registry；可避免「服務已死仍回報心跳」的誤判，清單更精準。

## Q: 什麼是 Client-Side Discovery Pattern？有哪些優缺點？
Client-Side Pattern 由「Registry-aware HTTP Client」在呼叫前直接向 registry 查詢所有可用節點，並在 Client 端自行負載平衡。  
優點：  
• 可自訂最符合業務需求的負載演算法。  
• 邏輯在程式內，效率高、除錯容易。  
缺點：  
• 屬侵入式程式碼，更新需重編譯與重新部署。  
• 服務將與特定 registry SDK 綁定，降低技術獨立性。

## Q: 什麼是 Server-Side Discovery Pattern？有哪些優缺點？
Server-Side Pattern 由一層 registry-aware Load Balancer/Proxy 代替 Client 查詢 registry 並轉送請求。  
優點：  
• 對應用透明，Client 不需嵌入任何 SDK。  
• 更新與規則調整集中於 Load Balancer，維運簡單。  
缺點：  
• 形成額外轉送路徑，增加延遲與單點故障風險。  
• 流量集中可能成為效能瓶頸。

## Q: Netflix Eureka / Ribbon 採用哪種服務發現模式？特色是什麼？
Eureka 提供服務註冊中心；Ribbon 則是與之整合的 Client-Side IPC Library。兩者組合屬於 Client-Side Discovery Pattern，讓開發者可以在程式內自訂負載平衡、失效轉移等邏輯，並已在 Netflix 大量雲端場景中實戰驗證。

## Q: Consul 為何受到許多團隊青睞？它除了服務發現還提供哪些功能？
Consul 內建：  
1. Service Discovery：支援 HTTP 及 DNS 介面，方便與舊系統共存。  
2. Health Check：可用 HTTP、TCP 或自訂 Script 定期探測。  
3. KV Store：集中式設定管理、Feature Flag、協調選主等用途。  
4. 多資料中心：原生支援跨 DC 的服務註冊與查詢。  
部署簡單、整合度高，是近年常見的輕量化 Service Discovery 解決方案。

## Q: 使用 Service Discovery 對系統可靠度有多大幫助？
在沒有 Service Discovery 的情況下，任何一個 Instance 故障都可能影響整體；若每個節點故障率為 1%，當微服務總數增加到 100 個時，整體故障率可高達 63%。  
引入 Service Discovery 後，只有「全部節點同時故障」才會影響整體，可將故障率降到 10⁻²⁰⁰ 等級，顯著提升整體 SLA。

## Q: Docker / Kubernetes 等容器平台本身提供了哪些服務發現能力？
Docker 透過內建 DNS (預設 127.0.0.11) 自動將每個 Service Name 映射到動態 IP；在 Swarm 或 Kubernetes 中，更進一步提供 Ingress/Routing Mesh，將 Reverse Proxy、負載平衡與健康檢查整合為平台內建的 Server-Side Discovery。

## Q: 為什麼作者將「Docker 內部 DNS + Nginx Reverse Proxy」歸類為 Server-Side Pattern？
在該案例中，外部流量統一經由 Nginx 反向代理，再由 Nginx 依據 Docker 內建 DNS 的即時資訊把請求導向正確的容器。服務發現與路由邏輯全部集中在代理層，對應用程式透明，符合 Server-Side Discovery Pattern 的定義。