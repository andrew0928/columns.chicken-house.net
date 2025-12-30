---
layout: synthesis
title: "Digital Camera Filer - Source Code (update)"
synthesis_type: faq
source_post: /2006/11/18/digital-camera-filer-source-code-update/
redirect_from:
  - /2006/11/18/digital-camera-filer-source-code-update/faq/
---

# Digital Camera Filer - Source Code (update) 常見問答集

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

Q1: 什麼是 Digital Camera Filer 工具？
- A簡: 一個以 .NET 開發的媒體歸檔工具，依副檔名與 EXIF 資訊自動分類相片與影片，採工廠模式與屬性標註支援擴充與外掛。
- A詳: Digital Camera Filer 是一個以 .NET 2.0 與 Visual Studio 2005 開發的數位相機媒體歸檔小工具。它會遞迴掃描資料夾找出相片與影片，依檔案類型分派給對應的 MediaFiler 類別，讀取 EXIF 或縮圖資訊進行檔名規範與搬移。程式設計上採用 Factory Pattern 與反射，搭配自訂屬性 MediaFilerFileExtensionAttribute 指定各 MediaFiler 支援的副檔名，達到鬆耦合與外掛式擴充。內建以 PhotoLibrary 讀取 EXIF，並透過 Microsoft RAW Image Viewer 包含的 Canon SDK 處理 Canon RAW 與 .thm 縮圖配對。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q6, B-Q1

Q2: 這個工具主要解決什麼問題與痛點？
- A簡: 解決相機檔案雜亂無章，依拍攝資訊自動整理命名與歸檔，支援 RAW 與縮圖配對，降低手動管理成本。
- A詳: 數位相機常產生大量檔案，包含 JPEG、RAW、影片及相機產生的 .thm 縮圖，手動分類與命名耗時且易錯。此工具自動遞迴掃描來源資料夾，依副檔名選用對應 MediaFiler，讀取 EXIF 拍攝時間或使用縮圖配對等資訊，將檔案命名與搬移至預期位置。透過工廠模式與屬性標註，加入新格式不需改動既有程式碼，亦可外掛部署，讓整理流程可維護、可擴充與可重複。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, A-Q7, B-Q12

Q3: 什麼是 MediaFiler？在系統中扮演什麼角色？
- A簡: MediaFiler 是抽象基類，定義處理特定檔案格式的歸檔行為，各格式實作各自子類。
- A詳: MediaFiler 為抽象類別，是系統處理單一檔案格式之行為的統一介面。每種檔案類型各自實作一個對應的 MediaFiler 子類，例如 JpegMediaFiler、CanonRawMediaFiler、CanonVideoMediaFiler。主程式遞迴找出所有檔案後，透過工廠以副檔名與屬性標註動態選出合適的 MediaFiler，將個別檔案交由它完成讀取 EXIF 或縮圖資訊、命名與搬移等歸檔流程。此設計將檔案類型差異封裝，讓新增格式只需新增子類而不影響既有邏輯。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q4, A-Q5, B-Q1

Q4: 什麼是 CanonPairThumbMediaFiler？為何需要它？
- A簡: 一個抽象類別，專處理會附帶 .thm 縮圖的檔案格式，封裝主檔與縮圖配對邏輯。
- A詳: 某些 Canon 相機產生的 RAW 或影片檔會附帶同名 .thm 縮圖檔，內容為 JPEG 格式的縮圖。CanonPairThumbMediaFiler 是抽象類別，負責抽象化處理這類成雙出現的檔案，包括找到對應的 .thm、驗證一致性、同步命名與搬移等共通步驟。具體的 CanonRawMediaFiler 與 CanonVideoMediaFiler 便可繼承它，針對 RAW 與 AVI 的差異覆寫各自細節。此抽象層降低重複程式碼並統一處理規則。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q6, D-Q5

Q5: JpegMediaFiler、CanonRawMediaFiler 與 CanonVideoMediaFiler 有何差異？
- A簡: 三者皆處理歸檔但對象不同：JPEG 單檔，RAW 與影片需處理對應 .thm 縮圖與特定讀取庫。
- A詳: JpegMediaFiler 處理副檔名 .jpg 的相片，通常只需讀取 EXIF 拍攝時間並據此命名與搬移。CanonRawMediaFiler 針對 .crw RAW 檔，常需搭配 .thm 縮圖，並透過 Microsoft RAW Image Viewer 的 Canon SDK 包裝器取得必要資訊。CanonVideoMediaFiler 針對 .avi 影片，同樣考慮 .thm 的配對處理。RAW 與影片類型共同繼承 CanonPairThumbMediaFiler 以共用縮圖配對與同步作業。三者在輸入來源與依賴庫、處理流程與錯誤處理都有所不同。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, B-Q7, B-Q8

Q6: 什麼是 Factory Pattern？本工具為何採用？
- A簡: 工廠模式以統一入口建立物件，隔離類型選擇；本工具用副檔名選出對應 MediaFiler。
- A詳: Factory Pattern 提供一個集中化的建立物件機制，將類型判斷與建構過程封裝於工廠方法，呼叫端僅據需求取得正確實例。在本工具中，工廠方法 Create(sourceFile) 會掃描可用的 MediaFiler 子類，依自訂屬性標註的副檔名比對選出正確類別，透過反射建立實例。此作法讓主流程與類型選擇解耦，新增支援格式只需新增類別與屬性，工廠核心無須修改，達成開放封閉原則與外掛式擴充。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q3, A-Q16

Q7: 什麼是 EXIF？為何在歸檔中重要？
- A簡: EXIF 是相片內嵌拍攝資訊標準，包含日期等；用於命名與分類的依據。
- A詳: EXIF（Exchangeable Image File Format）是數位相片內嵌的中繼資料標準，包含拍攝日期時間、相機型號、曝光參數等。歸檔時常以拍攝時間作為檔名與目錄結構依據，較檔案建立時間可靠，能反映實際拍攝順序。本工具透過 PhotoLibrary 封裝 System.Drawing.Image 讀取 EXIF，將時間資訊用於規則化命名與搬移。若無 EXIF，則需退回以檔案時間或縮圖輔助判斷，降低資料錯誤。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q10, C-Q5, D-Q4

Q8: .THM 縮圖檔是什麼？為何會隨檔案出現？
- A簡: .thm 是相機產生的縮圖檔，內含 JPEG 縮圖，常與 RAW 或影片同名成對出現。
- A詳: 許多相機在拍攝 RAW 或錄製影片時，會額外生成一個 .thm 副檔名的縮圖檔，內容為 JPEG 縮圖，供快速預覽與管理軟體使用。這些縮圖通常與主檔同名且位於相同資料夾。本工具設計了 CanonPairThumbMediaFiler 抽象類別，協助尋找配對的 .thm，並在命名與搬移時維持主檔與縮圖同步，以確保預覽與後續處理的連續性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, B-Q6, D-Q5

Q9: 什麼是 Microsoft RAW Image Viewer？在專案中如何使用？
- A簡: 微軟提供的 RAW 檢視器，包含 Canon SDK 與 .NET 包裝，用以處理 CRW 等 RAW。
- A詳: Microsoft RAW Image Viewer 是微軟早期提供的 RAW 檔檢視工具，內含部分廠商 SDK 與 .NET 包裝元件，能協助讀取像 Canon .crw 的 RAW 檔資訊。在本專案中，它提供處理 Canon RAW 所需的 API，使 CanonRawMediaFiler 能取用必要的中繼資料或縮圖，並與 .thm 檔協同運作。不過此元件年代久遠，部署時需確保相容性與授權條款符合，並處理例外狀況。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, D-Q6, C-Q1

Q10: 什麼是 PhotoLibrary？它解決了哪些問題？
- A簡: 一個封裝 System.Drawing.Image 的函式庫，簡化 EXIF 等相片中繼資料讀取。
- A詳: PhotoLibrary 是第三方函式庫，將 System.Drawing.Image 相關操作封裝成較易用的介面，特別是讀取 EXIF 中繼資料如拍攝日期、相機資訊等。對於 JpegMediaFiler 等需要從 JPEG 取用拍攝時間以進行檔名或目錄分類的場景，使用 PhotoLibrary 可避免自行解析標籤，縮短開發時間並降低錯誤。它屬於非核心但關鍵的基礎能力元件。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q10, C-Q5, D-Q4

Q11: 為何使用自訂 Attribute 而非要求子類提供抽象靜態方法？
- A簡: C# 當時無法強制靜態多型，自訂屬性可在無實例前提供比對資訊。
- A詳: 類型選擇需在建立實例之前完成，若要求子類以抽象方法提供副檔名，必須先有實例才能呼叫，多型只對實例方法有效；而 C# 2.0 並無可強制的抽象靜態成員機制。自訂屬性 MediaFilerFileExtensionAttribute 可直接標註在類別上，工廠以反射掃描型別與屬性，不需建立實例便能比對副檔名並決定要建立哪個類別，精準解決靜態多型的缺口。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q1, A-Q12

Q12: Attribute 與多型在此架構中的關係是什麼？
- A簡: 屬性提供類型選擇的中繼資料，多型負責各子類的行為差異，各司其職。
- A詳: 在本架構中，自訂屬性負責在編譯時標註類別的能力（支援副檔名），工廠於執行時以反射讀取屬性做型別選擇；完成選擇並建立實例後，才進入多型階段，由基底 MediaFiler 抽象介面分派到各子類的具體實作。換言之，屬性解決「在多型前如何選類別」，多型解決「選定類別後如何差異化執行」。兩者串接，形成鬆耦合且可擴充的處理管線。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q1, B-Q4

Q13: 什麼是外掛式（plug-in）架構？此專案如何支援？
- A簡: 外掛讓功能以獨立組件裝載；此專案掃描 AppDomain 組件自動辨識新 MediaFiler。
- A詳: 外掛式架構將新功能封裝在獨立組件，主程式於執行時載入與發現，無須重編主程式。在此專案中，工廠會掃描已載入 AppDomain 的所有組件，尋找繼承 MediaFiler 且貼有 MediaFilerFileExtensionAttribute 的類型。一旦找到副檔名匹配的類型，即以反射建立實例執行。開發者只需在新類別庫中實作 MediaFiler 子類與屬性標註，將 DLL 放在同一目錄，主程式即能支援新檔案格式，達成外掛效果。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q9, C-Q2, D-Q3

Q14: 遞迴掃描檔案在此工具中的角色與意義？
- A簡: 遞迴掃描遍歷來源樹，將每個檔案交給工廠選派 MediaFiler，形成處理流水線。
- A詳: 主程式核心首先從指定根目錄開始遞迴列舉所有子目錄與檔案，對每一個檔案呼叫工廠 Create(sourceFile) 取得對應的 MediaFiler 實例，接著呼叫其處理方法完成 EXIF 讀取、命名與搬移。遞迴掃描確保不遺漏任何深層檔案，並將檔案處理與檔案發現清楚分離。此流程是將資料輸入與策略選擇連接起來的膠水，支撐整體管道化處理。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q12, C-Q7, D-Q7

Q15: MediaFiler 架構的核心價值是什麼？
- A簡: 封裝格式差異、促進擴充與維護，讓新增格式不影響既有流程與工廠核心。
- A詳: MediaFiler 以抽象類別統一定義處理界面，將各檔案格式的差異與依賴封裝在各自子類，讓主程式不感知細節。配合自訂屬性進行靜態選擇與反射實例化，新增格式僅需新增類別與標註，工廠與主流程無需修改。這種遵循開放封閉原則的設計降低耦合、提升測試性與可維護性，並使外掛化部署成為可能。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q6, A-Q16, B-Q1

Q16: 為什麼不用修改 Factory Create 就能支援新格式？
- A簡: 因工廠以反射掃描類型與屬性比對副檔名，新增類別即自動被發現。
- A詳: Factory Create(sourceFile) 的流程是通用的：掃描可用 MediaFiler 類型清單，讀取 MediaFilerFileExtensionAttribute 的副檔名，與輸入檔案副檔名做忽略大小寫比對，找到後反射呼叫 string 建構子建立實例。這個流程不依賴任何特定格式的硬編碼判斷，因此當新增一個貼好屬性的子類並放在可載入的組件中，工廠便能自動發現與使用它。支援新格式無需改動工廠方法本身。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q3, C-Q2

### Q&A 類別 B: 技術原理類

Q1: Factory Create(sourceFile) 的執行流程是什麼？
- A簡: 掃描型別→過濾繼承與屬性→比對副檔名→取 string 建構子→反射建立實例。
- A詳: Create 先以 FileInfo 取得來源副檔名，呼叫 GetAvailableMediaFilers 列舉已載入 AppDomain 的所有型別。過濾條件包含：型別需繼承 MediaFiler，且類別貼有 MediaFilerFileExtensionAttribute。對每個候選型別讀取屬性中的 FileExtension，與來源副檔名做不區分大小寫的比較；若匹配，則以反射取得簽章為 (string) 的建構子，並以來源路徑為參數呼叫 ctor.Invoke 建立實例。若無任何匹配則回傳 null。此流程將型別選擇與建立統一化處理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, A-Q16, B-Q3

Q2: GetAvailableMediaFilers 如何取得待比對的型別集合？
- A簡: 掃描目前 AppDomain 已載入的所有組件，列舉其型別並過濾符合條件者。
- A詳: 在 .NET 執行環境中，AppDomain 維持已載入組件清單。可透過 AppDomain.CurrentDomain.GetAssemblies() 取得組件，對每個 assembly 呼叫 GetTypes() 列舉型別，接著以 IsSubclassOf(typeof(MediaFiler)) 與是否貼有 MediaFilerFileExtensionAttribute 做初步過濾，形成候選清單。如此可自動包含主程式與任何同目錄可被載入的外掛組件，達成動態擴充。需留意反射列舉例外、安全性與效能開銷。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q9, D-Q9

Q3: 透過自訂 Attribute 比對副檔名的機制是什麼？
- A簡: 在類別上貼 MediaFilerFileExtensionAttribute，工廠反射讀取 FileExtension 比對檔案。
- A詳: 自訂屬性 MediaFilerFileExtensionAttribute 定義一個公開屬性 FileExtension，指明該 MediaFiler 子類負責的副檔名。工廠以 Type.GetCustomAttributes 取得此屬性實例，讀出 FileExtension，與來源 FileInfo.Extension 做不分大小寫的字串比對。符合則視為相容處理器。此方式將對應關係由程式碼條件移至中繼資料，讓新增支援只需貼標註，避免修改判斷式並消除硬編碼表列。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, A-Q12, B-Q1

Q4: 反射建立 MediaFiler 實例的關鍵步驟是什麼？
- A簡: 尋找 (string) 建構子→ConstructorInfo 取得→Invoke 傳入來源路徑→取得實例。
- A詳: 當找到副檔名匹配的型別後，工廠呼叫 Type.GetConstructor(new Type[]{typeof(string)}) 取得接受單一 string 參數的建構子。接著以 ctor.Invoke(new object[]{sourceFile}) 呼叫建構子，回傳值轉型為 MediaFiler。此設計假設所有 MediaFiler 子類都有一致的建構子簽章，讓工廠無需知道類別細節即可建立實例。若建構子缺失或存取限制，會拋出例外或導致 null，需妥善防護。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q2, C-Q1, C-Q2

Q5: 為何選擇掃描 AppDomain 已載入的組件，而非手動維護清單？
- A簡: 可自動發現外掛、減少硬編碼與維護成本，同時維持鬆耦合擴充性。
- A詳: 掃描 AppDomain 的優勢在於不需手動維護類型對應清單，避免新增格式時修改配置或程式。外掛組件放至同目錄並載入後，自然出現在掃描結果，符合屬性條件便可用。此作法實現自動發現，提高部署彈性與可維護性。其代價是啟動掃描的反射開銷與安全控管需求，通常可透過快取與白名單策略緩解。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q9, D-Q9, D-Q10

Q6: CanonPairThumbMediaFiler 處理主檔與 .thm 的流程為何？
- A簡: 尋找同名 .thm→驗證存在與一致→同步命名與搬移→錯誤時採補救策略。
- A詳: 流程包含：從主檔路徑推導同名 .thm 路徑；檢查縮圖是否存在且格式為 JPEG；若存在則在命名或搬移主檔時，同步對縮圖套用相同規則，確保兩者關聯不丟失。若 .thm 缺失，依設定採忽略、記錄或以主檔中繼資料補救。此抽象流程由 CanonRawMediaFiler 與 CanonVideoMediaFiler 繼承與覆寫其特定差異，例如 RAW 資訊來源或影片時間戳推導。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, D-Q5, C-Q6

Q7: JpegMediaFiler 的典型歸檔流程是什麼？
- A簡: 讀 EXIF 拍攝時間→生成目錄與檔名→搬移檔案，記錄結果與例外。
- A詳: 對 JPEG，相對單純。步驟為：以 PhotoLibrary 讀取 EXIF 的 DateTimeOriginal；若無則回退使用檔案建立或修改時間；依約定的命名規則組合目錄與檔名，如依日期分層與序號；檢查目標是否衝突，必要時附加去重後綴；執行搬移與寫入日誌。此流程將 EXIF 作為真實世界時間來源，提升整理品質。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q10, D-Q4

Q8: CanonRawMediaFiler 與 CanonVideoMediaFiler 的機制差異是什麼？
- A簡: RAW 倚賴 Canon SDK 讀中繼資料，影片則以檔案或縮圖時間，兩者皆同步處理 .thm。
- A詳: CanonRawMediaFiler 使用 Microsoft RAW Image Viewer 所含的 Canon SDK 或包裝以讀取 RAW 特有的中繼資料或縮圖；影片檔缺乏 EXIF，通常以檔案時間或 .thm 內的 JPEG EXIF 近似推導時間。兩者共同處理 .thm 的發現、驗證與同步命名。錯誤處理也不同：RAW 側重解碼與 SDK 相容性，影片則側重時間來源的可靠性與文件系統操作。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q6, B-Q11, D-Q6

Q9: 外掛部署後，主程式如何自動偵測到新格式支援？
- A簡: DLL 放入同目錄→被載入 AppDomain→掃描到繼承與標註→比對副檔名即生效。
- A詳: 將含新 MediaFiler 子類的類別庫 DLL 放至主程式可發現的目錄，程式啟動或掃描時載入該組件。工廠掃描 AppDomain 上的組件與型別，過濾出繼承 MediaFiler 且貼有 MediaFilerFileExtensionAttribute 的類別。當有檔案副檔名與標註匹配，即以反射建立該類實例，無需修改或重編主程式。若需熱插拔與載入順序控制，可配合設定與顯式 Assembly.Load。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q13, C-Q2, D-Q3

Q10: 使用 PhotoLibrary 讀取 EXIF 的原理與介面為何？
- A簡: 封裝 GDI+ 影像屬性存取，提供友善 API 讀取 EXIF 標籤如拍攝時間。
- A詳: System.Drawing.Image 透過 PropertyItems 暴露 EXIF，但使用繁雜。PhotoLibrary 將常用標籤如 DateTimeOriginal 以強型別或易用方法封裝，處理編碼、ID 與格式轉換，開發者僅呼叫簡單 API 取得字串或 DateTime。此封裝降低直接操作 GDI+ 的風險，並提升可讀性與可靠性，適合在 JpegMediaFiler 中直接取用。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q10, C-Q5, D-Q4

Q11: 使用 Microsoft RAW Image Viewer 處理 CRW 的流程是什麼？
- A簡: 初始化 SDK→開檔讀中繼或縮圖→取得必要資訊→關閉與釋放資源。
- A詳: 以該檢視器提供的 .NET 包裝初始化 Canon SDK，開啟 .crw 檔取得中繼資料或縮圖資料流；若需時間資訊而 RAW 無標準 EXIF，則依 SDK 提供的欄位或以 .thm 補充。完成後關閉檔案並釋放 SDK 資源。因年代久遠，需注意作業系統相容性、授權與例外處理，並在不可用時提供退讓策略。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q9, D-Q6, C-Q1

Q12: 主程式如何將遞迴掃描結果派發到各 MediaFiler？
- A簡: 列舉檔案→呼叫 Factory.Create→若有實例則執行處理→記錄結果與錯誤。
- A詳: 主流程負責檔案發現，對每個檔案呼叫工廠取得對應 MediaFiler；若回傳非空，則調用其處理方法完成命名搬移，若為 null 表示不支援則略過或記錄。流程中應加強錯誤捕捉、防止單一檔案失敗中斷整體，並於結束提供統計報表。此派發模式將掃描與處理分離，便於測試與擴展。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q14, D-Q1, C-Q7

Q13: 當檔案量巨大時，如何設計型別快取以提升工廠效能？
- A簡: 預先建立副檔名到建構子委派的快取字典，避免重複反射與掃描。
- A詳: 啟動時掃描一次 AppDomain，過濾出符合條件的型別，為每個副檔名建立至 ConstructorInfo 或 Activator 委派的映射表，例如 Dictionary<string,Func<string,MediaFiler>>；之後每次 Create 先查快取直接呼叫委派建立實例，避免重複掃描與反射查找建構子。若支援熱外掛，可在檔案監視事件發生時更新快取。此策略可顯著降低高併發或大量檔案處理時的開銷。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q8, D-Q7, D-Q9

Q14: 反射與外掛載入帶來的安全風險有哪些？如何降低？
- A簡: 可能載入不可信程式碼、型別欺騙與資源濫用；可用白名單、簽章與沙箱。
- A詳: 反射掃描外掛可能執行不可信 DLL，導致惡意程式碼、型別衝突或資源濫用。降低風險可採用簽章驗證與強名稱白名單、限制外掛搜尋目錄、最小權限原則、隔離 AppDomain 或進程、加上 Timeouts 與例外防護，並記錄稽核日誌。對屬性與建構子也應驗證存在與可見性，拒絕不合規的型別，避免型別欺騙。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: D-Q10, B-Q5, C-Q9

### Q&A 類別 C: 實作應用類（10題）

Q1: 如何新增一個支援 .NEF（Nikon RAW）的 MediaFiler？
- A簡: 建立繼承 MediaFiler 的類別，貼上副檔名屬性，實作處理流程並加入相容讀取庫。
- A詳: 具體步驟：1) 建立類別庫專案，新增 class NikonRawMediaFiler : MediaFiler。2) 在類別上貼 [MediaFilerFileExtension(".nef")]。3) 在建構子接收 sourceFile 路徑，於處理方法中讀取 NEF 所需的中繼資料（需引入相容的 NEF 解碼或中繼讀取庫），推導時間與命名規則。4) 完成搬移與日誌。5) 編譯 DLL 放至主程式目錄。程式碼片段示例：[MediaFilerFileExtension(".nef")] public class NikonRawMediaFiler : MediaFiler { public NikonRawMediaFiler(string path){...} public override void Process(){...} } 注意：選用授權合規的 NEF 讀取庫並處理無 EXIF 的退讓。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q9, B-Q11, C-Q2

Q2: 如何在新組件中實作外掛並讓主程式自動辨識？
- A簡: 在 DLL 中實作子類並標註屬性，確保放在同目錄且可載入，重啟即生效。
- A詳: 步驟：1) 建立 Class Library 專案，參考主程式之共用抽象（含 MediaFiler 與屬性定義）。2) 新增子類並貼 [MediaFilerFileExtension(".ext")]。3) 實作一致的建構子與處理方法。4) 編譯產生 DLL，放入主程式執行目錄。5) 啟動或重新啟動主程式，工廠掃描 AppDomain 時將自動發現。最佳實踐：外掛以語意化版本與簽章管理，避免衝突；提供自我診斷日誌；若需熱載可加入 AssemblyResolve 與檔案監聽。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q13, B-Q9, D-Q3

Q3: 如何撰寫 MediaFilerFileExtensionAttribute？
- A簡: 定義繼承 Attribute 的類別，暴露 FileExtension 屬性並限定可套用在 class。
- A詳: 實作範例： [AttributeUsage(AttributeTargets.Class, Inherited=false, AllowMultiple=false)] public sealed class MediaFilerFileExtensionAttribute : Attribute { public string FileExtension {get;} public MediaFilerFileExtensionAttribute(string ext){ FileExtension = ext; } } 使用時貼於子類：[MediaFilerFileExtension(".jpg")] class JpegMediaFiler : MediaFiler {...} 工廠透過 t.GetCustomAttributes(typeof(MediaFilerFileExtensionAttribute), false) 取得屬性。注意：統一副檔名格式（含點、大小寫），避免多重標註造成歧義。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q1, D-Q2

Q4: 如何在 Visual Studio 2005 建立類別庫並部署外掛？
- A簡: 新建 Class Library→參考共用抽象→實作子類與屬性→建置 DLL→複製至主程式目錄。
- A詳: 操作步驟：1) New Project 選 Class Library。2) 加入參考指向含 MediaFiler 與 Attribute 的共用組件。3) 新增檔案實作子類與 [MediaFilerFileExtension] 標註，提供 public 類別與 public (string) 建構子。4) 設定組件版本與強名稱（可選）。5) Build 產出 DLL。6) 將 DLL 複製到主程式 .exe 同一資料夾。7) 啟動並測試。最佳實踐：加入後置事件自動複製、提供外掛描述檔與日誌。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q2, B-Q9, D-Q3

Q5: 如何使用 PhotoLibrary 讀取 JPEG EXIF 的拍攝日期？
- A簡: 以 PhotoLibrary 開檔，讀取 DateTimeOriginal，解析為 DateTime 作為命名依據。
- A詳: 範例步驟：1) 使用 PhotoLibrary API 載入檔案，如 var photo = Photo.Load(path); 2) 讀取 DateTimeOriginal 或 CreateDate：var dt = photo.Exif.DateTimeOriginal ?? photo.Exif.CreateDate; 3) 將字串轉為 DateTime，格式化為命名字串如 yyyyMMdd_HHmmss；4) 檢查空值採用檔案時間回退。注意：處理不同地區時間與時區，當 EXIF 缺失或破損需記錄與回退。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q10, D-Q4

Q6: 如何處理與搬移 .thm 縮圖使其與主檔同步？
- A簡: 以主檔名推導 .thm 路徑，驗證存在，命名搬移時對兩檔套同規則。
- A詳: 步驟：1) var thm = Path.ChangeExtension(mainPath, ".thm"); 2) if(File.Exists(thm)){ 3) 依主檔的命名結果 targetMain 推導 targetThm = Path.ChangeExtension(targetMain,".thm"); 4) 確保目錄存在 Directory.CreateDirectory(Path.GetDirectoryName(targetThm)); 5) File.Move(thm, targetThm); } else 記錄遺失並採策略。最佳實踐：檢查 .thm 內容為 JPEG，衝突時採去重命名，整體操作以交易性順序避免部分成功。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, D-Q5, A-Q8

Q7: 如何調整遞迴掃描的根目錄與輸出目的地？
- A簡: 在主程式設定來源與輸出路徑參數，遞迴列舉來源，MediaFiler 以輸出規則搬移。
- A詳: 典型作法：1) 於主程式支援從組態或命令列讀取 sourceRoot 與 targetRoot。2) 使用 Directory.EnumerateFiles(sourceRoot,"*",SearchOption.AllDirectories) 遞迴列舉。3) 工廠建立 MediaFiler 後，於處理方法中以 targetRoot 與規則生成最終路徑並搬移。注意：確認路徑權限、處理長路徑與非法字元，並避免跨磁碟搬移造成大量 IO，可先在相同磁碟重命名再移動。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q12, D-Q8, D-Q7

Q8: 如何為工廠建立型別清單快取以優化效能？
- A簡: 啟動時掃描建構字典映射副檔名→委派，Create 時直接查表呼叫。
- A詳: 程式碼要點：static Dictionary<string,Func<string,MediaFiler>> map; static void Init(){ map=new(); foreach(var t in GetAvailableMediaFilers()){ var ext=GetAttr(t).FileExtension.ToLowerInvariant(); var ctor=t.GetConstructor(new[]{typeof(string)}); var del=(Func<string,MediaFiler>)(s=> (MediaFiler)ctor.Invoke(new object[]{s})); map[ext]=del; } } MediaFiler Create(path){ var ext=Path.GetExtension(path).ToLowerInvariant(); return map.TryGetValue(ext,out var f)? f(path): null; } 注意：處理外掛更新時的快取重建與同步鎖。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q13, D-Q7, D-Q9

Q9: 如何為反射實例化加入錯誤處理與記錄？
- A簡: 捕捉缺建構子、Invoke 例外與型別不符，記錄屬性資料與檔案路徑便於追蹤。
- A詳: 在工廠 Create 包裹 try-catch，分辨 MissingMethodException（無 string 建構子）、TargetInvocationException（內部例外）、InvalidCastException（非 MediaFiler）。記錄內容包含：類型名稱、屬性副檔名、來源副檔名、堆疊與檔名。失敗時回退為 null 並於總結報表列出。亦可加入重試或隔離問題外掛至隔離清單，避免反覆失敗拖慢流程。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: D-Q2, D-Q3, B-Q4

Q10: 如何撰寫單元測試驗證新 MediaFiler 行為？
- A簡: 以假檔案與測試資料夾，驗證 EXIF 取值、命名與搬移結果及錯誤情境。
- A詳: 測試要點：1) 建立臨時資料夾與測試檔案，必要時植入 EXIF 或 .thm。2) 呼叫工廠建立對應 MediaFiler，執行處理。3) 斷言輸出目錄與檔名符合規則、.thm 同步性、衝突處理。4) 模擬缺 EXIF、.thm 遺失、目標已存在等異常。5) 使用測試替身抽換檔案系統操作以加速與避免實 IO。6) 清理現場。確保測試涵蓋核心邏輯與退讓策略。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: D-Q4, D-Q5, C-Q1

### Q&A 類別 D: 問題解決類（10題）

Q1: 工廠 Create 回傳 null（找不到合適 MediaFiler）怎麼辦？
- A簡: 檢查副檔名大小寫與屬性標註、外掛是否載入、快取是否更新與白名單限制。
- A詳: 症狀：特定檔案未被處理，Create 回傳 null。可能原因：1) 檔案副檔名不符合任何屬性標註或大小寫不一致。2) 外掛 DLL 未放在可載入目錄或未載入 AppDomain。3) 工廠快取未重建。4) 安全策略阻擋外掛。解法：確認子類標註如“.ext”一致、檔案副檔名正確；確保外掛部署目錄與載入時機；重建型別快取或重啟程式；檢查簽章或白名單設定。預防：加入啟動檢查列出可用處理器與副檔名清單。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q9, C-Q8

Q2: 反射建立實例失敗（缺少 string 建構子）如何處理？
- A簡: 例外顯示 MissingMethod，補上 public (string) 建構子或調整工廠建構邏輯。
- A詳: 症狀：TargetInvocation 或 MissingMethod 例外。原因：子類未提供 public 建構子接收來源路徑，或存取修飾錯誤。解法：為所有 MediaFiler 子類新增 public ClassName(string sourceFile) 建構子；或在工廠加入更彈性建構邏輯，如支援無參數建構加後設置屬性。預防：於外掛驗證流程檢查建構子存在；將此規範寫入開發指引與單元測試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, C-Q3, C-Q9

Q3: 外掛組件未被偵測（新格式無法生效）如何診斷？
- A簡: 檢查 DLL 位置與版本、相依性、簽章與白名單、AppDomain 載入與掃描時機。
- A詳: 症狀：外掛 DLL 放入後無作用。原因：放錯目錄、相依組件缺失、平台不相容、未載入 AppDomain、掃描在載入前完成、安全限制。解法：將 DLL 同目錄或設定探查路徑；使用 Fusion Log 或載入日誌檢查相依性；確保目標 .NET 版本與位元數一致；在程式啟動時顯式 Assembly.Load；延後或重觸發掃描；檢查簽章與白名單。預防：提供外掛健康檢查工具與清晰部署說明。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q9, B-Q5, C-Q4

Q4: EXIF 讀取失敗或時間為空的原因與解法？
- A簡: 檔案無 EXIF、標籤缺失或損壞、解碼庫不支援；改用檔案時間或縮圖退讓。
- A詳: 症狀：取得 DateTimeOriginal 為空或例外。原因：相片經編輯移除 EXIF、相機未寫入、檔案損壞、讀取庫不支援特定格式。解法：以 CreateDate、ModifyDate 或檔案系統時間回退；對 RAW 以 SDK 或 .thm 內 JPEG EXIF 推導；記錄無法確定的檔案供人工處理。預防：在流程中加入多層退讓與一致性檢查，並對編輯軟體導致的 EXIF 損失加以提醒。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q10, C-Q5

Q5: .THM 縮圖遺失或不匹配該如何處理？
- A簡: 檢查同名存在與內容格式，遺失則記錄並跳過或重建，命名時保持主檔一致。
- A詳: 症狀：找不到 .thm 或與主檔不同名。原因：同步失誤、使用者移動、相機未生成。解法：以主檔名推導 .thm 路徑，若遺失則記錄並僅處理主檔；或嘗試從 RAW/影片抽取縮圖重建；若多個 .thm 衝突，採最近時間或大小規則。預防：處理時採原子性順序、批次操作保證主縮圖同步，並於日誌中警示異常。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q6, A-Q8

Q6: 處理 CRW/RAW 檔讀取錯誤時如何排查？
- A簡: 確認 RAW Image Viewer 與 SDK 安裝與相容性、檔案完整性與權限，再設退讓。
- A詳: 症狀：開啟 RAW 失敗、拋出 SDK 例外。原因：SDK 未安裝或版本不符、OS 相容性差、檔案損壞、權限不足。解法：安裝或更新 Microsoft RAW Image Viewer，檢查相依 DLL；以另一工具驗證檔案完整；在權限足夠的環境重試；無法解碼時回退以 .thm 或檔案時間處理。預防：啟動自檢 SDK 可用性，對不支援格式提前標記不處理。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q11, A-Q9, C-Q1

Q7: 大量檔案處理效能不佳的原因與優化方法？
- A簡: 反射掃描與 IO 瓶頸、重複解碼；採用型別快取、批次 IO、非同步與重用實體。
- A詳: 原因：每檔案反覆掃描型別與反射、隨機 IO、重複讀取 EXIF。優化：啟動建快取將副檔名映射至建構委派；將檔案按副檔名分組，降低切換成本；批次建立目錄與搬移；非同步處理與並行度控制；重用 PhotoLibrary 實例或緩存時間資訊；寫入日誌合併批次。預防：提供效能統計，及早發現瓶頸並調整策略。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q13, C-Q8, B-Q12

Q8: 因權限或路徑問題導致搬移失敗怎麼辦？
- A簡: 檢查目標目錄存在與權限、長路徑與非法字元，採用安全重試與回滾。
- A詳: 症狀：IOException、UnauthorizedAccessException。原因：無寫入權限、目錄不存在、路徑過長或含非法字元、目標已存在。解法：預先建立目錄、檢查權限、正規化檔名移除非法字元、衝突時採去重規則、使用 File.Replace 提供回滾。預防：啟動前測試目標路徑可寫，提供模擬模式先驗證命名與路徑。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q7, B-Q7, C-Q9

Q9: 組件掃描造成啟動變慢，如何改善？
- A簡: 啟動預建快取、延遲載入外掛、白名單掃描與結果持久化，必要時分層掃描。
- A詳: 原因：大量組件 GetTypes 費時。解法：將掃描結果序列化快取，版本變動時才重建；以白名單或命名慣例限制掃描範圍；延遲在首次需要時才載入外掛；在背景線程刷新快取。預防：外掛採前綴命名與目錄隔離；提供診斷模式觀察掃描耗時。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q13, C-Q8, B-Q5

Q10: 載入未知外掛的安全風險如何防護？
- A簡: 啟用簽章驗證、白名單、最小權限與隔離執行，強化日誌與審計機制。
- A詳: 風險：惡意程式碼、資料外洩、破壞檔案。防護：要求外掛強名稱簽章與信任憑證；維護白名單與版本控管；以最低必要權限執行；使用隔離 AppDomain 或外部進程，限制可用 API；加入行為與例外日誌，支援審計；為工廠加入型別驗證與黑名單。預防：外掛審核流程與安全指引，定期稽核外掛清單。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q14, B-Q5, C-Q9

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 Digital Camera Filer 工具？
    - A-Q2: 這個工具主要解決什麼問題與痛點？
    - A-Q3: 什麼是 MediaFiler？在系統中扮演什麼角色？
    - A-Q6: 什麼是 Factory Pattern？本工具為何採用？
    - A-Q7: 什麼是 EXIF？為何在歸檔中重要？
    - A-Q8: .THM 縮圖檔是什麼？為何會隨檔案出現？
    - A-Q10: 什麼是 PhotoLibrary？它解決了哪些問題？
    - A-Q14: 遞迴掃描檔案在此工具中的角色與意義？
    - A-Q15: MediaFiler 架構的核心價值是什麼？
    - A-Q16: 為什麼不用修改 Factory Create 就能支援新格式？
    - B-Q1: Factory Create(sourceFile) 的執行流程是什麼？
    - B-Q7: JpegMediaFiler 的典型歸檔流程是什麼？
    - C-Q4: 如何在 Visual Studio 2005 建立類別庫並部署外掛？
    - C-Q5: 如何使用 PhotoLibrary 讀取 JPEG EXIF 的拍攝日期？
    - D-Q1: 工廠 Create 回傳 null（找不到合適 MediaFiler）怎麼辦？

- 中級者：建議學習哪 20 題
    - A-Q4: 什麼是 CanonPairThumbMediaFiler？為何需要它？
    - A-Q5: JpegMediaFiler、CanonRawMediaFiler 與 CanonVideoMediaFiler 有何差異？
    - A-Q11: 為何使用自訂 Attribute 而非要求子類提供抽象靜態方法？
    - A-Q12: Attribute 與多型在此架構中的關係是什麼？
    - A-Q13: 什麼是外掛式（plug-in）架構？此專案如何支援？
    - B-Q2: GetAvailableMediaFilers 如何取得待比對的型別集合？
    - B-Q3: 透過自訂 Attribute 比對副檔名的機制是什麼？
    - B-Q4: 反射建立 MediaFiler 實例的關鍵步驟是什麼？
    - B-Q5: 為何選擇掃描 AppDomain 已載入的組件，而非手動維護清單？
    - B-Q6: CanonPairThumbMediaFiler 處理主檔與 .thm 的流程為何？
    - B-Q9: 外掛部署後，主程式如何自動偵測到新格式支援？
    - B-Q10: 使用 PhotoLibrary 讀取 EXIF 的原理與介面為何？
    - B-Q11: 使用 Microsoft RAW Image Viewer 處理 CRW 的流程是什麼？
    - B-Q12: 主程式如何將遞迴掃描結果派發到各 MediaFiler？
    - C-Q1: 如何新增一個支援 .NEF（Nikon RAW）的 MediaFiler？
    - C-Q2: 如何在新組件中實作外掛並讓主程式自動辨識？
    - C-Q3: 如何撰寫 MediaFilerFileExtensionAttribute？
    - C-Q6: 如何處理與搬移 .thm 縮圖使其與主檔同步？
    - D-Q2: 反射建立實例失敗（缺少 string 建構子）如何處理？
    - D-Q3: 外掛組件未被偵測（新格式無法生效）如何診斷？

- 高級者：建議關注哪 15 題
    - B-Q8: CanonRawMediaFiler 與 CanonVideoMediaFiler 的機制差異是什麼？
    - B-Q13: 當檔案量巨大時，如何設計型別快取以提升工廠效能？
    - B-Q14: 反射與外掛載入帶來的安全風險有哪些？如何降低？
    - C-Q8: 如何為工廠建立型別清單快取以優化效能？
    - C-Q9: 如何為反射實例化加入錯誤處理與記錄？
    - C-Q10: 如何撰寫單元測試驗證新 MediaFiler 行為？
    - D-Q4: EXIF 讀取失敗或時間為空的原因與解法？
    - D-Q5: .THM 縮圖遺失或不匹配該如何處理？
    - D-Q6: 處理 CRW/RAW 檔讀取錯誤時如何排查？
    - D-Q7: 大量檔案處理效能不佳的原因與優化方法？
    - D-Q8: 因權限或路徑問題導致搬移失敗怎麼辦？
    - D-Q9: 組件掃描造成啟動變慢，如何改善？
    - D-Q10: 載入未知外掛的安全風險如何防護？
    - A-Q13: 什麼是外掛式（plug-in）架構？此專案如何支援？
    - A-Q11: 為何使用自訂 Attribute 而非要求子類提供抽象靜態方法？