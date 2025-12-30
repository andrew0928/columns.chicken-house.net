---
layout: synthesis
title: "莫明奇妙的錯誤訊息: 找不到 VJSharpCodeProvider ?"
synthesis_type: faq
source_post: /2008/09/10/mysterious-error-message-vjsharpcodeprovider-not-found/
redirect_from:
  - /2008/09/10/mysterious-error-message-vjsharpcodeprovider-not-found/faq/
---

# 莫明奇妙的錯誤訊息: 找不到 VJSharpCodeProvider ?

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 CodeDOM Provider？
- A簡: CodeDOM Provider 是 .NET 的語言編譯器介面，用來依副檔名/語言將原始碼轉為組件。
- A詳: CodeDOM Provider 是 .NET 的編譯抽象層，提供統一 API 讓工具根據語言（如 C#、VB、J#）將程式碼動態編譯為組件。Visual Studio 與 ASP.NET 會透過它辨識檔案副檔名或語言名稱，載入相對應編譯器。常見 Provider 包含 CSharpCodeProvider、VBCodeProvider；VJSharpCodeProvider 對應 J#。此機制廣泛用於 Web Site 預編譯、動態編譯與設計階段工具。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, B-Q3, D-Q1

A-Q2: 什麼是 Visual J# 與 VJSharpCodeProvider？
- A簡: Visual J# 是 .NET 舊語言，VJSharpCodeProvider 是其對應的 CodeDOM 編譯器。
- A詳: Visual J# 是微軟曾提供的 .NET 語言，語法類似 Java，但已淘汰。VJSharpCodeProvider 則是用於編譯 .java/.jsharp 檔的 CodeDOM 實作。在 VS 建置網站時，若偵測到 .java 檔，系統會嘗試載入 VJSharpCodeProvider。若該提供者在環境中不存在，就會拋出「could not be located」錯誤。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, B-Q9, D-Q5

A-Q3: 什麼是 ASP.NET 的 App_Data 資料夾？
- A簡: App_Data 用於存放資料文件，執行時不提供服務，不應放原始碼。
- A詳: App_Data 是 ASP.NET 特殊資料夾，設計用於存放資料檔（如 XML、MDF、SQLite、JSON）。在執行階段，IIS 不會直接回應此資料夾的檔案內容。雖然設計上不會參與動態編譯，但在 Visual Studio 的 Web Site 建置過程，仍可能被掃描到特定檔案類型，導致建置行為受影響。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, B-Q6, D-Q4

A-Q4: ASP.NET Web Site 與 Web Application 有何差異？
- A簡: Web Site 動態/整體編譯；Web Application 預先編譯、檔案級控制。
- A詳: Web Site 模型以資料夾為專案，建置時掃描整體樹狀結構；執行時可動態編譯。Web Application 是專案檔驅動，採 MSBuild 與預先編譯，對檔案的 Build Action、包含/排除控制更精確。錯誤定位、參考管理與 CI 整合通常 Web Application 較友善。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, C-Q5, D-Q3

A-Q5: 為何 App_Data 也可能影響建置？
- A簡: Web Site 模型建置會掃描整站檔案，特殊類型或提供者映射會被觸發。
- A詳: 即使 App_Data 在執行期不參與動態編譯，Visual Studio 的 Build Website 仍會掃描網站樹。若掃描到具「已知編譯器支援」的副檔名（如 .java），VS 會嘗試載入對應 CodeDOM Provider。若該 Provider 缺失，即報錯，導致整體建置失敗，進而影響偵錯流程。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q6, D-Q4

A-Q6: 什麼是 ASP.NET 的動態編譯與預先編譯？
- A簡: 動態編譯執行時產生組件；預先編譯於建置或部署前完成。
- A詳: 動態編譯由 ASP.NET 在第一次請求時編譯頁面與 App_Code；預先編譯則透過 VS/aspnet_compiler 先產生組件，縮短首請求延遲並提早發現錯誤。Web Site 支援兩種模式；Web Application 以預先編譯為主。錯誤可在不同階段被發現，影響偵錯與部署策略。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q12, D-Q3

A-Q7: 為什麼會出現「CodeDom provider type ... could not be located」？
- A簡: 環境中缺少對應編譯器組件，卻偵測到需該編譯器之檔案。
- A詳: 當 VS 或 ASP.NET 建置/預編譯過程中，根據檔案副檔名或語言名稱解析到某 CodeDOM Provider，但在本機 .NET/GAC 無相應組件可載入，就會拋出此錯誤。常見情境為專案中含 .java，但環境未安裝 Visual J#。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, B-Q5, D-Q1

A-Q8: 該錯誤為何常沒有檔名與行號？
- A簡: 屬全域建置階段錯誤，非來源檔語法錯誤，故無行號。
- A詳: 此類錯誤發生在載入編譯器、建立編譯管線前的全域階段，屬「環境/配置」問題，而非某一檔案的語法錯誤。因未進入語法剖析階段，自然無法產生檔名與行號，僅能提示 Provider 載入失敗。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, D-Q2, D-Q1

A-Q9: VS 為何會對 .java 檔使用 J# Provider？
- A簡: 依副檔名與 Provider 映射，.java 對應 VJSharpCodeProvider。
- A詳: VS 透過 CodeDOM Provider 提供的已定義副檔名與語言映射表，識別 .java 這類檔案屬 J#。當建置掃描到此副檔名，就會嘗試載入 VJSharpCodeProvider。若該 Provider 不存在，則拋出載入失敗錯誤。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q4, D-Q5

A-Q10: 為什麼網站可以執行，卻無法 F5 偵錯？
- A簡: 執行可靠動態編譯，但 F5 需先建置，建置失敗即中斷。
- A詳: Web Site 在執行時可跳過完整預編譯，由 ASP.NET 按需動態編譯可運作；但 F5 本地偵錯流程會先建置網站，以便設定中斷點與符號。若建置因 Provider 載入失敗而中止，就無法進入 F5 偵錯。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q6, D-Q3, C-Q6

A-Q11: 何謂 system.codedom/compilers？
- A簡: 設定可用的 CodeDOM Provider 清單與對應語言/副檔名。
- A詳: 在 machine.config 或 web.config 的 system.codedom/compilers 區段，可宣告可用的 Provider 類型、版本、PublicKeyToken、支援語言與副檔名。VS 會參考此清單決定如何載入各語言編譯器。可藉由覆寫該清單限制或擴充可用 Provider。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q10, C-Q3, D-Q1

A-Q12: Machine.config 與 Web.config 在編譯上有何關係？
- A簡: Web.config 可覆寫 machine.config 的預設 Provider 與編譯行為。
- A詳: machine.config 定義全機器預設的編譯器與 ASP.NET 行為；Web.config 可在應用程式層級覆寫，如調整 system.codedom/compilers、compilation 屬性。適當覆寫可避免載入不需要的 Provider，或強制使用特定語言版本。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q11, C-Q3, D-Q7

A-Q13: GAC 與 Provider 載入失敗有何關聯？
- A簡: Provider 組件常註冊於 GAC，缺失即無法解析載入。
- A詳: 多數 CodeDOM Provider（如 VJSharpCodeProvider）以強式名稱安裝至 GAC。建置時 CLR 依組件識別（名稱、版本、PublicKeyToken）從 GAC 解析。若未安裝或版本不符，將導致載入失敗並拋出「could not be located」訊息。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q17, D-Q1, D-Q7

A-Q14: 為何安裝或未安裝 Visual J# 會影響建置？
- A簡: 是否安裝決定 J# Provider 是否存在，影響含 .java 的建置。
- A詳: 有無 Visual J# 會影響 VJSharpCodeProvider 是否可用。一旦專案中含有 .java，Build Website 會嘗試載入該 Provider。若環境未安裝，建置失敗；若已安裝，建置可通過，但多數情境其實不需 J#，更安全作法是移除或排除 .java。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, B-Q22, D-Q5

A-Q15: 為什麼不建議將原始碼放進 App_Data？
- A簡: 容易觸發非預期建置掃描，導致 Provider 載入錯誤。
- A詳: App_Data 並非為原始碼設計；放入 .java、.cs、.vb 等檔，雖執行期不提供服務，但設計期建置掃描仍可能辨識到並觸發對應 Provider。最佳實務是將資料與程式碼分離，或在 Web Application 以 Build Action 控制。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q2, D-Q4, A-Q3

A-Q16: BlogEngine.NET 擴充元件（extension）是什麼？
- A簡: BlogEngine 的可插拔功能模組，通常以 .cs 檔實作。
- A詳: BlogEngine.NET extension 是事件導向的功能擴充點，可在文章發表、瀏覽計數等事件中執行自訂邏輯。通常以 C# 源碼放於 App_Code 或專案中，由 ASP.NET 編譯參與。與本文錯誤關聯是建置過程受不相關 .java 檔干擾。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q7, D-Q9, A-Q4

A-Q17: App_Code 與 App_Data 差異是什麼？
- A簡: App_Code 供編譯共享程式碼；App_Data 存資料檔，不編譯。
- A詳: App_Code 是 ASP.NET 特殊資料夾，放置 C#/VB 等程式碼並於執行期或預編譯時被編譯；App_Data 用於資料檔並且不參與執行期服務。混用兩者用途容易引發建置與部署問題。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, B-Q6, D-Q4

A-Q18: 為什麼錯誤訊息「(0): Build (web)」很難追蹤？
- A簡: 表示建置階段早期失敗，缺乏具體來源檔上下文。
- A詳: 「(0): Build (web)」代表 VS 的網站建置器在建立編譯管線前就失敗，通常是 Provider 載入或配置問題。缺乏來源檔上下文會使問題定位困難，需從全域設定與檔案掃描切入排查。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: D-Q2, B-Q5, C-Q1

A-Q19: 為何 Attach Process 可行但不便？
- A簡: 可繞過建置失敗入侵程式，但設定符號與中斷較繁瑣。
- A詳: Attach to Process 可直接連接到 w3wp/IIS Express 來偵錯執行中網站，繞過建置前置需求。然而中斷點、PDB 符號管理、啟動流程控制較不便，對迭代開發效率影響較大，應優先修復建置問題。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q6, D-Q3, A-Q10

A-Q20: Build Provider 與 CodeDOM 有何關係？
- A簡: Build Provider 對應檔案類型，內部可使用 CodeDOM 編譯。
- A詳: Build Provider 是 ASP.NET 對特定副檔名（如 .aspx, .ascx）的建置處理器；當需要產生程式碼或組件時會呼叫 CodeDOM Provider 進行編譯。兩者共同構成網站建置與預編譯的處理鏈，影響錯誤產生位置與訊息。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q21, B-Q4, A-Q11

A-Q21: 為什麼應避免在網站根目錄混放非 Web 檔案？
- A簡: 可能被建置掃描、部署同步或安全規則誤處理。
- A詳: 網站根目錄常有建置、部署與安全規則，放置非 Web 檔（原始碼、工具、備份）可能被掃描或發佈，導致錯誤、洩漏或包體膨脹。建議將此類檔案置於解決方案外或專用資料夾並排除。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q8, D-Q6, A-Q15

A-Q22: 這個案例的根因和結論是什麼？
- A簡: App_Data 下的 .java 觸發 J# 編譯器載入；移除後建置即通過。
- A詳: 專案中意外包含舊 .java 程式碼於 App_Data；VS 建置掃描判定需 J# Provider，因環境未安裝而失敗。移除（或排除）該檔後建置恢復。結論：App_Data 不宜放原始碼，網站根目錄須嚴格控管檔案類型。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: D-Q1, C-Q2, A-Q5

### Q&A 類別 B: 技術原理類

B-Q1: ASP.NET 網站的整體編譯流程如何運作？
- A簡: 掃描檔案、建立建置圖、呼叫 Build Provider 與 CodeDOM 編譯。
- A詳: 原理說明：ASP.NET/VS 會掃描網站目錄，建立建置圖，識別頁面與程式碼檔，交由對應 Build Provider 產出程式碼，最後透過 CodeDOM Provider 編譯為組件。關鍵步驟或流程：1) 掃描與分類檔案；2) 載入建置/編譯器；3) 編譯與連結；4) 產生輸出與錯誤。核心組件介紹：Build Manager、Build Provider、CodeDOM Provider、aspnet_compiler。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q2, B-Q4

B-Q2: Visual Studio 的 Build Website 執行流程為何？
- A簡: VS 呼叫 ASP.NET 預編譯，掃描整站，交由對應處理器與編譯器。
- A詳: 技術原理說明：VS 以 aspnet_compiler 類似行為預編譯網站，並建立臨時 AppDomain。關鍵步驟：1) 收集專案檔案（含 App_Data）；2) 依副檔名選擇 Build Provider；3) 透過 system.codedom 解析編譯器；4) 產生組件與符號。核心組件：VS Web Build Manager、System.Web.Compilation、CodeDOM Providers。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, A-Q5, D-Q2

B-Q3: 系統如何解析副檔名對應的編譯器？
- A簡: 由 Provider 宣告支援副檔名，VS 依此映射載入對應編譯器。
- A詳: 技術原理說明：CodeDOM Provider 透過 IsDefinedExtension/IsDefinedLanguage 宣告支援類型；machine/web.config compilers 節點也可定義語言與副檔名。關鍵步驟：1) 掃描檔案副檔名；2) 查映射表；3) 載入 Provider 類型。核心組件：system.codedom/compilers、CodeDomProvider 靜態方法。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q9, A-Q11, B-Q4

B-Q4: CodeDOM Provider 的機制是什麼？
- A簡: 以抽象 API 生成編譯單元並呼叫底層編譯器輸出組件。
- A詳: 技術原理說明：Provider 封裝語法與編譯器調用，將 CodeCompileUnit 或原始碼轉為組件。關鍵步驟：1) 建立編譯參數；2) 設定引用/符號；3) 調用 CompileAssemblyFromSource/File。核心組件：CSharpCodeProvider、VBCodeProvider、VJSharpCodeProvider 等。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q1, B-Q1, B-Q5

B-Q5: 當找不到 Provider 會發生什麼？
- A簡: 載入對應類型失敗，丟出全域建置錯誤，無檔名行號。
- A詳: 技術原理說明：VS 解析到 Provider 類型字串，透過反射與組件解析載入；若 GAC/路徑無此組件，拋出 TypeLoad/Configuration 錯誤。關鍵步驟：1) 讀 compilers 節點；2) 嘗試 Assembly.Load；3) 失敗報錯。核心組件：Assembly Loader、machine.config、fusion log。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q8, A-Q13, D-Q1

B-Q6: App_Data 設計時與執行時的處理差異？
- A簡: 執行時不服務，但設計時建置掃描仍可能檢視其內容。
- A詳: 原理說明：ASP.NET 執行期跳過 App_Data 的直接提供；但 VS 的建置掃描基於專案檔案觀（Web Site），不嚴格等同執行期規則。關鍵步驟：1) VS 收集檔案；2) 模式化掃描副檔名；3) 觸發 Provider。核心組件：VS Web Project System、掃描器。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, A-Q5, D-Q4

B-Q7: 為何錯誤沒有行號—全域錯誤來源？
- A簡: 發生在載入組件前的配置階段，尚未分析任何來源檔。
- A詳: 原理說明：在編譯器與 Build Provider 載入前，系統先讀取設定解析 Provider；此時尚未進入語法剖析。關鍵步驟：1) 解析設定；2) 載入 Provider；3) 失敗即中止。核心組件：ConfigurationManager、Assembly Loader。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, D-Q2, B-Q5

B-Q8: 如何從錯誤訊息反推問題範圍？
- A簡: 由 Provider 名稱回推檔案副檔名與掃描範圍找可疑檔。
- A詳: 原理說明：錯誤含 Provider 類型（如 VJSharp），推知需對應副檔名（.java）。關鍵步驟：1) 全站搜尋該副檔名；2) 檢查 App_Data/隱藏資料夾；3) 檢視 compilers 映射。核心組件：Solution Search、web.config、machine.config。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q1, D-Q1, D-Q2

B-Q9: .java 檔如何觸發 VJ# Provider 載入？
- A簡: VS 依已知映射認定 .java 需 J#，嘗試載入 VJSharpCodeProvider。
- A詳: 原理說明：VS 專案系統或 Provider 自述支援 .java，掃描到後註冊到編譯清單。關鍵步驟：1) 掃描檔案系統；2) 比對映射表；3) 呼叫 Provider 載入。核心組件：VJSharpCodeProvider 的 extension 宣告、VS 專案系統。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q9, A-Q2, D-Q5

B-Q10: web.config 的 system.codedom 如何影響 Provider 列表？
- A簡: 可覆寫機器預設，只註冊需要的 Provider 降低風險。
- A詳: 原理說明：web.config compilers 節點若出現，會覆寫 machine.config 預設清單。關鍵步驟：1) 在 web.config 僅列 C#/VB Provider；2) 減少不必要 Provider；3) 減少誤載入。核心組件：system.codedom/compilers、CSharpCodeProvider、VBCodeProvider。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q3, A-Q11, D-Q1

B-Q11: machine.config 與 web.config 的繼承/覆寫機制？
- A簡: 子層設定可覆寫父層；網站以 web.config 為主導。
- A詳: 原理說明：ASP.NET 設定層級自上而下繼承（machine → root web.config → 應用 web.config）。關鍵步驟：1) 讀取機器層；2) 合併/覆寫；3) 應用於應用域。核心組件：Configuration Hierarchy、ConfigurationElement 規則。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q12, C-Q3, D-Q7

B-Q12: 動態編譯與預編譯的差異與流程？
- A簡: 動態按需編譯；預編譯於建置/部署前完成，錯誤提前。
- A詳: 原理說明：動態編譯使用 BuildManager 在首次請求時觸發；預編譯由 aspnet_compiler 或 VS 進行。關鍵步驟：動態：請求→生成→快取；預編譯：掃描→生成→部署。核心組件：BuildManager、aspnet_compiler、Temporary ASP.NET Files。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q6, D-Q3, C-Q10

B-Q13: Debugger Attach 的原理與限制？
- A簡: 連接現有進程插入偵錯，缺少建置整合，符號需手動管理。
- A詳: 原理說明：VS 透過偵錯器協定附加到 w3wp/iisexpress，載入對應 PDB。關鍵步驟：1) 建置符號；2) 起站點；3) Attach；4) 設中斷。核心組件：DbgShim、PDB/Symbol Server、w3wp/iexpress。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q19, C-Q6, D-Q3

B-Q14: VS 排除檔案/資料夾機制如何運作？
- A簡: Web Application 以專案檔控制；Web Site 以排除自專案視圖。
- A詳: 原理說明：Web Application 使用 csproj ItemGroup/Build Action 控制；Web Site 以「排除自專案」從 VS 視圖移除，不再參與建置清單。關鍵步驟：選檔→右鍵排除。核心組件：MSBuild、VS Web Project System。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q2, C-Q5, D-Q4

B-Q15: 在 Web Site 中如何讓檔案不參與建置？
- A簡: 使用「排除自專案」，或移出網站根目錄避免掃描。
- A詳: 原理說明：Web Site 無 Build Action 屬性，僅能藉由排除或移動位置來避免掃描。關鍵步驟：1) 右鍵排除；2) 改存放位置；3) 使用解決方案外資料夾。核心組件：VS 檔案清單、專案系統。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q2, A-Q21, D-Q6

B-Q16: BlogEngine.NET 擴充與 ASP.NET 編譯的關係？
- A簡: 擴充本質是 C# 程式碼，由 ASP.NET/VS 一併編譯管理。
- A詳: 原理說明：Extension 是程式碼檔，位於 App_Code 或專案內，受相同建置規則與 Provider 解析。關鍵步驟：加入檔案→建置包含→運行。核心組件：BuildManager、App_Code 編譯子系統。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q16, C-Q7, D-Q9

B-Q17: PublicKeyToken 與組件解析流程？
- A簡: 強式名稱含 PublicKeyToken，用於從 GAC 準確解析載入。
- A詳: 原理說明：組件解析會比對名稱、版本、文化與 PublicKeyToken，於 GAC 或 probing path 搜尋。關鍵步驟：1) 合成顯式名稱；2) Fusion 搜尋；3) 載入或失敗。核心組件：Fusion Loader、GAC、App.config bindingRedirect。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q13, D-Q7, B-Q5

B-Q18: Provider 載入失敗 VS 如何呈現？
- A簡: 顯示 Build (web) 全域錯誤，內容含 Provider 類型資訊。
- A詳: 原理說明：VS 捕捉到 Configuration/TypeLoad 例外，將其轉映為建置輸出。關鍵步驟：1) 例外捕捉；2) 訊息格式化；3) 顯示於 Error List。核心組件：VS Build Output、Error List。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, D-Q2, B-Q5

B-Q19: 為何 App_Data 大型檔不建議納入建置流程？
- A簡: 增加掃描時間與風險，可能觸發意外處理器。
- A詳: 原理說明：Web Site 掃描成本隨檔案數與型態上升；大量或特殊副檔名可能誤觸 Build/CodeDOM Provider。關鍵步驟：精簡網站內容、移出備份/樣本。核心組件：VS 掃描器、檔案系統。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q21, C-Q8, D-Q6

B-Q20: CodeDomProvider.IsDefinedExtension 的判斷原理？
- A簡: Provider 宣告支援副檔名，供系統比對決定匹配。
- A詳: 原理說明：Provider 內部維護支援副檔名清單；系統用靜態查詢判定。關鍵步驟：呼叫 IsDefinedExtension → true 則交由該 Provider。核心組件：CodeDomProvider 類別。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q3, A-Q9, B-Q4

B-Q21: buildProviders 如何影響編譯？
- A簡: 針對特定副檔名自訂處理流程，可能產生程式碼交編譯。
- A詳: 原理說明：system.web/compilation/buildProviders 可為副檔名指定建置處理器，轉為程式碼後交 CodeDOM 編譯。關鍵步驟：定義 provider→掃描匹配→生成→編譯。核心組件：BuildProvider、CodeDOM Provider。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q20, B-Q1, C-Q3

B-Q22: 安裝 Visual J# 的影響與風險？
- A簡: 可通過建置，但引入淘汰元件與維護負擔，不建議。
- A詳: 原理說明：安裝 J# 會提供 VJSharpCodeProvider，建置含 .java 可通過。風險：J# 已淘汰、相依性增加、安全更新缺乏。關鍵建議：移除 .java 或改為 Web Application 控制 Build Action，避免新增過時相依。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: D-Q8, A-Q14, C-Q4

B-Q23: 現代環境如何處理舊 .java 檔？
- A簡: 移出網站根目錄或排除，必要時改用獨立 Java 工具鏈。
- A詳: 原理說明：.java 檔不應由 .NET J# 編譯；改用 JDK/Gradle 等外部流程。關鍵步驟：1) 檔案外移；2) CI 中分離建置；3) 僅產出二進位或資源供網站使用。核心組件：JDK、CI Pipeline、Artifacts。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q4, D-Q8, A-Q21

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何快速定位 VJSharpCodeProvider 找不到的根因？
- A簡: 以副檔名反推，搜尋 .java，檢查 App_Data 與 web.config 映射。
- A詳: 具體實作步驟：1) 全站搜尋 *.java；2) 檢查 App_Data、隱藏資料夾；3) 檢視 web.config 的 system.codedom/compilers；4) 讀取機器層 machine.config；5) 移除或排除 .java。關鍵程式碼片段或設定：無需程式碼，使用 VS 搜尋及設定檔檢視。注意事項與最佳實踐：優先移除檔案；僅在必要時調整 compilers 清單，避免誤傷其他 Provider。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, D-Q1, A-Q22

C-Q2: 在 Web Site 中如何排除 .java 檔不參與建置？
- A簡: 以「排除自專案」或移至專案外資料夾，避免掃描。
- A詳: 具體實作步驟：1) 在 VS 中選取 .java 檔；2) 右鍵→排除自專案；3) 或將檔案移出網站根目錄；4) 重新建置驗證。關鍵程式碼片段或設定：不適用。注意事項與最佳實踐：Web Site 無 Build Action，排除後才真正脫離建置清單；勿留在 App_Data 內。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q15, D-Q4, A-Q15

C-Q3: 如何用 web.config 覆寫 system.codedom 只保留 C#/VB？
- A簡: 在 web.config 定義 compilers 節點，列出 C#、VB Provider。
- A詳: 具體實作步驟：在 web.config 加入：
  ```
  <configuration>
    <system.codedom>
      <compilers>
        <compiler language="c#;cs" extension=".cs" type="Microsoft.CSharp.CSharpCodeProvider, System.CodeDom, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b03f5f7f11d50a3a" />
        <compiler language="vb;visualbasic" extension=".vb" type="Microsoft.VisualBasic.VBCodeProvider, System.CodeDom, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b03f5f7f11d50a3a" />
      </compilers>
    </system.codedom>
  </configuration>
  ```
  注意事項與最佳實踐：此操作會覆寫機器清單，確保版本與目標框架一致；測試後再提交。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q10, A-Q11, D-Q7

C-Q4: 如何將 .java 轉為靜態資源避免編譯？
- A簡: 改副檔名或壓縮封裝，避免被 Provider 映射識別。
- A詳: 具體實作步驟：1) 將 .java 改名為 .txt 或 .dat；2) 以 zip 壓縮；3) 必要時調整存取程式，解壓或讀文本。關鍵程式碼片段或設定：以 File.ReadAllText 讀取文本資源。注意事項與最佳實踐：保留原檔於版本庫，但部署時以資源形式隨附，避免誤觸建置。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q23, D-Q8, A-Q21

C-Q5: 如何改用 Web Application 專案以掌控 Build Action？
- A簡: 轉換為 Web Application，透過 Build Action 控制編譯參與。
- A詳: 具體實作步驟：1) 新建 Web Application；2) 將原網站檔案加入；3) 設定 .cs 為 Compile，資源為 Content，.java 設為 None；4) 修正命名空間；5) 建置測試。關鍵程式碼片段或設定：csproj ItemGroup 中 Include 與 Build Action。注意事項與最佳實踐：使用 MSBuild/CI，更可控的建置流程。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, B-Q14, D-Q6

C-Q6: 如何設定 VS 偵錯附加至 IIS Express/w3wp？
- A簡: 啟動網站，VS 選擇 Attach to Process，選擇 IIS Express 或 w3wp。
- A詳: 具體實作步驟：1) 在無法 F5 時以 Ctrl+F5 啟動站點；2) VS→Debug→Attach to Process；3) 勾選 Show processes from all users；4) 選擇 iisexpress.exe 或 w3wp.exe；5) Attach。關鍵程式碼片段或設定：無。注意事項與最佳實踐：確保對應 PDB 存在；設定 Just My Code 以利中斷點命中。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q13, D-Q3

C-Q7: 如何建立 BlogEngine.NET 本機開發環境？
- A簡: 取得原始碼、編譯核心、引入站台檔，不含敏感/大型 App_Data。
- A詳: 具體實作步驟：1) 從官方取得 BlogEngine 原始碼；2) 編譯核心解決方案；3) 建立本機站台，複製網站檔案；4) 僅引入必要資料（避免整包 App_Data）；5) 以假資料或測試資料庫運行。關鍵程式碼片段或設定：web.config 連線字串。注意事項與最佳實踐：避免攜入非必要檔案如 .java。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q16, D-Q9, A-Q21

C-Q8: 如何安全搬移 App_Data 而不破壞建置？
- A簡: 僅搬遷必要資料檔，過濾程式碼/備份/大型無關檔案。
- A詳: 具體實作步驟：1) 列出需要的資料檔副檔名（.xml/.mdf/.sqlite/.json）；2) 批次複製並排除 *.java、*.cs、*.vb、*.bak、*.zip；3) 建置驗證。關鍵程式碼片段或設定：robocopy 篩選參數 /XF /XD。注意事項與最佳實踐：建立 .gitignore/.tfignore，避免不必要檔進入版本控制。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q19, A-Q21, D-Q6

C-Q9: 如何清除 VS/ASP.NET 暫存以排除殘留錯誤？
- A簡: 清除 bin、obj、Temporary ASP.NET Files、VS ComponentModelCache。
- A詳: 具體實作步驟：1) 關閉 VS/IIS Express；2) 刪除專案 bin/obj；3) 刪除 %LocalAppData%\Microsoft\WebsiteCache；4) 刪除 %LocalAppData%\Microsoft\VisualStudio\XX\ComponentModelCache；5) 刪除 Temporary ASP.NET Files；6) 重開 VS 重建。注意事項與最佳實踐：備份必要檔案，避免誤刪。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: D-Q7, B-Q18, A-Q18

C-Q10: 如何用 aspnet_compiler 預編譯驗證建置？
- A簡: 使用 aspnet_compiler 指向網站路徑預編譯，提早發現錯誤。
- A詳: 具體實作步驟：1) 開啟開發者命令列；2) 執行：
  ```
  aspnet_compiler -v /MySite -p C:\Path\To\Site C:\PrecompiledOut
  ```
  3) 觀察輸出錯誤訊息；4) 修正後重試。注意事項與最佳實踐：以相同 .NET 版本執行；與 VS 設定一致；納入 CI。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q12, D-Q1, A-Q6

### Q&A 類別 D: 問題解決類（10題）

D-Q1: 遇到「CodeDom provider type ... could not be located」怎麼辦？
- A簡: 由 Provider 反推檔案類型，搜尋並移除或排除觸發檔案。
- A詳: 問題症狀描述：建置失敗，訊息指向某 Provider 載入失敗。可能原因分析：專案內存在需該 Provider 的檔案（如 .java），或設定映射不當。解決步驟：1) 搜尋相應副檔名；2) 移除/排除檔案；3) 覆寫 web.config compilers（選用）；4) 清理快取重建。預防措施：控管站點檔案類型，建立搬遷白名單。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, B-Q5, A-Q7

D-Q2: VS 顯示「(0): Build (web)」無檔名錯誤如何診斷？
- A簡: 確認為全域建置錯誤，檢查 Provider、config 與檔案掃描。
- A詳: 問題症狀描述：錯誤無檔名/行號。可能原因分析：Provider 載入失敗、組件缺失、設定覆寫衝突。解決步驟：1) 讀錯誤文本找 Provider 名稱；2) 搜尋相應副檔名；3) 檢查 web.config/machine.config compilers；4) Fusion log 追蹤。預防措施：固定 Provider 清單，減少歧義。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, C-Q3, A-Q18

D-Q3: 網站能執行但無法 F5 偵錯怎麼辦？
- A簡: 先修建置錯誤；過渡期以 Attach 偵錯確保開發不中斷。
- A詳: 問題症狀描述：CTRL+F5 可跑，F5 因建置失敗中斷。可能原因分析：建置前置掃描觸發 Provider 錯誤。解決步驟：1) 按 D-Q1 修復建置；2) 臨時用 C-Q6 Attach；3) 建置恢復後改回 F5。預防措施：CI 預編譯檢查，提交前建置。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q10, C-Q6, B-Q12

D-Q4: 加入 App_Data 後建置失敗的可能原因？
- A簡: 夾帶程式碼或特殊副檔名，引發 Provider 或 Build Provider。
- A詳: 問題症狀描述：搬入 App_Data 後開始報錯。可能原因分析：存在 .java、.cs、.vb、.config 等被掃描處理的檔案。解決步驟：1) 篩選/移除非資料檔；2) 排除自專案；3) 覆寫 compilers；4) 重建。預防措施：資料檔白名單策略，排除模式。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, C-Q8, B-Q6

D-Q5: 出現要求安裝 Visual J# 但我沒用 J#，怎麼解？
- A簡: 搜尋並移除 .java 等觸發檔案，避免安裝過時 J#。
- A詳: 問題症狀描述：錯誤指出 VJSharpCodeProvider 不存在。可能原因分析：掃描到 .java。解決步驟：1) 搜索 *.java；2) 移除/排除；3) 清理快取；4) 重建。預防措施：不要在站點內儲存 Java 原始碼；改用外部存放或壓縮。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, B-Q9, C-Q2

D-Q6: 建置時間過長與錯誤風險如何降低？
- A簡: 精簡站點內容、移除無關檔、採 Web Application 管理。
- A詳: 問題症狀描述：Build 緩慢且偶發錯誤。可能原因分析：掃描檔案多、混放類型。解決步驟：1) 移出大檔與非 Web 檔；2) Web Application 控制 Build Action；3) CI 預編譯。預防措施：檔案結構治理、忽略清單、白名單發佈。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q19, C-Q5, A-Q21

D-Q7: 移除 .java 後仍報 Provider 錯，如何清理？
- A簡: 清除 bin/obj、WebsiteCache、Temporary ASP.NET Files 後重建。
- A詳: 問題症狀描述：已刪檔仍報錯。可能原因分析：快取/暫存未更新。解決步驟：1) 依 C-Q9 清理快取；2) 重啟 VS/IIS Express；3) 驗證 web.config 覆寫；4) Fusion 日誌確認無殘留引用。預防措施：建置前清理；避免平行建置。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q9, B-Q17, B-Q18

D-Q8: 若確實需要 .java，如何正確支援？
- A簡: 外部 Java 工具鏈編譯產出，再以資源/服務方式整合。
- A詳: 問題症狀描述：需要 Java 程式邏輯。可能原因分析：誤圖以 J# 在 .NET 內編譯。解決步驟：1) 用 JDK/Gradle/Maven 建置；2) 產出 JAR/輸出資料；3) 以服務或互通協定整合（HTTP/GRPC/檔案）。預防措施：避免安裝 J#；分離技術棧與部署。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q23, C-Q4, A-Q14

D-Q9: BlogEngine.NET 升級後編譯錯誤如何核對？
- A簡: 先確保核心可建置，再逐步合併站台檔，排除非必要檔。
- A詳: 問題症狀描述：升級/擴充後報錯。可能原因分析：帶入站台歷史檔（如 .java）、設定不一致。解決步驟：1) 乾淨編譯核心；2) 分批搬檔；3) 每步建置驗證；4) 檢查 web.config 差異。預防措施：建立升級清單與檔案白名單。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q7, A-Q22, B-Q2

D-Q10: 出現未知 Provider（如 JScript/VBScript）錯誤怎診斷？
- A簡: 同樣由 Provider 名稱反推副檔名，搜尋、排除、覆寫映射。
- A詳: 問題症狀描述：Provider 名稱不同但型態相似。可能原因分析：專案中有對應副檔名或 config 指向該 Provider。解決步驟：1) 搜尋副檔名；2) 排除或改名；3) 覆寫 compilers；4) 清理快取重建。預防措施：固定 Provider 清單，嚴管檔案型態。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, C-Q3, A-Q11

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 CodeDOM Provider？
    - A-Q2: 什麼是 Visual J# 與 VJSharpCodeProvider？
    - A-Q3: 什麼是 ASP.NET 的 App_Data 資料夾？
    - A-Q4: ASP.NET Web Site 與 Web Application 有何差異？
    - A-Q5: 為何 App_Data 也可能影響建置？
    - A-Q6: 什麼是 ASP.NET 的動態編譯與預先編譯？
    - A-Q7: 為什麼會出現「CodeDom provider type ... could not be located」？
    - A-Q8: 該錯誤為何常沒有檔名與行號？
    - A-Q10: 為什麼網站可以執行，卻無法 F5 偵錯？
    - A-Q15: 為什麼不建議將原始碼放進 App_Data？
    - A-Q17: App_Code 與 App_Data 差異是什麼？
    - A-Q22: 這個案例的根因和結論是什麼？
    - C-Q1: 如何快速定位 VJSharpCodeProvider 找不到的根因？
    - C-Q2: 在 Web Site 中如何排除 .java 檔不參與建置？
    - D-Q1: 遇到「CodeDom provider type ... could not be located」怎麼辦？

- 中級者：建議學習哪 20 題
    - B-Q1: ASP.NET 網站的整體編譯流程如何運作？
    - B-Q2: Visual Studio 的 Build Website 執行流程為何？
    - B-Q3: 系統如何解析副檔名對應的編譯器？
    - B-Q4: CodeDOM Provider 的機制是什麼？
    - B-Q5: 當找不到 Provider 會發生什麼？
    - B-Q6: App_Data 設計時與執行時的處理差異？
    - B-Q7: 為何錯誤沒有行號—全域錯誤來源？
    - B-Q8: 如何從錯誤訊息反推問題範圍？
    - B-Q10: web.config 的 system.codedom 如何影響 Provider 列表？
    - B-Q11: machine.config 與 web.config 的繼承/覆寫機制？
    - B-Q12: 動態編譯與預編譯的差異與流程？
    - B-Q14: VS 排除檔案/資料夾機制如何運作？
    - B-Q15: 在 Web Site 中如何讓檔案不參與建置？
    - B-Q17: PublicKeyToken 與組件解析流程？
    - C-Q3: 如何用 web.config 覆寫 system.codedom 只保留 C#/VB？
    - C-Q5: 如何改用 Web Application 專案以掌控 Build Action？
    - C-Q6: 如何設定 VS 偵錯附加至 IIS Express/w3wp？
    - C-Q9: 如何清除 VS/ASP.NET 暫存以排除殘留錯誤？
    - D-Q2: VS 顯示「(0): Build (web)」無檔名錯誤如何診斷？
    - D-Q3: 網站能執行但無法 F5 偵錯怎麼辦？

- 高級者：建議關注哪 15 題
    - B-Q20: CodeDomProvider.IsDefinedExtension 的判斷原理？
    - B-Q21: buildProviders 如何影響編譯？
    - B-Q22: 安裝 Visual J# 的影響與風險？
    - B-Q23: 現代環境如何處理舊 .java 檔？
    - A-Q11: 何謂 system.codedom/compilers？
    - A-Q12: Machine.config 與 Web.config 在編譯上有何關係？
    - A-Q13: GAC 與 Provider 載入失敗有何關聯？
    - A-Q20: Build Provider 與 CodeDOM 有何關係？
    - C-Q4: 如何將 .java 轉為靜態資源避免編譯？
    - C-Q10: 如何用 aspnet_compiler 預編譯驗證建置？
    - D-Q5: 出現要求安裝 Visual J# 但未用 J#，怎麼解？
    - D-Q6: 建置時間過長與錯誤風險如何降低？
    - D-Q7: 移除 .java 後仍報 Provider 錯，如何清理？
    - D-Q8: 若確實需要 .java，如何正確支援？
    - D-Q10: 出現未知 Provider（如 JScript/VBScript）錯誤怎診斷？