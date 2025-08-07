# 如何在執行檔 (.NET) 裡附加額外的資料?

## 摘要提示
- 單一執行檔需求: 將程式與資料包成一檔，方便攜帶與解壓。
- 土法練鋼做法: 直接把資料附加在 .exe 尾端即可執行。
- 安全與相容疑慮: 附加法可能遇到防毒、PEVerify、簽章問題。
- 正規官方流程: 透過 csc 編譯成 module，再用 al 彙整成 exe。
- 兩段式建置: 模組可預先產生，執行期只需替換資源再呼叫 al。
- 建置示範指令: csc /t:module 產 module；al /embed 產 exe。
- VS2005 限制: IDE 不支援 module 專案型別，只能命令列。
- 執行環境門檻: al.exe 隨 .NET SDK 才有，客戶端多半缺乏。
- Web‐App 效能顧慮: ASP.NET 呼叫外部工具需高權限且影響效能。
- 待改進方向: 尋找內建 API 或批次方式，避免即時編譯瓶頸。

## 全文重點
作者想實作一種「自解壓」模式，將 .NET 執行程式與任意資料打包成單一可執行檔，使用者雙擊即可自動解開並執行對應行為。第一種直覺方法是把資料直接加在現成 .exe 的檔尾，實測可行且執行無礙，但對未來的相容性、防毒偵測、PEVerify 以及簽章驗證都充滿疑慮，屬於「能用但心裡不安」的黑客手段。  
為求正規，作者改採微軟官方工具鏈：先用 csc.exe 把程式碼編譯成 .net module，再由 al.exe (Assembly Linker) 把 module 與欲附加的檔案以 /embed 方式封進資源，產出最終 exe。如此即可在執行階段多次重複建立不同資料包，效果類似 WinZip 的自解壓功能。作者以 StartApp 範例示範：1) VS2005 建立簡易 Windows Form 程式，於 Runtime 釋放並開啟名為 attachment 的資源；2) 用 csc 編為 startup.module；3) 用 al 把 module 與 paint.jpg 結合，產生 start.exe。  
雖然流程正式，但也帶來新問題：IDE 不支援 module 專案型別；al.exe 僅隨 .NET SDK 發佈，環境布署體積大；在 ASP.NET 中呼叫外部編譯工具面臨權限與效能瓶頸。作者暫未找到純 API 方案，呼籲若有更佳作法請分享，否則在 Web 環境建置此功能可謂自找苦吃。

## 段落重點
### 專案動機與需求
作者想模仿壓縮軟體的自解壓功能，把解壓邏輯與任意資料包成單一 .NET 執行檔，以便攜帶、存檔與即時解開。市面開發工具多於編譯期嵌入資源，難以在執行期動態插入檔案，因而展開研究。

### 直接附檔尾方法
同事嘗試「把資料直接接在 exe 尾端」的土法練鋼。結果能正常執行，但對未來相容、病毒誤判、PE 驗證與數位簽章皆存疑，屬於不被官方保障的做法，作者心裡仍感不安。

### 使用 csc 與 al 的正式流程
為消除疑慮，作者拆解建置流程：1) 以 csc.exe /t:module 將程式碼編成 module；2) 以 al.exe /embed 將 module 與目標資料彙整成 exe；3) 在程式中把名為 attachment 的資源釋放到暫存路徑並 shell 執行。如此可於執行期多次包裝不同資料，完全符合官方規範。

### 實作範例與步驟
作者提供 StartApp 範例：VS2005 專案只負責釋放資源與呼叫；命令列完成三步：① csc /out:startup.module /t:module /recurse:*.cs /resource:Form1.resx；② al /embed:paint.jpg,attachment /t:exe startup.module /out:start.exe /main:StartApp.Program.Main；③ 執行後按 [RUN] 即自動開啟 paint.jpg。流程證實可行。

### 工具與環境限制
缺點隨之浮現：VS 不支援 module 專案導致日常建置不便；al.exe 僅隨 380MB 的 .NET SDK 發佈，不利客戶端佈署；ASP.NET 執行情境呼叫外部可執行檔需較高權限且增添效能負擔。現階段尚無對等 class library 可替代，若改批次執行雖可減壓但失即時性。

### 結論與徵求更佳方案
作者暫將此流程作為可行折衷方案，但認為在 Web 環境動態產生自解壓 exe 仍屬「自找苦吃」，希望社群有更完善、低門檻且安全的實作技巧，進一步提升開發與佈署體驗。