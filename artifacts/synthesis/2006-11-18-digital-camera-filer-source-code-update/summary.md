# Digital Camera Filer - Source Code (update)

## 摘要提示
- 第三方函式庫整合: 以 PhotoLibrary 與 Microsoft RAW Image Viewer 解決 EXIF 讀取與 Canon RAW 支援
- Factory Pattern: 以工廠模式動態指派不同檔案類型對應的處理器 MediaFiler
- 抽象類別設計: 以 MediaFiler 與 CanonPairThumbMediaFiler 作為擴充基底
- 檔案格式支援: 內建處理 JPEG、Canon RAW (.crw)、Canon 影片 (.avi) 及其 .thm 縮圖
- Attribute 註記機制: 以自訂屬性標記檔案副檔名，搭配反射建立對應處理器
- 反射建立實例: 以反射掃描 AppDomain 的可用型別並動態建構 MediaFiler 實例
- 靜態方法與多型限制: 說明 C# 無法強制衍生類別實作靜態方法，改以 Attribute 解法
- 外掛式擴充: 新增格式支援可獨立於原程式，以 class library 丟同目錄即插即用
- 維護成本降低: 核心 Create() 不變，新增格式只需新增實作與標記即可
- 原始碼下載與 Zip Handler: 提供 VS2005 專案下載，並介紹自製 Zip Folder HttpHandler 的應用

## 全文重點
本文介紹一個以 .NET 開發的數位相機檔案歸檔工具「Digital Camera Filer」，其核心思路是用最小成本組裝出可維護、可擴充且能處理多媒體檔案類型的架構。作者先以兩個現成的第三方函式庫解決最麻煩的部分：PhotoLibrary 封裝 System.Drawing.Image，讓讀取 EXIF 等影像中繼資料更便利；Microsoft RAW Image Viewer 則提供 Canon SDK 與 .NET 包裝，讓工具能處理 Canon RAW 格式。藉由這兩者，剩餘工作便以「剪貼與組裝」的方式完成。

架構上採用 Factory Pattern，每一種檔案類型對應一個 MediaFiler 類別，主程式會遞迴掃描資料夾內所有檔案，逐一交給適當的 MediaFiler 處理。MediaFiler 是抽象基底類別，負責定義單一檔案的歸檔行為；CanonPairThumbMediaFiler 亦為抽象基底，但專處理會伴隨 .thm 縮圖（JPEG 格式）的檔案類型。實作面目前包含 JpegMediaFiler（*.jpg）、CanonRawMediaFiler（*.crw，同時處理對應 .thm）、CanonVideoMediaFiler（*.avi，同時處理對應 .thm）。

文章在 2006/11/20 的更新重點，是引入 Attribute 與反射以提升擴充性。既然 C# 無法強迫衍生類別實作靜態方法，且在尚未知道具體型別前也無法仰賴多型，作者改以自訂屬性 MediaFilerFileExtensionAttribute 為每個 MediaFiler 標記事先負責的副檔名。工廠方法在執行時掃描已載入 AppDomain 內所有型別，篩選出繼承 MediaFiler 且貼有該屬性的類別，再比對副檔名，最後用反射呼叫建構子產生對應實例。這個流程讓 Create() 的核心邏輯在新增格式支援時完全不需修改。

如此一來，擴充新檔案格式相當容易：僅需新增一個 MediaFiler 實作並加上對應副檔名的 Attribute，無須動到既有程式碼。更進一步地，這些新實作可以放在獨立的 class library（另一個 assembly），只要投放至同一執行目錄，即可在執行階段被發現與使用，形成簡潔的外掛式架構。文章最後附上完整 Visual Studio 2005 專案下載連結，並順帶介紹作者自製的 Zip Folder HttpHandler：可讓網站直接把 .zip 當作資料夾瀏覽，藉此省去同時維護「圖檔」與「壓縮包」兩份檔案的麻煩。

整體來說，本文重點不在複雜演算法，而在於以簡單的設計模式、反射與自訂屬性，建立一個低耦合、高擴充、易於維護與部署的檔案歸檔工具框架。對於需要處理多媒體檔案、面臨不斷新增格式或希望以外掛方式擴充功能的 .NET 專案，這套方法具實務參考價值。

## 段落重點
### 工具概述與開發資源
作者說明本工具的開發策略：把困難點交由成熟函式庫處理，其餘以輕量組裝完成。選用 PhotoLibrary 以簡化 EXIF 與影像資訊存取；同時採用 Microsoft RAW Image Viewer 提供的 Canon SDK 與 .NET 包裝層，以支援 Canon RAW。透過這兩者，工具能快速具備處理常見影像與 RAW 的能力，開發者只需專注在檔案分類與歸檔流程的搭建與自動化。

### 類別結構與 Factory Pattern
程式核心是 Factory Pattern：為每種檔案類型提供一個 MediaFiler 實作，主程式遞迴遍歷目錄，將檔案交由對應 MediaFiler 處理。MediaFiler 為抽象類別，定義單檔案歸檔行為；CanonPairThumbMediaFiler 為處理會附帶 .thm 縮圖的特殊基底。這種一個蘿蔔一個坑的對應方式，讓主流程極為單純且清晰，類別責任單一，便於測試與維護。

### 內建檔案處理器實作
目前提供三種實作：JpegMediaFiler 處理 *.jpg；CanonRawMediaFiler 處理 *.crw，並同時處理其配對的 .thm 縮圖；CanonVideoMediaFiler 處理 *.avi，同步處理對應的 .thm。藉由抽象類別分工，縮圖處理等共通邏輯可在 CanonPairThumbMediaFiler 聚合，減少重複碼。此設計能快速擴大支援面，並在不干擾其他格式的前提下，針對個別格式優化流程。

### 以 Attribute 與反射動態綁定處理器
更新版引入自訂屬性 MediaFilerFileExtensionAttribute，將「副檔名對應哪個 MediaFiler」這項知識移到類別宣告層。工廠方法會掃描 AppDomain 內所有型別，篩選出「繼承 MediaFiler 且具有該屬性」的類別，當檔案副檔名符合屬性設定時，便以反射呼叫建構子建立實例。此路徑迴避了 C# 無法強制實作靜態方法、以及在未定型別前無法運用多型的限制，讓動態綁定更直觀且鬆耦合。

### 擴充性與外掛式架構
得益於 Attribute 驅動與反射建構，新增格式支援只需新增一個 MediaFiler 實作並標記屬性，核心 Create() 無須修改。更可將新實作編譯成獨立 assembly，與主程式放同一資料夾即可自動載入，達成外掛式（plug-in）擴充。相較傳統外掛框架的繁瑣，此法只需十餘行核心掃描/比對/建構的程式碼，即能完成可維護且可部署的延展模型，降低風險並縮短發佈迭代。

### 原始碼下載與 Zip Handler 應用
作者提供完整 Visual Studio 2005 專案下載連結，並介紹自製的 Zip Folder HttpHandler：可讓網站將 .zip 視為目錄直接存取，方便將資源（如類別圖）嵌在壓縮檔中而免去重複維護多份檔案。這種部署方式對於分享示意圖與完整原始碼包特別實用，有助於同步更新與一致性管理，強化專案的可傳遞性與可重現性。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - C#/.NET 基礎語法與專案結構（Class Library、Assembly）
   - 物件導向設計（抽象類別、繼承、介面/多型概念）
   - 設計模式：Factory Pattern
   - .NET 反射（Reflection）、AppDomain 與組件載入
   - Custom Attribute 的設計與使用
   - 影像檔與相機格式知識（JPEG/EXIF、Canon RAW .crw、.thm 縮圖配對）
2. 核心概念：
   - MediaFiler 階層架構：以抽象類別定義檔案歸檔行為，具體類別各司其職
   - Attribute 驅動的型別配對：以 MediaFilerFileExtensionAttribute 標註支援的副檔名
   - 反射與動態實例化：掃描已載入的 Assemblies，找出合規型別並呼叫建構式建立實例
   - Factory Pattern 的無侵入擴充：Create() 不需修改即可支援新格式
   - 特殊格式處理：.thm（JPEG 縮圖）與原檔（例如 .crw、.avi）的成對處理
3. 技術依賴：
   - PhotoLibrary：封裝 System.Drawing.Image 以讀取 EXIF 資訊
   - Microsoft RAW Image Viewer：提供 Canon SDK 與 .NET 包裝（處理 Canon RAW）
   - 專案本身依賴上述兩套 Library；應用層依賴 MediaFiler 抽象層，具體格式依賴對應的實作
   - Attribute 與 Reflection 依賴 .NET 類型系統與 AppDomain 掃描
4. 應用場景：
   - 數位相機影像與影片的自動歸檔（依檔名/日期/EXIF 等）
   - 跨多格式相機檔案支援（JPEG、Canon RAW、含 .thm 的影片）
   - 以外掛形式擴充新檔案格式的支援（無需重編譯主程式）
   - 圖像後處理流程的前置整理（統一命名與目錄結構）
   - 下載站點以 HTTP Handler 提供 zip 內容瀏覽（輔助發佈；非核心）

### 學習路徑建議
1. 入門者路徑：
   - 熟悉 C# 類別、抽象類別、繼承與基本集合操作
   - 實作最簡單的 JpegMediaFiler：讀檔、取 EXIF、輸出到指定目錄
   - 練習基本 Factory：以副檔名 switch 建立對應類別（先不使用 Attribute）
2. 進階者路徑：
   - 學習 Reflection 與 Custom Attribute 的定義與讀取
   - 將 Factory 重構為：掃描 Assemblies → 過濾繼承 MediaFiler 且具標註 → 動態建構
   - 實作 CanonPairThumbMediaFiler 抽象層，處理主檔與 .thm 縮圖的成對規則
   - 導入第三方 Library：PhotoLibrary 讀 EXIF、Microsoft RAW Image Viewer 處理 .crw
3. 實戰路徑：
   - 以獨立 Class Library 撰寫新格式 MediaFiler（例如 .nef、.mp4）
   - 以 Attribute 標註副檔名，部署到同目錄作為外掛，驗證無需改動主程式即可運作
   - 補上日誌、錯誤處理與單元測試（Mock 檔案系統、測試多組件載入）
   - 規劃目錄/命名策略（依日期/攝影機型號/EXIF 場景），並批次跑資料夾

### 關鍵要點清單
- MediaFiler 抽象類別: 定義單一檔案格式的歸檔行為，是所有實作的共同基底 (優先級: 高)
- CanonPairThumbMediaFiler: 抽象層處理主檔與 .thm 縮圖成對邏輯（例如 .crw/.avi 搭配 .thm） (優先級: 高)
- JpegMediaFiler: 針對 .jpg 的具體實作，示範最基本流程與 EXIF 使用 (優先級: 中)
- CanonRawMediaFiler: 針對 .crw 的實作，結合 Canon SDK/.NET Wrapper 處理 RAW (優先級: 中)
- CanonVideoMediaFiler: 針對 .avi 的實作，處理與 .thm 的配對與搬移 (優先級: 中)
- Factory Pattern 核心 Create(): 以檔案副檔名選擇合適 MediaFiler 的工廠方法 (優先級: 高)
- Custom Attribute（MediaFilerFileExtensionAttribute）: 將副檔名能力以標註宣告，支援動態發現 (優先級: 高)
- Reflection 與動態實例化: 以 Type/GetConstructor/Invoke 於執行時建立實體 (優先級: 高)
- AppDomain 組件掃描: 從已載入 Assemblies 枚舉 Type，過濾繼承與標註以定位候選類別 (優先級: 高)
- 無侵入式擴充: 新增檔案格式只需新增實作類別與標註，無需修改工廠方法 (優先級: 高)
- 外掛式部署: 將新格式支援封裝為獨立 Assembly，置於同目錄即可被發現 (優先級: 中)
- EXIF 讀取與運用: 透過 PhotoLibrary/System.Drawing.Image 取得拍攝資訊作為歸檔依據 (優先級: 中)
- Microsoft RAW Image Viewer/Canon SDK: 提供 RAW 處理能力與 .NET 包裝 (優先級: 中)
- 檔案遞迴掃描流程: 主程式遞迴收集檔案並交由對應 MediaFiler 處理 (優先級: 中)
- 錯誤處理與日誌: 對動態載入、反射與 I/O 操作的例外加強可維運性 (優先級: 中)