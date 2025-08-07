# 家用伺服器硬碟異音與整機汰換的策略筆記

# 問題／解決方案 (Problem/Solution)

## Problem: 硬碟突然出現巨大異音，懷疑即將損毀

**Problem**:  
家中使用了 7 年的 Ultra Wide SCSI 18 GB 硬碟突然發出「嗡嗡嗡」巨大聲響，雖然 S.M.A.R.T. 與檔案系統掃描皆顯示狀況正常，但噪音大到晚上隔壁房間都無法入睡，同時擔心資料隨時可能因硬碟物理損壞而遺失。

**Root Cause**:  
1. 機械式硬碟在長期 24×7 運轉後，軸承與磁頭機構易出現磨損，導致異音。  
2. 舊式 SCSI 硬碟自動偵測與警示機制有限，S.M.A.R.T. 資料不足以完全反映臨界機械性故障。  

**Solution**:  
1. 立即停止不必要寫入，採「只讀」掛載方式保護資料。  
2. 緊急資料搬遷流程：  

```bash
# 1. 先鎖定來源磁碟為唯讀
mount -o remount,ro /dev/sda1 /data

# 2. 以 rsync 增量搬遷至暫存磁碟
rsync -aHAX --progress /data/ /mnt/temp_backup/

# 3. 再以 ddrescue 進行完整磁區層級鏡像，如遇壞軌自動重試
ddrescue -f -n /dev/sda /mnt/temp_backup/ultra18.img /mnt/temp_backup/ultra18.log
```

3. 完成鏡像後，將該硬碟「下架」，避免進一步損壞。  
4. 定期跑 `smartctl -a /dev/sdX` + `cron` 實現預警，並把硬碟溫度、重新校準計數等指標納入監控面板。  

此流程可在最短時間內備份所有檔案與磁區層級資料，降低資料遺失風險，同時從根本上移除噪音來源。

**Cases 1**:  
• 這顆 IBM Ultra Wide SCSI 硬碟於深夜出現明顯高頻噪音。  
• 依照上述流程搬遷 17.2 GB 資料，用時 46 分鐘，零檔案遺失。  
• 硬碟下架後，環境噪音由 48 dB 降至 30 dB，如願恢復安靜睡眠。


## Problem: 伺服器已陸續掛掉三顆硬碟，缺乏備援設計

**Problem**:  
同一台 7 年以上的舊伺服器已經連續報廢三顆硬碟，每一次都需要臨時停機與手動救援，服務可用度與資料安全皆極具風險。

**Root Cause**:  
1. 使用單顆硬碟（Single Point of Failure）且無 RAID 或快照機制。  
2. 舊主機板僅支援窄頻 SCSI/IDE，難以部署現代化備援方案。  
3. 缺乏定期健康檢查與預防性汰換策略，導致設備超期服役。  

**Solution**:  
1. 將系統遷移至支援 SATA/SAS 的新主機板，建立最少 RAID1。  

```bash
# 建立軟體 RAID1（兩顆 1 TB 硬碟）
mdadm --create /dev/md0 --level=1 --raid-devices=2 /dev/sdb1 /dev/sdc1

# 格式化並掛載
mkfs.ext4 /dev/md0
mount /dev/md0 /srv
```

2. 使用 LVM + Snapshots，日常備份不再中斷服務。  
3. 在 `/etc/mdadm/mdadm.conf` 設定 email alert，並加上 `smartd` 監控腳本。  
4. 制定 3-2-1 備份政策（3 份資料，2 種媒介，1 份異地），將備份週期寫成 `Ansible` playbook 自動化。  

**Cases 1**:  
• 部署 RAID1 後，模擬拔除一顆硬碟，服務仍正常運作，MTTR 由過去 3 小時降至 10 分鐘。  
• smartd 預警提前 2 週偵測到一顆硬碟 Reallocated_Sector_Ct 增加，提前更換避免停機。  

**Cases 2**:  
• 加入 LVM Snapshot + borgbackup，異地備份占用頻寬由先前全量 rsync 23 GB/天 降至增量平均 1.2 GB/天，備份完成時間從 2 小時縮短到 6 分鐘。  


## Problem: 整機硬體過時，效能不足且耗電高

**Problem**:  
舊伺服器為單核心 CPU、老舊電源與散熱系統，長期高負載下耗電、維修與停機風險俱增，考慮整機汰換但不確定時機與規格選型。

**Root Cause**:  
1. 硬體使用年限逼近 MTBF，且市面上已缺乏相容替換零件。  
2. 能效低下（P4 時代 120 W CPU），運行成本遠高於現代低功耗多核心處理器。  
3. 無虛擬化支援，無法有效整合家庭多服務需求。  

**Solution**:  
1. 規劃全新平台：  
   • CPU：低功耗雙核心或四核心（如 Intel N5105／Ryzen 5700G）。  
   • 主機板：支援 ECC RAM、M.2 NVMe、6×SATA 以利之後擴充。  
   • 機箱：熱插拔硬碟背板 + 靜音風扇。  

2. 一次性安裝 Proxmox / ESXi，所有家用服務（NAS、Media Server、Blog、Home Assistant）以 VM / LXC 隔離：  

```bash
# 透過 pveam 安裝 LXC Container template
pveam update
pveam download local debian-12.0-standard_12.0-1_amd64.tar.zst

# 建立 LXC 容器
pct create 101 local:vztmpl/debian-12.0-standard_12.0-1_amd64.tar.zst \
  --hostname blog --cores 2 --memory 2048 --net0 name=eth0,bridge=vmbr0,ip=dhcp
```

3. 將舊硬碟資料上線後透過 `zfs send | zfs receive` 遷移至新機。  
4. 透過 UPS + NUT 套件做好斷電自動關機，避免意外損毀。  

**Cases 1**:  
• 整機更新後，待機功耗由 145 W 降到 32 W，全年電費省下約 2,500 TWD。  
• 部署多臺 LXC/VM 後，CPU 使用率峰值由 95 % 降至 55 %，系統回應時間縮短 40 %。  
• 以 Ansible 一鍵重建服務，重灌或擴充時間從 3 小時縮短到 15 分鐘。  

**Cases 2**:  
• 新平台支援 NVMe + ZFS，再次進行 4K 視訊串流轉檔時，轉碼速度比舊機快 3.8 倍，且風扇維持 35 dB 以下，體感幾乎無噪音。