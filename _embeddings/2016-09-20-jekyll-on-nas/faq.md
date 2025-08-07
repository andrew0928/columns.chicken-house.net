# Running Jekyll on NAS ‑ 高效率的新選擇

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼在 NAS 上使用 Jekyll 的靜態網站，比直接安裝 WordPress 更適合？
靜態 HTML 幾乎不耗資源，速度快又安全；而 WordPress 需要 PHP 與資料庫，對 NAS 上相對貧弱的 CPU/RAM 是額外負擔。在同樣硬體條件下，靜態網站點一下就開，體感明顯「飛快」。

## Q: 在 NAS 上架設 Jekyll 需要多久？難度高嗎？
利用官方 Docker 映像 (jekyll/jekyll:latest) 搭配 Synology 的 Docker 及 Web Station，流程不到五分鐘：拉映像、掛載 /docker/jekyll、複製網站檔、設定虛擬主機即可完成。

## Q: Jekyll 如何拿來做軟體專案的文件管理？
把程式碼與 Markdown 文件一併放進 Git 版本控制：  
1. 程式註解可自動產生 API/Library 文件。  
2. 其他手冊直接寫 Markdown。  
Push 後由 Jekyll（或 GitHub Pages）自動重建並部署 Web 版文件，讓「Code + Docs」同步更新，對開發者而言天衣無縫。

## Q: MSDN 的 Windows Containers 文件是不是也用 Jekyll？為何能確定？
是的。每篇文件最前面都有標準 Jekyll front-matter（title、description、keywords…），且「Contribute」連結直接指向 GitHub 上的 Markdown 原檔，證明其背後採用 Jekyll。

## Q: 要在 Synology（S 牌）NAS 上跑 Jekyll，需要先準備哪些條件？
1. NAS 韌體需支援 Docker。  
2. 預留目錄 /docker/jekyll 作為網站原始碼與輸出(_site)存放處。  
3. 啟用 Web Station（建議 Nginx）以便對外服務靜態內容。

## Q: 完整的安裝/部署步驟是什麼？
1. 在 Docker Registry 搜尋並拉取 jekyll/jekyll:latest，建立 container，將 NAS 的 /docker/jekyll 對應到 container 內 /srv/jekyll。  
2. 把網站樣板與文章複製進 NAS:/docker/jekyll（文章放 _posts，編譯結果將輸出到 _site）。  
3. 於 Web Station 建立 Virtual Host，根目錄指向 /docker/jekyll/_site，即可透過網域或 Port 存取。

## Q: NAS 的 Atom CPU 編譯 Jekyll 網站會不會很慢？
不會。實測 Synology DS-412+ (Atom D2701, 2 GB RAM) 完整編譯約 42 秒；桌機 i7-2600K 約 30 秒。差距不大，日常使用可接受。

## Q: 如何判斷 Jekyll 已經成功完成編譯？
在 Docker 容器 log 看到 “Generating… done in xx seconds.” 代表建置結束；亦可用 http://{NAS IP}:{對應的 port 4000} 或 Web Station 網域進行頁面驗證。

## Q: 網站上線後還需要一直跑 Jekyll 嗎？
不用。Jekyll 只負責把 Markdown 轉成靜態 HTML；之後由 Web Station/Nginx 提供服務，就算 Jekyll 容器關掉，網站仍可正常存取。