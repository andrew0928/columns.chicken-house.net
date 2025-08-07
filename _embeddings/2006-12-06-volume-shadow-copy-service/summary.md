# Volume Shadow Copy Service 簡易介紹與批次備份應用

## 摘要提示
- Copy-on-Write: VSS 透過「寫入時複製」機制，在極短時間內完成磁碟快照而不影響原始資料。
- Snapshot: 快照是一種在檔案系統層以下作標記的技術，未變動的區塊不需實際複製即可保留歷史狀態。
- Provider 架構: Windows 2003 的 VSS 開放 Provider 介面，讓 SQL2005、Exchange2007 等應用可延伸出更完整的備份與還原功能。
- GUI 與網芳操作: 透過磁碟內容頁與網路芳鄰可直接檢視或還原特定時間點的檔案。
- 進階需求: 作者需要「真實複製」的備份，並能隨時執行、避免檔案鎖定問題。
- 批次自動化: 結合 vssadmin.exe 建立/刪除快照與 RAR.exe 封裝，完成一條龍批次備份。
- UNC 路徑存取: 快照會以 \\localhost\D$\@GMT-YYYY.MM.DD-HH.MM.SS 形式對外提供唯讀存取。
- 範例指令: RAR.exe a -r c:\backup.rar \\nest\Home\@GMT-2006.11.28-23.00.01 將指定時間點檔案打包。
- 系統限制: 目前完整自動化僅適用 Windows Server 2003；XP 功能不完整，Vista 是否支援尚待確認。
- 實務收穫: 透過快照路徑與命令列工具，解決多年來備份時檔案被鎖定或需關閉應用程式的困擾。

## 全文重點
Windows Server 2003 隨附的 Volume Shadow Copy Service（VSS）雖稱不上新功能，但在企業與進階使用者的日常維運中極為實用。VSS 工作於檔案系統之下，透過 Copy-on-Write 機制在數十毫秒內建立快照；只要檔案未被修改，就不需要實體複製任何資料，因此效能衝擊極低。當有寫入動作時，系統先複製原區塊再寫入新資料，確保快照保留建立當下的完整狀態。

Windows 2003 進一步提供 Provider 架構，讓第三方或微軟自家軟體（如 SQL Server 2005、Exchange 2007、Data Protection Manager 2006）得以利用同一套機制擴充更進階的備份、複寫與還原功能。對一般使用者而言，僅需在磁碟內容的「Shadow Copy」頁面排程快照，即可在網路芳鄰以滑鼠右鍵「Previous Versions」檢視或還原歷史檔案。

然而作者面臨更嚴謹的備份需求：必須將資料真正複製到其他儲存裝置，且執行時不可受檔案鎖定影響，同時希望藉由批次檔隨時手動或排程觸發。解決方案是：先用 vssadmin.exe 建立快照，再從快照對應的唯讀 UNC 路徑（格式為 \\主機\磁碟$\@GMT-時間戳）進行檔案複製或壓縮，最後視需要移除快照。如此一來，備份作業永遠針對靜態快照進行，不會被系統或應用程式占用所阻擾。

整體流程：
1. vssadmin create shadow /for=d: 建立快照並取得時間戳。
2. RAR.exe a -r c:\backup.rar \\localhost\d$\@GMT-YYYY.MM.DD-HH.MM.SS\  將快照內容封裝。
3. vssadmin delete shadows /for=d: /oldest 移除快照或保留作多版本。

此方法雖簡易，卻足以解決作者多年「備份前必須先關程式」或「複製途中檔案被鎖定」的痛點。惟需要注意，完整的 vssadmin 與 UNC 快照路徑僅於 Windows Server 2003 提供；Windows XP 功能受限，Vista 是否支援類似操作則有待實測。

## 段落重點
### 1. VSS 與 Copy-on-Write 基礎
作者首先說明 VSS 在 Windows 2003 中所扮演的角色。它位於檔案系統之下，以 Copy-on-Write 技術在極短時間內標記快照。當快照存在時，如有檔案寫入動作，系統先複製原區塊再更新，使得快照保持建立當下的完整性。這與傳統「先複製再寫入」的備份方式不同，速度快又省空間。

### 2. Provider 架構與企業應用
VSS 不僅服務檔案系統，也開放 Provider 架構給各種軟體。Microsoft SQL Server 2005、Exchange 2007 以及 Data Protection Manager 2006 等皆能利用 VSS 建立資料庫層級的快照與備份。此機制讓第三方備份工具得以整合，提供一致性備份與還原流程，大幅提升企業環境的資料保護能力。

### 3. GUI 快照操作與一般使用者體驗
對多數使用者而言，VSS 的操作並不困難：在磁碟屬性裡啟用 Shadow Copy，並設定排程後，系統即可定時保存磁碟狀態。透過網路芳鄰或檔案總管的「Previous Versions」功能，不僅能瀏覽舊檔，也可將特定版本還原。此特性對誤刪檔案或覆寫錯誤的緊急救援特別方便。

### 4. 進階批次備份需求與命令列實作
作者有「真正複製」的需求，並希望避開檔案鎖定問題。最終解法是透過 vssadmin.exe 建立快照，使用 \\localhost\磁碟$\@GMT-時間戳 的 UNC 路徑讀取唯讀快照，再配合 RAR.exe 或其他備份工具封裝。流程完成後，視情況刪除快照。範例指令：  
vssadmin create shadow /for=d:  
RAR.exe a -r c:\backup.rar \\nest\Home\@GMT-2006.11.28-23.00.01  
vssadmin delete shadows /for=d: /oldest  
此組合解決了多年來備份時檔案被鎖定或需關閉應用程式的痛點，但完整功能僅限 Windows Server 2003，其他版本支援度有限。

