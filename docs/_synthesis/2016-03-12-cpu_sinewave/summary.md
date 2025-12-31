---
layout: synthesis
title: "[樂CODE] Microsoft 面試考題: 用 CPU utilization 畫出正弦波"
synthesis_type: summary
source_post: /2016/03/12/cpu_sinewave/
redirect_from:
  - /2016/03/12/cpu_sinewave/summary/
postid: 2016-03-12-cpu_sinewave
---

# [樂CODE] Microsoft 面試考題: 用 CPU utilization 畫出正弦波

## 摘要提示
- 題目背景: 以控制 CPU 使用率繪出正弦波，源自號稱 Microsoft 面試題目，引發作者動手實作與優化。
- 基本原理: 以時間切片，依 f(x) = (sin x + 1) / 2 計算每片段的目標 CPU 利用率，交替 busy 與 idle。
- 多核心影響: 單執行緒 busy waiting 對多核心只佔部分負載，需限制核心或多執行緒補足。
- Idle 精準度: Thread.Sleep 精度與飄移、SpinWait.SpinUntil 延遲與穩定性各有取捨。
- 實驗比較: 在有/無背景干擾下，比較 Sleep、SpinUntil 與兩種進階改法之準確度與精密度。
- 最佳方案: Advanced SpinUntil（以外部計時判定超時）在準確與穩定性綜合表現最佳。
- 降噪策略: 預先計算（查表）、壓縮運算到 busy 段、保留足夠 idle 時間以減少自我干擾。
- 成果優化: 以 100ms 單位、週期化計時，先 idle 再 busy，波形顯著平滑。
- 擴充玩法: 以 ASCII 圖轉換成對照表，藉 CPU 使用率繪出任意圖案（如 Batman logo）。
- 原始碼提供: 專案 Andrew.CPUDraw 發佈於 GitHub，便於讀者實驗與延伸。

## 全文重點
本文從「用 CPU 使用率畫出正弦波」的面試題切入，作者先以單純的 busy-waiting 與 Sleep 控制時間片嘗試，發現波形雜訊大、外在干擾多。為降低系統噪聲，改在 1 核 VM、精簡 Windows Server Core 上測試，但仍不足以得到漂亮曲線。作者將問題分解：一是多核心下單執行緒只能拉動部分負載；二是如何「精確地 idle」。對策是以多執行緒或限制核心解決第一點；第二點則比較 Thread.Sleep 與 SpinWait.SpinUntil 在精度與飄移上的差異。實測顯示 Sleep 的平均誤差小但飄移大且受硬體影響；SpinUntil 飄移較小但有固定延遲，推測與 delegate 呼叫次數造成的執行耗時有關。

為提升時間控制，作者提出兩種進階作法：Advanced Sleep 以 while+Sleep(0) 做忙等折衷；Advanced SpinUntil 以外部 Stopwatch 判斷條件、取消內建 timeout。以 0~10 個背景干擾執行緒測 50 次，分別從「準確度（平均值靠近目標）」與「精密度（標準差）」評估，結果 Advanced SpinUntil 在高負載環境下綜合表現最佳，其次為 Advanced Sleep、原生 SpinUntil、Sleep。基於穩定性與硬體相依性考量，最終採 Advanced SpinUntil 作為 idle 控制核心。

接著作者針對自體干擾進一步優化：將昂貴運算（sin）在初始化期預先完成，以查表 O(1) 取得每段目標負載；把所有必要運算歸到 busy 區，保障 idle 段淨空；流程上先 idle 至該段目標時間，再以忙迴圈補滿當段。經此調整，CPU 使用率曲線顯著平滑接近理想正弦波。最後作者進一步將「對照表」泛化：不僅可由三角函數生成，也能從 ASCII 圖取得每列第一個像素的位置轉成負載表，進而用 CPU 使用率「畫出」任意圖樣，舉例成功呈現 Batman 標誌。全文於收尾附上 GitHub 專案，供讀者取用與延伸，並以輕鬆語氣自嘲這番「為面試題奮戰」的技術探索。

## 段落重點
### 什麼!!! Microsoft 面試考這個?
作者看到「Microsoft 面試題：用 CPU 使用率畫正弦波」後起念實作。初版以簡單 busy-waiting 與時間片控制實現，但結果雜訊大且不美觀。為減少外在干擾，改在 1 核、精簡 Server Core 的 VM 執行，雖有改善仍不理想。作者意識到，題目不難但要畫得漂亮不易，核心挑戰在「訊號控制的穩定性與精準度」，決定深入調整方法。

### 基本原理與時間片設計
以微積分概念將時間離散化：每 100ms 為一段，依 f(x) = (sin x + 1)/2 計算該段目標 CPU 利用率。具體做法是：一段時間內先 busy 一段（達到 100%），再 idle 一段，使整段平均符合目標百分比。例如目標 70%，就 busy 70ms + idle 30ms。此法理論正確，但實務面臨兩大問題：多核心下單執行緒只能拉高部分總使用率；idle 段如何精準「不打擾」CPU，避免引入新的負載與誤差。

### Idle 控制策略：Sleep vs Spin 的實測
多核心負載問題可靠多執行緒或限制核心解決；難點在 idle 精準度。傳統觀念認為 Thread.Sleep 精度低且喚醒有不確定性，SpinWait 透過 HLT/讓步減少 CPU 占用、理當更穩定。作者重現實驗：在無與有背景干擾時，分別以 Sleep(10ms) 與 SpinUntil(10ms)測量。結果顯示 Sleep 在數值上較接近 10ms，但飄移範圍大、受 OS/硬體影響明顯；SpinUntil 較穩定但有系統性延遲（多落在 23-26ms），推測與內部迭代執行 delegate 造成的固定成本有關。此處也回顧 SpinWait 與 HLT 指令的底層意涵。

### 進階改法與定量評估
為彌補原生 API 侷限，作者提出兩種改良：Advanced Sleep 以 while(timer<idle) Thread.Sleep(0) 忙等折衷；Advanced SpinUntil 以 SpinUntil(() => timer.Elapsed > idle) 外部計時，避免內建 timeout 帶來的額外迴圈成本。以 0~10 個干擾執行緒、各 50 次樣本，從「準確度（平均接近目標）」與「精密度（標準差越小越穩）」比較四法：Advanced SpinUntil 在高負載下綜合最佳，其後依序為 Advanced Sleep、原生 SpinUntil、Sleep。考量可預測性與對硬體時脈的依賴度，最終選擇 Advanced SpinUntil 作為 idle 控制核心。

### 降低自我干擾與最終波形
為讓波形更平滑，作者採三策：1) 昂貴運算（如 sin）移至初始化階段預計算成查表，執行期 O(1) 取值；2) 所有額外運算都歸入 busy 段，最大化 idle 段的淨空；3) 每單位步驟先 idle 到既定時間點，再以忙迴圈補滿剩餘時間。實作上以 Stopwatch 對齊時間片，計算當前 step、offset 與該步驟的 idle_until、busy_until，先 SpinUntil 超過 idle_until，再 while 迴圈忙到 busy_until。經此改造，CPU 使用率的正弦波顯著平滑，外觀接近理想曲線。

### 查表泛化：用 CPU 畫任意圖
既然查表不必限定來源為三角函數，作者將資料源改成 ASCII 圖的字串陣列：逐列掃描首個‘X’位置，換算成每步的負載值，並沿用同一繪製主迴圈，即可用 CPU 使用率「畫圖」。範例以 Batman 標誌產生對照表，實測出的 CPU 曲線外觀與原圖相當貼近，證實方法可泛化為任意圖樣繪製。最後提供 GitHub 專案 Andrew.CPUDraw 供讀者下載試玩，並以輕鬆語氣為這段從面試題延伸而來的工程實驗畫下句點。

### 測試精確度用的程式碼:
文中附上量測 Sleep 與 SpinUntil 在 10ms idle 的小程式：建立多個背景 busy thread 製造干擾，使用 Stopwatch 量測實際耗時，分別記錄 Sleep(idle) 與 SpinUntil(delegate, idle) 的表現，並擴充出 Advanced Sleep 與 Advanced SpinUntil 兩種實作。這些實測數據支撐後續對準確度與精密度的分析與結論。

## 資訊整理

### 知識架構圖
1. 前置知識：學習本主題前需要掌握什麼？
- 三角函數與 sin 波形的基本概念（振幅、位移、週期）
- 作業系統排程與 CPU 使用率的意義
- 多執行緒基礎（busy waiting、context switch、spin/yield）
- .NET/C# 基本能力（Thread、SpinWait、Thread.Sleep、Stopwatch）
- 計時精度/準確度與量測方法（平均值、標準差）

2. 核心概念：本文的 3-5 個核心概念及其關係
- CPU 利用率塑形：以短時間片控制忙/閒比例，讓利用率近似 f(t)= (sin t + 1)/2
- 計時/等待策略：Sleep 與 SpinWait（含 Advanced 變體）的準確度與精密度取捨
- 雜訊與隔離：背景負載、核心數對測量與控制的干擾，單核心/VM 降噪
- 前置計算與查表：將昂貴運算搬到初始化，執行期查表 O(1) 降低干擾
- 任意波形生成：以字元圖或資料表取代三角函數，產生自定圖形的 CPU 波形

3. 技術依賴：相關技術之間的依賴關係
- Stopwatch 精準量測 → 驅動時間片切割與忙/閒邏輯
- SpinWait/Thread.Sleep → 實作「閒」的策略，影響準確度/精密度
- 多執行緒/核心拓撲 → 決定 busy waiting 對總體 CPU 利用率的影響
- 前置計算（sin 或 bitmap -> lookup table）→ 降低執行期負載 → 改善波形品質
- OS/硬體計時器精度 → 影響 Sleep 精度與飄移；Spin 減少排程不確定性

4. 應用場景：適用於哪些實際場景？
- 面試/教學：作業系統排程、計時精度、忙等/閒等策略之展示
- 效能實驗：不同等待策略在不同負載下的準確度/穩定性比較
- 壓測/合成負載：用 CPU 波形產生器模擬特定利用率圖樣
- 視覺化概念驗證：用 CPU 利用率「畫圖」展示任意波形（如 logo、文字）

### 學習路徑建議
1. 入門者路徑：零基礎如何開始？
- 了解 sin 波與 f(x) = (sin x + 1)/2 的位移/縮放意義
- 認識 CPU 利用率與時間片的概念，嘗試用固定比率的忙/閒產生 50% 利用率
- 練習 C# Stopwatch、Thread.Sleep、SpinWait 的基本使用
- 在單核心環境（VM）中觀察最小雜訊下的結果

2. 進階者路徑：已有基礎如何深化？
- 比較 Sleep vs SpinUntil 的誤差、飄移、標準差（收集樣本並統計）
- 實作 Advanced Sleep（Sleep(0) busy wait）與 Advanced SpinUntil（自控 timeout）
- 引入背景干擾（noise threads）並量測不同負載下的穩定性
- 將 sin 計算移至初始化，改用查表；比較波形品質提升幅度

3. 實戰路徑：如何應用到實際專案？
- 封裝「時間片+忙/閒控制」為策略介面，替換不同等待策略
- 實作資料來源抽換：sin、外部資料、字元圖，統一輸出 lookup table
- 加入監控與統計模組（平均值、標準差、偏差）做自動化品質評估
- 延伸為壓測工具：可配置週期、幅度、載入圖樣、核心綁定等參數

### 關鍵要點清單
- CPU 利用率塑形：以短時間片內的忙/閒比例控制瞬時利用率，近似目標波形 (優先級: 高)
- 正弦波位移縮放：f(x) = (sin x + 1)/2 將 [-1,1] 映至 [0,1] 便於映射利用率 (優先級: 高)
- 時間片長度選擇：如 100ms 影響解析度與控制精度，需在顯示平滑與抖動間取捨 (優先級: 高)
- Busy waiting 的局限：單執行緒只吃到單核心，總體 CPU 百分比受核心數影響 (優先級: 中)
- 單核心隔離：用 1-core VM 或綁定核心降低背景干擾，提升可控性 (優先級: 中)
- Sleep 精度與飄移：受硬體/OS 計時影響，平均誤差小但飄移較大 (優先級: 中)
- SpinWait 行為：降低 context switch 不確定性，穩定性較佳但絕對誤差可能偏大 (優先級: 高)
- Advanced SpinUntil：用外部 Stopwatch 控制條件，改善精度與穩定性（本文最佳） (優先級: 高)
- Advanced Sleep：用 while+Sleep(0) 折衷，減少切換成本但穩定性次於 Adv Spin (優先級: 中)
- 前置計算與查表：把 sin/圖形轉 lookup table，執行期 O(1) 取值降噪 (優先級: 高)
- 計算歸類：把非必要運算移到 BUSY 段，確保 IDLE 段足夠「乾淨」 (優先級: 高)
- 準確度 vs 精密度：以平均誤差與標準差雙指標評估策略表現 (優先級: 中)
- 背景雜訊測試：逐步增加 noise threads，觀察飽和點（例如 4c/8t 在 7-8 開始惡化） (優先級: 中)
- 任意波形/圖形：以字元圖產生 lookup table，可「用 CPU」畫出 logo/圖案 (優先級: 低)
- 量測工具鏈：Stopwatch、統計（平均/標準差）、可視化是驗證品質的基礎 (優先級: 中)