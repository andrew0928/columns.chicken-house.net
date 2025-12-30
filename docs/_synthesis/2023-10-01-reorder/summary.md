---
layout: synthesis
title: "架構面試題 #5: Re-Order Messages"
synthesis_type: summary
source_post: /2023/10/01/reorder/
redirect_from:
  - /2023/10/01/reorder/summary/
---

# 架構面試題 #5: Re-Order Messages

## 摘要提示
- 順序處理問題: API 在高併發下需保障訊息按序處理，無法事後整批排序，只能串流中即時修正。
- 訊息可排序性: 訊息需內含可判斷先後與缺漏的欄位（如 sequence、timestamp）。
- 緩衝取捨: 需定義時間與空間的緩衝範圍，延遲與丟棄之間必須權衡。
- 核心介面: 以 IReOrderBuffer 管理 Push/Flush 與 SEND/DROP/SKIP 三類事件。
- 驅動邏輯: Push 為主引擎，先送可直通的，再以 buffer 補齊連續段並送出，不足時觸發 Skip。
- 資料結構: 使用 SortedSet 依 Position 排序搭配 _current_next_index 追蹤下一期待序號。
- 監控設計: 建立 Push/Send/Drop/Skip/BufferMax/Delay 指標，秒級統計輸出 CSV 觀察。
- 環境模擬: 模擬隨機延遲與丟包，驗證演算法在不同 period/noise/buffer 下的表現。
- 參數權衡: Buffer 不一定越大越好；過大會拉高延遲，過小會上升 Drop。
- 改善方向: 加入 timer/timeout 以 SLO 為中心主動 Skip/Drop，兼顧延遲上限與完整性。

## 全文重點
本文聚焦在「串流中維持訊息順序」的實作思路：當請求以非序抵達且需要盡快處理時，無法等資料收齊再排序，只能邊收邊判斷。作者以 TCP 的排序/重送概念為靈感，建構出 ReOrder Buffer 的模型，重點是：訊息本身要能被排序（sequence/timestamp），並明確界定緩衝的時間與空間界限，才能在延遲與完整性之間進行工程化取捨。

系統設計由四個部件構成：Command Source（模擬亂序輸入與延遲/丟失）、ReOrder Buffer（重排引擎）、Command Handler（按序執行）、Metrics（監控）。核心介面 IReOrderBuffer 提供 Push/Flush 與三類事件：CommandIsReadyToSend（可執行）、CommandWasDroped（已收但放棄）、CommandWasSkipped（未收但判定略過）。設計上，以 SortedSet 儲存暫存訊息並依 Position 排序，搭配 _current_next_index 追蹤下一期待序號；Push 的流程是：若收到剛好是下一個則直通送出（SEND_PASSTHRU），否則先入 buffer，並嘗試把可形成連續區間的訊息一次送出（SEND_BUFFERED）。當 buffer 超過上限且前一號碼尚未到，觸發 Skip 略過未收到的序號以釋放後續訊息；Flush 則在資料源結束時清算剩餘訊息，對尚未收到的序號進行 Skip，並送出可用訊息。

作者以單元測試和環境模擬驗證演算法：調整 command_period（訊息產生週期）、command_noise（隨機延遲）、buffer_size（緩衝容量），觀察 Drop、Max/Avg Delay、Buffer Usage 等監控指標。結果顯示：buffer 並非越大越好；若網路丟包存在，過大 buffer 會使後續訊息無謂等待而拉高延遲；過小 buffer 則無法等待足夠的序號補齊而增加 Drop。以固定 period/noise 為例，buffer=10 時 Max Delay 可破 1.2s；降到 5 反而延遲大幅降低；降到 3 以下 Drop 開始上升（至 buffer=1 時 Drop 達 14%）。因此，合適的 buffer 應以 SLO 為中心，在可接受延遲上限與訊息完整性間取得平衡。

進一步的改良是引入以時間驅動的輔助引擎（timer/timeout）：當沒有新 Push 觸發時也能主動決策 Skip/Drop，確保延遲上限可控。作者強調，這類架構練習不在於「重造輪子」，而是理解機制、能以 PoC 建模、模擬與監控，快速在 Dev（演算法與介面）與 Ops（指標與行為）兩端驗證決策，將風險前移。全文示範了如何以小規模可重現的程式與度量，提早發現瓶頸、制定 SLO，並讓後續團隊能自信地實作上線。

## 段落重點
### 練習前的思考: 我需要了解這些機制嗎?
作者主張不必重造所有輪子，但需具備理解原理與在必要時自製關鍵輪子的能力。透過小成本的練習與 PoC，可掌握跨系統整合的關鍵技術，並在面對複雜需求時快速做出技術決策。此題目即以 TCP 排序與 QoS 思維為基礎，讓讀者理解在必要時如何自行處理串流中的訊息順序問題。

### 1. 訊息排序的基本觀念
串流排序不同於批次排序：收到就得決策。若順序正確立即處理；若錯亂，短暫緩衝等待缺失訊息或選擇放棄。關鍵在於訊息可判定先後與缺漏（sequence/timestamp）、並設定時間與空間的緩衝界限（SLO）。整體流程以 buffer 暫存不連續項，待成為連續序列時批次送出；當緩衝耗盡或等待超時則必須明確 Skip/Drop，並把狀態傳遞給下一階段。

### 1-1, 訊息來源 ( GetCommands )
定義 OrderedCommand（Position/Origin/OccurAt/Message），以可重現的亂數產生器模擬序列在傳輸中引入的延遲與亂序，並以 OccurAt 排序輸出，逼迫後端重排。此處亦可注入丟包情境，以檢驗演算法在資料缺失下的決策品質。

### 1-2, 重整訊息順序 ( IReOrderBuffer )
IReOrderBuffer 定義 Push/Flush 與三種事件：CommandIsReadyToSend（可執行）、CommandWasDroped（收到了但丟棄）、CommandWasSkipped（未收到而略過）。Push 是主要入口：每進一筆即判斷是否直通送出或進 buffer，並觸發後續可連續的批次送出；Flush 負責收尾結算。

### 1-3, 處理訊息 ( ExecuteCommand )
Handler 僅驗證收到的 Position 必須嚴格遞增，確保 buffer 已提供正確序列。跳號不視為錯誤（可能真丟包），以符合「在順序正確的前提下持續前進」的要求，避免阻塞。

### 1-4, 監控運作狀態 ( Metrics )
設計秒級監控：Push/Send/Drop/Skip、Buffer Usage（最大暫存量）、Buffer Delay（因緩衝造成延遲）。用簡單 CSV（stderr）輸出，便於以 Excel/圖表快速觀察行為，驗證設計指標是否能反映真實狀況，並為日後接入監控平台鋪路。

### 1-5, 牛刀小試
以單元測試先行驗證：在局部亂序（如 0,1,2,3,5,4,6…）時，ReOrderBuffer 能將 #4 暫存並在時機成熟時與 #5 一併送出；事件紀錄會標示 SEND_PASSTHRU 與 SEND_BUFFERED，並可觀察平均延遲與 Buffer Usage。TDD 驗證核心規則後再擴展情境。

### 2. 環境模擬
將 period/noise/loss 等外部條件抽象化，建立可重現的實驗環境；結合 ReOrderBuffer 與 Handler，形成可觀察的閉環系統。以 DateTime Mock 壓縮時間推進，並以每秒事件回報 metrics，讓模擬在單機中快速反覆執行。

### 2-1. 模擬網路傳輸延遲 (隨機)
以 period 控制產生頻率、noise 控制延遲上限（0~noise ms）；越小的 period 與越大的 noise 越容易形成亂序，進而需要更大的 buffer 與更精準的決策。用固定亂數種子確保結果可重現，便於比較不同參數下的影響。

### 2-2. 模擬網路傳輸丟失請求
注入固定機率的丟包，測試「等不到的序號」如何處置。當 buffer 充足時，可能拖延大量後續訊息；當 buffer 緊縮時，會更早 Skip 缺失序號，提前釋出後續訊息。從指標比較可見延遲與 Skip/Drop 的此消彼長。

### 2-3. 用 Buffer 串接來源與目的地
示範整合：訂閱事件、逐筆 Push 來源命令、最後 Flush 收尾。整個系統由 Push 驅動，事件鏈貫通 Source → Buffer → Handler。此結構貼近真實線上處理模式，便於逐步引入更多約束（如超時）。

### 2-4. 模擬監控機制
以秒級 ResetMetrics 收斂統計，再以 CSV 管線導出，快速建立觀察面板。此做法能在 PoC 期模擬日後的 dashboard，提前驗證指標是否足夠診斷、是否能支撐決策與告警，降低上線後的維運風險。

### 3. Reordering Buffer 的設計
設計重點：介面與事件先行（Contract First），再落地資料結構與 Push 核心邏輯。先標定範圍（不做重送、精準計時與過期處理），集中處理重排、Buffer 限制與處置策略，確保可用最小解運作並可後續擴充。

### 3-1, 用 Buffer 來 Re-Order Command 的規則
規則直觀：直通可連續的序號；對後到的較大序號先暫存；當缺失序號補到時，將連續區段批次送出。以具體案例（#1,#3,#4,#2…）呈現時間序下的 Push/Execute/Buffered 狀態轉移，對照事件輸出確認正確性。

### 3-2, Buffer Size 越大越好嗎?
以兩案例對比：buffer=100 對缺 #5 情境導致大量延遲累積；buffer=3 則較早 Skip，整體延遲顯著下降。結論：buffer 過大未必好，若存在丟包會徒增等待；需以 SLO（延遲上限/完整性）決定最合適的容量。

### 3-3. 資料結構
以 _current_next_index 追蹤下一期待序號，並用 SortedSet 儲存暫存命令（依 Position 排序，避免重複）。此結構在 Push 時能快速判斷是否可連續送出、或需繼續暫存；也為未來加入集合運算（如濾除已 Skip 範圍）留擴充空間。

### 3-4, 監控指標 Metrics
六項核心：push/send/drop/skip/buffer_max/total_delay。以 Interlocked.Exchange 實作 ResetMetrics，確保擷取時一致性，並為日後搬到外部存儲（如 Redis GETSET）提供對應實作思路。這些指標是調優與保證 SLO 的基礎。

### 3-5, Push() , 驅動 Buffer 運作的引擎
Push 流程：過號即 Drop；等號直通送出、遞增期待序號；其餘入 buffer。之後迭代：若 buffer 超限且期待序號小於 buffer 最小序號，則 Skip 期待序號並遞增；再檢查是否能從最小序號開始連續送出（SEND_BUFFERED）。Flush 負責結算：能送的送、其餘 Skip。

### 3-6, Adapters 串聯事件機制
Send/Drop/Skip 統一封裝：更新對應 metrics、發出事件，讓外界（Handler 或下游）接收與記錄。這層確保行為一致、易於替換或串接外部系統（如寫入支援 FIFO 的 MQ）。

### 3-7. DateTime Mock
以 DateTimeUtil 模擬時間軸與秒級事件，避免依賴系統時間與 Sleep。可控「現在」與加速時間推進，讓模擬高效且可重現，並保障計時行為（timer/metrics）在 PoC 階段能被真實驗證。

### 4. 模擬與監控
將三個外部參數（period/noise/loss）與一個內部限制（buffer_size）組合測試，觀察 Drop/Max Delay/Buffer Usage 等指標變化。以 CSV 匯出、Excel 繪圖快速定位瓶頸，建立以數據導向的調參與決策模式。

### 4-1, 模擬測試 (100, 500, 10)
buffer=10 且 noise=500 下：Drop=0，但 Max Delay 可超過 1.2s。分析顯示：平時亂序修正延遲<100ms；遇丟包則因等待缺號導致延遲尖峰（peak）。驗證過大 buffer 在丟包場景下會擴大延遲尾部。

### 4-2, 模擬測試 (100, 100, 10)
noise 降為 100：平均延遲下降、亂序修正的低延遲段幾近消失，剩下丟包導致的尖峰，顯示網路品質改善對重排負擔與延遲具正向效果。

### 4-3, 模擬測試 (100, 500, 5 ~ 1)
逐步縮小 buffer：5 時大幅降低 Max Delay 且無 Drop；3 時 Drop 開始出現（約 0.2%）；2 時 Drop 3%；1 時 Drop 高達 14%。得出折衷：在該網路品質下 buffer≈5 較合適，能控延遲又避免資料損失。

### 4-4, 改善
缺口在於「時間驅動」：當無新 Push 時也要能依 SLO 主動 Skip/Drop（timeout）以控制延遲上限。加入高精度 timer 與超時策略後，方可放心擴大 buffer 應對瞬態變動，同時保障延遲與完整性。此為最終走向的設計。

### 5, 總結
本例以模型+模擬落實 Dev 與 Ops 一體思維：先以介面與演算法確立可運轉的最小解，再以可重現的環境與指標觀察驗證可上線性。架構師需能在早期用小成本 PoC 驗證方案，將風險前移；並以 SLO 為中心，在延遲與完整性間找到工程化的最佳點，最後交付團隊落實生產級實作與監控。

## 資訊整理

### 知識架構圖
1. 前置知識
- 網路通訊基礎：TCP/UDP、封包順序與重送概念
- 資料結構與演算法：序號、排序、Set/SortedSet、緩衝區策略
- 分散式事件處理：事件順序、丟包、亂序、因果順序
- 服務 SLO/SLA 概念：延遲、丟失率、吞吐量與取捨
- 基礎工程實務：Unit Test、TDD、Metrics/監控、POC/模擬、C# 語言與事件模型

2. 核心概念
- 訊息可排序性：以 Position/Sequence 或來源時間戳記能判斷先後與缺漏
- 緩衝重排(Re-Order Buffer)：以有限時間/空間暫存亂序訊息，連續即可釋出
- 決策機制：在延遲與丟棄(SKIP/DROP)間做 SLO 驅動的取捨
- 觀測性與指標：Push/Send/Drop/Skip、Buffer Usage、Delay/Max Delay
- 模擬與驗證：以可控的 period/noise/lost-rate 驅動模型，據實驗修正設計

3. 技術依賴
- 訊息模型 OrderedCommand(Position, Origin, OccurAt, Message)
- ReOrderBuffer 介面與事件(IReOrderBuffer: Push/Flush + SEND/DROP/SKIP events)
- 資料結構：SortedSet<OrderdCommand> + IComparer 按 Position 排序
- 引擎驅動：Push 為主迴圈，Flush 為清算；Timer/Timeout 為進階(可主動 Skip/Drop)
- 監控機制：每秒 ResetMetrics 輸出 CSV，外部以 Excel/Dashboard 觀測
- 測試設計：Unit Tests 驗證順序、丟包與緩衝大小情境

4. 應用場景
- 需要順序一致性的交易/事件處理(財務轉帳、指令流)
- 微服務事件匯流排：分割槽內有序、跨服務重排
- 物聯網/遙測資料流：網路抖動與亂序修正
- 日誌/稽核流水處理：在可控延遲內維持事件順序
- 實時控制/遊戲狀態同步：在丟包與延遲間的最佳化取捨

### 學習路徑建議
1. 入門者路徑
- 了解 TCP 與 UDP 在順序/重送的差異與原理
- 實作簡單 OrderedCommand 與 IReOrderBuffer 介面骨架
- 用最小案例(Unit Test)驗證簡單亂序(#3 先到、#2 後到)能重排成功
- 讀懂基本 Metrics：Push/Send、Buffer Usage、Delay

2. 進階者路徑
- 導入丟包情境與 Buffer Size 限制，觀察 Drop/Skip 差異與臨界行為
- 新增 Timeout/Timer 機制：無 Push 時也能依 SLO 主動 Skip/Drop
- 處理重送/重複訊息去重與已跳過段落的快速前跳
- 以持久化緩衝(檔案/Redis/Kafka local state)提升可靠度與重啟復原

3. 實戰路徑
- 與 MQ/Kafka 整合：以 key 保序(partition) + 本地重排補強
- 以真實監控堆疊(Prometheus/Grafana/ELK)替換 CSV，設計 SLO 看板
- 以混沌測試/網路模擬(tc/netem)打噪音，跑負載與延遲曲線
- 制定營運策略：在 Drop Rate 與 Max Delay 的 SLO 下自動調整 Buffer/Timeout

### 關鍵要點清單
- 訊息可排序性：訊息需帶 Position/Sequence 或等價標記，能判斷先後與缺漏 (優先級: 高)
- 緩衝時間/空間界線：明確定義等待多久、暫存多少，避免無限等待與資源耗盡 (優先級: 高)
- Push 驅動引擎：每次 Push 觸發送出或暫存與連續段釋放，是核心運作點 (優先級: 高)
- Flush 清算：序列結束或收束時清理 Buffer，對未到達者進行 Skip/Drop (優先級: 高)
- Skip vs Drop：Skip 代表未收到但決定略過；Drop 代表已收到但放棄，兩者分流度量 (優先級: 高)
- Metrics 設計：Push/Send/Drop/Skip、Buffer Usage、平均/最大 Delay 是優化依據 (優先級: 高)
- SLO 駕馭的取捨：延遲越小通常丟棄越多，須依商業目標權衡 (優先級: 高)
- Buffer Size 非越大越好：過大會放大延遲峰值；需結合超時策略取得平衡 (優先級: 高)
- Timer/Timeout 機制：在無新訊息時也能依時間邊界主動決策，限制最長等待 (優先級: 高)
- 單元測試情境：亂序、缺漏、緩衝極限構成最小驗證面，驅動正確性 (優先級: 中)
- 資料結構選擇：SortedSet + IComparer 便於按 Position 排序與取最小值 (優先級: 中)
- 監控與輸出管線：以 CSV/StdErr 快速搭建觀測，後續替換為正式監控 (優先級: 中)
- 模擬環境參數：command_period/noise/lost-rate 幫助重現真實網路狀態 (優先級: 中)
- 去重與已跳過段處理：未來需處理重送與跳號後的狀態一致性 (優先級: 中)
- 持久化與恢復：實務上需面對重啟/故障，緩衝需可持久化並可恢復 (優先級: 低)