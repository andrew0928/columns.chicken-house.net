# [Azure] Multi-Tenancy Application #1, 設計概念

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 什麼是 Multi-Tenancy？
Multi-Tenancy（多租戶）是一種讓同一套應用程式透過適當的切割，能「分租」給多個客戶共同使用的設計概念，與傳統一套系統只服務一個客戶的作法不同。

## Q: 在資料隔離層面，最常見的三種 Multi-Tenancy 架構是哪些？
1. Separated DB（各租戶各自一個資料庫）  
2. Separate Schemas（共用資料庫，但各租戶有獨立的 Schema／資料表）  
3. Shared Schema（共用同一資料庫與資料表，以 TenantID 欄位區分資料）

## Q: Separated DB 架構的主要特色與優缺點是什麼？
特色：每個客戶使用獨立的資料庫，隔離等級最高；就算工程師粗心，也很難把不同客戶資料混在一起。  
缺點：需為每位客戶建立與維護一個資料庫，成本最高。

## Q: Separate Schemas 架構帶來哪些好處與挑戰？
好處：多個客戶共用同一資料庫即可，相較 Separated DB 成本較低；因為不同 Schema 隔離，資料串錯風險仍低。  
挑戰：實作稍複雜，但 SQL Server 2005 之後支援 Schema，複雜度已有所降低。

## Q: Shared Schema 架構最大的風險是什麼？
所有客戶共用同一組資料表，靠 TenantID 欄位區分。如果任何一條 SQL 少加「WHERE TenantID = …」，就可能把 A 客戶資料顯示到 B 客戶畫面上，資料外洩風險最高。

## Q: 在 Shared Schema 模式下，若要擴充資料結構，常見做法有哪些？
常見做法是預先在每張表保留幾個備用欄位（如 Column1、Column2…），或改採類似 NoSQL 的 Name-Value 結構。不過如此一來 SQL Query 會變得難寫且不易維護。

## Q: 如果只能使用 Windows Server + SQL Server 來開發企業內部的 Multi-Tenancy 應用，該參考哪份文件？
可以參考 MSDN 2006 年的文章〈Multi-Tenant Data Architecture〉，該文對設計、開發、上線及調校各階段皆有詳細說明。

## Q: 今日使用 Microsoft Azure 與 ASP.NET MVC4 來開發 Multi-Tenancy 應用程式，相較過去有何優勢？
Azure PaaS 與成熟的 MVC 架構大幅降低了開發與部署大型 Web 應用的門檻，讓過去需自行摸索的隔離、擴充與維運機制，能透過雲端服務與現成框架更簡潔地實現。

## Q: 本系列文章的下一步將探討什麼？
作者將在下一篇文章中說明，如何透過當前熱門技術（Microsoft Azure + ASP.NET MVC4）實際打造優雅的 Multi-Tenancy Web 應用。