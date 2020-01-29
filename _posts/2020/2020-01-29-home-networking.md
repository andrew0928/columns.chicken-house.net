---
layout: post
title: "水電工日誌 8. 善用 VLAN + UniFi AP 建置家用網路環境"
categories:
- "系列文章: 水電工日誌"
tags: ["水電工", "有的沒有的", "敗家"]
published: false
comments: true
redirect_from:
logo: 
---

趁著過年, 繼上篇把家裡的 wifi 弄起來之後, 過年期間我把最後一哩路也補上了。總算，從 12 年前初次建置後，這次我終於把累積的幾個需求通通都解決掉了。物理上最麻煩的就是布線了，這次總算在過年前把實體的環境跟設備都準備到位了，過年期間可以好好的把線上的設定跟組態全部搞定，過完年開工就可以正式享用建設的成果了 :D

由於是我自己的施工跟建置紀錄，寫起來有點像流水帳；但是其中有不少我自己搭建 UniFi (非全家筒, 有部分是自行搭配) 採到的地雷，我相信會有很多人有興趣想要參考的。因此我就按照我的需求來逐一說明。如果你碰到的環境跟需求跟我雷同，那就可以點近來參考看看我的作法。

事隔 12 年，我自己在三個月前，期望要解決的問題有這些:

1. 隔離: servers / NAS 要有獨立的網段, 手機 / PC 存取要經過防火牆防護。NAS / 我的 PC 要能支援 LACP
1. 隔離: 不受信任的設備有獨立網段, 要能上網但是不能存取內部網路 (訪客手機, 以及部分需要上網的大陸家電: 小米電扇, 小米掃地機器人... etc)。
1. 統一 WiFi SSID, 兩台 AP 之間可以自動漫遊不用再手動選擇切換。
1. 監控設備網路化 (原本是類比監控攝影機, 需要額外一台 DVR, 線路要透過 cable 同軸電纜, 希望統一改成網路線)。
1. 我個人 PC 要有專屬 port, 能直接存取家中所有的網段, 包含能直接撥接 PPPoE。
1. 集中管理，簡化實體架構 (包含設備跟最少的佈線), 需要建置的管理服務全部往 NAS 集中 (docker, 內建 package 皆可), 設備別讓我再擔心散熱或穩定度問題。

於是，花了三個月，空閒之餘 (平常沒什麼空閒啊啊啊啊) 總算買齊也建置好我理想中的環境了。以下我列出這次從頭到尾我採購的設備清單，如果不想踩雷可以參考我的清單 (除了二手品之外，其他都是含稅開發票, 不含運費):

1. 網路卡: Intel i350-T4 (OEM, 二手), NTD 900
1. 路由器: Ubiquiti EdgeRouter-X SFP (曾經考慮過 USG: UniFi Security Guard, 最後決定的原因後述), NTD 2900
1. 交換器: Netgear GS116E v2 (16 ports, 網管, NTD 3210), Netgear GS108PE v3 (8 ports, 網管, PoE, NTD 3150)
1. 基地台: Ubiquiti UniFi AP AC-Lite x 2, NTD 6600
1. 攝影機: Ubiquiti UniFi UVC-G3 Flex x 2, NTD 5800

相關的既有設備:

1. NAS #1 (Synology DS-918+, 執行 UniFi controller, UniFi video controller, Synology Surveillance Station)
1. NAS #2 (Synology DS-412+, 負責備份)
1. 我的 PC (AMD Ryzen 9 - 3900X, 64GB, Samsung 970Pro 480GB SSD)

其他材料類型的就參考用了，我單純是自己想紀錄而已:

1. 拉線器 (10m)
1. 網路線 (50m) + 水晶頭 (RJ45 x 100)
1. 標籤機: (這是亂入的) 精臣 D11 + 網路標線貼紙 x 2

OK, 專案需求列好了, 設備清單也出來了, 剩下就剩建置系統而已。如果上面有講到你感興趣的細節, 那就往下看吧 :D


<!--more-->

# 前言 - 為何不挑選 UniFi 全家筒?

// cost

// 可用性: 希望 router 活著，主要網路都還能正常運作

// 儲存都集中到 NAS
// - syslogd
// - video record
// - redius

// poe

// 手X, 想自己摸索 router, switch, vlan

// next: UDM pro

// https://www.mobile01.com/topicdetail.php?f=110&t=5952455&p=3
// 1. 若一台 NAS 是透過 USG 配發 DHCP，是不是在這台 NAS 的 Docker 上是沒辦法裝 Unifi Controller 去控制 USG 的，因為我可以抓到，但是他會一直斷掉，不能接管

// no qos
// expected IDP

# VLAN 規劃與設定

// vlan: 1,  設備管理網路
// vlan: 10, MODEM
// vlan: 100, NAS
// vlan: 200, Home
// vlan: 201, Guest

// PC settings

// NAS settings (?)




// ref:
// https://blog.router-switch.com/2014/04/network-design-with-examples-core-and-distribution/
// https://www.microsemi.com/applications/communications/enterprise-infrastructure
// https://blog.westmonroepartners.com/a-beginners-guide-to-understanding-the-leaf-spine-network-topology/






// ref:
// https://www.windshow.com/archives/1516

// ref:
// https://medium.com/@nonsingular/unifi-usgpro4-dualwan-%E8%A8%AD%E5%AE%9A%E7%AD%86%E8%A8%98-f707ba54a18f

## 網管設備的管理: SWITCH

// 管理 IP 透過 vlan1 發放

## 網路設備的管理: AP + VLAN

// AP 管理 IP 透過 vlan1 or untagged lan 發放

## 外部存取: L2TP VPN

## PC 端的設定

// pppoe

// intel vlan

// switch config




# AP 設定 (SSID, Guest WiFi without USG)

# CAM 設定 (UniFi Video vs Synology Surveillance)

## 佈線

## UniFi Video / UniFi Protect / Synology Surveillance Station