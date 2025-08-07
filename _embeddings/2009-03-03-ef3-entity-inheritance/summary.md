# EF#3. Entity & Inheritance

## 摘要提示
- 物件導向繼承: 繼承是 OOP 的靈魂，ORM 必須能把它正確保存到關聯式資料庫中。
- Virtual Table: C++/CLR 以虛擬表實作繼承，概念上可對應到資料庫的 Table Schema。
- 映射核心: 把「子類別擁有父類別欄位」轉成資料表欄位配置是 ORM 首要課題。
- Table Per Hierarchy (TPH): 同一張表存放整個繼承樹，實作簡單但欄位與資料量膨脹。
- Table Per Type (TPT): 依類別切表並以 PK/FK 串聯，正規化好但查詢需要多層 JOIN。
- Table Per Concrete Type (TPC): 每個具體子類別一張表，折衷兩者優劣，欄位異動成本高。
- EF 與 NH 命名: EF 用 TPH/TPT/TPC，NH 為「class hierarchy / subclass / concrete class」。
- 選擇考量: 資料量、繼承深度、查詢頻率及 Schema 約束決定最佳策略。
- 優缺點表: 文章列出三策略適用與限制，便於實務評估。
- 系列續篇: 文末預告將持續探討 EF 與物件導向設計的其他議題。

## 全文重點
文章從物件導向的核心──繼承──談起，指出如果沒有繼承，OOP 的威力將大打折扣；而 ORM 要在關聯式資料庫中保存具有繼承關係的物件，就得先解決「資料表如何描述父子類別共用與差異欄位」的問題。作者先回顧 C++ 與 CLR 以 Virtual Table 實作繼承的歷史，讓讀者理解「物件實體其實只是一段連續記憶體，唯靠虛擬表把父類別的成員帶進來」。把這概念平移到資料庫時，可以把 Virtual Table 想成 Table Schema，把 Instance 想成資料列，如此便能把「Is-A 關係」翻譯為「欄位拷貝或拆分」。

接著介紹三種主流資料表映射策略。第一種 Table Per Hierarchy (TPH) 以單表存放整個階層，並用 Discriminator 欄位區分型別，優點是實作與查詢簡單、欄位調整方便，缺點是資料量大時效能下滑且 Schema 難加嚴格限制。第二種 Table Per Type (TPT) 切分為父表與多個子表，用 PK/FK 連接，保持高度正規化且可對各層施加約束，但查詢須多層 JOIN，階層愈深成本愈高。第三種 Table Per Concrete Type (TPC) 為每個具體子類別獨立建表，綜合前兩者的優勢並能個別加 Constraint，但要同時抓取多型集合時需要 UNION/JOIN，且父類別欄位一變動就要同步變更所有子表。

作者再說明 Entity Framework 與 NHibernate 都支援這三種策略，只是命名略異，並引用官方文件連結以便進一步深入。最後附上一張比較表，整理各策略適用與不適用的情境，讓開發者能依據資料量、查詢模式、繼承深度與 Schema 彈性挑選最佳方案。文章以「未完待續」收尾，預告後續將繼續討論 EF 與物件導向設計相關議題。

## 段落重點
### 繼承在物件導向與 ORM 中的地位
作者強調繼承是 OOP 的核心特色，若拿掉繼承 OOP 就失去魅力；而 ORM 若不能妥善保存繼承關係，就無法稱職地在 RDBMS 與物件世界之間橋接。為了讓讀者意識到問題本質，文章先把焦點放在「父類別資料怎麼跟著子類別存進資料庫」這個最基本需求。

### Virtual Table 與資料表對應的直覺聯想
回顧 C++/CLR 的 Virtual Table 機制：父類別成員在編譯期被擺進虛擬表，物件執行期透過該表決定實際方法與欄位位置。將此思維映射到資料庫時，Virtual Table 相當於 Table Schema，而一個物件實例則對應資料表中的一列，於是「繼承＝父欄位複製」的想像便成形，為後續三種資料表策略埋下伏筆。

### 三種繼承映射策略概述
1. Table Per Hierarchy (TPH)：把父子類別所有欄位集中在同一表，並用類別識別欄位區分型別。實作最快，適合資料量不大或查詢必須一次抓全家族時使用，但欄位多且 Null 值多，效能與完整性檢查皆受限。  
2. Table Per Type (TPT)：父類別一表、每個子類別各一表，靠 PK/FK 連接。能維持高度正規化並各自加 Constraint，適用需要嚴謹 Schema 控制且查詢多針對單一型別的系統；但跨型別集合查詢需多重 JOIN，階層越深效能越差。  
3. Table Per Concrete Type (TPC)：每個具體子類別獨立建表，表結構完整包含父欄位。查詢單一型別最簡單，也能設定獨立 Constraint，但抓多型集合需 UNION/JOIN，且父層欄位變動要同步所有子表，維護成本高。

### EF 與 NHibernate 的對應與優缺點比較
Entity Framework 依序稱為 TPH、TPT、TPC；NHibernate 分別叫做 Table per class hierarchy、Table per subclass、Table per concrete class。兩者提供的機制本質一致，只因設計哲學或 API 命名不同。文章附表列出各策略「適用於／不適用於」的情境，幫助開發者根據資料量、查詢模式、階層深度與 Schema 彈性等面向做取捨。

### 結語與後續
作者總結三種策略無優劣絕對，端看實務需求而定；並預告系列文章將持續探討 Entity Framework 與物件導向設計的其他議題，鼓勵讀者先消化本篇概念，再對照官方文件與實際專案做實驗。