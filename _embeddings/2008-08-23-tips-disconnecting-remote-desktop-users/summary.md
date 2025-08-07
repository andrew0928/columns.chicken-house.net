# Tips: 踢掉遠端桌面連線的使用者

## 摘要提示
- 連線人數限制: Windows Server 預設僅提供 2 條管理員 RDP 連線，滿額時將導致其他人無法登入。  
- Console Session: 透過在 mstsc 後加 /console 參數可直接佔用本機主控台，不與一般遠端連線競爭名額。  
- 工作管理員: 進入 Console Session 後於「使用者」頁即可查看並中斷特定 Session。  
- Session ID: 每條遠端桌面連線皆有獨立 ID，0 代表 Console，其餘為額外連線。  
- TSDISCON 指令: 當所有名額皆滿時，可使用 TSDISCON <ID> /SERVER:<伺服器> 斷線指定 Session。  
- 權限需求: 執行 TSDISCON 需具備遠端伺服器系統管理員權限，且網路須允許 NetBIOS。  
- NET USE 預登入: 透過 NET USE \\Server /user:Account * 先建立驗證，可避免權限不足。  
- 授權考量: 未購買額外 TS CAL 時，Windows 內建授權僅限 2 條管理員連線，過度使用可能違規。  
- 應急策略: 先踢掉佔線者再迅速登入，可降低對方重新連線的機率。  
- 秘技心法: 任何「秘技」一旦公開即成常識，故理解原理才是長久之計。  

## 全文重點
本文由作者親身經驗出發，說明當 Windows Server 遠端桌面連線數達到上限、無法再登入時，系統管理員可以採取的兩種緊急處置方法。首先介紹以 `/console` 參數登入本機主控台 Session 的技巧：由於 Console Session 不佔用一般的兩條 RDP 名額，因此可以在其他使用者已滿時仍強行登入。登入後開啟工作管理員「使用者」分頁，即可看到所有遠端連線的 Session ID、使用者名稱與狀態，直接選擇「中斷連線」即可踢人。此方法對 90% 的案例都有效。

若連 Console Session 也被其他管理員占用，就需動用更低層的命令列工具 TSDISCON。步驟為：先使用 `NET USE \\MYSERVER /user:MYACCOUNT *` 建立與伺服器的驗證，再下 `TSDISCON 1 /SERVER:MYSERVER`，其中 1 為要中斷的 Session ID。TSDISCON 會即時斷線指定連線，使用者會被強制登出。因 Windows 預設僅有 0 (Console) 與 1、2 兩條管理員連線，故大多可直接測試 1 或 2，即可恢復一條空位，管理員便能重新以一般方式遠端登入。

作者提醒，執行 TSDISCON 必須具備伺服器管理員權限，且防火牆不能封鎖 NetBIOS；若企業需長期多連線，應購買合規的 Remote Desktop Services CAL。最後強調「秘技」公開後就不再神祕，重點在於理解 Windows 遠端桌面與 Session 管理的原理，才能靈活應對各種維運狀況。

## 段落重點
### 1. 問題情境與 RDP 連線限制
作者回憶同事因「連線人數已滿」而無法登入伺服器的窘境。Windows 2000 之後雖內建 RDP，但標準安裝只允許兩條管理員連線；若同時有三人欲連，就會鎖在登入畫面。此限制是許多初級維運人員常忽略的痛點，也是本文提出解法的出發點。

### 2. 使用 /console 參數進入 Console Session
在 mstsc 命令加上 `/console`（新版本為 `/admin`）即可連進伺服器的本機主控台 Session，此 Session 特殊之處在於不計入一般 RDP 連線限制。成功登入後，開啟工作管理員的「使用者」分頁，即可查看所有 Session ID、使用者名稱與狀態。管理員可透過「中斷連線」或「登出」功能立即釋放名額，通常這步驟即可解決大多數「塞車」問題。

### 3. TSDISCON：命令列強制中斷 Session
若連 Console Session 也被佔用，只能依賴 `TSDISCON.exe`。使用流程：
1. `NET USE \\MYSERVER /user:MYACCOUNT *` 以管理員身分建立隱含登入。
2. `TSDISCON <SessionID> /SERVER:MYSERVER` 斷線指定 Session。
Session ID 在工作管理員中可查，也可先抓常見的 1 或 2 測試。執行後，被踢的用戶端會立即顯示「遠端桌面連線已中斷」，釋放出的名額就能被管理員接手，確保維運作業不中斷。

### 4. 授權與操作注意事項
TSDISCON 雖強大，但需注意：
- 需具管理員權限與 NetBIOS 通訊。
- 未購買 RDS CAL 時，仍只能合法使用兩條管理員連線；若組織長期需要多人連線，應盡速購買授權。
- 強踢用戶端可能導致未儲存資料遺失，操作前應先嘗試通知對方或確認系統狀態。

### 5. 結語：秘技成常識，重在理解原理
作者最後提醒，所有「秘技」公開後即不再神祕，真正關鍵是理解 Windows Terminal Services 的 Session 機制。只要掌握 Console Session 與 TSDISCON 的原理與使用情境，面對 RDP 塞車或遠端維運突發狀況，即可迅速、正確地排除障礙，維護系統穩定。