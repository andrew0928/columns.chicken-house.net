# 網路搶票小幫手 - 遠端網站時鐘, WebServerClock v1.0

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 我該怎麼在網站時間 00:00 整準確地按下訂購按鈕？
透過 WebServerClock 先與目標網站同步，取得本機與伺服器的時間差並修正後，再依畫面上顯示的「伺服器時間」操作，就能把誤差降到最小。

## Q: WebServerClock 主要依靠哪一個 HTTP 標頭來取得伺服器時間？
它使用 HTTP/1.1 規範中必須回傳的 Date response header，藉此獲得伺服器端的時間戳。

## Q: 為什麼不直接用 NTP 來對時？
大多數訂票或搶購網站既不架設 NTP Server，也未必啟用 NTP Client，因此 NTP 不可行；唯一一定能取得且適用的對時資訊就是 HTTP 的 Date 標頭。

## Q: WebServerClock 是怎麼計算本機與伺服器的時間差 (offset)？
程式在送出 HEAD 要求時記錄本機時間 T0，收到回應時記錄 T3，假設伺服器送出 Date 標頭的時刻落在 T0 與 T3 的中點，即 T0 + (T3‒T0)/2，再用這個時間與 Date 標頭值相比即可得到 offset。

## Q: 以上方法的最大可能誤差是多少？
最大誤差等於整個往返時間 (T3‒T0) 的一半，也就是 (T3‒T0)/2。

## Q: WebServerClock 是不是自動搶票的機器人？
不是。它只是顯示經過校正的伺服器時間，協助你手動在正確時刻點擊按鈕，並不會自動下單或使用任何不正當手段。