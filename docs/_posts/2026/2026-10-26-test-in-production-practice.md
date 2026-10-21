---
layout: post
title: "TiP, Test In Production 的刻意練習"
categories:
- "系列文章: 架構師觀點"
tags: ["架構師觀點","技術隨筆"]
published: false
comments_disqus: false
comments_facebook: false
comments_gitalk: false
redirect_from:
logo: 
---








我平常會習慣捕捉工作上看到的 "難題", 覺得有意思, 有研究價值的, 就會挑出來親自想個情境 PoC 練習解題, 這是我快速獲取經驗的方法, 這次碰到了一個新的題目, 就是怎麼有效的建置測試環境? 測試環境建立並不難, 困難的是新環境怎麼模擬既有環境的 "資料" ? 為了要能在這些基礎上正常運作, 沒有好好的設計, 這還真的是件棘手的事情... 

這看起來像是個老問題, 不過因為最近我都在研究 design for agents 的軟體設計, 這些資料, 跟這個環境, 就是這個應用程式要提供給 agent 最重要的 context 啊, 這需求範圍遠比過去 "要有資料才能測試" 的涵蓋面更大了, 也因為 agent 這個課題, 再度喚起我對他的重視了..




## 1, 寫這篇的動機


測試環境的資料, 真的是個頭痛的題目, 過去 QA 的領域中, 特定的行為都需要有預先安排好的 "資料" 才能顯現, 因此 QA 通常都用 scripts 來建立假資料｡ 好處是很容易重建, 也容易自動化, 但是缺點也是資料 "很假", 看起來就不像真實資料, 不過 QA 用途的測試環境也就測試目的在使用, 這倒也不是太大的問題...


### 1.1, 測試資料的重要性, 從 Data 到 Context

不過, 現在 "資料" 已經提升到另一個維度了, 他不再只是 "Data", 而是 "Context", 一個線上銷售的網站, 背後的資料就足以講出不同的故事了｡ 我為何會在意這個差別? 我先前才在 facebook 聊 "以後的軟體是寫給 Agent 使用的" 這觀點, 而對 Agent 而言, 比起功能是否完整, 相對的 Context 是否完整會來的更重要且關鍵｡

```
Agent 有高度 tool use 的執行能力, 說實在功能給基本有效率的就以足夠, 不用給很多 "懶人" 的技能, 更重要的是語意明確可以任意組合

相對的, Agent 需要更多的 context 讓他理解他現在的狀況, 以及接下來要幹嘛, 已購物網站來說, 如果你授權給 agent 操作, 比起教他怎麼操作購物車跟刷卡付錢, 更重要的是讓他知道網站賣什麼, 你想買什麼, 怎麼買更優惠更划算..., 這就是 context

想像一下, 如果你正在開發這樣的系統, 測試 agent 的行為, 你還有辦法用 "很假" 的測試資料嗎? 如果能有效率的在 "正式環境" 拿真實的資料測試, 不是更理想嗎?
```

也因為 Agent 的成熟, Context 的重要性越來越高了, 測試資料這題對我而言又重新拉上檯面, 我意識到傳統從 QA 角度準備測試環境的各種自動化做法, 已經跟不上這個時代的要求了, 我開始朝向另一條路線找解決方案, 我一開始找的路線是 TiP , Test In Production environment, 在正式環境上面測試 的技巧｡


我決定先選路線, 再決定實作的工程方法; 要準備測試環境的 "資料", 大致上就兩種路線:

- 蓋一個可以安全測試的環境, 然後把 context 都搬過來 ( 要定期, 持續搬移 )
- 變更系統的設計,  "安全" 的在生產環境進行測試 ( 要變更系統架構設計 )

這是兩個不同的路線選擇, (1) 不需要變更既有的設計, 但是需要投資在資料的抄寫, 這方法門檻不高, 但是很煩人, 你要負擔一次性的資料搬移工具的開發, 還有負擔每次轉移產生的費用; 而 (2) 則是押注在大規模的重構, 相對難度高, 但是設計得當能一勞永逸｡ 

現在 Agent 可以做更多 "實作" 層面的任務了, 我覺得可以更貼近需求, 不用過度顧慮開發資源的取捨, 剩下的重點只剩: 該怎麼掌握這樣的需求來規劃架構? 

於是我心理先入為主, 決定挑戰一下 (2) 的可行性了, 開始動手前, 我多花了點時間做研究, 我想先搞清楚兩件事, 一個是我所謂的 "測試", 目標跟意圖到底是什麼? 另一個是, 不要閉門造車, 業界大廠是否有可參考的案例?



### 1.2, 三種不同的 "測試" 意圖

我先梳理了一下研究目的, 平時我在講的 "測試", 實際上有三種不同的意圖包含在內:

1. 測試要驗證的是 "新功能":
   你需要在部署上有所區隔, 最單純的是建立 develop / staging / production 環境, 完全隔離; 細緻一點的, 可以透過一些手段, 在 production 環境上有條件的開放部分未完全驗證成功的功能 ( 透過 feature flag, 做金絲雀部署 ) 等等都是可行的做法
   
2. 測試要驗證的是 "新客戶":
   你需要的是正規的功能 (早已測試過的), 但是要提供一個不影響業務行為的環境或方式給客戶使用 (例如交易不會出貨, 信用卡支付不會扣款), 粗暴一點的手段可以用 (1) 來滿足, 細緻一點的會在產品設計上直接支援這類需求 (註記)
   
3. 測試要驗證的是 "新開發人員"
   你需要的是正規的整合介面 (早已測試過的 API), 但是要提供一個不影響業務行為的環境或方式給合作夥伴使用 (同上, 例如交易不會出貨, 信用卡支付不會扣款, 通知信件不會真的發出去), 一樣可以粗暴一點提供 (1), 當然也有更細緻的做法

(1), 這是典型的 QA / Testing 議題, 要驗證的是你的系統本身, 尤其是新增的功能測試｡ 這類目的方法論都很成熟了, 我不大需要重新發明他, 正確的使用常見的幾種技巧就已足夠 ( ex: feature flag, A/B test 等等 ), 有很多 DevOps 的 best practice 可以參考了, 這個我略過; 

我想多談的是 (2) 跟 (3) 的測試,  這比較像是 "評估", 只是需要有個隔離的機制, 避免影響真正的業務行為 (例如金流, 物流, 銷售) 等等｡ (2) 是新客戶要評估你的系統合不合用, 而 (3) 真正要測試的是 "外部" 開發中的系統, 能否順利的跟你的系統對接? 這兩類的共通點是: 你的系統本身是已經定案, 穩定且可靠的, 而不是不斷變更或是開發中的功能｡

搞清楚這三種 "測試", 開始抓到中間的差別了, 我意識到我真正需要的是在正確的顆粒度上做到 "隔離", 隔離邊界的拿捏看來是很重要的決策, 我決定先繼續做完研究, 再回頭來思考我自己的邊界該抓在哪裡｡

## 2, 業界做法研究


接下來, 就是找大廠的參考案例了, 最後我找了有代表性的三家: Salesforce / Shopify / Stripe, 剛好是三種完全不同的 patterns.

我覺得挺有意思的, 這三家的差別, 不在技術能力的優劣, 三家都是國際級的大廠, 我覺得都在水準之上了, 這三種模式, 反應了三家公司的業務需求跟技術選型的不同... , 我就逐一來說明一下:

(1) Salesforce, 提供企業層級付費的 Sandbox
https://www.salesforce.com/ap/platform/sandboxes-environments/

做法: 提供完全隔離的環境 ( Sandbox ), 同時會幫你複製正式環境的資料與設定

基本上就是客戶花錢買獨立的環境建置 (Sandbox), 你會得到一個完全一致的 Sandbox, 有你的真實環境資料, 設定; Salesforce 會幫你搞定 replicas 的問題, 讓你能放心測試; 正式環境的資料會抄寫過來, 你在 Sandbox 做的變更也能選擇性的寫回去...

這堪稱理想的方案, 但是代價就是用錢堆出來的, 基礎建設的成本完全是兩倍 (甚至更多, 可能有些共用服務沒有那麼多客戶來分攤一次性成本), 額外的跨環境 Replication 機制的設計開發也是額外成本 (每增加一個新功能, 你就要檢查新功能能否正確的被複寫)

[Sandbox 類型](https://www.salesforce.com/platform/sandboxes-environments/salesforce-sandbox-guide/)、[Change Sets](https://help.salesforce.com/s/articleView?id=changesets.htm&language=en_US&type=0)、[定價](https://www.salesforce.com/ap/platform/sandboxes-environments/pricing/)


(2) Shopify, 提供開發者替客戶建立 development shop
https://www.shopify.com/partners/blog/how-to-build-and-transfer-a-development-store

做法: 免費建立測試商店, 需密碼存取, 只限模擬交易, 無法使用真實世界的金流

Shopify 特地為了 Partner 準備了這樣的服務: 你可以替客戶開一個 Development Store, 沒有額外的費用 (真佛心), 而且這 Shop 將來是可以直接轉移給客戶使用的, 在這個模式下, development store 跟一般 live store 在功能上有這些差別:

1. 免月費
2. 強制密碼保護 (一般訪客無法直接瀏覽, 需要密碼)
3. 只能使用模擬金流 (無法真實處理信用卡付款)

這是個對開發者很友善的設計, 背後其實是有成本的, 不過 Shopify 大概是想說這些將來都能轉換成真的客戶, 所以不收費, 但是他在背後的系統設計, 完全是從產品功能來定義的, 不是在 infrastructure 層級來隔離｡

這邊我開始看到很明確的 "業務邊界", 就是交易｡ 有一條明確的界線絕對不能跨過去, 就是金流跟交易; 一旦你用真正的信用卡, 那這間 development store 就不再只是個 "development" store 了, 同樣的問題也會發生在業績計算, 發票, 物流等等 (模擬交易不應該開發票, 也不應該觸發真正的物流機制) ...

Shopify 的產品 / 架構團隊, 應該花了不少心思設計這樣的體系, 來支撐他們的業務形態

現行文件已區分 **Dev stores** 與 **Client transfer stores**，前者不能轉交客戶。平台禁止真實交易、限制有效運送面單，也不足以推論所有第三方發票／物流整合都會自動隔離。[現行商店分類](https://shopify.dev/docs/apps/build/stores)、[限制說明](https://help.shopify.com/en/partners/manage-clients-stores/client-transfer-stores)|

(3) Stripe, 提供客戶 "Test Mode" API token, 不需真實金流就能測試完整流程
https://docs.stripe.com/testing
https://docs.stripe.com/testing-use-cases


做法: 同一套 API 透過不同 key 選擇正式／測試用途, 正式付款跟測試付款都會走完相同流程, 測試付款不經真實金流網路。


Stripe 的做法更細緻了, 看文件說明, 應該是在同一組 API 背後, 靠不同的 APIKEY 區隔 Live Mode 跟 Test Mode, 兩者會共享 account 的設定, 但是產生的交易資料是隔離的, 測試的交易也會走完完整的流程, 對開發者來說是最無痛的做法, 大概就是換掉 APIKEY 就可以切換到正式環境, 而測試資料的隔離 (例如帳務等等相關功能) Stripe 端都已經處理妥當, 你可以放心在正式環境測試, 不用擔心弄髒正式環境

Stripe 隔離涵蓋 Customer、Product 等 API 物件，**不只交易**。本次查閱的官方文件沒有揭露 database／table 的實體配置；測試卡也不會把 live key 的請求自動轉成 test mode。不能由此推論它免除了測試資料準備。[API 模式判定](https://docs.stripe.com/api)、[物件隔離規則](https://docs.stripe.com/keys)






## 3, 背後的設計模式解析


整體來看, 大家都是在某種邊界做好隔離, 來區分 Live / Test Mode, 而這三家代表廠商的差異在於:

Salesforce ( CRM / SaaS 領導廠商 ) - Hosting Environment 隔離
Shopify ( E-Commerce Platform 領導廠商) - Store 隔離
Stripe ( Payment Service 領導廠商 ) - Test Mode 隔離

不同廠商的背景, 不同的設計 , 不同的做法 , 帶來不同的隔離層級, 同時也帶來不同的抽象層級, 有著完全不同的實作方式...


整體看來, 我覺得 Stripe 的設計最貼近我的需求, 雖然背後資料是分開的 (文件這樣寫), 但是在介面上, Stripe 最大化做了整合, 包括:

1. Dashboard 是同一個 (但是你要切換 Sandbox / Account)
2. API endpoint 是同一個 (依靠 APIKEY 來區隔)
3. Webhooks 是同一個 (可同時收到 live / test mode 的 callback, 要靠參數判定)
4. Report / SQL 明確的區隔 (看起來 Report 不會跨 mode 查詢, 部分 Report 只支援 live mode )

其實這就做的很棒了, 感覺背後也是有 Sandbox 的設計, 只是不像 Salesforce / Shopify, 明確的對外就用不同的 tenant / cluster 等層級明確的隔離, 至少 Stripe 讓開發者最大化的感受到這是 "同一個" Account .. 體感上能做到 "我在我申請的正式環境上測試", 而這些機制的安排不會讓我的帳務錯亂 的效果



我相信這是開發團隊深思熟慮後的結果｡ 業界的設計案例研究到這邊告一段落, 我大概能理解各大廠的隔離結構了, 下一個問題是:

如果我要替我的 Andrew Shop 做類似的設計, 我會怎麼做?

就應用, Andrew Shop 比較貼近 Shopify, 但是就做法, 我比較喜歡 Stripe 的 DX ...

我先濃縮設計的取捨, 我覺得每個大廠都是在做這兩個決定, 只是他們的答案不同而已; 同樣的, 我需要決定的是我的 Andrew Shop 這兩個問題的答案應該是什麼?

關鍵決策:

1. 明確的界定測試的邊界在哪裡 ( Live Mode / Test Mode 的邊界 )
2. 明確的界定行為差距 ( Test Mode 邊界內的行為要有哪些不同 )

我試著用這兩個問題, 分別回答一次三個案例的答案..

Salesforce
1. 給測試環境 "完全隔離的基礎建設", 從登入網址開始就完全獨立, (推測) 會有完全隔離的實體環境
2. 所有行為都跟正式環境完全獨立, 只有明確手動的資料搬移

Shopify
1. 多租戶的隔離層級, 可能位於同一個 site / cluster, 但是靠 tenant 的不同來區隔
2. 依據租戶 (店) 決定特定功能是否開放 ( ex: 真實的金流 , 物流 等功能選項 )

Stripe
1. Live Mode / Test Mode Sandbox 的隔離, 但是整合在同一個 API endpoints, 靠不同的 APIKEY 區隔
2. 不同 Sandbox 的資料完全隔離, 物件也不會跨 Sandbox 參照, callback 會標記 mode 作為區隔


那麼, Andrew Shop 呢?

這部份就是我自己的 "許願" 了, 我想先定義我要的開發者測試體驗, 再來決定做法, 理解大廠的設計模式後, 我重新想了一下我的期待: 交易部分我想要像 Stripe 能明確隔離, 但是很難建立或是累積的資料 (例如上架商品等等) 我想要共用.. 

所以, 從我的角度來思考, 我會這樣回答這兩個決策:
1. 針對 "交易" 範圍隔離 ( checkout, orders ), 這範圍內依據交易的執行者 ( customers or credit 來識別 ) 來決定是否為 test mode
   
2. "交易" 資料在隔離層級不互通, 其餘資料共享, 會對實際真實業務產生影響的操作只限定 live mode 能執行

因為更高度的整合了, 所以規則也更難釐清, 因為上架商品跟庫存資訊我不打算隔離, 因此是共用的, 那難題來了, 我用 test credit 買了一件商品並完成結帳成立訂單, 那我到底要不要扣掉庫存?

扣了的話, 測試訂單不收錢, 不出貨, 庫存扣了就間接影響實際銷售了 (有貨但是不能賣), 所以我多了一條原則:

3. 測試的行為, 絕對不能影響真實業務的進行
   (隔離的邊界: 真實業務影響, 任何違背這條規則的設計都視為不合格)

這條規則我範圍開的很大, 只要踩到 "影響真實業務" 的行為, 測試交易就應該避開, 留下 LOG 交代, 其他照舊｡ 以前面的例子來說明, 正式交易成立時應該扣掉庫存, 正式訂單成立應該要發動履約 (出貨, 寄送); 而這些行為在 Andrew Shop 則讓他略過, 這不是對錯, 這是選擇, 我做了選擇可以專注在 "交易執行過程" 的測試, 而這選擇犧牲了後面的測試 (因為被略過了)

切記, 這不代表我這樣做才是對的, 這是因為我知道我的重心在交易的測試, 所以選擇犧牲了其他的測試要求, 比起 "完整" 的設計, 我更在意我有沒有能力依據需求來做正確的設計 / 選擇? 未來有 AI 輔助, 知道怎麼選擇, 比知道完美的設計是什麼更重要, 這些權衡跟取捨, 才是跟 AI 協作的關鍵...

因此, 我把這次要重構變更的範圍想清楚了, 需求濃縮成一段話, 就是:

1. 隔離測試的交易資訊, 需要有獨立的儲存方式 ( database, table, storage ), 範圍為 checkouts, orders
2. 發動交易端需要有明確的識別 ( .isTest ), 建立後不可變更 ( member , payment id )
3. 測試模式必須略過指定的行為, 略過的操作必須在 logs 內說明

我覺得整個研究, 對我而言最有價值的就是這段 "規格" 了, 要是沒有前面那些研究過程, 我是開不出這樣精確的規格的｡ 在這個年代, 你講不出規格, 你就無法期待 AI 做出來的東西是 100% 符合你預期的, 講不出規格, 你也無法把整個系統 (大黑箱) 拆成多個子系統, 個別突破 (呼應到我在 DevOpsDays 2026 提到的 黑箱解構 這頁簡報)

// slides: 



## 4, 按照設計, 實際開發

到了這個步驟, 就是要考量 Andrew Shop 目前的架構, 如何達成前面開的需求規格｡ 我把三條需求, 用系統化的角度重新列一次:

1. 依據交易執行者 (ex: 指定的測試帳號, 指定的測試卡號), 區隔正式與測試的交易行為 (結帳, 訂單)
2. 明確隔離 "交易結果" 的記錄儲存與查詢, 預防資料庫操作的誤區 (ex: 下錯過濾條件導致查詢錯誤, 需要明確跨表 / 跨資料庫查詢才能取得兩類的交易結果)
3. 測試交易的結果不能產生真實商業效果 (ex: 產生真實的金流, 物流, 或是會影響銷售金額或是庫存等結果的行為)

其實我大可以把這需求, 直接丟給 agent 替我處理, 現再 agent 的能力應該都能確實做到沒有問題, 不過就像你跟能力很好的同事合作一樣, 他能解決問題, 但是解決的方式不見得跟你期待的一樣, 如果負責的是你, 這些過程跟細節你也必須確認才行｡

我的做法會 top -> down, 我先定義好主要流程跟架構, 把邊界跟框架都確認下來, 這關守好後, 後面就算做歪了影響也都是局部的錯誤, 那個範圍重做就好｡ 這就好像汽車導航, 你只給目的地, 導航可能帶你走了一條非預期的路線 (例如走高速公路, 但是你想走平面道路等等), 你可以指定幾個關鍵的點 (ex: 要求要走中正橋過河), 其餘讓導航規劃, 這時局部走錯路, 導航會幫你修正回來

我按照我的思考脈絡, 用這六個階段分別執行｡ 這部份我自己 "逆向工程" 我自己開發的 code, 由於我有要求留下重要的決策記錄, 因此事後要還原這些 "過程" 實在太輕鬆了, 底下這段我就試著讓 Agent 幫我整理, 我只做些微潤飾就直接貼上來:

--

1. **先確立不能違反的大原則** (當時還沒有決定實作方式)
    
    > 服務部署在正式環境，測試行為不應產生真實商業效果。
    
    這個原則先排除了兩種看似可行的方案：先執行真實交易再退款／還原，以及只在最後把訂單標成 test。兩者都無法保證過程沒有影響正式業務。
    
    當時明確保留來源判定、資料儲存與 contract，等後續需求收斂才決定。大原則決策被 Harness 自動留下決策記錄 (docs/decisions/2026-10-16-tip-no-real-business-effects.md:15)
    
2. **盤點領域物件，把抽象原則轉成保護範圍。**
    
    接著盤點會持久化的物件，區分兩種責任：
    
    - 需要辨識正式／測試用途，而且建立後不能任意改變用途。
    - 屬於正式業務資源，測試行為不得異動，例如商品、SKU、庫存、預約與時段。
    
    同時確認：身分、權限與業務檢查仍須執行，不能看到 test 就直接成功。
    
    這個分類也曾調整：最初 Cart 被納入用途分類，10/17 縮小實作範圍後，改成 Cart 共用且不標記用途，交易用途到 Checkout 建立時才決定。原始物件分類 (docs/decisions/2026-10-16-tip-domain-object-classification.md:13)、範圍修訂 (docs/decisions/2026-10-17-tip-standard-scope-and-context.md:25)
    
3. **用 Given／When／Then，把原則展開成能觀察結果的案例。**
    
    你沒有停在「不扣庫存」這種描述，而是逐步補上成功、正常失敗、並行及權限案例。例如：
    
    |案例|前提與操作|必須觀察到的結果|
    |---|---|---|
    |AC-001：成功的測試交易|單價 100、庫存 10，測試會員買 2 件|建立 200 元的測試訂單；庫存仍為 10；實際略過的效果有紀錄|
    |AC-003：失敗的測試交易|庫存只有 1，測試會員買 2 件|正常回報庫存不足、不建立訂單；不能虛構「略過扣庫存」紀錄|
    |AC-009：正式與測試並行|庫存 10，正式會員買 3 件、測試會員買 2 件|最後庫存 7；正式統計只增加 1 筆、300 元|
    
    這裡有兩個明確由你補上的驗收要求：**正式統計必須比較實際結果，不能只看 log；只有真正走到、且因 test 略過的操作，才能留下略過紀錄。**逐條確認紀錄 (docs/decisions/2026-10-16-tip-domain-object-classification.md:22)
    
4. **用邊界案例修正過度簡化的規則，進而形成 context 模型。**
    
    最值得寫進文章的是 AC-012 與 AC-013 的對照：
    
    - **AC-012：**測試會員發現正式預約已逾期，系統仍應正常清理正式預約。
    - **AC-013：**系統接手處理測試訂單，後續事件與重試仍須遵守測試限制。
    
    AC-012 原草案曾把到期更新也當成測試寫入而略過，是你明確要求修正的。這組案例顯示，不能只靠最初呼叫者的 test 標記決定全部後續行為。到期整理的修正紀錄 (docs/decisions/2026-10-16-tip-system-expiration-boundary.md:9)
    
    到 10/17，你進一步把判斷依據分成：
    
    - **Identity context：誰正在執行。**
    - **Transaction context：正在處理哪一筆交易，以及它的用途。**
    
    架構負責正確傳遞或恢復資訊，業務操作負責依資訊執行政策。兩類 context 的決策 (docs/decisions/2026-10-17-tip-contract-and-context-boundaries.md:41)
    
5. **收斂 PoC 範圍，再轉成正式規格、合約與測試。**
    
    10/17 確認標準商店優先，暫不實作 PetShop TiP；測試付款以 PaymentId 白名單代表，並在 Checkout 建立時固定用途。
    
    接著把 AC 對應到 `/spec/testcases`，例如 AC-002 展開為正式會員使用測試 PaymentId、會員用途不變、交易用途固定等案例。AC 與正式 testcase 對照 (spec/tip-phase1.md:43)
    
    這裡也有可引用的 TDD 素材：**白名單與 Context 的 21 項新增測試，先確認可編譯但測試失敗，再以相同行為斷言驗證實作轉綠。**這是特定基礎合約的紅綠循環，不能擴寫成「所有 AC 的完整測試一開始就全部寫好了」。TDD 檢查點 (docs/decisions/2026-10-17-tip-allowlist-and-tdd-checkpoint.md:9)
    
6. **Phase 2 之後重新確認隔離要求，追加 Phase 3。**
    
    10/19 的重要決策是：嚴格隔離交易，認證與非交易資料共用；既有交易依保存用途決定 storage 與效果，不依當下 Token 重新分類。
    
    同時修訂商品改價政策：test identity 必須明確被拒絕，不能回報成功但略過寫入。這直接修改了 AC-005，並新增儲存隔離規格與 26 條案例。交易邊界決策 (docs/decisions/2026-10-19-tip-identity-storage-and-access-boundaries.md:17)、追加 Phase 3 的決策 (docs/decisions/2026-10-19-tip-phase3-spec-and-refactor-plan.md:17)
    
    **因此，拆 collection 與商品改價明確拒絕，應寫成後續需求收斂的結果，而不是最初就已定案的完整設計。**

--

回到我親自手寫的文章內容; 上面這些設計過程跑完後 (我不是跑 Waterfall, 我還是跑 Scrum 的原則, 邊設計邊開發, 同時回頭調整設計的順序), 最終定案了這些 AC, 我列出來給各位參考, 看完你會比較有感上面這些決策到底在決定什麼:





**完整 AC 清單如下，採用最新確認版本。**

|AC|驗收重點|本輪範圍|
|---|---|---|
|001 (docs/tip/tip-acceptance-criteria.md:9)|測試會員可完成一般商品結帳；正常計算與驗證，不影響庫存、真實付款、出貨及正式統計；略過效果可追查。|標準商店|
|002 (docs/tip/tip-acceptance-criteria.md:48)|正式會員使用測試 PaymentId，可成立測試交易；會員／Token 仍為正式用途。|標準商店|
|003 (docs/tip/tip-acceptance-criteria.md:73)|測試交易庫存不足時正常失敗，不建立訂單，不產生虛構的略過紀錄。|標準商店|
|004 (docs/tip/tip-acceptance-criteria.md:105)|Member、Token、Checkout、Order 建立後，正式／測試用途不能互轉；其他合法欄位仍可更新。|標準商店|
|005 (docs/tip/tip-acceptance-criteria.md:131)|test identity 修改商品售價必須明確拒絕；商品與後續正式交易的價格不變。|標準商店；P3 修訂|
|006 (docs/tip/tip-acceptance-criteria.md:158)|測試修改 SKU，必要檢查照常；通過後略過更新並留紀錄，SKU、關聯與庫存不變。|標準商店|
|007 (docs/tip/tip-acceptance-criteria.md:185)|測試預約通過檢查後，不建立 Reservation、衍生商品或占用正式時段。|PetShop，未納入|
|008 (docs/tip/tip-acceptance-criteria.md:215)|測試預約遇到已占用時段，正常拒絕，既有正式預約不受影響。|PetShop，未納入|
|009 (docs/tip/tip-acceptance-criteria.md:245)|正式與測試交易並行，兩者用途與效果各自隔離，只有正式交易影響正式業務。|標準商店|
|010 (docs/tip/tip-acceptance-criteria.md:276)|測試會員的購物車增刪正常保存；Cart 不標記用途，不因 test 身分略過寫入。|標準商店|
|011 (docs/tip/tip-acceptance-criteria.md:305)|測試會員不能完成其他會員的 Checkout，即使雙方都是 test。|標準商店|
|012 (docs/tip/tip-acceptance-criteria.md:333)|測試查詢發現正式預約逾期，可通知系統正常清理；不因發現者為 test 而停止整理。|PetShop，未納入|
|013 (docs/tip/tip-acceptance-criteria.md:369)|測試訂單的事件、背景處理與重試維持測試用途，不因改由 System 處理而解除限制。|標準商店|
|014 (docs/tip/tip-acceptance-criteria.md:395)|用途必須明確；遺失或矛盾視為 BUG，阻止效果，不默認成正式交易。|標準商店|
|015 (docs/tip/tip-acceptance-criteria.md:419)|測試預約略過建立後，流程停止；不捏造預約商品接續購物車與結帳。|PetShop，未納入|

至於 coding, 我就真的完全沒介入了, 除了挑出幾個關鍵的 interface / contract 我有肉眼看 code 之外 (很少, 下一段我全部列出來說明), 其他就是跟他講要做哪個階段, 等個十幾分鐘看到他回報寫完了, 我開起來用瀏覽器親自確認幾個情境, 就 commit / push 了



這六個步驟, 我最在意這幾個環節, 因此我全程真正有 "看 code" 的只有這幾個地方, 確保實作出來的結果跟我想要的是一致的:

1. 需要被標記 ".IsTest" 的資料庫物件 Schema 確認
   這部份的設計, 決定了 database schema 的規劃, 儲存的結構都在這裡確認   
   
2. 需要被定義的 Identity / Transaction Context 以及運作方式的確認
   這邊的設計主要是結合了 .NET Dependency Injection 機制的對應, 我在 Scope 內注入能描述當下 identity / transaction 的資訊, 所有程式碼都能直接取得; 跨 scope 就要明確傳遞, 這可以解決 async / offline 執行等等邊界問題   
   其實這是個很大的課題, 有興趣的可以看我多年前在 .NET Conf 分享的演講 ( ... )
   
3. 查詢 "真實商業效果" 的 query
   我先定義了哪些是我認定的 "真實商業效果", 某種程度也是拿來當作驗證結果用的設計
   實際系統應該是各種統計報表的功能, 在這邊我只簡單定義了一組 admin api / admin cli 來簡化, 這 cli 可以查詢業績統計, 會按照 (1) 的設計排除 test mode 的資訊

我把這些內容整理一下, 列在下方:

--

**1. 哪些資料需要保存 `.IsTest`，以及用途如何決定**

目前有四種物件保存 `.IsTest`：

|物件|用途如何決定|儲存位置|
|---|---|---|
|`Member`|建立時依會員名稱白名單決定|共用 `members`|
|`MemberAccessTokenRecord`|簽發時繼承 Member 的用途|共用 `member_tokens`|
|`CheckoutTransactionRecord`|建立時依 Member 與 PaymentId 決定|正式／測試各自的 active、archived collections|
|`Order`|繼承建立它的 Checkout 用途|`orders`／`test_orders`|

這裡最適合呈現的 Schema 是：

```
public class Member
{
    public int Id { get; set; }
    public bool IsTest { get; init; }
    // ...
}

public class MemberAccessTokenRecord
{
    public string Token { get; set; } = string.Empty;
    public int MemberId { get; set; }
    public bool IsTest { get; init; }
    // ...
}

public class CheckoutTransactionRecord
{
    public int TransactionId { get; set; }
    public int MemberId { get; set; }

    public bool IsTest { get; init; }
    public int PaymentId { get; init; }
    // ...
}

public class Order
{
    public int Id { get; private set; }
    public bool IsTest { get; init; }

    public int? CheckoutTransactionId { get; init; }
    // ...
}
```

來源：Member.cs (src/AndrewDemo.NetConf2023.Core/Member.cs:5)、Token／Checkout Schema (src/AndrewDemo.NetConf2023.Core/ShopDatabaseContext.cs:275)、Order.cs (src/AndrewDemo.NetConf2023.Core/Order.cs:14)。



這段值得說明的重點是：**身分用途與交易用途分別保存，因此正式會員也能建立測試交易。** Cart、Product、SKU、Inventory 則維持共用，沒有增加 `.IsTest`。

用途的決定與承接，可以再摘錄這兩段：

```
// Checkout 建立時，決定並保存這筆交易的用途。
var transaction = new CheckoutTransactionRecord
{
    // ...
    PaymentId = command.PaymentId,
    IsTest = member.IsTest || _allowlist.IsTestPayment(command.PaymentId),
    // ...
};

// Order 承接 Checkout 已經保存的用途。
var order = new Order(_transactions.NextOrderId())
{
    Buyer = consumer,
    IsTest = transaction.IsTest,
    CheckoutTransactionId = transaction.TransactionId,
    // ...
};
```


來源：Checkout 建立 (src/AndrewDemo.NetConf2023.Core/Checkouts/CheckoutService.cs:102)、Order 建立 (src/AndrewDemo.NetConf2023.Core/Checkouts/CheckoutService.cs:164)。



目前 PaymentId 是用來查白名單的識別值，沒有獨立的 `Payment.IsTest` 物件。交易建立後，後續流程沿用保存的用途，不重新依白名單判定。

Phase 3 將這個用途直接對應到 collection：

```
public static string Orders(bool isTest) =>
    isTest ? "test_orders" : "orders";

public static string Checkouts(bool isTest, bool archived = false) =>
    (isTest ? "test_" : "")
    + (archived
        ? "archived_checkout_transactions"
        : "checkout_transactions");
```

來源：TransactionCollections.cs (src/AndrewDemo.NetConf2023.Core/Storage/TransactionCollections.cs:11)。

`init` 表達建立後不可任意賦值的意圖；持久化層另外檢查用途與 collection、Checkout／Order 關聯的一致性，不能只靠 `init` 保證資料隔離。

---

**2. Identity／Transaction Context 的合約，以及跨執行邊界的運作**

這組是最值得完整放在文章裡的 interface：

```
public interface IIdentityContext
{
    IdentitySnapshot Current { get; }
}

public interface ITransactionContext
{
    TransactionSnapshot? Current { get; }
}
```

兩份快照分別保存：

```
public sealed class IdentitySnapshot
{
    public IdentityKind Kind { get; }
    public int? MemberId { get; }
    public bool IsTest { get; }

    // ...建構式與 factory
}

public sealed class TransactionSnapshot
{
    public TransactionKind Kind { get; }
    public int Id { get; }
    public bool IsTest { get; }

    // ...建構式
}
```

其中 `IdentityKind` 為 `Anonymous`、`Member`、`System`；`TransactionKind` 為 `Checkout`、`Order`。

來源：IdentityContextContracts.cs (src/AndrewDemo.NetConf2023.Abstract/Contexts/IdentityContextContracts.cs:3)、TransactionContextContracts.cs (src/AndrewDemo.NetConf2023.Abstract/Contexts/TransactionContextContracts.cs:3)。

這裡可以直接接上這段說明：

> Identity Context 回答「現在是誰在執行」，Transaction Context 回答「現在處理的是哪一筆交易」。兩者的用途不必相同：正式會員可以建立測試交易，正式的 System 身分也可以處理測試訂單。是否扣庫存等交易效果，必須依交易用途判斷，不能只看執行者是不是測試帳號。

在實作上，兩種 Context 分開註冊為 scoped service，同一個 scope 內透過介面與具體類別取得的是同一份物件：

```
services.AddScoped<IdentityContext>();
services.AddScoped<IIdentityContext>(
    sp => sp.GetRequiredService<IdentityContext>());

services.AddScoped<TransactionContext>();
services.AddScoped<ITransactionContext>(
    sp => sp.GetRequiredService<TransactionContext>());
```

來源：ExecutionServices.cs (src/AndrewDemo.NetConf2023.Core/Contexts/ExecutionServices.cs:15)。

HTTP 入口驗證 Token 後建立 Identity；涉及既有 Checkout 時，另外檢查買方，再從保存的 Checkout 載入 Transaction Context。**Context 並不是跨 HTTP request 自動延續，而是在新的執行邊界重新建立。**

訂單事件的這段最能說明這個設計：

```
using var scope = scopeFactory.CreateScope();
var services = scope.ServiceProvider;

// ...初始化操作結果與錯誤處理

services.GetRequiredService<IdentityContext>()
    .Initialize(IdentitySnapshot.System);

services.GetRequiredService<OrderContextLoader>()
    .Bind(orderId);

// ...執行事件處理器
```

來源：DefaultOrderEventDispatcher.cs (src/AndrewDemo.NetConf2023.Core/Orders/DefaultOrderEventDispatcher.cs:31)。

`OrderContextLoader.Bind(orderId)` 會讀取已保存的 Order，再用它的 `IsTest` 建立交易快照。因此，即使原來的 HTTP request 已經結束，新的 System scope 仍然知道這是一筆測試訂單。載入實作 (src/AndrewDemo.NetConf2023.Core/Orders/OrderContextLoader.cs:14)

後續政策分成兩種：

- **商品改價**：檢查 Identity，測試身分明確拒絕。
- **Checkout 扣庫存、Order 衍生效果**：檢查 Transaction，測試交易略過受保護寫入；缺少正確的交易 Context 則視為錯誤。

對應程式集中在 ProtectedWriteExecutor.cs (src/AndrewDemo.NetConf2023.Core/Effects/ProtectedWriteExecutor.cs:17)。

---

**3. 查詢實際保存的結果，確認商業效果受到隔離**

這部分建議放「訂單統計」與「庫存讀回」兩組，分別證明測試訂單沒有混入正式統計，以及測試交易沒有扣掉共用庫存。

訂單查核的實際入口是 `AdminQueryService.GetOrders()`：

```
public AdminOrderResult GetOrders(AdminQueryOptions options) => Read(() =>
{
    var queriedAt = timeProvider.GetUtcNow().UtcDateTime;

    var candidates = new TransactionStore(database.Database)
        .ReadOrders(options.Purpose)
        .Select(OrderRow)
        .Where(x => MatchesPurpose(x.IsTest, options)
                 && MatchesMember(x.MemberId, options))
        .ToArray();

    var excluded = candidates.Count(
        x => HasTimeFilter(options) && x.CreatedAt == null);

    var rows = candidates
        .Where(x => MatchesTime(x.CreatedAt, options))
        .OrderByDescending(x => x.Id)
        .ToArray();

    var unknown = rows.Count(x => x.TotalPrice == null);

    decimal known;
    try { known = rows.Sum(x => x.TotalPrice ?? 0m); }
    catch (OverflowException)
    {
        throw new AdminDataInvalidException("訂單金額超過可表示範圍。");
    }

    return new AdminOrderResult(
        Page(rows, options, queriedAt, excluded),
        unknown == 0 ? known : null,
        known,
        unknown);
});
```

來源：AdminQueryService.cs (src/AndrewDemo.NetConf2023.Core/AdminQueries/AdminQueryService.cs:10)。

這段查詢有三個要求：

- 預設 `Purpose = "normal"`；先選擇用途對應的 collection，再核對 **Order 自己的 `IsTest`**，不依 Buyer 的用途分類。
- 先算完整符合條件的統計，再分頁，總額不受畫面顯示幾筆影響。
- 歷史訂單若缺少金額，回傳未知筆數，完整總額為 `null`；不把未知金額當作零元訂單。

管理 CLI 對應的查詢如下，假設已完成 publish 並設定 Admin 認證：

```
# 正式訂單統計
.local/admin-cli/publish/shop-admin stats --source order --type normal

# 測試訂單統計
.local/admin-cli/publish/shop-admin stats --source order --type test

# 合併查核正式與測試訂單
.local/admin-cli/publish/shop-admin stats --source order --type all
```

來源：AdminCLI 操作說明 (docs/tip/admin-cli.md:44)。這裡統計的是**保存的訂單金額**；專案沒有接真實金流，不能將它描述成已收款金額。

庫存則有直接讀回資料庫的驗收程式碼。案例預先建立庫存 10 件、購買 2 件，完成 Checkout 後檢查：

```
Assert.Equal(CheckoutCompleteStatus.Succeeded, result.Status);

Assert.Equal(
    expectedTest ? 10 : 8,
    Context.InventoryRecords.FindById(sku).AvailableQuantity);
```

同一案例涵蓋四種組合：

```
[InlineData(false, 0, false)]
[InlineData(false, 990001, true)]
[InlineData(true, 0, true)]
[InlineData(true, 990001, true)]
```

參數依序為 `memberTest`、`payment`、`expectedTest`。只有「正式會員＋一般付款」會把庫存從 10 扣到 8，其餘組合仍為 10。

來源：TransactionStorageTests.cs (tests/AndrewDemo.NetConf2023.Core.Tests/TransactionStorageTests.cs:18)。

商品改價也有相同的讀回檢查：測試身分要求將價格從 100 改成 80，操作必須拒絕，保存價格仍為 100：

```
Assert.Throws<TestIdentityForbiddenException>(
    () => maintenance.UpdatePrice(id, 80, _ => { }));

Assert.Empty(effects.Skipped);
Assert.Equal(100, Context.Products.FindById(id).Price);
```

來源：商品改價驗收 (tests/AndrewDemo.NetConf2023.Core.Tests/TransactionStorageTests.cs:50)。

這兩段可以支撐你的論述：**驗收會讀回實際庫存、商品價格與訂單統計，確認隔離結果；log 則用來交代哪些操作被略過。**



## 5, 實際驗證成果 (真人)

我就不一步一步從頭開始執行了, 好在我有先準備好 AC list, 先跑一次當作基底, 跑完一輪 AC 後, 資料庫的狀態是這個樣子 (我只列訂單, normal / test 都列):



目前共 **13 筆訂單**，PaymentId 由各訂單關聯的已封存 Checkout 取得。

| 訂單 ID | 模式        | Member ID | Member 名稱          | PaymentId | 金額  |
| ----- | --------- | --------- | ------------------ | --------- | --- |
| 13    | 測試 test   | 1         | test               | 990001    | 18  |
| 12    | 測試 test   | 1         | test               | 0         | 18  |
| 11    | 測試 test   | 4         | ac-normal-20261021 | 990001    | 18  |
| 10    | 正式 normal | 4         | ac-normal-20261021 | 0         | 18  |
| 9     | 正式 normal | 4         | ac-normal-20261021 | 0         | 36  |
| 8     | 測試 test   | 1         | test               | 0         | 18  |
| 7     | 正式 normal | 4         | ac-normal-20261021 | 0         | 18  |
| 6     | 正式 normal | 4         | ac-normal-20261021 | 0         | 54  |
| 5     | 測試 test   | 1         | test               | 0         | 36  |
| 4     | 測試 test   | 1         | test               | 990001    | 18  |
| 3     | 測試 test   | 1         | test               | 0         | 18  |
| 2     | 測試 test   | 4         | ac-normal-20261021 | 990001    | 18  |
| 1     | 正式 normal | 4         | ac-normal-20261021 | 0         | 18  |

- **正式業績：5 筆，144 元**
- 測試訂單：8 筆，162 元
- 全部合計：13 筆，306 元

> 會員 `test` 或 PaymentId `990001` 任一條件成立，交易即為測試模式。


接下來, 我用我自己的帳號 ( andrew ) 登入, 分別用正式的信用卡號 ( 123456 ), 跟測試用的信用卡號 ( 990001 ) 各買三罐啤酒:



用正式的信用卡號 123456 結帳:

![alt text](/images/2026-10-26-test-in-production-practice/image-1.png)

結帳結果

![alt text](/images/2026-10-26-test-in-production-practice/image-2.png)

![alt text](/images/2026-10-26-test-in-production-practice/image-3.png)

再用測試的信用卡號 990001 結帳:

![alt text](/images/2026-10-26-test-in-production-practice/image-4.png)

![alt text](/images/2026-10-26-test-in-production-practice/image-5.png)

再次查詢業績統計, 這兩筆訂單都有正確的被識別, 也有正確的統計加總:

已重新查詢，目前 **15 筆訂單**；新增的是 **#14 正式訂單**與 **#15 測試訂單**。

|訂單 ID|模式|Member ID|Member 名稱|PaymentId|金額|
|---|---|---|---|---|---|
|**15**|測試 test|2|andrew|990001|169|
|**14**|正式 normal|2|andrew|123456|169|
|13|測試 test|1|test|990001|18|
|12|測試 test|1|test|0|18|
|11|測試 test|4|ac-normal-20261021|990001|18|
|10|正式 normal|4|ac-normal-20261021|0|18|
|9|正式 normal|4|ac-normal-20261021|0|36|
|8|測試 test|1|test|0|18|
|7|正式 normal|4|ac-normal-20261021|0|18|
|6|正式 normal|4|ac-normal-20261021|0|54|
|5|測試 test|1|test|0|36|
|4|測試 test|1|test|990001|18|
|3|測試 test|1|test|0|18|
|2|測試 test|4|ac-normal-20261021|990001|18|
|1|正式 normal|4|ac-normal-20261021|0|18|

- **正式業績：6 筆，313 元**
- 測試訂單：9 筆，331 元
- 全部合計：15 筆，644 元

我就不跑完所有的情境了, 只是簡單示範兩個主要路徑, 證明整個 prototype 有按照預期的要求設計｡

另外, 值得一提的是這個 shop-admin CLI 的設計, 我覺得是個很精巧的做法, 如果你有打算開發自己的 CLI 都值得看看...

我在先前演講, 帶過這頁簡報 ( GUI vs CLI ), 提到我很討厭做管理後台, 因此我選擇做好 API + CLI, 替代自己刻 Admin UI:

// slide

經過這幾個月, 做法更細緻了, 我的情境是: CLI 盡可能的把我需要的基礎操作功能都做出來, 用 --help 列出使用提示, 讓使用者知道有哪些參數能用 (當然 Agent 也能看), 例如:

// --help

然而, 有些組合的情境, 需要額外指引 agent 怎麼使用, 例如搭配特定流程, 哪些情況下該用哪些參數組合, 或是該輸出什麼格式給業務人員, 他們的習慣格式是什麼等等..., 這些需求每次都要下 prompt 很麻煩, 自然就會收成 SKILL ...

不過, CLI 一旦有改版, 如果變更也會影響輸出格式, 那 SKILL 就必須跟著改版, 但是這兩種資訊的安裝跟更新途徑不大一樣, 很難隨時都維持 100% 同步.. 

我想說, CLI 的 usage 就沒有這種問題啊, 難道 SKILL 不能比照辦理? 於是我先前在 facebook 發了一篇文, 說明這構想: (link)

這邊我也這樣做了, 我追加了一個參數: --skill (topic) , 印出的內容就會是預先準備好的 SKILL.md, 基本上對 agent 而言大同小異, 都是需要時才會進入 context window, 但是我可以把 SKILL.md 在編譯時期就放進 assembly 裡面啊, 這麼一來, CLI / SKILL 就從根本上達成同步了, 你只要安裝對的 CLI, 就會拿到對應的 SKILL...

效果出奇的好, 基本上我不用靠任何 SKILL 的輔助, agent 就能很 "熟練" 的操作 CLI 了, 我會說 "熟練" 而不是說 "正確", 是因為 agent 不只知道該怎麼操作, 而是他操作的方式看起來就像個老手, 一次就用最精簡的參數組合來執行命令, 而不是像個新手一般, 先 --help, 然後測試, 修正, 多次之後才會下對指令拿到結果

這就是 SKILL 存在的目的, 而我只是把部署的方式簡化, 從源頭直接消除不同步的困擾而已

![alt text](/images/2026-10-26-test-in-production-practice/image.png)

> 一次到位就下對指令