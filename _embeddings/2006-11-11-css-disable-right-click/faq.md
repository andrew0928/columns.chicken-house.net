# CSS 擋右鍵

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 要在網站的所有頁面上禁止滑鼠右鍵，有沒有不必在每一頁都插入 `<script>` 的做法？
使用 IE 專屬的 DHTML Behavior 技術即可做到。只要在共用的 CSS 中加入  
`body { behavior:url('context-menu-blocker.htc'); }`  
並在 `context-menu-blocker.htc` 檔攔截 `oncontextmenu` 事件並取消它，就能讓所有套用該 CSS 的頁面自動停用右鍵，完全不需要逐頁嵌入 JavaScript。

## Q: `.htc` 檔案在這個解決方案中負責什麼工作？
`.htc` 是行為描述檔 (HTML Component)。在範例裡它只做一件事──攔截 `oncontextmenu` 事件並呼叫 `return false` 取消該事件，藉此達到「擋右鍵」的效果。

## Q: DHTML Behavior 是什麼時候被引進的？之後還有改進嗎？
DHTML Behavior 從 IE5 開始出現，IE5.5 對 `.htc` 又做了一些改良；之後就幾乎沒有新的進展。作者也不確定 IE7 是否對 `.htc` 仍有改動或增強。

## Q: 如果網站已經使用 CSS，改用 behavior 來禁右鍵有什麼優勢？
因為 behavior 可以透過 CSS 一次佈署到指定標籤，當網站本來就以 CSS 管理樣式時，只需在共用樣式檔宣告一次，整站所有頁面就同步套用，不必手動修改每一個網頁，省時省力。

## Q: 為什麼作者對「擋右鍵」的網站感到反感？
作者認為並非所有使用者按右鍵都是要偷內容，被預設為「小偷」讓人不舒服；此外，真正想查看內容的人仍可透過工具（如 Fiddler）輕易取得，因此此做法既不友善也不見得有效。