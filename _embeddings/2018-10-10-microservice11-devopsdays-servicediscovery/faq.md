# DevOpsDays 專刊: Service Discovery, 微服務架構的基礎建設

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 微服務架構落地時，開發與運維首先會碰到的最大技術難題是什麼？
服務發現 (Service Discovery)。  
當服務種類與 instance 數量急遽增加時，如何讓每一個服務都能被快速、正確且健康地尋址，是所有微服務團隊的第一道門檻。

## Q: Service Discovery 應該歸屬於 Infra/Ops 還是 Service/Dev 的職責？
都不是，它是 Dev 與 Ops 交會的「中介層服務」。  
兩邊的人都必須理解其原理與用法，才能把大量服務的生命週期管理與應用程式的商業邏輯真正整合起來。

## Q: 團隊普遍採用哪些傳統方式來定位服務？各自有哪些侷限？
1. DNS + Load Balancer  
   ‑ 無法感知單一 instance 健康狀態，亦難做更細緻的流量分配；LB 本身還可能成為效能瓶頸或單點失敗。  
2. 靜態組態檔 (Config)  
   ‑ 內容固定，服務異動或故障時無法即時更新，常導致長時間等待或例外拋出，影響整體可用度。

## Q: 如果呼叫端想「有系統地」確認服務是否可用，取代靜態 config 應該怎麼做？
導入具有健康檢查 (Health Check) 的 Service Registry。  
Client 在每次呼叫前先向 Registry 取得當下仍通過健康檢查的 instance 清單，再依策略挑選目標，便可避免對失效服務的無謂等待。

## Q: 如何讓同一支服務依「客戶等級」或「區域」做更精準的流量分配？
在 Service Registry 為各 instance 加上 Metadata/Tags (例如 PLUS_ONLY、FREE、APAC、EU 等)。  
Client 於查詢 Registry 時帶入 Request Context (使用者方案、區域等) 去過濾或排序 instance，便能動態取得符合條件的節點，而不必再為每種組合建立額外 URL 或 LB。

## Q: 要為不同客戶階級提供不同 SLA (例如 99.9% vs 99.99%)，Service Discovery 可以怎麼幫忙？
將高 SLA 需求的 instance 以標籤區隔，例如只將 60 個節點標成 PLUS_ONLY，並在客戶請求時於 Client 端過濾。  
如此可為高級客戶保留更多備援資源，提高整體可用度，而開發端無須改變商業邏輯，運維端也免去額外維護多組 LB 或網域的負擔。

## Q: 為什麼「運維對開發完全透明」的傳統做法違背 DevOps 精神？
許多雲原生功能（動態伸縮、細粒度流量治理、service mesh 等）都必須讓應用程式與基礎建設深度協作；若開發人員不了解運維層面的行為與限制，就難以實現這些能力。

## Q: 在邁向 Sidecar / Service Mesh 之前，團隊必須先打好的基礎是什麼？
一套可靠的 Service Registry 與完整的健康檢查機制。  
只有先解決動態尋址與服務狀態感知，才能進一步把流量控制、熔斷、觀測等功能下放到 sidecar 乃至 service mesh。

## Q: 近年 API Gateway 領域的領導者為何宣稱「傳統 API Management 已死」？
隨著微服務與 Service Discovery 普及，服務節點與路由資訊高度動態，傳統以靜態配置為核心的 API Management 已無法因應；必須轉向能即時整合 Registry、支援 service mesh 的新式架構。

## Q: 架構師在 Service Discovery 專案中的角色與價值是什麼？
架構師需洞悉 Dev 與 Ops 雙方需求，做出正確的技術選型，並在必要時帶領團隊深入原理、甚至自行實作。  
唯有如此，才能在可靠度、擴充性與交付速度之間取得最佳平衡，真正落實 DevOps 文化。