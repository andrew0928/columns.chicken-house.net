---
layout: synthesis
title: "搭配 CodeFormatter，網站須要配合的設定"
synthesis_type: faq
source_post: /2008/04/04/configuring-website-settings-for-codeformatter-compatibility/
redirect_from:
  - /2008/04/04/configuring-website-settings-for-codeformatter-compatibility/faq/
---

# 搭配 CodeFormatter，網站須要配合的設定

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 CodeFormatter？
- A簡: CodeFormatter 是產生語法高亮 HTML 的函式庫，強調乾淨標記，樣式外掛於 CSS。
- A詳: CodeFormatter 是一套將原始程式碼轉為語法上色 HTML 的函式庫（本文以 C# 為例）。其核心理念是「標記乾淨」，也就是將語法顏色、字型等全部交由外部 CSS 控制，而非在 HTML 內寫入繁雜的 style 屬性。如此可讓文章 HTML 結構精簡、易於維護，且外觀風格可透過更新單一 CSS 統一調整。要正確呈現高亮效果，網站端必須提供對應的 CSS，並於貼文頁面成功載入。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, B-Q1

A-Q2: 為什麼要為 CodeFormatter 配置網站端 CSS？
- A簡: 因其輸出不含內嵌樣式，需載入對應 CSS 才能呈現正確語法高亮。
- A詳: CodeFormatter 的 HTML 僅提供語意與結構，不含色彩與字型資訊；顏色、字型、行號、關鍵字等顯示完全依賴外部 CSS 類別（如 .csharpcode、.kwrd、.str 等）。若網站未配置或未正確載入該套 CSS，頁面將只顯示未上色的預設文字，無法達到閱讀友善與辨識度高的效果。因此，第一步必須在部落格或 CMS 的佈景設定中新增對應 CSS，確保每篇含程式碼的文章頁面都能正確引用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, B-Q2, C-Q1

A-Q3: CodeFormatter 產生的 HTML 有何特點？
- A簡: 標記精簡、語意清楚、以類別標註語法元素，外觀交由 CSS 控制。
- A詳: 產出 HTML 通常以容器附上語言類別（如 .csharpcode），內部以 <pre> 包裹，並以語法元素類別標示，如 .kwrd（關鍵字）、.str（字串）、.rem（註解）、.preproc（前置處理）、.attr（屬性）與 .lnum（行號）。這種做法使結構與視覺解耦：HTML 結構單純描述「是什麼」，而「如何顯示」交由 CSS 決定。優點是樣式統一、易調整與可重用，且減少頁面大小與重複樣式。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q2

A-Q4: C# Code Formatter 的 CSS 主要包含哪些類別？
- A簡: 包含 .csharpcode 容器、.kwrd、.str、.rem、.preproc、.attr、.lnum、.alt 等樣式。
- A詳: 官方提供之 CSS 以 .csharpcode 作為主要容器與字型設定（如 Consolas、Courier New）；.kwrd 控制關鍵字顏色、.str 控制字串、.rem 註解、.preproc 前置處理、.attr 屬性、.op 運算子、.html HTML 文本；.lnum 用於行號顏色，而 .alt 常作為交錯背景行的輔助類別。這些類別對應到 CodeFormatter 輸出的標記，可細緻控制語法高亮的各種語意元素顯示。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, C-Q1

A-Q5: 為什麼建議將樣式抽離到 CSS？
- A簡: 降低 HTML 冗長、集中管理風格、提升快取效率與維護性。
- A詳: 抽離樣式能讓 HTML 專注於內容語意，減少重複 style 造成的傳輸負擔；樣式集中於 CSS 檔，便於跨站或跨文章統一調整，替換主題時只需更新樣式檔。瀏覽器會快取 CSS，減少後續頁面載入成本。此外，分離可降低誤植風險，提高可讀性與協作效率。對語法高亮這類大量色彩與字型控制的需求而言，這種解耦益處尤為明顯。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, B-Q1

A-Q6: 什麼是「copy code」功能？
- A簡: 一鍵將顯示區塊中的原始程式碼複製到剪貼簿，避免格式干擾。
- A詳: 「copy code」是在程式碼標題旁提供的操作連結。使用者點擊後，頁面會把該段程式碼以「乾淨純文字」的形式複製到剪貼簿，避免因語法高亮或 HTML 標記而影響貼上結果。本文方案利用 HTC 與 CSS 行為將事件綁定至頁面元素，以便在不插入 <script> 的前提下實現複製功能，特別適合預設會過濾腳本的部落格平台（如 Community Server）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, C-Q3

A-Q7: 為什麼需要「copy code」功能？
- A簡: 提升複製體驗，避免帶入行號、顏色或多餘空白，確保可直接編譯。
- A詳: 直接在網頁上反白複製常會把語法高亮的 HTML、行號或不可見字元一併帶走，貼入 IDE 後需手動清理，易出錯且耗時。「copy code」提供乾淨的程式碼字串，省去整理步驟，提升學習與開發效率。對於教學文章、範例分享與團隊知識庫，此功能可顯著降低讀者摩擦，落實「貼上即用」的可用性目標。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q3

A-Q8: 什麼是 HTC（HTML Component）？
- A簡: IE 特有的元件技術，可藉 CSS behavior 統一套用事件與行為。
- A詳: HTC 是 Internet Explorer 支援的 HTML Components 機制，允許以外部檔（.htc）封裝 DHTML 行為，並透過 CSS 的 behavior:url(...) 將該行為套用到符合選擇器的元素。它可把 onclick、onload 等事件處理集中管理，達到類似「用 CSS 管理行為」的效果。由於某些平台（如 Community Server）會移除 <script>，HTC 成為在不改平台設定情況下，為頁面元素增加互動功能的可行方案。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q5, C-Q2

A-Q9: HTC 與 jQuery 的差異是什麼？
- A簡: jQuery 跨瀏覽器但需腳本載入；HTC 為 IE 專屬，透過 CSS behavior 注入行為。
- A詳: jQuery 提供強大的 DOM 操作與事件綁定，跨瀏覽器相容性佳，通常以 <script> 引入。若平台會過濾腳本，需額外白名單或設定。HTC 則不需在文章中寫 <script>，透過 CSS behavior 即可注入行為，但僅 IE 支援。本文情境下，因 Community Server 預設封鎖 <script>，以 HTC 實作「copy code」較便捷；若可安全載入腳本，jQuery 亦能達成同目標，且對非 IE 的支援更好。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q6, D-Q7

A-Q10: 什麼是 HTA（HTML Application）？
- A簡: 以 IE 引擎執行的桌面應用封裝，降低本機 HTML 安全警示。
- A詳: HTA 是用 mshta.exe 執行的 HTML Application，使用 IE 的排版與腳本引擎，但具有較寬鬆的本機許可，適合做工具或預覽。本文為避免直接用 IE 開本機 HTML 時反覆跳出安全警告，改以 HTA 實作預覽介面，並在預覽中加入原始庫作者與站點資訊。HTA 適用於 Windows/IE 環境，能提供更順暢的預覽體驗。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q7, C-Q5

A-Q11: 什麼是 Community Server（CS）？
- A簡: 一套部落格/社群平台，提供佈景自訂與安全機制，預設過濾 <script>。
- A詳: Community Server 是早期常見的社群與部落格平台，提供 DashBoard 後台、佈景調整與「Custom Styles (Advanced)」頁面，可直接加入自訂 CSS。基於安全考量，CS 預設會封鎖 <script> 標籤以降低 XSS 風險。本文的設定即以 CS 為例，將 CodeFormatter 的 CSS 貼入自訂樣式，並用 HTC 取代內嵌腳本來實作「copy code」。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, C-Q1, C-Q2

A-Q12: 為何 Community Server 會封鎖 <script>？
- A簡: 出於安全（防 XSS/惡意注入），預設過濾貼文中的可執行腳本。
- A詳: 多數部落格/社群平台會移除或過濾貼文中的 <script>，以避免讀者載入惡意腳本導致竊資、跳轉或會話劫持。CS 即採此預設。雖然可修改 communityserver.config 放寬限制，但需權限與風險評估。本文選擇以 HTC 注入行為，避免改動平台設定，達到功能與安全的折衷。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, B-Q6, D-Q6

A-Q13: 什麼是 CSS behavior 屬性？
- A簡: IE 專屬屬性，讓元素載入外部 HTC 檔以新增行為。
- A詳: behavior 是 IE 支援的 CSS 擴充屬性，可將外部 .htc 指定為元素的行為提供者。當頁面解析該元素並載入 HTC 後，行為檔可監聽事件、操作 DOM、改變顯示等。本文在 .copycode 類別中指定 behavior:url('/themes/code.htc')，讓被套用的元素具備一鍵複製的互動能力，同時避開直接在貼文中加入 <script> 的限制。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q5, C-Q2

A-Q14: .copycode 這段 CSS 的作用是什麼？
- A簡: 設定指標樣式、顏色、預設隱藏，並透過 behavior 掛載 HTC 行為。
- A詳: .copycode {cursor:hand; color:#c0c0ff; display:none; behavior:url('/themes/code.htc');} 此規則讓「copy code」連結呈現可點擊指標、淡藍字色；一開始 display:none 可能配合 HTC 在載入後決定顯示時機，並負責綁定 onclick 複製動作。behavior 指向 code.htc，將複製邏輯外包給行為檔，達到樣式與行為集中管理、貼文零腳本的目的。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, C-Q2

A-Q15: 為什麼 HTC 檔案要放在 /themes/code.htc？
- A簡: 因 CSS 行為使用絕對路徑指向 /themes/code.htc，需對應實體檔。
- A詳: 在 .copycode 的 CSS 中，behavior:url('/themes/code.htc') 使用了網站根目錄下 /themes 路徑。為使瀏覽器能載入 HTC，伺服器必須提供該 URL 並正確回應檔案內容。若調整放置路徑，需同步修改 CSS 的 URL。不同平台對大小寫與檔案路徑敏感度不同，建議維持一致命名，並確認能以 HTTP 正確取用。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q2, D-Q2

A-Q16: 勾選「產生出來的HTML會包含原始程式碼」有何用？
- A簡: 讓輸出 HTML 內同時保留純文字程式碼，供「copy code」讀取複製。
- A詳: 插入程式碼時勾選該選項，產出的 HTML 會包含可辨識的原始程式碼內容（不被語法高亮標記破壞），以便「copy code」功能直接讀取乾淨字串。若未勾選，複製可能連同標記、行號、縮排等雜訊，降低貼上品質。此步驟確保功能一致性與跨環境可用性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q4, D-Q10

A-Q17: 為什麼預覽不直接用 IE 開 HTML，而改用 HTA？
- A簡: 避免本機安全警示與權限限制，HTA 提供更順暢的預覽體驗。
- A詳: 直接以 IE 開啟本機 HTML 常觸發安全提示（腳本、剪貼簿等），影響預覽效率。改用 HTA 後，由 mshta 以桌面應用模式執行，獲得較寬鬆的權限，減少安全對話框干擾。作者也在預覽頁加入原庫作者與站點資訊，整體更符合教學展示需求。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q10, B-Q7

A-Q18: 本方案的瀏覽器相容性如何？
- A簡: 語法高亮的 CSS 跨瀏覽器；HTC 與 behavior 僅 IE 支援。
- A詳: 以 CSS 呈現語法高亮在現代瀏覽器皆可運作；但「copy code」依賴 IE 的 HTC 與 behavior 屬性，非 IE 環境無法執行該行為。若需跨瀏覽器的一鍵複製，則須引入腳本方案（如 Clipboard API 或第三方庫），但這和文中避免 <script> 的限制相衝。本文方案在 IE 下具最佳體驗，在其他瀏覽器則提供可閱讀的高亮顯示。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, A-Q9, D-Q7

A-Q19: 什麼是 CS 的「Custom Styles (Advanced)」？
- A簡: 後台提供的自訂樣式頁，可直接貼入全站生效的 CSS。
- A詳: 在 Community Server 後台（DashBoard）中，「Custom Styles (Advanced)」允許管理者將自訂 CSS 注入佈景，無需修改實體檔案。將 CodeFormatter 與 .copycode 的 CSS 貼入此處，即可讓所有貼文頁讀取樣式，快速啟用語法高亮與「copy code」外觀。此方式不影響平台安全策略，也便於回滾與維護。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, C-Q2

A-Q20: CodeFormatter 與其他語法高亮工具有何特色差異？
- A簡: 著重 HTML/樣式分離與乾淨標記，便於平台整合與維護。
- A詳: 許多高亮工具會輸出大量 inline style 或依賴腳本執行。CodeFormatter 的特色是將視覺層徹底交由 CSS，讓 HTML 輕量清晰，便於貼入各平台。配合 HTC 可在禁止 <script> 的環境下提供基本互動（如「copy code」），形成「安全友善」的整合路徑。若平台允許腳本，亦可採其他工具取得更廣泛的瀏覽器支援。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q2, A-Q9, B-Q6

### Q&A 類別 B: 技術原理類

B-Q1: 語法高亮的 CSS 原理如何運作？
- A簡: 以語法類別標記元素，CSS 對應上色與字型，達成視覺呈現。
- A詳: CodeFormatter 先將程式碼解析成語法單元，輸出帶有語意類別的 HTML 標記（如 .kwrd、.str）。瀏覽器載入對應 CSS 後，依選擇器設定顏色、字型、背景與行距等，產生高亮效果。容器類別（.csharpcode）統一控制區塊字型與底色；子類別各自處理關鍵字、字串、註解與行號顯示。此模式讓「樣式=CSS」、「內容=HTML」，避免程式碼展示與外觀耦合。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q1, A-Q4

B-Q2: CodeFormatter 產生的 HTML 結構為何？
- A簡: 以 .csharpcode 容器搭配 <pre>，內含依語法分段的 span/class。
- A詳: 常見結構為 <div class="csharpcode"><pre>...</pre></div>，或 <pre class="csharpcode">...。內部語法元素通常以 <span class="kwrd">、<span class="str"> 等包裹，並可能包含行號標記（.lnum）或交錯行背景（.alt）。如此一來，CSS 可準確鎖定各類元素調整樣式；而工具或行為（如 HTC）也可藉由容器查找需要操作的純文字來源。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q3, C-Q5

B-Q3: 「copy code」複製到剪貼簿的機制是什麼？
- A簡: 點擊事件觸發 HTC 行為，讀取原始字串並呼叫剪貼簿 API 複製。
- A詳: 以 HTC 綁在 .copycode 元素上，當使用者點擊「[copy code]」時，行為檔會找到對應的原始程式碼（由勾選選項輸出），將其整理為純文字，並透過 IE 支援的剪貼簿存取方式進行複製。過程避免 HTML 標記干擾，確保結果可直接貼入 IDE。若瀏覽器或設定限制剪貼簿操作，複製可能失敗，需相容性與權限評估。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, A-Q16, D-Q3

B-Q4: HTC 如何統一管理 DHTML 事件？
- A簡: 將事件處理封裝於 .htc，透過 behavior 對應元素自動掛載。
- A詳: HTC 檔內可撰寫 script 與事件處理，當某元素 CSS 指定 behavior:url(...) 並載入完成後，該元素便具備 HTC 定義的行為與事件綁定。這使得 onclick、onmouseover 等邏輯可集中在單一檔案維護，像 CSS 統一定義樣式般統一定義行為，避免每篇文章內嵌 script。此能力為 IE 專屬。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, A-Q13

B-Q5: CSS behavior:url(...) 的運作流程為何？
- A簡: 解析到元素後，IE 下載並執行指定 HTC，將行為附加到元素。
- A詳: 當 CSS 解析到包含 behavior:url('/themes/code.htc') 的規則，且符合選擇器的元素出現時，IE 會請求該路徑的 HTC 檔，載入後執行其初始化邏輯，並將事件處理器綁定到元素生命週期。此過程依賴正確的 URL 與 MIME 回應；若路徑錯誤或無法下載，行為無法啟用，「copy code」將不顯示或無作用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, D-Q2

B-Q6: 在 CS 被動過濾 <script> 的情況如何繞過需求？
- A簡: 改用 HTC 搭配 CSS 行為注入互動，避免直接嵌入腳本。
- A詳: CS 出於安全預設會移除 <script>。若需互動功能（如複製），可將相關邏輯封裝到 HTC，然後用 CSS behavior 引入。如此不需修改 communityserver.config 即可啟用功能，兼顧部署簡易與安全邊界。若管理者允許白名單腳本，也可改用 jQuery/Clipboard API，但需評估影響範圍。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, A-Q9, D-Q6

B-Q7: HTA 為何能降低本機 HTML 的安全提示？
- A簡: HTA 以應用程式模式執行，具較寬鬆權限，減少警示干擾。
- A詳: 直接用 IE 開本機 HTML，許多動作（如存取剪貼簿、ActiveX）會觸發安全對話框。HTA 由 mshta 啟動，採應用程式信任模型，允許更寬鬆的本機操作，因而改善預覽體驗。本文用 HTA 作為預覽容器，避免安全提示干擾，同時可嵌入外部連結展示資訊。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q10, A-Q17

B-Q8: 預覽機制的設計概念是什麼？
- A簡: 以 HTA 承載預覽頁，載入樣式、樣本與資訊連結，模擬最終呈現。
- A詳: 作者未直接開本機 HTML，而是建立 HTA 來載入示例頁面，注入 CodeFormatter CSS 與「copy code」相關元素，並加入原庫作者首頁與站點資訊，兼具致敬與導流。此設計確保預覽更接近發佈後的使用體驗，且避免安全提示。
- 難度: 初級
- 學習階段: 進階
- 關聯概念: B-Q7, C-Q5

B-Q9: 「copy code」連結如何顯示與觸發？
- A簡: 標籤加上 .copycode 類別；HTC 載入後控制顯示並綁定點擊。
- A詳: CSS 將 .copycode 預設 display:none；當 HTC 成功載入並判定環境可支援複製時，會將其顯示出來（或以程式動態控制），並把 onclick 綁定到複製流程。若 HTC 未載入或瀏覽器不支援，連結可能保持隱藏，避免給出無效操作。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, D-Q1

B-Q10: 如何確保複製的是「乾淨純文字」而非帶格式內容？
- A簡: 以原始碼節點作來源，過濾標記與行號，輸出純文字再複製。
- A詳: 行為檔在觸發時，應找到未包裹 HTML 標記的原始碼來源（靠插入時的選項產生），或先將展示區塊中的標記剝離，排除 .lnum 等行號與多餘空白，再輸出純文字。如此貼到 IDE 即可編譯。若來源僅有帶標記的展示區，需額外清理步驟。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, D-Q10

B-Q11: 字型與配色策略有何考量？
- A簡: 等寬字型提升對齊與可讀性，色彩需兼具清晰與對比。
- A詳: CSS 使用 Consolas、「Courier New」、Courier、Monospace 等等寬字型，使縮排與對齊穩定；顏色如 .kwrd 藍、.str 青、.rem 綠，對比明顯便於辨識。背景色與交錯行（.alt）可減少閱讀疲勞，行號（.lnum）低對比不搶版面。這些設定可依站點主題微調。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, C-Q9

B-Q12: 交錯行背景（.alt）與行號（.lnum）如何協作？
- A簡: .alt 提升行間辨識，.lnum 標示行序，不干擾內容對比。
- A詳: .alt 常用於偶數行賦予淡背景，提高長段程式碼的掃讀效率；.lnum 給予行序參考，利於溝通與除錯。兩者應保持低干擾設計，避免掩蓋語法色彩。當「copy code」複製時，需排除這些視覺元素。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q10, D-Q10

B-Q13: 路徑與大小寫對 HTC 載入的影響？
- A簡: 行為 URL 須與實體檔一致；區分大小寫的環境需精確匹配。
- A詳: behavior:url('/themes/code.htc') 使用絕對路徑。若部署在區分大小寫的伺服器（如部分 Linux/Nginx），/themes/code.htc 與 /Themes/Code.HTC 視為不同路徑，將導致載入失敗。建議檢查實體路徑、大小寫與 MIME 設定，並以瀏覽器直接請求該 URL 驗證。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q15, D-Q2

B-Q14: 在無法用 HTC 的環境如何設計降級？
- A簡: 保持高亮 CSS；隱藏或禁用複製按鈕，避免無效操作。
- A詳: 非 IE 環境可照常顯示語法高亮，並透過 CSS/偵測判斷不顯示「copy code」，或提示使用者自行選取複製。若平台允許腳本，可另行以 Clipboard API 實作跨瀏覽器複製；否則就採讀者手動複製的方式，確保體驗一致與清楚預期。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q18, D-Q7

B-Q15: 為何不直接修改 communityserver.config 啟用 <script>？
- A簡: 涉及平台安全與維護風險；HTC 提供低侵入替代。
- A詳: 放寬腳本限制雖可用現代方案，但需管理者權限、審查與長期維護，且可能影響整站安全邊界。本文以 HTC 達成必要互動，避免修改平台配置，是對現有架構友善的做法。若確定需求長期存在且可控，再規劃更廣泛的腳本方案。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q6

B-Q16: 安全層面應注意什麼？
- A簡: 控制來源檔路徑、最小權限、避免不受信任腳本與行為檔。
- A詳: HTC/HTA 具執行能力，檔案來源須可信；限制可寫目錄、正確 MIME、HTTPS 傳輸；避免讓匿名上傳能覆蓋 /themes/code.htc。若採用腳本替代方案，也需 Content Security Policy 與輸入過濾，確保站內安全。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q7, D-Q6

B-Q17: 為什麼 .copycode 預設 display:none？
- A簡: 由 HTC 評估環境與時機後再顯示，避免無用或錯誤操作。
- A詳: 預設隱藏可避免在不支援或尚未載入行為時，使用者看到但無法使用的按鈕。HTC 載入並完成初始化後再顯示，或根據瀏覽器與權限判斷是否啟用，提升體驗一致性。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q9, D-Q1

B-Q18: 文章中的示例程式碼如何與按鈕關聯？
- A簡: 按鈕元素鄰近或關聯容器，行為檔藉 DOM 關聯找到對應區塊。
- A詳: 一般做法是「copy code」按鈕放在程式碼標題附近；HTC 透過 DOM 遍歷尋找相鄰的 .csharpcode/<pre> 容器，或以自訂屬性關聯。建立可靠的關聯方式，能確保複製的是正確區塊。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q5, D-Q10

B-Q19: 頁面快取與載入順序對樣式/行為影響？
- A簡: CSS 需先載入；HTC 載入成功後才顯示按鈕與綁定事件。
- A詳: 建議在頁面 <head> 中載入 CodeFormatter CSS，確保首屏正確渲染。HTC 依附於匹配元素，當元素出現在 DOM 中且規則命中時才載入行為；因此來源路徑與載入時機需驗證。若使用延遲載入或動態內容，需確保行為能觸達新元素。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q1, D-Q1

B-Q20: 此方案的擴充與替代方向？
- A簡: 可維持 CSS 高亮，視平台安全改以腳本提供跨瀏覽器複製。
- A詳: 若未來平台允許安全載入腳本，可以 Clipboard API 或第三方庫（如 clipboard.js）實作跨瀏覽器複製，同時保留現有 CSS 高亮。也可加入語言標籤偵測、多主題支援、深色模式等，皆不影響 HTML 結構。HTC 可作為舊 IE 相容保留，逐步過渡。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q18, B-Q14

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何在 Community Server 加入 CodeFormatter 的 CSS？
- A簡: 進入 DashBoard 的「Custom Styles (Advanced)」，貼入官方 CSS。
- A詳: 步驟：1) 以管理者登入 CS 後台；2) 開啟「Custom Styles (Advanced)」；3) 貼入下列 CSS 並儲存；4) 發佈含程式碼的文章測試。關鍵程式碼：
  .csharpcode, .csharpcode pre { font-size: small; color: black; font-family: Consolas,"Courier New",Courier,Monospace; background-color:#fff; } 
  .csharpcode pre { margin:0; } .csharpcode .rem{color:#080;} .kwrd{color:#00f;} .str{color:#006080;} .op{color:#00c;} .preproc{color:#c63;} .asp{background:#ff0;} .html{color:#800000;} .attr{color:#f00;} .alt{background:#f4f4f4;width:100%;margin:0;} .lnum{color:#606060;}
  注意：確保 CSS 在頁面載入，必要時清除快取並重整。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, B-Q1

C-Q2: 如何啟用 HTC 與「copy code」行為？
- A簡: 加入 .copycode CSS 並把 code.htc 置於 /themes 供行為載入。
- A詳: 步驟：1) 在「Custom Styles (Advanced)」追加：
  .copycode { cursor:hand; color:#c0c0ff; display:none; behavior:url('/themes/code.htc'); }
  2) 將 code.htc 上傳至網站根目錄的 /themes/code.htc；3) 確認以 HTTP 可存取該檔；4) 重新整理含程式碼頁。注意：路徑大小寫需與 CSS 完全一致；若改用其他路徑，需同步修改 CSS 的 behavior URL。IE 以外瀏覽器不支援 HTC，按鈕可能隱藏。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q14, A-Q15

C-Q3: 如何在貼文中啟用「copy code」按鈕？
- A簡: 插入程式碼時勾選「輸出 HTML 含原始碼」，並確保頁面含 .copycode 元素。
- A詳: 步驟：1) 以外掛或工具插入程式碼時，勾選「產生出來的HTML會包含原始程式碼」；2) 確認輸出區塊標題旁有 [copy code] 的元素（通常為 <span class="copycode">）；3) 網站已載入 C-Q2 的 CSS 與 HTC；4) 於 IE 測試點擊複製。注意：若看不到按鈕，檢查 .copycode 是否被 HTC 顯示，以及 HTC 是否下載成功。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q16, B-Q9

C-Q4: 如何驗證複製內容為乾淨純文字？
- A簡: 點擊按鈕後貼進記事本或 IDE，確認無行號與標記。
- A詳: 步驟：1) 在 IE 開啟含程式碼頁；2) 點擊 [copy code]；3) 開記事本/IDE（以純文字貼上），檢查是否無 .lnum 行號、無 HTML 標籤、縮排正確；4) 在 IDE 嘗試編譯（以 C# 為例）。若失敗，確保插入時勾選原始碼選項（A-Q16），並檢查 HTC 是否正確從原始節點讀取而非展示節點。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q10, D-Q10

C-Q5: 不依賴外掛，如何手動寫出展示結構？
- A簡: 以 .csharpcode 容器包 <pre>，標題旁放 .copycode 元素。
- A詳: 範例：
  <h3>MSDN Sample Code <span class="copycode">[copy code]</span></h3>
  <div class="csharpcode"><pre>using System; ...</pre></div>
  步驟：1) 在文章 HTML 模式插入上述結構；2) 確保已載入 C-Q1 的 CSS；3) 若需複製功能，依 C-Q2 部署 HTC。注意：實際外掛輸出結構可能略有差異，請以外掛輸出為準，手動時維持語意清楚與樣式一致。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q18

C-Q6: 站點不是用 /themes 路徑，如何調整？
- A簡: 改 CSS 中 behavior 的 URL，並將 HTC 放入對應目錄。
- A詳: 步驟：1) 選擇可公開讀取的資料夾（例 /assets/htc/）；2) 上傳 code.htc 至 /assets/htc/code.htc；3) 修改 CSS：.copycode { behavior:url('/assets/htc/code.htc'); }；4) 清除快取、重新整理測試；5) 直接以瀏覽器請求該 URL 確認可下載。注意：相對/絕對路徑選擇一致，跨子站時建議用絕對路徑。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q13, D-Q2

C-Q7: 在非 CS 平台（如 WordPress）如何整合？
- A簡: 把 CSS 加入主題樣式或外掛；HTC 置於可公開路徑並更新行為 URL。
- A詳: 步驟：1) 將 C-Q1 的 CSS 貼入主題的 style.css 或「外觀→自訂 CSS」；2) 上傳 code.htc 至主題或上傳目錄（例 /wp-content/uploads/code.htc）；3) 更新 .copycode 的 behavior 路徑；4) 於文章中插入 C-Q5 的結構或透過外掛產生；5) 在 IE 測試複製。注意：有些主機對 .htc MIME 設定需調整；非 IE 無法使用 HTC 行為。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q18, B-Q14

C-Q8: 如何調整「copy code」的外觀？
- A簡: 透過 .copycode CSS 修改顏色、游標與定位樣式。
- A詳: 範例：
  .copycode { color:#337ab7; cursor:pointer; float:right; margin-left:8px; behavior:url('/themes/code.htc'); }
  步驟：1) 於自訂 CSS 中覆寫 .copycode 規則；2) 調整位置（float/position）以貼齊標題右側；3) 依主題風格微調顏色；4) 測試載入不影響行為。注意：勿移除 behavior 設定；若需在非 IE 也顯示按鈕，可另行加入提示並在 HTC 不支援時隱藏。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q9, B-Q11

C-Q9: 如何為程式碼區塊套用深色主題？
- A簡: 覆寫 .csharpcode 子類別配色與背景為深色高對比。
- A詳: 範例：
  .csharpcode{background:#1e1e1e;color:#d4d4d4;font-family:Consolas,Monospace;}
  .csharpcode .kwrd{color:#569cd6;} .str{color:#ce9178;} .rem{color:#6a9955;} .lnum{color:#858585;}
  步驟：1) 於自訂 CSS 覆寫顏色；2) 確保行高與字距在深色下可讀；3) 測試列印/高對比模式。注意：維持足夠對比與一致字型，保留 .alt 的微弱對比或停用交錯視覺。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q11, B-Q12

C-Q10: 如何驗證 HTC 已成功載入？
- A簡: 以瀏覽器直接開啟 /themes/code.htc；檢視按鈕是否顯示並可點擊。
- A詳: 步驟：1) 在瀏覽器輸入 https://your.site/themes/code.htc 檢查可讀；2) 開啟含 .copycode 的頁面，確認按鈕從隱藏變為可見；3) 在 IE 點擊測試剪貼簿；4) F12 檢查網路請求是否載入 .htc，與是否有 404/403。注意：若使用 CDN 或代理，需確保 .htc 正確轉送與 Content-Type 合理（可為 text/x-component 或 text/plain）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, D-Q2

### Q&A 類別 D: 問題解決類（10題）

D-Q1: 「copy code」按鈕不顯示怎麼辦？
- A簡: 檢查 .copycode CSS 載入、HTC 路徑正確與瀏覽器為 IE。
- A詳: 症狀：標題旁未出現 [copy code]。原因：1) CSS 未載入或被覆蓋；2) HTC 載入失敗（URL 錯、大小寫不符、403/404）；3) 非 IE 瀏覽器不支援 behavior；4) 行為初始化失敗。解法：確認 C-Q1/C-Q2 已正確配置；以瀏覽器直接請求 code.htc；用 IE 測試；檢查 F12 網路錯誤。預防：使用固定路徑與大小寫一致，於部署後進行整站驗證。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q9, C-Q10

D-Q2: HTC 404 或載入失敗如何排查？
- A簡: 驗證 URL、大小寫、檔案位置與伺服器 MIME/存取權限。
- A詳: 症狀：網路面板顯示 code.htc 404/403。原因：放錯目錄、大小寫不符、路由攔截、未部署、權限不足。解法：確保實體位於網站根目錄 /themes/code.htc（或同步調整 CSS 行為 URL），檢查伺服器存取權限，直接請求該路徑驗證。預防：建立部署檢查清單，變更路徑時同步修改 CSS。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q13

D-Q3: 點擊後未複製任何內容的原因？
- A簡: IE 剪貼簿權限限制、未輸出原始碼、HTC 未正確讀取節點。
- A詳: 症狀：點擊無反應或貼上為空。原因：1) IE 設定阻擋程式存取剪貼簿；2) 未勾選「含原始碼」導致來源不純；3) HTC 邏輯找錯 DOM；4) 例外拋出未提示。解法：調整 IE 安全區域允許剪貼簿存取；依 A-Q16 重新插入內容；檢查 HTC DOM 對應；於開發者工具觀察錯誤。預防：在設計上加入權限檢測與用戶提示。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q3, B-Q10

D-Q4: 語法高亮未生效（都是黑白）怎麼辦？
- A簡: 確認 CodeFormatter CSS 已載入且類別名稱與 HTML 匹配。
- A詳: 症狀：程式碼無色彩。原因：CSS 未載入/順序錯誤、類別名不一致、快取未更新。解法：確認 C-Q1 CSS 存在於頁面；檢查 .csharpcode 與子類別是否命中；清除瀏覽器快取；檢視是否有其他 CSS 覆蓋。預防：在統一位置載入樣式，避免多重覆寫。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, C-Q1

D-Q5: 文字字型或背景顯示異常如何修正？
- A簡: 檢查字型堆疊、背景色與覆寫規則，必要時提高選擇器權重。
- A詳: 症狀：字型不等寬、背景不白或對比不足。原因：主題 CSS 覆蓋、系統無 Consolas。解法：調整 .csharpcode 使用字型堆疊（Consolas,"Courier New",Monospace），加入 !important 或提高選擇器權重，重新指定背景色；測試印刷樣式。預防：主題設計初期即整合程式碼區塊樣式。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q11, C-Q9

D-Q6: CS 將 <script> 移除導致互動失效，怎麼辦？
- A簡: 改以 HTC 行為實作，或由管理者調整安全設定允許腳本。
- A詳: 症狀：手寫或外掛注入的 <script> 消失。原因：CS 安全策略過濾。解法：採用本文 HTC 方案（C-Q2）避開腳本；或由管理者審慎調整 communityserver.config、白名單必要腳本。預防：遵循平台安全規範，優先低侵入作法。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q6

D-Q7: 非 IE 瀏覽器無法一鍵複製怎麼辦？
- A簡: 設計降級：隱藏按鈕或顯示提示；必要時改用跨瀏覽器腳本方案。
- A詳: 症狀：Chrome/Firefox 看不到或點了無效。原因：HTC 與 behavior 僅 IE 支援。解法：以 CSS/偵測在非 IE 隱藏按鈕；或在平台允許腳本時改用 Clipboard API 實作跨瀏覽器複製。預防：文件明確說明支援清單，避免誤導使用者。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q18, B-Q14

D-Q8: 貼上後出現行號或多餘空白如何處理？
- A簡: 確保來源使用原始碼節點，排除 .lnum 與展示標記。
- A詳: 症狀：貼到 IDE 有行號、對齊錯亂。原因：複製來源來自展示區（含標記/行號），未對齊處理。解法：依 A-Q16 重新輸出含原始碼；調整 HTC 讀取原始節點；必要時在複製前移除 .lnum 與多餘空白。預防：建立測試用例，確保每次複製結果一致。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q10, C-Q4

D-Q9: 部署後偶發失效（快取/順序問題）怎麼辦？
- A簡: 固化載入順序、清快取、避免條件載入影響行為綁定。
- A詳: 症狀：有時有色彩，有時無按鈕。原因：CSS/HTC 延遲載入、快取殘留、動態內容延後注入。解法：將 CSS 放 head；確認 .copycode 與目標代碼在 DOM ready 時已存在；檢查 CDN/代理快取設定。預防：版本化樣式路徑、部署腳本加快取清除。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q19, C-Q10

D-Q10: 貼上後無法編譯，可能原因？
- A簡: 原始碼未輸出、複製來源錯誤、字元被轉義或缺行結尾。
- A詳: 症狀：IDE 報語法錯。原因：1) 未勾選輸出原始碼；2) 複製到含 HTML 的文本；3) 特殊字元轉義（如 &lt; &gt;）；4) 行結尾不一致。解法：勾選原始碼輸出（A-Q16）；確保 HTC 取自純文字來源；貼到純文字模式；檢查字元編碼與換行。預防：在文章內提供可編譯的最小範例，並自測複製結果。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q10, C-Q4

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 CodeFormatter？
    - A-Q2: 為什麼要為 CodeFormatter 配置網站端 CSS？
    - A-Q3: CodeFormatter 產生的 HTML 有何特點？
    - A-Q4: C# Code Formatter 的 CSS 主要包含哪些類別？
    - A-Q5: 為什麼建議將樣式抽離到 CSS？
    - A-Q6: 什麼是「copy code」功能？
    - A-Q7: 為什麼需要「copy code」功能？
    - A-Q11: 什麼是 Community Server（CS）？
    - A-Q12: 為何 Community Server 會封鎖 <script>？
    - A-Q19: 什麼是 CS 的「Custom Styles (Advanced)」？
    - B-Q1: 語法高亮的 CSS 原理如何運作？
    - B-Q2: CodeFormatter 產生的 HTML 結構為何？
    - C-Q1: 如何在 Community Server 加入 CodeFormatter 的 CSS？
    - C-Q2: 如何啟用 HTC 與「copy code」行為？
    - C-Q3: 如何在貼文中啟用「copy code」按鈕？

- 中級者：建議學習哪 20 題
    - A-Q8: 什麼是 HTC（HTML Component）？
    - A-Q9: HTC 與 jQuery 的差異是什麼？
    - A-Q10: 什麼是 HTA（HTML Application）？
    - A-Q14: .copycode 這段 CSS 的作用是什麼？
    - A-Q15: 為什麼 HTC 檔案要放在 /themes/code.htc？
    - A-Q16: 勾選「產生出來的HTML會包含原始程式碼」有何用？
    - A-Q18: 本方案的瀏覽器相容性如何？
    - B-Q3: 「copy code」複製到剪貼簿的機制是什麼？
    - B-Q4: HTC 如何統一管理 DHTML 事件？
    - B-Q5: CSS behavior:url(...) 的運作流程為何？
    - B-Q6: 在 CS 被動過濾 <script> 的情況如何繞過需求？
    - B-Q9: 「copy code」連結如何顯示與觸發？
    - B-Q10: 如何確保複製的是「乾淨純文字」？
    - B-Q11: 字型與配色策略有何考量？
    - B-Q12: 交錯行背景（.alt）與行號（.lnum）如何協作？
    - B-Q13: 路徑與大小寫對 HTC 載入的影響？
    - B-Q19: 頁面快取與載入順序對樣式/行為影響？
    - C-Q5: 不依賴外掛，如何手動寫出展示結構？
    - C-Q6: 站點不是用 /themes 路徑，如何調整？
    - C-Q10: 如何驗證 HTC 已成功載入？

- 高級者：建議關注哪 15 題
    - A-Q17: 為什麼預覽不用直接 IE 開 HTML，而改用 HTA？
    - B-Q7: HTA 為何能降低本機 HTML 的安全提示？
    - B-Q8: 預覽機制的設計概念是什麼？
    - B-Q14: 在無法用 HTC 的環境如何設計降級？
    - B-Q15: 為何不直接修改 communityserver.config 啟用 <script>？
    - B-Q16: 安全層面應注意什麼？
    - B-Q20: 此方案的擴充與替代方向？
    - C-Q7: 在非 CS 平台（如 WordPress）如何整合？
    - C-Q8: 如何調整「copy code」的外觀？
    - C-Q9: 如何為程式碼區塊套用深色主題？
    - D-Q1: 「copy code」按鈕不顯示怎麼辦？
    - D-Q3: 點擊後未複製任何內容的原因？
    - D-Q7: 非 IE 瀏覽器無法一鍵複製怎麼辦？
    - D-Q9: 部署後偶發失效（快取/順序問題）怎麼辦？
    - D-Q10: 貼上後無法編譯，可能原因？