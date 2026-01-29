---
layout: post
title: "架構師怎麼帶 AI 寫大型系統？Contract-First 實戰筆記"
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

看到高見龍最近寫了一篇 [Spec-as-source 的理想與現實](https://kaochenlong.com/sdd-spec-as-source)，點出了 SDD（Spec-Driven Development）的核心矛盾：**LLM 本質上是非確定性的，但程式碼需要確定性**。同樣的 spec，AI 每次產出的 code 都不一樣；而自然語言本身就有曖昧性，你寫得再精確，AI 還是會「自由發揮」。這些盲點我很認同，這也是我一直在嘗試解決的問題。除了執行結果之外，我更在意的是架構的設計——這些非原始規格要求的環節，就是我這篇想聊的。 

架構師的日常, 就是處理「跨團隊、跨專案、跨系統」的協作問題。這些邊界上的介面設計，直接影響整體系統的主幹——對系統品質、穩定性、以及未來的擴充性都息息相關，也是我花最多心思的地方。這類規格我不會只用文字來敘述, 取而代之我會想辦法直接用 code 來跟團隊溝通, 因為: 

- 你沒辦法讓編譯器幫你驗證「規格文件」是否被正確實作, 但是 code 可以, 所以我會嘗試用 code 來說明規格 (interface)
- 你沒辦法讓 AI 在開發過程中自動檢查是否偏離規格, 但是 compiler 可以, 所以我會嘗試用 interface 來約束實作方式
- 你沒辦法在 CI/CD pipeline 裡自動攔截違反規格的 code, 但是 unit test 可以, 所以我會嘗試用 test case 來敘述使用情境

我的解法是：**用 code 來寫 spec**。把關鍵的介面設計寫成可編譯的 interface / abstract class，讓編譯器成為規格的驗證器。這不是什麼新觀念——這是架構師行之有年的工作方法，只是過去用來跨團隊溝通，現在我把它拿來跟 AI 溝通。高見龍文章裡提到的「形式方法」就是這個思路的極致版本，而 TypeScript 的型別系統、Rust 的所有權機制，都是「輕量版形式方法」的成功案例。

這篇文章，我用一個實際案例來示範這套工作流: **Contract-First + TDD + SDD**

1. 為什麼 Vibe Coding 在大型系統會碰壁？
2. 架構師如何用「介面設計」來控制 AI 產出的品質？
3. 如何用 Decision Table 確保測試覆蓋所有關鍵情境？
4. 規格完備後，SDD 如何讓開發速度起飛？

如果你想直接看結論，可以跳到最後的「心得」章節。如果你想知道具體怎麼做，請繼續往下看實驗記錄。


<!-- ====== 原始引言（保留備查）======

看完高見龍的這篇文章, 我決定重寫我這篇文章的引言了 (範例早就寫好了沒改), 龍哥提到的 SDD 的盲點我很認同, 這也是我一直在嘗試解決的問題｡

ai coding 的能力已經沒人懷疑了, 現在的瓶頸都在: (事前) 你怎麼指揮 AI 做出 "你想要的" 系統? (事後) AI 真的做出來了, 你怎麼確認這就是你要的系統? 這些問題其實把 AI 換成外包, 或是換成你帶的開發團隊等等都適用, 只是現在從 "真人" 換成 AI 了, 效率更快, 成本更低, 但是不確定性也高, 這些都是你在 "外包" 開發專案時你需要學習掌握的環節｡

所以我覺得問題已經不在模型本身了, 跟工作方法比較有關, 取決於你如何控制這些風險｡ 自然語言有很大的 "解釋空間", 因此你可以高度壓縮你的意圖, 用一句話就可以講完所有的需求 (ex: 幫我復刻一個 Facebook 這樣的系統)｡ 這樣做的後果是什麼大家都知道了, 我想嘗試的是如何在只出一張嘴, 跟全部自己動手做的兩個極端之間找出一個平衡的切點｡

在現階段 (2025/年末), 我的答案是: 用 SDD, 但是你的 SPEC 不應該只有 "文件", 若你的系統包含跨多個其他系統或專案的溝通 (而且這些系統不在你這次的開發範圍), 你就必須把這些系統之間的 "邊界" 也交代清楚｡ 用文字不夠精確, 你必須善用其他工程技巧來描述這些規格｡ 在過去, 架構師常用的方法是: 抽象化 -> 訂介面 (你可以用 IDL 來訂, 不要只是文字) -> 介面實作 (例如 api 就給出 open api spec + mock, 或是 c# 就給出真正可編譯的 interface / abstract class ) -> 介面測試案例 ( 有 c# interface 你就可以開始寫 test case 了), 用這些方法, 我在開發流程中可以插入多個檢查點, 只要開發過程中這些檢查點都沒問題, 我就會對外包團隊的產出更有信心, 除了能動之外, 我會知道我要求的測試案例都通過 (隱含已經符合我期待的運作流程), 符合設計規格 (隱含已經符合跨系統的溝通要求, 以及未來擴充的能力), 這些都是身為架構師會額外要求的非功能需求範圍｡

所以, 在 SDD 的前提下, 我納入了先前一直在推廣的 Contract-First ( API-First ) 開發方法, 也納入了 TDD 的工作流程來當作規格的一部分, 而規格怎麼無中生有? 我以 SPEC 為分界點, 在 SPEC 還沒定案前, 我採用較靈活的 vibe coding 來做 prototyping, 藉由大量的 test case 先確認這些 contract 是否真的能滿足期待? 之後定案變成 spec 的一部分後, 再走 SDD 完成開發｡ 

這樣的流程, 其實是了解各種工作方法的優缺點後, 重新規劃的最佳路徑, 而這篇, 我挑了一個過去嘗試過的 side project: 折扣計算 來當案例, 重寫一次, 看看這樣的做法是否真的能滿足我的期待? 這篇文章內容很長, 我會附上我的實作記錄, 有興趣可以繼續往下閱讀 (第一段), 如果想跳過實作直接看心得, 可以從 (第二段) 開始看｡

====== 原始引言結束 ====== -->


---

## 建議章節結構（待重組）

<!-- 
以下是根據素材分析後建議的章節結構，供重組參考：

### 0. 引言：問題意識 ✅ 已完成
- 呼應龍哥：SDD 的瓶頸不在 AI，在「規格怎麼寫」
- 你的解法預告：用 code 寫 spec，讓編譯器驗證

### 1. 為何 Vibe Coding 不夠？
- 對照組實驗展示
- 點出問題：介面設計是 AI 自決的黑箱
- 銜接龍哥觀點：自然語言曖昧性 + LLM 非確定性
- 素材來源：現有「對照組」章節

### 2. 架構師的核心能力：抽象化與邊界切割
- 論述：為何介面設計是人的責任？
- 大型系統 = 多個黑箱，切割邊界才能控制複雜度
- 銜接龍哥觀點：角色轉變，從 how 到 what
- 素材來源：現有「動機」章節 + 心得區的「切割邊界」論述

### 3. Contract-First：用 Code 當 Spec
- 論述：為何用 interface/IDL 比自然語言更好？
- 呼應龍哥「形式方法」：這是輕量版，編譯器就是驗證器
- 複利效應：100% contract → 100% test → 99% code
- 素材來源：現有 TODO 區塊，需補充論述

### 4. 測試先行：用 Decision Table 確保規格完備
- 論述：TDD 的真正價值是驗證 contract 好不好用
- 實驗展示：step 3 的 decision table → 25 個 test case
- 素材來源：現有「實驗組 step 3」

### 5. SDD 收割：規格完備後的大規模實作
- 實驗展示：step 4-7 的快速推進（精簡版）
- 呼應龍哥 Spec-anchored：spec 是活文件，不是用完即丟
- 素材來源：現有「實驗組 step 4-7」，需大幅精簡

### 6. 對照總結
- 表格比較：對照組 vs 實驗組
- 核心差異：誰決定 contract？誰驗證 contract？
- 素材來源：現有 TODO 區塊

### 7. 心得：架構師在 AI 時代的定位
- IDE/Debugger 還需要嗎？
- 架構師的價值：切割邊界 + 定義 contract
- 結語：不是取代，是放大
- 素材來源：三個修訂版整併
-->

---






即使 AI coding 的能力已經超過大部分的工程師水準了, 使用者的程度是專業還是業餘, 仍然有很大的差別｡ 這次我做了點嘗試, 特地挑了過去做過, 有點難度的的 side project, 來測試看看單純的 "vibe coding" 對照架構師角度來命令 AI 替我寫 code, 比較一下兩者的差異｡

先說結果, 我覺得產出成果的差異是很大的, 架構師的視角會 review 關鍵的介面設計 (contract, or interface), 並且針對這些約定用測試保護, 用最少的資源來保障整體系統的體質｡ 這很困難, 因為 interface 的設計是需要經驗的, 可以動 vs 理想 中間的空間非常大, 換句話說, 這很吃架構師設計的 "品味", 也是現在 AI 最難掌握的環節.

從另一個角度來看, AI 還難以完全掌握 contract 的另一個原因是: 這設計通常是橫跨多個專案, 多個系統, 會持續長時間的設計, 我拿 API spec 當作例子, 重要的 API, 開發跟使用的團隊可能完全不一樣, 你現在用的 coding agent 就是服務特定團隊而已, 負責 "使用" API 的 agent, 可能根本沒有能力調整 API spec, 因此這些跨團隊的協調, 仍然是 "人" 的工作, 也是架構師的主要任務之一｡

抽象化能力, 依然是開發人員很重要的能力, 即使到了 AI 時代仍然是這樣 (甚至更重要了), 因為不需要抽象化能力的 coding 都已經交給 AI 了啊, 因此這次我挑了個需要高度抽象化思考能力的 side project: 折扣設計 來當作練習的題目｡ 我做了兩組實驗, 一個純無腦 vibe coding, 另一個從架構師的視角來要求 AI 來完成任務, 我把步驟跟成果都對比給各位參考｡ 你可以看看最終的成效, 來體會兩者的差異; 如果你想知道怎麼做到, 你也可以看看我記錄下來的步驟, 體會一下跟你平常做法的差別再哪裡｡ 




<!--more-->

這次的實驗內容如下, 有興趣看過程的可以往下看:

題目: 購物車折扣計算的機制設計 (參考我 2020/04 的文章)
影響: 程式碼能正確運作是基本條件, 我評估的標準是軟體工程角度, 是否容易維護, 擴充, 部署等環節來評分

對照組 (人設1): 由可以描述功能性需求的 PM 來開發, 在 vibe coding 的過程中我會裝傻, 會避開不提及技術相關議題
實驗組 (人設2): 直接由架構師來進行開發, 會要求程式碼結構, 繼承階層, 公開的介面規格, 軟體工程的工作方法 (ex: TDD)

結果毫無懸念, 你時間花在哪, 成果就會在哪裡｡ 架構師的這組實驗, 花了 5 倍的 premium request 才完成, 得到的成果也明顯較好, 這是可預期的｡ 我想表達的是: "實驗組" 的開發過程是怎麼做的? 各位可以從這些過程中反思, 哪些環節仍然必須依賴有經驗的人來進行? 如果無法完全交給 AI, 那 AI 可以怎麼輔助? 掌握這些差異, 有助於各位仔細思考未來團隊需要準備什麼樣的角色, 各位自身的能力該往什麼樣的領域發展｡




# 1. 動機: 為何選這題目

我刻意挑選 "購物車的折扣計算" 這題目是有原因的, 因為這題目的複雜性在於 "解決未知問題", 以及 "系統層級的擴充機制"｡ 我希望購物車的系統現在就開發完成, 但是折扣則是未來按照需求會不斷擴充, 要能類似瀏覽器的 extension 一般, 不需更動主系統就能動態載入新的折扣規則, 這邊就牽涉到現在還未出現的需求 (需要猜測, 要決定方向), 也需要跨團隊溝通 (開發購物車跟開發折扣規則可能是不同團隊), 目前的 coding agent 都是團隊內部自己的選擇, AI 工具的發展還沒有成熟到 "我的 agent 能跟你的 agent 約定好規格, 然後各自開發" 的程度, 因此這些技術的決策跟協作, 責任都還是在 "人" 的身上...

所以, 我拿這個題目, 看的就是架構師這樣的角色, 該如何善用 coding agent 來開發這樣的系統, 同時該用什麼樣的順序跟流程進行才會順利? 對我來說不只是 "觀點的討論" 而已, 而是更進一步的流程驗證, 這篇就是我嘗試過程的一個記錄跟心得｡

從結果來說, 大型系統的開發, 這幾個面向是需要架構師這樣角色來負責的, AI 可以輔助, 但是還無法完全替代:

1. 系統的公開介面設計 (ex: API spec)
2. 架構上的關鍵設計 (ex: 類別階層設計, 依賴關係設計, 依賴注入的結構設計)
3. 需要跨團隊 / 跨專案約定的設計 (ex: 分工邊界, 系統邊界, 責任範圍, 商業規則, 特定業務相關的演算法)

這些都是架構師這類角色的日常, AI 已經可以負擔很多資訊蒐集, 整理的任務了｡ 但是要生成各種報告或設計, AI 可以做到語法跟結構正確, 但是目的是否正確仍然需要人工的驗證 (就像 vibe coding 也需要 code review / unit test 一樣), 如果你根本不知道 "正確答案" 的話, 你拿什麼能力來驗證 AI 的產出?

所以, 最後 "實驗組" 的流程, 我大致上分前中後三段逐步進行, 是我認為現在的工具組合下, 最有效率的做法:

1. 確認邊界 (快速用 vibe coding 產出我想像的結構, 實際驗證看看是否合適)
2. 確認規格 (邊界確認後, 按照邊界的規格 + decision table 做高覆蓋率的測試計畫, 確保規格的合理性, 降低規格需要翻掉重來的風險)
3. 大規模實作 (用 SDD 來加速開發, SDD 是好東西, 但是困難的地方在於你要有明確的規格, 前面兩個步驟就是架構師怎麼掌握規格的手段)

在實驗組, 其實我花了大部分的時間在 "品質" 這件事身上, 所謂的 "品質”, 是指在設計上的每個環節都符合我對軟體開發的期待, 即使絕大部分的程式碼都不是我寫的, 但是 ai 產生的 code 卻能高度的符合我的預期, 包含業務邏輯, 架構設計, 以及執行結果, 還有非功能性需求等等, 都符合我的期待｡

接下來的篇幅, 我就把我跟 AI 互動關鍵的部分記錄下來, 成果跟歷程我都放上 GitHub, 有興趣的朋友可以自行參考, 文章我就論述我認為的重點


# 2. 設計原則: Contract-First 的核心思路

// TODO: 從動機章節的「三段流程」展開，說明 Contract-First 的核心觀點
// TODO: 為何介面設計是關鍵？為何要先定義 contract 再寫 test？
// TODO: 複利效應：用最少力氣得到 100% 正確的 contract → 100% 正確的 test → 99% 正確的 code


# 3. 對照組: 純需求敘述 + Vibe Coding

既然是對照組, 我就 "只” 談我表面上需要的 "功能規格” 了, 看看 AI 能替我做到什麼樣的程度｡ 基本上我只談需求, 實作完全交給 AI, 我用現在最理想的模型 Claude Opus 4.5 來處理這段開發任務｡ 這對照組的實驗結果是:

開發出來的程式碼完全符合我的功能需求, 但是對系統內部的結構我一無所知, 只能等開發後期看到 code 才能確定｡ 我的設計重點是 “折扣規則的擴充能力”, 從事後的角度來看, 其實算及格, Opus 4.5 並沒有再設計上抄捷徑, 規格上有確實實作出折扣的抽象介面, 不過由於我沒有任真的把這介面當作需求, 因此做出來的樣貌跟我預期的有落差｡ 真要打分數的話我給 70 分, 跟預期的落差我後面說明｡

執行對照組的人物設定, 我就把我自己當作 “不會寫 code” 的角色來執行 vibe coding 吧! 我直接在 GitHub Copilot 輸入這段話來啟動開發任務:

> 設計購物車結帳金額計算規則
> 結帳若符合折扣規則, 則要用優惠價格計算.
>
> 我想要的規則有這幾個 (按照優先順序):
>
> 1. 指定商品 (product-id=102), 一次買兩件的話, 這兩件 8 折優惠
> 2. 指定商品 (product-id=128) 買一件, 搭配的商品免費 (product-id=129)
> 3. 結帳總金額大於 1000 元, 折價 100 元
>
> 請替我生成:
>
> 1. 結帳計算邏輯
> 2. 生成樣本資料
> 3. 生成單元測試
>
> 用 dotnet 10, c# 開發

過程我就跳過了, 就是 AI 自顧自的輸出了一些訊息, 也改了好幾個檔案, 在完全沒有我介入的情況下就跑完了, 這是我輸入上面這段要求後, AI 給我的結果回報:

[[2026-01-01-ai-vibe-coding-contract-first-01.png]]

其實比較超出我預期的是: 即使我沒特別要求, Claude Opus 4.5 已經知道這要求該用 C# 多型的技巧來實作了 (大約半年多前, 同樣的要求 AI 是用了很醜的 if / else 來實作…), 而且實作的機制其實蠻到位的,  只接收到我給他很有限的資訊, 就能做到這樣其實很厲害了｡

所以, 硬要挑毛病的話, 就是他的設計跟我想要的不大一樣而已 (但是我的確沒說出來)｡ 其他細節我就不看了, 特別來看看他定義的 IDiscountRule.cs :

```csharp

/// <summary>
/// 折扣規則介面
/// </summary>
public interface IDiscountRule
{
    /// <summary>
    /// 規則名稱
    /// </summary>
    string RuleName { get; }

    /// <summary>
    /// 優先順序 (數字越小優先順序越高)
    /// </summary>
    int Priority { get; }

    /// <summary>
    /// 檢查規則是否適用
    /// </summary>
    bool IsApplicable(Cart cart, CheckoutContext context);

    /// <summary>
    /// 計算折扣
    /// </summary>
    AppliedDiscount? Apply(Cart cart, CheckoutContext context);
}
```

中規中矩的設計, 結構是很合理的, 只是沒對齊的是現在以及未來的需求｡ 第一個問題: IDiscountRule 未來可能是別的團隊開發的, 這些規格是溝通過的嗎? 在這個案例, IDiscountRule 這介面根本完全沒出現在需求內, 連名字都是 ai 自己取的, 而這介面是未來擴充折扣規則的重要設計, 這是不能隨便亂改的, 需要更嚴格的設計與檢視, 並且要輸出對應的公開規格文件才對｡ 當你過度重視 “能動的 code”, 就會忽略掉這類協作問題｡ 而這些問題, 對於不碰 code 的各種角色來說是完全不會想到的

因此, 我常說的 "大型專案” 就是包含很多這類的情境, 太多規格不會在你一次的 coding agent 對話過程中能決定的, 介面的定義, 若沒有負責的角色出來統合各方的共識與設計, 是很難定案的｡ 沒有定案前, 你讓 ai 寫的 code 寫的再好都沒用.. 這些任務, 看起來仍然需要由人類來負責, 而且是需要有經驗, 有技術判斷能力, 以及協作溝通能力的角色, 例如技術經理或架構師｡

另一個盲點, 來看看 IDiscountRule 出現的 CheckoutContext 這個 class 的設計:

```csharp


/// <summary>
/// 結帳上下文 - 用於追蹤已處理的項目和累計折扣
/// </summary>
public class CheckoutContext
{
    /// <summary>
    /// 已經被折扣規則處理過的商品數量 (ProductId -> 已處理數量)
    /// </summary>
    public Dictionary<int, int> ProcessedQuantities { get; } = new();

    /// <summary>
    /// 累計的折扣金額
    /// </summary>
    public decimal AccumulatedDiscount { get; set; }

    /// <summary>
    /// 已套用的規則標記 (用於限制只能套用一次的規則)
    /// </summary>
    public HashSet<string> AppliedRules { get; } = [];

    /// <summary>
    /// 取得商品剩餘未處理的數量
    /// </summary>
    public int GetRemainingQuantity(int productId, int originalQuantity)
    {
        return originalQuantity - ProcessedQuantities.GetValueOrDefault(productId, 0);
    }

    /// <summary>
    /// 標記商品數量已處理
    /// </summary>
    public void MarkAsProcessed(int productId, int quantity)
    {
        ProcessedQuantities.TryGetValue(productId, out var current);
        ProcessedQuantities[productId] = current + quantity;
    }
}
```

從 ai 寫的這段 code 來看, 可以推敲出他的商業規則: 一個商品只能套用一次折扣活動 (寫死的規則)

而一筆訂單, 同一個折扣活動是否只能生效一次, 則可以由 IDiscountRule 自己決定 ( IsApplicable ). 同樣的這不是對錯的問題, 而是 AI 直接幫你寫出來了, 如果你沒有察覺, 這些需求就出去了. 我會再次的討論這個主題, 是因為這都是 "發行後” 就很難修改的內容, 因為影響範圍可能會跨越多個專案, 而替你寫這份程式碼的 AI, 他的影響範圍只在這個專案內…

再來看一段 code, 驗證一下前面提的, 這次來看其中一個折扣任務的實作:

```csharp


/// <summary>
/// 規則3: 結帳總金額大於 1000 元, 折價 100 元 (只套用一次)
/// </summary>
public class TotalAmountDiscountRule : IDiscountRule
{
    private const decimal Threshold = 1000m;
    private const decimal DiscountAmountValue = 100m;
    private const string AppliedKey = "TotalAmountDiscountApplied";

    public string RuleName => "滿千折百";
    public int Priority => 3;

    public bool IsApplicable(Cart cart, CheckoutContext context)
    {
        // 此規則只能套用一次
        if (context.AppliedRules.Contains(AppliedKey)) return false;

        // 計算折扣後的金額是否仍超過門檻
        var subtotal = cart.GetSubtotal();
        var currentTotal = subtotal - context.AccumulatedDiscount;
        return currentTotal > Threshold;
    }

    public AppliedDiscount? Apply(Cart cart, CheckoutContext context)
    {
        if (context.AppliedRules.Contains(AppliedKey)) return null;

        var subtotal = cart.GetSubtotal();
        var currentTotal = subtotal - context.AccumulatedDiscount;

        if (currentTotal <= Threshold) return null;

        context.AppliedRules.Add(AppliedKey);
        context.AccumulatedDiscount += DiscountAmountValue;

        return new AppliedDiscount(
            RuleName,
            $"結帳金額超過 {Threshold:N0} 元，折抵 {DiscountAmountValue:N0} 元",
            DiscountAmountValue
        );
    }
}
```

兩個我不大喜歡的寫法:

1. IsApplicable, 每個 Rule 的實作都要自己填寫一次幾乎一樣的邏輯｡ 如果有人寫的不一樣, 那規則可能就在這邊出現例外｡這時這邊的設計應該要包含內建的實作, 應該把 interface 換成 abstract class 會更合適
2. 同上, Apply(…) 也包含太多類似的程式碼, CheckoutContext 是會橫跨多個 IDiscountRule 的共用物件, 讓每個 DiscountRule 自己更新實在很不妥, 只要有一個開發商亂寫就完蛋了, 這段邏輯應該統一集中在 CheckoutService 結帳時集中計算才對

這些, 都是 Vibe Coding 用來開發複雜度高, 需要跨不同開發專案溝通確認的環節, Vibe Code + 沒有足夠的經驗, 幾乎沒辦法閃開這些問題｡ 資深人員你們的工作不會不見, 但是相對的, 你要有能力管理好這些狀況

最後, 我出一張嘴要 AI 幫我寫測試, 他也照做了, 不過我沒跟他講要測試什麼… 來看看 AI 替我做了哪些驗證｡ 

首先, AI 替我準備了這些上架商品跟折扣內容:

[[2026-01-01-ai-vibe-coding-contract-first-02.png]]

 

接著 AI 替我展開這 24 項測試

[[2026-01-01-ai-vibe-coding-contract-first-03.png]]

看起來很棒, 但是… 你知道這樣的測試 "夠不夠” 嗎?

同樣的, 這不是 AI 的問題, 是命令他做這件事的人的問題｡ 你知道怎樣的測試才算足夠嗎? 如果不夠, 你知道缺了什麼嗎? Vibe Coding 過於容易, 這些問題很容易就被隱藏起來了｡ 同樣的, 要是你沒有能力發現這些狀況, 那很抱歉, 現階段你還不適合用 ai 來開發大型系統…

不過, 這實驗也點出一個血淋淋的現實, 把 code 寫出來的技能, 已經確定 AI 大勝了. 我這篇文章在 2020 的時候發表, 當時很多人還給我 feedback, 說過去完全沒想到這問題能這樣解… 結果現在花幾塊錢 ( 大概只花掉 github copilot - 5 premium request 而已 .. ) 就寫的出來了｡ 我上面條列的缺點, 通通都是 "操作人員” 的缺失, 不是 AI 的缺失…, 還想繼續從事軟體開發, 你要想辦法讓自己跟的上, 變成能夠有效帶領 AI 的角色

# 4. 實驗組: 架構師主導設計 + SDD

看完對照組, 接下來看看我認為比較 "適合” 大型系統的 ai 開發方式｡ SDD 大概已經是開發人員的共識了, 用 SDD 就能得到很精確可靠的成果｡ 那麼問題往左移了, 你能寫出夠好的規格嗎?

我的做法都是從上到下, 逐步落實的｡ 當你還沒有 "規格” 之前, 你該做的是靠 vibe coding 快速的生成 prototype, 並且快速確認這是不是你要的, 確認後這結果就能當作規格的一部分, 逐步有效的擴大, 最小化需要完全人工決定的規格範圍

從架構設計的角度來說, 我常說先看 "全貌” 或是 "主要流程”, 其實拆解之後, 就是掌握關鍵環節的介面設計而已｡ 介面的規格會約束模組之間如何溝通, 而大型系統都會拆解成多個獨立模組或是服務, 個別按照需要滿足的介面規格, 個別開發, 因此介面的設計的好壞, 基本上就定型了整套系統的樣貌｡

我會關注兩個面向的介面, 一個是挖深, 從最上層到下層, 抓出其中的關鍵介面, 確實遵守介面規格, 你會得到能支撐高樓的骨幹基礎建設 (這就像蓋摩天大樓的結構設計)｡ 另一個是擴展, 定義好擴充介面後, 從中心往外擴散, 確實遵守介面規格, 你會得到能持續發展的生態體系, 不需要變更核心設計, 外圍的擴充機制能持續的更新跟發展新功能 (這就像交通建設)｡

同樣的案例, 我換個人物設定, 這次我扮演架構師的角色, 看看差別會在哪｡ 我用這段要求, 在新的 Repo 下啟動開發作業:

> 設計購物車結帳金額計算規則
> 結帳若符合折扣規則, 則要用優惠價格計算.
>
> 我想要的規則有這幾個 (按照優先順序):
>
> 1. 指定商品 (product-id=102), 一次買兩件的話, 這兩件 8 折優惠
> 2. 指定商品 (product-id=128) 買一件, 搭配的商品免費 (product-id=129)
> 3. 結帳總金額大於 1000 元, 折價 100 元
>
> 請替我生成:
>
> 1. 結帳計算邏輯
> 2. 生成樣本資料
> 3. 生成單元測試
>
> 用 dotnet 10, c# 開發
>
> --
> 上述需求, 我要明確指定跨越不同 project 的公開介面, 我要落實 contract-first
> 公開介面一律要經過我的 review, 各個 project 之間要完全遵守 contract 的定義
>
> 請依序協助我完成下列 project:
>
> 1. .Abstraction, 只定義 interface / data model
> 2. .ShopProviders, 模擬商店資訊取得管道, 要能列舉該商店設定的折扣內容與上架的商品內容
> 3. .Tests , 包含 Mock 以及 Unit Tests
> 4. .Core, 基本的實作程式碼
> 5. .Services, Http Rest API
>
> 有任何問題可以現在詢問我
> 沒問題的話就從第一個開始, 建立空白專案給我, 我會給你我的細部規格

其實前半段, 跟實驗組用的 prompt 是一模一樣的, 但是我多補充了後半段的要求｡ 這些內容, 就是平常架構師的日常, 我會強調工作方法, 先把最關鍵的 contract 確認下來, 這邊程式碼的量很低, 我會花足夠的人力跟 AI 互動確認, 完成後將 contract 視為重要的規格, 再靠 SDD 快速完成大範圍的程式碼開發｡

因此, 我要求了工作方法 ( contract-first ), 我要求了共用部分的程式碼結構 ( abstract, providers, core ), 我要求了測試項目 ( tests ), 以及最終要交付的服務 ( service )

## step 1, contract

明確的分級, 最重要的 contract, 程式碼最少, 我花最多力氣 (甚至不惜親手改 code, 親自 review 每一個 interface ), 並且搭配 decision table 來決定 test 範圍, 確保 contract 完全符合我的期待. 這環節完成後, 後面大部分都能靠 SDD 快速完成, 不需要太多人工的介入

初始化的需求, 得到了第一部分的產出:

[[2026-01-01-ai-vibe-coding-contract-first-04.png]]

 要求了 contract-first 的工作方法後, 果然 AI 謹慎的多, 把關鍵的規格 ( interface / model ) 挑出來讓我逐一確認｡ 其實這邊的程式碼很少, 大概上百行而已, 即使逐行全部看完也不吃力｡ 

我抓出 ai 第一個設計不合理的地方, 在於他把 DiscountRule 歸類為 “record”, 而不是歸類成 interface or abstract class, 不同折扣的行為差異, 原本是靠 DiscountRule.Type 的屬性來識別 (我猜之後會用 switch case 來處理不同的規則計算), 這邊被我改掉了｡ 另一個地方是我追加了 "加購建議”, 我希望折扣計算的時候能給消費者提示, 再加購 xxx 的話就可以額外享有 ooo 折扣, 這些都委派給每個折扣規則自己決定, 最後就是我定案的 DiscountRule 版本｡ 無奈我忘了 commit 留下這段過程, 因此只能貼我調整後的 code 給大家看:

```plaintext


/// <summary>
/// 折扣規則定義 (抽象基底類別)
/// </summary>
public abstract class DiscountRule
{
    /// <summary>
    /// 規則編號
    /// </summary>
    public required int Id { get; init; }

    /// <summary>
    /// 規則名稱 (由衍生類別定義)
    /// </summary>
    public abstract string Name { get; }

    /// <summary>
    /// 優先順序 (數字越小優先權越高)
    /// </summary>
    public required int Priority { get; init; }

    /// <summary>
    /// 是否可與其他規則疊加
    /// </summary>
    public bool IsStackable { get; init; } = true;

    /// <summary>
    /// 處理購物車，計算並回傳符合此規則的折扣項目
    /// </summary>
    /// <param name="cart">購物車</param>
    /// <param name="member">會員資訊</param>
    /// <param name="products">商品資訊查詢 (供規則查詢商品單價)</param>
    /// <returns>符合的折扣項目清單</returns>
    public abstract IEnumerable<AppliedDiscount> ProcessCart(Cart cart, Member member, IReadOnlyDictionary<int, Product> products);

    /// <summary>
    /// 取得加購建議
    /// </summary>
    /// <param name="cart">購物車</param>
    /// <param name="member">會員資訊</param>
    /// <param name="products">商品資訊查詢</param>
    /// <returns>加購建議清單</returns>
    public virtual IEnumerable<SuggestedDiscount> GetSuggestions(Cart cart, Member member, IReadOnlyDictionary<int, Product> products)
    {
        return [];
    }
}
```

受惠於過去的訓練與經驗累積, 我看到 interface / data model 的設計大概就能料想未來的運行架構, 因此光是這些資訊 (幾乎都只有定義, 沒有太多 logic code, 因此很快就能 review 完成), 我就能給出不少修正建議｡ 除了前面提到的 DiscountRule 之外, 其他還陸陸續續修正了不少會影響結構的 contract 設計, 例如這是兩段修正的 prompt:

> 先修正 interface(s), 請同時幫我修正對應的 models
>
> 1. ICheckoutService.CalculateAsync, 參數改成 Cart 而不是只有 IEnumerable, 未來可能會包含其他相關資訊, 例如 payment method, 或是是否提供 coupon, points 等資訊, 另外第二個參數請提供 Member, 作為身分識別, 未來會包含會員等級資訊, 或是預設運送地址等相關參數
>
> 2. CheckoutResult 我要有足夠資訊能對應將來產生收據, 請明確列出所有 CartItem[], 並且明確列出符合的 DiscountItems (收據上要列出原價明細, 與符合的每一項折扣, 負項)
>
> 3. 為了未來 ui 操作可能要再加入購物車時即時顯示結帳金額, 追加 Estimate 來試算結帳金額, 這邊可以簡化不需要列出明細, 但是要輸出 總金額, 以及建議資訊 (例如再加購 xxx 就能享有 ooo 折扣)
>
> 4. DiscountRule 改成 abstract class, 需要 virtual IEnumerable ProcessCart(Cart cart, Member member)
>
> 5. 擴充 AppliedDiscount 提示的建議資訊, 能標示建議加購的資訊

> AppliedDiscount 只要表達符合的折扣資訊即可
> 另外用 suggest discount 來表達建議加購的資訊
>
> 移除不必要的 DiscountRule 屬性
>
> - DiscountType -&gt; 不必要
> - Name -&gt; 由衍生的 class 自訂, get only

到這裡為止, contract 總算符合我想像中的樣子了, 第一階段完成, AI 給我這段訊息之後, 我就讓他 commit changes, 並繼續下一步驟:

[[2026-01-01-ai-vibe-coding-contract-first-05.png]]

 

## step 2, in-memory provider

我在構思這專案時, 其實腦袋大概都想好未來應用的藍圖了, 然後從 top down 的角度逐步確認關鍵的介面規格, 最後才把 production 的 code 逐一補上｡ 最外圍的 contract 確認完畢之後, 接下來是系統內部的關鍵介面設計｡ 我這部分要解決的, 主要是: 系統怎麼取得關鍵的資料來源? ( 上架了哪些商品? 啟用了哪些折扣? )

我想要一套能完全基於 code ( in-memory ) 就能運作的系統 (用於開發驗證), 於是經過一番溝通後, AI 給了我這樣的設計, 並且附贈三個折扣規則的實作:

[[2026-01-01-ai-vibe-coding-contract-first-06.png]]

這邊其實很順利, 看完 code 沒有什麼大問題, 我就繼續往下  ~~開發~~  出一張嘴 了

 

## step 3, tests

接下來就是重要的觀念了｡ TDD 不斷的強調, 他的工作方法是先寫 test 再寫 code, 然後在寫 code 的過程中, 就是不斷的把 test 從紅燈變成綠燈的過程, 引導你逐步完成所有的任務｡ 不過, 真的能認真遵守這原則的人其實不多啊, 關鍵的原因不是因為懶, 而是有相當多的人在沒寫出 code 之前, 其實根本不知道要 test 什麼 ( 背後的原因: 你可能是開始寫 code 的時候才開始邊寫邊改 contract )

TDD 要把寫 test 安排在寫 code 之前執行, 背後的原因很單純, 我自己的體會是:
1. 你要藉由 "寫" 測試 的過程, 親自體驗你自己設計出來的 contract 到底好不好用? 如果不好用的話, 現在就要改了, 別執著要把測試寫完, 要把 code 寫完...
1. 如果 "寫" 的很順利, 那就用 AI 輔助, 讓測試覆蓋率涵蓋所有重要的情境, 這步驟越早做, 再往後的步驟越能引導 AI 快速幫你寫出正確的 code (因為有測試, 寫錯了不需要等你 review, AI 就知道該怎麼修正了)

因此, 我的流程規劃中, test 是 ASAP 要執行的項目, (1) 是基本設計, 要被驗證的設計, (2) 則是讓 test 能跑起來的基礎建設, 有他我才能建立起基本的驗證環境, 這裡就是你最早能準備 test 的階段了

還記得之前我寫的這篇 vibe testing 嗎? 要確保 "重要的情境" 有哪些, 我認為 decision table 是個系統化的好選擇, 把如果你的介面都設計好了, 你可以很容易的就用 decision table 來決定你測試的範圍, 這是很有效率的圈訂測試範圍的技巧, 我花了一點 "口舌” (tokens) 跟 ai 溝通我要的測試範圍, 過程我省掉了, 我直接貼最終的結果:

[[2026-01-01-ai-vibe-coding-contract-first-07.png]]

 

[[2026-01-01-ai-vibe-coding-contract-first-08.png]]

 

AI 把我要的條件跟組合都列出來了, C1 \~ C3 是指結帳時購物車內有多少符合折扣條件的關鍵商品購買數量, C4 則是其他充數用的商品..

A1 \~ A3 則是三個折扣規則各命中的折扣金額, A4 是未折扣的總金額, A5 是折扣後的金額, 而按照我要的條件組合 (可重複命中的折扣, 至少要測試到 2 組以上), 總共列出 R01 - R25, 共計 25 組..

確認完 decision table, 接下來 AI 就真的幫我完成了大部分大量的苦差事了, 按照 R01 \~ R25 的要求, 幫我補完 25 個 unit test ..

## 對比 test

這邊各位可以反思一下, 我再這邊的做法, 跟前面對照組的測試有何不同? 我覺得有三個主要的差異:

1. 這邊的測試標的, 是我明確定義過的 contract
2. 這邊測試的條件 (輸入) 跟結果 (輸出), 都是我明確定義過的
3. 這邊測試的程式碼, 其實都有明確的規格 ( contract + decision table 就是最明確的規格了 )

對比前面對照組我只丟了一句 "生成單元測試”, 資訊量其實天差地遠, 對照組的做法其實你根本完全無法 review, 只能再不知情的狀況下選擇接受或是重寫而已｡面對大型系統的開發, 所有不確定性的因素你都該盡力一個一個排除才對｡ 做完 contract 後立刻接著確認 test, 是我能用最小的力氣得到最大範圍的 "精確” 輸出的結果｡ 

這效果, 就像 "複利” 一樣, 我用最少的力氣得到 100% 正確的 contract, 接著我就能用最少的力氣得到 100% 正確的 unit test, 因此後面的步驟可能會產生上萬行的 source code, 這些我已經很有信心的 contract + unit test, 就可以替我驗證完 99% 的 code, 這就是複利的效益, 你能最大化 AI 的力量, 並且最小化 AI 的弱點 (幻覺). 當你熟悉軟體工程的知識跟實作技巧時, 這些技巧就是你控制 AI 最重要的能力｡

接下來, 都是 AI 的苦工, 其實我做的事情並不多, 就是看 AI 不斷的執行測試, 同時替我修正錯誤的過程而已:

[[2026-01-01-ai-vibe-coding-contract-first-09.png]]

花費了 20 分鐘, 我在旁邊納涼, 最後得到了這樣的 unit test (我只貼一小段), 其實還蠻好 code review 的, 結構很單純, 幾乎就是把 decision table 的數字一個一個抄過來而已… 

```csharp

    [Fact]
    public void R04_Rule1_1組_數量2()
    {
        // Arrange: C1=2, C2=0, C3=0
        var cart = CreateCart(2, 0, 0);

        // Act
        var originalTotal = CalculateOriginalTotal(cart);
        var (rule1, rule2, rule3) = ApplyAllRules(cart);
        var finalTotal = originalTotal - rule1 - rule2 - rule3;

        // Assert: 899×2=1798, Rule1: 1798×0.2=359.6, Rule3: 100
        Assert.Equal(1798m, originalTotal);
        Assert.Equal(359.6m, rule1);
        Assert.Equal(0m, rule2);
        Assert.Equal(100m, rule3);
        Assert.Equal(1338.4m, finalTotal);
    }
```

 

## step 4, checkout service

不知有沒有人發現, 不是 contract-first 嗎? 都還沒實作, 那 test 100% 通過率是哪來的?  XDDD

其實到這裡, 真正有實作內容的只有 3 個 DiscountRule 啊, 這邊的實作是 UnitTest 自己補的, 這個步驟我就要開始來寫正規的 CheckoutService 了, 同時把測試調整成使用 CheckoutService, 並且驗證 decision table 表達的所有測試都應該正確通過

[[2026-01-01-ai-vibe-coding-contract-first-10.png]]

 有發現嗎? 軟體工程掌握的夠好的話, 你會發現越後面的步驟雖然要做的事情越多, 但是其實越單純明確, 交給 AI 來做並不大費事｡ 這個步驟我特地把上一步 ai 詢問的訊息一起擷圖, 就是想讓大家知道工作方法的重要｡ 這個步驟, 我只是回答 "OK" 而已, 其他就是讓 AI 慢慢跑, 事情就做完了｡ 

因為累積到這裡, 每個步驟的需求都是非常明確的, 架構也都再我的掌控之中, 剩下的真的只是讓 AI 扮演碼農幫我把 code 都長出來而已｡如果前面的步驟沒有到 100%, 就算只有 1% 沒確認好, 到後面都會放大, 因為那 1%, 你會不得不去 review 相當多 code , 因為你不會知道那 1% 出現在哪裡…

[[2026-01-01-ai-vibe-coding-contract-first-11.png]]

 最後, 沿用原本的 25 test 改成測試 CheckoutService, 另外補上額外的 4 個新測試, 修改至全數通過, 完成這個回合｡ 這步驟最大的收穫, 是我得到了一個能被重複使用 ( CheckoutService ), 並且通過規劃好的測試的購物車結帳計算的程式碼:

```csharp


/// <summary>
/// 結帳計算服務實作
/// </summary>
public class CheckoutService : ICheckoutService
{
    private readonly IProductProvider _productProvider;
    private readonly IDiscountProvider _discountProvider;

    public CheckoutService(IProductProvider productProvider, IDiscountProvider discountProvider)
    {
        _productProvider = productProvider;
        _discountProvider = discountProvider;
    }

    /// <inheritdoc />
    public async Task<CheckoutResult> CalculateAsync(Cart cart, Member member, CancellationToken cancellationToken = default)
    {
        // 取得所有商品資訊
        var productIds = cart.Items.Select(i => i.ProductId).Distinct();
        var products = (await _productProvider.GetProductsByIdsAsync(productIds, cancellationToken))
            .ToDictionary(p => p.Id);

        // 建立明細項目
        var lineItems = cart.Items
            .Where(item => products.ContainsKey(item.ProductId))
            .Select(item =>
            {
                var product = products[item.ProductId];
                return new CheckoutLineItem
                {
                    ProductId = item.ProductId,
                    ProductName = product.Name,
                    UnitPrice = product.Price,
                    Quantity = item.Quantity,
                    Subtotal = product.Price * item.Quantity
                };
            })
            .ToList();

        // 計算原始總金額
        var originalTotal = lineItems.Sum(i => i.Subtotal);

        // 取得折扣規則並計算折扣
        var rules = await _discountProvider.GetActiveDiscountRulesAsync(cancellationToken);
        var discountItems = new List<AppliedDiscount>();
        var appliedNonStackableRule = false;

        foreach (var rule in rules.OrderBy(r => r.Priority))
        {
            // 如果已套用不可疊加的規則，跳過後續規則
            if (appliedNonStackableRule)
                break;

            var appliedDiscounts = rule.ProcessCart(cart, member, products);
            foreach (var discount in appliedDiscounts)
            {
                discountItems.Add(discount);
                
                if (!rule.IsStackable)
                {
                    appliedNonStackableRule = true;
                    break;
                }
            }
        }

        // 計算總折扣與最終金額
        var totalDiscount = discountItems.Sum(d => d.DiscountAmount);
        var finalTotal = Math.Max(0, originalTotal - totalDiscount);

        return new CheckoutResult
        {
            LineItems = lineItems,
            DiscountItems = discountItems,
            OriginalTotal = originalTotal,
            TotalDiscount = totalDiscount,
            FinalTotal = finalTotal
        };
    }

    /// <inheritdoc />
    public async Task<EstimateResult> EstimateAsync(Cart cart, Member member, CancellationToken cancellationToken = default)
    {
        // 取得所有商品資訊 (包含可能的建議商品)
        var allProductIds = cart.Items.Select(i => i.ProductId).Distinct().ToList();
        
        // 先取得購物車內的商品
        var products = (await _productProvider.GetProductsByIdsAsync(allProductIds, cancellationToken))
            .ToDictionary(p => p.Id);

        // 取得所有商品以便建議 (這裡可以優化，只取需要的)
        var allProducts = (await _productProvider.GetAllProductsAsync(cancellationToken))
            .ToDictionary(p => p.Id);

        // 計算原始總金額
        var originalTotal = cart.Items
            .Where(item => products.ContainsKey(item.ProductId))
            .Sum(item => products[item.ProductId].Price * item.Quantity);

        // 取得折扣規則並計算折扣
        var rules = await _discountProvider.GetActiveDiscountRulesAsync(cancellationToken);
        var totalDiscount = 0m;
        var suggestions = new List<SuggestedDiscount>();
        var appliedNonStackableRule = false;

        foreach (var rule in rules.OrderBy(r => r.Priority))
        {
            if (appliedNonStackableRule)
                break;

            // 計算已套用的折扣
            var appliedDiscounts = rule.ProcessCart(cart, member, products);
            foreach (var discount in appliedDiscounts)
            {
                totalDiscount += discount.DiscountAmount;
                
                if (!rule.IsStackable)
                {
                    appliedNonStackableRule = true;
                    break;
                }
            }

            // 取得加購建議
            var ruleSuggestions = rule.GetSuggestions(cart, member, allProducts);
            suggestions.AddRange(ruleSuggestions);
        }

        var finalTotal = Math.Max(0, originalTotal - totalDiscount);

        return new EstimateResult
        {
            OriginalTotal = originalTotal,
            TotalDiscount = totalDiscount,
            FinalTotal = finalTotal,
            Suggestions = suggestions
        };
    }
}
```

## step 6, builder 

最後一哩路了, 從架構的角度來看, 到目前為止, 我在處理的其實都是 domain logic, 沒有太多基礎建設的成分在內, 現在這步驟, 要把所有這些非 business domain 的需求全部都補起來了

這邊我開始補 builder, 要把所有的東西整合起來, 能抽換的地方都用 DI 的方式整理好, 讓使用的人能夠有效率的搭配. 這邊, 我先要求 AI 按照 DI 使用方式的慣例, 替我重構先前的程式碼｡ 我用了這樣的 prompt :

> 調整實作
>
> ShopProviders 只處理初始設定
> 例如設定 discounts, 以及 products 上架
>
> 至於 discount rules 的開發 (系統支援哪幾種 discount rule)
> 以及系統支援哪幾種 load products ( static, load from json, bind to database .. etc )
>
> 同時追加 ShopProvider Builder, 用 di 的做法, 標準化 shop 的建立程序
>
> 這些支援應該放在 Core 專案
> 請執行這些重構, 並且確認通過既有的所有測試, 最後讓我 review changes

同樣我跳過中間的過程了, 最後 AI 給了我這樣的結果報告, 重構成大家習慣的 Builder 使用方式, 自己搭配 Product / Discount 來源的 Provider, 並且再度調整 unit test, 用同樣方式初始化測試環境, 調整完程式, 並且通過所有的測試:

[[2026-01-01-ai-vibe-coding-contract-first-12.png]]

 

## step 7, http api + SDD

到目前為止, 嚴格的來說都還不是 SDD, 只是我用很嚴謹的軟體工程做法, 用很隨興的手段來 vibe coding 而已. 到了要開發 http service 這步驟, 所有開發部署, 監控維運, 效能, 擴充, 資安, 可靠度等等非功能需求通通都浮上檯面了

這邊就真的要拿出真本事了, 所以這段我開始祭出 spec-kit, 用正規的 SDD 來開發了 (終於!! ), 幸運的是, 最難處理的商業邏輯, 我前面都處理掉了, 相關的規格, 我都用更有效率的方式 ( contract + unit test ) 提供了, ai 可以更容易的從程式碼掌握這些資訊, 可以靠 build success 來確認是否符合 contract, 可以靠 test success 來確認是否符合 business logic.

於是, 這個階段就把這些功能 / 非功能需求都湊在一起, 用 spec-kit 來完成最後段落

我在這個 repo 準備好 spec-kit 後, 用這段 specify 指令, 啟動 http api 的開發:

> Follow instructions in [speckit.specify.prompt.md](file:///Users/andrew/code-work/contract-first/demo2/.github/prompts/speckit.specify.prompt.md).
>
> 我要建立 ShoppingCart Http Rest API
> 除了 [ShoppingCart.Services](http://ShoppingCart.Services) 專案之外, 其他專案 ( abstraction, core, providers, tests ) 都屬於共用專案, 不再這次異動的範圍內
>
> 我要符合 domain 的角度來設計 api
> 主要的 entity 要有:
>
> 1. products -&gt; product info access
> 2. member -&gt; current user only
> 3. cart -&gt; current user cart
> 4. checkout -&gt; checkout service, empty cart, accept payment, and create order
>
> api 需要有標準化的認證機制, 並且要能支援 scaleout, 並且有標準化的 observibility 能力, 支援 container

接下來就是一連串的輸出跟詢問, 我貼一段 clarify 的對話當作代表:

[[2026-01-01-ai-vibe-coding-contract-first-13.png]]

 

過程中確認了不少我要求的細節確認, 例如這個是確認資訊安全的部分, token 生命週期的規格:

[[2026-01-01-ai-vibe-coding-contract-first-14.png]]

 

接下來的這段, 大概花了 2 \~ 3 hr, 就放著讓 ai 慢慢跑, 一路跑完 plan, 產生了 156 個 tasks 待執行:

[[2026-01-01-ai-vibe-coding-contract-first-15.png]]

 ( 以下還有一大段, 全部 pass )

最終, 經過 3hr 奮戰, 我得到了:

1. 完全符合我期待的 Http Server, 包含 health check, authentication, cache, openapi spec …
2. 額外送我一個生成 JWT token 的 CLI-tools, 因為我說 JWT token 會由外部服務提供, API 只負責驗證
3. 完整的 dockerfile, 以及 compose 執行環境, AI 幫我準備了一個包含 redis 的驗證環境, 我可以隨時本地端就跑起來


# 5. 對照總結

// TODO: 加入對照表，比較對照組 vs 實驗組的差異
// 面向建議: 介面設計、測試覆蓋、架構掌控、可維護性、跨團隊協作
// 格式範例:
// | 面向 | 對照組（純 Vibe） | 實驗組（Contract-First） |
// |------|------------------|------------------------|
// | 介面設計 | AI 自決，事後才知 | 人工定義，編譯器驗證 |


# 6. 心得：架構師在 AI 時代的定位

## 6.1 AI Coding 時代，你還需要 IDE 嗎？

我最近跟幾個資深朋友聊了一個問題：「當你已經習慣讓 coding agent 寫所有的 code，你還需要 IDE 嗎？如果 IDE 都不需要了，那 debugger 呢？」

有趣的是，兩派說法都有。我是沒辦法完全拋棄 IDE 的那一派。

我的理由很簡單：目前的 coding agent 碰到問題，除錯手段大多還是「黑箱驗證」。Agent 雖然看得到 source code，但對正在跑的 process 狀態其實一無所知，只能靠 log、test 等外圍訊號去推敲。對我來說這種驗證太粗糙——遇到錯上加錯的巧合，你很可能就抓不到那個 bug。

對我而言，目前至少這幾個情境我仍然離不開 IDE：

1. **核心邏輯驗證**：演算法、平行處理、難以重現的狀況，我沒辦法只靠 log/test 間接驗證，還是得用 debugger 實際確認執行狀態。

2. **用 code 定義規格**：Contract（interface code）本身就是最理想的設計規格。手寫 code 最快能忠實輸出我腦袋裡的想法，比起自然語言，code 是更精準的敘述方式。

3. **Review 關鍵介面**：即使 AI 寫的 code，關鍵的 interface 我必定會逐行 review。我驗證的不是程式碼邏輯，而是介面定義——因為這介面定義，是切割後相關專案的重要規格。


## 6.2 IDE 的未來：從工具到協作介面

順著這個脈絡，我去找了業界大神的看法，意外看到 Zed 創辦人 Nathan Sobo（Atom 也是出自他手）的專訪：[Why IDEs Won't Die in the Age of AI Coding](https://www.youtube.com/watch?v=...)。

他從「IDE 未來會變什麼樣貌」的角度切入，幾個觀點讓我大開眼界：

1. 如果 IDE 能擺脫傳統 git 協作節奏（edit/commit/push，對方再 pull/edit...），改成像 Google Docs 那種即時協作，溝通方式會整個改寫。

2. 那如果「協作的另一個人」是 AI 呢？他因此訂了 ACP（Agent Client Protocol），讓主流 coding agent 能透過 protocol 掛上 Zed。

3. 未來 IDE 應該會變成「人」跟 AI 協作的介面：你查某一行 code 的時候，IDE 應該能回溯——你下了什麼 prompt、agent 根據哪些前後文、查了哪些文件，才寫出這段 code。

Nathan 談的是 IDE 的「未來」，而我的問題沒那麼遠，只是談「現在」的 IDE 還有沒有價值。我的答案是：**有，而且很重要**。


## 6.3 架構師的價值：切割邊界 + 定義 Contract

回到這篇文章的主題。架構師過去的能力，就是善用各種軟體工程技巧，有系統有效率地切割邊界，讓一個大黑箱拆解成有明確邊界定義的多個小黑箱。

如果是 3D 世界的黑箱，尺寸切一半，一個大黑箱就能拆成八個小黑箱，多了多個邊界的定義，讓你能更精準地掌控每個小黑箱的行為。資訊工程內有個常識：規模越大，複雜度通常是指數上升。因此你要簡化任何問題的第一步就是「切割」。

過去架構師能力發揮的最大瓶頸是：**你設計出來的「理想」架構，沒有足夠的高素質人力去實現它**。

而 AI 能填補這個缺口。瓶頸被移除後，架構師的能力開始會大幅提升。當系統只有一半大的時候（用 line of code 來看），複雜度大約降低到 (1/2)³。在 AI 能力還沒到 2³ 前，架構師就已經有能力掌控 2 × (1/2)³ 的系統了——沒這種能力的團隊，則還無法放大 vibe coding 的能力到這程度。

切割的關鍵能力，其實是老掉牙的傳統技能：**抽象化、封裝、解耦**。包含 OOP 強調的抽象化、封裝、繼承、多型，軟體工程強調的 SOLID、DI，微服務的拆分原則——都屬於這類。


## 6.4 結語：不是取代，是放大

Coding 交給 AI 來負責，我覺得已經沒有懸念了。接下來競賽的是：**你能多有效地運用這些技巧（架構師技能）來跟 AI Agent 團隊合作？**

模型能力會進步，但這跟架構師的能力不衝突。掌握得當，你就有能力用同樣模型，控制比其他人規模還大的開發專案。

最後給個建議：

> **別太早丟掉你的 IDE**。只要人類還有「面對 code」的需求，你就還需要 IDE。同時，挑選一個對 Agent 友善的 IDE 也很重要——這會是未來人機協作的關鍵介面。


<!-- ====== 原始心得素材（保留備查）======
---

> vibe coding demorequirement:
> discount calchow: separate frontend / backend / core lib and engine ?
> if 3 teams, who decision the interface between them ?ideal: architect ( or tech lead, staff engineer else .. ) develop the interface ( higher abstraction ), with dummy / test, and make sure it work for major scenario.use interface as specs, delivery to 3 teams, and develop it

2025, AI 讓很多事情的 "平衡” 被打破了… ~~Junior 的工作機會少了, 但是某些能善用 AI 的 Junior 也搶走了跟不上 AI 的 Senior 工作機會;~~ AI 讓 coding 的速度改變了, 多出來的產能, 迫使人們花更多時間在 code review / testing 上, 但是這樣的 "攻防” 戰, 總覺的不是辦法, 因為 AI 會一直進步, 終有一天會守不住的, AI 會進步到你連 code review 都跟不上, 一定有某些工作方法也需要跟著改變, 才能突破這 "舊流程” 替人類自己設下的瓶頸.. 重新建立新的平衡…

## 

noteAI coding, 你還需要 "自己寫 code" 嗎? 你還需要 IDE + debugger 嗎?
我用了各種 coding agent, 除錯方式都是 "黑箱", 簡單的說就是印 log, 看 log 這種
AI 會善用很多工具做到很強的 "watch" 能力, 但終究不是 debugger, 監控不到某個變數, 也無法倒出記憶體內的內容..
什麼情況這些事情是免不了的?

1. core lib / sdk, 你定義的 interface 會被別人使用, 開發跟使用, 是兩個不同的 team, 你得做好決定 (所以你要自己看, 你要看的懂 interface, 跟判別 interface design 的好壞)
2. interface 背後的行為, 好不好用, 你要有能力做出 mock, 親自確認每個步驟都如你預期, 所以你可以用 AI 生成 mock + test case, 用六角架構的觀念來看, 撇開根 domain 無關的所有細節，複雜度降低到你能輕易 review 的程度, 把 interface 設計好，當作規格的一部分

架構師能力發揮最大的瓶頸: 你設計出來的 "理想" 架構，沒有足夠的高素質人力去實現它。
而 AI 能填補這缺口。瓶頸被移除，架構師的能力開始會大幅提升。複雜且龐大的系統，若能被正確的設計，則能切割成獨立的小塊。
當系統只有一半大的時候 (用 line of code 來看)，複雜度大約降低到 (1/2)^3，在 AI 能力還沒到 2^3 前，架構師就已經有能力掌控 2 x (1/2)^3 的系統了，沒這種能力的團隊，則還無法放大 vibe coding 的能力到這程度

切割的關鍵能力，其實是老掉牙的傳統技能: 抽象化，封裝，解耦等等這類技巧...

vibe coding 基本上就是黑箱, 你輸入 prompt, requirement, even specs
可以看到靜態 (檔案) 的輸出, code, db schema ... etc

寫出 code 的思考過程是黑箱, 執行當下的運作細節也被遮蔽 ( AI 還沒有辦法很精準的操作 debugger, code 不是你寫得基本上要有效的 trace 也不容易 ), 如何能有效的掌握這黑箱就是能力的差距

架構師過去的能力，就是善用各種軟體工程的技巧，有系統有效率的切割邊界，讓一個大黑箱拆解成有明確邊界定義的多個小黑箱。如果是 3D 世界的黑箱, 尺寸切一半, 一個大黑箱就能拆成八個小黑箱, 多了多個邊界的定義, 讓你能更精準的掌控每個小黑箱的行為。

Coding 交給 AI 來負責，我覺得已經沒有懸念了，接下來競賽的是，你能多有效的運用這樣的技巧 (架構師技能) 來跟 AI Agent 團隊合作? 模型能力會進步，但是這跟架構師的能力不衝突。掌握得當你就有能力用同樣模型，控制比其他人規模還大的開發專案

回顧幾個相關的領域技能，都對 "拆解" 有很好的效果。包含微服務，包含 OOP 強調的抽象化，封裝，繼承，多型，軟體工程強調的 SOLID，DI 等等技巧都屬於這類。

我拿過去示範過的折扣計算，用兩種方式個別實作一次，讓大家體驗一下差別

# 整合修訂版本 - 2026/01/03 02:04

我最近跟幾個朋友聊了一個問題 (都很資深, 甚至有 Claude Code 用到出神入化的那種) :
「當你已經能適應讓 coding agent 寫所有的 code, 你還需要 IDE 嗎? 如果 IDE 都不需要了, 那 debugger 呢?」

對我而言, 若有這三種需求時, IDE 還是必要的:

1. Code Viewer

2. Debugger

3. Edit Code (但這真的越來越少了, 我只剩下寫 interface 時還會自己手寫)

有趣的是, 兩派說法都有｡ 我是沒辦法完全拋棄 IDE 的那一派｡ 我相信 coding agent 的能力, 但是我覺得關鍵的 code 還是得用 debugger trace 一次, 確保執行方式跟想像一致｡

我的理由很簡單: 目前的 coding agent 碰到問題, 除錯手段大多還是「黑箱驗證」｡ Agent 雖然看得到 source code, 但對正在跑的 process 狀態其實一無所知, 只能靠 log, test 等外圍訊號去推敲｡ 對我來說這種驗證太粗糙; 遇到錯上加錯的巧合, 你很可能就抓不到那個 bug｡

順著這個脈絡, 我去找了業界大神的看法, 意外看到這段訪談, 讓我看到不同的觀點:

Why IDEs Won't Die in the Age of AI Coding: Zed Founder Nathan Sobo

(影片連結放留言)｡

專訪的對象: Nathan Sobo (Atom / Zed 都是出自他手) 從「IDE 未來會變什麼樣貌」的角度切入, 我蠻認同他的幾個觀點:

1. 如果 IDE 能擺脫傳統 git 協作節奏 (edit/commit/push, 對方再 pull/edit...), 改成像 Google Docs 那種即時協作, 溝通方式會整個改寫｡

2. 那如果「協作的另一個人」是 AI 呢? 他因此訂了 ACP (agent client protocol), 讓主流 coding agent 能透過 protocol 掛上 Zed｡

3. 未來 IDE 應該會變成「人」跟 AI 協作的介面: 你查某一行 code 的時候, IDE 應該能回溯 - 你下了什麼 prompt, agent 根據哪些前後文, 查了哪些文件, 才寫出這段 code｡

看完我真的大開眼界｡ Nathan 是在回答「IDE 下一步會往哪裡走」, 而我的問題沒那麼遠, 只是談現在的 IDE 還有沒有價值? 我的答案仍然是: 有｡

對我而言, 目前開發的情境中, 至少這幾個情境我仍然離不開 IDE:

1. 核心邏輯驗證:
   黑箱驗證仍然不足, 我需要更清楚的觀測 (trace) 執行過程｡
   身為架構師, 我偶爾還是要面對特定領域的 core logic: 演算法, 平行處理, 難以重現的狀況｡ 這種東西我沒辦法只靠 log / test 間接驗證, 還是得用 debugger 實際確認執行狀態｡ 到目前為止, 我用過的 coding agent 都還沒辦法直接操作 debugger｡ 即使我挖出 gdb 這種命令列除錯工具也是一樣 (這什麼骨董工具... XDD)｡ 如果哪天 agent 連 debugger 都能用, 我可能會改觀｡

2. 我需要用 code 定義規格:
   Contract (interface code) 本身就是最理想的設計規格｡
   當我需要用「code」來定義 spec 的時候 (contract-first 那種), 手寫 code 最快能忠實的輸出我腦袋裡的想法, 就算不手寫, 也是幾句敘述讓 agent 幫我產出後我直接修改 code. 這情況下 IDE 也很難被取代｡ 比起自然語言, code 是更精準的敘述方式｡

若能選擇, 我更喜歡直接用語言的 interface 來當作規格, 因為這樣就能讓編譯器來驗證 code 是否符合規格 (C# 在這點真的很好用)｡

我拿五年前寫的〈抽象化程式設計〉裡折扣計算的案例來驗證, 用 GitHub Copilot 重寫了一次｡ 這是個充分運用 OOP 多型技巧的案例: 先定義折扣規則的規格 IDiscountRule, 再實作 DiscountEngine 在結帳過程中逐條套用規則｡ 而且它要支援後續由其他團隊或其他專案, 追加各種折扣規則 (implement IDiscountRule) 並掛載到系統內使用｡

由於 IDiscountRule 是跨多個專案運作的重要規格, 如果我沒有先把它定義清楚, 就把整個需求丟給 AI 處理, 得到的結果雖然可以動, 但 interface 往往沒有達到我的期待｡ 更麻煩的是, 這類規格若要事後修正, 又牽涉跨專案 (通常 coding agent 都是一次處理一個專案), 甚至跨團隊, 那它就更需要由架構師預先定義清楚｡

結果蠻有意思的｡ 實際操作過一次後 (程式碼我另外再發文貼出來示範, 這次就略過) , 我更確認了我的想法: IDE / Debugger / 手寫 code 可能不再是所有人的必須｡ 但是對於架構師要掌控系統邊界 (contract), 或是核心邏輯 (core) 的時候, 仍是重要的工具跟手段｡ 這時 code 不是「產出」, 而是「spec」｡ 用 code 來寫 spec, 你就能有更多工具 (compiler) 替你保證輸出的正確性｡

# 整合修訂版 v2, 2025/01/03 16:06

認真看完這段 Zed / Atom 開發者 Nathan Sobo 的專訪, 很高興有看到覺得 IDE 還是有必要存在的見解了, 這篇就借題發揮一下, 聊一下未來還需不需要 IDE 這題目｡

我最近跟幾個朋友聊了一個問題 (都是很資深的狠角色, 用 AI coding 的程度都已經到大神等級的):

" 你現在寫 code 還會需要用到 Debugger 嗎? "

這件事對我來說, 意義非凡｡ 我大概在 2003 那個年代, 看了 eXtreme Programming, 也看了約耳談軟體, 有幾個觀念就被刻在我腦袋裡了, 其中包含一個我到現在還維持的好習慣: 我一定會親自用 debugger 至少跑過一次我寫的 code ..., 確保程式的流程, 還有變數的變化, 跟我想像的一樣｡

不過, 現在 AI coding 實在太吸引人了, AI 寫出來的 code 你都不見得看的懂了, 何況 trace 一次確認過程? ( 你會知道這個 if 現在 "應該” 跑 true or false part? 這個變數現在 “應該” 是什麼數值才正確?

我自己的看法是: 我還是會繼續用 IDE, 因為這樣我才有操作 debugger 的空間｡ 目前的 coding agent, 從寫完 code 後, 編譯 + 執行 到看到結果為止, 中間的過程其實對 agent 來說是個黑箱, coding agent 其實是不清楚過程的 (畢竟這些資訊, 由其實 process 執行的過程, 每個變數的內容, 記憶體的內容都不在 coding agent 的 context 內), 因此當我提出各種 "驗證” 的要求時, 其實 coding agent 都會很巧妙地操作 code 寫 log, 然後用盡各種手段來查閱 log 檢查看看有沒有我講的問題…｡

這就是我擔心的, 如果我想確認的狀態, 細緻到變數內容何時被改變? 或是我想確認 thread safe 的狀況是否有做到位, 這些要求其實都不容易靠 "黑箱驗證” 的手段來確認, IDE 的價值就在這種時候, 抓這類問題 AI 還沒進化到能操作 gbd 的程度…

不過, 說真的就算是我也不需要到每一行 code 都用這高標準對待, 我會先觀察整個 project 的全貌, 每個應用應該都會有特別關鍵的核心邏輯, 在這個應用內絕對不能錯的那部分, 如果有的話, 我的習慣會是:

1. 先做好邊界劃分, 把核心邏輯的部分獨立出來, 不處理其他工程相關 (網路, 檔案, 資料庫等等)
2. 替這部份核心邏輯定義好 interface ( 語言能直接支援的話最好, C# 或 Java, 在這部分都很合適 ), 針對 interface 寫 test
3. 拿 interface 當作 spec, 開始填 implementation 的程式碼, 執行 test, 用 debugger 確認 code 的執行過程

這邊的 "劃分邊界”, 其實就是多年擔任架構師養成的另一個習慣, 資訊工程內有個常識, 規模越大, 複雜度通常是指數上升, 因此你要簡化任何問題的第一步就是 "切割", 而怎樣有效的切割則是個學問, 不論是 class / object 的切割, 或是大到單體切割成微服務, 談的都是切割的技巧, 而你切了一刀, 切的部分就有新的 interface 需要被定義｡ 這刀切的好壞, 直接影響到你的系統架構的優劣

因此, 重要的專案, 即使有 coding agent 加持, 我仍然需要 IDE 做好兩件事:

1. 關鍵的 interface ( code ), 我會手寫, 或是讓 AI 寫完我必定會 "逐行 review”, 我驗證的不是程式碼邏輯, 而是介面定義｡ 因為這介面定義, 是切割後的相關專案的重要規格 (對, 就是 spec), 當我能用 code 定義 spec, 後面的各種驗證, 在 build 的過程中, 編譯器就能幫我抓出來
2. 關鍵的 interface, 我會讓 AI 替我產生 unit test, 雖然還沒有 implementation, 但是大部分語言這時都已經能編譯了, 編譯器會幫我挑出語法問題 (例: 沒有正確 implement interface), 同時我會 review test code, 檢查 code 是否有正確的表達我的驗證情境 ( test scenario ? )
3. 關鍵的 implementation ( code ), 我會用 AI 來寫, 或是自己手寫不拘 (看我當下判斷), 寫完後我會用上述步驟, 用 debugger 至跑跑過一次, 原因同上不再贅述

這過程, 正好是 IDE 提供的三個關鍵操作, edit code, view code, run code with debugger … 也是我還離不開 IDE 的主要原因｡ 其實很多問題都沒有標準答案, 決策也不是單純的二分法, 在這些問題仍然需要靠 "人” 來解決的時候, IDE 就還有存在的必要｡

不過, 以上都還是我自己對 IDE 的看法, 跟這段專訪沒啥關係, 專訪影片內 Nathon 提了許多很棒的見解, IDE 應該扮演人跟 AI 溝通 “code” 的終極介面, 這很有意思, 也因為這樣他徹底放棄了用 web + javascript 技術來開發 IDE ( 效能太差, 他想要的效能是你敲了一個字, 螢幕就要在下次頁面刷新時就顯示內容 ), 改用 Rust + GPU.. 因為他認為, 如果多人協作能像 google docs 這樣的互動, 比起你 commit + push , 另一個人 pull + review 有效率的多了. 而這個 "多人” 如果升級成 "多個 Agent” , 也能用一樣的互動方式呢?

這樣的協作方式, 是他想像的 "未來” IDE, 看到這邊我更期待了｡ 原本我只是期待 Agent 要能駕馭操作 Debugger 這種程度的功能, 而 Nathon 給我的願景則更往前跨了一步..

最後, 我的看法是:

別太早丟掉你的 IDE , 只要人類還有 "面對” code 的需求, 你就還需要 IDE, 挑選一個對 Agent 友善的 IDE 也很重要, 看完這段專訪, 了解他背後的理念後, 我開始對 Zed 這 IDE 感興趣了 :D, 如果你有相關的見解, 也歡迎在底下留言討論

影片的連結, 我放在留言

# Notes, 2026/01/14

AI coding 再厲害, 有些需要人工堅守 review 的原則仍然不能放過

我舉幾個例子:

1. 公開的介面設計 ( ex: API, data model, schema )
   既然都要 review, 最好的是在一開始 design 的時候就介入 (不管有沒有用 ai coding)
2. 架構上關鍵的設計 ( ex: Abstract class, Bridge … etc )
   (…)
3. 跨團隊 / 跨專案約定的設計
   不同團隊即使都用 ai coding, 也是獨立的 agent 在處理, 任何一個 ai 都沒辦法同時兼顧… 因此需要人為
   的介入 review, 最理想的是這些 "約定” 能被系統化, 例如有共用套件只描述 interface, 雙方
   同時引用這套件, 並且各自確保能成功通過編譯

====== 原始心得素材結束 ====== -->