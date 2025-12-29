---
date: 2025-02-28
datetime: 2025-02-28T17:35:17+08:00
timestamp_utc: 1740735317
title: "花了點時間試了一下 GitHub Copilot Workspace, 驚為天人, 只能說這產品的定"
---

花了點時間試了一下 GitHub Copilot Workspace, 驚為天人, 只能說這產品的定位太厲害了... 打從心底佩服這 Product Owner ..

GitHub Copilot Workspace, 讓你從規格文件起始一個專案，產生環境，產生 code ... blah blah, 東西當然不會一次到位, 你覺得不符合你期待的, 就開個 issue 讓 AI 幫你改, 改完會發 PR 給你, 你再來 review 看看是否接受..

我覺得厲害的有幾個地方:

1. 撇開 AI, 其實這流程跟正常的開發流程沒什麼兩樣啊, 只是真人來執行的話, 通常都會依據經驗, 省掉部分環節而已 (咦?)。流程本身本來就是 GitHub 的強項，只是背後多了很多會寫 code 的 agent 扮演 developer，跟你一起完成這專案...

2. 這一切都在 server side 進行, 巧妙的進攻其他 AI coding 工具 (尤其是 IDE 型態的, 例如 Cursor, 或是它們自家的 GitHub Copilot) 沒進攻的地盤

而我會覺得厲害，並不是他的 code 生成的比別人好 (其實大家後面的模型都是那幾個)，而是它讓你不知不覺，從扮演 "programmer" 的身分，變成扮演 "team leader" 的身分了。

平常是那些角色才會決定規格，啟動專案? 每個公司分工也許不同，但是大部分都是 team leader, 或是 senior engineer 這類角色..

誰會發 issue 給 developer? 通常都是 PO, QA, 客戶.. 而分派的角色通常也是 team leader ..

而 GitHub Copilot Workspace, 就是讓你玩角色扮演, 準備了一堆厲害的 AI Agent, 只要你扮演好 team leader, 這些 agent 就會幫你完成專案.. 當然你也可以自己改 code, 或是安排一個厲害的 developer 幫你處理 AI 搞不定的 issue, 那就是 GitHub Copilot + VScode 上場的機會了 (或是對等的用 cursor 等等都行)

這是個很具體的發展趨勢，以前的標準配置，可能是 team leader x 1 + 3 ~ 4 developer ( 一個 pizza 可以餵飽的團隊規模 )，而這類服務普及後，會改變這比例，顯而易見的，以後市場對於 team leader 的需求會擴大..

--

最後補一下我的想法:

我覺得從來都不會有誰取代誰的問題，不管有沒有 AI coding, 市場上需要被開發的軟體專案就是會越來越多，需要溝通的案子跟團隊也會越來越多，因此第一線的角色完全不用擔心... 這些生產力工具是個大利多，快點學會掌握他替你做事..

至於 developer, 我也覺得是大利多。畢竟市場上需要被開發的軟體終究是會變多，不會變少。差別在於你是否是以後能跟 team leader 配合的那個 developer? 持續精進是必要的，用 AI coding 也是必要的。

另一個機會是，GitHub Copilot Workspace 這樣的服務也出現了。已經有一定能力的 developer, 快點熟悉怎麼善用這樣的服務，你不就是在練習怎麼做好 team leader 了嗎? 這麼好的工具你不用老闆給你機會，你也不用怕丟臉，自己就可以練習... 過了這門檻，你的機會就是上面那圈的機會...

最後，大家常再說 junior developer 也不要灰心，AI coding 對你們也是大利多，但是 AI 終究需要人來做最後把關。你要有能力 "把關" 你才能待的下去。過去是市場太缺人，也養了部分沒有這種能力的 (偽) developer, 只是現在 AI coding 成熟了，開始把這類人擠出去而已。

Junior Developer 用 AI coding, 請別只是以 "能動" 為目的。花點時間看看 AI 給你的 code, 學學他怎麼做到的 ( code 都給你看了 )。AI 給你建議的時候，別無腦按下 Accept, 看完再按, 不懂就問到懂再按。如果你可以閉著眼睛就 Accept 的情況，那大可以根本就不用跟你確認了啊。如果你都有真的看懂這些 code, 你學習速度會比過往還快，你很快就能進入上面的 (真) developer 角色了
