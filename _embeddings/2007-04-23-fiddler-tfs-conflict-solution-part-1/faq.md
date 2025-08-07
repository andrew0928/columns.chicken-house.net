# Fiddler 跟 TFS 相衝的問題解決 - I

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 同時開啟 Fiddler 與 Visual Studio 2005、連線 TFS 時會出現什麼異常現象？
當 Fiddler 開啟後，VS2005 與 TFS 之間的 HTTP 連線會被卡住無法繼續；在 Fiddler 的紀錄裡可以看到 TFS 伺服器回傳 HTTP 401 (Unauthorized) 的錯誤碼。

## Q: 為什麼會出現 HTTP 401 錯誤？
VS2005 對 TFS 使用的身份驗證資訊沒有被 Fiddler 正確地轉送到 TFS 伺服器，伺服器因而認定請求沒有授權，回覆 401。

## Q: 最快速、最簡單的解決方法是什麼？
啟動 Fiddler 讓它自動修改 IE 的 Proxy 設定後，手動把 TFS 的網址加入 Fiddler 的 bypass host list (不走 Proxy)；完成後 VS2005 便能正常連線 TFS。

## Q: 若想把上述解法自動化，可以採取哪些步驟？
計畫流程如下：
1. 在 Fiddler 啟動時先保存目前的 Proxy 設定。  
2. 讓 Fiddler 將 WinINET Proxy 改成 127.0.0.1:8888。  
3. 在 Fiddler 的 OnAttach 事件中加入自訂 Script，重複第 2 步的程式碼並額外把 TFS 網址加入 bypass host list，使日後啟動 Fiddler 時可自動完成設定。