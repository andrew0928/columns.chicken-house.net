---
layout: synthesis
title: "原來 System.Net.Mail 也會有 Bug ..."
synthesis_type: summary
source_post: /2007/04/06/system-net-mail-bug-discovered/
redirect_from:
  - /2007/04/06/system-net-mail-bug-discovered/summary/
---

# 原來 System.Net.Mail 也會有 Bug ...

## 摘要提示
- System.Net.Mail Bug: 在寄信前呼叫 MailAddress.ToString 會破壞編碼，導致後續寄信失敗
- 亞洲語系顯示名: 中文顯示名稱（Big5/非 ASCII）是觸發問題的關鍵
- 可重現條件: 任何語系的 XP/2003/Vista，打齊更新皆可重現
- 例外症狀: SmtpException 包 FormatException，訊息為「標頭值中找到無效的字元」
- 觸發點: Console.WriteLine("{0}", mail.From) 隱式呼叫 ToString 即會出錯
- 根因分析: MailAddress.FullAddress 快取與 ToString 未編碼，污染後續使用
- 正確路徑: ToEncodedString 會正確編碼，但 ToString 的實作有誤
- 原始碼線索: HeaderCollection.Set 中 IsAnsi 檢查不過，因 value 被未編碼字元污染
- 避免策略: 不在送信前呼叫 ToString；要顯示請用 Address/DisplayName 自行格式化
- 教訓總結: 缺乏 i18n 測試與重複實作未重構，易引發快取與編碼的副作用

## 全文重點
作者在使用 .NET 的 System.Net.Mail 寄送含中文顯示名稱的郵件時，若直接寄送，運作一切正常；但若在送出前為了記錄訊息而印出 mail.From（造成隱式呼叫 MailAddress.ToString），寄送即失敗，拋出 SmtpException，內含 FormatException，訊息指「標頭值中找到無效的字元」。問題在多台、不同 Windows 版本與語系環境都可重現。

作者以反組譯追查呼叫堆疊，發現 HeaderCollection.Set 會檢查標頭字元是否為 ANSI；而產生該值的來源，是 MailAddress 在組合 fullAddress 的過程。MailAddress 有一個 fullAddress 的私有快取欄位，ToEncodedString 與 ToString 兩者在第一次建構 fullAddress 時會各自執行其實作：前者會對顯示名稱做 MIME 編碼後再組字串；但後者卻將 DisplayName 直接包上引號而未做任何編碼。由於 fullAddress 被快取，一旦先呼叫 ToString，快取就被未編碼的內容污染，後續 SmtpClient.Send 在準備標頭時取用這個不合法的值，因含有非 ASCII 的中文而觸發 FormatException。

因此，問題不在 SMTP 傳送程序或環境設定，而是 .NET Framework 中 MailAddress 的實作瑕疵：ToString 與 ToEncodedString 重複實作但未共享正確的編碼流程，且搭配 fullAddress 快取引發副作用。務實的避險方式是：不要在送信前呼叫 mail.From.ToString；若要記錄，請使用 mail.From.Address 與 mail.From.DisplayName 自行組字串（或在記錄後重新建立 MailAddress 再指派給 mail.From）。此案例也凸顯國際化/在地化測試與重構（消除重複邏輯）的重要性。

## 段落重點
### 問題背景與示例程式碼
作者以 System.Net.Mail 建立 MailMessage，From/To 的顯示名稱使用中文並設定 Big5（950）編碼，主旨與主體也正常配置，直接呼叫 SmtpClient.Send 能成功寄出且編碼無誤。為了在寄出前增加友善的日誌輸出，作者加入 Console.WriteLine("準備寄信 (From: {0})", mail.From)。看似無害的輸出，實際上觸發了 mail.From 的 ToString，被證實是後續錯誤的導火線。此改動前後，唯一差別就是是否對 MailAddress 做 ToString 呼叫。

### 加入 ToString 後的例外與重現情境
加入 Console.WriteLine 後，送信即拋出 SmtpException，內含 FormatException，指出郵件標頭含有無效字元。作者在 Windows XP、Server 2003、Vista，含中英文版系統，且皆安裝最新更新，均能重現，顯示問題與環境無關而是程式庫問題。此處的關鍵是 ToString 將 DisplayName 中的中文帶入 header 組裝流程，若未經 MIME 編碼，會包含非 ASCII 字元，違反標頭規範，導致失敗。

### 追蹤呼叫堆疊與原始碼分析
作者依例外堆疊進入 HeaderCollection.Set，看到當 value 非 ANSI 時就丟出 FormatException；再往回追到 MailAddress 的 ToEncodedString 與 ToString。MailAddress 透過私有欄位 fullAddress 快取已經組好的完整位址字串。ToEncodedString 的實作會對顯示名稱進行正確的編碼後再組合 <address> 格式；但 ToString 的實作卻直接以引號包裹 DisplayName 而不經任何編碼。因兩者都會在 fullAddress 為空時初始化該快取，一旦先呼叫 ToString，就以未編碼的內容填入快取，使後續寄送流程撿到錯的值並遭檢查擋下。

### Bug 根因、影響與應對策略
根因是重複邏輯未重構與快取副作用：ToString 沒做 MIME 編碼，卻會填滿 fullAddress 快取；之後 Send 路徑原本應透過 ToEncodedString 的正確結果，卻被快取覆蓋。影響範圍是所有包含非 ASCII（尤其中文顯示名稱）的 MailAddress，且只要在送信前任何地方呼叫了 ToString 就會中標。建議做法：避免在寄送前呼叫 mail.From/To 的 ToString；記錄時改用 Address 與 DisplayName 自行格式化，或在記錄後重新建立 MailAddress 並再次指派；也可延後記錄到寄送完成後。此事件提醒開發者重視 i18n 測試、避免重複實作與留心快取對外部行為的副作用。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 電子郵件基本結構與標頭（From/To/Subject）與 RFC 規範（RFC 2822/5322、RFC 2047）
   - 字元編碼與語系（ASCII、ANSI、UTF-16、Big5/950、MIME encoded-word）
   - .NET 的 System.Net.Mail 常用類別（MailMessage、MailAddress、SmtpClient）
   - 例外處理與除錯基本流程（call stack、反編譯觀念）

2. 核心概念：
   - System.Net.Mail 在含非 ASCII 顯示名稱時的標頭編碼需求
   - MailAddress.ToString 與 ToEncodedString 行為差異與內部快取欄位 fullAddress
   - 無意間呼叫 ToString 造成 fullAddress 被以未編碼內容快取，導致後續送信時 Header 驗證失敗
   - HeaderCollection 與 MimeBasePart.IsAnsi 的檢核邏輯（禁止非 ANSI 未編碼字元進入標頭）
   - 除錯追溯：從 SmtpException → FormatException → HeaderCollection.Set → MailAddress.ToEncodedString/ToString

3. 技術依賴：
   - MailMessage 依賴 MailAddress（From/To）
   - SmtpClient.Send 依賴 Message.PrepareHeaders → HeaderCollection.Set
   - HeaderCollection.Set 依賴 MimeBasePart.IsAnsi 做標頭值合法性檢查
   - MailAddress 的輸出依賴 encodedDisplayName 與 fullAddress（由 ToEncodedString/ToString 設定）
   - MailBnfHelper/GetDotAtomOrQuotedString 用於產出合法的 RFC 字串

4. 應用場景：
   - 以 System.Net.Mail 寄送含中文（或任何非 ASCII）寄件者/收件者顯示名稱的郵件
   - 寫 log 或 Console 輸出 MailAddress 物件時避免影響後續送信
   - 建置國際化/本地化郵件系統，確保標頭正確編碼
   - 單元測試與回歸測試，驗證非 ASCII 標頭在不同環境（XP/2003/Vista、中英文版）的一致性

### 學習路徑建議
1. 入門者路徑：
   - 認識 System.Net.Mail：建立 MailMessage、設定 From/To/Subject/Body、使用 SmtpClient.Send
   - 了解字元編碼基本概念與 SubjectEncoding、BodyEncoding 的設定
   - 嘗試寄送含中文主旨與內文的郵件，觀察收信端顯示

2. 進階者路徑：
   - 深入 RFC 2047（MIME encoded-word）與 RFC 5322 的標頭格式要求
   - 研究 MailAddress、HeaderCollection、MimeBasePart 的內部行為與限制
   - 練習從例外訊息與 call stack 反查源頭；使用反編譯工具理解框架實作

3. 實戰路徑：
   - 重現問題：在含中文 DisplayName 的 MailAddress 上呼叫 ToString，再寄送並觀察 SmtpException/FormatException
   - 採取防呆：避免在送信前呼叫 MailAddress.ToString；改以顯式輸出 mail.From.Address 或手工格式化
   - 撰寫封裝/輔助方法：提供安全的記錄/輸出函式，或於建構 MailAddress 後立即以 ToEncodedString 產出安全字串用於 log
   - 加入單元測試覆蓋含非 ASCII 顯示名稱的情境，避免回歸

### 關鍵要點清單
- System.Net.Mail 非 ASCII 標頭需求: 郵件標頭含中文等非 ASCII 必須依 RFC 2047 正確編碼才可被接受 (優先級: 高)
- 問題觸發條件: 在送信前對 MailAddress 呼叫 ToString 會以未編碼內容設定 fullAddress，進而導致錯誤 (優先級: 高)
- 例外與訊息: 典型錯誤為 SmtpException 包裹 FormatException「標頭值中找到無效的字元」(優先級: 高)
- 正確做法的對比: ToEncodedString 會處理（或沿用）已編碼的顯示名稱，而 ToString 的實作未編碼且會快取 (優先級: 高)
- fullAddress 快取副作用: 第一次呼叫若用錯方法，之後即便正確流程也會沿用錯誤快取 (優先級: 高)
- HeaderCollection.Set 驗證: 送入的標頭值若含超出 ANSI 的字元且未經編碼，會被 MimeBasePart.IsAnsi 擋下 (優先級: 中)
- Logging 影響行為: 對物件做 Console.WriteLine("{0}", mail.From) 會隱式呼叫 ToString，可能改變物件內部狀態 (優先級: 高)
- 語系與平台: 問題與 OS 語系/版本無關，在 XP/2003/Vista 皆可重現 (優先級: 中)
- 避免方式一: 記錄時輸出 mail.From.Address 或自組 $"\"{displayName}\" <{address}>" 並自行確保編碼 (優先級: 高)
- 避免方式二: 若需完整字串，使用 ToEncodedString 的結果作為輸出，不要呼叫 ToString (優先級: 高)
- 主旨與內文編碼: 仍需正確設定 SubjectEncoding/BodyEncoding，避免顯示亂碼 (優先級: 中)
- 測試策略: 建立含中文顯示名稱的單元測試，涵蓋「呼叫/不呼叫 ToString」兩種路徑 (優先級: 中)
- 除錯技巧: 從 call stack 反查到 HeaderCollection/IsAnsi，再反編譯 MailAddress 比對 ToString/ToEncodedString 實作 (優先級: 中)
- 風險認知: 第三方或框架方法的副作用（如快取）可能影響後續流程，應審慎呼叫 (優先級: 中)
- 維運建議: 在記錄管線中對 MailAddress 統一走安全輸出方法，避免運維診斷日志觸發問題 (優先級: 中)