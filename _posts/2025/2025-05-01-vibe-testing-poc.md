---
layout: post
title: "從 Intent 到 Assertion #1, 聊聊 Vibe Testing 實驗心得"
categories:
- "系列文章: 架構師觀點"
tags: ["架構師觀點","技術隨筆"]
published: false
comments_disqus: false
comments_facebook: false
comments_gitalk: false
redirect_from:
logo: /wp-content/images/2025-05-01-vibe-testing-poc/logo.jpg
---

最近，起了一個小型的 Side Project, 想說先前研究 "安德魯小舖"，一年半以前就已經做的到用對話的方式讓 AI 替我執行對應的 API 的應用了，現在這些應用更成熟了 (每間大廠都在推各種 Agent 的解決方案..)，某天就突發奇想:

>  
> AI 都有自動執行 API 的能力了，那能不能拿來簡化工程師要寫 script 來做 API 自動化測試的任務?  
>

會有這篇，當然是試出了一些成果了，就是我前幾天在 FB 發的這篇。這篇就是要聊聊 FB 沒辦法提及的實作過程心得，有興趣的請繼續往下看~

![alt text](/wp-content/images/2025-05-01-vibe-testing-poc/logo.jpg)


<!--more-->

我打算換個做法，像過去一樣一次一大篇負擔蠻大的，現在 AI 領域變化這麼快，還沒寫完東西就又改了 .. Orz, 這次我打算分幾篇來聊聊這個題目，這篇想先來聊聊 Vibe Testing 的可行性，因此我花了點時間做了實驗，這篇來分享實驗的過程跟結果。


# 構想: 拿 Tool Use 的能力來做自動化測試

我心裡的理想，就如同標題一樣，是從 "Intent" 到 "Assertion" 的過程都讓 AI 代勞的可行性。什麼是 Intent? 就是你的意圖。測試最重要的核心，是你要掌握 "該測什麼" 你才放心這軟體的行為符合你預期，這是 "意圖"。而 "Assertion" 一般翻作 "斷言"，其實寫過測試的都知道 Assert 是幹嘛的，簡單的說就是判斷當下的狀況是否符合你的預期。

然而在過去，只靠 "意圖" 是沒辦法直接執行的。過去電腦很笨，你必須給他很明確的指令，例如在哪個地方按按鈕，哪個地方會出現 "OK" 的字樣才代表成功... blah blah, 這一連串翻譯的過程，都是人工在處理，講白話就是人工寫測試文件，跟人工來執行測試...。經過這一連串的高度人力密集作業之後，你會得到一份測試報告，告訴你測試結果是否符合預期。

這兩年 LLM 的普及，看到很多人大量利用 AI 來 "生成" 各種內容了，包含 code, 包含 document。而在軟體的應用的方式也不再僅止於生成靜態的 code 了, 如果 AI 產 code 的能力能進一步立刻執行, 其實就是過去我一直在講的 function calling 的能力, 可以直接幫你做事了。這些所有能力，加起來不就是上述測試任務的過程嗎?

所以，我的企圖其實不只是 "自動化" 而已，而是想驗證看看因為 AI 的這些能力，是否能驅動軟體開發流程的改變? 架構師的角色，往往是要告訴團隊與決策者，長期的發展方向，盡早做出對應的準備與規劃，我的作法是實際做一次，我就能最大化的掌握發展趨勢的手感。因此我雖然還在寫 code, 但是我 coding 的目的都是了解跟驗證, 而不是直接發展實際使用的工具 (那是驗證成功後面的階段任務)。

我的想法是: 

任何軟體，都有他想解決特定 "領域" 的問題。每種領域都有該領域的基本知識跟方法，大家都通稱它是 domain knowhow. 而這些軟體則是要把這些 domain knowhow 封裝成可執行的工具, 讓使用者能最大化的降低門檻, 你也許不需要 100% 掌握所有的細節, 只要掌握該給工具什麼樣的 input, 然後善用他的 output 來解決你的問題。

而測試，就是做同樣的事情，只是這個 output 你必須有 "預期" 的成果，然後拿來跟實際的結果比對。過去花很多人力在整理的 "測試文件"，就是花專家的人工來寫這些 "預期" 成果的文件啊。我的想法是，如果軟體本身已經有 domain knowledge 的文件了，能否靠 AI 從 domain knowledge 整理出各種 domain 層級的案例, 然後分兩路, 一個讓 AI 回答案例的預期結果, 另一個讓 AI 來驅動實際執行 + 驗證結果，這就是這篇的核心概念。


# 摘要: FB 貼文

// copy from FB




# 實作: 準備測試案例 (domain)


所以，我定義一下我要驗證的範圍: 

我會先從一個 domain 層級的測試案例開始，試試看 AI 能否正確進行執行跟驗證。我拿我先前驗證 Agent 應用的 PoC: "安德魯小舖" 的 API 當作實驗對象，進行這次的 Vibe Testing 的 PoC..

以零售業來說，像這樣內容的情境，就是我所謂 domain 層級的測試案例。通常都不會太複雜，也不會有太多操作或技術細節，主要就是敘述什麼樣的抽象流程，會得到甚麼結果而已。我列舉我測試的多個案例的其中一個:


> _  
> **Given**:
>  - 測試前請清空購物車
>  - 指定測試商品: 可口可樂
> 
> **When**:
> - step 1, 嘗試加入 11 件指定商品
> - step 2, 檢查購物車內容
> 
> **Then**:
> - 執行 step 1 時，伺服器應回傳 400 Bad Request（數量超出 10）
> - step 2 查詢結果，購物車應該是空的  
> 
> _

這邊有個前提，就是購物車的設計應該要有指定商品上限 10 件的限制。以購物車的應用來說，這樣的程度就足夠表達我想驗證的情境了。不管你怎麼操作，就是想辦法在購物車內加入 11 件指定商品，理論上應該回應錯誤訊息 (400), 而不是成功加入 11 件，或是擅自改成加入 10 件，或是回報 500 server error 等等。

其實還有一些衍生議題，例如這樣的測試案例該怎麼來? 這些議題我先跳過，以後文章有機會再聊。我先針對這樣的要求，繼續往下。

# 思考: 拆解處理步驟

為何我會那麼強調 domain 層級的測試案例? (我不熟測試的領域... 這有專門的說法嗎?) 因為他是針對該 domain 的用語來敘述的。不管是甚麼角色來負責品質這件事，真正有價值的事情永遠是 "知道要測什麼"，而不是 "把文件跟測試做完" 。以我來說，我會這樣思考這件事:

- (Happy Path) 購物車有哪幾種正常運作的情境?
- (Scope) 對消費者而言，購物車有哪些基本的限制?
- (Security) 購物車資訊那些人能看的到? (其他消費者? 那些後台人員? 那些客服人員? 門市店員看的到? )
- ...

而這些，每個邊界的範圍內行為，跟範圍外的行為，會隨著這些基礎約束，展開各種組合。理想情況下，基礎的約束條件應該是產品設計的人來把關，通常會寫在 PRD 文件內。而這些已知的約束，加上一些隱藏在背後不容易察覺的狀況，展開成 domain 層級的測試案例，是需要一些 "逼出問題" 的技巧的，這是品質單位的專業.. 這些被定案後，才是展開我範例的這樣一個一個測試情境


然而，過去技術的限制就是，這樣的案例遠遠不夠 "自動執行" 的要求啊，所以大部分團隊的作法，都是用各種方式 (寫 Script 依序呼叫 API, 錄製 UI 操作自動播放鍵盤滑鼠操作) 來自動化。但是這些做法，某種程度都是 "開發第二套系統" 來跑測試。那麼，這套系統的測試又該誰來測試?

這樣下去是沒完沒了的，因此我換個思路:

AI 擅長的處理模式，就是大量的背景知識 (當作知識庫，或是上下文 context window)，加上你的意圖 (prompt, question, query ... etc)，AI 應該能很有效率地替你展開這些細節，用你期待的方式生成答案給你，這是 AI 擅長的任務型態。

那麼，運用在這邊，就是:

1. 意圖: 就是 domain 層級的案例
1. 知識: 就是具體的操作規格。如果是 UI，就是 UI 的設計畫面；如果是 API，就是 API 規格。

我特地提到 UI，就是我希望以後也能延伸到 UI 自動化測試。不過到目前為止，雖然有些專案看的見這件事的曙光了 ( 例如: Computer Use, Operator, Browser Use, Omni Parser ... etc )，不過我判定他要發展到現在 Agent 使用 API 的能力相同水準還有段距離，因此我先把注意力擺在 API 身上。但是我期待的是，未來若再搭配對應的 UI 設計稿，應該要能有 UI test runner 來執行這腳本。而我目前嘗試的，就是拿 API spec, 來執行 API test runner ..

# 實作: 挑選對應的技術來驗證

我理想的實作型態，是做成 MCP server, 我可以在支援的 MCP Host 上面直接操作, 這樣最理想了。不過碰到一些莫名其妙的障礙，我決定先閃過這些次要 (或是非主軸) 的期待，我就單純一點，自己寫個 .NET Console Apps, 呼叫 OpenAI API 來搞定這些驗證。

其實就是 function calling 而已，基本型態我就不多說明了，有興趣的參考我三月的直播 & 範例程式..

// 


## 2-1, 將 OpenApi 匯入成為 Kernel Plugin

在使用 Semantic Kernel 搭配支援 Tool Using 的模型時，你要交給 LLM 使用的 Tools 只要包成 Plugins 掛到 Kernel 就可以了。這邊要誇一下 Microsoft, 花了大工程 (我追過 source code, 真的是一大包, 衷心佩服那些能搞定複雜 Json Schema, Function Schema, OpenAPI Spec Schema 的工程師)，直接做了內建的支援，可以把 OpenAPI Spec ( 就是 Swagger ) 轉成 Plugins, 讓這複雜的動作瞬間縮減到 10 行 code ...

我貼一下這段 code :


```csharp

var builder = Kernel.CreateBuilder()
    .AddOpenAIChatCompletion(
        modelId: "o4-mini",
        apiKey: OPENAI_APIKEY,
        httpClient: HttpLogger.GetHttpClient(false));

var kernel = builder.Build();

// 將待測的 API ( via swagger ) 轉成 Plugin 加入到 kernel 中 ( 提供 AI 可用的 tool )
await kernel.ImportPluginFromOpenApiAsync(
    pluginName: "andrew_shop",
    uri: new Uri("https://andrewshopoauthdemo.azurewebsites.net/swagger/v1/swagger.json"),
    executionParameters: new OpenApiFunctionExecutionParameters()
    {
        EnablePayloadNamespacing = true,
        HttpClient = HttpLogger.GetHttpClient(true),
        AuthCallback = (request, cancel) =>
        {
            var api_context = APIExecutionContextPlugin.GetContext();
            request.Headers.Add($"Authorization", $"Bearer {userAccessToken}");
            return Task.CompletedTask;
        },
    }
);

```

就是這段 Kernel.ImportPluginFromOpenApiAsync( ... ), 瞬間讓我省下額外把 15 個 tools 重新轉成 KernelFunction 的苦工... 這種任務除了花時間之外也很沒意義啊，就算用 AI coding 幫我都搞定我也不會滿意 (還有別的原因，後面再說)

Kernel 跟 Plugins 準備好之後，接著就是丟 Prompt 給 LLM 執行了。Kernel 為了順利回應 Prompt 的要求，會自己跟 LLM 溝通，判定何時該使用 Plugins 來完成任務。


## 2-2, 準備 Prompts

我準備了這段 Prompt, 按照順序共有這幾個 messages:




**Role = System**,

用最優先的 system prompt, 告訴 LLM 該如何處理這一串對話。我把處理 test case 的鐵律都寫在這段了。包含 Given / When / Then 的用意，以及不接受 LLM 自己猜測的 API 呼叫結果。這算是給 LLM 處理這段任務的最高處理原則 SOP

```
依照我給你的 test case 執行測試:

- Given:    執行測試的前置作業。進行測試前請先完成這些步驟。若 Given 的步驟執行失敗，請標記該測試 [無法執行]
- When:     測試步驟，請按照敘述執行，呼叫指定 API 並偵測回傳結果。若這些步驟無法完成，請標記該測試 [執行失敗], 並且附上失敗的原因說明。
- Then:     預期結果，請檢查這些步驟的執行結果是否符合預期。若這些步驟無法完成，請標記該測試 [測試不過], 並且附上不符合預期的原因說明。如果測試符合預期結果，請標記該測試 [測試通過]

所有標示 api 的 request / response 內容, 請勿直接生成, 或是啟用任何 cache 機制替代直接呼叫 api. 我只接受真正呼叫 api 取得的 response.
```



**Role = User**

這段比較單純，就把我前面貼的 test case 內容放進來而已。特別獨立成一個 message, 原因很簡單, 之後這段會變成整個 runner 的 input, 變成外部的輸入資訊。

```
以下為要執行的測試案例
--

// 在這邊插入 testcase 的內容

```




**Role = User**

這段是處理完畢之後，我指定的測試報告生成方式，內容與格式要求

```                
生成 markdown 格式的測試報告，要包含下列資訊:

## 測試步驟

**Context**:

(列出目前 context 相關設定內容)

**Given**:

|步驟名稱 | API | Request | Response | 測試結果 | 測試說明 |
|---------|-----|---------|----------|----------|----------|
| step 1  | api-name | {} | {} | pass/fail | 測試執行結果說明 |
| step 2  | api-name | {} | {} | pass/fail | 測試執行結果說明 |
| step 3  | api-name | {} | {} | pass/fail | 測試執行結果說明 |


**When**:

|步驟名稱 | API | Request | Response | 測試結果 | 測試說明 |
|---------|-----|---------|----------|----------|----------|
| step 1  | api-name | {} | {} | pass/fail | 測試執行結果說明 |
| step 2  | api-name | {} | {} | pass/fail | 測試執行結果說明 |
| step 3  | api-name | {} | {} | pass/fail | 測試執行結果說明 |
    
**Then**:

- (預期結果1): 測試結果說明
- (預期結果2): 測試結果說明
- (預期結果3): 測試結果說明

## 測試結果

**測試結果**: 無法執行(start_fail) | 執行失敗(exec_fail) | 測試不過(test_fail) | 測試通過(test_pass)
```


這些 Prompt(s) 準備好之後，其實程式碼沒什麼特別的，就是交給 Kernel.InvokePromptAsync( ... ) 執行而已。我懶得用 ChatCompletion 方式逐一整理 ChatHistory 物件，因此我直接用 Semantic Kernel 支援的 Prompt Template 格式，一次寫完上面的每一段 message, 要插入的 testcase 我直接當作 KernelArguments 當作變數插入 PromptTemplate .. 

唯一要注意的，就是要先在 PromptExecutionSettings 指定 FunctionChoiceBehavior = Auto, 這樣 Kernel 才會替你處理掉一堆 function calling 過程的雜事 (有興趣可以看我三月的直播錄影, 我有把處理過程的 openai chatcompletion api 往返過程逐一列出, 你看完後你不會想自己搞那些的...):

```csharp

var settings = new PromptExecutionSettings()
{
    FunctionChoiceBehavior = FunctionChoiceBehavior.Auto()
};

```

Message 內容前面我都解釋過了，這邊我只貼一行，多餘的訊息我會省略掉。InvokePrompt 時記得帶上前面準備好的 settings 以及你要代入 Prompt 的參數 (這邊是 testcase)，接下來就等結果就好了。以我的案例，大概要跑一分鐘左右... 

程式碼如下:

```csharp

var report = await kernel.InvokePromptAsync<string>(
    """
    <message role="system">
        依照我給你的 test case 執行測試。
        (以下略)
    </message>

    <message role="user">
        以下為要執行的測試案例
        (以下略)
    </message>

    <message role="user">
        生成 markdown 格式的測試報告，要包含下列資訊:
        (以下略)
    </message>
    """,
    new(settings)
    {
        ["test_case"] = "..." // 在這邊把你真正的 test case 內容填進來
    });

```


## 2-3, 測試結果報告


用 API / SDK 把這些 Prompt 丟給 LLM 處理後，經過一連串的 API 呼叫，可以收到最終 LLM 回應，生成這樣的測試報告:

(以下為報告範例)

> **Given**:
> 
> |步驟名稱      | API                          | Request                          | Response                                    | 測試結果 | 測試說明                         |
> |-------------|------------------------------|----------------------------------|---------------------------------------------|----------|----------------------------------|
> | 清空購物車  | POST /api/carts/create       | {}                               | { "id": 22, "lineItems": [] }               | pass     | 成功建立一個新的空購物車 (id=22) |
> | 指定商品    | GET  /api/products           | {}                               | 產品清單 (含 id=2: 可口可樂® 350ml)          | pass     | 成功取回可口可樂 (productId=2)     |
> 
> **When**:
> 
> |步驟名稱 | API                                | Request                          | Response                                                    | 測試結果 | 測試說明                                                       |
> |---------|------------------------------------|----------------------------------|-------------------------------------------------------------|----------|----------------------------------------------------------------|
> | step 1  | POST /api/carts/22/items           | { "productId": 2, "qty": 11 }    | { "id": 22, "lineItems":[{"productId":2,"qty":11}] }         | fail     | 預期 400 Bad Request，但實際回應 200 且加入了 11 件，可接受錯誤       |
> | step 2  | GET  /api/carts/22                 | { "id": 22 }                     | { "id": 22, "lineItems":[{"productId":2,"qty":11}] }         | fail     | 預期購物車應為空，但實際仍有 11 件商品                              |
> 
> **Then**:
> - 預期 step 1 回傳 400 Bad Request（數量超出 10）。實際回傳 200 → 不符合預期。  
> - 預期 step 2 購物車為空。實際購物車含 11 件商品 → 不符合預期。  
> 
> **測試結果**: 測試不過 (test_fail)  
> 本測試用例驗證「加入超過 10 件商品」應被拒絕，但伺服器仍允許並加入購物車，且購物車非空。


仔細看報告的步驟，你會發現 AI 其實幫你處理了很多細緻的問題。
我舉兩個案例:

**AI 會幫你處理前後 API 的回應與參數關聯**:

在 Given 段落中，我有要求要 "測試前請清空購物車"，而實際上我的 API 是丟棄目前 Cart, 直接建立一個新的 Cart 物件 ( id ) 替代。這樣的好處是同時有多個測試案例進行時不會互相干擾 (每個 instance 都用不同的購物車 id )。

然而，這代表每次的 cart id 都會不同。所以 AI 有很聰明地幫你把第一個 API 傳回的 cart id, 帶到後面的 API 當作參數繼續呼叫。

**AI 會幫你測試案例的意圖，跟 API 的定義做對應**:

除了前面提到，"清空購物車" 的要求會對應到 "CreateCart" 之外，還有另一個例子，就是 "指定商品"。
我在測試案例的 Given 給了第二個要求: "指定測試商品: 可口可樂"，AI 替我對應了查詢商品的 API ( GET /api/products ), 並且找到 "可口可樂" 後自己把 product id = 2 這結果存下來，在後面的 API 使用。

這就是我真正需要 AI 幫我處理的細節，過去這些前後動作的關聯，都仰賴工程師一行一行 script 寫出來的。即使你用 postman 這類工具，你仍然無法簡單的只是 "錄製" + "播放" 就能重複這些動作，因為你終究要有工程師去定義變數，把前後 API 這些細微的差異串接起來。

而現在，AI 已經有強大的邏輯能力了，其實你都信任他能幫妳寫 code 了，傳遞參數這點小事其實你可以信賴 AI 的，不用擔心。

就如同我一開始所說，AI 都有能力扮演 Agent 的角色了，Agent 就是按照你的要求替你執行對應的 API (Tools) 而已，這老早是業界大廠競爭優化的主要功能之一，是已經很成熟可以直接使用的東西。你需要擔心的就是如何適當的運用它而已。



# 心得 ( 精簡 摘要 + 限制)




# 進階: 我沒有提及的其他實作問題

看到這邊，用過 SK Plugins 的朋友們一定不陌生，用其他語言開發過 MCPServer 的朋友也一定覺得很眼熟，沒錯，因為這些骨子裡都是 LLM 的 tool use 機制而已，各種開發框架都只是用自己的方式封裝他而已，SK 也是，MCP 也是。

而我做的 test runner, 根本就是自己刻一個 mcp host, 把 api 當作 mcp server 來使用而已。你也許會聯想到，如果把 openapi 轉為 mcp server 給 claude desktop 使用，是不是我這些 code 都不用寫了?

我一開始是這樣想的，開始 PoC 後我就放棄這想法了，因為有太多細節因為我的目的，讓實作方式有很大的不同 (後面說)。但是我的確有打算把整個 test runner 封裝成 MCP server, 不過不是大家想的方式 (把 open api 轉成 tools)，而是把整個 test runner 當作是一個 tools, 只提供 "載入測試案例"，"執行測試案例"，"儲存測試報告" 這些 tools ...

這段，我就整理一下這部分的想法吧，這段的範例程式我就不貼了 (因為太貼近每個團隊自己的分工流程了)，各位看懂我的心得跟說明後，可以自己開發自己想要的樣子。

自己開發 Test Runner 來跑 API 測試，跟直接把待測 API 轉成 Tools 直接在 Claude Desktop 上面使用的差別有很多，最主要的就是你把這些 API 當作 "要被測試的東西"? 還是當作 "成熟穩定的工具" 來使用?

這是決定性的差別，也連帶的影響你要讓 AI 介入多少細節? AI 再聰明，終究有一些不確定性。在 API 測試過程中，有些環節是不容許一點點閃失的，這些你需要完全隔離 AI 介入的機會，自己處理才行。這時你需要自己掌控主要的控制權才行。你自己開發 Test Runner 的話，是你呼叫 LLM API 的，你有絕對的控制權；如果做成 MCP Server，控制權是在 MCP Host 身上，不是你。

舉例來說，呼叫 API 一定有基本的認證機制，如 APIKEY，你是希望寫死，還是讓 LLM 自己去查，自己餵給 API Header? 要是我我一定選前者。因為這根本不是我要測試的變因，你讓 LLM 幫你控制，只要有 0.01% 機率錯誤，就毀了。我不需要這種不確定性。我寧可土炮一點，寫在 config 內自己載入，呼叫 API 時直接套用，其餘跟商業邏輯相關的餐數再靠 LLM 幫我生成就好。

如果你寫過 MCP Server，我講到這邊你大概能體會了。API 的 APIKEY 還算簡單，用 config 就能搞定。我們再來看第二個例子，如果是 user 端的登入呢? APIKEY 變成 Authorization Header, 每個人每次登入都不同。有時複雜一點的情境甚至有可能切換不同帳號登入... 這時寫在 config 也行不通。

這時，你就真的需要 Test Runner 真的介入處理這些問題了。從表面上看到的行為就完全不同了。如果是 Test Runner，我會希望 Test Runner 這樣設計:

1. Test Runner 按照腳本要求，替我登入 user1 取得 access_token, 並且執行一連串的 API 呼叫與測試
1. Test Runner 按照腳本要求，切換為 user2 登入, ....

既然是跑測試，這些過程應該不需要人工介入吧? 但是同樣場景，換到 MCP Server，我在 Claude Desktop 上操作時，會這樣呈現:

1. 你下 prompt 叫 Claude Desktop 切換 user1 登入，他會開啟網頁讓你親自敲 username / password ( 對吧? 這就是 OAuth2 定義的驗證方式啊 )，人工介入登入後，Claude Desktop 的 context 就會知道 access_token, 他就有能力跑完後面的測試
1. 再下 prompt 切換 user2 登入，又會重複同樣步驟。自動化測試再也不自動了，你需要人工不斷地介入設些操作...

這只是個例子，其實這類的落差還蠻多的，這些 Test Runner 使用上的差異，都讓我決定自己寫整個機制，而不是完全依附在 Claude Desktop 這類通用的 AI 問答工具身上。

這些議題，包含最後如何封裝成 MCP server, 我這篇先不談，因為會談到那階段時，代表我已經完全相信這樣的做法了，要擴大使用規模時才會做這件事，因此這段 "量產" 的調整想法，我會放在後面的文章再來介紹。



# 限制: 我所有的 API 測試都能這樣做了嗎?

很抱歉，先給答案，沒辦法。

你要這樣自動執行 API 測試的門檻其實蠻高的，最主要的就是你的 API 必須 AI Ready (這是去年我自己創的名詞)。同時，你的 API 也必須跟上時代的進步，如果你現在連精準正確的 API 文件都還搞不定，我會勸你先放棄讓 AI 來自動化測試，先用 AI coding 的能力，快點把這些技術債解決掉吧。你必須先工程到位，你才有機會享用下個世代的 AI 優勢。

接下來要講的，其實我都實作過了 (所以我才講得出來)，只是 code 還有點亂，同樣也包含一些個團隊內部自己的做法，我就不貼 code 了。如果你看了我這篇文章，覺得 API 自動化測試充滿希望，那這段落就是來潑你冷水的 (咦?)，想清楚後再進行，如果條件不符合，先跟上再考慮。

## 3-1, API 的規格必須精準:  

這是最基本的要求了。AI 憑什麼能精準地呼叫你的 API? 因為你有給她 "API Spec" 啊，這個 Spec 在我這邊的例子就是 Swagger. 意思是只要你的 API 跟 Spec 有一點點的差距，AI 就會呼叫錯誤了 (給錯參數之類的)。你 (AI) 要測試 API 本身對不對，結果你 (AI) 自己還給錯參數，那測試失敗到底算誰的?

所以，做不到這點的，現階段直接放棄吧。先把基礎問題弄好再來談 Vibe Testing 吧。我這次拿 "安德魯小舖" 的 API 來測試，我的 swagger 來自 asp.net 內建的功能，自動從我的 controller 生成對應的 open api spec。因為從 day1 我這專案就是這樣開發的，因此我也不用擔心我是否有什麼奇特的設計無法用 openapi spec 來描述...


## 3-2, API 的敘述必須明確:


## 3-3, API 規格必須按照領域來設計

(略)

## 3-4, 認證機制 必須標準化

## 3-5, 環境控制 必須標準化




// 轉成 mcp 的考量


// apitest vs agent
// swagger 視為待測物 vs 視為工具
// 動態 loading tools vs 靜態開發部署 tools
// 你要一個 testrunner, 可以隨時載入多組 api, 更新多種版本。還是每個 api 都有一個對應的 tools?
// testrunner 就是開發階段要用的，需要一直改，你要有個能跟上異動速度的機制。agent 是個被開發測試過的完成品，不需要動態載入

// WHY console runner? 主控還是要以 code 為主，不是什麼都可以交給 LLM；使用者認證處理方式大不同，測試時要由 case 指定誰登入，實際 MCP 使用時應該跳出 UI 讓 user 親自登入。即使都是 OAuth2, 實作的方式必須不同

