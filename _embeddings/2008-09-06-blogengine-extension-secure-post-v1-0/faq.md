# BlogEngine Extension: Secure Post v1.0

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 SecurePost（BlogEngine.NET 擴充）？
- A簡: SecurePost 是 BlogEngine.NET 的輕量密碼保護擴充，透過事件攔截與伺服端驗證，只對指定文章顯示輸入密碼提示。
- A詳: SecurePost 是一個為 BlogEngine.NET 設計的簡易內容保護 Extension。它不需建立使用者帳號或登入流程，只針對內文開頭含有特定標記的文章啟用保護，攔截輸出流程，改為顯示輸入密碼提示，並在伺服端驗證 URL 參數中的密碼是否正確。若通過，才回復顯示原文；若未通過，持續顯示提示。此設計聚焦「最小可行保護」，以低門檻滿足特定情境分享需求。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q5, B-Q2

A-Q2: SecurePost 解決了什麼使用情境與需求？
- A簡: 無需帳號與登入，只要輸入文章級密碼即可閱讀，適合臨時、限定對象的簡易保護。
- A詳: 需求來自「特定幾篇文章需要輸入密碼才能看」，且作者不想為每位讀者建立帳號或管理角色。SecurePost 以文章級別控制，僅當內文開頭含標記時才啟用，避免全站複雜權限與登入流程。它透過伺服端驗證簡單密碼，快速達成「看前先輸入暗號」的輕量保護目標，特別適合家庭、班級、內部分享等低風險場景。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q3, A-Q6

A-Q3: SecurePost 與 Password Protected Post 擴充的差異是什麼？
- A簡: 前者以單一密碼保護單篇文章，後者需登入並依角色與分類授權，權限模型較重。
- A詳: Password Protected Post 採用登入後的角色與分類授權機制，適合站內既有帳號管理與細緻權限控制。SecurePost 則不需登入，僅以單一密碼保護特定文章，讀者輸入密碼即可閱讀。前者安全性與治理較強、複雜度高；後者配置快速、維運成本低，聚焦極簡場景。選擇取決於管理需求強度與使用者體驗取捨。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q9, B-Q4

A-Q4: 為什麼不使用 IIS 整合式驗證而採用 SecurePost？
- A簡: 整合式驗證易造成授權錯配與體驗不佳；SecurePost 以文章級密碼更符合簡單需求。
- A詳: IIS 整合式驗證屬伺服器層級，需處理使用者身分、群組與資源授權，對只需「幾篇文章輸入密碼」的需求過於繁重，且容易出現該擋未擋、該放未放的情況。SecurePost 在應用層攔截文章輸出，僅針對被標記的文章啟用簡單密碼保護，體驗更直覺，部署也更輕量，避免全站安全策略帶來的維運成本。
- 難度: 中級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q5, B-Q2

A-Q5: SecurePost 的核心安全原則是什麼？
- A簡: 密碼必須伺服端驗證，且在未通過前，文章內容不得在用戶端出現或被簡單揭露。
- A詳: 作者定下兩大原則：(1) 密碼只在伺服端比對，避免在前端原始碼可被直接讀出；(2) 在未通過驗證前，文章真實內容不得出現在客戶端（不以 DHTML 僅「藏」起來），從根本避免右鍵檢視原始碼即可看到內容。這讓保護機制基於伺服端輸出決策，有效降低內容洩漏風險。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q5, D-Q8

A-Q6: SecurePost 如何指定哪些文章需要保護？
- A簡: 文章內文開頭須以 [password] 作為啟用標記，未標記的文章不受影響。
- A詳: 為避免全站套用，SecurePost 採「顯式啟用」策略：僅當文章內容（e.Body）以字串 [password] 開頭時，才進入保護流程。程式以字首比對（忽略大小寫文化差異）判斷是否啟用，從而精準控制保護範圍。其他文章維持原有輸出，不被攔截或修改。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q12, C-Q3, C-Q10

A-Q7: 為什麼選擇使用 Post.Serving 事件來攔截輸出？
- A簡: Post.Serving 可在文章輸出前統一介入並修改內容，是最小侵入、覆用性高的切入點。
- A詳: BlogEngine.NET 在內容輸出前觸發 Post.Serving 事件，提供擴充掛鉤機制。SecurePost 借助此事件將原文改寫為「輸入密碼」提示，或在驗證通過時放行原文。這種事件導向方式不需改動核心程式碼，且對所有輸出位置（頁面、摘要）一致生效，維護性與可移植性佳。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q5, C-Q1

A-Q8: SecurePost 的安全性界線與限制為何？
- A簡: 採明碼 query string，防竊聽與複雜攻擊不在目標範圍，定位為最低限度保護。
- A詳: SecurePost 強調「基本可用」而非完整資訊安全。密碼以 URL 參數傳遞，未採雜湊或傳輸層加密；若無 HTTPS，可能遭攔截或被瀏覽器記錄。它避免了最直觀的右鍵檢視原始碼洩漏，但不抵禦中間人攻擊、暴力嘗試等。適合低風險場合，不建議用於敏感或機密資訊。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, A-Q14, D-Q7

A-Q9: 與需要登入的權限控制相比，SecurePost 的價值是什麼？
- A簡: 以極低成本提供文章級最小保護，避免帳號管理負擔，提升可用性與部署速度。
- A詳: 帳號與角色帶來細緻控制與審計能力，但需要使用者註冊、登入、權限維護。SecurePost 去除這些摩擦，讓作者僅以一組密碼限制存取，快速滿足「只讓少數人看」的需求。它不是權限系統替代品，而是針對小場景的務實工具，提升效率與使用體驗。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, B-Q2, C-Q5

A-Q10: 什麼是 BlogEngine 的 Extension Manager？
- A簡: Extension Manager 管理擴充套件設定與啟用，允許以 UI 編輯參數、匯入設定。
- A詳: BlogEngine.NET 提供 Extension Manager 以圖形介面管理擴充。SecurePost 利用其設定儲存三個參數（顯示訊息、密碼提示、密碼值），並透過 ExtensionSettings 匯入預設值。管理者登入後可在 UI 編輯參數，無須手動改檔或資料庫，即可快速調整行為。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, C-Q2, C-Q1

A-Q11: SecurePost 可調整的設定有哪些？
- A簡: 三項：保護時顯示訊息、密碼提示文字、實際密碼值，皆可於管理介面修改。
- A詳: 為方便非技術使用者操作，SecurePost 透過 ExtensionSettings 暴露三個可調參數：(1) SecurePostMessage：提示用語；(2) PasswordHint：提醒密碼線索；(3) PasswordValue：比對用密碼。這些值具有預設內容，並可於管理後台以 UI 即時調整，立即影響執行行為。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, B-Q4, C-Q2

A-Q12: settings.IsScalar 在此扮演什麼角色？
- A簡: 將設定視為單筆資料集合（非表格多列），簡化 UI 與存取模式。
- A詳: ExtensionSettings 支援「多列」或「單筆」設定。IsScalar 設為 true 表示本擴充僅有一組設定值，不需新增、刪除多筆項目。這讓 Extension Manager 的 UI 呈現為單頁表單，程式端也能用 GetSingleValue 直接取得特定鍵值，簡化讀寫與維護。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q14, C-Q2

A-Q13: 哪些情況會略過密碼保護？
- A簡: 已登入的使用者、密碼驗證通過、或文章未以 [password] 標記，皆不攔截內容。
- A詳: SecurePost 先後檢查：(1) HttpContext.Current.User.Identity.IsAuthenticated，如已驗證則直接放行；(2) Request["pwd"] 是否等於設定密碼，若相符放行；(3) 內文是否以 [password] 開頭，否則不啟用保護。三段判斷確保僅當必要時才改寫輸出，避開不相關文章與合法使用者。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q18, D-Q5

A-Q14: 為何密碼以 Query String 傳遞（而非雜湊或表單提交）？
- A簡: 為求簡單快速，採用 URL 參數；作者明確接受「明碼」的限制，非追求高安全。
- A詳: 目標是最小可行保護與快速完成。若採雜湊需前後端一致演算法、額外程式與部署複雜度；表單提交亦需調整流程。作者選擇直接用 ?pwd=xxx，清楚知悉其安全風險，並界定適用於低風險場合。這是以可用性優先的折衷方案。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q10, D-Q7

A-Q15: 什麼是 POC（Proof of Concept）在此的意義？
- A簡: 先用最少程式驗證可行性與體驗，再逐步補強設定與細節。
- A詳: 作者以少量程式碼攔截輸出並顯示密碼提示，驗證需求可被滿足（POC）。確認路徑可行後，才加入設定管理、登入放行等完善化。此法能快速驗證核心想法，避免過早最佳化與過度設計，提高開發效率與成功率。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, C-Q5, D-Q1


### Q&A 類別 B: 技術原理類

B-Q1: Post.Serving 事件如何運作？
- A簡: 於文章輸出前觸發，允許擴充讀寫 e.Body、判斷 e.Location，改寫呈現內容。
- A詳: BlogEngine 在呈現文章內容前會引發 Post.Serving 事件，傳入 ServingEventArgs。擴充可於事件中讀取原始 e.Body、定位輸出情境（例如頁面或 Feed），並以程式改寫 e.Body。SecurePost正是藉此在未通過驗證前輸出「輸入密碼」畫面，而在通過驗證後直接放行原文，完成可插拔的輸出控制。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q5, B-Q21

B-Q2: SecurePost 的整體執行流程為何？
- A簡: 事件掛鉤→條件判斷→未通過則改寫為提示→通過則放行原文。
- A詳: 靜態建構子註冊 Post.Serving 事件處理器。執行時先檢查使用者是否已登入，是則 return 放行；再讀取 Request["pwd"] 與設定密碼比對，相同則放行；再檢查 e.Body 是否以 [password] 開頭，不是則放行；若需保護，組出提示密碼的 HTML 並覆寫 e.Body。如此以「最小侵入、條件短路」實現有效攔截。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q6, C-Q5

B-Q3: 靜態建構子在 Extension 中的角色是什麼？
- A簡: 用於一次性初始化：註冊事件、匯入設定、載入設定物件，確保擴充生效。
- A詳: SecurePost 以 static constructor 執行啟動程序：註冊 Post.Serving 事件處理器；建立 ExtensionSettings、加入三個參數與預設值；匯入設定到 Extension Manager；再以 GetSettings 取得實際設定實例供執行期使用。此初始化流程僅執行一次，確保擴充與設定在應用程序生命週期中可用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q14, C-Q1

B-Q4: ExtensionSettings 與 Extension Manager 如何整合？
- A簡: 程式端定義參數與預設值，匯入後由 UI 管理；執行期以 GetSingleValue 取用。
- A詳: 擴充建立 ExtensionSettings("SecurePost")，加入三個參數鍵與預設值，設 IsScalar=true 並設定 Help 說明，再呼叫 ExtensionManager.ImportSettings 匯入。之後使用 ExtensionManager.GetSettings 取得設定物件，執行期透過 GetSingleValue(key) 讀值。UI 端可編輯並持久化，程式端即時反映。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, A-Q11, A-Q12

B-Q5: e.Body 的替換機制與注意事項？
- A簡: 事件中直接以字串生成新 HTML 指派給 e.Body；須避免洩露原文內容。
- A詳: 在 Post.Serving 事件內，以 StringBuilder 組出提示畫面 HTML，最後 e.Body = bodySB.ToString()。在密碼未通過前不應包含任何原文內容或可還原線索；必要時對動態訊息進行 HtmlEncode，避免 XSS。替換只影響內容本身，不更動標題、作者等其他欄位。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q16, D-Q8

B-Q6: 密碼驗證邏輯的關鍵順序為何？
- A簡: 先放行已登入→比對密碼→判斷是否需保護→否則改寫提示畫面。
- A詳: 邏輯順序採「短路」：1) 若 Identity.IsAuthenticated，直接 return；2) 若 Request["pwd"] == Password，return；3) 若 e.Body 非 [password] 開頭，return；4) 以上皆非，表示需保護且未通過，將 e.Body 改為密碼提示。順序設計兼顧效能與正確性，減少不必要處理。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q9, D-Q1

B-Q7: 如何辨識輸出位置（例如 Feed）？
- A簡: 透過 ServingEventArgs.Location 判斷，如為 Feed 可調整行為或不顯示輸入框。
- A詳: 事件參數 e.Location 指示輸出情境（ServingLocation.Feed 等）。SecurePost 範例在 Feed 分支留白，可延伸為僅顯示提示文字、不附導向按鈕，避免 RSS 閱讀器互動不佳。此設計讓同一份邏輯適配不同通道的呈現需求。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q8, D-Q6, B-Q21

B-Q8: 密碼提示畫面 HTML 如何生成？
- A簡: 以 StringBuilder 串接提示、輸入框與按鈕，按鈕用 JS 導向附加 ?pwd= 的網址。
- A詳: 範例用 StringBuilder.AppendFormat 輸出提示訊息（HtmlEncode 保護），再輸出 <input type="password"> 與 <button>。按鈕 onclick 將 document.location.href 設為 post.AbsoluteLink + "?pwd=" + escape(輸入值)，完成導向提交。此法簡單直覺，易於改版與國際化。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q10, C-Q7, C-Q9

B-Q9: 如何在伺服端取得使用者輸入的密碼？
- A簡: 透過 HttpContext.Current.Request["pwd"] 讀取，與設定值比對。
- A詳: SecurePost 使用 ASP.NET 的 Request 集合讀取名為 "pwd" 的參數。Request[] 會整合 QueryString 與 Form 值，因此即使改成表單 POST 亦可取得。比對方式為字串相等判斷，通過則直接 return 放行；否則進入內容攔截流程。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, C-Q9, D-Q1

B-Q10: 為什麼採用 JS 導向並夾帶 Query String？
- A簡: 以最少程式達成互動提交；代價是密碼出現在網址，屬可接受風險折衷。
- A詳: 透過 button 的 onclick 直接改變 location.href，可省去建立 form 與事件處理的複雜度，快速提交到同一篇文章的原始連結並附 pwd 參數。雖有安全性上的可見性問題，但實作簡單、跨瀏覽器相容性高，符合此擴充「快速可用」定位。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, C-Q9, D-Q7

B-Q11: 為何使用 return 放行內容而非重寫畫面？
- A簡: return 提早結束處理，保留原輸出，效能與可讀性好，避免多餘組字串。
- A詳: 事件處理器多採「提早返回」提高可讀性與效能。當符合任一放行條件（已登入、密碼正確、無需保護）即 return，可避免進入後續字串組裝與覆寫。這種守門員模式清晰表達邏輯分支，減少錯誤面積。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, D-Q1, D-Q2

B-Q12: 為什麼用 StartsWith("[password]") 當啟用條件？
- A簡: 易於編輯與辨識，對文章影響最小；忽略大小寫避免文化差異造成失效。
- A詳: 在內容首行加入 [password] 可由作者直接在編輯器操作，無需額外欄位或後台標籤。比較以 StringComparison.CurrentCultureIgnoreCase，提升容錯性。此法不更動資料結構，維持低耦合與可移除性。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q6, C-Q3, C-Q10

B-Q13: 擴充安裝到 ~/App_Code/Extension 的原理？
- A簡: App_Code 是 ASP.NET 動態編譯區，放入 .cs 後由框架自動編譯並裝載。
- A詳: BlogEngine 採 ASP.NET 應用程式模型，App_Code 目錄下的原始碼會在應用啟動時動態編譯。將 SecurePost.cs 放在 ~/App_Code/Extension 後，應用啟動自動載入類別，靜態建構子負責註冊事件與設定，即完成「部署即生效」的輕量安裝。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q1, D-Q4, B-Q3

B-Q14: ImportSettings 與 GetSettings 有何差異？
- A簡: ImportSettings 用來註冊/匯入設定架構與預設值；GetSettings 用於執行期讀取實際值。
- A詳: ImportSettings 將擴充的設定中繼資料（參數清單、預設值、說明等）註冊進管理系統，使 UI 可編輯並儲存。GetSettings 則在執行期抓到目前有效設定（可能已被使用者修改），供程式讀取鍵值並行為化。兩者分別對應「定義/註冊」與「讀取/使用」階段。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, C-Q2, B-Q4

B-Q15: 為何需對提示文字進行 HtmlEncode？
- A簡: 防止設定值被注入 HTML/JS，避免 XSS，確保輸出安全。
- A詳: 提示訊息與密碼提示由使用者設定，若未編碼，惡意字串可能成為 DOM 的一部分而執行腳本。SecurePost 以 HtmlEncode 包裹輸出，有效中斷標籤與腳本解釋，降低跨站攻擊風險。這是處理動態字串輸出的基本防線。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q5, D-Q8, C-Q7

B-Q16: 已登入使用者放行的技術依據是什麼？
- A簡: 讀取 HttpContext.Current.User.Identity.IsAuthenticated，若為 true 則不攔截。
- A詳: ASP.NET 將驗證狀態掛在 HttpContext 的 User.Identity 上。SecurePost 在事件開頭先檢查 IsAuthenticated，若為 true 直接 return，確保站內既有權限機制高於文章密碼，避免對已授權使用者造成多餘阻礙。這讓擴充與站內登入相容。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q13, D-Q5, B-Q6

B-Q17: 為何使用 Post.AbsoluteLink 作為導向目標？
- A簡: 確保導向至文章正式網址，避免相對路徑或查詢字串錯誤。
- A詳: AbsoluteLink 是 BlogEngine 為文章提供的絕對 URL，能避免當前頁面相對路徑與路由差異造成的導向問題。將 pwd 附加於此，可在各種佈景與部署環境下穩定運作，降低前端環境差異帶來的錯誤。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q7, D-Q1, B-Q10

B-Q18: ServingEventArgs 的關鍵屬性有哪些？
- A簡: e.Body（可讀寫內容）、e.Location（輸出位置）；兩者決定呈現與通道行為。
- A詳: ServingEventArgs 提供擴充修改輸出的介面。e.Body 包含原本要輸出的 HTML，可直接改寫；e.Location 指示當前輸出通道，如 Feed 或頁面。SecurePost 透過這兩者決定是否攔截與如何顯示提示，實現通道感知的輸出管控。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q7, B-Q5

B-Q19: 事件式攔截對效能有何影響與設計考量？
- A簡: 採短路判斷與最小組字串，僅在必要時改寫，降低每篇輸出的額外成本。
- A詳: 事件每次輸出都會觸發，因此邏輯以「先放行再攔截」設計，減少不必要處理。僅當需保護且未通過時才組字串替換，並避免昂貴的運算。此策略讓擴充在高流量下仍具可擴展性，對未標記事件幾乎零影響。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q6, D-Q3, D-Q2

B-Q20: [Extension(...)] 屬性中版本與作者資訊的用途？
- A簡: 用於顯示於 Extension Manager，提供識別、版本管理與來源連結。
- A詳: 類別頂端以 Extension(name, version, link) 標註，讓管理介面能顯示名稱、版本與作者連結，便於識別與維護。這有助於使用者確認擴充來源、版本更新與支援資訊，強化治理與可信度。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, D-Q4, B-Q14


### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何安裝 SecurePost 擴充？
- A簡: 複製 SecurePost.cs 至 ~/App_Code/Extension，重新啟動網站，在管理後台啟用與設定。
- A詳: 實作步驟：1) 將文末完整程式碼另存為 SecurePost.cs；2) 放入 ~/App_Code/Extension/；3) 重新啟動站台或觸發應用重載；4) 以管理者登入 BlogEngine 後台，至 Extension Manager 找到 SecurePost；5) 啟用並編輯設定。注意保持檔名與類別一致，確保無語法錯誤。最佳實踐：版本控管與備份原始碼。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q13, B-Q20, C-Q2

C-Q2: 如何設定顯示訊息、密碼提示與密碼值？
- A簡: 於 Extension Manager 的設定畫面編輯三個參數，儲存後立即生效。
- A詳: 步驟：1) 後台 > Extensions > SecurePost > Edit；2) 分別填入「顯示訊息」「密碼提示」「指定密碼」；3) 儲存。程式碼片段：透過 _settings.GetSingleValue("SecurePostMessage/PasswordHint/PasswordValue") 取得；IsScalar=true 表示單筆設定。注意：訊息請避免含 HTML；若需，確保已 HtmlEncode 以防 XSS。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, B-Q4, B-Q15

C-Q3: 如何標示某篇文章為受保護文章？
- A簡: 在文章內文開頭加入 [password] 標記，儲存後即受 SecurePost 攔截保護。
- A詳: 步驟：1) 編輯文章；2) 於最前面輸入 [password]（大小寫不拘）；3) 發布。程式碼：if (!e.Body.StartsWith("[password]", StringComparison.CurrentCultureIgnoreCase)) return; 注意：標記需在內文最前面，不可有空白或其他字元。最佳實踐：另行在文末提醒讀者需輸入密碼。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q12, D-Q2

C-Q4: 如何修改提示畫面文字與語氣？
- A簡: 直接在設定中調整提示文字，程式端以 HtmlEncode 輸出，避免 HTML 注入。
- A詳: 步驟：後台設定 SecurePostMessage 與 PasswordHint。關鍵程式：bodySB.AppendFormat("<b>{0}</b>", HtmlEncode(SecurePostMessage)); 注意：若需使用粗體、換行請在設定端輸入純文字，由程式負責安全輸出。最佳實踐：保持訊息精簡，提供清楚的提示但避免洩漏太多線索。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q15, D-Q8

C-Q5: 如何驗證擴充是否正確運作？
- A簡: 清除登入狀態，開啟被標記文章，應顯示密碼提示；輸入正確密碼後顯示原文。
- A詳: 步驟：1) 登出或用匿名模式；2) 造訪含 [password] 文章；3) 應看見提示與密碼欄；4) 輸入設定密碼，URL 將出現 ?pwd=xxx；5) 頁面顯示原文。關鍵檢查：未標記文章不受影響；已登入者不會被攔截。注意：若未生效，確認檔案路徑與語法、重啟應用。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q2, D-Q1, D-Q4

C-Q6: 如何確保已登入使用者可直接觀看？
- A簡: 擴充已內建檢查 IsAuthenticated，若為 true 則直接放行無需輸密碼。
- A詳: 程式片段：if (HttpContext.Current.User.Identity.IsAuthenticated == true) return; 使用方式：只要站台已有登入機制（Forms/Windows），通過驗證的使用者就不會被攔截。注意：若仍被攔截，確認驗證流程與管線、或其他擴充是否覆寫輸出。最佳實踐：清楚告知內部使用者可免密碼存取。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q16, D-Q5

C-Q7: 如何客製輸入 UI（按鈕文字、欄位等）？
- A簡: 修改組字串區塊，調整 input/button HTML 與 onclick 腳本，並保持 HtmlEncode。
- A詳: 步驟：1) 找到 bodySB.Append(...) 區塊；2) 改為 placeholder、按鈕文字等；3) 例如：<input id="postpwd" type="password" placeholder="請輸入密碼">；4) 變更按鈕 <button>GO</button> 文字；5) 仍使用 HtmlEncode 輸出訊息。注意：避免輸入框 id 與 JS 取值不一致造成讀值失敗。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, B-Q15, D-Q1

C-Q8: 如何調整 RSS/Feed 的顯示行為？
- A簡: 依 e.Location==Feed 分支輸出純文字提示，不附互動控制，避免閱讀器相容性問題。
- A詳: 步驟：在 if (e.Location == ServingLocation.Feed) 分支輸出簡短提示：例如 e.Body="本篇已受密碼保護，請至網站輸入密碼觀看。"; 程式碼：判斷分支後直接賦值。注意：RSS 多為只讀環境，不適合輸入表單或 JS。最佳實踐：提示附文章連結，導流至正規頁面。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q7, D-Q6, C-Q5

C-Q9: 如何改用表單 POST 遞送密碼，避免顯示於網址？
- A簡: 將按鈕改為 <form method="post"> 提交，伺服端以 Request.Form["pwd"] 讀取。
- A詳: 步驟：1) 將輸入與提交改為 <form method="post" action="{post.AbsoluteLink}">；2) <input name="pwd" type="password"> 與 <button type="submit">送出</button>；3) 伺服端使用 Request["pwd"] 仍可取得。注意：避免 CSRF 與快取問題；最佳實踐：同時建議使用 HTTPS。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q9, B-Q10, D-Q7

C-Q10: 如何改變啟用規則（不使用 [password] 標記）？
- A簡: 將 StartsWith("[password]") 改為自訂條件，如分類、標籤或自訂前綴。
- A詳: 步驟：1) 尋找檢查語句 if (!e.Body.StartsWith(...)) return; 2) 替換為自訂條件，如檢查 post.Tags 或 Category；3) 或以正則比對特定前綴；4) 測試多篇文章。注意：保持條件判斷快速、可維護。最佳實踐：保留顯式啟用，避免誤攔。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q12, C-Q3, D-Q2


### Q&A 類別 D: 問題解決類（10題）

D-Q1: 輸入正確密碼仍看不到內容怎麼辦？
- A簡: 檢查參數名稱、導向網址、判斷順序及其他擴充是否覆寫 e.Body。
- A詳: 症狀：輸入密碼後仍顯示提示。可能原因：1) 參數名非 pwd；2) JS 導向未帶參數；3) 判斷順序錯誤造成未 return；4) 其他擴充再次改寫 e.Body。解法：檢查 onclick 腳本與 Request["pwd"]、比對邏輯與 return 位置；暫時停用其他擴充排除衝突。預防：撰寫單元測試、維持短路結構。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q17, D-Q10

D-Q2: 為何所有文章都被攔截顯示密碼提示？
- A簡: 多半是啟用條件判斷錯誤，未正確檢查 [password] 標記或誤改邏輯。
- A詳: 症狀：未標記文章也被要求輸密碼。原因：StartsWith 檢查被移除/誤判；移動了 return 順序；或貼上內容自動加入了隱藏字符。解法：恢復 if (!e.Body.StartsWith(...)) return；確認不含 BOM/空白；加上 TrimStart。預防：建立明確啟用規則與編輯器檢查。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q12, C-Q3, C-Q10

D-Q3: 提示文字或密碼提示出現亂碼如何處理？
- A簡: 確保檔案與站台使用相同編碼（UTF-8），避免雙重編碼或未編碼輸出。
- A詳: 症狀：中文顯示亂碼。原因：檔案非 UTF-8、回應標頭與頁面編碼不一致、手動輸出未經正確編碼。解法：將 cs 檔案與佈景版面統一 UTF-8；確認 Response.ContentEncoding；保持 HtmlEncode 處理動態字串。預防：在開發環境即設定一致編碼政策。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, B-Q15, C-Q4

D-Q4: 安裝後 Extension Manager 中看不到 SecurePost？
- A簡: 檢查檔案路徑、類別標註、語法錯誤與應用是否成功重新編譯。
- A詳: 症狀：後台沒有出現擴充。原因：檔案未置於 ~/App_Code/Extension；[Extension(...)] 屬性遺失；編譯錯誤；應用未重載。解法：確認路徑與檔名；檢視錯誤日誌；觸發應用重啟（如 web.config 變更）。預防：版本控管、部署前本機測試成功。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q13, B-Q20, C-Q1

D-Q5: 已登入使用者仍被要求輸入密碼？
- A簡: 驗證管線可能未設定或自訂驗證失效，導致 IsAuthenticated 為 false。
- A詳: 症狀：登入後仍出現提示。原因：FormsAuth 未正確設定；自訂驗證未賦值 User；反向代理/子應用破壞 Cookie；事件執行順序受其他擴充影響。解法：追蹤 HttpContext.Current.User 身分；修正驗證設定；停用其他擴充比對。預防：統一驗證中介，撰寫整合測試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q16, B-Q6, C-Q6

D-Q6: RSS/Feed 中提示顯示異常或含互動元件？
- A簡: 在 e.Location==Feed 分支輸出純文字，避免表單或 JS。
- A詳: 症狀：RSS 閱讀器顯示破版或按鈕無效。原因：在 Feed 也輸出表單/JS。解法：於 Feed 分支輸出純文字提示與連結，不含互動元素。預防：在開發時即測試 RSS 通道，建立獨立呈現策略。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q7, C-Q8, C-Q5

D-Q7: 密碼出現在網址造成安全疑慮怎麼辦？
- A簡: 改用表單 POST、啟用 HTTPS、縮短快取與導頁紀錄，並教育使用者風險。
- A詳: 症狀：瀏覽器歷史或截圖看得到密碼。原因：採用 Query String 明碼。解法：C-Q9 改 POST 提交；全站啟用 HTTPS；避免外部連結攜帶 pwd；關閉中繼與快取。預防：在需求階段明確說明安全界線，避免承載敏感資訊。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q8, A-Q14, C-Q9

D-Q8: 如何避免 XSS 或注入風險？
- A簡: 對所有動態文字 HtmlEncode，避免將設定值直接拼入 HTML 或 JS。
- A詳: 症狀：惡意輸入導致腳本執行。原因：未編碼輸出設定值。解法：持續使用 HtmlEncode(SecurePostMessage 等)；JS 內嵌時使用適當編碼或改為 data- 屬性；審核輸入來源。預防：建立輸入/輸出編碼規範與安全審查。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q15, B-Q5, C-Q4

D-Q9: 例外錯誤：e.Body 為空或非文章內容怎麼處理？
- A簡: 增加空值與類型檢查，僅在 sender 為 Post 且 e.Body 有值時才處理。
- A詳: 症狀：偶發 NullReference。原因：事件可能在非預期情境觸發，或其他擴充先行改動。解法：加入健全性檢查：var post = sender as Post; if (post==null || string.IsNullOrEmpty(e.Body)) return; 預防：記錄日誌與防禦式編碼，避免假設。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q1, B-Q18, D-Q10

D-Q10: 與其他改寫 e.Body 的擴充發生衝突怎麼辦？
- A簡: 調整事件處理順序、相容性判斷與條件短路，必要時合併邏輯。
- A詳: 症狀：顯示內容不一致或彼此覆蓋。原因：多個擴充在 Serving 事件中改寫 e.Body。解法：控制載入順序（命名與編譯順序）；在 SecurePost 放行時提早 return；必要時將邏輯整合到單一擴充。預防：建立事件相容性準則與回歸測試。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q5, B-Q19, D-Q1


### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 SecurePost（BlogEngine.NET 擴充）？
    - A-Q2: SecurePost 解決了什麼使用情境與需求？
    - A-Q3: SecurePost 與 Password Protected Post 擴充的差異是什麼？
    - A-Q6: SecurePost 如何指定哪些文章需要保護？
    - A-Q7: 為什麼選擇使用 Post.Serving 事件來攔截輸出？
    - A-Q9: 與需要登入的權限控制相比，SecurePost 的價值是什麼？
    - A-Q10: 什麼是 BlogEngine 的 Extension Manager？
    - A-Q11: SecurePost 可調整的設定有哪些？
    - B-Q1: Post.Serving 事件如何運作？
    - B-Q5: e.Body 的替換機制與注意事項？
    - C-Q1: 如何安裝 SecurePost 擴充？
    - C-Q2: 如何設定顯示訊息、密碼提示與密碼值？
    - C-Q3: 如何標示某篇文章為受保護文章？
    - C-Q5: 如何驗證擴充是否正確運作？
    - D-Q4: 安裝後 Extension Manager 中看不到 SecurePost？

- 中級者：建議學習哪 20 題
    - A-Q4: 為什麼不使用 IIS 整合式驗證而採用 SecurePost？
    - A-Q5: SecurePost 的核心安全原則是什麼？
    - A-Q8: SecurePost 的安全性界線與限制為何？
    - A-Q12: settings.IsScalar 在此扮演什麼角色？
    - A-Q13: 哪些情況會略過密碼保護？
    - A-Q14: 為何密碼以 Query String 傳遞？
    - B-Q2: SecurePost 的整體執行流程為何？
    - B-Q3: 靜態建構子在 Extension 中的角色是什麼？
    - B-Q4: ExtensionSettings 與 Extension Manager 如何整合？
    - B-Q6: 密碼驗證邏輯的關鍵順序為何？
    - B-Q7: 如何辨識輸出位置（例如 Feed）？
    - B-Q9: 如何在伺服端取得使用者輸入的密碼？
    - B-Q10: 為什麼採用 JS 導向並夾帶 Query String？
    - B-Q16: 已登入使用者放行的技術依據是什麼？
    - B-Q17: 為何使用 Post.AbsoluteLink 作為導向目標？
    - B-Q18: ServingEventArgs 的關鍵屬性有哪些？
    - C-Q4: 如何修改提示畫面文字與語氣？
    - C-Q6: 如何確保已登入使用者可直接觀看？
    - C-Q8: 如何調整 RSS/Feed 的顯示行為？
    - D-Q1: 輸入正確密碼仍看不到內容怎麼辦？

- 高級者：建議關注哪 15 題
    - B-Q15: 為何需對提示文字進行 HtmlEncode？
    - B-Q19: 事件式攔截對效能有何影響與設計考量？
    - B-Q20: [Extension(...)] 屬性中版本與作者資訊的用途？
    - C-Q7: 如何客製輸入 UI（按鈕文字、欄位等）？
    - C-Q9: 如何改用表單 POST 遞送密碼，避免顯示於網址？
    - C-Q10: 如何改變啟用規則（不使用 [password] 標記）？
    - D-Q2: 為何所有文章都被攔截顯示密碼提示？
    - D-Q3: 提示文字或密碼提示出現亂碼如何處理？
    - D-Q5: 已登入使用者仍被要求輸入密碼？
    - D-Q6: RSS/Feed 中提示顯示異常或含互動元件？
    - D-Q7: 密碼出現在網址造成安全疑慮怎麼辦？
    - D-Q8: 如何避免 XSS 或注入風險？
    - D-Q9: 例外錯誤：e.Body 為空或非文章內容怎麼處理？
    - D-Q10: 與其他改寫 e.Body 的擴充發生衝突怎麼辦？
    - A-Q15: 什麼是 POC（Proof of Concept）在此的意義？