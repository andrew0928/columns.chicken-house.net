---
layout: synthesis
title: "用 WSL + VSCode 重新打造 Linux 開發環境"
synthesis_type: solution
source_post: /2024/11/11/working-with-wsl/
redirect_from:
  - /2024/11/11/working-with-wsl/solution/
postid: 2024-11-11-working-with-wsl
---
{% raw %}

以下內容根據原文逐一萃取並重構為可教學、可實作、可評測的問題解決案例。每個案例包含問題、根因、方案、實施、程式碼、實測數據、學習要點、練習與評估標準。共 18 個案例。

```markdown
## Case #1: Qdrant 在 Windows Volume 上啟動極慢

### Problem Statement（問題陳述）
**業務場景**：本地端搭建向量資料庫 Qdrant，作為 RAG 測試平台的底層向量索引服務。資料量約 4 萬筆、數 GB，需頻繁隨機讀寫與重啟容器驗證資料一致性。開發機為 Windows 11，Docker 以掛載 Windows 路徑的方式啟動容器。

**技術挑戰**：容器掛載 Windows 目錄（/mnt/c）作為 Qdrant 的資料目錄，導致隨機 IO 效能嚴重衰退，容器啟動時間長達數十秒至一分鐘，插入/恢復資料緩慢，開發體驗無法接受。

**影響範圍**：- 服務啟動等待時間過長 - 測試與資料載入時間無法預期 - 同類型 DB/索引服務都受影響

**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 容器透過 DrvFS 掛載 NTFS：WSL 機制以 9P 協定/DrvFS 轉譯 NTFS 與 EXT4，跨 OS Kernel 檔案操作延遲高。
2. 高隨機 IO 工作負載：Qdrant 啟動會大量掃描/恢復 collection，4K 隨機讀寫對跨層轉譯極度敏感。
3. 檔案事件機制不相容：NTFS 的 FileSystemWatcher 與 Linux inotify 不一致，容器側無法有效偵測變更，退化為輪巡。

**深層原因**：
- 架構層面：資料放在 Windows 檔案系統，計算放在 Linux（WSL/Docker），造成跨 Kernel I/O。
- 技術層面：DrvFS/9P 的協定延遲與 Hyper-V 虛擬化額外開銷。
- 流程層面：沿用「把主機目錄直接掛進容器」的習慣，忽略 WSL 檔案系統差異。

### Solution Design（解決方案設計）
**解決策略**：將 Qdrant 資料目錄搬入 WSL EXT4（如 /opt/docker/qdrant），改由 WSL 內安裝的 Docker 執行容器與掛載 volume，完全避免跨 Kernel I/O；Windows 端以 mklink 映射 WSL 路徑僅作瀏覽，不進行大量 IO。

**實施步驟**：
1. 移轉資料至 WSL EXT4
- 實作細節：建立 /opt/docker/qdrant，將原資料搬移到該目錄
- 所需資源：WSL Ubuntu、rsync 或 cp
- 預估時間：0.5 小時

2. 在 WSL 內安裝 Docker 並啟動
- 實作細節：安裝 docker-ce，設定 systemctl 啟動
- 所需資源：apt、systemd（WSL）
- 預估時間：0.5 小時

3. 更新 docker-compose volume 映射
- 實作細節：將 volume 映射到 /opt/docker/qdrant
- 所需資源：docker compose
- 預估時間：0.5 小時

4. Windows 端建立方便瀏覽的連結
- 實作細節：mklink /d 將 \\wsl$\ubuntu\opt\docker 映射為 c:\CodeWork\docker
- 所需資源：mklink.exe
- 預估時間：10 分鐘

**關鍵程式碼/設定**：
```yaml
# docker-compose.yml 範例（Qdrant）
services:
  qdrant:
    image: qdrant/qdrant:latest
    container_name: qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - /opt/docker/qdrant:/qdrant/storage    # 關鍵：WSL EXT4 位置
    restart: unless-stopped
```

```bat
:: Windows 端建立方便入口（僅瀏覽，勿大量 IO）
mklink /d C:\CodeWork\docker \\wsl$\Ubuntu\opt\docker
```

實際案例：Qdrant（資料量約 40k 筆、檔案 28 萬個、5.386GB）
實作環境：Windows 11 24H2 + WSL2 Ubuntu 24.04 + Docker CE
實測數據：
- 改善前：/mnt/c 掛載，啟動 38.376 秒
- 改善後：WSL EXT4 掛載，啟動 1.499 秒
- 改善幅度：約 25.6 倍

Learning Points（學習要點）
核心知識點：
- DrvFS/9P 協定的跨 Kernel I/O 代價
- 容器資料放置位置對效能的巨大影響
- WSL EXT4 與 NTFS 的事件/權限模型差異

技能要求：
- 必備技能：Docker 基本操作、WSL 目錄操作
- 進階技能：Linux I/O 模式與檔案系統觀念、docker-compose 最佳實務

延伸思考：
- 其他高 I/O 服務（如 OLTP DB、搜尋引擎）同理可得
- 若需極致效能，是否要採用 WSL 專用實體磁碟？
- 如何以監控（如 iostat、pidstat）量化日常效能？

Practice Exercise（練習題）
- 基礎練習：將一個小型 SQLite 容器從 /mnt/c 改到 /opt/docker，量測查詢時間差（30 分）
- 進階練習：以 fio 模擬 4k randrw 比較 /mnt/c 與 /opt/docker（2 小時）
- 專案練習：完成一份「容器資料安置策略」文件與自動化 compose（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：容器可啟動、資料保留、Volume 位置正確
- 程式碼品質（30%）：compose 清楚、目錄結構合理
- 效能優化（20%）：啟動與查詢時間顯著改善
- 創新性（10%）：附加監控/自動化腳本
```

```markdown
## Case #2: Jekyll（GitHub Pages）本機開發編譯極慢與熱重載失效

### Problem Statement（問題陳述）
**業務場景**：以 Jekyll（GitHub Pages）在本機預覽部落格文章。希望邊寫邊看、支援自動重新編譯與瀏覽器自動刷新。

**技術挑戰**：原先在 Windows 路徑掛載到容器（/mnt/c），Jekyll 編譯一次需 110 秒，檔案變更偵測不到（退化為輪巡），更改一行字也要等近 2 分鐘。

**影響範圍**：迭代速度極慢、開發者體驗差、容易誤判內容呈現。

**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 透過 DrvFS 掛載 NTFS 路徑：跨層轉譯造成高延遲。
2. inotify 與 NTFS 的通知不相容：Jekyll 的檔案監看無法運作，轉為低效輪巡。
3. 容器內大量小檔案存取：4K 隨機 IO 更受影響。

**深層原因**：
- 架構層面：編譯（Linux）與檔案（NTFS）分離。
- 技術層面：FileSystemWatcher 與 inotify 機制差異。
- 流程層面：沿用「Windows 掛載資料夾進容器」的慣性。

### Solution Design（解決方案設計）
**解決策略**：將整個網站 repo 搬到 WSL EXT4（如 /opt/docker/columns.chicken-house.net），以 VSCode Remote - WSL 開啟；容器在 WSL 內啟動，volume 掛載 WSL 路徑，恢復 inotify 與高速 IO，達到秒級熱重載。

**實施步驟**：
1. 專案搬遷至 WSL EXT4
- 實作細節：git clone 至 /opt/docker/... 或直接搬移
- 所需資源：git、bash
- 預估時間：20 分鐘

2. VSCode Remote - WSL 開啟專案
- 實作細節：在 WSL 中執行 code . 安裝/啟動 vscode-server
- 所需資源：VSCode、WSL 擴充套件
- 預估時間：10 分鐘

3. 以 docker compose 啟動 Jekyll
- 實作細節：volume 指向 WSL 路徑；開啟 livereload/port-forward
- 所需資源：docker compose
- 預估時間：20 分鐘

**關鍵程式碼/設定**：
```yaml
# docker-compose.yml（Jekyll）
services:
  jekyll:
    image: jekyll/jekyll:latest
    command: jekyll serve --livereload --force_polling=false
    ports:
      - "4000:4000"
      - "35729:35729"
    volumes:
      - /opt/docker/columns.chicken-house.net:/srv/jekyll
    working_dir: /srv/jekyll
    restart: unless-stopped
```

```bash
# 在 WSL 目錄開啟 VSCode（會自動安裝/啟動 vscode-server）
cd /opt/docker/columns.chicken-house.net
code .
```

實際案例：部落格 Repo（Jekyll, GitHub Pages）
實作環境：Windows 11 + WSL2 Ubuntu 24.04 + Docker CE + VSCode Remote - WSL
實測數據：
- 改善前：單次 build 約 110 s、文件更新需 ~120 s 才可見
- 改善後：建置時間約為原本 1/18（約 6.1 s）、變更偵測即時
- 改善幅度：約 18 倍（建置），檔案變更延遲由分鐘級降至秒級

Learning Points（學習要點）
核心知識點：
- inotify 與 NTFS 事件不相容，Dev Loop 容易失效
- Remote - WSL 將工具鏈與 I/O 留在 Linux 端
- 小檔案大量讀寫對跨層 I/O 的放大效應

技能要求：
- 必備技能：docker-compose、Jekyll 基本操作
- 進階技能：VSCode Remote、WSL 檔案系統與 port-forward

延伸思考：
- 類似的前端開發（webpack/vite）亦深受檔案監控影響
- 若需從 Windows 側編輯，如何在不犧牲效能下共享？（建議僅瀏覽）

Practice Exercise（練習題）
- 基礎練習：以 Remote - WSL 模式開啟 repo 並成功熱重載（30 分）
- 進階練習：量測 force_polling=true/false 對 CPU 與延遲影響（2 小時）
- 專案練習：撰寫自動化腳本一鍵起/停 Jekyll 與瀏覽器（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：可編譯、可熱重載、可預覽
- 程式碼品質（30%）：compose 正確、設定清晰
- 效能優化（20%）：建置時間明顯下降
- 創新性（10%）：額外加入自動化或監控
```

```markdown
## Case #3: 建立可重現的 WSL 檔案系統 I/O 基準量測

### Problem Statement（問題陳述）
**業務場景**：需量化不同檔案路徑與 OS 邊界的存取性能，支援 DB/索引/編譯等場景的決策。希望同機測試四種通路並客觀比較。

**技術挑戰**：跨 Windows/WSL、跨檔案系統（NTFS/EXT4）、跨協定（9P/DrvFS/Hyper-V），參數需要一致可比較。

**影響範圍**：錯誤的資料放置策略導致 Dev/Prod 服務慢上數十倍。

**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 測試工具與參數不一：難以客觀比較。
2. I/O 引擎差異：Windows 與 Linux 須用對應引擎。
3. 未分辨通路的轉譯層：9P/DrvFS/Hyper-V 各自帶來延遲。

**深層原因**：
- 架構層面：不同檔案通路（Windows->Windows、WSL->WSL、Windows->WSL、WSL->Windows）存在多層轉譯。
- 技術層面：I/O 深度與隨機 4K 模式更能反映 DB 類情境。
- 流程層面：缺乏基準流程導致主觀判斷。

### Solution Design（解決方案設計）
**解決策略**：使用 fio 在 Windows/WSL 各自以相同參數測試 4 組情境（隨機 4K、numjobs=8、iodepth=64、direct=1、300s），建立可重現報表並以 Windows->Windows 作為 100% 基準。

**實施步驟**：
1. 安裝 fio（Windows/WSL）
- 實作細節：Windows 版與 Linux 版分別安裝
- 所需資源：官方套件
- 預估時間：20 分鐘

2. 定義一致參數與路徑
- 實作細節：--rw=randrw --bs=4k --numjobs=8 --iodepth=64 --direct=1 --runtime=300
- 所需資源：測試目錄與硬碟空間
- 預估時間：20 分鐘

3. 執行四組路徑量測
- 實作細節：切換不同資料夾（NTFS/EXT4/DrvFS/9P）
- 所需資源：同一顆 SSD
- 預估時間：1 小時

**關鍵程式碼/設定**：
```bash
# Windows -> Windows（NTFS，本機）
fio --name=benchmark --directory=c:\benchmark_temp --size=16G --rw=randrw --bs=4k \
    --numjobs=8 --iodepth=64 --ioengine=windowsaio --direct=1 --time_based --runtime=300

# WSL -> WSL（EXT4，rootfs）
fio --name=benchmark --directory=~/benchmark_temp --size=16G --rw=randrw --bs=4k \
    --numjobs=8 --iodepth=64 --ioengine=libaio --direct=1 --time_based --runtime=300

# Windows -> WSL（\\wsl$，9P）
fio --name=benchmark --directory=\\wsl$\ubuntu\home\andrew\benchmark_temp --size=16G --rw=randrw --bs=4k \
    --numjobs=8 --iodepth=64 --ioengine=windowsaio --direct=1 --time_based --runtime=300

# WSL -> Windows（/mnt/c，DrvFS）
fio --name=benchmark --directory=/mnt/c/benchmark_temp --size=16G --rw=randrw --bs=4k \
    --numjobs=8 --iodepth=64 --ioengine=libaio --direct=1 --time_based --runtime=300
```

實際案例：相同機器，同一 SSD，以 16GB、4K 隨機讀寫、8 jobs、iodepth=64 測試
實作環境：Windows 11 + WSL2 Ubuntu 24.04
實測數據（讀取 MiB/s）：
- Windows->Windows：576（100%）
- WSL->WSL：209（36.28%）
- Windows->WSL：16.5（2.86%）
- WSL->Windows：37.5（6.51%）

Learning Points（學習要點）
核心知識點：
- 4K 隨機 I/O 與 DB workload 關聯
- 9P/DrvFS/Hyper-V 層層轉譯的成本
- 以基準路徑（Windows->Windows）為 100% 作對照

技能要求：
- 必備技能：fio 參數運用、Windows/WSL 路徑辨識
- 進階技能：I/O 監控與結果解讀

延伸思考：
- 若改為順序讀寫或更大 block size，結果是否不同？
- 是否可藉由 dedicated disk/VHDX 提升 WSL->WSL 表現？

Practice Exercise（練習題）
- 基礎練習：重跑四組路徑，繪製柱狀圖（30 分）
- 進階練習：比較不同 iodepth 對結果的影響（2 小時）
- 專案練習：寫成一鍵基準量測腳本與報表輸出（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：四組路徑皆能正確量測
- 程式碼品質（30%）：參數一致、輸出可讀
- 效能優化（20%）：能提出有效配置建議
- 創新性（10%）：自動生成圖表/報告
```

```markdown
## Case #4: 將 WSL 使用專屬 SSD（EXT4）以獲取接近原生的 I/O 效能

### Problem Statement（問題陳述）
**業務場景**：長期以 WSL 為主要 Linux 開發/執行環境，需要 DB/索引/建置等高 I/O 任務的穩定與效能。

**技術挑戰**：WSL 預設 rootfs 位於 .vhdx，與 OS 共用磁碟、經 Hyper-V 虛擬層，效能僅 Windows->Windows 的約 36%。希望提升至接近原生。

**影響範圍**：各類高 I/O 容器/服務（DB、搜尋、建置）與開發流程。

**複雜度評級**：高

### Root Cause Analysis（根因分析）
**直接原因**：
1. .vhdx 虛擬化開銷：經 Hyper-V 發生性能折損。
2. 與 OS 共用同顆 SSD：背景干擾不可控。
3. NTFS 與 EXT4 差異：NTFS 開銷較高。

**深層原因**：
- 架構層面：WSL 預設將 rootfs 置於 Windows 使用中的系統磁碟。
- 技術層面：Hyper-V 虛擬磁碟、檔案系統差異（EXT4 vs NTFS）。
- 流程層面：未納入專屬磁碟規劃，導致雜訊與資源競爭。

### Solution Design（解決方案設計）
**解決策略**：配置專用實體 SSD，格式化為 EXT4，使用「wsl --mount」在 WSL 直接掛載實體分割區，將高 I/O 的資料與容器 volume 置於該分割區，避開 Hyper-V 與 OS 干擾。

**實施步驟**：
1. 安裝專屬 SSD 並分割
- 實作細節：以 Windows Disk Management 或 Linux parted 建立分割
- 所需資源：一顆 SSD（建議 TLC/MLC）
- 預估時間：0.5~1 小時

2. 以 wsl --mount 掛載實體分割區
- 實作細節：wsl --mount <PhysicalDriveX> --partition N --type ext4
- 所需資源：Windows 11 24H2 以上
- 預估時間：10 分鐘

3. 在 WSL 內格式化與掛載
- 實作細節：mkfs.ext4、建立掛載點、寫入 /etc/fstab
- 所需資源：root 權限
- 預估時間：30 分鐘

4. 調整容器 volume 與資料位置
- 實作細節：將 /opt/docker 移至新掛載點（如 /data/docker）
- 所需資源：docker compose
- 預估時間：30 分鐘

**關鍵程式碼/設定**：
```powershell
# 列出可掛載磁碟
wsl --list --verbose
# 掛載實體磁碟（舉例）
wsl --mount \\.\PHYSICALDRIVE2 --partition 1 --type ext4

# 於 WSL 內處理
sudo mkfs.ext4 /dev/sdc1
sudo mkdir -p /data
sudo mount /dev/sdc1 /data

# 永久掛載（WSL 內）
echo "/dev/sdc1 /data ext4 defaults 0 0" | sudo tee -a /etc/fstab
sudo mount -a
```

實際案例：Samsung 970Pro Gen3 MLC SSD
實作環境：Windows 11 24H2 + WSL2 + 專屬 SSD（EXT4）
實測數據（4K 隨機，8 jobs，iodepth=64）：
- Windows+NTFS：646 MB/s（100%）
- WSL+EXT4（實體直掛）：780 MB/s（120.74%）
- 改善幅度：相對 Windows 原生基準「超越」約 20.74%；相較預設 WSL .vhdx（~209 MB/s）則是約 3.7 倍+

Learning Points（學習要點）
核心知識點：
- 專屬 SSD、EXT4、實體直掛對 WSL 效能的顯著提升
- OS 干擾與 Hyper-V 虛擬化的效能代價
- NAND 顆粒類型對高負載隨機 I/O 的影響

技能要求：
- 必備技能：分割/格式化、fstab、WSL mount
- 進階技能：fio 基準測試與結果分析

延伸思考：
- 若採用 VHDX（EXT4 on NTFS）與實體直掛差距？
- 是否需要 LUKS 加密與其效能影響？

Practice Exercise（練習題）
- 基礎練習：建立 /data 掛載點並搬移 /opt/docker（30 分）
- 進階練習：比較 .vhdx vs 實體直掛 vs DrvFS（2 小時）
- 專案練習：撰寫 WSL 專屬磁碟建置與基準量測自動化（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：掛載穩定、開機自動掛載
- 程式碼品質（30%）：腳本化、可重複
- 效能優化（20%）：I/O 顯著提升
- 創新性（10%）：監控/告警/報表
```

```markdown
## Case #5: 以專屬 VHDX（EXT4）隔離 WSL I/O 干擾

### Problem Statement（問題陳述）
**業務場景**：不便新增實體 SSD，但仍希望提升 WSL I/O 效能並隔離與 OS 的互相干擾。

**技術挑戰**：WSL 預設 rootfs 與 OS 共用同顆磁碟，虛擬磁碟 I/O 受背景影響大，4K 隨機性能偏低。

**影響範圍**：DB/索引/建置等高 I/O 場景。

**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 預設 rootfs.vhdx 與 OS 共用同顆磁碟，I/O 雜訊大。
2. 虛擬磁碟存在 Hyper-V 層開銷。
3. NTFS 宿主檔案系統的行為影響虛擬磁碟效能。

**深層原因**：
- 架構層面：WSL rootfs 預設落在 OS 系統碟目錄。
- 技術層面：VHDX 受宿主（NTFS）表現與併發影響。
- 流程層面：未對 WSL 的儲存進行分區與隔離。

### Solution Design（解決方案設計）
**解決策略**：在 Windows 建立獨立 VHDX 映像檔，格式化為 EXT4 並以 wsl --mount --vhd 掛載給 WSL 使用；將容器資料與高 I/O 任務集中至該 VHDX，減少與 OS 互相干擾。

**實施步驟**：
1. 建立獨立 VHDX
- 實作細節：使用 diskpart 或 PowerShell 建立並附掛 VHDX 檔
- 所需資源：足夠的磁碟空間（建議不同於 C:）
- 預估時間：20 分鐘

2. 掛載 VHDX 至 WSL
- 實作細節：wsl --mount --vhd <path-to.vhdx>
- 所需資源：Windows 11 24H2 以上
- 預估時間：10 分鐘

3. WSL 內格式化與掛載
- 實作細節：mkfs.ext4、指定掛載點、寫入 fstab
- 所需資源：root 權限
- 預估時間：30 分鐘

4. 將資料與 volume 搬遷
- 實作細節：/opt/docker → /mnt/vhdx/docker（舉例）
- 所需資源：rsync
- 預估時間：30 分鐘

**關鍵程式碼/設定**：
```powershell
# 建立並掛載 VHDX（以 PowerShell 為例）
New-VHD -Path "D:\WSL\wsl-data.vhdx" -SizeBytes 500GB -Dynamic
Mount-VHD -Path "D:\WSL\wsl-data.vhdx"

# 將 VHDX 掛入 WSL
wsl --shutdown
wsl --mount --vhd "D:\WSL\wsl-data.vhdx"

# WSL 內操作
sudo mkfs.ext4 /dev/sdx1   # 依實際裝置
sudo mkdir -p /mnt/vhdx
sudo mount /dev/sdx1 /mnt/vhdx
echo "/dev/sdx1 /mnt/vhdx ext4 defaults 0 0" | sudo tee -a /etc/fstab
sudo mount -a
```

實際案例：在同顆 SSD 上以獨立 VHDX 減少雜訊
實作環境：Windows 11 24H2 + WSL2 + VHDX（EXT4）
實測數據（Crucial T500）：
- 舊：WSL rootfs.vhdx 共用系統碟，約 209 MB/s
- 新：獨立 VHDX，約 620 MB/s
- 改善幅度：約 3 倍

Learning Points（學習要點）
核心知識點：
- VHDX 隔離可顯著減少與 OS 互擾
- EXT4 on VHDX 的表現受宿主 NTFS 影響但可優化
- wsl --mount --vhd 的好處與限制

技能要求：
- 必備技能：Windows 磁碟管理、WSL 掛載
- 進階技能：I/O 量測與併發優化

延伸思考：
- 若 VHDX 存於非系統碟，效能是否更佳？
- 與實體直掛相比何時應選擇 VHDX？

Practice Exercise（練習題）
- 基礎練習：建立 50GB VHDX 並於 WSL 掛載（30 分）
- 進階練習：比較 rootfs.vhdx 與獨立 VHDX 4K randrw 差異（2 小時）
- 專案練習：封裝為自動化部署腳本與搬遷工具（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：VHDX 正確掛載與持久化
- 程式碼品質（30%）：腳本化、具備容錯
- 效能優化（20%）：I/O 明顯提升
- 創新性（10%）：自動化與報表
```

```markdown
## Case #6: DrvFS 下檔案監看與熱重載幾乎失效的修復

### Problem Statement（問題陳述）
**業務場景**：前端/靜態站點/後端開發，需依賴檔案監控（watch）與熱重載（live reload）提升迭代效率。

**技術挑戰**：將 Windows 目錄掛到容器（/mnt/c → 容器）時，監看事件無法透過 DrvFS 映射至 inotify，導致改動不被偵測或需高成本輪巡。

**影響範圍**：Dev Loop 嚴重退化，需手動重啟容器或等待長時間輪巡。

**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. NTFS 的 FileSystemWatcher 與 Linux inotify 機制不相容。
2. DrvFS/9P 無法高效轉譯檔案事件。
3. 掛載 Windows 目錄作為容器 volume 的慣性。

**深層原因**：
- 架構層面：檔案在 NTFS，工具鏈在 Linux。
- 技術層面：事件模型差異造成 watch 失效。
- 流程層面：便利性（Windows 路徑）與效能/功能（Linux watch）取捨未被辨識。

### Solution Design（解決方案設計）
**解決策略**：將源碼完全放置於 WSL EXT4，工具鏈（編譯/熱重載）在 WSL 或容器內執行；Windows 僅作瀏覽。必要時才退而求其次使用輪巡（但不建議）。

**實施步驟**：
1. 移動專案至 WSL EXT4
- 實作細節：git clone 至 /opt/docker/... 或移轉
- 所需資源：git
- 預估時間：20 分鐘

2. VSCode Remote - WSL 啟動開發
- 實作細節：code .，在 WSL 端啟動 watch
- 所需資源：VSCode
- 預估時間：10 分鐘

3. 正確設定容器 volume 與監視
- 實作細節：volume 指向 WSL 路徑，確保 inotify 可用
- 所需資源：docker compose
- 預估時間：20 分鐘

**關鍵程式碼/設定**：
```yaml
# Good: volume 指向 WSL EXT4
volumes:
  - /opt/docker/myapp:/workspace

# Bad: volume 指向 /mnt/c（DrvFS）
# - /mnt/c/Code/myapp:/workspace
```

實際案例：Jekyll/前端工具鏈
實作環境：Windows 11 + WSL2 + Docker
實測數據：
- 改善前：檔案變更偵測延遲分鐘級（甚至需手動重啟）
- 改善後：inotify 即時觸發，秒級熱重載
- 改善幅度：由手動/分鐘級 → 秒級（功能由不可用 → 可用）

Learning Points（學習要點）
核心知識點：
- inotify 與 FileSystemWatcher 差異
- DrvFS 的事件轉譯侷限
- Dev Loop 要求資料與工具鏈同在 Linux

技能要求：
- 必備技能：docker-compose、VSCode Remote
- 進階技能：診斷 watch/notify 問題（strace/inotifywait）

延伸思考：
- 在跨平台專案中如何定義「可用且高效」的開發流程？
- 何時可接受 polling 作為降級方案？

Practice Exercise（練習題）
- 基礎練習：以 inotifywait 驗證檔案變更事件（30 分）
- 進階練習：比較 polling/notify CPU 負載（2 小時）
- 專案練習：形成團隊「資料安置與 hot reload 指南」（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：watch 可用且穩定
- 程式碼品質（30%）：compose/腳本清晰
- 效能優化（20%）：延遲明顯降低
- 創新性（10%）：監控與可視化
```

```markdown
## Case #7: 把 DrvFS 當「網路磁碟」使用的邊界與規範

### Problem Statement（問題陳述）
**業務場景**：團隊希望在 Windows 檔案總管中瀏覽/備份 WSL 內檔案，但避免影響 Linux 端執行效能。

**技術挑戰**：DrvFS/9P 通路在高 I/O 下表現極差；如何制定規範避免誤用（如把 DB/索引資料指向 /mnt/c）。

**影響範圍**：任意重 I/O 工作若錯用 DrvFS 會降至僅 6%~42% 的相對效能（依 SSD 而異）。

**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 9P 協定與 DrvFS 的設計初衷非重 I/O。
2. 事件/權限模型難以映射，兼容性差。
3. 對「方便」的過度偏好造成誤用。

**深層原因**：
- 架構層面：跨 Kernel 路徑天生高延遲。
- 技術層面：不同檔案系統與協定棧的折損。
- 流程層面：缺乏明確使用準則。

### Solution Design（解決方案設計）
**解決策略**：制訂「DrvFS 使用準則」：僅供輕度瀏覽/搬運，嚴禁 DB/索引/建置/編譯等重 I/O 使用；所有重 I/O 皆必須放在 WSL EXT4；必要時用 mklink 暴露入口以提升體驗。

**實施步驟**：
1. 制訂與公告準則
- 實作細節：文件化並納入 PR 檢查/Code Review 清單
- 所需資源：團隊文件平台
- 預估時間：1 小時

2. 建立 WSL 標準資料根目錄
- 實作細節：/opt/docker、/data 等
- 所需資源：WSL
- 預估時間：30 分

3. 提供 Windows 入口（僅瀏覽）
- 實作細節：mklink /d
- 所需資源：Windows
- 預估時間：10 分

**關鍵程式碼/設定**：
```bat
:: 僅提供入口，不做重 I/O
mklink /d C:\CodeWork\docker \\wsl$\Ubuntu\opt\docker
```

實際案例：綜合 fio 測試
實作環境：多顆 SSD、相同 fio 參數
實測數據（相對 Windows 原生）：
- WSL→Windows（DrvFS）：6.51%（T500）、5.71%（970Pro）、42.38%（NV1）、34.8%（Intel 730）
- 指南結論：把 DrvFS 視為「網路磁碟」只做瀏覽/搬運

Learning Points（學習要點）
核心知識點：
- DrvFS 適用場景與邊界
- 制度化規範比個人經驗更能避免踩雷
- 相對效能的思維方式

技能要求：
- 必備技能：WSL/Windows 基本操作
- 進階技能：團隊規範設計與落地

延伸思考：
- 是否需要權限限制避免誤用（如 CI 禁止 /mnt/c volume）？
- 能否在 compose lint 階段攔截錯誤掛載？

Practice Exercise（練習題）
- 基礎練習：在團隊 README 增補 DrvFS 使用守則（30 分）
- 進階練習：寫一個 compose 檢查腳本攔截 /mnt/c 掛載（2 小時）
- 專案練習：導入 pre-commit hook 實施（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：規範完整、可執行
- 程式碼品質（30%）：檢查腳本穩定
- 效能優化（20%）：踩雷案件數下降
- 創新性（10%）：自動化與告警
```

```markdown
## Case #8: 在 WSL 啟用 GPU（CUDA）運算能力

### Problem Statement（問題陳述）
**業務場景**：在本機運行 LLM/ML 推論（如 Ollama），需要使用 NVIDIA GPU 加速以獲得可用的回應速度。

**技術挑戰**：Windows 與 Linux CUDA 堆疊複雜、容易版本相依錯誤；期望在 WSL 中直接使用 GPU 而不需安裝 Linux 版驅動。

**影響範圍**：所有需要 GPU 的容器與工具鏈。

**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 傳統做法要求 Linux 端安裝 GPU Driver 與 CUDA，維運成本高。
2. Windows/WSL 的 GPU 虛擬化與堆疊差異難以理解。
3. 容器內需額外設定 runtimes 才能取得 GPU。

**深層原因**：
- 架構層面：WSL 透過 /dev/dxg 與虛擬化堆疊暴露 GPU 能力。
- 技術層面：Host（Windows）Driver 為關鍵，WSL 不需安裝 Linux Driver。
- 流程層面：需正確安裝與驗證工具鏈（nvidia-smi）。

### Solution Design（解決方案設計）
**解決策略**：在 Windows 安裝最新 NVIDIA 顯示卡驅動；WSL 內不安裝 Linux 驅動，直接驗證 nvidia-smi 可以看到 GPU；後續再裝 NVIDIA Container Toolkit 供 Docker 使用。

**實施步驟**：
1. 安裝/更新 Windows NVIDIA Driver
- 實作細節：WDDM 版本需符合支援（如 2.9+）
- 所需資源：NVIDIA 官方驅動
- 預估時間：10-20 分鐘

2. 在 WSL 驗證 GPU 可見
- 實作細節：執行 nvidia-smi
- 所需資源：WSL
- 預估時間：5 分鐘

3. 準備容器使用（交由 Case #9）
- 實作細節：安裝 NVIDIA Container Toolkit
- 所需資源：apt repo
- 預估時間：-（見下一案例）

**關鍵程式碼/設定**：
```bash
# WSL 內檢查 GPU 是否可見
nvidia-smi
# 預期可看到顯卡、Driver 與 CUDA 版本
```

實際案例：RTX 4060Ti 16GB
實作環境：Windows 11 24H2 + WSL2 Ubuntu 24.04
實測數據：
- 驗證輸出：nvidia-smi 正常列出 GPU 與 Driver/CUDA 版本，/Xwayland 占用可見
- 效益：WSL 端無需安裝 Linux GPU Driver，降低相依與風險

Learning Points（學習要點）
核心知識點：
- WSL GPU 虛擬化原理（/dev/dxg）
- Host Driver 是關鍵，Guest 無需安裝 Linux Driver
- 驗證工具鏈（nvidia-smi）的定位

技能要求：
- 必備技能：Windows Driver 安裝與版本判讀
- 進階技能：WSL 與 GPU 虛擬化堆疊理解

延伸思考：
- 多 GPU 與 MIG 情境如何在 WSL 呈現？
- GPU 資源配額與隔離策略？

Practice Exercise（練習題）
- 基礎練習：在 WSL 執行 nvidia-smi 並截圖（30 分）
- 進階練習：嘗試 OpenCL/CUDA 範例程式跑通（2 小時）
- 專案練習：撰寫 GPU 驗證自動化腳本（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：nvidia-smi 顯示正確
- 程式碼品質（30%）：驗證腳本清楚
- 效能優化（20%）：可跑基本 GPU 程式
- 創新性（10%）：診斷報表/兼容性檢查
```

```markdown
## Case #9: 讓 Docker 容器在 WSL 中使用 GPU（NVIDIA Container Toolkit）

### Problem Statement（問題陳述）
**業務場景**：希望容器中的 LLM/ML 推論（如 Ollama）可使用 GPU 加速。

**技術挑戰**：WSL 雖可見 GPU，但容器需要正確 runtime 與工具鏈設定才能取得 GPU。

**影響範圍**：所有 GPU 需求容器。

**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. Docker 預設 runtime 不包含 NVIDIA。
2. 未安裝 NVIDIA Container Toolkit 無法暴露 GPU。
3. /etc/docker/daemon.json 未設定預設 runtime。

**深層原因**：
- 架構層面：容器 runtime 與 Host GPU 能力對接的標準流程。
- 技術層面：nvidia-ctk 需正確安裝與設定。
- 流程層面：缺少驗證步驟導致容器內看不到 GPU。

### Solution Design（解決方案設計）
**解決策略**：在 WSL 安裝 NVIDIA Container Toolkit，使用 nvidia-ctk 設定 Docker runtime（nvidia），重啟 Docker；並以測試容器驗證 GPU 可用。

**實施步驟**：
1. 安裝 NVIDIA Container Toolkit
- 實作細節：加入 repo、apt 安裝
- 所需資源：官方文件
- 預估時間：20 分鐘

2. 設定 Docker 預設 runtime
- 實作細節：nvidia-ctk runtime configure，檢查 /etc/docker/daemon.json
- 所需資源：root 權限
- 預估時間：10 分鐘

3. 驗證容器內 GPU 可見
- 實作細節：docker run --gpus all nvidia/cuda:... nvidia-smi
- 所需資源：docker
- 預估時間：10 分鐘

**關鍵程式碼/設定**：
```bash
# Install NVIDIA Container Toolkit（WSL 內）
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -fsSL https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list \
  | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# 設定 Docker runtime
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# 驗證
docker run --rm --gpus all nvidia/cuda:12.3.1-base-ubuntu22.04 nvidia-smi
```

實際案例：WSL + Docker CE + NVIDIA Toolkit
實作環境：Windows 11 24H2 + WSL2 Ubuntu 24.04
實測數據：
- 成效：容器內可正確列出 GPU（nvidia-smi）
- 指標：部署成功率一次到位、容器能加速推論

Learning Points（學習要點）
核心知識點：
- nvidia-ctk 與 Docker runtime 的對接
- 驗證容器 GPU 可用性的標準方式
- Host 驅動與容器 runtime 的邏輯關係

技能要求：
- 必備技能：Docker、apt 套件管理
- 進階技能：容器 runtime 設定與除錯

延伸思考：
- 多 GPU/MIG 配置如何在容器中分配？
- K8s（WSL 上）與 GPU 的整合？

Practice Exercise（練習題）
- 基礎練習：跑 nvidia/cuda 基礎映像測試 nvidia-smi（30 分）
- 進階練習：寫 Dockerfile 執行簡單 CUDA 程式（2 小時）
- 專案練習：以 docker-compose 部署 GPU 推論服務（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：容器可見 GPU
- 程式碼品質（30%）：設定文件清楚
- 效能優化（20%）：推論速度明顯改善
- 創新性（10%）：加入監控與告警
```

```markdown
## Case #10: 以 Docker 啟動 Ollama 並使用 GPU 加速

### Problem Statement（問題陳述）
**業務場景**：在本機以容器啟動 Ollama 並使用 GPU，加速 LLM 推論；並搭配 Web UI（Open WebUI）作為使用介面。

**技術挑戰**：確保容器能取得 GPU；設定 volume 保留模型；連通管理。

**影響範圍**：本地 LLM 開發與原型驗證。

**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 未指定 --gpus，容器看不到 GPU。
2. 未設置模型快取 volume，頻繁重拉模型。
3. 端口未配置導致 Web 無法訪問。

**深層原因**：
- 架構層面：推論服務需 GPU 資源與持久化模型目錄。
- 技術層面：docker run 參數到位、port/volume 正確。
- 流程層面：啟停與驗證缺乏標準流程。

### Solution Design（解決方案設計）
**解決策略**：以 docker run 或 docker-compose 啟動 ollama/ollama，設置 --gpus=all、映射模型 volume 與 11434 端口；可再搭配 Open WebUI 提供介面。

**實施步驟**：
1. 啟動 Ollama 容器
- 實作細節：--gpus=all、volume 維持模型、port 11434
- 所需資源：NVIDIA ToolKit、Docker
- 預估時間：5 分鐘

2. 驗證推論速度與 GPU 使用
- 實作細節：拉取 llama3.2（或其他）並提問
- 所需資源：CLI 或 Open WebUI
- 預估時間：10 分鐘

3. （可選）加入 Open WebUI
- 實作細節：docker-compose 定義兩個服務互通
- 所需資源：compose
- 預估時間：20 分鐘

**關鍵程式碼/設定**：
```bash
# 單服務啟動（Ollama）
docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

```yaml
# docker-compose（Ollama + Open WebUI 範例）
services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    runtime: nvidia
    environment:
      - OLLAMA_KEEP_ALIVE=24h
    volumes:
      - ollama-data:/root/.ollama
    ports:
      - "11434:11434"

  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    ports:
      - "3000:8080"
    environment:
      - OLLAMA_API_BASE=http://ollama:11434
    depends_on:
      - ollama

volumes:
  ollama-data:
```

實際案例：Ollama + Open WebUI
實作環境：Windows 11 + WSL2 + Docker + NVIDIA Toolkit
實測數據：
- 效益：問答回應約 1 秒出現、Task Manager 顯示 GPU 負載
- 開箱即用：以 compose up -d 一次建立完整環境

Learning Points（學習要點）
核心知識點：
- 容器 GPU 啟用與 Volume 持久化
- 推論 API 與 UI 的服務組合
- 端口轉發與安全性

技能要求：
- 必備技能：docker run/compose
- 進階技能：監控 GPU 使用、模型管理

延伸思考：
- 多模型/多使用者配額如何規劃？
- 以 Nginx/TLS 加固公開訪問？

Practice Exercise（練習題）
- 基礎練習：啟動 Ollama 並測試一個模型（30 分）
- 進階練習：加入 Open WebUI 與使用者管理（2 小時）
- 專案練習：建立一套企業內部 LLM 原型環境（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：GPU 可用、模型可推論
- 程式碼品質（30%）：compose 清晰、變數化
- 效能優化（20%）：回應時間可量化
- 創新性（10%）：監控/告警/自動伸縮構想
```

```markdown
## Case #11: 使用 VSCode Remote - WSL 取得「近本地」的開發體驗

### Problem Statement（問題陳述）
**業務場景**：在 Windows 主機開發 Linux 目標應用，需使用 Linux 工具鏈與原生檔案系統；同時保有 Windows 上的 UI/快捷體驗。

**技術挑戰**：直接在 Windows 執行 VSCode 編譯 Linux 專案易遇路徑與 I/O 問題；需將 IDE 前後端分離，讓所有重活在 WSL。

**影響範圍**：所有開發流程（編輯、建置、除錯、預覽）。

**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. VSCode 在 Windows 執行時，工具鏈與檔案操作在 Windows 端。
2. 透過 \\wsl$ 編輯導致 I/O 慢與監看失效。
3. 缺乏一致的遠端執行端（server）。

**深層原因**：
- 架構層面：IDE UI 與工具鏈需分離。
- 技術層面：vscode-server 在 WSL 執行，UI 在 Windows。
- 流程層面：未採用 code . 啟動遠端模式。

### Solution Design（解決方案設計）
**解決策略**：安裝 VSCode Remote - WSL 擴充，在 WSL 目錄內以 code . 開啟專案；vscode-server 負責所有 Linux 端操作（檔案/terminal/debug），Windows 端僅顯示 UI。

**實施步驟**：
1. 安裝 VSCode 與 Remote - WSL
- 實作細節：Marketplace 安裝擴充
- 所需資源：VSCode
- 預估時間：10 分鐘

2. 在 WSL 目錄以 code . 啟動
- 實作細節：自動安裝/啟動 vscode-server
- 所需資源：WSL
- 預估時間：5 分鐘

3. 驗證遠端環境
- 實作細節：左下顯示 WSL - Ubuntu、Terminal 為 bash、Port Forward 可用
- 所需資源：—
- 預估時間：5 分鐘

**關鍵程式碼/設定**：
```bash
# 在 WSL 目錄內
git clone <repo>
cd <repo>
code .
# VSCode 左下角應顯示：WSL - Ubuntu
# Terminal（Ctrl+`）為 bash，且可直接跑 Linux/容器工具鏈
```

實際案例：Jekyll/Qdrant 等專案透過 Remote - WSL 開發
實作環境：Windows 11 + WSL2 + VSCode
實測數據：
- 效益：所有 I/O 與監看在 Linux 端執行，配合 Case #2 的 18 倍提速效果
- 使用者體感：近本地體驗、端口轉發可直接預覽

Learning Points（學習要點）
核心知識點：
- vscode-server 架構與資源邊界
- code . 的工作機制（啟動/更新 server）
- 遠端 Terminal 與 Port Forward 使用

技能要求：
- 必備技能：VSCode、WSL 基礎
- 進階技能：遠端除錯、端口/代理設定

延伸思考：
- 是否可以改用 DevContainer/K8s 作為遠端？
- CI 環境如何模擬一致工具鏈？

Practice Exercise（練習題）
- 基礎練習：在 WSL 內使用 code . 開啟並執行簡單測試（30 分）
- 進階練習：於 VSCode 內轉發容器端口並預覽（2 小時）
- 專案練習：建立團隊 Remote - WSL 上手指南（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：可正常遠端開發/除錯
- 程式碼品質（30%）：設定檔與說明清楚
- 效能優化（20%）：編譯/預覽延遲降低
- 創新性（10%）：流程自動化（tasks/launch）
```

```markdown
## Case #12: 以 explorer.exe/cmd.exe 在 WSL 與 Windows 間無縫協作

### Problem Statement（問題陳述）
**業務場景**：在 WSL 開發時需要偶爾呼叫 Windows 工具（檔案總管、cmd、PowerShell）進行瀏覽、管理或輔助操作。

**技術挑戰**：跨 OS 啟動不同執行檔的體驗與路徑問題。

**影響範圍**：日常開發操控效率、快速定位目錄、檔案操作便利性。

**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 開發者不知道 WSL 已註冊 PE 格式（binfmt_misc）可直接呼叫 .exe。
2. 不熟悉 explorer.exe . 直接開啟當前 WSL 路徑。

**深層原因**：
- 架構層面：WSL Interop 透過 binfmt_misc 對應 .exe。
- 技術層面：/proc/sys/fs/binfmt_misc/WSLInterop 設定。
- 流程層面：未建立跨 OS 工具的順手工作法。

### Solution Design（解決方案設計）
**解決策略**：在 WSL 直接呼叫 explorer.exe . 開啟當前目錄、cmd.exe /c 執行 Windows 命令，並熟悉相關限制（如 UNC path 提示）。

**實施步驟**：
1. 基本操作
- 實作細節：explorer.exe .；cmd.exe /c
- 所需資源：WSL
- 預估時間：10 分鐘

2. 理解 Interop 機制
- 實作細節：查看 /proc/sys/fs/binfmt_misc/WSLInterop
- 所需資源：—
- 預估時間：10 分鐘

3. 建立常用 alias（可選）
- 實作細節：.bashrc 中 alias e="explorer.exe ."
- 所需資源：bash
- 預估時間：5 分鐘

**關鍵程式碼/設定**：
```bash
# 直接於 WSL 呼叫 Windows App
explorer.exe .
cmd.exe /c dir

# 查看 Interop
cat /proc/sys/fs/binfmt_misc/WSLInterop
```

實際案例：從 WSL 直接開啟檔案總管定位 \\wsl.localhost\Ubuntu\...
實作環境：Windows 11 + WSL2
實測數據：
- 效益：顯著降低路徑切換成本與心智負擔（步驟數顯著下降）
- 相容性：UNC 路徑提示可忽略

Learning Points（學習要點）
核心知識點：
- WSL Interop/binfmt_misc 的運作
- explorer.exe 與路徑映射
- Windows/Linux 指令互補

技能要求：
- 必備技能：bash 基礎
- 進階技能：批次/PowerShell 混合流程

延伸思考：
- 是否可將此模式加入自動化（tasks.json）？
- 權限/安全邊界（防止誤操作）

Practice Exercise（練習題）
- 基礎練習：WSL 內一鍵開啟當前路徑於檔案總管（30 分）
- 進階練習：批次產生 Windows 快捷操作對多專案生效（2 小時）
- 專案練習：建立個人化跨 OS 開發快捷工具箱（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：指令可用、互通順暢
- 程式碼品質（30%）：alias/腳本清潔
- 效能優化（20%）：操作步驟顯著減少
- 創新性（10%）：快捷工具設計
```

```markdown
## Case #13: 以 mklink 暴露 WSL 目錄給 Windows 端（僅瀏覽）

### Problem Statement（問題陳述）
**業務場景**：資料與容器 volume 置於 WSL EXT4 以獲取效能，但仍希望在 Windows 檔案總管/VSCode（Windows 側）快速瀏覽或查閱。

**技術挑戰**：\\wsl$ 路徑每次手動輸入不便；需在 Windows 側以熟悉的路徑存取（但不做重 I/O）。

**影響範圍**：日常操作效率、誤用風險控制。

**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 缺少方便入口導致來回切換成本高。
2. 易誤將重 I/O 操作在 DrvFS 上執行。

**深層原因**：
- 架構層面：資料放在 WSL，UI/瀏覽在 Windows。
- 技術層面：mklink 可導引至 \\wsl$。
- 流程層面：需要邊界提醒。

### Solution Design（解決方案設計）
**解決策略**：以 mklink /d 建立 Windows 資料夾捷徑映射至 WSL 路徑，作為只讀/輕操作入口；重 I/O 一律在 WSL 內執行。

**實施步驟**：
1. 建立捷徑
- 實作細節：mklink /d C:\CodeWork\docker \\wsl$\Ubuntu\opt\docker
- 所需資源：cmd 管理員
- 預估時間：5 分鐘

2. 團隊告示
- 實作細節：註明「此捷徑僅瀏覽用」
- 所需資源：README/Wiki
- 預估時間：10 分鐘

**關鍵程式碼/設定**：
```bat
mklink /d C:\CodeWork\docker \\wsl$\Ubuntu\opt\docker
```

實際案例：日常瀏覽 WSL Volume 與專案
實作環境：Windows 11 + WSL2
實測數據：
- 效益：以熟悉的 C:\ 路徑快速進入 WSL 目錄
- 風險控制：重 I/O 仍在 WSL 端進行，維持 Qdrant/Jekyll 之 25x/18x 提升

Learning Points（學習要點）
核心知識點：
- mklink 與 \\wsl$ 入口整合
- 操作便利與效能安全邊界
- 文件化降風險

技能要求：
- 必備技能：cmd/mklink
- 進階技能：團隊規範

延伸思考：
- 是否以 GPO/腳本集中發放捷徑？
- 加上只讀標示或檢查機制？

Practice Exercise（練習題）
- 基礎練習：為 /opt/docker 建立 Windows 入口（30 分）
- 進階練習：以 PowerShell 批次建立多專案捷徑（2 小時）
- 專案練習：撰寫「只讀入口」規範與教育素材（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：捷徑可用
- 程式碼品質（30%）：腳本簡潔
- 效能優化（20%）：重 I/O 未誤用 DrvFS
- 創新性（10%）：使用者體驗提升設計
```

```markdown
## Case #14: WSL 專屬儲存的 SSD/NAND 顆粒選型指引（MLC/TLC/QLC）

### Problem Statement（問題陳述）
**業務場景**：為 WSL（DB/索引/建置）挑選專屬 SSD，期望在高隨機 I/O 下表現穩定。

**技術挑戰**：市場多為 QLC/TLC，MLC 稀有昂貴；不同 NAND/控制器影響大。

**影響範圍**：成本/效能/壽命。

**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. QLC 在高隨機 I/O（4K randrw）表現差。
2. 控制器/DRAMless 設計導致低負載也差。
3. 使用者僅看順序吞吐易誤判。

**深層原因**：
- 架構層面：工作負載特性與硬體選型不匹配。
- 技術層面：隨機 I/O 與快取/顆粒/控制器強相關。
- 流程層面：缺少以 fio 量測的採購流程。

### Solution Design（解決方案設計）
**解決策略**：以 fio 4K randrw（numjobs=8、iodepth=64、direct=1）比對不同 SSD；優先 MLC/TLC（高階）而非 QLC；將 WSL Volume 放在最佳盤。

**實施步驟**：
1. 準備測試清單
- 實作細節：採購前列出候選 SSD
- 所需資源：規格表
- 預估時間：1 小時

2. fio 量測（同參數）
- 實作細節：Windows/WSL 分別量測
- 所需資源：fio
- 預估時間：2 小時

3. 決策與部署
- 實作細節：選擇 MLC/TLC，避開 QLC/DRAMless
- 所需資源：—
- 預估時間：1 小時

**關鍵程式碼/設定**：
```bash
# 參考 Case #3 的 fio 參數，重點為 4K randrw、高 iodepth
```

實際案例：四顆 SSD 測試（摘錄）
實作環境：同機、同參數
實測數據（WSL+EXT4 直掛 vs Windows 基準）：
- Samsung 970Pro（MLC）：780 MB/s（120.74% 相對 Windows）
- Kingston NV1（QLC）：49.6 MB/s（66.94% 相對 Windows）
- Intel 730（MLC, SATA）：99 MB/s（99% 相對 Windows）
結論：QLC 在目標工作負載表現顯著不佳

Learning Points（學習要點）
核心知識點：
- 隨機 I/O 與 NAND 顆粒/控制器關聯
- 以數據導向選型
- Windows vs WSL 的相對效率觀察

技能要求：
- 必備技能：fio 測試
- 進階技能：硬體選型與成本分析

延伸思考：
- 小容量 vs 大容量的影響？
- 韌體/對齊/超額預留如何影響表現？

Practice Exercise（練習題）
- 基礎練習：比較兩顆 SSD 的 4K randrw（30 分）
- 進階練習：加上 queue depth 曲線對比（2 小時）
- 專案練習：形成採購指南模板（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：完成測試與報告
- 程式碼品質（30%）：測試腳本標準化
- 效能優化（20%）：正確解讀數據
- 創新性（10%）：圖表/儀表板
```

```markdown
## Case #15: 以架構方式避免「跨 Kernel」I/O：容器資料安置準則

### Problem Statement（問題陳述）
**業務場景**：團隊常見 DB/索引/建置等容器化工作負載，需制定一條通用資料安置準則，避免跨 Kernel I/O。

**技術挑戰**：不同專案/人員習慣不同，常直接掛 /mnt/c 導致嚴重效能問題。

**影響範圍**：所有容器化專案的效能與穩定性。

**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 缺乏通用準則導致錯誤掛載。
2. 對 WSL 檔案通路理解不足。

**深層原因**：
- 架構層面：資料與計算跨 OS Kernel。
- 技術層面：9P/DrvFS/Hyper-V 層層損耗。
- 流程層面：未將準則內建於模板/腳手架。

### Solution Design（解決方案設計）
**解決策略**：制定模板與 Lint 規則，規定：
- 重 I/O volume 一律掛 WSL EXT4（/opt/docker 或 /data）
- 禁用 /mnt/c 作為 volume
- Windows 僅作瀏覽（mklink）

**實施步驟**：
1. 範本化 compose
- 實作細節：提供標準 volume path 與變數
- 所需資源：repo 模板
- 預估時間：1 小時

2. 加入 Lint/CI 檢查
- 實作細節：發現 /mnt/c 掛載即 Fail
- 所需資源：pre-commit/CI
- 預估時間：2 小時

3. 教育與宣導
- 實作細節：文件/讀我
- 所需資源：—
- 預估時間：1 小時

**關鍵程式碼/設定**：
```yaml
# 標準化 volume（變數化路徑）
volumes:
  - ${WSL_DATA_ROOT:-/opt/docker}/mydb:/var/lib/mydb
```

實際案例：Qdrant/Jekyll 專案標準化
實作環境：Windows 11 + WSL2 + Docker
實測數據：
- 指標：跨專案一體化，避免 25x/18x 效能損失再發生
- 效益：新專案「開箱即對」

Learning Points（學習要點）
核心知識點：
- 架構先行：以規範避免錯誤
- 模板與 Lint 的落地手段
- WSL 資料根目錄標準化

技能要求：
- 必備技能：compose、CI
- 進階技能：政策落地與變更管理

延伸思考：
- 是否需要集中式儲存（NFS/SMB）？相容性與效能？
- 對 CI Runner（Linux 原生）之策略？

Practice Exercise（練習題）
- 基礎練習：將現有專案改用 WSL 標準 volume（30 分）
- 進階練習：寫一個 Lint 腳本攔截 /mnt/c 掛載（2 小時）
- 專案練習：建立公司級腳手架專案模板（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：模板可用
- 程式碼品質（30%）：Lint 規則穩定
- 效能優化（20%）：避免踩雷帶來的性能損失
- 創新性（10%）：自動化程度
```

```markdown
## Case #16: 用一條指令開發：code . 自動安裝/啟動 vscode-server

### Problem Statement（問題陳述）
**業務場景**：希望以最小心智負擔進入 WSL 遠端開發模式，不必手動配置 server 或路徑。

**技術挑戰**：開發者不熟悉 vscode-server 的啟動/更新流程。

**影響範圍**：入門門檻、團隊一致性。

**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 不知道 code 其實是 shell script，會自動安裝/更新/啟動 vscode-server。
2. 不熟悉從 WSL 啟動 VSCode 的正確姿勢。

**深層原因**：
- 架構層面：VSCode 前後端分離。
- 技術層面：code 腳本負責 server lifecycle。
- 流程層面：習慣從 Windows 直接開啟檔案夾。

### Solution Design（解決方案設計）
**解決策略**：養成從 WSL 目錄執行 code . 的習慣，確保工作區、工具鏈、I/O 都在 Linux 端；Windows 僅顯示 UI。

**實施步驟**：
1. 在專案根目錄執行 code .
- 實作細節：code 會安裝/啟動 server
- 所需資源：VSCode、WSL
- 預估時間：5 分鐘

2. 驗證指標
- 實作細節：左下角顯示 WSL - Ubuntu、Terminal=Bash
- 所需資源：—
- 預估時間：5 分鐘

**關鍵程式碼/設定**：
```bash
cd /opt/docker/myrepo
code .
# 注意：左下角顯示 WSL - Ubuntu，Terminal 為 bash
```

實際案例：部落格 repo、Qdrant 管理工具
實作環境：Windows 11 + WSL2 + VSCode
實測數據：
- 效益：「零設定」切入遠端模式，降低新手上手時間
- 與 Case #2：疊加帶來 18x 的建置提升

Learning Points（學習要點）
核心知識點：
- code 腳本職責與 vscode-server lifecycle
- 遠端工作區與本地 UI 的邏輯

技能要求：
- 必備技能：VSCode/WSL 基本操作
- 進階技能：VSCode 啟動疑難排解

延伸思考：
- DevContainer/SSH/Tunnel 其他模式如何同理？
- 整合 tasks/launch，形成一鍵開發

Practice Exercise（練習題）
- 基礎練習：用 code . 開啟三個不同專案（30 分）
- 進階練習：加入 tasks 執行 docker compose（2 小時）
- 專案練習：團隊模板含 VSCode 設定（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：遠端模式可用
- 程式碼品質（30%）：VSCode 設定清晰
- 效能優化（20%）：啟動時間與流程簡化
- 創新性（10%）：一鍵工作區腳本
```

```markdown
## Case #17: 使用 VSCode Port Forwarding 預覽容器服務

### Problem Statement（問題陳述）
**業務場景**：在 WSL/容器內啟動 Web 服務（Jekyll、LLM UI），希望在 Windows 瀏覽器直接預覽，並能於 VSCode 內部預覽。

**技術挑戰**：WSL 與容器內的端口需映射與轉發，並在 IDE 中可見。

**影響範圍**：前後端開發的體驗與效率。

**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 不熟悉 VSCode Remote 的 Port 面板與自動偵測。
2. Docker/WSL 端口對應關係不清。

**深層原因**：
- 架構層面：多層網路命名空間。
- 技術層面：VSCode 透過 server/tunnel 轉發端口。
- 流程層面：缺乏「內外一致」的端口規劃。

### Solution Design（解決方案設計）
**解決策略**：在 compose 中固定端口，啟動後於 VSCode Port 面板觀察並一鍵在瀏覽器或內嵌視窗開啟；對於多服務（Ollama + Open WebUI）一致化端口。

**實施步驟**：
1. 固定容器端口並映射
- 實作細節：compose ports: "3000:8080" 等
- 所需資源：docker compose
- 預估時間：10 分鐘

2. 使用 VSCode Port 面板
- 實作細節：開啟 UI 列出 Port，點選預覽
- 所需資源：VSCode
- 預估時間：5 分鐘

3. （可選）內嵌預覽
- 實作細節：在 VSCode 內開啟內嵌瀏覽器
- 所需資源：—
- 預估時間：5 分鐘

**關鍵程式碼/設定**：
```yaml
# 端口固定的 compose 片段
services:
  web:
    image: myweb
    ports:
      - "4000:4000"   # Jekyll
      - "35729:35729" # livereload
```

實際案例：Jekyll 預覽、Open WebUI（3000）
實作環境：Windows 11 + WSL2 + VSCode
實測數據：
- 效益：一鍵在 Windows 瀏覽器或 VSCode 內嵌視窗預覽
- 指標：端口清單可視化、零心智負擔

Learning Points（學習要點）
核心知識點：
- 端口映射與 VSCode Port 面板
- 一致化端口規劃策略
- IDE 內外預覽轉換

技能要求：
- 必備技能：compose 基礎
- 進階技能：VSCode Remote 端口管理

延伸思考：
- 公網暴露需加強安全（auth/TLS）
- 多服務端口規劃模板化

Practice Exercise（練習題）
- 基礎練習：列表/預覽容器端口（30 分）
- 進階練習：將多服務端口統一化（2 小時）
- 專案練習：建立內嵌預覽工作流（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：端口可視化與預覽
- 程式碼品質（30%）：映射清晰
- 效能優化（20%）：預覽迭代迅速
- 創新性（10%）：一鍵開啟所有服務
```

```markdown
## Case #18: 在 Windows 上原生跑 Linux GUI 應用（WSLg）

### Problem Statement（問題陳述）
**業務場景**：在 WSL 中運行需要 GUI 的 Linux 工具，仍希望在 Windows 桌面上原生顯示、與其他應用無縫整合。

**技術挑戰**：傳統需 X11 server/Wayland 配置，跨系統整合不易。

**影響範圍**：視覺化工具、IDE、分析器等。

**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. WSLg 提供對 X11/Wayland 的整合，但開發者不了解。
2. 不清楚如何啟動與權限設定。

**深層原因**：
- 架構層面：WSLg 將 Linux GUI 應用顯示於 Windows 桌面。
- 技術層面：剪貼簿、視窗管理互通。
- 流程層面：未納入 GUI 工具於 WSL 的開發流程。

### Solution Design（解決方案設計）
**解決策略**：直接於 WSL 安裝需要 GUI 的應用並啟動，Windows 端可於開始選單/工作列整合，支援 Alt+Tab 切換與剪貼簿共享。

**實施步驟**：
1. 安裝 GUI 應用
- 實作細節：apt 安裝（如 gedit）
- 所需資源：WSL
- 預估時間：10 分鐘

2. 啟動應用
- 實作細節：直接在 WSL 執行 gedit 等
- 所需資源：—
- 預估時間：5 分鐘

3. 驗證整合
- 實作細節：檢查開始選單、任務列、Alt+Tab
- 所需資源：Windows
- 預估時間：5 分鐘

**關鍵程式碼/設定**：
```bash
sudo apt update && sudo apt install -y gedit
gedit &
# 應可於 Windows 桌面顯示，支援剪貼簿/任務列/Alt+Tab
```

實際案例：Linux GUI 應用於 Windows 桌面顯示
實作環境：Windows 11 + WSL2（WSLg）
實測數據：
- 功能性指標：可於開始選單啟動、支援剪貼簿、任務列、Alt+Tab
- 使用者體感：GUI 工具無縫融入日常桌面

Learning Points（學習要點）
核心知識點：
- WSLg 能力與限制
- X11/Wayland 與 Windows 的整合
- 開發流程中的 GUI 工具選型

技能要求：
- 必備技能：WSL/apt
- 進階技能：GUI 應用除錯

延伸思考：
- GPU 加速的 GUI 應用（OpenGL/DirectML）在 WSLg 的表現？
- 安全性與權限管理

Practice Exercise（練習題）
- 基礎練習：安裝並啟動一個 GUI 編輯器（30 分）
- 進階練習：整合到 VSCode tasks 內一鍵開啟（2 小時）
- 專案練習：建立 GUI 工具清單與安裝腳本（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：GUI 可正常顯示與操作
- 程式碼品質（30%）：安裝腳本清晰
- 效能優化（20%）：啟動流暢
- 創新性（10%）：與開發流程整合
```

--------------------------------
案例分類

1) 按難度分類
- 入門級（適合初學者）
  - Case #7, #12, #13, #16, #17, #18
- 中級（需要一定基礎）
  - Case #1, #2, #3, #9, #10, #11, #14, #15
- 高級（需要深厚經驗）
  - Case #4, #5

2) 按技術領域分類
- 架構設計類
  - Case #4（專屬 SSD/EXT4）、#5（VHDX 隔離）、#15（資料安置準則）
- 效能優化類
  - Case #1（Qdrant）、#2（Jekyll）、#3（fio 基準）、#4、#5、#7、#14
- 整合開發類
  - Case #10（Ollama+GPU）、#11（Remote - WSL）、#16（code .）、#17（Port）、#18（WSLg）
- 除錯診斷類
  - Case #6（watch 修復）、#3（基準方法）、#9（GPU 容器驗證）
- 安全防護類
  - 關聯建議（非主軸）：#10、#17（端口公開時的安全性提示）

3) 按學習目標分類
- 概念理解型
  - Case #3、#7、#12、#14、#18
- 技能練習型
  - Case #11、#16、#17
- 問題解決型
  - Case #1、#2、#4、#5、#6、#9、#10、#13、#15
- 創新應用型
  - Case #10（LLM 堆疊）、#18（WSLg GUI 整合）

--------------------------------
案例關聯圖（學習路徑建議）

- 建議先學
  - Case #3（WSL I/O 基準與 4 通路認知）→ 形成對 DrvFS/9P/Hyper-V 的整體理解
  - Case #11（VSCode Remote - WSL）與 Case #16（code .）→ 建立日常工作流底座
  - Case #7（DrvFS 使用邊界）→ 避免踩雷

- 依賴關係
  - Case #1（Qdrant 提速）、#2（Jekyll 提速）依賴 Case #3、#7、#11、#16 的共識與工具
  - Case #4（專屬 SSD）與 Case #5（VHDX）屬於 Case #1/#2 的高階優化
  - Case #6（watch 修復）與 Case #2 強關聯（inotify 必須）
  - GPU 線（Case #8 → Case #9 → Case #10）：先可見 GPU，再容器可用，最後建構應用堆疊
  - Case #13（mklink）作為 Case #1/#2 的輔助（僅瀏覽）

- 完整學習路徑建議
  1) 基礎概念與工具流：Case #3 → #11 → #16 → #7
  2) 快速見效的問題解決：Case #2（Jekyll）與 #1（Qdrant）
  3) 可靠的資料安置與優化：Case #15 → #5（VHDX）或 #4（專屬 SSD）
  4) 開發體驗完善：Case #17（Port）→ #12（Interop）→ #13（mklink）
  5) GPU 能力線：Case #8（WSL GPU）→ #9（容器 GPU）→ #10（Ollama）→（可延伸更多 GPU 服務）
  6) 額外 GUI 能力：Case #18（WSLg）為輔助增強

以上 18 個案例涵蓋從 WSL 架構認知、效能優化、開發整合到 GPU 堆疊的完整實戰脈絡，並提供可重現的步驟、程式碼與量化數據，便於教學、實作與評測。
```

{% endraw %}