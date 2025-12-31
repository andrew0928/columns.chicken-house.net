---
layout: synthesis
title: "Canon Raw Codec + WPF #2, ThreadPool"
synthesis_type: faq
source_post: /2007/12/12/canon-raw-codec-wpf-2-threadpool/
redirect_from:
  - /2007/12/12/canon-raw-codec-wpf-2-threadpool/faq/
postid: 2007-12-12-canon-raw-codec-wpf-2-threadpool
---

# Canon Raw Codec + WPF #2, ThreadPool

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 Canon RAW Codec？
- A簡: Canon RAW Codec 是用來解碼 Canon 相機 RAW 檔（如.CR2）的編解碼器，供應用程式讀取與轉換影像。
- A詳: Canon RAW Codec 是由 Canon 提供的解碼元件，負責將相機專有的 RAW 格式（如 CR2）轉換為可見或可處理的影像資料。RAW 含有感光元件的未壓縮或少量處理數據，保留高動態範圍與後製空間。應用場景包括相片後製、批次轉檔、縮圖與預覽。本文觀察到該 codec 的解碼效能在多執行緒下不易線性擴充，對 CPU 利用率貢獻有限，因此需特別規劃工作排程與執行緒使用策略。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, B-Q20, C-Q3

A-Q2: 什麼是 WPF？為何影響影像工具的相容性？
- A簡: WPF 是 Windows 圖形框架，與 GDI+ 架構不同，造成舊影像工具在 Vista 上相容性問題。
- A詳: Windows Presentation Foundation（WPF）是基於向量與硬體加速的 UI 框架，取代傳統 GDI/GDI+ 的許多用途。由於圖形管線、資源管理與控制項模型不同，Windows XP 時代的影像 PowerToys（如 Image Resizer）在 Vista/WPF 環境下無法直接運作。這迫使開發者在新平台上重建批次影像處理工具，並處理 UI 執行緒與背景工作協同、影像解碼與編碼等跨層次問題。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q24, C-Q5, D-Q7

A-Q3: 什麼是 .NET ThreadPool？
- A簡: .NET ThreadPool 提供共用工作執行緒與工作佇列，簡化非同步工作排程與執行。
- A詳: .NET ThreadPool 是 CLR 提供的共用執行緒池，開發者可用 QueueUserWorkItem（或 Task/TPL）提交工作，由池內工作執行緒自動執行。它自動管理執行緒數量與生命週期，適合一般背景工作。限制在於無法細緻設定每個工作或執行緒的優先權、無法輕易建立多組獨立池，也缺乏直接、簡易的「等待全部完成」API（需透過 WaitHandle 等機制），因此在本案例的精準排程與 UI 響應控制上不夠用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q19, B-Q1, C-Q1

A-Q4: 什麼是 SimpleThreadPool（自訂 ThreadPool）？
- A簡: 為滿足固定執行緒數、可設定優先權、多池與易於等待完成而自製的輕量執行緒池。
- A詳: SimpleThreadPool 是作者為解決內建 ThreadPool 無法設定優先權、難以做多池隔離與等待完成等需求而實作的簡化版執行緒池。它支援：固定執行緒數（避免過多上下文切換）、可設定 ThreadPriority（降低對 UI thread 干擾）、可建立多組池（RAW 與 JPEG 分流）、提供 StartPool/QueueWorkItem/EndPool 等介面，易於掌控生命週期。此設計讓「慢而不可平行的 RAW 解碼」與「快而可平行的 JPEG 編碼/縮圖」能協同運作、提升整體吞吐與 UI 流暢。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q3, C-Q2

A-Q5: 為什麼需要自訂 ThreadPool？
- A簡: 因為需控制優先權、多池隔離、固定執行緒數與簡易等待，內建 ThreadPool 難以滿足。
- A詳: 本案例的核心需求包含：1) RAW 解碼任務需高優先權但限單執行緒；2) JPEG 任務可多執行緒並以較低優先權填滿剩餘 CPU；3) UI thread 必須保持流暢；4) 需要在流程末端等待所有工作完成。內建 ThreadPool 不提供 per-thread 優先權設定，也不易建立多個相互隔離的池，等待所有工作完成亦需繞 WaitHandle。自訂池能精準落實「一慢多快」的排程策略，結果顯示從 110 秒降至 90 秒，且 UI 更為順暢。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q19, B-Q5, D-Q3

A-Q6: 什麼是 CPU-bound 工作？為何影像轉檔屬於此類？
- A簡: CPU-bound 受限於 CPU 計算，影像解碼/編碼常屬此類，需善用多核心與排程。
- A詳: CPU-bound 指主要瓶頸在 CPU 計算而非 I/O（例如磁碟或網路）。影像解碼、縮圖與 JPEG 編碼通常涉及大量像素運算與壓縮演算法，典型屬 CPU-bound。這類工作若無法平行化（如某些 RAW 解碼器），即使開多執行緒也難以提高 CPU 利用率；反之若可拆分（如多張 JPEG 縮圖），便能藉由多執行緒提升吞吐。理解 CPU-bound 的特性，有助於採用「限制慢任務的併發、放大快任務的併發」的策略。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q13, B-Q21, D-Q2

A-Q7: Canon RAW 解碼與 JPEG 任務的差異是什麼？
- A簡: RAW 解碼慢且不易平行；JPEG 任務短、可並行，適合填補 CPU 空檔。
- A詳: 觀察顯示 Canon RAW 解碼（CR2→影像）需要較長時間，且即使多開執行緒，CPU 使用率仍停在約 50-60%，顯示其內部不可平行或有序列化瓶頸。相對地，JPEG 解碼/編碼與縮圖工作顆粒小、獨立性高，適合以多執行緒平行處理，能有效利用剩餘 CPU。據此，最佳策略是：限制 RAW 併發（如 1 執行緒，較高優先權），同時以多執行緒較低優先權執行 JPEG 任務，達到吞吐與回應性的平衡。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, B-Q21, C-Q4

A-Q8: 為什麼多開執行緒無法讓 Canon RAW 解碼更快？
- A簡: 因 RAW 解碼器內部非平行設計或受限鎖與序列化，難以隨執行緒數擴充。
- A詳: 當多開執行緒處理 RAW 檔時，CPU 利用率僅約 60%，說明瓶頸非在可平行的計算，而可能在內部序列化鎖、I/O 排他、或演算法本身的單線程設計。此時增加執行緒只造成上下文切換與競爭，反而拉長單張處理時間。正確做法是將 RAW 解碼控制在少量併發（甚至 1），並用可平行的 JPEG 任務消化剩餘資源，以改善整體時間與 UI 體驗。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q13, D-Q2, C-Q3

A-Q9: 什麼是執行緒優先順序（ThreadPriority）？為何重要？
- A簡: ThreadPriority 決定 OS 調度傾向。調低工作執行緒可保護 UI；提升關鍵任務可縮短瓶頸。
- A詳: ThreadPriority 影響排程器如何分配 CPU 時間片。對 CPU-bound 任務，調低工作執行緒優先權（如 BelowNormal/Lowest）能減少對 UI thread 的干擾，維持介面流暢；對關鍵瓶頸（如 RAW 解碼），略高於其他工作可確保其持續推進，避免系統被大量短任務飽和。自訂 ThreadPool 支援設定優先權，是本案例能同時提升整體時間與使用者體驗的關鍵。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q4, C-Q7, D-Q9

A-Q10: 為什麼要使用多組 ThreadPool？
- A簡: 以多池隔離不同任務特性，分別設定執行緒數與優先權，達到最佳排程。
- A詳: RAW 與 JPEG 任務有截然不同的行為（慢且不可平行 vs 短且可平行）。使用多組 ThreadPool 可對它們分別設定：RAW 池僅 1 執行緒、較高優先權；JPEG 池可 2-4 執行緒、較低優先權。這種隔離避免兩者互相擠壓資源，讓瓶頸任務穩定推進，同時用短任務填滿空檔，提高 CPU 整體利用率並維持 UI 回應。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q2, D-Q3

A-Q11: 為什麼固定執行緒數量通常較好？
- A簡: 過多執行緒增加切換與競爭開銷；固定數量易控資源與回應性。
- A詳: CPU-bound 場景下，執行緒數大於核心數太多，會造成上下文切換、快取失效與鎖競爭，反而降低效能。固定可控的執行緒數（如依核心數設定）能充分利用硬體、維持穩定延遲，並避免壓垮 UI thread。本文自訂池採固定數量設計，RAW 池 1 執行緒、JPEG 池最多 4 執行緒，於雙核/四核皆表現合理。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q12, C-Q8, D-Q3

A-Q12: 什麼是 UI Thread？為何要保護它的流暢性？
- A簡: UI thread 執行畫面更新與互動。若被 CPU 工作壓制，介面會卡頓與無回應。
- A詳: 在 WPF/WinForms，UI thread 負責處理使用者輸入、排版、繪製與資料繫結。如果 CPU-bound 背景執行緒與它競爭激烈，且優先權過高，UI 可能無法及時取得時間片，導致進度條與預覽影像不更新甚至「未回應」。因此需：降低背景執行緒優先權、將影像處理放入背景池、以 Dispatcher 將 UI 更新切回 UI thread、並避免過度頻繁的 UI 更新。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, C-Q5, D-Q1

A-Q13: 什麼是 WaitHandle？為何不便於等待 ThreadPool 工作？
- A簡: WaitHandle 用於同步等待；搭配 ThreadPool 需自行設計，較繁瑣難維護。
- A詳: WaitHandle（如 AutoResetEvent/ManualResetEvent）可用於等待事件或多個工作完成。在內建 ThreadPool 中，若要等待一批工作收尾，需為每個工作設置句柄並用 WaitAll/WaitAny 之類方法同步，架構與錯誤處理更複雜。自訂 ThreadPool 直接提供 EndPool 等 API，於內部管理計數與同步，簡化使用面與降低錯誤風險。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, C-Q6, D-Q6

A-Q14: 什麼是 QueueWorkItem 與 WaitCallback？
- A簡: QueueWorkItem 將工作排入池；WaitCallback 是標準委派簽章，接受 state 參數。
- A詳: 在 .NET 傳統模型中，QueueUserWorkItem/QueueWorkItem 接受一個 WaitCallback 委派與可選 state 物件。執行緒池工作者取出後呼叫該委派，讓你在背景執行任務。自訂 SimpleThreadPool 比照此介面，讓既有程式碼可低成本切換，並加入 StartPool/EndPool 與優先權設定，維持 API 親和力與可維護性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, C-Q2, B-Q2

A-Q15: 什麼是 HD Photo（Windows Media Photo）的「小圖快顯」特性？
- A簡: HD Photo 支援按目標尺寸解碼或漸進式呈現，網路/大圖也能快速預覽小圖。
- A詳: HD Photo（後更名為 JPEG XR）設計允許以較低解析度子採樣或漸進式解碼，快速產生縮圖。文中觀察：CR2→原尺寸 JPEG 約 60 秒，但 CR2→800×600 僅約 5 秒，推測 decode 階段就針對目標尺寸做最佳化。這種特性非常適合批次縮圖與網路預覽，顯著降低等待時間與資源消耗。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, D-Q5, C-Q9

A-Q16: 為什麼縮成小尺寸比輸出原尺寸快很多？
- A簡: 因為解碼器可在解碼階段就按目標尺寸抽取/縮放，少做全像素運算。
- A詳: 若解碼器支援子採樣或目標尺寸解碼，生成小圖不需完整展開原始高解析像素，也可避免後段昂貴的縮放與高品質重採樣。文中數據顯示小圖只需 5 秒，明顯驗證了「解碼即縮放」或類似設計。對批次處理而言，優先採用小尺寸管線能提升整體吞吐、降低記憶體壓力與 I/O。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q9, D-Q5, C-Q9

A-Q17: 什麼是「慢任務優先、快任務填充」的排程策略？
- A簡: 先確保瓶頸任務（RAW）穩定推進，再用可平行短任務（JPEG）填滿剩餘 CPU。
- A詳: 當系統包含一類慢且不可平行的任務（RAW 解碼）與一類快且可平行任務（JPEG 編/解碼），若將慢任務設為較高優先權、限制其併發為 1，並用多執行緒執行快任務，就能讓 CPU 使用率在 80-100% 間平穩波動，縮短總工期並維持 UI 回應。此策略在本文中將總時間自 110 秒降至 90 秒，且預覽能即時顯示。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q10, C-Q4

A-Q18: CPU 使用率曲線面積與總運算量的關係是什麼？
- A簡: CPU 使用率曲線下的積分近似總計算量；平滑高利用率可縮短完工時間。
- A詳: 若忽略 I/O 等因素，CPU 使用率 vs. 時間的曲線下面積對應總運算量。若一段時間維持低於可用峰值（如 50-60%），代表資源閒置，完工時間被拉長。透過適當排程讓使用率接近且穩定於高水位（但不壓死 UI），可縮短總工時。本文透過多池與優先權控制，將斷崖式的 100% 段落拉平，整體完工更快。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, D-Q2, C-Q10

A-Q19: 內建 ThreadPool 與 SimpleThreadPool 的差異是什麼？
- A簡: 內建池自動化但難控；自訂池可控優先權、多池與等待完成，更適合精準排程。
- A詳: 內建 ThreadPool 擅長一般非同步，提供自動伸縮與低使用門檻；但缺少 per-thread 優先權、多池隔離、簡單 Wait-all 的 API。SimpleThreadPool 則提供固定執行緒數、可設定優先權、Start/End、與易用的 QueueWorkItem；特別適合需要控制 CPU 佔用、保護 UI、與協同不同工作型態的場景。本文的 20 秒縮短與更佳體驗，主要來自這些可控性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q2, C-Q2

A-Q20: 為什麼要做多核心最佳化？
- A簡: 多核心只有在工作可平行且排程得當時才有價值；否則資源會被浪費。
- A詳: 雙核/四核 CPU 若未妥善併行，常見現象是 CPU 使用率長期低落（如 50-60%），反映出瓶頸不可平行或排程不當。經由任務拆分（顆粒度合理）、優先權控制與多池隔離，將可平行工作平展至多核心，讓不可平行瓶頸穩定推進，才能把硬體潛力兌現。本文在雙核環境透過此法獲得實質時間與體驗提升。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q12, C-Q4, D-Q2

A-Q21: ThreadPool 與平行程式庫（Parallel Extensions/TPL）差在哪？
- A簡: ThreadPool 管理執行緒；TPL 管理「工作/資料平行」與排程，更聰明有效率。
- A詳: ThreadPool 重點在工作排入與執行緒供應；TPL/Parallel Extensions（後續發展為 TPL/PLINQ）則提供平行化控制流、工作分割、負載均衡與工作竊取等高階機制，更適合平行化迴圈與資料處理。本文提到當時尚在 Community Preview，故未採用。概念上，TPL 通常比手動池更能挖掘平行性，但在需要細緻優先權與多池隔離時，自訂池仍有價值。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q19, C-Q1, D-Q3

A-Q22: 批次縮圖工具的核心價值是什麼？
- A簡: 以最少操作快速產出縮圖，兼顧效能、品質與使用者體驗（UI 流暢）。
- A詳: 批次縮圖工具旨在讓使用者選取多張影像後，快速產生目標尺寸或品質的輸出。核心價值包括：1) 效能與吞吐（時間縮短、CPU 利用率高）；2) 輸出品質（JPEG 品質 80-90% 等）；3) 使用者體驗（進度回報、預覽快速顯示、UI 不凍結）；4) 相容性（不同來源 RAW/JPEG）。本文透過自訂排程與多池設計，兼顧這三者。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q9, D-Q1, A-Q15

A-Q23: 本案例中 WinForms 與 WPF 的關係是什麼？
- A簡: UI 可用 WinForms/WPF；關鍵在背景工作排程與 UI thread 的協同。
- A詳: 文章提到「會寫 WinForms 拉兩下就好」，但核心挑戰不在 UI 技術本身而在背景影像處理的排程與 UI 響應。無論使用 WinForms 或 WPF，原則相同：將 CPU-bound 任務移至背景池、設定優先權以保護 UI、以 Dispatcher/Invoke 將 UI 更新回主執行緒、控制更新頻率。WPF 的圖形管線與 XP PowerToys 相容性議題，促成重寫工具。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, C-Q5, D-Q1

A-Q24: GDI+ 遷移到 WPF 的痛點是什麼？
- A簡: 圖形管線差異導致舊工具無法沿用；需重寫並處理新平台執行緒與效能議題。
- A詳: XP 時代的 PowerToys 依賴 GDI+；Vista/WPF 採用不同的 UI 與繪圖架構，導致舊工具無法直接運作。開發者需重建流程：影像載入/解碼、縮圖/編碼、UI 更新/Dispatcher，並重新面對執行緒、優先權、與資源管理等議題。本文即是在 WPF 生態下以自訂 ThreadPool 重新打造批次縮圖的實務經驗。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, C-Q5, D-Q7

A-Q25: 為何 UI 更新要避免被工作執行緒干擾？
- A簡: 背景執行緒若搶占 CPU，UI 會延遲或停滯；需降優先權與正確封送回 UI。
- A詳: 影像處理是重 CPU 負載；若背景執行緒與 UI 用同等或更高優先權，UI 可能長期排不到時間片，造成進度列動但預覽不出現。最佳實踐：背景執行緒用 BelowNormal/Lowest；UI 更新使用 Dispatcher.BeginInvoke（避免封鎖）；降低更新頻率（合批、節流）；分離慢/快任務到不同池，保證瓶頸推進且 UI 流暢。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q7, C-Q5, D-Q1

### Q&A 類別 B: 技術原理類

B-Q1: .NET 內建 ThreadPool 如何運作？限制為何？
- A簡: 內建池以共用執行緒處理排入工作，動態調節數量；難以控優先權、多池、與簡易等待。
- A詳: 技術原理說明：ThreadPool 維持工作佇列與工作執行緒群，動態伸縮以回應負載。關鍵步驟或流程：工作以 QueueUserWorkItem 排入；池從佇列取出執行；系統根據堵塞/CPU 利用率調整執行緒。核心組件介紹：工作佇列、工作執行緒、全域池。限制：無 per-thread 優先權設定、難以做多池隔離、等待全部完成需自行以 WaitHandle 設計，對本案例精準排程與 UI 友善不足。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, A-Q19, D-Q6

B-Q2: SimpleThreadPool 的架構包含哪些元件？
- A簡: 包含固定數量工作執行緒、工作佇列、啟停控制、計數與同步，以及優先權設定。
- A詳: 技術原理說明：SimpleThreadPool 建置時指定執行緒數與 ThreadPriority；StartPool 產生工作執行緒，迴圈取佇列工作執行。關鍵步驟或流程：1) 建立佇列（執行緒安全）；2) StartPool 啟動；3) QueueWorkItem 排入；4) 工作者取出執行；5) EndPool 等待佇列清空與執行緒收尾。核心組件介紹：佇列（如 ConcurrentQueue/自製鎖保護）、工作者執行緒、同步事件（喚醒）、計數器（追蹤未完成工作）、優先權設定 API。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, C-Q1, C-Q6

B-Q3: SimpleThreadPool 的執行流程為何？
- A簡: 啟動池→排入工作→工作者迴圈取出執行→更新計數→待空佇列→收尾。
- A詳: 技術原理說明：每個工作者執行緒在啟動後進入等待/取件迴圈，收到新工作或終止信號時喚醒。關鍵步驟或流程：1) StartPool 建立 N 執行緒；2) QueueWorkItem 將 (delegate,state) 入佇列並發出通知；3) 工作者取出、執行 delegate(state)；4) 完成後遞減未完成數；5) EndPool 設定終止旗標並等待未完成為 0，然後 Join 執行緒。核心組件介紹：終止旗標、未完成計數、喚醒事件、鎖與佇列結構。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q1, C-Q6, A-Q14

B-Q4: 執行緒優先權如何影響排程？
- A簡: 較高優先權較易取得時間片；較低可讓位於 UI。需謹慎避免飢餓與反直覺效應。
- A詳: 技術原理說明：Windows 排程器以優先權階層與動態調整分配 CPU。關鍵步驟或流程：設定 Thread.Priority 後，排程器在同一核心上偏好選擇較高優先緒。核心組件介紹：ThreadPriority 列舉（Highest→Lowest）、UI thread 通常 Normal。實務上將 RAW 池設為略高（BelowNormal/Normal）、JPEG 池更低（Lowest/BelowNormal），可確保瓶頸推進與 UI 流暢；避免設過高導致 UI 飢餓或系統互動性降低。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, C-Q7, D-Q9

B-Q5: 兩個 ThreadPool 協同的排程機制是什麼？
- A簡: RAW 池（1執行緒、高優先）負責慢任務；JPEG 池（多執行緒、低優先）填滿剩餘 CPU。
- A詳: 技術原理說明：以多池隔離不同負載，避免互相干擾。關鍵步驟或流程：1) 建立 RAW 池（1 thread, higher prio）；2) 建立 JPEG 池（2-4 threads, lower prio）；3) 當 RAW 在跑時，JPEG 併行利用剩餘 CPU；4) RAW 完成後，JPEG 清空尾端任務。核心組件介紹：兩個獨立佇列與工作者群、優先權設定、EndPool 同步。此機制的效果是將 CPU 使用率拉近飽和且維持 UI 響應。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, C-Q2, D-Q2

B-Q6: RAW 解碼與 JPEG 任務併行的資料流如何設計？
- A簡: RAW 解碼先產生中介影像；JPEG 任務並行對多張影像進行縮放/編碼輸出。
- A詳: 技術原理說明：將工作拆為「慢→快」兩類。關鍵步驟或流程：1) RAW 池負責解碼 CR2→位圖（或指定尺寸）；2) 每當一張 RAW 解完，將對應 JPEG 輸出任務（縮圖、編碼）排入 JPEG 池；3) 同時處理原生 JPEG 的縮圖任務；4) 每張完成後觸發 UI 更新（Dispatcher）。核心組件介紹：中介資料結構（位圖/路徑）、跨池任務轉交、UI 更新管線。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, C-Q4, C-Q9

B-Q7: WPF UI 響應如何與背景工作協同？
- A簡: 以背景執行緒處理重工作，用 Dispatcher 在 UI thread 更新；並調低背景優先權。
- A詳: 技術原理說明：WPF 要求 UI 更新在 Dispatcher 所屬的 UI thread 執行。關鍵步驟或流程：1) 背景池執行影像處理；2) 完成後以 Dispatcher.BeginInvoke 將縮圖、進度更新封送回 UI；3) 控制更新頻率避免 UI 過載；4) 背景執行緒優先權調低。核心組件介紹：Dispatcher、SynchronizationContext、ThreadPriority。此協同可避免「進度動但預覽不出來」的用戶體驗問題。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, C-Q5, D-Q1

B-Q8: 如何設計「等待所有工作完成」的機制？
- A簡: 以未完成工作計數與事件同步，在 EndPool 阻塞直到佇列清空且工作執行完畢。
- A詳: 技術原理說明：採用計數器追蹤排入與完成數量，搭配事件在歸零時訊號化。關鍵步驟或流程：1) QueueWorkItem 時未完成++；2) 工作結束時未完成--；3) EndPool 設終止旗標並等待未完成=0；4) Join 工作者執行緒；5) 釋放資源。核心組件介紹：Interlocked 計數、ManualResetEvent/Condition、終止旗標。此設計比逐個 WaitHandle 管理更簡潔可靠。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, C-Q6, D-Q6

B-Q9: 小尺寸輸出為何在解碼階段就變快？
- A簡: 若解碼器支援子採樣/目標尺寸解碼，可少展開像素與縮放運算，大幅加速。
- A詳: 技術原理說明：部分影像格式/codec 支援以較低解析度層級讀取或子採樣，直接解出接近目標尺寸的資料。關鍵步驟或流程：1) 根據目標尺寸選擇解碼層級；2) 減少全尺寸展開與後段縮放；3) 快速輸出縮圖。核心組件介紹：影像金字塔/子採樣、解碼參數。本文數據顯示 CR2→800×600 僅 5 秒，支持此原理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, A-Q16, D-Q5

B-Q10: CPU 使用率與完工時間的關係機制是什麼？
- A簡: 在固定總運算量下，使用率越接近且穩定高水位，總時間越短；但需保護 UI。
- A詳: 技術原理說明：總運算量近似使用率曲線面積；長時間低使用率意味閒置。關鍵步驟或流程：1) 分類任務可否平行；2) 調整優先權與執行緒數，盡量填滿空檔；3) 監控避免壓死 UI；4) 反覆調校達到平穩高水位。核心組件介紹：使用率監測、池參數（thread/prio）、UI 事件。本文多池策略將 110 秒降至 90 秒即為示例。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q18, C-Q10, D-Q2

B-Q11: 工作佇列與同步如何設計才穩定？
- A簡: 使用執行緒安全佇列、條件變數/事件喚醒、終止旗標與計數器避免死鎖/漏件。
- A詳: 技術原理說明：生產者-消費者模型需正確同步。關鍵步驟或流程：1) 以鎖/Concurrent 結構保護佇列；2) 無工作時等待事件；3) 入列觸發喚醒；4) 終止旗標讓工人安全退出；5) 例外處理保證計數一致。核心組件介紹：ConcurrentQueue、ManualResetEvent、lock/Monitor、Interlocked。良好設計避免忙等、競態與資源洩漏。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: C-Q1, C-Q6, D-Q6

B-Q12: 執行緒數如何與核心數對映？
- A簡: CPU-bound 任務以核心數±1 為基準；混合負載依任務型態與 UI 需求微調。
- A詳: 技術原理說明：CPU-bound 最佳化常以「每核心一執行緒」起步，避免過度切換。關鍵步驟或流程：1) 偵測核心數；2) RAW 類瓶頸限制在 1；3) JPEG 類設定為 2~核心數（四核可 4）；4) 觀察使用率與 UI 回應微調。核心組件介紹：Environment.ProcessorCount、ThreadPriority、池參數。本文在雙核設定 RAW=1、JPEG=2~4，即可達到平衡。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, C-Q8, D-Q2

B-Q13: 為何多開執行緒可能反而更慢？
- A簡: 受限於不可平行瓶頸、鎖競爭、快取失效率與切換開銷，效率下降。
- A詳: 技術原理說明：當任務內部序列化或大量共享狀態時，新增執行緒不帶來實際並行，反而增加切換與鎖競爭。關鍵步驟或流程：1) 確認瓶頸可否平行；2) 控制併發度；3) 減少共享資源；4) 監測實際使用率。核心組件介紹：鎖/監視器、上下文切換、CPU 快取。本文 RAW 解碼即便多線程仍僅約 60% 使用率，說明此現象。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, D-Q3, C-Q3

B-Q14: 如何避免 UI thread starvation？
- A簡: 調低背景優先權、控制併發、節流 UI 更新、使用 Dispatcher 非同步呼叫。
- A詳: 技術原理說明：UI 飢餓源於時間片被背景工作搶占。關鍵步驟或流程：1) 背景執行緒設 BelowNormal/Lowest；2) 限制 JPEG 池併發；3) 合批或節流 UI 更新頻率；4) 使用 BeginInvoke 非阻塞；5) 量測輸入延遲。核心組件介紹：ThreadPriority、Dispatcher、計時器/節流器。此策略能解決「進度有動、預覽不出」的體驗問題。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q25, C-Q5, D-Q1

B-Q15: 預覽圖顯示的資料流設計？
- A簡: 背景完成一張即產生縮圖，封送回 UI 更新 Image 控制項，避免阻塞。
- A詳: 技術原理說明：以事件驅動的逐張完成更新 UX。關鍵步驟或流程：1) RAW/JPEG 任務完成→產生縮圖位元資料；2) 透過 Dispatcher.BeginInvoke 更新 Image.Source；3) 控制頻率與清理舊資源；4) 與進度列更新解耦。核心組件介紹：位圖快取、Dispatcher、弱事件/訊息。此設計讓「每張轉完就顯示」成為可能，增強回饋。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q5, D-Q4, A-Q25

B-Q16: 為何內建 ThreadPool 不能設定優先權與多池？
- A簡: 因其設計定位在通用共用資源，避免複雜化 API；細緻控制需自訂或用高階框架。
- A詳: 技術原理說明：ThreadPool 是 CLR 層通用元件，需平衡簡單性與安全性。關鍵步驟或流程：集中管理執行緒避免濫用，限制 per-thread 調度控制。核心組件介紹：全域池、工作排程。對需要優先權隔離與多池場景，自訂池或使用更高階框架（如 TPL 自定 TaskScheduler）更合適。本文採自訂池達成需求。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q19, C-Q1, D-Q3

B-Q17: WaitHandle 在等待多工作時的局限？
- A簡: 需為每工作建立/管理句柄，易複雜化與資源洩漏；錯誤處理困難。
- A詳: 技術原理說明：WaitHandle 適合理解同步基礎，但在大量工作管理上負擔大。關鍵步驟或流程：1) 建立多個 AutoResetEvent；2) 每工作完 Set 一次；3) WaitAll/WaitAny 等待；4) 清理資源。核心組件介紹：事件物件、OS 資源。自訂池用計數+單一事件即可等全部完成，架構更簡潔可靠。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q13, C-Q6, D-Q6

B-Q18: 測試比較如何設計？
- A簡: 固定資料集、切換不同排程策略，量測 CPU 使用率曲線與完工時間與 UX 差異。
- A詳: 技術原理說明：以對照組比對策略效果。關鍵步驟或流程：1) 固定測試集（如 125 JPEG + 22 RAW）；2) 場景一：內建 ThreadPool；3) 場景二：自訂多池與優先權；4) 記錄 CPU 曲線與完工秒數；5) 評估 UI 預覽是否即時。核心組件介紹：計時器、性能監視工具、日誌。本文結果：110 秒→90 秒，且 UI 預覽可即時顯示。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q10, D-Q2, A-Q17

B-Q19: 與 Parallel Extensions/TPL 的關係？
- A簡: TPL 提供更聰明的平行運算（如平行迴圈）；當時為預覽版，本文暫未採用。
- A詳: 技術原理說明：Parallel Extensions（後成為 TPL/PLINQ）提供資料/工作平行模型、工作竊取排程與自動負載平衡。關鍵步驟或流程：用 Parallel.For/PLINQ 重寫迴圈可自動平行化。核心組件介紹：Task、TaskScheduler、Parallel。本文聚焦在優先權與多池隔離，這是 TPL 不直接提供的細節控制，因此以自訂池應對當下需求。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q21, C-Q1, D-Q3

B-Q20: Canon RAW Codec 的瓶頸在哪一層？
- A簡: 主要在解碼階段，屬不可平行或內部序列化，限制 CPU 使用率提升。
- A詳: 技術原理說明：觀測到單張 RAW 的處理時間長，且多執行緒無法拉滿 CPU。關鍵步驟或流程：嘗試增加併發仍停在 50-60% 使用率。核心組件介紹：RAW 解碼器內部運作（黑盒）、可能鎖/序列化。策略結論：限制 RAW 併發並提高優先權，讓 JPEG 任務併行填充，最佳化整體吞吐。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q1, A-Q8, D-Q2

B-Q21: 為什麼 JPEG 任務適合用多執行緒？
- A簡: JPEG 任務獨立、短、可平行，併發處理能接近線性提升吞吐。
- A詳: 技術原理說明：多張 JPEG 的縮圖/編碼彼此間無共享狀態或依賴。關鍵步驟或流程：將每張圖片視為工作單元，分派到多個執行緒併行處理；完工即回報與輸出。核心組件介紹：工作佇列、獨立任務、低優先權池。此法能有效利用 RAW 無法吃滿的 CPU 剩餘能力，提高整體效率。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q7, C-Q4, D-Q2

B-Q22: 任務顆粒度（granularity）如何影響效能？
- A簡: 顆粒過小有排程/切換開銷；過大則平行度不足。需結合負載特性調整。
- A詳: 技術原理說明：理想顆粒度讓工作時間遠大於排程與同步開銷。關鍵步驟或流程：1) 以單張影像為顆粒；2) RAW 維持單一長任務；3) JPEG 多個中短任務；4) 依測試調整批量與更新頻率。核心組件介紹：工作分割策略、批次大小、更新節流。本文以影像為單位獲得良好平衡。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q4, C-Q9, D-Q3

B-Q23: ThreadPool 對 I/O-bound 與 CPU-bound 的適用性差異？
- A簡: I/O-bound 可多開以隱藏等待；CPU-bound 需控併發與優先權，避免壓死 UI。
- A詳: 技術原理說明：I/O-bound 花時間在等待，更多併發可提高吞吐；CPU-bound 真正消耗 CPU，多開不一定好。關鍵步驟或流程：辨識任務型態，I/O-bound 可提高併發；CPU-bound 控制於核心數，並調低優先權。核心組件介紹：池參數、ThreadPriority、任務分類。本文屬 CPU-bound，故強調併發控制與多池策略。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q12, D-Q2

B-Q24: 進度列與預覽對體驗有何技術影響？
- A簡: 穩定更新提升可預期性；顯示每張完成的預覽能強化回饋與錯誤可視性。
- A詳: 技術原理說明：即時回饋可降低等待焦慮並提升信任。關鍵步驟或流程：1) 每張完成即更新預覽；2) 進度列採總任務完成比例；3) 控制更新頻率避免 UI 顫動；4) 錯誤與重試可視化。核心組件介紹：UI thread、Dispatcher、進度模型。本文自訂池讓 UI 在高負載下仍能順暢更新，顯著提升使用體驗。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q7, C-Q5, D-Q4

B-Q25: 設計權衡：效能、回應與複雜度如何平衡？
- A簡: 以多池+優先權換取效能與 UX；複雜度增加但可控，較適合關鍵效能場景。
- A詳: 技術原理說明：自訂池增加開發/維護成本，但能帶來顯著效益。關鍵步驟或流程：1) 明確瓶頸定位；2) 以最小必要功能（固定數、優先權、EndPool）實作；3) 驗證效益（110→90 秒）；4) 管控風險（測試、記錄）。核心組件介紹：池框架、測試基礎設施、回歸檢測。此平衡在需要精準排程的影像處理特別划算。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q5, B-Q18, D-Q3

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何用 C# 快速實作最小版 SimpleThreadPool？
- A簡: 建立固定工作者執行緒、執行緒安全佇列、Start/Queue/End API 與優先權設定。
- A詳: 具體實作步驟：1) 定義 SimpleThreadPool(int threads, ThreadPriority prio)；2) 建立佇列與同步事件；3) StartPool 生成工作者執行緒，設定 Priority 後進入取件迴圈；4) QueueWorkItem 入列並 Set 事件；5) EndPool 設終止旗標、等未完成=0、Join。關鍵程式碼片段或設定:
```
class SimpleThreadPool {
  readonly Thread[] workers; volatile bool stopping=false;
  readonly ConcurrentQueue<(WaitCallback,object)> q = new();
  int pending=0; AutoResetEvent ev = new(false);
  public void StartPool() { /* 建立workers, 設Priority, ThreadStart: loop取q*/ }
  public void QueueWorkItem(WaitCallback cb, object s){ Interlocked.Increment(ref pending); q.Enqueue((cb,s)); ev.Set(); }
  public void EndPool(){ stopping=true; while(Volatile.Read(ref pending)>0) ev.Set(); foreach(var t in workers) t.Join(); }
}
```
- 注意事項與最佳實踐：確保例外處理時 pending--；避免忙等；釋放資源。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q3, C-Q6

C-Q2: 如何建立兩組池並配置優先權與執行緒數？
- A簡: 建 RAW 池（1執行緒、較高優先）與 JPEG 池（2-4執行緒、較低優先），分流任務。
- A詳: 具體實作步驟：1) var rawPool=new SimpleThreadPool(1, ThreadPriority.BelowNormal/Normal)；2) var jpgPool=new SimpleThreadPool(2..4, ThreadPriority.Lowest/BelowNormal)；3) 分別 StartPool；4) RAW 任務排入 rawPool；JPEG 任務排入 jpgPool。關鍵程式碼片段或設定:
```
var rawPool = new SimpleThreadPool(1, ThreadPriority.BelowNormal);
var jpgPool = new SimpleThreadPool(Environment.ProcessorCount, ThreadPriority.Lowest);
rawPool.StartPool(); jpgPool.StartPool();
```
- 注意事項與最佳實踐：依核心數調整 jpgPool；觀察 UI 流暢度微調優先權。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q5, A-Q10, C-Q8

C-Q3: 如何將 RAW 解碼任務限制為單執行緒？
- A簡: 建立專屬 RAW 池僅 1 執行緒，所有 RAW 任務都排入該池，避免併發與競爭。
- A詳: 具體實作步驟：1) 建 rawPool(1, prioHigher)；2) 將每個 CR2 檔建立 WaitCallback 封裝解碼；3) QueueWorkItem 至 rawPool；4) 在解碼完成回呼中將後續 JPEG 任務排入 jpgPool。關鍵程式碼片段或設定:
```
rawPool.QueueWorkItem(_ => {
  var bmp = CanonDecode(cr2Path, targetSize);
  jpgPool.QueueWorkItem(__ => SaveJpeg(bmp, outPath), null);
}, null);
```
- 注意事項與最佳實踐：確保解碼失敗有錯誤回報與重試；釋放中介影像。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q6, D-Q2

C-Q4: 如何併行 JPEG 任務以填滿 CPU？
- A簡: 將每張 JPEG 縮圖/編碼視為獨立工作，排入多執行緒低優先權池平行執行。
- A詳: 具體實作步驟：1) 建 jpgPool(2..核心數, Lowest)；2) 對每張 JPG 或解碼完成的 RAW 產生縮圖任務；3) QueueWorkItem 到 jpgPool；4) 完成後回 UI 更新預覽。關鍵程式碼片段或設定:
```
foreach(var img in inputs)
  jpgPool.QueueWorkItem(_ => ResizeAndSave(img, size, quality), null);
```
- 注意事項與最佳實踐：控制磁碟寫入併發以免 I/O 抖動；批次 flush；錯誤隔離。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q21, A-Q17, D-Q2

C-Q5: 如何在 WPF 安全更新 UI（預覽圖與進度）？
- A簡: 背景執行緒完成一張後用 Dispatcher.BeginInvoke 更新 UI，降低更新頻率。
- A詳: 具體實作步驟：1) 工作完成時封送回 UI thread；2) 更新 Image.Source 與 ProgressBar 值；3) 以節流控制頻率。關鍵程式碼片段或設定:
```
Application.Current.Dispatcher.BeginInvoke(new Action(() => {
  image.Source = CreateBitmapSource(preview);
  progress.Value = completed/(double)total*100;
}));
```
- 注意事項與最佳實踐：避免使用 Invoke（同步阻塞）；釋放舊位圖避免記憶體泄漏。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, A-Q12, D-Q1

C-Q6: 如何實作等待所有工作完成（EndPool）？
- A簡: 以未完成計數與事件等待，在 EndPool 阻塞直至計數為 0，再 Join 工作者。
- A詳: 具體實作步驟：1) pending++/-- 管理；2) 當 pending 轉為 0 時 Set 事件；3) EndPool 設 stopping=true 並 WaitOne()；4) Join 執行緒。關鍵程式碼片段或設定:
```
ManualResetEvent done = new(false);
void OnWorkDone(){ if(Interlocked.Decrement(ref pending)==0) done.Set(); }
public void EndPool(){ stopping=true; if(pending>0) done.WaitOne(); foreach(var t in workers) t.Join(); }
```
- 注意事項與最佳實踐：處理例外時務必遞減計數；避免死鎖；允許超時與取消。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, B-Q17, D-Q6

C-Q7: 如何設定 ThreadPriority 以保護 UI？
- A簡: RAW 池設 BelowNormal/Normal，JPEG 池設 Lowest/BelowNormal，避免搶占 UI。
- A詳: 具體實作步驟：1) 建池時傳入目標優先權；2) 或建立 Thread 後設定 thread.Priority；3) 根據實測微調。關鍵程式碼片段或設定:
```
var t = new Thread(WorkerLoop){ IsBackground=true, Priority=ThreadPriority.Lowest };
t.Start();
```
- 注意事項與最佳實踐：避免 Highest；若 UI 仍卡，進一步降至 Lowest 並減少併發。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q4, D-Q1, D-Q9

C-Q8: 如何依 CPU 核心數動態決定執行緒數？
- A簡: 以 Environment.ProcessorCount 為基準，設定 JPEG 池=核心數，RAW 池=1。
- A詳: 具體實作步驟：1) int n=Environment.ProcessorCount；2) var jpgPool=new SimpleThreadPool(Math.Max(2,n), ThreadPriority.Lowest)；3) RAW 池固定 1。關鍵程式碼片段或設定:
```
int cores = Environment.ProcessorCount;
var jpgPool = new SimpleThreadPool(Math.Min(4, Math.Max(2, cores)), ThreadPriority.Lowest);
```
- 注意事項與最佳實踐：觀察使用率與 UI 流暢度做微調；四核以上可擴至 4。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q12, A-Q11, D-Q2

C-Q9: 如何撰寫批次縮圖程式骨架？
- A簡: 掃描檔案→按類型分派 RAW/JPEG 任務→處理完成即回報→等待全部完成→收尾。
- A詳: 具體實作步驟：1) 遍歷輸入清單；2) RAW→rawPool 解碼，再派 JPG 任務；JPG→jpgPool 直接縮圖；3) 每張完成更新 UI；4) EndPool 等待；5) 資源清理。關鍵程式碼片段或設定:
```
foreach(var f in files)
  if(IsRaw(f)) rawPool.QueueWorkItem(_=>DecodeThenEnqueueJpeg(f),null);
  else jpgPool.QueueWorkItem(_=>ResizeJpeg(f),null);
rawPool.EndPool(); jpgPool.EndPool();
```
- 注意事項與最佳實踐：小尺寸優先（更快）；控制磁碟併發；記錄錯誤與重試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q22, B-Q6, D-Q5

C-Q10: 如何做效能量測與記錄 CPU 使用率？
- A簡: 固定資料集，量測總時間與觀察 CPU 使用率曲線，記錄 UI 響應情況。
- A詳: 具體實作步驟：1) Stopwatch 量測總時；2) PerformanceCounter 或外部工具監控 CPU 使用率；3) 對照不同策略（單池/多池）；4) 記錄預覽顯示延遲。關鍵程式碼片段或設定:
```
var sw=Stopwatch.StartNew(); // ... run ...
sw.Stop(); Console.WriteLine($"Elapsed: {sw.Elapsed.TotalSeconds}s");
```
- 注意事項與最佳實踐：多次測試取中位數；避免背景程式干擾；分離 I/O 與 CPU。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q10, B-Q18, D-Q2

### Q&A 類別 D: 問題解決類（10題）

D-Q1: UI 卡住或預覽不顯示怎麼辦？
- A簡: 降低背景優先權、限制併發、用 Dispatcher.BeginInvoke 更新 UI、節流更新頻率。
- A詳: 問題症狀描述：進度列在跑，但預覽圖不出現或 UI 無回應。可能原因分析：工作執行緒與 UI thread 搶占 CPU；同步更新阻塞 UI。解決步驟：1) 背景執行緒設 BelowNormal/Lowest；2) 限制 JPEG 併發；3) 以 Dispatcher.BeginInvoke 非同步更新；4) 合批/節流 UI 更新。預防措施：在設計期就採多池隔離、優先權保護 UI，並加入 UI 回應度監測。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q7, A-Q25, C-Q5

D-Q2: CPU 利用率長期停在 60% 左右，如何提升？
- A簡: 限制 RAW 併發至 1、提高其優先權，並用多執行緒 JPEG 任務填滿剩餘 CPU。
- A詳: 問題症狀描述：多開執行緒仍無法拉滿 CPU。可能原因分析：RAW 解碼不可平行或內部序列化。解決步驟：1) RAW 池 1 執行緒、較高優先權；2) JPEG 池多執行緒、低優先權；3) 觀察並微調執行緒數與優先權；4) 優先使用小尺寸解碼。預防措施：設計時將任務分類、選擇合適顆粒度與池配置。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q5, C-Q4

D-Q3: 多開 ThreadPool 反而更慢，原因與解法？
- A簡: 不可平行瓶頸導致競爭與切換開銷；以多池隔離、控併發與優先權解決。
- A詳: 問題症狀描述：執行緒數增加但單張時間變長、總時間上升。可能原因分析：RAW 解碼序列化、鎖競爭、快取失效。解決步驟：1) RAW 限 1；2) JPEG 多執行緒，但不超過核心數；3) 降低 JPEG 優先權；4) 優先處理瓶頸任務。預防措施：量測與調參、避免盲目擴大併發、優先採用平行程式庫於可平行區段。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q13, A-Q5, C-Q2

D-Q4: 進度列會動但影像不更新，如何診斷？
- A簡: 檢查 UI 更新是否在 UI thread、更新是否阻塞、是否過於頻繁導致飢餓。
- A詳: 問題症狀描述：進度變化但預覽圖未顯示。可能原因分析：UI 更新未用 Dispatcher 封送、同步呼叫阻塞、更新過密。解決步驟：1) 確保使用 Dispatcher.BeginInvoke；2) 減少每張更新內容大小；3) 增加節流（如每 N 張更新一次）；4) 觀察 UI thread 負載。預防措施：建立 UI 更新抽象層與節流策略。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q15, C-Q5, A-Q25

D-Q5: RAW 轉檔一張要 60–80 秒，如何優化？
- A簡: 目標小尺寸輸出、限制 RAW 併發、提升其優先權，並讓 JPEG 併行填充。
- A詳: 問題症狀描述：原尺寸輸出極慢。可能原因分析：RAW 解碼成本高且不可平行。解決步驟：1) 若需求允許，直接以小尺寸解碼/輸出（5 秒級）；2) RAW 池單執行緒、較高優先權；3) JPEG 任務並行；4) 避免非必要的高品質重採樣。預防措施：需求階段即確認輸出尺寸；建立以目標尺寸為核心的管線。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q16, B-Q9, C-Q9

D-Q6: ThreadPool 工作無法全部完成或難以等待，如何處理？
- A簡: 使用自訂 EndPool（計數+事件）等待全部完成，或以 WaitHandle 正確實作。
- A詳: 問題症狀描述：流程結束時仍有背景工作殘留。可能原因分析：缺乏一致的等待/收尾機制。解決步驟：1) 自訂池以 pending 計數追蹤工作數；2) EndPool 設 stopping 並等待 pending=0；3) Join 工作者；4) 若使用內建池，為每工作配置 WaitHandle 並 WaitAll。預防措施：建立一致的工作生命週期管理與例外保證遞減。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, B-Q17, C-Q6

D-Q7: Vista 上舊 PowerToy 不能用，如何替代？
- A簡: 以自製批次縮圖工具（WPF/WinForms）結合自訂 ThreadPool 與現有 codec。
- A詳: 問題症狀描述：XP 的 Image Resizer PowerToy 在 Vista/WPF 不相容。可能原因分析：GDI+→WPF 管線差異。解決步驟：1) 寫自有工具（WPF/WinForms 皆可）；2) 整合 Canon RAW/JPEG/HD Photo codec；3) 以多池與優先權確保效能與 UX。預防措施：選擇與平台相容的 API；建立可替換 codec 介面。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q24, C-Q9

D-Q8: 記憶體占用過高導致系統鈍，怎麼防治？
- A簡: 優先小尺寸解碼、釋放中介位圖、控制同時在處理與在記憶體的影像數。
- A詳: 問題症狀描述：處理大量高解析影像時記憶體暴增。可能原因分析：同時保留多張全尺寸位圖；GC 壓力。解決步驟：1) 使用目標尺寸解碼；2) 每張完成即釋放暫存位圖；3) 控制 JPEG 併發上限；4) 使用 using/Dispose 管理資源。預防措施：建立資源池與上限；監控工作集大小。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q9, C-Q4, C-Q9

D-Q9: JPEG 任務擠壓 UI，如何設定優先權修正？
- A簡: 將 JPEG 池降至 Lowest，必要時減少執行緒數；UI 更新改為非同步節流。
- A詳: 問題症狀描述：UI 頓挫、輸入延遲。可能原因分析：JPEG 任務使用 Normal 優先權、併發過高。解決步驟：1) 設 ThreadPriority.Lowest；2) 將執行緒數降至核心數或更少；3) UI 更新以 BeginInvoke 並節流；4) 驗證輸入延遲改善。預防措施：預設就採低優先權並從較小併發起步。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q4, C-Q7, A-Q25

D-Q10: 不同相機 RAW 表現差異導致不穩定，如何保護？
- A簡: 為 RAW 池保留併發=1 與較高優先權；加入超時、錯誤回報與跳過策略。
- A詳: 問題症狀描述：部分 RAW 型號解碼更慢或偶有例外。可能原因分析：codec 實作差異、檔案特性差異。解決步驟：1) 持續維持 RAW 併發=1；2) 加入超時與取消；3) 記錄錯誤並允許跳過；4) 對特定型號可調整批次策略。預防措施：在前測階段就蒐集多型號資料；設計可擴充的錯誤處理。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q1, B-Q20, C-Q3

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 Canon RAW Codec？
    - A-Q2: 什麼是 WPF？為何影響影像工具的相容性？
    - A-Q3: 什麼是 .NET ThreadPool？
    - A-Q6: 什麼是 CPU-bound 工作？為何影像轉檔屬於此類？
    - A-Q7: Canon RAW 解碼與 JPEG 任務的差異是什麼？
    - A-Q9: 什麼是執行緒優先順序（ThreadPriority）？為何重要？
    - A-Q10: 為什麼要使用多組 ThreadPool？
    - A-Q11: 為什麼固定執行緒數量通常較好？
    - A-Q12: 什麼是 UI Thread？為何要保護它的流暢性？
    - A-Q15: 什麼是 HD Photo 的「小圖快顯」特性？
    - A-Q16: 為什麼縮成小尺寸比輸出原尺寸快很多？
    - B-Q1: .NET 內建 ThreadPool 如何運作？限制為何？
    - B-Q5: 兩個 ThreadPool 協同的排程機制是什麼？
    - B-Q7: WPF UI 響應如何與背景工作協同？
    - D-Q1: UI 卡住或預覽不顯示怎麼辦？

- 中級者：建議學習哪 20 題
    - A-Q4: 什麼是 SimpleThreadPool（自訂 ThreadPool）？
    - A-Q5: 為什麼需要自訂 ThreadPool？
    - A-Q8: 為什麼多開執行緒無法讓 RAW 更快？
    - A-Q17: 什麼是「慢任務優先、快任務填充」的排程策略？
    - A-Q18: CPU 使用率曲線面積與總運算量的關係是什麼？
    - A-Q19: 內建 ThreadPool 與 SimpleThreadPool 的差異是什麼？
    - B-Q2: SimpleThreadPool 的架構包含哪些元件？
    - B-Q3: SimpleThreadPool 的執行流程為何？
    - B-Q4: 執行緒優先權如何影響排程？
    - B-Q6: RAW 解碼與 JPEG 任務併行的資料流如何設計？
    - B-Q9: 小尺寸輸出為何在解碼階段就變快？
    - B-Q10: CPU 使用率與完工時間的關係機制是什麼？
    - B-Q12: 執行緒數如何與核心數對映？
    - B-Q13: 為何多開執行緒可能反而更慢？
    - B-Q18: 測試比較如何設計？
    - C-Q2: 如何建立兩組池並配置優先權與執行緒數？
    - C-Q3: 如何將 RAW 解碼任務限制為單執行緒？
    - C-Q4: 如何併行 JPEG 任務以填滿 CPU？
    - C-Q5: 如何在 WPF 安全更新 UI？
    - D-Q2: CPU 利用率長期停在 60% 左右，如何提升？

- 高級者：建議關注哪 15 題
    - B-Q11: 工作佇列與同步如何設計才穩定？
    - B-Q14: 如何避免 UI thread starvation？
    - B-Q16: 為何內建 ThreadPool 不能設定優先權與多池？
    - B-Q17: WaitHandle 在等待多工作時的局限？
    - B-Q19: 與 Parallel Extensions/TPL 的關係？
    - B-Q22: 任務顆粒度如何影響效能？
    - B-Q23: ThreadPool 對 I/O-bound 與 CPU-bound 的適用性差異？
    - B-Q25: 設計權衡：效能、回應與複雜度如何平衡？
    - C-Q1: 如何用 C# 快速實作最小版 SimpleThreadPool？
    - C-Q6: 如何實作等待所有工作完成（EndPool）？
    - C-Q8: 如何依 CPU 核心數動態決定執行緒數？
    - D-Q3: 多開 ThreadPool 反而更慢，原因與解法？
    - D-Q5: RAW 轉檔一張要 60–80 秒，如何優化？
    - D-Q6: ThreadPool 工作無法全部完成或難以等待，如何處理？
    - D-Q10: 不同相機 RAW 表現差異導致不穩定，如何保護？