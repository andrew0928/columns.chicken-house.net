---
layout: post
title: "WMCmd.vbs 在 VISTA 下執行會導至 cscript.exe 發生錯誤..."
categories:

tags: ["Tips","技術隨筆","有的沒的"]
published: true
comments: true
redirect_from:
  - /2007/04/15/wmcmd-vbs-vista-cscript-error-fix/
  - /2007/04/15/wmcmd-vbs-在-vista-下執行會導至-cscript-exe-發生錯誤/
  - /columns/post/2007/04/16/WMCmdvbs-e59ca8-VISTA-e4b88be59fb7e8a18ce69c83e5b08ee887b3-cscriptexe-e799bce7949fe98cafe8aaa4.aspx/
  - /post/2007/04/16/WMCmdvbs-e59ca8-VISTA-e4b88be59fb7e8a18ce69c83e5b08ee887b3-cscriptexe-e799bce7949fe98cafe8aaa4.aspx/
  - /post/WMCmdvbs-e59ca8-VISTA-e4b88be59fb7e8a18ce69c83e5b08ee887b3-cscriptexe-e799bce7949fe98cafe8aaa4.aspx/
  - /columns/2007/04/16/WMCmdvbs-e59ca8-VISTA-e4b88be59fb7e8a18ce69c83e5b08ee887b3-cscriptexe-e799bce7949fe98cafe8aaa4.aspx/
  - /columns/WMCmdvbs-e59ca8-VISTA-e4b88be59fb7e8a18ce69c83e5b08ee887b3-cscriptexe-e799bce7949fe98cafe8aaa4.aspx/
  - /blogs/chicken/archive/2007/04/16/2344.aspx/
wordpress_postid: 167
---

我用的冷門工具在 vista 裡又碰到問題了 [:S]

Windows Media Encoder 9 附的 script: WMCmd.vbs, 在 vista 下執行時, cscript.exe 就會因為 DEP 的原因發生問題, 被攔下來, 看來 Microsoft 自己的 code 也是到處都藏著地雷, 隨便也碰到 data segment 被執行的狀況, 然後 DEP 就啟動了...

本想把 DEP 關掉了事, 不過 cscript.exe 在 vista 還被限定非得開啟 DEP 不可, Orz, 只好 Google / Microsoft support 查看看有沒有解了. 沒想到運氣還真不錯, 果然在官方網站找到 solution:

> FIX: You may experience issues when you use Windows Media Encoder 9 Series on a computer that is running Windows Vista

> URL: [http://support.microsoft.com/kb/929182/en-us](http://support.microsoft.com/kb/929182/en-us)

果然 FIX 裝了就一切正常, 以前寫的[批次轉 video script](/post/e5a4a7e5b7a5e7a88b-60GB-e79a84-DV-avi-e5a393e68890-WMV.aspx) 繼續用, 剩下只缺 Canon 補上 .CRW 的 codec 了 [:D]
