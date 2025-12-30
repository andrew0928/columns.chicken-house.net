---
layout: synthesis
title: "API & SDK Design #3, API 的向前相容機制"
synthesis_type: faq
source_post: /2016/10/31/microservice5/
redirect_from:
  - /2016/10/31/microservice5/faq/
---

# API & SDK Design #3, API 的向前相容機制

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是向前相容（Forward Compatibility）？
- A簡: 新版 API 能與既有舊版 SDK 正常協作，避免升級中斷服務，確保穩定演進。
- A詳: 向前相容指新版 API 在發布後，仍能支援過去某時點以後的所有 SDK 版本。重點是新版不破壞舊客戶端既有行為，讓歷史版本 SDK 可繼續安全呼叫。它與「當下約定」不同，後者只保證同一時間點的 API/SDK 搭配，向前相容是跨時間的承諾。實踐關鍵在契約（contract）管控、明確版本識別與相容策略。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q10, B-Q5

A-Q2: API 與 SDK 的「當下約定」與「承諾」有何差異？
- A簡: 約定保證當下搭配可行；承諾保證新 API 對舊 SDK 持續可用，跨版本相容。
- A詳: 「當下約定」意指在同一批次發布時，API 與 SDK 對功能、介面、資料模型完全匹配，可立即互動；「承諾」則跨越時間，保證日後 API 升級後仍能讓既有 SDK 正常運作。前者關注同步版本；後者要求不可任意移除或更動既有介面，並需建立版本識別與相容性檢查，以避免舊用戶端在新環境下失效。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q10, B-Q7

A-Q3: 什麼是 API Contract？為何重要？
- A簡: 合約是 API 對外介面與資料規格的嚴格定義，用以約束雙方行為，避免破壞性變更。
- A詳: API Contract 定義可被呼叫的方法、路由、參數與資料結構（DTO）。它是 API 與 SDK 的共同依據，讓團隊在升級或重構時能清楚知道哪些元素不可破壞。若無契約，開發者可能在不自覺下修改介面造成不相容。透過契約與檢查工具（如 ActionFilter 或測試），能將「只增不減」的原則制度化，降低升級風險。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q2, C-Q1

A-Q4: WCF 與 ASP.NET Web API 在合約管控上的差異？
- A簡: WCF 天生以合約為中心；Web API 彈性高但需自建契約與檢查機制來強化約束。
- A詳: WCF 以 ServiceContract/DataContract 為核心，介面與資料契約天然強化編譯期約束；而 ASP.NET Web API 強調 REST 與路由彈性，原生不強制契約。於是需借助 interface 標記、ActionFilter、單元測試等方式在執行期或交付流程補上合約檢查，確保 API 對外規格受控且可追蹤變更。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q16, C-Q1

A-Q5: 為何 API 的版本管理比程式庫更複雜？
- A簡: API 面對多樣客戶端、長生命週期與跨網路契約，破壞性影響更廣、更難回收。
- A詳: 程式庫通常由內部掌控上下游相依；API 面向外部客戶端，使用版本分散、更新節奏不一，且網路介面一旦破壞難以立即修復。API 必須兼顧全球唯一服務端點、長期營運、舊客戶端兼容與升級路徑，因此需要清晰的版本策略、契約治理與雙端檢查，成本與複雜度均高於一般庫。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, A-Q9, B-Q17

A-Q6: 什麼是相容性版本策略（Compatible Versioning）？
- A簡: 僅保留最新 API 版本，承諾對舊 SDK 保持相容；以小步擴充避免破壞。
- A詳: Compatible Versioning 主張服務端只保留最新版，但嚴守相容性原則，使過去發布的 SDK 仍能正常運作。它能降低多版本維護成本，同時以「只增不減」維持向前相容。關鍵是契約管控、清楚的版本號意義（Major/Minor）與嚴謹的廢止政策，避免不當移除造成舊客戶端中斷。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, A-Q8, B-Q17

A-Q7: 什麼是無版本策略（The Knot）？風險是什麼？
- A簡: 不標示版本、永遠只有最新；若無相容保證，升級易導致舊客戶端壞掉。
- A詳: 無版本策略即不暴露版本，服務端永遠只提供當前實作。優點是簡潔、無需協商；缺點是若缺乏嚴格的向前相容治理，任何改動都有可能立即破壞舊客戶端。除非同時採嚴謹相容原則與自動化檢查，否則建議慎用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q17, D-Q5

A-Q8: 什麼是點對點版本策略（Point-to-Point）？
- A簡: 多版本並存，客戶端選其一。維護成本高，但升級風險較低且可逐步遷移。
- A詳: P2P 策略讓多個 API 版本同時提供，客戶端指定要用的版本。好處是升級可控且逐步；壞處是服務端要維護多條分支，測試與營運成本高。相較之下，相容性版本策略用治理換維運成本，P2P 用多版本維運換低升級風險。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q17, D-Q8

A-Q9: 為什麼只保留最新版仍須保證向前相容？
- A簡: 單一版本降低維運，但若不相容，舊客戶端即斷線；相容性是存續關鍵。
- A詳: 保留最新版有助於集中資源與降低分歧，但外部 SDK 可能數月不更新。若新版 API 破壞舊行為，將直接導致大量用戶端失效。向前相容提供穩定升級階梯，讓舊版能運作，新版能擴充，兼顧效率與可持續演進。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q7, D-Q6

A-Q10: 在相容策略下的核心原則是什麼？
- A簡: 介面與參數只增不減；既有定義不改義、不移除，必要時標示廢止過渡。
- A詳: 核心原則是「只增不減」。已公開的端點、方法、參數與資料欄位不能移除或改義；新增功能以新增欄位或端點實現。若必須淘汰，用 [Obsolete] 或對應標示與公告期，於下一次 Major 才移除。透過此原則，舊 SDK 得以繼續運作，新 SDK 能用到新能力。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q7, B-Q15

A-Q11: Major/Minor/Build/Revision 各代表什麼？
- A簡: Major 不相容、Minor 相容擴充、Build 重編譯、Revision 完全可互換之修補。
- A詳: Major 表重大不相容改版；Minor 表相容性增強；Build 代表同一來源在不同編譯環境/參數的重編譯；Revision 則是完整相容的修補（如安全修正）。相容性檢查常以 Major 相等、伺服端 Minor ≥ 客戶端要求為基準。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q11, B-Q10, C-Q7

A-Q12: 何時調升 Major？何時調升 Minor？
- A簡: 破壞性改動升 Major；相容擴充升 Minor；修補與重編譯用 Build/Revision。
- A詳: 若移除/改義既有介面或無法保證舊 SDK 正常，須調升 Major。若只是新增端點、參數或欄位且不影響既有呼叫，調升 Minor。修補漏洞或重編譯則更新 Build/Revision。這套規則支撐自動化檢查與升級決策，避免意外破壞。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q7, D-Q8

A-Q13: Build 與 Revision 在 API 治理中的角色？
- A簡: 兩者不影響介面相容，常用於重編譯與安全修補，利於追蹤交付。
- A詳: Build 多代表同源重編譯（環境、平台、編譯器差異）；Revision 代表可完全互換的修補（例如安全修正）。在相容性判斷中通常不納入比較，但對追蹤出貨、定位回歸問題與稽核變更相當重要，建議由 CI/CD 自動帶入。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q11, B-Q18, C-Q6

A-Q14: 何謂 API 廢止（Deprecation）與 [Obsolete]？
- A簡: 廢止是計畫性淘汰；以標示與公告期提示遷移，待下次 Major 才移除。
- A詳: 當某介面需移除，應先標記為 [Obsolete] 或給予明確的 deprecation 訊息，提供替代方案與時間表。保留舊介面至下一個 Major 版本，讓用戶端有充裕時間遷移。此流程能避免突發中斷，維持相容與信任。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q15, D-Q8

A-Q15: 為何版本識別機制是關鍵？
- A簡: 無法識別版本，就無從比較相容，亦難以精準回報與防止誤用。
- A詳: 版本識別讓 SDK 能知悉 API 現況，伺服端能理解客戶端需求，再據以檢查或協商。常見做法包含：提供版本查詢端點（如 OPTIONS）、在回應夾帶版本資訊、以 Header 傳遞 SDK 要求版本等。它是自動化相容檢查與錯誤回饋的前提。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, B-Q8, C-Q3

A-Q16: 為什麼 SDK 初始化時要檢查 API 版本？
- A簡: 及早失敗，避免在關鍵業務流程中才發現不相容，縮短排錯時間。
- A詳: 初始化就檢查可立刻發現不相容版本，讓應用程式選擇降級、切換端點或提示用戶更新。這對長流程或批次任務尤為重要，可避免浪費資源與造成資料不一致。若 SDK 生命週期很長，仍應搭配每次請求的伺服端檢查。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q6, D-Q1

A-Q17: 為什麼每次 API 呼叫也要檢查版本？
- A簡: 應對長生命週期 SDK 與動態升級，確保每一請求都在安全版本範圍內。
- A詳: 某些 SDK 客體可能長期駐留（如 static 單例），初始化版本可能已過時。於是每次請求附帶 SDK 要求版本，由伺服端以 ActionFilter 實時檢查，可防止在服務端已升級後仍用舊假設執行，保障一致性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q5, D-Q6

A-Q18: 為何執行期（runtime）契約檢查仍有價值？
- A簡: 編譯期難覆蓋路由/反射/設定等動態面向，執行期可補強防線。
- A詳: Web API 設計常含路由、屬性、設定檔與反射等動態行為，僅靠編譯期無法完全保障外部契約。執行期利用 ActionFilter 檢查 controller 是否實作契約介面、方法存在與簽章規範，可在發佈前透過整合測試或運行中把關，降低風險。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q1, B-Q13, C-Q1

A-Q19: 為何要管控 API 規格修改權責與版控紀錄？
- A簡: 明確授權與可追溯，避免無意破壞；變更留痕，回溯與稽核更可行。
- A詳: 將契約異動納入版控與權限管理，可限制只有負責人能修改規格，並留下差異紀錄（如 PR、變更單）。當事故發生可迅速定位來源，亦便利回滾與還原討論脈絡。這是大型團隊、長期營運下的基礎治理能力。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q18, D-Q4, D-Q5

A-Q20: 單元測試能當作契約嗎？限制是什麼？
- A簡: 可作保障但非完美；測試變更不必然等同規格變更，追蹤粒度較粗。
- A詳: 使用測試描述預期行為是有效的「活文件」。然而測試修正可能反映測試錯誤而非規格改動，故難作為唯一的契約來源。建議「契約介面 + 測試」雙保險：介面作規格源頭，測試驗證行為一致，並透過 CI 強制執行。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q19, C-Q10, D-Q3

A-Q21: API 介面契約與資料契約（DTO）有何不同？
- A簡: 介面契約定義可呼叫的方法與路由；資料契約定義輸入輸出結構與欄位。
- A詳: 介面契約聚焦「能呼叫什麼與怎麼呼叫」；資料契約關注「資料長什麼樣」。兩者一體兩面：只增不減原則同時適用，才能保證舊 SDK 序列化/反序列化與端點呼叫皆不破壞。資料契約常以可序列化類別維護。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, B-Q25, A-Q10

A-Q22: 什麼是 ActionFilter？在相容性中扮演什麼角色？
- A簡: ActionFilter 於執行管線前後插入邏輯；可實作契約檢查與版本校驗。
- A詳: 在 ASP.NET Web API，ActionFilter 可攔截每次動作執行，便於統一實作前置檢查，如：確認 controller 實作契約、方法存在、從 Header 讀取 SDK 版本並比較伺服端版本等。它將相容性策略集中化、免重複且易於測試與維護。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q6, C-Q5

A-Q23: 為何用 HTTP Header 傳送 SDK 需求版本？
- A簡: Header 不汙染業務負載，便於基礎建設攔截、日誌化與版本協商。
- A詳: 以 Header（如 X-SDK-REQUIRED-VERSION）承載版本，不影響既有 payload 與路由語意。伺服端可在 ActionFilter 或 Gateway 層快速讀取判斷，亦便於記錄與風險分析。相較於放在 body，Header 更適合用於協商與控制訊息。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q8, B-Q9, C-Q4

A-Q24: 長生命週期的 SDK Client 有何風險？
- A簡: 初始檢查過期、服務端已升級而未再驗；易造成隱性不相容。
- A詳: 若 SDK Client 存活數月（如單例緩存），只在建構時檢查版本會失去時效。服務端升級後，舊假設可能不成立。故需每次請求由伺服端再檢查，或在 SDK 內週期性重握手，確保任何時刻皆在安全相容範圍內。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q17, B-Q6, D-Q6

A-Q25: 什麼是版本相容性政策？包含哪些面向？
- A簡: 對支援範圍與檢查時機的正式規則，包括約束、識別與檢查流程。
- A詳: 版本相容性政策包含：契約治理（誰可改、如何審）、版本號規則（Major/Minor 等）、版本識別（端點、Header）、檢查時機（初始化/每次請求）、錯誤回報格式、廢止流程與公告策略。政策落地才能長期維運而不失控。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q17, B-Q18, D-Q5

---

### Q&A 類別 B: 技術原理類

B-Q1: ContractCheckActionFilter 如何運作？
- A簡: 於執行前反射查找契約介面與方法，若未定義或不匹配即拒絕執行。
- A詳: 技術原理說明：ActionFilter 在 OnActionExecuting 時取得 Controller Type，反射其介面集合找出實作 IApiContract 的介面，進一步比對當前 Action 名稱是否存在於契約方法集中。關鍵步驟或流程：反射尋找契約介面→方法存在性檢查→不符合則擲出 NotSupportedException。核心組件介紹：IApiContract 標記介面、具體契約介面（如 IBirdsApiContract）、ContractCheckActionFilter。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, A-Q22, C-Q1

B-Q2: 如何在執行期比對 Controller 與契約介面？
- A簡: 透過反射列舉介面與方法名稱，對應當前 Action 名稱是否存在。
- A詳: 技術原理說明：利用 Type.GetInterfaces() 與 Interface.GetMethods() 取得方法清單，將 ActionDescriptor.ActionName 與方法名比對。關鍵步驟或流程：取得 Controller Type→列舉介面→篩選實作 IApiContract→列舉方法→名稱比對→擲例外。核心組件介紹：HttpActionContext、ActionDescriptor、反射 API。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, C-Q1, D-Q3

B-Q3: 如何設計 IApiContract 與 IBirdsApiContract？
- A簡: 以 IApiContract 為標記，IBirdsApiContract 列出公開行為以供雙端對照。
- A詳: 技術原理說明：定義空的 IApiContract 作為契約標記，所有契約介面繼承它；IBirdsApiContract 寫明可公開的 Action 簽章。關鍵步驟或流程：定義標記介面→為每組 API 設專屬契約→Controller 實作契約→Filter 檢查。核心組件介紹：IApiContract、IBirdsApiContract、BirdsController。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, C-Q2, C-Q1

B-Q4: 如何以 OPTIONS 端點回傳 API 版本？
- A簡: 新增 Options 方法回傳版本字串，供 SDK 初始化取得版本資訊。
- A詳: 技術原理說明：在契約與 Controller 增加 Options()，回傳版本字串。SDK 以 HttpClient 發送 OPTIONS /api/birds 取得。關鍵步驟或流程：契約新增 Options→Controller 實作→SDK 呼叫→解析版本。核心組件介紹：HttpClient、HttpRequestMessage、Options 方法。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q15, C-Q3, B-Q11

B-Q5: SDK 初始化的版本檢查流程是什麼？
- A簡: 取得伺服端版本→解析為 Version→比對 Major/Minor→不相容即失敗。
- A詳: 技術原理說明：SDK 建構時請求版本資訊，轉為 System.Version，比較規則為 Major 相等且伺服端 Minor ≥ 需求 Minor。關鍵步驟或流程：發送 OPTIONS→解析→比較→擲例外或繼續。核心組件介紹：System.Version、HttpClient、例外處理（InvalidOperationException）。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q16, A-Q11, C-Q7

B-Q6: 每次請求時的伺服端版本檢查如何進行？
- A簡: SDK Header 帶出需求版本；伺服端 Filter 取 Header 與自身版本比對。
- A詳: 技術原理說明：SDK 於 DefaultRequestHeaders 加上 X-SDK-REQUIRED-VERSION。伺服端 ActionFilter 讀 Header，與 Assembly 版本比對。關鍵步驟或流程：設定 Header→Filter 取值→GetName().Version→比對→擲例外。核心組件介紹：HttpRequestHeaders、ActionFilterAttribute、AssemblyName.Version。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q17, C-Q4, C-Q5

B-Q7: SDK 需求版本與伺服端實際版本的比對規則？
- A簡: Major 必須相等；伺服端 Minor 不得小於 SDK 需求 Minor。
- A詳: 技術原理說明：以 System.Version 比較，若 Major 不相等視為不相容；若伺服端 Minor < 需求 Minor 亦不相容。Build/Revision 不參與相容判定。關鍵步驟或流程：解析→比較→判定→擲例外。核心組件介紹：System.Version.Compare 操作或屬性比較。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, A-Q12, C-Q7

B-Q8: 如何用 HTTP Header 傳遞 X-SDK-REQUIRED-VERSION？
- A簡: SDK 設定 DefaultRequestHeaders.Add，所有請求皆自動附帶版本需求。
- A詳: 技術原理說明：在 SDK 建構後，對 HttpClient.DefaultRequestHeaders.Add("X-SDK-REQUIRED-VERSION", version)。關鍵步驟或流程：建立 HttpClient→設定 BaseAddress→加入 Header→後續所有 API 呼叫自動帶出。核心組件介紹：HttpClient、HttpRequestHeaders。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q23, C-Q4, B-Q6

B-Q9: ActionFilter 中如何讀取請求 Header？
- A簡: 由 HttpActionContext.Request.Headers.GetValues 取得鍵值集合解析。
- A詳: 技術原理說明：在 OnActionExecuting 中，使用 actionContext.Request.Headers.GetValues("X-SDK-REQUIRED-VERSION") 取得字串，再 new Version。關鍵步驟或流程：取得 Headers→取值→解析→判定。核心組件介紹：HttpActionContext、HttpRequestMessage、System.Version。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, C-Q5, D-Q9

B-Q10: 如何於伺服端取得 Assembly 的版本號？
- A簡: 以 this.GetType().Assembly.GetName().Version 讀取執行組件版本。
- A詳: 技術原理說明：反射目前執行中的組件名稱，再取 Version 欄位。關鍵步驟或流程：取得 Type→Assembly→AssemblyName→Version。核心組件介紹：System.Reflection、AssemblyName、Version。此值可由 AssemblyInfo.cs 的 AssemblyVersion 設定或 CI 注入。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q11, C-Q6, A-Q13

B-Q11: 如何設定 AssemblyVersion 與自動 Build/Revision？
- A簡: 在 AssemblyInfo.cs 指定 Major.Minor.*，由 MSBuild 自動補 Build/Revision。
- A詳: 技術原理說明：設定 [assembly: AssemblyVersion("10.26.*")]，編譯時工具自動產生 Build/Revision。關鍵步驟或流程：變更 AssemblyInfo→CI/CD 注入或覆寫→編譯→產出一致版本。核心組件介紹：AssemblyVersion、AssemblyFileVersion、MSBuild/CI。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q6, A-Q11, A-Q13

B-Q12: Web API 如何將例外轉為 JSON 回傳？
- A簡: 內建例外處理會序列化為錯誤 JSON，包含訊息、型別與堆疊追蹤。
- A詳: 技術原理說明：ASP.NET Web API 的全域管線會捕捉未處理例外，透過預設格式器輸出 JSON 錯誤結構。關鍵步驟或流程：例外拋出→管線攔截→格式化→回傳。核心組件介紹：ExceptionHandler、MediaTypeFormatter、JSON 格式化器。可自訂以返回一致錯誤碼與相容提示。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q2, C-Q5, B-Q22

B-Q13: 如何快取契約檢查結果以提升效能？
- A簡: 將反射出的介面與方法對應緩存，僅首次計算，其後直接查表。
- A詳: 技術原理說明：反射昂貴，可在應用啟動或首次請求時，建立 Controller→契約→方法對應表，存放於 ConcurrentDictionary。關鍵步驟或流程：首次掃描→存入快取→後續檢查走快取→部署變更時清空或版本化。核心組件介紹：Memory cache、ConcurrentDictionary、啟動鉤子。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q18, C-Q8, D-Q3

B-Q14: 不相容時 SDK 應如何處理例外？
- A簡: 以明確例外類型與訊息快速失敗，並提供替代動作或升級指引。
- A詳: 技術原理說明：SDK 在初始化或呼叫時，接獲版本不相容應擲封裝例外（含伺服端版本、需求版本、建議行動）。關鍵步驟或流程：捕捉 Http 例外→解析錯誤 JSON→轉換為 SDK 層例外→上拋。核心組件介紹：自訂 Exception 型別、錯誤碼、重試/降級策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q1, D-Q2, C-Q7

B-Q15: 如何用 [Obsolete] 管理過渡期？
- A簡: 在將移除前以 [Obsolete] 標示，提供替代與期限，待下一 Major 真正移除。
- A詳: 技術原理說明：為即將淘汰的端點或方法加上 [Obsolete("use X by YYYY-MM")], 使編譯器警示。關鍵步驟或流程：標示→公告→觀測→於 Major 移除。核心組件介紹：ObsoleteAttribute、公告/版本說明、監控。此法讓兼容與演進可並行。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q14, D-Q8, C-Q9

B-Q16: 版本識別 API 應如何設計（OPTIONS/HEAD/端點）？
- A簡: 可用 OPTIONS/HEAD 或 /version 端點，重點是輕量、穩定且易於快取。
- A詳: 技術原理說明：OPTIONS/HEAD 適合無副作用查詢；也可提供 /api/version 端點回傳版本與能力。關鍵步驟或流程：選擇方法→定義回傳格式→實作→文件化。核心組件介紹：HttpMethod.Options/Head、自定路由、回應快取策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, A-Q15, C-Q3

B-Q17: 三種版本策略的架構影響比較？
- A簡: 無版本簡單但高風險；P2P 安全但成本高；相容策略平衡維運與演進。
- A詳: 技術原理說明：The Knot 依賴嚴格相容治理才可用；P2P 需多版本路由、資料庫與測試矩陣；相容策略用單版本加嚴格合約與檢查。關鍵步驟或流程：選策略→治理落地→監控與回饋。核心組件介紹：路由版本化、契約檢查、CI/CD 門檻。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q6, A-Q7, A-Q8

B-Q18: 如何把版本與權限治理整合到 CI/CD？
- A簡: 以 PR/審核守門、合規掃描與自動測試，限制未授權契約改動。
- A詳: 技術原理說明：在 CI 執行契約比對、API 測試與版本規則檢查，PR 需通過守門人與自動化檢查才可合併。關鍵步驟或流程：提交→自動檢查→人工審核→版本號管理→發布。核心組件介紹：Git Hooks、Pipeline、版本產生器、權限控制。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q19, D-Q5, C-Q6

B-Q19: 如何以測試表達 API 規格（Contract Tests）？
- A簡: 以端對端測試固定輸入/輸出與狀態碼，防止行為回歸與不兼容。
- A詳: 技術原理說明：撰寫覆蓋公開端點的測試，固定資料夾/JSON 模板，斷言狀態碼、欄位存在與不變契約。關鍵步驟或流程：設計用例→資料夾→斷言→CI 強制執行。核心組件介紹：整合測試框架、快照測試、契約報表。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q20, C-Q10, D-Q3

B-Q20: 如何避免編譯期無法保障的改動？
- A簡: 以執行期檢查、路由限制與靜態分析，彌補反射/屬性/設定面向。
- A詳: 技術原理說明：編譯期無法覆蓋路由/屬性等動態面，需以 ActionFilter、靜態分析（Roslyn 分析器）、部署前契約比對工具補強。關鍵步驟或流程：設計規範→工具落地→CI 檢查。核心組件介紹：Filter、分析器、契約比對器。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q18, B-Q1, B-Q13

B-Q21: 契約如何同時約束 SDK 與 Server？
- A簡: 契約介面讓 Server 實作；SDK 以此作為功能映射與檢查依據。
- A詳: 技術原理說明：共享一份契約定義（或生成 SDK 端映射），Server 實作契約；SDK 依契約建立呼叫封裝與校驗。關鍵步驟或流程：契約定義→雙端同步→檢查/測試。核心組件介紹：介面定義、SDK 映射、生成器。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, C-Q2, C-Q7

B-Q22: 版本錯誤的錯誤碼與訊息應如何設計？
- A簡: 提供一致錯誤碼、伺服端/需求版本與建議動作，便於用戶與監控理解。
- A詳: 技術原理說明：定義專屬錯誤碼（如 API_VERSION_INCOMPATIBLE），回傳 current/required version 與升級指引 URL。關鍵步驟或流程：統一錯誤格式→全域處理→文件對齊。核心組件介紹：ExceptionHandler、中介軟體、標準錯誤結構（RFC7807 類似）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q2, B-Q12, C-Q7

B-Q23: 伺服端能否依 SDK 版本調整行為（協商）？
- A簡: 可根據 Header 做回應降級或欄位裁剪，但仍須遵守契約與監控。
- A詳: 技術原理說明：讀取需求版本，若低版本則回傳兼容格式或關閉新欄位。關鍵步驟或流程：讀 Header→版本判斷→選擇回應模板/策略。核心組件介紹：版本策略器、回應模板、功能旗標。需謹慎避免邏輯分叉失控。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q17, D-Q3, C-Q5

B-Q24: 如何追蹤契約異動與變更紀錄？
- A簡: 契約專案獨立版控，變更走 PR 與審核，生成 Changelog 與公告。
- A詳: 技術原理說明：將契約獨立專案化，任何變更開 PR，經自動檢查與守門人審核；發布時產出變更日誌與公告。關鍵步驟或流程：PR→檢查→審核→版本標記→公告。核心組件介紹：Git、語意化版本、產生器。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q19, B-Q18, D-Q5

B-Q25: 如何讓資料契約（DTO）保持向前相容？
- A簡: 僅新增欄位，不移除或改義；反序列化預設值與忽略未知欄位。
- A詳: 技術原理說明：以可選欄位新增能力，避免 Breaking Change；客戶端序列化設定忽略未知欄位，伺服端為缺漏欄位給合理預設。關鍵步驟或流程：欄位新增→預設策略→兼容測試。核心組件介紹：JSON Serializer 設定、後相容策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q21, C-Q10, D-Q2

---

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何在 Web API 實作契約標記與執行期檢查？
- A簡: 定義 IApiContract 與專屬契約介面，寫 ActionFilter 反射比對方法。
- A詳: 實作步驟：1) 定義 IApiContract 標記介面；2) 為每組 API 建立契約介面（如 IBirdsApiContract）；3) Controller 實作契約；4) 撰寫 ContractCheckActionFilter 在 OnActionExecuting 反射比對方法名。程式碼片段：controller.GetType().GetInterfaces()→GetMethods() 比對。注意事項：加上快取、覆蓋率測試，避免反射開銷與漏網之魚。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q2, A-Q3

C-Q2: 如何實作 IBirdsApiContract 與 BirdsController？
- A簡: 在契約列出公開方法簽章，Controller 實作並受 Filter 檢查。
- A詳: 實作步驟：1) 建 IBirdsApiContract：Head(), Get(), Get(string id), Options()；2) BirdsController : ApiController, IBirdsApiContract；3) 以 [ContractCheckActionFilter] 套用檢查。程式碼片段：interface IBirdsApiContract { IEnumerable<BirdInfo> Get(); }。注意：契約是唯一來源；新增行為先加到契約再實作。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, A-Q21, C-Q1

C-Q3: 如何讓 SDK 以 OPTIONS 取得 API 版本？
- A簡: 建 Options 端點回傳版本字串，SDK 用 HttpClient 呼叫並解析 Version。
- A詳: 實作步驟：1) 契約/Controller 增加 Options(){ return "10.26.0.0"; }；2) SDK 建構時發送 HttpMethod.Options 至 /api/birds；3) JsonConvert.DeserializeObject<string>() 解析；4) new Version(字串)。程式碼片段：_http.SendAsync(new HttpRequestMessage(HttpMethod.Options,"/api/birds")).注意事項：錯誤處理與超時、端點文件化。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, A-Q15, B-Q5

C-Q4: 如何在 SDK 預設加入 X-SDK-REQUIRED-VERSION Header？
- A簡: 建立 HttpClient 後於 DefaultRequestHeaders.Add 加入版本字串。
- A詳: 實作步驟：1) _http = new HttpClient { BaseAddress = url }; 2) var v = new Version(10,0,0,0); 3) _http.DefaultRequestHeaders.Add("X-SDK-REQUIRED-VERSION", v.ToString()); 程式碼片段：DefaultRequestHeaders.Add(...). 注意事項：Header 名稱統一、避免重複加入、版本來源集中管理。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, B-Q6, A-Q23

C-Q5: 如何在伺服端以 ActionFilter 檢查版本並擲例外？
- A簡: 讀取 Header 需求版本，對比 Assembly 版本，違規則擲 InvalidOperationException。
- A詳: 實作步驟：1) OnActionExecuting 取 Headers.GetValues("X-SDK-REQUIRED-VERSION"); 2) 解析 new Version；3) var current = this.GetType().Assembly.GetName().Version; 4) 規則：Major 相等、Minor ≥；5) 否則擲例外。程式碼片段：if (cur.Major!=req.Major || cur.Minor<req.Minor) throw new InvalidOperationException(); 注意：統一錯誤碼與訊息，便於 SDK 解析。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q10, B-Q22

C-Q6: 如何設定 AssemblyVersion 讓 Build/Revision 自動化？
- A簡: 在 AssemblyInfo 設定 "Major.Minor.*"，由 CI/MSBuild 自動注入數字。
- A詳: 實作步驟：1) AssemblyInfo.cs： [assembly: AssemblyVersion("10.26.*")]; 2) CI 設定版本來源（日期/流水號）；3) 打包時一致性校驗。程式碼片段：AssemblyVersion/AssemblyFileVersion。注意：避免手工修改；發版時產出對映表，便於追蹤。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q11, A-Q13, B-Q18

C-Q7: 如何在 SDK 初始化比較版本並安全失敗？
- A簡: 取回伺服端版本，比對規則不符即擲自訂例外，提供用戶端指引。
- A詳: 實作步驟：1) 取得版本（OPTIONS 或健康端點）；2) new Version 比較 Major/Minor；3) 不相容擲 ApiVersionIncompatibleException（含 current/required）；4) 呼叫端捕捉後採取升級/切換/降級策略。程式碼片段：if (req.Major!=cur.Major || req.Minor>cur.Minor) throw new ApiVersionIncompatibleException(...); 注意：訊息清楚、可記錄。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q14, B-Q22

C-Q8: 如何快取契約反射結果以降低 ActionFilter 開銷？
- A簡: 以 ConcurrentDictionary 快取 Controller→方法集合，首次建立後重用。
- A詳: 實作步驟：1) 建立靜態 ConcurrentDictionary<Type, HashSet<string>>；2) 若無快取則反射介面/方法並加入；3) 檢查時直接 Contains；4) 若部署變更可利用 AppDomain 重啟或版本鍵清空。程式碼片段：cache.GetOrAdd(type, BuildMethodSet); 注意事項：避免記憶體洩漏，控制鍵空間。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q13, A-Q18, D-Q3

C-Q9: 如何標記與移除將廢止的 API？
- A簡: 以 [Obsolete] 標示與公告期，監控使用後於下一 Major 正式移除。
- A詳: 實作步驟：1) 在方法上加 [Obsolete("Use X, removal in vNextMajor")]；2) 文件與版本說明公告；3) 以日誌觀測流量；4) 下一次 Major 刪除程式與路由映射。程式碼片段：[Obsolete("...")]。注意：提供替代方案，預留遷移週期。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q15, A-Q14, D-Q8

C-Q10: 如何用測試建立 API 規格防護網？
- A簡: 以端對端契約測試驗證狀態碼與必備欄位，防止不兼容變更進入主幹。
- A詳: 實作步驟：1) 為各端點撰寫測試（必備欄位存在、未知欄位忽略）；2) 建立快照或 JSON Schema；3) CI 中強制執行；4) 不通過不得合併。程式碼片段：Assert.Contains("BirdInfo", json); 注意：測試為輔助，不取代契約源頭。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q19, A-Q20, D-Q3

---

### Q&A 類別 D: 問題解決類（10題）

D-Q1: SDK 初始化拋 InvalidOperationException 怎麼辦？
- A簡: 代表版本不相容；檢視 current/required，比對 Major/Minor 後升級或降級。
- A詳: 問題症狀：SDK 建構時立即失敗。可能原因：伺服端 Major 與 SDK 不同，或伺服端 Minor 小於需求。解決步驟：1) 讀錯誤訊息與版本；2) 升級 SDK 或切換相容伺服端；3) 臨時關閉新功能旗標。預防：初始化檢查、明確錯誤碼、版本公告機制。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, B-Q7, C-Q7

D-Q2: 呼叫 API 得到 JSON 錯誤回應，如何診斷版本問題？
- A簡: 解析錯誤 JSON 的訊息與堆疊，若為版本錯誤依提示升級或調整。
- A詳: 問題症狀：回應 JSON 含 ExceptionMessage/Type。可能原因：伺服端 ActionFilter 判定版本不符或契約缺失。解決步驟：1) 解析錯誤 JSON；2) 比對版本；3) 調整 SDK Header 或升級；4) 伺服端統一錯誤碼。預防：制定標準錯誤結構與文件化。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, B-Q22, C-Q5

D-Q3: 契約檢查導致延遲上升，如何優化？
- A簡: 反射結果快取、僅首次計算；以整合測試補充，減少執行期負擔。
- A詳: 問題症狀：高 QPS 下 CPU 飆高。原因：每請求反射檢查昂貴。解決步驟：1) 加入快取；2) 啟動時預載；3) 減少方法名比對成本；4) 搭配契約測試降低執行期檢查強度。預防：基準測試與快取策略設計。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q13, C-Q8, B-Q19

D-Q4: 多團隊修改導致破壞性變更，如何防堵？
- A簡: 權限管控、PR 守門與自動化契約比對，未通過者不可合併。
- A詳: 症狀：上線後舊 SDK 大量失效。原因：缺乏變更治理。解法：1) 契約專案獨立；2) PR 審核與自動檢查（版本規則、契約差異）；3) 強制升 Major 或標示 [Obsolete]；4) 發布前公告。預防：版本策略與 CI Gate 落地。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q19, B-Q18, B-Q24

D-Q5: API 版本號管理混亂，如何建立流程？
- A簡: 明定語意化規則、版本來源單一、CI 自動注入並產生變更日誌。
- A詳: 症狀：版本跳動、不可追溯。原因：手工管理、缺乏規則。解法：1) 定義 Major/Minor/Build/Revision；2) CI 產生與統一；3) 變更日誌與公告；4) 偵測不相容變更需升 Major。預防：守門人制度與自動化校驗。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q11, B-Q24

D-Q6: 長期存活的 SDK Client 造成隱性不相容，如何處理？
- A簡: 每請求伺服端檢查或週期性重握手；必要時在 SDK 加入自我更新提示。
- A詳: 症狀：久未重啟服務的客戶端偶發錯誤。原因：僅初始化檢查。解法：1) 伺服端 Filter 每請求檢查；2) SDK 定期重新驗證版本；3) 發出升級警示。預防：文件強調生命週期與檢查機制。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q17, B-Q6, C-Q4

D-Q7: Build/Revision 差異導致誤判，如何避免？
- A簡: 相容性只比較 Major/Minor；Build/Revision 僅作追蹤，不參與判斷。
- A詳: 症狀：同一功能因重編譯被視為不相容。原因：比較包含了 Build/Revision。解法：調整檢查規則只比較 Major/Minor。預防：在程式與文件明確定義比較準則，並於測試與 CI 檢核。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, B-Q7, C-Q7

D-Q8: 必須移除舊 API 時如何兼顧相容與進度？
- A簡: 先標示廢止與公告期限，提供替代端點，於下一 Major 移除並監控。
- A詳: 症狀：技術債拖累進度。原因：歷史端點累積。解法：1) [Obsolete] 與公告計畫；2) 替代方案與遷移指南；3) 監控使用量下降；4) 下一 Major 移除。預防：制定廢止政策與時程表。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q15, C-Q9

D-Q9: 有些 SDK 忽略 Header 未帶版本，伺服端怎辦？
- A簡: 設定保守預設需求版本或拒絕請求，並回傳清楚錯誤與指引。
- A詳: 症狀：伺服端無法判斷相容。原因：SDK 未帶 Header。解法：1) 伺服端為舊客戶端設最低支援版本；2) 或直接 400/409 回應要求帶 Header；3) 文件與範本修正。預防：SDK 模板統一注入 Header。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, B-Q22, C-Q4

D-Q10: 緊急安全修補如何兼顧相容性？
- A簡: 以 Revision 發布可互換修補；避免更動介面，必要時提供旗標開關。
- A詳: 症狀：需立即修補漏洞。原因：安全問題。解法：1) 僅變更內部實作，維持契約；2) 提升 Revision；3) 功能旗標控制風險；4) 快速回滾機制。預防：安全測試與藍綠/金絲雀發布。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q13, B-Q11, B-Q18

---

### 學習路徑索引

- 初學者：建議先學習 15 題
    - A-Q1: 什麼是向前相容（Forward Compatibility）？
    - A-Q2: API 與 SDK 的「當下約定」與「承諾」有何差異？
    - A-Q3: 什麼是 API Contract？為何重要？
    - A-Q5: 為何 API 的版本管理比程式庫更複雜？
    - A-Q6: 什麼是相容性版本策略（Compatible Versioning）？
    - A-Q9: 為什麼只保留最新版仍須保證向前相容？
    - A-Q10: 在相容策略下的核心原則是什麼？
    - A-Q11: Major/Minor/Build/Revision 各代表什麼？
    - A-Q12: 何時調升 Major？何時調升 Minor？
    - B-Q4: 如何以 OPTIONS 端點回傳 API 版本？
    - B-Q5: SDK 初始化的版本檢查流程是什麼？
    - B-Q8: 如何用 HTTP Header 傳遞 X-SDK-REQUIRED-VERSION？
    - C-Q3: 如何讓 SDK 以 OPTIONS 取得 API 版本？
    - C-Q4: 如何在 SDK 預設加入 X-SDK-REQUIRED-VERSION Header？
    - D-Q1: SDK 初始化拋 InvalidOperationException 怎麼辦？

- 中級者：建議學習 20 題
    - A-Q14: 何謂 API 廢止（Deprecation）與 [Obsolete]？
    - A-Q15: 為何版本識別機制是關鍵？
    - A-Q16: 為什麼 SDK 初始化時要檢查 API 版本？
    - A-Q17: 為什麼每次 API 呼叫也要檢查版本？
    - A-Q22: 什麼是 ActionFilter？在相容性中扮演什麼角色？
    - A-Q23: 為何用 HTTP Header 傳送 SDK 需求版本？
    - B-Q1: ContractCheckActionFilter 如何運作？
    - B-Q6: 每次請求時的伺服端版本檢查如何進行？
    - B-Q7: SDK 需求版本與伺服端實際版本的比對規則？
    - B-Q10: 如何於伺服端取得 Assembly 的版本號？
    - B-Q11: 如何設定 AssemblyVersion 與自動 Build/Revision？
    - B-Q12: Web API 如何將例外轉為 JSON 回傳？
    - B-Q19: 如何以測試表達 API 規格（Contract Tests）？
    - C-Q1: 如何在 Web API 實作契約標記與執行期檢查？
    - C-Q2: 如何實作 IBirdsApiContract 與 BirdsController？
    - C-Q5: 如何在伺服端以 ActionFilter 檢查版本並擲例外？
    - C-Q6: 如何設定 AssemblyVersion 讓 Build/Revision 自動化？
    - C-Q7: 如何在 SDK 初始化比較版本並安全失敗？
    - D-Q2: 呼叫 API 得到 JSON 錯誤回應，如何診斷版本問題？
    - D-Q5: API 版本號管理混亂，如何建立流程？

- 高級者：建議關注 15 題
    - A-Q18: 為何執行期（runtime）契約檢查仍有價值？
    - A-Q19: 為何要管控 API 規格修改權責與版控紀錄？
    - A-Q25: 什麼是版本相容性政策？包含哪些面向？
    - B-Q13: 如何快取契約檢查結果以提升效能？
    - B-Q17: 三種版本策略的架構影響比較？
    - B-Q18: 如何把版本與權限治理整合到 CI/CD？
    - B-Q20: 如何避免編譯期無法保障的改動？
    - B-Q21: 契約如何同時約束 SDK 與 Server？
    - B-Q22: 版本錯誤的錯誤碼與訊息應如何設計？
    - B-Q23: 伺服端能否依 SDK 版本調整行為（協商）？
    - B-Q24: 如何追蹤契約異動與變更紀錄？
    - B-Q25: 如何讓資料契約（DTO）保持向前相容？
    - C-Q8: 如何快取契約反射結果以降低 ActionFilter 開銷？
    - D-Q3: 契約檢查導致延遲上升，如何優化？
    - D-Q8: 必須移除舊 API 時如何兼顧相容與進度？