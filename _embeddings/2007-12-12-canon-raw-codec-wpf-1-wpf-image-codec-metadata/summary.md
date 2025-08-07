# Canon Raw Codec + WPF #1, WPF Image Codec, Metadata

## 摘要提示
- RAW 支援: 為避免 JPEG 老化與資訊折損，作者視 RAW 為長期保存相片的必要條件。  
- Canon RAW Codec: Canon 釋出的官方 WPF Codec 成為研究 Canon G9 RAW 檔的切入點。  
- WPF 影像管線: WPF 以物件＋Transform 為核心，與傳統 GDI/GDI+ 迥異。  
- HD Photo: 微軟新格式提供廣色域等優勢，可完整承接 RAW 內含資訊。  
- 影像縮放轉檔: 範例程式展示將 CR2 依比例縮小並輸出 JPEG 的最小程式碼。  
- EXIF Metadata: 轉檔若遺失 EXIF 令人難以接受，成為後續必解課題。  
- Metadata Query 機制: WPF 以類 XPath 語法讀寫 metadata，但各格式標籤並不對應。  
- 標籤對照表: 作者比對 Canon RAW 與 JPEG EXIF，手工建立映射表並生成 XML。  
- Library 封裝: 對照表與轉檔流程被包成 ImageUtil，可一行指令完成轉檔＋EXIF 搬移。  
- 效能瓶頸: 功能已通，接下來的重點將是轉檔效能優化。  

## 全文重點
作者因購入支援 RAW 的 Canon G9，決定徹底研究 Windows Presentation Foundation（WPF）在影像處理上的可能性。Canon 同步推出的 RAW Codec 讓 WPF 能直接解碼 CR2，這與長期保存需求不謀而合：JPEG 規格老舊且有壓縮損失，而 RAW 保留所有原始資訊，未來即使影像格式汰舊換新，仍可轉出最佳品質。  
研究過程中作者注意到微軟正力推的新格式 HD Photo （後改名為 JPEG XR）。相較 JPEG，HD Photo 擁有更廣色域與更多影像細節；若先由 RAW 讀出完整資訊再存成 HD Photo 或其他新格式，便能避免中途轉檔損失。  

實作層面，作者首先以 WPF 的 BitmapDecoder 讀入 CR2，再以 JpegBitmapEncoder 壓縮輸出，並透過 TransformedBitmap 進行縮圖。與傳統 GDI+ 相比，WPF 更像是「影像物件組合＋層層 Transform」的概念，思考模式完全不同。  
圖像本體處理解決後，下一個難題是 EXIF。直接轉成 JPEG 時 metadata 全數遺失，於是作者深入 System.Windows.Media.Imaging 的 Metadata Query 機制。WPF 把各格式 metadata 抽象化，透過類 XPath 字串（/ifd/{ushort=…}）定位標籤，再以 GetQuery／SetQuery 讀寫。然而 Canon RAW 的節點路徑與 JPEG EXIF 並不一致，導致對照困難。作者只好對照實際檔案，摸索出一份「RAW → JPEG」的標籤映射表，並以程式掃描產生 XML，最後封裝成 ImageUtil 函式庫。使用者只需呼叫  
ImageUtil.SaveToJPEG(src, dst, w, h, quality)  
即可一次完成縮圖、轉檔與 EXIF 搬移。  
當前基礎功能已齊備，但處理大量 RAW 時的效率仍令人擔憂；性能優化將是下一篇文章的主題。  

## 段落重點
### 換機動機與 RAW 支援必要性
作者原本就打算換機，G9 重新支援 RAW 且 Canon 官方發表 WPF Codec，遂成購買主因。RAW 能保留最大資訊量，未來不論影像格式如何演進，都能確保檔案可再次被最佳化轉出。  

### WPF 與 Canon RAW Codec 的研究起點
取得相機後作者須自行撰寫整理工具；Canon Codec 負責解碼，WPF 則是全新的 UI 與影像平台，必須先摸熟 System.Windows.Media.Imaging 相關 API。  

### HD Photo 格式帶來的新優勢
微軟推出 HD Photo，具備高動態範圍與廣色域，若能直接由 RAW 轉成此類新格式，可避免轉成 JPEG 時的資訊損失，對長期保存更有利。  

### WPF 影像物件架構與轉檔範例
作者展示以 BitmapDecoder 讀 CR2、TransformedBitmap 縮圖、JpegBitmapEncoder 輸出的最小程式碼範例，並比較 WPF 與 GDI+ 在思考模式上的差異。  

### EXIF Metadata 複製需求與挑戰
影像縮圖後若沒有 EXIF 就像失去靈魂；然而範例程式轉出的 JPEG 完全沒有 metadata，需要額外機制搬移。  

### Metadata Query 對照與 Library 封裝
WPF 使用類 XPath 語法操作 metadata，但 Canon RAW 與 JPEG EXIF 標籤不一致。作者以比對方式建立對照表（如 /ifd/{ushort=256} → /app1/ifd/exif/{ushort=256}），並將對照表嵌入程式庫 ImageUtil，使轉檔同時複製 EXIF。  

### 效能問題預告
經過一連串測試，基本轉檔與 EXIF 搬移已可穩定運作，但大量 RAW 批次處理的效能尚待改善，作者預告下一篇將專注於性能優化議題。