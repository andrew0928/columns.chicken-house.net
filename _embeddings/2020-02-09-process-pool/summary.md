# 微服務基礎建設: Process Pool 的設計與應用  

## 摘要提示
- 隔離層級選擇: 透過 In-Process、Thread、AppDomain、Process 等技術比較啟動與執行效能，確認 Process 隔離最符合需求。  
- .NET Core 優勢: Core 版在記憶體、I/O 與演算法最佳化上全面勝出，主控端與工作端皆建議優先採用。  
- IPC 通訊策略: 跨 Process 採 STDIO/Pipe 等 OS I/O 機制可簡化串接，示例以 STDIO Redirect 實作。  
- Benchmark 方法: 以空轉與實負載、VALUE 與 BLOB 兩種參數模式，量測啟動速率與 Task 吞吐量。  
- Process 建立成本: 單機一秒僅能啟動 ~23 個 Process，與每秒可執行超過 3.7 萬 Task 的落差高達千倍。  
- Process Pool 構想: 以 Thread Pool 思維擴大至 Process，透過 min/max pool size 與 idle timeout 動態調控。  
- 100 行實作: 使用 BlockingCollection + 專屬 Thread 照護 Process，完成動態擴縮、CPU Affinity 與 Priority。  
- 效能提升: 同樣 .NET Core 版本，Process Pool 將單機吞吐提升約 2~3 倍，重負載下可達近 9 倍差距。  
- Auto-Scaling 示範: 依 queue 壓力自動增減 Process，閒置時回收以釋放 RAM，降低雲端成本。  
- 架構決策觀點: 基礎原理 + 局部自製 + 既有基礎設施（k8s/VM）結合，才能在可靠度、效能與維運間取得平衡。  

## 全文重點
本文從實務需求出發：在大型微服務系統內，眾多開發團隊的非同步任務需併存於同機器或同叢集執行，為避免「惡鄰居」問題（記憶體耗盡、CPU 爭奪、靜態狀態污染、未捕捉例外造成整個行程終止），必須提供隔離機制，同時又要兼顧啟動速度與執行效能。  
作者首先比較 In-Process、Thread、AppDomain、Process 四種隔離技術，以「環境啟動速率」與「Task 執行吞吐」為指標，並在 .NET Framework、.NET Core、兩種參數傳輸策略（VALUE／BLOB）及空轉／實負載多維度測試。結果顯示：  
1. In-Process 與 Thread 幾乎無隔離，僅作為對照組；  
2. AppDomain 雖能隔離 managed 物件，但綁死 .NET Fx，且效能仍劣於 Process + Core；  
3. Process 隔離雖啟動最慢，但在 .NET Core 加持下，執行吞吐可與 In-Process 接近，遠勝 AppDomain；  
4. .NET Core 在 SHA512 與 I/O 等最佳化下普遍快於 .NET Fx。  
因此最終結論：主控端與工作端盡量使用 .NET Core，隔離層級採 OS Process，跨行程通訊使用 STDIO/Pipe。  
然而 Process 建立成本高昂，若每個 Task 均新啟一行程將嚴重浪費。作者遂將十年前自製 Thread Pool 的理念延伸，撰寫「Process Pool」。核心邏輯只有約 100 行程式碼：  
• 以 BlockingCollection 作為 Producer/Consumer Queue；  
• Thread 對應單一 Process，負責接收 Task、處理與回報；  
• 依 queue 長度與 idle timeout 動態增刪 Process，遵循 min/max pool size；  
• 終止流程以 AutoResetEvent 協調，確保 Stop 時所有工作完成；  
• 額外支援 CPU Affinity 與 Process Priority 以保護系統其他服務。  
Benchmark 顯示，相同 1 MB Hash 計算場景，單獨 Process 約 55 tasks/sec，而 Process Pool 可達 184 tasks/sec；在 .NET Fx + AppDomain 的舊方案僅 21 tasks/sec，效能差距近 9 倍。  
最後作者回顧決策脈絡：公有雲 serverless 與 container orchestration 雖成熟，但受限於 Windows/.NET Fx 相容、DB Connection Reuse、低頻任務資源浪費等因素，仍需自建局部機制；藉由 Process Pool 管理單機內可重用的工作行程，再交由 k8s 或雲端 Auto Scaling 進行 VM/Pod 級擴縮，可在可靠度、效能與成本三者之間得到最佳折衷。  

## 段落重點
### 挑戰: Isolation 的機制研究
作者列舉 In-Process、Thread、GenericHost、AppDomain、Process、Hypervisor 六種層級，說明各自隔離強度與適用性；接著以啟動空程式、執行計算 SHA512 等 benchmark 比較不同平台與參數模式下的效能。結果顯示 Process + .NET Core 結合時效能/彈性最佳，而 AppDomain 雖較快啟動但被 Core 淘汰，不宜再投資。

### 為何需要建立隔離環境
從多團隊共用 Worker 的真實痛點出發，說明未隔離時記憶體、CPU、靜態變數、未捕捉例外等問題；示範 AppDomain 靜態污染實驗，並討論 Serverless 與 Container 在 Windows/.NET Fx 支援、冷啟動、連線池等限制。結論是單機層面須自建隔離，跨機器再交給雲端或 k8s。

### 自行建置 Process Pool 的編排機制
將 Thread Pool 概念移植到 Process：維持 min/max pool size、idle timeout、自動增減，並以 BlockingCollection 同步。完整 100 行程式碼涵蓋 Process 啟動、IPC (STDIO)、排程、回收、Stop 等待，以及 CPU Affinity、Priority 等進階調整。Benchmark 證實在 1 KB 與 1 MB 載荷下可獲 2~3 倍至 9 倍效能提升。

### 最後結論
Process Pool 用極少程式碼即可達到類 k8s 的單機行程調度效果；適時「自己造輪子」能填補現有框架不足又避免過度相依。關鍵是以應用需求為核心，理解基礎原理，在成熟基礎設施與自製機制間取得平衡；對團隊與雲端成本皆大幅受益。  

