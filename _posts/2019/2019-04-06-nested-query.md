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

RDBMS + SQL 是個絕配，將資料轉成表格，加上結構化的查詢就能解決過去 80% 的問題了。不過 tree 不限定階層這個要求，對於 RDBMS 就有點頭痛。你要把階層攤平，你無法預測最多要幾層...，如果你結構上只處理上下兩層，那 query 在 join 時也會碰到一樣困境，不知道要 join 幾次...。搭配特殊語法 (如 T-SQL CTE), 或是用 programming language 搭配, 就必須在複雜度與效能間做取捨了。

我覺得這是個不錯的題目，能鑑別出你的基礎知識夠不夠札實，能否靈活運用；也能看出你是否容易被既有的工具或是框架限制住做法的測驗。這邊先不討論 tree 到底該不該擺在 RDBMS 上面處理這種議題，那是另一個層次的討論。我想談的是背後的 storage 就限定在 RDBMS 的話，那我們有哪些方法能夠妥善的處理他?

準備好接受挑戰了嗎? 想是看看的話不要急著往下看，你可以先想想你工作上要是面臨這樣的問題，你會怎麼去設計解決方式? 這種問題很常碰到啊，隨便舉過去我處理過的案例就好幾種應用，例如:

1. 文件 (分類及權限)
1. 商品 (分類)
1. 組織圖

...

<!--more-->

這類資料的搜尋，往往都要搭配複合的條件，例如:

1. 找出特定分類 (含以下子分類) 的所有商品，同時滿足其他條件 (如售價範圍等等)。
1. 找出符合權限 (假設權限綁定在分類上面) 的所有文件，同時符合關鍵字等其他條件過濾。
1. 找出某個部門以下所有單位，同時符合職等或是年資等過濾條件的員工。

對於 SQL 稍有概念的就知道，如果你不能在 SQL 的層級，把兩大過濾條件都處理掉 (一個是分類的過濾條件，另一個是其他過濾條件)，然後 join 取得最終結果的話，兩邊分開處理後，再把資料倒到 code 端去合併，是很沒有效率的。因此後面的幾種方式探討，都有這些前提須要被滿足:

1. 需要支援階層的異動
1. 需要支援階層的查詢 (例如某分類以下的所有分類)
1. 大量資料下，效能必須維持在合理範圍內 (不考慮把整個 tree 都載入到 memory 裡，用 code 去解決)

準備好了嗎? 想挑戰的先別往下看，自己想想你會怎麼解決這需求吧! 想完之後歡迎往下看看我整理的做法。



# 前言: 寫這篇文章的動機

繼續之前，照例來聊一下，我寫這篇文章的動機: 基礎知識

雖然這篇的內容跟微服務 (Microservices) 沒啥關聯，但是我還是拿微服務來開個頭...。我常常被問到跟維服務相關的幾個 FAQ, 最多的就是微服務架構下的資料該怎麼處理了。微服務架構，主張把大型系統切割成獨立運作的小服務，中間只靠 API 來協做；因為服務切割的夠小，因此開發團隊有能力獨自維護，同時能負擔開發與維運的任務 (對，就是 DevOps)。這架構下，過去獨立且龐大的關聯式資料庫，當然也一起被切開了 (如果不切割資料庫，改成微服務架構的目的還存在嗎?)。

資料庫如果隨著服務的切割，也被隔開了的話，過去透過大量 join 操作，應該都會被一連串的 API 查詢取代。這部分有沒有效率我就暫時不討論了，不在這篇我要探討的主題。我想談的重點是，切割之後，我們面對的資料問題，就跟過去不大一樣了。我們會從整個 application 範圍的資料維護，縮減到單一功能 / domain 的資料維護。但是你要切割成微服務通常都會有服務量增加的前提，因此資料的量應該都會比過去還要大幾個量級。



這裡就衍生出一個問題: 除了 Dev + Ops 之外，那原本 DBA 負責的資料管理任務，也一併回歸到開發團隊身上嗎?

這其實是個很弔詭的問題，就跟 DevOps 一樣，背後的意義往往都被誤解了。我先從較容易理解的 DevOps 開始，DevOps 的核心觀念並不是 "單純" 的要開發團隊把維運的任務搶回來而已那麼簡單，而是要藉著開發團隊自己維運，快速取得回饋，同時思考該如何反應在流程與開發的改善。開發人員若有維運的經驗，則更能開發出善於維運的服務 (design for operation), 就能更輕鬆的讓維運自動化, 不需要人工的介入。

同樣的，讓開發團隊自己規劃資料的管理也一樣，並不是要開發團隊把 DBA 的任務搶回來，而是當團隊對於服務的邊界掌握的更精準時，資料的複雜度會降低 (但是量會變大)，過去關聯式資料庫的 "關聯" 問題，會被轉移到跨服務的 "API" 身上。若單一服務內的資料庫複雜度降低了，同時又有 NOSQL 這類新興的服務盛行，過去必須依靠 DBA 才能做好的資料管理，理論上開發團隊現在就能顧好它了。


當你的資料複雜度降低時 (單一一個服務，也許只需要 10 個資料表)，因應 SaaS 的發展，換來的是資料量會爆增 (開始會衍生多租戶架構的問題) 的問題。加上資料的進出口，都由過去的 DBMS 往外移，變成 API level 的問題了，你看出關鍵點了嗎? 處理巨量資料的各種問題，都從 DBA 轉移到 DEV 身上了。這時，吃的不是你對於工具的掌握能力，而是吃你的整合能力與資訊科學的基礎能力。

因為不斷看到這種情況，也不斷的看到很多資深的工程師，碰到這類吃基本觀念的問題，就束手無策了。想想 "架構面試題" 這系列也停了好一陣子，於是就想來寫這篇了。



# 前言



























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