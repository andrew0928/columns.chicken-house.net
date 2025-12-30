---
layout: synthesis
title: "Fiddler 跟 TFS 相衝的問題解決 - II"
synthesis_type: faq
source_post: /2007/04/24/fiddler-tfs-conflict-solution-part-2/
redirect_from:
  - /2007/04/24/fiddler-tfs-conflict-solution-part-2/faq/
---

# Fiddler 跟 TFS 相衝的問題解決 - II

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 Fiddler？
- A簡: Fiddler 是 Windows 上的 HTTP(S) 代理除錯工具，透過修改 WinINET 代理設定攔截流量。
- A詳: Fiddler 是一款廣泛使用的 HTTP(S) 代理除錯工具，主要在 Windows 上運作。它啟用時會將系統（WinINET）代理指向 127.0.0.1:8888，藉此攔截瀏覽器與其他 WinINET 客戶端的流量，便於檢視、修改與重放請求。Fiddler 提供事件式的 FiddlerScript（CustomRules.js），能在不同階段（如 OnAttach）自動執行自訂邏輯，提升除錯與測試效率。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, B-Q1, B-Q5

A-Q2: 什麼是 TFS（Team Foundation Server）？
- A簡: TFS 是微軟的 ALM/DevOps 平台，提供版本控制、工作項目、建置與部署。
- A詳: Team Foundation Server（現 Azure DevOps Server）是微軟提供的應用生命週期管理平台，涵蓋版本控制、工作項目追蹤、建置/發佈與測試。用戶端（例如 Visual Studio）與 TFS 伺服器的通訊多依賴 WinINET 或相關 HTTP 堆疊，因此當系統代理被臨時改為 Fiddler 時，若未妥善設定例外或網路介面，可能導致 TFS 操作（如 Get Latest）受影響。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, B-Q13, D-Q4

A-Q3: 什麼是 WinINET 代理設定？
- A簡: WinINET 是 Windows 網路堆疊，IE 與許多應用使用其代理設定（含每介面卡設定）。
- A詳: WinINET 是 Windows 提供的網路 API，IE 與多數以 WinINET 為基底的應用會讀取其代理設定。代理設定包含地址、連接埠與「不使用代理的位址」清單（Bypass List），且支援每個網路介面卡（連線）擁有獨立設定。Fiddler 啟用時通常將這些設定改為 127.0.0.1:8888，以攔截與分析流量。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q12, B-Q15, C-Q4

A-Q4: 什麼是 CustomRules.js？
- A簡: FiddlerScript 檔案，用於定義 Fiddler 的事件處理與規則，動態編譯執行。
- A詳: CustomRules.js 是 Fiddler 的腳本檔，用於以 JScript.NET（或 C#）擴充 Fiddler 的行為。它在 Fiddler 執行期間動態載入與編譯，並提供多個事件（如 OnAttach、OnBeforeRequest）供使用者插入自訂流程，例如修改標頭、重新導向、或在開始擷取時調整 WinINET 代理例外清單。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, C-Q1, C-Q3

A-Q5: 什麼是 OnAttach 事件？
- A簡: OnAttach 在 Fiddler 開始擷取流量時觸發，可放自動化初始化程式。
- A詳: OnAttach 是 FiddlerScript 中於 Fiddler 進入「開始擷取流量」狀態時觸發的事件。常見用途包括：記錄狀態、設定測試標記、或調整 WinINET 代理相關屬性（如例外清單），使系統在啟用攔截當下即套用必要設定，確保後續工具（如 TFS）不受影響。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, B-Q1, B-Q16

A-Q6: 什麼是 AppDomain？
- A簡: AppDomain 是 .NET 的隔離邊界，提供與行程類似的安全隔離但成本較低。
- A詳: AppDomain 是 .NET 執行期提供的隔離區域，允許在同一行程中隔離程式碼、類型與安全證據。它兼具行程的安全隔離與執行緒的低成本溝通特性。Fiddler 會在獨立 AppDomain 動態編譯與載入 FiddlerScript，因此腳本對於宿主程式之可見型別、權限與載入邏輯會受限制。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q5, B-Q15

A-Q7: AppDomain 與 Process 有何差異？
- A簡: AppDomain 是行程內的邏輯隔離；Process 是 OS 隔離。AppDomain成本較低。
- A詳: Process 是作業系統級隔離，擁有獨立記憶體空間與更強的安全邊界；AppDomain 則是 .NET 執行期內的邏輯隔離，具較低切換成本且可共享行程資源。AppDomain 適合隔離外掛/腳本；Process 則多用於可靠性與安全需求更高的外部工具（如文中以外部 exe 變更代理設定的做法）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, D-Q9, A-Q6

A-Q8: 什麼是 .NET 反射（Reflection）？
- A簡: 反射允許動態載入組件、查詢型別、呼叫方法/屬性。
- A詳: .NET 反射提供在執行期探索與操作型別的能力，包括載入組件（Assembly.LoadFrom）、建立執行個體（CreateInstance）、以及透過 MethodInfo/PropertyInfo 呼叫方法或設定屬性。反射能繞過編譯時依賴，但在部分信任與可見性（private/internal）上會受限，且在 FiddlerScript 的 AppDomain 內更可能受安全或解析規則影響。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, B-Q10, D-Q8

A-Q9: 什麼是 sHostsThatBypass（代理例外清單）？
- A簡: 指定不經代理的主機清單，使用分號分隔並支援萬用字元。
- A詳: sHostsThatBypass 是 WinINET 代理設定中的例外清單，列出不需透過代理的主機或網域，常見格式為「*.domain.com;localhost;10.*;」。在 Fiddler 架構中可由 WinINETProxyInfo 設定，以避免某些服務（如 TFS）被 Fiddler 攔截或經代理導致問題，改善相容性與效能。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q12, C-Q5, D-Q5

A-Q10: 為什麼 Fiddler 與 TFS 會相衝？
- A簡: Fiddler改寫系統代理，若未排除 TFS 網域，通訊會被攔截或錯誤。
- A詳: Fiddler 啟用時會將 WinINET 代理改至本機 127.0.0.1:8888。若 TFS 連線未加入代理例外，請求即會經 Fiddler。當憑證、代理規則或多網卡設定不一致時，可能導致 TFS 連線逾時、認證異常或 Get Latest 失敗。將 TFS 網域加入 Bypass 或於 OnAttach 自動調整設定能解決衝突。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q8, D-Q4, B-Q1

A-Q11: 為什麼在 VPN/無線環境 Fiddler 常失效？
- A簡: 因 IE 支援每介面卡代理，Fiddler常只改「區域連線」，其他未改。
- A詳: IE（WinINET）允許每個網路介面卡（例如有線、無線、VPN）擁有獨立代理設定。Fiddler 預設多只改「區域連線」，導致實際使用的 VPN 或無線介面仍沿用原設定，造成無法攔截或通訊異常。需手動或以腳本同步修改實際使用介面卡的代理與例外清單。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q13, C-Q4, D-Q3

A-Q12: 何謂每個網路介面卡各自的 Proxy 設定？
- A簡: WinINET 可為每個連線保存獨立代理與例外清單。
- A詳: 在 Windows 的「網際網路選項」中，每個連線（撥號、VPN、LAN 介面）可分別指定代理伺服器與不使用代理的位址。這提供彈性，但也帶來一致性挑戰：若工具或腳本只改變單一連線，其它連線仍照舊，造成攔截失效或服務受影響。自動化時需識別當前使用連線並一併更新。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, B-Q15, C-Q4

A-Q13: Fiddler 如何保存與還原 Proxy 設定？
- A簡: 啟用時保存當前設定；停用時自動還原原始值。
- A詳: Fiddler 在開始擷取時會先保存當前 WinINET 代理狀態（包含代理、例外清單），再將代理切換到本機。停止擷取或關閉 Fiddler 時，會將保存的舊值寫回，恢復原環境。此設計可讓工具暫時接管網路而不永久污染系統設定。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, C-Q6, D-Q7

A-Q14: 方案 A/B/C/D 分別是什麼策略？
- A簡: A：直連內部欄位；B：參考 Fiddler 類型；C：反射動態載入；D：外部 exe。
- A詳: 方案A試圖直接取用 Fiddler 內部/私有欄位（piPrior/piThis），因存取限制而失敗；方案B將 Fiddler.exe 當 DLL 參考以調 WinINETProxyInfo，於外部程式可行；方案C在腳本中以反射載入並呼叫，受 AppDomain/權限限制仍失敗；方案D於腳本改為 Process.Start 外部 exe，成功達成目標。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q8, B-Q9, B-Q11

A-Q15: 修改系統 Proxy 有哪些風險？
- A簡: 影響全域連線、認證、企業策略；需注意還原與範圍控制。
- A詳: 修改 WinINET 代理屬於系統層變更，可能影響所有使用 WinINET 的應用（IE、VS、Office）。常見風險包含：登入流程失敗、憑證不相容、公司群組原則覆寫、或工具崩潰後未還原。建議：限定時機（OnAttach/OnDetach）、只改必要欄位（例外清單）、提供還原機制與錯誤處理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q6, D-Q7, D-Q10

### Q&A 類別 B: 技術原理類

B-Q1: Fiddler 啟用擷取的執行流程為何？
- A簡: 先保存 WinINET 設定，再設代理為 127.0.0.1:8888，觸發 OnAttach。
- A詳: 啟用時，Fiddler 會保存當前 WinINET 代理狀態（如 Proxy 伺服器、Port、Bypass List），然後將系統代理指向本機 127.0.0.1:8888，以攔截 HTTP(S) 流量。接著載入並執行 FiddlerScript 的 OnAttach 事件，供使用者插入自動化邏輯（例如補齊例外清單）。之後所有 WinINET 客戶端請求將經由 Fiddler。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, A-Q13, C-Q1

B-Q2: Fiddler 停用擷取如何還原設定？
- A簡: 將先前保存的 WinINET 設定寫回，恢復原代理狀態。
- A詳: 在停用擷取或關閉 Fiddler 時，程式會讀取啟用前保存的代理資訊，將其完整寫回 WinINET，包含代理位址、連接埠與例外清單。此流程通常自動執行，確保 Fiddler 的介入僅在擷取期間，降低對系統網路行為的干擾。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q13, C-Q6, D-Q7

B-Q3: WinINETProxyInfo 物件的核心組件是什麼？
- A簡: 提供從 WinINET 讀/寫代理的 API，含 sHostsThatBypass 等屬性。
- A詳: WinINETProxyInfo 封裝了對 WinINET 代理設定的存取能力，常見成員包含從系統讀取（GetFromWinINET）與回寫（SetToWinINET），以及屬性如 sHostsThatBypass（代理例外清單）。在 Fiddler 內部，另有 piPrior、piThis 等成員分別保存原始與目前代理狀態，用於啟停還原。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, A-Q9, B-Q7

B-Q4: GetFromWinINET 與 SetToWinINET 的機制是什麼？
- A簡: 前者讀取當前系統代理；後者將調整後設定寫回 WinINET。
- A詳: GetFromWinINET 會從 WinINET 目前使用的連線讀取代理參數與例外清單，回填至物件；SetToWinINET 則將物件中的代理與 sHostsThatBypass 等屬性反寫回系統。透過此讀-改-寫流程，可在不中斷其他設定的前提下，精準調整特定欄位（如僅更新 Bypass List）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q2, C-Q10, D-Q8

B-Q5: FiddlerScript 的編譯與載入機制如何？
- A簡: 動態載入腳本於獨立 AppDomain，限制可見型別與權限。
- A詳: Fiddler 在執行期間動態載入 CustomRules.js，使用 JScript.NET 或 C# 編譯成組件，並裝入獨立 AppDomain 執行。為安全與穩定，腳本可見型別受限，且某些 API 或宿主內部類型可能不可達。此設計防止腳本影響宿主核心，亦避免記憶體/安全風險蔓延。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q6, D-Q1

B-Q6: 為何在腳本中無法直接參考 Fiddler.WinINETProxyInfo？
- A簡: 因 AppDomain 可見性與權限限制，宿主內部型別不可達。
- A詳: 雖然程式外部（如自建 console app）能參考 Fiddler.exe 並使用 WinINETProxyInfo，但在 FiddlerScript 的 AppDomain 中，該型別可能未公開、未被允許或無法解析載入，導致編譯/執行期錯誤。此限制促使需改採間接方式，例如以外部程式處理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q9, D-Q2

B-Q7: oProxy、piPrior、piThis 各是什麼？
- A簡: oProxy 是 Fiddler 代理管理器；piPrior/ piThis 保存前後代理狀態。
- A詳: 以 Reflector 檢視 Fiddler 可見，oProxy（Fiddler.Proxy）統籌代理邏輯；piPrior 為啟用擷取前保存的 WinINET 設定，piThis 為 Fiddler 正在套用的設定。這些成員多為內部/私有，無法由腳本或外部直接修改，用於穩定執行啟停與還原流程。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q1, B-Q2

B-Q8: 方案 B（參考 Fiddler.exe 當 DLL）的原理？
- A簡: 自建程式參考 Fiddler.exe，直接呼叫 WinINETProxyInfo API。
- A詳: 將 Fiddler.exe 視為可載入的組件，於自建 console app 中加入參考，程式內建立 WinINETProxyInfo 實例，呼叫 GetFromWinINET/SetToWinINET 並更新 sHostsThatBypass。此法在外部行程可行，避開 FiddlerScript 的 AppDomain 限制，能精準改動代理設定。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q2, C-Q10, B-Q6

B-Q9: 方案 C（反射載入 + CreateInstance）的流程？
- A簡: 腳本中 Assembly.LoadFrom 載入 Fiddler.exe，再反射存取型別成員。
- A詳: 在腳本中以 Assembly.LoadFrom("Fiddler.exe") 載入組件，取得 Type("Fiddler.WinINETProxyInfo")，CreateInstance 建立物件，分別反射呼叫 GetFromWinINET、設定 sHostsThatBypass、SetToWinINET。理論可行，但受腳本執行環境的安全與可見性限制，實務上常失敗。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q8, B-Q5, B-Q10

B-Q10: 方案 C 仍失敗的可能原因？
- A簡: 型別不可見、部分信任、載入路徑/版本衝突、限制 API。
- A詳: 失敗成因包含：型別非 public 或被 InternalsVisibleOnly 限制；腳本所在 AppDomain 為部分信任，禁用反射存取或 P/Invoke；組件載入脈絡（LoadFrom vs Load）導致相依解析失敗；或宿主刻意阻擋敏感 API。這些使腳本內反射難以操作宿主內部型別。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: D-Q1, D-Q2, B-Q5

B-Q11: 方案 D（Process.Start 外部程式）的機制？
- A簡: 由腳本啟動外部 exe，在獨立行程修改 WinINET 設定。
- A詳: 在 CustomRules.js 的 OnAttach 內呼叫 System.Diagnostics.Process.Start 啟動自建 exe（如 myproxycfg.exe）。該程式於獨立行程執行，不受腳本 AppDomain 限制，可安全地透過 WinINET API 調整代理例外清單。此法簡單穩健，是限制環境下的務實解法。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q3, D-Q6, A-Q7

B-Q12: 代理例外（Bypass）字串的規則為何？
- A簡: 分號分隔；可用萬用字元；只填主機/網域，不含 http://。
- A詳: WinINET 的 Bypass 字串以「;」分隔，支援萬用字元（如 *.domain.com、10.*）；項目為主機或網域，不包含協定（http://）或路徑。設定錯誤（含協定、空白）會導致規則無效。正確維護 Bypass 有助避開被 Fiddler 攔截的關鍵服務（如 TFS）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, C-Q5, D-Q5

B-Q13: 為何 Fiddler 只改「區域連線」會有影響？
- A簡: 實際上線路可能來自 VPN/無線，未被改動即無法攔截或錯誤。
- A詳: 多網卡環境下，實際活躍路徑可能非「區域連線」。若 Fiddler 只更動該連線的代理，其他（VPN/無線）保持原狀，導致部分應用不經 Fiddler 或發生連線不一致。需同步更新當前使用之連線代理與 Bypass，或用外部工具批量設定。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, C-Q4, D-Q3

B-Q14: AppDomain 隔離與效能的權衡？
- A簡: 提供安全隔離且輕量；但限制型別可見與 API，影響擴充自由度。
- A詳: AppDomain 在同一行程內提供邏輯隔離，跨界交互成本低於進程間通訊，適合腳本或外掛。但其安全模型與載入邊界限制了可見型別與許多操作（如反射敏感 API），避免破壞宿主穩定。當需求超出其能力時，轉向外部行程是常見實務選擇。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, A-Q7, B-Q11

B-Q15: 多網卡環境的 Proxy 決議流程？
- A簡: 依目前連線決議對應代理；各連線保存獨立設定與例外。
- A詳: WinINET 根據當前有效連線（撥號、VPN、LAN）選取對應的代理設定與例外清單。若多條路徑同時存在，應用可能依其 API/設計選擇路徑。因各連線設定獨立，工具僅改動單一路徑會造成不一致。設計自動化時需偵測有效連線並涵蓋其設定。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, C-Q4, D-Q3

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何在 OnAttach 自動套用代理例外清單？
- A簡: 於 CustomRules.js 的 OnAttach 呼叫外部程式或 API 更新 Bypass。
- A詳: 步驟：1) 開啟 FiddlerScript（Rules > Customize Rules）。2) 在 OnAttach 事件中加入自動化。3) 由於腳本無法直接用 WinINETProxyInfo，建議呼叫外部 exe 更新 Bypass。代碼：Process.Start("myproxycfg.exe")。注意：確保 exe 路徑可達、錯誤捕捉、僅改 Bypass，避免覆寫其他設定。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q11, C-Q3, A-Q5

C-Q2: 如何建立 myproxycfg.exe 來設定 WinINET Proxy？
- A簡: 建立 .NET 主控台程式，參考 Fiddler.exe，呼叫 WinINETProxyInfo API。
- A詳: 步驟：1) 新建 Console App。2) 將 Fiddler.exe 當作參考。3) 程式碼：讀取→修改 Bypass→回寫。範例：
  ```
  var p = new Fiddler.WinINETProxyInfo();
  p.GetFromWinINET(null);
  p.sHostsThatBypass = "*.tfs.company.com;*.intra;";
  p.SetToWinINET(null);
  ```
  注意：避免改代理位址/連接埠，僅調整 Bypass；在 Fiddler 目錄部署，確保權限足夠。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, B-Q4, D-Q6

C-Q3: 如何在 CustomRules.js 內呼叫外部 exe？
- A簡: 使用 System.Diagnostics.Process.Start 啟動位於已知路徑的程式。
- A詳: 在 OnAttach 內加入：
  ```
  System.Diagnostics.Process.Start("myproxycfg.exe");
  ```
  或提供完整路徑。加入 try/catch 記錄失敗；可在 OnDetach 視需求執行還原工具。注意：程式需與 Fiddler 同資料夾或 PATH 可搜尋，且企業安全政策可能限制啟動外部程式。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q11, D-Q6, D-Q1

C-Q4: 如何針對 VPN/無線網卡同步設定 Proxy？
- A簡: 判斷當前連線，對所有有效連線寫入一致代理與 Bypass。
- A詳: 做法：1) 在外部 exe 中列舉有效介面/連線（或直接調整 WinINET 全局 LAN 設定）。2) 將代理（127.0.0.1:8888）與 Bypass 同步至當前使用的 VPN/無線連線。3) 測試切換網路時是否保持攔截。注意：避免覆寫不相關連線；企業環境建議先備份再批量套用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q13, B-Q15

C-Q5: 如何使用萬用字元設定 Bypass（*.domain.com）？
- A簡: 以分號分隔條目，支援 *.domain.com、10.* 等樣式。
- A詳: 規則：1) 不含協定（不要寫 http://）。2) 支援萬用字元前綴（*.corp.local）。3) 以「;」分隔多條目。範例：
  ```
  "*.tfs.company.com;localhost;10.*;*.intra.company;"
  ```
  注意：避免空格與錯別字；以最小集原則維護，防止意外繞過代理的外部站點。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q12, D-Q5, A-Q9

C-Q6: 如何驗證 Fiddler 啟停時 Proxy 有正確還原？
- A簡: 觀察「網際網路選項」代理頁面，啟用/停用時應切換與還原。
- A詳: 步驟：1) 開啟控制台 > 網際網路選項 > 連線 > 局域網設定。2) 啟用 Fiddler，確認代理改為 127.0.0.1:8888 並含自訂 Bypass。3) 停用擷取或關閉 Fiddler，確認還原至原始設定。若未還原，依 D-Q7 進行修復與預防。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q13, D-Q7, B-Q2

C-Q7: 如何避免在腳本中取用內部類別而改用反射？
- A簡: 不建議在腳本用反射操作宿主型別，改採外部程式。
- A詳: 由於腳本 AppDomain 的安全限制，反射載入宿主組件常失敗。建議作法：1) 將必要操作封裝到外部 exe。2) 腳本僅負責決策與觸發（Process.Start）。3) 外部程式內部使用反射或正式 API 完成工作。此設計提高可靠性並減少維護成本。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, B-Q11, D-Q1

C-Q8: 如何將 TFS 網址加入不經代理清單以避免衝突？
- A簡: 將 TFS 主機或網域加入 sHostsThatBypass，避開 Fiddler 攔截。
- A詳: 在外部 exe 的邏輯內，於讀取現況後追加 TFS 網域：
  ```
  p.sHostsThatBypass = "*.tfs.company.com;*.dev.company;";
  ```
  再 SetToWinINET。或於 Fiddler UI 設定對應的 Bypass（依版本）。注意：若 TFS 走 HTTPS 且需解密測試，則不要繞過，改設定信任憑證與專案排程。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, D-Q4, B-Q12

C-Q9: 如何撰寫容錯：外部 exe 失敗時的處理？
- A簡: 以 try/catch 記錄錯誤，提供回退與重試；不阻斷擷取流程。
- A詳: 在腳本呼叫外部 exe 時以 try/catch 包裹，失敗時寫入 Fiddler 日誌並提示使用者手動修正。外部 exe 也應加上：1) 日誌與返回碼。2) 前置檢查（權限、路徑）。3) 安全回退（不修改代理或僅追加 Bypass）。此確保失敗不影響 Fiddler 基本功能。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q6, D-Q1, C-Q3

C-Q10: 如何以純 .NET API（不依賴 Fiddler.exe）設定 Proxy？
- A簡: 透過 WinINET 相關 P/Invoke 或登錄機碼操作，更新代理與 Bypass。
- A詳: 在外部程式中可用 WinINET P/Invoke（InternetSetOption 等）或修改使用者層登錄（HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings 與 Connections）更新代理與 Bypass。步驟：讀取→合併→寫回→通知系統。注意：需處理語意細節與系統通知，避免破壞現有設定。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q4, B-Q15, D-Q10

### Q&A 類別 D: 問題解決類（10題）

D-Q1: FiddlerScript 出現「Script compilation error」怎麼辦？
- A簡: 多因缺參考/不可見型別或語法錯誤；減少依賴並檢查語法。
- A詳: 症狀：啟用擷取時彈出腳本編譯錯誤視窗。原因：引用宿主內部型別、未加 using、語法或版本不符。解法：1) 回退只用受支持的 API。2) 移除對 Fiddler 內部類別的直接存取。3) 用外部 exe 承擔變更。預防：將自訂邏輯最小化並加上註解與版本相容測試。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, B-Q6, C-Q3

D-Q2: 腳本可編譯但執行時「type not found」？
- A簡: 動態載入失敗或型別不可見；避免在腳本反射宿主組件。
- A詳: 症狀：Process 啟動前拋出型別解析例外。原因：Assembly.LoadFrom 路徑/相依錯誤、AppDomain 限制、型別非 public。解法：1) 移除腳本內反射，改採外部 exe。2) 若仍需反射，確保完整強名稱與載入脈絡。預防：降低腳本對宿主組件依賴。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, B-Q10, C-Q7

D-Q3: VPN/無線環境下 Fiddler 不抓包怎麼排查？
- A簡: 檢查當前連線代理是否被修改；必要時批次同步設定。
- A詳: 症狀：瀏覽器/應用未經 Fiddler。原因：Fiddler 只改「區域連線」，VPN/無線未改；WPAD/自動偵測干擾。步驟：1) 確認活躍連線。2) 檢查該連線代理是否 127.0.0.1:8888。3) 以外部工具同步設定。預防：在 OnAttach 觸發批量更新，或改用全域 LAN 設定。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q13, C-Q4

D-Q4: 開著 Fiddler 時 TFS Get Latest 失敗怎麼處理？
- A簡: 將 TFS 域名加入 Bypass，或暫停 Fiddler；確認憑證與代理。
- A詳: 症狀：Get Latest/連線逾時或認證失敗。原因：TFS 請求被 Fiddler 攔截、憑證/NTLM 受代理影響、連線走錯 NIC。步驟：1) 將 *.tfs.company.com 加入 Bypass。2) 若需攔截，設定憑證信任。3) 確認正確 NIC 代理。預防：在 OnAttach 自動維護 Bypass，減少手動切換。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, C-Q8, B-Q12

D-Q5: Bypass 字串包含「http://」導致無效如何修正？
- A簡: 移除協定，僅保留主機/網域；使用分號分隔項目。
- A詳: 症狀：已設定 Bypass 但無效。原因：WinINET Bypass 僅接受主機/網域，不含協定與路徑。解法：將「http://tfs.company.com」改為「tfs.company.com」或「*.company.com」。預防：遵循 Bypass 規則，測試每次變更。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q12, C-Q5, A-Q9

D-Q6: Process.Start 找不到 myproxycfg.exe 的解法？
- A簡: 放在 Fiddler 目錄或寫完整路徑；檢查權限與防毒攔截。
- A詳: 症狀：OnAttach 執行但無效果/例外。原因：檔案不在 PATH、相對路徑錯誤、UAC/防毒阻擋。步驟：1) 將 exe 與 Fiddler 同目錄。2) 使用絕對路徑。3) 以 try/catch 顯示錯誤並回傳碼。預防：安裝腳本時一併部署並測試啟動。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q3, C-Q9, B-Q11

D-Q7: 關閉 Fiddler 後 Proxy 未還原怎麼辦？
- A簡: 可能異常終止或外部程式覆寫；手動還原或用工具修復。
- A詳: 症狀：關閉 Fiddler 後仍指向 127.0.0.1。原因：Fiddler 異常退出未寫回、外部 exe 覆蓋設定、群組原則干擾。步驟：1) 手動復原網際網路選項。2) 重啟 Fiddler 啟停一次。3) 用修復工具寫回備份。預防：外部 exe 僅改 Bypass；在 OnDetach 檢查復原。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q13, C-Q6, C-Q9

D-Q8: 反射呼叫 SetToWinINET 擲出安全性例外怎麼辦？
- A簡: 因部分信任/權限不足；改用外部行程或提升信任。
- A詳: 症狀：反射呼叫時拋 SecurityException。原因：腳本 AppDomain 權限不足、組件缺少完全信任。解法：1) 改以外部 exe。2) 若在可控環境，調整信任（不建議）。預防：在擴充點避免敏感 API，將系統層變更移出腳本。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, C-Q7, B-Q5

D-Q9: 變更 Proxy 後 IE/VS 未生效怎麼辦？
- A簡: 需要通知或重啟；檢查使用的連線與快取。
- A詳: 症狀：設定已改但應用仍未走代理。原因：應用快取、未監聽設定變更、使用不同連線。步驟：1) 嘗試關閉重開 IE/VS。2) 清除快取。3) 確認應用使用的連線與 WinINET（非 WinHTTP）。預防：在設定後呼叫系統通知，或引導使用者重啟應用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, B-Q15, C-Q6

D-Q10: 企業策略阻擋修改 Proxy 時怎麼做？
- A簡: 與 IT 協作白名單化工具、改走應用層排除或用測試環境。
- A詳: 症狀：修改被還原或拒絕。原因：群組原則（GPO）鎖定代理、端點防護阻擋外部程式。對策：1) 與 IT 溝通將工具與域名加入白名單。2) 改用 Fiddler 層級排除（若版本支援）。3) 在隔離測試環境進行。預防：遵循變更流程，避免違反政策。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, C-Q10, D-Q6

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 Fiddler？
    - A-Q2: 什麼是 TFS（Team Foundation Server）？
    - A-Q3: 什麼是 WinINET 代理設定？
    - A-Q4: 什麼是 CustomRules.js？
    - A-Q5: 什麼是 OnAttach 事件？
    - A-Q9: 什麼是 sHostsThatBypass（代理例外清單）？
    - A-Q10: 為什麼 Fiddler 與 TFS 會相衝？
    - A-Q13: Fiddler 如何保存與還原 Proxy 設定？
    - B-Q1: Fiddler 啟用擷取的執行流程為何？
    - B-Q2: Fiddler 停用擷取如何還原設定？
    - B-Q12: 代理例外（Bypass）字串的規則為何？
    - C-Q1: 如何在 OnAttach 自動套用代理例外清單？
    - C-Q3: 如何在 CustomRules.js 內呼叫外部 exe？
    - D-Q1: FiddlerScript 出現「Script compilation error」怎麼辦？
    - D-Q4: 開著 Fiddler 時 TFS Get Latest 失敗怎麼處理？

- 中級者：建議學習哪 20 題
    - A-Q6: 什麼是 AppDomain？
    - A-Q7: AppDomain 與 Process 有何差異？
    - A-Q11: 為什麼在 VPN/無線環境 Fiddler 常失效？
    - A-Q12: 何謂每個網路介面卡各自的 Proxy 設定？
    - A-Q14: 方案 A/B/C/D 分別是什麼策略？
    - A-Q15: 修改系統 Proxy 有哪些風險？
    - B-Q3: WinINETProxyInfo 物件的核心組件是什麼？
    - B-Q4: GetFromWinINET 與 SetToWinINET 的機制是什麼？
    - B-Q5: FiddlerScript 的編譯與載入機制如何？
    - B-Q6: 為何在腳本中無法直接參考 Fiddler.WinINETProxyInfo？
    - B-Q7: oProxy、piPrior、piThis 各是什麼？
    - B-Q13: 為何 Fiddler 只改「區域連線」會有影響？
    - B-Q14: AppDomain 隔離與效能的權衡？
    - B-Q15: 多網卡環境的 Proxy 決議流程？
    - C-Q2: 如何建立 myproxycfg.exe 來設定 WinINET Proxy？
    - C-Q4: 如何針對 VPN/無線網卡同步設定 Proxy？
    - C-Q5: 如何使用萬用字元設定 Bypass（*.domain.com）？
    - C-Q6: 如何驗證 Fiddler 啟停時 Proxy 有正確還原？
    - D-Q3: VPN/無線環境下 Fiddler 不抓包怎麼排查？
    - D-Q6: Process.Start 找不到 myproxycfg.exe 的解法？

- 高級者：建議關注哪 15 題
    - B-Q8: 方案 B（參考 Fiddler.exe 當 DLL）的原理？
    - B-Q9: 方案 C（反射載入 + CreateInstance）的流程？
    - B-Q10: 方案 C 仍失敗的可能原因？
    - B-Q11: 方案 D（Process.Start 外部程式）的機制？
    - C-Q7: 如何避免在腳本中取用內部類別而改用反射？
    - C-Q8: 如何將 TFS 網址加入不經代理清單以避免衝突？
    - C-Q9: 如何撰寫容錯：外部 exe 失敗時的處理？
    - C-Q10: 如何以純 .NET API（不依賴 Fiddler.exe）設定 Proxy？
    - D-Q2: 腳本可編譯但執行時「type not found」？
    - D-Q5: Bypass 字串包含「http://」導致無效如何修正？
    - D-Q7: 關閉 Fiddler 後 Proxy 未還原怎麼辦？
    - D-Q8: 反射呼叫 SetToWinINET 擲出安全性例外怎麼辦？
    - D-Q9: 變更 Proxy 後 IE/VS 未生效怎麼辦？
    - D-Q10: 企業策略阻擋修改 Proxy 時怎麼做？
    - A-Q15: 修改系統 Proxy 有哪些風險？