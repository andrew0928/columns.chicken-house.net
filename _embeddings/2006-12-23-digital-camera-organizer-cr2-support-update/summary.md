# 歸檔工具更新 - .CR2 Supported

## 摘要提示
- .CR2 支援: 為回應朋友與同事需求，作者替歸檔工具加入 Canon RAW 檔 .CR2 的解析能力。
- 測試來源: 透過公司主管的 20D 拍攝樣本，驗證 Microsoft RAW SDK 對 .CR2 的相容性。
- 無 .THM 縮圖: .CR2 檔不附帶 .thm，導致以 SDK 轉出的 JPEG 不含完整 EXIF。
- 原廠雙檔策略: 高階 Canon DSLR 通常同步存一張完整尺寸 JPEG，減少另行轉檔需求。
- Attribute 改寫: MediaFilerFileExtensionAttribute 新增「逗號分隔」語法，可對應多副檔名。
- Factory Pattern: Create() 方法同步調整，讓單一 MediaFiler 處理多種延伸檔。
- 設定檔擴充: 在 configuration 中加入 pattern.cr2 區段，完成新格式註冊。
- 檔案下載: 更新後之 Binary 已釋出，供有需要者直接下載使用。
- G2 相容性怪癖: 作者發現自家 G2 拍 RAW 時如外閃未回電，Microsoft Raw Image Viewer 會解碼失敗。
- 感謝支持: 特別向購買 5D 的友人與提供樣本的老闆致謝，促成此次更新。

## 全文重點
作者雖未擁有 Canon DSLR，卻因友人、同事的需求決定為自製的數位影像歸檔工具加入 .CR2 支援。經由主管的 20D 拍攝樣本測試，確認 Microsoft RAW Image SDK 及其 Wrapper 對 .CR2 解析完全相容，呼叫方式與既有格式一致。唯一差異是 .CR2 不會伴隨 .thm 縮圖檔，導致 SDK 自動轉出的 JPEG 缺少完整 EXIF；然而多數高階 Canon 機身本就可同時存一張原尺寸 JPEG，故作者選擇不再實作額外轉檔流程。  
本次程式碼更新重點在於：1) 將 MediaFilerFileExtensionAttribute 改寫為可用逗號列舉多副檔名，以便單一 MediaFiler 同時服務 RAW、JPEG 等多格式；2) Factory Pattern 的 Create() 隨之調整；3) 設定檔加入 pattern.cr2，完成格式宣告。除了上述核心修改，再無其他影響。  
檔案已封裝為 Binary 供下載測試，作者並在文末小抱怨自己的 Canon G2：若外接閃光燈未及時回電導致曝光不足，該 RAW 影像雖能在機身預覽，卻會令 Microsoft Raw Image Viewer 與相同 SDK 解碼失敗並拋出例外，原因仍待查證。最後，作者感謝友人的 5D 以及老闆提供的樣本，讓工具得以快速提升功能性。

## 段落重點
### 加入 .CR2 支援的契機與測試過程
作者原本並未擁有 Canon DSLR，卻因朋友小熊子購入 5D 而被詢問工具能否解析 .CR2。為蒐集測試檔，他向公司主管借來 20D 拍攝數張 RAW，並以 Microsoft RAW Image SDK 及其 Wrapper 進行驗證。結果顯示函式介面與先前處理的格式無縫銜接，唯 .CR2 檔缺少 .thm 縮圖，導致自動轉出的 JPEG 不含完整 EXIF。考量高階 DSLR 通常同時產生一張完整 JPEG，作者評估後決定不再重做 .CR2→JPEG 流程，僅確保歸檔工具能正確接收與索引 .CR2 原檔。

### 程式碼與組態的核心更新
本次發佈僅動到少數關鍵區段。首先，MediaFilerFileExtensionAttribute 新增逗號分隔功能，允許一個 Attribute 同時標示多個副檔名，使單一 MediaFiler 可處理 RAW、JPEG、TIFF 等多格式；相對應的 Factory Pattern Create() 亦調整演算法，能依傳入副檔名自動比對正確的處理器。其次，在應用程式組態檔加入 pattern.cr2 區段，使新副檔名於啟動時即被註冊。除此之外並無其他變更，維護風險低且易於回溯。更新後的 Binary 已上傳並提供下載連結，方便使用者直接替換測試。

### 感謝、下載與 G2 解碼疑難
作者在文末特別感謝小熊子分享 5D 的使用心得，以及公司老闆提供 20D 样本，讓工具能夠迅速驗證並擴充 .CR2 支援。同時也附上最新 Binary 下載點，方便社群立即體驗。然而他亦抱怨自身的 Canon G2：若拍攝 RAW 時外閃來不及回電導致畫面嚴重欠曝，雖能在機背正常預覽，卻會在 Microsoft Raw Image Viewer 及相同 SDK 呼叫時拋出例外，無法解碼。此問題目前尚未找到成因，作者推測可能與 RAW 內部標記或相容性檢查有關，留待未來進一步排除。