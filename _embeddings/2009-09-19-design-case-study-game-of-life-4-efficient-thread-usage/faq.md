# [設計案例] 生命遊戲 #4, 有效率的使用執行緒

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼必須重新設計第 3 篇中使用的執行緒模型？
在 30×30 的生命遊戲世界裡，舊版程式一次就開出 903 條執行緒，但 CPU 使用率不到 5%，顯示大量執行緒都在閒置等待。若將此設計用在多人連線遊戲的伺服器，極易因執行緒暴增而資源耗盡，必須改進效能與可擴充性。

## Q: 舊版 (第 3 篇) 的 30×30 範例實際會啟動多少條執行緒？
共 903 條。

## Q: 透過 yield return 與集中排程後，大約只需要多少條執行緒就能達到同樣效果？
僅需 9 條執行緒。

## Q: 把 Thread.Sleep(...) 改成 yield return TimeSpan 的最大好處是什麼？
Thread.Sleep 會讓每個 Cell 擁有專屬執行緒自行睡眠，yield return TimeSpan 則把「要休息多久」回報給 GameHost，讓 GameHost 透過少量共用執行緒與執行緒集區排程 Cell 的後續行為，顯著降低執行緒數量並提高效率。

## Q: GameHost 改寫後如何決定何時喚醒各 Cell？
1. 建立一份時間排序的 CellToDoList。  
2. GameHost 從清單取出下一個要被喚醒的 Cell。  
3. 若時間未到就 Thread.Sleep(預定時間 – 現在)。  
4. 時間到時，將 Cell 的 OnNextStateChangeEx 交給 ThreadPool 執行。  
5. Cell 回傳下一次喚醒時間後，GameHost 再把它丟回清單，持續循環。

## Q: CellToDoList 對外提供哪些核心方法？
• AddCell(Cell)：加入並依預定喚醒時間排序。  
• GetNextCell()：取出時間最早的 Cell。  
• CheckNextCell()：只查看、不取出下一個 Cell。  
• Count：目前排程中的 Cell 數量。

## Q: 為什麼要改用執行緒集區 (ThreadPool) 來執行 Cell 的邏輯？
執行緒集區能重複使用少量執行緒來處理大量短命工作，減少大量 idle thread 帶來的記憶體與排程成本，同時讓作業系統更有效率地利用 CPU 資源。