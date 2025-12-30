---
layout: synthesis
title: "Blogging as code !!"
synthesis_type: faq
source_post: /2016/09/16/blog-as-code/
redirect_from:
  - /2016/09/16/blog-as-code/faq/
---

# Blogging as code !!

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是「Blogging as code」？
- A簡: 以程式化方式經營部落格：用 Git 版控、Markdown 撰寫、Jekyll 編譯、GitHub Pages 發佈，讓寫作像部署程式碼一樣可追蹤與自動化。
- A詳: 「Blogging as code」是一種以開發者思維經營內容的方法。核心理念是把文章、版型與網站設定視為程式碼資產，用 Git 管理歷程、分支、合併與回溯；用 Markdown 專注內容，以 Liquid 模板生成頁面，並交由 Jekyll 將靜態頁部署到 GitHub Pages。互動功能如留言、統計、社群分享改以第三方服務嵌入，去除伺服器 runtime 依賴，降低維運成本與風險。整體流程與軟體開發一致，利於協作、審閱、測試與持續改進。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q3, A-Q4, B-Q1, C-Q1

A-Q2: 為什麼選擇靜態網站寫部落格？
- A簡: 靜態網站無需後端執行，速度快、安全、維運簡單；互動功能以第三方嵌入補齊，降低資源耗用與維護負擔。
- A詳: 多數部落格內容無須「當下計算」即可決定，文章、列表、分類、標籤、分頁都可預先生成為 HTML。改用純靜態架構可避免伺服器程式升級、資料庫維護與安全面攻擊面；效能高、成本低且綠色節能。必要的動態需求（留言、按讚、統計）以 Disqus、Facebook、Google Analytics 等外掛碼嵌入即可，讓靜態頁面也擁有互動能力，同時保留簡潔的發佈流程。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q13, B-Q2, B-Q10

A-Q3: GitHub Pages 是什麼？提供哪些功能？
- A簡: GitHub 的靜態網站託管服務，綁定指定 branch；變更觸發 Jekyll 建置，將倉庫內容轉成可公開瀏覽的網站。
- A詳: GitHub Pages 讓你在指定的 repository 與 branch（例如 main 或 gh-pages）上維護網站原始碼。每次推送異動，GitHub Pages 會自動啟動 Jekyll 進行建置，將 Markdown 與模板轉為 HTML，並直接託管輸出結果。它特別適合專案文件與部落格，提供自動化部署、免費 CDN 與自有網域綁定，無需自架主機與後端。對開發者而言，整個網站即程式碼，配合 Pull Request 審閱與版本回溯，流程清晰。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, C-Q1

A-Q4: Jekyll 是什麼？扮演什麼角色？
- A簡: Jekyll 是靜態網站產生器，將 Markdown、Liquid 模板與 Front Matter 組裝為 HTML，驅動 GitHub Pages 建置。
- A詳: Jekyll 以 Ruby 實作，讀取專案中的內容文件（Markdown、HTML）、版型（Liquid）、組態（_config.yml）與前置資料（Front Matter），在本地或 GitHub Pages 端將其轉譯為純 HTML 靜態網站。它支援文章、頁面、草稿、分類/標籤與分頁等常見部落格需求，並能透過外掛擴充（如 jekyll-redirect-from）。在「Blogging as code」流程中，Jekyll是編譯器與打包器，將文字資源變為可部署的網站。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, C-Q3, C-Q4

A-Q5: 為何選擇 Markdown 撰寫內容？
- A簡: Markdown 語法簡潔、跨平台易讀，搭配 VS Code 預覽與 Git 比對高效，專注內容而非繁複排版。
- A詳: Markdown 是以可讀性為優先的輕量標記語言，標題、清單、程式碼、引用等常用格式簡潔直觀。它是純文字，與 Git 完美結合，利於 diff、審閱與合併，避免 WYSIWYG 編輯器帶來的樣式干擾。搭配 VS Code 可即時預覽、語法高亮與延伸套件支援，提升寫作效率與品質。文章的價值在內容本身，Markdown 讓你專注文字與結構，將美術與模板交給 Liquid 與 CSS 處理。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, B-Q10, C-Q2

A-Q6: 靜態網站與動態網站有何差異？
- A簡: 靜態站預先產生 HTML，請求即回應；動態站請求時執行程式組頁。靜態快、安全易維；動態彈性強、可即時運算。
- A詳: 靜態網站在建置階段完成內容生成，伺服器只需回傳檔案，因而更快、更安全，且易於快取與低成本託管；缺點是即時互動需另依賴外部服務。動態網站在請求時執行後端程式（如 PHP、Rails、Node），可根據用戶狀態或資料庫即時產頁，彈性高，但維護、擴容與安全壓力較大。選擇何種模式，取決於是否存在必須即時計算才能決定的內容。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q13, B-Q2

A-Q7: 為什麼不使用部落格系統內建的版本控制？
- A簡: Git 提供分支、合併、回溯、PR 與強大比對能力，遠勝多數部落格系統簡化的版控與備份機制。
- A詳: 專業開發工作流仰賴 Git 的分支與合併模型來管理變更，能細緻追蹤每一行差異、提交訊息與作者，並支持多人協作審閱（Pull Request）。相較之下，多數傳統部落格系統的版本功能侷限於單篇歷程或備份，難以一致管理文章、設定與模板的整體變更。以 Git 控制整個網站，能在改版時開分支驗證，再合併上線，極大提升可靠度與可回溯性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, B-Q12

A-Q8: 為何將部落格 Open Source？
- A簡: 透明協作、易於引用與擴散；配合 CC 授權標註出處，既促進分享也管理風險與授權邊界。
- A詳: 把整個部落格放上 GitHub 開源，意味著他人可 clone、fork、發 PR，共同改進內容或模板。這促進知識擴散與社群互助，也讓錯誤更快被發現。雖然「被整站複製」風險增加，但可藉由 Creative Commons 等授權聲明要求標註出處，維持合法引用與傳播。對作者而言，開源將寫作從個人活動轉為協作工程，回饋可觀。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q1, A-Q15

A-Q9: 第三方服務在靜態站的角色是什麼？
- A簡: 以嵌入碼提供留言、按讚、分享與流量統計，讓靜態頁面擁有動態互動能力而不需伺服器程式。
- A詳: 靜態站不執行後端程式，但可透過前端嵌入第三方 widget 提供互動功能。例如 Disqus 或 Facebook Comments 處理留言，Facebook Social Plugins 提供按讚/分享，Google Analytics 追蹤流量。只需在模板適當位置加上服務提供的 HTML/JS，再以 Liquid 填入動態變數（如標題、網址、摘要），即可生效。這種方式保留靜態架構優勢，同時滿足常見網站需求。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q8, C-Q9

A-Q10: GitHub Pages 的運作模式為何？
- A簡: 綁定 repo 指定 branch；每次 push 觸發 Jekyll 建置，將 Markdown 與模板轉為 HTML 後自動託管。
- A詳: 在 GitHub Pages 中，你設定某個 branch 作為網站來源。當該 branch 發生變更（commit/push），GitHub 的建置流程會啟動 Jekyll，依 _config.yml 與專案結構解析內容、套模板、輸出到公開的網站根目錄。整個過程無需手動部署；你只需專注於提交內容與版型，其他交給平台自動處理，這正是「as code」流程的關鍵。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, C-Q1

A-Q11: 為何從 WordPress 轉向 Jekyll？
- A簡: 功能過多且維運重，Markdown 支援不足；改用靜態可專注內容，並用 Git、模板與外掛服務補足需求。
- A詳: 過去使用 WordPress 雖功能完整，但實際需求常用不到 5%，卻要承擔升級、備份、安全與效能的維護成本。相反地，Jekyll + GitHub Pages 以靜態方式滿足主要需求，搭配 Markdown 撰寫體驗佳，Git 版控與分支讓寫作與改版更工程化。互動與分析需求以第三方服務嵌入即可，整體更貼近開發者工作流。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q9, C-Q7

A-Q12: 什麼是 Liquid？與 Markdown 有何關係？
- A簡: Liquid 是模板引擎，提供變數、迴圈與條件；Markdown 負責內容標記，兩者合力生成最終 HTML。
- A詳: Liquid 由 Shopify 推出，是 Jekyll 使用的模板語言。它允許在版型中使用變數（如頁面標題、URL）、控制流程（迴圈列出文章、條件判斷分類）與過濾器處理字串/日期。Markdown 則著重內容撰寫的語法標記。建置時，Jekyll 先把 Markdown 轉 HTML，再由 Liquid 將資料套入佈局版型，組裝成完整頁面。兩者角色分工清晰，提升重用性與維護性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, C-Q6

A-Q13: 何謂「是否需要 runtime process」的判斷？
- A簡: 若內容不需即時計算與個人化，皆可在建置期預先產出靜態頁；互動交由前端嵌入服務達成。
- A詳: 判斷重點是頁面在「請求當下」是否必須依使用者狀態或即時資料決定內容。像文章、列表、分類、標籤與分頁等，可在建置時生成；留言、按讚、統計等則由第三方前端元件處理。若核心內容多為可預先決定，採用靜態架構即可大幅簡化系統，保留效能與安全優勢，同時以外掛服務補齊互動性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q2, B-Q2, A-Q9

A-Q14: 以開發者為中心的寫作流程有何價值？
- A簡: 工具鏈一致、可版本化、可審閱與自動化，讓寫作與部署像開發一樣可靠、可追蹤且易於協作。
- A詳: 選擇 Git、Markdown、Liquid、Jekyll 與 GitHub Pages，讓寫作流程與軟體開發一致。文字檔便於 Diff 與 Code Review，Pull Request 可導入審稿機制；分支可隔離改版，合併後自動部署；模板化可重用、可測試；第三方服務嵌入降低後端負擔。這些優勢合力提升內容品質與交付穩定性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q1, A-Q15, B-Q12

A-Q15: 用 Git 工作流管理文章的核心價值？
- A簡: 可同時控管多篇文章、草稿、設定與版型；開分支測試改版，合併上線並保留完整歷程。
- A詳: 以 Git 管理，不只單篇文章，還包括整站配置（_config.yml）、模板（_layouts）、資產（images、css）與資料（_data）。你可在 feature 分支重構模板、改版 UI，或在 draft 分支編寫尚未發布的內容；確認無誤後合併至主分支即自動上線。若發現問題可回滾版本，確保穩定交付。這種一致性控管是部落格系統難以達成的。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, C-Q10

A-Q16: Categories 與 Tags 的差異與重要性？
- A簡: 分類偏主題層次，標籤偏關鍵字維度；皆利於導覽與搜尋，Jekyll 原生支援並可在模板呈現。
- A詳: Categories 通常用於定義內容的大方向（如 技術/生活/教學），具層級性；Tags 則提供交叉維度（如 GitHub、Jekyll、Docker），方便彈性聚合。正確標註有助讀者探索、提升 SEO 與網站結構清晰度。Jekyll 會在文章 Front Matter 解析 categories 與 tags，你可在 Liquid 中產生列表或雲圖，提供良好導覽體驗。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q7, C-Q6

A-Q17: 靜態站如何處理留言與社交互動？
- A簡: 以第三方服務（如 Disqus、Facebook Social Plugins）嵌入留言、按讚與分享元件，模板輸出必要 HTML/JS 即可。
- A詳: 將互動交給專業服務：留言可用 Disqus 或 Facebook Comments，按讚與分享用 Facebook Social Plugins，流量分析用 GA。你只需在模板中嵌入服務提供的程式碼片段，並以 Liquid 注入文章標題、網址、描述與 og meta，即可運作。此法保留靜態站的速度與安全，同時滿足常見互動需求。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q8, C-Q9

A-Q18: 什麼是 jekyll-redirect-from？用途為何？
- A簡: 用 Front Matter 宣告舊網址，外掛自動產生重導頁，維持歷史連結與 SEO，支援多來源映射。
- A詳: jekyll-redirect-from 外掛允許在文章 Front Matter 加入 redirect_from 欄位，列出歷史 URL（含舊平台如 WordPress、BlogEngine、Community Server）。建置時外掛會生成對應重導頁，確保舊連結仍能導向新文章，降低 404 與 SEO 流量損失。對大型遷移尤為關鍵，也利於保留外部引用效益。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, C-Q6

A-Q19: 為何檔名大小寫在不同平台會出問題？
- A簡: Windows/IIS 對檔名大小寫不敏感；GitHub Pages（類 Unix）嚴格區分，連結與實體檔案大小寫不一致會 404。
- A詳: 在 Windows 上，檔案系統與 IIS 對大小寫通常不敏感，因此 a.png 與 A.PNG 被視為同一檔。但部署到 GitHub Pages（以 Linux 為基礎）時，URL 與檔名必須精確一致，否則引用圖片或連結會失效。遷移與預覽時應統一命名規範，並注意 Git on Windows 對大小寫變更不易察覺的特性，必要時使用 git mv -f 強制更名。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q5, B-Q6

A-Q20: 為何選擇 VS Code 作為寫作工具？
- A簡: VS Code 輕量快速，內建 Git、Markdown 預覽與語法高亮，擴充豐富，適合以文字檔為核心的寫作流程。
- A詳: VS Code 提供跨平台的開發體驗，對 Markdown 具預覽、目錄導覽與延伸套件（如拼字檢查、Lint）的良好支援；內建 Git 面板可視化提交、分支與差異比對。對「Blogging as code」而言，它同時是編輯器、預覽器與版控前端，將寫作、測試與提交整合於同一介面，顯著提高效率。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, C-Q10

---

### Q&A 類別 B: 技術原理類

B-Q1: GitHub Pages 如何觸發並完成建置與發佈？
- A簡: 指定 branch 異動即觸發 Jekyll 於雲端建置，讀取專案結構與設定輸出 HTML，完成後自動託管。
- A詳: 原理說明：GitHub Pages 監聽指定 branch 的 push 事件。關鍵流程：1) 解析 _config.yml 與 repo 結構；2) 啟動 Jekyll，載入文章、頁面與 Front Matter；3) Markdown 轉 HTML；4) 套用 Liquid 版型與資料；5) 執行外掛（如 redirect-from）；6) 輸出靜態檔；7) 發佈至 Pages 主機。核心組件：GitHub Webhooks/內建建置管線、Jekyll、儲存與 CDN。開發者只需維護原始碼與提交，建置與託管全自動完成。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q10, C-Q1

B-Q2: Jekyll 建置的執行流程與組件為何？
- A簡: 讀設定與內容→解析 Front Matter→Markdown 轉 HTML→套 Liquid 佈局→執行外掛→輸出 _site。
- A詳: 原理說明：Jekyll 將內容與版型分離。流程：1) 載入 _config.yml；2) 掃描 posts/pages，解析 YAML Front Matter（標題、分類、標籤、永久連結等）；3) 將 Markdown 以轉換器處理為 HTML；4) 以 Liquid 將資料套入 layouts/includes；5) 執行外掛（如 jekyll-redirect-from）；6) 輸出到 _site。核心組件：轉換器（Markdown）、模板引擎（Liquid）、集合（collections）、插件系統。此流程支撐靜態化與可擴充性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, B-Q10

B-Q3: jekyll --watch 與 --force_polling 背後機制是什麼？
- A簡: --watch 依賴檔案系統通知；通知不可用時改用 --force_polling 定期掃描檔案差異，效能較低。
- A詳: 原理說明：--watch 透過 OS 的檔案變更通知（如 inotify、FSEvents、Windows notify）即時偵測異動，快速觸發重建。於 Docker for Windows 的 volume 上，通知常無法傳入容器，導致不生效。此時 --force_polling 以周期性掃描目錄比對時間戳與雜湊判斷變更。關鍵步驟：1) 設定監控目錄；2) 監聽通知或輪詢；3) 差異檢測；4) 增量或全量重建。核心組件：檔案監看器、輪詢器、建置觸發器。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q3, D-Q1, D-Q2

B-Q4: 為何 Docker for Windows 的 volume 會失去變更通知？
- A簡: Windows 檔案系統通知穿越虛擬化與 volume 映射時常無法傳遞至容器，導致 --watch 偵測不到異動。
- A詳: 原理說明：Docker for Windows 透過檔案共享機制將主機目錄掛載到 Linux 容器。Windows 的變更通知 API 與 Linux 的 inotify 機制不完全對應，經過虛擬層與網路檔案系統轉譯後，容器內觀察點收不到事件。關鍵步驟：1) 主機檔案變更；2) 共享機制同步內容；3) 通知事件丟失；4) 容器內監看器無感。核心組件：檔案共享守護程序、虛擬化層、容器內檔案系統。解法即改用 polling 或改在主機原生執行。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q1, D-Q2

B-Q5: 在 Windows 同時使用 Jekyll 與 IIS Express 的架構？
- A簡: Jekyll s 監看與建置（如 4000），IIS Express 服務 _site 靜態輸出（如 4001），視需求切換預覽。
- A詳: 原理說明：Jekyll 內建伺服器在 Windows 對某些情境（如中文檔名）支援不佳，可分離建置與服務。流程：1) jekyll s -w 監看與產出至 _site；2) IIS Express 對 _site 提供靜態服務；3) 開兩個不同埠口預覽；4) 遇到 .aspx 擴充名在 IIS 會被 ASP.NET 模組攔截時，改用 Jekyll 端預覽。核心組件：Jekyll watcher、IIS 靜態檔模組、埠口路由。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q5, D-Q7

B-Q6: 大小寫敏感性的系統差異與對網站的影響？
- A簡: Windows/IIS 大小寫不敏感，Linux/Pages 敏感；導致連結與檔名不一致時，部署後才爆錯。
- A詳: 原理說明：檔案系統與 Web 伺服器的大小寫敏感策略不同。Windows 的 NTFS + IIS 多半視 a.png 與 A.PNG 為同檔案；Linux 檔案系統與 Nginx/Pages 服務則視為不同資源。關鍵影響：1) 本機預覽正常、雲端 404；2) Git on Windows 對僅大小寫變更不易察覺。防範步驟：統一命名規範、在本機以大小寫敏感容器驗證、用 git mv -f 強制更名。核心組件：檔案系統、HTTP 伺服器、Git。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q19, D-Q5

B-Q7: WordPress 到 Jekyll 的資料轉換原理？
- A簡: 由 WP 匯出 XML，解析文章/分類/標籤/網址/留言，轉為含 Front Matter 的 Markdown 與對應資源。
- A詳: 原理說明：利用 WP Export（或外掛）輸出整站 XML，再以轉換工具（官方 jekyll-import、外掛或自製程式）讀取節點，將文章內容轉為 Markdown，並將標題、日期、分類、標籤、permalink 與轉址列表寫入 Front Matter。特殊處理：中文網址解碼、留言對應、舊平台多種 URL 格式映射。核心組件：XML 解析器、轉換器、Jekyll 專案結構。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q7, D-Q6, D-Q9

B-Q8: 舊網址轉址機制（jekyll-redirect-from）如何運作？
- A簡: 根據 Front Matter 的 redirect_from 清單產生對應重導頁，請求時導向新 permalink。
- A詳: 原理說明：外掛在建置階段掃描每篇文章的 redirect_from 陣列，為每個舊 URL 生成對應的靜態頁（或設定標頭），該頁面包含導向邏輯（如 meta refresh 或 server 規約）。流程：1) 解析舊 URL 清單；2) 生成重導頁；3) 部署後訪問舊連結時導向新頁。核心組件：Jekyll plugin、Front Matter、靜態重導頁。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q18, C-Q6

B-Q9: 留言遷移與 URL 對應的技術要點是什麼？
- A簡: 留言系統以 URL 為錨點，需將舊 WP URL 與新 permalink 對上；必要時預處理 XML 的中文網址。
- A詳: 原理說明：第三方留言服務以頁面 URL 或識別碼綁定留言串。遷移時若只改新網址，舊留言會失聯。步驟：1) 解析 WP XML，取得每篇舊 URL（含 ?p=ID、slug 與中文路徑）；2) 在轉檔時寫入對應 permalink 與 redirect_from；3) 留言服務設定以新 URL 為主，並確保舊 URL 會 301/重導到新 URL。核心組件：URL 映射表、Front Matter、自動化轉檔程式。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: D-Q6, C-Q7

B-Q10: Markdown 與 Liquid 如何共同生成最終頁面？
- A簡: 先將 Markdown 轉 HTML，後以 Liquid 將資料套入 layout/includes，輸出完整頁面。
- A詳: 原理說明：建置時，Jekyll 先用 Markdown 轉換器將文章正文渲染成 HTML 片段；接著讀取 layout 與 includes 的 Liquid 模板，將 Front Matter 與站點變數（site、page）注入，組裝出頁框、導覽、側欄與 meta 標籤。流程：1) 內容轉換；2) 模板套用；3) 外掛處理；4) 輸出靜態檔。核心組件：Markdown 轉換器、Liquid、Front Matter、外掛。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, C-Q8, C-Q9

B-Q11: Docker 模式下 polling 與通知的效能差異？
- A簡: 通知即時低耗；polling 須頻繁掃描，I/O 與 CPU 耗用高，重建延遲明顯、隨檔案數量成長。
- A詳: 原理說明：通知機制只在變更時觸發，資源使用低；polling 必須定期檢查所有檔案時間戳或雜湊，成本與檔案數線性甚至更差。案例：數百篇文章下，polling 的 rebuild 可能延遲至數十秒甚至數分鐘。建議在開發環境避免 watch 容器，改手動重啟或在 Windows 原生執行 Jekyll。核心組件：檔案系統、監控策略、建置觸發器。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q2, C-Q3

B-Q12: 用 Git 分支管理網站改版的技術架構？
- A簡: 以 feature 分支進行模板/設定改動，CI/建置預覽後合併主分支自動發佈，可回溯與快速回滾。
- A詳: 原理說明：將網站視作程式碼，改版在獨立分支開發，避免影響線上。流程：1) 建立分支（feature/theme-redesign）；2) 提交變更（模板、CSS、_config.yml）；3) 本地或 Pages 預覽驗證；4) 發 PR 審閱；5) 合併至主分支觸發部署；6) 問題時回滾或 hotfix。核心組件：Git、審閱流程、Jekyll 建置、自動部署。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, C-Q10

---

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何在 GitHub Pages 上建立 Jekyll 部落格？
- A簡: 建立 repo 與指定 branch，加入 Jekyll 專案結構與設定，推送後由 Pages 自動建置與託管。
- A詳: 
  - 具體實作步驟:
    1) 在 GitHub 建立 repo，設定 Pages 來源 branch。
    2) 於本地建立 Jekyll 專案（或複製範本），撰寫 _config.yml、_posts/、_layouts/。
    3) git add/commit/push 至指定 branch。
  - 關鍵程式碼片段或設定:
    - _config.yml 基本站點設定（title、url、permalink）。
  - 注意事項與最佳實踐:
    - 確保 Front Matter 正確；避免大小寫錯誤；先在本地建置驗證，再推送。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q2

C-Q2: 如何用 VS Code 撰寫 Markdown 並預覽？
- A簡: 以 VS Code 開啟專案，使用 Markdown Preview，同時搭配 Git 面板提交版本，效率高。
- A詳:
  - 具體實作步驟:
    1) 打開資料夾：code d:\blog
    2) 新增或編輯 _posts/檔案.md，寫 Front Matter 與內文。
    3) 使用預覽（Ctrl+Shift+V），確認格式。
    4) Git 提交與推送。
  - 關鍵程式碼片段或設定:
    - Front Matter 範例：
      ---
      title: "標題"
      date: 2025-01-01
      tags: [Jekyll]
      ---
  - 注意事項與最佳實踐:
    - 使用字數檢查/拼字外掛；保持檔名與連結大小寫一致。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, A-Q20

C-Q3: 如何用 Docker for Windows 執行 Jekyll？
- A簡: 以官方 jekyll/jekyll:pages 映像搭配 volume 與埠轉發啟動，必要時加 --force_polling。
- A詳:
  - 具體實作步驟:
    1) 安裝 Docker for Windows。
    2) 於命令列執行：
       docker run -ti --rm -p 4000:4000 -v D:\Blog:/srv/jekyll jekyll/jekyll:pages jekyll s --watch --force_polling
  - 關鍵程式碼片段或設定:
    - -v D:\Blog:/srv/jekyll 將本機專案掛載至容器。
    - --force_polling 解決通知無法傳遞問題。
  - 注意事項與最佳實踐:
    - 檔案多時 polling 會慢；考慮改手動重啟或加大容器資源。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q4, D-Q1

C-Q4: 如何在 Windows 安裝並啟動 Jekyll？
- A簡: 安裝 Ruby（選擇 2.2 版較相容）、安裝 jekyll/gems，啟動 jekyll s -w 監看建置。
- A詳:
  - 具體實作步驟:
    1) 安裝 Ruby 2.2.x。
    2) gem install jekyll bundler
    3) jekyll s --draft -w
  - 關鍵程式碼片段或設定:
    - jekyll s --draft -w 生成草稿並監看。
  - 注意事項與最佳實踐:
    - 部分套件不支援新 Ruby；若遇錯誤降版；確認 PATH 與 gem 安裝完成。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q3, B-Q2

C-Q5: 如何同時使用 Jekyll 與 IIS Express 預覽？
- A簡: 讓 Jekyll 監看輸出 _site，再用 IIS Express 服務 _site，兩埠並行預覽並避開編碼限制。
- A詳:
  - 具體實作步驟:
    1) 啟動 Jekyll：jekyll s --draft -w
    2) 啟動 IIS Express：
       "c:\Program Files\IIS Express\iisexpress.exe" /port:4001 /path:d:\blog\_site
  - 關鍵程式碼片段或設定:
    - 以 4000 預覽 Jekyll、4001 預覽 _site（IIS）。
  - 注意事項與最佳實踐:
    - .aspx 擴充名在 IIS 會被轉給 ASP.NET；遇問題改用 Jekyll 端預覽。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, D-Q7

C-Q6: 如何設定 jekyll-redirect-from 處理舊網址？
- A簡: 在 Front Matter 加入 redirect_from 陣列列出舊 URL，建置時自動產生重導頁維持相容。
- A詳:
  - 具體實作步驟:
    1) 安裝外掛（在 GitHub Pages 支援清單內）。
    2) 在文章 Front Matter 加：
       redirect_from:
         - /old/path-1/
         - /post/123.aspx/
  - 關鍵程式碼片段或設定:
    ---
    redirect_from:
      - /columns/post/2008/10/10/xxx.aspx/
      - /?p=59
    ---
  - 注意事項與最佳實踐:
    - 蒐集各平台歷史 URL；大量轉址時自動化生成 Front Matter。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, D-Q6

C-Q7: 如何把 WordPress 匯出資料轉成 Jekyll 文章？
- A簡: 匯出 WP XML，使用轉換工具解析並輸出含 Front Matter 的 Markdown，處理中文網址與分類標籤。
- A詳:
  - 具體實作步驟:
    1) 在 WP 匯出 XML。
    2) 使用 jekyll-import 或自製工具解析，產生 _posts/*.md。
    3) 將 categories、tags、permalink、redirect_from 寫入 Front Matter。
  - 關鍵程式碼片段或設定:
    - Front Matter 包含 wordpress_postid 便於對應。
  - 注意事項與最佳實踐:
    - 處理中文網址解碼；建立 URL 映射以保留留言與 SEO。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, D-Q9

C-Q8: 如何加入 Google Analytics 與 AdSense？
- A簡: 將 GA 與 AdSense 提供的 script 片段貼入模板（如 head 或 body），以 Liquid 注入動態資訊。
- A詳:
  - 具體實作步驟:
    1) 取得 GA 測量 ID 與 AdSense 客戶 ID。
    2) 在 _layouts/default.html 的 head/body 嵌入官方 script。
  - 關鍵程式碼片段或設定:
    - GA:
      <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXX"></script>
      <script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-XXXX');</script>
  - 注意事項與最佳實踐:
    - 依需求在文章頁才載入；確認隱私與地區法規。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, B-Q10

C-Q9: 如何加入 Facebook Open Graph 與分享按鈕？
- A簡: 在 head 放 og:title/url/image 等 meta，於頁面嵌入 FB 分享/讚按鈕程式碼，Liquid 注入變數。
- A詳:
  - 具體實作步驟:
    1) 在 head 加：
      <meta property="og:title" content="{{ page.title }}">
      <meta property="og:url" content="{{ page.url | absolute_url }}">
    2) 放入 FB SDK 與分享按鈕 HTML。
  - 關鍵程式碼片段或設定:
    - <div class="fb-like" data-href="{{ page.url | absolute_url }}" data-layout="button_count"></div>
  - 注意事項與最佳實踐:
    - 提供 og:image；確保 URL 可公開訪問以利抓取。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q17, B-Q10

C-Q10: 如何設計高效的寫作工作流？
- A簡: 以「撰寫→預覽→修正→提交→發佈」循環，配合分支管理與在地建置，提升品質與速度。
- A詳:
  - 具體實作步驟:
    1) 開 VS Code：code d:\blog
    2) 啟動 Jekyll：jekyll s --draft -w
    3)（可選）啟動 IIS Express 預覽 _site
    4) 編寫與預覽，修正
    5) git commit/push 觸發發佈
  - 關鍵程式碼片段或設定:
    - 命令如上；草稿用 --draft。
  - 注意事項與最佳實踐:
    - 用分支承載大改版；提交訊息語意化；發佈前本地全站預覽。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q15, B-Q12

---

### Q&A 類別 D: 問題解決類（10題）

D-Q1: 在 Docker 中 jekyll --watch 不生效怎麼辦？
- A簡: 因變更通知無法傳入容器，改用 --force_polling 或改以手動重啟容器觸發建置。
- A詳:
  - 問題症狀描述: 變更檔案後容器內 Jekyll 不重建。
  - 可能原因分析: Windows 到容器的共享 volume 丟失檔案變更通知。
  - 解決步驟: 1) 加上 --force_polling；2) 或去掉 --watch，改以修改後重啟容器；3) 或改在 Windows 原生跑 Jekyll。
  - 預防措施: 減少 polling 頻率對效能衝擊；在開發期選擇原生環境。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q4, C-Q3

D-Q2: Docker 模式 rebuild 很慢如何優化？
- A簡: Polling 造成高 I/O 與延遲，避免 watch，調高容器 CPU/RAM，或改用 Windows 原生 Jekyll。
- A詳:
  - 問題症狀描述: 檔案更新需十多秒甚至數分鐘才觸發重建。
  - 可能原因分析: --force_polling 對大量檔案造成負擔；容器資源不足。
  - 解決步驟: 1) 不用 watch，改手動重啟；2) 調整 Docker 資源配額；3) 減少不必要的檔案監看。
  - 預防措施: 開發用原生環境、部署用容器；模組化目錄減少掃描範圍。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, C-Q3

D-Q3: Windows 下 Ruby 版本相容性問題如何解？
- A簡: 若套件不支援新 Ruby，改用 2.2 等較相容版本，再安裝 jekyll 與相依 gem。
- A詳:
  - 問題症狀描述: gem 安裝或執行報版本相依錯誤。
  - 可能原因分析: Jekyll 或外掛尚未支援最新 Ruby。
  - 解決步驟: 1) 卸載新版；2) 安裝 Ruby 2.2.x；3) 重新安裝 jekyll/bundler；4) 測試建置。
  - 預防措施: 參考相依矩陣；固定版本於 Gemfile；建立可複製的開發環境。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q4, B-Q2

D-Q4: Jekyll 內建伺服器無法處理中文檔名怎麼辦？
- A簡: 改以 IIS Express 服務 _site 或統一使用英數 slug 檔名避免編碼問題。
- A詳:
  - 問題症狀描述: 本地預覽時中文路徑/檔名無法正確顯示。
  - 可能原因分析: Windows 環境下內建伺服器對路徑編碼支援不佳。
  - 解決步驟: 1) 用 jekyll s 監看輸出；2) 用 IIS Express 提供靜態服務預覽；3) 或改名為英數。
  - 預防措施: 制定命名規範與 permalink 策略，降低編碼風險。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q5, B-Q5

D-Q5: 推上 GitHub Pages 掉圖怎麼辦（大小寫不一致）？
- A簡: 檢查連結與檔名大小寫，改為一致；在 Windows 上以 git mv -f 強制更名提交。
- A詳:
  - 問題症狀描述: 本地預覽正常，線上圖片或連結 404。
  - 可能原因分析: Windows 對大小寫不敏感；GitHub Pages 嚴格區分。
  - 解決步驟: 1) 比對 URL 與檔名大小寫；2) 用 git mv -f 原名 改名 強制提交大小寫變更；3) 全站掃描修正。
  - 預防措施: 制定小寫命名規範；PR 檢查腳本；在大小寫敏感環境預覽。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q19, B-Q6

D-Q6: 遷移後留言消失如何診斷與修復？
- A簡: 檢查留言系統綁定的 URL，建立舊新 URL 映射與 redirect_from，確保重導至新 permalink。
- A詳:
  - 問題症狀描述: 歷史文章頁無留言或留言數為零。
  - 可能原因分析: 留言服務以 URL 綁定，遷移後網址改變未映射。
  - 解決步驟: 1) 從 WP XML 萃取舊 URL；2) 轉檔時寫入 redirect_from；3) 驗證重導至新 URL；4) 確認服務端設定。
  - 預防措施: 在轉檔前建立 URL 對照表；統一 permalink 策略。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q9, C-Q6, C-Q7

D-Q7: IIS Express 存取 .aspx 出現 404 怎麼辦？
- A簡: IIS 會交由 ASP.NET 模組處理 .aspx，改用 Jekyll 伺服器預覽，或避免使用 .aspx 延伸名。
- A詳:
  - 問題症狀描述: 頁面實為靜態 index.html，但以 .aspx 形式請求時 404。
  - 可能原因分析: IIS 看到 .aspx 即交給 ASP.NET；該路徑無動態處理程式。
  - 解決步驟: 1) 改用 Jekyll 預覽此頁；2) 或調整 IIS 對 .aspx 的處理（不建議）；3) 以 redirect-from 導向新路徑。
  - 預防措施: 避免動態副檔名；統一靜態 permalink。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q5

D-Q8: 靜態站無法處理 ?p=59 這類查詢字串怎麼辦？
- A簡: 以前端 JS 讀取查詢參數，查表映射至新路徑並導向；或用 redirect-from 列出對應新 URL。
- A詳:
  - 問題症狀描述: 舊連結使用 querystring ID，點擊後無法找到新頁。
  - 可能原因分析: 靜態伺服器不解讀參數路由。
  - 解決步驟: 1) 建立 ID→permalink 映射表；2) 在首頁加 JS 讀取 location.search 導向；3) 或在各文章加入 redirect_from。
  - 預防措施: 遷移前產生完整映射；盡量改用語意化路徑。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: C-Q6, C-Q7

D-Q9: 轉檔後只剩分類或只剩標籤如何修補？
- A簡: 檢查轉換工具輸出 Front Matter，補齊 categories/tags 欄位，選擇支援兩者的主題模板。
- A詳:
  - 問題症狀描述: 文章 Front Matter 只有 categories 或只有 tags。
  - 可能原因分析: 匯出工具或外掛僅支援其中之一。
  - 解決步驟: 1) 調整轉換設定或腳本；2) 二次處理 Front Matter 批次補欄位；3) 換用支援兩者的 theme。
  - 預防措施: 小樣本試轉驗證；建立自動化檢查腳本。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, C-Q7

D-Q10: 如何預防資料遺失與版本回溯失敗？
- A簡: 以 Git 小步提交、語意化訊息與遠端備援；改版用分支，重大變更前打標籤與本地建置驗證。
- A詳:
  - 問題症狀描述: 不慎覆寫或無法回到可用版本。
  - 可能原因分析: 缺乏系統化版控與發佈流程。
  - 解決步驟: 1) 採用 Git 工作流；2) 小步提交推送遠端；3) 發佈前本地全站建置；4) 打 tag 紀錄版本點。
  - 預防措施: 版本策略（branch/tag）；自動化檢查；PR 審閱流程。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q15, B-Q12

---

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是「Blogging as code」？
    - A-Q2: 為什麼選擇靜態網站寫部落格？
    - A-Q3: GitHub Pages 是什麼？提供哪些功能？
    - A-Q4: Jekyll 是什麼？扮演什麼角色？
    - A-Q5: 為何選擇 Markdown 撰寫內容？
    - A-Q6: 靜態網站與動態網站有何差異？
    - A-Q9: 第三方服務在靜態站的角色是什麼？
    - A-Q10: GitHub Pages 的運作模式為何？
    - A-Q20: 為何選擇 VS Code 作為寫作工具？
    - C-Q1: 如何在 GitHub Pages 上建立 Jekyll 部落格？
    - C-Q2: 如何用 VS Code 撰寫 Markdown 並預覽？
    - C-Q10: 如何設計高效的寫作工作流？
    - B-Q1: GitHub Pages 如何觸發並完成建置與發佈？
    - B-Q2: Jekyll 建置的執行流程與組件為何？
    - C-Q8: 如何加入 Google Analytics 與 AdSense？

- 中級者：建議學習哪 20 題
    - A-Q7: 為什麼不使用部落格系統內建的版本控制？
    - A-Q11: 為何從 WordPress 轉向 Jekyll？
    - A-Q12: 什麼是 Liquid？與 Markdown 有何關係？
    - A-Q13: 何謂「是否需要 runtime process」的判斷？
    - A-Q14: 以開發者為中心的寫作流程有何價值？
    - A-Q15: 用 Git 工作流管理文章的核心價值？
    - A-Q16: Categories 與 Tags 的差異與重要性？
    - A-Q18: 什麼是 jekyll-redirect-from？用途為何？
    - A-Q19: 為何檔名大小寫在不同平台會出問題？
    - B-Q3: jekyll --watch 與 --force_polling 背後機制是什麼？
    - B-Q4: 為何 Docker for Windows 的 volume 會失去變更通知？
    - B-Q5: 在 Windows 同時使用 Jekyll 與 IIS Express 的架構？
    - B-Q6: 大小寫敏感性的系統差異與對網站的影響？
    - B-Q10: Markdown 與 Liquid 如何共同生成最終頁面？
    - B-Q11: Docker 模式下 polling 與通知的效能差異？
    - B-Q12: 用 Git 分支管理網站改版的技術架構？
    - C-Q3: 如何用 Docker for Windows 執行 Jekyll？
    - C-Q4: 如何在 Windows 安裝並啟動 Jekyll？
    - C-Q5: 如何同時使用 Jekyll 與 IIS Express 預覽？
    - C-Q6: 如何設定 jekyll-redirect-from 處理舊網址？

- 高級者：建議關注哪 15 題
    - B-Q7: WordPress 到 Jekyll 的資料轉換原理？
    - B-Q8: 舊網址轉址機制（jekyll-redirect-from）如何運作？
    - B-Q9: 留言遷移與 URL 對應的技術要點是什麼？
    - D-Q1: 在 Docker 中 jekyll --watch 不生效怎麼辦？
    - D-Q2: Docker 模式 rebuild 很慢如何優化？
    - D-Q3: Windows 下 Ruby 版本相容性問題如何解？
    - D-Q4: Jekyll 內建伺服器無法處理中文檔名怎麼辦？
    - D-Q5: 推上 GitHub Pages 掉圖怎麼辦（大小寫不一致）？
    - D-Q6: 遷移後留言消失如何診斷與修復？
    - D-Q7: IIS Express 存取 .aspx 出現 404 怎麼辦？
    - D-Q8: 靜態站無法處理 ?p=59 這類查詢字串怎麼辦？
    - D-Q9: 轉檔後只剩分類或只剩標籤如何修補？
    - D-Q10: 如何預防資料遺失與版本回溯失敗？
    - C-Q7: 如何把 WordPress 匯出資料轉成 Jekyll 文章？
    - C-Q9: 如何加入 Facebook Open Graph 與分享按鈕？