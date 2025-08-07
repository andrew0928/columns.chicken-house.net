# 偷偷升級到 CS2007 ..

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 站長什麼時候把網站升級到 CS2007？
大約在兩個禮拜前，站長已經將本站從舊版 Community Server 升級到 CS2007。

## Q: 升級到 CS2007 主要需要做哪些步驟？
只要進行「資料庫升級 (DB upgrade)」及「檔案升級 (File upgrade)」兩個步驟即可完成升級。

## Q: 舊版 (1.0~2.x) Community Server 的樣版系統有什麼特點？
舊版樣版系統大量使用動態載入的 User Control；版面配置寫在 User Control 的標籤 (TAG) 中，資料與邏輯則寫在程式碼後端，要客製化時相對麻煩，需要花時間了解其做法。

## Q: CS2007 在樣版系統上做了哪些改變？
CS2007 改採 ASP.NET 2.0 的標準做法，每套樣版由一個 master page 與對應的 theme.config 組成；以 Blog 為例，每個頁面就是單純的 .aspx，修改起來方便許多。

## Q: 升級後作者如何處理原本客製化的 User Control？
作者趁這次改版將原本需要編譯成 DLL 的 User Control 重新改寫成 .ascx + .cs 檔案，直接放在站台上即可部署，維護與部署都更方便。

## Q: 作者目前對 CS2007 的新功能了解得如何？
作者尚未仔細研究 CS2007 的新功能，但表示至少現在整個平台已經就緒。