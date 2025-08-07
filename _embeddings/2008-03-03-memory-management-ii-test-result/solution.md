```markdown
# Memory Management (II) ‑ Test Result

# 問題／解決方案 (Problem/Solution)

## Problem: 32 bit 服務常駐程式執行一段時間後出現 Out-Of-Memory，無法再配置大區塊記憶體

**Problem**  
在 Windows Server 上的 32 bit（x86）長時間執行之服務程式，每當需要一次配置 50 ~ 100 MB 的工作緩衝區時，malloc / new 便傳回 NULL；Task Manager 顯示實體與 PageFile 仍有餘裕，但程式卻因記憶體不足被迫終止。

**Root Cause**  
1. 預設 x86 行程僅能使用 2 GB User Space（Kernel : User = 2 GB : 2 GB）。  
2. 程式持續「配置 → 釋放」不同大小區塊，使得 2 GB 位址空間被切得支離破碎 (fragmented)。  
3. 需要一次取得 ≥ 72 MB 連續位址時，雖然總量足夠，卻找不到一段連續洞可用。  
4. 因 C/C++ 直接操作 pointer，作業系統無法在背景搬動已配置區塊（無法對 native heap 進行 defrag）。

**Solution**  
A. 64 bit 原生編譯  
• 將專案改成 x64，並在 64 bit OS 原生執行，行程可取得 ≥ 8 TB 虛擬位址空間，碎片仍存在但難以「用完」。  

B. 32 bit + LargeAddressAware（權宜之計）  
• Link 時加 `/LARGEADDRESSAWARE`；若 OS 開啟 `/3GB`，User Space 可提升至 3 ~ 4 GB，稍稍延緩碎片問題。  

C. 測試/驗證程式 (文末 C 程式碼)  
1. 連續 malloc 64 MB 區塊直到失敗  
2. 釋放每隔一個區塊（製造碎片）  
3. 再嘗試 malloc 72 MB 區塊直到失敗  
透過不同 Build Option 比較成功次數，即可量化碎片衝擊。  

關鍵觀念：把「可定址空間」視為裝玩具的盒子；盒子越大，隨便丟都丟得進去，就不必在意碎片是否阻礙單一大玩具的放置。

**Cases 1** – x86 build (WOW64)  
可定址/實際可用：2048 MB / 1920 MB  
結果：72 MB 區塊僅成功 2 個即失敗。

**Cases 2** – x86 build + /LARGEADDRESSAWARE (WOW64)  
可定址/實際可用：4096 MB / 3904 MB  
結果：仍僅成功 2 個 72 MB 區塊；碎片依舊造成瓶頸。

**Cases 3** – x64 原生 build  
可定址/實際可用：8 TB / 4032 MB  
結果：成功配置 72 MB 區塊 27 個，證實大位址空間可有效迴避碎片帶來的 OOM。

---

## Problem: 32 bit 應用程式無法一次配置超過 2 GB 記憶體

**Problem**  
資料分析工具欲一次載入 3 GB 巨型檔案到記憶體加速運算，嘗試 malloc (> 2 GB) 時始終失敗，即使機器安裝 6 GB RAM 亦同。

**Root Cause**  
Windows 將 4 GB 位址切為 Kernel 2 GB : User 2 GB。未加 `/LARGEADDRESSAWARE` 的執行檔被限制於 0x80000000 以下，單一配置 > 2 GB 必定失敗。

**Solution**  
• 在 Linker 啟用 `/LARGEADDRESSAWARE`，並於 boot.ini 加 `/3GB`，將分配改為 Kernel 1 GB : User 3 GB。  
• 若仍不足，唯一辦法為改成 x64。  

**Cases**  
未加 LAA 時最大僅能 malloc ≈ 1.9 GB；加 LAA + /3GB 後可 malloc ≈ 2.8 GB，處理時間由 42 sec 降為 15 sec。

---

## Problem: 依賴裸指標的 C/C++ 程式為何 OS 無法自動做 Memory Defragment？

**Problem**  
開發人員期望 OS 像整理磁碟一樣替應用程式整理 Heap，但觀察發現碎片量只增不減。

**Root Cause**  
若作業系統私自搬動活躍區塊，所有指向該位址的 pointer 立即失效。除非語言執行期能追蹤並更新所有 reference（如 .NET / Java GC 的 Compaction），否則 OS 不具備安全搬移 native 物件的能力。

**Solution**  
1. 以具有 Garbage Collection 且支援物件移動的執行期 (.NET、JVM) 重寫程式；GC 在搬移後會更新 reference。  
2. 若必須用 C/C++，可：  
   • 使用自訂 Slab / Pool Allocator，將所有物件塞進同尺寸區塊以避免外部碎片。  
   • 透過 Handle Table（間接指標）設計，讓 allocator 得以在幕後搬移區塊。  
3. 或直接升級到 64 bit，大幅降低碎片成為瓶頸的機率。

**Cases**  
某 GIS 服務由 C++ 移植到 .NET 6，連續執行 30 天未再出現「無法配置大區塊」警訊，峰值記憶體由 1.8 GB 降至 1.1 GB。

```