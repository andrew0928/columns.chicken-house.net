# 微服務基礎建設: Process Pool 的設計與應用

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼在 .NET 的隔離技術中最終選擇 Process，而不是 AppDomain 或 Thread？
Process 具備最完整的記憶體與執行空間隔離，能將不同團隊的程式碼完全區隔，避免 static 變數汙染、未捕捉例外導致整個服務崩潰等問題。實測顯示，在 .NET Core 環境下，Process 的啟動成本雖高，但搭配 Process Pool 後，整體吞吐量仍優於 AppDomain，同時享有跨語言、跨平台的彈性；而 Thread 幾乎沒有隔離能力，不符合需求。

## Q: 實際 Benchmark 呈現什麼結果？  
1. 在 .NET Core 中，每秒可啟動 Process 約 23 次，但同一秒可執行 Task 逾 37,000 次，顯示「啟動成本 ≫ 執行成本」。  
2. 啟用 Process Pool 後，Process 版本的效能比單純 Single-Process 版本提升 2～4 倍；與 .NET Framework + AppDomain 相比可高出將近 9 倍。  
3. .NET Core 的 SHA512 與 I/O 進步，使同一程式在 .NET Core 下普遍比 .NET Framework 快 2～4 倍。

## Q: .NET Core 與 .NET Framework 誰適合作為主控端與工作端的開發平台？
建議主控端與工作端都優先採用 .NET Core。  
若有 Legacy 限制，工作端可以暫時維持 .NET Framework，但建議改寫成 .NET Standard，並以條件式編譯保留升級彈性。整體來看，.NET Core 帶來的記憶體與 I/O 最佳化，使效能顯著優於 .NET Framework。

## Q: 隔離環境中的參數傳遞，為何建議使用 BLOB（Base64）而非僅傳遞值？
實測顯示，在 Process 隔離下傳遞 1 KB～1 MB 的 Base64 BLOB，與僅傳遞 int 等值類型相比，效能差距不到一倍，卻能省去再到資料庫或快取撈資料的延遲與複雜度；因此在開發便利與效能之間，直接傳 BLOB 更划算。

## Q: Process Pool 的核心參數有哪些？  
1. _min_pool_size：保留的最少 Process 數。  
2. _max_pool_size：允許的最大 Process 數。  
3. _process_idle_timeout：單一 Process 閒置多久即回收。  
4. BlockingCollection 佇列大小：決定主控端可先行佇列多少 Task。  
這些參數共同決定了 Pool 在「冷啟動延遲、資源利用率、記憶體占用」之間的平衡。

## Q: 如何避免 Process Pool 吃滿所有 CPU 導致其他服務卡頓？
可以在啟動 Process 時設定：  
• ProcessPriorityClass.BelowNormal：讓 OS 先排其他重要程序。  
• ProcessorAffinity：限定 Process 只跑在部分核心，例如 `0b00001110` 只用第 1-3 號核心。如此既可榨乾剩餘 CPU，也不影響主程式或其他服務反應。

## Q: 若已有 Serverless 或 K8s，還需要自己實作 Process Pool 嗎？
若任務無法完全搬到 Linux、冷啟動時間要求極嚴格、Windows Container 支援度不足，或需要在單一 VM 內針對「Job 等級」做精細調度時，自建 Process Pool 仍是最務實的方案；跨 VM 的水平擴充則仍可交由 K8s 或雲端 Auto-Scaling 處理。

## Q: Process Pool 的 100 行程式碼大致怎麼運作？
1. 以 BlockingCollection 收 Task，Producer / Consumer 模式同步。  
2. 每個 Process 由專屬 Thread 監管，透過 STDIN/STDOUT 以 Base64 傳遞參數與結果。  
3. 進入工作前檢查是否需「擴充 Process」；無工作且逾 timeout 檢查是否「回收 Process」。  
4. Stop() 會 `CompleteAdding()` 佇列並等待所有 Process 結束，確保優雅關閉。

## Q: 為何需要隔離環境？有哪些常見的「惡鄰居」情境？
1. 他人程式吃光 RAM，造成 OutOfMemory。  
2. 他人程式 CPU 線程失控，導致整體延遲。  
3. Static 變數被改寫，汙染共用程式庫狀態。  
4. 未捕捉例外導致整個 Process Crash。  
透過 Process Pool 或 AppDomain Pool 可將影響範圍侷限在單一任務，提升可靠度。

## Q: 這篇文章給架構師與開發者最大的結論是什麼？
基礎原理與量化驗證仍是架構決策核心。當現有框架或雲端服務無法滿足「效能、平台限制、維運成本」等綜合需求時，適度自行實作關鍵環節（如 Process Pool）往往只要數十到百行程式碼，就能大幅提升可控性與整體效益。