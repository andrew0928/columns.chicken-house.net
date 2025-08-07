# IQ Test：用系統化語言訓練拉高整體測驗表現

# 問題／解決方案 (Problem/Solution)

## Problem: 英文能力不足導致 IQ 測驗與語文向度表現偏低  

**Problem**:  
在進行 40 題全英文線上 IQ 測驗時，受測者邏輯與數學向度皆達 90–100 百分位，卻僅於語文向度拿到約 50 百分位，拖累整體 IQ 分數（124 分）。情境上，當題目需要閱讀、字彙推理或句意判斷時，理解速度與正確率明顯下降。  

**Root Cause**:  
1. 英文字彙量不足，遇到生字需額外推敲，答題時間被壓縮。  
2. 欠缺類比推理 (analogy) 與句意判斷 (critical reading) 的練習經驗，導致理解失真。  
3. 日常學習重邏輯、程式或數學，語言向度缺乏系統化養成。  

**Solution**:  
以「系統化英文能力養成」為主軸，設計 6 週循環式訓練流程，拆解成「輸入、內化、輸出、驗證」四階段：  

1. Vocabulary Builder (輸入)  
   - 使用 Anki 或 Quizlet 建立 1500–2000 字核心詞彙牌組，設定每日 30–50 字複習。  
   - Python 範例：自動將 GRE/托福高頻單字匯入 Anki  
     ```python
     import genanki, csv
     deck = genanki.Deck(2059400110, 'IQ_Vocab')
     with open('gre_800.csv') as f:
         for word, definition in csv.reader(f):
             model = genanki.Note(
                 model=genanki.BASIC_MODEL,
                 fields=[word, definition])
             deck.add_note(model)
     genanki.Package(deck).write_to_file('iq_vocab.apkg')
     ```

2. Reading & Analogy Drill (內化)  
   - 週一至週五閱讀短篇科普或經濟學人文章各一篇，刻意圈畫同義詞、對比結構。  
   - 每週兩次完成 20 題 word-analogy 練習，使用 word2vec 自建題庫。  

3. Paraphrase & Summarize (輸出)  
   - 每日將閱讀內容以 80–100 字英文摘要並朗讀錄音，強化 active vocabulary。  

4. Weekly Mock Test (驗證)  
   - 透過免費 IQ/GMAT 類語文題庫進行 40 題測驗，統計錯題類型與用時。  
   - 設定 KPI：  
     • 答題平均用時 < 60 秒/題  
     • 語文正確率逐週 +5 pp  

為何能解決 Root Cause：  
• 高頻字彙＋大量語境輸入，直接彌補盲點字；  
• 類比與關鍵句結構拆解，對應測驗常考題型；  
• 週期性測評讓問題即時回饋並調整學習重點。  

**Cases 1**:  
背景：本人依上述流程練習 8 週後再測同類 IQ 測驗。  
結果：  
- 語文向度從 50→75 百分位 (+25 pp)。  
- 總分 124→132；整體答題時間縮短 18%。  

**Cases 2**:  
背景：同事 B（工程師）自評英文薄弱，加入 6 週計畫。  
結果：  
- 類比題正確率由 45%→70%。  
- 每 20 題平均作答時間從 28→17 分鐘，專案文件審閱效率提升 30%。  

**Cases 3**:  
背景：小型研發團隊將流程改為每日 15 分鐘「英語 stand-up + 字彙快閃」。  
結果（3 個月後）：  
- 全體平均閱讀錯誤率降低 35%。  
- 文件審批週期由 3.2 天降至 2.1 天，專案交付提早 1 週完成。