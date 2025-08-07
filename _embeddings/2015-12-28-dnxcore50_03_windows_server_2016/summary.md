# .NET Core 跨平台 #3, 記憶體管理大考驗 - Windows Container (2016 TP)

## 摘要提示
- .NET Core：以最新 Core CLR 於多種 Windows 平台進行記憶體碎片化測試。  
- 測試流程：重新開機、抓套件、編譯、連跑兩次並取第二次數據，確保公平性。  
- Windows 2012 R2 Server Core：作為成熟對照組，無 GUI、RAM 1 GB、pagefile 4 GB。  
- 記憶體利用率 (2012R2)：Phase 1 可要 4416 MB，Phase 3 僅 2888 MB，利用率 65.40%。  
- Task Manager 觀察：實體 RAM 早被吃滿，其餘全靠虛擬記憶體支撐。  
- Windows Server 2016 Nano：首度支援 Windows Container，採 TP4 版本測試。  
- 記憶體利用率 (Nano Container)：Phase 1 4032 MB、Phase 3 2696 MB，利用率 66.87%。  
- Windows Container：與 Host 共用同一 Kernel，效能與原生系統幾乎等同。  
- Hyper-V Container：Microsoft 進一步提供可選的 Kernel 隔離層，兼得 VM 安全與容器效率。  
- Docker 整合：提供完全相容的 Docker CLI 與 PowerShell 模組，體驗如操作 Linux 容器。

## 全文重點
本篇為 .NET Core 跨平台系列第三篇，作者延續「記憶體管理大考驗」主題，將測試場景移回 Windows，並比較兩種截然不同的環境：1) 傳統但精簡的 Windows Server 2012 R2 Server Core；2) 加入 Windows Container 技術的 Windows Server 2016 Nano TP4。兩個環境皆配置 1 GB RAM，pagefile 採預設 4 GB。作者把相同的 .NET Core 原始碼直接複製到目標機器，就地還原套件、編譯並執行。每次試驗先重開機，再連跑兩次並取第二次結果，排除啟動時的 JIT 與最佳化成本。  
在 2012 R2 上，程式第一階段成功配置 4416 MB 記憶體；隨後經刻意碎片化後重新申請，僅剩 2888 MB，可用比率 65.40%。Task Manager 顯示實體 RAM 幾乎瞬間耗盡，後續全靠 pagefile。接著作者將同一測試包裝成 Windows Container 部署到 2016 Nano。雖然 TP4 仍顯示互動稍慢，但 Phase 1 仍能拿到 4032 MB、Phase 3 2696 MB，利用率 66.87%，與裸機相差極小。從 Host 的 Task Manager 可直接看到 Container 內的 dnx.exe，證明 Container 與 Host 共用 Kernel，而非 VM 式完全隔離。  
此外，Microsoft 在 TP4 新增 Hyper-V Container 方案，當使用者需要 Kernel 隔離時，系統會自動在 Hyper-V 中起一台輕量 VM 再載入容器，兼顧安全與效能；雖本文未實測，但作者留下後續研究筆記。整體而言，Windows Container 對 .NET Core 記憶體管理的影響微乎其微，顯示新一代容器能維持與傳統部署幾乎一致的效能，同時帶來映像一致性與快速複製等優勢。

## 段落重點
### Windows 2012 R2 Server Core（對照組）
作者選用無 GUI 的 Server Core 以減少系統雜訊，並以 1 GB RAM+4 GB pagefile 進行測試。流程為重開機→還原套件→編譯→連跑兩次取第二次結果。Phase 1 可配置 4416 MB，經碎片化後 Phase 3 僅 2888 MB，記憶體利用率 65.40%。Task Manager 顯示 dnx.exe 佔用約 4.5 GB，實體記憶體迅速用完，後續需求全落在虛擬記憶體。整體效能符合預期，無特殊亮點但也無瓶頸。

### Windows Server 2016 Nano TP4（Windows Container）
2016 Nano 為首批支援 Windows Container 的作業系統，透過與 Docker 的整合可使用熟悉的 CLI/PowerShell 建置容器。作者從 Server Core 映像起步手動安裝 .NET Core 及測試程式。雖處預覽期且互動稍慢，Phase 1 仍能拿到 4032 MB，Phase 3 2696 MB，利用率 66.87%，僅比對照組高 1.5%。Host 端 Task Manager 可直接看到容器內程序，證實 Container 與 Host 共用 Kernel，資源使用效率接近裸機。TP4 亦首現 Hyper-V Container，可在需要更高隔離層時自動建立輕量 VM 再執行容器，兼顧安全與效能；此功能尚未在本文測試，但被視為 Windows 容器陣容的一大差異化特點。