上篇花了一堆口水，說明各種 data layer 的設計方式，這回不噴口水了，直接來實作...。

開始前先說明一下我的期望，我先假設各位都用過 Entity Framework 或是這類的 solution, 我希望在 data context 這層，就能處理掉所有隔離 tenancy data 的問題，也就是我可以用一般 application 的開發概念來開發 multi-tenancy 的 application。換另一個說法，我希望在一個 storage 內，模擬出讓每個 tenancy 都有獨立的 storage 可運用的介面。

Web 的這部份也是一樣的概念，我希望在網址這層，邏輯上就讓每個 tenancy 有獨立的 URL (虛擬目錄)。有這種網址上自行客製的需求，當然是非 MVC 不可，因此這次會在 MVC 的 Routing 上動手腳，除了 controller 及 action 之外，能夠再切出一層 client 出來，讓 application 也像是能夠虛擬化一樣，每個用戶可擁有自己的 partition。

最後當然也希望 WEB 這邊的架構，能緊密的跟 DATA 這邊結合。讓開發人員就照一般的方法就能快速開發出Multi-Tenancy Applicaiotn。寫這種系統，若規模不夠大就沒意思了，因此我初期就把目標鎖定在 Windows Azure Storage + MVC4, 而應用程式就以常見的 "訂便當系統" 為案例。

訂便當系統，是個很適合開發成 Multi-Tenancy 模式的主題。原因有幾個:

1. 這系統一定是一個團體才會需要用的，如果你只有兩三個人，用講的比較快... 通常是部門、辦公室、或是規模不大，可以一起訂便當的團體會需要使用。這需要基本的每日訂單管理，還有簡單的會員管理功能。

2. 既然是 Multi-Tenancy Application, 那麼用 SaaS (Service as a Service) 的方式營運也是很理所當然的。所有客戶通用的內容，就可以由營運單位來負責整理及規劃。

3. 除了切割很多獨立的 "分割區" 各自運作之外，Hosting 的一方其實也有很多商機，像是合作的餐聽或是便當店，這些資料就可以共用。甚至是可以主動匯入，讓客戶訂購起來更方便。若這樣能為便當店帶來生意，Hosting 的一方抽點庸金也是很合理的 XD

4. 後台 BI 也是很有商機的一環。Service Hosting 的一方，就可以看看各種統計報表，看跟那家餐廳合作的機會較大，另外也可以設計客戶 share 他們自己開發的便當店資訊，給其它客戶使用。若越多客戶採用，可以給些系統租金的回饋等等….

越想越多，再想下去這個 POC 用的 prototype 就寫不完了，需求給各位讀者再去延伸，我這邊作 POC 就把需求收殮一下...。偷學一下 SCRUM 的 story 撰寫技巧，以下是我這次 POC 要實作的 stories:

好，看來一個設計良好的 DataContext, 可以省掉不少工夫。大部份的 coding logic, 都是在客戶的專區內運作的。我把整套系統稱作 "Hub", 而每個客戶專區內的資料，就通稱為 "HubData", 如會員資料，或是訂單等等。而其它非 HubData, 就是整個系統通用的資料。因此，我希望 Hub 用的 Data Context 能有這些功能:

1. 取得 HubDataContext 時，就已經能確定目前是在那個 Client 的使用範圍。
2. HubDataContext 能直接提供該 Client 才能用的 Data Collection, 我只要拿來再用 Linq 過濾即可，即使我沒控制好，也不會拿到別的 Client 專區內的 HubData。
3. 全域 (共用) 的資料則不在此限。每個 Client 都能完整存取這些資料內容。

OK，噴了三篇的口水，終於看到第一段程式碼了 Q_Q，HubDataContext 的 interface 看起來要像這樣:

使用它的 Code 要像這樣 (這段我就寫在 unit test 內…):

花了一點時間，總算把實作都寫出來，成功通過單元測試了。套句 Luddy Lee 前輩常說的話，寫雲端的程式測試跟佈署都比以前麻煩，因此做好完整的規劃跟測試就變的更重要了，單元測試是少不了的，請各位切記。過去吃了很多苦頭，更加證明 Luddy Lee 前輩講的話一點都沒錯....

最終的 HubDataContext 實作如下... 其實也沒幾行:

OK，第一步通過了，接下來我們開始來規劃一下 Data Schema …. Azure Table Storage 已經沒有所謂的 "schema" 這回事了，它完全就像 EF5 裡面的 code first 一樣，你的 Data Entity class 定義好，就可以跑了... 這些細節就不在這篇裡多做說明，各位有興趣可以參考其它的資料。既然都是 Code First 開發模式了，我就直接用 class diagram 來描述這些資料 (Entity) 之間的關係: