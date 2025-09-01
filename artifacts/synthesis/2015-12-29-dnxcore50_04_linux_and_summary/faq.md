# .NET Core 跨平台 #4, 記憶體管理大考驗 – Docker @ Ubuntu / Boot2Docker

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 本文的測試主題是什麼？
- A簡: 比較 .NET Core 在 Ubuntu 與 Boot2Docker 的記憶體配置、破碎化與回收率，並剖析異常來源（惰性配置、swap、OOM）。
- A詳: 文章聚焦於 .NET Core CLI 在 Docker 容器中於兩種 Linux 環境（Ubuntu Server 15.10 與 Boot2Docker）的記憶體行為。重點包含：三階段配置/釋放/再配置的測試設計、初始化與否造成的「可配置超大」假象（疑涉 SPARSEMEM/惰性配置）、swap 預設差異導致的可配置量差異、容器內程式被 OS 直接 Killed（OOM Killer）與 CLR 丟出 OutOfMemoryException 的差異，以及最後 Ubuntu 98.85% 回收率、Boot2Docker 約 88.46% 表現與定位結論。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, A-Q8, A-Q9, A-Q11, A-Q13

A-Q2: 什麼是 .NET Core CLI Container？
- A簡: 微軟提供的 dotnet CLI Docker 映像，用於建置、執行 .NET Core 應用的基礎容器。
- A詳: .NET Core CLI Container 是官方發佈的 Docker 映像，內含 dotnet 指令工具與必要的 .NET Core 執行環境。開發者可直接以 docker pull 抓取映像，並使用 docker run 啟動容器執行 dotnet restore/build/run 等命令。它簡化了跨平台部署與一致化開發體驗，尤其便於在 Linux（如 Ubuntu、Boot2Docker 等）上快速測試 .NET Core 應用與其在不同作業系統與容器組態下的記憶體行為與效能特性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, C-Q2

A-Q3: 什麼是 Boot2Docker？
- A簡: 基於 Tiny Core 的輕量 Linux，專為執行 Docker 容器，從 RAM 開機、體積小、啟動快。
- A詳: Boot2Docker 是一個極輕量的 Linux 發行版，核心目的是快速運行 Docker。它以 ISO 方式提供，開機後即從 RAM 運作，映像約 27–30MB，啟動數秒可用。此設計使它非常適合開發與測試，但因偏向 RAM 運行且預設無 swapfile，資源利用較保守，長時間或高負載情境、對磁碟持久化與虛擬記憶體依賴較高的工作負載並不合適用於正式環境。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, A-Q14, B-Q8, D-Q4

A-Q4: Ubuntu 與 Boot2Docker 的定位差異是什麼？
- A簡: Ubuntu 為通用伺服器環境，Boot2Docker 為輕量測試環境；資源管理與可調性差異大。
- A詳: Ubuntu Server 是完整、可持久化安裝於磁碟的 Linux 伺服器系統，具備完善封包管理、檔案系統與 swap 設定彈性，適用於正式環境。Boot2Docker 則為 RAM 運行、極簡的容器宿主，主打快速、輕便、易取得與測試用。兩者因此在可配置記憶體、swap 與穩定性、I/O 與資源回收等行為有所不同。本測試結果也反映此定位：Ubuntu 表現穩健且回收率高；Boot2Docker 偏保守且更適合測試用途。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q13, A-Q14, B-Q8

A-Q5: 什麼是 Sparse File（稀疏檔案）？
- A簡: 邏輯大小大於實際占用空間，未寫入區段不消耗實體儲存的檔案形式。
- A詳: 稀疏檔案的邏輯長度可遠大於實際磁碟占用，未初始化或未寫入的區段不佔空間，直到真正寫入才分配。此概念用於大型檔案初始化或檔案系統效率最佳化。文中提及此概念，類比到記憶體：當配置大量記憶體但不初始化，作業系統可能延後實體頁面分配，導致「看似」可配置極大容量。為避免量測誤判，測試需主動初始化記憶體以迫使實際分配。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, A-Q7, B-Q2

A-Q6: 什麼是 Linux 的 SPARSEMEM/惰性配置現象？
- A簡: 一類記憶體管理策略與延後配置行為，未觸發寫入時不實配頁面。
- A詳: SPARSEMEM 是 Linux 核心支援的一種記憶體管理模式，用於支援稀疏分布的實體記憶體與熱插拔情境；搭配一般 Linux 的惰性配置/寫入時分頁等機制，可能出現「未初始化的分配看似巨大」的現象。換言之，malloc/new 成功不代表實體頁面已保留，只有在寫入（初始化）時才真正佔用。本文以初始化（亂數填充）驗證此效應，避免過度樂觀的容量判讀。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q3, A-Q5, A-Q7

A-Q7: 為什麼測試中必須初始化配置的記憶體？
- A簡: 強迫作業系統實際分頁與佔用，避免惰性配置造成容量誤判。
- A詳: 不初始化的分配常因作業系統惰性配置與零頁共享而延後分頁，導致應用端誤以為「可配置量」極高，形成不實測值。文中改以 Random.NextBytes 對整個緩衝區填充，確保每頁都被寫入，作業系統必須分配實體內存或 swap，從而反映真實可用記憶體。這一步在針對記憶體分配極限、碎片化後再配置能力等評量時是必要的。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, C-Q3

A-Q8: 什麼是 swapfile？與 Windows 的 pagefile 有何不同？
- A簡: swapfile/partition 為 Linux 的虛擬記憶體；Windows 為 pagefile，預設容量與管理不同。
- A詳: swap 在 Linux 中可為檔案或分割區，用來將不活躍頁面換出，以擴大有效記憶體容量；Windows 對應的是 pagefile.sys。本文關鍵修正是 Ubuntu 預設只有 1GB swap，導致初期配置量偏低；調整到 4GB 後，結果明顯改善至 4864MB/4808MB（98.85%）。差異點包括預設大小、配置工具與啟用方式，測試前務必確認，以免將環境差異誤判為執行時差異。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q4, C-Q5, D-Q3

A-Q9: 什麼是 OOM Killer？與 CLR 的 OutOfMemoryException 差異？
- A簡: OOM Killer 由 OS 觸發強制殺進程；CLR OOM 是執行階段例外，可被捕捉。
- A詳: Linux 當系統內存壓力過大時，會啟動 OOM Killer 根據分數殺掉進程，常見症狀是應用直接「Killed」，來不及丟出應用層例外。CLR 的 OutOfMemoryException 屬於程式執行階段的可捕捉例外，意味著 CLR 尚能運作並回報錯誤。本文多次觀察到 Linux 上直接被 Killed 的情況，顯示在嚴重壓力下，OS 可能先於 CLR 主導終止。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q1, B-Q6, C-Q8

A-Q10: 什麼是記憶體破碎化（fragmentation）？
- A簡: 記憶體被不同大小與時間序釋放/配置打散，導致可用空間不連續。
- A詳: 當應用多次配置與釋放不同大小的記憶體，系統會出現許多不連續的小塊空間，雖總量足夠，但難以滿足大塊連續分配，影響再配置能力與效能。本文以三階段測試量測初次配置量、釋放後再配置量與回收比例（再配置/初次配置），以觀測記憶體管理與 GC 在碎片化後的實際表現。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, B-Q9, C-Q9

A-Q11: 文章中三階段測試設計是什麼？
- A簡: 第一階段大量配置；第二階段釋放打散；第三階段再配置並計算回收率。
- A詳: 測試流程概念為：（1）連續配置記憶體至極限，得到初次總量；（2）釋放部分與重複配置，模擬碎片化；（3）再次嘗試配置，得到第三階段的可用量，並以回收率（第三/第一）衡量碎片化後的實際可得空間。此設計可比較不同平台與容器組態下的碎片抵抗力與回收效率。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q9, B-Q12

A-Q12: 測試中的「回收率」如何定義與解讀？
- A簡: 回收率=碎片化後再配置量/初次配置量，用於衡量碎片抗性與回收效率。
- A詳: 回收率以 Ratio = Phase3Allocated / Phase1Allocated 表示，反映系統在經歷碎片化後，仍能重新取得連續可用空間的能力。值越接近 100%，代表記憶體管理（含 GC、分配器、OS）越能抵抗碎片影響。本文 Ubuntu 達約 98.85%，Boot2Docker 約 88.46%，顯示 Ubuntu 在此指標上更佳。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, A-Q13, C-Q9

A-Q13: 本文的主要結論有哪些？
- A簡: Ubuntu 回收率近乎完美且穩健；Boot2Docker 適測試不宜正式；Linux 整體回收效率優。
- A詳: 歸納結果：（1）Ubuntu Server 記憶體管理最佳，初次配置與碎片後再配置表現近完美，但曾出現被 OS 直接 Killed；（2）Boot2Docker 因設計輕量、RAM 運行、預設無 swap，表現保守且不適正式環境；（3）Linux 在回收率上普遍高於 Windows（此前篇比較），但絕對配置量需留意 swap 預設；（4）初始化配置避免誤判是關鍵；（5）環境組態（swap、容器限制）往往影響大於執行階段差異。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q8, A-Q14, D-Q3

A-Q14: 為何 Boot2Docker 不適合正式環境？
- A簡: 其設計為 RAM 運行、無預設 swap、資源保守，重視啟動與輕量，不適長時高載。
- A詳: Boot2Docker 的價值在快速啟動與極簡使用，適合拉映像、短時測試、開發迭代。因其從 RAM 運行、映像小、預設無 swapfile，多數資源管理策略偏向保守，容器與主機的 I/O 與記憶體配置不像一般伺服器 OS 那樣可深度調校。本文實測也見到寫入 swap 的錯誤訊息與回收率較低的情況，更凸顯其在正式環境的限制。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, D-Q4

A-Q15: Linux 與 Windows 在本文測試中有何差異亮點？
- A簡: Linux 回收率高；Windows 異常少更穩；差異受 swap、分配器與 GC 實作影響。
- A詳: Linux（Ubuntu）在碎片化後的再配置比例表現亮眼（>90%，實測近 98.85%），顯示對碎片的抵抗力較高；但在極端壓力下可能由 OOM Killer 直接終止。Windows 雖在此前篇中表現穩定且較少遇到被 OS 直接殺掉的情況，但回收率不一定高於 Linux。實際差異受 OS 分配與回收策略、GC 模式、swap/pagefile 預設與容器限制共同影響。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, C-Q10

A-Q16: 文末列出的待確認問題有哪些？
- A簡: 未初始化分配僅占小量、Linux 版 CLR 被砍無例外、Server GC/壓縮影響待驗。
- A詳: 三項未決題包括：（1）Linux 對未初始化分配的處理（疑似 SPARSEMEM/惰性配置）導致容量假象；（2）極端內存壓力下，Linux 版 CLR 可能來不及丟例外即被 OS 終止；（3）Windows Server GC 的表現可否透過 server GC（壓縮/compact）改善。本研究主要針對現象描述與環境修正，保留進一步驗證空間。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q3, B-Q6, C-Q10

---

### Q&A 類別 B: 技術原理類

B-Q1: dotnet CLI 容器在 Ubuntu 上如何運作？
- A簡: 透過 Docker 拉取官方映像，容器內執行 dotnet 工具鏈，隔離於宿主系統。
- A詳: 原理上，Docker 利用映像分層提供 .NET Core CLI 執行所需檔案與依賴。啟動容器時，cgroups/namespaces 提供資源隔離；檔案系統由映像/容器層組合。關鍵步驟：1) docker pull microsoft/dotnet（或對應標籤）；2) docker run -it 掛載原始碼或工作目錄；3) 容器內執行 dotnet restore/build/run。核心組件包括：Docker Engine、映像層、網路命名空間、cgroups、容器內的 dotnet CLI 與 runtime。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q1, C-Q2

B-Q2: Linux 為何在未初始化時「看起來」能配置數百 GB 記憶體？
- A簡: 因惰性分配/按需分頁，僅建立虛擬位址，未寫入前不保留實體頁面。
- A詳: 當程式分配巨大緩衝但未寫入，Linux 常僅建立虛擬記憶體映射；直到存取（尤其寫入）發生，才以 page fault 分配實體頁面或 swap。此機制加上零頁共享、寫入時複製（COW）等，讓「已配置」容量被誇大。關鍵步驟：分配→映射→延後至寫入才分頁。核心組件：虛擬記憶體管理、頁面表、缺頁中斷處理。實務上需以初始化（寫入）來逼真。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, A-Q6, A-Q7

B-Q3: SPARSEMEM 模式背後機制是什麼？
- A簡: 以節區（section）管理稀疏實體記憶體，支援熱插拔與不連續記憶體。
- A詳: SPARSEMEM 是 Linux 核心的記憶體模型之一，將物理記憶體抽象為節區以適配稀疏、可變布局的硬體。它本質是管理實體位址空間的策略，常搭配 NUMA、記憶體熱插拔。雖非直接等同「惰性配置」，但與整體 VM 機制互動後，會呈現未初始化分配時的延後實配現象。關鍵組件：節區描述結構、頁框管理器、VM 佈局。測試現象與此或其他 VM 機制共同作用有關。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q2, A-Q6

B-Q4: 為何用亂數初始化比填零更保險？
- A簡: 填零可能共用零頁或被壓縮；亂數寫入確保每頁實際分配與寫入。
- A詳: 在某些系統下，填零可能命中共享零頁或被記憶體壓縮技術優化，使分頁分配不完整反映實際可用量。改用 Random.NextBytes 亂數填充能觸發對每個頁框的真實寫入，避免被最佳化掩蓋，量測更接近真相。步驟：分配→亂數填充→驗證 RSS 與 swap 變化。核心組件：頁面分配器、壓縮/去重機制、應用層填充策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q3, A-Q7

B-Q5: CLR/GC 在容器中的基本運作原理是什麼？
- A簡: GC 管理受控堆，分代/壓縮策略運作；容器以 cgroups 限制資源上限。
- A詳: .NET CLR 的 GC 負責管理受控堆（含小物件堆 SOH、大物件堆 LOH），透過分代收集、標記-清除、必要時壓縮以回收與整理碎片。於容器中，GC 本身邏輯不變；但可用資源受 cgroups（記憶體、CPU）約束。當容器無記憶體限制時，實際可用量近似宿主；若有限制，超出則可能遭 OOM Kill。核心組件：GC 分代機制、容器 cgroups、記憶體映射。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, C-Q10, D-Q1

B-Q6: OOM Killer 的觸發流程為何？
- A簡: 系統壓力過大時，核心計分選擇進程並強制殺死以釋放記憶體。
- A詳: 當可用記憶體和 swap 都不足，核心會評估各進程的 OOM 分數（基於使用量、優先度等），挑選「成本較低」或佔用較高者終止。關鍵步驟：內存壓力上升→嘗試回收頁面→失敗→啟動 OOM Killer→選擇目標→發送 SIGKILL。核心組件：kswapd、記憶體回收器、OOM 採擇器。症狀：程式直接被 Killed，dmesg 有 OOM 記錄。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, C-Q8, D-Q1

B-Q7: Linux 的 swap 與物理記憶體如何協同？
- A簡: 不活躍頁面換出至 swap，釋放 RAM；換入需 I/O，性能較慢。
- A詳: Linux 透過頁面回收策略將長期不活躍頁面寫入 swap，以釋放 RAM 供活躍工作集使用；當被存取時再換回。關鍵步驟：記憶體壓力→頁面老化評估→寫出 swap→更新頁表；換入時觸發缺頁→從 swap 讀回。核心組件：kswapd、LRU 列表、swapfile/partition。適度 swap 提升可配置量，但過多換入換出會拖慢效能。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, C-Q4, C-Q5

B-Q8: Boot2Docker 的儲存與 RAM-only 設計如何影響 swap？
- A簡: 以 RAM 運行且預設無 swap，造成可配置量與穩定性受限。
- A詳: Boot2Docker 從 RAM 啟動、輕量化，預設不配置 swapfile，也不強調持久化磁碟。即便掛載外部磁碟供映像使用，系統層面仍可能未啟用 swap，導致在高記憶體壓力下更早出現錯誤或被 Killed。核心組件：RAM 根檔系統、ISO 啟動、Docker Engine 預設組態。若需穩定的大記憶體測試，建議改用完整 Linux 發行版。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q14, D-Q4

B-Q9: 記憶體碎片化如何影響 .NET 配置與 GC？
- A簡: 大量不連續空間降低大塊分配成功率，增加 GC 壓力與回收成本。
- A詳: 碎片化使可用空間被打散，小物件常可滿足，但大物件（LOH）或大陣列易失敗或迫使 GC 更頻繁整理。若無壓縮或壓縮受限（例如 LOH 傳統不壓縮），再配置量下降。關鍵步驟：多次配置/釋放→不連續空間→大塊配置失敗→GC 更頻繁/效能下滑。核心組件：GC 分代、壓縮策略、LOH 行為。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, A-Q12, C-Q10

B-Q10: 為何 Linux 與 Windows 的回收率可能不同？
- A簡: 受 OS 分配器、GC 策略、虛擬記憶體與 swap/pagefile 預設差異影響。
- A詳: 回收率反映多層交互：OS 的分配/回收策略（glibc/內核 vs Windows）、GC 模式（Server/Workstation、壓縮）、虛擬記憶體管理、swap/pagefile 及其預設大小。Linux 在分配與頁面回收策略上常顯示良好碎片抵抗力，但在極端壓力下更可能由 OOM 主導終止；Windows 異常較少但回收率不一定高。測試前需校準環境以公平比較。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, C-Q10

B-Q11: Docker 記憶體限制與 cgroup 如何設計？
- A簡: 以 cgroups 管控容器資源；透過 -m 指定上限，避免擴散至宿主。
- A詳: Docker 透過 Linux cgroups 對容器施加記憶體/CPU/IO 限制。啟動容器可用 -m/--memory、--memory-swap 等旗標指定上限與 swap 行為。關鍵步驟：docker run -m 2g ...；超出時可能觸發 OOM Killer。核心組件：cgroup v1/v2 設定、memory limits、oom_kill_disable。正確設定能避免單一容器拖垮宿主。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q7, D-Q1

B-Q12: 測試程式 AllocateBuffer/InitBuffer 的原理？
- A簡: 先分配 byte[]，再用亂數填充，強迫 OS 分頁實配並觀測真實使用。
- A詳: AllocateBuffer 建立指定大小的 byte[]；InitBuffer 使用 Random.NextBytes 對陣列全寫，觸發頁面實際配置。流程：分配→初始化→釋放→再配置；透過不同階段總量推估碎片化影響與回收率。核心組件：受控堆分配、JIT 優化、OS 虛擬記憶體與分頁、容器資源限制。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q3, A-Q11

B-Q13: 調整 Ubuntu swap 的原理與作法？
- A簡: 建立 swapfile、mkswap、swapon 啟用，永久化寫入 fstab。
- A詳: 以 fallocate/dd 建立檔案（如 4GB），mkswap 格式化，swapon 啟用，並在 /etc/fstab 增加條目以開機自動掛載。步驟：fallocate -l 4G /swapfile→chmod 600→mkswap→swapon→/etc/fstab 設置。核心組件：檔案系統、swap 子系統、開機掛載流程。本文將 Ubuntu 由預設 1GB 調至 4GB，實測配置量與回收率大幅改善。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q4, D-Q3

B-Q14: 為何 Boot2Docker 可能出現寫入 swap 錯誤？
- A簡: 因 RAM 運行、未啟用/不持久 swap，加上 I/O 與資源限制導致不穩定。
- A詳: 由於 Boot2Docker 的 RAM-root 設計與預設無 swap，加上對外部磁碟的整合方式與啟動流程，若強行在其上建立 swapfile，可能遇到不持久、I/O 路徑或記憶體壓力下的錯誤訊息。此屬設計取向差異，不代表 Linux 核心不耐；本文觀察到隨機寫入 swap 錯誤與較低再配置量，印證它更適合測試而非高負載正式用途。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q4, A-Q14

---

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何在 Ubuntu 15.10 安裝 Docker 並拉取 dotnet CLI 映像？
- A簡: 安裝 Docker Engine，使用 docker pull 取得 microsoft/dotnet 映像。
- A詳: 步驟：1) 安裝 Docker（apt-get update && apt-get install -y docker.io 或依官方指南）；2) 啟動服務並設為開機啟動；3) docker pull mcr.microsoft.com/dotnet/runtime 或對應 CLI 映像（舊版為 microsoft/dotnet）；4) 驗證 docker images。最佳實踐：使用官方來源、鎖定標籤、確保網路品質與磁碟空間足夠。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, C-Q2

C-Q2: 如何在容器中執行 .NET Core 記憶體測試程式？
- A簡: 將專案掛載進容器，容器內 dotnet restore/build/run 執行。
- A詳: 範例：docker run -it --rm -v $PWD:/app -w /app mcr.microsoft.com/dotnet/sdk dotnet run -c Release。步驟：1) 本機準備程式碼；2) -v 掛載至 /app；3) -w 設工作目錄；4) 容器內 dotnet restore/build/run。注意：確保初始化記憶體邏輯存在，避免惰性配置造成假象；視需求加上 -m 設定記憶體限制。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q11

C-Q3: 如何修改程式以初始化記憶體（避免惰性配置誤判）？
- A簡: 使用 Random.NextBytes 填滿新分配的 byte[]。
- A詳: 關鍵片段：
  byte[] buf = new byte[size];
  new Random().NextBytes(buf);
步驟：1) 分配緩衝；2) 立即亂數填充；3) 之後再測量配置量與 RSS。注意：避免僅填零；亂數寫入更能確保每頁實際分配。最佳實踐：將初始化封裝為工具函式，確保各平台一致性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, B-Q4

C-Q4: 如何在 Ubuntu 建立 4GB swapfile？
- A簡: fallocate 建檔→chmod 600→mkswap→swapon→寫入 /etc/fstab。
- A詳: 指令：sudo fallocate -l 4G /swapfile；sudo chmod 600 /swapfile；sudo mkswap /swapfile；sudo swapon /swapfile；echo "/swapfile swap swap defaults 0 0" | sudo tee -a /etc/fstab。注意：確保磁碟空間足夠、權限 600、防止被意外讀取。最佳實踐：以 free -m、swapon --show 驗證生效。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q13, D-Q3

C-Q5: 如何檢查 Linux 的記憶體與 swap 使用狀態？
- A簡: 使用 free -m、swapon --show、cat /proc/meminfo 等指令。
- A詳: 常用：free -m 檢視總量/使用量；swapon --show 查看 swap 裝置；cat /proc/meminfo 讀取詳細統計；vmstat 1 觀察系統行為。注意：容器內可另用 cat /sys/fs/cgroup/memory/memory.usage_in_bytes 等檔案檢視 cgroup 使用。最佳實踐：測試前後都記錄，以利比對回收率與異常。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, B-Q11

C-Q6: Boot2Docker 如何增加可用儲存與（有限）swap 支援？
- A簡: 掛載外部虛擬磁碟供映像；swap 須手動建置且可能不持久。
- A詳: 步驟：1) 於 VM 管理程式新增虛擬磁碟供 Docker 映像使用；2) 必要時嘗試建立 swapfile（dd/fallocate→mkswap→swapon），但注意重啟後可能失效；3) 驗證 free -m 與 swapon --show。注意：Boot2Docker 設計非為長期/高載，swap 與 I/O 不保證穩定，若需嚴格測試建議改用完整 Linux。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q8, B-Q14, D-Q4

C-Q7: 如何限制容器記憶體避免拖垮宿主？
- A簡: docker run -m/--memory 與 --memory-swap 設定上限與 swap 行為。
- A詳: 範例：docker run -m 2g --memory-swap 3g ...。-m 指定 RAM 上限；--memory-swap 指定 RAM+swap 上限。注意：過低限制會導致容器內更易被 OOM Kill；過高則影響宿主。最佳實踐：以壓力測試尋找臨界值，並監測 dmesg 與容器記錄。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q11, D-Q1

C-Q8: 如何蒐集 OOM 事件與診斷「Killed」的原因？
- A簡: 使用 dmesg/journalctl 查核核心記錄，確認 OOM 與被殺進程。
- A詳: 在宿主執行 dmesg | grep -i oom 或 journalctl -k | grep -i oom；亦可查 /var/log/kern.log。容器內若無系統記錄，需回到宿主檢視。注意：對應容器 PID 與宿主 PID 的映射（docker top 或 /proc）。最佳實踐：保留時間戳、配置與負載資訊以重現問題。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q6, D-Q1

C-Q9: 如何量測回收率並繪製比較圖？
- A簡: 紀錄第一/三階段配置量，計算比例並以條/折線圖呈現。
- A詳: 步驟：1) 程式列印 Phase1/Phase3 配置總量；2) 計算 Ratio=Phase3/Phase1；3) 匯出 CSV；4) 使用 Excel/gnuplot 繪製：灰色為 Phase1、深藍 Phase3、線為回收率。注意：需初始化記憶體避免誤判；環境（swap、限制）須一致比對。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q11, A-Q12

C-Q10: 如何在 .NET Core 調整 GC 模式（Server GC）？
- A簡: 以 runtimeconfig.json 或環境變數啟用 Server GC，改善碎片與吞吐。
- A詳: 方法一：在 runtimeconfig.json 的 runtimeOptions 設定 "System.GC.Server": true。方法二：設定環境變數（如 DOTNET_GCServer=1 或 COMPlus_gcServer=1）。注意：不同版本配置鍵略異；需驗證實際版號。最佳實踐：在壓力測試對照回收率與延遲，避免僅憑猜測。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q5, B-Q9, D-Q5

---

### Q&A 類別 D: 問題解決類（10題）

D-Q1: 容器內程式被直接「Killed」沒有 OOM 例外怎麼辦？
- A簡: 檢查宿主 dmesg OOM 記錄，增加 swap/降低負載/設置容器記憶體上限。
- A詳: 症狀：程式無例外即終止，終端顯示 Killed。可能原因：宿主內存壓力觸發 OOM Killer、容器限制不足。解法：1) dmesg/journalctl 查 OOM 訊息；2) 增加宿主 swap（C-Q4）或提升 RAM；3) 合理設定 docker -m/--memory-swap；4) 降低程式瞬時分配峰值或分批處理；預防：壓力測試、監控、預設限制到位。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q6, C-Q7, C-Q8

D-Q2: 看到可配置數百 GB 的荒謬數字該如何解讀與修正？
- A簡: 多因未初始化惰性配置；改為全量寫入初始化再量測。
- A詳: 症狀：小 RAM 機器卻顯示可配置數百 GB。原因：未初始化，OS 僅建立虛擬映射。解法：1) 程式改為 Random.NextBytes 全量寫入；2) 觀察 RSS 與 swap 實際變化；3) 驗證 free -m 數據。預防：將初始化納入測試標準流程，避免誤導結論。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q2, C-Q3

D-Q3: Ubuntu 測試只能配置到約 2GB 的可能原因與修正？
- A簡: 多因預設 swap 僅 1GB；調整為 4GB 後可大幅改善。
- A詳: 症狀：初次配置量偏低，碎片後再配置更差。原因：預設 /swapfile 僅 1GB。解法：依 C-Q4 建立/擴增至 4GB（或需求值）；重新測試：本文由 1GB 調至 4GB 後，達到 4864MB/4808MB（98.85%）。預防：測試前檢查 free -m、swapon --show。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, B-Q13

D-Q4: Boot2Docker 出現寫入 swap 錯誤與表現不穩定怎麼辦？
- A簡: 其設計限制所致；改用完整 Linux（如 Ubuntu）進行正式測試。
- A詳: 症狀：隨機 swap 寫入錯誤、再配置量偏低。原因：RAM 運行、預設無 swap、I/O 與持久化限制。解法：1) 僅將其當作測試用；2) 若必須，嘗試手動 swap（不保證穩定）；3) 更換為 Ubuntu Server 等正式發行版。預防：依使用情境選擇宿主環境。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q14, B-Q8, B-Q14

D-Q5: 回收率偏低（碎片嚴重）如何改善？
- A簡: 採 Server GC/調整配置策略、降低大物件分配、增加 RAM/swap。
- A詳: 症狀：Phase3/Phase1 比例低。原因：碎片化、大物件堆（LOH）壓力、GC 模式不佳。解法：1) 啟用 Server GC（C-Q10）；2) 降低大陣列分配、改小區塊池化；3) 增加 RAM/swap；4) 分批處理、控制並行度。預防：壓力測試、記憶體分析、設計時避免超大長壽命物件。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q9, C-Q10

D-Q6: 容器中的 .NET Core 程式常被 OOM Kill 的預防方案？
- A簡: 設定合理記憶體上限、增加 swap、分批分配、監控與告警。
- A詳: 症狀：高載時不定期被殺。原因：容器未限流、宿主壓力大、分配尖峰。解法：1) docker -m/--memory-swap；2) 擴增宿主 RAM/swap；3) 程式採分批處理/緩衝池；4) 加入監控（RSS、swap、pagefault）。預防：容量規劃、壓力測試與自動伸縮策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, C-Q7, C-Q8

D-Q7: 測試結果隨機失敗的排查流程？
- A簡: 固化環境（swap、限制、映像版本）、加強記錄、重現最小案例。
- A詳: 步驟：1) 固定映像與標籤、鎖版本；2) 確認 swap 與限制一致；3) 收集 dmesg/容器日誌；4) 建立最小重現程式（僅分配/初始化）；5) 逐步增加負載。可能原因：惰性配置、I/O 不穩、資源競用。預防：測試自動化與環境宣告式管理（IaC）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q8, C-Q9

D-Q8: 圖表/數據差異過大如何驗證？
- A簡: 檢查初始化、swap、容器限制、以 RSS/smaps 交叉驗證。
- A詳: 步驟：1) 確定程式做了全量初始化；2) free -m、swapon --show 驗證；3) docker inspect / cgroup 檔案檢查限制；4) 以 /proc/<pid>/smaps、pmap 觀察 RSS 與映射差異；5) 重複測試多次取中位數。預防：一致環境腳本化、版本鎖定。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, C-Q3, C-Q5

D-Q9: 下載映像或運行時空間不足怎麼辦（Boot2Docker/Ubuntu）？
- A簡: 增加虛擬磁碟、清理舊映像、調整映像儲存位置。
- A詳: 症狀：docker pull 失敗、運行時磁碟不足。解法：1) VM 增加 VHD；2) docker system prune 清理未使用資源；3) 調整 Docker data-root；4) Ubuntu 可擴容檔案系統、Boot2Docker 建議改正式 OS。預防：定期清理、設定磁碟監控。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, C-Q6

D-Q10: Windows 與 Linux 結果差異過大如何判斷是否環境因素？
- A簡: 統一限制/版本/swap，確保初始化，重測以排除非執行時差異。
- A詳: 步驟：1) 統一容器限制與 GC 模式；2) Windows pagefile 與 Linux swap 比齊；3) 確保初始化記憶體一致；4) 鎖定 dotnet/runtime 版本；5) 多輪測試取統計值。若差異縮小，多為環境；若仍顯著，才分析執行時行為（分配器、GC、OS 策略）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q10, C-Q10

---

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 本文的測試主題是什麼？
    - A-Q2: 什麼是 .NET Core CLI Container？
    - A-Q3: 什麼是 Boot2Docker？
    - A-Q4: Ubuntu 與 Boot2Docker 的定位差異是什麼？
    - A-Q5: 什麼是 Sparse File（稀疏檔案）？
    - A-Q7: 為什麼測試中必須初始化配置的記憶體？
    - A-Q8: 什麼是 swapfile？與 Windows 的 pagefile 有何不同？
    - A-Q9: 什麼是 OOM Killer？與 CLR 的 OutOfMemoryException 差異？
    - A-Q10: 什麼是記憶體破碎化（fragmentation）？
    - A-Q11: 文章中三階段測試設計是什麼？
    - A-Q12: 測試中的「回收率」如何定義與解讀？
    - C-Q1: 如何在 Ubuntu 安裝 Docker 並拉取映像？
    - C-Q2: 如何在容器中執行 .NET Core 測試程式？
    - C-Q3: 如何修改程式以初始化記憶體？
    - C-Q5: 如何檢查 Linux 的記憶體與 swap 使用狀態？

- 中級者：建議學習哪 20 題
    - B-Q1: dotnet CLI 容器在 Ubuntu 上如何運作？
    - B-Q2: Linux 未初始化時為何「看起來」能配置超大記憶體？
    - B-Q4: 為何用亂數初始化比填零更保險？
    - B-Q5: CLR/GC 在容器中的基本運作原理是什麼？
    - B-Q6: OOM Killer 的觸發流程為何？
    - B-Q7: Linux 的 swap 與物理記憶體如何協同？
    - B-Q8: Boot2Docker 設計如何影響 swap？
    - B-Q9: 記憶體碎片化如何影響 .NET 配置與 GC？
    - B-Q10: 為何 Linux 與 Windows 的回收率可能不同？
    - B-Q11: Docker 記憶體限制與 cgroup 如何設計？
    - B-Q12: 測試程式 AllocateBuffer/InitBuffer 的原理？
    - B-Q13: 調整 Ubuntu swap 的原理與作法？
    - C-Q4: 如何在 Ubuntu 建立 4GB swapfile？
    - C-Q7: 如何限制容器記憶體避免拖垮宿主？
    - C-Q8: 如何蒐集 OOM 事件與診斷原因？
    - C-Q9: 如何量測回收率並繪圖？
    - D-Q1: 程式被「Killed」怎麼辦？
    - D-Q2: 荒謬配置數字的修正步驟？
    - D-Q3: Ubuntu 僅能配置約 2GB 的修正？
    - D-Q9: 下載映像或運行時空間不足怎麼辦？

- 高級者：建議關注哪 15 題
    - A-Q6: 什麼是 Linux 的 SPARSEMEM/惰性配置現象？
    - A-Q13: 本文的主要結論有哪些？
    - A-Q15: Linux 與 Windows 的差異亮點？
    - A-Q16: 文末列出的待確認問題有哪些？
    - B-Q3: SPARSEMEM 模式背後機制是什麼？
    - B-Q10: 為何 Linux 與 Windows 的回收率可能不同？
    - C-Q6: Boot2Docker 增加儲存與（有限）swap 的做法
    - C-Q10: 如何在 .NET Core 調整 GC 模式（Server GC）？
    - D-Q4: Boot2Docker swap 錯誤與不穩定的處置
    - D-Q5: 回收率偏低（碎片嚴重）如何改善？
    - D-Q6: 容器程式常被 OOM Kill 的預防方案？
    - D-Q7: 測試結果隨機失敗的排查流程？
    - D-Q8: 圖表/數據差異過大如何驗證？
    - D-Q10: Windows 與 Linux 差異過大如何判定環境因素？
    - B-Q14: 為何 Boot2Docker 可能出現寫入 swap 錯誤？