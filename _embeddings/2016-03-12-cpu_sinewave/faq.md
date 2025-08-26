# [樂CODE] Microsoft 面試考題: 用 CPU utilization 畫出正弦波

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是「用 CPU utilization 畫出正弦波」？
- A簡: 透過控制每段時間的忙/閒比例，使 CPU 使用率隨時間呈現正弦波。
- A詳: 題目的本質是用程式讓 CPU 在固定時間窗內呈現指定負載比例。將時間切成若干小段（如每 100ms），在每段中用忙等（busy wait）與空閒（idle）時間的比例對應 sin 函數值，令使用率隨時間變化近似正弦波。核心是把連續的類比目標，離散化為可控的時間片行為。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q7, B-Q1, B-Q3

A-Q2: 為什麼要將 sin(x) 位移與縮放為 f(x)=(sin x + 1)/2？
- A簡: 將 [-1,1] 正規化為 [0,1]，對應忙/閒比例的百分比。
- A詳: 原始 sin(x) 落在 [-1,1]，無法直接作為負載百分比。位移與縮放成 f(x)=(sin x+1)/2，可將其映射為 [0,1] 的比例值。於每段時間單位 unit 內，busy=unit·f(x)，idle=unit-busy，即可把數學函數直覺地轉化為可執行的時間分配。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, B-Q2, C-Q3

A-Q3: 什麼是 Busy Waiting（忙等）？
- A簡: 以持續運算的無窮迴圈消耗 CPU，令單核心近似 100% 使用。
- A詳: 忙等是以迴圈不停執行（如 while(true)）來占用 CPU 時間片，常用於簡單的等待/控制場景。優點是可預測、響應即時，缺點是浪費能耗且單執行緒通常僅能吃到單核心。搭配適當時間控制，可作為「負載上升」的手段。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q4, D-Q2

A-Q4: SpinWait 與 Thread.Sleep 有何差異？
- A簡: Sleep 交還時間片，精度受 OS/硬體影響；SpinWait 忙等+讓步，穩定性較佳。
- A詳: Thread.Sleep 會讓出時間片，由排程器決定喚醒時點，精度受硬體計時與 OS 影響，容易飄移。SpinWait 則在迴圈中混合短暫自旋與讓步（含 HLT）降低耗能，少掉上下文切換的不確定性，通常穩定但可能有固定延遲偏移。實測顯示 Sleep 誤差小但飄移大；SpinWait 飄移小但平均偏長。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q5, D-Q3, D-Q4

A-Q5: 「精確度」與「精密度」有何不同？
- A簡: 精確度指接近真值，精密度指結果穩定一致；兩者獨立。
- A詳: 精確度（accuracy）衡量平均值距離目標的接近程度；精密度（precision）衡量多次測量的離散程度（如標準差）。在本題中，需兼顧兩者：平均對得準（精確）且波動小（精密），波形才會漂亮。實驗以 50 次測量平均值評估精確度、標準差評估精密度。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, D-Q1

A-Q6: 多核心為何會影響 CPU 使用率控制？
- A簡: 單一忙等執行緒只吃一核心，總體使用率被攤薄。
- A詳: 忙等迴圈通常只在單執行緒/單核心上消耗，於 4 核 8 執行緒的處理器，單執行緒忙等僅約 12.5% 全機使用率。若要達到更高總體使用率或多核一致波形，需增加對應數量的忙等工作或限定於單核心/單核 VM 運行以降低干擾。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q5, D-Q2, B-Q9

A-Q7: 為什麼要把時間切成固定單位（如 100ms）？
- A簡: 便於離散控制每段忙/閒比例，權衡解析度與穩定性。
- A詳: 將連續時間離散化為 unit 長度有助於務實控制。unit 越小解析度越高但對雜訊更敏感，管理成本上升；unit 越大曲線較平滑但細節變少。文章以 100ms 為折衷，能兼顧可觀測性與實作難度。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q11, D-Q6

A-Q8: 為什麼 Thread.Sleep 不適用於高精密時間控制？
- A簡: 受排程與時鐘解析度影響，喚醒漂移大且硬體依賴高。
- A詳: Sleep 會進入等待，喚醒由 OS 與硬體計時器決定；在負載或背景雜訊下漂移明顯。不同主機板/電源管理策略也影響精度。雖然單次誤差可能小，但不可預測性使波形易變形。改用 Spin 或改良式 Sleep/Spin 可提升穩定度。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, D-Q3, C-Q7

A-Q9: 什麼是 SpinWait.SpinUntil（概念層次）？
- A簡: 反覆執行委派條件判斷與自旋/讓步，直到條件成立或逾時。
- A詳: SpinUntil 接受一個回呼條件與逾時，框架以內部自旋策略多次評估條件，中途穿插讓步與節能指令，直到條件成立或逾時。它減少了睡眠/喚醒的不確定性，但委派評估與自旋策略帶來固定成本。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q10, D-Q4

A-Q10: 為什麼要預先計算查表（Lookup Table）？
- A簡: 把昂貴運算搬到初始化，執行期 O(1) 查詢，留時間給 idle。
- A詳: sin/影像轉換等運算放在初始化建立 data[] 對照表，主迴圈只需查表與簡單加減，避免在每個時間片內額外 CPU 消耗，減少對波形的干擾。此技術同時提升效能與可預測性，是穩定波形的關鍵。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, C-Q3, C-Q8

A-Q11: HLT 指令在忙等待中的角色是什麼？
- A簡: 讓 CPU 暫停至中斷回來，降低能耗與熱，改善忙等副作用。
- A詳: HLT（halt）可使處理器暫停，待外部事件喚醒。現代自旋策略常混合 HLT 或類似節能手段，避免長時間滿載忙等導致發熱與搶奪時間片。C# 不直接呼叫 HLT，但 SpinWait 內部策略會妥善利用硬體行為。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q10

A-Q12: 什麼是 Advanced Sleep 與 Advanced SpinUntil？
- A簡: 改良等待：Sleep(0) 讓步輪詢、或以 Stopwatch 回呼判斷取代逾時。
- A詳: Advanced Sleep 以 while(timer<idle) Thread.Sleep(0) 實作，頻繁讓步降低漂移；Advanced SpinUntil 改用 SpinUntil(()=>timer.Elapsed>idle) 控時，避開 timeout 的固定開銷。實測這兩者相較原生版本更可預測，後者在準確度/精密度上最佳。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q7, B-Q8, D-Q4

A-Q13: 為什麼要最小化程式自身的干擾？
- A簡: 額外運算會改變負載，破壞預期 idle 時間並扭曲波形。
- A詳: 任一非必要工作（運算、IO、日誌、GC）都會在「應 idle」的時間吃掉 CPU，導致使用率偏移。最佳做法：重計算前置化、主迴圈只查表與簡單運算、所有額外工作算入 busy 段以免侵蝕 idle。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q1, C-Q3, B-Q3

A-Q14: 為什麼 idle 段也會被系統干擾？
- A簡: 排程、背景執行緒、GC/中斷都會引用時間片，縮短可用 idle。
- A詳: 即便在 Spin/休眠狀態，系統仍可能切走你的執行緒，或有背景工作插入佔用 CPU，造成 idle 期實際更短。應建立乾淨環境、降低噪音執行緒，並使用更穩定的等待方式。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, D-Q1, C-Q1

A-Q15: 為什麼可用 ASCII Art 畫任意圖形？
- A簡: 將每列圖形的高度映射為時間-負載表，依序輸出即成曲線。
- A詳: 以字串陣列描繪圖樣，逐步掃描每個 x（時間步）找第一個 'X' 的 y 位置，轉為該步的 idle 時間。主迴圈按 data[] 執行 idle→busy，CPU 利用率曲線即呈現出圖形外輪廓。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q8, B-Q14, C-Q2

A-Q16: 本題的核心價值是什麼？
- A簡: 以工程方法把數學轉行為，實測量化、迭代優化，展現系統思維。
- A詳: 題目結合數學映射、OS 排程、計時器、執行緒與量測方法論。透過建模（sin→比例）、實作（忙/閒控制）、量測（平均/標準差）與迭代（Advanced*），體現「以實證修正直覺」與「降低不確定性」的工程精神。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q8, D-Q1

### Q&A 類別 B: 技術原理類

B-Q1: CPU 利用率如何由忙/閒比例決定？
- A簡: 固定時間窗內，busy 時間除以總時間即為利用率。
- A詳: 原理說明：在長度為 unit 的時間片中，以 busy_ms/unit 近似該片 CPU 利用率。關鍵步驟：計算目標比例 p、求 busy_ms=p·unit、idle_ms=unit-busy_ms。核心組件：Stopwatch 作計時、忙等迴圈填滿 busy、等待機制實現 idle。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q7, B-Q2

B-Q2: 數學函數如何映射為忙/閒時間？
- A簡: 用 p=(sin x+1)/2 得到比例，再換算忙/閒毫秒數。
- A詳: 原理說明：x=2πt/period，p=(sin x+1)/2。關鍵步驟：以時間 t 算出 x、求得 p、再轉為 busy/idle 時間。核心組件：三角函數、正規化、period 與 unit 設定，保證函數→時間控制的一致性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, C-Q3

B-Q3: 程式架構與執行流程為何？
- A簡: 初始化對照表→主迴圈取樣→Idle→Busy→循環。
- A詳: 原理說明：以查表 data[] 對應每步 idle 長度。關鍵步驟：以 Stopwatch 得 elapsed、計 step 與 offset、算 idle_until/busy_until、先 idle 再 busy。核心組件：Stopwatch、SpinWait、自旋忙等、查表資料結構，降低計算干擾。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q2, C-Q9, A-Q10

B-Q4: Thread.Sleep 與 SpinWait 的計時機制差異？
- A簡: Sleep 依賴排程與硬體定時，SpinWait 自旋評估條件混合讓步。
- A詳: 原理說明：Sleep 進入等待，由 OS 以時鐘喚醒；SpinWait 持續檢查條件，穿插讓步/節能。關鍵步驟：Sleep(毫秒) 與 SpinUntil(條件, timeout) 使用。核心組件：內核排程器、硬體計時器、HLT/讓步策略。影響：Sleep 漂移大，SpinWait 更穩。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, D-Q3, D-Q4

B-Q5: 為何 SpinUntil 的 timeout 造成固定延遲？
- A簡: 委派重複評估與自旋策略成本高，逾時是上限而非精準點。
- A詳: 原理說明：SpinUntil 多次呼叫委派，混入等待策略，timeout 僅限制最長等待。關鍵步驟：實測 10ms 目標會因委派評估 130~150 次等成本延至 23~26ms。核心組件：委派呼叫、記憶體屏障、自旋計數。解法：改用 Stopwatch 控制條件回呼。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q7, D-Q4

B-Q6: Advanced Sleep 的機制與流程？
- A簡: 以 Stopwatch 控時，迴圈 Sleep(0) 讓步至達目標時間。
- A詳: 原理說明：Sleep(0) 讓出時間片但不強制睡眠。關鍵步驟：Restart 計時→while(elapsed<idle) Sleep(0)。核心組件：Stopwatch、Sleep(0)。優點：避免長睡眠喚醒飄移；缺點：仍受排程影響。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, D-Q3

B-Q7: Advanced SpinUntil 的機制與流程？
- A簡: 用 Stopwatch 驗證條件，SpinUntil(()=>elapsed>idle) 取代 timeout。
- A詳: 原理說明：移除 timeout 參數，改以自定條件控制退出點。關鍵步驟：timer.Restart()→SpinUntil(()=>timer.Elapsed>idle)。核心組件：Stopwatch、SpinWait。優點：準確度/精密度更佳；缺點：仍有自旋成本。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, D-Q4, C-Q4

B-Q8: 如何量化準確度與精密度？
- A簡: 多次測量求平均值評估準確度，標準差評估精密度。
- A詳: 原理說明：統計方法驗證等待策略品質。關鍵步驟：每種方法在不同噪音執行緒下跑 50 次，分析平均與標準差。核心組件：資料收集、平均/標準差、圖表比較。結論：Advanced SpinUntil 綜合表現最佳。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, D-Q1, C-Q7

B-Q9: 背景干擾（noise threads）如何影響？
- A簡: 佔用時間片、增加上下文切換，推遲喚醒與自旋進度。
- A詳: 原理說明：噪音執行緒與你的執行緒競爭 CPU。關鍵步驟：隨噪音執行緒數增加，Sleep 飄移放大，SpinUntil 受影響較小。核心組件：OS 排程、公平性、超執行緒。建議：減少背景程式或用單核 VM。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, D-Q1, C-Q1

B-Q10: SpinWait 在單核/多核/超執行緒的行為？
- A簡: 單核偏讓步，多核混合自旋/讓步，避免硬體執行緒飢餓。
- A詳: 原理說明：.NET 的 SpinWait 會依環境調整策略。關鍵步驟：在單處理器更常 yield；在超執行緒上避免壓死同 die 的兄弟執行緒。核心組件：SpinWait 策略、HLT/PAUSE 指令、排程器互動。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, A-Q9

B-Q11: 時間單位（unit）選擇的取捨？
- A簡: 小單位解析高但抖動多；大單位穩定但細節少。
- A詳: 原理說明：unit 影響波形解析度與穩定性。關鍵步驟：依需求在 50–200ms 間權衡，本文使用 100ms。核心組件：計時器解析度、取樣窗口（工作管理員/PerfMon）。選擇會影響觀測與控制的協調。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, D-Q6

B-Q12: Stopwatch 的角色與原理？
- A簡: 使用高解析度硬體計時，提供穩定的 elapsed 計量。
- A詳: 原理說明：Stopwatch 基於 QueryPerformanceCounter，解析度高於 DateTime。關鍵步驟：Restart、讀取 Elapsed/ElapsedMilliseconds。核心組件：硬體計時器、單調時鐘。是等待與評測的基石。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q7, C-Q4

B-Q13: 如何避免時間累積誤差（漂移）？
- A簡: 用 offset 對齊單位邊界，計算 idle_until/busy_until 再執行。
- A詳: 原理說明：每循環用 elapsed 除以 unit 計 step，mod 求 offset，將本段起訖對齊單位邊界。關鍵步驟：step=(elapsed/unit)%(period/unit)、idle_until=elapsed-offset+v、busy_until=elapsed-offset+unit。核心組件：整數除法/模運算。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q9, C-Q2

B-Q14: 任意圖形如何映射到 CPU 載入？
- A簡: 掃描字元陣列求每步高度，轉為 idle 時間表供主迴圈。
- A詳: 原理說明：用字元圖描述外形，x 軸對應時間，y 軸對應負載高度。關鍵步驟：取 x 列、由上而下找第一個 'X' 高度、正規化為 idle 時間。核心組件：bitmap 字串、data[]、主迴圈執行器。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, C-Q8

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何建立最小干擾的執行環境？
- A簡: 使用 1 核心 VM/Server Core，關閉背景程式與節能干擾。
- A詳: 具體步驟：1) 建立 1 核 VM，安裝 Windows Server Core；2) 關閉不必要服務與防毒；3) 電源計畫設為高效能；4) 只執行測試程式。程式碼片段：可提高優先權與限制親和性（選用）
  ```
  using System.Diagnostics;
  Process.GetCurrentProcess().PriorityClass=ProcessPriorityClass.High;
  // 僅綁定核心0
  Process.GetCurrentProcess().ProcessorAffinity=(IntPtr)1;
  ```
  注意事項：避免其他應用、排程任務與更新。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q9, D-Q1

C-Q2: 如何用 C# 基本實作忙/閒控制迴圈？
- A簡: Stopwatch 取樣、依對照表先 idle 後 busy、循環執行。
- A詳: 具體步驟：1) 設定 unit/period；2) 產生 data[]；3) 主迴圈計 step/offset 與 idle_until/busy_until；4) 先 SpinUntil 再忙等。關鍵程式碼：
  ```
  Stopwatch timer=new Stopwatch(); timer.Restart();
  while(true){
    long step=(timer.ElapsedMilliseconds/unit)%(period/unit);
    long offset=timer.ElapsedMilliseconds%unit;
    long v=data[step];
    long idle_until=timer.ElapsedMilliseconds-offset+v;
    long busy_until=timer.ElapsedMilliseconds-offset+unit;
    SpinWait.SpinUntil(()=>timer.ElapsedMilliseconds>idle_until);
    while(timer.ElapsedMilliseconds<busy_until){}
  }
  ```
  注意：計時對齊可減漂移。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q13

C-Q3: 如何實作 sin 查表法提升效能？
- A簡: 初始化期計算 data[]，執行期 O(1) 查詢。
- A詳: 具體步驟：1) 設 steps=period/unit；2) 迴圈算 f(x)；3) 轉為每步 idle。程式碼：
  ```
  long[] GetDataFromSineWave(long period,long unit){
    long steps=period/unit; var data=new long[steps];
    for(int s=0;s<steps;s++){
      data[s]=(long)(unit-(Math.Sin(Math.PI*s*360/steps/180.0)/2+0.5)*unit);
    }
    return data;
  }
  ```
  注意：將昂貴運算移至初始化。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, B-Q2

C-Q4: 如何使用 Advanced SpinUntil 控制 idle？
- A簡: 以 Stopwatch 作條件，SpinUntil(()=>elapsed>idle) 執行。
- A詳: 具體步驟：1) timer.Restart()；2) 在 idle 段以回呼判斷；3) busy 段自旋填滿。程式碼：
  ```
  Stopwatch timer=new Stopwatch(); timer.Restart();
  // idle
  SpinWait.SpinUntil(()=>timer.Elapsed>idle);
  // busy
  while(timer.Elapsed<busy_until){}
  ```
  注意：避免使用 timeout 參數以減固定延遲；確保 timer 為單調高解析。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, D-Q4

C-Q5: 如何以多執行緒填滿多核心？
- A簡: 啟動與可用邏輯核心相近的繪製執行緒，各自跑迴圈。
- A詳: 具體步驟：1) 取得 Environment.ProcessorCount；2) 啟動 N 個執行緒各自執行 DrawLoop；3) 控制 N≤邏輯核心避免過量。程式碼：
  ```
  int n=Environment.ProcessorCount; var ts=new List<Thread>();
  for(int i=0;i<n;i++){ var t=new Thread(DrawLoop); t.Start(); ts.Add(t); }
  ```
  注意：避免超額執行緒導致爭用；或選擇單核 VM。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, D-Q2, B-Q9

C-Q6: 如何調整 unit 與 period 以優化波形？
- A簡: 根據觀測調整 unit（50–200ms）與 period（例如 60s）。
- A詳: 具體步驟：1) 先以 unit=100ms、period=60s；2) 視抖動降低或細節需求調整；3) 觀察 PerfMon/工作管理員平滑效果。程式碼：
  ```
  long unit=100; long period=60*1000;
  var data=GetDataFromSineWave(period,unit);
  ```
  注意：unit 越小越敏感，負載高時請適度放大。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q11, D-Q6

C-Q7: 如何測試 Sleep 與 SpinUntil 的計時精度？
- A簡: 以噪音執行緒 + 多次測量比較 elapsed 與標準差。
- A詳: 具體步驟：1) 啟動 noise 執行緒；2) 以 Stopwatch 測 10 次 Sleep(idle) 與 SpinUntil(idle)；3) 記錄毫秒、計平均與標準差。程式碼：
  ```
  for(int i=0;i<10;i++){ timer.Restart(); Thread.Sleep(10); log(timer.ElapsedMs); }
  for(int i=0;i<10;i++){ timer.Restart(); SpinWait.SpinUntil(()=>false,TimeSpan.FromMs(10)); log(timer.ElapsedMs); }
  ```
  注意：噪音執行緒可模擬真實干擾。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, A-Q8

C-Q8: 如何將 ASCII Art 轉為負載表？
- A簡: 掃描每列 X 的高度生成 data[]，交由主迴圈執行。
- A詳: 具體步驟：1) 準備字串陣列；2) 對每步 s 計算 x；3) 自上而下找 'X' 的 y；4) 轉 idle。程式碼：
  ```
  long[] GetDataFromBitmap(long period,long unit){
    int max_x=bitmap[0].Length, max_y=bitmap.Length;
    long steps=period/unit; var data=new long[steps];
    for(int s=0;s<steps;s++){
      int x=(int)(s*max_x/steps), y=0; for(;y<max_y;y++) if(bitmap[y][x]=='X') break;
      data[s]=y*unit/max_y;
    } return data;
  }
  ```
  注意：字圖要等寬對齊，避免索引越界。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, B-Q14

C-Q9: 如何用 offset 對齊避免時間漂移？
- A簡: 以 offset=elapsed%unit 對齊當前單位起點再計 idle/busy。
- A詳: 具體步驟：1) 算 step 與 offset；2) idle_until=elapsed-offset+v；3) busy_until=elapsed-offset+unit。程式碼：
  ```
  long step=(elapsed/unit)%(period/unit);
  long offset=elapsed%unit;
  long idle_until=elapsed-offset+v;
  long busy_until=elapsed-offset+unit;
  ```
  注意：避免直接累加時間，長時運行更穩。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q13, C-Q2

C-Q10: 如何觀測與記錄波形結果？
- A簡: 用工作管理員或 PerfMon 觀測，設定合適取樣間隔。
- A詳: 具體步驟：1) 工作管理員「效能」頁觀察 CPU 曲線；2) PerfMon 加入 Processor(_Total)\% Processor Time 或 Process\% Processor Time，設取樣 1s；3) 匯出日誌分析平均/標準差。注意：不同工具平滑策略不同，需一致化取樣。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q11, D-Q10

### Q&A 類別 D: 問題解決類（10題）

D-Q1: 波形雜訊大、曲線不平滑怎麼辦？
- A簡: 減少背景干擾、改用 Advanced Spin、前置計算、調大 unit。
- A詳: 症狀：波形鋸齒、上下飄。可能原因：噪音執行緒、Sleep 漂移、運算干擾、unit 過小。解決步驟：1) 清理背景程式或用單核 VM；2) 改用 Advanced SpinUntil；3) 查表法搬運算到初始化；4) unit 上調至 100–200ms。預防：固定環境、記錄標準差監控品質。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, B-Q9, C-Q1

D-Q2: 忙等僅顯示 12.5%（8 執行緒 CPU）怎麼辦？
- A簡: 增加並行忙等工作或在單核 VM 執行以避免攤薄。
- A詳: 症狀：單執行緒忙等全速仍僅十多％。原因：總體使用率是全核心平均。解決：1) 啟動接近邏輯核心數的繪製執行緒；2) 或以單核心限制進程/VM。預防：評估目標曲線是單核心還是全機，提前設計。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, C-Q5, B-Q9

D-Q3: Thread.Sleep 漂移嚴重如何處理？
- A簡: Sleep 受排程影響大，改用 Spin 或 Advanced Sleep。
- A詳: 症狀：Sleep(10ms) 實際 10–30ms 不等。原因：喚醒時機不確定、硬體時鐘解析度。解決：1) 改用 Advanced SpinUntil；2) 或用 while(elapsed<idle) Sleep(0)；3) 減少噪音執行緒。預防：避免長時間 Sleep 精準控制。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q6, C-Q7

D-Q4: SpinUntil 時間偏長怎麼辦？
- A簡: timeout 版本有固定開銷，改用回呼條件搭配 Stopwatch。
- A詳: 症狀：設定 10ms，實測 23–26ms。原因：委派多次評估、自旋策略成本、timeout 僅上限。解決：SpinWait.SpinUntil(()=>timer.Elapsed>idle)。預防：避免使用 timeout 參數；重用委派降低分配。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q7, C-Q4

D-Q5: 高負載下曲線崩壞的原因與對策？
- A簡: 時間片爭用導致飄移，調大 unit、提高優先權、降噪音。
- A詳: 症狀：峰谷錯位、波形失真。原因：與多程式競爭、上下文切換密集。解決：1) unit 增大至 150–200ms；2) 提升進程優先權；3) 減少背景負載或離峰時段測試。預防：在隔離環境測試與監控標準差。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, C-Q1, C-Q6

D-Q6: 單位（unit）過小導致抖動怎麼辦？
- A簡: 提高 unit 長度（如 100ms 以上），降低對雜訊敏感度。
- A詳: 症狀：曲線抖動劇烈。原因：小 unit 對微小延遲非常敏感。解決：把 unit 調大、平衡解析度與穩定性；配合 PerfMon 取樣間隔。預防：根據觀測工具與硬體特性設定 unit。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q11, C-Q6

D-Q7: Stopwatch 不準或受限頻影響？
- A簡: 檢查高解析度、開啟高效能電源、避免限頻。
- A詳: 症狀：計時抖動或跳動。原因：非高解析度來源、CPU 降頻/省電模式。解決：Stopwatch.IsHighResolution 應為真；電源計畫高效能；固定最大/最小處理器狀態。預防：測試前穩定硬體時鐘與頻率。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, C-Q1

D-Q8: 多執行緒太多導致過載與失真？
- A簡: 限制執行緒數≤邏輯核心，避免過度競爭。
- A詳: 症狀：曲線雜亂、CPU 上下翻飛。原因：超額執行緒互搶時間片。解決：設定 N=ProcessorCount 或以下；必要時設定親和性分配。預防：根据目標使用率與環境先估算所需執行緒。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q5, B-Q9

D-Q9: 虛擬機與主機結果不同？
- A簡: Hypervisor 排程與計時虛擬化差異，導致觀測偏差。
- A詳: 症狀：相同程式在 VM 與宿主曲線不同。原因：虛擬化層分配 CPU 與時鐘方式不同。解決：固定 vCPU 數（1 核）、盡量獨占主機核心、關閉 VM 背景任務。預防：在目標部署型態上實測與校正。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q1, A-Q6

D-Q10: PerfMon 與工作管理員顯示不一致？
- A簡: 取樣間隔與平滑策略不同，需統一設定。
- A詳: 症狀：兩者曲線相位/幅度不一。原因：取樣窗口、平滑與類別不同。解決：在 PerfMon 設相同取樣間隔（如 1s），選 Processor(_Total)\% Processor Time；同時觀測 Process\% Processor Time。預防：統一工具與設定再比較。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q10, B-Q11

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是「用 CPU utilization 畫出正弦波」？
    - A-Q2: 為什麼要將 sin(x) 位移與縮放為 f(x)=(sin x + 1)/2？
    - A-Q3: 什麼是 Busy Waiting（忙等）？
    - A-Q7: 為什麼要把時間切成固定單位（如 100ms）？
    - A-Q5: 「精確度」與「精密度」有何不同？
    - A-Q10: 為什麼要預先計算查表（Lookup Table）？
    - B-Q1: CPU 利用率如何由忙/閒比例決定？
    - B-Q2: 數學函數如何映射為忙/閒時間？
    - B-Q11: 時間單位（unit）選擇的取捨？
    - B-Q12: Stopwatch 的角色與原理？
    - C-Q2: 如何用 C# 基本實作忙/閒控制迴圈？
    - C-Q3: 如何實作 sin 查表法提升效能？
    - C-Q10: 如何觀測與記錄波形結果？
    - D-Q6: 單位（unit）過小導致抖動怎麼辦？
    - D-Q10: PerfMon 與工作管理員顯示不一致？

- 中級者：建議學習哪 20 題
    - A-Q4: SpinWait 與 Thread.Sleep 有何差異？
    - A-Q6: 多核心為何會影響 CPU 使用率控制？
    - A-Q8: 為什麼 Thread.Sleep 不適用於高精密時間控制？
    - A-Q12: 什麼是 Advanced Sleep 與 Advanced SpinUntil？
    - A-Q13: 為什麼要最小化程式自身的干擾？
    - A-Q14: 為什麼 idle 段也會被系統干擾？
    - A-Q15: 為什麼可用 ASCII Art 畫任意圖形？
    - B-Q3: 程式架構與執行流程為何？
    - B-Q4: Thread.Sleep 與 SpinWait 的計時機制差異？
    - B-Q5: 為何 SpinUntil 的 timeout 造成固定延遲？
    - B-Q6: Advanced Sleep 的機制與流程？
    - B-Q7: Advanced SpinUntil 的機制與流程？
    - B-Q8: 如何量化準確度與精密度？
    - B-Q9: 背景干擾（noise threads）如何影響？
    - B-Q13: 如何避免時間累積誤差（漂移）？
    - B-Q14: 任意圖形如何映射到 CPU 載入？
    - C-Q4: 如何使用 Advanced SpinUntil 控制 idle？
    - C-Q5: 如何以多執行緒填滿多核心？
    - C-Q6: 如何調整 unit 與 period 以優化波形？
    - C-Q7: 如何測試 Sleep 與 SpinUntil 的計時精度？

- 高級者：建議關注哪 15 題
    - B-Q5: 為何 SpinUntil 的 timeout 造成固定延遲？
    - B-Q7: Advanced SpinUntil 的機制與流程？
    - B-Q8: 如何量化準確度與精密度？
    - B-Q9: 背景干擾（noise threads）如何影響？
    - B-Q10: SpinWait 在單核/多核/超執行緒的行為？
    - B-Q13: 如何避免時間累積誤差（漂移）？
    - B-Q14: 任意圖形如何映射到 CPU 載入？
    - C-Q8: 如何將 ASCII Art 轉為負載表？
    - C-Q9: 如何用 offset 對齊避免時間漂移？
    - C-Q1: 如何建立最小干擾的執行環境？
    - D-Q1: 波形雜訊大、曲線不平滑怎麼辦？
    - D-Q2: 忙等僅顯示 12.5%（8 執行緒 CPU）怎麼辦？
    - D-Q3: Thread.Sleep 漂移嚴重如何處理？
    - D-Q4: SpinUntil 時間偏長怎麼辦？
    - D-Q5: 高負載下曲線崩壞的原因與對策？