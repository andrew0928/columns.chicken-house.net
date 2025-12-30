---
layout: synthesis
title: ".NET Core 跨平台 #4, 記憶體管理大考驗 – Docker @ Ubuntu / Boot2Docker"
synthesis_type: faq
source_post: /2015/12/29/dnxcore50_04_linux_and_summary/
redirect_from:
  - /2015/12/29/dnxcore50_04_linux_and_summary/faq/
---

# .NET Core 跨平台 #4 記憶體管理大考驗 – Docker @ Ubuntu / Boot2Docker FAQ

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

Q1: 什麼是 .NET Core CLI 容器？
- A簡: Microsoft 提供的 dotnet CLI Docker 映像，用於在容器內建置與執行 .NET Core。
- A詳: .NET Core CLI 容器是 Microsoft 發佈的 Docker 映像，內含 dotnet 命令列工具與執行環境，便於在跨平台容器中建置、測試與執行 .NET Core 應用。它將開發環境標準化，降低安裝複雜度，常用於 CI/CD、快速實驗與跨 OS 相同版本的測試。本篇以該映像在 Ubuntu 及 Boot2Docker 上進行記憶體管理行為比對。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q9, B-Q8

Q2: Ubuntu Server 15.10 在測試中的角色是什麼？
- A簡: 標準 Linux 伺服器環境，安裝 Docker Engine，承載 .NET Core CLI 容器進行測試。
- A詳: Ubuntu Server 15.10 是本次測試的標準 Linux 伺服器平台。僅安裝 SSH 與 Docker Engine，透過拉取 Microsoft 的 dotnet CLI 映像執行測試程式。其預設 swapfile 為 1GB（可調整），影響容器可用的虛擬記憶體與實際分配表現。修正 swap 後，Ubuntu 在記憶體碎片回收效率與最大分配量上表現最佳。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, B-Q5, C-Q1

Q3: 什麼是 Boot2Docker？
- A簡: 基於 Tiny Core Linux 的輕量發行版，專為快速執行 Docker 容器而設計，常用於測試。
- A詳: Boot2Docker 是隨 Docker Toolbox 提供的輕量 Linux 發行版，約 27MB，完全在 RAM 中運作，開機約 5 秒。它預先安裝 Docker，適合本機快速測試與教學，但預設不使用交換空間，資源配置保守，較不適合高負載或正式環境。本測試顯示其在大量記憶體壓力場景下表現受限。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q13, B-Q6, D-Q4

Q4: 什麼是 swapfile？為何影響測試結果？
- A簡: Linux 的交換檔，供虛擬記憶體使用；容量決定可分配記憶體上限與穩定性。
- A詳: swapfile 是 Linux 用於擴充虛擬記憶體的檔案，當實體 RAM 不足時，系統將部分頁面換出至 swap。其大小直接影響可分配的總記憶體與 OOM 風險。本文中 Ubuntu 預設 1GB 導致分配量偏低，調整至 4GB 後最大分配提升至約 4.864GB、回收效率達 98.85%。Boot2Docker預設不使用 swap，故表現保守。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, C-Q3, D-Q3

Q5: 什麼是 Sparse File（稀疏檔案）？
- A簡: 一種檔案系統最佳化，延遲配置未初始化區塊的磁碟空間。
- A詳: 稀疏檔案是檔案系統的技術，針對尚未寫入資料的區塊不占用實體磁碟空間，直到資料寫入才實際配置。用途在於節省存儲資源，常見於虛擬磁碟、資料庫檔。本文以其概念比擬 Linux 在未初始化記憶體時呈現的「看似可大規模分配」現象，提醒需透過初始化來驗證真實佔用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q2, D-Q2

Q6: 什麼是 Linux 的 SPARSEMEM/延遲分頁策略？
- A簡: 一種記憶體模型與分頁策略，可能讓未觸碰頁面暫不實配。
- A詳: SPARSEMEM 是 Linux 記憶體模型之一，配合延遲分頁與 overcommit 策略，可能在分配但未初始化的記憶體時不立即映射至實體頁面。本文中未初始化陣列導致「可分配數百 GB」的假象，透過填充亂數觸碰頁面後數據回歸正常。此行為提醒需以初始化確認真實占用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, D-Q2, C-Q4

Q7: 什麼是記憶體破碎化（fragmentation）？
- A簡: 記憶體空間分散成零碎區塊，降低可連續大塊分配與回收效率。
- A詳: 記憶體破碎化指長期分配/釋放後，空閒空間被切割成零碎小片，難以再分配大塊連續記憶體。對 .NET Core 而言，尤其 LOH（大物件堆）更易受影響，造成回收率下降、效能退化。本測試以三階段分配/釋放觀察各平台在破碎後的可回收比例，Ubuntu 表現最穩定。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, A-Q15, D-Q5

Q8: 什麼是 OOM Killer？為何畫面顯示「Killed」？
- A簡: Linux 的低記憶體保護機制，選擇並終止高風險進程以釋放資源。
- A詳: OOM Killer 是 Linux 在嚴重記憶體不足時啟用的機制，根據 oom_score 等權重選擇進程終止。被殺的進程可能來不及拋出例外，終端僅顯示「Killed」。容器高壓情境下常見，需透過調整 swap、容器內存限制、GC設定與監控來降低觸發機率。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, D-Q1, C-Q9

Q9: 為什麼要在容器中測試 .NET Core 記憶體行為？
- A簡: 容器讓環境一致、易複製，可比較不同平台的記憶體管理差異。
- A詳: 使用容器可把執行環境標準化，移除機器差異，便於跨 OS 比較行為。本測試在 Ubuntu 與 Boot2Docker 的 dotnet CLI 容器內觀察分配、回收與碎片化影響，發現 swap與初始化策略對結果影響顯著，有助挑選適合的部署平台與調整系統參數。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, B-Q8, C-Q1

Q10: 為什麼需要初始化新配置的記憶體？
- A簡: 觸碰頁面迫使實體分配，避免延遲分頁造成錯誤的容量幻象。
- A詳: 未初始化的陣列可能僅建立邏輯分配，未映射至實體頁面，導致「可配置超大容量」的假象。使用 rnd.NextBytes 對緩衝區填充亂數可迫使每頁被觸碰，確保真實佔用與正確衡量分配量與回收率。這是驗證測試可信度與跨平台可比性的關鍵步驟。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q9, C-Q2, D-Q2

Q11: Windows 與 Linux 虛擬記憶體的預設差異是什麼？
- A簡: Windows 預設較大 pagefile，Ubuntu 預設較小 swapfile，影響可分配上限。
- A詳: Windows Server 預設 c:\pagefile.sys 常見約數 GB；Ubuntu 安裝程式常預設 /swapfile 為 1GB。不同預設導致容器可分配的總記憶體差異大。本測試修正 Ubuntu swap 至 4GB後，最大分配與回收效率大幅提升，凸顯虛擬記憶體設定對高記憶體壓力工作負載的重要性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q10, C-Q3, D-Q3

Q12: Ubuntu 與 Boot2Docker 的記憶體管理差異？
- A簡: Ubuntu可調整swap、回收率佳；Boot2Docker運行於RAM，資源保守，易受限。
- A詳: Ubuntu 是完整伺服器環境，支援持久化存儲與可配置 swap，容器在高負載下仍有良好回收效率（98.85%）。Boot2Docker以RAM運作、極輕量，預設不使用swap，面對大量分配時容易觸發限制或錯誤。二者定位不同：前者適合穩定生產，後者利於快速測試。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, D-Q4, C-Q7

Q13: Boot2Docker 的核心價值與定位是什麼？
- A簡: 極輕量、快速啟動的測試環境，方便本機運行 Docker，但非為高負載設計。
- A詳: Boot2Docker 基於 Tiny Core Linux，主打「輕量、快」、「RAM 內運作」，隨 Docker Toolbox 提供，安裝即用。其設計目標是降低試用門檻與學習成本，不追求持久化或高資源利用。在需要大量記憶體或穩定性時，應改用完整 Linux 伺服器如 Ubuntu。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, B-Q6, D-Q4

Q14: 什麼是 gcServer（Server GC）？
- A簡: .NET 的伺服器端垃圾回收模式，能提升吞吐並支援壓縮以減少碎片。
- A詳: Server GC 是 .NET 的垃圾回收模式，為多核心伺服器優化，能並行 GC，提高吞吐。部分情境可進行堆壓縮以緩解碎片（視版本與設定）。在 .NET Core 可透過環境變數（如 COMPlus_GCServer 或 DOTNET_GCServer）或 runtimeconfig 啟用。對大量分配與 LOH 情境有助益。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q13, C-Q6, D-Q10

Q15: 什麼是三階段記憶體測試模型？
- A簡: 先大量分配、再釋放造成碎片、最後重分配，觀察可回收比例與效率。
- A詳: 三階段模型：第一階段大量分配以逼近上限；第二階段釋放特定區塊造成碎片；第三階段嘗試重分配觀察能否回收與再利用。以此衡量平台在碎片化後的可用性與 GC 效率。本文記錄各平台最大分配與回收百分比，Ubuntu表現最佳。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, D-Q5, C-Q2

Q16: 什麼是 Docker Toolbox？Boot2Docker 如何隨附？
- A簡: Docker 的工具集，含 Boot2Docker 等組件，便於在桌面快速啟動容器。
- A詳: Docker Toolbox 是早期在 Windows/macOS 上使用 Docker 的工具包，包含 Boot2Docker、客戶端與相關工具。它以 Boot2Docker 提供輕量 Linux VM 以承載 Docker Engine，降低安裝與相容性成本。本文使用其提供的 Boot2Docker 快速建置測試場景。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, B-Q15, C-Q1

Q17: Docker 容器的記憶體與 swap 限制是什麼？
- A簡: 由 cgroups 控制，可透過 --memory 與 --memory-swap 指定限制與互動。
- A詳: Docker 透過 cgroups 管理容器記憶體，--memory 限制 RAM 上限，--memory-swap 限制 RAM+swap 總量。若未設定，容器可用主機資源上限；設定不當會提前觸發 OOM。需依工作負載與主機 swap 配置合理設定，確保穩定與可預期行為。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, C-Q5, D-Q8

Q18: 為什麼 Linux 測試中出現數百 GB 的配置數字？
- A簡: 未初始化導致延遲分頁/overcommit顯示邏輯容量，非真實占用。
- A詳: 未觸碰頁面的分配在 Linux 下可能被延遲映射，配合 overcommit 顯示「分配成功」但不占用實體記憶體，形成誤導性超大數值（如 330GB、700GB）。透過初始化每頁（亂數填充）即可令計數回到可用的真實範圍，避免錯誤結論。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, C-Q4, D-Q2

Q19: 為什麼 Ubuntu 修正 swap 後表現最佳？
- A簡: 足夠虛擬記憶體搭配有效 GC，使分配上限與回收效率顯著提升。
- A詳: Ubuntu 調整 swap 至 4GB 後，容器擁有更充裕的虛擬記憶體，降低 OOM 風險。配合 .NET Core 的 GC 在碎片化後仍具高回收率，實測達 4864MB 分配與 98.85% 回收。顯示正確系統參數與初始化策略能大幅改善大型分配工作負載的穩定性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q3, B-Q17, D-Q3

Q20: 為什麼 Boot2Docker 不適合生產環境？
- A簡: RAM 中運作、無預設 swap、資源受限，定位為測試用非高負載。
- A詳: Boot2Docker 追求輕量與快速啟動，設計上不使用持久化或 swap，資源管理保守。在高分配壓力或需要穩定長期運行的場景容易出現限制或錯誤。其核心價值是降低門檻與加速試用，正式環境應選擇完整 Linux 伺服器以獲得可調資源與穩定性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, B-Q6, D-Q4

Q21: 什麼是 .NET Core CLR？與 .NET Framework 有何差異？
- A簡: .NET Core 的跨平台執行引擎，相較 .NET Framework 更輕量且可在 Linux/容器運行。
- A詳: .NET Core CLR 是 .NET Core 的執行時環境，負責 IL 載入、JIT、GC 等，支援 Windows、Linux、macOS 與容器。相較 .NET Framework（Windows 為主），更模組化與跨平台。本文在 Linux 容器內觀察其記憶體分配、回收與 OOM 行為。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, C-Q6, D-Q7

Q22: 為什麼使用 rnd.NextBytes 初始化記憶體？
- A簡: 亂數填充每頁，避免填 0 被最佳化，確保真正觸碰並分配物理頁。
- A詳: 使用 rnd.NextBytes 對緩衝區填入隨機資料能確保每個頁面被觸碰。相比填 0，某些平台可能套用壓縮或最佳化，影響測試可信度。亂數更能代表真實負載，避免延遲分頁造成的錯誤分配數據，提升跨平台比較的準確性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q9, C-Q2, D-Q2

Q23: 什麼是 pagefile.sys 與 /swapfile 的差異？
- A簡: Windows 的交換檔稱 pagefile，Linux 的交換檔常為 /swapfile，機制相似。
- A詳: Windows 使用 pagefile.sys 作為虛擬記憶體的交換檔，Linux 常用 /swapfile 或交換分割區。兩者皆在 RAM 不足時換出頁面。差異在預設大小與管理方式：Windows常預設較大，Linux安裝常預設較小。本測試顯示大小直接影響容器記憶體壓力下的表現。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q10, C-Q3, D-Q3

Q24: 為何 Linux 版本 CLR 有時無法拋出 OOM 例外？
- A簡: OOM Killer 直接終止進程，CLR來不及拋例外，終端僅見「Killed」訊息。
- A詳: 在 Linux 記憶體嚴重不足或受 cgroups 限制時，系統可能啟用 OOM Killer 直接結束進程。由於終止是由 OS 層級觸發，CLR 不一定能處理並拋出 OutOfMemoryException。此情境需從系統資源與容器限制角度預防。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, D-Q1, C-Q9

Q25: 什麼是容器中的資源管理（cgroups）？
- A簡: Linux 以 cgroups 控制容器的 CPU、記憶體等資源上限與隔離。
- A詳: cgroups 是 Linux 核心機制，用於限制與隔離進程資源，包括記憶體（含 swap）、CPU、I/O。Docker 以 cgroups 設定容器資源上限，避免單一容器耗盡主機。錯誤的限制可能導致 OOM 或性能抖動，需要依工作負載合理配置。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, C-Q5, D-Q8

Q26: 什麼是 Tiny Core Linux？Boot2Docker 的基礎？
- A簡: 極簡 Linux 發行版，體積小、啟動快，為 Boot2Docker 的底層。
- A詳: Tiny Core Linux 是以最小化為目標的 Linux 發行版，提供核心與基本功能，便於快速啟動。Boot2Docker 以此為基礎，打造輕量 Docker 環境，特性包含 RAM 運作、無預設持久存儲與交換空間，利於快速測試但不適合高負載。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, B-Q6, D-Q4

Q27: 什麼是 Overcommit Memory 設定？
- A簡: Linux 控制允許分配超過可用實體的策略，影響分配行為與 OOM風險。
- A詳: vm.overcommit_memory 決定核心在邏輯分配時是否允許超過可用的物理與 swap。模式包含總是允許、嚴格檢查與啟發式。在測試中，未初始化分配可能被允許，造成超大分配數字。適當設定可降低 OOM 風險與誤導性觀測。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q1, D-Q2, C-Q5

Q28: 什麼是大物件堆（LOH）與其碎片化影響？
- A簡: 針對大物件的 GC 區域，壓縮成本高，易受碎片化影響分配失敗。
- A詳: LOH 儲存大於某門檻的物件（如陣列），GC 對其壓縮成本高，通常不常壓縮。大量分配/釋放會使 LOH 容易碎片化，導致大型分配失敗或回收率下降。改善可透過減少大物件、使用池化或啟用適合的 GC 模式。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, D-Q5, C-Q2

Q29: 什麼是 .NET Core 的 GC 壓縮（compaction）概念？
- A簡: 透過移動物件整理堆空間，減少碎片、提升可分配連續區塊。
- A詳: GC 壓縮會在回收後搬移存活物件，釋放連續空間以減少碎片。不同堆（Gen0/1/2/LOH）與模式（Workstation/Server）行為有別。壓縮可提升重分配成功率，但會增加暫停開銷。需依負載特性取捨。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q13, D-Q10, C-Q6

Q30: 為什麼要比較多平台記憶體管理？核心價值？
- A簡: 找出不同 OS/容器下的行為差異，指引部署與調教策略。
- A詳: 多平台比較能揭示 OS、容器與執行時在分配、回收、碎片化與 OOM 行為上的差異。可據此選擇適合的部署環境（如 Ubuntu vs Boot2Docker）與調整參數（swap、cgroups、GC），提升穩定性與效能。本文即提供實測指引。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q15, B-Q17, D-Q5

Q31: 什麼是容器鏡像（image）與拉取（pull）？
- A簡: 鏡像是不可變層的封裝；pull 是從註冊伺服器下載鏡像。
- A詳: Docker 鏡像包含應用與依賴的不可變層，容器由其實例化。docker pull 從登錄伺服器（如 Docker Hub、MCR）下載鏡像。本文拉取 dotnet CLI 鏡像於 Ubuntu/Boot2Docker，用於跨平台一致的測試環境。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, B-Q8, D-Q9

Q32: 什麼是 swap partition 與 swap file 的選擇？
- A簡: 交換分割區與交換檔皆可用；檔更易調整，分割區具穩定性。
- A詳: Linux 可用交換分割區（固定尺寸、獨立分割）或交換檔（柔性調整、建置簡易）。分割區通常效能穩定，檔方便運維。本測試採用 /swapfile 並調整至 4GB，快速驗證虛擬記憶體對容器分配的影響。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q3, B-Q5, D-Q6

Q33: 什麼是 Docker 在 Boot2Docker 的存儲特性？
- A簡: 以 RAM 為主，持久化依附外部磁碟或掛載，預設不配置交換空間。
- A詳: Boot2Docker 的檔案系統主要在 RAM，容器鏡像可存於外接虛擬磁碟或共享資料夾。預設無 swap，寫入壓力下更易受限。適合短時測試，不適合長時高 I/O 或記憶體密集負載。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q20, B-Q6, D-Q4

Q34: 什麼是 OOM 分數（oom_score）與選擇策略？
- A簡: Linux 根據進程分數決定 OOM 時優先終止的對象。
- A詳: oom_score 根據進程記憶體使用、優先級等計算，決定 OOM Killer 的終止順序。可透過 oom_score_adj 調整偏好，降低關鍵進程被殺機率。容器工作負載可藉此控制風險，配合合理內存限制與監控。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q7, D-Q1, C-Q9

Q35: 為什麼測試中採用 1GB RAM 的 VM？
- A簡: 受限資源下壓力測試，更易觀察虛擬記憶體與 GC 的邊界行為。
- A詳: 小 RAM 環境更容易觸發分配極限、碎片化與 OOM，適合驗證 swap 與初始化策略的影響。雖非生產配置，但有助比較平台在壓力下的記憶體管理能力，形成實務調教的依據。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q15, B-Q5, D-Q3

---

### Q&A 類別 B: 技術原理類

Q1: Linux 延遲分頁/overcommit 如何造成「假性大配置」？
- A簡: 未初始化頁面不立即映射，overcommit允許邏輯分配超過物理。
- A詳: 原理在於核心允許 malloc/new 返回成功，頁面在首次觸碰時才以缺頁中斷分配實體。vm.overcommit_memory 若允許，邏輯分配可超過物理+swap上限。測試中未初始化陣列導致報告極大分配量，初始化後觸發實際映射，數據回歸正常。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q6, C-Q4, D-Q2

Q2: Sparse File 在檔案系統中如何運作？
- A簡: 未寫入區段僅記錄邏輯偏移，直到寫入才配置磁碟。
- A詳: 檔案系統維護稀疏映射表，空洞區段不占用空間。寫入時配置資料塊並更新索引。優點是節省空間、加速建立大檔案。與記憶體延遲分頁類比：邏輯存在、實體延後。理解此原理有助辨識「假性大配置」現象。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, A-Q18, D-Q2

Q3: .NET Core GC 如何處理碎片化？核心機制？
- A簡: 透過分代回收與壓縮，減少碎片並回收空間；LOH另有策略。
- A詳: .NET GC以分代管理物件，短命物件在 Gen0/1 回收，長壽在 Gen2。壓縮會搬移物件釋放連續空間，降低碎片。LOH回收策略較保守、壓縮成本高。Server GC以多執行緒提升吞吐，對大量分配有助。配置與模式選擇影響回收率與暫停時間。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q29, C-Q6, D-Q10

Q4: 三階段記憶體測試的執行流程？
- A簡: 大量分配→選擇性釋放造碎片→嘗試重分配並統計回收率。
- A詳: 步驟：1) 第一階段連續分配固定大小陣列至臨界；2) 第二階段釋放部分陣列製造破碎；3) 第三階段嘗試再分配同等大小，記錄成功量與回收百分比。核心組件：分配器、GC、OS分頁/交換。此流程量化不同平台在碎片化後的可用性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, D-Q5, C-Q2

Q5: Ubuntu swap 設定如何影響容器記憶體？
- A簡: swap增加虛擬記憶體總量，延緩 OOM，提升最大分配與回收率。
- A詳: 容器受主機的 RAM 與 swap 影響。Ubuntu 調整 /swapfile 至 4GB，使分配上限顯著提升。流程：建立/啟用 swap→容器獲得更多可用虛擬記憶體→GC 有更大空間進行壓縮與回收。過小 swap 易觸發 OOM，過大可能造成 I/O 壓力。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, C-Q3, D-Q3

Q6: Boot2Docker 架構如何設計？資源運作原理？
- A簡: 基於 Tiny Core、全 RAM 運行、極小系統，持久化依外置，預設無 swap。
- A詳: Boot2Docker 以 Tiny Core Linux 為核心，將系統載入 RAM 中運作，僅最小必要元件，Docker Engine 預裝。資源來自 VM 配置與掛載的外部磁碟。設計目標是快速與輕量，犧牲高負載穩定性。因此在記憶體壓力場景易現侷限。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, D-Q4, C-Q7

Q7: Linux OOM Killer 的機制與流程？
- A簡: 計算 OOM 分數、選擇進程、終止以釋放資源，記錄至系統日誌。
- A詳: 當可用記憶體與 swap 低於安全閾值，核心評估進程的 oom_score，考量優先級、使用量、調整值，選定目標並發送訊號終止。過程記錄至 dmesg/syslog。容器環境下 cgroups 限制亦觸發類似行為。可透過調整分數與限制降低風險。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q8, D-Q1, C-Q9

Q8: Docker cgroups 記憶體/Swap 限制如何生效？
- A簡: 容器啟動時設置限制，核心依 cgroups 控制分配與回收邊界。
- A詳: docker run --memory/--memory-swap 透過 cgroups 設定上限。核心在分配與換出時檢查 cgroups 狀態，超出限制則阻止分配或觸發 OOM。核心組件：cgroup v1/v2、記憶體控制器、容器執行時。需與主機 swap 配置協調。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q17, C-Q5, D-Q8

Q9: rnd.NextBytes 初始化如何導致實體分頁配置？
- A簡: 每次寫入迫使頁面觸碰，觸發缺頁中斷並分配物理記憶體。
- A詳: 未觸碰頁面僅存在邏輯映射。當 rnd.NextBytes 將資料寫入緩衝區時，核心發現頁面未映射，執行缺頁中斷流程，配置實體頁並更新表。如此可避免延遲分頁造成的錯誤分配統計，反映真實記憶體使用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, C-Q2, D-Q2

Q10: Windows pagefile 與 Linux swap 的技術差異？
- A簡: 命名與管理差異，功能類似；預設值與調整方式不同。
- A詳: Windows 的 pagefile 與 Linux 的 swap 皆提供虛擬記憶體。Windows 管理由系統控制，常自動調整；Linux 可使用檔或分割區，手動建立與啟用。性能差異多與磁碟類型、大小與工作負載相關。正確配置對容器穩定性重要。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q23, C-Q3, D-Q6

Q11: 容器內記憶體觀測指標與來源有哪些？
- A簡: free、vmstat、/proc/meminfo、docker stats，配合日誌與dmesg。
- A詳: 在容器/主機可用 free -m、vmstat 觀測可用記憶體與交換；/proc/meminfo 提供詳細指標；docker stats 顯示容器使用與限制；dmesg/syslog 可見 OOM 訊息。綜合監控可定位瓶頸與 OOM 來源。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q8, D-Q1, A-Q25

Q12: LOH 分配與碎片化背後機制？
- A簡: 大物件直接進 LOH，壓縮成本高，碎片化更影響後續分配。
- A詳: 大於閾值的物件直接分配至 LOH，GC 對 LOH 的壓縮較少，以避免高停頓成本。長期大量分配/釋放會造成 LOH 空間零碎，難以重用。應用設計可透過物件池、小物件化或壓縮策略改善。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q28, D-Q5, C-Q2

Q13: Server GC 與 Workstation GC 的運作差異？
- A簡: Server GC並行、吞吐優先；Workstation GC低延遲、互動應用友善。
- A詳: Server GC在多核心伺服器上並行執行，多個 GC 執行緒，提升吞吐；Workstation GC偏重低延遲，適用桌面互動應用。選擇影響停頓時間、分配速度與碎片處理行為。容器中的後端服務通常受益於 Server GC。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, C-Q6, D-Q10

Q14: Boot2Docker 實際寫入 swap 失敗背後原因？
- A簡: 系統在 RAM 中運行、未配置 swap，寫入可能受檔系統/資源限制。
- A詳: Boot2Docker 預設不使用 swap，且檔系統在 RAM。嘗試建立/寫入交換檔可能因空間、掛載與權限限制失敗；即使建立，I/O 壓力在 RAM 上不合理。建議改用完整伺服器，或謹慎掛載外部磁碟並評估風險。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q20, C-Q7, D-Q6

Q15: Docker Toolbox 與 Hypervisor 的互動原理？
- A簡: 透過虛擬機（如 VirtualBox）提供 Linux 主機，承載 Docker Engine。
- A詳: Docker Toolbox 在桌面 OS 上安裝 Hypervisor（VirtualBox/Hyper-V），建立小型 Linux VM（Boot2Docker/Tiny Core），於其內運行 Docker Engine。容器其實在 VM 中運行，資源取決於 VM 配置與 Hypervisor 行為。理解此層有助正確調參。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, D-Q9, C-Q1

Q16: 容器記憶體可能被 OS 直接終結的流程？
- A簡: 觸發 cgroups 或核心 OOM，OS評估分數，發訊號終止進程。
- A詳: 當容器達到 cgroups 限制或主機總記憶不足，核心評估 oom_score並選擇終止目標。容器內應用收到 SIGKILL，無法捕捉並處理，導致無例外直接「Killed」。需從系統資源與限制配置面預防。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q8, D-Q1, C-Q5

Q17: Ubuntu 表現 98.85% 回收比率代表什麼機制？
- A簡: GC與記憶體管理有效壓縮空間，碎片化後仍能高比例重分配。
- A詳: 高回收比率顯示 GC壓縮與頁面管理有效，空閒片段能整合成連續空間。swap提供緩衝，減少 OOM，使第三階段可接近第一階段分配。此結果說明正確初始化與系統調參的價值。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q19, D-Q5, C-Q3

Q18: Boot2Docker 88.46% 的瓶頸來源？
- A簡: 資源保守、無 swap、I/O 限制，導致重分配能力較低。
- A詳: 無 swap與 RAM 檔系統提高壓力，且資源限制保守，使碎片化後可重用空間較少。可能的 I/O 錯誤與隨機失敗也影響穩定性。符合其定位：方便測試、非為高負載設計。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, D-Q4, C-Q7

Q19: 初始化為 0x00 與亂數的差異與最佳化風險？
- A簡: 填0可能被壓縮/最佳化；亂數更能保證真實觸碰每頁。
- A詳: 某些平台對零填充有壓縮或特殊處理，可能低估實際佔用。亂數填充避免此最佳化，讓每頁確實寫入。測試與性能評估時應選擇能代表真實存取行為的初始化策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q22, C-Q2, D-Q2

Q20: 將 32GB VHD 掛載給 Docker 的存儲流程？
- A簡: 在 Hypervisor 建立虛擬磁碟，於 VM 掛載，供 Docker 拉取鏡像與存儲使用。
- A詳: 步驟：於虛擬化平台建立 32GB 虛擬磁碟→掛載至 VM→在 OS 中格式化與掛載→Docker 使用該存儲拉取鏡像與寫入層。核心組件：Hypervisor、VM OS、Docker 存儲驅動。此為 Boot2Docker 測試中提供鏡像空間的做法。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q1, D-Q9, A-Q33

---

### Q&A 類別 C: 實作應用類（10題）

Q1: 如何在 Ubuntu 安裝 Docker 並拉取 .NET CLI 映像？
- A簡: 安裝 Docker Engine，使用 docker pull 取得 dotnet 映像並運行容器。
- A詳: 步驟：1) apt-get install docker.io 或依官方安裝引導；2) systemctl enable/start docker；3) docker pull mcr.microsoft.com/dotnet/sdk:8.0（版本視需求）；4) docker run -it --rm mcr.microsoft.com/dotnet/sdk:8.0 bash。注意：使用最新 LTS、設定代理與存儲驅動。最佳實踐：置於非特權使用者、啟用日誌與資源限制。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, B-Q15, A-Q31

Q2: 如何撰寫 C# 程式進行記憶體碎片化測試？
- A簡: 分配陣列→釋放部分→再分配，以 rnd.NextBytes 初始化測量回收率。
- A詳: 程式：AllocateBuffer(size){ var b=new byte[size]; rnd.NextBytes(b); return b;}；第一階段迭代分配；第二階段釋放部分索引；第三階段嘗試再分配與統計成功。注意：避免填0最佳化、記錄時間與 GC 情況。最佳實踐：分配大小一致、控制總量、收集性能指標。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, B-Q9, D-Q5

Q3: 如何在 Ubuntu 建立與擴增 /swapfile 至 4GB？
- A簡: 關閉 swap→建立檔→設定權限→mkswap→swapon→更新 fstab。
- A詳: 步驟：1) sudo swapoff -a；2) sudo dd if=/dev/zero of=/swapfile bs=1M count=4096；3) sudo chmod 600 /swapfile；4) sudo mkswap /swapfile；5) sudo swapon /swapfile；6) echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab。注意：確保磁碟空間、權限；最佳實踐：設定 vm.swappiness、監控 I/O。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, B-Q5, D-Q6

Q4: 如何在容器內驗證記憶體是否真正被分配？
- A簡: 初始化緩衝區、使用 free/vmstat 觀測、比對 /proc/meminfo 與 docker stats。
- A詳: 步驟：1) 在程式中 rnd.NextBytes 觸碰頁面；2) 容器內執行 free -m、cat /proc/meminfo；3) 觀測 docker stats 與主機 vmstat；4) 比較初始化前後分配量。注意：避免只看邏輯數字，需確認物理與 swap。最佳實踐：配合日誌與性能計數器。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, A-Q10, D-Q2

Q5: 如何在 Docker 設定容器的記憶體與 swap 限制？
- A簡: 使用 --memory 與 --memory-swap 指令，依工作負載與主機配置調參。
- A詳: 範例：docker run --memory=2g --memory-swap=3g --oom-kill-disable ...；流程：估算應用峰值→預留安全緩衝→設定限制→監控調整。注意：--memory-swap 必須≥ --memory；避免設太小導致 OOM。最佳實踐：搭配主機 swap 與告警。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q17, B-Q8, D-Q8

Q6: 如何啟用 .NET Core Server GC（gcServer）？
- A簡: 設定環境變數或 runtimeconfig 啟用 Server GC，提升吞吐與回收。
- A詳: 方法：1) 環境變數 COMPlus_GCServer=1 或 DOTNET_GCServer=1；2) runtimeconfig.json 設定 "System.GC.Server": true。注意：Server GC 適合伺服器負載，可能增加暫停；與容器 CPU 配置搭配。最佳實踐：壓測比對 Workstation/Server。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q13, D-Q10

Q7: 如何在 Boot2Docker 嘗試建立 swap 並評估風險？
- A簡: 掛載外部磁碟、建立交換檔，但需評估 RAM檔系統與穩定性風險。
- A詳: 步驟：1) 於 Hypervisor 掛載持久磁碟；2) 在該掛載點建立 /swapfile（dd/mkswap/swapon）；3) 確認 fstab 或開機腳本；注意：Boot2Docker在RAM運作，swap可能不穩、I/O受限。最佳實踐：若需高負載，改用完整Linux伺服器。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, D-Q6, A-Q20

Q8: 如何監控容器記憶體：free、vmstat、/proc/meminfo？
- A簡: 在容器/主機使用指令與 /proc 觀測指標，結合 docker stats 與日誌。
- A詳: 指令：free -m（總量/可用）、vmstat（分頁/換出）、cat /proc/meminfo（細部）、docker stats（容器使用）。流程：建立基準→壓測觀測變化→記錄 OOM 日誌。最佳實踐：加上告警與趨勢分析。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q11, D-Q1, A-Q25

Q9: 如何處理被 OOM Killed 的 .NET 容器並收集診斷？
- A簡: 重新啟動、查看 dmesg/syslog、分析 docker logs 與指標，調整資源限制。
- A詳: 步驟：1) docker logs 與應用日誌；2) 主機 dmesg/syslog 查 OOM 訊息；3) 分析 docker stats 指標；4) 調整 --memory/--memory-swap、增大主機 swap；5) 若必要調整 oom_score_adj。預防：監控、容量規劃與 GC 調教。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q7, D-Q1

Q10: 如何將測試結果整理成圖表並比較平台？
- A簡: 記錄各階段分配量與回收率，使用圖表呈現趨勢與差異。
- A詳: 步驟：1) 程式輸出分配/回收數據；2) 匯出 CSV；3) 使用 Excel/Notebook 繪製柱狀+折線（分配量與回收%）；4) 註記平台、配置；注意：確保初始化一致、採樣足夠。最佳實踐：附上系統參數、版本與環境描述。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q30, B-Q4, D-Q5

---

### Q&A 類別 D: 問題解決類（10題）

Q1: 遇到「Killed」無例外，如何診斷與處理？
- A簡: 檢查主機/容器 OOM 日誌與資源限制，調整內存與 swap，優化 GC。
- A詳: 症狀：程式突然終止，終端顯示「Killed」。可能原因：cgroups 內存限制、主機 OOM。解法：查 dmesg/syslog、docker stats；提高 --memory/--memory-swap、增大主機 swap；優化分配模式與 GC（Server GC）。預防：監控告警、容量規劃、壓測。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q7, C-Q9

Q2: 看到 300GB~700GB 配置數字，如何確認與修正？
- A簡: 初始化緩衝區、比對 /proc 與 docker stats，禁用誤導性觀測。
- A詳: 症狀：分配數字異常巨大。原因：延遲分頁/overcommit 未初始化。解法：使用 rnd.NextBytes 觸碰頁；以 free/meminfo 觀測真實使用；必要時調整 overcommit 設定。預防：測試時一律初始化、紀錄方法。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, C-Q4, A-Q10

Q3: Ubuntu 無法分配到 2GB 以上，可能原因與解法？
- A簡: swap過小、cgroups限制，需擴大 /swapfile 或放寬容器內存。
- A詳: 症狀：分配量受限。原因：預設 /swapfile 1GB、容器 --memory 限制。解法：擴增 swap 至4GB（dd/mkswap/swapon）；調整容器 --memory/--memory-swap；確認無其他限制。預防：安裝後檢查 swap配置，壓測驗證。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, C-Q3, B-Q5

Q4: Boot2Docker 在第一階段就中止，如何排查？
- A簡: 檢查 RAM/存儲限制與 swap狀況，考慮改用完整伺服器。
- A詳: 症狀：早期分配即失敗或錯誤。原因：RAM運作、無swap、I/O限制。解法：檢查可用資源、嘗試掛載外部磁碟建立交換檔（風險大）、降低負載；建議改用 Ubuntu Server。預防：以 Boot2Docker 僅做輕量測試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q20, B-Q6, C-Q7

Q5: 容器效能不佳、回收比率低，原因與優化？
- A簡: 碎片化嚴重、GC模式不適、資源不足；可調 GC、減少大物件。
- A詳: 症狀：第三階段回收比率低。原因：LOH碎片、GC壓縮不足、內存緊張。解法：啟用 Server GC、減少大物件或改用池化、增加主機 swap；調整分配策略。預防：設計時避免大物件濫用、定期壓測。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q28, B-Q13, C-Q6

Q6: Swap 寫入錯誤訊息噴出，如何解決與預防？
- A簡: 檢查掛載與權限、空間、I/O；在 RAM系統避免依賴 swap。
- A詳: 症狀：系統控制台顯示 swap寫入錯誤。原因：掛載錯誤、權限不足、空間不足、RAM檔系統限制。解法：於持久磁碟建立 swap；確認 chmod 600；確保空間；或停用 swap（RAM系統）。預防：選擇合適平台與存儲。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q14, C-Q7, A-Q33

Q7: Linux CLR 偶發無法拋 OOM 例外，如何應對？
- A簡: 以系統資源管理為主，減少 OOM Killer 觸發機率。
- A詳: 症狀：無例外、直接「Killed」。原因：OS層級 OOM Killer。解法：提升 --memory/--memory-swap、增大主機 swap；優化分配；必要時調整 oom_score_adj；記錄診斷。預防：容量管理、監控與告警。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q24, B-Q7, C-Q9

Q8: Docker 內存限制導致 OOM，如何診斷與調整？
- A簡: 查看 docker stats與啟動參數，適度提高限制或優化應用。
- A詳: 症狀：容器內存達上限後被終止。原因：--memory/--memory-swap 設定過低。解法：提高限制；優化應用分配策略；監控指標。預防：依負載估算、預留緩衝，持續觀測。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q17, B-Q8, C-Q5

Q9: 容器拉取映像空間不足，如何處理 Boot2Docker？
- A簡: 擴充 VM磁碟、掛載外部存儲，或改用完整 Linux 主機。
- A詳: 症狀：docker pull 失敗，空間不足。原因：RAM檔系統/磁碟過小。解法：為 VM 增加虛擬磁碟並掛載；清理未用鏡像；或改用 Ubuntu Server。預防：容量規劃、定期清理。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q15, C-Q1, A-Q33

Q10: .NET 記憶體碎片化嚴重，如何改善 GC 行為？
- A簡: 啟用 Server GC、減少 LOH、採用物件池化，並壓測驗證。
- A詳: 症狀：重分配失敗、回收率低。原因：碎片化、LOH壓縮不足。解法：COMPlus_GCServer=1、調整設計減少大物件、採用池化；觀測 GC 指標。預防：設計階段考量堆使用、定期壓測。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q29, B-Q13, C-Q6

---

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 .NET Core CLI 容器？
    - A-Q2: Ubuntu Server 15.10 在測試中的角色是什麼？
    - A-Q3: 什麼是 Boot2Docker？
    - A-Q4: 什麼是 swapfile？為何影響測試結果？
    - A-Q5: 什麼是 Sparse File（稀疏檔案）？
    - A-Q10: 為什麼需要初始化新配置的記憶體？
    - A-Q11: Windows 與 Linux 虛擬記憶體的預設差異是什麼？
    - A-Q12: Ubuntu 與 Boot2Docker 的記憶體管理差異？
    - A-Q13: Boot2Docker 的核心價值與定位是什麼？
    - A-Q15: 什麼是三階段記憶體測試模型？
    - A-Q31: 什麼是容器鏡像（image）與拉取（pull）？
    - C-Q1: 如何在 Ubuntu 安裝 Docker 並拉取 .NET CLI 映像？
    - C-Q3: 如何在 Ubuntu 建立與擴增 /swapfile 至 4GB？
    - C-Q8: 如何監控容器記憶體：free、vmstat、/proc/meminfo？
    - D-Q3: Ubuntu 無法分配到 2GB 以上，可能原因與解法？

- 中級者：建議學習哪 20 題
    - A-Q6: 什麼是 Linux 的 SPARSEMEM/延遲分頁策略？
    - A-Q8: 什麼是 OOM Killer？為何畫面顯示「Killed」？
    - A-Q17: Docker 容器的記憶體與 swap 限制是什麼？
    - A-Q19: 為什麼 Ubuntu 修正 swap 後表現最佳？
    - A-Q22: 為什麼使用 rnd.NextBytes 初始化記憶體？
    - A-Q25: 什麼是容器中的資源管理（cgroups）？
    - B-Q1: Linux 延遲分頁/overcommit 如何造成「假性大配置」？
    - B-Q3: .NET Core GC 如何處理碎片化？核心機制？
    - B-Q4: 三階段記憶體測試的執行流程？
    - B-Q5: Ubuntu swap 設定如何影響容器記憶體？
    - B-Q8: Docker cgroups 記憶體/Swap 限制如何生效？
    - B-Q9: rnd.NextBytes 初始化如何導致實體分頁配置？
    - C-Q2: 如何撰寫 C# 程式進行記憶體碎片化測試？
    - C-Q4: 如何在容器內驗證記憶體是否真正被分配？
    - C-Q5: 如何在 Docker 設定容器的記憶體與 swap 限制？
    - C-Q6: 如何啟用 .NET Core Server GC（gcServer）？
    - D-Q1: 遇到「Killed」無例外，如何診斷與處理？
    - D-Q2: 看到 300GB~700GB 配置數字，如何確認與修正？
    - D-Q5: 容器效能不佳、回收比率低，原因與優化？
    - D-Q8: Docker 內存限制導致 OOM，如何診斷與調整？

- 高級者：建議關注哪 15 題
    - A-Q27: 什麼是 Overcommit Memory 設定？
    - A-Q29: 什麼是 .NET Core 的 GC 壓縮（compaction）概念？
    - A-Q34: 什麼是 OOM 分數（oom_score）與選擇策略？
    - B-Q7: Linux OOM Killer 的機制與流程？
    - B-Q10: Windows pagefile 與 Linux swap 的技術差異？
    - B-Q12: LOH 分配與碎片化背後機制？
    - B-Q13: Server GC 與 Workstation GC 的運作差異？
    - B-Q14: Boot2Docker 實際寫入 swap 失敗背後原因？
    - B-Q16: 容器記憶體可能被 OS 直接終結的流程？
    - B-Q17: Ubuntu 表現 98.85% 回收比率代表什麼機制？
    - B-Q18: Boot2Docker 88.46% 的瓶頸來源？
    - B-Q19: 初始化為 0x00 與亂數的差異與最佳化風險？
    - C-Q7: 如何在 Boot2Docker 嘗試建立 swap 並評估風險？
    - D-Q6: Swap 寫入錯誤訊息噴出，如何解決與預防？
    - D-Q10: .NET 記憶體碎片化嚴重，如何改善 GC 行為？