---
layout: post
title: "微服務架構 #4, 如何強化微服務的安全性? API Token / JWT 的應用"
categories:
- "系列文章: .NET + Windows Container, 微服務架構設計"
- "系列文章: 架構師觀點"
tags: ["API", "Token", "microservice", "系列文章", "ASP.NET", "架構師", "Swagger"]
published: true
comments: true
redirect_from:
logo: /wp-content/uploads/2016/12/apitoken-logo.jpg
---

![洛基的權杖 - Token](/wp-content/uploads/2016/12/apitoken-logo.jpg)

其實本來就有打算寫這篇了，聊聊微服務架構下的安全機制該怎麼做? 微服務把整套系統切割成很多套獨立的服務，這些
獨立的服務就必須有機制去識別其他的服務是否是安全的? 有沒有很簡單的方法解決他? 這類越是基礎的問題，越需要
使用正確的架構及演算法。沒有理論的基礎，只會越搞越糟而已，這也是架構師最重要的職責。微服務是個很要求
架構正確的應用模式，想要導入微服務，千萬別忽略這部分。

很巧的是，兩個禮拜前受邀在[線上讀書會](https://www.facebook.com/groups/207139586323090)分享這個主題，
我就把我過去土炮 API Token 的經驗拿來分享了，藉由簡單的 POC 過程，讓大家
了解 API Token 的原理跟應用。這套機制尤其適用在 microservices 架構下，因為這套機制靠著密碼學的原理，讓兩個
service 之間不需要直接溝通，就能完成驗證的過程。

這兩年 [JWT](https://jwt.io/) (Json Web Token) 當紅，但是跟幾個人聊了聊，大都是停在 library 用的很熟練
的階段，但是問到如何應用? 有無變通的應用方式就剩一半了，再問下去問知不知道 JWT 背後怎麼運作的? 若要實作有無
辦法自己做一套? 就沒有了 XD

在開始之前，先聊一下我為何會想挑這個主題。從事軟體開發的行業，我一直覺的我這年代是很幸運的。比我還年長的，
大都經歷過寫組合語言，甚至是用卡片的年代。比我年輕的，才剛入行就要面對各種技術及 framework。比我年長的那一代，
過程大都在跟工具及技術奮鬥，能把心思花在解決 user 問題本身的比例不高。比我年輕的這一代，面臨太多 framework,
每個 framework 都是累積多少經驗跟智慧才堆積起來的結晶，能夠充分掌握怎麼 "使用" 就很了不起了，哪有時間等你
慢慢鑽研背後的原理?

所以我覺得我這年代是很幸運的，我經歷過軟體還不是這麼複雜難搞的年代，也經歷過 Java, C#, JavaScript 這些可以
讓我專心思考架構之美的程式語言。我碰過很多問題，當年都還沒有妥善的 framework 可以直接套用，因此或多或少
我都自己土炮過一些 framework, 包含 ORM (在 SQL2000 年代，實作 object > xml > database，外加 xml index), 
Content Server (自己處理 URL, 用自己的機制去 mapping file system), MVC 架構 (對，用 asp.net webform + 
url rewrite, 實作 MVC 架構) 等等，當然也包括這次的主題: API Token。

<!--more-->

這些土炮的過程跟經驗，其實價值不在於我當年寫的東西多好用 (現在都被熱門 framework 比下去了 T_T)。但是開發
的過程累積的 know how 是無價的。比如我土炮過 ORM，現在用別家的 ORM 我大概就能理解他的做法是什麼，這樣的
作法在那些地方會有限制等等。更重要的是，我的進入障礙變得很低，我不再需要去了解一堆背後的原理，我只剩下表面
的工具跟函式庫需要去熟悉而已。因為上手速度快，所以我有更多充足的時間去評估幾套類似的 framework, 能比其他人
更精確的挑出合用的技術。這些能力是擔任 architect 必備的啊，挑錯 framework, 你可能會害整個團隊浪費幾個人月
的精力..

這篇文章其實寫的很到位，完全寫到我心坎裡了，貼出來給大家參考參考

[土炮精神](http://www.ithome.com.tw/voice/99856), 王建興 2015/11/19

節錄文章最後一個段落，當作前言的結尾:

> *如果我們在軟體開發的領域裡，只做使用者，那麼，很多基礎的東西，我們會愈來愈陌生，甚至就失去把它們做出來的能力了。*  
>
> *自己把某個主題做了一次，即使做的沒有現成的那麼好、那麼強大，但是一些基礎的核心議題必然經歷過一輪，之後，即使只當使用者了，也會更了解這個主題。*  
>
> *而或者，這個「土炮」出來的產物，未來，得以繼續發展，而漸漸地，有了和其他產品分庭抗禮的實力。你能擁有自己土炮的實力之後，當現成的產物無法那麼貼切的滿足自己的需求，才有機會透過自己來滿足這些需求。*  


{% include series-2016-microservice.md %}



# API Token 原理說明

接下來就來重現當天線上讀書會的內容了。讀書會全程都有[錄影](https://www.facebook.com/andrew.blog.0928/videos/345280552513896/) (1小時)，不想花一小時看得，可以
直接看 slideshare 的[投影片](http://www.slideshare.net/chickenwu/api-token?qid=7bd09d0a-587f-4ed6-826d-d12c71f0b252&v&b&from_search=1)，搭配 github 上面的 [source code](https://github.com/andrew0928/MeetUp.ApiTokenDemo) 一起服用。這些連結請到文章最後面就看的到。


## API Token 要解決的難題

首先先來看看，一般的網站開發，若碰到熱門的服務導向架構，你需要從 A 網站或服務取得的授權，再到 B 網站去使用
他的服務，同時 A B 兩個服務之間沒有辦法很有效率且即時的溝通時，如何解決兩個網站之間的信任問題? 尤其是在 internet
上，離開服務的範圍都是不安全的，你傳遞的資訊送到 client side (不論是 APP 或是 browser) 更是不安全，資安專家
有上百種的方式可以把你想隱藏的資訊挖出來破解...

舉個例子，如果 A 服務是付款，同時讓你取得遊戲點數，你可以去 B 服務訂購商品。B 服務寄出商品後會月底跟 A 服務商
收取貨款。這種情況下如果資訊的傳遞沒有保護好，client 在 A 付了 100 元，卻可以在 B 訂購 1000 元的商品，這樣你還
敢做生意嗎?

![API Token 要解決的難題](/wp-content/uploads/2016/12/apitoken-slides04.png)

簡單的用一張圖來代表這個情境，你必須想一個方式來確保這些資訊的傳遞是安全的，否則賠錢的生意絕對做不久的...

先來看看實體的世界怎麼解決問題? 大家應該都買過車票，我舉個類似的情境。你在 7-11 訂了張車票，也付款取票了。
當你要去車站搭車時，車站的驗票系統或是站長確認無誤，讓你進站搭車了。這時站長可能當場打電話給 7-11 確認這張
車票嗎? (Orz, 突然覺得我這例子有點蠢..) 當然不會這樣做。所以車站憑 "什麼" 確認這張票的正確性? 同時票上面
也註記了你的服務使用範圍，例如你可以搭 1/1 72車次 莒光號，從台北到花蓮站，座位是 9 車 16 號...

最基本的是車票本身有防偽造的設計，例如蓋章，雷射標籤，磁卡等等。這機制如果夠可靠，車站只需要檢查車票是不是
假的 (是不是真的從售票單位賣出來的?)，只需要確認上面標記的資訊有無被竄改 (台北到花蓮，有沒有被塗改?)。這些
資訊若都能簡單的驗證，那麼就可以省掉大幅的溝通成本，不需要跟 7-11 當場確認就可以讓乘客搭車了。


## RSA 數位簽章

當你把問題拆解成: B 要能驗證資訊是原封不動從 A 送出的，這問題其實就簡化很多了。關鍵技術就只有一個: 數位簽章。
先不講技術，來講 "簽章" 的目的是什麼?

現實世界的文件，合約等等，都是印出紙本，要你看完後在上面簽名，代表你同意上面的內容。或是新聞稿、公文等，你在
上面簽名，代表這是你本人發出來的訊息，不是路人甲假冒你名字發言的。為什麼簽個名就有這效果? 因為每個人的筆跡不同，
簽名是無法偽造的，所以把明文跟簽名放在一起，就有這種效用。

數位的世界怎麼重現這樣的情境? 那就是密碼學裡常講到的 "數位簽章" (digital signature) 了。
講到密碼學，我想大家頭就開始痛了，我點到為止就好，我們常聽到的 RSA 加密，各位只要記得三個原則:

![RSA基本概念](/wp-content/uploads/2016/12/apitoken-slides05.png)

這原則你就暫時把它當作鐵律，別再去懷疑他了。他是有數學的原理在背後支持的，當這三條鐵律在有限的時間內不可能被
破解的話，我們能怎麼用它來解決問題? 先來看看 RSA 怎麼做到數位簽章的效果?

![RSA基本概念-產生數位簽章](/wp-content/uploads/2016/12/apitoken-slides06.png)

**Hint**: Hash
> 在這產生簽章的過程中，Hash 是個必須要懂得技巧。你可以用特定演算法，把一連串的資料算出他的 Hash。如果原始資料
> 改了一個 byte, 那算出來的 Hash 就會完全不一樣。若不一樣的資料算出一樣的 Hash, 這就是 Hash 碰撞。好的演算法，很少會碰到碰撞的狀況。
> 尤其是原始資料看起來格式等等都正確，只是改了你想改的內容時，還能算出一樣的 Hash, 那機率更低。

數位簽章的原理就是拿原始資料的 Hash, 用你的 private key 算出簽章，附加在你的原始資料中，就是簽章過的資料了。



![RSA基本概念-驗證數位簽章](/wp-content/uploads/2016/12/apitoken-slides07.png)

由 A 送出的簽章過的資料，送到 B 手上，B 只要用相反的程序驗證就可以了。其中的關鍵就是，經過 private key 加密的
Hash, 只有對應的 public key 能解開。若你用特定對象的 public key 解開後驗證無誤，你就能確認手上的資料是他的
private key 產生出來的。然而 private key 只有對方手上才有，整個過程就可以肯定資料來源跟正確性。

實際上驗證的步驟是:

1. 分解出資料跟簽章兩部分
1. 將簽章 (加密過的 Hash) 用 public key 解密，可以還原出 Hash
1. 將 (1) 分解出的資料，自己重新計算一次 Hash #2
1. 比對 Hash 與 Hash #2，若兩者相同，則資訊安全無誤，是 A 送出來的內容沒有被竄改過

這麼神奇嗎? 沒錯! 這就是數學神奇的地方。搭配這簡單的應用，你就能確認手上的資訊是安全的了。即使在傳遞的過程
中被 1000 個 hacker 看光了，那也無所謂，這資訊沒被竄改就足夠了，不是嗎?




# API Token 實作 (土炮版)

好，數位簽章的故事講完，開始應用了。前面講的數位簽章能怎樣幫我們解決難題?

回到剛才的場景，當你通過帳號密碼等等各種驗證機制後，A 服務已經願意跟你交易了，你付了 100 元，A 產生了簽章過的 100 元
代幣給你，這就是 SESSION TOKEN。你可以憑著這 SESSION TOKEN 到 B 去使用，所有的帳都記在 A 的帳上。B 怎麼確認
A 同意你這樣做? 用上述流程驗證簽章過的 SESSION TOKEN 就可以了。

當然 A 能附加在 SESSION TOKEN 上的資訊不只是 "100元" 這麼簡單，你可以附加任何你想要的資訊上去，只要最後記得
正確地完成簽章程序就好了。

該怎麼做? 開始來看 code 了。其實這些做法我大約一年前有三篇文章講過了，這邊我摘要的說明就好。為了簡化簽章跟驗證的程序，
我設計了簡單的 ```TokenData``` 與 ```TokenHelper``` 兩個類別。```TokenData``` 用來存放 Token 本身的資料，他會被 Json 
的 library 進行 serialization / deserialization。```TokenHelper``` 則是做編碼及解碼動作用的工具類別。

直接來看 code, 先看 ```TokenData```, 所有的 ```TokenData``` 都必須衍生自 ```TokenData``` 這個基底類別:

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
    /// 對應 TokenData 衍生類別的 Type Name
    /// </summary>
    [JsonProperty]
    public string TypeName { get; internal set; }

    [JsonProperty]
    public DateTime ExpireDate { get; set; }
    

    /// <summary>
    /// (可覆寫) 驗證 Token Data 資料是否合法
    /// </summary>
    /// <returns></returns>
    public virtual bool IsValidate()
    {
        if (this.GetType().FullName != this.TypeName) return false;
        if (DateTime.Now > this.ExpireDate) return false;
        return true;
    }
}
```    

這次範例裡面用到的 ```SessionToken```:

```csharp
public class SessionToken : TokenData
{

    [JsonProperty]
    public DateTime CreateDate { get; set; }

    [JsonProperty]
    public string ClientID { get; set; }

    [JsonProperty]
    public string UserHostAddress { get; set; }

    [JsonProperty]
    public bool EnableAdminFunction { get; set; }

    [JsonProperty]
    public bool EnableVIPFunction { get; set; }

    [JsonProperty]
    public bool EnableMemberFunction { get; set; }
}
```    

接著來看看 ```TokenHelper``` 如何替 ```TokenData``` 做編碼及解碼? 編碼 (Encode) 的部分:

```csharp
public static string EncodeToken(string keyName, TokenData token)
{
    if (_RSACSP_STORE[keyName].PublicOnly) throw new InvalidOperationException("Need Private KEY.");

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
        sign_buffer = _RSACSP_STORE[keyName].SignData(
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


接著是解碼 (Decode) 的部分:

```csharp
public static T DecodeToken<T>(string keyName, string tokenText) where T : TokenData, new()
{
    bool isSecure;
    bool isValidate;
    T token = TryDecodeToken<T>(keyName, tokenText, out isSecure, out isValidate);

    if (isSecure == false) throw new TokenNotSecureException();

    if (isValidate == false) throw new TokenNotValidateException();

    return token;
}


public static T TryDecodeToken<T>(string keyName, string tokenText, out bool isSecure, out bool isValidate) where T : TokenData, new()
{
    string[] parts = tokenText.Split(_SplitChar);

    if (parts == null || parts.Length != 2) throw new TokenFormatException();

    byte[] data_buffer = Convert.FromBase64String(parts[0]);
    byte[] sign_buffer = Convert.FromBase64String(parts[1]);

    // 還原 token 物件，將資料反序列化還原為 object, 同時驗證 token 的授權是否合法
    T token = null;
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
    
    isSecure = _RSACSP_STORE[keyName].VerifyData(
        data_buffer,
        _HALG,
        sign_buffer);

    return token;
}
```        

> 程式碼加起來大約 100 行左右而已，稍微看一下應該不難看懂。其實只有幾個關鍵而已，```TokenData``` 用來代表
> 你要保護的資料內容，你可以自己衍生出來擴充。只要配合 Json 的規範去標記 attrib 就可以了。編碼之前
> 會先用 Json 把你的 ```TokenData``` 編成字串 (範例我用 [BSON](http://bsonspec.org/), Binary Json, 效率跟體積會好一些)。
> 
> 接著就是上述數位簽章的程序了，計算 Hash 並且用 private key 加密 (這段都被包在 .SignData() 內了)，
> 最後的結果跟 data 合併再一起。
>
> 解碼的過程就是反過來，加上驗證的結果就結束了。


這些基礎準備好之後，後續用起來就簡單了，在 A 的部分 (請參考 AUTH 這個 project) 這樣使用，可以得到
一串 SessionToken 字串:

```csharp
/// <summary>
/// 已經註冊過的開發者，可以憑 APIKEY，向 AUTH 認證服務
/// 建立 SESSION。SESSION 建立成功後會取得 SESSION TOKEN，
/// 可以憑 TOKEN 道別的服務去呼叫 API。
/// 
/// SESSION TOKEN 有效期限為 60 分鐘
/// </summary>
/// <returns></returns>
public IHttpActionResult Post()
{
    string apikey = this.Request.Headers.GetValues("X-APIKEY").First();
    ApiKeyToken apikeyToken = TokenHelper.DecodeToken<ApiKeyToken>("APIKEY", apikey);

    SessionToken sessionToken = TokenHelper.CreateToken<SessionToken>();
    sessionToken.ClientID = apikeyToken.ClientID;
    sessionToken.UserHostAddress = System.Web.HttpContext.Current.Request.UserHostAddress;
    sessionToken.CreateDate = DateTime.Now;
    sessionToken.ExpireDate = DateTime.Now.AddHours(1.0);
    sessionToken.EnableAdminFunction = false;
    sessionToken.EnableMemberFunction = !apikeyToken.Tags.Contains("BAD");
    sessionToken.EnableVIPFunction = apikeyToken.Tags.Contains("VIP");

    return new TokenTextResult("SESSION", sessionToken);
}
```


client 拿到 SessionToken 後，呼叫 B 的 API 時會把 SessionToken 一起帶過去。在 B 只要這樣
還原 SessionToken 物件，沒有產生任何 Exception 就算驗證成功:

```csharp
/// <summary>
/// 骰出指定次數的骰子
/// </summary>
/// <param name="count">要骰幾次?</param>
/// <returns></returns>
public IEnumerable<int> Get(int count)
{
    // session check
    SessionToken session = TokenHelper.DecodeToken<SessionToken>(
        "SESSION", 
        this.Request.Headers.GetValues("X-SESSION").First());

    // 以下略過
}
```

好，這麼一來你可以不用擔心 SessionToken 的內容被亂改了。裡面標記的資訊都是可以信賴的，不需要懷疑他。
這個例子我是舉遊樂場的例子，AUTH 代表售票口，使用者透過 API TOKEN 認證通過後，就可以取得 SESSION TOKEN。
裡面註記了使用期限 (ExpireDate), [你的名字](https://zh.wikipedia.org/wiki/%E4%BD%A0%E7%9A%84%E5%90%8D%E5%AD%97%E3%80%82) (UserID)，還有 A 對你的註記 (標籤 Tags)。這些


API 專案則代表遊樂場，他會依據你的 SESSION TOKEN，確認無誤且沒有過期的話，就提供遊樂設施給你使用。隨著
Tags 註記的不同，你能夠享用的設施層級也不同。被標記為 VIP 則可無限次使用 (骰骰子可骰無限次)。若被標記為
奧客 (BAD) 則只能骰五次。沒有特別標記就是一般會員，最多可以骰 10 次。

各位可以自己試看看，你也許可以還原 SESSION 的內容，但是除非你有拿到 A 的 private key, 否則你再怎麼樣
也無法產生你想要的 SESSION TOKEN 內容。就算只是想從已產生的 SESSION TOKEN 去把 BAD 改為 VIP 也沒辦法。
因為你改不動簽章的部分。一但你改了原始資訊，簽章還原的 Hash 還是修改前的 Hash, 而 B 重新計算的 Hash #2
則是修改後的 Hash, 演算法告訴我們這樣的情況下 Hash 會不同，造假的 SESSION TOKEN 就被揪出來了。

整個 Demo 的過程很多細節，文章不大容易表達，有興趣的可以直接看影片的 Demo, 那邊解說得比較詳細。同時還有
示範如何用 Swagger 測試 API 的方式。正好 DEMO 的東西也都放在 Azure 上面，用的跟[上一篇文章](/2016/11/27/microservice6/) 講的是同一個服務: Azure API Apps。
有興趣的朋友可以參考這段 [影片](https://www.facebook.com/andrew.blog.0928/videos/345280552513896/):  11:50 ~ 43:00  



# 阻擋 Replay Attack

甚麼是 "Replay Attack" ? 先來看看 [Wiki](https://en.wikipedia.org/wiki/Replay_attack) 的說法: 
https://en.wikipedia.org/wiki/Replay_attack

簡單的說，Hacker 根本不用去跟你的 ```TokenData``` 加解密等等去奮鬥，他只要去偷一份真實的 SessionData，在他
過期之前使用就夠了。因為他偷來的是 100% 真實，100% 正常程序產生的 SessionToken, 你要驗證也一定是對的..
這種情況我們該怎麼應付?

其實，只要多一個小動作，你就能阻絕那些竊聽 / 攔截 Token 的攻擊了。在現實世界，這就像
有小偷把你的車票偷走，複製一份 (而且複製的非常精美，分不出真假)。結果偷兒就用這張假車票去搭車了...
預防方法很簡單，想辦法在車票上記名，然後搭車再出示身分證件。 

這樣的機制，在數位的世界要怎麼做? 其實 Token 的應用是可以有很多變化的，先來重新來看一下 SessionToken 
的定義長什麼樣子:

```csharp
public class SessionToken : TokenData
{
    [JsonProperty]
    public DateTime CreateDate { get; set; }

    [JsonProperty]
    public string ClientID { get; set; }

    [JsonProperty]
    public string UserHostAddress { get; set; }

    [JsonProperty]
    public bool EnableAdminFunction { get; set; }

    [JsonProperty]
    public bool EnableVIPFunction { get; set; }

    [JsonProperty]
    public bool EnableMemberFunction { get; set; }
}
```    

除了 ```TokenData``` 就內含 ExpireDate 來紀載這個 Token 的有效期限之外，SessionToken 也額外附加
了 UserHostAddress, 用來紀載授權的 Client 的 IP Address. 因為 Session 是控制很短的一段時間內
的授權，通常是幾分鐘，到幾個小時不等，我先假設這段期間內使用者的 IP 不會變化。

加了這個欄位能幹嘛? 這欄位在 client 跟 A (AUTH) 取得授權，產生 SessionToken 時就決定好了，A 偵測到
使用者 IP 就把他寫進 Token, 簽章之後整筆 Token 到了 B (API)，驗證玩 Token 後接著驗證使用者 IP 是否
符合，通過再提供服務。


這裡使用 IP 也是類似的意思。當然 IP 不是 100%
適合的資訊，這只是當作範例。如果你的 client 是手機的 APP，行動網路 IP 一直在變化，這時你若能取得
device unique ID, 或是電話號碼等等，都是個值得考慮的作法。

除非 hacker 偷倒 token, 還能偽造你的 IP, 或是 device unique ID 等等，否則你這作法相對的就更安全
了，不用花太多額外成本，就能阻擋掉大部分的惡意攻擊對象。



# JWT (Json Web Token)

最前面的前言，說過我的想法，不一定什麼都要自己從頭做。但是有機會的話自己試著做一次 POC，對了解問題
是很有幫助的。上面貼的 100 行左右的 ```TokenData``` / ```TokenHelper``` 就是這個目的之下寫出來的，但是當你真正
要正式上線使用的時候，找一套使用的人多，工具及語言支援廣泛的套件來用，是比較合適的。

這邊我推薦的，就是熱門的套件: [JWT - Json Web Token](http://jwt.io)
JWT 是什麼? 能幹嘛? 其實前面你都看懂的話，那就都講完了! 唯一不同的是他的格式是有 RFC 規範的。我從官網
截一張圖來說明:

![示意圖](/wp-content/uploads/2016/12/apitoken-slides20.png)

他的格式區分為 header, payload, signature 三段, 有標準的套件可以產生 & 解碼，其中加密演算法及強度等
也都可以自由控制。

支援的工具及平台也很廣泛 (這就是土炮的方案最不足的一環了)，大概現在還有人在用的語言都有支援... Orz..
官網 > Libraries 就可以看到支援的清單，.NET, Java, Python, Node.js, JavaScript, Perl, Ruby...
就不一個一個列下去了。

本來我想把上面的 sample code 改一個 JWT 版本的，不過感覺很多餘... 一來 Token 的用法，其實不用改就
可以表達得很清楚了。再者如果是要示範 JWT 的語法，我講應該不如官網講得清楚 @@

所以我就用官網的資源代替了，想進一步了解的可以參考 [這邊](https://jwt.io/introduction/):

這篇看完，或是看完這篇前面 10 min 的影片大概就會用了



# 延伸應用

其實，看似很困難的密碼學，包裝成 Token, 再搞懂原理後其實還蠻實用的。我舉兩個我常用的應用方式，不論你
是自己土炮，或是用 JWT 都適用!


## 1, 軟體的啟用序號

第一個就是軟體的啟用序號。過去軟體往往都花很多心思在搞定這問題，搞了一堆複雜的機制，最後沒擋到盜版，卻
苦了合法的使用者...。其實用了數位簽章，序號本身就很難破解了啊，強度夠的話理論上是不可能的，除非有人把
private key 流出來..

![示意圖](/wp-content/uploads/2016/12/apitoken-slides23.png)

做法很簡單，你把授權的資訊當作 ```TokenData```, 最後加上簽章，整串就是啟動序號了。軟體啟動時只要驗證過無誤
再按照 ```TokenData``` 上的描述，啟用對應的功能跟期限就可以了。Public Key 怎麼拿? 既然都是 publc key, 那就
直接放到 code 裡面就可以了。

不過這樣不代表萬無一失喔，這只代表序號本身是夠安全的...，如果我直接反組譯，跳過檢查的 code 還是沒輒。
更 X 的是我另外產生一組 public / private key, 換掉 code 裡面的 public key, 之後我就可以拿造假的
private key 產生新的授權...

如果你面對的對手是有能力改 source code or binary code, 那這部分就要另外傷腦筋了。正規的解決方式是:

你編譯出來的 code 也簽章就好了~ 這個各大開發工具，各大平台其實都支援了。最簡單的例子，手機 APP 就預設
都採取這種做法了。你必須用自己的 key sign 過後的 APP 才能上架，原理也是相同。兩者合併使用就萬無一失了。



## 2, 雲端分散式的系統驗證

牽扯到雲端、分散式系統、SOA、甚至是微服務 (microservices) 都會有類似的議題:

1. 哪些服務是合法建立的? 是可以信賴的?
1. 那些服務可以使用哪些其他網站的服務?

這邊一樣可以用同樣方式解決。我的概念是: 把每個服務當成一個點，服務跟服務之間若允許使用，就會有個箭頭 (線)。
每個點都要產生一組 SiteToken 給他，用來驗證 site id (authentication), 每個線都要產生一組 ServiceToken 給他，
用來驗證用來驗 authorization.

畫張示意圖，如下, 紅字代表 token 裡面要存放的資訊:

![示意圖](/wp-content/uploads/2016/12/apitoken-slides25.png)

每個 site 都有自己的 site token, 綁定 site id 跟 site url, 因此 site id 就是無法偽造的了，也無法把這服務架在
未被授權的 URL。服務端被呼叫前，只要先檢查 service token 的兩端 site id 是否正確 (身分驗證)? 通過後再
驗證 service id 是否符合 (服務授權)? 都通過後就能直接提供服務了。就如同前面的範例 SessionToken，你可以
按照 service token 裡面的資訊決定要提供什麼層級的服務。

這一切的一切，你只要做好一件事情: 保管好你的 private key, 所有的 token 都由你親自產生提供給系統維護者就可以了。
這樣你至少就可以擋掉未經授權的使用者，或是有人架設私服來使用你的服務了。




# 以下開放 Q & A:

這是在當天讀書會有人問到的問題，不過當場沒有回答到，我在這裡佔點篇幅補充一下:

Q: **有人問到，我講的用 private key 加密，用 public key 解密用反了。應該是 public key 加密，private key 解密才對。**

A: 其實兩種方法都可以。RSA 只有要求用哪個 KEY 加密，你就要用同一對的另一個 KEY 去解密。
兩種都有不同的使用時機。我舉幾個例子:

1. X 要寄私人信件給 Y，這是機密的信件，X 只想讓 Y 看的到內容，其他人一律不給看。  
這時正確的做法，就是 X 拿 Y 的 public key 加密後寄給 Y。因為全世界只有 Y 手上有他自己的 private key, 所以
這封信只有 Y 能解的開。

2. X 要張貼公告給所有人，要證明這公告是 X 親自送出的。  
這時正確的做法，是 X 用自己的 private key 替這公告加密。其他任何一個人只要拿 X 的 public key 解密，
能解開就代表這公告是 X 發出的無誤。如果公告內容太龐大，可以先把公告內容化簡為 Hash, 再針對 Hash 加密
即可。  
針對 Hash + 加密的作法，其實也就是我們講的數位簽章。

3. 極機密的信件，例如 FBI 要送指令給特務... 要確認訊息是 FBI 發出的，而且要確認只有指定的 SPY 能解讀。  
這時正確做法是，合併使用兩者的 KEY 就可以了。  
FBI 拿自己的 private key 加密訊息，再拿 SPY 的 public key 加密第二次。SPY 收到訊息後，拿自己的 private key
解密，成功後再拿 FBI 的 public key 解密。  
只有發訊息者跟收訊息者，兩邊都是正確的，才有可能完成這整個程序。

所以，不同情況下有不同的應用，用在 Token 的情境時，用 private key 加密是正確的作法... :D 


# 結論

安全問題一直很頭痛，分散式的安全更頭痛。微服務架構很強調 "去中心化"，對於做法的正確性就更講究了。
這種情況下架構的正確性是第一要務，千萬不要自己硬搞一些奇奇怪怪自以為安全的機制啊，多用標準的演算法
以及 framework 才是上策!






# Reference

[線上讀書會](https://www.facebook.com/groups/207139586323090) 的 [錄影](https://www.facebook.com/andrew.blog.0928/videos/345280552513896/):
<iframe src="https://www.facebook.com/plugins/video.php?href=https%3A%2F%2Fwww.facebook.com%2Fandrew.blog.0928%2Fvideos%2F345280552513896%2F&show_text=0&width=560" width="560" height="315" style="border:none;overflow:hidden" scrolling="no" frameborder="0" allowTransparency="true" allowFullScreen="true"></iframe>
https://www.facebook.com/andrew.blog.0928/videos/345280552513896/


SlideShare [投影片內容](http://www.slideshare.net/chickenwu/api-token?qid=7bd09d0a-587f-4ed6-826d-d12c71f0b252&v&b&from_search=1):
<iframe src="//www.slideshare.net/slideshow/embed_code/key/KtCTtyKgN5r20n" width="595" height="485" frameborder="0" marginwidth="0" marginheight="0" scrolling="no" style="border:1px solid #CCC; border-width:1px; margin-bottom:5px; max-width: 100%;" allowfullscreen> </iframe> <div style="margin-bottom:5px"> <strong> <a href="//www.slideshare.net/chickenwu/api-token" title="API Token 入門" target="_blank">API Token 入門</a> </strong> from <strong><a target="_blank" href="//www.slideshare.net/chickenwu">Andrew Wu</a></strong> </div>

http://www.slideshare.net/chickenwu/api-token?qid=7bd09d0a-587f-4ed6-826d-d12c71f0b252&v&b&from_search=1


GitHub [範例程式碼](https://github.com/andrew0928/MeetUp.ApiTokenDemo):
https://github.com/andrew0928/MeetUp.ApiTokenDemo
