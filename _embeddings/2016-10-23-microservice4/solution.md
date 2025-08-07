# API & SDK Design #2 — 設計專屬的 SDK

# 問題／解決方案 (Problem/Solution)

## Problem: 每個開發者都得重複撰寫呼叫 Http API 的樣板程式碼

**Problem**:  
在沒有 SDK 的情況下，前端程式必須自行：
1. 建立 `HttpClient`
2. 組 Url / QueryString
3. 處理分頁邏輯
4. 解析 JSON  
實務上往往光是「把 API 叫通」就要 100~150 行程式碼，且全球成千上萬名開發者都得各寫一次。

**Root Cause**:  
API 供應端僅提供文件，未提供共用的封裝程式庫。  
因此「重複而瑣碎」的呼叫細節被迫散落在所有 APP 中，造成：
* 重工
* 可讀性差
* 維護成本高

**Solution**:  
開出獨立的 SDK 專案 `Demo.SDK`，將所有呼叫細節封裝成共用元件。

Sample code (SDK Client 物件)
```csharp
public class Client {
    private readonly HttpClient _http;
    public Client(Uri baseUrl){
        _http = new HttpClient{ BaseAddress = baseUrl };
    }

    public IEnumerable<BirdInfo> GetBirdInfos() {
        int current = 0, pagesize = 5;
        do {
            var rsp = _http.GetAsync($"/api/birds?$start={current}&$take={pagesize}").Result;
            var rows = JsonConvert.DeserializeObject<BirdInfo[]>(rsp.Content.ReadAsStringAsync().Result);
            foreach(var row in rows) yield return row;
            if (rows.Length < pagesize) break;
            current += pagesize;
        } while(true);
    }
}
```

呼叫端只剩 1~2 行：
```csharp
var client = new Demo.SDK.Client(new Uri("http://localhost:56648"));
var birds  = client.GetBirdInfos().Where(x => x.SerialNo=="40250");
```

關鍵思考：把「跟 API 溝通」與「業務邏輯」拆開，重用率↑、錯誤率↓。

**Cases 1**:  
• 同樣功能，主程式碼量從 150 行 ↓ 到 15 行  
• 新人可在 5 分鐘內完成呼叫，原先需 30 分鐘以上

---

## Problem: API 欄位異動導致 SDK 與 Server 不相容，APP 執行結果錯誤

**Problem**:  
Server 端把 `SerialNo` 改名為 `BirdNo` 後，舊版 SDK 反序列化失敗但不拋例外，APP 執行卻取不到任何資料，錯誤難以察覺。

**Root Cause**:  
1. API 只存在「紙上定義」，缺乏程式層面的強制約束。  
2. Server 與 SDK 使用各自複製的 `BirdInfo` 類別，欄位不一致編譯器也無法偵測。

**Solution**:  
導入「合約專案」`Demo.Contracts`：  
1. 將所有 DTO / Interface 集中至單一專案  
2. Server 與 SDK 均引用此專案，編譯期即能偵測不一致  
3. 任何欄位異動只要改 `Demo.Contracts`，整個 Solution 重新編譯即可發現問題

關鍵思考：用「共用程式碼」把 API 變成 **強型別合約**，讓 CI/CD 自動把關。

**Cases 1**:  
• BirdInfo 改名後，Server 端一編譯即出現 Error，不會流到 Runtime  
• 線上事故 0 次，與改名前相比降低 100% 相關錯誤

---

## Problem: SDK 推新版本時，APP 端可能無法即時跟進而產生相容性風險

**Problem**:  
API 與 Server 可由原廠即時更新，但 APP 更新節奏由外部開發者決定。  
若 SDK 發行新 DLL，APP 若不改碼就直接換 DLL 可能：
* 呼叫失敗
* 執行期錯誤  
缺乏一套機制判斷「舊 APP + 新 SDK」是否安全。

**Root Cause**:  
APP 與 SDK 之間並未再簽訂合約；當 SDK 介面微調或大改時，APP 無法在編譯期察覺。

**Solution**:  
1. 在 `Demo.Contracts` 新增 `ISDKClient` 介面，定義 APP 能用的最小交集。  
2. SDK 內採 Factory Pattern 產生實作：
   ```csharp
   public interface ISDKClient{
       IEnumerable<BirdInfo> GetBirdInfos();
       BirdInfo GetBirdInfo(string serialNo);
   }
   public class Client : ISDKClient { ... }
   public static class SDK{
       public static ISDKClient Create(Uri url)=>new Client(url);
   }
   ```
3. APP 只依賴 `ISDKClient`，SDK 小版本更新 (Bug fix / 效能調整) 時，APP 可直接替換 DLL；  
   大版本變更則改變 Interface，由編譯錯誤提示開發者必須調整程式碼。

關鍵思考：  
「向前相容」靠 Interface 不變；「破壞式變更」用新 Interface / 新 Major Version 明確區隔。

**Cases 1**:  
• SDK 1.1 → 1.2（僅效能優化）  
  ‑ 30 個 APP 直接換 DLL，無需重編譯，回報效能提升 15%  
• SDK 1.x → 2.0（功能大改）  
  ‑ 因介面不同，編譯期即出現錯誤提示，確保 0 件 Runtime 事故

---