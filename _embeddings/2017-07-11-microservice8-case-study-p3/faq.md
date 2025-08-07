# 架構師觀點 - 轉移到微服務架構的經驗分享 (Part 3)

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 微服務架構必備的基礎建設有哪些？
API Gateway、Service Discovery、Communication／Event-Driven System（通常以 Message Queue／Bus 實作）以及集中化 Log 管理解決方案，這四者被視為微服務運行的核心基礎設施。

## Q: 為什麼不建議新創團隊一開始就直接上微服務？
微服務需要昂貴且複雜的基礎建設與維運能力（快速佈署、監控、故障處理等）。規模尚小時，這些成本與複雜度往往得不償失；先從單體式架構持續重構、待瓶頸出現再逐步切割，通常較符合效益。

## Q: 導入微服務前必須具備哪些前置條件？
1. 團隊流程：持續整合、持續佈署、監控等 DevOps 能力。  
2. 系統／環境：可靠的網路、運算與儲存資源，以及能支援上列四大基礎設施的配置與維運能力。

## Q: API Gateway 在微服務中負責什麼？
它位於客戶端與內部服務之間，負責 API 路由、聚合、多版本轉換、快取、認證與安全控管。透過一次呼叫即可整合多個後端服務，提高效率並隔離內部細節。

## Q: Service Discovery 解決的核心問題是什麼？
動態註冊／取消註冊服務，維護可用節點清單，提供健康檢查與組態管理，讓其他服務或負載平衡器能即時找到正確的服務端點，並避開異常節點。

## Q: 為何在微服務間強調使用 Message Queue 或 Message Bus？
Message Queue 可同時支援同步與非同步通訊、Pub/Sub 與事件驅動模式，將資料流複雜度從程式碼抽離，提升可靠度（儲存後轉送、可離線重送）與水平擴充能力，並簡化 N×M 類型的直接呼叫關係。

## Q: 微服務架構下如何確保跨服務交易的一致性？
常見做法是配合可靠的 Message Broker 與分散式交易模式（如 Two-Phase Commit, 2PC）：先以事件通知所有相關服務預留資源，全部確認後再正式提交；若任何一方失敗或逾時，則統一回滾或取消交易。

## Q: 把認證邏輯集中到 API Gateway 有什麼好處？
可避免每個服務各自實作驗證邏輯，降低 N×(N-1) 的授權組合數，並集中紀錄與管理認證失敗或異常，讓內部服務只需信任來自 Gateway 的憑證即可。

## Q: 若沒有穩固的基礎建設就貿然微服務化會發生什麼事？
服務雖然被切小，但整體複雜度轉移到服務間互動；沒有成熟的 API Gateway、Service Discovery、訊息系統與 Log 管理支撐，系統將難以監控、部署、排障而失去微服務應有的效益。

## Q: 有哪些常見的開源或雲端工具可用於上述基礎建設？
• API Gateway／API Management：Kong、Azure API Management  
• Service Discovery：etcd、ZooKeeper、Consul、Microphone (.NET)  
• Message Queue／Bus：RabbitMQ、Kafka；需求較簡單時可用 Redis Queue，Windows 環境亦可考慮 MSMQ。