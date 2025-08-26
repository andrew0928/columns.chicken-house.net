# [MSDN] Visual Studio Add-Ins Every Developer Should Download Now

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

Q1: 什麼是 Visual Studio Add-in？
- A簡: Add-in 是擴充 Visual Studio 的外掛，透過自動化與命令擴展 IDE 功能，提升生產力。
- A詳: Visual Studio Add-in 是以自動化物件模型（DTE/EnvDTE）為核心，透過命令、工具列與事件掛鉤擴展 IDE 的外掛。它可自動化重複工作、加入自訂工具與選單、整合第三方服務。Add-in 早期多採 COM/IDTExtensibility2 介面，現已由 VSIX 擴充（VSPackage、MEF 等）取代，但核心目標均是強化開發效率與體驗。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q6, B-Q2

Q2: Add-in 與 Extension（VSIX）有何差異？
- A簡: Add-in 多為舊式 COM 自動化；Extension 以 VSIX 打包、VSPackage/MEF 為核心，更現代與安全。
- A詳: Add-in 使用 IDTExtensibility2 與 DTE 自動化，特性是上手快但功能較受限；VSIX Extension 以 VS SDK、VSPackage 或 MEF 元件為基礎，能深度擴充命令、編輯器、語言服務與 UI，打包格式為 .vsix，安裝/卸載更乾淨安全。自 VS 2015 起，Add-in 正式被移除，建議全面改用 VSIX。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, B-Q3, B-Q4

Q3: 什麼是 VSIX？
- A簡: VSIX 是 Visual Studio 擴充的標準封裝格式，便於安裝、更新、簽章與相容性管理。
- A詳: VSIX（.vsix）封裝包含擴充組件、資源、相依性與 vsixmanifest 描述檔。它由 VSIX Installer 管理，支援簽章驗證、自動更新、版本限制（支援 VS 範圍）與使用者範圍/全機範圍安裝。VSIX 可包含 VSPackage、MEF 元件、編輯器擴充、範本等，是現代 VS 擴充的主要載具。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, B-Q13, A-Q14

Q4: 為什麼需要安裝 Add-ins/Extensions？
- A簡: 它們自動化工作、補足 IDE 缺口、整合工具鏈，顯著提升效率與品質。
- A詳: 擴充可提供範本生成、程式碼重構、靜態分析、測試與偵錯輔助、來源控制整合等功能，降低重複勞務與人為錯誤。對個人與團隊而言，擴充能標準化流程、縮短交付時間、提升可維護性。MSDN 推薦清單即強調「立即可得的價值」，幫助開發者快速升級生產力堆疊。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q19, B-Q11, C-Q1

Q5: Visual Studio 擴充性的核心價值是什麼？
- A簡: 可延展、可組合、可維護，讓 IDE 隨情境演進，持續符合團隊與專案需求。
- A詳: 核心價值包含三面向：可延展（提供命令、視窗、編輯器與語言層面的擴展點）、可組合（透過 MEF 組件化，擴充互相協作）、可維護（VSIX 隔離安裝、明確版本邊界、易於更新/回滾）。這些特性使 VS 能以外掛方式持續擴張能力，避免客製化變成負擔。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, B-Q7, B-Q13

Q6: 什麼是 DTE/EnvDTE 自動化模型？
- A簡: DTE 是 VS 自動化入口，提供文件、專案、命令與事件的程式化控制。
- A詳: EnvDTE 是 Visual Studio 的自動化物件模型，DTE（Development Tools Environment）為其根物件。透過 DTE，可操作解決方案、專案、文件、選單命令與事件，支援巨集與 Add-in 的自動化擴展。雖然現代擴充多使用 VS SDK，DTE 仍在許多腳本化與工具整合場景中實用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q9, C-Q2

Q7: 什麼是 VSPackage？
- A簡: VSPackage 是 VS SDK 的擴充單元，能深度整合命令、UI、編輯器與專案系統。
- A詳: VSPackage 是使用 VS SDK 建置的擴充，透過 AsyncPackage 安全延遲載入，提供命令、工具視窗、選項頁、專案系統掛鉤與服務。它比 Add-in 更底層、可定制程度更高。VSIX 封裝通常包含一個或多個 VSPackage，以提供完整的 IDE 整合體驗。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q5, A-Q14

Q8: Add-in、巨集（Macros）與 VSPackage 有何差異？
- A簡: 巨集最輕量；Add-in 透過 DTE 擴充；VSPackage 最強、以 VS SDK 深度整合。
- A詳: 巨集偏向程式錄製與腳本自動化，部署簡易但受限多；Add-in 以 DTE 操作 IDE，能加命令與工具列，功能中等；VSPackage 以 VS SDK/AsyncPackage 建置，掌控命令、UI、編輯器與服務註冊，能力最強、學習曲線較高。現代開發多以 VSIX+VSPackage 為主。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, B-Q4, C-Q2

Q9: MEF 在 Visual Studio 中扮演什麼角色？
- A簡: MEF 提供元件化與組合，支援編輯器與服務的可插拔擴展。
- A詳: Managed Extensibility Framework（MEF）透過匯出/匯入（Export/Import）宣告式組件組合，讓 VS 在啟動或需求時發現並載入擴充部件。編輯器子系統（分類器、標記器、完成清單等）大量依賴 MEF。這種鬆耦合模式能降低相依錯誤並提升擴展可維護性與測試性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q8, D-Q4

Q10: 什麼是命令（Command）與選單擴充？
- A簡: 命令是可綁定按鈕/快捷鍵的行為；擴充可新增至選單與工具列。
- A詳: VS 以命令為抽象行為單元，透過 .vsct 或擴充 API 宣告命令、路由與可見性規則。擴充可將命令綁定到主選單、內容選單或工具列，並根據內容（例如選取檔案類型）控制啟用狀態。這是最常見的擴充方式之一，便於將工作流程一鍵化。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, C-Q6, D-Q2

Q11: 什麼是工具視窗（Tool Window）？
- A簡: 可停駐於 IDE 的自訂面板，用於呈現資料、面板與交互操作。
- A詳: 工具視窗是可與方案總管、輸出視窗同級的停駐面板。擴充可創建自訂工具視窗，承載 WPF/WinForms UI，與命令、服務互動，提供搜尋、儀表板、診斷或可視化功能。生命週期由 VSPackage 管理，可持久化狀態與佈局。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q3, D-Q3

Q12: 什麼是編輯器擴充（如語法高亮、IntelliSense）？
- A簡: 編輯器擴充透過 MEF 插點提供語法標示、分析、完成與重構。
- A詳: 編輯器提供多種擴展點：分類器（Classifier）決定顏色化、標記器（Tagger）提供裝飾、完成提供器（Completion）加入建議、CodeLens/Peek 等深入體驗。擴充以 MEF 匯出元件並宣告內容型別，於開啟對應檔案時載入，為語言或特定檔案類型增能。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, B-Q7, C-Q4

Q13: 什麼是 Visual Studio Marketplace？
- A簡: 微軟的擴充市集，提供搜尋、安裝、評價與自動更新機制。
- A詳: Visual Studio Marketplace 是官方擴充分發平台，作者可上架 VSIX，提供版本相容範圍、發行說明與簽章。使用者可從 IDE 內搜尋安裝、接收更新通知。市集機制提高信任度、簡化更新，並促進社群與商業擴充的生態繁榮。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, C-Q8, B-Q13

Q14: 什麼是 vsixmanifest？
- A簡: VSIX 的描述檔，定義擴充身分、內容、相容版本與相依性。
- A詳: vsixmanifest（source.extension.vsixmanifest）包含擴充名稱、作者、版本、支援 VS 範圍、包含的 VSPackage/MEF 組件、資源與相依性（如共用 SDK）。它驅動安裝程序、更新比對與 IDE 載入邏輯。維護精確的 manifest 是確保相容與正確部署的關鍵。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q13, C-Q8

Q15: 為什麼舊式 Add-in 在新版 VS 不再支援？
- A簡: 舊模型受限且難維護，VS 以 VSIX/VSPackage 取代以提升安全與擴展力。
- A詳: Add-in 依賴 IDTExtensibility2 與 COM 自動化，缺乏細緻生命周期控制、安裝/卸載不夠隔離，且對編輯器與語言服務介入有限。VS 在 2015 移除 Add-in，改以 VSIX 與 AsyncPackage、MEF 為主，強化延遲載入、安全簽章、相容控制與生態一致性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, B-Q4, B-Q20

Q16: 安裝擴充的安全風險與信任模式是什麼？
- A簡: 風險含惡意程式與隱私外洩；透過簽章、市集審查與權限隔離降低。
- A詳: 擴充具有 IDE 內高權限，可能存取檔案與專案資訊。安全策略包含：VSIX 簽章驗證、市集稽核、版本與範圍限制、沙箱化資料夾、最低必要權限設計。企業可建立白名單與內部簽發，並限制來源與自動更新策略以控管風險。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q15, D-Q9, C-Q8

Q17: 擴充對效能有何影響與評估方式？
- A簡: 不當擴充會拖慢啟動與編輯；應用延遲載入與量測工具評估。
- A詳: 影響來源包括同步初始化、頻繁 UI 更新、長時間檔案掃描與過度事件訂閱。最佳實踐：使用 AsyncPackage 延遲載入、背景工作、節流/快取；以 Performance Profiler、ActivityLog 與 ETW 量測。定期審視啟用擴充清單並移除冗餘。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q16, D-Q3, C-Q7

Q18: 擴充相容性（VS 版本、CPU 架構）需注意什麼？
- A簡: 明確標註支援版本與 x86/x64，測試不同通道與多實例。
- A詳: VS 版本差異影響 API 可用性與行為；vsixmanifest 應設定支援範圍。VS 2022 為 64 位元，需使用 AnyCPU/適當目標架構並更新原生相依。亦須測試不同工作負載、預覽通道與多使用者環境，以確保安裝與執行一致性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q14, D-Q8, C-Q8

Q19: 常見擴充類型有哪些？
- A簡: 生產力輔助、偵錯/測試、程式碼分析、編輯器強化、專案/範本與整合。
- A詳: 分類可含：生產力（重構、模板、快速導覽）、偵錯/測試（測試執行器、快照偵錯）、程式碼品質（分析器、規範檢查、格式化）、編輯器（語法/完成/視覺化）、專案系統與範本、DevOps/雲/來源控制整合。依團隊需求選擇組合提升價值。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, B-Q11, C-Q1

Q20: MSDN 推薦 Add-ins 對學習者的意義是什麼？
- A簡: 提供精選工具線索，快速建立擴充選型與生產力基線。
- A詳: 官方推薦代表穩定、價值明確與社群驗證。對初學者，它是「快速上手清單」；對中高階者，它提供工具空缺與最佳實踐的參考，並引導了解擴充機制。即便年代久遠，核心理念（選擇可靠擴充、聚焦痛點）仍適用於現代 VS 生態。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, C-Q1, C-Q9

### Q&A 類別 B: 技術原理類

Q1: Visual Studio 擴充架構如何運作？
- A簡: 以 VS SDK、VSPackage、MEF 與 VSIX 為核心，透過擴展點組合進 IDE。
- A詳: 架構由核心 IDE、擴展點（命令、工具視窗、編輯器、語言服務）、擴充載體（VSPackage/MEF 元件）、封裝與部署（VSIX/manifest）組成。啟動時 VS 解析 VSIX、建立服務、透過 MEF 組合部件，必要時延遲載入 AsyncPackage。命令路由與事件系統驅動互動流程。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q4, B-Q7

Q2: 舊式 Add-in（IDTExtensibility2）如何運作？
- A簡: 藉由 DTE 自動化與事件，透過 COM 載入並注入命令與 UI。
- A詳: Add-in 實作 IDTExtensibility2，在 OnConnection 時取得 DTE，註冊命令與工具列，透過事件（如 DocumentEvents）響應 IDE 狀態。卸載時清理資源。其優點是易上手；缺點是可擴性受限、安裝/移除不夠隔離、與現代編輯器/語言服務整合不足。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q1, A-Q6, B-Q20

Q3: VSIX 打包與安裝機制是什麼？
- A簡: VSIX 包含檔案與 manifest，由 VSIX Installer 驗證、部署、註冊。
- A詳: 安裝流程：解析 vsixmanifest→驗證簽章/版本相容→處理相依→部署檔案至擴充資料夾→註冊資源（命令/字形/資源）→通知 IDE 重啟或熱載。更新透過識別 ID 比對版本，支援回滾。取消安裝以 manifest 追蹤檔案進行乾淨移除。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, A-Q14, B-Q13

Q4: VSPackage/AsyncPackage 的啟動流程？
- A簡: 以延遲載入為主，依自動載入規則或命令觸發初始化。
- A詳: AsyncPackage 透過 ProvideAutoLoad 或 VSCT 命令首次觸發時初始化。初始化於主執行緒/後台分工，避免阻塞 UI。註冊服務、命令、工具視窗與選項頁，並訂閱必要事件。這種模型提升啟動效能與穩定性，是現代擴充標配。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q16, C-Q2

Q5: 命令與按鈕如何透過 .vsct 定義？
- A簡: 以 VSCT 宣告命令、群組、放置位置與鍵綁定，IDE 解析並渲染。
- A詳: VSCT 檔描述命令 ID、可見性、群組與放置（Menus/Groups/Buttons），並可設定 QueryStatus/Exec 路由。打包時編譯為 .ctc/.pkgdef，IDE 載入後於相應選單與工具列顯示。此機制將 UI 菜單與行為明確宣告化，便於管理與本地化。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, C-Q6, D-Q2

Q6: 工具視窗的建立與生命週期如何設計？
- A簡: 由 Package 註冊與建立，承載 WPF/WinForms，支援停駐與狀態持久化。
- A詳: 透過 ProvideToolWindow 特性註冊，於命令或自動載入時建立視窗。生命週期含建立、顯示、隱藏與釋放；可保存位置與 UI 狀態。與 VS 服務（如 IVsUIShell）互動，提供停駐、浮動、停靠群組等體驗。需注意 UI 執行緒與資源釋放。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, C-Q3, D-Q3

Q7: MEF 元件發現與組合的流程是什麼？
- A簡: 以 Export/Import 標註，IDE 依內容型別與條件組合載入。
- A詳: 擴充將類別以 [Export] 標註並宣告契約；[Import]/[ImportMany] 注入相依。VS 啟動或開啟文件時，MEF Catalog 掃描 VSIX 組件，根據 ContentType、Name、Order 等條件組合元件。組合失敗會出現 Composition Error，需檢查相依與標註一致性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q8, D-Q4

Q8: 編輯器擴充的核心機制（TextView、Classifier、Tagger）？
- A簡: 透過 MEF 匯出對應介面，在檔案開啟時為 TextView 附加服務。
- A詳: 開檔建立 ITextBuffer/ITextView；分類器 IClassifier 提供分類資訊供顏色化；標記器 ITagger 產生標記（如錯誤波浪線、裝飾）；完成提供器 ICompletionSource 提供建議。元件以 ContentType 篩選，僅在相關檔案啟用。需避免頻繁重算造成延遲。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q12, C-Q4, D-Q3

Q9: DTE 事件與自動化的運作原理？
- A簡: 透過 EnvDTE 事件源監聽 IDE 狀態變化並執行自動化動作。
- A詳: DTE 提供 Events 集合（SolutionEvents、DocumentEvents 等）。Add-in 或 Extension 訂閱事件，於檔案開啟、儲存、建置等時點執行邏輯，如自動格式化或檔案生成。注意事件生命週期、弱參考避免洩漏，以及跨執行緒呼叫 UI 的安全。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, C-Q2, D-Q6

Q10: 選項頁與設定儲存如何實作？
- A簡: 以 OptionsPage 提供 UI，透過 SettingsStore/Registry 存取持久化設定。
- A詳: VSPackage 可提供 DialogPage/ToolsOptionsProvider，建立 Options 頁面。設定可存入 WritableSettingsStore 或使用自定檔案（如 JSON）。需處理版本升級遷移、預設值、驗證與即時套用，並避免頻繁 I/O 影響效能。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q3, C-Q8, D-Q3

Q11: Roslyn Analyzer/Code Fix 的原理是什麼？
- A簡: 於編譯器管線分析語法/語意，提出診斷並提供自動修正。
- A詳: Analyzer 以 Roslyn API 訂閱語法/語意節點，對應規則輸出 Diagnostic。CodeFixProvider 回應診斷，提供修正動作（CodeAction），產生新語法樹。此機制整合至編輯器與建置，跨專案一致。可用 VSIX 或 NuGet 分發。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q12, C-Q5, D-Q7

Q12: 擴充調試的啟動與部署機制？
- A簡: 以 Experimental Instance 啟動隔離的 VS，熱部署 VSIX 進行偵錯。
- A詳: 在 VSIX 專案設定為「啟動外部程式」指向 devenv.exe /rootSuffix Exp，啟動實驗實例。建置後自動部署 VSIX 至實驗環境，支援中斷點偵錯。此流程確保不污染主 VS，便於快速迭代與回滾。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q7, D-Q6, B-Q3

Q13: 擴充的更新與版本管理如何運作？
- A簡: 以擴充 ID 與版本比對，支援自動更新與相容性檢查。
- A詳: Marketplace 以 Extension ID 識別擴充，IDE 定期檢查更新資訊。更新流程驗證版本、相容範圍與簽章，成功後替換舊版本。可設定必要版本、通道（穩定/預覽）與破壞性更新提示，保障用戶體驗與穩定性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q13, A-Q14, D-Q8

Q14: 依賴與安裝範圍（Per-User/All Users）如何設計？
- A簡: 透過 manifest 定義相依與安裝範圍，影響權限與更新行為。
- A詳: vsixmanifest 可宣告相依庫或擴充。Per-User 安裝至使用者路徑，無需管理員權限；All Users 安裝需提權，供多人共用。相依需明確版本範圍並避免菱形依賴。企業環境可用離線封裝與集中部署。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, A-Q18, C-Q8

Q15: 擴充的安全性機制有哪些？
- A簡: 簽章驗證、來源稽核、權限最小化與封鎖清單防護。
- A詳: VSIX 可附數位簽章，安裝時驗證發行者。Marketplace 進行掃描與政策檢查。VS 具安全設定（允許/封鎖清單），企業可強化政策。擴充本身應最小權限、隔離設定、保護隱私資料並提供明確的遙測告知與關閉選項。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, D-Q9, C-Q8

Q16: 延遲載入與效能監控如何實作？
- A簡: 使用 AsyncPackage、背景工作與 Profiler 度量啟動與 UI 延遲。
- A詳: 以 ProvideAutoLoad 或命令觸發，僅在需要時初始化。長工作改為 async/await 背景執行，使用 JoinableTaskFactory 保持 UI 響應。透過 PerfView/ETW、VS Performance Profiler、ActivityLog 記錄瓶頸，持續優化熱路徑。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q17, C-Q7, D-Q3

Q17: 擴充如何與解決方案/專案系統互動？
- A簡: 透過 VS 服務與事件（如 IVsSolutionEvents）監聽與操作。
- A詳: 訂閱解決方案開啟/關閉、專案加入/移除事件，使用 DTE 或 CPS/Project System API 讀寫專案屬性。需考慮跨語言/多目標框架差異與長時間 IO 的非同步化，避免阻塞建置/載入流程。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q9, C-Q3, D-Q6

Q18: 來源控制整合的原理是什麼？
- A簡: 透過 VS 提供的服務與事件，掛鉤檔案狀態、差異與操作。
- A詳: 擴充可使用 Team Explorer/Source Control API，監聽檔案變更、提供差異視圖、擴展提交體驗。舊式 SCCI 介面提供基本掛鉤；現代更多走 REST/CLI 與擴展 UI。需注意同步狀態與衝突處理的使用者體驗。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q19, D-Q5, C-Q1

Q19: 遙測（Telemetry）與隱私在擴充中的考量？
- A簡: 量測使用以改進品質，須匿名化、可關閉並合規。
- A詳: 擴充可記錄功能使用與錯誤，以改善體驗；但應遵循最小化原則、移除可識別資訊、提供明確同意與關閉開關，並遵循 GDPR/隱私政策。數據安全存放與傳輸加密同樣重要。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, D-Q9, C-Q8

Q20: 從 Add-in 遷移到 VSIX 的原理與步驟？
- A簡: 對映 DTE 自動化至 VS SDK/MEF，改以 VSIX 打包並支援延遲載入。
- A詳: 盤點 Add-in 功能→將命令/事件對映至 VSPackage/VSCT→用 MEF 重寫編輯器邏輯→實作 AsyncPackage 與服務註冊→建立 vsixmanifest 與相容版本→測試實驗實例與效能→制定升級/回滾策略。此轉換提升可維護性與相容性。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q15, C-Q9, D-Q8

### Q&A 類別 C: 實作應用類

Q1: 如何在 Visual Studio 安裝 VSIX 擴充？
- A簡: 透過 IDE 擴充管理或下載 VSIX 檔，按提示完成安裝與重啟。
- A詳: 具體步驟：1) 在 VS 中開啟「延伸模組管理員」搜尋並安裝；或 2) 從 Marketplace 下載 .vsix，雙擊啟動 VSIX Installer；3) 檢查相容版本與簽章；4) 完成後重啟 VS。注意事項：優先官方來源、檢視權限與評價、備份設定，避免同類擴充重疊造成衝突。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q13, A-Q3, D-Q1

Q2: 如何建立一個帶命令的簡單 VSIX 擴充？
- A簡: 使用 VS SDK 專案範本，新增命令與 VSCT，打包為 VSIX。
- A詳: 步驟：1) 建立「VSIX Project」+「VS Package」；2) 於 VSCT 定義命令；3) 在 Package.Initialize 中註冊命令回呼；4) 執行於實驗實例測試。程式碼示例：在命令回呼中呼叫 DTE.ActiveDocument.Save()。注意使用 AsyncPackage 與非同步初始化，避免阻塞 UI。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q4, C-Q7

Q3: 如何建立自訂工具視窗？
- A簡: 使用 ProvideToolWindow 註冊，建立 WPF 控制並以命令顯示。
- A詳: 步驟：1) 新增 ToolWindow 範本；2) 在 Package 上套用 [ProvideToolWindow(typeof(MyToolWindow))]；3) 在命令中呼叫 FindToolWindow+Show()；4) WPF UserControl 承載 UI。注意跨執行緒 UI 更新、持久化狀態（例如讀寫設定檔）與釋放資源。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, A-Q11, D-Q3

Q4: 如何為編輯器新增基本語法高亮？
- A簡: 以 MEF 匯出 IClassifier，針對 ContentType 提供分類與顏色。
- A詳: 步驟：1) 建立分類型別與格式定義；2) 實作 IClassifier，於 GetClassificationSpans 判定關鍵字範圍；3) 以 [Export(typeof(IClassifierProvider))] 與 [ContentType("myLang")] 標註；4) 打包 VSIX。注意避免每字元重算，可用快取。簡例：遇到 "TODO" 回傳提示分類以上色。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q8, B-Q7, D-Q3

Q5: 如何撰寫 Roslyn Analyzer 與 Code Fix？
- A簡: 建立 Analyzer 專案，定義診斷與規則，配對 CodeFixProvider。
- A詳: 步驟：1) 使用「Analyzer with Code Fix」範本；2) 定義 DiagnosticDescriptor（ID、訊息、嚴重性）；3) 訂閱語法/語意節點分析；4) 實作 CodeFixProvider 提供 CodeAction；5) 單元測試驗證；6) 以 VSIX 或 NuGet 發佈。注意效能、誤報率與可設定性。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q11, D-Q7, C-Q8

Q6: 如何將命令加入選單並設定快捷鍵？
- A簡: 在 VSCT 放置命令至選單群組，使用 KeyBindings 指定快捷鍵。
- A詳: 步驟：1) VSCT 定義 <Buttons><Button> 與所在群組如 IDG_VS_TOOLSMENU；2) 在 <KeyBindings> 指定 Ctrl+Alt+K 等組合；3) 在 QueryStatus 控制可見；4) 測試衝突並提供使用者自訂。注意符合 VS 快捷鍵慣例與本地化文字。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, A-Q10, D-Q2

Q7: 如何偵錯與測試 VSIX 擴充？
- A簡: 使用實驗實例啟動，設中斷點，搭配 ActivityLog 與 Profiler。
- A詳: 步驟：1) 專案啟動外部程式 devenv.exe /rootsuffix Exp；2) 建置部署 VSIX；3) 下中斷點驗證命令/MEF 載入；4) 啟用 ActivityLog.xml 與 ETW；5) 使用 Performance Profiler 量測。注意避免在主實例測試，必要時重置實驗環境。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, B-Q16, D-Q6

Q8: 如何封裝、簽署並發佈 VSIX 到 Marketplace？
- A簡: 完成 vsixmanifest、加簽、相容設定，於 Marketplace 上架審核。
- A詳: 步驟：1) 填寫 manifest（ID、版本、支援 VS 範圍）；2) 使用簽章工具或 CI 在 VSIX 上附簽；3) 準備描述、截圖、隱私政策；4) 上傳 Marketplace、通過稽核；5) 設定自動更新。注意遵守政策、標註權限、提供變更紀錄與回滾方案。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q13, A-Q16

Q9: 如何將舊 Add-in 遷移至 VSIX？
- A簡: 盤點 DTE 用法，改為 VSPackage/MEF，重建 VSIX 封裝與命令。
- A詳: 步驟：1) 列出 Add-in 命令/事件；2) 用 VSCT 重建命令；3) 將 DTE 自動化替換為 VS 服務或 Roslyn API；4) 將 Editor 功能改為 MEF 元件；5) 建立 AsyncPackage；6) 撰寫 vsixmanifest；7) 測試效能與相容。注意 API 差異與使用者資料遷移。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q20, A-Q15, D-Q8

Q10: 如何定期清理擴充快取以提升穩定性？
- A簡: 清除 ComponentModelCache、重置實驗實例，避免快取損壞。
- A詳: 步驟：1) 關閉 VS；2) 刪除 %LocalAppData%\Microsoft\VisualStudio\<ver>\ComponentModelCache；3) 視需要刪除 MEFCache 與 Roslyn 快取；4) 重新啟動 VS 重建快取。注意先備份設定，並確認非企業鎖控環境。此法可解決載入異常與組合錯誤。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: D-Q2, D-Q4, B-Q7

### Q&A 類別 D: 問題解決類

Q1: 安裝 VSIX 時出現 VSIXInstaller 錯誤怎麼辦？
- A簡: 檢查相容版本、簽章與相依性，改用離線安裝或更新 VS。
- A詳: 症狀：安裝失敗、版本不相容或簽章無效。原因：VS 版本不支援、缺少相依、下載損壞。解法：更新 VS 至支援範圍；從官方重新下載；檢查 vsixmanifest 要求；嘗試以管理員權限或離線安裝。預防：優先市集來源、固定通道與版本測試。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, B-Q3, A-Q18

Q2: 啟動 VS 時提示「擴充載入失敗」如何處理？
- A簡: 查看 ActivityLog，移除或更新衝突擴充，重建快取。
- A詳: 症狀：啟動彈窗顯示某擴充無法載入。原因：版本不相容、MEF 組合失敗、檔案損壞。解法：啟用 Log（devenv /log），檢視 ActivityLog.xml；禁用/移除最近更新擴充；清除 ComponentModelCache；更新至支援版本。預防：分階段更新與回滾策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, C-Q10, A-Q18

Q3: 安裝擴充後 IDE 變慢或卡頓怎麼辦？
- A簡: 啟用延遲載入、禁用可疑擴充，使用 Profiler 找瓶頸。
- A詳: 症狀：啟動變慢、打字延遲。原因：同步初始化、頻繁分析、UI 阻塞。解法：逐一停用擴充定位；檢視性能分析、ActivityLog；要求作者改為 AsyncPackage 與背景任務；調低分析頻率。預防：只裝必要擴充，定期評估清單。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q16, A-Q17, C-Q7

Q4: 出現 MEF Composition Error 如何診斷？
- A簡: 檢查 Export/Import 契約、ContentType 與相依性版本。
- A詳: 症狀：錯誤列出未滿足匯入或循環依賴。原因：契約名稱不一致、缺少 Export、版本衝突。解法：對照類型與名稱，確保單一載入來源；檢查 vsixmanifest 與相依版本；清除快取重試。預防：以測試覆蓋 MEF 邏輯，維持嚴格命名。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q7, C-Q10, B-Q8

Q5: 擴充與其他擴充衝突怎麼解？
- A簡: 比對功能重疊，調整載入順序或停用其一，回報作者協調。
- A詳: 症狀：重複功能、快捷鍵衝突、UI 疊加。原因：選單/命令同名、編輯器 Tagger 競爭、全域快捷鍵搶占。解法：調整快捷鍵、禁用重疊功能、設定 ContentType/Order；必要時只留一個。預防：安裝前檢視功能清單與相容聲明。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q6, B-Q5, A-Q19

Q6: 擴充導致 VS 當機或拋例外如何處理？
- A簡: 在實驗實例重現，收集日誌與傾印，回報或回滾版本。
- A詳: 症狀：特定操作崩潰。原因：未捕捉例外、跨執行緒 UI、相依破損。解法：在 Exp 實例中測試；啟用 /log 與 Windows 事件檢視；收集 crash dump；回滾擴充版本或禁用；向作者回報附最小重現。預防：優先穩定通道，延後大版本升級。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, C-Q7, D-Q2

Q7: Roslyn Analyzer 造成編輯體驗變慢怎麼辦？
- A簡: 降低規則嚴格度、改背景分析，排查昂貴路徑與快取。
- A詳: 症狀：打字卡頓、分析耗時。原因：同步分析、遍歷過大、無快取。解法：調整 .editorconfig 規則嚴重性；將重工作移至建置階段；優化語法/語意存取、使用 Incremental Analyzer；更新至最新版。預防：設績效門檻與效能測試。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q11, C-Q5, A-Q17

Q8: VS 更新後擴充無法使用怎麼辦？
- A簡: 檢查支援範圍與相依，等待或安裝相容更新，必要時回退 VS。
- A詳: 症狀：擴充消失或載入錯誤。原因：API 變更、架構不符（如升至 x64）。解法：在 Marketplace 檢查相容版；與作者聯繫；若關鍵，回退 VS 版本或改替代工具。預防：在預覽通道先行驗證、設定延後自動更新。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q18, B-Q14, C-Q8

Q9: 如何面對不明來源擴充的安全疑慮？
- A簡: 僅用可信來源、檢查簽章與權限，企業採白名單策略。
- A詳: 症狀：來源不明、權限過廣。風險：資料外洩、惡意行為。解法：僅用 Marketplace 或內部簽署擴充；檢查簽章與評價；審閱權限與遙測說明；使用最小權限帳戶測試。預防：企業政策、代理審核、封鎖清單與持續稽核。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q16, B-Q15, C-Q8

Q10: 如何有效回報擴充問題並收集診斷？
- A簡: 提供最小重現、版本資訊、日誌與快照，附環境與步驟。
- A詳: 症狀：難以重現或資訊不足。解法：說明 VS/擴充版本、支援範圍；提供最小重現專案；附 ActivityLog、ETW/Profiler 報告、崩潰傾印；描述實際與預期行為、重現步驟。預防：在 CI 加入擴充驗證，維持可複製環境。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q7, B-Q12, D-Q6

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 Visual Studio Add-in？
    - A-Q2: Add-in 與 Extension（VSIX）有何差異？
    - A-Q3: 什麼是 VSIX？
    - A-Q4: 為什麼需要安裝 Add-ins/Extensions？
    - A-Q5: Visual Studio 擴充性的核心價值是什麼？
    - A-Q10: 什麼是命令（Command）與選單擴充？
    - A-Q11: 什麼是工具視窗（Tool Window）？
    - A-Q13: 什麼是 Visual Studio Marketplace？
    - C-Q1: 如何在 Visual Studio 安裝 VSIX 擴充？
    - B-Q1: Visual Studio 擴充架構如何運作？
    - B-Q3: VSIX 打包與安裝機制是什麼？
    - D-Q1: 安裝 VSIX 時出現 VSIXInstaller 錯誤怎麼辦？
    - D-Q2: 啟動 VS 時提示「擴充載入失敗」如何處理？
    - A-Q18: 擴充相容性（VS 版本、CPU 架構）需注意什麼？
    - D-Q8: VS 更新後擴充無法使用怎麼辦？

- 中級者：建議學習哪 20 題
    - A-Q6: 什麼是 DTE/EnvDTE 自動化模型？
    - A-Q14: 什麼是 vsixmanifest？
    - A-Q17: 擴充對效能有何影響與評估方式？
    - B-Q4: VSPackage/AsyncPackage 的啟動流程？
    - B-Q5: 命令與按鈕如何透過 .vsct 定義？
    - B-Q6: 工具視窗的建立與生命週期如何設計？
    - B-Q7: MEF 元件發現與組合的流程是什麼？
    - B-Q8: 編輯器擴充的核心機制（TextView、Classifier、Tagger）？
    - B-Q9: DTE 事件與自動化的運作原理？
    - B-Q10: 選項頁與設定儲存如何實作？
    - B-Q13: 擴充的更新與版本管理如何運作？
    - B-Q14: 依賴與安裝範圍（Per-User/All Users）如何設計？
    - B-Q15: 擴充的安全性機制有哪些？
    - B-Q16: 延遲載入與效能監控如何實作？
    - C-Q2: 如何建立一個帶命令的簡單 VSIX 擴充？
    - C-Q3: 如何建立自訂工具視窗？
    - C-Q6: 如何將命令加入選單並設定快捷鍵？
    - C-Q7: 如何偵錯與測試 VSIX 擴充？
    - D-Q3: 安裝擴充後 IDE 變慢或卡頓怎麼辦？
    - D-Q5: 擴充與其他擴充衝突怎麼解？

- 高級者：建議關注哪 15 題
    - A-Q8: Add-in、巨集（Macros）與 VSPackage 有何差異？
    - A-Q12: 什麼是編輯器擴充（如語法高亮、IntelliSense）？
    - A-Q15: 為什麼舊式 Add-in 在新版 VS 不再支援？
    - B-Q11: Roslyn Analyzer/Code Fix 的原理是什麼？
    - B-Q17: 擴充如何與解決方案/專案系統互動？
    - B-Q18: 來源控制整合的原理是什麼？
    - B-Q19: 遙測（Telemetry）與隱私在擴充中的考量？
    - B-Q20: 從 Add-in 遷移到 VSIX 的原理與步驟？
    - C-Q4: 如何為編輯器新增基本語法高亮？
    - C-Q5: 如何撰寫 Roslyn Analyzer 與 Code Fix？
    - C-Q8: 如何封裝、簽署並發佈 VSIX 到 Marketplace？
    - C-Q9: 如何將舊 Add-in 遷移至 VSIX？
    - D-Q4: 出現 MEF Composition Error 如何診斷？
    - D-Q6: 擴充導致 VS 當機或拋例外如何處理？
    - D-Q7: Roslyn Analyzer 造成編輯體驗變慢怎麼辦？