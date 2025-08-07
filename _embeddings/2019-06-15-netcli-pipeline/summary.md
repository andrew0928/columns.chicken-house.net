# 後端工程師必備: CLI + PIPELINE 開發技巧

## 摘要提示
- Pipeline: 以分段並行的方式同時滿足批次量能與串流低佔用，獲得數倍效能。
- CLI: 將邏輯拆成多個命令列程式並用管線串接，可直接借力 OS 的 stdin/stdout 緩衝與多行程。
- 批次 vs 串流: 批次易維護但吃記憶體，串流省空間但程式混雜，須視需求權衡。
- C# yield: 透過 IEnumerable 與 yield return 可快速寫出單行程 Pipeline，保持各階段單一職責。
- Async Pipeline: 加入 Task 與 async/await 讓各階段重疊運算，總時間由 ΣMi 降為 N×Max(Mi)。
- BlockingCollection: 以受控佇列封裝緩衝，實現生產者/消費者，簡化同步問題。
- 資源觀測: 實驗顯示 Pipeline 模式記憶體固定且可調，緩衝大小決定速度與佔用。
- CLI Pipeline 實作: 拆成 CLI-DATA、CLI-P1/P2/P3，shell pipe 即得與程式內 Pipeline 等效的並行。
- 測試分析: 透過 1GB/4MB/16B 範例比較 batch、stream、pipeline 的時間與記憶體曲線。
- 實務價值: 熟練 CLI + PIPELINE 讓後端能寫出高效背景服務、批次轉檔與跨機器分散處理。

## 全文重點
本文以「批次、串流、管線」三種處理模型為軸，說明後端工程師在面對百萬筆以上資料時，如何在效能、記憶體與程式可維護性之間取得平衡。首先釐清批次一次處理大量資料但必須等整批完成、串流一次只處理一筆可節省記憶體但回應速度有限；管線則把多道步驟拆開並行，讓第一筆資料能最快完成，同時整體完成時間可縮短到 N×Max(Mi)。

作者以 C# 寫出五個 DEMO：  
1. Batch 逐階段迴圈，簡單卻佔滿記憶體。  
2. Stream 逐筆完整處理，記憶體固定但程式混雜。  
3. Pipeline(yield) 以 IEnumerable 封裝各階段，兼具結構與低佔用。  
4. Pipeline(async) 將 Task 與 await 加入，各階段可重疊，時間大幅縮短。  
5. Pipeline(BlockingCollection) 以 BlockingCollection 作緩衝，實現生產者/消費者並可調平行度。

接著把程式內 Pipeline 拆成四個 CLI：CLI-DATA 產生 jsonl、CLI-P1/P2/P3 各負責一階段，透過 shell pipe 串成「CLI-DATA | CLI-P1 | CLI-P2 | CLI-P3」。OS 會自動建立管線緩衝與阻塞控制，使每個子程序獨立釋放資源並取得更佳重疊度。實測 4MB×1000 筆及 16B×1000 筆，可見記憶體穩定維持在單程序 160MB/5MB；速度受限於最慢階段，但因前階段提早完成，使整體佔用與停機時間最小化。

最後指出 CLI + PIPELINE 進一步可延伸到多機 ssh 管線、tee 分流、dotnet tool 發佈、微服務批次作業等場景；並提醒善用基礎知識比倚賴大型框架更具彈性與可控性。

## 段落重點
### PIPELINE 的基本概念
闡述 Batch、Stream、Pipeline 三種模型的差異：Batch 以流程為單位、Stream 以資料為單位、Pipeline 交錯兩者並行。透過示意圖比較第一筆完成時間、全部完成時間與半成品數量，說明 Pipeline 在各階段耗時相當時理論可達三倍效率。

### 在單一專案內 (code) 的處理方式
介紹基礎類別 DataModel 及三段處理函式，並用 GetModels() 產生測試資料。透過五個 DEMO 展示不同寫法對時間與記憶體的影響，並用 VS Profiler 觀察實際佔用。結論是 Pipeline+Async 可在維持固定記憶體下大幅縮短總時間，BlockingCollection 更能調整緩衝大小換取速度。

#### DEMO 1 批次處理
三重 foreach 先後跑 P1~P3，第一筆與全部完成時間皆為 N×ΣMi，記憶體隨資料量線性上升。

#### DEMO 2 串流處理
單迴圈依序呼叫 P1~P3，第一筆僅需 ΣMi，記憶體固定，但結構耦合。

#### DEMO 3 管線處理 (yield return)
將各階段封裝成 IEnumerable 並以 yield return 串接，兼具低佔用與清晰分工。

#### DEMO 4 管線處理 (async)
在每階段加入 Task 執行並等待上一筆，形成局部重疊，總時間由 22s 降到 13s，記憶體略增。

#### DEMO 5 管線處理 (BlockingCollection)
改用 BlockingCollection 作佇列並以背景執行緒推送資料，可自行設定容量，進一步縮短時間但增加記憶體。

### CLI 的處理方式
說明拆成多個 CLI 的好處：由 OS 管理行程、緩衝與阻塞，程式本身更簡潔。

#### CLI: 獨立的 PROCESS
闡釋 shell pipe 的工作原理與 STDIN/STDOUT/STDERR，示例 tasklist | find 的資料流。

#### CLI-DATA, Data Source
CLI 1 產生 jsonl，使用 JsonSerializer 逐筆輸出避免一次序列化造成 OOM。

#### CLI-P1, Data Processing
CLI 2 接收 STDIN 逐筆反序列化並執行 P1，再輸出到 STDOUT；示範 SupportMultipleContent 與錯誤輸出走 STDERR。

#### CLI-P1~P3 整合測試
將四支 CLI 串起來，得到與 DEMO 5 等效的時間軸；由於管線 buffer 自動調節，P1 會領先約 40 筆後被阻塞，確保記憶體穩定。

#### PIPELINE 效能與記憶體測試
以 4MB×1000、16B×1000 測試，觀察多進程記憶體曲線與 LOG；證實每個行程佔用固定且可提早釋放，整體時間取決於最慢階段。

### PIPELINE 其他應用
提示三個延伸話題：  
1. I/O 重導向配合 ssh 可形成跨機器分散式批次。  
2. 透過檔案或 tee 可自由切換批次與管線模式、局部重跑。  
3. 用 dotnet tool 發佈 CLI，可在任何裝有 .NET Core 的環境直接安裝使用。

### 總結
強調後端工程師應熟悉 CLI、STDIO、非同步與生產者／消費者等基礎概念，才能在不倚賴龐大框架的情況下寫出高效、可維護且易於佈署的資料處理工具。CLI + PIPELINE 是兼顧效能、可靠度與可操作性的最佳組合，值得在日常專案與面試題中深入練習。