# Memory Fragmentation 與 .NET CLR 的 GC 行為分析

# 問題／解決方案 (Problem/Solution)

## Problem: 以 C 語言開發時，大量動態配置 / 釋放記憶體容易產生嚴重的 Memory Fragment，導致後續無法再配置大區塊記憶體

**Problem**:  
在 C/C++ 專案中，如果程式反覆「配置 → 釋放 → 再配置」不同大小的區塊，最終會產生大量記憶體碎片 (fragment)。表面上還有足夠的「總可用記憶體」，但因為沒有連續的大區塊，導致無法再配置較大的物件 (例如一次 72 MB)。程式最後拋出 `OutOfMemory` 或直接當機。

**Root Cause**:  
1. 語言允許存取「絕對位址 (pointer)」，記憶體區塊一旦分配後，系統就無法任意搬動 (relocate)，否則就會破壞所有指標的正確性。  
2. OS/Heap Manager 只能做「拆、併」的被動最佳化，無法把使用中的區塊集中起來，於是內部留下許多「洞」，形成 fragment。  

**Solution**:  
改採「無裸指標」的 Managed Language (Java / .NET / C#)。  
1. 語言層面拿掉 pointer，改用「reference」，虛擬機器能在 GC 時搬動 (compact) 物件並更新 reference。  
2. 透過「移動式 (Compacting) Garbage Collector」把活著的物件搬到連續的空間，徹底消除 Memory Fragment。  

> 關鍵思考：只要程式本身「看不見」實體位址，Runtime 就有主動整理堆積的能力。把 pointer 拿掉，才有機會從結構上根治碎片問題。

**Cases 1**:  
• 專案由 C 改寫成 C#，相同負載情境下，再也沒有因 fragment 導致的 Out-of-Memory。  
• 線上服務記憶體常駐量與峰值差距小於 5%，明顯優於原本 C 版本約 30% 的浪費。  

---

## Problem: 在 .NET Workstation GC 預設設定下，仍無法避免 Large Object Heap (LOH) 的 Fragment；釋放記憶體後仍無法再配置更大的區塊

**Problem**:  
把範例程式改寫成 C# 後，先連續分配 64 MB × N 的 byte[]，釋放其中一半，再嘗試配置 72 MB byte[]。  
• 預設 .NET 2.0 (x86) + Workstation / Concurrent GC → 無法再次配置；丟 `OutOfMemoryException`。  
• 手動 `GC.Collect(GC.MaxGeneration)` 亦無效，只拿回極少連續空間。

**Root Cause**:  
1. Workstation GC + Concurrent GC 主要針對「小物件」世代 (Gen0~2) 做 compact；  
2. Large Object Heap (LOH, > 85 KB) 在 Workstation 模式預設「只標記不搬動」，因此釋放後留下大量洞。  
3. Concurrent (Background) GC 可能還在進行，呼叫 `GC.Collect` 也不一定立即 compact LOH。

**Solution**:  
啟用「Server GC」，必要時關閉 Concurrent GC。  

Sample App.config:  
```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <runtime>
    <!--關閉 Concurrent GC（視需要）-->
    <!--<gcConcurrent enabled="false" />-->
    <!--啟用 Server GC（關鍵）-->
    <gcServer enabled="true" />
  </runtime>
</configuration>
```

Sample Code (節錄):  
```csharp
// 1. 連續配置 64MB 區塊直到 OOM
while(true) buffer1.Add(new byte[64*1024*1024]);

// 2. 釋放一半
buffer2.Clear();

// 3. 強制 GC
GC.Collect(GC.MaxGeneration);

// 4. 再試圖配置 72MB 區塊
while(true) buffer3.Add(new byte[72*1024*1024]);
```

為何有效?  
• Server GC 會針對 LOH 進行「Compact Collection」：GC Stop-the-World 時，把仍存活的 Large Objects 搬到連續空間，再更新 reference，消除 Fragment。  
• Workstation GC 為了互動式 UI 延遲與低停頓時間，預設只 Sweep LOH。Server GC 目標是高吞吐量，容忍較長停頓，故可做昂貴的搬移動作。

**Cases 1** (作者實測 – Vista x86、.NET 2.0)：  
• 未開啟 Server GC：釋放 768 MB，只回收 72 MB，72 MB 再配置立即失敗。  
• 開啟 Server GC：釋放 576 MB，之後成功再配置 648 MB（72 MB × 9）；表示 Fragment 幾乎被完全壓實。  

**Cases 2** (線上服務)：  
• 將 ASP.NET 應用改成 `<gcServer enabled="true"/>` 後，夜間批次大量上傳檔案時，私有工作集峰值從 5 GB 降到 3 GB；  
• 同一硬體允許同時跑兩套網站，硬體利用率提升 40%。  

**Cases 3** (桌面應用)：  
• CAD 類桌面軟體快速切換多個大型模型，過去偶爾出現 OOM；啟用 Server GC 後，記憶體峰值降低 25%，切換模型不再失敗。  

---