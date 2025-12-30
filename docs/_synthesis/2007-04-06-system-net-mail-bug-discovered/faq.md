---
layout: synthesis
title: "原來 System.Net.Mail 也會有 Bug ..."
synthesis_type: faq
source_post: /2007/04/06/system-net-mail-bug-discovered/
redirect_from:
  - /2007/04/06/system-net-mail-bug-discovered/faq/
---

# 原來 System.Net.Mail 也會有 Bug …

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

Q1: 什麼是 System.Net.Mail？
- A簡: .NET Framework 的內建郵件傳送命名空間，提供建立郵件、設定標頭與透過 SMTP 寄送的 API，如 MailMessage、MailAddress、SmtpClient 等。
- A詳: System.Net.Mail 是 .NET Framework 中用於寄送電子郵件的核心命名空間。它提供 MailMessage（封裝郵件主旨、本文、收件人、附件）、MailAddress（封裝郵件地址與顯示名稱）與 SmtpClient（透過 SMTP 伺服器送出郵件）等常用類別。其設計遵循 SMTP 與 MIME/RFC 5322 等標準，並在屬性上提供編碼設定（如 SubjectEncoding、BodyEncoding），以便處理非 ASCII 的語系文字。相較早期 System.Web.Mail，System.Net.Mail 有較高的型別安全性與可擴充性。本文案例正是使用這些類別寄送含中文的郵件顯示名稱時，觸發標頭編碼與 API 實作缺陷，導致例外拋出，顯示這些 API 在多語系情境中的細節相當重要。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q3, B-Q1

Q2: 什麼是 MailMessage？
- A簡: 表示一封郵件的物件，包含 From、To、Subject、Body、Attachments 等欄位，並可設定編碼與內容格式。
- A詳: MailMessage 是用來描述一封完整電子郵件的類別，核心屬性包含 From（寄件者，MailAddress）、To/CC/BCC（收件者集合）、Subject/SubjectEncoding（主旨與其編碼）、Body/BodyEncoding（本文與其編碼）、IsBodyHtml（是否為 HTML 內容）與 Attachments。建立 MailMessage 後，透過 SmtpClient.Send 送出。對非 ASCII 語系，需特別設定 SubjectEncoding/BodyEncoding；收件人與寄件人顯示名稱則依 MailAddress 建構子提供的 Encoding 處理。本文問題出於 From 的 MailAddress 內部字串快取與 ToString 實作錯誤，導致產生未編碼的標頭值，觸發 InvalidHeaderValue 例外。理解 MailMessage 與其屬性如何被序列化成 SMTP 標頭與內容，是排除此類問題的基礎。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q3, B-Q2

Q3: 什麼是 MailAddress？
- A簡: 表示郵件地址的型別，包含 Address（email）與 DisplayName（顯示名稱），可指定顯示名稱的編碼。
- A詳: MailAddress 用於表示電子郵件地址結構。其 Address 屬性為純 email（例如 someone@example.com），DisplayName 為顯示名稱（例如 吳小皮），兩者可組合成標頭格式「顯示名稱 <地址>」。為支援非 ASCII 語系，建構子 MailAddress(string address, string displayName, Encoding displayNameEncoding) 可指定顯示名稱的編碼。內部會視需要將 DisplayName 依 RFC 2047 以「encoded-word」形式轉為 ASCII，確保標頭合法。但本文揭露 ToString 的實作錯誤，會把未編碼的 DisplayName 放入內部快取 fullAddress，之後寄送時被當成標頭值使用而失敗。正確流程應由內部 ToEncodedString 產出已編碼的標頭片段。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, A-Q9, B-Q4

Q4: 為什麼郵件標頭必須是 ASCII？為什麼需要編碼？
- A簡: 郵件標頭依 RFC 5322/2047 規範僅允許 ASCII；非 ASCII 必須以 encoded-word（例如 =?UTF-8?B?...?=）表示。
- A詳: 郵件標頭（如 From、Subject）早期為跨系統互通，規範僅允許 7-bit ASCII 字元（RFC 5322）。要在標頭使用非 ASCII（如中文、日文），需依 RFC 2047 轉成「encoded-word」格式，常見為 Base64 或 Quoted-Printable 搭配宣告字集（如 =?utf-8?B?...?=）。這樣一來標頭內容仍是 ASCII，卻能被收件端正確解碼並顯示。本文案例中，正確路徑是將 DisplayName 透過 MailAddress 與指定 Encoding 轉為 encoded-word；但 ToString 的錯誤把原始 Unicode 直接塞入標頭，導致 HeaderCollection 檢查時發出 InvalidHeaderValue。理解為何必須編碼，是處理多語系郵件可靠性的核心。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, B-Q4, B-Q15

Q5: 什麼是 MIME 標頭的 encoded-word（RFC 2047）？
- A簡: 在標頭中表示非 ASCII 的格式：=?charset?B|Q?encoded_text?=，確保整體仍為 ASCII 可傳輸。
- A詳: RFC 2047 規定的 encoded-word 用於在標頭（非內文）夾帶非 ASCII 字元。其形式為「=?字元集?編碼方式?編碼後字串?=」，常見編碼方式為 B（Base64）或 Q（Quoted-Printable）。例如中文名稱「吳小皮」以 UTF-8 Base64 可能呈現為「=?utf-8?B?5ZyL5bCP5bCP?=」。寄件者顯示名稱、主旨最常用這種表示。System.Net.Mail 在正確路徑下會自動產生此格式；本文問題即因 ToString 實作未產生 encoded-word 且污染快取，導致後續送出使用了未編碼的標頭字串，違反規範並被拒。了解 encoded-word 能幫助你檢視與除錯標頭是否合規。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, B-Q4, B-Q15

Q6: SubjectEncoding 與 MailAddress 顯示名稱編碼有何差異？
- A簡: SubjectEncoding 直接套用於主旨；顯示名稱編碼由 MailAddress 建構子指定並在序列化時轉 encoded-word。
- A詳: 在 System.Net.Mail 中，主旨的編碼由 MailMessage.SubjectEncoding 指定，寄送時會依此把主旨轉成 encoded-word，通常穩定可靠。而寄件者/收件者的顯示名稱編碼則由 MailAddress 的建構子第三參數設定；真正產生標頭時，內部會根據此 Encoding 將顯示名稱編為 encoded-word。本文情境中，主旨正常因其路徑正確；但 From 使用 MailAddress 並在送出前被外部 Console.WriteLine 誤觸 ToString（錯誤路徑），使未編碼的顯示名稱值被快取，導致後續寄送失敗。這也說明主旨與顯示名稱在 API 階層負責的模組不同，導致行為差異。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, A-Q8, C-Q1

Q7: Encoding.GetEncoding(950) 是什麼？為何使用？
- A簡: 950 為繁體中文 Big5 編碼代碼頁。設定後可正確將中文顯示名稱/主旨轉為標頭所需的 encoded-word。
- A詳: Encoding.GetEncoding(950) 回傳 Big5（繁體中文）編碼器，對於歷史上以 Big5 為主要環境的系統，將顯示名稱與主旨用此編碼轉換，收件端可正確解碼與顯示（前提是雙方郵件用戶端支援）。在 .NET 中，MailAddress 的 displayNameEncoding 與 MailMessage.SubjectEncoding 可以分別指定這個 Encoding。本文範例即使用 950，若採用 UTF-8（Encoding.UTF8）也可。重點是：正確的編碼要配合 encoded-word 生效；若像問題中的 ToString 錯實作讓未編碼的 Unicode 直接進入標頭，即使指定了 Encoding 也無用，因為它沒有被用在正確的轉換路徑中。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, C-Q1, B-Q15

Q8: 文中揭露的 Bug 是什麼？
- A簡: MailAddress.ToString 首次被呼叫時，將未編碼的顯示名稱組入 fullAddress 並快取，導致後續寄送用錯字串，造成標頭無效。
- A詳: Bug 核心在於 MailAddress 內部使用 fullAddress 欄位快取「序列化後的地址字串」。正確應由 ToEncodedString 產生（含 encoded-word）的已編碼字串；但 ToString 的實作在首次呼叫時，用未編碼的 DisplayName 產生形如 "顯示名稱" <address> 的字串並寫入 fullAddress。寄送時，系統檢查 fullAddress 已有值便直接重用，導致把未編碼的 Unicode 放入標頭。HeaderCollection 在 Set 時檢查非 ASCII 即丟出 FormatException「InvalidHeaderValue」，被 SmtpClient 包成 SmtpException。這使得「僅加一行 Console.WriteLine(mail.From)」也會讓寄送失敗，屬於因觀察導致行為改變的典型缺陷。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q5, D-Q2

Q9: MailAddress.ToString 與 ToEncodedString 有何差異？
- A簡: ToEncodedString 產生 RFC 合規、可用於標頭的編碼字串；ToString 實作出錯，未做編碼且汙染快取，導致後續寄送失敗。
- A詳: 依設計，ToEncodedString（internal）會根據 encodedDisplayName 與 Address，用 MailBnfHelper 等組件產生已編碼、可直接放入郵件標頭的 ASCII 字串。反之 ToString 應僅供顯示；但特定 .NET 版本其實作有缺陷：以未編碼的 DisplayName 建構 "DisplayName" <Address>，並將結果寫入 fullAddress。由於 fullAddress 被兩者共享，後續寄送改用這個未編碼值，違規於標頭 ASCII 要求而失敗。理解兩者差異可指導你避免呼叫 ToString 影響寄送，或以屬性（Address/DisplayName）自行格式化日誌。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q4, B-Q5

Q10: 什麼是 fullAddress 快取？為何會出問題？
- A簡: MailAddress 內部快取序列化結果的欄位；但被 ToString 寫入未編碼值，汙染後續寄送流程。
- A詳: 為避免重複計算，MailAddress 使用 private 欄位 fullAddress 快取第一次產生的「完整地址字串」。設計上，若 fullAddress 不為空，後續就直接重用。然而在缺陷版本中，ToString 也會寫入 fullAddress，且內容是未經 RFC 2047 編碼的字串；結果是：一旦程式在寄送前呼叫了 ToString（例如為了日誌），fullAddress 即被填入錯值，寄送時預期應由 ToEncodedString 產生的正確值被這個快取覆蓋，造成 InvalidHeaderValue。此類跨方法共用快取導致的污染，是物件狀態設計與不可變性的一個反面教材。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q13, D-Q2, C-Q6

Q11: 什麼是 IsAnsi 檢查？與錯誤有何關係？
- A簡: 標頭設定時會檢查是否僅含允許字元（ANSI/ASCII）；含非 ASCII 即拋 FormatException：InvalidHeaderValue。
- A詳: HeaderCollection.Set 在寫入標頭時，會先檢查值是否符合允許集合（實作以 IsAnsi 為名）。這個檢查目的是確保標頭只含可傳輸的 ASCII 字元，避免協定不相容與安全問題。若包含非 ASCII（如中文），正確做法是先用 encoded-word 轉成 ASCII 再寫入。本文錯誤路徑讓未編碼的顯示名稱直接落入 Set，導致 IsAnsi 檢查失敗而拋出 FormatException「InvalidHeaderValue」，再由 SmtpClient 包成 SmtpException「傳送郵件失敗」。因此例外訊息雖看似與 SMTP 相關，實際根因在標頭編碼前的字串生成。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, D-Q1, D-Q5

Q12: 為什麼一行 Console.WriteLine 就讓程式壞掉？
- A簡: 因為格式化輸出會呼叫 MailAddress.ToString，寫入錯誤的 fullAddress，影響後續寄送使用的標頭值。
- A詳: .NET 的 Console.WriteLine("...{0}...", obj) 會呼叫 obj.ToString() 取得字串表示。若傳入的是 MailAddress，缺陷版本的 ToString 會產生未編碼的 "DisplayName" <Address>，並快取到 fullAddress。寄送時，System.Net.Mail 看到 fullAddress 已有值就重用，導致非 ASCII 字元直接進入標頭，違反規範而被拒絕。這是典型的「觀察造成副作用」：為了日誌而呼叫 ToString，使物件內部狀態改變並影響行為。解法是避免以 {0} 輸出 MailAddress，改用 Address/DisplayName 屬性自行組字串，或在日誌之後重建 MailAddress。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, C-Q2, D-Q2

Q13: 這個問題與作業系統或語系設定有關嗎？
- A簡: 無關。於多個 Windows 版本與語系均可重現，核心在於 .NET 類別庫的實作缺陷。
- A詳: 文中驗證於 Windows XP、Server 2003、Vista 等不同版本，且中英文版、已更新最新修補的系統皆可重現同樣例外。例外訊息的語言會因系統語系不同而異，但錯誤類型與堆疊（SmtpException 包裝 FormatException: InvalidHeaderValue）一致。這顯示根因不在 OS 或更新，而在 .NET Framework 某一版本 System.Net.Mail 的 MailAddress 實作。也因此即便更換 SMTP 伺服器或作業系統，若程式碼與執行框架未更動，問題仍存在。最直接的避免方式在應用層修正呼叫模式或升級至修補版本。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: D-Q6, A-Q8, B-Q5

Q14: 為什麼說這是「忽略亞洲語系需求」的例子？
- A簡: 測試多集中於 ASCII 場景；未涵蓋 CJK 等非 ASCII 顯示名稱，導致邊界情況未被發現。
- A詳: 多語系支援常見陷阱是：開發與測試環境以英文為主，API 在 ASCII 場景運作正常，卻未覆蓋 CJK（中日韓）等非 ASCII 情境。本文缺陷即是 ToString 未編碼仍可在英文名（僅 ASCII）下通過，且快取機制亦不出錯；一旦換成中文顯示名稱，ASCII 檢查即失敗。這說明國際化（i18n）與在地化（l10n）測試的重要性，尤其是郵件、URL、檔名等需要嚴格字元集合的場域。良好實務包含：以多語系樣本自動化測試、使用 Unicode 資料集、檢查輸出是否符合 RFC 標準。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: D-Q9, C-Q3, B-Q8

Q15: 這個案例的核心啟示是什麼？
- A簡: 避免以 ToString 影響物件狀態；重視標準相容與多語系測試；日誌不應改變行為。
- A詳: 案例揭示三點：一、API 設計與實作應避免 ToString 影響內部狀態，快取應由單一正確路徑產生以免污染。二、遵循 RFC 的邊界條件（僅 ASCII 標頭）需以自動化測試覆蓋各語系；英文通過不代表國際化通過。三、日誌與偵錯輸出應設計為無副作用；當對象可能有昂貴或危險的 ToString，應改用可控屬性組字串。對使用者而言，短期可透過安全輸出與重新建立 MailAddress 規避；長期則應升級至已修復版本或評估替代函式庫。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: D-Q10, C-Q5, B-Q13

### Q&A 類別 B: 技術原理類

Q1: System.Net.Mail 寄信的主要流程為何？
- A簡: 建立 MailMessage；序列化標頭與內文；透過 SmtpClient 與 SMTP 伺服器溝通，傳送 DATA 與結束。
- A詳: 寄信流程大致為：1) 應用程式建立 MailMessage，填入 From、To、Subject、Body、附件等。2) SmtpClient.Send 觸發 Message.PrepareHeaders，將 MailMessage 轉換為標頭集合（HeaderCollection），其中會以 RFC 6449/5322/2047 規範編碼必要欄位（如主旨與顯示名稱）。3) 建立 SMTP 連線，進行 HELO/EHLO、MAIL FROM、RCPT TO 等命令；進入 DATA 階段傳送先前序列化的標頭與內文。4) 伺服器 250/354/250 回應後 QUIT。本文例外發生在步驟 2 的標頭準備；由於 From 標頭的值包含未編碼的非 ASCII，HeaderCollection.Set 檢查時即丟出 FormatException，尚未進入到資料實際傳輸階段。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, B-Q2, D-Q1

Q2: SmtpClient.Send 如何準備郵件標頭？
- A簡: 呼叫 Message.PrepareHeaders，將欄位轉 HeaderCollection，檢查合法性並套用必要的 MIME/RFC 編碼。
- A詳: 在 Send 開始前，MailMessage 需被轉為文字標頭與本文。Message.PrepareHeaders 會組合 From、To/CC/BCC、Subject、Date、MIME-Version、Content-Type 等欄位。對非 ASCII 的欄位（如 Subject 或顯示名稱），會根據編碼設定產生 RFC 2047 的 encoded-word。最終透過 HeaderCollection.Set 寫入並驗證字元集合。本文問題是 From 取值來自 MailAddress 的 fullAddress；若其被 ToString 汙染成未編碼字串，Set 會於 IsAnsi 檢查時發現非法字元而拋出例外，整個傳送流程因此中止。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, A-Q8, D-Q1

Q3: HeaderCollection.Set 與 IsAnsi 的機制是什麼？
- A簡: Set 在寫入標頭前檢查值是否僅含合法 ASCII；若否則拋 FormatException「InvalidHeaderValue」。
- A詳: HeaderCollection.Set 負責將給定 name/value 放入集合，並確保 value 符合郵件標頭的語法與字元限制。內部會呼叫 IsAnsi 或等效檢查，確定無非 ASCII 或保留字元。這項檢查可防止非法輸出（如未轉義的 CRLF、非 ASCII 文本）導致 SMTP 協定中斷或安全風險（如 header injection）。當值包含中文時，正確路徑應先做 encoded-word 轉換使其成為 ASCII 安全表示。本文案例因 fullAddress 已被未編碼的 Unicode 汙染，Set 立即拒絕，堆疊顯示為 FormatException，由 SmtpClient 包裝為 SmtpException。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, D-Q1, D-Q8

Q4: MailAddress.ToEncodedString 的原理與組件是什麼？
- A簡: 依 encodedDisplayName 與 Address，透過 MailBnfHelper 組合並對顯示名稱做 RFC 2047 編碼，回傳可放入標頭的 ASCII 字串。
- A詳: ToEncodedString（internal）是 MailAddress 用於產生 RFC 合規輸出的方法。它先檢查 encodedDisplayName 是否可用，必要時將原始 DisplayName 依指定 Encoding 轉為 encoded-word；再使用 MailBnfHelper.GetDotAtomOrQuotedString 處理顯示名稱的語法（加引號或點原子）；最後串接「 <Address>」得到完整標頭片段。此輸出確保通過 HeaderCollection 的 ASCII 檢查。這條路徑才是寄送應走的；但在缺陷版本，ToString 也寫入 fullAddress，讓 ToEncodedString 檢查 fullAddress 已有值而直接重用錯誤字串，造成寄送失敗。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q9, B-Q5, B-Q9

Q5: 為什麼 ToString 的實作會出錯？
- A簡: 它用未編碼的 DisplayName 組字串，且將結果寫入 fullAddress 快取；後續寄送誤用此值。
- A詳: 預期的 ToString 應回傳僅用於顯示的無害字串，且不影響物件狀態。然而缺陷版本在 ToString 中：1) builder.Append('"'); builder.Append(DisplayName); builder.Append("\" <"); builder.Append(Address); builder.Append('>'); 2) 將結果指派給 fullAddress。這樣一來，任何觸發 ToString（包含日誌格式化）都會把未編碼的 Unicode 內容記入快取。寄送流程因優先採用 fullAddress 以避免重複編碼而沿用錯誤值，導致非法標頭。根因是快取邏輯分散於多處且未共用同一產生器，違反單一來源原則。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q10, B-Q13, D-Q10

Q6: .NET 的格式化輸出如何導致呼叫 ToString？
- A簡: string.Format/Console.WriteLine 的複合格式化會呼叫每個參數的 ToString 取得輸出字串。
- A詳: Console.WriteLine("準備寄信 (From: {0})", mail.From) 使用複合格式化。格式化引擎會遍歷引數陣列，依文化特性（IFormatProvider）呼叫每個參數的 ToString() 或 IFormattable.ToString(format, provider)，將結果插入佔位符。這對大多數型別是無害的，但若 ToString 有副作用或錯誤實作，就可能改變物件狀態。本文便是如此：MailAddress.ToString 寫入 fullAddress，導致後續寄送使用錯誤快取。避免方式是僅輸出無副作用屬性（Address/DisplayName）或對敏感型別使用自訂格式化器。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, C-Q2, D-Q2

Q7: 為何主旨正常而 From 出錯？
- A簡: 主旨使用 SubjectEncoding 由另一條正確編碼路徑處理；From 依 MailAddress，受到 ToString 快取污染。
- A詳: 主旨（Subject）由 MailMessage.SubjectEncoding 控制，序列化時呼叫專用的標頭編碼器產生 encoded-word，未受 MailAddress 影響。而 From 則取決於 MailAddress 的序列化結果。當 ToString 寫入未編碼的 fullAddress 後，From 標頭便以此錯值寫入 HeaderCollection，遭到 IsAnsi 檢查拒絕。這種差異源自兩者分屬不同模組與責任範圍，說明在 API 使用上需分別注意。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, D-Q3, B-Q2

Q8: ASCII、ANSI、Unicode 的差異與本案關係？
- A簡: 標頭需求為 ASCII；ANSI 常指單位元組編碼；Unicode 是內部通用字集。未轉為標準 ASCII 表示就會違規。
- A詳: ASCII 是 7-bit 字元集，用於網際傳輸協定的基礎；ANSI 常被泛指單位元組的區域編碼（如 Big5、Windows-1252）；Unicode 是跨語系的統一字集（.NET 使用 UTF-16）。郵件標頭規範要求 ASCII，非 ASCII 內容須透過 encoded-word 映射為 ASCII。本文中，顯示名稱原本是 Unicode（例如「吳小皮」），正確應依指定 Encoding（Big5/UTF-8）轉為 encoded-word；但錯誤實作直接把 Unicode 放入標頭，導致檢查失敗。理解三者關係有助於正確選擇與轉換字元集。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, A-Q7, B-Q15

Q9: Dot-Atom 與 Quoted String 在郵件標頭中的角色？
- A簡: 顯示名稱與地址的語法元素；顯示名稱可能需加雙引號（Quoted String）或被編碼。
- A詳: 郵件地址語法允許「顯示名稱」與「<local-part@domain>」搭配。顯示名稱若包含空白或特殊字元，需使用 Quoted String 以雙引號包裹；純英數與允許符號可用 Dot-Atom 表示。System.Net.Mail 透過 MailBnfHelper.GetDotAtomOrQuotedString 決定使用何者。當顯示名稱包含非 ASCII 時，還需先轉為 encoded-word，之後再套語法。本文中正確路徑會對顯示名稱做編碼與適當引號處理；錯誤 ToString 僅加引號，未做編碼，因而被拒。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q15, A-Q5

Q10: 反組譯 .NET 程式集如何幫助定位此問題？
- A簡: 透過工具（如 Reflector）檢視 System.Net.Mail 的內部實作與呼叫堆疊，找出 ToString 與快取邏輯的缺陷。
- A詳: 當錯誤僅顯示在高階 API 堆疊時，反組譯可揭露內部細節。本文使用反組譯工具檢視 System.Net.Mime.HeaderCollection.Set、System.Net.Mail.Message.PrepareHeaders 與 MailAddress 的 ToEncodedString/ToString 實作，對照堆疊追蹤，鎖定 IsAnsi 檢查點與 fullAddress 的來源，最終發現 ToString 在首次呼叫時寫入未編碼值到 fullAddress。這類分析技巧在封閉源碼環境中特別重要，可區分「你的程式碼」與「框架缺陷」，避免盲目繞路。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q1, A-Q8, B-Q5

Q11: encodedDisplayName 與 DisplayName 有何不同？
- A簡: DisplayName 是原始文字；encodedDisplayName 是依指定編碼轉換後、適合標頭使用的版本。
- A詳: MailAddress 內部維持顯示名稱的兩種表示：DisplayName（原始 Unicode 文字）與 encodedDisplayName（根據建構子指定的 Encoding 轉換後，可能帶有 encoded-word 格式或已轉義處理的版本）。ToEncodedString 會優先使用 encodedDisplayName 來組標頭，確保 ASCII 合規。反之 ToString（缺陷）是以 DisplayName 建構，既未編碼也可能只加引號，導致含有非 ASCII 字元直接出現在輸出。了解兩者差異可幫你在日誌與寄送兩情境分別採取合適的來源。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q4, A-Q9, D-Q2

Q12: 何謂觀察者效應（Heisenbug），本案如何體現？
- A簡: 指為了觀察/除錯而改變系統行為的 bug。本案因日誌呼叫 ToString，改變 MailAddress 狀態而致錯。
- A詳: Heisenbug 是指當你嘗試觀察或除錯時，系統行為跟著改變，使問題難以重現或被誤導。本文中，單純「加印一行」Console.WriteLine 就從正常變成失敗。原因並非時間或併發，而是 ToString 有副作用：汙染 fullAddress 快取。這是觀察介入導致狀態變更的典型案例，也提醒 ToString 應避免副作用；而在撰寫日誌時，對關鍵型別採用保守策略（輸出屬性值），降低此類風險。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, D-Q2, D-Q10

Q13: 為何 fullAddress 快取會造成跨方法污染？
- A簡: 因 ToString 與 ToEncodedString 共用同一快取欄位，彼此覆蓋導致錯誤被放大至寄送流程。
- A詳: 快取策略若跨多個產生路徑共享，且沒明確來源控制，即可能被不相容的來源污染。此例中，ToString 與 ToEncodedString 都檢查 fullAddress 是否有值；ToString 寫入未編碼結果，導致 ToEncodedString 認為已有可用值而不再重算（避免費用重複編碼）。這種跨方法共享快取且缺乏「來源/格式」元資料的設計，破壞了單一責任與可驗證性，使得顯示用路徑誤導了傳輸用路徑。修正策略應是：由單一正確來源產生並快取，不應由 ToString 回填快取。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q5, A-Q10, D-Q10

Q14: IsAnsi(value,false) 以 char<0xFF 為準有何含意？
- A簡: 內部以字元範圍近似檢查「可傳輸」集合；超出範圍（如 CJK）視為非法，須先編碼為 ASCII。
- A詳: 雖規範要求 7-bit ASCII，實作上可能以更寬鬆的 ANSI/Latin-1 切點（<0xFF）做初步篩選，再搭配其他語法檢查。對 .NET 的 char（UTF-16）而言，多數 CJK 字元值遠大於 0xFF，因此會被判為非 ANSI/ASCII。這只是一道護欄：目的在於阻止未經 RFC 2047 編碼的內容進入標頭。真正合規的做法是先經 encoded-word 轉為 ASCII，再通過這類檢查。本文錯誤就是跳過編碼，直接讓 Unicode 值進入，觸發 FormatException。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q3, A-Q11, B-Q15

Q15: 郵件標頭的最終編碼長怎樣（範例）？
- A簡: 形如 From: =?big5?B?...?= <user@example.com>，顯示名稱成為 encoded-word，地址維持 ASCII。
- A詳: 以 Big5/UTF-8 為例，顯示名稱「吳小皮」會先以指定字集轉位元組，再以 Base64 編碼，組成 =?charset?B?base64?=。完整 From 標頭例如：From: =?utf-8?B?5bGx5a6J5bCP?= <peter@chicken-house.net>。收件端會解讀 encoded-word 還原顯示名稱，並以 <...> 中的 ASCII 地址作為實際路由。若顯示名稱僅含 ASCII，encoded-word 可省略。本文的錯誤輸出則是直接產生 "吳小皮" <peter@...>，未經 encoded-word，因此被 HeaderCollection 拒絕。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, A-Q7, B-Q4

### Q&A 類別 C: 實作應用類

Q1: 如何在 C# 安全寄送含中文的 From/To/Subject？
- A簡: 建立 MailAddress 時指定 Encoding，Subject 設 SubjectEncoding；避免呼叫 MailAddress.ToString，直接 Send。
- A詳: 具體步驟與程式碼：
  - 建立編碼器，例如 var enc = Encoding.GetEncoding(950) 或 Encoding.UTF8。
  - 建構寄件者與收件者：new MailAddress("user@example.com", "吳小皮", enc)。
  - 設定主旨與編碼：mail.Subject = "今天天氣很好"; mail.SubjectEncoding = enc。
  - 重要：不要在寄送前對 mail.From 或收件者集合做 ToString 輸出，避免觸發缺陷。
  - 送出：new SmtpClient().Send(mail)。
  程式碼：
  ```
  var enc = Encoding.UTF8;
  var mail = new MailMessage();
  mail.From = new MailAddress("peter@x.com", "吳小皮", enc);
  mail.To.Add(new MailAddress("annie@x.com", "吳小妹", enc));
  mail.Subject = "今天天氣很好";
  mail.SubjectEncoding = enc;
  mail.Body = "內容...";
  new SmtpClient().Send(mail);
  ```
  注意：盡量使用 UTF-8 提升相容性；Big5 適用於特定環境。日誌請參考 C-Q2 的安全作法。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, A-Q7, D-Q1

Q2: 如何安全印出 MailAddress 做日誌而不觸發 Bug？
- A簡: 不用 {0} 直接帶 MailAddress；改以 Address/DisplayName 手動組字串，如 $"{m.DisplayName} <{m.Address}>"。
- A詳: 關鍵是避免呼叫 MailAddress.ToString。建議：
  - 直接輸出屬性：
    ```
    var m = mail.From;
    Console.WriteLine($"準備寄信 From: {m.DisplayName} <{m.Address}>");
    ```
  - 或僅輸出地址：
    ```
    Console.WriteLine($"From: {mail.From.Address}");
    ```
  - 若要可攜的 JSON 日誌：
    ```
    Console.WriteLine(JsonSerializer.Serialize(new { mail.From.DisplayName, mail.From.Address }));
    ```
  - 千萬不要：Console.WriteLine("From: {0}", mail.From);
  這些做法不會寫入 fullAddress，因此不會污染寄送流程。若你想看 RFC 2047 形式，需自行編碼（見 C-Q10），切勿依賴 MailAddress.ToString。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, D-Q2, C-Q5

Q3: 如何寫單元測試重現並捕捉該 Bug？
- A簡: 在寄送前分別呼叫與不呼叫 ToString，預期前者拋 SmtpException/FormatException，後者成功（或模擬）。
- A詳: 測試步驟：
  - Arrange：建立 MailMessage，From/To 使用含中文顯示名稱與指定 Encoding。
  - Act：
    - Case1：不呼叫 ToString，直接呼叫內部序列化方法（可用私有反射或以 SmtpClient.Send 替代，建議以 stub/mock SMTP）。
    - Case2：先 Console.WriteLine($"{mail.From}") 或 $"{mail.From}"，再寄送。
  - Assert：
    - Case1 不拋出 FormatException。
    - Case2 捕捉到 SmtpException 內含 InnerException 為 FormatException，訊息包含「InvalidHeaderValue」。
  代碼要點：用 Fake SMTP（如本機接收器）避免真寄；或使用 try/catch 驗證例外型別與訊息。此測試可防回歸並教育團隊避免在日誌中使用 ToString。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q1, A-Q8, B-Q2

Q4: 想在日誌中看到「編碼後的」From，該怎麼做？
- A簡: 不能靠 ToString；自行依 RFC 2047 產生 encoded-word，再組成 "=?charset?B?…?= <addr>"。
- A詳: 你可自行產生 encoded-word 供日誌觀察，避免影響 MailAddress 狀態：
  ```
  static string EncodeWord(string text, Encoding enc) {
      var bytes = enc.GetBytes(text);
      var b64 = Convert.ToBase64String(bytes);
      return $"=?{enc.WebName}?B?{b64}?=";
  }
  static string EncodeHeaderAddress(MailAddress m, Encoding enc) {
      var name = string.IsNullOrEmpty(m.DisplayName)
          ? ""
          : EncodeWord(m.DisplayName, enc) + " ";
      return $"{name}<{m.Address}>";
  }
  Console.WriteLine(EncodeHeaderAddress(mail.From, Encoding.UTF8));
  ```
  這純粹用於觀察，不回寫 MailAddress。注意：完整 RFC 2047 還有長度換行與字界處理，簡版足供大多數日誌用途。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q15, A-Q5, C-Q2

Q5: 如何做一個 SafeFullAddress 擴充方法？
- A簡: 回傳 $"{DisplayName} <{Address}>"，不呼叫 ToString，也不改變物件狀態。
- A詳: 擴充方法可統一團隊用法，避免踩雷：
  ```
  public static class MailAddressExtensions {
      public static string SafeFullAddress(this MailAddress m) {
          if (m == null) return "";
          return string.IsNullOrEmpty(m.DisplayName)
            ? m.Address
            : $"{m.DisplayName} <{m.Address}>";
      }
  }
  // 使用
  Console.WriteLine($"From: {mail.From.SafeFullAddress()}");
  ```
  原則：僅讀屬性、不可呼叫 ToString、不做任何回寫快取的操作。若需 RFC 2047 形式，改用 C-Q4 的編碼器，並清楚標示僅供日誌觀察。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, A-Q12, D-Q10

Q6: 如果已誤觸 ToString，如何在寄送前修復？
- A簡: 重新建立 MailAddress 指派回 From/To，或重建整個 MailMessage，確保 fullAddress 不含錯值。
- A詳: 兩種修復：
  - 重建 From：
    ```
    var old = mail.From;
    mail.From = new MailAddress(old.Address, old.DisplayName, Encoding.UTF8);
    ```
  - 重建所有收件者（迭代 To/CC/BCC 以同法重建）。
  - 或重建 MailMessage（保險但較麻煩）。
  原理：新的 MailAddress 物件未被 ToString 汙染。之後避免再調用 ToString。也可在寄送前做自檢：檢查是否包含非 ASCII 而未含 "=?...?" 模式，若是則強制重建。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, D-Q1, D-Q7

Q7: 如何攔截並記錄 SmtpException/FormatException 以利除錯？
- A簡: try/catch 捕捉 SmtpException，列印 InnerException、堆疊與 From 標頭相關欄位（用安全輸出）以定位問題。
- A詳: 範例：
  ```
  try {
      new SmtpClient().Send(mail);
  } catch (SmtpException ex) {
      Console.Error.WriteLine($"SMTP: {ex.Message}");
      if (ex.InnerException != null)
          Console.Error.WriteLine($"Inner: {ex.InnerException}");
      Console.Error.WriteLine($"From: {mail.From.Address} / {mail.From.DisplayName}");
      // 可加印 SubjectEncoding、使用的 Encoding
  }
  ```
  注意：不要在 catch 中再呼叫 mail.From.ToString。將例外與關鍵欄位（From/To/Subject 的編碼設定）寫入日誌，有助識別是否為 InvalidHeaderValue。若可控制環境，開啟 System.Net tracing（見 C-Q8）觀察更底層行為。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: D-Q1, C-Q2, C-Q8

Q8: 如何開啟 System.Net 追蹤以觀察 SMTP 與郵件序列化？
- A簡: 在 app.config 啟用 System.Net traceSource 與 network logging，輸出到檔案或主控台。
- A詳: app.config 片段：
  ```
  <configuration>
    <system.diagnostics>
      <sources>
        <source name="System.Net" switchValue="Verbose">
          <listeners>
            <add name="net" type="System.Diagnostics.TextWriterTraceListener" initializeData="net.log"/>
          </listeners>
        </source>
      </sources>
      <trace autoflush="true"/>
    </system.diagnostics>
  </configuration>
  ```
  這會記錄連線、命令與例外。配合應用層日誌（勿呼叫 ToString），可對照出錯前的內部路徑與堆疊。注意：標頭內容可能包含敏感資訊，應在安全環境使用並妥善保護日誌。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, D-Q1, C-Q7

Q9: 若想避免框架風險，如何改用 MailKit/MimeKit 寄信？
- A簡: 使用 MimeKit 建構 MIME 訊息與 MailKit SmtpClient 寄送，對多語系支援成熟且維護活躍。
- A詳: 範例：
  ```
  var msg = new MimeKit.MimeMessage();
  msg.From.Add(new MimeKit.MailboxAddress("吳小皮", "peter@x.com"));
  msg.To.Add(new MimeKit.MailboxAddress("吳小妹", "annie@x.com"));
  msg.Subject = "今天天氣很好";
  msg.Body = new MimeKit.TextPart("plain") { Text = "內容..." };
  using var client = new MailKit.Net.Smtp.SmtpClient();
  client.Connect("smtp.example.com", 587, MailKit.Security.SecureSocketOptions.StartTls);
  client.Authenticate("user", "pass");
  client.Send(msg);
  client.Disconnect(true);
  ```
  MailKit 對標頭編碼、折行與 RFC 細節處理完整，避免歷史版本框架的坑。遷移時仍需正確處理日誌，避免 ToString 類副作用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q15, D-Q6

Q10: 如何自製 RFC 2047 encoded-word 編碼器（簡版）？
- A簡: 以指定 Encoding 取位元組，Base64 後包成「=?charset?B?...?=」，供日誌觀察。
- A詳: 代碼：
  ```
  static string EncodeWord(string text, Encoding enc) {
      if (string.IsNullOrEmpty(text)) return text;
      var b64 = Convert.ToBase64String(enc.GetBytes(text));
      return $"=?{enc.WebName}?B?{b64}?=";
  }
  static string EncodeHeader(string name, string value, Encoding enc) {
      return $"{name}: {EncodeWord(value, enc)}";
  }
  Console.WriteLine(EncodeHeader("Subject", "今天天氣很好", Encoding.UTF8));
  ```
  注意事項：
  - 僅供日誌或教學；生產環境需處理長度限制（76 字元換行）、字界切割與多段 encoded-word。
  - 對 From/To 應組合「encoded-word <address>」格式（見 C-Q4）。
  - 不要嘗試回寫到 MailAddress，以免與框架行為衝突。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q15, A-Q5, C-Q4

### Q&A 類別 D: 問題解決類

Q1: 遇到「SmtpException: 傳送郵件失敗」與「FormatException: InvalidHeaderValue」，怎麼辦？
- A簡: 檢查是否在寄送前呼叫了 MailAddress.ToString；改用屬性輸出或重建 MailAddress，確認編碼設定正確。
- A詳: 症狀：寄送立即失敗，堆疊包含 System.Net.Mime.HeaderCollection.Set 與 Message.PrepareHeaders，InnerException 為 FormatException: InvalidHeaderValue。可能原因：
  - 標頭含非 ASCII 但未編碼（多見於 From/To 顯示名稱）。
  - 誤觸 MailAddress.ToString 汙染 fullAddress。
  解法：
  - 搜尋格式化輸出，移除 "{0}" 帶 MailAddress 的用法，改輸出 Address/DisplayName。
  - 若已呼叫過 ToString，於寄送前重建 MailAddress（見 C-Q6）。
  - 確認 SubjectEncoding/顯示名稱 Encoding 設定。
  預防：
  - 寫靜態分析或 code review 規範，禁止對 MailAddress 呼叫 ToString。
  - 單元測試覆蓋含非 ASCII 的情境。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, C-Q7, D-Q5

Q2: 為何加入 Console.WriteLine 後才失敗？如何診斷？
- A簡: 因它呼叫 ToString，改變 MailAddress 狀態；以安全輸出替代並比較前後行為，即可驗證。
- A詳: 診斷步驟：
  - 比對兩版程式：唯一差異是 Console.WriteLine("...", mail.From)。
  - 在該行改成輸出 mail.From.Address 或 DisplayName，若恢復正常則證實是 ToString 副作用。
  - 於例外處列印 InnerException 與堆疊，觀察 HeaderCollection.Set。
  - 適用的修復：移除 ToString；或重建 MailAddress 後再寄。
  原因機制與詳細說明見 A-Q12、B-Q6。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, B-Q6, C-Q2

Q3: 中文主旨正常但 From 出錯，可能原因？
- A簡: 主旨經 SubjectEncoding 正確編碼；From 來自 MailAddress 被 ToString 汙染為未編碼值。
- A詳: 現象差異來自編碼責任不同。主旨的 encoded-word 由 SubjectEncoding 控制，與 MailAddress 無關；From 需依 MailAddress 的序列化結果。若在寄送前呼叫 ToString，fullAddress 被置換為未編碼字串，使 From 被拒。檢查與修復：檢視日誌輸出、移除 ToString、重建 From，確保建構 MailAddress 時有指定 Encoding。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q7, C-Q6

Q4: 收到端顯示亂碼或寄送失敗，如何區分是標頭還是內文問題？
- A簡: 若拋 InvalidHeaderValue 多為標頭；內文亂碼不致拋此例外，通常是 Content-Type/Encoding 設定問題。
- A詳: 判斷步驟：
  - 有無例外：若 SmtpException 包 FormatException: InvalidHeaderValue，多半是標頭非法（From/To/Subject）。
  - 無例外但亂碼：檢查 Content-Type、BodyEncoding、Content-Transfer-Encoding（內文）。
  - 檢視原始郵件（.eml）：觀察 From/Subject 是否為「=?charset?...?=」；內文是否宣告正確 charset。
  - 針對本文場景，重點在 From 未經 encoded-word 導致拒絕；主旨正常代表內文與主旨設定可能已正確。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, A-Q4, D-Q5

Q5: 如何快速找出哪個標頭含非法字元？
- A簡: 最小化測試：僅保留 From/To/Subject/Body，逐一移除或改為 ASCII，二分法定位問題欄位。
- A詳: 步驟：
  - 建立最小訊息：一個收件者、簡單主旨與本文。
  - 將 Subject 設為 ASCII 測試；若仍錯，將 From DisplayName 改為 ASCII；再測。
  - 若改為 ASCII 後可寄，則顯示名稱編碼路徑有問題（多半是 ToString）。
  - 若 From/To 都 ASCII 仍失敗，檢查自訂標頭（Headers）是否含非 ASCII。
  - 透過 try/catch 記錄內層例外訊息佐證。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, C-Q7, B-Q3

Q6: 無法升級 .NET 時，如何預防此 Bug？
- A簡: 規定不呼叫 MailAddress.ToString；以擴充方法輸出；寄送前重建 MailAddress；加單元測試防回歸。
- A詳: 預防措施：
  - 程式碼規範：禁止 ToString 用於 MailAddress；提供 SafeFullAddress（C-Q5）。
  - 日誌檢視：固定輸出 Address/DisplayName，而非物件本身。
  - 防呆：寄送前重建 From/To（尤其在除錯模式或特定旗標開啟時）。
  - 測試：加入含非 ASCII 的 E2E 測試；CI 檢查。
  - 文件化：在開發指南中記錄此歷史缺陷與替代作法。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q5, C-Q6, D-Q10

Q7: 第三方框架強制呼叫 ToString，如何繞開？
- A簡: 傳入包裝型別或字串，避免讓框架拿到 MailAddress；或在最後一刻才設定 MailMessage。
- A詳: 策略：
  - 不把 MailAddress 暴露給會日誌化的框架；改傳入自訂 DTO（含 Address/DisplayName），由你控制輸出。
  - 延遲設定：先在本地組好資料，待框架處理完後才建立 MailMessage 並寄送。
  - 寄送前重建 MailAddress，確保 fullAddress 乾淨。
  - 若框架會反射列舉屬性，也要確保不會因 ToString 被呼叫（可封裝為 string）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q6, D-Q10, A-Q12

Q8: 沒呼叫 ToString 仍拋 InvalidHeaderValue，可能還有哪些原因？
- A簡: 顯示名稱含 CR/LF 或控制字元、注入攻擊、手動加入自訂標頭含非 ASCII 或格式錯誤。
- A詳: 檢查清單：
  - 顯示名稱是否含換行、制表或控制字元（需移除或轉義）。
  - 自訂 Headers 是否加入非 ASCII 未經編碼的值。
  - 是否誤用 addr-spec 語法（多餘的引號、逗號等）。
  - 是否有 header injection（如 "\r\nBcc:"）。
  - 嘗試將顯示名稱清洗為僅可見字元再測試；或完全移除自訂標頭驗證。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, D-Q5, A-Q4

Q9: 如何提升跨語系郵件相容性？
- A簡: 優先使用 UTF-8、避免未編碼的非 ASCII、加強測試樣本、檢視收發雙方客戶端支援。
- A詳: 實務建議：
  - 選擇 UTF-8 做為主體與標頭的首選編碼。
  - 嚴禁未經 RFC 2047 的非 ASCII 進入標頭。
  - 自動化測試涵蓋 CJK、重音字母、表情符號等樣本。
  - 對長標頭做合規折行（encoded-word 分段）。
  - 確認收發端（郵件伺服器與客戶端）對 UTF-8 標頭的支援。
  - 以替代函式庫（如 MailKit）降低歷史缺陷風險。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, A-Q5, C-Q9

Q10: 如何在 Code Review 中避免此類副作用問題？
- A簡: 檢查 ToString 的使用、日誌對象、不可變性原則與快取來源一致性；加入規範與檢查清單。
- A詳: 實務做法：
  - 建立規範：對敏感型別（MailAddress、HttpRequest 等）禁止 ToString 用於日誌。
  - 使用擴充方法/包裝類提供「安全輸出」。
  - 檢查不可變性：ToString 不應回寫狀態；快取應由單一路徑產生。
  - 在 PR 模板加入「日誌是否可能改變行為？」的核對項。
  - 設計單元測試覆蓋非 ASCII 與日誌混入情境。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, B-Q13, C-Q5

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 System.Net.Mail？
    - A-Q2: 什麼是 MailMessage？
    - A-Q3: 什麼是 MailAddress？
    - A-Q4: 為什麼郵件標頭必須是 ASCII？為什麼需要編碼？
    - A-Q5: 什麼是 MIME 標頭的 encoded-word（RFC 2047）？
    - A-Q6: SubjectEncoding 與 MailAddress 顯示名稱編碼有何差異？
    - A-Q7: Encoding.GetEncoding(950) 是什麼？為何使用？
    - A-Q12: 為什麼一行 Console.WriteLine 就讓程式壞掉？
    - B-Q1: System.Net.Mail 寄信的主要流程為何？
    - B-Q6: .NET 的格式化輸出如何導致呼叫 ToString？
    - C-Q1: 如何在 C# 安全寄送含中文的 From/To/Subject？
    - C-Q2: 如何安全印出 MailAddress 做日誌而不觸發 Bug？
    - D-Q1: 遇到「SmtpException: 傳送郵件失敗」與「FormatException: InvalidHeaderValue」，怎麼辦？
    - D-Q2: 為何加入 Console.WriteLine 後才失敗？如何診斷？
    - A-Q15: 這個案例的核心啟示是什麼？

- 中級者：建議學習哪 20 題
    - A-Q8: 文中揭露的 Bug 是什麼？
    - A-Q9: MailAddress.ToString 與 ToEncodedString 有何差異？
    - A-Q10: 什麼是 fullAddress 快取？為何會出問題？
    - A-Q11: 什麼是 IsAnsi 檢查？與錯誤有何關係？
    - B-Q2: SmtpClient.Send 如何準備郵件標頭？
    - B-Q3: HeaderCollection.Set 與 IsAnsi 的機制是什麼？
    - B-Q4: MailAddress.ToEncodedString 的原理與組件是什麼？
    - B-Q5: 為什麼 ToString 的實作會出錯？
    - B-Q7: 為何主旨正常而 From 出錯？
    - B-Q9: Dot-Atom 與 Quoted String 在郵件標頭中的角色？
    - B-Q10: 反組譯 .NET 程式集如何幫助定位此問題？
    - C-Q3: 如何寫單元測試重現並捕捉該 Bug？
    - C-Q4: 想在日誌中看到「編碼後的」From，該怎麼做？
    - C-Q5: 如何做一個 SafeFullAddress 擴充方法？
    - C-Q6: 如果已誤觸 ToString，如何在寄送前修復？
    - C-Q8: 如何開啟 System.Net 追蹤以觀察 SMTP 與郵件序列化？
    - D-Q3: 中文主旨正常但 From 出錯，可能原因？
    - D-Q5: 如何快速找出哪個標頭含非法字元？
    - D-Q6: 無法升級 .NET 時，如何預防此 Bug？
    - D-Q10: 如何在 Code Review 中避免此類副作用問題？

- 高級者：建議關注哪 15 題
    - B-Q4: MailAddress.ToEncodedString 的原理與組件是什麼？
    - B-Q5: 為什麼 ToString 的實作會出錯？
    - B-Q11: encodedDisplayName 與 DisplayName 有何不同？
    - B-Q13: 為何 fullAddress 快取會造成跨方法污染？
    - B-Q14: IsAnsi(value,false) 以 char<0xFF 為準有何含意？
    - B-Q15: 郵件標頭的最終編碼長怎樣（範例）？
    - C-Q4: 想在日誌中看到「編碼後的」From，該怎麼做？
    - C-Q10: 如何自製 RFC 2047 encoded-word 編碼器（簡版）？
    - D-Q4: 收到端顯示亂碼或寄送失敗，如何區分是標頭還是內文問題？
    - D-Q7: 第三方框架強制呼叫 ToString，如何繞開？
    - D-Q8: 沒呼叫 ToString 仍拋 InvalidHeaderValue，可能還有哪些原因？
    - A-Q14: 為什麼說這是「忽略亞洲語系需求」的例子？
    - C-Q9: 若想避免框架風險，如何改用 MailKit/MimeKit 寄信？
    - D-Q9: 如何提升跨語系郵件相容性？
    - A-Q13: 這個問題與作業系統或語系設定有關嗎？