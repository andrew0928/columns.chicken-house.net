# 修改 Community Server 的 blog editor ( Part II )

## 摘要提示
- Community Server 架構: 1.0 版大量運用 Provider Pattern，模組化程度高。
- TextEditorWrapper: 編輯器外掛同樣以 Provider Pattern 實作，易於替換。
- 自訂 Wrapper: 透過繼承方式快速加入客製功能。
- 設定檔切換: 只需修改 communityserver.config 即可啟用新 Provider。
- 表情符號整合: 將自訂表情加入工具列，使用體驗大幅提升。
- FreeTextBox 進階功能: 解鎖原本隱藏的高階功能。
- 軟體可維護性: Provider 結構簡化未來升級與擴充工作。
- 開發效率: 不需動到核心程式碼即可完成深度客製。
- 測試結果: 編輯器外觀與操作更符合需求，爽度倍增。
- 後續計畫: 作者預告將持續改造其他 Community Server 元件。

## 全文重點
作者在深入研究 Community Server 1.0 原始碼後，對其清晰的三層架構與廣泛運用的 Provider Pattern 欣賞不已。Provider Pattern 讓系統中的多數服務（如會員、角色與驗證機制）都可被抽換，只需在組態檔改變指向的 Provider 名稱，即可切換到另一組實作。基於相同原理，本文聚焦於 TextEditorWrapper，這是包裝部落格編輯器的外掛層。作者藉由繼承官方 Wrapper，加入自訂功能，再在 communityserver.config 把原本的 Wrapper 切換成自己寫的類別，便實現了完整替換。

具體成效包括：將原先缺乏的表情符號全部嵌入編輯器工具列，並開啟 FreeTextBox 隱藏的進階選項，讓排版與媒體功能更豐富。整個過程無須修改任何核心程式碼，顯示 Provider 架構的彈性與維護優勢。文章最後作者表示實驗成功，並計畫接續對 Community Server 的其他模組進行同樣的客製化嘗試。

## 段落重點
### 架構分析與 Provider Pattern 運用
作者花時間閱讀 Community Server 1.0 的原始碼，指出三位核心作者以 Provider Pattern 為系統骨幹，從安全性模組到編輯器包裝層都採相同策略。此模式透過介面定義與組態檔的鬆耦合，讓開發者能自行撰寫替代 Provider，並在不動核心程式的前提下切換功能，顯著提升可維護性與擴充彈性。

### 客製化 TextEditorWrapper 的實作與成果
鎖定 TextEditorWrapper 後，作者繼承官方類別，加入自訂需求：一是整合完整表情符號套件到工具列，二是開啟 FreeTextBox 的進階排版功能。完成後在 communityserver.config 指定新的 Wrapper，便立即生效。實作結果驗證 Provider 架構可行性，使用者在編輯文章時獲得更直覺、豐富的操作體驗，也鼓勵作者未來持續改造其他模組。