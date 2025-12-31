---
date: 2025-11-03
datetime: 2025-11-03T23:35:55+08:00
timestamp_utc: 1762184155
title: "AI 轉型，困難的地方在於搭配的流程。因為沒人知道 “AI Native” 的做法是什麼，所以一不小"
---

AI 轉型，困難的地方在於搭配的流程。因為沒人知道 “AI Native” 的做法是什麼，所以一不小心，你就會掉入 “用新工具來套舊流程” 的困境…。

先前我在研究的 side project: vibe testing 就陷到這困境內了, 總覺得我的作法沒有發揮出 AI 真正的潛力。何謂 AI Native? 用對話就是了嗎? 用了 MCP 就是了嗎? 自己刻 UI 呼叫 AI API 就是了嗎? 想想都不大對，直到前陣子開始認真使用 SpecKit, 我才恍然大悟 ..

先講我的心得, 我在每種場合都是把 AI 當作假想的萬能同事，讀的書比我多，做事比我快 10x 以上。對他下的 prompt 就是我該跟他溝通的內容。同事的協作，目標是完成任務，而協作的重心則是 workflow ( #prompt ) .. 協作的過程中, 每一個步驟都要看一下之前做了什麼, 之後需要什麼 ( #context ), 而必要時我們必須善用各種工具 ( #tools ) 來輔助我們 ( #agent ) 來完成任務。

而 SpecKit 的操作方式，我突然想通了，這就是我一直在想的 AI Native 做法。GitHub 團隊很巧妙的把 “SDD (規格驅動開發)" 的流程，拆解成上面這幾個環節，然後包裝成一個 toolkit 上每個人都能很容易地遵循 SDD 的流程，跟你的 Coding Agent 完成任務。

於是，我花了一個晚上，把我的 vibe testing 重新組合了一下，做出我自己的 TestKit 了…, 我用 vscode 來當作整個 "測試" 的執行環境, 把測試拆成這幾個大階段 (就如同 /speckit.xxxx 一樣):

■ /testkit.gentest

第一個步驟，是從驗收條件 AC 來展開需要的測試案例 ( Test Case ), 我用決策表 ( Decision Table ) 來處理。讓 Agent 抓出 Criteria / Action 後, 組合出各種 Rules, 我看表格內容做好調整, 最終定案的 Decision Table 就可以將每個 Rules 展開成獨立的 Test Cases.

■ /testkit.run

有了 Test Case, 而我測試的標的是 API, 因此 Test Case 加上 API Spec, 理論上就能讓 AI 理解要完成 Test Case 該怎麼呼叫 API 來達成了。這邊有很多 API 呼叫的細節要處理，包含認證 (我用 OAuth2 測試)，包含執行的 LOG (我用 REST API)。這些過程很瑣碎，也必須很精準地完成，因此我把它包裝成我的 MCP server ( Text-To-Calls MCP ), 讓 Agent 使用

■ /testkit.gencode

用 AI 執行 test case 是很容易的事情，但是當我要回歸測試，每次發行都想要重跑一次的時候，AI 的缺點就被極度放大了。AI 執行的測試每次都不保證 100% 相同，這對測試來說是個大忌；而 AI 執行的速度很慢 (跟傳統的 test automation 相比) ，成本也很高。實在不適合這樣做。

因此我做了個調整，在 /testkit.run 的階段讓 AI 找出測試正確地跑法，留下完整充足的資訊，在 /testkit.gencode 這階段，讓 AI 充分發揮 coding 能力，把前面找出來的步驟轉乘能重複執行的 test code, 這樣不但發揮 AI 的能力，也避開 AI 自動化的挑戰

而這些流程，在我想通 SpecKit 的做法後，依樣畫葫蘆沒想到這麼簡單，我簡單錄了一段我的操作過程… 我還沒剪片，過程有點枯燥，有興趣的可以跳著看。原始的操作花掉 25min, 我用 4x 加速，同時在底下標上幾個重要的時間點..

有看完的歡迎給我 feedback, 這些過程我逐步整理後再 release 出來
(影片我改放留言)

----

■ TestKit: GenTest

00:00, /testkit.gentest, 輸入 AC, 展開 decision table

00:05, 人工調整 decision table, 調整 criteria, action

00:23, 人工調整 decision table, 調整 rule

00:33, 確認無誤, 開始按照 decision table 展開所有的測試案例 ( 5 組 )

■ TestKit:Run

00:52, /testkit.run, 節省時間, 我只執行指定的兩個 test case

(接下來是 copilot + mcp 按照 test case 執行 API 的過程)

01:00, 依序呼叫 mcp 的 QuickStart (讀取 instructions), ListOperations (讀取 swagger), AI 準備好開始執行測試

01:02, 開始執行第一個 test case, mcp Create Session, mcp RunStep (多次), 過程中可以看到 session 目錄不斷有 API 呼叫紀錄產生

01:31, 開始執行第二個 test case, mcp 建立第二個 Session

02:00, 測試完成, 看測試報告。列出每個 API 呼叫的結果，並標註是否符合預期

■ TestKit:GenCode

02:12, 依據 session logs, 生成 c# xunit test code

02:50, 測試寫完了, 不過碰到 OAuth2 跟一些型別問題, 這邊比較卡, 我要想想怎麼優化。總之這段就是 fix bug 的過程，花了我大半的時間，不然整個過程其實真實時間 10min 就完成了。

■ RunTestCode

04:08, Test Code 的問題都修正完成, 我已經得到一份不需要靠 AI 就能自動完成 API test 的測試程式了

![](/images/facebook-posts/facebook-posts-attachment-2025-11-03-001-001.png)
