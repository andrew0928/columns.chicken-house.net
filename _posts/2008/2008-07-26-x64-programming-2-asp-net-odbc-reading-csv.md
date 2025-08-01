---
layout: post
title: "x64 programming #2: ASP.NET + ODBC (讀取 CSV)"
categories:

tags: [".NET","ASP.NET","Tips","技術隨筆"]
published: true
comments: true
redirect_from:
  - /2008/07/26/x64-programming-2-asp-net-odbc-讀取-csv/
  - /columns/post/2008/07/26/x64-2-ASPNET-2b-ODBC-(e8ae80e58f96-CSV).aspx/
  - /post/2008/07/26/x64-2-ASPNET-2b-ODBC-(e8ae80e58f96-CSV).aspx/
  - /post/x64-2-ASPNET-2b-ODBC-(e8ae80e58f96-CSV).aspx/
  - /columns/2008/07/26/x64-2-ASPNET-2b-ODBC-(e8ae80e58f96-CSV).aspx/
  - /columns/x64-2-ASPNET-2b-ODBC-(e8ae80e58f96-CSV).aspx/
wordpress_postid: 83
---

今天的範例超簡單，簡單到很沒水準的地步... 難道本 columns 的水準降低了嘛? 咳咳... 不多說，今天的例子也不需要解釋，直接來看 sample code:

**Default.aspx.cs 程式碼**

```csharp
using System;
using System.Data;
using System.Web.UI.WebControls;
using System.Data.Odbc;

public partial class _Default : System.Web.UI.Page 
{
    protected void Page_Load(object sender, EventArgs e)
    {
        DataSet ds = new DataSet();
        OdbcConnection conn = new OdbcConnection("Driver={Microsoft Text Driver (*.txt; *.csv)};DBQ=" + Server.MapPath("~/App_Data"));
        OdbcDataAdapter adpt = new OdbcDataAdapter("select * from [database.txt]", conn);
        adpt.Fill(ds);

        this.DataGrid1.DataSource = ds.Tables[0];
        this.DataGrid1.DataBind();
    }
}
```

真的是沒什麼特別的 code, 連 exception 都沒處理... 難道 .aspx 有什麼特別的嘛? 來看看:

**Default.aspx**

```html
<%@ Page Language="C#" AutoEventWireup="true"  CodeFile="Default.aspx.cs" Inherits="_Default" %>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head runat="server">
    <title>Untitled Page</title>
</head>
<body>
    <form id="form1" runat="server">
    <div>
    <asp:DataGrid ID="DataGrid1" runat="server" />
    </div>
    </form>
</body>
</html>
```

真的沒啥特別的，再來看看 CSV 檔的內容好了，看看有沒有什麼特別的...

**~/App_Data/database.txt**

```
name,email
chicken,chicken@chicken-house.net
peter,peter@chicken-house.net
annie,annie@chicken-house.net
nancy,nancy@chicken-house.net
```

咳，想扁我的忍一下... 這支程式大概只比 "Hello World" 好一點，會看本 BLOG 的大概用看的就知道結果是什麼了吧? 不就把所有的內容套到 DataGrid 裡顯示出來? 像這樣:

![image](/wp-content/be-files/WindowsLiveWriter/x642ASP.NETODBCCSV_42B/image_3.png)

真是沒營養的內容... 現在要開始進入主題了。執行環境是 Vista x64 + Visual Studio 2008，這個 web site 是透過 DevWeb 來執行的，不是透過 IIS... 反正都一樣嘛，測完可以 RUN (這種程式應該不會有什麼 BUG，頂多打錯字編譯錯誤..) 後就收工了，把它 DEPLOY 到 IIS 上面 ( windows 2003 x64, IIS6 ) 跑看看:

![image](/wp-content/be-files/WindowsLiveWriter/x642ASP.NETODBCCSV_42B/image_6.png)

掛了... 當然... 不然這篇是要討論什麼? 老實說這是我親身碰到的例子，從這錯誤訊息還真摸不著頭腦，完全搞不懂發生什麼事。該裝的都裝了，也都沒錯，為什麼會這樣? 二話不說，先確定系統的 ODBC 是正常的，最好的方式就是找現成的程式試看看，就可以初步判定是我的問題 OR 系統的問題。到控制台的 ODBC Data Source Administrator 看看，先建個同樣的 ODBC data source...

![image](/wp-content/be-files/WindowsLiveWriter/x642ASP.NETODBCCSV_42B/image_9.png)

真是見鬼了，我的 windows 95 vpc 能用的 odbc driver 都比這裡多... 看來真的是沒有 ODBC driver，那我裝的 ADODB 是裝到那裡去了?

科學的實驗都講求先假設，再控制變因，然後證明假設是正確的... 不過現在一點線索都沒有，只能靠運氣了。會有這篇也真的是運氣好，聯想到是不是 x64 的問題? 用我謹有的知識: x64 / x86 兩種模式的程式不能同時出現在單一 process, 為了證明這件事，就特地在 SERVER 安裝了 excel, 用 excel 來開啟 odbc, 竟然可以?

解這問題，裝 office 是一年多前的事了，現在也沒畫面好抓，就跳過去... 想到 x64 一堆東西都有兩種版本，控制台是不是也有? 真該好好拿箱仙草蜜，拜一拜交大門口的土地公... Bingo! 執行了32位元版的 ODBC Data source Administrator (c:\Windows\SysWOW64\odbccp32.cpl), 結果出現了這畫面:

![image](/wp-content/be-files/WindowsLiveWriter/x642ASP.NETODBCCSV_42B/image_12.png)

真是好狗運，如果沒矇對的話，不知道還要搞多久... 這時才恍然大悟，原來 x64 要求所有的 driver 都要是 64 位元版，加上單一 process 不能混用 x86 / x64 兩種模式的 code，就是指這個... driver 不只是 "硬體" 的 driver，連各種軟體的都算。廣義一點來說，ODBC driver, OleDB Provider 也都算 driver 的一種，各種 Plug-Ins，甚至是各種 COM 元件 (只要是 In-Process 的都算)，到 COM 的延伸... IE ActiveX Control，Media Player 用的 Codec ... 通通都算...

我終於體會到要轉移到 x64 有多麻煩了。在 DOS 年代或是 WIN 3.1 年代，每個軟體都很獨立，換到 WIN32 沒什麼問題。現在的軟體就不一樣，轉到 x64 都可以跑，不過要用到的各種共用元件就不一定了。拿掉 COM 的話，VB / ASP 大概就什麼都不剩了吧...

回題，來看看這問題怎麼解。雖然搞清楚原因，但是我的程式還是不能動。CSV 其實還可以用文字檔硬解，不過我實際工作上碰到的例子是要解讀上傳的 EXCEL 檔的內容... EXCEL 我可沒辦法硬搞... 不過現在方向清楚了，只要有辦法把程式從 64 位元模式改成 32 位元模式執行，就可以抓的到 32 位元模式下的 ODBC Data Source, 程式就正常了。不過該怎麼告訴 IIS6，我的程式需要的執行環境是 32 位元?

上網查了一下 x64 版的 IIS 如何執行 x86 模式的程式? 找到這篇:

[http://support.microsoft.com/kb/894435/zh-tw](http://support.microsoft.com/kb/894435/zh-tw)

IIS 6.0 同時支援 32 位元模式及 64 位元模式。但是，IIS 6.0 不支援同時在 64 位元版的 Windows 上執行兩種模式。ASP.NET 1.1 只能在 32 位元模式中執行。ASP.NET 2.0 可以在 32 位元模式或 64 位元模式中執行。因此，如果要同時執行 ASP.NET 1.1 和 ASP.NET 2.0，您必須在 32 位元模式中執行 IIS。

實際切換的動作在這篇也有寫...

**ASP.NET 2.0 的 32 位元版本**  
如果要執行 32 位元版的 ASP.NET 2.0，請依照下列步驟執行：  
1. 按一下 [開始]，再按一下 [執行]，輸入 cmd，然後按一下 [確定]。  
2. 輸入下列命令以啟用 32 位元模式：  
cscript %SYSTEMDRIVE%\inetpub\adminscripts\adsutil.vbs SET W3SVC/AppPools/Enable32bitAppOnWin64 1  
3. 輸入下列命令以安裝 ASP.NET 2.0 (32 位元) 的版本，以及在 IIS 根目錄和下列位置底下安裝指令碼對應：  
%SYSTEMROOT%\Microsoft.NET\Framework\v2.0.40607\aspnet_regiis.exe -i  
4. 請確定在 Internet Information Services Manager 的 Web Service Extension 清單中，將 ASP.NET 2.0.40607 版 (32 位元) 的狀態設定為 Allowed。

切換過後，再重新執行一次，一切就正常了:

![image](/wp-content/be-files/WindowsLiveWriter/x642ASP.NETODBCCSV_42B/image_15.png)

雖然在 x64 下執行 x86 的程式，也是有一堆額外的好處，不過看起來就是不大爽... IIS6 只能二選一，兩種模式只能挑一種。這個問題到了 IIS7 就獲得解決了。 IIS7 允許同時存在這兩種模式的 Application ..

其實在 x64 下的問題還很多，不過大都不外乎這模式，x64 / x86 的 dll 不能混用。現今軟體都用一堆元件，你得確保每一個用到的元件都有 x64 版，如果有一個沒有? 乖乖的切回 x86 來執行吧...。類似的小狀況其實還蠻多的，下回多列幾種我碰到的狀況，以免各位跟我一樣碰釘子還試個老半天... 敬請期帶第三集 :D
