# 原來 System.Net.Mail 也會有 Bug …

## 摘要提示
- System.Net.Mail: 在 .NET 框架中寄送含中文郵件時可能因內部實作瑕疵而失敗  
- Asian Encoding: 中文信件需以 Big5（950）或其他編碼正確轉碼，否則 SMTP 伺服器拒收  
- 例外狀況 SmtpException: 寄信時拋出「標頭值中找到無效的字元」的 FormatException  
- MailAddress.ToString(): 第一次被呼叫即快取未編碼的結果，導致後續送信使用錯誤標頭  
- ToEncodedString(): 正確將 DisplayName 轉成「=?charset?B?...?=」格式，可正常寄信  
- fullAddress 快取: 兩個方法共用同一私有欄位 fullAddress，卻未保證內容一致  
- 測試程式: 只要在寄送前 Console.WriteLine(mail.From) 就能穩定重現問題  
- 反組譯追蹤: 利用 Reflector 逐層比對 System.Net.Mime.HeaderCollection 與 MailAddress 原始碼  
- IsAnsi 檢查: 例外實際在 HeaderCollection.Set 被觸發，但問題源自更上層的錯誤快取  
- Debug 經驗: 兩天排查確定是 Microsoft 內部 Bug，非程式使用者邏輯錯誤  

## 全文重點
作者在撰寫 .NET 應用程式寄送中文郵件時，原本以 Big5 編碼設定 MailMessage、MailAddress 與 SubjectEncoding，測試寄信皆正常；然而為了在主控台列出寄件者資訊，他於寄送前加上一行 `Console.WriteLine("準備寄信 (From: {0})", mail.From)`，卻立即在 `SmtpClient.Send` 拋出 `SmtpException`，內含「標頭值中找到無效的字元」的 `FormatException`。  
同樣程式在 Windows XP、Server 2003、Vista、中英文版及已套用所有更新的環境皆可重現，可排除作業系統與語系差異。作者因而深入 dump 與 call stack，借助 Reflector 反組譯 .NET 程式庫，鎖定 `System.Net.Mime.HeaderCollection.Set` 內 `IsAnsi` 檢查引發例外；然而 `IsAnsi` 判定只要字元碼小於 0xFF 即視為通過，與中文內容衝突的可能性不高。  
進一步回溯 value 的來源，發現是 `System.Net.Mail.MailAddress.ToEncodedString()` 的回傳值，並注意到 `ToEncodedString()` 與 `ToString()` 共用同一個私有欄位 `fullAddress` 來避免重複編碼。`ToEncodedString()` 會呼叫 `MailBnfHelper.GetDotAtomOrQuotedString()` 將中文顯示名稱編碼為 MIME 標準的「=?big5?B?...?=」格式，因此若直接寄信一切正常；但 `ToString()` 的實作卻僅將 `DisplayName` 以引號包起並拼上 `<address>`，完全沒有編碼動作。  
當程式在寄信前呼叫 `mail.From.ToString()` 供 `Console.WriteLine` 使用時，`fullAddress` 被第一次設定成未編碼的版本；之後 `SmtpClient.Send` 再呼叫 `ToEncodedString()` 時，因為 `fullAddress` 已有值而直接取用，結果把未經轉碼的中文寫進郵件標頭，SMTP Client 檢查時便視為非法字元而拒絕。  
根因即是 `MailAddress.ToString()` 與 `ToEncodedString()` 對 `fullAddress` 欄位缺乏同步與一致性設計，導致快取內容可能是錯誤格式。作者歷經兩天追查後確認此為 .NET Framework 內部缺陷，並非使用者程式碼錯誤，也藉此提醒開發者在國際化情境下需特別注意庫函式對亞洲語系的支援與可能的隱藏 bug。  

## 段落重點
### Bug 發現與重現步驟
作者使用 Big5 編碼建立 MailMessage，原始寄信程式碼運作正常；但在寄信前新增 `Console.WriteLine(mail.From)` 後，無論在各版本 Windows 均引發 `SmtpException`。此步驟證實只要呼叫 `MailAddress.ToString()` 即可穩定重現問題。

### 例外訊息與環境測試
錯誤訊息為「標頭值中找到無效的字元」，來自 `System.Net.Mail.SmtpException` 包裝的 `FormatException`。作者在 XP、2003、Vista、中英文版及已完成 Windows Update 的環境測試，結果一致，排除作業系統差異。

### 反組譯追蹤與程式庫分析
透過 Reflector 反組譯 System.Net 組件，作者先定位 `HeaderCollection.Set` 中的 `IsAnsi()`，確認驗證機制並未直接造成問題，再往上追至 `MailAddress.ToEncodedString()`。兩個方法共用同一個 `fullAddress` 欄位；`ToEncodedString()` 會將 DisplayName 依 RFC2047 編碼，`ToString()` 則直接輸出未編碼字串。

### 問題根因與結論
由於 `ToString()` 先被呼叫且寫入 `fullAddress`，後續 `ToEncodedString()` 便取得錯誤快取，將未編碼中文字寫入郵件標頭，引發 SMTP 驗證失敗。此設計瑕疵證明 System.Net.Mail 對亞洲語系仍存在隱患；開發者若需顯示 MailAddress 應避免使用 `ToString()`，或手動重建 MailAddress 物件。作者亦呼籲 Microsoft 修補此 bug，以免更多人踩坑。