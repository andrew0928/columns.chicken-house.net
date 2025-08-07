# 搭配 CodeFormatter，網站須要配合的設定

## 摘要提示
- CodeFormatter外掛：作者釋出新版本並提供下載，能讓 Live Writer 產生乾淨的程式碼區塊。
- CSS整合：要讓程式碼高亮呈現，必須將官方提供的樣式表貼入部落格的自訂 CSS。
- 乾淨 HTML：CodeFormatter 主要把所有格式抽離到 CSS，保持文章 HTML 精簡可讀。
- Community Server設定：在 CS 後台的 Custom Styles(Advanced) 加上樣式即可立即生效。
- Copy Code功能：透過 JavaScript 將程式碼送進剪貼簿，方便讀者一鍵複製。
- SCRIPT阻擋問題：Community Server 會過濾 `<script>`，需用替代方案嵌入腳本。
- HTC技術：作者選用 IE 專屬的 HTC (HTML Component) 來統一管理事件並繞過 SCRIPT 過濾。
- 額外CSS：為讓 HTC 生效，需在樣式表再加一行 `behavior:url('/themes/code.htc')`。
- 預覽機制：為避免 IE 安全警告，改用 HTA 應用程式實作外掛預覽畫面。
- 下載與授權：外掛可自由使用與散佈，但請註明出處；下載連結放在文末。

## 全文重點
作者釋出更新版的 CodeFormatter Live Writer 外掛，並說明部署到部落格伺服器時必須做的兩項設定：CSS 及 Copy Code 功能。首先，外掛輸出的程式碼區塊完全依賴 CSS 來呈現語法高亮與字型配置，因此站長必須將官方提供的 `.csharpcode` 全套樣式貼到部落格的自訂樣式區， Community Server 使用者只需在 Dashboard → Custom Styles 即可完成。接著若要啟用「Copy Code」按鈕，一鍵複製程式碼到剪貼簿，還需再加入一段定義 `.copycode` 的 CSS，並把對應的 `code.htc` 檔案放到 `/themes/` 目錄。HTC 為 IE 專屬機制，可把原本會被 CS 過濾的 `<script>` 行為包進外部元件，成功繞過限制，同時提供 onclick 事件以呼叫剪貼簿 API。設定完成後，讀者在文章右上角即可見到 [copy code] 按鈕，點擊即複製純文字程式碼，不受 HTML 樣式干擾。外掛預覽畫面則改為 HTA 執行檔，以避免直接開啟 HTML 觸發的安全警告，並在預覽中致謝原始 CodeFormatter 作者與作者本人網站。全文最後附上外掛下載連結與散佈授權說明，鼓勵有需要的使用者取用並回報 Bug。

## 段落重點
### 前言
作者宣布 CodeFormatter Live Writer Add-Ins 已進行小幅改版並開放下載，強調外掛雖已具備良好功能，但若要在個人或團隊部落格上正常運行，仍需對伺服器環境做些微調整。本文即針對常見的 Community Server 部署示範，歸納出兩大必做步驟，讓讀者可快速體驗高亮程式碼與複製功能。

### 1. CSS
CodeFormatter 產生的 HTML 幾乎零內嵌樣式，核心設計在於把所有格式資訊抽離到外部 CSS，如字型、顏色、行號等。作者提供了官方範例樣式，包括 `.kwrd`、`.str`、`.rem` 等語法元素對應的顏色設定，並示範在 Community Server 的 Dashboard → Custom Styles(Advanced) 貼入即可生效。此步驟完成後，文章中的 `<pre class="csharpcode">` 區塊即可正確呈現 C# 高亮、行號與背景色，同時保持 HTML 乾淨、利於後續維護或跨平台搬遷。

### 2. COPY CODE
若想在程式碼區塊右上角顯示 [copy code] 按鈕並支援一鍵複製，需額外配置 JavaScript 行為。然而 Community Server 安全機制會自動剔除 `<script>` 標籤，使得傳統內嵌腳本不可行。作者因此改採 IE 專屬的 HTC 技術將事件與腳本封裝於外部檔 `code.htc`，透過 CSS `behavior:url('/themes/code.htc')` 連結。站長只要：
1. 在 CSS 再加上 `.copycode {cursor:hand; color:#c0c0ff; display:none; behavior:url('/themes/code.htc');}`
2. 將 `code.htc` 上傳至 `/themes/`
即完成設定。此後 Live Writer 只要在插入程式碼時勾選「包含原始程式碼」，外掛便自動輸出對應 HTML，前端就能在 IE/Edge 等支援 ActiveX 環境中使用 ClipboardData 複製功能。作者亦提到為改善外掛預覽安全警告，已將原本直接用 IE 開啟 HTML 的方式改成啟動 HTA 應用，並在介面加上對 CodeFormatter 原作者與自身網站的致謝連結。最後提醒使用者可自由散佈外掛，但請保留來源資訊，並附上最新版下載位址。