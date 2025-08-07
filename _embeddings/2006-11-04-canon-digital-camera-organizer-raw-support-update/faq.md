# Canon Digital Camera 記憶卡歸檔工具 ‑ RAW Support Update

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼作者要替「Canon Digital Camera 記憶卡歸檔工具」加入 RAW 檔支援？
作者的朋友小熊子抱怨工具無法處理 Canon 的 RAW 檔 (CRW)，於是作者決定尋找解決方案並更新程式。

## Q: 要讓 DigitalCameraFiler 在 Windows XP 上讀取 Canon RAW 檔，需要先安裝什麼？
需要先安裝 Microsoft RAW Image Thumbnailer and Viewer for Windows XP。安裝後即可取得相關的 .NET Interop 組件來讀取 RAW 檔資訊。

## Q: 安裝完 Microsoft RAW Image Thumbnailer 後，哪個 .NET 組件可以用來存取 RAW 檔？
在該程式的安裝目錄內可以找到 RawManager.Interop.dll，透過它即可在 .NET (C#) 中讀取 Canon RAW 檔的內部資訊。

## Q: 使用 RawManager.Interop.dll 讀取 RAW 檔的基本程式碼長什麼樣子？
範例：
```csharp
CRawViewerClass raw = new CRawViewerClass();
raw.Load(@"c:\CRW_1234.crw");
Console.WriteLine("Camera Model: {0}", raw.CameraModel);
```
只要載入檔案即可取得像是相機型號等中繼資料。

## Q: 作者是否已找到能「編輯」RAW 檔的 API？
尚未。作者目前只挖到可以讀取資訊的 API，尚未發現可直接編輯 RAW 檔的介面。

## Q: 更新後的 DigitalCameraFiler 到哪裡下載？
可至作者提供的連結下載：DigitalCameraFilerSetup.msi (http://www.chicken-house.net/files/chicken/ChickenHouse.Tools.DigitalCameraFiler.Binary.zip)。使用前請務必先安裝 Microsoft RAW Image Thumbnailer and Viewer for Windows XP。