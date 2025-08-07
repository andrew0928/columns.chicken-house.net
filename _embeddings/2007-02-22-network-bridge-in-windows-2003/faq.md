# Network Bridge in Windows 2003...

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼作者即使在主機板上已有內建網卡，仍堅持改用 Intel 82559 系列網路卡？
作者相信大廠在驅動程式除錯上比較投入資源；實際使用 Intel 82559 後，傳送大型檔案時不再出現網路中斷等問題，整體穩定性遠勝過市面上常見的 d-xxxx、rxxxxt 等晶片。

## Q: 是什麼原因讓作者決定把家中的 100 Mbps 網路升級到 Gigabit Ethernet？
在 100 Mbps 網路下，從伺服器拉 ISO 到桌機再燒成 DVD 需要等待多次 10 分鐘以上的複製、燒錄與驗證流程；頻繁的時間浪費促使作者升級至 1000 Mbps 以縮短檔案傳輸時間。

## Q: 作者如何在不大幅修改 DHCP、靜態路由等設定的前提下，讓 1 Gbps 與 100 Mbps 網卡同時工作？
他利用 Windows Server 2003 內建的「Software Network Bridge」功能，將 100 Mbps 與 1 Gbps 兩張網卡橋接成單一邏輯介面，既保留原有網段設定，又能直接享受 Gigabit 傳輸速度。

## Q: 橋接完成後實際的傳輸效能有多大提升？
單純複製檔案時，Gigabit 連線大約可達 30% 使用率（約 300 Mbps），已較原先 100 Mbps 網路的 90 Mbps 提升三倍以上；若同時從不同硬碟讀取檔案，網路使用率可進一步衝到 60%。

## Q: 作者對 Marvell Gigabit 網卡有何顧慮？
過去公司伺服器長時間高流量運作時，內建的 Marvell 晶片會無預警斷線，必須手動停用再啟用網路介面才能恢復；雖然家用環境流量較小，作者仍對 Marvell 的穩定性抱持觀望態度。