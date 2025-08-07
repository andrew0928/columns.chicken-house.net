# WLW Plugins: Code Formatter

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼作者最後決定自己動手寫一個 Windows Live Writer 的 Code Formatter 外掛？
作者原本使用線上 c# code format 網站後再手動切換到 Live Writer 的 HTML 模式貼回文章，但隨著貼程式碼的頻率增加，這種做法過於耗時；試用過其他 Syntax Highlight 外掛又發現中文會亂碼，因此決定直接將 c# code format 的程式庫包成 WLW 外掛，一勞永逸。

## Q: 使用這個 Code Formatter 外掛最大的好處是什麼？
貼完程式碼按一下「OK」就完成排版，省去手動修改 HTML 的繁瑣流程，整體速度與便利性大幅提升。

## Q: 作者為何選擇 c# code format 這套程式庫來實作外掛？
1. 完全以 C# 撰寫，程式短小但架構佳。  
2. 作者長期使用其網站版本，對輸出格式熟悉。  
3. 產生的 HTML 乾淨，只需額外搭配一份 CSS。  
4. 支援 Unicode，不會出現中文亂碼問題。

## Q: 使用外掛時還需要做哪些額外設定？
必須把 c# code format 附帶的 CSS 加到部落格（或佈景主題）中，才能讓轉出的程式碼保持乾淨又美觀的樣式。

## Q: 在開發過程中，WinForms 的 ComboBox 遇到什麼困難？最終如何解決？
作者想用設計工具直接設定「Value / Display」不同的選項，但找遍 Designer 與 MSDN 都沒辦法一次完成，只好在程式碼中手動新增項目，示例如下：  

```csharp
comboBox1.DisplayMember = "Value";
comboBox1.ValueMember   = "Key";
comboBox1.Items.Add(new KeyValuePair<string,string>("HTML", "HTML / XML / ASP.NET"));
...
comboBox1.SelectedIndex = 1;
```

## Q: 想下載這個 WLW Code Formatter 外掛應去哪裡？
外掛與原始碼可從作者部落格下載：  
http://www.chicken-house.net/files/chicken/ChickenHouse.LiveWriterAddIns.zip