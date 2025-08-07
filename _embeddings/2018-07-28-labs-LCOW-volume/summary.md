# 使用 LCOW 掛載 Volume 的效能陷阱

## 摘要提示
- Volume I/O 落差: LCOW 透過 volume 讀寫大量檔案時效能遠遜於 Docker for Windows，甚至可能失敗。
- Jekyll 實測: container→container 僅 12 秒，LCOW volume→container 卻高達 135 秒，差距逾十倍。
- Permission issue: LCOW volume→volume 測試頻繁出現 “Operation not permitted” 錯誤而無法完成。
- dd 基準測試: Hyper-V 隔離層級與跨 OS 邊界會大幅拉高 I/O 時間，LCOW volume 最為明顯。
- Windows process 隔離: Windows container 採 process 隔離時寫入 container/volume 幾乎與原生一樣快。
- Docker for Windows: 透過 SMB 共用單一 VM，volume I/O 表現反而優於 LCOW。
- Nested virtualization: 雲端 VM 內再跑 Hyper-V 的效能低落，不適合生產環境。
- Microsoft 佈局: Windows Container 與 LCOW 主要瞄準開發者的混合 Windows/Linux 體驗。
- 場景選擇: 重 I/O 工作不建議用 LCOW 掛 volume，測試、開發環境則可享其便利。
- 正確定位: 了解各方案優缺點與效能數據，才能避免盲目採用導致「踩雷」。

## 全文重點
作者以自身部落格專案為例，對比 Docker for Windows 與 LCOW (Linux Container on Windows) 在不同掛載方式下的 I/O 效能。LAB1 透過 Jekyll 編譯網站，設計三種來源與目的地組合（volume→volume、volume→container、container→container），並在兩種引擎上重複測試。結果顯示 container→container 最快（約 12 秒），Docker for Windows volume→container 約 36 秒，而 LCOW volume→container 竟需 135 秒；LCOW volume→volume 甚至隨機遭遇檔案寫入失敗。

為釐清差異，LAB2 採用 dd 工具直接量測 1 GB 隨機資料寫入時間，涵蓋 Windows 原生、Linux 原生、Windows container（process/hyper-v）、LCOW、Docker for Windows 等六種組態，再分別落地於 container 與 volume。數據指出：1) 不使用 Hyper-V、僅做 process 隔離時，Windows 與 Linux container 效能與原生幾乎無差；2) 一旦升級至 Hyper-V，寫入 container 時延遲倍增（Windows 約 +276%，LCOW 約 +209%）；3) 掛載 volume 時，Windows container 經最佳化僅小幅增加，但 LCOW 慘跌十餘倍。雲端 VM 再開 Hyper-V 的 nested virtualization 更凸顯效能惡化，顯示不宜在生產環境使用。

作者據此提出觀點：LCOW 的最大價值在於開發階段可同時執行 Windows 與 Linux container、共用網路與 Compose 編排；若應用重度依賴磁碟 I/O，或需大規模檔案處理，仍建議選擇 Windows process 容器或獨立 Linux 節點。 Microsoft 透過 VS、WSL、容器技術與 GitHub 佈局開發者生態，LCOW 與 Windows Container 正是其「留住開發者」策略的一環。最終結論是：效能數字不代表一切，唯有理解產品定位與使用情境，才能做出正確技術決策。

## 段落重點
### LAB1：測試不同環境下 Jekyll 建置時間
作者使用官方 jekyll:2.4.0 映像，設計三種來源/目的地組合，比較 Docker for Windows 與 LCOW。container→container 兩者皆約 12 秒；Docker for Windows volume→container 為 36 秒，而 LCOW 同組態高達 135 秒；LCOW volume→volume 因隨機「Operation not permitted」錯誤無法完成。結果顯示跨越 Host/VM 邊界且使用 Volume 時 LCOW 效能與穩定度皆不佳。

### LAB2：不同組態下 container 的 I/O 效率
改用 dd/urandom 寫入 1 GB 測試，覆蓋 Windows/Linux 原生與多種容器隔離模式。process 隔離下，寫入 container/volume 皆與原生相近；Hyper-V 隔離則明顯拖慢寫入 container 的速度（Windows +3~4 倍，LCOW +3 倍），而 LCOW 寫入 volume 最慢，動輒 20～40 秒。Docker for Windows 因走 SMB share，volume 成績雖較原生慢，但遠優於 LCOW。Nested 虛擬化的 Azure 測試數據加倍惡化，說明雲端 VM 內再跑 Hyper-V 僅適合實驗用途。

### 測試方式與子項（LAB2-1/2/3）
三組硬體：Lenovo 實體 PC、白牌實體 PC、Azure DS4 v3 VM。依序在 Windows Server 1803、Windows 10 1803 與 Azure VM 上進行相同 dd 測試，各自比較不同 isolation 與目標位置。結果一致揭示：process 隔離近原生；Hyper-V 隔離耗時倍增；LCOW 掛 volume 表現最差；Docker for Windows 因共用單一 VM 且走 SMB，volume 雖慢仍可接受。Azure nested 模式則因雙層虛擬化與遠端儲存造成嚴重瓶頸。

### 測試結果解讀
1) Windows container 若能用 process 隔離，I/O 幾乎不受影響；2) Hyper-V 隔離保安全卻犧牲效能，特別是跨 OS 邊界或 LCOW；3) LCOW 目前缺乏針對 Volume 的最佳化，導致大量檔案操作效能低落；4) Docker for Windows 雖非官方，但在 Windows 10 上為 Linux 開發者提供較佳 Volume 表現；5) 雲端 VM 如需混合容器，應透過 Swarm/K8s 將 Linux container 派送至 Linux 節點，避免 nested 虛擬化。

### 結論
容器目標是以近原生效能提供封裝與快取優勢。LCOW 的定位並非高效 I/O，而是讓開發者在單一 Windows 環境同時啟動 Windows 與 Linux container、簡化測試與 CI/CD 流程。對於重度 I/O 或正式環境，建議仍以 Windows process container 或獨立 Linux 節點為主。效能數據並非否定 LCOW，而是提示使用者正確選擇工具：了解自家工作負載特性，選擇最合適的引擎與掛載方式，才不致「膝蓋中箭」。