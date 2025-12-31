---
layout: synthesis
title: "[架構師的修練] #1, 刻意練習 - 打好基礎"
synthesis_type: solution
source_post: /2021/03/01/practice-01/
redirect_from:
  - /2021/03/01/practice-01/solution/
postid: 2021-03-01-practice-01
---

以下為根據文章內容整理出的 18 個問題解決案例，皆具備問題、根因、解法（含流程/程式碼/方法）與效益指標，並可直接用於實戰教學、專案練習與能力評估。

## Case #1: 把工作難題轉為可練習的迭代（POC→指標→抽象→極限→同伴）

### Problem Statement（問題陳述）
業務場景：團隊在做後端非同步批次與效能優化時，常因缺少系統化的練習與量化指標，導致每次調校靠直覺，學習與成效無法複製，影響下次專案的估時與風險控管。  
技術挑戰：如何把真實問題轉為可獨立重現的最小可驗證環境，並建立客觀指標與迭代流程，支援持續改良。  
影響範圍：影響專案交期、效能穩定性、團隊能力成長與知識沉澱。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 無標準練習方法：沒有固定把問題轉為可重現/可測的練習題。
2. 無客觀指標：缺乏 TTFT/TTLT 等統一指標比較前後方案。
3. 學習依賴環境：只在正式專案嘗試新技術，風險高。

深層原因：
- 架構層面：缺乏用最小可行架構驗證假設（MVP/POC）的規範。
- 技術層面：測試與度量工具使用不足，對效能極限缺乏模型。
- 流程層面：沒有形成「練習→回饋→改善」的循環與同儕觀摩機制。

### Solution Design（解決方案設計）
解決策略：建立五步驟練習流程：1) 用最小程式定義問題與正確性；2) 設定 TTFT/TTLT/平均時間等指標；3) 抽象出可替換策略；4) 推導理論極限判定停止點；5) 同儕觀摩與 PR 迭代。

實施步驟：
1. 問題最小化（POC）
- 實作細節：用單一可執行專案+測試重現問題。
- 所需資源：xUnit/NUnit、.NET 6/8 或任意語言測試框架
- 預估時間：0.5 天

2. 建立指標
- 實作細節：記錄 TTFT/TTLT/Avg；輸出 CSV/JSON 以便對比
- 所需資源：Stopwatch/Benchmark 工具
- 預估時間：0.5 天

3. 策略抽象化
- 實作細節：以 interface 定義策略，方便切換方案
- 所需資源：語言 OOP 能力
- 預估時間：0.5 天

4. 推導理論極限
- 實作細節：以瓶頸理論（min(stage capacity)）估計上限
- 所需資源：紙筆/白板，簡單腳本計算
- 預估時間：0.5 天

5. 同儕觀摩與 PR
- 實作細節：在 GitHub 建 Repo，收 PR 比對指標
- 所需資源：GitHub/GitLab、CI
- 預估時間：持續

關鍵程式碼/設定：
```csharp
// C# 範例：可插拔策略 + 指標度量
public interface IJobRunner { Task RunAsync(IEnumerable<Job> jobs); }

public sealed class SequentialRunner : IJobRunner {
  public async Task RunAsync(IEnumerable<Job> jobs) {
    var swAll = Stopwatch.StartNew();
    var firstDone = false; long ttft = 0;
    foreach (var job in jobs) {
      await job.ExecuteAsync();
      if (!firstDone) { ttft = swAll.ElapsedMilliseconds; firstDone = true; }
    }
    swAll.Stop();
    Console.WriteLine($"TTFT={ttft}ms, TTLT={swAll.ElapsedMilliseconds}ms");
  }
}

// Implementation Example: 將不同 Runner 實作注入測試，記錄指標對比
```

實際案例：文章中作者以「平行任務處理」為例，定義 TTFT/TTLT/平均時間，透過多版本方案迭代比較。  
實作環境：.NET、xUnit、GitHub PR 流程  
實測數據：  
改善前：無固定指標與練習流程，優化方向主觀  
改善後：每版指標可比對，能定量呈現進步  
改善幅度：能穩定收斂至接近理論上限（視案例）

Learning Points（學習要點）
核心知識點：
- POC 最小化與策略抽換
- 度量指標（TTFT/TTLT/Avg）
- 瓶頸與理論極限思維

技能要求：
- 必備技能：單元測試、基礎 OOP、Git 流程
- 進階技能：效能建模、Benchmark 工具

延伸思考：
- 還能應用於重構、性能回歸測試、技術選型比較
- 風險：指標選錯、POC 偏離真實場景
- 優化：加上 CI 自動基準測試、可視化儀表板

Practice Exercise（練習題）
- 基礎練習：實作兩個 Runner（順序/平行）並輸出 TTFT/TTLT
- 進階練習：再加入 Pipeline Runner，比對三者指標
- 專案練習：建立 PR 比較流程與儀表板，供多人觀摩

Assessment Criteria（評估標準）
- 功能完整性（40%）：能正確執行並輸出指標
- 程式碼品質（30%）：策略抽象、可測性
- 效能優化（20%）：能解釋數據與瓶頸
- 創新性（10%）：實驗設計與觀測改良

---

## Case #2: 早期 Web 的線上影像處理（DHTML + CGI/COM）

### Problem Statement（問題陳述）
業務場景：需要在網頁上提供使用者對圖片加字、定位的功能，產生個人化電子賀卡，前端需捕捉座標與樣式，後端完成合成並回傳成品。  
技術挑戰：當時瀏覽器功能有限（IE3/4 時代），無現成 AJAX，跨語言/進程間的影像處理需在 Server 端完成。  
影響範圍：影響上線可行性、互動體驗與伺服器負載。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 前端無強大 API：無 Canvas/Fetch，僅能透過 DHTML 互動。
2. 影像運算重：需由伺服器端 native/com 元件處理。
3. 跨語言互通：ASP/VBScript 與 C/C++ 影像庫需橋接。

深層原因：
- 架構層面：缺少通用的 RPC/IPC 橋接層。
- 技術層面：需要 COM 作為二進位介面的共同語言。
- 流程層面：前後端協作需定義參數與回傳格式。

### Solution Design（解決方案設計）
解決策略：前端用 DHTML 取得位置與文字設定；後端以 COM 元件封裝影像處理，提供 ASP 呼叫；以簡單 QueryString/Form 傳遞參數，輸出合成圖檔。

實施步驟：
1. 前端互動
- 實作細節：以絕對定位/事件取得座標與樣式
- 所需資源：DHTML, JavaScript
- 預估時間：1 天

2. 後端影像處理
- 實作細節：以 COM 封裝影像庫函式供 ASP 呼叫
- 所需資源：C++/C#（CCW 亦可）、IIS
- 預估時間：3 天

關鍵程式碼/設定：
```html
<!-- 前端 DHTML 取得座標並送回 -->
<img id="pic" src="/img/base.jpg" onclick="mark(event)">
<script>
function mark(e){
  const x=e.offsetX,y=e.offsetY,text=encodeURIComponent(document.getElementById('t').value);
  location.href=`/api/compose.asp?x=${x}&y=${y}&text=${text}`;
}
</script>
```
```asp
' ASP 假想：呼叫 COM 組圖
<%
Set img = Server.CreateObject("MyImageComposer.Component")
img.LoadBase "/img/base.jpg"
img.DrawText Request("text"), CInt(Request("x")), CInt(Request("y"))
img.Save "/out/result.jpg"
Response.Redirect "/out/result.jpg"
%>
```

實際案例：作者在 2000 年代實作線上影像處理以產出電子賀卡。  
實作環境：IIS + ASP + COM（C++/C# CCW）  
實測數據：  
改善前：前端無法直接處理影像  
改善後：可互動定位並生成個人化圖  
改善幅度：從不可行到可上線，互動體驗顯著提升

Learning Points（學習要點）
- COM 為跨語言的二進位協定
- 前後端參數契約與最小介面設計
- Server-side heavy compute 的影響

技能要求：
- 必備：ASP/DHTML/COM 基礎
- 進階：影像庫封裝、資源管理

延伸思考：
- 可用現代 Canvas/Web API 重構
- 風險：COM 註冊/權限/穩定性
- 優化：後端改為容器化服務，前端用 Canvas 預覽

Practice Exercise：
- 基礎：前端取得座標與樣式參數（30 分）
- 進階：建立簡單後端合成文字（2 小時）
- 專案：以現代堆疊重做（8 小時）

Assessment Criteria：
- 功能（40%）：可生成圖
- 代碼（30%）：封裝與錯誤處理
- 效能（20%）：響應時間
- 創新（10%）：現代化重構

---

## Case #3: 從 XML 資料庫遷移到 RDBMS 的 XML-RDB 映射層

### Problem Statement（問題陳述）
業務場景：e-learning 產品累積大量 XML 資料，早期使用 Tamino（XML DB），但市場接受度低、招募困難，需遷移至 MS SQL 等主流 RDB。  
技術挑戰：需保留既有 XML 資料結構並轉入關聯式表，同時不重寫全部邏輯。  
影響範圍：開發速度、維護成本、長期技術選型風險。  
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 技術生態稀缺：XML DB 受市場支持不足。
2. 招募困難：RDBMS 為主流，人才充足。
3. 資料結構不相容：XML 與 RDB 模型差異大。

深層原因：
- 架構層面：耦合於特定 DB 能力。
- 技術層面：未有中介層管理模型差異。
- 流程層面：缺少漸進式遷移與驗證機制。

### Solution Design（解決方案設計）
解決策略：自建 XML-RDB 映射層（簡易 ORM），將 XML 節點映射為關聯表結構，保留邏輯層 API，不影響上層業務。

實施步驟：
1. 資料模型設計
- 實作細節：核心節點正規化；弱結構部分以 JSON/XML 欄位存放
- 所需資源：DBA、ER 建模工具
- 預估時間：3-5 天

2. 映射層實作
- 實作細節：建立 Load/Save API，處理結構差異
- 所需資源：C#、Dapper/ADO.NET
- 預估時間：5-10 天

關鍵程式碼/設定：
```csharp
// 例：將 XML 映射至 RDB 結構化字段 + 擴展欄
public sealed class XmlRdbMapper {
  public (CourseRow, string extraJson) MapCourse(XElement xml) {
    var row = new CourseRow {
      Id = (string)xml.Attribute("id"),
      Title = (string)xml.Element("title"),
      Author = (string)xml.Element("author")
    };
    // 其餘弱結構以 JSON 保存
    var extra = new JObject {
      ["rawXml"] = xml.ToString(SaveOptions.DisableFormatting)
    };
    return (row, extra.ToString());
  }
}
// Implementation Example：Load->Map->Persist；Read->Rehydrate
```

實際案例：作者於產品第二版將堆疊改為 IIS+ASP+MS-SQL，同時自建 XML-RDB 映射，平順遷移。  
實作環境：Windows/IIS、ASP、MS-SQL、C#  
實測數據：  
改善前：XML DB 招募/維運成本高  
改善後：轉向主流技術、團隊上手快  
改善幅度：維運風險與人力風險顯著下降（定性）

Learning Points：
- 模型轉換與資料正規化策略
- 中介層隔離技術差異
- 漸進式遷移風險控管

技能要求：
- 必備：RDB 設計、ADO.NET/Dapper
- 進階：抽象設計與資料一致性

延伸思考：
- 可配合資料遷移工具/批次驗證
- 風險：資料丟失/語意改變
- 優化：增加對 Schema 演進的版本控管

Practice Exercise：
- 基礎：設計三個節點的映射表（30 分）
- 進階：實作 XML→RDB 的 Load/Save（2 小時）
- 專案：完成端到端遷移腳本與回歸驗證（8 小時）

Assessment Criteria：
- 功能（40%）：正確讀寫
- 代碼（30%）：映射層封裝清晰
- 效能（20%）：批次寫入表現
- 創新（10%）：Schema 演進處理

---

## Case #4: 用 C# + CCW 實作 COM 元件讓 ASP 重用核心邏輯

### Problem Statement（問題陳述）
業務場景：既有系統為 Classic ASP，但核心邏輯需現代化（C#），又要兼容 ASP 與未來 ASP.NET。  
技術挑戰：跨語言/二進位互通、部署與註冊、版本相容。  
影響範圍：影響遷移速度、回溯相容與風險。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. ASP 與 C# 執行環境不同。
2. 無統一物件二進位規約。
3. 一次性重寫風險高。

深層原因：
- 架構層面：缺少中介組件分離 UI 與 Domain。
- 技術層面：需 COM Callable Wrapper 提供 COM 介面。
- 流程層面：部署需註冊、版本管理。

### Solution Design（解決方案設計）
解決策略：以 C# 開發核心邏輯，標註 ComVisible，建立 ProgId，透過 CCW 讓 ASP 以 COM 方式呼叫，同時為 ASP.NET 重用。

實施步驟：
1. 建立 C# COM 類別庫
- 實作細節：ComVisible、Guid、InterfaceType
- 所需資源：.NET、regasm
- 預估時間：1 天

2. 部署/註冊
- 實作細節：regasm /codebase；IIS 權限
- 所需資源：IIS 管理
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
using System.Runtime.InteropServices;

[ComVisible(true)]
[Guid("D9A2F6E4-8B7D-4F44-9F77-1234567890AB")]
[ProgId("MyCompany.CoreService")]
public class CoreService {
  public string Hello(string name) => $"Hi {name}";
}
// Implementation Example：ASP 以 CreateObject("MyCompany.CoreService") 呼叫
```

實際案例：作者以 C# + CCW 將核心元件提供給 ASP 呼叫，並為後續 ASP.NET 遷移鋪路。  
實作環境：Windows/IIS、.NET Framework、Classic ASP  
實測數據：  
改善前：ASP 直寫商業邏輯，可測性差  
改善後：核心邏輯集中於 .NET，可重用與測試  
改善幅度：遷移風險與重工顯著降低（定性）

Learning Points：
- CCW 與 COM 註冊流程
- 隔離 UI 與 Domain 邏輯
- 漸進式遷移策略

技能要求：
- 必備：C#、IIS、COM 基礎
- 進階：部署自動化與版本控管

延伸思考：
- 現代化可改為 gRPC/HTTP API
- 風險：COM 註冊與權限問題
- 優化：封裝於 Windows Service/容器

Practice Exercise：
- 基礎：建立可供 COM 呼叫的 C# 類別（30 分）
- 進階：在 ASP 中呼叫並傳遞參數（2 小時）
- 專案：拆出核心模組，雙端重用（8 小時）

Assessment Criteria：
- 功能（40%）：ASP 可呼叫成功
- 代碼（30%）：核心邏輯封裝
- 效能（20%）：呼叫延遲
- 創新（10%）：現代化替代方案

---

## Case #5: ASP 與 ASP.NET 共站運行與 Session 互通的漸進遷移

### Problem Statement（問題陳述）
業務場景：既有 ASP 系統需逐步導入 ASP.NET 新頁面，要求同站運行、Session 可互通，避免一次大改。  
技術挑戰：兩種 Session 機制不同、加密金鑰與儲存不一致。  
影響範圍：登入態、使用者體驗、遷移風險。  
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. Session 實作不同（InProc/OutProc 差異）。
2. Cookie/機器金鑰不一致。
3. ASP 無法直接讀取 ASP.NET InProc Session。

深層原因：
- 架構層面：缺乏跨框架的統一會話儲存。
- 技術層面：需外部化 Session（StateServer/SQL/自定存儲）。
- 流程層面：雙棧共存時的 Key/加密一致性管控。

### Solution Design（解決方案設計）
解決策略：將 ASP.NET Session 改為 SQL/OutProc 模式，或自建共享票據（cookie + DB）供兩端讀寫，確保機器金鑰與加密演算法一致。

實施步驟：
1. 外部化 Session
- 實作細節：ASP.NET 設為 SQLMode；ASP 透過 DB 存取共用欄位
- 所需資源：SQL Server、連線字串共用
- 預估時間：1-2 天

2. 票據一致
- 實作細節：machineKey 固定、Cookie 網域一致
- 所需資源：Web.config、IIS 設定
- 預估時間：0.5 天

關鍵程式碼/設定：
```xml
<!-- ASP.NET Web.config 設為 SQLServer Session -->
<sessionState mode="SQLServer" sqlConnectionString="Data Source=...;Initial Catalog=ASPState;..." />
<machineKey validationKey="..." decryptionKey="..." validation="SHA1" decryption="AES"/>
```
```asp
' ASP 端以 ADO 讀取共享會話表或自建單點登入票據
' Implementation Example：以自建表保存 userId/token，有效期一致
```

實際案例：作者提到 ASP/ASP.NET 可共站並互通 Session，達成平順遷移。  
實作環境：IIS、Classic ASP、ASP.NET、SQL Server  
實測數據：  
改善前：無法共站、須一次改版  
改善後：可漸進遷移、降低風險  
改善幅度：部署風險大幅下降（定性）

Learning Points：
- Session 外部化與票據一致性
- 漸進式上雲/遷移策略
- 共站風險管控

技能要求：
- 必備：IIS、ASP/ASP.NET 基礎
- 進階：安全/加密與票據設計

延伸思考：
- 現代可用集中認證（OpenID Connect）
- 風險：票據竊取、重放攻擊
- 優化：使用標準身份供應商與短期 Token

Practice Exercise：
- 基礎：設定 SQL Server Session（30 分）
- 進階：ASP 與 ASP.NET 共站共用登入資訊（2 小時）
- 專案：完成完整遷移計畫與回滾設計（8 小時）

Assessment Criteria：
- 功能（40%）：登入態可互通
- 代碼（30%）：安全與封裝
- 效能（20%）：Session 存取延遲
- 創新（10%）：現代身份替代

---

## Case #6: Code + Infra + Config 三分法的 DevOps 上線流程

### Problem Statement（問題陳述）
業務場景：多團隊協作的微服務上線頻繁出錯，責任界面不清，難以追蹤問題源頭。  
技術挑戰：同時涉及程式、基礎設施與環境設定，變更牽一髮動全身。  
影響範圍：上線失敗率、回滾時間、跨團隊協作成本。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 版本與設定混雜、不可追蹤。
2. 基礎設施手動變更，無 IaC。
3. Release 責任不清。

深層原因：
- 架構層面：邊界與契約未明確。
- 技術層面：缺 IaC 與 Config 管理。
- 流程層面：缺部署職能分工與審核機制。

### Solution Design（解決方案設計）
解決策略：將 Code、Infra、Config 割裂管理：應用團隊對 Code 負責；平台團隊以 IaC 管 Infra；Release/配置團隊管理 Config，藉 pipeline 組合，明確責權。

實施步驟：
1. IaC 建置
- 實作細節：Terraform/ARM/Ansible 管理基礎設施
- 所需資源：雲端賬戶、CI/CD
- 預估時間：3-5 天

2. Config 管理
- 實作細節：環境變數/Config Server；與 Code 分倉庫
- 所需資源：Vault/Consul/App Config
- 預估時間：2 天

關鍵程式碼/設定：
```yaml
# CI/CD (示意)：三階段拼裝
stages: [build, infra, release]

build:
  script: dotnet publish ...

infra:
  script: terraform apply -auto-approve

release:
  script: |
    export APP_VERSION=$(cat version.txt)
    ./deploy.sh --image $APP_VERSION --config env/prod.yaml
# Implementation Example：分層責任明確可審計
```

實際案例：作者在 DevOpsDays 分享 Code/Infra/Config 三分法，界定團隊職責與系統邊界。  
實作環境：雲平台 + CI/CD + IaC  
實測數據：  
改善前：頻繁人為錯誤、難回溯  
改善後：變更可追蹤、邊界清晰、可快速回滾  
改善幅度：上線成功率提升、回溯時間下降（定性）

Learning Points：
- 職責邊界與可追蹤性
- IaC 基礎與配置管理
- 微服務邊界劃分與組織對齊

技能要求：
- 必備：CI/CD、YAML、基礎雲概念
- 進階：Terraform/Vault 與權限治理

延伸思考：
- 應用於多租戶與跨區部署
- 風險：權限配置錯誤
- 優化：變更審批與策略管控

Practice Exercise：
- 基礎：把環境設定外部化（30 分）
- 進階：以 Terraform 管一套測試環境（2 小時）
- 專案：完成三分法的完整上線管線（8 小時）

Assessment Criteria：
- 功能（40%）：可一鍵部署/回滾
- 代碼（30%）：IaC 可讀性
- 效能（20%）：部署時間
- 創新（10%）：政策即程式（OPA 等）

---

## Case #7: 以 RabbitMQ 建立生產者-消費者解耦與抗峰值

### Problem Statement（問題陳述）
業務場景：需要處理瞬時激增的任務（如訂單事件、通知發送），同步模式造成 API 超時與資源耗盡。  
技術挑戰：穩定輸出、避免阻塞、工作節奏控制。  
影響範圍：用戶體驗、穩定性、營收。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 同步耦合導致 API 超時。
2. 後端資源無法即時擴展。
3. 任務處理不具備回壓機制。

深層原因：
- 架構層面：無事件驅動/消息中介。
- 技術層面：缺少任務隊列與工作池。
- 流程層面：無明確 SLA/SLO 管控。

### Solution Design（解決方案設計）
解決策略：以 RabbitMQ 建立 Queue，Producer 將任務入列，Worker 以穩定節奏取出執行，消化尖峰並穩定輸出。

實施步驟：
1. 定義交換器/隊列
- 實作細節：單一隊列 + 多 Worker；確認/重試策略
- 所需資源：RabbitMQ、.NET/任意 SDK
- 預估時間：1-2 天

2. 實作 Producer/Consumer
- 實作細節：標準化消息與錯誤處理
- 所需資源：應用代碼調整
- 預估時間：1-2 天

關鍵程式碼/設定：
```csharp
// C# Producer (RabbitMQ.Client)
using var conn = factory.CreateConnection();
using var ch = conn.CreateModel();
ch.QueueDeclare("jobs", durable:true, exclusive:false, autoDelete:false);
var body = Encoding.UTF8.GetBytes(JsonConvert.SerializeObject(payload));
ch.BasicPublish("", "jobs", null, body);

// C# Consumer
var consumer = new EventingBasicConsumer(ch);
consumer.Received += (_, ea) => {
  var json = Encoding.UTF8.GetString(ea.Body.ToArray());
  // do work...
  ch.BasicAck(ea.DeliveryTag, false);
};
ch.BasicConsume("jobs", autoAck:false, consumer);
// Implementation Example：穩定處理並可水平擴充 Worker
```

實際案例：作者以 RabbitMQ 作為典型非同步任務處理，在「後端工程師必備」與內訓示範。  
實作環境：RabbitMQ、.NET（或任意語言）  
實測數據：  
改善前：API 超時率高、吞吐不穩  
改善後：TTLT 降低、輸出平滑、峰值消化  
改善幅度：事故率下降（定性）

Learning Points：
- 事件驅動架構與解耦
- 消息可靠性（Ack/Nack）
- 穩定輸出與回壓

技能要求：
- 必備：MQ 基本概念與 SDK
- 進階：重試/死信/監控告警

延伸思考：
- 應用於各類非同步/批處理
- 風險：消息丟失/重複處理
- 優化：冪等設計與指標監控

Practice Exercise：
- 基礎：實作 Producer/Consumer（30 分）
- 進階：加入錯誤重試與告警（2 小時）
- 專案：替換既有同步流程為事件驅動（8 小時）

Assessment Criteria：
- 功能（40%）：穩定處理與 Ack
- 代碼（30%）：冪等與錯誤處理
- 效能（20%）：吞吐與延遲
- 創新（10%）：拓撲設計優化

---

## Case #8: 工作者節流與平行度控制（穩定輸出避免暴衝）

### Problem Statement（問題陳述）
業務場景：消費者數量調太大造成後端 DB 或外部 API 壓垮；太小又處理太慢。  
技術挑戰：動態調整平行度、避免暴衝並維持穩定輸出。  
影響範圍：可用性、成本、服務品質。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 沒有最大併發控制。
2. 工作者無回壓/節流策略。
3. 任務取得節奏不受控。

深層原因：
- 架構層面：無全局節流策略。
- 技術層面：缺少併發原語（Semaphore/Channel）。
- 流程層面：SLO 與限流政策不明。

### Solution Design（解決方案設計）
解決策略：以信號量或有界通道限制併發，工者完成才能再取下一件，配合指標調整平行度以達穩態最大吞吐。

實施步驟：
1. 加入併發控制
- 實作細節：SemaphoreSlim/Channels
- 所需資源：.NET TPL/任意語言併發工具
- 預估時間：0.5 天

2. 指標回饋
- 實作細節：觀測延遲/失敗率/資源占用
- 所需資源：簡單監控
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
var sem = new SemaphoreSlim(maxDegree);
foreach (var msg in messages) {
  await sem.WaitAsync();
  _ = Task.Run(async () => {
    try { await HandleAsync(msg); }
    finally { sem.Release(); }
  });
}
// Implementation Example：完成後才釋放，平行度受控
```

實際案例：作者闡述「每個 Worker 完成後再領取下一個任務，輸出穩定，不受瞬間大量影響」。  
實作環境：任意語言  
實測數據：  
改善前：暴衝造成外部依賴失效  
改善後：吞吐穩定、錯誤率下降  
改善幅度：穩態處理能力提升（定性）

Learning Points：
- 限流/併發控制
- 以穩態最大吞吐為目標
- 監控指標回饋調參

技能要求：
- 必備：基本併發原語
- 進階：自動調參/閉環控制

延伸思考：
- 應用於 API Gateway、批處理
- 風險：設定過小/過大
- 優化：自動化調參策略

Practice Exercise：
- 基礎：加入 Semaphore 控制（30 分）
- 進階：根據延遲自動調整 degree（2 小時）
- 專案：實作可視化平行度調參台（8 小時）

Assessment Criteria：
- 功能（40%）：併發受控
- 代碼（30%）：正確釋放/錯誤處理
- 效能（20%）：穩定吞吐
- 創新（10%）：自動調參

---

## Case #9: 批次任務的 Pipeline 化與指標導向優化

### Problem Statement（問題陳述）
業務場景：需處理大量資料的三階段流程（如清洗→運算→輸出），順序執行耗時長。  
技術挑戰：如何設計 Pipeline 讓多階段並行，並用指標驗證成效。  
影響範圍：處理時間、資源使用、成本。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 單執行緒串行處理。
2. 無指標對比不同策略。
3. 資源未充份利用。

深層原因：
- 架構層面：未抽象分段處理與緩衝。
- 技術層面：缺少併發與緩衝設計（Queue/Channel）。
- 流程層面：無基準測試/停止準則。

### Solution Design（解決方案設計）
解決策略：以 Channel（或等價結構）連接多個 Stage，形成生產線；加入監測 TTFT/TTLT/Avg；迭代調整緩衝大小與平行度。

實施步驟：
1. Stage 抽象
- 實作細節：IStage<TIn,TOut> 接口設計
- 所需資源：.NET Channels/TPL
- 預估時間：1 天

2. 指標與緩衝調整
- 實作細節：加入 Stopwatch 與併發控制
- 所需資源：監控/日誌
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
var ch1 = Channel.CreateBounded<Item>(100);
var ch2 = Channel.CreateBounded<Item>(100);

Task StageA() => Task.Run(async () => { /* produce to ch1 */ });
Task StageB() => Task.Run(async () => { /* read ch1, write ch2 */ });
Task StageC() => Task.Run(async () => { /* read ch2, finalize */ });

// Implementation Example：調整 bounded size 與並行度比對 TTFT/TTLT
```

實際案例：作者以「平行任務處理的思考練習」帶隊建造可實驗的 Pipeline 並以 TTFT/TTLT 評估。  
實作環境：.NET/TPL 或任意語言併發模型  
實測數據：  
改善前：TTLT 高、TTFT 慢  
改善後：TTFT/TTLT 顯著下降  
改善幅度：接近瓶頸理論極限（定性）

Learning Points：
- 生產線思維與緩衝設計
- 指標導向優化流程
- Pipe 容量與並行度調參

技能要求：
- 必備：併發與非同步
- 進階：瓶頸理論建模

延伸思考：
- 應用於 ETL、影音處理等
- 風險：緩衝過大記憶體爆增
- 優化：自適應緩衝

Practice Exercise：
- 基礎：三段 Pipeline（30 分）
- 進階：加入指標/調參（2 小時）
- 專案：可視化指標與自動調參（8 小時）

Assessment Criteria：
- 功能（40%）：多段並行
- 代碼（30%）：抽象清晰
- 效能（20%）：指標改善
- 創新（10%）：調參策略

---

## Case #10: 以理論極限指導效能優化的停止準則

### Problem Statement（問題陳述）
業務場景：團隊對性能優化沒有停止點，投入過多時間仍無顯著收益。  
技術挑戰：缺乏理論模型判斷最佳化上限與投資回報。  
影響範圍：研發效率、排程、成本。  
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 未定義滿分/上限。
2. 缺少瓶頸分析。
3. 無法評估投資回報。

深層原因：
- 架構層面：無資源斜率/容量模型。
- 技術層面：缺度量與拆解。
- 流程層面：缺 KPI 與停止準則。

### Solution Design（解決方案設計）
解決策略：以各階段理論處理速率推導最大吞吐，定義 TTFT/TTLT 的下界，當指標接近上限時停止深究，轉向下一瓶頸。

實施步驟：
1. 建模
- 實作細節：min(stage_capacity) 為吞吐上限
- 所需資源：簡單計算/實測核對
- 預估時間：0.5 天

2. 驗證
- 實作細節：對照實際指標差距
- 所需資源：測試場景
- 預估時間：0.5 天

關鍵程式碼/設定：
```python
# 極簡吞吐上限估算（示意）
stages = [1000, 800, 1200]  # items per min
max_throughput = min(stages)
print("Upper bound (items/min):", max_throughput)
# Implementation Example：對比實測數據決定停止點
```

實際案例：作者提出推導理論極限作為停止準則的觀念。  
實作環境：任意  
實測數據：  
改善前：無止盡優化  
改善後：有明確停止點與優先順序  
改善幅度：優化時間縮短（定性）

Learning Points：
- 瓶頸理論
- 指標下界/上界
- 投資報酬分析

技能要求：
- 必備：基礎數學/估算
- 進階：結合監控決策

延伸思考：
- 應用於容量規劃
- 風險：模型假設錯誤
- 優化：持續校準模型

Practice Exercise：
- 基礎：三階段模型上限估算（30 分）
- 進階：加入並行與緩衝（2 小時）
- 專案：實作自動建模與報表（8 小時）

Assessment Criteria：
- 功能（40%）：能算出上限
- 代碼（30%）：可讀可重用
- 效能（20%）：指標對齊
- 創新（10%）：模型延展

---

## Case #11: 以 SLO/SLA 思維管理系統服務水準

### Problem Statement（問題陳述）
業務場景：跨團隊對「穩定」認知不同，缺少可量化目標與錯誤預算管理。  
技術挑戰：定義 SLI/SLO、建立量測與治理流程。  
影響範圍：穩定性、優先級、資源配置。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 無統一可量測指標。
2. 缺少目標與錯誤預算。
3. 發生故障無決策依據。

深層原因：
- 架構層面：監控未對齊業務目標。
- 技術層面：缺可觀測性，無標準 SLI。
- 流程層面：無錯誤預算治理。

### Solution Design（解決方案設計）
解決策略：為關鍵路徑定義 SLI（如成功率/延遲/新鮮度），設定 SLO 目標，導入錯誤預算制度與變更凍結策略。

實施步驟：
1. 定義 SLI/SLO
- 實作細節：端到端延遲/成功率
- 所需資源：產品與運維協作
- 預估時間：1-2 天

2. 量測與治理
- 實作細節：統一量測、預算扣減、決策流程
- 所需資源：監控系統
- 預估時間：2-3 天

關鍵程式碼/設定：
```promql
# Prometheus SLI 示意：近 30 天成功率
sum(rate(http_requests_total{status=~"2.."}[30d]))
/
sum(rate(http_requests_total[30d]))
# Implementation Example：以報表對齊 SLO，超標觸發治理
```

實際案例：作者以 SLO 做為系統績效考核，類比 HR KPI，並結合 TOC。  
實作環境：監控/報警/日誌系統  
實測數據：  
改善前：穩定性討論主觀  
改善後：以錯誤預算驅動決策  
改善幅度：變更風險與爭議下降（定性）

Learning Points：
- SLI/SLO/SLA 與錯誤預算
- 以數據治理變更/容量
- 對齊業務價值

技能要求：
- 必備：可觀測性基礎
- 進階：治理流程設計

延伸思考：
- 應用於多團隊目標管理
- 風險：指標選錯導致偏行
- 優化：以北極星指標對齊業務

Practice Exercise：
- 基礎：定義兩個 SLI（30 分）
- 進階：建立 SLO 報表（2 小時）
- 專案：引入錯誤預算治理（8 小時）

Assessment Criteria：
- 功能（40%）：可觀測可追蹤
- 代碼（30%）：指標實作合理
- 效能（20%）：報表/告警有效
- 創新（10%）：治理設計

---

## Case #12: Blogging as Code：以 GitHub Pages/CI 建學習沙盒

### Problem Statement（問題陳述）
業務場景：工作中無法頻繁嘗試新技術，需要可控的實驗場域與內容自動化發佈。  
技術挑戰：在不增加維運成本下，實現版本控管與自動部署。  
影響範圍：個人/團隊學習效率、知識沉澱。  
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 無專案可練習新技術。
2. 手動部署耗時易錯。
3. 資源成本考量。

深層原因：
- 架構層面：缺少輕量平台承載實驗。
- 技術層面：未把內容當程式碼管理。
- 流程層面：缺自動化與回滾。

### Solution Design（解決方案設計）
解決策略：改用 GitHub Pages + Markdown/Jekyll，配 CI 自動化部署，把內容與設定納入版控，成為持續練習場域。

實施步驟：
1. 站台遷移
- 實作細節：Markdown、Jekyll、靜態化
- 所需資源：GitHub
- 預估時間：1 天

2. 自動化發佈
- 實作細節：GitHub Actions 觸發 build/deploy
- 所需資源：Actions 設定
- 預估時間：0.5 天

關鍵程式碼/設定：
```yaml
# .github/workflows/deploy.yml
name: Build & Deploy
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/jekyll-build-pages@v1
      - uses: actions/upload-pages-artifact@v1
  deploy:
    needs: build
    permissions: pages: write, id-token: write
    uses: actions/deploy-pages@v1
# Implementation Example：推送即部署，內容即程式碼
```

實際案例：作者多次遷移 Blog（自架→.Text→WP→GitHub Pages），以實驗不同技術。  
實作環境：GitHub Pages/Jekyll/Markdown  
實測數據：  
改善前：需自管伺服器/DB  
改善後：幾乎零維運、版本可追  
改善幅度：維運成本→趨近零（定性）

Learning Points：
- 內容即程式碼的理念
- 以 CI 實作自動化
- 自主學習場域

技能要求：
- 必備：Git/GitHub 基本
- 進階：CI 自動化腳本

延伸思考：
- 應用於文件/課程平台
- 風險：平台限制
- 優化：多分支/多環境預覽

Practice Exercise：
- 基礎：建立 Pages 站（30 分）
- 進階：加入 Actions 自動部署（2 小時）
- 專案：改造成可承載 Demo 的學習站（8 小時）

Assessment Criteria：
- 功能（40%）：自動部署成功
- 代碼（30%）：流程清晰
- 效能（20%）：構建時間/快取
- 創新（10%）：擴充能力

---

## Case #13: 用 CLI/Pipeline 快速組裝驗證與實驗

### Problem Statement（問題陳述）
業務場景：原型驗證常被大型框架拖慢，開發者需要低成本快速試驗。  
技術挑戰：以小工具拼裝資料流、快速迭代。  
影響範圍：POC 時間、學習效率。  
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 起手式過重。
2. 缺少資料管道串接。
3. 迭代成本高。

深層原因：
- 架構層面：未善用小型 CLI 的組合力。
- 技術層面：不熟標準輸入輸出/管線。
- 流程層面：沒有快速驗證流程。

### Solution Design（解決方案設計）
解決策略：以 CLI 工具接收 stdin/輸出 stdout，組合多工具形成 pipeline，快速試錯。

實施步驟：
1. 建立 CLI 標準
- 實作細節：--help、stdin/stdout、JSON IO
- 所需資源：.NET console 或任意語言
- 預估時間：0.5 天

2. Pipeline 組裝
- 實作細節：shell/PowerShell 管線串接
- 所需資源：系統 shell
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 讀 stdin 寫 stdout（JSON）.NET 例
var input = await new StreamReader(Console.OpenStandardInput()).ReadToEndAsync();
var obj = JsonConvert.DeserializeObject<MyInput>(input);
// ...process...
Console.WriteLine(JsonConvert.SerializeObject(result));
// Implementation Example：指令可互相管線
```

實際案例：作者「後端工程師必備：CLI + PIPELINE」系列分享用 CLI 加速練習與驗證。  
實作環境：任意  
實測數據：  
改善前：POC 需啟多服務/框架  
改善後：幾個 CLI 即可完成流程  
改善幅度：TTFT 顯著降低（定性）

Learning Points：
- UNIX 哲學：小而美可組合
- JSON 作為資料介面
- 快速試錯的價值

技能要求：
- 必備：CLI 開發與 shell
- 進階：跨平台腳本

延伸思考：
- 應用於資料前處理/驗證
- 風險：暫時性工具債
- 優化：封裝與版本管理

Practice Exercise：
- 基礎：寫 CLI 轉換 JSON（30 分）
- 進階：三個 CLI 組流水線（2 小時）
- 專案：將既有流程 CLI 化（8 小時）

Assessment Criteria：
- 功能（40%）：管線可用
- 代碼（30%）：介面清晰
- 效能（20%）：IO 效率
- 創新（10%）：工具組合

---

## Case #14: 以技能等級（Lv0-Lv4）建立能力評估與教學路徑

### Problem Statement（問題陳述）
業務場景：團隊常以「熟悉/精通」描述能力，標準不一，培訓難以聚焦。  
技術挑戰：建立可觀察的行為標準與驗收任務。  
影響範圍：招募、培訓、職涯晉升。  
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 定義模糊。
2. 無客觀驗收。
3. 期望錯位。

深層原因：
- 架構層面：職能模組化不足。
- 技術層面：缺少標準任務庫。
- 流程層面：未把學習與實戰接軌。

### Solution Design（解決方案設計）
解決策略：建立 Lv0-Lv4 行為描述與對應任務（如以 RabbitMQ 為例），用可交付任務驗收，將培訓轉為實戰。

實施步驟：
1. 定義等級
- 實作細節：以「能教/能解決」為 Lv3/Lv4 指標
- 所需資源：職能框架
- 預估時間：0.5 天

2. 任務化驗收
- 實作細節：每級對應練習與標準答案
- 所需資源：練習平台/Repo
- 預估時間：1 天

關鍵程式碼/設定：
```markdown
# 例：RabbitMQ 能力驗收任務（摘要）
- Lv2：完成 Producer/Consumer + Ack
- Lv3：解釋交換器與路由；帶新人成功上線
- Lv4：設計抗峰值方案並改善指標
# Implementation Example：以 PR 方式提交與評分
```

實際案例：作者提出 Lv0～Lv4 概念並以 RabbitMQ 說明各級行為。  
實作環境：文檔 + 練習 Repo  
實測數據：  
改善前：評估主觀  
改善後：標準化驗收與培訓路徑  
改善幅度：培訓效率提升（定性）

Learning Points：
- 行為式評估
- 任務化驗收
- 教學設計

技能要求：
- 必備：基本教學設計
- 進階：自動評分/平台化

延伸思考：
- 應用於所有技術模組
- 風險：過度簡化
- 優化：結合績效/實戰成果

Practice Exercise：
- 基礎：為某技術建立 Lv2/Lv3 任務（30 分）
- 進階：設計 LV4 改善題與指標（2 小時）
- 專案：完成一套可運行的驗收平台（8 小時）

Assessment Criteria：
- 功能（40%）：任務可執行
- 代碼（30%）：模板化產出
- 效能（20%）：評估效率
- 創新（10%）：教學創新

---

## Case #15: 以知識地圖開圖法識別「未知的未知」

### Problem Statement（問題陳述）
業務場景：面對新領域無從下手，常不知道缺什麼，搜尋關鍵字也失準。  
技術挑戰：建立從基礎科學到實作的知識地圖，找出斷點與學習順序。  
影響範圍：學習效率、技術決策品質。  
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 關鍵字選不準。
2. 不知全貌。
3. 學習無法串連。

深層原因：
- 架構層面：未從理論到實作建立映射。
- 技術層面：碎片知識無法連結。
- 流程層面：無學習路線/里程碑。

### Solution Design（解決方案設計）
解決策略：反向推演：問「能否從無到有做出？」將路徑一路推至基礎科學，畫出地圖，標註已掌握/缺失與先後順序。

實施步驟：
1. 建圖
- 實作細節：從應用→框架→系統→硬體→理論
- 所需資源：白板/軟體（XMind）
- 預估時間：0.5 天

2. 設里程碑
- 實作細節：每節點對應練習/檢核
- 所需資源：練習列表
- 預估時間：0.5 天

關鍵程式碼/設定：
```text
微服務 -> 通訊 -> 序列化 -> OS 網路 -> TCP/IP -> 佇列論
 (標記顏色：綠=已掌握、黃=入門、紅=缺失)
# Implementation Example：據此規劃學習與專案切入點
```

實際案例：作者以「能否從無到有打造」作為判斷是否還在「未知的未知」。  
實作環境：任意  
實測數據：  
改善前：學習分散無章  
改善後：路線清晰、能精準檢索與判斷資料價值  
改善幅度：學習效率提升（定性）

Learning Points：
- 逆向推導能力
- 知識連結與抽象
- 學習路線設計

技能要求：
- 必備：抽象與拆解
- 進階：知識圖譜工具

延伸思考：
- 團隊共用知識地圖
- 風險：過度完美主義拖延
- 優化：滾動更新

Practice Exercise：
- 基礎：替某領域畫 3 層地圖（30 分）
- 進階：定義每節點練習（2 小時）
- 專案：團隊共編知識地圖與任務分派（8 小時）

Assessment Criteria：
- 功能（40%）：地圖完整
- 代碼（30%）：可操作性（轉任務）
- 效能（20%）：導學效率
- 創新（10%）：圖譜演進機制

---

## Case #16: 用 ADR 做技術選型：主流堆疊 vs. 小眾技術

### Problem Statement（問題陳述）
業務場景：產品需選擇技術堆疊，過去採用小眾技術導致招募/維運困難。  
技術挑戰：平衡創新與可持續，留下遷移出口。  
影響範圍：長期成本、風險、交付速度。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 技術生態弱。
2. 團隊上手慢。
3. 維修與相容問題多。

深層原因：
- 架構層面：忽略可替換性/抽象層。
- 技術層面：未評估供應鏈與工具鏈。
- 流程層面：缺選型決策紀錄（ADR）。

### Solution Design（解決方案設計）
解決策略：以 ADR（Architecture Decision Record）紀錄選型：選主流堆疊，輔以抽象層隔離，保留遷移路徑與驗證計畫。

實施步驟：
1. 撰寫 ADR
- 實作細節：Context/Decision/Consequences
- 所需資源：ADR 模板
- 預估時間：0.5 天

2. 實證與回退
- 實作細節：POC/回退策略
- 所需資源：實驗環境
- 預估時間：1-2 天

關鍵程式碼/設定：
```markdown
# ADR-0001: DB 選型
Context: 既有大量 XML 資料，招募困難
Decision: 採用 MS-SQL + 自建 XML-RDB 映射
Consequences: 降低風險，保留遷移彈性
# Implementation Example：附 POC 指標證據
```

實際案例：作者從 XML DB 遷回 MS-SQL，並以自建映射降低風險。  
實作環境：Repo/Docs  
實測數據：  
改善前：小眾技術風險高  
改善後：轉主流堆疊，招募維運穩定  
改善幅度：人才/風險顯著改善（定性）

Learning Points：
- ADR 的價值
- 可替換性抽象
- 實證與回退思維

技能要求：
- 必備：文檔治理
- 進階：技術風險管理

延伸思考：
- 應用於雲廠商/框架選型
- 風險：過度保守
- 優化：引入創新配額與試點

Practice Exercise：
- 基礎：撰寫一份 ADR（30 分）
- 進階：附 POC 與指標佐證（2 小時）
- 專案：建立選型流程與審核會（8 小時）

Assessment Criteria：
- 功能（40%）：ADR 完整
- 代碼（30%）：證據鏈齊備
- 效能（20%）：流程可執行
- 創新（10%）：決策框架

---

## Case #17: 以抽象化與模組邊界提升團隊協作效率

### Problem Statement（問題陳述）
業務場景：專案程式碼可讀性差、接口不清，跨模組協作成本高，Bug 多。  
技術挑戰：建立清晰抽象層，強制依賴方向與契約。  
影響範圍：交付速度、品質、維護成本。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 直寫商業邏輯於 UI。
2. 模組邊界模糊。
3. 測試困難。

深層原因：
- 架構層面：缺 Domain/Infra/Interface 分層。
- 技術層面：接口設計薄弱。
- 流程層面：缺 code review 準則。

### Solution Design（解決方案設計）
解決策略：以介面驅動設計，建立 Domain-First 契約；Infra/Adapter 實作注入；搭配單元測試，將耦合集中於邊界。

實施步驟：
1. 契約先行
- 實作細節：定義 IOrderService/IRepo 等
- 所需資源：OOP/DI
- 預估時間：1 天

2. 落實測試
- 實作細節：mock 邊界、覆蓋率
- 所需資源：xUnit/Moq
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
public interface IOrderService {
  Task PlaceAsync(OrderDto dto);
}
public class OrderService : IOrderService {
  private readonly IOrderRepo _repo;
  public OrderService(IOrderRepo repo) => _repo = repo;
  public Task PlaceAsync(OrderDto dto) { /*...*/ }
}
// Implementation Example：UI 僅呼叫 IOrderService，Infra 可替換
```

實際案例：作者強調抽象化能力是連結知識與落地解法的關鍵，並多次以 OOP/封裝示範。  
實作環境：任意  
實測數據：  
改善前：跨層耦合、修改牽動大  
改善後：接口清晰、單元測試可行  
改善幅度：缺陷率/迭代時間下降（定性）

Learning Points：
- 依賴倒置與清晰契約
- 抽象層與邊界設計
- 單元測試護航重構

技能要求：
- 必備：OOP/設計原則
- 進階：組件化/清晰 API

延伸思考：
- 微服務邊界選擇
- 風險：過度抽象
- 優化：以 ADR 驗證抽象收益

Practice Exercise：
- 基礎：為小功能定義接口與實作（30 分）
- 進階：寫測試替換實作（2 小時）
- 專案：重構既有程式為分層架構（8 小時）

Assessment Criteria：
- 功能（40%）：契約正確
- 代碼（30%）：分層清晰
- 效能（20%）：可測可重構
- 創新（10%）：抽象設計巧思

---

## Case #18: 以 Side Project 把新技術練熟再導入生產

### Problem Statement（問題陳述）
業務場景：想導入新技術，但直接用於生產風險高；缺乏低風險試驗場。  
技術挑戰：如何在不傷害生產的情況下，練熟工具/框架與最佳實踐。  
影響範圍：品質、交期、風險。  
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 生產嘗試新技術，風險難控。
2. 無練習場域/流程。
3. 缺少驗證與回饋循環。

深層原因：
- 架構層面：缺 POC 專案骨架。
- 技術層面：未把練習方法工程化。
- 流程層面：無「練熟再上」政策。

### Solution Design（解決方案設計）
解決策略：建立個人/團隊 Side Project 模板（帶測試/指標/CI），先練熟再上；把生產問題抽取為可重現練習題，解完再回灌重構。

實施步驟：
1. 模板建立
- 實作細節：含測試/Benchmark/CI
- 所需資源：模板 Repo
- 預估時間：1 天

2. 問題抽出
- 實作細節：以最小代碼重現瓶頸
- 所需資源：範例資料
- 預估時間：1 天

關鍵程式碼/設定：
```yaml
# CI（摘要）：測試 + 基準測試
jobs:
  test: { ... }
  bench:
    steps:
      - run: dotnet run -c Release -- --bench > bench.json
# Implementation Example：以數據驅動導入決策
```

實際案例：作者強調「老闆請你來解決問題，不該用不熟技術上生產」，並以部落格作練習場。  
實作環境：任意  
實測數據：  
改善前：生產實驗導致事故  
改善後：練熟再上、風險可控  
改善幅度：上線事故下降（定性）

Learning Points：
- 練習先行的專業態度
- 模板化與數據化練習
- 迭代導入與回滾

技能要求：
- 必備：測試/CI
- 進階：基準測試與觀測

延伸思考：
- 導入門檻治理（技術雷達）
- 風險：練習偏離真實
- 優化：定期同步生產樣本

Practice Exercise：
- 基礎：建一個練習模板（30 分）
- 進階：把生產 Bug 抽為測試重現（2 小時）
- 專案：完成一輪導入（8 小時）

Assessment Criteria：
- 功能（40%）：模板可用
- 代碼（30%）：練習可重現
- 效能（20%）：指標完備
- 創新（10%）：導入治理

---

案例分類

1. 按難度分類
- 入門級（適合初學者）
  - Case 10, 12, 13, 14, 15, 18
- 中級（需要一定基礎）
  - Case 1, 5, 6, 7, 8, 9, 16, 17
- 高級（需要深厚經驗）
  - Case 2, 3, 4, 11

2. 按技術領域分類
- 架構設計類
  - Case 3, 4, 5, 6, 16, 17
- 效能優化類
  - Case 1, 8, 9, 10
- 整合開發類
  - Case 2, 4, 5, 7, 12, 13
- 除錯診斷類
  - Case 1, 9, 18
- 安全防護類
  - Case 5, 6, 11（治理層面）

3. 按學習目標分類
- 概念理解型
  - Case 10, 11, 14, 15, 16
- 技能練習型
  - Case 1, 7, 8, 9, 13, 17, 18
- 問題解決型
  - Case 2, 3, 4, 5, 6
- 創新應用型
  - Case 12, 16, 17

案例關聯圖（學習路徑建議）
- 初始基礎（先學）
  - Case 13（CLI/Pipeline 思維）
  - Case 12（Blog/CI 作為練習場）
  - Case 14（能力等級）+ Case 15（知識地圖）
- 練習方法論與度量
  - Case 1（POC→指標→抽象→極限→同伴）
  - Case 10（理論極限/停止準則）
- 事件驅動與非同步
  - Case 7（RabbitMQ 基礎）→ Case 8（節流/平行度）→ Case 9（Pipeline）
- 架構與遷移
  - Case 16（ADR 決策）→ Case 3（XML→RDB 映射）→ Case 4（C# COM）→ Case 5（共站與 Session 互通）
- DevOps 與治理
  - Case 6（Code/Infra/Config）→ Case 11（SLO/錯誤預算）
- 抽象與模組化
  - Case 17（抽象與邊界）→ 回饋至所有技術實作
- 實戰導入
  - Case 18（Side Project 練熟再上）作為所有導入的標準前置

依賴關係（摘要）：
- Case 1 依賴 Case 12/13/14/15（工具與方法與評估）
- Case 8/9 依賴 Case 7（MQ 基礎）
- Case 3/4/5 依賴 Case 16（選型策略）
- Case 11 依賴 Case 6（部署/可觀測基礎）
- Case 17 橫向強化所有案例的代碼品質

完整學習路徑建議：
1) 12→13→14→15 打好練習場、CLI 能力與評估/地圖  
2) 1→10 學方法與停止準則  
3) 7→8→9 建立非同步與平行實戰  
4) 16→3→4→5 練習遷移與相容策略  
5) 6→11 建立 DevOps 與 SLO 治理  
6) 17 以抽象化重構各解決方案  
7) 18 將新技術以 Side Project 練熟，再回到生產導入

以上案例皆可直接用於教學、專案演練與實作評估，並完整覆蓋文章中提到的實務問題、根因、解法與效益。
