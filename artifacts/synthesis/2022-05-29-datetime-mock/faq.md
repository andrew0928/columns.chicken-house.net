# [架構師的修練] - 從 DateTime 的 Mock 技巧談 PoC 的應用

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

Q1: 什麼是 DateTime.Now？
- A簡: C# 的靜態屬性，回傳執行環境的系統目前時間，無法以依賴注入直接替換。
- A詳: DateTime.Now 是 C# 中的靜態屬性，直接從 System.DateTime 類別取得系統時間。由於其為 static property，編譯時已靜態連結，無法以常見的依賴注入或介面替換手法攔截，造成測試不可預期、難以重現時間相關情境。為提升可測性與可控性，常以包裝、注入或攔截策略改寫其行為。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q7, B-Q11

Q2: 為什麼 DateTime.Now 難以單元測試？
- A簡: 因不可預測、靜態綁定且依賴系統時鐘，導致測試無法重現與穩定。
- A詳: 單元測試需要可重現與決定性的環境，但 DateTime.Now 於執行瞬間才取值，且受系統時鐘與執行延遲影響，導致時間相關邏輯很難寫出穩定斷言。此外它是 static 屬性，無法以注入替換，若未引入額外技術（包裝、介面或攔截）便難以控制測試基準時間與時間流逝的模擬。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q3, B-Q13

Q3: 什麼是時間 Mock（Time Mocking）？
- A簡: 以替代機制控制「現在時間」與時間流逝，使測試可預期、可重現。
- A詳: 時間 Mock 是以包裝、抽象或攔截手法，將系統時間來源替換為可控制的實作，使程式讀取到的「現在」由測試事先設定。它可凍結時間或模擬流逝，幫助測試驗證到期、排程、時區等情境。典型策略包括靜態包裝、介面注入、Ambient Context 與 Shims 攔截，各有成本與適用範圍。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, A-Q7, A-Q8, A-Q9

Q4: 什麼是 PoC（Proof of Concept，概念驗證）？
- A簡: 聚焦關鍵觀念可行性的最小實作，用以快速驗證設計與溝通。
- A詳: PoC 是在投入大規模實作前，針對核心概念做最小可行的技術驗證與示範，刻意忽略非關鍵細節以降低成本。其價值在於快速試錯、精準溝通與蒐集風險訊號。在時間驅動的流程、事件驅動架構與微服務設計中，PoC 能以簡化手段重現關鍵行為，促進決策。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, A-Q18, B-Q14

Q5: 單元測試與 PoC 在時間控制上的差異？
- A簡: 單元測試偏向凍結時間；PoC 常需時間流動與「時光快轉」能力。
- A詳: 單元測試追求可重現，常用固定時間點驗證某一瞬間的行為；PoC 則需觀察流程隨「時間推進」的行為，例如排程、到期、事件流。故 PoC 除可設定起始時間，更重視「時間流逝」與「快轉」能力，並透過事件驅動讓跨日、跨月的業務規則被完整驗證。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, B-Q4, C-Q4

Q6: 什麼是 Ambient Context Approach？
- A簡: 以「環境中的單一來源」提供時間等可取代資源，集中控制行為。
- A詳: Ambient Context 將可變動的系統資源（如現在時間）封裝在一個全域可取得但可替換的上下文物件中。程式向該物件要時間而非直呼 DateTime.Now，使測試或 PoC 可在不修改大量呼叫點的前提下，集中設定初始時間、模擬流逝與觸發事件。此法兼顧侵入性低與可擴充。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, A-Q11, B-Q1

Q7: 什麼是 SystemTime 靜態包裝法？
- A簡: 以自訂靜態類包裝 Now，提供可替換的 Now 屬性以利測試。
- A詳: SystemTime 是建立一個靜態類別（如 SystemTime.Now）來取代 DateTime.Now 的直接呼叫，測試中可設定其回傳值。不需介面注入，導入成本低，但仍是全域狀態，較難做出情境隔離或多實例控制，易在大型系統或並行測試中發生互相干擾。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, C-Q7, B-Q12

Q8: 什麼是 IDateTimeProvider 介面注入法？
- A簡: 將時間來源抽象成介面，透過依賴注入替換實作以控時間。
- A詳: 定義 IDateTimeProvider（含 Now 等），以建構式或 IoC 容器注入實作。生產使用系統時鐘，測試注入固定或可快轉時鐘。優點是隔離良好、測試友善；缺點是需改動呼叫點與傳遞依賴，在既有大量程式碼中導入成本相對高。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, C-Q8, A-Q10

Q9: 什麼是 Microsoft Fakes（Shims）？
- A簡: 以執行期攔截與重寫呼叫，替換像 DateTime.Now 之類靜態成員。
- A詳: Shims 是 Microsoft Fakes 的一部分，利用執行期重寫與攔截把對靜態方法/屬性的呼叫導向自訂委派，讓不改原始碼也能替換 DateTime.Now。優點是零侵入；限制為需 Visual Studio Enterprise、效能開銷較大、較適用單元測試環境，對 PoC 或產品執行環境不友善。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, C-Q6, A-Q11

Q10: 四種常用策略差異比較？
- A簡: 介面注入隔離佳；靜態包裝導入快；Ambient 折衷；Shims 零侵入。
- A詳: 介面注入（彈性最高、需改動呼叫點）、靜態包裝（導入快、全域狀態風險）、Ambient Context（集中控制、侵入低、可進階擴展）、Shims（零改碼、工具與效能受限）。依需求選擇：單元測試可用包裝/注入/Shims；PoC 與原型偏好 Ambient，兼顧流動時間與事件。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, A-Q7, A-Q8, A-Q9

Q11: 為何選 Ambient Context 而非 Shims？
- A簡: 兼顧低侵入、跨場景可用、可流動與事件驅動，比 Shims 更靈活。
- A詳: Shims 雖零改碼，但受 Enterprise 授權、效能與執行環境限制，較適合純單元測試。Ambient Context 則在不大動架構下集中控制時間，能提供流動、快轉、事件機制，適用 PoC、原型與示範環境，且易於後續擴展成注入或其他策略，工程實務彈性更好。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, A-Q9, B-Q1

Q12: 為什麼需要讓時間「流動」而不只凍結？
- A簡: 驗證排程、到期、事件連續性，需觀察時間前進後的系統行為。
- A詳: 凍結時間適合驗證單點邏輯；但許多需求依賴時間推進（跨日、月結、到期、排程觸發），需模擬真實流逝與「快轉」。讓時間流動可產生完整日誌、報表、訊息與狀態轉移，貼近實務。因此 PoC 與整體流程驗證需要可控且連續的時間軸。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, B-Q5, C-Q4

Q13: DateTimeUtil 的核心價值是什麼？
- A簡: 以單一來源提供可控、可流動時間與跨日事件，利測試與 PoC。
- A詳: DateTimeUtil 透過 Singleton 提供 Now、TimePass、Init/Reset 與 RaiseDayPassEvent。以偏移量保存時間差，確保時間隨真實時鐘而動；以事件補發與「應該」觸發時間，讓跨日規則可驗證。兼顧低侵入與高度可用，特別適合 PoC 與原型展示。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q3, B-Q5

Q14: DateTimeUtil 為何採用 Singleton？
- A簡: 簡化取得時間的方式，模擬 DateTime.Now 的隨取即用體驗。
- A詳: 為模擬 DateTime.Now 的易取性並降低導入成本，採用 Singleton 讓程式隨處以 DateTimeUtil.Instance 存取時間而不需傳遞依賴。這是將 Ambient Context 弱化為全域單一來源的折衷，利於快速落地 PoC，同時保留日後擴展成多 Context 的可能。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q2, C-Q1

Q15: 為何禁止時間倒流（TimePass 不接受負值）？
- A簡: 倒流會破壞事件順序與資料一致性，應以 Reset 重建情境。
- A詳: 若允許時間倒流，先前已觸發的事件是否回滾、資料如何回復將難以一致。為維持單向時間與可預期性，TimePass 僅允許前進；需回到過去應以 Reset + Init 重建情境，明確區分新時空線，避免副作用與狀態不一致。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, D-Q5, C-Q2

Q16: RaiseDayPassEvent 的用途是什麼？
- A簡: 在跨日時通知系統執行日界相關工作，並可補發漏觸發事件。
- A詳: RaiseDayPassEvent 於時間跨過 00:00:00 觸發，用於執行每日定期任務（如日結、報表、清理）。DateTimeUtil 於 Now 或 TimePass 檢查並補發跨日事件，EventArgs.OccurTime 標示應觸發日，讓接收端可根據業務需求精準處理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q3, C-Q4

Q17: OccurTime 與 Now 的差異是什麼？
- A簡: OccurTime 表「應該」觸發日；Now 為實際觸發當下的時間值。
- A詳: 補發機制可能導致事件在稍後才被處理，因此 RaiseDayPassEvent 以 OccurTime 指出原本應觸發的日界時間，Now 則代表觸發當下的實際系統時間。兩者分離可避免誤解，使業務邏輯以 OccurTime 為準、記錄時以 Now 反映處理延遲與實際順序。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, C-Q3, D-Q6

Q18: 什麼是「降維打擊」在 PoC 的意涵？
- A簡: 以低一維度的替代手段驗證核心概念，降低成本與複雜度。
- A詳: 降維打擊是把原需跨系統或複雜基礎設施的設計，降為語言級替代：RPC 降為函式呼叫、分散式為多執行緒、事件匯流排為語言事件、資料庫為記憶體集合。關鍵在明確映射真實與簡化維度，聚焦驗證概念本身，快速迭代與取捨設計方案。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q14, C-Q10, A-Q4

---

### Q&A 類別 B: 技術原理類

Q1: DateTimeUtil 如何運作？
- A簡: 以偏移量計算 Now、補發跨日事件、提供快轉與重設時間。
- A詳: 原理說明：以 _realtime_offset 儲存「期望現在」與實際系統時鐘的差；每次讀取 Now 以 DateTime.Now.Add(offset) 計算。流程：Init 設置偏移與最後檢查點，Now/TimePass 皆呼叫 Seek 檢查跨日並補發 RaiseDayPassEvent。核心組件：offset、_last_check_event_time、Seek_LastEventCheckTime、TimePass、RaiseDayPassEvent。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q5, A-Q13

Q2: Init 與 Reset 的執行流程與保護機制？
- A簡: Init 建立單例與初始偏移；重複 Init 拋例外；Reset 清空重建。
- A詳: 原理說明：Init 計算 expected - DateTime.Now 作為偏移，並將最後事件檢查點設為預設現在。流程：若 _instance 已存在則拋 InvalidOperationException，避免狀態污染；Reset 將 _instance 設 null。核心組件：Singleton、Init(DateTime)、Reset()、防重入保護與例外。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, D-Q4, C-Q1

Q3: Now 的取得流程是什麼？
- A簡: 以系統時鐘加偏移計算，並在取值時檢查與補發跨日事件。
- A詳: 原理說明：Now getter 回傳 DateTime.Now.Add(_realtime_offset)。流程：計算結果後呼叫 Seek_LastEventCheckTime(result) 檢查從最後檢查點到新時間是否跨日，跨則逐日補發事件並更新檢查點。核心組件：Now getter、偏移運算、Seek 檢查與事件觸發。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, A-Q16, D-Q3

Q4: TimePass 的工作原理？
- A簡: 調整偏移量以「快轉」時間，之後統一檢查並補發跨日事件。
- A詳: 原理說明：TimePass 將 _realtime_offset += duration，代表邏輯時間前進。流程：驗證 duration 不為負，更新偏移後取一次 Now 以觸發 Seek 檢查，補發漏掉的跨日事件。核心組件：TimePass(TimeSpan)、引數驗證、偏移更新、事件補發。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, D-Q5, C-Q2

Q5: Seek_LastEventCheckTime 如何觸發事件？
- A簡: 逐日推進檢查點，跨越日期即觸發 RaiseDayPassEvent 並更新狀態。
- A詳: 原理說明：以 while 比較 _last_check_event_time 與檢查時間；若 Date 不同，將檢查點推進至下一天的 00:00:00 並觸發事件。流程：重複直到日期一致或達檢查時間。核心組件：_last_check_event_time、Date 邊界、RaiseDayPassEvent、TimePassEventArgs.OccurTime。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, A-Q17, C-Q3

Q6: 為何以 _realtime_offset 儲存時間差而非固定時間？
- A簡: 保持與真實時鐘同步推移，確保時間自然流動而不需輪詢。
- A詳: 原理說明：儲存偏移可讓 Now 隨系統時鐘自然前進，避免固定值僅凍結。流程：每次取 Now 時動態計算，既能真實流逝又可快轉。核心組件：_realtime_offset、Now 計算、TimePass 更新，避免維護「絕對時間」的複雜度與漂移。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q4, A-Q12

Q7: 為何記錄 _last_check_event_time？
- A簡: 作為事件補發基準，確保跨日不漏觸發且次序正確。
- A詳: 原理說明：僅在 Now 或 TimePass 時才檢查跨日，需記錄最後檢查點以判定是否越過日界。流程：每次檢查逐日推進至目標時間，並在每次推進時觸發事件。核心組件：_last_check_event_time、Seek 機制、RaiseDayPassEvent、補發邏輯。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, D-Q3, A-Q17

Q8: RaiseDayPassEvent 的事件機制如何設計？
- A簡: 於跨日邊界發送事件，附上 OccurTime 標記應觸發日，允許延遲。
- A詳: 原理說明：事件在發現日界變化時被觸發，EventArgs.OccurTime 指定應觸發的日期。流程：Seek 逐日補發，可能與 Now 有延遲。核心組件：EventHandler<TimePassEventArgs>、OccurTime、事件訂閱與解除、補發策略，支持日結等批次工作。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, A-Q17, C-Q3

Q9: 實際時間推進時如何檢測跨日？
- A簡: 不輪詢；在下次存取 Now 或呼叫 TimePass 時一次檢查與補發。
- A詳: 原理說明：不啟用背景執行緒監控，僅在明確互動點進行檢查。流程：Thread.Sleep 過後，首次讀取 Now 會觸發 Seek 檢查並補發跨日事件。核心組件：Now getter、Seek、_last_check_event_time、無輪詢的惰性檢查模型。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q3, C-Q10, B-Q16

Q10: 「應該觸發時間」與「實際觸發時間」如何協同？
- A簡: 以 OccurTime 承載業務基準；以 Now 紀錄處理實際發生時刻。
- A詳: 原理說明：事件補發可能延遲，需分離基準時間與處理時間。流程：Handler 以 OccurTime 寫業務資料（報表日期、日結日），以 Now 寫操作時間（執行/延遲）。核心組件：TimePassEventArgs.OccurTime、DateTimeUtil.Now、審計欄位。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q17, C-Q3, D-Q6

Q11: Microsoft Fakes Shims 的攔截原理與流程？
- A簡: 建立 ShimsContext 後，以 ShimDateTime.NowGet 指派委派取代原呼叫。
- A詳: 原理說明：藉由產生對應 Fakes 程式集，於 ShimsContext 作用域內重寫中繼碼呼叫的目標。流程：Create() 建立範圍→指定 System.Fakes.ShimDateTime.NowGet 委派→執行被測邏輯→釋放範圍還原。核心組件：ShimsContext、Shim 類別、委派、範圍管理。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q9, C-Q6, D-Q7

Q12: 四種策略的技術架構如何設計？
- A簡: 注入（介面+IoC）、包裝（靜態類）、Ambient（單例/Context）、Shims（攔截）。
- A詳: 原理說明：注入以合約抽象與容器管理；包裝以靜態轉呼叫；Ambient 以可替換的全域上下文集中控制；Shims 以重寫攔截。流程：依現況選最小侵入方案。核心組件：IDateTimeProvider/IoC、SystemTime、DateTimeUtil（offset+event）、ShimsContext。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, C-Q7, C-Q8

Q13: 為何測試需設計時間誤差容忍（tolerance）？
- A簡: 執行延遲與毫秒級差異難免，容忍區間能提升測試穩定性。
- A詳: 原理說明：時間受執行環境、排程與除錯影響，毫秒到秒級誤差常見。流程：以 Assert 檢查差值小於某一容忍（如一秒）而非完全相等。核心組件：TimeSpan tolerance、時間比較策略、測試非決定性因素管理。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q9, D-Q8, A-Q2

Q14: 以事件驅動取代排程的思路是什麼？
- A簡: 以跨日事件當觸發源，將日結等任務轉為事件處理器執行。
- A詳: 原理說明：不依賴外部排程器，改由時間模型在跨日時發事件。流程：訂閱 RaiseDayPassEvent，於處理器內執行對應業務。核心組件：事件總線（語言等級）、事件處理器、補發機制、OccurTime 作為任務基準時間。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q3, C-Q4, A-Q18

Q15: 如何擴展為「每月15日 02:00」觸發？
- A簡: 監看跨日事件後檢查條件，或新增月界/時界檢查與補發機制。
- A詳: 原理說明：在既有跨日事件上檢查 OccurTime 是否為每月15日，再以內部計時器或擴展 Seek 邏輯處理 02:00。流程：日界→條件判斷→若需 02:00 再快轉或排定補發。核心組件：RaiseDayPassEvent、擴展條件、次級時間檢查或自定 Scheduler。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: C-Q4, A-Q12, D-Q6

Q16: 為什麼不使用背景執行緒輪詢時間？
- A簡: 降低複雜度與資源消耗，改在存取點惰性檢查即可滿足 PoC。
- A詳: 原理說明：背景輪詢增加執行緒、同步與關閉流程成本，且 PoC 對觸發即時性要求不高。流程：以 Now/TimePass 作為檢查點，於互動時補發跨日事件。核心組件：惰性檢查、事件補發、簡化資源與避免競態。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, D-Q10, A-Q18

---

### Q&A 類別 C: 實作應用類（10題）

Q1: 如何在專案啟動時初始化 DateTimeUtil？
- A簡: 在入口點呼叫 Init 設定起始時間；必要時於測試前 Reset 重設。
- A詳: 步驟：於 Main/測試初始化呼叫 DateTimeUtil.Init(expectedNow)，在不同情境前以 DateTimeUtil.Reset 清空。程式碼: 
  ```csharp
  DateTimeUtil.Init(new DateTime(2022,05,01,0,0,0));
  // ... app start
  ```
  注意：僅能初始化一次；重建情境需先 Reset。最佳實踐：集中管理初始化以避免測試互斥。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, D-Q4, A-Q14

Q2: 如何在單元測試中凍結或快轉時間？
- A簡: 以 Init 設定起始點，透過 TimePass 或 GoNextDays/Hours 控制流逝。
- A詳: 步驟：在 TestInitialize 呼叫 Init；用 TimePass 模擬流逝。程式碼:
  ```csharp
  DateTimeUtil.Init(new DateTime(2002,10,26,12,0,0));
  DateTimeUtil.Instance.TimePass(TimeSpan.FromHours(4));
  ```
  注意：TimePass 不接受負值。最佳實踐：斷言使用時間差容忍，避免毫秒誤差造成 flaky tests。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, B-Q13, D-Q5

Q3: 如何撰寫 RaiseDayPassEvent 處理器累計報表？
- A簡: 訂閱事件、以 OccurTime 判斷日結日，於處理器更新報表資料。
- A詳: 步驟：訂閱事件→在處理器中使用 args.OccurTime 作為報表日期→寫入資料庫。程式碼:
  ```csharp
  DateTimeUtil.Instance.RaiseDayPassEvent += (s,e)=> Report.Run(e.OccurTime);
  ```
  注意：使用 OccurTime 當邏輯日，Now 僅做審計。最佳實踐：處理器應冪等，支援補發。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, B-Q10, A-Q16

Q4: 如何模擬「每月15日 02:00」產出報表？
- A簡: 跨日事件中檢查 OccurTime 是否 15 日，再在 02:00 時間點執行。
- A詳: 步驟：訂閱 RaiseDayPassEvent→檢查 e.OccurTime.Day==15→若需 02:00，可在處理器內用 TimePass 快轉或以內部排程延遲至 02:00。程式碼:
  ```csharp
  if(e.OccurTime.Day==15) RunMonthly(e.OccurTime.Date.AddHours(2));
  ```
  注意：避免時間倒流；補發時以 OccurTime 為準。最佳實踐：記錄已處理月份避免重複。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q15, A-Q12, D-Q6

Q5: 如何以 UI 控制面板操控時間快轉？
- A簡: 建立顯示 Now 的標籤與快轉按鈕，呼叫 TimePass/GoNextDays 即可。
- A詳: 步驟：在 UI 綁定 DateTimeUtil.Instance.Now 顯示；按鈕事件呼叫 TimePass。程式碼:
  ```csharp
  labelNow.Text = DateTimeUtil.Instance.Now.ToString();
  btnNextDay.Click += (_,__)=>DateTimeUtil.Instance.GoNextDays(1);
  ```
  注意：顯示前先 Init；操作後刷新 UI。最佳實踐：提供重設與快速跳轉常用按鍵。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q13, B-Q3, C-Q1

Q6: 如何用 Microsoft Fakes 攔截 DateTime.Now？
- A簡: 在 ShimsContext 範圍內指定 ShimDateTime.NowGet 委派返回固定時間。
- A詳: 步驟：啟用 Fakes→測試中 using ShimsContext.Create()→指派 NowGet。程式碼:
  ```csharp
  using(ShimsContext.Create()){
    System.Fakes.ShimDateTime.NowGet=()=> new DateTime(2000,1,1);
    // act/assert
  }
  ```
  注意：需 VS Enterprise；有效能開銷。最佳實踐：限用於單元測試而非 PoC 執行環境。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q9, B-Q11, D-Q7

Q7: 如何以 SystemTime 靜態包裝替代 DateTime.Now？
- A簡: 建立 SystemTime.Now 屬性與可設定委派，測試時指定返回。
- A詳: 步驟：定義 static Func<DateTime> NowProvider，Now 轉呼叫 Provider。測試中設定 Provider。程式碼:
  ```csharp
  public static class SystemTime{
    public static Func<DateTime> NowProvider=()=>DateTime.Now;
    public static DateTime Now=>NowProvider();
  }
  ```
  注意：全域共享，並行測試需小心。最佳實踐：測試結束還原 Provider。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, B-Q12, D-Q6

Q8: 如何以 IDateTimeProvider 注入時間來源？
- A簡: 定義介面提供 Now，透過 DI 注入實作以控制時間行為。
- A詳: 步驟：定義介面→實作系統時鐘/測試時鐘→以建構式或容器注入。程式碼:
  ```csharp
  public interface IDateTimeProvider{ DateTime Now{get;} }
  ```
  注意：需修改呼叫點。最佳實踐：於應用層統一綁定 Provider，避免散落。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q12, D-Q7

Q9: 如何在測試中處理時間誤差容忍？
- A簡: 使用 TimeSpan 容忍區間比較，避免毫秒抖動造成斷言失敗。
- A詳: 步驟：定義 tolerance，例如 1 秒；比較差值是否小於容忍。程式碼:
  ```csharp
  var tol=TimeSpan.FromSeconds(1);
  Assert.IsTrue((actual-expected)<tol);
  ```
  注意：單步除錯會放大誤差。最佳實踐：在長操作測試提高容忍或改為等價條件檢查。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q13, D-Q8, A-Q2

Q10: 如何在 PoC 中整合 Timer 與 DateTimeUtil？
- A簡: 用 RaiseDayPassEvent 觸發器替代實體排程，或在處理器內再建短期計時。
- A詳: 步驟：以 RaiseDayPassEvent 作為日級觸發；需要更細時間（如 02:00）時，在處理器內判斷後以 TimePass 或短期 Timer 執行。程式碼:
  ```csharp
  if(e.OccurTime.Day==15) DoAt(e.OccurTime.AddHours(2));
  ```
  注意：避免雙重排程競態。最佳實踐：以 OccurTime 為唯一業務基準。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q15, A-Q18, D-Q6

---

### Q&A 類別 D: 問題解決類（10題）

Q1: 測試結果不穩定，因使用 DateTime.Now，怎麼辦？
- A簡: 以包裝、注入、Ambient 或 Shims 控制時間，並加入容忍區間。
- A詳: 症狀：同測試偶爾失敗，時間相關斷言波動。原因：直接使用 DateTime.Now 導致不可預測。解決：導入 SystemTime/IDateTimeProvider/DateTimeUtil 或 Shims；測試比較加入 tolerance。預防：建立時間取得規約，禁止直接呼叫 Now，集中管理時間來源。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, B-Q13, C-Q2

Q2: JWT/Token 未來到期導致測試失敗，如何修正？
- A簡: 設定測試啟動時間到有效期內，或動態產出長效 Token。
- A詳: 症狀：時間久後測試全數到期失敗。原因：固定 Token 有效期過期。解決：在 TestInitialize 用 DateTimeUtil.Init 設定情境時間，或改為測試時簽發動態 Token。預防：避免硬編碼到期，統一以可控時間來源與工廠方法產生證憑。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, A-Q5, B-Q1

Q3: 跨日事件未觸發，該如何診斷？
- A簡: 檢查是否曾存取 Now 或呼叫 TimePass，否則惰性檢查不會執行。
- A詳: 症狀：跨越午夜後，預期任務未跑。原因：DateTimeUtil 不輪詢，需在 Now/TimePass 時才檢查。解決：在流程關鍵點讀取 Now 或在測試後補一次 Now；或顯式呼叫 TimePass。預防：建立讀取 Now 的檢查點，或在框架層統一心跳拉取。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, C-Q10, A-Q16

Q4: 呼叫 Init 兩次丟 InvalidOperationException，怎麼辦？
- A簡: 先呼叫 Reset，再以 Init 重新建立情境，避免重複初始化。
- A詳: 症狀：第二次 Init 直接拋例外。原因：Singleton 已存在，防止狀態污染。解決：依需求 Reset() 清空，再 Init(newNow)。預防：在測試生命週期標準化 SetUp/Teardown；應用入口僅初始化一次，集中管理。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, C-Q1, A-Q14

Q5: 傳入負值給 TimePass 出現 ArgumentOutOfRange，如何處理？
- A簡: 不允許時間倒退；若需回到過去，請 Reset + Init 重建。
- A詳: 症狀：TimePass(負值) 拋例外。原因：為維持事件順序與一致性，禁止倒流。解決：使用 Reset 清空，再以 Init 設定新的過去情境。預防：封裝時間操作 API，僅暴露「前進」；測試中以建立新情境取代回溯。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q15, B-Q4, C-Q2

Q6: 跨大量天數時事件數量不精準，如何處置？
- A簡: 檢查補發邏輯與 OccurTime 使用；必要時分段快轉確保逐日觸發。
- A詳: 症狀：一次快轉多月後報表數不符。原因：處理器未以 OccurTime 為基準或補發邏輯遺漏。解決：在處理器採用 OccurTime；需要時多次 TimePass 分段（逐日或逐月）。預防：處理器冪等與完成標記，避免重複與遺漏。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q10, C-Q4

Q7: 使用 Shims 在 CI 環境失敗（無 Enterprise），怎麼辦？
- A簡: 改用介面注入、靜態包裝或 Ambient Context，移除 Enterprise 依賴。
- A詳: 症狀：CI 無法執行 Fakes 測試。原因：Shims 需 VS Enterprise 支援。解決：將時間控制改為 IDateTimeProvider 或 DateTimeUtil；必要時以條件編譯區分本機與 CI。預防：選用不綁特定授權的策略，確保跨環境一致性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, C-Q8, C-Q7

Q8: 單步除錯導致測試誤差加大，如何避免？
- A簡: 提高容忍區間或改以等價條件判斷，減少對精確秒數的依賴。
- A詳: 症狀：逐步執行時斷言常超時。原因：手動停頓放大時間差。解決：增大 tolerance、以「在某區間內」判斷、或在關鍵步驟以可控 TimePass 取代真實等待。預防：將時間關鍵測試自動化執行，避免人工介入。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q13, C-Q9, A-Q2

Q9: 不同時區或夏令時導致判斷錯誤，該怎麼處理？
- A簡: 明確選用 UTC 或 DateTimeOffset，並於事件以 OccurTime 作業務基準。
- A詳: 症狀：跨時區部署或 DST 切換時日期偏移。原因：使用本地時間未標示偏移。解決：以 UTC 儲存、以 DateTimeOffset 描述偏移；事件處理以 OccurTime（標準化）為基準。預防：規範時間標準；轉換只在展示層。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q10, C-Q3, A-Q12

Q10: 多執行緒同時操作 DateTimeUtil 造成競態，怎麼防護？
- A簡: 序列化時間操作、在 Seek/TimePass 加鎖，或於應用層集中操作。
- A詳: 症狀：事件重複或遺漏。原因：多執行緒競態更新偏移與檢查點。解決：為 TimePass 與 Seek 區段加 lock、或限制單執行緒操控時間。預防：在 PoC 控制台集中時間操作；如需並行，評估引入線程安全機制。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q16, C-Q5, A-Q14

---

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 DateTime.Now？
    - A-Q2: 為什麼 DateTime.Now 難以單元測試？
    - A-Q3: 什麼是時間 Mock（Time Mocking）？
    - A-Q4: 什麼是 PoC（Proof of Concept，概念驗證）？
    - A-Q5: 單元測試與 PoC 在時間控制上的差異？
    - A-Q7: 什麼是 SystemTime 靜態包裝法？
    - A-Q8: 什麼是 IDateTimeProvider 介面注入法？
    - A-Q9: 什麼是 Microsoft Fakes（Shims）？
    - A-Q12: 為什麼需要讓時間「流動」而不只凍結？
    - B-Q13: 為何測試需設計時間誤差容忍（tolerance）？
    - C-Q1: 如何在專案啟動時初始化 DateTimeUtil？
    - C-Q2: 如何在單元測試中凍結或快轉時間？
    - C-Q7: 如何以 SystemTime 靜態包裝替代 DateTime.Now？
    - D-Q1: 測試結果不穩定，因使用 DateTime.Now，怎麼辦？
    - D-Q5: 傳入負值給 TimePass 出現 ArgumentOutOfRange，如何處理？

- 中級者：建議學習哪 20 題
    - A-Q6: 什麼是 Ambient Context Approach？
    - A-Q10: 四種常用策略差異比較？
    - A-Q11: 為何選 Ambient Context 而非 Shims？
    - A-Q13: DateTimeUtil 的核心價值是什麼？
    - A-Q14: DateTimeUtil 為何採用 Singleton？
    - A-Q15: 為何禁止時間倒流（TimePass 不接受負值）？
    - A-Q16: RaiseDayPassEvent 的用途是什麼？
    - A-Q17: OccurTime 與 Now 的差異是什麼？
    - B-Q1: DateTimeUtil 如何運作？
    - B-Q2: Init 與 Reset 的執行流程與保護機制？
    - B-Q3: Now 的取得流程是什麼？
    - B-Q4: TimePass 的工作原理？
    - B-Q5: Seek_LastEventCheckTime 如何觸發事件？
    - B-Q8: RaiseDayPassEvent 的事件機制如何設計？
    - C-Q3: 如何撰寫 RaiseDayPassEvent 處理器累計報表？
    - C-Q4: 如何模擬「每月15日 02:00」產出報表？
    - C-Q9: 如何在測試中處理時間誤差容忍？
    - D-Q3: 跨日事件未觸發，該如何診斷？
    - D-Q4: 呼叫 Init 兩次丟 InvalidOperationException，怎麼辦？
    - D-Q8: 單步除錯導致測試誤差加大，如何避免？

- 高級者：建議關注哪 15 題
    - A-Q18: 什麼是「降維打擊」在 PoC 的意涵？
    - B-Q9: 實際時間推進時如何檢測跨日？
    - B-Q10: 「應該觸發時間」與「實際觸發時間」如何協同？
    - B-Q11: Microsoft Fakes Shims 的攔截原理與流程？
    - B-Q12: 四種策略的技術架構如何設計？
    - B-Q14: 以事件驅動取代排程的思路是什麼？
    - B-Q15: 如何擴展為「每月15日 02:00」觸發？
    - B-Q16: 為什麼不使用背景執行緒輪詢時間？
    - C-Q6: 如何用 Microsoft Fakes 攔截 DateTime.Now？
    - C-Q8: 如何以 IDateTimeProvider 注入時間來源？
    - C-Q10: 如何在 PoC 中整合 Timer 與 DateTimeUtil？
    - D-Q2: JWT/Token 未來到期導致測試失敗，如何修正？
    - D-Q6: 跨大量天數時事件數量不精準，如何處置？
    - D-Q9: 不同時區或夏令時導致判斷錯誤，該怎麼處理？
    - D-Q10: 多執行緒同時操作 DateTimeUtil 造成競態，怎麼防護？