---
layout: post
title: "[TxF] #2. 先作功課 - 熟悉 P/Invoke 及 Win32 檔案處理..."
categories:
- "系列文章: 交易式 (Transactional) NTFS"
tags: [".NET","C#","MSDN","Transactional NTFS"]
published: true
comments: true
redirect_from:
  - /2010/03/23/txf-2-先作功課-熟悉-pinvoke-及-win32-檔案處理/
  - /columns/post/2010/03/23/TxF-2-e58588e4bd9ce58a9fe8aab2-e7869fe68289-PInvoke-e58f8a-Win32-e6aa94e6a188e89995e79086.aspx/
  - /post/2010/03/23/TxF-2-e58588e4bd9ce58a9fe8aab2-e7869fe68289-PInvoke-e58f8a-Win32-e6aa94e6a188e89995e79086.aspx/
  - /post/TxF-2-e58588e4bd9ce58a9fe8aab2-e7869fe68289-PInvoke-e58f8a-Win32-e6aa94e6a188e89995e79086.aspx/
  - /columns/2010/03/23/TxF-2-e58588e4bd9ce58a9fe8aab2-e7869fe68289-PInvoke-e58f8a-Win32-e6aa94e6a188e89995e79086.aspx/
  - /columns/TxF-2-e58588e4bd9ce58a9fe8aab2-e7869fe68289-PInvoke-e58f8a-Win32-e6aa94e6a188e89995e79086.aspx/
wordpress_postid: 17
---

其實這篇是多寫的，因為[前一篇](/post/TxF-1-Transactional-NTFS-e5889de9ab94e9a997.aspx)提到的 Transactional NTFS 官方只提供 Win32 API 而已，不提供包裝好的 managed code 用的 library... 因此現階段想始用它，[P/Invoke](http://msdn.microsoft.com/en-us/library/aa446536.aspx) 是逃不掉的... 這篇就先來複習一下，想要在 C# 裡呼叫 unmanaged code 該怎麼用吧。這邊的例子為了配合後面幾篇，就同樣的以檔案處理為例。

這篇我不想去長篇大論的討論 P/Invoke 那堆規則及語法，也不想去討論那堆 Marshal 的觀念等等... 想學好 P/Invoke 就別看我這篇了，應該去 MSDN 看... 這篇我只想交待一下該如何配合 windows api 來作檔案處理而已。因為這些是往後要用到 Transactional NTFS 必要的技巧，TxF 新的 API 都是跟 win32 標準檔案處理的 API 一一對應的，弄懂了如何用 win32 api 操作檔案，你大概就學會八成的 TxF 了... 想用 TxF ... 熟悉點 P/Invoke 是應該的...

先從最單純的 [MoveFile](http://msdn.microsoft.com/en-us/library/aa365239(VS.85).aspx) 開始吧，它沒有扯到啥 pointer 或是 handle ... 算是最單純的例子.. 先來看看這 API 原生的樣子:

`BOOL WINAPI MoveFile( __in LPCTSTR lpExistingFileName, __in LPCTSTR lpNewFileName );`

這 API 做啥事就不用多說了，把 lpExistingFileName 這檔案搬到 lpNewFileName 去... 搬成功還是失敗，就用 BOOL 值把結果傳回來。這時就要透過 P/Invoke 的用法，想辦法產生一個可以對應到 unmanaged code 的 C# function ... 我先把宣告方式貼出來，再來解試 code ...

**P/Invoke: MoveFile**

```csharp
[DllImport("kernel32.dll")]
static extern bool MoveFile(string lpExistingFileName, string lpNewFileName);
```

寫過 C / C++ 的人，大概對 [extern](http://msdn.microsoft.com/zh-tw/library/e59b22c5.aspx) 這個 keyword 不陌生吧? extern 這修飾字代表這個 function 是外來的，C# 正好拿來用在這裡。外來的 DLL 都是 function 型態，所以一定是 static, 沒有綁著任何一個物件... 而標在上面的 Attribute: [DllImport](http://msdn.microsoft.com/zh-tw/library/aa984739(VS.71).aspx), 則是標上這個 function 是來自那個 DLL。

在這個例子裡，這樣就足夠了，直接在程式裡試著寫一段 C# (managed code) 來試看看結果吧:

**P/Invoke Sample #1. MoveFile**

```csharp
public class PInvokeTest
{
    [DllImport("kernel32.dll")]
    static extern bool MoveFile(string lpExistingFileName, string lpNewFileName);

    public static void Main(string[] args)
    {
        string srcFileName = @"C:\file1.txt";
        string dstFileName = @"C:\file2.txt";

        Console.Write("move file: from [{0}] to [{1}] ... ", srcFileName, dstFileName);

        if (MoveFile(srcFileName, dstFileName) == true)
        {
            Console.WriteLine("OK!");
        }
        else
        {
            Console.WriteLine("FAIL!");
        }
    }
}
```

程式執行前，看一下 C:\ 的 DIR *.TXT 指令執行結果:

![image](/images/2010-03-23-txf-2-homework-first-pinvoke-and-win32-file-handling/image_6.png)

沒錯，有 c:\file1.txt 這檔案... 接著來執行範例程式:

![image](/images/2010-03-23-txf-2-homework-first-pinvoke-and-win32-file-handling/image_7.png)

執行成功。再重新看一下 C:\ 的 DIR *.TXT 指令執行結果:

![image](/images/2010-03-23-txf-2-homework-first-pinvoke-and-win32-file-handling/image_8.png)

看來程式很順利的呼叫了 win32 api 裡定義的 MoveFile( ... ) ... 這種範例有點不入流，要處理檔案總不可能只有這樣吧? 接著我們再來看看需要 Open File 加上讀寫檔案內容的應用。

Windows 是個以 HANDLE 為主的作業系統，一般在寫 C / C++ 程式，都是以指標(POINTER)的方式在處理資料，但是在 windows 裡，作業系統提供的資料用的指標，則特別以 "HANDLE" 來稱呼，它比一般的 POINTER 來說多了一些管理的動作。因此你開啟的檔案，或是建立的視窗，通通都以 HANDLE 來稱呼，而不是單純的用 POINTER (雖然它也是個 POINTER 啦)。接下來的例子就來看看 HANDLE 的應用。

```csharp
public class PInvokeTest2
{
    [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Auto)]
    public static extern IntPtr CreateFile(
           string lpFileName,
           uint dwDesiredAccess,
           uint dwShareMode,
           IntPtr SecurityAttributes,
           uint dwCreationDisposition,
           uint dwFlagsAndAttributes,
           IntPtr hTemplateFile
           );

    [DllImport("kernel32.dll", SetLastError = true)]
    static extern bool CloseHandle(IntPtr hObject);

    public static void Main(string[] args)
    {
        IntPtr pFile = CreateFile(
            @"c:\file1.txt",
            0x80000000,
            0x00000001,
            IntPtr.Zero,
            3,
            0,
            IntPtr.Zero);

        Stream fs = new FileStream(pFile, FileAccess.Read);
        TextReader tr = new StreamReader(fs);

        Console.WriteLine(tr.ReadToEnd());

        tr.Close();
        fs.Close();
        CloseHandle(pFile);
    }
}
```

這個例子裡，很 "神奇" 的把 unmanaged code 拿到的指標 (IntPtr), 丟給 System.IO.* 底下的 FileStream 來用，竟然還能成功的開啟檔案並且把資料讀出來... 沒錯，MS寫的東西本來就都是同一家人，System.IO 那堆東西就是這樣包出來的。 這段範例程式除了看起來複雜一點之外，跟那堆要查文件才知道是啥意思的 flags 之外，其它都很簡單，不過就 Open File, 然後讀出內容，接著 Close ...

較特別的是，在 P/Invoke 的世界裡，都用 struct System.IntPtr 這個型別，來代表 unmanaged 世界裡常用到的 POINTER.. 藉著這個型別，我們就可以把兩個世界的橋樑給搭起來。不過當你執行這個範例時，編譯器會給你一個很礙眼的警告:

> *'System.IO.FileStream.FileStream(System.IntPtr, System.IO.FileAccess)' is obsolete: 'This constructor has been deprecated. Please use new FileStream(SafeFileHandle handle, FileAccess access) instead. [http://go.microsoft.com/fwlink/?linkid=14202'](http://go.microsoft.com/fwlink/?linkid=14202')*

沒錯，這是老用法了，一如用指標有數不盡的缺點，新的語言都想盡辦法扔掉它 (POINTER: 我是無辜的...)，連包裝過的 IntPtr 也不例外。在 .NET Framework 2.0 裡就不再建議你用這個建構式了，請改用 SafeFileHandle .... 既然在 windows 的世界裡，一切系統的資源都是以 HANDLE 來處理，自然的在 managed code 裡也有對應的型別，它就是 [System.Runtime.InteropServices.SafeHandle](http://msdn.microsoft.com/zh-tw/library/system.runtime.interopservices.safehandle(v=VS.90).aspx) 。接著再來看看改用 SafeHandle 的版本:

```csharp
public class PInvokeTest3
{
    [DllImport("Kernel32.dll", SetLastError = true, CharSet = CharSet.Auto)]
    static extern SafeFileHandle CreateFile(
        string fileName,
        uint fileAccess,
        uint fileShare,
        IntPtr securityAttributes,
        uint creationDisposition,
        uint flags,
        IntPtr template);

    public static void Main(string[] args)
    {
        SafeFileHandle pFile = CreateFile(
            @"c:\file1.txt",
            0x80000000,
            0x00000001,
            IntPtr.Zero,
            3,
            0,
            IntPtr.Zero);

        Stream fs = new FileStream(pFile, FileAccess.Read);
        TextReader tr = new StreamReader(fs);

        Console.WriteLine(tr.ReadToEnd());

        tr.Close();
        fs.Close();

        pFile.Close();
    }
}
```

執行的結果，當然也是順利的把文字檔內容印到 CONSOLE 裡了，我就不再多貼，直接看程式碼。

其實這裡有點偷吃步，用的是 SafeFileHandle, 而不是 SafeHandle。雖然兩者有繼承關係啦。不過後面我就都把它當成 SafeHandle 看待。這個版本的程式，除了把 IntPtr 換成 SafeFileHandle 之外，及最後的 CloseHandle( pFile ) 改成直接呼叫 SafeHandle.Close( ) 之外，沒有太大的不同了。有啦，把 IntPtr 跟 CloseHandle 兩者包裝在同一個 SafeHandler 裡是[安全](http://msdn.microsoft.com/zh-tw/library/fh21e17c(v=VS.90).aspx)的多，至少 SafeHandle 實作了 IDispose 的介面，在適當的情況下，它至少會自動的被呼叫 Dispose( ) 回收資源...

看到這裡，以前老搞不清楚的 FileStream 為什麼有幾個怪怪的 constructor, 自從研究了 TxF 之後，意外的晃然大悟... 算是額外的收穫吧! 原來就是要配合 P/Invoke 使用...

其實說穿了，呼叫 win32 api 大概就這幾招了，幾種 unmanaged code 裡用到的型別，指標都可以對應之後，程式寫起來就簡單了。這篇我特意漏掉一部份，就是各種用 uint 來當作 flags 的型別，沒有轉到對應的 enum 列舉型別，我是覺的這是 option 啦，畢竟查查文件就有，多列上來我得多打好多字... 篇幅有限 XD

這幾個例子如果都看懂後，那麼 TxF 就沒有障礙了! 接下來就看下回分解了 :D 下回會看到第一個 "交易式" 的檔案處理範例! 沒灌 windows vista / 2008 / 7 / 2008 R2 的讀者門，快去準備吧!

參考資訊:

1. 有用的網站: PINVOKE.NET
   [http://www.pinvoke.net/index.aspx](http://www.pinvoke.net/index.aspx)

   這網站幫你整理好了各種 win32 api 該如何宣告它的 C# signature, 以供 p/Invoke 使用。如果你不熟它的語法，這網站可以幫你不少忙。另外它也提供了一些方便的工具，像是 winform 的查詢工具，或是 visual studio 用的 add-ins

2. MSDN 的 API 說明: MoveFile
   [http://msdn.microsoft.com/en-us/library/aa365239(VS.85).aspx](http://msdn.microsoft.com/en-us/library/aa365239(VS.85).aspx)

3. 什麼是 P/Invoke ? Wiki 的說明:
   [http://en.wikipedia.org/wiki/Pinvoke](http://en.wikipedia.org/wiki/Pinvoke)

4. Safe Handle & Critical Finalization
   (實在是看不懂的中譯... "安全控制代碼和關鍵結束" ???)
   [http://msdn.microsoft.com/zh-tw/library/fh21e17c(v=VS.90).aspx](http://msdn.microsoft.com/zh-tw/library/fh21e17c(v=VS.90).aspx)
