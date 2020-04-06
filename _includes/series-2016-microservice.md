{% unless include.mode == "no_header" %}
# 前言: 微服務架構 系列文章導讀
-----
{% endunless %}




Microservices, 一個很龐大的主題，我分成四大部分陸續寫下去.. 預計至少會有10篇文章以上吧~
目前擬定的大綱如下，再前面標示 (計畫) ，就代表這篇的內容還沒生出來... 請大家耐心等待的意思:
  
1. **微服務架構(概念說明)**
  - [微服務架構 #1](/2016/09/15/microservice-case-study-01/), WHY Microservices? 2016/09/15
  - [微服務架構 #2](/2016/10/03/microservice2/), 按照架構，重構系統; 2016/10/03
1. **實做基礎技術: API & SDK Design**
  - [API & SDK Design #1](/2016/10/10/microservice3/) 資料分頁的處理方式; 2016/10/10
  - [API & SDK Design #2](/2016/10/23/microservice4/) 設計專屬的 SDK; 2016/10/23
  - [API & SDK Design #3](/2016/10/31/microservice5/) API 的向前相容機制; 2016/10/31
  - [API & SDK Design #4](/2016/11/27/microservice6/) API 上線前的準備 - Swagger + Azure API Apps; 2016/11/27
  - [API & SDK Design #5](/2016/12/01/microservice7-apitoken/) 如何強化微服務的安全性? API Token / JWT 的應用; 2016/12/01
  - (計畫) API & SDK Design #6, case study, API 異動 & SDK 的最佳化
1. **架構師觀點 - 轉移到微服務架構的經驗分享**
  - [Part #1](/2017/04/15/microservice8-case-study/) 改變架構的動機; 2017/05/09
  - [Part #2](/2017/05/20/microservice8-case-study-p2/) 實際改變的架構案例; 2017/05/20
  - (計畫) [Part #3] 轉移到微服務的必經之路 - 資料庫的設計與規劃;
1. **基礎建設 - 建立微服務的執行環境**
  - [Part #1](/2017/07/11/microservice8-case-study-p3/) 實際部署的考量: 微服務基礎建設; 2017/07/11
  - [Part #2](/2017/12/31/microservice9-servicediscovery/) 微服務基礎建設 - Service Discovery; 2017/12/31
  - [Part #3](/2018/06/10/microservice10-throttle/) 微服務基礎建設 - 服務負載的控制; 2018/06/10
  - [Part #4](/2018/12/12/microservice11-lineup/) 微服務基礎建設 - 排隊機制設計; 2018/12/12
  - [Part #5](/2019/01/01/microservice12-mqrpc/) 可靠的微服務通訊 - Message Queue Based RPC; 2019/01/01
  - [Part #6](/2020/02/09/process-pool/) 非同步任務的處理機制 - Process Pool; 2020/02/15
  - (計畫) 微服務基礎建設 - Service Mesh;
  - (計畫) 微服務基礎建設 - Circuit Breaker;
  - (計畫) 微服務基礎建設 - Log Tracking & Auth;
  - (計畫) 微服務基礎建設 - 版控, CI/CD, 容器化部署;
1. **案例實作 - IP 查詢服務的開發與設計**
  - [容器化的微服務開發 #1](/2017/05/28/aspnet-msa-labs1/) 架構與開發範例; 2017/05/28
  - [容器化的微服務開發 #2](/2018/05/12/msa-labs2-selfhost/) IIS or Self Host ? 2018/05/12
  - (計畫) [容器化的微服務開發 #3] 實際部署案例 - .NET + Consul; 2018/??/??
1. **建構微服務開發團隊**
  - [架構面試題 #1](/2018/03/25/interview01-transaction/) 線上交易的正確性; 2018/03/25
  - [架構面試題 #2](/2018/04/01/interview02-stream-statistic/) 連續資料的統計方式; 2018/04/01
  - [架構面試題 #3](/2019/06/01/nested-query/) RDBMS 處理樹狀結構的技巧; 2019/06/01
  - [架構面試題 #4](/2020/03/10/interview-abstraction/) 抽象化思考；折扣規則的設計機制; 2020/04/02

{% unless include.mode == "no_header" %}
-----
{% endunless %}
