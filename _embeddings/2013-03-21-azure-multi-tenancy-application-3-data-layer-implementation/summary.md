# [Azure] Multi-Tenancy Application #3, (資料層)實作案例

## 摘要提示
- Multi-Tenancy: 目標是讓單一資料儲存體在邏輯上被切成多個獨立分割區，供不同租戶安全共用。  
- DataContext: 於資料層即完成租戶隔離，開發者以一般 EF 使用方式即可操作多租戶資料。  
- MVC Routing: 透過自訂路由在 URL 加入 Client 區段，達成網站層級的虛擬分割。  
- SaaS 營運: 系統設計預設以雲端服務模式對外出租，便於集中管理與商業變現。  
- 案例—訂便當系統: 以日常易延伸的情境示範多租戶系統的切分、共用與商機。  
- Hub / HubData: 將平台稱為 Hub，租戶專屬資料統稱 HubData，其餘則為全域共用資料。  
- 需求收斂: 透過 Scrum Story 整理 POC 範圍，聚焦在資料存取與隔離機制。  
- 介面設計: HubDataContext 必須在取得時即確定租戶範圍，並只回傳該租戶可見的集合。  
- 單元測試: 雲端開發部署成本高，故以完整測試確保程式正確性與維護性。  
- Azure Table + Code First: 以類似 EF Code First 流程為 Table Storage 建模，不再受限傳統 Schema。

## 全文重點
本文為「Azure 多租戶應用程式」系列第三篇，聚焦在資料層的實作。作者期望在 DataContext 階段就完成租戶資料隔離，使開發人員能以熟悉的 Entity Framework 操作模式開發多租戶系統；同時，在 Web 端以 MVC Routing 加入「Client」節點，讓每個租戶擁有獨立 URL，看似擁有專屬應用。整體架構選擇 Windows Azure Storage 與 MVC4，並以「訂便當系統」作為情境範例，示範 SaaS 模式下的商業及技術需求。

作者提出 Hub/HubData 概念：Hub 為平台本體，HubData 為租戶私有資料；全域資料則不受租戶限制。為此設計 HubDataContext 介面，需達成三要件：(1) 在建構時即可確認當前租戶；(2) 僅暴露該租戶可見之資料集合，防止誤取他人資料；(3) 全域資料可供所有租戶完整存取。作者以 Unit Test 驗證 DataContext 正確分流，並強調雲端環境測試的重要性。

資料儲存採 Azure Table Storage，因其無固定 Schema、支援大量水平擴充，且與 EF Code First 概念相近，開發者可直接以 C# 定義 Entity Classes。文章最後附上簡要類別圖，示範訂便當系統中會員、訂單等實體如何與租戶識別整合。

## 段落重點
### 設計目標與前言
作者回顧前篇對多租戶資料層設計的討論，本篇不再理論而轉入實作。核心目標是在 DataContext 階段完成租戶資料隔離，讓開發者以「一般單租戶開發思維」即可安全操作多租戶資料；Web 層亦需透過 Routing 讓 URL 呈現租戶的獨立性。

### 以訂便當系統為示範的 Multi-Tenancy 構想
選擇「訂便當系統」作為 POC，因其天然具備群組使用、可 SaaS 化、可共享餐廳資料、具 BI 商機等特性。系統營運方可提供共通餐廳清單、收取手續費，並透過後台報表洞察商業機會，示範多租戶應用的價值。

### POC 使用者故事與需求收斂
為避免需求無限擴張，作者引用 Scrum Story 格式收斂範圍，聚焦資料隔離、租戶路由與共用資料機制。故事定義了平台端（Hub）與租戶端（Client）的角色與職責，確立後續實作方向。

### Hub 與 HubData 的概念及 DataContext 介面
整套系統稱為 Hub，租戶資料稱 HubData。HubDataContext 需在建立時綁定租戶，並僅回傳該租戶的資料集合；全域資料則不受限制。作者展示介面設計及使用範例，說明如何以 LINQ 操作時仍能保證租戶隔離。

### 單元測試與開發心得
作者花費時間完成實作並通過單元測試，引用前輩 Luddy Lee 的觀點—雲端佈署與測試成本高，故更需完善的規劃與自動化測試。透過測試確保 DataContext 能正確依租戶分流及保護資料。

### Azure Table Storage 與 Code First Schema
最後說明資料模型採 Azure Table Storage，無固定 Schema、可依 Entity Class 動態生成，開發體驗類似 EF Code First。作者以類別圖示範會員、訂單等實體，說明如何在多租戶環境下同時儲存租戶識別與商業資料，以利擴充與維護。