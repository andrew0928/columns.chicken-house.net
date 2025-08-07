# 升級失敗... Orz

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 作者這次原本想把 Community Server 從哪個版本升級到哪個版本？
作者打算將先前安裝的 Community Server 2.0 RTM 升級到 2.1 SP2。

## Q: 升級前作者做了什麼預防措施？
在動手更新檔案與執行 2.x→2.1 的升級 SQL Script 之前，作者先做了一份 shadow copy 來備份系統。

## Q: 為什麼最後作者又把系統還原回去？
升級後整個 Community Server 無法啟動，而 CS 內建的錯誤回報機制又隱藏了詳細訊息，作者只知道發生 Error 卻找不到問題原因；加上小孩在旁干擾無法專心處理，於是決定直接還原 shadow copy，改天再戰。