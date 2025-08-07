# DevOpsDays 專刊: Service Discovery, 微服務架構的基礎建設

## 摘要提示
- DevOps定位: 以開發者視角切入，說明 Service Discovery 如何連結 Dev 與 Ops。
- Service Discovery定義: 以動態註冊中心取代靜態 Config 與 DNS/LB，解決服務數量暴增與異動頻繁的痛點。
- Client-Side Pattern: 由呼叫端直接向 Registry 查詢服務實例，提升彈性並避免單點瓶頸。
- Health Check: 透過註冊中心內建的健康檢查機制，確保調用端只連到可用實例。
- Consul案例: 以 Consul 為例示範 Registry、Health Check、Key/Value 與 Tag 運用方式。
- SLA分級: 解析「同功能不同 SLA」的雲端商業模式，示範如何用 Tag 與過濾策略落實。
- 架構師角色: 協助 Dev 與 Ops 選型、整合與落地，避免各自為政造成技術債。
- Service Mesh演進: Registry 完備後，才能進一步導入 Sidecar/Service Mesh 以強化流量治理。
- 雲端限制: 單靠雲供應商 LB 難以支援進階路由與等級區分，須引入自建 Discovery。
- DevOps思維: 開發團隊必須理解運維視角，才能打造可延展、可治理的微服務平台。

## 全文重點
本文為 DevOpsDays Taipei 2018 的文字版，作者以開發者觀點重新審視 Service Discovery 在微服務架構中的關鍵地位。傳統企業將開發與運維切割，並以 DNS + Load Balancer 或靜態組態檔管理服務，然而在微服務數量暴增與容器化盛行的今日，這種做法已成瓶頸：  
1. 服務實體（instance）動態增減，靜態 URL 難以追蹤。  
2. 呼叫端無法即時得知服務健康狀態，導致逾時或錯誤蔓延。  
3. 進階需求如多區域、分級 SLA、流量分割等皆難以落實。  

Service Discovery 透過「Service Registry + Health Check」機制，將所有服務的位址、屬性與狀態集中管理，再配合 Client-Side Discovery Pattern，使呼叫端可在 runtime 根據情境過濾與挑選實例，並可進一步透過 Tag 做版本、區域或等級切分，為 Service Mesh 的流量治理奠定基礎。作者以 Consul 為範例說明 Registry 建置流程，並強調架構師需同時理解 Dev 與 Ops 的需求，在技術選型、邊界劃分及演進路徑上給予團隊指引。

進入進階場景，文章以「依客戶等級提供不同 SLA」為案例：假設後端共 100 個實例，其中 60 個專供 Plus 客戶，40 個供 Free/Standard 客戶。若只靠 DNS 或傳統 LB，勢必得維護多組網域與負載器且難以與身份驗證聯動；而以 Service Discovery 搭配 Tag 過濾即可輕鬆實現，同時仍保有動態伸縮能力。作者點明，類似需求無論是多雲、多區或藍綠部署，本質皆可透過同一組 Registry 與 Sidecar／Service Mesh 組合來解決，這才是 DevOps 整合與 Cloud Native 架構真正的價值。

## 段落重點
### 本文開始
作者說明投稿 DevOpsDays 的動機與主軸：以開發者角度切入，闡述 Service Discovery 如何作為 Dev 與 Ops 的交會點。在傳統企業中，運維常強調對開發透明，反而阻礙了雲原生創新；DevOps 精神要求雙方更緊密協作，架構師的職責就是在技術選型與落地方法上搭橋。文章將分 Basic、Advanced、Next 三階段講述基礎觀念、實務案例與未來演進。

### BASIC: Service Discovery for Developers
先回顧團隊常見的服務管理手法：DNS + LB 與 Config 檔。當服務種類與實例數高速成長，這兩種方式將面臨三大問題：健康檢查不足、路由粒度不夠以及 LB 單點瓶頸。Service Discovery 透過 Registry、Health Check 與 Tag 讓服務資訊動態化，開發者可在程式內直接查詢並決策，免去手動維護 Config；而運維則可集中控管並暴露必要細節，達成雙贏。作者提到的 Client-Side Pattern 成為後續 Service Mesh 的基石。

### Advanced Scenario
在進階情境中，單靠雲端 LB 或傳統運維手段無法解的問題便浮現，如多 SLA、A/B 測試或多區路由。這些需求必須讓應用層能理解用戶屬性並即時選擇後端資源，因此 Dev 與 Ops 的整合不可或缺。作者強調，選對可程式化的 Service Discovery 平台，才能讓開發者在程式邏輯內依 Tag 與健康狀態做動態決策，運維再透過相同機制調整基礎設施，最終導向以 Sidecar/Service Mesh 做細粒度流量治理。

### 案例: 提供不同 SLA 給不同層級的客戶
以 Slack 收費層級為例，功能相似但 SLA、效能及部署隔離不同。提高 SLA 的方法無非是使用更可靠的基礎設施或投入更多備援資源；然而如何保證 Plus 用戶的流量只落到高規硬體或較多實例？若用 DNS/LB 得維護多組網域且在登入後再轉發，代價高且流程複雜。改用 Service Discovery，只要在 Registry 為實例加上「PLUS_ONLY」等 Tag，呼叫端根據使用者身分過濾即可選到對應資源，開發與運維成本大幅降低，也為日後動態擴縮與版本灰度發布鋪路。

