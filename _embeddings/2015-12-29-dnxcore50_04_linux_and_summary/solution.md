# .NET Core 跨平台 #4 ― 記憶體管理大考驗 (Docker on Ubuntu / Boot2Docker)

# 問題／解決方案 (Problem/Solution)

## Problem: 在 Linux 容器中測得「離譜地大的可用記憶體」  
**Problem**:  
執行 .NET Core 記憶體壓力測試 (Docker on Ubuntu / Boot2Docker) 時，¹GB RAM 的 VM 卻顯示可配置 300~700 GB 以上的記憶體，看似「超級充裕」，導致測試數據完全失真。  

**Root Cause**:  
1. Linux Kernel 具備 `SPARSEMEM / sparse file` 機制：  
   未被實際寫入的頁 (page) 只是「邏輯配置」，並未真正佔用實體 RAM／Swap。  
2. 原始測試程式只做 `new byte[size]`，沒有對陣列內容做初始化，因此 Kernel 判定為「未實際使用」，造成巨大但虛假的可用量。  

**Solution**:  
強制對每一頁做 *實體寫入*，迫使 Kernel 真正分配記憶體。最簡單做法是在建立陣列後填入亂數：  
```csharp
static byte[] AllocateBuffer(int size)
{
    byte[] buffer = new byte[size];
    InitBuffer(buffer);          // 關鍵：強制寫入
    return buffer;
}

static void InitBuffer(byte[] buffer)
{
    new Random().NextBytes(buffer);
}
```  
寫入任何值即可（0x00 也行），但用亂數可避免遭到其他最佳化 (compress-zero-page) 影響。  
此解法能讓「邏輯配置 ≒ 實體配置」，測得的記憶體數據才可信。  

**Cases 1**:  
• Ubuntu 15.10 + .NET Core CLI  
  ‑ 修正前：第一階段顯示 712 GB  
  ‑ 修正後：第一階段實際 1 792 MB，碎片回收率 98.2 %  

**Cases 2**:  
• Boot2Docker + .NET Core CLI  
  ‑ 修正前：第一階段顯示 330 GB  
  ‑ 修正後：第一階段實際 832 MB，碎片回收率 88.4 %

---

## Problem: Ubuntu 容器隨機被 OS 直接「Killed」，連 OOM 例外都來不及拋  
**Problem**:  
在 Ubuntu Server 15.10 Docker Container 中跑記憶體測試，有時第三階段還未結束就被 OS 直接 kill，螢幕僅出現 `Killed`，應用程式完全來不及拋 `OutOfMemoryException`。  

**Root Cause**:  
Ubuntu 預設僅建立 1 GB `/swapfile`。當實體 1 GB RAM + 1 GB Swap 均用盡時，Linux OOM-Killer 直接終止最耗記憶體的 Process（此例為 `dotnet`），CLR 沒機會清理或擲回例外。  

**Solution**:  
擴大 Swap 至與 Windows Server 測試一致 (4 GB)，讓 OS 有足夠的虛擬記憶體緩衝。  
```bash
# 調整流程
sudo swapoff /swapfile
sudo dd if=/dev/zero of=/swapfile bs=1M count=4096
sudo mkswap /swapfile
sudo swapon /swapfile
# /etc/fstab 亦須更新確保開機自動掛載
```
增加 Swap 後，Kernel 不再過早啟動 OOM-Killer，CLR 可正常擲出/捕捉例外並完成回收流程。  

**Cases**:  
• Ubuntu 15.10 + .NET Core CLI + 4 GB Swap  
  ‑ 第一階段配置：4 864 MB  
  ‑ 碎片化後仍可配置：4 808 MB  
  ‑ 回收率：98.85 %  
  ‑ 再無隨機 `Killed` 情形

---

## Problem: Boot2Docker 無法穩定完成大記憶體測試，頻繁出現 swap I/O 錯誤  
**Problem**:  
在 Boot2Docker (Tiny Core Linux) 內執行相同測試，常於第一階段就因 swap I/O error 終止，或只能配置數百 MB，結果高度不穩定。  

**Root Cause**:  
1. Boot2Docker 為「完全載入 RAM 的輕量發行版」(~27 MB ISO)：  
   • 原生設計即 **不** 建立持久化磁碟，也預設 **沒有 swap**。  
2. 雖可外掛 32 GB VHD，但核心/初始化腳本對 swap 與 I/O 做了極度保守設定，易觸發 I/O error。  

**Solution**:  
選擇策略：  
A) 僅將 Boot2Docker 用於輕量開發/CI，避免重度記憶體場景；  
B) 若確需大記憶體測試，改採完整發行版 (Ubuntu, CentOS) 或自行重製 Boot2Docker ISO，手動：  
   • 掛載持久化磁碟  
   • 建立 & 開啟 swap  
   • 調整 `vm.swappiness`, `vm.overcommit_memory` 等參數  

**Cases**:  
• 原生 Boot2Docker 測試結果  
  ‑ 第一階段配置：832 MB  
  ‑ 碎片化後：736 MB  
  ‑ 回收率：88.46 %  
  仍遠低於 Ubuntu/Windows，證明其設計並非為高負載環境而來。

---

以上各解決方案使得同一份 .NET Core 記憶體壓力測試程式能在不同 Linux 發行版／容器情境下取得「可比較、可信且穩定」的數據，並揭示：

1) Ubuntu (正確設定 swap) 的記憶體管理效率最佳；  
2) Windows / Linux 之間的 GC 行為尚有差異，後續仍可針對 `Server GC`, `compact GC` 等參數做更深入探討；  
3) Boot2Docker 適合開發測試，而非生產級重度工作負載。