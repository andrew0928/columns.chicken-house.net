# Using VHDMount with Virtual PC

## 摘要提示
- Virtual Server 2005 R2 SP1: 微軟新版終於支援硬體輔助虛擬化與 VHDMount 工具。
- VHDMount: 可將 *.vhd 檔掛載為實體硬碟，類似常見的 ISO 虛擬光碟機。
- Undo Disk: 掛載時自動啟用 Undo Disk，可選擇在卸載時保留或放棄變更。
- VMware 比較: VMware 早已有類似功能，微軟此番跟進縮短差距。
- VPC/VS 互通: Virtual PC 與 Virtual Server 使用相同 VHD 格式，掛載後不影響相容性。
- 安裝建議: 在 XP 上只勾選安裝 VHDMount 即可，不必整套安裝 Virtual Server。
- 效率提升: 修改 VHD 不必開機進入來賓作業系統，可直接在主機端處理。
- 工具缺憾: 雖然虛擬化蓬勃，但仍缺乏「虛擬燒錄器」支援。
- 應用場景: 系統維護、檔案撈取、批次更新都能因 VHDMount 受益。
- 未來展望: 期待更多虛擬硬體類型（如燒錄器）被納入虛擬化生態。

## 全文重點
作者針對剛釋出的 Microsoft Virtual Server 2005 R2 SP1 發表心得，特別著墨於新加入的 VHDMount 工具。此工具能把 Virtual PC/Server 的硬碟映像檔 *.vhd 像 ISO 檔那樣直接掛載到主機作業系統，於檔案總管中視同一顆實體硬碟。掛載過程會自動啟用 Undo Disk，讓使用者在卸載時決定是否將修改寫回原始 VHD，因而大幅降低測試或維護的風險。作者指出 VMware 早就提供同級功能，如今微軟終於補足並加入更貼心的變更回溯機制，是一大進步。

由於 Virtual PC 與 Virtual Server 採用同一份 VHD 格式，因此即便主要只用 Virtual PC 的人，也能在 Windows XP 上安裝 Virtual Server 並僅勾選 VHDMount 就享受掛載便利，無須完整部署伺服器環境。藉此可免去進入客體作業系統的繁瑣流程，例如只為複製一份檔案、替換驅動程式或執行批次更新。文章最後抱怨目前虛擬化世界雖然 ISO、VHD 等都能模擬，卻始終沒有「虛擬燒錄器」可供模擬燒錄流程，期待未來有廠商填補這塊空缺。

## 段落重點
### Virtual Server 2005 R2 SP1 上市與新功能
作者首先提到微軟於兩週前推出 Virtual Server 2005 R2 SP1，除了支援硬體輔助虛擬化（Intel VT、AMD-V）外，最重要的新工具就是 VHDMount。該工具被視為與 ISO 虛擬光碟同等概念的「虛擬硬碟掛載器」，正式補足微軟在磁碟映像檔管理面的缺口。

### VHDMount 的操作模式與優勢
VHDMount 能把 .vhd 檔掛在主機 OS，並自動啟動 Undo Disk。使用者在卸載時可選擇 commit 或 discard 變更，既保護原始映像又方便測試。相比 VMware 早期提供的類似工具，微軟版本多了內建回溯機制，讓維護與回收更直觀安全。

### 在 Virtual PC 環境導入 VHDMount
雖然 VHDMount 隨 Virtual Server 發布，但因 VPC 與 VS 共用 VHD 格式，使用者可於 Windows XP 安裝 VS 2005 R2 SP1 時只勾選 VHDMount。如此可在不安裝整套伺服器功能的前提下，直接於 VPC 工作流程享有掛載、修改與提交 VHD 的簡易途徑，大幅減省以往須開機至客體 OS 進行檔案操作的時間。

### 虛擬化現況與「虛擬燒錄器」遺憾
文章最後發出小小抱怨：光碟、硬碟映像都已有成熟虛擬化支援，但市面上仍缺乏可完整模擬「燒錄器」行為的虛擬硬體。無論是虛擬光碟軟體還是虛擬機器，目前都無法讓使用者像真實燒錄器那樣進行燒錄測試，顯示虛擬化仍有待填補的領域與機會。