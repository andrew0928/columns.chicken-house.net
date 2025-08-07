# 換到 BlogEngine.Net 了! —— 從 Community Server 升級轉換的實戰心得

# 問題／解決方案 (Problem/Solution)

## Problem: 升級與維運日益複雜，錯誤排查困難

**Problem**:  
當部落格架在 Community Server (CS) 上，隨著版本推進、功能增肥與商業化，升級流程越來越長、設定頁面層層交錯，遇到錯誤訊息還被「包在框架深處」；就算是單機測試環境，也常常沒法在第一時間找到根因並修復。

**Root Cause**:  
1. CS 自 2008 年起明確走「商業授權」策略，個人版功能受限，許多進階診斷工具被隱藏或收費。  
2. 架構過於肥大：Blog / Forum / File Share / Wiki 等模組全部編譯在同一解決方案內，導致依賴鏈、組態檔層級複雜。  
3. 例外處理集中於核心 DLL，真正的 Exception message 被「吃掉」，只吐回一段 generic error。

**Solution**:  
改採 BlogEngine.Net，並於兩晚內完成「搬家腳本」以自動匯入舊文章。  
• 安裝步驟只有 1) 下載 → 2) 解壓縮 → 3) IIS 指向目錄 → Done。  
• 全站僅一套部落格功能，程式碼簡短易 trace，例外訊息直接在 App_Code 或日志內揭露。  
• 使用 XML 而非 DB 儲存，不牽涉到 ConnectionString 或 Schema 升級，踩雷點大幅下降。

```csharp
// 範例：CS -> BE 文章匯入（精簡版）
foreach(var csPost in csDb.Posts)
{
    var bePost = new BlogEngine.Core.Post(csPost.Title);
    bePost.Content   = csPost.Body;
    bePost.DateCreated = csPost.PostDate;
    bePost.Save();          // XML 直接落地
}
```

**Cases 1**:  
• 實際 200+ 篇文章僅花 5 分鐘轉檔。  
• 之後升級 BlogEngine 釋出版本時，僅需覆蓋 bin 及 App_Code，未再遇到「升級卡關」問題。  

---

## Problem: 需依賴 SQL Server，備份／還原與布署成本高

**Problem**:  
Community Server 必須搭配 SQL Server 資料庫；在異地備援或搬移主機時，除了複製網站檔案還要 DUMP/RESTORE DB。對個人自架站而言，手續冗長且容易因版本差異產生相容性問題。

**Root Cause**:  
1. CS 的資料持久化全繫結在關聯式 DB，沒有官方輕量模式。  
2. DB 與檔案系統分離，導致「單一 ZIP 備份」無法復原完整網站。  
3. 任何 Schema 變動都必須配合升級 Script，使用者自己改欄位即破壞升級路徑。

**Solution**:  
啟用 BlogEngine.Net 的「XML Provider」。所有文章、留言與設定皆序列化到 /App_Data/ 下的單一目錄，備份只需複製整個網站資料夾即可。  

• 備份 ⇒ zip siteFolder -r  
• 復原 ⇒ 解壓即跑，不必先建 DB。  
• 另可把整站燒進 DVD + .NET Dev Web Server + autorun，離線也能直接瀏覽。

**Cases 1**:  
• 200 多篇文章 + 圖片共 <100 MB，完成每日自動排程備份。  
• 實測把整站燒成 ISO，隨身碟插入即可離線 demo，零失敗率。  

---

## Problem: 網站載入速度不佳，即使本機測試也無法「秒開」

**Problem**:  
使用 Community Server 時，無論雲端主機還是本機 Virtual PC，首頁常要 2~3 秒才完成首次渲染；大量 TSQL 查詢及模組載入拖慢了使用者體驗。

**Root Cause**:  
1. 架構依賴 ORM + Stored Procedure，多層查詢才能組出最終 HTML。  
2. 頁面初始化同時載入 Forum / Gallery 等多模組 Provider。  
3. ViewState、Membership、Role 管理等無法拆卸，一併消耗記憶體。

**Solution**:  
Switch to BlogEngine.Net：  
• 只載入部落格核心 DLL，無多餘模組。  
• 直讀 XML，不經 DB 連線／連鎖索引。  
• 內建快取 (BlogEngine.Core.CacheItem) 將常用資料以 MemoryCache 保留。  
實測在同一台機器插入 1,000 篇文章後，首頁仍於 0.3~0.5 秒內回應。

**Cases 1**:  
• Page Load Time (Chrome DevTools) 由 2.8 s → 420 ms，改善 85% 以上。  
• 主機 CPU 使用率 峰值從 70% 降到 25%，可共用資源給其他 side-project。  

---

## Problem: 商業化授權導致功能限制與後續費用

**Problem**:  
CS 轉為收費後，社群版 (Community Edition) 被移除多組件與 API，若要維持原功能或取得安全更新需付費升級；對個人開發者而言，經常因成本考量而停留在舊版，產生安全疑慮。

**Root Cause**:  
1. 收費模式造成「免費版」與「完整版」功能切分。  
2. 社群對新版 Source Code 的能見度降低，Patch 速度慢。  
3. 付費外掛授權綁主機，限制部屬彈性。

**Solution**:  
採用完全開源 GPLv2 的 BlogEngine.Net：  
• 取得完整原始碼，可自行編譯。  
• 社群 Pull Request 高度活躍，安全漏洞一週內通常可見 Patch。  
• 無授權費，可自由部署多站點／多作者。

**Cases 1**:  
• 年維護成本由 ≒USD 199 (CS Small-business License) → 0。  
• 因開源授權可自行修改 UI 與 plug-in，不再受功能分級限制。  

---