---
layout: synthesis
title: "Thread Sync #2. 實作篇 - 互相等待的兩個執行緒"
synthesis_type: solution
source_post: /2008/08/15/thread-sync-2-implementation-two-threads-waiting-for-each-other/
redirect_from:
  - /2008/08/15/thread-sync-2-implementation-two-threads-waiting-for-each-other/solution/
---

## Case #1: 從被動回呼到主動思考：以 AsyncPlayer 反轉控制權

### Problem Statement（問題陳述）
業務場景：GameHost 控制整個猜數字遊戲的流程，透過呼叫 Player.StartGuess() 與 Player.GuessNext() 不斷拉取玩家的下一步猜測。當 Player 的解題邏輯包含多個階段時（探索、收斂、最終猜測），被迫拆在多個回呼中，耦合 GameHost 的節奏，導致邏輯分散與維護困難。
技術挑戰：如何讓 Player 擁有連續的「思考流程」，自行決定何時提問與如何推進，而不改動 GameHost 對 Player 的現有 API 契約。
影響範圍：影響 Player 的可讀性、可維護性與可測性；若實作不當，還會引入同步錯誤與死鎖。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Player 的解題邏輯被拆散在 StartGuess/GuessNext 之間，必須用跨呼叫狀態變數維持上下文。
2. GameHost 掌控呼叫節奏，Player 處於被動，難以以自然流程組織演算法。
3. 缺乏雙向同步通道，Player 無法在「思考」過程中主動向 Host 提問與取得回覆。

深層原因：
- 架構層面：介面設計為 Host 拉取（pull）模式，與 Player 需要的推進（push）模式不匹配。
- 技術層面：沒有抽象層將主動邏輯封裝，導致業務邏輯與同步糾纏。
- 流程層面：把多階段演算法拆成回呼導致變數外溢、切換點多、易錯。

### Solution Design（解決方案設計）
解決策略：引入 AsyncPlayer 作為適配層，在不變更 GameHost 介面的前提下，於 StartGuess 啟動專屬思考執行緒，將演算法整合進 Think()，並提供 GameHost_AskQuestion 作為雙向同步的問題/答案通道，化被動為主動。

實施步驟：
1. 建立 AsyncPlayer 抽象類別
- 實作細節：覆寫 StartGuess/GuessNext/Stop，新增 ThinkCaller 啟動背景執行緒，並定義抽象 Init/Think。
- 所需資源：.NET Thread, AutoResetEvent
- 預估時間：3 小時

2. 實作 Player 的連續思考邏輯
- 實作細節：在 Think() 中用 while 迴圈推進策略，透過 GameHost_AskQuestion 提交猜測、等待回覆。
- 所需資源：C# 類別繼承、演算法邏輯
- 預估時間：4 小時

關鍵程式碼/設定：
```csharp
public abstract class AsyncPlayer : Player {
  public override int[] StartGuess(int maxNum, int digits) {
    base.StartGuess(maxNum, digits);
    new Thread(this.ThinkCaller).Start();
    _host_return.WaitOne();           // 等待第一個猜測準備好
    return _temp_number;
  }
  public override int[] GuessNext(Hint lastHint) {
    _temp_hint = lastHint;
    _host_call.Set();                 // 回覆提示給背景執行緒
    _host_return.WaitOne();           // 等下一個猜測
    return _temp_number;
  }
  protected Hint GameHost_AskQuestion(int[] number) {
    if (_host_complete) throw new InvalidOperationException("GameHost stopped!");
    lock(this) {
      try {
        _temp_number = number;        // 放入猜測
        _host_return.Set();           // 通知 Host 取件
        _host_call.WaitOne();         // 等 Host 回覆提示
        return _temp_hint;
      } finally {
        _temp_number = null;          // 清理暫存
        _temp_hint = new Hint(-1, -1);
      }
    }
  }
}
```

實際案例：AsyncDummyPlayer 將隨機猜測邏輯放入 Think() 中，以 while(true) 迴圈持續提問，直到 A==digits。
實作環境：.NET（C#），System.Threading.Thread / AutoResetEvent。

實測數據：
改善前：邏輯分散在 StartGuess/GuessNext，多處狀態維持。
改善後：邏輯集中於 Think()，跨呼叫狀態歸零。
改善幅度：可讀性顯著提升；代價是同步開銷（見 Case #10）。

Learning Points（學習要點）
核心知識點：
- 適配層設計：用抽象類別轉換呼叫模式
- 非同步思維：由拉取（pull）轉為推進（push）
- WaitHandle 雙向同步手法

技能要求：
必備技能：C# 繼承與抽象、Thread/WaitHandle 基礎
進階技能：非同步流程設計、可重入/同步安全

延伸思考：
- 可應用於長流程工作者（crawler、ETL 工作單元）
- 風險：同步錯誤造成死鎖
- 優化：以 Channel/BlockingCollection/Task-based API 替代底層事件

Practice Exercise（練習題）
基礎練習：將 DummyPlayer 改寫為 Think() 迴圈（30 分鐘）
進階練習：加入兩階段策略（探索→收斂），在 Think() 切換（2 小時）
專案練習：以 AsyncPlayer 改寫另一個需要反轉控制的模組（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：Think() 能連續提問並收尾
程式碼品質（30%）：抽象清晰、沒有跨呼叫狀態外溢
效能優化（20%）：最小化不必要的 Set/Wait 次數
創新性（10%）：策略切換設計合理


## Case #2: 兩個 AutoResetEvent 實作請求/回覆的握手協定

### Problem Statement（問題陳述）
業務場景：玩家思考時需「提出猜測→等待回覆」，主機則需「接收猜測→計算提示→回覆」。雙方速度不可預期，容易出現一邊先到的情況。
技術挑戰：確保問題與回覆一一對應，且晚到的一方能被正確喚醒，避免競賽條件與亂序。
影響範圍：資料一致性、流程正確性；錯誤會造成死等、丟包、重用舊資料。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 兩個執行緒進度不同步，缺乏對稱的阻塞/喚醒機制。
2. 單一事件無法同時保障「準備好問題」與「回覆到位」兩個時點。
3. 無法保證一問一答的對偶關係。

深層原因：
- 架構層面：缺乏請求與回覆的明確握手協定。
- 技術層面：沒有適當的 WaitHandle 配置去封裝雙向同步。
- 流程層面：未定義好雙方各自的等待點與喚醒時機。

### Solution Design（解決方案設計）
解決策略：使用兩個 AutoResetEvent：_host_return 表示「玩家已提出猜測，主機可取」，_host_call 表示「主機已回覆提示，玩家可用」，形成對稱的雙向握手。

實施步驟：
1. 定義事件語義與責任
- 實作細節：玩家 Set _host_return；主機 Wait _host_return → Set _host_call；玩家 Wait _host_call。
- 所需資源：AutoResetEvent 2 個
- 預估時間：1 小時

2. 嚴格維持順序與原子性
- 實作細節：用 lock 包住暫存填寫與事件觸發的臨界區。
- 所需資源：lock、finally 清理
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
// 玩家側（Ask）
_temp_number = number;
_host_return.Set();  // 通知主機「問題準備好了」
_host_call.WaitOne(); // 等待主機「回覆提示」

// 主機側（StartGuess / GuessNext）
_host_return.WaitOne(); // 等待玩家提出猜測
var guess = _temp_number;
// ...計算 Hint
_temp_hint = hint;
_host_call.Set(); // 通知玩家回覆就緒
```

實際案例：AsyncPlayer 中 GameHost_AskQuestion 與 StartGuess/GuessNext 的互動。
實作環境：.NET AutoResetEvent。

實測數據：
改善前：無握手協定，存在亂序與資料不一致風險。
改善後：一問一答對齊，晚到方被阻塞並在對方 Set 後喚醒。
改善幅度：一致性風險顯著降低。

Learning Points（學習要點）
核心知識點：
- 對稱握手協定設計
- AutoResetEvent 單次喚醒特性
- 臨界區與清理的必要性

技能要求：
必備技能：WaitHandle 使用、臨界區
進階技能：雙向協定設計、失敗/超時路徑

延伸思考：
- 可延用到 RPC 的本地模擬、Producer-Consumer 對偶
- 風險：Set/Wait 順序錯誤即死等
- 優化：加入 timeout 與重試路徑

Practice Exercise（練習題）
基礎練習：將單事件模型改為雙事件握手（30 分鐘）
進階練習：補上 WaitOne(timeout) 與錯誤處理（2 小時）
專案練習：以此握手封裝本地 RPC（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：正確一問一答
程式碼品質（30%）：臨界區與清理完整
效能優化（20%）：無多餘 busy-wait
創新性（10%）：超時與恢復策略設計


## Case #3: 在 StartGuess 啟動背景思考執行緒並等待首個提問

### Problem Statement（問題陳述）
業務場景：GameHost 呼叫 StartGuess 要求玩家「初始化並給出第一個猜測」。玩家若採用背景執行緒思考，需在 StartGuess 返回前準備好初始猜測。
技術挑戰：在不阻塞背景思考的前提下，保證首個猜測必達並避免 GameHost 讀到空值。
影響範圍：首回合可用性、流程正確性；不當處理會出現 null 或舊值。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 背景執行緒與主執行緒存在時序不確定性。
2. 沒有同步點保證第一個猜測已準備好。
3. 共享暫存未受管控。

深層原因：
- 架構層面：需要「生產第一筆資料」的阻塞點。
- 技術層面：缺少 WaitHandle 協調。
- 流程層面：未定義 StartGuess 的最小完成條件。

### Solution Design（解決方案設計）
解決策略：StartGuess 啟動 ThinkCaller 執行緒後，WaitOne(_host_return) 等待玩家透過 GameHost_AskQuestion 提交第一個猜測。

實施步驟：
1. 在 StartGuess 啟動背景執行緒
- 實作細節：new Thread(ThinkCaller).Start()
- 所需資源：Thread
- 預估時間：15 分鐘

2. 等待第一個猜測
- 實作細節：_host_return.WaitOne()；從 _temp_number 取值後返回
- 所需資源：AutoResetEvent
- 預估時間：15 分鐘

關鍵程式碼/設定：
```csharp
public override int[] StartGuess(int maxNum, int digits) {
  base.StartGuess(maxNum, digits);
  var t = new Thread(this.ThinkCaller);
  t.Start();
  _host_return.WaitOne();  // 等待第一個猜測備妥
  return _temp_number;
}
```

實際案例：文章中 AsyncPlayer.StartGuess。
實作環境：.NET Thread/AutoResetEvent。

實測數據：
改善前：可能返回 null 或無效資料。
改善後：首猜必達，流程穩定。
改善幅度：首回合穩定性大幅提升。

Learning Points（學習要點）
核心知識點：
- 啟動背景工作與首筆資料阻塞
- WaitOne/Set 的配對使用
- 共享暫存取用時機

技能要求：
必備技能：Thread/WaitHandle
進階技能：初始化與第一里程碑設計

延伸思考：
- 可應用於任何需「冷啟動→首筆產出」的場景
- 風險：Thread 啟動失敗或例外未處理
- 優化：可以 Task + TaskCompletionSource 替代

Practice Exercise（練習題）
基礎練習：補上 Thread 啟動失敗的保護（30 分鐘）
進階練習：以 TaskCompletionSource 重寫（2 小時）
專案練習：將首筆資料阻塞封裝為可重用元件（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：首筆資料穩定返回
程式碼品質（30%）：錯誤處理與釋放
效能優化（20%）：不引入忙等
創新性（10%）：替代方案設計


## Case #4: 用 GuessNext 傳遞 Hint 並喚醒背景執行緒

### Problem Statement（問題陳述）
業務場景：主機在接到猜測後計算 Hint，需回覆給正在等待的玩家思考執行緒。
技術挑戰：如何安全地把 Hint 傳回玩家，並喚醒玩家側的等待點。
影響範圍：回覆正確性與玩家推進節奏；錯誤會導致卡死或讀到舊 Hint。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 玩家執行緒在 WaitOne(_host_call) 等待 Hint。
2. 主機必須以正確順序填入 _temp_hint 再 Set。
3. 缺少清理會使資料殘留。

深層原因：
- 架構層面：需要與玩家側的等待點對齊。
- 技術層面：回覆路徑需鏡像請求路徑。
- 流程層面：未定義 Hint 存活週期。

### Solution Design（解決方案設計）
解決策略：在 GuessNext 中先填 _temp_hint，再 _host_call.Set() 喚醒玩家側；玩家側在 finally 清理暫存。

實施步驟：
1. 正確回填與喚醒
- 實作細節：_temp_hint = lastHint; _host_call.Set()
- 所需資源：AutoResetEvent
- 預估時間：15 分鐘

2. 玩家側清理
- 實作細節：finally {_temp_number=null; _temp_hint=new Hint(-1,-1);}
- 所需資源：例外安全結構
- 預估時間：15 分鐘

關鍵程式碼/設定：
```csharp
public override int[] GuessNext(Hint lastHint) {
  _temp_hint = lastHint; // 填回覆
  _host_call.Set();      // 喚醒玩家
  _host_return.WaitOne();// 等下一個猜測
  return _temp_number;
}
```

實際案例：文章中 AsyncPlayer.GuessNext 與 GameHost_AskQuestion 的配對。
實作環境：.NET AutoResetEvent。

實測數據：
改善前：玩家可能永遠等待或讀到舊 Hint。
改善後：回覆安全按序到達。
改善幅度：穩定性顯著提升。

Learning Points（學習要點）
核心知識點：
- 回覆路徑鏡像請求路徑
- Set/Wait 的正確相對順序
- finally 清理避免汙染

技能要求：
必備技能：事件同步
進階技能：例外安全與清理策略

延伸思考：
- 可套用於雙向訊息匯流排
- 風險：Set 在填值之前造成讀取競態
- 優化：引入封裝類避免直接操作暫存

Practice Exercise（練習題）
基礎練習：刻意打亂順序觀察錯誤（30 分鐘）
進階練習：增加斷言與日誌保護（2 小時）
專案練習：抽象成 IRequest/IResponse 管道（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：回覆正確抵達
程式碼品質（30%）：順序明確、日誌完整
效能優化（20%）：避免多餘切換
創新性（10%）：抽象與封裝能力


## Case #5: 遊戲結束的雙向同步：Stop 與 _host_end 的協調

### Problem Statement（問題陳述）
業務場景：遊戲結束時，主機呼叫 Player.Stop()。此時玩家執行緒可能在等待主機回覆，或仍在思考中。需要安全地終止雙方而不遺留卡頓。
技術挑戰：如何喚醒玩家執行緒、讓迴圈自然結束，並讓 Stop 有可等待的完成訊號。
影響範圍：資源釋放、無限等待風險、整體穩定性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 玩家可能卡在 WaitOne(_host_call) 等待回覆。
2. Stop 若不提供回覆，玩家將永久等待。
3. 缺少全域完成訊號讓 Stop 知道玩家已退出。

深層原因：
- 架構層面：缺乏終止協定與對應信號。
- 技術層面：需要雙向喚醒與完成通知。
- 流程層面：未定義「停止」在玩家邏輯中的退出條件。

### Solution Design（解決方案設計）
解決策略：Stop 設定 _temp_hint 為終止條件（A==digits），Set _host_call 喚醒玩家，等待 _host_end；玩家在 ThinkCaller finally 中 Set _host_end 通知完成。

實施步驟：
1. 主機側 Stop
- 實作細節：_temp_hint=new Hint(_digits,0); _host_call.Set(); _host_end.WaitOne(); _host_complete=true;
- 所需資源：AutoResetEvent 三個
- 預估時間：30 分鐘

2. 玩家側退出
- 實作細節：Think() 判斷 h.A==_digits break；ThinkCaller finally {_host_end.Set();}
- 所需資源：例外保證
- 預估時間：30 分鐘

關鍵程式碼/設定：
```csharp
public override void Stop() {
  base.Stop();
  _temp_hint = new Hint(_digits, 0); // 終止訊號
  _host_call.Set();                  // 喚醒玩家
  _host_end.WaitOne();               // 等玩家結束
  _host_complete = true;
}
```

實際案例：文章中 Stop 與 ThinkCaller finally 的配合。
實作環境：.NET AutoResetEvent。

實測數據：
改善前：可能無限等待或資源外洩。
改善後：可預期地在 Stop 完成時釋放。
改善幅度：終止穩定性大幅提升。

Learning Points（學習要點）
核心知識點：
- 終止協定設計（訊號型式與語義）
- finally 中發佈完成事件的重要性
- 雙向同步的收尾

技能要求：
必備技能：事件同步、例外處理
進階技能：可中斷設計、終止語義一致性

延伸思考：
- 可用 CancellationToken 改良終止語義
- 風險：誤用終止 Hint 影響正常邏輯
- 優化：拆分「正常完成」與「被取消」的不同訊號

Practice Exercise（練習題）
基礎練習：模擬 Stop 於不同時機呼叫（30 分鐘）
進階練習：加入取消與逾時（2 小時）
專案練習：打造可重用的 Stop/Complete 協定（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：能在各時機安全停止
程式碼品質（30%）：finally 與狀態旗標一致
效能優化（20%）：最小阻塞時間
創新性（10%）：取消/終止語義清晰


## Case #6: 背景執行緒例外的封裝與不阻塞通知

### Problem Statement（問題陳述）
業務場景：玩家思考過程可能拋出例外。若未妥善處理，主機可能永遠等待回覆或無從得知失敗。
技術挑戰：如何捕捉背景執行緒例外並保證主機能順利收尾。
影響範圍：穩定性、可觀測性；可能造成 Stop 永久阻塞。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 背景執行緒例外預設不會傳遞到主執行緒。
2. 缺乏在失敗時的完成通知。
3. 未設計例外路徑的信號。

深層原因：
- 架構層面：背景工作錯誤與宿主流程解耦。
- 技術層面：沒有 finally 中發布完成事件。
- 流程層面：沒有錯誤日誌與診斷。

### Solution Design（解決方案設計）
解決策略：在 ThinkCaller try/catch 包住 Init/Think，log 例外，並在 finally 中 _host_end.Set() 通知主機可收尾。

實施步驟：
1. 包覆 ThinkCaller
- 實作細節：try{Init;Think;} catch{Console.WriteLine(...);} finally{_host_end.Set();}
- 所需資源：例外處理
- 預估時間：15 分鐘

2. 主機側 Stop 等待
- 實作細節：保持 Stop 等待 _host_end
- 所需資源：AutoResetEvent
- 預估時間：15 分鐘

關鍵程式碼/設定：
```csharp
private void ThinkCaller() {
  try {
    Init(_maxNum, _digits);
    Think();
  } catch(Exception ex) {
    Console.WriteLine("Player Exception: {0}", ex);
  } finally {
    _host_end.Set(); // 確保主機得知結束
  }
}
```

實際案例：文章中 ThinkCaller。
實作環境：.NET。

實測數據：
改善前：Stop 可能永遠等待。
改善後：即使 Think 崩潰，仍能收尾。
改善幅度：健壯性顯著提升。

Learning Points（學習要點）
核心知識點：
- 背景例外處理
- finally 通知確保宿主不阻塞
- 最小可觀測性（log）

技能要求：
必備技能：例外處理
進階技能：錯誤通報與監控介接

延伸思考：
- 用事件或回呼回報錯誤型別
- 風險：只 log 不足以告警
- 優化：搭配告警系統或度量

Practice Exercise（練習題）
基礎練習：刻意丟例外，驗證 Stop 不阻塞（30 分鐘）
進階練習：把錯誤透過狀態暴露給宿主（2 小時）
專案練習：建置通用的背景工作錯誤匯報器（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：錯誤時能安全收尾
程式碼品質（30%）：例外處理完整
效能優化（20%）：不增加等待成本
創新性（10%）：錯誤可觀測性設計


## Case #7: 用 lock 與 finally 保證共享暫存區的一致性

### Problem Statement（問題陳述）
業務場景：玩家與主機透過 _temp_number/_temp_hint 共享問題與回覆。若無同步保護，會出現競態與髒讀。
技術挑戰：確保每次握手中，暫存資料的寫入/讀取是原子、互斥且在結束時清理。
影響範圍：資料一致性、正確性與診斷難度。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 兩邊可能同時訪問暫存變數。
2. 例外情境中未清理會污染下次握手。
3. 沒有內存屏障保證可見性。

深層原因：
- 架構層面：共享緩衝未抽象封裝。
- 技術層面：缺乏互斥鎖與記憶體序。
- 流程層面：缺清理規範。

### Solution Design（解決方案設計）
解決策略：在 GameHost_AskQuestion 內用 lock(this) 包住，並用 finally 將暫存清空與設哨兵值，確保每次握手結束後狀態乾淨。

實施步驟：
1. 互斥保護
- 實作細節：lock(this){ _temp_number=...; _host_return.Set(); _host_call.WaitOne(); return _temp_hint; }
- 所需資源：lock
- 預估時間：30 分鐘

2. 例外安全清理
- 實作細節：finally {_temp_number=null; _temp_hint=new Hint(-1,-1);}
- 所需資源：finally
- 預估時間：15 分鐘

關鍵程式碼/設定：
```csharp
protected Hint GameHost_AskQuestion(int[] number) {
  lock(this) {
    try {
      _temp_number = number;
      _host_return.Set();
      _host_call.WaitOne();
      return _temp_hint;
    } finally {
      _temp_number = null;
      _temp_hint = new Hint(-1, -1);
    }
  }
}
```

實際案例：文章中 GameHost_AskQuestion。
實作環境：.NET。

實測數據：
改善前：偶發髒讀/殘留。
改善後：每輪握手狀態乾淨、互斥。
改善幅度：一致性顯著提升。

Learning Points（學習要點）
核心知識點：
- 互斥與臨界區
- 例外安全清理
- 哨兵值語義

技能要求：
必備技能：lock/finally
進階技能：避免 lock(this) 的替代（私有鎖物件）

延伸思考：
- 改為私有 readonly object _sync = new object();
- 風險：lock(this) 外部可干擾
- 優化：封裝緩衝為類型

Practice Exercise（練習題）
基礎練習：改為私有鎖物件（30 分鐘）
進階練習：用 Monitor.TryEnter 加超時（2 小時）
專案練習：設計型別安全的 MessageBuffer（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：無交錯讀寫
程式碼品質（30%）：鎖定範圍合理
效能優化（20%）：避免過度鎖定
創新性（10%）：封裝與抽象設計


## Case #8: 避免狀態機碎片化：用 Think 迴圈取代跨呼叫 state

### Problem Statement（問題陳述）
業務場景：原本 DummyPlayer 需在 GuessNext 以 switch/case 管理多階段狀態，跨呼叫維持進度，閱讀與維護成本高。
技術挑戰：以自然順序描述多階段演算法，避免把內部狀態暴露到物件層級。
影響範圍：可讀性、可維護性、錯誤率。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 呼叫模式迫使演算法分段。
2. 需要實例變數記錄「做到哪」。
3. 多處切換點容易出錯。

深層原因：
- 架構層面：被動回呼造成狀態外溢。
- 技術層面：沒有連續執行的容器方法。
- 流程層面：演算法階段與 API 節點不對齊。

### Solution Design（解決方案設計）
解決策略：把策略整合於 Think()，使用 while/for 組合描述階段流程；需要訊問時呼叫 GameHost_AskQuestion，階段內變數皆為區域變數。

實施步驟：
1. 收斂為 Think 迴圈
- 實作細節：第一階段 for 探索→第二階段 while 收斂→終止
- 所需資源：C# 控制流程
- 預估時間：2 小時

2. 移除跨呼叫狀態
- 實作細節：將進度變數改為方法區域變數
- 所需資源：重構工具
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
protected override void Think() {
  // 探索階段
  for(/*...*/){
    // 構造猜測
    var h = GameHost_AskQuestion(_currAnswer);
    // 根據提示調整策略...
  }
  // 收斂階段
  while(true){
    randomGuess();
    var h = GameHost_AskQuestion(_currAnswer);
    if (h.A == _digits) break;
  }
}
```

實際案例：文章說明 AsyncDummyPlayer 的 while(true) 直到猜中。
實作環境：.NET。

實測數據：
改善前：跨呼叫狀態多、邏輯分散。
改善後：邏輯集中、狀態封裝於區域。
改善幅度：可讀性與可維護性顯著提升。

Learning Points（學習要點）
核心知識點：
- 把演算法映射為連續控制流程
- 狀態封裝與作用域管理
- 回呼驅動與流程驅動的取捨

技能要求：
必備技能：控制流程設計
進階技能：狀態機到流程圖的重構

延伸思考：
- 適用於任何多階段決策演算法
- 風險：Think 迴圈若不阻塞會忙等
- 優化：在需要等待時必須阻塞等待

Practice Exercise（練習題）
基礎練習：將 switch 狀態機改為流程迴圈（30 分鐘）
進階練習：把探索/收斂切為兩個私有方法（2 小時）
專案練習：把另一個回呼型策略改寫（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：流程正確可終止
程式碼品質（30%）：狀態封裝良好
效能優化（20%）：避免忙等
創新性（10%）：重構思路清晰


## Case #9: 以阻塞等待取代忙等：WaitOne/Set 的應用

### Problem Statement（問題陳述）
業務場景：玩家在未收到 Hint 前不應繼續計算下一步，以免空轉耗 CPU；主機在未收到猜測前不應持續輪詢。
技術挑戰：避免 busy-wait，改為事件驅動的阻塞等待。
影響範圍：CPU 使用率、電力、效能穩定性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. while(true) 若不搭配等待會造成空轉。
2. 缺乏事件通知機制。
3. 不恰當輪詢代價高。

深層原因：
- 架構層面：沒有事件驅動模型。
- 技術層面：未利用 WaitHandle 阻塞。
- 流程層面：缺少等待點設計。

### Solution Design（解決方案設計）
解決策略：用 _host_return/_host_call 的 WaitOne/Set 實現阻塞式等待，直到對方完成為止。

實施步驟：
1. 玩家側等待 Hint
- 實作細節：Ask 後 WaitOne(_host_call)
- 所需資源：AutoResetEvent
- 預估時間：15 分鐘

2. 主機側等待猜測
- 實作細節：StartGuess/GuessNext 先 WaitOne(_host_return)
- 所需資源：AutoResetEvent
- 預估時間：15 分鐘

關鍵程式碼/設定：
```csharp
// 阻塞點示意
_host_return.WaitOne(); // 主機等猜測
_host_call.WaitOne();   // 玩家等回覆
```

實際案例：文章雙事件握手。
實作環境：.NET。

實測數據：
改善前：可能持續輪詢/空轉。
改善後：事件驅動，僅在必要時喚醒。
改善幅度：CPU 利用率下降、效能穩定。

Learning Points（學習要點）
核心知識點：
- Busy-wait vs. Event-driven
- WaitHandle 的使用契機
- 阻塞等待的設計位置

技能要求：
必備技能：WaitHandle
進階技能：超時/取消與恢復

延伸思考：
- 可用 async/await + TaskCompletionSource 現代化
- 風險：錯誤等待點引發死鎖
- 優化：增加監控、延遲追蹤

Practice Exercise（練習題）
基礎練習：將輪詢改為等待（30 分鐘）
進階練習：加入超時與告警（2 小時）
專案練習：大規模替換忙等點（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：等待點正確
程式碼品質（30%）：無輪詢碼
效能優化（20%）：CPU 明顯下降
創新性（10%）：整體事件化設計


## Case #10: 同步成本對效能的影響與取捨（Async 慢 4~5 倍）

### Problem Statement（問題陳述）
業務場景：改用 AsyncPlayer 後，作者實測在其機器上速度較 DummyPlayer 慢約 4~5 倍。
技術挑戰：辨識同步帶來的額外成本與適用場景，避免過度工程化。
影響範圍：延遲、吞吐量；在高頻互動場景尤為明顯。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 每次問答多一次或多次上下文切換。
2. AutoResetEvent WaitOne/Set 與 lock 帶來同步成本。
3. 背景執行緒管理開銷。

深層原因：
- 架構層面：以可讀性換取效能。
- 技術層面：同步原語成本不可忽視。
- 流程層面：一次猜測/一次回覆過於細粒度。

### Solution Design（解決方案設計）
解決策略：接受在可讀性價值高的情境下的效能下降，或調整策略粒度（每次問答包含更多資訊），或採用更輕量的同步工具。

實施步驟：
1. 度量與判斷適用性
- 實作細節：比較 DummyPlayer vs AsyncDummyPlayer 次數與耗時
- 所需資源：碼錶、日誌
- 預估時間：1 小時

2. 降低問答頻率
- 實作細節：把多步推理合併為一次提問
- 所需資源：策略改寫
- 預估時間：2 小時

關鍵程式碼/設定：
```csharp
// 觀測點：每次 Set/Wait/lock 的次數
// 建議：合併多步決策，減少 AskQuestion 次數
```

實際案例：文章陳述 Async 版本慢約 4~5 倍。
實作環境：.NET。

實測數據：
改善前：DummyPlayer 基準。
改善後：AsyncDummyPlayer 慢 4~5 倍（作者機器）。
改善幅度：-300% ~ -400%（相對）。

Learning Points（學習要點）
核心知識點：
- 同步原語的效能成本
- 可讀性 vs 效能的取捨
- 粒度設計的重要性

技能要求：
必備技能：效能測試
進階技能：策略分塊與合併

延伸思考：
- 在 I/O 密集 vs CPU 密集的適用性
- 風險：盲目套用造成退步
- 優化：以 Channel/Async/ValueTask 減少切換

Practice Exercise（練習題）
基礎練習：加上耗時計時統計（30 分鐘）
進階練習：減半問答頻率觀察改善（2 小時）
專案練習：做一份同步原語成本基準（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：測得可用數據
程式碼品質（30%）：測量點清晰
效能優化（20%）：策略調整有效
創新性（10%）：替代同步方案


## Case #11: 適配既有 GameHost API：抽象基底類別設計

### Problem Statement（問題陳述）
業務場景：GameHost 已固定呼叫 Player.StartGuess/GuessNext/Stop 介面，不能修改宿主；欲改用主動思考的玩家模型。
技術挑戰：在不動宿主的條件下，導入新行為模型。
影響範圍：相容性、風險管理。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 宿主 API 確定且廣泛使用。
2. 直接改宿主風險大。
3. 新模型與舊 API 不匹配。

深層原因：
- 架構層面：需要適配器層。
- 技術層面：抽象層封裝同步細節。
- 流程層面：保持客戶端契約不變。

### Solution Design（解決方案設計）
解決策略：設計 AsyncPlayer 繼承既有 Player，覆寫三個方法橋接非同步思考與同步 API，對上相容、對內創新。

實施步驟：
1. 實作覆寫點
- 實作細節：StartGuess/GuessNext/Stop 與 ThinkCaller
- 所需資源：抽象與繼承
- 預估時間：2 小時

2. 曝露新擴展點
- 實作細節：protected abstract Init/Think
- 所需資源：抽象設計
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
public abstract class AsyncPlayer : Player {
  protected abstract void Init(int maxNum, int digits);
  protected abstract void Think();
  // 覆寫 StartGuess/GuessNext/Stop 實現橋接
}
```

實際案例：文章中的 AsyncPlayer 類別。
實作環境：.NET。

實測數據：
改善前：無法引入主動思考而不改宿主。
改善後：相容宿主，玩家可主動思考。
改善幅度：相容性 100%，可讀性大幅提升。

Learning Points（學習要點）
核心知識點：
- 適配器模式/模板方法
- 對上相容、對內擴充
- 風險隔離

技能要求：
必備技能：OOP 抽象/繼承
進階技能：API 演進策略

延伸思考：
- 未來可用介面而非繼承實作
- 風險：過度繼承耦合
- 優化：以組合取代繼承

Practice Exercise（練習題）
基礎練習：為另一個玩家行為建子類（30 分鐘）
進階練習：將抽象改為介面+委派（2 小時）
專案練習：封裝一組相容層（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：相容宿主呼叫
程式碼品質（30%）：抽象清楚
效能優化（20%）：最小額外開銷
創新性（10%）：演進策略


## Case #12: 順序正確性：以時序圖設計對齊 thread 速度差

### Problem Statement（問題陳述）
業務場景：雙方執行緒速度可能不同，導致應後執行的動作先發生（亂序），需要一套順序對齊設計。
技術挑戰：把設計上的時序轉為程式中的等待/喚醒點，確保邏輯時間順序。
影響範圍：正確性、可預期性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 無法預測執行緒排程。
2. 缺少明確順序的同步點。
3. 程式未映射設計時序。

深層原因：
- 架構層面：未以序列圖思維設計同步。
- 技術層面：事件未對齊。
- 流程層面：尚無順序驗證。

### Solution Design（解決方案設計）
解決策略：以序列圖為藍本設計兩事件握手，每個箭頭對應一次 Set/Wait；使用 WaitOne 令先到的一方阻塞，確保順序。

實施步驟：
1. 轉圖為等待點
- 實作細節：每個訊息→一 Set/一 Wait
- 所需資源：設計圖
- 預估時間：1 小時

2. 實作與驗證
- 實作細節：加日誌，驗證箭頭順序
- 所需資源：日誌框架
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
// 兩條時間線對齊：玩家Ask(Set _host_return) ↔ 主機Wait(_host_return)
// 主機Reply(Set _host_call)   ↔ 玩家Wait(_host_call)
```

實際案例：文章提供時序圖與程式碼對照。
實作環境：.NET。

實測數據：
改善前：亂序風險高。
改善後：任何一方先到會被阻塞直到對方完成。
改善幅度：順序可預期性大幅提升。

Learning Points（學習要點）
核心知識點：
- 序列圖到同步點映射
- 先到/後到的等待策略
- 對稱握手

技能要求：
必備技能：序列圖閱讀
進階技能：同步點校正與驗證

延伸思考：
- 可應用於複雜工作流編排
- 風險：漏了等待點即破功
- 優化：加斷言校驗狀態

Practice Exercise（練習題）
基礎練習：畫出本握手序列圖（30 分鐘）
進階練習：用斷言驗證順序（2 小時）
專案練習：建置序列→程式生成器雛形（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：順序正確
程式碼品質（30%）：日誌斷言充分
效能優化（20%）：最少等待
創新性（10%）：從圖到碼的落地


## Case #13: 防止停止後的非法呼叫：_host_complete 與防呆

### Problem Statement（問題陳述）
業務場景：Stop 之後若玩家仍持續呼叫 GameHost_AskQuestion，可能對已關閉的宿主造成無效請求。
技術挑戰：如何在宿主關閉後，阻止玩家後續互動並給予明確錯誤。
影響範圍：健壯性、診斷清晰度。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 沒有關閉旗標。
2. 玩家可能晚到。
3. 缺乏錯誤明確回報。

深層原因：
- 架構層面：終止語義未傳遞至互動 API。
- 技術層面：缺旗標檢查。
- 流程層面：未定義停止後行為。

### Solution Design（解決方案設計）
解決策略：引入 _host_complete 旗標，在 GameHost_AskQuestion 冒頭檢查，若已停止則丟 InvalidOperationException。

實施步驟：
1. 定義旗標與維護點
- 實作細節：Stop 完成後 _host_complete=true
- 所需資源：布林狀態
- 預估時間：15 分鐘

2. 入口檢查
- 實作細節：if (_host_complete) throw ...
- 所需資源：例外型別
- 預估時間：15 分鐘

關鍵程式碼/設定：
```csharp
protected Hint GameHost_AskQuestion(int[] number) {
  if (_host_complete) throw new InvalidOperationException("GameHost stopped!");
  // ...
}
```

實際案例：文章中 GameHost_AskQuestion 的保護。
實作環境：.NET。

實測數據：
改善前：停止後仍可能互動，行為未定義。
改善後：立即拒絕並提示錯誤。
改善幅度：健壯性提升、診斷清晰。

Learning Points（學習要點）
核心知識點：
- 終止後行為定義
- 防呆檢查
- 明確錯誤通報

技能要求：
必備技能：狀態管理
進階技能：錯誤語義設計

延伸思考：
- 用 CancellationToken 改良
- 風險：旗標未標記為 volatile 可能有可見性問題
- 優化：Interlocked.Exchange 或 volatile

Practice Exercise（練習題）
基礎練習：加入 volatile/Interlocked（30 分鐘）
進階練習：停用後嘗試呼叫並驗證（2 小時）
專案練習：統一終止語義於多 API（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：停止後拒絕互動
程式碼品質（30%）：狀態同步妥善
效能優化（20%）：低成本檢查
創新性（10%）：更佳終止模型


## Case #14: 用 AutoResetEvent 而非 ManualResetEvent 的理由

### Problem Statement（問題陳述）
業務場景：請求/回覆的一問一答需要一次喚醒一個等待者，避免多方誤喚醒。
技術挑戰：選擇正確的事件型態以符合一對一握手。
影響範圍：一致性、安全性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. ManualResetEvent 喚醒所有等待者，需手動重置。
2. 本場景只有單一等待者且需要單次消費。
3. 使用 ManualResetEvent 易造成重複消費或漏重置。

深層原因：
- 架構層面：訊號粒度與消費模式不匹配。
- 技術層面：選錯同步原語。
- 流程層面：重置責任不清。

### Solution Design（解決方案設計）
解決策略：使用 AutoResetEvent 自動重置，一次 Set 精準喚醒一個等待者，符合一問一答協定。

實施步驟：
1. 替換事件類型
- 實作細節：new AutoResetEvent(false)
- 所需資源：.NET
- 預估時間：10 分鐘

2. 驗證喚醒行為
- 實作細節：測試多次 Set/Wait 配對
- 所需資源：單元測試
- 預估時間：30 分鐘

關鍵程式碼/設定：
```csharp
private AutoResetEvent _host_call = new AutoResetEvent(false);
private AutoResetEvent _host_return = new AutoResetEvent(false);
```

實際案例：文章中三個 AutoResetEvent 的使用。
實作環境：.NET。

實測數據：
改善前：可能多喚醒/漏重置。
改善後：一次一喚醒，自動重置。
改善幅度：可靠性提升。

Learning Points（學習要點）
核心知識點：
- Auto vs Manual Reset 差異
- 消費粒度設計
- 重置責任

技能要求：
必備技能：WaitHandle 類型選擇
進階技能：多等待者場景設計

延伸思考：
- 多消費者需不同設計（如 Semaphore）
- 風險：多等待者不適用
- 優化：用 Channel 取代事件

Practice Exercise（練習題）
基礎練習：切換兩種事件感受差異（30 分鐘）
進階練習：多等待者下用 SemaphoreSlim（2 小時）
專案練習：抽象訊號器介面（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：喚醒行為符合預期
程式碼品質（30%）：簡潔無過度控制
效能優化（20%）：無多餘 Set
創新性（10%）：同步原語選型合理


## Case #15: 臨界區資料清理策略：哨兵值與資源釋放

### Problem Statement（問題陳述）
業務場景：每次握手完成後，暫存的 _temp_number/_temp_hint 應被清空，避免下次讀到上次殘留。
技術挑戰：在有例外的情況也能保證清理執行。
影響範圍：資料正確性、除錯難度。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 未清理導致殘值。
2. 例外中跳出未執行清理。
3. 無法辨識資料是否有效。

深層原因：
- 架構層面：缺少狀態切換的明確標記。
- 技術層面：缺少 finally 包裝。
- 流程層面：未定義哨兵語義。

### Solution Design（解決方案設計）
解決策略：在 finally 設置 _temp_number=null 與 _temp_hint=new Hint(-1,-1)，用哨兵值表示「目前沒有有效資料」。

實施步驟：
1. finally 清理
- 實作細節：放於 GameHost_AskQuestion 的 finally
- 所需資源：例外安全
- 預估時間：15 分鐘

2. 哨兵語義
- 實作細節：-1,-1 代表無效
- 所需資源：文件化約定
- 預估時間：15 分鐘

關鍵程式碼/設定：
```csharp
finally {
  _temp_number = null;
  _temp_hint = new Hint(-1, -1); // 哨兵，非有效提示
}
```

實際案例：文章中 finally 清理段落。
實作環境：.NET。

實測數據：
改善前：偶發讀到舊資料。
改善後：狀態乾淨，可判斷無效。
改善幅度：正確性提升。

Learning Points（學習要點）
核心知識點：
- 哨兵值的使用
- 例外安全清理
- 無效狀態標註

技能要求：
必備技能：例外處理
進階技能：狀態語義設計

延伸思考：
- 可替換為 Nullable 或 Option 型別
- 風險：誤用哨兵值
- 優化：封裝為結構化類型

Practice Exercise（練習題）
基礎練習：以 Nullable 重構（30 分鐘）
進階練習：建立 Result<T> 包含有效/無效（2 小時）
專案練習：清理策略套用到其他模組（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：清理正確執行
程式碼品質（30%）：語義清楚
效能優化（20%）：無多餘操作
創新性（10%）：型別安全改良


## Case #16: 隨機猜測策略在非同步模型中的實作（AsyncDummyPlayer）

### Problem Statement（問題陳述）
業務場景：範例玩家以隨機猜測實作，需在非同步模型下持續提出猜測並根據提示判斷是否終止。
技術挑戰：在 Think 中正確初始化、產生不重複數字、提問並判斷結束。
影響範圍：範例完整性、教學價值。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 需要在 Init 初始化內部緩衝。
2. 隨機猜測需避免重複數字。
3. 正確呼叫 GameHost_AskQuestion 並依 Hint 決策。

深層原因：
- 架構層面：策略邏輯需移入 Think。
- 技術層面：隨機生成與集合判斷。
- 流程層面：循環直到 A==digits。

### Solution Design（解決方案設計）
解決策略：在 Init 配置 _currAnswer；Think 中 while(true) 隨機產生猜測→Ask→若 A==digits break。

實施步驟：
1. 初始化
- 實作細節：_currAnswer = new int[digits];
- 所需資源：內存配置
- 預估時間：10 分鐘

2. 生成與提問
- 實作細節：randomGuess 去重；GameHost_AskQuestion 提問
- 所需資源：List<int>、Random
- 預估時間：30 分鐘

關鍵程式碼/設定：
```csharp
protected override void Init(int maxNum, int digits) {
  _currAnswer = new int[digits];
}
protected override void Think() {
  while (true) {
    randomGuess();
    Hint h = GameHost_AskQuestion(_currAnswer);
    if (h.A == _digits) break;
  }
}
```

實際案例：文章中 AsyncDummyPlayer。
實作環境：.NET C#。

實測數據：
改善前：同步版本邏輯分散。
改善後：非同步版本邏輯集中、易讀。
改善幅度：可讀性提升；效能落後（見 Case #10）。

Learning Points（學習要點）
核心知識點：
- 在 Think 中撰寫策略
- Ask/Hint 迴圈
- 隨機去重技巧

技能要求：
必備技能：C# 集合/Random
進階技能：測試非確定性行為

延伸思考：
- 將隨機改為啟發式策略
- 風險：隨機效率低
- 優化：記錄已嘗試組合

Practice Exercise（練習題）
基礎練習：確保 randomGuess 無重複（30 分鐘）
進階練習：增加啟發式縮小空間（2 小時）
專案練習：比較多種策略迭代次數（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：可找到答案
程式碼品質（30%）：邏輯清晰
效能優化（20%）：減少嘗試次數
創新性（10%）：策略改良


--------------------------------
案例分類

1. 按難度分類
- 入門級（適合初學者）
  - Case #3, #4, #9, #13, #14, #15, #16
- 中級（需要一定基礎）
  - Case #1, #2, #5, #7, #8, #11, #12
- 高級（需要深厚經驗）
  - Case #6, #10

2. 按技術領域分類
- 架構設計類
  - Case #1, #8, #11, #12
- 效能優化類
  - Case #9, #10
- 整合開發類
  - Case #3, #4, #5, #16
- 除錯診斷類
  - Case #6, #7, #13, #15
- 安全防護類（同步正確性/一致性）
  - Case #2, #14

3. 按學習目標分類
- 概念理解型
  - Case #1, #2, #12, #14
- 技能練習型
  - Case #3, #4, #7, #9, #15, #16
- 問題解決型
  - Case #5, #6, #8, #13
- 創新應用型
  - Case #10, #11

--------------------------------
案例關聯圖（學習路徑建議）
- 先學哪些案例？
  - 基礎同步與握手：Case #2（雙事件握手）、#14（事件選型）、#9（阻塞 vs 忙等）
  - 基本 API 與流程：Case #3（啟動與首猜）、#4（回覆 Hint）

- 依賴關係
  - Case #1（反轉控制）依賴：#2、#3、#4、#9、#14
  - Case #5（安全停止）依賴：#1、#2
  - Case #6（例外封裝）依賴：#5
  - Case #7（臨界區一致性）依賴：#2
  - Case #8（避免狀態機碎片化）依賴：#1
  - Case #10（效能取捨）依賴：#1、#2、#9
  - Case #11（適配設計）依賴：#1
  - Case #12（時序對齊）依賴：#2
  - Case #13（停止防呆）依賴：#5
  - Case #15（清理策略）依賴：#7
  - Case #16（策略實作）依賴：#1、#3、#4

- 完整學習路徑建議
  1) 打好同步基礎：#14 → #9 → #2
  2) 掌握往返流程：#3 → #4
  3) 進入核心模式：#1（反轉控制）
  4) 強化正確性：#7（臨界區） → #12（時序） → #15（清理）
  5) 完整收尾：#5（停止） → #13（防呆） → #6（例外）
  6) 應用與取捨：#8（演算法流程化） → #11（適配） → #10（效能取捨）
  7) 綜合練習：#16（完整玩家策略實作）

此學習路徑由同步基礎到架構抽象，最後回到效率與策略，能幫助學習者系統性掌握「兩執行緒互等」的設計與實作。