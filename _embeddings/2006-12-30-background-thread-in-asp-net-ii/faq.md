# Background Thread in ASP.NET (II)

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼背景 worker thread 在大約 20 分鐘後就停止執行？
因為 COM+ Application Pool 的預設 Idle Timeout 設定為 20 分鐘。當 IIS 在這段時間內沒有新的 HTTP request 進入時，App Pool 會自動回收並釋放資源，導致 ASP.NET 應用程式被卸載，背景 worker thread 也隨之被終止。

## Q: 若要讓背景工作持續執行，需要調整哪一項設定？
必須修改 COM+（IIS Application Pool）的 Idle Timeout／回收設定，將其時間拉長或停用自動回收，避免因「20 分鐘內無新 request」而把整個 App Pool 關閉，才能讓背景 thread 長時間持續運行。

## Q: 調整 Idle Timeout 後還遇到了什麼問題？接下來的重點是什麼？
在更改 App Pool 設定後，背景工作雖已能跑上數小時，但因其他例外狀況導致 IIS 的 w3wp.exe 行程停止。下一步要專注的重點是如何妥善地做例外處理（exception handling），避免未捕捉的例外再次造成應用程式中斷。