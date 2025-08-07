# 架構師觀點: 你需要什麼樣的 CI / CD ?  

# 問題／解決方案 (Problem/Solution)

## Problem: 工具先行、目的缺位，CI/CD 專案常常「一擺就死」

**Problem**:  
團隊一聽到 CI / CD、DevOps、Micro-services 等熱門關鍵字就急著「買工具、裝服務」，結果真正開始要求流程（branch 規範、測試覆蓋率、佈署規則）時，內部成員反而強烈反彈，導入專案動輒失敗或無疾而終。  

**Root Cause**:  
1. 技術／框架迷思（工具控）盛行，討論時先問「用哪一套」而非「要解決什麼」。  
2. 面試、社群輿論把「有 CI/CD」當成指標，卻未同步累積落地經驗。  
3. 缺乏架構師或 Team Leader 從「需求」反推「流程」與「工具」的系統化思考。  

**Solution**:  
採「需求驅動」方式啟動 CI/CD：  
a. 先盤點團隊真正痛點（交付速度、品質不穩、佈署出錯…）。  
b. 讓帶頭者（架構師、Tech Lead）完整了解 CI/CD 每一站要解決的問題，再決定何時引工具。  
c. 將 CI/CD 分解為最小可行流程（版本控制、持續整合、發行管理）逐段推行，而非一次要求全套。  

**Cases 1**:  
• 現場面試工程師大量詢問「有無 CI/CD？用哪套？」；進公司後卻對 commit 規範、測試門檻產生排斥。  
• 透過「先講需求再講工具」的 workshop 讓團隊理解痛點與收益，反彈人數明顯下降，導入計畫得以繼續。  

---

## Problem: 從 0 到 1 建置 CI/CD，流程過度龐大導致推行卡關

**Problem**:  
完全沒有任何自動化與版本控管的新團隊，參考網路完整 CI/CD 範例時，發現涵蓋數十個步驟、數種環境，一開始就想「一次到位」，結果導入計畫超時、超支、最後被迫放棄。  

**Root Cause**:  
1. 參考案例多數來自成熟或大規模企業，流程過度完整。  
2. 團隊缺乏階段性目標與里程碑，導入門檻過高。  

**Solution**:  
提出「Minimum Viable CI/CD」(MVCICD) 觀念，只做三件事：  
1) 版本控制：所有原始碼都進 Git（或其他 SCM）並能追溯。  
2) 持續整合：一條 Pipeline 完成 Build＋Unit Test＋Artifacts 產生。  
3) 發行管理：把 Build 產物推送到可追蹤的 Package Manager (檔案 / Registry)。  

先保證每天都能「拉到可編譯且測試通過」的成品，再循序擴大到自動部署、靜態掃描、E2E 測試等下一層。  

**Cases 1**:  
• 2003 年作者以 VSS＋批次 Script＋Virtual PC 做出「Daily Build」，雖僅每天半夜跑一次，但已能確保程式可編譯並部署到 Dev VM，隔天即可整合測試。  
• 2017 年導入 MVCICD 後，團隊每天早上都可以先看 GitLab Pipeline 全綠勾，失敗立即收到通知；兩週內就消除了「合併後才發現不能編譯」的情況。  

---

## Problem: 工具疊床架屋，重複功能造成維運與學習負擔

**Problem**:  
同一團隊同時使用 GitLab、TFS、Redmine、Jenkins … 等多套系統，功能高度重疊（issue tracking、repository、CI server），造成：  
• 成員不知道該在哪一套開分支／送 Pull Request。  
• 維運人員需要為多套系統升級、備份、打補丁。  

**Root Cause**:  
1. 每遇新需求就「再裝一套系統」；缺乏整合藍圖。  
2. 學習曲線拖累導入速度，成員排斥再學新工具。  

**Solution**:  
「砍系統而非再加系統」，統整到單一平台：  
• 以 GitLab 取代 Git + Issue Tracking + Jenkins，利用內建 CI/CD 功能。  
• 原 Jenkins Pipeline、TFS Build Script 逐步遷移成 .gitlab-ci.yml。  
• 系統維運與使用者教育一次到位，顯著降低 TCO。  

**Cases 1**:  
• 合併後，一個 GitLab UI 就能完成 Code Review、CI Status、Issue 連動，開發者不必在多套系統跳轉，On-boarding 時間由 3 天降至 0.5 天。  
• 系統維護節省兩台虛機、四套備份策略，一年約省下 30% IT 維運工時。  

---

## Problem: 沒有一致分支策略，Release / Hotfix 版本混亂

**Problem**:  
團隊在同一條 master 上直接開發、修 Bug、發正式版；回報上一版漏洞時，找不到對應 Commit，產品緊急修補流程大亂。  

**Root Cause**:  
1. 不清楚成熟的 Branch Model（Git Flow、Trunk-Based Development）。  
2. 每個開發者「隨便切、隨便合」，導致回溯困難。  

**Solution**:  
導入 Git Flow，至少先固定：  
• master　：唯一可佈署到 Production 的 Long-Lived Branch  
• develop ：日常整合分支  
初期僅保留 master / develop 兩條永久分支，其餘 feature / hotfix / release 視需要快取快刪，降低 Branch 維護成本。  

**Cases 1**:  
• 團隊在第一個 Sprint 僅維護 master / develop，發現 Hotfix 流程需求後，再引入 hotfix Branch；導入成本可控、成員較易吸收。  
• 導入三個月後，QA 能精確回溯 Bug 時的 Commit Hash，缺陷追蹤時間由 2 小時降到 15 分鐘。  

---

## Problem: 缺少自動建置與單元測試，品質問題到最後一刻才爆炸

**Problem**:  
Developer Push Code →      手動 Build →      手動測試  
整合點才發現編譯失敗或功能衝突，甚至已上線才被用戶發現 Bug。  

**Root Cause**:  
1. 無持續整合環境；也缺乏測試 Culture。  
2. 建置、測試全憑個人電腦與人力操作，可重現性低。  

**Solution**:  
1. 用 GitLab CI 建立 Pipeline：  
```yaml
stages: [build, test, package]

build:
  image: mcr.microsoft.com/dotnet/sdk:6.0
  script:
    - dotnet restore
    - dotnet build --configuration Release
  artifacts:
    paths:
      - bin/Release

test:
  image: mcr.microsoft.com/dotnet/sdk:6.0
  script:
    - dotnet test --configuration Release --logger:trx

package:
  stage: package
  image: alpine
  script:
    - apk add --no-cache zip
    - zip -r app.zip bin/Release
  artifacts:
    paths: [app.zip]
```
2. Pipeline Gate：只有 Build ＆ Unit Test 全綠才產生 artifacts。  
3. 結果集中顯示於 GitLab Pipeline Dashboard，失敗即寄信 / App Push 通知。  

**Cases 1**:  
• 上述 Pipeline 部署後，主線編譯失敗率從每週 3 次掉到「幾乎 0」，開發者提早在 PR 階段就修正問題。  
• GitLab Pipeline 萬一紅燈，全組「Build Break Mail」立即寄出，平均修復時間 (MTTR) 從 4 小時縮短為 40 分鐘。  

---

## Problem: 佈署全靠人工，安全與可追蹤性堪憂

**Problem**:  
Production 佈署常常是「開發者在自己筆電 build DLL／Jar 檔，立刻複製上線」，曾發生惡意或無意的權限後門，但事後無法從版控還原真相。  

**Root Cause**:  
1. 缺少制式發行管道；Build 與 Deploy 沒銜接。  
2. 沒有封裝成套件，導致每次佈署都要手動挑檔案、改設定。  

**Solution**:  
1. 半自動 ➜ 全自動的漸進式發行管理：  
   a. CI 完成後，自動推送 artifacts 至 Package Manager（APT / npm / NuGet / Docker Registry）。  
   b. 手動佈署端僅需 `docker pull myrepo/app:1.2.3` 或 `apt-get install myapp=1.2.3`，省去挑檔案與版本判斷。  
2. 到位後，利用 Container 化（Docker / Kubernetes）把 Web / Service 整體封裝，落地 Immutable Infrastructure，佈署與回滾均只需換 Tag。  
3. 所有 Production Binary 都能對應到 CI Pipeline 與 Commit Hash，可稽核、可追溯，杜絕「暗改 DLL」風險。  

**Cases 1**:  
• 導入 Docker Registry 之後，OP 只允許從 Registry 拉取經 CI 簽章之映像檔；嘗試私接檔案佈署會被攔截，成功消除「暗渡陳倉」漏洞面。  
• 佈署時間（含驗證）由過去 1 小時手動 Copy ⭢ 改環境檔，縮短為 5 分鐘 `kubectl rollout restart`，而且可在任何時點用 `kubectl rollout undo` 一指回滾。  

---

> 以上六大問題與對應解決方案，皆以「先釐清需求，再逐步引入流程與工具」為核心思路。  
> 只要先把「版本控制、持續整合、發行管理」三件事做對，再循序擴大，就能在工程效率、品質與資訊安全三方面同步收穫。