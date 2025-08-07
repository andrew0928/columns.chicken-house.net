# 微服務架構 #1, WHY Microservices?  

## 摘要提示
- 微服務興起: Container 技術降低部署門檻，使 Microservices 從大型企業專利變成中小型團隊也能採用的主流架構。  
- SOA 演進: Microservices 可視為 SOA 在雲端與容器時代的落地版本，強調小型化、自治與 API 溝通。  
- Monolithic 限制: 單體式系統因規模龐大、部署與維運彈性差，難以因應快速變動的商業需求。  
- 重用層級: 重用可分為 Source、Binary 及 Service 三層，Microservices 以 Service 為核心單位。  
- 開發效率: 微服務將複雜度拆分，有利於團隊並行開發、異質技術選型，降低單一程式碼庫的耦合。  
- 維運優勢: 服務可獨立監控、部署與擴充，故障範圍小，資源利用率與可用性顯著提升。  
- DevOps 催化: 容器的快速佈署特性推動 DevOps 流程成形，開發到生產的交付週期大幅縮短。  
- .NET 實踐: 文中以 ASP.NET + Windows Container 為案例，示範微服務於 Microsoft 技術棧的可行性。  
- 部署挑戰: 服務數量倍增帶來部署複雜度，容器成為管理與自動化的關鍵解方。  
- 系列文章: 作者將以三篇文章闡述 Microservices、Container 部署及大型人資系統案例。

## 全文重點
本文源自作者受邀在 Microsoft Community Open Camp 所做的「微服務架構導入經驗分享」，主旨在於說明為何需要 Microservices，以及 Container 技術如何與之相輔相成。作者回顧 2000 年代 SOA 的理想，指出當時受限於工具與部署成本，只能由大型組織採用；隨著 VM 進化至 Container，最小部署單位縮小，SOA 精神遂以 Microservices 形式重生。  
文章首先比較單體式 (Monolithic) 與微服務架構，強調兩者均是將程式碼從基礎堆疊到應用的過程，但組裝時機不同：Monolithic 在開發期即以函式庫或元件方式組合，最終跑成單一 Process；Microservices 則於執行期透過明確 API 將多個自治服務串聯，可使用異質語言與平台。  
作者進一步從「重用」角度切入，將程式碼重用分為 Source Code、Binary 及 Service 三階。傳統單體式多停留在前兩層，而 Microservices 直接以 Service 為最小單位，帶來高度解耦與技術選擇彈性。對開發團隊而言，服務切分降低專案複雜度、利於並行開發；對維運團隊而言，可精細監控、獨立升級、針對瓶頸服務水平擴充，極大提升可用性與資源使用效率。  
然而，服務數量倍增也推高部署複雜度。Container 天生的隔離、映像不可變、快速啟動等特性，剛好補足了微服務在落地時的痛點，同時促成 CI/CD 與 DevOps 的普及。文末作者預告將於後續文章深入說明 Windows Container 的部署流程與實戰案例，並提供簡報、影片、原始碼供讀者參考。

## 段落重點
### 前言：Container + Microservices 的主題緣起
作者於 Community Open Camp 以「.NET + Windows Container」分享微服務導入經驗，強調單談 Container 僅是技術，若從解決問題的角度結合 Microservices，才能凸顯其價值。隨著 VM 進化到 Container，部署成本驟降，Microservices 因而成為顯學，也催生 DevOps 流程。本系列文章鎖定已有 .NET 經驗、但對 Microservices 與 Container 陌生的開發者，將分三篇探討架構原理、部署方法與企業案例。

### 微服務架構(Microservices) v.s. 單體式架構(Monolithic)
單體式應用在開發期即將所有模組以同一語言、框架及編譯鏈組裝為單一可執行檔，最終形成龐大 Process；微服務則將完整應用拆分為多個獨立服務，於執行期透過 API/協定彼此互動，可採異質技術堆疊。其核心目標是控制系統複雜度並提高彈性。微服務雖提高整體服務數量，但每個服務規模較小、自治性高，可獨立開發、部署與維護。

### Develop Team: Reuse of Codes
作者從「重用」角度解析兩種架構。重用層次分為：(1) Source Code—須取得原始碼並重新編譯；(2) Binary—以封裝後元件重用，可直接替換版本；(3) Service—以運行中服務透過 API 重用，無須重新編譯。單體式主要停留在 Source 與 Binary 層，Microservices 則將 Service 當成核心單位，提高技術選擇與版本獨立性，讓團隊能更快迭代並降低耦合。

### Operating Team: Application Maintainess
維運角度下，單體式應用僅能整體監控、整包部署或擴充，一旦故障需重啟整個 Process，且因規模龐大往往難以充分利用硬體資源。反之，微服務讓運維團隊可細緻監控每個服務、獨立升級或重啟，針對瓶頸服務水平擴充，甚至在維修期間局部關閉功能以降低用戶衝擊。唯一挑戰是部署與治理複雜度上升，而 Container 正好提供輕量化、標準化的部署機制，補足此缺口。作者預告下一篇將深入 Container 與微服務的結合細節。