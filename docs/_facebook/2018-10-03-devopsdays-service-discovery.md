---
date: 2018-10-03
datetime: 2018-10-03T00:19:38+08:00
timestamp_utc: 1538497178
title: "DevOpsDays 2018 微服務基礎建設 Service Discovery 演講"
---

這次我在 DevOpsDays Taipei 2018 講的場次，影片已經出來了!
不論你當天有沒有來聽，都歡迎留言給我意見 :)

附上這個 Session 的相關資源:

1. 大會共筆: https://hackmd.io/s/r1RYD2tvQ
2. 投影片: https://www.slideshare.net/chickenwu/service-discovery-andrew-wu

---
微服務的基礎建設 - Service Discovery

微服務架構下，講求動態擴充與自主管理。傳統的 IT 管理方式不再適合微服務的系統架構了。
Service Discovery 視為服務架構的關鍵基礎建設之一。
* 如何知道其他的服務實際的 IP 與 PORT 等資訊？即使服務的數量不斷動態的調整也不受影響？

* 當你有更動態的需求 (例如特定客戶要有更高的服務水準保證)，一般的 Load Balancer 或是 API Gateway 無法滿足時，你該怎麼辦？

* 當這些上百個 instance 彼此的流量已經大過單一 Load Balance 或是 API Gateway 能夠負擔的程度時，你該如何將集中式的通訊方式改為服務網格 (service mesh) 的模式？？

這些問題，只要你能靈活運用 service discovery 的機制妥善管理你的服務群, 就能彈指之間就辦到。這個 session 會以 HashiCorp 的 Consul，搭配 .NET 的應用程式為案例，說明如何妥善運用 service discovery 來解決這些問題。
