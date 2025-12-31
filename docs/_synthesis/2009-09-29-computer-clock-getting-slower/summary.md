---
layout: synthesis
title: "電腦時鐘越來越慢..."
synthesis_type: summary
source_post: /2009/09/29/computer-clock-getting-slower/
redirect_from:
  - /2009/09/29/computer-clock-getting-slower/summary/
postid: 2009-09-29-computer-clock-getting-slower
---

# 電腦時鐘越來越慢...

## 摘要提示
- 手機時鐘異常: 手機每天慢幾分鐘，兩週累積到約20分鐘，表面看似手機不準。
- 問題來源轉移: 手機透過USB同步時間，實際被家中PC帶偏，真正慢的是家中SERVER。
- 網路對時疑惑: SERVER長期連網理應對時準確，卻仍持續慢，顯示對時機制出問題。
- 架構變動關鍵: 重灌後將AD Domain Controller改裝在Hyper-V VM（Guest OS），Host負責NAT/RRAS/檔案服務。
- 時間同步循環: Hyper-V讓Guest與Host互相同步時間；Host加入網域又向DC同步，形成循環誤差累積。
- 漸進性飄移: 每次小誤差在循環中放大，幾週後造成顯著時間落後。
- 影響範圍擴大: PC被Server帶偏、手機再被PC同步，導致多設備整體時間漂移。
- 直接證據與圖示: 於Hyper-V中關閉時間同步選項後，問題立即消失。
- 修正措施: 關閉Hyper-V VM的時間同步整合功能，改讓DC對外部NTP伺服器校時。
- 經驗教訓: 複雜環境中對時路徑需明確單一來源，避免Host-Guest-AD的循環依賴。

## 全文重點
作者發現手機每日時間逐漸落後，兩週累計約二十分鐘，起初以為是手機老化或晶振不準。然而進一步檢查後發現，手機透過USB與家中PC同步時間，實際是被PC的系統時間帶偏；而PC又向家中Server（AD Domain Controller）對時，因此真正的源頭是Server的時間在持續變慢。

追查背景顯示，作者在重灌後將AD Domain Controller安裝於Hyper-V的虛擬機（Guest OS），而實體機（Host OS）負責NAT、RRAS與檔案伺服。這樣的佈局引發了關鍵問題：Hyper-V預設會讓VM與Host進行時間同步；同時Host本身加入了網域，按慣例會向網域的DC同步時間。結果造成Host與Guest（DC）之間相互同步的循環，任何微小誤差在此閉環中不斷被帶入與累積，經過幾週逐漸放大成為顯著的時間落後。

在這種循環下，Server時間不準使得PC對時也不準，最後手機透過USB同步再被帶偏，導致使用者感受到「手機越走越慢」。作者在Hyper-V的VM整合服務中關閉時間同步選項後，循環隨即被切斷，系統時間回到正常；最後改以讓網域控制站（DC）直接對外部NTP伺服器校時，建立單一可信時間來源，避免Host-Guest-AD之間相互依賴引發的誤差累積。

整體教訓是：在虛擬化與網域環境中，必須清楚規劃時間同步的權責與路徑，特別避免Host向Guest對時、Guest又受Host影響的雙向回授設計。關閉不必要的Hyper-V時間同步整合，並確保DC作為權威時間來源直接向外部NTP對時，是較穩健的做法。這次案例也提醒，即使是看似尋常的「時鐘不準」，在複雜系統中也可能需要完整的架構層面排查。

## 段落重點
### 問題現象：手機「越走越慢」
作者發現近兩週手機每日都會慢幾分鐘，最後累積到約20分鐘，與一般印象中電子裝置應該相當準確的經驗相違。更詭異的是，手機在公司白天似乎是準的，顯示問題與環境有關。由於手機會在家中以USB充電與同步，進一步懷疑手機的時間來源可能被外部設備影響，而非單純硬體老化。這個初步跡象導向對家中PC與Server的時間狀態進行檢查。

### 追查過程：從手機到PC再到Server
先確認手機與PC同步，發現PC的系統時間其實不準，於是再追到PC的上游時間來源——家中的Server（AD DC）。正常來說，一台長期上網的Server會與外部NTP服務同步，時間應該可靠；然而實測顯示Server仍然在逐步落後，表示內部時間同步機制存在異常。這層層回溯的過程，將問題從手機本體聚焦到家庭網路架構與對時設定。

### 架構與根因：Hyper-V時間同步循環
重灌後的架構是：DC裝在Hyper-V的VM（Guest OS），而Host OS提供NAT/RRAS/檔案服務。Hyper-V預設啟用VM與Host的時間同步整合；同時Host已加入AD網域，會向DC同步時間。這造成Host與Guest之間的雙向回授：Host受DC影響，Hyper-V又讓Guest受Host影響，形成循環同步。任何微小的時鐘偏差都會在此閉環中被帶入並逐步累積，長期下來導致Server顯著落後，進而牽連PC與手機的時間。這種「看似方便」的同步選項，在特定拓撲下反而成為誤差放大的來源。

### 解法與建議：切斷閉環、指定權威來源
作者在Hyper-V的VM設定中關閉時間同步整合服務後，問題立即消失，證實時間循環為根因。最終做法是讓網域控制站（DC）直接向外部NTP伺服器對時，成為網域內的單一權威時間來源；Host則不再透過Hyper-V回授影響Guest。建議在包含虛擬化與AD的環境中，務必規劃清楚時間同步路徑：避免Host-Guest互相依賴造成循環，關閉不必要的同步選項，並確保DC對外對時，其他成員向DC單向對時。這能防止小誤差累積成大偏差，維持整體系統時間的一致與可靠。

## 資訊整理

### 知識架構圖
1. 前置知識：  
   - 基本時間同步概念（本機時鐘、網路時間 NTP/W32Time）  
   - 虛擬化基礎（Hyper-V Host/Guest、整合服務 Integration Services）  
   - Active Directory 時間階層（PDC Emulator 與網域成員的對時關係）  
   - Windows 服務與角色（Domain Controller、RRAS/NAT、File Server）

2. 核心概念：  
   - 時間同步來源一致性：系統中只能有單一權威時間來源，避免循環同步。  
   - 虛擬機與主機的時間同步：Hyper-V 預設會讓 Guest 與 Host 同步時間。  
   - AD 網域時間架構：網域成員向 DC 對時，網域的 PDC Emulator 應向外部可靠 NTP 對時。  
   - 循環依賴（時間回路）：Host 向 DC 對時、DC（Guest）又由 Hyper-V 向 Host 對時，導致時間漂移累積。  
   - 端點連鎖效應：PC 時間錯誤會牽連同步到手機或其他裝置，擴大影響範圍。

3. 技術依賴：  
   - Windows Time Service（W32Time）依賴於網域角色（PDC Emulator）與外部 NTP。  
   - Hyper-V Integration Services 的 Time Synchronization 會覆寫 Guest 內部時間。  
   - AD 成員電腦的時間依賴 DC；DC 若為 VM 又依賴 Hyper-V 設定。  
   - 手機/客戶端與 PC 的同步（USB Sync/ActiveSync）依賴 PC 的正確時間。

4. 應用場景：  
   - 在家用/小型實驗網路中跑虛擬化 AD DC 的環境。  
   - 企業中將 DC 虛擬化並與 Host 同時加入同一網域。  
   - 任何需同時管理多層對時來源（外部 NTP、Host、Guest、用戶端）的情境。  
   - 需排除長期時間漂移造成之驗證失敗、排程錯誤、日誌對齊問題的環境。

### 學習路徑建議
1. 入門者路徑：  
   - 了解電腦時鐘與網路時間同步的基本概念（NTP、W32Time）。  
   - 學會檢查與手動對時（Windows：日期與時間設定、簡單 w32tm /query）。  
   - 觀察端到端影響（手機/裝置會跟 PC 同步，PC 與網域/網際網路同步）。

2. 進階者路徑：  
   - 學習 AD 時間階層與 PDC Emulator 的角色與責任。  
   - 熟悉 Hyper-V Integration Services（特別是 Time Synchronization）設定與影響。  
   - 能讀懂並調整 W32Time 設定（對外部 NTP、輪詢間隔、偏差控制）。

3. 實戰路徑：  
   - 在 Hyper-V 上承載 DC 時，關閉該 VM 的 Time Synchronization 整合服務，避免由 Host 覆寫。  
   - 指定網域 PDC Emulator 對齊外部可靠 NTP（如 pool.ntp.org 或政府/學術機構 NTP）。  
   - 以 w32tm 和事件檢視器持續監控時間狀態與偏差，驗證無循環同步與偏移累積。

### 關鍵要點清單
- 單一權威時間來源：確保網域中只有一個權威時間源（通常是 PDC Emulator），避免多重來源造成漂移或衝突。（優先級: 高）
- 避免時間循環：杜絕 Host↔Guest 的對時回路；Host 向 DC 對時時，不可讓 DC 再向 Host 對時。（優先級: 高）
- 關閉 DC VM 的 Hyper-V 時間同步：對於擔任 DC 的虛擬機，停用 Hyper-V Integration Services 的 Time Synchronization。（優先級: 高）
- PDC Emulator 對外同步：設定 PDC Emulator 與可靠外部 NTP 伺服器同步，成為網域內權威時間來源。（優先級: 高）
- 成員電腦對時路徑：一般網域成員應向其 DC 對時，不直接對外，維持層級一致性。（優先級: 中）
- 監測時間偏差：使用 w32tm /query、事件檢視器（System/W32Time）定期檢查漂移與同步狀態。（優先級: 中）
- 虛擬化最佳實務：對虛擬化的關鍵基礎設施（DC、AD FS、CA）特別審視時間同步設定。（優先級: 中）
- 端點連鎖影響意識：了解 PC 時間錯誤會連帶影響手機、排程、Kerberos 驗證與日誌時間。（優先級: 中）
- 重灌/搬遷風險：系統重裝、拓撲變更（如把 DC 移到 VM）時，重新審視時間同步配置。（優先級: 中）
- Host 網域身分影響：當 Hyper-V Host 加入同一 AD 網域時，更要避免與 DC VM 之間的雙向同步。（優先級: 中）
- 硬體時鐘與電池：留意 Host/主機板 RTC 與電池狀態，避免硬體層造成大幅漂移。（優先級: 低）
- 設定外部 NTP 清單：使用多個權威 NTP（含權重/同層多源）以提高穩定性與可用性。（優先級: 低）
- 同步間隔與偏差門檻：適度調整 poll 間隔與允許偏差，平衡網路負載與準確度。（優先級: 低）
- 變更後驗證：每次變更 Hyper-V 或 W32Time 設定後，觀察數日確認不再累積偏移。（優先級: 中）
- 文件化與告警：將時間源與設定納管到文件，並設告警監測超出閾值的時間漂移。（優先級: 低）