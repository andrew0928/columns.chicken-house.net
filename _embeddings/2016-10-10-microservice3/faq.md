# API & SDK Design #1, 資料分頁的處理方式

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 這篇文章示範的 Data API Service 主要用途是什麼？
它利用「特生中心 102 年繁殖鳥大調查」的 1,000 筆 JSON 資料，示範如何在微服務架構中設計一個支援分頁的 RESTful API，並進一步說明 API / SDK / APP 之間的協作方式與開發者體驗 (DX) 的重點。

## Q: 這個 API 如何實作「分頁」？Client 端要帶哪些參數，伺服器又會回哪些 Header？
1. 呼叫格式：`~/api/birds?$start={start}&$take={take}`  
   • `$start`：從第幾筆開始 (預設 0)  
   • `$take`：一次取回幾筆 (預設 10，最大 10)  
2. 伺服器於 Response Header 回傳：  
   • `X-DATAINFO-TOTAL`：資料總筆數  
   • `X-DATAINFO-START`：這一頁從第幾筆開始  
   • `X-DATAINFO-TAKE`：本頁最多回傳幾筆  
3. 亦支援 HTTP HEAD Verb，只會回傳 Header，不帶資料內容。  
4. 取單筆資料可用：`~/api/birds/{birdid}`。

## Q: 為什麼作者建議在 Client 端使用 C# 的 yield return 來存取分頁資料？
`yield return` 能把「資料巡覽」與「資料處理」分離，藉由延遲產生 (lazy evaluation) 讓程式：
1. 只在需要時才向伺服器抓下一頁，節省頻寬與記憶體。  
2. 使主程式只需寫一行 LINQ，迴圈邏輯更乾淨、可維護。  
3. 自然符合 iterator pattern，可與 `break` 或 `Take(n)` 等控制流程搭配，彈性高。  

## Q: 如果在 foreach 中提早 break，使用 yield return 仍會繼續呼叫後續 API 嗎？
不會。實驗顯示，一旦前端 `foreach` 因 `break` 或 `Take(1)` 等操作停止迭代，`yield return` 的迭代器就會立刻結束，後續的分頁呼叫不再發生，因此沒有多餘的網路流量與處理成本。

## Q: 在可以使用 OData 的情況下，還需要自己實作這種 IEnumerable 式的分頁嗎？
通常不需要。OData 透過 `IQueryable` 能把 LINQ 條件直接下放到 Server 端做查詢與過濾，效率更高、傳輸更少。若專案環境與資料來源皆支援 OData，直接採用 OData 是更理想的方案；自行實作 `IEnumerable` 式的分頁則適用於 API 不符合 OData 標準的情境。

## Q: 文章中提到的「DX」是什麼？和 UX 有什麼不同？
DX (Developer Experience) 指的是「開發者體驗」。API 的受眾是開發者，開發者在乎的是文件完整度、介面設計是否直覺、SDK 是否好用、效能與穩定度等。而 UX (User Experience) 著重於終端使用者的操作體驗。良好的 DX 能讓開發者覺得 API 優雅、易整合、易維護，進而提升整體產品的採用率與口碑。