# ChickenHouse.Web.CommunityServerExtension 新功能 之 2

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 這次為 ChickenHouse 的 Community Server 加了什麼新功能？
在 Blog 側邊欄顯示「最新十筆回應」，方便使用者與管理者即時看到新的留言。

## Q: 為什麼作者要自己動手開發「最新留言」功能？
因為 Community Server (含 1.1 版) 原本並沒有內建這項功能，若想查看新留言，管理者只能進管理介面，一般使用者甚至得逐篇文章搜尋，十分不便。

## Q: 把這個看似簡單的功能加進 CS 為什麼花了好幾天？
由於 CS 為了支援佈景主題/樣版，程式碼分散在七、八個專案、十多個 DLL 與多套樣版檔中，要追到真正輸出文字的位置相當困難，因此耗時良久。

## Q: 作者對 CS 的心情是「誇讚」還是「抱怨」？
作者一方面佩服 CS 的彈性，另一方面又嫌它「脫褲子放屁」——為了樣版機制把事情搞得複雜，所以是既愛又恨。

## Q: 加完這項功能後，ChickenHouse 的 CS 與其他站點有何不同？
多了「最新十筆回應」的側邊欄顯示，讓本站比其他採用 CS 的站點更具特色。