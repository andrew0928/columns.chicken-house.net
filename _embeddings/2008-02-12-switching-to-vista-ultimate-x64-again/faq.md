# 再度換裝 Vista … Vista Ultimate (x64)

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 作者為什麼決定再次把作業系統換成 Windows Vista Ultimate x64？
1. 新添購 750 GB 硬碟，可在不動舊系統的情況下安裝新 OS。  
2. 想擴充記憶體而 32 bit XP 無法充分利用 4 GB 以上 RAM；x64 才能完全發揮。  
3. 需要同時保留 MCE 功能與 x64，唯一選項就是 Vista x64。  
4. Canon Raw Codec 雖官方宣稱不支援 x64，但已找到臨時可行解法。  
5. 想研究 IIS 7，而用 Vista 比等 Windows Server 2008 快。  
6. 家人已使用 Vista 一段時間且運作正常。  
7. Vista 內建 DVD codec、基本影像剪輯程式等，滿足作者需求。  
8. 雖無「革命性」新功能，但各項小改進累積起來不少。  
9. Vista 內建 Tablet PC 支援，可搭配數位板使用。  
10. SuperFetch 讓常用大型軟體啟動速度感覺更快。  
11. VS 2008 已解決過去 VS 2005 在 Vista（尤其 x64）上的除錯問題。  
12. Vista SP1 將推出，時機成熟。  
13. 已買正版 Vista，再不用實在可惜。

## Q: 官方宣稱 Canon RAW Codec 不支援 Vista x64，作者是怎麼解決的？
將需要用到 Codec 的程式整個設定成 32 bit（如自行開發的轉檔工具改用 x86 target，或直接啟動 32 bit 版 Windows Live Gallery）。  
只要整個 Process 都是 32 bit，就能順利載入 32 bit Canon RAW Codec 以顯示、轉檔與讀取 .CR2 Metadata。

## Q: Vista 內建的「Complete PC 備份」有什麼用？與 Ghost 有何類似？
Complete PC 備份可以把整顆硬碟製成映像檔（副檔名 .vhd）。  
日後可用 Vista 安裝 DVD 還原，或用 Virtual Server 2005 R2 SP1 的 VHDMOUNT 掛載，功能與 Ghost 類似但直接支援 Microsoft 的 VHD 格式。

## Q: 在 64 bit Windows 中，為何有時必須整個程式都保持 32 bit？
因為同一個處理程序(process) 內不能混用 32 bit 與 64 bit 代碼；只要有任何 DLL/Driver 為 32 bit，就必須把整個 Process 設為 32 bit 才能載入並正常運作。

## Q: 32 bit 應用程式跑在 64 bit OS 下有什麼好處？
1. 記憶體管理效率更佳，相關操作速度較快。  
2. 雖仍受 4 GB 位址空間限制，但不用再切 2 GB 給 OS，本身即可使用完整 4 GB，對大型 32 bit 程式是實質助益。

## Q: Windows Live Photo Gallery 在 x64 系統下如何確保使用正確的版本？
重開機後第一次就啟動 32 bit 版的 Photo Gallery；因為程式會常駐並被後續呼叫，首次啟動的位元數決定之後載入的版本。