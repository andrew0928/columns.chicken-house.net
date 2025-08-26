# Using VHDMount with Virtual PC

## 摘要提示
- 發佈背景: Microsoft Virtual Server 2005 R2 SP1 釋出，新增硬體輔助虛擬化與 VHDMount。
- VHDMount 定義: 讓使用者在主機系統直接掛載 VHD 檔的工具，類似虛擬光碟掛載 ISO。
- 使用便利: 可不開機 Guest OS 即可修改 VHD 內容，提升維護與測試效率。
- 變更控制: 掛載時啟用 Undo Disk 機制，卸載時可選擇是否提交變更。
- 與 VPC 相容: VPC 與 VS2005 R2 SP1 的 VHD 格式互通，可安心交互使用。
- 安裝建議: 僅安裝 VS 的 VHDMount 工具即可在 XP/VPC 環境受益，無需完整安裝 VS。
- 與 VMware 對比: VMware 早有類似功能，微軟此版本終於補齊。
- 需求缺口: 市面常見虛擬裝置多為讀取裝置，仍缺少「虛擬燒錄器」的支援。

## 全文重點
本文以 Microsoft Virtual Server 2005 R2 SP1 的發佈為起點，重點介紹隨之提供的 VHDMount 工具。VHDMount 讓使用者能在主機作業系統直接掛載 VHD（Virtual Hard Disk）檔案，就像使用虛擬光碟軟體把 ISO 檔「放進」虛擬光碟機一樣，只是目標從光碟映像改為硬碟映像。此功能意味著，維護或修改虛擬機器硬碟內容時，不必再啟動虛擬機器中的客體系統（Guest OS），大幅提升日常管理、故障排除或批次作業的效率。

微軟在這次的實作上也整合了 Undo Disk 機制：在掛載 VHD 時會啟用變更追蹤，卸載時可選擇是否提交（commit）這些修改。這對於測試與驗證相當有利，因為可以先嘗試變更，最後再決定要不要保留。作者同時指出，VMware 早已提供類似工具，這次等於是微軟在功能層面上補齊差距。

由於 Virtual PC 與 Virtual Server 2005 R2 SP1 採用相同的 VHD 格式，兩者之間可互通。實務上，即便日常只使用 Virtual PC，也可以在 Windows XP 上安裝 Virtual Server 的元件時，僅選擇安裝 VHDMount，即可享有直接掛載 VHD 的便利。這種「精簡安裝」方式避免了完整部署 Virtual Server 的複雜度，卻能把 VHDMount 的效益帶到 VPC 的工作流程中。

文章最後以輕鬆的抱怨收尾：雖然虛擬化技術已相當普及，虛擬光碟也很常見，但市場上仍缺乏能模擬「燒錄器」的虛擬工具；不論是一般虛擬光碟程式或虛擬機器平台，都鮮少提供可「寫入」的虛擬燒錄器支援，形成一個尚未被滿足的需求。

## 段落重點
### VS2005 R2 SP1 發佈與 VHDMount 登場
作者指出 Microsoft Virtual Server 2005 R2 SP1 已在兩週前釋出，帶來硬體輔助虛擬化支援，並附上可在主機作業系統直接掛載 VHD 的工具 VHDMount。這代表微軟在虛擬化管理工具鏈上向前邁進，讓管理者不必透過虛擬機器本身也能處理 VHD 檔案。

### VHDMount 的定位：像掛 ISO 一樣掛 VHD
文中以熟悉的虛擬光碟使用情境作對比：以往大家會用虛擬光碟軟體把 ISO 當成光碟片掛載，VHDMount 的概念一致，差別只在對象從 ISO 變成 VHD。此類比清楚說明了 VHDMount 的價值—在主機端直接讀寫虛擬硬碟內容。

### 功能亮點與對比 VMware：Undo Disk 與提交選擇
作者提到 VMware 早已提供相近工具，如今微軟終於補上。更進一步的是，VHDMount 在掛載時會啟用 Undo Disk，卸載時可選擇是否提交變更，讓使用者能先試後定，對於維運、測試與回溯極為友善，降低了操作風險與成本。

### VPC 與 VS 的 VHD 相容與安裝建議
因 Virtual PC 與 Virtual Server 2005 R2 SP1 採用相同 VHD 格式，彼此可以互通。作者建議，即便只用 Virtual PC，也可在 XP 上安裝 Virtual Server 時僅勾選 VHDMount，無需安裝完整 VS。如此即可在 VPC 的日常工作中享有直接掛載 VHD 的便利，省時省力。

### 小吐槽：虛擬燒錄器的缺席
文章最後感嘆雖然虛擬化百花齊放，但仍缺乏「虛擬燒錄器」這類能模擬寫入行為的工具。無論是虛擬光碟軟體或虛擬機器平台，普遍只支持讀取型的虛擬裝置，沒有能完整模擬燒錄器的方案，成為實務工作中的一個遺憾與待補空白。

## 資訊整理

### 知識架構圖
1. 前置知識：學習本主題前需要掌握什麼？
- 了解虛擬化基本概念（Host OS、Guest OS、虛擬硬體）
- 認識磁碟映像檔格式差異（ISO vs VHD）
- 基本的 Virtual PC/Virtual Server 安裝與使用概念
- 檔案系統與磁碟掛載/卸載的基本操作與風險

2. 核心概念：本文的 3-5 個核心概念及其關係
- VHDMount：在 Host OS 直接掛載 VHD 的工具，支援暫存變更與可選擇提交
- VHD 格式相容性：Virtual PC 與 Virtual Server 2005 R2 SP1 的 VHD 互通
- Hardware Assisted Virtualization：Virtual Server 2005 R2 SP1 新增支援（背景提升）
- 與虛擬光碟相比：VHDMount 類似虛擬光碟工具，但對象為硬碟映像（VHD vs ISO）
- 變更管理（Undo/Commit）：掛載期間的變更可在卸載時選擇是否寫回

3. 技術依賴：相關技術之間的依賴關係
- Virtual Server 2005 R2 SP1 提供 VHDMount 工具 → 需在 Host OS 安裝
- Virtual PC/Virtual Server 使用相同 VHD 格式 → 確保掛載後可在兩者間共享
- Host OS 檔案系統與權限 → 影響 VHD 掛載、讀寫與提交動作
- 硬體虛擬化支援（背景）：提升虛擬化體驗，但不直接影響 VHDMount 的基本功能

4. 應用場景：適用於哪些實際場景？
- 直接在 Host OS 修改 VHD 內容（免開機 Guest OS）
- 快速抽取或注入檔案、修正設定、更新工具/腳本至 VHD
- 測試變更後選擇是否提交，避免破壞原始 VHD
- 在僅使用 Virtual PC 的環境，透過安裝 Virtual Server 的 VHDMount 得到進階工作流

### 學習路徑建議
1. 入門者路徑：零基礎如何開始？
- 認識 VHD 與 ISO 的差異與用途
- 安裝 Virtual PC（或了解其基本運作）
- 下載並安裝 Virtual Server 2005 R2 SP1，僅選擇安裝 VHDMount
- 練習將一個範例 VHD 掛載與卸載，觀察檔案系統變化

2. 進階者路徑：已有基礎如何深化？
- 練習使用 VHDMount 的 undo/commit 流程，體會不提交與提交的差異
- 建立一套修改 VHD 的工作流程（備份→掛載→變更→測試→決定提交）
- 在 Virtual PC 與 Virtual Server 間交互使用同一 VHD，驗證相容性
- 制定版本與變更管理策略，避免覆寫或誤提交

3. 實戰路徑：如何應用到實際專案？
- 在開發/測試環境中，使用 VHDMount 注入套件、更新檔或修復檔案
- 建置自動化腳本（批次掛載→注入→驗證→卸載→選擇提交）
- 對重要 VHD 建立基線與備份，並以「先不提交」驗證變更安全性
- 針對團隊流程撰寫 SOP：誰能掛載、何時提交、如何回復

### 關鍵要點清單
- VHDMount 基本功能: 在 Host OS 直接掛載 VHD，免啟動 Guest OS 即可讀寫內容 (優先級: 高)
- 變更提交選擇: 卸載時可決定是否將變更 commit 回 VHD，支援安全測試流程 (優先級: 高)
- VHD 格式相容性: Virtual PC 與 Virtual Server 2005 R2 SP1 使用相同 VHD 格式，可互通 (優先級: 高)
- 安裝策略: 在僅使用 VPC 的機器上也可安裝 Virtual Server 只取用 VHDMount 工具 (優先級: 高)
- ISO vs VHD: VHDMount 類似「虛擬光碟」概念，但對象是硬碟映像（可寫入）而非唯讀 ISO (優先級: 中)
- 使用情境優勢: 快速修改/檢查 VHD 內容，省去開機 guest 的時間成本 (優先級: 高)
- 風險控管: 使用 commit 前務必確認變更正確，建議先備份或以「不提交」驗證 (優先級: 高)
- 硬體輔助虛擬化: Virtual Server 2005 R2 SP1 新增支援，整體虛擬化體驗更佳（背景知識） (優先級: 中)
- 與 VMware 對比: VMware 早已提供類似功能，VHDMount 補足微軟生態缺口 (優先級: 低)
- Host OS 權限需求: 需足夠系統權限才能成功掛載/卸載並寫入 VHD (優先級: 中)
- 工作流程建議: 建立「掛載→變更→測試→卸載→決策提交」的標準流程 (優先級: 高)
- 檔案系統相容: 確保 Host OS 能正確辨識與存取 VHD 內檔案系統 (優先級: 中)
- 自動化與腳本: 可將 VHDMount 納入批次流程，提升重複性工作的效率 (優先級: 中)
- 工具限制意識: 市面常見為虛擬光碟，缺少「虛擬燒錄器」等更進階的寫入模擬工具 (優先級: 低)
- 團隊協作規範: 定義誰能 commit、版本命名與備份策略，避免多人誤覆寫 (優先級: 中)