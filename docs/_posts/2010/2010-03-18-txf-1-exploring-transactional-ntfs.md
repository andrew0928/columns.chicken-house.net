---
layout: post
title: "[TxF] #1. 初探 Transactional NTFS"
categories:
- "系列文章: 交易式 (Transactional) NTFS"
tags: [".NET","C#","MSDN","SQL","Transactional NTFS","作業系統"]
published: true
comments: true
redirect_from:
  - /2010/03/18/txf-1-初探-transactional-ntfs/
  - /columns/post/2010/03/18/TxF-1-Transactional-NTFS-e5889de9ab94e9a997.aspx/
  - /post/2010/03/18/TxF-1-Transactional-NTFS-e5889de9ab94e9a997.aspx/
  - /post/TxF-1-Transactional-NTFS-e5889de9ab94e9a997.aspx/
  - /columns/2010/03/18/TxF-1-Transactional-NTFS-e5889de9ab94e9a997.aspx/
  - /columns/TxF-1-Transactional-NTFS-e5889de9ab94e9a997.aspx/
wordpress_postid: 18
---

其實想用 TxF (Transactional NTFS, 交易式的 NTFS) 已經很久了，不過老是被一些雜事卡著，到過年期間才有空好好研究一下。這篇主要是介紹而已，就不講太多 Code, 先以瞭解 TxF 是什麼，及如何善用它等等方面為主。詳細的用法，就等後面幾篇吧!

Transactional NTFS, 中文是 "交易式NTFS"，或是常見到的縮寫 "TxF"，早期的相關文章也有人寫 "TxFS"。這是在 Windows Vista / 2008 推出時，首次正式提供的功能。雖然它叫作 Transactional **NTFS**, 實際上它並不是一個新的檔案系統，而是一組新的 API (跟原有的檔案處理 API 幾乎是一對一的對應),  支援你用交易的方式操作檔案。一起推出的還有 Transactional Registry (TxR)，一樣是有對應的 windows API，只不過它處理的對像是 windows registry，不是檔案...。

用這種方式處理檔案的讀寫動作，有種很神奇的感覺，過去都只在資料庫裡有機會這樣用，現在檔案的處理也可以了。配合像是 DTC 這類交易協調器的支援，甚至可以把檔案的處理及資料庫的處理，通通都包裝成一個交易來進行，一但任何一個環節失敗，都可以回復到最初的狀態，感覺好像是在用 DB，而不是寫檔案... 目前官方並沒有推出 managed code 的含式庫，現在要用只有幾種選擇:

1. 直接用 C / C++ 呼叫 win32 api
1. 用 P/Invoke，在 C# 裡呼叫 win32 api
1. 找那些別人 (非官方) 包裝好的 .net class library ..

這些用起來都有點不踏實，畢竟用 P/Invoke 不是長久之計，總覺的遲早會被替換掉。不過即使如此，這項還是掩蓋不了這技術的價值。我貼一段自己寫的 sample code，讓還沒用過的人體會一下，寫檔案還支援交易處理的 "爽度" ...




```csharp 
// 建立 KTM transaction object
IntPtr transaction = CreateTransaction(
    IntPtr.Zero,
    IntPtr.Zero,
    0, 0, 0, 0,
    null);

string[] files = new string[] {
    @"c:\file1.txt",
    @"c:\file2.txt",
    @"c:\file3.txt"};

try
{
    foreach (string file in files)
    {
        // 使用支援交易的 delete file API
        if (DeleteFileTransactedW(file, transaction) == false)
        {
            // 刪除失敗
            throw new InvalidOperationException();
        }
    }

    // 認可交易
    CommitTransaction(transaction);
}
catch (Exception ex)
{
    // 還原交易
    RollbackTransaction(transaction);
}
CloseHandle(transaction);
```            


 

範例裡用到的幾個 method, 像是 ```CreateTransaction()```, ```DeleteFileTransactedW()```, ```CommitTransaction()```, ```RollbackTransaction()``` ... 等等，都是透過 P/Invoke 的方式呼叫的 win32 api... 除了用的型別不如 pure .net class library 般直覺之外，這樣的 code 也已經很簡單了，短短卅行就可以搞定...

雖然這樣的 code 實在不大合我胃口，但是它畢竟是個堪用的方案... 對於 code 有潔癖的，可以考慮其它的用法。前面是最基本的 API call，如果你不滿意，MS自家的技術 [DTC](http://en.wikipedia.org/wiki/Distributed_Transaction_Coordinator) (Distributed Transaction Coordinator) 當然也支援 TxF。DTC 可以提供額外的好處，就是允許你做分散式的交易管理。意思是你配合 DTC，就可以把 Local File I/O 跟 database access 整合在同一個交易範圍內。

這邊的 sample code 我就不貼了，在 managed code 裡去呼叫到 COM 的那堆介面 (啥 ```QueryInterface``` 的) 實在跟 .NET programming 的 style 有點格格不入... 在 C# 的世界裡，應該用 ```TransactionScope``` 才對。在 MS 的世界裡，TxF + TxR + DB 都可以是 ```TransactionScope``` 內的一部份。這部份的 Sample Code 我一樣先不貼了，不然貼一堆 code 又沒篇幅說明，感覺很混...

其實，MS 該做的都做了，唯一缺的就是它竟然沒正式的併入 .NET Framework 內的一員... 如果 TxF 真的是你想用的東西，倒是有個 OpenSource Project 可以考慮一下: AlphaFS, 它的目標是能替換掉 namespace System.IO.*, 所以很多你常用的 class library, 它都有對等一樣用法的版本，當然它提供了更多的功能及改善... 其中 TxF 的支援就在內，你想用 TxF 來開發軟體的話，這是個不錯的選擇...

總之，這篇只是個開始，目的是想先 "預覽" 一下 TxF 的能耐，及未來它配 DTC / ```TransactionScope``` 後，能怎麼應用它的方式，還有其它可用的相關資源。接下來我會陸續整理一些相關的研究心得.. (別太期待，大概一兩週生一篇就很偷笑了 XD)，下回見 !

 

 







參考資訊:
1. AlphaFS: Brining Advanced Windows FileSystem Support to .NET  
[http://alphafs.codeplex.com/](http://alphafs.codeplex.com/)
1. MSDN magazine (July 2007): Enhance Your Apps With File System Transactions  
[http://msdn.microsoft.com/en-us/magazine/cc163388.aspx](http://msdn.microsoft.com/en-us/magazine/cc163388.aspx)
1. B# .NET BLOG: Windows Vista - Introducing TxF In C#  
Part 1: [Transacted File Delete](http://community.bartdesmet.net/blogs/bart/archive/2006/11/05/Windows-Vista-_2D00_-Introducing-TxF-in-C_2300_-_2800_part-1_2900_-_2D00_-Transacted-file-delete.aspx)  
Part 2: [Using System.Transactions and the DTC](http://community.bartdesmet.net/blogs/bart/archive/2006/11/19/Windows-Vista-_2D00_-Introducing-TxF-in-C_2300_-_2800_part-2_2900_-_2D00_-Using-System.Transactions-and-the-DTC.aspx)  
Part 3: [CreateFileTransacted Demo](http://community.bartdesmet.net/blogs/bart/archive/2007/02/21/windows-vista-introducing-txf-in-c-part-3-createfiletransacted-demo.aspx)
1. Code Project: Windows Vista TxF / TxR  
[http://www.codeproject.com/KB/vista/KTM.aspx](http://www.codeproject.com/KB/vista/KTM.aspx)
1. BLOG: Because we can  
[http://blogs.msdn.com/because_we_can/archive/2005/05/18/419809.aspx](http://blogs.msdn.com/because_we_can/archive/2005/05/18/419809.aspx)  
Discussion and explanation relating to the Transactional NTFS feature coming in Longhorn, plus any other interesting anecdotes... 
1. Performance Consoderations for Transactional NTFS  
[http://msdn.microsoft.com/en-us/library/ee240893(VS.85).aspx](http://msdn.microsoft.com/en-us/library/ee240893(VS.85).aspx)
1. When to Use Transactional NTFS  
[http://msdn.microsoft.com/en-us/library/aa365738(VS.85).aspx](http://msdn.microsoft.com/en-us/library/aa365738(VS.85).aspx)
