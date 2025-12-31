---
layout: synthesis
title: "架構面試題 #5: Re-Order Messages"
synthesis_type: solution
source_post: /2023/10/01/reorder/
redirect_from:
  - /2023/10/01/reorder/solution/
postid: 2023-10-01-reorder
---

以下內容基於原文抽取與重組，整理出可用於實戰教學、專案演練與能力評估的 17 個完整案例。每一個案例都涵蓋問題、根因、解法（含程式碼/流程）、實測數據、學習與練習、評估標準，並在最後提供分類與學習路徑建議。

## Case #1: 高併發 API 訊息順序保證的基線設計（ReOrder Buffer）

### Problem Statement（問題陳述）
業務場景：在短時間收到大量 API 請求（近即時處理），業務規則要求指令必須依序執行（例如：交易流水、帳戶變更、補償動作），但實際接收順序會受網路抖動影響，甚至先到後發。服務端需要在「盡快處理」與「維持正確順序」間取得平衡，且不可等待全量資料再排序（非離線批次），屬於串流場景。

技術挑戰：即時流無法等待完整排序；需能識別先後與掉號，並在有限緩衝空間/時間內完成重排；且要可觀測（Metrics）以便調參與 SLO 對齊。

影響範圍：若錯序執行將導致資料不一致、資金/庫存錯誤；若延遲過高或過久等待會造成 SLA 失敗與用戶體感下降；工程上難以測試與監控。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 網路延遲與抖動造成到達順序不同（OccurAt 非均值、非序）  
2. 訊息未攜帶足夠順序資訊（無 Position/Sequence、無時間戳）  
3. 直接丟入不保序的 MQ 導致順序更亂

深層原因：
- 架構層面：將串流排序需求交由非保序元件處理，缺少專責中介（ReOrder Buffer）
- 技術層面：缺乏順序欄位設計與事件驅動介面，導致處理耦合
- 流程層面：未建立度量指標與驗證流程，無法以數據調參

### Solution Design（解決方案設計）
解決策略：以 IReOrderBuffer 為中心的事件驅動重排器。訊息需包含 Position、Origin、OccurAt 等欄位以支援排序與掉號判定。Push() 為主要引擎，配合 Buffer（有上限）與 Flush() 結束清算，提供 SEND、DROP、SKIP 事件，並以 Metrics 監控 push/send/drop/skip/delay/usage。

實施步驟：
1. 資料模型與介面定義  
- 實作細節：定義 OrderedCommand（Position/Origin/OccurAt/Message）與 IReOrderBuffer 介面  
- 所需資源：.NET 6/7、C#  
- 預估時間：0.5 天

2. Push 引擎與事件對接  
- 實作細節：實作 SortedSet + IComparer；Push 驅動 SEND_PASSTHRU/SEND_BUFFERED/SKIP/DROP；連接 ExecuteCommand  
- 所需資源：.NET、單元測試框架（MSTest/xUnit）  
- 預估時間：1 天

3. Metrics 與觀測  
- 實作細節：Interlocked 計數、ResetMetrics，CSV 以 STDERR 導出  
- 所需資源：.NET、Excel 或其他繪圖工具  
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
public class OrderedCommand {
    public int Position;
    public DateTime Origin;
    public DateTime OccurAt;
    public string Message;
}

public interface IReOrderBuffer {
    bool Push(OrderedCommand data);
    bool Flush();
    event CommandProcessEventHandler CommandIsReadyToSend;
    event CommandProcessEventHandler CommandWasDroped;
    event CommandSkipEventHandler CommandWasSkipped;
}

static bool ExecuteCommand(OrderedCommand cmd) {
    // 確保不倒退
    // 略: 以 _last_command_position 驗證
    return true;
}
```

實際案例：BasicScenario2_OutOfOrderCommand（#4 與 #5 對調）  
實作環境：C#/.NET、Windows/Linux、MSTest  
實測數據：  
改善前：無序處理、不可觀測  
改善後：PUSH=11、SEND=11、DROP=0、SKIP=0、Command Delay=0.132ms、Buffer Usage=1  
改善幅度：從不可觀測到全面可觀測；正確順序率達 100%

Learning Points（學習要點）
核心知識點：
- 串流重排與有界緩衝
- 事件驅動設計（SEND/DROP/SKIP）
- 順序欄位與掉號檢測

技能要求：
- 必備技能：C#、集合結構、事件處理
- 進階技能：並行控制、SLO 與可觀測性設計

延伸思考：
- 也可轉發到支援 FIFO 的 MQ
- 漏斗效應（延遲高峰）與緩衝策略
- 如何以時間上限驅動主動 SKIP

Practice Exercise（練習題）
- 基礎練習：實作 IReOrderBuffer 事件接線，透過單元測試驗證順序（30 分鐘）
- 進階練習：加入隨機延遲模擬，觀察 Buffer Usage 與 Delay（2 小時）
- 專案練習：完成 CLI + CSV Metrics + Excel 圖表分析（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：事件正確、順序保證、Flush 清算
- 程式碼品質（30%）：結構清晰、單元測試齊全
- 效能優化（20%）：Push/Send O(logN) 操作、無多餘掃描
- 創新性（10%）：指標設計、可插拔 Handler

---

## Case #2: 訊息結構缺失導致無法判斷先後的重構

### Problem Statement（問題陳述）
業務場景：多來源服務透過 MQ/API 併發傳遞指令，現況只有 payload 無序號/時間戳，導致消費端無法判斷誰先誰後、是否掉號。業務端要求交易必須按原始順序處理，但現有結構無法保證。

技術挑戰：無序號即無法檢測漏失與相對順序；外部時鐘不一致時也需能靠來源時間/流水號判定。

影響範圍：無法自動修正順序；出錯時需人工排查；最終一致性難以收斂。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 訊息缺乏 Position/Sequence 欄位  
2. 無 Origin/OccurAt 時間資訊，無法區分產生與到達  
3. 消費端缺乏檢測掉號與重排的依據

深層原因：
- 架構層面：資料契約（Schema）未包含執行必要上下文
- 技術層面：傳遞協定與資料模型設計不足
- 流程層面：缺乏 Contract First 與測試規範

### Solution Design（解決方案設計）
解決策略：採用 OrderedCommand 資料模型，最少包含 Position、Origin、OccurAt，以支持掉號、錯序偵測與重排；以 IReOrderBuffer 推進處理。

實施步驟：
1. 定義資料契約  
- 實作細節：訂定 Position（連續）、Origin、OccurAt 欄位  
- 所需資源：C#、契約文件  
- 預估時間：0.5 天

2. 改造生產與消費端  
- 實作細節：生產端填入欄位；消費端接 IReOrderBuffer  
- 所需資源：服務端與客戶端程式碼  
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
public class OrderedCommand {
    public int Position;        // 0..N 連續
    public DateTime Origin;     // 產生時刻
    public DateTime OccurAt;    // 接收時刻
    public string Message;
}
```

實際案例：BasicScenario5_LostCommand（用 Position 判斷 #5 掉號）  
實作環境：C#/.NET  
實測數據：  
改善前：無法判斷掉號與順序  
改善後：SKIP=1 可被正確記錄；PUSH=10、SEND=10、DROP=0、Buffer Usage=5  
改善幅度：可觀測性從 0 提升至完整可監控

Learning Points（學習要點）
- 順序欄位是串流重排的根基
- 來源時間與到達時間的意義
- 合約先行（Contract First）提升可演練性

技能要求：
- 必備技能：資料模型設計
- 進階技能：跨系統契約治理

延伸思考：
- 需不要加入分片鍵（按業務 key 保序）？
- 來源時鐘漂移如何處理？

Practice Exercise
- 基礎：將既有 payload 加上 Position/Origin/OccurAt（30 分鐘）
- 進階：以不同來源模擬時鐘差並觀察結果（2 小時）
- 專案：撰寫契約測試確保欄位完整性（8 小時）

Assessment Criteria
- 功能完整性：欄位齊備、可解析
- 程式碼品質：型別與驗證
- 效能優化：欄位轉換最小化
- 創新性：契約演化策略

---

## Case #3: 串流重排演算法（即時而非全量排序）

### Problem Statement（問題陳述）
業務場景：指令連續流入，但不能等全量再排序；一邊接收、一邊按順序處理。需支援先收後發、後收先發等情況，並在條件滿足時立刻釋放。

技術挑戰：如何在任意亂序情境下，用有限 Buffer 完成最小延遲的重排與連續釋放。

影響範圍：延遲、吞吐、錯序風險、資源佔用。

複雜度評級：中

### Root Cause Analysis
直接原因：
1. 到達排序（OccurAt）與原始排序（Position）不一致  
2. 減少等待時間與維持連續性互相拉扯  
3. 無事件驅動，無法即時釋放可連續段

深層原因：
- 架構層面：未設計「連續段檢測」與「窗口」概念
- 技術層面：資料結構與判斷邏輯不足
- 流程層面：缺乏 TDD 驗證典型亂序情境

### Solution Design
解決策略：以 Push 為引擎，維護 current_next_index 與 SortedSet；每次 Push 後，在可連續段（buffer.Min.Position == current_next_index）時連續 SEND_BUFFERED；當新到達剛好是下一個，SEND_PASSTHRU。

實施步驟：
1. 建立 current_next_index 與 SortedSet  
- 實作細節：用 IComparer 以 Position 排序  
- 所需資源：.NET  
- 預估時間：0.5 天

2. 連續段釋放邏輯  
- 實作細節：while buffer.Min == next -> pop + send  
- 所需資源：單元測試  
- 預估時間：0.5 天

關鍵程式碼：
```csharp
if (data.Position == _current_next_index) {
    Send(data, SEND_PASSTHRU);
    _current_next_index++;
}
do {
    while (_buffer.Count > 0 && _current_next_index == _buffer.Min.Position) {
        var m = _buffer.Min;
        _buffer.Remove(m);
        Send(m, SEND_BUFFERED);
        _current_next_index++;
    }
} while (_buffer.Count > _buffer_size);
```

實際案例：BasicScenario14/15（#3、#4 先入 Buffer，#2 到後連續釋放）  
實作環境：C#/.NET、MSTest  
實測數據：  
改善前：需等待全量排序（高延遲）  
改善後：即時釋放；PUSH 全部成功；DROP=0；SKIP=0；Buffer 僅暫存必要數量  
改善幅度：延遲顯著低於全量排序（以 SEND_PASSTHRU 為主）

Learning Points
- 連續段檢測、窗口推進
- PASSTHRU vs BUFFERED 行為
- 事件驅動與 while 釋放

技能要求
- 必備：集合操作與比較器
- 進階：滑動窗口（sliding window）思路

延伸思考
- 可加入時間窗口限制
- 對齊 TCP 重排思路

Practice Exercise
- 基礎：完成 while 釋放連續段（30 分鐘）
- 進階：加入更多亂序測試（2 小時）
- 專案：以隨機流量壓測觀察延遲分布（8 小時）

Assessment Criteria
- 功能完整性：連續釋放正確
- 程式碼品質：簡潔、測試覆蓋
- 效能優化：避免線性掃描
- 創新性：窗口策略

---

## Case #4: 處理訊息遺失的策略（SKIP）與 Flush 清算

### Problem Statement
業務場景：串流中偶發掉封包（某 Position 永遠不會到），不能無限等待；需在條件滿足時跳過未收到的序號，釋放後續已收到的指令；在串流結束需做最後清算。

技術挑戰：如何區分「暫時未到」與「真的不會到」？何時 SKIP？串流結束如何收斂？

影響範圍：延遲、可用性、資料完整性（不得錯序）

複雜度評級：中

### Root Cause Analysis
直接原因：
1. 傳輸不可靠導致遺失  
2. 無時間/空間界限的等待會阻塞  
3. 串流結束時未清算會殘留

深層原因：
- 架構層面：無 Skip 與 Flush 機制
- 技術層面：缺少「Buffer 滿」或「超時」驅動
- 流程層面：缺少失敗情境測試

### Solution Design
解決策略：在 Push 期間以「Buffer 滿且下一個未到」觸發 SKIP；串流結束呼叫 Flush()，對 Buffer 中剩餘資料做 SEND 或 SKIP 清算，保證 pipeline 不殘留。

實施步驟：
1. Buffer 滿觸發 SKIP  
- 實作細節：if buffer.Count > size && next < buffer.Min.Position -> Skip(next)  
- 所需資源：.NET  
- 預估時間：0.5 天

2. Flush 清算  
- 實作細節：while buffer not empty -> 若命中 next 則 SEND_BUFFERED；否則 SKIP next  
- 所需資源：測試案例（掉 #5）  
- 預估時間：0.5 天

關鍵程式碼：
```csharp
if (_buffer.Count > _buffer_size && _current_next_index < _buffer.Min.Position) {
    Skip(_current_next_index, SKIP_BUFFERFULL);
    _current_next_index++;
}
...
bool IReOrderBuffer.Flush() {
    while(_buffer.Count > 0) {
        if (_current_next_index == _buffer.Min.Position) {
            var m = _buffer.Min; _buffer.Remove(m);
            Send(m, SEND_BUFFERED); _current_next_index++;
        } else {
            Drop(new OrderedCommand{ Position=_current_next_index }, SKIP_BUFFERFULL);
            _current_next_index++;
        }
    }
    return true;
}
```

實際案例：BasicScenario5_LostCommand（Buffer=100）與 Case13（Buffer=3）  
實作環境：C#/.NET、MSTest  
實測數據：  
- Case5（Buffer 100）：PUSH=10、SEND=10、DROP=0、SKIP=1、Max Delay=400.029ms、Avg Delay=100.021ms、Buffer Usage=5  
- Case13（Buffer 3）：PUSH=10、SEND=10、DROP=0、SKIP=1、Max Delay=300.300ms、Avg Delay=60.423ms、Buffer Usage=3  
改善幅度：在同一掉包情境下，較小 Buffer 提前 SKIP，Max Delay 降低約 25%

Learning Points
- SKIP 與 Flush 的分工（運行期 vs 結束清算）
- 空間界限策略替代時間界限
- 指標解讀（Max/Avg Delay、Buffer Usage）

技能要求
- 必備：條件觸發與事件處理
- 進階：Flush 一致性保障

延伸思考
- 加入時間界限（Timer）會更健壯
- SKIP 與 DROP 的下游語義差異

Practice Exercise
- 基礎：實作 Flush 清算（30 分鐘）
- 進階：在 Push 加入 Buffer 滿 SKIP（2 小時）
- 專案：以不同 Buffer 尺寸重跑測試並比較 Delay（8 小時）

Assessment Criteria
- 功能完整性：Flush 正確收斂
- 程式碼品質：條件清晰
- 效能優化：常數階與 O(logN)
- 創新性：SKIP 策略優化

---

## Case #5: 遲到/重複訊息的處理（DROP）避免錯序

### Problem Statement
業務場景：部分訊息延遲嚴重或重送產生重複，若仍執行將打破已建立的順序。需及時丟棄「已過號」或重複訊息（Position < current_next_index）。

技術挑戰：如何高效識別與丟棄？如何在可觀測性中區分 SKIP/DROP？

影響範圍：錯序執行風險、下游資料污染、回溯成本。

複雜度評級：低

### Root Cause Analysis
直接原因：
1. 非保序網路與重送  
2. 下游已執行至更高 Position  
3. 缺少防衛性邏輯導致錯序執行

深層原因：
- 架構層面：無過號防護
- 技術層面：無最小 Position 邏輯（current_next_index）
- 流程層面：無 DROP 監控指標

### Solution Design
解決策略：在 Push 入口以最小成本 Drop 過號訊息：Position < current_next_index 立即 DROP；統計 DROP 指標分離於 SKIP，便於調整 Buffer 與上游策略。

實施步驟：
1. 過號檢測與 DROP  
- 實作細節：Push 時先判斷 Position < current_next_index  
- 所需資源：.NET  
- 預估時間：0.25 天

2. 指標與事件  
- 實作細節：CommandWasDroped 與 metrics 增量  
- 所需資源：事件接線  
- 預估時間：0.25 天

關鍵程式碼：
```csharp
if (data.Position < _current_next_index) {
    Drop(data, DROP_OUTOFORDER);
    return false;
}
```

實際案例：多組模擬（Buffer 減小導致後續 DROP 增加）  
實作環境：C#/.NET  
實測數據：  
- Buffer=3：Drop=2（0.2%）  
- Buffer=2：Drop=36（3%）  
- Buffer=1：Drop=146（14%）  
改善幅度：加入過號 DROP 後，避免錯序執行（正確性 100%），以可觀測代價取代偽成功

Learning Points
- DROP 與 SKIP 的語意：已收到 vs 未收到
- 最小成本過號防護
- 指標驅動調參

技能要求
- 必備：防衛性編程
- 進階：指標設計與解讀

延伸思考
- 加入重複去重（dedup）機制
- DROP 是否要通報上游重送？

Practice Exercise
- 基礎：增加過號 DROP 判斷（30 分鐘）
- 進階：以不同 Buffer 尺寸觀察 DROP 變化（2 小時）
- 專案：設計 DROP 告警與自動調整（8 小時）

Assessment Criteria
- 功能完整性：過號必丟
- 程式碼品質：簡潔正確
- 效能優化：O(1) 檢查
- 創新性：DROP 策略擴展

---

## Case #6: 緩衝空間與延遲的取捨（選擇合適 Buffer Size）

### Problem Statement
業務場景：同一網路品質下（noise=500ms），Buffer 太大可能徒增延遲（等不到的號碼卡住），太小又導致 DROP 增加。需在 Drop Rate 與 Max Delay 間取得平衡（達成 SLO）。

技術挑戰：如何基於數據選擇合理 Buffer Size？

影響範圍：延遲尖峰（Max Delay）、丟棄率（Drop Rate）、可用性。

複雜度評級：中

### Root Cause Analysis
直接原因：
1. 大 Buffer 容易被「永不到號」長期卡住  
2. 小 Buffer 無法吸收亂序，導致 DROP  
3. 無量測→無法調參

深層原因：
- 架構層面：無 SLO 對齊、無調參策略
- 技術層面：缺乏 Metrics 與模擬
- 流程層面：未建立實驗方法

### Solution Design
解決策略：以 CSV 指標導出與 Excel 圖表分析，分別在 Buffer Size=10/5/3/2/1 下重跑，對比 Max Delay 與 Drop Rate，選擇最適策略（本文例：建議 ≥5）。

實施步驟：
1. 以批次腳本跑不同參數  
- 實作細節：cmd 批次 + 2> STDERR 導出 CSV  
- 所需資源：Windows cmd 或 Shell  
- 預估時間：0.5 天

2. 圖表分析與決策  
- 實作細節：Excel 作圖，關注 Max Delay、Drop  
- 所需資源：Excel 或繪圖程式  
- 預估時間：0.5 天

關鍵程式碼/設定：
```cmd
:: Usage: dotnet run {period} {noise} {buffer}
dotnet run 100 500 10 2> output\metrics-100-500-10.csv
dotnet run 100 500  5 2> output\metrics-100-500-05.csv
dotnet run 100 500  3 2> output\metrics-100-500-03.csv
dotnet run 100 500  2 2> output\metrics-100-500-02.csv
dotnet run 100 500  1 2> output\metrics-100-500-01.csv
```

實際案例：參照原文 4-3 組實驗  
實作環境：.NET、Windows cmd  
實測數據（Noise=500ms，Period=100ms）：  
- B=10：Drop=0、MaxDelay=1237.963ms  
- B=5：Drop=0、MaxDelay=777.193ms（較 B=10 降 37%）  
- B=3：Drop=2（0.2%）、MaxDelay=636.567ms  
- B=2：Drop=36（3%）、MaxDelay=425.002ms  
- B=1：Drop=146（14%）、MaxDelay=356.657ms  
改善幅度：建議 B=5（Drop=0 且 MaxDelay 較低），相對 B=10 延遲改善 37%

Learning Points
- 指標驅動的容量決策
- Max Delay 高峰多源於掉包串連
- 以數據換取業務 SLO 合意解

技能要求
- 必備：指標分析、批次腳本
- 進階：A/B 實驗設計與 SLO 對齊

延伸思考
- 不同業務可採不同分片 Buffer Size
- 結合時間上限將更穩健

Practice Exercise
- 基礎：跑兩組 Buffer 尺寸並比較（30 分鐘）
- 進階：加上不同 noise 比較（2 小時）
- 專案：整理報告與建議值（8 小時）

Assessment Criteria
- 功能完整性：實驗流程完整
- 程式碼品質：腳本清晰
- 效能優化：批次效率
- 創新性：參數尋優策略

---

## Case #7: 隨機延遲環境模擬（GetCommands 與可重現性）

### Problem Statement
業務場景：實際網路延遲不可控，需在 PoC 階段模擬各種隨機延遲、亂序情境以驗證設計；同時需要「重現性」以便反覆比較調參效果。

技術挑戰：如何隨機但可重現？如何模擬不同發送頻率與延遲噪音？

影響範圍：測試可靠性、決策正確性。

複雜度評級：低

### Root Cause Analysis
直接原因：
1. 無重現性導致測試對比失真  
2. 無延遲模型不易覆蓋問題情境  
3. 無法控制資料到達節奏

深層原因：
- 架構層面：缺乏模型驅動 PoC
- 技術層面：時間與亂數使用不當
- 流程層面：缺少基準實驗

### Solution Design
解決策略：GetCommands(period, noise) 以固定亂數種子產生 Position、Origin、OccurAt，OccurAt=Origin+Random(0..noise)，並以 OccurAt 排序後 yield。

實施步驟：
1. 固定亂數種子  
- 實作細節：Random(867)  
- 所需資源：.NET  
- 預估時間：0.25 天

2. 參數化 period/noise  
- 實作細節：CLI 傳入 period/noise  
- 所需資源：Program.cs 解析參數  
- 預估時間：0.25 天

關鍵程式碼：
```csharp
static IEnumerable<OrderedCommand> GetCommands(int period=100, int noise=500) {
    Random rnd = new Random(867);
    // 生成 Origin/OccurAt，按 OccurAt 排序後 yield
}
```

實際案例：多組 noise（100 vs 500）對延遲影響  
實作環境：C#/.NET  
實測數據：  
- Noise=500：Average Buffer Delay=104.525ms  
- Noise=100：Average Buffer Delay=52.932ms  
改善幅度：Avg Delay 降低約 49.4%

Learning Points
- 可重現性是調參的前提
- period/noise 對亂序與延遲的直接影響
- 模型化思維優於拍腦袋

技能要求
- 必備：隨機/時間模型
- 進階：高斯分布等更貼近現實的延遲模型

延伸思考
- 可加入突發抖動、尖峰延遲的混合模型
- 不同流量曲線（burst vs steady）

Practice Exercise
- 基礎：加上 CLI 支援（30 分鐘）
- 進階：嘗試高斯分布延遲（2 小時）
- 專案：建立多組場景矩陣批次執行（8 小時）

Assessment Criteria
- 功能完整性：可重現
- 程式碼品質：清晰參數化
- 效能優化：無阻塞產生
- 創新性：延遲模型設計

---

## Case #8: 傳輸丟失情境模擬與策略驗證

### Problem Statement
業務場景：偶發封包丟失（1%），需驗證重排器在遺失下的表現：是否會無限等待？是否能 SKIP 並釋放後續？

技術挑戰：模擬丟失、驗證 SKIP 與延遲影響。

影響範圍：可用性、Max Delay、完整性。

複雜度評級：低

### Root Cause Analysis
直接原因：
1. 傳輸層丟包  
2. 無丟失檢測與處理  
3. 無 Flush 清算

深層原因：
- 架構層面：缺 SKIP 與 Buffer 界限
- 技術層面：無丟失場景測試
- 流程層面：無指標監控

### Solution Design
解決策略：在 GetCommands 模擬 1% 隨機丟失；在 Push 過程以 Buffer 界限觸發 SKIP；Flush 時清算未收集完的段。

實施步驟：
1. 丟失模擬  
- 實作細節：if (rnd.Next(100)==0) continue  
- 所需資源：.NET  
- 預估時間：0.25 天

2. 驗證結果  
- 實作細節：觀察 SKIP 次數與 Max Delay 高峰  
- 所需資源：CSV/圖表  
- 預估時間：0.5 天

關鍵程式碼：
```csharp
// 1% lost rate
// if (rnd.Next(100) == 0) continue;
```

實際案例：BasicScenario5/13（#5 丟失）  
實作環境：C#/.NET  
實測數據：  
- Buffer=100：SKIP=1、Max Delay=400.029ms  
- Buffer=3：SKIP=1、Max Delay=300.300ms  
改善幅度：透過較小 Buffer 提前 SKIP，Max Delay 降低 25%

Learning Points
- 丟包導致延遲尖峰的連鎖效應
- SKIP 是遺失下維持流動性的關鍵

技能要求
- 必備：隨機事件模擬
- 進階：丟包率對 Drop/Delay 的影響模型

延伸思考
- 丟包率更高時的上限設計
- 需要重送/補償機制嗎？

Practice Exercise
- 基礎：開啟丟失模擬並觀察（30 分鐘）
- 進階：比較不同 Buffer 對 Max Delay 的影響（2 小時）
- 專案：在圖表中標註高峰點的根因（8 小時）

Assessment Criteria
- 功能完整性：丟失確實發生且被 SKIP
- 程式碼品質：隨機與可重現兼顧
- 效能優化：無多餘迴圈
- 創新性：丟失/延遲混合場景

---

## Case #9: 監控指標設計與蒐集（Interlocked + ResetMetrics）

### Problem Statement
業務場景：需要每秒觀測 push/send/drop/skip/buffer_max/delay 等指標，並以圖表監控，支援快速迭代與上線前驗證。

技術挑戰：如何以低成本、線程安全蒐集？如何按秒導出？

影響範圍：可觀測性、調參效率、運維可視化。

複雜度評級：低

### Root Cause Analysis
直接原因：
1. 無指標就無法改善  
2. 非線程安全會失真  
3. 導出成本高造成落地困難

深層原因：
- 架構層面：缺乏觀測面設計
- 技術層面：不了解原子操作與重置策略
- 流程層面：未將監控前置於 PoC

### Solution Design
解決策略：以 Interlocked.Exchange 實作 ResetMetrics()，每秒（RaiseSecondPassEvent）導出一次並歸零，將 CSV 寫入 STDERR，便於以管線分離。

實施步驟：
1. 指標原子重置  
- 實作細節：Interlocked.Exchange 歸零並回傳  
- 所需資源：.NET  
- 預估時間：0.5 天

2. 每秒導出  
- 實作細節：RaiseSecondPassEvent 中打印 CSV  
- 所需資源：DateTimeUtil  
- 預估時間：0.5 天

關鍵程式碼：
```csharp
public (int push,int send,int drop,int skip,int buffer_max,double delay) ResetMetrics(){
    return (
      Interlocked.Exchange(ref _metrics_total_push,0),
      Interlocked.Exchange(ref _metrics_total_send,0),
      Interlocked.Exchange(ref _metrics_total_drop,0),
      Interlocked.Exchange(ref _metrics_total_skip,0),
      Interlocked.Exchange(ref _metrics_buffer_max,0),
      Interlocked.Exchange(ref _metrics_buffer_delay,0)
    );
}
```

實際案例：多組實驗每秒輸出 CSV  
實作環境：C#/.NET  
實測數據：  
改善前：指標缺失  
改善後：可每秒觀察 Drop/Delay/Buffer Usage；例如（100,500,10）平均 Buffer Delay=104.525ms、Max Delay=1237.963ms  
改善幅度：從不可觀測到精確可觀測

Learning Points
- 原子操作與 Reset 設計
- 每秒切片（time slicing）的價值
- 數據為決策基礎

技能要求
- 必備：原子操作、指標規劃
- 進階：對接真實監控系統（如 Prometheus）

延伸思考
- 以 Redis GETSET 替代（分散式）
- 滾動視窗統計

Practice Exercise
- 基礎：加入 ResetMetrics 與每秒導出（30 分鐘）
- 進階：將 CSV 改為 JSON 並可視化（2 小時）
- 專案：與既有監控系統對接（8 小時）

Assessment Criteria
- 功能完整性：指標齊備
- 程式碼品質：线程安全
- 效能優化：低開銷導出
- 創新性：導出格式與可視化

---

## Case #10: CSV + STDERR 導出與批次實驗

### Problem Statement
業務場景：要在短時間跑多組參數觀察行為，若整合監控平台成本過高，需選擇低成本導出，快速量測。

技術挑戰：如何在不引入重型依賴下快速導出與分析？

影響範圍：PoC 效率、團隊協作速度。

複雜度評級：低

### Root Cause Analysis
直接原因：
1. 無快速導出→無法快速比較  
2. Stdout 與 Stderr 混雜  
3. 手工收集成本高

深層原因：
- 架構層面：忽略了 PoC 階段的效能需求
- 技術層面：不熟悉管線與重定向
- 流程層面：未建立實驗腳本

### Solution Design
解決策略：將 CSV 輸出寫到 Stderr（Console.Error），用 2> 分離至檔案；編寫批次檔快速跑多組參數。

實施步驟：
1. 程式輸出分離  
- 實作細節：Console.Error.WriteLine CSV  
- 所需資源：.NET  
- 預估時間：0.25 天

2. 批次實驗  
- 實作細節：cmd 批次 2> 導出多檔案  
- 所需資源：Windows cmd  
- 預估時間：0.25 天

關鍵程式碼/設定：
```cmd
dotnet run 100 500 10 2> output\metrics-100-500-10.csv
dotnet run  70 500 10 2> output\metrics-070-500-10.csv
...
```

實際案例：原文多組實驗  
實作環境：.NET、cmd  
實測數據：  
改善前：無法快速對比  
改善後：可視化多組結果，像是（Noise 100 vs 500）平均延遲 52.932ms vs 104.525ms  
改善幅度：實驗效率與決策速度顯著提升

Learning Points
- 輕量導出技術
- PoC 導出與正式監控的差異

技能要求
- 必備：管線與重定向
- 進階：批次與自動化

延伸思考
- 用 PowerShell 或 Bash 改寫
- 導入簡易儀表板（如 Python Matplotlib）

Practice Exercise
- 基礎：導出一組 CSV（30 分鐘）
- 進階：跑 5 組對比圖（2 小時）
- 專案：建立一鍵實驗腳本（8 小時）

Assessment Criteria
- 功能完整性：CSV 正確
- 程式碼品質：腳本清晰
- 效能優化：執行時間
- 創新性：可視化方式

---

## Case #11: TDD 驅動的可驗證重排（事件斷言）

### Problem Statement
業務場景：重排邏輯複雜，需以單元測試覆蓋典型亂序、丟失、緩衝上限等情境，確保每次調整不破壞既有行為。

技術挑戰：如何以事件作為可測點？如何驗證順序輸出？

影響範圍：品質穩定度、開發效率。

複雜度評級：低

### Root Cause Analysis
直接原因：
1. 無測試→回歸風險高  
2. 複合情境難手動驗證  
3. 無事件鉤子難以觀測

深層原因：
- 架構層面：接口先行（Contract First）不足
- 技術層面：測試設計未以事件為中心
- 流程層面：缺 CI 檢核

### Solution Design
解決策略：編寫 SequenceTest，對事件 CommandIsReadyToSend 註冊斷言順序；對 DROP/SKIP 記錄並核對計數；最後 Flush。

實施步驟：
1. 編寫事件測試  
- 實作細節：預期序列 vs 事件回調序列  
- 所需資源：MSTest/xUnit  
- 預估時間：0.5 天

2. 多情境覆蓋  
- 實作細節：正常、亂序、掉號、Buffer 限制  
- 所需資源：測試資料  
- 預估時間：1 天

關鍵程式碼：
```csharp
buffer.CommandIsReadyToSend += (sender,args)=>{
    Assert.AreEqual(expect_sequence[count], sender.Position);
    count++;
};
foreach (var cmd in GetBasicCommands(source_sequence))
    buffer.Push(cmd);
buffer.Flush();
Assert.AreEqual(expect_sequence.Length, count);
```

實際案例：BasicScenario2/5/13 等  
實作環境：C#/.NET、MSTest  
實測數據：  
- 測試時間：單測 ~10ms（原文）  
- 多情境全部通過  
改善幅度：迭代速度與信心提升

Learning Points
- 事件即可測點
- 序列斷言的簡潔做法

技能要求
- 必備：單元測試
- 進階：測試資料工廠與隨機化

延伸思考
- 整合 Property-based Testing
- 壓測與模擬結合

Practice Exercise
- 基礎：寫 1 個亂序測試（30 分鐘）
- 進階：寫 3 個掉號/限緩測試（2 小時）
- 專案：建置 CI 自動跑（8 小時）

Assessment Criteria
- 功能完整性：情境涵蓋
- 程式碼品質：測試可讀性
- 效能優化：測試速度
- 創新性：測試生成

---

## Case #12: 資料結構選型（SortedSet + IComparer）

### Problem Statement
業務場景：Buffer 需支援頻繁插入與取出最小 Position，若使用 List 會造成 O(N) 掃描，效率不佳。

技術挑戰：選擇合適結構以降低複雜度並簡化邏輯。

影響範圍：延遲、CPU 使用、可擴展性。

複雜度評級：低

### Root Cause Analysis
直接原因：
1. List 需掃描找最小 Position  
2. 插入排序成本高  
3. 容量增大時效能劣化

深層原因：
- 架構層面：結構選型忽略操作模式
- 技術層面：未使用平衡樹類結構
- 流程層面：沒有效能基準

### Solution Design
解決策略：使用 SortedSet<OrderedCommand>，自定 IComparer 以 Position 排序；取 Min 與刪除為 O(logN)，簡化 while 釋放邏輯。

實施步驟：
1. IComparer 實作  
- 實作細節：比較 Position  
- 所需資源：.NET  
- 預估時間：0.25 天

2. 以 Min 釋放  
- 實作細節：_buffer.Min / _buffer.Remove(m)  
- 所需資源：單元測試  
- 預估時間：0.25 天

關鍵程式碼：
```csharp
public class OrderedCommandComparer : IComparer<OrderedCommand> {
    public int Compare(OrderedCommand x, OrderedCommand y)
        => x.Position.CompareTo(y.Position);
}
```

實際案例：BasicScenario2 測試時間約 10ms  
實作環境：C#/.NET  
實測數據：  
改善前：List 掃描（理論）  
改善後：O(logN) 插入/取最小；單測快速  
改善幅度：理論複雜度下降，實測單測時間 < 10ms

Learning Points
- 結構選型符合操作模式
- IComparer 驅動排序語意

技能要求
- 必備：集合 API
- 進階：時間複雜度分析

延伸思考
- 若需定位任意 Position，可考慮 Dictionary + Min-Heap 混合

Practice Exercise
- 基礎：實作比較器（30 分鐘）
- 進階：替換為 SortedDictionary 測試（2 小時）
- 專案：效能基準測試（8 小時）

Assessment Criteria
- 功能完整性：最小值正確
- 程式碼品質：簡潔
- 效能優化：O(logN)
- 創新性：結構混搭

---

## Case #13: 事件驅動的解耦（Handlers 與適配器）

### Problem Statement
業務場景：重排器需與業務處理解耦，避免直接耦合到執行邏輯；同時要能切換目標（例如直接 Execute 或轉發到 FIFO MQ）。

技術挑戰：如何設計事件，使外部可掛接不同 Handler？

影響範圍：擴展性、可維護性、測試便利性。

複雜度評級：低

### Root Cause Analysis
直接原因：
1. 直呼業務邏輯導致高耦合  
2. 無法快速替換下游  
3. 測試困難

深層原因：
- 架構層面：缺乏事件適配層
- 技術層面：不熟悉 .NET 事件模型
- 流程層面：缺少可插拔設計

### Solution Design
解決策略：用 CommandIsReadyToSend、CommandWasDroped、CommandWasSkipped 三事件為接口；重排器只負責發事件，不關心處理方式。

實施步驟：
1. 事件定義與發射  
- 實作細節：Send/Drop/Skip 方法內觸發  
- 所需資源：.NET  
- 預估時間：0.5 天

2. 業務 Handler 掛接  
- 實作細節：ExecuteCommand 或 MQ Producer  
- 所需資源：應用邏輯  
- 預估時間：0.5 天

關鍵程式碼：
```csharp
ro.CommandIsReadyToSend += (sender,args)=> { ExecuteCommand(sender); };
// 或改為轉發到支援 FIFO 的 MQ
```

實際案例：Program.cs 內以 ExecuteCommand 直接處理  
實作環境：C#/.NET  
實測數據：  
改善前：耦合高  
改善後：可替換下游；順序驗證保持正確  
改善幅度：解耦帶來擴展性

Learning Points
- 事件即擴展點
- 發送與處理的責任分離

技能要求
- 必備：事件機制
- 進階：適配器模式

延伸思考
- 多播處理與錯誤隔離
- 回壓（Backpressure）策略

Practice Exercise
- 基礎：改用 MQ 發送（30 分鐘）
- 進階：為 DROP/SKIP 添加審計（2 小時）
- 專案：以 Feature Flag 切換 Handler（8 小時）

Assessment Criteria
- 功能完整性：事件皆可掛接
- 程式碼品質：低耦合
- 效能優化：事件處理開銷
- 創新性：Handler 可插拔

---

## Case #14: DateTime Mock 與每秒計時事件（RaiseSecondPassEvent）

### Problem Statement
業務場景：涉及時間的模擬（延遲、每秒輸出）若直接依賴系統時鐘會導致測試脆弱與慢。需可控的時間軸與每秒事件模擬。

技術挑戰：如何在不 Sleep 的前提下推進時間、觸發每秒事件？

影響範圍：測試穩定性、執行效率。

複雜度評級：中

### Root Cause Analysis
直接原因：
1. 直接用 DateTime.Now 無法控制  
2. Sleep 測試低效  
3. 無每秒觸發機制

深層原因：
- 架構層面：未抽象時間來源
- 技術層面：不熟悉時間 Mock 技術
- 整合層面：無定時事件驅動

### Solution Design
解決策略：DateTimeUtil 提供 Now/TimeSeek/TimePass 與 RaiseSecondPassEvent；模擬秒針前進自動觸發導出 Metrics。

實施步驟：
1. 時間來源抽象  
- 實作細節：以 DateTimeUtil 替代 DateTime.Now  
- 所需資源：輕量工具類  
- 預估時間：0.5 天

2. 每秒事件  
- 實作細節：時間跳動時觸發 RaiseSecondPassEvent  
- 所需資源：整合 ResetMetrics  
- 預估時間：0.5 天

關鍵程式碼（使用）：
```csharp
DateTimeUtil.Instance.RaiseSecondPassEvent += (s,a)=>{
   var m = (ro as ReOrderBuffer).ResetMetrics();
   Console.Error.WriteLine($"{t},{m.push},{m.send},...");
};
```

實際案例：所有模擬皆用每秒導出  
實作環境：C#/.NET  
實測數據：  
改善前：測試慢且脆弱  
改善後：快速可控，按秒導出穩定  
改善幅度：執行效率與穩定性顯著改善

Learning Points
- 時間抽象是可測試性的關鍵
- 模擬驅動觀測

技能要求
- 必備：Mock 思維
- 進階：高精度 Timer 設計（未實作）

延伸思考
- 用它驅動主動超時 SKIP/DROP

Practice Exercise
- 基礎：用 TimeSeek 驅動每秒事件（30 分鐘）
- 進階：模擬不同時間節拍（2 小時）
- 專案：加入高精度 Timer 實做（8 小時）

Assessment Criteria
- 功能完整性：事件穩定觸發
- 程式碼品質：時間依賴清理
- 效能優化：無 Sleep
- 創新性：時間驅動策略

---

## Case #15: 命令列參數化與多組場景跑批

### Problem Statement
業務場景：為快速評估 period/noise/buffer 三維參數對 Drop/Delay 的影響，需要可配置與可自動化執行的入口（CLI）。

技術挑戰：如何參數化並整合批次腳本？

影響範圍：實驗效率、可比較性。

複雜度評級：低

### Root Cause Analysis
直接原因：
1. 固定參數需改碼  
2. 無法快速生成多組數據  
3. 人工操作易錯

深層原因：
- 架構層面：不可配置
- 技術層面：CLI 處理缺失
- 流程層面：缺乏自動化

### Solution Design
解決策略：提供 CLI 接受 period/noise/buffer 三參數；配合批次腳本一鍵執行多組場景，輸出多個 CSV。

實施步驟：
1. CLI 支援  
- 實作細節：args[0..2] 解析  
- 所需資源：.NET  
- 預估時間：0.25 天

2. 批次腳本  
- 實作細節：for 不同參數組合執行  
- 所需資源：Windows cmd  
- 預估時間：0.25 天

關鍵程式碼：
```csharp
int command_period = int.Parse(args[0]);
int command_noise  = int.Parse(args[1]);
int buffer_size    = int.Parse(args[2]);
```

實際案例：原文 batch 範例  
實作環境：.NET、cmd  
實測數據：  
改善前：手動改碼/執行  
改善後：一鍵多組輸出，顯著縮短分析時間  
改善幅度：效率顯著提升

Learning Points
- 小投資大回報的自動化
- 對齊團隊協作流程

技能要求
- 必備：CLI 處理
- 進階：批次自動化

延伸思考
- 以 GitHub Actions 或 CI 定期跑

Practice Exercise
- 基礎：撰寫 CLI 解析（30 分鐘）
- 進階：批次跑 5 組並命名檔案（2 小時）
- 專案：CI 整合（8 小時）

Assessment Criteria
- 功能完整性：參數可用
- 程式碼品質：錯誤處理
- 效能優化：快速啟動
- 創新性：自動化程度

---

## Case #16: 外部網路品質改善對延遲的實際影響（Noise 500→100）

### Problem Statement
業務場景：網路優化投資是否值得？需量化在相同 Buffer 下，降低延遲噪音（noise）的實際收益。

技術挑戰：控制變因，對比 Avg/Max Delay。

影響範圍：延遲體感、資源利用、SLA。

複雜度評級：低

### Root Cause Analysis
直接原因：
1. 高 noise 造成更多亂序與 Buffer 停留  
2. 優化網路可減少重排延遲

深層原因：
- 架構層面：未建立量化框架
- 技術層面：無對照實驗
- 流程層面：缺決策依據

### Solution Design
解決策略：固定 period=100ms、buffer=10，noise 從 500 降至 100，重跑並比較 Average/Max Delay。

實施步驟：
1. 兩組場景執行  
- 實作細節：dotnet run 100 500 10；dotnet run 100 100 10  
- 所需資源：cmd  
- 預估時間：0.25 天

2. 結果比對  
- 實作細節：Excel 圖表與數據表  
- 所需資源：Excel  
- 預估時間：0.25 天

關鍵程式碼/設定：同 Case 10 批次

實際案例：原文 4-1 vs 4-2  
實作環境：.NET、cmd、Excel  
實測數據：  
- Noise=500：Avg Delay=104.525ms、Max Delay=1237.963ms  
- Noise=100：Avg Delay=52.932ms、Max Delay=1134.016ms  
改善幅度：Avg Delay 降 49.4%；Max Delay 下降約 8.4%

Learning Points
- 「平均改善」與「尖峰改善」的差異
- 外在品質優化對系統延遲的直接收益

技能要求
- 必備：實驗設計
- 進階：成本/效益分析

延伸思考
- 搭配時間上限控制可進一步壓低 Max Delay

Practice Exercise
- 基礎：重現兩組實驗（30 分鐘）
- 進階：加入第三組 noise=300（2 小時）
- 專案：撰寫優化建議書（8 小時）

Assessment Criteria
- 功能完整性：對照清晰
- 程式碼品質：重現性
- 效能優化：數據分析到位
- 創新性：決策建議

---

## Case #17: 以 SLO 為目標的 Timer 主動 SKIP/DROP 設計（設計延伸）

### Problem Statement
業務場景：僅靠 Buffer 空間界限仍可能導致延遲尖峰（等永不到號），需以時間上限（例如 500ms）保證 SLO，在無新訊息推進時也能主動決策 SKIP/DROP。

技術挑戰：如何在沒有 Push 時由時間驅動邏輯？如何避免誤判？

影響範圍：Max Delay、穩定性、用戶體感。

複雜度評級：高

### Root Cause Analysis
直接原因：
1. 僅靠 Push 無法在沉寂時段推進  
2. 無時間上限策略導致尖峰  
3. Buffer 大時風險更高

深層原因：
- 架構層面：缺 Timer 驅動引擎
- 技術層面：時間精度與檢查策略
- 流程層面：SLO 未被技術約束落實

### Solution Design
解決策略：新增高精度 Timer（或基於 DateTimeUtil），定期檢查：  
- 若 next 遲未到達，且已超時，則 SKIP next（釋放後續）  
- 若某命令在 Buffer 停留超時，則 DROP 該命令（或策略性退讓）

實施步驟：
1. Timer 觸發器  
- 實作細節：固定頻率掃描 Buffer 與 next  
- 所需資源：高精度 Timer 或 DateTimeUtil  
- 預估時間：1 天

2. 策略與安全閥  
- 實作細節：避免抖動、設置保護窗口  
- 所需資源：測試場景  
- 預估時間：1 天

關鍵程式碼/設定（示意）：
```csharp
void OnTimerTick() {
    // 若 _current_next_index 遲未到且超時，SKIP(_current_next_index)
    // 若某 buffered 命令停留超過閾值，DROP(該命令)
}
```

實際案例：設計延伸（原文未實作）  
實作環境：C#/.NET  
實測數據（目標）：  
改善前：Max Delay 最高可達 1237.963ms（示例）  
改善後（目標）：Max Delay 不超過 SLO（例如 ≤500ms）  
改善幅度：Max Delay 有界，尖峰受控

Learning Points
- 以 SLO 反推設計
- Push 與 Timer 的雙引擎

技能要求
- 必備：Timer 與時間判斷
- 進階：抖動與誤判處理

延伸思考
- 動態調整 Buffer 與超時閾值
- 結合分片保序與回壓

Practice Exercise
- 基礎：加一個簡單超時 SKIP（30 分鐘）
- 進階：以測試驗證 Max Delay 上限（2 小時）
- 專案：完整 Timer 引擎與策略（8 小時）

Assessment Criteria
- 功能完整性：Max Delay 可控
- 程式碼品質：清晰與安全
- 效能優化：Timer 開銷可控
- 創新性：策略與自適應

---

案例分類
1. 按難度分類
- 入門級（適合初學者）
  - Case 2 訊息結構重構
  - Case 7 隨機延遲模擬
  - Case 8 丟失模擬
  - Case 9 指標蒐集
  - Case 10 CSV/STDERR 導出
  - Case 11 TDD 驅動測試
  - Case 12 資料結構選型
  - Case 13 事件驅動解耦
  - Case 15 CLI 參數化跑批
- 中級（需要一定基礎）
  - Case 1 基線重排器
  - Case 3 串流重排演算法
  - Case 4 SKIP 與 Flush
  - Case 5 過號 DROP
  - Case 6 Buffer 尺寸取捨
  - Case 14 DateTime Mock 與每秒事件
  - Case 16 網路品質改善評估
- 高級（需要深厚經驗）
  - Case 17 SLO 與 Timer 主動控制

2. 按技術領域分類
- 架構設計類：Case 1, 3, 4, 5, 6, 13, 17
- 效能優化類：Case 6, 12, 16
- 整合開發類：Case 10, 13, 15
- 除錯診斷類：Case 7, 8, 9, 11, 14, 16
- 安全防護類：Case 5（防錯序）、17（SLO 控制）

3. 按學習目標分類
- 概念理解型：Case 2, 3, 5, 12, 13, 17
- 技能練習型：Case 7, 9, 10, 11, 14, 15
- 問題解決型：Case 1, 4, 6, 8, 16
- 創新應用型：Case 17（SLO 與 Timer）

案例關聯圖（學習路徑建議）
- 建議先學：
  - Case 2（訊息結構）→ Case 12（資料結構）→ Case 13（事件解耦）
  - Case 11（TDD 測試）與 Case 9（指標）可同步學，為後續驗證鋪路
- 依賴關係：
  - Case 1（基線重排器）依賴 Case 2（結構）、Case 12（資料結構）、Case 13（事件）
  - Case 3/4/5（演算法/策略）依賴 Case 1
  - Case 6（容量取捨）依賴 Case 9/10/14/15（觀測與實驗）
  - Case 7/8（環境模擬）是 Case 6/16 的基礎
  - Case 16（網路品質評估）依賴 Case 7/10/14/15
  - Case 17（Timer SLO 控制）在 Case 1/3/4 穩定後再做
- 完整學習路徑：
  1) Case 2 → 12 → 13 → 11 → 9  
  2) Case 1 → 3 → 4 → 5  
  3) Case 7 → 8 → 10 → 14 → 15 → 6  
  4) Case 16（外部品質分析）  
  5) Case 17（SLO 與 Timer 主動控制，最終優化）

說明：
- 這條路徑先奠定資料與事件基礎，再完成核心重排與策略，接著以模擬+指標驅動的方式找到合理 Buffer 與網路投資回報，最終導入以 SLO 為目標的 Timer 主動控制，使 Max Delay 有界、Drop 可控。
