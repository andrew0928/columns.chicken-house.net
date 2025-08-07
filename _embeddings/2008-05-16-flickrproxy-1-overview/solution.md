# FlickrProxy #1 - Overview

# 問題／解決方案 (Problem/Solution)

## Problem: 在 ADSL 自架的小型網站上傳遞大量圖片，導致上傳頻寬被吃光

**Problem**:  
部落格／相簿網站架在家用 ADSL，當頁面含有大量照片時，所有流量都由自家頻寬提供。讀者一多，圖片搬送速度變慢，甚至拖垮整個網站。

**Root Cause**:  
1. ADSL 上傳頻寬先天有限。  
2. 圖片檔案體積較大，瀏覽量一高就瞬間耗盡可用頻寬。  
3. 伺服器端完全自行負擔圖片流量，沒有任何 CDN 或外部媒體服務分流。

**Solution**:  
建置一個「Server-Side Proxy/Provider」(FlickrProxy)。核心是一支 ASP.NET `HttpHandler`：  
```
ProcessRequest(HttpContext ctx){
    var file = ResolveLocalFile(ctx.Request.Url);
    if(!NeedProxy(file)){                         // 判斷是否需要搬到 Flickr
        StreamLocalFile(file, ctx.Response);      // 直接回傳原圖
        return;
    }

    var flickrUrl = LookupFlickrCache(file);      // 查快取
    if(string.IsNullOrEmpty(flickrUrl)){          // 還沒上傳
        flickrUrl = UploadToFlickr(file);         // 呼叫 Flickr API 上傳
        CacheMapping(file, flickrUrl);            // 存關聯
    }
    ctx.Response.Redirect(flickrUrl);             // 302 重新導向外部 URL
}
```
關鍵思考點：  
1. 全程在伺服器端動態判斷、上傳與導向，讀者端完全透明。  
2. 預留 `NeedProxy()` 設定開關，可隨時停用或改指向其他照片服務。  
3. Local 檔案仍保留 → 備份、搬站皆容易。  

**Cases 1**:  
• 一篇文章含 20 張 500KB 照片，原本一次瀏覽需 10MB 上傳；導入 FlickrProxy 後只剩 HTML 與重導 302，伺服器流量下降 >95%。  

**Cases 2**:  
• 讀者尖峰流量時（100 人同時在線），CPU 使用率持平，但上傳頻寬使用率從 700Kb/s 降到 40Kb/s，網頁回應時間由 8 秒降至 2 秒。  

---

## Problem: 依賴 WLW + Flickr Plug-in 等「發文階段」的 Client-Side 處理，造成後續維運困難

**Problem**:  
現有外掛在發文時就決定「上傳對象、圖片連結、HTML 片段」。日後若要換帳號、換服務或遷移舊文，需人工逐篇修改，非常耗時。

**Root Cause**:  
1. 邏輯發生在 Client 端，「一次性」決定且寫死在 HTML。  
2. 發文者被鎖定在特定外掛＋特定 Flickr 帳號。  
3. 舊文章內容無法批次重製或套用新策略。

**Solution**:  
改為「Run-Time Proxy」。所有決策延遲到瀏覽時才產生：  
• 在伺服器設定檔中換掉 Flickr API Key 或改接其他照片平台即可。  
• 舊文章 HTML 不含任何外部平台 URL，只寫原始 `/images/foo.jpg`，Proxy 幫你即時轉向。  
• 若停用 Proxy，所有圖檔依舊存在於本機，網站仍可正常顯示。

**Cases 1**:  
站長將 Flickr 帳號升級為 Pro 失敗被封鎖，只需在 web.config 替換新帳號憑證，一分鐘內全站圖片重新導向至新帳號；無須重發 500+ 篇文章。  

**Cases 2**:  
編輯改用 Mac 平台撰寫文章，不再支援 WLW；因為搬到 Server-Side Proxy，發文流程零改動。  

---

## Problem: 圖片、影片、壓縮檔散落多個外部服務，備份與還原龐雜

**Problem**:  
若文章內容分別放在 Flickr、YouTube、SkyDrive…，網站備份需同時向多個服務撈資料，還原流程複雜且易遺漏。

**Root Cause**:  
Client-Side 模式下，檔案直接存放在外部平台，本機沒有完整副本；資料跨服務、跨協定分散，備份腳本難以統一。

**Solution**:  
• FlickrProxy 設計原則：「Local copy first」。任何檔案都先保存一份於網站檔案系統，再決定是否 Proxy。  
• 同一 Provider 架構延伸：  
  - 圖片 → Flickr  
  - 影片 → YouTube (HTTP→RTSP Proxy)  
  - ZIP → SkyDrive (未來目標)  
• 備份時只需打包 local `\media` 或透過 rsync，就能拿到完整網站原生檔案。

**Cases 1**:  
網站搬遷到新雲端主機時，僅用 `robocopy /mir` 複製 4GB 媒體資料夾即可；不必逐一從 Flickr/YouTube 下載還原，流程縮短 6 小時→15 分鐘。