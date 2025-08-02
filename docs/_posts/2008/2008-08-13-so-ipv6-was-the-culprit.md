---
layout: post
title: "原來是 IPv6 搞的鬼..."
categories:

tags: [".NET","ASP.NET"]
published: true
comments: true
redirect_from:
  - /2008/08/12/原來是-ipv6-搞的鬼/
  - /columns/post/2008/08/13/e58e9fe4be86e698af-IPv6-e6909ee79a84e9acbc.aspx/
  - /post/2008/08/13/e58e9fe4be86e698af-IPv6-e6909ee79a84e9acbc.aspx/
  - /post/e58e9fe4be86e698af-IPv6-e6909ee79a84e9acbc.aspx/
  - /columns/2008/08/13/e58e9fe4be86e698af-IPv6-e6909ee79a84e9acbc.aspx/
  - /columns/e58e9fe4be86e698af-IPv6-e6909ee79a84e9acbc.aspx/
wordpress_postid: 82
---

以前 (古早以前) 寫過一個簡單的 LIBRARY，就是去抓現在連上網頁的 CLIENT IP，然後簡單的套上 NET MASK，看看是不是在指定的網段內? 是的話就作些特別的處理 blah blah... 原本的 code 有點雜，我精簡之後變這樣，如果是 192.168.2.0 / 24 這範圍內的使用者連到這網頁，就會顯示 "Is Intranet? YES" ... 夠簡單吧? (怎麼連幾篇都這種不入流的 sample code ...)

這段 code 一直都運作的很好，沒碰過什麼大問題，不過就是把 IP address 切成四個 bytes, 然後利用位元運算併成 unsing integer, 方便跟後面的 netmask 作 bits and ...。不過某日興沖沖裝好 vista x64 + IIS7 之後發現，程式竟然不動了!?

先來看一下原始碼:

**ASP.NET 程式範例**

```csharp
<%@ Page Language="C#" Trace="true" %>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<script runat="server">
    protected void Page_Load(object sender, EventArgs e)
    {
        this.Trace.Warn(System.Net.IPAddress.Parse(this.Request["REMOTE_HOST"]).AddressFamily.ToString());
        this.IPLabel.Text = this.IsInSubNetwork(
            "192.168.2.0",
            "255.255.255.0",
            this.Request.ServerVariables["REMOTE_HOST"]) ? ("YES") : ("NO");
    }

    private bool IsInSubNetwork(string network, string mask, string address)
    {
        uint netval = _IP2INT(network);
        uint maskval = _IP2INT(mask);
        uint addval = _IP2INT(address);

        return (netval & maskval) == (addval & maskval);
    }
    
    private uint _IP2INT(string address)
    {
        string[] segments = address.Split('.');

        uint ipval = 0;
        foreach (string segment in segments)
        {
            ipval = ipval * 256 + uint.Parse(segment);
        }

        return ipval;
    }
 
</script>

<html xmlns="http://www.w3.org/1999/xhtml">
<head runat="server">
    <title>Untitled Page</title>
</head>
<body>
    <form id="form1" runat="server">
    <div>
    Is Intranet? <asp:Label ID="IPLabel" runat="server" />
    </div>
    </form>
</body>
</html>
```

後來追了半天才意外發現問題出在這... 打開 ASP.NET Trace, 看一下 REMOTE_ADDR 到底抓到啥子東西?

![image](/wp-content/be-files/WindowsLiveWriter/IPv6_13D1E/image_21.png)

嘖嘖嘖，搞半天原來是 Vista 預設把 IPv6 給開了起來，IIS7 / DevWeb 都中獎，直接回報 IPv6 格式的 IP Address 回來... 怎麼解? 這種問題說穿了就不值錢，強迫用 IPv4 就好。我試過幾種可行的方式，有:

1. **直接用 IPv4 的位址連線**: 這簡單，以我來說，URL 從 http://localhost/default.aspx 改成 http://192.168.100.40/default.aspx 就好了。不過這樣對 DevWeb 就沒用了，DevWeb 只接受來自 localhost 的連線...

   ![image](/wp-content/be-files/WindowsLiveWriter/IPv6_13D1E/image_22.png)

2. **改 IIS 設定，直接綁到 IPv4 的位址**，不過這招試不出來，似呼沒啥用，localhost 不會連到 192.168.100.40，而我直接打這 IP 的話就會變成範例1...

   ![image](/wp-content/be-files/WindowsLiveWriter/IPv6_13D1E/image_23.png)

3. **改 c:\windows\system32\drivers\etc\hosts**

   無意間 PING 看看 localhost, 才發現連 localhost 都被對應到 IPv6 了...

   ![image](/wp-content/be-files/WindowsLiveWriter/IPv6_13D1E/image_29.png)

   打開 C:\windows\system32\drivers\etc\hosts 這檔案看一看，果然...

   ![image](/wp-content/be-files/WindowsLiveWriter/IPv6_13D1E/image_28.png)

   把 IPv6 那行拿掉後再試試 ping localhost ...

   ![image](/wp-content/be-files/WindowsLiveWriter/IPv6_13D1E/image_27.png)

   耶! 這次 IP 就變成 IPv4 的了... 開 IE, 連 http://localhost/default.aspx 看看，it works!

   ![image](/wp-content/be-files/WindowsLiveWriter/IPv6_13D1E/image_26.png)

   因為這招是直接把 localhost 對應到 127.0.0.1，因此對於鎖 localhost 的 WEBDEV 也可以用。

4. **大絕招: 直接關掉 IPv6 ...**

   真是個沒品的傢伙，打不過就來這套...

   ![image](/wp-content/be-files/WindowsLiveWriter/IPv6_13D1E/image_25.png)

   ![image](/wp-content/be-files/WindowsLiveWriter/IPv6_13D1E/image_24.png)

   這樣也可以...

碰到這種怪問題，一時之間還熊熊不知道是那裡掛掉，還真是麻煩... 特地記一下這篇，讓一樣吃過 IPv6 苦頭的人參考一下。至於怎樣作才對? 當然是用 "正規" 的方式來處理 IP Address... System.Net.IPAddress 類別包含一個靜態方法: IPAddress Parse(string ipaddress), 用它可以把字串格式的 IP 換成這個類別的 instance, 用它內建的 property: AddressFamily，看看值是 enum 型態的 InterNetwork 還是 InterNetworkV6 就知道了，不要像我當年年少不更事一樣，自己硬去拆字串... Orz
