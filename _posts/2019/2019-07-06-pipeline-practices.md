---
layout: post
title: "後端工程師必備: 平行任務處理的思考練習"
categories:
tags: ["系列文章", "架構師", "Practices"]
published: true
comments: true
redirect_from:
logo: /wp-content/images/2019-07-06-pipeline-practices/logo.png
---

前面兩篇聊了不少 CLI / PIPELINE 開發的技巧跟基本功夫，這篇換個方式，來聊聊後端工程師該如何自己練習基本功夫吧。這次談的是 "精準" 控制的練習。

![](/wp-content/images/2019-07-06-pipeline-practices/logo.png)

我在公司負責架構的團隊，兩個月前，我出了個練習題讓團隊的人練習，目的是測驗大家對於處理大量複雜的任務的精準程度。所謂的 "精準"，是指你腦袋裡面能很清楚的掌握你 "期望" 程式該怎麼跑，以及實際上你的程式是否真的如你預期的執行。這篇文章，我想換個方式，把這練習題的 source code 公開出來，用實際的 Hands-On Labs 練習的方式來進行。有興趣的朋友可以親自練習看看。練習的目的，是讓你思考如何精準的處理任務，而不是學習一堆大部頭的框架，因此我設計的這練習題，你只要熟悉基本的 C# 語法與 BCL (Basic Class Library) 就足以應付了，困難的地方在於你如何解決問題。

練習可以很簡單，也可以很複雜；我還蠻想試看看收集大家的解法，在這篇文章的後半段統一做個評論的；如果你願意將你的 solution PR 放上來，我會在後半段用我的角度幫你 code review 當作回報。之前會想在內部讓 team member 做這練習，目的很簡單，現在的工程師越來越容易忽略掉一些開發的基礎能力，面臨問題就越來越依賴外部的工具或服務來解決。使用不得當，往往就會在執行效率，程式碼維護，或是系統維運的階段付出代價。我們都用 public cloud, 光是 VM 的 instance 數量就超過百台，工程師們你知道你寫的 code 會直接反映在成本上嗎? 只要改善 1% 的效能，每個月的費用成本就可以降低 1% ..., 這情況在你的流量很大的時候，加上背後的運算資源都來自雲端服務時會更明顯...。

因此，在公司我都會跟工程師在一對一面談的時候，問問 developer 自己是否想過這些問題:

1. 你是否能很 **精準** 的掌控你寫出來的 code ? 
1. 你是否清楚了解你面對的問題 **理想** 的效能在哪裡? 
1. 針對效能這件事，你是否有明確的 **指標** 來量化及評斷每個 solution 的好壞? 
1. 你的解法離 **理想** 情況還有多遠? 是否還有改善空間? 還是已經到理論極限了? 

<!--more-->

後端工程師免不了必須解決很多效能及穩定度的問題，因此 "精準" 的掌握你程式碼在做啥事，我覺得是很關鍵的一點。商業邏輯我想你寫得出來大概都沒問題，但是每當我講到平行處理 (例如非同步、多執行續、或是 scale out) 等等議題時，我發現能清楚掌握的人就少的多了。大部分的人都停留在多開幾個 threads, 或是丟到 thread pool, 或是多開幾個 VM 用 scale out 的方式來解決就了事了。如果討論我們多執行緒應該怎麼安排這些任務的處理規則，能精準地寫出來的人又少了一大半...。

我設計了一個 class library (```ParallelProcessPractice.Core```), 函式庫內我定義了一個類別 ```MyTask```，他的 instance 必須按照順序呼叫 ```DoStep1()```, ```DoStep2()```, ```DoStep3()``` 才算完成。練習的題目就是: 你必須處理完 1000 個 ```MyTask``` 物件才算完成任務。處理過程中有些限制需要留意:

1. 每個 task instance 的 Step 必須按照順序進行。
1. 每個 Step 的平行處理數量是有上限的。
1. 不同的 Step 執行時需要花費的時間不同。
1. 每個 task instance, 每個 step 執行過程都需要 allocate 不同的 memory, step 一開始就會 allocate memory, 結束才會 free memory。

會定義這些規則，目的就是希望 developer 在解題的過程中，必須知道你用的方式會花費多少資源? 例如 (4), 你就不能無限制地開啟任意數量的 threads 來處理, 過多的 task 都在處理中, 你的 memory 可能會爆掉；受限於 (1) 的限制, 你開啟過多 threads 不會得到對等的效能提升，會被 (2) 的上限綁住，過多的 threads 只是浪費資源而已。

題目會用 ```IEnumerable<MyTask>``` 的方式交付 100 個物件，你的目標是寫一個 ```Runner``` 接到 ```MyTask```, 把它消化完畢就對了。不限定你用任何方式或是框架來處理。不過，我會看這幾個指標來判定你做出來的品質:

1. 主要目標:   是否有確實完成每個 Task? 每個 Task 都必須按照順序完成每個 Step。
1. 品質指標 1: 過程中最大的 WIP (WIP: Work In Progress, 半成品, 只要開始 step1 而未完成的 task 都算) 數量。
1. 品質指標 2: 過程中占用的 memory size 最大值 (max memory allocated)。
1. 品質指標 3: 程式啟動後，第一個 task 完成所需要花費的時間 (TTFT, time to first task)。
1. 品質指標 4: 所有 Task 處理完畢的時間。

準備好接受挑戰了嗎? 現在就去下載題目來試著解看看吧! 這篇文章我會分成前後兩段來發布。前半先發布題目，如果你有意願的話，在一個月內 (時間 FB 我會說明)，在 GitHub 把你的 Runner 發 Pull Request 給我, 我會在後半段發布的內放上 PR 給我的 code, 並且評論一下每種解法的優缺點。

平常在做 code review 很難深入到這樣的問題啊 (要是真正有 deadline 的專案，用這樣的標準來 code review, 大概整段 code 都會被我翻掉)，在動手寫 code 之前就先做好充分練習才是根本之道，因此我就出了這樣的練習題給 team member 試看看，發現效果還不錯，於是就擴大範圍，也讓其他有興趣的朋友們參與看看。

當然我還有另一個動機: 招募。我也希望能藉這機會找到有心想磨練自己基本功的工程師，這樣的 code 交流我相信比面試聊上一個小時精準的多了。最重要的是透過這樣的方式，你會更清楚知道團隊的要求，你也可以藉這機會試試自己能力；加入團隊後會有更多這樣的挑戰與應用的機會。這不見得是件輕鬆的事情，但是如果你有興趣，這絕對是個難得的機會。





# 解題規則說明

現在就開始捲起袖子，動手練習吧! Source Code 請到我的 GitHub Repo: [ParallelProcessPractice](https://github.com/andrew0928/ParallelProcessPractice) 自行取用。


## 1, 建立並執行你的 TaskRunner

規則很簡單，我把題目的部分都封裝在 ```ParallelProcessPractice.Core``` 這個 .NET core 的 class library 內了。你只要另外用 console app project, 繼承 ```TaskRunnerBase```, 寫一個你自己版本的 ```TaskRunner```, 然後在 ```Main``` 裡面啟動他就可以了。

隨題目我附上一個很無腦的 demo, 只是示範最低標準能 pass 主要目標的版本，單純示範答題規則而已。請參考 ```AndrewDemo``` 這個 project, 基本上就是用 for loop 把每個 task 的 ```DoTaskN()``` 從 1 ~ 3 分別執行一次而已，完全沒有平行處理也沒有最佳化，各位就當作墊底的競爭者吧，理論上你應該不會寫出比這個 demo 還慢的版本...

規則很簡單，第一，先準備一個你的 ```TaskRunner```:

```csharp

public class AndrewTaskRunner : TaskRunnerBase
{
    public override void Run(IEnumerable<MyTask> tasks)
    {
        foreach (var task in tasks)
        {
            task.DoStepN(1);
            task.DoStepN(2);
            task.DoStepN(3);
        }
    }
}

```

然後，在 ```Main()``` 內這樣啟動你的 Runner 就夠了:


```csharp

class Program
{
    static void Main(string[] args)
    {
        TaskRunnerBase run = new AndrewTaskRunner();
        run.ExecuteTasks(100);
    }

}

```    



## 2, 檢查 console output

執行完畢之後，會有兩個地方可以看到執行結果。第一個是 console output:

```logs

Execution Summary: AndrewDemo.AndrewTaskRunner, PASS

* Max WIP:
  - ALL:      1
  - Step #1:  1
  - Step #2:  1
  - Step #3:  1

* Used Resources:
  - Memory Usage (Peak):  1536
  - Context Switch Count: 300

* Waiting (Lead) Time:
  - Time To First Task Completed: 1443.1671 msec
  - Time To Last Task Completed:  143032.4147 msec
  - Total Waiting Time: 7223482.8365 / msec, Average Waiting Time: 72234.828365

* Execute Count:
  - Total:   100
  - Success: 100
  - Failure: 0
  - Complete Step #1: 100
  - Complete Step #2: 100
  - Complete Step #3: 100

C:\Program Files\dotnet\dotnet.exe (process 6368) exited with code 0.
Press any key to close this window . . .

```



## 3, 進階監控資訊 (csv) 說明

Console output, 基本上就已經顯示了主要目標與品質目標的數值了。不過只看這些指標，對於我要求的 "精準" 還有段距離... 我同時準備了另一個紀錄檔，在跟執行檔同目錄會輸出成 .csv, 可以看到執行過程中更詳細的數據, 裡面會有執行過程中不斷記錄下來的幾個關鍵指標:

```csv

TS,MEM,WIP_ALL,WIP1,WIP2,WIP3,THREADS_COUNT,ENTER1,ENTER2,ENTER3,EXIT1,EXIT2,EXIT3,T1,T2,T3,T4,T5,T6,T7,T8,T9,T10,T11,T12,T13,T14,T15,T16,T17,T18,T19,T20,T21,T22,T23,T24,T25,T26,T27,T28,T29,T30
8,0,0,0,0,0,0,0,0,0,0,0,0,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
32,1536,1,1,0,0,1,1,0,0,0,0,0,1#1,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
60,1536,1,1,0,0,1,1,0,0,0,0,0,1#1,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
90,1536,1,1,0,0,1,1,0,0,0,0,0,1#1,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
120,1536,1,1,0,0,1,1,0,0,0,0,0,1#1,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
150,1536,1,1,0,0,1,1,0,0,0,0,0,1#1,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
180,1536,1,1,0,0,1,1,0,0,0,0,0,1#1,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
210,1536,1,1,0,0,1,1,0,0,0,0,0,1#1,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
240,1536,1,1,0,0,1,1,0,0,0,0,0,1#1,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
(以下略)

```

繼續之前先簡單說明一下欄位的意義:

* TS (time stamp): 該筆資料的時間，從 Runner 啟動開始計算 (單位: msec)。
* MEM: 當下模擬的 memory 使用量
* WIP(ALL,1,2,3): 當下在處理中狀態的 Task 總數
* THREADS_COUNT: 當下所有正在處理 Task 的執行緒總數
* ENTER / EXIT: 當下已經開始/已經結束第N個步驟的 Task 統計總數
* T1 ~ T30: 當下每個 thread (最多顯示 30 個執行緒) 正在處理的 Task 資訊 (格式: {Task序號}#{Step} )


做成 csv 為的是方便你用 excel 打開，直接用圖表來將你的執行成效視覺化用的。舉例來說，前兩個欄位 ```TS``` (time stamp, msec) 跟 ```MEM``` (allocated memory, bytes) 我把它用 excel 繪製成圖表的話，就可以看到這樣的 chart, 模擬像是你用 visual studio profiler 這類工具來監控你程式執行過程:

![](/wp-content/images/2019-07-06-pipeline-practices/021612.png)



不過，這個版本的 code 實在太單調了，完全看不出啥效果... 我換一個我自己用 thread pool 的 Runner, 拿 ```TS``` 當 X 軸， ```MEM``` 當 Y 軸，就可以看記憶體使用量:

![](/wp-content/images/2019-07-06-pipeline-practices/021935.png)



其實 .csv 內還藏了不少數據, 再來看看其他數據: ```WIP1``` ~ ```WIP3```, ```WIP_ALL```, 分別代表在 Step1 ~ Step3, 以及所有未完成的 task(s) 總數:

![](/wp-content/images/2019-07-06-pipeline-practices/022611.png)


如果我想看看 thread pool 背後到底動用了多少執行緒出來工作，打開 ```THREADS_COUNT``` 欄位可以看到過程中同時有多少個 threads 並行:

![](/wp-content/images/2019-07-06-pipeline-practices/022835.png)


最後，如果我真的想看每個瞬間，每個 thread 到底都在幹嘛，來看看最後 ```T1``` ~ ```T30``` 的欄位... 這就不是看圖表了，直接看表格的內容。我在 EXCEL 表格的格式加了工，把同一個 Task 用粗的框線框起來，讓視覺化更明顯一點:

![](/wp-content/images/2019-07-06-pipeline-practices/023121.png)

```TS``` 代表程式開始執行的時間 (單位: msec), ```T1``` ~ ```T30``` 則代表我最多會顯示每個時間點，每個 thread 都在做啥事，```T1``` 代表第一個 thread, ```T2``` 代表第二個，以此類推。至於表格內的數字，如 ```14#1```, 則代表 ```第 14 個 task 的第一個步驟```，我加上了框線，讓大家看得清楚一點，從上到下，可以看到你的 task 是如何被分配到每個 threads 執行的。你會發現，因為平行運算被受到限制，並不是每個 threads 都隨時保持忙碌的，中間空白的部分代表這個 thread 正在發呆，沒有任務可以進行。

到目前為止，這些資訊都是為了讓你 **精準** 的了解你的 code 到底是怎麼跑的，對於效能好壞也有個明確的指標可以評估。寫到這裡，你應該有所有足夠的資訊，可以用來了解你的 solution 實際執行狀況了。剩下的考驗，就是你是否能想出最佳的解法? 這些資訊可以協助你驗證，你的 code 是否真的很精準地照你的想法在執行?






# 品質指標的挑選

前一段說明了答題的規則，以及如何看輸出的資訊。接下來這段我們就來探討一下這些指標背後的意義與用意吧。

要通過這個測驗，其實很簡單，我附上的 ```AndrewDemo``` project, 寫個 for loop, 10 行以內的程式碼就可以搞定了，但是要比較出好壞，那就要花點心思。我這邊說明一下為何我要挑選這幾個指標來評斷 code 的優劣。這些指標，其實都可以對應到各位日常碰到的實際案例，我就一一來說明。很多指標其實在前兩篇也都帶到了，有興趣的朋友也可以參考前面的文章:

* 後端工程師必備: [CLI + PIPELINE 開發技巧](/2019/06/15/netcli-pipeline/), 2019/06/15
* 後端工程師必備: [CLI 傳遞物件的處理技巧](/2019/06/20/netcli-tips/), 2019/06/20


## 指標: 最大處理中任務數 (Max WIP)

這裡指的 "半成品" (WIP, Work In Progress) 數, 就是指同一瞬間，有多少 Task 是處於 ```DoStepN(1)``` 已經開始，而 ```DoStepN(3)``` 還沒完全結束的階段。

為何我會拿 WIP 當作指標? 對應到現實世界的 Task, 通常啟動後就會占用一些資源，從 temp file, memory cahce, memory buffer, 甚至是為了處理任務過程中需要的 temp object 等等都算。如果你用了各種平行處理的技巧來加速，別忘了每存在一個 WIP, 背後這個 Task 就要占用一些資源, 直到 Task 結束為止。這些資源要在 ```DoStepN(3)``` 結束後才會被釋放，如果佔用的是很有限 (或是成本很高) 的資源，那麼你必須在平行處理的數量與 WIP 數量之間取得平衡。

WIP 過高，先不論對效能的影響，如果對於關鍵資源 (如 memory) 敏感一點的環境, 也許你的系統撐不過尖峰就會掛掉了。因此這次的題目，會監控 Runner 全程執行過程中，WIP 的最大值，當作 max(WIP) 指標。


## 指標: 第一個任務完成時間 (Time To First Task, TTFT)

熟悉 SCRUM 的大概都對 WIP 不陌生，這名詞我的卻是從那邊借來用的。另一個 SCRUM 在做任務管理的指標就是 Lead Time (交期, 從需求提供到任務完成交付的時間)。這邊我也拿 Lead Time 當作指標之一。不過我比較偏好 TTFT (Time To First Task completed) 這名詞。這名詞我是從 Browser 的開發工具那邊學來的用法。監控網頁下載效率，有個很重要的指標 TTFB (Time To First Byte) 也是一樣的意思。

TTFT, 指的是 Runner 啟動之後, 完成全部步驟的第一個 Task 要花費的時間 (不限定一定要按照 Task 的順序執行)。TTFT 會直接影響使用者的感受，有大量 Task 交付執行時，你能完成第一個的時間，就是使用者視角看到的 Lead Time。過去在念作業系統 (OS, Operation System) 時, 對於多工排程的機制也有類似的指標，那個叫 "平均等待時間"，意思是每個 Task 從被交付到 OS 開始 (這裡指的是 Runner 啟動) 到 Task 完成的時間平均。TTFT 越大，代表你花越多時間在 "等待" 某些階段的完成。

我在這個例子，我挑選 Lead Time, 而不挑選 Execution Time 的原因是: Lead Time 包含 Task 等待被處理的時間 + 執行時間。執行時間考驗的是 Task 內的效率或是機器的效率, 在這了練習題內是固定的。我的重點在於你的 Runner 安排規劃的能力，因此我挑選 lead time, 更能代表終端使用者的感受。如果你能越早交付第一個 Task, 使用者就會感受到系統的回應速度越快，如果使用者端能配合，或許有後續的任務就能越快啟動。這是我挑選這個指標的用意。



## 指標: 所有任務完成時間 (Time To Last Task, TTLT)

相較於 TTFT 在意第一個 Task 完成的時間，另一個代表整體效能的指標則是整體完成時間。在互動的體驗不是那麼重要的情況下 (例如半夜的批次作業)，有時整體效能反而更為重要。因此能代表整體效能的，我挑了另一個指標: 最後一個 Task 的 lead time。如果硬要跟 TTFT 來對比，那這個指標就是 TTLT (Time To Last Task completed)。這指標完全不管過程中你如何交付 Task 的，只看最後一筆的交付時間，這指標代表整體的處理效率。

有些情況下，TTFT / TTLT 哪個重要，其實很難斷定，完全看你對於系統的服務品質怎麼定義。舉例來說，當 Task 的數量很大的時候，你能否忍受一個明明只要一秒鐘就能完成的任務，卻要在 1 小時後才能得到結果，換來的代價可能是整體完成的時間可以加速 30%, 或是執行的成本降低 30% ? 不同的考量，會影響這些指標的重要程度。

我在這個案例，由於我考量的是 pipeline, 越快完成第一個任務，我後續的階段就能越快開始，因此我把 TTFT 的重要性排在前面。




## 指標: 平均完成時間 (Average Lead Time)

這是從 OS 排程那邊學來的另一個指標。只看第一個任務，跟只看最後一個任務的完成時間，其實都是兩個極端。老實說我要是知道規則還蠻容易作弊的 XDDD, 假設我整批處理能縮短 30% 的執行時間，那麼為了 KPI 好看，我可以只處理第一筆，然後就交付成績；後面 2 ~ N 筆再用最有效率的做法，再最後才一次交付 2 ~ N 筆 Task 的成果，來衝這兩個 KPI 帳面上的數字...

當然這樣就本末倒置了，使用者體驗一定是不好的啊，因此我追加一個 OS 提到的指標: 平均等待時間。

這指標的定義是:每個 Task 的交期的平均值。這個案例裡，就是每個 Task 從 Runner 啟動開始，到 ```DoStepN(3)``` 完成為止的時間總平均。這是介於 TTFT 與 TTLT 中間的指標，越低代表使用者需要等待 (就是 Lead Time) 的時間越短。



# 下一步: 提交你的 TaskRunner !

有看過前面兩篇探討 CLI 的文章的話，應該不難發現這練習題要解決的問題，跟前面的 pipeline 很類似，連同我探討解決方式優劣的方式 (指標定義) 也很雷同。的確，我就是把這些問題抽象化之後，化簡為類似 LeetCode 那樣的模式來進行而已。

我在公司內部，試著進行這樣的練習，其實成效還不錯，藉著幾個明確的指標，這練習成功的刺激工程師們想清楚他的解決方式的處理細節，為何結果會是這樣? 跟理想的解決方案還有哪些差距? 要如何才能做得到... 等等。

除了練習之外，後續在幾個實際上的 project 面臨的效能問題，也能透過調整 Task 的 [參數設定檔](https://github.com/andrew0928/ParallelProcessPractice/blob/master/ParallelProcessPractice.Core/PracticeSettings.cs)，同時找出該校能問題最關鍵的品質指標是哪一個，接下來的問題就迎刃而解了。很多大師都說 "問對問題，就解決了一半" 是很有道理的，這樣的練習題就能具體的用 code 把你的問題定義清楚，剩下的就是找出解決方式，把品質指標改善到預期的範圍內。

當你覺得技術跟框架學不完，或是都覺得已經很熟練了，但是碰到問題有時還是不得其門而入時，不彷暫時跳出 "skill" 層面的學習, 讓自己有些空間思考問題的本質，並且試著挑戰看看吧! 

有興趣的朋友，歡迎 PR 你的練習結果給我。我會在後續的文章內容內來探討每種做法的優缺點與適用情境。探討會擺在下一章節內，有任何討論可以在底下的 comments, 或是到我的 facebook 粉絲專頁留言給我都歡迎!





# Solution Review (敬請期待)