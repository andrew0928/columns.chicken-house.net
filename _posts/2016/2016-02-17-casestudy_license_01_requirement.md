---
layout: post
title: "[設計案例] \"授權碼\" 如何實作? #1, 需求與問題"
categories:
- "設計案例: “授權碼” 如何實作?"
tags: ["專欄","技術隨筆","物件導向"]
published: true
comments: true
permalink: "/2016/02/17/casestudy_license_01_requirement/"
redirect_from:
wordpress_postid: 833
---

![](/wp-content/uploads/2016/02/img_56c431d4ac75a-e1455698460913.png)  
The Architect, The Source (電影: The Matrix 3)  

好久沒寫 [設計案例] 這系列的文章了。其實我一直注意到台灣的部落格 & 社群分享，講 "How To" 的遠多過講 "Why" ，過於注重 coding 的技巧，卻忽略了問題的思考。能挑選正確的技術與架構來解決 business 上碰到的問題，這才是 software / system architect 的核心能力啊... 這次我碰到適合的案例，就來補給篇文章吧，我想從我如何思考這問題的 solution, 到如何實作出解決方案的過程，從頭到尾交待一次，讓有興趣在軟體業走進 system architect 這角色的讀者們，有個可以參考的案例!

<!--more-->

這次的主題我想探討 "網站授權" 及 "API KEY" 這東西的實作。授權機制需要單靠一段字串或是號碼，就能讓軟體能判斷客戶或是使用者被授權使用那些功能? 這些機制不影響功能，但是會影響你的服務夠不夠安全。往往大家的注意焦點都會在 "你用了什麼加密技術? 夠不夠安全? 會不會被破解?" 這些技術規格的問題上，但是卻很少看到這類問題的架構及實作。我實際上碰到的狀況是，往往很多工程師對於 security 的領域知識不夠了解，因此在架構上沒處理好，但是因為正常狀況下這些 security 相關的機制也不會影響功能的正常使用，往往在真的爆出資安事件時才會被拿出來檢討...。然而 security 這類的問題處理起來就是很煩人，若不花點心思在程式碼的結構上，很容易就寫出義大利麵條式的程式碼出來...。我想把自己實作的經驗拿出來，讓各位讀者們參考一下，我認為理想的架構如何解決這類問題? 於是就有了想寫這系列文章的念頭。

----

本文開始前，先替我的就文章打個廣告，對這系列文章有興趣的，過去也有幾篇類似主題的文章可以參考:

[設計案例] "授權碼" 如何實作? 2016/02 (本篇系列文章)  

- #1, [需求與問題](/2016/02/17/casestudy_license_01_requirement/)  
- #2, [授權碼序列化](/2016/02/24/casestudy_license_02_serialization/)  
- #3, [數位簽章](/2016/02/24/casestudy_license_03_digital_signature/)  
- #3, (補) - [金鑰的保護](/2016/03/19/casestudy_license_03_appendix_key_management/)


[設計案例] 清除Cache物件, 2009/12  

- #1, [問題與作法](/2009/12/19/設計案例-清除cache物件-1-問題與作法/)
- #2, [Create Custom CacheDependency](/2009/12/19/設計案例-清除cache物件-2-create-custom-cachedependency/)


[設計案例] 生命遊戲, 2009/09  

- #1, [前言](/2009/09/12/設計案例-生命遊戲1-前言/)
- #2, [OOP版的範例程式](/2009/09/14/設計案例-生命遊戲2-oop版的範例程式/)
- #3, [時序的控制](/2009/09/15/設計案例-生命遊戲3-時序的控制/)
- #4, [有效率的使用執行緒](/2009/09/19/設計案例-生命遊戲-4-有效率的使用執行緒/)
- #5, [中場休息](/2009/09/24/設計案例-生命遊戲-5-中場休息/)
- #6, [抽像化 (Abstraction)](/2009/10/03/設計案例-生命遊戲-6-抽像化-abstraction/)
- #7, [多型 (Polymorphism)]


----



## [本文開始]

![](/wp-content/uploads/2016/02/img_56c350dc74e6a.png)  

我直接舉一個具體的情境，來描述要解決的問題。這個案例裡我把 "授權碼" 運用到網站的安裝上。我在公司開發的是商用系統，提供客戶 Install Based 的佈署模式，把系統安裝在客戶的 Data Center 內。以上圖為例，Service #B 及 Service #C 分別裝在不同客戶的 Data Center 內，而我們自行維護的 Cloud Service 則分別授權不同的功能給 Service #B 及 Service #C 呼叫 API 使用。這架構下碰到的問題是，無法保證能隨時連上 Internet，當然無法連上 Internet 就無法呼叫 Service #A 這些 Cloud Service，但是即使如此，授權的功能仍然要能發揮功效，無法被客戶的 IT 或是系統整合廠商的夥伴，未經過 Service Administrator 的許可就啟用。



如果把這些需求列成 Story, 那麼看起來會像這樣:

1. **網站授權的需求**:  
Server #B 或是 Server #C 上的功能及授權的使用期限，必須取得 Service Administrator (就是我們公司啦) 的授權才能啟用。然而 Service #B 及 Service #C 使用的是同一套系統，同一套程式碼，因此授權的啟用必須仰賴設定檔。然而除了原廠 (我們) 與客戶之外，中間還有系統整合廠商，會協助做整合或是客製化等等任務，他們必須熟悉這些設定的調整方式，因此必須找個能夠阻擋技術人員 (懂得 configuration 及 coding) 未經授權就能啟用功能的方法
1. **API KEY 機制的需求**:  
同樣的，Service #B 若要呼叫 Service #A 的 API，呼叫及傳輸過程必須有 API KEY 的機制保護，同時也一樣要取得原廠的授權才能啟用。Service #A 必須只檢查 API KEY 就要決定開放那些功能給 Service #B 呼叫
1. **授權期限的需求**:  
這一切都必須在封閉網路內能夠實現。某些組態下，甚至連 Service #A 也會搬到 Intranet 內，因此也無法在第一時間連回原廠的 server 做各種授權的驗證。這時授權的機制仍然必須正常運作，同時每次原廠發給授權必須配合服務合約，合約到期後授權必須中止，簽訂新的服務合約之後重新更換新的授權，才能恢復運作。
1. **安全強度的需求**:  
以上的安全機制，必須有一定水準的強度。防護的對象，可能包含熟悉架構的工程師，因此最好能用可靠的演算法或是加密的保護，即使是技術人員，沒有取得金鑰的情況下是沒有辦法突破這些防護的。
1. **擴充機制的需求**:  
這個機制必須容易擴充授權的功能，將來新增新的授權項目，或是新的服務，要能讓系統開發人員 (developer) 能輕易的沿用同樣的基礎架構，保護新的服務授權機制。

這些問題在技術上其實都不難解決，難的地方在於如何正確的使用業界的標準技術。其實要是你搞得懂對稱及非對稱加解密的運作原理，還有加密及數位簽章各是要解決什麼問題，這篇文章碰到的問題就解決一半了。剩下的另一半是什麼? 就是你的實作及封裝，是否符合開發人員 (developer) 的期待? 這邊提一下一個新名詞: DX (developer experience)，開發者體驗。什麼是 DX ? 可以看看 [這篇文章](http://nordicapis.com/why-api-developer-experience-matters-more-than-ever/) 的說明，我節錄其中一段:

> ![](http://nordicapis.com/wp-content/uploads/Why-API-Developer-Experience-Matters-web.jpg)  
> 
> **What Is Developer Experience?**  
> First, let’s look at **user experience** (UX) in general. UX considers the overall experience a person has with a
> mobile app or website. This attitude can be positive or negative given the value and ease of human-computer
> interactions.
> 
> Developer experience is an extension of UX that focuses on the developer, who can either be the intermediary or, as is
> the case [with many APIs, the end user](http://nordicapis.com/designing-apis-humans/). Whether or not you focus on DX
> design, your developers are always experiencing your API, and that experience may either be positive or negative.

DX 就跟 UX 一樣，為了讓使用者有更好的體驗。只是 DX 的 "使用者" 特別針對 Developer, 而非一般的使用者而已。API 能不能 Work, 跟 API 用的開不開心，是完全不同的兩回事，如何善用 OOP 的觀念，把這些問題寫成 CODE，如何善用 C# 的語法特性，能漂亮的實作這個架構，則是我另外一個想探討的主題。單純探討技術或語法感覺會像打高空一樣不切實際，所以就挑了個我最近碰到的實作案例來探討。


下回預告: #2, 序列化


# 參考文章:

- [Effective Developer Experience (DX)](https://uxmag.com/articles/effective-developer-experience)
- [APIs for Humans: The Rise of Developer Experience (DX)](http://blog.hellosign.com/the-rise-of-developer-experience/)
- [Why API Developer Experience Matters More Than Ever](http://nordicapis.com/why-api-developer-experience-matters-more-than-ever/)