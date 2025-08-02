---
layout: post
title: "Configuring Website Settings for CodeFormatter Compatibility"
categories:
tags: [".NET","作品集","技術隨筆"]
published: true
comments: true
redirect_from:
  - "/2008/04/04/搭配-codeformatter，網站須要配合的設定/"
  - /columns/post/2008/04/04/e690ade9858d-CodeFormatterefbc8ce7b6b2e7ab99e9a088e8a681e9858de59088e79a84e8a8ade5ae9a.aspx/
  - /post/2008/04/04/e690ade9858d-CodeFormatterefbc8ce7b6b2e7ab99e9a088e8a681e9858de59088e79a84e8a8ade5ae9a.aspx/
  - /post/e690ade9858d-CodeFormatterefbc8ce7b6b2e7ab99e9a088e8a681e9858de59088e79a84e8a8ade5ae9a.aspx/
  - /columns/2008/04/04/e690ade9858d-CodeFormatterefbc8ce7b6b2e7ab99e9a088e8a681e9858de59088e79a84e8a8ade5ae9a.aspx/
  - /columns/e690ade9858d-CodeFormatterefbc8ce7b6b2e7ab99e9a088e8a681e9858de59088e79a84e8a8ade5ae9a.aspx/
  - /blogs/chicken/archive/2008/04/04/3151.aspx/
wordpress_postid: 111
---

Just a side note, this plugin has received a small update again. You can [download it](http://www.chicken-house.net/files/chicken/ChickenHouse.LiveWriterAddIns.zip) from the original website.

This pretty much wraps things up. You're welcome to download and use it. However, some features require your BLOG SERVER to make adjustments to be effective. Let me explain them all:

## 1. **CSS**

The main reason I like using this function library is because the HTML it generates is very clean, as all the styling has been separated out to CSS. However, the downside is that you need to find another way to put the CSS up there... I'm providing the CSS content from the original manufacturer, and you can modify it however your BLOG SERVER allows. Taking CommunityServer that I use as an example, you just need to go into the DashBoard, go to the layout modification section, which provides a "Custom Styles (Advanced)" page, and just paste the CSS in there and you're done!

**C# Code Formatter CSS** [copy code]

```css
.csharpcode, .csharpcode pre
{
  font-size: small;
  color: black;
  font-family: Consolas, "Courier New", Courier, Monospace;
  background-color: #ffffff;
  /*white-space: pre;*/
}
.csharpcode pre { margin: 0em; }
.csharpcode .rem { color: #008000; }
.csharpcode .kwrd { color: #0000ff; }
.csharpcode .str { color: #006080; }
.csharpcode .op { color: #0000c0; }
.csharpcode .preproc { color: #cc6633; }
.csharpcode .asp { background-color: #ffff00; }
.csharpcode .html { color: #800000; }
.csharpcode .attr { color: #ff0000; }
.csharpcode .alt 
{
  background-color: #f4f4f4;
  width: 100%;
  margin: 0em;
}
.csharpcode .lnum { color: #606060; }
```

But don't rush to paste it!!! If you want the next feature, you'll need to add another CSS section...

## 2. **COPY CODE**

This feature isn't difficult - it just uses JavaScript to put a piece of text into the clipboard. However, the tricky part is how to smuggle this CODE into the article content... The CS I use blocks `<SCRIPT>` by default, so adding SCRIPT directly in HTML doesn't work. Of course, you could modify communityserver.config, but that's a bit troublesome, and I don't like changing it that way... So I brought out HTC..

The principle of HTC is simple. CSS manages various styles uniformly, so why can't DHTML events like onclick="..." onload="..." be managed uniformly like CSS? They can, but this requires IE-supported HTC (HTML Component) to achieve. The rising star jQuery actually has similar functionality, but to work with CS, you still need to find a way to hide `<SCRIPT>` in HTML, which is a bit troublesome... So in the end, I still chose to use HTC to implement this feature.

The setup is simple, just add another CSS section:

**CSS with HTC Support** [copy code]

```css
.copycode {cursor:hand; color:#c0c0ff; display:none; behavior:url('/themes/code.htc'); }
```

Then you need to put this [HTC](http://localhost/themes/code.htc) file in the directory specified in the CSS. According to the CSS above, you should put the HTC at /Themes/Code.HTC

That's it for the SERVER part. In the future, when inserting CODE, just check this option [The generated HTML will include the original source code]:

![image](/wp-content/be-files/WindowsLiveWriter/CodeFormatter_9FE0/image_9.png)

The final output will look like this, and the [copy code] function on the right side of the title will work normally. After clicking it, the SAMPLE CODE will be automatically copied to the clipboard, without being affected by all the formatting, so the CODE you copy can be used directly...

**MSDN Sample Code** [copy code]

```csharp
using System;

public class Sample {
    void Method() {
    Object Obj1 = new Object();
    Object Obj2 = new Object();
    Console.WriteLine(Obj1.Equals(Obj2)); //===> false
    Obj2 = Obj1;
    Console.WriteLine(Obj1.Equals(Obj2)); //===> true
    }
}
```

This feature isn't included in the preview. Also, I made some adjustments to the preview screen. On one hand, instead of directly opening the HTML file with IE, which would cause a bunch of security warning messages, I changed to using HTA (HTML APPLICATION) to implement the preview function. To thank the original author who provided this LIB, I also added his homepage to the preview screen. Finally, of course, I also have to promote my own website... Haha [H]

![image](/wp-content/be-files/WindowsLiveWriter/CodeFormatter_9FE0/image_8.png)

Well, this PLUGIN is pretty much finished. In the future, it'll probably just be bug fixes. Those who need it are welcome to download and use it. If you want to distribute it, please indicate the source.

[[Download Location]](http://www.chicken-house.net/files/chicken/ChickenHouse.LiveWriterAddIns.zip)
