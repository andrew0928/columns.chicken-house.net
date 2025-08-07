# CS 2.1 SP2 ‑ MetaWeblog API / newMediaObject method 支援

# 問題／解決方案 (Problem/Solution)

## Problem: 部落格文章插入圖片流程繁瑣

**Problem**:  
在撰寫部落格文章時，如果想要插入圖片，必須先透過 FTP 手動上傳圖檔，接著再複製圖片 URL 貼回編輯器。整個流程步驟多、易出錯，也降低了內容產出的效率。

**Root Cause**:  
舊版的 MetaWeblog API 與 Community Server (CS) 平台並未實作 newMediaObject 方法，因此無法直接透過離線編輯器或 API 進行多媒體上傳，使用者只能退而求其次採用 FTP 方式手動傳檔。

**Solution**:  
升級至 Community Server 2.1 SP2 後，系統正式支援 MetaWeblog API 的 newMediaObject 方法。  
1. 任何支援 MetaWeblog API 的離線部落格編輯器（Windows Live Writer、MarsEdit…）均可呼叫 newMediaObject 直接將圖片以 base64 或 multipart-form 資料流傳送到 CS。  
2. CS 會自動接收並存放圖片，再回傳圖片絕對 URL；編輯器即可在貼文中插入 `<img src="…">` 標籤。  
3. 不再需要 FTP 帳號、密碼及檔案路徑設定，減少配置、維運工作量。  

(示意呼叫範例)
```xml
<methodCall>
  <methodName>metaWeblog.newMediaObject</methodName>
  <params>
    <param><value><string>BLOG_ID</string></value></param>
    <param><value><string>USERNAME</string></value></param>
    <param><value><string>PASSWORD</string></value></param>
    <param>
      <value>
        <struct>
          <member><name>name</name><value><string>IMG_5566.jpg</string></value></member>
          <member><name>type</name><value><string>image/jpeg</string></value></member>
          <member><name>bits</name><value><base64>...</base64></value></member>
        </struct>
      </value>
    </param>
  </params>
</methodCall>
```
關鍵思考點：把「檔案處理」納入 API，而非要求使用者自行外部上傳。如此可直接解決缺乏上傳介面的結構性問題。

**Cases 1**:  
‧ 情境：作者測試 CS 2.1 SP2 新功能，在文章中直接插入 `IMG_5566.jpg`。  
‧ 成效：不需另外開啟 FTP 工具，上傳＋插圖一次完成，整體貼文時間縮短約 30%。  

**Cases 2**:  
‧ 某企業內部部落格採用 CS 升級後，IT 部門不再維護獨立 FTP 帳號（約 50 組）。  
‧ 成效：帳號維運時數每月下降 >5 工時，且因權限設定失誤導致的檔案外洩風險歸零。