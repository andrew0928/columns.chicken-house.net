# 網站升級: CommunityServer 2007.1

## 摘要提示
- 升級動機: 站長跳過多個 Service Pack 後，終於決定把原本的 CS 2007 (3.0) 一口氣升到 2007.1 (3.1)。
- 安裝流程: 多次失敗後改採「全新安裝＋資料庫升級腳本＋檔案目錄搬移」的方式完成部署。
- 佈景主題: 舊 themes 與新版本差異大，必須重新比對與修改，否則易產生相容性疑慮。
- 效能改善: 2007.1 重新設計快取框架、最佳化 SQL 查詢並加入多項鎖定機制。
- API/表單: 新增多個部落格前端表單與 Chameleon 控制項，強化 Blog CRUD 能力。
- 電子郵件: 信件佇列、通知與大量寄送全面改為背景執行，並加入「允許站台聯絡我」等使用者設定檢查。
- TinyMCE: 更新至新版包裝器，改善預設樣式、文件 URL 與可調整大小的編輯器行為。
- WLW/RSD: 完整支援 Windows Live Writer 與 RSD，包含自動偵測、關鍵字與 read-more 功能。
- 安全性: 新增暫時性使用者權杖、禁用匿名帳號刪改、修補多項 XSS 及權限漏洞。
- Bug 修正: 從快取、編碼、RSS、搜尋、UI 到權限等數百項瑕疵獲得修補。

## 全文重點
作者利用周日下午的空檔，將長期運行的 Community Server 2007（版本 3.0）直接升級到最新的 2007.1（3.1）。在嘗試以「就地升級」多次失敗後，他改採「全新佈署」策略：先安裝官方 2007.1 乾淨版，接著對舊資料庫套用官方 upgrade script，確認核心功能無誤後，再把舊有的 ~/blogs、~/photos、~/forums 等檔案儲存目錄搬回；最後花最多時間的是自訂佈景主題，因為 2007.1 幾乎調整了所有 theme 檔案，只能逐一比對並重新修改。作業完成後，他順手把同機器上另外兩套 CS 也同步升級。

接續文章貼出官方「Community Server 2007.1 Release Notes」，分為 Enhancements 與 Bug Fixes 兩大區塊。Enhancements 部分著重效能與擴充：重新設計的快取框架、SQL 最佳化、鎖定機制、背景佇列化的 Email/Notification、TinyMCE 與 Windows Live Writer 的整合、TagCloud 與 LinkCategory 分頁排序、暫時性 UserToken、KeepAlive 控制、基本站台與部落格新 Theme，以及多項 API 強化。Bug Fixes 則涵蓋檔案系統監聽路徑、編碼、匿名瀏覽重導、Editor 疊層、Gallery/Forum/Blog 多項介面與權限錯誤、快取名稱、搜尋索引、RSS Feed、Regex 驗證、XSS 等大量問題修補，徹底提升穩定度與安全性。

整體而言，2007.1 不僅是小幅更新，而是兼顧效能、功能與安全的大型整合版；對長久未更新的站台來說，升級後能在快取效率、寄信佇列、使用者體驗與後端維運上獲得顯著改善。

## 段落重點
### 升級紀錄
作者先描述自己趁家中清閒時進行升級作業，原本想直接套用 CS 3.0 SP1~SP3 都未實施，這次 3.1 出爐決定一次到位。過程中嘗試多次失敗後改走「全新安裝＋資料庫升級」路線：安裝 2007.1 官方版、對舊 DB 執行 upgrade script、搬移各應用程式 Storage 目錄並重製自訂 Theme；最後把同機器其餘兩套 CS 也一併升級，宣告任務完成。

### Enhancements（功能增強）
官方列出近 40 條強化項目：核心改動包含全新的快取框架、SQL Best Practice、Lock 支援；Blog 新增前端 Create/Edit/Delete 表單、TagCloud 控制更彈性；新增 LinkCategory/Link API 排序分頁；引入應用程式 Token 開關、暫時性 UserToken、背景執行 Email 佇列；TinyMCE 更新、WLW/RSD 完整支援；KeepAlive 控制重構；加入新基本 Theme 與 AdPlacement；改善日期格式、錯誤訊息呈現以及多項 UI/UX 細節。

### Bug Fixes（錯誤修補）
修補清單超過百項，涵蓋：FileSystemWatcher 路徑、Request/Response 編碼、匿名瀏覽不再誤導向登入；TinyMCE 視窗層疊、Blog AppKey/Validation、Gallery Search、Thread Cache、User Email 驗證、Theme 快取鍵錯誤、RSS Feed 錯誤、Forum Sticky 編輯、Avatar 重複編碼、Firefox 版面錯位、XML-RPC Ping 漏送、XSS 與 Regex 驗證、Infinite Redirect、Duplicate Post 檢查、Search 索引權限、KeepAlive Script 移除、IE/Firefox UI 高度問題等。整體大幅提升系統穩定性與安全性。