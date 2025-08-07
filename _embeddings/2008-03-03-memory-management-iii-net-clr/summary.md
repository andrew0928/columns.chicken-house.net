# Memory Management (III) - .NET CLR ?

## 摘要提示
- 指標與碎裂: C/C++ 的指標無法重定位記憶體，導致嚴重的記憶體碎裂問題。
- 參考型語言: Java、C# 拿掉 pointer、改用 reference，讓執行期得以搬移記憶體區塊。
- Compact GC: 具備「搬移並壓縮」能力的 compact collection 可從根本排除碎裂。
- 測試程式: 以 C# 改寫的範例，先配置 64 MB 塊，再交錯釋放後配置 72 MB 塊以驗證碎裂影響。
- 預設行為: .NET 2.0 Workstation GC 無法回收並重新利用零碎空間，測試失敗。
- 手動收集: 呼叫 GC.Collect 亦僅回收可達物件，仍難解決碎裂。
- gcConcurrent: 關閉並行 GC 對結果無實質幫助。
- gcServer: 啟用 Server GC 後，CLR 會進行 compact collection，成功消除碎裂並取回大區塊空間。
- 文件缺漏: 官方文件僅描述效能差異，對 Server GC 可執行 compact collection 著墨甚少。
- 實務啟示: 在需要長時間大量配置/釋放、易產生碎裂的伺服器程式，可透過 gcServer 取得最佳記憶體利用率。

## 全文重點
作者延續前兩篇記憶體管理文章，探討在 .NET 環境裡是否能根除記憶體碎裂問題。C/C++ 程式因為可直接存取 pointer，執行期無法任意移動已配置區塊，只能任其碎裂；而較新的 Java、C# 語言取消 pointer，改以受控 reference，使 CLR/JVM 有機會在垃圾回收時搬移物件並重新壓縮堆積 (heap)。這種「回收＋壓縮」的流程稱為 compact collection，理論上能徹底消除碎裂。

為驗證理論，作者將先前的 C 範例改寫為 C#：持續配置 64 MB byte 陣列直到 OutOfMemoryException，然後釋放隔列的記憶體塊，再嘗試配置 72 MB 塊，觀察可否成功。結果在 .NET 2.0、預設 Workstation GC 下仍失敗，顯示釋放後的零碎空間未被有效整合。作者接著嘗試手動 GC.Collect 並指定最高世代，情況依舊；再把 gcConcurrent 關閉亦無助益。最後開啟 `<gcServer enabled="true"/>`，結果立刻改善：釋放 576 MB 空間後，得以重新配置 648 MB 大塊記憶體，證實 Server GC 會執行 compact collection，因而消除碎裂。

雖然 MSDN 與 Google 上對 gcServer 的描述多聚焦於「伺服器情境效能較佳」，卻很少明講其可執行壓縮回收。透過 Reflector 也難以窺探其內部實作，因相關邏輯已進入 native 層。不過此次實驗明確示範了：在需要長時間、高頻率、大量配置/釋放的應用（如伺服器程式），開啟 Server GC 能顯著提升可用記憶體與穩定度。文章最後附上完整測試程式碼與 app.config 範例，供讀者在不同平台自行驗證。

## 段落重點
### 問題背景與動機
作者回顧前兩篇以 C 程式示範的記憶體碎裂問題，提出疑問：若改用 .NET 開發是否早已「自動」解決？同時也說明選擇冷門題材的寫作動機。

### Pointer 與碎裂的根本原因
指出 pointer 讓編譯器與執行期無法搬移記憶體，導致碎裂不可避免；而移除 pointer、僅留下 reference 的語言則讓執行期擁有重新配置空間的可能。

### GC 與 Compact Collection 理論
說明 .NET／JVM 的自動垃圾回收可在「回收」的同時「壓縮」存活物件 (compact)，此即 compact collection，可望徹底避免碎裂；但「能做到」與「預設會做」並非同義，需要實測驗證。

### 實驗設計：C# 版本程式
介紹測試程式：以 List<byte[]> 連續配置 64 MB 區塊，釋放交錯區塊，再配置 72 MB 區塊觀察成敗；測試平台為 Vista x86、.NET 2.0。

### 預設 GC、手動 GC 與 gcConcurrent 的測試結果
在 Workstation GC 下即使手動 GC.Collect、或關閉 gcConcurrent，都無法重新利用釋放的零碎空間，顯示仍受碎裂限制。

### 啟用 gcServer 的突破
將 app.config 設定 `<gcServer enabled="true"/>` 後重測，發現 GC 會執行壓縮並成功配置更大記憶體，大幅改善碎裂問題；此結果亦間接證實 Server GC 內含 compact collection 機制。

### 結論與心得
總結 .NET CLR 具備解決碎裂的能力，但需以 gcServer 明確啟用；官方文件對此著墨不足，實務上開啟 Server GC 對長效、高負載程式極具價值；作者也鼓勵讀者下載程式碼在不同平台重複實驗。