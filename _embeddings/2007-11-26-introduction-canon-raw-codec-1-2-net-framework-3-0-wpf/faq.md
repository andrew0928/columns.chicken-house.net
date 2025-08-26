# 前言: Canon Raw Codec 1.2 + .NET Framework 3.0 (WPF)

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 Canon Raw Codec 1.2？
- A簡: Canon 在 Windows 上的 RAW 編解碼，讓 XP/Vista 能預覽與讀取 .CR2，並供應用程式（含 WPF）使用。
- A詳: Canon Raw Codec 1.2 是 Canon 在 Windows 上提供的影像編解碼元件，安裝後可使 XP/Vista 檔案總管、相簿與應用程式直接顯示支援機種的 .CR2 RAW 縮圖、預覽與部分中繼資料。對於 WPF（.NET 3.0）而言，它讓 WPF 能透過系統編解碼層載入 CR2、取得影像與 EXIF/IFD 中繼資料，成為自動化處理與工具開發的基礎。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q5, B-Q7

A-Q2: .CR2 與 .CRW 是什麼？有何差異？
- A簡: 都是 Canon RAW 格式；.CR2 較新、基於 TIFF/IFD；.CRW 較舊、部分軟體相容性較差。
- A詳: .CR2 與 .CRW 皆為 Canon 的 RAW 檔。CR2 為較新格式，常見於 G9 等機種，結構接近 TIFF/IFD，支援較多標籤；CRW 為較舊格式，部分管線（如 WPF）可能在特定版本組合下產生例外，而 Microsoft 的 viewer 可能能正常顯示，顯示出「同檔不同管線」的相容性差異。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: D-Q5, B-Q11, A-Q12

A-Q3: 什麼是 WPF（.NET 3.0）？
- A簡: 微軟的桌面 UI 框架，支援向量圖形、媒體與影像處理，提供影像與中繼資料 API。
- A詳: WPF（Windows Presentation Foundation）是 .NET 3.0 的 UI 框架，整合向量繪圖、動畫、媒體與影像。其影像 API 能載入多種格式、取得 BitmapSource/BitmapFrame、讀寫 BitmapMetadata，並提供「Metadata Query Language」以查詢 EXIF/IFD 標籤，便於在應用中呈現 RAW/JPEG 的中繼資料。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, A-Q6, A-Q7

A-Q4: 什麼是 EXIF？為何重要？
- A簡: 影像中繼資料標準，存放拍攝參數、相機資訊、時間等，利於整理與自動化。
- A詳: EXIF 是影像交換格式中廣泛使用的中繼資料標準，記錄相機型號、鏡頭、曝光、白平衡、拍攝時間、軟體等資訊。對相片整理、搜尋、歸檔與批次處理相當關鍵。RAW 與 JPEG 多以 IFD 結構存取這些標籤，但不同容器（RAW/JPG）與廠商實作會有差異，影響程式的存取方式。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, B-Q8, C-Q7

A-Q5: 為什麼需要安裝廠商 RAW codec？
- A簡: 讓系統與應用程式能解碼顯示 RAW，存取其中繼資料，提供一致的開發基礎。
- A詳: Windows 與 WPF 會透過安裝於系統的編解碼器解析影像。未安裝 Canon RAW codec 時，CR2 可能無法顯示或取不到中繼資料；安裝後，Shell 與應用程式共享同一解碼能力。這提供一致的顯示與資料存取行為，是建構自動化流程與工具（如批次轉檔、歸檔器）的前提。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, C-Q8, D-Q10

A-Q6: WPF 的「Metadata Query Language」是什麼？
- A簡: 一套查詢字串語法，類似 XPath，用於讀寫 IFD/EXIF 中繼資料。
- A詳: WPF 提供 Metadata Query Language，讓開發者用路徑式字串（如「/ifd/{ushort=xxxx}」）透過 GetQuery/SetQuery 讀寫標籤。其概念類似 XPath 對 XML，屏蔽底層容器細節，統一以字串路徑定位標籤。然而，不同格式（CR2/JPG）實際可用路徑常不同，需先列舉或查表才能正確使用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q4, C-Q3

A-Q7: 為何 BitmapSource.Metadata 會是 null？
- A簡: 版本設計所限；WPF 3.0 不提供 BitmapSource 層級中繼資料，改從 Frame 取得。
- A詳: 在 .NET 3.0/WPF，BitmapSource.Metadata 可能為 null，因為當前版本不提供來源層級中繼資料；實際可用資訊存在 BitmapFrame.Metadata。需先由解碼器取得 Frames，再從特定 Frame 的 BitmapMetadata 讀取或修改，避免直接從 BitmapSource 取值造成誤判為「沒有中繼資料」。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, C-Q10, D-Q1

A-Q8: 什麼是 BitmapFrame？為何與 Metadata 有關？
- A簡: 影像的幀表示；每個 Frame 有自己的 BitmapMetadata，儲存 EXIF/IFD。
- A詳: BitmapFrame 表示解碼後影像的單一幀（多幀格式如 TIFF/GIF 可能有多幀）。WPF 在 Frame 級附帶 BitmapMetadata，包含 EXIF/IFD 等中繼資料。由於 BitmapSource 層不提供 Metadata，正確作法是從 BitmapDecoder.Frames[n].Metadata 取得與操作中繼資料。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q1, C-Q2

A-Q9: 什麼是 BitmapMetadata？
- A簡: WPF 影像中繼資料的物件模型，支援 GetQuery/SetQuery 與列舉鍵。
- A詳: BitmapMetadata 封裝影像的中繼資料，提供字串鍵值的查詢/設定介面（GetQuery/SetQuery）。其實作 IEnumerable<string>，可直接用 foreach 列舉可用的查詢鍵，對探索不同格式（CR2/JPG）的實際可用標籤很有用。修改後可附加至編碼器輸出，達到中繼資料保留或變更。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, C-Q3, C-Q4

A-Q10: 什麼是 GetQuery/SetQuery？
- A簡: 以查詢字串讀/寫中繼資料鍵的 API，是 WPF 存取 EXIF 的基礎。
- A詳: GetQuery 透過查詢字串讀取某個中繼資料鍵的值，SetQuery 則寫入值。查詢路徑需符合格式實際的 IFD 位置與標籤，否則會回傳 null 或拋例外。對於 RAW/JPG 的差異，先列舉現有鍵再讀寫可提升成功率，亦可建立對應表抽象出差異。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q2, C-Q2

A-Q11: 為何 WPF 內建可直接讀的 Metadata 欄位很少？
- A簡: 物件層級的屬性僅暴露少數欄位；完整 EXIF 需用 Query 語法存取。
- A詳: WPF 在物件層面僅提供少數常見欄位（如 ApplicationName、CameraModel 等），數量不到十個。其設計讓開發者透過 Metadata Query Language 以鍵路徑存取完整 EXIF/IFD。這避免API過度膨脹，但也意味著需靠查詢與列舉才能取得大多數標籤。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q14, C-Q2

A-Q12: .CR2 與 .JPG 的 Metadata Query 有何差異？
- A簡: 路徑與標籤對應不同；需先列舉鍵或建立對照，才能正確讀寫。
- A詳: 雖同為 EXIF/IFD 概念，CR2（RAW 容器）與 JPG（APP1/EXIF 容器）的實際查詢路徑往往不同，導致同名欄位的鍵不一致。實務上先列舉 BitmapMetadata 的鍵，得知實際可用路徑，再以對照表支援多格式，避免硬編路徑在不同檔案上失敗。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, B-Q12, C-Q7

A-Q13: 什麼是 InPlaceMetadataWriter？
- A簡: 嘗試在原檔上直接更新中繼資料的機制，但常受格式/解碼器限制。
- A詳: InPlaceMetadataWriter 允許在不重存影像像素的前提下，直接修改檔內中繼資料。其可用性受制於格式是否支援就地更新、檔案開啟模式與編解碼器實作。實務遇到不生效或拋例外時，可退回「複製 metadata＋重新編碼」的方式達成需求。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q7, C-Q4, D-Q2

A-Q14: 為什麼需要「列舉所有可用的 Metadata Query」？
- A簡: 因文件未列出完整鍵，且不同格式差異大；列舉才能確知可用標籤。
- A詳: 官方文件未提供完整的 Query 鍵清單，加上 CR2/JPG 差異顯著，若不先列舉，極易出現讀不到或寫錯目標的情況。BitmapMetadata 實作 IEnumerable<string>，能直接 foreach 得到現有鍵，搭配值型別與樣本比對，建立可靠的讀寫對照。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q4, C-Q3, D-Q7

A-Q15: Canon Codec 效能議題的核心是什麼？
- A簡: 解碼速度慢且難以吃滿多核，導致批次處理時間長、CPU 利用率低。
- A詳: 文中量測顯示，G9 的 4000×3000、約 15MB 的 CR2 全幅解開並以 JpegEncoder 100% 儲存，在 Core2Duo E6300 環境竟需約 80 秒。雙核僅 50–60% 使用率，顯示編解碼器難以多執行緒化，成為整體瓶頸。需靠流程調度與平行非解碼工作來彌補。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q3, D-Q4, B-Q10

A-Q16: 多核心 CPU 為何未被充分利用？
- A簡: 編解碼器單執行緒或內部序列化，外層多執行緒也難以提升。
- A詳: 即使開兩個工作執行緒處理不同檔案，若底層編解碼器內部序列化或含全域鎖，仍無法讓兩個解碼同時跑滿，導致 CPU 使用率停在 50–60%。改善方向包含：將 I/O、編碼、縮圖等與解碼分離並行，或挑選更佳效能的編解碼器。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, C-Q6, D-Q4

A-Q17: 為什麼改採「Clone Metadata 後再寫入編碼器」？
- A簡: InPlace 修改不穩定；複製後隨編碼輸出較可靠，跨格式相容性高。
- A詳: 由於 InPlaceMetadataWriter 在多數情境下不可用或不穩定，採用 metadata.Clone() 取得可寫副本，修改後附加到編碼器輸出的方式更實務。此法雖需重存檔案，但流程明確、錯誤少，並可同時控制輸出格式、品質與中繼資料完整保留或更新。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q4, D-Q2, B-Q21

A-Q18: 什麼是 RAW 處理自動化？為何需要？
- A簡: 以程式批次解碼、縮圖、寫入 EXIF 與歸檔，提升效率與一致性。
- A詳: 自動化指以工具批量處理 RAW：讀取檔案、擷取與修改 EXIF、縮圖、輸出 JPEG、歸檔與命名。面對大量檔案，人工操作易錯且耗時。透過 WPF＋Codec＋Metadata Query，能打造可重複、可監控的流程，並因應 CR2/JPG 差異建立對照，提高可靠性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q5, C-Q7, D-Q9

A-Q19: 文中規劃了哪些專案？
- A簡: 一個 Image Resizer 與一個記憶卡歸檔工具，支援 RAW 流程。
- A詳: 作者計畫提供兩個專案：Image Resizer（進行縮放、轉檔、寫入中繼資料），以及「記憶卡歸檔工具」（自動歸檔、命名、管理相片，早期已有版本，將續更）。兩者皆依賴 Canon Codec 與 WPF 的影像/中繼資料 API，解決批次處理與整理需求。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q5, C-Q7, D-Q8

A-Q20: 測試環境與條件為何？
- A簡: Core2Duo E6300、2GB RAM、XP MCE2005 SP2；G9 CR2 4000×3000/約15MB。
- A詳: 文中量測於 Core2Duo E6300（2GB RAM）與 Windows XP MCE 2005 SP2 上執行，影像為 Canon G9 產生的 .CR2，尺寸約 4000×3000、檔案約 15MB。全幅解碼再以 100% 品質 JPEG 輸出約需 80 秒，CPU 使用率 50–60%，顯示編解碼器成效瓶頸。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q15, D-Q3, B-Q17

---

### Q&A 類別 B: 技術原理類

B-Q1: WPF 如何載入影像並讀取 Metadata？
- A簡: 用 BitmapDecoder 載入，從 Frames 取得 BitmapMetadata，再以 Query 讀值。
- A詳: 原理與流程：1) 開啟檔案串流；2) 建立對應的 BitmapDecoder；3) 透過 decoder.Frames 取得 BitmapFrame；4) 從 frame.Metadata 取得 BitmapMetadata；5) 以 GetQuery 讀取欄位。核心組件包含 BitmapDecoder、BitmapFrame、BitmapMetadata 與編解碼器（Canon Codec）。這條路徑繞過 BitmapSource.Metadata 為 null 的限制。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q7, A-Q8, C-Q2

B-Q2: Metadata Query 的解析機制是什麼？
- A簡: 以路徑字串對應 IFD/EXIF 樹，解析到實際標籤位址並讀寫值。
- A詳: 查詢字串如「/ifd/{ushort=xxxx}」會被解析器拆解為節點，逐層定位 IFD、子 IFD、索引或鍵，最終映射到影像中繼資料區塊的偏移與型別。成功與否取決於容器布局與解碼器實作。關鍵步驟：解析路徑、定位節點、型別轉換、值回傳/寫入。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, A-Q10, C-Q3

B-Q3: 為何 Metadata 存在於 Frame，而非 BitmapSource？
- A簡: 設計將多幀格式的資料綁在 Frame；來源層不保證提供。
- A詳: 多幀容器（如 TIFF/GIF）各幀可能有不同中繼資料，WPF 將中繼資料與 Frame 綁定更符合語意。BitmapSource 抽象層則不保證有中繼資料，因此 Metadata 可能為 null。實務上應先取得特定 Frame，再從其 Metadata 操作，確保正確性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, A-Q8, C-Q10

B-Q4: BitmapMetadata 為何能列舉 Query 鍵？
- A簡: 其實作 IEnumerable<string>，foreach 可取出現存鍵路徑。
- A詳: BitmapMetadata 內部維護已存在的中繼資料鍵集合，並透過 IEnumerable<string> 讓開發者用 foreach 直接列舉。流程：取得 frame.Metadata 為 BitmapMetadata；在 foreach(var key in metadata) 中逐鍵檢視，配合 GetQuery(key) 得知值與型別，建構動態映射。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q3, A-Q14, D-Q7

B-Q5: 如何用 GetQuery 正確讀取 EXIF 欄位？
- A簡: 先列舉現有鍵，再以確定存在的路徑呼叫 GetQuery 取值。
- A詳: 步驟：1) 取得 BitmapMetadata；2) foreach 列舉鍵，找出關鍵欄位（如相機型號、拍攝時間）；3) 用 GetQuery(鍵) 讀值；4) 轉型。核心組件：BitmapFrame、BitmapMetadata。先列舉可避免不同容器下路徑不一致的問題，提高成功率。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q2, C-Q3, A-Q12

B-Q6: 如何用 SetQuery 修改 EXIF 欄位？
- A簡: 以可寫 BitmapMetadata 呼叫 SetQuery，再附加於編碼器輸出。
- A詳: 流程：1) 由原始 frame.Metadata.Clone() 取得可寫副本；2) 以 SetQuery(鍵, 值) 修改；3) 建立對應編碼器（如 JpegBitmapEncoder）；4) 建 Frame 並指定 Metadata；5) 儲存。注意：直接 InPlace 修改常失敗，重編碼方式較穩定。需留意鍵型別與格式支援。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q4, A-Q13, D-Q8

B-Q7: InPlaceMetadataWriter 的機制與限制？
- A簡: 嘗試就地改寫；受格式、空間與權限限制，常不可用。
- A詳: InPlaceMetadataWriter 要求檔案可隨機寫入、容器預留/可擴充中繼資料空間、解碼器支援就地寫。若任一條件不滿足，會失敗或拋例外。步驟通常是開啟可寫串流、建立 writer、SetQuery、Commit。若不成功，建議採用重編碼。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q13, D-Q2, C-Q4

B-Q8: CR2 與 JPG EXIF 對應不一致的技術原因？
- A簡: 容器與 IFD 佈局不同、廠商自訂標籤，導致路徑與鍵名差異。
- A詳: 雖都以 IFD 描述中繼資料，JPG 主要透過 APP1/EXIF 區塊，而 CR2 為 RAW 容器，子 IFD 與廠商自訂（MakerNote）差異大。解碼器可能以不同節點呈現，導致 Query 路徑不一致。透過列舉與對照可抽象差異，避免硬編固定路徑。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, C-Q7, D-Q6

B-Q9: JpegBitmapEncoder 的品質與輸出機制？
- A簡: 以 QualityLevel 控制壓縮品質；Frame 與 Metadata 一併寫出。
- A詳: JpegBitmapEncoder 透過 Frames 集合接收輸出幀，並可設定 QualityLevel（0–100）。將 BitmapFrame（含像素與 BitmapMetadata）加入後 Save，即輸出 JPEG 與對應中繼資料。高品質提高時間與檔案大小，需平衡效能與需求。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q4, D-Q3, A-Q15

B-Q10: 編解碼器如何決定解碼效能與多執行緒表現？
- A簡: 內部演算法與同步策略決定是否能併行，影響 CPU 利用率。
- A詳: 編解碼器掌握像素解碼的演算法、緩衝與鎖；若其內部為單執行緒或含全域鎖，外層多工無法讓多個解碼並行，導致 CPU 無法跑滿。效能取決於解碼複雜度、I/O、最佳化與併行設計。應用端可平行其他工作來填補空檔。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, A-Q16, C-Q6

B-Q11: 為何 Microsoft viewer 能看 CRW，但 WPF 會丟例外？
- A簡: 兩者走不同顯示/解碼管線；相依的解碼器或設定可能不同。
- A詳: Shell viewer 與 WPF 可能連結至不同的解碼路徑或版本、套用不同相容性旗標；某些舊格式（如 CRW）在其中一條管線獲得特殊處理而能顯示，另一條則失敗。根因可能是解碼器差異、檔案特例、權限或 API 限制。需以記錄與替代路徑偵錯。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: D-Q5, A-Q2, B-Q19

B-Q12: 如何建立跨格式的 Metadata 對應表？
- A簡: 先列舉鍵，萃取目標欄位，建立 CR2/JPG 鍵對鍵映射。
- A詳: 以多筆 CR2/JPG 樣本：1) 列舉各自鍵；2) 以欄位值（如相機型號、日期）比對對應關係；3) 建立鍵對鍵對照；4) 程式依檔案格式或鍵存在性選用適當路徑。此法可兼容差異並降低硬編路徑風險。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q7, A-Q12, D-Q6

B-Q13: 批次影像處理的管線化原理？
- A簡: 分離 I/O、解碼、處理、編碼並行化，提升吞吐量。
- A詳: 將工作拆為取檔（I/O）、解碼（CPU/Codec）、處理（縮放/標註）、編碼（CPU/磁碟）。使用佇列在階段間傳遞，讓可並行的步驟同時進行，填滿因單一階段瓶頸造成的空檔。調整每階段並行度以最佳化整體吞吐。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q6, A-Q15, D-Q9

B-Q14: 內建屬性少，如何完整存取 EXIF？
- A簡: 透過 Query 語法讀寫，並以列舉確認可用鍵與型別。
- A詳: 物件層的屬性僅涵蓋少數欄位；完整存取需依靠 Query。步驟：從 Frame 拿到 BitmapMetadata；列舉鍵；用 GetQuery 讀值；必要時 SetQuery 寫值；最後附加到編碼器輸出。這種方式能跨越容器差異與文件缺漏。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q11, C-Q3, C-Q4

B-Q15: 為何「先列舉再存取」能降低錯誤？
- A簡: 先知道「有什麼」再讀寫，避免路徑猜測導致 null 或例外。
- A詳: 不同檔案的標籤與路徑不一致，若硬編路徑，易頻繁遇到 null 或 Key 不存在。列舉現有鍵相當於取樣檔內實際布局，存取更具針對性；搭配對照表可提升跨格式成功率並簡化偵錯。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q14, C-Q3, D-Q7

B-Q16: 為何 BitmapSource.Metadata 設計為可能為空？
- A簡: 來源層抽象化，並非每種來源都有統一的中繼資料。
- A詳: BitmapSource 抽象各種來源（檔案、串流、即時來源），未必都有一致中繼資料模型；將 Metadata 綁在 Frame 更符合容器語意。這設計帶來彈性，但要求開發者改從 Frames 管道取得資料。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q3, C-Q10

B-Q17: 如何評估解碼與編碼的時間占比？
- A簡: 量測各階段耗時，拆解為 I/O、解碼、處理、編碼。
- A詳: 在管線中記錄時間戳：讀檔開始/結束、解碼開始/結束、處理開始/結束、編碼開始/結束。彙整統計可發現瓶頸（文中解碼佔大宗且多核未跑滿）。據此調整並行度與品質參數，或更換編解碼器。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: D-Q3, B-Q13, C-Q5

B-Q18: 何謂「把不相干的 job 排在一起」的原理？
- A簡: 將可平行且不互相阻塞的工作併行，以吃滿 CPU 與 I/O。
- A詳: 當解碼受限於單執行緒時，將 I/O、CPU 輕重不同的任務與解碼並行，可利用剩餘核心與磁碟頻寬，提高整體吞吐。例：一邊縮圖/寫檔，一邊排隊解碼下一張，避免待機時間。
- 難度: 初級
- 學習階段: 進階
- 關聯概念: A-Q16, C-Q6, D-Q4

B-Q19: WPF 與作業系統 Codec 的相依如何影響行為？
- A簡: WPF 倚賴系統已安裝的編解碼器，功能與相容性取決於其版本。
- A詳: 影像能否載入、支援的格式、可讀/可寫的中繼資料，都取決於系統層的編解碼器。不同版本或不同供應商實作會造成效能與相容性差異（如 CRW 在 viewer 可見、WPF 失敗）。部署時需檢查並鎖定對應版本。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q10, C-Q8, B-Q11

B-Q20: 內建少數屬性如何定位與用途？
- A簡: 如 CameraModel、ApplicationName 等，作為快速取用，但不涵蓋全部 EXIF。
- A詳: WPF 暴露少量常用屬性（相機型號、應用程式名等）便於快速顯示，但完整工作（批次歸檔、規則標記）仍須 Query。實務中以內建屬性作為「入口驗證」，再轉用 Query 讀取其餘欄位。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q14, C-Q2

---

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何在 WPF 載入 CR2 並顯示？
- A簡: 用 BitmapDecoder 讀檔、取第一個 Frame 建立 ImageSource 顯示。
- A詳: 實作步驟：1) FileStream fs = File.OpenRead(path)；2) BitmapDecoder dec = BitmapDecoder.Create(fs, ...)；3) BitmapFrame frame = dec.Frames[0]；4) image.Source = frame。關鍵程式碼片段：建立 Decoder、取 Frames[0]。注意：需已安裝 Canon Raw Codec；例外時以 try/catch 記錄詳細訊息，確認編解碼器是否可用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, C-Q8, D-Q5

C-Q2: 如何從 BitmapFrame 讀取相機型號（CameraModel）？
- A簡: 取得 frame.Metadata，列舉或直接用已知鍵呼叫 GetQuery。
- A詳: 步驟：1) var meta = (BitmapMetadata)frame.Metadata；2) 先 foreach(var k in meta) 檢視鍵；3) 用 meta.GetQuery(鍵) 讀值。程式碼片段：object v = meta.GetQuery(某鍵)；string model = v?.ToString()。注意：不同格式鍵不同，先列舉再存取；若 meta 為 null，改從其他 Frame 嘗試。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q5, C-Q3

C-Q3: 如何列舉所有 Metadata Query 鍵？
- A簡: 直接 foreach(BitmapMetadata) 取出鍵集合，再配合 GetQuery 看值。
- A詳: 步驟：1) var meta = (BitmapMetadata)frame.Metadata；2) foreach(string key in meta){ var val = meta.GetQuery(key);}；3) 記錄鍵與型別，建立對照表。關鍵程式碼片段：foreach(var key in meta){ Console.WriteLine($"{key}={meta.GetQuery(key)}"); }。注意：不同檔案鍵集合不同，需為每種容器取樣。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q4, A-Q14, B-Q12

C-Q4: 如何以 Clone 後的 Metadata 寫入 JPEG？
- A簡: meta.Clone() 後 SetQuery，建立 JpegBitmapEncoder 加 Frame 輸出。
- A詳: 步驟：1) var meta2 = meta.Clone() as BitmapMetadata；2) meta2.SetQuery(鍵, 值)；3) var enc = new JpegBitmapEncoder{ QualityLevel=100 }；4) var outFrame = BitmapFrame.Create(frame, null, meta2, frame.ColorContexts)；5) enc.Frames.Add(outFrame)；6) enc.Save(outStream)。注意：鍵型別匹配；InPlace 若失敗即用此法。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, A-Q17, D-Q8

C-Q5: 如何建立簡單批次 Image Resizer？
- A簡: 迭代檔案→解碼 Frame→縮放→附加 Metadata→Jpeg 編碼輸出。
- A詳: 步驟：1) 走訪資料夾檔名；2) 用 Decoder 取 Frame；3) 產生 TransformedBitmap 縮放；4) 複製/調整 Metadata；5) 用 JpegBitmapEncoder 輸出；6) 記錄耗時與錯誤。程式片段：var tb=new TransformedBitmap(frame,new ScaleTransform(w/ow,h/oh))；enc.Frames.Add(BitmapFrame.Create(tb,null,meta2,null))。注意：資源釋放與 I/O 例外。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, B-Q13, D-Q3

C-Q6: 如何在多核環境建立平行處理管線？
- A簡: 建立生產者/消費者佇列，分離 I/O、解碼、處理、編碼階段並行。
- A詳: 步驟：1) 用佇列串接四階段；2) I/O 執行緒讀檔案路徑；3) 解碼執行緒讀 Frame；4) 處理執行緒縮圖；5) 編碼執行緒寫檔；6) 控制每段並行度。程式片段：ThreadPool.QueueUserWorkItem(...); 以 ConcurrentQueue/ManualResetEvent 實作。注意：避免多解碼同時阻塞；讓非解碼工作吃滿空閒核心。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q13, A-Q16, D-Q4

C-Q7: 如何處理 CR2 與 JPG Metadata 對應差異？
- A簡: 先列舉各自鍵，建立欄位對照表，存取時優先使用存在的鍵。
- A詳: 步驟：1) 以多筆 CR2/JPG 樣本列舉鍵；2) 對齊常見欄位（時間、相機、鏡頭）；3) 建立 Dictionary<string,string> 對照；4) 讀取時依「檔案格式或鍵存在性」決定採用哪個鍵；5) 寫入時選擇目的格式可接受的鍵。注意：維護對照表版本與回報未知鍵。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, A-Q12, D-Q6

C-Q8: 如何偵測 Canon Codec 是否可用？
- A簡: 嘗試以 Decoder 載入 CR2；失敗時回報未安裝或版本不符。
- A詳: 實作：try 建立 BitmapDecoder.Create(fs, ...) 讀 CR2；若拋出「不支援格式」或「編解碼器不可用」，提示安裝 Canon Raw Codec。可在設定頁提供測試按鈕。補充：也可檢查系統已安裝的影像解碼能力，但最實際仍是以樣本檔驗證。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q19, D-Q10, C-Q1

C-Q9: 如何記錄與診斷 GetQuery/SetQuery 失敗？
- A簡: 捕捉例外，列印鍵、型別與值；輸出 Sample 的鍵清單比對。
- A詳: 作法：1) 封裝 GetQuery/SetQuery，catch 例外記錄關鍵資訊（鍵、型別、檔名）；2) 為每檔輸出鍵清單與範例值；3) 自動比對異常檔與正常檔差異；4) 回報未知鍵以擴充對照表。注意：避免在 UI 執行緒做 I/O；日誌需可搜尋與彙整。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q15, D-Q7, A-Q14

C-Q10: 如何避免 BitmapSource.Metadata 為 null 的陷阱？
- A簡: 永遠改從 decoder.Frames[n].Metadata 取用，而非 BitmapSource。
- A詳: 實務規則：1) 別直接用 BitmapSource.Metadata；2) 先建立 Decoder，取 Frames；3) 逐 Frame 嘗試 Metadata；4) 封裝方法 TryGetFrameMetadata(decoder,out meta)；5) 對 meta=null 做降級處理（提示、跳過）。此模式可避免誤判「無中繼資料」，提升穩定性。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q3, D-Q1

---

### Q&A 類別 D: 問題解決類（10題）

D-Q1: 遇到 BitmapSource.Metadata 為 null 怎麼辦？
- A簡: 切換至 Frame 級存取：decoder.Frames[n].Metadata 取得資料。
- A詳: 症狀：BitmapSource.Metadata 為 null。原因：WPF 3.0 不提供來源層級 Metadata。解法：建立 BitmapDecoder，改用 frame.Metadata 取得 BitmapMetadata，再用 Query 讀寫。預防：封裝共用讀取邏輯，避免直接存取 BitmapSource.Metadata。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q7, C-Q10, B-Q1

D-Q2: InPlaceMetadataWriter 失敗或不生效怎麼辦？
- A簡: 改用 Clone Metadata＋重新編碼輸出，確保寫入成功。
- A詳: 症狀：呼叫 InPlace 寫入拋例外或無變化。可能原因：格式不支援就地更新、檔案未以可寫模式開啟、解碼器限制。解決：meta.Clone()→SetQuery→JpegBitmapEncoder 輸出。預防：事先檢查是否支援 InPlace；預設採重編碼路徑。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, C-Q4, B-Q7

D-Q3: CR2 轉 JPEG 極慢怎麼辦？
- A簡: 降低品質/解析度、管線化分工、平行非解碼工作，縮短總時程。
- A詳: 症狀：單張約 80 秒。原因：編解碼器慢、解碼單執行緒。解法：1) 若允許，降低 QualityLevel 或先縮圖；2) 管線化 I/O/處理/編碼；3) 平行執行非解碼步驟；4) 若可，改用更快的編解碼器。預防：量測各階段，設定合理的品質目標。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q15, B-Q13, B-Q9

D-Q4: 雙核只用到 50–60% 怎麼提升？
- A簡: 平行化解碼以外的任務，或同時處理多檔以吃滿核心。
- A詳: 症狀：CPU 不滿載。原因：解碼器內部序列化。解決：1) 同時處理多檔，但限制並行解碼數；2) 將 I/O、縮圖、編碼與解碼併行；3) 背景執行 I/O。預防：設計多階段併行管線，監控並調優每段並行度。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q16, C-Q6, B-Q10

D-Q5: WPF 載入 G2 的 .CRW 丟例外怎麼辦？
- A簡: 驗證樣本檔、嘗試替代管線或更新 codec，並記錄詳細錯誤。
- A詳: 症狀：WPF 例外，但 Microsoft viewer 正常。可能原因：不同解碼路徑或相容性旗標、編解碼器版本差異、檔案特例。解決：更新或重裝 Codec；嘗試改用 Shell/其他 API 讀取；加入格式偵測與降級策略。預防：啟動前做可用性檢查與樣本驗證。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q11, C-Q1, C-Q8

D-Q6: 讀不到 EXIF 或為空值怎麼診斷？
- A簡: 先列舉鍵確認存在性，再用對照表按格式選路徑存取。
- A詳: 症狀：GetQuery 回 null。原因：鍵路徑錯、容器差異、鍵不存在。解法：列舉 meta 鍵；比對樣本建立對照；按存在性選路徑；確認型別與轉型。預防：存取前先檢查鍵存在；維護對照表與記錄未知鍵。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q3, B-Q12, C-Q7

D-Q7: 不知道可用的 Metadata Query 鍵怎麼辦？
- A簡: 直接 foreach(BitmapMetadata) 列舉，輸出鍵與樣本值。
- A詳: 症狀：文件未載明鍵；猜路徑常錯。解法：從 frame.Metadata 取得 BitmapMetadata，foreach 列舉鍵，配合 GetQuery 顯示值，建立清單。預防：將列舉與比對納入開發流程，隨格式更新同步更新清單。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q4, C-Q3, B-Q15

D-Q8: 儲存 JPEG 後 Metadata 消失或不完整？
- A簡: 確認 Frame 建立時帶入 BitmapMetadata，或使用 Clone 後附加。
- A詳: 症狀：輸出檔無 EXIF。原因：未在 Frame 指定 Metadata；某些鍵不支援目標格式。解法：outFrame = BitmapFrame.Create(像素, null, meta2, null)；確保 meta2 來自 Clone 並已 SetQuery 完成。預防：輸出前檢查必要鍵；測試多樣本驗證保存結果。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q4, B-Q9, B-Q6

D-Q9: 批次處理時 UI 卡頓怎麼辦？
- A簡: 將 I/O/解碼/編碼移至背景執行緒，UI 僅負責進度與取消。
- A詳: 症狀：介面凍結。原因：長工在 UI 執行緒。解法：使用 ThreadPool/背景執行緒執行耗時工作；UI 僅更新進度（Invoke/Dispatcher）；任務之間以佇列傳遞資料。預防：採用管線架構與非同步設計，避免任何阻塞 UI 的同步呼叫。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q13, C-Q6, A-Q18

D-Q10: XP/Vista 或不同機器行為不一致怎麼處理？
- A簡: 檢查並鎖定編解碼器版本，啟動時做可用性自檢與降級。
- A詳: 症狀：某機可讀，另機失敗。原因：作業系統/Codec 版本差異。解法：安裝並鎖定相同編解碼器版本；應用程式啟動時檢測樣本檔是否能讀；失敗時提示安裝或禁用相關功能。預防：部署文件列出必要元件與測試步驟。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q19, C-Q8, A-Q5

---

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 Canon Raw Codec 1.2？
    - A-Q2: .CR2 與 .CRW 是什麼？有何差異？
    - A-Q3: 什麼是 WPF（.NET 3.0）？
    - A-Q4: 什麼是 EXIF？為何重要？
    - A-Q5: 為什麼需要安裝廠商 RAW codec？
    - A-Q8: 什麼是 BitmapFrame？為何與 Metadata 有關？
    - A-Q11: 為何 WPF 內建可直接讀的 Metadata 欄位很少？
    - A-Q12: .CR2 與 .JPG 的 Metadata Query 有何差異？
    - B-Q1: WPF 如何載入影像並讀取 Metadata？
    - B-Q4: BitmapMetadata 為何能列舉 Query 鍵？
    - B-Q5: 如何用 GetQuery 正確讀取 EXIF 欄位？
    - C-Q1: 如何在 WPF 載入 CR2 並顯示？
    - C-Q2: 如何從 BitmapFrame 讀取相機型號（CameraModel）？
    - C-Q3: 如何列舉所有 Metadata Query 鍵？
    - D-Q1: 遇到 BitmapSource.Metadata 為 null 怎麼辦？

- 中級者：建議學習哪 20 題
    - A-Q6: WPF 的「Metadata Query Language」是什麼？
    - A-Q7: 為何 BitmapSource.Metadata 會是 null？
    - A-Q14: 為什麼需要「列舉所有可用的 Metadata Query」？
    - A-Q15: Canon Codec 效能議題的核心是什麼？
    - A-Q16: 多核心 CPU 為何未被充分利用？
    - A-Q17: 為什麼改採「Clone Metadata 後再寫入編碼器」？
    - B-Q2: Metadata Query 的解析機制是什麼？
    - B-Q3: 為何 Metadata 存在於 Frame，而非 BitmapSource？
    - B-Q6: 如何用 SetQuery 修改 EXIF 欄位？
    - B-Q8: CR2 與 JPG EXIF 對應不一致的技術原因？
    - B-Q9: JpegBitmapEncoder 的品質與輸出機制？
    - B-Q10: 編解碼器如何決定解碼效能與多執行緒表現？
    - B-Q12: 如何建立跨格式的 Metadata 對應表？
    - B-Q13: 批次影像處理的管線化原理？
    - B-Q14: 內建屬性少，如何完整存取 EXIF？
    - B-Q15: 為何「先列舉再存取」能降低錯誤？
    - C-Q4: 如何以 Clone 後的 Metadata 寫入 JPEG？
    - C-Q5: 如何建立簡單批次 Image Resizer？
    - C-Q7: 如何處理 CR2 與 JPG Metadata 對應差異？
    - D-Q8: 儲存 JPEG 後 Metadata 消失或不完整？

- 高級者：建議關注哪 15 題
    - A-Q13: 什麼是 InPlaceMetadataWriter？
    - B-Q7: InPlaceMetadataWriter 的機制與限制？
    - B-Q11: 為何 Microsoft viewer 能看 CRW，但 WPF 會丟例外？
    - B-Q16: 為何 BitmapSource.Metadata 設計為可能為空？
    - B-Q17: 如何評估解碼與編碼的時間占比？
    - B-Q18: 何謂「把不相干的 job 排在一起」的原理？
    - B-Q19: WPF 與作業系統 Codec 的相依如何影響行為？
    - C-Q6: 如何在多核環境建立平行處理管線？
    - C-Q8: 如何偵測 Canon Codec 是否可用？
    - C-Q9: 如何記錄與診斷 GetQuery/SetQuery 失敗？
    - D-Q2: InPlaceMetadataWriter 失敗或不生效怎麼辦？
    - D-Q3: CR2 轉 JPEG 極慢怎麼辦？
    - D-Q4: 雙核只用到 50–60% 怎麼提升？
    - D-Q5: WPF 載入 G2 的 .CRW 丟例外怎麼辦？
    - D-Q10: XP/Vista 或不同機器行為不一致怎麼處理？