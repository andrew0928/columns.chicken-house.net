離上一篇有營養的 post 已經隔好久了, 中間都是貼些五四三的, 哈哈... 今天再來貼點跟 .net development 有關的心得...

這篇要講的, 就是想做的像一般壓縮軟體, 可以把壓縮檔包成一個可執行檔, 這個執行檔包含解壓縮的程式, 同時也包含你自己資料, 包成單一執行檔無論攜帶或保存, 甚至隨時要解開都很方便...

看起來很普通的功能, 沒想到要實作起來還真麻煩... 一般標準的開發工具沒辦法產出這樣的 code, 頂多在 compile time 把一些資料當成 resource, 一起 compile 進 exe 內部. 不過即使如此, 這些動作都是在開發階段就完成的, 跟一般自解壓縮檔不同, 是執行階段才完成的...

跟同事討論了一下, 同事就土法練鋼, 試了第一種作法: 直接把 data 附加在 .exe 的後面.

出乎意料的, 這個方法竟然可行, 而且執行也沒有問題, 不過心裡就是毛毛的...

1. 
   1. *"是剛好嗎? 會不會以後就突然不行了?"*
   2. *"這作法好像病毒喔, 會不會被防毒軟體檔下來?"*
   3. *"這種作法能通過 PEVerify 檢查嘛?"*
   4. *"以後加上 signature, 還能執行嘛?"*
   5. *"....."*

上面的動作, (1), (2) 還沒碰到. (3) 對於沒有簽章過的可以, (4) 沒去試.. 不過為了免除這些疑慮, 只好朝向其它較 "正規" 的作法... 從官方的工具著手.

為了避免第一種作法的疑慮, 整個流程到最後產出 .exe 為止, 都必需用官方認可的作法, 所以我能做的動作只剩下把原本很簡單的動作盡量拆解, 盡量拆到只留最後一步, 其它可以先作的一次做掉, 留最後一步在 runtime 時才呼叫外部工具來執行.

原本很簡單的 windows application project, 在裡面加上 embedded resource, build 就可以搞定的事, 現在必需這樣做:

1. 除了要外加的 embedded resource 之外, 其它的部份先用 csc.exe 編譯成 module
2. 把 (1) 編譯好的 module 跟外加的 file(s), 用 al.exe 產出一份完整的 .net assembly (.exe)

其中 (1) 的部份可以事先作好, 未來在執行時就不用再重複 (1) 的步驟, 只要拿 module file 不斷的搭配不同的 embedded resource 就可以產出包含不同 data 的 exe file, 就像典型的自解壓縮檔那樣. 我簡單寫了一個 sample code, 試了一下, 可行. 有興趣的人可以[抓去研究看看](/wp-content/be-files/StartApp.zip)... 我的作法是:

1. 開一個 VS2005 的 windows application project: StartApp, 程式內容很簡單, 就是把 name 為 "attachment" 的 resource 存成暫存檔, 然後用 shell execute 去開啟它, 開完後把暫存檔砍掉, 程式結束.

2. 這個 project 不能 build, 得另外寫 command line 把它編譯成 module (start.module):  
   ```
   csc.exe /out:startup.module /t:module /recurse:*.cs /resource:Form1.resx
   ```

3. (2) 產出的 start.module 搭配圖檔 paint.jpg, 藉由 assembly linker 把它們結合成單一的可執行檔 (start.exe):  
   ```
   al.exe /embed:paint.jpg,attachment /t:exe start.module /out:start.exe /main:StartApp.Program.Main
   ```

大功告成! 產出的 start.exe 執行之後, 按下 [RUN] 就自動開啟圖檔, 就像你直接在 paint.jpg 上按兩下一樣... 完全達到我的期望 :D

這個作法看起來比較好, 因為產出的過程完全都是正式的作法, 不大會有什麼問題, 但是它也有缺點... Orz

1. Visual Studio 2005 的各種 project type, 並沒有包含 module 這種類型... 查了一下, 它只有在講解 .net 內部架構, SDK, 跟 assembly 等基礎知識的地方有提到... 除了直接用 csc.exe 之外, 沒有很簡單的工具可以產出 module... 這對未來要進行 daily build 就有點頭痛了...

2. csharp compiler (csc.exe) 還好, 只要有 CLR 就有, 但是 assembly linker (al.exe) 就麻煩了, 在我的 windows 2003 x64 裡竟然找不到, 查了一下這個要裝 .net framework sdk 才有. 當場去 download 回來裝, 哇靠... 380mb... 傻眼... 這個環境要求稍微高了點, 通常客戶的環境都會裝 .net runtime, 但是不會裝 .net sdk ...

3. 另一個麻煩是, 要執行這些工具, 最少要有基本的權限... 我是要透過 asp.net web application 執行上面這串動作, 要突破的 security 限制還不少...

4. 這些工具目前還查不到對等的 class library 可以簡單的達成一樣的目的, 沒事去拿 MSBuild 裡內建的那堆 task 反組譯看看, CSC / AL 這兩個 task, 通通都是 create process, 然後直接去呼叫 csc.exe / al.exe ... 這種動作對 web application 的效能很具殺傷力... 得改成批次執行, 對系統會好一些, 只是這樣就失去了即時產出的時效性了

試到這邊, 暫時想不到其它作法了, 沒想到要產出自定的 .exe 還真不容易... 如果有其它更好的作法, 就通知一下吧, 真的這樣在 web app 搞下去真是自找苦吃 :~~~