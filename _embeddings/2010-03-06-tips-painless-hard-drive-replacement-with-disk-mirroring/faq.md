# [Tips] 用 磁碟鏡像 無痛更換硬碟

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 在 Windows Server 上如何「幾乎不停機」地更換舊硬碟並升級容量？
只要利用作業系統內建的磁碟鏡像 (Mirror Set) 功能，先把新硬碟加入鏡像、等待 Resync 完成後中斷鏡像，再用 Extend Volume 把磁碟區擴充即可。整個過程中，除了關機裝入新硬碟那一刻，其餘時間所有服務 (SQL、IIS、Shared Folder 等) 都可維持正常運作。

## Q: 具體步驟是什麼？
1. 關機並裝入新硬碟。  
2. 在磁碟管理中把舊硬碟 (Disk 1) 與新硬碟 (Disk 2) 建立鏡像。  
3. 等待鏡像 Resync 完成。  
4. 中斷 (break) 鏡像，讓系統改用新硬碟上的磁碟區。  
5. 以 Extend Volume 功能將磁碟區容量擴充到新硬碟的完整大小。完成後即可收工。

## Q: 作者原本考慮過哪些替代方案？為何放棄？
1. 直接複製檔案：需長時間停機搬資料，還要重建分享與服務設定。  
2. 使用 True Image／Ghost 等 Disk Clone 工具：必須離線操作且容量大 (750 GB)；加上新硬碟採 Advanced Format，Clone 後還得再做效能校正，太麻煩。

## Q: 這種「鏡像 + Extend Volume」作法有哪些缺點？
1. 系統磁碟會被轉成 Dynamic Disk，其它作業系統或部份磁碟工具可能無法辨識。  
2. Mirror Set 僅限 Windows Server 版本；Windows 2000 Pro／XP／Vista／Win7 等桌面版不支援。  
3. Extend Volume 需 Windows Server 2008 以上才有；2003 只能做到 Span Volume，畫面上仍會看到兩個分割區。

## Q: 整個換碟流程中真正需要關機的時間點是什麼時候？
只有第一步「裝上新硬碟」必須關機；之後從建立鏡像到擴充容量皆可在開機狀態完成。

## Q: 使用此方法最大的優勢為何？
不需搬移資料、重建服務或修改任何設定；僅靠幾次滑鼠點擊即可在幾乎零中斷的情況下完成硬碟升級。