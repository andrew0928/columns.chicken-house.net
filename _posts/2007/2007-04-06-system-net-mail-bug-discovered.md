---
layout: post
title: "原來 System.Net.Mail 也會有 Bug ..."
categories:

tags: [".NET","Tips","技術隨筆"]
published: true
comments: true
redirect_from:
  - /2007/04/06/system-net-mail-bug-discovered/
  - /columns/post/2007/04/06/e58e9fe4be86-SystemNetMail-e4b99fe69c83e69c89-Bug-.aspx/
  - /post/2007/04/06/e58e9fe4be86-SystemNetMail-e4b99fe69c83e69c89-Bug-.aspx/
  - /post/e58e9fe4be86-SystemNetMail-e4b99fe69c83e69c89-Bug-.aspx/
  - /columns/2007/04/06/e58e9fe4be86-SystemNetMail-e4b99fe69c83e69c89-Bug-.aspx/
  - /columns/e58e9fe4be86-SystemNetMail-e4b99fe69c83e69c89-Bug-.aspx/
  - /blogs/chicken/archive/2007/04/06/2328.aspx/
wordpress_postid: 169
---

果然老外寫的程式, 就是容易忽略掉亞洲語系的需求... 為了這個 Bug, 足足浪費我兩天的時間 [:@], 既然糾出來了, 當然要講一下... 先來看這段 sample code:

```csharp
MailMessage mail = new MailMessage();
Encoding chtEnc = Encoding.GetEncoding(950);
mail.From = new MailAddress("peter@chicken-house.net", "吳小皮", chtEnc);
mail.To.Add(new MailAddress("annie@chicken-house.net", "吳小妹", chtEnc));
mail.Subject = "今天天氣很好";
mail.SubjectEncoding = chtEnc;
mail.Body = "blah blah blah...";
(new SmtpClient()).Send(mail);
```

嗯, 執行的很好, 收的到 MAIL, 編碼也沒問題. 不過沒有回應的 code 總是不大 friendly, 加印一行 message 看看...

```csharp
MailMessage mail = new MailMessage();
Encoding chtEnc = Encoding.GetEncoding(950);
mail.From = new MailAddress("peter@chicken-house.net", "吳小皮", chtEnc);
mail.To.Add(new MailAddress("annie@chicken-house.net", "吳小妹", chtEnc));
mail.Subject = "今天天氣很好";
mail.SubjectEncoding = chtEnc;
mail.Body = "blah blah blah...";
Console.WriteLine("準備寄信 (From: {0})", mail.From);
(new SmtpClient()).Send(mail);
```

My God !!! 啥米, 這樣就錯? 而且錯的地方讓我丈二金剛摸不著頭腦... 執行的環境試過 XP, 2003, Vista, 中英文版, 都有 windows update 更新所有的 patch, 除了訊息有中英文版不同之外, 錯誤通通一樣, Exception Dump 如下:

> ```
> 準備寄信(From: "吳小皮")未處理的例外狀況: System.Net.Mail.SmtpException: 
> 傳送郵件失敗。	--->System.FormatException: 
> 標頭值中找到無效的字元。	
> 於 System.Net.Mime.HeaderCollection.Set(String name, String value)   
>     於 System.Net.Mail.Message.PrepareHeaders(Boolean sendEnvelope)   
>     於 System.Net.Mail.Message.Send(BaseWriter writer, Boolean sendEnvelope)   
>     於 System.Net.Mail.SmtpClient.Send(MailMessage message)
>     -- - 內部例外狀況堆疊追蹤的結尾-- - 
>     於 System.Net.Mail.SmtpClient.Send(MailMessage message)   
>     於 Program.Main()
> ```

真是它ㄨㄨㄨ的, 怎麼會這樣? 我實際的情況比較慘, 是加了一堆 Console.WriteLine( ) 後才突然發現有問題, 跟本搞不清楚怎麼回事... 試到最後, 確定加了 Console.WriteLine( ) 會有問題, 問題是, 這行到底有什麼了不起的? 不過就是 mail.Form.ToString() ... [:|]

決定繼續挖下去, 先從 Exception 開始查. 前面有一大堆不好追的就跳過去了, 從 dump 的 call stack, 再用 Refactor 去反組譯 .net 的 assembly, 最後這裡看起來最像是 Exception 的源頭:

> class: System.Net.Mime.HeaderCollection  
> method: public override void Set(string name, string value)

截錄片段 source code:

```csharp
if (!MimeBasePart.IsAnsi(value, false))
{
    throw new FormatException(SR.GetString("InvalidHeaderValue"));
}
```

怎麼看都沒問題, 追過 IsAnsi( ), 裡面沒啥特別的 code, 就 char 的值小於 0xff 就判定 pass. 所以問題應該出在 value 的值送進來判定時就已經有問題了... 再往上追, value 的源頭是 MailAddress 物件的 .ToEncodedString( ) 來的:

class: System.Net.Mail.MailAddress

```csharp
internal string ToEncodedString()
{
    if (this.fullAddress == null)
    {
        if ((this.encodedDisplayName != null) && (this.encodedDisplayName != string.Empty))
        {
            StringBuilder builder = new StringBuilder();
            MailBnfHelper.GetDotAtomOrQuotedString(this.encodedDisplayName, builder);
            builder.Append(" <");
            builder.Append(this.Address);
            builder.Append('>');
            this.fullAddress = builder.ToString();
        }
        else
        {
            this.fullAddress = this.Address;
        }
    }
    return this.fullAddress;
}
```

然後跟加了就會出問題的 ToString( ) 比對著看:

```csharp
public override string ToString()
{
    if (this.fullAddress == null)
    {
        if ((this.encodedDisplayName != null) && (this.encodedDisplayName != string.Empty))
        {
            StringBuilder builder = new StringBuilder();
            builder.Append('"');
            builder.Append(this.DisplayName);
            builder.Append("\" <");
            builder.Append(this.Address);
            builder.Append('>');
            this.fullAddress = builder.ToString();
        }
        else
        {
            this.fullAddress = this.Address;
        }
    }
    return this.fullAddress;
}
```

Ouch, 真是想罵人, 問題就在這裡... 看起來是 Microsoft 工程師為了避開重複作編碼的動作, 每次呼叫 ToEncodedString( ) 及 ToString( ) 時都會去看看 fullAddress 這個 private field 是否有值? 有的話代表之前已經作過編碼了, 就直接撿現成. 問題出在第一次呼叫時, 編碼的動作在 ToString( ) 及 ToEncodedString( ) 各寫了一次 (果然沒有做好 refactoring ... 哈哈), 結果 ToString( ) 的這份 code implementation 是錯的, 跟本沒編碼 [:@] ... 我沒事雞婆在寄信前呼叫 ToString( ) 印 Messabe 算我運氣背, 就碰到這個 Bug.. [:@]

花了近兩天, 不過最後有找到 Bug, 而且還是 Microsoft 的 Bug, 哈哈, 總算證明人不是我殺的 [:D], submit Microsoft 的 Bug 有獎金嘛? 不只 Bug, 連問題都找到了... 有的話通知一下 [:D]
