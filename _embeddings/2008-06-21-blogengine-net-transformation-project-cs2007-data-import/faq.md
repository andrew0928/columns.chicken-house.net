# [BlogEngine.NET] 改造工程 - CS2007 資料匯入

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼作者在已經匯入 90% 資料後仍決定「重匯」而不是直接接受結果？
因為剩下的 10% 資料（例如原 CS PostID、PageViewCount 等）對作者來說非常重要；若當下不一次補齊，之後就再也無法回溯補回，等同永久遺失。

## Q: 作者為何沒有直接修改 BlogEngine.NET 內建的 BlogML WebService 匯入工具？
1. 官方匯入工具未公開 Source Code，不易客製。  
2. 每篇文章與每則回應都各觸發一次 WebService Call，效率低。  
3. 介面缺漏多項關鍵欄位（如原 CS PostID、瀏覽計數等），要補齊必須同時改 Client 端與 WebMethod，工程太大。  
綜合考量後，作者認為「重寫一支匯入程式」反而比較快。

## Q: 作者最後採取了什麼匯入策略？
以 BlogEngine 的 .ASMX 原始碼為範本，另外寫了一支 .ASHX：  
1. 先把 CS2007 匯出的 BlogML 放在 ~/App_Data。  
2. 於 .ASHX 中讀取 BlogML，分別處理 Post 與 Comment（兩層迴圈即可）。  
3. 先完成原有 90% 匯入，再分階段補足缺漏資訊。

## Q: 在第二階段補資料時，作者需要額外匯入哪些欄位？
1. 每篇文章的 PageView Counter  
2. 每則回應的完整作者／IP 等詳細資訊  
3. 每篇文章的「舊 ID（CS2007）」與「新 ID（BlogEngine）」對照  
4. 各種網址修正（圖檔、站內連結……）  
5. 原匯入程式的瑕疵修正（如 Modified Date 錯誤）

## Q: CS2007 內的 Comment 相關額外資訊（匿名者名稱、IP 等）為何無法直接由 BlogML 取得？
因為 CS2007 把這些欄位序列化後塞進 [cs_posts] 的 PropertyNames 與 PropertyValues 兩欄；BlogML 並未定義此結構，所以必須自行解析那串自訂格式的大字串。

## Q: 如何解析 PropertyNames／PropertyValues？
PropertyNames 以 `{Name}:{Type}:{StartPos}:{EndPos}:` 方式連續存放；  
PropertyValues 是實際值的長字串。  
程式需先掃描 PropertyNames 取出每個欄位的起迄位置，再到 PropertyValues 切割對應字元區段。作者寫了一段 C#「硬解」程式將結果轉成 XML，之後再匯入。

## Q: 要把 SQL 查詢結果快速轉為 XML，作者用了什麼技巧？
在 SQL Server 2005 Management Studio 執行：  
```sql
select PostID,PostAuthor,PropertyNames,PropertyValues
from cs_posts
where ApplicationPostType = 4
for xml auto
```  
點擊結果即可存成 XML，只需手動補上根節點即可。

## Q: 圖檔網址從 CS2007 改寫到 BlogEngine.NET 時，最終採用的 Regular Expression 是什麼？
```
(http\://(columns|community)\.chicken\-house\.net)?/blogs/chicken/([a-zA-Z0-9\-_\./%]*)
```  
用來抓出 `/blogs/chicken/` 之後的路徑，再組成 `image.axd?picture=...` 形式的新網址。

## Q: 為何修正「站內文章連結」必須採兩階段 (2-Pass) 處理？
第一次匯入時還不知道 BlogEngine 為每篇文章產生的新 GUID/Slug，新網址無法當場替換；因此先完整匯入並紀錄「舊 ID ➜ 新 ID」對照表，再進行第二次掃描替換。

## Q: 用來擷取舊 CS2007 文章 ID 的 Regular Expression 是？
```
(http\://(columns|community)\.chicken\-house\.net)?/blogs/chicken/archive/\d+/\d+/\d+/(\d+)\.aspx
```  
其中最後一個括號 `(\d+)` 即取得舊的 PostID (例：1234)。

## Q: 舊網址仍被外站引用時如何自動導向到新網址？
作者實作了一支 HttpHandler：`CSUrlMap.cs`  
1. 先以 Regex 判斷請求路徑是否符合舊 CS2007 格式。  
2. 解析出舊 PostID，查對照表取得新 URL。  
3. 利用 `Context.Server.Transfer` 將流量導向 `AutoRedirFromCsUrl.aspx`，顯示說明後再跳轉至新文章。  

## Q: 這次搬遷最大的心得或結論是什麼？
雖然整體屬於「雜七雜八的小事集合」，耗時約一週，但驗證了：  
1. BlogEngine.Core 的 Library 結構簡潔、易於客製。  
2. 重新撰寫匯入程式比修補既有工具快速且彈性高。  
3. 先把資料保完整，再談版面與功能，才不會留下永久遺憾。