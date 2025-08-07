# Blogging as Code !!

## 摘要提示
- 部落格演進: 作者十多年來換過 5 套系統，決定捨棄傳統動態平台。
- 靜態網站理念: 無需會員、後台與資料庫，全部交給 Git + Markdown。
- GitHub Pages: 以 Jekyll 自動編譯靜態頁面，免費、免維護。
- VS Code: 提供 Git 操作、Markdown 編輯與即時預覽的輕量工作環境。
- 本機開發: Windows 下可選原生 Jekyll 或 Docker 版，各有效能取捨。
- Workflow: 撰寫→Commit→Push→GitHub Pages 自動部署，流程單純。
- 匯出搬家: 自製 C# 工具將 WordPress 文章、分類、標籤與留言轉入 Jekyll。
- 轉址與 SEO: 利用 jekyll-redirect-from 保留舊網址與搜尋排名。
- 第三方服務: Comment、Like、GA、Adsense 以外掛 script 嵌入即可。
- 開源思維: 全站碼存 GitHub，促進版本控制與社群再利用。

## 全文重點
作者回顧自己十餘年來的部落格系統更迭後，決定徹底棄用需維護的動態平台，改走「Blogging as Code」路線：以純靜態檔案呈現網站內容，並利用 GitHub Pages 免費託管與自動建置。如此可消除會員、權限、後台與資料庫等負擔，將文章與設定統一放入 Git 儲存庫，由 Markdown 撰寫、Jekyll 編譯。編輯端選用 Visual Studio Code，兼具 Git 操作、語法高亮與即時預覽，形成開發者友好的工作流。

本機測試方面，作者在 Windows 上比較了三種方案：直接安裝 Jekyll、透過 Docker for Windows 執行，或改用 Linux。Windows 原生效能佳但安裝繁瑣；Docker 版部署簡易卻受檔案監控效能限制；Linux 為最佳體驗但與主要工作環境衝突。最終作者在開發期用 Windows 原生 Jekyll，必要時再切換 Docker。

為了將多年 WordPress 資料完整搬遷，作者評估官方 Jekyll-Import 及多種社群腳本後，自行撰寫 C# 工具，解決中文網址編碼、分類/標籤遺失、留言對應與舊連結轉址等問題，並透過 jekyll-redirect-from、JavaScript 與 Disqus 兼顧 SEO 及讀者互動。整體遷移完成後，不僅獲得簡化的維運與更強大的版本控制，亦符合開源精神；唯一代價是網站被「整倉複製」更加容易，但作者樂見其成，認為分享即價值所在。

## 段落重點
### TL;DR
作者細數自 2002 年以來歷經的五套部落格系統，指出傳統平台功能過剩又難維護，對開發者而言 Git 版本控制與 Markdown 才是核心需求；因此決定拋棄動態系統，改以純靜態網站加 GitHub Pages 實踐「Blogging as Code」。

### Solution: GitHub Pages Service + Visual Studio Code
GitHub Pages 透過 Jekyll 自動編譯指定 branch，發文者只要準備好模板與設定後，往正確分支 push Markdown 檔即可完成部署。配合 Visual Studio Code，可在單一介面進行 Git 操作、Markdown 編輯與預覽，形成成本低、學習曲線平緩的工具鏈。

### Workflow: How to create a new post ?
整體流程為撰寫（VS Code）→Commit→Push→GitHub Pages 自動建置，若需本機預覽則以 Jekyll 監聽檔案變動。作者習慣在 Windows 環境工作，因此針對 Jekyll 在 Windows、Docker 與 Linux 三條路線作效能與便利性評估。

### Running Jekyll on docker-for-windows
使用 Docker for Windows 僅需一行指令便能啟動 jekyll/jekyll:pages 映像並掛載專案目錄，但 Windows 檔案變動通知無法直達 container，需加上 --force_polling。Polling 造成 I/O 與 CPU 開銷，初次建置約 70 秒、後續監控更新可達 20 分鐘；作者建議改用手動重啟 container 取代 --watch。

### Running Jekyll on Windows
原生安裝 Ruby 與 Jekyll 可將初次建置壓至 30–40 秒，監聽更新約 30 秒完成，效能倍增。然而需注意 Ruby 版本、中文路徑、IIS 與 GitHub Pages 大小寫差異及 .aspx 靜態化等地雷。作者最終以 Jekyll --draft 配 IIS Express 雙伺服器方式在本機預覽草稿與正式文章。

### Wordpress to GitHub Pages Migration
官方匯入工具對中文與分類支援不足，作者參考多篇文章並自寫 C# 匯出器，修正中文 URL、檔名、分類、標籤及留言對應，同時透過 jekyll-redirect-from 保留多種舊網址格式，並嵌入 Google Analytics、Adsense、Facebook OG 與社群按鈕，使新舊站無縫銜接。

### Conclusion
「Blogging as Code」將文章、設定與佈景全納入 Git，提供橫跨多篇文章的版本管理、分支測試與快速回溯，對開發者而言大幅提升維運效率。雖然整站被 clone 更容易，但作者認為這與分享初衷一致，並鼓勵有興趣者嘗試 GitHub Pages + Jekyll 的輕量組合。