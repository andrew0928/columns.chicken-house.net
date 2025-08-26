# 利用 WPF 讀取 CANON (.CR2) 的 EXIF 及縮圖 (C# 範例程式說明)

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 EXIF？
- A簡: EXIF 是影像檔內嵌的拍攝資訊標準，包含曝光、鏡頭、時間、方向與相機品牌等屬性。
- A詳: EXIF（Exchangeable Image File Format）是數位相機與影像裝置將拍攝時的技術資料內嵌到影像檔中的標準。常見欄位包括曝光時間、光圈、ISO、焦距、相機廠牌與型號、拍攝時間、方向（Orientation）、GPS 等。EXIF 可用於影像管理、排序、搜尋與顯示調整（例如自動旋轉）。在 RAW 與 JPEG 皆可能存在，但對 RAW 檔（如 CR2），EXIF 與廠商自訂的 MakerNotes 往往更豐富，需要正確的解碼器（Codec）與查詢方式讀取。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q20, B-Q3

A-Q2: 在 WPF 影像系統中，什麼是 Metadata？
- A簡: WPF 將影像敘述資訊統稱為 Metadata，並以 Metadata Query Language 彈性查詢。
- A詳: 在 WPF（背後為 WIC）中，影像檔的敘述性資訊不僅限於 EXIF，還包含 XMP、IPTC 等。為統一處理，WPF 將此類資訊統稱為 Metadata，並提供 BitmapMetadata 與 GetQuery 方法，以 Metadata Query Language（MQL）語法從不同標準的節點與子樹中查詢值。這種作法避免依賴硬編碼的屬性名稱或 API 常數，特別適合 EXIF 規格複雜與各家廠商擴充（MakerNotes）情境。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, B-Q2, B-Q3

A-Q3: 什麼是 WPF 的 Metadata Query Language（MQL）？
- A簡: MQL 是 WPF 用於查詢影像 Metadata 的路徑語法，如 /ifd/{ushort=274} 指向 EXIF 欄位。
- A詳: Metadata Query Language（MQL）是一種針對影像中多種 Metadata 樹（如 IFD、EXIF IFD、XMP）的路徑式查詢語法。以 /ifd 為起點，使用 {ushort=TagNumber} 指定 EXIF Tag 數值，並可向下層節點（如 /ifd/{ushort=34665} 指向 EXIF IFD Pointer）遞迴查詢。例如 /ifd/{ushort=274} 取得 Orientation；/ifd/{ushort=34665}/{ushort=33434} 取得曝光時間。這讓開發者不必逐一映射複雜的屬性常數。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q4, A-Q2

A-Q4: Canon .CR2 與 JPEG 的差異是什麼？
- A簡: CR2 是 Canon RAW 檔，保留感測器原始資料；JPEG 是壓縮後的成品圖，體積小、解碼快。
- A詳: CR2（Canon RAW version 2）保留感測器近原始的曝光資料、位深與更多拍攝資訊，利於後製與動態範圍調整，但解碼成本高、檔案大且需專用 Codec。JPEG 則是經相機內部處理（白平衡、銳利化、壓縮）後的成品，檔案小、相容性高，顯示與傳輸快速。於 WPF 環境，解析 CR2 需 Canon RAW Codec；縮圖時可利用 Codec 的快速路徑（如嵌入預覽）獲得明顯的效能差異。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, B-Q9, D-Q2

A-Q5: 為什麼在影像轉檔時要保留 Metadata？
- A簡: Metadata 提供拍攝脈絡與管理價值，保留能維持檔案可用性與搜尋性。
- A詳: 轉檔時保留 Metadata（尤其 EXIF 與關鍵 XMP）可維持拍攝資訊、版權、建立日期與方向等語意資料，對影像管理、排序、檢索、顯示正確性（例如依 Orientation 自動旋轉）至關重要。若遺失，後續追溯拍攝條件與自動化流程（如相簿系統）將受影響。在 WPF 中，可利用 BitmapFrame.Create 時帶入來源的 Metadata，自動複製至輸出編碼器（例如 JpegBitmapEncoder）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q12, C-Q4, D-Q6

A-Q6: 什麼是影像 Codec？內建與第三方有何差異？
- A簡: Codec 是編解碼器。內建通常相容性佳；第三方支援特定格式如 CR2，行為可能不同。
- A詳: 影像 Codec（編解碼器）負責將檔案格式轉為像素與 Metadata，或反之。Windows/WPF 透過 WIC 調用系統或第三方 Codec。內建 Codec 多支援常見格式（JPEG/PNG/TIFF），行為穩定；第三方（如 Canon RAW Codec）支援專有 RAW，功能與效能取決於廠商實作，可能對 Metadata Query 的節點支援度、縮圖快速路徑與解碼策略有所差異，因此需按實測調整流程與容錯。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, D-Q10, D-Q2

A-Q7: 為何讀取 Metadata 時不能過早關閉檔案串流？
- A簡: WPF 影像解碼常延遲載入，串流若先關閉，後續 Metadata/像素會讀取失敗。
- A詳: BitmapDecoder 預設使用延遲載入與隨取（CacheOption=None），許多資訊直到實際存取 Frames 或 Metadata 才從串流讀取。若在取得 BitmapDecoder 後即關閉 FileStream，隨後呼叫 Frames[0] 或 Metadata.GetQuery 將因資料尚未載入而失敗或回傳 null。解法是：維持串流至使用完畢，或改用 BitmapCacheOption.OnLoad 讓解碼器在建立時就把所需資料完整載入，之後可安全關閉串流。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q14, D-Q4

A-Q8: 什麼是 BitmapDecoder 與 BitmapMetadata？
- A簡: BitmapDecoder 負責讀檔與產生影格；BitmapMetadata 提供查詢與操作影像描述資料。
- A詳: BitmapDecoder 是 WPF/WIC 的讀檔元件，根據檔頭選擇對應 Codec，輸出一或多個 Frames（BitmapFrame），每個 Frame 代表一個影像層或頁。BitmapMetadata 與 Frame 綁定，提供 GetQuery/SetQuery 讀寫 Metadata。對 RAW（CR2）而言，第一個 Frame 即主要影像，搭配 Metadata 可讀取 EXIF/廠商資訊。這兩者構成讀取像素與敘述資料的核心。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q2, A-Q10

A-Q9: 什麼是 IFD？EXIF 的 ushort 標籤是什麼？
- A簡: IFD 是影像檔目錄；EXIF 以無號短整數標籤識別欄位，如 274 表 Orientation。
- A詳: IFD（Image File Directory）是 TIFF/EXIF 使用的目錄結構，包含多個標籤項（Tag）。每個標籤以無號短整數（ushort）標識，例如 256/257 為寬/高、274 為方向、34665 為 EXIF IFD 指標，指向更多 EXIF 子標籤（如 33434 曝光時間、33437 光圈、34855 ISO）。WPF 的 MQL 以 /ifd/{ushort=TAG} 形式定位這些欄位。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, B-Q4, B-Q10

A-Q10: 什麼是 Frame（Frames[0]）？為何通常取第 0 個？
- A簡: Frame 是解碼後的影像頁或層。多數單張影像只有一個 Frame，因此取 Frames[0]。
- A詳: WPF 中的 BitmapDecoder 可能輸出多個 BitmapFrame，例如多頁 TIFF 或含縮圖的容器。一般單張 RAW/JPEG 僅有一個主要 Frame，故習慣使用 Frames[0]。對 RAW，Codec 也可能提供不同解析度路徑，但仍以第一個 Frame 為主。使用 Frames[0] 搭配 TransformedBitmap 可進一步縮放產生縮圖。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, B-Q8, C-Q2

A-Q11: 什麼是縮圖（Thumbnail）？與原圖有何差異？
- A簡: 縮圖是較小尺寸的預覽圖，便於快速瀏覽；原圖保留完整像素與細節，體積大。
- A詳: 縮圖是為快速瀏覽或列表顯示而產生的低解析度影像，通常數百像素邊長，檔案小且生成速度快。原圖則保留完整解析度與細節，用於編修與輸出。對 RAW 格式，Codec 常提供快速生成縮圖的路徑（可能取用內嵌 JPEG 預覽或低解析解碼），遠快於完整像素解碼。WPF 中可用 TransformedBitmap 搭配 JpegBitmapEncoder 產生縮圖。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, B-Q9, C-Q2

A-Q12: 為何產生縮圖比完整解碼 RAW 快非常多？
- A簡: RAW Codec 多對小尺寸輸出走快路徑，使用內嵌預覽或低解析解碼，省掉重計算。
- A詳: RAW 檔完整解碼需經去馬賽克、色彩轉換、降噪等重運算，耗時甚巨；但為了快速預覽，許多 RAW 檔內嵌 JPEG 預覽或提供降解析度的快速解碼通道。當請求輸出尺寸很小（例如 0.1 倍）時，Codec 會優先走這類快路徑，顯著縮短時間（實測 1.5 秒對比 60+ 秒）。因此縮圖生成可達到極大效能收益。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, C-Q2, D-Q3

A-Q13: 什麼是 JpegBitmapEncoder 的 QualityLevel？
- A簡: QualityLevel 控制 JPEG 壓縮品質與檔案大小，100 最佳、數值越低壓縮越高越失真。
- A詳: JpegBitmapEncoder 以量化（Quantization）控制壓縮強度。QualityLevel 0–100：值越高保留細節越多、檔案越大；越低失真越明顯但體積更小。常見建議縮圖品質 75–90 可兼顧外觀與大小。設定在 Save 前指定，並受輸入像素品質影響。縮圖視覺上對壓縮瑕疵較不敏感，故可選較低品質提升效能與節省儲存。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, C-Q3, B-Q22

A-Q14: 為什麼縮圖常用 75–90 的 JPEG 品質？
- A簡: 75–90 在視覺品質與檔案大小間達良好平衡，縮圖對壓縮失真較不敏感。
- A詳: 人眼對小尺寸預覽圖的高頻細節與微小壓縮痕跡不敏感。實務上，在 75–90 的品質區間，縮圖肉眼難見差異而可大幅減少檔案大小與 IO 壓力，亦縮短編碼時間。若用於網頁列表或後台索引，75–85 已足夠；對高質感展示可取 90。需依顯示尺寸與內容動態調整。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q13, B-Q22, C-Q3

A-Q15: 為什麼縮小尺寸會降低 RAW 解碼成本？
- A簡: 小尺寸可讓 Codec 採用低解析解碼或抽樣，避開昂貴的全像素去馬賽克與處理。
- A詳: 完整 RAW 解碼需針對每像素進行去馬賽克、色彩空間轉換、降噪等多階段運算。當輸出目標尺寸顯著小於原始解析度時，Codec 能先以降解析（例如 Bayer 抽樣）或直接取用內嵌預覽，將運算量與記憶體帶寬需求降到數十分之一甚至更少，導致巨幅加速。這是縮圖快於全尺寸轉檔的關鍵原因。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q9, D-Q3

A-Q16: BitmapCacheOption 有哪些選項，有何影響？
- A簡: 常用 None 與 OnLoad。None 延遲載入需保持串流；OnLoad 立即載入可提早關檔。
- A詳: BitmapCacheOption.None 採延遲載入，第一次存取像素或 Metadata 時才讀取來源，適合大檔案、逐步處理，但需避免過早關閉串流。OnLoad 則在建立 Decoder/Frame 時即載入資料，可立即關閉串流，減少檔案鎖定，適合短生命週期處理或 Web。Default 依實作選擇。選擇關乎資源管理與錯誤風險。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q14, D-Q4

A-Q17: BitmapCreateOptions 常見選項有何差異？
- A簡: 常見 None、PreservePixelFormat、DelayCreation；影響解碼行為與像素格式保存。
- A詳: None 表示使用預設策略。PreservePixelFormat 要求儘量保留來源像素格式，避免隱性轉換（可能影響性能或相容性）。DelayCreation 延遲建立影像源，配合延遲載入可降低初始開銷。實務上，若僅作縮圖，None 即可；若需精準控制像素格式，才考慮 PreservePixelFormat。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q19, C-Q2

A-Q18: 為何 WPF 轉全尺寸 CR2 可能比原廠 DPP 慢？
- A簡: WPF 經 WIC 與通用 Codec 路徑，額外抽象層與通用性取捨，致效能打折。
- A詳: WPF 透過 WIC 與外部 Codec 解碼。通用框架需處理多格式、多路徑與記憶體安全，常引入額外拷貝、抽象成本；再者，第三方 RAW Codec 對 WIC 的實作與最佳化程度不一，可能不及原廠 DPP 等專用軟體的管線最佳化。因此在全解析轉檔時，WPF 路徑可能耗時顯著；但在縮圖情境，藉快路徑仍具高效率。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q15, D-Q3

A-Q19: 為何 Web 縮圖服務仍需快取（Cache）？
- A簡: 即便縮圖加速，並行請求仍昂貴；快取可避免重算、降延遲與減輕 CPU/IO。
- A詳: 縮圖耗時可能為 1–2 秒，對高併發 Web 仍偏慢。若不快取，重複請求同一影像會佔用 CPU 與磁碟 IO，導致隊列積壓與逾時。透過檔案指紋（路徑+LastWriteTime）或雜湊鍵快取縮圖結果，可使重複請求直接命中，顯著改善效能與穩定性。亦可搭配背景批次生成與 CDN 分發。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q9, D-Q9, A-Q12

A-Q20: MQL 常見 EXIF 路徑有哪些？
- A簡: 例如 /ifd/{ushort=274} 方向、/ifd/{ushort=34665}/{ushort=33434} 曝光時間。
- A詳: 常用路徑包括：/ifd/{ushort=256,257} 寬高；274 方向；271/272 品牌型號；306 日期時間；34665 指向 EXIF IFD 後，33434 曝光時間、33437 光圈、34855 ISO、37386 鏡頭焦距、37510 使用者註記、40960/40961 色彩空間與相關資訊等。此類路徑可直接傳給 BitmapMetadata.GetQuery 取得值。遇到 MakerNotes（37500）則內容常為廠商自訂位元串。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q10, C-Q6

A-Q21: 使用 GDI+ 的 PropertyItem 與 WPF MQL 有何差異？
- A簡: GDI+ 以整數 ID 存取 EXIF；WPF 以路徑查詢，能跨多種 Metadata 樹且更彈性。
- A詳: System.Drawing（GDI+）透過 PropertyItem.Id 存取 EXIF，較貼近 TIFF/EXIF，但易受格式限制；WPF MQL 以路徑式語法跨 IFD、EXIF IFD、XMP 等多種樹狀結構查詢，支援更廣泛的容器與擴充。對 RAW 與第三方 Codec，MQL 的彈性更有利，但也需注意不同 Codec 的支援差異與回傳型別多樣性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q25, A-Q3, D-Q10

A-Q22: EXIF Orientation（274）有何用途？
- A簡: Orientation 指出相機持握方向；正確讀取後可自動旋轉顯示或輸出。
- A詳: EXIF Tag 274 表示影像需如何旋轉/翻轉才能正向顯示（1=正常、6=右轉90°等）。許多相片看似橫倒，其實像素未旋轉而依賴此標記。縮圖或轉檔時若忽略，結果可能方向錯誤。WPF 可讀取 274 後以 RotateTransform 修正輸出，並更新目標檔 Metadata 以維持一致性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q7, D-Q6, B-Q16

A-Q23: 第三方 RAW Codec 與 WPF 相容性有哪些風險？
- A簡: 支援的 Metadata 節點、縮圖快路徑與型別回傳可能不一致，需容錯與檢測。
- A詳: 不同廠牌或版本的 RAW Codec 對 WIC 介面的覆蓋程度不同，表現為：部分 MQL 路徑不支援或回傳 null、MakerNotes 格式不透明、縮圖快速路徑可用性差異、像素格式與色彩資訊處理不同。實務上需偵測解碼器可用性、在讀取 GetQuery 時加上型別判斷與預設值，並於縮圖流程提供降級路徑或快取避免阻塞。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q10, B-Q18, C-Q10

A-Q24: 為何使用 TransformedBitmap 進行縮放？
- A簡: TransformedBitmap 在 WPF 影像管線中以圖形化方式縮放，利於串接編碼與高效率。
- A詳: TransformedBitmap 將任意 Transform（如 ScaleTransform）套用於來源 BitmapSource，形成新的可編碼影像。其優勢是與 WIC 解碼器緊密協作，當縮放比例很小時可觸發解碼器的降解析策略，減少像素處理；並能直接傳給 JpegBitmapEncoder 產生輸出，流程精簡、效能好，且可再串接旋轉或色彩校正等處理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, C-Q2, C-Q3


### Q&A 類別 B: 技術原理類

B-Q1: WPF 如何選擇對應的影像解碼器（Codec）？
- A簡: 透過 WIC 依檔頭與註冊表選擇支援的解碼器，RAW 需安裝對應第三方 Codec。
- A詳: BitmapDecoder.Create 會交由 WIC 判斷來源資料流的格式（檔頭 magic/容器識別），再根據系統註冊的解碼器清單選擇相容的 Codec。若是 JPEG/PNG/ TIFF 等常見格式，使用內建解碼器；RAW（如 CR2）則需 Canon RAW Codec 等第三方提供。解碼器決定像素輸出、Metadata 節點與快速縮圖能力。若缺少對應 Codec，Create 將失敗或回傳不支援。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, D-Q2, B-Q18

B-Q2: 在 WPF 讀取 Metadata 的執行流程為何？
- A簡: 開檔流→建立 Decoder→取 Frames[0].Metadata→以 MQL GetQuery 取得欄位。
- A詳: 流程為：1) 開啟 FileStream；2) BitmapDecoder.Create(fs, CreateOptions, CacheOption) 建立 Decoder；3) 取 decoder.Frames[0]；4) 取得 frame.Metadata as BitmapMetadata；5) 對各 MQL 路徑呼叫 metadata.GetQuery(path)；6) 使用完畢關閉串流（或 OnLoad 後提前關）。此流程仰賴 Codec 提供的 Metadata 樹與路徑支援。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, A-Q20, C-Q1

B-Q3: MQL 路徑解析的機制是什麼？
- A簡: 以樹狀節點遍歷 /ifd/…，節點可為 IFD 指標、子 IFD 或具名命名空間（如 XMP）。
- A詳: MQL 將 Metadata 視為樹，根節點下可有 ifd、xmp、app1 等命名樹。/ifd/{ushort=34665} 代表節點為 EXIF IFD 的指標，再往下 /{ushort=33434} 取具體標籤。解析器依路徑逐節點查找，若節點不存在或不支援，回傳 null。對 XMP 可用具名節點與屬性存取。型別可能是數值、字串、Rational 或位元組陣列。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, A-Q20, D-Q1

B-Q4: EXIF IFD 在 MQL 中如何表示？
- A簡: 以 /ifd 為根，子標籤用 {ushort=Tag}，EXIF 子表透過 34665 指標再下鑽。
- A詳: 在 MQL 中，/ifd 表示主 IFD。主 IFD 常見標籤：256/257（寬高）、271/272（品牌型號）、274（方向）、306（日期）。標籤 34665（ExifIFDPointer）指向 EXIF 子 IFD，再於該層查詢 33434（曝光）、33437（光圈）、34855（ISO）、37386（焦距）等。這種層級化結構對映 TIFF/EXIF 的鏈結式目錄設計。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, A-Q20, C-Q6

B-Q5: 延遲載入與串流生命週期的內在原理？
- A簡: None 模式延遲解碼與讀檔，實際取用時才讀流；因此需維持串流開啟。
- A詳: CacheOption=None 時，Decoder 僅建立最小化狀態，直到訪問 Frames 或 Metadata 才向串流請求資料，且可能多次讀取。這降低初始成本，但要求串流在整個取用過程中可用。若提前關閉，後續讀取會失敗。OnLoad 則在建立時完整讀入快取，之後可立即關閉串流，換取較高初始耗時與記憶體占用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, A-Q16, D-Q4

B-Q6: WPF 的 Frame 與 RAW 預覽路徑如何互動？
- A簡: 通常以 Frames[0] 代表主影像；縮小輸出時 Codec 可能走預覽/降解析快路徑。
- A詳: Frames[0] 是主要影像的 BitmapSource。當它被包裝成 TransformedBitmap 並以小比例縮放查詢像素時，RAW Codec 得以判斷需求解析度，改走較快的預覽或抽樣解碼，避免完整去馬賽克與色彩處理。此互動實現了縮圖超快的效果；若請求 1.0 倍或更高解析，則需完整解碼。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q8, C-Q2

B-Q7: JpegBitmapEncoder 的工作機制？
- A簡: 接收 BitmapSource，進行色度取樣與量化壓縮，依 QualityLevel 決定失真與大小。
- A詳: 編碼器讀取輸入像素（可能經 Transform 處理），執行色彩空間轉換（通常至 YCbCr）、分區塊 DCT、量化與霍夫曼編碼。QualityLevel 調整量化表強度，影響壓縮率。編碼器亦可攜帶 Metadata（若 Frame 提供）。輸出至串流時需確保資料順序與資源正確釋放。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q22, C-Q2

B-Q8: TransformedBitmap 的管線如何設計？
- A簡: 以來源 BitmapSource 加上 Transform，延遲評估，編碼或渲染時才取樣輸出。
- A詳: TransformedBitmap 包裝來源並記錄幾何變換（縮放、旋轉等），不立即產生新像素。當下游（例如 Encoder 或 UI 渲染）請求像素時，才由來源解碼器依需要解析度解碼並執行取樣。此設計可讓解碼器自適應解析度，實現縮圖快路徑與避免不必要的中間緩衝。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q24, C-Q2, C-Q7

B-Q9: 為何縮圖時解碼器可走快路徑？
- A簡: 目標尺寸小，解碼器可使用內嵌預覽或降解析抽樣，避免重度像素處理。
- A詳: RAW Codec 能判定輸出目標的解析度需求，若遠低於原始大小，則可直接取用內嵌 JPEG 預覽或以較低解析度解碼演算法（如 skipping/averaging Bayer），大幅減少 CPU 與記憶體使用。此能力依 Codec 實作而異，但多數廠商為了使用者體驗會特別最佳化此路徑。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, A-Q15, D-Q3

B-Q10: EXIF 指標 34665 與巢狀查詢的意義？
- A簡: 34665 指向 EXIF IFD，必須先到該節點，再取子標籤如 33434（曝光時間）。
- A詳: 主 IFD 的 34665（ExifIFDPointer）不是最終資料，而是指向另一個目錄表。MQL 必須先到 /ifd/{ushort=34665} 節點，再以 /{ushort=33434,33437,34855,…} 取得對應資料。這反映 EXIF 擴充資訊分離於主 IFD 的設計，有助於結構化與相容性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, A-Q20, C-Q6

B-Q11: 如何由數字標籤對應語意名稱？
- A簡: 透過 EXIF 標籤表對照（如 274→Orientation），或以自建字典映射於程式中。
- A詳: EXIF 規格定義了標籤編號與含義，常見作法是建立 Dictionary<ushort,string> 映射，或使用現成對照表。WPF 本身不提供名稱轉換，GetQuery 直接回傳值。對 MakerNotes 等廠商自訂區塊，需參考廠商文件或使用專用函式庫解析。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q6, D-Q7, A-Q20

B-Q12: 如何在輸出 JPEG 時保留來源 Metadata？
- A簡: 建立 BitmapFrame.Create 時帶入來源 Metadata，Encoder 會將其寫入輸出。
- A詳: 使用 BitmapFrame.Create(source, thumbnail, metadata, colorContexts) 的 metadata 參數傳入來源的 BitmapMetadata，然後將該 Frame 加入 JpegBitmapEncoder.Frames。多數欄位可直接複製；部分不相容欄位（或 MakerNotes）可能被忽略或需手動過濾。務必在 Save 前完成設定。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q4, A-Q5, D-Q7

B-Q13: 產生縮圖的標準流程是什麼？
- A簡: 開檔→解碼→TransformedBitmap 縮放→建立 JPEG Encoder→設定品質→Save。
- A詳: 1) FileStream 讀取來源；2) BitmapDecoder.Create 建立解碼器；3) 取得 Frames[0]；4) new TransformedBitmap(frame, new ScaleTransform(sx, sy))；5) new JpegBitmapEncoder，設定 QualityLevel；6) target.Frames.Add(BitmapFrame.Create(transformed, null, metadata?, null))；7) Save 至輸出串流；8) 關閉串流並釋放物件。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, C-Q3, A-Q24

B-Q14: 為何 OnLoad 可讓你提前關閉串流？
- A簡: OnLoad 會在解碼器建立時讀完必要資料，之後不再依賴原始串流。
- A詳: 選用 BitmapCacheOption.OnLoad，WIC 將立即將像素與 Metadata 載入記憶體。如此，建立 Decoder/Frame 後即可關閉來源串流，避免檔案鎖住與延長佔用。代價是初始化時間與記憶體用量上升，適合 Web/服務情境。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, A-Q16, C-Q5

B-Q15: WPF 與 DPP 等原廠軟體在解碼架構上的差異？
- A簡: WPF 走通用管線與外掛 Codec；原廠軟體以專用優化管線，完整解碼更快。
- A詳: WPF/WIC 提供通用 API 與多格式支援，需在彈性、相容與安全間取捨；原廠軟體（DPP）可針對單一格式深度最佳化（SIMD、管線化、快取），並避免抽象成本。結果是全尺寸解碼 WPF 常較慢，但在縮圖等輕量任務差距縮小。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q18, D-Q3, B-Q9

B-Q16: Orientation 的處理流程與顯示機制？
- A簡: 讀取 274 值→套用對應旋轉/翻轉→必要時更新輸出 Metadata。
- A詳: 取得 /ifd/{ushort=274}，依值（1/3/6/8 等）決定 RotateTransform 或 Flip。若輸出像素已旋正，應將輸出檔的 Orientation 設為 1（正常），避免二次旋轉。WPF 需自行處理，非所有控制會自動尊重該標籤。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q7, D-Q6, A-Q22

B-Q17: 色彩空間與色彩管理在此流程的角色？
- A簡: EXIF/XMP 可能標示色彩空間；WPF 可附帶 ColorContexts，影響輸出正確性。
- A詳: EXIF 40961（ColorSpace）與 ICC Profile/XMP 可描述色彩空間。WPF 中 BitmapFrame 可攜帶 ColorContexts，JpegBitmapEncoder 亦可寫入 Profile。若忽略，可能導致顏色偏差。縮圖常忽略 Profile 以求簡化，但對精準色彩要求應保留。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q12, C-Q4, D-Q5

B-Q18: 如何偵測第三方解碼器是否可用？
- A簡: 嘗試建立 Decoder 或列舉 WIC 解碼器；失敗則顯示安裝指引或降級處理。
- A詳: 嘗試 BitmapDecoder.Create 包在 try/catch，捕捉 NotSupportedException；或透過 WIC 組件列舉已註冊解碼器。若 CR2 不支援，提示使用者安裝 Canon RAW Codec，或改走外部工具/備援流程（如 ImageMagick + dcraw）。並為 Web 路徑提供預設占位圖。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q2, C-Q10, A-Q23

B-Q19: 像素格式與效能有何關聯？
- A簡: 不必要的像素格式轉換會增加 CPU/記憶體；保持來源格式可提升效率。
- A詳: 轉換至高位深或不同色彩格式會觸發昂貴的重採樣與記憶體拷貝。若僅做縮圖，讓解碼器直接輸出適合編碼器的格式（例如 24bpp BGR→YCbCr）可更有效率。PreservePixelFormat 或適當 CreateOptions 可避免多餘轉換。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q17, C-Q2, D-Q8

B-Q20: 如何計算等比例縮放的 Scale 值？
- A簡: 以目標邊長/原始邊長取最小值，sx=sy=scale，維持比例不變。
- A詳: 讀取原始寬高（/ifd/{ushort=256,257} 或 frame.PixelWidth/Height），計算 scale = min(targetWidth/srcWidth, targetHeight/srcHeight)。將 ScaleTransform(scale, scale) 套用於 TransformedBitmap，可保證落於盒內且不裁切。固定寬或高時，另一邊以等比例求得。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q3, A-Q11, B-Q13

B-Q21: 如何正確量測效能？
- A簡: 使用 Stopwatch 記錄開始/結束時間，獨立測量 IO、解碼與編碼階段。
- A詳: 在關鍵步驟（開檔、Create、取 Frame、縮放、Save）前後標記時間，分段記錄可定位瓶頸。多次測量取中位數，並清理快取/暖機，以獲得穩定數據。注意避免將串流關閉時間包含在錯誤區段。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, D-Q3, A-Q18

B-Q22: JPEG 品質與檔案大小的權衡原理？
- A簡: 量化越強（低品質）→資料丟失多→檔案變小；反之亦然。
- A詳: JPEG 透過 DCT 將訊號轉至頻域，再以量化表砍掉高頻係數。低 QualityLevel 使用更激進的量化表，減少位元但造成失真與鋸齒/方塊等瑕疵。縮圖時因尺寸小，視覺容忍較高，可選 75–90；大圖或後製用途需更高品質或改用 PNG/無損方案。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q13, A-Q14, C-Q3

B-Q23: 記憶體使用與釋放的模式？
- A簡: OnLoad 占記憶體較多；None 需持續開檔。適度 using 與釋放流可穩定長時間執行。
- A詳: OnLoad 會將像素與 Metadata 保持於記憶體，適合短生命週期但需留意高併發時峰值。None 模式解碼延遲，但檔案鎖定時間長。以 using 包裝串流、Encoder 並在完成後釋放；對 BitmapSource 可考慮 Freeze 提升跨執行緒安全。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q8, C-Q5, B-Q14

B-Q24: WPF 影像的執行緒模型與 Freeze 為何重要？
- A簡: Freezable（如 BitmapSource）可 Freeze 成唯讀，以便跨執行緒存取與提升效能。
- A詳: WPF 物件多與 UI 執行緒關聯。對 BitmapSource/TransformedBitmap，若處理於背景工作執行緒，完成後呼叫 Freeze() 可將其設為不可變，允許安全跨執行緒傳遞至 UI，並讓系統進行內部最佳化。未凍結的物件跨執行緒使用會拋例外。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: D-Q9, C-Q2, B-Q23

B-Q25: 使用 System.Drawing 與 WPF 影像 API 的差異？
- A簡: GDI+ 在 Windows Forms 常見；WPF/WIC 在新式影像管線與 RAW/Metadata 更彈性。
- A詳: System.Drawing 偏向 GDI+，對 EXIF 基礎支援但對 RAW 依賴外部工具；WPF/WIC 原生支援多 Codec 與 MQL 查詢，管線化處理（TransformedBitmap+Encoder）更自然。選擇依 UI 架構與格式需求而定。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q21, C-Q1, D-Q10

B-Q26: Canon MakerNotes（37500）應如何看待？
- A簡: 為廠商自訂區塊，格式不公開，通常當作位元資料複製，慎防誤解析。
- A詳: MakerNotes 常含鏡頭型號、對焦點、快門次數等資訊，但編碼方式私有且可能綁定相機/韌體版本。WPF 僅能以 GetQuery 取得位元組陣列，建議不要嘗試解析，除非使用專門函式庫。轉檔時可選擇保留或移除以避免相容性問題。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q12, D-Q7, A-Q23


### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何用 WPF 讀取 CR2 的 Metadata（EXIF）？
- A簡: 建立 BitmapDecoder 後取得 Frames[0].Metadata 為 BitmapMetadata，使用 GetQuery 查值。
- A詳: 
  - 具體實作步驟:
    1) using 開啟 FileStream
    2) BitmapDecoder.Create 建立 Decoder
    3) 取 frame = decoder.Frames[0]
    4) 取得 metadata = (BitmapMetadata)frame.Metadata
    5) metadata.GetQuery("/ifd/{ushort=274}") 等
  - 關鍵程式碼片段:
    ```csharp
    using var fs = File.OpenRead(src);
    var dec = BitmapDecoder.Create(fs, BitmapCreateOptions.None, BitmapCacheOption.None);
    var meta = dec.Frames[0].Metadata as BitmapMetadata;
    var orient = meta?.GetQuery("/ifd/{ushort=274}");
    ```
  - 注意事項與最佳實踐: 串流勿過早關閉；需要提前關檔時改用 OnLoad；對 GetQuery 結果做 null/型別判斷。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, A-Q7, A-Q20

C-Q2: 如何以 WPF 產生 1/10 尺寸的 JPEG 縮圖？
- A簡: 以 TransformedBitmap 施加 ScaleTransform(0.1)，加入 JpegBitmapEncoder 後 Save。
- A詳: 
  - 具體實作步驟: 開檔→解碼→TransformedBitmap 縮放→JpegBitmapEncoder 設 Quality→Save。
  - 關鍵程式碼片段:
    ```csharp
    using var fi = File.OpenRead(src);
    using var fo = File.Create(dst);
    var dec = BitmapDecoder.Create(fi, BitmapCreateOptions.None, BitmapCacheOption.None);
    var tb = new TransformedBitmap(dec.Frames[0], new ScaleTransform(0.1, 0.1));
    var enc = new JpegBitmapEncoder { QualityLevel = 90 };
    enc.Frames.Add(BitmapFrame.Create(tb));
    enc.Save(fo);
    ```
  - 注意事項與最佳實踐: 小比例可觸發 RAW 快路徑；品質 75–90 足夠；必要時讀 Orientation 先旋正。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, B-Q8, B-Q13

C-Q3: 如何產生固定盒內（例如 400×300）的等比例縮圖？
- A簡: 讀原始寬高，計算 scale=min(400/w, 300/h)，用 ScaleTransform(scale, scale)。
- A詳: 
  - 具體實作步驟: 取得 frame.PixelWidth/Height→計算 scale→建立 TransformedBitmap→編碼保存。
  - 關鍵程式碼片段:
    ```csharp
    var frame = dec.Frames[0];
    double sw = 400.0 / frame.PixelWidth, sh = 300.0 / frame.PixelHeight;
    double s = Math.Min(sw, sh);
    var tb = new TransformedBitmap(frame, new ScaleTransform(s, s));
    ```
  - 注意事項與最佳實踐: 保留比例避免拉伸；可選較低 QualityLevel；可同時處理 Orientation。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q20, A-Q14, C-Q7

C-Q4: 如何在轉檔時保留來源 Metadata？
- A簡: 建立 BitmapFrame.Create 時傳入來源 Metadata，Encoder 會將其寫入輸出。
- A詳: 
  - 具體實作步驟: 取得來源 BitmapMetadata→BitmapFrame.Create(transformed, null, metadata, null)→加入 Encoder→Save。
  - 關鍵程式碼片段:
    ```csharp
    var srcMeta = dec.Frames[0].Metadata as BitmapMetadata;
    enc.Frames.Add(BitmapFrame.Create(tb, null, srcMeta, null));
    ```
  - 注意事項與最佳實踐: 某些 RAW 專屬欄位可能不相容；若已旋正像素，更新 Orientation=1；確保避免寫入非法欄位。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, A-Q5, B-Q16

C-Q5: 如何安全關閉串流又能讀到 Metadata？
- A簡: 使用 BitmapCacheOption.OnLoad 讓資料先讀入記憶體，再關閉串流。
- A詳: 
  - 具體實作步驟: Create 時指定 OnLoad→取用 Metadata 與像素→立即關檔。
  - 關鍵程式碼片段:
    ```csharp
    using var fs = File.OpenRead(src);
    var dec = BitmapDecoder.Create(fs, BitmapCreateOptions.None, BitmapCacheOption.OnLoad);
    fs.Close(); // 安全
    var meta = (BitmapMetadata)dec.Frames[0].Metadata;
    ```
  - 注意事項與最佳實踐: OnLoad 增加初始化時間與記憶體；適用於 Web/短流程；避免大批量同時 OnLoad 造成峰值。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, B-Q14, D-Q4

C-Q6: 如何讀取特定 EXIF 欄位（曝光、光圈、ISO）並轉成人類可讀？
- A簡: 使用對應 MQL 路徑取值，Rational 需轉小數或格式化為 1/x 秒、F x.x。
- A詳: 
  - 具體實作步驟: 33434→曝光時間；33437→光圈；34855→ISO；取得值後依型別轉換。
  - 關鍵程式碼片段:
    ```csharp
    var m = meta;
    var exp = m?.GetQuery("/ifd/{ushort=34665}/{ushort=33434}"); // 像 1/200
    var fno = m?.GetQuery("/ifd/{ushort=34665}/{ushort=33437}");
    var iso = m?.GetQuery("/ifd/{ushort=34665}/{ushort=34855}");
    string ExpToStr(object v) => v switch { ulong[] r when r.Length==2 => $"{r[0]}/{r[1]} s", _ => v?.ToString() ?? "-" };
    ```
  - 注意事項與最佳實踐: 處理多型別（有時為 ulong[] Rational）；加上 null 容錯；必要時自建對照表。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q20, B-Q11, D-Q1

C-Q7: 如何依 EXIF Orientation 自動旋正縮圖？
- A簡: 讀 274 值後套用 RotateTransform/ScaleTransform 組合，並更新輸出 Orientation。
- A詳: 
  - 具體實作步驟: 讀 274→決定角度或翻轉→將 RotateTransform 與 ScaleTransform 組合成 TransformGroup→建立 TransformedBitmap→輸出後將 Orientation 設為 1。
  - 關鍵程式碼片段:
    ```csharp
    int ori = Convert.ToInt32(meta.GetQuery("/ifd/{ushort=274}") ?? 1);
    Transform rot = ori switch { 6 => new RotateTransform(90), 8 => new RotateTransform(270), 3 => new RotateTransform(180), _ => Transform.Identity };
    var tg = new TransformGroup(); tg.Children.Add(rot); tg.Children.Add(new ScaleTransform(s,s));
    var tb = new TransformedBitmap(frame, tg);
    var outMeta = frame.Metadata.Clone() as BitmapMetadata;
    outMeta?.SetQuery("/ifd/{ushort=274}", (ushort)1);
    enc.Frames.Add(BitmapFrame.Create(tb, null, outMeta, null));
    ```
  - 注意事項與最佳實踐: 處理翻轉類型（2/4/5/7）；若不旋正像素，保留原 Orientation。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q16, A-Q22, D-Q6

C-Q8: 如何為 GetQuery 實作穩健的容錯與型別處理？
- A簡: 封裝讀取函式，對 null、不同型別（數值、Rational、byte[]）做安全轉換。
- A詳: 
  - 具體實作步驟: 建立 TryGet<T>(path, out T)；或建立 object→string 的安全轉換器。
  - 關鍵程式碼片段:
    ```csharp
    bool TryGetString(BitmapMetadata m, string p, out string s){ s=""; var v=m?.GetQuery(p); if(v==null) return false;
      s = v switch { ulong[] r when r.Length==2 => $"{r[0]}/{r[1]}", byte[] b => BitConverter.ToString(b), _ => v.ToString() }; return true; }
    ```
  - 注意事項與最佳實踐: 不同 Codec 回傳型別可能不同；避免 InvalidCastException；對未知欄位保留原始位元資料。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q1, A-Q23, B-Q11

C-Q9: 在 ASP.NET 中如何快取縮圖以提升併發效能？
- A簡: 使用檔案指紋作鍵，磁碟快取縮圖結果；命中則直接回傳而不重算。
- A詳: 
  - 具體實作步驟: 建構鍵=路徑+LastWriteTime；若快取檔存在→回傳；否則生成縮圖存入快取再回傳。
  - 關鍵程式碼片段:
    ```csharp
    string key = Hash(path + File.GetLastWriteTimeUtc(path));
    string thumb = Path.Combine(cacheDir, key + ".jpg");
    if(!File.Exists(thumb)) { GenerateThumbnail(path, thumb); }
    return PhysicalFile(thumb, "image/jpeg");
    ```
  - 注意事項與最佳實踐: 以檔案鎖與互斥避免驚群；設定過期策略；CDN/ResponseCache 搭配。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q19, D-Q9, C-Q2

C-Q10: 如何在程式啟動時檢查 CR2 解碼支援並提供替代方案？
- A簡: 嘗試開啟樣本或用 WIC 列舉解碼器，失敗則提示安裝或走備援管線。
- A詳: 
  - 具體實作步驟: 啟動時呼叫 ProbeDecoder(".cr2")；若不支援則顯示指引（連結 Canon RAW Codec），或改以外部工具/占位圖。
  - 關鍵程式碼片段:
    ```csharp
    bool CanDecodeCr2(){ try{ using var fs=File.OpenRead(sampleCr2); BitmapDecoder.Create(fs, BitmapCreateOptions.None, BitmapCacheOption.OnLoad); return true; } catch { return false; } }
    ```
  - 注意事項與最佳實踐: 避免硬相依；提供設定開關；記錄遺失狀態以利運維。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q18, D-Q2, A-Q23


### Q&A 類別 D: 問題解決類（10題）

D-Q1: GetQuery 常回傳 null，怎麼辦？
- A簡: 可能路徑不支援或無該欄位；檢查 MQL、Codec 支援，並加入容錯與替代欄位。
- A詳: 
  - 問題症狀描述: 多數標籤回傳 null 或僅部分可讀。
  - 可能原因分析: MQL 路徑誤寫；該檔案無此欄位；第三方 Codec 未提供節點；型別不符合。
  - 解決步驟: 驗證路徑；列印所有可用查詢嘗試；針對 Rational 等型別做解析；加上預設值。
  - 預防措施: 封裝安全的 TryGet；維護對照表；在多 Codec 環境加單元測試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, A-Q20, C-Q8

D-Q2: 建立 Decoder 失敗或報不支援 CR2，怎麼處理？
- A簡: 未安裝 Canon RAW Codec 或環境不相容；提示安裝、升級系統或採用備援。
- A詳: 
  - 問題症狀描述: Create 拋 NotSupportedException 或格式不支援。
  - 可能原因分析: 缺少對應 Codec；舊 OS 或 64 位元相容性問題。
  - 解決步驟: 安裝/更新 Canon RAW Codec；確認與 OS/CPU 架構相容；改用外部工具轉中間格式。
  - 預防措施: 啟動時偵測；記錄遺失；提供占位圖與重試策略。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q18, C-Q10

D-Q3: 轉全尺寸 CR2 耗時 60 秒以上的原因與改善？
- A簡: RAW 全解碼成本高且 WPF 管線有額外開銷；改用縮圖、快取與批次處理。
- A詳: 
  - 問題症狀描述: 全尺寸轉 JPEG 極慢。
  - 可能原因分析: RAW 去馬賽克等重運算；WIC 抽象開銷；Codec 未最佳化。
  - 解決步驟: 降低輸出尺寸觸發快路徑；調整品質；預先快取；離線批次產生。
  - 預防措施: Web 中避免即時全尺寸轉檔；加併發保護與佇列。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q9, C-Q9

D-Q4: 發生 ObjectDisposedException 或讀不到 Metadata？
- A簡: 串流過早關閉；改用 OnLoad 或延後關閉直到完成所有取用。
- A詳: 
  - 問題症狀描述: 取 Frames/Metadata 時拋已處置例外或回傳 null。
  - 可能原因分析: CacheOption=None 時延遲讀取需要活的串流。
  - 解決步驟: 選用 OnLoad；或以 using 區塊確保流程內都可用；最後才關閉。
  - 預防措施: 撰寫單元測試與檢查點；統一封裝讀取邏輯。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, B-Q5, C-Q5

D-Q5: 輸出 JPEG 體積過大或畫質不佳，如何調整？
- A簡: 調整 QualityLevel；檢視影像內容；必要時改用更高品質或不同格式。
- A詳: 
  - 問題症狀描述: 檔案太大或有壓縮瑕疵。
  - 可能原因分析: QualityLevel 設定不當；內容高細節；色彩管理缺失。
  - 解決步驟: 調整 Quality 至 75–90；必要時提高或改 PNG；保留 ICC Profile。
  - 預防措施: 依尺寸情境制定預設曲線；建立目標檔大小上限與回退策略。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q13, B-Q22, C-Q3

D-Q6: 縮圖方向顛倒或旋轉錯誤怎麼辦？
- A簡: 讀 EXIF 274，輸出前旋正像素並將 Orientation 設回 1，或保留並由前端處理。
- A詳: 
  - 問題症狀描述: 縮圖顯示方向不對。
  - 可能原因分析: 未處理 Orientation；不同顯示端尊重度不同。
  - 解決步驟: 依 274 套用 Rotate/Flip；輸出更新 Orientation；或保留原標記。
  - 預防措施: 在產線流程中統一旋正策略；測試多終端相容性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q16, C-Q7, A-Q22

D-Q7: MakerNotes 顯示亂碼或無法解析？
- A簡: 屬廠商自訂格式；避免解析，必要時原樣複製或使用專門函式庫。
- A詳: 
  - 問題症狀描述: 讀取 37500 得到無法識別的位元資料。
  - 可能原因分析: Canon 私有編碼，與機型/韌體相關。
  - 解決步驟: 當作 byte[] 保存或忽略；若需解析，使用 exiftool 等專門工具。
  - 預防措施: 不將其當作一般字串處理；避免破壞性重寫。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q26, B-Q12, C-Q4

D-Q8: 記憶體使用異常升高或發生 OOM？
- A簡: 大量 OnLoad 或過多同時解碼；分批處理、限制併發、釋放與 Freeze 物件。
- A詳: 
  - 問題症狀描述: 大量處理時記憶體飆升。
  - 可能原因分析: OnLoad 將像素常駐；未釋放串流；缺乏併發限制。
  - 解決步驟: 使用 using；限制同時處理數；完成即釋放；Freeze 以利 GC。
  - 預防措施: 設計管線化、壓力測試與監控告警。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q23, B-Q24, C-Q5

D-Q9: ASP.NET 併發下縮圖逾時或阻塞？
- A簡: 縮圖雖快仍昂貴；加入結果快取、互斥鎖、背景佇列與 CDN。
- A詳: 
  - 問題症狀描述: 多用戶同時請求縮圖導致高延遲。
  - 可能原因分析: 無快取；重複計算；磁碟 IO 瓶頸。
  - 解決步驟: 檔案快取；同鍵互斥避免驚群；背景預算縮圖；CDN。
  - 預防措施: 設定 TTL 與大小上限；監控命中率；退化為占位圖。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q9, A-Q19, B-Q21

D-Q10: 不同第三方 Codec 導致路徑或型別不一致？
- A簡: 建立相容層：多路徑嘗試、型別容忍與功能偵測；必要時提供格式特化處理。
- A詳: 
  - 問題症狀描述: 相同 MQL 路徑於不同機器結果不同。
  - 可能原因分析: Codec 版本差異、回傳型別不一致。
  - 解決步驟: 為關鍵欄位建立候選路徑列表；以 switch 型別處理；特定廠商建立 adapter。
  - 預防措施: 啟動時功能偵測；針對支援矩陣寫測試；記錄遙測。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q23, B-Q18, C-Q8


### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 EXIF？
    - A-Q2: 在 WPF 影像系統中，什麼是 Metadata？
    - A-Q4: Canon .CR2 與 JPEG 的差異是什麼？
    - A-Q5: 為什麼在影像轉檔時要保留 Metadata？
    - A-Q6: 什麼是影像 Codec？內建與第三方有何差異？
    - A-Q8: 什麼是 BitmapDecoder 與 BitmapMetadata？
    - A-Q10: 什麼是 Frame（Frames[0]）？為何通常取第 0 個？
    - A-Q11: 什麼是縮圖（Thumbnail）？與原圖有何差異？
    - A-Q13: 什麼是 JpegBitmapEncoder 的 QualityLevel？
    - A-Q14: 為什麼縮圖常用 75–90 的 JPEG 品質？
    - B-Q2: 在 WPF 讀取 Metadata 的執行流程為何？
    - C-Q1: 如何用 WPF 讀取 CR2 的 Metadata（EXIF）？
    - C-Q2: 如何以 WPF 產生 1/10 尺寸的 JPEG 縮圖？
    - C-Q3: 如何產生固定盒內（例如 400×300）的等比例縮圖？
    - D-Q4: 發生 ObjectDisposedException 或讀不到 Metadata？

- 中級者：建議學習哪 20 題
    - A-Q3: 什麼是 WPF 的 Metadata Query Language（MQL）？
    - A-Q7: 為何讀取 Metadata 時不能過早關閉檔案串流？
    - A-Q9: 什麼是 IFD？EXIF 的 ushort 標籤是什麼？
    - A-Q12: 為何產生縮圖比完整解碼 RAW 快非常多？
    - A-Q16: BitmapCacheOption 有哪些選項，有何影響？
    - A-Q17: BitmapCreateOptions 常見選項有何差異？
    - A-Q22: EXIF Orientation（274）有何用途？
    - B-Q1: WPF 如何選擇對應的影像解碼器（Codec）？
    - B-Q3: MQL 路徑解析的機制是什麼？
    - B-Q4: EXIF IFD 在 MQL 中如何表示？
    - B-Q6: WPF 的 Frame 與 RAW 預覽路徑如何互動？
    - B-Q8: TransformedBitmap 的管線如何設計？
    - B-Q13: 產生縮圖的標準流程是什麼？
    - B-Q14: 為何 OnLoad 可讓你提前關閉串流？
    - C-Q4: 如何在轉檔時保留來源 Metadata？
    - C-Q5: 如何安全關閉串流又能讀到 Metadata？
    - C-Q6: 如何讀取特定 EXIF 欄位（曝光、光圈、ISO）並轉成人類可讀？
    - C-Q7: 如何依 EXIF Orientation 自動旋正縮圖？
    - D-Q1: GetQuery 常回傳 null，怎麼辦？
    - D-Q3: 轉全尺寸 CR2 耗時 60 秒以上的原因與改善？

- 高級者：建議關注哪 15 題
    - A-Q18: 為何 WPF 轉全尺寸 CR2 可能比原廠 DPP 慢？
    - A-Q23: 第三方 RAW Codec 與 WPF 相容性有哪些風險？
    - A-Q24: 為何使用 TransformedBitmap 進行縮放？
    - B-Q9: 為何縮圖時解碼器可走快路徑？
    - B-Q11: 如何由數字標籤對應語意名稱？
    - B-Q15: WPF 與 DPP 等原廠軟體在解碼架構上的差異？
    - B-Q17: 色彩空間與色彩管理在此流程的角色？
    - B-Q18: 如何偵測第三方解碼器是否可用？
    - B-Q19: 像素格式與效能有何關聯？
    - B-Q23: 記憶體使用與釋放的模式？
    - B-Q24: WPF 影像的執行緒模型與 Freeze 為何重要？
    - B-Q26: Canon MakerNotes（37500）應如何看待？
    - C-Q8: 如何為 GetQuery 實作穩健的容錯與型別處理？
    - D-Q8: 記憶體使用異常升高或發生 OOM？
    - D-Q10: 不同第三方 Codec 導致路徑或型別不一致？