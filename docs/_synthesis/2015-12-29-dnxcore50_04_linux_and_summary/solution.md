---
layout: synthesis
title: ".NET Core 跨平台 #4, 記憶體管理大考驗 – Docker @ Ubuntu / Boot2Docker"
synthesis_type: solution
source_post: /2015/12/29/dnxcore50_04_linux_and_summary/
redirect_from:
  - /2015/12/29/dnxcore50_04_linux_and_summary/solution/
postid: 2015-12-29-dnxcore50_04_linux_and_summary
---

## Case #1: 消除 Linux 虛高記憶體數據：以隨機初始化避免 SPARSEMEM/延遲配置誤判

### Problem Statement（問題陳述）
業務場景：團隊要比較 .NET Core 在不同作業系統與容器上的記憶體管理表現，據以決定生產環境選型與調校策略。初次在 Ubuntu 與 Boot2Docker 進行容器化測試時，監測到不可思議的配置結果（Ubuntu 可配置 712GB，Boot2Docker 可配置 330GB），數據顯然不合理，造成決策混淆與測試延宕。  
技術挑戰：Linux 會對未觸碰的頁面採用延遲配置（lazy allocation）/稀疏記憶體（SPARSEMEM）策略，導致只「宣告」未「實觸」的記憶體不會立刻消耗實體資源，致使測試出現虛高數據。  
影響範圍：誤導容量與效率評估、造成跨平台結論偏差、可能導致錯誤的容量規劃與成本預估。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 測試程式只宣告 byte[] 未初始化，未觸碰頁面不會佔用實體記憶體。
2. Linux 內核對未觸碰頁面採行延遲配置，造成「看似已配置、實際未占用」的錯覺。
3. 以不完整指標（僅看配置總量）判讀，未交叉驗證 RSS/可用記憶體。

深層原因：
- 架構層面：未建立「觸碰頁面」的測試治具以逼真還原實際負載。
- 技術層面：對 Linux 記憶體策略（SPARSEMEM/overcommit/lazy allocation）理解不足。
- 流程層面：缺乏「結果異常時的驗證流程（code/系統層交叉驗證）」。

### Solution Design（解決方案設計）
解決策略：在每次配置緩衝區後立即以隨機資料觸碰頁面，強迫 OS 將虛擬頁面映射至實體記憶體/交換空間，杜絕虛高數據；同時以系統指標（free/ps）交叉驗證結果，確保測試可重現且可信。

### 實施步驟
1. 在配置後初始化緩衝區
- 實作細節：以 Random.NextBytes(buffer) 填入隨機值，避免 0x00 被壓縮/去重。
- 所需資源：.NET Core CLI container、C# Random。
- 預估時間：0.5 小時

2. 交叉驗證系統層指標
- 實作細節：容器內用 free -h、ps -o pid,rss,vsz 驗證 RSS 實際成長。
- 所需資源：Docker、Linux 基本工具。
- 預估時間：0.5 小時

3. 重跑測試，對照前後差異
- 實作細節：記錄初始化前後的可配置量差異與穩定性。
- 所需資源：相同映像與硬體配置。
- 預估時間：0.5 小時

### 關鍵程式碼/設定
```csharp
// 以隨機資料初始化，強迫觸碰每一頁
static readonly Random rnd = new Random();

static byte[] AllocateBuffer(int size)
{
    var buffer = new byte[size];
    rnd.NextBytes(buffer); // 觸碰頁面，避免虛高配置
    return buffer;
}
```

實際案例：Ubuntu 初測顯示可配置 712GB；Boot2Docker 顯示 330GB。加入初始化後回歸合理值。  
實作環境：Ubuntu 15.10 Server + Docker Engine + Microsoft .NET Core CLI Container；Boot2Docker（Docker Toolbox 內 Tiny Core Linux）。  
實測數據：
- 改善前：Ubuntu/Boot2Docker 顯示 712GB/330GB（虛高）
- 改善後：Ubuntu 能達 4864MB（搭配 4GB swapfile），Boot2Docker 首階段約 832MB
- 改善幅度：測試結果由不可用的虛高值轉為可比對的實測值（質化改善）

Learning Points（學習要點）
核心知識點：
- Linux lazy allocation/SPARSEMEM 導致未觸碰頁面不佔資源
- 測試應強制觸碰頁面，否則數據不可信
- 以 RSS/可用記憶體交叉驗證

技能要求：
- 必備技能：C# 記憶體操作、Linux 基本指令
- 進階技能：了解 OS 記憶體策略、容器觀測

延伸思考：
- 還可用於驗證 memory-mapped file、huge pages 行為
- 風險：過度初始化將增加測試時間
- 優化：以分段初始化權衡精準度與成本

Practice Exercise（練習題）
- 基礎練習：改寫你的配置程式，加入 Random.NextBytes，觀察 free -h 變化
- 進階練習：比較填 0x00 與亂數對 RSS 的差異（30%/2h）
- 專案練習：建立跨 OS 自動化測試腳本，輸出前後差異報告（8h）

Assessment Criteria（評估標準）
- 功能完整性（40%）：是否確實觸碰頁面避免虛高
- 程式碼品質（30%）：可讀性、可重用性、記錄完善
- 效能優化（20%）：初始化策略與成本控制
- 創新性（10%）：觀測與比對方法多樣性


## Case #2: 跨平台基準不公平：Ubuntu 預設 1GB swap 導致結果偏差，統一至 4GB

### Problem Statement（問題陳述）
業務場景：為公平比較 Windows 與 Ubuntu 上 .NET Core 容器的可配置記憶體量與碎片化回收率，需確保兩端虛擬記憶體策略一致。初期忽略 Ubuntu 預設僅有 1GB /swapfile，而 Windows Server 預設 pagefile 4GB，導致 Ubuntu 測得可配置量偏低，結論偏誤。  
技術挑戰：不同 OS 預設交換空間差異巨大，直接影響總可配置記憶體與 OOM 行為。  
影響範圍：錯誤的環境優劣判斷、錯配硬體資源、影響上線風險。  
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. Ubuntu 預設 /swapfile 僅 1GB。
2. Windows 預設 pagefile 約 4GB，總可配置量較高。
3. 未事先列出並對齊關鍵基線（swap 大小）。

深層原因：
- 架構層面：評測基線未標準化（RAM、swap、磁碟）。
- 技術層面：忽略交換空間對 OOM 與可配置量的影響。
- 流程層面：缺少「基線對齊清單」與檢核步驟。

### Solution Design（解決方案設計）
解決策略：將 Ubuntu 的 swapfile 對齊至 4GB，重跑整套測試以確保可比性，並保留修改前後的數據以佐證差異。

### 實施步驟
1. 檢查現有 swap
- 實作細節：swapon --show、free -h
- 所需資源：sudo 權限
- 預估時間：0.1 小時

2. 建立與啟用 4GB swapfile
- 實作細節：fallocate -l 4G /swapfile; chmod 600 /swapfile; mkswap /swapfile; swapon /swapfile; 永久化寫入 /etc/fstab
- 所需資源：Linux 管理工具
- 預估時間：0.3 小時

3. 重跑測試並比對
- 實作細節：保存前後測試結果與差異
- 所需資源：相同容器與程式碼
- 預估時間：0.5 小時

### 關鍵程式碼/設定
```bash
# 檢查
swapon --show
free -h

# 建立 4GB swapfile
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

實際案例：作者增設 4GB /swapfile 後重測。  
實作環境：Ubuntu 15.10 Server + Docker Engine + .NET Core CLI 容器。  
實測數據：
- 改善前：第一階段約 1792MB（未對齊 swap）
- 改善後：4864MB / 4808MB，回收率 98.85%
- 改善幅度：可配置量大幅提升（約 2.7 倍），指標可信度提升

Learning Points（學習要點）
核心知識點：
- swap 對總可配置記憶體的影響
- 基線對齊的重要性
- 前後對照實驗設計

技能要求：
- 必備技能：Linux 系統管理、基礎容器操作
- 進階技能：性能基線建立與驗證

延伸思考：
- 依工作負載調整 swap 大小與 swappiness
- 過大 swap 可能拖慢 OOM，導致更長延遲
- 自動化基線檢核腳本

Practice Exercise（練習題）
- 基礎練習：建立 2GB 與 4GB swap 比較可配置量差異（30 分）
- 進階練習：寫腳本於測試前自動檢核並對齊 swap（2 小時）
- 專案練習：建立跨 OS 基線檢核報表（RAM/CPU/磁碟/swap）（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：swap 對齊與永久化
- 程式碼品質（30%）：腳本穩健與可讀性
- 效能優化（20%）：對齊後數據穩定度
- 創新性（10%）：自動化與可視化呈現


## Case #3: Linux OOM Killer 導致 .NET 程序被強制 Killed 的取證與緩解

### Problem Statement（問題陳述）
業務場景：在 Ubuntu 容器測試第三階段時，應用並未拋出 .NET OOM 例外，而是被系統直接 Killed，畫面僅顯示「Killed」。  
技術挑戰：Linux OOM Killer 在極端內存壓力下可能先於 CLR 介入，導致無法在應用層接收到例外，且故障表徵不穩定。  
影響範圍：難以在應用層捕捉並降級處理，降低可靠性與可觀測性。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 交換空間不足，導致 OOM Killer 觸發。
2. 記憶體壓力高峰發生在 GC 回收前。
3. 容器/主機資源配置不一致。

深層原因：
- 架構層面：對 OOM 行為及優先順序缺乏保護機制。
- 技術層面：交換空間小、未對應工作負載特性。
- 流程層面：缺少內核訊息取證與事件告警。

### Solution Design（解決方案設計）
解決策略：擴充分頁檔（Case #2）、重跑測試驗證穩定性；同時建立取證流程（dmesg/journalctl），一旦發生「Killed」事件可快速定位為 OOM Killer 所致。

### 實施步驟
1. 擴充分頁檔並對齊基線
- 實作細節：套用 Case #2 的 4GB swapfile
- 所需資源：sudo 權限
- 預估時間：0.5 小時

2. 建立 OOM 取證流程
- 實作細節：dmesg -T | grep -i -E 'oom|killed'; journalctl -k
- 所需資源：Linux 日誌工具
- 預估時間：0.5 小時

3. 重跑並驗證
- 實作細節：觀察是否仍出現 Killed；保存內核訊息
- 所需資源：相同容器與程式碼
- 預估時間：0.5 小時

### 關鍵程式碼/設定
```bash
# 收集 OOM/Killed 線索
dmesg -T | grep -i -E 'oom|killed'
journalctl -k | grep -i -E 'oom|killed'
```

實際案例：增加 swap 後，Ubuntu 測試達到 4864MB/4808MB（98.85%）且穩定完成，未再頻繁出現「Killed」。  
實作環境：Ubuntu 15.10 Server + Docker Engine + .NET Core CLI 容器。  
實測數據：
- 改善前：第三階段偶發 Killed
- 改善後：完整跑完三階段，並得到 98.85% 回收率

Learning Points（學習要點）
核心知識點：
- OOM Killer 行為與應用層例外的差異
- 交換空間對 OOM 的影響
- 內核取證流程

技能要求：
- 必備技能：Linux 日誌查詢、資源監控
- 進階技能：OOM 分析與策略調整

延伸思考：
- 可否在容器層加入記憶體限制與預警
- 如何在應用層實施預先降載策略
- 以壓測找出 OOM 前的預兆

Practice Exercise（練習題）
- 基礎練習：觸發小規模 OOM 並用 dmesg 取證（30 分）
- 進階練習：寫一個腳本一旦偵測「Killed」就抓取關聯日誌（2 小時）
- 專案練習：建立 OOM 事件到告警系統的串接（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：是否能再現並取證 OOM
- 程式碼品質（30%）：腳本穩健性
- 效能優化（20%）：降低 OOM 發生率
- 創新性（10%）：自動化與可視化能力


## Case #4: Boot2Docker 虛高配置（330GB）矯正：初始化記憶體還原真實可用量

### Problem Statement（問題陳述）
業務場景：在 Boot2Docker 上同樣觀察到未初始化記憶體導致的虛高配置（高達 330GB），誤導測試數據並難以與 Ubuntu/Windows 比對。  
技術挑戰：Boot2Docker 也採用 Linux 內核策略，未觸碰頁面不佔用資源，需以初始化方式校正。  
影響範圍：錯誤結論、資源規劃偏差、測試報告可信度下降。  
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 未觸碰已配置的緩衝區。
2. 內核延遲配置導致虛高。
3. 未交叉驗證 RSS。

深層原因：
- 架構層面：測試治具未強制觸碰頁面。
- 技術層面：忽略容器/發行版差異。
- 流程層面：缺乏準備度檢核（初始化策略未生效）。

### Solution Design（解決方案設計）
解決策略：套用 Case #1 的隨機初始化策略，並在 Boot2Docker 進行交叉驗證，將虛高 330GB 矯正為真實可配置數字。

### 實施步驟
1. 在 Boot2Docker 版測試程式加入頁面觸碰
- 實作細節：Random.NextBytes(buffer)
- 所需資源：.NET Core CLI
- 預估時間：0.5 小時

2. 觀測 free -h 與 RSS
- 實作細節：驗證實際記憶體佔用
- 所需資源：Linux 指令
- 預估時間：0.2 小時

3. 出具更正報告
- 實作細節：紀錄前後數據與差異
- 所需資源：報表工具
- 預估時間：0.3 小時

### 關鍵程式碼/設定
```csharp
// 與 Case #1 相同：以亂數初始化避免虛高
rnd.NextBytes(buffer);
```

實際案例：Boot2Docker 由 330GB 虛高改為實測後的首階段 832MB、第三階段 736MB。  
實作環境：Boot2Docker（Docker Toolbox 內 Tiny Core Linux）+ .NET Core CLI 容器。  
實測數據：
- 改善前：330GB（虛高）
- 改善後：832MB（第一階段），736MB（第三階段），回收率 88.46%

Learning Points（學習要點）
核心知識點：
- 初始化頁面對數據真實性的關鍵性
- 不同發行版仍有一致的延遲配置特性
- 指標應以實測驗證

技能要求：
- 必備技能：C#、容器操作
- 進階技能：效能資料校正

延伸思考：
- 若必須用 Boot2Docker，如何建立輕量但可信的評測流程
- 與 Ubuntu 的差異是否來自 swap 或檔案系統特性
- 是否需要額外持久化層協助測試

Practice Exercise（練習題）
- 基礎練習：在 Boot2Docker 重現虛高與矯正（30 分）
- 進階練習：批次產生前後對照報表（2 小時）
- 專案練習：將初始化策略封裝為可重用 NuGet（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：可重現與矯正虛高
- 程式碼品質（30%）：封裝與測試
- 效能優化（20%）：初始化成本控制
- 創新性（10%）：自動報表/可視化


## Case #5: Boot2Docker 隨機 swap 寫入錯誤與不穩定，改用 Ubuntu Server/加入交換空間

### Problem Statement（問題陳述）
業務場景：Boot2Docker 測試時，第一階段即偶發失敗，虛擬主控台顯示大量 swap 寫入錯誤；成功次數少、數據不穩定。  
技術挑戰：Boot2Docker 以 RAM 運作、體積小、不依賴磁碟，預設沒有可觀交換空間與持久化，面對高記憶體壓力測試先天不利。  
影響範圍：測試不可重現、不適合用作容量與穩定性評估。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 以 RAM 運作、不配置持久化 swap。
2. 高壓測試需大量 swap，導致寫入錯誤。
3. 配置保守，資源未被充分利用。

深層原因：
- 架構層面：Boot2Docker 設計目標是快速測試而非高負載。
- 技術層面：缺少持久化儲存與交換空間。
- 流程層面：未依工作負載選擇合適發行版。

### Solution Design（解決方案設計）
解決策略：將高記憶體壓測移轉至 Ubuntu Server（可配置磁碟與 swap），或為測試目的改用具持久層與可調整 swap 的 Linux 發行版；Boot2Docker 僅作快速功能驗證。

### 實施步驟
1. 選擇合適發行版
- 實作細節：改用 Ubuntu Server 並配置 32GB 磁碟與 4GB swap
- 所需資源：虛擬機管理工具
- 預估時間：1 小時

2. 重跑測試與比較
- 實作細節：與 Boot2Docker 數據對照（穩定性/回收率）
- 所需資源：相同容器與程式碼
- 預估時間：1 小時

3. 界定使用邊界
- 實作細節：制定「何時用 Boot2Docker、何時用 Server 發行版」
- 所需資源：團隊共識
- 預估時間：0.5 小時

### 關鍵程式碼/設定
```text
無需程式碼變更；屬於環境選型與系統配置問題。
```

實際案例：Boot2Docker 成功跑完時回收率 88.46%（832MB/736MB）；Ubuntu Server 達 98.85%（4864MB/4808MB），且穩定無隨機錯誤。  
實作環境：Boot2Docker vs Ubuntu 15.10 Server。  
實測數據：穩定性與回收率 Ubuntu 明顯優於 Boot2Docker。

Learning Points（學習要點）
核心知識點：
- 發行版選型與設計目標（RAM 運作 vs 可持久）
- 交換空間缺失對壓測的影響
- 不同發行版的穩定性差異

技能要求：
- 必備技能：發行版選型與安裝
- 進階技能：根據工作負載制訂環境準則

延伸思考：
- 是否有輕量且可配置 swap 的替代發行版
- 以雲端 VM 搭配持久化磁碟的可行性
- 透過 cgroup 設限保護主機（延伸）

Practice Exercise（練習題）
- 基礎練習：在 Boot2Docker 與 Ubuntu 分別跑一次壓測並記錄穩定性（30 分）
- 進階練習：寫比較報告，提出選型建議（2 小時）
- 專案練習：以 IaC 自動化建置 Ubuntu 測試環境（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：穩定重現與比對
- 程式碼品質（30%）：IaC 腳本品質（若實作）
- 效能優化（20%）：穩定性提升
- 創新性（10%）：選型準則完整度


## Case #6: 建立 .NET Core 三階段記憶體破碎化測試治具（容器化）

### Problem Statement（問題陳述）
業務場景：團隊需要一套可重現的記憶體破碎化測試治具，以度量不同環境的「可配置量」與「碎片化後的回收能力」。  
技術挑戰：需容器化、可跨 OS 執行、可自動化，並能避免延遲配置的誤差。  
影響範圍：作為性能決策與容量規劃的基礎數據來源。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 缺少標準化測試程式（跨 OS 一致）。
2. 未觸碰頁面導致數據不可信。
3. 無一致的結果匯總與指標。

深層原因：
- 架構層面：缺乏容器化治具。
- 技術層面：測試邏輯未封裝。
- 流程層面：結果未自動化整理。

### Solution Design（解決方案設計）
解決策略：以 .NET Core 建立三階段壓測程式（配置/釋放/再配置），容器化執行；每次配置後觸碰頁面，並輸出「首配量」「碎後回收量」「回收率」三指標。

### 實施步驟
1. 擬定三階段流程與資料結構
- 實作細節：List<byte[]> 管理配置，釋放後再配置
- 所需資源：.NET Core CLI
- 預估時間：1 小時

2. 容器化與跨 OS 執行
- 實作細節：docker run -v 挂載程式碼，跨 OS 執行
- 所需資源：Docker Engine
- 預估時間：1 小時

3. 結果輸出與比對
- 實作細節：輸出 CSV/JSON，含三指標
- 所需資源：簡單報表腳本
- 預估時間：1 小時

### 關鍵程式碼/設定
```csharp
var rnd = new Random();
var blocks = new List<byte[]>();
int blockSize = 16 * 1024 * 1024; // 16MB
long firstTotal = 0, thirdTotal = 0;

// 第一階段：配置並觸碰
try {
    while (true) {
        var buf = new byte[blockSize];
        rnd.NextBytes(buf);
        blocks.Add(buf);
        firstTotal += blockSize;
    }
} catch (OutOfMemoryException) { }

// 第二階段：釋放一半（模擬碎片化）
for (int i = 0; i < blocks.Count; i += 2) blocks[i] = null;
GC.Collect(); GC.WaitForPendingFinalizers();

// 第三階段：再次配置
try {
    while (true) {
        var buf = new byte[blockSize];
        rnd.NextBytes(buf);
        thirdTotal += blockSize;
    }
} catch (OutOfMemoryException) { }

double reclaimRate = (double)thirdTotal / firstTotal * 100.0;
Console.WriteLine($"First={firstTotal/1024/1024}MB Third={thirdTotal/1024/1024}MB Rate={reclaimRate:F2}%");
```

實際案例：本文所有數據皆出自此類三階段測試。  
實作環境：同上。  
實測數據：Ubuntu 4864MB/4808MB（98.85%）、Boot2Docker 832MB/736MB（88.46%）。

Learning Points（學習要點）
核心知識點：
- 三階段設計與碎片化回收評估
- 容器化跨 OS 一致性
- 輸出可比指標

技能要求：
- 必備技能：C#、Docker
- 進階技能：測試封裝與自動化

延伸思考：
- 調整 blockSize 對結果的影響
- 加入多執行緒對 GC 行為的影響
- 以 CI 定期回歸

Practice Exercise（練習題）
- 基礎練習：實作三階段測試並輸出結果（30 分）
- 進階練習：容器化與跨 OS 跑測（2 小時）
- 專案練習：加上 CSV 彙總與圖表（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：三階段正確與指標完備
- 程式碼品質（30%）：結構清晰、可維護
- 效能優化（20%）：測試時間與穩定性
- 創新性（10%）：報表自動化


## Case #7: 建立「碎片化回收率」指標與計算方法

### Problem Statement（問題陳述）
業務場景：單看可配置總量不足以反映記憶體管理品質，需制定「碎片化回收率」作為跨環境可比的核心指標。  
技術挑戰：如何量化「碎片化後回收」的能力，並確保數據可重複、可比較。  
影響範圍：影響 GC 策略、環境選型與容器配置。  
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 缺少統一指標衡量碎片化影響。
2. 測試資料無標準化輸出。
3. 無自動化計算與校驗。

深層原因：
- 架構層面：缺乏度量模型。
- 技術層面：未系統化儀表板與報表。
- 流程層面：無跨環境對照流程。

### Solution Design（解決方案設計）
解決策略：定義回收率 = 第三階段配置量 / 第一階段配置量，並在測試程式內自動輸出；各環境皆用此指標比較。

### 實施步驟
1. 指標定義與程式輸出
- 實作細節：Console.WriteLine 格式化輸出
- 所需資源：C#
- 預估時間：0.2 小時

2. 結果收集與對照
- 實作細節：彙整成表/圖（如文中圖表）
- 所需資源：腳本或手動
- 預估時間：0.5 小時

3. 制定閾值
- 實作細節：例如 >95% 優、90~95% 良、<90% 待改善
- 所需資源：團隊共識
- 預估時間：0.5 小時

### 關鍵程式碼/設定
```csharp
double rate = 100.0 * thirdTotal / firstTotal;
Console.WriteLine($"ReclaimRate={rate:F2}% (First={firstTotal/MB}MB, Third={thirdTotal/MB}MB)");
```

實際案例：Ubuntu 98.85%、Boot2Docker 88.46%。  
實作環境：同上。  
實測數據：見上。

Learning Points（學習要點）
核心知識點：
- 指標設計與跨環境可比性
- 數據驅動決策
- 統計與視覺化

技能要求：
- 必備技能：基本程式輸出與資料處理
- 進階技能：報表/圖表建立

延伸思考：
- 再加入平均延遲/GC 次數等輔助指標
- 多次重跑取中位數以抗離群值
- 自動化儀表板

Practice Exercise（練習題）
- 基礎練習：輸出回收率並手繪圖（30 分）
- 進階練習：寫 Python/PowerShell 匯總圖（2 小時）
- 專案練習：打造簡易儀表板（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：指標正確輸出
- 程式碼品質（30%）：工具腳本品質
- 效能優化（20%）：處理多次測試資料
- 創新性（10%）：圖表與洞察


## Case #8: 避免零值填充導致的壓縮/去重：以亂數填充提高測試真實性

### Problem Statement（問題陳述）
業務場景：為避免 OS 對全 0 頁面做壓縮或透明最佳化，導致測試數據偏高，需改用亂數填充。  
技術挑戰：不同 OS/內核對可壓縮資料可能做最佳化，影響測試準確度。  
影響範圍：誤判可配置量與回收率。  
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 以 0x00 填充可能被壓縮/去重，降低實際佔用。
2. 測試假設資料均質。
3. 缺少對壓縮最佳化的防範。

深層原因：
- 架構層面：未針對資料模式設計測試。
- 技術層面：忽略資料可壓縮性。
- 流程層面：未記錄資料模式。

### Solution Design（解決方案設計）
解決策略：改以 Random.NextBytes 亂數填充，使頁面不可壓縮/去重，確保每一頁都被實際配置。

### 實施步驟
1. 將填充策略改為亂數
- 實作細節：rnd.NextBytes(buffer)
- 所需資源：C#
- 預估時間：0.1 小時

2. 交叉驗證
- 實作細節：觀察 RSS/可用記憶體下降趨勢
- 所需資源：Linux 指令
- 預估時間：0.2 小時

### 關鍵程式碼/設定
```csharp
// 避免 0x00 填充被壓縮/去重
rnd.NextBytes(buffer);
```

實際案例：作者由「填 0x00」改為「亂數」，數據更可信。  
實作環境：同上。  
實測數據：可信度提升（質化）。

Learning Points（學習要點）
核心知識點：
- 可壓縮資料對測試的影響
- 亂數填充的重要性
- 觀測指標交叉驗證

技能要求：
- 必備技能：C#
- 進階技能：效能測試策略

延伸思考：
- 可納入多種資料分佈進行對照
- 在長程測試控制亂數種子
- 衡量初始化成本

Practice Exercise（練習題）
- 基礎練習：0x00 vs 隨機填充對 RSS 的影響（30 分）
- 進階練習：不同分佈（常態/均勻）對結果影響（2 小時）
- 專案練習：封裝為「不可壓縮填充器」元件（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：確保頁面被觸碰
- 程式碼品質（30%）：抽象與測試
- 效能優化（20%）：初始化負載可控
- 創新性（10%）：資料分佈設計


## Case #9: 更正錯誤結論：「Windows > Linux 可配置量」源於 swap 誤差

### Problem Statement（問題陳述）
業務場景：初步結論認為 Windows 可配置量明顯高於 Linux；後經查核，發現 Ubuntu 預設 swap 僅 1GB，造成偏誤。  
技術挑戰：如何在發現基線問題後快速更正結論並溝通影響。  
影響範圍：避免錯誤的生產環境選擇與資源規劃。  
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. swap 未對齊跨 OS。
2. 以偏概全的初步觀察。
3. 未在結論前執行反證流程。

深層原因：
- 架構層面：基線未制度化。
- 技術層面：忽略虛擬記憶體策略差異。
- 流程層面：缺少結論審核與同行覆核。

### Solution Design（解決方案設計）
解決策略：增設 Ubuntu 4GB swap 後重測，更新報告與圖表，註記修訂時間與原因。

### 實施步驟
1. 對齊基線（見 Case #2）
2. 重測產出新數據
3. 發佈修訂：註明「2015/12/29 01:23 修訂」

### 關鍵程式碼/設定
```text
以流程為主：對齊 swap -> 重測 -> 修訂報告
```

實際案例：修訂後 Ubuntu 可配置 4864MB，回收率 98.85%。  
實作環境：同上。  
實測數據：更新後 Linux 表現優秀。

Learning Points（學習要點）
核心知識點：
- 基線錯誤會導致結論錯誤
- 科學測試需可修訂
- 紀錄修訂與影響面

技能要求：
- 必備技能：測試方法論
- 進階技能：報告治理

延伸思考：
- 建立結論審核清單
- 自動化檢查基線一致性
- 報告版本化

Practice Exercise（練習題）
- 基礎練習：撰寫修訂說明（30 分）
- 進階練習：建立基線檢核清單（2 小時）
- 專案練習：自動化基線檢核與提醒（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：修訂流程完整
- 程式碼品質（30%）：檢核腳本（若有）
- 效能優化（20%）：降低錯誤結論風險
- 創新性（10%）：報告治理工具化


## Case #10: 使用 Microsoft .NET Core CLI Container 快速復現測試環境

### Problem Statement（問題陳述）
業務場景：為降低測試環境建置成本，需要快速、可重現的 .NET Core 執行環境；作者選擇官方 CLI 容器映像。  
技術挑戰：跨 OS 一致性、最小化手動安裝、可立即測試。  
影響範圍：顯著縮短準備時間，提高重現性。  
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 容器映像已預裝 .NET CLI。
2. 只需 Docker pull/run 即可開始。
3. 減少 host 異質性。

深層原因：
- 架構層面：容器化能標準化環境。
- 技術層面：映像維護由官方提供。
- 流程層面：將建置時間轉為執行時間。

### Solution Design（解決方案設計）
解決策略：以官方 .NET Core CLI 容器為基礎，透過 docker run 掛載程式碼直接執行測試，確保跨 OS 一致。

### 實施步驟
1. 取得 CLI 容器映像
- 實作細節：docker pull <dotnet-cli-image>
- 所需資源：Docker
- 預估時間：0.2 小時

2. 掛載程式碼與執行
- 實作細節：docker run -v $(pwd):/app -w /app <image> dotnet run
- 所需資源：.NET 專案
- 預估時間：0.2 小時

3. 多平台測試
- 實作細節：同一映像、不同宿主 OS
- 所需資源：Windows/Linux 主機
- 預估時間：0.5 小時

### 關鍵程式碼/設定
```bash
docker pull <dotnet-cli-image>
docker run --rm -v "$PWD:/app" -w /app <dotnet-cli-image> dotnet run -c Release
```

實際案例：作者在 Ubuntu/Boot2Docker 直接使用 CLI 容器執行測試。  
實作環境：Docker Engine + .NET Core CLI 映像。  
實測數據：建置時間趨近於 0，數據可跨 OS 比對（質化）。

Learning Points（學習要點）
核心知識點：
- 容器化帶來的一致性
- 最小化環境差異
- 快速迭代

技能要求：
- 必備技能：Docker 基礎
- 進階技能：映像管理

延伸思考：
- 以多階段 Dockerfile 最小化映像
- 封裝測試與報表
- 以 CI 自動化

Practice Exercise（練習題）
- 基礎練習：以 CLI 容器跑 Hello World（30 分）
- 進階練習：掛載測試程式並輸出結果（2 小時）
- 專案練習：打造專屬測試映像（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：可執行且可比對
- 程式碼品質（30%）：Docker 指令/腳本
- 效能優化（20%）：縮短準備時間
- 創新性（10%）：映像優化


## Case #11: OOM 與 swap 問題的觀測取證：dmesg/console 與日誌

### Problem Statement（問題陳述）
業務場景：測試時偶發錯誤，需快速判斷是否 OOM 或 swap 寫入問題。  
技術挑戰：容器內訊息有限，需查主機內核訊息（console/dmesg）。  
影響範圍：縮短定位時間，避免誤判應用 bug。  
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 內核訊息未被納入觀測流程。
2. 僅看應用輸出無法判斷 OOM Killer。
3. 容器與主機的事件隔離。

深層原因：
- 架構層面：缺乏系統層 observability。
- 技術層面：對 Linux 日誌與 console 用法不熟。
- 流程層面：無標準取證SOP。

### Solution Design（解決方案設計）
解決策略：建立標準化取證命令集合，發生異常立即抓 dmesg、journalctl 與 console（若可達），保存與測試結果名稱關聯。

### 實施步驟
1. 取證命令清單
- 實作細節：dmesg -T、journalctl -k、grep 重要關鍵字
- 所需資源：Linux 指令
- 預估時間：0.2 小時

2. 腳本化
- 實作細節：wrap 成 ./collect-logs.sh
- 所需資源：Shell
- 預估時間：0.5 小時

3. 關聯測試輸出
- 實作細節：以 timestamp/測試案例名存檔
- 所需資源：Shell
- 預估時間：0.2 小時

### 關鍵程式碼/設定
```bash
#!/usr/bin/env bash
TS=$(date +%Y%m%d-%H%M%S)
mkdir -p logs/$TS
dmesg -T > logs/$TS/dmesg.txt
journalctl -k --no-pager > logs/$TS/journal-kernel.txt
grep -i -E 'oom|killed|swap' logs/$TS/* > logs/$TS/highlights.txt
```

實際案例：作者在 console 看到大量 swap 錯誤，輔助判斷 Boot2Docker 不穩。  
實作環境：Linux 主機/VM。  
實測數據：定位時間縮短（質化）。

Learning Points（學習要點）
核心知識點：
- 內核與容器層事件關係
- OOM/swap 錯誤指標
- 取證自動化

技能要求：
- 必備技能：Linux 日誌
- 進階技能：SOP 制定

延伸思考：
- 導入系統監控/告警
- 與測試框架整合
- 建立故障知識庫

Practice Exercise（練習題）
- 基礎練習：用腳本收集一次測試日誌（30 分）
- 進階練習：失敗時自動收集（2 小時）
- 專案練習：對 OOM 事件自動開工單（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：取證資料完整
- 程式碼品質（30%）：腳本健壯
- 效能優化（20%）：縮短定位時間
- 創新性（10%）：與告警串接


## Case #12: 高記憶體工作負載的環境選型：Ubuntu Server vs Boot2Docker

### Problem Statement（問題陳述）
業務場景：需選擇適合高記憶體壓力測試與生產的 Linux 發行版。  
技術挑戰：不同發行版定位不同；Boot2Docker 為快速啟動、RAM 運作，Ubuntu Server 可配置持久儲存與 swap。  
影響範圍：穩定性、回收率與可運維性。  
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. Boot2Docker 設計為輕量測試。
2. Ubuntu Server 適合長時運作與持久化配置。
3. 高記憶體負載需 swap 與穩定 IO。

深層原因：
- 架構層面：選型與負載不匹配。
- 技術層面：持久化與 swap 缺失。
- 流程層面：未先定義選型準則。

### Solution Design（解決方案設計）
解決策略：制定準則：快速體驗選 Boot2Docker、壓測/生產選 Ubuntu Server；同時給出實測數據支撐。

### 實施步驟
1. 明定準則
2. 以實測數據佐證（98.85% vs 88.46%）
3. 文件化並訓練

### 關鍵程式碼/設定
```text
準則文件（無需程式碼）
```

實際案例：作者建議 Boot2Docker 用於測試，正式環境用 Ubuntu。  
實作環境：同上。  
實測數據：Ubuntu 4864/4808MB（98.85%）vs Boot2Docker 832/736MB（88.46%）。

Learning Points（學習要點）
核心知識點：
- 發行版定位與適配
- 以數據支撐選型
- 風險邊界管理

技能要求：
- 必備技能：基礎運維
- 進階技能：SRE 決策方法

延伸思考：
- 其他發行版比較
- 雲端託管差異
- cgroup 與 QoS（延伸）

Practice Exercise（練習題）
- 基礎練習：撰寫選型建議書（30 分）
- 進階練習：納入你們的歷史故障資料（2 小時）
- 專案練習：建立選型決策表單（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：準則清晰
- 程式碼品質（30%）：文件規範
- 效能優化（20%）：風險控制
- 創新性（10%）：可量化指標


## Case #13: 測試資源對齊：磁碟 32GB 與交換空間策略

### Problem Statement（問題陳述）
業務場景：為避免拉取映像與運行時受限，作者額外配置 32GB VHD 給 Docker Engine；同時對齊 swap。  
技術挑戰：磁碟不足會干擾測試（image pull/swap），影響結果與穩定性。  
影響範圍：測試中斷、數據不完整。  
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 映像拉取需要足夠磁碟。
2. swap 需有持久化空間。
3. 預設磁碟空間不足。

深層原因：
- 架構層面：資源預算不足。
- 技術層面：未評估容器儲存需求。
- 流程層面：前置檢核缺失。

### Solution Design（解決方案設計）
解決策略：為測試 VM 提供 32GB 磁碟給 Docker 使用，並配置 4GB swap，作為最小可行資源基線。

### 實施步驟
1. 擴充虛擬磁碟/掛載
2. Docker 資料目錄檢查（/var/lib/docker）
3. 配置 swap（Case #2）

### 關鍵程式碼/設定
```bash
# 檢查磁碟
df -h
# Docker 目錄容量
du -sh /var/lib/docker
```

實際案例：作者在 Boot2Docker/Ubuntu 皆準備額外磁碟使 pull 與 swap 不受限。  
實作環境：VM + Docker。  
實測數據：穩定性提升（質化）。

Learning Points（學習要點）
核心知識點：
- 容器儲存與 swap 需求
- 測試資源基線
- 前置檢核

技能要求：
- 必備技能：系統管理
- 進階技能：容量規劃

延伸思考：
- 分離容器與資料磁碟
- 監控磁碟壓力
- Docker storage driver 影響（延伸）

Practice Exercise（練習題）
- 基礎練習：檢查並報告磁碟/目錄用量（30 分）
- 進階練習：寫前置檢核腳本（2 小時）
- 專案練習：自動擴容流程（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：資源檢核完整
- 程式碼品質（30%）：腳本品質
- 效能優化（20%）：降低中斷
- 創新性（10%）：自動化程度


## Case #14: 在 Docker 內正確觀測記憶體：觸碰頁面並用系統指標驗證

### Problem Statement（問題陳述）
業務場景：避免僅靠應用輸出判讀記憶體，需在容器內用 free/ps 驗證，確保頁面真的映射。  
技術挑戰：容器與主機指標差異、需確保測試攸關指標一致。  
影響範圍：數據可信度。  
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 僅看程式內計數。
2. 未使用系統指標交叉驗證。
3. 延遲配置導致誤判。

深層原因：
- 架構層面：監控視角不足。
- 技術層面：指標理解不足。
- 流程層面：未定義觀測 SOP。

### Solution Design（解決方案設計）
解決策略：在測試程式觸碰頁面後，使用 free、ps 觀測 RSS 與可用記憶體，形成 SOP。

### 實施步驟
1. 在配置後加入 sleep/標記點
2. 執行 free -h、ps -o pid,rss,vsz -p <pid>
3. 記錄並對照測試輸出

### 關鍵程式碼/設定
```bash
free -h
ps -o pid,cmd,rss,vsz -p $(pidof dotnet)
```

實際案例：作者在修正初始化策略後，數據與系統指標一致。  
實作環境：Docker 容器內。  
實測數據：可信度提升（質化）。

Learning Points（學習要點）
核心知識點：
- RSS/VSZ 與 free 指標
- 容器內觀測
- 交叉驗證

技能要求：
- 必備技能：Linux 指令
- 進階技能：監控思維

延伸思考：
- 加入 /proc/meminfo 指標
- 與 cAdvisor/Prometheus 整合
- 統一時間戳

Practice Exercise（練習題）
- 基礎練習：在配置高峰抓取 free/ps（30 分）
- 進階練習：寫觀測小腳本（2 小時）
- 專案練習：整合到自動測試流程（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：指標抓取正確
- 程式碼品質（30%）：腳本可讀性
- 效能優化（20%）：低侵入
- 創新性（10%）：可視化呈現


## Case #15: Ubuntu Server 記憶體管理最佳實務：達成 4864MB/4808MB、98.85%

### Problem Statement（問題陳述）
業務場景：以 Ubuntu Server 作為 Linux 代表環境，需獲得穩定且高回收率的結果，用於決策。  
技術挑戰：需避免虛高、對齊 swap、確保穩定三階段流程。  
影響範圍：作為 Linux 的標竿數據。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 初始有虛高與 swap 不對齊。
2. OOM Killer 偶發。
3. 未交叉驗證系統指標。

深層原因：
- 架構層面：基線建立
- 技術層面：初始化與 swap 調整
- 流程層面：取證與驗證 SOP

### Solution Design（解決方案設計）
解決策略：整合 Case #1/#2/#11 方法，最終在 Ubuntu 穩定達成 4864/4808MB 與 98.85% 回收率，作為推薦基線。

### 實施步驟
1. 亂數初始化避免虛高
2. swapfile 調整為 4GB
3. 建立 OOM 取證並確認穩定完成三階段

### 關鍵程式碼/設定
```text
綜合應用 Case #1、#2、#11 的程式與設定
```

實際案例：作者最終在 Ubuntu 取得最佳與穩定結果。  
實作環境：Ubuntu 15.10 Server + Docker + .NET Core CLI。  
實測數據：
- 改善前：數據虛高或不穩
- 改善後：4864MB/4808MB，98.85%

Learning Points（學習要點）
核心知識點：
- Linux 作為 .NET Core 容器宿主的高可用實務
- 基線與 SOP 的價值
- 指標化的優勢

技能要求：
- 必備技能：Linux/Docker/C#
- 進階技能：SRE 方法

延伸思考：
- 是否可調 GC 模式再微調（如 Server GC）
- 更大 RAM/不同 swap 策略的影響
- 長時壓測輪廓

Practice Exercise（練習題）
- 基礎練習：以 Ubuntu 重現 98%+ 回收率（30 分）
- 進階練習：嘗試不同 blockSize（2 小時）
- 專案練習：加自動重跑 5 次取中位數（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：達成高回收率
- 程式碼品質（30%）：測試穩定
- 效能優化（20%）：初始化/GC 成本
- 創新性（10%）：結果再現性


## Case #16: Boot2Docker 的碎片化表現與風險：832MB/736MB、88.46%

### Problem Statement（問題陳述）
業務場景：評估 Boot2Docker 在記憶體碎片化測試的表現與風險，作為使用邊界的佐證。  
技術挑戰：不穩定與 swap 限制，偶發錯誤；成功時回收率偏低。  
影響範圍：不適合作為生產或容量決策依據。  
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. RAM 運作、缺交換空間。
2. swap 寫入錯誤偶發。
3. 成功時回收率仍偏低。

深層原因：
- 架構層面：設計為「快速啟動」而非「高負載」。
- 技術層面：缺失持久化與 SWAP。
- 流程層面：未劃定使用邊界。

### Solution Design（解決方案設計）
解決策略：將 Boot2Docker 定位為「快速測試/教學」，避免用於容量/穩定性決策；必要時切換至 Ubuntu Server 執行壓測。

### 實施步驟
1. 重現成功樣本並記錄 88.46% 指標
2. 文件化風險與使用邊界
3. 調整團隊默契與 CI 測試環境

### 關鍵程式碼/設定
```text
無需程式碼；著重於環境使用準則
```

實際案例：Boot2Docker 成功結果為 832MB/736MB（88.46%）；多次偶發失敗且有 swap 錯誤訊息。  
實作環境：Boot2Docker。  
實測數據：88.46% 回收率（成功時）。

Learning Points（學習要點）
核心知識點：
- 測試環境使用邊界
- 指標對使用情境的意涵
- 風險管理

技能要求：
- 必備技能：測試方法
- 進階技能：決策治理

延伸思考：
- 若必須使用，是否能外掛持久化磁碟與 swap（高風險）
- 其他輕量發行版比較
- 在教學/POC 場景的價值

Practice Exercise（練習題）
- 基礎練習：在 Boot2Docker 跑一次並記錄結果（30 分）
- 進階練習：撰寫使用邊界文件（2 小時）
- 專案練習：將 CI 上的記憶體壓測切到 Ubuntu（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：數據重現
- 程式碼品質（30%）：文件規範
- 效能優化（20%）：風險降到可控
- 創新性（10%）：替代方案建議


--------------------------------
案例分類

1) 按難度分類
- 入門級（適合初學者）
  - Case #2, #4, #8, #10, #11, #12, #13, #14, #16
- 中級（需要一定基礎）
  - Case #1, #3, #5, #6, #7, #15
- 高級（需要深厚經驗）
  - 無（文章範圍以測試與環境實務為主）

2) 按技術領域分類
- 架構設計類
  - Case #5, #12, #13, #15, #16
- 效能優化類
  - Case #1, #2, #6, #7, #8, #14, #15
- 整合開發類
  - Case #6, #10, #13
- 除錯診斷類
  - Case #3, #4, #11, #14, #16
- 安全防護類
  - 無（本文未聚焦安全）

3) 按學習目標分類
- 概念理解型
  - Case #1, #7, #8, #12, #14
- 技能練習型
  - Case #2, #6, #10, #11, #13
- 問題解決型
  - Case #3, #4, #5, #9, #15, #16
- 創新應用型
  - Case #6, #7（指標與治具設計）


--------------------------------
案例關聯圖（學習路徑建議）

- 建議先學
  - Case #10（用 CLI 容器快速復現環境）
  - Case #13（資源基線對齊：磁碟/交換空間）
  - Case #14（在容器內正確觀測記憶體）

- 關鍵依賴關係
  - Case #1 依賴 Case #14 的觀測方法（先會觀測再能校正虛高）
  - Case #2 是 Case #9、#15 的前提（swap 對齊後才能更正結論並達成高回收率）
  - Case #3 依賴 Case #11（有取證 SOP 才能判定 OOM/Killed）
  - Case #6、#7 互為基礎（治具建立後才能產出回收率指標）
  - Case #5、#12、#16 彼此關聯（Boot2Docker 使用邊界與替代環境）

- 完整學習路徑建議
  1) Case #10 -> #13 -> #14：先能快速建環境、對齊資源並正確觀測
  2) Case #6 -> #7：建立三階段治具與核心指標
  3) Case #1 -> #8：掌握初始化策略，消除虛高/壓縮影響
  4) Case #2 -> #11 -> #3：交換空間對齊、建立取證，再緩解 OOM/Killed
  5) Case #15：在 Ubuntu 達成穩定高回收率，形成標竿
  6) Case #4 -> #5 -> #12 -> #16：理解 Boot2Docker 的限制與邊界，形成選型準則
  7) Case #9：學會在發現基線問題後修正結論與報告治理

循此路徑，學習者將能從環境建立、正確觀測、治具設計到問題診斷與決策治理，完整掌握 .NET Core 在 Linux/Docker 的記憶體測試與實務最佳做法。