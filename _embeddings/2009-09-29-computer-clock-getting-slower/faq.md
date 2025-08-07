# 電腦時鐘越來越慢...

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼我的手機時鐘會越來越慢，短短兩週就慢了將近 20 分鐘？
手機接上 USB 做充電與同步時，會自動向家裡的 PC 對時；由於 PC 自身的時間已經變慢，手機也跟著被「同步」到錯誤的時間，於是誤差愈來愈大。

## Q: 家裡的 PC 不是會上網校時嗎？為什麼還會出現誤差？
家裡的 PC 被設定成向內部的 Server（Domain Controller）對時，而非直接向外部時間伺服器對時；當 Server 的時間出錯時，PC 也就跟著錯。

## Q: Server 的時間為何會持續變慢？
Server 架構是 Hyper-V Host + Guest 兩層：  
1. 主機 (Host OS) 加入了 AD，預設會向 Guest (Domain Controller) 做時間同步。  
2. Hyper-V 又會將 Guest 的時間同步到 Host。  
這種「Host 跟 Guest 互相對時」形成循環，造成少量誤差不斷累積，最終導致系統時鐘嚴重落後。

## Q: 最後是如何解決這個循環導致的時間飄移問題？
在 Hyper-V 裡取消 Guest (Domain Controller) 的「Time synchronization」整合服務，讓 DC 改為直接向外部 NTP 伺服器校時，停止 Host/Guest 之間的循環同步後，時間即恢復正常。