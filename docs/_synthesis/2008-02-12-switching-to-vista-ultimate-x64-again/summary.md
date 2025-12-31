---
layout: synthesis
title: "再度換裝 Vista ... Vista Ultimate (x64)"
synthesis_type: summary
source_post: /2008/02/12/switching-to-vista-ultimate-x64-again/
redirect_from:
  - /2008/02/12/switching-to-vista-ultimate-x64-again/summary/
postid: 2008-02-12-switching-to-vista-ultimate-x64-again
---

# 再度換裝 Vista ... Vista Ultimate (x64)

## 摘要提示
- 升級動機: 以新硬碟與擴充記憶體為契機，轉向 Vista x64 以突破 32 位元限制與取得內建功能。
- 記憶體與架構: 64 位元系統能更好運用 >4GB 記憶體並改善記憶體管理效能。
- MCE/Tablet 整合: Vista x64 同時滿足 Media Center 與 Tablet PC 功能需求。
- 開發環境成熟: Visual Studio 2008 問題大幅減少，Vista 上開發更穩定。
- Canon Raw 支援: 官方不支援 x64 的瓶頸，透過 32 位元流程與設定繞過。
- 影像編解碼: 32/64 位元程式與 DLL 不能混用是關鍵相容性原則。
- 工具改建: 自製轉檔工具改為 x86 目標平台後即可抓到 Canon Raw Codec。
- 檔案管理顯示: 以 32 位元版 Windows Live Gallery 成功顯示 CR2 縮圖。
- 系統備份: Vista Complete PC 內建 VHD 磁碟映像備份，與 Virtual PC/Server 相容。
- 升級時機: Vista SP1 將出與正版授權已入手，時機成熟不再觀望。

## 全文重點
作者在先前短暫升級 Vista 後又回到 XP，經過近一年，因硬體更新與軟體環境成熟，決定再度升級至 Vista Ultimate x64。核心考量包含：新增 750GB 硬碟可並存新舊系統；欲擴充記憶體而 32 位元 XP 已不敷使用；希望同時保留 Media Center 與 Tablet PC 功能，而 Vista x64 是兼顧兩者的現成解法；內建 DVD 編碼與基本剪輯工具足以滿足日常需求；Vista 在多處小改良累積的體驗提升；家人使用經驗正向；以及想提早熟悉 IIS7，並配合即將推出的 Vista SP1 與已購買的正版授權。

升級時的最大障礙是 Canon Raw Codec 官方不支援 Vista x64，導致 CR2 檔縮圖與自製轉檔工具無法運作。作者回想 WOW64 的相容性原則：同一個行程內不得混用 32/64 位元代碼；問題常出在驅動與各式需內嵌於行程的 DLL/Codec/ActiveX。於是採取「整套 32 位元流程」策略：將自製轉檔工具的目標平台改為 x86，順利載入 Canon Raw Codec 與解析 metadata；同時改用 32 位元版的 Windows Live Gallery，CR2 縮圖顯示恢復正常。作者也提醒 Live Gallery 會留駐記憶體，未在開機後首次啟動就開對版本，之後可能仍跑錯位元版。整體而言，32 位元應用在 64 位元 OS 下仍可獲益，包括較佳的記憶體管理效率與擴大至 4GB 的使用位址空間。

此外，Vista 的 Complete PC 備份工具原生支援 VHD 影像，能一鍵建立磁碟映像並用安裝光碟還原，或透過 Virtual Server 的 VHDMOUNT 掛載使用，與作者既有虛擬化工作流程相容。隨著 Visual Studio 2008 解決先前在 Vista/x64 的偵錯與相容性問題，作者判定升級時機已成熟，對 Vista x64 的日常工作與影像處理流程亦已可行，因此不再觀望，並鼓勵有 x64 需求的使用者採用。

## 段落重點
### 升級背景與動機
作者先前因不適應而從 Vista 回到 XP，近一年後因硬體擴充需求與軟體生態成熟再度考慮升級。關鍵誘因包括：新增 750GB 硬碟可不影響舊系統；計畫擴充 RAM，32 位元 XP 的限制讓投資效益有限；需同時保留 Media Center 與 Tablet PC 功能，Vista x64 是唯一能同時滿足的版本；內建 DVD Codec 與基礎剪輯工具實用；Vista 雖無顛覆性改變，但多項小改良疊加帶來可感體驗；家人已穩定使用 Vista；希望熟悉 IIS7；Visual Studio 2008 出現後，先前在 Vista/x64 的開發痛點多已解決；Vista SP1 將出，加上已購買正版授權，綜合判斷為升級良機。

### Vista Complete PC 與 VHD 生態
升級後意外發現 Vista Complete PC 的實用性：可直接建立全碟 VHD 映像，並用 Vista DVD 還原，流程類似 Ghost，且與 Virtual PC/Server 的 VHD 生態一致。作者既使用虛擬化工具，VHDMOUNT 可將映像掛載直接取用，讓備份、還原、測試與遷移的效率大幅提升。此原生整合降低了第三方影像工具的依賴，讓系統維護與備援策略更簡單可控。

### Canon Raw Codec 在 x64 的限制
最大顧慮是 Canon Raw Codec 官方宣稱不支援 Vista x64。初步在虛擬機測試顯示能安裝但無法運作：自製轉檔工具抓不到 Codec，Windows Live Gallery 與檔案總管亦無法顯示 CR2 縮圖。此問題的本質源自 x64 環境中的位元數相容性：許多需要在行程內載入的元件（驅動、Codec、ActiveX、COM、ODBC、WPF Image Codec 等）若無對應位元數版本就無法在同一行程中共存，導致應用鏈斷裂。

### 32/64 位元相容性原則與效益
作者整理 x64 相容性的要訣：同一個 Process 內不可混用 32 與 64 位元代碼；因此驅動與 DLL 類型元件是難點。解法之一是「整套 32 位元」：在 x64 OS 上以 32 位元應用執行，避免混用。此作法除了解決相容性，還有實質效益：x64 OS 的記憶體管理效能較佳；雖然 32 位元應用仍受 4GB 限制，但在 x64 OS 下可利用完整 4GB 使用位址空間（不需與核心分割成 2GB/2GB），對大型應用是明顯助益。

### 實作繞過方案與使用注意
作者將自製轉檔工具的 .NET 目標平台從「Any CPU」改為「x86」，成功載入 Canon Raw Codec 並正確解析影像與 metadata；再開啟 Windows Live Gallery 的 32 位元版，CR2 縮圖亦能正確顯示。提醒一點：Live Gallery 啟動後可能留駐背景，若開機後首次未啟動正確位元版本，後續即使點 32 位元捷徑也可能仍以 64 位元常駐行程運作，需留意清除或重新啟動以確保載入正確版本。此繞過方案解除作者升級最大阻礙。

### 結語：升級決心與建議
在備份工具、開發環境、日常多媒體、IIS7 學習需求與 Canon Raw 的可行繞過方案加持下，作者決定轉向 Vista Ultimate x64，並認為這次不會像先前一樣退回 XP。對於準備採用 x64 的使用者，作者建議把握「整套 32 位元流程」原則來處理相容性問題；隨著 Vista SP1 的臨近與工具鏈成熟，已是合適的升級時機。

## 資訊整理

### 知識架構圖
1. 前置知識：學習本主題前需要掌握什麼？
- 32 位元與 64 位元系統的差異（記憶體定址、相容性、WOW64）
- 驅動程式、DLL、Codec 的基本概念與在同一 Process 中不可混用 x86/x64
- .NET Framework（目標平台 Any CPU/x86/x64 的影響）
- 影像工作流程與 RAW 格式（特別是 Canon CR2 與 Codec）
- Windows 安裝/備份還原基礎（Disk Image、VHD、Virtual PC/Server）
- 常見開發/工具環境（Visual Studio 2008、IIS7、Windows Live Gallery）

2. 核心概念：本文的 3-5 個核心概念及其關係
- Vista x64 的導入動機：硬體升級（大容量硬碟、>4GB RAM）、功能整合（MCE、Tablet PC）、內建工具與細節改良
- x86/x64 相容性原則：同一個 Process 內不可混用 32/64 位元元件（驅動、DLL、Codec、ActiveX）
- WOW64 與實務解法：在 x64 OS 下以 x86 版本程式運行，可繞過 x64 缺少的 Codec/元件限制
- 影像與開發流程的對應：Canon Raw Codec 僅有 x86；改以 x86 目標編譯或使用 x86 版的應用（如 Live Gallery）即能運作
- 系統內建能力增益：Complete PC（VHD 映像備份）、SuperFetch、IIS7、VS2008 相容改善

3. 技術依賴：相關技術之間的依賴關係
- Canon CR2 縮圖/解碼 → 依賴 Canon Raw Codec（x86） → 需要 x86 應用或 x86 目標編譯
- WPF 影像編解碼/Metadata → 依賴對應位元數的 Image Codec/DLL
- IE/ActiveX → ActiveX 多為 x86 → 在 x64 OS 常需使用 IE 32 位元
- Windows Live Gallery → 提供 x86/x64 版本 → 首次啟動版本會常駐，需注意版本選擇
- 系統映像備份 → Vista Complete PC → 產出 VHD → 可用 VHDMOUNT 或 Virtual Server/PC 掛載
- 開發/偵錯 → VS2008 在 Vista/x64 上的相容性與補丁狀況優於 VS2005

4. 應用場景：適用於哪些實際場景？
- 攝影工作者或開發者需在 x64 系統閱覽/處理 CR2 檔案
- 想升級至 >4GB RAM 並整合 Media Center、Tablet 功能的桌面環境
- 需要快速全碟映像備份/還原與虛擬化互通（VHD）的人員
- 在 Vista x64 上進行 Web/IIS7 開發與 VS2008 開發偵錯
- 需要利用 SuperFetch 等提升大型應用啟動體驗的使用者

### 學習路徑建議
1. 入門者路徑：零基礎如何開始？
- 了解 x86/x64 基礎概念與 WOW64 運作
- 規劃新硬碟與分割，備份現有系統
- 安裝 Vista x64，安裝常用驅動與 Windows Update
- 啟用 Complete PC 備份，建立第一份全碟映像（VHD）
- 安裝 Windows Live Gallery，確認 x86 版本可正確顯示 CR2
- 體驗內建多媒體（DVD Codec、簡易剪輯）、Tablet/手寫功能

2. 進階者路徑：已有基礎如何深化？
- 在 .NET 專案調整目標平台為 x86 以使用 x86 Codec/COM（避免 Any CPU 混位元問題）
- 研究並設定 IIS7（站台、應用程式集區、管理工具）
- 導入 VS2008 開發與偵錯於 Vista x64，熟悉必要權限與相容性設定
- 評估並最佳化 SuperFetch、記憶體使用與開機常駐程式
- 練習使用 VHDMOUNT/Virtual Server 掛載 VHD 進行檔案抽取與快速回復

3. 實戰路徑：如何應用到實際專案？
- 建立「安裝→備份→驗證」流程：安裝 Vista x64 → 完整驅動 → 安裝關鍵應用 → 建立 VHD 映像
- 對影像處理工具鏈：鎖定 x86 目標平台 → 測試 CR2 解碼與 Metadata 擷取 → 自動化批次轉檔
- 前端相容性策略：在 x64 環境中規範瀏覽器/元件以 x86 版本為主（IE/ActiveX）
- 服務部署：以 IIS7 部署測試站，驗證 .NET 應用在 x64 OS + x86 AppPool 的行為
- 回復演練：以 Vista DVD 或虛擬化工具從 VHD 還原/掛載，建立災難復原操作手冊

### 關鍵要點清單
- 升級動機整合：硬碟擴充、RAM 超過 4GB、功能整併（MCE/Tablet）(優先級: 高)
- x86/x64 不可混用原則：同一 Process 內 DLL/Codec/COM 必須同位元 (優先級: 高)
- WOW64 策略：在 x64 OS 下使用 x86 應用繞過 x64 元件缺口 (優先級: 高)
- .NET 目標平台設定：將 Any CPU 改為 x86 可啟用 x86 專屬 Codec/元件 (優先級: 高)
- Canon Raw Codec 限制：僅有 x86 版，需以 x86 App 或 x86 編譯來支援 CR2 (優先級: 高)
- Windows Live Gallery 雙版本：首次啟動會常駐，需確保啟動 x86 版以顯示 CR2 縮圖 (優先級: 中)
- IE/ActiveX 相容性：多數 ActiveX 僅支援 x86，需在 x64 OS 使用 IE 32 位元 (優先級: 中)
- 記憶體效益：x64 OS 提供較佳記憶體管理；x86 程式可用定址空間擴至 4GB (優先級: 中)
- Vista Complete PC：內建全碟映像備份為 VHD，便於還原與虛擬化使用 (優先級: 高)
- VHDMOUNT/虛擬化串接：可直接掛載 VHD 取用檔案或於 Virtual PC/Server 使用 (優先級: 中)
- SuperFetch/Caching：以 RAM 當快取提昇常用大型應用啟動體驗 (優先級: 低)
- VS2008 相容性：相較 VS2005，於 Vista/x64 上的偵錯與權限問題大幅改善 (優先級: 中)
- IIS7 學習與預研：借由 Vista 先行研究與部署，為 Server 版鋪路 (優先級: 中)
- MCE/Tablet 功能整合：Vista x64 單一版本即可同時具備（相較 XP 的版本區隔）(優先級: 低)
- 升級時機：Vista SP1 將近、環境逐步成熟，降低遷移風險 (優先級: 低)