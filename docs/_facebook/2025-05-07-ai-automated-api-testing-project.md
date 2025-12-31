---
date: 2025-05-07
datetime: 2025-05-07T21:56:51+08:00
timestamp_utc: 1746626211
title: "最近起了一個 side project, 我在嘗試透過 AI 能否簡化 / 自動化 API 測試的需"
---

最近起了一個 side project, 我在嘗試透過 AI 能否簡化 / 自動化 API 測試的需求?

結果可行，雖然只是個 PoC 的 side project, 還是挺令人興奮的 :D

我拿我之前為了 "安德魯小舖" 寫的購物車 API 當範例，用 ChatGPT 產了主要情境的正反測試案例 (共 15 個，只描述商業情境，沒有指定精確的 API 參數) 當作腳本，丟給我寫的 test runner, 結果不負眾望, test runner 順利地按照腳本呼叫了 API，也給了我完整的測試結果報告..

突然覺得好虛榮啊，出一張嘴就有人幫我把測試跑完 (包含從情境自己決定該打哪個 API，該生成什麼參數) + 雙手遞上報告... XD, 雖然還有很多外圍的問題待解決, 離正式上場還有好一段距離, 不過主要環節打通了還是挺開心的。接下來分享一下過程跟心得..

--

最初有這想法，來自於當今 LLM 都有很好的 Function Calling 的能力, 為何不拿這能力來面對自動化 API 測試呢? 複雜如 Agent 的應用都能面對了，API 自動化測試相對來說是小事吧~

果不其然，順利完成。其實這一切都如預期啊，本質來說，讓 LLM 按照測試案例執行 API，其實就跟我當時開發 "安德魯小舖" 按照對話完成購物 (也是呼叫 API) 完全是同一件事情，只是敘事角度換了個方式而已..  觀念一轉，反倒有這結果是理所當然的…

只是，API 要做到 AI Ready，本身還是有一點門檻的 (都在設計，不在技術方面)。真正有挑戰的，會在這些還沒滿足 AI Ready 的 API 該怎麼自動化執行測試吧… (這些議題，其實都在我去年分享的 “從 API First 到 AI First"，以及前年的 “API First Workshop”，”API First 的開發策略” 這幾場演講)

最後，貼個執行結果給大家體會一下，實作方式我整理一下再分享開發過程... Test Runner 是用 Microsoft Semantic Kernel 開發的，就是拿 Plugins 來簡化 function calling 操作而已。關鍵的部分大概 50 行以內就搞定了，敬請期待 😀

相關的內容，我放留言，有興趣請參考~

--
以下是 test case 內容 (實際貼給 AI 執行的內容)，主要是規格有註明購物車上限是十件商品，而我的 API 實作並沒有包含這限制，而這 test case 就是驗證這邊界有無實作的 scenario ..
--

## Context
- shop: shop123
- user: { user: andrew, password: 123456 }
- location: { id: zh-TW, time-zone: UTC+8, currency: TWD }

## Given
- 測試前請清空購物車
- 指定測試商品: 可口可樂

## When
- step 1, 嘗試加入 11 件指定商品
- step 2, 檢查購物車內容

## Then
- 執行 step 1 時，伺服器應回傳 400 Bad Request（數量超出 10）
- step 2 查詢結果，購物車應該是空的

--
輸出的 report 是 markdown, 為了排版我用截圖的。AI 依據我給的  spec, 加上我給的商業情境 (上面貼的)，就幫我決定 API 呼叫的順序及參數:

- GET /api/carts/create 建立新的購物車，目的是清空購物車
- POST /api/products 查詢商品清單，目的是找出可口可樂的 id
- POST /api/carts/22/items 加入 11 件可樂，測試是否會回報錯誤? (我的 API 沒做這段，所以測試會不如預期..)
- GET /api/carts/22 確認購物車結果是不是空的 (因為前個步驟沒有失敗，因此這步驟也會不如預期，會有 11 件可樂在裡面)

![](/images/facebook-posts/facebook-posts-attachment-2025-05-07-001-001.png)
