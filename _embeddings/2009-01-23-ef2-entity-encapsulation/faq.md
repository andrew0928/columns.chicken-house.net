# EF#2. Entity & Encapsulation

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼需要 ORM（例如 Entity Framework）來連接物件技術與關聯式資料庫？
物件技術演進快速，已能解決大多數軟體開發需求；但 RDBMS 的核心仍停留在「Table + Relationship + SQL」的模式，兩者面對的是截然不同的世界，造成三層式架構中的斷層。ORM 以「對應」機制把物件狀態持久化到關聯式資料庫，藉此橋接這兩個世界，並試圖讓程式設計師以更貼近物件導向的方式操作資料。

## Q: 除了使用 ORM，還有什麼辦法可解決物件世界與 RDBMS 的落差？未來五到十年哪一條路更被看好？
另一路徑是直接改造 RDBMS，讓資料庫本身具備物件導向特性（OODB）。然而就可預見的五到十年來看，ORM 仍被認為大有可為，因為只要把「對應」做到位，ORM 就能在應用程式端接近 OODB 的願景。

## Q: 文章中第一版 User 類別設計存在哪兩大問題？
1. 直接公開了 `PasswordHash`，洩漏過多實作細節。  
2. 在台灣的規則中身份證字號（SSN）與性別（Gender）具函數相依關係，但類別中未加以強制，容易造成資料不一致。

## Q: 重構後的 User 類別如何改進密碼與性別欄位的處理？
‧ 密碼：將 `PasswordHash` 改為 private，對外只提供 `Password` 的 Setter 與 `ComparePassword()` 方法，外部程式無法直接存取 Hash 值。  
‧ 性別：將 `GenderCode` 隱藏為 private；在 `OnSSNChanging` 事件裡根據新的 SSN 自動同步 `GenderCode`，並對外僅以唯讀屬性 `Gender`（Enum）公開。

## Q: 加入封裝性後，程式碼與系統整體品質有哪些具體提升？
重構後的程式碼更精簡、邏輯更清晰，減少重複與錯誤；同時能防止不合法資料寫入資料庫，降低散佈 `SqlException` 的機會，整體維護性與可靠度都大幅提高。

## Q: 作者之後將從哪四個面向持續檢視 Entity Framework 的支援度？
將以物件技術的三大核心「封裝、繼承、多型」以及資料庫最需要的「查詢（Query）」四個向度來觀察 Entity Framework 的能力與價值。