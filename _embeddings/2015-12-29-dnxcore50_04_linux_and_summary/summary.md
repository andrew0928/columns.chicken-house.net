# .NET Core 跨平台 #4 ─ 記憶體管理大考驗：Docker 於 Ubuntu / Boot2Docker

## 摘要提示
- Ubuntu Server: 調整 swapfile 並初始化記憶體後，容器可配置 4.8 GB、回收率 98.85%。
- Boot2Docker: 受限於 RAM 運行與缺乏 swap，真實可用記憶體僅約 0.8 GB，回收率 88%，且常見 swap 錯誤。
- SparseMem: Linux 未初始化區塊採類似 sparse file 的 SparseMem 機制，導致「虛假」超大配置。
- 記憶體初始化: 透過寫入亂數強制配置，可排除 SparseMem 造成的偽數值。
- Swapfile 設定: Ubuntu 預設僅 1 GB swap，提升至 4 GB 後測試結果大幅改善。
- CLR 穩定度: Linux 容器記憶體不足時 CLR 可能被 OS 直接 Killed 而無 OOM 例外，穩定度不如 Windows。
- 效率差異: Linux 在碎片化後的記憶體利用率明顯高於 Windows，同時配置量略低。
- Boot2Docker 定位: 追求輕量與快速啟動（全 RAM 27 MB ISO），不適合高負載正式環境。
- 測試環境: 1 GB RAM、32 GB HDD（Ubuntu）或純 RAM（Boot2Docker）之 Docker 容器，執行 .NET Core CLI。
- 待解議題: SparseMem 詳細原理、Linux CLR 被殺原因、gcServer 參數對 Windows 容器的影響。

## 全文重點
本文延續前幾篇 .NET Core 跨平台系列，聚焦於 Linux 家族的兩種典型部署：標準 Ubuntu 15.10 Server 與輕量化 Boot2Docker。作者以相同硬體條件（1 GB RAM、32 GB 虛擬硬碟）執行記憶體壓力測試，觀察 .NET Core 在 Docker 容器內對記憶體配置、碎片化回收與例外處理的表現。

最初在 Ubuntu 測得單一容器竟可「配置」七百多 GB 記憶體，後來確認是 Linux 核心 SparseMem 策略造成未初始化頁面不佔空間的假象。透過在配置後立即寫入亂數強制佔用，數據回到合理值，但又發現 Ubuntu 僅預設 1 GB swap，導致測試早早被 OOM Killed。將 /swapfile 調整為 4 GB 後，容器可一次配置 4.864 GB，碎片化後仍能回收 98.85%，表現甚至超越 Windows Server。

Boot2Docker 因設計上完全從 RAM 運行且無預設 swap，SparseMem 同樣使得初始測試顯示 330 GB 的離譜數字。修正後真實可配置量僅 0.8 GB 左右，且頻繁於第一階段即因 swap write error 終止，成功案例的回收率約 88%。作者推斷其核心與檔案系統組態為了輕量快啟動而犧牲高負載能力，並建議僅作開發測試用途。

綜合四個平台（含先前的兩款 Windows Server），Ubuntu 在記憶體利用率與碎片耐受性上居冠；Windows 在單次可配置量方面仍有優勢，但 Linux CLR 的不穩定（被 OS 強殺、無 OOM 例外）仍待改進。文末列出三項待釐清問題：SparseMem 詳解、Linux CLR 例外行為與 Windows gcServer 參數對碎片的影響，供後續研究。

## 段落重點
### Ubuntu Server 15.10 + Microsoft .NET Core CLI Container
作者以純淨安裝的 Ubuntu 15.10 Server 加上官方 .NET Core CLI 映像進行測試，起初遭遇 SparseMem 造成的虛假 712 GB 配置量；修正後又因預設 /swapfile 只有 1 GB 而頻繁被 OOM Killed。將 swapfile 擴充至 4 GB 後重新測試，第一階段成功配置 4 864 MB，第三階段碎片回收後仍有 4 808 MB，可用率 98.85%。雖偶見 CLR 被系統直接終結的現象，但整體記憶體管理效率優於 Windows，同時揭示 Linux 在未初始化記憶體與 swap 設定上的特殊行為。

### Boot2Docker + Microsoft .NET Core CLI Container
Boot2Docker 以 27 MB ISO、全 RAM 運行為特色，VM 建立後即可直接使用 Docker。測試同樣先遭遇 SparseMem 虛高值，改以亂數初始化後，第一階段僅能配置約 832 MB，且常於寫入 swap 時出現 I/O error 導致容器被殺；成功執行的個案第三階段僅剩 736 MB，可回收率 88.46%。作者判斷 Boot2Docker 的極簡組態不適用高負載場景，建議僅作本機開發或快速 demo 之用，同時提醒讀者勿以測試結果誤解其設計目標。

### 綜合比較與結論
對比四種平台（Windows Server 2016 Container、Windows Server 2012 R2、Ubuntu Server、Boot2Docker），Ubuntu 展現最佳碎片化耐性及回收效率；Windows 雖可配置逾 4 GB，但回收率較低，且須進一步研究 gcServer 參數以改善。Linux CLR 在極端情況會被系統直接 Kill，缺乏可預期的 OOM 例外處理；Boot2Docker 則因架構取向無法與其他伺服器級環境並論。總結而言，正式環境首選仍為 Windows Server 或完整的 Ubuntu Server，Boot2Docker 適合作為輕量測試工具；未來研究方向包括深入理解 SparseMem、探查 Linux CLR 被殺原因及評估不同 GC 策略對碎片的影響。