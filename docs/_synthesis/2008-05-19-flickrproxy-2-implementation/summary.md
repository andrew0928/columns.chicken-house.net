---
layout: synthesis
title: "FlickrProxy #2 - 實作"
synthesis_type: summary
source_post: /2008/05/19/flickrproxy-2-implementation/
redirect_from:
  - /2008/05/19/flickrproxy-2-implementation/summary/
postid: 2008-05-19-flickrproxy-2-implementation
---

# FlickrProxy #2 - 實作

## 摘要提示
- 目標與動機: 不改動 Blogger 既有流程與資料，讓圖片自動上傳與改由 Flickr 服務圖片
- 架構核心: 以 ASP.NET HttpHandler 截取圖片請求，判斷、上傳、快取、再 302 轉址到 Flickr
- 無侵入設計: 前端 HTML 與上傳流程不變，影響可還原，保障資料完整性
- 流程三步驟: 判斷是否代理、查快取、若無則上傳並建立快取後轉址
- IIS 設定重點: 將 .jpg 交由 ASP.NET 管理，再用 web.config 精準把目錄下的 jpg 指到自訂 Handler
- 快取策略: 以 ASP.NET Cache + 檔案快取儲存 Flickr URL，並以檔案相依性自動失效
- Flickr API 整合: 使用 FlickrNet，需 API Key/Security/Token 三組憑證才可上傳與取圖
- 可用尺寸檢測: 因 Flickr 各尺寸可能暫不可用，逐一以實際 HTTP 檢測 Medium/Large/Original
- 成果驗證: 以 Fiddler 觀察 302 轉址至 Flickr，並確認相片已出現在帳號中
- 效能與頻寬: 首次請求需上傳付出成本，其後以 302 導向 Flickr，顯著節省網站頻寬

## 全文重點
作者實作一個名為 FlickrProxy 的 ASP.NET HttpHandler，目標是在不改變 Blogger 任何操作習慣與網站既有 HTML/資料的前提下，讓站內圖片自動上傳到 Flickr 並改以 Flickr 提供的 URL 供前端瀏覽器取得，達成節省網站頻寬與消除手動搬運圖片的繁瑣流程。整體思路是以最小侵入、可逆的系統設計為核心：不改 HTML、不改原上傳機制，只在伺服器端攔截圖片請求並動態決策。

執行流程分為三步。第一步，接收 Http Request 時先判斷是否為需代理的圖片（如目錄與大小門檻等）。若不是，直接當靜態檔回傳。第二步，若要代理，先查快取（包含 ASP.NET 內建 Cache 與檔案型快取），若已有對應 Flickr 連結，立即以 302 轉址至 Flickr。第三步，若快取未命中，便計算檔案雜湊、建立快取檔，透過 FlickrNet 上傳圖片取得 photoID 與各尺寸 URL，檢測可用尺寸後寫入快取，再重走第二步完成轉址。此設計確保首次請求支付上傳成本，之後所有請求都走輕量的 302，極大減輕主站負載。

為讓 ASP.NET 有機會攔截 .jpg，需先在 IIS 把 .jpg 指給 aspnet_isapi.dll；為避免全站破圖，再於 web.config 先將 *.jpg 指回內建 StaticFileHandler，最後針對特定目錄（如 ~/storage）覆寫處理器為自訂的 FlickrProxyHttpHandler。此「全域交給 ASP.NET、預設還原靜態、目錄定向自訂」的三段式配置，兼顧穩定與精準導入。

代碼面，主 Handler 檢查快取目錄、取得或建立 cache info（含來源路徑、Flickr URL、photoID），並將 Flickr URL 放入 ASP.NET Cache（以檔案相依性控制失效），最後 Response.Redirect。BuildCacheInfoFile 核心是以 FlickrNet 串接 API，上傳取得 photoID，再 PhotosGetInfo 取得 Medium/Large/Original URL。由於 Flickr 在繁忙或特定條件下，某些尺寸 URL 可能暫不可用或拋出例外，作者採用「由中至大逐步測試可用 URL」策略：對每個候選 URL 實際發 HTTP 檢測可取回圖片者即為當前最優尺寸，並以最後成功者作為快取的最終 URL，提升穩定性。

測試上，簡單 HTML 嵌入本地 jpg。以 Fiddler 觀察，瀏覽器對 jpg 的請求會先收到 302，再自動前往 Flickr 取圖，頁面上顯示正常，並在 Flickr 帳號中看到上傳結果，驗證了「不改頁面、不改上傳流程、動態轉網外託管」的設計目標。效能上，首次請求雖需上傳成本，但後續僅 302 回應，節省大量頻寬。整個專案告一段落，未來將持續微調重構、整合既有代碼，有興趣可聯絡作者索取程式碼。

## 段落重點
### 目標與系統設計
作者希望 Blogger 完全不需理解或操作 Flickr，上傳與顯示流程都維持原狀；一切變更在伺服器端透明進行，且可隨時撤回不影響資料。核心方法是以 HttpHandler 攔截圖片請求，當符合條件即改由 Flickr 託管：若已有快取，引導瀏覽器 302 到 Flickr；若無，則自動上傳並建立快取後再轉址。此做法相對於修改 HTML 的方案更無侵入性，風險小、可回復。

### Handler 處理流程與 UML 概念
流程分三步：1) 接收請求與條件判斷（是否轉 Flickr）；2) 查 ASP.NET Cache 與檔案快取命中則直接 Redirect；3) 未命中則計算雜湊、建立快取檔、用 Flickr API 上傳取得 URL，寫回快取後再 Redirect。作者以時序圖呈現交互，顯示請求在站內與 Flickr 間的轉移與快取生效點。

### IIS 與 ASP.NET 設定關鍵
IIS 預設會直接回傳靜態圖檔，需先把 .jpg 指給 aspnet_isapi.dll 才能由 ASP.NET 介入。為避免全站圖片被攔截而破圖，web.config 中先將 *.jpg 綁定回 System.Web.StaticFileHandler 作為預設；再針對目錄（如 ~/storage）覆寫 *.jpg 使用自訂 FlickrProxyHttpHandler。此配置可「點狀導入」新行為、降低風險，且與 VS Dev Web 的行為不同，建議直接在 IIS 環境開發測試。

### 主處理器與快取實作
FlickrProxyHttpHandler 啟動時確保快取目錄存在；若快取檔不存在則呼叫 BuildCacheInfoFile 建立，存在則載入並從 ASP.NET Cache 取出 Flickr URL，若未命中則讀快取檔寫入 Cache（以 CacheDependency 綁定檔案）。最後以 Response.Redirect 導向 Flickr。雙層快取（檔案 + 記憶體）能兼顧跨程序與效能，並以檔案相依性自動同步。

### 與 FlickrNet 整合與授權流程
使用 FlickrNet 需具備三組憑證：API Key、Shared Secret、Auth Token。Key 與 Secret 於 Flickr 開發者頁面申請；Token 需透過使用者登入授權流程取得，作者直接使用 FlickrNet 範例程式走完授權獲得 Token。完成後即可上傳圖片取得 photoID，再以 PhotosGetInfo 取得各尺寸 URL。此段是本專案主要學習與整合成本所在。

### 針對尺寸可用性的穩健處理
Flickr 在繁忙或特定情況下，Medium/Large/Original 等尺寸 URL 可能暫時不可用或拋例外。作者無法掌握其規律，遂採取由中至大逐步嘗試並以實際 HTTP 檢測可用性的策略：一旦某尺寸不可用拋出例外即中止該路徑，保留上一個成功尺寸為最終 URL。此作法在不可靠的外部服務情境下提升整體穩定性與最終顯示品質。

### 測試與成效驗證
測試頁僅含一張本地圖片。以 Fiddler 觀察，對 jpg 的請求先收到 302，瀏覽器隨即前往 Flickr 下載並正常顯示；同時在 Flickr 帳號中可看到新上傳的相片。結果證實不需修改 HTML 與 Blogger 操作流程即可把圖片實際託管到 Flickr。頻寬層面，首次請求需上傳成本，但後續皆以 302 轉址，主站只付出極小回應代價，達到節流目標。

### 結語與後續計畫
專案已達到初版目標並在實站上成功運行。後續將以小幅調整、重構與整合既有程式為主。由於設定與環境差異（IIS 與開發伺服器）可能造成新手卡關，文中亦提供 MSDN 連結作為學習資源。有興趣閱讀或延伸此實作的人可聯絡作者取得程式碼。

## 資訊整理

### 知識架構圖
1. 前置知識： 
   - IIS 與 ASP.NET 基本架構與差異（Dev Web Server vs IIS）
   - ASP.NET HttpHandler 機制與 web.config 設定
   - HTTP 基礎（Request/Response、302 Redirect、Cache）
   - Flickr API 與 FlickrNet 使用、認證流程（API Key/Secret/Token）
   - 檔案存取與雜湊、快取依賴（CacheDependency）

2. 核心概念：
   - 透明代理圖片請求：以 HttpHandler 接管特定目錄/附檔名的圖片請求，不改動 HTML 與既有上傳流程
   - 快取策略：以 ASP.NET Cache + 檔案型 cache info（含 URL、photoID、hash）降低重複操作
   - Flickr 上傳與取回網址：用 FlickrNet 上傳圖片、查詢不同尺寸 URL，選擇可用的最大尺寸
   - 設定導向的覆蓋：IIS 將 *.jpg 交給 ASP.NET，web.config 再細分路徑設定與處理程序
   - 容錯與回退：針對 Flickr 圖片尺寸偶發不可用，以實際 HTTP 檢測逐步選擇可用 URL

3. 技術依賴：
   - IIS 映射 → ASP.NET ISAPI（aspnet_isapi.dll）→ web.config httpHandlers → 自訂 FlickrProxyHttpHandler
   - FlickrProxyHttpHandler → 檔案雜湊/快取檔 → FlickrNet SDK → Flickr API（需 API Key/Secret/Token）
   - ASP.NET Cache → CacheDependency（監看 cache info 檔變化）

4. 應用場景：
   - 部落格/網站圖片外移至 Flickr，節省主站頻寬與存取成本
   - 舊站不改 HTML 的前提下，逐步將媒體託管到外部服務
   - 對特定目錄的媒體請求做代理、審計或統一轉址
   - 作為簡易「類 CDN」的圖片轉送與快取方案

### 學習路徑建議
1. 入門者路徑：
   - 了解 HttpHandler 基本觀念，實作一個最小可行的同步 Handler
   - 在本機 IIS（非 Dev Web Server）部署簡單站台，測試 handler 生效
   - 以 web.config 配置 System.Web.StaticFileHandler，確認預設與覆寫行為差異

2. 進階者路徑：
   - 整合 FlickrNet，完成 API Key/Secret/Token 取得流程並測試上傳
   - 設計檔案型 cache info 與 ASP.NET Cache 搭配 CacheDependency
   - 實作圖片尺寸可用性檢測與錯誤處理（例外處理與回退策略）
   - 以雜湊鍵規劃快取命名，處理併發與重入

3. 實戰路徑：
   - 在 IIS 設定 *.jpg 指向 ASP.NET，並在 web.config 針對 ~/storage 覆寫 handler 指向 FlickrProxyHttpHandler
   - 完成 BuildCacheInfoFile：上傳、取回 photoID、查詢 URL、檢測可用性、寫入 cache info
   - 用 Fiddler/瀏覽器驗證 302 Redirect 至 Flickr，量測第一次與後續請求的行為差異
   - 逐步擴大覆蓋目錄或檔型，監控效能與錯誤日誌

### 關鍵要點清單
- 透明代理思維：不改 HTML 與使用流程，改由伺服端攔截圖片請求並轉向外部託管（優先級: 高）
- IIS 映射配置：將 *.jpg 導向 ASP.NET ISAPI，讓自訂 handler 有機會攔截（優先級: 高）
- 路徑級覆寫：以 web.config 的 location 對 ~/storage 指派自訂 handler，避免全站破圖（優先級: 高）
- 靜態檔回退：以 System.Web.StaticFileHandler 作為預設處理，確保非目標目錄影響最小化（優先級: 中）
- 快取策略設計：組合 ASP.NET Cache 與檔案型 cache info，減少重複上傳與查詢（優先級: 高）
- CacheDependency 應用：以 cache info 檔作為依賴，動態更新記憶體快取（優先級: 中）
- 雜湊鍵命名：使用檔案內容雜湊作為快取鍵與 cache 檔命名基礎，避免重複（優先級: 中）
- Flickr 認證三要素：API Key、Secret、Token 缺一不可，Token 需使用者授權流程取得（優先級: 高）
- FlickrNet 整合要點：UploadPicture 取得 photoID、PhotosGetInfo 取得各尺寸 URL（優先級: 高）
- 尺寸可用性檢測：對 Medium/Large/Original 逐一以 HTTP 測試，選最大可用尺寸（優先級: 中）
- 302 Redirect 機制：主站回應 302 導至 Flickr，後續流量改由 Flickr 承擔（優先級: 高）
- 初次成本與後續節流：首次請求會觸發上傳與建檔，後續以快取與 302 最小化負載（優先級: 中）
- 環境一致性：建議直接在 IIS 開發與測試，避免 Dev Web Server 與 IIS 行為差異（優先級: 高）
- 錯誤處理與容錯：對 Flickr 偶發「photo not available」實作例外處理與回退邏輯（優先級: 中）
- 可逆性與資料安全：不動原始檔與資料結構，隨時可停用 handler 回復原狀（優先級: 中）