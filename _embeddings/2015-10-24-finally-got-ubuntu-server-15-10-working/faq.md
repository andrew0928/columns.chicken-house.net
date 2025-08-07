# 終於搞定 Ubuntu Server 15.10 @@

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼作者不直接在 NAS 上繼續玩 Docker，而要另外建一套環境？
NAS 的硬體規格只有 Atom D2700（雙核心、1 GB RAM），裝幾個 container 就開始吃緊，作者想要一個可以隨時實驗又不用擔心效能的 Docker engine 環境。

## Q: 作者最後選用哪台硬體來架設新的 Docker／Ubuntu Server？
一台準備報廢的 Acer Aspire 5742Z 筆電，規格為：15.6" LCD（已裂）、Intel Pentium P6200、4 GB RAM、320 GB HDD。

## Q: 把舊筆電拿來當伺服器有什麼好處？
1. 省電，可 24 小時開機。  
2. 內建的舊電池可當作簡易 UPS，停電時還能撐幾分鐘讓系統正常關機。

## Q: 安裝過程中最終成功的作法是什麼？
將無線網卡直接拆掉，改用 Ubuntu Server 15.10 版本，安裝才順利完成。

## Q: 作者在安裝作業系統時遇到哪些主要問題？
1. 一開始使用錯誤的 USB 開機工具，只給 Net Install，因為網卡抓不到而卡關。  
2. 下載 12.04 LTS、14.04 LTS、CentOS 時都在安裝中途出現 “CDROM 內容不對” 的錯誤。  
3. 改裝 Desktop 版又在進入桌面後當機。  
最終才找到上述成功作法。

## Q: 基本系統安裝好之後，作者還做了哪些設定？
設定 SSH Server、固定 IP，以及 Samba 網路分享，確保可以遠端管理並與其他裝置交換檔案。

## Q: 架好這套環境後，作者的下一步計畫是什麼？
之後再花幾個禮拜把重點放到 ASP.NET 5 的研究與部署。