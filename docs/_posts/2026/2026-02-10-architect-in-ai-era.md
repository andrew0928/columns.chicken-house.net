---
layout: post
title: "架構師觀點: Architect In AI Era"
categories:
- "系列文章: 架構師觀點"
tags: ["架構師觀點","技術隨筆"]
published: false
comments_disqus: false
comments_facebook: false
comments_gitalk: false
redirect_from:
logo: 
---


我一直想寫這個主題: 架構師到底該在 AI 時代扮演什麼角色? 這三年來我看到的趨勢是, AI coding 能力越來越強, 人類註定會退出的, 我一直記得 Kent Beck 在三年前 (2023/04) 講的那句話:

https://x.com/KentBeck/status/1648413998025707520

> The value of 90% of my skills just dropped to $0. The leverage for the remaining 10% went up 1000x. I need to recalibrate.
> 翻譯: 我技能的 90% 已經沒有價值了 ($0), 但是剩下的 10% 技能的價值是過去的 1000x, 我需要重新調整策略

Kent Beck 提到的 90%, 就是現在 AI 直接能幫你搞定的部分, 到了 2026 年的今天, 你只要有足夠精確的 spec, 搭配 spec-kits , 以及夠強的模型, 大概都能搞定; 而剩下的 10%, 則是寫出 "足夠精確的 spec" 之前的事情, 做好它, 剩下的 90% 才會順利進行, 如何把模糊的商業及系統需求變成可落實的規格 (甚至是跨越多個團隊或是專案的共通基礎建設的規格), 則是未來架構師要努力的地方｡ 這種結構性的問題, 通常需要從根本的流程著手才能解決, 我在思考這題目的過程中, 看到三篇蠻有意思的文章:

1. 大齡工程師 facebook post: https://www.facebook.com/share/p/1AdpfkEciu/
2. OpenClaw 作者 Peter Steinberger 的專訪: I ship code I don't read https://newsletter.pragmaticengineer.com/p/the-creator-of-clawd-i-ship-code
3. 高見龍寫了篇關於 SDD 的文章: Spec-as-source 的理想與現實 https://newsletter.pragmaticengineer.com/p/the-creator-of-clawd-i-ship-code

這三篇文章的觀點我後面再談, 我主要的思考脈絡是:

AI 可能取代了你過去 90% 的工作, 但是剩下的 10% 是 "非你不可” 的, 這時你該做的只有兩件事: 
1. 一個是別讓 “自己” 變成瓶頸, 不需要你自己做的事情要最大化的轉移給 AI
1. 另一個是你要提升 “自己” 的能力, 讓自己有能力面對更複雜或是規模更大的問題, 而不是寫更多 code..

這是個典型的 "說起來很容易, 做起來很難” 的題目… 這類題目最好的拆解方式, 就是實際拿一個有代表性的 side project 來練一次手感, 你就能從過程中掌握到解題的技巧了｡ 我覺得最大的關鍵, 就是用 Prototype 來驗證問題, 前半部靠 Vibe Coding 快速的打造 Prototype 確保你的想法能解決問題, 閃開大部分的設計風險之後, 藉由這個可被驗證的 Prototype 來產生高品質的 SPEC, 讓後面的開發過程能最大化的享受到 SDD 帶來的優勢 ( SDD 最困難的就是你要先有高品質的 SPEC ).

身為架構師, 是否能做好這件事的關鍵, 就在於你能否把問題妥善的抽象化 + 建模? 你的抽象化能力, 決定了你能掌控多複雜的問題: 你的 coding 有多快, 決定了你的 prototype 能多快完成並且驗證成果; 這兩個能力取決於你能多快的完成高品質的 SPEC, 讓跟你配合的團隊能有效的進行 SDD

如果你都能做到, 這方法的理論天花板是 100x 的速度, 你可以掌控 10x 複雜的問題, 並且讓 10x 的開發團隊拿到高度一致並且已驗證過, 已排除高風險的設計規格, 團隊能用 10x 的速度靠 SDD 完成開發, 整體而言你會替公司帶來 100x 的價值｡

TD;LR;

為了驗證這想法, 我自己挑了我萬年主題之一: 安得魯小舖 當作情境, 來實際操作一次這樣的想法. 為了讓這些高度抽象的想法能夠好理解一點, 我決定先節錄部分我實作的過程 (包含 code), 先讓大家體會我做了什麼事情, 再從流程跟想法來解讀我為何這樣做的原因｡ 如果實作你很熟悉了, 可以跳過第一段, 直接看我的心得與思考過程｡

Side Project: Andrew Shop

講到 "複雜” 的題目, 加上需要依賴高度抽象化能力來解決的問題, 過去嘗試過的題目最貼近的就是 "折扣計算” 了, 這次我把題目難度提高一點, 除了 "折扣計算” 要能有擴充能力之外, 我希望 "販售” 的東西, 也能從靜態的商品, 擴充到動態的服務.. 而這些擴充的要求, 我都有一個前提: 主程式的程式碼不能異動任何一行, 只能調整設定就要能完成擴充｡

// 圖 1, checkout process, 只依賴介面, 不依賴實作, 26H1 - P18

// checkout → ISellItem x IDiscountRule + Membership + (PaymentMethod) → Order

這題的困難點在於, 業務端的需求還不明確 (你還不知道以後會擴充哪些折扣), 系統的規格也還不清楚 (還未經過系統分析及設計, 其實也還沒辦法取得詳細的規格), 而系統的範圍也大, 最終可能橫跨多個團隊分別開發, 橫跨多個團隊須要先約定好共通的規格 (例如 API Spec, 或是 Database Schema ), 並且在訂規格前就先做過完整的可行性驗證的話, 多個團隊的協作就會是個大瓶頸｡ 目前 AI coding 的範圍, 都還僅只再單一專案範圍內, 跨團隊的協作主要還是靠人在解決｡

想像一下這個案例:

“結帳的 API 規格改了, 前台購物車結帳的團隊要改, 後端處理交易的團隊要改, xxx 要跟著調整….”, 想像一下, 這過程 AI 能幫上多少忙? 比較好的補救方式是, 大家都依賴同一份 "SPEC” 來開發, 異動了這份 SPEC 就各自往下變更… 而更好的方式是: 在各團隊開發前, 這份 SPEC 如果能盡量做好驗證, 讓之後規格異動的範圍及風險都能降低的話, 麻煩事就會少很多｡ SDD 固然有效, 但是他的本質就是 waterfall 的流程 (只是依賴 AI 的 coding 能力, 即使是 waterfall 你也能很快看到成果), 規格的異動終究是需要把局部的流程都重新走一次的｡

這邊我打算這樣解:

用 Vibe Coding 來開發 Prototype (架構師親自操刀, 只實作關鍵部分, 不處理細節需求, 用同一份 code 能滿足所有情境為通過標準)

用 Prototype Code 來代替 SPEC (若需要調整 spec, 重構 code 會比重構 spec documents 來的有效率, 完成後再將 code 輸出成你需要的 SPEC)

核心觀念都是圍繞在用 code 當作最終的 spec , code 能被驗證 ( tests ), code 能變成 spec ( interface ), 調整規格叫精確 ( code 可以靠 ide 重構, 有 compiler 協助驗證, 有 tests 驗證需求是否符合 ), 只要你有能力用 code 來溝通, 設計階段 spec 還未穩定的階段, 用 code 來溝通的效率遠高於用文件, 這種流程我自己取了個名字: Spec as Code.

// SPEC as CODE

這步驟, 其實你心理有個大致的樣貌, 現今模型的能力其實很容易就能做的出來了｡ 我把這幾張圖直接當附件 (我也懶的重新打字或是換成 mermaid ), 其實 AI 很快就生成第一版給我｡ 這個階段, 生成的 code 很少, 我會逐一檢視, 每一行都看過一次｡

// SCENARIO → TESTs

為了具體一點看看這些 code 會怎麼被使用, 這樣比我自己看 interface 想像來的具體的多, 於是我開始讓 AI 做第二步驟, 把我要的情境, 寫成 Unit Test ..

這時, 觀察 Unit Test Code, 我開始發現一些 "使用方式” 跟我想像不大一樣的地方, 例如我在敘述 AppleStore BTS 優惠的時候, 就糾正了 AI, 我希望消費者自己把贈品也加入購物車, 只是在結帳時要自動把 AirPods 當成贈品, 用 $0 元計價, 而不是消費者購買 MacBook 的時候自動替他選擇贈品… 其實這些過程, 就是我提前在做 SpecKit.Clearify 而已. 而我修正回答後, 直接生成程式碼, 而不是生成規格文件

// Review Test and Adjust Interfaces

在這個階段, 我經歷過幾次的往返, 不斷的 review test case code, 判定 AI 是弄錯我的意思寫錯 test case? 還是 AI 在前一步給了不合適的 interface design? 由於 AI 太聽話了, 有時他會使命必答的完成你的要求, 即使你的要求不大合理｡ 過程中我就碰過 Core / Abstraction 放的類別位置不妥, 原本 Abstraction 應該只有定義, 不包含任何實作, Core 應該相依 Abstraction 才對, 結果卻出現 Abstraction 需要相依 Core, 導致 AI 寫了好幾個中間的類別要來解套, 這些 code 都再過程中被我挑出來刪掉了, 因為根本原因是前個步驟設計錯誤, 而不是現在將錯就錯, 產生一堆額外的設計來適應這不合理的結構｡

這邊我再次強調, 你一定要趁著 code 還不多, 只有很乾淨的 domain interface 的時候, 親自 review 每一個設計, 並且親自 review 每個 test case 是否清楚的還原你對 interface 該怎麼運作的想像｡ 這些你確認下來的設計原則, 測試案例, 以及 interface 定義, 將來都會變成能替你把關 AI code 的輔助機制:

Rules:例如我明確的說明了套件的規則, Abstraction 只包含 interface / data model 定義, 不包含 logic, 而 Core 則只包含特定範圍內的實作 ( membership, checkout service, 以及 DI Helper ),

Contracts:善用語言的特性 ( ex: C# interface / abstract class ), 你越精確的用語言來描述你的 contracts, 將來編譯器就能越精準的替你找初步符合規矩的實作. 這是為何我不管跟誰合作, Prototype 我一定是挑選我熟悉的 c# 來實作的原因, 因為 c# 對我而言是 "母語” 等級的語言, 我對他的熟悉程度已經到我能直接用 C# 把我腦袋想像的結構直接寫出來, 而我自己若能保證想像 → 程式語言 這部份的轉換, 其餘的驗證我就能靠編譯器來處理. 編譯器的驗證結果是有效率的, 並且是精準的 100% 正確, 這些環節我會讓編譯器來執行, 而不是交給 AI, 只有 95% 的正確率 (而且還花錢)

Tests:測試有兩個涵義, 一個是讓我確認 interface 的使用方式, 另一個是用 code 來表達你期待的情境, 用 code 的方式來描述呼叫步驟, 以及每個步驟的 input (arguments) 及 output ( return value, result ) 的預期. 現在還只有 interface, 測試一定是亮紅燈, 但是當你補完實作之後, 你有準備好這些測試, 你就能越輕鬆的揪出 AI coding 不符合你情境的錯誤

我採取的策略, 其實就跟 Peter 專訪提中提到的一個重點不謀而合, 你不要自己去 review 每一行 code, 而是你應該建立一個體系, 讓問題自己被抓出來. 我建立的體系, 就是善用 Rules + Compiler + Unit Tests 的組合來替我 review 後面階段 AI 的產出｡ 我需要善用這些方法才能跟的上 AI 量產過的 source code, 若不改變方法我根本 review 不完｡ 而我怎麼確保 Rules / Contracts / Tests 都是對的? 我趁這些內容都還再高度抽象化的階段, 數量還在可控的範圍內的時候, 親自 review 每一個 interface, tests, 來確保我已經跟 AI agent 完全對齊這三個期待.

// 魔法是想像的世界, 你能想像就能切割

// 對付這麼時代的魔法使 AI agent, 只要用基礎魔法就夠了

// Mock Code

接下來, 就是開始按照 contracts, 把實際上需要的 core / extensions 逐一補上了｡ 這時我還是不斷的堅守原本的流程: 修正過程中有必要我就會回頭修正 contracts 的設計, 而這些 spec (contracts) 是以 code 形態存在的, 因此修正對我來說非常容易, 就是 "重構” 的基本動作而已. 仰賴 compiler + IDE + agent 的協助, 我不需要擔心 interface 改了有沒有哪邊漏掉沒改? ( 包含 tests ), 只要漏改了任一個地方, build error 會清楚的指出哪一行有錯誤, 這非常有效, 這也是我喜歡在設計還沒定案前, 用 code 來表示 spec 的原因, 要進行重構, code 比 document 容易太多, 我選擇到 prototype 告一段落後才開始將 code 轉移成 spec documents ( abstraction 可以留著 )

// +NFR, 追加管理程式碼結構的輔助設施, 例如 Builder, Helper, Builder Extension Method … etc

// Prototype + Tests, 開始用實際的商業情境來驗證 "架構” (驗證架構 而非驗證功能, 以及 ui 操作細節)

// Generate Final Specs

// Develop Final API services, Repositories, and Real Business Requirement (Extensions)