# [RUN! PC] 2010 五月號 ─ TxF 讓檔案系統也能達到交易控制

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 作者的新文章登在哪一期的 RUN! PC？
2010 年五月號。

## Q: 這一系列文章的主題是什麼？
主題是 Transactional NTFS (TxF)，也就是讓 Windows 檔案系統具備交易 (Transaction) 控制能力的技術。

## Q: 為什麼作者決定從「執行緒技巧」系列轉換到 TxF 主題？
.NET Framework 4.0 已大幅簡化了多執行緒程式設計，自己手動操作 Thread 的需求變少；因此作者改寫自己更感興趣、且國內資料較少的 Transactional NTFS。

## Q: 新系列第一篇主要介紹哪些內容？
第一篇先講解 TxF 的觀念以及如何快速上手。

## Q: 作者提到的範例程式碼在哪裡可以下載？
可從 /wp-content/be-files/TransactionDemo.zip 下載 Visual Studio 2008 (C#) 專案。

## Q: 針對較零碎的 P/Invoke 等實作細節，作者打算如何分享？
這類較瑣碎的技巧會直接貼在作者的部落格。

## Q: 作者推薦了哪些延伸閱讀或工具來深入了解 TxF？
1. AlphaFS 專案 (CodePlex)  
2. MSDN Magazine 2007/7〈Enhance Your Apps With File System Transactions〉  
3. Bart Desmet 的三篇 TxF 系列文章  
4. CodeProject 文章〈Windows Vista TxF / TxR〉  
5. MSDN Blog「Because we can」  
6. MSDN 文件：Performance Considerations for Transactional NTFS  
7. MSDN 文件：When to Use Transactional NTFS