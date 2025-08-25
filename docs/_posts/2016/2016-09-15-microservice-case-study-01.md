---
layout: post
title: "微服務架構 #1, WHY Microservices?"
categories:
- "系列文章: .NET + Windows Container, 微服務架構設計"
- "系列文章: 架構師觀點"
tags: ["Microservices", "Monolithic", "Windows Container", "Container"]
published: true
comments: true
logo: /images/2016-09-15-microservice-case-study-01/stateless-authentication-for-microservices-12-6381.jpg
---

八月底，接受了 Microsoft 的邀請，參加了 Community Open Camp 研討會，講了這場 "微服務架構 導入經驗分享 - .NET + Windows Container"。
其實這個主題涵蓋範圍還蠻大的，不過我一直認為，container 技術單獨介紹的話，那他就是個技術而已，若從他存在的目的來介紹，那他就是能解決
問題的好東西。因此我特地訂了這個主題: container + microservices.

<!--more-->

一切要從 SOA (service oriented architecture) 開始說起。2000+ internet 紅了之後，很多大廠就開始主推 SOA 架構。不過在當時是叫好不叫座，
主要是因為開發的技術跟佈署的技術還跟不上，導致這種架構是只有大型團隊才玩得起。現在的 container, 大幅改善了佈署的門檻，也大幅降低了小規模
佈署的成本 (以前最小單位是 server, 後來進步到 vm, 現在則是縮小到 container), container + microservices 突然之間就變成顯學。

佈署方便且快速的特性，也影響到開發團隊的流程，逐漸的促成了 devops .. 這些都是 container 會快速普及的原因。其實我很想整個交代一遍，不過
這次 session 時間只有 40 分鐘，相當有限... 最後當然是略過了很多細節，我決定把重點擺在 microservices, 而實際的案例則用 container 來展示。
我用的是 asp.net (mvc) project, 因此也特地照顧了較少接觸 open source 資源的 windows developer 族群，demo 採用 windows container。

我準備的內容，包含 demo, 若是要講個 4hr 也是夠講的... XD，裡面其實太多細節跟經驗值得分享的。既然當天的場子講不完，我就整理一下用文字的
方式在這邊分享吧。這 session 主要的對象，我定位在已是有經驗的 .net developer, 但是不熟悉 microservice / container 技術的人。這樣的族群
在台灣企業其實還蠻多的... 我會分成這幾個章節，預計會分成三篇文章來說明:

1. 微服務架構
2. 容器化的佈署方式 (demo: windows container)
3. 實際案例說明 (大型人資系統, ASP.NET WebForm application)

在研討會，我的 session 提供的相關資訊，我就先擺在這裡給大家參考了。session 的內容，跟我這幾篇打算補充的內容，定位有些差別。
session 只有 40 min, 我必須雇到前後資訊的串接，也要顧到在場聽眾能否順著邏輯了解我要表達的重點，很多資訊是點到為止而已。但是寫在這裡
的文章就沒這問題，我會定位在你已經是個有經驗的 developer (特別是 .net developer), 但是想切入 microservice & container 技術的族群。

相關資源我列在:

相關資源:

1. [slides ppt](http://www.slideshare.net/chickenwu/community-open-camp)
2. [session video @ channel 9](https://channel9.msdn.com/Events/Community-Open-Camp/Community-Open-Camp-2016/ComOpenCamp018)
3. [source code, files, demo scripts](https://github.com/andrew0928/CommunityOpenCampDemo)


{% include series-2016-microservice.md %}


## 微服務架構(Microservices) v.s. 單體式架構(Monolithic)

軟體就是不斷的 reuse code, 不斷的堆疊, 累積成能解決問題的 application. 累積這些 code 的方法很多，過去的軟體開發方式，最常用的就是
library / component 的方式，把 code / binary 組裝成一個大型的 application。先來看張圖:

![單體式架構(monolithic) vs 微服務(microservices)](/images/2016-09-15-microservice-case-study-01/microservice-slides-06.PNG)

> 用這張圖實在太嚴肅了 (這是 Microsoft 那邊找來的 slides).. 我在找資料時找到一篇 [testing microservices](https://lostechies.com/andrewsiemer/2016/01/11/testing-microservices/) 的文章..
> 結果看到這張圖我就笑了 XDDD，有夠靠背的... 貼來給大家欣賞一下 :D
> ![也是 Microservices vs Monolithic](/images/2016-09-15-microservice-case-study-01/stateless-authentication-for-microservices-12-6381.jpg)


這兩種架構，應該從巨觀來看。說穿了很簡單，就是由最基礎的 code 堆疊到最終的 application，採用了不同 reuse 的做法而已。單體式架構
採用相同的 code / language / framework / platform 為基礎，借助開發工具或編譯器，在 develop time 就將這些元件，用函式庫或是元件
的方式組合起來。最終透過作業系統執行時，他就是個 process, 只是規模可能會很大。

微服務的架構，則採取了不同的策略。他控制單一 application 的規模跟複雜度，把過大的 application 切割成幾個獨立的 services，再用
定義好的介面 (API or protocol) 把這些獨立的 service 在 runtime 串接起來使用。由於服務之間只能透過 API 溝通，因此是否用同樣的
 platform / language or framework 開發並不重要。最終透過作業系統執行時，會被視為好幾個獨立的 process 執行, 個別服務的規模(複雜度)
 不大，但是一個完整的 application 可能會包含好幾個服務。


## Develop Team: Reuse of Codes 

從這些根本的差異，其實就看的出來它們的特性，跟適用的情境了。從軟體開發的角度來看，我把 code reuse 的方式分為幾種:

1. **source code**  
使用的時候，必須拿到要被重複利用的 source code。
code snippet, design patterns, scripts 等等都屬於這種。
reuse 的層級只在 compile time, 且限定為同一種語言 (廢話), 需要 develop team 重新編譯發行才能使用。
若 source code 有異動，application 通常得經過重新編譯及之後的所有程序 (如測試、發行等等) 才能升級。

2. **binary code**  
常見於元件(component)、套件(package)、插件(plugins)或是涵式庫(library / class library)。編譯過後的 library 通常有
一定的規範，例如 java jar, 或是 .net 的 assembly (.dll) 等等。reuse 的層級在 develop time, 不過 binary code
通常有較完整的規範，若不影響對外的介面 (如 c external signature, 或是 .net public class 等等)，可以直接替換 binary
而不需要經過重新編譯等過程。

3. **Service**  
更高層級的 reuse. 你使用的已經是個完整的服務了，只是你必須透過事先定義的 API or protocol 來使用他。最典型的例子就是 database.
你是架設好之後，開個 database, 就可以連線使用了。以 Microsoft SQL server 為例，他有他專屬的 protocol (TCP port 1433), 
你甚至必須使用對應的 library (data provider) 才能使用。若服務的
抽象畫及介面定義的夠好，你甚至可以抽換不同的服務，例如 wordpress 可以用 mysql, 也可以換成 sqlite 這樣的的案例就是。
升級 service 時，你的 application 不需要異動，甚至可以不用停機就能完成。reuse 的層級是 runtime.

從這角度 (開發者) 來看，單體式APP的開發，主要就是把APP內切割成多個模組或子系統，用 (1) or (2) 的方式實作出來的開發方式。而微服務架構，
則是以 (3) 的方式來解構整個 application, 之後每個 service 的開發，才會考慮到 (1) or (2) 開發方式的架構。 


## Operating Team: Application Maintainess

若從維運的角度來看，這兩種架構的差異也很明顯。對於維運團隊來看，上述的 (1) source code reuse, (2) binary code reuse 幾乎是
無感的，反正最終 develop team 打包好的 application 是什麼就是什麼了。在 OP 的觀點來看，單體式架構的 application 能做的管理跟監控很有限，掛掉了
就只能整個 application restart, 效能不足就只能整個 application scale out, 做 load balance, 或是整個 applicatio 備援。當 application
規模過大，往往也很難充分運用 server 的所有運算資源，間接讓執行的成本無法下降。

相較之下，微服務架構下給維運團隊的彈性就大很多。維運團對開始有機會個別監控每個獨立的 services, 可以個別升級，備分，維護等。碰到問題也能個別 restart,
甚至也能在修復時關閉部分功能，分區維修，將使用者的影響降到最低。效能不足時，也能視個別服務的 loading 不同，只針對特定的 service 做 scale out.
維運團隊對 application 的狀況掌握的精確程度，可以遠高於單體式的 application.

不過，相對於 application 的佈署，微服務架構也相對的複雜。最傳統的 application, 你可能只需要搞定 web + database, 改成微服務架構你要裝的
東西就多了。這是另一個門檻，也是我為何一定要在這個主題一起提到 container 的原因。因為這兩個技術真的是相輔相成，互相互補的技術啊! container 技術
正好填補了這個需求，大幅簡化了微服務架構的 application deployment 作業。這部分下一段再來說明 (未完待續...)
