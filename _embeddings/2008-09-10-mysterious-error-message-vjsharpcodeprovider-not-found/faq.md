# 莫明奇妙的錯誤訊息: 找不到 VJSharpCodeProvider ?

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 在 Visual Studio 2008 編譯 BlogEngine.NET 時，為什麼會出現 “The CodeDom provider type 'Microsoft.VJSharp.VJSharpCodeProvider … could not be located.'” 的錯誤？  
只要網站目錄裡出現 .java 原始碼檔 (本文是在 ~/App_Data/files 找到的舊 Java Applet)，Visual Studio 就會嘗試以 VJSharpCodeProvider (J# 編譯器) 來編譯它；若系統上沒裝 Visual J#，就會拋出上述訊息。

## Q: 解決 “找不到 VJSharpCodeProvider” 編譯錯誤的最快作法是什麼？  
將造成問題的 .java 檔刪除或移出網站目錄即可；作者刪除 ~/App_Data/files 中的舊 Java 程式後，編譯立即通過。另一種做法是安裝 Visual J#，但通常不必要。

## Q: ~/App_Data 目錄可以隨意放置任何檔案嗎？  
最好不要。雖然 ASP.NET 將 App_Data 視為資料存放區，Visual Studio 仍會在建置時掃描其中的原始碼檔 (.cs、.vb、.java 等)。放入不相關的程式碼檔可能觸發意料之外的編譯程序，導致錯誤訊息或建置失敗。

## Q: 為什麼錯誤訊息只顯示 “(0)” 而沒有檔名與行號？  
因為 VS 在整體網站的預編譯階段就偵測到需要 J# 編譯器，卻找不到對應提供者，因而立刻失敗；該例外並未對應到任何具體原始檔與行號，故訊息僅顯示 (0)。