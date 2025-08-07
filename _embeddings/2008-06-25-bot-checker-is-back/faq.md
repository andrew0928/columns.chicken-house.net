# Bot Checker 回來了!

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼在 Community Server 上很容易就能放進去的 Bot Checker，到了 BlogEngine.NET 卻拖到現在才完成?
原因在於 BlogEngine.NET 在張貼回應時大量使用 AJAX。為了把 Bot Checker 的程式碼插進這段流程，必須一路追 AJAX 呼叫與前後端互動，導致修改時間大增。

## Q: 目前這個 Bot Checker 能完全防堵 Bot 嗎?
不能。在攤開 HTML 原始碼後，Bot 仍然有機會直接取得題目與答案。不過作者認為自己的網站與 Bot Checker 知名度都不高，暫時不擔心會有人特地寫 Bot 來攻擊。

## Q: AJAX 在 Community Server 和 BlogEngine.NET 之間有什麼「諷刺」的差異?
雖然 AJAX 應用最廣的是 Community Server，但在 BlogEngine.NET 大部分功能反而走傳統 PostBack，唯獨「回應區」使用 AJAX，導致 Bot Checker 整合變得麻煩。

## Q: BlogEngine.NET 本身是否已內建 CAPTCHA 機制?
是的，作者在閱讀原始碼時發現 BlogEngine.NET 內部確實有 CAPTCHA 元件，但目前還找不到官方或明確的開啟方式，有興趣的人可以自行研究。

## Q: 因為 AJAX 限制，作者對留言表單做了哪些權宜處理?
為避開 AJAX 帶來的前後端同步問題，Bot Checker 的題目在產生後就被直接填到「評論」欄位。使用者若不想在留言中附帶「芭樂雞萬歲」等題目內容，可自行刪除再送出。