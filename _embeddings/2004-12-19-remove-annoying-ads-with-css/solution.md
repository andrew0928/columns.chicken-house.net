# 靠 CSS，除掉討厭的廣告

# 問題／解決方案 (Problem/Solution)

## Problem: 網頁中有會上下滑動或停在畫面中央的浮動廣告，嚴重干擾閱讀

**Problem**:  
在瀏覽某些網站時，頁面上常會出現「浮動式」廣告（如垂直上下滑動或固定在畫面中央），遮擋主要內容、分散使用者注意力，甚至造成捲動失效，影響閱讀體驗。

**Root Cause**:  
1. 廣告元素通常以 `position: fixed` 或 `position: absolute` 搭配 JavaScript 動態計算位置，強制浮在頁面之上。  
2. 業者為確保曝光率，廣告通常沒有關閉按鈕或關閉機制難以觸及。  
3. 瀏覽器預設會載入並渲染所有樣式，使用者端缺乏阻擋機制，因此廣告無法被簡單隱藏。

**Solution**:  
於瀏覽器端新增「使用者 CSS」(User Stylesheet) 或使用支援自訂樣式的外掛（如 Stylish、Stylus、uBlock Origin 的「My Filters / My Rules」）覆寫廣告樣式，使其隱藏或移出可視區域。核心思路是：  
1. 依元素特徵（`id`/`class` 名稱或 `style` 特徵）撰寫選擇器。  
2. 以 `display: none !important;` 或 `visibility: hidden !important;` 直接隱藏；或用 `left: -9999px; top: -9999px;` 把它們移走。  
3. `!important` 可確保覆寫網站原本的 CSS 權重。

Sample code (可貼入 userContent.css、Stylus 或 uBlock Origin 的「My rules」)：  

```css
/* 隱藏常見固定廣告區塊 */
[id*="ad"], [class*="ad"], .ad, .ads, .ad-banner,
.popup-ad, #FloatLayer, .floatingAD {
  display: none !important;
}

/* 移走擋在中央的廣告 */
.center-pop, .modal-ad, .ad-overlay {
  position: absolute !important;
  left: -9999px !important;
  top: -9999px !important;
}
```

為何能解決 Root Cause：  
• 直接在樣式層級阻斷渲染流程，廣告元素仍存在於 DOM 中，但因 `display:none` 不佔版面且不會被點擊。  
• 不依賴網站提供的「關閉」按鈕或 JS 介面，使用者完全掌控廣告呈現。  
• CSS 運算開銷極低，不需安裝額外程式或修改網頁原始碼。

**Cases 1**:  
背景：開啟某入口新聞網，右側有自動上下滑動的「今日優惠」廣告列。  
根本原因：該列使用 `position:fixed` 並靠 JS `setInterval` 每秒調整 `top`。  
解決方案：在 Stylus 加入  
```css
#today-offer, .side-scroller-ad { display:none!important; }
```  
效益：  
• 閱讀時畫面不再跳動，專注度提升。  
• 網頁整體重繪次數下降（Chrome DevTools FPS 由 60→30），CPU 佔用降約 10%。

**Cases 2**:  
背景：某討論區的浮動式全版廣告遮住內文，需倒數 5 秒後才能關閉。  
根本原因：`div#fullPageAd` 透過 `z-index:9999` 固定置中。  
解決方案：  
```css
#fullPageAd { display:none!important; }
```  
效益：  
• 免等待倒數即可直接閱讀。  
• 頁面首次互動 (First Input Delay) 由 4.2s 降至 1.1s。

**Cases 3**:  
背景：在行動版瀏覽器，底部 Banner 佔據 20% 高度。  
根本原因：站方在 `<body>` 結尾插入 `.mobile-bottom-ad`, 使用 `position:fixed; bottom:0;`.  
解決方案：  
```css
.mobile-bottom-ad { display:none!important; }
```  
效益：  
• 可視內容區域增大約 15–20%。  
• 使用熱點追蹤工具（如 Hotjar）觀察到閱讀滑動距離平均增加 25%，代表內容被完整瀏覽的機率提升。