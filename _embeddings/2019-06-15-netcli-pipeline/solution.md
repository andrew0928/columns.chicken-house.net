# 後端工程師必備: CLI + PIPELINE 開發技巧

# 問題／解決方案 (Problem/Solution)

## Problem: 批次程式一次載入「上百萬筆資料」導致效能低落、記憶體爆炸

**Problem**:  
在資料轉換／匯入等背景任務中，工程師慣性先把所有待處理資料 `ToArray()` 再依序執行 Phase1→Phase2→Phase3。  
• 第一筆資料完成要等到所有階段跑完  
• N 筆 × (M1+M2+M3) 的總時間  
• 需要同時配置 N 份資料的記憶體，資料若達 GB 等級，極易 OOM。

**Root Cause**:  
1. 採用「批次 (Batch)」模式：一次讀入、一次處理，全部資料都常駐於 RAM。  
2. 以「階段」為中心編寫 `foreach`，缺乏流式 (Streaming) 與管線 (Pipeline) 思維。  

**Solution**:  
1. 以資料為中心改寫為串流模式：  
   ```csharp
   foreach(var m in GetModels()) { 
       ProcessPhase1(m); 
       ProcessPhase2(m); 
       ProcessPhase3(m); 
   }
   ```  
   • `GetModels()` 改用 `yield return`，邊讀邊處理  
   • 記憶體峰值固定 ≒ 1 筆資料  
2. 避免一次序列化／反序列化：  
   ```csharp
   var json = JsonSerializer.Create();           // streaming serializer 
   json.Serialize(Console.Out, model);           // 邊寫邊送出
   ```  
   同理，反序列化用 `JsonTextReader(SupportMultipleContent=true)` 逐筆讀。  

**Cases 1** – DEMO2 (Stream Processing):  
• 第一筆完成 5s →由 12s 大幅縮短  
• 記憶體從 5 GB ↓ 至 1 ~ 2 GB，筆數再多也維持平穩  

---

## Problem: 串流雖省記憶體，整體時程仍與批次相同

**Problem**:  
改成邊讀邊處理後，第一筆提早產生，但總處理時間仍為 N×(M1+M2+M3)。CPU 在不同階段之間閒置。

**Root Cause**:  
1. Phase1、Phase2、Phase3 仍序列化執行，無法重疊 (pipeline)  
2. 缺乏緩衝區／非同步讓上一階段先「推」資料給下一階段

**Solution**:  
A. 純 C# 管線 (DEMO3) – `yield return` 包裝三層 Iterator  
   ```csharp
   var result = StreamP3(StreamP2(StreamP1(GetModels())));
   foreach(var m in result) { }
   ```  
   • 程式結構以階段分割，維護性佳  
   • 第一筆 = M1+M2+M3，記憶體固定 ≒ 2~3 筆

B. 加入 Async (DEMO4)  
   ```csharp
   Task<DataModel> prev = null;
   foreach(var m in models){
       if(prev!=null) yield return await prev;
       prev = Task.Run(()=>{ ProcessPhase1(m); return m;});
   }
   ```  
   • 每階段預抓 1 筆，利用執行緒重疊計算  
   • 全部時間 N × Max(M1,M2,M3) ≒ 13s (由 22s 改善 41%)

C. 使用 `BlockingCollection` (DEMO5)  
   ```csharp
   BlockingCollection<DataModel> buf = new(10);
   Task.Run(()=>{
       foreach(var m in models){ ProcessP1(m); buf.Add(m);}
       buf.CompleteAdding();
   });
   return buf.GetConsumingEnumerable();
   ```  
   • 明確設定 buffer size，提高各階段並行度  
   • 全部時間進一步降至 12s  
   • 記憶體依 buffer 大小線性增長，可控

**Cases 1** – DEMO4 與 DEMO5：  
| 方案 | 第一筆 | 全部完成 | RAM 峰值 | 備註 |
|----|----|----|----|----|
| DEMO3 | 4s | 22s | 2 GB | 無 buffer |
| DEMO4 | 5s | 13s | 6 GB | async +1 筆 buffer |
| DEMO5 | 4s | 12s | 6~25 GB | BlockingCollection(10) |

---

## Problem: 程式複雜、重跑某階段困難，難以跨語言 / 跨機器協作

**Problem**:  
單一 Console App 內部埋 Thread / Buffer，  
• 讀者難以理解、維護  
• 想只重跑 Phase2 得整個程式再跑一次  
• 無法與 Python / Bash 等其他語言工具鏈結  

**Root Cause**:  
1. 仍以「函式呼叫」耦合各階段  
2. Process、資源都在同一個 OS 行程，無法提早釋放  
3. 少了 OS 級別的管線與重導向能力

**Solution**:  
1. 將 Phase1/2/3 拆成獨立 CLI，標準化 STDIN/STDOUT/STDERR：  
   - CLS-DATA 產生 jsonl  
   - CLI-P1 / P2 / P3 讀一行處理一行再輸出  
2. 用 Shell Pipeline 組裝：  
   ```bash
   dotnet cli-data.dll |
   dotnet cli-p1.dll   |
   dotnet cli-p2.dll   |
   dotnet cli-p3.dll > nul
   ```  
3. 需要重跑 P2 只要：  
   ```bash
   type p1_output.jsonl | dotnet cli-p2.dll | dotnet cli-p3.dll
   ```  
4. 交由 OS 緩衝、排程，不再手刻 Thread / Queue；Process 完成即可釋放記憶體、連線。  
5. 以 `dotnet tool` 發佈，可跨平台、跨語言呼叫。

**Cases 1** – CLI Pipeline（16 B × 1 000 筆）：  
• 三個 dotnet Process 各佔 5 MB RAM，峰值平穩  
• P1 結束後立即終止，OS 釋放資源，P2/P3 繼續跑  
• 快速測試：可先 `cli-data > file`，反覆重播

**Cases 2** – CLI Pipeline（4 MB × 1 000 筆）：  
• 單階段獨立測試 P1 100 筆 = 108 s，記憶體 160 MB  
• 三階段串起來前 100 筆共 232 s，三個行程均保持 170 MB  
• Pipeline Buffer 約 40 筆：當 P1 超前過多即被 OS block，保持整體穩定

---

## Problem: 需要因應自動化、跨機器運行的大型批次任務

**Problem**:  
• 工作排程需拆分、分散；  
• 可能因網路或機器故障中斷；  
• 需在不同語言環境混用 (PowerShell、Bash、Python…)。  

**Root Cause**:  
缺乏標準化的 IPC 機制，將數據流、錯誤流與控制流混在一起，導致：  
– 難以將部分資料導向遠端；  
– 難以定位錯誤、重送；  
– 難以把 CLI 套件化、版本化。

**Solution**:  
1. 全面使用 STDIN / STDOUT 進行資料交換；STDERR 僅留給 Log。  
2. 配合 SSH + Pipe，即可把任何階段導向遠端：  
   ```bash
   cat data.jsonl | ssh user@host "cli-p1" | cli-p2 | cli-p3
   ```  
3. `tee`、重導向 (`>`, `>>`) 可在不中斷管線的前提下備份或分支資料流。  
4. 透過 NuGet + `dotnet tool install` 發佈，確保 CLI 在 CI/CD、容器或 VM 中一鍵安裝。

**Cases**  
• 某電商資料清洗鏈：P1 (停站時間) → P2/P3 (線上)；P1 全速跑完 10 分鐘，站台即恢復；P2/P3 可花 2 小時慢慢跑而不影響前端營運。  
• 透過 `tee` 同時備份中間 jsonl，以利錯誤重播，故障後僅需重跑 P3，節省 70% 時間。  

---

以上示例說明：  
1. 用「串流＋管線」取代「一次讀入＋批次」，能同時解決「首筆回應」「記憶體峰值」「總執行時間」三個維度的痛點。  
2. 善用 OS Pipeline 及 CLI 標準化，能把複雜的非同步/緩衝/平行問題下放給作業系統，開發者專注在單一階段的商務邏輯。  
3. 透過 `.NET tool` 封裝 CLI，更容易在各種部署環境落地，亦方便與其他語言工具鏈整合。