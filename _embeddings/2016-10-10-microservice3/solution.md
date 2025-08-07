# API & SDK Design #1 – 資料分頁的處理方式

# 問題／解決方案 (Problem/Solution)

## Problem: 客戶端因資料分頁造成「義大利麵式」程式碼

**Problem**:  
在開發者呼叫 API 時，後端一次只傳回部分資料（分頁），開發者必須：  
1. 自行維護 `$start / $take` 迴圈邏輯  
2. 不斷累加結果再進行篩選  
3. 將資料重組後再交給上層使用  
結果導致流程控制、分頁邏輯與商業邏輯混雜，程式碼難以維護，被戲稱為「義大利麵式 (Spaghetti)」程式碼。

**Root Cause**:  
API 端僅提供最陽春的分頁功能，沒有額外 SDK/Wrapper；Client 端必須手動：  
• 計算起始筆數、呼叫次數  
• 接收回傳資料後再自行組裝  
• 把查詢條件硬塞進分頁迴圈中  
分頁控制與商業邏輯耦合，難以重用與測試。

**Solution**:  
在 SDK 端利用 C# `yield return` 實作 Iterator Pattern，將「取資料」與「用資料」分離。  
Sample Code (擷取重點)：  
```C#
static IEnumerable<Dictionary<string,string>> GetBirdsData()
{
    int current = 0, pagesize = 5;
    do{
        var result = client.GetAsync($"/api/birds?$start={current}&$take={pagesize}").Result;
        var objs   = JsonConvert.DeserializeObject<Dictionary<string,string>[]>(result.Content.ReadAsStringAsync().Result);
        foreach(var item in objs)      // 一筆一筆往外 yield
            yield return item;
        if(objs.Length < pagesize) break;
        current += pagesize;
    }while(true);
}
```
呼叫端只需關心 LINQ / foreach：  
```C#
foreach(var b in GetBirdsData().Where(x=>x["Location"]=="玉山排雲山莊"))
   ShowBirdInfo(b);
```
關鍵思考點：  
• `yield return` 把一次「五筆」分開成「一筆一筆」傳給呼叫端。  
• Iterator 尚未走到盡頭就不會做下一次 HTTP 呼叫，程式碼乾淨且延遲載入。  
• 商業邏輯 (Where / Select) 完全寫在 Iterator 之外，可單元測試。

**Cases 1**:  
• 原始作法：20 行 loop 控制，3000 ms 才跑完 1000 筆  
• `yield` 作法：主程式僅 3 行 LINQ + foreach，結構清楚  
  – 逐頁取 5 筆 → 逐筆處理 → 再決定是否往下取  
• 維護者只需讀懂 GetBirdsData 即可重複利用，降低認知負擔。

**Cases 2**:  
• 只需第一筆符合條件 (`.Take(1)` 或 `break`) 時：  
  – 舊寫法仍把 1000 筆全部撈完  
  – Iterator 寫法在找到第 1 筆 (第 50 筆資料) 即停止，耗時降至 266 ms。

---

## Problem: 搜尋單一/少量資料時無謂地撈完所有分頁

**Problem**:  
使用者往往只想抓到第一筆 / 前 N 筆符合條件的資料，卻被迫把全部頁次都撈完，產生多餘的網路流量與延遲。

**Root Cause**:  
迴圈控制寫死於「全部取回 → 再篩選」模式；沒有機制告訴資料來源「我已經找到需要的資料，停止呼叫」。

**Solution**:  
利用 `yield return` + `foreach` + LINQ `.Take()` 或 `break`：  
1. Iterator 逐頁呼叫 API → 把結果逐筆 `yield` 出去  
2. Caller 於 foreach 內 `break` 或 `.Take(N)`，Enumerator 立即結束  
3. 迴圈自動釋放 Enumerator，後續 HTTP 呼叫不再發生

**Cases**:  
• Demo 中搜尋 SerialNo = 40250  
  – Iterator 每頁 5 筆，僅呼叫到第 10 頁 (0~50) 即停止  
  – 執行時間 266 ms，相較完整掃描 3000 ms 明顯縮短  
  – 總 HTTP 呼叫次數由 100 次降至 10 次。

---

## Problem: 客戶端過濾導致大量不必要的資料傳輸

**Problem**:  
伺服器未提供進階查詢 (filter / order / select)，Client 端只能撈完所有資料再過濾，浪費頻寬與 CPU。

**Root Cause**:  
Server 僅回傳 `IEnumerable` 分頁結果，無 `IQueryable` / OData 支援。  
• 無法把查詢條件下推到資料庫 / 服務端  
• 必須做 Table Scan 式的全表走訪

**Solution**:  
生產環境建議：  
1. 在 Server 端實作 OData 或自訂 Query DSL，讓查詢條件於伺服器端處理  
2. 回傳 `IQueryable`，由 OData Provider 將 LINQ 轉成 `$filter=...&$top=...`  
3. Client 端只拿到「已過濾」的小量資料，可與 `yield return` 串接

關鍵思考點：  
• `IQueryable` 允許延遲查詢並下推至資料來源 (SQL、NoSQL…)  
• 節省網路流量、提升回應速度，也避免 Client 重覆撰寫 filter 邏輯

**Cases**:  
• 以同樣 1000 筆資料測試：  
  – 無 OData：Client 共收 1000 筆，傳輸量 ≒ 1 MB+  
  – 有 OData `$filter=Location eq '玉山排雲山莊'`：Server 僅回 55 筆，流量瞬降 95％  
  – 客戶端只需 iterate 55 筆，CPU/記憶體消耗大幅降低。