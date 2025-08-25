---
layout: post
title: "皮哥皮妹的年齡 user control ..."
categories:

tags: [".NET","ASP.NET","Community Server","家人","技術隨筆","有的沒的"]
published: true
comments: true
redirect_from:
  - /2007/01/18/皮哥皮妹的年齡-user-control/
  - /columns/post/2007/01/18/e79aaee593a5e79aaee5a6b9e79a84e5b9b4e9bda1-user-control-.aspx/
  - /post/2007/01/18/e79aaee593a5e79aaee5a6b9e79a84e5b9b4e9bda1-user-control-.aspx/
  - /post/e79aaee593a5e79aaee5a6b9e79a84e5b9b4e9bda1-user-control-.aspx/
  - /columns/2007/01/18/e79aaee593a5e79aaee5a6b9e79a84e5b9b4e9bda1-user-control-.aspx/
  - /columns/e79aaee593a5e79aaee5a6b9e79a84e5b9b4e9bda1-user-control-.aspx/
  - /blogs/chicken/archive/2007/01/18/2068.aspx/
wordpress_postid: 193
---

![Age Control](/images/2007-01-18-children-age-user-control/age-control.gif)

每次看 sea 在貼文章都會貼小皮幾歲幾個月, 妹妹幾個月... 就想說直接寫個 user control 就搞定了, 沒想到真的寫下去還有點小麻煩... 哈哈...

曆法的規則還真不少, 難怪每個教寫程式的書都會來一段萬年曆的 sample code.. 每個月天數都不一樣, 還有潤年不潤年的, 四年一潤, 百年不潤, 四百年又潤... 

這堆原則弄下來, 單純的幾歲幾個月反而不好算了, 算從出生到現在共幾天, 去除 365 當歲數的誤差還好, 餘數再除 30 當月份的誤差就不小了, 最後的餘數再當天數就完全不對了...

弄了一下, 果然寫元件的爽度就是不一樣... 這個 control 寫好後的用法是這樣:

> `<CH:Age runat="server" birthday="2000/05/20" pattern="阿扁當總統已經 {0} 年 {1} 個月了" />`
> 
> 會顯示: `阿扁當總統已經 6 年 7 個月了`

細節就不多說了, 以後進到 皮哥&皮妹的小天地 的左上角, 就看的到年紀, 純脆自己爽一下, 我們家的 blog 又跟別人的有一點點地方不一樣了 :D
