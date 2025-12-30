---
layout: synthesis
title: "Vista 初體驗 - (DISK篇)..."
synthesis_type: summary
source_post: /2007/03/28/vista-first-experience-disk-edition/
redirect_from:
  - /2007/03/28/vista-first-experience-disk-edition/summary/
---

# Vista 初體驗 - (DISK篇)...

## 摘要提示
- Volume Shadow Copy: Vista 內建 VSS 讓個人電腦也能使用檔案版本保護，補起 XP 時期讓人不安的缺口。
- 家用伺服器轉桌機: 作者把原本檔案伺服器職能移到桌機，VSS 彌補照片等重要檔案被誤刪的風險。
- RAID-1 期待: 雖可用主機板內建 RAID-1，但期望微軟未來能內建更可靠的軟體 RAID 支援。
- Windows Complete PC: Vista（Ultimate）內建磁碟映像工具，出乎意料地以 VHD 為儲存格式。
- VHD 生態: VHD 與 Virtual PC/Server 生態相通，未來把實體 Vista 直接搬進 VM 的流程更順暢。
- 工具整合: Virtual Server 2005 R2 SP1 將提供 VHD 掛載，進一步打通備份、還原與虛擬化。
- iSCSI Initiator 內建: Vista 直接內建 iSCSI Initiator，顯示用戶端已準備好走向網路化儲存。
- 微軟復用策略: 微軟透過元件化與重用（如 IE 嵌入各處）建立不可取代性，成為戰略優勢。

## 全文重點
作者在試用兩天 Vista 後，集中分享與磁碟/儲存相關的三項驚喜。首先，Vista 將 Volume Shadow Copy（VSS）下放到用戶端，讓他把檔案伺服器職能搬到桌機後，仍能以快照保護重要資料（如家庭相片）免於誤刪；相較 XP 時期缺乏 VSS 的不安，Vista 的補強讓個人端也有企業級的資料回溯保護。雖然硬體層面的鏡像可交由主機板 RAID-1 承擔，但作者仍期盼微軟能提供更可靠的系統層 RAID 支援。

其次，Vista Ultimate 內建的 Windows Complete PC（整機映像）讓人驚艷不在於功能本身，而是它採用 VHD 作為映像格式。VHD 是微軟虛擬化生態的核心標準，Virtual PC/Server 均使用它作為虛擬磁碟；加上微軟開放 VHD 規格並將在 Virtual Server 2005 R2 SP1 提供 VHD 掛載工具，意味著從實體機做系統映像、到在 VM 直接掛載並啟動，遷移與備援流程將極為順暢，傳統的 Ghost 類工具不再具備相同的生態優勢。

第三，Vista 直接內建 Microsoft iSCSI Initiator，雖然該工具早已可免費下載，但進入預設配置代表用戶端已為 iSCSI 儲存就緒。作者進一步聯想：若未來 Windows Server 內建 iSCSI Target 並以 .vhd 作為後端格式，則虛擬機可望直接自 iSCSI Target 掛載並開機，先前需自行拼湊的解決方案可能將成為內建能力。

最後，作者由此延伸到微軟一貫的「軟體重用」與「平台化」戰略：不只是在產品上比拚功能，而是將核心元件（如瀏覽器 IE）以 SDK 與嵌入能力滲入系統與應用各處，從 HTML Help、檔案總管到各式管理工具、甚至遊戲面板都能看到 IE 的影子。這種可重用、可擴展、可整合的策略，使微軟在 Office、瀏覽器戰爭到虛擬化與 .NET 等關鍵戰場屢屢取勝。作者期待在 Vista 中持續挖掘更多此類「驚喜」。

## 段落重點
### Volume Shadow Copy：個人端也能有企業級檔案回溯
作者將原檔案伺服器工作移到桌機後，最在意的是資料保護能否延續。以往在伺服器上同時使用 RAID-1 與 VSS，既防硬碟故障也防誤刪；但換到 XP 時缺乏 VSS，讓家庭照片等重要檔案暴露在誤操作風險中。Vista 將 VSS 下放到用戶端，讓他重拾信心：當吳小皮或家人誤刪檔案時，可以快速從快照回復。雖然硬體層的 RAID-1 仍可藉由主機板實現，但作者不諱言擔憂主機板 RAID 的可靠性，期待微軟將更成熟的軟體 RAID 能力納入系統，形成「硬體容錯 + 檔案回溯」的雙重保護，讓家用與 SOHO 場景也能達到近似企業級的資料安全水準。

### Windows Complete PC 與 VHD：備份、還原到虛擬化的一條龍
Vista Ultimate 內建的 Windows Complete PC 可做整機映像，看似只是「內建的 Ghost」，真正驚喜在於其輸出格式是 VHD。VHD 作為微軟虛擬化堆疊的核心標準，早已被 Virtual PC 與 Virtual Server 廣泛使用；微軟又在一年前公開 VHD 規格，並規劃在 Virtual Server 2005 R2 SP1 提供 VHD 掛載工具。這種標準化與工具鏈布局，使一個實體 Vista 的映像檔能直接被虛擬機掛載與啟動，讓實體到虛擬（P2V）、災難復原、測試環境複製與異地備援更為便捷。傳統第三方映像工具若缺乏與虛擬化生態的深度整合，在可攜性與自動化流程上將相形失色。作者認為這種從備份格式即對齊虛擬化標準的設計，正是微軟「產品線協同」的實例。

### 內建 iSCSI Initiator：為網路化儲存與雲端化鋪路
Vista 內建 Microsoft iSCSI Initiator 本身並非新功能，但預設可用象徵用戶端對網路化區塊儲存（SAN over IP）的就緒。作者據此推測：若未來 Windows Server 內建 iSCSI Target，並以 .vhd 作為後端檔案格式，則用戶端與虛擬機可透過 iSCSI 直接掛載 VHD 進行開機或資料存取，形成「VHD 標準 + iSCSI 傳輸 + VM 啟動」的閉環。這將把他過去需東拼西湊才能實現的方案，轉化為原生與受支援的體驗。從家庭/小型辦公到企業機房，從本機映像到網路儲存，微軟正以一致的格式與協定把備份、遷移、虛擬化與存取串接起來，降低部署與維運的複雜度。

### 微軟的重用與平台化戰略：從 IE 到虛擬化的勝負手
收束於策略層面，作者指出微軟善於把單點功能平台化，透過 SDK 與元件重用去擴大滲透率並形成生態黏著。當年與 Netscape 的瀏覽器大戰，微軟不僅是把 IE 做好並綁入系統，更讓 IE 作為可被廣泛嵌入的元件：HTML Help、檔案總管、桌面元件、MSN Messenger 內的遊戲與眾多管理工具皆可見其身影。即使使用第三方瀏覽器，許多系統與企業軟體仍依賴 IE 元件，讓 IE 難以被完全取代。這種策略在 Office、.NET 以至今日的虛擬化與儲存布局（VHD、Complete PC、iSCSI）皆可見：以統一格式、API 與工具鏈，將產品線串接，賦能開發者與管理者，同時築高轉移成本。作者也因此期待在 Vista 中持續挖掘更多這類「被藏起來的」驚喜與協同效應。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 基本作業系統概念（Windows Vista/XP、檔案系統 NTFS）
   - 儲存技術基礎（RAID、快照/還原點、備份與還原）
   - 虛擬化基本概念（VHD、Virtual PC/Virtual Server）
   - 網路儲存概念（iSCSI 的 initiator/target 角色分工）

2. 核心概念：
   - Volume Shadow Copy（VSS）：在用戶端提供檔案層級的歷史版本與快照還原，補足誤刪/誤改的防護
   - Windows Complete PC（映像備份）：系統層級的整機映像備份，輸出為 VHD 格式
   - VHD 格式與虛擬化生態：備份映像可直接作為虛擬機磁碟使用，強化 P2V 流程與一致性
   - iSCSI Initiator 內建：客戶端直連區塊儲存的能力，鋪墊未來與伺服器端 iSCSI Target 的整合
   - Microsoft 的軟體重用/整合策略：跨產品共用技術（如 IE、VHD、管理工具），擴大生態鎖定力

3. 技術依賴：
   - VSS 依賴 NTFS 與 Shadow Copy Service；與本機/網路磁碟的支援狀態相關
   - Windows Complete PC 依賴 Vista（作者提到 Ultimate 版）功能；映像檔為 VHD
   - VHD 可由 Virtual PC/Virtual Server 掛載；VS 2005 R2 SP1 提供 VHD mount 工具
   - iSCSI Initiator 需網路與對應的 iSCSI Target；若未來 Windows Server 內建 Target，將簡化端到端部署
   - RAID 為硬體/主機板方案，與 VSS 層級不同（硬體容錯 vs. 軟體快照）

4. 應用場景：
   - 家用/小型辦公室的檔案保護：重要照片與文件的誤刪誤改還原（VSS）
   - 整機災難復原與異機還原：快速回復系統狀態（Complete PC 映像）
   - P2V 遷移與測試：將實體機映像直接掛為 VM 磁碟進行啟動與驗證（VHD）
   - 集中式儲存與擴充：用 iSCSI 連接共享區塊儲存，可能進一步搭配 VM 從 iSCSI 啟動
   - 系統維運流程優化：用一致格式（VHD）貫通備份、測試、部署

### 學習路徑建議
1. 入門者路徑：
   - 了解備份種類（檔案層級 vs. 映像層級）與快照概念
   - 在 Vista 啟用並測試 VSS（檔案「以前的版本」還原）
   - 建立一次 Windows Complete PC 映像備份，熟悉備份與還原流程
   - 認識 VHD 基本概念（它是什麼、能被哪些工具掛載）

2. 進階者路徑：
   - 以 Virtual PC/Virtual Server 測試掛載 Vista 的 VHD 映像，驗證 P2V 可行性
   - 研究 iSCSI 架構，安裝並設定 Initiator，連線至測試用 Target
   - 規劃多層防護：硬體 RAID 搭配 VSS 與映像備份的恢復演練
   - 探索 VHD 工具鏈（掛載、轉換、檢查）與自動化腳本

3. 實戰路徑：
   - 在桌機/小型檔案伺服器部署 VSS 以保護關鍵資料夾（如照片庫）
   - 制定映像備份週期，保存多版本 VHD，並定期演練還原到 VM
   - 建置 iSCSI 測試環境，驗證客戶端透過 Initiator 存取區塊儲存的效能與穩定度
   - 建立標準作業流程：備份、版本管理、異地保存、還原驗證報告

### 關鍵要點清單
- Volume Shadow Copy（VSS）：提供檔案歷史版本與快速還原，降低誤刪誤改風險（優先級: 高）
- RAID vs. VSS 分工：RAID 解決硬體故障，VSS 解決人為操作錯誤，兩者互補（優先級: 高）
- Windows Complete PC（映像備份）：系統層級完整備份，支援災難復原（優先級: 高）
- VHD 格式通用性：映像備份以 VHD 儲存，可直接被虛擬化平台使用（優先級: 高）
- P2V 流程簡化：以映像備份輸出 VHD，直接掛載到 VM 測試與啟動（優先級: 高）
- Virtual PC/Virtual Server 支援：原生支援 VHD，並提供 VHD 掛載工具（優先級: 中）
- iSCSI Initiator 內建：用戶端可直連區塊儲存，為集中式儲存整合鋪路（優先級: 中）
- 未來 iSCSI Target 期待：若伺服器內建 Target，將強化端到端 Windows 儲存解決方案（優先級: 中）
- 多層備援策略：RAID + VSS + 映像備份，兼顧可用性與可恢復性（優先級: 高）
- 測試與演練重要性：定期掛載 VHD/還原驗證，確保備份可用（優先級: 高）
- 檔案系統與相容性：VSS 依賴 NTFS 與系統服務，需確認磁碟與版本支援（優先級: 中）
- 效能與容量規劃：快照與映像會佔用空間，需預留儲存與排程時間窗（優先級: 中）
- 微軟整合策略洞見：跨產品重用技術（如 IE、VHD）擴大生態與競爭優勢（優先級: 低）
- 家用照片保護案例：以 VSS 抵禦家中成員誤刪，符合真實需求（優先級: 中）
- 工具鏈與自動化：運用腳本與工具管理 VHD、備份與還原，提高效率（優先級: 低）