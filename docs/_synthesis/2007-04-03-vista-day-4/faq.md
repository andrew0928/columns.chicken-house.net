---
layout: synthesis
title: "Vista Day 4..."
synthesis_type: faq
source_post: /2007/04/03/vista-day-4/
redirect_from:
  - /2007/04/03/vista-day-4/faq/
postid: 2007-04-03-vista-day-4
---

# Vista Day 4...

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: Windows Vista 帶來了哪些與本文主題最相關的關鍵變化？
- A簡: Vista 同時引入 UAC 提高安全、WPF/WIC 改寫影像管線、輸入法介面調整、工作列工具列行為更動，以及拖放安全限制，導致既有習慣與舊工具（如 PowerToys）相容性受影響。
- A詳: 本文聚焦的 Vista 變化涵蓋五大面向。安全上，User Account Control（UAC）改用「需要時再提權」的模式，防止不經意的危險操作；介面上，工作列工具列（Toolbar/Quick Launch）的拖曳與浮動行為被收斂；輸入上，注音輸入法的候選與編輯行為調整（如 Shift 輸入大小寫、Backspace 清除組字行為）改變多年使用習慣；開發/多媒體上，WPF（Windows Presentation Foundation）結合 WIC（Windows Imaging Component）全面改寫影像處理與編碼/解碼機制，以 Codec 為中心，並引入 HD Photo 格式；整體安全模型（如 UIPI）也影響拖放到 Console 等常用操作。這些改變帶來長期一致性與安全收益，但短期造成工作流斷裂與工具不相容，是升級者最直接的痛點。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, A-Q8, A-Q12, A-Q15, B-Q3, B-Q4

A-Q2: 什麼是 UAC（User Account Control）？
- A簡: UAC 是 Vista 引入的安全機制，預設以標準權限運行程式，必要時以同一帳號短暫提權並提示確認，以降低惡意程式或誤操作造成的系統風險。
- A詳: UAC 的核心理念是最小必要權限（Least Privilege）。即便使用者屬於系統管理員群組，登入後也只拿到受限權限的存取權杖（token）；當應用程式需要執行系統層級操作（寫系統目錄、修改登錄機碼、管理服務等）時，才透過同意/密碼確認將權限提升至完整管理員。此設計避免長期以高權限執行所有程式而放大攻擊面，並配合 UIPI（使用者介面權限隔離）阻斷跨權限的 UI 訊息注入。對一般使用者是顯著的安全進步，對已建立既有腳本與工具鏈的進階使用者，初期會感到頻繁提示的摩擦，需要調整工作流程（例如以排程/捷徑提權、區分日常與管理工作）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q8, B-Q1, B-Q2, B-Q3

A-Q3: 為什麼需要 UAC？它的核心價值是什麼？
- A簡: UAC 落實最小必要權限，降低持續以最高權限執行的風險，透過提權提示讓敏感操作可見、可控，提升整體系統安全衛生。
- A詳: 長年以來，許多 Windows 使用者以 Administrator 身分執行日常工作，導致惡意程式一旦入侵即獲完全控制。UAC 改變此模式：平時用受限權限執行，僅在需要進行敏感操作時才進行提權並提示使用者確認，將「危險時刻」集中、可見化。它也讓應用程式開發者更有動機遵循標準使用者資料資料夾與設定寫入位置，逐步改善軟體生態。核心價值包括：縮小攻擊面、提高使用者對權限敏感度、促進軟體遵循標準、降低整體維運成本。雖然帶來提示疲勞與流程摩擦，但可透過調整習慣與工具（如排程與捷徑提權、權限分離）降低影響。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q8, B-Q1, D-Q4

A-Q4: 什麼是「最小必要權限」（Least Privilege）？
- A簡: 僅給使用者與程式完成當前工作所需的最低權限，減少濫用或被入侵擴大的風險，是現代作業系統安全的基石。
- A詳: 最小必要權限是資訊安全設計準則，要求任何主體（使用者、程序、服務）只擁有完成任務必需的權限，其他權限在必要時以審核與控管的方式暫時賦予。其好處是明顯降低誤操作與漏洞被濫用的後果，並將攻擊行為的橫向移動與縱向升級難度提高。UAC 在 Windows 的設計正體現此原則：平時以標準權限執行，必要時提權並留下審計足跡。類似概念也體現在 Linux/UNIX 的 sudo 與能力（capabilities）管理，或企業環境中的 RBAC（角色存取控制）。對個人工作流而言，將日常使用與管理工作拆分、用 runas/捷徑/排程在需要時提權，是實踐該原則的有效方式。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q3, A-Q8, B-Q2

A-Q5: 什麼是 sudo 與 Windows 的 runas？兩者目的為何？
- A簡: sudo 與 runas 都是在需要時以另一身分執行指令或程式，目的是避免長期以高權限登入，僅在必要時提升權限。
- A詳: sudo（UNIX/Linux）允許一般使用者在經授權的情境下，以 root 或其他指定身分執行特定命令，並可記錄審計、限制可用指令；Windows 的 runas 讓你以另一個本機/網域帳號執行程式，常用於系統工具或 MMC 以管理員身分開啟。兩者都是將「高權限」從日常會話剝離，在需要時才短暫使用，有助於減少安全風險。差異在於整合程度與體驗：sudo 以命令列與 PAM/政策高度整合；runas 偏向手動切換身分。Vista 的 UAC 在此之上增加了系統級的「同一使用者提權」體驗（Admin Approval Mode），讓管理員群組成員不必輸入不同憑證也能在需要時提權，但仍可選擇使用 runas 保持傳統分離。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q10, D-Q4

A-Q6: UAC 與 sudo 有何差異？
- A簡: UAC 是系統層的同帳號提權與 UI 保護，sudo 是以另一身分執行指定命令的權限委派機制；前者強調使用者體驗與整體生態，後者強調授權與審計。
- A詳: UAC 讓管理員群組的使用者在日常以受限權限運作，需要時以同帳號短暫切換到完整權杖；其配套包含 UIPI 阻擋跨權限 UI 注入、虛擬化改善相容、以及一致的同意 UI。sudo 則透過 /etc/sudoers 對「誰能以誰的身分執行哪些命令」進行精細控制，強調最小權限授權與完整審計，通常需要輸入自己的密碼並可設定超時。Windows 也有 runas 可達到「以他人身分」的效果，但不含 UAC 的體驗整合。從使用角度看，UAC 更像「按需提權」的系統工作流；sudo/runas 更像「切換另一身分」的安全授權工具。兩者可互補：日常用 UAC，需強制隔離時用不同帳號/runas。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q1, B-Q10

A-Q7: 什麼是 WPF（Windows Presentation Foundation）？
- A簡: WPF 是 Vista 時代引入的 UI 框架，提供向量化繪圖、資料繫結、多媒體整合，影像處理改以 WIC 作為底層管線，取代傳統 GDI+ 的做法。
- A詳: WPF 是 .NET 圖形子系統，以 XAML 描述 UI、具備向量圖形、動畫、特效、字體與硬體加速（透過 MILCore）等能力。與本文關聯最深的是影像堆疊：WPF 不再使用 GDI+ 的 System.Drawing 為主，而是透過 Windows Imaging Component（WIC）提供統一的解碼、編碼、轉換與顏色管理能力。這讓影像格式的支援採「安裝 Codec 即得」的模式，方便擴充 RAW、HD Photo 等新格式。對開發者而言，這代表舊的 API 與行為（如 PowerToys 的影像 Shell 擴充）可能不再相容，需要改寫至新的物件模型與資料流程。優勢是更現代化、可擴充、色彩與高位元深支援更好；代價是遷移成本與學習曲線。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, A-Q9, B-Q4, B-Q5

A-Q8: 什麼是 WIC（Windows Imaging Component）？
- A簡: WIC 是 Windows 的影像框架，透過可外掛的 Codec 提供解碼/編碼、格式轉換、顏色管理與中繼資料處理，Vista 起成為 WPF/系統影像能力的基礎。
- A詳: WIC 將影像處理標準化為一組 COM 元件：工廠（IWICImagingFactory）、編解碼器（Decoder/Encoder）、格式轉換（FormatConverter）、色彩轉換（ColorContext/Transform）、中繼資料（Metadata Reader/Writer）等。其設計核心是「Codec 即能力」：安裝一個 RAW 或 HD Photo Codec，整個系統（含 WPF、檔案總管、縮圖、預覽）即可支援該格式，還可取得 Exif/廠牌中繼資料與視訊管線中的顏色一致性。相較 GDI+，WIC 支援更高位元深、廣色域與可擴充的格式，並統一 Shell 整合（縮圖、屬性）。對開發者，WIC 讓你以一致 API 使用多格式，減少各家專屬 SDK 的負擔；對使用者，則是安裝廠商 Codec 後即可流暢瀏覽 RAW 等專業格式。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, A-Q9, A-Q11, B-Q4, B-Q5

A-Q9: WIC 與 GDI+（System.Drawing）有什麼差異？
- A簡: GDI+ 著重傳統點陣繪圖與基本解碼；WIC 採 Codec 架構、支援高位元深、色彩管理與中繼資料，並與 WPF/Shell 深度整合，擴充性與一致性更高。
- A詳: GDI+ 提供基本的影像載入/儲存與繪圖功能，但格式支援受限、色彩管理與中繼資料處理較基礎，擴充新格式需要額外程式庫。WIC 以可外掛的 Codec 為中心，讓解碼、編碼、轉換、色彩管理（ICC Profile）與中繼資料有一套一致物件模型；任何支援 WIC 的應用程式（含 WPF）只要系統安裝對應 Codec，即可使用該格式。此外，WIC 對高位元深（16bpc、32bpc 浮點）、廣色域與 RAW 工作流更友善，Shell 也能直接產生縮圖與屬性顯示。對舊專案，轉換到 WIC 可改善一致性與畫質，但需要重構相關模組，特別是從 System.Drawing 轉到 System.Windows.Media.Imaging 的 API 與資源生命週期管理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, A-Q8, B-Q4, B-Q5, B-Q15

A-Q10: 什麼是 HD Photo（Windows Media Photo，後續標準化為 JPEG XR）的目標？
- A簡: HD Photo 旨在提供比 JPEG 更高壓縮效率、畫質與高位元深/廣色域支援，並與 WIC/WPF 一起成為新一代影像格式生態的一部分。
- A詳: HD Photo（Windows Media Photo）是 Microsoft 提出的影像格式，後來標準化為 JPEG XR。其設計目標包括：更佳的壓縮效率（相同檔案大小獲得更佳視覺品質）、高動態範圍（HDR）與高位元深支援、無損與有損編碼模式、以及更完善的中繼資料與色彩管理整合。Vista 透過 WIC/WPF 首度將 HD Photo 納入系統影像管線，並以 Codec 方式提供系統層支援。雖然要取代 JPEG 需時間與生態支持，但在專業攝影、圖像工作流中，HD Photo/JPEG XR 為高品質儲存與編輯提供了可行選項。對開發者，WIC 的一致 API 讓加入 HD Photo 支援的成本顯著降低。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q7, C-Q6

A-Q11: 什麼是 RAW（CRW/CR2/NEF）與 WIC Codec 的關係？
- A簡: 相機 RAW 是各家專有格式；在 Windows，透過安裝該廠牌的 WIC Codec，系統與應用程式即可解碼、顯示縮圖與讀取中繼資料。
- A詳: RAW（如 Canon CRW/CR2、Nikon NEF）保留感光元件的原始資料，提供更大後製彈性，但各家格式封裝與色彩轉換不同。WIC 讓 RAW 支援以「Codec 安裝」實現：一旦安裝對應 Codec，檔案總管可預覽/縮圖，WPF/WIC API 可開啟與處理，屬性系統可顯示拍攝參數。過去需依賴特定應用或不一致的 SDK；Vista 之後改為平台級統一管線，減少開發與使用成本。本文提到 Nikon 已先提供 NEF 的 WIC Codec，Canon 當時尚未釋出，導致依賴舊 PowerToys 或私有 Wrapper 的程式在 Vista 下失效，凸顯遷移到 WIC 的必要性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, A-Q12, B-Q6, D-Q3

A-Q12: 為什麼某些影像 PowerToys（Image Resizer、RAW Image Viewer）在 Vista 不能用？
- A簡: Vista 改用 WPF/WIC 與新的 Shell 架構，舊的 GDI+/Shell 擴充相依與相容性假設失效，加上安全限制，導致部分 PowerToys 停用或行為改變。
- A詳: PowerToys 多以 Shell 擴充與 GDI+ 為基礎，依賴特定的 COM 介面、檔總管行為與影像處理函式。Vista 在三個層面改變了地基：影像堆疊轉移到 WPF/WIC（包含縮圖與預覽）；Shell 屬性系統與中繼資料介面（IPropertySystem 等）重構；UAC/UIPI 引入新的安全界線，限制跨程序/跨權限的 UI 與檔案操作。這些變動讓原本設計針對 XP 的擴充無法直接運作或需要重簽名/重寫碼。實務上，應尋找為 Vista 及以後版本更新的替代工具，或以 WIC 重寫功能，以獲得更一致與安全的系統整合。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, B-Q14, D-Q2

A-Q13: 什麼是 ALT+數字鍵輸入 ASCII/Unicode？為何在某些情境失效？
- A簡: ALT+數字鍵可輸入代碼字元；但在特定輸入法的組字/選字狀態或新 IME 行為下可能被攔截，導致看似「無效」。
- A詳: ALT+數字鍵（俗稱 Alt code）在 Windows 可輸入 ASCII（十進位）或 Unicode 碼位的字元，需啟用 Num Lock 並使用數字鍵台。當前景輸入元件為 IME 且處於組字/選字狀態時，鍵盤事件先被 IME 處理，可能不再傳遞給系統層的 Alt code 解譯器；部分 IME 設定或模式也會變更 Shift/Alt 按鍵行為。Vista 的注音 IME 調整組字與選字流程，造成使用者長年養成的 Alt code 流程失靈。常見解法是短暫切回英數模式、使用「複製為路徑/字元對照表」或調整 IME 屬性，避免在組字期使用 Alt code，以降低衝突。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q14, D-Q6, C-Q9

A-Q14: Vista 的注音輸入法改了哪些與以往不同？
- A簡: 候選顯示與組字行為調整、Shift 在中文模式輸入為大寫、Backspace 不再中止選字、Alt code 輸入在組字期失效，整體體驗與舊版差異明顯。
- A詳: 本文點出四個關鍵差異：（1）最陽春的注音模式不再提供底部一列候選的舊式視覺；（2）中文模式下按住 Shift 輸入英文字母預設為大寫，影響舊習慣；（3）處於選字/組字狀態（候選下有虛線）時，Backspace 不能像過去那樣取消整段組字；（4）在組字過程中，ALT+數字鍵的代碼輸入可能被 IME 攔截。這些設計旨在一致化輸入體驗與國際化，但對重度使用者，初期會有顯著摩擦。可透過熟悉新的取消鍵（如 Esc）、調整 IME 選項、或快速切換英/中輸入來降低影響。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q13, B-Q11, B-Q12, D-Q5, D-Q8

A-Q15: 為什麼在 Console 視窗中拖放檔案會失效或沒有反應？
- A簡: Vista 引入 UIPI 與權限分隔，從較低權限的 Explorer 拖放到較高權限（提權）的 Console 會被阻擋；或應用未註冊接受拖放事件。
- A詳: 拖放需要來源與目標視窗位於相容的權限完整性層級。Vista 的 UAC/UIPI 阻擋跨完整性（如標準 Explorer → 提權 Console）的訊息傳遞，避免以拖放繞過安全界線。過去在 XP 以管理員登入時不會遇到這個限制，升級後便感覺「無法再拖放」。此外，Console 視窗是否有註冊接受拖放（如處理 WM_DROPFILES 或 OLE DnD）也影響結果。解法包括：在未提權的 Console 中操作、用「在此開啟命令視窗」避免長路徑、使用「複製為路徑」搭配貼上、或設計工作流避免跨權限拖放。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q9, D-Q1, C-Q2, C-Q3

---

### Q&A 類別 B: 技術原理類

B-Q1: UAC 在內部如何運作？
- A簡: UAC 透過「分裂權杖」與 Admin Approval Mode，預設以受限權杖運行，提權時切換到完整權杖，並以同意 UI 管控高權限操作。
- A詳: 當使用者屬於 Administrators 群組登入時，系統建立兩個權杖：受限權杖（移除危險權限、低完整性）與完整權杖。預設所有程序以受限權杖啟動；當程式宣告需要管理權（manifest 要求）或觸發需提權操作時，UAC 啟動同意 UI（consent/credential prompt），獲得使用者同意後以完整權杖建立新進程。這配合檔案/登錄虛擬化（在某些情境給舊程式臨時寫入重定向），以及完整性等級與 UIPI（阻擋跨權限 UI 訊息）構成完整護欄。優點是縮小攻擊面，缺點是提示疲勞與相容性摩擦。開發者需正確標示應用程式 manifest，區分標準/管理需求，避免不必要提權。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q2, A-Q3, B-Q2, B-Q3

B-Q2: 什麼是 Admin Approval Mode（AAM）的執行流程？
- A簡: AAM 讓管理員預設以受限權杖運行，必要時彈出同意對話；同意後以完整權杖啟動目標程式，並隔離與原進程的互動。
- A詳: 流程包括：（1）使用者登入建立雙權杖；（2）啟動程式時檢查其 manifest 與行為（如寫入保護目錄）判定是否需提權；（3）如需提權，觸發安全桌面的同意視窗；（4）同意後，由 AppInfo 服務建立以完整權杖運行的新進程；（5）為避免權限混淆，低完整性進程無法向高完整性進程注入訊息（UIPI），拖放與全域掛鉤受限。此流程確保高權限僅在必要範圍與時間內存在，並以可見化的方式讓使用者做出授權決策。企業可用群組原則微調提示策略（例如對管理員靜默提權，或強制輸入憑證）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q3, D-Q4

B-Q3: UIPI（使用者介面權限隔離）如何阻擋拖放與訊息注入？
- A簡: UIPI 依完整性等級限制跨進程 UI 訊息，低完整性無法向高完整性傳送敏感訊息，因而阻擋拖放、模擬輸入與掛鉤注入。
- A詳: Windows 引入完整性等級（低、中、高、系統）標記事件與進程。UIPI 規定進程只能向相同或更低完整性等級的視窗投遞 UI 訊息與 OLE 互動；因此當 Explorer（中等）嘗試向提權 Console（高等）發起拖放，訊息會被過濾。這阻止惡意程式透過 UI 自動化/注入操控高權限程序。實作上，系統維護允許清單（如少數無害訊息）與封鎖清單（如鍵盤/滑鼠注入），開發者需遵守設計：避免設計仰賴跨權限 UI 互動的工作流，改用明確 IPC 或重新設計提權/非提權邊界。使用者端的對策是避免跨權限拖放，或使用替代操作（複製為路徑、在此開啟命令視窗）。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q15, B-Q9, D-Q1

B-Q4: WPF 影像管線如何透過 WIC 工作？
- A簡: WPF 呼叫 WIC 的解碼/編碼/轉換元件，取得像素緩衝與色彩資訊，再交由 MILCore 渲染；安裝 Codec 即可擴充格式支援。
- A詳: 當 WPF 載入影像（BitmapImage/BitmapFrame）時，內部透過 WIC 的 IWICImagingFactory 建立對應 Decoder（依檔頭/副檔名），解出像素格式與中繼資料；必要時以 IWICFormatConverter 轉換到渲染支援的像素格式，並可透過 ColorContext/Transform 做色彩轉換。渲染階段，MILCore 將像素交給 GPU/CPU 管線，支援縮放、旋轉、透明與特效。儲存時則用對應 Encoder（如 Png/Jpeg/HDP）。這種設計讓系統影像能力一致、可擴充，檔總管縮圖/預覽與應用程式共用同一組解碼器與屬性系統。對開發者，代表以 System.Windows.Media.Imaging 而非 System.Drawing 為主要 API，並考慮位元深與色彩管理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, A-Q8, A-Q10, B-Q5

B-Q5: WIC 的核心組件有哪些？關鍵流程如何設計？
- A簡: 主要有 ImagingFactory、BitmapDecoder/Encoder、BitmapFrame、FormatConverter、ColorContext/Transform、Metadata Reader/Writer；流程是解碼→轉換→處理→編碼。
- A詳: WIC 以 COM 物件組裝影像流程。IWICImagingFactory 建立各元件；IWICBitmapDecoder 讀取來源串流，產生一或多個 IWICBitmapFrameDecode；可用 IWICFormatConverter 將像素格式轉到渲染/處理所需格式；色彩管理透過 IWICColorContext 與 IWICColorTransform 轉換到目標色域；IWICMetadataQueryReader/Writer 可讀寫 Exif/XMP/廠商自定中繼資料。處理完成後以 IWICBitmapEncoder 與對應 Frame 寫出。WIC 還定義了 Component Categories 用以註冊第三方 Codec 與轉換器，讓 Shell/WPF/應用自動發現。這種管線化設計提升可測試性與擴充性，解耦資料來源、格式與渲染目標。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q8, B-Q4, C-Q5, C-Q6

B-Q6: RAW WIC Codec 如何與 Shell/屬性系統整合？
- A簡: RAW Codec 提供解碼與縮圖，同時掛接屬性與中繼資料處理，讓檔總管能預覽、顯示參數並供應用程式讀取 RAW。
- A詳: 安裝 RAW Codec 後，系統在 WIC Component Categories 註冊該解碼器，Shell 利用它生成縮圖與預覽；同時，透過 IPropertyStore 與 IPropertyDescription 等介面提供拍攝參數（曝光、ISO、鏡頭等）給屬性面板與搜尋索引。應用程式（WPF/WIC）可用 Decoder 開啟 RAW 並選擇解出預覽 JPEG 或經廠商轉換後的線性/場景參照像素。這種整合讓全系統一致支援 RAW，而不需個別應用整合各家 SDK。限制在於不同廠商對解碼參數與色彩詮釋差異，需依 Codec 提供的能力運用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, D-Q3, C-Q4, C-Q5

B-Q7: HD Photo/JPEG XR 的壓縮原理（高階）是什麼？
- A簡: 採用基於轉換的壓縮（如 LPC 轉換/變換）、可選無損/有損模式、支持高位元深與區塊內預測，提升效率與畫質。
- A詳: 與 JPEG 的 DCT 區塊壓縮不同，HD Photo/JPEG XR 採用整數化轉換與可逆/不可逆選項，支援 16bpc 與浮點，並在色彩子抽樣與通道分離上更彈性。其區塊內預測與量化設計改善低頻/高頻資訊保留，在同等檔案大小下提供更佳視覺品質，或在相同品質下減少檔案大小。格式亦支援無損編碼，適合高動態範圍與後製工作流。為兼顧系統整合，WIC 提供標準化解碼/編碼器，讓應用不必直接面對壓縮細節。雖然普及取決於生態與相容性，但在 Windows 管線中可無縫使用。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q10, C-Q6

B-Q8: GDI+ 與 WIC/WPF 在色彩管理與畫質上的差異？
- A簡: WIC/WPF 對 ICC 色彩、廣色域與高位元深支援完整，渲染管線現代化；GDI+ 支援有限，易受限於 8bpc 與較簡單的轉換。
- A詳: GDI+ 雖可處理部分 ICC Profile，但在高位元深與色彩一致性上設計較舊，且與 Shell/預覽不共用同一解碼器，導致應用間顏色不一致。WIC 統一解碼與色彩轉換 API，支援 16bpc/32bpc、浮點像素與對應 Profile；WPF 渲染管線（MILCore）在轉場、縮放與濾鏡處理時更能保留細節，減少 banding（階調斷層）。因此，在專業影像工作流中，使用 WIC/WPF 能獲得更一致且高品質輸出。代價是需要更新應用架構並正確管理色彩（載入/轉換/輸出時的 Profile）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q4, B-Q5

B-Q9: Console 拖放的技術流程與 Vista 的改變是什麼？
- A簡: 傳統用 WM_DROPFILES 或 OLE DnD 通知目標視窗；Vista 加入完整性等級與 UIPI，跨權限拖放被阻擋，導致「無反應」的表象。
- A詳: 拖放流程：來源建立資料物件（IDataObject），目標視窗註冊接受拖放（DragAcceptFiles/OLE RegisterDropTarget），操作過程透過 UI 訊息/OLE 回呼傳遞。XP 時期幾乎不考慮跨權限隔離；Vista 引入 UIPI 與完整性等級，低權限來源不得向高權限目標投遞事件。此外，Console 主機在 Vista 的實作與訊息處理亦更保守，進一步限制某些互動。解法是避免跨權限拖放（改用未提權 Console、在此開啟命令視窗、或複製為路徑），或採用具名管道/命令列參數等明確 IPC。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q15, B-Q3, D-Q1, C-Q2, C-Q3

B-Q10: Windows 的 runas 技術架構是什麼？
- A簡: 由 Secondary Logon Service 處理，以指定帳號建立新進程，載入對應使用者設定與權杖，與原進程隔離。
- A詳: runas 會透過 Secondary Logon Service（seclogon）呼叫 LSA 授權，為目標帳號建立登入工作階段與存取權杖，然後以該權杖建立新進程，環境變數、網路身分、使用者設定皆獨立於原會話。這不同於 UAC 的同帳號提權：runas 是完全換身分，適合需要嚴格隔離的管理操作或存取不同網路資源（如不同網域）。限制包括：UI 整合較弱、剪貼簿/拖放跨身分可能受限。可搭配憑證管理員、捷徑或批次檔簡化使用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, A-Q6, D-Q4

B-Q11: Vista 注音 IME 的組字與選字機制背後機制是什麼？
- A簡: 透過 IME 組字狀態機管理緩衝、候選與確認，鍵盤事件先由 IME 攔截處理，再決定是否上送應用或系統。
- A詳: IME 於 TSF（Text Services Framework）之上，維持「組字中」「候選」「已確認」等狀態。鍵盤事件（含 Shift/Alt、Backspace）先由 IME 解讀：在組字/候選狀態時，按鍵多半操作組字緩衝或候選移動而非直接送入應用程式。Vista 注音 IME 調整了 Shift 在中文模式時的字母大小寫預設、Backspace 對組字的影響、候選 UI 呈現等，故使用者感受不同。正確理解：取消組字常用 Esc、Ctrl+Backspace 或清空緩衝，而非傳統直接 Backspace。這種設計優勢是行為一致與多語整合，但需要重新建立肌肉記憶。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, D-Q8, C-Q9, C-Q10

B-Q12: Backspace 與 Esc 在 IME 狀態機中各扮演什麼角色？
- A簡: Backspace 多數情況刪除組字緩衝內最後一個音/碼；Esc 常用來取消整段組字/候選，回到未組字狀態。
- A詳: 在組字狀態中，Backspace 通常回退一個輸入碼（如注音符號或拼音字母），維持在 IME 緩衝內；當進入候選狀態（顯示候選詞）時，Backspace 的行為可能因 IME 設計不同而不會「退出」候選，而是回退碼；Esc 則多被定義為放棄本次組字，將緩衝與候選一併取消並返回直接輸入狀態。Vista 調整後，一些使用者過往「Backspace 取消」的習慣不再成立，需改用 Esc 或 IME 指定快捷鍵。理解這一點可避免在即時應用（例如遊戲聊天）中卡住輸入焦點。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q14, D-Q8, C-Q10

B-Q13: 為何 Windows Explorer 難以「以系統管理員身分」完整執行？
- A簡: Explorer 採單一殼層進程與桌面整合，為維持穩定與一致體驗，預設不支援以高完整性啟動主要殼層。
- A詳: Explorer 是桌面殼層與檔案總管的宿主，預設採單一實例與整合 COM 物件模式。若讓主要 Explorer 以高完整性執行，將破壞許多應用與殼層之間的互動假設（例如拖放、Shell 擴充），也會讓低完整性應用無法與桌面互動。Vista 起因此不鼓勵也不提供直接「提升整個 Explorer」的方式，而是將提權局限在需要的管理工具或子進程。可行替代是啟用「分離進程」開資料夾、使用其他檔案管理器以管理員身分執行，或透過專門工具執行特定操作。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q3, D-Q1, D-Q4

B-Q14: PowerToys 的 Shell 擴充在 Vista 為何容易失效？
- A簡: Vista 重構屬性系統與安全界線，許多舊 COM 介面與假設（權限、Explorer 行為、GDI+）不再成立，需更新介面與簽名。
- A詳: XP 年代常見的 IColumnProvider、舊式中繼資料存取、以及對 Explorer/影像堆疊的假設在 Vista 發生變動：IPropertySystem 取代舊模型，影像解碼交由 WIC，UAC/UIPI 限制跨權限互動，64 位環境也要求相容性。未更新的 Shell 擴充（含 PowerToys）在載入時可能被封鎖、找不到依賴 API、或在新安全上下文下無法存取目的地資源。解法是在新 SDK 下重編譯並採新介面、簽署元件、遵循最小權限原則，或改以 WIC/WPF 重寫功能。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, C-Q10, D-Q2

B-Q15: 從 GDI+ 遷移到 WIC/WPF 的設計步驟為何？
- A簡: 盤點格式與流程→以 WIC 重構解碼/編碼/轉換→改用 System.Windows.Media.Imaging→處理色彩/中繼資料→測試相容與效能。
- A詳: 遷移策略：（1）盤點現有影像處理路徑（載入、轉存、效果、縮圖、中繼資料）；（2）以 WIC 對應每步的組件（Decoder、Converter、Color Transform、Metadata）建立新管線；（3）在 .NET 採 System.Windows.Media.Imaging（BitmapImage、BitmapFrame、BitmapEncoder/Decoder）取代 System.Drawing；（4）加入 ICC Profile 管理與高位元深處理；（5）整合 Shell（縮圖/屬性）與目標格式（含安裝第三方 RAW Codec）；（6）效能與記憶體測試，針對大圖與多核/硬體加速調整；（7）逐步淘汰舊函式，保留相容層以利過渡。這能獲得一致的格式支援與畫質，並貼合 Vista 之後的生態。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q4, B-Q5, C-Q5, C-Q6

---

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 在 Vista 如何啟用 Quick Launch 並調整工作列以貼近舊習慣？
- A簡: 右鍵工作列→工具列→勾選快速啟動；解除鎖定以調整位置與寬度，雖難以「拉出浮動工具列」，但可配置多列與位置。
- A詳: 實作步驟：（1）右鍵工作列，取消「鎖定工作列」；（2）選 工具列→快速啟動；（3）拖曳分隔線調整寬度與位置，亦可將工作列高度拉成兩列放更多圖示；（4）完成後再鎖定工作列。注意事項：Vista 收斂了「浮動工具列/deskband」能力，難以像 XP 那樣脫離工作列獨立浮動；可改以多列工作列、鍵盤快捷與固定到工作列取代。最佳實踐：保持圖示精簡、以群組/資料夾捷徑分類常用工具，並善用 Win+數字快速啟動。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: D-Q9, A-Q1

C-Q2: 如何避免在 Console 輸入長路徑？（在此開啟命令視窗）
- A簡: 使用 SHIFT+右鍵在資料夾空白處選「在此開啟命令視窗」，直接以該路徑啟動 cmd，避免手輸入或拖放。
- A詳: 步驟：（1）在檔案總管定位至目標資料夾；（2）於空白處按住 Shift 右鍵，選「在此開啟命令視窗」；（3）cmd 以該路徑為工作目錄啟動。注意：避免提權狀態與 Explorer 權限不一致導致拖放受限。最佳實踐：將此功能加入日常流程；如需提權命令提示字元，可先啟動提權 cmd 再手動切換路徑，或建立捷徑批次檔自動切換。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q15, D-Q1, C-Q3

C-Q3: 如何用「複製為路徑」與引號技巧取代拖放到 Console？
- A簡: SHIFT+右鍵檔案→複製為路徑，貼到 Console；包含引號可處理含空白的路徑，避免拖放被 UIPI 阻擋。
- A詳: 步驟：（1）在檔案總管選取檔案/資料夾；（2）Press Shift 並右鍵→選「複製為路徑」；（3）在 Console 貼上，即可得到含引號的完整路徑。注意：含空白的路徑需以引號包裹；若未使用該功能，可手動輸入引號。最佳實踐：建立簡短別名（DOSKEY）或使用批次/PowerShell 函式處理常用目錄；避免跨權限拖放造成無反應。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q15, B-Q3, D-Q1

C-Q4: 如何在 Vista 安裝 WIC RAW Codec 以支援 NEF/CR2？
- A簡: 從相機廠商下載對應的 WIC RAW Codec 套件安裝；重新啟動檔案總管後，縮圖、預覽與 WPF 應用即可支援該 RAW。
- A詳: 步驟：（1）前往官方網站（如 Nikon、Canon）下載針對 Vista 的 RAW Codec；（2）關閉相關應用程式並安裝；（3）重新啟動檔案總管/系統；（4）驗證：資料夾視圖顯示縮圖、屬性頁顯示拍攝資訊、WPF/WIC 成功開啟。注意：64 位系統需對應 64 位 Codec；不同代 RAW（CRW/CR2）需相容版本；安裝來源務必可信。最佳實踐：維持 Codec 更新、為舊機型考慮轉 DNG 的工作流備援。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, D-Q3, C-Q5

C-Q5: 如何用 .NET/WPF/WIC 讀取 RAW 並轉存為 PNG？
- A簡: 使用 BitmapDecoder 載入 RAW（取決於 Codec），取得第一個 Frame，透過 PngBitmapEncoder 儲存為 PNG。
- A詳: 實作步驟（C# WPF）：
  - var uri = new Uri(path);
  - var dec = BitmapDecoder.Create(uri, BitmapCreateOptions.PreservePixelFormat, BitmapCacheOption.OnLoad);
  - var frame = dec.Frames[0];
  - var enc = new PngBitmapEncoder(); enc.Frames.Add(BitmapFrame.Create(frame));
  - using (var fs = File.Create(outPath)) enc.Save(fs);
  注意事項：需先安裝對應 RAW Codec；使用 OnLoad 避免檔案鎖定；若需色彩校正，讀取 ColorContexts 並進行轉換。最佳實踐：處理大型影像時避免一次性載入全部像素；必要時以 TransformedBitmap 降採樣後再輸出。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q5, C-Q4

C-Q6: 如何將 HD Photo（.wdp/.hdp）轉為 JPEG（WIC）？
- A簡: 用 WIC Decoder 讀取 WDP Frame，再以 JpegBitmapEncoder 輸出，設定 QualityLevel 控制品質。
- A詳: 步驟（C# WPF）：
  - var dec = BitmapDecoder.Create(new Uri(inPath), BitmapCreateOptions.None, BitmapCacheOption.OnLoad);
  - var frame = dec.Frames[0];
  - var enc = new JpegBitmapEncoder { QualityLevel = 92 };
  - enc.Frames.Add(BitmapFrame.Create(frame));
  - using (var fs = File.Create(outPath)) enc.Save(fs);
  注意：色彩空間與位元深差異可能影響外觀；必要時先以 FormatConvertedBitmap 轉 24bpp BGR。最佳實踐：保留原始 WDP 備份；針對批次轉檔，控制執行緒與 I/O 以避免 UI 卡頓。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q7, B-Q5

C-Q7: 如何為需要管理權的腳本建立「一鍵提權」捷徑，降低 UAC 打擾？
- A簡: 透過工作排程程式建立「以最高權限執行」的工作，為其建立捷徑，點擊捷徑即以提權方式執行腳本。
- A詳: 步驟：（1）開啟排程工具（taskschd.msc）；（2）建立基本工作→動作執行你的腳本（wscript/cscript/powershell）；（3）勾選「以最高權限執行」；（4）建立捷徑指向 schtasks /run /tn "你的工作名"；（5）將捷徑固定到工作列。注意：首次建立仍需同意；之後觸發工作時提示減少。最佳實踐：簽署腳本、明確輸入/輸出路徑，避免寫入保護目錄；區分「需提權」與「不需提權」腳本。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q4, B-Q2

C-Q8: 如何合理調整 UAC 原則以降低提示頻率？
- A簡: 透過本機安全性原則調整管理員的提示行為，或將常用高權限工具改為集中提權，避免頻繁觸發。
- A詳: 步驟：（1）開啟 secpol.msc→本機原則→安全性選項；（2）調整「使用者帳戶控制」相關項，如「對系統管理員的提升提示行為」選「不提示，直接提升」（視需求）；（3）避免將標準使用者關閉 UAC；（4）將需管理權的操作集中在少數工具（MMC、特定腳本），其他維持標準權限。注意：降低提示會降低可見性，企業應以群組原則控管。最佳實踐：維持 UAC 開啟、減少不必要提權、清楚區隔工作流。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, B-Q2, D-Q4, C-Q7

C-Q9: 如何調整注音 IME 設定，改善 Shift 與選字體驗？
- A簡: 開啟語言列的注音屬性，調整英/中切換、Shift 行為與候選顯示；並熟悉 Esc 取消組字的快捷鍵。
- A詳: 步驟：（1）右鍵語言列→設定→選取注音→內容；（2）檢視「中英切換」「Shift/Space 行為」「全形/半形」等選項，調整符合習慣；（3）在應用中測試：中文模式下再按 Shift 是否仍為大寫，是否可改用 Ctrl+Space 快速切換；（4）練習 Esc/CTRL+Backspace 取消組字。注意：不同版本 IME 選項略異；部分行為（如 Backspace 取消）可能無法完全回復舊版。最佳實踐：統一常用快捷，避免在組字期混用 Alt code。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q14, B-Q11, B-Q12, D-Q7, D-Q8

C-Q10: Vista 找不到 Image Resizer/RAW Viewer，如何替代？
- A簡: 採用支援 Vista 的第三方替代（如新版 Image Resizer 工具）、或以 WIC/WPF 自建簡易批次轉檔/縮圖工具。
- A詳: 方法一：尋找支援 Vista 的 Shell 擴充或獨立應用（注意 32/64 位相容與簽名），安裝後測試右鍵功能是否正常。方法二：以 WPF/WIC 建立簡單 GUI/命令列工具，使用 BitmapDecoder/Encoder 與 TransformedBitmap 實作縮放與轉檔。注意：Shell 擴充需符合新安全/屬性系統介面，避免未簽名元件；自建工具則掌控更穩定。最佳實踐：將影像工作流集中在可維護的工具與腳本，減少依賴過時 PowerToys。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q14, C-Q5, C-Q6

---

### Q&A 類別 D: 問題解決類（10題）

D-Q1: 無法將檔案拖放到 Console，怎麼辦？
- A簡: 多因跨權限（UIPI）阻擋或目標未註冊拖放。用未提權 Console、Shift+右鍵「在此開啟命令視窗」、或「複製為路徑」替代。
- A詳: 症狀：將檔案從檔案總管拖到 Console 無反應。可能原因：（1）Console 已提權，Explorer 未提權，UIPI 阻擋跨完整性拖放；（2）Console 未註冊拖放事件。解決：避免跨權限操作（在未提權 Console 進行）、使用 Shift+右鍵在資料夾「在此開啟命令視窗」、或在檔案按 Shift+右鍵「複製為路徑」後貼上。預防：建立固定工作流（捷徑/批次）減少臨時拖放；僅在必要時提權 Console，並將提權工作與一般工作分流。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q15, B-Q3, B-Q9, C-Q2, C-Q3

D-Q2: PowerToys 的 Image Resizer/RAW Viewer 在 Vista 不能用，如何處理？
- A簡: 因架構/安全相容性改變導致失效。改裝支援 Vista 的替代工具或用 WIC 重建流程。
- A詳: 症狀：右鍵沒有條目、或執行失敗。原因：Vista 改為 WPF/WIC、Shell 屬性系統重構、UAC 限制使舊擴充無法載入或權限不足。解決：改用相容的替代工具（確認 32/64 位）、或自行開發 WIC 基礎的批次縮圖/轉檔工具；必要時移除舊擴充避免衝突。預防：升級前盤點依賴的 Shell 擴充，優先尋找新版或改為應用層工具，降低對舊 PowerToys 的依賴。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, B-Q14, C-Q10

D-Q3: RAW 縮圖/預覽在 Vista 不顯示，如何修復？
- A簡: 安裝相機廠商的 WIC RAW Codec；確認版本/位元數相符，重啟檔案總管；或以相容格式（如 DNG）做過渡。
- A詳: 症狀：CR2/NEF 僅顯示通用圖示、無縮圖/預覽。原因：系統未安裝對應 RAW Codec。解決：下載並安裝相機廠商提供的 Vista 版 Codec（對應 32/64 位），關閉再開檔案總管或重啟；檢查屬性頁是否顯示拍攝參數。若無官方支援，可考慮轉檔為 DNG 或以第三方瀏覽器。預防：維持 Codec 更新，選購設備前確認生態支援；建立轉檔備援流程。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, B-Q6, C-Q4, C-Q5

D-Q4: UAC 提示太頻繁，怎麼在不關閉 UAC 的前提下改善？
- A簡: 集中高權限操作、使用排程捷徑提權、調整本機安全性原則降低提示、區分日常與管理工作。
- A詳: 症狀：常見同意視窗干擾工作。原因：過多動作需寫系統目錄/登錄、或工具未標示需求導致頻繁提權。解決：將需提權操作集中（如 MMC/腳本），用排程建立「以最高權限」捷徑；透過 secpol.msc 調整管理員提示行為（視版本/策略）；教育自己與團隊分離日常帳號與管理任務。預防：選用不需提權的工具與安裝位置；在開發時正確標記 manifest，避免不必要提權；保留 UAC 啟用以維持安全。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, B-Q2, C-Q7, C-Q8

D-Q5: 找不到注音 IME 舊版「底下一排候選」的模式，如何適應？
- A簡: Vista 改版候選 UI，無法回復舊樣式；熟悉新候選操作、快捷鍵與屬性設定以降低摩擦。
- A詳: 症狀：候選顯示方式不同、選字不順。原因：Vista 注音 IME 調整候選 UI 與組字流程。解決：開啟 IME 屬性調整候選顯示/排序；練習以數字鍵選詞、方向鍵移動、Esc 取消；必要時評估第三方輸入法。預防：在需要高節奏輸入（如遊戲）前先熟悉新快捷；避免在組字期間觸發外部快捷造成卡鍵。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q14, B-Q11, C-Q9, C-Q10

D-Q6: ALT+數字鍵輸入逗號等字元在中文模式失效，如何解決？
- A簡: 在組字期 IME 攔截 Alt code。先切換英數、使用「字元對照表」、或預先片語替代；避免於組字期輸入 Alt code。
- A詳: 症狀：按 ALT+4 等無反應。原因：IME 在組字/候選狀態拋棄或改寫鍵盤事件。解決：先切換到英數模式（Ctrl+Space），再輸入 Alt code；或用「字元對照表」（charmap.exe）複製貼上；建立自動替代（AutoHotkey/片語工具）。預防：調整輸入習慣，在中文輸入時用標點鍵或 IME 內建標點；將常用符號加入快捷片語。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q13, C-Q9

D-Q7: 在中文模式按住 Shift 輸入都是大寫，如何打小寫？
- A簡: 這是新版預設。可改用 Ctrl+Space 暫時切英數、或在 IME 屬性調整 Shift 行為；或使用 Caps Lock 管理大小寫。
- A詳: 症狀：中文模式下需打小寫英文卻變大寫。原因：IME 將 Shift 定義為暫時大寫。解決：快速切換英數（Ctrl+Space）打完再切回；檢查 IME 屬性是否提供 Shift 行為選項；或以 Caps Lock 控制當前大小寫狀態。預防：在需要混打英文的情境（程式碼、命令列）優先使用英數模式；建立固定快捷習慣減少誤輸入。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q14, C-Q9

D-Q8: 在選字狀態 Backspace 無法取消組字，怎麼辦？
- A簡: 使用 Esc 或 IME 定義的取消快捷（如 Ctrl+Backspace）離開組字狀態，或改成先確定再刪除。
- A詳: 症狀：候選中按 Backspace 無法退出，甚至卡住其他操作。原因：Backspace 在組字/候選期被 IME 解讀為回退輸入碼。解決：用 Esc 取消整段組字；或試 Ctrl+Backspace（視 IME 設定）；在不能取消時先確認輸入再用 Backspace 刪除已上屏字元。預防：熟悉 IME 的取消/清空快捷；在高即時性情境避免長串組字。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q14, B-Q12, C-Q10

D-Q9: 無法將工作列工具列「拉出」成獨立浮動列，有替代嗎？
- A簡: Vista 收斂浮動工具列。以多列工作列、快速啟動、固定捷徑或第三方 Dock 取代。
- A詳: 症狀：嘗試拖曳工具列脫離工作列失敗。原因：Vista 移除/限制 deskband 浮動行為以提升穩定與一致性。解決：將工作列高度拉高、啟用快速啟動、將常用捷徑固定；或使用可信第三方 Dock 工具（注意相容與資源佔用）。預防：避免仰賴不被系統長期支援的操作模式；以鍵盤快捷補強效率。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, A-Q1

D-Q10: 自寫腳本常被安全軟體/系統阻擋或被 UAC 打斷，如何穩定執行？
- A簡: 簽署與白名單腳本、分離需提權的部分、用排程一鍵提權、避免寫入保護路徑，降低誤判與提示。
- A詳: 症狀：執行時彈出安全警告或 UAC；被防毒誤判為風險。原因：腳本操作檔案系統/登錄、未簽名、放在受保護位置。解決：將需提權操作獨立成腳本並以排程「最高權限」觸發；將可在使用者範圍完成的操作移出「Program Files/Windows」；為腳本簽章與設白名單；調整防毒排除。預防：遵循最小權限、规范安裝與資料寫入位置；定期檢視腳本權限需求與回報資訊。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q7, C-Q8, B-Q1, B-Q2

---

### 學習路徑索引

- 初學者：建議先學習哪 15 題
    - A-Q1: Windows Vista 帶來了哪些與本文主題最相關的關鍵變化？
    - A-Q2: 什麼是 UAC（User Account Control）？
    - A-Q3: 為什麼需要 UAC？它的核心價值是什麼？
    - A-Q4: 什麼是「最小必要權限」（Least Privilege）？
    - A-Q7: 什麼是 WPF（Windows Presentation Foundation）？
    - A-Q8: 什麼是 WIC（Windows Imaging Component）？
    - A-Q11: 什麼是 RAW（CRW/CR2/NEF）與 WIC Codec 的關係？
    - A-Q12: 為什麼某些影像 PowerToys 在 Vista 不能用？
    - A-Q13: 什麼是 ALT+數字鍵輸入 ASCII/Unicode？為何在某些情境失效？
    - A-Q14: Vista 的注音輸入法改了哪些與以往不同？
    - A-Q15: 為什麼在 Console 視窗中拖放檔案會失效或沒有反應？
    - C-Q1: 在 Vista 如何啟用 Quick Launch 並調整工作列以貼近舊習慣？
    - C-Q2: 如何避免在 Console 輸入長路徑？（在此開啟命令視窗）
    - C-Q3: 如何用「複製為路徑」與引號技巧取代拖放到 Console？
    - D-Q1: 無法將檔案拖放到 Console，怎麼辦？

- 中級者：建議學習哪 20 題
    - A-Q5: 什麼是 sudo 與 Windows 的 runas？兩者目的為何？
    - A-Q6: UAC 與 sudo 有何差異？
    - A-Q9: WIC 與 GDI+（System.Drawing）有什麼差異？
    - A-Q10: 什麼是 HD Photo（Windows Media Photo，後續標準化為 JPEG XR）的目標？
    - B-Q1: UAC 在內部如何運作？
    - B-Q2: 什麼是 Admin Approval Mode（AAM）的執行流程？
    - B-Q4: WPF 影像管線如何透過 WIC 工作？
    - B-Q5: WIC 的核心組件有哪些？關鍵流程如何設計？
    - B-Q6: RAW WIC Codec 如何與 Shell/屬性系統整合？
    - B-Q8: GDI+ 與 WIC/WPF 在色彩管理與畫質上的差異？
    - C-Q4: 如何在 Vista 安裝 WIC RAW Codec 以支援 NEF/CR2？
    - C-Q5: 如何用 .NET/WPF/WIC 讀取 RAW 並轉存為 PNG？
    - C-Q6: 如何將 HD Photo（.wdp/.hdp）轉為 JPEG（WIC）？
    - C-Q7: 如何為需要管理權的腳本建立「一鍵提權」捷徑，降低 UAC 打擾？
    - C-Q8: 如何合理調整 UAC 原則以降低提示頻率？
    - C-Q9: 如何調整注音 IME 設定，改善 Shift 與選字體驗？
    - D-Q2: PowerToys 的 Image Resizer/RAW Viewer 在 Vista 不能用，如何處理？
    - D-Q3: RAW 縮圖/預覽在 Vista 不顯示，如何修復？
    - D-Q4: UAC 提示太頻繁，怎麼在不關閉 UAC 的前提下改善？
    - D-Q10: 自寫腳本常被安全軟體/系統阻擋或被 UAC 打斷，如何穩定執行？

- 高級者：建議關注哪 15 題
    - B-Q3: UIPI（使用者介面權限隔離）如何阻擋拖放與訊息注入？
    - B-Q7: HD Photo/JPEG XR 的壓縮原理（高階）是什麼？
    - B-Q9: Console 拖放的技術流程與 Vista 的改變是什麼？
    - B-Q10: Windows 的 runas 技術架構是什麼？
    - B-Q11: Vista 注音 IME 的組字與選字機制背後機制是什麼？
    - B-Q12: Backspace 與 Esc 在 IME 狀態機中各扮演什麼角色？
    - B-Q13: 為何 Windows Explorer 難以「以系統管理員身分」完整執行？
    - B-Q14: PowerToys 的 Shell 擴充在 Vista 為何容易失效？
    - B-Q15: 從 GDI+ 遷移到 WIC/WPF 的設計步驟為何？
    - C-Q5: 如何用 .NET/WPF/WIC 讀取 RAW 並轉存為 PNG？
    - C-Q6: 如何將 HD Photo（.wdp/.hdp）轉為 JPEG（WIC）？
    - D-Q1: 無法將檔案拖放到 Console，怎麼辦？
    - D-Q2: PowerToys 的 Image Resizer/RAW Viewer 在 Vista 不能用，如何處理？
    - D-Q7: 在中文模式按住 Shift 輸入都是大寫，如何打小寫？
    - D-Q8: 在選字狀態 Backspace 無法取消組字，怎麼辦？