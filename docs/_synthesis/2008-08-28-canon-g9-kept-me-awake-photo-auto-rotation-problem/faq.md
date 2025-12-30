---
layout: synthesis
title: "Canon G9 害我沒睡好... 相片自動轉正的問題"
synthesis_type: faq
source_post: /2008/08/28/canon-g9-kept-me-awake-photo-auto-rotation-problem/
redirect_from:
  - /2008/08/28/canon-g9-kept-me-awake-photo-auto-rotation-problem/faq/
---

# Canon G9 害我沒睡好... 相片自動轉正的問題

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

Q1: 什麼是 EXIF？
- A簡: EXIF 是數位相片的拍攝資訊標準，包含時間、相機參數、方向等，可供軟體自動處理。
- A詳: EXIF（Exchangeable Image File Format）是數位相片內嵌的標準化拍攝資訊格式。它記錄快門、光圈、ISO、鏡頭、拍攝時間、相機型號與相片方向（Orientation）等。應用程式可讀取 EXIF 以自動旋轉、排序或歸檔。理解 EXIF 是處理相片自動轉正、批次縮圖與維持檔案中繼資料完整性的基礎，對相簿、相片管理與影像管線設計至關重要。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q7, B-Q2

Q2: 什麼是 EXIF Orientation（標籤 274）？
- A簡: Orientation 標籤記錄相片應呈現的方向，常見值 1、3、6、8 對應 0/180/90/270 度。
- A詳: EXIF Orientation（ID 274）描述影像的預期呈現方向。常見值：1=正常（0 度）、3=旋轉 180 度、6=順時針 90 度、8=逆時針 90 度（270 度）。少見值 2/4/5/7 涉及鏡像翻轉。影像檢視器依此標籤決定是否套用旋轉或翻轉。若標籤缺失或誤填，多數檢視器將以 1（不旋轉）呈現，導致側躺或倒置的視覺問題。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, B-Q4, C-Q1

Q3: 為什麼有些相片會自動轉正、有些不會？
- A簡: 因相機寫入的 Orientation 不一致、解碼器支援差異，或 180 度未偵測導致。
- A詳: 自動轉正依賴兩件事：相機是否正確寫入 EXIF Orientation、檢視/處理軟體是否依標籤套用旋轉。文中觀察到 Canon G9/IXUS55 對 180 度拍攝不設定對應值，導致標籤常為 1；另 CR2 透過 Canon RAW Codec 會在解碼階段自動旋轉，但 JPG 常需自行處理。若軟體忽略 Orientation 或讀取路徑不對，也會顯示方向錯誤。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, A-Q6, B-Q2

Q4: 相機上的自動轉正與電腦軟體有何差異？
- A簡: 相機用感測器即時旋轉顯示；電腦軟體多依 EXIF 或解碼器行為決定。
- A詳: 相機拍攝時利用重力感測（早期以水銀開關，後期加速度/方向感測器）判斷持機方向，即時在相機螢幕轉正，但寫入 EXIF 的策略與完整度依廠商而異。電腦端軟體多從 EXIF 讀 Orientation 後再套用旋轉，或倚賴特定解碼器（如 Canon RAW Codec）自動處理。兩端行為不必然一致，故會出現相機看起來正確、電腦卻側躺的情況。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q6, B-Q5

Q5: Canon G9/IXUS55 對 180 度拍攝的支援如何？
- A簡: 僅可靠偵測 90 度左右轉，180 度多未設定對應 Orientation 值。
- A詳: 文章以四種角度實測，發現 Canon G9/IXUS55 能穩定標註 6（順時針 90）與 8（逆時針 90），但 180 度常未寫入 3，甚至遺留為 1（視為不旋轉）。相機顯示時亦無法識別 180 度而自動轉正。這意味著對倒立自拍、孩童亂拍等情境，後製軟體須提供手動或自動化補償策略。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q11, D-Q2

Q6: CR2 與 JPG 在自動轉正行為有何差異？
- A簡: CR2 經 Canon RAW Codec 會自動旋轉；JPG 通常需自行依 Orientation 處理。
- A詳: Canon RAW（CR2）檔透過 Canon RAW Codec 進行解碼時，解碼器會據 EXIF 自動套用旋轉，使應用程式取得已轉正的影格。相對地，JPG 的解碼多回傳未旋轉的像素資料，需由應用自行讀取 Orientation（274）並施作 RotateTransform。兩者在 WPF 的 metadata 查詢路徑也不同，需分流處理以取得一致結果。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q8, C-Q4

Q7: Orientation 的常見值與對應旋轉是什麼？
- A簡: 1=0 度，3=180 度，6=順時針 90，8=逆時針 90；2/4/5/7 為鏡像變種。
- A詳: 常見實務對應：1=正常不轉；6=Rotate 90（CW）；8=Rotate 270（CCW）；3=Rotate 180。少見：2=水平鏡像；4=垂直鏡像；5=Rotate 90+CW 鏡像；7=Rotate 270+鏡像。多數相機僅使用 1/3/6/8。處理管線應先將這些值映射為旋轉角度，必要時處理鏡像，最後輸出並將 Orientation 正規化為 1。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q4, C-Q2, D-Q4

Q8: 為什麼需要在 WPF 中自行處理旋轉？
- A簡: 因 JPG 解碼不保證自動旋轉，需依 EXIF 值自行套用 RotateTransform。
- A詳: 在 WPF/WIC 管線中，JPG 多回傳原始像素，並不會自動依 EXIF Orientation 進行旋轉。若忽略該步驟，縮圖與輸出將方向錯誤。實務作法是讀取 Orientation，將 6/8/3 轉為 90/270/180 度，與 ScaleTransform 組合後再輸出。此舉也能讓 CR2/JPG 兩類來源在結果上保持一致。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q3, D-Q1

Q9: 什麼是 WPF 的 BitmapMetadata 與 GetQuery？
- A簡: BitmapMetadata 封裝影像中繼資料；GetQuery 以查詢路徑讀取特定標籤值。
- A詳: WPF 基於 WIC 提供 BitmapMetadata 物件以讀寫影像中繼資料。GetQuery 接受一段「查詢路徑」字串（如 /app1/{ushort=0}/{ushort=274}），可直接擷取特定 EXIF/IFD 節點值。不同格式的根路徑不同，導致 CR2 與 JPG 要用不同查法。使用時務必作 null/例外防護，避免缺失標籤導致失敗。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, C-Q1, D-Q3

Q10: 為何各格式的 metadata 查詢路徑不同？
- A簡: 因資料封裝位置不同，JPG 在 APP1 Exif 區，RAW/IFD 在不同根節點。
- A詳: JPG 的 EXIF 儲存在 APP1 區段，因此路徑以 /app1 開頭，常見為 /app1/{ushort=0}/{ushort=274} 指到 Orientation。RAW（如 CR2）採 IFD 結構，WIC 路徑多為 /ifd/{ushort=274}。若用錯根路徑將取不到值或拋例外。理解容器差異有助於跨格式讀寫中繼資料。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, C-Q4, D-Q3

Q11: 只靠 Orientation 能完全判斷相片方向嗎？
- A簡: 不一定。若相機未寫入或誤寫，特別是 180 度，需人工或其他方法。
- A詳: Orientation 是最經濟的方向來源，但仰賴相機端是否可靠寫入。Canon G9/IXUS55 就常未寫入 180 度（值 3），使倒置照片仍標為 1，導致軟體無從知悉。此時可提供使用者手動旋轉、記錄一次性校正，或引入影像內容分析（成本較高）以輔助判斷。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q5, D-Q2, C-Q6

Q12: 自動轉正的核心價值是什麼？
- A簡: 提升瀏覽體驗與縮圖一致性，減少手動旋轉與誤判的維護成本。
- A詳: 自動轉正可在相片瀏覽、管理與分享流程中確保方向一致。對批次縮圖、相簿生成、機器學習資料清理特別重要。它降低人工旋轉與返工成本，避免 UI 顯示歪斜造成使用者困惑，也利於後續影像分析。實作上需兼顧準確性、效能與原始 EXIF 的保留。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, B-Q6, C-Q3

Q13: 為什麼 Canon RAW Codec 會自動旋轉？
- A簡: 解碼器在還原像素時，根據 EXIF Orientation 主動套用旋轉。
- A詳: 某些供應商的 RAW 解碼器（如 Canon RAW Codec）會在解碼階段解析 EXIF Orientation，並直接輸出已轉正的像素。這讓上層應用不必再額外旋轉 CR2 影像。但對 JPG 或其他解碼器，則未必如此。為了行為一致，應用通常仍會以自身邏輯處理旋轉。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q5, D-Q8

Q14: 在相機上看到的自動轉正可信嗎？
- A簡: 部分可信。相機顯示正不代表已正確寫入 EXIF，特別是 180 度。
- A詳: 相機顯示與檔案中繼資料是兩件事。文中實測顯示，Canon 相機對 180 度情境即使顯示介面無法轉正，也未寫入對應 EXIF 值。即使相機上看正常（對 90 度），電腦端仍須檢查標籤與解碼器行為，避免被不同軟體呈現不一所誤導。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, A-Q3, D-Q1

Q15: 建立縮圖流程時，應優先考量哪些方向資訊？
- A簡: 讀 Orientation、統一旋轉策略、處理 CR2/JPG 差異並最終正規化標籤。
- A詳: 流程建議：先讀 EXIF Orientation（依格式選正確路徑），映射為旋轉角度；以 TransformGroup 將旋轉與縮放合併；輸出後將 Orientation 正規化為 1，同時保留其他 EXIF。對 CR2 與 JPG 建立一致策略，避免由解碼器自動旋轉造成行為差異。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q3, C-Q5

### Q&A 類別 B: 技術原理類

Q1: 相機如何偵測拍攝方向？
- A簡: 透過方向/加速度感測器（早期水銀開關）判斷相機姿態，決定是否寫入 EXIF。
- A詳: 相機內建的重力/方向感測器在快門時記錄機身姿態。早期設備可能使用水銀開關，現多為三軸加速度或陀螺傳感器。相機韌體依讀值決定是否將方向資訊寫入 EXIF Orientation。部分廠商僅對左右 90 度設值，對 180 度不處理，造成後端軟體無法自動轉正倒置相片。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, B-Q2, D-Q2

Q2: EXIF Orientation 如何被檢視器利用以自動轉正？
- A簡: 檢視器解析標籤值，於顯示階段套用對應旋轉/翻轉轉換後再呈現。
- A詳: 影像檢視器或處理管線在解碼影像後，讀取 Orientation 值並對像素套用 Rotate/Flip。值 6/8/3 對應 90/270/180 度，2/4/5/7 包含鏡像。若檢視器忽略該標籤，則按原始像素顯示，導致方向錯誤。某些解碼器（如 RAW Codec）在輸出像素前即完成旋轉，讓上層看似「自動轉正」。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q3, B-Q5

Q3: WPF 如何載入影像與其 EXIF？
- A簡: 透過 BitmapDecoder 取得 BitmapFrame 與 Metadata，再以 GetQuery 讀標籤。
- A詳: WPF 基於 WIC：以 BitmapDecoder 解碼檔案，取得第一個 BitmapFrame（或多幀），由其 Metadata 屬性獲得 BitmapMetadata。隨後用 GetQuery 與對應路徑讀取 EXIF（如 Orientation）。不同格式使用不同根路徑，必須分別處理，並為缺失標籤提供預設值與例外防護。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q8, C-Q1

Q4: 由 Orientation 值推導旋轉角度的流程是什麼？
- A簡: 將 6→90、8→270、3→180、其他→0，並選擇性處理鏡像值。
- A詳: 流程：讀 EXIF 值（UInt16）。映射：6=Rotate90（CW）、8=Rotate270（CCW）、3=Rotate180、1/0/缺失=Rotate0。若遇 2/4/5/7，需加上 ScaleTransform(-1,1) 或 (1,-1) 實現鏡像，再按對應角度旋轉。最後把旋轉與縮放組入 TransformGroup，輸出時將 Orientation 正規化為 1。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q7, C-Q2, C-Q5

Q5: Canon RAW Codec 在解碼時如何自動旋轉？
- A簡: 解碼器解析 EXIF，於像素輸出階段套用 RotateTransform，回傳已轉正影格。
- A詳: Canon RAW Codec 將 EXIF 作為解碼配置的一部分，於內部像素轉換（如 Demosaic、色彩校正）完成後，根據 Orientation 套用旋轉，最後輸出已轉正的 BitmapFrame。上層應用不需再旋轉，但為跨格式一致，仍建議建立獨立的旋轉邏輯。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, A-Q13, D-Q8

Q6: WPF 影像縮圖與旋轉的執行流程為何？
- A簡: 解碼→讀 Orientation→建 TransformGroup（縮放+旋轉）→TransformedBitmap→編碼。
- A詳: 步驟：1) 使用 BitmapDecoder 讀取來源影像與 Metadata；2) 解析 Orientation 推得角度；3) 建立 TransformGroup，先加入 ScaleTransform 再加入 RotateTransform；4) 以 TransformedBitmap 包裝來源 Frame；5) 建立 JpegBitmapEncoder，加入轉換後的 Frame，設定 QualityLevel；6) 輸出至檔案並釋放串流。此流程兼顧效能與一致性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q3, C-Q9, D-Q5

Q7: TransformGroup 架構如何設計以同時縮放與旋轉？
- A簡: 以 TransformGroup 順序加入 ScaleTransform 與 RotateTransform，統一應用。
- A詳: TransformGroup 允許堆疊多個 2D 轉換。常見做法先 Scale 後 Rotate，縮圖時採等比例縮放（如 0.1, 0.1），再按 Orientation 加入 90/180/270 度 RotateTransform。統一由 TransformedBitmap 套用整組變換，避免多次取樣造成畫質損失。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q3, D-Q5

Q8: 為什麼 .CR2 用「/ifd/{ushort=274}」，.JPG 用「/app1/{ushort=0}/{ushort=274}」？
- A簡: 因 WIC 對不同容器的根節點不同：RAW 在 IFD，JPEG 在 APP1 Exif 段。
- A詳: WIC 將 TIFF/RAW（IFD 結構）與 JPEG（APP1 Exif）視為不同樹根，導致查詢路徑不同。CR2 屬 RAW，Orientation 直掛在 /ifd；JPG 的 EXIF 在 APP1，需 /app1/{ushort=0}/ 前綴。選錯路徑會回 null 或擲出例外，故需依副檔名或解碼器選擇正確路徑。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, C-Q4, D-Q3

Q9: TransformedBitmap 的工作機制是什麼？
- A簡: 以延遲評估方式在解碼管線後套用 2D 轉換，輸出新視圖而非修改來源。
- A詳: TransformedBitmap 包裝來源 BitmapSource 與 Transform，呈現轉換後的「視圖」。其運作為按需取樣，將旋轉與縮放合併計算，避免多重取樣。這讓我們在不破壞原始影像的情況下產生已轉正縮圖，並交由編碼器輸出新檔。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q3, D-Q5

Q10: JpegBitmapEncoder 如何建立 Frame 與設定品質？
- A簡: 建立 Encoder→加入 BitmapFrame（可帶 Metadata）→設 QualityLevel→Save。
- A詳: WPF 以 JpegBitmapEncoder 負責 JPEG 編碼。流程是建立 encoder，呼叫 Frames.Add(BitmapFrame.Create(...))，可傳入 TransformedBitmap 與對應的 metadata，然後設定 QualityLevel（1–100），最後 Save 到串流。注意要關閉串流，並考慮複製/保留原始 EXIF。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q3, C-Q9, D-Q9

Q11: 當 Orientation 缺失或為 0x01 時軟體應如何處理？
- A簡: 預設不旋轉，並提供手動旋轉或記錄校正以彌補 180 度等案例。
- A詳: 若讀不到標籤或值為 1，預設 Rotate0 最安全。對常見失敗如 180 度倒置，可提供手動旋轉 UI、快捷鍵或批次規則，並將校正結果寫回輸出檔（且把 Orientation 設為 1），或以外部資料庫記錄使用者選擇，避免再次處理時重複出錯。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q11, C-Q6, D-Q2

Q12: 如何在不重新壓縮的情況下實現旋轉？
- A簡: 兩途徑：改寫 Orientation（不轉像素）或使用 JPEG 無損旋轉工具。
- A詳: 無損策略一是只改 EXIF Orientation（快速、零失真），前提是所有目標檢視器尊重該標籤；策略二使用 JPEG 無損轉換（基於 DCT 區塊）工具。WPF JpegBitmapEncoder 走重新壓縮路徑，非無損。若需無損，考慮專用程式庫或外部工具鏈，並在輸出後將 Orientation 設為 1。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: C-Q5, D-Q5, D-Q7

Q13: 如何保留或修改 EXIF（含時間、相機資訊與方向）？
- A簡: 由來源 Metadata 複製到新 Frame，必要時 SetQuery 寫入調整後的標籤。
- A詳: 讀取來源 BitmapMetadata，建立相容的目標 Metadata（如 new BitmapMetadata("jpg")），逐一 SetQuery 所需標籤，特別是維持拍攝時間、相機資訊、GPS。旋轉像素後應將 Orientation 設為 1。最後在 BitmapFrame.Create(...) 傳入 Metadata。注意不同格式的路徑差異與寫入權限。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: C-Q5, D-Q6, B-Q8

Q14: 如何驗證 90/180/270 三種情境的處理正確？
- A簡: 以四方向拍攝樣本，檢視 EXIF 值與實際輸出成品是否一致。
- A詳: 建立測試集：同一場景拍 0/90/180/270 四角度。使用工具讀 Orientation（預期 1/6/3/8），再經處理管線輸出縮圖。比對：螢幕呈現方向是否正確、EXIF 是否正規化為 1、解碼器是否對 CR2 做了額外旋轉。記錄邊界案例以調整邏輯。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q7, D-Q4, D-Q8

Q15: 影像處理順序（先旋轉或先縮放）對品質與效能有何影響？
- A簡: 合併為單一 Transform 最佳；避免重複取樣與多次壓縮造成畫質損失。
- A詳: 將旋轉與縮放合併到同一 TransformGroup 可一次取樣，避免先縮再旋或先旋再縮導致的兩次插值。對 JPEG，應減少重複編碼次數，必要時一次完成全部調整。若需高品質縮放，可考慮更佳的重採樣濾波器或離線工具。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q6, C-Q3, D-Q5

### Q&A 類別 C: 實作應用類（10題）

Q1: 如何在 WPF 中安全讀取 Orientation 值？
- A簡: 依格式選對查詢路徑，GetQuery 後轉 UInt16，並做 null/例外防護。
- A詳: 步驟：1) 以 BitmapDecoder 載入影像，取第一個 Frame.Metadata 為 BitmapMetadata；2) 依格式決定路徑：JPG 用 "/app1/{ushort=0}/{ushort=274}"，CR2 用 "/ifd/{ushort=274}"；3) 嘗試 GetQuery，若回 null 或擲例外，預設值為 1。範例:
  - 具體實作步驟: 解碼→TryGet→映射。
  - 關鍵程式碼片段:
    ```csharp
    ushort GetOrientation(BitmapMetadata m, bool isJpeg)
    {
        object v=null;
        try { v=m.GetQuery(isJpeg?"/app1/{ushort=0}/{ushort=274}":"/ifd/{ushort=274}"); }
        catch { }
        return v is ushort u?u:(ushort)1;
    }
    ```
  - 注意事項與最佳實踐: 一律防呆、記錄原值；跨格式測試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q2, B-Q3, B-Q8

Q2: 如何根據 Orientation 套用 RotateTransform？
- A簡: 將 6/8/3 映射為 90/270/180，組入 TransformGroup 後套用。
- A詳: 步驟：1) 讀取 Orientation；2) 映射角度；3) 建立 TransformGroup 並加入 RotateTransform；4) 用 TransformedBitmap 載入。範例:
  - 具體實作步驟: 解析→映射→建立 RotateTransform→包裝。
  - 關鍵程式碼片段:
    ```csharp
    Rotation r=Rotation.Rotate0;
    if(o==6) r=Rotation.Rotate90; else if(o==8) r=Rotation.Rotate270; else if(o==3) r=Rotation.Rotate180;
    var tf=new TransformGroup(); tf.Children.Add(new RotateTransform(r==Rotation.Rotate90?90:r==Rotation.Rotate180?180:r==Rotation.Rotate270?270:0));
    ```
  - 注意事項與最佳實踐: 確認左右方向；加上單元測試。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q4, D-Q4

Q3: 如何以 TransformGroup 同時縮放與旋轉並輸出 JPEG？
- A簡: 建 TransformGroup（Scale+Rotate）→TransformedBitmap→JpegBitmapEncoder→Save。
- A詳: 步驟：1) 讀源 Frame 與 Orientation；2) TransformGroup 先加入 ScaleTransform(如 0.1,0.1)，再加 RotateTransform；3) 用 TransformedBitmap 包裝；4) JpegBitmapEncoder 設 QualityLevel 後 Save。範例:
  - 具體實作步驟: 讀→建 Transform→建 Frame→編碼。
  - 關鍵程式碼片段:
    ```csharp
    var tfs=new TransformGroup();
    tfs.Children.Add(new ScaleTransform(0.1,0.1));
    tfs.Children.Add(new RotateTransform(rotateAngle));
    var frame=BitmapFrame.Create(new TransformedBitmap(srcFrame, tfs), null, null, null);
    var enc=new JpegBitmapEncoder{QualityLevel=90}; enc.Frames.Add(frame);
    using var fs=File.Create(tmpPath); enc.Save(fs);
    ```
  - 注意事項與最佳實踐: 先 Scale 後 Rotate 一次取樣；妥善關閉串流。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q7, D-Q5

Q4: 如何兼容 .CR2 與 .JPG 的 Orientation 查詢？
- A簡: 依副檔名或解碼器選擇 /ifd 與 /app1 路徑，並提供保底策略。
- A詳: 步驟：1) 以副檔名判斷：.jpg→/app1/{ushort=0}/{ushort=274}；.cr2→/ifd/{ushort=274}；2) 若讀不到，嘗試另一條路徑再回落 1；3) 封裝成 TryGetOrientation。範例:
  - 具體實作步驟: 檢測→嘗試→回退。
  - 關鍵程式碼片段:
    ```csharp
    ushort TryGetOrient(BitmapMetadata m, string ext){
      foreach(var p in ext.Equals(".jpg",true)?new[]{"/app1/{ushort=0}/{ushort=274}","/ifd/{ushort=274}"}:new[]{"/ifd/{ushort=274}","/app1/{ushort=0}/{ushort=274}"}){
        try{ var v=m.GetQuery(p); if(v is ushort u) return u; }catch{}
      }
      return 1;
    }
    ```
  - 注意事項與最佳實踐: 記錄實際命中路徑，便於追蹤。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q8, D-Q3

Q5: 如何在輸出後將 Orientation 正規化為 1？
- A簡: 在寫入新 JPEG 時建立 Metadata，SetQuery 將 274 設為 1 並複製其他標籤。
- A詳: 步驟：1) 旋轉像素後建立 BitmapMetadata("jpg")；2) 複製關鍵標籤（時間、相機、GPS）；3) SetQuery("/app1/{ushort=0}/{ushort=274}", (ushort)1)；4) 建立 Frame 時傳入 Metadata。範例:
  - 具體實作步驟: 旋轉→新建 Metadata→寫入 274→輸出。
  - 關鍵程式碼片段:
    ```csharp
    var md=new BitmapMetadata("jpg");
    md.SetQuery("/app1/{ushort=0}/{ushort=274}", (ushort)1);
    var frame=BitmapFrame.Create(transformed,null,md,null);
    ```
  - 注意事項與最佳實踐: WPF 對部分標籤寫入有限制；必要時用專門庫。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q13, D-Q6, B-Q12

Q6: 如何為 180 度疑難個案提供手動旋轉 UI？
- A簡: 提供一鍵旋轉 180 或左右 90，套用 Transform 後重新輸出並設 Orientation=1。
- A詳: 步驟：1) 在 UI 加入「左轉/右轉/倒轉」按鈕；2) 更新 TransformGroup 的 RotateTransform；3) 重新輸出 JPEG 並把 Orientation 設為 1；4) 記錄使用者選擇避免重複操作。範例:
  - 具體實作步驟: UI→事件→重建 Transform→Save。
  - 關鍵程式碼片段:
    ```csharp
    void Rotate180(){ rotateAngle=(rotateAngle+180)%360; SaveWithTransform(); }
    ```
  - 注意事項與最佳實踐: 明確標示方向；避免重複壓縮可延後批次輸出。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q11, D-Q2, C-Q5

Q7: 如何批次處理資料夾中的相片並自動轉正？
- A簡: 列舉檔案→讀 Orientation→套 Transform→輸出至目標資料夾並記錄日誌。
- A詳: 步驟：1) Directory.EnumerateFiles 過濾影像；2) 逐檔讀 Orientation 映射角度；3) 以 TransformGroup 縮放+旋轉；4) 設定品質並 Save；5) 記錄處理結果。範例:
  - 具體實作步驟: Enumerate→Process→Save→Log。
  - 關鍵程式碼片段:
    ```csharp
    foreach(var f in Directory.EnumerateFiles(src,"*.jpg")) ProcessOne(f, dst);
    ```
  - 注意事項與最佳實踐: 串流 using；遇錯誤持續下一檔；輸出 Orientation=1。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, D-Q10, C-Q1

Q8: 如何印出關鍵 EXIF 以便診斷方向問題？
- A簡: 讀取並輸出 Orientation、相機型號、拍攝時間，觀察與實際顯示是否一致。
- A詳: 步驟：1) 取得 BitmapMetadata；2) 讀 Orientation、DateTimeOriginal、Model；3) 輸出至 Console 或檔案；4) 比對解碼器行為。範例:
  - 具體實作步驟: 讀→取值→列印→比對。
  - 關鍵程式碼片段:
    ```csharp
    Console.WriteLine($"Ori={o}, Model={md.GetQuery("/app1/{ushort=0}/Model")}");
    ```
  - 注意事項與最佳實踐: 不同路徑差異；注意 null 檢查。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q14, B-Q14, D-Q3

Q9: 如何設定 JPEG 壓縮品質與臨時檔流程？
- A簡: 設 QualityLevel，先寫入唯一命名的暫存檔，成功後再 Replace 或 Move。
- A詳: 步驟：1) 建 JpegBitmapEncoder 設 QualityLevel（建議 85–92）；2) 產生 GUID 命名暫存檔；3) Save 完成後以原子操作 Move/Replace；4) 最後刪除暫存檔。範例:
  - 具體實作步驟: 設品質→Save→原子替換。
  - 關鍵程式碼片段:
    ```csharp
    var tmp=Path.Combine(outDir,$"{Guid.NewGuid():N}.tmp");
    using var fs=File.Create(tmp); enc.Save(fs);
    File.Move(tmp,finalPath,true);
    ```
  - 注意事項與最佳實踐: 防止局部寫入；處理同名衝突與 IO 例外。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q10, D-Q9, C-Q3

Q10: 如何以單元測試驗證方向映射與輸出結果？
- A簡: 準備四方向測資，檢查輸出像素方向與 EXIF Orientation 是否為 1。
- A詳: 步驟：1) 準備 0/90/180/270 樣本；2) 呼叫處理函式；3) 驗證像素寬高交換、視覺方向；4) 驗證新檔 EXIF 274=1；5) 檢查品質與檔案大小合理性。範例:
  - 具體實作步驟: Arrange→Act→Assert。
  - 關鍵程式碼片段:
    ```csharp
    Assert.Equal((ushort)1, ReadOrientation(outJpg));
    ```
  - 注意事項與最佳實踐: 以黃金檔比對；加入容忍度；自動化回歸測試。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q14, D-Q4, C-Q2

### Q&A 類別 D: 問題解決類（10題）

Q1: 遇到相片在電腦側邊顯示，怎麼辦？
- A簡: 檢查 Orientation 與軟體支援，必要時套用旋轉並正規化標籤為 1。
- A詳: 症狀描述：相片在部分軟體側躺。可能原因：軟體未支援 Orientation、標籤缺失或為 1。解決步驟：1) 讀 Orientation；2) 若為 6/8/3，依值旋轉；若為 1 而實際方向錯，提供手動旋轉；3) 輸出並將 Orientation 設為 1。預防：建立統一的處理管線與自動測試，確保跨平台一致。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, C-Q3, D-Q4

Q2: 180 度拍攝未自動轉正的原因與處理？
- A簡: 相機未寫入 3 值，導致軟體無從得知；需手動旋轉或規則補償。
- A詳: 症狀描述：倒置照片仍直立顯示。原因分析：Canon G9/IXUS55 不為 180 度寫 3，維持 1。解決步驟：提供倒轉按鈕；批次處理新增「若疑似倒置則 180」規則（謹慎使用）；輸出時將 Orientation=1。預防：教育拍攝姿態；流程中加入人工覆核節點。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, A-Q11, C-Q6

Q3: WPF GetQuery 擲出例外或回傳 null 怎麼辦？
- A簡: 確認查詢路徑正確、格式匹配，加入 try-catch 與預設值回退。
- A詳: 症狀描述：GetQuery 拋例外或得 null。原因：使用錯誤根路徑（/app1 vs /ifd）、標籤不存在、權限或損毀。解決步驟：依副檔名選路徑；用 try-catch 包起來；null 時回 1。預防：封裝 TryGetOrientation；在測試中覆蓋多格式樣本。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, C-Q1, C-Q4

Q4: 旋轉方向相反（左右顛倒）如何修正？
- A簡: 調整 6/8 映射（CW/CCW），以四方向測資驗證修正。
- A詳: 症狀描述：應右轉卻左轉。原因：把 6/8 映射顛倒、坐標系定義混亂。解決步驟：校正對應：6=順時針 90，8=逆時針 90；以四方向測資驗證；更新單元測試涵蓋。預防：封裝常數、避免魔數、文件化對應規則。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q7, C-Q2, C-Q10

Q5: 輸出後相片變糊或鋸齒，如何改善？
- A簡: 合併旋轉與縮放、提高品質、避免多次重壓，必要時採無損方案。
- A詳: 症狀描述：縮圖有鋸齒、細節流失。原因：多次取樣、重複 JPEG 壓縮、低 QualityLevel。解決步驟：用 TransformGroup 一次取樣；QualityLevel 設 85–92；避免重複開存；需要無損時改寫 Orientation 或用無損工具。預防：建立畫質基準測試與黃金樣本比對。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q15, C-Q9

Q6: 輸出後 EXIF 遺失或日期異常，怎麼處理？
- A簡: 建立新 Metadata 並複製關鍵標籤，旋轉後將 Orientation 設為 1。
- A詳: 症狀描述：日期、相機資訊不見。原因：未將來源 Metadata 帶入新 Frame。解決步驟：新建 BitmapMetadata("jpg")；複製 DateTimeOriginal、Make/Model、GPS 等；SetQuery 274=1；Frame.Create 時傳入。預防：建立複製清單與自動化驗證。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q13, C-Q5, C-Q3

Q7: 檔案大小激增或畫質下降的可能原因？
- A簡: 多次壓縮、過高/過低品質設定或色度子取樣差異導致。
- A詳: 症狀描述：檔案異常變大或變糊。原因：重複編碼；QualityLevel 設太高/低；不同子取樣設定。解決步驟：一次完成轉換；選擇合理品質（85–92）；保持一致的編碼設定。預防：在 CI 中監控輸出大小與 SSIM/PSNR 指標。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, B-Q15, C-Q9

Q8: CR2 顯示正確但轉成 JPG 後歪斜，為何？
- A簡: RAW Codec 已自動旋轉，JPG 管線未套用旋轉，需手動依 EXIF 處理。
- A詳: 症狀描述：CR2 檔在預覽正確，JPG 縮圖歪。原因：RAW 解碼器預旋轉；JPG 解碼未旋轉。解決步驟：統一管線，在 JPG 路徑讀 Orientation 並套用 RotateTransform；對 CR2 亦可保守再判斷一次，避免雙重旋轉。預防：建立跨格式一致化策略與測試。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q5, C-Q3

Q9: 儲存 JPEG 時遇到「檔案被占用」或串流例外？
- A簡: 使用 using 關閉串流；先寫暫存檔後原子替換，避免併發衝突。
- A詳: 症狀描述：Save 擲出 IOException 或「Cannot access a closed file」。原因：未釋放來源/目標串流、同名覆蓋競爭。解決步驟：全面使用 using；先存至 GUID 暫存檔，成功後 Move/Replace；避免平行存取同一檔名。預防：封裝 IO 流程、加入重試與日誌。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q9, B-Q10, D-Q10

Q10: 批次處理有些檔案未被轉正，如何診斷？
- A簡: 檢查 Orientation 是否缺失、路徑是否錯誤，建立日誌並提供人工覆核。
- A詳: 症狀描述：少量成品方向仍錯。原因：標籤為 1（特別是 180 度）、讀取路徑不符、例外被吃掉。解決步驟：在日誌中輸出原始 Orientation 與命中路徑；對值為 1 的檔案標記待覆核；提供一鍵倒轉工具。預防：擴充 TryGet 與測試樣本；加入處理結果報表。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, C-Q7, C-Q8

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 EXIF？
    - A-Q2: 什麼是 EXIF Orientation（標籤 274）？
    - A-Q3: 為什麼有些相片會自動轉正、有些不會？
    - A-Q4: 相機上的自動轉正與電腦軟體有何差異？
    - A-Q7: Orientation 的常見值與對應旋轉是什麼？
    - A-Q8: 為什麼需要在 WPF 中自行處理旋轉？
    - A-Q14: 在相機上看到的自動轉正可信嗎？
    - B-Q2: EXIF Orientation 如何被檢視器利用以自動轉正？
    - B-Q3: WPF 如何載入影像與其 EXIF？
    - B-Q4: 由 Orientation 值推導旋轉角度的流程是什麼？
    - B-Q6: WPF 影像縮圖與旋轉的執行流程為何？
    - C-Q1: 如何在 WPF 中安全讀取 Orientation 值？
    - C-Q2: 如何根據 Orientation 套用 RotateTransform？
    - C-Q3: 如何以 TransformGroup 同時縮放與旋轉並輸出 JPEG？
    - D-Q1: 遇到相片在電腦側邊顯示，怎麼辦？

- 中級者：建議學習哪 20 題
    - A-Q5: Canon G9/IXUS55 對 180 度拍攝的支援如何？
    - A-Q6: CR2 與 JPG 在自動轉正行為有何差異？
    - A-Q9: 什麼是 WPF 的 BitmapMetadata 與 GetQuery？
    - A-Q10: 為何各格式的 metadata 查詢路徑不同？
    - A-Q12: 自動轉正的核心價值是什麼？
    - A-Q15: 建立縮圖流程時，應優先考量哪些方向資訊？
    - B-Q1: 相機如何偵測拍攝方向？
    - B-Q5: Canon RAW Codec 在解碼時如何自動旋轉？
    - B-Q7: TransformGroup 架構如何設計以同時縮放與旋轉？
    - B-Q8: 為什麼 .CR2 用「/ifd/{ushort=274}」，.JPG 用「/app1/{ushort=0}/{ushort=274}」？
    - B-Q9: TransformedBitmap 的工作機制是什麼？
    - B-Q10: JpegBitmapEncoder 如何建立 Frame 與設定品質？
    - B-Q14: 如何驗證 90/180/270 三種情境的處理正確？
    - B-Q15: 影像處理順序對品質與效能有何影響？
    - C-Q4: 如何兼容 .CR2 與 .JPG 的 Orientation 查詢？
    - C-Q7: 如何批次處理資料夾中的相片並自動轉正？
    - C-Q8: 如何印出關鍵 EXIF 以便診斷方向問題？
    - C-Q9: 如何設定 JPEG 壓縮品質與臨時檔流程？
    - D-Q3: WPF GetQuery 擲出例外或回傳 null 怎麼辦？
    - D-Q4: 旋轉方向相反（左右顛倒）如何修正？

- 高級者：建議關注哪 15 題
    - A-Q11: 只靠 Orientation 能完全判斷相片方向嗎？
    - A-Q13: 為什麼 Canon RAW Codec 會自動旋轉？
    - B-Q11: 當 Orientation 缺失或為 0x01 時軟體應如何處理？
    - B-Q12: 如何在不重新壓縮的情況下實現旋轉？
    - B-Q13: 如何保留或修改 EXIF（含時間、相機資訊與方向）？
    - B-Q15: 影像處理順序對品質與效能有何影響？
    - C-Q5: 如何在輸出後將 Orientation 正規化為 1？
    - C-Q6: 如何為 180 度疑難個案提供手動旋轉 UI？
    - C-Q10: 如何以單元測試驗證方向映射與輸出結果？
    - D-Q2: 180 度拍攝未自動轉正的原因與處理？
    - D-Q5: 輸出後相片變糊或鋸齒，如何改善？
    - D-Q6: 輸出後 EXIF 遺失或日期異常，怎麼處理？
    - D-Q7: 檔案大小激增或畫質下降的可能原因？
    - D-Q8: CR2 顯示正確但轉成 JPG 後歪斜，為何？
    - D-Q10: 批次處理有些檔案未被轉正，如何診斷？