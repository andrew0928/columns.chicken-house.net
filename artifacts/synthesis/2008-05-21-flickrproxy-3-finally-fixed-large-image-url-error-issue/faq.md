# FlickrProxy #3 - 終於搞定大圖網址錯誤的問題

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 FlickrProxy？
- A簡: 一個以 .NET 為主的 Flickr API 代理，聚焦穩定取得可用圖片尺寸與正確網址，避免壞連結。
- A詳: FlickrProxy 是以 .NET/C# 實作的 Flickr API 代理層，目標是穩定取得照片各尺寸的正確網址，並以快取降低呼叫成本。它從實務問題出發：PhotosGetInfo 的 LargeUrl 在特定情境會錯，改以 PhotosGetSizes 精準查詢可用尺寸，並輸出包含 label、url、width、height 的結構化資料，確保顯示端不再出現「photo not available」。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, A-Q11, B-Q5

A-Q2: 什麼是 Flickr API？
- A簡: 與 Flickr 平台互動的介面，用於上傳、查詢、取得照片資訊與尺寸等。
- A詳: Flickr API 提供一組方法讓應用程式與 Flickr 溝通，包括上傳照片取得 photoId、查詢照片資訊 (如 PhotosGetInfo)、與查詢可用尺寸清單 (PhotosGetSizes)。不同 API 回傳的資料粒度與可靠性不同，像 PhotosGetInfo 以 ID 與格式規則組 URL，易受規則變更影響；PhotosGetSizes 則回傳實際可用尺寸與對應網址，更適合前端顯示使用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q10

A-Q3: 什麼是 PhotosGetInfo API？
- A簡: 依 photoId 取回 PhotoInfo，含多種屬性與以規則組出的 Medium/Large/Original 連結。
- A詳: PhotosGetInfo 接收 photoId，回傳 PhotoInfo 物件，其中包含一系列 ID 與屬性，並依據 Flickr 公布的網址格式組裝出各尺寸 URL，如 MediumUrl、LargeUrl、OriginalUrl。然而當 Flickr 調整格式或該尺寸實體不存在（例如小圖無 Large），以規則湊出的 URL 可能無效，導致顯示「photo not available」或 404。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, A-Q6, B-Q2

A-Q4: 什麼是 PhotoInfo 物件？
- A簡: PhotosGetInfo 的回傳型別，含照片相關 ID 與推導出的各尺寸 URL 屬性。
- A詳: PhotoInfo 是 Flickr API 呼叫 PhotosGetInfo 的回應型別，內含照片標識（如 photoId 等）與方便取用的屬性（如 MediumUrl、LargeUrl、OriginalUrl）。其 URL 多屬「依格式推導」而來，並非 Flickr 即時回報實際存在的尺寸清單，故在 Flickr 更改規格或該尺寸未產生時，屬性可能指向無效網址。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q5, A-Q11

A-Q5: MediumUrl、LargeUrl、OriginalUrl 分別是什麼？
- A簡: 分別對應中等、大圖與原始解析度圖片的 URL，便於前端按需求顯示。
- A詳: 這三個屬性代表不同顯示需求：MediumUrl 常用於一般頁面；LargeUrl 用於大圖預覽；OriginalUrl 為上傳原檔。需注意：在某些照片（檔案很小）可能未生成 Large 版本，此時用規則湊出的 LargeUrl 會失效；且 Original 的網址格式與一般尺寸不同，不可混用固定規則推導。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, A-Q7, B-Q3

A-Q6: 為什麼會出現大圖網址（LargeUrl）錯誤？
- A簡: 因為以格式湊出的 URL 在無 Large 實體或規格改動時會失效。
- A詳: 錯誤源自兩點：其一，PhotosGetInfo 依「公布的網址格式」拼出尺寸 URL，若 Flickr 曾調整格式或該尺寸未產生，拼出的連結即可能錯誤；其二，當照片太小時，Flickr 可能不存 Large 檔，直接以 Original 替代，而 Original 的網址格式又與其他尺寸不同，導致 LargeUrl 指向不存在的資源。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, B-Q3, A-Q11

A-Q7: 為何小圖可能沒有 Large 版本？
- A簡: Flickr 會依原圖大小與需求決定是否產生較大版本，太小時不另存 Large。
- A詳: 為節省儲存與處理成本，Flickr 會對不同上傳大小進行取樣產生多尺寸。若原圖解析度過小，平台判定無需再產生 Large 版本，即以現有最大（常為 Original）作為最高解析度；此時 Large 尺寸實體不存在，導致透過固定規則生成的 LargeUrl 成為壞連結。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q4

A-Q8: 什麼是「以網址格式湊出 URL」？
- A簡: 依照片 ID 與既定命名規則組字串，以得到不同尺寸圖片連結。
- A詳: 部分 API 或套件會根據 Flickr 公布的 URL 模板（包含 server、id、secret、size 後綴等）以字串格式化組出各尺寸連結。此法快速但脆弱，當命名規則變更，或某尺寸實際不存在時，即產生無效 URL。與之對比，查詢服務端「實際可用尺寸清單」更可靠。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, A-Q11

A-Q9: 為何 API 回傳與網站實際 URL 會不一致？
- A簡: 因規格更動與尺寸實體缺席，格式湊出的 URL 與網站使用的不同。
- A詳: Flickr 網站端會依實際可用尺寸動態選用正確圖片 URL；若某尺寸未產生，網站會切換到可用尺寸。而 PhotosGetInfo 以固定格式湊 URL，未實際驗證資源是否存在，當規格變更或尺寸缺席時便與網站採用的連結不同，造成不一致與壞連結。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q11

A-Q10: 什麼是 PhotosGetSizes API？
- A簡: 直接查詢 Flickr 回報的可用尺寸清單，含 label、url、寬高等屬性。
- A詳: PhotosGetSizes 以 photoId 為輸入，回傳一組實際可用尺寸的集合，每筆包含 label、source、url、width、height 等資訊。優點是資料由伺服器明確提供，能保證連結有效，避免因本地湊字串而產生的錯誤，適合前端顯示與尺寸選擇策略。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, B-Q5

A-Q11: PhotosGetInfo 與 PhotosGetSizes 有何差異？
- A簡: 前者以規則推導 URL，後者回傳實際可用尺寸與網址，可靠性高。
- A詳: PhotosGetInfo 重點在照片的描述與識別資訊，並包含「依格式推導」的尺寸 URL；PhotosGetSizes 專注於「可用尺寸實態」，每筆尺寸由伺服器確認存在並附上完整連結與寬高。若目標是正確顯示圖片，PhotosGetSizes 可靠度更高且能避免壞連結。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q10, B-Q5

A-Q12: 什麼是「可用尺寸」？
- A簡: Flickr 已產生並可直接存取的圖片版本集合，包含其實際網址與尺寸。
- A詳: 可用尺寸指的是伺服器端已產生且可公開取用的各種解析度版本。這些版本由 Flickr 依檔案大小與平台策略決定是否生成。使用 PhotosGetSizes 可獲得當下有效的尺寸列表與對應資訊，據此選擇最佳顯示尺寸並建立回退機制。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, B-Q5

A-Q13: 為什麼要改用 PhotosGetSizes？
- A簡: 因它回傳經伺服器確認的實際尺寸與網址，避免規則推導失誤。
- A詳: 改用 PhotosGetSizes 可直接取得 Flickr 當下實際存在的尺寸清單，連同正確 URL 與寬高，消除格式變更與尺寸缺席的風險。相較透過 PhotosGetInfo 以固定模板拼 URL，此做法可靠且可預期，能顯著降低壞連結與重試成本，簡化後續檢查與例外處理。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, B-Q6

A-Q14: 檢查 URL 可用性的用途為何？
- A簡: 在不可靠來源下用以驗證連結有效，避免前端顯示錯誤圖片。
- A詳: 當尺寸 URL 來源不可靠（如以規則湊出）時，程式可能對候選連結逐一發出請求（如 HEAD/GET）以確認可用。此法能降低壞連結風險，但增加延遲與負載。改用 PhotosGetSizes 後，由於 URL 由伺服器確認存在，通常可移除此步驟以提升效能與簡化邏輯。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, C-Q4

A-Q15: 何謂「photo not available」？
- A簡: 當請求圖片不存在或無法存取時，Flickr 顯示的佔位錯誤圖。
- A詳: 當應用程式請求到無效的圖片 URL（如拼湊錯誤、目標不存在或權限問題），Flickr 會回應佔位影像或錯誤頁面，常見為「photo not available」。其成因多半是尺寸實體不存在或 URL 模板不符。以 PhotosGetSizes 取得的 URL 可有效避免此情況。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: D-Q1, A-Q6

A-Q16: Size 物件包含哪些核心欄位？
- A簡: label、source、url、width、height，對應尺寸名、來源與實際大小。
- A詳: 使用 PhotosGetSizes 取得的 Size 物件至少含有：label（尺寸標籤，例如 Medium、Large 等）、source（影像來源連結）、url（點擊連結頁）、width/height（像素寬高）。這些欄位足以支持顯示決策（選擇最佳尺寸）、版面配置（計算占位大小）、與跳轉行為（點擊連結）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, C-Q3

A-Q17: 為什麼不能只憑 API 名稱猜用法？
- A簡: 名稱可能直觀但不保證語意與可靠性，需閱讀文件與驗證。
- A詳: 本案例中，PhotosGetInfo 看似可直接取用 LargeUrl，但其來源為模板推導，非伺服器確認實體。若不閱讀文件或驗證，易因規格差異導致壞連結。良好做法是：研讀官方文件、比對網站行為、以可驗證 API（如 PhotosGetSizes）作為資料真實性來源。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q11, D-Q9

A-Q18: 修正後的核心價值是什麼？
- A簡: 消除不確定性，取得穩定可用的圖片連結與尺寸資訊。
- A詳: 改用 PhotosGetSizes 的價值在於可靠與可預期。它以伺服器確認的可用尺寸取代本地模板推導，避免因規格變更或尺寸缺席造成錯誤，並讓前端僅需根據「已知可用」的清單做選擇與回退，提升用戶體驗、降低錯誤處理與重試成本。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q13, B-Q10

A-Q19: 為何要快取尺寸資訊？
- A簡: 降低重複呼叫開銷、提升效能並穩定顯示體驗。
- A詳: 尺寸清單通常在短期內不變，將 PhotosGetSizes 結果序列化（如 XML）快取，可減少外部呼叫、降低延遲與錯誤率。快取中保存 label、url、width、height，前端可直接讀取。需設計過期機制與失效更新，避免長期陳舊資料造成不一致。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, C-Q8

A-Q20: 此修正對專案成熟度有何意義？
- A簡: 從試驗走向實用，移除不確定性並簡化周邊防錯邏輯。
- A詳: 以正確 API 替代脆弱方案，讓 FlickrProxy 從「能跑」變成「好用且穩定」。壞連結與多餘檢查（逐一驗證 URL）得以移除，程式簡潔，維護成本更低，也更能承受 Flickr 未來格式變更，專案由此邁入實用階段。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q18, B-Q12

### Q&A 類別 B: 技術原理類

B-Q1: 上傳後取得圖片網址的典型流程為何？
- A簡: 上傳得 photoId，先取資訊，再取可用尺寸，最後選適合 URL。
- A詳: 流程通常為：1) 上傳照片成功取得 photoId；2) 呼叫 PhotosGetInfo 取得描述性資訊（非必需用於 URL）；3) 呼叫 PhotosGetSizes 取得伺服器確認的可用尺寸清單；4) 依需求選擇首選尺寸（如 Large）與回退順序（如 Large→Medium→Original）；5) 快取結果供前端使用。此流程兼顧正確性與效能。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, B-Q6, C-Q2

B-Q2: PhotosGetInfo 如何「湊」出各尺寸 URL？
- A簡: 依已知模板以 id、server、secret 與尺寸後綴組出連結。
- A詳: PhotosGetInfo 回傳多組識別資訊，客戶端（或套件）據此代入 Flickr 公布的 URL 模板產出尺寸連結，如加入 size 後綴（例：_m、_b 等）。此為字串規則推導，非即時查證，當 Flickr 調整命名格式或尺寸實體未產生時，便可能生成指向不存在資源的 URL。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, A-Q11

B-Q3: 原圖與其他尺寸的網址格式為何會不同？
- A簡: 原圖具不同命名規則與存放策略，與縮圖格式不完全一致。
- A詳: Flickr 對原圖（Original）常有獨立的儲存與命名策略，其 URL 格式與經取樣產生的尺寸（Medium、Large 等）並不完全相同。當系統以縮圖規則去推導原圖或以原圖替代某尺寸時，將導致連結不匹配，進而產生 404 或佔位圖。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, A-Q6

B-Q4: 為何當 Flickr 不產生 Large 時會造成錯誤？
- A簡: 模板仍生出 LargeUrl，但伺服端無該尺寸實體，結果即為壞連結。
- A詳: 當上傳檔案太小，Flickr 可能不建立 Large 版本。PhotosGetInfo 依模板仍可合成 LargeUrl，但伺服端並無相對應檔案，請求時便得到錯誤頁或佔位圖。這也是為何要以 PhotosGetSizes 查詢「實際可用」尺寸清單，再由清單挑選最接近需求的原因。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, A-Q10

B-Q5: PhotosGetSizes 的技術機制是什麼？
- A簡: 伺服器回傳一組尺寸集合，每項含標籤、URL 與寬高，保證可用。
- A詳: PhotosGetSizes 由伺服端根據照片實際已產生的版本回傳集合，常見欄位包含 label（尺寸名）、source/url（圖片/頁面連結）、width/height。因為清單是由服務端生成，不需在客戶端推導或猜測，天然具備一致性與正確性，適合驅動前端顯示與快取。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, A-Q16

B-Q6: 改用 PhotosGetSizes 的執行流程為何？
- A簡: 取 photoId → 呼叫 PhotosGetSizes → 依策略選尺寸 → 快取 → 顯示。
- A詳: 核心步驟：1) 取得 photoId；2) flickr.PhotosGetSizes(photoId) 取得 SizeCollection；3) 依優先順序（如 Large、無則 Medium、再 Original）挑選；4) 將選定與全部可用尺寸序列化（XML/JSON）快取；5) 前端直接以快取資料顯示，免逐一驗證 URL。此流程可移除昂貴的可用性檢查。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, C-Q2, C-Q3

B-Q7: PhotoInfo 與 Size 物件在角色上的差異？
- A簡: PhotoInfo 重描述與推導 URL；Size 則回報實際可用尺寸與連結。
- A詳: PhotoInfo 偏向元資料與描述（標題、擁有者、時間等）與「基於規則」的尺寸 URL。Size 表述「服務端真實存在」的尺寸與連結，適合顯示決策。兩者互補：PhotoInfo 供內容與上下文；Size 供穩定顯示與版面布局。顯示層應以 Size 為準。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, A-Q16

B-Q8: URL 可用性檢查的技術實作與成本？
- A簡: 以 HEAD/GET 驗證連結存在，但增加延遲與請求成本。
- A詳: 常見作法是對候選 URL 送出 HTTP HEAD（或小型 GET），若 200 則視為可用。此法能補足來源不可靠的缺陷，但代價是額外往返與延遲，且可能被視為濫用。當改用 PhotosGetSizes 後，應移除此步驟，讓可靠的資料源取代昂貴的事後驗證。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, C-Q4

B-Q9: 尺寸資訊快取的架構如何設計？
- A簡: 將 Size 集合序列化存放（如 XML），含 label/url/寬高與過期策略。
- A詳: 攝取 SizeCollection 後，將每個尺寸以元素節點寫入快取（元素名如 size，屬性含 label、source、url、width、height），並建立根節點與版本標識。設置過期與重建策略，確保當 Flickr 更新圖檔或策略變更時能重新取得，保持一致性與效能平衡。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q3, C-Q8

B-Q10: 回退策略如何降低不確定性？
- A簡: 預先定義尺寸優先序與替代順序，保證總有可用圖可顯示。
- A詳: 以 PhotosGetSizes 得到清單後，建立明確優先順序（如 Large→Medium→Original）。當首選不存在時自動回退到下一選擇，避免中斷顯示。此策略以「實際可用」為基礎，故回退決策可預測、易測試，並能在格式變更時維持穩定輸出。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, D-Q3

B-Q11: 如何驗證 API 回傳與網站實際使用一致？
- A簡: 對照 PhotosGetSizes 清單與網站行為，檢視尺寸是否相符。
- A詳: 以 PhotosGetSizes 做「真實來源」，在開發階段比對網站顯示的尺寸與 URL 是否為清單中的某一項。若發現差異，檢查是否因快取陳舊、網站動態裁切或 API 規格更新。此驗證流程能避免因猜測導致的錯誤理解與實作偏差。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, C-Q7

B-Q12: 移除多餘 URL 檢查對效能的影響？
- A簡: 大幅降低請求數與延遲，簡化錯誤處理，提高吞吐量。
- A詳: 當以 PhotosGetSizes 作為單一事實來源後，逐一 HEAD/GET 驗證的步驟可移除。這不僅減少外部請求與網路往返，也讓程式碼更單純；錯誤處理集中在「取得清單」這一步，提升可觀測性與效能，前端載入速度與穩定性明顯改善。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q18, C-Q1

B-Q13: 如何面對 API 可能的未來變更？
- A簡: 依賴服務端真實清單、設計抽象與快取更新機制以應對。
- A詳: 首重「依賴服務端聲明的真實狀態」，避免本地推導。以介面抽象封裝 API 呼叫，集中處理變更；用快取+版本標識/過期策略降低依賴強度；建立驗證與監控以捕捉偏差，並設自動回退策略。如此可在 API 變化時降低維護成本。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, B-Q11

B-Q14: 將尺寸選擇抽象為策略模式如何設計？
- A簡: 封裝多種優先序規則，支援替換與單元測試，提升可維護性。
- A詳: 定義 ISizeSelectionStrategy（輸入 Size 集合，輸出最佳 Size），可實作「偏大圖」、「限制寬度」、「行動優先」等策略。透過依賴注入切換策略，並以固定輸入集合撰寫單元測試，確保在 Flickr 尺寸供應變動時，行為仍可預期與可測。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q2, B-Q10

B-Q15: 以 photoId 作為主鍵的辨識原理？
- A簡: photoId 唯一識別一張照片，串接後續所有查詢與操作。
- A詳: 上傳成功後取得的 photoId 是後續 API 的關鍵輸入。所有資訊查詢（PhotosGetInfo、PhotosGetSizes）都以它為核心。正確管理 photoId（保存、索引、權限關聯）能確保查詢一致並降低錯誤來源，是資料流穩定的前提。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, C-Q1

B-Q16: 什麼是不確定性的傳播機制？
- A簡: 來源資料不可靠會迫使下游補救，造成複雜與效能損耗。
- A詳: 以規則推導 URL 屬不可靠來源，前端需增加可用性檢查與回退，導致狀態機複雜化、請求數暴增與延遲累積。改以服務端真實清單可阻斷不確定性向下游擴散，讓系統在邊界就校正資料，改善整體穩定性與可維護性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q18, B-Q12

B-Q17: 舊版 try/catch 驗證流程的技術代價？
- A簡: 以逐一驗證換取正確性，代價是請求冗餘與例外吞沒。
- A詳: 舊碼對 Medium/Large/Original 逐一呼叫 CheckFlickrUrlAvailability，並用 try/catch 吃例外，雖能暫避壞連結，但引入多次外部請求與隱性錯誤，且例外被吞沒降低可觀測性。此做法難以擴展，亦加重效能負擔與除錯成本。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q5, D-Q9

B-Q18: 新版 foreach 尺寸收集流程的重點？
- A簡: 以 PhotosGetSizes 回傳集合，逐項保存 label/url/寬高至快取。
- A詳: 新碼遍歷 flickr.PhotosGetSizes(photoId).SizeCollection，將每項尺寸以 XML 節點保存（label、source、url、width、height）。此流程將真實狀態落地，前端只需讀取快取決策顯示。這種單一事實來源與資料驅動方式，簡化了控制流程與錯誤處理。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q3, B-Q6

B-Q19: 記錄與追蹤在此案例的作用？
- A簡: 用於比對 API/網站差異、觀測錯誤率與驗證修正成效。
- A詳: 在切換方案前後，紀錄壞連結比例、請求耗時與例外種類，有助於驗證 PhotosGetSizes 方案的成效。對差異案例加註 photoId 與尺寸清單，便於回溯與報告問題來源（如規則改動、快取過期）。良好的觀測能縮短修復與優化迭代。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, D-Q2

B-Q20: 單元測試如何覆蓋 API 差異帶來的風險？
- A簡: 以模擬回傳與固定輸入測策略輸出，避免回gress 與壞連結。
- A詳: 為尺寸選擇策略建立測試：給定一組模擬 Size 清單（含缺 Large、僅 Medium/Original 等），驗證最終選擇與回退符合預期。對快取序列化/反序列化做可靠性測試。以 Stub 取代實際呼叫，確保在 Flickr 改動時能快速發現行為偏差。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q9, B-Q14

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何將程式從 PhotoInfo 改為 PhotosGetSizes？
- A簡: 以 PhotosGetSizes 取得 SizeCollection，改存 label/url/寬高並供前端使用。
- A詳: 
  - 具體步驟: 
    1) 以 photoId 呼叫 flickr.PhotosGetSizes(photoId);
    2) 遍歷 SizeCollection，收集 label、source、url、width、height；
    3) 序列化至快取（XML/JSON）； 
    4) 前端改讀快取。
  - 程式碼:
    ```csharp
    var sizes = flickr.PhotosGetSizes(photoId).SizeCollection;
    foreach (var s in sizes) { SaveSize(s.Label, s.Source, s.Url, s.Width, s.Height); }
    ```
  - 注意: 確保有根節點；處理 null 欄位；記錄版本與過期。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q3

C-Q2: 如何選出最佳顯示尺寸並建立回退？
- A簡: 定義優先序如 Large→Medium→Original，按順序挑第一個存在者。
- A詳: 
  - 步驟: 
    1) 取得 Size 集合；
    2) 定義優先序陣列；
    3) 依序查找第一個存在的尺寸；
    4) 無則回傳集合中最大寬度者。
  - 程式碼:
    ```csharp
    string[] pref = { "Large", "Medium", "Original" };
    var pick = sizes.FirstOrDefault(s => pref.Contains(s.Label)) 
            ?? sizes.OrderByDescending(s => s.Width).First();
    return pick.Source;
    ```
  - 注意: 標籤大小寫與在地化；保底策略可用最大寬度。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q10, B-Q14

C-Q3: 如何將尺寸資訊寫入 XML 快取？
- A簡: 建立根節點，逐項新增 size 元素並設定 label/url/寬高屬性。
- A詳: 
  - 步驟:
    1) 建立 XmlDocument 與根 <sizes>；
    2) 遍歷 SizeCollection；
    3) 建立 <size> 元素與屬性；
    4) 持久化至檔案/記憶體快取。
  - 程式碼:
    ```csharp
    var doc = new XmlDocument();
    var root = doc.CreateElement("sizes"); doc.AppendChild(root);
    foreach (var s in sizes) {
      var e = doc.CreateElement("size");
      e.SetAttribute("label", s.Label);
      e.SetAttribute("source", s.Source);
      e.SetAttribute("url", s.Url);
      e.SetAttribute("width", s.Width.ToString());
      e.SetAttribute("height", s.Height.ToString());
      root.AppendChild(e);
    }
    doc.Save(path);
    ```
  - 注意: 確保 DocumentElement 非空；處理字串編碼。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q9, D-Q4

C-Q4: 如何實作 CheckFlickrUrlAvailability（如需保留）？
- A簡: 以 HTTP HEAD 檢查 200，超時與重試設置謹慎，避免延遲放大。
- A詳: 
  - 步驟:
    1) 建立 HttpClient；
    2) 對 URL 發 HEAD；
    3) 檢查 2xx 視為可用；
    4) 記錄非 2xx 與例外。
  - 程式碼:
    ```csharp
    async Task<bool> IsAliveAsync(string url){
      using var req=new HttpRequestMessage(HttpMethod.Head,url);
      using var client=new HttpClient{Timeout=TimeSpan.FromSeconds(3)};
      try{ var resp=await client.SendAsync(req); return resp.IsSuccessStatusCode; }
      catch{ return false; }
    }
    ```
  - 注意: 頭部可能被阻擋，必要時退回小 GET；勿大量並發。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q8, D-Q5

C-Q5: 如何封裝 Flickr 尺寸取得為服務類別？
- A簡: 建立 IFlickrSizeService，實作以 PhotosGetSizes 取回並套用選擇策略。
- A詳: 
  - 介面與實作:
    ```csharp
    public interface IFlickrSizeService{
      Task<IReadOnlyList<Size>> GetSizesAsync(string photoId);
      Size PickBest(IReadOnlyList<Size> sizes);
    }
    ```
    以 DI 注入 Flickr 客戶端；GetSizes 呼叫 PhotosGetSizes；PickBest 依策略挑選。
  - 注意: 加入快取層、重試與記錄；單元測試以 Stub。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q14, C-Q2

C-Q6: 如何在 ASP.NET 綁定圖片 URL 來源為快取？
- A簡: 後端讀快取選尺寸 URL，前端以 <img src="..."> 綁定輸出。
- A詳: 
  - 步驟:
    1) 後端載入 XML 快取；
    2) 套用選擇策略得最佳 source；
    3) 傳給 ViewModel；
    4) 頁面輸出。
  - 程式碼（Razor）:
    ```csharp
    var sizes = LoadSizesFromCache(photoId);
    var best = SelectBest(sizes);
    <img src="@best.Source" width="@best.Width" height="@best.Height" />
    ```
  - 注意: 提供寬高避免 CLS；處理失敗時顯示替代圖。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q2, C-Q3

C-Q7: 如何撰寫 API/網站差異的驗證工具？
- A簡: 列印 PhotosGetSizes 清單，人工對照網站顯示尺寸與連結。
- A詳: 
  - 步驟:
    1) 給定 photoId；
    2) 取 PhotosGetSizes 清單；
    3) 依 label/width 排序輸出；
    4) 在瀏覽器檢視該照片頁，對照顯示尺寸。
  - 程式碼:
    ```csharp
    var sizes = flickr.PhotosGetSizes(photoId).SizeCollection;
    foreach(var s in sizes) Console.WriteLine($"{s.Label} {s.Width} {s.Source}");
    ```
  - 注意: 啟用記錄，收集差異案例以調整策略與快取。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q11, B-Q19

C-Q8: 如何為尺寸快取設計過期與更新？
- A簡: 設 TTL 與背景重建，讀取時若過期則回傳舊值並觸發刷新。
- A詳: 
  - 步驟:
    1) 快取附加 timestamp；
    2) 設定 TTL（如 24h）；
    3) 讀取時若過期，立即返回舊資料避免阻塞，同步觸發刷新；
    4) 刷新成功後覆蓋。
  - 程式碼（概念）:
    ```csharp
    if(cache.IsExpired(photoId)){ TriggerRefresh(photoId); }
    return cache.Get(photoId); // stale-while-revalidate
    ```
  - 注意: 避免驟發抖動，加入抖動時間與併發抑制。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q9, D-Q8

C-Q9: 如何寫單元測試確保不再出現壞連結？
- A簡: 以模擬 Size 清單覆蓋缺 Large 等情境，驗證選擇與回退。
- A詳: 
  - 步驟:
    1) 構造含 Medium/Original、無 Large 的清單；
    2) 呼叫 PickBest 應回 Medium 或 Original；
    3) 構造只有 Large 的清單應回 Large；
    4) 驗證序列化/反序列化不丟欄位。
  - 程式碼（xUnit 概念）:
    ```csharp
    var sizes = new[]{ new Size{Label="Medium",Width=500,Source="..."} };
    Assert.Equal("Medium", service.PickBest(sizes).Label);
    ```
  - 注意: 隔離外部 API；固定資料以避免測試不穩定。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q20, C-Q2

C-Q10: 如何漸進式上線改用 PhotosGetSizes？
- A簡: 影子發布與雙寫快取，觀測錯誤率與延遲，逐步切流量。
- A詳: 
  - 步驟:
    1) 新增尺寸服務並雙寫快取；
    2) 先後台切換少量流量讀新快取；
    3) 比對壞連結率/延遲/錯誤；
    4) 無異常逐步擴大；
    5) 清理舊驗證邏輯。
  - 注意: 預置回退開關；保留觀測儀表板與告警。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q12, B-Q19

### Q&A 類別 D: 問題解決類（10題）

D-Q1: 遇到「photo not available」怎麼辦？
- A簡: 多因尺寸 URL 無效。改用 PhotosGetSizes 並依優先序回退。
- A詳: 
  - 症狀: 大圖顯示佔位錯誤圖或 404。
  - 可能原因: Large 實體不存在；以模板湊 URL 錯誤；快取過舊。
  - 解決步驟: 用 PhotosGetSizes 取清單；依 Large→Medium→Original 選擇；刷新快取。
  - 預防: 以服務端清單為準；設快取過期；寫單元測試覆蓋缺尺寸情境。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q15, C-Q2

D-Q2: 為何 LargeUrl 偶爾 404？如何排查？
- A簡: 模板生成的連結不存在。改查 Sizes 清單並更新快取。
- A詳: 
  - 症狀: 部分照片 LargeUrl 404，其餘正常。
  - 原因: Flickr 未產生 Large；URL 模板與現行規格不符。
  - 步驟: 對該 photoId 呼叫 PhotosGetSizes；確認是否無 Large；選用存在尺寸；更新快取。
  - 預防: 前端不直接用 LargeUrl；統一走尺寸服務與回退策略。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q11

D-Q3: PhotosGetSizes 沒有 Large 標籤怎麼處理？
- A簡: 依回退策略改用 Medium 或 Original，並紀錄以便分析。
- A詳: 
  - 症狀: Size 清單中缺 Large。
  - 原因: 上傳圖過小；平台策略不產生 Large。
  - 步驟: 實作優先序 Large→Medium→Original；選到替代尺寸後更新前端。
  - 預防: 將優先序策略常態化；建立監控以評估缺 Large 的比例。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q2, B-Q10

D-Q4: AppendChild 失敗：DocumentElement 為 null？
- A簡: 未建立根節點。先 CreateElement 根並 Append，再附加子節點。
- A詳: 
  - 症狀: NullReference 或無法附加 <size>。
  - 原因: 未先建立/附加根節點。
  - 步驟: 先 doc.AppendChild(doc.CreateElement("sizes"))；再 root.AppendChild(size)。
  - 預防: 建立快取初始化流程；加入空值檢查與單元測試。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q3, B-Q9

D-Q5: CheckFlickrUrlAvailability 造成延遲過高？
- A簡: 多餘驗證導致多次網路往返。改以 PhotosGetSizes 移除此步驟。
- A詳: 
  - 症狀: 載入緩慢、請求數激增。
  - 原因: 逐一 HEAD/GET 檢查 Medium/Large/Original。
  - 步驟: 切換到以 Sizes 清單為準；僅在必要情況保留單一驗證。
  - 預防: 監控請求數與延遲；預設關閉逐一驗證。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, C-Q4

D-Q6: PhotoInfo 的 Medium/Large/Original 為空或無效？
- A簡: 不依賴 PhotoInfo URL。改走 PhotosGetSizes 的 Source。
- A詳: 
  - 症狀: PhotoInfo 屬性空字串或點擊顯示錯誤。
  - 原因: 模板推導失準；尺寸不存在。
  - 步驟: 使用 PhotosGetSizes；以清單選擇與回退；更新快取。
  - 預防: 將 PhotoInfo 改作描述用途；顯示層一律走 Sizes。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q11, C-Q1

D-Q7: 遍歷 Size 時 s.Url 或 s.Source 為空怎麼辦？
- A簡: 濾除空欄位，並以其他可用欄位或尺寸回退維持可用性。
- A詳: 
  - 症狀: NullReference 例外或產生空連結。
  - 原因: 個別尺寸欄位不全。
  - 步驟: 迴圈內加空值檢查；選擇有 Source 的項；若缺則回退到下一尺寸。
  - 預防: 在序列化前做驗證；新增單元測試覆蓋缺欄位。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q3, C-Q2

D-Q8: 快取過舊導致錯誤連結？
- A簡: 啟用 TTL 與背景刷新，採用 stale-while-revalidate 策略。
- A詳: 
  - 症狀: 網站端已調整，舊快取仍指向錯誤 URL。
  - 原因: 無過期機制或刷新失敗。
  - 步驟: 為快取加入 timestamp；判過期觸發重建；新舊並行切換。
  - 預防: 設 TTL 與抖動；監控快取命中率與重建錯誤。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q8, B-Q9

D-Q9: try/catch 吃掉例外導致難以定位？
- A簡: 避免空 catch。記錄 photoId、尺寸、URL 與錯誤內容便於追查。
- A詳: 
  - 症狀: 錯誤消失無紀錄，行為不穩定。
  - 原因: 空的 catch 區塊吞掉例外。
  - 步驟: 移除空 catch；最少記錄 error、photoId、URL 與堆疊；必要時重拋。
  - 預防: 設定記錄等級與告警；以測試覆蓋例外情境。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q17, B-Q19

D-Q10: 網路波動導致 PhotosGetSizes 失敗怎麼辦？
- A簡: 加入重試與快取回退，避免阻塞顯示，並記錄以便重取。
- A詳: 
  - 症狀: 呼叫超時或偶發失敗，頁面無圖。
  - 原因: 短暫網路中斷或遠端不穩。
  - 步驟: 實作有限次重試（退避）；若快取有舊資料，先回舊值；重試成功後覆蓋。
  - 預防: 設超時與重試策略；監控失敗率；預留降級顯示占位圖。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q8, B-Q12

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 FlickrProxy？
    - A-Q2: 什麼是 Flickr API？
    - A-Q3: 什麼是 PhotosGetInfo API？
    - A-Q4: 什麼是 PhotoInfo 物件？
    - A-Q5: MediumUrl、LargeUrl、OriginalUrl 分別是什麼？
    - A-Q6: 為什麼會出現大圖網址（LargeUrl）錯誤？
    - A-Q7: 為何小圖可能沒有 Large 版本？
    - A-Q8: 什麼是「以網址格式湊出 URL」？
    - A-Q10: 什麼是 PhotosGetSizes API？
    - A-Q11: PhotosGetInfo 與 PhotosGetSizes 有何差異？
    - A-Q12: 什麼是「可用尺寸」？
    - A-Q14: 檢查 URL 可用性的用途為何？
    - B-Q1: 上傳後取得圖片網址的典型流程為何？
    - B-Q5: PhotosGetSizes 的技術機制是什麼？
    - D-Q1: 遇到「photo not available」怎麼辦？

- 中級者：建議學習哪 20 題
    - B-Q2: PhotosGetInfo 如何「湊」出各尺寸 URL？
    - B-Q3: 原圖與其他尺寸的網址格式為何會不同？
    - B-Q4: 為何當 Flickr 不產生 Large 時會造成錯誤？
    - B-Q6: 改用 PhotosGetSizes 的執行流程為何？
    - B-Q8: URL 可用性檢查的技術實作與成本？
    - B-Q9: 尺寸資訊快取的架構如何設計？
    - B-Q10: 回退策略如何降低不確定性？
    - B-Q11: 如何驗證 API 回傳與網站實際使用一致？
    - B-Q12: 移除多餘 URL 檢查對效能的影響？
    - B-Q13: 如何面對 API 可能的未來變更？
    - B-Q14: 將尺寸選擇抽象為策略模式如何設計？
    - C-Q1: 如何將程式從 PhotoInfo 改為 PhotosGetSizes？
    - C-Q2: 如何選出最佳顯示尺寸並建立回退？
    - C-Q3: 如何將尺寸資訊寫入 XML 快取？
    - C-Q4: 如何實作 CheckFlickrUrlAvailability（如需保留）？
    - C-Q5: 如何封裝 Flickr 尺寸取得為服務類別？
    - C-Q6: 如何在 ASP.NET 綁定圖片 URL 來源為快取？
    - D-Q2: 為何 LargeUrl 偶爾 404？如何排查？
    - D-Q3: PhotosGetSizes 沒有 Large 標籤怎麼處理？
    - D-Q5: CheckFlickrUrlAvailability 造成延遲過高？

- 高級者：建議關注哪 15 題
    - B-Q15: 以 photoId 作為主鍵的辨識原理？
    - B-Q16: 什麼是不確定性的傳播機制？
    - B-Q17: 舊版 try/catch 驗證流程的技術代價？
    - B-Q18: 新版 foreach 尺寸收集流程的重點？
    - B-Q19: 記錄與追蹤在此案例的作用？
    - B-Q20: 單元測試如何覆蓋 API 差異帶來的風險？
    - C-Q7: 如何撰寫 API/網站差異的驗證工具？
    - C-Q8: 如何為尺寸快取設計過期與更新？
    - C-Q9: 如何寫單元測試確保不再出現壞連結？
    - C-Q10: 如何漸進式上線改用 PhotosGetSizes？
    - D-Q4: AppendChild 失敗：DocumentElement 為 null？
    - D-Q6: PhotoInfo 的 Medium/Large/Original 為空或無效？
    - D-Q7: 遍歷 Size 時 s.Url 或 s.Source 為空怎麼辦？
    - D-Q8: 快取過舊導致錯誤連結？
    - D-Q10: 網路波動導致 PhotosGetSizes 失敗怎麼辦？