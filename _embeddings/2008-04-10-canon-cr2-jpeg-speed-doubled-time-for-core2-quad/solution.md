# Canon CR2 → JPEG 速度加倍，要換 Core2 Quad 嗎？

# 問題／解決方案 (Problem/Solution)

## Problem: .CR2 轉 .JPEG 時 CPU 利用率始終上不去  

**Problem**:  
在將大量 Canon .CR2 Raw 檔批次轉換成 .JPEG 時，即使使用 ThreadPool 把可並行的工作全部排滿，CPU 占用率仍然常年停在單核心水位，導致整體歸檔流程被「最後一批 .CR2 檔」拖慢。  

**Root Cause**:  
1. Canon Codec 在同一個 Process 內「不可重入」，Converted 方法被上鎖，導致無法同時使用兩顆以上 CPU。  
2. 雖然程式把其餘可並行的步驟（搬檔、產縮圖等）都填滿 ThreadPool，但真正花時間的轉檔仍然只能單線程執行，成為系統瓶頸。  

**Solution**:  
1. 將「.CR2 → .JPEG」邏輯抽離成獨立可執行檔 (converter.exe)。  
2. 歸檔主程式同時啟動兩份 converter.exe，讓 Canon Codec 各跑在自己的 Process 內，避開「同一進程不可重入」的限制。  
3. 控制流程：  
   ```csharp
   // pseudo code
   var tasks = new List<string>(Directory.GetFiles(cr2Folder, "*.cr2"));
   while (tasks.Any())
   {
       var slice = tasks.Take(2).ToArray();       // 同時跑兩個
       tasks.RemoveRange(0, slice.Length);

       var p1 = Process.Start("converter.exe", slice[0]);
       var p2 = slice.Length > 1 ? Process.Start("converter.exe", slice[1]) : null;

       p1.WaitForExit();
       p2?.WaitForExit();
   }
   ```  
4. IPC/回傳值以「檔案存在與否」與 Process ExitCode 判斷轉換結果，省去複雜的管線通訊，亦不影響總轉檔時間。  
5. 關鍵思考：把鎖粒度從「執行緒」放大到「Process」後，Canon Codec 的限制就不再互相影響，多核心終於能被吃滿。  

**Cases 1**:  
• 測試環境：Intel Core 2 Duo E6300  
• 原流程：單 Process，單張 .CR2 需 70 秒；CPU 使用率 ≈ 45%  
• 新流程：兩個 Process 並行，70 秒可完成 2 張，等同每張 35 秒；CPU 使用率 ≈ 80%  
• 效益：加工速度翻倍，CPU 利用率提升 ~35%，無需改動硬體。

**Cases 2**:  
• 工作量：一次 120 張婚禮 RAW 檔  
• 原估時：120 × 70s ≈ 140 分鐘  
• 新估時：120 ÷ 2 × 70s ≈ 70 分鐘  
• 實際執行：71 分鐘完成，落差 <2%  
• 成效：交件時間從「兩個小時多」壓縮到「一小時整」。  

**Cases 3**:  
• 後續在四核心 (Q9450) 機器上開四個 Process，再次驗證：  
  - CPU 使用率可逼近 95%  
  - 單張 RAW 轉檔有效時間降到 ~18 秒  
  - 整體 Throughput 約為舊流程的 3.8 倍  
• 結論：軟體瓶頸解除後，升級硬體才真正有感。