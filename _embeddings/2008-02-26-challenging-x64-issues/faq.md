# 困難重重的 x64

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 升級到 6 GB 記憶體並在 BIOS 開啟 Memory Remap 後，作者首先遇到的問題是什麼？
作者的電視卡在 Vista x64 下無法正常收視，Media Center 一直顯示「訊號微弱」，關閉 Memory Remap 後才恢復正常。

## Q: 為什麼開啟 Memory Remap 會讓電視卡失效？
電視卡的驅動程式與 Vista x64 在 Memory Remap 模式下存在相容性問題；裝置管理員雖顯示正常，但實際上驅動沒有正確處理記憶體映射，導致無訊號。

## Q: 作者改回 Vista x86 後，開或關 Memory Remap 皆可正常使用電視卡，這說明了什麼？
這顯示問題多半出在 64 位驅動程式，32 位 (x86) 驅動在同樣硬體設定下並無異常。

## Q: 在現階段使用 Vista x64，作者認為有哪些主要缺點？
1. 很多軟體與 DLL 必須同時安裝 x64 與 x86 版本，佔用空間。  
2. 64 位程式的指標長度較大，記憶體用量增加。  
3. 需要使用 COM 元件的程式多半透過 WOW 層執行，效能略降。

## Q: 為何作者在 Vista x86 下開啟 BIOS Remap 反而只剩 2 GB 可用記憶體？
ASUS P5B-E Plus 主機板在 Vista x86 + BIOS Remap 組合下存在相容性缺陷；線上亦有許多使用者回報相同問題，目前無解只能關閉 Remap 或接受 2 GB 限制。

## Q: 作者如何利用 Gavotte Ramdisk 取回作業系統認不到的記憶體？
只要讓 Vista 啟用 PAE，Gavotte Ramdisk 會自動把超出 32 位位址空間且無法被 OS 使用的 RAM 建立為一個 RamDisk，讓使用者仍可利用這段記憶體。

## Q: Gavotte Ramdisk 有哪些優點？
它免費、容量不設上限、穩定度佳，並具備「回收未被 OS 取用之記憶體」的特殊功能，對安裝大量記憶體而受 32 位系統限制者特別實用。

## Q: 最後作者採取的暫時解決策略是什麼？
作者先退回 Vista x86、拔掉 2 GB 記憶體，只保留 4 GB，其中約 2 GB 交由 Gavotte Ramdisk 做為 TEMP 用途，待未來驅動與軟體環境更成熟後再重試 x64。