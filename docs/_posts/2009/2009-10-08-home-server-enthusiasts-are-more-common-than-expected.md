---
layout: post
title: "原來在家裝 SERVER 的魔人還真不少..."
categories:
tags: ["技術隨筆","敗家","有的沒的","水電工"]
published: false
comments: true
redirect_from:
  - /2009/10/08/原來在家裝-server-的魔人還真不少/
  - /columns/post/2009/10/08/e58e9fe4be86e59ca8e5aeb6e8a39d-SERVER-e79a84e9ad94e4babae98284e79c9fe4b88de5b091.aspx/
  - /post/2009/10/08/e58e9fe4be86e59ca8e5aeb6e8a39d-SERVER-e79a84e9ad94e4babae98284e79c9fe4b88de5b091.aspx/
  - /post/e58e9fe4be86e59ca8e5aeb6e8a39d-SERVER-e79a84e9ad94e4babae98284e79c9fe4b88de5b091.aspx/
  - /columns/2009/10/08/e58e9fe4be86e59ca8e5aeb6e8a39d-SERVER-e79a84e9ad94e4babae98284e79c9fe4b88de5b091.aspx/
  - /columns/e58e9fe4be86e59ca8e5aeb6e8a39d-SERVER-e79a84e9ad94e4babae98284e79c9fe4b88de5b091.aspx/
wordpress_postid: 25
---

看了 [這一篇: How I manage servers in my house](https://learn.microsoft.com/en-us/archive/blogs/virtual_pc_guy/how-i-manage-servers-in-my-house), (virtual pc guy’s weblog)，才發現我比起來真是小 CASE ... 哈哈，看他這樣寫，正好最近升級到 2008R2，我也趁機把我的 SERVER 介紹一下好了 :D

最早在家裡架 SERVER，可以追溯到 1997 ... 當時剛當兵，花了一些時間在看 MCSE 那堆 NT server administration 的書... 雖然後來沒去考，不過學到的東西還挺有用的。第一個想架的念頭，就是在 NT4 上面裝 RRAS，然後讓全家 (其實也只有我跟我姊而已) 共用一台 modem 撥接上網... 那時就弄起 RRAS，自己也寫了個 DCOM 的小程式，方便從我的 PC 遠端叫 NT SERVER 的 modem 撥號上網...

接著就越用越兇了，基本的 NAT, NT domain controller, File Server, Printer Server, Fax Server, DHCP server 都是基本用途... 後來開始架網站，買了 chicken-house.net 這 domain name 後，開始加上 DNS / IIS / SQL 起來... 再來連 VPN 都弄起來後，事業就越作越大了..

NT4 進步到 2000 時，原本的 NT domain 升級成 Active Directory, 開始覺的在家裡弄個 AD 有點過頭了，所以之後就沒再用 Domain, 只用 workgroup .. 直到現在...。每次重灌 SERVER 最頭痛的就是那堆帳號全部得重設一次，加上現在 Hyper-V 的效能很不錯，已經到了實用的階段，就重新燃起這念頭，也就是現在的配置。正式來介紹一下我的 SERVER 吧 :D