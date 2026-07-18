---
layout: post
title: "AI Era, 架構師的注意力該用在哪裡?"
categories:
- "系列文章: 架構師觀點"
tags: ["架構師觀點","技術隨筆"]
published: true
comments_disqus: false
comments_facebook: false
comments_gitalk: true
redirect_from:
logo: /images/2026-07-08-devopsdays-aiera-architect-showcase/image.png
---


![alt text](/images/2026-07-08-devopsdays-aiera-architect-showcase/image.png)

今年六月底, 忙完兩場演講 (DevOpsDays Taipei 2026, Generative AI 開發者年會 2026), 把我上半年的所有研究都交代完了｡ 過程中得到不少現場參加的朋友給我的回饋, 最熱烈的是 DevOpsDays 會後, 找我聊我示範的 side project: Andrew Shop 的執行方法｡ 其實這本來只是單純的架構設計難題驗證而已 (交易系統, 要標準化, 又必須滿足高度客製化的要求), 只是我 "順手" 用了我覺得 AI coding 應該要有的樣子來執行而已｡

這篇, 我換了另一個案例當作練習, 我的系統有很多操作需要計費, 而計費的機制我希望做的像 Claude Code 的使用量限制那樣的規則, 有每 5 小時, 也有每 7 天的額度限制, 超過額度可以選擇從儲值的點數扣除｡ 系統上的要求則是我只能用 SQLite, 設計上我想盡量降低 database 處理交易的負擔｡

我改用這個案例, 重新用我在台上分享的流程來做一次, 並且把過程記錄下來, 讓大家親自體驗跟直接不經思考就把需求扔給 AI 開發的差別｡ 這些過程跟步驟, 我在台上其實沒機會好好說明 (畢竟我的場合是演講, 不是工作坊), 所以我把這段用文章形式放在這裡, 有興趣的人可以參考~

<!--more-->



# 0, 寫在前面


這篇我想表達的觀點是: 

> 架構師 (或是對等的技術決策者) 的主要工作, 已經從親自實作, 逐步轉移到辨識不確定性, 做出決策, 並且把決策固化成 agent 能明確執行與驗證的規格 (護欄) 的過程｡

這背後的想法, 就是把人跟 agent 的分工更清楚明確的定義出來, 最大化兩者的產能｡ 相對於 agent, 人腦是很難 scale out 的, 因此我的做法是盡可能的讓人的部分有效率的運作, 只要 agent 能做的就丟給 agent, 而為了避免丟給 agent 的任務又會回到人的身上, 因此丟給 agent 的任務必須符合基本的結構, 能自循環驗證 + 改善, 而不是需要人一直在旁邊監督｡

這些做法很多人都在講, 但是卻很少看到實際的案例, 所以我自己嘗試過這練習題, 並且把過程記錄下來, 實際拆解步驟直接執行給大家看｡ 我挑了一個大家都很熟悉的題目:

> 我想在我自己系統內模擬 claude code 訂閱額度控制機制 ( 5h / 7d limit ), 如果超出額度則暫停服務, 或是讓使用者選擇儲值 + 扣 credit 繼續使用｡ 這需求如果你自己要實作, 你會怎麼做?

有的人選擇 vibe coding, 自己不碰任何技術端的決策, 也不 review code 或是架構設計, 只描述外部需求, 認為 AI 已經強大到足以完成任務｡ 這是一條路線, 要賭的是你不碰的技術端決策到底重不重要? 若你放掉重要的決策沒有把關, 那案子高機率會失敗收場｡

我的選擇反過來, 我要面對的題目都是大型系統, 有很多環節是沒有錯誤的空間的; 架構師的天職就是要避免技術決策的失誤, 盡早的導正方向來確保案子能可靠的執行, 因此我如果事先對這題目有些想像, 我會在腦袋裡描繪出系統該怎麼運作的設計細節, 然後讓 agent 替我驗證, 補足細節, 完成設計; 如果我沒辦法做到這樣的話, 也可以局部讓 agent 發揮想法, 快速驗證並且做出選擇, 決定最後的設計｡ 

這件事若你還能將之拆成幾個獨立的步驟, 再把這些細節定義成邊界規格, 再個別讓 AI 完成組裝, 那成功率就更高了, 失敗的風險也更低, 這是另一條路線｡



這些能力是需要練習的, 如果你一開始什麼都丟給 agent 處理了, 那你會在什麼地方練習? 這是你要為你自己負責的｡ 這篇文章我就是想給大家一個練習的案例, 我拿這個題目做了幾個實驗, 用同樣的起始規格 (黑箱規格, 只從外部觀點來描述系統運作的要求, 不涉及系統內部的運作方式), 用同樣的模型與工具設定 ( 都用 Codex, 模型選擇 GPT5.5 + extra high ), 分別嘗試了 vibe coding mode 跟 architect mode 兩種方式, 來看產出的差異, 同時追加額外的對照組, 改用 Claude Code + Fable 5 + Ultracode 當作參考, 證明模型的能力已經不再是最關鍵的影響因素｡



# 1, 定義需求規格

這次題目, 規則很簡單, 我假設的情境是: 我的系統內需要頻繁的處理各種任務, 而這些任務是計費的｡ 例如執行一次報表要扣 10 點, 而更新一筆資料要扣掉 3 點這樣的操作｡ 現在 claude code 或其他的 agent, 大家都不約而同的用訂閱制度, 搭配限制使用量的機制 ( ex: 每 5 hours 以及每 7 days 的使用量限制, 以及規範的時間會定期 reset 的機制 ), 同時也補上了不靠訂閱, 能夠額外儲值扣點的設計 ( ex: 額外儲值 1000 點, 當訂閱的限制到達時可以讓使用者選擇是否扣除儲值點數 )

我想基於這樣簡單的規則, 附加了一些系統層級的要求, 包括:

這些點數消耗是要留下交易記錄的, 事後必須拿來查帳, 對帳使用 (點數消耗記錄-收入, 必須跟服務被呼叫的記錄-成本 數字能對照, 代表每一筆支出都有正確被對應)｡ 同時我也另外給了嚴格的要求, 我沒有使用功能很完善的資料庫來支援交易處理, 只有 SQLite 這種層級的 embed database, 在設計上要避免過度依賴資料庫的交易處理能力｡

於是第一版規格就這樣完成了, 以下所有操作, 若沒有特別說明, 我都是在同樣的環境 (  codex + gpt5.5 xhigh + fast mode ) 執行的 , 用這段 prompt 產生了這次的規格:


```
(prompt)

替我準備第一版規格
這版規格只描述外在能觀測的行為跟結果, 不要描述任何系統內部的實作跟設計
我先簡述我的期待, 替我轉成正式的規格跟驗收案例

--
我有我自己的計費服務使用量管制機制, 我想要有個基於 database 運作的 rate limit, 行為就比照大家熟悉的 claude code 那樣
對於 credit 的 usage, 有 5h 的窗口限制, 有 7d 的窗口限制
超過有額外 extra pool 的機制

單位都用整數, credit 來計算

我想要在單一 database 管理多個 user 的 subscription 用量
我希望架構越單純越好, 可以的話我希望能在入門等級的資料庫就能運作 (sqlite), 並且有良好的結構設計, 帳務出現異常時能夠有完整記錄回溯

設計考量, 帳務絕對不能出錯這是基本的, 但是對我而言最優先的是建置成本, 能使用的 infrastructure 越精簡越好


```

產出的結果我就不貼了, 我放 github 連結: [spec/subscription-credit-rate-limit-v1.md](https://github.com/andrew0928/AndrewDemo.AgentRateLimit/blob/e60674f406852d778ab747612c1d4673948603d0/spec/subscription-credit-rate-limit-v1.md)



整個專案我都放在 GitHub 上了, Repo 的結構我後面再說明, 連結我擺在這裡, 歡迎大家自己拿回去研究: [AndrewDemo.AgentRateLimit](https://github.com/andrew0928/AndrewDemo.AgentRateLimit/)







## 1-1, 我的實驗方法

為了做這次的驗證, 我總共嘗試了三個方法, 前面建立的初始規格, 加上我自己設置的基本 Harness 設置, 就是這個 Repo 的初始 commit ( 我標上了 init 這個 tag ), 每一組實驗都是從這個 commit 獨立分出來的 branch. 這個 repo 的 git graph 長這個樣子:

![三個實驗分支的 Git graph](/images/2026-07-08-devopsdays-aiera-architect-showcase/experiment-branches.png)

這個 repo 包含三個額外的 branch, 分別是 ```goal-mode```, ```architect-mode```, ```fable5``` 三個. ```main``` branch 我保留來做報告與彙整資料用, 不包含實作與開發, 可以忽略｡ 我準備這三組實驗的用意, 是要區別用不同的方法來執行同一套初始規格的開發, 我想看看不同方法論開發下來的成果差異在哪, 以及過程差異在哪; 我看了很多人闡述他怎麼用多個 agent 協作 blah blah, 但是沒有太多人交代執行的步驟, 而你若沒有親自做過一次, 你也不會有手感..., 因此我也自己做了一次｡ 

以下我分別說明一下這三個 branch 背後各代表了什麼做法:

**goal-mode**:

這個分支是第一個 vibe coding 的代表, 我直接開啟 /goal 模式讓 codex 一路跑到完成為止, 花了 12m 5s 完成這任務 (如果沒開 fast mode 加速, 那應該要花掉 20m 以上了吧)

```
(prompt)
use dotnet10 and sqlite to implement this spec
```

我仗勢著我有 "完整的規格" (事後證明這遠遠不夠), 就可以無腦丟給 agent 完成後面所有任務, 因此記錄上你只看到一個 commit 就結束了, 實際上也真的只有一個步驟而已｡ 做法說明先到這邊, 成果後面一起看｡


**fable5**:

所有條件都同 goal-mode, 只是這次剛好碰到 Fable 5 重新開放的優惠期, 我就換成 claude code + fable5 ultracode ( 其實只用到 xhigh 而已, 過程並沒有啟用 dynamic workflow ) 來當作第二個對照組｡

我使用的 prompt 完全一樣, 一字不差的直接 copy 上面的案例, 差別只在用了不同的工具跟模型而已, 而這個任務一次就把我 5x 訂閱的 5h 額度用光了, 晾了幾個小時才接續完成, 時間我就不特別記錄了:


```
(prompt)
use dotnet10 and sqlite to implement this spec
```

一樣, 成果也有做出來, 跟我期待的落差後面一起看｡

**architect-mode**:

這就是今天的主角了, 我按照我的節奏一步一步往下確認, 細節後面聊, 過程中藉由跟 agent 的對齊做法跟持續修正規格, 越前面的資訊量越少, 即使需要 review, 都是短短的幾十行 code 而已, 即使如此, 我也是花了最多人力在 review (其他兩組根本沒有 review)｡

整體最有感的是, 拆了幾個階段, 前面花了些時間 review, 但是最後要把 code 寫出來的時候, 其實也是丟了依據 prompt 就一次到位了, 嚴格說起來, 我其實是靠 agent 陪我 vibe architecting ... , 都在補架構相關的規格設計｡ 花的時間最多, 但是這過程我覺得很可靠又有效, 就是我這篇想要聊的主軸｡

這段的做法跟分析, 我直接寫在下一個章節...





# 2. 我的開發步驟說明 (architect-mode)

這個實驗, 整體大概花了我一個晚上的時間, 我把心思花在前面的階段, 不斷的跟 agent 修正我期待的規格跟需求, 跟一般 vibe coding 不大一樣的地方是, 我會親自 review 護欄的內容, 包含切割範圍的 interface code, 以及我預期結果的 unit test code.

這實驗最大的收穫, 應該是我在敘述我對這題目的想法的過程中, 不斷的收到 agent 給我的回饋, 不斷的釐清規格細節跟技術決策的過程. 過去業界常常把 XXX 左移掛在嘴邊, 測試左移, 設計左移... 等等, 不過過去因為開發是最大的瓶頸, 高度耗費人力, 每一種 "左移" 都會碰到角色跟專長的衝突, 你要左移, 人的能力就會需要重新要求, 執行就會有阻礙...

換成 agent 後開始沒這些困擾了 (換上對的 skill 就解決了), 我開始嘗試把各種原本要寫完 code 才能驗證的事情, 往前提到定義規格階段就先讓 agent 替我模擬結果, 這考驗模型的推理能力, 而到了今年 (2026), 我覺得主流的前沿模型已經跨過這道門檻了, 包含 gpt5.4, 也包含 opus 4.7 ...

這流程, 是讓後面步驟能夠高效率並且可靠的執行最重要的關鍵, 因為大部分實作才會發現的盲點, 都被我的工作流程提前在前面階段就處理完畢了:

![architect-mode 的開發流程](/images/2026-07-08-devopsdays-aiera-architect-showcase/architect-mode-workflow.png)


上圖是我實際執行的步驟, 第一步 "黑箱規格" 就是 Init 那包 commit, 是整個過程的起點｡ 

大部分人認知的 "開發" 是真的有程式碼產出, 而我的流程, 則是在 "規格定案" 這步驟後才真正有可執行的程式碼產出, 前面的階段都只是在進行設計與事前驗證而已｡ 這段很吃模型的推論能力, 也很考驗執行者的判斷能力｡

這實驗, 在開發前, 我主要要掌握的是邊界的規格設計, 我需要 agent 產出的是每個邊界的介面規格 (interface, 用 code 表示), 以及介面行為 (用 unit test, 也是用 code 表示)｡ 而開發的部分, 則是要 agent 按照設計, 產出名為 *.core 的 dotnet class library 專案 (只有業務邏輯) 跟名為 *.api 的 dotnet asp.net webapi 專案 (包含非功能性需求). 而最後要部署的方式我也切出來了 ( deploy, 我這邊定義的是最終要交付 docker image + docker compose ), 產出就是可本地運作的 docker file, 跟 compose.yaml. 


當你有能力分清楚他們的邊界在哪, 你就能更清楚的切分邊界, AI 做出來的成果就會越貼近你的期待｡ 因為我按照不同的目標 (業務邏輯, 技術要求, 部署方式) 來切分了, 因此這些需求我都可以個別定義, 可以個別跟不同的專家確認, 累積下來的需求文件也可以個別重複使用, 不需要每個案子都重新定義一次｡ 這過程考驗的是你是否具備 "高度抽象化" 討論跟對焦能力, 切的越明確, AI 的任務就越明確｡ 


再拉高一點來看, 其實做法可以繼續收斂, 我不斷重複的只是這樣的結構:

![規格定義與驗證的 review loop](/images/2026-07-08-devopsdays-aiera-architect-showcase/review-loop.png)
這結構很基礎, 定義了介面, 套用情境來確認是否符合, 若不符合就按照回饋來修正, 不斷循環這個 review loop, 直到符合期待為止｡ 我用這樣的循環, 進一步將業務需求再拆成 (1) code contract, 以及 (2) data contract, 最後才決定驗收範圍並且開始實作, 就是整個專案的進行方式｡

對我來說, 在開發之前先做這些收斂是很值得的, 因為拆解後, 可以大量降低我自己的認知負擔, 每一階段的 review, 都可以降低後面階段的風險, 拆的越精細, 加成效果越明顯｡ 而拆的越細, 前後是否精確維持一致就越重要｡ 在高度要求一致的設計要求下, 我開始發現, 有些規格, 用 code 來定義遠比用自然語言定義有效率的多, 如果你有一個已經到 "母語" 層級的程式語言 (對我來說 C# 就是), 不要客氣, 直接拿他來當作你的規格定義方式｡ 如果很不巧你熟悉的語言跟要開發實作的語言不同也沒關係, 讓 agent 替你翻譯｡ 重點是你要掌握的規格是否精確, 跟你用的語言沒有太大差異｡

因為看到這效益, 我在 DevOpsDays 那場演講, 我才會在台上說:

> Developer 能看懂 Code 是你的特權, 不是你的負擔

這句話我沒寫到簡報裡, 但是我講這句的當下, 用的是[這頁簡報](https://slides.chicken-house.net/s/2026-DEVOPSDAYS?p=26):


![自然語言與程式碼規格的對照](/images/2026-07-08-devopsdays-aiera-architect-showcase/code-as-spec.png)



這剛好是個網路笑話, 也說明了自然語言要敘述精確規格的困難, 尤其是有時你會不知不覺的踩到這陷阱｡ 右邊是用 code 的對照組, 清楚明確, 毫無錯誤的可能｡ 架構師該做的就是這種判斷, 當你需要精確的敘述時, 別覺得拿出 code 來說明是很丟臉的事 (再強調一次, 這是你身為開發人員的特權)

越是這種 "看起來觀念很簡單", 但是不知道怎麼實作的, 你需要的就是實際的案例演練｡ 接下來, 我會在下一段, 把我 architect-mode 的操作過程一步一步記錄下來, 各位可以體會一下我每個步驟都 "解決" 了哪些環節的不確定性｡



# 3, 實際開發過程說明

上一段提到的流程圖, 我心理想的是拆三個階段進行而已:

1. **確認程式碼的邊界**:  
   主要是 .Abstract, 封裝 domain logic 的核心邊界定義, 我會親自 review .abstract 的設計 ( c# code ), 同時用實際的使用案例來檢視這些介面會怎麼被使用, 就是 DX review 的步驟

2. **確認資料庫結構的邊界**:  
   資料庫是這次實作的重點, 因此我特別獨立拉出來, 主要是 database schema, 同時我也會把案例套進去, 看看這些案例執行過程中 database 資料的變化是不是跟我想像的一致, 其實這邊跟 (1) 一樣, 只是我 review 的是 database 的設計, 不是 code 的設計

3. **確認實作與驗收邊界**:  
   規格定案後, 會同時確認驗收範圍 ( decision table 會決定要展開哪些 test case ), 這是實作部分的規格跟護欄, 會影響 domain logic 的開發 (業務邏輯), 以及 domain api hosting 的開發 (工程需求), 並且產生必要的 deployment artifacts

接下來就分別看這實際三個階段, 我的做法過程記錄...




## 3-1, 確認程式碼的邊界

我在 README.md 就明確的定義了 code (project) layout 規格, 程式碼的介面規格, 會放在 AndrewDemo.AgentRateLimit.Abstract 這專案下 (以下都簡稱 .Abstract), 這是 Microsoft 常見的命名規格, 這個專案只包含介面定義, 不包含實作, 使用的 code 只要參考 .Abstract 就能編譯了, 而實際的實作程式碼, 則是衍生這專案內的 Interface , 並且靠 DI 做依賴注入, 整個體系就能串起來｡

因此第一步驟很單純, 直接讓 AI 替我生成 [第一版介面規格](https://github.com/andrew0928/AndrewDemo.AgentRateLimit/blob/3daf49fc85a4190418f214dd693f644d0ff509c5/docs/architecture/subscription-credit-abstract-design.md)｡ 而經過我的 review (這段我真的一行一行看), 我開始刪減我認為不必要的設計:


```
(ptompt)

我需要 schema 設計能支持重新計算 但是我不需要在 abstract 支援這些介面 .abstract 只要支援正常的服務處理 "判定與消費" 就夠了 我的判斷是: IUsageReconciliationExporter, IExtraPoolAdjustmentService 介面是不必要的

```

我修正的差異在於:  

我的確需要對帳等等功能, 但是在我腦袋裡的藍圖, 那是 database schema 必須保留足夠的原始資訊讓我可以事後核對帳務, 並且有修正的能力｡ 但是我現在在 review 的是給主要服務使用的 "交易控制" 介面規格, 在這個邊界需求上, 我不需要 "對帳", 我只需要正常處理 "判定能否使用", 以及 "使用之後的費用回報" 就夠了｡

這是我做的決策之一 (最後會看到我總共做了多少決策) 於是兩個介面被我砍了, 我跟 agent 討論修正後, 拿到 [第二版設計規格](https://github.com/andrew0928/AndrewDemo.AgentRateLimit/blob/b84c06ec09598ba91a34d57d38e883b5a0806e53/docs/architecture/subscription-credit-abstract-design.md)｡ 砍完後, 主要介面剩一個, 其實我真正需要 review 的 code, 其實也只有這段而已:

```csharp

public interface ISubscriptionCreditUsageService
{
    ValueTask<UsageCreditDecision> DecideAsync(
        UsageCreditRequest request,
        CancellationToken cancellationToken);

    ValueTask<UsageCreditDecision> ConsumeAsync(
        UsageCreditRequest request,
        CancellationToken cancellationToken);
}

```

這設計我第一眼看來沒什麼大問題, 當我需要進一步驗證時, 過去我會開始畫圖, 核對 class diagram, 看看是否有相依的 class 水火不容? 畫 sequence diagram 看看是否每一個步驟需要的介面都被正確的定義了?

為了能讓我理解的效率最大化, 這些資訊我都要求 agent, 直接用這 contract, 生成對應的文件 (包含 diagram) 直接讓我檢視, 我唯一要做的就只是看看運作方式跟我想像的是否一致...

舉例來說 (這是後面步驟才完成的內容, 我拿來示範), 與其花我的注意力來看程式碼 "想像" 程式會怎麼跑, 不如讓 agent 替我燒 tokens, 省下燒我腦細胞的機會, 我直接驗這類似這樣的 [sequence diagram](https://github.com/andrew0928/AndrewDemo.AgentRateLimit/blob/architect-mode/docs/architecture/subscription-credit-abstract-design.md#10-consume-sequence) 來確認實行順序:

![alt text](/images/2026-07-08-devopsdays-aiera-architect-showcase/image-1.png)





這階段完成後, 下一步就是檢驗 DX ( developer experience ) ...



所謂的 DX, 主要是看你的介面設計對於開發人員是否友善? 基本一點的, 命名是否夠清楚? 相同的資訊, 在不同的 API 之間的定義是否一致? 例如查詢訂單傳回的結構, 跟建立新訂單輸入的結構, 相同的部分是否共用定義等等...

好的 DX 可以引導開發人員寫出正確的程式碼, 省掉很多不必要的檢查與轉換, 語意也會更清晰可讀, 這些除了對真人有幫助之外, 對 AI 同樣也有幫助｡ 清晰的介面定義, 你可以用更少的敘述就交代清楚的他的用法 (這樣 context window 不就消耗更少了嗎? ), 語意更清楚, 寫出來的程式碼會更簡潔 (這樣處理 source code 花費的 input / output token 不就更少了嗎?)

我的看法很簡單, 歸納起來, 好的 DX 對 AI 而言, 代表:

- AI 可以用更少的思考步驟就完成任務
- AI 可以花費更少的 token, 更小型的模型就能完成同樣任務
- AI 犯錯的機率降低了
- 設計出來的介面可能被多個不同團隊使用, 上述的影響可以讓多個團隊的 AI / Developer 寫出來的程式碼更一致 (你更可以確保每個團隊都能正確的使用你的介面)

其實你會發現, 很多對人友善的設計, 對於 LLM 也是友善的, 這是跟過去很不一樣的觀念轉變｡ DX 這題就是其中之一, 怎麼做好 DX 這邊我就點到為止, 真的有興趣, 可以去翻我過去寫過好幾篇 API First 相關的主題, 談的都是怎麼設計正確合理的 API, 並且搭配 SDK 顧好對開發人員的體驗｡ 回到主題, 我在這個階段我會怎麼 "Review DX" ?  我的做法是:

直接叫 AI 按照現在的 .Abstract 設計, 產生一段示範怎麼使用的程式碼, 我直接來看這段 example code 是否飄出了程式碼的壞味道..., 這件事情過去我做的太多次了, 對我來說這是讓我驗證 DX 最有效率的方法, 於是我這樣要求 agent:

```

(prompt)
試著寫第一個 test case, 我要用實際使用 .abstract code 的 test 來評估 developer experience
測試不需要通過, 只需要讓我理解以後我會怎麼用 .abstract 就足夠, 還未實作的你可以用註解說明略過

```

Agent 給了我這版, 用 unit test 風格寫的 test case, 省略掉 Assert 的部分, 其實真正用起來就是這樣:

```csharp

ISubscriptionCreditUsageService usage = new ContractOnlyUsageService();

var request = new UsageCreditRequest(
	UserId: new UserId("user-a"),
	SubscriptionId: new SubscriptionId("sub-a"),
	RequestedCredits: RequestedCreditsInput.FromInt32(20),
	IdempotencyKey: new IdempotencyKey("tc-window-001"),
	CorrelationId: new CorrelationId("corr-tc-window-001"),
	Source: "abstract-dx-test");

var decisionOnly = await usage.DecideAsync(request, CancellationToken.None);

var consumed = await usage.ConsumeAsync(request, CancellationToken.None);

```


看到這 example code, 我才發現我自己漏掉很重要的事情, 這是規格層級的問題, 但是我先前都沒想到｡

這段測試, 描述 user-a 想要從使用額度內扣除 20 點, 於是使用 UsageCreditRequest 來詢問這個動作該不該執行?
乍看很合理, 不過對比 claude code 的規則, 請問大家, 我在丟任務給 agent 當下, 我會知道這個任務跑完要花多少 token 嗎? 應該是沒辦法的, 所以典型的做法是:

1. 先檢查目前還 "有沒有" 額度? 
2. 檢查的 request 無法預知需要花費的 token 數量, 因此判定一定會失準
3. 任務執行完畢, 事實已經發生, 即使超出額度也要記錄, 因此剩餘額度可能是負的, 系統端會需要承擔一定的費用

於是, 實際的用法開始跟設計的用法有落差了, 系統必須允許扣到負數, 業務端也必須接受一定範圍的超額使用｡ 這些都不在原始規格敘述內, 所幸現在一行 code 都還沒開始寫, 我也只 review 了上面 10 行 code 就抓到問題了, 這過程非常值得｡ 

而這些規格的落差, 即使是我, 我也沒信心在完全沒看到 contract code 的情況下就想的到, 直接讓 agent 展開成實際的應用案例片段, 等於是對 reviewer 的我最直接的驗證方式了｡

於是, 我又推進了一版, 這版我有 git commit, 更新了規格文件, 並且在文件上補充了 [使用案例說明](https://github.com/andrew0928/AndrewDemo.AgentRateLimit/blob/bab4a8f81393e0ec54786cd918eae4326646153b/docs/architecture/subscription-credit-abstract-design.md#unknown-final-credits-usage-case), 我直接擷圖 .md 的規格說明片段:

![Unknown final credits 的案例](/images/2026-07-08-devopsdays-aiera-architect-showcase/unknown-final-credits.png)



## 3-2, 科普 - 把帳本與計算分開

下一步是用同樣的方式, 只是驗證的對象是 database schema, 不是 code interface. 在那之前, 先來科普一下, 區隔一下 "帳本" 跟其他的 "運算" ...

這次的題目, 我在初始需求就指定使用 SQLite｡ SQLite 本身支援 ACID 與 transaction, 足以處理一般的交易需求, 不過in-process database 的設計讓他先天有部分限制 (例如: 同時間只能有一個 writer, 依賴 OS / file system 必須正確運作, 不支援巢狀的 transaction 等等在其它 DBMS 很常見的功能), 因此設計上我還是希望盡量縮小需要由 database 嚴格保護的一致性邊界, 避免把過多跨資料表的狀態同步與計算責任都壓在 database 上｡

簡單的說, sqlite in-process 的設計限制了吞吐量, 而且也受限於 file system, 本身的處理能力無法跟常見的 postgresql 這類資料庫相比, 我在設計階段必須想辦法降低對資料庫能力的依賴, 要盡可能的縮小 transaction 處理的範圍, 也要盡可能的將運算從 database 移到 code...

我的做法是先把資料分成兩類｡ 第一類是已經發生、不能遺失或任意修改的事實; 第二類則是根據這些事實與業務規則計算出來的目前狀態｡

以這個系統來說, 每一筆實際發生的 consume record 都代表真實的服務成本, 也是事後對帳、拆帳與追查異常時最重要的依據, 因此我會把它視為帳本｡ 所謂的 "帳本", 意思就是一旦寫入帳本, 就不應該有任何理由刪除或是修改, 你也不應該在已經過去的時間點插入新的帳務資料｡ 若真的有資料錯誤, 應該在後面的時間補上一筆沖銷的記錄才對｡

因為有這些特性的要求 (俗稱: immutable, 不可變更的資料), 帳本只能採用 append-only 的方式操作, 常聽到的 CRUD, 對於帳本而言只能接受 CR, 不能 UD... 至於目前使用額度、window 狀態與剩餘點數等資料, 則盡可能視為服務運作時使用的狀態或計算結果, 等帳本資料確定寫入完成後, 再依據帳本來做延伸的計算｡

這樣拆分的好處, 是 database 不需要同時承擔所有查詢、計算與狀態還原的責任｡ 只要帳本保存了足夠的事實, 許多統計資料與查詢結果就能由 application 重新計算或重建｡ 真正需要嚴格保護的資料範圍因此變小, 需要定期核對的帳務資料範圍也會更明確, schema 的責任也會更清楚｡

這不代表可以完全取代 ACID transaction 的需求, 只能簡化與縮小範圍而已｡ 以這個案例來說, 典型的做法可能要把帳務記錄跟剩餘額度的更新併入同一個 transaction 的範圍內處理, 當你改用帳本的結構, transaction 只需要涵蓋帳本本身就夠了, 加上只會 CR 不會 UD, 鎖定的範圍跟要隔離的操作更單純｡ 當一次 consume settlement 同時涉及新增 consume record、更新目前用量, 或扣除額外點數時, 仍然需要 transaction 或適當的 concurrency control 來確保一致性｡ 這個設計降低的是資料異動、對帳與重建的複雜度, 不是取消交易正確性的要求｡

這個方向和 CQRS、Event Sourcing 常見的設計思路有關, 不過這裡我不打算展開討論這些模式｡ 有興趣的讀者可以參考我在 2020 .NET Conf 分享過的內容:


![alt text](/images/2026-07-08-devopsdays-aiera-architect-showcase/image-2.png)
[2021 .NET Conf - 微服務資料管理的天堂路](https://slides.chicken-house.net/s/2021-NETCONF), 談 CQRS / Event Sourcing 的應用與實踐



## 3-3, 定義資料的邊界與規格驗證

回到主題, 驗證 database schema 的設計, 以上關於帳本設計的科普我就介紹到這, 因此這段的敘述我就不著墨太多｡ 接下來我會強調: 這樣的初始黑箱規格, 加上前面已經確認過的 code 邊界設計, 來推演 database schema 該怎麼設計才能符合期待｡

我按照我跟 agent 對話的順序來說明這部份｡ 初始化的 schema design:

```

(prompt)

給我 database schema 的設計, 類似 abstract 一樣, 我先看主要結構, 細節 (例如 type, relation, constraint 等等) 可以晚點再補

```

第一版得到的結果大致是這樣, 跟第一版的 .Abstract 設計類似, 結構上工程觀點都作的很正確, 但是給太多了, 對我來說有點過度設計...


```

主要方向是：source facts append-only，status/audit/reconciliation 都當成可重建 projection。

核心 table groups：

- `subscription_account`
- `subscription_credit_policy_snapshot`
- `usage_decision`
- `usage_credit_movement`
- `extra_pool_movement`
- `usage_idempotency_record`
- `usage_audit_entry` projection
- `subscription_usage_projection` projection
- `reconciliation_run` optional

我特別把 system absorbed overage 的重算語意寫清楚了：rolling window used 要看 `subscription-window-usage`，不是只看 `subscription-allowance-covered`。所以 actual 120、allowance covered 100、system absorbed 20 時，5h used 仍增加 120，remaining 顯示 0，直到 rolling window reset 釋放。

```

### 用情境確認: 剩餘額度計算規則

接著我用前面相同的做法: 直接讓 agent 用這版 schema 設計, 套用我指定的情境, 並且把表格資料變化逐筆列出來給我確認:


```

(prompt)

用這個案例演示 table 內容給我確認

1. 初始化, 2026/07/01 23:01:23 第一次使用服務, 5h limit: 100, 7d limit: 1000, call: decide
2. 使用, 2026/07/01 23:10:00, 使用 30
3. 使用, 23:30:00, 使用 80
4. 使用, 23:45:00, 使用 20
5. 使用, 2026/07/02 08:00:00, 使用 50

```

這段我還沒有真正建立資料庫, 完全只是存在於 context 內的 database schema 設計而已｡ 而這樣的設計我能夠給情境, 就能模擬的出來操作過程, 靠的是 LLM 的推論能力, 因此你要記得挑選數理以及推理能力好一點的模型來用, 同時也不要 100% 相信他是正確的. 即使如此, 這方法還是很有用的, 因為現在的模型能力都很不錯, 正確率其實是夠的, 對我而言, 更重要的是協助我驗證結果, 我需要確認的是結構, 而不是要真的計算...

其實以前我就很常在腦袋裡 "想像" (腦補) 這段程式碼會怎麼跑, 跑出來的結果會是什麼... 只是現在這腦袋換成 LLM, 我只是叫 agent 在他的腦袋裡面想像執行結果給我確認而已｡ 

這是 agent 回應給我, 決定是否能夠消費的判定清單:

|decision_id|time|requested|result|audit_ref|
|---|---|---|---|---|
|dec-001|2026-07-01 23:10:00|30|accepted|audit-001|
|dec-002|2026-07-01 23:30:00|80|accepted|audit-002|
|dec-003|2026-07-01 23:45:00|20|accepted|audit-003|
|dec-004|2026-07-02 08:00:00|50|accepted|audit-004|

結果, 果然看出端倪... 

跟我預期有落差的是第三筆. 我的理解是 5h 的額度是 100, 按照前面的規格要求, 5h 範圍內, 第一筆 30 應該可以消費, 第二筆 80 因為起始時還有餘額, 雖然超過了應該也要成功消費, 剩餘額度 -10, 理論上第三筆 20 的消費應該被拒絕才對, 但是 agent 模擬出來的結果仍然可以消費...

因為這次確認, 我找出雙方誤會規格的地方了｡ Agent 誤認為這三筆是連續的單一動作產生的三筆消費, 都是已經發生的事實, 所以 Agent 就都認列了(前面有提到, 已經發生事實只能接受, 並且扣到負數), 才會產生這三筆都被承認的結果

於是我再次補充規格:

```

(prompt)

重來一次, 我只列出每次要消費的額度, 每次消費都是獨立的操作 (不是連續不可分割的操作)
我會假設每次消費前都會先 decide 確認餘額, 確認能否使用

1. 初始化, 2026/07/01 23:01:23 第一次使用服務, 5h limit: 100, 7d limit: 1000, call: decide
2. 使用, 2026/07/01 23:10:00, 使用 30
3. 使用, 23:30:00, 使用 80
4. 使用, 23:45:00, 使用 20
5. 使用, 2026/07/02 08:00:00, 使用 50

```


經過這樣的修正過程, 結果正確了, 至此需求規格算是清楚了 ( agent 的回應我就略過了 )｡  接下來我開始確認計算的問題｡ 

我心理的想像是:

> 既然要最小化 database 運算的負擔, 採用 CQRS 的策略自然是資料產生時就盡可能的先將未來要使用的形態計算好, 用 write model 儲存資料, 同時多寫幾份 read model, 用最方便使用的結構多存一份, 避免查閱當下再用複雜的 query 來取得統計資訊的傳統做法｡


### 用情境確認: reset 的時機

所以我繼續問了這個問題:


```

(query)

系統怎麼追蹤剩餘額度? 存在哪個 table?
如何知道超過 5hr 額度可以重置?
我在意每次 decide 都有大量運算 (ex: 必須 scan 過去 5hr / 24x7hr 的記錄)

```

Agent 這段的回覆很經典, 我覺得是整個過程最關鍵的地方:


```

**剩餘額度存哪裡**

存 projection，不存 source table：

`subscription_usage_projection`

| subscription_id | 5h_used | 5h_remaining | 5h_next_expire_at   | 7d_used | 7d_remaining | 7d_next_expire_at   | projection_updated_at |
| --------------- | ------- | ------------ | ------------------- | ------- | ------------ | ------------------- | --------------------- |
| sub-a           | 110     | 0            | 2026-07-02 04:10:00 | 110     | 890          | 2026-07-08 23:10:00 | 2026-07-01 23:30:00   |

這張是 fast path 狀態表，給 `DecideAsync` 用。

```


到這裡為止, 我第一次確認到 5h / 7d 的 reset time 的儲存方式. 每個 claude code 的訂閱都有一筆這樣的記錄, 這張表格記錄的是這訂閱當下的使用狀態, 分 5h / 7d 兩組, 個別記錄 used / remaining 點數, 簡單的說你每次查閱 usage 的時候, 就是把你的訂閱對應的這筆資料顯示出來而已｡

關鍵的 time window 處理, 5h 這組只有三個數字: 用了多少 (5h_used), 剩餘多少 (5h_remaining), 重置時間 (5h_next_expire_at)... 7d 的結構都一樣, 重複這三個欄位的設計而已｡ 

這設計背後已經隱含幾種更新機制了, 包含:

1. 檢查當下就會先判定時間, 決定繼續沿用這筆資料, 還是已經超出時間範圍, 先觸發 reset 機制再回應?
2. reset 的必要資訊 ( 額度是多少? remaining 理論上應該被重設回 100, 但是沒看到 100 除存在哪裡, 寫在 code? )


這邊挖出另一個問題, reset 的時間點判定, 在 database schema 設計上其實看不出來｡ AI 給的設計是不管你有沒有在使用, 就固定每隔 5h / 7d 會 reset 一次; 這跟我們 "體感" 使用 claude code 的規則不大一樣, 實際使用上是 reset 後, 直到你下一次開始使用的那瞬間, 才重新按下 reset 倒數計時的碼表 (也就是當下才 +5hr 寫入 5h_next_expire_at 欄位), 不是按照固定週期...

於是, 我繼續跟 agent 修正需求規格:

```

(prompt)

不對, 按照 claude code, 我長時間沒使用的話什麼是都不會發生
但是當我這瞬間開始使用, 若 5h 已經重置, 則 5h 是從現在開始 +5h, 7d 比照辦理
我覺得他的演算法就是模擬 leaking buttle algorithm

```

這次 codex 就真的跑了很久 ( 花了 6m 49s, 我有開 1.5x fast ), 然後修正了整組 database schema 設計, 回應了這些結果給我:

```

對，前面的 rolling window 假設是錯的。這版已改成 **lazy quota window lease**：長時間 idle 什麼都不做；下一次 `DecideAsync(1)` 進來時，如果 5h / 7d lease 已過期，就從當下開新 lease，時間是 `now + 5h` / `now + 7d`。這比較像 leaky bucket/token bucket 的 admission-control 直覺，但我在 spec 裡用 lease 命名，避免誤解成每秒背景 leaking 或每筆 usage rolling expiry。

```

到這裡為止, reset time window 機制的需求跟設計就算定案｡ 我接著繼續處理其他的設計問題｡



### 收斂必要的帳本記錄


我盤點了一下, 目前設計總共要 9 張原始資料表 (source of truth), 以及 3 張 projection 用的資料表 (可以被重建).. 我覺得太多了, 想像中複雜度不應該這麼大才對 (我要最小化帳本 / sourth of truth 的範圍)... 

我發現設計過度了, 數值設定的異動也被當成 source of truth 看待, 但是對我來說真正重要的就是消費的記錄表, 其它都可以視為一般資料看待｡ 於是我下了收斂設計的要求:



```

(prompt)

能正常運作的最小表格

我釐清我的意圖, 對我重要的是:
1. 實際 consume 的記錄, 這是內部成本, 涉及拆帳分潤等, 必須確實記錄
2. time window 我不在意, 這只是控制手段, 避免瞬間大量使用. 如果需要重算, 其實消費都已經發生了, 我不會需要重算 time window
3. 我真正在意的是 consume 記錄跟真實 infra log 比對, 有沒有少算一筆 consume record 才是最關鍵的, 所以我認定的 source of truth 只有這個

其餘應該有必要的資料表 (例如 subscription .. ), 多餘不需要的額外表格都可以刪除

```

很多時候都是你有要求他才會修正, 這次我得到的最小設計只要三張表, 包含先前被 agent 誤認為非必要的 extra pool (額外儲值) 需求, 跟我預期的一致:

|Table|必要性|性質|責任|
|---|---|---|---|
|`subscription_account`|必要|mutable state|subscription 狀態、5h/7d admission state、extra pool current balance|
|`subscription_consume_record`|必要|append-only source of truth|每一筆實際 consume；包含 actual credits、infra reference、`credits_covered_by_extra_pool`、system absorbed、拆帳分潤 snapshot|
|`subscription_extra_pool_record`|必要|append-only source of truth|extra pool 的增加、調整、修正來源，例如 top-up、manual adjustment、grant、correction|


### 用情境驗證: 超出額度的用量處理原則

最後, 我再次用一個測試情境來驗證這份 schema 是否合理, 我重新丟出這個測試案例, 只是這次的設計, 除了 5h / 7d 的限制之外, 額外預先儲值了 1000 等待需要時直接扣, 不需要等 reset:

```
(prompt)

最後用前面我舉的案例, 用這三張表格重跑一次
假設一開始 extra table 有儲值 1000
```

Agent 模擬試算後給我這答案, extra pool 最後會剩下:

```
1000 - (10 + 20) = 970
```


數字又跟我預期的不同, 我預期剩餘額度應該是 ```1000 - 20 = 980``` 才對, 結果我又抓到定義沒有對齊的問題了... 

前面的設定是 5h 額度 100, 我依序扣掉 30, 80, 20 .. 這次判定錯誤的是 80 那筆, 我的認知是 80 扣掉後, limit 會變成 -10, 這落差由系統吸收, 因為這已經發生才記錄, 而要使用 extra pool 應該要使用者確認, 所以只有最後 20 經過確認後會扣掉 extra pool 才對 (我的期待), 而 agent 的設計是 -10 也會扣掉 extra pool ...

```

(prompt)

修正, 5h 超額 10 那次應該要系統吸收
因為再下一筆, decide 時才會發現 5h pool 已經不足, 需要動用到 extra pool
UI 應該要提示, 詢問使用者是否願意使用 extra pool? 或是願意等到 5h reset 在繼續?

前面溢出的 10 沒有詢問, 因此歸在內部吸收

```

補足規格, 更新規格文件後, 重新讓 agent 再模擬一次, 最後一切都定案了:

```

1000 - 20 = 980

```

規格的邊界行為被修正了, 連帶的這些設計也回到前面的 code / schema design 文件｡ 這次的變更可以直接看這包 git commit, 你有興趣可以特別看看這次變更的 schema 說明文件: [subscription-credit-schema-design](https://github.com/andrew0928/AndrewDemo.AgentRateLimit/blob/d2cd72bd0f248b5fb1171872bab13412ee8c81d1/docs/architecture/subscription-credit-schema-design.md)



## 3-4, 確認實作與驗收邊界

設計階段快要完成了, 最後是我要親自指定必要的驗收條件, 我在台上提到的是把影響測試路線的變因列出, 用 decision table 把所有可能的組合列出來, 這樣你會有個覆蓋率 100% 的全貌, 從中挑出你認為價值高的測試優先驗證, 因為有全貌, 所以你知道你略過了什麼, 將來有需要你也能很容易的補回來

這邊我就示範一下 decision table 的操作方式, 我先給了 agent 我想像的第一版要求:

```

(prompt)

接下來 decision table 重新調整
以一個 run ( detect, and consume 的完整過程 ) 來說, 會決定結果的有幾種條件:

1. 5h expired
2. 7d expired
3. 5h quota available
4. 7d ...
5. 5h limit enough
6. 5h limit not enough
7. 7d ...
8. 7d ...
9. extra pool available

若還有其他會影響結果的條件我沒列出來請跟我說
沒問題的話, 請依據這樣的結果展開 decision table

筆數很多, 先更新表格就好, 有必要我挑選後再展開 test case 內容

```



結果, 要把 9 個維度所有組合列在一張表呈現實在太大, 9 種變因光是符合跟不符合兩種可能, 全部列出來就有 512 組, 何況有些維度還不是只有 true / false, 範圍更大｡ Agent 很聰明的幫我分成幾個獨立的 group, 每種組合不互相混在一起檢驗, 我自己判定這樣分群組還算合理｡

我得到的結果像這樣: [subscription-credit-rate-limit-v1-decision-table](https://github.com/andrew0928/AndrewDemo.AgentRateLimit/blob/53982de8477c32b1a1aaa926623f0ae4ec55336f/spec/coverage/subscription-credit-rate-limit-v1-decision-table.md)



我節錄其中一張表格當作案例, 所謂的 decision table 大致像這樣:

![alt text](/images/2026-07-08-devopsdays-aiera-architect-showcase/image-3.png)

每種可能影響結果的變因, 會列在欄位上, 這些欄位的每種可能的組合, 都會逐筆列出來｡ 因此整張表格就代表這些條件內所有的組合了, 在這範圍內是 100% 的覆蓋率｡ 每一筆就是一種測試案例, AI 替我把每一筆測試案例都取了名字 (case), 也都標上了預期結果 (expected result), 同時也都標上了測試案例編號...

這樣的表格總共有 6 張, 每張表格都各自對應不同的主題, 各自展開不同的變因.. 我逐一檢視之後, 最後我指定了其中一個 ```end to end run outcome table``` 當作我的驗收要求:

![alt text](/images/2026-07-08-devopsdays-aiera-architect-showcase/image-4.png)

簡單的說, 這是在驗證 5h / 7d 的限制額度在不同的情況下產生的各種組合, 總共有 16 筆. 我指定了這 16 個測試案例當作驗收要求, 因此我繼續向 agent 下了這段 prompt:



```

(prompt)

我先集中測試 End to end run outcome table 的所有測試
替我展開這部份的 Given/When/Then Testcases, 案例就用我剛才示範的, 5h: 100, 7d:1000, 若有必要放 extra pool 就用 1000

這測試案例是第一版我必須要通過的所有情境

```

最後展開的結果在這邊, 連結我直接跳到 end to end run outcome table 這位置, 這表格列出的 16 種情境就是我要求的驗收條件 (同一份文件, 只是我只指定了 [end-to-end-run-outcome-table](https://github.com/andrew0928/AndrewDemo.AgentRateLimit/blob/53982de8477c32b1a1aaa926623f0ae4ec55336f/spec/coverage/subscription-credit-rate-limit-v1-decision-table.md#end-to-end-run-outcome-table) 這張表的測試組合當作我的驗收要求)




這步驟的意義很重大, 透過這張決策表, 我其實已經做了決策:

> 在所有各種可能的組合中, 我挑出了我認為對我最重要的情境範圍

我挑出的 decision table 的每一列, 其實都包含了足夠的資訊, 可以讓 AI 接手展開成完整的 given when then 的測試案例, 這些測試案例自然也能接續展開成 unit test code. 後面都是很明確的轉換, 我只要在這裡用濃縮的表格, 用我的經驗來決定驗證範圍｡


## 3-5, 規格確認, 進入開發 - .Core

至此, 前面的步驟把介面規格都定義清楚了, 這個步驟也把驗收的條件都交代清楚了, 交給 AI 的任務, 從程式碼, 從資料庫, 每個角度都把 contract / expected 都用程式碼定義的清清楚楚的, AI 需要滿足的條件就變的很單純:

> 每個切割的任務, 只要 AI 產出的程式碼能通過 contract ( 搭配 .Abstract, 能通過編譯器的檢查 ), 也能通過 expected ( 能通過 unit test / end to end test ), 就算完成, 這就是我在 DevOpsDays 台上講的用程式碼當護欄的具體操作方式｡


接下來的步驟, 其實... 就很無聊了 XDD,  打一行字叫 agent 開始寫 code 而已｡ 我打了一行字叫 agent 照既定的規格開發, 把 .Core 專案完成, 並且按照 decision table 敘述的範圍完成 unit test, 然後直到能通過測試為止在交付成果給我

這過程中已經不需要我的介入了, 由於前面的過程都把需求提前驗證結束, 這段就丟著給 agent 執行就好, 這正是我的目的, 越後面的任務越能獨立進行!

Agent 全速跑了 12m 49s (這是有啟用加速的 1.5x fast mode), 結果就出來了, 我得到了一份完全符合我 .Abstract 要求的介面實作 (包含我指定的 DX 設計), 同時這份實作也完全通過指定的測試...

這段成果我就不貼了, 總之看 commit history, 這個 commit 突然間 code 通通都寫好了, 有興趣直接看, 這是 ready 到可以開始開發的那個版本 files 狀態:

- commit - [browser files](https://github.com/andrew0928/AndrewDemo.AgentRateLimit/tree/59584250703e232a84a7642869fc01fda2046089)



## 3-6, 追加需求, 開發 - .API

本來我只想到此為止就收手的 (對照組也都只做到這邊而已), 但是最後一步實在太順利, 於是我忍不住加碼... 我除了 .Core 能完成商業邏輯的設計之外, 我想進一步做成能真正獨立部署, 能真正被呼叫的 Http Rest API Service... 撇除商業邏輯不談, 這部份剩下的都屬於 "NFR" ( Non - Functional Requirement , 非功能性需求 ) ..

我希望 AI 能替我產出:
1. 封裝成 aspnet webapi 的 http api hosting
1. 包含部署的設計 ( docker file, docker compose yaml )
1. 建置好的 docker image

這些結果, 讓我可以直接在本地端用 docker compose 啟動 http api 來驗證跟測試, 我在 DevOpsDays 展示的案例 Andrew Shop, 甚至同步產生了 Azure Container Apps 的部署設定檔, 這邊我就簡化成 docker compose 就好｡

在額外追加這需求時, 我只追加了一條設計規格, 那就是安全機制的設計: access token. 我指定了 access token 的 database table (前面規劃 database schema 我沒有處理到 access token), 也指定了 http api 使用的 tech stack, 同時要求 agent 在本地端替我打包成 docker compose, 同時要額外準備一個 tool, 用來初始化資料庫..

```

(prompt)

我要開始開發 api hosting, 這 rate limit 需要變成正規的 http rest api, 並且有基本的安全機制

在 database 建立 access token 的管理表, 只有兩個欄位, 一個是 token (type: UUID), 另一個是 subscription id

所有 http api 都要在 authorization header 帶這個 token ( bearer, 全大寫, 不包含減號 )
後續的 api 都按照 token 對應的 subscription id 來操作

給我 api spec 說明, 先給我文件確認規格設計

```

過程我分三個階段實作, 並且 commit, 從 git history 可以清楚看到每個階段 agent 改了什麼｡ 實作階段就這最後 4 個 commit, 分別是:

![API 實作階段的 commit 記錄](/images/2026-07-08-devopsdays-aiera-architect-showcase/api-implementation-commits.png)

依序是:

1. **Design subscription credit HTTP API token auth**:
   說明存放 access token 的 table schema, 以及程式碼處理的原則 (我有指定 authorization header)
2. **Add subscription credit API hosting scaffold**:
   實際開發出來可被部署的 api service, 這步驟也包含了 dockerfile, docker compose 封裝, 我要求對應的 .http 可以手動發出 http request 的測試腳本也準備好了
3. **Add subscription credit API blackbox tests**:
   本來我只是想簡單用 shell script 測試一下 API 是否正確, 不過想想規格情境都有了, agent 寫 code 也不會累, 我就直接叫他寫一版把 api 當作黑箱, 只能用 http client 驗證結果的 unit test 了

最後當然都順利完成, 結果就是大家看到, architect-mode 最新的內容, 一切符合預期｡ 我貼一張本地端跑 docker compose, 啟動本機測試環境後, 用 .http 發出測試的 http request 的擷圖吧, 過去為了做到這樣, 不知道需要手寫多少 code 跟設定:

![alt text](/images/2026-07-08-devopsdays-aiera-architect-showcase/image-5.png)


實作過程到此告一段落, 整個第三節, 就是整個 architect-mode 的執行過程｡





# 4, 成果比較

至此, 實驗過程都交代完畢, 成果到底如何, 我從幾個視角來檢視:

- **規格對齊**: Human decision gate 改變了什麼?
- **投入產出**: 人腦寶貴的注意力該用在哪裡?
- **實驗設計**: 三組實驗的結果各自說明了什麼?

這整個專案操作下來, 我最想表達的效益, 都在上面這三點了｡ 這個階段, 我會說明我的主觀意見, 包含這次實驗能夠實際證實的效益, 也包含我自己在過程中主觀觀察, 或是我在其他的專案中得到的心得, 剛好有相關我會在這邊一起提出我的觀點｡ 

從流程來看, 我的觀點是: 架構師本來就有義務盡早點出設計階段的問題, 引導團隊 (包含 agent) 走向正確的方向, 避免後面的風險與損失, 而 AI 的成熟需要正確的流程配合, 所以我調整了能最大化人類決策效益的做法, 在 AI 開發過程中提早插入 human decision gate

這流程的設計, 我是以 "人腦" 最有效運作為優先來考量的｡ 因為 AI 終究會越來越快, 能力越來越強, 成本越來越便宜, 更容易訓練, 複製跟擴展｡ 最終瓶頸還是會落在關鍵的人員身上｡ 第二點我想呈現的就是, 從事後的過程分析數據, 來證實這個推論, 人腦不應該去 review 大量 AI 產出, 而是該 review 產出前餵給 AI 的規格｡ 提前一步處理, 抽象層級就往上一級, 要 review 的內容數量就降低一個數量級, 影響範圍就擴大一個數量級

最後, 我做的這三組實驗, 分別代表 "理想的流程" (architect-mode), "沒有架構師介入的對照組" (goal-mode), "沒有架構師介入的對照組 - 用最強的模型" (fable5), 來證實模型與工具成熟到某種程度之後, 影響品質的關鍵已經轉移到操作者身上了, 我希望透過這些案例大家可以清楚的看到這差異


## 4.1, 規格對齊: 成果是否符合業務需求?

這個題目, 我用實際的案例呈現了很多專案執行時會碰到的盲點, 一開始你以為規格很完整了, 實際做下去才發現還有很多規格需要釐清... 你可以現在回頭看 (1) 定義需求規格的章節, 試想如果你是負責開規格的人, 沒這樣跑過一次設計跟驗證流程的話, 你能把規格開的多 "正確" ? 跑完你就會理解我說的這件事的重要性了｡

我在初始規格中, 也埋了簡單的 Harness, 其中一個就是自動幫我記錄過程中我提出的 "重要決策", 並且記錄在 ./docs/decisions/index.md 下｡ 我把最後的清單擷圖放在下面, 給各位感受一下:

從結果來看, 執行過程中有發生的重要決策, Harness 都有忠實記錄下來, 想看完整清單可以直接到 github 看 [decisions/index.md](https://github.com/andrew0928/AndrewDemo.AgentRateLimit/blob/architect-mode/docs/decisions/index.md), 這張表格我特別擷圖下來說明:


![architect-mode 的 decision log](/images/2026-07-08-devopsdays-aiera-architect-showcase/decision-log.png)


過程中我藉由上面的 review / validate 流程, 找出了幾個初始黑箱規格的盲點, 並且修正了｡ 我事後分析這三個實驗, 整理了這張表, 各位可以實際對比看看, 人為的介入到底替你把關了哪些問題:

| |關鍵語意|goal-mode|fable5|architect-mode|
|-|---|---|---|---|
|1|Unknown final credits|未處理|未處理|minimum balance + settlement|
|2|Window semantics|rolling|rolling ledger|lazy lease|
|3|Extra pool|shortfall 自動扣除|shortfall 自動扣除|explicit authorization|
|4|Accounting truth|audit/usage 混合|audit ledger|consume record|
|5|測試策略|快速基本驗證|adversarial hardening 最強|對齊人工凍結的 16 outcomes|

這張對照表我分兩段來看, 講了兩類的關鍵決策, 一個是業務需求規格 ( 1 ~ 4 ), 另一個是工程品質 ( 5 ).

業務規格的前四項, 可以明確的看到, 即使你選擇更強的模型, 也無法保證他幫你 "腦補" 的規格決策會更貼近你的期待｡ 因為你的期待壓根不存在任何既有的 context 內｡ 在這兩個對照組都顯示 "AI 的直覺", 跟我的本意是不同的, 這些是業務需求沒親自對齊就外包給 AI 處理的風險

而代表工程水準的第五項, 則是表達另一個結論, AI 會自主替你決定該怎麼管控品質, 從結果也可以看到 fable5 明顯的在工程水準要求更高, 但是回到業務需求, 你仍然得自己定義你認為的 "好" 應該是什麼, 會不會過度? 這些都是你需要做的判斷

從結果而論, 各位最應該留意的是: 有沒有在實作前安排 decision gate, 把隱藏的業務選擇攤開, 確認並凍結? 我的做法是讓架構師介入, 並且最大化的降低人為判斷的負擔｡ 得到的成果很明顯, 這些規格落差都被拉齊了｡ 這些規格差異是否重要, 沒有處理的風險有多高, 就端看各位自行判斷了｡ 對我而言, (3) extra pool 沒有使用者授權就能扣款, (4) 對帳的範圍偏差, 這都是嚴重影響業務進行的環節, 如果這是真實的專案, 我會很慶幸我有親自 review ...


## 4.2, 架構師的注意力該用在哪裡?

這段, 我要分析一下 "架構師的注意力"｡ 我覺得這是未來 AI 成熟後, 人的腦袋就是最稀缺的關鍵資源, 尤其是有思考或決策能力的各領域資深人員｡ 在這個我自己練習的 side project 裡, 我定義一下 architect-mode 跟 goal-mode 之間的哪些差異, 是我靠更多的 "注意力" 換來的成果｡ 從前面 4-1 的比較表, 很明顯的看到因為我的決策, 才修正了四個規格上的認知差異｡

我願意花時間處理這些差異, 這是我的 "投資", 而我能揪出這些差異, 不只是花時間而已, 更重要的是我用了一些方法, 讓我擔心的潛在問題浮上表面, 讓我更容易診斷, 因為我知道我的注意力很寶貴, 這是保護我的 "投資" 的方式, 把稀缺的 "注意力" 資源, 放在能獲得最大回報的地方｡

在講結論之前, 我從執行的過程中找出一些能量化的指標來佐證我的想法｡ 首先, 我先找很表面的資訊, 我觀察對話記錄, 看看我在不同 branch, 不同的 commit 之間, 聊了多少 "次" ? 我把 Codex 的 session logs 挖出來分析, 得到這張表格:


![三個 branch 的成果統計](/images/2026-07-08-devopsdays-aiera-architect-showcase/branch-metrics.png)

這張是總表, 我統計了:

1. **prompts**, 代表提問次數
2. **decisions**, 代表我下決策的次數
3. **tool calls**, **tokens**, 顧名思義, 當作 agent 做了多少事的依據
4. **LOC** (line of code), 代表產出, 我把執行跟邊界的程式碼分開統計

這些指標, 我背後有個別想觀察的訊息, prompts 代表我互動的次數, 這是花時間的地方之一 (我要思考我要問什麼), 而在 architect-mode 這實驗組中, contract 是我 "一定" 會進行 code review 的, 而 decisions 則代表我在過程中明確提出選擇並且定案的次數...

因此, 如果我簡單的定義:

- **Human interaction**:  
  參考 prompts, explicit human decisions
- **Review surface**:  
  實際被 review 的 contract code, 以及衍生的 DX review, 以及 decision table review
- **Agent activity**:  
  參考 tool calls, tokens
- **Output scale**:  
  Prod / Test / Contract LOC, 用程式碼行數來評估推論產出的規模

這些指標並沒有嚴謹到能 100% 量化我想觀察的面向, 不過用來觀察同一個 branch 之間, 在每個 commit 的變化分佈是足夠的, 因此接下來我再把 architect-mode 這個 branch 展開, 看每個 commit 的統計:


![architect-mode 各階段的投入統計](/images/2026-07-08-devopsdays-aiera-architect-showcase/architect-mode-commit-metrics.png)

從這張表格來看, 很明顯的可以觀察到:

1. prompts / decisions 明顯的集中在 3, 4, 5 commits, 這些代表架構師的投入都在這些階段 (問答確認細節, 同時做出關鍵決策)
2. prod / test code 的產出明顯都集中在 6, 8, 9 commits, 這些代表真正有效用的程式碼產出, 都在這些階段 (主要的 coding 任務都在這些階段)

看到了嗎? 這分佈各別對應流程圖的上下階段, human in the loop 只需要在前半段流程而已, 後半段則是可以讓 agent 完全自主:

![architect-mode 的開發流程](/images/2026-07-08-devopsdays-aiera-architect-showcase/architect-mode-workflow.png)

後面階段, 我追加了額外的 http api 開發需求, 也因此引入了部分 human decisions 的操作, 而這段過程再次證明, 我把邊界定義清楚後 ( access token 的做法 ), Agent 後面承接整個 API 的開發實作, 以及對應的 end to end api test 也是相當順利, 一次完成｡

能做到這樣的原因很簡單, 因為:

1. 開發範圍內的規格語意已經清楚到足以正確的實作
2. Agent 已經能依據由 build / test 建立起來的護欄修正實做的問題

不需要硬套我上面的流程, 實際上, 只要每次有新的需求或是問題被發現 (例如 bug report 其實也算), 就會產生新的設計邊界, 而這時 human decision gate 就會出現, 只要你盡早將邊界規格界定清楚, 後面的實作與問題解決, 就很容易被大量委派 (不論是外包, 交給其他團隊, 或是交給 Agent), 這才是這方法真正的效益所在｡


## 4.3, 這些成果說明了什麼?


這邊開始, 我會引用多張我在 DevOpsDays 台上講的投影片來說明 "架構師" 的注意力有多重要, 也會包含部分只有在現場提及的內容, 建議大家可以先看過一次 [簡報](https://slides.chicken-house.net/s/2026-DEVOPSDAYS) 再繼續往下看, 首先是我在開場用的這頁:

![alt text](/images/2026-07-08-devopsdays-aiera-architect-showcase/image-6.png)

這頁說明的是: 將複雜系統 (大黑箱) 深度拆解的效益, 除了橫向的切割 (通常是按照功能, 以這次案例而言, 整個系統拆出計費機制, 拆出額度管控, 只是其中一個功能), 也包含縱向切割 (通常是按照階層, 以這次案例而言, 分成 api 要處理的非功能性需求, 以及 .core 要處理的業務邏輯, 以及 .abstract 要處理的介面規格), 這些一路切下去, 你可以把大黑箱切成多個小黑箱, 只要你切的夠細緻, 你不需要完整實作你就能掌握系統全貌...

然而真正的難題在於: 你切完的 "結果", 能否穩定且可靠的交給下一棒接手? 我這邊的例子是交給 agent 開發, 能在 zero shot 就精確的完成結果｡ 靠的不是 vibe coding, 而是靠預先模擬跑完整個流程確認規格後 (把框線定好), 最後才真正完成實作 (把格子填滿)｡ 對照看這頁簡報, 這是在後面提到頁面:

![alt text](/images/2026-07-08-devopsdays-aiera-architect-showcase/image-7.png)

同一張圖, 但是我加了紅框｡ 個別代表的意義是:

1. **把需求當作大黑箱** (左邊紅框):  
完全沒有拆解, 而你期待這樣就能讓 AI 代勞, 其實是不切實際的｡ 看看初始規格交給最強的模型的結果 ( fable5 這組 ), 寫出了很棒的程式碼, 但是最重要的需求卻沒有對齊, 這對 vibe coding 的角度來說很厲害, 但是在企業應用上這是遠遠不足的｡ 我這次實驗沒有做完這條路線做到底需要多跑幾回合, 我簡單的推測一下就好, 我在 architect-mode 這條路線, 花了至少五次重大修正才完全對齊, 大黑箱我就比照辦理吧, 你能想像 agent 把整包 code 交給你之後, 你才發現做錯了叫他重改, 整個至少改了五次要花多少時間跟 token 嗎?  
  
2. **拆解規格, 定義邊界** (右邊綠色框線):  
我在 architect-mode 示範的前半段流程, 就是逐步在確認規格跟邊界, 也就是大黑箱拆解後的綠色框線｡ 我釐清的是規格, 就是邊界, 還不是實作｡ 不過我掌握到的資訊, 已經足夠我想像整個系統的樣貌, 並且我可以逐步把每個綠線的框線都設計完成｡  這階段因為還沒開始實作, 但是規格都很明確 (還記得我已經開始用 code 來定義邊界了嗎), 因此要驗證跟修正都很容易, 這階段得到的成效是, 你能夠很正確的掌握全貌, 並且快速且有效率的修正連動的規格設計  
  
3. **開發與實作** (右邊的紅色區塊):  
當你邊界都清楚後, 每個小黑箱的實作都是很明確且容易的｡ 以這個例子來說, 3-5, 3-6 都是真正的實作, 但是幾乎都沒有人力的介入, 人力大概都只是啟動跟進行驗證確認而已｡


對應前面 4-2 我的實驗分析對照, 想像一下, 以後更有規模的大型團隊運作的樣貌會是: 軟體開發團隊的主要 "human" 的角色, 將會是有能力決定規格, 並且做出技術決策的資深人員, 大部分的架構師屬於這類, 而有的團隊雖然沒有架構師的編制, 但是也會有對等的角色在負責這些任務, 例如 principal engineer, senior engineer, RD manager 等等, 未來需要 human in the loop 的主要任務, 就是將大黑箱拆解, 並且把綠線都畫出來的環節 (就是確認邊界與規格)

而把每個小黑箱填滿, 變成小白箱的任務, 則開始可以下放到開發團隊, 甚至更激進一點, 直接委派給 agent 大軍開發實作了｡ 這階段由於不再需要 "真人" 的介入 (或是只需要很少的比例), 因此這邊是很容易 scale out 的, 這時 AI 的執行速度我覺得已經不再是絕對的重點了, 跑的不夠快, 同時派兩個 agent 就好了, 只要你的黑箱切的夠多, 速度是可以透過 scale out 拉回來的. 

想一想就會覺得很恐怖, 兩個獨立的任務照順序做, 跟平行一起做, 總共的 token 費用會有很大的差異嗎? 現在都是靠 token 計價, 只要你還沒踩到 api rate limit 的上限時, 基本上費用是一樣的 (如果你用 subscription, 那個基本算人頭, 原廠會限制速率, 那是另一回事), 如果你是老闆, 你有理由讓他一個一個慢慢做嗎? 當然沒有, 一定是全速進行, 因此我一開始才會說, 未來最主要的瓶頸, 一定都是在人身上, 尤其是架構師這樣的角色, 因為整個團隊的效率, 取決於你定義規格的速度｡


## 4.4, 回到 V-Model, 架構師該把注意力放在哪裡?

在演講的時候, 我提了兩次 V-Model, 我把結尾的那頁放在這邊說明:

![V-Model 中設計與驗證的對應關係](/images/2026-07-08-devopsdays-aiera-architect-showcase/v-model-design-validation.png)

軟體工程中, V-Model 的方法論已經行之有年, 我大概是在 20 多年前, 還是個初階技術主管時學到的理論｡ V-Model 左邊從需求、系統到模組逐層定義設計, 右邊則用 acceptance test、system test、integration test 與 unit test 逐層驗證｡ 左邊每做出一個決定, 右邊就應該有一個能觀察這項決定是否成立的方法; 中間谷底的是 coding, 透過真正的 "開發" 才能產出可執行的程式碼, 你才有機會爬到右邊的山壁, 逐一驗證需求, 把兩邊連接起來｡

我在這次實驗中做的 contract review、DX review、schema simulation 與 decision table, 本質上就是在 coding 以前先釘錨, 先把橋的兩端固定下來而已｡ Contract 說明這個邊界應該如何被使用, scenario 與 testcase 說明什麼結果才算正確｡ 當左右兩端都清楚以後, 中間仍然可能有很多程式碼要寫, 但這些工作已經有明確的方向, 也有 build、test 與 blackbox test 可以持續校正｡ 這時把實作交給 Agent, 才不只是希望它做對, 而是系統本身就有辦法判定它有沒有做對｡

AI 改變最多的, 就是 coding 本身, 也就是 V-Model 最底下的部分, 想像這個比喻, AI 就像是溪水, 不斷的往上漲, 你還堅持手工寫 code 的話, 終究會被溪水淹沒的, 未來還是需要能寫 code 的人才, 但是那會像是潛水夫, 只有特殊需求時你才需要全身裝備的下潛作業, 大部分的任務, 搭船或是過橋就能解決｡

因此, 世界正在改變, 當水淹上來, 要適應的是改搭船 (探索), 或是搭橋讓大部隊直接用走的就能走過去｡ 架構師該扮演的是搭船去探索最佳路徑的人, 而組織內應該要有人把最佳路徑規模化, 變成穩固可靠的大橋, 讓大部隊用走的就能走過去｡ 這不就是兩種最關鍵的角色嗎? 一個是掌握軟體規格的人 (架構師的本質), 另一個是 Harness Maintainer, 負責替團隊把 Harness 搭建起來的人｡





![alt text](/images/2026-07-08-devopsdays-aiera-architect-showcase/image-8.png)

我在公司內部有個實際的專案, 開發的是 agent platform, 有趣的是團隊的組成, 只有四個人, 一個是決定產品走向的 PO (Product Owner), 一個是決定產品 UX (User Experience) 的設計師, 另外兩個就是都是有多年經驗的 Architect (包括我), 我們兩位就共同分攤了系統的規格決策, 以及整體運作的 Harness Maintainer, 我們同時不斷的產出高品質的架構設計決策, 也不斷的調整優化 Harness Engineering, 讓定案的規格能夠快速的交付｡

簡單的說, 實際操作就是上面的做法, 這也是我們團隊並沒有配置 "programmer" 角色的原因｡ 因為我們定完規格後, 就 "順手" 交給 agent 就夠了, 要讓 agent 有效率的自主運行, 其實真正的瓶頸不是模型的能力, 而是你的規格準備的是否足夠充分, 跟你的基礎能力是否足夠紮實｡


![alt text](/images/2026-07-08-devopsdays-aiera-architect-showcase/image-9.png)

這段我點出了最關鍵的一點: 影響 agent 能力的因素, 大致可以分兩類, 一個是模型跟工具, 屬於外面買的到的, 大家都差不多 (除了付不起 token 的例外), 我測試用的 codex + gpt5.5, claude code + fable5 都是大家有訂閱就能用的東西; 而真正有差異的, 是內部團隊的準備程度. 我在這篇探討的都是規格, 但是實際上還有 context 的掌握能力 (這我這篇沒有談到), 這些的成熟度, 才是真正在業界上會造成差異的主要因素｡



## 4.5, Summary and Take Away ...

最後, 這頁簡報是演講的收尾, 我也拿來當作這篇文章的收尾...

![alt text](/images/2026-07-08-devopsdays-aiera-architect-showcase/image-10.png)

如果各位都還有心繼續在軟體開發領域繼續發展, 面對 AI 的浪潮, 我給大家三個建議:

1. **對於你的服務能否持續成長**:  
我認為回到根本, 只要顧好兩件事情, 一個是隨時維持你的服務架構正確, 另一個是隨時維持你的團隊運作的紀律, 而這兩件事情你必須高度擁抱 AI, 找出最有效率的做法｡ 我這篇文章示範了 "隨時維持服務架構正確" 的示範, 我的流程都是高度依據架構師的屬性, 讓 agent 來配合, 最大化架構師決定規格的效率｡ 因為我知道這是最大的瓶頸, 因此不是人去配合 AI, 而是讓 AI 來輔助, 讓瓶頸能盡可能的發揮最大效率｡ 

2. **對於你的團隊能否持續成長**:  
未來團隊的運作, 一定是高度依賴 Agent 來運作. 這點我在台上其實講了很多, 但是我在這篇文章都沒有提到 XDD (這篇是 "補完"), 有興趣的可以先看我釋出的簡報, 或是共筆, 或是等我有機會再補文章說明...

3. **對於你個人能否持續成長**:  
其實這個觀點我也在 facebook 提過好多次了, 簡單的說現在是 AI 已經在 coding 領域夠成熟了, 成熟到你不再有疑慮把 coding 任務交給他的程度了｡ 不過如我示範, 你還是要有 coding 能力 (以我的例子: 我需要有個夠熟悉的程式語言 "母語", 來跟 agent 有效率的溝通規格), 但是當你大量依賴 agent 來負責 coding 時你還有辦法掌握這樣的能力嗎?  在這時代, 你必須反過來, 讓 agent 替你完成任務後, 務必跟上, 方法就是看看 agent 怎麼解決問題, 然後把你完全搞不懂的部分, 多花一點 token 在你身上, 問到你理解為止

其實, 回到這頁簡報, 這就是最後這頁我想表達的觀點啊, AI 可以 10x 加速軟體的發展, 加速有兩個意義, 一個是加速 "成長", 一個是加速 "衰敗", 過去軟體迭代到一定程度就會崩壞 (技術債太多, 整個打掉重練), 試問, 你的服務配合 AI 加速之後會是哪一種? 原本 10 年壽命的服務, 是 1 年就要打掉重練? 還是 10 年?

關鍵就是第一點, 你有沒有隨時維持你的服務架構正確?

我的經驗是, 如果 AI 真的能替你帶來短時間 10x 的效率改善, 別把他都用在開發新功能上, 我建議 60% 用在新功能開發, 30% 用在持續重構與優化體質, 10% 用在提升你自身能力

看懂這點後, 好好想想目前的策略, AI 的加速是必然的, 多學習與掌握 AI 技能也是必要的, 但是別忘了重點還是在你的團隊身上, 團隊的成熟度才是最大的競爭優勢啊!

