# Using VHDMount with Virtual PC

# 問答集 (FAQ, frequently asked questions and answers)

## Q: Microsoft Virtual Server 2005 R2 SP1 新增了哪些重要功能？
它加入了 Hardware Assisted Virtualization（硬體輔助虛擬化）的支援，並且隨附可以在主機端掛載 .vhd 磁碟映像檔的工具 VHDMount。

## Q: 什麼是 VHDMount？它和常見的虛擬光碟機軟體有何相似之處？
VHDMount 是一個讓使用者把 Virtual PC／Virtual Server 用的 .vhd 虛擬硬碟檔直接掛載到主機作業系統的工具；就像把 .iso 檔掛到虛擬光碟機一樣，只是它掛的是硬碟映像檔而非光碟映像檔。

## Q: 使用 VHDMount 掛載 .vhd 後，在卸載時可以做哪些選擇？
VHDMount 會啟用 Undo Disk 機制；當你卸載 (dismount) VHD 時，可以選擇是否將變更「提交 (commit)」到原始 .vhd，或捨棄這些變更。

## Q: Virtual PC 的使用者要如何利用 VHDMount 帶來的便利？
因為 Virtual PC 與 Virtual Server 2005 R2 SP1 所使用的 .vhd 格式完全相容，使用者可以在 Windows XP 等主機上只安裝 Virtual Server 2005 R2 SP1 中的 VHDMount 元件，不必安裝整個 Virtual Server，就能在 Virtual PC 環境中直接掛載 .vhd 進行檔案操作。

## Q: 作者對目前虛擬化生態系統還有什麼不滿或期望？
作者抱怨雖然各種裝置都虛擬化了，卻一直沒有「虛擬燒錄器」──既沒有能模擬燒錄機行為的虛擬光碟軟體，虛擬機器也尚未支援模擬燒錄器。