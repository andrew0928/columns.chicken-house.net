# 架構師觀點 - API First 的開發策略

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 什麼是「API First」的開發策略？
API First 指的是在系統開發流程中，先以 API（即服務對外的介面與合約）為核心來思考與設計，再展開後續的程式實作、UI/UX 與基礎建設工作。也就是說，先把 API 規格（Contract）訂好並獲得利害關係人 (stakeholders) 的回饋，之後所有程式碼都依此合約開發。

## Q: 為什麼 API 規格必須在一開始就設計並盡量保持穩定？
API 規格就是各系統、各團隊彼此協作的「合約」。  
一旦 API 對外發布，任何大幅修改都會影響所有呼叫端，修改成本極高；因此必須在專案初期就花時間把合約設計正確，之後才能在敏捷與 DevOps 的快速循環中，持續交付而不被介面變動拖累。

## Q: API First 與敏捷 / DevOps「快速交付、持續改善」的精神會衝突嗎？
不會。API First 先訂出介面合約，反而能讓團隊更早取得利害關係人回饋，驗證 domain/service 設計是否正確，之後每個迭代只要遵守合約即可並行開發與部署，與 DevOps 的快速交付高度相容。

## Q: 團隊想評估自己對 API First 的「期待」時，可以從哪三個面向切入？
1. 產品面：服務是先設計 UI 還是先設計 API？  
2. 技術面：先寫可運作程式再「抽」API，還是先訂 API 規格再並行開發前後端？  
3. 經營面：API 只是產品附帶功能，還是被當成獨立產品與商業模式來經營？  
若答案偏向 API 端，表示團隊越趨近 API First。

## Q: Amazon 創辦人 Jeff Bezos 2002 年的內部備忘錄對 API 有何要求？
Bezos 規定所有團隊必須以 Service Interface (API) 作為與其他團隊溝通的唯一方式，不可直接透過共用資料庫等手段交換資料；所有介面都要能對外公開，違者將被開除。這一規定奠定了 AWS 服務化、平台化的基礎。

## Q: 架構師在敏捷團隊推動 API First 時應扮演什麼角色？
架構師需：
1. 看見長期 Roadmap（技術與領域 Domain）；  
2. 抽象化需求，設計核心機制及其 Interface；  
3. 與多團隊溝通並確保 everyone on the same page；  
4. 支援開發者（指導、工具、框架）；  
5. 監督交付成果符合最初 Architecture 設計。  
簡言之，就是守護長期目標並透過良好介面設計貫穿整個開發生命週期。

## Q: API First 能為企業帶來哪些商業價值（API 經濟）？
標準化的 API 讓服務易於整合、自動化及規模化，進而：
1. 降低客製整合成本，擴大客戶群；  
2. 促成合作夥伴或第三方開發者在你服務上創造新應用，形成生態系；  
3. 讓公司既能產品化又能客製化，兼顧效率與彈性。

## Q: 採用 API First 時常見的失敗模式（Anti-pattern）是什麼？
把重心放在命名規則、HTTP 風格等「技術細節」合規，而忽略 API 是否真正描述並解決核心商業領域 (domain) 問題。結果會得到「格式完美卻無法解決需求」的 API。

## Q: 若 API 要保持精簡又要好用，除了在介面上堆砌複雜度，還有什麼手段？
可以透過 SDK、Code Template、BFF（Backend For Frontend）等方式，讓呼叫端快易取用；API 本身保持最小且穩定，複雜組合邏輯則放在呼叫端或專用適配層，兼顧彈性與易用性。

## Q: 建立 API First 能力與文化，可參考哪些書籍與學習資源？
1. Continuous API Management（持續 API 治理）：探討 API 生命週期與治理。  
2. API Design Patterns：整理 30 種常見 RESTful API 介面設計模式。  
3. Software Engineering at Google：從 Google 角度談軟體工程、文化與技術決策。