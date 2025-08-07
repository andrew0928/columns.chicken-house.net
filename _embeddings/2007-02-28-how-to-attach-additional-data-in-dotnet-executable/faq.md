# 如何在執行檔 (.NET) 裡附加額外的資料?

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 在 .NET 中，如果想要把額外資料與解壓程式包成單一可執行檔，有哪兩種主要做法？
1. 直接把資料「硬塞」到現成的 .exe 檔結尾。  
2. 走官方流程：先把程式編成 module，再用 Assembly Linker (al.exe) 把 module 與欲嵌入的檔案一起組成新的 .exe（並把檔案標成 embedded resource）。

## Q: 直接把資料附加在 .exe 後面可行嗎？會有哪些疑慮？
可行，執行時也正常；但會擔心：  
• 未來 CLR 更新後會不會失效  
• 是否像病毒行為而被防毒軟體攔下  
• 這樣的檔案能否通過 PEVerify  
• 若日後替組件加簽章 (signature) 是否還能跑

## Q: 官方較「正規」的實作流程是什麼？
1. 先用 csc.exe 將程式碼編譯成 module，例如：  
   `csc.exe /out:start.module /t:module /recurse:*.cs /resource:Form1.resx`
2. 將 (1) 產生的 module 與要內嵌的檔案（如 paint.jpg）用 al.exe 合成可執行檔：  
   `al.exe /embed:paint.jpg,attachment /t:exe start.module /out:start.exe /main:StartApp.Program.Main`
3. 執行 start.exe 即可在 Runtime 解開並開啟 paint.jpg，完成「自解壓縮」效果。

## Q: 實作這個流程需要用到哪些工具？一般環境都會有嗎？
• csc.exe：隨 .NET Runtime 就有，幾乎任何裝有 CLR 的機器都找得到。  
• al.exe：只隨 .NET Framework SDK 提供，必須另外安裝（約 380 MB），多數客戶端機器預設並沒有。

## Q: 使用 module + al.exe 這套流程，有哪些明顯缺點？
1. Visual Studio 本身沒有「module 專案」類型，開發與 Daily Build 需額外寫批次檔或腳本。  
2. 目標機器要裝到 .NET SDK 才有 al.exe，部署門檻較高。  
3. 若在 ASP.NET Web 應用程式中動態呼叫外部 exe，會面臨權限與安全性限制。  
4. 呼叫外部製品 (csc/al) 會 Spawn Process，對 Web 站臺效能有殺傷力，只能改成離線批次生成，失去即時產生的彈性。

## Q: 範例程式 StartApp 做了什麼？
StartApp 會從自身的 embedded resource 取出名稱為「attachment」的檔案，存至暫存目錄後用 ShellExecute 開啟，待程式結束再將暫存檔刪除；因此把任何檔案指定給 /embed:xxx,attachment 就能做成專屬的「自解檔」exe。