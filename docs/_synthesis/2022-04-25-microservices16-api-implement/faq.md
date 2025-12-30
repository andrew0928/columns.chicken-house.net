---
layout: synthesis
title: "微服務架構 - 從狀態圖來驅動 API 的實作範例"
synthesis_type: faq
source_post: /2022/04/25/microservices16-api-implement/
redirect_from:
  - /2022/04/25/microservices16-api-implement/faq/
---

# 微服務架構 - 從狀態圖來驅動 API 的實作範例

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是「用狀態機驅動的 API 設計」？
- A簡: 以有限狀態機描述資料生命週期與行為，將狀態、動作、授權與轉移規則化，使 API 設計、實作與驗證有一致基準。
- A詳: 狀態機驅動的 API 設計，是先以有限狀態機（FSM）描述實體的狀態、可執行動作與狀態轉移，再據此設計 API 規格。FSM 的點表示狀態，邊表示動作與轉移，邊可附加授權條件（例如 USER/STAFF）。此法能在設計期整合存取控制，避免規格與實作偏差，並用同一張圖檢核安全與一致性。對應到會員服務，即用 FSM 管控註冊、啟用、鎖定、刪除等行為，讓 API 呼叫必須符合狀態與身分，否則拒絕。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, B-Q1, B-Q2

A-Q2: 什麼是有限狀態機（FSM），在會員服務怎麼用？
- A簡: FSM 是以離散狀態與轉移定義系統行為。會員服務用 FSM 管控帳號狀態與允許動作。
- A詳: 有限狀態機（Finite State Machine）以有限集合的狀態、觸發動作與轉移規則描述系統。會員服務中，成員（帳號）是實體，每筆資料具有 START、CREATED、ACTIVATED、DEACTIVED、ARCHIVED、END 等狀態。每個動作（如 register、activate、lock）在特定初始狀態才允許執行，並產生既定終止狀態，動作同時標註可執行的身分（USER/STAFF）。這讓服務能在呼叫時據狀態與身分判斷放行或拒絕。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, B-Q1, B-Q7

A-Q3: 為什麼微服務 API 要先設計（Spec First）再實作？
- A簡: 先以 FSM 收斂規格，降低誤解與破壞性改動，並能平行開發與測試，提升交付品質。
- A詳: Spec First 能在實作前以狀態機與合約（Contracts）確立 API 邊界、狀態轉移、安全模型與錯誤語意，避免「先做再補」導致破壞性改版。以單元測試驗證案例可反向校正規格合理性。當規格穩固，Core 與 WebAPI、前台與後台團隊可平行作業，降低溝通成本與返工風險，兼顧擴充性與相容性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q22, B-Q13, B-Q22

A-Q4: 認證、授權、存取控制的定義與差異？
- A簡: 認證證明「你是誰」，授權定義「你可做什麼」，存取控制規範「此功能需哪些權限」。
- A詳: 認證（Authentication）確認呼叫者身分，如 JWT 內的 subject。授權（Authorization）決定其可執行的動作或可存取的資源，如 USER/STAFF 身分或 scope。存取控制（Access Control）是功能側的要求，描述「執行某動作需具備哪些授權」，在文中以 FSM 的邊標註身份類型實現。三者結合形成一致的安全模型，並在 Middleware 與 Core 層落地檢查。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, B-Q24, B-Q25

A-Q5: 什麼是 MemberServiceToken？
- A簡: 封裝 JWT 內容的身分物件，包含 IdentityType（USER/STAFF）與 IdentityName 等宣告。
- A詳: MemberServiceToken 由 JWT 解析建構，內含 IdentityType（對應授權類型，簡化為 USER/STAFF）、IdentityName（誰在呼叫，如 webui 或 andrew）、jti、iat、exp、scope 等欄位。它是所有安全判斷的起點，搭配 FSM 的存取控制，決定 API 能否執行。服務以 DI 採 Scoped 生命週期，保證單一請求期間使用一致 token。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, B-Q5, B-Q14

A-Q6: USER 與 STAFF 的差異是什麼？
- A簡: USER 代表前台使用者，只能操作自身資料；STAFF 代表後台人員，可跨成員執行管理操作。
- A詳: 在簡化權限模型下，IdentityType 僅分 USER 與 STAFF。USER 僅可存取自己資料，能註冊、啟用、變更密碼等；STAFF 代表後台管理身分，可執行鎖定、強制重置密碼、查詢所有會員、匯入等管理動作。FSM 將動作與身份關聯，確保相同 API 對不同 token 有不同能力邊界。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, B-Q14, C-Q7

A-Q7: 會員的核心狀態有哪些？意義為何？
- A簡: 包含 START、CREATED、ACTIVATED、DEACTIVED、ARCHIVED、END，對應生命週期各階段。
- A詳: START 表未建立；CREATED 表已註冊待驗證；ACTIVATED 為啟用可登入；DEACTIVED 為停用/鎖定；ARCHIVED 為軟刪除保存；END 表硬刪除終態。各狀態允許的動作不同，FSM 以此約束流程，如 CREATED 可 activate、ACTIVATED 可 lock/soft-delete、DEACTIVED 可 unlock 或重設密碼等。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q16, C-Q6

A-Q8: 狀態與動作（action）之間的關係？
- A簡: 狀態是點，動作是邊，邊決定從初始狀態到終止狀態的合法轉移與授權。
- A詳: FSM 以圖表述，節點為狀態，箭頭為動作與轉移。每條邊標註 actionName、initState、finalState、允許的身份類型（如 USER/STAFF）。API 呼叫先對照當前狀態與 token 身份，若無符合邊則拒絕；若符合則執行商業邏輯並更新至 finalState。此設計將業務流程與安全規則融合在同一模型。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, B-Q24, C-Q5

A-Q9: 為何 API 要「最小開放面積」？
- A簡: 降低組合攻擊面、複雜度與維運風險，避免重疊 API 與不必要入口，聚焦核心能力。
- A詳: 面向內外部系統的 API，開放即風險。最小開放面積策略強調合併相近需求、由客端組合、以本地儲存補位，非必要不增新端點。除非涉分散式交易或批次性能需求才特設。能降低誤用、提高一致性與安全性，並將進階需求導向 Workflow 或 Client 邏輯處理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q23, A-Q11, A-Q21

A-Q10: 專案分層（Core/Contracts/WebAPI/CLI/Tests）各扮演什麼角色？
- A簡: Contracts 定義合約；Core 實作業務；WebAPI 對外；CLI 批次與工具；Tests 驗證規格與行為。
- A詳: Contracts 提供跨專案介面與模型定義，是相容性與版控核心；Core 實作 domain/service、FSM 與安全整合；WebAPI 僅負責 HTTP 通訊、路由與 Middleware；CLI 提供產生 token、批次匯入等工具；Tests 以單元測試與情境測試確保規格與實作一致。分層使責任清晰、重用性高。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q11, B-Q12, B-Q22

A-Q11: 為何以「中台／內部 API 視角」設計會員服務？
- A簡: 服務內部系統與團隊，取代直連資料庫，統一流程、安全與資料一致性。
- A詳: 中台視角強調以 domain 能力為核心，不為單一前端畫面設計，而是統一服務內外部（前台/後台/合作夥伴）需求。以服務 API 取代直接 DB 存取，集中安全、日誌、配置與授權，提升一致性與可觀測性，降低各系統直接動資料庫的風險與耦合。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q11, B-Q21

A-Q12: 安全模型在 API 設計中的核心價值？
- A簡: 將身分、授權與存取控制內建於規格，統一檢核，避免規格與實作的安全缺口。
- A詳: 安全模型需在設計期確定，並以可驗證規格呈現。本文將 USER/STAFF 身分與各動作之授權寫進 FSM 的邊；認證則由 JWT token 承載身分資訊；存取控制則由 FSM 決定特定狀態下誰可執行何動作。透過 Middleware 與 Core 檢核，形成不可被繞過的防護網。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, B-Q5, B-Q15

A-Q13: 什麼是 JWT？本文如何使用？
- A簡: JWT 是攜帶宣告的簽章令牌。文中用來封裝身分、時效與授權，供 Middleware 解析驗證。
- A詳: JSON Web Token 以三段（header.payload.signature）組成，支援簽章與驗證。本文用 jose-jwt 建立/驗證 token，payload 包含 iss（身份類型）、sub（呼叫者）、jti、iat、exp 等。WebAPI 由 Authorization: Bearer 取得 token，Middleware 解析為 MemberServiceToken，供 FSM 驗證與授權決策。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, B-Q25, C-Q2

A-Q14: JWT 的 HMAC 與 RSA 有何差異？
- A簡: HMAC 使用對稱金鑰，實作簡單；RSA 使用非對稱金鑰，易於發行與驗證分離。
- A詳: HMAC（如 HS512）簽章與驗證使用同一把金鑰，部署簡單但需妥善保護密鑰。RSA（如 RS256）以私鑰簽章、公鑰驗證，適合跨系統公開驗證、集中發行。本文為簡化示範採 HMAC，生產環境則建議 RSA 並配套金鑰管理與輪替策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q25, C-Q2, D-Q5

A-Q15: FSM 與存取控制（Access Control）如何整合？
- A簡: 將可執行身份標註於轉移邊，執行時以 token 身分與當前狀態比對決定可否放行。
- A詳: 每條狀態轉移邊定義 actionName、initState、finalState、allowIdentityTypes。執行 API 前，Core 以 token.IdentityType 與資料當前狀態比對 FSM；若不存在符合邊則拒絕。此法將「能否執行」從程式邏輯抽離，集中於規格，易於檢核與演進。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q24, C-Q5

A-Q16: SafeChangeState 在架構中的角色是什麼？
- A簡: 封裝狀態變更樣板，統一鎖定、檢核、執行與事件通知，避免重複與競態。
- A詳: SafeChangeState 接受 id、actionName 與委派函式。步驟：鎖定資料；用 FSM 檢核當前狀態與身分；執行傳入的商業邏輯；確認執行後的狀態符合 FSM；持久化；最後發布狀態改變事件。它將橫切關注（鎖定、安全、事件）集中管理，讓各 action 寫更少、行為一致。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q8, D-Q4

A-Q17: 事件驅動（OnStateChanged）在服務中的用途？
- A簡: 當狀態變更時發出事件，支援後續通知、審計、異步處理與跨服務整合。
- A詳: 服務於成功完成狀態變更後，透過 C# event 發出事件，包含動作、起訖狀態與關聯資料。此設計可延伸為以 MQ 發佈，支援多訂閱者（如寄信、稽核、同步索引）。在單體或 PoC 階段用事件委派，進入分散式時切換成 Kafka、RabbitMQ 等更可靠的機制。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, C-Q9, D-Q9

A-Q18: AOP（面向切面）在本案例的意義？
- A簡: 將共通檢查與橫切關注（授權、FSM、日誌）抽離集中處理，減少重複與遺漏。
- A詳: 本文以 Middleware、屬性（MemberServiceAction）與 SafeChangeState 封裝橫切邏輯，在進入 Controller 前完成 token 解析與 FSM 預檢，在 Core 內統一鎖定與事件，使每個 action 的商業邏輯保持精煉。這是 AOP 思維在 .NET 的實踐。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q6, B-Q7

A-Q19: DI 生命週期（Singleton/Scoped）為何這樣選？
- A簡: Repo、FSM 為 Singleton；Token、Service 為 Scoped，以請求為界確保一致性與效能。
- A詳: MemberRepo 與 MemberStateMachine 為系統級資源，適合 Singleton；MemberServiceToken 與 MemberService 與請求安全相關，必須與 Request 綁定（Scoped），確保同一請求的 token 與服務一致，避免身分漂移。此配置兼顧效能與正確性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, C-Q3, D-Q8

A-Q20: 為什麼建議先做 PoC/MVP？
- A簡: 以可運作最小實作驗證設計抽象正確性，降低過度設計與昂貴返工風險。
- A詳: 架構要能落地，PoC/MVP 能在有限範圍驗證設計選型是否能支撐需求，如 FSM 安全模型、Middleware、事件與測試流程。先以 In-memory repository、簡化 JWT 實作，待驗證通過再替換為正式元件，有效掌握風險與投資節奏。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, C-Q10, B-Q22

A-Q21: Spec-first 與過度設計如何拿捏？
- A簡: 規格看得遠、實作做剛好。抽象設計完整，先交付核心路徑與關鍵驗證。
- A詳: 抽象層次以 FSM/Contracts 確保未來擴充空間，但實作階段以最小可行為主（如 In-memory、簡化 JWT），避免一次把所有非關鍵細節做滿。必要性與可替換性高的留在後期替換，如 DB、分散式鎖、MQ。保持界面穩定，逐步深化實作水位。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q22, C-Q10

A-Q22: 什麼是「合約（Contracts）」與相容性管理？
- A簡: 合約是跨專案介面與模型定義。版本變更須維持相容或提供遷移策略。
- A詳: Contracts 封裝 public interface 與資料模型，是跨團隊、跨專案溝通標準。它需嚴格版控，變更採後相容策略（如新增欄位、保留舊介面），或以新版本並行。測試應對齊合約，確保消費者不因更新破壞。這是 API-first 能持續演進的基礎。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q22, D-Q7, A-Q3

A-Q23: 為何以 Domain method 而非 HTTP 視角設計 MemberService？
- A簡: 先以領域動作建模，WebAPI 僅是傳輸外衣，避免耦合通訊細節於業務邏輯。
- A詳: MemberService 以動作（Register、Activate、Lock…）為介面，對應 FSM。HTTP Controller 僅轉入參數並回應標準代碼。此分離讓相同核心可被多種介面（CLI、API、Worker）重用，也更容易測試與替換通訊層，保持清晰邊界。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, C-Q4, C-Q6

A-Q24: Middleware 在安全與 FSM 檢查中的角色？
- A簡: 在 Controller 前解析 token、辨識 action 與 member id，先行進行規則檢查與錯誤映射。
- A詳: Middleware 讀取 Authorization Bearer，建立 MemberServiceToken，從路由與屬性取得 id/action，呼叫 Service 進行 FSM 預檢，異常統一回應（如 403/500）。它讓安全與規則前移，減少 Controller 重複程式碼，並確保不可繞過的檢查點。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q6, D-Q6

A-Q25: 為何「先寫測試」能改善 API 設計？
- A簡: 測試從使用者視角驗證案例，反向校正介面合理性與缺參數、回傳定義等問題。
- A詳: 以測試描述註冊到啟用、密碼錯誤鎖定、後台解鎖等情境，能暴露 API 輸入輸出不完整、錯誤語意不一致等問題。在尚未完整實作時，測試即是「可執行的規格」，驅動設計迭代，提升 API 可用性與穩定性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q13, C-Q6, D-Q8


### Q&A 類別 B: 技術原理類

B-Q1: MemberStateMachine 的資料結構如何設計？
- A簡: 以 List(tuple) 儲存邊，記 action、起訖狀態與允許身分；以 enum 表達狀態節點。
- A詳: 技術原理說明: FSM 以圖實作，節點用 enum MemberState，邊以 List<(actionName, initState?, finalState?, allowTypes[])> 表示。關鍵步驟或流程: 啟動時載入所有合法轉移；查核時以 action+currentState+identityType 篩選邊。核心組件介紹: MemberState、MemberStateMachine（內含 _fsmext 列表）、CanExecute 方法。此結構直觀、易擴充且可序列化。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q2, A-Q8, B-Q2

B-Q2: CanExecute 的執行流程是什麼？
- A簡: 依 action、當前狀態與身份在邊集合查找，找到即允許並回推終止狀態。
- A詳: 原理: 以引數（currentState、actionName、identityType）查詢 FSM 邊集合；若符合條件即可執行。步驟: 1) 取得當前狀態；2) 匹配 actionName；3) 比對 initState 與 allowIdentityTypes；4) 回傳可否與 finalState。核心組件: MemberStateMachine.CanExecute（兩種多載：指定成員與非成員 API）。此方法作為交通警察，前置把關行為合法性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, B-Q7, C-Q5

B-Q3: 為何以 Graph 模型表達 FSM，有何優勢？
- A簡: Graph 將狀態與轉移明確化，易查驗、可視化且能直接對應程式資料結構。
- A詳: 原理: FSM 本質即有向圖。以枚舉列點、清單列邊，符合電腦內部結構。步驟: 用 enum 定義狀態；以 tuple 集合定義所有合法邊；在邏輯中僅從集合查詢。核心組件: enum、tuple、LINQ 查詢。優勢在於：規則集中、可抽換儲存、易產生測試用例與視覺化檢核。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, A-Q1, A-Q8

B-Q4: MemberServiceToken 如何由 JWT 建構？
- A簡: Middleware 取 Authorization Bearer，jose-jwt 驗證簽章，解析 claims 填入 Token 物件。
- A詳: 原理: JWT 包含 header、payload、signature。服務用 jose-jwt 以金鑰驗證 signature。步驟: 1) 取出 Authorization: Bearer；2) 驗簽；3) 解析 iss/sub/jti/iat/exp；4) 建構 MemberServiceToken；5) 以 DI Scoped 保存。核心組件: MemberServiceTokenHelper、jose-jwt、Middleware。此流程確保身分可信且請求期間一致。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, A-Q13, B-Q5

B-Q5: Middleware 解析 Authorization 的機制？
- A簡: 在管線早期攔截請求，解析 Bearer token、抽出路由資訊，並呼叫 FSM 預檢。
- A詳: 原理: ASP.NET Core Middleware 依註冊順序串接。步驟: 1) 讀 header；2) 檢查 "Bearer "；3) 解析 token 建立 MemberServiceToken；4) 取路由 controller/id 與 MemberServiceAction；5) 呼叫 Service 進行 FSM 規則檢查；6) 異常映射為 HTTP 錯誤。核心組件: HttpContext、Endpoint Metadata、DI。確保 Controller 前完成安全與規則把關。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q24, B-Q6, D-Q6

B-Q6: MemberServiceAction 屬性如何協助 FSM 檢查？
- A簡: 以屬性標註端點對應的 actionName，供 Middleware 正確取得欲執行動作。
- A詳: 原理: ASP.NET Core 可從 Endpoint Metadata 讀取自訂屬性。步驟: 1) 在 Controller 方法標記 [MemberServiceAction("activate")]；2) Middleware 於 GetEndpoint() 取得 Metadata；3) 擷取 actionName 供 FSM 檢查。核心組件: Attribute、Endpoint、Middleware。此做法把「操作語意」顯式化，避免依方法命名或路由猜測。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q24, C-Q4, D-Q6

B-Q7: SafeChangeState 的執行流程與組件？
- A簡: 鎖定→再次檢核→執行業務委派→驗證狀態→持久化→發布事件，確保原子性與一致性。
- A詳: 原理: 將狀態變更的通用步驟封裝。步驟: 1) 以 lock 鎖定資料；2) 以 FSM 檢查；3) 執行委派（傳入 Model 副本）；4) 驗證狀態符合 finalState；5) 寫回 Repository；6) 若狀態變更則觸發事件。核心組件: MemberRepo、MemberStateMachine、事件機制。此模板降低重複與 race condition 風險。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q16, B-Q8, D-Q4

B-Q8: 競態條件如何處理？單機 lock 與分散式鎖的差別？
- A簡: 單機以程式鎖保護臨界區；多機需分散式鎖或交易設計避免同時更新。
- A詳: 原理: 并行存取共享狀態會產生競態。步驟: 單機用 C# lock；多機改用分散式鎖（如 Redis Redlock、DB row lock）或以事件/補償交易設計流程。核心組件: 鎖服務、資料庫交易、Idempotency Key。PoC 用 lock 模擬；生產環境需替換為可靠分散式機制。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q7, D-Q10, C-Q10

B-Q9: 樂觀鎖與悲觀鎖如何取捨？
- A簡: 讀多寫少用樂觀鎖（版本號重試）；衝突高或一致性嚴格用悲觀鎖（先鎖後做）。
- A詳: 原理: 樂觀鎖假設低衝突，提交時比對版本；悲觀鎖在開始即鎖定資源。步驟: 樂觀鎖需版本欄位與重試；悲觀鎖需鎖資源並考量死鎖與可用性。核心組件: RowVersion/ETag、DB 鎖模式、分散式鎖。會員狀態變更可先以悲觀鎖確保一致，再評估切換。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q8, D-Q4, C-Q10

B-Q10: 事件通知機制如何設計（C# event vs MQ）？
- A簡: 內部以 C# event 實作；跨服務以消息佇列（Kafka/RabbitMQ）發布/訂閱確保可靠傳遞。
- A詳: 原理: 事件驅動促進解耦與擴展。步驟: 1) 內部先以 event 撰寫；2) 抽象事件介面；3) 切換為 MQ 實作並保證至少一次傳遞；4) 增加重試與死信隊列。核心組件: Event Publisher、MQ、消費者（Worker）。狀態變更事件可觸發寄信、同步索引與審計。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q17, C-Q9, D-Q9

B-Q11: WebAPI Controller 如何對應 Core 服務？
- A簡: Controller 僅負責路由與參數繫結，呼叫 MemberService，回應標準 HTTP 狀態。
- A詳: 原理: 通訊層與業務層分離。步驟: 1) DI 注入 MemberService；2) 映射路由與 [FromForm]/路由參數；3) 呼叫對應方法（如 Activate）；4) 依結果回傳 200/403/500。核心組件: ASP.NET Core Controller、Model Binding、DI。此分層提升可測試性與重用性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q23, C-Q4, B-Q12

B-Q12: DI 注入與生命週期管理如何設計？
- A簡: 以 AddSingleton 註冊 Repo/FSM；AddScoped 註冊 Token/Service，確保一致與效能。
- A詳: 原理: 依資源特性決定生命週期。步驟: 1) Startup.ConfigureServices 註冊物件；2) Middleware 透過 DI 取得 Token/Service；3) Controller 直接注入使用。核心組件: IServiceCollection、Scoped/Singleton、DI 容器。正確生命週期避免競態與重複建構開銷。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q19, C-Q3, D-Q8

B-Q13: 單元測試如何驅動 API 設計（TDD 思路）？
- A簡: 以情境測試描述端到端流程，迫使介面回傳與錯誤語意清晰可用。
- A詳: 原理: 測試即規格。步驟: 1) 先寫情境（註冊→啟用→登入→鎖定→客服協助）；2) 撰寫最少實作通過測試；3) 重構抽象出樣板；4) 擴大測試覆蓋與邊界案例。核心組件: Unit Test Framework、Mock Repo、固定 Token。讓規格在代碼中可執行與可驗證。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q25, C-Q6, D-Q8

B-Q14: 前台/後台 token 如何影響可執行的 action？
- A簡: token.IdentityType（USER/STAFF）與 FSM 邊 allowIdentityTypes 比對，決定允不允許。
- A詳: 原理: 授權與存取控制在 FSM 交會。步驟: 1) Middleware 建立 Token；2) 解析 action 與 member id；3) FSM 以 identityType 查詢符合邊；4) 無符合拒絕（403/500）；5) 符合則進入 Service。核心組件: Token、FSM、Middleware。此法讓同一端點對不同身分呈現不同能力。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, A-Q15, C-Q7

B-Q15: FSM/Middleware 如何對應 HTTP 錯誤碼？
- A簡: 授權不足回 403；規則檢核失敗或服務內部錯誤回 500；可細化成標準 Problem+JSON。
- A詳: 原理: 安全與規則檢核前移到 Middleware。步驟: 1) 預檢失敗映射 403/500；2) Controller 層保持單純；3) 錯誤訊息使用 RFC7807 Problem+JSON。核心組件: Middleware 錯誤處理、狀態碼對映。清楚的錯誤語意助於診斷與用戶端行為調整。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: D-Q1, A-Q24, C-Q7

B-Q16: ResetPassword 的 FSM 路徑如何？
- A簡: ACTIVATED 可用舊密碼重設；ACTIVATED/DEACTIVED 可用驗證碼重設並可能解鎖。
- A詳: 原理: 以動作與狀態決定可行路徑。步驟: 1) reset-password-with-old-password：需 ACTIVATED；2) reset-password-with-validate-number：ACTIVATED→ACTIVATED 或 DEACTIVED→ACTIVATED；3) force-reset-password：STAFF 於 ACTIVATED/DEACTIVED 均可。核心組件: FSM 邊定義。讓重置密碼同時扮演解鎖流程。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, A-Q15, C-Q6

B-Q17: GenerateValidateNumber 的條件與原則？
- A簡: 在 CREATED/START/DEACTIVED 可產生驗證碼；此動作不改變狀態（finalState 為 null）。
- A詳: 原理: 輔助性動作不影響狀態。步驟: 1) FSM 定義對應邊；2) Service 產生驗證碼並保存；3) 由外部通路傳遞（信件、簡訊）；4) 不改變成員狀態。核心組件: FSM、Service、Repository。此設計使驗證碼的發放不影響主要狀態流程。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, C-Q6, D-Q2

B-Q18: CheckPassword 連續錯誤如何鎖定帳號？
- A簡: 累計失敗次數，達門檻切換狀態為 DEACTIVED，成功則清零，透過 SafeChangeState 執行。
- A詳: 原理: 安全策略與 FSM 結合。步驟: 1) 比對 Hash；2) 失敗計數+1；3) 達門檻改狀態 DEACTIVED；4) 成功則計數清零；5) 發送事件。核心組件: Repository（計數欄位）、FSM、SafeChangeState。此策略降低暴力破解風險，並與客服解鎖流程銜接。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q7, D-Q3

B-Q19: Import/GetMembers/GetMember 屬於無特定成員 API 如何驗證？
- A簡: 無需成員狀態，僅依身份類型比對 FSM 邊的 allowIdentityTypes 即可。
- A詳: 原理: 無成員 API 不涉特定狀態。步驟: 1) 使用 CanExecute(actionName, identityType) 多載；2) 僅比對身份是否允許；3) 放行或拒絕。核心組件: FSM、Token。此區分類別清晰，避免混淆成員狀態與服務級動作。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, A-Q6, C-Q7

B-Q20: WebAPI 中路由與 Model Binding 如何設計？
- A簡: 路由負責資源定位（/members/{id}/activate），表單或 JSON 承載參數，屬性標註語意。
- A詳: 原理: RESTful 路由語意清晰。步驟: 1) [Route] 設定路由模板；2) [HttpPost]/[HttpGet] 指定動詞；3) [FromForm]/[FromBody] 繫結資料；4) [MemberServiceAction] 標明動作。核心組件: ASP.NET Core 路由、模型繫結。此設計提升可讀性與一致性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q4, B-Q6, B-Q15

B-Q21: 日誌/追蹤應落在哪層？如何傳遞 Request Id？
- A簡: 橫切於 Middleware 與 Core；以 Request Id 貫穿，事件/日誌攜帶，便於端到端追蹤。
- A詳: 原理: 可觀測性需跨層級。步驟: 1) Middleware 產生/擷取 Request Id；2) 注入到 Service/事件；3) 回應標頭附帶；4) 集中於 Log 系統。核心組件: 日誌抽象、分散式追蹤（如 W3C TraceContext）。本文示範以事件列印，可延伸至集中式平台。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, A-Q17, D-Q8

B-Q22: Contracts 版控與相容性策略怎麼做？
- A簡: 嚴格版控、後相容優先；重大變更以新版本並行，提供轉換與淘汰期。
- A詳: 原理: 合約即規格，變更即風險。步驟: 1) 以語意化版本標示；2) 變更偏好新增不刪除；3) 废棄標示與期限；4) 測試驗證相容；5) 文件同步更新。核心組件: 契約專案、NuGet 釋出、相容性測試。維持客戶端穩定，支撐長期演進。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q22, D-Q7, A-Q3

B-Q23: 縮小 API 表面積的技術策略？
- A簡: 合併常用組合、讓客端序列呼叫、用本地暫存；僅在必要時開合成端點。
- A詳: 原理: 控制風險與複雜度。步驟: 1) 盤點高頻序列；2) 評估由客端組合是否足夠；3) 若涉交易/效能才提供合成端點；4) 嚴格權限與速率管控。核心組件: FSM 規則、限流、快取。此策略讓系統既簡潔又能因需伸展。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, C-Q7, D-Q1

B-Q24: 如何把安全模型以規格表達到 FSM 與程式？
- A簡: 在 FSM 邊標註允許身份；Middleware 解析 token，與邊規則比對決定放行。
- A詳: 原理: 把可執行身份內嵌在轉移規則。步驟: 1) FSM 定義 allowIdentityTypes；2) Token 解析得 IdentityType；3) CanExecute 比對；4) 不合則拒絕。核心組件: FSM、Token、Middleware。將安全規則從散落程式轉為集中、可視與可測規格。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q2, B-Q5

B-Q25: Token 的 iat/exp/jti 與時效管理如何運作？
- A簡: iat 建立時間、exp 過期時間、jti 唯一識別；服務以此檢核時效、防重放。
- A詳: 原理: JWT 時效與唯一性控管。步驟: 1) 簽發含 iat/exp 的 token；2) Middleware 驗簽並比對時效；3) 可加 jti 黑名單/快取防重放；4) 重要操作再驗證。核心組件: jose-jwt、時間同步、金鑰管理。生產需輪替金鑰與最小存活時間策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, A-Q14, D-Q5


### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何實作 MemberStateMachine？
- A簡: 以 enum 定義狀態，List(tuple) 定義邊，提供 CanExecute 多載檢核行為合法性。
- A詳: 
  - 具體實作步驟: 
    1) 定義 enum MemberState；2) 建立 List<(action, init?, final?, allowTypes[])>；3) 填入所有動作與轉移；4) 實作 CanExecute。 
  - 關鍵程式碼片段:
    enum MemberState { START, CREATED, ACTIVATED, DEACTIVED, ARCHIVED, END }
    _fsmext.Add(("activate", CREATED, ACTIVATED, new[]{ "USER" }));
  - 注意事項與最佳實踐: 以常數/enum 避免字串錯拼；維持單一來源；為非特定成員 API 提供無狀態檢查多載。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q2, A-Q8

C-Q2: 如何用 jose-jwt 產生與驗證 MemberServiceToken？
- A簡: jose-jwt 以金鑰簽章/驗證 JWT，解析 claims 填入 Token，建議生產用 RSA。
- A詳:
  - 具體實作步驟:
    1) 建立 payload（iss, sub, iat, exp, jti）；2) 用 HS512/RS256 簽章；3) Middleware 驗簽並解析；4) 建構 MemberServiceToken。
  - 關鍵程式碼片段:
    var jwt = JWT.Encode(payload, key, JwsAlgorithm.HS512);
    var json = JWT.Decode(jwt, key, JwsAlgorithm.HS512);
  - 注意事項與最佳實踐: 金鑰妥善管理與輪替；exp 設置存活時間；生產建議改 RSA，避免共享對稱金鑰。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, A-Q14, B-Q25

C-Q3: 如何在 ASP.NET Core 註冊 DI 與 Middleware？
- A簡: 在 ConfigureServices 註冊 Singleton/Scoped；在 Configure 加入自訂 Middleware。
- A詳:
  - 具體實作步驟:
    1) services.AddSingleton<MemberRepo>(); services.AddSingleton<MemberStateMachine>(); 
       services.AddScoped<MemberServiceToken>(); services.AddScoped<MemberService>();
    2) app.UseMiddleware<MemberServiceMiddleware>();
  - 關鍵程式碼片段:
    services.AddScoped<MemberService>();
    app.UseMiddleware<MemberServiceMiddleware>();
  - 注意事項與最佳實踐: Token/Service 必須 Scoped；Middleware 須在 MVC 前；確保路由可讀取 Endpoint Metadata。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q12, B-Q5, A-Q19

C-Q4: 如何在 Controller 建立 Activate/Lock 等端點？
- A簡: 建立路由與動作屬性，注入 MemberService，轉遞參數呼叫 Core 方法。
- A詳:
  - 具體實作步驟:
    1) [ApiController][Route("[controller]")]；2) 建構子注入 MemberService；3) 設定路由與動作屬性。
  - 關鍵程式碼片段:
    [HttpPost, Route("{id:int:min(1)}/activate")]
    [MemberServiceAction(ActionName="activate")]
    public IActionResult Activate(int id, [FromForm] string number) { _service.Activate(id, number); return Ok(); }
  - 注意事項與最佳實踐: 嚴格輸入驗證；錯誤由 Middleware 統一處理；回應 Problem+JSON。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q11, B-Q6, B-Q15

C-Q5: 如何實作 SafeChangeState 樣板並套用到多個 action？
- A簡: 封裝鎖定、檢核、委派執行、驗證與事件，action 僅提供業務委派邏輯。
- A詳:
  - 具體實作步驟:
    1) SafeChangeState(id, actionName, Func<Model,bool> func)；2) 內部 lock→檢核→func→比對 finalState→寫回→事件。
  - 關鍵程式碼片段:
    return SafeChangeState(id, "activate", m => { if(m.ValidateNumber!=num) return false; m.State=ACTIVATED; m.ValidateNumber=null; return true; });
  - 注意事項與最佳實踐: func 僅關注商業邏輯；嚴格比對 FSM finalState；例外轉為一致錯誤回應。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q7, B-Q8, A-Q16

C-Q6: 如何用單元測試實作新會員註冊到啟用流程？
- A簡: 準備 Token/Repo/FSM，呼叫 Register→Activate→CheckPassword，斷言狀態與回傳值。
- A詳:
  - 具體實作步驟:
    1) 建立 web_token 與 MemberService；2) Register 取回 ValidateNumber；3) CheckPassword 應失敗；4) Activate 成功；5) 再 CheckPassword 應成功。
  - 關鍵程式碼片段:
    var m=svc.Register("brian","1234","b@x"); Assert.AreEqual(CREATED,m.State);
    svc.Activate(m.Id, m.ValidateNumber); Assert.IsTrue(svc.CheckPassword(m.Id,"1234"));
  - 注意事項與最佳實踐: 使用固定 Token 與 In-memory Repo；測試同時作為可執行規格。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q13, A-Q25, A-Q7

C-Q7: 如何用 Postman 測試 Authorization 與權限區分？
- A簡: 在 Header 設 Authorization: Bearer <JWT>，分別用 USER/STAFF token 呼叫端點比對行為。
- A詳:
  - 具體實作步驟:
    1) 在 Postman 設置 Authorization Bearer；2) STAFF 呼叫 GET /members/ 應 200；3) USER 呼叫同端點應被拒；4) 依流程測試 Register/Activate/CheckPassword。
  - 關鍵設定:
    Headers: Authorization = Bearer eyJ...
  - 注意事項與最佳實踐: 驗證 403/500 錯誤語意；保存環境變數重用 token；勿外洩敏感 token。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q15, D-Q1

C-Q8: 如何在 CLI 產生測試 token？
- A簡: 以 jose-jwt 在 CLI 產出 USER/STAFF token，輸出字串供 Postman 與測試使用。
- A詳:
  - 具體實作步驟:
    1) 建立 Console 專案；2) 設定 payload（iss/sub/iat/exp/jti）；3) jose-jwt 簽章輸出；4) Console.WriteLine 顯示。
  - 關鍵程式碼片段:
    Console.WriteLine(MemberServiceTokenHelper.CreateToken("STAFF","andrew"));
  - 注意事項與最佳實踐: 測試金鑰與生產金鑰隔離；避免把金鑰硬編碼在版本庫（示範可，生產不可）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, B-Q25, D-Q5

C-Q9: 如何把 OnStateChanged 事件改為 MQ 發布？
- A簡: 封裝 Publisher 介面，將事件改投遞到 Kafka/RabbitMQ，消費者訂閱處理。
- A詳:
  - 具體實作步驟:
    1) 定義 IEventPublisher.Publish(StateChangedEvent e)；2) 實作 Kafka/RabbitMQ Publisher；3) 在 SafeChangeState 成功後呼叫 Publish；4) 建立 Worker 訂閱處理（寄信、審計）。
  - 關鍵程式碼片段:
    await publisher.Publish(new StateChangedEvent{ Id, Init, Final, Action });
  - 注意事項與最佳實踐: 至少一次傳遞、重試/死信佇列、Idempotency 處理。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q10, A-Q17, D-Q9

C-Q10: 如何將 In-memory Repository 改為 EF Core 資料庫？
- A簡: 以 Repository 介面抽象，替換為 EF Core 實作，確保交易與並行一致策略。
- A詳:
  - 具體實作步驟:
    1) 抽象 IMemberRepo 介面；2) 建立 DbContext/Entity；3) 實作 CRUD 與必要欄位（版本、計數）；4) 在 SafeChangeState 中使用 Transaction。
  - 關鍵程式碼片段:
    using var tx=await db.Database.BeginTransactionAsync(); ... await db.SaveChangesAsync(); await tx.CommitAsync();
  - 注意事項與最佳實踐: 使用 RowVersion（並行控制）；對高衝突操作評估鎖策略；索引與查詢優化。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q8, B-Q9, D-Q10


### Q&A 類別 D: 問題解決類（10題）

D-Q1: 遇到 403/500 錯誤怎麼辦？
- A簡: 403 多為授權不足；500 常見為 FSM 規則或服務內錯誤。檢查 token、屬性與 FSM 定義。
- A詳:
  - 問題症狀描述: API 回應 403 Forbidden 或 500 Internal Server Error。
  - 可能原因分析: 403 為身份不允許（USER 調用 STAFF 動作）；500 可能為 FSM 不允許轉移、Middleware 例外、服務邏輯拋錯。
  - 解決步驟: 1) 確認 Authorization Bearer；2) 核對 [MemberServiceAction] 與 FSM 邊定義；3) 檢視服務日誌/例外堆疊；4) 以 Postman 切換 token 比對。
  - 預防措施: 規則測試覆蓋；錯誤語意標準化；Contract 與 FSM 變更走版控流程。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q15, C-Q7, A-Q12

D-Q2: Activate 輸入錯誤驗證碼如何處理？
- A簡: 服務應返回失敗，不改變狀態。檢查使用的驗證碼來源與有效期限。
- A詳:
  - 問題症狀描述: 使用錯誤驗證碼呼叫 activate，回應失敗。
  - 可能原因分析: 驗證碼不匹配或過期；帳號不在 CREATED 狀態。
  - 解決步驟: 1) 由 STAFF 發送新驗證碼（generate-validate-number）；2) 用新碼重試；3) 確認當前狀態允許轉移。
  - 預防措施: 設定驗證碼時效與重送機制；隱藏具體失敗原因防止試探。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q17, C-Q6, A-Q7

D-Q3: 三次密碼錯誤被鎖定如何解？
- A簡: 帳號進入 DEACTIVED。可由 USER 用驗證碼重設或 STAFF 強制重設/解鎖。
- A詳:
  - 問題症狀描述: 登入連續失敗後無法登入。
  - 可能原因分析: 失敗計數達門檻觸發鎖定策略（轉為 DEACTIVED）。
  - 解決步驟: 1) USER 申請驗證碼後 ResetPasswordWithValidateNumber；或 2) STAFF 執行 unlock/force-reset-password。
  - 預防措施: 調整門檻與時間窗；加強 CAPTCHA、防暴力破解；登入通知與審計。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q18, B-Q16, C-Q7

D-Q4: 並發造成重複狀態更新怎麼辦？
- A簡: 競態條件導致雙寫。以 SafeChangeState 鎖定保護，或上分散式鎖與交易策略。
- A詳:
  - 問題症狀描述: 兩個請求同時變更同一成員，導致資料不一致。
  - 可能原因分析: 缺乏鎖定與一致性策略；使用者重複提交。
  - 解決步驟: 1) 確認 SafeChangeState 已以鎖保護；2) DB 版控/交易；3) 分散式情境加入 Redis/DB 鎖；4) 引入冪等鍵。
  - 預防措施: 前端防重複提交；工作流程設計避免雙寫；事件處理設計冪等。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q7, B-Q8, C-Q10

D-Q5: Token 過期或無效如何診斷與處理？
- A簡: 驗證簽章與 exp；過期則引導重新登入或刷新；偽造需檢查金鑰與發行流程。
- A詳:
  - 問題症狀描述: API 一律返回 401/403 或 500，日誌顯示驗簽失敗或過期。
  - 可能原因分析: exp 到期、iat 時差、簽章不匹配、金鑰錯誤。
  - 解決步驟: 1) 使用 jwt.io 檢視 payload；2) 檢查伺服器時間同步；3) 金鑰正確性與輪替；4) 重新簽發 token。
  - 預防措施: 設定合理存活時間；提供刷新機制；金鑰保管與輪替策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q25, C-Q2, C-Q7

D-Q6: Middleware 未解析到 ActionName 造成錯誤？
- A簡: 端點未標註屬性或路由不符。補加 [MemberServiceAction] 並確認路由模板。
- A詳:
  - 問題症狀描述: Middleware 無法取得 actionName，FSM 檢查失敗。
  - 可能原因分析: Controller 方法缺少屬性；路由未命中；Endpoint Metadata 無資料。
  - 解決步驟: 1) 補上 [MemberServiceAction]；2) 檢查路由表與大小寫；3) 確認 Middleware 註冊順序正確。
  - 預防措施: 建立規則檢查與範本；在 CI 驗證所有端點皆標註屬性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, C-Q4, B-Q5

D-Q7: Contracts 改動導致相容性問題怎麼辦？
- A簡: 回滾或引入新版本並行，提供遷移文件與測試，確保客戶端平滑過渡。
- A詳:
  - 問題症狀描述: 更新後客戶端編譯/執行失敗。
  - 可能原因分析: 破壞性變更（刪欄位、改語意）；版本不一致。
  - 解決步驟: 1) 回滾到穩定版；2) 發布新 Major 版本並行；3) 文件/範例與遷移指南；4) 加入相容性測試。
  - 預防措施: 嚴格版控流程；偏好增量式變更；預先公告 Deprecation。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q22, A-Q22, A-Q3

D-Q8: WebAPI 返回 500 但 Core 測試正常，如何定位？
- A簡: 檢查 Middleware 與 Controller 映射、模型繫結、DI 與錯誤處理路徑，對照端到端日誌。
- A詳:
  - 問題症狀描述: 單元測試通過，HTTP 呼叫 500。
  - 可能原因分析: Middleware 預檢拋錯、模型繫結失敗、DI 範圍錯誤、未處理例外。
  - 解決步驟: 1) 打開開發錯誤頁；2) 驗證 Header 與路由；3) 檢查 DI 註冊；4) 加入端到端追蹤 id 日誌。
  - 預防措施: 整合測試覆蓋；統一錯誤映射；健全日誌與追蹤。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, B-Q12, B-Q21

D-Q9: 事件未觸發或重複觸發怎麼辦？
- A簡: 確認觸發條件（狀態變更才發）、訂閱註冊一次；MQ 需冪等與重試控制。
- A詳:
  - 問題症狀描述: 預期無事件或未收到／收到多次。
  - 可能原因分析: 狀態未改變就觸發；訂閱多次註冊；MQ 重試無冪等。
  - 解決步驟: 1) 僅在狀態改變時觸發；2) 訂閱端用唯一註冊；3) 加入事件 Idempotency；4) 配置死信與重試策略。
  - 預防措施: 事件規格明確；以事件 Id 去重；監控事件流量與失敗率。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, C-Q9, A-Q17

D-Q10: 切換到分散式環境後鎖定失效怎麼辦？
- A簡: 程式鎖僅單機有效。引入分散式鎖或資料庫交易，確保跨節點一致性。
- A詳:
  - 問題症狀描述: 多節點同時更新導致狀態錯亂。
  - 可能原因分析: 使用 C# lock 無法跨程序；缺分散式協調。
  - 解決步驟: 1) 導入 Redis Redlock/DB Row Lock；2) 強化交易邊界；3) 設計冪等與重試；4) 壅塞時回退或排隊。
  - 預防措施: 壓測並發；選擇合適一致性策略；行為以事件驅動化簡臨界區。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q8, B-Q9, C-Q10


### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是「用狀態機驅動的 API 設計」？
    - A-Q2: 什麼是有限狀態機（FSM），在會員服務怎麼用？
    - A-Q3: 為什麼微服務 API 要先設計（Spec First）再實作？
    - A-Q4: 認證、授權、存取控制的定義與差異？
    - A-Q5: 什麼是 MemberServiceToken？
    - A-Q6: USER 與 STAFF 的差異是什麼？
    - A-Q7: 會員的核心狀態有哪些？意義為何？
    - A-Q8: 狀態與動作（action）之間的關係？
    - A-Q10: 專案分層（Core/Contracts/WebAPI/CLI/Tests）各扮演什麼角色？
    - A-Q13: 什麼是 JWT？本文如何使用？
    - B-Q1: MemberStateMachine 的資料結構如何設計？
    - B-Q2: CanExecute 的執行流程是什麼？
    - B-Q5: Middleware 解析 Authorization 的機制？
    - C-Q3: 如何在 ASP.NET Core 註冊 DI 與 Middleware？
    - C-Q4: 如何在 Controller 建立 Activate/Lock 等端點？

- 中級者：建議學習哪 20 題
    - A-Q9: 為何 API 要「最小開放面積」？
    - A-Q11: 為何以「中台／內部 API 視角」設計會員服務？
    - A-Q12: 安全模型在 API 設計中的核心價值？
    - A-Q15: FSM 與存取控制（Access Control）如何整合？
    - A-Q16: SafeChangeState 在架構中的角色是什麼？
    - A-Q17: 事件驅動（OnStateChanged）在服務中的用途？
    - A-Q18: AOP（面向切面）在本案例的意義？
    - A-Q19: DI 生命週期（Singleton/Scoped）為何這樣選？
    - A-Q21: Spec-first 與過度設計如何拿捏？
    - A-Q22: 什麼是「合約（Contracts）」與相容性管理？
    - B-Q6: MemberServiceAction 屬性如何協助 FSM 檢查？
    - B-Q10: 事件通知機制如何設計（C# event vs MQ）？
    - B-Q11: WebAPI Controller 如何對應 Core 服務？
    - B-Q12: DI 注入與生命週期管理如何設計？
    - B-Q15: FSM/Middleware 如何對應 HTTP 錯誤碼？
    - B-Q16: ResetPassword 的 FSM 路徑如何？
    - B-Q18: CheckPassword 連續錯誤如何鎖定帳號？
    - C-Q6: 如何用單元測試實作新會員註冊到啟用流程？
    - C-Q7: 如何用 Postman 測試 Authorization 與權限區分？
    - D-Q1: 遇到 403/500 錯誤怎麼辦？

- 高級者：建議關注哪 15 題
    - B-Q7: SafeChangeState 的執行流程與組件？
    - B-Q8: 競態條件如何處理？單機 lock 與分散式鎖的差別？
    - B-Q9: 樂觀鎖與悲觀鎖如何取捨？
    - B-Q21: 日誌/追蹤應落在哪層？如何傳遞 Request Id？
    - B-Q22: Contracts 版控與相容性策略怎麼做？
    - B-Q23: 縮小 API 表面積的技術策略？
    - B-Q24: 如何把安全模型以規格表達到 FSM 與程式？
    - B-Q25: Token 的 iat/exp/jti 與時效管理如何運作？
    - C-Q2: 如何用 jose-jwt 產生與驗證 MemberServiceToken？
    - C-Q5: 如何實作 SafeChangeState 樣板並套用到多個 action？
    - C-Q9: 如何把 OnStateChanged 事件改為 MQ 發布？
    - C-Q10: 如何將 In-memory Repository 改為 EF Core 資料庫？
    - D-Q4: 並發造成重複狀態更新怎麼辦？
    - D-Q9: 事件未觸發或重複觸發怎麼辦？
    - D-Q10: 切換到分散式環境後鎖定失效怎麼辦？