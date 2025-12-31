---
layout: synthesis
title: "Policy Injection Application Block 小發現..."
synthesis_type: faq
source_post: /2008/11/18/policy-injection-application-block-small-discovery/
redirect_from:
  - /2008/11/18/policy-injection-application-block-small-discovery/faq/
postid: 2008-11-18-policy-injection-application-block-small-discovery
---

# Policy Injection Application Block 小發現...

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 Microsoft Enterprise Library？
- A簡: 微軟 Patterns & Practices 提供的可重用應用程式區塊集合，涵蓋記錄、例外、快取、安全、驗證等基礎設施，簡化企業級 .NET 開發。
- A詳: Microsoft Enterprise Library 是微軟 PnP 團隊整理的可重用元件集合，針對企業應用常見的基礎需求（Logging、Exception Handling、Caching、Security、Validation、Policy Injection 等）提供一致且可設定的解決方案。其目標是降低樣板式基礎設施程式的重複撰寫，透過配置與可插拔架構，讓開發者專注於商業邏輯，同時維持跨專案一致的非功能性需求實作。它也示範最佳實務與可維護的架構設計。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q13, B-Q10

A-Q2: 什麼是 Policy Injection Application Block（PIAB）？
- A簡: 以攔截與代理技術，將記錄、授權、快取、驗證等橫切關注透過宣告式與設定式注入至方法呼叫的應用區塊。
- A詳: PIAB 是 Enterprise Library 的一個區塊，透過代理（RealProxy/TransparentProxy）攔截方法呼叫，將「呼叫處理器（Call Handlers）」以管線形式套用在目標物件。開發者可用屬性（Attributes）或配置來宣告需要的橫切關注，如 Authorization、Logging、Caching、Exception Handling、Performance Counter、Validation 等。呼叫時先流經處理器管線，執行檢查或增強，再到達原方法。此法降低散落在各處的樣板碼，達到鬆耦合與一致性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, A-Q13, B-Q1

A-Q3: 為什麼需要 Policy Injection（而非手寫樣板碼）？
- A簡: 減少重複樣板碼、集中管理非功能性需求、以宣告式方式提高一致性與可維護性，讓商業邏輯更純粹。
- A詳: 記錄、驗證、授權、例外處理、快取等屬於橫切關注，若以手寫方式散落於各方法，會造成重複與耦合，增加維護成本。Policy Injection 讓這些關注從主邏輯抽離，以屬性或設定宣告一次、套用多處。其攔截式管線確保流程一致，並能彈性調整順序或關閉功能。這提升可測試性（核心邏輯可單測）、可配置性（依環境切換），也減少人為遺漏與錯誤。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, A-Q20, B-Q2

A-Q4: 什麼是 Call Handler（呼叫處理器）？
- A簡: 攔截方法呼叫時於前後插入邏輯的元件，依序形成管線，處理授權、記錄、快取、驗證等橫切需求。
- A詳: Call Handler 是 PIAB 的核心概念。當代理攔截到方法呼叫後，會依預先設定的順序執行一連串處理器，每個處理器可在「前置」與「後置」階段加入邏輯，如驗證輸入、檢查授權、寫入日誌、包裝例外、讀寫快取、遞增效能計數器等。處理器可決定是否繼續向下傳遞，也能改寫輸出或短路（例如快取命中直接回傳）。處理器可重複使用、組合，並以屬性或設定套用至目標。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, B-Q20, A-Q13

A-Q5: PIAB 的宣告式用法是什麼？
- A簡: 透過在目標方法或型別上套用對應屬性（如 AuthorizationCallHandler）宣告需求，並以代理建立物件使其生效。
- A詳: 宣告式使用指在方法或類別上加上對應的 Handler 屬性，例如 [AuthorizationCallHandler("op")]、[LogCallHandler]、[CachingCallHandler] 等，表示該位置需套用對應政策。此宣告本身不會自動生效，必須以 PolicyInjection.Create 或 Wrap 建立「加料」後的代理物件，呼叫才會被攔截並套用管線。宣告式優點是貼近程式碼語意、可讀性高，缺點是需控制物件建立方式。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, C-Q2, B-Q12

A-Q6: CAS 角色檢查與 PIAB 授權有何差異？
- A簡: CAS 角色檢查判斷是否屬於某角色；PIAB 授權可套用更細緻規則與提供可插拔授權提供者，彈性更高。
- A詳: CAS（如 PrincipalPermissionAttribute）在執行時確認呼叫端是否屬於特定角色，屬於 CLR 層級的內建檢查。PIAB 的 AuthorizationCallHandler 則可連結授權提供者，評估「操作」是否允許，可結合 ACL 或商業規則，比純角色判斷更精細。PIAB 屬於應用層，易擴充、可記錄與整合其他處理器；CAS 雖簡潔但不易自訂管線，也難加入記錄、快取等邏輯。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q4, B-Q23

A-Q7: 什麼是橫切關注（Cross-Cutting Concerns）？
- A簡: 貫穿多處商業邏輯的共通關注，如記錄、驗證、授權、快取、效能監控與例外處理。
- A詳: 橫切關注是指不屬於單一業務功能，卻需在多數方法或服務中一致執行的技術性需求，像是寫入日誌、參數驗證、權限檢查、結果快取、效能指標蒐集、例外處理策略等。若在每個方法手寫，會造成重複與維護困難。PIAB 以代理攔截，將這些關注抽離為可組合的處理器，統一配置與版本控管，維持核心邏輯的單一職責。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q20, B-Q2

A-Q8: Policy Injection 與 AOP 的關係是什麼？
- A簡: PIAB 是 AOP 思想在 .NET 的實務化，透過攔截與處理器達成切面化的前後置增強。
- A詳: 面向切面程式設計（AOP）主張將橫切關注抽離為切面，以宣告或配置將其織入執行流程。PIAB 以 .NET 代理攔截呼叫，使用處理器管線實現前置與後置增強，對開發者呈現為屬性或設定的宣告式用法。雖非編譯期織入（無需 IL 改寫），但達成了運行時切面化，兼顧彈性與非侵入性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q19, C-Q8

A-Q9: .NET Remoting 在 PIAB 中扮演什麼角色？
- A簡: PIAB 以本機代理（RealProxy/TransparentProxy）攔截呼叫，借用 .NET Remoting 的代理機制於本機達成 AOP。
- A詳: 雖然多數應用不使用跨進程的 .NET Remoting，PIAB 借用了其代理基礎：RealProxy 建立 TransparentProxy，攔截介面或 MarshalByRefObject 之方法呼叫，封裝成訊息，再由處理器管線處理並反射呼叫目標。這讓在本機也能以 Remoting 機制進行攔截與增強，不需改變既有 API 介面。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q11, B-Q12

A-Q10: 什麼是 RealProxy 與 TransparentProxy？
- A簡: RealProxy 產生 TransparentProxy 攔截方法呼叫；TransparentProxy 對呼叫端看似真實物件，實際轉發至 RealProxy。
- A詳: RealProxy 是 .NET 提供的代理基底，能攔截對目標物件的方法呼叫。它建立的 TransparentProxy 是一個透明代理，對使用者而言與原型別相容（如同實作同介面或為 MBRO），但每次呼叫都會轉為訊息，交由 RealProxy 處理。PIAB 以此機制包裝目標，將呼叫導入處理器管線，再觸達原方法。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q12, D-Q8

A-Q11: PIAB 的 Create 與 Wrap 有何差異？
- A簡: Create 由 PIAB 建立新代理與目標實例；Wrap 將既有實例包成代理。兩者皆需透過代理呼叫才會套用處理器。
- A詳: PolicyInjection.Create<T>() 會建立目標類別的新實例，並以代理包裹後回傳。PolicyInjection.Wrap<T>(instance) 則接收現有物件，外層生成代理以攔截其方法呼叫。不論哪種，僅對代理參考的呼叫才會進入處理器管線；若改用原生實例或 new 建立，則不會觸發。Wrap 適合整合既有物件，Create 適合新建並同時裝配策略。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q7, B-Q12, D-Q1

A-Q12: 角色（Role）與授權（Authorization）的差異？
- A簡: 角色是身份分組；授權是針對特定資源與操作的允許判定，通常比角色更細緻可控。
- A詳: 角色用來表達主體的職能群組（如 Administrators），常做粗粒度控制；授權則針對特定資源（如檔案、功能）與操作（讀、寫、執行）判斷是否允許，可結合 ACL 與商業規則。PIAB 的 AuthorizationCallHandler 以「操作名稱」對應授權供應者，允許以情境化規則判斷，不受限於僅檢查角色隸屬。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q4, D-Q9

A-Q13: PIAB 內建有哪些常用處理器？
- A簡: 授權、快取、例外處理、記錄、效能計數器、驗證，並支援自訂管線處理器以擴充行為。
- A詳: 常見處理器包含 Authorization Handler（檢查授權）、Caching Handler（結果快取）、Exception Handling Handler（例外策略化處理）、Logging Handler（呼叫日誌）、Performance Counter Handler（遞增計數器）、Validation Handler（輸入輸出驗證），以及自訂處理器。這些處理器可組合使用，依需求設定順序與適用範圍，以宣告或配置綁定至目標方法或型別。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, B-Q2, C-Q1

A-Q14: 何時該使用 Caching Handler？
- A簡: 當方法計算昂貴且結果可重用，輸入相同時結果穩定，使用快取可顯著降低延遲和資源消耗。
- A詳: 適合純函數或具相對穩定結果的方法，例如查詢排行榜、彙總統計、設定讀取等。Caching Handler 會以方法簽章與參數組合生成快取鍵，命中則短路回傳，未命中才執行原方法並寫入。需評估資料新鮮度、快取容量與失效策略。對易變資料或具副作用方法不宜使用。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q3, D-Q5

A-Q15: 何時該使用 Logging Handler？
- A簡: 需追蹤呼叫脈絡、輸入輸出、耗時與例外時，透過記錄處理器建立可觀測性與稽核能力。
- A詳: Logging Handler 可在方法前後寫入結構化記錄，包含方法名稱、引數、回傳值、例外、耗時等，利於問題診斷、稽核與性能分析。可與 Exception Handling、Performance Counter 搭配。注意隱私與敏感資訊遮蔽，避免過度記錄造成噪音與費用。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q1, D-Q6

A-Q16: 何時使用 Exception Handling Handler？
- A簡: 希望集中化轉換、記錄與分類例外，並維持一致的對外錯誤契約與重試政策時。
- A詳: 透過 Exception Handling Handler，可將低階例外映射為領域例外、統一記錄格式、決定是否重拋或包裝，並可與策略（如重試或補償）結合。這避免在每個方法重複 try/catch，降低洩漏內部實作細節的風險，並提升一致性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, C-Q6, D-Q7

A-Q17: 何謂 Performance Counter Handler 的價值？
- A簡: 在呼叫時自動遞增 Windows 計數器，提供方法呼叫率、錯誤率等可視化監控指標。
- A詳: Performance Counter Handler 能在方法進入與退出時更新特定計數器，如呼叫次數、平均耗時、失敗數。這與 Windows Performance Monitor 整合，有助於在生產環境持續監控與容量規劃。與 Logging 搭配可形成全方位可觀測性方案。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q8, C-Q4, D-Q7

A-Q18: 何時使用 Validation Handler？
- A簡: 當需統一參數或回傳值的驗證規則，避免分散在各方法手寫驗證時。
- A詳: Validation Handler 能在方法執行前後依既有驗證規則（屬性或設定）檢查引數與輸出，若不通過則阻擋執行並回報錯誤。這讓輸入檢核一致且可重用，避免重複程式碼與遺漏。常與授權、例外策略搭配確保業務邏輯在乾淨狀態執行。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q9, C-Q5, D-Q5

A-Q19: 什麼是 Custom Pipeline Handlers？
- A簡: 由開發者自訂的呼叫處理器，用於擴充框架未涵蓋的橫切需求，並可加入既有管線。
- A詳: 當內建處理器無法滿足需求（如多租戶標記、資料遮蔽、審核事件發佈），可透過實作 ICallHandler 或繼承 HandlerAttribute 實現客製處理器。它與內建處理器同樣能設定順序、前後處理與短路行為，並以屬性或設定套用到目標。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q20, C-Q8, D-Q6

A-Q20: 什麼是處理器管線（Pipeline）？
- A簡: 攔截後依序執行的處理器鏈，具前置與後置階段，可短路或改寫結果，最後才觸達目標方法。
- A詳: 管線是處理器的組合與順序。呼叫進來時依 Order 由小到大執行前置邏輯；呼叫返回時則反向執行後置邏輯。某些處理器（如快取命中）可直接產生回應並短路剩餘處理與目標呼叫。正確設計順序能確保驗證先於授權、記錄覆蓋完整範圍等。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q3, C-Q9

A-Q21: 使用 PIAB 有哪些適用條件與限制？
- A簡: 需以代理建立物件，並以介面或 MarshalByRefObject 供攔截；部分情境對效能與偵錯有成本。
- A詳: 代理攔截仰賴 .NET Remoting 機制：目標型別須實作介面或繼承 MarshalByRefObject，呼叫端透過代理參考才會走管線。Hot path 可能有少量額外開銷；某些語言特性（如密封類不走介面）或私有方法不可攔截。偵錯時需注意代理堆疊與實體目標的對應。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: D-Q2, D-Q3, B-Q14

A-Q22: 為何宣告式（Attributes）較具維護性？
- A簡: 規則與程式碼鄰近、語意清晰、可組合；變更集中在宣告與組態，降低散落式修改風險。
- A詳: 宣告式將意圖貼在方法或類別上，閱讀即知此處需驗證、授權、記錄或快取。與處理器組態搭配，可在不改動核心邏輯下開關功能或調整順序。相較命令式散布多處的樣板碼，宣告式更易審閱、測試與一致化。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q5, A-Q20, B-Q24

A-Q23: 使用 PIAB 的潛在缺點與風險？
- A簡: 代理開銷、偵錯複雜度提升、過度記錄或快取風險、與型別限制導致攔截落空。
- A詳: 攔截導致每次呼叫增加少量開銷；代理堆疊讓偵錯與例外追蹤更複雜。若未妥善控管，Logging 可能外洩敏感資訊，Caching 可能造成陳舊資料。型別未符合攔截條件或未用代理建立可能導致處理器不生效。需以測試與規範降低風險。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: D-Q1, D-Q6, D-Q7

A-Q24: PIAB 與手動插入樣板碼有何不同？
- A簡: PIAB 將橫切關注抽離為可配置管線，免除重複程式碼，支援順序控制、短路與集中維護。
- A詳: 手動插入雖直接，但容易重複、遺漏且難統一。PIAB 以代理與處理器讓橫切邏輯集中、可重用，並可宣告式套用。處理器可在前後置掛鉤、決定短路或包裝例外，並以順序控制確保語意正確。此法更易於維護、測試與審核。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q3, A-Q20, B-Q2

A-Q25: 宣告式與設定式套用策略的差異？
- A簡: 宣告式在程式碼加屬性；設定式以外部組態與比對規則配綁，無需改碼更動套用範圍。
- A詳: 宣告式可讀性高、靠近程式語意；設定式則透過匹配規則（如命名、命名空間、屬性條件）在外部組態掛上處理器，利於環境切換與批量套用。兩者可並用，但需管理好順序與衝突策略。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q22, B-Q24, C-Q1

---

### Q&A 類別 B: 技術原理類

B-Q1: PIAB 攔截呼叫的基本機制如何運作？
- A簡: 以 RealProxy 建立 TransparentProxy 攔截方法呼叫，封裝訊息進入處理器管線，最後以反射呼叫目標方法。
- A詳: 呼叫端取得的其實是 TransparentProxy。每次方法呼叫被轉換成訊息物件，交由 RealProxy 的 Invoke 處理。PIAB 在此將訊息流經處理器管線：前置階段可驗證、授權、快取命中短路；若繼續則以反射呼叫實際目標，取得回傳或例外，再由後置處理器處理（記錄、包裝例外、更新快取、遞增計數器）。最終產生回應返回呼叫端。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, A-Q10, B-Q2

B-Q2: 處理器的執行流程為何？
- A簡: 依 Order 遞增執行前置、可短路；目標返回後以相反順序執行後置，最後回傳結果或例外。
- A詳: 管線進入時，PIAB 依處理器的 Order 屬性由小到大執行前置 OnInvoke。若某處理器返回短路結果（如快取命中），則跳過後續前置與目標呼叫。若繼續，反射呼叫目標取得結果或例外，再依 Order 由大到小執行後置（如記錄回傳、包裝例外、更新快取、遞增計數器）。此對稱流程確保語意一致且便於推理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q20, B-Q3, C-Q9

B-Q3: 如何決定與控制處理器順序（Order）？
- A簡: 透過屬性或設定的 Order 屬性設定整數權重；數字越小越先執行前置，越後執行後置。
- A詳: 多個處理器並用時，需明確設定 Order 以確保語意正確。例如 Validation（10）→ Authorization（20）→ Caching（30）→ Logging（40）→ Performance（50）→ Exception Handling（60）。前置依序進行，後置則反向。宣告式屬性與設定式皆可指定 Order，混用時以合併策略建立單一序列。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q20, C-Q9, D-Q4

B-Q4: AuthorizationCallHandler 的機制是什麼？
- A簡: 於方法前置階段依操作名稱查詢授權提供者，根據主體與環境評估是否允許，拒絕則丟擲例外。
- A詳: 該處理器會取得呼叫脈絡（使用者、角色、宣告等）與設定的 operation name，交由註冊的授權提供者判斷。若不允許，直接丟擲授權例外短路；允許則繼續管線。它可與 Validation、Logging 搭配，先驗證再授權，並記錄拒絕事件。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, A-Q12, D-Q9

B-Q5: Caching Handler 如何決定快取鍵與命中？
- A簡: 通常以方法名稱、型別與輸入參數序列化組成鍵；命中則直接回傳，未命中執行並寫入快取。
- A詳: 進入前置時，處理器以可設定的鍵策略計算鍵（含型別/方法/參數）。若快取存在且未失效，直接短路回傳；否則呼叫目標並在後置寫入。需注意參數可序列化性、相等比較，與避免包含敏感資料。可調整過期、區域與依賴。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, C-Q3, D-Q5

B-Q6: Logging Handler 如何擷取輸入輸出？
- A簡: 於前置擷取方法名稱、參數與脈絡；於後置擷取回傳與例外、耗時，形成結構化日誌輸出。
- A詳: 前置記錄呼叫起點（時間、主體、方法、引數摘要）；若發生例外於後置捕捉、分類並記錄堆疊與關鍵欄位；成功則記錄回傳摘要與耗時。可設定遮蔽欄位、層級與目標。與 Performance Counter 搭配可補足量化指標。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q15, C-Q1, D-Q6

B-Q7: Exception Handling Handler 背後機制？
- A簡: 捕捉目標拋出的例外，依策略分類、記錄、轉換或重拋，維持對外一致錯誤契約。
- A詳: 於後置階段攔截例外，根據設定策略（例外類型對映處理規則）決定動作：記錄、包裝為領域例外、附加相機資訊、或抑制/重拋。可與 Logging、Performance 整合，形成端到端可觀測與一致錯誤處理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, C-Q6, D-Q7

B-Q8: Performance Counter Handler 如何運作？
- A簡: 呼叫前後更新預先註冊的計數器，包含呼叫數、失敗數、耗時統計，供 PerfMon 觀察。
- A詳: 於前置紀錄開始時間並遞增「呼叫次數」；後置計算耗時、判斷成功或失敗遞增相應計數並更新平均值。需事先建立計數器類別與實例，並以設定或屬性關聯到方法。過度粒度會增加負擔，需適度選擇。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q17, C-Q4, D-Q7

B-Q9: Validation Handler 檢核流程為何？
- A簡: 於前置對輸入參數套用規則，於後置對回傳值套用規則；失敗則擲回驗證例外並短路。
- A詳: 驗證規則可來源於屬性或外部設定，涵蓋必填、範圍、格式、自訂邏輯等。前置確保方法在乾淨狀態執行；後置保證輸出契約。錯誤收集後以一致方式回報，利於前端顯示與稽核。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q18, C-Q5, D-Q5

B-Q10: PIAB 如何同時支援屬性與設定？
- A簡: 以屬性宣告本地需求，並以設定定義處理器與匹配規則；兩者在執行前合併為單一管線。
- A詳: 執行時會蒐集類別/方法上的處理器屬性，再根據設定中匹配規則（如型別、命名模式）附加處理器。合併後依 Order 排序執行。此機制令同一二進位在不同環境以配置開關或調整策略。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q25, B-Q22, B-Q24

B-Q11: IMessage 與 IMessageSink 在此扮演什麼角色？
- A簡: 代表方法呼叫的訊息與處理鏈節點；PIAB 可於訊息處理過程注入自訂邏輯。
- A詳: 在 Remoting 模型中，方法呼叫被包成 IMessage 並透過 IMessageSink 鏈傳遞。PIAB 的代理以同理路徑擴展，將處理器視作鏈上節點，於鏈中執行前後置邏輯。雖然多數情境本機使用，仍沿用此訊息導向概念。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q9, B-Q1, B-Q12

B-Q12: PolicyInjection.Create/Wrap 的代理建立細節？
- A簡: Create 生成目標與代理；Wrap 外包既有實例。代理實現介面或 MBRO，攔截公開方法呼叫。
- A詳: Create 會反射呼叫建構子建立目標，再用 RealProxy 生成相容代理；Wrap 對傳入實例建立外層代理，保留其狀態。若目標實作介面，代理回傳為該介面型別；若為 MBRO，則可回傳為原類型的透明代理。非公開成員不攔截。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q11, D-Q1, D-Q2

B-Q13: 代理對型別與相等性的影響？
- A簡: 代理看似原型別（介面或 MBRO），參考相等性與序列化行為可能不同，須留意 is/as 與跨界限。
- A詳: 以介面代理時，回傳型別為介面，無法以具體型別 cast；需依賴介面程式設計。MBRO 透明代理在 is/as 可通過，但序列化或跨邊界行為與一般物件不同。參考相等性可能比較代理而非目標，需避免在相等性敏感處過度依賴參考比較。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: D-Q8, B-Q12, C-Q7

B-Q14: PIAB 與執行緒安全/Principal 的交互？
- A簡: 授權多仰賴 Thread.CurrentPrincipal 或自訂脈絡；需在呼叫前設置正確身份，避免管線中斷。
- A詳: AuthorizationCallHandler 會從執行緒上下文讀取 Principal 或自訂提供者的身份資訊。若主體未設置或遺失（如背景工作），可能導致誤判拒絕。需在邏輯入口（如 API 層）建立或流轉正確主體，並避免於處理器中變更影響後續。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q6, A-Q12, D-Q9

B-Q15: 處理器如何處理 out/ref 參數與回傳值？
- A簡: 管線會在前置讀取輸入；後置可讀回傳與 out/ref 值。部分快取或記錄需特別處理此類參數。
- A詳: 設計處理器時，需於後置階段取得最終回傳與 out/ref 值以正確記錄或驗證。Caching Handler 一般只支援基於輸入與回傳值的快取，不建議包含 out/ref。Logging 需避免序列化大物件與敏感資料。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: D-Q5, B-Q6, B-Q5

B-Q16: 管線中例外的傳遞與處理規則？
- A簡: 例外可由目標或處理器丟出；若有 Exception Handling Handler，依策略轉換後再向外拋出或吞沒。
- A詳: 若處理器或目標拋出例外，後續處理器的後置階段仍可接收並決策。Exception Handling Handler 可記錄、映射與重拋。吞沒例外須謹慎，避免隱藏錯誤。Logging 應在轉換前記錄足跡。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, B-Q7, D-Q7

B-Q17: 性能成本來源與量級？
- A簡: 主要來自代理轉發、反射呼叫、處理器邏輯；對多數業務方法為微小固定開銷，熱路徑需評估。
- A詳: 代理將直接呼叫改為訊息路徑與反射，增加數十微秒級開銷（視處理器多寡與記錄 I/O 而變）。快取命中可抵銷成本。應避免在高頻緊迴圈或極低延遲路徑套用過多處理器，對 I/O 密集或網路呼叫佔比高之方法影響較小。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q23, D-Q7, C-Q9

B-Q18: PIAB 與裝飾器模式/動態代理比較？
- A簡: PIAB 用動態代理自動織入切面，無需手寫裝飾類；裝飾器需顯式包裝且易重複。
- A詳: 裝飾器提供明確結構但需撰寫多層包裝類。PIAB 以動態代理在運行時攔截，透過屬性與設定組合行為，靈活切換。對於需要大量橫切關注的系統，PIAB 更具生產力與一致性；對極簡需求，裝飾器亦可行。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q8, A-Q24, C-Q8

B-Q19: 自訂 ICallHandler 的設計要點？
- A簡: 明確定義前後置行為、短路條件、順序與可配置項；避免狀態耦合與副作用。
- A詳: 自訂處理器需實作 Invoke 並包住下一個委派，前置讀取脈絡與參數，決定是否短路；後置處理結果與例外。公開可配置屬性（如遮蔽欄位、逾時），並提供對應屬性/組態供套用。注意執行緒安全與效能，避免不可預期副作用。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q19, C-Q8, D-Q6

B-Q20: HandlerAttribute 與 ICallHandler 的關係？
- A簡: HandlerAttribute 是宣告用屬性，負責產生 ICallHandler 實例並注入設定，兩者協同完成織入。
- A詳: 在宣告式用法中，開發者繼承 HandlerAttribute 並覆寫 CreateHandler 以回傳 ICallHandler。屬性攜帶的設定（如 Order、遮蔽等）會轉交處理器實例。這使宣告語意與執行邏輯分離，便於重用與測試。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q8, A-Q5, B-Q3

B-Q21: 如何比對政策適用範圍（Matching Rules）？
- A簡: 透過命名模式、命名空間、屬性條件等規則，決定哪些型別/方法套用處理器。
- A詳: 設定式可定義多種匹配規則，像類別/方法名稱通配、命名空間前綴、存在某屬性等，組合形成適用集。這讓無需改碼即可批量套用或排除，並可依部署環境調整。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q25, B-Q10, C-Q1

B-Q22: 宣告式與設定式合併時的衝突處理？
- A簡: 兩來源的處理器會合併排序；如行為重疊，需以 Order 與限定匹配避免重複或衝突。
- A詳: 合併後可能出現重複記錄或多次驗證。可透過：調整匹配規則範圍、統一 Order、或在自訂處理器中偵測避免重入。測試與審閱組態是關鍵。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q25, B-Q3, D-Q4

B-Q23: 與 CLR CAS 的執行模型差異？
- A簡: CAS 在 CLR 層執行 Demand；PIAB 在應用層以代理管線評估，易擴充但不具 CLR 強制性。
- A詳: CAS 屬執行階段的安全模型，與 CLR 權限系統緊密整合。PIAB 則是應用層框架，可插拔且可記錄，彈性高但需正確使用代理與配置。安全強度與可擴充性取捨需視情境而定。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, A-Q21, D-Q9

B-Q24: 如何確保多來源處理器順序穩定？
- A簡: 統一制定 Order 約定、集中管理共用處理器、在組態覆寫預設順序並建立測試檢核。
- A詳: 設計指引中明確定義各類處理器的預設 Order，宣告式屬性採相同預設；在組態中對全域處理器指定 Order；建立單元測試驗證實際順序；於程式碼審查中檢查屬性與組態衝突。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q3, B-Q22, C-Q9

B-Q25: 從 CAS 遷移到 PIAB 的策略？
- A簡: 以 AuthorizationCallHandler 替換角色檢查，導入操作概念與授權提供者，並建立日誌與例外策略。
- A詳: 盤點現有 [PrincipalPermission] 用例，將「角色檢查」提升為「操作授權」，定義操作清單與規則來源。以屬性宣告與設定式補上共通需求（記錄、驗證、例外）。逐步以代理建立物件，建立整合測試確保語意一致。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q6, B-Q4, C-Q2

---

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何以屬性快速為服務方法加入記錄？
- A簡: 在方法加上 LogCallHandler 屬性，並以 PolicyInjection.Create 建立代理呼叫，即可自動記錄呼叫資訊。
- A詳: 
  - 具體實作步驟:
    1) 在類別方法上加 [LogCallHandler].
    2) 以 PolicyInjection.Create<IService, Service>() 取得代理。
    3) 透過代理呼叫方法。
  - 程式碼:
    ```csharp
    public interface IAcct { void Deposit(decimal amt); }
    public class Acct : IAcct {
      [LogCallHandler] public void Deposit(decimal amt){ /* ... */ }
    }
    var acct = PolicyInjection.Create<IAcct, Acct>();
    acct.Deposit(100m);
    ```
  - 注意事項: 遮蔽敏感欄位；避免記錄大量物件；在設定中調整目標與層級。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q15, B-Q6, D-Q6

C-Q2: 如何為方法加入授權檢查？
- A簡: 在方法加 AuthorizationCallHandler 屬性指定操作名稱，並以代理呼叫，由授權提供者判定是否允許。
- A詳:
  - 實作步驟:
    1) 設定授權提供者/策略。
    2) 在方法宣告 [AuthorizationCallHandler("operation-name")].
    3) 以 PolicyInjection.Create/Wrap 取得代理呼叫。
  - 程式碼:
    ```csharp
    public class Bank {
      [AuthorizationCallHandler("Deposit")]
      public void Deposit(decimal amount){ /* ... */ }
    }
    var bank = PolicyInjection.Create<Bank>();
    bank.Deposit(100m);
    ```
  - 注意: 確保 Thread.CurrentPrincipal 正確；定義操作與資源對映。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q4, D-Q9

C-Q3: 如何啟用 Caching Handler 加速昂貴查詢？
- A簡: 以屬性啟用 CachingCallHandler，設定過期策略，代理呼叫時命中即短路回傳。
- A詳:
  - 步驟:
    1) 啟用快取區塊與儲存。
    2) 在方法加 [CachingCallHandler(Expiration=60)] 等設定。
    3) 透過代理呼叫。
  - 程式碼:
    ```csharp
    public interface IRepo { string GetTopN(int n); }
    public class Repo : IRepo {
      [CachingCallHandler(SecondsToExpire=60)]
      public string GetTopN(int n){ /* costly */ }
    }
    var repo = PolicyInjection.Create<IRepo, Repo>();
    var a = repo.GetTopN(10); // 計算
    var b = repo.GetTopN(10); // 命中快取
    ```
  - 注意: 避免快取易變或含敏感資料；確保參數可作為鍵。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q5, D-Q5

C-Q4: 如何以 Performance Counter 監控方法？
- A簡: 在方法加 PerformanceCounterCallHandler 並預先建立計數器，代理呼叫自動遞增監控指標。
- A詳:
  - 步驟:
    1) 以 InstallUtil 或程式建立計數器類與實例。
    2) 在方法加 [PerformanceCounterCallHandler("Category","Instance")].
    3) 透過代理呼叫並用 PerfMon 觀察。
  - 程式碼:
    ```csharp
    public class Service {
      [PerformanceCounterCallHandler("MySvc","API")]
      public void Foo(){ /* ... */ }
    }
    var s = PolicyInjection.Create<Service>();
    s.Foo();
    ```
  - 注意: 避免過多細粒度；與記錄協同避免重複成本。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q17, B-Q8, D-Q7

C-Q5: 如何在方法層加入輸入輸出驗證？
- A簡: 搭配 Validation Block 規則，在方法加 ValidationCallHandler，違規即拋出驗證例外。
- A詳:
  - 步驟:
    1) 定義規則（屬性或設定）。
    2) 在方法加 [ValidationCallHandler].
    3) 透過代理呼叫，未通過則擲錯。
  - 程式碼:
    ```csharp
    public class OrderSvc {
      [ValidationCallHandler]
      public void Place([NotNullValidator]Order o){ /* ... */ }
    }
    var svc = PolicyInjection.Create<OrderSvc>();
    svc.Place(null); // 觸發驗證例外
    ```
  - 注意: 清晰錯誤訊息；避免重複驗證；輸出驗證同理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q18, B-Q9, D-Q5

C-Q6: 如何應用 Exception Handling Handler 統一錯誤？
- A簡: 配置例外策略並套用屬性，於後置統一記錄與映射例外，維持對外一致契約。
- A詳:
  - 步驟:
    1) 建立例外處理策略（型別對映、動作）。
    2) 方法加 [ExceptionCallHandler("PolicyName")].
    3) 代理呼叫並觀察統一錯誤輸出。
  - 程式碼:
    ```csharp
    public class Repo {
      [ExceptionCallHandler("DataPolicy")]
      public Customer Get(int id){ /* throws SqlException */ }
    }
    var r = PolicyInjection.Create<Repo>();
    r.Get(1); // 轉為 DataAccessException
    ```
  - 注意: 不可濫用吞沒；保留診斷資訊。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, B-Q7, D-Q7

C-Q7: 何時使用 Wrap 而非 Create？如何實作？
- A簡: 當已有實例需套用政策時使用 Wrap；Create 用於新建。兩者皆須以代理參考呼叫。
- A詳:
  - 步驟:
    1) 建立既有物件。
    2) 以 PolicyInjection.Wrap<IType>(instance) 包裝。
    3) 使用回傳之代理參考。
  - 程式碼:
    ```csharp
    var raw = new Acct();
    var acct = PolicyInjection.Wrap<IAcct>(raw);
    acct.Deposit(100m); // 走管線
    ```
  - 注意: 後續請勿再用 raw 呼叫；使用介面以利攔截。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q12, D-Q1

C-Q8: 如何撰寫自訂處理器與屬性？
- A簡: 實作 ICallHandler 定義前後置邏輯，並建立繼承 HandlerAttribute 的屬性產生處理器實例。
- A詳:
  - 步驟:
    1) 實作 ICallHandler.Invoke。
    2) 建立 MyHandlerAttribute: HandlerAttribute，覆寫 CreateHandler。
    3) 在方法上加屬性，透過代理呼叫。
  - 程式碼:
    ```csharp
    public class MaskHandler: ICallHandler {
      public IMethodReturn Invoke(IMethodInvocation input, GetNextHandlerDelegate next){
        // 前置: 遮蔽敏感參數
        var ret = next()(input, next);
        // 後置: 遮蔽回傳
        return ret;
      }
    }
    [AttributeUsage(AttributeTargets.Method)]
    public class MaskAttribute: HandlerAttribute {
      public override ICallHandler CreateHandler(IUnityContainer c){ return new MaskHandler(); }
    }
    ```
  - 注意: 無副作用、可配置；設定 Order。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q19, B-Q20, D-Q6

C-Q9: 如何組合多個處理器並控制順序？
- A簡: 以屬性 Order 指定順序或在設定中統一排序，確保驗證→授權→快取→記錄→例外等語意。
- A詳:
  - 步驟:
    1) 在屬性指定 Order。
    2) 在組態中對全域處理器設定預設 Order。
    3) 撰寫測試驗證實際順序與行為。
  - 程式碼:
    ```csharp
    [ValidationCallHandler(Order=10)]
    [AuthorizationCallHandler("Deposit", Order=20)]
    [CachingCallHandler(Order=30)]
    [LogCallHandler(Order=40)]
    [ExceptionCallHandler("Policy", Order=60)]
    public void Deposit(decimal amt) { /* ... */ }
    ```
  - 注意: 避免衝突與重複；建立順序約定。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q24, D-Q4

C-Q10: 如何撰寫單元測試驗證處理器效果？
- A簡: 以代理呼叫，驗證副作用（如日誌輸出、快取命中次數、授權拒絕），並模擬邊界情境。
- A詳:
  - 步驟:
    1) 使用測試替身收集日誌/計數器。
    2) 呼叫同參數兩次驗證快取。
    3) 設定不同 Principal 驗證授權。
    4) 模擬例外檢查映射。
  - 程式碼（概念）:
    ```csharp
    var svc = PolicyInjection.Create<IRepo, Repo>();
    svc.GetTopN(10); svc.GetTopN(10);
    Assert.Equal(1, logger.Calls["GetTopN"].CacheMiss);
    ```
  - 注意: 驗證順序與遮蔽；避免依賴真實外部資源。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q17, B-Q24, D-Q7

---

### Q&A 類別 D: 問題解決類（10題）

D-Q1: 為何加了屬性仍不生效（不進入處理器）？
- A簡: 物件以 new 建立未經代理；需用 PolicyInjection.Create 或 Wrap 建立代理並以代理參考呼叫。
- A詳:
  - 症狀: 方法上有處理器屬性但呼叫不記錄、不驗證。
  - 可能原因: 直接 new；呼叫時使用原始實例；注入容器未整合 PIAB。
  - 解決步驟: 以 PolicyInjection.Create/Wrap 取得代理；確保所有呼叫流經代理；在容器註冊攔截器。
  - 預防: 建立工廠/容器統一建立，避免 new 散落。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q5, A-Q11, C-Q7

D-Q2: 為何代理攔截不到（型別限制導致）？
- A簡: 目標未實作介面或非 MarshalByRefObject；請使用介面程式設計或改為 MBRO。
- A詳:
  - 症狀: 使用 Create/Wrap 但仍未攔截。
  - 可能原因: 類別密封且未實作介面；非 MBRO；呼叫以具體型別參考。
  - 解決步驟: 對外以介面暴露；或讓型別繼承 MarshalByRefObject；改以介面型別接住代理。
  - 預防: API 設計優先介面；建立設計規範與靜態檢查。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q21, B-Q12, B-Q13

D-Q3: 為何建構子與私有方法無法被攔截？
- A簡: PIAB 攔截公開方法呼叫；建構子與私有成員不在攔截範圍，需改以工廠/公開方法承載。
- A詳:
  - 症狀: 期望在建構與私有操作記錄/驗證，卻無效果。
  - 原因: 代理攔截層級限制於公開/可攔截方法呼叫。
  - 解決: 將初始化邏輯移至可攔截的公開初始化方法；將私有邏輯拆至可攔截的協作物件。
  - 預防: 設計時考量可攔截性，避免關鍵邏輯封閉於不可攔截處。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q21, B-Q12, C-Q9

D-Q4: 處理器順序錯誤導致語意不對怎麼辦？
- A簡: 明確設定 Order，統一約定，於組態覆寫並加入測試驗證，避免宣告式與設定式衝突。
- A詳:
  - 症狀: 先快取後驗證、先記錄後授權等語意錯序。
  - 原因: 預設 Order 或混用來源未協調。
  - 解決: 統一定義 Order；在屬性與組態顯式指定；檢視實際合併順序。
  - 預防: 建立順序檢查測試；審查變更。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q22, C-Q9

D-Q5: 為何快取沒有命中或行為異常？
- A簡: 參數不可序列化、含 ref/out、回傳為 void、鍵策略不當或過期設定太短。
- A詳:
  - 症狀: 同參數重複呼叫仍執行原方法；或快取污染。
  - 原因: 參數無法作鍵；out/ref 改變語意；回傳 void 無可快取；過期太短或未持久化。
  - 解決: 僅快取純函數結果；自訂鍵策略；避免 out/ref；調整過期。
  - 預防: 撰寫命中率測試；監控快取效益。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q5, C-Q3

D-Q6: 記錄過量或洩漏敏感資訊如何處理？
- A簡: 調整濾波與層級、遮蔽敏感欄位、縮減粒度，並以自訂處理器實作遮蔽與取樣。
- A詳:
  - 症狀: 日誌暴增、包含帳號、卡號等敏感資料。
  - 原因: 預設記錄全部參數、未遮蔽。
  - 解決: 設定遮蔽；在屬性標示敏感欄位；自訂處理器統一遮蔽；調整取樣率。
  - 預防: 資安審查與測試；資料分類標記。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, B-Q6, C-Q8

D-Q7: 效能不佳的原因與優化方法？
- A簡: 過多處理器、重 I/O 記錄、熱路徑不適用；可縮減處理器、改非同步、精準匹配與使用快取。
- A詳:
  - 症狀: 延遲上升、吞吐下降。
  - 原因: 管線過長、同步 I/O、計數器粒度過細。
  - 解決: 移除不必要處理器；將記錄非同步；僅匹配關鍵方法；快取昂貴結果。
  - 預防: 基準測試；監控計數器；設計指引。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q17, C-Q9, C-Q3

D-Q8: 代理造成型別/序列化或轉型問題怎麼辦？
- A簡: 以介面為邊界、避免依賴具體型別；限制跨 AppDomain；必要時改用非攔截路徑。
- A詳:
  - 症狀: 無法 cast 至具體類、序列化失敗、相等性比較異常。
  - 原因: 介面代理僅為介面型別；MBRO 跨界限限制；代理參考與目標不同。
  - 解決: 以介面編程；不在代理上做二進位序列化；需要具體類時於邊界解除攔截。
  - 預防: 在 API 設計期即規劃介面邊界；撰寫相容性測試。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q13, B-Q12, C-Q7

D-Q9: 授權處理器總是拒絕，如何診斷？
- A簡: 確認 Thread.CurrentPrincipal、操作名稱對映、提供者設定與匹配規則；以記錄追蹤評估結果。
- A詳:
  - 症狀: 合法使用者也被拒絕。
  - 原因: 主體未設置；操作名稱錯誤；提供者未註冊；管線未觸發。
  - 解決: 在入口設置 Principal；校對操作與規則；增加診斷日誌；確認以代理呼叫。
  - 預防: 驗收測試涵蓋授權矩陣；文件化操作清單。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q4, D-Q1

D-Q10: 如何在偵錯時看清楚代理與實際呼叫？
- A簡: 於日誌加入追蹤 ID、在處理器中記錄進入/退出、使用代理揭露目標資訊或暫時停用處理器。
- A詳:
  - 症狀: 呼叫堆疊包含代理層難以追蹤。
  - 解決: 在管線兩端記錄呼叫 ID；於代理/處理器曝露 InnerTarget 供偵測；在本機配置關閉非必要處理器；使用條件中斷點與過濾。
  - 預防: 建立診斷處理器；為每次呼叫注入關聯性（Correlation ID）。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q1, B-Q6, A-Q23

---

### 學習路徑索引

- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 Microsoft Enterprise Library？
    - A-Q2: 什麼是 Policy Injection Application Block（PIAB）？
    - A-Q3: 為什麼需要 Policy Injection（而非手寫樣板碼）？
    - A-Q4: 什麼是 Call Handler（呼叫處理器）？
    - A-Q5: PIAB 的宣告式用法是什麼？
    - A-Q6: CAS 角色檢查與 PIAB 授權有何差異？
    - A-Q7: 什麼是橫切關注（Cross-Cutting Concerns）？
    - A-Q13: PIAB 內建有哪些常用處理器？
    - A-Q14: 何時該使用 Caching Handler？
    - A-Q15: 何時該使用 Logging Handler？
    - A-Q16: 何時使用 Exception Handling Handler？
    - A-Q17: 何謂 Performance Counter Handler 的價值？
    - A-Q18: 何時使用 Validation Handler？
    - A-Q24: PIAB 與手動插入樣板碼有何不同？
    - C-Q1: 如何以屬性快速為服務方法加入記錄？

- 中級者：建議學習哪 20 題
    - B-Q1: PIAB 攔截呼叫的基本機制如何運作？
    - B-Q2: 處理器的執行流程為何？
    - B-Q3: 如何決定與控制處理器順序（Order）？
    - B-Q4: AuthorizationCallHandler 的機制是什麼？
    - B-Q5: Caching Handler 如何決定快取鍵與命中？
    - B-Q6: Logging Handler 如何擷取輸入輸出？
    - B-Q7: Exception Handling Handler 背後機制？
    - B-Q8: Performance Counter Handler 如何運作？
    - B-Q9: Validation Handler 檢核流程為何？
    - B-Q10: PIAB 如何同時支援屬性與設定？
    - C-Q2: 如何為方法加入授權檢查？
    - C-Q3: 如何啟用 Caching Handler 加速昂貴查詢？
    - C-Q4: 如何以 Performance Counter 監控方法？
    - C-Q5: 如何在方法層加入輸入輸出驗證？
    - C-Q6: 如何應用 Exception Handling Handler 統一錯誤？
    - C-Q7: 何時使用 Wrap 而非 Create？如何實作？
    - C-Q9: 如何組合多個處理器並控制順序？
    - D-Q1: 為何加了屬性仍不生效（不進入處理器）？
    - D-Q4: 處理器順序錯誤導致語意不對怎麼辦？
    - D-Q5: 為何快取沒有命中或行為異常？

- 高級者：建議關注哪 15 題
    - A-Q21: 使用 PIAB 有哪些適用條件與限制？
    - A-Q23: 使用 PIAB 的潛在缺點與風險？
    - A-Q25: 宣告式與設定式套用策略的差異？
    - B-Q11: IMessage 與 IMessageSink 在此扮演什麼角色？
    - B-Q12: PolicyInjection.Create/Wrap 的代理建立細節？
    - B-Q13: 代理對型別與相等性的影響？
    - B-Q14: PIAB 與執行緒安全/Principal 的交互？
    - B-Q15: 處理器如何處理 out/ref 參數與回傳值？
    - B-Q16: 管線中例外的傳遞與處理規則？
    - B-Q17: 性能成本來源與量級？
    - B-Q18: PIAB 與裝飾器模式/動態代理比較？
    - B-Q19: 自訂 ICallHandler 的設計要點？
    - B-Q22: 宣告式與設定式合併時的衝突處理？
    - D-Q2: 為何代理攔截不到（型別限制導致）？
    - D-Q8: 代理造成型別/序列化或轉型問題怎麼辦？