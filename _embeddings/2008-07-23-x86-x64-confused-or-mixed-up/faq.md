# x86? x64? 傻傻分不清楚...

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

Q1: 什麼是 x86 與 x64？
- A簡: x86/x64是CPU與作業系統的位元架構，決定位址寬度、指令集與相容性邊界。
- A詳: x86通常指32位元架構（IA-32），x64指64位元架構（x86-64/AMD64）。兩者差異在可用記憶體位址寬度、暫存器數量與指令集擴充。位元架構決定程式與元件是否可相互載入與執行，影響驅動、COM、程式編譯目標等。選擇正確架構是部署與相容性管理的基礎。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q5, B-Q1

Q2: x86 與 x64 的核心差異是什麼？
- A簡: 差在位址空間、暫存器與ABI，導致二進位不可互載、需「選邊站」執行。
- A詳: 64位元提供更大的虛擬位址空間與更多暫存器，對大資料、高併發有優勢；32位元受限於約4GB位址空間。兩者ABI／呼叫約定不同，PE格式也不同（PE32 vs PE32+），因此x86 DLL不能被x64行程載入，反之亦然。相容性不是透明的，需依元件位元選擇對應行程。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, B-Q21

Q3: 為什麼需要從 32 位元轉到 64 位元？
- A簡: 為突破記憶體限制、提升效能與擴充性，同時迎合平台主流演進。
- A詳: 32位元因虛擬位址空間受限，對大型資料處理、快取密集工作成為瓶頸。64位元擴大位址空間、暫存器與指令集能力，利於影像/影音編碼、資料庫、虛擬化等應用。同時作業系統與工具鏈逐步偏向x64，早期轉換能降低長期維運成本。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, B-Q3

Q4: 16→32 與 32→64 遷移的差異？
- A簡: 16→32靠v86與wowexec集中執行；32→64改為WOW64的使用者模式相容層。
- A詳: 16→32位元年代透過v86模式與wowexec在單一行程承載16位元程式；32→64則由WOW64提供使用者模式相容層，允許32位元程式各自成為獨立行程。關鍵限制是單一行程內不能混合兩種位元的程式碼，避免ABI衝突。這使跨位元的COM僅能透過跨行程路徑解決。
- 難度: 中級
- 學習階段: 基礎
- 關聯概念: A-Q5, B-Q1

Q5: 什麼是 WOW64？
- A簡: WOW64是64位元Windows的32位元相容層，在使用者模式模擬與轉接系統介面。
- A詳: WOW64（Windows-on-Windows 64-bit）攔截32位元應用對系統呼叫、檔案與登錄存取，提供對應的轉接與重新導向，讓x86應用可在x64系統獨立運作。它不允許同一行程混用x86/x64 DLL，主要提供檔案系統與登錄的雙視圖與基礎API轉譯，對驅動程式不提供相容性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q8

Q6: 為何同一個 Process 不能同時載入 x86 與 x64 程式碼？
- A簡: 因ABI與位址寬度不同，呼叫慣例不相容，載入即會失敗或崩潰。
- A詳: x86與x64在呼叫慣例、堆疊布局、PE格式、指令集與暫存器配置皆不同。程式載入器會拒絕不同位元的DLL（BadImageFormat），即使強制載入也會因參數寬度與返回約定不合而失敗。解法是選邊站，或改用跨行程的通訊機制分離位元。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q7

Q7: System32 與 SysWOW64 有何差異？
- A簡: System32存放x64系統DLL；SysWOW64存放x86用的系統DLL，名稱反直覺。
- A詳: 在x64 Windows中，System32內是64位元系統元件；供32位元程式使用的32位元系統DLL則位於SysWOW64。WOW64提供檔案重新導向，讓32位元程式要求System32時實際被導向到SysWOW64，確保載入正確位元元件。需小心直接路徑呼叫以避免混亂。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, C-Q4

Q8: Program Files 與 Program Files (x86) 的差異？
- A簡: 前者預設存放x64應用；後者存放x86應用，利於隔離與相容。
- A詳: 在x64系統中，系統安裝程式會將64位元應用放入Program Files資料夾，32位元應用放入Program Files (x86)。這有助於維持元件與登錄的對應關係，並讓WOW64正確執行檔案與登錄重新導向。部署時應依應用位元安裝至對應資料夾。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q19, C-Q10

Q9: x64 上為什麼登錄機碼會有兩份視圖？
- A簡: WOW64提供32/64位元分離的登錄視圖，避免元件註冊互相覆蓋。
- A詳: x64登錄在多數路徑下有x64與x86（Wow6432Node）兩個視圖。32位元程式透過WOW64自動被導向到Wow6432Node分支，64位元程式使用原生分支。這確保COM註冊、路徑與設定各自獨立。開發時需使用正確RegistryView或對應工具註冊。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q5

Q10: 什麼是 .NET 的 AnyCPU？
- A簡: AnyCPU讓IL在執行時由JIT轉為當前作業系統的位元，x64上預設為64位元。
- A詳: 將PlatformTarget設為AnyCPU，編譯產生中立IL。啟動於x64系統時JIT為64位元，於x86系統則為32位元。它簡化部署，但若程式涉及本機COM、P/Invoke或僅有單一位元的元件，AnyCPU可能在x64上變成64位元而造成相容性問題。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q3

Q11: 為什麼 AnyCPU 不保證「高枕無憂」？
- A簡: 因本機相依（COM/驅動/PInvoke）需位元吻合，AnyCPU可能誤上64位元。
- A詳: AnyCPU僅保證IL可JIT成對應位元，但無法改變外部元件的位元屬性。若應用需使用僅有x86版本的COM（如舊版CDO、某些Codec、ODBC/JET）或P/Invoke到x86 DLL，AnyCPU在x64上會變成64位元行程導致載入失敗。此時應改為x86目標或拆分流程。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q1, D-Q1

Q12: COM 元件的 x86-only 與 x64-only 有什麼影響？
- A簡: 位元不合的In-Proc COM無法載入；需同位元或改用跨行程COM。
- A詳: In-Proc COM透過DLL載入到呼叫端行程，故位元需吻合；x86程式只能載入x86 COM DLL。若僅有x64 COM存在，x86程式會出現Class not registered或BadImageFormat錯誤。替代方式是使用Out-of-Proc COM或自建外部服務，跨行程RPC不受位元限制。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, C-Q5

Q13: 什麼是 In-Process 與 Out-of-Process COM？
- A簡: In-Proc是DLL內嵌同行程；Out-of-Proc是獨立EXE跨行程呼叫。
- A詳: In-Proc COM以DLL載入，效能佳但要求與呼叫端位元一致。Out-of-Proc COM以EXE執行，透過RPC通訊，容許不同位元與隔離失效風險。當需要混用x86/x64元件或隔離不穩定元件時，選擇Out-of-Proc可增強相容與穩定性，代價是跨行程開銷。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, C-Q7

Q14: .NET 跨位元執行的核心價值是什麼？
- A簡: 透過CLR與JIT隔離硬體差異，多數純管理碼可無痛在x86/x64運作。
- A詳: CLR提供IL執行環境，JIT於執行時針對當前位元產生本機碼，使純管理碼對位元差異敏感度低。這降低遷移成本與部署複雜度。不過一旦牽涉本機互通（COM/PInvoke）或平台特定API，仍須關注位元一致與資料型別大小差異。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q3, C-Q1

Q15: 什麼是檔案系統重新導向（Redirection）？
- A簡: WOW64將x86程式對System32等路徑的存取導向至x86對應位置。
- A詳: 為確保x86程式載入正確DLL，WOW64攔截對特定系統路徑的存取，如System32，實際指向SysWOW64。這稱檔案重新導向。開發與部署時須避免硬編碼路徑，或在必要時以明確路徑呼叫對應位元的工具（如cscript.exe）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, C-Q4

Q16: 64 位元 Windows 中 cscript.exe 為何會有兩種？
- A簡: 存在x64與x86兩版cscript，位於System32與SysWOW64供對應程式使用。
- A詳: x64系統隨附兩版Windows Script Host：64位元在System32，32位元在SysWOW64。x86程式自動被導向到32位元版本。批次或自動化腳本若需特定位元，應以完整路徑呼叫，避免在COM自動化或轉檔流程出現「找不到元件」或相容性問題。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q4, D-Q3

Q17: 為何有些舊驅動或編解碼器在 x64 不可用？
- A簡: 驅動屬核心模式無WOW64相容；編解碼器多為In-Proc需同位元。
- A詳: x64不支援32位元核心模式驅動，必須提供x64原生版本。多數多媒體Codec透過In-Proc COM或DLL載入到行程，位元需一致。若僅有x86 Codec，x64程式無法使用；常見解法是以x86行程承載該Codec，或改用等效的x64替代品。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q23, D-Q5

Q18: 從 WPF 影像編碼與相機 RAW Codec 可以學到什麼？
- A簡: 影像Codec受位元束縛；呼叫端行程位元決定能否載入該Codec。
- A詳: WPF依賴Windows Imaging Component等介面載入Codec，通常為In-Proc COM或DLL。若只安裝x86 RAW Codec，則WPF在x64行程便無法使用。實務上可將應用編譯成x86，或將涉及Codec的處理拆到x86外部進程並以IPC溝通。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q8, C-Q7

Q19: 為什麼 ODBC/JET 在 x64 上常踩坑？
- A簡: 驅動常僅有x86版；x64行程無法載入，導致連線或DSN找不到。
- A詳: 舊版JET/部分ODBC驅動只有x86版本。當應用以x64行程執行（如AnyCPU於x64上）時，會出現Provider not found或連線失敗。解法是將應用編譯為x86、使用32位元ODBC管理員設定DSN，或改用支援x64的替代驅動。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q10, D-Q6

Q20: 什麼是 BadImageFormatException 的位元意涵？
- A簡: 代表載入了不同位元的組件/DLL，或PE格式與平台目標不符。
- A詳: 在.NET或原生載入時，若行程嘗試載入不同位元的元件，常見即拋出BadImageFormatException或載入器錯誤。此錯誤提醒位元不一致或平台目標設定錯誤。修正方式是調整PlatformTarget、改用對應位元的元件，或改為跨行程呼叫。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q9, C-Q1


### Q&A 類別 B: 技術原理類

Q1: WOW64 相容層如何運作？
- A簡: 以使用者模式攔截API，提供檔案/登錄重新導向與呼叫轉譯。
- A詳: 技術原理說明：WOW64在x64 Windows上為每個x86行程建立子系統，轉譯Win32 API呼叫至x64內核接口。關鍵流程：行程啟動、載入x86 ntdll/wow64.dll、進行系統呼叫轉接。核心組件：wow64.dll、wow64cpu.dll、wow64win.dll。它同時提供System32→SysWOW64與登錄Wow6432Node的重新導向。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q5, B-Q8

Q2: x64 系統啟動 32 位元程式的流程為何？
- A簡: 載入x86版載入器與WOW64元件，建立獨立x86行程與對應視圖。
- A詳: 技術原理說明：當使用者啟動PE32執行檔，系統檢查PE Header的Machine欄位，選擇x86載入器。關鍵步驟：建立行程、載入x86 ntdll、初始化WOW64層、套用檔案/登錄重新導向。核心組件：PE Loader、WOW64子系統、檔案/登錄轉接器。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q1, A-Q7

Q3: .NET AnyCPU 的執行決策與JIT流程？
- A簡: 依作業系統位元選擇JIT目標，x64上預設產生64位元本機碼。
- A詳: 技術原理說明：AnyCPU產出IL，由CLR根據OS位元選擇JIT後端。關鍵步驟：CLR載入、檢查PE標記（ILOnly/AnyCPU）、選擇JIT、產生本機碼。核心組件：CLR、JIT Compiler、PE/CLR Header中的CorFlags。若涉及COM/PInvoke，JIT不會自動處理位元不合問題。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, C-Q1

Q4: Windows 如何決定載入 System32 或 SysWOW64 的 DLL？
- A簡: 由行程位元與WOW64檔案重新導向決定實際搜尋與載入路徑。
- A詳: 技術原理說明：載入器依行程位元選擇搜尋順序。x86行程要求System32時，WOW64將其導向至SysWOW64。關鍵步驟：API呼叫攔截、路徑判斷、目錄映射。核心組件：WOW64檔案轉接、PE Loader。避免硬編碼路徑，改用環境變數與已知資料夾API。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q8

Q5: 登錄的 Wow6432Node 與 COM 解析流程是什麼？
- A簡: x86視圖映射至Wow6432Node；COM依視圖尋找CLSID與InprocServer32。
- A詳: 技術原理說明：WOW64為x86程式提供獨立登錄視圖。關鍵步驟：按行程位元選擇RegistryView、從對應視圖查找CLSID/ProgID、解析InprocServer32路徑。核心組件：登錄轉接、COM子系統。註冊時需用對應位元的regsvr32或RegAsm/RegSvcs，避免註冊到錯誤視圖。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: C-Q5, D-Q8

Q6: 為何 x86 DLL 不能載入 x64 行程？
- A簡: PE格式與ABI不同，載入器會拒絕，呼叫約定亦無法相容。
- A詳: 技術原理說明：x86為PE32，x64為PE32+，Machine欄位不同。關鍵步驟：載入器讀取PE Header、驗證位元一致、否則拋出錯誤。核心組件：PE Loader、Windows ABI。強行混載會造參數寬度不匹配、堆疊破壞。解法是同位元編譯或跨行程。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, D-Q9

Q7: .NET P/Invoke 在 x86/x64 的差異？
- A簡: 指標與結構大小不同，需用IntPtr與正確佈局避免參數錯位。
- A詳: 技術原理說明：x64下指標與長整數寬度增大。關鍵步驟：宣告使用IntPtr、LayoutKind.Sequential/Explicit、Pack設定、CallingConvention。核心組件：CLR互通層、Marshaler。避免假設指標等於int，使用SafeHandle與SizeOf檢查，確保跨位元一致。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: C-Q8, D-Q7

Q8: 檔案系統重新導向的機制細節？
- A簡: 針對敏感路徑進行透明映射，讓x86程式獲取x86對應檔案。
- A詳: 技術原理說明：WOW64攔截CreateFile/LoadLibrary等API。關鍵步驟：判斷呼叫端位元、檢測目標路徑、套用映射（如System32→SysWOW64）。核心組件：WOW64檔案轉接層。必要時可用特定API或路徑（如明確呼叫SysWOW64）繞過預設行為。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, C-Q4

Q9: Registry Redirection 與視圖選擇如何影響應用？
- A簡: 依行程位元選擇視圖，避免註冊覆蓋；需用對應工具操作。
- A詳: 技術原理說明：登錄提供獨立x86/x64視圖。關鍵步驟：API根據KEY_WOW64_*旗標或預設視圖存取、COM查找於對應視圖解析。核心組件：登錄轉接層。管理工具如regedit有64位元版；x86工具看到的路徑可能映射到Wow6432Node，需留意。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q5

Q10: cscript/wscript 雙位元並存時如何選擇？
- A簡: 以完整路徑指定位元版本；或在x86行程內自動導向至x86版。
- A詳: 技術原理說明：WOW64依行程位元導向腳本主機版本。關鍵步驟：檢查呼叫端位元、匹配對應cscript/wscript。核心組件：檔案重新導向。需要跨位元呼叫時，以C:\Windows\System32\cscript.exe（x64）或C:\Windows\SysWOW64\cscript.exe（x86）明確指定。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q16, C-Q4

Q11: IIS 中 32 位元應用程式集區切換的原理？
- A簡: 以應用程式集區旗標強制以x86 w3wp.exe承載網站。
- A詳: 技術原理說明：IIS可將App Pool設定為允許32位元應用，改以x86 w3wp.exe啟動。關鍵步驟：設定「Enable 32-Bit Applications」。核心組件：IIS工作進程、WOW64。此舉允許網站載入x86 COM/ODBC，代價是無法載入x64專屬元件。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q6, D-Q6

Q12: Out-of-Proc COM 如何繞過位元限制？
- A簡: 以跨行程RPC通訊，呼叫端與伺服端可不同位元安全互通。
- A詳: 技術原理說明：COM服務端為EXE，透過SCM啟動，客戶端以代理/骨架進行RPC。關鍵步驟：註冊本地伺服器、建立代理、序列化呼叫。核心組件：COM RPC、SCM。不同位元可互通，但需承擔序列化開銷與部署額外EXE。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q13, C-Q7

Q13: 影像編解碼器在WPF/WIC下的位元綁定原理？
- A簡: 多為In-Proc COM/DLL，必須與呼叫端位元一致方能載入。
- A詳: 技術原理說明：WIC透過COM發現與載入Codec，WPF使用WIC進行解碼。關鍵步驟：查找CLSID、載入In-Proc DLL、進行解碼。核心組件：WIC、COM、Codec DLL。若呼叫端為x64，僅能載入x64 Codec；無對應版即失敗。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q18, C-Q8

Q14: SMTP/CDO 與 .NET 的互動在 x64 上有何限制？
- A簡: 若CDO僅有x86，AnyCPU在x64上會失敗；需改x86或改用Managed API。
- A詳: 技術原理說明：CDO為COM，.NET以COM Interop呼叫。關鍵步驟：RCW建立、位元一致性檢查、方法呼叫。核心組件：COM Interop、CDO COM。x64行程無法載入x86 CDO，導致執行期錯誤。改以x86或使用System.Net.Mail等受管替代。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q1, C-Q1

Q15: ODBC 驅動載入的決策流程？
- A簡: 依行程位元載入對應ODBC驅動；DSN亦分x86與x64獨立管理。
- A詳: 技術原理說明：ODBC管理員與驅動亦分位元。關鍵步驟：應用呼叫ODBC、Driver Manager判斷位元、載入對應驅動。核心組件：odbc32.dll（x86/x64版本）。x86應用需用SysWOW64\odbcad32.exe設定DSN，否則會「找不到資料來源」。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q10, D-Q6

Q16: 常見「Class not registered」錯誤的解析流程？
- A簡: 代表CLSID未在對應視圖註冊或位元不符，需檢查Wow6432Node。
- A詳: 技術原理說明：COM由CLSID解析至InprocServer32/LocalServer32。關鍵步驟：依位元選視圖、查CLSID、讀取伺服路徑、啟動。核心組件：COM登錄、SCM。錯誤多因註冊到錯誤視圖或缺對應位元版本。用正確位元的註冊工具與檢視器確認。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q5, D-Q8

Q17: 多進程協作時，IPC 技術如何選擇？
- A簡: 依效能與維護選擇Named Pipe、Socket、gRPC或WCF等。
- A詳: 技術原理說明：跨位元以外部進程分離後，需IPC傳遞命令與資料。關鍵步驟：定義協定、序列化、錯誤處理、版本管理。核心組件：NamedPipe、TCP Socket、序列化庫。Named Pipe在本機低延遲；Socket通用性好。選型依資料量與佈署需求而定。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q7, D-Q2

Q18: Media Encoder COM 自動化的原理？
- A簡: 透過COM腳本/自動化API控制轉檔，需位元符合才能載入。
- A詳: 技術原理說明：Media Encoder暴露COM自動化介面，腳本以cscript/wscript建立COM物件、設定來源/輸出參數、啟動轉檔。關鍵步驟：建立物件、設定Profile、啟動、監控事件。核心組件：COM自動化、腳本主機。位元不合會造成建立物件失敗或流程卡住。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q3, C-Q9

Q19: 環境變數 ProgramFiles 與 ProgramFiles(x86) 如何解析？
- A簡: 依行程位元提供對應路徑，用於安裝與尋徑避免硬編碼。
- A詳: 技術原理說明：OS提供不同環境變數指向各自的安裝資料夾。關鍵步驟：行程讀取環境變數、組合路徑、存取檔案。核心組件：環境變數、WOW64轉接。使用這些變數可避免手動判斷資料夾、減少在x64上的路徑錯誤。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, C-Q9

Q20: 與 VM86 的歷史做法相比，WOW64 有何技術不同？
- A簡: VM86以虛擬8086模式處理16位元；WOW64是使用者模式API轉接。
- A詳: 技術原理說明：VM86在處理器層模擬16位元環境；WOW64則在OS使用者模式攔截與轉接x86 API至x64。關鍵步驟：VM86靠CPU模式切換；WOW64靠DLL層轉譯。核心組件：CPU模式/OS子系統。WOW64較輕量、易維護，亦設定行程位元隔離原則。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q4, B-Q1


### Q&A 類別 C: 實作應用類（10題）

Q1: 如何在 Visual Studio 將 .NET 專案指定為 x86？
- A簡: 於專案屬性PlatformTarget選x86，或以MSBuild參數指定x86。
- A詳: 具體實作步驟：在專案屬性→Build→Platform target選x86；或用MSBuild /p:PlatformTarget=x86。關鍵程式碼片段或設定：csproj中設定 <PlatformTarget>x86</PlatformTarget>。注意事項與最佳實踐：凡涉及x86 COM/ODBC/Codec，應強制x86；並標示安裝需求，避免AnyCPU誤上x64。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, D-Q1

Q2: 如何用 CORFLAGS 或 MSBuild 強制 32 位元執行？
- A簡: 用corflags /32BIT+或MSBuild設PlatformTarget，強制以x86啟動。
- A詳: 具體實作步驟：corflags YourApp.exe /32BIT+ 將IL標記為32位元偏好；或MSBuild /p:PlatformTarget=x86。關鍵程式碼片段或設定：corflags命令與CSProj設定。注意事項與最佳實踐：優先用編譯時設定；corflags會修改PE旗標，需在CI中控管一致性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, D-Q9

Q3: 如何在程式中偵測目前行程與作業系統的位元？
- A簡: 以Environment.Is64BitProcess/OS檢測，或檢查IntPtr.Size。
- A詳: 具體實作步驟：在程式啟動時檢查Environment.Is64BitProcess與Environment.Is64BitOperatingSystem。關鍵程式碼片段或設定：
  if (Environment.Is64BitProcess) { /* x64 */ }
  int ptr = IntPtr.Size; // 8為x64
注意事項與最佳實踐：依位元選擇路徑/COM CLSID/ODBC；避免在核心路徑分支過多，維持清晰架構。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, A-Q14

Q4: 如何在 x64 系統呼叫正確的 cscript.exe/wscript.exe？
- A簡: 以明確路徑指定位元：System32為x64，SysWOW64為x86版。
- A詳: 具體實作步驟：呼叫"C:\Windows\System32\cscript.exe"執行x64腳本主機；呼叫"C:\Windows\SysWOW64\cscript.exe"執行x86版。關鍵程式碼片段或設定：ProcessStartInfo.FileName設為對應路徑。注意事項與最佳實踐：避免相對路徑；從x86應用內呼叫時，預設會被導向至SysWOW64。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q16, B-Q10

Q5: 如何正確註冊 32/64 位元 COM 元件？
- A簡: 使用對應位元的regsvr32或RegAsm於正確視圖註冊。
- A詳: 具體實作步驟：x64 COM用C:\Windows\System32\regsvr32.exe；x86 COM用C:\Windows\SysWOW64\regsvr32.exe。Managed COM用RegAsm /codebase對應位元版本。關鍵程式碼片段或設定：regsvr32 path\your.dll。注意事項與最佳實踐：以系統位元與檔案位元對齊；確認CLSID出現於正確視圖。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, D-Q8

Q6: 如何在 IIS 讓網站以 32 位元執行以載入 x86 元件？
- A簡: 將App Pool啟用Enable 32-Bit Applications，並編譯網站為x86。
- A詳: 具體實作步驟：IIS管理員→應用程式集區→進階設定→Enable 32-Bit Applications=True；網站/應用程式目標設為x86。關鍵程式碼片段或設定：appcmd set apppool /enable32BitAppOnWin64:true。注意事項與最佳實踐：確認所有相依COM/ODBC皆為x86，避免混入x64元件。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, D-Q6

Q7: 如何以多進程拆分混用 x86/x64 元件？
- A簡: 將不同位元相依封裝為獨立EXE，透過IPC協作。
- A詳: 具體實作步驟：核心程式保留AnyCPU或x64；建立x86 Helper EXE承載x86 COM/Codec。用Named Pipe/標準輸入輸出傳遞命令與結果。關鍵程式碼片段或設定：.NET使用NamedPipeServerStream/ClientStream建立通道。注意事項與最佳實踐：定義穩定協定、處理錯誤與重試、監控子程序壽命。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q12, D-Q2

Q8: 如何在 WPF 中處理需要 32 位元 Codec 的影像？
- A簡: 將應用目標改為x86，或把影像轉換拆到x86外部進程。
- A詳: 具體實作步驟：專案PlatformTarget設x86；或建立x86工具EXE進行解碼，主程式以檔案/管線取得結果。關鍵程式碼片段或設定：透過WIC建立BitmapDecoder前檢查位元。注意事項與最佳實踐：避免在x64行程內直接載入僅有x86的Codec，降低崩潰風險。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q18, D-Q5

Q9: 如何跨位元自動進行媒體轉檔（Media Encoder）？
- A簡: 安裝對應位元版本，並以正確cscript與COM位元鏈結流程。
- A詳: 具體實作步驟：同機安裝x86/x64版Media Encoder；x86流程以SysWOW64\cscript+ x86 COM；x64流程以System32\cscript + x64 COM。關鍵程式碼片段或設定：以ProcessStartInfo啟動對應位元腳本主機。注意事項與最佳實踐：避免跨位元直接互叫；失敗時檢查CLSID與註冊視圖。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q18, D-Q3

Q10: 如何正確設定 ODBC（32/64 位元）資料來源？
- A簡: x86用SysWOW64\odbcad32.exe；x64用System32\odbcad32.exe分別設定。
- A詳: 具體實作步驟：設定x86 DSN請執行C:\Windows\SysWOW64\odbcad32.exe；x64 DSN用C:\Windows\System32\odbcad32.exe。關鍵程式碼片段或設定：連線字串指向對應驅動/DSN。注意事項與最佳實踐：應用與DSN位元需一致；無x64驅動時將應用改為x86。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q15, D-Q6


### Q&A 類別 D: 問題解決類（10題）

Q1: AnyCPU 程式在 x64 呼叫 CDO 出現執行期錯誤怎麼辦？
- A簡: 因CDO僅x86，AnyCPU在x64成64位元；改編譯x86或改用受管API。
- A詳: 問題症狀描述：建立CDO物件時失敗或拋例外。可能原因分析：x64行程無法載入x86 COM。解決步驟：將PlatformTarget改為x86；或改用System.Net.Mail等受管API。預防措施：清點COM相依，避免AnyCPU誤上x64造成位元不合。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q14

Q2: 32 位元程式如何處理需要呼叫 x64 COM 元件的需求？
- A簡: 無法In-Proc載入；改以Out-of-Proc或獨立x64 Helper以IPC橋接。
- A詳: 問題症狀描述：Class not registered或載入失敗。可能原因分析：位元不合禁止混載。解決步驟：使用Out-of-Proc COM（EXE伺服）或自建x64服務，32位元程式以IPC呼叫。預防措施：架構上以進程邊界隔離跨位元相依，避免緊耦合。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q12, C-Q7

Q3: Media Encoder 自動化轉檔完成後卡在 100% 不結束？
- A簡: 可能位元混用或COM事件/釋放問題；改用同位元或明確釋放。
- A詳: 問題症狀描述：腳本或自動化流程停在完成狀態。可能原因分析：x86呼叫x64或反之導致事件回呼不觸發、資源釋放失敗。解決步驟：全流程統一位元；檢查使用對應cscript與COM；顯式釋放COM物件。預防措施：測試同位元組合，避免跨位元互叫。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q18, C-Q9

Q4: 程式找不到 System32 資源實際落在 SysWOW64？
- A簡: 因檔案重新導向；以明確路徑或停用導向再存取。
- A詳: 問題症狀描述：x86程式存取System32卻載入x64 DLL或找不到。可能原因分析：WOW64將System32導向至SysWOW64。解決步驟：明確使用SysWOW64路徑；或改為x64行程。預防措施：避免硬編碼System32；以環境變數與API取得正確路徑。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, C-Q4

Q5: WPF 無法載入相機 RAW Codec 的問題如何處理？
- A簡: 因Codec僅x86；將應用改為x86，或外掛x86進程進行解碼。
- A詳: 問題症狀描述：載入RAW影像失敗或拋例外。可能原因分析：WPF/WIC需In-Proc載入Codec，x64行程無法使用x86 Codec。解決步驟：將應用編譯為x86；或用x86外部轉換工具。預防措施：部署前檢查Codec位元供應與替代方案。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q18, C-Q8

Q6: 64 位元上使用 JET/某些 ODBC 驅動失敗？
- A簡: 驅動僅x86；將應用改為x86，並用x86 ODBC管理員設定DSN。
- A詳: 問題症狀描述：Provider not found、連線失敗或找不到DSN。可能原因分析：x64行程載入不到x86驅動。解決步驟：改x86目標；用SysWOW64\odbcad32.exe建立DSN；或改用支援x64的驅動。預防措施：釐清驅動位元支援矩陣，建立部署檢查清單。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q10, B-Q15

Q7: P/Invoke 在 x64 發生參數錯位/崩潰怎麼診斷？
- A簡: 檢查指標/結構宣告與對齊，改用IntPtr/SafeHandle。
- A詳: 問題症狀描述：隨機崩潰、回傳值異常。可能原因分析：x64下指標為8位元組、結構Pack不同。解決步驟：審視DllImport、改用IntPtr、設定Layout與Pack、核對CallingConvention。預防措施：避免將指標宣告為int；以SizeOf與單元測試驗證封送對象。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q7, C-Q8

Q8: 註冊了 COM 還是「Class not registered」？
- A簡: 多半註冊到錯誤視圖；請用對應位元regsvr32/RegAsm重註冊。
- A詳: 問題症狀描述：建立COM物件失敗。可能原因分析：x86/x64視圖不符、CLSID不存在於對應視圖。解決步驟：用SysWOW64\regsvr32註冊x86 DLL；System32\regsvr32註冊x64 DLL；檢查登錄Wow6432Node。預防措施：建立註冊腳本區分位元，於安裝時執行。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q5

Q9: 出現 BadImageFormatException 時如何處理？
- A簡: 代表位元不符；調整PlatformTarget或改用對應位元的元件。
- A詳: 問題症狀描述：啟動或載入DLL拋BadImageFormat。可能原因分析：程式或依賴DLL位元不一致、PE旗標錯誤。解決步驟：統一為x86或x64；檢查組件PE與CorFlags；修正AnyCPU策略。預防措施：CI檢查架構一致性、產生多版安裝包。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q20, C-Q2

Q10: 同機需安裝 x86 與 x64 版本軟體時的衝突怎解？
- A簡: 分別安裝至對應資料夾，確保註冊於正確視圖與相依匹配。
- A詳: 問題症狀描述：兩版並存互相覆蓋設定或COM註冊衝突。可能原因分析：共用檔案或註冊未分視圖。解決步驟：安裝至Program Files與Program Files (x86)；確認COM以對應位元工具註冊；分離設定檔。預防措施：制定清晰目錄與註冊策略，並自動化檢查。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q19


### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 x86 與 x64？
    - A-Q2: x86 與 x64 的核心差異是什麼？
    - A-Q3: 為什麼需要從 32 位元轉到 64 位元？
    - A-Q5: 什麼是 WOW64？
    - A-Q7: System32 與 SysWOW64 有何差異？
    - A-Q8: Program Files 與 Program Files (x86) 的差異？
    - A-Q10: 什麼是 .NET 的 AnyCPU？
    - A-Q11: 為什麼 AnyCPU 不保證「高枕無憂」？
    - A-Q14: .NET 跨位元執行的核心價值是什麼？
    - A-Q15: 什麼是檔案系統重新導向（Redirection）？
    - A-Q16: 64 位元 Windows 中 cscript.exe 為何會有兩種？
    - B-Q3: .NET AnyCPU 的執行決策與JIT流程？
    - C-Q1: 如何在 Visual Studio 將 .NET 專案指定為 x86？
    - C-Q4: 如何在 x64 系統呼叫正確的 cscript.exe/wscript.exe？
    - D-Q9: 出現 BadImageFormatException 時如何處理？

- 中級者：建議學習哪 20 題
    - A-Q4: 16→32 與 32→64 遷移的差異？
    - A-Q6: 為何同一個 Process 不能同時載入 x86 與 x64 程式碼？
    - A-Q9: x64 上為什麼登錄機碼會有兩份視圖？
    - A-Q12: COM 元件的 x86-only 與 x64-only 有什麼影響？
    - A-Q13: 什麼是 In-Process 與 Out-of-Process COM？
    - A-Q18: 從 WPF 影像編碼與相機 RAW Codec 可以學到什麼？
    - A-Q19: 為什麼 ODBC/JET 在 x64 上常踩坑？
    - B-Q1: WOW64 相容層如何運作？
    - B-Q2: x64 系統啟動 32 位元程式的流程為何？
    - B-Q4: Windows 如何決定載入 System32 或 SysWOW64 的 DLL？
    - B-Q5: 登錄的 Wow6432Node 與 COM 解析流程是什麼？
    - B-Q6: 為何 x86 DLL 不能載入 x64 行程？
    - B-Q10: cscript/wscript 雙位元並存時如何選擇？
    - B-Q11: IIS 中 32 位元應用程式集區切換的原理？
    - B-Q15: ODBC 驅動載入的決策流程？
    - C-Q5: 如何正確註冊 32/64 位元 COM 元件？
    - C-Q6: 如何在 IIS 讓網站以 32 位元執行以載入 x86 元件？
    - C-Q10: 如何正確設定 ODBC（32/64 位元）資料來源？
    - D-Q1: AnyCPU 程式在 x64 呼叫 CDO 出現執行期錯誤怎麼辦？
    - D-Q6: 64 位元上使用 JET/某些 ODBC 驅動失敗？

- 高級者：建議關注哪 15 題
    - B-Q7: .NET P/Invoke 在 x86/x64 的差異？
    - B-Q8: 檔案系統重新導向的機制細節？
    - B-Q9: Registry Redirection 與視圖選擇如何影響應用？
    - B-Q12: Out-of-Proc COM 如何繞過位元限制？
    - B-Q13: 影像編解碼器在WPF/WIC下的位元綁定原理？
    - B-Q14: SMTP/CDO 與 .NET 的互動在 x64 上有何限制？
    - B-Q16: 常見「Class not registered」錯誤的解析流程？
    - B-Q17: 多進程協作時，IPC 技術如何選擇？
    - B-Q18: Media Encoder COM 自動化的原理？
    - B-Q20: 與 VM86 的歷史做法相比，WOW64 有何技術不同？
    - C-Q2: 如何用 CORFLAGS 或 MSBuild 強制 32 位元執行？
    - C-Q7: 如何以多進程拆分混用 x86/x64 元件？
    - C-Q8: 如何在 WPF 中處理需要 32 位元 Codec 的影像？
    - D-Q2: 32 位元程式如何處理需要呼叫 x64 COM 元件的需求？
    - D-Q7: P/Invoke 在 x64 發生參數錯位/崩潰怎麼診斷？