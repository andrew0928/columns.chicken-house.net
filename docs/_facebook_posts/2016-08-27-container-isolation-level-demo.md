---
date: 2016-08-27
datetime: 2016-08-27T14:12:14+08:00
timestamp_utc: 1472278334
title: "Container 隔離層級測試：Host 對 Container 的影響"
---

今天 "忍痛" 跳過的 demo, 主要是展示 container 的隔離層級的差別。現在我手上的 2016 TP5 還沒辦法在 VM 內展示 hyper-v container, 我就針對一班的 container isolation level 來測試

host 可以跳過 container 的管控，直接影響到 container 內的 process, 但是 container 內則受到隔離，無法看到其他 container 在搞甚麼..

實際的例子可以看影片，用 host 的工作管理員可能會搞壞 container, 實際部屬時大家可以評估看看你的 host 是否能信賴他，進而挑選合適的隔離層級
