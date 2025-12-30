---
layout: synthesis
title: "FlickrProxy #3 - 終於搞定大圖網址錯誤的問題"
synthesis_type: summary
source_post: /2008/05/21/flickrproxy-3-finally-fixed-large-image-url-error-issue/
redirect_from:
  - /2008/05/21/flickrproxy-3-finally-fixed-large-image-url-error-issue/summary/
---

# FlickrProxy #3 - 終於搞定大圖網址錯誤的問題

## 摘要提示
- Flickr API 回傳疑慮: 使用 PhotosGetInfo 取得的 LargeUrl 有時會錯，導致大圖無法顯示
- 問題觸發場景: 照片上傳成功後，讀取 Medium/Large/Original Url 時偶發錯誤
- 網址生成機制: PhotosGetInfo 只回傳一堆 ID，SDK 依公開規則「湊」出各尺寸網址
- Flickr 規則變動: 部分情況不會另存 Large 圖，直接指向原圖，導致既有網址規則失效
- 失效條件: 當上傳圖不夠大，Large 尺寸會被省略，原圖網址規則又和一般尺寸不同
- 正確解法: 改用 PhotosGetSizes，向 Flickr 查詢實際可用尺寸與對應網址
- 穩定性提升: 改用 Sizes 後，不再出現 photo not available 的掛圖問題
- 程式碼調整: 從直接取 PhotoInfo.Medium/Large/OriginalUrl，改為迭代 SizeCollection
- 維護策略: 以服務端回傳為準，避免本地推測網址格式，降低對規則變動的脆弱性
- 經驗教訓: 不能只憑 API 名稱猜用途，應詳讀文件與變更歷史

## 全文重點
作者在開發 FlickrProxy 時，遇到一個棘手的問題：照片上傳到 Flickr 後，透過 PhotosGetInfo 取得的 MediumUrl 或 LargeUrl 有時會失效，導致頁面出現「photo not available」。起初作者以為是 API 或程式處理的偶發錯誤，但與 Flickr 網站實際顯示的圖片連結對比後，發現 API 得到的網址有時與網站不同，顯示出問題並非單純的網路或暫時性狀況。

深入追查和查閱論壇後，作者理解到關鍵差異：PhotosGetInfo 並非直接傳回各尺寸圖片的最終網址，而是基於一組 ID 與既定的網址規則在客端或 SDK 中「拼湊」出來。過去 Flickr 曾調整過部分圖片的網址格式，尤其當照片尺寸不大時，系統會判定不需額外產生 Large 版本，而是直接提供原圖（original）。原圖的網址規則與一般尺寸不同，導致在「推測網址」的邏輯下，大圖連結會在某些照片上失效。

找到根因後，作者改採用 PhotosGetSizes API。這支 API 會直接回傳該 photoId 實際存在的所有尺寸選項，包含尺寸標籤、實際網址、寬高等詳細資訊。改以此為依據，從 SizeCollection 中逐一讀取並保存來源資訊，就能保證所使用的連結一定存在且可用，不再需要額外的「確認網址是否可用」的防呆流程。最終，FlickrProxy 的穩定性大幅提升，避免了大圖隨機掛掉的問題。

作者也反思這次教訓：不能只靠 API 名稱猜用途或沿用舊規則，應詳讀文件與變更記錄，特別是當服務端可能動態調整資源產出（如不同尺寸是否生成）時，應以「查詢實際可用資源」的 API 作為真實來源，而不是本地推導網址。程式碼層面也從直接取 PhotoInfo 的 Medium/Large/OriginalUrl，改為以 PhotosGetSizes 回傳的尺寸陣列為唯一依據，並將各尺寸的屬性完整寫入快取，確保後續顯示與選擇邏輯一致可靠。至此，FlickrProxy 進入實用階段，問題順利收束。

## 段落重點
### 問題背景：上傳後取得的圖片網址偶發失效
作者在使用 Flickr API 開發 FlickrProxy 時，發現上傳照片雖可取得 photoId，但透過 PhotosGetInfo 取得的 MediumUrl 或 LargeUrl 偶爾會無法顯示，出現「photo not available」。雖然直覺以為 API 應該可靠，但實際比對 Flickr 網站上的連結後，確定有時 API 取回的網址與網站不同，顯示並非單純網路不穩或快取問題。

### 問題根因：以規則「湊」網址 + Flickr 尺寸生成策略
追查與查閱論壇得知，PhotosGetInfo 本質只提供一組 ID，SDK 再依公開規則組出各尺寸網址。然而 Flickr 曾調整過網址規則，並在小尺寸照片時不生成 Large 圖，直接使用原圖。因原圖的網址格式與一般尺寸不同，導致用既有規則推測出的 LargeUrl 會失效。這是一個由服務端策略變動搭配客端推測邏輯所引發的結構性問題。

### 解法：改用 PhotosGetSizes 查實際可用尺寸與網址
為避免推測錯誤，改以 PhotosGetSizes API 向 Flickr 查詢該照片實際可用的尺寸清單，包含標籤、來源網址、頁面網址與寬高等屬性。以此結果為唯一真實來源來決定顯示哪個尺寸，徹底避免了「尺寸不存在但網址被組出來」的矛盾情況，從根本上解決掛圖問題。

### 程式碼調整：由 PhotoInfo.URL 屬性改為迭代 SizeCollection
原本程式碼直接存取 PhotoInfo 的 MediumUrl、LargeUrl、OriginalUrl，並加上自訂的 CheckFlickrUrlAvailability 來補救。修改後，改為遍歷 flickr.PhotosGetSizes(photoID).SizeCollection，逐一取得 Size 的 Label、Source、Url、Width、Height，並寫入快取 XML。這讓前端渲染能據實選擇可用尺寸，不再需要事後檢查網址有效性。

### 成果與經驗：穩定性提升與對文件的敬畏
完成改造後，FlickrProxy 不再出現大圖隨機失效，穩定性顯著提升。作者反思，不能怪 API，不看文件、憑名稱猜用法才是主因。面對會隨策略變動的外部服務，應優先使用能「查詢實際狀態」的 API，而非在客端推導；同時將關鍵資訊（如各尺寸實際存在與屬性）納入快取與流程設計，降低未來規則變更的風險。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 基本 REST/API 認知與閱讀 API 文件能力
   - Flickr 開發者平台與認證（API Key）
   - .NET/C# 基礎（物件、例外處理）
   - XML/JSON 資料讀寫與模型對應（如 PhotoInfo、Size）
2. 核心概念：
   - PhotoInfo 與 PhotosGetInfo：取得照片基本資訊，但部分 URL 為以規則湊出來
   - 尺寸衍生規則：Flickr 會視原檔大小決定是否產生 Large 等衍生圖
   - 原圖（Original）網址格式與其他尺寸不同
   - PhotosGetSizes：以權威資料來源查詢可用尺寸與對應 URL，避免猜測
   - 錯誤來源與解法：LargeUrl 有時錯誤 → 改用 PhotosGetSizes 的 SizeCollection
3. 技術依賴：
   - Flickr API/FlickrNet SDK（或等效封裝）
   - PhotosGetInfo 依賴本地組合 URL 規則；PhotosGetSizes 依賴 Flickr 伺服端回傳實際可用尺寸
   - XML 處理（建立節點、屬性、快取）
   - 例外處理與連線穩定性
4. 應用場景：
   - 建置圖片代理/相簿服務（如 FlickrProxy），需穩定取得可用圖片 URL
   - 頁面展示多尺寸圖片（縮圖、中圖、大圖、原圖）
   - 降低「圖片無法顯示」風險並簡化可用性檢查邏輯
   - 快取尺寸清單以提升效能與減少 API 呼叫

### 學習路徑建議
1. 入門者路徑：
   - 申請 Flickr API Key，安裝並初始化 Flickr SDK
   - 以 photoId 呼叫 PhotosGetInfo，理解回傳欄位與常見尺寸命名
   - 實作基本圖片顯示頁，觀察不同照片的 LargeUrl 是否可用
2. 進階者路徑：
   - 研究 Flickr 尺寸生成策略與原圖網址差異
   - 改用 PhotosGetSizes，解析 SizeCollection，建立按優先序選圖策略
   - 將尺寸資訊序列化/快取（XML/JSON），設計有效期限與更新策略
3. 實戰路徑：
   - 在服務端封裝一個取得最佳可用尺寸 URL 的模組（含 fallback）
   - 移除對 URL 可用性的多次探測，改以 PhotosGetSizes 為單一真實來源
   - 監控 API 回應與錯誤，記錄不可用尺寸案例，建立告警與日誌

### 關鍵要點清單
- PhotosGetInfo 的限制: 該方法多以 ID 與規則組合 URL，非總是權威來源，可能出錯（優先級: 高）
- LargeUrl 常見問題: 當 Flickr 未產生 Large 圖時，LargeUrl 會失效或不一致（優先級: 高）
- 原圖網址差異: Original 的 URL 格式與其他尺寸不同，不能用同一規則推導（優先級: 高）
- 使用 PhotosGetSizes: 直接查詢所有可用尺寸與其實際 URL，避免猜測（優先級: 高）
- 尺寸選擇策略: 依需求從 SizeCollection 中選擇最佳尺寸並設計 fallback（如優先 large→medium→original）（優先級: 高）
- 簡化可用性檢查: 有了 PhotosGetSizes，即可移除逐一「探測 URL 是否可用」的額外開銷（優先級: 中）
- 例外處理最佳化: 將 try-catch 從多次網路探測轉為針對 API 呼叫與資料解析（優先級: 中）
- 快取尺寸清單: 將 SizeCollection（含 label、source、url、width、height）快取以減少 API 次數（優先級: 中）
- API 變更風險意識: Flickr 可能調整網址規則或尺寸政策，避免硬編碼規則（優先級: 中）
- 以文件為準: 不憑名稱猜用法，閱讀官方說明與社群討論可節省大量除錯時間（優先級: 高）
- 測試覆蓋: 以不同大小、是否產生衍生圖的照片建立測試案例（優先級: 中）
- 模組化封裝: 抽象出「依需求取得可用圖片 URL」的服務，隱藏 API 細節（優先級: 中）
- 日誌與監控: 針對不可用尺寸與 API 錯誤記錄 log，便於追蹤回歸與平台變動（優先級: 低）
- 效能考量: 減少不必要的 HTTP 探測與重試，優化頁面載入（優先級: 低）
- 相容性策略: 當 PhotosGetSizes 失敗時的備援（重試、退回特定尺寸或暫時隱藏圖）（優先級: 低）