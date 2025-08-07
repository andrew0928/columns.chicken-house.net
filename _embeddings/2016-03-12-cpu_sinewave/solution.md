# [樂CODE] Microsoft 面試考題: 用 CPU utilization 畫出正弦波  

# 問題／解決方案 (Problem/Solution)

## Problem: 無法以 CPU 使用率穩定畫出平滑的正弦波

**Problem**:  
在 Windows 工作管理員的 CPU History 視窗中，想利用程式碼把 CPU 使用率控制成一條漂亮的正弦波。但實際執行後，波形充滿雜訊及毛邊，完全稱不上 “漂亮”。

**Root Cause**:  
1. 測試機為 4C/8T，單純的 busy-wait 只會吃到單一硬體執行緒，理論峰值僅 12.5% → 波形振幅明顯不足。  
2. 背景服務、其他 Process 與 OS Scheduler 造成不可控的負載雜訊。  
3. 多核心排程使每顆核心的曲線彼此干擾。  

**Solution**:  
1. 先在只分配 1 core 的 VM 內執行，排除多核心干擾。  
2. 每 100 ms 為一個 time-slice，slice 內透過  
   busy (wait) time = unit × (sin(t)+1)/2  
   idle time  = unit – busy time  
   方式控制 CPU。  
3. “busy” 採 `while(true);`，“idle” 採 `SpinWait.SpinUntil()`(後續再優化)。  

**Cases 1**:  
• 由實體 8 核轉為 1 核 VM 後，正弦波雜訊明顯降低（附圖第二張），波形已能勉強辨識。  

---

## Problem: `Thread.Sleep()` 與 `SpinWait.SpinUntil()` 造成時間控制不精確

**Problem**:  
即使單核執行，仍發現波形會隨時間飄移，某些 slice 偏高/偏低，導致曲線畸形。

**Root Cause**:  
1. `Thread.Sleep()` 會做 context-switch，喚醒時間高度受 Windows Timer Resolution 與排程影響，精確度不足。  
2. `SpinWait.SpinUntil()` 雖避免 context switch，但內部以反覆呼叫 delegate 判斷 timeout；10 ms 內部可能迴圈 130~150 次，造成額外延遲。  
3. 當背景 threads (noise) 增加時，兩者的「準確度(accuracy)」與「精密度(precision)」都劇烈下降。  

**Solution**:  
提出四種實驗方案並量測：  
a. Sleep( )     b. SpinUntil( )  
c. Advanced Sleep : `while(timer<idle) Thread.Sleep(0);`  
d. Advanced Spin  : `SpinUntil(()=>timer.Elapsed>idle);` (自控 timeout)  

50 次 × noise=0~10 threads，統計平均值(accuracy)及標準差(precision)。  
結果顯示：  
• `Advanced Spin` 在 8T 噪音下，平均最接近 10 ms，標準差最低 ⇒ 同時滿足準確度與精密度。  

**Cases 1**:  
• 準確度曲線圖：noise=7 以後僅 `Advanced Spin` 能維持於理想值附近，其餘方法平均誤差 >10 ms。  
• 精密度圖：noise=8 時 `Advanced Spin` 標準差 <1 ms，`Sleep()` 高達 7 ms。  
採用 `Advanced Spin` 後，CPU 曲線穩定度大幅提升。

---

## Problem: 程式本身運算開銷干擾 CPU 負載，進一步扭曲波形

**Problem**:  
即使換成 `Advanced Spin`，仍發現波形邊緣偶有鋸齒；檢視後發現 slice 內部還在做 `Math.Sin()` 計算與其他邏輯，佔掉應該「Idle」的時間。

**Root Cause**:  
1. 每個 100 ms slice 即時計算三角函數屬 O(1) 但仍消耗數 μs–ms，直接侵蝕 idle window。  
2. 任何非必要的運算都屬「隱藏負載」，難以事後補償。  

**Solution**:  
1. 於初始化階段一次性建立 lookup-table (LUT)  
   `long[] sineTable = GetDataFromSineWave(period,unit);`  
   查表完全 O(1) 而且快。  
2. 執行順序調整：  
   a. 初始化 → 建表 → 預載所有資料。  
   b. 進迴圈：先 Idle (`SpinUntil`) → 再 Busy (`while(true);`)；  
      其餘邏輯全劃歸 Busy，確保 Idle 時段「乾淨」。  
3. 所有 CPU 核心不可用之誤差皆以 Busy 區段吞掉。  

**Cases 1**:  
• 採 LUT + Advanced Spin，最終正弦波完全貼合理想曲線（附第三張圖）。  
• 運行 10 分鐘，最大誤差 <3 % (以 RMS 差值計)。  

**Cases 2** (延伸應用):  
只要換掉 LUT，即可畫任意圖形。示範將 ASCII Batman Logo 轉成負載表，CPU History 成功顯示蝙蝠俠圖樣，證實架構具高度彈性。  

---

## Problem: Busy-Wait 只能吃單核心，無法繪製高振幅曲線

**Problem**:  
在實體 8T 機器直接跑 Busy-Wait 時，CPU 整體最高只到 12.5%，波形幾乎貼近底線。

**Root Cause**:  
Busy-Wait 迴圈固定綁在一條 Hardware Thread，其他 7 條 Thread Scheduler 依舊 Idle → 整體負載被平均稀釋。

**Solution**:  
1. 乾脆將程式移到只分配 1 Core 的 VM，讓所有 Busy 時間都反映在單一核心。  
2. 或者改成在實體機同時開 N 條 Busy-Wait 線程，每線程 Pin 到不同核心 (affinity)，使總負載符合預期。  

**Cases 1**:  
• 單核 VM 方案簡單可靠，馬上讓振幅可達 0–100%。  
• 多線程方案可在 4 核同步畫 4 條正弦波，驗證可用於多核心展示或教學。

