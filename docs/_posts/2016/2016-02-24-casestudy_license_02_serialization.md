---
layout: post
title: "[設計案例] 授權碼 如何實作?  #2, 序列化"
categories:
- "設計案例: 授權碼 如何實作?"
tags: [".NET","C#","專欄","技術隨筆","物件導向"]
published: true
comments: true
permalink: "/2016/02/24/casestudy_license_02_serialization/"
redirect_from:
wordpress_postid: 855
---

![](/images/2016-02-24-casestudy_license_02_serialization/img_56cc8c9caafc8.png)

這次直接跳到主題: 網站安裝授權開始吧。這東西的用途，就跟過去安裝軟體要輸入序號一樣的目的，輸入序號之後，軟體不用上網就要能知道你購買的是什麼版本，有哪些功能要被啟用? 在不連到 internet 的情況下，要單靠一段授權資料就達到這目的，最好是能簡單明瞭，資料結構清楚容易擴充維護，同時安全強度還要夠強 (防止偽造)，這就是這次要解決的問題。

我的目的，不但要顧及功能性(安全強度)，同時也要顧及程式碼及系統架構的層面，因此我拆成兩個部份來探討，一個就是最關鍵的資料安全問題，另一個就是如何用程式碼來表達及封裝這些功能?

<!--more-->

---

**[設計案例] "授權碼" 如何實作? 2016/02 (本篇系列文章)**  
#1. [需求與問題](/2016/02/17/casestudy_license_01_requirement/)  
#2. [授權碼序列化](/2016/02/24/casestudy_license_02_serialization/)  
#3. [數位簽章](/2016/02/24/casestudy_license_03_digital_signature/)  
#3. [(補) - 金鑰的保護](/2016/03/19/casestudy_license_03_appendix_key_management/)

---

## 資料的封裝: 序列化

先從簡單的開始吧! 我這次的想法是，先由原廠提供授權碼 (一段編碼過的外星文)，裡面包含兩大部分，分別是設定的資訊 (存放原廠讓你啟用那些功能)，另一段則是數位簽章 (確認這份資訊是原廠提供的)。我想要讓這樣的授權碼很容易的被產生、驗證、及讀取資訊。授權的內容對我而言並不是機密，可以公開沒有問題，然而真正的問題是我希望我能夠驗證這段授權是不是真的由原廠 (我們公司) 發出來的? 我需要驗證的是它的來源。為了能同時解決這兩個問題 (容易編碼解碼、驗證來源) 因此我設計了兩個類別，彼此搭配來完成這個任務:

![- Class Diagram](/images/2016-02-24-casestudy_license_02_serialization/img_56c4a40001a60.png)

兩大主角分別是 TokenData, 以及 TokenHelper。 TokenData 代表授權的設定，任何自訂的授權資料，都應該繼承這個類別，擴充設定資訊，同時定義 (override) 你自己的驗證邏輯，例如授權是否過期等等。跟他搭配的，則是 TokenHelper，專門負責產生、編碼、解碼 TokenData 用的靜態類別 (static class)。公開的介面只有 Init, Create / Encode / Decode Token 這組 static method. 這樣的設計，其實是參考了 Factory 這個 Design Pattern, 可以有效的把 TokenData 的生成方是從本身的 constructor 獨立出來，集中在 TokenHelper 一起控制。待會會講到的數位簽章的部分，也會在那邊介紹。

TokenData 本身就只定義了設定資料，以及 bool IsValidate() 這個驗證授權設定本身是否正確的 method. 然而物件 (object) 終究還是需要被轉換成資料 (data)，才能儲存及簽章。這邊當然也不再重新發明輪子了，直接採用紅翻天的 JSON 來當成序列化的格式。

```csharp
/// <summary>
/// 如何自訂 TokenData ?
/// 
/// 1. 繼承自 TokenData
/// 2. 加上你的自訂項目，標上 [JsonProperty]
/// 3. 覆寫 (override) bool IsValidate( ), 自訂你的授權驗證邏輯
/// 
/// 完成
/// </summary>
[JsonObject(MemberSerialization = MemberSerialization.OptIn)]
public abstract class TokenData
{
    internal TokenData() { }

    /// <summary>
    /// 產生該 Token 的 Site ID
    /// </summary>
    [JsonProperty]
    public string SiteID { get; internal set; }

    /// <summary>
    /// 對應 TokenData 衍生類別的 Type Name
    /// </summary>
    [JsonProperty]
    public string TypeName { get; internal set; }

    /// <summary>
    /// (可覆寫) 驗證 Token Data 資料是否合法
    /// </summary>
    /// <returns></returns>
    public virtual bool IsValidate()
    {
        if (this.GetType().FullName != this.TypeName) return false;
        return true;
    }
        
}
```

## 自訂 TokenData: SiteLicenseToken

這個設計應該簡單到不能再簡單了吧? 我直接使用 NuGet 上面的 [NewtonSoft.Json](https://www.nuget.org/packages/Newtonsoft.Json/) 這個套件，來進行序列化，為了別把一堆亂七八糟的東西也一起轉成資料，我採用明確的宣告方式，只有被標上 [JsonProperty] 的部分，才會被序列化處理。如果你想要自訂一個你專用的 TokenData, 那也很簡單，繼承下來就可以了。上圖的 class diagram 有個 SiteLicenseToken 就是一個例子:

```csharp
public class SiteLicenseToken : TokenData
{
    /// <summary>
    /// 該網站的註冊 TITLE
    /// </summary>
    [JsonProperty]
    public string SiteTitle;

    /// <summary>
    /// 是否啟用該網站的 API access
    /// </summary>
    [JsonProperty]
    public bool EnableAPI;

    /// <summary>
    /// 網站授權: 啟用時間
    /// </summary>
    [JsonProperty]
    public DateTime LicenseStartDate;

    /// <summary>
    /// 網站授權: 停用時間
    /// </summary>
    [JsonProperty]
    public DateTime LicenseEndDate;

    /// <summary>
    /// 
    /// </summary>
    /// <returns></returns>
    public override bool IsValidate()
    {
        if (this.LicenseStartDate > DateTime.Now) return false;
        if (this.LicenseEndDate < DateTime.Now) return false;
        return base.IsValidate();
    }
}
```

真的是沒有藏甚麼特別的機關在裏頭，只要這幾個步驟就完成:

1. 繼承自 TokenData
2. 加上你的自訂項目，標上 [JsonProperty] 序列化的標註
3. 覆寫 (override) bool IsValidate( ), 自訂你的授權驗證邏輯

沒錯，這樣就結束了... 看起來好像沒什麼，接下來就換 TokenHelper 上場，來看看他是怎麼跟 TokenData 搭配的?

## 驗證授權碼 (解碼 + 驗證)

先來看看使用頻率最高的: 如何驗證授權碼，並且取得授權的資訊?

```csharp
// 初始化存放所有金鑰的 KEYSTORE，同時設定這個網站本身的 SITEID
TokenHelper.Init(
    "GLOBAL", 
    @"D:\KEYDIR\_PRIVATE\GLOBAL.xml", 
    @"D:\KEYDIR");

// 本文 + 簽章
plaintext = @"nwAAAAJTaXRlVGl0bGUACAAAAFNJVEUgIzEACEVuYWJsZUFQSQABCUxpY2Vuc2VTdGFydERhdGUAADgYadwAAAAJTGljZW5zZUVuZERhdGUAAAjmJbsDAAACU2l0ZUlEAAcAAABHTE9CQUwAAlR5cGVOYW1lACQAAABBbmRyZXcuQXBpRGVtby5TREsuU2l0ZUxpY2Vuc2VUb2tlbgAA|0ofhHMSEHQGZMOafFQxF6zfQchnThv+iPc7PrFZMrL89dkxvYvkYjHhUYLgHNOVz3RGXMxAMQVnwZjrHRNz5GLkaLs19wl1HWCt9kOdWQI/zkvS129IZntdoM4hnN9F/aeVnsDtSS82lx+ESTIh2Wcp5wVwowkzI3l82D3dZwCo=";

try
{
    // 驗證簽章。若驗證失敗則會丟出 TokenException
    SiteLicenseToken token = TokenHelper.DecodeToken<SiteLicenseToken>(plaintext);

    // 成功通過驗證，直接取出設定值
    Console.WriteLine("SiteID:        {0}", token.SiteID);
    Console.WriteLine("Site Title:    {0}", token.SiteTitle);
    Console.WriteLine("Enable API:    {0}", token.EnableAPI);
    Console.WriteLine("License Since: {0}", token.LicenseStartDate);
    Console.WriteLine("License Until: {0}", token.LicenseEndDate);
}
catch(TokenException)
{
    // 驗證失敗
}
```

初始化的部分，包含到金鑰的存放設定，稍後再說明，只要在第一次使用 TokenHelper 前有正確的初始化就可以了。不論我們是從甚麼方式取得授權碼，把這字串內容，丟進 TokenHelper.DecodeToken( ) 就可以進行各種驗證。若成功通過所有的驗證，那麼你就能將這堆授權碼還原成當初產生的 TokenData 了。看起來沒有一行是多餘的，就是 decode, and use it, 就這樣而已。

來挖開這個 Decode 是怎麼做的吧，先看看 code:

```csharp
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

前面的驗證 hash / signature 後面再說明，先看看 token 被反序列化還原成物件之後的行為。這邊是套用到物件導向的 "多形" (Polymorphism) 的機制，不論你是如何自定 TokenData, 這邊還原後，會主動呼叫你定義的 IsValidate( ) method, 來驗證目前的設定是否合法。因此當你在設計自訂 TokenData 時，可以填上你想要的自訂驗證方式，比如驗證授權是否過期，檢查帳號數量是否超過上限等等就可以了。在每次 TokenData 被驗證及解碼還原時，都會自動執行一次驗證。

## 產生授權碼 (編碼 + 簽章)

剩下最後一段了，就是如何從無到有產生 TokenData。先來看看產生 TokenData 的 code:

```csharp
// 初始化存放所有金鑰的 KEYSTORE，同時設定這個網站本身的 SITEID
TokenHelper.Init(
    "GLOBAL", 
    @"D:\KEYDIR\_PRIVATE\GLOBAL.xml", 
    @"D:\KEYDIR");

// 建立空的 SiteLicenseToken 物件
SiteLicenseToken slt = TokenHelper.CreateToken<SiteLicenseToken>();

string plaintext = null;

// 填入設定值
slt.SiteTitle = "SITE #1";
slt.EnableAPI = true;
slt.LicenseStartDate = new DateTime(2000, 1, 1);
slt.LicenseEndDate = new DateTime(2099, 12, 31);

// 編碼，將原始資料及數位簽章，打包成單一字串。可以用任何形式發佈出去
plaintext = TokenHelper.EncodeToken(slt);
```

接著看一下，在 TokenHelper 內的 CreateToken 是怎麼實作的:

```csharp
/// <summary>
/// 建立新的 TokenData 物件
/// </summary>
/// <typeparam name="T">TokenData 型別，必須是 TokenData 的衍生類別</typeparam>
/// <returns></returns>
public static T CreateToken<T>() where T : TokenData, new()
{
    T token = new T();

    token.SiteID = _CurrentSiteID;
    token.TypeName = typeof(T).FullName;

    return token;
}
```

最後，TokenData 準備好之後，會透過 TokenHelper.EncodeToken( ) 的協助，產生最終的授權碼字串:

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

最後這三段我一起說明，產生的程序有三個步驟:

1. 呼叫 TokenHelper.CreateToken<T>( ), 產生一個未初始化的 TokenData 物件。
2. 取得 token 的物件後，完成他的初始化 (設定必要欄位資訊)。
3. 透過 TokenHelper.EncodeToken( ) 的處理，將 token 轉成包含簽章的設定資料字串。

(1) 建立的步驟，除了用 CreateToken<T>() 來取代物件本身的 new 之外，就沒有特別的地方了。為何要這樣使用，有興趣的讀者可以參考一下 "工廠模式" (Factory Pattern)。整個過程的重點在 (3) 的轉換過程，正好跟前面的 DecodeToken( ) 是相反的。先將 TokenData 序列化，之後計算簽章，最後打包合併在一起就完成了。

打包的部分，因為格式很簡單很固定，我就沒特別去處理了。[研究了一下 BASE64 的編碼](https://en.wikipedia.org/wiki/Base64)，他會把 3 bytes 的資料，編成 4 characters, 因此每個 char 只要負責 64 種不同的變化就夠了。BASE64 編碼的規範，只會用到這 65 個字元，不會有其他字元出現:

1. 英文字母 (a ~ z, A ~ Z): 26 + 26 = 52
2. 數字 ( 0 ~ 9 ): 10
3. 另外補上兩個符號字元 ( + / ): 2
4. 不足 4 的倍數，空白部分用 = 填補: 1

所以我的格式就從簡，挑了 | 這個不在 65 個字元內的符號，當作分隔字元，分別把 data 跟 signature 的 BASE64 編碼自串串起來，就是我的授權碼了。EncodeToken( ) / DecodeToken( ) 就都按照這個規格來進行編碼及解碼。

這邊要特別注意的是，如果靠這段程式就能產生一個可用的授權碼，那別的工程師拿我的 class library 依樣畫葫蘆不就能偽造資料，任意產生他想要的授權碼了嗎? 當然沒有這麼好的事。關鍵在於產生的 code 之前，必須先 init key store 的部分。要能產生簽章，你必須先拿到 private key 才行，而這段 code 的前提是你的 KEY STORE 內，必須要包含原廠的 private key ，否則這段 code 根本無法執行。這部分的細節，留到下一段 [數位簽章] 的說明再來探討。

完整程式碼下載: [https://github.com/andrew0928/ApiDemo](https://github.com/andrew0928/ApiDemo)

下回預告: #3 數位簽章

**[設計案例] "授權碼" 如何實作? 2016/02 (本篇系列文章)**  
#1. [需求與問題](/2016/02/17/casestudy_license_01_requirement/)  
#2. [授權碼序列化](/2016/02/24/casestudy_license_02_serialization/)  
#3. [數位簽章](/2016/02/24/casestudy_license_03_digital_signature/)
