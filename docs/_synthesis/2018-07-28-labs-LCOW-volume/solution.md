---
layout: synthesis
title: "使用 LCOW 掛載 Volume 的效能陷阱"
synthesis_type: solution
source_post: /2018/07/28/labs-LCOW-volume/
redirect_from:
  - /2018/07/28/labs-LCOW-volume/solution/
postid: 2018-07-28-labs-LCOW-volume
---

以下內容基於提供的文章，萃取並結構化 15 個具完整教學價值的「問題解決案例」。每一案例均包含問題、根因、解決方案（含實作與程式碼）、實測數據與學習要點，並在最後提供分類與學習路徑建議。

## Case #1: LCOW volume->volume 的 Jekyll 建置隨機失敗

### Problem Statement（問題陳述）
業務場景：在 Windows 開發機上以 LCOW（Linux Container on Windows）執行 Jekyll 官方 image（2.4.0），希望將網站原始碼與輸出目錄都掛載至 volume，讓修改立即反映並持久化，支援本機預覽與快速迭代。
技術挑戰：在 LCOW 下 volume->volume 寫入大量小檔案時，Jekyll 建置任意時間點會因檔案操作「Operation not permitted」中斷。
影響範圍：開發者無法完成本機預覽，持續整合流程中斷；影響團隊效率與發布節奏。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 文件系統返回「Operation not permitted」，特徵為隨機發生於不同輸出檔案（.js/.jpg/.gif）。
2. 問題集中在 volume 寫入階段，且發生於大量 I/O 場景。
3. 在 LCOW 下重複多次均可重現，且停止位置不固定，疑似 race condition。

深層原因：
- 架構層面：跨越 Windows Host 與 LCOW LinuxKit VM 的共享機制，權限/鎖定語意與時機不一致。
- 技術層面：LCOW 對跨 VM/Host 的 volume 路徑處理尚未優化，對大量並發小檔案寫入易觸發錯誤。
- 流程層面：將來源與目的都掛 volume，導致跨邊界 I/O 密集且頻繁，放大風險。

### Solution Design（解決方案設計）
解決策略：避免在 LCOW 下對掛載的 volume 進行大量寫入，改為「destination 寫在 container 內部（如 /tmp）」以繞過跨邊界 I/O，再於成功後一次性拷出或改用 Docker for Windows 引擎。

實施步驟：
1. 切換輸出至 container 內
- 實作細節：Jekyll -d 指向 /tmp 或 /srv/jekyll/_site 改為 container 內路徑
- 所需資源：jekyll/jekyll:2.4.0
- 預估時間：0.5 小時

2. 成品安全複製回 Host
- 實作細節：使用 docker cp 或建立短命 copy 容器將 /tmp 複製到 host 目錄
- 所需資源：Docker CLI
- 預估時間：0.5 小時

3. 或改用 Docker for Windows（Linux 引擎）
- 實作細節：使用 Docker for Windows 的 MobyLinux VM 執行 Linux container
- 所需資源：Docker Desktop for Windows
- 預估時間：1 小時

關鍵程式碼/設定：
```bash
# 在 LCOW 下改為 container -> container（避免 volume 寫入）
docker run --rm \
  -v %CD%:/srv/jekyll:ro \  # source 只讀
  jekyll/jekyll:2.4.0 \
  jekyll build -s /srv/jekyll -d /tmp/site

# 完成後將輸出複製回 Host（Windows PowerShell）
$container=$(docker create jekyll/jekyll:2.4.0)
docker cp $container:/tmp/site .\_site
docker rm $container
```

實際案例：LAB1 測試環境 #1（LCOW volume->volume）多次失敗，錯誤訊息「Operation not permitted @ apply2files - ...」
實作環境：Windows 10/Server 1803 + LCOW + jekyll/jekyll:2.4.0
實測數據：
- 改善前：volume->volume 隨機失敗（無法完成）
- 改善後（volume->container）：135.493s
- 進一步（container->container）：12.86s
- 改善幅度：從無法完成到 12.86s（成功），相較 135.493s 提升約 90.5%

Learning Points（學習要點）
核心知識點：
- 跨 Host/VM volume 的權限與鎖定差異
- LCOW 與 Docker for Windows 引擎差異
- 開發環境 I/O 模式對效能與穩定性的影響

技能要求：
- 必備技能：Docker volume 與容器檔案系統、基本 Linux 命令
- 進階技能：跨引擎排錯、檔案系統語意與鎖定理解

延伸思考：
- 這個解決方案還能應用在哪些場景？任一大量小檔案輸出的建置流程（前端打包、靜態網站生成）。
- 有什麼潛在的限制或風險？container 內輸出需拷出流程，需確保同步正確。
- 如何進一步優化這個方案？以容器內部快取/層（layer）加速，或以壓縮打包再跨邊界移動。

Practice Exercise（練習題）
- 基礎練習：在 LCOW 下重現 volume->volume 錯誤，改為 container->container 完成建置。
- 進階練習：加入 docker cp 步驟自動化，確保輸出同步回 Host。
- 專案練習：把 jekyll 本地開發流程改為 compose 腳本自動建置與同步。

Assessment Criteria（評估標準）
- 功能完整性（40%）：可穩定建置並取得輸出
- 程式碼品質（30%）：容器命令與腳本清晰、可維護
- 效能優化（20%）：建置時間顯著縮短且穩定
- 創新性（10%）：同步與快取策略設計合理


## Case #2: LCOW volume->container 過慢，改為 container->container

### Problem Statement（問題陳述）
業務場景：開發者在 LCOW 下使用 jekyll image，source 掛在 volume、destination 寫 container 以避開 vol 寫入錯誤，但發現建置時間仍高達 135 秒，造成迭代緩慢。
技術挑戰：跨 OS 邊界讀（volume）仍有顯著延遲，大量小檔案讀取放大 overhead。
影響範圍：本地開發迭代時間延長 10x 以上，降低開發效率。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. source 從 volume 讀取，仍需跨 Windows Host 與 LCOW VM 邊界。
2. Jekyll 讀寫小檔案頻繁，跨邊界呼叫成本高。
3. LCOW volume 讀取未經特別優化。

深層原因：
- 架構層面：LCOW 單容器單 VM 的設計，跨邊界 I/O 成本高。
- 技術層面：大量 metadata 操作（開檔、關檔）在跨 VM 邊界放大延遲。
- 流程層面：仍以 volume 為主資料來源，導致讀取瓶頸。

### Solution Design（解決方案設計）
解決策略：把 source 也搬進 container（container->container），建置過程完全在容器檔案系統內，僅在開發完成時一次性同步回本機。

實施步驟：
1. 啟動前先把 source 複製進容器
- 實作細節：docker cp 或在 docker run 前 mount 為只讀後 cp 到 /tmp/source
- 所需資源：Docker CLI
- 預估時間：0.5 小時

2. 在容器內執行 jekyll 建置
- 實作細節：jekyll -s /tmp/source -d /tmp/site
- 所需資源：jekyll/jekyll:2.4.0
- 預估時間：0.5 小時

3. 完成後再把輸出拷回 Host
- 實作細節：docker cp $cid:/tmp/site ./_site
- 所需資源：Docker CLI
- 預估時間：0.5 小時

關鍵程式碼/設定：
```bash
# 容器內全內部 I/O
docker run --name jekbuild -d jekyll/jekyll:2.4.0 sh -c "sleep infinity"
docker cp . jekbuild:/tmp/source
docker exec jekbuild jekyll build -s /tmp/source -d /tmp/site
docker cp jekbuild:/tmp/site ./_site
docker rm -f jekbuild
```

實際案例：LAB1 #2（LCOW volume->container 135.493s）→ #3（container->container 12.86s）
實作環境：Windows + LCOW + Jekyll 2.4.0
實測數據：
- 改善前：135.493s
- 改善後：12.86s
- 改善幅度：約 90.5%（~10.5x 加速）

Learning Points（學習要點）
核心知識點：
- 讀/寫兩端跨邊界 I/O 開銷
- 小檔案密集工作負載對共享檔案系統的影響
- 容器內 I/O 與 volume I/O 的本質差異

技能要求：
- 必備技能：Docker 基本操作、Linux 檔案操作
- 進階技能：建置流程拆分與資料同步策略

延伸思考：
- 還能應用於前端打包、靜態資產生成、Sphinx/Hugo 等。
- 容器內 I/O 需要額外同步步驟，處理衝突與版本需小心。
- 可加入 rsync/壓縮打包以降低單次同步開銷。

Practice Exercise（練習題）
- 基礎：將 source 改為容器內路徑並完成建置。
- 進階：寫 script 自動完成「啟動→拷入→建置→拷出→清理」。
- 專案：將流程整合至 CI，產出 artifact。

Assessment Criteria（評估標準）
- 功能完整性：建置可重現且輸出正確
- 程式碼品質：腳本容錯、結構清晰
- 效能優化：建置時間顯著下降
- 創新性：同步策略/快取設計


## Case #3: Docker for Windows volume->volume 過慢，改為 volume->container

### Problem Statement（問題陳述）
業務場景：使用 Docker for Windows（Linux 引擎）執行 Jekyll，source 與 destination 都掛載 volume，期望本機直接讀寫持久化資料。
技術挑戰：volume->volume 建置需 120.368s，無法接受。
影響範圍：開發迭代與預覽延遲，降低效率。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. Docker for Windows 用 SMB 將本機磁碟分享給 MobyLinux VM，跨 VM 邊界讀/寫。
2. Jekyll 產生大量小檔案，SMB 行為易放大延遲。
3. 來源與輸出皆走 SMB，共兩倍跨邊界 I/O。

深層原因：
- 架構層面：單 VM（MobyLinux）對所有 Linux containers，Volume 經 SMB。
- 技術層面：SMB 在高頻 metadata I/O 場景下效率不佳。
- 流程層面：把雙端都放 volume，導致最差路徑。

### Solution Design（解決方案設計）
解決策略：source 保留在 volume（便於變更），但 destination 改寫 container 檔案系統（volume->container），大幅降低寫入跨邊界次數。

實施步驟：
1. 保留 source 掛載
- 實作細節：-v %CD%:/srv/jekyll:ro
- 所需資源：Docker Desktop
- 預估時間：0.2 小時

2. destination 切到容器內
- 實作細節：-d /tmp/site
- 所需資源：jekyll image
- 預估時間：0.2 小時

3. 視需要複製輸出回 Host
- 實作細節：docker cp
- 所需資源：Docker CLI
- 預估時間：0.2 小時

關鍵程式碼/設定：
```bash
docker run --rm \
  -v %CD%:/srv/jekyll:ro \
  jekyll/jekyll:2.4.0 \
  jekyll build -s /srv/jekyll -d /tmp/site
```

實際案例：LAB1 #4（volume->volume 120.368s）→ #5（volume->container 35.763s）
實作環境：Windows 10 + Docker for Windows + Jekyll 2.4.0
實測數據：
- 改善前：120.368s
- 改善後：35.763s
- 改善幅度：約 70.3%

Learning Points（學習要點）
核心知識點：
- Docker for Windows 的 SMB volume 實作
- 讀與寫路徑的優化策略
- 小檔案 vs. 連續寫入在 SMB 的差異

技能要求：
- 必備技能：Docker volume 操作
- 進階技能：檔案系統與網路分享協定行為理解

延伸思考：
- 可套用於 webpack、rollup 的 build 輸出。
- 仍需處理輸出持久化的擷取。
- 可加上 watch 模式與增量建置提升體驗。

Practice Exercise
- 基礎：volume->container 完成 Jekyll 建置。
- 進階：自動將輸出同步回 Host。
- 專案：將此模式包裝成 npm script 或 makefile。

Assessment Criteria
- 功能完整性：可重現
- 程式碼品質：腳本穩定
- 效能優化：建置時間降幅顯著
- 創新性：自動化程度


## Case #4: 建置全在容器內（container->container），完成後再 copy out

### Problem Statement（問題陳述）
業務場景：開發者需要最短建置時間以快速預覽，且避免 LCOW/Docker for Windows volume 的效能與穩定性問題。
技術挑戰：如何兼顧速度與輸出可取回。
影響範圍：開發迭代速度直接受影響。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. container 檔案系統本地化 I/O 最快。
2. 只需在最後一次性將結果拷出，將跨邊界 I/O 次數降至最低。
3. 寫入量大時特別有效。

深層原因：
- 架構層面：避免跨 VM/Host 邊界的 I/O。
- 技術層面：連續大量寫入在本地 FS 表現最佳。
- 流程層面：分離「建置」與「同步」兩個階段。

### Solution Design（解決方案設計）
解決策略：採用 container->container 建置模式，完成後用 docker cp 或短命 copy 容器把輸出帶回 Host。

實施步驟：
1. 容器內建置
- 實作細節：-s /tmp/src -d /tmp/dst
- 所需資源：目標 image
- 預估時間：0.5 小時

2. 輸出拷回
- 實作細節：docker cp $cid:/tmp/dst ./_site
- 所需資源：Docker CLI
- 預估時間：0.5 小時

3. 自動化包裝
- 實作細節：腳本或 makefile
- 所需資源：Shell/PowerShell
- 預估時間：1 小時

關鍵程式碼/設定：
```bash
# 建置（容器內 I/O）
docker run --name b1 -d jekyll/jekyll:2.4.0 sh -c "sleep infinity"
docker cp . b1:/tmp/src
docker exec b1 jekyll build -s /tmp/src -d /tmp/dst
docker cp b1:/tmp/dst ./_site
docker rm -f b1
```

實際案例：LAB1 #3（LCOW 12.86s）、#6（Docker for Windows 12.11s）
實作環境：Windows + LCOW/Docker for Windows + Jekyll 2.4.0
實測數據：
- 改善前：LCOW volume->container 135.493s；Docker for Windows volume->container 35.763s
- 改善後：~12s
- 改善幅度：LCOW 約 10.5x；Docker for Windows 約 2.95x

Learning Points
核心知識點：
- 建置與同步分離的流程設計
- 容器內 FS I/O 與 Volume I/O 差異
- 小檔案大量寫入的最佳實踐

技能要求：
- 必備：Docker CLI、Shell/PowerShell
- 進階：流程自動化

延伸思考：
- 可整合 cache（如 bundle/cache）以更快。
- 輸出衝突與差異比對（rsync/校驗）。
- CI/CD 的 artifact 管理。

Practice Exercise
- 基礎：以 container->container 完成一次建置與拷出。
- 進階：自動偵測變更才重建。
- 專案：封裝為整合開發腳本。

Assessment Criteria
- 功能：一鍵建置+同步
- 程式碼：腳本結構清楚
- 效能：時間顯著下降
- 創新：快取與增量策略


## Case #5: Windows Container 隔離層級（process vs hyper-v）對 to-container I/O 的衝擊

### Problem Statement（問題陳述）
業務場景：在 Windows Server 執行 Windows container，選擇不同隔離層級以平衡安全與效能。
技術挑戰：hyper-v 隔離層級的 to-container I/O 顯著變慢。
影響範圍：I/O 密集型工作負載效能顯著下降。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. LAB2-1：process→to container 1.5724s；hyper-v→to container 5.9010s（+276%）。
2. hyper-v 會將容器放進專屬輕量 VM，跨邊界成本增加。
3. 連續寫入與 metadata 操作均受影響。

深層原因：
- 架構層面：隔離層級越高，I/O 路徑越長。
- 技術層面：虛擬化層處理資料路徑與中斷。
- 流程層面：未針對隔離層級調整 I/O 策略。

### Solution Design（解決方案設計）
解決策略：能用 process 隔離時盡量使用（開發/低風險環境），若必須用 hyper-v，改為 to-volume 或重構 I/O 模式。

實施步驟：
1. 在 Windows Server 使用 process 隔離
- 實作細節：--isolation=process
- 所需資源：Windows Server 1803+
- 預估時間：0.5 小時

2. I/O 密集任務固定調度到 process 隔離節點
- 實作細節：標記 node/compose profiles
- 所需資源：Swarm/K8s（可選）
- 預估時間：1 小時

3. 若必須 hyper-v 隔離，偏向寫 volume
- 實作細節：參考 Case #6
- 所需資源：本機 volume
- 預估時間：0.5 小時

關鍵程式碼/設定：
```powershell
# Windows container 指定隔離層級
docker run --isolation=process mcr.microsoft.com/windows/servercore:1803 cmd /c echo ok
```

實際案例：LAB2-1 Windows Server 1803
實作環境：Windows Server 1803，Intel i7-2600K，Intel 730 SSD
實測數據：
- process to container：1.5724s
- hyper-v to container：5.9010s
- 差異：+276%（效能下降約 3.76x）

Learning Points
核心知識點：
- Windows container 隔離層級與 I/O 關係
- 安全與效能取捨
- 任務調度策略

技能要求：
- 必備：Windows container 基礎
- 進階：節點分群與調度策略

延伸思考：
- 適合 process：開發、可信網段
- 適合 hyper-v：多租戶/強隔離
- 進一步：拆分 I/O 密集與 CPU 密集容器

Practice Exercise
- 基礎：同 workload 在 process 與 hyper-v 下測 dd。
- 進階：寫 compose 在不同 profiles 切換隔離層級。
- 專案：在實驗集群上進行自動調度。

Assessment Criteria
- 功能：可切換隔離層級
- 程式碼：compose/profile 清楚
- 效能：量化差異
- 創新：調度策略合理


## Case #6: 在 Windows Container hyper-v 下改寫 volume 比寫 container 快

### Problem Statement（問題陳述）
業務場景：合規要求下必須用 hyper-v 隔離的 Windows container，I/O 密集任務需要優化。
技術挑戰：hyper-v 下寫 container 昂貴，如何降低成本。
影響範圍：批次任務/建置任務耗時。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. LAB2-1：hyper-v to container 5.9010s；hyper-v to volume 2.2083s。
2. 寫入 volume 的路徑在此情境下更短或更優化。
3. metadata 操作成本降低。

深層原因：
- 架構層面：hyper-v 專屬 VM 內部 FS 寫入路徑較長。
- 技術層面：volume 的對應後端與快取策略有效。
- 流程層面：I/O 策略未依隔離層級調整。

### Solution Design（解決方案設計）
解決策略：在 hyper-v 隔離時，調整工作流為「寫入 volume」，並確保 volume 位於效能良好的本機磁碟。

實施步驟：
1. 建立本機 volume 並掛載
- 實作細節：-v C:\data\out:/out
- 所需資源：SSD 推薦
- 預估時間：0.2 小時

2. 工作負載輸出指向 /out
- 實作細節：應用配置將輸出改為 /out
- 所需資源：應用設定
- 預估時間：0.5 小時

3. 驗證效能並監控
- 實作細節：dd/工具監測
- 所需資源：dd.exe
- 預估時間：0.5 小時

關鍵程式碼/設定：
```powershell
# hyper-v 隔離 + 將輸出指向 volume
docker run --isolation=hyperv -v C:\data\out:/out mcr.microsoft.com/windows/servercore:1803 powershell -c "
# 寫測試檔案到 /out
"
```

實際案例：LAB2-1
實作環境：Windows Server 1803
實測數據：
- 改寫前：to container 5.9010s
- 改寫後：to volume 2.2083s
- 改善幅度：約 62.6%

Learning Points
核心知識點：
- 同一隔離層級下 to-container vs to-volume 的差異
- volume 後端與 I/O 路徑優化
- 任務輸出路徑設計

技能要求：
- 必備：volume 掛載、應用輸出路徑設定
- 進階：磁碟/檔案系統效能觀念

延伸思考：
- volume 存放的磁碟類型對效能影響
- 讀寫分離（讀 container，寫 volume）
- 加入資料完整性校驗

Practice Exercise
- 基礎：在 hyper-v 下切換 to container 與 to volume 測試 dd。
- 進階：替應用加入輸出路徑參數化。
- 專案：將策略納入部署模版。

Assessment Criteria
- 功能：輸出可切換
- 程式碼：參數化良好
- 效能：降幅可量化
- 創新：磁碟選型/監控設計


## Case #7: LCOW 寫 volume 極慢，避免在 LCOW 對 volume 寫入

### Problem Statement（問題陳述）
業務場景：Linux 工作負載在 Windows 上用 LCOW 跑，需將輸出寫到 volume 持久化。
技術挑戰：LCOW 寫 volume 異常緩慢（LAB2-1: 21.3261s）。
影響範圍：I/O 密集型任務建置時間暴增。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. LCOW hyper-v to volume：21.3261s（vs Windows container hyper-v to volume 2.2083s）。
2. 跨邊界共享機制在 LCOW 上未優化。
3. 大量連續/小檔案寫對 volume 成本極高。

深層原因：
- 架構層面：LCOW 每個容器一個 VM，volume 跨邊界更重。
- 技術層面：共享協定/檔案系統實作差異。
- 流程層面：未避開 LCOW 的弱項。

### Solution Design（解決方案設計）
解決策略：在 LCOW 下避免對 volume 大量寫入；若必須 Linux 容器大量寫 volume，改用 Docker for Windows 引擎或將輸出改為容器內再拷出。

實施步驟：
1. 優先 container->container（同 Case #4）
- 實作細節：輸出在容器內部
- 所需資源：Docker CLI
- 預估時間：0.5 小時

2. 若必須 volume：切換 Linux 引擎到 Docker for Windows
- 實作細節：Docker Desktop 使用 Linux 引擎
- 所需資源：Docker Desktop
- 預估時間：1 小時

3. 驗證持續效能
- 實作細節：dd/工具持續監測
- 所需資源：dd
- 預估時間：0.5 小時

關鍵程式碼/設定：
```bash
# Docker for Windows（Linux 引擎）掛 SMB volume
docker run --rm -v %CD%:/data alpine sh -c "dd if=/dev/urandom of=/data/largefile bs=1M count=1024"
```

實際案例：LAB2-1（LCOW to volume 21.3261s）
實作環境：Windows Server 1803
實測數據（參考對照）：
- LCOW to volume：21.3261s
- Windows container hyper-v to volume：2.2083s
- 差距：約 9.7x

Learning Points
核心知識點：
- LCOW 對 volume I/O 的弱項
- 引擎選擇對 I/O 的實質影響
- 選擇 container FS 優於跨邊界 volume 寫

技能要求：
- 必備：引擎切換、volume 掛載
- 進階：I/O 模式重構

延伸思考：
- 何時選 LCOW（混合容器共存）vs Docker for Windows（Linux I/O）
- 是否能延後 volume 寫入
- 有無可接受的最終同步策略

Practice Exercise
- 基礎：重現 LCOW to volume 的 dd 與對照。
- 進階：切引擎對比 I/O。
- 專案：封裝成快速基準測試腳本。

Assessment Criteria
- 功能：可切引擎並測試
- 代碼：腳本可維護
- 效能：差異呈現清晰
- 創新：測試自動化


## Case #8: Linux 容器寫 volume：Docker for Windows 明顯快於 LCOW

### Problem Statement（問題陳述）
業務場景：Windows 開發機上跑 Linux 容器，需寫入 volume。
技術挑戰：LCOW 寫 volume 慢於 Docker for Windows。
影響範圍：建置/打包任務時間膨脹。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. LAB2-2：LCOW to volume 41.1397s；Docker for Windows to volume 9.1047s。
2. Docker for Windows 透過 SMB 共享磁碟，性能較 LCOW 方案佳。
3. LCOW volume 路徑處理未最佳化。

深層原因：
- 架構層面：LCOW 每容器獨立 VM；Docker for Windows 共享單 VM。
- 技術層面：共享協定/快取行為差異。
- 流程層面：無根據引擎調整 I/O 策略。

### Solution Design（解決方案設計）
解決策略：對 Linux 容器需要大量寫 volume 的場景，優先使用 Docker for Windows；或改 container 內寫，再複製回 Host。

實施步驟：
1. 切換至 Docker for Windows Linux 引擎
- 實作細節：Docker Desktop 切換
- 所需資源：Docker Desktop
- 預估時間：0.5 小時

2. 調整 volume 掛載並測試
- 實作細節：-v C:\path:/data
- 所需資源：SMB 自動分享
- 預估時間：0.5 小時

3. 對比 dd/Jekyll 實測
- 實作細節：重跑 dd 與 Jekyll
- 所需資源：dd/jekyll image
- 預估時間：1 小時

關鍵程式碼/設定：
```bash
# Docker for Windows（Linux）
docker run --rm -v %CD%:/data alpine sh -c "dd if=/dev/urandom of=/data/largefile bs=1M count=1024"
```

實際案例：LAB2-2
實作環境：Windows 10 1803
實測數據：
- LCOW to volume：41.1397s
- Docker for Windows to volume：9.1047s
- 改善幅度：約 77.9%

Learning Points
核心知識點：
- Linux 容器在 Windows 的兩種路徑差異
- SMB 共享行為特性
- I/O 策略需依引擎選擇

技能要求：
- 必備：Docker Desktop 操作
- 進階：效能測試與判讀

延伸思考：
- 為何 Docker for Windows 在此更佳？
- SMB 最佳化（防毒排除、快取設定）是否可能？
- 何時必須改 container->container？

Practice Exercise
- 基礎：兩引擎對比 dd。
- 進階：改 Jekyll 建置流程測量差異。
- 專案：產出引擎選型 decision log。

Assessment Criteria
- 功能：能切換與測量
- 程式碼：測試腳本可重用
- 效能：差異明確
- 創新：決策依據完整


## Case #9: 避免 Nested Virtualization（Azure 上 hyper-v 慘烈）

### Problem Statement（問題陳述）
業務場景：在 Azure VM（已是虛擬化）內再啟動 hyper-v 容器，評估 I/O 性能。
技術挑戰：Nested Virtualization 下 I/O 性能極差，不具實務價值。
影響範圍：任何 I/O 密集型容器在雲端 VM 的 nested hyper-v 模式。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. LAB2-3：windows hyper-v→to container 66.8226s；linux hyper-v→to container 52.5351s。
2. VM 裡再跑 VM，I/O 路徑最長。
3. Azure 磁碟也非本地直通，額外延遲。

深層原因：
- 架構層面：雙層虛擬化
- 技術層面：虛擬化層與雲端存儲延遲疊加
- 流程層面：在雲端 VM 內強行啟動 hyper-v 容器

### Solution Design（解決方案設計）
解決策略：不要在雲端 VM 做 nested hyper-v；以編排器（Swarm/K8s）將 Linux/Windows 容器分派到對應 OS 的節點，以 process 隔離執行。

實施步驟：
1. 區分 Linux/Windows 節點
- 實作細節：標籤/taint 節點
- 所需資源：K8s/Swarm
- 預估時間：1 小時

2. 用 nodeSelector 指派工作負載
- 實作細節：K8s Deployment 設定
- 所需資源：K8s
- 預估時間：1 小時

3. 關閉 nested hyper-v 試驗性用法
- 實作細節：CI/環境守則
- 所需資源：團隊規範
- 預估時間：0.5 小時

關鍵程式碼/設定：
```yaml
# K8s 示例：Linux 工作負載只跑在 linux=true 的節點
apiVersion: apps/v1
kind: Deployment
metadata:
  name: linux-workload
spec:
  replicas: 2
  selector:
    matchLabels: { app: linux-workload }
  template:
    metadata:
      labels: { app: linux-workload }
    spec:
      nodeSelector:
        kubernetes.io/os: linux
        workload: io-heavy
      containers:
      - name: app
        image: alpine
        command: ["sh","-c","dd if=/dev/urandom of=/tmp/file bs=1M count=1024"]
```

實際案例：LAB2-3 Azure D4S v3
實作環境：Azure VM（Windows Server Datacenter 1803）
實測數據：
- nested hyper-v：66.8226s（Win）/ 52.5351s（Linux）
- 原生/過程隔離（對照其他組）：~2-6s
- 改善幅度：>10x（避免 nested）

Learning Points
核心知識點：
- 雲端虛擬化與 nested 的疊加效應
- 編排器的節點選擇
- 適地適材：Linux 容器跑 Linux 節點

技能要求：
- 必備：K8s 基礎
- 進階：節點標籤/選擇器

延伸思考：
- 雲廠商磁碟方案選擇（Premium SSD 等）
- 是否分離 I/O 密集與非 I/O 工作負載
- 監控與 SLO 設計

Practice Exercise
- 基礎：在 K8s 用 nodeSelector 佈署。
- 進階：加入 taint/toleration 控制。
- 專案：設計一個多節點調度策略文檔。

Assessment Criteria
- 功能：部署正確
- 程式碼：YAML 清晰
- 效能：避免 nested 帶來的劣化
- 創新：調度策略完整


## Case #10: 建立跨環境 I/O 基準（dd）以客觀選型

### Problem Statement（問題陳述）
業務場景：團隊需要客觀數據決定容器引擎/隔離層級/volume 策略。
技術挑戰：環境多、硬體不同、數據易誤讀。
影響範圍：引擎/架構選型決策與費用效益。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 不同硬體/OS/隔離層級不可直接互比。
2. 缺少一致測試方法易產生誤判。
3. 缺乏自動化基準腳本。

深層原因：
- 架構層面：測試分組不明
- 技術層面：測試工具/參數不一致
- 流程層面：缺少基準流程

### Solution Design（解決方案設計）
解決策略：制定 dd 標準測試（if=/dev/urandom，bs=1M，count=1024），同一組硬體內各組態跑 5 次取平均，對比 to container/volume。

實施步驟：
1. 撰寫跨平台測試腳本
- 實作細節：Linux dd / Windows dd.exe
- 所需資源：dd 工具
- 預估時間：1 小時

2. 規範分組比較
- 實作細節：相同硬體、不同組態
- 所需資源：表格模板
- 預估時間：0.5 小時

3. 建立決策門檻
- 實作細節：>2x 認定顯著差異
- 所需資源：團隊規範
- 預估時間：0.5 小時

關鍵程式碼/設定：
```bash
# Linux
dd if=/dev/urandom of=./largefile bs=1M count=1024

# Windows 容器（示意，需 dd.exe）
dd.exe if=\\?\Device\Null of=.\largefile bs=1M count=1024
```

實際案例：LAB2-1/2/3 三組硬體與 OS 的系統性比較
實作環境：Windows Server/Windows 10/Azure VM
實測數據：文中各表格（同組內可直接對比）
- 效益：避免誤判、選型更精準

Learning Points
核心知識點：
- 測試設計與統計基本觀念
- I/O 基準設計
- 跨平台差異解讀

技能要求：
- 必備：Shell/PowerShell、自動化測試
- 進階：數據分析與報告

延伸思考：
- 加入 filecount/metadata 測試補足 dd 局限
- 長時程監測
- 將基準納入 CI 檢查

Practice Exercise
- 基礎：完成 dd 基準腳本
- 進階：加入重試/平均/標準差
- 專案：製作選型報告模版

Assessment Criteria
- 功能：腳本可用
- 程式碼：可維護、跨平台
- 效能：數據可比性強
- 創新：報告工具化


## Case #11: Windows 10 上的 Linux 容器寫 volume：選 Docker for Windows

### Problem Statement（問題陳述）
業務場景：開發機為 Windows 10，需運行 Linux 容器並頻繁寫 volume。
技術挑戰：LCOW 表現劣於 Docker for Windows。
影響範圍：開發迭代與本機預覽。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. LAB2-2：LCOW to volume 41.1397s；Docker for Windows 9.1047s。
2. Windows 10 不支援 Windows container process 隔離（對 Win 容器），但此案例聚焦 Linux 容器。
3. Docker for Windows 的 SMB 路徑較佳。

深層原因：
- 架構層面：Windows 10 下 LCOW 能力受限、成熟度不如 Docker for Windows。
- 技術層面：MobyLinux + SMB 的表現優於 LCOW 的共享機制。
- 流程層面：未按 OS 特性選擇引擎。

### Solution Design（解決方案設計）
解決策略：Windows 10 上的 Linux 容器大量寫 volume，優先用 Docker for Windows；或調整為容器內寫、最後同步。

實施步驟：
1. 切引擎為 Docker for Windows（Linux）
- 實作細節：Docker Desktop 切換
- 所需資源：Docker Desktop
- 預估時間：0.5 小時

2. 以 volume->container 或 container->container
- 實作細節：參考 Case #3/#4
- 所需資源：Jekyll 或目標 image
- 預估時間：0.5-1 小時

3. 驗證 dd 與實際 workload
- 實作細節：收集時間數據
- 所需資源：dd/工具
- 預估時間：0.5 小時

關鍵程式碼/設定：
```bash
# Linux 容器在 Docker for Windows 上寫 volume
docker run --rm -v %CD%:/out alpine sh -c "dd if=/dev/urandom of=/out/f bs=1M count=1024"
```

實際案例：LAB2-2
實作環境：Windows 10 1803
實測數據：
- LCOW to volume：41.1397s
- Docker for Windows to volume：9.1047s
- 改善幅度：約 77.9%

Learning Points
核心知識點：
- Windows 10 上 Linux 容器引擎選擇
- volume I/O 策略
- dd 與實務 workload 的對應

技能要求：
- 必備：Docker Desktop 操作
- 進階：I/O 優化策略

延伸思考：
- 何時再改為 container->container？
- 是否需要雙引擎並存策略？
- 對 CI 的影響？

Practice Exercise
- 基礎：切引擎並測 dd
- 進階：套用到 Jekyll/前端打包
- 專案：制定 Windows 10 開發機標準

Assessment Criteria
- 功能：引擎切換正確
- 程式碼：測試可復用
- 效能：差異明顯
- 創新：標準落地


## Case #12: 混合 Windows/Linux 容器共存：選 LCOW，但重構 I/O

### Problem Statement（問題陳述）
業務場景：同一台開發/測試機需同時跑 Windows 與 Linux 容器，且共用網路與 compose。
技術挑戰：LCOW volumes I/O 弱項衝擊 Linux workload。
影響範圍：整體開發體驗與效能。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. LCOW 可共存/共網路/同 compose，但 volume I/O 對 Linux workload 效能差。
2. container->container 在 LCOW 下表現最佳（~12s）。
3. volume->container/volume->volume 在 LCOW 下差或不穩。

深層原因：
- 架構層面：混合容器共存便利，但 I/O 需避開 LCOW 弱項。
- 技術層面：容器內 I/O 與一次性拷出是最佳解。
- 流程層面：需要建立一致的開發 workflow。

### Solution Design（解決方案設計）
解決策略：在 LCOW 環境採 container->container，最後一次拷出；Windows 容器依需求選 process/hyper-v 並調整 I/O 路徑。

實施步驟：
1. Compose 中分離 Linux/Windows 服務
- 實作細節：labels 或 profiles
- 所需資源：docker compose
- 預估時間：1 小時

2. Linux build 容器採 container->container
- 實作細節：volume 只讀掛 source、輸出在 /tmp
- 所需資源：Jekyll/前端 image
- 預估時間：0.5 小時

3. 自動化輸出拷回
- 實作細節：post-step docker cp
- 所需資源：腳本
- 預估時間：1 小時

關鍵程式碼/設定：
```yaml
# docker-compose.yml（示意）
services:
  jekyll:
    image: jekyll/jekyll:2.4.0
    volumes:
      - ./:/src:ro
    command: sh -c "cp -a /src /tmp/source && jekyll build -s /tmp/source -d /tmp/site && sleep infinity"
    # 完成後用 docker cp 取回 /tmp/site
```

實際案例：LAB1 container->container ~12s（LCOW/Docker for Windows）
實作環境：Windows + LCOW + docker compose
實測數據：
- Jekyll：LCOW vol->cont 135.493s → cont->cont 12.86s（~90.5%）
- 綜效：共存便利 + 性能可控

Learning Points
核心知識點：
- LCOW 的定位：共存/共網路/共 compose
- 引擎便利性 vs I/O 最佳化
- Workflow 設計

技能要求：
- 必備：compose、Docker CLI
- 進階：跨服務資料流設計

延伸思考：
- 何時改用分開機器（Windows node / Linux node）？
- 開發與 CI 的策略差異
- 標準化模板落地

Practice Exercise
- 基礎：建立含 Win/Linux 的 compose。
- 進階：接入拷出與服務依賴。
- 專案：完成混合技術棧 demo。

Assessment Criteria
- 功能：可同時運行
- 程式碼：compose 清晰
- 效能：Linux build 可達 ~12s
- 創新：流程自動化


## Case #13: Windows Server 上以 process 隔離，I/O 幾近原生

### Problem Statement（問題陳述）
業務場景：Windows Server 作為建置節點，追求接近原生的 I/O。
技術挑戰：選擇正確隔離層級與 I/O 路徑。
影響範圍：CI/CD 節點效能與資源配置。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. LAB2-1：Windows 原生 to volume 1.5673s；process to container 1.5724s/ to volume 1.6365s，差距極小。
2. process 隔離最接近原生。
3. 寫 container/volume 都接近原生。

深層原因：
- 架構層面：無 VM 隔離層的成本。
- 技術層面：最短 I/O 路徑。
- 流程層面：標準化節點 OS 與隔離層級。

### Solution Design（解決方案設計）
解決策略：在 Windows Server 上使用 process 隔離作為預設，僅在需要時才切換 hyper-v。

實施步驟：
1. 設定預設 isolation=process
- 實作細節：Docker daemon/部署腳本指定
- 所需資源：Windows Server
- 預估時間：0.5 小時

2. 建置任務優先跑在該節點
- 實作細節：CI agent 綁定
- 所需資源：CI 工具
- 預估時間：1 小時

3. 性能監控
- 實作細節：定期 dd/實際 build 測量
- 所需資源：監控工具
- 預估時間：1 小時

關鍵程式碼/設定：
```powershell
# 預設使用 process 隔離
docker run --isolation=process mcr.microsoft.com/windows/servercore:1803 cmd /c ver
```

實際案例：LAB2-1
實作環境：Windows Server 1803
實測數據：
- 原生 vs process：1.5673s vs 1.5724s（幾乎相同）
- 效益：近原生效能，適合建置節點

Learning Points
核心知識點：
- Windows Server + process 的性價比
- CI 節點規劃
- 容器安全與效能平衡

技能要求：
- 必備：Windows 容器運維
- 進階：CI 節點管理

延伸思考：
- 安全需求高時如何切換策略？
- 節點汰換與彈性擴縮
- I/O 型工作負載專用節點

Practice Exercise
- 基礎：在 process 隔離下跑 dd。
- 進階：接入 CI agent。
- 專案：撰寫節點標準運維手冊。

Assessment Criteria
- 功能：節點可用
- 程式碼：部署腳本完善
- 效能：接近原生
- 創新：節點分層策略


## Case #14: Linux 工作負載盡量跑在 Linux（避免 Windows 上的虛擬化）

### Problem Statement（問題陳述）
業務場景：I/O 密集型 Linux 工作負載選擇最合適的執行平台。
技術挑戰：Windows 上以虛擬化方式跑 Linux 容器 I/O 代價高。
影響範圍：CI/CD、資料管線、建置節點。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. LAB2-3 Linux 原生/過程隔離 ~6.4-6.5s；Linux 在 Windows 虛擬化（hyper-v）~52.5-59.9s。
2. 跨層虛擬化與共享機制增加延遲。
3. 連續寫與 metadata 操作皆受影響。

深層原因：
- 架構層面：Windows 上跑 Linux 多一層虛擬化。
- 技術層面：共享檔案系統效率劣於原生。
- 流程層面：未針對平台選型。

### Solution Design（解決方案設計）
解決策略：Linux 工作負載盡量跑在 Linux 節點（裸金屬或原生 VM），避免 Windows 上虛擬化層；用編排器分派。

實施步驟：
1. 建立 Linux 節點池
- 實作細節：K8s node 標籤
- 所需資源：Linux 節點
- 預估時間：2 小時

2. 調度 I/O 密集工作負載
- 實作細節：nodeSelector/tolerations
- 所需資源：K8s
- 預估時間：1 小時

3. 對比與監控
- 實作細節：dd/實務任務監測
- 所需資源：監控平台
- 預估時間：1 小時

關鍵程式碼/設定：
```yaml
# 僅在 Linux 節點運行
spec:
  nodeSelector:
    kubernetes.io/os: linux
    perf: native
```

實際案例：LAB2-3
實作環境：Azure VM（Linux 節點 vs Windows hyper-v）
實測數據：
- Linux 原生/process：~6.4-6.5s
- Windows 上 Linux hyper-v：~52.5-59.9s
- 改善幅度：>8x

Learning Points
核心知識點：
- 原生平台優勢
- 編排器對齊工作負載與平台
- I/O 效能敏感工作負載選型

技能要求：
- 必備：K8s/Swarm
- 進階：平台規劃

延伸思考：
- 何時容忍虛擬化成本（本地開發/混合需求）
- 混合集群設計
- 成本與效能的平衡

Practice Exercise
- 基礎：Linux 節點佈署與標籤。
- 進階：I/O 工作負載調度。
- 專案：撰寫平台選型報告。

Assessment Criteria
- 功能：能調度到 Linux 節點
- 程式碼：YAML 清晰
- 效能：差異可驗證
- 創新：選型有據


## Case #15: Windows 10（hyper-v 唯一選擇）下，優先寫 container 再視需要同步

### Problem Statement（問題陳述）
業務場景：Windows 10 上跑 Windows 容器，OS 限制僅能 hyper-v 隔離。
技術挑戰：to-volume 比 to-container 更慢。
影響範圍：本地開發/測試回饋時間。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. LAB2-2：Windows hyper-v to container 4.5774s；to volume 5.6002s。
2. hyper-v 下寫 container 路徑較短。
3. volume 經過額外轉換/分享。

深層原因：
- 架構層面：Windows 10 限制不支援 process 隔離。
- 技術層面：volume 的共享/轉譯導致延遲。
- 流程層面：未因 OS 限制調整策略。

### Solution Design（解決方案設計）
解決策略：在 Windows 10 上以 hyper-v 隔離時，優先寫 container（內部），僅需持久化時再同步回 Host。

實施步驟：
1. 應用輸出路徑改為容器內
- 實作細節：將輸出目錄改 /tmp/out
- 所需資源：應用設定
- 預估時間：0.5 小時

2. 同步回 Host（按需）
- 實作細節：docker cp，或短命 copy 容器
- 所需資源：Docker CLI
- 預估時間：0.5 小時

3. 自動化腳本
- 實作細節：一鍵建置/同步
- 所需資源：PowerShell
- 預估時間：1 小時

關鍵程式碼/設定：
```powershell
# 建置輸出在容器內，再 cp 回 Host
$cid = docker run -d mcr.microsoft.com/windows/servercore:1803 powershell -c "Start-Sleep -Seconds 3600"
# ...在容器內完成輸出到 C:\tmp\out 後
docker cp $cid:"C:\tmp\out" .\out
docker rm -f $cid
```

實際案例：LAB2-2
實作環境：Windows 10 1803
實測數據：
- to container：4.5774s
- to volume：5.6002s
- 改善幅度：約 18.3%

Learning Points
核心知識點：
- Windows 10 的隔離限制與策略
- to-container 在 hyper-v 下可能更快
- 按需同步的工作流

技能要求：
- 必備：Windows 容器操作
- 進階：建置流程參數化

延伸思考：
- 改為 Windows Server 以用 process 隔離是否更佳？
- 不同磁碟/路徑對 to-volume 的影響？
- 加入快取/增量。

Practice Exercise
- 基礎：改輸出為 container 內路徑。
- 進階：寫同步腳本。
- 專案：Windows 10 開發模板。

Assessment Criteria
- 功能：可建置+同步
- 程式碼：腳本可維護
- 效能：時間縮短
- 創新：流程優化



--------------------------------
案例分類

1. 按難度分類
- 入門級（適合初學者）：Case 3, 4, 6, 8, 11, 15
- 中級（需要一定基礎）：Case 1, 2, 5, 7, 12, 13
- 高級（需要深厚經驗）：Case 9, 10, 14

2. 按技術領域分類
- 架構設計類：Case 9, 12, 14
- 效能優化類：Case 2, 3, 4, 5, 6, 7, 8, 11, 13, 15
- 整合開發類：Case 1, 12
- 除錯診斷類：Case 1, 10
- 安全防護類：Case 5（隔離層級取捨）

3. 按學習目標分類
- 概念理解型：Case 5, 8, 10, 13, 14
- 技能練習型：Case 3, 4, 6, 11, 15
- 問題解決型：Case 1, 2, 7, 9, 12
- 創新應用型：Case 10, 12, 14


案例關聯圖（學習路徑建議）
- 建議先學（基礎概念與快速收穫）：
  - Case 10（建立一致的 I/O 基準）
  - Case 3 / 4（volume->container 與 container->container 的實操）
  - Case 11（Windows 10 引擎選擇）
- 進一步（針對 Windows/LCOW 的深入）：
  - Case 5（隔離層級的效能影響）
  - Case 6（hyper-v 下 to-volume 策略）
  - Case 7 / 8（LCOW 與 Docker for Windows 的差異與選擇）
  - Case 13（Windows Server process 隔離近原生）
- 實戰整合（混合/編排與平台選型）：
  - Case 12（Win/Linux 容器共存的 workflow 設計）
  - Case 14（Linux 工作負載盡量跑 Linux）
  - Case 9（避免 nested virtualization，編排器調度）
- 依賴關係：
  - Case 1、2 依賴 Case 3/4 的 I/O 模式理解
  - Case 12 依賴 Case 5/7/8 的引擎與 I/O 策略
  - Case 9、14 依賴 Case 10 的測量方法做決策
- 完整學習路徑建議：
  1) Case 10 → 3 → 4 → 11（掌握基準與常用 I/O 模式）
  2) Case 5 → 6 → 7 → 8 → 13（深入 Windows/LCOW 差異與最佳策略）
  3) Case 12 → 14 → 9（完成混合場景與雲端調度的整體方案）
  4) 最後回看 Case 1 → 2（套用於 Jekyll/大量小檔案的實戰最佳化）