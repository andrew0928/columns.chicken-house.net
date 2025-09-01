其實，類似的主題 ([微服務基礎建設 - Service Discovery](/2017/12/31/microservice9-servicediscovery/)) 去年底就已經寫過一篇了。不過這次有幸投稿 DevOpsDays Taipei 2018 有幸榮獲大會青睞，能上台講這個主題，加上目前工作需要，我們自己也開始有計畫逐步導入 service discovery。因此關注 Consul 也有一陣子，對於 Service Discovery 的看法又有些進化了。於是決定趁著準備這次演講，除了 Slides 之外，也來個文字版的文章吧! 比起演講，文章的形式還是比較有組織，比較能深入一些。

這次我換個角度，介紹 Service Discovery 的基本觀念，以及應用的方式，最後帶到如何逐步演進到 sidecar / service mesh。我分三個部分進行:

1. Basic: Service Discovery for Developers
1. Advanced: Case Study
1. Next: Service Mesh

<!--more-->


所有微服務相關的文章，可以直接參考下列的導讀。

{% include series-2016-microservice.md %}


# 本文開始

這次畢竟是為了大活動 DevOpsDays Taipei 2018 準備的，當然不能隨便講個主題就蒙混過去。DevOps 講究的是 Develop 跟 Operation 兩種流程的整合與良性的回饋與改善循環。我的專長還是在 Develop 的領域啊，要在這種大場子吹噓我不擅長的 Operation 領域不是我的風格啊，因此我在當初投稿時就已經定調，這個 session 的主軸會擺在:

> 讓 developer 更了解 operation 如何看待與管理大量的服務 (service discovery)，更重要的是 developer 充分掌握相關知識之後，更高度的整合能力可以創造出過去難以開發出來的功能。

這種敘述方式，對我來說也是個新的挑戰。傳統的企業往往都把開發與運維團隊分成兩個部門，過去企業 IT 的發展，運維技術往往也都強調對開發人員是透明的，不用改任何一行 code 就可以 blah blah ..., 但是這就是違背了 DevOps 的精神啊，在 Cloud Native 的時代，很多創新的功能必須讓這兩個領域的技術更緊密整合才能辦的到。這是我想在這 40 min 的 session 表達的理念。

因此我會囉嗦一些，說明技術的演進，為何這樣設計，以及應用的範式 (patterns) 是我的重點，至於實際的 coding 與具體的 tech stack 選用，只是個參考範例而已。這篇文章我用我熟悉的 docker, .net framework, consul 當作案例。不過，這篇文章講的內容，你可以套用在各種主流的開發技術或是框架上面。

架構師存在的目的，是替團隊做出正確的技術選型，協助兩大團隊 (develop + operation) 正確的規畫與運用技術，解決 Dev + Ops 的整合問題。對技術或是服務的掌握，要清楚背後的運作原理。架構師必須做好最壞的打算，在有必要時，你得要有辦法帶領團隊自己寫一個；不過通常你不必這麼做 (通常你不是第一個碰到問題的人，你的需求沒有這麼特別)。了解原理有助於你做出更正確的選擇，更精準地講，你會做出更正確的應用與整合方式。

然而，帶領團隊邁向微服務架構碰到的第一個問題，就是 service discovery。常常有人問我，Service Discovery 算是 Infra (Ops) or Service (Dev) 的職責? 我覺得都不是!! 它是融合兩者的中間層服務，兩邊的團隊都需要了解他。


# BASIC: Service Discovery for Developers

微服務架構的第一個難題，就是你該如何管理好為數眾多的服務? 在這架構下，團隊會面臨越來越多樣的服務 (大型應用程式拆解之後的結果)，隨著規模的擴大，每個服務也會由越來越多的小型 instances 組成 (如 container)。

![](/images/2018-10-10-microservice11-devopsdays-servicediscovery/2018-10-14-15-26-49.png)

服務的種類及數量都不斷的在增加，服務的異動也越來越頻繁 (也許幾秒鐘就會有變化)。過去簡單的管理方式 (或是不管理? XD) 都會變成系統發展的瓶頸。回想一下，你的團隊目前都怎麼管理內外部的服務?

1. DNS + ELB  
這是最常見的模式了，替每個服務指派專屬的 URL, 搭配 Load Balancer 來把 request 引導到後端不固定個數的 service instance. 對於服務的提供者或是開發團隊來說，這樣算是足夠了。

1. Config  
對於使用服務的團隊來說，我也許需要同事調用多個外部服務。即使這些服務都已經有 DNS + ELB 的設置了，但是我仍然得管理這些服務的清單與 URL 啊! 大部分的團隊碰到這種需求，就會把這些資訊放到 application configuration 內管理。這樣在某種程度上也算解決了基本需求了。

不過，我反問幾個問題，各位可以思考看看這是否是你的團隊面臨的瓶頸?

1. 以呼叫端來說，我如何有系統地確認每個服務在當下都是可用的? config 是靜態的，一旦服務失敗 (可能有各種難以預料的狀況)，我的系統是否會因為這樣就停止回應 (通常等待對方回應都會有 30 sec timeout)? 或是直接丟出 exception 導致後面的功能都無法操作? 是否有更建全的服務狀態資料庫能取代 config, 讓系統能更精準的面對這狀況?
1. 如何更精準的調用外部服務? 應用的規模更大時，單一的 URL 可能無法解決所有的需求。舉例來說，同樣的通知服務，也許有分不同服務層級，也有分不同的區域，而這些服務如果都只有同樣的 URL，選擇的能力就只能依靠 operation team 搭配 DNS 來控制了。如果你想要有更進階的選擇，也許就要規劃專屬的 URL ... 但是這樣複雜度就掉到 application 端... 
1. 即使主流的 cloud provider 提供的 LB 都已經做得不錯了，可以及時反映內部的 instance 動態更新。不過對於內部團隊自行開發的多種服務，要調用還需要繞道經過 Load Balancer, 有點多此一舉，同時 LB 也可能成為單點失敗的潛在風險，也可能變成效能的瓶頸。也有可能透過 LB 過多後端的資訊會被遮蔽，內部期望預設開放反而會是這種架構的阻礙...

最後，補上這篇文章，這些趨勢論點還是給大師級的來說明比較到位。這是今年 (2018/09) 舉辦的 Kong Summit, Day 1 Keynotes 裡面的一段，提到傳統的 API management is dead.. (參考報導: [3 Reasons Why API Management Is Dead](https://thenewstack.io/3-reasons-why-api-management-is-dead/))。有研究過微服務基礎架構的人，一定對 Kong 這套 Open Source 的 API Gateway 不陌生，算是 APIGW 的主流服務了，這個觀點由 Kong 自己來說明格外的有說服力。

其實，以上這些議題，都是 Service Discovery 要解決的問題。從 client 端來看，首先要解放的是透過 config 來管理 service definition 的問題，將這部分透過專屬的 service registry + 完善的 health check。這些基礎做好之後，才有可能進一步演進到 service mesh 等等更進階的架構。

----

接下來的部分，容許我偷懶一下。為了顧及與會現場的朋友們，不見得每一位都很清楚這些服務架構，所以 session 的前 10 分鐘，我花了一點篇幅介紹一下基本的 service discovery 的基礎原理跟應用方式，這些細節我都在上一篇 ([微服務基礎建設 - Service Discovery](/2017/12/31/microservice9-servicediscovery/)) 交代過了，這邊我就不再重複，有興趣的朋友們可以自行參考文章或是大會錄影。



# Advanced Scenario

這段開始，才是我想傳達的 service discovery 應用情境啊! 這些是很實際的應用情境，但是偏偏單靠 cloud infra 無法直接搞定，單靠 developer 要解決也是大工程，唯一的解決方式就是尋找能高度整合 infra 的方案給開發人員好好運用。先來看看這些令開發團隊頭痛的案例:




## 案例: 提供不同 SLA 給不同層級的客戶

雲端服務開始盛行之後，就很常看見服務商端出這幾種套餐:
1. 免費: 讓你用基本的功能, 基本的 SLA (例如 99.9%)
1. 付費: 用所有的功能, 較佳的 SLA (例如 99.95%)
1. 企業方案: 所有的功能, 並且保證獨立運算資源, 不與其他客戶共用

有趣的是，這些 "差異"，都不是在功能身上啊! 除了 (免費) 跟 (付費) 之間也許有些功能差異之外，其他的差異都存在於可靠度或是效能 (SLA)，甚至是部署上面 (VM/DB) 的差別。那麼，這些功能應該怎麼被實做出來?

這就是我一開始說的，團隊 DevOps 之間整合度不足，就搞不定這類問題的。在 application level 才能知道這些細節 (例如: 客戶註冊時填的資料或是購買的方案，存在資料庫內)，這些屬於 Dev 掌控範圍。但是，要交付的不同層級的服務，則是 Ops 的掌控範圍啊!

這時來看看 Service Discovery 的 Service Definition 資料庫 (registry) 能如何運用吧! 先來看看 Slack 提供的服務方案:

![](/images/2018-10-10-microservice11-devopsdays-servicediscovery/2018-11-05-02-22-51.png)

不同方案，有不同的服務內容。File storage 的控制是小菜一碟，按照規格開發即可。Support 則是人工的服務，按照 SOP 即可。最難理解怎麼辦到的，則是 SLA 99.99% 保證這件事。我大膽的假設一下，這件事背後可能有幾種做法:

1. 完全不管 SLA，Slack 團隊就是盡力顧好 SLA 就對了。唯一的差別在於，一旦那天 SLA 低於 99.99%, 只對 PLUS 會員賠償就好
1. 替 PLUS 會員準備獨立的設備。

SLA 是要用錢燒出來的，最基本的就是每個資源都至少要有兩份以上作互相備援 (一般是三份)。SLA 要從最底層開始算，如果你用的 cloud service 底層只提供 99.95% 的 SLA, 你得要多花些心思才能把它提高到 99.99%, 這還不包括你自己寫的 code 掛掉的問題。因此提高 SLA 別無他法，大概就這幾種手段:

1. 從 code 本身強化 (不過你 code 都寫好了，除非要耗用比較多的資源，不然沒道理不下放給其他會員吧)
1. 採用 SLA 較高的基礎建設 (不論是 Azure / AWS, 其實底層也都提供不同可靠度不同價格的選項)
1. 花較多資源來進行備援，從架構面提高整體 SLA (相對的成本也會變高)

不論你用 (2) 或是 (3), 現在問題來了。如果後端某個關鍵服務共有 100 個 instance, 功能完全都一樣，旦是我希望其中 40 nodes 提供給 FREE / STD 等級的會員使用，而 60 nodes 要保留給 PLUS 會員，用較多的 nodes 我期望提供較高的 SLA ，這時我應該怎麼 "開發" 這樣的系統?

如果你用的是 DNS + LB, 不是做不到，只是這樣可能會搞死開發人員跟運維人員了。要建立兩個 domain name 嗎? 還是兩組 LB ? 會員屬於哪種方案，通常要登入後查詢資料庫，在 runtime 才能得知這個 request 該走哪一群...，靠一般的 IT 手段難以解決這類問題。

BUT! 如果你採用的，是前面提到的，Client Side Discovery Patterns, 那問題就簡單多了。Service Discovery 在一開始建立 service registry database 時, 如果預先替這 100 個 nodes 標好 tags, 是先標記那些是 PLUS_ONLY 的 nodes... Client Side 在查詢時就能根據目前 request context, 來決定要不要過濾不是和它的 nodes ..