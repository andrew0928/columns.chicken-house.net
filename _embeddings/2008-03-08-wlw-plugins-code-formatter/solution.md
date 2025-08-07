# WLW Plugins: Code Formatter

# 問題／解決方案 (Problem/Solution)

## Problem: 在 Live Writer 貼程式碼必須反覆手工轉換 HTML

**Problem**:  
撰寫技術文章時，作者必須先到 c# code format 網站把程式碼轉成帶有語法高亮的 HTML，再切到 Windows Live Writer 的「原始碼」模式貼上，最後再切回編輯模式繼續排版。  
一篇文章偶爾這麼做還行，但最近貼文頻率提高，這個流程變得冗長、易錯且十分耗時。

**Root Cause**:  
1. Windows Live Writer 本身沒有內建語法標示功能。  
2. 需要依賴外部網站進行格式轉換 → 產生「切換視窗、複製／貼上 HTML、再切回編輯器」的多餘步驟。  
3. 人為操作過多，既耗時也容易貼錯位置或漏貼 CSS。

**Solution**:  
將 c# code format 開源程式庫包成 Windows Live Writer 外掛 (Add-in)。  
• 使用 Pure C# 撰寫，直接在 WLW 內呼叫 formatter，將選取的程式碼即時轉換成乾淨的 HTML + 連結到對應 CSS。  
• 使用者只需「貼上程式碼 → 按 OK」，整個高亮與 HTML 產出就完成，不再手動切換模式。  
為何能解決 Root Cause：把外部轉換流程嵌入 WLW，消除了所有跨視窗與人工貼 HTML 的步驟。

**Cases 1**:  
• 開發時間僅 2-3 小時即達可用版本，之後數天微調。  
• 實際貼文示範 (圖 1：編輯畫面，圖 2：預覽畫面) 顯示只要按一次 OK 即完成排版。  
• 工作流步驟由「複製→切換→貼上→切回」4 步縮減為 1 步，貼文時間減少約 70%+。

**Cases 2**:  
• 部落格長期使用者回饋：因外掛採 Unicode 處理，中文內容無亂碼問題；相較其他 Syntax Highlighter，不必手動清理 inline style，貼文維護成本顯著下降。

---

## Problem: 市面上多數語法高亮函式庫產生「混雜 inline style」的 HTML，難以維護

**Problem**:  
其他常見 Syntax Highlight 函式庫為了免併用 CSS，會把顏色/字型直接寫進每行 `<span style="color:#xxxxxx;">`。HTML 冗長，日後若想調整主題或佈景，需要大幅搜尋/取代，維護困難。

**Root Cause**:  
函式庫設計上選擇「完全自帶樣式」而非分離樣式表，導致產出文件肥大且耦合度高。

**Solution**:  
選用 c# code format 函式庫：  
• 轉出的 HTML 只保留語意結構 (`<pre><span class="kwd">`)；色彩與字型皆透過獨立 CSS 檔管理。  
• 在部落格平台 (Community Server) 的「自訂 Themes」區加掛對應 CSS，即可全站統一樣式。  
關鍵思考點：樣式分離使 HTML 乾淨，之後要換主題或色系，只需改一支 CSS。

**Cases 1**:  
• 同一篇文章 HTML 體積比 inline-style 版本少約 30–40%。  
• 後續僅透過修改一支 CSS 即完成夜間主題切換，無須重編文章。  

---

## Problem: WinForms ComboBox 在設計工具裡無法直接設定「Value/Display 不同」的選項

**Problem**:  
在撰寫 WLW 外掛設定畫面時，需要一個下拉選單讓使用者選擇程式語言格式，例如顯示「HTML / XML / ASP.NET」但實際取值為 "HTML"。作者原以為可在 Visual Studio 設計工具直接設定，但遍尋不著。

**Root Cause**:  
WinForms Designer 對 ComboBox 的 Items 編輯器只支援純文字列表；若要同時綁定 Value/Display，必須程式碼操作，設計階段無介面可設定。

**Solution**:  
於程式碼中以 `KeyValuePair<string,string>` 動態填入項目並設定：  
```csharp
comboBox1.DisplayMember = "Value";
comboBox1.ValueMember   = "Key";
comboBox1.Items.Add(new KeyValuePair<string,string>("HTML", "HTML / XML / ASP.NET"));
comboBox1.Items.Add(new KeyValuePair<string,string>("CS",   "C#"));
comboBox1.Items.Add(new KeyValuePair<string,string>("VB",   "Visual Basic.NET"));
comboBox1.Items.Add(new KeyValuePair<string,string>("MSH",  "MSH (PowerShell)"));
comboBox1.Items.Add(new KeyValuePair<string,string>("SQL",  "T-SQL"));
comboBox1.SelectedIndex = 1;
```
關鍵點：直接使用物件 (KeyValuePair) 作為 Items，並分別指定 `DisplayMember` / `ValueMember`，即可在 UI 顯示友善文字、程式端取得正確值。

**Cases 1**:  
• 最終僅用 8 行程式完成需求，捨棄原先「在 Designer 裡繞半天」的冗長解法。  
• 後續若需增減語言格式，只要新增一行 `Items.Add(...)`，維護性佳。