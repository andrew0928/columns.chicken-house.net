以下為基於原文內容提取與延展的 16 個可教學、可實作、可評估的實戰案例。每個案例均包含問題、根因、解法、步驟、程式碼與學習要點等，供課程、專案練習與評量使用。

## Case #1: NAS 資源瓶頸下的容器外移與分工

### Problem Statement（問題陳述）
業務場景：家用 NAS（DS-412+，Atom D2700、1GB RAM）上已部署多個 Docker 容器（含部落格與反向代理），但硬體資源有限，隨容器數量增加開始擔心穩定性與效能。需要在不中斷現有服務的前提下，建立一個可彈性實驗的新 Docker 環境，將非關鍵工作負載外移，確保 NAS 上正式服務穩定運作。
技術挑戰：如何在不影響 NAS 現行服務下，建立第二個 Docker 主機並實施工作負載分流與資源管控。
影響範圍：若資源飽和，正式網站可能延遲變高、重啟或 OOM；影響可用性與用戶體驗。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. NAS CPU 與記憶體規格過低，易被多容器爭用
2. 正式與實驗性容器混跑，資源互相干擾
3. 缺乏容器資源限制（CPU/記憶體）策略

深層原因：
- 架構層面：單一主機承載所有服務，缺乏分層與冗餘
- 技術層面：未使用資源隔離與多主機管理
- 流程層面：部署流程未明確區分「正式」與「實驗」工作負載

### Solution Design（解決方案設計）
解決策略：建立一台獨立的 Docker 主機（舊筆電），將實驗性與開發用途容器外移；同時在兩端設置資源限制與監控，採用反向代理統一對外入口，確保正式服務不受影響，逐步分流與觀察。

實施步驟：
1. 規劃分流策略
- 實作細節：列出正式/實驗容器清單，定義外移順序
- 所需資源：工單與資源盤點表
- 預估時間：0.5 天

2. 部署新 Docker 主機
- 實作細節：於 Ubuntu Server 安裝 Docker，開啟遠端管理
- 所需資源：舊筆電、Ubuntu 安裝媒體
- 預估時間：0.5 天

3. 外移容器並設資源限制
- 實作細節：docker-compose 設定 mem/cpu 限制；使用 volumes 搬移資料
- 所需資源：docker-compose、rsync
- 預估時間：1 天

4. 反向代理銜接
- 實作細節：Nginx/Traefik 透過 DNS 或路由配置到不同主機
- 所需資源：Nginx/Traefik
- 預估時間：0.5 天

關鍵程式碼/設定：
```yaml
# docker-compose.yml（在新主機上部署實驗性容器）
version: "3.8"
services:
  app-dev:
    image: your/app:dev
    deploy: # 若單機可忽略 deploy，改用下方限制
    # 單機限制：
    mem_limit: 512m
    cpus: "1.0"
    restart: unless-stopped
    volumes:
      - appdata:/data
volumes:
  appdata:
```

實際案例：文中作者將正式部落格與反向代理放在 NAS，另起一台可「隨便玩」的 Docker 主機承接實驗負載。
實作環境：Synology DS-412+（NAS）、Ubuntu Server 15.10（新主機）、Docker
實測數據：
改善前：同主機混跑，資源競爭風險高
改善後：正式與實驗分離，風險降低
改善幅度：成功率從易干擾 -> 穩定完成外移（質性）

Learning Points（學習要點）
核心知識點：
- 單主機多容器風險與分層部署策略
- Docker 資源限制（mem_limit、cpus）
- 反向代理在多主機下的路由與聚合

技能要求：
必備技能：Docker 基本運維、Linux 檔案系統
進階技能：反向代理與多主機管理

延伸思考：
- 是否導入 Swarm/Kubernetes 進一步調度？
- 資料一致性與備份如何設計？
- 是否需要觀察與告警（Prometheus/Grafana）？

Practice Exercise（練習題）
基礎練習：將一個 Nginx 容器設定 mem_limit 與 cpus
進階練習：把一個開發服務從 NAS 搬到新主機，透過反向代理連通
專案練習：規劃與完成正式/實驗容器分流方案，含回滾策略

Assessment Criteria（評估標準）
功能完整性（40%）：容器可用、配置正確、路由通
程式碼品質（30%）：compose 結構清晰、版本管理
效能優化（20%）：資源限制生效、負載平衡合理
創新性（10%）：自動化部署或監控整合


## Case #2: 以舊筆電打造 24x7 低功耗 Docker 主機

### Problem Statement（問題陳述）
業務場景：需要一台長時間運作、低功耗且少維護的 Docker 主機，PC/VM 雖易達成但耗電與管理成本較高。恰有一台報廢前的舊筆電（Acer Aspire 5742Z，螢幕破裂），可否改造為無頭（headless）伺服器提供持續服務。
技術挑戰：無螢幕運作、硬體老舊、需穩定開機與遠端管理；並利用電池作為臨時 UPS。
影響範圍：若不穩定將影響容器服務可用性；若無遠端管理將提高維護成本。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 傳統桌機/VM 耗電與噪音高，不適合 24x7
2. 舊筆電螢幕已裂，需無頭運作
3. 無電力保護易在跳電時不當關機

深層原因：
- 架構層面：缺乏低成本高可用的家庭實驗環境
- 技術層面：未建立無頭與遠端維運能力
- 流程層面：未定義停電/復電自動化流程

### Solution Design（解決方案設計）
解決策略：以 Ubuntu Server 部署筆電為無頭主機，開機即進入 multi-user 目標、啟用 SSH、禁用休眠與合蓋睡眠，設定自動開機，並配置電池電量低時自動安全關機。

實施步驟：
1. BIOS 與電源設定
- 實作細節：設定 AC 復電自動開機、關閉安全啟動（若有）
- 所需資源：BIOS 介面
- 預估時間：0.5 小時

2. 無頭化與遠端管理
- 實作細節：設定 multi-user target、開啟 SSH、禁用睡眠
- 所需資源：systemd、openssh-server
- 預估時間：1 小時

3. 電池 UPS 化
- 實作細節：安裝 acpid、低電量觸發安全關機
- 所需資源：acpid/upower
- 預估時間：1 小時

關鍵程式碼/設定：
```bash
# 無頭開機（預設即 multi-user target，若有 GUI 可強制）
sudo systemctl set-default multi-user.target

# 安裝 SSH
sudo apt-get update && sudo apt-get install -y openssh-server
sudo systemctl enable --now ssh

# 禁用睡眠/合蓋
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
sudo bash -c 'printf "[Login]\nHandleLidSwitch=ignore\n" > /etc/systemd/logind.conf'
sudo systemctl restart systemd-logind

# 低電量自動關機（acpid 事件）
sudo apt-get install -y acpid
# /etc/acpi/events/battery-low
event=battery.* # 依裝置調整
action=/etc/acpi/battery-low.sh

# /etc/acpi/battery-low.sh
#!/bin/bash
PCT=$(upower -i $(upower -e | grep BAT) | awk '/percentage/ {gsub("%","",$2); print int($2)}')
if [ "$PCT" -le 7 ]; then /sbin/shutdown -h now "Battery low"; fi
```

實際案例：文中以舊筆電取代耗電 PC/VM，並利用電池當作內建 UPS。
實作環境：Acer Aspire 5742Z、Ubuntu Server 15.10
實測數據：
改善前：無低功耗常開主機；停電風險高
改善後：24x7 運作、低電量自動關機
改善幅度：可用性提升（質性）

Learning Points（學習要點）
核心知識點：
- 無頭伺服器設計與 systemd 目標管理
- SSH 遠端管理與安全
- acpid 事件與電池監控

技能要求：
必備技能：Linux 服務管理、SSH
進階技能：電源事件腳本、自動化維運

延伸思考：
- 可否加入 NUT/外接 UPS 做雙保護？
- 開機後自動部署容器流程？
- 合蓋散熱與風扇控制注意事項？

Practice Exercise（練習題）
基礎練習：安裝 openssh-server 並以金鑰登入
進階練習：撰寫 acpid 腳本實作低電量關機
專案練習：打造無頭筆電主機，部署 2-3 個容器

Assessment Criteria（評估標準）
功能完整性（40%）：無頭可用、SSH 安全、低電量關機生效
程式碼品質（30%）：腳本健壯、註解完整
效能優化（20%）：開機自動化與資源使用穩定
創新性（10%）：電源/溫度監控延伸整合


## Case #3: 製作可離線安裝的 Ubuntu 開機 USB（避免 Netinstall 卡網路）

### Problem Statement（問題陳述）
業務場景：在舊筆電上安裝 Ubuntu Server，初期使用的 USB 製作工具生成的媒體僅支援 Netinstall，導致安裝程序強制要求設定網路；但安裝程式抓不到 NIC，無法繼續，安裝受阻。
技術挑戰：在無可用網卡驅動的情況下，完成離線安裝。
影響範圍：安裝流程中斷，無法建立目標主機。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 使用 netboot/mini 安裝映像，必須連網
2. NIC 驅動未被安裝程式辨識
3. USB 工具將 ISO 轉換為 netinstall 模式

深層原因：
- 架構層面：安裝流程過度依賴網路
- 技術層面：工具選用錯誤（非 dd 模式）
- 流程層面：缺乏媒體驗證與安裝前檢核

### Solution Design（解決方案設計）
解決策略：改用完整安裝映像（非 netboot），以 dd 模式或等效方式燒錄 USB，確保所有基本套件可離線安裝，待系統上線後再安裝驅動與更新。

實施步驟：
1. 下載完整 ISO 並驗證
- 實作細節：比對 SHA256/MD5 校驗值
- 所需資源：官方 ISO、校驗碼
- 預估時間：0.5 小時

2. dd 模式製作 USB
- 實作細節：使用 Rufus（選 DD 模式）或 balenaEtcher
- 所需資源：Rufus/Etcher
- 預估時間：0.5 小時

3. 離線安裝
- 實作細節：略過網路設定步驟，完成最小系統
- 所需資源：鍵盤/螢幕
- 預估時間：0.5-1 小時

關鍵程式碼/設定：
```bash
# Linux/macOS 以 dd 製作
sudo dd if=ubuntu-15.10-server-amd64.iso of=/dev/sdX bs=4M status=progress && sync

# Windows Rufus 建議：
# - 選擇 ISO 檔
# - 映像選項：'DD 模式'（非 ISO 模式/非持續化）
# - 分割方式依 BIOS/UEFI 選擇
```

實際案例：文中更換 USB 開機工具後，不再被強制網路設定，安裝得以進行。
實作環境：Acer Aspire 5742Z、Ubuntu Server 15.10
實測數據：
改善前：卡在網路設定，進度 0%
改善後：完成離線安裝，進度 100%
改善幅度：成功率 0% -> 100%

Learning Points（學習要點）
核心知識點：
- Netinstall vs 完整 ISO 差異
- dd 模式燒錄避免工具改檔
- 安裝流程離線化策略

技能要求：
必備技能：ISO 校驗、USB 製作
進階技能：安裝參數與開機引導診斷

延伸思考：
- 是否需要 Slipstream 驅動到 ISO？
- 建置內網鏡像站提升之後更新效率？
- 一次製作多機可用的通用安裝碟？

Practice Exercise（練習題）
基礎練習：下載 ISO 並完成校驗
進階練習：以 dd 模式製作可開機 USB 並試開機
專案練習：文件化一份離線安裝 SOP

Assessment Criteria（評估標準）
功能完整性（40%）：USB 可開機且完成安裝
程式碼品質（30%）：過程命令與紀錄清晰
效能優化（20%）：安裝時間可控、步驟最簡
創新性（10%）：工具比較與風險評估


## Case #4: 安裝程式偵測不到網卡（NIC Driver 問題）

### Problem Statement（問題陳述）
業務場景：使用安裝程序時，網路硬體無法被自動偵測，導致無法設定網路；即使可跳過，後續更新與套件安裝仍受限。需確認驅動支援與替代方案。
技術挑戰：在安裝階段 NIC 未辨識，如何繞過並在安裝後補齊驅動。
影響範圍：影響安裝與後續更新，導致系統不可用。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 內建 NIC 使用老舊或冷門晶片
2. 安裝映像不含對應驅動或韌體
3. 可能受無線網卡衝突影響（見 Case #7）

深層原因：
- 架構層面：離線安裝依賴驅動打包完整度
- 技術層面：驅動載入/黑名單機制不熟悉
- 流程層面：未準備替代連線方式（USB NIC）

### Solution Design（解決方案設計）
解決策略：安裝時改用較新版本（15.10）或完整映像，跳過網路設定；開機後用 USB 網卡或離線套件安裝驅動，並更新核心與韌體。

實施步驟：
1. 跳過網路設定完成安裝
- 實作細節：先完成基礎系統
- 所需資源：完整 ISO
- 預估時間：0.5 小時

2. 臨時連網
- 實作細節：接 USB 乙太網卡或手機 USB 網路分享
- 所需資源：USB NIC/手機
- 預估時間：0.5 小時

3. 安裝驅動與韌體
- 實作細節：安裝 linux-firmware、更新核心
- 所需資源：apt
- 預估時間：0.5 小時

關鍵程式碼/設定：
```bash
# 確認裝置
lspci -nn | egrep -i 'ethernet|network'
dmesg | grep -i firmware

# 安裝韌體與更新核心
sudo apt-get update
sudo apt-get install -y linux-firmware
sudo apt-get dist-upgrade -y
sudo reboot

# 嘗試載入模組
sudo modprobe e1000e # 依實際晶片替換
```

實際案例：文中指出 NIC 未被偵測導致 netinstall 卡關，最終改用不同 USB 工具與版本完成。
實作環境：Acer Aspire 5742Z、Ubuntu Server 15.10
實測數據：
改善前：安裝卡網路設定
改善後：跳過網路、開機後補齊
改善幅度：安裝完成率顯著提升（質性）

Learning Points（學習要點）
核心知識點：
- NIC 驅動與韌體管理
- 離線到上線的連網銜接策略
- dmesg/lspci 診斷流程

技能要求：
必備技能：Linux 基本診斷與套件安裝
進階技能：核心模組管理與黑名單

延伸思考：
- 是否需要自己編譯驅動？
- 長期保養：鎖版本或定期更新？
- 替代 NIC（USB）做災備？

Practice Exercise（練習題）
基礎練習：使用 lspci 與 dmesg 找出 NIC 型號
進階練習：安裝 linux-firmware 並驗證網路恢復
專案練習：撰寫 NIC 驅動診斷與修復 SOP

Assessment Criteria（評估標準）
功能完整性（40%）：網路恢復可用
程式碼品質（30%）：記錄清晰，命令正確
效能優化（20%）：復原時間短、步驟最少
創新性（10%）：替代連網方案設計


## Case #5: 安裝過程出現「CDROM 內容不對」錯誤（USB 安裝）

### Problem Statement（問題陳述）
業務場景：多次嘗試不同發行版（12.04、14.04、CentOS），安裝中出現「CDROM 內容不對」錯誤，雖已比對 MD5 仍無解。需排除 USB 製作與開機參數影響。
技術挑戰：判斷是 ISO 問題、USB 製作方法、或安裝器辨識邏輯造成。
影響範圍：無法繼續安裝。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. USB 製作方式導致卷標/結構不符合安裝器預期
2. 舊硬體 BIOS/控制器對 USB 相容性較差
3. 安裝器使用 CDROM 檢測邏輯未正確辨識 USB

深層原因：
- 架構層面：安裝器對多種媒體辨識不夠健壯
- 技術層面：Rufus/UNetbootin 模式選錯
- 流程層面：缺乏替代引導參數與驗證步驟

### Solution Design（解決方案設計）
解決策略：改用 dd 模式重製 USB，或在開機參數加入 cdrom/usb 偵測選項，必要時改用另一版本或另一工具；亦可在 BIOS 切換 USB 模式。

實施步驟：
1. 重新製作 USB（dd 模式）
- 實作細節：Rufus 選擇 DD 模式或使用 balenaEtcher
- 所需資源：USB 工具
- 預估時間：0.5 小時

2. 設定開機參數
- 實作細節：於 boot 參數加入 cdrom-detect/try-usb=true
- 所需資源：安裝器開機選單
- 預估時間：0.5 小時

3. BIOS 相容性調整
- 實作細節：切換 USB 2.0/3.0、開關 Legacy/UEFI
- 所需資源：BIOS
- 預估時間：0.5 小時

關鍵程式碼/設定：
```text
# 在安裝器開機畫面（按 e 編輯內核引數），增加：
cdrom-detect/try-usb=true apt-setup/disable-cdrom=true

# 另可嘗試 (視發行版安裝器支援)
boot=casper
```

實際案例：作者多次遇到「CDROM 內容不對」，最終透過更換 USB 工具與版本解決。
實作環境：Acer Aspire 5742Z、Ubuntu/CentOS 安裝器
實測數據：
改善前：安裝中斷
改善後：安裝可繼續
改善幅度：成功率 0% -> 100%（針對該機器）

Learning Points（學習要點）
核心知識點：
- 安裝器媒體偵測邏輯
- 開機參數調整技巧
- BIOS 相容性設定

技能要求：
必備技能：基本 BIOS 操作、引導參數修改
進階技能：安裝器除錯與媒體製作細節

延伸思考：
- 是否改用 PXE/網路安裝環境？
- 建立標準化 USB 製作器（腳本化）
- 多發行版安裝器差異

Practice Exercise（練習題）
基礎練習：以 DD 模式重製 USB 並測試
進階練習：嘗試開機參數強制 USB 偵測
專案練習：整理一份跨發行版安裝疑難排解指南

Assessment Criteria（評估標準）
功能完整性（40%）：安裝可順利進行
程式碼品質（30%）：參數正確、文件清楚
效能優化（20%）：嘗試步驟節省時間
創新性（10%）：備援方案設計


## Case #6: Ubuntu Desktop 安裝進入桌面即凍結（GUI 問題）

### Problem Statement（問題陳述）
業務場景：在舊筆電上嘗試 Desktop 版，開到桌面便當機。考慮改用 Server 版避免 GUI 相關相容性。
技術挑戰：釐清是顯示驅動、桌面環境還是硬體問題；並確保能完成安裝。
影響範圍：安裝無法完成，影響時程。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 舊 GPU 與新桌面環境/驅動不相容
2. 記憶體不足導致桌面載入不穩
3. 內建破損螢幕與外接顯示切換造成問題

深層原因：
- 架構層面：桌面環境依賴較多圖形堆疊
- 技術層面：缺乏顯示驅動除錯（nomodeset 等）
- 流程層面：未先驗證硬體相容性即嘗試 GUI

### Solution Design（解決方案設計）
解決策略：改用 Server 版（無 GUI）進行安裝，必要時在開機參數加入 nomodeset；後續僅用 SSH 遠端管理，避免圖形堆疊風險。

實施步驟：
1. 使用 Server 版安裝
- 實作細節：最小化安裝，啟用 SSH
- 所需資源：Server ISO
- 預估時間：1 小時

2. 啟用 nomodeset（若需）
- 實作細節：於開機選單暫時加入，安裝後寫入 GRUB
- 所需資源：GRUB
- 預估時間：0.5 小時

關鍵程式碼/設定：
```bash
# 一次性（開機畫面按 e），在 linux 行加入 nomodeset

# 永久寫入 /etc/default/grub
sudo sed -i 's/GRUB_CMDLINE_LINUX=""/GRUB_CMDLINE_LINUX="nomodeset"/' /etc/default/grub
sudo update-grub
```

實際案例：作者 Desktop 版進桌面即不動，最終使用 Server 版成功安裝。
實作環境：Acer Aspire 5742Z、Ubuntu Server 15.10
實測數據：
改善前：安裝卡 GUI
改善後：安裝完成並可用 SSH 管理
改善幅度：成功率 0% -> 100%

Learning Points（學習要點）
核心知識點：
- nomodeset 與圖形驅動故障繞過
- 伺服器無頭化的價值
- GRUB 引數管理

技能要求：
必備技能：GRUB 編輯、SSH
進階技能：顯示驅動相容性排除

延伸思考：
- 事後是否仍需 GUI？可裝輕量桌面
- 圖形加速與容器的關係（通常不必）
- 遠端管理工具替代 GUI（Cockpit 等）

Practice Exercise（練習題）
基礎練習：在 GRUB 中加入 nomodeset 開機
進階練習：完成 Server 版安裝與 SSH 管理
專案練習：撰寫 GUI 卡死的診斷與替代方案報告

Assessment Criteria（評估標準）
功能完整性（40%）：可開機、可 SSH
程式碼品質（30%）：設定變更記錄清晰
效能優化（20%）：輕量化安裝
創新性（10%）：替代管理工具整合


## Case #7: 移除無線網卡解決安裝異常（硬體衝突）

### Problem Statement（問題陳述）
業務場景：安裝過程中遇到不明卡頓與失敗，最後將無線網卡直接拔除後才順利安裝完成。顯示無線網卡或其驅動可能造成衝突。
技術挑戰：快速定位故障元件，提供可逆的規避方案。
影響範圍：安裝進度受阻、穩定性不佳。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 無線網卡硬體損壞或接觸不良
2. 驅動（模組）於安裝階段載入後造成 hang
3. 與其他裝置（顯示/有線網卡）產生中斷衝突

深層原因：
- 架構層面：安裝器對硬體異常的容錯不足
- 技術層面：模組黑名單與安裝器參數不熟悉
- 流程層面：未逐步排除硬體（最小化配置法）

### Solution Design（解決方案設計）
解決策略：以最小化硬體配置進行安裝（拔除 Wi-Fi），或於開機參數先黑名單對應驅動；安裝完成後再行加入並測試穩定性。

實施步驟：
1. 最小化硬體配置
- 實作細節：移除/停用無線網卡
- 所需資源：螺絲起子/BIOS
- 預估時間：0.5 小時

2. 黑名單驅動（不拆機方案）
- 實作細節：將疑似模組列入黑名單
- 所需資源：modprobe.d 設定
- 預估時間：0.5 小時

關鍵程式碼/設定：
```bash
# 黑名單無線網卡（例如 ath9k 或 b43，依實機而定）
echo "blacklist ath9k" | sudo tee /etc/modprobe.d/blacklist-wifi.conf
sudo update-initramfs -u
```

實際案例：作者拔除無線網卡後，換用 15.10 成功安裝。
實作環境：Acer Aspire 5742Z
實測數據：
改善前：安裝多次失敗
改善後：安裝一次到位
改善幅度：成功率大幅提升（質性）

Learning Points（學習要點）
核心知識點：
- 最小化硬體法（最小可行配置）
- 模組黑名單與 initramfs
- 安裝後逐步加回硬體檢測

技能要求：
必備技能：硬體拆裝或 BIOS 操作
進階技能：initramfs 與模組管理

延伸思考：
- 安裝後是否需要換新 Wi-Fi 卡或 USB Wi-Fi？
- 是否紀錄硬體相容名單？
- 失敗時如何回溯與記錄？

Practice Exercise（練習題）
基礎練習：建立一個模組黑名單檔並更新 initramfs
進階練習：嘗試以最小硬體配置安裝虛擬機並逐步加裝
專案練習：撰寫硬體排除法 SOP（表格化）

Assessment Criteria（評估標準）
功能完整性（40%）：能順利安裝
程式碼品質（30%）：黑名單設定正確
效能優化（20%）：排除步驟簡潔有效
創新性（10%）：替代方案與驗證設計


## Case #8: 安裝並強化 OpenSSH Server（無頭管理）

### Problem Statement（問題陳述）
業務場景：完成 Server 安裝後，需要遠端管理與自動化部署；需快速架設 SSH 並做基本加固（密碼策略、防火牆、金鑰登入）。
技術挑戰：兼顧便利與安全，避免弱點暴露。
影響範圍：SSH 安全欠佳會影響整體主機風險。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 預設未安裝 SSH 或未啟用
2. 密碼登入風險高
3. 防火牆未配置

深層原因：
- 架構層面：缺乏統一的存取與憑證策略
- 技術層面：不了解 sshd_config 與 UFW
- 流程層面：未建立初始硬化步驟

### Solution Design（解決方案設計）
解決策略：安裝 openssh-server、啟用 UFW 僅允許必要連線、建立金鑰登入並關閉密碼登入，設定自動更新安全修補。

實施步驟：
1. 安裝與啟用 SSH
- 實作細節：安裝、開機自動啟動
- 所需資源：apt
- 預估時間：0.5 小時

2. 金鑰登入與加固
- 實作細節：建立金鑰、禁密碼、非標準 Port（選）
- 所需資源：ssh-keygen、sshd_config
- 預估時間：0.5 小時

3. 防火牆
- 實作細節：UFW 開放 SSH 與必要服務
- 所需資源：ufw
- 預估時間：0.25 小時

關鍵程式碼/設定：
```bash
sudo apt-get update && sudo apt-get install -y openssh-server ufw
sudo systemctl enable --now ssh

# 建立金鑰（在管理端）
ssh-keygen -t ed25519
ssh-copy-id user@server

# /etc/ssh/sshd_config 重要設定
PasswordAuthentication no
PermitRootLogin prohibit-password
PubkeyAuthentication yes

sudo systemctl restart ssh

# UFW
sudo ufw allow OpenSSH
sudo ufw enable
```

實際案例：作者完成基本環境配置（含 SSH）。
實作環境：Ubuntu Server 15.10
實測數據：
改善前：僅可本機操作
改善後：可遠端安全管理
改善幅度：管理效率顯著提升（質性）

Learning Points（學習要點）
核心知識點：
- sshd_config 安全選項
- 金鑰登入與授權管理
- UFW 基本用法

技能要求：
必備技能：Linux 基本操作、SSH
進階技能：安全基線設定

延伸思考：
- Fail2ban 是否需要？
- 多人協作金鑰輪替策略
- 記錄與審計（journald）

Practice Exercise（練習題）
基礎練習：配置金鑰登入並禁用密碼
進階練習：UFW 僅允許管理端 IP 存取
專案練習：撰寫 SSH 加固基線腳本

Assessment Criteria（評估標準）
功能完整性（40%）：SSH 可用且金鑰登入
程式碼品質（30%）：設定正確、註解清楚
效能優化（20%）：存取控制合理
創新性（10%）：加固自動化


## Case #9: 設定固定 IP（避免 DHCP 變動影響）

### Problem Statement（問題陳述）
業務場景：伺服器採預設 DHCP，導致 IP 變動使得 SSH 與服務定位困難。需要設定固定 IP 以便穩定對外提供服務與管理。
技術挑戰：Ubuntu 15.10 使用 ifupdown，需正確編輯 interfaces 並避免衝突。
影響範圍：IP 改變將造成中斷與定位困難。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. DHCP 分配 IP 不保證恆定
2. 未在 DHCP 伺服器保留租約
3. 未配置靜態路由與 DNS

深層原因：
- 架構層面：缺乏網段規劃
- 技術層面：不熟悉 ifupdown/netplan 差異
- 流程層面：未定義 IP 命名與管理規範

### Solution Design（解決方案設計）
解決策略：於 /etc/network/interfaces 設定靜態 IP、Gateway、DNS；或在 DHCP Server 以 MAC 保留；以文件化落地。

實施步驟：
1. 盤點網段
- 實作細節：確認可用 IP、網關、DNS
- 所需資源：路由器管理介面
- 預估時間：0.25 小時

2. 編輯 interfaces
- 實作細節：設定 eth0 為 static
- 所需資源：編輯器
- 預估時間：0.25 小時

關鍵程式碼/設定：
```bash
# /etc/network/interfaces
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet static
  address 192.168.1.50
  netmask 255.255.255.0
  gateway 192.168.1.1
  dns-nameservers 1.1.1.1 8.8.8.8

sudo systemctl restart networking
```

實際案例：作者完成固定 IP 設定。
實作環境：Ubuntu Server 15.10
實測數據：
改善前：IP 不固定，連線不穩
改善後：IP 固定，定位穩定
改善幅度：可用性提升（質性）

Learning Points（學習要點）
核心知識點：
- ifupdown 靜態網路設定
- DNS 指定與測試
- DHCP 保留策略

技能要求：
必備技能：Linux 網路設定
進階技能：網段規劃與命名

延伸思考：
- IPv6 是否同設？
- 多網卡路由優先順序？
- NetworkManager 衝突避免？

Practice Exercise（練習題）
基礎練習：設定靜態 IP 並 ping 測試
進階練習：同時配置多 DNS 並驗證
專案練習：撰寫網路設定變更 SOP

Assessment Criteria（評估標準）
功能完整性（40%）：IP 固定可連通
程式碼品質（30%）：設定正確、註解清楚
效能優化（20%）：DNS/路由合理
創新性（10%）：DHCP 保留整合


## Case #10: 以 Samba 建立跨平台網路分享

### Problem Statement（問題陳述）
業務場景：需於家庭/小型辦公環境提供跨平台檔案共享，便於容器資料交換與備份。選用 Samba 快速提供 SMB 服務。
技術挑戰：設定權限、使用者管理與防火牆開放。
影響範圍：檔案共享不可用將影響佈署效率。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 預設無 SMB 服務
2. 權限與目錄結構未規劃
3. 防火牆未放行

深層原因：
- 架構層面：存取權限與群組策略缺失
- 技術層面：smb.conf 配置不熟
- 流程層面：未建立使用者/群組準則

### Solution Design（解決方案設計）
解決策略：安裝 Samba，建立共享目錄與群組權限，限制只允許內網，記錄存取規範。

實施步驟：
1. 安裝與目錄建立
- 實作細節：安裝 samba，建立 /srv/share 與權限
- 所需資源：apt
- 預估時間：0.5 小時

2. smb.conf 配置
- 實作細節：定義 share、只允許內網
- 所需資源：編輯器
- 預估時間：0.5 小時

關鍵程式碼/設定：
```bash
sudo apt-get install -y samba
sudo mkdir -p /srv/share
sudo groupadd smbgrp
sudo chgrp -R smbgrp /srv/share
sudo chmod -R 2775 /srv/share

# /etc/samba/smb.conf
[global]
   workgroup = WORKGROUP
   map to guest = Bad User
   server min protocol = SMB2

[public]
   path = /srv/share
   browsable = yes
   writable = yes
   guest ok = no
   valid users = @smbgrp

# 建立使用者
sudo useradd -m alice -G smbgrp
sudo smbpasswd -a alice

sudo systemctl restart smbd nmbd
sudo ufw allow 137,138/udp
sudo ufw allow 139,445/tcp
```

實際案例：作者提及已設定 Samba 完成網路分享。
實作環境：Ubuntu Server 15.10
實測數據：
改善前：檔案交換不便
改善後：可跨平台共享
改善幅度：作業效率提升（質性）

Learning Points（學習要點）
核心知識點：
- Samba 基本共享配置
- 權限與群組繼承（setgid）
- SMB 防火牆設定

技能要求：
必備技能：Linux 使用者/權限
進階技能：Samba 安全與效能調校

延伸思考：
- 是否改用 NFS 對 Linux 容器更友善？
- 版本協商與舊客戶端相容性
- 共享與備份策略整合

Practice Exercise（練習題）
基礎練習：建立一個可寫入的共享
進階練習：限制僅內網可存取
專案練習：規劃含多共享/群組的 SMB 方案

Assessment Criteria（評估標準）
功能完整性（40%）：共享可用、權限正確
程式碼品質（30%）：配置明確、註解完整
效能優化（20%）：傳輸穩定
創新性（10%）：存取政策與備份整合


## Case #11: 在 Ubuntu 15.10 安裝與配置 Docker Engine

### Problem Statement（問題陳述）
業務場景：為了在非 NAS 平台上彈性運行容器，需要於 Ubuntu Server 15.10 安裝 Docker，並確保一般使用者可操作與開機自動啟動。
技術挑戰：在較舊發行版上正確安裝並設定權限與啟動方式。
影響範圍：安裝不當會影響後續部署。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 預設未安裝 Docker
2. 權限不足（需 docker 群組）
3. 開機未自動啟動

深層原因：
- 架構層面：容器化落地流程未標準化
- 技術層面：舊版套件來源差異
- 流程層面：未建立安裝驗收步驟

### Solution Design（解決方案設計）
解決策略：使用官方腳本或套件庫安裝 Docker，將使用者加入 docker 群組，設定服務自動啟動並以 hello-world 驗證。

實施步驟：
1. 安裝 Docker
- 實作細節：使用官方 get.docker.com 或套件庫
- 所需資源：curl/apt
- 預估時間：0.5 小時

2. 權限設定與驗證
- 實作細節：usermod 加入 docker、運行測試容器
- 所需資源：shell
- 預估時間：0.25 小時

關鍵程式碼/設定：
```bash
# 快速安裝（舊版系統用）
curl -fsSL https://get.docker.com | sh

# 權限
sudo usermod -aG docker $USER
newgrp docker

# 自動啟動
sudo systemctl enable --now docker

# 驗證
docker run --rm hello-world
```

實際案例：作者在新主機上運行 Docker 以承接實驗用途。
實作環境：Ubuntu Server 15.10、Docker
實測數據：
改善前：無容器平台
改善後：可啟動容器
改善幅度：部署能力提升（質性）

Learning Points（學習要點）
核心知識點：
- Docker 安裝與服務管理
- 群組權限與安全
- 基礎健康檢查

技能要求：
必備技能：Linux/apt、systemd
進階技能：Docker 儲存與網路設定

延伸思考：
- 是否鎖定 Docker 版本避免破壞性更新？
- logs 與 dirver（overlay2）選擇
- rootless 模式可行性

Practice Exercise（練習題）
基礎練習：安裝 Docker 並執行 hello-world
進階練習：建立一個具有健康檢查的容器
專案練習：寫一份 Docker 安裝基線腳本

Assessment Criteria（評估標準）
功能完整性（40%）：Docker 可用
程式碼品質（30%）：腳本健壯
效能優化（20%）：啟動時間與資源佔用
創新性（10%）：版本與配置管理


## Case #12: 在 NAS 上以 Nginx 建立反向代理

### Problem Statement（問題陳述）
業務場景：將部落格與其他服務透過 NAS 上的反向代理統一對外，簡化網域/證書與路由管理，也便於未來導入第二主機。
技術挑戰：正確路由至內部容器、處理 Header 與壓縮、健康檢查。
影響範圍：入口錯誤會造成服務不可達或安全風險。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 多服務需共用 80/443
2. 內部容器位於不同主機/port
3. 未統一處理 TLS 與快取

深層原因：
- 架構層面：需要 API Gateway/反代集中管理
- 技術層面：Nginx 反代配置與容器網路
- 流程層面：證書續期與路由變更流程缺失

### Solution Design（解決方案設計）
解決策略：以 Nginx（容器化）作為入口，配置 upstream 與 proxy，集中處理 TLS 與壓縮；後續可切換至 Traefik/NGINX Proxy Manager 做自動化。

實施步驟：
1. 部署 Nginx 反代容器
- 實作細節：map 設定與憑證
- 所需資源：docker-compose
- 預估時間：0.5 天

2. 配置站點
- 實作細節：upstream 與 proxy_* 參數
- 所需資源：Nginx conf
- 預估時間：0.5 天

關鍵程式碼/設定：
```nginx
# /etc/nginx/conf.d/blog.conf
upstream blog_upstream {
    server blog:2368; # 內部容器名稱:port
}
server {
    listen 80;
    server_name blog.example.com;

    location / {
        proxy_pass http://blog_upstream;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

實際案例：作者於 NAS 上建立反向代理，將部落格服務對外。
實作環境：Synology NAS、Docker Nginx
實測數據：
改善前：多服務直出管理混亂
改善後：單一入口集中管控
改善幅度：可維運性提升（質性）

Learning Points（學習要點）
核心知識點：
- Nginx 反代與 upstream
- 代理 Headers 與 TLS 終結
- 容器 DNS 與跨容器連線

技能要求：
必備技能：Nginx 基本配置
進階技能：TLS、自動化簽證（Let’s Encrypt）

延伸思考：
- 引入 Traefik 實現自動路由與憑證
- 健康檢查與回源超時策略
- 灰度路由/藍綠部署

Practice Exercise（練習題）
基礎練習：建立一個簡單反代站點
進階練習：加入 gzip 與快取設定
專案練習：以 docker-compose 管理多站反代

Assessment Criteria（評估標準）
功能完整性（40%）：代理正常、Header 正確
程式碼品質（30%）：配置清晰、可維護
效能優化（20%）：壓縮/快取合理
創新性（10%）：自動化與監控整合


## Case #13: 將部落格自代管商（GoDaddy）遷移回自家 NAS

### Problem Statement（問題陳述）
業務場景：原先部落格放於 GoDaddy hosting，決定遷回自家 NAS 上，且以 Docker 部署並由反向代理對外，降低成本並提升掌控度。
技術挑戰：資料遷移、容器化、DNS 切換與停機時間控制。
影響範圍：遷移過程若處理不當將造成服務中斷。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 外部 hosting 受限且成本持續
2. 需要與現有容器體系整合
3. DNS/SSL 需重配置

深層原因：
- 架構層面：自託管帶來控制權但需良好運維
- 技術層面：容器化與資料一致性
- 流程層面：缺少遷移切換計畫

### Solution Design（解決方案設計）
解決策略：先在 NAS 以容器完成部落格落地（資料卷），測試無誤後調整反代，最後再切 DNS 以將流量導向新環境，並保留回滾方案。

實施步驟：
1. 資料導出與容器落地
- 實作細節：靜態網站可直接掛載；動態 CMS 匯出 DB
- 所需資源：rsync/docker
- 預估時間：0.5-1 天

2. 預先驗證與壓測
- 實作細節：內網域名、curl 檢查
- 所需資源：Nginx 反代、hosts
- 預估時間：0.5 天

3. DNS 切換與監控
- 實作細節：TTL 降低、切換後監控
- 所需資源：DNS 控制台
- 預估時間：0.25 天

關鍵程式碼/設定：
```yaml
# docker-compose.yml（靜態網站以 Nginx 提供）
version: "3.8"
services:
  blog:
    image: nginx:alpine
    volumes:
      - ./public:/usr/share/nginx/html:ro
    restart: unless-stopped
    networks:
      - proxy
networks:
  proxy:
    external: true
```

實際案例：作者將部落格移回 NAS，透過反向代理對外。
實作環境：Synology NAS、Docker、Nginx
實測數據：
改善前：外部代管、控制度低
改善後：自託管、集中管理
改善幅度：掌控度提升（質性）

Learning Points（學習要點）
核心知識點：
- 資料遷移與容器化
- DNS TTL 與切換策略
- 回滾設計

技能要求：
必備技能：Docker/Nginx 基礎、DNS 操作
進階技能：零停機切換與監控

延伸思考：
- CDN/快取是否導入？
- SSL/TLS 自動續期
- 備援與異地備份

Practice Exercise（練習題）
基礎練習：以 Nginx 容器提供靜態站
進階練習：模擬 DNS 切換流程（hosts）
專案練習：完成一次實際遷站（測試域名）

Assessment Criteria（評估標準）
功能完整性（40%）：站點可用、無主要缺頁
程式碼品質（30%）：compose 與 Nginx 配置清楚
效能優化（20%）：壓測穩定
創新性（10%）：回滾與監控設計


## Case #14: 使用筆電電池當作內建 UPS，實作安全關機

### Problem Statement（問題陳述）
業務場景：用舊筆電作為主機時，其電池可在停電時充當短暫 UPS，為避免資料毀損需在低電量自動安全關機。
技術挑戰：準確偵測電量並觸發自動關機，避免誤判。
影響範圍：不當關機可能造成檔案系統損毀。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 停電時無自動保護機制
2. 人工關機不及時
3. 無監控告警

深層原因：
- 架構層面：缺乏電力事件處理
- 技術層面：acpid/upower 未配置
- 流程層面：未建立測試與演練機制

### Solution Design（解決方案設計）
解決策略：以 upower 查詢電量、acpid 監聽電源事件，門檻值觸發有序關機；寫入日誌並提供測試命令。

實施步驟：
1. 安裝與檢測
- 實作細節：upower 確認電池路徑與百分比
- 所需資源：upower/acpid
- 預估時間：0.5 小時

2. 事件與腳本
- 實作細節：acpid 事件綁定 battery-low.sh
- 所需資源：shell
- 預估時間：0.5 小時

關鍵程式碼/設定：
```bash
# 測試取得電量
upower -e
upower -i /org/freedesktop/UPower/devices/battery_BAT0 | grep percentage

# 事件腳本同 Case #2，可加日誌
logger "Battery low, shutting down"
```

實際案例：作者將電池視為內建 UPS 的概念並落地。
實作環境：Ubuntu Server 15.10、Acer Aspire 5742Z
實測數據：
改善前：停電風險高
改善後：低電量自動關機
改善幅度：資料風險下降（質性）

Learning Points（學習要點）
核心知識點：
- 電力事件監控
- 安全關機流程
- 日誌與測試

技能要求：
必備技能：shell、systemd
進階技能：告警整合（mail/telegram）

延伸思考：
- 外接 UPS 與 NUT 整合
- 關機前先停服務/容器
- 復電自動恢復策略

Practice Exercise（練習題）
基礎練習：撰寫電量查詢腳本
進階練習：掛 acpid 事件自動關機
專案練習：整合通知並演練停電流程

Assessment Criteria（評估標準）
功能完整性（40%）：事件觸發與關機生效
程式碼品質（30%）：腳本健壯、日誌完善
效能優化（20%）：誤判控制與回測
創新性（10%）：通知與自動恢復設計


## Case #15: 低資源硬體上的容器資源限制與穩定性

### Problem Statement（問題陳述）
業務場景：NAS 與舊筆電資源有限（低核數/1GB RAM），需要對容器施加資源限制與日誌輪轉，避免 OOM 與磁碟被日誌占滿。
技術挑戰：合理設定記憶體/CPU/日誌與重啟策略。
影響範圍：未限制可能導致服務崩潰。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 容器預設不限記憶體與 CPU
2. 日誌預設無限增長
3. 無重啟策略保護

深層原因：
- 架構層面：資源治理缺失
- 技術層面：Docker 選項未善用
- 流程層面：缺乏容量監控

### Solution Design（解決方案設計）
解決策略：為容器設定 mem/cpu、log-opts 與 restart policy，配合監控定期檢視。

實施步驟：
1. 調整資源限制
- 實作細節：--memory、--cpus
- 所需資源：docker-compose
- 預估時間：0.25 天

2. 日誌與重啟
- 實作細節：--log-opt max-size、restart: unless-stopped
- 所需資源：Docker
- 預估時間：0.25 天

關鍵程式碼/設定：
```yaml
services:
  app:
    image: your/app:prod
    mem_limit: 256m
    cpus: "0.5"
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

實際案例：作者對資源有限問題有所考量，並外移實驗負載（見 Case #1）。
實作環境：Synology NAS、Ubuntu 主機、Docker
實測數據：
改善前：資源爭用風險高
改善後：可控且穩定
改善幅度：穩定性提升（質性）

Learning Points（學習要點）
核心知識點：
- Docker 資源限制
- 日誌輪轉
- 重啟策略

技能要求：
必備技能：Docker 選項
進階技能：監控/警報（docker stats/Prometheus）

延伸思考：
- cgroup v1/v2 差異
- 優先級與 cpuset 分配
- 預算內的硬體升級策略

Practice Exercise（練習題）
基礎練習：替現有容器加上 mem/cpu 限制
進階練習：設定日誌輪轉並驗證
專案練習：針對 1GB RAM 機器規劃容器配額

Assessment Criteria（評估標準）
功能完整性（40%）：限制生效
程式碼品質（30%）：配置清楚
效能優化（20%）：避免 OOM 且服務穩定
創新性（10%）：監控與調整策略


## Case #16: 安裝疑難排解流程與診斷方法（整體整理）

### Problem Statement（問題陳述）
業務場景：連續遭遇多個安裝阻礙（USB 工具、CDROM 錯誤、GUI 凍結、NIC/無線衝突），需要系統化的診斷流程快速定位與解決。
技術挑戰：在老舊硬體上建立高成功率的安裝 SOP。
影響範圍：避免重工與時間成本。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 工具選擇錯誤（netinstall/非 dd）
2. 硬體相容性差（Wi-Fi/GPU）
3. 版本差異（舊版驅動不全）

深層原因：
- 架構層面：未建立標準化安裝流程
- 技術層面：缺少診斷命令與技巧
- 流程層面：未落實最小化配置法

### Solution Design（解決方案設計）
解決策略：制定「最小化硬體 + dd USB + Server 版 + 必要開機參數 + 逐步加回元件」的 SOP，搭配診斷命令與記錄，快速收斂問題。

實施步驟：
1. 前置檢核
- 實作細節：ISO 校驗、BIOS 設定、dd 製作
- 所需資源：校驗工具
- 預估時間：0.5 天

2. 最小化安裝
- 實作細節：拔 Wi-Fi、Server 版、nomodeset
- 所需資源：安裝器
- 預估時間：0.5 天

3. 逐步加回與記錄
- 實作細節：一次加一項硬體，記錄 dmesg
- 所需資源：dmesg、journalctl
- 預估時間：0.5 天

關鍵程式碼/設定：
```bash
# 記錄診斷
dmesg -T > /var/log/dmesg.install.log
journalctl -b -1 > /var/log/last-boot.log

# 確認硬體
lspci -nn
lsusb
lsmod
```

實際案例：綜合文中多個阻礙的解法彙整成 SOP。
實作環境：Acer Aspire 5742Z、Ubuntu Server 15.10
實測數據：
改善前：多次失敗、耗時
改善後：一次到位或快速收斂
改善幅度：安裝效率大幅提升（質性）

Learning Points（學習要點）
核心知識點：
- 診斷命令與日誌收集
- SOP 與最小化配置法
- 逐步回歸與變更控制

技能要求：
必備技能：Linux 診斷工具
進階技能：SOP 撰寫與知識庫整理

延伸思考：
- 將 SOP 模板化與自動化
- 建立裝機可檢核清單
- 分享社群（Issue/Forum）擴充知識

Practice Exercise（練習題）
基礎練習：收集一次安裝日誌與硬體清單
進階練習：撰寫安裝 SOP 並實測
專案練習：建立一個可重用的裝機工具包

Assessment Criteria（評估標準）
功能完整性（40%）：SOP 可執行且成功
程式碼品質（30%）：命令與文件清晰
效能優化（20%）：時間成本下降
創新性（10%）：工具化與分享


--------------------------------
案例分類
1. 按難度分類
- 入門級：Case #3, #4, #8, #9, #10, #11
- 中級：Case #1, #2, #5, #6, #7, #12, #13, #15, #16
- 高級：無（涉及高級內容可延伸到叢集與自動化）

2. 按技術領域分類
- 架構設計類：Case #1, #2, #12, #13, #15, #16
- 效能優化類：Case #1, #15
- 整合開發類：Case #12, #13
- 除錯診斷類：Case #3, #4, #5, #6, #7, #16
- 安全防護類：Case #8, #12（TLS/反代可延伸）

3. 按學習目標分類
- 概念理解型：Case #1, #2, #12
- 技能練習型：Case #8, #9, #10, #11, #15
- 問題解決型：Case #3, #4, #5, #6, #7, #16
- 創新應用型：Case #2, #14, #13

--------------------------------
案例關聯圖（學習路徑建議）
- 建議先學（基礎環境與工具）：Case #3（USB 製作）、#6（Server 版/nomodeset 概念）、#4（NIC 問題）、#7（最小化硬體）
- 其後（完成系統與基礎服務）：Case #8（SSH）、#9（固定 IP）、#10（Samba）
- 容器平台建立：Case #11（Docker 安裝）
- 架構與對外服務：Case #12（反向代理）、#13（遷移部落格）
- 資源治理與可靠性：Case #1（分流）、#15（資源限制）、#14（UPS 化）
- 系統化沉澱：Case #16（SOP 與診斷）

依賴關係示意：
- Case #3 → #6/#4/#7 → #8/#9 → #11 → #12 → #13
- Case #1 依賴 #11/#12（已能運行容器與反代）
- Case #15 建議在 #11 後實施
- Case #14 可於 #2 完成後導入
- Case #16 橫向支援所有案例，作為知識化沉澱

完整學習路徑建議：
1) 先掌握安裝與硬體問題排除（#3, #4, #5, #6, #7）
2) 配置無頭與網路基礎（#8, #9, #10）
3) 建置 Docker 平台（#11）
4) 建構對外服務入口與遷移（#12, #13）
5) 針對低資源情境做資源治理與穩定性提升（#1, #15, #14）
6) 最後以 SOP 將經驗標準化（#16）

以上 16 個案例均可獨立授課、搭配專案實作與評估，並能串接成系統化學習路徑。