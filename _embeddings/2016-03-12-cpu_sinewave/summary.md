# [樂CODE] Microsoft 面試考題: 用 CPU utilization 畫出正弦波

## 摘要提示
- 面試題目: 透過程式碼把 Windows 工作管理員的 CPU 使用率畫成正弦波。  
- Busy/Idle 切片: 每 100 ms 切一段，用 busy waiting + idle 時間拼出目標利用率。  
- 三角函數調整: 把 sin(x) 位移及縮放為 (sin x + 1)/2 以取得 0~1 的負載比例。  
- 多核心干擾: Busy wait 僅能吃滿單核心，需在單核心 VM 或多執行緒分攤。  
- 時間控制手段: 比較 Thread.Sleep 與 SpinWait.SpinUntil 的精確度與飄移量。  
- 改良技巧: 以「Advanced Sleep」與「Advanced SpinUntil」降低 context-switch 誤差。  
- 實驗數據: 噪音 thread 0~10 階段下，Adv_SpinUntil 於準確度與精密度皆最佳。  
- 效能優化: 初始化階段先建 lookup table，執行期僅查表並分離 busy/idle。  
- 延伸玩法: 透過 ASCII Art 建表，成功在管理員畫出 Batman Logo。  
- 開源分享: 完整專案已上傳 GitHub，供有興趣者下載試玩。

## 全文重點
作者在網路上看到「Microsoft 面試—用 CPU 利用率畫正弦波」的討論，激起勝負心後立刻動手以 C# 實作。基本思路是把時間離散化：每 100 ms 為一單位，計算 (sin x + 1)/2 得到 0–1 的比例，再令該時間片中 busy waiting 的長度 = 百分比×100 ms，其餘時間則 idle，便可在系統監控上拼出波形。  
初版程式在多核心機器上飽和度偏低且雜訊明顯，作者改在僅配置 1 core 的 VM 上測試，同時開始研究「如何精確地睡眠與旋轉」。實測顯示 Thread.Sleep(10 ms) 在空載時已可達到約 10 ms，但一旦加入背景雜訊 thread，誤差可高達 31 ms，且飄移範圍大；SpinWait.SpinUntil 雖平均落在 23–26 ms，卻較穩定。  
為改善兩者缺點，作者提出兩個「Advanced」版本：  
1. 以 while(timer.Elapsed<target) Thread.Sleep(0) 方式微調；  
2. 使用 SpinWait.SpinUntil(()=>timer.Elapsed>target) 取消內建 timeout 迴圈，直接以委派控制。  
對四種手段在 0–10 條干擾 thread 下進行 50 次量測，比較平均值（準確度）與標準差（精密度）。結果顯示 Advanced SpinUntil 在八條背景 thread 時仍最貼近 10 ms 且變異最小，因而成為最終實作方案。  
為進一步降低自身干擾，作者把所有耗時計算移到初始化階段，將整個週期的目標值預先寫成 lookup table；執行時只做：1) SpinUntil 進入 idle；2) busy while 填滿剩餘；3) 進入下一片段。調整後波形已趨平滑。  
既然查表即可繪圖，作者索性把來源改為 ASCII Art，讓 CPU 線條描出 Batman Logo；成品效果與官方 Logo 已可相互辨識，證實方法泛用。  
整個過程涵蓋了多執行緒、作業系統排程、硬體計時器、busy waiting 與 HLT 指令等概念，也突顯「理論 vs. 實務」間的差距。文章最後附上 GitHub 位址，並幽默地自問：「這樣算通過 Microsoft 面試了嗎？」

## 段落重點
### 什麼!!! Microsoft 面試考這個?
作者因網友貼文而得知此題，決定挑戰；初版方案以 busy/idle 切片配合 sin 函式，但在多核心與系統雜訊下波形失真嚴重。為排除干擾改在 1-core VM 運行，並重新檢討時間控制及 CPU 飽和策略，理解到精確的「休息」與「忙碌」同樣關鍵。

### 測試精確度用的程式碼:
核心問題轉向「如何準確等待」。作者撰寫測試程式比較 Sleep 與 SpinUntil，在有無噪音 thread 下量測 10 ms 延遲，發現兩者各有缺點；進而設計 Advanced Sleep 與 Advanced SpinUntil 兩種改良版，加上統計分析，確立 Adv_SpinUntil 為最佳選擇。隨後引入查表法、Busy/Idle 分離、降噪順序，最終畫出平滑正弦波，並延伸至 Batman ASCII 圖案；完整程式碼開源分享。