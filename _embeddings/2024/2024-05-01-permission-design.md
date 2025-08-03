---
source_file: "_posts/2024/2024-05-01-permission-design.md"
generated_date: "2025-08-03 14:30:00 +0800"
version: "1.0"
tools: github_copilot
model: claude_sonnet_3_5
---

# 架構面試題 #6: 權限管理機制的設計 - 生成內容

## Metadata

### 原始 Metadata

layout: post
title: "xxxxx 架構面試題 #6: 權限管理機制的設計"
categories:
- "系列文章: 架構師的修練"
tags: ["系列文章", "架構師的修練", "架構師觀點", "刻意練習", "抽象化"]
published: false
comments_disqus: false
comments_facebook: false
comments_gitalk: false
redirect_from:
logo: 

### 自動識別關鍵字

keywords:
  primary:
    - 權限管理
    - RBAC
    - 角色權限控制
    - 授權機制
    - 架構設計
    - 安全機制
  secondary:
    - IPrincipal
    - IIdentity
    - Permission
    - Role
    - Operation
    - Authorization
    - 認證與授權
    - 訂單管理系統
    - CRUD權限
    - 業務流程

### 技術堆疊分析

tech_stack:
  languages:
    - C#
  frameworks:
    - .NET
    - ASP.NET MVC
  tools:
    - Visual Studio
  platforms:
    - Windows
  concepts:
    - Role-Based Access Control
    - Authentication
    - Authorization
    - Security Design
    - Interface Design
    - Business Process Design

### 參考資源

references:
  internal_links:
    - (文中提及但未完整提供)
  external_links:
    - https://en.wikipedia.org/wiki/Role-based_access_control
    - https://learn.microsoft.com/zh-tw/aspnet/core/security/authorization/roles?view=aspnetcore-8.0
    - https://github.com/microsoft/referencesource/tree/master/mscorlib/system/security/principal
  mentioned_tools:
    - .NET Framework
    - Windows Security
    - Active Directory
    - ASP.NET MVC
    - AuthorizeAttribute
    - Thread.CurrentPrincipal
    - HttpContext

### 內容特性

content_metrics:
  word_count: 8180
  reading_time: "25 分鐘"
  difficulty_level: "中級"
  content_type: "教學"

## 摘要

### 文章摘要

作者透過架構面試題的形式，深入探討權限管理機制的設計原理與實作方法。文章從一個實際的訂單管理系統案例出發，說明權限管理的核心問題：如何控制不同角色的使用者能夠執行哪些功能。作者首先建立了權限管理的基本概念框架，包括認證與授權的分離、使用者角色的定義、以及功能權限的規劃。文章詳細介紹了.NET框架中的IIdentity和IPrincipal介面，說明如何透過這些基礎介面建立完整的認證機制。接著作者提出了權限管理的抽象化模型，定義了Subject、Role、Permission、Operation等核心概念，並說明它們之間的關聯關係。文章重點討論了RBAC（Role-Based Access Control）的設計原理，強調角色應該對應實際的業務職能，而非單純的技術分組。作者特別提醒，權限設計應該在系統設計階段就確定，而非在運行時期任意調整，以確保安全機制的一致性和可靠性。整篇文章透過具體的程式碼範例和設計原則，幫助讀者理解如何建立一個既安全又實用的權限管理系統。

### 關鍵要點

- 權限管理本質是商業需求而非純技術問題，必須對應實際業務流程
- 認證(Authentication)與授權(Authorization)是兩個不同層次的安全機制
- .NET的IIdentity和IPrincipal介面提供了權限管理的基礎架構
- RBAC中的Role應該對應實際職務功能，而非任意的使用者分組
- 權限設計應該在開發階段確定，避免運行時期的任意調整
- Permission應該對應系統的基本操作，Operation則是使用者可見的功能
- 良好的權限設計能夠從源頭控制安全，降低錯誤設計的風險
- 權限管理的複雜度可以透過適當的抽象化設計來降低

### 練習前的思考: 我需要了解這些機制嗎？

作者在開始技術討論前，先提出了是否需要重新發明輪子的哲學問題。作者認為雖然市面上已有成熟的權限管理解決方案，但架構師仍需要具備理解和設計權限機制的能力。這種能力對於判斷技術選擇、整合複雜系統特別重要。作者建議的平衡點是做好必要的練習，投入不算多但能獲得保障。透過理解原理，架構師才能在面對複雜且需要高度整合的系統時，立即做出正確的技術決策。作者強調這些練習雖然不大花時間，但在判斷技術選擇時能發揮關鍵作用，幫助架構師具備重新建立必要輪子的能力。

### 0. 權限管理是在做什麼?

作者將權限管理定義為商業需求而非技術需求，並用一個B2B零售商的銷售系統作為案例說明。系統有三種角色：業務助理負責訂單輸入維護、管理階層需要統計報表、系統管理人員處理技術問題。作者提出權限管理的評估標準包括管理困難度和精確度。通過20個使用者和50個功能的矩陣分析，說明直接管理1000種組合與透過角色和權限分類管理15種組合的差異。作者強調精確度的重要性，即系統實際給使用者的權限與老闆期望的一致性。這個案例展示了權限管理的核心目標：在保持管理便利性的同時，確保權限分配的精確性和安全性。

### 1. 權限基礎: 認證與授權

作者介紹了權限管理的基礎建設，強調認證與授權的分離。文章詳細解釋了.NET Framework中的兩個核心介面：IIdentity負責識別使用者身分（姓名、認證狀態、認證類型），IPrincipal則處理角色檢查（IsInRole方法）。作者透過Console應用程式和ASP.NET MVC的程式碼範例，展示這些介面的實際應用方式。在MVC中，認證結果會放在HttpContext.User中，而AuthorizeAttribute則自動處理角色檢查。作者特別強調這兩個介面自.NET 1.1時代就存在，設計優雅且經過時間考驗。這些基礎介面為後續更複雜的授權機制提供了穩固的基礎，即使在現代的.NET Core/5+版本中仍然廣泛使用。

### 抽象化授權機制

作者提出了權限管理的抽象化模型，定義了解題的兩個關鍵面向：應用程式如何檢查權限、權限如何運作與儲存。權限檢查需要三個輸入資訊：使用者身分（你是誰）、操作意圖（要做什麼）、權限設定（從哪裡取得規則）。作者引用RBAC的Wikipedia定義，說明Subject、Role、Permission、Operation等核心概念的關聯關係。文章定義了四個核心介面：IPrincipal（對應Subject）、ICustomRole、ICustomPermission、ICustomOperation，以及封裝整個授權檢查機制的ICustomAuthorization。作者特別說明了Permission和Operation的差異：Permission是授權的最小單位，Operation是使用者可見的功能，一個Operation可能需要多個Permission的組合。這種設計能夠大幅降低需要管理的權限數量，從上百個功能降為1-20個Permission的組合。

### 2. RBAC, Role based access control

作者詳細介紹RBAC（Role-Based Access Control）的核心概念和實作方式。透過Wikipedia的經典結構圖，說明Subject、Role、Permission之間的關聯關係，特別是Permission Assignment（PA）的重要性。作者強調Role與Group的差異：Role代表能執行某個任務的授權，具有業務涵義；而Group僅是分類工具。文章以訂單管理系統為例，定義了系統管理員、業務主管、業務專員三種角色，以及訂單的CRUD+Query五種權限。作者提出兩張關鍵對照表：Permission Assignment（角色與權限的對應）和Operation Assignment（權限與功能的對應）。透過這兩張表的組合，可以推導出Role與Operation的最終對照表。作者特別強調，這些角色和權限的定義應該在設計階段就確定，對應實際的業務流程和職務功能，而非在運行時期任意調整。

## 問答集

### Q1: 權限管理與一般的功能開發有什麼本質差異？
Q: 為什麼權限管理被視為商業需求而非純技術需求？
A: 權限管理的核心是要對應實際的業務流程和組織職責。它不僅涉及技術實作，更重要的是要反映真實世界中誰應該能做什麼事情。權限設計必須考慮組織架構、工作流程、職務分工等商業因素，因此是業務需求的技術實現，而非單純的技術問題。

### Q2: IIdentity和IPrincipal這兩個介面的設計理念是什麼？
Q: .NET Framework為什麼要將認證分為IIdentity和IPrincipal兩個層次？
A: IIdentity專注於身分識別的基本資訊（姓名、是否認證、認證類型），而IPrincipal則負責角色相關的授權檢查。這種分層設計符合認證與授權分離的原則，讓身分識別與權限檢查各司其職。IPrincipal透過IsInRole方法提供查詢介面而不直接暴露角色清單，這種設計增加了安全性和彈性。

### Q3: 在RBAC中，Role和Group有什麼重要差異？
Q: 為什麼不能將Role當成Group來使用？
A: Role代表的是「能執行某個任務的授權」，具有明確的業務涵義和權限意涵。當你指派Role給使用者時，就等於授權他執行特定任務。而Group僅是分類工具，本身不包含授權意涵。Role應該對應實際的職務功能（如job function），在系統設計階段就應該確定，而不是讓管理者隨意創建。

### Q4: 為什麼權限設計要在開發階段就確定而非運行時調整？
Q: 提供彈性的權限設定介面不是更好嗎？
A: 權限設計應該反映系統的業務邏輯和安全原則，這些是產品規格的一部分，應該在設計階段就經過仔細分析確定。如果允許運行時任意調整，容易導致權限設定混亂，最終可能變成每個角色都能做所有事情，權限機制形同虛設。正確的做法是將Role、Permission、Permission Assignment視為系統的「憲法」。

### Q5: Permission和Operation在設計上有什麼不同的考量？
Q: 如何決定哪些功能應該設計為Permission，哪些設計為Operation？
A: Permission應該對應系統的基本操作，通常是資料的CRUD+Query，或者是業務流程中的狀態轉移操作。Operation則是使用者實際看到的功能選單或按鈕。一個Operation可能需要多個Permission的組合才能執行。這種設計能將上百個功能簡化為1-20個Permission的組合，大幅降低管理複雜度。

## 解決方案

### 問題：如何建立基礎的認證與授權架構
問題：在.NET應用程式中如何正確實作認證與授權機制？
根本原因：缺乏對認證與授權分離原則的理解，以及對.NET內建安全介面的掌握不足
解決方案：
- 使用IIdentity介面處理身分識別（姓名、認證狀態、認證類型）
- 透過IPrincipal介面的IsInRole方法進行角色檢查
- 在Console應用程式中使用Thread.CurrentPrincipal存放認證結果
- 在Web應用程式中使用HttpContext.User取得當前使用者
- 善用AuthorizeAttribute簡化MVC控制器的權限檢查

範例程式碼：
```csharp
// Console應用程式
static void Sales_Report()
{
    var user = Thread.CurrentPrincipal;
    if (user.IsInRole("manager"))
    {
        Console.WriteLine("Query orders: ......");
    }
    else
    {
        Console.WriteLine("No permission to query orders.");
    }
}

// MVC控制器
[Authorize(Roles = "manager")]
public class ControlPanelController : Controller
{
    public IActionResult Sales_Report() =>
        Content("query orders: ......");
}
```

### 問題：如何設計可擴展的權限管理介面
問題：如何定義權限管理的核心介面，支援不同的授權機制？
根本原因：缺乏對權限管理核心概念的抽象化，無法支援RBAC、PBAC、ABAC等不同機制
解決方案：
- 定義ICustomRole介面封裝角色概念
- 設計ICustomPermission介面，包含IsGranted方法檢查權限
- 建立ICustomOperation介面，列舉執行操作所需的權限
- 實作ICustomAuthorization介面，提供統一的授權檢查方法
- 將Permission設計為基本操作單位，Operation設計為使用者可見功能

介面定義：
```csharp
public interface ICustomPermission
{
    string Name { get; }
    bool IsGranted(IPrincipal user);
}

public interface ICustomOperation
{
    string Name { get; }
    IEnumerable<ICustomPermission> RequiredPermissions { get; }
}

public interface ICustomAuthorization
{
    bool IsAuthorized(IPrincipal user, ICustomOperation operation);
}
```

### 問題：如何正確設計RBAC權限架構
問題：在實際業務系統中如何規劃角色、權限和功能的對應關係？
根本原因：對RBAC概念理解不清，角色定義不當，或權限粒度設計不合理
解決方案：
- 角色定義要對應實際的業務職能，而非任意分組
- 權限設計要對應系統的基本操作（如CRUD+Query）
- 建立Permission Assignment表格（Role vs Permission）
- 建立Operation Assignment表格（Permission vs Operation）
- 透過兩表組合推導出最終的Role vs Operation對照
- 在程式碼中固化角色和權限的定義，避免運行時隨意調整

設計案例：
- 角色：系統管理員、業務主管、業務專員
- 權限：order-create、order-read、order-update、order-delete、orders-query
- 功能：業績查詢、當日訂單總覽、輸入訂單、訂單狀態更新、訂單批次作業

權限分配原則：
- 業務主管：只能讀取和查詢，不能修改訂單
- 業務專員：可以進行訂單CRUD，但不能大範圍查詢
- 系統管理員：專注於系統維護，不涉及業務操作

## 版本異動紀錄

### v1.0 (2025-08-03)
- 初始版本，基於原始文章內容生成
- 包含權限管理基礎概念、RBAC設計原理的完整分析
- 提供實用的程式碼範例和設計指導原則
