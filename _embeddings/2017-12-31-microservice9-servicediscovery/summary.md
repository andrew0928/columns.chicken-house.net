# 微服務基礎建設 - Service Discovery

## 摘要提示
- 服務發現: 微服務能否正常協作的靈魂，解決「找到服務」與「確認健康」兩大核心問題。  
- 三大機制: Register、Query、Healthy Check 組成所有 Service Discovery 的基本流程。  
- DNS/DHCP 類比: 以熟悉的網路例子說明服務註冊、查詢與存活偵測的概念。  
- 登錄模式: 自我註冊(Self-Registration) 與 第三方註冊(Third-Party Registration)。  
- Client-Side Pattern: 由呼叫端負責查詢與負載平衡，彈性大但具侵入性。  
- Netflix Eureka: 典型 Client-Side 實作，搭配 Ribbon 提供客製化負載演算法。  
- Consul: 整合 Service Discovery、Health Check、DNS 介面與 KV Store 的新興解法。  
- Server-Side Pattern: 以 Registry-Aware Load Balancer 代管流量，對應用程式透明。  
- 雲端與容器實例: Azure/AWS Load Balancer 與 Docker 內建 DNS 展現 Server-Side 思維。  
- 效益評估: 有無 Service Discovery 的 SLA 差距懸殊，是微服務落地的首要關鍵。  

## 全文重點
微服務天生是分散式系統，最大挑戰之一在於「如何在龐大且動態的服務叢集中，快速而正確地找到可用節點」。Service Discovery 透過「註冊、查詢、健康檢查」三步驟維護一份即時且可靠的服務清單，使跨服務呼叫不必再硬寫 IP 或端口。傳統 DNS/DHCP 模式雖能示範概念，卻因 TTL、健康檢測與負載能力不足而無法滿足秒級彈性伸縮的需求，遂衍生多種實作與模式。

在註冊層面，可由服務自己回報心跳(Self-Registration)，或交由外部探測器(Third-Party Registration)維護精度。調用層面則分為兩大流派：Client-Side Discovery 將 Registry-Aware 客戶端程式庫嵌入服務，常見於 Netflix Eureka + Ribbon；優點是演算法自由、效能最佳，但更新與語言相依性高。另一派為 Server-Side Discovery，以與 Registry 整合的 Load Balancer 代管路由，應用端僅需呼叫固定入口，典型如 AWS ELB、Azure LB，或在容器世界中的 Docker Routing Mesh、Kubernetes Service。此模型部屬容易、對應用零侵入，惟多一層轉送帶來延遲與集中化風險。

Consul 則整合 Service Discovery、Health Check、DNS 介面與 KV Store，同時支援多資料中心，降低導入門檻並兼顧傳統系統整合。文章最後以簡化的 SLA 計算說明：若沒有 Service Discovery，服務數量增加將大幅放大故障機率；反之，只要任何一個實例仍存活且被正確路由，整體可用度可指數級提升。微服務成功關鍵在治理，Service Discovery 是第一道門檻，後續還需配合 CI/CD、測試、監控等完整工程能力，才能真正釋放微服務的彈性與韌性。

## 段落重點
### Service Discovery Concepts
說明 Service Discovery 的目的與三大基本動作(Register、Query、Healthy Check)，並以 DHCP + DNS 的日常案例對映微服務情境，強調在高速變動的容器／雲端環境中，單靠傳統 DNS 已不足以支撐秒級伸縮與健康感知。  

### Service Registration Pattern(s)
探討如何維持「正確的服務清單」：  
1. 自我註冊：服務自行向 Registry 報到並送心跳。  
2. 第三方註冊：外部程式定期探測服務狀態並更新 Registry。  
兩者可混合使用以提高清單精度，避免僵屍節點或假陽性。  

### The Client-Side Discovery Pattern
由呼叫端內嵌 Registry-Aware Client(如 Ribbon)完成查詢、負載與容錯，具高彈性與效能，並易於實現點對點網狀拓撲(Service Mesh)。缺點是侵入式、更新須重編譯，且與特定 Registry 耦合。  

### Netflix Eureka 與 Consul 案例
Eureka + Ribbon 展示成熟的 Client-Side 解法，已於 Netflix 大規模驗證。Consul 則進一步整合 DNS 介面、KV Store、跨資料中心與豐富健康檢查，降低導入門檻並兼容舊系統，是新世代熱門方案。  

### The Server-Side Discovery Pattern
把查詢與負載邏輯下放至獨立的 Registry-Aware Load Balancer，由其統一轉送流量，對應用程式完全透明。優點是零侵入、語言無關，缺點為多一跳延遲、集中化瓶頸與額外維運成本。  

### 雲端與容器實例
AWS ELB、Azure Load Balancer 天生與各家雲端 Registry 整合，開箱即用；Docker 利用內建 DNS + Overlay Network 實現 Container 級 Service Discovery，Swarm 的 Routing Mesh 與 Kubernetes Service 亦屬 Server-Side 思維，可透過反向代理(Nginx)或 Ingress Controller 暴露外部流量。  

### 效益與結論
以簡化機率模型比較有無 Service Discovery 時的應用故障率，可見在服務數量級距從 10 到 100 時差距呈指數成長。Service Discovery 是微服務落地的首要基礎設施，必須與 DevOps、CI/CD、測試、監控等整體工程能力並行，才能真正獲得高可用、易擴充與快速迭代的效益。