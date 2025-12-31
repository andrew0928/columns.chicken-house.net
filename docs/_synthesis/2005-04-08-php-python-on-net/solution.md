---
layout: synthesis
title: "php python on .net"
synthesis_type: solution
source_post: /2005/04/08/php-python-on-net/
redirect_from:
  - /2005/04/08/php-python-on-net/solution/
postid: 2005-04-08-php-python-on-net
---

說明：原文僅為「.NET CLR 支援更多語言（IronPython、Phalanger）」的簡訊，未包含具體的問題敘述、根因、方案與成效數據，無法直接「抽取」出案例。為滿足教學、實作與評估需求，以下提供「依主題延伸設計」且可落地實作的 15 個完整案例，聚焦於在 .NET 上使用 Python（IronPython）與 PHP（Phalanger 的現代替代 PeachPie）之整合、優化與部署。所有成效數據為示例性測試數據與目標範圍，用於實作評估與驗收標準，非原文實測。

## Case #1: 以 IronPython 為企業系統加入動態規則引擎

### Problem Statement（問題陳述）
- 業務場景：計費系統折扣規則常變更，過去需改 C# 程式再走完整建置與發佈流程，跨部門協作成本高，需求回應慢。希望運營人員可調整規則且不需整站重發佈。
- 技術挑戰：在 .NET 服務中安全、高效地載入與執行 Python 規則，並與強型別的 .NET 域模型互操作。
- 影響範圍：每次規則調整導致 1-2 天的發佈窗，影響行銷活動上線時程與收益。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 規則硬編碼於 C#，每次調整需重新建置與部署。
  2. 缺乏腳本化與熱更新機制，無法讓營運人員自助修改。
  3. 缺少規則版控與審核流程，變更風險大。
- 深層原因：
  - 架構層面：單體架構，規則與核心耦合。
  - 技術層面：無腳本宿主、無型別安全的互操作層。
  - 流程層面：變更需經開發、測試、發佈全流程。

### Solution Design（解決方案設計）
- 解決策略：嵌入 IronPython 作為規則宿主，提供受控的強型別 API（DTO/Facade）給腳本呼叫，建立規則倉儲與版控，支援熱載入、審批與回滾，並在沙箱/超時下執行。

### 實施步驟
1. 建立規則宿主與型別安全的腳本 API
- 實作細節：以 Microsoft.Scripting.Hosting 建立 Python 引擎，暴露純 POCO DTO 供規則使用；規則執行採 Scope 隔離與超時控制。
- 所需資源：NuGet IronPython、Microsoft.Scripting
- 預估時間：2-3 天

2. 規則管理與熱載入
- 實作細節：規則儲存於 Git/DB，後台審核後以檔案監聽或配置下發更新；提供審計日誌。
- 所需資源：Git/DB、檔案監聽、審批流程
- 預估時間：2 天

3. 安全與測試
- 實作細節：白名單 API、限制反射與檔案/網路 IO；建立單元測試與回歸測試。
- 所需資源：測試框架、稽核
- 預估時間：2 天

### 關鍵程式碼/設定
```csharp
// NuGet: IronPython, Microsoft.Scripting
using IronPython.Hosting;
using Microsoft.Scripting.Hosting;

public class RuleHost {
  private readonly ScriptEngine _engine = Python.CreateEngine();
  public decimal EvalDiscount(OrderContext ctx, string script) {
    var scope = _engine.CreateScope();
    scope.SetVariable("order", ctx); // 強型別 DTO
    var src = _engine.CreateScriptSourceFromString(@"
def calc(order):
    # 例：滿額打折
    if order.Total >= 1000: return order.Total * 0.9
    return order.Total
");
    var compiled = src.Compile();
    compiled.Execute(scope);
    dynamic calc = scope.GetVariable("calc");
    return (decimal)calc(order); // DLR dynamic 呼叫
  }
}

public class OrderContext { public decimal Total { get; set; } }
```

實際案例：設計為動態規則引擎，營運上傳 Python 規則腳本後審批生效。
實作環境：.NET 8、IronPython 3.x、Windows/Linux
實測數據：
- 改善前：規則變更 lead time 1-2 天
- 改善後：1-2 小時（含審批）
- 改善幅度：>80%

Learning Points（學習要點）
- 核心知識點：DLR 腳本宿主、Scope 隔離、型別互操作
- 技能要求：C#、IronPython、基礎設計模式
- 進階技能：治理與審批、腳本安全、觀察性

延伸思考：可應用於定價、風控規則；風險為腳本誤用與資源耗盡；可加強靜態掃描與資源限額。

Practice Exercise：基礎（建置宿主與調用函式）、進階（加入熱載入與審批）、專案（完整規則中心含審計）
Assessment Criteria：功能（可動態替換規則）、程式碼（清晰 API 與測試）、效能（p95 不退化）、創新（擴展性）

---

## Case #2: IronPython 無法使用 CPython C 擴充（如 NumPy）的替代策略

### Problem Statement
- 業務場景：舊有 Python 規則依賴 NumPy/SciPy，遷移至 IronPython 後無法載入 C 擴充，導致核心計算中斷。
- 技術挑戰：在無 C 擴充支援下，需替換為 .NET 原生數值庫或微服務外掛。
- 影響範圍：定價/風控模型無法運行，影響上線。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. IronPython 不支援 CPython C API 擴充。
  2. 以 CPython-only 生態套件構建的功能無法直移。
  3. 無替代設計（.NET 數值庫或外部服務）。
- 深層原因：
  - 架構：計算耦合在同進程。
  - 技術：套件選型未考慮執行時差異。
  - 流程：遷移前缺少兼容性盤點。

### Solution Design
- 解決策略：優先以 .NET 數值庫（Math.NET、ML.NET）替代；若需原始庫，拆分為外部 CPython 微服務（gRPC/REST）並做結果緩存。

### 實施步驟
1. 庫替換（內嵌）
- 實作細節：以 MathNet.Numerics 重寫核心矩陣運算，提供薄封裝給 IronPython。
- 資源：MathNet.Numerics
- 時間：2-4 天

2. 外掛微服務（可選）
- 實作細節：保留 CPython + NumPy，獨立服務，使用 gRPC；IronPython 以 .NET 客戶端呼叫。
- 資源：CPython、gRPC
- 時間：3-5 天

### 關鍵程式碼/設定
```python
# IronPython 使用 MathNet.Numerics
import clr
clr.AddReference("MathNet.Numerics")
from MathNet.Numerics.LinearAlgebra import Double

A = Double.DenseMatrix.OfArray([[1.0,2.0],[3.0,4.0]])
b = Double.DenseVector([5.0, 6.0])
x = A.Solve(b)  # 代替 numpy.linalg.solve
print(list(x))
```

實作環境：.NET 8、IronPython 3.x、Math.NET 5.x
實測數據：
- 改善前：核心計算不可用
- 改善後：功能恢復；與 CPython 相比性能相近至 +20%（視演算法）
- 改善幅度：功能恢復 100%，性能達標

Learning Points：執行時差異、替代庫選型、微服務邊界
技能要求：IronPython 互操作、Math.NET、gRPC（進階）
延伸思考：可混合策略（快路徑 .NET、慢路徑微服務）；風險為跨服務延遲；可加快取策略。

Practice：將 numpy 運算改寫為 Math.NET；進階：加入 gRPC 後備；專案：AB 回歸測試與效能基準
Assessment：功能等價（數值誤差容限）、碼品質（抽象封裝）、效能（延遲與吞吐）、創新（動態策略）

---

## Case #3: IronPython 並行與共享狀態安全（無 GIL 假設）

### Problem Statement
- 業務場景：多執行緒背景作業使用 Python 字典共享狀態，偶發競態導致錯誤與資料不一致。
- 技術挑戰：IronPython 無 GIL 假設，需用 .NET 並行原語保護共享狀態。
- 影響範圍：批次處理準確性與可用性。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 共享字典未加鎖。
  2. 誤以為 Python 具有 GIL 可保護操作。
  3. 缺少並發測試。
- 深層原因：
  - 架構：共享可變狀態設計。
  - 技術：不了解 IronPython 執行模型。
  - 流程：無壓力/競態測試。

### Solution Design
- 解決策略：以 .NET ConcurrentDictionary 或不可變結構替代；封裝原子操作；補齊並發測試與度量。

### 實施步驟
1. 結構替換與封裝
- 實作細節：Python 綁 .NET 類型 ConcurrentDictionary；暴露原子 Upsert API。
- 資源：System.Collections.Concurrent
- 時間：1-2 天

2. 並發測試
- 實作細節：以 BenchmarkDotNet/自製壓測；引入遞增負載測試。
- 資源：測試框架
- 時間：1-2 天

### 關鍵程式碼/設定
```python
import clr
clr.AddReference("System.Collections.Concurrent")
from System.Collections.Concurrent import ConcurrentDictionary

cache = ConcurrentDictionary[str, int]()

def inc(key):
    def factory(k): return 1
    # 原子遞增
    return cache.AddOrUpdate(key, factory, lambda k,v: v+1)
```

實作環境：.NET 8、IronPython 3.x
實測數據：
- 改善前：高併發錯誤率 ~0.8%
- 改善後：0%（10 分鐘 10k rps 壓測）
- 改善幅度：錯誤率下降 100%

Learning Points：並行原語、不可變 vs 可變、併發測試
技能要求：IronPython、.NET 並發容器
延伸思考：用不可變快照 + 事件溯源；風險為記憶體上升；加上分段清理。

Practice：用 ConcurrentDictionary 實作計數器；進階：加壓測；專案：共享快取層
Assessment：功能（無資料競態）、碼品質（封裝清晰）、效能（線性擴展）、創新（不可變策略）

---

## Case #4: IronPython 腳本熱路徑效能調優（編譯與快取）

### Problem Statement
- 業務場景：每次請求都重新解譯腳本，造成延遲上升與 CPU 耗用。
- 技術挑戰：降低 DLR 動態調用成本，重用已編譯腳本與 Scope。
- 影響範圍：API p95 延遲與吞吐量。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 每次請求都 Execute 字串。
  2. 未使用 ScriptSource.Compile 與緩存。
  3. Scope 建立成本高。
- 深層原因：
  - 架構：缺乏腳本快取層。
  - 技術：不了解 DLR 呼叫站台快取。
  - 流程：無效能基準管控。

### Solution Design
- 解決策略：預編譯腳本、Scope 物件池、函式委派快取，並加上配置變更快取失效。

### 實施步驟
1. 預編譯與快取
- 實作細節：ScriptSource.Compile + ConcurrentDictionary 快取；檔案雜湊作為版本鍵。
- 資源：IronPython、ConcurrentDictionary
- 時間：1-2 天

2. 物件池與基準
- 實作細節：Scope 物件池；BenchmarkDotNet 基準追蹤。
- 資源：BenchmarkDotNet
- 時間：1 天

### 關鍵程式碼/設定
```csharp
class ScriptCache {
  private readonly ScriptEngine _engine = Python.CreateEngine();
  private readonly ConcurrentDictionary<string, CompiledCode> _cache = new();

  public dynamic GetFunc(string codeKey, string code) {
    var compiled = _cache.GetOrAdd(codeKey, _ => 
      _engine.CreateScriptSourceFromString(code).Compile());
    var scope = _engine.CreateScope();
    compiled.Execute(scope);
    return scope.GetVariable("calc");
  }
}
```

實作環境：.NET 8、IronPython 3.x
實測數據（示例基準）：
- 改善前：p95 150ms、吞吐 1.2k rps
- 改善後：p95 80ms、吞吐 2.1k rps
- 幅度：延遲 -47%、吞吐 +75%

Learning Points：DLR 編譯、呼叫快取、物件池
技能要求：C#、IronPython、效能基準
延伸思考：跨多節點的快取同步；風險為熱更新一致性；可加版本雜湊。

Practice：寫快取層並做基準；進階：Scope 池與失效；專案：熱路徑調優報告
Assessment：功能（快取命中）、碼品質（並發安全）、效能（基準改善）、創新（自適應失效）

---

## Case #5: IronPython 存取 SQL Server（ADO.NET）

### Problem Statement
- 業務場景：Python 規則需查詢客戶等級與歷史消費來調整折扣，需安全高效連 DB。
- 技術挑戰：在 IronPython 中正確使用 ADO.NET，避免連線洩漏與注入。
- 影響範圍：資料一致性與查詢延遲。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 無連線池與 using 模式。
  2. 字串拼接 SQL 易注入。
  3. 查詢無超時設定。
- 深層原因：
  - 架構：腳本直接打 DB。
  - 技術：ADO.NET 用法不足。
  - 流程：缺少統一資料層。

### Solution Design
- 解決策略：以 Parameterized Query 與 using 管理連線；抽象資料存取函式，限制腳本直查權限。

### 實施步驟
1. ADO.NET 封裝
- 實作細節：提供 get_customer_tier(customerId) 函式；連線字串以安全配置注入。
- 資源：System.Data.SqlClient
- 時間：0.5-1 天

2. 權限與超時
- 實作細節：最小權限登入、CommandTimeout、重試策略。
- 資源：連線帳號、策略
- 時間：0.5 天

### 關鍵程式碼/設定
```python
import clr
clr.AddReference("System.Data")
from System.Data.SqlClient import SqlConnection, SqlCommand, SqlParameter

def get_customer_tier(conn_str, cid):
    with SqlConnection(conn_str) as conn:
        conn.Open()
        cmd = SqlCommand("SELECT Tier FROM dbo.Customer WHERE Id=@id", conn)
        cmd.Parameters.Add(SqlParameter("@id", cid))
        cmd.CommandTimeout = 3
        tier = cmd.ExecuteScalar()
        return tier or "NORMAL"
```

實作環境：.NET 8、IronPython 3.x、SQL Server
實測數據：
- 改善前：偶發連線耗盡、p95 120ms
- 改善後：零連線洩漏、p95 90ms
- 幅度：穩定性↑、延遲 -25%

Learning Points：ADO.NET 正確用法、注入防護、超時
技能要求：IronPython、資料庫
延伸思考：改為中台 API；風險為直連耦合；可加快取。

Practice：封裝查詢 API；進階：加入重試與快取；專案：資料層 Facade
Assessment：功能（正確查詢）、碼品質（資源釋放）、效能（延遲與連線池）、創新（快取策略）

---

## Case #6: IronPython 外掛的安全沙箱與資源隔離

### Problem Statement
- 業務場景：第三方外掛以 Python 提供，曾出現腳本誤用檔案系統或 CPU 爆滿。
- 技術挑戰：在 .NET 上有效隔離腳本權限與資源，避免單體內崩潰。
- 影響範圍：服務穩定性與資安。
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：
  1. 於同進程執行且無資源限制。
  2. 未限制 IO/反射。
  3. 無超時與殺進程策略。
- 深層原因：
  - 架構：缺少隔離邊界。
  - 技術：誤用過時 CAS（.NET Core 無）。
  - 流程：外掛審核不足。

### Solution Design
- 解決策略：外掛改為獨立進程（或容器）執行，透過 RPC（gRPC/命名管道）與主系統通訊；設定 CPU/記憶體/時間限制與白名單 API。

### 實施步驟
1. 子進程宿主與 RPC
- 實作細節：Process 啟動 IronPython 宿主；命名管道傳遞請求；標準輸出錯誤重導。
- 資源：System.IO.Pipes、gRPC（可選）
- 時間：3-5 天

2. 資源限制與監測
- 實作細節：Windows Job Object 或 Linux cgroup；超時計時與強制終止。
- 資源：OS 能力、監控
- 時間：2-3 天

### 關鍵程式碼/設定
```csharp
var psi = new ProcessStartInfo("python-host.exe"){ RedirectStandardOutput=true, UseShellExecute=false };
var proc = Process.Start(psi);
// 綁定到 JobObject 限制 CPU/記憶體（Windows），或使用 cgroup（Linux）
// 透過 NamedPipeClientStream 與宿主通訊，傳入受控 API
```

實作環境：.NET 8、IronPython 3.x、Windows/Linux
實測數據：
- 改善前：外掛偶發拖垮主進程
- 改善後：外掛崩潰不影響主系統；資源峰值受限
- 幅度：可用性顯著提升（MTBF +）

Learning Points：進程隔離、資源限制、RPC
技能要求：進程間通訊、OS 資源管理
延伸思考：容器化（K8s 限額）；風險為 RPC 延遲；可用批次執行佇列平衡。

Practice：建立子進程宿主；進階：加入 JobObject/cgroup；專案：外掛中心
Assessment：功能（隔離生效）、碼品質（通訊協議）、效能（低延遲）、創新（自我修復）

---

## Case #7: 跨語言除錯與追蹤（C# ↔ IronPython）

### Problem Statement
- 業務場景：C# 調用 Python 規則時偶發例外且難追蹤，無跨語言關聯 ID 與堆疊。
- 技術挑戰：建立跨語言追蹤、將 Python 堆疊與 C# 活動關聯、可視化。
- 影響範圍：問題定位時效與 MTTR。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 日誌分散且無關聯 ID。
  2. Python 例外未攔截格式化。
  3. 無集中化追蹤。
- 深層原因：
  - 架構：觀察性缺失。
  - 技術：DLR 例外處理理解不足。
  - 流程：無事後回溯流程。

### Solution Design
- 解決策略：使用 System.Diagnostics.Activity 建立 TraceId；捕捉 IronPython 例外並輸出 traceback；集中化到 OpenTelemetry/ELK。

### 實施步驟
1. 追蹤關聯
- 實作細節：建立 Activity；將 TraceId 注入 Python 執行環境與日誌。
- 資源：OpenTelemetry、Serilog
- 時間：1-2 天

2. 例外格式化
- 實作細節：捕捉 Microsoft.Scripting 例外，印出 Python traceback。
- 資源：IronPython API
- 時間：0.5 天

### 關鍵程式碼/設定
```csharp
using System.Diagnostics;
try {
  using var act = new Activity("RuleEval").Start();
  scope.SetVariable("trace_id", act.TraceId.ToString());
  compiled.Execute(scope);
} catch (Exception ex) {
  // IronPython 例外通常包在 Microsoft.Scripting.Runtime.Exceptions
  var msg = ex.ToString(); // 可含 Python 堆疊
  _logger.LogError("{TraceId} {Error}", Activity.Current?.TraceId, msg);
  throw;
}
```

實作環境：.NET 8、IronPython 3.x、OpenTelemetry Collector
實測數據：
- 改善前：MTTR 2-4 小時
- 改善後：<1 小時
- 幅度：-50% ~ -75%

Learning Points：跨語言追蹤、Activity/TraceId、例外處理
技能要求：記錄與追蹤、IronPython 例外
延伸思考：加採樣與敏感遮罩；風險為日誌量；可設動態取樣。

Practice：實作 TraceId 串接；進階：導入 OTEL；專案：跨語言故障演練
Assessment：功能（堆疊還原）、碼品質（追蹤清晰）、效能（低開銷）、創新（可視化）

---

## Case #8: 將 PHP 專案遷移到 .NET（Phalanger→PeachPie）

### Problem Statement
- 業務場景：舊 PHP 站點需整合 .NET 生態與 DevOps，提升效能與維運一致性。
- 技術挑戰：使用 PeachPie 將 PHP 編譯為 IL，保留語意與提高可維運性。
- 影響範圍：可用性、效能、部署流程。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. Phalanger 已停維，需轉 PeachPie。
  2. PHP 與 .NET 生態割裂。
  3. 發布鏈路與監控不一致。
- 深層原因：
  - 架構：語言與平台分裂。
  - 技術：缺少標準化 SDK 與管線。
  - 流程：CI/CD 不統一。

### Solution Design
- 解決策略：以 PeachPie.NET.Sdk 建立專案，逐步編譯 PHP 原始碼，分階段修正不兼容部分；整合 .NET CI/CD。

### 實施步驟
1. 以 SDK 初始化與建置
- 實作細節：建立 csproj 引用 PHP；dotnet build 出 IL。
- 資源：PeachPie SDK、.NET 8
- 時間：1-2 天

2. 介面測試與逐步修正
- 實作細節：修正不支援語法/函式；導入單元測試。
- 資源：測試框架
- 時間：3-5 天

### 關鍵程式碼/設定
```xml
<!-- app.csproj -->
<Project Sdk="Peachpie.NET.Sdk/Latest">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
  </PropertyGroup>
  <ItemGroup>
    <Compile Include="**\*.php" />
  </ItemGroup>
</Project>
```
```php
<?php // index.php
echo "Hello from PeachPie on .NET";
```

實作環境：.NET 8、PeachPie 最新穩定版、IIS/Kestrel
實測數據：
- 改善前：分散部署、監控不一
- 改善後：統一 .NET CI/CD 與監控；吞吐 +20%（示例）
- 幅度：維運一致性↑、效能中度提升

Learning Points：PeachPie SDK、相容性修正、.NET 管線
技能要求：PHP、.NET SDK、CI
延伸思考：以 NuGet 分發 PHP 套件；風險為相容性缺口；可以冒煙測試控風險。

Practice：建置 Hello PeachPie；進階：遷移小模組；專案：完整子系統遷移
Assessment：功能（等價）、碼品質（結構清晰）、效能（吞吐/延遲）、創新（整合度）

---

## Case #9: C# 呼叫 PHP 函式（PeachPie 生成的 .NET 程式庫）

### Problem Statement
- 業務場景：現有 .NET 服務需重用既有 PHP 函式庫邏輯。
- 技術挑戰：以 PeachPie 編譯為 .NET 程式庫並在 C# 直接呼叫。
- 影響範圍：重用效率與一致性。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 跨語言重用缺管道。
  2. 手動重寫成本高。
  3. 缺少 Context 與型別映射。
- 深層原因：
  - 架構：重用策略缺失。
  - 技術：不了解 PeachPie 互操作。
  - 流程：缺少包管理。

### Solution Design
- 解決策略：將 PHP 專案建為 Class Library，透過 Context 呼叫匯出的函式。

### 實施步驟
1. 建置 PHP Library
- 實作細節：PeachPie Class Library；dotnet build 產出 dll。
- 資源：PeachPie SDK
- 時間：0.5 天

2. C# 引用與呼叫
- 實作細節：Context.CreateEmpty、呼叫靜態方法。
- 資源：.NET
- 時間：0.5 天

### 關鍵程式碼/設定
```php
<?php // lib/utils.php
function slugify($s) { return strtolower(preg_replace('/\W+/','-',$s)); }
```
```csharp
using Pchp.Core;
using PhpLib; // PeachPie 產生的命名空間
var ctx = Context.CreateEmpty();
var slug = PhpLib.utils.slugify(ctx, "Hello World!");
```

實作環境：.NET 8、PeachPie
實測數據：重用時間由數週改為 1 天；缺陷率下降（示例目標）
Learning Points：Context、命名空間映射、打包
技能要求：.NET、PeachPie
延伸思考：以 NuGet 發佈；風險為語義差異；加測試。

Practice：導出一個函式給 C#；進階：複雜資料結構；專案：完整工具庫
Assessment：功能（對齊）、碼（型別映射清晰）、效能（呼叫開銷低）、創新（包化）

---

## Case #10: 在 PHP（PeachPie）中直接使用 .NET 類庫

### Problem Statement
- 業務場景：PHP 端想直接使用 .NET 的高效能工具（如 StringBuilder、HttpClient）。
- 技術挑戰：於 PeachPie 中正確參考與使用 .NET 類型。
- 影響範圍：開發效率與效能。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 未在 csproj 中加入 .NET 參考。
  2. 命名空間映射不清。
  3. 型別/可空處理不當。
- 深層原因：
  - 架構：互操作缺範例。
  - 技術：語法/型別知識不熟。
  - 流程：缺少規範。

### Solution Design
- 解決策略：在 PeachPie 專案檔加入 Reference，於 PHP 以完全修飾名稱使用 .NET 類型。

### 實施步驟
1. 加入 .NET 參考
- 實作細節：csproj <Reference Include="System.Net.Http" />。
- 資源：PeachPie SDK
- 時間：0.5 天

2. 實作與測試
- 實作細節：使用 System\Text\StringBuilder。
- 資源：.NET
- 時間：0.5 天

### 關鍵程式碼/設定
```xml
<ItemGroup>
  <Reference Include="System.Net.Http" />
</ItemGroup>
```
```php
<?php
use System\Text\StringBuilder;
$sb = new StringBuilder();
$sb->Append("Hello");
$sb->Append(" .NET");
echo $sb->__toString();
```

實作環境：.NET 8、PeachPie
實測數據：字串拼接熱路徑 CPU 減少 15%（示例）
Learning Points：Reference、命名空間對應、型別互通
技能要求：PHP、.NET 類型
延伸思考：使用 Span/Memory 功能；風險為不相容 API；加抽象層。

Practice：用 StringBuilder；進階：呼叫 HttpClient；專案：封裝 .NET 實用類
Assessment：功能（可用）、碼（互操作乾淨）、效能（開銷低）、創新（泛型使用）

---

## Case #11: PeachPie 網站部署至 ASP.NET Core on IIS/Azure

### Problem Statement
- 業務場景：需將 PeachPie 應用部署到 Windows IIS/Azure App Service。
- 技術挑戰：正確設定 ASP.NET Core Module、環境變數與日誌。
- 影響範圍：上線可用性。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. web.config 設定錯誤。
  2. 發布目錄結構不對。
  3. 缺少健康檢查。
- 深層原因：
  - 架構：部署腳本不一致。
  - 技術：IIS 模組認知不足。
  - 流程：缺少藍綠/回滾。

### Solution Design
- 解決策略：使用 dotnet publish 產出；IIS 使用 ASP.NET Core Module v2；加入健康檢查與日誌轉發。

### 實施步驟
1. 發布與設定
- 實作細節：dotnet publish -c Release；web.config 指向可執行檔。
- 資源：IIS、ASP.NET Core Hosting Bundle
- 時間：1 天

2. 健康檢查與日誌
- 實作細節：/health 檢查端點；stdoutLogFile 啟用。
- 資源：IIS 配置
- 時間：0.5 天

### 關鍵程式碼/設定
```xml
<!-- web.config -->
<configuration>
 <system.webServer>
  <handlers>
   <add name="aspNetCore" path="*" verb="*" modules="AspNetCoreModuleV2" resourceType="Unspecified"/>
  </handlers>
  <aspNetCore processPath=".\MyApp.exe" stdoutLogEnabled="true" stdoutLogFile=".\logs\stdout">
  </aspNetCore>
 </system.webServer>
</configuration>
```

實作環境：.NET 8、PeachPie、IIS/Azure
實測數據：部署成功率 100%；冷啟 < 2s（示例）
Learning Points：IIS 模組、發佈工件、健康檢查
技能要求：Windows/IIS、.NET 發佈
延伸思考：容器化、滾動升級；風險為設定漂移；用 IaC。

Practice：IIS 部署演練；進階：加健康檢查與日誌；專案：自動化部署腳本
Assessment：功能（可啟動）、碼（設定版控）、效能（啟動與 p95）、創新（IaC）

---

## Case #12: PeachPie 效能調優（Release、R2R、Tiered JIT、配置）

### Problem Statement
- 業務場景：PeachPie 網站在高流量下 p95 偏高。
- 技術挑戰：結合 .NET 執行時優化與程式層面最佳化。
- 影響範圍：使用者體感與成本。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. Debug 建置上線。
  2. Tiered JIT 未啟用、R2R 未使用。
  3. 程式層面過度動態。
- 深層原因：
  - 架構：熱路徑無基準。
  - 技術：.NET 執行時調優不熟。
  - 流程：缺少性能守門。

### Solution Design
- 解決策略：Release + TieredPGO + ReadyToRun；避免不必要動態；快取結果；設壓測基準。

### 實施步驟
1. 執行時優化
- 實作細節：csproj 啟用 TieredPGO、R2R；伺服器 GC。
- 資源：.NET SDK
- 時間：0.5 天

2. 程式層面
- 實作細節：快取重複計算、減少反射。
- 資源：程式優化
- 時間：1-2 天

### 關鍵程式碼/設定
```xml
<PropertyGroup>
  <Configuration>Release</Configuration>
  <PublishReadyToRun>true</PublishReadyToRun>
  <TieredCompilation>true</TieredCompilation>
  <TieredPGO>true</TieredPGO>
  <ServerGarbageCollection>true</ServerGarbageCollection>
</PropertyGroup>
```

實作環境：.NET 8、PeachPie
實測數據（示例）：
- p95 由 180ms → 110ms（-39%）
- 吞吐 +25%

Learning Points：.NET 執行時選項、熱路徑優化
技能要求：.NET 性能、PeachPie
延伸思考：R2R 對動態碼效果有限；風險為包體增加；可用多階段編譯。

Practice：切換 Release 與 R2R 對比；進階：壓測報告；專案：完整調優案
Assessment：功能（無回歸）、碼（設定清楚）、效能（達標）、創新（自動基準）

---

## Case #13: 以 .NET 測試框架測 PHP（PeachPie）單元測試

### Problem Statement
- 業務場景：希望將 PHP 函式納入 .NET 測試管線中驗證。
- 技術挑戰：在 xUnit/NUnit 直接呼叫 PeachPie 編譯出的函式並斷言。
- 影響範圍：品質把關。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 無跨語言測試樣板。
  2. Context 未初始化。
  3. 測資分散。
- 深層原因：
  - 架構：測試與產物未整合。
  - 技術：呼叫約定不熟。
  - 流程：CI 未納管。

### Solution Design
- 解決策略：用 xUnit 建立測試專案，引用 PeachPie 產物並以 Context 呼叫，集中測資。

### 實施步驟
1. 測試專案
- 實作細節：dotnet new xunit；引用 PeachPie 專案。
- 資源：xUnit
- 時間：0.5 天

2. 測試實作
- 實作細節：Arrange/Act/Assert；邊界條件。
- 資源：測試框架
- 時間：0.5 天

### 關鍵程式碼/設定
```csharp
public class PhpLibTests {
  [Fact]
  public void Slugify_Works() {
    var ctx = Pchp.Core.Context.CreateEmpty();
    var s = PhpLib.utils.slugify(ctx, "Hello, World!");
    Assert.Equal("hello-world", s.ToString());
  }
}
```

實作環境：.NET 8、xUnit、PeachPie
實測數據：測試納入 CI，回歸率↓；平均修復時間↓（示例）
Learning Points：Context、測試整合
技能要求：.NET 測試
延伸思考：覆蓋率度量；風險為雙語測試複雜度；可產生測試模板。

Practice：為 3 個 PHP 函式寫測試；進階：邊界與錯誤；專案：測試套件
Assessment：功能（測試可運行）、碼（AAA 清晰）、效能（CI 時間）、創新（範本化）

---

## Case #14: 將 PHP 函式庫以 NuGet 供 .NET 重用

### Problem Statement
- 業務場景：內部多個 .NET 服務需共享 PHP 工具函式。
- 技術挑戰：以 PeachPie 打包為 NuGet，標準化版本與發佈。
- 影響範圍：重用效率與治理。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 以檔案拷貝共享。
  2. 無版本治理。
  3. 相依關係混亂。
- 深層原因：
  - 架構：缺少套件中心。
  - 技術：打包知識不足。
  - 流程：無審批與簽章。

### Solution Design
- 解決策略：在 csproj 加入打包中繼資訊，dotnet pack 產生 nupkg；發佈至私有 NuGet feed。

### 實施步驟
1. 打包設定
- 實作細節：PackageId、Version、Authors、RepositoryUrl。
- 資源：NuGet feed
- 時間：0.5 天

2. CI 發佈
- 實作細節：push 至 Azure Artifacts/GitHub Packages。
- 資源：CI/CD
- 時間：0.5 天

### 關鍵程式碼/設定
```xml
<PropertyGroup>
  <PackageId>Company.PhpUtils</PackageId>
  <Version>1.0.0</Version>
  <Authors>Team</Authors>
  <PackageRequireLicenseAcceptance>false</PackageRequireLicenseAcceptance>
</PropertyGroup>
```

實作環境：.NET 8、PeachPie、NuGet Server
實測數據：跨專案整合時間 -70%（示例）
Learning Points：NuGet 打包、版本策略、供應鏈安全
技能要求：.NET 打包、CI
延伸思考：簽章與 SBOM；風險為破壞性變更；用 SemVer。

Practice：完成打包與安裝；進階：私庫發佈；專案：版本治理
Assessment：功能（成功引用）、碼（中繼完善）、效能（CI 流暢）、創新（簽章）

---

## Case #15: 跨語言字串編碼與在地化一致性（.NET ↔ Python/PHP）

### Problem Statement
- 業務場景：C#、IronPython、PHP（PeachPie）間字串在含 emoji/中日韓文字時出現亂碼或裁剪。
- 技術挑戰：.NET UTF-16、PHP/Python 常以 UTF-8 與二進位混用，需建立一致規範。
- 影響範圍：使用者資料、報表、搜尋。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 未明確指定編碼。
  2. 錯誤的 bytes/string 轉換。
  3. 未處理 surrogate pairs。
- 深層原因：
  - 架構：無統一 i18n 策略。
  - 技術：編碼知識不足。
  - 流程：未在測試涵蓋。

### Solution Design
- 解決策略：統一以 UTF-8 作為 IO 邊界，內部 .NET 使用 string（UTF-16）；提供安全轉換工具並加上單元測試與壓測。

### 實施步驟
1. 轉換工具與規範
- 實作細節：封裝 Encoding.UTF8/GetString、處理錯誤替代；PHP 明確使用 mb 庫。
- 資源：.NET Encoding、mbstring
- 時間：1 天

2. 測試用例
- 實作細節：emoji、合字、右到左等測試。
- 資源：測試資料
- 時間：0.5 天

### 關鍵程式碼/設定
```csharp
// C#：UTF-8 邊界
byte[] ToUtf8(string s) => System.Text.Encoding.UTF8.GetBytes(s);
string FromUtf8(byte[] b) => System.Text.Encoding.UTF8.GetString(b);
```
```php
<?php
mb_internal_encoding('UTF-8');
$s = "測試🙂";
$bytes = \System\Text\Encoding::UTF8()->GetBytes($s);
$back = \System\Text\Encoding::UTF8()->GetString($bytes);
```

實作環境：.NET 8、IronPython、PeachPie
實測數據：亂碼缺陷率降為 0；處理延遲無明顯上升（示例）
Learning Points：UTF-8/UTF-16、邊界設計、i18n 測試
技能要求：字串/編碼基礎
延伸思考：正規化（NFC/NFD）；風險為外部系統不一致；可加兼容層。

Practice：撰寫轉換工具；進階：特殊字元測試；專案：i18n 檢查清單
Assessment：功能（正確往返）、碼（邊界明確）、效能（低開銷）、創新（自動檢測）

--------------------------------
案例分類

1) 按難度分類
- 入門級：#5, #9, #10, #13
- 中級：#1, #2, #3, #4, #7, #8, #11, #12, #15
- 高級：#6, #14（亦可列中高，涉及治理/供應鏈）

2) 按技術領域分類
- 架構設計類：#1, #6, #8, #11, #14
- 效能優化類：#4, #12
- 整合開發類：#2, #3, #5, #9, #10, #13, #15
- 除錯診斷類：#7, #15
- 安全防護類：#6, #1（規則安全）

3) 按學習目標分類
- 概念理解型：#2, #15
- 技能練習型：#5, #9, #10, #13
- 問題解決型：#1, #3, #4, #7, #8, #11, #12
- 創新應用型：#6, #14

案例關聯圖（學習路徑建議）
- 先學：基礎互操作與打底
  - #5（IronPython + DB 基礎）
  - #9（C# 呼叫 PHP）
  - #10（PHP 用 .NET 類庫）
  - #13（.NET 測試 PHP）
- 進階：整合與效能
  - #1（動態規則引擎）依賴 #5、#7
  - #2（C 擴充替代）依賴 #5
  - #3（並行安全）依賴 #5
  - #4（腳本快取）依賴 #1
  - #12（PeachPie 調優）依賴 #8、#11
  - #15（編碼一致）可並行學習
- 部署與運維
  - #8（PHP 遷移至 .NET）→ #11（部署）
  - #7（追蹤）橫切所有案例
- 高級與治理
  - #6（外掛沙箱）依賴 #1、#7
  - #14（NuGet 打包治理）依賴 #9

完整學習路徑建議：
1) 打好互操作與測試基礎（#5 → #9 → #10 → #13 → #15）
2) 建立可用的動態能力與健全觀察性（#1 → #7）
3) 解決關鍵相容性與並發問題（#2 → #3）
4) 熱路徑效能優化（#4）
5) 完成 PHP 遷移與部署（#8 → #11 → #12）
6) 進入高級安全與包治理（#6 → #14）

備註：若您需要嚴格「只基於原文內容」的抽取，原文不含可抽取的四要素資訊；上述案例為依主題延伸的實戰教學設計。如需特定場景或技術棧版本鎖定（例如 IronPython 2.7 vs 3.x、PeachPie 版本、IIS/Azure/K8s），請告知以便精準化範本與測試腳本。