# [RUN! PC] 2010 七月號 - 結合檔案及資料庫的交易處理（TxF、TransactionScope、AlphaFS）

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是交易處理（Transaction）？
- A簡: 交易處理以 ACID 為核心，確保多步操作要麼全部成功、要麼全部回滾，維持系統一致性。
- A詳: 交易處理是一種保證資料一致性的機制，強調 ACID 四要素：原子性、 一致性、隔離性、持久性。其目的在於把多個邏輯相關的操作納入同一個不可分割的單位，確保要麼全部成功提交，要麼全部回復到初始狀態。除了資料庫常見的交易外，當應用同時涉及檔案與資料庫寫入時，也可用跨資源的交易來維持整體一致性，避免出現「資料庫新增成功但檔案未建立」的破碎狀態。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, A-Q12, B-Q5

A-Q2: 什麼是 TransactionScope？
- A簡: .NET 的高階交易 API，提供環境交易，讓多個支援 System.Transactions 的資源自動加入同一交易。
- A詳: TransactionScope 是 .NET System.Transactions 的簡化用法。開啟一個範圍後，範圍內所有支援 System.Transactions 的資源（例如 SQL 連線）會自動「加入」目前環境交易。只要在 using 區塊結束前呼叫 Complete()，交易就會提交，否則自動回滾。它可在需要時升級為分散式交易，協調多個資源的兩階段提交，讓開發者以最少樣板程式碼達成複雜的交易一致性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, A-Q11, B-Q9

A-Q3: 什麼是 Transactional NTFS（TxF）？
- A簡: TxF 是 NTFS 的交易機制，讓檔案/目錄操作可提交或回滾，達成檔案系統的原子性。
- A詳: Transactional NTFS（TxF）是 Windows 在 NTFS 上提供的交易性檔案系統擴充。透過 TxF，建立、刪除、寫入、搬移等檔案操作可以納入一個交易，成功則提交，失敗則回滾，避免產生半成品檔案或不一致。雖然 .NET 早期未內建 TxF 包裝，但可藉由 P/Invoke 或 AlphaFS 這類函式庫，在 .NET 程式中使用 TxF 的能力，並與 TransactionScope 協同工作。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, A-Q5, A-Q20

A-Q4: 為什麼要把檔案系統與資料庫結合為單一交易？
- A簡: 確保跨資源操作一致性，避免只成功一半的破碎狀態，提升資料可靠性與可恢復性。
- A詳: 很多業務同時牽涉「寫資料庫」與「寫檔案」（如上傳檔案並記錄表格資料）。若兩者不在同一交易，當其中之一失敗就會留下不一致：例如 DB 寫入成功但檔案遺失。將檔案和資料庫納入單一交易，可以確保操作要麼全部成功，要麼全部回滾，簡化錯誤恢復，降低營運風險，也讓例外情況處理更可預期。這正是 TxF 與 TransactionScope 結合的核心價值。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, B-Q3, C-Q1

A-Q5: TxF 與 TransactionScope 的關係是什麼？
- A簡: TxF 提供檔案的交易能力，TransactionScope 提供跨資源協調；兩者結合達成單一交易。
- A詳: TxF負責在 NTFS 層實現檔案操作的交易性；TransactionScope 則是 .NET 的交易協調入口。當以適當包裝（如 AlphaFS）將 TxF 的「核心交易」與 .NET 的「環境交易」對接後，便可在 TransactionScope 中同時進行 DB 與檔案操作。提交時一起成功，回滾時一起還原，讓檔案系統和資料庫共享同一個 ACID 保證。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q16, C-Q1

A-Q6: 什麼是 AlphaFS？
- A簡: AlphaFS 是擴充 System.IO 的 .NET 類別庫，支援 NTFS 進階功能，如 TxF、VSS、HardLink 等。
- A詳: AlphaFS 是社群維護的 .NET 函式庫，目標是「像 System.IO 一樣好用，卻能存取更多 NTFS 能力」。它以 .NET 風格封裝大量 Win32 API，提供長路徑、硬連結、掛載點、VSS、以及（早期版本中）TxF 等功能的管理介面。對開發者而言，使用 AlphaFS 可避免大量 P/Invoke 樣板，並更容易把檔案操作納入交易情境與自動化測試流程。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, B-Q4, C-Q3

A-Q7: AlphaFS 與 System.IO 有何差異？
- A簡: System.IO 提供基本檔案 API；AlphaFS 在其基礎上加入 NTFS 進階能力與交易式操作封裝。
- A詳: System.IO 提供跨平台的基礎檔案操作，但對 NTFS 特有功能沒有完整支援。AlphaFS 針對 Windows/NTFS 深化：支援長路徑、替代資料流、硬連結、掛載點、VSS 以及（在支持版本中）TxF 交易式 API。對只需通用檔案處理的應用，System.IO 足矣；若要用到 NTFS 深度功能與交易整合，AlphaFS 更便利且程式碼更精簡。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, C-Q3, B-Q11

A-Q8: 什麼是 P/Invoke？在此議題的角色為何？
- A簡: P/Invoke 讓 .NET 呼叫 Win32 API；未有托管包裝時，常用它操作 TxF 原生函式。
- A詳: 平台呼叫（P/Invoke）允許 .NET 程式直接呼叫非受控的 Win32 API。早期 .NET 未提供 TxF 托管支援時，若要使用 CreateFileTransacted 等 TxF 函式，需自訂 P/Invoke 宣告與結構。這雖可行，但繁瑣且易出錯。AlphaFS 等函式庫即是將這些 P/Invoke 封裝為安全、易用的 .NET 介面，降低維護成本。
- 難度: 中級
- 學習階段: 基礎
- 關聯概念: B-Q10, B-Q11, C-Q4

A-Q9: 什麼是 NTFS 的進階功能（VSS、HardLink）？
- A簡: VSS 提供一致性快照；HardLink 允許多個目錄項指向同一檔案資料，皆為 NTFS 特性。
- A詳: VSS（Volume Shadow Copy Service）能在不中斷服務下建立一致性快照，便於備份或還原。硬連結（HardLink）則是在同一 NTFS 卷上為同一資料內容建立多個檔名，刪除其中之一不會移除資料本體。AlphaFS 對這些 NTFS 特性提供友善 API，使應用能在備份、部署、內容管理場景中更彈性地運用檔案系統能力。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q17, B-Q18, A-Q6

A-Q10: 為何 .NET Framework 沒有內建支援 TxF？
- A簡: TxF 屬於 Windows/NTFS 的原生功能，.NET 早期未提供直接包裝，需靠 P/Invoke 或第三方庫。
- A詳: TxF 是作業系統層面的 NTFS 特性，並非 .NET 通用 API 的一部分。因此在 2010 年的 .NET Framework 中沒有提供直接封裝。若想在 .NET 程式中使用 TxF，只能選擇自行 P/Invoke 呼叫 Win32 TxF 函式，或採用像 AlphaFS 這樣的包裝庫，以降低複雜度與風險。這也促成了社群方案的出現與成熟。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, A-Q6, B-Q11

A-Q11: 何謂「單一交易」（跨資源交易）？
- A簡: 將多個資源的操作納入同一提交/回滾邊界，常靠兩階段提交協調一致性。
- A詳: 單一交易在語意上指「多資源共享同一個 ACID 邊界」。它可涵蓋資料庫、訊息佇列、檔案系統等多個資源，並以交易協調器（如 System.Transactions）整合，透過兩階段提交確保一致。對開發者而言，這讓跨元件的錯誤恢復簡化，並大幅降低手動補償的負擔。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q3, A-Q2

A-Q12: 結合交易的核心價值是什麼？
- A簡: 提升一致性與可靠性，讓錯誤可控、恢復容易，降低營運與維護成本。
- A詳: 將檔案與資料庫結合為單一交易，最大的價值是「可預期的一致性」。開發者不必為每個失敗分支撰寫複雜補償；營運面則避免殘留髒資料與孤兒檔案，減少事後清理成本。測試面也更容易以交易邊界驗證成功/失敗兩種路徑，提升品質與交付速度。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, B-Q3, C-Q8

A-Q13: TxF 與資料庫交易有何不同？
- A簡: 都提供 ACID；TxF 針對檔案系統，資料庫交易針對關聯/文件資料，資源類型與鎖定方式不同。
- A詳: 兩者皆追求 ACID，但作用層不同。資料庫交易作用於表格/文件等資料結構，具備豐富的隔離層級、鎖定策略與查詢優化；TxF 則針對檔案/目錄操作的原子性與可回復性，鎖定與可見性以檔案系統為主。兩者結合時，需要交易協調器協同提交與回滾。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q2, B-Q6

A-Q14: 何時應避免使用 TxF？
- A簡: 在不支援或不建議環境、跨平台需求、高性能路徑，宜改採補償/最終一致等替代方案。
- A詳: 若部署環境不支援 TxF（非 NTFS、部分新系統不建議使用）、或應用需跨平台/雲原生，直接倚賴 TxF 會受限。此時應考慮替代策略，如「暫存＋原子改名」模式、Outbox/收據表、多階段確認與補償。對高吞吐低延遲場景，也需評估交易開銷與鎖定影響。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q9, D-Q8, D-Q10

A-Q15: 什麼是 VSS（Volume Shadow Copy Service）？
- A簡: Windows 的一致性快照服務，允許在不中斷運作時備份或還原資料。
- A詳: VSS 能與應用協調，建立某一時刻的卷快照，確保快照內的檔案狀態一致。它解決「正在變動的檔案如何安全備份」問題，常用於備份、災難復原。與 TxF 不同，VSS 聚焦「拍照保存」，TxF 聚焦「原子提交/回滾」；兩者可互補使用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q17, A-Q9

A-Q16: 什麼是硬連結（HardLink）？
- A簡: 同一卷內多個檔名指向同一份資料內容，刪除其一不會立刻移除資料。
- A詳: 在 NTFS 中，硬連結讓多個目錄項（檔名）共用同一檔案內容。這有助節省空間與實現版本/發佈策略。建立、刪除硬連結可以納入交易（在支援情況下），使目錄結構變更與資料庫更新一起提交或回滾，避免半途狀態。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q18, A-Q9, C-Q3

A-Q17: 什麼是核心交易（Kernel Transaction）？
- A簡: Windows 核心層的交易物件，用於協調檔案系統等資源的交易操作。
- A詳: TxF 倚賴 Windows 的核心交易機制（KTM）。核心交易是 OS 內部的交易物件，檔案系統可將操作附著其上以達到提交/回滾。藉由適當包裝，可將核心交易與 .NET 的環境交易銜接，達到跨資源一致性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q3, B-Q11

A-Q18: 什麼是 MSDTC？何時會用到？
- A簡: 分散式交易協調器，當交易跨多資源或升級時，負責兩階段提交的協調。
- A詳: Microsoft Distributed Transaction Coordinator（MSDTC）在交易涉及多個資源管理員時出場，協調「準備/提交」兩個階段。使用 TransactionScope 當偵測到需要升級（例如多個不同連線）時，就可能使用 MSDTC。若未啟動，交易可能失敗並拋出例外。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, D-Q1, C-Q10

A-Q19: 什麼是「環境交易」（Ambient Transaction）？
- A簡: 目前執行緒上的交易內容，支援資源自動加入，簡化交易傳遞與管理。
- A詳: System.Transactions 以 Ambient Transaction 表示當前交易，透過 Transaction.Current 取得。TransactionScope 建立範圍後，支援交易的資源可自動加入，不需顯式傳遞交易物件。這對 ADO.NET 與 AlphaFS 這類封裝非常關鍵，可讓檔案與資料庫在同一範圍自動協調。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q9, A-Q2

A-Q20: 為什麼 AlphaFS 能簡化 TxF 的應用？
- A簡: 它將繁瑣的 Win32 TxF 呼叫封裝為 .NET 風格 API，避免 P/Invoke 細節與易錯點。
- A詳: 直接使用 TxF 需處理交易句柄、結構體、錯誤碼等繁瑣細節。AlphaFS 以熟悉的 File/Directory 類別樣式提供對應的 Transacted 方法（如 CreateDirectoryTransacted），並與環境交易整合，讓開發只需少量程式碼就能把檔案操作納入 TransactionScope，顯著降低學習與維護成本。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, C-Q1, C-Q3

### Q&A 類別 B: 技術原理類

B-Q1: TransactionScope 的運作機制是什麼？
- A簡: 建立範圍後資源自動加入環境交易，Complete 提交、未呼叫則回滾，可視情況升級分散式。
- A詳: 建立 TransactionScope 會設定 Transaction.Current。支援 System.Transactions 的資源管理員在使用過程會加入（Enlist）這個交易。scope.Complete() 表示業務成功，Dispose 時若已 Complete 則提交，反之回滾。當偵測多資源或特定情境時會升級成分散式交易，由 MSDTC 協調兩階段提交。這種模式極大簡化了跨資源交易的樣板程式碼。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q2, A-Q19, A-Q18

B-Q2: TxF 如何讓檔案操作具備交易性？
- A簡: 以核心交易附著檔案操作，暫存變更直至提交；提交成功再永久化，失敗則回滾。
- A詳: TxF 透過 Kernel Transaction Manager（KTM）在 NTFS 層面跟蹤與隔離檔案操作。當使用 Transacted API 開檔、寫入或建立目錄時，變更並不立即對全域可見，而是掛在交易上下文中。提交（Commit）才將變更持久化；回滾（Rollback）則丟棄變更。此機制讓檔案操作具備原子性與一致性，可與其他資源的交易協同。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, A-Q17, B-Q3

B-Q3: TxF 與 TransactionScope 整合的執行流程為何？
- A簡: 建立 TransactionScope→DB/檔案加入交易→完成則提交、否則回滾；由協調器保證一致。
- A詳: 一般流程為：1) 建立 TransactionScope（設定逾時/隔離）。2) 執行 ADO.NET 操作，連線自動加入交易。3) 透過 AlphaFS 的 Transacted API 執行檔案操作，將其綁定到同一環境交易。4) 驗證業務邏輯無誤後呼叫 Complete。5) Dispose 時執行提交（或回滾）。若過程涉及多資源，可能由 MSDTC 協調兩階段提交，確保整體一致。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, C-Q1, A-Q18

B-Q4: 使用 AlphaFS 進行 TxF 的技術架構？
- A簡: 以 .NET 介面封裝 Win32 Transacted API，對接環境交易，提供 File/Directory 的 Transacted 方法。
- A詳: AlphaFS 在 Alphaleonis.Win32.Filesystem 命名空間下，提供與 System.IO 類似的 API，並加入 Transacted 版本（如 CreateDirectoryTransacted、WriteAllTextTransacted）。這些方法內部以 P/Invoke 呼叫 Win32 的 TxF 函式，並將交易關聯至 Transaction.Current，使檔案與資料庫在同一交易範圍內被協調提交/回滾。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, A-Q20, C-Q3

B-Q5: 兩階段提交（2PC）的原理是什麼？
- A簡: 分為「準備」與「提交」兩階段，所有資源先準備成功，協調器才發出最終提交指令。
- A詳: 在跨資源交易中，協調器先向所有參與者發出「準備（Prepare）」訊息；若全部回覆「就緒」，才進入第二階段的「提交（Commit）」。若任一參與者在準備失敗或超時，協調器會指示所有參與者回滾（Rollback）。此協定是分散式交易一致性的關鍵，System.Transactions 與 MSDTC 即採此機制。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, A-Q18, B-Q3

B-Q6: 交易隔離性對檔案與資料庫有何影響？
- A簡: 隔離限制了未提交變更的可見性；DB 用隔離層級，檔案用 TxF 的可見性與鎖定規則。
- A詳: 在資料庫，隔離層級（如 ReadCommitted）控制讀寫衝突與幻讀等現象；在檔案系統，TxF 使未提交的檔案變更對其他行程不可見或受限。整體系統需兼顧兩者，以避免交錯讀寫造成不一致。設計時應考量存取順序與逾時，降低鎖競爭。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q13, B-Q12, C-Q5

B-Q7: 交易失敗時檔案系統如何回復？
- A簡: 若未提交，TxF 會自動丟棄交易中的變更，系統回到變更前狀態，避免殘留半成品。
- A詳: 檔案與目錄在交易內的建立、刪除、寫入都屬暫存；當交易回滾，TxF 撤銷這些操作。這讓程式不必再為「清理殘檔」撰寫額外邏輯。不過若過程有交易外的暫存檔或外部副作用，仍須自行清理與補償。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q7, D-Q5, A-Q3

B-Q8: 在交易範圍內處理跨執行緒與非受控資源的機制？
- A簡: 使用環境交易自動傳遞，必要時手動傳遞交易內容；非受控資源需以封裝支援交易。
- A詳: Ambient Transaction 不會自動跨執行緒/非同步流動（需選擇性啟用），也不是所有非受控資源都能感知交易。可利用 TransactionScopeAsyncFlowOption.Enabled 讓非同步延續攜帶交易；對非受控資源需藉由封裝（如 AlphaFS 封裝 TxF）參與交易；否則應採補償策略。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: C-Q5, C-Q1, A-Q19

B-Q9: 資源管理員加入（Enlistment）交易的機制？
- A簡: 資源透過 System.Transactions 介面註冊加入，接收準備/提交/回滾回呼以協調一致。
- A詳: 支援交易的資源管理員會在使用時向 Transaction.Current 註冊，標準介面包含參與者在準備、提交、回滾階段的回呼。這讓協調器得以通知各資源一致地完成或撤銷操作。ADO.NET 提供內建支持；檔案系統則需由封裝（如 AlphaFS）扮演管理員角色或橋接核心交易。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q1, B-Q3, A-Q5

B-Q10: 以 P/Invoke 使用 TxF API 的流程為何？
- A簡: 建立核心交易→呼叫 Transacted API（如 CreateFileTransacted）→提交或回滾→釋放資源。
- A詳: 典型步驟：1) P/Invoke CreateTransaction 取得交易句柄。2) 使用 CreateFileTransacted、MoveFileTransacted 等函式進行檔案操作並附帶該交易句柄。3) 業務成功則 CommitTransaction，失敗則 RollbackTransaction。4) 關閉句柄與清理。此作法易受宣告與結構對齊等細節影響，維護成本較高。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q8, C-Q4, B-Q11

B-Q11: AlphaFS 如何封裝 P/Invoke 以支援 TxF？
- A簡: 將 Win32 結構與呼叫隱藏在 .NET 方法內，對接環境交易，提供安全的托管 API。
- A詳: AlphaFS 將 TxF 的句柄管理、錯誤碼轉換、Unicode/長路徑、權限與重試策略等細節封裝，暴露為熟悉的靜態方法或類別方法，並處理交易關聯。開發者只需呼叫 Transacted 版本 API，即可享有 TxF 與 System.Transactions 的整合效益。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q4, C-Q3

B-Q12: 使用 TxF 的檔案鎖定與可見性如何運作？
- A簡: 交易內變更對外不可見或受限；鎖定在交易期間持有，提交後才公開變更。
- A詳: 在交易期間，檔案的新增或內容變動對其他行程通常不可見，或遭受訪問限制，避免髒讀。鎖定策略由 NTFS 與 TxF 決定；提交後才會將變更公開。需避免長交易與大量鎖定導致資源競爭與等待。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q6, D-Q7, C-Q1

B-Q13: TransactionScope 的逾時與隔離層級如何影響系統？
- A簡: 逾時過短易回滾；隔離層級越高越安全但越慢。需依業務與負載權衡設定。
- A詳: TransactionOptions 可設定 Timeout 與 IsolationLevel。逾時限制交易最長持續時間，避免長鎖拖累系統；隔離層級控制讀寫衝突與一致性保障。過嚴會影響並行度，過鬆易出現一致性風險。需配合檔案與資料庫行為整體評估。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q5, D-Q5, B-Q6

B-Q14: TxF 的限制有哪些？
- A簡: 僅支援 NTFS；部分操作或環境不支援；版本支援狀態與相容性需依文件驗證。
- A詳: TxF 只適用 NTFS，對 FAT/ExFAT/網路檔案系統不生效。並非所有檔案操作都提供 Transacted 版本，且在不同 Windows 版本支援狀況不一。設計時須檢查目標環境與 API 可用性，必要時提供替代流程或禁用相關路徑。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q2, C-Q9, A-Q14

B-Q15: 如何在一個 TransactionScope 處理多個資料庫與檔案？
- A簡: 讓所有連線與檔案操作都在同一範圍內進行，必要時由 MSDTC 協調分散式交易。
- A詳: 於同一 TransactionScope 內開啟所有 DB 連線與檔案操作（AlphaFS Transacted API）。若涉及多個資源管理員或多個不同連線，交易可能升級為分散式，由 MSDTC 協調 2PC。務必做好逾時設定與錯誤處理，避免長時間持鎖。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q18, C-Q1, D-Q3

B-Q16: AlphaFS 與 System.Transactions 的互操作機制？
- A簡: AlphaFS 透過對接 Transaction.Current，讓檔案操作加入同一環境交易與協調流程。
- A詳: 當 TransactionScope 建立後，Transaction.Current 代表當前交易。AlphaFS 在呼叫 Transacted API 時會檢查並關聯此交易，進而加入協調流程。提交或回滾時，檔案系統與資料庫能一致行動。這是達成「單一交易」的關鍵一環。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q3, C-Q1

B-Q17: VSS 與 TxF 的關係與差異？
- A簡: VSS 管快照，TxF 管交易；前者保整體一致快照，後者保單次操作原子提交/回滾。
- A詳: VSS 適用備份/還原，重點是「某時點一致性視圖」；TxF 重點是「操作原子性」。在某些流程中可先用 TxF 確保變更一致，再以 VSS 製作快照，供備份與回溯之用，兩者互補。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q15, A-Q3, B-Q2

B-Q18: 硬連結在交易中的行為如何？
- A簡: 硬連結建立/刪除可作為交易的一部分，提交才生效，回滾則撤銷目錄結構變更。
- A詳: 在支援 TxF 的環境中，對硬連結的建立與刪除可被納入同一交易，讓目錄結構調整與資料庫更新一致提交。這對版本切換、零停機發佈等情境很有幫助。需確認 API 與環境支援度。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, B-Q14, C-Q3

B-Q19: 如何設計錯誤處理以確保一致性？
- A簡: 嚴格使用交易邊界、檢查回傳值、集中處理例外，必要時提供補償與重試策略。
- A詳: 將所有相關操作置於同一 TransactionScope，任何例外都應導致回滾。對可能暫時性失敗（I/O、網路）的步驟設計重試與退避；對不可交易的外部副作用，提供補償方案。記錄交易 ID 以利稽核與重放。逾時要清楚設定，避免長鎖導致系統資源耗盡。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: D-Q5, C-Q7, C-Q8

B-Q20: 如何在本架構中實作交易記錄與審計？
- A簡: 以交易 ID 結合應用日誌，紀錄每步驟狀態，提交後寫入審計表或事件來源。
- A詳: 建議在 TransactionScope 開始時生成/取得交易 ID，於應用日誌與資料庫審計表關聯記錄每個關鍵動作與結果。提交後可再記錄一筆成功事件；回滾則標示原因與堆疊，便於追查。對檔案操作，記錄目標路徑、雜湊與版本，提供完整證據鏈。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q8, D-Q5, A-Q12

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何用 TransactionScope + AlphaFS 同步寫入資料庫與檔案？
- A簡: 於 TransactionScope 中同時執行 ADO.NET 與 AlphaFS Transacted API，呼叫 Complete 提交。
- A詳: 具體步驟：1) 設定 TransactionOptions（逾時/隔離）。2) using (var scope = new TransactionScope(...)) 建立交易。3) 開啟 SqlConnection 並執行 INSERT/UPDATE。4) 以 AlphaFS 的 Transacted 方法寫入檔案。5) 驗證無誤後 scope.Complete()，離開 using 自動提交。程式碼片段（示意）：
// C#
var opt = new TransactionOptions { Timeout = TimeSpan.FromSeconds(30) };
using (var scope = new TransactionScope(TransactionScopeOption.Required, opt)) {
  using (var c = new SqlConnection(cs)) { c.Open(); /* SQL 操作 */ }
  Alphaleonis.Win32.Filesystem.File.WriteAllTextTransacted(@"C:\data\a.txt", "content", Encoding.UTF8);
  scope.Complete();
}
注意：依所用 AlphaFS 版本調整 API 名稱；加上錯誤處理與日誌。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, C-Q5, A-Q5

C-Q2: 如何在 .NET 中檢查環境是否支援 TxF？
- A簡: 檢查磁碟格式為 NTFS、Windows 版本可用，並以最小 Transacted 操作試探與例外處理。
- A詳: 步驟：1) new DriveInfo("C").DriveFormat 是否為 "NTFS"。2) 判斷 OS 平台為 Windows。3) 以 AlphaFS 的 Transacted API 執行一次小操作（如建立臨時檔），以 try/catch 捕捉 NotSupportedException/Win32Exception。4) 若失敗，切換到替代流程。程式碼片段：
// C#
bool isNtfs = new DriveInfo(@"C").DriveFormat.Equals("NTFS", StringComparison.OrdinalIgnoreCase);
try { if (isNtfs) Alphaleonis.Win32.Filesystem.File.WriteAllTextTransacted(tempPath, "x", Encoding.UTF8); }
catch { /* 回退策略 */ }
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q14, C-Q9, D-Q2

C-Q3: 如何用 AlphaFS 建立交易性目錄與檔案？
- A簡: 呼叫 CreateDirectoryTransacted、WriteAllTextTransacted 類 API，於交易範圍內操作。
- A詳: 步驟：1) using TransactionScope 建立交易。2) 使用 AlphaFS 建立目錄/檔案（Transacted 版本）。3) 完成後 scope.Complete() 提交。示例：
// C#
using (var scope = new TransactionScope()) {
  Alphaleonis.Win32.Filesystem.Directory.CreateDirectoryTransacted(@"C:\txf\data");
  Alphaleonis.Win32.Filesystem.File.WriteAllTextTransacted(@"C:\txf\data\a.txt", "hi", Encoding.UTF8);
  scope.Complete();
}
注意：請依實際 AlphaFS 版本確認 API 名稱；若不支援，需改用替代流程。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, A-Q6, B-Q16

C-Q4: 如何從既有 P/Invoke 遷移至 AlphaFS？
- A簡: 將自訂 TxF P/Invoke 替換為 AlphaFS Transacted API，整合至 TransactionScope，保留回退機制。
- A詳: 步驟：1) 盤點所有 TxF 相關 P/Invoke。2) 對照 AlphaFS 提供的對等 API（Transacted 方法）。3) 用 TransactionScope 包裹呼叫。4) 移除交易句柄管理，保留原錯誤處理與日誌。5) 增加環境檢查與替代方案（避免不支援時中斷）。完成後以單元測試驗證一致性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q11, C-Q8

C-Q5: 如何設定 TransactionScope 的逾時與隔離層級？
- A簡: 使用 TransactionOptions 指定 Timeout 與 IsolationLevel，依負載與一致性需求調整。
- A詳: 範例：
// C#
var opt = new TransactionOptions {
  IsolationLevel = IsolationLevel.ReadCommitted,
  Timeout = TimeSpan.FromSeconds(60)
};
using (var scope = new TransactionScope(TransactionScopeOption.Required, opt)) {
  // 交易內操作
  scope.Complete();
}
注意：逾時過短易回滾；隔離過高影響併發。觀察延遲、鎖等待與錯誤率調整。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q13, D-Q5, B-Q6

C-Q6: 如何將 TxF 交易與 ADO.NET 交易整合？
- A簡: 於同一 TransactionScope 中進行 DB 與 AlphaFS Transacted 操作，避免手動管理多筆交易。
- A詳: 具體做法：1) 建立 TransactionScope。2) 開啟 SqlConnection，直接執行命令（不需手動 SqlTransaction）。3) 用 AlphaFS Transacted API 操作檔案。4) 成功後 Complete。這樣 DB 與檔案會一起由協調器提交或回滾。若需細緻控制，仍可搭配 SqlTransaction，但以 TransactionScope 為主。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, A-Q5, B-Q15

C-Q7: 如何在回滾時清理暫存檔？
- A簡: 將暫存檔也納入同一交易，或以 try/finally 在回滾後執行檔案清理與補償。
- A詳: 最佳作法是讓暫存檔操作也使用 Transacted API，交易回滾會自動撤銷。若有不受交易保護的暫存檔，使用 try/finally：Complete 前失敗則在 finally 刪除；提交後才做交易外的後續處理（如通知）。建議以統一的清理工具/背景工作掃描與移除殘留。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q19, D-Q5

C-Q8: 如何用單元測試驗證檔案+資料庫交易一致性？
- A簡: 設計成功/失敗兩路徑：故意拋例外，確認 DB 與檔案皆回滾；成功時兩者皆存在。
- A詳: 測試步驟：1) 成功案例：執行交易流程，Assert DB 有資料且檔案存在。2) 失敗案例：中途故意拋出例外，Assert DB 無資料且檔案不存在。3) 邊界：測試逾時與重試。4) 清理：使用隔離測試資料庫與臨時目錄，避免互相干擾。可加上雜湊檢查檔案內容。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q20, B-Q7, A-Q12

C-Q9: 在不支援 TxF 的環境，如何達成近似的一致性？
- A簡: 採「寫入暫存→原子改名」與 DB 交易協同、Outbox/補償等策略，實現最終一致。
- A詳: 替代方案：1) 先寫入 temp 檔，同交易完成時以原子改名（同卷 Move）發布；2) DB 內寫入 Outbox 記錄，由背景工作可靠執行檔案步驟；3) 設計補償流程（失敗時刪檔/撤銷 DB）。需確保操作順序與遷移路徑不留下半成品。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q14, B-Q14, D-Q8

C-Q10: 如何在部署環境啟用分散式交易（如需）？
- A簡: 啟用並設定 MSDTC 服務、允許網路存取，配置防火牆與安全性，確保節點互通。
- A詳: 步驟：1) 啟用「Distributed Transaction Coordinator」服務並設為自動。2) 在元件服務（dcomcnfg）中啟用 MSDTC 網路存取、入站/出站。3) 設定防火牆開放 MSDTC 相關埠。4) 依安全策略限制授權帳號。5) 以簡單跨資源交易驗證連通與提交流程。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q18, D-Q1, B-Q5

### Q&A 類別 D: 問題解決類（10題）

D-Q1: 遇到「MSDTC 未啟動」導致交易升級失敗怎麼辦？
- A簡: 啟用 MSDTC 服務與網路存取，配置防火牆，重試交易；或避免升級為分散式。
- A詳: 症狀：TransactionScope 涉及多資源時拋出交易協調器無法使用的例外。原因：MSDTC 服務未啟動、未允許網路存取、防火牆阻擋。解法：啟動服務、在 dcomcnfg 啟用 MSDTC 網路存取、開放埠，重新測試。預防：減少不必要的升級（如重用同一連線），或在單機內使用輕量交易。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q18, C-Q10, B-Q15

D-Q2: 使用 TxF 拋出 NotSupportedException 或相關錯誤怎麼辦？
- A簡: 確認磁碟為 NTFS、系統版本支援，若不支援則切換到替代策略與補償流程。
- A詳: 症狀：呼叫 Transacted API 時拋 NotSupported/Win32 交易不支援錯。原因：非 NTFS、API 不可用、系統設定或版本限制。解法：檢查 DriveFormat、以試探式呼叫判斷支援度、更新至支援的 API/版本。預防：啟動前環境檢查與功能旗標；提供回退（C-Q9）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q14, C-Q2, C-Q9

D-Q3: TransactionScope 一直升級為分散式交易造成效能不佳？
- A簡: 重用同一 DB 連線、避免在同範圍內建立不同連線，縮小交易範圍，降低升級機率。
- A詳: 症狀：每次交易都啟動 MSDTC，延遲上升。原因：多個不同連線字串/資料來源、跨進程資源。解法：在單一 scope 內重用同一 SqlConnection，合併操作；如可行將流程拆段。預防：明確控制連線生命週期、避免不必要的資源加入。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q1, B-Q15, C-Q6

D-Q4: 使用 AlphaFS 遇到 UnauthorizedAccessException？
- A簡: 檢查路徑權限、UAC、檔案鎖；以系統/服務帳號運行或調整 ACL；避免跨卷限制。
- A詳: 症狀：檔案/目錄操作被拒。原因：ACL 權限不足、UAC 限制、檔案被佔用、網路路徑存取限制。解法：確認執行帳號權限、釋放佔用、以系統服務帳號/提權執行、調整 NTFS ACL。預防：部署前設置正確權限與路徑策略；以重試/退避處理暫時性鎖。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q12, C-Q1, C-Q3

D-Q5: 交易逾時導致回滾，如何診斷與解決？
- A簡: 增加逾時、優化 I/O 與 SQL、縮小交易範圍、記錄耗時點並消除瓶頸。
- A詳: 症狀：到達 Timeout 回滾。原因：I/O 慢、SQL 慢、鎖競爭、交易範圍過大。解法：提高 Timeout、優化查詢與索引、將昂貴操作移出交易、分割長交易。預防：監控平均耗時、設定警示，持續調校。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q13, C-Q5, B-Q19

D-Q6: 交易內檔案變更對其他行程不可見，如何處理？
- A簡: 這是預期行為；必要時以快照或交易外讀取機制取得一致視圖，避免髒讀。
- A詳: 症狀：其他程式看不到未提交檔案。原因：TxF 的隔離性保護一致性。解法：若需讀取，將讀者設計為在提交後讀取；或以 VSS 取得快照視圖。預防：清楚定義可見性需求與流程，同步設計生產/消費時點。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q12, B-Q17, A-Q4

D-Q7: 同時大量檔案與資料庫操作導致死鎖或資源競爭？
- A簡: 規範鎖定順序、縮小交易範圍、分批處理、設定合理逾時與重試策略。
- A詳: 症狀：交易互相等待、逾時。原因：鎖順序不一致、大範圍鎖、資源緊張。解法：統一先鎖 DB 再鎖檔案（或反之，一致即可）、分批/排程處理、縮短交易時間、加索引減少鎖競爭。預防：壓力測試找瓶頸，建立重試/避讓機制。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q6, B-Q12, B-Q19

D-Q8: 部署在雲端/容器時發現 TxF 不可用怎麼辦？
- A簡: 改以應用層模式：暫存＋原子改名、Outbox、事件驅動與補償，實現最終一致。
- A詳: 症狀：TxF API 不可用或受限。原因：平台不支援或政策不建議。解法：採 C-Q9 的替代架構：資料庫交易配合檔案暫存/原子 rename；以 Outbox 可靠發送；用事件與補償處理跨界副作用。預防：在設計階段即規劃可移植策略。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q9, B-Q14, A-Q14

D-Q9: P/Invoke 呼叫 CreateFileTransacted 失敗如何排查？
- A簡: 檢查 API 宣告、結構對齊、交易句柄、路徑長度與權限，記錄 GetLastError。
- A詳: 症狀：Win32Exception，錯誤碼顯示參數或存取錯誤。原因：宣告不正確、未附帶交易句柄、長路徑未處理（需 \\?\ 前綴）、權限不足、非 NTFS。解法：對照官方簽章、使用安全宣告、開啟 SE_BACKUP/RESTORE 權限、測試短路徑、確認句柄有效。預防：以 AlphaFS 等封裝取代自訂 P/Invoke。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q10, C-Q4, D-Q4

D-Q10: 升級至新版本 Windows 後 TxF 被標記為不建議使用，如何應對？
- A簡: 保守維護既有路徑，優先評估替代方案（暫存+改名、Outbox、補償），逐步遷移。
- A詳: 症狀：文件標示 TxF 不建議使用或 API 受限。風險：未來相容性與維運成本。解法：短期維持穩定，加入環境檢查與回退；中長期設計與導入替代架構（C-Q9），降低對 OS 特定功能的依賴。預防：在技術選型時保留抽象層，避免硬耦合。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q14, B-Q14, C-Q9

### 學習路徑索引

- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是交易處理（Transaction）？
    - A-Q2: 什麼是 TransactionScope？
    - A-Q3: 什麼是 Transactional NTFS（TxF）？
    - A-Q4: 為什麼要把檔案系統與資料庫結合為單一交易？
    - A-Q6: 什麼是 AlphaFS？
    - A-Q7: AlphaFS 與 System.IO 有何差異？
    - A-Q9: 什麼是 NTFS 的進階功能（VSS、HardLink）？
    - A-Q11: 何謂「單一交易」（跨資源交易）？
    - A-Q12: 結合交易的核心價值是什麼？
    - A-Q15: 什麼是 VSS（Volume Shadow Copy Service）？
    - A-Q16: 什麼是硬連結（HardLink）？
    - B-Q1: TransactionScope 的運作機制是什麼？
    - B-Q2: TxF 如何讓檔案操作具備交易性？
    - B-Q3: TxF 與 TransactionScope 整合的執行流程為何？
    - C-Q3: 如何用 AlphaFS 建立交易性目錄與檔案？

- 中級者：建議學習哪 20 題
    - A-Q5: TxF 與 TransactionScope 的關係是什麼？
    - A-Q8: 什麼是 P/Invoke？在此議題的角色為何？
    - A-Q13: TxF 與資料庫交易有何不同？
    - A-Q18: 什麼是 MSDTC？何時會用到？
    - A-Q19: 什麼是「環境交易」（Ambient Transaction）？
    - A-Q20: 為什麼 AlphaFS 能簡化 TxF 的應用？
    - B-Q4: 使用 AlphaFS 進行 TxF 的技術架構？
    - B-Q5: 兩階段提交（2PC）的原理是什麼？
    - B-Q6: 交易隔離性對檔案與資料庫有何影響？
    - B-Q12: 使用 TxF 的檔案鎖定與可見性如何運作？
    - B-Q13: TransactionScope 的逾時與隔離層級如何影響系統？
    - B-Q16: AlphaFS 與 System.Transactions 的互操作機制？
    - C-Q1: 如何用 TransactionScope + AlphaFS 同步寫入資料庫與檔案？
    - C-Q2: 如何在 .NET 中檢查環境是否支援 TxF？
    - C-Q5: 如何設定 TransactionScope 的逾時與隔離層級？
    - C-Q6: 如何將 TxF 交易與 ADO.NET 交易整合？
    - C-Q7: 如何在回滾時清理暫存檔？
    - C-Q8: 如何用單元測試驗證檔案+資料庫交易一致性？
    - D-Q1: 遇到「MSDTC 未啟動」導致交易升級失敗怎麼辦？
    - D-Q5: 交易逾時導致回滾，如何診斷與解決？

- 高級者：建議關注哪 15 題
    - A-Q14: 何時應避免使用 TxF？
    - B-Q8: 在交易範圍內處理跨執行緒與非受控資源的機制？
    - B-Q9: 資源管理員加入（Enlistment）交易的機制？
    - B-Q10: 以 P/Invoke 使用 TxF API 的流程為何？
    - B-Q11: AlphaFS 如何封裝 P/Invoke 以支援 TxF？
    - B-Q14: TxF 的限制有哪些？
    - B-Q18: 硬連結在交易中的行為如何？
    - B-Q19: 如何設計錯誤處理以確保一致性？
    - B-Q20: 如何在本架構中實作交易記錄與審計？
    - C-Q4: 如何從既有 P/Invoke 遷移至 AlphaFS？
    - C-Q9: 在不支援 TxF 的環境，如何達成近似的一致性？
    - C-Q10: 如何在部署環境啟用分散式交易（如需）？
    - D-Q3: TransactionScope 一直升級為分散式交易造成效能不佳？
    - D-Q8: 部署在雲端/容器時發現 TxF 不可用怎麼辦？
    - D-Q10: 升級至新版本 Windows 後 TxF 被標記為不建議使用，如何應對？