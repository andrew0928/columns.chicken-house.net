# [Azure] Multi-Tenancy Application #3, (資料層)實作案例

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼作者希望在 Data Context 這層處理掉所有租戶資料隔離的問題？
作者希望讓開發者能用「一般應用程式開發」的思維來撰寫 Multi-Tenancy 應用，若在 Data Context 就完成資料隔離與過濾，後續的程式邏輯就不必每次都手動判斷租戶，能大幅簡化開發負擔。

## Q: 這個範例的 Web 層如何為每個租戶提供獨立的 URL？
透過 ASP.NET MVC 的 Routing 機制，在 controller 及 action 之外再切出一層「client」路由片段，讓每個租戶都擁有自己的虛擬目錄與獨立網址。

## Q: 為什麼「訂便當系統」適合拿來當 Multi-Tenancy 應用的 POC？
1. 用戶通常是部門或辦公室等「團體」，需要每日訂單與會員管理。  
2. 採 SaaS 模式營運合理，平台方可統一維護共用資料。  
3. Hosting 端可與多家餐廳合作，分享餐廳資料並抽佣。  
4. 後台 BI 可分析訂單與合作餐廳成效，衍生更多商業機會。

## Q: 這個 POC 最初鎖定的技術平台是什麼？
後端採用 Windows Azure Storage（主要是 Azure Table Storage），前端則選擇 ASP.NET MVC4；資料操作模式比照 Entity Framework Code-First。

## Q: HubDataContext 需要具備哪些核心能力？
1. 在取得 HubDataContext 時，即能確定目前所屬的 Client（租戶）範圍。  
2. 只暴露該 Client 可用的資料集，開發者即使 Linq 過濾寫錯，也無法取到其他租戶的資料。  
3. 系統級（共用）的全域資料不受租戶限制，所有 Client 皆可存取。

## Q: 作者引用 Luddy Lee 前輩的哪句建議？其意涵為何？
「寫雲端的程式測試跟佈署都比以前麻煩，因此做好完整的規劃跟測試就變得更重要。」  
意即在雲端環境開發，部署與測試流程複雜度提高，必須更加重視單元測試與事前規劃，才能避免後續問題。

## Q: HubDataContext 的實作目前進度如何？
介面與主要實作已完成並通過單元測試，標誌著資料層第一階段目標達成；接下來將進一步規劃 Azure Table Storage 的資料模型與實體類別。