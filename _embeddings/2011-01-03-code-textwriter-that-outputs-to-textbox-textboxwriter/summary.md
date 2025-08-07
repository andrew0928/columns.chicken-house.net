# [CODE] 可以輸出到 TextBox 的 TextWriter: TextBoxWriter!

## 摘要提示
- Azure 移植: 系統搬遷到 Windows Azure 後因分層明確導致 I/O 延遲增加。
- 生產線模式: Worker Role 透過 Pipeline 設計大幅減少 Storage I/O、效能提升十餘倍。
- Windows Service : 以 Service 取代 Task Scheduler，並以 WinForm 方便除錯與控制。
- Console 轉 WinForm: 原本依賴 Console.Out 的程式必須改為可在 TextBox 顯示訊息。
- TextWriter 重用: 保持函式庫接受 TextWriter 的介面，降低程式改動與耦合。
- 多執行緒困難: UI 執行緒限制與輸出交錯需要妥善同步與 Thread-Safe 處理。
- TextBoxWriter 實作: 自訂 TextWriter 派生類別，將輸出導向 TextBox。
- Invoke 必要: 透過 Control.Invoke 保證僅由 UI Thread 操作控制項。
- 效能優化: 直接覆寫 Write(char[] buffer, int index, int count) 以避免一字一字更新。
- 待續議題: 訊息循環回收、跨執行環境紀錄檔寫入等將於下一篇討論。

## 全文重點
作者在 2011 年初忙於將既有系統移轉至 Windows Azure，並把原以 Console App 加 Task Scheduler 執行的排程改寫成 Windows Service。在雲端環境中，Web Role、Worker Role 與 Storage 分層明確，導致大量 I/O 時效能急遽下降，作者藉由「生產線（Pipeline）」設計讓 Worker 端以佇列方式批次存取資料，將速度提升十餘倍。  
為了方便除錯，他先以 WinForm 包裝 Service，提供 START/STOP/PAUSE/CONTINUE 之 UI，但原程式廣泛使用 Console.Out 進行日誌輸出，轉到 WinForm 後就必須顯示於 TextBox，進而遭遇下列問題：  
1. 若改用 TextBox.AppendText() 勢必修改現有大量程式碼，且眾多第三方函式庫仍要求 TextWriter 介面；  
2. 只有建立控制項的 UI Thread 可呼叫 AppendText()；  
3. 多執行緒混寫容易讓輸出交錯不可讀；  
4. 長時間執行會造成 TextBox 內容過多，需要循環；  
5. 實務上仍需同時寫入檔案 Log。  

作者決定以「TextWriter 的多型」解決輸出問題，設計一個能直接綁定至 TextBox 的 TextWriter 衍生類別 TextBoxWriter，讓原本所有 Console.Out 呼叫在 WinForm 環境下無縫轉向 UI 控制項。同時為了 Thread-Safe，他使用 TextWriter.Synchronized() 包裝，再於 TextBoxWriter 中檢查 InvokeRequired，必要時以 Control.Invoke 執行委派，確保僅由 UI Thread 操作 TextBox。效能方面則避免覆寫 Write(char) 逐字更新，而改為覆寫 Write(char[] buffer, int index, int count) 批次處理字串，使輸出流暢。  
完整程式碼展示了類別的建構子、覆寫 Write 與 Encoding 屬性，以及將 AppendText 行為封裝成私有方法。文章最後提及 UI Thread 限制的背景與錯誤訊息，並引用 Darkthread 部落格提供的詳細說明。其餘如訊息回收與跨環境寫檔等議題留待下一篇繼續探討。

## 段落重點
### 前言與近況
作者先以「吃葡萄不吐葡萄皮」開場並祝賀新年，接著說明近月忙於將系統搬遷至 Windows Azure、改寫排程為 Windows Service，並重新拾起過去認為用不到的多執行緒技巧。

### Azure 分層與效能挑戰
在雲端結構中，Web Role、Worker Role、Azure Storage 的分層雖帶來清晰架構，卻也使每層間的通訊耗時明顯；Worker Role 若大量 I/O，速度極差。作者採用「生產線模式」(Pipeline) 讓作業分段併發，測試結果效能提升十多倍，印證「架構對了，事情就簡單」。

### Windows Service 取代 Task Scheduler
第二個重構案例是將原本靠 Task Scheduler 執行的排程程式改成自製 Windows Service；由於 Service 難以直接除錯，作者先用 WinForm 殼層包裝，透過 UI 按鈕控制 START/STOP/PAUSE/CONTINUE，使開發階段更方便。

### Console.Out 移植困境
WinForm 缺乏 Console，因此過去用 Console.Out.WriteLine 輸出的程式需要改成 TextBox.AppendText，但直接修改會破壞大量程式碼，也不符合復用現有接受 TextWriter 的函式庫，並衍生 Thread-Safe、UI 限制、訊息過多等問題。

### TextBoxWriter 設計目標
作者提出需求：維持 TextWriter 介面、可直接綁定 TextBox、支援多執行緒安全、可日後擴充到文件或 Socket，且若能循環回收與寫檔更佳。核心想法是讓所有輸出依然呼叫 WriteLine，但目的地改為 TextBox。

### 使用範例示範
透過 TextWriter.Synchronized(new TextBoxWriter(textBox1)) 建立執行個體後，只要呼叫 output.WriteLine(...)，訊息即不斷於 TextBox 滾動，效果與 Console 視窗相仿，示意圖顯示 terminal 風格輸出。

### TextBoxWriter 實作細節
1. TextBoxWriter 繼承 TextWriter，透過建構子取得 TextBox 參照。  
2. 覆寫 Write(char) 時僅轉呼叫 Write(char[]...) 避免逐字更新；覆寫 Write(char[] buffer,int index,int count) 則在必要時使用 Control.Invoke 執行委派以符合 UI Thread 限制。  
3. AppendTextBox 私有方法實際執行 TextBox.AppendText，寫入後不需額外同步。  
4. Encoding 屬性固定回傳 UTF-8。  
此設計兼顧效能與 Thread-Safe，並能被 TextWriter.Synchronized() 再次包裝增加鎖定。

### UI Thread 鐵律與錯誤示例
若非 UI Thread 更新控制項，執行時會收到「跨執行緒作業無效」警告，作者貼出相關對話框截圖，並引用 Darkthread 文章解釋 UI Thread 限制與 Control.Invoke 用法，強調多執行緒 WinForm 程式必須遵守此規則。

### 收尾與後續工作
目前 TextBoxWriter 已滿足「不改動既有程式即可在 WinForm 顯示日誌」的基本需求，但訊息回收、同步寫入檔案等功能尚待補完。作者自嘲久未寫文，一篇寫不完，只好賣個關子留待下回分解。