---
layout: synthesis
title: "Canon RAW Codec for Vista 出來了.."
synthesis_type: faq
source_post: /2007/04/04/canon-raw-codec-for-vista-released/
redirect_from:
  - /2007/04/04/canon-raw-codec-for-vista-released/faq/
postid: 2007-04-04-canon-raw-codec-for-vista-released
---

# Canon RAW Codec for Vista：WIC、WPF 與 CR2/CRW 支援

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 RAW 影像？
- A簡: RAW 是感光元件原始資料檔，保留細節供後製。
- A詳: RAW 指數位相機感光元件輸出的近原始資料，未經相機強烈壓縮、銳化與降噪。其特點包括高位元深度、寬動態範圍與可調白平衡、色調曲線，利於非破壞式後製；缺點是檔案較大、需專用解碼器與軟體支援。應用於專業攝影、科學影像與需高品質輸出的工作流程，相較 JPEG 有更大後製彈性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q22, A-Q2, A-Q20

A-Q2: 什麼是 Canon RAW？
- A簡: Canon RAW 為佳能相機的 RAW 格式，含 CR2 與較舊的 CRW。
- A詳: Canon RAW 泛指佳能相機產生的專有 RAW 檔案，主要有兩種：新一代 CR2（基於 TIFF/EP 容器）與較舊的 CRW（基於 CIFF）。兩者封裝影像感測資料與豐富中繼資訊，但結構、壓縮與中繼資料差異大。應用上需相對應的編解碼器或轉檔軟體才能在作業系統、瀏覽器與影像應用程式中預覽與開啟。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q4, A-Q5

A-Q3: 什麼是 CR2？
- A簡: CR2 是 Canon 新一代 RAW，基於 TIFF/EP，普遍支援。
- A詳: CR2（Canon RAW 2）是佳能較新的 RAW 容器，沿用 TIFF/EP 結構，便於擴充與相容一般影像基礎設施。它通常包含 Bayer 陣列原始資料、內嵌預覽 JPEG 與豐富 EXIF/MakerNote。特點是被較多系統與第三方程式支援，包括 Windows 的 WIC 架構在安裝相容編解碼器後可直接生成縮圖、預覽與載入。適用多數單眼與新款機身。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, B-Q6, B-Q3

A-Q4: 什麼是 CRW？
- A簡: CRW 是較舊 Canon RAW，基於 CIFF，支援度較低。
- A詳: CRW（Canon RAW）是佳能早期 RAW 格式，採 CIFF（Camera Image File Format）容器，結構與 CR2 明顯不同。常見於早期型號（如 PowerShot G2、部分初代 EOS 機身）。因使用較舊私有規格，系統級與第三方通用解碼支援度較低，需特定編解碼器或使用原廠（如 DPP）與第三方轉檔軟體處理，對於新版作業系統的內建預覽相對不友善。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, D-Q3, B-Q6

A-Q5: CR2 與 CRW 有何差異？
- A簡: CR2 基於 TIFF/EP，支援度高；CRW 基於 CIFF，較舊難支援。
- A詳: 差異在容器與生態支援：CR2 以 TIFF/EP 為基礎，欄位結構規範較清晰、支援度普遍，易於以 WIC 等架構整合；CRW 以 CIFF 為基礎，私有部分較多、MakerNote 差異性大。實務上 CR2 較易獲得系統級縮圖與預覽，CRW 則常須仰賴原廠或專用轉檔流程。對開發者而言，兩者需不同編解碼器與中繼資料解析策略。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, A-Q3, A-Q4

A-Q6: 什麼是 WIC 編解碼器（Codec）？
- A簡: WIC Codec 是可插拔元件，讓系統解特定影像格式。
- A詳: WIC 編解碼器是 Windows Imaging Component 的可插拔 COM 元件，負責將特定影像格式解碼成統一的像素資料與中繼資訊。其特點是系統層整合、共用於殼層、WPF、Windows Photo Gallery 等。安裝後，所有使用 WIC 的應用程式可自動獲取對該格式的支援，無需各自內建解碼邏輯，提升擴充性與維護性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, A-Q7, A-Q9

A-Q7: 什麼是 Windows Imaging Component（WIC）？
- A簡: WIC 是 Vista 起的影像基礎架構，統一解碼與中繼。
- A詳: WIC 是 Windows 自 Vista 起提供的影像平台 API，負責統一影像解碼、編碼、像素格式轉換與中繼資料存取。它透過外掛式 Codec 擴充新格式支援，並服務於系統殼層、相片應用與 WPF。特點是統一管線、可插拔、可共用加速與色彩管理，讓 OS 級預覽與第三方應用共享同一份格式支援。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q4, A-Q6

A-Q8: WPF 與 WIC 的關係是什麼？
- A簡: WPF 透過 WIC 解碼影像，Codec 安裝即得支援。
- A詳: WPF 的影像類型（如 BitmapImage、BitmapSource）底層倚賴 WIC 解碼與像素轉換。當系統安裝相容的 WIC Codec，WPF 即可無縫載入該格式（含 RAW 的預設渲染），同時受益於 WIC 的中繼資料與色彩管理。此設計讓 .NET 應用在不改碼的前提下，隨 OS 新增的 Codec 擴充支援更多影像格式。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, A-Q6, C-Q3

A-Q9: 為什麼在 Vista 需要 Canon RAW Codec？
- A簡: Vista 需外掛 Codec 才能預覽與載入 Canon RAW。
- A詳: Vista 雖內建 WIC，但不包含所有廠商 RAW 的解碼器。若要在 Explorer、Windows Photo Gallery 或 WPF 應用中直接預覽、縮圖與開啟 Canon RAW，必須安裝對應的 Canon RAW Codec。安裝後，系統與應用可共享該能力，改善工作流程效率，無需各應用程式各自實作 RAW 支援。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q4, C-Q1

A-Q10: 2007 年釋出的 Canon RAW Codec 支援什麼？
- A簡: 當時版本主要支援 CR2，不支援舊款的 CRW。
- A詳: 依當時公告，面向 Windows Vista 的 Canon RAW Codec 首波支援集中於 CR2 檔案類型，尚未涵蓋較舊的 CRW。這讓多數較新機身可在系統層獲得縮圖、預覽與載入，但使用早期機型（如 PowerShot G2）者仍需原廠軟體或另行轉檔。後續是否擴充 CRW 需視廠商與平台支援策略。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: D-Q3, A-Q5, C-Q5

A-Q11: 為何初期僅支援 CR2 而非 CRW？
- A簡: 因容器差異、私有規格多，CR2 較易整合。
- A詳: CR2 採用 TIFF/EP，結構清楚、工具鏈成熟，對 WIC 整合較友善；CRW 基於 CIFF，含大量私有欄位與歷史差異，維護成本高。為了儘速覆蓋較新機身並降低風險，初期 Codec 多先支援 CR2。CRW 的支援需額外處理 MakerNote、色彩矩陣與壓縮細節，測試矩陣也更複雜。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, A-Q4, B-Q20

A-Q12: 安裝 RAW Codec 的核心價值是什麼？
- A簡: 一次安裝，全系統共享預覽、縮圖與載入能力。
- A詳: WIC Codec 屬系統層擴充，安裝後 Explorer、相片應用、WPF 程式皆可共享新格式支援。核心價值在於一致性與維運效率：統一色彩與中繼資料解析，降低各應用重複開發；也讓使用者工作流程順暢，無需在不同軟體間反覆轉檔。對企業環境，集中部署亦可快速擴充影像能力。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, A-Q14, B-Q1

A-Q13: Vista 殼層縮圖與預覽如何受惠於 Codec？
- A簡: Explorer 透過 WIC 與 Codec 生出 RAW 縮圖與預覽。
- A詳: Vista 殼層（Explorer）與 Windows Photo Gallery 透過 WIC 載入影像；當安裝 Canon RAW Codec 後，殼層即可對 CR2 進行解析、擷取內嵌預覽或解碼生成縮圖與快速檢視。其特點是效能優化與快取重用，讓相簿瀏覽更順暢。無 Codec 時則僅顯示通用圖示或使用內嵌 JPEG 畫質有限。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, A-Q9, D-Q1

A-Q14: 安裝 Codec 對應用程式有何影響？
- A簡: 所有使用 WIC 的應用立即獲得新格式支援。
- A詳: 安裝完成後，任何透過 WIC 進行影像載入的程式（如 WPF 應用、Photo Gallery、部份第三方相片管理工具）皆可即時讀取該格式，含縮圖與中繼資料。若應用為 64 位元，需對應 64 位元 Codec 才能載入。對開發者來說，程式碼不需修改即可擴充支援，但仍需注意錯誤處理與顏色管理一致性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q9, C-Q6, D-Q5

A-Q15: 什麼是 WPF？
- A簡: WPF 是 .NET 的 UI 框架，提供向量與媒體呈現。
- A詳: Windows Presentation Foundation 是 .NET 的視覺化 UI 框架，支援向量圖形、動畫、版面與影像呈現。其影像功能倚賴 WIC 提供統一解碼與像素處理，讓應用可不變更程式碼而支援更多影像格式。WPF 適合建構相片檢視器、資產管理與影像工作流程工具，結合資料繫結與可組成式 UI。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, C-Q3, C-Q9

A-Q16: 為何 WPF 不內建各家 RAW Codec？
- A簡: 授權、維護與相容性成本高，採外掛式。
- A詳: RAW 格式含廠商私有內容與授權限制，且機型頻繁更新。若將各家 Codec 內建於 WPF/.NET，不僅授權複雜，維護更新也困難。Windows 採用 WIC 的外掛式架構，將格式支援下放至獨立編解碼器，讓廠商與使用者按需安裝，既降低平台負擔，又能快速回應新機型與修正。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q1, A-Q14

A-Q17: 為何老相機（如 G2）使用 CRW？
- A簡: 早期機型採用 CIFF/CRW，後期改用 CR2。
- A詳: 佳能早期數位相機在 TIFF/EP 尚未普及與內部工具鏈成熟前，採用了自家 CIFF 容器形成 CRW 格式。隨著產業標準演進與軟體相容需求，後續機型轉向 CR2。這造成新系統對 CR2 支援較佳，而 CRW 需依賴舊版軟體或轉檔流程才能納入現代工作環境。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, A-Q5, C-Q5

A-Q18: 若無 CRW Codec，常見替代流程是？
- A簡: 使用原廠軟體或轉 DNG/TIFF，再進系統流程。
- A詳: 當系統無法原生解 CRW 時，可用原廠 Digital Photo Professional（DPP）或第三方工具將 CRW 轉為 DNG 或 16 位元 TIFF。轉檔後，可被系統與多數影像軟體順利處理，也能保留大部分色彩與動態範圍。此流程雖多一步轉換，但可立即融入現代資產管理與備份體系。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q5, D-Q3, A-Q12

A-Q19: WIC Codec 的 32/64 位元差異是什麼？
- A簡: 進程位元數須與 Codec 相符，否則無法載入。
- A詳: WIC Codec 為 In-Proc COM 元件，需與載入它的進程位元數一致。64 位元應用需 64 位元 Codec；32 位元應用需 32 位元 Codec。在 x64 系統上，Explorer 與應用可能有 x86/x64 兩種版本，需分別安裝對應位元的 Codec 才能在各自環境顯示縮圖與開啟檔案。這是常見相容性問題來源。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, D-Q5, C-Q6

A-Q20: WIC Codec 與 RAW 編輯器有何差異？
- A簡: Codec 提供解碼預覽；編輯器提供進階調整。
- A詳: WIC Codec 主要目標是系統級解碼、縮圖、基本預覽與中繼資料存取；多數不提供進階去馬賽克選項、曲線、降噪與鏡頭校正控制。RAW 編輯器（如 DPP、Lightroom）提供完整影像處理與批次輸出。兩者互補：Codec 讓檔案在 OS 層可見可用；編輯器負責專業後製與輸出。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, B-Q7, A-Q22

A-Q21: 安裝 Codec 的安全性該注意什麼？
- A簡: 僅從可信來源下載，驗證簽章與相容性。
- A詳: 由於 Codec 為 In-Proc 模組，與殼層與應用同進程運行，穩定性與安全性至關重要。建議僅從原廠或可信平台取得，檢查數位簽章與版本相容說明，避免來路不明的套件。企業環境可先行驗證再部署，並建立更新機制，以降低崩潰、漏洞或相容性問題風險。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: D-Q10, D-Q7, A-Q14

A-Q22: RAW 檔的優缺點是什麼？
- A簡: 優：高寬容後製彈性；缺：檔大需解碼器。
- A詳: 優點包括高位元深度、保留更多高光與陰影細節、可調白平衡與色調、非破壞編輯；缺點是檔案大、工作流程需解碼與轉檔、平台相容性依賴 Codec 或軟體支援。對追求品質與彈性的攝影者是基本選擇；對僅需輕量分享者，JPEG 仍具效率與相容優勢。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q20, B-Q7

A-Q23: 如何判斷相機是否受 Codec 支援？
- A簡: 查官方相容清單與版本說明，測試縮圖預覽。
- A詳: 先至原廠或 Microsoft 相容性頁面查詢支援機型與格式版本，再確認系統位元與 OS 版本。安裝後以 Explorer 檢視同資料夾中的 RAW 檔：若能顯示縮圖、可在相片應用開啟，即表示支援。對較舊機型（CRW）需特別留意，可能仍需轉檔或另行工具。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q1, A-Q10, D-Q1

A-Q24: 為什麼需要顏色管理（ICC/WCS）？
- A簡: 確保 RAW 解碼後顏色正確、跨設備一致。
- A詳: RAW 解碼涉及色彩空間轉換與相機色彩矩陣，若無正確 ICC/WCS 管理，顏色易偏移。顏色管理可依顯示器校正檔與工作色域精準映射，確保預覽與輸出一致。WIC 與 WPF 可整合 WCS 與 ICC，讓系統級預覽與應用呈現一致，是專業工作流程的必要基礎。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, C-Q8, D-Q4

---

### Q&A 類別 B: 技術原理類

B-Q1: WIC 架構如何運作？
- A簡: 以可插拔 COM 編解碼器統一影像解碼與中繼。
- A詳: 技術原理說明：WIC 提供統一 API，透過登錄的編解碼器（COM In-Proc）解碼多種格式為標準化像素與中繼資料。關鍵步驟或流程：應用呼叫 IWICImagingFactory 建立解碼器、解析框架與中繼；WIC 按檔頭簽名選派對應 Codec。核心組件介紹：ImagingFactory、BitmapDecoder/FrameDecode、ColorContext、FormatConverter、MetadataReader，協作完成載入與轉換。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, A-Q7, B-Q11

B-Q2: WPF 載入影像的執行流程為何？
- A簡: WPF 透過 WIC 建立解碼器，輸出 BitmapSource。
- A詳: 技術原理說明：WPF 的 BitmapImage/BitmapFrame 以 WIC 為後端，解碼並轉為可繪製的 BitmapSource。關鍵步驟或流程：指定 Uri/Stream → 建立 BitmapImage → WIC 選派 Decoder → 解碼 Frame → 格式轉換（如 Pbgra32）→ 呈現。核心組件介紹：BitmapImage、BitmapSource、ImagingFactory、FormatConverter、WriteableBitmap（進一步處理）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, C-Q3, B-Q1

B-Q3: 透過 WIC 解碼 CR2 的流程是什麼？
- A簡: 由 CR2 Codec 解析檔頭、取預覽或去馬賽克輸出。
- A詳: 技術原理說明：CR2 Codec 讀取 TIFF/EP IFD，解析感測資料、色彩矩陣與內嵌 JPEG。關鍵步驟或流程：1) 檔頭辨識 → 2) 讀 IFD/Tag → 3) 決定使用內嵌預覽或解 RAW → 4) 去馬賽克與色彩轉換 → 5) 輸出標準像素。核心組件介紹：CR2 Decoder、MetadataReader（EXIF/MakerNote）、ColorContext（ICC/WCS）、FormatConverter。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, B-Q7, B-Q11

B-Q4: Vista 殼層縮圖如何生成？
- A簡: Explorer 透過 WIC 解碼，快取縮圖供後續快速載入。
- A詳: 技術原理說明：Shell 以 WIC 取內嵌預覽或解碼產生縮圖，並寫入縮圖快取。關鍵步驟或流程：Shell 索引檔 → 查詢快取 → 若無則調用 WIC 解碼 → 產生縮圖 → 寫入快取。核心組件介紹：Shell Thumbnail Provider、WIC Decoder/Frame、Windows Thumbnail Cache、Color Management Pipeline。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q13, D-Q1, B-Q1

B-Q5: WIC 的中繼資料處理機制是什麼？
- A簡: 以 MetadataReader 統一讀取 EXIF/XMP/MakerNote。
- A詳: 技術原理說明：WIC 統一中繼資料模型，透過編解碼器提供對標準與私有標籤的存取。關鍵步驟或流程：建立 MetadataQueryReader → 以查詢語法讀取 EXIF/XMP → 對私有 MakerNote 由 Codec 提供映射。核心組件介紹：IWICMetadataQueryReader/Writer、Container Format Handlers、Codec 對應的 Tag 解析器。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q8, C-Q3, B-Q11

B-Q6: CR2 與 CRW 的容器技術差異是什麼？
- A簡: CR2 採 TIFF/EP，CRW 採 CIFF，欄位與壓縮差異大。
- A詳: 技術原理說明：CR2 基於 TIFF/EP 的 IFD/Tag 結構，便於標準工具解析；CRW 基於 CIFF，使用塊狀節點與私有欄位。關鍵步驟或流程：CR2 解析 IFD → 取 Tag；CRW 需遍歷 CIFF 節點、解私有欄位。核心組件介紹：CR2/CRW 專屬 Decoder、TIFF/EP Handler、CIFF 解析器、MakerNote 對應表。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, A-Q4, A-Q11

B-Q7: RAW 解碼的色彩管理與去馬賽克機制？
- A簡: 由 Codec 以相機矩陣去馬賽克並套用色彩轉換。
- A詳: 技術原理說明：RAW 需去馬賽克（Demosaic）與色彩空間轉換。關鍵步驟或流程：讀取黑位/白點 → 去馬賽克 → 應用相機色彩矩陣與白平衡 → 映射至工作色域（sRGB/AdobeRGB）→ Gamma/曲線。核心組件介紹：Demosaic 模組、ColorContext（ICC/WCS）、Tone Mapping、Noise Reduction（視 Codec 支援）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q24, D-Q4, B-Q3

B-Q8: WIC 解碼效能的關鍵是什麼？
- A簡: 善用內嵌預覽、快取、串流與延遲載入。
- A詳: 技術原理說明：WIC 支援串流、逐步解碼與格式轉換最佳化。關鍵步驟或流程：優先讀取內嵌縮圖 → 需求導向延遲解碼 → 以 OnDemand 快取策略 → 適當像素格式轉換。核心組件介紹：IWICStream、BitmapCacheOption、Thumbnail Cache、FormatConverter（硬體加速視平台）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q10, D-Q6, B-Q4

B-Q9: x86/x64 Codec 載入規則是什麼？
- A簡: 進程與 Codec 位元數必須一致，否則載入失敗。
- A詳: 技術原理說明：WIC Decoder 以 In-Proc COM 載入，受進程位元數限制。關鍵步驟或流程：應用啟動 → COM 以 CLSID 從登錄定位 DLL → 比對位元數 → 載入或失敗。核心組件介紹：COM 註冊（HKCR\CLSID）、WOW64 隔離、Explorer x86/x64 版本，牽動縮圖與預覽是否生效。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q19, D-Q5, C-Q6

B-Q10: 沒有 Codec 時應用如何回退？
- A簡: 使用內嵌 JPEG 預覽或顯示格式不支援。
- A詳: 技術原理說明：若無對應 Codec，WIC 嘗試由容器取內嵌預覽；若也無，則解碼失敗。關鍵步驟或流程：檔頭識別 → 尋找內嵌縮圖/預覽 → 失敗則回報錯誤。核心組件介紹：Container Handler、Preview Extractor、BitmapDecoder 回傳錯誤碼，WPF 對應為例外（如 FileFormatException）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q4, D-Q2, B-Q24

B-Q11: WIC 如何選擇對應的編解碼器？
- A簡: 依檔頭魔術數與容器特徵選派對應 Decoder。
- A詳: 技術原理說明：WIC 檢查檔頭簽名（Magic Number）、MIME、擴展名與登錄的解碼器能力表。關鍵步驟或流程：掃描可用 Decoder → 呼叫 MatchesPattern → 選擇最適者 → 建立解碼器。核心組件介紹：IWICBitmapDecoderInfo、Component Enumerator、Capability Flags、Container Pattern。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q3, B-Q5

B-Q12: WPF 影像管線的核心組件為何？
- A簡: BitmapImage、BitmapSource、FormatConverter、WriteableBitmap。
- A詳: 技術原理說明：WPF 以 BitmapImage/Frame 表示影像來源，以 FormatConvertedBitmap 轉像素格式，以 WriteableBitmap 寫像素。關鍵步驟或流程：建立來源 → 解碼 → 格式轉換（如 Pbgra32）→ 繪製。核心組件介紹：BitmapImage、BitmapFrame、FormatConvertedBitmap、WriteableBitmap、ImagingFactory（底層 WIC）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, C-Q3, C-Q8

B-Q13: Windows Photo Gallery 與 WIC 如何整合？
- A簡: 透過 WIC 統一解碼、縮圖、色彩與中繼資料。
- A詳: 技術原理說明：相片應用以 WIC 作為單一解碼層。關鍵步驟或流程：掃描媒體 → WIC 解碼縮圖 → 以快取加速 → 讀取中繼建立索引 → 顯示與基本調整。核心組件介紹：WIC Decoder、MetadataReader、Thumbnail Cache、Color Management Pipeline，確保系統與應用一致呈現。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q13, B-Q4, B-Q5

B-Q14: 殼層編解碼器的安全模型與風險？
- A簡: In-Proc 執行，崩潰與漏洞影響整個進程。
- A詳: 技術原理說明：Codec 於殼層或應用進程內執行，安全邊界較弱。關鍵步驟或流程：Shell 載入 Codec → 解析不可信檔案 → 若有漏洞可能導致崩潰或 RCE。核心組件介紹：COM 安全、代碼簽章、更新機制、Windows Error Reporting。建議僅用可信來源並維持更新。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q21, D-Q7, D-Q10

B-Q15: WIC 像素格式與轉換如何設計？
- A簡: 統一為常用格式，如 24/32 位，便於渲染。
- A詳: 技術原理說明：WIC 支持多像素格式，透過 FormatConverter 轉為渲染友好的格式（如 Pbgra32）。關鍵步驟或流程：Decoder 輸出原生格式 → 檢查渲染需求 → 轉換位元深度、色彩通道與預乘 Alpha。核心組件介紹：IWICFormatConverter、PixelFormat GUID、ColorContext，確保跨應用一致。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, C-Q3, D-Q4

B-Q16: RAW 預設轉換與白平衡如何處理？
- A簡: 使用相機/自動白平衡與預設曲線生成預覽。
- A詳: 技術原理說明：多數 Codec 以相機白平衡與預設 Tone Curve 快速生成預覽。關鍵步驟或流程：讀拍攝設定 → 套用 WB/曝光補償 → 套曲線與 Gamma → 輸出 sRGB 預覽。核心組件介紹：MetadataReader（WB、Picture Style）、Tone Mapping、ColorContext。結果與專業編輯器可能有差異。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q4, A-Q24, B-Q7

B-Q17: XMP/Sidecar 檔案如何被 WIC 使用？
- A簡: 視 Codec 支援，讀取旁註檔補充中繼資料。
- A詳: 技術原理說明：部分 Codec 支援讀取 .XMP 旁註檔，合併至中繼視圖。關鍵步驟或流程：開檔 → 嘗試尋找同名 .xmp → 解析 XMP → 與 EXIF/MakerNote 合併。核心組件介紹：MetadataQueryReader、XMP 解析器、合併策略（優先序）。支援情況依 Codec 實作而異。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: D-Q8, B-Q5, C-Q3

B-Q18: 內嵌縮圖與多幀影像如何處理？
- A簡: 優先使用內嵌 JPEG 作快速預覽，再需時解 RAW。
- A詳: 技術原理說明：RAW 常含多尺寸內嵌縮圖。關鍵步驟或流程：讀取目錄 → 選最合適尺寸縮圖 → 若不足再解 RAW 產生預覽。核心組件介紹：FrameEnumerator、Preview/Thumbnail Tag、Decoder 策略（速度 vs 品質）。此策略平衡效能與體驗。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, D-Q6, B-Q4

B-Q19: 如何診斷 WIC Codec 載入問題？
- A簡: 檢查位元數、登錄項、事件記錄與測試樣本。
- A詳: 技術原理說明：載入失敗可能出在 COM 註冊、位元數或相依 DLL。關鍵步驟或流程：查看位元數 → 檢查 CLSID 註冊 → 事件檢視器錯誤 → 使用 WIC 工具/範例程式測試 → ProcMon/Dependency Walker 查相依。核心組件介紹：COM Registry、Event Viewer、WIC 流水測試工具。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: D-Q5, C-Q6, B-Q9

B-Q20: 為何泛用支援 CRW 困難？
- A簡: 私有 MakerNote 與歷史差異大，解析成本高。
- A詳: 技術原理說明：CRW 的 CIFF 結構含大量私有欄位，且不同機身/韌體差異顯著。關鍵步驟或流程：需針對各機型對照表解析 → 驗證輸出 → 調整色彩矩陣。核心組件介紹：CIFF 解析器、機型映射表、測試數據庫。維護與授權因素也增加難度。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q11, A-Q4, D-Q3

B-Q21: 安裝新 Codec 後如何讓系統即時生效？
- A簡: 重新啟動使用該 Codec 的進程或登出/重開。
- A詳: 技術原理說明：COM 元件載入於進程生命週期內緩存。關鍵步驟或流程：安裝 → 重啟 Explorer/相片應用 → 清除縮圖快取（必要時）→ 重載測試。核心組件介紹：Explorer 進程、Thumbnail Cache、COM 註冊快取。大型更新後建議重開機確保環境乾淨。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: D-Q1, C-Q2, B-Q4

B-Q22: WIC 與 Windows Color System（WCS）的關係？
- A簡: WIC 可使用 WCS/ICC 進行色彩轉換與校正。
- A詳: 技術原理說明：WIC 提供 ColorContext，與 WCS/ICC 整合進行色彩空間轉換。關鍵步驟或流程：讀取來源色彩定義 → 套用顯示/工作色域 → 轉換與 Gamma 校正。核心組件介紹：IWICColorContext、ICM/WCS 管線、Monitor Profile。確保跨應用與設備一致的顏色呈現。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q24, C-Q8, D-Q4

B-Q23: 程式如何列舉已安裝的 WIC Codec？
- A簡: 以 Component Enumerator 走訪 DecoderInfo 清單。
- A詳: 技術原理說明：WIC 提供元件枚舉 API。關鍵步驟或流程：建立 IWICImagingFactory → CreateComponentEnumerator → 篩選 Decoder 類型 → 讀取友好名稱、支援格式。核心組件介紹：IWICComponentInfo、IWICBitmapDecoderInfo、Enumerator，便於診斷支援狀態與 UI 列示。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q7, B-Q19, A-Q23

B-Q24: WIC 錯誤如何映射到 .NET 例外？
- A簡: 解碼失敗會拋 FileFormatException/COM 例外。
- A詳: 技術原理說明：WPF 將底層 WIC HRESULT 轉為 .NET 例外。關鍵步驟或流程：WIC 解碼 → 回報 HRESULT → WPF 對應為 FileFormatException 或 NotSupportedException → 上拋。核心組件介紹：BitmapImage、BitmapDecoder、Exception Mapping，有助於撰寫穩健的錯誤處理與降級策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q2, B-Q10, C-Q4

---

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何在 Vista 安裝 Canon RAW Codec？
- A簡: 下載官方安裝程式，依 OS/位元安裝並重啟殼層。
- A詳: 具體實作步驟：1) 至 Canon/可信平台下載對應 Vista 與位元數的 RAW Codec；2) 關閉相片應用/Explorer；3) 執行安裝並完成註冊；4) 重啟 Explorer 或重開機。關鍵程式碼片段或設定：無需程式碼；確保安裝檔具數位簽章。注意事項與最佳實踐：確認支援清單（特別是 CR2/CRW）、位元數相符、建立還原點以便回滾。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, A-Q23, B-Q21

C-Q2: 如何驗證 CR2 縮圖是否生效？
- A簡: 開啟包含 CR2 的資料夾，應顯示縮圖與預覽。
- A詳: 具體實作步驟：1) 在 Explorer 以「大型圖示」檢視 CR2；2) 開啟預覽窗格；3) 在 Windows Photo Gallery 中開啟檔案確認。關鍵程式碼片段或設定：可清理縮圖快取（磁碟清理）重建快取。注意事項與最佳實踐：若無效，重啟 Explorer，確認位元數正確、Codec 安裝成功，並測試其他 CR2 樣本排除檔案損毀。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, D-Q1, B-Q21

C-Q3: 如何在 WPF 載入 CR2 影像？
- A簡: 以 BitmapImage 指向檔案，WIC 會調用 Codec。
- A詳: 具體實作步驟：建立 Image 控制項，使用 BitmapImage 載入檔案。關鍵程式碼片段或設定：
// C#
var bmp = new BitmapImage();
bmp.BeginInit();
bmp.CacheOption = BitmapCacheOption.OnDemand;
bmp.UriSource = new Uri(path);
bmp.EndInit();
image.Source = bmp;
注意事項與最佳實踐：確保已安裝 Codec；增加例外處理；使用 OnDemand/DecodePixelWidth 以控記憶體；必要時先取用內嵌預覽加速。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q10, B-Q15

C-Q4: 無 Codec 時如何改用內嵌 JPEG？
- A簡: 掃描容器取出預覽流，退而求其次顯示。
- A詳: 具體實作步驟：1) 嘗試以 WIC 讀取縮圖/預覽 Frame；2) 若可取得，輸出為 JPEG Stream 供顯示；3) 無法則顯示提示。關鍵程式碼片段或設定：使用 BitmapDecoder.Thumbnail 或 MetadataQueryReader 查詢預覽標籤。注意事項與最佳實踐：畫質受限；清楚告知用戶安裝 Codec 可獲更佳效果。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, D-Q2, B-Q18

C-Q5: 如何將 CRW 轉為 DNG/TIFF 以便工作？
- A簡: 用原廠或第三方工具批次轉 DNG/TIFF 再處理。
- A詳: 具體實作步驟：1) 以 DPP/Adobe DNG Converter 開啟 CRW；2) 選擇輸出 DNG 或 16-bit TIFF；3) 保留原檔備份；4) 將轉檔結果納入資產管理。關鍵程式碼片段或設定：無程式碼；工具提供批次模式。注意事項與最佳實踐：選 16 位元保留動態範圍；同步保存 XMP；驗證色彩設定一致。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q18, D-Q3, A-Q22

C-Q6: 如何確認應用與 Codec 位元數相容？
- A簡: 在 x64 系統需安裝對應 x86/x64 版本各一套。
- A詳: 具體實作步驟：1) 檢視應用是 32/64 位元（工作管理員或關於視窗）；2) 於安裝頁面選擇相符位元數的 Codec；3) 在 x64 上同時安裝 x86/x64 以覆蓋不同進程。關鍵程式碼片段或設定：無。注意事項與最佳實踐：Explorer 亦可能有 x86 實例；安裝後重啟相關進程，避免載入舊版本。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, D-Q5, B-Q19

C-Q7: 如何註冊/解除註冊 WIC Codec？
- A簡: 透過安裝程式或 regsvr32 註冊 COM 元件。
- A詳: 具體實作步驟：1) 優先使用官方安裝/解除程式；2) 進階：以 regsvr32 路徑\codec.dll 進行註冊/反註冊；3) 確認登錄 CLSID 項目。關鍵程式碼片段或設定：regsvr32 /u codec.dll。注意事項與最佳實踐：需系統管理員權限；避免手動改登錄；備份登錄或建立還原點。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q1, B-Q19, B-Q23

C-Q8: 如何在 WPF 啟用色彩管理以正確顯示？
- A簡: 使用 FormatConvertedBitmap 與正確顯示器 ICC。
- A詳: 具體實作步驟：1) 確認系統顯示器 ICC 設為校正檔；2) WPF 預設使用 WCS；3) 必要時用 ColorConvertedBitmap 指定來源/目標色域。關鍵程式碼片段或設定：ColorConvertedBitmap(source, srcICC, dstICC, PixelFormats.Pbgra32)。注意事項與最佳實踐：確保編碼器輸出為標準色域（如 sRGB）；避免重複色彩轉換。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q22, A-Q24, D-Q4

C-Q9: 如何建立簡易 CR2 檢視器（WPF）？
- A簡: 建立 WPF 專案，Image 綁定檔案清單與 BitmapImage。
- A詳: 具體實作步驟：1) 建立 WPF 專案；2) 以 FileSystemWatcher/檔案對話選取 CR2；3) Image.Source 綁定 BitmapImage；4) 清單顯示縮圖。關鍵程式碼片段或設定：使用 DecodePixelWidth 產生縮圖，提升效能。注意事項與最佳實踐：加入例外處理、非同步載入、快取策略，提示用戶安裝 Codec。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q3, B-Q8, D-Q6

C-Q10: 如何測量解碼效能並最佳化快取？
- A簡: 量測載入時間，優先內嵌預覽並使用快取策略。
- A詳: 具體實作步驟：1) 計時解碼/顯示流程；2) 優先取內嵌縮圖；3) 調整 DecodePixelWidth；4) 啟用 OnDemand；5) 以記憶體/磁碟快取結果。關鍵程式碼片段或設定：Stopwatch 計時、BitmapCacheOption.OnDemand。注意事項與最佳實踐：控制同時解碼數量；避免過多像素格式轉換；批次預先產生縮圖。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q8, B-Q18, D-Q6

---

### Q&A 類別 D: 問題解決類（10題）

D-Q1: CR2 縮圖在 Explorer 不顯示怎麼辦？
- A簡: 檢查是否安裝正確版本 Codec 並重啟殼層。
- A詳: 問題症狀描述：資料夾僅顯示通用圖示，預覽窗格空白。可能原因分析：未安裝 Codec、位元數不符、縮圖快取損壞。解決步驟：1) 安裝對應位元數 Codec；2) 重啟 Explorer/重開機；3) 清理縮圖快取；4) 測試其他 CR2。預防措施：維持 Codec 更新，安裝後重啟相關進程，建立標準化部署流程。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, B-Q4, B-Q21

D-Q2: WPF 載入 CR2 拋出 NotSupportedException？
- A簡: 表示缺 Codec 或解碼失敗，改用內嵌預覽降級。
- A詳: 問題症狀描述：BitmapImage.EndInit 時拋出不支援/格式錯誤。可能原因分析：無對應 Codec、檔案毀損、流未重置。解決步驟：1) 安裝 Canon RAW Codec；2) 檢查檔案完整性；3) 實作回退至內嵌預覽。預防措施：在載入前檢查副檔名與魔術數、加上例外處理與逾時、記錄錯誤以利診斷。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, B-Q24, C-Q4

D-Q3: CRW 檔在 Vista 無法預覽/開啟怎麼辦？
- A簡: 多數情況未受支援，建議以工具轉 DNG/TIFF。
- A詳: 問題症狀描述：Explorer 無縮圖，WPF/相片應用無法開啟。可能原因分析：當時 Codec 僅支援 CR2、無 CRW 解碼。解決步驟：1) 以原廠 DPP 或 DNG Converter 轉檔；2) 使用支援 CRW 的第三方軟體瀏覽；3) 保留原始檔備份。預防措施：規劃轉檔流程，統一存檔格式，建立色彩/中繼一致策略。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, C-Q5, B-Q20

D-Q4: RAW 顏色偏差或過飽和如何修正？
- A簡: 檢查色彩管理，調整白平衡與工作色域。
- A詳: 問題症狀描述：顏色偏移、膚色不自然、對比過強。可能原因分析：顯示器 ICC 不正確、Codec 預設曲線差異、白平衡不合。解決步驟：1) 校正顯示器與套用正確 ICC；2) 在支援的應用調整白平衡/曝光；3) 使用 RAW 編輯器輸出正確色域。預防措施：維持色彩管理流程、統一 sRGB/AdobeRGB、定期校色。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q24, B-Q16, C-Q8

D-Q5: 64 位元程式仍無法載入 Codec？
- A簡: 可能僅安裝 x86 版本，補裝 x64 版本解決。
- A詳: 問題症狀描述：x64 應用報不支援，但 x86 正常。可能原因分析：Codec 僅有或僅安裝了 x86 版本、COM 註冊缺失。解決步驟：1) 安裝 x64 版 Codec；2) 確認 CLSID 註冊；3) 重啟應用/系統。預防措施：建立位元數盤點清單，於 x64 系統同時部署 x86/x64 版本，避免混淆。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q19, B-Q9, C-Q6

D-Q6: 瀏覽大量 RAW 速度很慢怎麼辦？
- A簡: 先用內嵌縮圖、限制解碼尺寸並啟用快取。
- A詳: 問題症狀描述：資料夾捲動卡頓、CPU 飆高。可能原因分析：每張都全幅解 RAW、缺乏快取、同時解碼過多。解決步驟：1) 啟用縮圖快取；2) 使用內嵌預覽；3) 在應用中設定 DecodePixelWidth；4) 控制並行數。預防措施：預先批次產縮圖；以 SSD 儲存快取；定期清理損壞快取。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, B-Q18, C-Q10

D-Q7: 發生記憶體漏出或當機與 Codec 有關？
- A簡: 可能是 Codec 不穩，更新或回退版本。
- A詳: 問題症狀描述：預覽時 Explorer 或應用偶發崩潰、記憶體不斷攀升。可能原因分析：Codec 漏洞、相依 DLL 衝突、異常檔案觸發。解決步驟：1) 更新至最新穩定版；2) 回退至已驗證版本；3) 以最小樣本重現並回報廠商。預防措施：控管版本、先測試再大量部署、啟用 WER 收集崩潰資料。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q14, A-Q21, B-Q19

D-Q8: 為何無法讀取 RAW 中繼資料？
- A簡: Codec 不支援或使用私有標籤需特別解析。
- A詳: 問題症狀描述：日期、鏡頭資訊或評等缺失。可能原因分析：Codec 未公開私有 MakerNote、XMP 旁註未被合併。解決步驟：1) 使用支援中繼的應用；2) 檢查 XMP 是否同名同路徑；3) 以 WIC MetadataQueryReader 測試可用欄位。預防措施：統一以 XMP 存放編輯中繼；選擇支援良好的 Codec。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q5, B-Q17, C-Q3

D-Q9: 副檔名關聯錯亂或無法開啟 RAW？
- A簡: 重設預設應用，並確認 Codec 與相依套件。
- A詳: 問題症狀描述：雙擊 RAW 未開啟，或用錯程式開啟。可能原因分析：關聯被其他應用變更、Codec 缺失。解決步驟：1) 於系統設定重設預設應用；2) 修復/重裝 Codec；3) 測試在相片應用中開啟。預防措施：在部署中鎖定關聯設定；避免安裝多個重疊套件造成衝突。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, B-Q21, D-Q1

D-Q10: 如何避免下載到惡意或不穩定的 Codec？
- A簡: 使用官網來源、驗證簽章與社群評價。
- A詳: 問題症狀描述：安裝後系統不穩或有警告。可能原因分析：非官方來源、無簽章或被竄改。解決步驟：1) 僅從原廠或可信通道下載；2) 檢查數位簽章與雜湊；3) 使用沙箱/測試機先驗證。預防措施：建立白名單與版本控管、定期更新、保留回退機制與系統還原點。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q21, D-Q7, C-Q1

---

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 RAW 影像？
    - A-Q2: 什麼是 Canon RAW？
    - A-Q3: 什麼是 CR2？
    - A-Q4: 什麼是 CRW？
    - A-Q5: CR2 與 CRW 有何差異？
    - A-Q6: 什麼是 WIC 編解碼器（Codec）？
    - A-Q7: 什麼是 Windows Imaging Component（WIC）？
    - A-Q8: WPF 與 WIC 的關係是什麼？
    - A-Q9: 為什麼在 Vista 需要 Canon RAW Codec？
    - A-Q10: 2007 年釋出的 Canon RAW Codec 支援什麼？
    - A-Q12: 安裝 RAW Codec 的核心價值是什麼？
    - A-Q15: 什麼是 WPF？
    - C-Q1: 如何在 Vista 安裝 Canon RAW Codec？
    - C-Q2: 如何驗證 CR2 縮圖是否生效？
    - D-Q1: CR2 縮圖在 Explorer 不顯示怎麼辦？

- 中級者：建議學習哪 20 題
    - A-Q11: 為何初期僅支援 CR2 而非 CRW？
    - A-Q19: WIC Codec 的 32/64 位元差異是什麼？
    - A-Q20: WIC Codec 與 RAW 編輯器有何差異？
    - A-Q22: RAW 檔的優缺點是什麼？
    - A-Q23: 如何判斷相機是否受 Codec 支援？
    - A-Q24: 為什麼需要顏色管理（ICC/WCS）？
    - B-Q1: WIC 架構如何運作？
    - B-Q2: WPF 載入影像的執行流程為何？
    - B-Q3: 透過 WIC 解碼 CR2 的流程是什麼？
    - B-Q4: Vista 殼層縮圖如何生成？
    - B-Q5: WIC 的中繼資料處理機制是什麼？
    - B-Q8: WIC 解碼效能的關鍵是什麼？
    - B-Q9: x86/x64 Codec 載入規則是什麼？
    - B-Q10: 沒有 Codec 時應用如何回退？
    - B-Q15: WIC 像素格式與轉換如何設計？
    - C-Q3: 如何在 WPF 載入 CR2 影像？
    - C-Q4: 無 Codec 時如何改用內嵌 JPEG？
    - C-Q6: 如何確認應用與 Codec 位元數相容？
    - D-Q2: WPF 載入 CR2 拋出 NotSupportedException？
    - D-Q6: 瀏覽大量 RAW 速度很慢怎麼辦？

- 高級者：建議關注哪 15 題
    - B-Q6: CR2 與 CRW 的容器技術差異是什麼？
    - B-Q7: RAW 解碼的色彩管理與去馬賽克機制？
    - B-Q11: WIC 如何選擇對應的編解碼器？
    - B-Q14: 殼層編解碼器的安全模型與風險？
    - B-Q17: XMP/Sidecar 檔案如何被 WIC 使用？
    - B-Q18: 內嵌縮圖與多幀影像如何處理？
    - B-Q19: 如何診斷 WIC Codec 載入問題？
    - B-Q20: 為何泛用支援 CRW 困難？
    - B-Q22: WIC 與 Windows Color System（WCS）的關係？
    - B-Q23: 程式如何列舉已安裝的 WIC Codec？
    - B-Q24: WIC 錯誤如何映射到 .NET 例外？
    - C-Q8: 如何在 WPF 啟用色彩管理以正確顯示？
    - C-Q10: 如何測量解碼效能並最佳化快取？
    - D-Q4: RAW 顏色偏差或過飽和如何修正？
    - D-Q7: 發生記憶體漏出或當機與 Codec 有關？