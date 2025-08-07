# [BlogEngine.NET] 改造工程 - CS2007 資料匯入

## 摘要提示
- 匯入動機: 原 BlogML 工具僅能轉入 90% 資料，遺漏舊文章 ID、瀏覽數等關鍵欄位。
- 自製工具: 參考 blogImporter.asmx 的程式碼，重寫成本機 ASHX，一次處理所有文章與回應。
- 進階需求: 追加文章瀏覽計數、回應詳細資訊、舊新 ID 對照、網址修正與日期錯誤修補。
- CS2007 特殊欄位: 解析 PropertyNames / PropertyValues 串列，取回匿名作者名稱與 IP 等資訊。
- SQL → XML: 透過 SQL2005 FOR XML AUTO 一次匯出，再以程式分拆並寫回 BlogEngine。
- 圖檔網址: 以 Regex 將 /blogs/chicken/* 路徑轉為 BlogEngine 的 image.axd 參數格式。
- 站內連結: 三種 CS URL 轉為兩種 BlogEngine URL，需先匯入再二階段替換。
- 舊址導向: 撰寫 HttpHandler CSUrlMap，依舊 ID 查表 301 轉址並處理 RSS。
- 正規表示式: 多網域、多格式網址一次命中，減少大量字串判斷程式。
- 成果總結: 一週完成資料轉移，後續將著手版面與 FunP 推推王整合。

## 全文重點
作者將部落格由 Community Server 2007 搬遷至 BlogEngine.NET，發現官方 BlogML 匯入工具僅能轉入九成資料，且缺少原文章 ID、瀏覽次數等欄位，於是決定自行撰寫匯入程式。首先他研究 blogImporter.asmx 的 WebMethod 實作，改寫成在網站本機執行的 ASHX，直接讀取放在 App_Data 的 BlogML，分別把文章與回應寫入，迅速完成基本匯入。  
為了補足剩餘的一成資訊，他列出五大需求：文章計數器、回應完整欄位、舊新 ID 對照、圖檔與站內連結修正，以及修補原程式將 ModifiedDate 寫錯的 bug。  
CS2007 將許多延伸屬性序列在 cs_posts 的 PropertyNames 與 PropertyValues 兩欄中，格式為 {Name}:{Type}:{Start}:{End}:；作者必須自行解析字串才能取得匿名留言者名稱、IP 等內容。完成解析後，他利用 SQL2005 Management Studio 的 FOR XML AUTO 指令，把查詢結果直接輸出為 XML，再用程式回填 BlogEngine。  
連結部分，他以 Regular Expression 大量替換。圖檔路徑需從 /blogs/chicken/… 轉為 BlogEngine 的 image.axd?picture=…，而站內文章連結有「archive/postID」、「archive/titleHash」與「/blogs/postID」三種形式，需在匯入完畢後，根據舊新 ID 表進行二次替換。  
為確保外部引用的舊網址不致失效，他撰寫 CSUrlMap HttpHandler，攔截所有 /blogs/*.aspx 請求，分析網址取出舊 PostID，查表後發 301 轉址至新 URL；RSS 也同樣導向新版路徑。  
整體工作歷時一週，雖然動作瑣碎，卻完成了資料、連結與統計的完整搬遷。下一階段作者將調整版型並與 FunP 推推王做深度整合。

## 段落重點
### 換站緣起與原工具限制
搬家後發現 BlogML 匯入僅轉入九成資料，缺失舊 CS PostID、PageViewCount 等欄位，擔心資料遺失而決定重新匯入。

### 決定自寫匯入程式
檢視 blogImporter.asmx 發現一次只處理一篇文章或一則留言且缺欄位，故改以 BlogEngine Lib 重寫為 ASHX，效能與可擴充性更佳。

### 基礎匯入流程
ASHX 開檔讀 BlogML，雙層迴圈依序新增文章與回應，短時間內完成原有九成資料的轉入。

### 追加五大自訂資訊
列出必須補齊的計數器、回應欄位、舊新 ID、網址修正與日期修補等需求，作為後續程式改造目標。

### 解析 CS2007 序列欄位
說明 PropertyNames / PropertyValues 拼接格式，透過程式分割字串以取得匿名留言者、IP 等被 BlogML 漏掉的資料。

### SQL 匯出成 XML
利用 SQL2005 Management Studio 執行 FOR XML AUTO，快速把查詢結果存成 XML 檔，再由程式載入使用。

### 圖檔與附件網址替換
分析 CS 舊圖檔的四種網址形式，以 Regex 擷取 /blogs/chicken/ 後段路徑並組成 image.axd 呼叫，成功修正所有圖片顯示。

### 站內連結二階段修正
舊站內三種文章連結格式需在匯入後透過舊新 ID 對照表再次替換，Regex 精準抓出舊 PostID 並生成新 URL 或 Slug。

### 舊網址轉址機制
撰寫 CSUrlMap HttpHandler，攔截舊網址與 RSS，依查表結果 301 轉往新站；程式碼片段展示正規式比對與 Server.Transfer 流程。

### 結語與後續計畫
搬遷工作雜而不難，一週完成資料與連結全數到位；下一篇將專注版面客製與 FunP 推推王整合，敬請期待。