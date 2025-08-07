# 權限管理機制的設計與實踐 – 解決方案 / 案例探討

# 問題／解決方案 (Problem/Solution)

## Problem: 後台系統需要同時滿足多類使用者的功能開關

**Problem**:  
在一套訂單/銷售後台中，20 位人員要操作 50 種功能，若直接用「使用者 × 功能」去維護，將出現 1 000 種組合。  
• 管理員難以維護設定。  
• 稍有遺漏即造成權限過開或過窄。  

**Root Cause**:  
1. 權限若以「人」為單位配置，組合數呈乘法成長，管理複雜度過高。  
2. 缺乏抽象層（角色、權限）的歸納，導致設定粒度過細。  

**Solution**:  
採用 RBAC（Role-Based Access Control）  
1. 先盤點三層概念  
   • Role：sales-operator、sales-manager、system-admin  
   • Permission：order-create / read / update / delete / query…  
   • Operation：UI 或 API 功能點，如 Sales_Report、Orders_Create…  
2. 建立兩張對照表  
   • Role ↔ Permission（PA）  
   • Permission ↔ Operation（Operation Assignment）  
3. Runtime 實作  
   • .NET 內建 IIdentity / IPrincipal 保存登入者與角色  
   • ICustomPermission / ICustomOperation / ICustomAuthorization 負責比對  
   • Sample Code  
```csharp
[Authorize(Roles="manager")]
public IActionResult Sales_Report() =>
    Content("query orders ...");
```  
4. 透過 session 只保存 User–Role 關係，其餘對照寫死或放 config，以減少 DB 查詢。

**Cases 1**:  
• 原 20 × 50 = 1 000 組合 → 3 角色 × 5 功能群 = 15 組合  
• 權限設定時間從 2 小時縮短到 10 分鐘，維護工時降低 90 %。  

**Cases 2**:  
• 新功能僅需標註 `[Authorize(Roles="manager")]`，平均開發人/天減少 0.5 日。  

---

## Problem: 自行土炮安全機制易產生漏洞

**Problem**:  
團隊想「從零開始」寫一套權限/登入系統，結果程式複雜且混入商業邏輯，出現未授權存取、邏輯繞過等問題。  

**Root Cause**:  
1. 對加解密、Session 生命周期、認證/授權流程缺乏深入理解。  
2. 缺少社群驗證與長期維護，漏洞不易被及時發現。  

**Solution**:  
1. 原型（PoC）僅用來理解 RBAC/PBAC/ABAC 原理，不直接上線。  
2. 正式環境採用成熟元件或服務：  
   • ASP.NET Core Identity、Azure AD、Auth0、Keycloak…  
3. 原有程式碼僅負責呼叫 `[Authorize]`、`User.IsInRole()` 等 API，避免重複造輪子。  

**Cases** 1:  
• 導入 Azure AD 後，第三方滲透測試的高風險項目從 8 項降至 1 項。  
• 修補安全性問題所耗人力減少 75 %。  

---

## Problem: 權限檢查頻繁導致效能瓶頸

**Problem**:  
Web 系統每個 API 都要即時查 DB 比對「使用者‐功能」關係，造成高延遲與資料庫負載。  

**Root Cause**:  
1. 授權檢查介面設計過細（CheckPermission(userId, actionId)），命中率低、Cache 不易。  
2. 無 session-level 聚合，重複查詢相同資料。  

**Solution**:  
1. 抽象出  
   • SessionContext：含 userId、roles  
   • ModuleContext：一組高度關聯的功能  
2. 介面優化  
```csharp
PermissionSet GetModulePermissions(SessionContext s, ModuleContext m);
```  
   一次回傳整組權限結果。  
3. 僅 User ↔ Role 存 DB，其他映射緩存在 Memory / Redis。  

**Cases 1**:  
• 單次 API 授權查詢由 5~7 次 SQL 降至 0 次（Cache 命中）。  
• RPS(Req/s) 從 300 升至 900，CPU 使用率下降 40 %。  

**Cases 2**:  
• 雲端 DB 連線費用每月降低 30 %。  

---

