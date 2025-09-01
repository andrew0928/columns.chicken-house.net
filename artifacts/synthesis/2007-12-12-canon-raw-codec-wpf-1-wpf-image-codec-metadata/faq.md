# Canon Raw Codec + WPF #1：WPF Image Codec 與 Metadata

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 RAW 檔與「RAW 支援」？
- A簡: RAW 是感光器原始影像資料；支援指系統能解碼、讀取、處理並轉換該格式，避免早期壓縮損失。
- A詳: RAW 指相機感光元件輸出的原始資料，保留完整位深與相機特定資訊，便於後製與長期保存。「RAW 支援」表示作業系統或應用程式具備對應的解碼器（codec），可直接讀取與處理該品牌與機型的 RAW，如文中安裝 Canon RAW codec 後，WPF 即可用 BitmapDecoder 讀 CR2，再透過 Encoder 轉為 JPEG 等格式。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, A-Q5, B-Q1

A-Q2: 為什麼保留 RAW 對未來更有保障？
- A簡: JPEG 老舊且有損，未來規格會更替；保留 RAW 可再轉新格式，避免經由 JPEG 二次折損。
- A詳: 作者強調照片不可重拍，格式演進難以預測。若只留 JPEG，後續轉換會疊加壓縮損失；而 RAW 保留最多原始資訊。只要相機廠與解碼器仍可用，之後可無縫轉換到新的通用格式，保有廣色域與高位深等優勢，因此 RAW 是耐久保存與未來相容性的關鍵。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, A-Q7, B-Q18

A-Q3: 什麼是 WPF（Windows Presentation Foundation）？
- A簡: WPF 是 .NET 的視覺化框架，強調宣告式 UI、向量圖形與可合成的圖像處理流程。
- A詳: WPF 是微軟的 UI 框架，採 XAML 與 .NET 管理程式碼。影像在 WPF 中是「來源→轉換→合成」的資料流，透過物件與轉換（如 TransformedBitmap）層層套用，類似影像軟體的圖層概念。相較 GDI/GDI+ 以像素繪製為主，WPF 更像 Flash/Photoshop 的組合式視覺模型，利於可重用與非破壞式處理。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, A-Q13, B-Q17

A-Q4: 什麼是 WPF 的 Image Codec？
- A簡: WPF 透過影像編解碼器物件，統一讀寫多種格式（RAW、JPEG、HD Photo），提供抽象化 API。
- A詳: WPF 以解碼器（BitmapDecoder）與編碼器（如 JpegBitmapEncoder）抽象化各格式處理，開發者用一致 API 讀寫影像與中繼資料。安裝相機廠的 RAW codec 後，Decoder 就能識別並解出 RAW 內容，再配合 Encoder 轉存到目標格式。這使跨格式處理與 metadata 存取擁有一致體驗。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q8, A-Q10

A-Q5: 什麼是 Canon RAW Codec？與 WPF 有何關係？
- A簡: Canon RAW Codec 是能解出 CR2 的系統編解碼器；安裝後 WPF 可用 Decoder 讀取 RAW。
- A詳: Canon 提供的 RAW codec 會註冊到系統，使支援該格式的框架（如 WPF 影像堆疊）能直接建立 BitmapDecoder 解析 CR2。文章示例中，安裝 codec 後以 BitmapDecoder.Create 指向 CR2，即可取得影格、縮圖與 metadata，再用 Encoder 轉成 JPEG，形成完整的 RAW→JPEG 流程。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, B-Q1, C-Q1

A-Q6: RAW 與 JPEG 有何差異？
- A簡: RAW 保留原始感光資料且無損；JPEG 為有損壓縮，體積小但資訊減少，後製彈性較低。
- A詳: RAW 富含感光器原始資訊、位深與相機參數，適合後製與長期保存；JPEG 經有損壓縮，雖體積小、相容性高，但會捨棄細節與動態範圍。文章觀點認為未來規格會更替，保留 RAW 可讓後續轉換保持品質，避免在舊 JPEG 上再轉而累積損失。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, B-Q18, A-Q7

A-Q7: 什麼是 HD Photo？為何值得注意？
- A簡: HD Photo 是微軟推出的新影像格式，支援廣色域等特性並與 WPF codec 集成良好。
- A詳: HD Photo（文中提及）為微軟提出的新格式，主打高動態範圍、廣色域與較佳壓縮效率。重要的是，WPF 的影像 codec 管線能保留與傳遞這些高品質資訊；若從 RAW 解出後再存 JPEG，可能喪失部分優勢。這讓 RAW→新格式的轉換更具價值，也呼應作者強調的「保留 RAW 面對未來」。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q9, B-Q18, A-Q6

A-Q8: 作者選擇 Canon G9 的關鍵因素是什麼？
- A簡: 關鍵在「再次支援 RAW」與 Canon 發佈專屬 RAW codec，便於結合 WPF 建構工作流程。
- A詳: 文中指出 G9「又」支援 RAW，加上 Canon 推出對應 codec、WPF 影像管線帶來的新優勢，促成作者升級決策。作者計畫保留 RAW、以 WPF 自動化轉檔與管理，並利用新格式（如 HD Photo）的能力，建立面向未來的照片歸檔與處理流程。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, A-Q2, C-Q9

A-Q9: WPF 與 GDI/GDI+ 的影像處理思維有何不同？
- A簡: GDI 類似「小畫家」逐像素操作；WPF 強調來源與轉換的合成流程，像 Photoshop 圖層。
- A詳: 作者形容 GDI 類應用偏像素繪製與命令式流程；WPF 以影像來源物件套疊多層轉換（如縮放、旋轉），最後合成輸出，近似 Photoshop layer 與 Flash 的場景式設計。這種抽象讓縮放、轉存、保留 metadata 等操作更一致也易封裝。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q17, A-Q13, B-Q3

A-Q10: 什麼是 BitmapDecoder？
- A簡: 它是 WPF 用於解開影像檔的類別，可從 URI/串流讀取各格式並產生影格與中繼資料。
- A詳: BitmapDecoder.Create 接受檔案位置與選項，回傳能提供 Frames、Metadata、Thumbnail 等資訊的解碼器。若已安裝特定格式的 codec（如 Canon RAW），Decoder 會自動使用之來解析 CR2，成為後續影像處理流程的資料來源。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q2, C-Q1, A-Q5

A-Q11: 什麼是 JpegBitmapEncoder？
- A簡: WPF 的 JPEG 編碼器，用於將 BitmapFrame 等輸入轉存為 JPEG 檔，並可設定品質等屬性。
- A詳: JpegBitmapEncoder 收集輸入影格（Frames）後，依照設定（如 QualityLevel）輸出 JPEG。可搭配從 RAW 解出的轉換後位圖、縮圖與 metadata，建立完整的新影格，最後寫入檔案。這是文中 CR2→JPEG 的關鍵元件。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q1, A-Q20

A-Q12: 什麼是 BitmapFrame？
- A簡: 影格是解碼後的位圖資料單元，含像素、縮圖與中繼資料，可作為編碼輸入。
- A詳: BitmapFrame 封裝一張影像（或多影格格式中的單一影格）的圖像資料、關聯的 Thumbnail 與 Metadata。WPF 讓你用 BitmapFrame.Create 將轉換後的位圖、舊縮圖、整理好的 metadata 組裝成新影格，再交由 Encoder 寫出，形成一致的轉檔流程。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, C-Q1, C-Q6

A-Q13: 什麼是 TransformedBitmap 與 ScaleTransform？
- A簡: TransformedBitmap 對來源位圖套用變換；ScaleTransform 是常見的縮放變換。
- A詳: 在 WPF 中，TransformedBitmap 接收一個 BitmapSource 與一個 Transform，將變換結果作為新的影像來源。ScaleTransform 可等比例或非等比例縮放像素，文中用 0.3 縮小圖片，以便輸出較小 JPEG。這種非破壞式的變換組裝在來源管線中，利於重複使用與封裝。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q3, C-Q1, B-Q16

A-Q14: 什麼是 Metadata/EXIF？為何重要？
- A簡: EXIF 是照片的拍攝中繼資料，如曝光、鏡頭等；保留可支援檢索、歸檔與後製。
- A詳: Metadata 泛指影像的附加資料。EXIF 是常見的攝影資訊標準，包含時間、相機參數、縮圖等。作者強調轉檔若不保留 EXIF，總覺缺失；在歸檔、搜尋與顯示（例如相機、鏡頭、時間軸）上會受影響。因此轉檔流程需將 RAW 的對應欄位正確寫入目標格式。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q15, B-Q10, C-Q2

A-Q15: 什麼是 WPF 的 Metadata Query 語法？
- A簡: 類似 XPath 的路徑字串，用以定位 metadata 節點，如 /ifd/{ushort=256}。
- A詳: WPF 將多格式 metadata 抽象化，使用 Query 字串指定項目位置。例：/ifd/{ushort=256} 表示在 IFD 區塊中，鍵值 256 的項目；而 JPEG EXIF 常見為 /app1/ifd/exif/{ushort=256}。透過 GetQuery/SetQuery 可讀寫指定欄位。這讓跨格式處理一致，但需要正確的對應關係。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q20, C-Q2

A-Q16: 什麼是 GetQuery/SetQuery？
- A簡: 它們是讀寫指定 metadata 欄位的 API，依 Query 路徑取得或設定值。
- A詳: 在 WPF 中，你先取出影像的 Metadata 物件，透過 GetQuery(路徑) 取得值，或以 SetQuery(路徑, 值) 寫入。因為不同格式的路徑差異，實務要先建立 RAW→JPEG 的對照表，再批次搬運欄位，確保 EXIF 等資訊在轉檔後仍完整。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, C-Q2, D-Q2

A-Q17: Canon RAW 與 JPEG EXIF 路徑為何會不同？
- A簡: 因其 metadata 容器與組織不同，導致 Query 路徑前綴與節點層級不一致。
- A詳: RAW 與 JPEG 的中繼資料封裝標準不同。例如文中以 /ifd/{ushort=256} 對應到 JPEG 的 /app1/ifd/exif/{ushort=256}。RAW 與 JPEG 的容器層級與段落（如 APP1）不相同，導致跨格式需要對照表來映射，否則讀寫會失敗或丟欄位。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q16, B-Q11, C-Q2

A-Q18: 什麼是 DelayCreation 與 BitmapCacheOption.None？
- A簡: DelayCreation 延遲實際解碼；CacheOption.None 不在記憶體保留快取，降低占用但需反覆讀取。
- A詳: 建立 Decoder 時可指定 DelayCreation，先建立物件、延後耗時的解碼；CacheOption.None 表示不緩存像素，減少記憶體峰值，適合批次處理。但也意味著後續取用像素時仍需解碼，對 I/O 與效能有不同影響，需依工作負載調整。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, D-Q4, C-Q5

A-Q19: 什麼是 Embedded Resource？用在此處有何好處？
- A簡: 內嵌資源是將檔案編入組件；用於隨程式攜帶 metadata 對照表，部署更單純。
- A詳: 建立 RAW→JPEG metadata 對應表後，存為 XML 並嵌入成資源，程式在執行時即可直接載入，不需額外檔案部署。這使函式庫（library）更自足、可重用，減少環境差異造成的錯誤，是穩定批次轉檔流程的好做法。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q3, B-Q12, C-Q4

A-Q20: JPEG 的 QualityLevel 是什麼？影響是什麼？
- A簡: QualityLevel 控制 JPEG 壓縮品質；值越高畫質越好、檔案越大，需取捨。
- A詳: JpegBitmapEncoder.QualityLevel 以 1–100 範圍控制壓縮，80、75 等常見值兼顧體積與品質。對批次縮圖與上傳情境，應根據目標分辨率與用途選擇品質，以免過大或畫質不足。文中示例即設定 80 與 75 做轉存。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, C-Q8, D-Q6

---

### Q&A 類別 B: 技術原理類

B-Q1: WPF 的「解碼→轉換→編碼」整體流程如何運作？
- A簡: 以 BitmapDecoder 讀來源，透過轉換組裝成 BitmapFrame，最後由 Encoder 寫出。
- A詳: 流程為：1) 用 BitmapDecoder.Create 指向檔案（可啟用 DelayCreation、CacheOption）；2) 取出 Frames[0] 與 Metadata/Thumbnail；3) 視需求用 TransformedBitmap（如 ScaleTransform）進行縮放；4) 以 BitmapFrame.Create(位圖、縮圖、metadata、其他) 組新影格；5) 用 JpegBitmapEncoder 設定 QualityLevel，Frames.Add 後 Save 到檔案。核心組件：Decoder、Transform、Frame、Encoder。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q10, A-Q11, A-Q12

B-Q2: BitmapDecoder.Create 的內部機制與選項含義？
- A簡: 它依副檔名與已安裝 codec 選擇解碼器；DelayCreation 延後解碼，CacheOption 控制快取。
- A詳: Create 會根據輸入 URI/Stream 與註冊的編解碼器解析格式，建立對應 Decoder。BitmapCreateOptions.DelayCreation 使物件先建立即後解碼，BitmapCacheOption 控制像素緩存策略（None 表示按需）。這些選項影響記憶體占用、I/O 次數與整體效能。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q18, D-Q4, C-Q5

B-Q3: TransformedBitmap 的變換流程與核心組件是什麼？
- A簡: 它接收來源位圖與 Transform，於取像時套用數學變換生成新像素。
- A詳: TransformedBitmap 將 BitmapSource 與 Transform（如 ScaleTransform）鏈接，存取像素時才計算輸出。步驟：建立 Transform→以來源與 Transform 建立 TransformedBitmap→交由 BitmapFrame.Create 包裝→Encoder 寫出。核心元件：BitmapSource、Transform、TransformedBitmap、Frame。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q16, C-Q1

B-Q4: BitmapFrame.Create 合成新影格時做了什麼？
- A簡: 它將位圖、縮圖、metadata 等組合成完整影格，供編碼器直接寫出。
- A詳: Create 接收：1) 影像來源（可為 TransformedBitmap）；2) Thumbnail；3) Metadata；4) 可選其他參數。它將視覺像素與中繼資料合併，成為 Encoder 可消費的統一單位。如此可在轉檔時同步保留縮圖與 EXIF。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q12, C-Q1, C-Q6

B-Q5: JpegBitmapEncoder 的品質控制原理是什麼？
- A簡: 透過量化矩陣與熵編碼控制壓縮程度；QualityLevel 越高壓縮越弱。
- A詳: JPEG 以 DCT、量化與熵編碼達成壓縮。QualityLevel 調整量化強度，影響高頻細節保留程度。WPF 將此以 1–100 的屬性暴露，實務上需配合輸出尺寸與用途試算合適值，以避免檔案過大或品質不足。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q20, C-Q8, D-Q6

B-Q6: WPF Metadata Query 是如何解析與定位的？
- A簡: 以路徑樣式字串逐層定位容器與鍵值，對應到內部 metadata 結構。
- A詳: Query 字串類似 XPath，節點代表容器（如 /app1/ifd/exif）與鍵（如 {ushort=256}）。GetQuery 解析路徑、進入相應節點並取回值；SetQuery 反向寫入。不同格式容器層級不同，需建立跨格式對應表才能正確存取。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, A-Q16, B-Q10

B-Q7: GetQuery/SetQuery 的流程與型別處理為何關鍵？
- A簡: 函式需找到正確節點並匹配型別（如 UShort、Rational）；型別錯誤會寫入失敗。
- A詳: 執行時先解析路徑→查找節點→讀/寫值。值需符合該欄位的資料型別與格式；雖文中未細述型別，但實務常見 UShort、Ascii、Rational 等。對照表除了路徑，也應標註型別，避免寫入例外或資料不正確。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q2, D-Q10, A-Q17

B-Q8: Canon RAW Codec 如何被 WPF 自動使用？
- A簡: 安裝後 codec 註冊於系統，Decoder 建立時依格式自動挑選對應解碼器。
- A詳: 當 Canon RAW codec 安裝至系統，格式關聯與編解碼器註冊完成。WPF 在 Create Decoder 時根據檔案格式選用可用解碼器，因此開發者僅需呼叫 BitmapDecoder.Create 指向 CR2，便可取得 Frames、縮圖與 metadata，而無須手動處理低階解碼細節。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q2, D-Q3

B-Q9: 從 RAW 保留廣色域等資訊的傳遞機制為何？
- A簡: 由 codec 解出高品質資料，透過 Frame 與 metadata 傳遞到目標格式，避免資料被提前丟棄。
- A詳: 若 RAW 內含寬廣色域或高動態範圍資訊，且 codec 能解出，WPF 的來源→轉換→合成流程會盡量保留；再輸出到支援更多色彩表現的格式時效益更大。若改存 JPEG，部分優勢會因格式限制而消失，因此流程設計要考量目標格式能力。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q7, B-Q18, A-Q2

B-Q10: 為何說 WPF 抽象化了 EXIF/IFD/XMP 的存取？
- A簡: 它以統一路徑 Query 屏蔽不同格式的容器差異，讓讀寫介面一致。
- A詳: 不同標準（EXIF、IFD、XMP）有不同的結構與存放位置。WPF 使用統一路徑字串來描述位置，並以相同 API 讀寫，降低跨格式摩擦。真正的差異由 Query 路徑與 codec 內部處理吸收，因此要解決的是路徑與對照表，而非 API 差異。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q15, A-Q17, B-Q6

B-Q11: RAW→JPEG 的 metadata 對應策略如何設計？
- A簡: 建立對照表，將 RAW 路徑對應到 JPEG 的 EXIF 路徑，轉檔時逐欄搬移。
- A詳: 先蒐集常用欄位，觀察 RAW 與 JPEG 轉檔後的 Query 路徑，建立映射（如 /ifd/{ushort=256}→/app1/ifd/exif/{ushort=256}）。轉檔流程中讀 RAW 的值→依對照表寫入 JPEG。可存成 XML 並嵌入資源，確保部署一致。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q2, A-Q19, B-Q20

B-Q12: 以 Embedded Resource 配置對照表的運作流程？
- A簡: 將 XML 內嵌到組件，執行時以資源串流載入並解析為對照資料結構。
- A詳: 編譯時把 XML 標記為嵌入資源；執行時用 Assembly.GetManifestResourceStream 讀取→載入為 XDocument/XmlDocument→建立字典（RAW 路徑→JPEG 路徑）。呼叫轉檔 API 時查表搬移值，實現零外部依賴的穩定部署。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q19, C-Q3, C-Q4

B-Q13: 縮圖（Thumbnail）如何在流程中被保留？
- A簡: 由來源 Frame.Thumbnail 取得，於 BitmapFrame.Create 時一併指定寫入目標。
- A詳: 多數格式在 metadata 或結構中帶縮圖。從 Decoder 取 Frames[0].Thumbnail，若非空則在建立新 Frame 時傳入，以保留原縮圖。如此相簿軟體或檔案總管可快速顯示縮圖，提升使用者體驗。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q12, C-Q6, D-Q9

B-Q14: URI 與 Stream 兩種輸入有何設計考量？
- A簡: URI 方便檔案導向流程；Stream 適合管線化或非檔案來源，控制生命週期更彈性。
- A詳: BitmapDecoder 可接受 URI 或 Stream。使用 URI 簡潔直觀；Stream 便於從壓縮包、網路或記憶體讀取，並可搭配 CacheOption 管控資源。選擇取決於來源型態與效能考量。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q1, D-Q8, B-Q2

B-Q15: 為何使用 Frames[0]？多影格有何意涵？
- A簡: 多數照片僅一影格，故取 0；多影格格式可能含多頁或多解析度。
- A詳: Decoder.Frames 是影像集合。相片通常只有一個主影格，因此使用 Frames[0]。特定格式可能包含多影格（如動畫、多頁文件或多解析度存放），此時應遍歷或選擇適合的影格處理。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q12, C-Q1, D-Q9

B-Q16: 路徑如 /ifd/{ushort=256} 的技術意涵？
- A簡: 指向 IFD 區塊中鍵值 256 的欄位，是以型別+鍵標註的定位方式。
- A詳: IFD（Image File Directory）中各欄位以鍵值識別，Query 使用 {ushort=256} 表示該鍵。這是抽象化定位法，無須直接解析二進位結構。對應到 JPEG 的 APP1/EXIF 容器時，需加上容器層級前綴，形成跨格式一致的語義。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q15, A-Q25, B-Q11

B-Q17: 影像處理的「來源-變換-合成」架構有何優勢？
- A簡: 非破壞、可重組、可重用；便於建立穩定的批次轉檔與封裝 API。
- A詳: 將影像視作來源（BitmapSource），透過變換（Transforms）與合成（BitmapFrame）組裝，能以少量程式碼靈活實作縮放、轉存與 metadata 保留。這種架構讓流程明確、維護容易，亦便於擴充新格式或新變換。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q3, C-Q4

B-Q18: JPEG、RAW、HD Photo 的資料完整性風險如何比較？
- A簡: RAW 最完整；HD Photo 可保較佳品質；JPEG 有損壓縮最易丟細節與色彩。
- A詳: RAW 保存最多原始資訊，後製空間最大；HD Photo（文中提及的新格式）能保留更多色彩與動態資訊；JPEG 因有損壓縮，轉存與重複處理會累積損失。轉檔設計應盡量在高品質管線中處理與保存 metadata，最後才視需求輸出到相容格式。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, A-Q7, B-Q9

B-Q19: 品質與體積該如何權衡？
- A簡: 依用途選擇輸出尺寸與 QualityLevel，測試找到可接受的畫質/容量平衡點。
- A詳: 影像體積由解析度與壓縮品質共同決定。批次縮圖時先設定合理像素上限（如 800×800），再微調 QualityLevel（如 75、80）觀察畫質與檔案大小。不同題材（雜訊、細節、平滑區）對壓縮敏感度不同，需實測取捨。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q20, C-Q8, D-Q6

B-Q20: 為什麼 RAW 與 JPEG 的 Query 前綴如 /app1/ifd/exif 不同？
- A簡: 因封裝容器不同，JPEG 多以 APP1 存 EXIF；RAW 則依自身結構組織 IFD。
- A詳: JPEG 習慣在 APP1 區段存放 EXIF，因此 Query 需要加上 /app1/ifd/exif；RAW 檔如 CR2 使用與 TIFF 類似的 IFD 結構，Query 常見簡化為 /ifd。這是容器層級差異，必須以對照表映射，避免讀/寫錯位。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q17, B-Q6, B-Q11

---

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何以 WPF 將 CR2 轉為縮小後的 JPEG？
- A簡: 用 BitmapDecoder 讀 CR2，TransformedBitmap 縮放，BitmapFrame.Create 組影格，JpegBitmapEncoder 輸出。
- A詳: 步驟：1) 安裝 Canon RAW codec；2) var dec = BitmapDecoder.Create(uri, DelayCreation, CacheNone)；3) var src = dec.Frames[0]；4) var scaled = new TransformedBitmap(src, new ScaleTransform(0.3,0.3))；5) var frame = BitmapFrame.Create(scaled, src.Thumbnail, metadata, null)；6) 設定 encoder.QualityLevel；7) Save 至檔案。程式碼：
  ```csharp
  var dec = BitmapDecoder.Create(new Uri(@"C:\IMG.CR2"),
      BitmapCreateOptions.DelayCreation, BitmapCacheOption.None);
  var enc = new JpegBitmapEncoder { QualityLevel = 80 };
  var scaled = new TransformedBitmap(dec.Frames[0], new ScaleTransform(0.3, 0.3));
  enc.Frames.Add(BitmapFrame.Create(scaled, dec.Frames[0].Thumbnail, metadata, null));
  using var fs = File.OpenWrite(@"C:\IMG.jpg"); enc.Save(fs);
  ```
  注意：確認 metadata 來源與縮圖非空。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q10, A-Q11, A-Q13

C-Q2: 如何從 RAW 複製 EXIF 到 JPEG？
- A簡: 建對照表，逐項以 GetQuery 讀 RAW、SetQuery 寫入 JPEG 的相對應路徑。
- A詳: 實作：1) 準備 RAW→JPEG Query 對照（如 /ifd/{ushort=256}→/app1/ifd/exif/{ushort=256}）；2) 取得來源 metadata；3) 建立新 BitmapMetadata("jpg")；4) 迭代對照表：若來源有值，SetQuery 寫至目標；5) 用該 metadata 建立 BitmapFrame。範例：
  ```csharp
  var srcMeta = (BitmapMetadata)dec.Frames[0].Metadata.Clone();
  var dstMeta = new BitmapMetadata("jpg");
  foreach (var map in mappings)
  {
      if (srcMeta.ContainsQuery(map.Raw)) dstMeta.SetQuery(map.Jpeg, srcMeta.GetQuery(map.Raw));
  }
  var frame = BitmapFrame.Create(scaled, src.Thumbnail, dstMeta, null);
  ```
  注意型別相容性與例外處理。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q15, A-Q16, B-Q11

C-Q3: 如何建立 metadata 對照表並做成 Embedded Resource？
- A簡: 以 XML 定義 RAW→JPEG 的 Query 映射，內嵌到組件並在執行時載入解析。
- A詳: 步驟：1) 建立 mappings.xml，內容含 <raw path> 與 <jpeg path>；2) 專案屬性設為「內嵌資源」；3) 執行時用 Assembly.GetManifestResourceStream 讀入並解析；4) 轉檔時查表搬移 metadata。注意：維護常見欄位，並在測試照片上驗證。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, B-Q11, D-Q2

C-Q4: 如何封裝成函式庫 ImageUtil.SaveToJPEG？
- A簡: 提供輸入路徑、輸出路徑、寬高與品質參數，內部完成讀、縮、轉、寫與 EXIF 搬移。
- A詳: 介面：
  ```csharp
  public static void SaveToJPEG(string src, string dst, int maxW, int maxH, int quality)
  ```
  實作：1) 用 Decoder 讀 RAW；2) 計算縮放比，建立 TransformedBitmap；3) 複製縮圖與 metadata（依對照表）；4) 建 Frame；5) 設定 JpegBitmapEncoder.QualityLevel 後 Save。注意例外處理與資源釋放。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, C-Q2, A-Q19

C-Q5: 如何選擇 DelayCreation 與 CacheOption？
- A簡: 大量批次時用 DelayCreation、CacheNone 降記憶體；頻繁重用像素時考慮快取以減 I/O。
- A詳: 若每張圖僅讀一次並立即轉存，DelayCreation+CacheNone 可降低峰值記憶體；若需重複取像或多步處理，採用 OnLoad（快取）可減少重解碼成本。依檔案大小、批次量與硬碟/CPU 平衡調整。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q18, B-Q2, D-Q4

C-Q6: 如何保留與寫入縮圖（Thumbnail）？
- A簡: 取 source.Frames[0].Thumbnail，於 BitmapFrame.Create 時傳入，若為 null 則可忽略。
- A詳: 1) var thumb = srcFrame.Thumbnail；2) 若 thumb != null，Create(frame) 時作為第二參數；3) 某些來源無縮圖，需容錯。這能讓檔案總管快取縮圖、加速瀏覽。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q13, A-Q12, D-Q9

C-Q7: 如何驗證輸出 JPEG 是否含 EXIF？
- A簡: 重新以 BitmapDecoder 讀輸出檔，檢查 Metadata 與常見 Query 是否存在。
- A詳: 步驟：1) 用 Decoder.Create 讀輸出 JPEG；2) 取 frame.Metadata；3) 測幾個關鍵欄位（如 /app1/ifd/exif/{ushort=…}）；4) 若缺失，檢查對照表映射與 SetQuery 是否成功。亦可用外部檢視器交叉驗證。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: D-Q1, D-Q2, A-Q14

C-Q8: 如何設定輸出尺寸與 QualityLevel 的平衡？
- A簡: 先限制最長邊（如 800px），再調整 QualityLevel（75–80）檢視畫質與體積。
- A詳: 1) 計算縮放比：min(maxW/srcW, maxH/srcH)；2) 用 ScaleTransform 建立 TransformedBitmap；3) 設 QualityLevel=75/80 測試；4) 比較檔案大小與可視品質。依用途定案：網頁分享偏小、列印偏大。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q19, A-Q20, D-Q6

C-Q9: 如何規劃自動歸檔與批次縮圖流程？
- A簡: 封裝通用 API，迭代資料夾檔案，轉存並搬移 EXIF，輸出到結構化目錄。
- A詳: 1) 以檔案列舉取得 RAW；2) 呼叫 SaveToJPEG 轉出目標尺寸與品質；3) 依 EXIF 時間/相機建立目錄；4) 記錄失敗與缺欄位；5) 加入單元測試覆蓋常見機型。確保流程重現性與可維護性。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q8, C-Q4, D-Q1

C-Q10: 如何在專案中引用並使用轉檔函式庫？
- A簡: 新建 class library，暴露 API；在應用加入引用，於程式中呼叫轉檔入口方法。
- A詳: 1) 建立 .NET 類別庫專案（包含對照表資源）；2) 提供靜態方法 ImageUtil.SaveToJPEG；3) 應用專案加入對該 DLL 引用；4) 在 UI/CLI 觸發批次轉檔；5) 以設定檔控制輸出參數，便於調整與重用。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q4, A-Q19, C-Q9

---

### Q&A 類別 D: 問題解決類（10題）

D-Q1: 轉出的 JPEG 沒有 EXIF 怎麼辦？
- A簡: 檢查 metadata 搬移流程：對照表、Get/SetQuery、目標 metadata 型別與 Frame 組裝。
- A詳: 症狀：輸出檔 Metadata 為空或僅部分欄位。可能原因：未建立對照表、路徑錯誤、未建立正確目標 Metadata、未在 Frame.Create 傳入、SetQuery 型別不符。解法：建立/校正對照表；確認 src.ContainsQuery→dst.SetQuery；用 BitmapMetadata("jpg")；重新組裝 Frame。預防：加入驗證與單元測試。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q2, C-Q7, B-Q11

D-Q2: GetQuery 擲出「找不到路徑」如何處理？
- A簡: 路徑不正確或欄位不存在；比對對照表與來源含有的實際欄位，必要時跳過。
- A詳: 症狀：GetQuery/ContainsQuery 失敗。原因：RAW 與 JPEG 容器路徑不同、機型差異導致欄位缺失。解法：先用 ContainsQuery 檢查再讀；校正對照表；為缺欄位設預設或跳過。預防：用日誌記錄缺欄位，逐步完善對照表。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, B-Q6, C-Q3

D-Q3: 無法讀取 CR2，Decoder 建立失敗怎麼辦？
- A簡: 多半未安裝 Canon RAW codec 或版本不相容；安裝/更新後重試。
- A詳: 症狀：BitmapDecoder.Create 擲例外或 Frames 為空。原因：系統無對應 codec、檔案損毀。解法：安裝官方 Canon RAW codec，或更新至支援該機型版本；確認檔案可於其他檢視器開啟。預防：在部署需求中列出必要 codec。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, B-Q8, C-Q1

D-Q4: 轉檔效能不佳的可能原因與改善？
- A簡: 受解碼、縮放與 I/O 影響；調整 CacheOption、批次策略與品質/尺寸參數。
- A詳: 症狀：轉檔速度慢。可能原因：大檔 RAW 解碼耗時、重複讀取像素、硬碟 I/O 限制。解法：一次性處理像素（避免重覆解碼）、視情況使用快取模式、降低輸出解析度/品質、批次處理時控管並行度。預防：量測瓶頸並針對性優化。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q18, C-Q5, B-Q2

D-Q5: 縮放後影像顯得模糊，如何改善？
- A簡: 調整縮放比例與流程，避免重複縮放；一次完成目標尺寸並檢視品質設定。
- A詳: 症狀：輸出影像偏糊。原因：縮放比例過小、重複縮放、原檔雜訊與壓縮。解法：計算一次性縮放至目標尺寸；避免多次縮放；提高輸出 QualityLevel；必要時調整目標像素。預防：建立固定比例與測試案例。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q8, B-Q3, B-Q19

D-Q6: 檔案過大或過小，如何調整？
- A簡: 透過輸出解析度與 QualityLevel 雙向調整，並以實測驗證最終效果。
- A詳: 症狀：檔案尺寸不符預期。原因：輸出尺寸與品質搭配不當。解法：先設定目標最長邊，再以 5–10 為步進調整 QualityLevel 比較畫質與體積。預防：針對不同用途（網頁/列印）建立建議組合。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q20, C-Q8, B-Q19

D-Q7: 轉檔後部分 EXIF 欄位不見的原因？
- A簡: 對照表不完整、欄位不存在或型別不符；補齊映射並加強容錯。
- A詳: 症狀：某些欄位缺失。原因：RAW 與 JPEG 路徑差異未覆蓋、不同機型欄位差異、SetQuery 型別錯誤。解法：比對實拍樣本補完對照；在搬移前後記錄與驗證；處理不同型別寫入。預防：持續更新對照表並單元測試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, C-Q2, C-Q7

D-Q8: 讀檔路徑或 URI 問題如何診斷？
- A簡: 確認路徑正確、權限足夠；必要時改用 FileStream 與 try/catch 詳列錯誤。
- A詳: 症狀：Create 失敗或找不到檔案。原因：路徑錯誤、無權限、文件被占用。解法：檢查 Uri 格式、使用絕對路徑、測試以 Stream 輸入；加入完整錯誤日誌。預防：在程式中統一路徑處理與權限檢查。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q14, C-Q1, C-Q10

D-Q9: 當來源 Thumbnail 為 null 時如何處理？
- A簡: 容錯忽略或自行產生縮圖；不影響主影像輸出。
- A詳: 症狀：Frame.Thumbnail 為 null。原因：來源未內嵌縮圖或被移除。解法：Create 時傳入 null 即可；如需縮圖，另行產生並嵌入。預防：流程中允許縮圖缺失不致失敗。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q13, C-Q6, C-Q1

D-Q10: Metadata 寫入失敗（型別錯誤）怎麼辦？
- A簡: 確認目標欄位型別，轉換值型別後再 SetQuery；必要時跳過不相容欄位。
- A詳: 症狀：SetQuery 擲例外。原因：資料型別不符欄位需求。解法：查對照表或來源欄位型別，進行格式轉換（如數值、字串、分數）；加上 try/catch 與白名單欄位策略。預防：在對照表中增加型別資訊與驗證。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q7, C-Q2, D-Q7

---

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 RAW 檔與「RAW 支援」？
    - A-Q2: 為什麼保留 RAW 對未來更有保障？
    - A-Q3: 什麼是 WPF（Windows Presentation Foundation）？
    - A-Q4: 什麼是 WPF 的 Image Codec？
    - A-Q5: 什麼是 Canon RAW Codec？與 WPF 有何關係？
    - A-Q6: RAW 與 JPEG 有何差異？
    - A-Q7: 什麼是 HD Photo？為何值得注意？
    - A-Q10: 什麼是 BitmapDecoder？
    - A-Q11: 什麼是 JpegBitmapEncoder？
    - A-Q12: 什麼是 BitmapFrame？
    - A-Q13: 什麼是 TransformedBitmap 與 ScaleTransform？
    - A-Q14: 什麼是 Metadata/EXIF？為何重要？
    - B-Q1: WPF 的「解碼→轉換→編碼」整體流程如何運作？
    - C-Q1: 如何以 WPF 將 CR2 轉為縮小後的 JPEG？
    - C-Q7: 如何驗證輸出 JPEG 是否含 EXIF？

- 中級者：建議學習哪 20 題
    - A-Q9: WPF 與 GDI/GDI+ 的影像處理思維有何不同？
    - A-Q15: 什麼是 WPF 的 Metadata Query 語法？
    - A-Q16: 什麼是 GetQuery/SetQuery？
    - A-Q17: Canon RAW 與 JPEG EXIF 路徑為何會不同？
    - A-Q18: 什麼是 DelayCreation 與 BitmapCacheOption.None？
    - A-Q19: 什麼是 Embedded Resource？用在此處有何好處？
    - A-Q20: JPEG 的 QualityLevel 是什麼？影響是什麼？
    - B-Q2: BitmapDecoder.Create 的內部機制與選項含義？
    - B-Q3: TransformedBitmap 的變換流程與核心組件是什麼？
    - B-Q4: BitmapFrame.Create 合成新影格時做了什麼？
    - B-Q6: WPF Metadata Query 是如何解析與定位的？
    - B-Q11: RAW→JPEG 的 metadata 對應策略如何設計？
    - B-Q12: 以 Embedded Resource 配置對照表的運作流程？
    - B-Q13: 縮圖（Thumbnail）如何在流程中被保留？
    - B-Q19: 品質與體積該如何權衡？
    - C-Q2: 如何從 RAW 複製 EXIF 到 JPEG？
    - C-Q3: 如何建立 metadata 對照表並做成 Embedded Resource？
    - C-Q4: 如何封裝成函式庫 ImageUtil.SaveToJPEG？
    - C-Q8: 如何設定輸出尺寸與 QualityLevel 的平衡？
    - D-Q1: 轉出的 JPEG 沒有 EXIF 怎麼辦？

- 高級者：建議關注哪 15 題
    - B-Q5: JpegBitmapEncoder 的品質控制原理是什麼？
    - B-Q7: GetQuery/SetQuery 的流程與型別處理為何關鍵？
    - B-Q8: Canon RAW Codec 如何被 WPF 自動使用？
    - B-Q9: 從 RAW 保留廣色域等資訊的傳遞機制為何？
    - B-Q10: 為何說 WPF 抽象化了 EXIF/IFD/XMP 的存取？
    - B-Q14: URI 與 Stream 兩種輸入有何設計考量？
    - B-Q15: 為何使用 Frames[0]？多影格有何意涵？
    - B-Q16: 路徑如 /ifd/{ushort=256} 的技術意涵？
    - B-Q17: 影像處理的「來源-變換-合成」架構有何優勢？
    - B-Q18: JPEG、RAW、HD Photo 的資料完整性風險如何比較？
    - B-Q20: 為什麼 RAW 與 JPEG 的 Query 前綴如 /app1/ifd/exif 不同？
    - C-Q5: 如何選擇 DelayCreation 與 CacheOption？
    - D-Q4: 轉檔效能不佳的可能原因與改善？
    - D-Q7: 轉檔後部分 EXIF 欄位不見的原因？
    - D-Q10: Metadata 寫入失敗（型別錯誤）怎麼辦？