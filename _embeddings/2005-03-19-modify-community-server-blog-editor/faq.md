# 修改 Community Server 的 blog editor

# 問答集 (FAQ, frequently asked questions and answers)

## Q: Community Server 的 Blog 文章編輯器實際上採用了哪一套第三方元件？
Community Server 內建的編輯器是包裝（wrapper）了 FreeTextBox 這套 WYSIWYG 編輯器。

## Q: 為什麼在 Community Server 上要修改編輯器會比較麻煩？
因為 Community Server 不是直接引用 FreeTextBox，而是中間再加了一層自家的 Editor Wrapper，而且官方釋出的原始碼並不包含這個 Wrapper。少了這段程式碼，想自訂或延伸功能就必須繞路處理，難度因此提高。

## Q: 作者修改後遇到的主要畫面問題是什麼？
新增的工具列無法併入原本 FreeTextBox 的工具列，只能「格格不入」地顯示在畫面最上方。

## Q: 作者想為編輯器新增哪些常用功能？
作者的目標是讓編輯器能方便地「貼圖」以及插入「表情符號」。

## Q: 作者對 FreeTextBox 還有什麼遺憾或可惜之處？
FreeTextBox 其實還有許多好用的工具列功能可以開啟，但因為受到 Community Server Wrapper 限制，無法順利整合與使用，作者覺得相當可惜。