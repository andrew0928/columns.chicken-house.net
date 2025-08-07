# 令人火大的 SQL 字元編碼...

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 在透過 Linked Server 將資料從系統 A 抓到中繼資料庫時，最先出現的問題是什麼？  
兩邊資料庫的中文字編碼不同，直接 SELECT 會出現亂碼。

## Q: 作者如何解決最初的亂碼問題？  
在中繼資料庫把欄位轉成 Unicode（convert 成 ntext），便能正確顯示中文。

## Q: 為什麼作者認定後續發生的「資料錯亂」不是編碼或定序設定造成？  
直接 SELECT 可以得到正確結果，但 SELECT INTO 產生的暫存表卻把上一筆或其他筆的內容混在一起，這種「上一筆覆蓋、舊值殘留」的現象更像緩衝區溢位 (buffer overflow)；因此作者判斷是 SQL Server / SQL Native Client 本身的 BUG，而非編碼問題。

## Q: 最終讓資料正確的方法是什麼？  
改用 CURSOR，一筆一筆 FETCH 到 nvarchar 變數，再寫回暫存表。用這種「逐筆搬運」的方式就完全沒有資料錯亂。

## Q: 作者給遇到相同狀況的工程師什麼建議？  
別再跟各種編碼或定序設定硬碰硬；如果懷疑是 SQL Server 的 BUG，就繞道而行，用其他搬運方式（例如 CURSOR）避免踩到問題即可。