# community server 改造工程

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 作者針對 Community Server 1.0 做了哪些主要改造與增強？
作者進行了五大改造：  
1. 重新撰寫 TextEditorProvider，全面開啟 FTB 3.0 的進階編輯功能。  
2. 啟用 FTB 3.0 的「Insert Image From Gallery」，讓使用者可像 Office 多媒體藝廊般上傳並插入圖片。  
3. 新增一排可直接插入表情符號的 emotion icons 工具列。  
4. 實作相簿批次上傳：自建 Web Service 並撰寫指令列工具，先在本機縮圖後再上傳，同時自動建立對應的 group／gallery。  
5. 重新設計多個頁面：  
   ‧ 首頁改為以 gallery／blogs／forums 的 ASP.NET Control 顯示。  
   ‧ Blog 首頁改成部落格列表。  
   ‧ 個別 Blog 首頁僅顯示標題，需點入才見全文，以符合家人需求。

## Q: 為什麼要啟用 FTB 3.0 的「Insert Image From Gallery」功能？
因為 FTB 3.0 內建 image gallery，可讓使用者上傳欲插入的圖檔，操作體驗類似 Office 的多媒體藝廊；開啟後，無論發佈 Blog 或 Forum 文章，都能直接使用這項功能，大幅提升貼圖方便性。

## Q: 作者是如何解決 Community Server 相簿缺乏「批次上傳」功能的？
作者自寫一個 Web Service 併入 CS，並依照該 API 開發指令列工具：  
1. 先在本機端將相片批次縮小。  
2. 透過指令列工具呼叫 Web Service 進行上傳。  
3. 系統會自動建立相關的 group 與 gallery。

## Q: 被作者「改掉」的頁面有哪些？改成了什麼樣子？
1. 首頁：原本僅顯示大量文字，改為展示 gallery、blogs、forums 的 ASP.NET 控制項。  
2. Blog 首頁：改為顯示 Blog 列表。  
3. 個別 Blog Homepage：改成只顯示標題，內容需點入才顯示。

## Q: 完成這些改造後，作者的下一步計畫是什麼？
在完成上述改造並獲得「成就感」後，作者打算將舊的「ChickenHouse Forum」資料轉移到新的 Community Server 環境。