---
layout: synthesis
title: "如何透過命令列, 從手機搬檔案到電腦?"
synthesis_type: summary
source_post: /2007/03/13/how-to-transfer-files-from-phone-via-command-line/
redirect_from:
  - /2007/03/13/how-to-transfer-files-from-phone-via-command-line/summary/
---

# 如何透過命令列, 從手機搬檔案到電腦?

## 摘要提示
- 自動化需求: 需要可寫入批次檔的命令列流程，並與 DigitalCameraFiler 自動歸檔相片整合。
- ActiveSync 限制: 檔案總管的「瀏覽裝置」是 shell extension，不能直接用路徑搭配 xcopy。
- 解法方向: 先找命令列工具把手機檔案拉出來，再交由 DigitalCameraFiler 處理。
- 方案一 rcmd: 以 RAPI 為基礎的 rcmd.exe 可從 PC 端複製/刪除手機檔案，實測可行。
- 方案二 .NET: MSDN 文章示範如何用 .NET 撰寫類似工具，走開發客製化路線。
- 批次流程設計: 建暫存資料夾→從手機拷貝相片→刪手機檔→交給 DCF 歸檔→清理暫存與環境變數。
- 微軟未提供 .NET 封裝: 官方未出 RAPI 的 .NET 類別庫。
- OpenNETCF wrapper: 社群已提供完整 RAPI .NET 封裝，被 MSDN 範例採用。
- 裝置控制能力: 除檔案操作外，還能取裝置資訊、讀寫 registry、遠端啟動程式等。
- 後續規劃: 打算基於 OpenNETCF 撰寫自用工具以擴充自動化能力。

## 全文重點
作者想把手機上的相片自動搬到電腦，並交由 DigitalCameraFiler 進行歸檔，要求能全程自動化與批次化。直覺以為可直接用 ActiveSync 掛載後的路徑配合 xcopy，但實測發現 ActiveSync 的「瀏覽裝置」其實是 shell extension，並非真實檔案系統路徑，無法被一般命令列工具直接存取。於是改採「先透過命令列將檔案拉到本機暫存，再交由 DigitalCameraFiler 處理」的兩段式流程。

搜尋後找到兩條路：其一是使用 CodeProject 上的 rcmd.exe（基於 Microsoft RAPI）可直接在命令列對手機執行檔案操作；其二是依 MSDN 文章以 .NET 自行開發類似工具。作者先試 rcmd，證實可行，便設計批次檔：先以亂數建立暫存資料夾，利用 rcmd 將手機相片拷貝到暫存，再刪除手機端相片，接著呼叫 DigitalCameraFiler 進行歸檔，最後清理暫存與環境變數，達成一鍵自動化。

延伸閱讀中作者注意到，雖然 RAPI 是微軟提供，但官方並未推出 .NET 封裝；反而是 OpenNETCF 社群已完成成熟的 RAPI .NET wrapper，功能涵蓋檔案操作、裝置資訊擷取、registry 操作與遠端啟動程式等，甚至被 MSDN 示範採用。基於此，作者計畫下次改以 OpenNETCF 開發自用工具，以取得更彈性與更完整的裝置端自動化能力。

## 段落重點
### 背景與需求
作者希望從手機將相片自動搬到電腦，並整合 DigitalCameraFiler 做相片歸檔。核心要求是流程必須能以批次檔自動化，免手動操作。一般人可能會用 ActiveSync 連線後在檔案總管拖拉，但這無法滿足自動化與批次需求，因此需要找能在命令列環境下操作手機檔案的解法，才能與既有的相片歸檔工具串接。

### 既有方法的限制
原本想直接擷取檔案總管中顯示的手機路徑，搭配 xcopy 或類似工具，但發現 ActiveSync 的「瀏覽裝置」其實只是 shell extension，讓使用者看起來像是本機路徑，實際上不是一般可被命令列工具識別的檔案系統。這使得直接在批次檔裡面用路徑拷貝的作法不可行。要不改寫 DigitalCameraFiler 讓它直接讀手機裝置，要不就必須找一個能透過 ActiveSync/ RAPI 和手機互動的命令列工具作為中介。

### 解法搜尋與兩種方案
作者評估兩條路：一是採用現成工具 rcmd.exe（出自 CodeProject，透過 Microsoft RAPI 與手機端溝通），能在命令列執行 copy、del 等動作，快速滿足需求；二是參考 MSDN 文章，以 .NET 寫出自家的命令列工具，等同複製 rcmd 的能力但可客製化。考量時程，先試現成的 rcmd，結果運作正常，證明 RAPI 途徑可行。後續若需進一步最佳化或整合，則再考慮自行開發。

### 批次檔自動化流程
實作上，批次檔的流程為：先以亂數建立一個暫存資料夾；使用 rcmd 將手機上的相片（如儲存在「Storage Card/My Documents/My Pictures」）複製到該暫存資料夾；為避免重複處理，再用 rcmd 刪除手機端已拷貝的相片；接著呼叫 DigitalCameraFiler，將暫存資料夾中的相片依規則歸檔到目標路徑；最後刪除暫存資料夾並清理環境變數。此流程把「手機到本機」與「相片歸檔」兩個階段解耦，兼顧可靠性與自動化。

### RAPI 與 .NET 封裝現況
作者在閱讀 MSDN 文章時注意到一個現況：雖然 RAPI 是微軟用於 PC 與行動裝置溝通的官方 API，但微軟並未提供 RAPI 的 .NET 版類別庫。這意味著若走 .NET 自行開發，需要自己包 P/Invoke 或尋找第三方封裝。這也解釋了為何 MSDN 的示範會引用社群的封裝方案來完成教學，對開發者而言，直接利用成熟封裝能大幅縮短開發時程。

### OpenNETCF 能力與後續規劃
OpenNETCF 社群已提供完善的 RAPI .NET wrapper，功能不僅包含檔案操作，還能取得裝置詳細資訊、存取 registry、甚至遠端啟動手機端程式，擴展出更多自動化可能。由於此封裝已在 MSDN 範例中被採用，可信度與穩定性具一定背書。作者因此計畫下次以 OpenNETCF 進行開發，打造更客製的命令列工具或整合流程，讓手機檔案處理與裝置管理更全面自動化。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 基本 Windows 命令列與批次檔撰寫（環境變數、md/rd/xcopy/copy 等）
   - ActiveSync/Windows Mobile 連線概念與裝置儲存路徑（例如 "\Storage Card\My Documents\My Pictures\"）
   - RAPI（Remote API）在 PC 與行動裝置間的遠端操作原理
   - 了解目標應用（如 DigitalCameraFiler）的輸入/輸出需求

2. 核心概念：
   - ActiveSync 的 Shell Extension 限制：檔案總管可瀏覽但非真實檔案系統路徑，無法直接用 xcopy 等命令列工具
   - RAPI：透過 ActiveSync 提供的遠端 API 對裝置進行檔案/系統操作
   - 命令列工具 rcmd.exe：以 RAPI 為基礎，提供 copy/del 等指令實作自動化
   - 自動化流程設計：以暫存目錄中繼、批次腳本串接搬檔與歸檔（DigitalCameraFiler）
   - .NET 開發替代方案：使用 OpenNETCF 的 RAPI wrapper 自行擴充工具

3. 技術依賴：
   - Windows PC + ActiveSync 連線中的 Windows Mobile/CE 裝置
   - RAPI 是底層能力；rcmd.exe 或 OpenNETCF RAPI wrapper 是其上層工具/封裝
   - DigitalCameraFiler 作為後續檔案歸檔工具；批次檔串接 rcmd.exe 與 DigitalCameraFiler
   - 若自製工具：.NET Framework + OpenNETCF Library 依賴

4. 應用場景：
   - 自動從手機相簿批次匯入照片到電腦並歸檔
   - 定期同步/清空裝置指定目錄（如釋放拍照空間）
   - 取得裝置資訊、操作 registry、遠端啟動裝置程式（擴充維運腳本）
   - 將命令列流程整合到更大批次/排程任務中

### 學習路徑建議
1. 入門者路徑：
   - 瞭解 ActiveSync 與裝置路徑命名
   - 下載並測試 rcmd.exe 的基本指令（copy、del、dir）
   - 編寫簡單批次檔：建立暫存資料夾、copy -> 後處理 -> 清理

2. 進階者路徑：
   - 強化批次檔健壯性：錯誤處理、重試、日誌紀錄、隨機/時間戳暫存路徑
   - 延伸 rcmd.exe 使用情境：檔案過濾、子資料夾處理、雙向同步策略
   - 研究 RAPI 能力邊界與安全性考量

3. 實戰路徑：
   - 使用 OpenNETCF RAPI wrapper 以 .NET 實作自訂 CLI 工具（加入進度回報、比對、跳過重複）
   - 與 DigitalCameraFiler 或其他媒體管理工具完整串接（參數化、回傳碼處理）
   - 佈署為排程任務（Windows Task Scheduler），監控與告警整合

### 關鍵要點清單
- ActiveSync Shell Extension 限制: 檔案總管可見但非真實路徑，無法直接用 xcopy/robocopy (優先級: 高)
- RAPI（Remote API）: 透過 ActiveSync 對裝置檔案/系統進行遠端操作的核心技術 (優先級: 高)
- rcmd.exe 工具: 基於 RAPI 的命令列工具，支援 copy、del 等常用操作 (優先級: 高)
- 批次檔自動化流程: 以暫存資料夾中繼，串接搬檔、歸檔、清理的全流程 (優先級: 高)
- 路徑與萬用字元: 正確指定裝置端路徑與 *.jpg 等過濾條件 (優先級: 高)
- 暫存資料夾策略: 使用亂數或時間戳避免衝突，處理清理與例外 (優先級: 中)
- 與 DigitalCameraFiler 串接: 明確傳遞來源/目的參數，確保後處理順利 (優先級: 高)
- 例外與錯誤處理: 連線中斷、檔案鎖定、空目錄、權限問題的防護 (優先級: 高)
- OpenNETCF RAPI Wrapper: .NET 環境下快速存取 RAPI 的開源封裝 (優先級: 中)
- 自訂 CLI 開發: 若需擴充功能或更佳控制，使用 .NET + OpenNETCF 自製工具 (優先級: 中)
- 裝置資訊與 Registry 操作: 進階維運可讀取系統資訊、編修登錄檔 (優先級: 低)
- 遠端啟動程式: 透過 RAPI 觸發裝置端應用以配合流程 (優先級: 低)
- 安全性與授權: 確認裝置信任、ActiveSync 設定與工具來源的安全 (優先級: 中)
- 排程與監控: 以排程器自動化與日誌/告警確保長期穩定 (優先級: 中)
- 相片搬移後清理: 自動刪除裝置端已匯出檔案以釋放空間 (優先級: 中)