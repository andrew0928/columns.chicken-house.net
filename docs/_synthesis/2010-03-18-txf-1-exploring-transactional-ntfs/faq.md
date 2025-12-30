---
layout: synthesis
title: "[TxF] #1. 初探 Transactional NTFS"
synthesis_type: faq
source_post: /2010/03/18/txf-1-exploring-transactional-ntfs/
redirect_from:
  - /2010/03/18/txf-1-exploring-transactional-ntfs/faq/
---

# [TxF] #1. 初探 Transactional NTFS

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 Transactional NTFS（TxF）？
- A簡: TxF 是一組讓檔案操作具交易（ACID）特性的 Win32 API，而非新檔案系統。
- A詳: Transactional NTFS（TxF）是 Windows 自 Vista/Server 2008 正式提供的「交易式檔案操作」功能。它不是新的檔案系統，而是一組與原有檔案 API 幾乎一對一對應的 Win32 API（如 DeleteFileTransacted、CreateFileTransacted），讓開發者得以用交易（commit/rollback）管理檔案的建立、刪除、寫入等動作。其設計可搭配 DTC 與 .NET 的 TransactionScope，將檔案與資料庫操作整合在同一交易中。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q8, B-Q2, B-Q3

A-Q2: TxF 是新的檔案系統嗎？
- A簡: 不是。TxF 是 API 層級的交易能力，建立在 NTFS 與 KTM 上。
- A詳: TxF 名稱雖含「NTFS」，但它並非取代 NTFS 的新檔案系統。它是建立在 NTFS 之上，由 Kernel Transaction Manager（KTM）提供交易基礎的一組 Win32 API。這些 API 與傳統檔案 API 命名相似，多了 Transacted 後綴。開發者以交易物件包住一連串檔案操作，最後選擇提交或回復，從而在原有 NTFS 上達到交易式效果。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q12, B-Q1

A-Q3: TxF 的核心價值是什麼？
- A簡: 讓檔案操作具 ACID，跨檔案、多步驟操作可一致提交或回復。
- A詳: TxF 核心價值在於為檔案 I/O 帶來資料庫般的 ACID 特性。藉由交易物件包覆多個檔案動作（新增、刪除、改名、寫入），可於所有步驟成功時一次提交，失敗時完整回復，避免部分成功導致狀態不一致。配合 DTC 與 TransactionScope，還可把檔案與資料庫操作放在同一交易中，簡化錯誤處理與恢復邏輯，提升可靠性與一致性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, A-Q14, B-Q5

A-Q4: 為什麼需要在檔案系統上使用交易？
- A簡: 解決多步驟檔案操作的原子性與一致性問題，簡化回復。
- A詳: 傳統檔案 I/O 遇到多檔案或多步驟操作時，若中途失敗，常留下不一致狀態，需額外補償。TxF 讓開發者以交易方式包覆檔案動作，確保全部成功才可見，一旦失敗可回復到原狀，降低錯誤復原與狀態管理成本。對需要跨檔案原子性、與資料庫一致變更、或部署/更新流程的應用特別有益。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q16, B-Q4

A-Q5: TxF 何時首次推出？適用哪些 Windows 版本？
- A簡: 自 Windows Vista 與 Windows Server 2008 正式提供並支援。
- A詳: 依文章說明，TxF 於 Windows Vista/Server 2008 首次正式提供。這表示在這些作業系統與後續版本上，Win32 API 提供了對應的 Transacted 檔案操作。開發者在規劃部署時需確認目標系統版本，並處理在不支援版本上的相容與回退策略（例如偵測 API 是否可用、或切換到非交易替代流程）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q23, D-Q1, D-Q10

A-Q6: TxF 與 Transactional Registry（TxR）有何不同與關聯？
- A簡: 兩者皆提供交易，但 TxR 針對登錄機碼，TxF 針對檔案。
- A詳: TxF 專注於檔案系統操作的交易化；TxR 則是針對 Windows Registry 的交易化。兩者皆建立在 Windows 的交易基礎（KTM）之上，並有相對應的 API。從開發觀點，兩者可在同一交易中協同運作，甚至配合 DTC 與 TransactionScope，把檔案、登錄檔與資料庫的變更整合為單一原子行為。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q10, B-Q18, C-Q7

A-Q7: TxF 與資料庫交易的相同與差異？
- A簡: 相同具 ACID；差異在對象不同、API 不同、隔離細節不同。
- A詳: 相同點是皆追求 ACID：原子性、一致性、隔離性、持久性。差異在於對象（檔案/目錄 vs. 資料表/記錄）、API（Win32 Transacted API vs. SQL/ADO.NET）、隔離行為與衝突解法（檔案層級鎖 vs. 行/頁鎖）。當利用 DTC 與 TransactionScope 整合時，兩者可共處同一交易，達到跨資源的一致提交/回復。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q5, C-Q4

A-Q8: TxF 與傳統 NTFS 檔案 I/O 的差異？
- A簡: TxF 多了交易控制（Commit/Rollback），傳統 I/O 為立即生效。
- A詳: 傳統檔案 I/O 一旦呼叫成功即生效，失敗時需手動清理。TxF 則在交易上下文中執行，變更先暫存於交易，直到 CommitTransaction 後才對系統可見；若 RollbackTransaction，變更將被撤銷。此模式讓多步驟檔案作業具原子性與一致性，代價是增加額外的交易管理與效能開銷。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, B-Q15, D-Q7

A-Q9: TxF 的 API 設計特點是什麼？
- A簡: 與既有檔案 API 幾乎一對一對應，帶 Transacted 後綴。
- A詳: TxF 以熟悉的 Win32 檔案 API 為基礎，新增「Transacted」變體，例如 CreateFileTransacted、DeleteFileTransacted。開發者建立交易物件（CreateTransaction）後，將其句柄傳入這些 API，即可在該交易中執行檔案操作，再以 Commit/Rollback 決定結果。此設計降低學習成本並便於遷移。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, B-Q24, C-Q2

A-Q10: 什麼是 DTC（Distributed Transaction Coordinator）？
- A簡: Windows 的分散式交易協調器，用於跨資源統一提交/回復。
- A詳: DTC 是 Windows 的交易協調服務，能協調多個交易資源管理員（例如資料庫、TxF 檔案系統、TxR 註冊表）在單一分散式交易中一致提交（Two-Phase Commit）或回復。在 .NET 中，當 TransactionScope 涉及多資源或跨界需求時，會升級到 DTC，由其負責協調各資源的一致性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q19, C-Q4

A-Q11: 什麼是 .NET 的 TransactionScope？與 TxF 如何互動？
- A簡: .NET 的交易範圍抽象，可整合 DB、TxF、TxR 至同一交易。
- A詳: TransactionScope 提供宣告式的交易邏輯。程式於 using 區塊內自動參與「環境交易」。當只涉及單一輕量資源，可能為本機交易；當涉及多資源或需跨程序/機器時會升級到 DTC。TxF/TxR 可透過相容 API 與 DTC 一起被納入 TransactionScope，達到跨檔案、登錄、資料庫的一致提交/回復。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q4, D-Q5

A-Q12: 什麼是 KTM（Kernel Transaction Manager）？
- A簡: Windows 內核的交易管理基礎，支撐 TxF 與 TxR 的運作。
- A詳: KTM 是 Windows 內核的交易管理元件，提供建立、管理、提交、回復交易的核心能力。TxF 與 TxR 均建立在 KTM 之上；應用程式透過如 CreateTransaction/CommitTransaction 等 API 與 KTM 互動，再把交易物件傳給具交易性的檔案或註冊表 API，以完成原子化作業。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q18, C-Q2

A-Q13: 本機交易與分散式交易有何差異？
- A簡: 本機限單一資源管理員；分散式由 DTC 協調多資源一致性。
- A詳: 本機交易通常只涵蓋單一資源（例如單純 TxF 檔案操作），低延遲、管理簡單。分散式交易涉及多個資源（檔案、資料庫、註冊表），需要 DTC 以兩階段提交協調一致性。分散式具更高可靠性與一致性保證，但帶來額外的溝通與效能開銷。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, B-Q5, D-Q6

A-Q14: 使用 TxF 能保證哪些 ACID 特性？
- A簡: 原子性與一致性最明顯；隔離與持久性依實作與場景而定。
- A詳: TxF 的提交/回復提供原子性，整組變更同進退；一致性來自交易邏輯與系統保證。隔離性使交易中的變更在提交前不對外可見；持久性依 NTFS 與系統機制確保提交後不喪失。整合 DTC 時，跨資源也以兩階段提交維持 ACID。實務上仍需考量效能、鎖競爭與失敗恢復策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q4, B-Q20

A-Q15: TxF 支援哪些典型檔案操作？
- A簡: 與常見檔案 API 對應的 Transacted 版本，如建立、刪除、開啟。
- A詳: 依設計，TxF 提供與多數常見檔案 API 對應的交易版本，例如 CreateFileTransacted（建立/開啟檔案）、DeleteFileTransacted（刪除檔案）。開發者將交易 handle 傳入，即可把該操作納入交易。多個操作可串接於同一交易內，最後統一提交或回復。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q24, C-Q3, C-Q1

A-Q16: 使用 TxF 的常見應用情境？
- A簡: 多檔案原子更新、部署升級、與資料庫一致性寫入。
- A詳: 典型情境包括：應用程式或資料的多檔案原子更新（避免部分檔案更新導致損壞）；安裝/升級流程（回復機制簡化失敗恢復）；與資料庫操作需保持一致性（檔案與 DB 同時成功或回復）。透過 DTC/TransactionScope，可將跨資源變更納入單一交易。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q4, D-Q7, A-Q4

A-Q17: 何時不建議使用 TxF？
- A簡: 單一步驟簡單 I/O 或對效能極敏感、不需回復的情境。
- A詳: 交易帶來管理與效能開銷，若只有單一檔案、單一步驟且錯誤可容忍或易於補償，使用 TxF 反而複雜。高頻 I/O、超低延遲要求、或平台不支援時，也應避免。可參考「When to Use Transactional NTFS」等指南，權衡可靠性與性能成本。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q18, D-Q7, B-Q12

A-Q18: 使用 TxF 的效能考量為何？
- A簡: 交易管理、日誌與隔離增加額外成本，需謹慎評估。
- A詳: TxF 需要維護交易狀態與日誌，提交或回復會有額外同步成本；隔離也可能造成鎖競爭與等待。對 I/O 密集或延遲敏感的工作負載，效能影響更明顯。最佳實務包括：僅在必要範圍使用交易、減少交易內動作數量與存取時間、分批處理，並搭配效能監測。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q7, B-Q20, B-Q21

A-Q19: 為何 .NET Framework 沒內建 TxF 的 managed library？
- A簡: 文章指出官方未納入，需 P/Invoke 或第三方套件。
- A詳: 根據文章，微軟未將 TxF 正式併入 .NET Framework 的 managed 類別庫。開發者若在 .NET 使用 TxF，常見做法有：C/C++ 呼叫 Win32 API、C# 以 P/Invoke 直接呼叫、或採用第三方包裝（如 AlphaFS）。這使原生類型與資源管理較繁雜，但依然可行。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q20, A-Q22, C-Q2

A-Q20: 使用 TxF 的開發方式有哪些？
- A簡: 原生 C/C++、C# P/Invoke、或第三方 .NET 類庫（如 AlphaFS）。
- A詳: 文章列出三種主要方式：1) 以 C/C++ 直接呼叫 Win32 TxF API；2) 在 C# 以 P/Invoke 宣告並呼叫相關 API；3) 採用非官方第三方類庫進行包裝（例如 AlphaFS），提供更 .NET 風格的 API 與額外功能。各有權衡：原生最直接，但跨語言整合不便；P/Invoke 夠靈活但易出現封送問題；第三方易用性高但需評估維護性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, C-Q6, D-Q9

A-Q21: 什麼是 P/Invoke？在 TxF 中為何常見？
- A簡: .NET 呼叫原生 Win32 函式的機制；TxF 多以此方式使用。
- A詳: P/Invoke（Platform Invocation Services）讓受管程式碼（如 C#）能呼叫原生 DLL 函式。因 TxF 未內建於 .NET Managed 類庫，開發者常以 P/Invoke 宣告 CreateTransaction、CommitTransaction、DeleteFileTransacted 等 API，直接使用交易機制。好處是立即可用，風險是簽章與記憶體/資源管理需特別謹慎。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, D-Q9, B-Q8

A-Q22: AlphaFS 是什麼？可解決哪些問題？
- A簡: 提供進階 Windows 檔案系統支援的 .NET 套件，含 TxF 能力。
- A詳: AlphaFS 是一個開源專案，目標可替換 System.IO.* 命名空間，提供更完整的 Windows 檔案系統能力，包括長路徑、交易式操作（TxF）等。對 .NET 開發者而言，它以 managed 風格包裝原生 API，降低 P/Invoke 的複雜度，讓交易式檔案處理更容易上手並提高可維護性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q6, A-Q20, D-Q9

A-Q23: 文章中的程式碼範例在做什麼？
- A簡: 建立交易後刪除多個檔案，成功提交，失敗回復。
- A詳: 範例先以 CreateTransaction 建立交易物件，接著迴圈使用 DeleteFileTransactedW 刪除多個目標檔案。若任一刪除失敗，拋出例外並呼叫 RollbackTransaction 回復；全數成功則 CommitTransaction 提交。最後以 CloseHandle 釋放資源。示範了多步驟檔案操作的原子性封裝。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, B-Q15, D-Q3

A-Q24: TxF 與 TxFS 名稱上的差異？
- A簡: 常見縮寫為 TxF；早期文獻偶見 TxFS，皆指交易式 NTFS。
- A詳: 文章提到 TxF 的中文稱為交易式 NTFS，縮寫為 TxF；早期也有人寫成 TxFS。兩者在社群文章中常指同一技術，不必太執著於縮寫差異。正式文件多以 TxF 稱呼。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1

A-Q25: TxF 是否能與資料庫操作同一交易中執行？
- A簡: 可以。透過 DTC 與 TransactionScope，可整合檔案與資料庫。
- A詳: 文章指出，配合 DTC 等交易協調器，檔案處理與資料庫處理可包裝成單一交易。於 .NET 中，可使用 TransactionScope 在同一範圍內執行 SQL 操作與 TxF 檔案操作；若涉及多資源，TransactionScope 會升級到 DTC，確保提交/回復一致。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, A-Q11, C-Q4

A-Q26: TxR 的使用情境與價值？
- A簡: 在需要原子化更新登錄設定的情境中，提供回復能力。
- A詳: 當應用程式需一次性更新多個註冊表鍵值（例如安裝設定、功能開關），TxR 能將變更包在交易中，確保全部成功或還原到初始狀態。與 TxF 類似，它降低自寫補償邏輯的複雜度；與 DTC/TransactionScope 搭配時，還能與檔案、資料庫變更協同一致。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, C-Q7, B-Q10

A-Q27: TxF 對既有程式碼遷移的影響？
- A簡: 需改用 Transacted API 並導入交易管理與資源處理。
- A詳: 遷移時，原本的檔案 API 呼叫點需替換為對應的 Transacted 版本；並在流程上加入 CreateTransaction、Commit/Rollback、Handle 管理與錯誤處理。若採 .NET，可能需新增 P/Invoke 或引入第三方封裝（如 AlphaFS）。測試上也要新增提交/回復的案例驗證一致性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q8, C-Q10, D-Q9

A-Q28: 使用 TxF 需要哪些前置條件？
- A簡: 支援版本的 Windows、正確 API/DLL、適當權限與錯誤處理。
- A詳: 需在支援 TxF 的 Windows 版本上執行（如 Vista/Server 2008 與後續），正確載入相關 DLL（如 KtmW32、Kernel32 的 Transacted 函式），以適當權限存取目標檔案/資料夾，並妥善處理交易生命週期（建立、提交、回復、釋放）。若納入 DTC，還需啟用並設定 MSDTC 服務。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q1, D-Q6, C-Q5

---

### Q&A 類別 B: 技術原理類

B-Q1: TxF 的基本運作原理是什麼？
- A簡: 以 KTM 管理交易，Transacted API 在提交前隔離變更，提交後可見。
- A詳: TxF 建立於 Kernel Transaction Manager（KTM）之上。應用程式透過 CreateTransaction 取得交易物件，並將其句柄傳入對應的 Transacted 檔案 API。這些操作在交易上下文中執行，變更先被隔離與記錄。當呼叫 CommitTransaction，系統將變更原子化地套用；若 RollbackTransaction，則撤銷變更。整體由 KTM 與 NTFS 支撐。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q3, B-Q4

B-Q2: Transacted 檔案 API 的執行流程為何？
- A簡: 建立交易→呼叫 Transacted API→檢查回傳→提交或回復→釋放。
- A詳: 典型流程：1) CreateTransaction 建立交易物件；2) 以該交易句柄呼叫 Transacted API（如 CreateFileTransacted、DeleteFileTransacted）；3) 檢查錯誤碼，必要時拋出例外；4) 全部成功後呼叫 CommitTransaction；5) 失敗則 RollbackTransaction；6) 最終以 CloseHandle 釋放交易與相關資源。流程清楚可保障原子性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, C-Q1, C-Q3

B-Q3: CreateTransaction/Commit/Rollback 的機制是什麼？
- A簡: 建立交易上下文，提交套用變更，回復撤銷，皆由 KTM 管理。
- A詳: CreateTransaction 由 KtmW32.dll 提供，回傳交易句柄供後續 API 使用。CommitTransaction 觸發交易完成，系統將已記錄的變更原子化地永久寫入，對外可見；RollbackTransaction 則根據交易日誌撤銷變更。這些動作由 KTM 與 NTFS 合作完成，確保一致性與原子性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, C-Q2, D-Q3

B-Q4: 在 TxF 中的隔離與可見性如何運作？
- A簡: 交易中的變更對其他程序不可見，直到提交後才公開。
- A詳: TxF 的交易隔離意味著在交易尚未提交前，其他程序或不在該交易中的操作無法看見交易內的變更。提交後，變更一次性生效並對外可見；回復則完全撤銷，使外界仿若未曾操作。此機制降低外部觀察到中間狀態的風險，簡化一致性維護。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, A-Q8, D-Q8

B-Q5: 如何以 DTC 協調 TxF 與資料庫？
- A簡: 透過兩階段提交，由 DTC 將 TxF 與 DB 納入同一分散式交易。
- A詳: 當一個交易同時涉及 TxF（檔案）與資料庫時，可由 DTC 擔任協調者。各資源先進行預備（prepare），若都可提交，DTC 發出 commit 指令使變更同時生效；有任一資源無法提交，DTC 指示全部回復。這確保跨資源一致性，避免部分提交的情況。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, A-Q25, C-Q4

B-Q6: TransactionScope 的環境交易與升級機制是什麼？
- A簡: using 範圍內自動加入交易，跨多資源時可升級到 DTC。
- A詳: TransactionScope 提供環境交易（ambient transaction），程式碼在 using 區塊內呼叫相容的資源時會自動加入該交易。當只涉及單一資源可維持本機交易；當加入第二個資源或需跨程序/電腦時，會升級到 DTC，由其統籌兩階段提交，以維持跨資源一致性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q5, D-Q5

B-Q7: 交易內的檔案 Handle 應如何管理？
- A簡: 僅在交易有效期間使用，提交/回復後釋放並避免洩漏。
- A詳: 在使用 Transacted API 開啟檔案後，相關 Handle 與交易生命週期關聯緊密。應僅於交易有效期間使用，提交或回復後儘速關閉。建議使用安全的封裝或 finally 區塊確保 CloseHandle 被呼叫，避免資源洩漏或鎖未釋放導致後續操作受阻。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q1, C-Q3, D-Q4

B-Q8: P/Invoke 呼叫 DeleteFileTransacted 的關鍵點？
- A簡: 正確 DLL、字元集與 SetLastError，並傳入交易句柄。
- A詳: DeleteFileTransacted 定義於 Kernel32.dll。宣告時需指定 CharSet.Unicode（或使用 W 版本）、SetLastError=true，以便取得錯誤碼。呼叫時務必傳入 CreateTransaction 取得的交易句柄。回傳失敗時用 Marshal.GetLastWin32Error 診斷。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q2, D-Q9, D-Q1

B-Q9: 使用 TxF 時錯誤回傳與錯誤碼解讀流程？
- A簡: 檢查 API 回傳/LastError，決定提交或回復並記錄。
- A詳: 每次 Transacted API 呼叫後，先檢查回傳值；若失敗，呼叫 GetLastError（.NET 用 Marshal.GetLastWin32Error）取得錯誤碼，據以判斷是權限、路徑、共享衝突或交易錯誤。若交易內任何一步失敗，應回復整體交易並記錄，以利後續重試或人工分析。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q2, D-Q3, D-Q7

B-Q10: TxR 的架構與 TxF 的共通機制？
- A簡: 皆建於 KTM，提供交易物件與提交/回復的 API 模型。
- A詳: TxR 與 TxF 都使用 KTM 的交易物件與同樣的生命週期（建立、提交、回復）。差異是操作對象不同：TxR 面向 Registry，而 TxF 面向檔案系統。從設計觀點，兩者在錯誤處理、隔離與一致性上共享概念，方便在同一交易中協同。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, C-Q7, B-Q18

B-Q11: 交易範圍與跨執行緒/跨程序的行為？
- A簡: 交易句柄可在同程序內共享；跨界需依協定與 DTC 協調。
- A詳: 一般在同一程序內，多執行緒可傳遞與重用交易句柄，但需確保同步與生命週期管理。跨程序或跨電腦的交易協調則倚賴 DTC 與資源管理員的協議。TransactionScope 會在需要時自動升級以支援此類跨界協調。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q5, B-Q6, D-Q6

B-Q12: 混用交易式與非交易式 I/O 的風險？
- A簡: 可能讀到未提交狀態或破壞原子性，須避免交叉操作。
- A詳: 若在交易進行中同時對同一資源使用非交易式 I/O，可能觀察到不一致，或導致鎖競爭與不可預期結果。最佳實務是對同一批次的目標檔案，統一使用交易式 API，並在提交/回復前避免外部非交易式干擾。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q8, A-Q17, B-Q4

B-Q13: TxF 與 .NET 的資源處理（IDisposable/using）如何搭配？
- A簡: 以包裝類型管理 IntPtr/Handle，using 確保釋放。
- A詳: 因 TxF 在 .NET 需用 P/Invoke 取得非受管資源句柄，建議封裝為 SafeHandle 或自訂 IDisposable 類型，於 Dispose 中呼叫 CloseHandle。將交易物件與檔案 handle 置於 using 區塊內，避免洩漏與鎖未釋放的問題，提升可靠性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q8, D-Q4, A-Q21

B-Q14: AlphaFS 如何包裝 Win32 TxF API？
- A簡: 以 managed 風格提供交易式檔案操作，減少 P/Invoke。
- A詳: AlphaFS 目標是替換 System.IO.*，並加入 Windows 特有功能。對 TxF，通常以類別與方法多載接受「交易物件」或內部管理 KTM 交易，使開發者以 .NET 風格呼叫檔案 API，降低宣告與封送成本，並提供更多便捷功能。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q22, C-Q6, A-Q20

B-Q15: 刪除多個檔案的交易流程設計？
- A簡: 先建交易，逐一 Transacted 刪除，全成則提交，不然回復。
- A詳: 流程包含：CreateTransaction→for 迴圈呼叫 DeleteFileTransacted→任何一步失敗即捕獲→RollbackTransaction→釋放；若全部成功→CommitTransaction→釋放。此模式將一批刪除視為原子操作，避免只刪部分檔案的半完成狀態。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, A-Q23, D-Q3

B-Q16: Transacted 的檔案建立/寫入流程？
- A簡: CreateFileTransacted 開啟/建立，寫入後依結果提交或回復。
- A詳: 以 CreateFileTransacted 開啟或建立檔案（含存取模式、共享、旗標），取得 handle 後呼叫 WriteFile 等寫入 API（或對應包裝）。完成所有寫入與驗證後，如果都成功則 CommitTransaction；若有錯誤則 Rollback。最後關閉檔案與交易句柄。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q3, D-Q2, B-Q7

B-Q17: 交易的超時與取消如何處理？
- A簡: CreateTransaction 可設定超時；也可手動回復作為取消。
- A詳: 建立交易時可指定超時（如 API 參數），逾時可能導致交易自動失敗並需回復。應用也可在邏輯上偵測條件後主動呼叫 RollbackTransaction 作為取消機制。務必加強錯誤處理與日誌，以便診斷與重試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q3, D-Q4, C-Q9

B-Q18: KTM 在 TxF/TxR 中扮演什麼角色與物件關係？
- A簡: KTM 提供交易物件與生命週期，TxF/TxR 作為資源管理員。
- A詳: KTM 管理交易物件（建立、提交、回復）的核心機制；TxF 與 TxR 則是具體的資源管理員，接受交易並於內部維護變更與日誌。應用程式與 KTM 互動以驅動交易，並將交易句柄帶至 TxF/TxR API 完成資源操作。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q1, B-Q10, A-Q12

B-Q19: DTC 網路交易的元件與通訊路徑？
- A簡: 應用程式、DTC 服務、各資源管理員，透過兩階段提交協同。
- A詳: 當交易跨程序/機器時，應用透過 TransactionScope 與 DTC 建立關聯。DTC 與各資源管理員（如 DB、TxF、TxR）通訊，先 prepare 再 commit/abort。網路與安全設定（防火牆、服務狀態）會影響通訊。失敗需重試或回復。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: D-Q6, A-Q10, B-Q6

B-Q20: TxF 的日誌與恢復（高層次）機制？
- A簡: 交易期間維護變更記錄，提交套用，回復依記錄撤銷。
- A詳: 在交易進行中，系統會維護足以回復或套用變更的記錄。提交時依序原子化地更新實體狀態；回復時依日誌撤銷。這讓應用能在失敗或當機後恢復一致狀態。實務上須平衡日誌開銷與恢復需求。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q14, D-Q4, D-Q7

B-Q21: 交易衝突與重試策略？
- A簡: 避免長交易，縮小範圍，衝突時回復後延遲重試。
- A詳: 當多交易競爭相同檔案或目錄時，可能出現共享違規或鎖衝突。策略包括縮短交易時間、減少交易內動作、排序與分批處理；失敗時回復交易並根據錯誤碼使用退避（backoff）重試，降低活鎖風險。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q7, D-Q8, B-Q4

B-Q22: 安全/ACL 在交易中的評估時點？
- A簡: 與一般 I/O 相同，根據呼叫時權限評估並套用。
- A詳: 交易不繞過安全性。TxF 操作會依當前安全內容（使用者權限、ACL）進行權限檢查。若權限不足，Transacted API 會返回錯誤。提交/回復不改變權限要求；因此在進入交易前應確認對目標資源擁有足夠權限。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q2, A-Q28, C-Q1

B-Q23: 版本支援與回退行為該如何處理？
- A簡: 啟動前偵測支援，失敗時改用非交易流程或跳過功能。
- A詳: 部署到不支援 TxF 的系統時，呼叫 Transacted API 可能失敗或找不到進入點。應在啟動或功能入口偵測 API 可用性與 OS 版本，必要時切換到非交易替代方案，或通知使用者功能限制，確保可預期行為。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q1, D-Q10, C-Q5

B-Q24: 常見 API 對應表與命名規則（Transacted 後綴）？
- A簡: 多數檔案 API 有 Transacted 變體，如 Create/Copy/Delete。
- A詳: 命名上通常是在原 API 名稱後加入「Transacted」，例如 CreateFile→CreateFileTransacted，DeleteFile→DeleteFileTransacted。使用時多一個交易句柄參數。這讓開發者可直觀將既有流程切換到交易式版本，維持 API 使用習慣。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, C-Q3, C-Q1

---

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何用 P/Invoke 在 C# 實作刪除多檔案的交易？
- A簡: 建交易→逐一 DeleteFileTransacted→成功提交，否則回復。
- A詳: 
  - 實作步驟: 1) CreateTransaction 建交易；2) 迴圈呼叫 DeleteFileTransacted；3) 任一步驟失敗則 Rollback，成功則 Commit；4) finally 釋放。 
  - 程式碼片段:
    [DllImport("KtmW32.dll", SetLastError=true)]
    static extern IntPtr CreateTransaction(IntPtr lpAttr, IntPtr uow, uint opt, uint iso, uint res, uint ms, string desc);
    [DllImport("KtmW32.dll", SetLastError=true)]
    static extern bool CommitTransaction(IntPtr hTx);
    [DllImport("KtmW32.dll", SetLastError=true)]
    static extern bool RollbackTransaction(IntPtr hTx);
    [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
    static extern bool DeleteFileTransacted(string lpFileName, IntPtr hTx);
    // 流程同文章示例
  - 注意: 檢查 GetLastWin32Error；確保 CloseHandle；處理不支援情況。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q23, B-Q8, D-Q3

C-Q2: 如何宣告 CreateTransaction/Commit/Rollback 等 P/Invoke 簽章？
- A簡: 來自 KtmW32.dll 與 kernel32.dll，注意 SetLastError/Unicode。
- A詳: 
  - 簽章:
    [DllImport("KtmW32.dll", SetLastError=true)] static extern IntPtr CreateTransaction(IntPtr, IntPtr, uint, uint, uint, uint, string);
    [DllImport("KtmW32.dll", SetLastError=true)] static extern bool CommitTransaction(IntPtr);
    [DllImport("KtmW32.dll", SetLastError=true)] static extern bool RollbackTransaction(IntPtr);
    [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)] static extern bool DeleteFileTransacted(string, IntPtr);
  - 關鍵: 指定 CharSet；布林回傳對應 Win32 BOOL；用 Marshal.GetLastWin32Error 取錯誤碼；以 SafeHandle/IDisposable 包裝資源。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, B-Q13, D-Q9

C-Q3: 如何用 CreateFileTransacted 寫入檔案並可回滾？
- A簡: 交易中開檔→寫入→成功提交，失敗回復，皆用 Transacted API。
- A詳: 
  - 步驟: 1) hTx=CreateTransaction；2) hFile=CreateFileTransacted(..., hTx)；3) WriteFile/WriteFileEx 寫入；4) 成功則 CommitTransaction，失敗則 Rollback；5) 關閉 handle。
  - 程式碼:
    [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
    static extern SafeFileHandle CreateFileTransacted(string path, uint access, uint share, IntPtr sa, uint disp, uint flags, IntPtr tpl, IntPtr hTx, IntPtr mini, IntPtr ext);
  - 注意: 權限與旗標設定、錯誤處理、釋放 SafeFileHandle。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q16, D-Q2, B-Q7

C-Q4: 如何用 TransactionScope 整合檔案刪除與 SQL 寫入？
- A簡: using TransactionScope，內含 DB 操作與 TxF 操作，最後 Complete。
- A詳: 
  - 步驟: 1) using (var scope=new TransactionScope())；2) 執行 ADO.NET 寫入；3) 執行 TxF（可透過包裝或第三方庫呼叫 Transacted API）；4) scope.Complete() 提交；未呼叫則回復。
  - 程式碼片段:
    using (var scope = new TransactionScope()) {
      // DB: SqlConnection + SqlCommand
      // File: 呼叫 DeleteFileTransacted 或 AlphaFS 交易方法
      scope.Complete();
    }
  - 注意: 可能升級到 DTC；需啟用 MSDTC；處理例外即回復。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q25, B-Q5, D-Q5

C-Q5: 如何在程式中選擇本機 TxF 或 DTC 升級？
- A簡: 先使用本機交易；多資源時讓 TransactionScope 自動升級。
- A詳: 
  - 步驟: 1) 若僅檔案操作，使用 KTM 本機交易（CreateTransaction）；2) 若同時含 DB/Registry，建議以 TransactionScope 包覆，讓系統判斷是否升級到 DTC；3) 於啟動檢查 MSDTC 狀態；4) 設計回退機制。
  - 注意: 減少不必要的升級；在測試環境驗證 DTC 通訊設定。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q23, D-Q6

C-Q6: 如何以 AlphaFS 進行交易式檔案操作？
- A簡: 使用 AlphaFS 提供之交易化方法或交易物件，多為 .NET 風格。
- A詳: 
  - 步驟: 1) 引入 AlphaFS 套件；2) 使用其檔案 API（位於 Alphaleonis.Win32.Filesystem 命名空間）與交易支援（如傳入交易物件的多載）；3) 以 using 確保釋放；4) 失敗時回復。
  - 程式碼片段: 依 AlphaFS 版本，常見為 File/Directory 方法的交易多載。
  - 注意: 參閱專案文件確認對應 API 與行為；版本相容性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q22, B-Q14, D-Q9

C-Q7: 如何用 TxR 在交易內修改多個 Registry 值？
- A簡: 建交易→呼叫交易化的 Registry API→成功提交，否則回復。
- A詳: 
  - 步驟: 1) hTx=CreateTransaction；2) 透過 TxR 對應 API（Windows Registry 的 Transacted 版本）設定多個鍵值；3) 全數成功則 CommitTransaction；失敗則 RollbackTransaction。
  - 注意: 權限（需可寫入 Registry 分支）、錯誤處理、避免與非交易式修改混用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q10, D-Q2

C-Q8: 如何封裝 TxF 為可重用的 .NET 元件（簡版）？
- A簡: 建立 IDisposable 交易類別，內部封裝 Create/Commit/Rollback。
- A詳: 
  - 步驟: 1) 建 TransactionScope-like 類別，持有 IntPtr hTx；2) 在 ctor 呼叫 CreateTransaction；3) Commit/Dispose 中分別呼叫 CommitTransaction/CloseHandle；4) 提供包裝方法呼叫 Transacted API；5) 使用 using 管理生命週期。
  - 注意: SafeHandle、例外安全、記錄錯誤碼與可觀測性。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q13, D-Q4, D-Q9

C-Q9: 如何為 TxF 操作加入健全的錯誤處理與日誌？
- A簡: 檢查回傳/錯誤碼，統一回復交易，記錄上下文與重試策略。
- A詳: 
  - 步驟: 1) 每次呼叫後取得錯誤碼；2) 失敗即回復交易並記錄檔案路徑、動作、錯誤碼、堆疊；3) 視錯誤類型決定退避重試；4) 將交易 ID 與相依資源狀態一併記錄，便於追蹤。
  - 注意: 避免吞例外；將提交/回復結果也納入日誌。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, D-Q7, D-Q3

C-Q10: 如何撰寫單元測試驗證 TxF 的提交與回滾？
- A簡: 準備測試檔案→執行交易→驗證提交可見、回復無副作用。
- A詳: 
  - 步驟: 1) 建立測試資料夾與檔案；2) 測試提交路徑：交易內變更後 Commit，斷言檔案狀態；3) 測試回復路徑：於交易中故意觸發錯誤並 Rollback，斷言檔案未變；4) 清理環境。
  - 注意: 隔離測試環境；在不支援系統跳過測試或改為非交易測試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q23, D-Q10, A-Q27

---

### Q&A 類別 D: 問題解決類（10題）

D-Q1: 遇到 EntryPointNotFoundException 呼叫 Transacted API 怎麼辦？
- A簡: 檢查 OS 支援與 DLL 名稱、API 簽章；必要時採回退策略。
- A詳: 症狀: P/Invoke 找不到函式入口。原因: OS 版本不支援、DLL 名稱/位元數錯、函式簽章不符。解法: 確認目標系統（Vista/Server 2008+）、CreateTransaction 來自 KtmW32.dll、其他 Transacted 來自 kernel32.dll；檢視 CharSet/CallingConvention。提供偵測機制，在不支援時使用非交易流程。預防: 啟動時做功能檢測與記錄。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q23, C-Q2, A-Q5

D-Q2: 刪除或寫入回報 Access Denied 怎麼辦？
- A簡: 檢查 ACL/鎖定/共享模式與提升權限，必要時重試或調整流程。
- A詳: 症狀: API 失敗，LastError 顯示存取被拒。可能原因: 權限不足、檔案被占用、共享模式不匹配。解法: 以具權限帳號執行或調整 ACL；關閉占用檔案的程序；用正確的 DesiredAccess/ShareMode 開啟。預防: 事前檢查權限與鎖狀態，設計重試與退避。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q22, B-Q16, C-Q3

D-Q3: CommitTransaction 失敗或回傳錯誤如何處理？
- A簡: 取得錯誤碼分析狀態，若不可恢復則回復並記錄重試策略。
- A詳: 症狀: 提交回傳 false。原因: 資源衝突、超時、內部錯誤。解法: 用 GetLastError 判定是否可重試；可重試則回復後延遲重試；不可重試則回復並標記失敗，通知上游。預防: 縮短交易時間、降低衝突、設定合理超時並監控。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q17, B-Q21, C-Q9

D-Q4: RollbackTransaction 發生例外或資源未釋放？
- A簡: 確保 finally 釋放 Handle；若回復失敗，作業層面補償。
- A詳: 症狀: 回復時拋例外或句柄洩漏。原因: 句柄管理不當、重入問題。解法: 以 using/IDisposable 包裝，於 finally 釋放；回復失敗時記錄並採補償（如重新比對檔案狀態並清理）。預防: 封裝資源與一致的錯誤流程，加入測試覆蓋。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q13, C-Q8

D-Q5: 使用 TransactionScope 時出現「交易升級到 DTC」造成失敗？
- A簡: 啟用 MSDTC、開放防火牆、檢查網路 DTC 設定與授權。
- A詳: 症狀: TransactionScope 自動升級後提交失敗。原因: MSDTC 服務未啟用、網路/防火牆阻擋、DTC 安全設定不符。解法: 啟動與設定 MSDTC；允許網路 DTC 存取；調整防火牆；確認機器雙向可通。預防: 部署前腳本化檢查與設定，納入健康監控。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q19, C-Q4

D-Q6: DTC 整合時無法連線或分散式交易失敗？
- A簡: 檢查服務狀態、名稱解析、雙向通訊與時鐘同步。
- A詳: 症狀: 跨機交易 prepare/commit 超時或失敗。原因: 服務停用、DNS/Hosts 問題、雙向 RPC 被阻、時鐘偏差。解法: 啟用 DTC、檢視事件記錄、測試 RPC、校時、調整安全/防火牆。預防: 標準化環境設定與監控告警。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q19, A-Q13, C-Q5

D-Q7: TxF 效能不佳的可能原因與優化方式？
- A簡: 交易與日誌開銷、鎖競爭；縮小交易範圍、分批與重試。
- A詳: 症狀: 延遲升高、吞吐下降。原因: 交易日誌與提交成本、長交易鎖定、I/O 爭用。解法: 縮短交易時間、減少交易內作業數、批次處理、避開尖峰；只在必要時使用交易。預防: 基準測試與監控，持續調整參數與架構。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q18, B-Q21, C-Q9

D-Q8: 混用交易式與非交易式 API 導致不可預期結果怎麼辦？
- A簡: 統一使用交易式 API，隔離交易期間外部存取。
- A詳: 症狀: 看到中間狀態或操作失敗。原因: 非交易式存取讀到未提交變更，或造成共享衝突。解法: 在交易期間對同一資源一律使用交易式 API，並限制外部非交易存取。預防: 設計存取層抽象，避免混用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, B-Q4, C-Q8

D-Q9: P/Invoke 簽章錯誤造成隨機崩潰如何診斷？
- A簡: 核對 DLL/函式簽章、字元集、呼叫慣例與結構封送。
- A詳: 症狀: 間歇性崩潰、回傳值異常。原因: 簽章不正確（參數型別/順序、CharSet、BOOL 對應）、呼叫慣例不符。解法: 對照官方文件修正；加上 SetLastError；改用 SafeHandle；以 x86/x64 各別測試。預防: 封裝重用、撰寫小型驗證程式。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q2, B-Q13, A-Q21

D-Q10: 程式在不同 Windows 版本行為不一致？
- A簡: 檢查 API 可用性，加入能力偵測與功能回退。
- A詳: 症狀: 在某些版本成功，另一些版本失敗。原因: OS 支援差異、API 行為差異。解法: 啟動時檢測 TxF 支援；以反射/動態載入或版本檢查決定是否啟用；提供非交易替代流程或禁用相關功能。預防: 在目標版本矩陣全面測試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q23, C-Q10, A-Q28

---

### 學習路徑索引

- 初學者：建議先學習 15 題
  - A-Q1: 什麼是 Transactional NTFS（TxF）？
  - A-Q2: TxF 是新的檔案系統嗎？
  - A-Q3: TxF 的核心價值是什麼？
  - A-Q4: 為什麼需要在檔案系統上使用交易？
  - A-Q5: TxF 何時首次推出？適用哪些 Windows 版本？
  - A-Q6: TxF 與 Transactional Registry（TxR）有何不同與關聯？
  - A-Q8: TxF 與傳統 NTFS 檔案 I/O 的差異？
  - A-Q9: TxF 的 API 設計特點是什麼？
  - A-Q10: 什麼是 DTC（Distributed Transaction Coordinator）？
  - A-Q11: 什麼是 .NET 的 TransactionScope？與 TxF 如何互動？
  - A-Q15: TxF 支援哪些典型檔案操作？
  - A-Q16: 使用 TxF 的常見應用情境？
  - A-Q22: AlphaFS 是什麼？可解決哪些問題？
  - A-Q23: 文章中的程式碼範例在做什麼？
  - B-Q2: Transacted 檔案 API 的執行流程為何？

- 中級者：建議學習 20 題
  - A-Q7: TxF 與資料庫交易的相同與差異？
  - A-Q13: 本機交易與分散式交易有何差異？
  - A-Q14: 使用 TxF 能保證哪些 ACID 特性？
  - A-Q17: 何時不建議使用 TxF？
  - A-Q18: 使用 TxF 的效能考量為何？
  - A-Q20: 使用 TxF 的開發方式有哪些？
  - A-Q21: 什麼是 P/Invoke？在 TxF 中為何常見？
  - A-Q28: 使用 TxF 需要哪些前置條件？
  - B-Q1: TxF 的基本運作原理是什麼？
  - B-Q3: CreateTransaction/Commit/Rollback 的機制是什麼？
  - B-Q4: 在 TxF 中的隔離與可見性如何運作？
  - B-Q5: 如何以 DTC 協調 TxF 與資料庫？
  - B-Q6: TransactionScope 的環境交易與升級機制是什麼？
  - B-Q8: P/Invoke 呼叫 DeleteFileTransacted 的關鍵點？
  - B-Q12: 混用交易式與非交易式 I/O 的風險？
  - C-Q1: 如何用 P/Invoke 在 C# 實作刪除多檔案的交易？
  - C-Q2: 如何宣告 CreateTransaction/Commit/Rollback 等 P/Invoke 簽章？
  - C-Q4: 如何用 TransactionScope 整合檔案刪除與 SQL 寫入？
  - D-Q1: 遇到 EntryPointNotFoundException 呼叫 Transacted API 怎麼辦？
  - D-Q7: TxF 效能不佳的可能原因與優化方式？

- 高級者：建議關注 15 題
  - B-Q10: TxR 的架構與 TxF 的共通機制？
  - B-Q11: 交易範圍與跨執行緒/跨程序的行為？
  - B-Q14: AlphaFS 如何包裝 Win32 TxF API？
  - B-Q16: Transacted 的檔案建立/寫入流程？
  - B-Q17: 交易的超時與取消如何處理？
  - B-Q18: KTM 在 TxF/TxR 中扮演什麼角色與物件關係？
  - B-Q19: DTC 網路交易的元件與通訊路徑？
  - B-Q20: TxF 的日誌與恢復（高層次）機制？
  - B-Q21: 交易衝突與重試策略？
  - C-Q3: 如何用 CreateFileTransacted 寫入檔案並可回滾？
  - C-Q5: 如何在程式中選擇本機 TxF 或 DTC 升級？
  - C-Q6: 如何以 AlphaFS 進行交易式檔案操作？
  - C-Q8: 如何封裝 TxF 為可重用的 .NET 元件（簡版）？
  - D-Q5: 使用 TransactionScope 時出現「交易升級到 DTC」造成失敗？
  - D-Q6: DTC 整合時無法連線或分散式交易失敗？