# .NET Core 跨平台 #2：記憶體管理大考驗（setup environment）FAQ

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

Q1: 什麼是記憶體碎片化（Memory Fragmentation）？
- A簡: 可用空間被切成不連續小塊，無法滿足更大連續配置，導致配置失敗或效能降低。
- A詳: 記憶體碎片化是指雖有足夠總可用記憶體，但連續空間被拆散成許多小區塊，當需要較大連續空間時（如 72MB），因找不到足夠長度的連續區段而失敗。本測試先以 64MB 大量配置，再釋放其中一半製造碎片，再嘗試配置 72MB，檢驗 GC 與執行階段對碎片的處理。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, B-Q4, B-Q8, D-Q8

Q2: 什麼是 OOM（Out Of Memory）？
- A簡: 當進程無法再獲得所需記憶體時發生，.NET 可能拋出 OutOfMemoryException，或被系統直接終止。
- A詳: OOM 是記憶體耗盡或無法滿足配置要求的狀態。在 .NET 中，通常拋出 OutOfMemoryException；但於容器或某些 OS 設定下，可能由 OOM Killer 直接終止進程。測試中透過 while 連續配置直到 OOM，以記錄可配置塊數與行為差異，觀察執行階段在極端情況的保護能力。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, D-Q1, C-Q7

Q3: 什麼是 .NET Core 的垃圾回收（GC）？
- A簡: 自動管理物件生命週期的機制，回收無參照的記憶體，降低手動釋放負擔。
- A詳: .NET GC 以代數（Gen0/1/2）回收短命與長命物件，並有大型物件堆（LOH）。GC 自動回收無用物件並嘗試減少碎片，但 LOH 傳統上不常壓實，易累積碎片。本測試用 Clear() 解參照並強制 GC.Collect，觀察 GC 在碎片情境下的效果與限制。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q14, B-Q3, B-Q8

Q4: 為何用 64MB 與 72MB 區塊進行測試？
- A簡: 先以 64MB 製造碎片，再以更大的 72MB 驗證連續空間不足時的配置行為。
- A詳: 64MB 屬大型物件，會進入 LOH。先連續配置多個 64MB，釋放其中一半形成交錯空洞；接著嘗試配置更大的 72MB 連續空間。若碎片嚴重，雖總空間足夠，也可能找不到足夠大的連續段，反映實務中「大塊配置在碎片環境下易失敗」的現象。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, B-Q4, B-Q8

Q5: 什麼是 LOH（Large Object Heap），與本測試有何關聯？
- A簡: 儲存大型物件的堆區（>~85KB）；較少壓實，易碎片化，與大陣列配置密切相關。
- A詳: LOH 是 .NET 專門放置大型物件的堆區，常見如大型 byte[]。其回收通常隨 Gen2 進行，歷史上預設不壓實或僅在特定條件壓實，故長期容易碎片化。本測試的 64MB/72MB byte[] 全屬 LOH，能直接觀察 LOH 碎片對大塊連續配置成功率與 OOM 的影響。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q8, C-Q8

Q6: 釋放（de-reference）與 GC.Collect 有何差異？
- A簡: 釋放是移除參照；GC.Collect 是請求 GC 立即回收。前者必要，後者不一定需要。
- A詳: de-reference（如 List.Clear()）讓物件成為可回收；GC.Collect(GC.MaxGeneration) 則嘗試立刻執行完整回收。實務上除壓力測試或關鍵階段外不建議頻繁呼叫 Collect；本測試為控制變因、觀察極端情境，才同時採用清參照與強制 GC。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, D-Q3

Q7: 為何要在多平台（Windows、Linux、Container）上測試？
- A簡: 各平台對記憶體、OOM、容器限制處理不同，能顯示執行階段行為差異。
- A詳: 記憶體管理高度仰賴底層 OS/容器。Windows 與 Linux 的分頁、overcommit、映像配置、以及容器的 cgroups 限制皆不同。相同 .NET Core 程式在不同平台可能遇到不同 OOM 行為（拋例外或被殺）、不同回收與壓實效果，因此跨平台驗證能掌握實際差異與風險。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, B-Q7, D-Q7

Q8: 測試程式中的三個 List（buffer1/2/3）用途是什麼？
- A簡: buffer1/2 用於交錯配置 64MB 並釋放一半；buffer3 用於再配置 72MB 檢驗碎片影響。
- A詳: 程式先輪流將 64MB byte[] 放入 buffer1、buffer2，形成交錯分佈；再 Clear() buffer2 並 GC.Collect，造成實質碎片；最後將 72MB 放入 buffer3，測試在碎片化後，較大連續物件的配置成功率與 OOM 行為，並記錄耗時與數量。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q4

Q9: 為何關閉 Hyper-V 動態記憶體（Dynamic Memory）？
- A簡: 避免主機動態調整 VM 記憶體造成干擾，確保各測試條件一致可比。
- A詳: 動態記憶體會因壓力自動擴縮，改變 VM 可用 RAM 與回收行為，易影響 OOM 時點與 GC 表現。本測試追求可重現與公平比較，統一 1GB RAM、4GB swap，關閉動態記憶體，並一次僅開一台 VM，降低跨測試互相干擾。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q13, C-Q1

Q10: 為什麼需要 InitBuffer 隨機填滿記憶體？
- A簡: 透過實際寫入頁面，避免僅保留虛擬保留而未觸發真實承諾，確保測試有效。
- A詳: OS 與執行階段常採延遲承諾（first-touch）或 overcommit 策略；只配置不寫入，實體記憶體可能尚未分配。InitBuffer 以亂數寫滿陣列，強制觸發分頁、零頁填充與承諾，避免高估可用量。程式保留此步驟以便比對「僅配置」與「實際使用」的差異。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q6, C-Q9

Q11: Container 與 VM 的記憶體管理有何差異？
- A簡: 容器靠 cgroups 限制與共享核心；VM 有獨立 OS。容器可能觸發 OOM Killer 而非例外。
- A詳: 容器與主機共用核心，受 cgroups 管控記憶體與 swap；超限時常由 OOM Killer 結束進程。VM 有獨立 OS 與分頁，OOM 行為較接近裸機。相同程式在容器與 VM 會呈現不同 OOM 與統計，故本測試同時涵蓋兩者以觀察差異。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, D-Q1, C-Q7

Q12: .NET Core 與 .NET Framework 在記憶體管理的異同？
- A簡: 核心概念相同（GC/LOH），實作與預設值、平台支援有差異，跨平台行為更豐富。
- A詳: 兩者皆採代數 GC 與 LOH；但 .NET Core 在跨平台、Server GC、背景 GC、容器感知等方面持續演進，對 cgroups 限制、壓實選項與診斷工具支援更友善。行為細節與預設設定可能不同，故同測試在 Core 與 Framework 結果或表徵亦會不同。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, B-Q14

Q13: 為何要統一 VM 規格並一次只開一台？
- A簡: 排除資源競爭與噪音，讓結果僅反映平台差異與程式行為，提升可比性。
- A詳: 記憶體與 IO 是共享資源。若同時多台 VM 競爭，將影響分頁、快取與 swap 行為，造成結果偏差。統一 CPU/RAM/SWAP/磁碟設定並單機跑測試，能將外部因素降至最低，提升數據重現性與跨平台對照的意義。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, C-Q10

Q14: 什麼是 GC 代數（Generation）？與測試關係？
- A簡: 物件依存活時間分代回收。大型物件屬 LOH，通常隨 Gen2 回收，影響碎片行為。
- A詳: GC 將物件分成 Gen0/1/2，短命物件常在 Gen0/1 回收；長命與大型物件（LOH）通常於 Gen2 回收。LOH 的壓實行為與 Gen2 有關，本測試透過 GC.Collect(GC.MaxGeneration) 強制完整回收，觀察 LOH 碎片是否仍阻礙更大配置。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q8

Q15: 本測試要回答哪些核心問題（Why）？
- A簡: 驗證碎片化下 GC/執行階段能否有效回收與防護，以及跨平台行為差異與效能。
- A詳: 目標包括：GC 是否能在碎片情境下維持大塊配置成功率；LOH 碎片影響程度；不同 OS/容器在 OOM 時的保護與表現；強制 GC 的效果與成本；InitBuffer 對真實耗用的影響；以及在統一資源配額下的跨平台差異，為後續最佳化與部署提供依據。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q1, B-Q1, B-Q14

### Q&A 類別 B: 技術原理類

Q1: 測試執行流程如何運作？
- A簡: 先大量配置 64MB，釋放一半並強制 GC，再嘗試配置 72MB，觀察碎片影響與 OOM。
- A詳: 流程分三步：1) while 交錯配置 64MB 直到 OOM（buffer1/2）；2) 清空 buffer2 並 GC.Collect(GC.MaxGeneration)，讓一半區塊可回收，形成交錯空洞；3) 持續配置 72MB（buffer3），統計可成功數量與耗時，藉此觀察 LOH 碎片、GC 回收與平台 OOM 行為。核心組件：List<byte[]>、GC、LOH。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, A-Q4, C-Q6

Q2: .NET 配置大型 byte[] 的內部機制是什麼？
- A簡: 大於 ~85KB 的陣列進入 LOH，需連續空間；回收隨 Gen2 進行，壓實行為受設定影響。
- A詳: 配置大型陣列時，GC 向 LOH 請求連續記憶體。如果可用空間碎裂，即使總量足夠也可能失敗。LOH 回收通常在完整 GC（Gen2）時進行；壓實可透過 API（CompactOnce）或設定啟用。關鍵步驟：尋找連續段、分頁承諾、記錄物件，失敗則拋 OOM 或由 OS 終止。核心：LOH、Gen2、壓實策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q8, C-Q8

Q3: GC.Collect(GC.MaxGeneration) 在測試中的機制與影響？
- A簡: 觸發完整 GC（含 Gen2/LOH 回收），可加速回收，但成本高且未必能消除碎片。
- A詳: 呼叫 GC.Collect(GC.MaxGeneration) 會嘗試執行完整回收與停頓，釋放已無參照的物件。對 LOH 來說，回收並不等於壓實，若沒有啟用 LOH 壓實，碎片仍可能存在。關鍵步驟：標記、清除、可能的壓實。核心組件：代數 GC、LOH、壓實模式。成本：停頓時間、CPU 使用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q8, C-Q8

Q4: 碎片化如何導致 72MB 配置失敗？
- A簡: 雖有足夠總空間，但缺乏足夠長的連續空間，LOH 無法滿足配置需求而失敗。
- A詳: 在交錯釋放後，64MB 空洞彼此分隔，若中間被其他小塊佔據，無法連接成 ≥72MB 連續段。LOH 需要連續空間配置，故會尋找可用段，找不到即失敗。關鍵：連續性要求、非壓實 LOH、free list 分配策略。結果可能是 OOM 例外或 OS OOM 終止。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q4, D-Q2

Q5: InitBuffer 對 OS 承諾/配置機制的影響是什麼？
- A簡: 透過實際寫入頁面觸發分頁錯與承諾，避免僅保留虛擬地址造成虛高的可用量。
- A詳: 多數 OS 採延遲承諾與頁面初次觸發策略。只 new 大陣列未寫入時，有些頁面未實際佔用物理記憶體；寫入則觸發缺頁、中斷、分配零頁與承諾，增加實際 RSS。流程：配置→首次寫→缺頁→承諾→RSS 上升。核心：分頁、零頁、overcommit。確保測試真實反映物理壓力。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q6, C-Q9

Q6: Linux overcommit 與本測試的關聯？
- A簡: overcommit 允許分配超過物理記憶體；實際寫入時才承諾，可能導致晚期 OOM。
- A詳: Linux 可允許進程先獲得大於實體的虛擬配置，直到實際寫入才分配物理頁。測試若未啟用寫入，可能錯估可分配數；啟用 InitBuffer 後才顯示真實極限。超限時，可能觸發 OOM Killer 而非例外。核心：vm.overcommit 設定、cgroups 記憶體限制、RSS 與虛擬記憶體差異。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q2, A-Q10, B-Q7

Q7: 容器中的記憶體限制與 OOM Killer 機制如何運作？
- A簡: cgroups 定義上限；進程超限時由 OOM Killer 根據分數選擇並殺掉，通常無法攔截。
- A詳: 容器透過 cgroups 限制記憶體與 swap；當 RSS+cache 超限，核心評估 oom_score，挑選進程終止，釋放資源。應用端常接不到 OutOfMemoryException。關鍵：--memory/--memory-swap 設定、oom_kill_disable、記錄 dmesg/OOM 日誌。核心組件：cgroups、kernel OOM。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, D-Q1, C-Q7

Q8: LOH 碎片化與壓實（compaction）原理是什麼？
- A簡: LOH 因大型物件移動成本高而較少壓實，可透過設定或 API 觸發一次性壓實。
- A詳: 壓實會移動物件以合併空洞，降低碎片，代價是搬移與停頓。LOH 歷史上預設不壓實，避免長停頓；.NET 可用 GCSettings.LargeObjectHeapCompactionMode=CompactOnce 搭配 GC.Collect 進行一次性壓實。核心：移動成本、停頓、自由清單合併、回收效率。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q8, D-Q8, B-Q3

Q9: List<byte[]> 擴張策略對測試有何影響？
- A簡: List 內部動態擴張自己小陣列（管理用），非主要記憶體成本，影響有限但存在。
- A詳: List 本身透過倍增策略擴張其引用陣列，存放 byte[] 參照；真正耗用是各 64/72MB 陣列。List 擴張少量增加 LOH 外的壓力，對碎片主要影響不大。關鍵步驟：Add 追加、內部 array resize、GC 根保持參照，防止過早回收。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, B-Q10

Q10: 清空 List 是否等於將記憶體歸還給 OS？
- A簡: 不一定。清參照可讓 GC 回收，但記憶體可能留在堆中，未立即歸還 OS。
- A詳: GC 回收會釋放物件讓堆可重用；是否歸還 OS 取決於執行階段策略與頁面狀態。LOH 即使回收也可能留下碎片；堆容量保持以利後續重用。關鍵：堆保留、虛擬/實體頁面、釋放到 OS 條件。需整體觀察 RSS、虛擬記憶體與 GC 計數。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q3, B-Q8

Q11: Server GC 與 Workstation GC 對結果的影響？
- A簡: Server GC 偏向吞吐量與多核心並行，停頓型態不同；對 LOH 行為也可能有差異。
- A詳: Server GC 針對多核心優化，分段堆與並行回收，停頓與分配行為與 Workstation GC 不同。對大型物件回收時間點、背景 GC、堆擴張策略有所影響。可透過 DOTNET_GCServer 控制。選擇不同模式會影響測試中的耗時與瞬時尖峰。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q7, D-Q6

Q12: Windows 與 Linux 容器在 GC 偵測/限制上的差異？
- A簡: Linux 容器依 cgroups；Windows 容器亦支援資源限制，但記憶體度量與回報稍異。
- A詳: Linux 容器使用 cgroups v1/v2 提供嚴格限制，並影響 GC 的容器感知行為；Windows 容器則由 Host OS 管理，記憶體回報與限制 API 路徑不同。GC 在不同平台上的「可見記憶體」資訊影響堆擴張與收縮策略，進而改變 OOM 觸發點。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q7, D-Q4

Q13: 為何設定 SWAP 為 4GB？機制如何？
- A簡: 提供額外後援空間，延後 OOM 觸發，觀察 GC 與分頁行為；但可能造成抖動。
- A詳: SWAP 允許將冷頁換出，釋放實體 RAM；在壓力測試下可延後 OOM，讓程式走到更多配置階段。但過度 swap 會造成 I/O 抖動與延遲。流程：記憶體壓力→頁面選擇→換出→I/O。設定一致有助跨平台公平比較。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q6, C-Q1

Q14: .NET Core 在 OOM 時如何保護應用程式？
- A簡: 嘗試拋出 OutOfMemoryException，讓程式捕捉並釋放資源；容器超限時可能無法保護。
- A詳: 在非容器或未被 OS 強制終止情況，CLR 會拋 OOM 例外，供應用程式清理與降級處理。然而在 cgroups 超限或核心 OOM 情境，進程可能直接被殺，無法進行保護。建議：預留餘裕、監控、分塊配置與重試策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q1, C-Q7

Q15: 為何選擇 1 vCPU、1GB RAM 作為測試基準？
- A簡: 形成明確記憶體壓力，縮短重現時間，並便於不同平台之間對照。
- A詳: 小資源配置更容易觸發 GC 與 OOM，便於觀察差異；同時降低測試成本，提高重現性。搭配 4GB swap 可觀察更多行為分段。此基準有利於對齊各平台資源，聚焦執行階段與 GC 行為，而非硬體效能差異。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, B-Q13

### Q&A 類別 C: 實作應用類（10題）

Q1: 如何在 Hyper-V 建立統一 VM 並關閉動態記憶體？
- A簡: 新建 VM→設定 1 vCPU/1024MB RAM、關閉動態記憶體→設 32GB VHDX→啟用 4GB 交換空間。
- A詳: 步驟：1) Hyper-V 新建 VM（第 1 代/2 代皆可）；2) 設定處理器 1；3) 記憶體 1024MB，取消「啟用動態記憶體」；4) 新建 32GB VHDX；5) 安裝 OS；6) 於 Linux 配置 swapfile（如 dd/ mkswap/ swapon 4G），Windows 可忽略。注意：一次僅開一台 VM，避免互相干擾，解析度設 1366x768 便於觀察。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, B-Q13

Q2: 如何在 Windows Server 2012 R2 安裝 .NET Core 並執行測試？
- A簡: 安裝 .NET SDK→建立/載入專案→編譯執行→觀察輸出與記憶體監控。
- A詳: 步驟：1) 下載安裝 .NET SDK（建議 LTS）；2) dotnet new console -n MemFragTest；3) 貼上範例程式；4) dotnet run；5) 以資源監視器觀察記憶體/RSS。注意：若需比較，設定環境變數 DOTNET_GCServer、COMPlus_GCHeapHardLimit 等保持一致；避免同機其他程式干擾。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q11, C-Q6

Q3: 如何在 Ubuntu 安裝 Docker 並執行 .NET 程式？
- A簡: 安裝 Docker→撰寫 Dockerfile→建置映像→設記憶體限制執行容器→觀察 OOM 行為。
- A詳: 步驟：1) apt-get install docker.io；2) Dockerfile: FROM mcr.microsoft.com/dotnet/runtime:8.0 複製並執行；3) docker build -t memfrag:latest .；4) docker run --memory=1g --memory-swap=5g memfrag；5) dmesg 觀察 OOM 訊息。注意：以 --init 或適當設定接收終止訊號；核對 overcommit 與 cgroups 版本。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, D-Q1

Q4: 如何在 Boot2Docker 環境執行測試？
- A簡: 啟動 Boot2Docker VM→Docker 映像建置→以記憶體上限執行容器→收集日誌與計數。
- A詳: 步驟：1) 啟動 Boot2Docker；2) 使用相同 Dockerfile 建置鏡像；3) docker run -m 1g --memory-swap 5g memfrag；4) 以 docker logs、/var/log/dmesg 蒐集 OOM；5) 比對分配統計輸出。注意：版本偏舊，建議改用現代 Docker Desktop 或原生 Linux，以降低工具鏈差異。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q7

Q5: 如何在 Windows Server 2016（Nano）建立 Windows Container 並執行？
- A簡: 啟用容器功能→拉取 windowsservercore→安裝 .NET 執行→以相同程式測試與記錄。
- A詳: 步驟：1) 啟用 Containers 功能；2) docker pull mcr.microsoft.com/windows/servercore；3) 放入已編譯之 .NET 應用；4) docker run --memory 1g --memory-swap 5g 測試；5) 以事件檢視器觀察終止訊息。注意：TP 版本僅供參考；務必固定鏡像版本與資源上限以便對照。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q12

Q6: 如何用 dotnet CLI 編譯並執行範例程式？
- A簡: dotnet new→貼上程式→dotnet build→dotnet run，觀察 64/72MB 配置統計與耗時。
- A詳: 指令：dotnet new console -n MemFrag; cd MemFrag; 取代 Program.cs 為範例；dotnet build -c Release；dotnet run -c Release。可加上環境變數 DOTNET_GCServer=1 比較模式。注意：釋放步驟需保證 Clear() 後無殘餘參照；避免 JIT 最佳化影響測試段落。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q11

Q7: 如何在容器中設定記憶體上限並觀察 OOM 行為？
- A簡: 使用 --memory/--memory-swap→執行→比對例外與 OOM Killer 日誌，調整限額分析。
- A詳: docker run -m 1g --memory-swap 5g --name mf memfrag；若進程被殺，檢查 dmesg | grep -i oom 與容器退出碼；若拋例外，檢查程式輸出。逐步收斂限額觀察臨界點。注意：oom_kill_disable 與 swappiness 會影響行為；記錄容器與主機度量以免誤判。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, D-Q1

Q8: 如何啟用 LOH 壓實以減緩碎片化？
- A簡: 以程式碼設定 CompactOnce 並觸發完整 GC，觀察 72MB 配置是否改善。
- A詳: 在釋放後加入：GCSettings.LargeObjectHeapCompactionMode = GCLargeObjectHeapCompactionMode.CompactOnce; GC.Collect(GC.MaxGeneration); 再進行 72MB 配置。注意：壓實可能造成長停頓，僅於必要時執行；比較壓實前後結果以評估效益與代價。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, D-Q8

Q9: 如何新增隨機填充以確保實際耗用記憶體？
- A簡: 在配置後呼叫 InitBuffer(buffer) 寫入，每頁至少觸發一次，避免虛擬高估。
- A詳: 將 AllocateBuffer 內的 InitBuffer(buffer) 取消註解；或用 for 步進每 4KB 寫入一位元組。確保每頁被觸發，抬升 RSS。注意：此操作大幅增加 CPU 與時間成本；測試應分別記錄「寫入前後」結果，避免誤將初始化成本混入 GC 成本。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, B-Q5

Q10: 如何記錄配置數量與耗時，建立可比結果？
- A簡: 使用程式內輸出統計＋外部監控（RSS/GC 事件/日誌），並固定版本與限制。
- A詳: 程式已輸出配置次數與耗時；外部搭配 dotnet-counters（或 PerfMon、pidstat）收集 GC/記憶體/RSS；容器環境記錄 cgroups 指標與 dmesg。固定 SDK/Runtime 版本、容器鏡像、資源上限，並一次只開一台 VM，以保證可比性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q11

### Q&A 類別 D: 問題解決類（10題）

Q1: 程式未拋 OutOfMemoryException 就被殺掉，怎麼辦？
- A簡: 容器或 OS 觸發 OOM Killer。放寬限額、調整 swap、降低並行或改用 VM 重現。
- A詳: 症狀：程式無例外就退出。原因：cgroups 超限或 Linux OOM Killer 終止。解法：提高 --memory/--memory-swap、降低壓力、在 VM 或裸機測試；檢查 dmesg 與退出碼。預防：加監控、預留緩衝、以區塊重試與回退策略。關聯：容器資源治理與 GC 容器感知。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, C-Q7

Q2: 64MB 配置很快就失敗，可能原因？
- A簡: 可用連續空間不足、系統限額過低、swap 未啟用或被其他程式佔用。
- A詳: 症狀：少量配置即 OOM。原因：低 RAM/限額、先前殘留占用、LOH 碎片、ulimit/cgroups 限制。步驟：關閉其他程式、確認限額/ulimit、啟用/放大 swap、重開 VM。預防：固定測試順序、一次只開一台 VM、保持乾淨環境。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q13, C-Q1

Q3: GC.Collect 後記憶體佔用不降，為什麼？
- A簡: 記憶體被堆保留或 LOH 碎片未壓實；回收不等於立刻歸還 OS。
- A詳: 症狀：RSS 維持高。原因：堆空間保留待重用、頁面仍在工作集、LOH 無壓實。解法：觀察一段時間、嘗試 LOH 壓實（CompactOnce）、降低壓力；避免頻繁 Collect。預防：合理分塊與重用緩衝、避免大量短期大型配置。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, C-Q8

Q4: 容器內記憶體統計與主機不一致，怎麼診斷？
- A簡: 比對 cgroups 指標、容器內外 RSS、Page Cache；確認 v1/v2 與度量口徑。
- A詳: 症狀：容器顯示小，主機顯示大。原因：cache/共享記憶體計算口徑差、cgroups 版本差異。步驟：/sys/fs/cgroup 讀取限制與使用量、docker stats、cat /proc/meminfo、主機 ps/rss；統一觀測口徑。預防：固定度量工具與版本。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, C-Q7

Q5: 啟用 InitBuffer 後效能劇降，如何優化？
- A簡: 降低寫入頻率、頁粒度寫入、改用 memset/Span 步進；分離測試階段。
- A詳: 症狀：CPU 飆高、耗時倍增。原因：缺頁處理與大量記憶體寫入。解法：每 4KB 寫 1byte、以 Random.Shared/Span 低成本填充、以 Release 建置；將初始化放獨立階段。預防：僅在需要真實 RSS 時啟用，平衡精準度與成本。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, C-Q9

Q6: 測試導致主機當機或嚴重抖動，如何避免？
- A簡: 降低壓力、限制容器 CPU/IO、調整 swap 與 swappiness、分批執行。
- A詳: 症狀：系統卡頓、I/O 滿載。原因：過度換頁、I/O 爆量。解法：降低配置速率、減少同時執行、限流（--cpus、--blkio-weight）、降低 swap 使用或關閉、於隔離主機測試。預防：先小規模演練，建立自動化與警戒閾值。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q13, C-Q7

Q7: Windows 與 Linux 測試結果差異大，如何查因？
- A簡: 檢核 GC 模式、容器限制、overcommit、swap、版本差異與度量工具口徑。
- A詳: 症狀：可配置數量/耗時差異明顯。原因：GC 伺服/工作站、cgroups 設定、overcommit、swap 策略、Runtime 版本。步驟：統一環境變數、版本、限額；用 dotnet-counters/PerfMon 收集 GC 事件；分析 dmesg/事件檢視器。預防：事前列出控制變因清單。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q11

Q8: 大型陣列導致 LOH 碎片化，應用程式如何處理？
- A簡: 重用緩衝（池化）、分塊策略、避免固定大物件、必要時執行一次性壓實。
- A詳: 症狀：長期運行後 OOM 或延遲突增。解法：使用 ArrayPool/MemoryPool 重用；以多個小塊組合避免超大型連續；避免固定/針對性釘選；在維護窗以 CompactOnce。預防：設計時評估資料流量與壽命，加入監控與自動降級。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, C-Q8

Q9: 在虛擬化環境測不到預期 OOM，如何校正？
- A簡: 確認動態記憶體關閉、限制一致、關閉其他 VM、降低限額或啟用 InitBuffer。
- A詳: 症狀：無法觸發 OOM。原因：主機資源溢出供應、動態記憶體、其他 VM 干擾。解法：關閉動態記憶體、一次只開一台、降低 RAM 限額、啟用寫入填充。預防：測試前快照環境、使用自動化腳本建立乾淨 VM。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, C-Q1

Q10: 如何預防生產環境的碎片化與 OOM 問題？
- A簡: 池化重用、分塊設計、容量監控、預留緩衝、容器限額與警戒、離峰壓實。
- A詳: 策略：避免大量短期大型配置；採用緩衝池；以分塊/流水線降低連續需求；加入記憶體與 GC 監控與告警；容器設定合理記憶體與 swap；定期健康檢查與離峰 CompactOnce。演練：壓力測試與故障注入，驗證降級路徑與復原機制。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, C-Q10

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是記憶體碎片化（Memory Fragmentation）？
    - A-Q2: 什麼是 OOM（Out Of Memory）？
    - A-Q3: 什麼是 .NET Core 的垃圾回收（GC）？
    - A-Q4: 為何用 64MB 與 72MB 區塊進行測試？
    - A-Q8: 測試程式中的三個 List（buffer1/2/3）用途是什麼？
    - A-Q9: 為何關閉 Hyper-V 動態記憶體（Dynamic Memory）？
    - C-Q1: 如何在 Hyper-V 建立統一 VM 並關閉動態記憶體？
    - C-Q6: 如何用 dotnet CLI 編譯並執行範例程式？
    - B-Q1: 測試執行流程如何運作？
    - B-Q4: 碎片化如何導致 72MB 配置失敗？
    - B-Q10: 清空 List 是否等於將記憶體歸還給 OS？
    - D-Q2: 64MB 配置很快就失敗，可能原因？
    - D-Q3: GC.Collect 後記憶體佔用不降，為什麼？
    - C-Q10: 如何記錄配置數量與耗時，建立可比結果？
    - D-Q10: 如何預防生產環境的碎片化與 OOM 問題？

- 中級者：建議學習哪 20 題
    - A-Q5: 什麼是 LOH（Large Object Heap），與本測試有何關聯？
    - A-Q6: 釋放（de-reference）與 GC.Collect 有何差異？
    - A-Q10: 為什麼需要 InitBuffer 隨機填滿記憶體？
    - A-Q11: Container 與 VM 的記憶體管理有何差異？
    - A-Q12: .NET Core 與 .NET Framework 在記憶體管理的異同？
    - A-Q14: 什麼是 GC 代數（Generation）？與測試關係？
    - B-Q2: .NET 配置大型 byte[] 的內部機制是什麼？
    - B-Q3: GC.Collect(GC.MaxGeneration) 的機制與影響？
    - B-Q5: InitBuffer 對 OS 承諾/配置機制的影響是什麼？
    - B-Q6: Linux overcommit 與本測試的關聯？
    - B-Q7: 容器中的記憶體限制與 OOM Killer 機制如何運作？
    - B-Q8: LOH 碎片化與壓實（compaction）原理是什麼？
    - B-Q11: Server GC 與 Workstation GC 對結果的影響？
    - B-Q13: 為何設定 SWAP 為 4GB？機制如何？
    - B-Q14: .NET Core 在 OOM 時如何保護應用程式？
    - C-Q3: 如何在 Ubuntu 安裝 Docker 並執行 .NET 程式？
    - C-Q7: 如何在容器中設定記憶體上限並觀察 OOM 行為？
    - C-Q8: 如何啟用 LOH 壓實以減緩碎片化？
    - C-Q9: 如何新增隨機填充以確保實際耗用記憶體？
    - D-Q6: 測試導致主機當機或嚴重抖動，如何避免？

- 高級者：建議關注哪 15 題
    - A-Q7: 為何要在多平台（Windows、Linux、Container）上測試？
    - A-Q13: 為何要統一 VM 規格並一次只開一台？
    - B-Q9: List<byte[]> 擴張策略對測試有何影響？
    - B-Q12: Windows 與 Linux 容器在 GC 偵測/限制上的差異？
    - B-Q15: 為何選擇 1 vCPU、1GB RAM 作為測試基準？
    - C-Q4: 如何在 Boot2Docker 環境執行測試？
    - C-Q5: 如何在 Windows Server 2016（Nano）建立 Windows Container 並執行？
    - D-Q1: 程式未拋 OutOfMemoryException 就被殺掉，怎麼辦？
    - D-Q4: 容器內記憶體統計與主機不一致，怎麼診斷？
    - D-Q5: 啟用 InitBuffer 後效能劇降，如何優化？
    - D-Q7: Windows 與 Linux 測試結果差異大，如何查因？
    - D-Q8: 大型陣列導致 LOH 碎片化，應用程式如何處理？
    - B-Q5: InitBuffer 對 OS 承諾/配置機制的影響是什麼？
    - B-Q7: 容器中的記憶體限制與 OOM Killer 機制如何運作？
    - B-Q8: LOH 碎片化與壓實（compaction）原理是什麼？