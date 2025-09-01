以下內容基於提供文章的觀點與實務經驗，抽取並結構化 17 個具完整教學價值的解決方案案例。每個案例包含問題、根因、解法、實作步驟、示例設定/程式、實際效益與評估方式，便於在實戰教學、專案練習與能力評估中使用。

## Case #1: 從工具導向到問題導向的 CI/CD 啟動專案

### Problem Statement（問題陳述）
**業務場景**：團隊希望導入 CI/CD，但成員大量關注工具選型（如 Jenkins、GitHub Actions、GitLab CI 等），忽略了目標問題（版本可追溯、品質回饋、發布一致性）。面試與日常對話常圍繞「是否有 CI/CD」，實際落地時卻面臨流程抗拒與無法持續維運，導致導入失敗或半途而廢。
**技術挑戰**：缺乏問題驅動的需求定義與最小可行流程（Minimal Viable Pipeline, MVPipe）設計，導致複雜度過高、工具學習門檻大、導入期過長。
**影響範圍**：導入失敗、成員反彈、維運負擔增加、交付節點延誤、品質與可追溯性不足。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 工具迷思：以工具為先，忽略需求與目標問題，實作無法聚焦。
2. 一次到位心態：企圖同時導入完整 CI/CD，導致風險與反彈加劇。
3. 學習門檻與流程衝突：新工具+新流程同時上線，團隊吸收速度不足。

**深層原因**：
- 架構層面：缺乏以能力疊代為核心的交付架構設計（版本控制、CI、發行管理的最小閉環）。
- 技術層面：無標準化 Pipeline 模板，缺乏 artifacts 與 package 的統一產出策略。
- 流程層面：未設定明確目標與衡量指標（如 Lead Time、Build 成功率、發布失敗率）。

### Solution Design（解決方案設計）
**解決策略**：以問題驅動導入，先建立「最小可行 CI/CD」：版本控制規範（Git Branch 策略）、基本 CI（編譯+單元測試+Artifacts）、基本發行管理（推送至套件/映像倉庫）。先集中使用現有平台（例如 GitLab 全家桶），逐步擴充，並用明確指標衡量導入成效。

**實施步驟**：
1. 啟動工作坊（Problem->Goal->MVPipe）
- 實作細節：定義三大核心問題與對應目標；確認 3-5 個衡量指標。
- 所需資源：協作工具、白板、OKR 模板
- 預估時間：0.5 天

2. 工具盤點與收斂
- 實作細節：評估現有工具重疊，確定單一平台落地（如 GitLab）。
- 所需資源：GitLab 伺服器/雲服務
- 預估時間：1-2 天

3. MVPipe 模板落地
- 實作細節：建立 .gitlab-ci.yml 模板（build/test/artifacts）。
- 所需資源：GitLab Runner（Docker）
- 預估時間：1 天

4. 迴圈式擴充計畫
- 實作細節：每兩週回顧，逐步加上更嚴格規則（如測試覆蓋門檻）。
- 所需資源：Scrum 會議
- 預估時間：持續

**關鍵程式碼/設定**：
```yaml
# .gitlab-ci.yml - MVPipe 模板
stages: [build, test, package]

variables:
  NODE_ENV: test

build:
  stage: build
  image: node:18
  script:
    - npm ci
    - npm run build
  artifacts:
    paths:
      - dist/
    expire_in: 7 days

unit_test:
  stage: test
  image: node:18
  needs: [build]
  script:
    - npm test -- --ci --reporter=spec
  artifacts:
    when: always
    reports:
      junit: junit.xml

package:
  stage: package
  image: node:18
  needs: [unit_test]
  only:
    - develop
    - master
  script:
    - tar -czf artifact-$CI_COMMIT_SHORT_SHA.tgz dist/
  artifacts:
    paths:
      - artifact-*.tgz
```

實際案例：作者指導團隊以 GitLab 收斂版控、CI、發行管理，先上最小管線與 artifacts。
實作環境：GitLab CE/EE 14+、Runner(Docker)、Node.js 18 或 .NET 6。
實測數據（參考值）：
- 改善前：導入週期>8 週；Build 成功率 < 60%
- 改善後：導入週期 2-3 週；Build 成功率 > 90%
- 改善幅度：導入時間縮短 60%+；Build 成功率提升 30%+

Learning Points（學習要點）
核心知識點：
- 問題驅動的工程導入法
- 最小可行管線（MVPipe）的設計
- 以指標衡量研發流程效果

技能要求：
- 必備技能：Git 基礎、CI 概念、YAML
- 進階技能：OKR/度量設計、流水線模板化

延伸思考：
- 可套用於測試平台、監控平台的逐步導入
- 風險：過度簡化導致不具延展性
- 優化：抽象共用管線模板、參數化配置

Practice Exercise（練習題）
- 基礎練習：為一個專案建立 MVPipe（build/test/artifacts）
- 進階練習：加入發布到內部套件倉庫的步驟
- 專案練習：設計兩專案共用的管線模板並量化成效

Assessment Criteria（評估標準）
- 功能完整性（40%）：能從 Commit 到 artifacts 的閉環
- 程式碼品質（30%）：可讀性、模板可重用性
- 效能優化（20%）：管線時間、快取使用
- 創新性（10%）：指標設計與可視化

---

## Case #2: 最小可行 CI/CD（版本控制+CI+發行管理）的落地

### Problem Statement（問題陳述）
**業務場景**：從零開始的新團隊，急需能持續交付可測版本，但沒有完整 CI/CD 基礎。團隊成員技術背景不一，需要一套能快速落地且未來可擴充的最小流程，確保每次提交都能產出可驗證的版本與可追溯的發布。
**技術挑戰**：如何以最少的規則，覆蓋版本控制、CI、發行管理三大能力，並讓團隊樂於採用。
**影響範圍**：無規範導致回歸錯誤頻繁、無法快速回退、版本不可追溯。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 缺乏最低限度的分支策略（develop/master）。
2. CI 無 artifacts 管理，後續無法穩定發布。
3. 無統一套件/映像倉庫，手動拷貝造成錯誤。

**深層原因**：
- 架構層面：未建立從 Commit 到可部署產物的閉環。
- 技術層面：缺少標準 YAML 模板與倉庫規劃。
- 流程層面：環境/分支/版本映射未定義。

### Solution Design（解決方案設計）
**解決策略**：定義 develop/master 分支與對應發布渠道（develop->beta、master->RC/RTM），建立標準 CI（build+test+artifacts），並將產物推送至內部套件或容器映像倉庫，形成最小閉環。

**實施步驟**：
1. 分支策略落地
- 實作細節：建立 develop/master，禁止直接推 master。
- 所需資源：Git 服務（GitLab）
- 預估時間：0.5 天

2. 標準 CI 模板
- 實作細節：建置 build/test/artifacts 三階段。
- 所需資源：Runner, YAML
- 預估時間：1 天

3. 發行管理（倉庫對接）
- 實作細節：Artifacts 上傳至 GitLab Package Registry 或 Docker Registry。
- 所需資源：GitLab Registry
- 預估時間：1 天

4. 規則文件與看板
- 實作細節：README/CONTRIBUTING、管線狀態徽章。
- 所需資源：GitLab badges
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```yaml
# 針對分支/渠道的規則
package:
  stage: package
  script:
    - ./scripts/pack.sh
  rules:
    - if: '$CI_COMMIT_BRANCH == "develop"'
      variables: { CHANNEL: "beta" }
    - if: '$CI_COMMIT_BRANCH == "master"'
      variables: { CHANNEL: "rtm" }
  artifacts:
    paths: [ "builds/$CHANNEL/*.tgz" ]
```

實際案例：文章建議 develop 發行 BETA、master 發行 RC/RTM，透過套件倉庫統一發布。
實作環境：GitLab + GitLab Registry、Ubuntu Runner。
實測數據（參考值）：
- 改善前：可測版本產出需 1-2 天
- 改善後：每次提交 10-20 分鐘內可得 beta 產物
- 改善幅度：交付時間縮短 90%+

Learning Points
- 分支與環境映射的重要性
- Artifacts 與套件/映像倉庫的關係
- 用 rules 對應不同渠道

技能要求
- 必備：Git、CI 基礎、Shell
- 進階：GitLab rules、Registry 權限管理

延伸思考
- 可拓展至多環境（QA/UAT/Prod）
- 風險：Artifacts 保留策略過短導致回溯困難
- 優化：加入 SBOM/簽章、供應鏈安全

Practice Exercise
- 基礎：建立 develop/master 與保護規則
- 進階：將產物發佈到 GitLab Package Registry
- 專案：多專案共用管線、渠道管理

Assessment Criteria
- 功能完整性：產物可追溯、可下載
- 程式碼品質：YAML 清晰、參數化
- 效能優化：快取與並行
- 創新性：自動化版本標示

---

## Case #3: 無事件觸發的老舊版控（日更型 Daily Build）土炮 CI

### Problem Statement（問題陳述）
**業務場景**：使用老舊 VSS（Visual SourceSafe）等不支援 Webhook 的版控系統，預算有限且無法立即升級，但仍需每日整合最新程式碼並驗證可編譯與基本可用性，作為團隊早晨整合測試的基礎。
**技術挑戰**：無法在提交時觸發 CI；需以排程方式自動化還原乾淨環境、抓取最新碼、建置與進行簡單冒煙測試。
**影響範圍**：若無日更驗證，團隊將無法得知前一天的整體品質是否可用，導致整合風險增加。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 版控無事件觸發能力（非服務化）。
2. 缺少自動化建置腳本與測試腳本。
3. 無集中產物存放與分享機制。

**深層原因**：
- 架構層面：缺乏可回復到乾淨狀態的可再現環境。
- 技術層面：腳本化與排程式自動化能力薄弱。
- 流程層面：缺少每日固定的整合節奏與責任人。

### Solution Design（解決方案設計）
**解決策略**：以排程器（Windows Task Scheduler）+ 虛擬機還原（或容器重建）+ 批次腳本，實現每天午夜自動更新程式碼、建置、部署到本機 IIS/服務，並執行 HTTP 冒煙測試，產出日更建置結果與共用產物。

**實施步驟**：
1. 準備乾淨 VM 模板
- 實作細節：建立可還原快照，內含建置工具與 VSS 客戶端。
- 所需資源：Hyper-V/Vmware/VirtualBox
- 預估時間：0.5-1 天

2. 排程腳本化
- 實作細節：每晚 1:00 還原快照、Get Latest、Build、Deploy。
- 所需資源：Windows Task Scheduler/cron、批次腳本
- 預估時間：1 天

3. 冒煙測試
- 實作細節：以 curl/PowerShell 測一組頁面/端點列表。
- 所需資源：curl、PowerShell
- 預估時間：0.5 天

4. 共用產物與報告
- 實作細節：打包 build 結果至共享目錄，寄送結果通知。
- 所需資源：檔案伺服器、SMTP
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```bat
:: daily-build.bat (Windows)
:: 1) Restore VM snapshot (示意，依虛擬化平台提供 CLI)
:: 2) VSS Get Latest
"c:\Program Files\VSS\ss.exe" Get $/Project -R -I- -Yuser,password

:: 3) Build
msbuild Project.sln /p:Configuration=Release

:: 4) Deploy to local IIS (示意)
xcopy /E /Y build\Release\* c:\inetpub\wwwroot\app\

:: 5) Smoke test
powershell -File smoke.ps1 > report.txt

:: 6) Copy artifacts and report
xcopy /Y build\Release\*.zip \\fileserver\builds\%date%
xcopy /Y report.txt \\fileserver\builds\%date%
```

實際案例：作者 2003 年以 VSS+Virtual PC 腳本化日更建置，早晨團隊可用於整合測試。
實作環境：Windows、VSS、VM 平台、IIS。
實測數據（參考值）：
- 改善前：合併日易破、整合不確定
- 改善後：每日可用建置一份；早會 5 分鐘內得知情況
- 改善幅度：整合風險顯著下降，回饋週期由天縮至日

Learning Points
- 在受限環境下以排程達成「準 CI」
- 冒煙測試對穩定度的價值
- 可再現環境的重要性

技能要求
- 必備：批次/PowerShell、MSBuild/IIS
- 進階：VM 自動化 CLI、基礎監控

延伸思考
- 可用容器取代 VM 快照
- 風險：排程失敗無監控
- 優化：加入失敗告警與簡易 Dashboard

Practice Exercise
- 基礎：撰寫冒煙測試腳本（curl 一組 URL）
- 進階：完成每日排程與報告
- 專案：建置一個「舊環境準 CI」方案

Assessment Criteria
- 功能完整性：每日產物、報告齊備
- 程式碼品質：腳本可讀、錯誤處理
- 效能優化：建置時間控制
- 創新性：在受限環境中的替代方案

---

## Case #4: 工具叢林收斂（GitLab 一站式替代重疊系統）

### Problem Statement（問題陳述）
**業務場景**：團隊同時使用 GitLab、TFS、Redmine、Jenkins 等多套工具，功能重疊（版控、CI、Issue 管理），維護成本高、流程割裂，成員學習負擔重，整體效率低下。
**技術挑戰**：如何在不中斷現行開發的前提下，收斂至單一平台（例如 GitLab）並維持未來擴展性。
**影響範圍**：工具成本、學習門檻、流程一致性、整合風險。
**複雜度評級**：高

### Root Cause Analysis（根因分析）
**直接原因**：
1. 歷史沿革引入多工具，缺乏收斂決策。
2. 每套工具各自建置流程，形成資訊孤島。
3. 維運與授權分散，權限與審計困難。

**深層原因**：
- 架構層面：缺失「一站式」平台策略與 Roadmap。
- 技術層面：資料遷移與相容性評估不足。
- 流程層面：流程標準化與培訓計畫缺位。

### Solution Design（解決方案設計）
**解決策略**：制定收斂準則（滿足三大基本能力+可擴充），選定 GitLab 作為主平台，分階段遷移版控、議題與管線；建立共用模板與權限模型；逐步淘汰其他工具，降低阻力與風險。

**實施步驟**：
1. 成本/風險評估與決策
- 實作細節：功能對照矩陣、授權成本、維運人力。
- 所需資源：會議與分析表
- 預估時間：1 週

2. POC 與範本建立
- 實作細節：挑 1-2 專案遷移，建立 CI 模板、Issue 模板。
- 所需資源：GitLab 專案與 Runner
- 預估時間：1-2 週

3. 分批遷移
- 實作細節：先版控，再 CI，再議題；每批配培訓。
- 所需資源：遷移腳本、教學資源
- 預估時間：4-8 週

4. 下架與優化
- 實作細節：停用重疊工具，強化審計與報表。
- 所需資源：權限盤點工具
- 預估時間：1-2 週

**關鍵程式碼/設定**：
```bash
# Git 遷移（TFS/Git->GitLab）
git clone --mirror <source_repo>
cd <repo>.git
git remote add gitlab <gitlab_repo_url>
git push gitlab --mirror
```

實際案例：作者將 GitLab、TFS、Jenkins 等重疊工具收斂至 GitLab。
實作環境：GitLab CE/EE、TFS、Jenkins。
實測數據（參考值）：
- 改善前：工具數量 3-4 套，學習週期 4-6 週
- 改善後：主平台 1 套，學習週期 1-2 週
- 改善幅度：學習與維運成本下降 50-70%

Learning Points
- 以能力而非品牌評估工具
- 漸進式收斂的風險控制
- 權限與審計的集中化價值

技能要求
- 必備：Git 遷移、管線模板
- 進階：權限模型、資料遷移策略

延伸思考
- 可擴展至 Wiki、容器登錄、包管理
- 風險：遷移中斷服務
- 優化：自動化遷移與回退計畫

Practice Exercise
- 基礎：將一個 Git 專案遷移到 GitLab
- 進階：建立共用 CI 模板並在兩專案落地
- 專案：以 GitLab 替換 Jenkins 專案管線

Assessment Criteria
- 功能完整性：遷移完整與可用
- 程式碼品質：自動化腳本穩健
- 效能優化：管線耗時
- 創新性：可重用遷移框架

---

## Case #5: Git Flow 精簡版（僅 master/develop）快速上手

### Problem Statement（問題陳述）
**業務場景**：團隊分支混亂，開發與上線版本無法區隔，回溯困難。希望導入 Git Flow，但擔心複雜度，期望從最少分支開始有效管控。
**技術挑戰**：在不增加太多成本下，建立可用的分支與發布策略。
**影響範圍**：版本混亂導致回退困難、熱修補無法準確定位。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 無統一分支策略。
2. 缺乏保護分支與合併規則。
3. 沒有標準化 Tag/版本規則。

**深層原因**：
- 架構層面：發行管理缺失。
- 技術層面：Git Flow 概念未被理解。
- 流程層面：Code Review 與 Merge 條件鬆散。

### Solution Design（解決方案設計）
**解決策略**：導入 Git Flow 精簡版，僅保留 master（已發布/穩定）與 develop（開發）分支；master 受保護、僅允許 MR；Tag 採 SemVer；配合 CI 規則映射發行渠道。

**實施步驟**：
1. 建立與保護分支
- 實作細節：保護 master，禁止直接 push。
- 所需資源：GitLab 保護規則
- 預估時間：0.5 天

2. 合併規則與檢查
- 實作細節：MR 需通過 CI 才可合併；至少 1 Reviewer。
- 所需資源：MR 模板、管線設定
- 預估時間：0.5 天

3. 版本與 Tag
- 實作細節：SemVer 與預發版標記（-beta、-rc）。
- 所需資源：版本腳本
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```bash
# 初始化精簡 Git Flow
git checkout -b develop
git checkout -b master
git push -u origin develop
git push -u origin master

# 版本標記
git tag v1.2.0
git push origin v1.2.0
```

實際案例：作者建議新手團隊先只用 master/develop，待上手再加 feature/release/hotfix。
實作環境：GitLab/GitHub/Gitea 皆可。
實測數據（參考值）：
- 改善前：回溯時間不可控
- 改善後：回溯精準，回退平均 < 10 分鐘
- 改善幅度：回溯效率提升 80%+

Learning Points
- 「少即是多」的分支策略
- 保護分支與 MR 守門
- Tag 與發行對應

技能要求
- 必備：Git、MR 流程
- 進階：合併條件、自動化版本

延伸思考
- 後續導入 feature/release/hotfix
- 風險：過度簡化不適合複雜產品
- 優化：加上變更日誌自動化

Practice Exercise
- 基礎：建立 master/develop 與保護規則
- 進階：設定「通過 CI 才可合併」
- 專案：以此策略交付一個迭代版本

Assessment Criteria
- 功能完整性：分支與規則正確
- 程式碼品質：MR 模板規範
- 效能優化：降低衝突發生
- 創新性：規則自動化腳本

---

## Case #6: Git Flow 進階（features/release/hotfix）與回流策略

### Problem Statement（問題陳述）
**業務場景**：產品複雜度提升，需要對功能開發、釋出候選版、緊急修補有明確隔離與回流策略，避免長期分支與回合併災難。
**技術挑戰**：維持高可用性與高節奏開發並行，確保修補能正確回流 develop。
**影響範圍**：發行節奏、品質與可預測性。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 功能分支與主線污染。
2. 缺乏 release 分支與 RC 管理。
3. 熱修補無法回流 develop。

**深層原因**：
- 架構層面：發行節奏未階段化。
- 技術層面：分支與合併策略不熟練。
- 流程層面：缺少標準作業與檢查清單。

### Solution Design（解決方案設計）
**解決策略**：導入 feature/release/hotfix 分支；release 分支凍結功能只修錯；hotfix 從 master 切出、修畢回流 master+develop；搭配 CI/CD 定義不同渠道與自動化測試閘門。

**實施步驟**：
1. 分支策略訓練與 SOP
- 實作細節：教學與手冊（含圖示）。
- 所需資源：Wiki、工作坊
- 預估時間：0.5 天

2. 模板化腳本
- 實作細節：建立 git flow alias/腳本。
- 所需資源：Shell/PowerShell
- 預估時間：0.5 天

3. 管線對應渠道
- 實作細節：release -> RC 測試套件增強；master -> RTM。
- 所需資源：CI rules
- 預估時間：1 天

**關鍵程式碼/設定**：
```bash
# feature 開發
git checkout -b feature/awesome develop
# 完成後
git checkout develop && git merge --no-ff feature/awesome
git branch -d feature/awesome

# 建 release
git checkout -b release/1.2.0 develop
# 修畢 -> RC 測試通過後
git checkout master && git merge --no-ff release/1.2.0
git tag v1.2.0
git checkout develop && git merge --no-ff release/1.2.0
git branch -d release/1.2.0

# hotfix
git checkout -b hotfix/1.2.1 master
# 修畢
git checkout master && git merge --no-ff hotfix/1.2.1 && git tag v1.2.1
git checkout develop && git merge --no-ff hotfix/1.2.1
git branch -d hotfix/1.2.1
```

實際案例：作者建議先理解完整 Git Flow，再選擇性導入，以免砍錯關鍵環節。
實作環境：標準 Git 平台。
實測數據（參考值）：
- 改善前：修補遺漏回流導致重複缺陷
- 改善後：hotfix 回流率 100%，重複缺陷下降 70%+
- 改善幅度：可預測性顯著提升

Learning Points
- 階段化分支的價值
- 無快轉合併（--no-ff）的可追溯性
- 回流策略的重要性

技能要求
- 必備：Git 進階、合併策略
- 進階：自動化版本/變更日誌

延伸思考
- 依產品特性調整分支數量
- 風險：分支過多管理負擔上升
- 優化：機器人協助建立/關閉分支

Practice Exercise
- 基礎：模擬一次 release 分支流程
- 進階：執行一次 hotfix 並回流
- 專案：將 RC 管線與 RTM 管線分離

Assessment Criteria
- 功能完整性：流程符合規範
- 程式碼品質：合併紀錄清晰
- 效能優化：衝突降低
- 創新性：腳本自動化

---

## Case #7: 單元測試導入策略（新專案 TDD、舊專案選擇性補測）

### Problem Statement（問題陳述）
**業務場景**：舊專案缺乏單元測試，新專案希望納入 TDD，但人力有限且既有代碼難測。需制定務實策略，避免「為測試而測試」。
**技術挑戰**：如何在短期內提升測試產出與價值，並導入 CI 測試關卡。
**影響範圍**：缺陷率、回 regresion 風險、開發效率。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 舊代碼耦合高，難以撰寫單元測試。
2. 測試文化缺乏，無標準。
3. CI 無測試關卡與報告。

**深層原因**：
- 架構層面：未以可測性設計。
- 技術層面：Mock/Stubs 等測試技術不足。
- 流程層面：未把測試當交付的一部分。

### Solution Design（解決方案設計）
**解決策略**：新專案採 TDD；舊專案優先補「Bug 重現測試」「API 合約測試」「核心 Library 範例測試」。在 CI 中強制單元測試通過方可合併，逐步引入覆蓋率門檻。

**實施步驟**：
1. 測試策略宣導與樣板
- 實作細節：提供不同測試類型的模板。
- 所需資源：測試框架（Jest/xUnit）
- 預估時間：0.5 天

2. CI 測試與報告
- 實作細節：JUnit/coverage 報告上傳、顯示。
- 所需資源：GitLab 測試報告
- 預估時間：0.5 天

3. 門檻與緩衝
- 實作細節：先僅要求測試存在，後逐步提高覆蓋率（例如 30%->50%）。
- 所需資源：覆蓋率工具
- 預估時間：持續

**關鍵程式碼/設定**：
```yaml
unit_test:
  stage: test
  image: node:18
  script:
    - npm ci
    - npm run test:ci -- --coverage --reporters=default --reporters=jest-junit
  artifacts:
    reports:
      junit: junit.xml
    paths:
      - coverage/
```

實際案例：作者建議以 TDD 啟動新專案，舊專案以高價值測試優先（bug 重現、API 規格）。
實作環境：GitLab CI、Jest/xUnit。
實測數據（參考值）：
- 改善前：回歸缺陷頻發
- 改善後：重複缺陷下降 40-60%；平均修復時間縮短 30%+
- 改善幅度：品質與效率雙升

Learning Points
- 測試類型分層與取捨
- CI 測試報告與門檻設計
- 以測試推動設計改善

技能要求
- 必備：測試框架、Mock
- 進階：契約測試、消費者驅動合約（CDC）

延伸思考
- 可引入靜態掃描與風險熱點
- 風險：覆蓋率指標被「刷高」
- 優化：以缺陷預防為導向的測試設計

Practice Exercise
- 基礎：為一函式撰寫 TDD 測試
- 進階：為一 API 建立契約測試
- 專案：為舊專案補齊 bug 重現測試池

Assessment Criteria
- 功能完整性：測試通過與報告齊備
- 程式碼品質：測試可讀、維護性
- 效能優化：測試時間合理
- 創新性：契約測試實踐

---

## Case #8: CI 產物管理（Artifacts）與保留策略

### Problem Statement（問題陳述）
**業務場景**：CI 每次重建導致結果不一致，CD 階段無法直接取用已驗證的產物，回溯與比對困難。
**技術挑戰**：如何確保「一次建置，多處部署」，並有清晰的保留與清理策略。
**影響範圍**：發布一致性、可追溯性、儲存成本。
**複雜度評級**：低

### Root Cause Analysis
**直接原因**：
1. 無 artifacts 導致每環境重建。
2. 缺乏統一命名與版本規則。
3. 無保留/過期策略。

**深層原因**：
- 架構層面：Build 與 Deploy 未解耦。
- 技術層面：管線未輸出標準產物。
- 流程層面：缺少產物管理規範。

### Solution Design
**解決策略**：在 CI 中標準化輸出 artifacts（含版本、Meta 資訊），設定過期時間與下載路徑，並與套件/映像倉庫對接，形成「一次建置，多處部署」。

**實施步驟**：
1. 定義產物格式與命名
- 實作細節：artifact-<semver>-<commit>.tgz
- 資源：規範文件
- 時間：0.5 天

2. 管線產出 artifacts
- 實作細節：設定 paths、expire_in。
- 資源：YAML
- 時間：0.5 天

3. 對接倉庫
- 實作細節：發佈至 Package/Registry。
- 資源：倉庫憑證
- 時間：0.5 天

**關鍵程式碼/設定**：
```yaml
build:
  stage: build
  script: [ "npm ci", "npm run build" ]
  artifacts:
    name: "artifact-$CI_COMMIT_TAG-$CI_COMMIT_SHORT_SHA"
    paths: [ "dist/" ]
    expire_in: 14 days
```

實際案例：作者強調 manage artifacts 是導入初期的關鍵之一。
實作環境：GitLab CI。
實測數據（參考值）：
- 改善前：多環境重建，故障難回溯
- 改善後：可直接部署同一產物，回溯時間 < 10 分鐘
- 改善幅度：一致性顯著提升

Learning Points
- Build/Deploy 解耦
- 命名與保留策略
- 與倉庫整合

技能要求
- 必備：YAML、包裝/打包
- 進階：SBOM、產物簽章

Practice Exercise
- 基礎：輸出 artifacts
- 進階：命名規則與過期策略
- 專案：統一多專案 artifacts 規範

---

## Case #9: 發行管理用套件管理機制（apt/npm/nuget）與 SemVer

### Problem Statement
**業務場景**：CD 難以一次到位，需先以套件管理簡化部署；希望用標準化版本與依賴管理，減少手動錯誤。
**技術挑戰**：確保版本可追溯、相依可解決、團隊能快速上手。
**影響範圍**：部署錯誤率、回退時間、依賴一致性。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 手動下載與拷貝造成錯誤。
2. 無 SemVer 導致相容性混亂。
3. 依賴未集中管理。

**深層原因**：
- 架構層面：缺乏內部倉庫策略。
- 技術層面：未整合發佈至倉庫的步驟。
- 流程層面：版本命名與升版缺乏規範。

### Solution Design
**解決策略**：以 npm/nuget 等作為內部發行管道，規範 SemVer 2.0 與預發版標註（-beta/-rc），CI 於分支/Tag 觸發發佈至內部倉庫，作為手動或半自動部署的唯一來源。

**實施步驟**：
1. 倉庫建置
- 實作細節：GitLab Package Registry/Artifactory。
- 資源：倉庫服務
- 時間：0.5 天

2. 發佈腳本
- 實作細節：npm publish/nuget push，分渠道。
- 資源：憑證、腳本
- 時間：0.5 天

3. 版本規範
- 實作細節：SemVer 與預發版（-beta/-rc）。
- 資源：規範文件
- 時間：0.5 天

**關鍵程式碼/設定**：
```bash
# npm 發佈（CI 內）
npm version 1.2.0-rc.1 --no-git-tag-version
npm publish --registry $NPM_REGISTRY --tag rc

# nuget 發佈
dotnet pack -c Release -p:PackageVersion=1.2.0
dotnet nuget push bin/Release/*.nupkg --source $NUGET_FEED --api-key $API_KEY
```

實際案例：作者建議在 CD 未完成前，先用套件管理達成穩定發行。
實作環境：GitLab Package Registry、npm/nuget。
實測數據（參考值）：
- 改善前：部署錯誤率高
- 改善後：透過倉庫安裝，錯誤率下降 60-80%
- 改善幅度：部署可靠度大幅提升

Learning Points
- SemVer 與預發版
- 倉庫化發行的價值
- 依賴管理與可追溯性

技能要求
- 必備：npm/nuget、版本規劃
- 進階：私有倉庫、權限控管

Practice Exercise
- 基礎：將庫發佈至私有 npm/nuget
- 進階：分渠道（beta/rc）管理
- 專案：以套件管理支援半自動部署

---

## Case #10: 容器化網站/服務，統一用映像倉庫管理 CD

### Problem Statement
**業務場景**：網站與服務無合適套件管理，部署流程繁雜且環境不一致；希望用容器化統一打包並透過映像倉庫管理。
**技術挑戰**：建立 Docker 打包、設定變數/密鑰與多環境部署策略。
**影響範圍**：環境一致性、部署速度、安全性。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 缺乏標準打包格式。
2. 環境配置四處散落。
3. 映像不可追溯。

**深層原因**：
- 架構層面：未導入容器與映像倉庫。
- 技術層面：Dockerfile/多階段建置缺乏。
- 流程層面：缺少管線到部署的一致策略。

### Solution Design
**解決策略**：以 Docker 多階段建置打包應用，推送至 GitLab Container Registry；以 Tag 映射版本與渠道；環境設定透過環境變數/Secrets；部署由運維拉取指定 Tag 版本。

**實施步驟**：
1. Docker 化
- 實作細節：Dockerfile 多階段建置、健康檢查。
- 資源：Docker
- 時間：1-2 天

2. CI 建像與推送
- 實作細節：以 Commit SHA/Tag 標示。
- 資源：GitLab CI、Registry
- 時間：0.5 天

3. 部署流程
- 實作細節：環境變數/Secrets、滾動更新/回滾。
- 資源：Docker Compose/K8s
- 時間：1-2 天

**關鍵程式碼/設定**：
```dockerfile
# Dockerfile (multi-stage)
FROM node:18 AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci && npm run build

FROM nginx:stable
COPY --from=build /app/dist /usr/share/nginx/html
HEALTHCHECK CMD curl -f http://localhost/ || exit 1
```

```yaml
# .gitlab-ci.yml 片段
docker_build:
  image: docker:24
  services: [ docker:24-dind ]
  script:
    - docker login $CI_REGISTRY -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA
```

實際案例：作者建議網站/服務以容器化，統一由 Registry 分發。
實作環境：Docker、GitLab Registry。
實測數據（參考值）：
- 改善前：部署需 2-4 小時
- 改善後：拉取映像並啟動 10-30 分鐘
- 改善幅度：部署時間縮短 75%+

Learning Points
- 多階段建置與體積優化
- Tag 管理與回滾策略
- 環境變數與 Secrets 管理

技能要求
- 必備：Docker 基礎、CI 整合
- 進階：Compose/K8s 滾更、探針

Practice Exercise
- 基礎：為網站寫 Dockerfile 並跑起來
- 進階：CI 自動建像推送
- 專案：完成一套「拉像即部署」流程

---

## Case #11: 禁止開發者本機編譯直上線（以 CI 產物與最小權限落實資安）

### Problem Statement
**業務場景**：缺乏 CI/CD 時，開發者常在本機編譯後直接上傳 Production，無可追溯，存在重大資安與合規風險（惡意後門、未經授權變更）。
**技術挑戰**：建立以 CI 產物為唯一部署來源，並限制生產環境權限與審計。
**影響範圍**：資安、合規、營運風險。
**複雜度評級**：高

### Root Cause Analysis
**直接原因**：
1. 無中央建置產物。
2. 開發者對生產環境擁有過高權限。
3. 無審計與追蹤。

**深層原因**：
- 架構層面：流程未形成閉環。
- 技術層面：缺乏簽章/哈希驗證。
- 流程層面：權限分離與審批缺失。

### Solution Design
**解決策略**：以 CI 為唯一建置源；部署只允許來自 Registry/Package 的簽章產物；開發者無 Production 登入權；生產部署需審批與審計紀錄；加入哈希/簽章驗證。

**實施步驟**：
1. 權限治理
- 實作細節：開發者移除 Prod 登入；只允許運維與 CD Bot。
- 資源：IAM/AD
- 時間：0.5 天

2. 來源限制
- 實作細節：部署腳本只接受 Registry 來源，驗證哈希/簽章。
- 資源：Hash/Sign 工具
- 時間：1 天

3. 審批與審計
- 實作細節：GitLab Environments Approval，審批紀錄。
- 資源：GitLab EE 或外部工單
- 時間：0.5 天

**關鍵程式碼/設定**：
```yaml
deploy_prod:
  stage: deploy
  environment:
    name: production
    url: https://app.example.com
  rules:
    - if: '$CI_COMMIT_TAG'   # 只允許標籤的正式版進 Prod
  when: manual               # 需人工審批
  script:
    - ./scripts/verify_signature.sh artifact.tgz
    - ./scripts/deploy.sh artifact.tgz
  approvals:
    required: 1              # EE 功能，或用外部審批流程替代
```

實際案例：作者以資安風險說明 CI/CD 的價值與必要性。
實作環境：GitLab、簽章工具（cosign/gpg）。
實測數據（參考值）：
- 改善前：未授權變更難追溯
- 改善後：本機直部署事件降為 0；所有部署可稽核
- 改善幅度：重大風險清除

Learning Points
- 「只從 CI 產物部署」的治理邏輯
- 權限最小化與審批
- 產物簽章與驗證

技能要求
- 必備：CI/CD、權限管理
- 進階：簽章與供應鏈安全

Practice Exercise
- 基礎：加入 Prod 審批步驟
- 進階：實作產物簽章與驗證
- 專案：制定部署治理準則與審計流程

---

## Case #12: 管線可視化與通知（Pipeline、Badge、訊息整合）

### Problem Statement
**業務場景**：團隊對當前品質狀態無感，錯過失敗通知，導致回饋遲緩。
**技術挑戰**：建立可視化與主動通知，提升回饋速度。
**影響範圍**：修復時間、跨團隊協作效率。
**複雜度評級**：低

### Root Cause Analysis
**直接原因**：
1. 無統一查看處。
2. 無通知策略。
3. 多專案狀態分散。

**深層原因**：
- 架構層面：缺乏狀態匯總。
- 技術層面：未善用內建可視化。
- 流程層面：未設定響應 SLO。

### Solution Design
**解決策略**：啟用 GitLab Pipeline 頁面、專案徽章、Email/Slack/App 通知；在首頁建立專案燈號看板；定義回應 SLO。

**實施步驟**：
1. 啟用通知
- 實作細節：設定 Email/Slack Webhook。
- 資源：Slack/Teams
- 時間：0.5 天

2. 連結徽章
- 實作細節：README 放上 Pipeline/coverage 徽章。
- 資源：GitLab badges
- 時間：0.5 天

3. 看板與 SLO
- 實作細節：建立失敗響應 SLO（如 30 分鐘內回應）。
- 資源：Wiki
- 時間：0.5 天

**關鍵程式碼/設定**：
```md
![pipeline status](https://gitlab.com/<group>/<project>/badges/master/pipeline.svg)
![coverage](https://gitlab.com/<group>/<project>/badges/master/coverage.svg)
```

實際案例：作者指出 GitLab pipeline 與通知能確保第一時間掌握品質。
實作環境：GitLab、Slack/Teams。
實測數據（參考值）：
- 改善前：失敗發現需數小時
- 改善後：通知即時，平均回應 < 15 分鐘
- 改善幅度：MTTR 下降 50-70%

Learning Points
- 可視化與行為改變
- 通知與雜訊控制
- SLO 與責任到人

技能要求
- 必備：平台設定
- 進階：訊息格式化與 ChatOps

Practice Exercise
- 基礎：為專案加入徽章
- 進階：整合 Slack 通知
- 專案：建立跨專案燈號看板

---

## Case #13: 分支-環境-發布渠道映射（develop->beta, master->RC/RTM）

### Problem Statement
**業務場景**：不同分支產生的版本在環境與標籤上無規範，導致測試/上線混亂。
**技術挑戰**：建立清晰映射，讓測試與運維明白來源與目的。
**影響範圍**：測試準確性、上線穩定性。
**複雜度評級**：低

### Root Cause Analysis
**直接原因**：
1. 沒有映射表。
2. 發佈標籤混用。
3. 測試版本與上線版本混淆。

**深層原因**：
- 架構層面：沒有渠道設計。
- 技術層面：管線規則未體現映射。
- 流程層面：測試與運維交接模糊。

### Solution Design
**解決策略**：規範 develop->beta，master->RC/RTM；管線 rules/only 依分支決定標籤與發布行為；文件化與看板同步可視化。

**實施步驟**：
1. 制定映射
- 實作細節：Wiki 與 README。
- 時間：0.5 天
2. 規則落地
- 實作細節：CI rules 依分支設定 CHANNEL。
- 時間：0.5 天
3. 可視化
- 實作細節：Badge 與看板顯示渠道狀態。
- 時間：0.5 天

**關鍵程式碼/設定**：
```yaml
rules:
  - if: '$CI_COMMIT_BRANCH == "develop"'
    variables: { CHANNEL: "beta" }
  - if: '$CI_COMMIT_BRANCH == "master"'
    variables: { CHANNEL: "rc" }   # 發 RC，打 Tag 後為 RTM
```

實際案例：文章建議依分支設定不同發行方式與規則。
實作環境：GitLab CI。
實測數據（參考值）：
- 改善前：渠道混亂
- 改善後：測試與上線一目了然
- 改善幅度：交付錯版率下降 80%+

Learning Points
- 映射的清晰度決定效率
- 利用 rules 參數化渠道
- 文檔與可視化同步

Practice Exercise
- 基礎：建立映射文件
- 進階：實作 rules 管道
- 專案：跨多專案渠道統一

---

## Case #14: 半自動 CD：以套件/檔案伺服器簡化手動部署

### Problem Statement
**業務場景**：無法短期內完成全自動 CD，但手動步驟複雜易錯，需有穩定半自動流程。
**技術挑戰**：如何縮短步驟且可稽核。
**影響範圍**：錯誤率、效率與安全。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 手動步驟繁多不一致。
2. 無唯一來源。
3. 無稽核紀錄。

**深層原因**：
- 架構層面：未標準化部署包。
- 技術層面：缺部署腳本與清單。
- 流程層面：缺檢查清單與回報。

### Solution Design
**解決策略**：以 CI 產生標準部署包，存於套件倉庫或檔案伺服器；制定簡單可複用的部署腳本與 Checklist；保留部署紀錄與回報。

**實施步驟**：
1. 標準部署包
- 實作細節：包含版本資訊與校驗。
- 時間：0.5 天

2. 部署腳本與 Checklist
- 實作細節：一鍵解壓、備份、切換。
- 時間：1 天

3. 稽核與回報
- 實作細節：部署紀錄上傳、通知。
- 時間：0.5 天

**關鍵程式碼/設定**：
```bash
# deploy.sh
set -e
ARTIFACT=$1
sha256sum -c $ARTIFACT.sha256
timestamp=$(date +%Y%m%d%H%M)
cp -r /srv/app /srv/app_bak_$timestamp
tar -xzf $ARTIFACT -C /srv/app
systemctl restart app.service
echo "$ARTIFACT deployed at $timestamp" >> /var/log/deploy.log
```

實際案例：作者建議「做不到全自動，就半自動但要減錯」。
實作環境：Linux/File Server/Package Registry。
實測數據（參考值）：
- 改善前：手動 20+ 步驟
- 改善後：3-5 步（拉包、校驗、腳本）
- 改善幅度：錯誤率下降 70%+

---

## Case #15: SemVer 與預發版標註（BETA/RC/RTM）治理

### Problem Statement
**業務場景**：版本號混亂，無法一眼看出相容性與穩定程度；需有統一版本規範。
**技術挑戰**：實作一致的升版流程與預發版標註。
**影響範圍**：相容性判斷、依賴管理、測試與上線節奏。
**複雜度評級**：低

### Root Cause Analysis
**直接原因**：
1. 無版本規範。
2. 人工命名錯誤。
3. 測試/運維無從判斷穩定度。

**深層原因**：
- 架構層面：未將版本當契約。
- 技術層面：缺少版本工具鏈。
- 流程層面：升版與標註未自動化。

### Solution Design
**解決策略**：採 SemVer 2.0，使用 -beta/-rc 作為預發標註；以腳本自動升版與打標，並在 CI 中統一注入版本資訊。

**實施步驟**：
1. 規範制定
- 實作細節：主次修定義與預發規則。
- 時間：0.5 天
2. 自動化腳本
- 實作細節：npm version/腳本打標。
- 時間：0.5 天
3. CI 注入版本
- 實作細節：環境變數與輸出文件。
- 時間：0.5 天

**關鍵程式碼/設定**：
```bash
# bump.sh
# 用法：./bump.sh minor rc
type=$1    # major/minor/patch
pre=$2     # rc/beta/none
npm version $type --no-git-tag-version
ver=$(node -p "require('./package.json').version")
[ "$pre" != "none" ] && ver="${ver}-${pre}.1"
git commit -am "chore: release $ver"
git tag "v$ver"
git push && git push --tags
```

實際案例：作者建議依 SemVer 並標註 BETA/RC/RTM。
實作環境：任意語言/平台。
實測數據（參考值）：
- 改善前：版本混用
- 改善後：一眼辨識穩定度與相容性
- 改善幅度：協作效率顯著提升

---

## Case #16: 無單元測試時的冒煙測試（HTTP 頁面/端點清單）

### Problem Statement
**業務場景**：早期或舊系統缺乏單元測試，仍需最基本品質防線。
**技術挑戰**：快速建立低成本、可自動化的冒煙測試。
**影響範圍**：線上故障率、回歸風險。
**複雜度評級**：低

### Root Cause Analysis
**直接原因**：
1. 單元測試缺失。
2. 介面測試未建立。
3. 無自動驗證。

**深層原因**：
- 架構層面：未以可測性設計。
- 技術層面：缺乏自動化測試工具使用。
- 流程層面：無最小測試清單。

### Solution Design
**解決策略**：維護一份關鍵頁面/端點清單，於 CI/排程以 curl/newman 逐一檢查狀態與關鍵字，快速標紅異常，建立最小防線。

**實施步驟**：
1. 清單建立
- 實作細節：URL+預期狀態/關鍵字。
- 時間：0.5 天
2. 腳本化
- 實作細節：bash/powershell 實作探測。
- 時間：0.5 天
3. CI 接入
- 實作細節：失敗即紅燈、報告產出。
- 時間：0.5 天

**關鍵程式碼/設定**：
```bash
# smoke.sh
set -e
while read url expect; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "$url")
  [ "$code" = "$expect" ] || { echo "FAIL $url"; exit 1; }
done <<EOF
https://app.example.com/health 200
https://app.example.com/login 200
EOF
```

實際案例：作者 2003 年以 HTTP 客戶端點擊頁面作為簡易測試。
實作環境：任意。
實測數據（參考值）：
- 改善前：基本功能失效未即時發現
- 改善後：關鍵頁面故障可即時警示
- 改善幅度：早期攔截率顯著上升

---

## Case #17: 工具替換決策框架（先善用舊工具，再考慮更換）

### Problem Statement
**業務場景**：團隊常陷入「工具控」，動輒更換系統，導致成本高、學習曲線陡、交付受阻。
**技術挑戰**：建立一套評估與決策框架，避免頻繁、非必要替換。
**影響範圍**：成本、風險、效率。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 缺乏替換準則。
2. 忽視「人」與「流程」因素。
3. 成本估算不足。

**深層原因**：
- 架構層面：未以能力需求出發。
- 技術層面：相容性與遷移成本評估缺失。
- 流程層面：培訓與支持計畫不足。

### Solution Design
**解決策略**：制定替換準則（重大缺口、已掌握 80% 功能仍不能滿足、明確長期收益），優先「找對人用好工具」；能沿用則沿用；必要時再更換，分階段遷移。

**實施步驟**：
1. 差距分析
- 實作細節：功能差距、實作難度、成本。
- 時間：1-2 天
2. POC 與效益試算
- 實作細節：小範圍驗證與量化。
- 時間：1 週
3. 決策與路線圖
- 實作細節：分波次遷移、培訓與支持。
- 時間：1-2 週

**關鍵程式碼/設定**：
```md
決策檢核清單（節選）
- 需求是否確定與穩定？
- 既有工具是否能達成？缺口大小？
- 遷移成本（人/時/風險）與回收期？
- 培訓與維運是否可承擔？
```

實際案例：作者強調先善用現有（如 GitLab）避免多香爐多隻鬼。
實作環境：不限。
實測數據（參考值）：
- 改善前：每年 1-2 次大替換
- 改善後：3 年僅 0-1 次必要替換
- 改善幅度：風險與成本顯著下降

---

案例分類
1) 按難度分類
- 入門級：Case 5, 8, 12, 13, 15, 16
- 中級：Case 1, 2, 3, 7, 9, 10, 14, 17
- 高級：Case 4, 6, 11

2) 按技術領域分類
- 架構設計類：Case 1, 2, 4, 6, 11, 13, 17
- 效能優化類：Case 8, 10, 12, 14
- 整合開發類：Case 2, 4, 9, 10, 15
- 除錯診斷類：Case 3, 7, 16
- 安全防護類：Case 11, 15

3) 按學習目標分類
- 概念理解型：Case 1, 5, 13, 15, 17
- 技能練習型：Case 2, 7, 8, 10, 16
- 問題結構化解決型：Case 3, 4, 6, 11, 14
- 創新應用型：Case 9, 12

案例學習路徑建議
- 先學哪些案例？
  - 入門基礎（觀念+最小落地）：Case 1（問題導向）、Case 5（精簡 Git Flow）、Case 2（最小 CI/CD 閉環）、Case 8（Artifacts）
  - 基礎品質與可視化：Case 7（單元測試策略）、Case 16（冒煙測試）、Case 12（可視化與通知）
- 依賴關係
  - Case 13（分支-渠道映射）依賴 Case 5
  - Case 9（套件發行）依賴 Case 2、8、15
  - Case 10（容器化）依賴 Case 2、8、15
  - Case 11（資安治理）依賴 Case 2、8、9/10、13
  - Case 6（進階 Git Flow）依賴 Case 5
  - Case 4（工具收斂）依賴 Case 1（價值導向）
- 完整學習路徑建議
  1. 概念與最小落地：Case 1 → Case 5 → Case 2 → Case 8
  2. 品質防線與回饋：Case 7 → Case 16 → Case 12
  3. 發行與版本治理：Case 15 → Case 13 → Case 9
  4. 容器化與一致部署：Case 10 →（可選）Case 14 半自動 CD
  5. 安全與合規落實：Case 11
  6. 工具與流程進化：Case 6（進階 Git Flow）→ Case 4（工具收斂）→ Case 17（替換決策）

說明
- 各案例的「實測數據」為導入專案常見參考值，用於教學與評估目標設定，實作時應依團隊基線重測與校準。