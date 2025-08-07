# CaseStudy: 網站重構, NGINX (REVERSE PROXY) + 文章連結轉址 (Map)

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼作者要將前端 Reverse Proxy 從 Apache 改為 NGINX？
在新的 Ubuntu Server 環境裡不再受 NAS 內建 Apache 佔用 80 port 的限制，加上 NGINX 本身效能更好、設定檔更精簡，且社群正熱門，作者便決定用 NGINX 取代 Apache 來擔任 Reverse Proxy。

## Q: 作者是如何在 NGINX 裡處理 400 篇文章、6 種網址格式 (約 2400 組) 的舊網址轉址需求？
他利用 NGINX 的 map 指令。  
1. 先在 server 區段用正則式擷取舊網址中的 slug，存入變數 $slug。  
2. NGINX 透過 `map $slug $slugwpid { include maps/slugmap.txt; * 0; }` 讀取外部對照表 slugmap.txt，把 slug 對應到新的 WordPress 文章 ID。  
3. 最後以 `return 301 /?p=$slugwpid;` 送出 HTTP 301，完成舊網址 → 新網址的轉址。

## Q: 為何作者放棄 Synology NAS，改用舊筆電 + Ubuntu Server + Docker 來架設部落格？
Synology 412+ (Atom 2701D + 2 GB RAM) 在多開幾個 Docker container 後就明顯變慢；反之，舊筆電 (Pentium P6100 + 4 GB RAM) 運算力與記憶體都較佳、耗電低，而且內建電池可當 UPS，整體更符合自架需求。

## Q: 作者認為投入時間熟悉 Linux／Open Source 技術的主要原因是什麼？
現代大型佈署多採 Linux + Open Source，而 .NET Core 亦將跨平台執行；連 Microsoft CEO Satya Nadella 都公開表示「Linux is best for cloud」。若不熟悉 Linux，就無法把自己寫的程式順利部署到雲端或跨平台環境。

## Q: NGINX map 指令運作的核心原理是什麼？
在宣告 `map $source $target` 後，只要在任一處給 `$source` 賦值，NGINX 便會自動查表，將對應結果放入 `$target` 變數。藉此可於設定檔內簡潔地完成大量字串對應與轉址邏輯。