# IE6 縮放網頁: using css + htc

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 如何在 IE6 中達成「所有網頁都能縮放」而不必安裝 IE7／Firefox？
利用 IE 的「使用者自訂 CSS」功能，配合 CSS 的 behavior 屬性呼叫本機的 HTML Component (HTC)，就能把自製的 zoom 行為套用到任意網頁，達到縮放效果。

## Q: HTC 是什麼？為何適合拿來做這件事？
HTC（HTML Component）自 IE5 起提供，允許開發者把 JavaScript 與樣式封裝成一個 client-side 元件並以 behavior 掛在任意 HTML 標籤上；再藉由 CSS 直接散佈到整站，無須修改每一頁 HTML，是實作全站縮放的關鍵。

## Q: 要把縮放功能裝到自己的 IE6，實際步驟是什麼？
1. 先下載並放好三個檔案：C:\zoom.htc、C:\zoom.css、C:\zoom.html  
2. 在 IE → 工具 → 網際網路選項 → 存取設定 → 樣式表，指定 C:\zoom.css  
3. 開啟 C:\zoom.html（或任何網頁）  
4. 在頁面上按住 Alt 並點一下滑鼠左鍵，選擇百分比即可改變整頁縮放比例。

## Q: 為什麼到 Google 首頁就失效，沒有跳出縮放選單？
因為本機的 C:\zoom.htc 屬於「本機電腦區域」(Local Zone)，而 www.google.com.tw 在「網際網路區域」，且兩者網域不同；IE 的安全機制會阻擋跨區域、跨網域的呼叫 (cross-talk)，導致 HTC 無法載入，縮放便失效。

## Q: 有沒有簡單的方法繞過這個安全限制？
作者目前還沒找到一個「既安全又簡便」的作法；若有更好的點子，歡迎提供。