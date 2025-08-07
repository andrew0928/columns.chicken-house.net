# 電腦時鐘越來越慢...

# 問題／解決方案 (Problem/Solution)

## Problem: 家中所有裝置的時間愈來愈慢

**Problem**:  
在過去兩個星期內，家中 PC 與手機的系統時間每天都會慢上數分鐘，累計誤差已接近 20–30 分鐘。手機因為透過 USB 與家用 PC 進行同步 (充電＋ActiveSync) 而取得錯誤時間，導致所有裝置的時鐘都不準確。

**Root Cause**:  
1. 家中 PC 加入 Active Directory 網域後，會向網域中的 Domain Controller (DC) 同步時間。  
2. 該 DC 被安裝在 Hyper-V 虛擬機 (Guest OS) 內，而 Hyper-V 的「Time synchronization integration service」會讓 Guest 與 Host 互相對時。  
3. Host OS 也加入同一個網域，會再向 Guest DC 對時，形成「Host ↔ Guest」的跨層迴圈。迴圈中每一次同步都可能產生毫秒級誤差，長期累積後放大成分鐘級落差。  

**Solution**:  
1. 在 Hyper-V 管理員中，對承載 AD DC 的虛擬機取消勾選「Time synchronization」(Integration Services)。  
2. 於 Guest DC 內設定其向外部 NTP Server (例如 time.windows.com、pool.ntp.org) 單向取得權威時間，而非再從 Host 取時。  
   ```powershell
   w32tm /config /manualpeerlist:"time.windows.com,0x8" `
          /syncfromflags:manual /reliable:yes /update
   net stop w32time && net start w32time
   ```  
3. 確認其他網域成員 (包含 Host OS) 只向此權威 DC 對時，杜絕循環。  

此方案透過「切斷 Guest ↔ Host 之間的循環同步」並讓 DC 對外部 NTP 取時，消除了系統性時間漂移的根本原因，恢復了單向、權威的時間階層。

**Cases 1**:  
• 變更後 24 小時內觀察，PC 與手機每日漂移量從原本的 2–3 分鐘降至 < 1 秒。  
• 一週後再次檢查，累積誤差維持 < 3 秒；與網路 NTP Server 比對誤差在 50 ms 內。  
• 不再出現手機 / PC 每日手動校正的額外維運工作量，節省約 10 分鐘／日的人工排查與調整時間。