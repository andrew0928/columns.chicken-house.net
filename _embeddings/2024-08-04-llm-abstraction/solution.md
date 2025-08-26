以下內容根據原文的抽象化介面設計思路，整理出 18 個可實作、可教學、可評估的案例。每個案例都含問題、根因、解決方案、步驟、關鍵程式、實測數據（POC 示意）、學習要點與練習題，便於課程與專案實作。

------------------------------------------------------------

## Case #1: 統一 LLM 抽象介面 IIntelligence/IChatBot

### Problem Statement（問題陳述）
- 業務場景：團隊要將多家 LLM 服務（OpenAI、Ollama、未來新供應商）納入同一個應用，並允許部分情境以「工人智慧」真人回覆。開發者困擾於每家 API 介面不同，導致應用程式高耦合、難以替換或共用 UI/流程。
- 技術挑戰：缺乏一致的抽象，導致業務層邏輯被迫理解每家 API 的差異；無法輕易實現 A/B 測試或快速切換模型/供應商。
- 影響範圍：功能擴展速度、維護成本、供應商鎖定風險、品質一致性。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 供應商 API 不一致（輸入/輸出型別、串流語義、功能命名差異）。
  2. 業務邏輯直接呼叫 SDK，缺乏隔離層。
  3. 沒有明確定義「對話」與「完成」的抽象。
- 深層原因：
  - 架構層面：未建立清晰邊界與端口（ports），導致強耦合。
  - 技術層面：未採用 Adapter/Facade 等設計模式。
  - 流程層面：缺少「供應商接入規格」與契約測試。

### Solution Design（解決方案設計）
- 解決策略：定義 IIntelligence/IChatBot 為唯一對外介面，將供應商差異封裝在 Adapter。業務層僅面對抽象介面，新增或替換供應商僅新增 Adapter，即可達到可替換性與一致性。

- 實施步驟：
  1. 設計抽象介面與資料模型
     - 實作細節：定義 IIntelligence（Ask）、ChatMessage、ChatOptions 等。
     - 所需資源：.NET 8、C# 12。
     - 預估時間：0.5 天
  2. 建立 Adapter 契約與 Provider 能力宣告
     - 實作細節：ICapabilities 描述是否支援串流、工具使用等。
     - 所需資源：原生 C#。
     - 預估時間：0.5 天
  3. 業務層改用抽象介面
     - 實作細節：依賴反轉（DI），注入 IIntelligence。
     - 所需資源：Microsoft.Extensions.DependencyInjection。
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
public record ChatMessage(string Role, string Content);
public record ChatOptions(bool Stream = true);

public interface IIntelligence
{
    // 非串流
    Task<string> AskAsync(string prompt, SessionState session, ChatOptions? options = null, CancellationToken ct = default);
    // 串流
    IAsyncEnumerable<string> AskStreamAsync(string prompt, SessionState session, ChatOptions? options = null, CancellationToken ct = default);
    Capabilities GetCapabilities();
}

public record Capabilities(bool SupportsStreaming, bool SupportsTools);

public class SessionState
{
    private readonly List<ChatMessage> _history = new();
    public IReadOnlyList<ChatMessage> History => _history;
    public void AddUser(string text) => _history.Add(new("user", text));
    public void AddAssistant(string text) => _history.Add(new("assistant", text));
}
```

- 實際案例：同一 UI 透過 IIntelligence 切換 OpenAI 與 Ollama，不改 UI 程式碼。
- 實作環境：.NET 8、C# 12、Windows 11/Ubuntu 22.04。
- 實測數據：
  - 改善前：切換供應商需修改 8 個檔案、約 600 行。
  - 改善後：新增 1 個 Adapter 檔案、約 180 行。
  - 改善幅度：修改面積降低 75%，新增供應商時間減少 60%。

Learning Points（學習要點）
- 核心知識點：
  - 抽象介面與 Adapter 模式
  - 能力宣告（Capabilities）與條件分支
  - 對話模型的核心資料結構
- 技能要求：
  - 必備技能：介面設計、DI、非同步程式設計。
  - 進階技能：設計模式（Adapter/Facade）、契約穩定性管理。
- 延伸思考：
  - 如何支援更多語言或平台（Node/Go）？
  - 介面是否需要考慮多模態（圖像/語音）？
  - 如何將訊息安全地匿名化以便紀錄？
- Practice Exercise（練習題）
  - 基礎練習：為 IIntelligence 增加 system 指令支援（30 分鐘）
  - 進階練習：實作一個 FakeIntelligence（回聲機器）供測試（2 小時）
  - 專案練習：建置一個可注入多 Adapter 的簡易對話平台（8 小時）
- Assessment Criteria（評估標準）
  - 功能完整性（40%）：支援非串流與串流模式
  - 程式碼品質（30%）：模組化、可測試
  - 效能優化（20%）：串流延遲與記憶體佔用
  - 創新性（10%）：能力宣告與自動降級設計

------------------------------------------------------------

## Case #2: 串流回應抽象化與取消控制

### Problem Statement（問題陳述）
- 業務場景：聊天 UI 需要即時顯示 LLM token，提升互動性與體感。使用者希望可中途取消生成或快速切換話題。
- 技術挑戰：串流 API 與同步 API 的語義不同；需支援取消、錯誤恢復、緩衝與背壓控制。
- 影響範圍：使用者體驗、記憶體佔用、效能與穩定性。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 只提供 string 完成式介面，TTFB 長。
  2. 未提供 CancellationToken，無法中斷。
  3. UI 與串流生命週期耦合不清。
- 深層原因：
  - 架構層面：缺少標準串流管道與錯誤處理策略。
  - 技術層面：不了解 IAsyncEnumerable 的迭代中斷。
  - 流程層面：未建立串流行為測試標準。

### Solution Design（解決方案設計）
- 解決策略：以 IAsyncEnumerable<string> 定義串流回應，統一 TTFB、取消、錯誤邊界行為；在 UI 以 Channel 做緩衝，提供清晰的取消與清理。

- 實施步驟：
  1. 換用 IAsyncEnumerable 串流
     - 實作細節：yield return token；支援取消。
     - 所需資源：C# 8+。
     - 預估時間：0.5 天
  2. UI 緩衝與取消
     - 實作細節：Channel<string> 對應 UI render loop。
     - 所需資源：System.Threading.Channels。
     - 預估時間：0.5 天
  3. 錯誤與重試
     - 實作細節：中斷時釋放資源、記錄 partial。
     - 所需資源：ILogger、Polly。
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
public async IAsyncEnumerable<string> AskStreamAsync(
    string prompt, SessionState session, [EnumeratorCancellation] CancellationToken ct)
{
    await foreach (var tk in _provider.StreamTokensAsync(session.History, prompt, ct))
    {
        ct.ThrowIfCancellationRequested();
        yield return tk; // 最快 TTFB
    }
}
```

- 實際案例：Console UI 以 Ctrl+C 取消當前生成，UI 立即停止，記錄 partial tokens。
- 實作環境：.NET 8、Channels、Polly。
- 實測數據：
  - 改善前：TTFB 約 1.8s、無法取消。
  - 改善後：TTFB 約 0.3s、可 <50ms 內取消。
  - 改善幅度：TTFB 降低 83%；中途取消成功率 100%。

Learning Points（學習要點）
- 核心知識點：IAsyncEnumerable、取消語意、背壓與緩衝。
- 技能要求：
  - 必備技能：非同步程式、CancellationToken。
  - 進階技能：Channel/背壓、Polly 重試。
- 延伸思考：如何顯示 partial 並標示為草稿？如何在取消後保留上下文？
- Practice Exercise：
  - 基礎：將 IEnumerable 改為 IAsyncEnumerable（30 分）
  - 進階：加入 Channel 緩衝與取消（2 小時）
  - 專案：串流 UI + 可恢復取消的對話器（8 小時）
- Assessment Criteria：
  - 功能完整性（40%）：串流/取消完整
  - 程式碼品質（30%）：清理與資源管理
  - 效能（20%）：TTFB、CPU 利用
  - 創新（10%）：背壓策略

------------------------------------------------------------

## Case #3: 對話 SessionState 與上下文記憶

### Problem Statement（問題陳述）
- 業務場景：多輪對話需要歷史與系統指示（instructions），並可能使用工具。系統須在擴展時不遺失上下文。
- 技術挑戰：如何管理長對話歷史、容量與隱私；如何在不同 Worker 間傳遞一致上下文。
- 影響範圍：回答品質、可擴展性、隱私合規。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 對話歷史散落於 Worker 記憶體。
  2. 缺乏統一 Session 模型與序列化策略。
  3. 工具與歷史耦合不清。
- 深層原因：
  - 架構層面：狀態與邏輯未分離。
  - 技術層面：缺乏持久化與修剪策略。
  - 流程層面：無對歷史大小與保留策略的標準。

### Solution Design（解決方案設計）
- 解決策略：SessionState 作為單一真實來源（SSOT），包含歷史、指示與工具清單。提供序列化、修剪（摘要）、敏感遮罩（PII）。

- 實施步驟：
  1. 定義 SessionState 結構
     - 實作細節：History、Instructions、Tools、Metadata。
     - 所需資源：System.Text.Json。
     - 預估時間：0.5 天
  2. 修剪與摘要
     - 實作細節：超出長度時做壓縮摘要。
     - 所需資源：可呼叫內建 LLM 摘要。
     - 預估時間：1 天
  3. 隱私與遮罩
     - 實作細節：PII 掃描器、遮罩策略。
     - 所需資源：正則/敏感字典。
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
public sealed class SessionState
{
    public string SessionId { get; init; } = Guid.NewGuid().ToString();
    public List<ChatMessage> History { get; } = new();
    public string? Instructions { get; set; }
    public Dictionary<string, Func<string, Task<string>>> Tools { get; } = new();
    public int MaxTokensInHistory { get; set; } = 4000;

    public void AddTool(string name, Func<string, Task<string>> fn) => Tools[name] = fn;

    public void AddUser(string text) => History.Add(new("user", text));
    public void AddAssistant(string text) => History.Add(new("assistant", text));

    public string ToJson() => JsonSerializer.Serialize(this);
    public static SessionState FromJson(string json) => JsonSerializer.Deserialize<SessionState>(json)!;
}
```

- 實際案例：Worker 重啟或切換後，從 SessionState JSON 完整恢復對話。
- 實作環境：.NET 8、JsonSerializer。
- 實測數據：
  - 改善前：Worker 切換後上下文丟失率 100%。
  - 改善後：上下文保留率 100%；平均恢復時間 < 20ms。
  - 改善幅度：服務恢復可用性大幅提升。

Learning Points（學習要點）
- 核心知識點：狀態外部化、會話修剪、PII 遮罩。
- 技能要求：
  - 必備技能：序列化、資料建模。
  - 進階技能：歷史摘要策略與權衡。
- 延伸思考：是否使用外部 KV/向量庫儲存長期記憶？
- Practice Exercise：
  - 基礎：加上 Instructions 欄位並在提示詞前置（30 分）
  - 進階：對超長歷史做摘要後替換（2 小時）
  - 專案：將 SessionState 存入 Redis 並支援復原（8 小時）
- Assessment Criteria：
  - 功能（40%）：序列化/修剪/遮罩
  - 品質（30%）：資料一致性
  - 效能（20%）：恢復延遲
  - 創新（10%）：摘要策略

------------------------------------------------------------

## Case #4: 接線生 Operator 與交換器 Switch 的分派設計

### Problem Statement（問題陳述）
- 業務場景：系統需像 Uber 一樣，將用戶對話分派給「空閒的人類或 AI 工人」以回覆。要確保高併發下公平排程與低等待。
- 技術挑戰：分派策略、資源健康檢查、錯誤轉移、會話黏性。
- 影響範圍：吞吐量、等待時間、穩定性。
- 複雜度評級：高

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 直連 Worker，缺乏調度層。
  2. 無健康度或負載監控。
  3. 無會話黏性策略（同一對話固定同一 Worker）。
- 深層原因：
  - 架構層面：缺少中介人（Operator/Switch）。
  - 技術層面：沒有標準化的分派契約。
  - 流程層面：無排程策略與 SLO 定義。

### Solution Design（解決方案設計）
- 解決策略：引入 Operator（接線生）與 Switch（交換器），Operator 管理 Worker 資源與分派策略，Switch 維持會話路徑，並監控健康狀態與重試。

- 實施步驟：
  1. 定義 IOperator/ISwitch
     - 實作細節：Dispatch/Release、HealthCheck、StickySession。
     - 所需資源：C# 介面。
     - 預估時間：1 天
  2. 實作最小策略（RR/LeastLoaded）
     - 實作細節：記錄 Worker 活動指標。
     - 所需資源：ConcurrentDictionary。
     - 預估時間：1 天
  3. 健康檢查與降級
     - 實作細節：超時/失敗即移除，降級至次選供應商。
     - 所需資源：Polly、Metrics。
     - 預估時間：1 天

- 關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
public interface IOperator
{
    ValueTask<WorkerHandle> DispatchAsync(SessionState session, CancellationToken ct);
    void Release(WorkerHandle handle);
}

public interface ISwitch
{
    IIntelligence Route(WorkerHandle handle);
}

public sealed record WorkerHandle(string WorkerId, Uri Endpoint, bool Sticky);
```

- 實際案例：當 OpenAI 速率限制時，自動切換本地 Ollama，對話不中斷。
- 實作環境：.NET 8、Polly、Metrics（OpenTelemetry）。
- 實測數據：
  - 改善前：高峰期 P95 等待 2.1s，錯誤率 7%。
  - 改善後：P95 等待 0.8s，錯誤率 1.5%。
  - 改善幅度：等待降低 62%，錯誤率下降 78%。

Learning Points（學習要點）
- 核心知識點：資源池、分派策略、健康檢查。
- 技能要求：
  - 必備技能：平行處理、並發容器。
  - 進階技能：SLO/熔斷/降級策略。
- 延伸思考：是否要引入優先權佇列與 SLA 層級？
- Practice Exercise：
  - 基礎：實作 RR 分派（30 分）
  - 進階：加入失敗暫停（circuit breaker）（2 小時）
  - 專案：支援 Sticky Session + 降級（8 小時）
- Assessment Criteria：
  - 功能（40%）：分派/釋放/健康檢查
  - 品質（30%）：錯誤處理
  - 效能（20%）：P95 等待
  - 創新（10%）：降級策略

------------------------------------------------------------

## Case #5: Worker 切換與無狀態（Stateless）Worker 設計

### Problem Statement（問題陳述）
- 業務場景：對話期間 Worker 可能離線、超時或需切換供應商；系統需平滑交接不中斷。
- 技術挑戰：如何保留上下文、如何在不同模型間保持行為一致。
- 影響範圍：穩定性、體驗、SLO。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. Worker 內保留狀態，切換即中斷。
  2. 歷史不可攜，指示與工具未帶入。
  3. 缺乏標準交接流程。
- 深層原因：
  - 架構層面：狀態與執行未分離。
  - 技術層面：無上下文序列化契約。
  - 流程層面：沒有切換條件與路徑。

### Solution Design（解決方案設計）
- 解決策略：Worker 完全無狀態，每次請求送入完整 SessionState（或壓縮後）；Operator 檢測異常立即切換，Switch 將歷史與指示傳遞給新 Worker。

- 實施步驟：
  1. 會話打包
     - 實作細節：SessionState.ToJson() 打包。
     - 所需資源：JsonSerializer。
     - 預估時間：0.5 天
  2. Worker 接口改為接受狀態
     - 實作細節：Adapter 層反序列化並執行。
     - 所需資源：IIntelligence 介面擴充。
     - 預估時間：0.5 天
  3. 切換流程
     - 實作細節：超時/錯誤 -> 重新 Dispatch 並重送。
     - 所需資源：Polly、超時設定。
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
public async Task<string> AskAsync(string prompt, SessionState session, CancellationToken ct)
{
    var payload = session.ToJson();
    // 傳遞完整狀態給 stateless worker
    return await _provider.InvokeAsync(payload, prompt, ct);
}
```

- 實際案例：OpenAI 429/503 異常時改用本地模型續答，對話不中斷。
- 實作環境：.NET 8、Polly。
- 實測數據：
  - 改善前：異常續答失敗率 100%。
  - 改善後：異常續答成功率 95%（5% 因供應商全面性故障）。
  - 改善幅度：續答成功率 +95%。

Learning Points（學習要點）
- 核心知識點：無狀態服務、交接協定、錯誤恢復。
- 技能要求：
  - 必備技能：序列化、重試策略。
  - 進階技能：行為一致性與 Prompt 正規化。
- 延伸思考：如何在切換時對結果做一致性校對？
- Practice Exercise：
  - 基礎：讓 Worker 從 Session JSON 恢復（30 分）
  - 進階：設計切換觸發條件與記錄（2 小時）
  - 專案：異常注入測試（8 小時）
- Assessment Criteria：
  - 功能（40%）：交接可用
  - 品質（30%）：錯誤可觀察
  - 效能（20%）：切換延遲
  - 創新（10%）：一致性保障

------------------------------------------------------------

## Case #6: Tool Use 能力整合（函式呼叫）

### Problem Statement（問題陳述）
- 業務場景：僅回文字無法解任務，需要讓模型呼叫特定工具（查庫、發郵件、計算）。
- 技術挑戰：在抽象介面中表達「工具呼叫」與「文字回覆」並存；工具註冊與授權。
- 影響範圍：自動化能力與安全風險。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 介面只能回 string。
  2. 無工具登錄與授權清單。
  3. 無標準工具輸入輸出格式。
- 深層原因：
  - 架構層面：結果型別設計過於單一。
  - 技術層面：少了 union/variant 結構。
  - 流程層面：缺少工具審核流程。

### Solution Design（解決方案設計）
- 解決策略：回傳結果引入 Discriminated Union：Message 或 ToolCall；SessionState 保存 Tool registry，執行器負責安全與審批（可人工確認）。

- 實施步驟：
  1. 型別設計
     - 實作細節：Result = Message | ToolCall。
     - 所需資源：C# record。
     - 預估時間：0.5 天
  2. 工具註冊與授權
     - 實作細節：Tools 字典 + AllowList。
     - 所需資源：組態/ACL。
     - 預估時間：0.5 天
  3. 執行器與審批
     - 實作細節：工具執行前可人工確認。
     - 所需資源：UI 流程/審批旗標。
     - 預估時間：1 天

- 關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
public abstract record ChatResult;
public sealed record Message(string Text) : ChatResult;
public sealed record ToolCall(string ToolName, string ArgsJson) : ChatResult;

public class SessionState
{
    public Dictionary<string, Func<string, Task<string>>> Tools { get; } = new();
    public HashSet<string> AllowedTools { get; } = new();
}
```

- 實際案例：模型請求「getWeather(city=Taipei)」，通過審批後執行 API 回填結果到對話。
- 實作環境：.NET 8、JSON。
- 實測數據：
  - 改善前：任務需手動查詢，完成率低。
  - 改善後：工具可用任務一次完成率 92%。
  - 改善幅度：任務效率顯著提升。

Learning Points（學習要點）
- 核心知識點：Union 型別、工具註冊、最小權限。
- 技能要求：
  - 必備技能：JSON 序列化、函式包裝。
  - 進階技能：安全審批、審計紀錄。
- 延伸思考：如何將工具定義導出為 OpenAI function schema？
- Practice Exercise：
  - 基礎：註冊一個計算機工具（30 分）
  - 進階：加入允許清單與審批（2 小時）
  - 專案：三種工具（天氣/翻譯/郵件）整合（8 小時）
- Assessment Criteria：
  - 功能（40%）：工具呼叫可用
  - 品質（30%）：安全與審計
  - 效能（20%）：工具延遲
  - 創新（10%）：工具 schema 生成

------------------------------------------------------------

## Case #7: 多供應商 Adapter（OpenAI、Assistant API、Ollama）

### Problem Statement（問題陳述）
- 業務場景：產品要同時支援雲端（OpenAI/Assistant API）與本地（Ollama）模型，並快速切換。
- 技術挑戰：API 參數、串流協定、工具呼叫語意差異大。
- 影響範圍：開發效率、成本、上線速度。
- 複雜度評級：高

### Root Cause Analysis（根因分析）
- 直接原因：
  1. Chat Completion 與 Assistant API 模型不同（thread/run）。
  2. Ollama 的 REST/stream chunk 格式不同。
  3. 工具呼叫 schema 差異。
- 深層原因：
  - 架構層面：未建立 Provider 能力協商。
  - 技術層面：缺乏標準化轉換層。
  - 流程層面：接入驗收條件不明。

### Solution Design（解決方案設計）
- 解決策略：以 ProviderAdapter 封裝供應商細節，導入 Capability 探測與條件降級；提供統一 streaming/token 計數與工具 schema 映射。

- 實施步驟：
  1. 定義 ProviderAdapter 介面
     - 實作細節：Map SessionState -> Provider payload。
     - 所需資源：介面/抽象。
     - 預估時間：1 天
  2. 各供應商 Adapter 落地
     - 實作細節：OpenAI、Assistant、Ollama。
     - 所需資源：SDK/REST。
     - 預估時間：2-3 天
  3. 自動降級
     - 實作細節：功能缺失 -> 提示詞補償或關閉工具。
     - 所需資源：Capabilities。
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
public interface IProviderAdapter
{
    Capabilities Cap { get; }
    IAsyncEnumerable<string> StreamAsync(SessionState session, string prompt, CancellationToken ct);
    Task<string> CompleteAsync(SessionState session, string prompt, CancellationToken ct);
}
```

- 實際案例：在雲端限流時，自動切到 Ollama，功能差異以提示詞補償（無 tools 時要求模型回自然語回覆）。
- 實作環境：.NET 8、OpenAI SDK、Ollama REST。
- 実測數據：
  - 改善前：切換供應商需 3-5 天整合。
  - 改善後：新增一個 Adapter 1 天內完成。
  - 改善幅度：整合效率 +60~80%。

Learning Points（學習要點）
- 核心知識點：Adapter 模式、能力協商、降級策略。
- 技能要求：
  - 必備技能：REST/SDK 整合。
  - 進階技能：語意對齊、工具 schema 映射。
- 延伸思考：是否需要策略機（Strategy）選擇最適供應商？
- Practice Exercise：
  - 基礎：實作 DummyAdapter（30 分）
  - 進階：完成 OllamaAdapter 串流（2 小時）
  - 專案：整合 OpenAI + Ollama + 自動降級（8 小時）
- Assessment Criteria：
  - 功能（40%）：三適配器可用
  - 品質（30%）：降級正確
  - 效能（20%）：切換延遲
  - 創新（10%）：自動選路

------------------------------------------------------------

## Case #8: gRPC「工人智慧」通訊協定

### Problem Statement（問題陳述）
- 業務場景：在 2010s 的「工人智慧」模式下，以 gRPC 連接真人坐席（Worker App）與平台。
- 技術挑戰：雙向串流、心跳、掉線恢復、延遲控制。
- 影響範圍：擴展性、使用者體驗、成本。
- 複雜度評級：高

### Root Cause Analysis（根因分析）
- 直接原因：
  1. HTTP/輪詢延遲大且不穩。
  2. 無心跳與重新連線機制。
  3. 無案件分派/釋放 API。
- 深層原因：
  - 架構層面：沒有正式通訊協定。
  - 技術層面：串流與狀態管理欠缺。
  - 流程層面：坐席上線/下線流程不明。

### Solution Design（解決方案設計）
- 解決策略：定義 gRPC Proto，包含雙向串流 Chat、心跳、分派 RPC。以 WorkerId 維持黏性，Operator 管控名單與健康度。

- 實施步驟：
  1. 定義 Proto 介面
     - 實作細節：Chat(stream) 與 Heartbeat RPC。
     - 所需資源：Grpc.AspNetCore。
     - 預估時間：1 天
  2. 服務端與客戶端
     - 實作細節：雙向串流處理與重連。
     - 所需資源：gRPC Stub。
     - 預估時間：1 天
  3. 分派整合
     - 實作細節：Operator 與 Worker 列表整合。
     - 所需資源：ConcurrentDictionary。
     - 預估時間：1 天

- 關鍵程式碼/設定：
```proto
// Implementation Example（實作範例） - gRPC
service Worker {
  rpc Chat (stream ChatPacket) returns (stream ChatPacket);
  rpc Heartbeat (HeartbeatRequest) returns (HeartbeatReply);
}

message ChatPacket { string sessionId = 1; string role = 2; string content = 3; }
message HeartbeatRequest { string workerId = 1; }
message HeartbeatReply { bool ok = 1; }
```

- 實際案例：真人坐席可同時處理多會話，平台實時分派與回收。
- 實作環境：.NET 8、Grpc。
- 實測數據：
  - 改善前：HTTP 輪詢 P95 延遲 1200ms。
  - 改善後：gRPC P95 延遲 180ms。
  - 改善幅度：延遲降低 85%。

Learning Points（學習要點）
- 核心知識點：gRPC 雙向串流、心跳與重連。
- 技能要求：
  - 必備技能：Proto 定義、串流。
  - 進階技能：分派策略與回收。
- 延伸思考：是否要支援 WebSocket 作為瀏覽器坐席？
- Practice Exercise：
  - 基礎：完成 Heartbeat RPC（30 分）
  - 進階：雙向串流 Chat（2 小時）
  - 專案：Operator + Worker 完整 POC（8 小時）
- Assessment Criteria：
  - 功能（40%）：雙向串流可用
  - 品質（30%）：重連穩定
  - 效能（20%）：P95 延遲
  - 創新（10%）：動態擴容

------------------------------------------------------------

## Case #9: Token 計費與成本控管

### Problem Statement（問題陳述）
- 業務場景：多供應商下成本失控，團隊需統一計費、預算與告警。
- 技術挑戰：不同 token 規則（模型/供應商差異）、串流計數、工具回合計價。
- 影響範圍：營運成本、利潤率、預算風險。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 未統一 token 計數。
  2. 缺乏每請求成本估算與上限。
  3. 無模型/供應商成本對比。
- 深層原因：
  - 架構層面：無成本計量中介層。
  - 技術層面：未導入 tokenizer。
  - 流程層面：未設成本政策與警戒線。

### Solution Design（解決方案設計）
- 解決策略：導入 TokenMeter 中介層攔截請求，標準化 token 計數、估算成本，設置配額與超額阻擋；儀表板與警報。

- 實施步驟：
  1. Tokenizer 整合
     - 實作細節：TiktokenSharp 或相容庫。
     - 所需資源：NuGet 套件。
     - 預估時間：0.5 天
  2. 中介層計量
     - 實作細節：請求/回應 token 與成本記錄。
     - 所需資源：中介裝飾器。
     - 預估時間：1 天
  3. 預算與告警
     - 實作細節：配額與 Slack/Email 告警。
     - 所需資源：監控工具。
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
public sealed class TokenMeter : IIntelligence
{
    private readonly IIntelligence _inner; private readonly ICostModel _cost;
    public TokenMeter(IIntelligence inner, ICostModel cost){ _inner=inner; _cost=cost; }

    public async Task<string> AskAsync(string prompt, SessionState s, ChatOptions? o=null, CancellationToken ct=default)
    {
        var inTokens = _cost.CountTokens(s.History, prompt);
        var text = await _inner.AskAsync(prompt, s, o, ct);
        var outTokens = _cost.CountTokens(text);
        var price = _cost.Estimate(inTokens, outTokens);
        // 記錄成本與配額檢查
        return text;
    }

    public IAsyncEnumerable<string> AskStreamAsync(string prompt, SessionState s, ChatOptions? o=null, CancellationToken ct=default)
        => _inner.AskStreamAsync(prompt, s, o, ct);
    public Capabilities GetCapabilities()=>_inner.GetCapabilities();
}
```

- 實際案例：對每個使用者/專案設定月度配額與每日上限，超過即停用或降級到本地模型。
- 實作環境：.NET 8、TiktokenSharp、OpenTelemetry。
- 實測數據：
  - 改善前：月度超支 22%。
  - 改善後：成本控制在預算 ±5% 內。
  - 改善幅度：超支風險大幅降低。

Learning Points（學習要點）
- 核心知識點：token 統計、成本模型、中介層。
- 技能要求：
  - 必備技能：字串處理、Decorator。
  - 進階技能：告警/配額策略。
- 延伸思考：是否依任務自動選擇性價比最佳模型？
- Practice Exercise：
  - 基礎：計算一次請求的 token（30 分）
  - 進階：建立成本估算器（2 小時）
  - 專案：配額+告警+降級流程（8 小時）
- Assessment Criteria：
  - 功能（40%）：計費/配額可用
  - 品質（30%）：計數準確
  - 效能（20%）：計量開銷
  - 創新（10%）：自動模型選擇

------------------------------------------------------------

## Case #10: 圖靈測試應用架構（Human vs AI）

### Problem Statement（問題陳述）
- 業務場景：建立可盲測的人與 AI 回覆系統，評估可用性與自然度。
- 技術挑戰：同一介面對接 AI 或真人，並匿名化來源避免偏見。
- 影響範圍：產品決策、模型選型、UX。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 沒有統一介面抽象。
  2. 記錄與顯示中洩漏來源。
  3. 測試流程不標準。
- 深層原因：
  - 架構層面：無對等實作（HumanIntelligence、ArtifactIntelligence）。
  - 技術層面：匿名化缺失。
  - 流程層面：缺少盲測規程。

### Solution Design（解決方案設計）
- 解決策略：HumanIntelligence 與 ArtifactIntelligence 實作同一介面；記錄層匿名化來源；測試儀表與問卷收集。

- 實施步驟：
  1. 實作兩種 Intelligence
     - 實作細節：同介面、不同來源。
     - 所需資源：IIntelligence。
     - 預估時間：0.5 天
  2. 匿名化與隨機分配
     - 實作細節：隨機給測試者，隱藏來源。
     - 所需資源：Operator。
     - 預估時間：0.5 天
  3. 統計與問卷
     - 實作細節：主觀/客觀分數。
     - 所需資源：儀表板。
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
public sealed class HumanIntelligence : IIntelligence { /* 聊天由人類坐席完成 */ }
public sealed class ArtifactIntelligence : IIntelligence { /* AI Provider 完成 */ }
```

- 實際案例：10 位內部測試者盲測，收集偏好與自然度評分。
- 實作環境：.NET 8、簡易 Web 前端。
- 實測數據：
  - 改善前：無法量化自然度。
  - 改善後：收集有效問卷 50 份，AI 自然度 4.1/5。
  - 改善幅度：決策依據明確化。

Learning Points（學習要點）
- 核心知識點：對等抽象、盲測。
- 技能要求：
  - 必備技能：介面設計。
  - 進階技能：統計分析。
- 延伸思考：如何自動化 AB 測試與多臂土 bandit？
- Practice Exercise：
  - 基礎：建立 FakeHuman（鍵入回覆）（30 分）
  - 進階：盲測切換器（2 小時）
  - 專案：盲測統計儀表板（8 小時）
- Assessment Criteria：
  - 功能（40%）：雙來源切換
  - 品質（30%）：匿名化正確
  - 效能（20%）：回覆延遲統計
  - 創新（10%）：自動分流

------------------------------------------------------------

## Case #11: 本地推理整合（Ollama/OnnxRuntime）

### Problem Statement（問題陳述）
- 業務場景：資料敏感或離線環境需在邊緣/本地執行推理，降低成本與風險。
- 技術挑戰：本地環境安裝、性能、與雲端 API 行為差異。
- 影響範圍：成本、隱私、延遲。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 僅使用雲端 API。
  2. 未提供本地 Adapter。
  3. 無行為對齊策略。
- 深層原因：
  - 架構層面：依賴單一供應商。
  - 技術層面：本地推理經驗缺乏。
  - 流程層面：部署流程未涵蓋本地。

### Solution Design（解決方案設計）
- 解決策略：建立 OllamaAdapter 與 OnnxRuntimeAdapter，提供相同 IIntelligence 行為；加入提示詞正規化策略縮小差異。

- 實施步驟：
  1. 安裝本地推理環境
     - 實作細節：Ollama 模型 pull、OnnxRuntime 初始化。
     - 所需資源：Ollama/OnnxRuntime。
     - 預估時間：0.5-1 天
  2. Adapter 實作
     - 實作細節：串流/非串流輸出。
     - 所需資源：REST/Native。
     - 預估時間：1 天
  3. 行為對齊
     - 實作細節：prompt 模板化、一致性測試。
     - 所需資源：測試集。
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
public sealed class OllamaAdapter : IProviderAdapter
{
    public Capabilities Cap => new(true, false);
    public async IAsyncEnumerable<string> StreamAsync(SessionState s, string prompt, [EnumeratorCancellation] CancellationToken ct)
    {
        // 呼叫 Ollama /api/generate 串流解析
        yield return "...";
    }
    public Task<string> CompleteAsync(SessionState s, string prompt, CancellationToken ct) => Task.FromResult("...");
}
```

- 實際案例：月成本超支時，晚間時段降級使用本地模型，敏感資料只走本地。
- 實作環境：.NET 8、Ollama、OnnxRuntime。
- 實測數據：
  - 改善前：月成本高、敏感資料外流風險。
  - 改善後：雲端成本降低 55%，敏感資料外發 0 件。
  - 改善幅度：成本/風險雙降。

Learning Points（學習要點）
- 核心知識點：本地推理、行為對齊。
- 技能要求：
  - 必備技能：REST、模型部署。
  - 進階技能：Prompt 正規化。
- 延伸思考：如何以 GPU/量化提升本地性能？
- Practice Exercise：
  - 基礎：安裝並呼叫 Ollama（30 分）
  - 進階：實作串流解析（2 小時）
  - 專案：雲端/本地動態切換（8 小時）
- Assessment Criteria：
  - 功能（40%）：本地可用
  - 品質（30%）：行為一致
  - 效能（20%）：延遲與吞吐
  - 創新（10%）：動態策略

------------------------------------------------------------

## Case #12: 背壓與限流（Channel + Token-Bucket）

### Problem Statement（問題陳述）
- 業務場景：高峰時大量請求湧入，供應商速率限制與服務緩慢導致崩潰。
- 技術挑戰：公平排隊、速率控制、取消過期請求、避免雪崩。
- 影響範圍：服務可用性、成本、SLO。
- 複雜度評級：高

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 沒有排隊與背壓機制。
  2. 無全球/供應商速率控制。
  3. 超時處理不當。
- 深層原因：
  - 架構層面：缺少佇列與節流層。
  - 技術層面：對並發控制不足。
  - 流程層面：無峰值治理策略。

### Solution Design（解決方案設計）
- 解決策略：導入 Channel 作為請求佇列，Token-Bucket 實施供應商/全域限流，過期請求丟棄；結合熔斷/退避。

- 實施步驟：
  1. 佇列與工作者
     - 實作細節：ChannelReader/Writer。
     - 所需資源：System.Threading.Channels。
     - 預估時間：1 天
  2. 速率限制
     - 實作細節：每供應商 token 桶。
     - 所需資源：計時器。
     - 預估時間：0.5 天
  3. 超時/取消
     - 實作細節：傳遞 CancellationToken/Deadline。
     - 所需資源：Polly。
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
var queue = Channel.CreateBounded<Request>(new BoundedChannelOptions(1000){FullMode=BoundedChannelFullMode.DropOldest});
```

- 實際案例：高峰每分鐘 3000 請求時保持穩定，無連鎖失敗。
- 實作環境：.NET 8、Channels、Polly。
- 實測數據：
  - 改善前：錯誤率 12%，P99 延遲 > 10s。
  - 改善後：錯誤率 < 2%，P99 延遲 2.1s。
  - 改善幅度：穩定性大幅提升。

Learning Points（學習要點）
- 核心知識點：背壓、限流、佇列。
- 技能要求：
  - 必備技能：並發控制。
  - 進階技能：熔斷/退避。
- 延伸思考：是否需要優先權佇列和多租戶隔離？
- Practice Exercise：
  - 基礎：建立 bounded channel（30 分）
  - 進階：token bucket 實作（2 小時）
  - 專案：高峰壓測方案（8 小時）
- Assessment Criteria：
  - 功能（40%）：限流生效
  - 品質（30%）：過期丟棄
  - 效能（20%）：P99/錯誤率
  - 創新（10%）：優先權

------------------------------------------------------------

## Case #13: 觀測性與追蹤（Logs/Metrics/Traces）

### Problem Statement（問題陳述）
- 業務場景：跨供應商、跨 Worker 的問題難以定位，需要精準觀測與追蹤。
- 技術挑戰：串流 token 計量、分派路徑、錯誤關聯、成本追蹤。
- 影響範圍：故障修復時間、成本透明度。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 無 requestId/sessionId。
  2. 串流過程未記錄 token 速率。
  3. 成本/錯誤散落於多處。
- 深層原因：
  - 架構層面：缺乏觀測性標準。
  - 技術層面：分散式追蹤缺失。
  - 流程層面：無事件命名規範。

### Solution Design（解決方案設計）
- 解決策略：統一 Correlation ID，建立三支柱（logs/metrics/traces），將成本與分派資訊入指標；OpenTelemetry 全線打點。

- 實施步驟：
  1. Correlation 與命名
     - 實作細節：Session/Request ID。
     - 所需資源：活動（Activity）。
     - 預估時間：0.5 天
  2. 指標與分佈
     - 實作細節：latency、tokens、cost。
     - 所需資源：OTel/Meter。
     - 預估時間：1 天
  3. 追蹤
     - 實作細節：分派->Adapter->Provider。
     - 所需資源：OTel Tracing。
     - 預估時間：1 天

- 關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
using var activity = MyActivitySource.StartActivity("Ask");
activity?.SetTag("session.id", session.SessionId);
activity?.SetTag("provider", currentProvider);
```

- 實際案例：費用暴增時快速定位到特定工具被濫用。
- 實作環境：.NET 8、OpenTelemetry。
- 實測數據：
  - 改善前：定位時間 4 小時。
  - 改善後：定位時間 20 分鐘。
  - 改善幅度：MTTR -92%。

Learning Points（學習要點）
- 核心知識點：OTel、指標設計。
- 技能要求：
  - 必備技能：記錄/量測。
  - 進階技能：分散式追蹤。
- 延伸思考：如何以 tracing 驅動動態路由與熔斷？
- Practice Exercise：
  - 基礎：加入 requestId（30 分）
  - 進階：加入 tokens/sec 指標（2 小時）
  - 專案：完整 OTel 管線（8 小時）
- Assessment Criteria：
  - 功能（40%）：三支柱齊備
  - 品質（30%）：一致命名
  - 效能（20%）：打點開銷
  - 創新（10%）：指標驅動路由

------------------------------------------------------------

## Case #14: 錯誤處理與重試（含串流恢復）

### Problem Statement（問題陳述）
- 業務場景：外部 API 可能 429/5xx/網路中斷，串流中途斷線常見。
- 技術挑戰：安全重試、串流恢復、避免重複工具操作。
- 影響範圍：可用性、資料一致性、成本。
- 複雜度評級：高

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 串流中斷不處理。
  2. 工具呼叫無冪等保證。
  3. 無分類重試策略。
- 深層原因：
  - 架構層面：缺乏中介容錯層。
  - 技術層面：冪等鍵缺失。
  - 流程層面：錯誤分類不明。

### Solution Design（解決方案設計）
- 解決策略：Polly 實作指數退避重試；串流以「段落重試」策略恢復；工具以冪等鍵與 side-effect 防護。

- 實施步驟：
  1. 錯誤分類與策略
     - 實作細節：429/5xx 重試，4xx 不重試。
     - 所需資源：Polly。
     - 預估時間：0.5 天
  2. 串流恢復
     - 實作細節：保留 partial，重試接續。
     - 所需資源：緩衝區。
     - 預估時間：1 天
  3. 工具冪等
     - 實作細節：Idempotency-Key。
     - 所需資源：存儲層。
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
var retry = Policy.Handle<HttpRequestException>()
    .OrResult<HttpResponseMessage>(r => (int)r.StatusCode >= 500)
    .WaitAndRetryAsync(3, i => TimeSpan.FromMilliseconds(200 * Math.Pow(2, i)));
```

- 實際案例：串流中斷 2 次仍可完整輸出，工具不重複執行。
- 實作環境：.NET 8、Polly。
- 實測數據：
  - 改善前：串流失敗率 9%。
  - 改善後：串流失敗率 1.2%。
  - 改善幅度：-86.6%。

Learning Points（學習要點）
- 核心知識點：退避重試、冪等。
- 技能要求：
  - 必備技能：錯誤分類。
  - 進階技能：串流接續。
- 延伸思考：如何實現跨供應商的「續答」？
- Practice Exercise：
  - 基礎：對 5xx 啟用重試（30 分）
  - 進階：串流恢復機制（2 小時）
  - 專案：冪等工具框架（8 小時）
- Assessment Criteria：
  - 功能（40%）：重試/恢復有效
  - 品質（30%）：冪等與審計
  - 效能（20%）：額外延遲
  - 創新（10%）：跨供應商續答

------------------------------------------------------------

## Case #15: 版本演進與能力協商（Assistant v2 等）

### Problem Statement（問題陳述）
- 業務場景：供應商頻繁更新（Chat Completion -> Assistant v2），舊碼易壞、升級成本高。
- 技術挑戰：功能差異（threads/runs/tools）、行為變更。
- 影響範圍：開發效率、相容性、穩定性。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 直接耦合舊 API。
  2. 缺少能力偵測與條件流程。
  3. 無版本旗標與降級。
- 深層原因：
  - 架構層面：抽象不穩。
  - 技術層面：缺乏 Feature Flag。
  - 流程層面：升級驗收不足。

### Solution Design（解決方案設計）
- 解決策略：Capabilities + Feature Flags；在 Adapter 內做版本差異映射；設計降級路徑（無 threads 時以 SessionState 模擬）。

- 實施步驟：
  1. 能力偵測
     - 實作細節：開機時呼叫 /models 或 capability API。
     - 所需資源：SDK/REST。
     - 預估時間：0.5 天
  2. Feature Flags
     - 實作細節：By env/tenant。
     - 所需資源：組態服務。
     - 預估時間：0.5 天
  3. 映射與降級
     - 實作細節：threads->SessionState 映射。
     - 所需資源：Adapter 層。
     - 預估時間：1 天

- 關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
public record Capabilities(bool SupportsStreaming, bool SupportsTools, bool SupportsThreads);
```

- 實際案例：預先以 SessionState 模擬 threads，改版後一鍵切換至官方 threads。
- 實作環境：.NET 8、FeatureFlag。
- 實測數據：
  - 改善前：升級需 2 週。
  - 改善後：升級 2 天完成。
  - 改善幅度：時間縮短 85%。

Learning Points（學習要點）
- 核心知識點：能力協商、降級設計。
- 技能要求：
  - 必備技能：版本管理。
  - 進階技能：旗標治理。
- 延伸思考：如何自動化契約測試來驗證升級？
- Practice Exercise：
  - 基礎：加入 SupportsThreads（30 分）
  - 進階：threads->Session 映射（2 小時）
  - 專案：旗標驅動升級流程（8 小時）
- Assessment Criteria：
  - 功能（40%）：能力/旗標生效
  - 品質（30%）：映射正確
  - 效能（20%）：升級停機最小化
  - 創新（10%）：自動校驗

------------------------------------------------------------

## Case #16: 安全與權限（API Key、工具 RBAC）

### Problem Statement（問題陳述）
- 業務場景：多供應商金鑰管理複雜，工具呼叫涉及外部系統，需權限與審計。
- 技術挑戰：金鑰保護、按使用者/專案授權工具。
- 影響範圍：資安、合規、風險。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 硬編金鑰。
  2. 工具無 RBAC。
  3. 無審計與告警。
- 深層原因：
  - 架構層面：缺少金鑰與權限層。
  - 技術層面：密鑰保存與輪替。
  - 流程層面：審批缺失。

### Solution Design（解決方案設計）
- 解決策略：金鑰放置於 Vault；工具引入 RBAC（角色/資源/操作）；所有工具呼叫記錄審計日志並告警。

- 實施步驟：
  1. 金鑰治理
     - 實作細節：Azure Key Vault/AWS KMS。
     - 所需資源：雲端祕密管理。
     - 預估時間：0.5 天
  2. 工具 RBAC
     - 實作細節：使用者->角色->工具權限。
     - 所需資源：DB 結構。
     - 預估時間：1 天
  3. 審計與告警
     - 實作細節：每次工具執行記錄與告警。
     - 所需資源：Logging/Alert。
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
public bool CanInvokeTool(User u, string toolName) => _rbac.IsAllowed(u.Role, toolName, "invoke");
```

- 實際案例：郵件發送工具限制僅客服主管可呼叫，異常行為即時告警。
- 實作環境：.NET 8、Key Vault。
- 實測數據：
  - 改善前：金鑰外洩 1 起/月。
  - 改善後：0 起；未授權工具阻擋率 100%。
  - 改善幅度：重大風險消除。

Learning Points（學習要點）
- 核心知識點：金鑰治理、RBAC、審計。
- 技能要求：
  - 必備技能：祕密管理。
  - 進階技能：授權模型設計。
- 延伸思考：是否需要 ABAC/PBAC 精細權限？
- Practice Exercise：
  - 基礎：改用 Vault 讀取金鑰（30 分）
  - 進階：簡易 RBAC（2 小時）
  - 專案：審計與告警串接（8 小時）
- Assessment Criteria：
  - 功能（40%）：金鑰/RBAC/審計
  - 品質（30%）：安全實作
  - 效能（20%）：查詢延遲
  - 創新（10%）：細粒度政策

------------------------------------------------------------

## Case #17: 測試策略與契約測試（Adapters/Providers）

### Problem Statement（問題陳述）
- 業務場景：外部依賴使測試不穩定，且介面變動常破壞功能。
- 技術挑戰：隔離外部系統、可重現、快速。
- 影響範圍：開發效率、品質。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 測試直打雲端。
  2. 無契約測試。
  3. 未建假伺服器。
- 深層原因：
  - 架構層面：未抽象 Providers。
  - 技術層面：缺少 stub/mock。
  - 流程層面：CI 不穩。

### Solution Design（解決方案設計）
- 解決策略：為每個 ProviderAdapter 撰寫契約測試；使用 TestServer/WireMock 建 stub；以錄製回放降低外部依賴。

- 實施步驟：
  1. 建立契約測試
     - 實作細節：對輸入/輸出與錯誤語義測試。
     - 所需資源：xUnit/NUnit。
     - 預估時間：1 天
  2. Stub/Mock 伺服器
     - 實作細節：WireMock.Net。
     - 所需資源：NuGet。
     - 預估時間：0.5 天
  3. 錄製回放
     - 實作細節：確保一致性。
     - 所需資源：中介器。
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
// 驗證 StreamAsync 對 429/5xx 的語義
[Fact] public async Task Provider_Stream_Retry_On_5xx() { /* ... */ }
```

- 實際案例：升級 OpenAI SDK 後，契約測試即時發現工具 schema 變動。
- 實作環境：.NET 8、xUnit、WireMock.Net。
- 實測數據：
  - 改善前：回歸缺陷 6 起/月。
  - 改善後：回歸缺陷 1 起/月。
  - 改善幅度：-83%。

Learning Points（學習要點）
- 核心知識點：契約測試、錄放。
- 技能要求：
  - 必備技能：單元/整合測試。
  - 進階技能：Mock/Stub 設計。
- 延伸思考：是否用 Pact 做跨團隊契約？
- Practice Exercise：
  - 基礎：為 Adapter 寫第一個契約測試（30 分）
  - 進階：WireMock stub（2 小時）
  - 專案：CI 契約閘門（8 小時）
- Assessment Criteria：
  - 功能（40%）：測試覆蓋
  - 品質（30%）：可重現
  - 效能（20%）：測試時間
  - 創新（10%）：錄放方案

------------------------------------------------------------

## Case #18: 從 Chat Completion 遷移到 Assistant API

### Problem Statement（問題陳述）
- 業務場景：現有系統基於 Chat Completion，需要遷移至 Assistant API（threads/runs/tools）以獲得更豐富能力。
- 技術挑戰：資料模型差異、行為變更、相容舊有流程。
- 影響範圍：開發時間、風險、使用者體驗。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. Chat Completion 與 Assistant API 概念差異大。
  2. 直接改動業務層易破壞。
  3. 測試用例不齊。
- 深層原因：
  - 架構層面：未以抽象介面隔離。
  - 技術層面：缺工具 schema 映射。
  - 流程層面：缺升級計畫與旗標切換。

### Solution Design（解決方案設計）
- 解決策略：在 Adapter 層完成 threads/runs 與 SessionState 的映射；以 Feature Flag 控制灰度，並設回滾路徑。

- 實施步驟：
  1. 模型映射
     - 實作細節：thread=SessionId、run=一次 Ask。
     - 所需資源：Adapter。
     - 預估時間：1 天
  2. 工具 schema 映射
     - 實作細節：Functions->Tools。
     - 所需資源：JSON schema。
     - 預估時間：0.5 天
  3. 灰度切換與回滾
     - 實作細節：旗標、分流、回退。
     - 所需資源：FeatureFlag。
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
public sealed class AssistantAdapter : IProviderAdapter
{
    // Map SessionState -> Thread; Ask -> Run; Tools -> Function calling
}
```

- 實際案例：10% 使用者先行使用 Assistant API，問題收斂後全量切換。
- 實作環境：.NET 8、OpenAI Assistant API。
- 實測數據：
  - 改善前：一次性切換造成 2 天不穩。
  - 改善後：灰度 1 週無重大事故。
  - 改善幅度：風險大幅降低。

Learning Points（學習要點）
- 核心知識點：資料模型映射、灰度與回滾。
- 技能要求：
  - 必備技能：Adapter。
  - 進階技能：變更管理。
- 延伸思考：是否要建立雙寫比對期間的差異分析？
- Practice Exercise：
  - 基礎：映射 thread/run 概念（30 分）
  - 進階：工具 schema 轉換（2 小時）
  - 專案：灰度/回滾腳本（8 小時）
- Assessment Criteria：
  - 功能（40%）：映射準確
  - 品質（30%）：灰度可控
  - 效能（20%）：切換延遲
  - 創新（10%）：差異比對

------------------------------------------------------------

案例分類

1) 按難度分類
- 入門級：Case 1, 2, 10
- 中級：Case 3, 5, 6, 7, 9, 11, 13, 15, 16, 17, 18
- 高級：Case 4, 8, 12, 14

2) 按技術領域分類
- 架構設計類：Case 1, 3, 4, 5, 7, 10, 15, 18
- 效能優化類：Case 2, 11, 12, 13, 14
- 整合開發類：Case 6, 7, 8, 11, 18
- 除錯診斷類：Case 13, 14, 17
- 安全防護類：Case 9, 16

3) 按學習目標分類
- 概念理解型：Case 1, 3, 10, 15
- 技能練習型：Case 2, 6, 8, 11, 12, 17
- 問題解決型：Case 4, 5, 9, 13, 14, 16, 18
- 創新應用型：Case 7, 11, 12, 15

案例關聯圖（學習路徑建議）
- 基礎先學：Case 1（抽象介面）、Case 2（串流）、Case 3（SessionState）
- 中階拓展：
  - 路由與分派：Case 4（Operator/Switch）-> Case 5（無狀態切換）
  - 工具能力：Case 6（Tool Use）
  - 多供應商：Case 7（Adapter）
- 實務整合：
  - 本地/雲端混合：Case 11（本地推理）
  - 成本/安全：Case 9（Token 成本）、Case 16（安全）
  - 觀測與穩定：Case 13（觀測）、Case 14（重試）、Case 12（限流）
- 測試與演進：
  - Case 17（契約測試）→ Case 15（能力協商）→ Case 18（Assistant 遷移）
- 依賴關係摘要：
  - Case 4 依賴 Case 1-3
  - Case 5 依賴 Case 3-4
  - Case 7 依賴 Case 1-3
  - Case 12 依賴 Case 4
  - Case 14 依賴 Case 2, 7
  - Case 18 依賴 Case 7, 15, 17
- 完整學習路徑：
  1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 11 -> 9 -> 16 -> 13 -> 12 -> 14 -> 17 -> 15 -> 18 -> 8 -> 10
  - 說明：先奠定抽象/串流/狀態基礎；再進入分派與工具；完成供應商適配與本地化；加入成本與安全；建立觀測與穩定性；最後導入測試、版本協商與遷移；gRPC 工人與圖靈測試作為延展實作。

說明
- 本文各「實測數據」為 POC 示意指標與可驗證的度量建議，用於教學與評估；實作時請在您的環境中重現量測。