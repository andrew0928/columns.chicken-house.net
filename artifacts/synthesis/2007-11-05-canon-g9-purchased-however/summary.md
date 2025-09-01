# Canon G9 入手, 不過...

## 摘要提示
- 購機動機: 觀望多代後決定入手 Canon G9，因其回歸 RAW、採用 DIGIC III 與具備 IS。
- 機型取捨: 因缺少熱靴、功能退步或無 RAW，先後淘汰 S2/S3/S5、G6、G7 等選項。
- 畫質期待: 小尺寸感光元件高像素導致畫質僅與 G2 相當，有時 G2 反勝，略感失望。
- 檔案體積: 12MP 造成 RAW 12–15MB、JPEG 3–4MB，RAW+JPEG 單張可達 18MB。
- 配件升級: 因檔案大與 SDHC 需求，連帶更換記憶卡與讀卡機。
- RAW 相容性: 多數主流軟體（PS、DPP、Raw Codec 1.0、MS Viewer）無法讀 G9 CR2。
- 工作流程受阻: 自寫歸檔程式仰賴 EXIF 與 RAW 轉檔，因不相容而中斷。
- 暫時解法: 改用 RAW+JPEG，歸檔流程跳過 RAW→JPEG 步驟以維持可用。
- 新版編解碼器: Canon Raw Codec 1.2 釋出，名義支援 G9/G2 RAW，實測仍有阻礙。
- 實測問題: 速度極慢、單執行緒、WPF 取不到 EXIF，導致歸檔自動化仍不可行。

## 全文重點
作者在長期評估 Canon 高階消費機之後，最終於 G9 世代入手水貨，主因在於 G9 回補 RAW、升級 DIGIC III、鏡頭具 IS，整體規格在可接受範圍內。先前考慮過 G 系列與 S 系列多款機種，但因缺少熱靴、畫質進步有限或移除 RAW 等因素而放棄。雖然購前做足功課，實際使用仍遭遇多重瓶頸：首先是畫質並不驚艷，小尺寸感光元件硬塞高像素導致細節與噪點控制有限，與舊款 G2 相比未見明顯優勢，偶爾甚至略遜；其次檔案體積巨大，RAW 動輒 12–15MB，JPEG 3–4MB，RAW+JPEG 單張可至 18MB，使得小容量記憶卡形同虛設，被迫購入 SDHC 並更換讀卡機。

最關鍵的障礙在於 RAW 格式相容性。購機初期，Photoshop 更新後仍不認得 G9 的 CR2，多數主流工具（Canon Raw Image Converter、DPP 3.0、Microsoft Raw Image Viewer、Raw Codec for Vista 1.0）也無法處理，僅 ZoomBrowser EX 可用，但工作流程受限；Google Picasa 雖可開檔但顏色不正。此狀況直接影響作者自製的歸檔系統，因該系統仰賴 EXIF 與 RAW→JPEG 流程，以自動歸檔、改檔名與影像旋正。為維持基本可用性，只能調整流程：改以 RAW+JPEG 拍攝，並在歸檔時暫不進行 RAW 轉 JPEG。

稍後 Canon 釋出 Raw Codec 1.2，宣稱支援 G9 與 G2 RAW。作者立即測試並整合至 .NET 3.0 的 WPF，實測在 XP SP2 亦能運作，突破官方標示的 Vista 32 位限制。然而新問題浮現：CR2 解碼速度極慢，15MB 檔案需近一分鐘，即便在 Core2Duo 6300 上也僅用到約 50% CPU，推測為單執行緒公寓模式，使多核心優勢無從發揮；更糟的是透過 WPF 仍無法取得任何 EXIF，中介回傳的 BitmapMetadata 為空。對作者而言，這等同於無法支撐既有的自動化歸檔架構：既讀不到必要的 EXIF，又付出極高的時間成本。結論是短期內仍得依賴 RAW+JPEG 的折衷方案，等待 Canon 後續改良編解碼器的效能與 metadata 支援，才有可能全面更新自動化流程。

## 段落重點
### 購機背景與機型取捨
作者自 G6 時代便物色新機，但因 G6 與 G2 同用 DIGIC，效能與錄影表現平平而作罷；S2/S3 因缺乏熱靴不列入，S5 也未打動人。G7 雖採 DIGIC II 屬大改版，但縮小光圈、取消翻轉 LCD 與 RAW，使其不在考慮名單。最終選定的 G9 與 G7 相近，關鍵在於加回 RAW、升級 DIGIC III，並具 IS，綜合考量後在可接受範圍內入手水貨，價差約三千。雖然 Canon 並無 G8，此代被視為回應使用者需求的折衷之作，讓作者決定行動。

### 初期使用的主要阻礙
實拍後的第一印象是畫質未達預期：小面積 CCD 搭配高像素造成訊噪與細節表現受限，整體與 G2 相近，偶爾 G2 還略勝。第二是檔案體積膨脹，12MP 導致 RAW 12–15MB、JPEG 3–4MB，RAW+JPEG 可達 18MB，官方附贈 32MB 記憶卡不堪使用，被迫升級至 SDHC 並更換讀卡機。第三是 RAW 相容性崩盤：PS、Canon 舊工具、微軟檢視器與舊版 Codec 均無法正常讀取 G9 的 CR2，僅 ZoomBrowser EX 勉強可用，Picasa 顏色不正。這些限制讓既有的影像處理與管理習慣受到嚴重影響。

### 工作流程受影響與暫行調整
由於作者的自製歸檔程式依賴 EXIF 與 RAW→JPEG 流程進行自動歸檔、改名與自動旋轉，在 RAW 無法解的情況下整個流程陷入停擺。為了不中斷拍攝與管理，作者選擇改變策略：沿用 RAW+JPEG 的拍攝模式，並在歸檔時跳過 RAW→JPEG 的轉換，以 JPEG 作為瀏覽與管理主體，暫緩完整的 RAW 工作流。8GB SD 暫能支撐此方式，但並非長久之計，仍期待上游軟體端盡快補齊支援。

### Canon Raw Codec 1.2 更新與實測
Canon 釋出 Raw Codec 1.2，宣稱支援 G9 與 G2 的 RAW。作者將其與 .NET 3.0 WPF 結合測試，發現即使在 XP SP2 也可運作，突破了官方的 Vista 32-bit 限制。然而實測暴露出三大問題：解碼速度極慢，15MB CR2 需近 60 秒；CPU 使用率僅約 50%，推測為 Single Thread Apartment，無法利用雙核；透過 WPF 抓取不到任何 metadata，BitmapMetadata 為 null。這些問題使其難以納入自動化歸檔流程，尤其 metadata 缺失直接阻斷 EXIF 依賴的各項自動化功能。

### 結論與後續打算
綜合評估，G9 在硬體與手感上仍符合預期，IS 與新處理器帶來整體可用性提升；但在畫質、檔案體積與軟體鏈相容性上，短期內必須以 RAW+JPEG 的混合模式折衷。Canon Raw Codec 1.2 雖解鎖了基本支援，卻因速度慢、單執行緒與無 EXIF 可取而難以實戰。作者暫定持續以 JPEG 為管理主軸，等待 Canon 改善 Codec 的效能與 metadata 支援後，再行更新自動化歸檔流程與完整 RAW 作業。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 數位相機基本概念（感光元件尺寸、畫素、光圈、IS、熱靴）
   - 影像檔格式差異（RAW vs JPEG）、EXIF 中繼資料的用途
   - Windows 影像解碼流程（Codec/RAW 解碼器、WIC/WPF）、軟硬體相容性
   - 儲存媒體（SD/SDHC）與讀卡機相容性與效能

2. 核心概念：
   - 相機世代差異與取捨：G2/G6/G7/G9 在 DIGIC、RAW、翻轉螢幕、光圈等變化影響實拍與工作流
   - RAW 工作流程與軟體相容性：各家軟體對 .CR2（G9）的支援落差造成流程阻塞
   - 檔案體積與儲存策略：1200 萬畫素導致 RAW/JPEG 體積暴增，牽動記憶卡與讀卡機升級
   - Codec 實作限制與效能：Canon RAW Codec 1.2 在 WPF 的相容性、單執行緒、EXIF 讀取問題
   - 臨時性解法與流程調整：以 RAW+JPEG 拍攝、歸檔程式跳過 RAW→JPEG、等待官方解碼器改善

3. 技術依賴：
   - Canon RAW Codec 1.2 依賴 Windows 影像架構（WIC），官方標註 Vista 32-bit，但實測可用於 XP SP2
   - WPF（.NET Framework 3.0）呼叫 RAW Codec；Runtime Callable Wrapper 與 COM/S(T)A 模式影響多緒化
   - 軟體支援鏈：Photoshop ACR、Canon DPP/Raw Image Converter、ZoomBrowser EX、Microsoft Raw Image Viewer、Google Picasa（色彩不正）
   - 硬體效能與平行化：Core2Duo 在單執行緒解碼下無法有效吃滿多核

4. 應用場景：
   - 攝影者升級相機與建立 RAW 工作流程
   - Windows 平台上的相片歸檔與自動化（依賴 EXIF 的自動命名、旋轉、分類）
   - 軟體相容性未成熟時的過渡期操作（RAW+JPEG 並行）
   - 企業/個人影像庫需評估解碼效能與中繼資料可用性的情境

### 學習路徑建議
1. 入門者路徑：
   - 認識 RAW 與 JPEG 差異、EXIF 是什麼以及為何重要
   - 瞭解 G 系列相機功能（DIGIC、IS、熱靴、翻轉螢幕）與實拍差異
   - 建立基本儲存觀念：選購 SDHC 與相容讀卡機、估算容量與檔案大小

2. 進階者路徑：
   - 試裝與比對不同 RAW 解碼器（Canon Codec、DPP、ACR、第三方）之相容性與色彩表現
   - 在 Windows 上以 WPF/.NET 建立簡單影像瀏覽與 EXIF 讀取工具，驗證 Codec 與 WIC 行為
   - 評估與優化流程：RAW+JPEG 並拍、批次處理、備援軟體清單與色彩管理

3. 實戰路徑：
   - 實作歸檔程式：自動依 EXIF 改檔名、分類、旋轉；設計容錯（EXIF 缺失 fallback）
   - 進行效能測試：多緒排程 vs 單緒 Codec 限制、I/O 與 CPU 使用率監控
   - 制定過渡策略：在官方 Codec 改善前的操作規範、版本鎖定與回滾計畫

### 關鍵要點清單
- G 系列升級取捨：G7 移除 RAW/翻轉 LCD、縮光圈；G9 把 RAW 加回並升級 DIGIC III (優先級: 高)
- 影像畫質期望管理：小感光元件高像素下畫質進步有限，與 G2 互有勝負 (優先級: 中)
- RAW 檔案體積：G9 的 .CR2 約 12–15MB，JPEG 約 3–4MB，RAW+JPEG 可至 ~18MB/張 (優先級: 高)
- 儲存升級連鎖：需改用 SDHC 大容量卡並更換相容讀卡機 (優先級: 中)
- 軟體相容性斷鏈：多數常見軟體初期不支援 G9 .CR2，流程受阻 (優先級: 高)
- 臨時可用工具：隨機附的 ZoomBrowser EX 可讀，Picasa 可讀但色彩有誤 (優先級: 中)
- Canon RAW Codec 1.2 發布：新增對 G9 與 G2 RAW 的支援 (優先級: 高)
- 平台相容性觀察：雖標示 Vista 32-bit，實測在 XP SP2 也可用 (優先級: 中)
- 解碼效能瓶頸：15MB .CR2 在 Core2Duo E6300 需近 60 秒，效率偏低 (優先級: 高)
- 多核無法吃滿：Codec 疑為 STA/單緒設計，Thread Pool 併發仍僅約 50% CPU 使用 (優先級: 高)
- EXIF 取用失敗：透過 WPF 取得 BitmapMetadata 為 null，導致自動化歸檔流程失效 (優先級: 高)
- 工作流調整：改以 RAW+JPEG 並拍並在歸檔時跳過 RAW→JPEG 步驟應急 (優先級: 高)
- IS 與鏡頭改進：硬體穩定與成像整體仍有感提升，具實用價值 (優先級: 中)
- 自製工具依賴：歸檔程式高度依賴 EXIF 以命名/旋轉/分類，需設計容錯 (優先級: 高)
- 待官方優化：需等待 Canon Codec 改善效能與中繼資料支援再全面改版 (優先級: 中)