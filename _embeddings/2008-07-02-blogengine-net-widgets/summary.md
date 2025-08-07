# BlogEngine.NET Widgets 功能心得

## 摘要提示
- Widgets 概念: BlogEngine.NET 1.4 新增可拖拉的小工具，讓版面配置更自由。
- 開發容易: 只要繼承指定類別、放進 ~/Widgets/ 目錄，就能完成一個可用的 widget。
- Flickr 範例: 透過 FlickrNet 寫兩個 User Control，即可把相片秀到側欄並提供簡易設定。
- 歷史回顧: 作者從 OLE、OpenDoc 談到物件技術演進，映射到今日 widget 的便利。
- 升版經驗: 部落格剛搬家就遇到 1.4 釋出，只花一兩小時就順利升級。
- 樣板問題: 舊佈景移植後不支援 widgets，後續還需手動調整。
- 開發心情: 功能太簡單反而讓人感嘆，昔日碩士論文研究顯得像寫好玩的。
- 社群資訊: 文章引用 rtur.net 的教學與小熊子的相關討論，顯示資源充足。
- 使用者體驗: 後台直接點選 [EDIT] 即可進入設定介面，操作直覺。
- 物件導向優勢: Widget 之所以易於擴充，全賴 .NET 的 User Control 架構。

## 全文重點
作者原本只想查找 BlogEngine.NET Extension 儲存自訂設定值的方法，卻意外發現 1.4 版新加入的 Widgets 機制。Widgets 就像桌面或網頁上的「小工具」，可透過拖拉快速安置在版面任一區域。回想早年插圖或共用文件需要各種曲折技巧，直到 OLE、OpenDoc 等物件導向技術問世，才真正做到跨應用程式整合。如今在 BlogEngine.NET 上，只需撰寫簡短的 User Control，繼承官方規定的類別，並放進 ~/Widgets/ 資料夾，就能自動出現在後台並支援拖曳、編輯等功能。作者引用 rtur.net 的教學，以 FlickrNet 為例：第一個 User Control 負責抓圖顯示，第二個 User Control 讓使用者輸入 API Key、相簿編號等設定，整體程式碼相當精簡。升級到 1.4 的過程也頗為順利，僅需一兩小時，但原先精心改造的佈景主題並未內建 widget 佈局，勢必再投入時間調整。作者一方面感嘆當年做研究的艱辛，如今卻只要幾行程式就能完成相似功能；另一方面也對 BlogEngine.NET 的易用與彈性表示欣喜，期待未來持續改善版面並充分運用 widgets 帶來的擴充性。

## 段落重點
### 意外發現 BlogEngine Widgets
作者原想找 Extension 設定範例，卻在搜尋過程中挖到 BlogEngine.NET 1.4 新功能——Widgets，驚覺開發門檻之低令人傻眼。

### 小工具與物件技術的歷史聯想
從早期在 ET 手工插圖、到 Windows 3.1 的 OLE、再到 Apple 的 OpenDoc，作者回顧物件導向技術如何逐步讓「把外部元件嵌進文件」變得簡單，並感慨自己的碩士研究如今看來只是玩票。

### FlickrNet 範例與開發流程
引用 rtur.net 的教學，只要撰寫兩個 User Control 分別負責顯示與設定，即可完成 Flickr 相片 widget；程式碼放進 ~/Widgets/ 便自動生效。

### Widgets 帶來的使用者體驗
BlogEngine 1.4 將側欄區塊全面元件化，部落格管理者可在前端拖拉擺放，並透過 [EDIT] 快速修改屬性，操作類似 Web Parts。

### 升級到 1.4 與佈景挑戰
作者在搬站完成後才發現新版釋出，仍成功於短時間內升級；但舊樣板不支援 widget 版面，需重新調整，成為後續待解決的工作。