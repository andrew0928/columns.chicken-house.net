---
layout: synthesis
title: "WLW Plugins: Code Formatter"
synthesis_type: summary
source_post: /2008/03/08/wlw-plugins-code-formatter/
redirect_from:
  - /2008/03/08/wlw-plugins-code-formatter/summary/
---

# WLW Plugins: Code Formatter

## 摘要提示
- 開發動機: 因頻繁張貼含程式碼的文章而厭倦手動貼 HTML，決定自製 WLW 外掛自動格式化程式碼
- 核心技術: 以 c# code format 開源庫為基礎，封裝為 Windows Live Writer Plugins
- 效果展示: 透過編輯與預覽畫面示意，顯示語法上色與排版成品
- 寫作流程優化: 從貼上原始碼到按 OK 即完成，省去切換 HTML 視圖與手工調整
- 格式化優點: 產生乾淨 HTML、需搭配 CSS、支援 Unicode、不會有中文亂碼
- CSS 整合: 將官方 CSS 直接貼入部落格主題（Community Server）以維持清爽輸出
- 他法取捨: 放棄內嵌顏色碼的其他庫，避免產生冗長難讀的 HTML
- WinForms 插曲: ComboBox 無法用 Designer 輕鬆設定 Value/Display，只能以程式碼 KeyValuePair 方式初始化
- 範例程式: 提供 C# Console 範例與 ComboBox 初始化程式片段
- 下載與後續: 提供外掛下載連結，未來視時間與意願不定期更新

## 全文重點
作者因經常在部落格張貼含程式碼的文章，過去仰賴 c# code format 網站轉出語法高亮的 HTML，再回到 Windows Live Writer（WLW）切換原始碼模式貼入，流程雖可行但繁瑣。嘗試使用現成的 WLW Syntax Highlight 外掛時遇到中文亂碼問題，遂改用 c# code format 所釋出的原始碼，自行封裝成 WLW 外掛，以便在編輯器內直接完成程式碼格式化。外掛最終成品在編輯與預覽畫面皆能呈現良好的語法上色與排版，貼上原始碼後按下 OK 即完成，大幅簡化寫作流程。

作者選擇 c# code format 的理由包含：純 C# 開發、架構簡潔、輸出 HTML 乾淨、支援 Unicode、不會出現中文亂碼。此外，雖然需搭配外部 CSS，但相較於其他庫直接在 HTML 內硬塞色碼所導致的冗長輸出，這種做法更清爽且易於維護。作者將官方 CSS 直接貼入 Community Server 的自訂主題設定，無須動到檔案即可生效。

文中亦提到開發過程中遇到的 WinForms ComboBox 小插曲：希望以 Designer 直接設定每個選項的 Value 與 Display，但查遍文件與支援文章均無簡便解法，最終以程式碼設定 DisplayMember/ValueMember，並使用 KeyValuePair 新增項目解決。文末提供 C# 範例與 ComboBox 初始化片段，並附上外掛下載連結。作者表示未來將視時間與動力不定期更新，歡迎回饋建議。

## 段落重點
### 動機與背景：減少貼文時的手工負擔
作者常需在文章中嵌入程式碼，以往流程是到 c# code format 網站轉出 HTML，再回 WLW 用原始碼模式貼入，來回切換頗為繁瑣。既有的 WLW 語法高亮外掛在中文顯示上有問題，促使作者動念把 c# code format 的開源程式封裝成 WLW 外掛，讓貼文時能一鍵完成格式化。此舉主要為提升撰寫效率、避免手動處理 HTML 的重複性工作，並維持既有閱讀品質。

### 外掛功能與效果：從編輯到預覽的流暢體驗
外掛完成後，編輯畫面與預覽畫面均能正確呈現語法高亮與排版，作者以實際截圖與 C# Console 範例展示成品效果。使用步驟極簡：在 WLW 編輯器貼上原始碼、選擇語言格式、按下 OK 即完成嵌入，不再需要切換 HTML 視圖或手工清理標籤。此流程有效縮短貼文時間，並降低格式錯誤風險，兼顧可讀性與維護性。

### 採用 c# code format 的理由與整合方式
作者比較多種語法上色庫後，偏好 c# code format，理由包括：純 C# 開發、程式碼精煉、架構良好；輸出 HTML 乾淨不冗長；支援 Unicode，避免中文亂碼；且作者原本就熟悉其輸出風格。雖需搭配外部 CSS 才能完整呈現樣式，但比起把色碼硬寫進 HTML 的作法更清爽。實務上，作者將官方 CSS 貼入部落格（Community Server）的自訂主題設定，即可全站套用樣式而無需動檔案，使用過程順暢。

### WinForms ComboBox 的小插曲與程式碼解法
在外掛的格式選擇 UI 上，作者原想以 Designer 為 ComboBox 直接設定 Value 與 Display（例如 Value=HTML、Display=HTML / XML / ASP.NET），查遍 MSDN 與相關社群資源仍未找到不用寫程式即可完成的方式。最終改以程式主導：設定 DisplayMember 與 ValueMember，並用 KeyValuePair 加入選項，包含 HTML、C#、VB、PowerShell、T-SQL 等，預設選擇 C#。雖非零程式碼方案，但僅需數行即可達成需求，實作直覺且維護成本低。

### 下載、更新與回饋
作者提供外掛下載連結，方便有相同需求的使用者直接取用。未來更新將視時間與動機不定期釋出，歡迎讀者提出改進建議；但更新節奏將依作者的空檔與意願而定。整體而言，外掛有效解決了貼文流程中繁瑣的 HTML 處理，並在可讀性、穩定性（特別是中文支援）與維護性之間取得良好平衡。

## 資訊整理

### 知識架構圖
1. 前置知識：  
   - 基本 C#/.NET 與 WinForms 開發經驗  
   - Windows Live Writer（WLW）的使用與外掛概念  
   - HTML/CSS 基礎（特別是語法標示的呈現方式）  
   - 程式碼語法標示（Syntax Highlighting）的基本原理

2. 核心概念：  
   - WLW 外掛開發：以外部程式庫包裝為可在 WLW 內插入程式碼片段的外掛  
   - c# code format 程式庫：純 C# 開發、輸出乾淨 HTML、需搭配 CSS、支援 Unicode  
   - 表現層策略：使用外部 CSS 控制樣式，避免在 HTML 內內嵌大量 color style  
   - 多語系兼容：處理中文不亂碼（Unicode 可靠性）  
   - WinForms ComboBox 設計：以 KeyValuePair 搭配 DisplayMember/ValueMember 建立選單

3. 技術依賴：  
   - WLW 插件框架（WLW Add-ins API）  
   - .NET Framework（C#）  
   - c# code format 程式庫（Manoli’s C# Code Formatter）  
   - 外部 CSS（在部落格主題或佈景中加入樣式）  
   - 部落格平台（例如 Community Server）以便注入/管理 CSS

4. 應用場景：  
   - 在部落格張貼程式碼時快速進行語法上色  
   - 減少切換至 HTML 原始碼手動調整的時間成本  
   - 保持輸出 HTML 乾淨、可維護，並確保中文顯示正確  
   - 於企業或技術文件編寫時一致化程式碼樣式

### 學習路徑建議
1. 入門者路徑：  
   - 安裝與使用 WLW，了解如何編寫與發佈文章  
   - 安裝 Code Formatter 外掛，嘗試貼上 C#/HTML/SQL 等語言的程式碼  
   - 在部落格佈景或主題中加入對應的 CSS，驗證樣式是否正確套用  
   - 熟悉基本語法標示效果與常見問題（字形、字體大小、行號、中文顯示）

2. 進階者路徑：  
   - 研究 c# code format 程式庫的使用方式與可調校參數  
   - 自訂或優化 CSS（深色主題、對比度、等寬字型、行高）  
   - 擴充外掛的語言清單與對應的格式設定  
   - 在 WinForms UI 中以 DisplayMember/ValueMember 寫出可維護的語言選單

3. 實戰路徑：  
   - 從零包裝一個 WLW 插件：建立專案、引用 formatter 程式庫、實作插入點  
   - 設計插入對話框：以 ComboBox 維護語言清單（Value=語言代碼、Display=友善名稱）  
   - 規劃樣式部署：將 CSS 併入部落格平台的自訂主題或共用 CSS  
   - 驗證多語言內容（含中文）與各瀏覽器顯示，並撰寫部署文件

### 關鍵要點清單
- 外掛目標：將程式碼一鍵轉為帶語法上色的乾淨 HTML（優先級: 高）
- 選用程式庫：c# code format（純 C#、短小精悍、輸出乾淨、支援 Unicode）（優先級: 高）
- CSS 分離：以外部 CSS 控制樣式，避免在 HTML 內塞滿 style 屬性（優先級: 高）
- Unicode 支援：確保中文不亂碼，適用多語系內容（優先級: 高）
- WLW 整合：透過插件在編輯器中直接插入格式化程式碼，減少切換原始碼的手工（優先級: 高）
- 使用流程：貼入 -> 選語言 -> 確認 -> 完成（提升效率與一致性）（優先級: 中）
- WinForms ComboBox 綁定：使用 KeyValuePair + DisplayMember/ValueMember 管理選單（優先級: 中）
- 初始值設定：在 ComboBox.Items 中加入語言對應並設定 SelectedIndex（優先級: 中）
- 語言清單設計：Value 用語言代碼（如 HTML/CS/VB/MSH/SQL）、Display 用人類可讀名稱（優先級: 中）
- 佈景整合：在部落格平台（如 Community Server）將 CSS 放入自訂主題（優先級: 中）
- HTML 輸出品質：保持語意簡潔與結構清楚，方便維護與換皮（優先級: 中）
- 擴充性：未來可擴充語言清單、調整樣式、修正 UI 細節（優先級: 低）
- 相容性測試：在不同瀏覽器與平台驗證顯示一致性（優先級: 中）
- 發佈維護：提供下載連結與不定期更新，蒐集使用者回饋（優先級: 低）
- 效能與體驗：避免過多外掛互斥或卡頓，保持插入流程流暢（優先級: 低）