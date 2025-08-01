---
layout: post
title: "Next Ten Years..."
categories:

tags: ["有的沒的","水電工"]
published: true
comments: true
redirect_from:
  - /2008/05/12/next-ten-years/
  - /columns/post/2008/05/12/Next-Ten-Years.aspx/
  - /post/2008/05/12/Next-Ten-Years.aspx/
  - /post/Next-Ten-Years.aspx/
  - /columns/2008/05/12/Next-Ten-Years.aspx/
  - /columns/Next-Ten-Years.aspx/
  - /blogs/chicken/archive/2008/05/12/3236.aspx/
wordpress_postid: 107
---

經過一個禮拜的準備，總算在這週末完成移機的動作了... 為什麼標題叫 "Next Ten Years" ? 因為換下來的 server 已經陪我十年了，不知道這次換的新 SERVER 能不能陪我再撐十年?

沒想到當年的 ASUS P2B-DS 這麼耐用，中間換了 CPU，換了 RAM，機殼，顯示卡，連硬碟光碟都換過好幾次了，唯獨主機板跟 Power 都沒換過...

![CRW_4278 (Canon PowerShot G2)](/wp-content/be-files/WindowsLiveWriter/NextTenYears_2C30/CRW_4278%20(Canon%20PowerShot%20G2)_thumb.jpg)  
舊 server 拆掉前

其實舊 server 能撐這麼久也不是沒有原因的，除了硬體都沒壞之外，老實說跑跑簡單的 NAT / DHCP / DNS 也都夠用，跑現在這個網站 (BLOG + SQL) 也都撐的住。不過規格時在是不饒人啊，現在已經買不大到 IDE 的硬碟了，就算買的到也很不划算。前陣子弄了張 PCI 的 4 ports SATA card，結果也因為BIOS實在太古董了，裝上硬碟就停在那邊不開機 @_@，舊硬碟只要 COPY 大檔，SQL 2005 Express 就給我罷工... 最後跟同事借了台量耗電的機器，舊SERVER一開機就要 150W... 以它的處理能力來說實在不划算，所以才會忍不住去敗了零件來換...

本來換機的 roadmap 規劃的很漂亮，想說等到 2009 Q1 ~ Q2，INTEL換了新的架構後，現在的桌機 (P5B-E Plus + E6300) 拿來當SERVER，桌機就換新的... 不過實在是受不了硬碟一直維持不到 5% 剩餘空間，加上每次一挪空間網站就給我掛掉，就改變策略直接買來換掉現在的SERVER，桌機就將就點用吧...

這次換的配備，都是以省電為主要訴求，規格就挑同級裡最低階的:

| 配件 | 規格 |
|------|------|
| CPU | Intel Core2 Quad Q9300 |
| RAM | A牌 DDR2-800 2GB x 4 |
| 主機板 | Intel Q35 (ASUS P5E-VM DO) |
| 硬碟 | WD7500AACS (750GB) x 3 |
| Power | S牌 330W |

一直覺的SERVER還要找張VGA卡裝上去實在是很雞肋，跟本用不到幾次，不過不裝又很麻煩... 雖然2003號稱可以支援，不過我想還是別自找麻煩好了 [H]，主機板就鎖定 Q35 的，因為它定位在商用機種，內建 VGA，同時又保有基本的效能... 不會像其它內建顯示晶片的板子，要嘛RAM只能插兩條，不然就是SATA只有四個...

CPU挑了四核最入門的 Q9300，為什麼不挑 Q6600 ? 差一千五左右，不過耗電量跟溫度都有差，因為我堆SERVER的房間通風很差，太熱實在很麻煩，就挑了Q9300. 硬碟挑的是WD GP系列，閒的時後轉速可以自動從7200降到5400，正好符合我的需求。我一向不大在意硬碟有多快... 反正快慢頂多差個10%，實在沒差多少，容量多一點，溫度低一點比較實在..

![CRW_4285 (Canon PowerShot G2)](/wp-content/be-files/WindowsLiveWriter/NextTenYears_2C30/CRW_4285%20(Canon%20PowerShot%20G2)_thumb.jpg)

裝好的新 SERVER

舊 SERVER 把機殼塞的滿滿的，相對之下新SERVER就顯的小多了，多插張網路卡就一切搞定了，之前插的滿滿的 (網卡 x 2 + USB + VGA ...) 耗電量也省的多，之前只接一顆硬碟，只要 70W... 四顆硬碟都加上去應該也不到 100W... 早知道買 330W 的 POWER 幹嘛...

移機的過程就不提了，原本還很謹慎的弄台IP分享器，想說換機過程中至少讓家裡對外網路是通的，事實證明這完全是多此一舉... 家裡會上網的人全都睡覺去了 [H]... 不過還是要感謝一下提供IP分享器的米國人 [:D] (沒錯，Honga 就是你..)，貼張照片感謝一下:

![CRW_4274 (Canon PowerShot G2)](/wp-content/be-files/WindowsLiveWriter/NextTenYears_2C30/CRW_4274%20(Canon%20PowerShot%20G2)_thumb.jpg)

換完後又設定東設定西，檔案這裡搬過來那裡搬過去，總算弄完了。最後除了舊的 Modem 找不到 windows 2003 x64 driver 之外，其它一切正常。因為系統都重灌了，有缺啥設定漏掉的，或是發現網站那裡不正常的再通知我吧!

--------  
趁機借問一下，有沒有推薦的 USB Modem (我只要拿來收發傳真而以)，有 2003 x64 驅動程式的? 網站是找到幾款，不過都是天價，不然就是市面上買不到...
