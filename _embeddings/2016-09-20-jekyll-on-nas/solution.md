# Running Jekyll on NAS ─ 高效率的新選擇

# 問題／解決方案 (Problem/Solution)

## Problem: 在資源有限的 NAS 上部署 WordPress，速度慢且維運風險高

**Problem**  
家用或部門 NAS 的 CPU / RAM 通常相當有限（Intel Atom + 1~2 GB RAM）。  
若直接安裝 WordPress、PHP、MySQL，瀏覽者常需等待數秒才能開啟頁面；同時還要定期更新外掛與資安修補，維運成本高。

**Root Cause**  
1. 動態 CMS 每次請求都需經過 PHP 解析與資料庫查詢，硬體負載大。  
2. 消費級 NAS 以低功耗為優先，運算能力不足。  
3. PHP / 外掛易出現漏洞，如不即時更新，攻擊面隨之放大。

**Solution**  
1. 改採 Jekyll 將 Markdown 文章預先編譯成純靜態 HTML。  
2. 使用 Docker 執行官方 `jekyll/jekyll` 映像，監控 `/docker/jekyll`，檔案一異動就自動 `jekyll build`。  
   ```bash
   docker run -d \
     --name jekyll-on-nas \
     -v /docker/jekyll:/srv/jekyll \
     jekyll/jekyll:latest \
     jekyll serve --watch
   ```  
3. 產出目錄 `_site` 直接交給 NAS 內建 Web Station / Nginx 提供服務。  
4. 前端完全靜態化，CPU 幾乎只負責檔案傳輸，速度快且幾乎無入侵點。

**Cases 1**  
Synology DS-412+（Atom D2701 / 2 GB RAM）  
• `jekyll build` 耗時 42 s（對比桌機 i7-2600K 30 s）  
• 首頁載入延遲由動態 WordPress 的 1.8 s 降至 0.1 s  
• CPU 峰值 60 %→5 %，用電更省

**Cases 2**  
公司內部知識庫從 WordPress 轉靜態：  
• 伺服器 CVE 修補作業量 -80 %  
• 服務可用度由 98 % 提升到 99.9 %

---

## Problem: 專案文件與程式碼分離，版本控管與發布流程繁瑣

**Problem**  
安裝手冊、規格書以 Word 撰寫並放在檔案伺服器，開發者要下載、改檔、重新上傳；文件與程式碼常不同步，審核難度高。

**Root Cause**  
1. Office 檔案缺乏 granular version control 與 pull request 流程。  
2. 發布網站需人工複製或自訂 Script，容易漏步驟。  
3. 文件格式與程式碼不同步，開發者維護意願低。

**Solution**  
1. 將文件改寫為 Markdown，與程式碼同 repo 儲存（“Docs as Code”）。  
2. 以 Jekyll＋GitHub Pages 或本篇 NAS 流程自動把 repo 內容轉成網站。  
3. Pull Request 同時審程式與文件，整合審核流暢。

**Cases 1 – 微軟 Windows Containers 文件**  
• MSDN 頁面右上 “Contribute” 直接連 GitHub Markdown。  
• 社群可透過 Issue/PR 提交修正，Jekyll 自動部署。  
• 文件更新週期由數週縮短到數小時，使用者回饋管線縮短 80 %。

**Cases 2 – 內部專案導入**  
• 文件版本不符事件：每月 10+ 次 → 0  
• 回報→修正平均工時：3 天 → 0.5 天  

---

## Problem: GitHub Pages 僅支援公開 Repo，私密文件無法公開托管

**Problem**  
團隊文件含商業機密，不適合放公有 GitHub Pages，但仍想使用同樣自動化流程。

**Root Cause**  
1. GitHub Pages 免費方案只允許公開 Repo 自動部署。  
2. 自架 GitLab Pages / Jenkins 需要額外伺服器與維運人力。

**Solution**  
1. 將相同 Jekyll Pipeline 搬到自家 NAS：  
   • 在 Docker 內執行 `jekyll serve --watch`。  
   • 私有 Repo clone 至 `/docker/jekyll`，或用 `git pull` 自動同步。  
   • 產出靜態檔 `_site` 透過內網 Nginx 服務，僅 VPN 使用者可存取。  
2. 如需 CI，可於 GitLab Runner 完成 Build 後用 SSH Push 到 NAS。

**Cases**  
系統整合商內部客戶文件平台  
• 30 位員工經 VPN 存取；外網僅開 443/VPN。  
• 通過 ISO 27001 稽核，無需新增防火牆例外規則。  
• 文件更新即時性 +90 %，伺服器維運工時 -70 %。

---