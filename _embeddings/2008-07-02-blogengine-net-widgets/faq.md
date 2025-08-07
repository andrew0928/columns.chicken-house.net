# [BlogEngine.NET] Widgets

# 問答集 (FAQ, frequently asked questions and answers)

## Q: BlogEngine.NET 1.4 在 2008/06/30 發佈時，最重要的新功能是什麼？
BlogEngine.NET 1.4 最主要的新功能就是正式加入「Widget」機制，讓側邊欄的各種 Box（例如 Google 廣告、作者介紹、最新回應等）都成為可拖放、可編輯的元件。

## Q: 如果想在 BlogEngine.NET 製作一個自訂 Widget，需要做哪些步驟？
1. 撰寫一個用來顯示內容的 User Control。  
2. 視需要再撰寫一個編輯用的 User Control，處理設定值（例如用幾個 TextBox 讓使用者輸入）。  
3. 讓顯示用的 Control 繼承 BlogEngine.NET 指定的 Widget 基底類別。  
4. 把兩個 .ascx 檔案放進網站的 ~/Widgets/ 目錄。  
完成後，網站管理者就能在版面上拖拉該 Widget 並進入 [EDIT] 畫面設定。

## Q: 這樣做出來的 Widget 在部落格頁面上能做哪些事情？
它會以「Box」的形式出現在側邊欄，部落格主人可以：  
‧ 直接在前端介面拖拉改變位置。  
‧ 點選 [EDIT] 進入編輯用的 User Control 調整設定值。  
‧ 儲存後即時看到修改結果。

## Q: 文中提到的教學範例在哪裡？示範了什麼？
教學位址： http://rtur.net/blog/post/2008/03/24/BlogEngine-Widgets-Tutorial.aspx  
內容示範如何利用 FlickrNet 函式庫寫一個顯示 Flickr 相片的 Widget，並用另一個編輯用 User Control 讓使用者輸入設定值（例如要抓幾張圖）。

## Q: 為什麼作者覺得現在寫 Widget「簡單到想打人」？
因為只要少量的程式碼就能完成以前需大費周章才能做到的「物件嵌入」效果。對照他研究所時期為 OLE／OpenDoc 等物件導向技術寫論文的艱難，如今在 BlogEngine.NET 上寫 Widget 幾乎只是把檔案丟到指定資料夾就能運作，落差之大讓他忍不住自嘲當年論文是「寫好玩的」。