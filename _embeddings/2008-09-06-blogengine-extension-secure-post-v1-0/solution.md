# BlogEngine Extension: Secure Post v1.0

# 問題／解決方案 (Problem/Solution)

## Problem: 在 BlogEngine.NET 中為「特定文章」提供不需帳號登入的密碼保護

**Problem**:  
搬家至 BlogEngine.NET 前，家中長輩提出「只有在特定文章輸入密碼才能閱讀」的需求；若無此功能就拒換系統。過去嘗試過 IIS 整合式驗證，但結果是「該看的看不到，不該看的仍看得到」，不合用。官方現有的 Password Protected Post Extension 又需要先建立帳號並以角色/分類授權，違反「不想替每個讀者建帳號」的原始需求。

**Root Cause**:  
1. BlogEngine.NET 核心並未內建「單篇貼文密碼鎖」功能。  
2. 官方/社群現有 Extension 走帳號 + 角色權限機制，無法滿足「輸入暗號即可閱讀」的極簡場景。  
3. 直接使用 IIS 或資料夾層級驗證只能做到整站或整資料夾保護，無法精確到「單篇」；且使用體驗複雜，易造成授權錯誤。

**Solution**:  
自製 Extension「SecurePost」，流程與關鍵碼如下：  
1. 監聽 `Post.Serving` 事件：所有貼文輸出前都會觸發，方便攔截與替換內容。  
2. 啟用條件：文章內容開頭若含 `[password]` 字串，便視為受保護貼文。  
3. 驗證機制 (Server Side)  
   ```csharp
   if (HttpContext.Current.User.Identity.IsAuthenticated) return;      // 已登入者直接放行
   if (HttpContext.Current.Request["pwd"] == Password) return;         // 比對 QueryString pwd
   if (!e.Body.StartsWith("[password]", StringComparison.CurrentCultureIgnoreCase)) return;
   ```  
4. 若密碼尚未通過：動態改寫 `e.Body`，顯示提示＋密碼輸入欄，提交後把 `?pwd=<使用者輸入>` 回送至同篇貼文 URL。  
5. ExtensionSettings：讓管理者於「Extension Manager」介面自訂  
   • SecurePostMessage – 遇到保護文章時的訊息  
   • PasswordHint      – 密碼提示文字  
   • PasswordValue     – 真正密碼  
   範例設定碼（擷取）：  
   ```csharp
   ExtensionSettings settings = new ExtensionSettings("SecurePost");
   settings.AddParameter("SecurePostMessage","顯示訊息:");
   settings.AddParameter("PasswordHint","密碼提示:");
   settings.AddParameter("PasswordValue","指定密碼:");
   settings.AddValues(new[] { "本篇文章已受密碼保護...", "一二三四", "1234" });
   settings.IsScalar = true;
   ExtensionManager.ImportSettings(settings);
   _settings = ExtensionManager.GetSettings("SecurePost");
   ```  
6. 完整程式不足 100 行，放入 `~/App_Code/Extension/SecurePost.cs` 即完成「安裝」。

**為何能解決 Root Cause**  
• 直接在貼文輸出階段攔截 → 精確至單篇文章。  
• 不涉及 BlogEngine 角色/帳號 → 使用者無須註冊登入。  
• 驗證邏輯放在 Server Side → View Source 不會洩漏密碼或全文。  
• 透過 ExtensionSettings → 不需另建資料表或檔案，即能後台 UI 調整參數，維持「夠簡單」。

**Cases 1**:  
背景：家中長輩只想閱讀特定家庭照／文章，其他訪客須先輸入暗號。  
流程：  
a. 在受保護文章開頭加上 `[password]`。  
b. 於 Extension Manager 設定「顯示訊息／提示／密碼」。  
c. 發布文章後，訪客僅看到「本篇文章已受密碼保護...」與密碼輸入框；輸入正確密碼後重導，方能閱讀全文。  
效益：  
• 無需創建任何帳號；長輩可直接分享密碼給親友。  
• 全部作業時間 < 30 分鐘（下載原始碼、複製 .cs、後台設定）。  
• 成功說服家中長輩轉用 BlogEngine.NET。

**Cases 2**:  
背景：部落格作者偶爾發布公司內部教學筆記，需要臨時封鎖。  
流程：  
• 在貼文前綴 `[password]`，設定一次性密碼後公開連結。  
• 日誌分享完畢可直接移除 `[password]` 標籤即解除保護。  
效益：  
• 不必動用伺服器層級權限或新增分類/角色。  
• 重複利用同一 Extension 設定，減少維護成本。  

---