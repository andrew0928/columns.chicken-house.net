# Canon Digital Camera 記憶卡歸檔工具 - RAW Support Update

## 摘要提示
- 需求提出: 工具原本不支援 Canon RAW 檔，小熊子提出改進建議。
- 資源匱乏: 市面上可用的 Canon RAW 開放原始碼專案與 SDK 皆不成熟或僅支援 C++。
- 微軟套件: Microsoft RAW Image Thumbnailer and Viewer for Windows XP 意外成為突破口。
- 反組譯發現: 在安裝目錄找到 RawManager.Interop.dll，可直接用 .NET 呼叫。
- 簡易呼叫: 只需三行 C# 程式碼即可載入 RAW，讀取相機型號等資訊。
- SDK 角色: Interop DLL 背後仍呼叫 Canon Digital Camera SDK，但封裝成 .NET 更易用。
- 功能限制: 目前僅讀取基本資訊，尚未找到可編輯 RAW 的 API。
- 需求滿足: 對歸檔工具而言，只要能抓時間與基本 EXIF 就足夠。
- 更新發布: 提供新版 DigitalCameraFiler 安裝檔，並附上微軟檢視器下載連結。
- 後續計畫: 未來視需求再研究 RAW 編輯與自動轉正功能。

## 全文重點
作者原本開發的「Canon Digital Camera 記憶卡歸檔工具」僅處理 JPEG 檔，小熊子提出希望能支援 RAW（.crw、.cr2）格式。作者調查後發現，公開可用的 Canon RAW 函式庫選擇極少：開源專案不穩定；Canon 官方 Digital Camera SDK 雖免費，但僅有 C++ 介面，而作者多年未觸碰 C++，導致導入成本過高。

在搜尋過程中，作者注意到微軟針對 Windows XP 提供的「Microsoft RAW Image Thumbnailer and Viewer」，裝完後可在總管直接預覽各家 RAW。推測此工具內部應含有 .NET 元件，作者遂以反組譯方式檢視安裝目錄，果然發現 RawManager.Interop.dll。此 DLL 封裝了 Canon RAW 的讀取邏輯，只需在程式碼中建立 CRawViewerClass 物件並呼叫 Load，就能即時取得 CameraModel、拍攝時間等 EXIF 資訊。

如此一來，作者便能維持既有 C# 架構，不必重新撰寫 C++，快速替歸檔工具加入 RAW 處理功能。雖然目前尚未找到修改 RAW 或自動轉正（rotate）的 API，但對單純「依拍攝日期整理檔案」的需求已足夠。文章最後提供新版安裝檔與微軟檢視器下載網址，提醒使用者須先安裝檢視器以取得 DLL 依賴，才可正常使用更新後的歸檔工具。未來作者將視需求深入研究 RAW 編輯可能性。

## 段落重點
### 改版需求與窘境
作者收到好友小熊子的回饋，指出記憶卡歸檔工具缺乏 RAW 支援；作者調查後發現只有零星的開源方案與 Canon C++ SDK，且後者需額外申請，學習曲線高，短期難以整合。  

### 微軟檢視器成為轉機
在持續搜尋期間，作者注意到「Microsoft RAW Image Thumbnailer and Viewer」能於 Windows XP 預覽 CRW 檔，且安裝時需要 .NET Framework，因而推測內含可重複利用的 .NET 元件。  

### 反組譯尋寶與實作
安裝檢視器後，作者於目錄內找到 RawManager.Interop.dll，透過反組譯確認介面簡潔，並以三行 C# 程式碼驗證可成功載入 RAW 並讀取相機型號。背後實際仍是 Canon SDK，但經 Interop 封裝後可直接在 .NET 呼叫，省去 C++ 麻煩。  

### 功能限制與未來方向
目前 DLL 僅暴露讀取、縮圖等基礎能力，尚無編輯 RAW 或自動旋轉等進階 API。不過歸檔工具僅需讀取拍攝時間即可完成分類，小熊子也認為已經「夠用」。作者計畫後續再研究進階功能。  

### 更新發布與使用指引
文章最後附上新版 DigitalCameraFiler 安裝檔連結，提醒使用者須先安裝 Microsoft RAW Image Thumbnailer and Viewer 以獲得必要的 Interop DLL。透過此方式，原工具即可在 Windows XP 上支援 Canon RAW 檔案的拍攝日期與相機資訊擷取功能。