---
layout: post
title: "x64 programming #1: 環境變數及特殊目錄.."
categories:

tags: [".NET","技術隨筆"]
published: true
comments: true
redirect_from:
  - /2008/07/25/x64-programming-1-環境變數及特殊目錄/
  - /columns/post/2008/07/25/x64-programming-1-e792b0e5a283e8ae8ae695b8e58f8ae789b9e6ae8ae79baee98c84.aspx/
  - /post/2008/07/25/x64-programming-1-e792b0e5a283e8ae8ae695b8e58f8ae789b9e6ae8ae79baee98c84.aspx/
  - /post/x64-programming-1-e792b0e5a283e8ae8ae695b8e58f8ae789b9e6ae8ae79baee98c84.aspx/
  - /columns/2008/07/25/x64-programming-1-e792b0e5a283e8ae8ae695b8e58f8ae789b9e6ae8ae79baee98c84.aspx/
  - /columns/x64-programming-1-e792b0e5a283e8ae8ae695b8e58f8ae789b9e6ae8ae79baee98c84.aspx/
wordpress_postid: 84
---

被 X64 折騰了這麼久，總要留些戰蹟下來... 先從每個人都會碰到的目錄路徑調整開始吧...

有些目錄大家都耳熟能詳，像是 c:\Program Files\ 之類的，不過如果你的程式把這種路徑寫死了，你就要注意了... 因為到了 x64 位元下的 x86 相容模式，路徑就完全不一樣了... 先來看這一段程式執行結果是啥? 別急著看解答，猜一下..

**印出所有 SpecialFolder**

```csharp
Console.WriteLine("Spacial Folder(s):");
foreach (Environment.SpecialFolder value in Enum.GetValues(typeof(Environment.SpecialFolder)))
{
    Console.WriteLine("{0}: {1}", value, Environment.GetFolderPath(value));
}
```

Visual Studio Platform 設定為 x86，在 Vista x64 下執行的結果是:

Spacial Folder(s):  
Desktop: D:\HomeDisk\chicken\Desktop  
Programs: C:\Users\chicken\AppData\Roaming\Microsoft\Windows\Start Menu\Programs  
Personal: D:\HomeDisk\chicken\Documents  
Personal: D:\HomeDisk\chicken\Documents  
Favorites: D:\HomeDisk\chicken\Favorites  
Startup: C:\Users\chicken\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup  
Recent: C:\Users\chicken\AppData\Roaming\Microsoft\Windows\Recent  
SendTo: C:\Users\chicken\AppData\Roaming\Microsoft\Windows\SendTo  
StartMenu: C:\Users\chicken\AppData\Roaming\Microsoft\Windows\Start Menu  
MyMusic: D:\HomeDisk\chicken\Music  
DesktopDirectory: D:\HomeDisk\chicken\Desktop  
MyComputer:   
Templates: C:\Users\chicken\AppData\Roaming\Microsoft\Windows\Templates  
ApplicationData: C:\Users\chicken\AppData\Roaming  
LocalApplicationData: C:\Users\chicken\AppData\Local  
InternetCache: C:\Users\chicken\AppData\Local\Microsoft\Windows\Temporary Internet Files  
Cookies: C:\Users\chicken\AppData\Roaming\Microsoft\Windows\Cookies  
History: C:\Users\chicken\AppData\Local\Microsoft\Windows\History  
CommonApplicationData: C:\ProgramData  
System: C:\Windows\system32  
**ProgramFiles: C:\Program Files (x86)**  
MyPictures: D:\HomeDisk\chicken\Pictures  
**CommonProgramFiles: C:\Program Files (x86)\Common Files**

改成 x64 / Any CPU，在 Vista x64 下執行的結果是:

Spacial Folder(s):  
Desktop: D:\HomeDisk\chicken\Desktop  
Programs: C:\Users\chicken\AppData\Roaming\Microsoft\Windows\Start Menu\Programs Personal: D:\HomeDisk\chicken\Documents  
Personal: D:\HomeDisk\chicken\Documents  
Favorites: D:\HomeDisk\chicken\Favorites  
Startup: C:\Users\chicken\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup  
Recent: C:\Users\chicken\AppData\Roaming\Microsoft\Windows\Recent  
SendTo: C:\Users\chicken\AppData\Roaming\Microsoft\Windows\SendTo  
StartMenu: C:\Users\chicken\AppData\Roaming\Microsoft\Windows\Start Menu  
MyMusic: D:\HomeDisk\chicken\Music  
DesktopDirectory: D:\HomeDisk\chicken\Desktop  
MyComputer:  
Templates: C:\Users\chicken\AppData\Roaming\Microsoft\Windows\Templates  
ApplicationData: C:\Users\chicken\AppData\Roaming  
LocalApplicationData: C:\Users\chicken\AppData\Local  
InternetCache: C:\Users\chicken\AppData\Local\Microsoft\Windows\Temporary Internet Files  
Cookies: C:\Users\chicken\AppData\Roaming\Microsoft\Windows\Cookies  
History: C:\Users\chicken\AppData\Local\Microsoft\Windows\History  
CommonApplicationData: C:\ProgramData  
System: C:\Windows\system32  
**ProgramFiles: C:\Program Files**  
MyPictures: D:\HomeDisk\chicken\Pictures  
**CommonProgramFiles: C:\Program Files\Common Files**

再來看一段 code, 把所有的環境變數印出來:

**印出所有的環境變數..**

```csharp
Console.WriteLine("Environment Variable(s):");
IDictionary evs = Environment.GetEnvironmentVariables();
foreach (string key in evs.Keys)
{
    Console.WriteLine("{0}: {1}", key, evs[key]);
}
```

x86:

Environment Variable(s):  
Path: C:\Windows\system32;C:\Windows;C:\Windows\System32\Wbem;C:\Program Files\Intel\DMIX  
TEMP: C:\Users\chicken\AppData\Local\Temp  
SESSIONNAME: Console  
PATHEXT: .COM;.EXE;.BAT;.CMD;.VBS;.VBE;.JS;.JSE;.WSF;.WSH;.MSC  
USERDOMAIN: CHICKEN-PC  
**PROCESSOR_ARCHITECTURE: x86**  
**ProgramW6432: C:\Program Files**  
TRACE_FORMAT_SEARCH_PATH: [\\NTREL202.ntdev.corp.microsoft.com\34FB5F65-FFEB-4B61-BF0E-A6A76C450FAA\TraceFormat](file://\\NTREL202.ntdev.corp.microsoft.com\34FB5F65-FFEB-4B61-BF0E-A6A76C450FAA\TraceFormat)  
APPDATA: C:\Users\chicken\AppData\Roaming  
windir: C:\Windows  
LOCALAPPDATA: C:\Users\chicken\AppData\Local  
**CommonProgramW6432: C:\Program Files\Common Files**  
TMP: C:\Users\chicken\AppData\Local\Temp  
USERPROFILE: C:\Users\chicken  
**ProgramFiles: C:\Program Files (x86)**  
**CommonProgramFiles(x86): C:\Program Files (x86)\Common Files**  
FP_NO_HOST_CHECK: NO  
HOMEPATH: \Users\chicken  
COMPUTERNAME: CHICKEN-PC  
ProgramData: C:\ProgramData  
**PROCESSOR_ARCHITEW6432: AMD64**  
USERNAME: chicken  
NUMBER_OF_PROCESSORS: 4  
PROCESSOR_IDENTIFIER: Intel64 Family 6 Model 23 Stepping 7, GenuineIntel  
WecVersionForRosebud.1054: 2  
SystemRoot: C:\Windows  
ComSpec: C:\Windows\system32\cmd.exe  
LOGONSERVER: \\CHICKEN-PC  
DFSTRACINGON: FALSE  
**ProgramFiles(x86): C:\Program Files (x86)**  
VisualStudioDir: D:\HomeDisk\chicken\Documents\Visual Studio 2008  
SystemDrive: C:  
**CommonProgramFiles: C:\Program Files (x86)\Common Files**  
PROCESSOR_LEVEL: 6  
PROCESSOR_REVISION: 1707  
PROMPT: $P$G  
ALLUSERSPROFILE: C:\ProgramData  
VS90COMNTOOLS: C:\Program Files (x86)\Microsoft Visual Studio 9.0\Common7\Tools\  
PUBLIC: C:\Users\Public  
OS: Windows_NT  
HOMEDRIVE: C:

x64:

Environment Variable(s):  
COMPUTERNAME: CHICKEN-PC  
VisualStudioDir: D:\HomeDisk\chicken\Documents\Visual Studio 2008  
HOMEPATH: \Users\chicken  
LOCALAPPDATA: C:\Users\chicken\AppData\Local  
USERNAME: chicken  
**PROCESSOR_ARCHITECTURE: AMD64**  
Path: C:\Windows\system32;C:\Windows;C:\Windows\System32\Wbem;C:\Program Files\Intel\DMIX  
**CommonProgramFiles(x86): C:\Program Files (x86)\Common Files**  
**ProgramFiles(x86): C:\Program Files (x86)**  
PROCESSOR_LEVEL: 6  
LOGONSERVER: \\CHICKEN-PC  
HOMEDRIVE: C:  
USERPROFILE: C:\Users\chicken  
SystemRoot: C:\Windows  
TEMP: C:\Users\chicken\AppData\Local\Temp  
WecVersionForRosebud.1054: 2  
PUBLIC: C:\Users\Public  
ALLUSERSPROFILE: C:\ProgramData  
FP_NO_HOST_CHECK: NO  
APPDATA: C:\Users\chicken\AppData\Roaming  
DFSTRACINGON: FALSE  
ProgramData: C:\ProgramData  
PATHEXT: .COM;.EXE;.BAT;.CMD;.VBS;.VBE;.JS;.JSE;.WSF;.WSH;.MSC  
OS: Windows_NT  
CommonProgramFiles: C:\Program Files\Common Files  
PROCESSOR_IDENTIFIER: Intel64 Family 6 Model 23 Stepping 7, GenuineIntel  
ComSpec: C:\Windows\system32\cmd.exe  
TRACE_FORMAT_SEARCH_PATH: [\\NTREL202.ntdev.corp.microsoft.com\34FB5F65-FFEB-4B61-BF0E-A6A76C450FAA\TraceFormat](file://\\NTREL202.ntdev.corp.microsoft.com\34FB5F65-FFEB-4B61-BF0E-A6A76C450FAA\TraceFormat)  
PROMPT: $P$G  
SystemDrive: C:  
PROCESSOR_REVISION: 1707  
ProgramFiles: C:\Program Files  
NUMBER_OF_PROCESSORS: 4  
VS90COMNTOOLS: C:\Program Files (x86)\Microsoft Visual Studio 9.0\Common7\Tools\   
TMP: C:\Users\chicken\AppData\Local\Temp  
SESSIONNAME: Console  
windir: C:\Windows  
USERDOMAIN: CHICKEN-PC

有差異的地方我用紅色的字標出來了，看來程式還真的不能亂寫，那種寫好 RUN 了沒事就交差的人要注意了，哈哈.. 千萬不要雞婆自己湊路徑就是這樣... 其實同樣的狀況發生在好幾個地方，Win32 API 會重新導向， 32/64 用的是不同版本，Registry Key 也會重新導向，File System 也會重新導向...。

不過比較特別的是 c:\windows\system32 這目錄，文件上說會自動重新導向到 c:\windows\syswow64 下 (如果你是在 x64 環境下執行 x86 的程式)，不過上面的例子抓到的路徑依舊是 c:\windows\system32 ( x86 / x64 都一樣 )，甚至是我在 x86 版本寫個檔案到 c:\windows\system32 下，回到 x64 的檔案總管看，它還真的在 c:\windows\system32\ 下...

不過當程式需要載入原本在 c:\windows\system32 下的檔案，或是呼叫到原本 windows 內建在這目錄下的 .dll / .exe 的話，還真的會被重新導向到 c:\windows\syswow64 ... 有興趣的朋友可以自己去這個目錄下逛一逛，該有的檔案都有，不過通通是 32 位元的版本.. 

所以裝 x64 有個缺點，C:\ 會變比較肥... 哈哈，因為什麼東西都擺兩份，Orz...

不過我用的方式都是土法鍊鋼，看起來像自己試出來的... 其實這樣不好，我是亂練的，大家不要學... 要寫 x64 程式的人，MSDN 這一個章節一定要看一下:

**Programming Guide for 64-bit Windows**

[http://msdn.microsoft.com/en-us/library/bb427430(VS.85).aspx](http://msdn.microsoft.com/en-us/library/bb427430(VS.85).aspx)

這個章結的內容不多，翻一翻就看完了，裡面才是正解啊，不要再相信一些沒有根據的說法了... (咳，我又沒禿頭..)，下次來講 IIS6 + x64 碰到的一堆靈異事件...
