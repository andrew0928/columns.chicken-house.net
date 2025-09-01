## Case #1: Linux 記憶體「假分配」數據異常（SPARSEMEM/延遲配置）修正

### Problem Statement（問題陳述）
**業務場景**：在進行 .NET Core 記憶體壓力與碎片化回收測試時，於 Ubuntu Server 與 Boot2Docker 的 Docker 容器內執行，需量化不同平台的記憶體配置能力與回收比例。初次測試在 1GB RAM 的主機環境卻觀察到可配置高達數百 GB 的記憶體，數據顯然不合理，導致評估結論失真。
**技術挑戰**：Linux 會延遲實際的記憶體配置（demand paging），未被觸碰（未初始化）的頁面不會真正 commit，出現「可配置超大」的錯覺。
**影響範圍**：會導致記憶體測試報告嚴重失真，跨平台比較無法進行；錯誤結論會影響平台選型與容量規劃。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 測試程式配置 byte[] 但未寫入，OS 不會立即實配記憶體頁面。
2. Linux 採延遲配置與 overcommit 策略，未觸碰的頁面不算真正使用。
3. Docker 容器未對此行為施加限制，進一步放大感知上的「可配置量」。

**深層原因**：
- 架構層面：測試方案未定義「write-touch」以驗證真實 commit。
- 技術層面：未考慮 Linux SPARSEMEM/overcommit 與零頁最佳化帶來的測試假象。
- 流程層面：未建立跨平台一致的測試規範（如記憶體必須初始化）。

### Solution Design（解決方案設計）
**解決策略**：修改測試程式，在每次配置後立即「寫入」緩衝區（使用隨機值），強迫 OS 真正配置頁面並建立公平的跨平台比較基準。

**實施步驟**：
1. 修改配置函式加入初始化
- 實作細節：用 rnd.NextBytes(buffer) 填滿陣列，避免 0x00 被 dedupe/壓縮。
- 所需資源：C#/.NET Core SDK
- 預估時間：0.5 小時

2. 重新執行各平台測試
- 實作細節：於 Ubuntu 與 Boot2Docker 的同一個 .NET Core CLI 容器版本重跑。
- 所需資源：Docker Engine、Microsoft .NET Core CLI 容器映像
- 預估時間：0.5 小時

3. 比對修正前後數據合理性
- 實作細節：確認不再出現「數百 GB」的虛高數據。
- 所需資源：測試日誌、圖表
- 預估時間：0.5 小時

**關鍵程式碼/設定**：
```csharp
// 強制觸碰頁面，避免 Linux 延遲配置/虛高數據
static readonly Random rnd = new Random();

static byte[] AllocateBuffer(int size)
{
    byte[] buffer = new byte[size];
    InitBuffer(buffer); // 關鍵：強制寫入
    return buffer;
}

static void InitBuffer(byte[] buffer)
{
    // 使用隨機，避免 OS 對全 0 進行壓縮/共用零頁優化
    rnd.NextBytes(buffer);
}
```

實際案例：Ubuntu 與 Boot2Docker 初次測試分別出現 712GB、330GB 的「可配置量」錯覺；加入初始化後，回到合理範圍。
實作環境：Ubuntu 15.10 Server、Boot2Docker（Tiny Core Linux）；.NET Core CLI Docker image
實測數據：
- 改善前：Ubuntu 顯示可配置 712GB；Boot2Docker 顯示 330GB（皆不合理）
- 改善後：回歸至與實體 RAM + swap 相符的數值（例如 Ubuntu 最終 4864MB/回收後 4808MB, 98.85%）
- 改善幅度：由「虛高」回歸到真實測值（消除 99% 以上錯誤偏差）

Learning Points（學習要點）
核心知識點：
- Linux demand paging/overcommit 與 SPARSEMEM 概念
- 記憶體測試需「觸碰頁面」才能反映真實用量
- 0x00 初始化可能被 OS/硬體優化

技能要求：
- 必備技能：C#、Docker 操作、基本 Linux 概念
- 進階技能：理解 OS 記憶體管理策略與行為

延伸思考：
- 這個解決方案還能應用在哪些場景？任何需要測量真實記憶體占用的壓測或容器容量規劃。
- 有什麼潛在的限制或風險？隨機填充會增加 CPU 與 IO 壓力。
- 如何進一步優化這個方案？以逐頁觸碰（page-touch）策略降低不必要的寫入成本。

Practice Exercise（練習題）
- 基礎練習：將現有配置程式加上 rnd.NextBytes 並觀察 top/htop 變化（30 分鐘）
- 進階練習：實作以頁大小（4KB）為單位的 page-touch 初始化（2 小時）
- 專案練習：建立可配置初始化策略（零填、隨機、頁觸碰）與報表（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：是否能穩定消除「虛高分配」
- 程式碼品質（30%）：初始化策略可配置、可測
- 效能優化（20%）：初始化成本可控
- 創新性（10%）：頁面級初始化優化與報表呈現


## Case #2: Ubuntu 預設 swap 過小導致測試偏差

### Problem Statement（問題陳述）
**業務場景**：比較 Windows 與 Linux 的記憶體配置與回收能力，初步測試顯示 Linux 配置量低於預期甚至隨機被「Killed」，導致早期結論偏向 Windows。
**技術挑戰**：不同 OS 預設虛擬記憶體（swap）差異很大，Ubuntu 預設僅 1GB。
**影響範圍**：跨平台對比不公平、易誤導平台選型；Linux 測試不穩定。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. Ubuntu 預設 /swapfile 僅 1GB，無法支撐重度配置測試。
2. 可用 swap 太小，當實體 RAM 不足易觸發 OOM killer。
3. 測試前未統一虛擬記憶體配置基準。

**深層原因**：
- 架構層面：缺乏測試前的資源基準化流程。
- 技術層面：忽略 swap 對 heavy allocation 測試的直接影響。
- 流程層面：前期環境核對不足導致錯誤結論。

### Solution Design（解決方案設計）
**解決策略**：將 Ubuntu 的 swapfile 調整至與 Windows 相同的 4GB，重新測試並比對回收比例。

**實施步驟**：
1. 建立並啟用 4GB swapfile
- 實作細節：建立 /swapfile，設定權限，mkswap 與 swapon，並設開機掛載。
- 所需資源：root 權限、Ubuntu 15.10
- 預估時間：0.5 小時

2. 重新執行 .NET Core 記憶體測試
- 實作細節：使用相同的 Docker image 與程式碼
- 所需資源：Docker、.NET Core CLI image
- 預估時間：0.5 小時

3. 記錄與對比數據
- 實作細節：採集第一階段/第三階段數據與回收比
- 所需資源：系統監控工具、測試程式
- 預估時間：0.5 小時

**關鍵程式碼/設定**：
```bash
# 建立 4GB swapfile（Ubuntu）
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
# 開機自動掛載
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
# 確認
free -h
```

實際案例：將 Ubuntu swapfile 調整為 4GB 後重跑測試。
實作環境：Ubuntu 15.10 Server（Docker Engine + .NET Core CLI 容器）
實測數據：
- 改善前：不穩定、配置量低於預期
- 改善後：4864MB / 4808MB，回收比 98.85%
- 改善幅度：穩定性與可用容量大幅提升；消除錯誤結論

Learning Points（學習要點）
核心知識點：
- swap 大小對 heavy allocation 測試的決定性影響
- 測試前資源基準化的重要性
- OOM 與 swap 的關聯

技能要求：
- 必備技能：Linux 管理、swap 設定
- 進階技能：容量規劃、測試設計

延伸思考：
- 這個解決方案還能應用在哪些場景？任何記憶體壓測、容器容量規劃。
- 潛在限制或風險？swap 太大可能掩蓋記憶體不足的實際問題。
- 如何進一步優化？配合 vm.swappiness、cgroups/容器限制精細化管理。

Practice Exercise（練習題）
- 基礎練習：建立/擴充 swapfile 至 2GB 並觀察 free/top（30 分鐘）
- 進階練習：比較在 1G / 4G / 8G swap 下的測試結果（2 小時）
- 專案練習：自動化 swap 校準與測試跑批腳本（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：swap 正確建立並開機生效
- 程式碼品質（30%）：腳本化、可重複
- 效能優化（20%）：合理的 swap 策略
- 創新性（10%）：動態根據負載調整策略


## Case #3: Boot2Docker 記憶體「假分配」與初始化修正

### Problem Statement（問題陳述）
**業務場景**：使用 Boot2Docker 快速搭建 Docker 環境跑 .NET Core 記憶體測試，但初次測試出現可配置 330GB 的離譜結果。
**技術挑戰**：Boot2Docker（Tiny Core Linux）同樣採用延遲配置，未初始化的分配會呈現虛高。
**影響範圍**：不正確的數據導致錯誤決策，低估環境限制。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 分配的 byte[] 未初始化。
2. Boot2Docker 走 RAM 為主、精簡設計，行為更依賴 Linux 的延遲配置。
3. 測試程式未實施頁面觸碰。

**深層原因**：
- 架構層面：選用的極簡環境並非為重度記憶體測試設計。
- 技術層面：忽略初始化導致的 overcommit 假象。
- 流程層面：缺少跨平台一致的測試守則。

### Solution Design（解決方案設計）
**解決策略**：沿用 Ubuntu 修正，配置後立即 init 緩衝，消除虛高；同時將此行為納入跨平台的固定測試規格。

**實施步驟**：
1. 啟用初始化（同 Case #1）
- 實作細節：rnd.NextBytes 觸碰頁面
- 所需資源：C#/.NET Core SDK
- 預估時間：0.5 小時

2. 重新執行多輪測試
- 實作細節：由於 Boot2Docker 不穩定，跑多次取穩定區間
- 所需資源：Boot2Docker VM
- 預估時間：1 小時

3. 記錄實際上限與回收比
- 實作細節：截圖記錄第一/第三階段
- 所需資源：系統監控
- 預估時間：0.5 小時

**關鍵程式碼/設定**：
```csharp
// 同 Case #1，重點在於必須初始化緩衝，避免虛高
rnd.NextBytes(buffer);
```

實際案例：Boot2Docker 初測顯示可配 330GB；加入初始化後回歸合理，並捕捉到一次完整成功的結束畫面。
實作環境：Boot2Docker（Tiny Core Linux, RAM-based），.NET Core CLI 容器
實測數據：
- 改善前：顯示可配置 330GB（不合理）
- 改善後：第一階段 832MB；第三階段 736MB；回收比 88.46%
- 改善幅度：消除虛高，得出真實、可對比的上限與回收率

Learning Points（學習要點）
核心知識點：
- 精簡發行版（RAM-based）對測試行為的影響
- 初始化策略是跨平台測試必要條件
- 「成功結束」需多輪跑測以排除隨機失敗

技能要求：
- 必備技能：Docker/Boot2Docker 操作、C#
- 進階技能：壓測流程設計與重試策略

延伸思考：
- 可應用於其他 RAM-based 容器 OS。
- 風險：重試可能掩蓋底層穩定性問題。
- 優化：建立自動化重跑與統計工具。

Practice Exercise（練習題）
- 基礎練習：於 Boot2Docker 啟用隨機初始化（30 分鐘）
- 進階練習：自動連跑 10 次並彙總結果（2 小時）
- 專案練習：做一個 Boot2Docker vs Ubuntu 的對比報表（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：能重現且修正虛高分配
- 程式碼品質（30%）：初始化模組化
- 效能優化（20%）：重跑與統計自動化
- 創新性（10%）：對 RAM-based 發行版的適配策略


## Case #4: Linux CLR 被 OS 強制終止（無 OOM 例外）之穩定性改善

### Problem Statement（問題陳述）
**業務場景**：在 Linux（Ubuntu/Boot2Docker）執行 .NET Core 測試時，第三階段偶發性被 OS 直接「Killed」，應用無法捕捉 OOM 例外，造成測試中斷。
**技術挑戰**：Linux OOM killer 會在極端資源壓力下直接終止程序；容器內的 CLR 無法在所有情況下及時拋例外。
**影響範圍**：穩定性不足，難以收集完整測試資料；生產風險升高。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 記憶體/交換空間不足，觸發 OOM killer。
2. 程式配置模式瞬間造成高壓，CLR 未來得及丟出 OOM。
3. Boot2Docker 更易受限於 RAM-only 架構。

**深層原因**：
- 架構層面：缺乏容器資源防線（swap/限制/監控）設計。
- 技術層面：未透過 dmesg/虛擬終端及時觀察 kernel OOM log。
- 流程層面：沒有事先建立「穩定性保證」步驟（如先校準 swap）。

### Solution Design（解決方案設計）
**解決策略**：先進行資源校準（擴充 swap 至 4GB）、採用初始化寫入避免 overcommit 假象，再次執行測試；對於 RAM-only 的 Boot2Docker，將其定位為測試用途，重度壓測改用 Ubuntu Server。

**實施步驟**：
1. 擴充與校準 swap（Ubuntu）
- 實作細節：同 Case #2 指令
- 所需資源：root 權限
- 預估時間：0.5 小時

2. 啟用初始化以降低 overcommit 風險
- 實作細節：rnd.NextBytes 初始化
- 所需資源：C#/.NET Core SDK
- 預估時間：0.5 小時

3. 觀察 kernel log 與重試
- 實作細節：開虛擬終端，觀察 dmesg
- 所需資源：系統 log
- 預估時間：1 小時

**關鍵程式碼/設定**：
```bash
# 觀察 OOM 訊息（另開終端）
dmesg --follow | grep -i -E "oom|killed|out of memory"
```

實際案例：Ubuntu 擴充 swap 至 4GB 並啟用初始化後，測試可完整跑完；Boot2Docker 仍偶有失敗，成功一次得 88.46% 回收。
實作環境：Ubuntu 15.10；Boot2Docker；.NET Core CLI 容器
實測數據：
- 改善前：Linux 偶發 Killed，資料不完整
- 改善後（Ubuntu）：4864MB/4808MB，98.85%（可完整測試）
- 改善幅度：穩定性顯著提升；對 Boot2Docker 採取測試定位作為替代方案

Learning Points（學習要點）
核心知識點：
- OOM killer 行為與容器內應用的關聯
- swap 校準與初始化對穩定性的提升
- 觀察 kernel 訊息的重要性

技能要求：
- 必備技能：Linux log 觀察、swap 管理
- 進階技能：測試穩定性設計、容器資源管理

延伸思考：
- 在 Kubernetes/cgroups 下如何進一步做資源限制？
- 可否以漸進式配置曲線降低 peak？
- 以 Windows 作為生產環境的風險/收益評估？

Practice Exercise（練習題）
- 基礎練習：Ubuntu 擴充 swap 後重跑一次（30 分鐘）
- 進階練習：在重壓下觀察 dmesg 並記錄 OOM 日誌（2 小時）
- 專案練習：設計一個自動化穩定性檢測流程（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：完整跑完測試與日誌收集
- 程式碼品質（30%）：測試基線一致
- 效能優化（20%）：降低 OOM 機率
- 創新性（10%）：穩定性策略的自動化與可視化


## Case #5: 跨平台比較基線不一致（swap 差異）導致錯誤結論

### Problem Statement（問題陳述）
**業務場景**：原先結論誤以為 Windows 記憶體配置較優，後發現 Ubuntu 的 swap 預設較小導致測試不公平。
**技術挑戰**：不同 OS 的虛擬記憶體預設差異很大，若不統一，比較結論不可信。
**影響範圍**：平台選型、採購與部署策略可能錯誤。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. Windows 預設 pagefile.sys 約 4GB；Ubuntu 預設 /swapfile 約 1GB。
2. 測試前未統一 swap 配置。
3. 未設計「資源基線核對清單」。

**深層原因**：
- 架構層面：測試框架缺乏「基線校準」階段。
- 技術層面：未意識到 swap 對記憶體壓測的重要性。
- 流程層面：缺少跨平台環境檢核流程。

### Solution Design（解決方案設計）
**解決策略**：在所有比較平台上，先完成相同的 swap 配額（4GB）與初始化策略，然後才開始正式測試與繪圖報告。

**實施步驟**：
1. 制定基線準則
- 實作細節：RAM、swap、容器版本、程式碼初始化策略一致
- 所需資源：測試規範文件
- 預估時間：1 小時

2. 基線核對與簽核
- 實作細節：以 checklist 驗證每台機器
- 所需資源：自動化腳本
- 預估時間：1 小時

3. 重跑測試並產生對比圖
- 實作細節：只保留調整後的結果
- 所需資源：報表工具
- 預估時間：1 小時

**關鍵程式碼/設定**：
```bash
# 例：基線檢查腳本（片段）
echo "RAM: $(grep MemTotal /proc/meminfo)"
echo "Swap: $(grep SwapTotal /proc/meminfo)"
docker --version
dotnet --info
```

實際案例：調整 Ubuntu swap 至 4GB 後，重跑數據顯示 Linux 表現最佳，推翻先前誤判。
實作環境：Windows Server、Ubuntu、Boot2Docker + .NET Core CLI 容器
實測數據：
- 改善前：誤認為 Windows 較佳
- 改善後：Ubuntu 4864MB/4808MB；98.85%，位居最佳
- 改善幅度：結論可信度大幅提升

Learning Points（學習要點）
核心知識點：
- 基線一致性對實驗可信度的影響
- swap 與記憶體壓測關係
- 報告前的驗證流程

技能要求：
- 必備技能：基礎自動化腳本
- 進階技能：測試治理、報告設計

延伸思考：
- 是否需要 CPU/磁碟也做基線統一？
- 如何在 CI 中自動套用基線檢查？
- 異常值如何處理？

Practice Exercise（練習題）
- 基礎練習：寫一個基線檢查腳本（30 分鐘）
- 進階練習：自動生成基線合格報告（2 小時）
- 專案練習：將基線檢查納入 CI pipeline（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：能檢出不一致基線
- 程式碼品質（30%）：腳本穩健
- 效能優化（20%）：核對流程輕量快速
- 創新性（10%）：與 CI/CD 深度整合


## Case #6: Boot2Docker 寫入 swap 相關錯誤與定位策略

### Problem Statement（問題陳述）
**業務場景**：在 Boot2Docker 重度測試時，虛擬終端出現大量錯誤訊息，測試中途失敗，僅偶有一次能完整結束。
**技術挑戰**：Boot2Docker 為 RAM-based 極簡系統，預設不依賴 HDD/無 swapfile，重度記憶體壓力時動態性差。
**影響範圍**：測試可靠性差；不適合生產環境。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. RAM-based 設計，無持久化 swap，重壓時可能出現錯誤。
2. 極簡發行版資源保守，對 I/O/swap 行為較敏感。
3. 容器層未對資源施加保護。

**深層原因**：
- 架構層面：Boot2Docker 定位為「方便測試」，非高負載。
- 技術層面：未提供預設交換空間與高負載優化。
- 流程層面：將測試結果直接類比到生產的誤用。

### Solution Design（解決方案設計）
**解決策略**：將 Boot2Docker 明確定位於「快速測試」，重負載與準生產測試改用 Ubuntu Server；若必須在 Boot2Docker 壓測，需自行規劃持久化存儲與 swap（但此屬進階客製）。

**實施步驟**：
1. 環境定位與切分
- 實作細節：Boot2Docker 用於拉 image/輕量測；Ubuntu 用於重度壓測
- 所需資源：VM 管理
- 預估時間：0.5 小時

2. 以 Ubuntu 重跑重度測試
- 實作細節：同 Case #2/3 配置
- 所需資源：Ubuntu VM
- 預估時間：1 小時

3. （選配）Boot2Docker 客製 swap
- 實作細節：在持久化磁碟（如 /mnt/sda1）建立 swapfile（版本差異大，需自測）
- 所需資源：Boot2Docker 磁碟掛載
- 預估時間：1 小時

**關鍵程式碼/設定**：
```bash
# Boot2Docker（示意）在可寫入的持久化掛載點建立 swapfile（版本差異需自行驗證）
sudo dd if=/dev/zero of=/mnt/sda1/swapfile bs=1M count=2048
sudo chmod 600 /mnt/sda1/swapfile
sudo mkswap /mnt/sda1/swapfile
sudo swapon /mnt/sda1/swapfile
free -h
```

實際案例：Boot2Docker 多次失敗、僅一次成功（回收 88.46%）；Ubuntu 可穩定完成（98.85%）。
實作環境：Boot2Docker、Ubuntu 15.10
實測數據：
- Boot2Docker：第一 832MB、第三 736MB、回收 88.46%（偶發失敗）
- Ubuntu：4864MB/4808MB、回收 98.85%（穩定）
- 效益：將重壓改至 Ubuntu 後，測試可靠性大幅提升

Learning Points（學習要點）
核心知識點：
- RAM-based 精簡系統的定位與限制
- 測試/生產環境的角色分工
- swap 對穩定性的影響

技能要求：
- 必備技能：VM/容器環境規劃
- 進階技能：極簡系統客製化（持久化/開機腳本）

延伸思考：
- 也可考慮使用完整 Linux 發行版的最小化映像替代。
- Boot2Docker 更新版掛載點差異需驗證。
- 長期應以 IaC（Packer/Cloud-Init）維運。

Practice Exercise（練習題）
- 基礎練習：在 Ubuntu 與 Boot2Docker 各跑一次測試並對比（30 分鐘）
- 進階練習：嘗試為 Boot2Docker 建立臨時 swapfile（2 小時）
- 專案練習：設計一套測試/生產環境分層與切換策略（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：正確完成對比與策略切分
- 程式碼品質（30%）：客製腳本可重複
- 效能優化（20%）：穩定性顯著提升
- 創新性（10%）：環境治理策略完整


## Case #7: 初始化策略從「全 0」改為「隨機」避免壓縮/去重干擾

### Problem Statement（問題陳述）
**業務場景**：為避免 OS 對全 0 進行壓縮或共用零頁而低估真實內存使用，需改變初始化策略。
**技術挑戰**：初始化為全 0 可能被 OS/硬體最佳化，造成低估。
**影響範圍**：壓測數據偏低、不準確。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 全 0 容易被壓縮或映射至同一零頁。
2. 實際 commit 未達「最差情境」。
3. 測試程式僅執行配置未驗證內容。

**深層原因**：
- 架構層面：缺少資料圖樣（pattern）策略。
- 技術層面：忽略 OS 針對固定模式的優化。
- 流程層面：初始化策略未列入測試規範。

### Solution Design（解決方案設計）
**解決策略**：將初始化改為隨機資料，確保每頁真實被寫入與佔用，避免壓縮/去重。

**實施步驟**：
1. 將 InitBuffer 改為 rnd.NextBytes
- 實作細節：同 Case #1 代碼
- 所需資源：C#
- 預估時間：0.5 小時

2. 重測並核對記憶體 commit
- 實作細節：觀察 free/htop 變化
- 所需資源：Linux 工具
- 預估時間：0.5 小時

**關鍵程式碼/設定**：
```csharp
static void InitBuffer(byte[] buffer)
{
    rnd.NextBytes(buffer); // 避免 0x00 模式被壓縮/共享零頁
}
```

實際案例：作者原本考慮填 0，改為隨機以避免最佳化，使測試更簡潔也更可靠。
實作環境：Ubuntu、Boot2Docker
實測數據：
- 改善前：存在低估風險
- 改善後：確保真實 commit，對齊 swap+RAM 的實際上限（Ubuntu 98.85% 回收）
- 改善幅度：數據可信度提升

Learning Points（學習要點）
核心知識點：
- 資料圖樣對記憶體管理的影響
- 共享零頁與壓縮
- 測試可靠性的工程化

技能要求：
- 必備技能：C#、OS 基礎
- 進階技能：壓測設計與效度評估

延伸思考：
- 可否改為按頁觸碰以降低 CPU 成本？
- 在 NUMA/透明大頁（THP）環境的行為如何？
- 隨機種子的一致性控制？

Practice Exercise（練習題）
- 基礎練習：比較 0x00 vs 隨機初始化的內存佔用（30 分鐘）
- 進階練習：以頁為單位的初始化實作（2 小時）
- 專案練習：設計可切換資料圖樣的測試框架（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：能避免低估 commit
- 程式碼品質（30%）：策略可配置
- 效能優化（20%）：初始化成本可控
- 創新性（10%）：圖樣策略的擴展性


## Case #8: 以 Ubuntu Server 作為重度壓測與生產候選環境

### Problem Statement（問題陳述）
**業務場景**：需為 .NET Core 記憶體敏感型工作負載選擇 Linux 發行版；Boot2Docker 表現不穩定。
**技術挑戰**：Boot2Docker 為測試導向，資源配置保守；需一個穩定且可擴展的平台。
**影響範圍**：壓測結果可信度與生產穩定性。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. Boot2Docker RAM-based、無預設 swap，重負載不穩定。
2. Ubuntu Server 可靈活配置 swap 與資源。
3. 官方 .NET Core CLI 容器在 Ubuntu 上更一致可靠。

**深層原因**：
- 架構層面：環境定位不同，測試與生產需求不一致。
- 技術層面：資源池彈性與管理工具缺口。
- 流程層面：未明確指定壓測環境標準。

### Solution Design（解決方案設計）
**解決策略**：以 Ubuntu Server + 4GB swap 作為記憶體壓測與生產前測的標準平台；Boot2Docker 僅作快速驗證。

**實施步驟**：
1. 建立 Ubuntu 標準映像
- 實作細節：安裝 Docker Engine、設置 4GB swap
- 所需資源：Ubuntu 15.10
- 預估時間：1 小時

2. 拉取 .NET Core CLI 容器執行測試
- 實作細節：docker pull + dotnet 測試
- 所需資源：Docker、網路
- 預估時間：0.5 小時

3. 產出基準數據
- 實作細節：記錄三階段數據與回收比
- 所需資源：測試程式
- 預估時間：0.5 小時

**關鍵程式碼/設定**：
```bash
# 標準化 Ubuntu 測試步驟（摘要）
sudo apt-get update && sudo apt-get install -y docker.io
# 建立 4GB swap（見 Case #2）
# 拉取 .NET Core CLI 容器（示意）
docker pull mcr.microsoft.com/dotnet/sdk
```

實際案例：Ubuntu 最終測得 4864MB/4808MB，回收 98.85%，表現最佳；Boot2Docker 88.46% 且不穩定。
實作環境：Ubuntu 15.10 Server；.NET Core CLI 容器
實測數據：
- Ubuntu：4864MB / 4808MB，98.85%
- Boot2Docker：832MB / 736MB，88.46%
- 效益：以 Ubuntu 作為重壓標準環境，測試穩定性與上限明顯更優

Learning Points（學習要點）
核心知識點：
- 發行版定位與測試可靠性
- swap 與資源可擴展性
- 容器化對重負載的影響

技能要求：
- 必備技能：Linux/Docker 管理
- 進階技能：容量規劃、基準測試

延伸思考：
- 其他發行版（Alpine、Debian）在相同策略下的表現？
- 不同 GC 模式對結果的影響？
- 長期監控與告警如何整合？

Practice Exercise（練習題）
- 基礎練習：在 Ubuntu 上重跑測試（30 分鐘）
- 進階練習：變動 swap 大小觀察回收比變化（2 小時）
- 專案練習：建立標準化壓測映像與 pipeline（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：標準環境可重現最佳結果
- 程式碼品質（30%）：自動化建置腳本
- 效能優化（20%）：穩定性與上限提升
- 創新性（10%）：跨發行版對比方法


## Case #9: Boot2Docker 快速體驗 vs 生產適用性辨識

### Problem Statement（問題陳述）
**業務場景**：需快速啟動 Docker 環境進行試驗，但最終要確保生產級可靠性。
**技術挑戰**：Boot2Docker 體積小（~27MB）、5 秒開機，適合快速體驗；但 RAM-based、無 swap，重負載表現差。
**影響範圍**：若誤用於生產，易出現不穩定與性能不足。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. Boot2Docker 為 Tiny Core Linux，完全自 RAM 運行。
2. 設計目標是「快速、輕量、體驗」非「高負載」。
3. 預設缺少持久化資源與 swap 支援。

**深層原因**：
- 架構層面：工具定位與使用場景不匹配。
- 技術層面：缺乏擴充與資源治理手段。
- 流程層面：環境選型未區分開發/測試/生產。

### Solution Design（解決方案設計）
**解決策略**：將 Boot2Docker 僅用於快速 PoC；任何性能/穩定性測試一律轉至 Ubuntu Server 或類似完整發行版。

**實施步驟**：
1. 明確制定環境用途矩陣
- 實作細節：文件化，評審；Boot2Docker=PoC；Ubuntu=壓測/生產前測
- 預估時間：0.5 小時

2. 建立模板與腳本
- 實作細節：分別建立 boot2docker.iso 啟動腳本與 Ubuntu IaC
- 預估時間：1 小時

3. 相關人員培訓與守則
- 實作細節：在團隊內公告
- 預估時間：0.5 小時

**關鍵程式碼/設定**：
```text
策略要點：
- Boot2Docker：~27MB, ~5s boot, RAM-based（快速體驗）
- Ubuntu Server：可配置 swap、資源充足（壓測/準生產）
```

實際案例：Boot2Docker 僅做拉 image/簡測；重壓改用 Ubuntu，獲得穩定 98.85% 回收。
實作環境：Boot2Docker、Ubuntu
實測數據：
- Boot2Docker：88.46% 回收（且偶發失敗）
- Ubuntu：98.85% 回收（穩定）
- 效益：環境定位清晰，避免誤用引發風險

Learning Points（學習要點）
核心知識點：
- 發行版定位與適用性
- 快速體驗 vs 生產可靠性的取捨
- 團隊規範的重要性

技能要求：
- 必備技能：環境選型
- 進階技能：治理與培訓

延伸思考：
- 其他輕量替代方案（如 Alpine）如何定位？
- 是否引入雲端即開即用的 Docker 主機替代？

Practice Exercise（練習題）
- 基礎練習：用 Boot2Docker 拉取並啟動 .NET Core 容器（30 分鐘）
- 進階練習：在 Ubuntu 上重現壓測數據並出報告（2 小時）
- 專案練習：完成「環境用途矩陣」與內規文件（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：用途矩陣落地
- 程式碼品質（30%）：啟動腳本/文件清晰
- 效能優化（20%）：壓測改用正確平台
- 創新性（10%）：治理機制的完整性


## Case #10: 三階段記憶體碎片化測試法建置

### Problem Statement（問題陳述）
**業務場景**：需要量化不同 OS/容器的記憶體配置上限與碎片化回收能力。
**技術挑戰**：設計一個可重複、跨平台一致的測試方法。
**影響範圍**：影響最終對平台的性能評估與選型。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 單次配置無法看出碎片化後的回收能力。
2. 不一致的初始化與 swap 使結果不可比。
3. 測試代碼需可控與可視化。

**深層原因**：
- 架構層面：缺乏標準化測試流程。
- 技術層面：OS 行為差異造成干擾。
- 流程層面：缺少資料可視化。

### Solution Design（解決方案設計）
**解決策略**：以三階段（初配/釋放/再配）來觀察碎片化的回收比例，輔以初始化與 swap 校準，最後輸出圖表比較。

**實施步驟**：
1. 建立三階段測試代碼
- 實作細節：以固定粒度配置→釋放→再配置
- 所需資源：C#/.NET
- 預估時間：1 小時

2. 初始化與 swap 校準
- 實作細節：同 Case #1/#2
- 所需資源：Linux/Windows 主機
- 預估時間：1 小時

3. 數據收集與視覺化
- 實作細節：輸出 CSV，繪製柱狀/折線圖
- 所需資源：Excel/腳本
- 預估時間：1 小時

**關鍵程式碼/設定**：
```csharp
// 示意：三階段測試
List<byte[]> phase1 = new();
for (int i = 0; i < N1; i++) phase1.Add(AllocateBuffer(CHUNK));

phase1.Clear(); GC.Collect(); GC.WaitForPendingFinalizers();

List<byte[]> phase3 = new();
for (int i = 0; i < N3; i++) phase3.Add(AllocateBuffer(CHUNK));

// 計算回收比例 = phase3總量 / phase1總量
```

實際案例：文中以「第一階段 vs 第三階段」與回收比例來比較各環境。
實作環境：Windows、Ubuntu、Boot2Docker；.NET Core CLI 容器
實測數據（節錄）：
- Ubuntu：4864MB / 4808MB；回收 98.85%
- Boot2Docker：832MB / 736MB；回收 88.46%
- 效益：以統一方法穩定對比不同平台表現

Learning Points（學習要點）
核心知識點：
- 記憶體碎片化測量方法
- 初始化與 swap 對測試有效度的影響
- 基準數據的圖表化

技能要求：
- 必備技能：C#、資料處理
- 進階技能：測試框架設計

延伸思考：
- 是否要加入不同 chunk size 的敏感度分析？
- GC 模式/參數對結果的影響？

Practice Exercise（練習題）
- 基礎練習：實作三階段測試並輸出 CSV（30 分鐘）
- 進階練習：加入不同 chunk size 與圖表（2 小時）
- 專案練習：建立完整的多平台跑批與報表（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：三階段測試可重現
- 程式碼品質（30%）：參數化良好
- 效能優化（20%）：測試時間/負載合理
- 創新性（10%）：圖表與洞察品質


## Case #11: Boot2Docker 磁碟空間規劃避免拉取映像失敗

### Problem Statement（問題陳述）
**業務場景**：Boot2Docker 以 ISO 啟動，若無附加磁碟，拉取大型 Docker 映像可能因空間不足失敗。
**技術挑戰**：RAM-based 系統可寫空間小，需外掛 VHD 作為儲存層。
**影響範圍**：映像拉取/更新失敗，測試流程中斷。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 預設無 HDD，寫入空間有限。
2. 拉取官方 .NET CLI 映像需較大儲存空間。
3. 無持久化磁碟導致每次重開需重拉。

**深層原因**：
- 架構層面：Boot2Docker 設計為輕量啟動。
- 技術層面：儲存層不足。
- 流程層面：環境準備疏漏。

### Solution Design（解決方案設計）
**解決策略**：啟動 VM 時附加 32GB VHD，將其提供給 Docker Engine 使用，確保映像能順利拉取並持久化。

**實施步驟**：
1. 建 VHD 並掛載
- 實作細節：於 Hypervisor（如 VirtualBox/Hyper-V）建立 32GB 虛擬磁碟並附加
- 預估時間：0.5 小時

2. 啟動 Boot2Docker 並確認可寫入
- 實作細節：確認 /var/lib/docker 或對應掛載點可用容量
- 預估時間：0.5 小時

3. 拉取 .NET Core CLI 映像
- 實作細節：docker pull 測試
- 預估時間：0.5 小時

**關鍵程式碼/設定**：
```bash
# 驗證 Docker 儲存目錄容量（示意）
df -h /var/lib/docker
docker pull mcr.microsoft.com/dotnet/sdk
```

實際案例：作者附加 32GB VHD，映像拉取與測試順利。
實作環境：Boot2Docker + 32GB VHD
實測數據：
- 改善前：存在空間不足風險
- 改善後：映像可順利拉取，測試流程不中斷
- 效益：提高測試準備效率與穩定性

Learning Points（學習要點）
核心知識點：
- RAM-based 系統的儲存限制
- Docker 儲存層依賴
- VM 磁碟規劃

技能要求：
- 必備技能：Hypervisor 操作
- 進階技能：Docker 儲存配置

延伸思考：
- 是否改用持久化主機映射卷？
- 拉取映像的快取策略？

Practice Exercise（練習題）
- 基礎練習：附加一顆 16GB 磁碟並拉取映像（30 分鐘）
- 進階練習：測試重新開機後映像是否持久（2 小時）
- 專案練習：自動化建立 VM + VHD + Docker 初始化（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：映像拉取成功且持久
- 程式碼品質（30%）：自動化腳本清晰
- 效能優化（20%）：縮短準備時間
- 創新性（10%）：可移植性與可重用性


## Case #12: 將「初始化規範」納入跨平台測試標準作業流程（SOP）

### Problem Statement（問題陳述）
**業務場景**：不同測試者在不同環境執行，因初始化差異導致數據不可比。
**技術挑戰**：無一致的初始化規範（是否觸碰頁面、資料圖樣）。
**影響範圍**：報告可信度下降，難以回溯。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 測試者自行決定是否初始化。
2. 無共同的「資料圖樣」規範。
3. 未明訂測試代碼版本。

**深層原因**：
- 架構層面：缺乏測試治理。
- 技術層面：缺少初始化策略模板。
- 流程層面：版本控管與簽核不足。

### Solution Design（解決方案設計）
**解決策略**：制定 SOP：強制初始化（隨機）、固定 chunk size、統一 swap、統一容器版本、統一報告格式。

**實施步驟**：
1. 撰寫 SOP 與範例代碼
- 實作細節：提供初始化工具類別
- 預估時間：1 小時

2. 建立自動化校驗
- 實作細節：CI 驗證測試代碼版本與設定
- 預估時間：2 小時

3. 統一報表模板
- 實作細節：CSV 欄位、圖表樣式
- 預估時間：1 小時

**關鍵程式碼/設定**：
```csharp
// InitializationPolicy.cs（片段）
public enum InitPattern { Random /*...*/ }
public static void Apply(byte[] buffer, InitPattern pattern = InitPattern.Random)
{
    rnd.NextBytes(buffer);
}
```

實際案例：文中以「改為隨機初始化」作為關鍵修正，值得納入 SOP。
實作環境：多平台
實測數據：
- 改善前：結果不可比
- 改善後：結果可比（例如 Ubuntu 98.85%、Boot2Docker 88.46%）
- 效益：報告可信度與可重複性提升

Learning Points（學習要點）
核心知識點：
- 測試治理與 SOP 重要性
- 初始化策略標準化
- 報表一致性

技能要求：
- 必備技能：文件化能力、代碼封裝
- 進階技能：CI/CD 整合

延伸思考：
- 將 SOP 模板版本化與審核流程？
- 將測試代碼封裝為 NuGet 套件？

Practice Exercise（練習題）
- 基礎練習：把初始化策略封裝成靜態類別（30 分鐘）
- 進階練習：CI 檢查測試程式版本與設定檔（2 小時）
- 專案練習：完成 SOP + 範例工程 + 報表模板（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：SOP 可落地
- 程式碼品質（30%）：封裝清晰
- 效能優化（20%）：提升測試效率
- 創新性（10%）：與工具鏈整合


## Case #13: 以圖表呈現碎片回收比例，提升決策效率

### Problem Statement（問題陳述）
**業務場景**：利害關係人不易從大量文字數據理解差異。
**技術挑戰**：需以視覺化呈現三階段數據與回收比例。
**影響範圍**：決策效率與認知一致性。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 文字陳述難以比較多平台結果。
2. 沒有統一圖表格式。
3. 回收比例（%）需直觀呈現。

**深層原因**：
- 架構層面：缺乏視覺化標準。
- 技術層面：原始數據未結構化。
- 流程層面：報告步驟未包含圖表輸出。

### Solution Design（解決方案設計）
**解決策略**：將第一/第三階段配置量用柱狀圖呈現，回收比用折線呈現；統一配色與順序。

**實施步驟**：
1. 數據結構化輸出
- 實作細節：CSV 欄位：平台、階段1、階段3、回收%
- 預估時間：0.5 小時

2. 繪圖腳本
- 實作細節：用 Python/Excel 自動繪製
- 預估時間：1 小時

3. 報告模板整合
- 實作細節：圖表與結論一體化
- 預估時間：0.5 小時

**關鍵程式碼/設定**：
```python
# 繪圖示意（matplotlib）
import pandas as pd, matplotlib.pyplot as plt
df = pd.read_csv('result.csv')
# 畫柱狀 + 折線（略）
```

實際案例：文中以柱狀（階段分配量）+ 折線（回收%）呈現，清楚對比 Ubuntu/Boot2Docker 差異。
實作環境：任意
實測數據：
- 例：Ubuntu 98.85%、Boot2Docker 88.46%
- 效益：提高閱讀效率與決策品質

Learning Points（學習要點）
核心知識點：
- 如何用圖表呈現多維數據
- 回收比例作為核心 KPI
- 視覺化標準化

技能要求：
- 必備技能：資料處理/繪圖
- 進階技能：報告自動化

延伸思考：
- 加上置信區間/箱型圖顯示多輪結果？
- 以 dashboard 呈現？

Practice Exercise（練習題）
- 基礎練習：將測試結果轉 CSV（30 分鐘）
- 進階練習：畫出柱狀+折線圖（2 小時）
- 專案練習：產出一套完整報表（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：圖表正確表達
- 程式碼品質（30%）：腳本清晰
- 效能優化（20%）：自動化流程
- 創新性（10%）：圖表設計


## Case #14: Linux 記憶體效率普遍高於 Windows 的測試設計與觀測

### Problem Statement（問題陳述）
**業務場景**：需比較不同 OS 的碎片化後回收效率，作為平台選型參考。
**技術挑戰**：避免因環境差異造成錯誤判讀。
**影響範圍**：影響最終部署決策。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 未初始化/未統一 swap 會扭曲比較。
2. 必須以百分比回收作為核心 KPI。
3. 測試需跨多平台一致執行。

**深層原因**：
- 架構層面：測試設計需理清因果。
- 技術層面：CLR 與 OS 行為差異。
- 流程層面：需有標準化報告。

### Solution Design（解決方案設計）
**解決策略**：三階段測法 + 初始化 + swap 校準，將回收比視為主指標；多輪測試取穩定值。

**實施步驟**：
1. 設定一致基線（見 Case #5）
2. 啟用初始化（見 Case #1/#7）
3. 多輪測試/取中位數

**關鍵程式碼/設定**：
```text
KPI：回收比例（第三階段/第一階段）
```

實際案例：文中指出 Linux 明顯優於 Windows（多數可達 90% 以上），Ubuntu 實測 98.85%。
實作環境：多平台
實測數據：
- Ubuntu：98.85%
- Linux 整體：多數 >90%（相較 Windows）
- 效益：為平台選型提供量化依據

Learning Points（學習要點）
核心知識點：
- 以百分比 K PI 消弭硬體差異的干擾
- 多輪測試與統計
- 測試治理

技能要求：
- 必備技能：測試設計
- 進階技能：統計與報告

延伸思考：
- 不同 GC 參數/版本的影響？
- 容器限制（cgroups）加入比較？

Practice Exercise（練習題）
- 基礎練習：取三輪測試回收比平均（30 分鐘）
- 進階練習：加入置信區間（2 小時）
- 專案練習：完成跨平台比較白皮書（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：KPI 設計正確
- 程式碼品質（30%）：資料處理與統計
- 效能優化（20%）：測試效率
- 創新性（10%）：洞察的深度


## Case #15: 將 Linux OOM 訊息與測試流水線整合（可觀測性）

### Problem Statement（問題陳述）
**業務場景**：偶發 Killed 事件難以追蹤根因，需要把 OOM 訊息納入測試流水線。
**技術挑戰**：容器內外多層日志分散，需集中收斂。
**影響範圍**：問題定位困難，重現成本高。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. OOM 訊息在 kernel log，應用內看不到。
2. 多輪測試資料缺少關聯時間戳。
3. 無集中化日誌彙整。

**深層原因**：
- 架構層面：測試流水線缺可觀測性設計。
- 技術層面：日誌採集未覆蓋 kernel。
- 流程層面：問題重現機制不足。

### Solution Design（解決方案設計）
**解決策略**：在測試期間並行收集 dmesg（或 /var/log/kern.log）、容器 stdout，建立時間戳對齊，將 OOM 事件與測試階段關聯。

**實施步驟**：
1. 啟動 dmesg 監聽
- 實作細節：dmesg --follow 過濾 OOM 關鍵詞
- 預估時間：0.5 小時

2. 測試程式輸出事件時間戳
- 實作細節：各階段開始/結束/錯誤打點
- 預估時間：0.5 小時

3. 對齊與產報
- 實作細節：腳本合併兩路日誌生成報表
- 預估時間：1 小時

**關鍵程式碼/設定**：
```bash
# 併發收集
(dmesg --follow | grep -i -E "oom|killed|out of memory") > kernel.log &
dotnet run > app.log
# 對齊
paste -d '|' app.log kernel.log > merged.log
```

實際案例：文中於虛擬終端觀測到錯誤訊息，將此納入正式測試流程可大幅提高可觀測性。
實作環境：Ubuntu/Boot2Docker
實測數據：
- 改善前：僅見 Killed，無上下文
- 改善後：可定位 OOM 與測試階段關聯
- 效益：定位效率提升，降低重現成本

Learning Points（學習要點）
核心知識點：
- 可觀測性與測試融合
- kernel log 與應用日志整合
- 事件對齊方法

技能要求：
- 必備技能：Linux 日誌
- 進階技能：資料對齊與報表

延伸思考：
- 導入 ELK/Promtail 等集中式日志方案？
- 加入記憶體指標（/proc/meminfo）採集？

Practice Exercise（練習題）
- 基礎練習：並行收集 app/kernal 日誌（30 分鐘）
- 進階練習：自動生成 OOM 事件報告（2 小時）
- 專案練習：整合集中式日誌平台（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：可對齊與定位 OOM
- 程式碼品質（30%）：腳本可靠
- 效能優化（20%）：收集負擔可控
- 創新性（10%）：報表洞察


## Case #16: 以「回收比例」作為核心 KPI 的決策方法論

### Problem Statement（問題陳述）
**業務場景**：需要一個能跨平台/跨版本比較且不受硬體差異過度影響的指標。
**技術挑戰**：單看配置量不準；需能衡量碎片化後的可用性。
**影響範圍**：平台選型、優化方向。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 絕對配置量受 RAM/swap 影響大。
2. 碎片化後能否再利用才是關鍵。
3. 需簡潔的一致性指標。

**深層原因**：
- 架構層面：缺乏統一 KPI。
- 技術層面：GC/OS 行為差異需抽象化衡量。
- 流程層面：報告聚焦紊亂。

### Solution Design（解決方案設計）
**解決策略**：採「第三階段/第一階段」為回收比例 KPI，輔以圖表報告，將平台差異具象化。

**實施步驟**：
1. 定義 KPI 與計算方式
2. 測試程式輸出所需數據
3. 報告聚焦於 KPI

**關鍵程式碼/設定**：
```text
回收比例 = 第三階段總配置量 / 第一階段總配置量
```

實際案例：文中以回收比例作結論主指標，Ubuntu 98.85% > Boot2Docker 88.46%。
實作環境：多平台
實測數據：
- Ubuntu：98.85%
- Boot2Docker：88.46%
- 效益：統一指標，決策明確

Learning Points（學習要點）
核心知識點：
- KPI 設計與可比性
- 碎片化影響的量化
- 報告聚焦技巧

技能要求：
- 必備技能：資料分析
- 進階技能：決策方法論

延伸思考：
- 可加入 p95/p99 統計？
- 對不同工作負載的延展？

Practice Exercise（練習題）
- 基礎練習：手算回收比例（30 分鐘）
- 進階練習：多輪取平均/中位（2 小時）
- 專案練習：建立 KPI 儀表板（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：KPI 準確實作
- 程式碼品質（30%）：資料處理穩健
- 效能優化（20%）：報表效率
- 創新性（10%）：展示與洞察


==============================
案例分類
1. 按難度分類
- 入門級（適合初學者）
  - Case #3, #7, #8, #9, #11, #16
- 中級（需要一定基礎）
  - Case #1, #2, #4, #5, #10, #13, #14, #15
- 高級（需要深厚經驗）
  - Case #6, #12

2. 按技術領域分類
- 架構設計類
  - Case #5, #8, #9, #12, #16
- 效能優化類
  - Case #1, #2, #4, #6, #7, #10, #14
- 整合開發類
  - Case #11, #13, #15
- 除錯診斷類
  - Case #4, #6, #15
- 安全防護類
  - （本次文章無明確安全議題）

3. 按學習目標分類
- 概念理解型
  - Case #7, #9, #14, #16
- 技能練習型
  - Case #1, #2, #3, #10, #11, #13
- 問題解決型
  - Case #4, #5, #6, #12, #15
- 創新應用型
  - Case #12, #13, #16

==============================
案例關聯圖（學習路徑建議）
- 先學案例（基礎概念與基線）
  - Case #9（環境定位）→ Case #11（磁碟規劃）→ Case #3（Ubuntu swap 設定）
- 測試正確性與方法論
  - Case #7（初始化策略）→ Case #1（Linux 假分配修正）→ Case #10（三階段測法）→ Case #16（KPI 設計）
- 跨平台公平性與結論可信度
  - Case #5（基線統一）→ Case #13（圖表報告）
- 稳定性與除錯
  - Case #4（Killed/穩定性）→ Case #15（可觀測性整合）
- 環境選型與定位
  - Case #6（Boot2Docker 錯誤與定位）→ Case #8（Ubuntu 作為標準壓測/生產前測）

依賴關係：
- Case #1 依賴 Case #7 的初始化概念
- Case #2、#5 依賴 Case #3（swap 校準）
- Case #10、#16 依賴 Case #1、#5（正確性與基線）
- Case #4、#6 依賴 Case #1、#3（避免 OOM 與環境不穩）
- Case #13 依賴 Case #10、#16 的數據產出

完整學習路徑建議：
1) Case #9 → #11 → #3 → #7 → #1 → #10 → #16
2) 然後進入公平性與呈現：#5 → #13
3) 強化穩定性與診斷能力：#4 → #15
4) 最後建立環境選型與策略：#6 → #8 → #12

以上 16 個案例均以文中問題、根因、解法與成效為基礎，並補足操作步驟與關鍵代碼，便於教學、實作與評估。