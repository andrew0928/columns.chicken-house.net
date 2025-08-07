# EF#2. Entity & Encapsulation

## 摘要提示
- ORM 目的: 透過對應機制把物件狀態持久化到關聯式資料庫，並讓開發者專注於物件思維。  
- 物件╱資料庫斷層: 物件技術快速演進，RDBMS 本質 20 年不變，三層式架構中產生落差。  
- 對應兩條路: ORM 框架或 OODB，未來五到十年仍是 ORM 大顯身手的舞台。  
- 物件三核心: 封裝、繼承、多型；本文聚焦「封裝」在 Entity Framework 的實踐。  
- 範例資料表: Users 表僅六欄，含 ID、PasswordHash、SSN、Gender… 等基礎欄位。  
- 未封裝問題: 直接公開 PasswordHash、SSN 與 Gender 依賴關係易產生不一致或洩露。  
- 封裝重構: 利用 partial class 隱藏實作細節，改以 Password setter、ComparePassword 方法與唯讀 Gender 枚舉呈現。  
- 效益比較: 新程式碼更簡潔、邏輯清楚並集中驗證邏輯，降低 SQL 端 trigger 或 constraint 複雜度。  
- EF 強項: 複雜商業規則可在實體層封裝，避免侷限於 SQL 能力與效能。  
- 後續主題: 將延伸討論繼承、多型與查詢機制，完整評估 Entity Framework 價值。  

## 全文重點
本文是「Entity Framework 與物件導向設計」系列第二篇，作者在第一篇說明概念後，此篇藉由實作示範「封裝」在 Entity Framework（EF）中的必要性與實踐方式。文章開頭先重申 ORM 的終極目標──讓程式物件與關聯式資料表之間「對應」得既簡單又自然，因為物件技術已進化到可以解決大多數應用問題，而 RDBMS 仍停留在 table＋relationship 的世界，兩者落差導致開發者被迫在資料存取層作大量轉換。雖然也有人企圖將資料庫本身物件化（OODB），但可預見的未來仍是 ORM 扮演關鍵角色。

要客觀評估 EF 是否值得投資，必須從物件導向三大核心（封裝、繼承、多型）與查詢能力來觀察。本文聚焦「封裝」，示範未封裝的 User Entity 如何讓程式散布著重複且容易出錯的邏輯，並一一點出問題：1) 直接公開 PasswordHash 泄露實作，2) 台灣身份證字號與性別具函數相依卻毫無約束，容易資料不一致。

接著作者利用 EF 部署的 EDMX 與 partial class 擴充，將 PasswordHash 與 GenderCode 設為私有，對外僅提供 Password setter、ComparePassword 方法，以及將 GenderCode 轉為 Enum 的唯讀 Gender 屬性。同時在 OnSSNChanging 部分實作同步更新 GenderCode 的邏輯，確保資料一致並將驗證集中於物件層。

重構後建帳號與驗證密碼的程式碼大幅精簡，開發者無須再手動計算 hash 或比對陣列，也不必關心 SSN–Gender 依賴。相較於在 SQL 端撰寫 trigger 或複雜 constraint，將商業邏輯封裝於 Entity 更符合物件導向精神，並能保持 DB 結構單純、跨系統一致。最後作者預告接下來將探討 EF 支援的繼承與多型特性，深入證明 EF 的物件導向能力。

## 段落重點
### ORM 與對應機制的價值
作者先回顧 ORM 的共同使命：簡化物件與資料表的映射，使開發專注於商業邏輯。由於 RDBMS 延續 20 年仍以 table+SQL 為核心，而物件世界對應層面需求卻日益複雜，三層式架構容易在資料層出現斷層。目前可行方案分兩條線：一是透過 ORM 把兩個世界「黏」起來；二是將資料庫本身物件化（OODB）。就現階段與可預見的未來，ORM 仍具備成熟工具與廣大市場，因此值得深入探討。

### 物件導向三核心切入點
要判斷某 ORM 框架是否稱職，必須回到物件導向的封裝、繼承、多型與查詢能力四面向。作者提醒讀者先具備 EF 基礎，並提供 Microsoft MVP 朱明中的系列文章當作入門教材。本文主角是「封裝」，其它面向將於後續章節揭露。

### 未封裝的 User Entity 範例
文章舉出最直觀的 Users 資料表（ID、PasswordHash、SSN、Gender…），並在 EDMX Designer 直接匯入後撰寫新增帳號與驗證密碼程式碼。由於屬性完全開放，開發者需自行計算 MD5、比較位元組陣列，也必須確保 SSN 與 Gender 一致。此作法導致：
1. 密碼實作細節外洩，增加安全與維護風險。
2. SSN 與 Gender 的函數相依無法保證，產生資料不一致或需倚賴複雜 SQL trigger。

### 封裝缺失帶來的風險
從物件導向觀點，User 應只公開「驗證密碼」之能力，而非暴露密碼本身或其 Hash。同樣，Gender 應由 SSN 推得，不該讓前端自由修改。若繼續放任欄位裸露，程式不僅雜亂易錯，也迫使資料庫層塞入不必要的防禦性邏輯，如複雜 constraint、trigger，進而削弱系統彈性。

### 利用 partial class 重構與封裝
作者示範在 EF 產生的 User 類別外，再宣告 partial class 補強：
1. 將 PasswordHash、GenderCode 的存取子標為 private。
2. 新增 Password setter，自動計算 MD5 並寫入 Hash。
3. 提供 ComparePassword 方法統一比對流程。
4. 以 Enum GenderCodeEnum 封裝 Gender，僅開放唯讀 Getter。
5. 借助 OnSSNChanging 部分方法在 SSN 更新時同步計算 GenderCode，確保資料一致。
這些改動將實作細節與商業規則集中於單一位置，維護、更動或擴充都更安全且容易測試。

### 重構後的程式示範與效益
重新撰寫「建立帳號」與「檢查密碼」示例可發現：
- 開發者只需設定 Password 明碼，亦無需自行計算 Hash。
- 驗證僅呼叫 ComparePassword 即可得結果，避免重複程式。
- 不存在 SSN╱Gender 不一致風險，亦省去 SQL 端複雜度。
因此，透過 EF 搭配封裝能讓程式碼更精簡、意圖更清晰，也避免因實作分散而導致的 bug 與維護成本。

### 小結與後續預告
文章以具體範例證明「封裝」在實體層的重要性及 EF 的天然優勢：可利用 partial class 無縫擴充 Entity，將複雜商業規則藏於物件中，而非交由資料庫或前端各自實作。作者最後預告將於系列後續篇幅繼續示範 EF 在「繼承」與「多型」上的應用，協助讀者更全面評估 EF 的投資價值。