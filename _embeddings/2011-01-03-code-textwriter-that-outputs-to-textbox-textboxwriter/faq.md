# [CODE] 可以輸出到 TextBox 的 TextWriter: TextBoxWriter!

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 在 Windows Form 開發時，為什麼不能直接沿用 Console.Out 來輸出執行過程訊息？
1. Windows Form 中顯示訊息通常需要透過 TextBox 之類的 UI Control，而 Console.Out 只會把資料寫到 DOS 視窗或檔案。  
2. UI Control 只能由建立它的 UI Thread 進行操作，直接在背景執行緒呼叫 TextBox.AppendText 會觸發「跨執行緒存取」錯誤。  
3. 如果把程式最後要跑在 Windows Service（沒有 UI）的情境考慮進來，還是保留以 TextWriter 為共用介面最具彈性。  

## Q: 要如何在 Windows Form 中，仍用 TextWriter 介面把訊息即時寫進 TextBox？
透過自訂的 TextWriter 衍生類別「TextBoxWriter」。使用方式如下：  
```csharp
private TextWriter output;
public Form1()
{
    InitializeComponent();
    // 建立與 TextBox 綁定的執行緒安全 TextWriter
    this.output = TextWriter.Synchronized(new TextBoxWriter(this.textBox1));
}

private void Form1_Load(object sender, EventArgs e)
{
    for (int i = 0; i < 300; i++)
        this.output.WriteLine("{0}. Hello!!!", i);   // 與使用 Console.Out 幾乎相同
}
```
程式只需面對 TextWriter 介面，不但保留了既有函式庫的相容性，也讓未來改寫成真正的 Windows Service 時能直接改成檔案或 Socket Writer 而不動到主要邏輯。

## Q: TextBoxWriter 是怎麼實作的？  
核心重點在三件事：  
1. 衍生自 `TextWriter`，覆寫 `Write(char)` 與 `Write(char[] ,int ,int)` 兩個方法即可涵蓋其他 30 多個多載。  
2. 在 `Write(char[] ,int ,int)` 中判斷 `InvokeRequired`，必要時把要寫進 TextBox 的動作包成 delegate，再用 `TextBox.Invoke(...)` 回到 UI Thread 執行，確保 thread-safe。  
3. 為了效能，直接把 char 陣列一次轉為字串後呼叫 `TextBox.AppendText(...)`，避免逐字輸出造成的嚴重延遲。  
完整程式骨架：  
```csharp
public class TextBoxWriter : TextWriter
{
    private TextBox _textbox;
    public TextBoxWriter(TextBox textbox){ this._textbox = textbox; }

    public override void Write(char value){ this.Write(new []{ value }, 0, 1); }

    public override void Write(char[] buffer, int index, int count)
    {
        if (this._textbox.InvokeRequired)
            this._textbox.Invoke((Action<string>)AppendTextBox,
                                 new string(buffer, index, count));
        else
            AppendTextBox(new string(buffer, index, count));
    }

    private void AppendTextBox(string text){ this._textbox.AppendText(text); }
    public override Encoding Encoding => Encoding.UTF8;
}
```

## Q: 為什麼一定得透過 Invoke 再呼叫 TextBox.AppendText，而不能直接寫？
Windows Form 有一條鐵律：  
「只有建立該 Control 的 UI Thread 能改變它的狀態。」  
如果在背景執行緒直接修改 UI Control，執行期就會丟出「Cross-thread operation not valid」警告。把真正的 UI 更新動作（AppendText）包成 delegate，交回 UI Thread 的 `Invoke` 或 `BeginInvoke` 執行，就能安全又正確地更新畫面。  

## Q: 改用 TextBoxWriter 後，輸出效能與可讀性有何改善？
1. 先前若只覆寫 `Write(char value)`，每個字元都會觸發一次 UI 更新，效能低落到「一行字 1 秒」的程度。  
2. 透過同時覆寫 `Write(char[] ,int ,int)`，一次處理成段文字並用 `AppendText` 輸出，可大幅降低 UI 呼叫頻率，效能恢復正常。  
3. 搭配 `TextWriter.Synchronized(...)`，即可確保多執行緒時訊息不會交錯，保持可讀性。