---
layout: post
title: "架構面試題: RDBMS 處理樹狀結構的技巧"
categories:
- "系列文章: 架構師觀點"
tags: [""]
published: true
comments: true
redirect_from:
logo: /wp-content/images/2019-06-01-nested-query/2019-06-01-23-22-03.png
---

![](/wp-content/images/2019-06-01-nested-query/2019-06-01-23-22-03.png)
> 圖片來源: https://pixabay.com/photos/tree-landscape-field-branch-696839/


架構面試題，這系列好久沒寫了。這次來探討一下，怎麼用 RDBMS 來處理樹狀結構的做法吧。

即使 NOSQL 風行了這麼多年，現在還是有不少服務背後是用 RDBMS 在處理資料的。RDBMS + SQL 是個絕配，將資料轉成表格，加上結構化的查詢就能解決過去 80% 的問題了。不過 Tree 這種資料結構，在 RDBMS 裡面就是格格不入。幾種 Tree 的基本操作，在 RDBMS 裡面都要花些心思轉換才能夠妥善處理。例如不限定階層的儲存、查詢某個節點以下 (不限定階層) 的所有子節點，或是 Tree 的搬移、刪除等等操作都是。如果用 RDBMS 的關聯性來處理 Tree Node 跟 Node 之間的關聯，就會衍生幾個階層就需要 Join 幾次的困境 (我不可能無限制的一直 Join 下去啊)。如果搭配特殊語法 (如 T-SQL CTE), 或是用 programming language 搭配或許能夠解決, 不過你就必須在複雜度與效能間做取捨了。

我覺得這是個不錯的題目，能鑑別出你的基礎知識夠不夠札實，能否靈活運用；也能看出你是否容易被既有的工具或是框架限制住做法的測驗。這邊先不討論 tree 到底該不該擺在 RDBMS 上面處理這種議題，那是另一個層次的討論。如果背後的 storage 就限定在 RDBMS 的話，我想探討的是我們有哪些方法能夠妥善的處理他?


<!--more-->




# 開始前的準備

我先把需求收斂定義一下好了。樹狀的資料很多，我就先以最常見的 file system 為例子就好。 File system 有目錄 (folder) 跟檔案 (file) 兩種主要的 node, folder 是個容器，底下可以包含其他的 folder 或是 file. 不考慮 shortcut 或是 symbol link 這類機制的話，一個 folder 或是 file 不能同時放在一個以上的 folder 內。簡單的說就是個標準的 tree 結構。

我期望在這樣的結構下，要有效率的完成這幾種 operation:

1. 搜尋某個目錄下 (包含所有子目錄) 符合的檔案清單
1. 目錄搬移 (move) 的操作
1. 目錄刪除 (delete) 的操作

為了準備測試資料，我特地寫了個小程式，把我目前電腦的 C:\ 下所有的目錄與檔案爬出來，存到 SQL database 內當作範例。基本上我的電腦大概就是裝好 windows 10 + visual studio 而已，沒有太多有的沒的東西 (我沒勇氣爬 D:\ 給大家看 XDD)。以我寫這篇文章當下的狀態，我的 C:\ 的狀況如下:

```text
- Total Dir(s):  218817
- Total File(s): 1143165
- Total File Size: 231712 MB
- Max Dir Level: 18
- Max Files In One Dir: 83947
- Total Scan Time: 1199.4157913 sec. (FPS: 953.101508494371 files/sec)
```


接下來，後面的例子都會用同一份資料為準來進行這幾項測試，並且用 SQL 的執行計劃來評估 cost:

1. 模擬 dir c:\windows 的結果，列出 c:\windows 下的目錄與檔案清單，統計檔案的大小
1. 模擬 dir /s /b c:\windows\system32\*.ini, 找出所有位於 c:\windows\system32 目錄下 (包含子目錄) 所有副檔名為 .ini 的檔案清單
1. 模擬 mkdir c:\windows\backup
1. 模擬 move c:\windows\system32 c:\windows\temp\system32
1. 模擬 rm /s /q c:\windows\system32 (叔叔有練過，好孩子不要學)




# 方案 1, self relation / join

最直覺的方式，就是這個 self join 的做法了。基本的結構就是一個目錄一筆資料。除了相關 metadata 之外，關鍵的欄位就是自己的 ID，以及上一層 ID。舉例來說，若有這個 Tree:

![](/wp-content/images/2019-06-01-nested-query/2019-05-30-23-00-38.png)

那麼資料表應該長這樣:

| ID | PARENT_ID |
|----|-----------|
|A|NULL|
|B|A|
|C|A|
|D|C|
|E|C|


用這概念，直接拉出 SQL table schema:

![](/wp-content/images/2019-06-01-nested-query/2019-05-27-23-19-57.png)


很直覺的結構，設計 schema 本身是小事，直接來看看這五項需求該如何面對...



## 需求 1, 查詢指定目錄下的內容

> 1. 模擬 dir c:\windows 的結果，列出 c:\windows 下的目錄與檔案清單，統計檔案的大小

直接來看一下，這結構該怎麼處理這兩個查詢需求。要列出檔案與清單，其實是小菜一碟。先找出 c:\windows 的目錄 ID:

```sql

declare @root int;
select @root = D2.ID
from demo1.DIRINFO D1 inner join demo1.DIRINFO D2 on D1.ID = D2.PARENT_ID 
where D1.NAME = 'c:\' and D2.NAME = 'windows'

print @root

```

知道 c:\windows 的目錄 ID 之後，剩下的需求就很無腦了，不做解釋直接看結果:

```sql

declare @root int;

select @root = D2.ID
from demo1.DIRINFO D1 inner join demo1.DIRINFO D2 on D1.ID = D2.PARENT_ID 
where D1.NAME = 'c:\' and D2.NAME = 'windows'

-- list DIR
select NAME from demo1.DIRINFO where PARENT_ID = @root

-- list FILE
select NAME, SIZE from demo1.FILEINFO where DIR_ID = @root


```

查詢結果:

![](/wp-content/images/2019-06-01-nested-query/2019-05-27-23-43-08.png)





要模擬就模擬到位一點，格式調整一下:

```sql

declare @root int;

select @root = D2.ID
from demo1.DIRINFO D1 inner join demo1.DIRINFO D2 on D1.ID = D2.PARENT_ID 
where D1.NAME = 'c:\' and D2.NAME = 'windows'


select * from
(
	select '<DIR>' as type, name, NULL as size from demo1.DIRINFO where PARENT_ID = @root
	union
	select '' as type, NAME as name, SIZE as size from demo1.FILEINFO where DIR_ID = @root
) IX order by name asc

```

查詢結果:

![](/wp-content/images/2019-06-01-nested-query/2019-05-27-23-28-02.png)


跟我自己的電腦執行 ```dir c:\windows``` 的結果對照一下:

```
C:\Windows>dir /a
 Volume in drive C is OS
 Volume Serial Number is 1C40-8489

 Directory of C:\Windows

2019/05/11  上午 10:20    <DIR>          .
2019/05/11  上午 10:20    <DIR>          ..
2018/09/15  下午 03:33    <DIR>          addins
2018/12/02  上午 08:42    <DIR>          appcompat
2019/05/23  下午 10:14    <DIR>          apppatch
2019/05/27  上午 08:03    <DIR>          AppReadiness
2019/05/27  上午 08:08    <DIR>          assembly
2019/05/23  下午 10:14    <DIR>          bcastdvr
2018/09/15  下午 03:28            78,848 bfsvc.exe
2018/09/15  下午 05:08    <DIR>          BitLockerDiscoveryVolumeContents
2018/09/15  下午 03:33    <DIR>          Boot
2019/05/27  下午 08:12            67,584 bootstat.dat
2018/09/15  下午 03:33    <DIR>          Branding

(中間內容省略)

2018/09/15  下午 03:29            11,776 winhlp32.exe
2019/05/25  下午 07:11    <DIR>          WinSxS
2018/09/15  下午 05:08           316,640 WMSysPr9.prx
2018/09/15  下午 03:29            11,264 write.exe
2018/12/01  下午 12:12    <DIR>          zh-TW
              35 File(s)     16,313,953 bytes
              81 Dir(s)  233,929,641,984 bytes free

C:\Windows>

```

這查詢沒甚麼困難，扣掉檔案系統內建的 ```.``` 跟 ```..``` 兩個目錄， SQL 查詢的總數跟 DIR 列出來的數字是一致的，第一題算是輕鬆過關。





## 需求 2, 查詢指定目錄下的內容 (遞迴)

1. 模擬 dir /s /b c:\windows\system32\*.ini, 找出所有位於 c:\windows\system32 目錄下 (包含子目錄) 所有副檔名為 .ini 的檔案清單


這個開始棘手一點了。麻煩的部分是，每要往下找一層，就得將 DIRINFO 自己跟自己 self join 一次，就可以往下找一層。但是我不知道有幾層啊? 因此要嘛搭配 code 用遞迴 (recursive) 的方式一路查下去，或是 SQL 必須在有限的階層下通通找一次，不過這兩個方法都不大好看，重點是難以直接在 SQL 內處理完畢。

階層的問題，在這案例裡面會碰到兩次，一個是先找出 c:\windows\system32 的 ID, 這邊按照順序是 c:\ 底下的 windows 底下的 system32, 由於階層明確，我還可以笨一點，直接 self join 三層就可以找到:

```sql

declare @root int;

select @root = D3.ID
from
	demo1.DIRINFO D1 inner join 
	demo1.DIRINFO D2 on D1.ID = D2.PARENT_ID inner join
	demo1.DIRINFO D3 on D2.ID = D3.PARENT_ID

where D1.NAME = 'c:\' and D2.NAME = 'windows' and D3.NAME = 'system32'

select @root

```

我刻意先示範蠢一點的作法，這方法笨，可是可以找的到答案。但是我不曉得 c:\windows\system32 目錄以下到底還有幾層，總不可能這樣無腦的一直寫下去吧! Microsoft 替這種問題，在 SQL 2005 以後就添加了 CTE (Common Table Expression) 的語法，嘗試解決這問題。

直接來看這個範例，我先列出 c:\windows\system32 下的所有子目錄，搜尋的過程中同時組合出正確的相對路徑:

```sql

-- 我直接填上上一個範例查到的 ID
declare @root int = 189039;


;with DIR_CTE(ID, NAME, FULLNAME) as
(
	select ID, NAME, cast('./' + NAME as ntext)
	from demo1.DIRINFO
	where PARENT_ID = @root

	union all

	select D1.ID, D1.NAME, cast(concat(D2.FULLNAME, '/', D1.NAME) as ntext)
	from demo1.DIRINFO D1 inner join DIR_CTE D2 on D1.PARENT_ID = D2.ID
)

select * from DIR_CTE 

```

這段 SQL 的執行結果:

![](/wp-content/images/2019-06-01-nested-query/2019-05-28-00-03-05.png)



這邊簡單說明一下 CTE 的觀念，語法與範例等等有興趣的可以自行參考 Microsoft 官方文件:

* [WITH common_table_expression (T-SQL)](https://docs.microsoft.com/zh-tw/sql/t-sql/queries/with-common-table-expression-transact-sql?view=sql-server-2017)

簡單的說，CTE 就像是很靈活的 VIEW 一樣，就是用一段 SQL Query 定義的 VIEW，讓後續的 SQL Script 可以操作他。特別的是 CTE 的定義可以自己參考自己，就類似 programming language 自己呼叫自己的遞迴運作模式一般。用這個特性，像這類樹狀結構的處理就會變得非常容易。

不過語法好寫，不等於效能會跟語法一樣簡潔快速。CTE 寫的不好的話，是會引發災難的。寫的時候請特別留意會不會不小心就跑過頭了。你可以用 ```MAXRECURSION``` 來限制遞迴的呼叫層數，避免寫的很糟糕的 CTE 陷入無窮迴圈。

回到我們要解決的問題，既然目錄結構都查出來了，要查出檔案就不是太大問題了。只需要再多 join 一次 demo1.FILEINFO，就可以取得檔案清單。這次我貼上一段完整的 T-SQL:


```sql

declare @root int;

-- step 1, 找出 c:\windows\system32 的 ID
select @root = D3.ID
from
	demo1.DIRINFO D1 inner join 
	demo1.DIRINFO D2 on D1.ID = D2.PARENT_ID inner join
	demo1.DIRINFO D3 on D2.ID = D3.PARENT_ID
where D1.NAME = 'c:\' and D2.NAME = 'windows' and D3.NAME = 'system32'

-- step 2, 建立 c:\windows\system32 下的所有 DIR LIST 清單 (CTE)
;with DIR_CTE(ID, NAME, FULLNAME) as
(
	select ID, NAME, cast('./' + NAME as ntext)
	from demo1.DIRINFO
	where PARENT_ID = @root

	union all

	select D1.ID, D1.NAME, cast(concat(D2.FULLNAME, '/', D1.NAME) as ntext)
	from demo1.DIRINFO D1 inner join DIR_CTE D2 on D1.PARENT_ID = D2.ID
)

-- step 3, 依據 (2), 找出所有 (2) 目錄下, 附檔名為 .ini 的檔案及大小清單
select concat(D.FULLNAME, '/', F.NAME) as NAME, F.SIZE
from DIR_CTE D inner join demo1.FILEINFO F on D.ID = F.DIR_ID
where F.EXT = '.ini'


```

查詢結果:

![](/wp-content/images/2019-06-01-nested-query/2019-05-28-00-20-07.png)


拿 DIR 指令 ( ```dir /s /b /a c:\windows\system32\*.ini``` ) 對照一下:

```txt

C:\Windows\System32>dir /s /b /a *.ini

C:\Windows\System32\PerfStringBackup.INI
C:\Windows\System32\tcpmon.ini
C:\Windows\System32\WimBootCompress.ini
C:\Windows\System32\appraiser\Appraiser_Data.ini
C:\Windows\System32\DriverStore\FileRepository\prnge001.inf_amd64_2ce5a77183fe3339\Amd64\TTY.INI
C:\Windows\System32\DriverStore\FileRepository\prnms001.inf_amd64_f340cb58fcd23202\MXDW-manifest.ini
C:\Windows\System32\DriverStore\FileRepository\prnms004.inf_amd64_01e60efea4ee9a09\Amd64\unisharev4-manifest.ini
C:\Windows\System32\DriverStore\FileRepository\prnms005.inf_amd64_6c1071b47c60ba60\Amd64\MSxpsOpenXPS-manifest.ini
C:\Windows\System32\DriverStore\FileRepository\prnms005.inf_amd64_6c1071b47c60ba60\Amd64\MSxpsPCL6-manifest.ini
C:\Windows\System32\DriverStore\FileRepository\prnms005.inf_amd64_6c1071b47c60ba60\Amd64\MSxpsPS-manifest.ini

(以下省略)

```


跟實際在本機下指令看到的結果一致，這項測試也算過關!

不過，從這裡開始，效能就出現差異了。效能問題最後再一起探討，我先記錄一下效能相關資訊:

執行時間: 00:00:00.547 (sec)
執行計畫 (Estimated Subtree Cost): 0.942181

![](/wp-content/images/2019-06-01-nested-query/2019-05-28-00-19-20.png)



不過這幾個檔案就花掉 0.547 sec... 我換大一點的範圍再來搜尋一次看看；這次換成搜尋 c:\windows 下所有的 *.dll :

```sql

declare @root int;

-- step 1, 找出 c:\windows 的 ID
select @root = D2.ID
from
	demo1.DIRINFO D1 inner join 
	demo1.DIRINFO D2 on D1.ID = D2.PARENT_ID 
where D1.NAME = 'c:\' and D2.NAME = 'windows' 

-- step 2, 建立 c:\windows 下的所有 DIR LIST 清單 (CTE)
;with DIR_CTE(ID, NAME, FULLNAME) as
(
	select ID, NAME, cast('./' + NAME as ntext)
	from demo1.DIRINFO
	where PARENT_ID = @root

	union all

	select D1.ID, D1.NAME, cast(concat(D2.FULLNAME, '/', D1.NAME) as ntext)
	from demo1.DIRINFO D1 inner join DIR_CTE D2 on D1.PARENT_ID = D2.ID
)

-- step 3, 依據 (2), 找出所有 (2) 目錄下, 附檔名為 .dll 的檔案及大小清單
select concat(D.FULLNAME, '/', F.NAME) as NAME, F.SIZE
from DIR_CTE D inner join demo1.FILEINFO F on D.ID = F.DIR_ID
where F.EXT = '.ini'

```

執行時間: 00:00:08.138 (sec)
執行計畫 (Estimated Subtree Cost): 3.09097

![](/wp-content/images/2019-06-01-nested-query/2019-05-28-23-37-47.png)




MSSQL 小記:
> CTE 從 MS-SQL 2005 開始支援，而到了 MS-SQL 2008 則更進一步支援了 hierarchyid 這種欄位的型別，直接支援了樹狀結構的操作，處理這類結構的效能也比 CTE 來的好。不過我這篇不打算額外介紹這機制了，我的目的是讓 developer 多思考這類問題的解決方式，而非介紹 SQL SERVER 的特異功能。會介紹 CTE 已經是我的極限了，至少他只是在查詢語法上的支援，在不同的 DBMS 大都有類似對應的語法。我期望 developer 看完我這篇，會思考如何有效的靈活應用，不論是在 MS-SQL, Oracle, 或是 MySQL / Postgras ...



## 需求 3 ~ 5, 搬移 / 刪除 / 建立指定目錄

這種結構，就是以每個目錄上下層的相對關係為主來設計的，因此對於 tree 的異動 (搬移、刪除、建立) 都很直覺。因此需求 3, 4, 5 我就合併在一起示範了。

> 1. 模擬 mkdir c:\windows\backup, 在 c:\windows 下建立子目錄: backup

建立目錄的需求挺容易的，三個欄位給對就結束了。直接看 T-SQL script:

```sql

declare @root int;

-- step 1, 找出 c:\windows 的 ID
select @root = D2.ID
from
	demo1.DIRINFO D1 inner join 
	demo1.DIRINFO D2 on D1.ID = D2.PARENT_ID 
where D1.NAME = 'c:\' and D2.NAME = 'windows' 


-- step 2, 在 c:\windows 下新增子目錄 backup
insert demo1.DIRINFO (PARENT_ID, NAME) values (@root, 'backup');
select @@identity

```

這種 insert 操作，其實閃一下就過去了。執行計畫回報的 Estimated Subtree Cost 為: 0.0500064

為了確認結果，我們用前面的 script, 查詢看看 c:\windows 的子目錄長啥樣。下列這段 SQL script 請依附在上面的 script 後面執行:

```sql

-- step 3, 查詢 c:\windows (ID: @root) 下的子目錄
select * from demo1.DIRINFO where PARENT_ID = @root order by NAME asc

```

查詢結果:

![](/wp-content/images/2019-06-01-nested-query/2019-05-28-00-59-41.png)



這題也輕鬆過關了! 接下來挑戰搬移目錄:

> 1. 模擬 move c:\users c:\windows\backup\

這邊我特地挑了目錄搬移前後的階層會改變的範例。後面的範例就知道難搞了。一樣，基本上把要搬移的目錄，還有搬移的目的地目錄的 ID 找出來後，一行 update 指令就大功告成:


```sql

declare @srcID int;
declare @destID int;

-- step 1, 找出 c:\windows\backup 的 ID (@destID)
select @destID = D3.ID
from
	demo1.DIRINFO D1 inner join 
	demo1.DIRINFO D2 on D1.ID = D2.PARENT_ID inner join
	demo1.DIRINFO D3 on D2.ID = D3.PARENT_ID
where D1.NAME = 'c:\' and D2.NAME = 'windows' and D3.NAME = 'backup'


-- step 2, 找出 c:\users 的 ID (@srcID)
select @srcID = D2.ID
from
	demo1.DIRINFO D1 inner join 
	demo1.DIRINFO D2 on D1.ID = D2.PARENT_ID 
where D1.NAME = 'c:\' and D2.NAME = 'users'


-- step 3, 搬移 c:\users 目錄
update demo1.DIRINFO set PARENT_ID = @destID where ID = @srcID


-- step 4, 用 DIR_CTE 列出 c:\windows\backup\ 的目錄列表
;with DIR_CTE(ID, NAME, FULLNAME) as
(
	select ID, NAME, cast('./' + NAME as ntext)
	from demo1.DIRINFO
	where PARENT_ID = @destID

	union all

	select D1.ID, D1.NAME, cast(concat(D2.FULLNAME, '/', D1.NAME) as ntext)
	from demo1.DIRINFO D1 inner join DIR_CTE D2 on D1.PARENT_ID = D2.ID
)

select * from DIR_CTE

```

其中真正有異動資料的部分，只有 step 3 的那行 update 指令而已。 step 4 我是用前面範例介紹的 DIR_CTE，拿來當 DIR 的工具，把 c:\windows\backup 目錄下的子目錄列出來，證明搬移有成功執行而已。

這段 update 的執行計畫，Estimated Subtree Cost: 0.0232853

執行結果:

![](/wp-content/images/2019-06-01-nested-query/2019-05-28-01-19-38.png)


接下來最後一關，刪除剛才建立且搬移的目錄:

> 1. 模擬 rm /s /q c:\windows\backup (叔叔有練過，好孩子不要學)

基本上，就是綜合題而已。查出 c:\windows\backup 下的所有檔案及子目錄，逐一刪除就好了。
我先留 c:\windows\backup 本身不刪除 (其實就多補一行 delete 就搞定了)，這樣查詢刪除前後結果會比較清楚。


```sql

declare @root int;		-- c:\windows
declare @destID int;	-- c:\windows\backup

-- step 1, 找出 c:\windows\backup 的 ID (@destID)
select @destID = D3.ID, @root = D2.ID
from
	demo1.DIRINFO D1 inner join 
	demo1.DIRINFO D2 on D1.ID = D2.PARENT_ID inner join
	demo1.DIRINFO D3 on D2.ID = D3.PARENT_ID
where D1.NAME = 'c:\' and D2.NAME = 'windows' and D3.NAME = 'backup'

-- step 1.1, 列出 c:\windows 的所有子目錄 (刪除前)
;with DIR_CTE(ID, NAME, FULLNAME) as
(
	select ID, NAME, cast('./' + NAME as ntext)
	from demo1.DIRINFO
	where PARENT_ID = @root

	union all

	select D1.ID, D1.NAME, cast(concat(D2.FULLNAME, '/', D1.NAME) as ntext)
	from demo1.DIRINFO D1 inner join DIR_CTE D2 on D1.PARENT_ID = D2.ID
)

select * from DIR_CTE

-- step 2, 刪除 c:\windows\backup (@destID) 下的所有檔案

;with DIR_CTE(ID, NAME, FULLNAME) as
(
	select ID, NAME, cast('./' + NAME as ntext)
	from demo1.DIRINFO
	where PARENT_ID = @destID

	union all

	select D1.ID, D1.NAME, cast(concat(D2.FULLNAME, '/', D1.NAME) as ntext)
	from demo1.DIRINFO D1 inner join DIR_CTE D2 on D1.PARENT_ID = D2.ID
)

delete demo1.FILEINFO where DIR_ID in (select ID from DIR_CTE)



-- step 3, 刪除 c:\windows\backup (@destID) 下的所有目錄

;with DIR_CTE(ID, NAME, FULLNAME) as
(
	select ID, NAME, cast('./' + NAME as ntext)
	from demo1.DIRINFO
	where PARENT_ID = @destID

	union all

	select D1.ID, D1.NAME, cast(concat(D2.FULLNAME, '/', D1.NAME) as ntext)
	from demo1.DIRINFO D1 inner join DIR_CTE D2 on D1.PARENT_ID = D2.ID
)

delete demo1.DIRINFO where ID in (select ID from DIR_CTE)


-- step 4, 列出 c:\windows 的所有子目錄 (刪除後)
;with DIR_CTE(ID, NAME, FULLNAME) as
(
	select ID, NAME, cast('./' + NAME as ntext)
	from demo1.DIRINFO
	where PARENT_ID = @root

	union all

	select D1.ID, D1.NAME, cast(concat(D2.FULLNAME, '/', D1.NAME) as ntext)
	from demo1.DIRINFO D1 inner join DIR_CTE D2 on D1.PARENT_ID = D2.ID
)

select * from DIR_CTE


```

刪除前 (截錄片段):

![](/wp-content/images/2019-06-01-nested-query/2019-05-28-02-15-00.png)

刪除後 (截錄片段):

![](/wp-content/images/2019-06-01-nested-query/2019-05-28-02-15-37.png)


執行計畫:
- 刪除檔案 Estimated Subtree Cost: 2.57332
- 刪除目錄 Estimated Subtree Cost: 1.90982

總執行時間: 00:00:22.536 sec



## 方案 1 小結

寫到這邊，開始有 fu 了嗎? SQL 這種很關聯式的資料庫，要處理 tree 這種東西，先天就是不大自然。你會發現很多語法其實都有點彆扭，寫起來就沒有那種一路到底的順暢感，尤其處理到不固定階層的地方腦袋都要轉好幾個彎，同時效能也不盡理想。CTE 只是解決遞迴的 query 不好寫的問題而已，他並沒有解決多層 self-join 帶來的效能影響。可以從前面的查詢計畫看到 cost, 搜尋的效能不算理想，若 CTE 還要再 join 其他 table, 甚至再進行 update / delete 的操作，效能問題就更明顯了。

因為這個方案，就是直接把寫 code 用的指標結構，原封不動的搬到 SQL schema 內來，因此原本用 programming language 的 recursive 處理方式，若 RDBMS 自身沒有支援 (例如查詢 ID 時, 幾層目錄你就要自己 self-join 幾次的作法)，你就會發現很多 SQL 語法會囉嗦到你都看不下去。雖然 Oracle (CONNECT TO) / MS-SQL (CTE) 都有階層的查詢語法支援, 但是這些終究不是標準 SQL 語法，換句話說你使用 Entity Framework 這類 ORM, 或是你的 RDBMS 需要遷移到不同的系統時 (如 MS-SQL 換到 MySQL)，這些 SQL query 就通通得重來...

因此，接下來的兩個解決方案，我就會開始拋開特定 DBMS 的語法支援，回歸到最單純原生的 RDBMS 操作技巧，回歸到資料結構的設計本身來看看 developer 應該如何在 RDBMS 內設計你的 Tree 結構。










# 方案 2, columns per hierarchy

方案一的方式，雖然能漂亮的用 SQL 語法解決問題，不過有經驗的人大概都感覺得出來，這樣的效能實在有很大的改善空間。一般 DBA 在處理的資料量，都是要在幾千萬筆，甚至上億筆的數量級之下，查詢還要能在瞬間傳回來的。想像一下如果這些資料是你雲端硬碟的檔案清單，光是查詢就花掉 8 sec, 你一定不會覺得這服務速度很快很好用... (如果這是用在目錄同步的 API，我相信你會為了同步速度而抓狂...)

終究 RDBMS 擅長的不是這種遞迴的查詢，執行效能會耗費在多次重覆查詢的過程中，索引帶來的改善其實很有限。因此第二種方式，我試另一種極端的作法，放棄一些嚴謹的設計跟彈性，換來較理想的效能。這次我們來試看看，每一個階層都用一個欄位來代表的作法。

同樣先用簡單的 tree 來說明。用前面的圖來說明:

![](/wp-content/images/2019-06-01-nested-query/2019-05-30-23-00-38.png)

那麼資料表應該長這樣 (我簡化成三層就好):

| ID | ID1 | ID2 | ID3 |
|----|-----|-----|-----|
|A|NULL|NULL|NULL|
|B|A|NULL|NULL|
|C|A|NULL|NULL|
|D|A|C|NULL|
|E|A|C|NULL|


一樣，直接來看看轉化成 SQL table schema (範例資料 c:\ 目錄最深是 18 層, 我建立了 1 ~ 20 層的 ID 欄位):

![](/wp-content/images/2019-06-01-nested-query/2019-05-28-23-51-39.png)

如果你對資料的一致性要求嚴格一點的話，接下來的步驟就麻煩了，你得對每一個欄位都設定 constraint ... 沒錯，你決定建立 20 層欄位來應付將來的搜尋的話，你就得建立 20 次關聯性限制... 這邊容許我偷一點懶，我決定放棄建立關聯性限制了，我只針對搜尋的效能建立索引...。建立資料的部分我就略過了，以下是按照這種 schema 建立好的資料範例:

![](/wp-content/images/2019-06-01-nested-query/2019-05-28-23-53-01.png)



資料準備好了，同樣的來挑戰看看上述的需求:

## 需求 1 / 2, 查詢指定目錄下的內容

由於這種 table schema, 解決這兩個問題的方式很類似，我就寫在一起了。

> 1. 模擬 dir c:\windows 的結果，列出 c:\windows 下的目錄與檔案清單，統計檔案的大小
> 1. 模擬 dir /s /b c:\windows\*.dll，找出所有位於 c:\windows 目錄下 (包含子目錄) 所有副檔名為 .dll 的檔案清單


這種結構，已經預先把目錄拆好了，按照階層順序逐步擺在 20 個欄位內。
為了簡化後面的查詢，我決定省略一些不重要的 script, 首先，先找到起始目錄 c:\, c:\windows, c:\windows\system32 的 ID, 後面的範例就直接填入 ID 了:

| ID | PATH |
|----|------|
|1   |c:\   |
|134937|c:\users|
|151535|c:\windows|
|189039|c:\windows\system32|


接下來就容易了，如果我們要找到直接掛在 c:\windows 下的所有子目錄，我會把查詢解讀成 "找到 ID01 是 1 (c:\), 且 ID02 是 151535 (c:\windows), 且 ID03 ~ ID20 都是 NULL 的目錄"。

其實這邊可以偷懶一點，只要我的資料建立時就是正確的話，ID02 = 151535 時，ID01 = 1 一定是成立的，同時 ID03 如果是 NULL，以後所有的 ID 也一定都是 NULL ... 因此我的搜尋條件可以再簡化一點:

```sql

select * 
from demo2.DIRINFO
where ID02 = 151535 and ID03 is NULL

```

查詢結果:

![](/wp-content/images/2019-06-01-nested-query/2019-05-29-00-04-27.png)

執行時間: 00:00:00.184 (sec)
執行計畫 (Estimated Subtree Cost): 0.0077312


要補上檔案也不是什麼難事:

```sql

select *
from demo2.FILEINFO
where DIR_ID = 151535

```

查詢結果:

![](/wp-content/images/2019-06-01-nested-query/2019-05-29-00-09-20.png)

執行時間: 00:00:00.157 (sec)
執行計畫 (Estimated Subtree Cost): 0.213376


同前面的範例，整理一下格式:

```sql

select * from
(
	select '<DIR>' as type, name, NULL as size from demo2.DIRINFO where ID02 = 151535 and ID03 is NULL
	union
	select '' as type, NAME as name, SIZE as size from demo2.FILEINFO where DIR_ID = 151535

) IX order by name asc

```

![](/wp-content/images/2019-06-01-nested-query/2019-05-29-00-11-59.png)




接下來，如果我們要遞迴的搜尋，在這案例反而更簡單了! 如果我要查詢 c:\windows\system32 下的所有子目錄，我的查詢只要這樣解讀:

 "找到 ID01 是 1 (c:\), ID02 是 151535 (c:\windows) 且 ID03 是 189039 的目錄" 就可以了。
 
 跟前面不同的是，你不再需要過濾 ID04 is NULL ... ID04 是 NULL 代表這是 c:\windows\system32 下的子目錄，若 ID04 不是 NULL 則代表是再下一層的子目錄... 因此我要找 c:\windows\system32 下所有的子目錄清單，只要這樣下查詢:

```sql

select * 
from demo2.DIRINFO
where ID03 = 189039

```

查詢結果:

![](/wp-content/images/2019-06-01-nested-query/2019-05-29-00-20-30.png)


執行時間: 00:00:00.407 (sec)
執行計畫 (Estimated Subtree Cost): 0.0264708


目錄清單都出來了，要找到 c:\windows\system32\ 下所有子目錄的 *.ini 檔案清單，也不用太複雜的 SQL 就能搞定:

```sql

select F.NAME, F.SIZE
from demo2.FILEINFO F inner join demo2.DIRINFO D on F.DIR_ID = D.ID
where F.EXT = '.ini' and D.ID03 = 189039

```

查詢結果:

![](/wp-content/images/2019-06-01-nested-query/2019-05-29-00-26-53.png)

執行時間: 00:00:00.067 (sec)
執行計畫 (Estimated Subtree Cost): 0.18752


看到查詢效能跟語法上的差異了嗎? 整個困難度跟 [方案1] 完全是不同檔次的啊... 雖然 schema 的設計看起來蠢了一點，但是不得不說在效能跟查詢的困難度上來說是大勝啊!

難道方案1就一無是處嗎? 這也未必，我們繼續往下看...



## 需求 5, 建立目錄

同樣的例子，如果我們要模擬 mkdir c:\windows\backup, 這方案的 schema 設計下應該怎麼做:

```sql
insert demo2.DIRINFO (NAME, ID01, ID02) values ('backup', 1, 151535)
select @@identity
```

查詢結果: 218818
執行時間: 00:00:00.117 (sec)
執行計畫 (Estimated Subtree Cost): 0.0400054

這邊討厭的地方在於，你的 SQL script 很難固定下來，寫成 store procedure ... 因為你建立目錄的階層，會直接影響你寫的 T-SQL 結構... 或者你就必須寫出很蠢的語法，帶 ID01 ~ ID20 全部的參數，不需要的部份給 NULL ...，否則你就必須用程式碼產生 SQL script, 這樣很容易就會寫出 SQL injection 漏洞的程式碼...

不過，這問題還算好解決，不算很嚴重的缺點。我們繼續看下一個例子...



## 需求 3, 搬移指定目錄

同前面的方案1，接著我們來模擬 move c:\users c:\windows\backup :

這邊開始有點令人抓狂了，我拆成幾個分解動作...

1. 找出所有 c:\users 下的子目錄
2. 把 (1) 的 ID 都往右平移一層，例如 ID19 搬到 ID20, ID18 搬到 ID19 ...
3. 把 ID01, ID02, ID03 填入 1(c:\), 151535(c:\windows), 218818(c:\windows\backup)

寫成 SQL 實在有點醜... 

```sql

update demo2.DIRINFO
set
	ID20 = ID19,
	ID19 = ID18,
	ID18 = ID17,
	ID17 = ID16,
	ID16 = ID15,
	ID15 = ID14,
	ID14 = ID13,
	ID13 = ID12,
	ID12 = ID11,
	ID11 = ID10,
	ID10 = ID09,
	ID09 = ID08,
	ID08 = ID07,
	ID07 = ID06,
	ID06 = ID05,
	ID05 = ID04,
	ID04 = ID03,	-- 以上為 shift right
	ID03 = 218818,	-- ID03 => c:\windows\backup
	ID02 = 151535,	-- ID02 => c:\windows
	ID01 = 1		-- ID01 => c:\
where ID02 = 134937 -- c:\users

```

查詢結果:

執行時間: 00:00:00.758 (sec)
執行計畫 (Estimated Subtree Cost): 18.3011

這查詢看起來真是有點噁心... 最討厭的是 shift right 的動作一樣，很難寫成 store procedure, 搬移前後的階層變化，會決定每個 ID 要 shift 的層數。也因為無法預測搬移階層，這樣的 SQL 指令很難寫成固定的 store procedure, 得依靠前端的 programming language 搭配 dynamic sql ...


至於這指令有沒有搬移成功? 用前面的技巧查看看:

dir c:\windows\backup (218818)

```sql

select * from demo2.DIRINFO where ID03 = 218818

```

查詢結果:

![](/wp-content/images/2019-06-01-nested-query/2019-05-29-01-02-46.png)


好吧，雖然噁心但是至少也是有效率的完成任務了。總檢討後面再說，來看最後一個需求...



## 需求 4, 刪除指定目錄

延續前面案例，如果我要刪除 c:\windows\backup 下的子目錄跟檔案... 這反而沒什麼困難，先查詢所有的子目錄跟檔案，然後刪除即可。

不囉唆直接看 SQL 指令 (我一樣保留 c:\windows\backup 目錄本身，方便稍後驗證結果) :



del /s c:\windows\backup


```sql

delete demo2.FILEINFO where DIR_ID in (select ID from demo2.DIRINFO where ID03 = 218818)

```
(刪除檔案部分)
執行時間: 00:00:18.962 (sec)
執行計畫 (Estimated Subtree Cost): 143.985


```sql

delete demo2.DIRINFO where ID03 = 218818

```

(刪除目錄部分)
執行時間: 00:00:01.343 (sec)
執行計畫 (Estimated Subtree Cost): 13.7447



## 方案 2 小結

寫到這邊快昏倒了，後面更新 tree 的操作真是令人反胃啊，一直很強調程式碼結構跟可讀性的我，要我寫這種看起來就很不乾脆的 SQL script 真是痛苦，總算把這段範例寫完了。

看完方案 2 的 schema 設計，跟各種 tree 的操作，有看出兩個方案的差異了嗎? 以我的觀點來說，這兩種方案各有優點:

方案一的設計，明顯搭配資料結構課本講的 tree 的結構，所有結構都是相對的，因此很容易做搬移的操作；相對的 tree 的查詢需要用到遞迴，效能就拉不起來，相對的 SQL query 也不容易撰寫 (如果你不用 CTE 這類指令來簡化的話，問題會更惡化)。這是一種針對 tree 異動最佳化的設計。

方案二的設計則是採取另一個面向。我把 ID01 ~ ID20 這很醜的欄位，視為 developer 自行維護的 index 來看待。這些索引，在應付各種 tree 的查詢都能發揮最大功效 (你可以明顯看出查詢的速度與語法的優勢)。不過索引是需要花力氣維護的，因此這些資料維護的複雜度，在 "搬移" tree node 時就完全暴露出來了。這是一種針對 tree 搜尋效率極度最佳化的設計。

我想，做過這樣的比較，大部分人都會想: 

> 既然這樣，我不需要 tree 搬移的功能的話 (通常組織圖、或是網站的選單、購物網站的分類等等都不常見到搬移的操作)，絕大部分都是查詢，我當然是選擇方案二啊...

不過，這方法雖然又蠢又有效，但是那個程式碼時在很礙眼.. XD, 接下來我要介紹一個過去十幾年來，幾乎各個方面都是完美的設計... (鋪梗鋪真久)










# 方案 3, Nested Set Model

這方法我在 2003 年的時候，花了不少功夫在研究。當年碰到前系統用 Tamino, 一套原生的 XML database (其實就是現在的 NOSQL, 很多觀念都很類似)；當時用在處理數位學習的各種資料交換。這個產業的資料定義大都用 XML 為基礎建構起來的，理所當然的資料庫也選擇 XML database 是最合適的。無奈當時這觀念還是太前衛，許多企業 IT 碰到這聽都沒聽過的 database, DBA 沒有能力維護，我們的解決方案就很難打入企業的採購案內...

於是在將系統轉移到 MS-SQL 過程中，我碰到很多必須把 TREE 轉移到 MS-SQL 的情境。這個 Nested Set Model 就是我在那時看到的技巧。我只能說發明他的人實在太聰明了，在每個節點加上 left / right 左右兩個索引，就能夠很完美的用 SQL 擅長的 Set Operation (就是 SELECT 指令) 對 TREE 的資料結構做各種操作，完全沒有跨不同的 programming model 帶來的隔閡。

多年後我才看到 wiki 有這做法的說明，轉貼給各位參考:

* [Wiki: Nested set model](https://en.wikipedia.org/wiki/Nested_set_model#Example)

我同樣用前面的 tree 來說明一下:

![](/wp-content/images/2019-06-01-nested-query/2019-05-30-23-11-42.png)

標上 left / right 的資料:

|ID|LEFT|RIGHT|
|--|----|-----|
|A|1|10|
|B|2|3|
|C|4|9|
|D|5|6|
|E|7|8|

這 left / right index 怎麼標出來的? 看看圖上標示的黃色箭頭... 基本上就是按照 depth first traversal 的方式走完每個節點。每個節點第一次被走到的時候就按順序標上 left，繞了一圈回到這個節點後再標上 right.. 按照順序標上流水號，就成為這個結果了。

沒仔細想的話，看到這堆數字大概丈二金剛摸不著頭腦吧! 這是為 tree struct 精心設計的 index, wiki 上用了另一種視角來看這個結構。看一下 wiki 上的另一個例子:

![](/wp-content/images/2019-06-01-nested-query/2019-05-31-00-12-10.png)

把標上的 index 呈現在數線上:

![](/wp-content/images/2019-06-01-nested-query/2019-05-31-00-12-59.png)

看出這標號的用意了嗎? clothing 的標記是 left:1, right:22, 代表所有 left, right 被包圍在 1 ~ 22 之間的都是他的子節點 (因為這些都是在 depth first traversal 走回來之前經過的節點)。看懂這 index 的意義了嗎? 如果把 tree 想像成這張圖的 "包圍" 結構，tree 越上層代表越外圈... left / right index 代表數線上的左右邊界...

搞懂規則後，只要你能在 tree 節點有異動時維護好這些 left / right index, 你會發現 tree 的各種操作會變的非常容易 (而且很容易對應到 SQL 的操作)。

舉個例子來說:

1. 要找出 clothing(1,22) 所有的子節點，只要查詢: ```select * from TREE where 1 < left and right < 22;```
1. 要計算 clothing(1,22) 底下有多少節點，只要: ``` set @total_nodes = (22 - 1 - 1) / 2; ```;

有沒有很神奇? 簡單先介紹到這裡，實際的範例我們還是回到我的 c:\ 清單，實際走過這五個需求，看看這樣的 nested set model 應該怎麼處理。

同樣的，為了簡化後面的查詢，後面的範例就直接填入 ID 了:

| ID | NAME | LEFT | RIGHT |
|----|------|------|-------|
|1   |c:\   |1|437634|
|134937|c:\users|269872|302911|
|151535|c:\windows|303068|437609|
|189039|c:\windows\system32|378075|380740|




## 需求 1, 查詢指定目錄下的內容

> 1. 模擬 dir c:\windows 的結果，列出 c:\windows 下的目錄與檔案清單，統計檔案的大小

簡單的說，這需求的查詢條件要想像成這樣: 

> 找出所有位於 PARENT 底下的 CHILD, 但是中間不存在任何 MID 節點的清單...

有點繞舌? 直接來看看 SQL 查詢:

```sql

select C.*
from demo3.DIRINFO C inner join demo3.DIRINFO P on C.LEFT_INDEX between P.LEFT_INDEX and P.RIGHT_INDEX
where P.ID = 151535 and not exists
(
  select *
  from demo3.DIRINFO M
  where M.LEFT_INDEX between P.LEFT_INDEX and P.RIGHT_INDEX
    and C.LEFT_INDEX between M.LEFT_INDEX and M.RIGHT_INDEX
	and M.ID <> P.ID and M.ID <> C.ID
)

```

查詢結果:

![](/wp-content/images/2019-06-01-nested-query/2019-05-31-00-51-03.png)

執行時間: 00:02:33.591 (sec)
執行計畫 (Estimated Subtree Cost): 0.941395


這查詢看起來有點蠢，把目標節點(P)所有的子節點(C)都找出來，然後排除中間有其他節點(M)的部分...

這我覺得有點矯枉過正了。WIKI 的範例是額外加上 DEPTH 這個索引 (一樣你要在 tree 異動時自己維護這欄位)。我自己是合併 [方案一] 的 PARENT_ID，作法比較直覺。如果你像我一樣額外維護 PARENT_ID，那這個查詢的效能就會跟方案一的一模一樣。

至於格式化輸出的部分就省了，這邊完全跟前面的範例一樣，join FILEINFO 即可。



# 需求 2, 查詢指定目錄下的內容 (遞迴)

> 1. 模擬 dir /s /b c:\windows\system32\*.ini, 找出所有位於 c:\windows\system32 目錄下 (包含子目錄) 所有副檔名為 .ini 的檔案清單

這結構的強項來了。如同前面介紹的一般，只要透過 LEFT / RIGHT 包圍的範圍來查詢就可以得到答案:


```sql

select F.*
from demo3.DIRINFO C inner join demo3.FILEINFO F on C.ID = F.DIR_ID
where F.EXT = '.ini' and C.LEFT_INDEX between 378075 and 380740

```

查詢結果:

![](/wp-content/images/2019-06-01-nested-query/2019-05-31-01-13-38.png)

執行時間: 00:00:00.173 (sec)
執行計畫 (Estimated Subtree Cost): 0.167235




對比 [方案一]，如果也試著查看看 c:\windows\ 下的 *.dll, 看看結果:


```sql

select F.*
from demo3.DIRINFO C inner join demo3.FILEINFO F on C.ID = F.DIR_ID
where F.EXT = '.dll' and C.LEFT_INDEX between 303068 and 437609

```

查詢結果:

![](/wp-content/images/2019-06-01-nested-query/2019-05-31-01-14-07.png)

執行時間: 00:00:00.836 (sec)
執行計畫 (Estimated Subtree Cost): 10.7832


看出 [方案三] 特別的地方了嗎? 沒有 [方案一] 糟糕的效能；幾乎跟 [方案二] 同等級秒返的效率，但是查詢的語法卻不會像 [方案二] 那樣隨著層級改變，難以寫成 store procedure, 索引固定為 LEFT_INDEX / RIGHT_INDEX 兩個欄位 (不像 [方案二] 要 20 個欄位，你還無法預期要對哪個欄位下過濾條件)。這樣的結構大幅簡化了查詢的語法，完全可以將它放到 store procedure, 搭配參數即可執行。


當然，如果要把目錄跟檔案混在一起並且格式化輸出也不是難事:

```sql
select * from
(
	select '<DIR>' as type, name, NULL as size from demo3.DIRINFO where LEFT_INDEX between 303068 and 437609

	union

	select '' as type, F.NAME, F.SIZE
	from demo3.DIRINFO C inner join demo3.FILEINFO F on C.ID = F.DIR_ID
	where F.EXT = '.ini' and C.LEFT_INDEX between 303068 and 437609

) IX order by name asc
```

查詢結果:

![](/wp-content/images/2019-06-01-nested-query/2019-05-31-01-08-02.png)

執行時間: 00:00:00.546 (sec)
執行計畫 (Estimated Subtree Cost): 4.08984





## 需求 5, 建立目錄

同樣的例子，如果我們要模擬 mkdir c:\windows\backup, 這方案的 schema 設計下應該怎麼做:

回到 wiki 那張用 "涵蓋範圍" 觀念想像的圖來思考，建立一個目錄，就是插入一個節點，然後插入點右邊的所有 index 都 +2 (右移兩位) 就好了.. 直接來看 SQL:

```sql

declare @windows_left as int = 303068;
declare @windows_right as int = 437609;

-- step 1, 在 303068 騰出兩個位子，把所有 right_index > 303068 的數值都 +2
update demo3.DIRINFO set RIGHT_INDEX = RIGHT_INDEX + 2 where RIGHT_INDEX > @windows_left;

-- step 2, 在 303068 騰出兩個位子，把所有 left_index > 303068 的數值都 +2
update demo3.DIRINFO set LEFT_INDEX = LEFT_INDEX + 2 where LEFT_INDEX > @windows_left;

-- step 3, 空出的兩個 index 就保留給插入的新目錄 c:\windows\backup
insert demo3.DIRINFO (NAME, LEFT_INDEX, RIGHT_INDEX) values ('backup', @windows_left + 1, @windows_left + 2);

```

Step 1:
執行時間: 00:00:01.343 (sec)
執行計畫 (Estimated Subtree Cost): 7.39088

Step 2:
執行時間: 00:00:02.017 (sec)
執行計畫 (Estimated Subtree Cost): 29.6923

Step 3:
執行時間: 00:00:00.017 (sec)
執行計畫 (Estimated Subtree Cost): 0.0400054




查一下目錄是否有成功的被建立起來:

```sql

declare @windows_left as int = 303068;
declare @windows_right as int = 437609;
select * from demo3.DIRINFO where LEFT_INDEX > @windows_left;

```

查詢結果:

![](/wp-content/images/2019-06-01-nested-query/2019-06-01-01-14-21.png)

新增的目錄 ID: 218822




## 需求 3, 搬移指定目錄

同前面的方案1，接著我們來模擬 move c:\users c:\windows\backup ...

動手之前，再來看一次該怎麼拆解 tree node 搬移的動作。回到前面說明用的圖:

![](/wp-content/images/2019-06-01-nested-query/2019-05-30-23-11-42.png)

我把它換成 wiki 的看法，在數線上面重畫一次這個 tree:

![](/wp-content/images/2019-06-01-nested-query/2019-06-01-01-58-04.png)

視覺化之後就很容易了解了。每個方框就是個 node, 上面的 node 寬度一定會完全涵蓋底下的 nodes, 同一層的 nodes 彼此不會重疊。接著用這種結構圖來說明一下搬移的步驟。其實步驟很簡單，就是兩個區塊之間的挪移而已。只是挪移的過程會卡來卡去的很麻煩，所以我用 0 以下的空間 (負數) 當作暫存區，先把要搬移的 nodes (C, D, E) 搬到暫存區, 然後把其他的 nodes 先調整大小，把目標 node (B)下的空間騰出來，最後再把搬到暫存區的 nodes (C, D, E) 搬回來就結束了。

直接來看分解步驟:


1. 被搬移的 nodes 搬到暫存區:
C, D, E 都往左 shift 到全部的 index 都為負數為止。經過計算全部都 -10

![](/wp-content/images/2019-06-01-nested-query/2019-06-01-02-04-25.png)


1. 目標 node 騰出空間:
B 原本只有 2 ~ 3 (沒有空間再放其他 nodes 了), 擴張到 B(2,9), 騰出待會可以放下三個 nodes 的空間。如果 B 還有其他兄弟 nodes, 也要一起配合挪出位子..

![](/wp-content/images/2019-06-01-nested-query/2019-06-01-02-08-40.png)

1. 把暫存區的 nodes 搬回來:
B(2,9) 騰出了 3 ~ 8 的 index, 原本被搬到暫存區的 C, D, E 經過計算，全部 index +9 就可以搬回來新位置了。

![](/wp-content/images/2019-06-01-nested-query/2019-06-01-02-10-23.png)

經過這四個步驟大功告成。搬移結束。


為何我會先花一些篇幅，甚至畫圖來說明，就是這些觀念不先搞懂的話，你光是看我寫出來的 SQL script, 我保證你一定看不懂我的意圖是什麼，所以我才先解釋觀念。接下來我就一次把 SQL 寫出來，執行看結果了:

```sql


declare @src_node int = 134937; -- c:\users 269872,302911
declare @dest_node int = 218824; -- c:\windows\backup 303069 303070
declare @offset int;

-- 搬移的參數:
-- * 被搬移的範圍: 269872 ~ 302911 (c:\users)
-- * 搬移目的範圍: 303069 ~ 303070 (c:\windows\backup)


-- step 1, move src to temp area
set @offset = 0 - 302911 - 1;

update demo3.DIRINFO
set LEFT_INDEX = LEFT_INDEX + @offset,
	RIGHT_INDEX = RIGHT_INDEX + @offset
where LEFT_INDEX between 269871 and 302912

-- step 2, allocate space
set @offset = 302911-269872+1;

update demo3.DIRINFO
set LEFT_INDEX = LEFT_INDEX - @offset
where LEFT_INDEX between 269872 and 303069

update demo3.DIRINFO
set RIGHT_INDEX = RIGHT_INDEX - @offset
where RIGHT_INDEX between 269872 and 303069

-- step 3, move all nodes in temp area to allocated space
set @offset = 303070

update demo3.DIRINFO
set LEFT_INDEX = LEFT_INDEX + @offset,
	RIGHT_INDEX = RIGHT_INDEX + @offset
where LEFT_INDEX < 0

-- check result
select * 
from demo3.DIRINFO P inner join demo3.DIRINFO C on C.LEFT_INDEX between P.LEFT_INDEX and P.RIGHT_INDEX
where P.ID = @root_node

```

Step 1:
執行時間: 00:00:00.527 (sec)
執行計畫 (Estimated Subtree Cost): 2.69808

Step 2:
執行時間: 00:00:00.116 (sec)
執行計畫 (Estimated Subtree Cost): 2.44647, 2.44594

Step 3:
執行時間: 00:00:00.023 (sec)
執行計畫 (Estimated Subtree Cost): 0.066514


執行時間: 00:00:00.550 (sec)



想確定執行結果的話，我們可以拿 [需求1] 的查詢來驗證看看 c:\windows\backup 下的目錄是不是都搬過來了:

```sql

declare @root int = 218824;

select C.*
from demo3.DIRINFO C inner join demo3.DIRINFO P on C.LEFT_INDEX between P.LEFT_INDEX and P.RIGHT_INDEX
where P.ID = @root and C.ID <> @root
and not exists
(
  select *
  from demo3.DIRINFO M
  where M.LEFT_INDEX between P.LEFT_INDEX and P.RIGHT_INDEX
    and C.LEFT_INDEX between M.LEFT_INDEX and M.RIGHT_INDEX
	and M.ID <> P.ID 
	and M.ID <> C.ID
)

```

查詢結果:

![](/wp-content/images/2019-06-01-nested-query/2019-06-01-13-46-20.png)

果然, ID = 134937 的 Users 目錄，整包都被搬過來了，執行成功!






## 需求 4, 刪除指定目錄

最後一個需求，如果我要刪除 c:\windows\backup 下的子目錄跟檔案... 
這點一直跟前面的方案沒什麼不同，就是先查詢所有的子目錄跟檔案，然後刪除即可。執行的效能關鍵還是一樣，都在如何找出要刪除的清單。

同樣的，為了方便確認結果，我會保留 c:\windows\backup 目錄本身，刪除所有子目錄，及所有的檔案。整個刪除的程序分為三個步驟:

1. 選出所有的子目錄 (包含 root), 刪除關聯的檔案
1. 刪除所有的子目錄 (不包含 root)
1. 回收清出來的 index 空間

```sql

-- step 1
delete demo3.FILEINFO where DIR_ID in (
	select ID from demo3.DIRINFO where LEFT_INDEX >= 270029 and LEFT_INDEX <= 303070
)

-- step 2
delete demo3.DIRINFO where LEFT_INDEX > 270029 and LEFT_INDEX < 303070

-- step 3
update demo3.DIRINFO set RIGHT_INDEX = LEFT_INDEX + 1 where ID = 218825;
update demo3.DIRINFO set LEFT_INDEX = LEFT_INDEX - (303070-270029-1) where LEFT_INDEX > 270030;
update demo3.DIRINFO set RIGHT_INDEX = RIGHT_INDEX - (303070-270029-1) where RIGHT_INDEX > 270030;

```


Step 1:  刪除檔案部分
執行時間: 00:00:05.756 (sec)
執行計畫 (Estimated Subtree Cost): 217.166

Step 2: 刪除目錄部分
執行時間: 00:00:00.887 (sec)
執行計畫 (Estimated Subtree Cost): 0.792744

Step 3: 回收索引空間
執行時間: 00:00:02.515 (sec)
執行計畫 (Estimated Subtree Cost): 0.0432873, 12.0335, 11.8227



刪除之後，我們在來查詢 c:\windows\backup 目錄下有多少子目錄掛著:


```sql

declare @root int = 218825; -- c:\windows\backup 270029 ~ 303070
select C.*
from demo3.DIRINFO C inner join demo3.DIRINFO P on C.LEFT_INDEX between P.LEFT_INDEX and P.RIGHT_INDEX
where P.ID = @root --and C.ID <> @root
and not exists
(
  select *
  from demo3.DIRINFO M
  where M.LEFT_INDEX between P.LEFT_INDEX and P.RIGHT_INDEX
    and C.LEFT_INDEX between M.LEFT_INDEX and M.RIGHT_INDEX
	and M.ID <> P.ID 
	and M.ID <> C.ID
)

```


![](/wp-content/images/2019-06-01-nested-query/2019-06-01-17-27-21.png)



## 方案 3 小結










# 寫在最後: 寫這篇文章的動機

結束之前，來聊一下，我寫這篇文章的動機: 基礎知識

RDBMS 的主要應用市場，還是以企業為主。由於維護 RDBMS 需要很多的專業知識與經驗，通常企業的組織都會搭配對應的職位: DBA (Database Administrator) 來負責。

不過，資訊科技的發展，越來越走向高度整合。DBA 跟 Developer 的界線就越來越模糊。資訊科技發展這麼多年，RDBMS 的發展確實有點跟不上開發技術的發展了。我先前寫過幾篇 ORM (Object Relation Mapping) 的介紹文章 (Orz, 10 年了...) 就有提到，為了解決商業邏輯的複雜需求，程式語言發展出 OOP 的概念來因應，但是在 Database 領域卻完全跟不上...

例如: 程式裡操作的物件，要如何 "有效率" 的儲存在資料庫? 我當然可以序列化之後存在 BLOB 欄位，但是幾億筆資料的搜尋，索引跟 SQL 語法就派不上用場... 為了彌補這個空缺，各種 ORM 的技術就被發展出來。物件有繼承，封裝等等特性，這些特性 RDBMS 又無法對映了，於是 ORM 也隨著越來越複雜，看看 Entity Framework 就好了，他是個好東西，但是整個 RDBMS 的生態系的每個環節都必須要有物件版本，才能分的乾淨。從 Entity 的設計，DB 欄位的對應開始，就是個大工程 (要依賴 code first, migration tools, EDMX...), 需要透過 Database Context, 到資料的查詢，需要透過 LINQ 轉譯成對應的 T-SQL 等等重量級的 framework 輔助, 這整件事才得以發生。能搞懂其中每個環節的人大概沒幾個，大多數是知道怎麼寫就上場了。

不過，為何我還要探討這類基本的資料結構設計 (schema) 與定義的問題? ORM 終究是靠向 programming language 一方的產物。以 C# 為例，終究是注重程序的語言，撇除整理結構能支援物件導向的各種機制之外，對邏輯的處理終究是 C Like 的程序 (如: if / while / for / foreach 等等)；這跟 SQL 是以集合的處理 (set operation) 方式截然不同。這篇其實我真正想探討的就是如何用 set operation 的角度，來看待 tree 的處理作法。


















