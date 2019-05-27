---
layout: post
title: "架構面試題: RDBMS 處理樹狀結構的技巧"
categories:
- "系列文章: 架構師觀點"
tags: [""]
published: false
comments: true
redirect_from:
logo: https://pixabay.com/photos/tree-landscape-field-branch-696839/
---

![樹](https://pixabay.com/photos/tree-landscape-field-branch-696839/)
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

最直覺的方式，就是這個 self join 的做法了。基本的結構就是一個目錄一筆資料。除了相關 metadata 之外，關鍵的欄位就是自己的 ID，以及上一層 ID。舉例來說像這樣:


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

寫到這邊，開始有 fu 了嗎? SQL 這種很關聯式的資料庫，要處理 tree 這種東西，先天就是不大自然。你會發現很多語法其實都有點彆扭，寫起來就沒有那種一路到底的順暢感，尤其處理到不固定階層的地方腦袋都要轉好幾個彎。

因為這個方案，就是直接把寫 code 用的指標結構，原封不動的搬到 SQL schema 內來，因此原本用 programming language 的 recursive 處理方式，若 RDBMS 自身沒有支援 (例如查詢 ID 時, 幾層目錄你就要自己 self-join 幾次的作法)，你就會發現很多 SQL 語法會囉嗦到你都看不下去。雖然 Oracle (CONNECT TO) / MS-SQL (CTE) 都有階層的查詢語法支援, 但是這些終究不是標準 SQL 語法，換句話說你使用 Entity Framework 這類 ORM, 或是你的 RDBMS 需要遷移到不同的系統時 (如 MS-SQL 換到 MySQL)，這些 SQL query 就通通得重來...

因此，接下來的兩個解決方案，我就會開始拋開特定 DBMS 的語法支援，回歸到最單純原生的 RDBMS 操作技巧，回歸到資料結構的設計本身來看看 developer 應該如何在 RDBMS 內設計你的 Tree 結構。





# 方案 2, columns per hierarchy

方案一的方式，雖然能漂亮的用 SQL 語法解決問題，不過有經驗的人大概都感覺得出來，這樣的效能實在有很大的改善空間。一般 DBA 在處理的資料量，都是要在幾千萬筆，甚至上億筆的數量級之下，查詢還要能在瞬間傳回來的。想像一下如果這些資料是你雲端硬碟的檔案清單，光是查詢就花掉 5 sec, 你一定不會覺得這服務速度很快很好用... (如果這是用在目錄同步的 API，我相信你會為了同步速度而抓狂...)

回頭思考，終究 RDBMS 擅長的不是這種遞迴的查詢，遞迴就注定需要類似 stack 來暫存資料，執行效能會耗費在多次重覆查詢的過程中，索引帶來的改善其實很有限。

因此第二種方式，我試著做一些反正規化，放棄一些嚴謹的設計跟彈性，換來較理想的效能。這次我們來試看看，每一個階層都用一個欄位來代表的作法。

先看看 table schema (為了簡潔易懂起見，我只建立到 LV1 ~ LV5, 往後略):



如果你對資料的一致性要求嚴格一點的話，接下來的步驟就麻煩了，你得對每一個欄位都設定 constraint ... 沒錯，你決定建立 20 層欄位來應付將來的搜尋的話，你就得建立 20 次關聯性限制...



建立資料的部分我就略過了，以下是按照這種 schema 建立好的資料範例:





在最前面的說明，我的 C:\ 目錄最深有到 19 層目錄結構，理論上我應該最少要建立 LV1 ~ LV19 這 19 個欄位才對，我只偷懶建立了 LV1 ~ LV5, 後續的案例仍然能進行，但是我按照目錄搜尋的條件，只能對前五層目錄下條件而已。


資料準備好了，同樣的來挑戰看看上述的需求:

## 需求 1 / 2, 查詢指定目錄下的內容

由於這種 table schema, 解決這兩個問題的方式很類似，我就寫在一起了。

> 1. 模擬 dir c:\windows 的結果，列出 c:\windows 下的目錄與檔案清單，統計檔案的大小
> 1. 模擬 dir /s /b c:\windows\*.dll，找出所有位於 c:\windows 目錄下 (包含子目錄) 所有副檔名為 .dll 的檔案清單


這種結構，已經預先把目錄拆好了，按照階層順序逐步擺在 5 個欄位內。

首先，先找到起始目錄 c:\windows 的 ID:






接下來就容易了，如果我們要找到直接掛在 c:\windows 下的所有子目錄，我會把查詢解讀成 "找到 LV1 是 123456, 且 LV2 以後的欄位是 NULL 的所有目錄"。既然目錄都找出來了，要把檔案也一起列出來自然不是難事:





如果我們要遞迴的搜尋，在這案例反而更簡單了! 我的查詢只要這樣解讀 "找到 LV1 是 123456 的所有目錄" 即可。LV2 是否是 NULL 一點都不重要，通通撈出來就對了:





## 需求 3, 搬移指定目錄


## 需求 4, 刪除指定目錄


## 需求 5, 建立目錄








# 方案 3, Nested Set Model

這方法我在 2003 年的時候，花了不少功夫在研究。當年碰到前系統用 Tamino, 一套原生的 XML database (其實就是現在的 NOSQL, 很多觀念都很類似)；當時用在處理數位學習的各種資料交換。這個產業的資料定義大都用 XML 為基礎建構起來的，理所當然的資料庫也選擇 XML database 是最合適的。無奈當時這觀念還是太前衛，許多企業 IT 碰到這聽都沒聽過的 database, DBA 沒有能力維護，我們的解決方案就很難打入企業的採購案內...

於是在將系統轉移到 MS-SQL 過程中，我碰到很多必須把 TREE 轉移到 MS-SQL 的情境。這個 Nested Set Model 就是我在那時看到的技巧。我只能說發明他的人實在太聰明了，在每個節點加上 left / right 左右兩個索引，就能夠很完美的用 SQL 擅長的 Set Operation (就是 SELECT 指令) 對 TREE 的資料結構做各種操作，完全沒有跨不同的 programming model 帶來的隔閡。

多年後我才看到 wiki 有這做法的說明，轉貼給各位參考:

* [Wiki: Nested set model](https://en.wikipedia.org/wiki/Nested_set_model#Example)














# 寫在最後: 寫這篇文章的動機

結束之前，來聊一下，我寫這篇文章的動機: 基礎知識

RDBMS 的主要應用市場，還是以企業為主。由於維護 RDBMS 需要很多的專業知識與經驗，通常企業的組織都會搭配對應的職位: DBA (Database Administrator) 來負責。

不過，資訊科技的發展，越來越走向高度整合。DBA 跟 Developer 的界線就越來越模糊。資訊科技發展這麼多年，RDBMS 的發展確實有點跟不上開發技術的發展了。我先前寫過幾篇 ORM (Object Relation Mapping) 的介紹文章 (Orz, 10 年了...) 就有提到，為了解決商業邏輯的複雜需求，程式語言發展出 OOP 的概念來因應，但是在 Database 領域卻完全跟不上...

例如: 程式裡操作的物件，要如何 "有效率" 的儲存在資料庫? 我當然可以序列化之後存在 BLOB 欄位，但是幾億筆資料的搜尋，索引跟 SQL 語法就派不上用場... 為了彌補這個空缺，各種 ORM 的技術就被發展出來。物件有繼承，封裝等等特性，這些特性 RDBMS 又無法對映了，於是 ORM 也隨著越來越複雜，看看 Entity Framework 就好了，他是個好東西，但是整個 RDBMS 的生態系的每個環節都必須要有物件版本，才能分的乾淨。從 Entity 的設計，DB 欄位的對應開始，就是個大工程 (要依賴 code first, migration tools, EDMX...), 需要透過 Database Context, 到資料的查詢，需要透過 LINQ 轉譯成對應的 T-SQL 等等重量級的 framework 輔助, 這整件事才得以發生。能搞懂其中每個環節的人大概沒幾個，大多數是知道怎麼寫就上場了。

不過，為何我還要探討這類基本的資料結構設計 (schema) 與定義的問題? ORM 終究是靠向 programming language 一方的產物。以 C# 為例，終究是注重程序的語言，撇除整理結構能支援物件導向的各種機制之外，對邏輯的處理終究是 C Like 的程序 (如: if / while / for / foreach 等等)；這跟 SQL 是以集合的處理 (set operation) 方式截然不同。這篇其實我真正想探討的就是如何用 set operation 的角度，來看待 tree 的處理作法。




























<!--

這個產業，走向雲端化，打破了不少產業的分工；即使身在這個產業的軟體開發人員也躲不掉。隨著敏捷、DevOps、及微服務架構等等趨勢，你不難發現分工的模式跟過去越來越不同了。過去是走 "專業" 分工，例如三層式架構，前後端，DBA，都是垂直的角度來切割責任範圍的。但是敏捷、DevOps、Microservices 等發展趨勢，都從不同的角度 (流程、技術、架構) 告訴我們要靈活面對市場，分工必須由 domain 來分，每個小團隊都要能掌握垂直角度從上到下的技能，顧好自己的服務才能致勝。

其實這種例子很多啊，過去的組織都是同樣專業能力的人在同一個部門，但是現在更偏向可以獨立自主交付價值的團隊，每個小團隊都有前端到後端的執行能力；DevOps 也告訴我們開發人員也要了解維運，並且自己維運從中間取得 feedback ... Microservices 也告訴我們把大型 application 切割成可以獨立自主運作的小型服務，並透過 API 連結起來；每個小型服務只要夠簡單，就能由一個團隊獨自維護與開發... 。






























不過，教育及訓練的體系並沒有完全跟上來啊! 之前在做訓練系統時，在某年 ASTD 簡報上看過一張圖: 過去 (1986 的資料)，學校訓練出來的人，已經能滿足業界 75% 的技能需求。這個比例隨著時間快速往下掉，到了 1997 就剩下 15 ~ 20% (Orz, 正好是我出社會的那個年代)。資料統計到 2008, 則更往下掉到 8 ~ 10% ...

這資料我沒有再往下追了，但是我相信只會越來越低而已。



最近手上的案子變化越來越多端了，碰到的問題越來越多都不是靠單一技能能解決的了。我常常跟朋友聊這個業界的趨勢，就是大整合的時代。這個年代, developer 越來越難靠單一技能就搞定所有問題了。隨手一舉就有好幾個現成的例子: DevOps(開發運維一體化)、TDD(先寫測試再寫程式, 自己的 code 自己測)...。

-->



# RDBMS 處理樹狀結構的難點



1. 階層數量不固定
- 策略: 攤平所有階層
- 策略: 只處理與上層結構

2. 攤平 (每個階層一個欄位)
- 難以決定 schema (需決定最大階層)

3. 相對結構 (只記錄上層)
- 難以執行 join 查詢 (join 必須在寫 query 時就決定)

4. recursive 查詢

5. tree node move 資料更新問題

...





# 測試資料 (我的 C:\) ..




# 方法1, 查詢效能最佳化 (攤平)

# 方法2, 儲存 / 更新最佳化 (正規化)

# 方法3, 兼顧 (自行維護左右邊界)

# 效能驗證

評比項目 (查詢):
1. 查詢 c:\windows\system32\ 目錄下的檔案列表
1. 查詢 c:\windows\system32\ 目錄統計 (子目錄數，檔案數，大小)

評比項目 (異動):
1. 大量匯入

1. 新增目錄
1. 刪除目錄
1. 重新命名

1. 新增檔案 (c:\windows\temp\a.txt, 100 bytes)
1. 刪除檔案
1. 重新命名 




# References

https://hub.docker.com/r/microsoft/mssql-server-windows-express/
https://en.wikipedia.org/wiki/Nested_set_model#Example

```sql

USE [master]
GO
/****** Object:  Database [DIRDB]    Script Date: 2019/4/8 上午 03:49:21 ******/
CREATE DATABASE [DIRDB]
 CONTAINMENT = NONE
 ON  PRIMARY 
( NAME = N'DIRDB', FILENAME = N'C:\Program Files\Microsoft SQL Server\MSSQL14.SQLEXPRESS\MSSQL\DATA\DIRDB.mdf' , SIZE = 532480KB , MAXSIZE = UNLIMITED, FILEGROWTH = 65536KB )
 LOG ON 
( NAME = N'DIRDB_log', FILENAME = N'C:\Program Files\Microsoft SQL Server\MSSQL14.SQLEXPRESS\MSSQL\DATA\DIRDB.ldf' , SIZE = 532480KB , MAXSIZE = 2048GB , FILEGROWTH = 65536KB )
GO
ALTER DATABASE [DIRDB] SET COMPATIBILITY_LEVEL = 140
GO
IF (1 = FULLTEXTSERVICEPROPERTY('IsFullTextInstalled'))
begin
EXEC [DIRDB].[dbo].[sp_fulltext_database] @action = 'enable'
end
GO
ALTER DATABASE [DIRDB] SET ANSI_NULL_DEFAULT ON 
GO
ALTER DATABASE [DIRDB] SET ANSI_NULLS ON 
GO
ALTER DATABASE [DIRDB] SET ANSI_PADDING ON 
GO
ALTER DATABASE [DIRDB] SET ANSI_WARNINGS ON 
GO
ALTER DATABASE [DIRDB] SET ARITHABORT ON 
GO
ALTER DATABASE [DIRDB] SET AUTO_CLOSE OFF 
GO
ALTER DATABASE [DIRDB] SET AUTO_SHRINK OFF 
GO
ALTER DATABASE [DIRDB] SET AUTO_UPDATE_STATISTICS ON 
GO
ALTER DATABASE [DIRDB] SET CURSOR_CLOSE_ON_COMMIT OFF 
GO
ALTER DATABASE [DIRDB] SET CURSOR_DEFAULT  LOCAL 
GO
ALTER DATABASE [DIRDB] SET CONCAT_NULL_YIELDS_NULL ON 
GO
ALTER DATABASE [DIRDB] SET NUMERIC_ROUNDABORT OFF 
GO
ALTER DATABASE [DIRDB] SET QUOTED_IDENTIFIER ON 
GO
ALTER DATABASE [DIRDB] SET RECURSIVE_TRIGGERS OFF 
GO
ALTER DATABASE [DIRDB] SET  DISABLE_BROKER 
GO
ALTER DATABASE [DIRDB] SET AUTO_UPDATE_STATISTICS_ASYNC OFF 
GO
ALTER DATABASE [DIRDB] SET DATE_CORRELATION_OPTIMIZATION OFF 
GO
ALTER DATABASE [DIRDB] SET TRUSTWORTHY OFF 
GO
ALTER DATABASE [DIRDB] SET ALLOW_SNAPSHOT_ISOLATION OFF 
GO
ALTER DATABASE [DIRDB] SET PARAMETERIZATION SIMPLE 
GO
ALTER DATABASE [DIRDB] SET READ_COMMITTED_SNAPSHOT OFF 
GO
ALTER DATABASE [DIRDB] SET HONOR_BROKER_PRIORITY OFF 
GO
ALTER DATABASE [DIRDB] SET RECOVERY FULL 
GO
ALTER DATABASE [DIRDB] SET  MULTI_USER 
GO
ALTER DATABASE [DIRDB] SET PAGE_VERIFY CHECKSUM  
GO
ALTER DATABASE [DIRDB] SET DB_CHAINING OFF 
GO
ALTER DATABASE [DIRDB] SET FILESTREAM( NON_TRANSACTED_ACCESS = OFF ) 
GO
ALTER DATABASE [DIRDB] SET TARGET_RECOVERY_TIME = 60 SECONDS 
GO
ALTER DATABASE [DIRDB] SET DELAYED_DURABILITY = DISABLED 
GO
ALTER DATABASE [DIRDB] SET QUERY_STORE = OFF
GO
USE [DIRDB]
GO
/****** Object:  Table [dbo].[DIRINFO]    Script Date: 2019/4/8 上午 03:49:21 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DIRINFO](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[PARENT_ID] [int] NULL,
	[FULLNAME] [nvarchar](255) NOT NULL,
	[NAME] [nvarchar](255) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[FILEINFO]    Script Date: 2019/4/8 上午 03:49:22 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[FILEINFO](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[DIR_ID] [int] NOT NULL,
	[FULLNAME] [nvarchar](255) NOT NULL,
	[FILE_NAME] [nvarchar](255) NOT NULL,
	[FILE_EXT] [nchar](10) NOT NULL,
	[FILE_SIZE] [int] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
ALTER TABLE [dbo].[DIRINFO]  WITH CHECK ADD  CONSTRAINT [FK_DIRINFO_DIRINFO] FOREIGN KEY([ID])
REFERENCES [dbo].[DIRINFO] ([ID])
GO
ALTER TABLE [dbo].[DIRINFO] CHECK CONSTRAINT [FK_DIRINFO_DIRINFO]
GO
ALTER TABLE [dbo].[FILEINFO]  WITH CHECK ADD  CONSTRAINT [FK_FILEINFO_DIRINFO] FOREIGN KEY([DIR_ID])
REFERENCES [dbo].[DIRINFO] ([ID])
GO
ALTER TABLE [dbo].[FILEINFO] CHECK CONSTRAINT [FK_FILEINFO_DIRINFO]
GO
USE [master]
GO
ALTER DATABASE [DIRDB] SET  READ_WRITE 
GO


```






----------------------







準備好接受挑戰了嗎? 想是看看的話不要急著往下看，你可以先想想你工作上要是面臨這樣的問題，你會怎麼去設計解決方式? 這種問題很常碰到啊，隨便舉過去我處理過的案例就好幾種應用，例如:

1. 文件 (分類及權限)
1. 商品 (分類)
1. 組織圖

...


我就直接列出需求了。這類資料的搜尋，往往都要搭配複合的條件，例如:

1. 找出特定分類 (含以下子分類) 的所有商品，同時滿足其他條件 (如售價範圍等等)。
1. 找出符合權限 (假設權限綁定在分類上面) 的所有文件，同時符合關鍵字等其他條件過濾。
1. 找出某個部門以下所有單位，同時符合職等或是年資等過濾條件的員工。

對於 SQL 稍有概念的就知道，如果你不能在 SQL 的層級，把兩大過濾條件都處理掉 (一個是分類的過濾條件，另一個是其他過濾條件)，然後 join 取得最終結果的話，兩邊分開處理後，再把資料倒到 code 端去合併，是很沒有效率的。因此後面的幾種方式探討，都有這些前提須要被滿足:

1. 需要支援階層的異動
1. 需要支援階層的查詢 (例如某分類以下的所有分類)
1. 大量資料下，效能必須維持在合理範圍內 (不考慮把整個 tree 都載入到 memory 裡，用 code 去解決)

準備好了嗎? 想挑戰的先別往下看，自己想想你會怎麼解決這需求吧! 想完之後歡迎往下看看我整理的做法。











雖然這篇的內容跟微服務 (Microservices) 沒啥關聯，但是我還是拿微服務來開個頭...。我常常被問到跟維服務相關的幾個 FAQ, 最多的就是微服務架構下的資料該怎麼處理了。微服務架構，主張把大型系統切割成獨立運作的小服務，中間只靠 API 來協做；因為服務切割的夠小，因此開發團隊有能力獨自維護，同時能負擔開發與維運的任務 (對，就是 DevOps)。這架構下，過去獨立且龐大的關聯式資料庫，當然也一起被切開了 (如果不切割資料庫，改成微服務架構的目的還存在嗎?)。

資料庫如果隨著服務的切割，也被隔開了的話，過去透過大量 join 操作，應該都會被一連串的 API 查詢取代。這部分有沒有效率我就暫時不討論了，不在這篇我要探討的主題。我想談的重點是，切割之後，我們面對的資料問題，就跟過去不大一樣了。我們會從整個 application 範圍的資料維護，縮減到單一功能 / domain 的資料維護。但是你要切割成微服務通常都會有服務量增加的前提，因此資料的量應該都會比過去還要大幾個量級。


這裡就衍生出一個問題: 除了 Dev + Ops 之外，那原本 DBA 負責的資料管理任務，也一併回歸到開發團隊身上嗎?

這其實是個很弔詭的問題，就跟 DevOps 一樣，背後的意義往往都被誤解了。我先從較容易理解的 DevOps 開始，DevOps 的核心觀念並不是 "單純" 的要開發團隊把維運的任務搶回來而已那麼簡單，而是要藉著開發團隊自己維運，快速取得回饋，同時思考該如何反應在流程與開發的改善。開發人員若有維運的經驗，則更能開發出善於維運的服務 (design for operation), 就能更輕鬆的讓維運自動化, 不需要人工的介入。

同樣的，讓開發團隊自己規劃資料的管理也一樣，並不是要開發團隊把 DBA 的任務搶回來，而是當團隊對於服務的邊界掌握的更精準時，資料的複雜度會降低 (但是量會變大)，過去關聯式資料庫的 "關聯" 問題，會被轉移到跨服務的 "API" 身上。若單一服務內的資料庫複雜度降低了，同時又有 NOSQL 這類新興的服務盛行，過去必須依靠 DBA 才能做好的資料管理，理論上開發團隊現在就能顧好它了。


當你的資料複雜度降低時 (單一一個服務，也許只需要 10 個資料表)，因應 SaaS 的發展，換來的是資料量會爆增 (開始會衍生多租戶架構的問題) 的問題。加上資料的進出口，都由過去的 DBMS 往外移，變成 API level 的問題了，你看出關鍵點了嗎? 處理巨量資料的各種問題，都從 DBA 轉移到 DEV 身上了。這時，吃的不是你對於工具的掌握能力，而是吃你的整合能力與資訊科學的基礎能力。

因為不斷看到這種情況，也不斷的看到很多資深的工程師，碰到這類吃基本觀念的問題，就束手無策了。想想 "架構面試題" 這系列也停了好一陣子，於是就想來寫這篇了。





















---------

note1.sql

```sql
-- select top 100 * from DIRINFO
-- select count(*) from DIRINFO
-- select count(*) from FILEINFO
-- truncate table [FILEINFO]
-- truncate table [DIRINFO]
-- delete [DIRINFO]

declare @root int;
select @root = ID from DIRINFO where fullname = 'c:\windows'
print @root
--select * from DIRINFO where fullname = 'c:\windows'

/*
--select * from (
	select '<DIR>' as type, name from DIRINFO where PARENT_ID = @root
	union
	select '' as type, FILE_NAME as name from FILEINFO where DIR_ID = @root
--) obj order by name asc
*/

;with DIR_CTE(ID, NAME, FULLNAME, LV) as
(
	select ID, NAME, FULLNAME, 1 as LV
	from DIRINFO
	where PARENT_ID = @root

	union all

	select D1.ID, D1.NAME, D1.FULLNAME, D2.LV + 1
	from DIRINFO D1 inner join DIR_CTE D2 on D1.PARENT_ID = D2.ID
)

select * from DIR_CTE
--select F.* from DIR_CTE D inner join FILEINFO F on D.ID = F.DIR_ID where F.FILE_EXT = '.dll'

--where ROOT_ID = 339957

```



note2
```sql
--
--  RAW data to SOL2
--

-- truncate table SOL2_DIRINFO

declare @root int;
select @root = ID from DIRINFO where fullname = 'c:\'

;with DIR_CTE(ID, NAME, FULLNAME, LV) as
(
	--select ID, NAME, FULLNAME, 0 as LV
	--from DIRINFO
	--where ID = @root

	--union

	select ID, NAME, FULLNAME, 1 as LV
	from DIRINFO
	where PARENT_ID = @root

	union all

	select D1.ID, D1.NAME, D1.FULLNAME, D2.LV + 1
	from DIRINFO D1 inner join DIR_CTE D2 on D1.PARENT_ID = D2.ID
)

--insert into SOL2_DIRINFO (ID, NAME, FULLNAME) select ID, NAME, FULLNAME from DIRINFO where PARENT_ID = 0;
--insert into SOL2_DIRINFO (ID, NAME, FULLNAME, LV1) select ID, NAME, FULLNAME, ID as LV1 from DIR_CTE where LV = 1;
--insert into SOL2_DIRINFO (ID, NAME, FULLNAME, LV2) select ID, NAME, FULLNAME, ID as LV2 from DIR_CTE where LV = 2;
--insert into SOL2_DIRINFO (ID, NAME, FULLNAME, LV3) select ID, NAME, FULLNAME, ID as LV3 from DIR_CTE where LV = 3;
--insert into SOL2_DIRINFO (ID, NAME, FULLNAME, LV4) select ID, NAME, FULLNAME, ID as LV4 from DIR_CTE where LV = 4;
--insert into SOL2_DIRINFO (ID, NAME, FULLNAME) select ID, NAME, FULLNAME from DIR_CTE where LV > 5;


/*
select * from DIRINFO
select * from SOL2_DIRINFO
*/
--
-- post process
--

update S set LV4 = D.PARENT_ID
from SOL2_DIRINFO S inner join DIRINFO D on S.LV5 = D.ID
where LV5 is not null

update S set LV3 = D.PARENT_ID
from SOL2_DIRINFO S inner join DIRINFO D on S.LV4 = D.ID
where LV4 is not null

update S set LV2 = D.PARENT_ID
from SOL2_DIRINFO S inner join DIRINFO D on S.LV3 = D.ID
where LV3 is not null

update S set LV1 = D.PARENT_ID
from SOL2_DIRINFO S inner join DIRINFO D on S.LV2 = D.ID
where LV2 is not null



update S2 set LV1 = S1.LV1, LV2 = S1.LV2, LV3 = S1.LV3, LV4 = S1.LV4, LV5 = S1.LV5
from SOL2_DIRINFO S1 inner join SOL2_DIRINFO S2 on CHARINDEX(S1.FULLNAME, S2.FULLNAME, 1) = 1
where S1.LV1 is not null and S2.LV1 is null
```