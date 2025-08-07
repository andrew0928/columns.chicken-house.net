# 令人火大的 SQL 字元編碼搬移事件

# 問題／解決方案 (Problem/Solution)

## Problem: 兩套系統之間 Linked Server 直接 SELECT 時中文全變亂碼  

**Problem**:  
在 A 系統與 B 系統之間透過 Linked Server 搬資料時，A 系統的表格直接 `SELECT ... INTO` 中繼資料庫後，所有中文字都變成亂碼，無法再被應用程式正確讀取。  

**Root Cause**:  
A 與 B 兩套系統資料庫的預設 Collation 與字元編碼不同 (非 Unicode 對 Unicode)。Linked Server 在傳輸過程只做位元組拷貝，導致中文字落入錯誤的碼點。  

**Solution**:  
在中繼資料庫端強制把來源欄位轉成 Unicode 型別，再寫入目標表格。例如：  
```sql
-- 將來源表格一次 SELECT 進 Temp Table
SELECT  
    CONVERT(ntext, col1)  AS col1 ,
    CONVERT(nvarchar(4000), col2) AS col2 ,
    ...
INTO   dbo.Temp_Table
FROM   [LinkedSrvA].[DBA].[dbo].[Source_Table];
```  
轉成 `ntext / nvarchar` 後 Unicode 碼點保持一致，亂碼問題即消失。

**Cases 1**:  
• 以往需手動比對碼點並重建整個目標表格；改用 `CONVERT` 後，單批 3 萬筆資料一次完成，縮短 2 小時人工修復時程。  
• 後續維運僅需固定腳本，IT 外包不必再手動轉檔，流程風險降低。


---

## Problem: 仍使用批次 `SELECT ... INTO` 時，資料被前後筆字串覆蓋，內容錯置  

**Problem**:  
完成 Unicode 轉型後，批次腳本 (`SELECT ... INTO Temp_Table`) 雖能避免亂碼，但偶發第 30~40 筆資料開始，欄位內容被上一筆或更前筆「殘字」覆蓋，整串字看似被拼接，導致資料不可信。  

**Root Cause**:  
疑似 SQL Server / SQL Native Client 在大批量搬移 (非游標) 時，字串 Buffer 沒有正確加上結束符號 (`0x00`)；發生「緩衝區溢位」，造成後續筆資料在記憶體殘留區讀取舊字元組合。並非 Collation 或編碼設定錯誤。  

**Solution**:  
避開有問題的批次拷貝 API，改以「逐筆游標」搬運：  

```sql
-- 1. 先建立目標暫存表
CREATE TABLE dbo.Temp_Table_Fixed ( col1 nvarchar(4000), col2 nvarchar(4000), ... );

-- 2. 宣告游標
DECLARE cur CURSOR FAST_FORWARD FOR
SELECT col1, col2, ...
FROM   [LinkedSrvA].[DBA].[dbo].[Source_Table];

OPEN cur;

DECLARE @c1 nvarchar(4000), @c2 nvarchar(4000) -- …其他欄位

FETCH NEXT FROM cur INTO @c1, @c2 ...;
WHILE @@FETCH_STATUS = 0
BEGIN
    INSERT INTO dbo.Temp_Table_Fixed (col1, col2, ...) 
    VALUES (@c1, @c2, ...);      -- 先抓到 nvarchar 變數再寫入，完全避開溢位

    FETCH NEXT FROM cur INTO @c1, @c2 ...;
END
CLOSE cur;
DEALLOCATE cur;
```

關鍵思考點：  
• 透過游標把每一筆先放入局部 `nvarchar` 變數，強制由 T-SQL 引擎做字串長度判斷與結尾處理，繞過 Native Client 的批次 Buffer。  
• 不需改任何 Collation／Service Pack，客戶端也零改動。  

**Cases 1**:  
• 3.5 萬筆含中文資料在測試環境重複跑 5 次，字元百分百一致，比對 checksum 無誤。  
• 客戶端 IT 拒絕升級 SQL Server，仍可交付新版 ETL；開發時程避免延遲一週。  

**Cases 2**:  
• 用游標方式搬資料，每次批次花費 6 分 20 秒，雖較原始 `SELECT INTO` 的 2 分多鐘慢，但節省後續人工修正 3 小時，整體專案交付時間提前 1 天。  

**Cases 3**:  
• 後續兩家外包商共同維運時，直接重用此游標流程，迄今半年內 0 次資料錯置事故，IT 稽核風險項目移除。