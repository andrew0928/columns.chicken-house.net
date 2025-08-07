# Digital Camera Filer - Source Code (update)

# 問答集 (FAQ, frequently asked questions and answers)

## Q: Digital Camera Filer 這個工具的主要功能是什麼？
它是一個用來將數位相機拍攝的各種媒體檔案（JPEG、Canon RAW、AVI…）依檔案類型自動歸檔、搬移與重新命名的小工具。

## Q: 開發過程中最麻煩的兩個部分，作者是靠哪兩套現成的 Library 解決的？
1. PhotoLibrary：封裝 `System.Drawing.Image`，方便讀取 EXIF 等資訊。  
2. Microsoft RAW Image Viewer：內含 Canon SDK 及 .NET wrapper，負責讀取 Canon RAW 檔。

## Q: 專案中用來處理不同副檔名的核心設計模式是什麼？
Factory Pattern。程式會依檔案副檔名動態產生對應的 `MediaFiler` 子類別來進行歸檔。

## Q: MediaFiler 類別階層大致包含哪些抽象類別與實作類別？
抽象類別：  
• `MediaFiler`  
• `CanonPairThumbMediaFiler`（專處理會附帶 *.thm 縮圖的檔案）  

實作類別：  
• `JpegMediaFiler`（*.jpg）  
• `CanonRawMediaFiler`（*.crw + *.thm）  
• `CanonVideoMediaFiler`（*.avi + *.thm）

## Q: `MediaFilerFactory.Create(string sourceFile)` 方法如何決定要回傳哪個 MediaFiler 實例？
它會：
1. 列舉目前 AppDomain 內所有已載入的 Assemblies 與 Type。  
2. 過濾出「繼承自 `MediaFiler`」且「貼有 `MediaFilerFileExtensionAttribute`」的類別。  
3. 比對屬性中宣告的副檔名與實際檔案副檔名；相符就用 Reflection 呼叫該類別的建構子，動態產生實例並回傳。

## Q: 作者為什麼不用抽象方法或傳統多型，而改用自訂 Attribute 標示副檔名？
因為在決定「要建立哪一個子類別的實例」之前，根本還沒有任何物件可以套用多型。C# 也無法強迫衍生類別一定要實作某些 static 方法；使用自訂 Attribute 就能在「尚未有實例」的情況下，透過型別資訊把副檔名與類別做靜態對應，再利用 Reflection 建立物件。

## Q: 如果日後要支援新的檔案格式，需要怎麼做？
只要：
1. 新增一個繼承自 `MediaFiler` 的類別實作。  
2. 在該類別上貼 `MediaFilerFileExtensionAttribute`，標明它負責的副檔名。  
3. (選擇性) 另外建立一個 Class Library，編譯成新的 Assembly，與原執行檔放在同一資料夾即可。  
原有 Factory 的 `Create()` 方法完全不需修改。

## Q: 這種 Attribute + Reflection 的做法還帶來了哪些優點？
它讓程式自然形成 Plug-in 架構：後續支援其他檔案類型不必重新編譯主程式，只要把新的 Assembly 丟到同一目錄即可，擴充性與維護性大幅提升。

## Q: 想看完整 Source Code 要到哪裡下載？
可至以下網址下載 Visual Studio 2005 專案：  
http://www.chicken-house.net/files/chicken/ChickenHouse.Tools.DigitalCameraFiler.zip

## Q: 文章中提到的「zip folder HttpHandler」有什麼用途？
作者實做的 HttpHandler 能把伺服器上的 .zip 檔視為資料夾存取，例如直接從壓縮檔內取出並顯示圖片，方便同時提供「下載 zip」與「線上瀏覽內容」而不需維護兩份檔案。