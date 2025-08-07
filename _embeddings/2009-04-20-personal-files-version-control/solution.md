# 個人檔案版本治理最佳化：從 VSS 到「USB Disk ＋ SVN」

# 問題／解決方案 (Problem/Solution)

## Problem: 個人文件的版本失控與編修流程卡關  
**Problem**:  
• Word、PPT 等文件在「一份母稿、客戶 A 改一版、客戶 B 再改一版」的情境下， 很快就出現檔名滿天飛 (final_v3、final_v3_fix…) 與版本搞混的困擾。  
• 需要在公司桌機、家中 PC、NB 以及客戶現場不停切換，還要隨時看得到歷史版本與差異。  

**Root Cause**:  
1. Visual SourceSafe (VSS) 以「先 Check-out Lock、再編輯」為核心，  
 • 單人/小規模檔案管理很少遇到 LOCK 衝突，但卻強迫流程。  
 • 換電腦必須先打開 VSS Explorer，再開 Word/PPT，流程中斷。  
2. VSS 網路架構採 File-Based，共用資料夾透過 VPN／Internet 時速度極慢。  
3. 一旦改檔前忘了 Check-out，Word 仍以唯讀方式開檔，需重開程式。  

**Solution**: USB Disk ＋ SVN (TortoiseSVN + VisualSVN Server)  
1. 採「先編輯、後 Commit」的 CVS/SVN 模式：不鎖檔案，不破壞思考流程。  
2. SVN 的 .svn 資訊夾直接跟在 USB 目錄裡，插到任何電腦皆可用，免額外 Workspace 設定。  
3. 先離線修改 (客戶現場／無網路)，回到辦公室再一次 Commit；同時留下可加註說明的版本點。  

**Cases 1**: 客戶簡報現場改稿  
• 情境：NB 投影簡報途中臨時被要求修改。  
• 行動：直接改完存檔→回公司插 USB→右鍵 Commit，加上「客戶 A 現場修正」說明。  
• 效益：過去需重開 VS + Check-out 的 3-5 分鐘流程縮成 10 秒完成。  

---

## Problem: Snapshot 類備份 (Windows VSS) 難以精準回溯版本  
**Problem**:  
• Windows 2003/2008 Volume Shadow Copy Service 只靠排程 Snapshot，不論檔案有無意義改動就整批保存。  
• 無法對「特定檔案 a.doc 的第 N 版」加註說明，也無法僅還原那一版。  

**Root Cause**:  
• COW + Snapshot 機制對「檔案層級意義」一無所知，只能回到某個時間點整體還原。  
• 無檔案標籤 / Comment 概念，導致「可用卻難用」。  

**Solution**: SVN 精準版本庫即時備份  
• 每一次 Commit 即產生一個具意義的 Revision，可附說明文字。  
• 只儲存差異 (Delta)；要還原僅取該檔、該版即可，效率與精準兼得。  

**Cases 1**: 調閱半年前標書  
• 過往作法：先找出正確 Snapshot→整包還原→手動比對。  
• SVN 作法：Show Log→依訊息「2012_Q3_標書_定稿」→右鍵 Export 單檔。  
• 時間從 20 分鐘降到 1 分鐘；磁碟 I/O 量減少 >90%。  

---

## Problem: 團隊級平台 (TFS) 體積龐大、環境需求複雜  
**Problem**:  
• TFS 依賴 IIS、SQL Server、SharePoint、AD，安裝與維運成本極高。  
• 開啟/連線必須透過 Visual Studio；在外簡報只為改 PPT 而開 VS，顯然不切實際。  

**Root Cause**:  
• TFS 針對多開發者、多 ALM 流程設計，並非單人文件管理使用情境。  

**Solution**: 輕量化 SVN Server (VisualSVN)  
• 可安裝在家用 PC 或小型 Windows Server，一鍵 Setup、無附帶重型元件。  
• 透過 HTTPS + 基本帳號即可遠端存取；用戶端只需 File Explorer + TortoiseSVN。  

**Cases 1**: 低規格 VM 部署  
• 1 vCPU / 1 GB RAM Windows Server 2008 R2 + VisualSVN Server。  
• 20 GB Repository 儲存 4 年文件歷程，CPU 使用率長期 <3%、RAM 佔用 <400 MB。  

---

## Problem: USB 隨身碟只靠 ZIP 備份，易遺失且版本難管理  
**Problem**:  
• 隨身碟天天插拔，忘記備份或直接遺失風險高。  
• 「每日 ZIP」只能全量壓縮，遇到文件回溯只能整包解壓，再手動翻找檔案。  

**Root Cause**:  
• ZIP 備份缺乏版本說明與差異紀錄；全量壓縮導致時間 & 空間成本高。  

**Solution**:  
1. 將 USB 根目錄作為 SVN Working Copy → 本地即同步留存一份最新檔案。  
2. Commit 時自動生成差異檔，等同「增量備份＋可讀 Metadata」。  
3. 定期再把 Repository 熱備到 NAS 或家用 Server，即完成第二道防線。  

**Cases 1**: 每日差異備份量  
• 典型工作日 200 MB 變更量 → SVN Repository 只新增 15-20 MB Delta；  
• ZIP 全量備份則需 200 MB。增量節省 90% 儲存空間，備份時間由 5 分鐘降到 20 秒。  

---

## Problem: 出門忘記帶 USB，仍需存取最新文件  
**Problem**:  
• 人在外地、手邊僅有公共電腦或平板，卻急需調閱/下載最新版本檔案。  

**Root Cause**:  
• 工作檔僅存在 USB Disk，未同步到雲端或其他主機。  

**Solution**:  
• VisualSVN Server 內建 Web UI；只要能上網，即可透過 HTTPS 瀏覽 Repository、下載任意版本檔案。  
• 若臨時具備 SVN Client，更可直接 Checkout/Update 取得工作目錄。  

**Cases 1**: 客戶臨時索取 CAD 檔  
• 忘帶 USB，在客戶現場使用對方電腦 → 瀏覽 https://myhomeip/svn/Docs → 下載 dwg v105。  
• 過往需遠端桌面回公司 PC，再用 FTP/Email 轉檔，流程耗時 20-30 分鐘；現縮短至 3 分鐘內完成。  

---

上述多重問題皆透過「USB Disk ＋ SVN」一併解決，兼具：  
• 無鎖式流暢工作流程  
• 精準差異與版本說明  
• 輕量部署、隨插即用  
• 線上／離線雙模式備份與存取  

若你也在苦惱個人文件版本與備份，可試行同樣架構並視需求再疊加第二層 Snapshot/ZIP 備援，即可達到高度彈性與安全性。