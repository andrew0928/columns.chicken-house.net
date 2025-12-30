---
layout: synthesis
title: "搭配 CodeFormatter，網站須要配合的設定"
synthesis_type: summary
source_post: /2008/04/04/configuring-website-settings-for-codeformatter-compatibility/
redirect_from:
  - /2008/04/04/configuring-website-settings-for-codeformatter-compatibility/summary/
---

# 搭配 CodeFormatter，網站須要配合的設定

## 摘要提示
- 外掛更新與下載: 作者釋出小改版的 Live Writer 外掛並提供下載連結，功能告一段落以後續修 bug 為主。
- 伺服器需配合: 部分功能需部落格伺服器端設定配合，否則無法完整運作。
- CSS 樣式整合: CodeFormatter 產生乾淨 HTML，樣式抽離至 CSS，需將官方提供的 CSS 佈署到站台。
- Community Server 設定: 可在 Dashboard 的 Custom Styles (Advanced) 貼上 CSS 以套用程式碼樣式。
- C# 語法標色: CSS 定義關鍵字、字串、註解、運算子等類別，實現語法醒目顯示。
- COPY CODE 功能: 透過 JavaScript 複製程式碼至剪貼簿，解決使用者複製後格式干擾的問題。
- SCRIPT 封鎖繞道: 因 CS 會擋 <script>，改用 IE 專屬 HTC 技術在 CSS 中掛載行為實作複製功能。
- HTC 佈署重點: 在 CSS 加上 behavior 指向 /themes/code.htc，並確保檔案放在指定路徑。
- 預覽以 HTA 呈現: 預覽改用 HTA 以避免 IE 直接開 HTML 的安全警告，並致謝原作者與自站。
- 授權與散佈: 歡迎下載使用並請註明出處，未來以修正問題為主。

## 全文重點
作者釋出一版小改良的 Windows Live Writer 外掛，支援與 CodeFormatter 的整合，提供下載並宣告此階段功能告一段落。由於外掛部分功能必須仰賴網站端設定，文中統一說明伺服器需要配合的調整，主要分為兩大區塊：CSS 樣式配置與「Copy Code」複製功能實作。

首先談 CSS。作者喜歡 CodeFormatter 的原因在於輸出的 HTML 結構精簡，將格式控制交由外部 CSS 管理，因此使用者必須把官方提供的 CSS 佈署到自己的部落格平台。以 Community Server 為例，可在後台 Dashboard 的版面設定中找到 Custom Styles (Advanced) 頁面，直接貼上 CSS 即可生效。附帶的 CSS 定義了 csharpcode 容器與各種語法標色類別（如註解、關鍵字、字串、運算子、前置處理器、HTML 屬性等），搭配等寬字型呈現，使 C# 程式碼片段以高可讀性方式展示。作者提醒若想啟用下一個「Copy Code」功能，CSS 還需再加上一段設定。

接著是「Copy Code」。此功能本質上是利用 JavaScript 將程式碼文字寫入剪貼簿；但在 Community Server 預設會封鎖 <script> 標籤，因此無法直接在文章 HTML 內嵌腳本。為解此限制，作者採用 IE 專屬的 HTC（HTML Component）技術，讓行為像 CSS 一樣集中管理：透過在 CSS 中對 .copycode 類別設定 behavior:url('/themes/code.htc')，由瀏覽器載入外部 HTC 來綁定事件與操作剪貼簿，如此便不用在內容中出現 <script>。此作法相較以 jQuery 實作雖然概念類似，但仍需插入腳本，對 CS 而言同樣會被擋，因此 HTC 更合適。讀者只要將這段 CSS 加入，並把 code.htc 放到 /themes/code.htc 指定路徑，伺服器端就算設定完成。

完成上述設定後，使用外掛插入程式碼時勾選「包含原始碼」的選項，生成的 HTML 會在區塊標題右側出現「copy code」連結。點擊後可將範例程式碼（例如文中顯示的 MSDN C# 範例）乾淨複製到剪貼簿，不會夾帶格式，能直接貼到開發環境使用。需要注意的是，預覽畫面不會加上此功能。為提升預覽體驗並避免 IE 直接開啟本機 HTML 所引發的安全警告，作者改以 HTA（HTML Application）方式呈現預覽，同時在畫面裡致謝 CodeFormatter 原作者並加入自己網站連結。

最後，作者表示此階段開發暫告一段落，後續以修 bug 為主，歡迎有需要的使用者下載，也請在散佈時註明出處。

## 段落重點
### 前言與下載資訊
作者宣布為 Live Writer 外掛進行小幅更新，並提供最新壓縮檔下載連結。此外掛的目標是讓撰寫技術文章（特別是含程式碼）的流程更順暢，並與 CodeFormatter 協同工作，輸出既乾淨又可讀性高的程式碼區塊。作者強調，由於部分功能需要網站端環境配合，因此特別整理伺服器端須要的設定。一言以蔽之：用戶端外掛負責產生結構化內容與選項，伺服器端則需提供正確的 CSS 與客製化行為支援，兩者相輔相成方能達到最佳效果。文章後續分兩大點逐一說明：先處理樣式（CSS），再處理複製功能（Copy Code）。同時也預告預覽機制採用 HTA 以改善安全警告問題，並在預覽中加入對原作者的致敬與自家網站資訊。整體來看，此版本功能已趨穩定，未來以修正問題為主，並邀請讀者自由下載使用、轉載時請註明來源。

### 1. CSS 設定與樣式匯入
CodeFormatter 的輸出策略是盡量讓 HTML 保持輕量，將視覺樣式全部外移到 CSS，因此站台端必須先妥善匯入官方提供的 CSS 才能正確呈現語法標色與排版。作者提供了一份 C# 專用樣式，包含 csharpcode 容器、pre 標籤間距、與 rem（註解）、kwrd（關鍵字）、str（字串）、op（運算子）、preproc（前置處理器）、html、attr（屬性）、lnum（行號）等類別的色彩指定，並套用適合閱讀程式碼的等寬字型。以 Community Server 為例，只需到 Dashboard 的版面設定頁，找到「Custom Styles (Advanced)」將整段 CSS 貼上，即可全站套用。作者提醒若接下來要啟用「Copy Code」按鈕，先別急著只貼這段，因為還需要加上一小段額外 CSS 來掛載 HTC 行為。這個階段的重點是：沒有這份 CSS，程式碼區塊會失去標色和排版一致性，整體閱讀體驗會大打折扣；而有了它，就能得到整潔的 HTML 結構與清晰的語法高亮，為後續的互動功能鋪路。

### 2. COPY CODE：以 HTC 實作剪貼簿複製
複製程式碼到剪貼簿的核心其實只是簡單的 JavaScript，但在 Community Server 這類平台，直接在文章內容插入 <script> 會被預設策略封鎖；若硬改平台設定（如調整 communityserver.config）又過於侵入且不易維護。作者因此採用 IE 獨有的 HTC（HTML Component）方案，讓行為像 CSS 一樣集中管理：在 CSS 中為 .copycode 類別加入 behavior:url('/themes/code.htc')，並設定 cursor、顏色與 display；同時把 code.htc 檔案放到 /themes/code.htc 的實體路徑。如此一來，頁面載入時 IE 會自動將該元素綁定 HTC 內定義的事件與邏輯（例如點擊後把指定程式碼文字寫入剪貼簿），而不需要在文章 HTML 內嵌任何 <script>。完成伺服器端佈署後，作者的外掛在插入程式碼時只要勾選「包含原始程式碼」選項，就會輸出帶有 [copy code] 的標題列。使用者點擊後能取得無格式汙染的純淨程式碼，可直接貼到 IDE 使用，避免手動清理格式的麻煩。作者也提到雖然 jQuery 也能達成類似行為，但在 CS 的腳本封鎖情境下仍須面對同樣的注入問題，因此 HTC 更合適。

### 預覽機制與結語
為避免以 IE 直接開啟本機 HTML 預覽時常見的安全性警告，作者改以 HTA（HTML Application）實作預覽視窗，帶來更流暢的測試體驗。預覽畫面也特別加入對 CodeFormatter 原作者的致敬連結與自家網站資訊。需要留意的是，預覽模式並不會啟用「Copy Code」功能，該功能需在實際佈署於站台、且 HTC 與 CSS 正確配置時才會生效。全文總結：此外掛與網站端配置到此已算告一段落，關鍵在於兩步驟——先貼入 CodeFormatter 的 CSS，再為「Copy Code」加入 HTC 行為與檔案。落實後，最終呈現的程式碼區塊可同時具備高可讀性與可用性，一鍵複製免去格式干擾。作者最後歡迎讀者下載使用並協助散佈，但請註明出處；後續將以修正問題為主，持續維護品質。下載連結也一併附上，方便讀者立即試用整合成效。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 基本 HTML/CSS 與 JavaScript 觀念
   - 部落格平台（如 Community Server）後台操作與版面/樣式自訂
   - 站台檔案部署與路徑管理（能上傳 CSS、HTC 等靜態檔）
   - 瀏覽器相容性概念（特別是 IE 專屬的 HTC/behavior）
2. 核心概念：
   - CodeFormatter 外掛：將程式碼轉為乾淨 HTML，樣式交由 CSS 控制
   - 語法高亮 CSS：以類別選擇器（.kwrd, .str, .rem 等）實現主題風格
   - Copy Code 功能：以 JavaScript 寫入剪貼簿；在限制環境下用 IE 的 HTC 行為注入
   - 平台限制繞道：因部落格會封鎖 <script>，改以 CSS behavior 指向 HTC 來掛事件
   - 檔案與路徑部署：CSS 置入自訂樣式區、HTC 置於指定目錄（如 /themes/code.htc）
3. 技術依賴：
   - CodeFormatter 生成的 HTML -> 需對應的 CSS 規則才能顯示正確高亮
   - Copy Code -> 依賴 CSS behavior:url(...) 指向 HTC（IE 專屬）來處理剪貼簿
   - 平台（Community Server）-> 需允許自訂 CSS；若封鎖 <script> 則改用 HTC 達成
   - 預覽（HTA）-> 用 HTA 取代直接開 HTML 以避免安全警告
4. 應用場景：
   - 技術部落格張貼多語言程式碼片段並需語法高亮
   - 需要一鍵複製程式碼且不希望附帶多餘格式
   - 受 CMS/Blog 平台防護政策限制（阻擋內嵌 <script>）的發文環境
   - 以 Community Server 為主的站台客製化

### 學習路徑建議
1. 入門者路徑：
   - 安裝並啟用 CodeFormatter 外掛
   - 將提供的語法高亮 CSS 貼入部落格的 Custom Styles（例如 Community Server 的 Dashboard > Custom Styles）
   - 新增 HTC 支援的 CSS 規則（.copycode { behavior:url('/themes/code.htc') }）
   - 將 code.htc 上傳至對應路徑（如 /themes/code.htc），於撰文時勾選「輸出含原始碼」與「copy code」選項
   - 發佈一篇含程式碼的文章驗證呈現與複製功能
2. 進階者路徑：
   - 調整 CSS 主題（字型、配色、行號、交錯底色 .alt 等）以符合站台風格
   - 規劃資源路徑與快取（CDN 或版本化）避免快取汙染
   - 研究平台安全政策與白名單機制，理解為何 <script> 受限與替代方案
   - 增加降級策略：偵測非 IE 瀏覽器時的 UI 處理（隱藏或改為提示）
3. 實戰路徑：
   - 在測試站部署：套上語法高亮 CSS、上傳 HTC、調整路徑，發文測試多段程式碼
   - 針對多瀏覽器驗證：IE 看到 copy code；非 IE 檢查顯示/隱藏策略是否合理
   - 調整預覽流程：使用 HTA 預覽避免安全警告，並加入版權/來源資訊
   - 文件化安裝步驟與維運手冊（含檔案清單、路徑、平台設定、常見錯誤）

### 關鍵要點清單
- 語法高亮 CSS 對應類別：CodeFormatter 產生的 .kwrd/.str/.rem 等必須有對應樣式，否則效果失真 (優先級: 高)
- 乾淨 HTML 設計：將視覺樣式從 HTML 分離到 CSS，提升可維護性與一致性 (優先級: 中)
- Community Server 自訂樣式：於 Dashboard 的 Custom Styles 貼入提供的 CSS 即可生效 (優先級: 高)
- <script> 受限問題：平台會封鎖內嵌腳本，需以替代技術（HTC）注入行為 (優先級: 高)
- HTC 行為注入：以 CSS 的 behavior:url('/themes/code.htc') 對 .copycode 元素掛載事件 (優先級: 高)
- 路徑與部署：確保 code.htc 放在與 CSS 指定一致的路徑（如 /themes/code.htc） (優先級: 高)
- Copy Code 觸發元素：.copycode 類別結合 HTC 使「[copy code]」能複製純程式碼至剪貼簿 (優先級: 高)
- IE 相容性限制：HTC 為 IE 專屬，非 IE 瀏覽器需接受功能降級或另行實作 (優先級: 中)
- 預覽使用 HTA：以 HTA 取代直接開 HTML，避免安全警告干擾預覽體驗 (優先級: 中)
- 行號與交錯底色：.lnum 與 .alt 提升可讀性，可依主題調整顏色與背景 (優先級: 低)
- 字型選擇：等寬字型（Consolas/Courier New）確保對齊與可讀性 (優先級: 中)
- 內容安全與權限：遵守平台安全策略，不隨意開放 script 白名單，以降低風險 (優先級: 高)
- 發文流程勾選：插入程式碼時勾選輸出含原始碼與 copy code，確保最終 HTML 包含必要標記 (優先級: 中)
- 測試與驗證：在測試環境檢查多段程式碼、不同語言與瀏覽器的行為 (優先級: 中)
- 來源與授權：散佈外掛與範例時標注來源與作者網站，維持版權與社群禮節 (優先級: 低)