# 「用 CPU utilization 畫出正弦波」實作筆記

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 微軟這道面試題的內容是什麼？
利用 CPU 使用率（Task Manager 上的 CPU utilization 曲線）畫出一條正弦波。

## Q: 產生正弦波的核心公式與做法是？
把時間切成很細的小段（作者用 100 ms），在第 n 段時間內先算出  
f(x) = (sin x + 1) / 2  
得到 0~1 之間的值，再將該值乘以段長決定「Busy Waiting」時間，其餘時間則讓執行緒 Idle，如此即可讓 CPU 使用率隨時間呈現 sin 波形。

## Q: 為什麼單純的 Busy Waiting 在多核心電腦上不夠用？
Busy Waiting 只能吃滿呼叫它的那一顆 CPU，因此在 4C/8T 的機器上最多只會出現 12.5%（1/8）負載，無法拉出完整波形；作者改用「只配一顆 CPU 的 VM」或多執行緒同時 Busy 來解決。

## Q: 在「讓 CPU 空閒」這件事上，Thread.Sleep() 與 SpinWait.SpinUntil() 的差異與測試結果如何？
1. Thread.Sleep() 精度表面上不差，但在高背景雜訊 (noise threads) 下飄移大，10 ms 可能睡到 31 ms。  
2. SpinWait.SpinUntil() 少掉 context switch 的不確定性，波動較小，但誤差值(延遲)偏大。  
結論：兩者都不完美，需要改良版。

## Q: 作者最後採用哪一種時間控制機制？為什麼？
採用「Advanced SpinUntil」──以外部 Stopwatch 控制 timeout、僅靠 SpinWait 迴圈自行判斷是否跳出。  
理由：在 8 threads 背景干擾下，準確度（平均值最接近目標）與精密度（標準差最小）都最佳，且不依賴硬體 timer 精度。

## Q: 為降低程式本身對 CPU 曲線的干擾，作者做了哪些優化？
1. 所有複雜運算（如 sin）於初始化階段先算完並做成查表。  
2. 把與繪圖無關的運算都算到「Busy」時間內，確保 Idle 區段足夠空閒。  
3. Busy 部分除了必要運算外用 while(true) Busy Waiting 補滿。

## Q: 上述優化後，波形品質有什麼改善？
Task Manager 上的 CPU 使用率曲線由最初雜訊明顯、形狀模糊，進步到幾乎與理想正弦波重合，雜訊顯著降低，視覺上「漂亮很多」。

## Q: 在證明「可以畫任意圖形」的實驗中，作者如何把 Batman Logo 畫到 CPU 曲線？
把 Logo 轉成 ASCII Art 陣列，寫一個 GetDataFromBitmap() 把每個 X 座標對應到「最上方遇到 ‘X’ 的列數」，再換算成「Idle 時間長度」做查表，主程式不變即可畫出 Batman 曲線。

## Q: 作者最終的開源程式碼在哪裡取得？
GitHub 專案 Andrew.CPUDraw  
網址：https://github.com/andrew0928/Andrew.CPUDraw

## Q: 這樣做完作者真的算通過 Microsoft 面試了嗎？
這只是作者的自我挑戰與技術筆記，真正的面試結果還是要看面試官；文章最後作者也自嘲地問：「我這樣算通過 Microsoft 面試了嗎？XDDDD」並未給出肯定答案。