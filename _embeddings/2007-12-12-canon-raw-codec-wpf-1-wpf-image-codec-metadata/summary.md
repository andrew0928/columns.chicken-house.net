# Canon Raw Codec + WPF #1, WPF Image Codec, Metadata

## 摘要提示
- 動機與背景: 因 Canon G9 重啟 RAW 支援並有官方 Raw Codec，作者以 WPF 建立自動化影像歸檔流程。
- WPF 與 GDI+ 差異: WPF 以影像來源+Transform+Layer 的思維處理圖像，與 GDI/GDI+ 的小畫家式流程不同。
- HD Photo 意涵: 微軟新格式強調廣色域與高動態，搭配 Codec 可避免從 RAW 轉 JPEG 的資訊折損。
- 基本轉檔流程: 以 BitmapDecoder 讀 CR2、TransformedBitmap 縮放、JpegBitmapEncoder 輸出 JPEG。
- EXIF 保留問題: 直接轉檔不帶 EXIF，需額外處理 metadata 以保留相片隱藏資訊。
- WPF Metadata 模型: 以類 XPath 的 Metadata Query 透過 GetQuery/SetQuery 抽象化各格式的讀寫。
- Canon RAW 與 JPEG 對應: RAW 的 metadata query 與 JPEG EXIF 不一致，需要自行建立對應表。
- 對應表建立方法: 以多張樣本比對、試誤推測，彙整成 XML，內嵌於自製 library 供轉檔套用。
- 實作成果: 封裝成 ImageUtil.SaveToJPEG，可指定長寬與壓縮品質並保留 EXIF。
- 下一步議題: 基本功能完成但效能仍待優化，預告後續文章探討。

## 全文重點
作者因購入 Canon G9 並看重 RAW 支援，著手以 WPF 及 Canon 提供的 RAW Codec 建立影像歸檔與批次縮圖流程。其核心動機在於：JPEG 規格老舊且有損壓縮，未來勢將被新格式取代，而保留 RAW 能確保後續能以較新標準重新輸出，避免資訊折損。微軟同時推出 HD Photo（後來演變為 JPEG XR），宣稱具備廣色域、動態範圍等優勢；若以官方 Codec 直接由 RAW 解碼至新格式或中間處理，理論上能最大化保留原始資訊，相較從 JPEG 再處理更具意義。

技術面上，WPF 與 GDI/GDI+ 有本質差異：WPF 將圖像視為資料來源，經由多層 Transform 與合成（類似 Photoshop 的圖層）得到最終影像。作者的首要任務是以 WPF 的 Imaging API 完成「讀 RAW、縮放、輸出 JPEG」。透過 BitmapDecoder 讀取 CR2、配合 TransformedBitmap 進行 ScaleTransform，再以 JpegBitmapEncoder 輸出即可，程式碼精簡，但思維模式已不同於以往 GDI+ 的寫法。

接續挑戰在 metadata。單純轉檔不會自動帶出 EXIF，對重視拍攝資訊的作者而言難以接受。雖然 WPF 已將 metadata 操作抽象化，提供近似 XPath 的查詢語法與 GetQuery/SetQuery，但實務上 Canon RAW（CR2）的 metadata query 與 JPEG EXIF 的路徑與結構並不一致，導致無法直接對映。作者遂以比對不同格式的樣本檔，試誤建立 query 對應表（如 /ifd/{ushort=256} 對映 /app1/ifd/exif/{ushort=256} 等），雖未完全弄清規範細節（IFD、EXIF、XMP 等標準與欄位意義），但以可用為原則，彙整成 XML，內嵌於自製 library 中。

完成後，作者將流程封裝為 ImageUtil.SaveToJPEG(API: 輸入 RAW 路徑、輸出 JPEG 路徑、最大寬高、品質)，可同時執行縮圖與 EXIF 搬運，滿足日常歸檔需求。文章最後指出已達成「可用」階段，但在大量處理或後續擴充時，效能問題浮現，準備於下一篇深入探討最佳化策略。

## 段落重點
### 為何選擇 RAW 與 WPF：動機、目標與環境
作者購入 Canon G9 的關鍵因素之一是 RAW 支援與官方 RAW Codec 的推出。考量到 JPEG 為老舊規格、長期保存與再利用價值有限，保留 RAW 能確保未來轉向新格式（如 HD Photo/JPEG XR）時維持最高品質。WPF 作為新一代圖形框架，配合 Canon 的 Codec，能在轉檔、縮圖與後續資料保留上提供更好的技術基礎。目標是打造一個自動化、可重複的影像歸檔與縮圖流程，兼顧品質與資訊完整性。

### WPF Imaging 與 GDI+ 的思維差異與基本轉檔實作
WPF 以資料驅動與組合式渲染為核心：影像是來源，經 Transform 與層層處理後產生輸出，與傳統 GDI/GDI+ 的逐步繪製流程不同。作者以簡潔範例展示：BitmapDecoder 讀取 CR2，TransformedBitmap 進行縮放，JpegBitmapEncoder 設定品質與輸出，迅速完成 RAW→JPEG 的基本流程。這種 API 設計鼓勵以管線化方式組裝處理步驟，便於日後擴充更多影像效果或轉檔選項。

### Metadata/EXIF 的落差與 WPF 的抽象化存取
直接轉檔不會帶出 EXIF，導致拍攝資訊流失。WPF 的影像 Metadata 存取已抽象化，透過類 XPath 的 Query（GetQuery/SetQuery）統一讀寫不同格式的 metadata。然而實務上 CR2 與 JPEG 的 metadata 結構、命名空間與路徑不同，無法直接搬移。作者面臨的挑戰在於：如何從 Canon RAW 的 IFD/EXIF 結構，可靠對應到 JPEG 的 APP1/IFD/EXIF 路徑，並保證欄位正確性與完整性。

### 建立 Canon RAW 與 JPEG EXIF 的 Query 對應表
作者採用多檔比對與試誤法，逐步推得常用欄位的對應關係（例如 /ifd/{ushort=256} 對應 /app1/ifd/exif/{ushort=256} 等），雖未完全吃透 W3C 與相關規範（EXIF、XMP、IFD 的細節），但以「可用且可驗證」為原則整理出一份對照表。最終將對照表輸出為 XML 並作為 embedded resource 置入 library，以程式在轉檔時讀取並套用，實現自動化的 metadata 映射與寫入。

### 封裝為可重用的 Library 並預告效能議題
完成轉檔與 EXIF 搬運後，作者封裝為 ImageUtil.SaveToJPEG，提供輸入輸出路徑、最大邊長與 JPEG 品質等參數，一行呼叫完成 RAW→JPEG 縮圖與資訊保留，滿足日常批次處理與歸檔需求。雖然功能達標，但在大量檔案與更複雜處理情境中，效能成為下一個瓶頸。作者預告將於下一篇深入探討效能最佳化的手法與實作考量。

## 資訊整理

### 知識架構圖
1. 前置知識：學習本主題前需要掌握什麼？
- .NET 與 C# 基礎（檔案 I/O、例外處理、物件導向）
- WPF 影像處理基本觀念（ImageSource、BitmapSource、Transform）
- 影像格式與編碼概念（RAW、JPEG、HD Photo/JPEG XR）
- EXIF/IFD/XMP 等常見影像中繼資料規格的基本認識
- 作業系統影像編解碼器（Codec）的角色與安裝

2. 核心概念：本文的 3-5 個核心概念及其關係
- WPF 影像管線：以 BitmapDecoder/BitmapEncoder 為核心，透過 Frames 與 TransformedBitmap 完成讀取、縮放、輸出。
- 外部 Codec 的依賴：Canon RAW Codec 供 WPF 解出 CR2，WPF 再以統一 API 操作。
- 中繼資料抽象化：WPF 以 Metadata Query（類 XPath）統一讀寫各格式中繼資料。
- 格式間中繼資料對應：RAW（Canon/IFD）到 JPEG（APP1/EXIF）的欄位映射需要建立對照表。
- 保真與未來相容：保留 RAW 便於未來轉換到新格式；HD Photo 提供更寬色域與新特性，透過正確 Codec 可避免資訊折損。

3. 技術依賴：相關技術之間的依賴關係
- Canon RAW 檔（CR2）解碼 → 依賴 Canon RAW Codec
- WPF System.Windows.Media.Imaging → 依賴 .NET/WPF Runtime 與可用的影像 Codec
- 中繼資料存取 → 依賴 WPF 的 Metadata Query API 與正確的 Query Path
- 影像轉檔/縮放 → 依賴 BitmapDecoder（讀）+ TransformedBitmap（縮放）+ 對應 Encoder（寫入 JPEG/HD Photo）
- 中繼資料跨格式搬運 → 依賴自建的對照表（RAW IFD → JPEG EXIF APP1）

4. 應用場景：適用於哪些實際場景？
- 相片歸檔流程自動化：RAW 轉檔為 JPEG 並保留/轉寫 EXIF
- 批次縮圖工具：大量影像的長邊縮放與壓縮品質控制
- 作品集輸出：以一致的色域與品質設定輸出網用或列印用檔案
- 影像管理系統：讀取/維持中繼資料，未來可延伸至搜尋、分類、標註
- 格式升級過渡：從舊格式（JPEG）過度到新格式（如 HDR/寬色域），以 RAW 為來源避免損失

### 學習路徑建議
1. 入門者路徑：零基礎如何開始？
- 安裝 .NET SDK 與熟悉 C# 基本語法與檔案操作
- 建立 WPF 專案，練習以 BitmapDecoder 讀取一般 JPEG/PNG
- 理解 BitmapFrame、TransformedBitmap，實作基本縮放與另存
- 了解 EXIF 是什麼，使用現成工具檢視 EXIF（如 ExifTool）建立直覺

2. 進階者路徑：已有基礎如何深化？
- 安裝 Canon RAW Codec，嘗試讀取 CR2 並以 WPF 流水線轉存為 JPEG
- 使用 Metadata Query（GetQuery/SetQuery）讀寫 EXIF 欄位
- 研究 RAW IFD 與 JPEG EXIF 的 Query Path 差異，建立欄位對照表
- 比較 JPEG 與 HD Photo（JPEG XR）輸出差異（色域、檔案大小、品質）
- 把功能封裝成 Library（ImageUtil），設計 API 與錯誤處理

3. 實戰路徑：如何應用到實際專案？
- 規劃批次轉檔器：輸入資料夾 → 解析 RAW → 轉存 JPEG → 搬運 EXIF
- 將對照表外部化為 XML/JSON 並嵌入為資源，支援維護與更新
- 增加命令列或 GUI 參數：長邊尺寸、品質、輸出格式、是否保留縮圖
- 實作日誌與例外重試，確保大量檔案處理穩定
- 度量效能（I/O、解碼、縮放、編碼、Meta 搬運）並針對瓶頸優化（多執行緒、快取）

### 關鍵要點清單
- WPF BitmapDecoder/Encoder：WPF 以解碼器/編碼器模型統一處理影像讀寫。（優先級: 高）
- TransformedBitmap 縮放：以 Transform（如 ScaleTransform）在管線中執行縮放。（優先級: 高）
- Canon RAW Codec 依賴：讀 CR2 需安裝對應 Codec，否則無法解碼。（優先級: 高）
- Metadata Query 模型：以類 XPath 的 Query Path 讀寫中繼資料（GetQuery/SetQuery）。（優先級: 高）
- RAW 與 JPEG EXIF 對應：不同格式的 Query Path 不同，需建立對照表才能搬運資料。（優先級: 高）
- EXIF/IFD/XMP 基礎：理解常見中繼資料區塊與儲存位置，便於 Mapping。（優先級: 中）
- HD Photo（JPEG XR）特性：更大色域等新功能，配合 Codec 可避免資訊折損。（優先級: 中）
- 編碼參數控制：JpegBitmapEncoder.QualityLevel 影響檔案大小與品質。（優先級: 中）
- 縮圖與縮圖快取：合理使用 Thumbnail 與快取策略，提升轉檔效率。（優先級: 中）
- 錯誤處理與相容性：不同相機/檔案可能有差異，需加強異常與回退機制。（優先級: 高）
- 封裝成 Library：以 API（如 ImageUtil.SaveToJPEG）對外提供簡潔使用介面。（優先級: 中）
- 對照表外部化：將欄位 Mapping 存為 XML/資源，便於維護與擴充。（優先級: 中）
- 批次處理與自動化：以工具化方式簡化歸檔與轉檔的例行工作。（優先級: 高）
- 效能與多執行緒：大量影像處理需考慮 I/O 併發與 CPU 利用率（預告下一步需優化）。（優先級: 中）
- 未來相容策略：保留 RAW 作為母檔，便於將來轉換到新通用格式。（優先級: 中）