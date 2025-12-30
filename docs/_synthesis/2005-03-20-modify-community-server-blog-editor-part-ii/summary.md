---
layout: synthesis
title: "修改 Community Server 的 blog editor ( Part II )"
synthesis_type: summary
source_post: /2005/03/20/modify-community-server-blog-editor-part-ii/
redirect_from:
  - /2005/03/20/modify-community-server-blog-editor-part-ii/summary/
---

# 修改 Community Server 的 blog editor ( Part II )

## 摘要提示
- Provider Pattern: Community Server 多處採用 Provider Pattern，讓功能可藉由設定輕鬆替換與擴充
- TextEditorWrapper: 繼承並客製 TextEditorWrapper，加入所需功能與自訂工具列
- CommunityServer 1.0: 原始碼架構設計良好，顯示三位作者的工程實力與可維護性
- 設定切換: 透過修改 communityserver.config 將自製 Wrapper 掛載生效
- 表情符號整合: 將表情符號加入編輯器 Toolbar，提升編輯體驗
- FreeTextBox 功能: 開啟原本隱藏的 FreeTextBox 進階功能，強化編輯能力
- 開發流程: 研究原始碼、繼承擴充、設定注入，快速驗證與迭代
- 可擴充性: 同一模式也應用於 membership、roles、auth 等安全機制
- 使用體驗: 實作後功能齊全，用起來更順手、滿意度提升
- 後續計畫: 計畫持續修改系統其他部分，探索更多可客製化的點

## 全文重點
作者研究了 Community Server 1.0 的原始碼後，讚賞其整體架構設計，尤其是廣泛運用 Provider Pattern 的作法。這種設計讓系統中多個核心元件（包含會員、角色、驗證等安全機制）都能以相同模式被替換與擴充：開發者只要撰寫相容的 Provider，並於設定檔切換，即可無痛替換實作。延續前一篇討論的 TextEditor Wrapper，作者這次實際動手擴充該元件：透過繼承原有的 TextEditorWrapper，加上所需功能後，在 communityserver.config 中將自訂的 Wrapper 掛上就能立即生效。如此便突破了先前認為無法修改的限制，不僅把表情符號加入編輯器的工具列，還開啟了 FreeTextBox 原先未啟用的進階功能，讓編輯體驗大幅提升。雖然日常最常用的仍是少數功能，但能自由掌控與調整的彈性，使得使用上的「爽度」顯著增加。最後，作者表示會持續挑戰系統的其他區塊，嘗試更多基於 Provider Pattern 的客製化可能，進一步驗證 Community Server 架構的可延展性與實務效益。

## 段落重點
### Provider Pattern 與架構設計的讚賞
作者深入閱讀 Community Server 1.0 的原始碼後，發現系統在多個面向上採用 Provider Pattern，包含會員、角色與驗證等安全相關模組。這種模式讓功能的實作與系統的使用介面解耦，開發者只需撰寫符合介面的 Provider，便能藉由設定快速切換不同實作，達到高度可替換性與擴充性。作者特別稱讚三位作者的整體架構安排漂亮、清晰，顯示出良好的工程設計思維。此架構也為後續客製化奠定基礎，降低修改風險並提升維護的便利性。

### 客製 TextEditorWrapper：從繼承到設定掛載
延續前一篇對 TextEditor Wrapper 的討論，作者這次實作了實際的擴充流程：先透過繼承既有的 TextEditorWrapper 加入所需功能，完成後在 communityserver.config 進行設定調整，將自製的 Wrapper 掛入系統。此舉成功解除先前被認為難以更動的限制，包含將表情符號加入編輯器的工具列，以及開啟 FreeTextBox 的進階功能。結果是編輯工具更好用、選項更完整，雖然日常常用功能仍不多，但能自訂並全面掌握的感受明顯提升，帶來更高的使用滿意度與生產力。

### 後續展望：持續改造更多模組
在編輯器客製化獲得成功後，作者計畫進一步嘗試修改系統其他部分，延續 Provider Pattern 的擴充思路，探索更多可替換元件的可能性。透過相同方法（研究原始碼、繼承擴充、調整設定），預期可在不侵入核心的前提下持續優化功能與體驗。此經驗也再次驗證 Community Server 架構的可延展性：當系統以清楚的抽象與設定為中心設計時，後續維護與自訂便能更快速、風險更低，讓實務應用更具彈性。作者也對未來的改造挑戰表達期待，準備在其他模組上複製這次的成功經驗。

## 資訊整理

### 知識架構圖
1. 前置知識： 
   - 基本 .NET/C# 語言與面向物件繼承
   - ASP.NET Web Forms 與伺服器控制項基礎
   - Provider Pattern 概念與配置（web.config/communityserver.config）
   - Community Server 1.0 專案結構與建置流程
2. 核心概念：
   - Provider Pattern：以介面/抽象類別解耦實作，透過設定切換 Provider
   - TextEditor Wrapper：編輯器包裝層，作為可替換的 Provider 實作點
   - 組態驅動（Configuration-driven）：在 communityserver.config 指定自訂 Wrapper
   - 擴充既有控制項（FreeTextBox）：開啟進階功能與客製工具列（如表情符號）
   - 模組化安全機制：membership/roles/auth 同樣以 Provider 實作，易於替換
3. 技術依賴：
   - Community Server 核心依賴 Provider 抽象 → 由 TextEditorWrapper 具體實作
   - FreeTextBox 等第三方/內建控制項 → 由 Wrapper 進行進階設定與功能開關
   - 組態系統（communityserver.config）→ 驅動載入何種 Provider/Wrapper
   - ASP.NET Page Lifecycle → 控制項初始化與渲染時機
4. 應用場景：
   - 自訂部落格編輯器功能（工具列、表情符號、格式化工具）
   - 在不改核心程式碼的前提下替換編輯器或安全機制
   - 針對不同站台/環境以組態快速切換 Provider
   - 將第三方控制項進階功能整合進平台

### 學習路徑建議
1. 入門者路徑：
   - 了解 Provider Pattern 與 .NET 組態檔基礎
   - 熟悉 Community Server 專案架構與 TextEditorWrapper 的角色
   - 嘗試在不改碼的情況下調整 communityserver.config 觀察行為變化
2. 進階者路徑：
   - 閱讀 Community Server 1.0 原始碼，理清 Provider 抽象與依賴關係
   - 繼承 TextEditorWrapper，增添自訂工具列項目（如表情符號）
   - 探索並啟用 FreeTextBox 的進階功能，處理相依設定與事件
3. 實戰路徑：
   - 開發一個自訂的 TextEditorWrapper，封裝常用工具與樣式
   - 以 communityserver.config 切換至新 Wrapper，做 A/B 驗證
   - 規劃通用的 Provider 設計，日後可平移至 security/membership 等模組

### 關鍵要點清單
- Provider Pattern 架構：以可替換的 Provider 實作解耦核心與變動功能，透過設定切換 (優先級: 高)
- TextEditorWrapper 角色：作為編輯器抽象包裝層，便於擴充與替換 (優先級: 高)
- communityserver.config 設定：以組態掛載自訂 Wrapper，無需改動核心程式碼 (優先級: 高)
- FreeTextBox 進階功能：透過 Wrapper 開啟/控制進階編輯能力，提升編輯體驗 (優先級: 中)
- 工具列客製（Toolbar）：在 Wrapper 中加入表情符號等自訂按鈕 (優先級: 中)
- 安全機制 Provider 化：membership/roles/auth 同樣以 Provider 設計，便於橫向擴充 (優先級: 中)
- 原始碼閱讀能力：理解架構與抽象點，找出正確擴充接點 (優先級: 高)
- 面向物件繼承/覆寫：以繼承 Wrapper 的方式注入新行為 (優先級: 高)
- 組態驅動開發：以設定檔控制行為，提升部屬與維護彈性 (優先級: 中)
- 模組化與低耦合：將可變部分隔離為 Provider，維持核心穩定 (優先級: 高)
- 不侵入式改造：以 Wrapper/設定替換達成改造，降低升級風險 (優先級: 中)
- 相容性與回退策略：設定層面可快速回退至預設 Provider (優先級: 中)
- 測試與驗證：切換 Provider 後需驗證編輯器功能完整與穩定 (優先級: 中)
- UI/UX 提升：表情符號與常用進階功能提高編輯「爽度」與效率 (優先級: 低)
- 可移植性思維：在編輯器成功經驗上，擴展至其他模組（如安全、儲存） (優先級: 中)