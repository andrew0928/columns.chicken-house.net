Source-Code-(update).aspx/
  - /post/2006/11/18/Digital-Camera-Filer---Source-Code-(update).aspx/
  - /post/Digital-Camera-Filer---Source-Code-(update).aspx/
  - /columns/2006/11/18/Digital-Camera-Filer---Source-Code-(update).aspx/
  - /columns/Digital-Camera-Filer---Source-Code-(update).aspx/
  - /blogs/chicken/archive/2006/11/18/1953.aspx/
wordpress_postid: 204
---

這個程式其實很簡單, 最麻煩的兩個部份都找到現成的 library 就解決掉了, 剩下的就只有剪剪貼貼的手工業而以. 先介紹這個 tools 開發時用到的兩套 library:

1. PhotoLibrary: 封裝 System.Drawing.Image 方便讀取 EXIF 等資訊.  
   Project Site: [http://www.gotdotnet.com/workspaces/workspace.aspx...](http://www.gotdotnet.com/workspaces/workspace.aspx...)
2. Microsoft RAW Image Viewer: 它提供了 canon sdk 及 .net wrapper  
   Download Site: [http://www.microsoft.com/downloads/details.aspx?fa...](http://www.microsoft.com/downloads/details.aspx?familyid=D48E808E-B10D-4CE4-A141-5866FD4A3286&displaylang=en)

扣掉這兩套 lib 幫的忙之外, 其它剩下的就真的沒啥好看的了... 只有一些五四三的還能拿來講一講... 底下是整個 project 的 class diagram:

![Class Diagram](http://www.chicken-house.net/files/chicken/ChickenHouse.Tools.DigitalCameraFiler.zip/CodeStructure.png)

程式主要是用到 Factory Patterns, 每種要處理的檔案類型各有一種對應的 MediaFiler 類別來負責, 之後主程式就是 recursive 找出所有的檔案, 一個一個丟給 MediaFiler 處理而以. 簡單的說明一下這幾個 class:

- class MediaFiler: 沒啥好說的, 所有的 MediaFiler 都要從這個抽像類別繼承下來. MediaFiler 會處理單一個特定格式的檔案歸檔動作.
- class CanonPairThumbMediaFiler: 一樣是抽像類別, 不過處理的檔案類型較特別, 專門處理會附帶一個縮圖檔 ( *.thm , 內容為 JPEG 格式縮圖 ) 的檔案類型.

扣掉這兩個 abstract class, 剩下就一個蘿蔔一個坑了... 來點名吧:

- JpegMediaFiler: 就是處理 *.jpg 的 MediaFiler
- CanonRawMediaFiler: 處理 *.crw (會附帶處理對應的 .thm)
- CanonVideoMediaFiler: 處理 *.avi (會附帶處理對應的 .thm)

[update: 2006/11/20]

講這麼多還丟 source code 幹嘛? 其實有個目的, 就是這工具的架構及選用的 library 其實已經有足夠的擴充能力去適應非 canon 的檔案格式了, 改版後做了一點調整, 搭配了 Attribute 來達成這目的, 舉片段的 code 當例子:

```csharp
  237     public static MediaFiler Create(string sourceFile)
  238     {
  239         FileInfo sf = new FileInfo(sourceFile);
  240         foreach (Type t in GetAvailableMediaFilers()) 
  241         {
  242             //
  243             // match
  244             //
  245             MediaFilerFileExtensionAttribute ea = GetFileExtensionAttribute(t);
  246             if (string.Compare(ea.FileExtension, sf.Extension, true) == 0)
  247             {
  248                 //
  249                 // file extension match
  250                 //
  251                 ConstructorInfo ctor = t.GetConstructor(new Type[] { typeof(string) });
  252                 return ctor.Invoke(new object[] { sourceFile }) as MediaFiler;
  253             }
  254         }
  255         return null;
  256     }
```

for loop 的部份就是列出所有已載入 AppDomain 的 Assemblies 裡所有包含的 Type, 過濾的條件是:

1. 要繼承自 class MediaFiler
2. class 要有貼上 MediaFilerFileExtensionAttribute 自訂屬性

符合這兩個條件的所有 type 就會一個一個拿來比對. 也許有人會問, 用 attrib 看起來比較強嗎? 這種典型的應用不是應該用 abstract method, 讓底下的 class 來實作就好?

是的, 如果我用 java 寫的話, 我會這麼做. 不過, polymophism 的前題就是要有 instance, 我連要用那個 class 來產生 instance 都還不曉得, 如何能享用到 polymphism 的好處? 用 static method 就沒有這種好處了, 況且 c# 語法也沒有辦法強迫衍生類別一定要 implements 某些 static method ...

這時透過 attrib 就可以很漂亮的解決這個問題, 細節就不管了, 總之我透過 custom attribute 替每個 MediaFiler 標明, 每個 MediaFiler 負責的 file extension 為何.

動態挑到適當的 MediaFiler 後, 剩下的就靠 Reflection 產生 instance, 收工.

看起來有點小題大作, 目的只有一個, 如果有新的檔案格式要支援怎麼辦? 目前的架構很簡單, 只要加上新的 MediaFiler implementation, 然後用 custom attribute 標明它負責的是那種 file extension, 其它就通通結束了, Factory Pattern 核心的部份 Create( ) 完全不用改.

優點不只如此, 還可以再做的徹底一點, 其它檔案類型的支援, 甚至不用改到原本的 code / .exe, 只要另外開 class library project, 寫在其它的 assembly, 丟在同一個目錄下執行就好了. 以往要做到 plug-ins 架構的程式非常麻煩, 現在十行左右的 code 就完成了.

最後, 要看 source code 的人可以到下面列的網址下載整個 project. 順便廣告一下我自己寫的 [zip folder http handler](/post/e4b889e5808be5a5bde794a8e79a84-ASPNET-HttpHandler.aspx) (H), 幹嘛用的? 直接把 zip 檔丟上來, 透過 http handler 加持, 就可以把 .zip 檔視為一個目錄了... 方便的很, 上面的 class diagram 其實就是藏在 zip 檔裡的圖而以... 我就不用另外再維護兩份檔案了 (一份圖檔, 一份 zip 下載檔)

Source Code (Visual Studio 2005 Project): [http://www.chicken-house.net/files/chicken/Chicken...](http://www.chicken-house.net/files/chicken/ChickenHouse.Tools.DigitalCameraFiler.zip)