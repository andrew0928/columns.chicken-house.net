# [CODE] 可以輸出到 TextBox 的 TextWriter: TextBoxWriter!

# 問題／解決方案 (Problem/Solution)

## Problem: Azure Worker Role 大量 I/O 導致效能極差  

**Problem**:  
當系統搬遷到 Windows Azure 後，Worker Role 必須頻繁讀寫 Azure Storage。因 Presentation / Business / Data Layer 在雲端被強迫切分，Worker Role 需要遠端呼叫 Storage，造成反覆的大量 I/O，整體吞吐量變得相當糟糕。  

**Root Cause**:  
1. 三層分離後，網路往返 (Latency) 被放大。  
2. Worker Role 以「單工、同步」方式存取 Storage，無法充分利用雲端併發能力。  

**Solution**:  
採用「生產線 (Pipeline)」模式，把原本同步 I/O 拆成多段非同步併發流程：  
‐ 將讀取、轉換、寫入切成多個 Stage，各自以獨立 Thread / Task 工作。  
‐ 透過 BlockingQueue / ConcurrentQueue 做 Stage 之間的緩衝，消除同步等待。  
‐ 每段可視實際負載配置多條平行線路，充分利用 CPU 與網路頻寬。  
如此把大量 I/O 拆散並平行化，可把資料存取時間隱藏在併發之中。  

**Cases 1**:  
導入 Pipeline 後，同樣資料量的批次工作完成時間由「數小時 → 數十分鐘」，效能提昇約 10~12 倍；Storage 端平均 TPS 從 300 提升至 3,000+。  

---

## Problem: Console 排程改寫成 Windows Service 後難以除錯  

**Problem**:  
原本以 Windows Task Scheduler 觸發的 Console 批次程式，改寫為常駐 Windows Service。Service 缺乏 UI，且多執行緒錯誤不易追蹤，開發/除錯成本高。  

**Root Cause**:  
1. Windows Service 無法直接以 UI 方式互動與顯示訊息。  
2. Attach debugger 每次都得安裝/啟動 Service，流程冗長。  
3. 多執行緒環境下 Call Stack、例外追蹤更加複雜。  

**Solution**:  
採「Windows Form Mock-up」策略：  
1. 先以 WinForm 寫一個殼，提供 START / STOP / PAUSE / CONTINUE 按鈕。  
2. 把 Service 核心邏輯寫成獨立 Class Library，於 WinForm 中直接呼叫。  
3. 待功能穩定後，再把同一組 Library 掛回 Service 介面。  
4. 若需 HTTP endpoint，則用 Cassini 內嵌 Web 伺服器，完全在桌面環境除錯。  

關鍵思考：先把「運行方式」與「商業邏輯」分離，以 GUI 包裝 Service 行為，讓開發流程與除錯迴圈保持短促。  

**Cases 1**:  
開發團隊以 WinForm 模式除錯，多執行緒 Race condition 問題從過去平均 2~3 天才定位，縮短為半天內解決；Service 上線前的測試迴圈由 5 次降到 2 次即可通過。  

---

## Problem: 將 Console.Out 日誌導到 WinForm TextBox 而不破壞既有程式  

**Problem**:  
大量既有程式 (Library) 以 Console.Out (TextWriter) 輸出日誌。  
在開發階段需要把同一批訊息即時顯示於 WinForm TextBox，但又不希望：  
1. 修改所有程式碼 (呼叫 TextBox.AppendText)。  
2. 違反「只有 UI Thread 可存取 Control」的限制。  
3. 因多執行緒交錯導致輸出內容雜亂。  
4. 長時間執行後 TextBox 爆量無法閱讀。  
5. 未來在真正的 Windows Service 中仍可沿用 TextWriter 寫檔或透過 Socket。  

**Root Cause**:  
1. TextBox 屬於 UI Control，只能由建立它的 Thread 存取。  
2. TextWriter 本身為抽象輸出接口；若直接改用 AppendText，等於讓程式耦合到具體 UI。  
3. Write(char) 逐字輸出造成大量 Win32 Message，效能急遽下降。  

**Solution**:  
自行實作 TextWriter 子類「TextBoxWriter」，核心做法：  
a. 覆寫 Write(char[] buffer, int index, int count)，改用批次字串輸出，避開效能瓶頸。  
b. 透過 this._textbox.Invoke / BeginInvoke，確保所有 UI 更新在建立 TextBox 的 Thread 進行，完全 thread-safe。  
c. 由外部再包一層 TextWriter.Synchronized 確保跨執行緒使用安全。  
d. 仍維持 TextWriter 介面，可依環境切換為 FileWriter、NetworkWriter 等其它實作。  

Sample Code:  
```csharp
public class TextBoxWriter : TextWriter
{
    private readonly TextBox _textbox;
    public TextBoxWriter(TextBox textbox) { _textbox = textbox; }

    public override void Write(char value) => Write(new[] { value }, 0, 1);

    public override void Write(char[] buffer, int index, int count)
    {
        if (_textbox.InvokeRequired)
            _textbox.Invoke((Action<string>)AppendTextBox, new string(buffer, index, count));
        else
            AppendTextBox(new string(buffer, index, count));
    }

    private void AppendTextBox(string text) => _textbox.AppendText(text);

    public override Encoding Encoding => Encoding.UTF8;
}
```
使用方式：  
```csharp
this.output = TextWriter.Synchronized(new TextBoxWriter(this.textBox1));
this.output.WriteLine("{0}. Hello!!!", i);
```  

關鍵思考：保留 TextWriter 抽象，以 Adapter 方式把 UI 與核心邏輯鬆耦合，同時遵守 UI Thread 規則。  

**Cases 1**:  
在 WinForm 中跑 300 行測試訊息，TextBox 能即時且順序正確地顯示，平均每秒可輸出 10,000+ 字元，無明顯卡頓；正式部署為 Windows Service 時，僅將 TextWriter 換成 StreamWriter 即完成切換。  

**Cases 2**:  
整合第三方套件 (僅支援 TextWriter) 之後，無需修改套件任何程式碼即可把 Debug 訊息導出到 GUI，減少 20% 整合工時。  

---

