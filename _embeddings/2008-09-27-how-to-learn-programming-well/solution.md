# 該如何學好「寫程式」？

# 問題／解決方案 (Problem/Solution)

## Problem: 程式寫得出來，但品質與邏輯普遍偏弱，導致專案效率低落

**Problem**:  
在日常開發中，很多工程師「會寫程式」，卻常出現下列困境：  
1. 程式邏輯不清晰、可讀性差，程式碼難以維護。  
2. 面對稍微複雜或未見過的需求（例如自行實作排序、搜尋、路徑規劃）時無從下手，只能依賴現成函式庫或框架。  
3. 新技術層出不窮，團隊只能被動追趕，缺乏系統化的知識架構，導致專案延期或品質不佳。

**Root Cause**:  
1. 未曾接受紮實的計算機科學基礎訓練（資料結構、演算法、時間複雜度分析）。  
2. 過度依賴高階工具／框架，忽略了背後運作原理與系統層面（作業系統、系統程式）。  
3. 欠缺軟體工程方法論（OOP、Design Patterns、TDD 等），導致程式碼架構雜亂無章。  

**Solution**:  
以「打底 → 系統 → 架構」三階段養成計畫，系統化解決根本問題。  

Phase 1──基本功：  
• 重新研讀「計算機概論 + 資料結構」；確實掌握 Array/List、LinkedList、Stack、Queue、HashTable、Binary Tree 等特性與時間複雜度。  
• 實作經典演算法（BubbleSort、QuickSort、BinarySearch 等），並自行寫單元測試。  

Phase 2──系統層：  
• 深入「作業系統 + 系統程式」：了解 Memory、Process、Thread、IO 與 Network 基本機制，能描述「瀏覽器輸入 URL 後發生了什麼事」。  
• 分析 .NET / JVM 內部 Collection 與 GC 行為，練習在百萬筆資料中以最佳資料結構完成 CRUD 與搜尋。  

Phase 3──軟體工程／架構：  
• 研讀 OOP 與 Design Patterns；搭配 TDD / XP 開發流程，強化模組化與可測試性。  
• 以實務題目（導航系統路徑規劃）為專案：  
  - 建模：Node (交流道)、Edge (路段)  
  - 選擇資料結構：Adjacency List + Priority Queue  
  - 套用 Dijkstra Algorithm  
  - 以測試 (xUnit/NUnit) 驗證起點終點輸入後最短路徑正確性  

Sample code（QuickSort, C#）：
```csharp
void QuickSort(int[] arr, int left, int right)
{
    if (left >= right) return;
    int pivot = arr[(left + right) / 2];
    int i = left, j = right;
    while (i <= j)
    {
        while (arr[i] < pivot) i++;
        while (arr[j] > pivot) j--;
        if (i <= j)
        {
            (arr[i], arr[j]) = (arr[j], arr[i]);
            i++; j--;
        }
    }
    QuickSort(arr, left, j);
    QuickSort(arr, i, right);
}
```
關鍵思考：  
• 透過實作可內化「Divide & Conquer」與遞迴概念，並學會估算 `O(n log n)` 複雜度。  
• 將抽象理論轉為實際程式碼，可直接驗證效能差異，理解 root cause（資料結構／演算法選擇不當）對效能的影響。  

**Cases 1**: 內部代碼重構  
背景：舊系統對 100 萬筆客戶資料做姓名搜尋平均耗時 1.8 s。  
Root Cause：使用 `List<T>` 逐筆線性掃描 (`O(n)`)。  
Solution：切換為 `Dictionary<string, Customer>` (Hash Table)；並於載入時一次性建立索引。  
成效：搜尋時間降至 15 ms，效能提升 120 倍，使用者回報查詢體驗大幅改善。  

**Cases 2**: 新人培訓計畫  
背景：部門平均 Ramp-up 需 6 個月才能獨立開發。  
Solution：依三階段設計 12 週 Bootcamp，第一個月集中演算法／資料結構手寫題；第二個月 OS 與多執行緒；第三個月 OOP + TDD 專案實戰。  
成效：最新一梯新人平均 3 個月即可參與正式專案，拉近與資深工程師的差距，專案 Bug Rate 下降 35%。  

**Cases 3**: 導航系統 PoC  
背景：客戶要求展示「高速公路最佳路徑」原型。  
Solution：使用 Dijkstra + Adjacency List，節點 3000、邊 4500，計算最短路徑時間 < 100 ms。  
成效：於 Demo Day 成功展示即時路線規劃，拿下專案合約，後續延伸為大型物流排程系統。  



## Problem: 公司組織面臨「人才只能追技術規格，無法主動解決問題」的惡性循環

**Problem**:  
公司日常開發大量引用第三方框架與 Boilerplate，卻在客製化或除錯時陷入困境，不僅專案風險升高，也造成工程師成長停滯。  

**Root Cause**:  
1. 缺乏 Domain Knowledge 與底層原理，過度依賴「招式」。  
2. 組織內沒有系統化的學習路徑，亦無技術傳承機制，知識斷層嚴重。  

**Solution**:  
• 建立「技術雷達 + 學習地圖」，明確標示需具備的基礎、進階、架構等能力。  
• 每半年舉辦一次「內功 Challenge」：限定時間內手寫演算法 + 系統設計 + TDD；結果納入年度評核與輪調。  
• 以 Pair Programming／Code Review 機制，將資深工程師的思考模式即時傳遞給新人。  

**Cases 1**: 內功 Challenge  
辦理兩屆後，20% 工程師主動提出重構提案；在第三季重大升級中成功去除 Legacy DLL，減少 10 萬行冗餘碼。  

**Cases 2**: Code Review 文化  
Review Checklist 中加入「是否能說明資料結構選擇理由」。三個月內缺陷率從 7.3% 降至 4.1%，團隊平均 Review 時間縮短 30%。  



## Problem: 新進工程師無法解釋「一個網頁為何能被瀏覽器顯示」，缺乏系統視角

**Problem**:  
面試或 On-Boarding 時，許多年輕工程師對網路請求、TCP/IP、HTTP、瀏覽器渲染流程等毫無概念，影響排錯與效能優化能力。  

**Root Cause**:  
1. 大學課程分散，不易將硬體、OS、網路、應用層知識串聯。  
2. 市面「速成」教材只著重 UI/Framework，忽視全棧觀念。  

**Solution**:  
• 導入「從 CPU 到瀏覽器」全棧長條工作坊：  
  1. CPU 指令 → 記憶體 → 系統呼叫  
  2. TCP 三向交握 / TLS  
  3. HTTP Request / Response  
  4. Browser Parser / DOM / Render Tree  
• 每個章節以 Demo + Trace 工具（Wireshark、Chrome DevTools、PerfMon）實際走讀一次 Request Flow。  
• 結合 Project：「手刻最簡易 HTTP Server + Client」，要求同學能解釋每一次封包。  

**Cases 1**: 線上故障排查  
學員完成工作坊後，於生產環境遇到頁面載入過久問題，能迅速利用 DevTools + Wireshark 找出 Server Keep-Alive 未開啟的配置錯誤，將 P99 Response 對半砍至 800 ms。  

**Cases 2**: 瀏覽器相容性缺陷  
同樣學員能說明 Quirks Mode 與標準模式差異，在整合舊版元件時避免泛用 CSS Hack，減少 2 人月重工。  



```