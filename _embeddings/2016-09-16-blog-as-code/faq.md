# Blogging as code !!

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼作者決定丟掉傳統部落格系統、改用純靜態網站？
作者想省去維護整套系統的麻煩、降低主機運算資源消耗，也因此決定走「最低科技」路線：把文章都變成純靜態檔案，放到 GitHub Pages 上，以達到「省事、省錢、又環保」的目的。

## Q: 什麼是「Blogging as code」？
把部落格當成程式碼來管理：文章、版型與組態都寫在文字檔，放進 Git version control，用程式碼編輯器維護，再交給靜態網站產生器（GitHub Pages 內建的 Jekyll）自動編譯成網頁。

## Q: 作者最終選擇的核心工具組合是什麼？
1. GitHub Pages（Jekyll）負責產生與託管靜態網站  
2. Git 做版本控制  
3. Visual Studio Code 作為本機編輯器  
4. (選配) 在 Windows 上直接安裝 Jekyll 或使用 Docker for Windows 來本機預覽

## Q: 用靜態網站後，「會員／權限管理」與「後台管理」怎麼辦？
讀者人人都能直接閱讀；作者只剩自己一人發文，因此完全不需要會員系統。發文採用本機編輯、git push 的方式，也就不需要傳統後台。

## Q: 靜態網站如何做版本控制？
所有檔案都是文字檔，直接丟進 Git repository。可自由 commit、branch、merge，甚至用 pull request 方式協作，文章與網站設定都一併受到版本管理與備份保護。

## Q: 為什麼作者堅持用 Markdown 而不用 WYSIWYG 編輯器？
Markdown 簡潔、純文字、格式不易走樣，搭配程式碼高亮與即時預覽編輯效率最高；反觀 HTML 所見即所得編輯器在文章一長或 CSS 改版時常出問題。

## Q: 純靜態網站要怎麼提供留言、按讚等互動功能？
利用第三方服務（例如 Disqus、Facebook Social Plugins、Google Analytics 等），只要在網頁嵌入對方提供的一段 HTML / JavaScript 程式碼即可。

## Q: GitHub Pages 背後使用的是哪個靜態網站產生器？
Jekyll。

## Q: 在 Windows 上要本機預覽 Jekyll，有哪三種做法？
1. 直接在 Linux 安裝 Jekyll（效能最佳，但需切換作業系統）  
2. 在 Windows 原生安裝 Jekyll（效能佳，但安裝環境較折騰）  
3. 利用 Docker for Windows 執行 Jekyll（安裝簡單，效能稍差）

## Q: Docker for Windows 跑 Jekyll 的主要痛點與解法是什麼？
Docker volume 無法把檔案變更通知傳到 container，導致 `jekyll --watch` 偵測不到異動。解法是加 `--force_polling` 參數改用輪詢，或乾脆手動重新啟動 container。

## Q: 為何作者最終偏好「Windows 原生 Jekyll」？
在作者的機器上，Windows 原生版首次建站約 30–40 秒、重建約半分鐘，而 Docker 版要 70 秒＋偵測延遲十多秒甚至數分鐘，實際寫作體驗差距明顯。

## Q: WordPress 資料要怎麼搬到 GitHub Pages / Jekyll？
作者參考 Jekyll-Import、WordPress Jekyll Exporter 等方案，再自行寫了 C# 工具，統一解決中文網址、分類／標籤、留言匯入及轉址等問題後，再輸出為符合 Jekyll 的 Markdown 與 Front-matter。

## Q: 舊網址（.aspx、含 QueryString…）如何在新網站保持可用？
安裝 `jekyll-redirect-from` 外掛，在每篇文章的 Front-matter 中列出舊網址清單 (`redirect_from:`)，必要時再配合前端 JavaScript 處理 QueryString，即可自動 301 轉址到新位置。

## Q: 全站開放在 GitHub 上，有什麼潛在風險？
別人要「整站打包」只要一行 `git clone`。作者認為部落格本來就是分享，用 CC 授權標明出處即可，被「複製」其實也是另一種推廣。

## Q: 作者認為把 Blog 放進 Git 最大的收穫是什麼？
不再只是單篇文章版本控制，而是「整個網站」—文章、草稿、設定、版型都能一次被 Git 追蹤與回溯；改版也可用分支測試後再合併上線，完全把寫 Blog 變成寫程式的工作流程。