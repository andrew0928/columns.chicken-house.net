---
source_file: "_posts/2022/2022-04-25-microservices16-api-implement.md"
generated_date: "2025-01-28 11:30:00 +0800"
version: "1.1"
tools:
  - github_copilot
  - claude_sonnet_3_5
model: "claude-3-5-sonnet-20241022"
---

# 微服務架構 - 從狀態圖來驅動 API 的實作範例 - 生成內容

## Metadata

### 原始 Metadata

```yaml
layout: post
title: "微服務架構 - 從狀態圖來驅動 API 的實作範例"
categories:
- "系列文章: 微服務架構"
tags: ["系列文章", "架構師的修練", "microservices"]
published: true
comments_disqus: false
comments_facebook: false
comments_gitalk: true
redirect_from:
logo: /wp-content/images/2022-04-25-microservices16-api-implement/2022-05-08-02-58-31.png
```

### 自動識別關鍵字
keywords:
  primary:
    - 微服務架構
    - API 設計
    - 狀態機
    - FSM
    - 會員服務
    - .NET Core
  secondary:
    - JWT Token
    - 安全機制
    - 狀態轉移
    - 分層架構
    - 單元測試
    - DI 注入

### 技術堆疊分析
tech_stack:
  languages:
    - C#
  frameworks:
    - ASP.NET Core
    - .NET Core
  tools:
    - JWT
    - Postman
    - Entity Framework
  platforms:
    - GitHub
  concepts:
    - Finite State Machine
    - Microservices
    - RESTful API
    - Dependency Injection

### 參考資源
internal_links:
  - "/2016/12/01/microservice7-apitoken/"
  - "/2016/02/17/casestudy_license_01_requirement/"
  - "/2016/02/24/casestudy_license_02_serialization/"

external_links:
  - "https://github.com/andrew0928/AndrewDemo.MemberServiceDesign/tree/article2"
  - "https://jwt.io/introduction/"
  - "https://www.freecodecamp.org/news/rest-api-best-practices-rest-endpoint-design-examples/"

tools_mentioned:
  - JWT (Json Web Token)
  - Postman
  - GitHub
  - Visual Studio
  - Entity Framework

### 內容特性
content_type: "技術實作教學"
complexity_level: "進階"
estimated_reading_time: "25-30分鐘"
article_length: "長篇深度文章"
target_audience: "架構師、資深開發者"

## 摘要 (Summaries)

### 文章摘要 (Article Summary)

本文是微服務 API 設計系列的第二篇，專注於將理論設計轉化為實際可執行的程式碼實作。作者以會員服務為例，示範如何運用有限狀態機 (FSM) 來驅動 API 設計，並透過 .NET Core 生態系統完整實現從設計到部署的全流程。文章涵蓋專案分層架構、JWT 安全機制、狀態機實作、核心服務設計、WebAPI 開發以及整合測試等關鍵技術環節，強調架構師必須具備將抽象設計轉化為具體實作的能力。

### 關鍵要點 (Key Points)

- 使用有限狀態機 (FSM) 來收斂和驗證 API 設計的一致性
- 建立清晰的專案分層架構：Core、WebAPI、Repository 三層分離
- 實作基於 JWT Token 的微服務安全機制，區分前台和後台授權
- 將狀態機邏輯程式碼化，確保 API 操作符合業務規則
- 運用依賴注入 (DI) 和中介軟體 (Middleware) 建立可測試的架構
- 強調實作驗證設計的重要性，避免紙上談兵的架構設計

### 段落摘要 (Section Summaries)

#### 重新複習: 系統設計與狀態機
作者重申設計要看得夠遠但只實作必要部分的原則，以會員服務為例說明微服務在內部系統中的定位。透過 FSM 來定義會員帳號的各種狀態轉移，每個箭頭代表一個可能的 API 操作，建立起設計與實作之間的直接對應關係。

#### 專案分層說明  
建立三層架構：AndrewDemo.Member.Core (核心業務邏輯)、AndrewDemo.Member.WebAPI (HTTP 接口層)、AndrewDemo.Member.Repository (資料存取層)。每層都有明確的職責分工，Core 層專注業務邏輯實作，WebAPI 層處理 HTTP 通訊，Repository 層負責資料持久化。

#### API 的安全機制 - Token
實作基於 JWT 的雙重安全機制：認證 (誰在操作) 和授權 (能做什麼)。透過 IdentityType 區分前台使用者和後台管理員，IdentityName 識別具體操作者身分。設計 MemberStateMachine 類別來管理不同身分對各種狀態轉移的操作權限。

#### StateMachine 
詳細實作有限狀態機的資料結構和操作邏輯。透過 tuple 結構 (actionName, initState, finalState, allowIdentityTypes) 來定義每個可能的狀態轉移規則，並提供 IsValid 方法來驗證特定操作在當前狀態下是否被允許。

#### Core Service
實作核心業務邏輯層，整合安全機制與狀態驗證。MemberService 類別結合 MemberStateMachine 和安全檢查，確保所有 API 操作都符合業務規則。包含完整的單元測試案例來驗證各種情境下的行為正確性。

#### WebAPI, 從 Core 到 HTTP
建立 WebAPI 層來橋接 HTTP 通訊與核心服務。實作 Controller、依賴注入設定、中介軟體以及 Postman 整合測試。此層主要負責協定轉換、錯誤處理、日誌記錄等 HTTP 相關的技術議題。

#### 結論
強調架構師必須具備將設計落實為可執行程式碼的能力，避免只會紙上談兵。透過實際 PoC 開發可以發現許多設計階段無法預見的技術細節，如微服務間的認證授權複雜性、多租戶架構的存取控制等。良好的抽象化設計是維持大型系統一致性的關鍵。

## 問答集 (Q&A Pairs)

### Q1, 如何運用狀態機來驅動 API 設計？
Q: 在微服務架構中，如何運用有限狀態機 (FSM) 來驅動 API 的設計與實作？
A: 首先分析業務領域中實體的各種狀態，如會員帳號的創建、啟用、停用等狀態。將每個狀態轉移對應到一個 API 操作，形成狀態圖。接著在程式碼中建立 StateMachine 類別，用 tuple 結構定義 (操作名稱, 起始狀態, 結束狀態, 允許身分) 的規則集合，確保 API 調用時會檢查當前狀態是否允許該操作。

### Q2, 微服務的三層架構如何劃分職責？
Q: 在微服務實作中，Core、WebAPI、Repository 三層架構各自負責什麼職責？
A: Core 層專注純粹的業務邏輯實作，不依賴任何外部技術框架，包含實體定義、狀態機邏輯、業務規則驗證等。WebAPI 層負責 HTTP 通訊協定的處理，包含 Controller、中介軟體、依賴注入設定等。Repository 層專責資料存取，封裝資料庫操作細節。這種分層讓各層可以獨立測試和替換。

### Q3, JWT Token 在微服務中如何實現安全控制？
Q: 如何透過 JWT Token 在微服務中實作認證和授權機制？
A: 設計雙重安全檢查機制：IdentityType 用於授權 (區分前台 USER 和後台 STAFF)，IdentityName 用於認證 (識別具體操作者)。在狀態機定義中加入 allowIdentityTypes 欄位，限制不同身分可執行的操作。每個 API 調用時先驗證 Token 有效性，再檢查該身分是否有權限執行特定的狀態轉移操作。

### Q4, 如何確保 API 操作符合業務規則？
Q: 在實作微服務 API 時，如何確保每個操作都符合業務邏輯的限制？
A: 透過 MemberStateMachine 的 IsValid 方法進行雙重驗證：首先檢查操作者身分是否有權限執行該操作，接著驗證目標實體的當前狀態是否允許該狀態轉移。只有通過兩項檢查的操作才會被執行，否則回傳錯誤。這確保了 API 行為與業務規則的一致性。

### Q5, 單元測試如何驗證狀態機邏輯？
Q: 在微服務開發中，如何設計單元測試來驗證狀態機和業務邏輯？
A: 針對每個可能的狀態轉移設計測試案例，包含正向測試 (允許的操作) 和反向測試 (禁止的操作)。測試不同身分在不同狀態下的操作權限，驗證錯誤情境的處理。使用 Arrange-Act-Assert 模式，先準備測試資料和狀態，執行操作，最後驗證結果是否符合預期。

### Q6, 依賴注入在微服務中扮演什麼角色？
Q: 依賴注入 (DI) 在微服務架構中如何提升程式碼的可測試性和維護性？
A: DI 讓各層之間透過介面而非具體實作耦合，提升了可測試性。Core 層可以注入 mock 的 Repository 進行單元測試，WebAPI 層可以注入測試用的 Core Service。同時支援不同環境使用不同的實作，如開發環境使用記憶體資料庫，正式環境使用 SQL Server，而不需修改業務邏輯程式碼。

### Q7, 中介軟體如何處理橫切關注點？
Q: WebAPI 中的 Middleware 如何處理安全驗證、日誌記錄等橫切關注點？
A: Middleware 在 HTTP 請求管線中提供統一的前置和後置處理。安全中介軟體負責 JWT Token 的解析和驗證，在請求到達 Controller 前完成身分認證。日誌中介軟體記錄每個請求的追蹤 ID、執行時間、錯誤資訊等。這種設計避免在每個 Controller 重複相同的處理邏輯。

### Q8, 如何進行微服務的整合測試？
Q: 使用 Postman 等工具進行微服務整合測試時，應該關注哪些重點？
A: 建立完整的測試情境腳本，模擬真實的業務流程：從會員註冊、啟用、到停用的完整生命週期。測試不同身分的權限控制，驗證錯誤狀態下的 API 回應。檢查 HTTP 狀態碼、回應格式、錯誤訊息的正確性。建立可重複執行的測試集合，支援持續整合流程。

## 解決方案 (Solutions)

### P1, 狀態機驅動的 API 設計方法
Problem: 傳統的 API 設計往往缺乏一致性，容易出現業務規則不一致或狀態管理混亂的問題
Root Cause: 缺乏統一的設計方法論，業務邏輯分散在各個 API 中，沒有中央化的狀態管理機制
Solution: 
- 使用有限狀態機 (FSM) 來建模業務實體的狀態轉移
- 將每個狀態轉移對應到一個 API 操作
- 在程式碼中實作 StateMachine 類別來強制執行轉移規則
- 整合安全機制，確保不同身分只能執行被授權的操作

Example:
```csharp
public class MemberStateMachine
{
    private List<(string actionName, MemberState? initState, MemberState? finalState, string[] allowIdentityTypes)> _fsmext = new List<(string actionName, MemberState? initState, MemberState? finalState, string[] allowIdentityTypes)>();

    public MemberStateMachine()
    {
        this._fsmext.Add(("register", MemberState.START, MemberState.CREATED, new string[] { "USER" }));
        this._fsmext.Add(("activate", MemberState.CREATED, MemberState.ACTIVATED, new string[] { "USER" }));
        this._fsmext.Add(("lock", MemberState.ACTIVATED, MemberState.DEACTIVED, new string[] { "USER", "STAFF" }));
    }
}
```

### P2, 微服務三層架構實作
Problem: 微服務內部程式碼結構混亂，業務邏輯與技術實作耦合過深，難以測試和維護
Root Cause: 缺乏清晰的分層設計，業務邏輯直接依賴具體的技術框架和資料存取實作
Solution:
- 建立 Core 層專注純粹業務邏輯，不依賴外部框架
- WebAPI 層負責 HTTP 通訊協定處理和技術整合
- Repository 層封裝資料存取邏輯，提供抽象介面
- 使用依賴注入來管理層間相依性

Example:
```
AndrewDemo.Member.Core/        # 核心業務邏輯
├── Entities/
├── Services/
└── StateMachine/

AndrewDemo.Member.WebAPI/      # HTTP 接口層
├── Controllers/
├── Middleware/
└── Program.cs

AndrewDemo.Member.Repository/  # 資料存取層
├── Interfaces/
└── Implementations/
```

### P3, JWT 基礎的安全機制整合
Problem: 微服務間的認證和授權管理複雜，難以區分不同來源和權限的 API 調用
Root Cause: 缺乏統一的安全框架，沒有明確區分認證 (who) 和授權 (what) 的機制
Solution:
- 使用 JWT Token 攜帶使用者身分和權限資訊
- 定義 IdentityType 來區分前台使用者和後台管理員
- 在狀態機中集成權限檢查，限制不同身分的操作範圍
- 透過 Middleware 統一處理 Token 驗證和身分解析

Example:
```csharp
public class MemberIdentity
{
    public string IdentityType { get; internal set; }  // USER | STAFF
    public string IdentityName { get; internal set; }  // 具體身分識別
}

// 在狀態機中檢查權限
public bool IsValid(string actionName, MemberState currentState, MemberIdentity identity)
{
    var rule = _fsmext.FirstOrDefault(x => x.actionName == actionName && x.initState == currentState);
    if (rule.actionName == null) return false;
    return rule.allowIdentityTypes.Contains(identity.IdentityType);
}
```

### P4, 可測試的微服務架構設計
Problem: 微服務程式碼難以進行單元測試，特別是涉及資料庫和外部服務的部分
Root Cause: 程式碼與具體實作緊密耦合，沒有適當的抽象化和依賴注入機制
Solution:
- 為每個外部相依性定義介面，使用依賴注入
- Core 層完全獨立於外部技術，可進行純粹的單元測試
- 使用 mock 物件替代真實的資料存取和外部服務
- 建立完整的測試案例覆蓋各種業務情境

Example:
```csharp
// 介面定義
public interface IMemberRepository
{
    Member GetMember(int id);
    void UpdateMember(Member member);
}

// 單元測試
[Test]
public void TestActivateMember()
{
    // Arrange
    var mockRepo = new Mock<IMemberRepository>();
    var member = new Member { State = MemberState.CREATED };
    mockRepo.Setup(x => x.GetMember(1)).Returns(member);
    
    var service = new MemberService(mockRepo.Object, new MemberStateMachine());
    
    // Act & Assert
    Assert.DoesNotThrow(() => service.Activate(1, userIdentity));
}
```

### P5, HTTP API 層的技術整合
Problem: 將核心業務邏輯暴露為 HTTP API 時，需要處理協定轉換、錯誤處理、日誌記錄等技術議題
Root Cause: HTTP 通訊層的技術複雜性與業務邏輯混合，缺乏清晰的職責分離
Solution:
- 建立專門的 WebAPI 層處理 HTTP 相關技術議題
- 使用 Controller 進行協定轉換和參數驗證
- 透過 Middleware 處理橫切關注點如安全驗證和日誌記錄
- 保持業務邏輯與 HTTP 技術的完全分離

Example:
```csharp
[ApiController]
[Route("api/[controller]")]
public class MemberController : ControllerBase
{
    private readonly IMemberService _memberService;
    
    [HttpPost("{id}/activate")]
    public IActionResult Activate(int id)
    {
        try
        {
            var identity = HttpContext.Items["Identity"] as MemberIdentity;
            _memberService.Activate(id, identity);
            return Ok();
        }
        catch (InvalidOperationException ex)
        {
            return BadRequest(ex.Message);
        }
    }
}
```

## 版本異動紀錄

### v1.1 (2025-01-28)
- 修正摘要格式，改用第三人稱敘述，加入生成工具資訊

### v1.0 (2025-01-28)
- 初始版本
