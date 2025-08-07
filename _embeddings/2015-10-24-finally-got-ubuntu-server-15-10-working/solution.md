# 終於搞定 Ubuntu Server 15.10 @@

# 問題／解決方案 (Problem/Solution)

## Problem: NAS 上 Docker 容量與效能有限，無法安心開更多容器

**Problem**:  
想在 Synology DS-412+ (Atom D2700 / 1 GB RAM) 上用 Docker 做 ASP.NET 5 的測試，但一旦多開幾個容器就明顯吃緊，擔心影響 NAS 原有的檔案服務。

**Root Cause**:  
NAS 本身僅雙核心 Atom + 1 GB 記憶體，屬於「夠用就好」的儲存設備，非為大量運算/多容器情境而設計；擴充性有限、升級成本又高。

**Solution**:  
1. 盤點自家舊硬體 → 發現一台準備報廢的 Acer Aspire 5742Z 筆電 (Pentium P6200 / 4 GB RAM / 320 GB HDD)。  
2. 將螢幕拆除、關閉背光，縮減耗電；利用筆電電池當「迷你 UPS」。  
3. 在該筆電上安裝 Ubuntu Server 15.10 + Docker Engine，作為「隨開即用」的低功耗 Docker Host。  

為何能解決根本原因：  
‒ 多 2 GB RAM 與雙核心 Pentium，可承載更多容器；  
‒ 筆電待機功耗遠低於桌機，比 NAS 略高但仍可 24x7；  
‒ 完全不動到原本 NAS，分散風險。

**Cases 1**:  
• 筆電安裝完成後，同時跑 Nginx Reverse Proxy、WordPress 舊站搬遷容器、實驗性 ASP.NET 5 容器，NAS 僅保留檔案服務。  
• Docker Host CPU 使用率約 30 % 以內、記憶體剩餘 1 GB 以上；NAS 執行負載恢復至 <10 %。  
• 災害演練：拔掉外部電源，筆電靠殘餘電量維持 6 分鐘；UPS 功能驗證成功，之後自動關機無資料遺失。

---

## Problem: 用錯 USB 製作工具，安裝程式只能 Net Install，且網卡驅動抓不到

**Problem**:  
製作 Ubuntu Server 開機隨身碟後啟動，安裝程式只剩「Net Install」流程，必須先連網才可繼續；但筆電有線/無線網卡都未被偵測，無法往下安裝。

**Root Cause**:  
選用的 USB boot 製作工具（非官方推薦版本）僅將 Minimal ISO 寫入，缺少完整離線安裝檔；加上安裝核心尚未含目標硬體網路驅動。

**Solution**:  
1. 改用官方文件推薦的「Rufus (Windows) / `dd` (Linux/Mac)」重新燒錄完整 ISO。  
2. 重新開機後可直接進入 text-based full installer，無須網路即可繼續安裝。  

關鍵思考：改變工具 → 改變 ISO 內容 → 移除對網路驅動的前置依賴。

**Cases 1**:  
• 同一台筆電改用 Rufus 重灌，安裝流程 20 分鐘內完成；無需任何網路設定。  

---

## Problem: 多種發行版 (12.04 LTS / 14.04 LTS / CentOS) 安裝到一半報「CDROM 內容不符」

**Problem**:  
嘗試數個映像檔 (Ubuntu 12.04 LTS, 14.04 LTS, CentOS 7) 均在中段跳錯：「CDROM couldn't be read / contents not valid」，雖已反覆下載並驗證 MD5/sha256。

**Root Cause**:  
1. 舊無線網卡 (Atheros) 在安裝過程中載入驅動時觸發 kernel message，導致 installer 誤判 ISO media read 錯誤；  
2. Ubuntu 舊版核心對該筆電 SATA 控制器有 bug，15.10 之後才修正。

**Solution**:  
1. 物理拔除 Wi-Fi 模組，避免衝突驅動被載入。  
2. 直接選用較新的 Ubuntu Server 15.10 (kernel 4.2+)。  
3. 安裝流程一次通過。  

關鍵思考：如果軟體層面無解 → 嘗試移除疑似問題硬體 + 更新核心版本。

**Cases 1**:  
• 拔除 WLAN 後使用 15.10，安裝程序全程未再出現 CDROM error。  
• 之後透過 USB Wi-Fi 或有線 LAN 接入，系統正常運作 2 週無任何 I/O 錯誤。  

---

## Problem: 裝好 Linux 後，要設定 SSH、固定 IP、Samba 共享，花費時間

**Problem**:  
作者多年未大量接觸 Linux，對 NetworkManager / systemd 指令不熟；單純想要「遠端 SSH + 固定 IP + Windows 檔案分享」卻查文件花了不少時間。

**Root Cause**:  
知識斷層 + Ubuntu 15.10 改用 `systemd`, `netplan` 尚未引入，與舊版 `/etc/network/interfaces` 寫法混淆；再加 Samba 關鍵設定項目繁多。

**Solution**:  
以下為最終整理的最小可行腳本 / 流程：

```bash
# 1. 安裝 SSH Server
sudo apt-get update
sudo apt-get install -y openssh-server

# 2. 固定 IP（/etc/network/interfaces）
cat <<'EOF' | sudo tee /etc/network/interfaces.d/eth0.cfg
auto eth0
iface eth0 inet static
  address 192.168.1.50
  netmask 255.255.255.0
  gateway 192.168.1.254
  dns-nameservers 8.8.8.8 8.8.4.4
EOF
sudo systemctl restart networking

# 3. 安裝並設定 Samba
sudo apt-get install -y samba
sudo smbpasswd -a $USER     # 建立個人帳號密碼
sudo tee -a /etc/samba/smb.conf <<'EOF'

[docker-share]
   path = /var/docker
   valid users = @users
   read only = no
EOF
sudo systemctl restart smbd nmbd
```

為何有效：  
‒ 把高頻指令整理成腳本，以後重灌/複製直接貼上；  
‒ 明確切分「網路固定 IP」與「檔案分享」兩件事，降低學習曲線。

**Cases 1**:  
• 重灌同一台筆電只需 10 分鐘完成安裝，複製上述腳本後 2 分鐘內即可 SSH 進入；  
• Windows 端以 `\\dockerhost\docker-share` 連線，平均傳輸 40 MB/s，符合老式 HDD 預期值。  

---

以上四組問題與對應解決方案，便組成了「把快報廢的筆電變成 24x7 Docker Server」的完整心路歷程與可重複步驟。