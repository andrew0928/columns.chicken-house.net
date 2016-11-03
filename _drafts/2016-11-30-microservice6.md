---
layout: post
title: "API Hosting @ Azure"
categories:
- "有的沒的"
tags: ["有的沒的"]
published: false
comments: true
redirect_from:
logo: /public/logo.png
---

前面花了很多篇幅，介紹怎麼寫好一組 API，現在寫好的服務應該要上線了，這篇就來探討一下，除了寫好 Code 之外，API 服務
要上線還要注意什麼? 雲端時代當然就別再自己養機器了，所以今天的範例，我會用 Azure 來示範。Microsoft 特地為了 API 型態
的服務，設計了 API Apps, 替開發者省了不少功夫。其實 Azure 還有更進階的 API manager, 不過這部分這篇只會點到為止的介紹。
實際應用案例，我會留到 Microservice 部署的議題時再拿出來探討。


<!--more-->

{% include series-2016-microservice.md %}

# 線上環境，除了 API 之外你還需要什麼?

Developer 當久了，往往除了寫 code 之外其他都會忘掉... 這就是 developer 跟 stakeholder 的差別。
切記，永遠別忘了你寫的code 是要解決什麼問題。前面提過了，API 的使用者就是其他的 developer, 寫 code 來
呼叫你的 service。因此你要留意的是 DX (**D**eveloper e**X**perience)。DX 包含哪些東西? 

這篇文章 "[What is API Developer Experience and Why It Matters](https://www.infoq.com/news/2015/10/api-developer-experience#.WBtTAul_ScU.facebook)" 
寫的不錯，很扼要的點出 API DX 的四個要點，我就補充一下我的看法:

Four key concerns that can help reach the goal of API excellence:
* **Functionality**:  
  這是最重要的一點了，就是你的 API 到底有沒有把你要解決的問題做好? 有沒有做到完美? 如果沒有做到一個水準之上，
  別的團隊自己寫一個就好了啊~ 沒錯，API 既然專注在解決特定問題，你就有義務把他做到比別人好，這 API 才有存在的價值。 

* **Reliability**:  
  除了功能面上的考量之外，服務的可靠度也是很關鍵的一環。包含是否穩定可靠? SLA 是否夠理想? 這些都是 developer 不想碰的議題
  但是這也是使用者在意的議題，沒辦法忽略他。

* **Usability**:  
  一般系統在講 usability (可用性)，是指這個東西到底好不好操作? 用在這邊就代表這個 API 好不好董，文件清不清楚這類議題。
  好的 API，文件應該很容易查閱才對，甚至有各種 sample code, 搭配運用的 tools, 甚至還有不用寫 code 就能試著呼叫 API 的
  線上工具等等。

* **Pleasure**:  
  除了上述幾點之外，使用你的 API / SDK 的開發者，用起來心情是愉快的嗎? :D
  