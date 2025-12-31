---
layout: synthesis
title: "Canon Digital Camera 記憶卡歸檔工具 - RAW Support Update"
synthesis_type: summary
source_post: /2006/11/04/canon-digital-camera-organizer-raw-support-update/
redirect_from:
  - /2006/11/04/canon-digital-camera-organizer-raw-support-update/summary/
postid: 2006-11-04-canon-digital-camera-organizer-raw-support-update
---

# Canon Digital Camera 記憶卡歸檔工具 - RAW Support Update

## 摘要提示
- 問題起點: 使用者抱怨不支援 RAW 檔，促成工具更新
- 資源稀缺: Canon RAW 開放資源少，多數專案不成熟且不可靠
- 官方 SDK: Canon 提供免費 C++ SDK，但需申請且非 .NET 友善
- 微軟線索: 找到 Microsoft RAW Image Thumbnailer and Viewer for Windows XP
- Interop 組件: RawManager.Interop.dll 可於安裝目錄取得並供 .NET 呼叫
- C# 存取: 以 CRawViewerClass 載入 RAW 並讀取 CameraModel 等屬性
- 內部實作: Interop 背後實作仍依賴 Canon Digital Camera SDK
- 功能限制: 目前僅讀取資訊，尚無編輯 RAW 或自動轉正功能
- 更新釋出: 提供新版 DigitalCameraFiler 安裝檔與先決安裝需求

## 全文重點
作者因應使用者反映記憶卡歸檔工具不支援 RAW 檔，著手尋找解法。市場上能穩定存取 Canon RAW（如 CRW）的自由軟體資源很少，多數看來尚未成熟；Canon 雖提供免費的 Digital Camera SDK，但僅支援 C++、需申請，對於以 .NET 為主的開發流程不夠便利。作者多年未碰 C++，傾向尋找可直接在 .NET 使用的方案。

在搜尋過程中，作者發現微軟推出的 Microsoft RAW Image Thumbnailer and Viewer for Windows XP，能在系統中提供各家 RAW 檔的預覽與縮圖功能。安裝後，於其安裝目錄內找到 RawManager.Interop.dll，經反組譯與試用，確認這個 Interop 組件提供一致、易懂的 .NET 介面，可直接在 C# 中載入 Canon RAW 檔並讀取內部資訊，如相機型號(CameraModel)。雖然實際底層仍由 Canon Digital Camera SDK 負責，但透過這個 Interop，開發者可用 C# 便捷地存取 RAW Metadata，無須自行撰寫 C++ 包裝。

作者展示了簡短的 C# 範例，透過 CRawViewerClass 物件載入檔案並輸出 CameraModel，證明整合可行與介面設計友善。功能方面，目前重點在讀取資訊與檔案管理，尚未找到可編輯 RAW 的 API；對於「自動轉正」等影像處理訴求，作者與使用者溝通後認為 RAW 的核心需求多半是時間與基本 metadata 的準確取得，因此本次更新優先解決讀取需求，後續再視需要評估進一步編輯能力。

最後，作者提供更新後的 DigitalCameraFiler 安裝檔下載連結，並明確標示使用前需先安裝 Microsoft RAW Image Thumbnailer and Viewer for Windows XP，因為 Interop 組件與功能即隨該工具安裝。整體而言，此更新用最小成本實現了 RAW 支援：在不重寫 C++ 的前提下，藉由微軟提供的 Interop 將 Canon SDK 能力帶入 .NET 應用，使既有的記憶卡歸檔工具能讀取 RAW 內部資訊、提升相容性與實用性，同時也為後續擴充（如更多 metadata 欄位、批次處理與進階功能）鋪路。

## 段落重點
### 背景與動機：使用者需求驅動的 RAW 支援
作者的記憶卡歸檔工具原本不支援 RAW，因使用者反映希望能處理 Canon RAW（如 CRW），觸發作者尋求解法。重點在於以 .NET 為基礎的專案能否快速支援 RAW metadata 存取，以維持開發效率並避免投入高成本的底層重寫。

### 探索可用資源：開源不足與官方 SDK 侷限
搜尋過程發現能穩定處理 Canon RAW 的開源專案稀少、多數不成熟；Canon 的 Digital Camera SDK 雖免費，但僅支援 C++ 且需申請，對 .NET 生態不友善。作者多年未碰 C++，因此尋找能直接在 .NET 環境運行的替代方案，以降低整合成本與維運風險。

### 微軟工具線索：RAW Viewer 與 Interop 組件
發現 Microsoft RAW Image Thumbnailer and Viewer for Windows XP 能在系統層級提供 RAW 縮圖與檢視功能。安裝後於目錄中找到 RawManager.Interop.dll，經反組譯與測試，確認它提供可在 .NET 直接呼叫的類別，解決了先前缺乏可靠 .NET 函式庫的痛點，等同為 Canon SDK 提供了受管包裝。

### C# 整合實作：CRawViewerClass 簡潔用法
透過 Interop 的 CRawViewerClass，C# 可直接載入 RAW 檔並讀取屬性。示例程式以三行程式碼完成 Load 與 CameraModel 輸出，顯示 API 設計一致、學習曲線低。雖然實務仍由 Canon SDK 處理，但開發者不必面對 C++ 細節，達到快速導入與維護容易的平衡。

### 功能界線與需求對齊：以讀取為先
目前尚未取得可編輯 RAW 或自動轉正的 API。與使用者溝通後確認，最關鍵需求是正確取得拍攝時間等 metadata，圖片旋轉並非當務之急。因此本次更新聚焦在可靠讀取資訊，待未來有合適 API 再考慮影像處理與編輯能力，避免過度設計。

### 發佈與安裝需求：下載與先決條件
作者提供更新版 DigitalCameraFiler 的安裝檔連結。使用前必須先安裝 Microsoft RAW Image Thumbnailer and Viewer for Windows XP，因 Interop 組件 RawManager.Interop.dll 隨該工具提供且為功能運作的關鍵依賴。此部署方式簡化相依管理，確保工具能在目標環境正常讀取 RAW 檔資訊。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 基本相機與影像格式知識（RAW/CRW 與 EXIF 概念）
   - .NET/C# 基礎程式設計
   - Windows 環境安裝與系統相依性（Windows XP 時代工具）
   - COM/Interop 基本觀念與 DLL 參照
2. 核心概念：
   - RAW 檔讀取與中介層：利用 Microsoft RAW Image Thumbnailer and Viewer 的 Interop DLL 讀取 RAW
   - 技術相依策略：不直接用 Canon C++ SDK，改以 Microsoft 發佈的 Interop 封裝
   - 中介組件使用方法：透過 RawManager.Interop.dll 的 CRawViewerClass 取得相機機型等中繼資料
   - 能力與限制：可讀取（thumbnail/metadata），但未找到可編輯 RAW 的 API
   - 專案整合：將 RAW 支援整合進 DigitalCameraFiler（記憶卡歸檔工具）
3. 技術依賴：
   - 最底層：Canon Digital Camera SDK（由 Microsoft 工具間接呼叫）
   - 中介：Microsoft RAW Image Thumbnailer and Viewer for Windows XP（提供 COM 介面與 DLL）
   - 封裝：RawManager.Interop.dll（Interop Assembly）
   - 上層：.NET Framework 與 C# 應用（DigitalCameraFiler.exe）
4. 應用場景：
   - 記憶卡歸檔工具需讀取 RAW 檔的相機型號、拍攝時間等 metadata 以自動歸檔/命名
   - Windows 桌面應用快速加入多廠牌 RAW 縮圖與中繼資料檢視能力
   - 不動 RAW 像素、只做資訊抽取與整理的工具鏈

### 學習路徑建議
1. 入門者路徑：
   - 了解 RAW/EXIF 與常見副檔名（CRW/CR2 等）
   - 安裝 Microsoft RAW Image Thumbnailer and Viewer for Windows XP
   - 在 C# 專案中參照 RawManager.Interop.dll，練習用 CRawViewerClass 載入 RAW、讀取 CameraModel/拍攝時間
2. 進階者路徑：
   - 熟悉 COM Interop、例外處理與資源釋放（STA/MTA 與 COM 生命週期）
   - 比較 EXIF vs. 廠商私有標籤（Canon MakerNote）取得更完整 metadata
   - 擴充支援多廠牌 RAW，並建立抽象層封裝第三方依賴
3. 實戰路徑：
   - 在歸檔工具中加入「檢測安裝依賴」「自動解析 RAW 中繼資料」「以時間與機型歸檔命名」
   - 打包部署（MSI），啟動前檢查並引導安裝 Microsoft Viewer
   - 加入縮圖預覽、批次處理、錯誤回報與記錄

### 關鍵要點清單
- 微軟 RAW Viewer 相依性：必須先安裝 Microsoft RAW Image Thumbnailer and Viewer for Windows XP 才能使用其 Interop 能力（優先級: 高）
- Interop 組件位置：安裝後在目錄中可找到 RawManager.Interop.dll 供 .NET 參照（優先級: 高）
- 主要類別使用：CRawViewerClass 可載入 RAW（Load）並讀取 CameraModel 等屬性（優先級: 高）
- C# 範例呼叫：raw.Load(path) 後直接讀取屬性（如 CameraModel），開發門檻低（優先級: 高）
- 能力範圍：目前重點在讀取/檢視（thumbnail/metadata），尚無可編輯 RAW 的 API（優先級: 高）
- 技術堆疊：底層仍倚賴 Canon Digital Camera SDK，但透過 Microsoft 工具間接使用（優先級: 中）
- 開源替代方案現況：早期多不成熟或不穩定，可靠度不如官方/微軟方案（優先級: 中）
- 歸檔需求聚焦：實務上多只需拍攝時間與基本機型資訊即可完成自動歸檔（優先級: 高）
- 旋轉處理觀念：RAW 本體通常不需旋轉，旋轉多為顯示層或 JPEG 導出處理（優先級: 中）
- 例外與相容性：需處理不同廠牌/機型 RAW 差異與未安裝相依組件的錯誤（優先級: 高）
- 部署考量：MSI 打包前後，應加入依賴檢測與導引安裝流程（優先級: 中）
- 平台限制：此方案著重 Windows XP 時代生態與 .NET Framework，相容性需評估（優先級: 中）
- 性能與批次：大批量讀取 RAW 需注意 I/O 與 Interop 呼叫成本（優先級: 中）
- 擴充性設計：以介面/抽象層包裝第三方 DLL，降低供應商鎖定風險（優先級: 中）
- 使用情境最佳化：以時間戳、機型規則自動命名與歸檔，提升工作流程效率（優先級: 高）