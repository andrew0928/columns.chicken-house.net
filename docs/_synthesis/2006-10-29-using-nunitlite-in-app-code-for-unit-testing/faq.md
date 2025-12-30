---
layout: synthesis
title: "利用 NUnitLite, 在 App_Code 下寫單元測試"
synthesis_type: faq
source_post: /2006/10/29/using-nunitlite-in-app-code-for-unit-testing/
redirect_from:
  - /2006/10/29/using-nunitlite-in-app-code-for-unit-testing/faq/
---

# 利用 NUnitLite 在 App_Code 下寫單元測試

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 NUnitLite？
- A簡: 精簡版單元測試框架，易嵌入應用程式，適合 Web 環境以程式碼自建測試執行器。
- A詳: NUnitLite 是由 NUnit 衍生的精簡單元測試框架，移除 GUI 與進階 Runner，相對輕量、依賴少。它可直接嵌入應用程式，由程式碼呼叫執行測試，特別適合 Web 應用中以頁面或主控台輸出測試結果的情境。對於中小型專案或需快速驗證環境設定的場合，能以最小成本導入自動化測試。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q3, B-Q1

A-Q2: NUnit 與 NUnitLite 有何差異？
- A簡: NUnit 功能完整含 GUI/分離執行域；NUnitLite 輕量、嵌入式、無外部 Runner。
- A詳: NUnit 提供 GUI/Console Runner、豐富擴充、獨立 AppDomain 與多執行緒隔離，更適合大型或嚴謹流程。NUnitLite 移除外部 Runner，主張由應用程式內部呼叫執行，部署與相依較少，對 Web 應用較友善，避免額外 AppDomain/Thread 帶來的宿主相容性與安全性問題。選擇取決於專案規模與執行環境。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q13, B-Q10

A-Q3: 為何在 Web 應用中選擇 NUnitLite？
- A簡: 部署輕量、避免額外 AppDomain/Thread，容易用頁面呈現測試結果。
- A詳: Web 環境對執行緒、AppDomain、組件載入極為敏感。NUnit 常以新 AppDomain 與獨立執行緒執行，可能與 ASP.NET 生命週期牴觸，且 Assembly 解析不易載入 App_Code。NUnitLite 可嵌入頁面，沿用既有 HTTP 要求脈絡執行，能直接取得 HttpContext、Session 與設定，對檢查配置與快速驗證更順手。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, B-Q2, B-Q10

A-Q4: 什麼是 ASP.NET 的 App_Code 組件？
- A簡: App_Code 於執行期動態編譯成單一組件，供整站共用類別。
- A詳: 在 ASP.NET Web Site 專案中，放在 App_Code 資料夾的類別檔會由 ASP.NET 動態編譯為一個組件，並被網站其他頁面或元件共用。這有利於把測試類別（TestFixture）集中管理，且測試執行器只需指向「App_Code」即可掃描並執行所有測試，無需自行組裝或管理多個專案與輸出。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, B-Q4, C-Q3

A-Q5: 為什麼要把環境設定納入單元測試？
- A簡: 可自動檢查部署正確性，降低人工誤設風險與跨站點差異。
- A詳: 多站點部署、非開發人員安裝時，環境設定（Session 啟用、檔案權限、目錄存在）常是故障來源。將配置檢核以測試表達，可在啟用前一鍵驗證，快速回饋問題點。雖非傳統「函式單元」測試，但在現實專案中能有效提升可用性與維運效率。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q3, D-Q2, D-Q3

A-Q6: 什麼是 TestFixture 與 Test 屬性？
- A簡: 用於標註測試類與測試方法，供框架發現與執行。
- A詳: [TestFixture] 標註包含測試的類別；[Test] 標註具體要執行的測試方法。NUnit/NUnitLite 會以反射掃描這些標註，建立測試樹並逐一執行。配合 Assert 類別進行斷言，將預期行為轉為可自動檢查的結果。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, C-Q3

A-Q7: 什麼是測試執行器（Test Runner）？
- A簡: 負責載入測試、執行與輸出結果的工具或程式碼。
- A詳: 測試執行器可為 GUI、命令列或自訂程式。在本文中以 ASP.NET 頁面扮演 Runner，透過 ConsoleUI.Main 呼叫執行測試，將輸出導向 HTTP 回應。Runner 決定測試發現策略、隔離模型與呈現形式，是整個測試體驗的入口。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, B-Q1, B-Q2

A-Q8: 為何使用瀏覽器頁面作為測試執行器？
- A簡: 符合 Web 環境脈絡，易於操作與共享，免額外工具。
- A詳: 在 Web 站台中，以頁面觸發測試能沿用目前應用程式脈絡，取得 HttpContext、Session 與組態，避免跨進程或跨域帶來的相容性問題。部署後，維運或測試人員只需造訪頁面即可檢視結果，降低工具門檻並加速回饋。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, C-Q2, C-Q5

A-Q9: 為什麼要將 Console 輸出導向 Response？
- A簡: 讓 ConsoleUI 輸出直接顯示在瀏覽器回應中。
- A詳: NUnitLite 的 ConsoleUI 預設輸出至標準輸出（Console）。在 Web 環境，並無主控台視窗，需以 Console.SetOut 指向 Response.Output，將純文字結果回傳給瀏覽器，達成所見即所得的測試回饋。這也是用現有 ConsoleUI 的最小改動方案。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, C-Q2, D-Q4

A-Q10: 設定 Content-Type 為 text/plain 的目的？
- A簡: 明確宣告純文字輸出，避免瀏覽器錯誤解析格式。
- A詳: 測試輸出以純文字為主，設定 Response.ContentType = "text/plain" 可提示瀏覽器用等寬字型與原樣呈現，避免 HTML 解譯。但少數瀏覽器可能 MIME 嗅探誤判，必要時可加上標頭或改為下載附件形式以確保顯示正確。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: D-Q1, C-Q6

A-Q11: 為何需要檢查 Session 是否啟用？
- A簡: 確保功能依賴的狀態管理可用，避免執行期 Null 例外。
- A詳: 許多 Web 功能仰賴 Session 存取使用者狀態。部署或設定差異可能關閉 Session，導致執行期失敗。以測試檢查 HttpContext.Current.Session 不為 null，可在上線前即發現設定問題，降低風險。亦可延伸檢查模式（InProc/StateServer/SQL）與讀寫權限。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q3, D-Q2, B-Q6

A-Q12: 為何需要檢查 temp folder 的存取？
- A簡: 驗證檔案系統權限與路徑正確，避免寫入失敗。
- A詳: Web 應用常需暫存檔案。錯誤的目錄路徑或應用程式集區帳號缺權限，會在執行期拋出存取例外。測試包含 Exists/Write/Read/Delete 可一次驗證「可用性與清理」流程，確保環境具備必要能力，也能提示維運調整 ACL。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q4, D-Q3, D-Q9

A-Q13: 何時應該選用 NUnit 而非 NUnitLite？
- A簡: 大型專案、需嚴格隔離、豐富報表與外部 Runner 時。
- A詳: 當測試套件龐大、需跨平台 Runner、平行化、擴充套件與進階報表時，NUnit 更合適。其獨立 AppDomain 與執行緒隔離提升測試純度，減少相依副作用。若主要在非 Web 環境或需與 CI 工具深度整合，選擇 NUnit 更具彈性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q2, B-Q10

A-Q14: 在 Web 專案中使用 NUnit 的風險？
- A簡: 組件載入、AppDomain 隔離與執行緒模型可能與 ASP.NET 衝突。
- A詳: 完整版 NUnit 會建立新 AppDomain、以獨立執行緒執行測試。對 ASP.NET 而言，這可能導致 App_Code 組件無法解析、HttpContext 缺失、生命週期錯配及權限不同步。除非明確評估影響並隔離環境，不建議直接在 Web 應用內使用外部 Runner。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, D-Q6

A-Q15: 什麼是 AppDomain？為何在 Web 下避免新建？
- A簡: .NET 隔離邏輯執行域；在 Web 新建恐破壞宿主語境。
- A詳: AppDomain 提供組件隔離與回收邊界。Web 宿主（aspnet_wp/w3wp）已管理應用程式域與回收策略。自行新建/交跨 AppDomain 可能破壞既有相依、組件解析與安全語境，導致資源與生命週期管理混亂，影響穩定性與診斷。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q10

A-Q16: 為何測試要避免跨執行緒副作用？
- A簡: Web 要求脈絡非執行緒安全；跨執行緒易遺失 HttpContext。
- A詳: ASP.NET 把 HttpContext 與 Session 綁定於目前請求的執行緒。若測試於背景或不同執行緒執行，會取不到必要脈絡，造成 Null 例外或不一致。嵌入頁面的 Runner 在同一請求執行，可避免這類副作用，除非你能正確地傳遞與流轉脈絡。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q9

A-Q17: 何謂部署前的設定驗證？
- A簡: 上線前以自動化測試檢查環境是否符合需求。
- A詳: 設定驗證將必需條件轉為測試，例如 Session 可用、目錄與權限正確、必要連線串接通。部署完成後先執行測試頁面，若通過即代表環境達標。這種「基礎設施測試」能快速隔離環境與程式問題，縮短故障排除時間。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q5, D-Q10

A-Q18: 什麼是 ASP.NET Hosting？為何提及？
- A簡: 以程式碼自託管 ASP.NET 執行環境的機制。
- A詳: ASP.NET Hosting 指以程式建立與承載 ASP.NET 應用，控制管線與生命週期。文中提到作者實務也用到 Hosting 來執行測試，但為避免偏題未展開。重點在於：即使在更進階的自託管情境，NUnitLite 仍可作為嵌入式 Runner。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q9, B-Q20

A-Q19: IE 將 text/plain 當 XML 的問題是什麼？
- A簡: 瀏覽器 MIME 嗅探誤判，導致以 XML 嘗試解析而報錯。
- A詳: 少數 IE 版本會忽略宣告的 Content-Type，嘗試據內容推斷 MIME 類型（MIME sniffing）。若判成 XML，遇到純文字格式就會抱怨結構錯誤。解法包含改為附件下載、加入禁止嗅探標頭或直接以「檢視原始碼」查看。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q1, C-Q6

A-Q20: 本文範例的核心價值是什麼？
- A簡: 用最小代價把環境檢核納入測試，快速驗證部署品質。
- A詳: 透過 NUnitLite 與簡短 Runner 頁面，直接於 Web 脈絡執行測試，將常見配置風險（Session、檔案權限、目錄）以自動化方式驗證。這種務實方法在中小型或多站點專案尤有價值，降低人為疏失並提升交付穩定度。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, C-Q3, D-Q3

### Q&A 類別 B: 技術原理類

B-Q1: NUnitLite 的 ConsoleUI.Main 如何運作？
- A簡: 掃描指定組件，發現測試並逐一執行，將結果輸出至 Console。
- A詳: ConsoleUI.Main 解析命令列參數，載入對應組件（如 "App_Code"），以反射掃描 [TestFixture]/[Test]，建立測試樹，依序執行，收集通過、失敗、錯誤與略過統計，並將過程與摘要輸出至 Console。於 Web 環境需以 SetOut 重導至 Response。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, A-Q9, C-Q2

B-Q2: NUnitLiteTestRunner.aspx 的執行流程是什麼？
- A簡: Page_Load 設定 ContentType、重導輸出，呼叫 ConsoleUI 執行測試。
- A詳: 瀏覽器請求頁面時，ASP.NET 建立 HttpContext 並觸發 Page_Load；程式碼設定 Response.ContentType="text/plain"，以 Console.SetOut(Response.Output) 將輸出導向 HTTP 回應，再呼叫 ConsoleUI.Main(new[]{"App_Code"}) 執行。請求結束即回傳整份測試結果。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, A-Q9, C-Q2

B-Q3: App_Code 是如何被編譯成組件的？
- A簡: ASP.NET 動態監控並將檔案增量編譯為網站組件。
- A詳: ASP.NET 監看 App_Code 檔案變更，於首次請求或變更時觸發動態編譯，生成一個或多個臨時組件，載入至應用程式域中。Web 頁面與執行器可直接參考這些型別。這解釋了為何只需向 ConsoleUI 指定 "App_Code" 即可載入測試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, B-Q4

B-Q4: 測試發現與執行的機制是什麼？
- A簡: 以反射掃描標註屬性，建樹執行，使用 Assert 判定結果。
- A詳: NUnitLite 透過反射尋找帶 [TestFixture] 的類、[Test] 的方法，建立測試節點與執行順序。呼叫方法時攔截例外與 Assert 結果，分類為通過、失敗（斷言不符）、錯誤（未預期例外）。最後匯總數據並輸出報告。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q1

B-Q5: Console.SetOut 的輸出重導原理是什麼？
- A簡: 將 Console 的 TextWriter 替換為 Response.Output 實例。
- A詳: Console 類維護一個 TextWriter 代表標準輸出。呼叫 Console.SetOut 可注入任意 TextWriter。ASP.NET 的 Response.Output 即為 TextWriter 實作，能將文字串流寫入 HTTP 回應。此技巧使傳統主控台輸出無縫出現在瀏覽器。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, C-Q2, D-Q4

B-Q6: HttpContext.Current.Session 的提供機制如何？
- A簡: ASP.NET 以模組管理 Session，於請求管線附掛至 HttpContext。
- A詳: 開啟 Session 後，SessionStateModule 在管線 AcquireRequestState 取得或建立 Session，並附加至 HttpContext.Current。若停用或於非標準請求（如外部執行緒），會取不到 Session。使用嵌入頁面執行器可確保同一請求脈絡。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, D-Q2

B-Q7: ConfigurationManager.AppSettings 的工作原理？
- A簡: 讀取 web.config 的 appSettings 區段並快取於應用域。
- A詳: ConfigurationManager 解析組態檔，將 appSettings 的鍵值讀入，於應用程式域快取；變更檔案會觸發重載與應用程式回收。測試使用 ConfigurationManager.AppSettings["temp-folder"] 可取得設定值，需注意鍵名正確與空值處理。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q4, D-Q3

B-Q8: 目錄與檔案 I/O 測試的機制與風險？
- A簡: 以 Exists/Write/Read/Delete 驗證，需注意權限與鎖定。
- A詳: 目錄存在性以 Directory.Exists 檢查；寫入以 File.WriteAllText，讀回比較內容，一致後以 File.Delete 清理。風險在於權限不足、檔案鎖定、並發存取與磁碟配額。建議使用唯一檔名、try-finally 清理與最小權限原則。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, D-Q3, D-Q8

B-Q9: 在 Web 上執行測試對 HTTP 管線的影響？
- A簡: 測試與回應共用同請求；長時測試恐阻塞與逾時。
- A詳: Runner 在同一 HTTP 請求中執行；長時間或大量 I/O 測試會占用工作執行緒，導致回應延遲與逾時。應限制測試時間、分頁執行、或提升 executionTimeout（謹慎）。避免阻塞生產流量，可在維護時段或隔離路徑執行。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q7, C-Q5

B-Q10: NUnit 與 NUnitLite 在 AppDomain/執行緒模型差異？
- A簡: NUnit 常啟用獨立 AppDomain/執行緒；NUnitLite 隨宿主執行。
- A詳: NUnit 的 Runner 為提升隔離，創建新 AppDomain、使用獨立執行緒執行測試，減少測試間污染。NUnitLite 多以嵌入模式在現有 AppDomain 與執行緒內進行，與宿主語境一致，易於取得 Web 相關資源。選擇取決於隔離 vs. 相容需求。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, A-Q15

B-Q11: 安全性與應用程式集區帳號對檔案權限影響？
- A簡: 寫檔權限取決於 AppPool 身分與目標目錄 ACL。
- A詳: IIS 應用程式以 AppPool 身分執行（如 ApplicationPoolIdentity）。該帳號需對暫存目錄具讀寫/刪除權限。權限不足將造成 UnauthorizedAccessException。建議賦予最小必要權限至專用目錄，避免授權過廣的系統路徑。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, D-Q9

B-Q12: text/plain 被瀏覽器誤判的原因與機制？
- A簡: MIME 嗅探根據內容字節猜測類型，可能與宣告不符。
- A詳: 某些瀏覽器會忽略 Content-Type，嘗試依內容猜測 MIME，以提升容錯；若字首類似 XML 宣告或結構化符號，可能誤判為 XML/HTML。可加上 X-Content-Type-Options: nosniff、指定下載附件、或輸出明確的純文字頭部避免誤判。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q19, D-Q1

B-Q13: 部署多站點時為何要設計環境自檢？
- A簡: 降低人工差異，快速定位安裝與設定缺陷。
- A詳: 多站點環境常由非開發人員部署，配置差異頻繁。自檢測試將需求轉為程式化檢查，任何錯誤立即回報並附現象，減少反覆溝通與猜測。此法也是交付的「驗收清單」，可被維運流程制度化。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, A-Q17

B-Q14: 測試與設定檔變更的即時編譯機制？
- A簡: web.config 或程式變更觸發重編與應用域回收。
- A詳: 變更 App_Code 會重新編譯該組件；變更 web.config 會導致應用程式回收並重啟。測試頁反映最新程式與設定，但需注意回收造成的會話中斷與短暫不可用。將測試與業務隔離可降低影響。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q5, D-Q10

B-Q15: 例外處理與測試失敗訊號如何傳遞？
- A簡: Assert 失敗與未捕捉例外分別記錄為 Failure/Error。
- A詳: 測試中 Assert.* 不符會擲出 AssertionException，被框架攔截記錄為 Failure；未預期的例外則記錄為 Error。兩者都會呈現堆疊與訊息，最終統計在摘要。適當訊息能提升問題定位效率。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q3, D-Q3

B-Q16: 測試輸出格式設計（純文字 vs HTML）？
- A簡: 純文字簡易穩定；HTML 便於閱讀與格式化但較繁。
- A詳: 純文字便於重導 Console，實作簡單；HTML 可高亮通過/失敗、折疊詳情，但需自行組版，不再能直接重用 ConsoleUI。可折衷：純文字為主、提供下載與「檢視原始碼」，或額外產生簡易 HTML 總結區塊輔助瀏覽。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q6, A-Q10

B-Q17: 在測試中使用 try-finally 做資源回收的理由？
- A簡: 確保例外時也能清理暫存檔，避免資源遺漏。
- A詳: 測試若於讀寫過程失敗，未清除暫存檔會污染後續測試或占用磁碟。以 try 進行操作，finally 中清除檔案與釋放資源，即使失敗也能回到乾淨狀態，提升測試可重入性與穩定度。對檔案與連線尤為重要。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q3, D-Q8

B-Q18: Web.config 中 sessionState 的影響機制？
- A簡: 開關與模式決定 Session 可用性與存取語意。
- A詳: sessionState 可設置 mode（InProc/StateServer/SQLServer）與 enable/timeout 等。關閉時 HttpContext.Session 為 null；外部模式需要額外服務與連線設定。測試應至少檢查可用性，必要時驗證跨請求持久性與序列化。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, D-Q2

B-Q19: 如何篩選執行特定測試（概念）？
- A簡: 以命名空間/型別篩選或自訂反射過濾集合執行。
- A詳: 若框架/版本未提供命令列過濾，可自行撰寫 Runner：以反射取得 App_Code 中型別，依命名空間或名稱過濾，再逐一執行標註 [Test] 的方法。此作法能避免全量執行造成逾時，適合快速檢查特定模組。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: C-Q8, B-Q4

B-Q20: 在 CI/CD 中整合此 Runner 的設計？
- A簡: 以內網 HTTP 觸發頁面、解析輸出、門檻化部署。
- A詳: 於部署步驟後由管線呼叫受保護的測試頁（內網/Basic Auth/IP 白名單），擷取純文字輸出並解析通過/失敗統計，將失敗視為管線中斷。可分「環境健檢」與「功能冒煙」兩頁，分離責任也便於權限控管。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: C-Q5, C-Q7, D-Q10

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何建立 Web Site 並加入 NUnitLite？
- A簡: 建立 ASP.NET Web Site，下載編譯 NUnitLite，加入參考。
- A詳: 步驟：1) 在 VS 建立 ASP.NET 2.0 Web Site；2) 由 NUnitLite 官方取得原始碼並自行 Build 產出 NUnitLite.dll；3) 於網站加入參考；4) 確認 bin 夾包含 DLL；5) 建立 App_Code 以放測試類。注意 DLL 版本一致與相依最小化。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q3

C-Q2: 如何撰寫 NUnitLiteTestRunner.aspx？
- A簡: 在 Page_Load 設定 ContentType、SetOut，呼叫 ConsoleUI.Main。
- A詳: 實作：於網站新增 WebForm NUnitLiteTestRunner.aspx，後置碼示例：
```csharp
protected void Page_Load(object s, EventArgs e){
  Response.ContentType="text/plain";
  Console.SetOut(Response.Output);
  ConsoleUI.Main(new[]{ "App_Code" });
}
```
注意：必要時 Response.BufferOutput=false、執行完畢可 Flush。頁面可限內網使用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, B-Q2, D-Q4

C-Q3: 如何在 App_Code 撰寫 ConfigurationTest？
- A簡: 建 TestFixture，檢查 Session 與暫存目錄讀寫刪除。
- A詳: 於 App_Code 新增類：
```csharp
[TestFixture]
public class ConfigurationTest{
  [Test] public void SessionEnableTest(){
    Assert.NotNull(HttpContext.Current.Session);
  }
  [Test] public void TempFolderAccessTest(){
    var path=ConfigurationManager.AppSettings["temp-folder"];
    Assert.True(Directory.Exists(path));
    var f=Path.Combine(path,"test.txt"); var c="12345";
    File.WriteAllText(f,c);
    Assert.AreEqual(File.ReadAllText(f),c);
    File.Delete(f);
  }
}
```
確保引用 System.Configuration。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, A-Q12, B-Q7

C-Q4: 如何在 web.config 設定 temp-folder？
- A簡: 於 appSettings 加入鍵值，指向具讀寫權限的目錄。
- A詳: 於 web.config：
```xml
<appSettings>
  <add key="temp-folder" value="C:\AppTemp\" />
</appSettings>
```
或使用相對路徑 Server.MapPath("~/App_Data/temp")。確保目錄存在且 AppPool 帳號具讀/寫/刪除權限。建議使用 App_Data 子資料夾避免佈署干擾。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, B-Q11, D-Q9

C-Q5: 如何部署並執行測試頁？
- A簡: 發佈網站與 DLL，瀏覽器造訪 Runner 頁面檢視結果。
- A詳: 1) 發佈網站至目標 IIS；2) 確認 bin 有 NUnitLite.dll；3) 設定 web.config 與目錄權限；4) 瀏覽 http(s)://site/NUnitLiteTestRunner.aspx；5) 檢視純文字結果。若需在 CI 觸發，可用 curl 取回輸出並解析。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q9, B-Q20, D-Q7

C-Q6: 如何將輸出改為 HTML 並格式化？
- A簡: 改以自訂渲染器輸出 HTML，或包裝純文字於 <pre>。
- A詳: 簡易法：ContentType="text/html"，以 <pre> 包裹 Console 輸出。進階法：改寫 Runner，改用 StringWriter 收集輸出，解析統計後生成 HTML：
```csharp
var sw=new StringWriter();
Console.SetOut(sw); ConsoleUI.Main(new[]{"App_Code"});
var text=sw.ToString(); Response.Write($"<pre>{HttpUtility.HtmlEncode(text)}</pre>");
```
可加總結區塊與樣式。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q16, A-Q10, D-Q1

C-Q7: 如何限制只有內部人員可執行測試頁？
- A簡: 以驗證與授權限制，例如 Windows/Forms/IP 白名單。
- A詳: 作法：1) 以 <authorization> 限制角色；2) 只允許內網存取（IIS IP 限制）；3) 在頁面檢查 User.IsInRole；4) 設置自訂路徑，避免被搜尋到；5) 加上基本驗證或單次密碼。確保測試頁不暴露敏感環境資訊。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q20, D-Q10

C-Q8: 如何只執行特定命名空間或類別測試？
- A簡: 自訂反射篩選型別，逐一執行標註的測試方法。
- A詳: 若無內建篩選，改寫 Runner：用反射過濾 App_Code 組件中名稱含關鍵字的 TestFixture，手動執行：
```csharp
var asm=BuildManager.GetReferencedAssemblies().Cast<Assembly>()
  .First(a=>a.GetName().Name.StartsWith("App_Code"));
var targets=asm.GetTypes().Where(t=>t.IsClass && t.GetCustomAttributes(typeof(TestFixtureAttribute),true).Any()
  && t.Namespace?.Contains("Config")==true);
foreach(var t in targets){ /* 反射呼叫帶 [Test] 的方法 */ }
```
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q19, B-Q4

C-Q9: 如何在部署後第一次啟動時執行測試？
- A簡: 於 Application_Start 或健康檢查流程觸發內部測試。
- A詳: 在 Global.asax 的 Application_Start 註冊背景工作呼叫 Runner；或設定 Deployment Pipeline 最後以 HTTP ping 測試頁。注意：避免在啟動同步執行長測試阻塞啟動；可記錄結果並只在失敗時告警，或用旗標控制只跑一次。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, D-Q7, D-Q10

C-Q10: 如何在本機與多站點環境重用該測試？
- A簡: 以設定驅動測試，避免硬編碼路徑，抽象環境差異。
- A詳: 以 appSettings 驅動所有外部資源（暫存路徑、服務端點），測試只依賴鍵名。將站點差異透過 transforms 或環境變數注入。提供統一 Runner 頁面，各站以相同測試碼驗證，穩定比較差異與回報。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q13

### Q&A 類別 D: 問題解決類（10題）

D-Q1: IE 將結果當 XML 顯示錯誤，怎麼辦？
- A簡: 使用「檢視原始碼」、禁用嗅探、或改為附件下載。
- A詳: 症狀：IE 顯示 XML 錯誤而非純文字。原因：MIME 嗅探誤判。解法：1) 按右鍵檢視原始碼；2) 回應加上 X-Content-Type-Options:nosniff；3) 改 ContentType="application/octet-stream" 並加 Content-Disposition 附件；4) 以 <pre> 包含 HTML。預防：固定輸出格式並測試主要瀏覽器。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q19, C-Q6, B-Q12

D-Q2: 測試無法讀取 Session，如何排查？
- A簡: 確認 sessionState 啟用、在同一請求執行、未跨執行緒。
- A詳: 症狀：Assert.NotNull(Session) 失敗。原因：web.config 關閉 Session、測試於非請求執行緒、或以外部 Runner 執行。步驟：1) 檢查 <sessionState mode="InProc" cookieless="false" />；2) 確保由頁面 Runner 執行；3) 不要用背景執行緒。預防：建立專用 Session 健檢測試。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, B-Q6, A-Q16

D-Q3: TempFolderAccessTest 失敗，可能原因？
- A簡: 路徑錯、目錄不存在、權限不足、檔案鎖定。
- A詳: 症狀：Exists/Write/Read/Delete 任一步失敗。分析：appSettings 鍵名錯誤或空值、目錄未建立、AppPool 帳號無權限、檔案被掃毒或同步程序鎖定。步驟：1) 記錄實際路徑；2) 建立目錄；3) 調整 ACL；4) 用唯一檔名。預防：使用 App_Data 子目錄與最小權限。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q11, B-Q8

D-Q4: 測試頁無輸出或空白，如何處理？
- A簡: 檢查 SetOut、ContentType、例外攔截與 Response.Flush。
- A詳: 症狀：頁面空白或無任何結果。原因：未 SetOut、NUnitLite 未載入、例外被 ASP.NET 錯誤頁隱藏、緩衝未刷新。步驟：1) 確認 Console.SetOut(Response.Output)；2) 確認引用 DLL 與版本；3) Try/Catch 包住 ConsoleUI.Main 記錄例外；4) 最後呼叫 Response.Flush。預防：加啟用詳細錯誤。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q2

D-Q5: 引用 NUnitLite.dll 失敗或版本衝突？
- A簡: 重新編譯相容版本、清理 bin、核對目標框架。
- A詳: 症狀：編譯/執行期找不到或載入失敗。原因：.NET 版本不符、混入舊版 DLL、相依組件缺失。步驟：1) 以相同目標框架重新編譯 NUnitLite；2) 清理 bin 與 Temporary ASP.NET Files；3) 檢查 Web.Config bindingRedirect；4) 檢視 Fusion Log。預防：以套件管理統一版本。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q1, B-Q1

D-Q6: 使用 NUnit GUI/Console 無法載入 App_Code？
- A簡: 外部 Runner 不識別動態編譯與 Web 脈絡，改用頁面 Runner。
- A詳: 症狀：NUnit 無法找到測試或拋載入錯誤。原因：App_Code 為動態組件、外部 Runner 在不同 AppDomain/執行緒，缺乏 ASP.NET 解析。解法：改用嵌入頁面 Runner；若要用 NUnit，改以 Class Library 專案承載測試。預防：Web 內避免外部 Runner。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q10

D-Q7: 測試執行時間過長導致 timeout？
- A簡: 縮短測試、拆分頁面、提高 executionTimeout（謹慎）。
- A詳: 症狀：請求逾時或 500。原因：長測試占用請求執行緒。步驟：1) 移除慢測試（I/O/外部依賴）；2) 把環境健檢與冒煙測試分頁；3) web.config 調整 <httpRuntime executionTimeout="180" />（評估風險）；4) 後台任務記錄輸出。預防：保持測試短小。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, C-Q5

D-Q8: 檔案刪除拋例外，可能原因與對策？
- A簡: 檔案被占用或權限不足，確保關閉流並重試。
- A詳: 症狀：File.Delete 例外。原因：前一步仍開啟流、其他程序占用、無刪除權。解法：1) 使用 File.*AllText（無留流）；2) 使用 using 關閉；3) 加入重試與退避；4) 確認刪除權限。預防：唯一檔名與 try-finally 清理，避免平行測試競爭。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, B-Q17

D-Q9: 部署後測試無法存取檔案權限？
- A簡: 檢查 AppPool 身分與目錄 ACL，授最小必需權。
- A詳: 症狀：UnauthorizedAccess。原因：AppPool 身分無權限、路徑在受保護區（如 Program Files）。步驟：1) 確認身分（IIS 管理器）；2) 在目標目錄新增該身分讀/寫/刪除；3) 改用 App_Data；4) 避免網路磁碟（權限複雜）。預防：佈署腳本自動化設定。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q11, C-Q4

D-Q10: 執行測試影響線上系統，如何降風險？
- A簡: 隔離測試頁、控管權限與時段、僅跑輕量健檢。
- A詳: 風險：阻塞請求、暴露資訊、影響效能。作法：1) 測試頁限內網/授權；2) 控管維護時段執行；3) 減少 I/O 與外部依賴；4) 拆分健檢與功能測試；5) 加入節流與逾時設定；6) 在 CI 部署後自動觸發再下線，避免人工誤操作。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q7, B-Q20, B-Q9

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 NUnitLite？
    - A-Q2: NUnit 與 NUnitLite 有何差異？
    - A-Q3: 為何在 Web 應用中選擇 NUnitLite？
    - A-Q4: 什麼是 ASP.NET 的 App_Code 組件？
    - A-Q5: 為什麼要把環境設定納入單元測試？
    - A-Q6: 什麼是 TestFixture 與 Test 屬性？
    - A-Q7: 什麼是測試執行器（Test Runner）？
    - A-Q8: 為何使用瀏覽器頁面作為測試執行器？
    - A-Q9: 為什麼要將 Console 輸出導向 Response？
    - A-Q10: 設定 Content-Type 為 text/plain 的目的？
    - C-Q1: 如何建立 Web Site 並加入 NUnitLite？
    - C-Q2: 如何撰寫 NUnitLiteTestRunner.aspx？
    - C-Q3: 如何在 App_Code 撰寫 ConfigurationTest？
    - C-Q5: 如何部署並執行測試頁？
    - D-Q1: IE 將結果當 XML 顯示錯誤，怎麼辦？

- 中級者：建議學習哪 20 題
    - B-Q1: NUnitLite 的 ConsoleUI.Main 如何運作？
    - B-Q2: NUnitLiteTestRunner.aspx 的執行流程是什麼？
    - B-Q3: App_Code 是如何被編譯成組件的？
    - B-Q4: 測試發現與執行的機制是什麼？
    - B-Q5: Console.SetOut 的輸出重導原理是什麼？
    - B-Q6: HttpContext.Current.Session 的提供機制如何？
    - B-Q7: ConfigurationManager.AppSettings 的工作原理？
    - B-Q8: 目錄與檔案 I/O 測試的機制與風險？
    - B-Q9: 在 Web 上執行測試對 HTTP 管線的影響？
    - B-Q10: NUnit 與 NUnitLite 在 AppDomain/執行緒模型差異？
    - A-Q11: 為何需要檢查 Session 是否啟用？
    - A-Q12: 為何需要檢查 temp folder 的存取？
    - A-Q14: 在 Web 專案中使用 NUnit 的風險？
    - C-Q4: 如何在 web.config 設定 temp-folder？
    - C-Q6: 如何將輸出改為 HTML 並格式化？
    - C-Q7: 如何限制只有內部人員可執行測試頁？
    - C-Q9: 如何在部署後第一次啟動時執行測試？
    - D-Q2: 測試無法讀取 Session，如何排查？
    - D-Q3: TempFolderAccessTest 失敗，可能原因？
    - D-Q7: 測試執行時間過長導致 timeout？

- 高級者：建議關注哪 15 題
    - A-Q15: 什麼是 AppDomain？為何在 Web 下避免新建？
    - A-Q16: 為何測試要避免跨執行緒副作用？
    - A-Q18: 什麼是 ASP.NET Hosting？為何提及？
    - B-Q11: 安全性與應用程式集區帳號對檔案權限影響？
    - B-Q12: text/plain 被瀏覽器誤判的原因與機制？
    - B-Q16: 測試輸出格式設計（純文字 vs HTML）？
    - B-Q17: 在測試中使用 try-finally 做資源回收的理由？
    - B-Q18: Web.config 中 sessionState 的影響機制？
    - B-Q19: 如何篩選執行特定測試（概念）？
    - B-Q20: 在 CI/CD 中整合此 Runner 的設計？
    - C-Q8: 如何只執行特定命名空間或類別測試？
    - C-Q10: 如何在本機與多站點環境重用該測試？
    - D-Q5: 引用 NUnitLite.dll 失敗或版本衝突？
    - D-Q6: 使用 NUnit GUI/Console 無法載入 App_Code？
    - D-Q10: 執行測試影響線上系統，如何降風險？