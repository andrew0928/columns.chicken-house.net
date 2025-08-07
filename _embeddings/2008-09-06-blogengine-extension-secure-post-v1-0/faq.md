# BlogEngine Extension: Secure Post v1.0

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 作者為什麼要自己撰寫 Secure Post 這個 BlogEngine.NET 擴充功能？
為了滿足家人「只有部分文章需要輸入密碼才能閱讀，且不想建立帳號或登入」的需求，而官方或社群現有的 Password Protected Post 擴充功能必須先登入並依角色授權，無法達成「輸入暗號即看文」的簡易模式，所以作者決定自行開發。

## Q: Secure Post 與現成的 Password Protected Post 擴充程式有何主要差異？
Password Protected Post 透過使用者登入及角色 (ROLE) 與分類 (CATEGORY) 配對來控制存取；Secure Post 則完全不需要帳號與登入，只要輸入作者設定的單一密碼即可閱讀指定文章。

## Q: Secure Post 如何判斷哪些文章需要密碼保護？
文章內容開頭只要出現字串「[password]」，Secure Post 便會啟用密碼保護機制；未含此字串的貼文則維持原本公開狀態。

## Q: 尚未登入的讀者若要閱讀受保護文章，畫面流程是什麼？
1. 讀者僅會看到作者自訂的提示訊息與一個密碼輸入框。  
2. 輸入正確密碼後按 [GO]，瀏覽器會帶著 `?pwd=使用者輸入值` 回到同一篇文章。  
3. 伺服器端確認密碼正確後才顯示完整內容；否則仍顯示輸入框。

## Q: Secure Post 是否要求使用者先登入 BlogEngine？
不需要。只要輸入正確密碼即可閱讀；而已登入 (Authenticated) 的使用者則直接跳過密碼檢查。

## Q: 密碼在網址列會以明碼出現，作者為何仍採用此做法？
作者只要求「基本防護」：  
1. 密碼驗證必須在伺服器端完成。  
2. 在客戶端（瀏覽器）未輸入密碼前不得出現文章內容。  
進階的加密／雜湊 (Hash) 與竊聽防護並非此版本目標，因此直接使用明碼以降低前後端實作複雜度。

## Q: Secure Post 提供哪些可由 Extension Manager 調整的參數？
1. SecurePostMessage – 文章被保護時顯示的提示文字。  
2. PasswordHint – 給讀者的密碼提示。  
3. PasswordValue – 實際要比對的密碼。

## Q: 程式實作上採用了哪個事件來攔截並修改文章輸出？
在 static constructor 中掛接 `Post.Serving` 事件，於事件處理函式 `Post_Serving` 中決定是否替換文章內容或直接送出原文。

## Q: 安裝 Secure Post 的步驟是什麼？
1. 將全文程式碼存為 `~/App_Code/Extension/SecurePost.cs`。  
2. 重新編譯／重啟網站後，以管理者登入 BlogEngine 後台。  
3. 在 Extension Manager 啟用 SecurePost，並透過 [編輯] 連結設定提示文字、密碼提示與密碼。

## Q: Secure Post 的程式碼量大概有多少？
包含設定與功能不到 100 行 C# 程式碼，核心邏輯僅幾十行即可運作。

## Q: 開發者對散佈 Secure Post 有何小小要求？
歡迎自由取用與散佈，但請不要另行上傳程式檔到其他下載點，僅需提供原始文章的網址即可，並鼓勵留下回饋或推文支持。