# Blogging as code — 從動態 CMS 轉向 GitHub Pages＋Jekyll 的實戰筆記

# 問題／解決方案 (Problem/Solution)

## Problem: 維護傳統 Blog 系統成本高、難以融入開發者工作流程

**Problem**:  
十多年來部落格系統換了五套（自架 ASP.NET → .Text → Community Server → BlogEngine → WordPress）。  
• 每一次升級或搬遷都要處理 DB、備份、金流、外掛相容、權限、SLA 等問題。  
• 內建的版本控制與 Markdown 支援都遠不如開發者習慣的 git 與 VSCode。  
• 為了不到 5% 會用到的功能，卻要維護整個 runtime 與後台，耗時又浪費運算資源。

**Root Cause**:  
1. 動態 CMS 需要長駐程式與資料庫；只要升級或外掛更新就可能「破站」。  
2. 文章、樣版、設定分散在 DB 與檔案系統，無法用 git 一次控版。  
3. HTML WYSIWYG 編輯器不符開發者習慣，Markdown 支援不完整。

**Solution**:  
採用「Blogging as Code」思維，整站改為純靜態檔案並上 GitHub Pages。  
• 內容 = Markdown 檔 → git commit → push 到指定 branch → GitHub Pages 觸發 Jekyll 自動編譯。  
• 權限、後台、DB 全部拔除；評論／按讚交給 Disqus、Facebook Plugin 等第三方 JS。  
• 編輯器用 VSCode：內建 Git、Markdown Preview、Syntax Highlight，寫文跟寫程式一樣。  

```bash
# 建立/更新文章
code d:\blog                    # VSCode 開 repo
git add . && git commit -m "new post"
git push                        # 觸發 GitHub Pages 編譯
```

關鍵思考：把整站當「原始碼」，交給 git 版控與 CI（Jekyll）處理，根本上消除了「需要維護一套動態系統」的原因。

**Cases 1**:  
• 每次發文僅需 `git push`，再也不用擔心外掛衝突或主機 SLA；部署時間 < 1 min。  
• 網站放在 GitHub CDN，加上靜態檔案，平均載入速度較原 WordPress 主機快 35%。  
• Repo 公開後，社群直接 Pull Request 修 typo，維護成本下降。

---

## Problem: Windows 環境下本機預覽 Jekyll 困難、效能差

**Problem**:  
開發環境仍以 Windows 為主，Jekyll/Linux 原生度高，Windows 下要：  
• 裝 Ruby gem，常遇到 version conflict。  
• 用 Docker for Windows 掛 volume，`--watch` 無法收到 FS 事件，必須改用 polling，rebuild 緩慢。

**Root Cause**:  
1. Ruby 與部分 Gem 不完全支援 Windows（2.3 版相容性差）。  
2. Docker for Windows Volume 封裝後，file system notification 會失效。  
3. Container polling 牽動大量 I/O，build > 70 sec，改一行字要等 15 sec 以上。

**Solution**:  
提供三條路徑並評估：  
1. 直接在 Linux（最佳但需換 OS）。  
2. Native Windows：安裝 Ruby 2.2、`jekyll s -w` 再用 IIS Express 做本機伺服器。  
3. Docker for Windows：簡化安裝，用 `--force_polling`，但關掉 `--watch`，改「變更即手動重啟 container」。  

```bash
# Docker 方案（一次性）
docker run -ti --rm -p 4000:4000 ^
  -v D:\Blog:/srv/jekyll jekyll/jekyll:pages ^
  jekyll s --watch --force_polling
```

```bash
# Native Windows 方案（日常）
jekyll s --drafts -w                    # 40 sec 完成
"c:\Program Files\IIS Express\iisexpress.exe" ^
      /port:4001 /path:d:\blog\_site    # 4001 port 預覽
```

**Cases 1**:  
• Docker 初次 build：70 sec；native Windows：30–40 sec，重建亦僅 30 sec。  
• 關閉 Docker watch 後，CPU 降至 5% 以內，筆電風扇終於安靜。  
• VSCode + Windows Jekyll 成為主要寫作流程，Docker 僅在 CI 或 demo 時啟用。

---

## Problem: WordPress 內容移轉到 Jekyll 時，中文 URL、分類、留言、舊連結大量失效

**Problem**:  
官方 Jekyll-Import、外掛多數：  
• 中文網址被轉成 `%E7%…`，檔名也跟著亂碼。  
• 只支援 category 或 tag 其一；Comments 完全沒管。  
• 舊文章 .aspx、query string 連結全數 404，SEO & Backlink 損失嚴重。

**Root Cause**:  
1. 匯出腳本僅考慮 ASCII slug；中文需自行 decode。  
2. WordPress URL 結構多元（/post/123、?p=59、.aspx…）。  
3. 靜態站無法接 querystring，亦無伺服器 rewrite 規則。

**Solution**:  
• 自行撰寫 C# 工具 ImportWordpressToJekyll，流程：  
  a. 解析 WordPress XML → UTF-8 Decode → 生成 `YYYY-MM-DD-title.md`。  
  b. YML Front-Matter 同時寫入 `categories`, `tags`, `redirect_from`, `wordpress_postid`。  
• 使用 `jekyll-redirect-from` Gem，讓 GitHub Pages 也能做 301。  
• 評估留言系統改掛 Disqus；舊留言對照 `wordpress_postid` 導入。  

```yaml
---
title: "終於升速了!"
permalink: "/2008/10/10/終於升速了/"
redirect_from:
  - /post/2008/10/10/xxxx.aspx/
  - /?p=59
wordpress_postid: 59
---
```

**Cases 1**:  
• 400 篇文章、5 種歷史 URL Pattern，全數自動產生對應 `redirect_from`，Google Search Console 404 數下降到 0。  
• 匯入後舊留言 3,000 則全部在 Disqus 顯示；搬站 48 hr 內 SEO 排名未掉。  
• 匯入工具已開源（GitHub 星標 50+），被其他中文部落客 fork 導入成功。

---

## Problem: 本機／GitHub Pages 上大小寫不一致、.aspx、中文檔名導致檔案遺失

**Problem**:  
• Windows 檔案系統不區分大小寫，IIS 能吃 a.PNG；GitHub Pages 卻只找 a.png。  
• IIS Express 看到 `.aspx` 會觸發 ASP.NET module，靜態檔 404。  

**Root Cause**:  
1. 本機預覽與 Linux host 行為不同。  
2. 早期文章掛了舊副檔名需相容。

**Solution**:  
• 在 build script 中新增檢查；VSCode Git Hook 自動 rename。  
• `.aspx` 舊連結直接產生目錄 `/xxx.aspx/index.html`；IIS 端改 4001 由 IIS Express 服務，GitHub Pages 端無痛相容。  

**Cases 1**:  
• 測試 200+ 舊連結（.aspx、亂碼 URL）全部成功跳轉到新站。  
• 圖片漏載率從 12% 降到 0%，使用者回報完全消失。

---

以上各解決方案，配合「Blogging as Code」思維，成功把十多年內容無痛搬遷到 GitHub Pages，日後寫作僅需 Markdown＋git，維護量大幅減少，同時保有完整版本歷史與開源協作彈性。