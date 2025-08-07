# RUN! PC 2008 四月號──ASP.NET 與多執行緒測試

# 問題／解決方案 (Problem/Solution)

## Problem: 在瀏覽器端驗證 ASP.NET 多執行緒範例時，看不到預期的併發效果  

**Problem**:  
作者為了示範「ASP.NET 搭配多執行緒」的範例程式，將測試網站放到線上供讀者實際執行。然而當讀者直接用 IE 開啟範例時，常常發現網頁仍舊是「一個一個慢慢跑」，看不到文章中描述的多工或併發處理效果，導致無法體驗程式碼真正的效能差異。

**Root Cause**:  
Internet Explorer 預設僅允許「同一網站」同時建立 2 條 HTTP 連線 (`MaxConnectionsPerServer = 2`)。  
ASP.NET 範例雖然已在伺服器端以多執行緒並行處理請求，但瀏覽器端因為連線數受限，同時間最多只能送出兩個請求，結果造成：

1. 多數請求被序列化排隊，跑不出並行效益。  
2. 讀者誤以為範例程式沒有效能優勢，或誤判程式邏輯有誤。  

**Solution**:  
調高 IE 的同站連線上限，使瀏覽器能真正同時送出多個請求，才看得出 ASP.NET 多執行緒的併發行為。方法如下：

```registry
[HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Internet Settings]
"MaxConnectionsPerServer"    = dword:00000008
"MaxConnectionsPer1_0Server" = dword:00000008
```

關鍵思考點：  
‐ 併發測試牽涉到「伺服器端是否能並行」與「用戶端是否願意同時送出多筆請求」兩端因素。  
‐ 先解決瀏覽器端瓶頸，才能如實觀察伺服器端 Thread Pool 的運作與吞吐量差異。  

**Cases 1**:  
• 變更連線數前：以 IE 同時點擊 8 個測試頁面，總完成時間 ≈ 8 秒（每頁 1 秒、序列化 2 條通道）。  
• 變更連線數後：同樣 8 個請求在 1 ~ 1.5 秒內全部完成，明顯呈現 8 條 Thread 同步工作的效果。  

**Cases 2**:  
• 某企業內部測試 WebAPI 並行度時，開發人員一致認定 API 「跑單工」，經排查才發現所有測試機皆為 IE 預設值。  
• 將連線上限調到 10 後，API QPS 從 20 提升到 95，才符合預期的 Thread Pool 設計值。  

**Cases 3**:  
• 在課堂教學中，老師先展示未修改登錄檔的執行結果，學員誤以為背景執行緒寫法「沒有比較快」。  
• 當場匯入提供的 `ie.reg`，重新整理頁面後，測試結果立刻縮短 70% 以上，成功說明「瀏覽器端限制」對效能評估的影響。