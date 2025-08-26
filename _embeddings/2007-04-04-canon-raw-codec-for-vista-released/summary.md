# Canon RAW Codec for Vista 出來了..

## 摘要提示
- 發佈消息: 微軟 PIX 部落格於 2007/03/30 宣布 Canon RAW Codec for Vista 釋出。
- WPF 與 WIC: 作者先前抱怨 WPF 的 WIC 未內建 Canon RAW 編解碼器。
- 支援格式限制: 新版僅支援 .CR2 檔案格式，不支援較舊的 .CRW。
- 老機使用者困境: 使用 Canon G2 等舊機的使用者因 .CRW 未獲支援而受限。
- 期望後續更新: 作者盼望未來能補上 .CRW 的 codec。
- 時間差誤解: 作者在抱怨後才發現其實功能已於 3/30 釋出，自嘲「失敬」。
- 生態系整合: 有了 codec，Vista 與 WPF 圖像處理生態可望更完整。
- 向後相容性: 檔案格式支援分歧凸顯向後相容的重要性。
- 使用情緒: 作者以幽默語氣表達失望與等待心情。
- 參考來源: 提供官方公告連結供讀者查閱詳情。

## 全文重點
這篇短文記錄了作者對「Canon RAW Codec for Vista」釋出的即時反應與心情轉折。作者原本才抱怨 WPF 的 Windows Imaging Component（WIC）沒有內建 Canon RAW 的編解碼器，結果發現微軟在 2007 年 3 月 30 日已透過 PIX 部落格宣布釋出 Canon RAW Codec，讓他自嘲「失敬」。不過喜訊之中仍有遺憾：這次釋出的版本僅支援較新的 .CR2 格式，對使用較早期 Canon 機種（例如作者的 G2）所產出的 .CRW RAW 檔案並不相容。這使得仍在使用舊機的使用者，即便有了 Vista 平台與 WPF/WIC 的整合優勢，也無法直接受惠於新 codec 帶來的系統層級解碼、縮圖和預覽功能。文章以輕鬆幽默的語氣表達對產品支援策略的複雜情緒：一方面肯定 Canon RAW Codec 的推出補上了 Windows 影像處理流程的一塊拼圖，提升了應用整合與工作流效率；另一方面則對缺乏向後相容的設計感到無奈，凸顯影像格式世代差異帶來的長尾需求未被滿足。最後，作者期盼未來能補上 .CRW 的支援，選擇「再等一等」作為折衷，反映技術更新與使用者期待之間的拉鋸。全文雖短，但指向三個重點：其一，Windows 影像生態對專有 RAW 編解碼器的依賴；其二，廠商對新舊格式資源配置的不平衡；其三，終端使用者在器材世代更迭中的尷尬處境。文末附上官方公告連結，方便讀者追蹤細節與後續更新。

## 段落重點
### Canon RAW Codec 釋出與來源
文章首先引用微軟 PIX 部落格於 2007/03/30 的公告，指出 Canon RAW Codec for Vista 已正式釋出，並提供原始連結作為資訊來源。此舉代表在 Windows 平台上，透過 WIC 可支援 Canon RAW 的系統層級解碼，對於使用 Vista 進行影像管理、預覽與處理的工作流程是一大補強。

### WPF/WIC 缺口被補上但僅限 .CR2
作者提到自己才剛抱怨 WPF 的 WIC 沒有內建 Canon RAW codec，旋即發現其實已經推出，語帶自嘲；然而關鍵限制在於僅支援 .CR2 格式。也就是說，較新的 Canon 機種拍攝的 RAW 可受惠，但舊機產出的 .CRW 檔案仍然無法由系統直接解碼、預覽或產生縮圖，功能覆蓋不完整。

### 舊機使用者的失落與對 .CRW 支援的期待
作者以自身使用老相機 Canon G2 的經驗，表達對缺乏 .CRW 支援的失望與無奈，語氣幽默卻直指需求落差。雖然新 codec 的出現使生態更完整，但對長尾用戶而言效益有限。文章最後以「往好方面想」收束，期待 .CRW 的 codec 能在未來推出，選擇繼續等待，反映使用者對向後相容與全面支援的持續期待。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - Windows Vista 影像基礎架構（WIC, Windows Imaging Component）
   - WPF 影像處理與 BitmapSource/Imaging API 基礎
   - 相機 RAW 格式概念與差異（Canon .CR2 vs .CRW）
   - 編解碼器（Codec）的角色與作業系統層級整合

2. 核心概念：
   - WIC 編解碼模型：作業系統透過安裝的編解碼器提供影像解碼能力
   - Canon RAW Codec（Vista 版）：新增對 Canon RAW 的系統層支援
   - 格式支援範圍：此版僅支援 .CR2，不含舊款 .CRW
   - WPF 與 WIC 整合：WPF 影像顯示依賴 WIC 可用的編解碼器來讀取 RAW
   - 向下相容性問題：舊相機（如 Canon G2 的 .CRW）受限於缺少對應 codec

3. 技術依賴：
   - WPF 影像顯示 → 依賴 WIC → 依賴已安裝的第三方/原廠 Codec（此處為 Canon RAW Codec）
   - 檔案瀏覽與縮圖（Explorer/Photo Gallery）→ 依賴 WIC → 受支援格式清單（現支援 .CR2）
   - 舊格式（.CRW）→ 需額外第三方 codec 或轉檔工具（如 DNG 轉檔）→ 才能被 WIC/WPF 使用

4. 應用場景：
   - Windows Explorer/Photo Gallery 顯示 Canon .CR2 縮圖與預覽
   - WPF 應用程式載入並顯示 .CR2 RAW 檔
   - 攝影工作流程在 Vista 環境中原生支援 .CR2 的瀏覽與基礎處理
   - 企業/個人相片管理工具整合系統層解碼以簡化相容性

### 學習路徑建議
1. 入門者路徑：
   - 了解 RAW 與 JPEG 的差異與 Canon RAW 格式（.CR2/.CRW）
   - 在 Vista 環境安裝 Canon RAW Codec，驗證 Explorer 能顯示 .CR2 縮圖/預覽
   - 認識 WIC 是 OS 級影像解碼層，應用程式可直接受惠

2. 進階者路徑：
   - 學習 WPF 影像 API（BitmapImage、BitmapSource）與透過 WIC 載入影像
   - 實作載入流程中的例外處理與格式偵測（不支援格式時的降級策略）
   - 探索第三方 codec 或轉檔（例如將 .CRW 轉 DNG/JPEG）以支援舊格式

3. 實戰路徑：
   - 寫一個簡易 WPF RAW 檢視器：偵測系統可用編解碼器、載入 .CR2、顯示縮圖與中繼資料
   - 實作不支援格式（如 .CRW）時的替代管道：提示安裝對應 codec 或啟用轉檔流程
   - 建立部署指引：安裝 Canon RAW Codec 的必要性與版本檢查腳本

### 關鍵要點清單
- WIC（Windows Imaging Component）：Vista 的系統級影像解碼層，應用可共用編解碼能力 (優先級: 高)
- WPF 與 WIC 整合：WPF 影像載入依賴 WIC 已安裝的 codec (優先級: 高)
- Canon RAW Codec 釋出：2007/03/30 發佈的 Vista 專用 Canon RAW 解碼器 (優先級: 中)
- 支援格式限制：此版僅支援 .CR2，未支援 .CRW (優先級: 高)
- 舊機型相容性：如 Canon G2 使用 .CRW，現階段無法受益於此 codec (優先級: 高)
- 系統層受益：安裝 codec 後，Explorer/Photo Gallery/WPF 皆能讀取 .CR2 (優先級: 高)
- 開發者影響：WPF 開發可直接載入 .CR2，減少自寫解碼或外掛流程 (優先級: 中)
- 例外處理策略：對不支援格式需檢測並提供替代（提示安裝、轉檔） (優先級: 中)
- 轉檔替代方案：對 .CRW 可考慮轉 DNG 或使用第三方 codec (優先級: 中)
- 驅動/codec 維護：留意原廠後續更新是否加入 .CRW 支援 (優先級: 中)
- 測試驗證：安裝後以 Explorer/相片工具驗證縮圖/預覽是否生效 (優先級: 中)
- 平台限制：本次 codec 釋出針對 Vista，其他 Windows 版本需確認相容性 (優先級: 低)
- 工作流程優化：系統級解碼可簡化攝影與管理工具的整合成本 (優先級: 中)
- 使用者教育：告知使用者其相機格式與系統支援狀態，避免誤解 (優先級: 低)