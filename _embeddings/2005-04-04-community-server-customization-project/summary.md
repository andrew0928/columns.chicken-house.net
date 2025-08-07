# community server 改造工程

## 摘要提示
- TextEditorWrapper: 重新撰寫 TextEditorProvider 以全面開放 FTB 3.0 進階編輯功能。  
- 圖片藝廊: 啟用「Insert Image From Gallery」讓 Blog 與 Forum 可直接上傳並插入圖片。  
- 表情符號列: 於 FTB 3.0 介面新增一列 Emotion Icons 供使用者一鍵插入。  
- 相簿批次上傳: 自行撰寫 Web Service 與 CLI 工具，支援圖片縮圖後的批次傳輸與自動建立相簿。  
- 首頁重構: 以 ASP.NET 控制項取代預設首頁文字區，集中顯示 gallery / blogs / forums。  
- Blog 列表化: 將部落格首頁改為列表檢視，並將文章內容改為點擊後才展開全文。  
- 客製化需求: 依「太座」意見調整 UI 及閱讀體驗，確保家用環境滿意度。  
- 系統滿意度: 所有改造項目完成後，作者對 Community Server 整體使用感到成就。  
- 後續計畫: 下一步將把傳統 ChickenHouse Forum 資料遷移進 Community Server。  

## 全文重點
作者自安裝 Community Server 1.0 RTM 起，持續針對其不足之處進行改造。首先透過自行撰寫的 TextEditorProvider，完整開啟 FTB 3.0 內建但預設關閉的高階編纂功能；並進一步啟用「Insert Image From Gallery」，讓使用者能像在 Office 多媒體藝廊般直接上傳、插圖。為提升互動性，又額外打開 Emotion Icons 工具列，簡化表情符號插入程序。

針對影像管理，作者發現 CS 缺乏批次上傳機制，遂建立 Web Service 與命令列工具：本機照片可自動縮圖、同時傳輸，且能動態生成相對應的群組與相簿，大幅提升相片發佈效率。

介面層面，原始首頁佈滿文字說明，不符實際需求，因此以 ASP.NET Controls 重新布局，改為直接展示 Gallery、Blogs、Forums 三大區塊；Blog 首頁亦重構為列表檢視，文章僅展示標題須點擊後閱讀全文，滿足家人閱讀習慣。

透過上述五大改造，作者終於讓家人與自身對 Community Server 的不滿幾乎清零，並對完成度頗感欣慰。接下來的工作重心，將轉向把舊有 ChickenHouse Forum 的資料移轉至新平台，完成整體社群服務的升級與整合。

## 段落重點
### 前言與動機
安裝 Community Server 1.0 後，作者發現其功能與介面無法滿足家用需求，因此展開一連串客製化改造，目標是修正缺點並加入所需新功能。

### TextEditorWrapper 全面升級
預設 CS 僅開啟 FTB 3.0 基本功能；作者重新撰寫 TextEditorProvider，在系統掛載後即可一次解鎖所有進階編輯選項，包含字型、色彩、表格與程式碼標示等，讓版主與使用者皆能享受完整 WYSIWYG 體驗。

### 啟用 Insert Image From Gallery
FTB 3.0 內建的圖庫功能原被隱藏，經作者研究後成功嵌入 Blog 與 Forum 的張貼介面。使用者可先上傳多張圖片，再於編輯器中挑選插入，流程類似 Office Media Gallery，提升圖文混合效率。

### Emotion Icons 工具列
為增加貼文表情豐富度，作者開啟 FTB 3.0 隱藏的 Emotions Toolbar。點擊任一圖示即可即時插入對應表情符號，不必再手動輸入表情碼。

### 相簿批次上傳解決方案
Community Server 原生僅支援單張照片上傳，對大量相片分享相當不便。作者設計 Web Service API，並撰寫命令列工具，可對本機相片批次縮圖、上傳，同時自動建立群組及相簿結構，極大化作業效率。

### 首頁與 Blog 介面重構
1. 首頁：捨棄冗長文字說明，改以 ASP.NET 控制項整合展示 Gallery、Blogs、Forums，入口資訊一目了然。  
2. Blog 首頁：改成純列表模式；Blog 文章頁則僅顯示標題與摘要，需點擊才能讀完整內容，以精簡版面並符合家人閱讀偏好。

### 完工心得與後續計畫
完成五大項改造後，作者及家人均對新系統滿意，並表示有十足成就感。下一階段將著手把舊 ChickenHouse Forum 資料遷移到 Community Server，以完成社群平台全面升級。