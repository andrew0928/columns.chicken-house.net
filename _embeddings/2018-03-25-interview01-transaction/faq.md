# 架構面試題 #1, 線上交易的正確性

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 在設計帳務系統時，為什麼必須遵守「金錢守恆定律」？
錢不應該在系統內憑空產生或消失；於任何時刻，封閉系統內的金額總和必須維持不變。若交易只做了一半（例如扣款後未入帳），就會破壞此守恆定律，因此系統必須保證交易過程的完整與正確性。

## Q: 面試題中要求的交易驗證方式是什麼？
以多執行緒 (N 個 threads) 各重複執行 M 次將 1 元轉入同一帳戶，理論上最後餘額應增加 N×M 元；透過單元測試驗證預期與實際餘額是否一致即可判斷交易引擎是否正確。

## Q: 在單機 (1 host) 環境下如何避免交易錯誤？
使用程式語言或作業系統提供的 lock 機制，將「讀取餘額 → 更新餘額 → 紀錄交易」包成 Critical Section，避免 Race Condition。常用關鍵字／API 如 lock、Interlocked、Critical Section 等。

## Q: 若省略單機環境中的 lock 會發生什麼情況？
會因多執行緒同時讀寫導致 Race Condition，造成部分計算結果被覆寫，最終餘額少算（文章示範約少 20%），即「錢憑空消失」。

## Q: 在 10+ hosts 規模、使用關聯式資料庫時如何確保交易正確？
把交易邏輯交由資料庫透過 SQL Transaction 處理。RDBMS 具備 ACID 特性，可在 INSERT 與 UPDATE 等指令間維持一致性與原子性，應用程式只需包裝成單一 transaction 即可。

## Q: 當系統擴充到 100+ hosts 且改用不支援交易的 NoSQL 時，該怎麼辦？
需在應用層建立分散式鎖定 (Distributed Lock)。常見作法是使用 Redis + RedLock 演算法：  
1. 嘗試取得鎖（可設定等待與重試時間）。  
2. 取得鎖後進行讀取餘額、更新餘額、寫入交易紀錄。  
3. 完成後釋放鎖；若逾時未釋放，由鎖本身的過期機制自動回收。  
如此可在多個微服務實例間仍維持臨界區，避免 Race Condition。

## Q: 不同職級的工程師在此題目中各自需要掌握哪些解法？
• Junior Engineer：能在單機情境中正確使用 Lock，了解 Race Condition 與 Critical Section。  
• Senior Engineer：能在多主機情境下利用 RDBMS 的 ACID / SQL Transaction 確保正確性。  
• Architect：能在大規模分散式情境下設計並實作 Distributed Lock（或分散式交易）機制。

## Q: 作者為何偏好用「應用題」作為面試白板題，而非 LeetCode 式標準答案題？
因為 microservice 團隊需要的是具備獨立思考與實作能力的工程師，而非找出唯一標準解的人。應用題能觀察面試者面對實際問題的分析、抽象化及在不同規模下的解決策略。