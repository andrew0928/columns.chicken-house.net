```markdown
# Case Study: BlogEngine -> WordPress 大量(舊)網址轉址問題處理

# 問題／解決方案 (Problem/Solution)

## Problem: 新舊系統 URL 格式差異，造成大量 404 舊連結失效  

**Problem**:  
部落格從 BlogEngine 1.6 (.NET) 搬遷到 WordPress 後，原先約 400 篇文章各自衍生 6 種 URL 形態（含日期、不含日期、有無多重部落格路徑、以 GUID 為參數等）。外部網站與搜尋引擎仍大量引用舊網址，若不轉址將出現 2400+ 個 404，影響 SEO 與讀者體驗。

**Root Cause**:  
BlogEngine 與 WordPress 的網址產生邏輯完全不同，且 BlogEngine 歷史版本曾改版導致多重 URL 形態並存；遷移時缺乏對應表，搜尋引擎因此抓到的全是不存在的新主機路徑。

**Solution**: Phase-1 臨時解法 – 以 Apache `Redirect 301` 為每一條舊網址建立對應規則  
1. 撰寫 C# 工具掃描 400 篇文章，自動產生 2400 行設定：  
   ```apache
   Redirect 301 /post/2008/07/10/GoodProgrammer1.aspx /?p=65
   Redirect 301 /columns/post/2008/07/10/GoodProgrammer1.aspx /?p=65
   ...
   ```  
2. 一併部署在 Synology NAS 前端的 Apache Reverse Proxy。

**Cases 1**: Google Search Console 的 404 錯誤不再持續上升，舊網址可立即取得 301 轉址。  
**Cases 2**: 不須修改 WordPress 本身，完成遷移當週即恢復多數外部連結的可用性。  


## Problem: 2400 條 Redirect 規則難以維護且拖慢回應時間  

**Problem**:  
手動/自動產生的 2400 行 `Redirect` 與主站設定檔混在一起：  
• 例外狀況（日期寫錯）無法涵蓋  
• 每次修改都得重新產生整份設定  
• Apache 需線性比對所有規則，NAS CPU 低效能下反應時間可達 4 s

**Root Cause**:  
Apache `Redirect`/`RewriteRule` 會依序比對 (O(n))。未命中的請求需跑完整清單；且逐條字串比對對例外值毫無容錯能力。

**Solution**: Phase-2 改寫 – 使用 `RewriteRule + RegExp` 將 6 種格式濃縮為 1 條規則/文章  
```apache
RedirectMatch 301 ^/?(columns/)?post(/\d+)?(/\d+)?(/\d+)?/([^.]+)\.aspx /?p=65
```  
• 400 篇文章→400 條規則  
• RegExp 容許日期欄位缺失或錯誤，提升容錯  
• 統一產生腳本，維護量較 Phase-1 減少 80%

**Cases 1**: 設定檔大小大幅縮減，閱讀與版本控制更單純。  
**Cases 2**: Google Search Console 額外抓出的「日期錯誤網址」亦能正確導向。  
**Cases 3**: 仍屬線性比對；效能雖有改善但不顯著，需再尋更佳方案。  


## Problem: Regex 規則仍需線性比對，在 NAS 上效能不足  

**Problem**:  
400 條 RegExp 每次請求都要執行，絕大多數請求其實已是新 WordPress URL，卻仍被迫跑完整比對，NAS CPU 相對吃緊。平均回應時間維持在 1 s 以上，尖峰高達 4 s。

**Root Cause**:  
`RewriteRule` 本質仍是順序掃描；Regex 比對屬 CPU-bound。缺乏散列表式 O(1) 查詢，導致效能瓶頸。

**Solution**: Phase-3 最終解法 – 導入 `RewriteMap` Hash Table  
1. 啟用模組並宣告對照表  
   ```apache
   RewriteEngine On

   RewriteMap slugmap "txt:/volume/slugmap.txt"
   RewriteRule "^(/columns)?/post(/\d+)?(/\d+)?(/\d+)?/(.*)\.aspx" \
               "?p=${slugmap:$5}" [R=301,L]
   ```  
2. `slugmap.txt` 只存 slug → WordPress post id，約 400 行  
   ```
   GoodProgrammer1       65
   RUNPC-2008-11         52
   ...
   ```  
3. 以 `httxt2dbm` 轉成 `.dbm`，查表時間複雜度 O(1)。  
4. 完整轉址邏輯縮成「1 行 regex + 1 份對照表」，維護與效能兼顧。

**Cases 1**: Google Search Console 平均回應時間由 1130 ms 降至 907 ms，約 20% 改善 (11/06→11/11)。  
**Cases 2**: 404 Not Found 由 1000+ 筆壓到剩 6 筆（均為實際死鏈接）。  
**Cases 3**: 未來若新增文章僅需 append `slugmap.txt`，無須改動 Apache conf；維運成本極低。
```