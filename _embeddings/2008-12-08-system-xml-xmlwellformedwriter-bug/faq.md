# 原來 System.Xml.XmlWellFormedWriter 有 Bug ..

# 問答集 (FAQ, frequently asked questions and answers)

## Q: System.Xml.XmlWellFormedWriter 被發現的 Bug 是什麼？
XmlWellFormedWriter 在呼叫 WriteRaw( ) 時會「再次」對傳入的字串做字元跳脫（把 `<`、`>` 轉成 `&lt;`、`&gt;` 等），導致輸出的內容被雙重編碼，而這與 MSDN 對 WriteRaw( )「應直接輸出原始字串、不做任何處理」的說明不符。

## Q: 使用相同的 WriteRaw( ) 呼叫，XmlTextWriter 與 XmlWellFormedWriter 的輸出差異在哪裡？
• XmlTextWriter：  
　輸出 `<?xml …?><root><a/><a/><a/><a/><a/></root>`，保持原始 `<a/>` 片段不變。  
• XmlWellFormedWriter：  
　輸出 `<?xml …?><root>&lt;a/&gt;&lt;a/&gt;&lt;a/&gt;&lt;a/&gt;&lt;a/&gt;</root>`，把 `<a/>` 片段再次轉成 `&lt;a/&gt;`。

## Q: 為什麼說 XmlTextWriter 的行為才是正確的？
MSDN 文件指出 WriteRaw( ) 應將呼叫端提供的字串「原樣」寫入，不應再進行任何編碼或驗證；XmlTextWriter 符合此規格，而 XmlWellFormedWriter 多做了一次編碼，因此被視為有 Bug。

## Q: 如果想避開這個 Bug，有什麼替代做法？
作者改用「XmlCopyPipe」方法：  
1. 先用 XmlReader 讀取來源片段（經過解析與驗證）。  
2. 再把 XmlReader 讀到的節點逐一寫到目標 XmlWriter。  
此流程完全不依賴 WriteRaw( )，自然就不會觸發 XmlWellFormedWriter 的 Bug。

## Q: 就算沒有這個 Bug，直接呼叫 WriteRaw( ) 也有什麼風險？
WriteRaw( ) 不會替呼叫端驗證內容是否合法；若傳入不合法的 XML 資料，整份輸出檔可能因此損毀，因此本身就屬於高風險 API。

## Q: 如果要用 XmlReader 讀取含有多個 root 的 XML 片段，該如何設定？
將 XmlReaderSettings.ConformanceLevel 設為 `ConformanceLevel.Fragment`，即可讓 XmlReader 正確處理多個 root element 的片段資料。