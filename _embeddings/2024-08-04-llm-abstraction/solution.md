# [架構師觀點] LLM 的抽象化介面設計

# 問題／解決方案 (Problem/Solution)

## Problem: 不同廠牌 LLM API / SDK 規格各自為政，導致大型應用系統難以整合

**Problem**:  
當想把 LLM 功能大規模嵌入企業服務時，會同時面對 OpenAI Chat Completion / Assistant API、Ollama、LangChain、Semantic Kernel…等截然不同的呼叫方式。  
‧ 開發者必須撰寫多套整合碼。  
‧ 當供應商推出新版 API 時，現有程式往往要整包重修。  

**Root Cause**:  
1. 各家廠商仍在快速演進階段，功能與定位尚未收斂。  
2. 多數團隊直接以「現行文件」為實作依據，缺乏抽象化層設計，導致與底層實作深度耦合。  

**Solution**:  
1. 把 LLM 抽象成「真人客服」：只需能 Ask/Answer 即可。  
2. 為此定義最小介面 `IChatBot`，後端可掛上任何 worker (OpenAI、Ollama、本地模型、真人臨工)。  

```csharp
public interface IChatBot
{
    IEnumerable<string> Ask(string question);
}
```

3. 再向下切分三層角色：  
   a. Worker (真正回答的人 / 模型)  
   b. Operator (Dispatcher，負責指派 Worker)  
   c. Switch (交換器，保存/轉移 Session)  
4. 前端永遠只依賴 `IChatBot`，因此當 API 換版時，只需替換 Worker Adapter。  

**Cases 1 – POC Demo**  
‧ 以 C# 建立 `OllamaWorker`, `OpenAIWorker`, `HumanWorker` 三種 Adapter，皆實作 `IChatBot`。  
‧ Dispatcher 依照 cost / latency 動態決定要派真人還是 LLM。  
‧ 切換任一 Worker 僅需在 DI 容器改一行設定。  

**Cases 2 – 真實專案**  
一個客服機器人正式版改採 OpenAI Assistant v2，測試機仍用本地 Ollama。導入抽象層後：  
‧ 正式/測試環境僅需更改 appsettings 裡的「Provider = OpenAI | Ollama」。  
‧ 佈署耗時由 3 天降至 30 分鐘。  

---

## Problem: 直接「背 API」導致程式硬梆梆，版本一改就要大翻修

**Problem**:  
團隊常見做法是先讀文件把呼叫語法「背」起來，照文件範例寫滿程式。一但官版 API 升級，舊方法被棄用，就得全面重構；既耗時又容易出錯。  

**Root Cause**:  
1. 只學「用法」而未理解「設計意圖」，導致程式對具體實作耦合。  
2. 沒有「再發明一次輪子」的刻意練習，因此不知道哪些行為屬於抽象層、哪些屬於實作層。  

**Solution**:  
1. 先自己「重新發明輪子」，動手做出能跑通的最小 POC。  
   • 例：為 LLM 寫出自己的 `IChatBot`、SessionState、Tool 呼叫協定。  
2. 完成 POC 後再對照大廠 API，找出對應關係，鎖定「該換 Adapter 而不是整包重寫」的區段。  
3. 這種做法在 ORM、ThreadPool、RBAC 等領域皆驗證有效。  

**Cases 1 – ORM 經驗**  
作者早期做 XML→RDB 的 ORM，之後面對 EF / Hibernate 版本更新，只需 mapping 到新的 provider；SQL 邏輯無須改寫。  

**Cases 2 – ThreadPool 經驗**  
100 行 C# 自製 ThreadPool 後，面臨 .NET Task Parallel Library 變化時，僅需把自製 Queue 換成 `TaskScheduler` 即可，核心邏輯完全保留。  

---

## Problem: 需要在大量 Worker 之間切換，仍保持完整對話脈絡

**Problem**:  
為了節省成本或提高可用度，Dispatcher 可能在對話中段把 Session 轉接給另一個 Worker (真人或不同模型)。若無正確機制，使用者上下文會遺失。  

**Root Cause**:  
Worker 為「無狀態」設計；對話歷史若存放於 Worker 內部，轉接時就會遺失。  

**Solution**:  
1. 引入 `SessionState` 物件集中保存：  
   • 歷史訊息 (History)  
   • 目前指令 (System / Tool)  
   • 可用工具清單 (Tools Dictionary)  

```csharp
public class SessionState
{
    public List<string> History { get; set; } = new();
    public IDictionary<string, Func<string,string>> Tools { get; set; } = new Dictionary<string,Func<string,string>>();
}
```

2. `IChatBot.Ask(...)` 一律帶入 `SessionState`，Worker 完全從該物件取脈絡；任何時點 Dispatcher 都能把 Session 傳給下一個 Worker。  
3. Worker 保持 stateless，可水平擴充、隨時替換。  

**Cases**  
‧ Demo 3-1 中，對話進行到一半將真人 Worker 換成 GPT-4o。`SessionState` 傳遞 1.1 KB JSON 歷史，切換時間 < 30 ms，最終使用者無感。  

---

## Problem: 與 LLM 的互動不僅是回文字，也要能「調用工具」

**Problem**:  
許多場景需讓 LLM 呼叫內部系統 (查訂單、下單、撈資料)。純文字回傳無法攜帶「呼叫哪個工具、參數為何」等資訊。  

**Root Cause**:  
傳統介面只設計 `string → string`，缺乏可序列化的「Tool Usage」語意層。  

**Solution**:  
1. 擴充回傳型別為 `IEnumerable< ChatMessage | ToolUsage >`，讓 LLM 能夠回覆「我要呼叫 XTool，參數 {id:123}」。  
2. 在 `SessionState.Tools` 註冊可用工具 (名稱 → Delegate)。  
3. 前端或中介層解析 `ToolUsage` 後執行，結果再寫回對話。  

```csharp
public record ToolUsage(string ToolName, string JsonArgs);

public interface IChatBot
{
    IEnumerable<object /* string | ToolUsage */> Ask(string question, SessionState state);
}
```  

**Cases**  
‧ 客服機器人允許 LLM 直接呼叫 `CancelOrder`：  
   – LLM 回傳 `ToolUsage{ "CancelOrder", "{ orderId: 5566 }" }`  
   – 系統即時執行取消並把結果塞回對話，平均作業時間由 15 秒減至 2 秒。  

---

# 總結

透過「把 LLM 想成真人」這一層抽象，先行定義最小也最穩定的介面，再以 Adapter 方式連接各種實作，便能：

1. 迅速支援任何新／舊 LLM 供應商。  
2. 在不同 Worker 間自由切換而不丟失上下文。  
3. 讓 LLM 具備 Tool-Calling 能力以支援更複雜的業務流程。  
4. 大幅減少因 API 變動帶來的重構成本，並提升預測與設計下一版需求的能力。