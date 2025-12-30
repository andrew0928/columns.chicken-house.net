---
layout: synthesis
title: "Web Site Application + Sandcastle"
synthesis_type: faq
source_post: /2007/02/16/web-site-application-sandcastle/
redirect_from:
  - /2007/02/16/web-site-application-sandcastle/faq/
---

# Web Site Application + Sandcastle

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 XML 文件註解（comment help）？
- A簡: C# 以 /// 撰寫的 XML 註解，透過編譯器 /doc 選項輸出 .xml，供 NDoc、Sandcastle 生成 API 說明文件。
- A詳: XML 文件註解是 C# 提供的結構化註解格式，常見標籤含 <summary>、<param>、<returns> 等。當以編譯器加上 /doc:xxx.xml 參數編譯時，會將註解萃取為對應型別與成員的 XML 說明，與編譯產生的組件（DLL）搭配，供 NDoc、Sandcastle 等說明工具解析，最後輸出 CHM 或網站形式的 API 文件。它讓程式碼註解成為可維護的正式文件來源，避免重寫文件。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, B-Q6, C-Q5

A-Q2: 為什麼產生說明文件需要同時提供 Assembly 與 XML 文件？
- A簡: 工具利用 DLL 的中繼資料了解 API 結構，使用 XML 提供文字說明，兩者缺一不可。
- A詳: 說明產生工具一方面須以反射讀取組件（DLL）的中繼資料，取得命名空間、型別、成員與其簽章（結構）；另一方面需要開發者撰寫的 XML 註解提供語意敘述（內容）。只有結構沒有內容，無法顯示說明；只有內容沒有結構，無法正確對應 API。因而工具皆要求同時輸入 Assembly 與 XML 文件，才能組合出完整、可瀏覽的 API 文件。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, B-Q2, C-Q5

A-Q3: 什麼是 Sandcastle？與 NDoc 有何不同？
- A簡: Sandcastle 是微軟的 .NET 文件生成工具，支援泛型等 .NET 2.0 功能，但生成速度較 NDoc 慢。
- A詳: Sandcastle 是微軟推出的 API 文件生成工具，能解析 .NET 2.0 之後的語言特性（如泛型），並轉換 Assembly 與 XML 註解成 CHM 或網頁。文章指出其速度較舊版 NDoc 慢：同樣專案，NDoc 約 20 分鐘完成，而 Sandcastle 約需 60 分鐘。雖然效能較慢，但因其支援較新語言特性，對需要 .NET 2.0+ 支援者較為實用。選用時可在功能與速度間權衡。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, B-Q10, C-Q5, D-Q5

A-Q4: 什麼是 ASP.NET 2.0 的 Web Site 專案型別？
- A簡: 不需預先產生單一 DLL，程式放在 App_Code 即可動態編譯，部署簡單但難取得 DLL 與 XML。
- A詳: Web Site 是 ASP.NET 2.0 引入的專案模型，檔案直接放在網站資料夾（如 App_Code）即可由 ASP.NET 執行階段動態編譯執行，不需像 Web Application 一樣先產生單一 DLL。優點是部署與修改彈性高；缺點是缺少預先編譯的 DLL 與 XML 註解輸出，導致無法直接餵給 NDoc/Sandcastle。當需要 API 文件或其他依賴 DLL 的工具時，Web Site 模型必須額外設法產出這些輸入。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, A-Q6, B-Q1

A-Q5: Web Site 與 Web Application 的差異是什麼？
- A簡: Web Application 預先編譯成單一 DLL；Web Site 動態編譯、無單一 DLL，取用 DLL/XML 較不便。
- A詳: Web Application 採傳統專案制，開發期以專案檔統一管理並產生單一 Assembly 與 XML，利於單元測試、文件生成與版本管理；Web Site 則以檔案為單位，由 ASP.NET 於伺服器端動態依目錄編譯，部署彈性高，但難以一次取得完整 DLL 與 XML 文件。在需要整合文件生成工具時，Web Application 天生較有利；Web Site 則需額外步驟產出必要輸入。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, B-Q1, C-Q4

A-Q6: App_Code 目錄的角色是什麼？
- A簡: App_Code 放置可共用的原始碼，ASP.NET 會依目錄為單位動態編譯，供整個網站使用。
- A詳: 在 Web Site 專案中，App_Code 是預設的程式碼資料夾。ASP.NET 執行階段會將其中的 .cs 檔視為同一編譯單元編譯，並可跨頁面引用。文章強調其編譯是「以目錄為單位」進行，子目錄亦會分次編譯，導致若用單一定名的 /doc 輸出，會在每次目錄編譯時被覆蓋或清理，造成產出不穩定。因此瞭解其編譯粒度是解決文件生成問題的關鍵。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, A-Q10, D-Q1

A-Q7: 什麼是 aspnet_compiler.exe？
- A簡: ASP.NET 編譯工具，可將網站預先編譯為多個組件，常用於部署與優化啟動速度。
- A詳: aspnet_compiler.exe 是 ASP.NET 的預先編譯工具，能將 Web Site 專案中的頁面與程式碼預先編譯為多個 Assembly，減少首次請求延遲並利於部署。文章提到可用該工具「直接 build web site，輸出 DLL」，但它不會自動產生對應 XML 文件，仍需其他方式補齊 XML，以便後續文件生成工具使用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, A-Q8, C-Q2

A-Q8: 什麼是 Web Deployment Project？
- A簡: VS2005 的附加專案類型，先用 aspnet_compiler 編譯，再合併多個組件為單一 DLL。
- A詳: Web Deployment Project（VS2005 SP1 內建）提供一個部署流程：先以 aspnet_compiler 編譯 Web Site，產生多個組件，接著再透過組件合併工具（assembly merge）將其併為單一 DLL，便於部署與管理。文章指出此法能「輕鬆拿到 DLL」，但仍無法產生 XML 註解文件，對於 NDoc/Sandcastle 的需求仍不完整，須額外處理 XML。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, C-Q3, D-Q5

A-Q9: 什麼是 C# 編譯器 csc.exe？
- A簡: 微軟 C# 命令列編譯器，可用參數設定輸出 DLL 與 XML 文件，適合自動化與腳本化。
- A詳: csc.exe 是 C# 的命令列編譯器，可透過 /target:library 產出 DLL，/doc:xxx.xml 匯出 XML 註解，/recurse:App_Code\*.cs 遞迴收集原始碼檔。文章透過單行指令，成功為 Web Site 的 App_Code 產出 DLL 與 XML，成為補齊 NDoc/Sandcastle 所需輸入的可行路徑。這種方式簡單、直觀，適合納入批次檔或 CI 流程。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, C-Q4, D-Q3

A-Q10: 為何在 web.config 設定 compilerOptions 產生 XML 會失敗？
- A簡: 因 App_Code 以目錄為單位多次編譯，固定檔名的 XML 在過程中被覆蓋或刪除。
- A詳: 透過 <system.codedom> 設定 compilerOptions="/doc:...xml" 雖可在簡單情境輸出 XML，但在實際站台中，ASP.NET 會針對各子目錄重複進行編譯，且該參數需指定單一檔名，無法是萬用字元或自動分檔。結果是每次子目錄編譯都覆蓋同一 XML，或在中途被清理，導致最終無穩定輸出。因此此法僅適用極簡結構，不符合生產環境需求。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q2, D-Q1

A-Q11: 為什麼 /doc 參數不能使用萬用字元造成限制？
- A簡: /doc 需單一檔名，Web Site 多階段編譯下會互相覆蓋，難以保留多份輸出。
- A詳: C# 編譯器的 /doc 參數設計為輸出單一 XML 檔案，對於一個「一次性」編譯流程非常合理。然而 Web Site 的 App_Code 採多目錄、多階段編譯，若每次都用同一檔名，必然互相覆蓋；若嘗試用萬用字元分檔，編譯器不支援。這個限制使得以 web.config 直接產出 XML 的可行性大幅降低，必須改以外部一次性整合編譯（如 csc.exe）處理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q9, C-Q4

A-Q12: 以 csc.exe 手動產出 DLL 與 XML 的策略是什麼？
- A簡: 以單次編譯收集 App_Code 下所有 .cs，輸出一個 DLL 與一個 XML，供說明工具使用。
- A詳: 文章採用「外部一次性編譯」策略，跳過 ASP.NET 多階段編譯：以 csc.exe /target:library /recurse:App_Code\*.cs /out:App_Code.dll /doc:App_Code.xml，將 App_Code 內所有 C# 原始碼一次編譯為 DLL，並同時匯出對應 XML 註解。這種作法可穩定產出 NDoc/Sandcastle 所需的兩個輸入，且容易封裝為批次檔或整合到 CI 流程。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q9, C-Q4, D-Q3

A-Q13: 為什麼手動 csc 編譯仍有覆蓋範圍限制？
- A簡: csc 只編譯現存 .cs，無法自動納入 ASP.NET 動態產生或轉換的程式碼。
- A詳: csc.exe 只會處理指定的原始碼檔案集合（如 App_Code\*.cs）。然而 Web Site 中有些檔案（如 .wsdl、.xsd）在 ASP.NET 編譯流程中會觸發工具自動產生代理類或 Typed DataSet 原始碼，.aspx/.ascx 也會經由模板解析產生半邊的 partial 類別。這些動態產物若未先行明確轉換為 .cs 並納入編譯，單用 csc 無法涵蓋，導致文件不完整。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, A-Q15, B-Q8, B-Q7

A-Q14: App_Code 中的 .wsdl/.xsd 會如何影響文件產生？
- A簡: 這些檔在 ASP.NET 會觸發自動產生程式碼；csc 未整合該步驟時，相關 API 將缺席。
- A詳: 放在 App_Code 的 .wsdl 可自動產生 Web Service 代理類，.xsd 可產生 Typed DataSet 對應的原始碼。這些步驟原本由 ASP.NET 編譯流程觸發。若改以外部 csc.exe 直接編譯 .cs，則未經產生的部分不會出現在輸入集中，造成文件缺漏。若要補齊，須先用對應工具將 .wsdl/.xsd 轉為 .cs 再編譯，否則需接受此範圍的文件缺口。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, C-Q8, D-Q4

A-Q15: 為什麼 .aspx/.ascx 的 code-behind 不能直接用 csc 編入？
- A簡: 其 partial 類的另一半由 ASP.NET 解析模板動態產生，單用 csc 缺少該半部定義。
- A詳: ASP.NET 頁面採 partial class 模式，code-behind 只是一半；另一半類別會由 ASP.NET 引擎在編譯時解析 .aspx/.ascx 模板自動產生對應 .cs，再與 code-behind 合併編譯。外部以 csc.exe 直接編譯時，少了模板解析與產生步驟，會遇到找不到成員或類型不完整的錯誤。因此 code-behind 類別通常不適合作為 csc 的輸入來源。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, D-Q3, C-Q8

A-Q16: 若完整重現 ASP.NET 編譯步驟是否可行？代價是什麼？
- A簡: 理論可行，但等於自製 aspnet_compiler 流程，工程大、維護成本高，不划算。
- A詳: 依序把 .wsdl/.xsd 轉碼、模板解析產生 .cs、合併與編譯，理論上能重現 ASP.NET 的完整產物，再行文件生成。然而這等同重做一個 aspnet_compiler 的子集合，需撰寫多段腳本或 MSBuild 工作，處理相依與序列，投入高、風險大。相較之下，聚焦於可重用的 class library、接受頁面相關 API 暫不進文件，成本效益更佳。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q14, A-Q15, B-Q3

A-Q17: 使用 Web Deployment Project 為何仍無法得到 XML 文件？
- A簡: 它負責編譯與合併 DLL，不會替你開啟 /doc 匯出 XML 註解，仍需另行產出。
- A詳: Web Deployment Project 流程是「先 aspnet_compiler 輸出多個 DLL，再以合併工具聚合為單一 DLL」。這條路徑著眼於部署與組件整合，不會自動將 C# XML 註解匯出成 .xml。因此即便順利拿到單一 DLL，仍缺乏文件工具需要的文字內容來源，必須以 csc、web.config 選項或其他方式額外產生 XML 註解檔，才能補足輸入。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q8, C-Q3, C-Q4

A-Q18: 為什麼最終選擇忽略部分（如 .ascx）文件產出？
- A簡: 文件重點在可共用的 class library；頁面類別較少寫註解，權衡下先聚焦核心。
- A詳: 文件製作的目的是讓可重用的 API 有清楚說明。頁面與使用者控制項往往註解較少，且需付出高昂代價才能完整重現 ASP.NET 產物。文章因此採取務實策略：透過 csc 先穩定產出 App_Code 的 DLL 與 XML，將可重用類別納入文件；對於頁面類型暫時忽略，待有更便利工具再行補強。此決策在效益與成本間取得平衡。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q12, A-Q15, C-Q5

A-Q19: 為何 App_Code 多層目錄會導致 XML 檔覆蓋？
- A簡: ASP.NET 會對各目錄各編一次；固定 /doc 檔名導致重複輸出互相覆蓋或被清理。
- A詳: ASP.NET 的動態編譯邏輯是以目錄為編譯單位，App_Code 的子目錄會各自編譯並產出中繼檔。若在 web.config 設定 /doc 為某一檔名，則每次子目錄編譯都會生成（或清理）同一個檔案，造成覆蓋、刪除與混亂，最終難以保留穩定輸出。這說明了為何該方法在生產環境不可行，須改以單次整合編譯。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, A-Q10, B-Q1

A-Q20: 為什麼仍建議採用文件工具（如 Sandcastle/NDoc）？
- A簡: 它們將結構化註解轉為易讀文件，促進知識共享、維運與學習，長期價值高。
- A詳: 將程式碼中的註解轉為正式文件，能建立一致的 API 溝通語言，降低跨團隊溝通成本。NDoc、Sandcastle 能從 DLL 與 XML 自動化產出 CHM/網站，減少手工編寫維護文件的負擔，並讓即時文件與程式同步演進。即便在 Web Site 模型下要多做一步產生 DLL/XML，其帶來的知識沉澱與可維護性，對長期產品品質極具價值。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q2, C-Q5

### Q&A 類別 B: 技術原理類

B-Q1: ASP.NET 2.0 Web Site 的動態編譯機制如何運作？
- A簡: 以目錄為單位解析並編譯 App_Code 等檔案，子目錄分次編譯，於執行期載入使用。
- A詳: ASP.NET 啟動時監看網站目錄結構，對 App_Code 及相關資料夾進行分批編譯：每個目錄收集其中的 .cs 原始碼，解析特定檔（如 .wsdl/.xsd），並在臨時目錄產生中繼組件。各目錄編譯後，執行階段載入這些組件以提供網站功能。此「多編譯單元」策略提升彈性，也解釋了為何固定檔名的 /doc 會被覆蓋，與為何外部一次性編譯可避開此限制。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, A-Q10, B-Q9

B-Q2: <system.codedom> compilerOptions 參數背後機制是什麼？
- A簡: 它將額外參數傳遞給 CodeDom Provider（C# 編譯器），例如 /doc，用於產生 XML。
- A詳: system.codedom 節點可設定語言對應的編譯器（如 CSharpCodeProvider）與其 compilerOptions。ASP.NET 在動態編譯各目錄時，會將此設定注入到每次編譯呼叫，使底層 C# 編譯器套用對應旗標，如 /optimize、/warn、/doc。然而因為 Web Site 是分目錄多次編譯，固定的 /doc 檔案在流程中會多次生成與清理，導致覆蓋問題，反映了配置層與執行模型的交互限制。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q1, B-Q9

B-Q3: aspnet_compiler.exe 的流程為何？
- A簡: 掃描網站、解析頁面與程式碼、執行必要轉碼，輸出多個編譯後的組件。
- A詳: aspnet_compiler 會載入網站根目錄，解析 .aspx/.ascx 等標記檔，將其轉為對應的 partial 類別原始碼，再與 code-behind、App_Code 原始碼整合，按區段進行編譯，最後輸出多個 DLL 至目標資料夾。這條流程重現了執行期的動態編譯，但在部署時先行完成。其焦點在將網站完整轉換為可執行的組件集，並非文件生成，故不會主動輸出 XML 註解。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, A-Q8, A-Q17

B-Q4: Web Deployment Project 的技術架構如何設計？
- A簡: 以前置編譯輸出多 DLL，再以合併工具將其合成單一組件，簡化部署與參照。
- A詳: 該專案先驅動 aspnet_compiler 生成網站所需的多個 DLL，接著透過 Assembly Merge 工具（如 ILMerge 類型工具）將相關組件合併，減少部署時的檔案數量與相依複雜度。雖有利於形成單一 DLL 供其他系統參照，但整個管線的目的仍是部署最佳化，並未介入或保存 C# XML 註解輸出，因此在文件生成場景仍須另行補足 XML。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, A-Q17, C-Q3

B-Q5: C# 編譯器（csc.exe）相關參數的原理是什麼？
- A簡: /target 指出產物類型、/out 指定 DLL、/doc 匯出註解、/recurse 收集檔案。
- A詳: csc.exe 以命令列旗標驅動：/target:library 讓編譯器輸出類別庫 DLL；/out:xxx.dll 指定輸出檔名；/doc:xxx.xml 匯出 XML 註解；/recurse:dir\*.cs 會遞迴收集目錄內符合模式的檔案。一次性統合 App_Code 下的所有 .cs，讓文件生成的兩大輸入（DLL 與 XML）在單一步驟產出。此方式繞過 ASP.NET 的多階段編譯，避免覆蓋問題。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, A-Q12, C-Q4

B-Q6: 說明工具如何使用 Assembly 元資料與 XML 註解？
- A簡: 以反射解析型別/成員結構，將 XML 的節點對映至對應成員，生成可讀文件。
- A詳: 文件工具先以反射掃描 DLL，建立命名空間、型別、方法、屬性的結構樹，並以成員 ID（如 "M:Namespace.Type.Method"）作為索引；再載入 XML 註解檔，將 <member> 節點依 ID 對應到該結構樹的節點，合併出每個成員的說明、參數描述與回傳值資訊。最後套用樣板輸出 CHM 或 HTML。少了任一輸入，都會使對映或內容缺失。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q2, C-Q5, D-Q2

B-Q7: .aspx/.ascx 的 partial 類別是如何產生與合併的？
- A簡: 模板解析生成設計端 partial 類，與 code-behind partial 類在編譯時合併成完整類型。
- A詳: ASP.NET 在編譯頁面時，會讀取 .aspx/.ascx 標記，針對控制項樹與宣告生成對應的設計端 partial 類（包含欄位、初始化程式），再與開發者編寫的 code-behind partial 類於編譯階段合併，形成完整類別。此過程由 ASP.NET 掌控，外部以 csc.exe 直接編譯 code-behind 將因缺少另一半 partial 而失敗或不完整，亦無法取得相應文件。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, D-Q3, C-Q8

B-Q8: .wsdl/.xsd 在 Web Site 中的自動化生成扮演什麼角色？
- A簡: 觸發工具自動產生代理類與 Typed DataSet 原始碼，納入 ASP.NET 的編譯流程。
- A詳: 放置於 App_Code 的 .wsdl 檔會驅動服務代理類的生成，.xsd 會生成強型別資料集相關類別。這些生成步驟整合在 ASP.NET 的動態編譯中，輸出暫存原始碼再合併編譯。若跳離該流程改用 csc.exe，除非事先以對應工具轉出 .cs，否則最終 DLL/XML 不會包含這些由模板/描述檔衍生的 API，影響文件完整性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, C-Q8, D-Q4

B-Q9: 為何固定檔名的 XML 在 Web Site 編譯過程易被覆蓋或清理？
- A簡: 多目錄、多階段編譯各自嘗試寫入同一路徑，造成覆蓋；中間產物清理亦會刪除。
- A詳: 每個編譯單元（子目錄）都套用相同的 compilerOptions，當 /doc 指向同一檔時，先後編譯單元會輪流輸出，後者覆蓋前者。某些階段 ASP.NET 會清理中繼輸出以維持一致，也會刪除前一輪產物。結果即便一度產生了 XML，流程結束時也未必保留。因此在 Web Site 模型中，web.config 的 /doc 較難得到穩定結果。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, A-Q19, D-Q1

B-Q10: 為何 Sandcastle 生成文件較 NDoc 緩慢（高層原因）？
- A簡: 為支援新特性與更完整的處理管線，Sandcastle 的解析與轉換步驟較繁重。
- A詳: 相較 NDoc，Sandcastle 為支援 .NET 2.0 之後的語言特性（如泛型）與更彈性的輸出樣板，採用較完整的處理管線（多階段反射、轉換、組裝與樣板套用）。文章觀察同專案生成 CHM，NDoc 約 20 分鐘，Sandcastle 約 60 分鐘。雖然細節取決於專案規模與設定，但整體趨勢是功能更豐富、代價是計算耗時更長。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q3, C-Q10, D-Q5

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何在 web.config 設定 compilerOptions 產生 XML 文件？
- A簡: 在 <system.codedom> 為 C# 編譯器加入 /doc 路徑；但多層目錄易覆蓋，僅適合簡單站台。
- A詳: 
  - 具體步驟
    - 在 web.config 加入：
      - <system.codedom><compilers><compiler ... compilerOptions="/doc:c:\sample.xml" /></compilers></system.codedom>
    - 重新編譯/啟動網站觀察輸出。
  - 範例設定
    - compilerOptions="/doc:c:\site\App_Code.xml"
  - 注意事項與最佳實踐
    - 僅適用 App_Code 單層且檔案少的情境；
    - 在生產環境常被多階段編譯覆蓋/清理；
    - 不支援萬用字元自動分檔；建議改用 csc.exe。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, B-Q2, D-Q1

C-Q2: 如何使用 aspnet_compiler.exe 輸出網站 DLL？
- A簡: 以 aspnet_compiler 指向網站路徑與目標資料夾，預先編譯輸出多個組件供部署。
- A詳:
  - 具體實作步驟
    - 開啟命令列，執行：
      - aspnet_compiler -p "C:\src\Site" -v / "C:\out\Precompiled"
  - 關鍵參數
    - -p：實體路徑；-v：虛擬根；目標資料夾為輸出。
  - 注意事項與最佳實踐
    - 該工具不會輸出 XML 註解；
    - 可搭配 Web Deployment Project 合併多 DLL；
    - 權限與目錄存在性需事先確認。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q3, A-Q17

C-Q3: 如何建立 Web Deployment Project 產生單一 DLL？
- A簡: 在 VS 建立部署專案，先預編譯，再用合併工具將多個組件併為單一 DLL。
- A詳:
  - 具體實作步驟
    - 在 VS 安裝/啟用 Web Deployment Project；
    - 對 Web Site 新增部署專案；
    - 設定「預先編譯」與「合併成單一組件」；
    - 建置專案得到單一 DLL。
  - 重要設定
    - 合併策略（強名稱、版本）；
    - 輸出路徑。
  - 注意事項與最佳實踐
    - 不會自動產出 XML，需要另以 csc 或其他方式補齊；
    - 驗證合併後的型別可見性與相依性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q4, A-Q17

C-Q4: 如何用 csc.exe 為 App_Code 產生 DLL 與 XML？
- A簡: 使用 /target:library、/out、/doc、/recurse 將 App_Code\*.cs 一次編譯輸出 DLL 與 XML。
- A詳:
  - 具體實作步驟
    - 於網站根目錄執行：
      - csc.exe /out:App_Code.dll /doc:App_Code.xml /target:library /recurse:App_Code\*.cs
  - 關鍵指令碼
    - /recurse 遞迴抓取所有 .cs；
    - /doc 匯出 XML 註解；
    - /target:library 生成類別庫 DLL。
  - 注意事項與最佳實踐
    - 不會處理 .aspx/.ascx、.wsdl/.xsd 的動態產物；
    - 輸出路徑請使用可寫目錄；
    - 納入 CI 前，先在本機確保可重現。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q9, A-Q12, D-Q3

C-Q5: 如何將 DLL + XML 交給 NDoc/Sandcastle 生成 CHM？
- A簡: 準備組件與 XML，依工具建立專案或命令列，選擇輸出格式後生成文件。
- A詳:
  - 具體實作步驟
    - 準備 App_Code.dll 與 App_Code.xml；
    - 以 NDoc/Sandcastle 指定輸入檔與輸出格式（CHM/HTML）；
    - 執行生成流程。
  - 關鍵設定
    - 輸入組件清單與對應 XML；
    - 命名空間過濾、可見性設定。
  - 注意事項與最佳實踐
    - 確保 DLL 與 XML 版本一致；
    - Sandcastle 生成較慢，可先針對核心命名空間試跑；
    - 檢查警告以找出缺漏註解。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q2, A-Q3, B-Q6

C-Q6: 如何寫批次檔封裝 csc 編譯 App_Code？
- A簡: 建立 .bat 收集路徑與輸出，呼叫 csc；加入存在性檢查與錯誤處理。
- A詳:
  - 具體實作步驟
    - 建立 build-docs.bat：
      - ```
        @echo off
        set SRC=%~dp0
        set OUT=%SRC%docs
        if not exist "%OUT%" mkdir "%OUT%"
        csc /target:library /recurse:%SRC%App_Code\*.cs ^
            /out:%OUT%\App_Code.dll /doc:%OUT%\App_Code.xml || exit /b 1
        ```
  - 關鍵程式碼片段
    - 使用環境變數與目錄檢查；
    - 以 || exit /b 1 作為錯誤處理。
  - 注意事項與最佳實踐
    - 避免相對路徑錯誤；
    - 清理舊輸出避免混淆；
    - 於 CI 前先本機驗證。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q4, D-Q2, D-Q3

C-Q7: 如何在 CI 流程整合文件生成？
- A簡: 在建置管線加入步驟：csc 產 DLL/XML、呼叫文件工具、保存產出與工件。
- A詳:
  - 具體實作步驟
    - 階段 1：還原/建置網站；
    - 階段 2：執行批次檔（csc 產生 DLL/XML）；
    - 階段 3：呼叫 NDoc/Sandcastle 生成文件；
    - 階段 4：上傳工件（CHM/HTML）至檔案庫。
  - 關鍵設定
    - 代理程式帳戶要有寫入權限；
    - 記錄生成時間與警告。
  - 注意事項與最佳實踐
    - 控制頻率（如夜間建置）以節省 Sandcastle 時間；
    - 僅針對核心命名空間生成以加速迭代。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q6, A-Q3, D-Q5

C-Q8: 面對 .wsdl/.xsd 與 .aspx/.ascx 無法由 csc 處理，怎麼辦？
- A簡: 事前轉出 .cs（wsdl/xsd），或暫時排除頁面層，聚焦可重用類庫的文件。
- A詳:
  - 具體實作步驟
    - 以相對工具（如 wsdl.exe/xsd.exe）將描述檔轉為 .cs；
    - 調整 csc /recurse 篩選或以 include 清單納入；
    - 對 .aspx/.ascx 頁面層暫不納入文件。
  - 關鍵設定
    - 管理產生 .cs 的輸出與命名空間；
    - 避免重複型別衝突。
  - 注意事項與最佳實踐
    - 明確界定文件範圍；
    - 後續再引入能處理頁面產物的工具或流程。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q14, A-Q15, D-Q4

C-Q9: App_Code 有多個子目錄時，如何分拆或合併輸出？
- A簡: 可分別以 csc 對子目錄輸出，再以合併工具併成單一 DLL；或一次性 /recurse 全抓。
- A詳:
  - 具體實作步驟
    - 方案一：一次性
      - csc /recurse:App_Code\*.cs /out:App_Code.dll /doc:App_Code.xml
    - 方案二：分段
      - 針對每個子目錄各自輸出 DLL/XML，再以合併工具整合。
  - 關鍵選擇
    - 一次性簡單但需處理相依順序；
    - 分段較清晰但步驟增多。
  - 注意事項與最佳實踐
    - 保持命名一致與版本同步；
    - 避免重複型別導致合併衝突。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q5, D-Q8

C-Q10: 如何評估與優化 Sandcastle 的生成時間？
- A簡: 控制輸入範圍、過濾命名空間、降低輸出樣板負擔，必要時降低頻率。
- A詳:
  - 具體實作步驟
    - 分析目前輸入 DLL/命名空間；
    - 設定過濾器只生成核心 API；
    - 調整輸出選項（僅生成必需格式）。
  - 關鍵調整
    - 降低輸出規模可顯著縮短時間；
    - 規劃夜間批次生成。
  - 注意事項與最佳實踐
    - 先以小範圍試跑驗證；
    - 比對 NDoc 與 Sandcastle 的時間差異，選擇合適工具。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q3, B-Q10, D-Q5

### Q&A 類別 D: 問題解決類（10題）

D-Q1: 在 web.config 設定 /doc 後，XML 檔被覆蓋或消失，怎麼辦？
- A簡: 因多目錄編譯互相覆蓋，改用 csc 一次性編譯輸出 DLL/XML，避免覆蓋問題。
- A詳:
  - 問題症狀
    - 看到 XML 短暫出現後消失；或最終只留最後一輪編譯的內容。
  - 可能原因
    - App_Code 以目錄為單位重複編譯，固定檔名互相覆蓋；清理步驟刪除中繼產物。
  - 解決步驟
    - 移除 web.config 的 /doc；
    - 以 csc /recurse 一次性輸出 DLL 與 XML。
  - 預防措施
    - 避免在複雜站台用 compilerOptions 產 XML；
    - 將外部編譯納入批次或 CI。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q9, C-Q4

D-Q2: 文件工具提示找不到 XML 或 Assembly，如何排查？
- A簡: 檢查路徑與版本一致性，確保 DLL/XML 同步生成且在可讀位置。
- A詳:
  - 問題症狀
    - NDoc/Sandcastle 報錯缺少 XML、無法載入 DLL、成員對應不到。
  - 可能原因
    - 輸入路徑錯誤；DLL/XML 版本不一致；權限不足。
  - 解決步驟
    - 確認 DLL/XML 實際存在且時間戳一致；
    - 修正工具輸入清單與路徑；
    - 以管理者權限或授予讀權。
  - 預防措施
    - 建置腳本固定輸出目錄；
    - 自動化檢查輸入完整性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, C-Q5, C-Q6

D-Q3: 用 csc 編譯時出現 partial 類別缺失或找不到成員怎麼辦？
- A簡: 這多源於 .aspx/.ascx 缺少設計端 partial，將頁面層排除改只編 App_Code。
- A詳:
  - 問題症狀
    - 編譯錯誤顯示無法找到欄位/方法；partial 定義不完整。
  - 可能原因
    - 缺少由 ASP.NET 解析模板產生的 partial 類別檔。
  - 解決步驟
    - /recurse 限定為 App_Code\*.cs；
    - 排除頁面 code-behind；
    - 僅針對可重用類別生成文件。
  - 預防措施
    - 明確規範文件範圍；
    - 不將頁面層納入外部 csc 編譯。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, B-Q7, C-Q8

D-Q4: App_Code 中的 .wsdl/.xsd 導致類別缺漏，如何補救？
- A簡: 先用相應工具將 .wsdl/.xsd 轉為 .cs，再納入 csc 編譯；或接受文件範圍縮小。
- A詳:
  - 問題症狀
    - 文件中缺少服務代理或 Typed DataSet API。
  - 可能原因
    - csc 未觸發自動生成步驟，未納入相關 .cs。
  - 解決步驟
    - 預先執行 wsdl.exe/xsd.exe 產生 .cs；
    - 將生成檔加入 /recurse 範圍；
    - 重新編譯輸出。
  - 預防措施
    - 將轉碼加入建置腳本；
    - 管理命名空間避免衝突。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q8, C-Q8

D-Q5: Sandcastle 生成速度很慢，該怎麼處理？
- A簡: 限縮輸入範圍、夜間批次執行、優先 NDoc 試跑，再切回 Sandcastle 完整生成。
- A詳:
  - 啪題症狀
    - 同規模專案，Sandcastle 生成時間顯著高於 NDoc（如 60 分 vs 20 分）。
  - 可能原因
    - 處理管線較重、支援新特性導致耗時。
  - 解決步驟
    - 僅選擇核心命名空間輸出；
    - 調整生成頻率（夜間/週期性）；
    - 初期以 NDoc 快速迭代驗證結構。
  - 預防措施
    - 在專案成長期控制 API 表面積；
    - 將生成步驟隔離到非尖峰時段。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q3, B-Q10, C-Q10

D-Q6: 生成的 CHM 沒內容或目錄空白，怎麼診斷？
- A簡: 多半是 XML 對映不到 DLL 成員或檔案缺失，檢查成員 ID 與輸入一致性。
- A詳:
  - 問題症狀
    - CHM 成功產生但導航空白或頁面無說明。
  - 可能原因
    - DLL 與 XML 不匹配；XML 結構錯誤；命名空間被過濾掉。
  - 解決步驟
    - 檢查 XML <member> 節點與 DLL 成員是否一致；
    - 檢視工具過濾設定；
    - 重新以一致版本輸出 DLL/XML。
  - 預防措施
    - 建置流程一次性產出兩者；
    - 對輸入檔名與版本加上校驗。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q5, C-Q6

D-Q7: 生產環境用 web.config 產生 XML 出現權限問題怎麼辦？
- A簡: 改用可寫路徑或避免在生產站上輸出，改以外部建置機產出。
- A詳:
  - 問題症狀
    - 例外顯示無法寫入 XML 檔案。
  - 可能原因
    - 目標路徑無寫權；App Pool 帳戶權限不足。
  - 解決步驟
    - 設定輸出到具寫入權目錄；
    - 或改以 csc 在建置機產出；
    - 將 XML 連同部署工件一併發佈。
  - 預防措施
    - 將文件生成移出生產站；
    - 權限最小化原則避免不必要風險。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q1, C-Q6, C-Q7

D-Q8: 多個 DLL 合併後發生型別命名衝突，怎麼處理？
- A簡: 檢查命名空間與可見性，調整合併順序或排除重複型別來源。
- A詳:
  - 問題症狀
    - 合併或文件生成時報重複型別、相同成員衝突。
  - 可能原因
    - 分段編譯或自動生成造成重複定義。
  - 解決步驟
    - 以一次性 /recurse 降低重複；
    - 合併前清理重複來源；
    - 規整命名空間。
  - 預防措施
    - 建立清楚的輸入清單；
    - 於 CI 加入檢查規則。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q9, B-Q5, C-Q3

D-Q9: Web Site 缺少 .csproj，文件工具要求專案檔時如何應對？
- A簡: 文件工具以 DLL+XML 為主，不必依賴 .csproj；先用 csc 或部署專案產生 DLL。
- A詳:
  - 問題症狀
    - 工具介面偏向載入專案檔，Web Site 無 .csproj。
  - 可能原因
    - 工具預設情境為 Web Application/類庫。
  - 解決步驟
    - 以 csc 或 Web Deployment 先產出 DLL；
    - 在工具中改用「以組件為輸入」模式；
    - 指派對應 XML。
  - 預防措施
    - 將文件生成流程標準化為「DLL+XML」模式；
    - 不依賴專案檔。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q4, A-Q8, C-Q5

D-Q10: 目標 .NET 版本不一致導致生成失敗，怎麼辦？
- A簡: 確保 csc 與文件工具使用的框架版本一致，避免 API 解析錯誤。
- A詳:
  - 問題症狀
    - 生成報反射錯誤、找不到參考組件。
  - 可能原因
    - 編譯與文件工具使用不同版本框架/參考。
  - 解決步驟
    - 指定對應版本的 csc 與參考路徑；
    - 在文件工具設定目標框架；
    - 重新生成。
  - 預防措施
    - 固定建置環境的 SDK 路徑；
    - 版本一致性檢查納入管線。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q6, C-Q7, C-Q5

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 XML 文件註解（comment help）？
    - A-Q2: 為什麼產生說明文件需要同時提供 Assembly 與 XML 文件？
    - A-Q3: 什麼是 Sandcastle？與 NDoc 有何不同？
    - A-Q4: 什麼是 ASP.NET 2.0 的 Web Site 專案型別？
    - A-Q5: Web Site 與 Web Application 的差異是什麼？
    - A-Q6: App_Code 目錄的角色是什麼？
    - A-Q7: 什麼是 aspnet_compiler.exe？
    - A-Q8: 什麼是 Web Deployment Project？
    - A-Q9: 什麼是 C# 編譯器 csc.exe？
    - B-Q5: C# 編譯器（csc.exe）相關參數的原理是什麼？
    - B-Q6: 說明工具如何使用 Assembly 元資料與 XML 註解？
    - C-Q2: 如何使用 aspnet_compiler.exe 輸出網站 DLL？
    - C-Q4: 如何用 csc.exe 為 App_Code 產生 DLL 與 XML？
    - C-Q5: 如何將 DLL + XML 交給 NDoc/Sandcastle 生成 CHM？
    - D-Q2: 文件工具提示找不到 XML 或 Assembly，如何排查？

- 中級者：建議學習哪 20 題
    - A-Q10: 為何在 web.config 設定 compilerOptions 產生 XML 會失敗？
    - A-Q11: 為什麼 /doc 參數不能使用萬用字元造成限制？
    - A-Q12: 以 csc.exe 手動產出 DLL 與 XML 的策略是什麼？
    - A-Q13: 為什麼手動 csc 編譯仍有覆蓋範圍限制？
    - A-Q14: App_Code 中的 .wsdl/.xsd 會如何影響文件產生？
    - A-Q15: 為什麼 .aspx/.ascx 的 code-behind 不能直接用 csc 編入？
    - A-Q17: 使用 Web Deployment Project 為何仍無法得到 XML 文件？
    - A-Q19: 為何 App_Code 多層目錄會導致 XML 檔覆蓋？
    - B-Q1: ASP.NET 2.0 Web Site 的動態編譯機制如何運作？
    - B-Q2: <system.codedom> compilerOptions 參數背後機制是什麼？
    - B-Q3: aspnet_compiler.exe 的流程為何？
    - B-Q4: Web Deployment Project 的技術架構如何設計？
    - B-Q7: .aspx/.ascx 的 partial 類別是如何產生與合併的？
    - B-Q8: .wsdl/.xsd 在 Web Site 中的自動化生成扮演什麼角色？
    - B-Q9: 為何固定檔名的 XML 在 Web Site 編譯過程易被覆蓋或清理？
    - C-Q1: 如何在 web.config 設定 compilerOptions 產生 XML 文件？
    - C-Q6: 如何寫批次檔封裝 csc 編譯 App_Code？
    - C-Q7: 如何在 CI 流程整合文件生成？
    - D-Q1: 在 web.config 設定 /doc 後，XML 檔被覆蓋或消失，怎麼辦？
    - D-Q3: 用 csc 編譯時出現 partial 類別缺失或找不到成員怎麼辦？

- 高級者：建議關注哪 15 題
    - A-Q16: 若完整重現 ASP.NET 編譯步驟是否可行？代價是什麼？
    - A-Q18: 為什麼最終選擇忽略部分（如 .ascx）文件產出？
    - B-Q10: 為何 Sandcastle 生成文件較 NDoc 緩慢（高層原因）？
    - C-Q8: 面對 .wsdl/.xsd 與 .aspx/.ascx 無法由 csc 處理，怎麼辦？
    - C-Q9: App_Code 有多個子目錄時，如何分拆或合併輸出？
    - C-Q10: 如何評估與優化 Sandcastle 的生成時間？
    - D-Q4: App_Code 中的 .wsdl/.xsd 導致類別缺漏，如何補救？
    - D-Q5: Sandcastle 生成速度很慢，該怎麼處理？
    - D-Q6: 生成的 CHM 沒內容或目錄空白，怎麼診斷？
    - D-Q7: 生產環境用 web.config 產生 XML 出現權限問題怎麼辦？
    - D-Q8: 多個 DLL 合併後發生型別命名衝突，怎麼處理？
    - D-Q9: Web Site 缺少 .csproj，文件工具要求專案檔時如何應對？
    - D-Q10: 目標 .NET 版本不一致導致生成失敗，怎麼辦？
    - A-Q20: 為什麼仍建議採用文件工具（如 Sandcastle/NDoc）？
    - A-Q3: 什麼是 Sandcastle？與 NDoc 有何不同？