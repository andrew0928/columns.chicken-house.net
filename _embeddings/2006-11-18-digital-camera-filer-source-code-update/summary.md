# Digital Camera Filer ‑ Source Code (update)

## 摘要提示
- Library選用: 透過 PhotoLibrary 與 Microsoft RAW Image Viewer 兩套現成函式庫，大幅簡化 EXIF 解析與 Canon RAW/SDK 的處理。  
- Factory Pattern: 以工廠模式動態產生各種 MediaFiler，負責對應副檔名的歸檔流程。  
- 抽象層設計: 兩個核心抽象類別 MediaFiler 與 CanonPairThumbMediaFiler 定義共通行為並覆用縮圖處理邏輯。  
- 個別實作: 目前內建 JpegMediaFiler、CanonRawMediaFiler、CanonVideoMediaFiler，分別對應 JPG、CRW、AVI。  
- Attribute應用: 自訂 MediaFilerFileExtensionAttribute 標示副檔名，取代硬寫 static 方法判斷，提升維護彈性。  
- Reflection建立: 透過反射尋找符合條件的類別並動態建構實例，完全免改 Factory 核心程式碼。  
- 外掛架構: 新增格式支援時僅需另外組件並貼上 Attribute，放入同目錄即可熱插拔。  
- 專案簡潔: 真正困難的影像/RAW 處理交由第三方 library，程式主體以「剪貼＋封裝」方式完成。  
- HTTP Handler: 作者自製 ZipFolder HttpHandler，可將 zip 直接當成虛擬資料夾，方便展示與下載。  
- 原始碼開放: VS2005 專案完整釋出，鼓勵讀者自行擴充或學習 plug-in 與反射技巧。  

## 全文重點
本文介紹「Digital Camera Filer」的程式架構與最新原始碼，重點在說明如何以最少程式量完成相機檔案分類、縮圖與 RAW 支援。作者先借助 PhotoLibrary 讀取 EXIF，以及 Microsoft RAW Image Viewer 取得 Canon SDK 與 .NET 包裝，解決最棘手的兩大難題；剩餘工作只需透過工廠模式整理不同檔案格式的歸檔邏輯。核心抽象類別 MediaFiler 定義共通操作，另一個 CanonPairThumbMediaFiler 則專責處理會伴隨 .thm 縮圖檔的格式。各具體類別（Jpeg、CanonRaw、CanonVideo）「一個蘿蔔一個坑」對應副檔名，實作實際搬移與命名規則。

為了讓工具能輕鬆支援非 Canon 機種，新版加入 MediaFilerFileExtensionAttribute。程式啟動時，利用 Reflection 枚舉目前 AppDomain 內所有型別，只要同時「繼承 MediaFiler」且「貼上 Attribute」，就納入可用清單；當有檔案要處理時，Factory 便比對副檔名、動態建構實例並呼叫其方法。此做法帶來兩大好處：一、原 Factory.Create() 永遠不用修改；二、任何第三方只要寫一支 class library、標示對應副檔名，放進程式資料夾即自動生效，形同 plug-in 架構。

此外，文章還示範作者撰寫的 ZipFolder HttpHandler，能讓網站直接把 .zip 當資料夾瀏覽，如本文用來嵌入 class diagram。最後附上 VS2005 完整專案下載連結，鼓勵讀者學習 Attribute、Reflection 與 Factory Pattern 的組合威力，並依需求擴充更多影像或影音格式。

## 段落重點
### 開發所需 Library
作者最大的兩個困難──EXIF 解析與 Canon RAW 存取──分別交給 PhotoLibrary 與 Microsoft RAW Image Viewer 代勞。前者封裝 System.Drawing.Image 方便擷取 EXIF；後者內含 Canon SDK 及 .NET Wrapper，可直接解碼 CRW/THM 和讀取 RAW 標頭。省去底層影像處理後，開發者只需關注檔案分類與搬移邏輯。

### 程式架構與 Class Diagram
整個專案的骨幹為 Factory Pattern。主程式以遞迴遍歷目錄，遇到檔案時交由 Factory.Create() 取得對應的 MediaFiler；MediaFiler 再依檔名、拍攝日期、縮圖等資訊決定輸出路徑。兩個抽象類別扮演模板角色：MediaFiler 定義最小化接口；CanonPairThumbMediaFiler 額外處理會攜帶 .thm 縮圖的格式，避免重複碼。Class Diagram 顯示各類別間簡潔的繼承與組合作用。

### MediaFiler 具體實作
目前內建三支實作者：JpegMediaFiler 處理 .jpg；CanonRawMediaFiler 處理 .crw，並同時搬移對應 .thm；CanonVideoMediaFiler 處理 .avi，也需同步 .thm。每支類別實作抽象方法，負責擷取拍攝日期、產生目標資料夾、並確保檔案與縮圖一起被搬移。設計上「一格式一類別」使維護與測試都單純。

### Attribute 與 Reflection 的擴充機制
新版透過 MediaFilerFileExtensionAttribute 標示「我負責的副檔名」。Factory 在啟動時枚舉所有 Assembly 裡的型別，篩選出「繼承 MediaFiler 且貼 Attribute」的類別，再比對副檔名決定使用哪個實例。這種做法解決了「尚未知道要建哪個 instance 時就想用多型」的典型困境，並避免 C# 無法強迫實作 static method 的侷限。

### Plug-in 架構與未來擴充
由於選用 Attribute+Reflection，只要另外另開一個 class library 專案，實作新的 MediaFiler、貼上屬性、編譯後放到主程式目錄，就能即插即用，無須重編主程式。對影像軟體常遇到的「支援新機種、新影音格式」需求而言，這種 Plug-in 式部署尤為便利；同時也示範了在 .NET 中打造輕量外掛機制的最佳實踐。

### 原始碼下載與 ZipFolder HttpHandler
文章最後提供 VS2005 完整專案下載連結，讀者可直接參考、改寫或新增 MediaFiler 實作。同時作者也自推 ZipFolder HttpHandler，可讓網站將 .zip 視為虛擬資料夾瀏覽；本文的 Class Diagram 就是透過此 Handler 從壓縮檔即時讀取。整體而言，Digital Camera Filer 展示了「善用第三方函式庫＋清晰架構＋ Attribute/Reflection 擴充」的高效開發思維。