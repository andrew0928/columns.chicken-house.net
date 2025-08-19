---
layout: post
title: "[設計案例]  授權碼 如何實作?  #3, 數位簽章"
categories:
- "設計案例: 授權碼 如何實作?"
tags: [".NET","ASP.NET","C#","專欄","技術隨筆","物件導向"]
published: true
comments: true
permalink: "/2016/02/24/casestudy_license_03_digital_signature/"
redirect_from:
wordpress_postid: 871
---

![](/wp-content/uploads/2014/04/shutterstock_160680575-Certified-Stamp-Small1.jpg)

## 資料的封條: 數位簽章 原理說明

這裡最關鍵的就是軟體該如何確認 "這份資料是否是原廠提供，而非第三者偽造的假資料?" 這個問題。這類安全問題，最忌諱的就是讓一些搞不清楚狀況的工程師自己土炮一堆怪怪的 "加密" 方式，試圖混淆內容讓別人認不出來。這是很危險的，因為你靠的是 "演算法" 來保護資料，而不是靠 "金鑰" 來保護。如果你靠的是別人不知道你怎麼加密的，那麼將來這份程式碼你敢 Open Source 嗎? 你能不讓你的團隊其他成員 REVIEW 你的 CODE 嗎? 既然 CODE 不是絕對保密的，那麼你如何能證明你的資料是絕對安全的? 所以，比較可靠的方式，還是要靠那麼多人對密碼學的研究，用公開的演算法 + 只有你才擁有的金鑰，來保護你的資料才是上策。也因為這樣，請盡可能的採用廣為流通的加密方式及涵式庫。

<!--more-->

---

**[設計案例] "授權碼" 如何實作? 2016/02 (本篇系列文章)**

#1. [需求與問題](/2016/02/17/casestudy_license_01_requirement/)

#2. [授權碼序列化](/2016/02/24/casestudy_license_02_serialization/)

#3. [數位簽章](/2016/02/24/casestudy_license_03_digital_signature/)

#3. [(補) - 金鑰的保護](/2016/03/19/casestudy_license_03_appendix_key_management/)

---

講到這裡，要保護授權碼這類的資訊，熟悉資訊安全技術的人一定會聯想到 "數位簽章"。數位簽章就像真正的簽章一樣，每個人的簽名都被視為獨一無二，無法仿造的。只要看到我簽過名的文件，就代表是我同意的內容，而且還具有法律效力，同樣的數位簽章也有一樣的目的。

數位簽章的原理我就不在這邊班門弄斧了，我也只是略知一二而已 XD，我貼 wiki 的 [數位簽章](https://zh.wikipedia.org/wiki/%E6%95%B8%E4%BD%8D%E7%B0%BD%E7%AB%A0) 說明片段:

> **數位簽章**（又稱**公鑰數位簽章**）是一種類似寫在[紙](https://zh.wikipedia.org/wiki/%E7%BA%B8)上的普通的物理[簽名](https://zh.wikipedia.org/wiki/%E7%AD%BE%E5%90%8D)，但是使用了[公鑰加密](https://zh.wikipedia.org/wiki/%E5%85%AC%E9%92%A5%E5%8A%A0%E5%AF%86)領域的技術實現，用於鑑別數位信息的方法。一套數位簽章通常定義兩種互補的運算，一個用於簽名，另一個用於驗證，但法條中的電子簽章與數位簽章，代表之意義並不相同，電子簽章用以辨識及確認電子文件簽署人身分、資格及電子文件真偽者。而數位簽章則是以數學演算法或其他方式運算對其加密，才形成電子簽章，意即使用數位簽章才創造出電子簽章。

這裡我順帶說明一下，加密技術通常是先有專家研究出夠安全的演算法 (演算法及程式碼都是公開的)，搭配只有自己才知道的金鑰 (key) 作為參數，就可以將原始資料 (明文, plaintext) 計算出一段加密過的結果 (密文, ciphertext)，只有持有正確的金鑰才能解讀。沒有正確的金鑰想破解，那只能用暴力法去計算。只要你的金鑰強度夠強，個人的力量要靠暴力法破解，那幾乎是不可能的。

加密技術大概分兩大類，對稱式及非對稱式加密。簡單的說，加密用的金鑰, 跟解密用的金鑰是同一個，就是對稱式的演算法，不一樣的就是非對稱式。這次我用的是 [RSA 加密演算法](https://zh.wikipedia.org/wiki/RSA%E5%8A%A0%E5%AF%86%E6%BC%94%E7%AE%97%E6%B3%95)，典型的非對稱式加密技術。他的金鑰是一對的，一個只能你自己留著私鑰 (private key)，另一個你可以任意公開給別人的公鑰 (public key)。當你用私鑰加密過的資料，別人只能拿你的公鑰才能成功解開。

別小看這個技術，他能應用的地方可多了，我舉幾種情境:

1. ![電影: 模仿遊戲](https://upload.wikimedia.org/wikipedia/zh/a/a1/The_Imitation_Game.jpg)

   **在不安全的管道，從事一對多的安全通訊:**
   電影 "模仿遊戲" 裡演的德軍密碼機 "ENIGMA"，其實就可以算是對稱式加密了。德軍的密碼官都有本 code book, 每天換密碼，只要你有正確的組態，加上一台 ENGIMA，你就可以把軍令打進去，會自動被轉成密文透過不安全的無線電傳送。在戰場的另一頭，友軍就可以從廣播接收到訊息，並且用有同樣設定的 ENIGMA 解碼。電影情節我想看過的人都知道了，沒有正確的組態情況下，圖靈的團隊可是吃盡苦頭才掌握到破解的關鍵。

2. **在不安全的管道，從事一對一的安全通訊:**
   如果你要通訊的對象只有一個 (A -> B)，用非對稱式加密就可以輕鬆辦到。A 拿自己的 private key + B 的 public key，把資料加密，傳送給 B。B 接到後再用 A 的 public key + B 的 private key，就可以順利的解開密文。整個過程中，暴露在外的只有三個部分: 加密過的密文、A 的 public key、B 的 public key。這些都是可以放心在外傳遞的，沒有 A 的 private key, 是沒有辦法仿造 A 的身分發文的，沒有 B 的 private key，是沒有辦法解開這密文的。

3. **證明資料的來源是我本人，且未經破壞或修改:**
   這就是數位簽章。先取得整份資料的 Hash (雜湊值)，再用我的 private key 來加密 Hash，加密後的密文就是所謂的數位簽章 (digital signature)。我只要把這簽章跟原始的資料打包放在一起，供人任意取用，收到這份資料的人若想確認資料是不是我送出來的，只要同樣拿原始資料 (明文) 計算一次 Hash, 同時用我的 public key 把 signature 解密，可以拿到另一份被還原的 Hash, 這兩份 Hash 逐一比對，如果結果一模一樣，那就證明資料是出自我手中，可以放心閱讀。

## 實作說明: 數位簽章 + 授權碼 實作

這次我就是拿 RSA 的數位簽章技術，來做網站的授權機制。主要是靠數位簽章的技術來驗證授權碼是不是由原廠發出來的? 如果確認無誤，剩下的就是授權碼決定要開給客戶用那些功能就開。

我只要先編輯好一份設定檔 (不論格式是 XML、JSON、或是其他自訂格式都可)，把設定檔附上數位簽章，放到網站的 configuration 裡。網站在啟動執行時，先驗證一次簽章是否正確，通過驗證網站就可以放心按照授權碼的指示啟用網站! 這樣的做法簡單又有效，不用像以前一樣擔心序號被盜用或是破解。整個程式運作的流程，我簡單畫下來，大概像這樣:

![](/wp-content/uploads/2016/02/img_56c49acfd56e7.png)

實作的部分，其實前面都貼過了。其實這種加解密的演算法，金鑰的管理是很重要的基礎。正規的方式是透過 OS 提供的 [Key Container](https://blogs.msdn.microsoft.com/alejacma/2007/12/13/key-containers-basics/) 來管理，KEY 的產生及散布就透過 CA 來進行。金鑰放在 Key Container 有各種防護機制，我這邊的 Sample Code 為了便於 DEMO，沒有把這段列入考慮，暫時用指定的目錄，或是自行匯入 RSACryptoService XML 來替代。切記! 實際環境下這樣是很不安全的作法，金鑰沒保護好，別人也不用破解了，看完這篇文章就知道怎麼破解了，連駭客都不用找...

這邊回頭來補充說明一下，TokenHelper.Init( ) 到底做了什麼事，這部分是整個安全系統的起點。再來看一次 Init 的部分。這邊提供兩種 Init 的作法，你可以指定存放金鑰的目錄，或是自己將金鑰的 XML 逐一指定:

```csharp
private static string _CurrentSiteID = null;
private static RSACryptoServiceProvider _CurrentRSACSP = null;
private static Dictionary<string, RSACryptoServiceProvider> _PublicKeyStoreDict = null;
private static HashAlgorithm _HALG = new SHA256CryptoServiceProvider();

/// <summary>
/// 初始化，呼叫其他 static method 前必須先正確的執行初始化動作。
/// siteID 的 KeyXML 必須包含 private info
/// </summary>
/// <param name="siteID">目前環境的 Site ID</param>
/// <param name="keyDIR">存放 KEY xml 的磁碟目錄</param>
public static void Init(string siteID, string siteKeyFile, string keyDIR)
{
    // ToDo: 改成使用 key container
    if (string.IsNullOrEmpty(keyDIR) == true || Directory.Exists(keyDIR) == false)
    {
        keyDIR = @"D:\KEYDIR";
        if (Directory.Exists(keyDIR) == false) Directory.CreateDirectory(keyDIR);
    }

    Dictionary<string, string> _xmldict = new Dictionary<string, string>();
    foreach (string file in Directory.GetFiles(keyDIR, "*.xml", SearchOption.TopDirectoryOnly))
    {
        _xmldict.Add(
            Path.GetFileNameWithoutExtension(file),
            File.ReadAllText(file));
    }

    Init(
        siteID, 
        (File.Exists(siteKeyFile))?(File.ReadAllText(siteKeyFile)):(null),
        _xmldict);
}

/// <summary>
/// 初始化，呼叫其他 static method 前必須先正確的執行初始化動作。
/// siteID 的 KeyXML 必須包含 private info
/// </summary>
/// <param name="siteID">目前環境的 Site ID</param>
/// <param name="keyXmlDict">包含所有 site 的 key xml dictionary</param>
public static void Init(string siteID, string siteKeyXml, Dictionary<string, string> keyXmlDict)
{
    Dictionary<string, RSACryptoServiceProvider> _tempKeyStoreDict = new Dictionary<string, RSACryptoServiceProvider>();
    foreach(string site in keyXmlDict.Keys)
    {
        RSACryptoServiceProvider rsa = new RSACryptoServiceProvider();
        rsa.FromXmlString(keyXmlDict[site]);
        _tempKeyStoreDict.Add(site, rsa);
    }

    //if (_tempKeyStoreDict.ContainsKey(siteID) == false) throw new ArgumentException("siteID(" + siteID + ") not found");
    //if (_tempKeyStoreDict[siteID].PublicOnly == true) throw new ArgumentException("must include private key");

    _CurrentSiteID = siteID;
    if (string.IsNullOrEmpty(siteKeyXml) == false)
    {
        _CurrentRSACSP = new RSACryptoServiceProvider();
        _CurrentRSACSP.FromXmlString(siteKeyXml);
    }
    _PublicKeyStoreDict = _tempKeyStoreDict;
}
```

我把相關的 static field 也一起列出來了。我用了 Dictionary<string, RSACryptoServiceProvider> 當作簡易的 KEY store cache, 目的有兩個，一個是儲存自己 SITE 本身的 private key, 另一個是儲存其他友站 (可能會 access 到的其他站台) 的 public key。自身的 private key 沒甚麼問題，其他人的 public key，若可以的話也可以從 CA 取得，不一定要每一台都放一份，這樣將來也會造成維護的困難。因為後續的 DEMO 會處理到好幾台不同 server 之間的溝通，因此我先把 KEY STORE 用這方式抽象化方便說明。再次強調，實際運作時這部分最好要替換成 KEY container 為佳。

RSACryptoServiceProvider 是 .NET 內建的 class library, 可以透過 .FromXmlString( ) 將存在 XML 的 KEY 匯入之後，這個 RSACryptoServiceProvider 的 instance 就具備了加解密、簽屬或是驗證數位簽章的能力了。

XML 的格式，也是 Microsoft 是先定義好的，其實他只是把 Parameters 用 XML 描述而已，關鍵的是其中幾個關鍵數值而已。這格式可以區分 Public / Private 屬性，也就是我門口中常聽到的 Public Key / Private Key。我把同一組 Key Pair 分別匯出包含與不包含 Private Key 的版本內容，給各位參考。這不是真正運作中的 KEY，我也不怕各位看，這是這範例程式真正在使用的 KEY，貼到 CODE 內是可以使用的:

包含 Public / Private Info 的 XML:

```xml
<RSAKeyValue>
  <Modulus>tkh6g17prMpaRC+p7Q4FQHuTti5ekcjWNqQC9Qh3tsrkyq4pp+lytagR6y6q9zSA57UQy3cURJt/0km2W0v31yC9YFmhZ6fbmCfUCBmxbvb1CzgkFP3fx6cipRzScCpIMmUXcvtpvKR+fWbt1i9ohoT8Sk2zTGd4dqyFTselNGc=</Modulus>
  <Exponent>AQAB</Exponent>
  <P>7ZU2GJKEJTSIr648g/2m2GgBggTVTY6uehkGSH/pnyuc1517Jy2BBThMK7Sa1vvcmcnJYYKd9KhnpdcYgJXVJQ==</P>
  <Q>xGnan823m0OB9r7fltqMVE1MOILqmLDldN6gRB0fWnihFSMQoxQJBqdfvbqdnwRKPygMMXjOoxf13noP67Vbmw==</Q>
  <DP>6LbZMCSD7/WPVZXzjM4uWZc2suaNENULrmlIsEcqzVBo5wJImU2HLVfBtKXJbX9yy+jNqwfINNen/te8FmetSQ==</DP>
  <DQ>lm8IzoqOTPHokabhszXScyL89O94ZNhf9iIpF+JCSFXJ8ll3/Z9zxk/daYCMBuYPQ84VgLKpeYr5ept8pCi0bw==</DQ>
  <InverseQ>5Wn1A4VEJAI0F/3sMvzEm5CL2dLb5/Xo6yYg9HH6WuVnMr9p7DMcHce7FjCqKNIcC9QsFiuS/NpEMQ0QvUsgjA==</InverseQ>
  <D>E7GL7vKLq3vnObOul6pqnddcE5Q56mU444lfumpySKDuDAm5/Wam2oJwgSi3FuMoxB/XUywn1+u26RjGp2FzQq9mx0KkQGKM6mZfIMMVZDTLIyVVhQn66GuO1Zbt9hqWtBxmQy8X6TN9ASQeUFsOMDvtm0PrBrax7KHf1H8NIBU=</D>
</RSAKeyValue>
```

只包含 Public Info 的 XML:

```xml
<RSAKeyValue>
  <Modulus>tkh6g17prMpaRC+p7Q4FQHuTti5ekcjWNqQC9Qh3tsrkyq4pp+lytagR6y6q9zSA57UQy3cURJt/0km2W0v31yC9YFmhZ6fbmCfUCBmxbvb1CzgkFP3fx6cipRzScCpIMmUXcvtpvKR+fWbt1i9ohoT8Sk2zTGd4dqyFTselNGc=</Modulus>
  <Exponent>AQAB</Exponent>
</RSAKeyValue>
```

看到了嗎? 差異的部分就是你需要自己好好保管的機密，一旦外流了，你所有加密或是簽章的東西都不安全了。因為別人將會有辦法用你的身分發出任何資訊。而其他人完全沒辦法驗證真偽。這幾個參數的意義，有興趣的讀者可以[看看WiKi 的介紹](https://zh.wikipedia.org/wiki/RSA%E5%8A%A0%E5%AF%86%E6%BC%94%E7%AE%97%E6%B3%95)，跟我一樣看不懂也懶得看的，只要記得那些是 Private Info, 哪些是 Public Info 就夠了。

只要你匯入的 XML 包含 Private Info, 那麼這個 RSACryptoServiceProvider 就可以執行簽章 SignData( )的動作，反之你則只能進行驗證簽章 VerifyData( ) 的動作而已。

解釋了這些機制之後，再回頭來看看 EncodeToken( ) 的做法就更容易懂了，關鍵就在按照 SiteID 取出對應的 RSACryptoServiceProvider 之後，進行 SignData( ) 的動作那一行:

```csharp
/// <summary>
/// 
/// </summary>
/// <param name="token"></param>
/// <returns></returns>
public static string EncodeToken(TokenData token)
{
    // TokenData 經過序列化之後的 binary data (使用 BSON format)
    byte[] data_buffer = null;
    {
        MemoryStream dataMS = new MemoryStream();
        using (BsonWriter bw = new BsonWriter(dataMS))
        {
            JsonSerializer js = new JsonSerializer();
            token.TypeName = token.GetType().FullName;
            js.Serialize(bw, token);
        }
        data_buffer = dataMS.ToArray();
    }
            
    // data_buffer 的簽章
    byte[] sign_buffer = null;
    {
        //sign_buffer = _PublicKeyStoreDict[_CurrentSiteID].SignData(
        sign_buffer = _CurrentRSACSP.SignData(
            data_buffer,
            _HALG);
    }

    // 打包 data_buffer, sign_buffer
    return string.Format(
        @"{1}{0}{2}",
        _SplitChar,
        Convert.ToBase64String(data_buffer),
        Convert.ToBase64String(sign_buffer));
}
```

接下來看 DecodeToken( ) 也是一樣，看看關鍵的 RSACryptoServiceProvider.VerifyData( ) 那段:

```csharp
/// <summary>
/// 
/// </summary>
/// <typeparam name="T"></typeparam>
/// <param name="tokenText"></param>
/// <returns></returns>
public static T DecodeToken<T>(string tokenText) where T : TokenData, new()
{
    bool isSecure;
    bool isValidate;
    T token = TryDecodeToken<T>(tokenText, out isSecure, out isValidate);

    if (isSecure == false) throw new TokenNotSecureException();

    if (isValidate == false) throw new TokenNotValidateException();

    return token;
}


/// <summary>
/// 
/// </summary>
/// <typeparam name="T"></typeparam>
/// <param name="tokenText"></param>
/// <param name="isSecure"></param>
/// <param name="isValidate"></param>
/// <returns></returns>
public static T TryDecodeToken<T>(string tokenText, out bool isSecure, out bool isValidate) where T : TokenData, new()
{
    string[] parts = tokenText.Split(_SplitChar);

    if (parts == null || parts.Length != 2) throw new TokenFormatException();

    byte[] data_buffer = Convert.FromBase64String(parts[0]);
    byte[] sign_buffer = Convert.FromBase64String(parts[1]);

    // 還原 token 物件，將資料反序列化還原為 object, 同時驗證 token 的授權是否合法
    T token = null;
    //string siteID = null;
    {
        MemoryStream ms = new MemoryStream(data_buffer, false);
        using (BsonReader br = new BsonReader(ms))
        {
            JsonSerializer js = new JsonSerializer();
            token = js.Deserialize<T>(br);

            if (token == null) throw new TokenFormatException();
        }
        isValidate = token.IsValidate();
    }

    // 檢查 signature, 確認 token 的安全性，確保資料沒有被偽造
    if (_PublicKeyStoreDict.ContainsKey(token.SiteID) == false) throw new TokenSiteNotExistException();

    isSecure = _PublicKeyStoreDict[token.SiteID].VerifyData(
        data_buffer,
        _HALG,
        sign_buffer);

    return token;
}
```

## 實際應用: ASP.NET MVC5 啟動時檢查授權碼

OK，經過這麼大費周章的說明 (只是說明的部分很多而已，CODE 其實沒多少)，我們終於可以大大方方地應用在網站上了。這部分老實說沒啥好 DEMO 的，不過為了讓這主題告一段落，還是補一下好了...  如果要參考授權資訊，讓 ASP.NET MVC 取得合法的授權才能啟動網站的話，只要按照下列步驟即可。我已 Visual Studio 2015 預設的 ASPNET MVC5 空白專案為起點，按照下列步驟 Step By Step:

將下列 Token 相關設定資訊，放到 ~/appsettings.json 內，加入 "License" 的區段，原本就有的 Data / Logging 的內容，為了省篇幅我就刪掉了::

```json
{
  "Data": {},
  "Logging": {},
  "License": {
    "TokenData": "nwAAAAJTaXRlVGl0bGUACAAAAFNJVEUgIzEACEVuYWJsZUFQSQABCUxpY2Vuc2VTdGFydERhdGUAADgYadwAAAAJTGljZW5zZUVuZERhdGUAAAjmJbsDAAACU2l0ZUlEAAcAAABHTE9CQUwAAlR5cGVOYW1lACQAAABBbmRyZXcuQXBpRGVtby5TREsuU2l0ZUxpY2Vuc2VUb2tlbgAA|0ofhHMSEHQGZMOafFQxF6zfQchnThv+iPc7PrFZMrL89dkxvYvkYjHhUYLgHNOVz3RGXMxAMQVnwZjrHRNz5GLkaLs19wl1HWCt9kOdWQI/zkvS129IZntdoM4hnN9F/aeVnsDtSS82lx+ESTIh2Wcp5wVwowkzI3l82D3dZwCoa",
    "SiteID": "ORCA",
    "SitePrivateKey": "<RSAKeyValue><Modulus>tkh6g17prMpaRC+p7Q4FQHuTti5ekcjWNqQC9Qh3tsrkyq4pp+lytagR6y6q9zSA57UQy3cURJt/0km2W0v31yC9YFmhZ6fbmCfUCBmxbvb1CzgkFP3fx6cipRzScCpIMmUXcvtpvKR+fWbt1i9ohoT8Sk2zTGd4dqyFTselNGc=</Modulus><Exponent>AQAB</Exponent><P>7ZU2GJKEJTSIr648g/2m2GgBggTVTY6uehkGSH/pnyuc1517Jy2BBThMK7Sa1vvcmcnJYYKd9KhnpdcYgJXVJQ==</P><Q>xGnan823m0OB9r7fltqMVE1MOILqmLDldN6gRB0fWnihFSMQoxQJBqdfvbqdnwRKPygMMXjOoxf13noP67Vbmw==</Q><DP>6LbZMCSD7/WPVZXzjM4uWZc2suaNENULrmlIsEcqzVBo5wJImU2HLVfBtKXJbX9yy+jNqwfINNen/te8FmetSQ==</DP><DQ>lm8IzoqOTPHokabhszXScyL89O94ZNhf9iIpF+JCSFXJ8ll3/Z9zxk/daYCMBuYPQ84VgLKpeYr5ept8pCi0bw==</DQ><InverseQ>5Wn1A4VEJAI0F/3sMvzEm5CL2dLb5/Xo6yYg9HH6WuVnMr9p7DMcHce7FjCqKNIcC9QsFiuS/NpEMQ0QvUsgjA==</InverseQ><D>E7GL7vKLq3vnObOul6pqnddcE5Q56mU444lfumpySKDuDAm5/Wam2oJwgSi3FuMoxB/XUywn1+u26RjGp2FzQq9mx0KkQGKM6mZfIMMVZDTLIyVVhQn66GuO1Zbt9hqWtBxmQy8X6TN9ASQeUFsOMDvtm0PrBrax7KHf1H8NIBU=</D></RSAKeyValue>",
    "PublicKeyStore": [
      {
        "SiteID": "GLOBAL",
        "KeyXML": "<RSAKeyValue><Modulus>23cuijAaHiumnoRM+VV1dqAGrYeYUt11OK4H5rcmXZeix2dxK9Oh2928A9RHwqpAU+u/HY1nrHo1nEUnduiIai+1JShg4flewwUnXAIrP3hxUtPly/5/9vHtalEABxPzVtRhwN2rtpVpxkR8j0U2r98TGrvr62xhg3KYDG6Qax8=</Modulus><Exponent>AQAB</Exponent></RSAKeyValue>"
      },
      {
        "SiteID": "ORCA",
        "KeyXML": "<RSAKeyValue><Modulus>tkh6g17prMpaRC+p7Q4FQHuTti5ekcjWNqQC9Qh3tsrkyq4pp+lytagR6y6q9zSA57UQy3cURJt/0km2W0v31yC9YFmhZ6fbmCfUCBmxbvb1CzgkFP3fx6cipRzScCpIMmUXcvtpvKR+fWbt1i9ohoT8Sk2zTGd4dqyFTselNGc=</Modulus><Exponent>AQAB</Exponent></RSAKeyValue>"
      }
    ]
  }
}
```

這邊除了加上授權相關資訊之外，也加上了 TokenHelper Init 所需要的相關資訊 (後面的案例會需要)

接下來，在 ~/Startup.cs 加入對應的判斷，若授權沒有通過驗證，則丟出 Exception, 中斷後面的動作。由於這個動作安排在定應 Routing 之前，沒有通過的話整個網站是無法正常啟用的。這段在 Startup.cs 的 public void Configure(...) 內:

```csharp
// init token
{
    IConfigurationSection licconf = Configuration.GetSection("License");

    Dictionary<string, string> dict = new Dictionary<string, string>();
    foreach (Dictionary<string, string> keyitem in licconf.Get<Dictionary<string, string>[]>("PublicKeyStore"))
    {
        dict.Add(
            keyitem["SiteID"],
            keyitem["KeyXML"]);
    }

    TokenHelper.Init(
        licconf.Get<string>("SiteID"),
        licconf.Get<string>("SitePrivateKey"),
        dict);

    SiteLicenseToken lictoken = TokenHelper.DecodeToken<SiteLicenseToken>(licconf.Get<string>("TokenData"));
}
```

除了 Init 所需的資訊，改成從 appsettings.json 取得之外，其他沒有太大的不同。各位可以自行編譯試看看。若授權正常的話，會順利執行 MVC 預設的示範網站。若失敗的話，會顯示 MVC ERROR 畫面，同時會列出出問題的 Exception 內容:

![授權一切正常時，可以正確地進入 MVC Web](/wp-content/uploads/2016/02/img_56c9629bc2f62.png)

![已經超出授權的日期，會引發 TokenNotValidateException，超過正常使用期限，則無法正常啟動網站。](/wp-content/uploads/2016/02/img_56c9625fc4d28.png)

![如果 TokenData 遭到損毀或是竄改偽造，則會辨識出這個 TokenData 的來源有問題，系統會發出 TokenNotSecureException](/wp-content/uploads/2016/02/img_56c9630d7d101.png)

完整的 Code 我就不貼了，整個完整的 Solution 有興趣的讀者們可以到我的 GitHub 上面 Clone 所有的 Source Code 下來慢慢研究~

完整程式碼下載: https://github.com/andrew0928/ApiDemo
