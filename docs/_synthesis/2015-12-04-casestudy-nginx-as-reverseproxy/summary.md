---
layout: synthesis
title: "CaseStudy: 網站重構, NGINX (REVERSE PROXY) + 文章連結轉址 (Map)"
synthesis_type: summary
source_post: /2015/12/04/casestudy-nginx-as-reverseproxy/
redirect_from:
  - /2015/12/04/casestudy-nginx-as-reverseproxy/summary/
postid: 2015-12-04-casestudy-nginx-as-reverseproxy
---

# CaseStudy: 網站重構, NGINX (REVERSE PROXY) + 文章連結轉址 (Map)

## 摘要提示
- 跨平台趨勢：.NET Core 跨平台與雲端時代，使熟悉 Linux/Open Source 成為必然。
- Docker 切入：以 Docker 簡化安裝與配置，降低在 Linux 生態的進入門檻。
- 架構瓶頸：Synology NAS 硬體受限（Atom + 2GB RAM），多容器後效能顯著下降。
- 重構目標：將部屬從 NAS 轉到 Ubuntu Server（舊 NB），提升效能與可控性。
- Reverse Proxy 策略：前端以 NGINX 取代 Apache，統一對外 IP:80 並承擔轉址邏輯。
- 舊文轉址：將 Apache RewriteMap 的 2400 種網址組合改寫為 NGINX map 機制。
- Volume-Container：依 Docker 建議切分資料層，改用 volume container 管理持久化。
- NGINX map 原理：以變數觸發查表（$slug → $slugwpid），達成高效且簡潔的轉址。
- 對照表設計：採外部文字檔 key/value 對應，支援註解，易維護與批次產生。
- 效能與取捨：NGINX 效能佳，Map 彈性高；在固定 400 篇規模下無明顯效能顧慮。

## 全文重點
作者從個人學習與實務需求出發，因應 .NET Core 跨平台與雲端環境盛行，決定跨入 Linux/Open Source 生態。初期以 Synology NAS + Docker 快速搭建 WordPress，並以 Apache Httpd 作為前端 Reverse Proxy，同時用 RewriteMap 解決從舊系統 BlogEngine.NET 過來的大量舊文網址轉址需求。然而 NAS 的硬體受限，當容器數量增加時明顯感受性能瓶頸，促成將整體環境遷移至 Ubuntu Server（以一台舊 NB 部署）以獲得更穩定的計算與記憶體資源。

在新架構中，作者延續「前端 Reverse Proxy + 後端多個 Web/DB 容器」的拓撲，改以 NGINX 取代 Apache 作為反向代理。一方面統一對外服務入口（IP:80）以映射多個 Docker 容器，一方面把複雜的舊網址轉新網址邏輯置於代理層，避免加重 WordPress 的負擔。容器分層方面，依 Docker 官方建議引入 volume container 管理資料持久化，將資料層與應用容器職責分離，利於後續擴展與維護。

核心技術調整在於將 Apache 的 RewriteMap 遷移至 NGINX 的 map 機制。NGINX 配置以 C-like 語法呈現，透過正規表達式擷取舊網址中的 slug 片段，指派給變數 $slug，並藉由 map 宣告把 $slug 對應查表至 $slugwpid，最後以 301 轉址到 /?p=$slugwpid 的新網址。其關鍵是「隱性觸發」：一旦設定 $slug，NGINX 會自動依 map 規則查表填入 $slugwpid，使轉址規則與對照表分離而簡潔清晰。

對照表採外部檔案維護，每行以「key value;」表示新舊對應，支援 # 註解，便於閱讀與批次處理。相較 Apache，NGINX 的 map 還支援萬用字元與正規表達式，具更高彈性；作者推估這可能使其難以像 Apache 一樣將 Map 預編成二進位 Hash，但在 NGINX 本身效能優勢、資料量僅 400 篇且不再成長的新部屬環境下，實測無明顯影響，故不再深究基準測試。

整體而言，此次重構達成數個目標：在保留既有容器化與反向代理策略的前提下，藉由更強的主機資源與 NGINX 高效能，改善了回應延遲；以 volume container 強化資料持久化與部署一致性；以 NGINX map 取代 Apache RewriteMap，維持大量舊文轉址的可維護性與可讀性。最後，作者以個案經驗鼓勵從 Microsoft 生態跨入 Linux 的開發者，重點在於以實戰需求導向選擇技術與切入點（如 Docker/Reverse Proxy），用能快速產生價值的成果驅動學習，而非深陷於不必要的配置細節。

## 段落重點
### 動機與背景：跨入 Linux/Open Source 與 Docker 的實戰切點
作者因 .NET Core 跨平台和雲端普及的趨勢，意識到熟悉 Linux 與開源方案已是必要技能。過往在 Linux 上安裝配置的痛點在於套件安裝容易、配置難度高且各異，與其深陷設定細節，不如以 Docker 作為切入點，先建立能快速複製的執行環境。初期選擇在 Synology NAS 上運行 Docker，迅速把個人部落格從 BlogEngine.NET 遷至 WordPress，並以 Apache Httpd 作為前端 Reverse Proxy，利用 RewriteMap 承接大量舊文轉址需求。這一階段的目標是以最小學習曲線取得可用成果，逐步將學習重心放在架構層次與部署模式，而非被繁瑣的 Linux 組態綁死，為後續的全面重構鋪路。

### 架構重構：從 NAS 到 Ubuntu Server，反向代理與資料分層
隨容器數量增長，NAS 的硬體限制（Atom CPU、2GB RAM）導致明顯延遲，促使作者將系統遷移至 Ubuntu Server。新主機雖是舊 NB（Pentium P6100 + 4GB），但在 CPU 與記憶體上仍大幅優於 NAS，且筆電的電池等同內建 UPS，兼顧省電與可靠性。新架構延續前端 Reverse Proxy 聚合多個容器服務的策略，同時把繁複的轉址責任集中在代理層，避免污染後端應用。關鍵技術調整包括：1) 以 NGINX 取代 Apache 作為反向代理，解放於 NAS 綁定與取得更佳效能；2) 採用 Docker volume container 管理資料持久化與掛載，實現應用與資料分離、部署可重現。這樣的拓撲不僅與 UML/Deployment Diagram 的設計精神相符，也讓「按圖佈署」真正落地。

### NGINX 轉址實作：map 機制、正規表達式與對照表維護
重構的技術核心在於把 Apache RewriteMap 的 2400 組轉址規則改寫為 NGINX map。做法是用 if 判斷 URI 與正規表達式抓出 slug 片段，指派給變數 $slug；map 區塊則宣告 $slug 與 $slugwpid 的對應，一旦 $slug 被設定，NGINX 便自動查表填入 $slugwpid；最後以 return 301 將請求導向 /?p=$slugwpid 的新格式。此模式將「抽取規則」與「對照表」解耦，規則簡潔、變更成本低。對照表採外部檔案，每行以「key value;」定義新舊對應，支援 # 註解，既易閱讀也利於批次處理，和 Apache 的 TXT RewriteMap 格式非常相近，從舊環境遷移的成本低。值得注意的是，NGINX map 另支援萬用字元與正規表達式，具更高表現力，為未來複雜場景預留擴充空間。

### 成果、效能與心得：取捨與給跨生態開發者的建議
作者推估 NGINX 的 map 因為支援更動態的匹配，可能不若 Apache 可將 Map 預編為二進位 Hash；但在 NGINX 本身高效能、硬體升級、舊文固定規模（約 400 篇）且不再成長的前提下，實測並無明顯效能影響，因而不再進一步進行基準測試。重構後，系統在回應速度、維護性與部署一致性上均有提升：前端代理更輕量、轉址邏輯清楚可維護、資料層分離利於備份與遷移。對於想從 Microsoft 生態跨入 Linux/Open Source 的開發者，作者建議以實戰需求驅動學習，優先挑選能快速產生價值的工具（如 Docker、NGINX Reverse Proxy），用可量化的成果鞏固學習動機；同時把繁複配置責任下沉到容器與基礎元件，將心力集中在架構決策與服務邏輯，才能在跨生態的過程中走得穩且長。

## 資訊整理

### 知識架構圖
1. 前置知識：學習本主題前需要掌握什麼？
- 基礎 Linux 操作與檔案系統觀念
- 網頁伺服器基礎（HTTP、反向代理、虛擬主機）
- Docker 基本概念（容器、映像、Volume）
- 正則表達式與 URL 重寫概念
- 基本網路與部署概念（DNS、Port、UML Deployment Diagram 讀圖）

2. 核心概念：本文的 3-5 個核心概念及其關係
- 反向代理層：以 NGINX 取代 Apache，統一入口處理多容器服務與 URL 轉址
- URL 轉址策略：利用 NGINX map 機制維護大量舊文連結對應（Key-Value 對照表）
- 容器化部署：以 Docker 組合 Web、DB、與 Volume-Container 分離資料
- 遷移架構：從 NAS（Synology + Docker）轉到專用 Ubuntu Server 提升效能與可控性
- 架構思維導向：以部署圖抽象設計，透過容器對應落地實作

3. 技術依賴：相關技術之間的依賴關係
- 硬體/OS：舊 NB（Ubuntu Server）或 NAS → 提供 Docker 執行環境
- Docker：承載 WordPress（Web）、Database、Volume-Container（資料）
- NGINX（前端）：反向代理至後端容器，負責路由、SSL（可擴充）、URL Map 轉址
- URL Map 檔：外部文字檔維護 slug → postId 對應，被 NGINX map 指令引用
- 網域/DNS：指向前端 NGINX 公網 IP（或 NAS/伺服器 IP）

4. 應用場景：適用於哪些實際場景？
- 舊部落格/網站遷移且需大規模舊網址長期有效
- 一機多服務（多容器）共用 80/443 埠的流量聚合
- 想減少在應用端（如 WordPress）實作重寫邏輯，改在邊界層集中治理
- 家用/中小規模自架站點，從 NAS 過渡到輕型伺服器優化效能與維運
- 以文本維護映射表，對 SEO 友善的永久 301 轉址

### 學習路徑建議
1. 入門者路徑：零基礎如何開始？
- 了解反向代理與基本 HTTP 狀態碼（特別是 301）
- 安裝 Docker、啟動簡單的 Web 容器（如 Nginx Hello World）
- 在本機安裝 NGINX，配置最基本的反向代理到單一容器
- 學習簡單正則表達式，嘗試 NGINX rewrite 與 map 的最小示例
- 理解 Volume 與 Bind Mount 基礎，備份與還原資料夾

2. 進階者路徑：已有基礎如何深化？
- 建立多容器（Web、DB）與 Volume-Container 拆分資料的部署
- 將 URL 對照維護改為外部檔案（包含註解與版本控管）
- 規劃 NGINX 的站點分離、Include 結構與環境參數化
- 比較 Apache RewriteMap 與 NGINX map 的差異與性能考量
- 導入監控與日誌輪替，驗證轉址命中率與效能

3. 實戰路徑：如何應用到實際專案？
- 將既有站點的舊 URL（多種格式）清點，產生 slug → postId 對映表
- 在 NGINX 前端實作 map + return 301 的規則，並以外部檔案 include
- 使用 Docker Compose 建立前端（NGINX）+ 後端（WordPress、DB、Volume）拓撲
- 進行灰度遷移（小流量切換），監看 404、301 命中、回應時間
- 撰寫遷移與回滾手冊（資料備份、DNS 切換、容器重建流程）

### 關鍵要點清單
- NGINX 作為反向代理：集中處理多容器流量與入口治理（SSL/路由/轉址）(優先級: 高)
- URL 永久轉址（301）：維護 SEO 與使用者書籤，確保舊連結長期有效 (優先級: 高)
- NGINX map 機制：以 Key-Value 查表自動對應變數，搭配正則抽取 slug (優先級: 高)
- 外部映射檔維護：以文字檔管理大量對照（含註解），便於版本控制與擴充 (優先級: 高)
- Apache RewriteMap vs NGINX map：語法差異、可用性與性能取捨 (優先級: 中)
- 容器分層設計：Web/DB 與資料（Volume-Container）分離，降低耦合 (優先級: 高)
- 從 NAS 遷移到 Ubuntu Server：提升運算與記憶體資源，改善效能 (優先級: 中)
- 單 IP 多服務共用 80/443：以反向代理實現服務聚合與清晰路由 (優先級: 高)
- 正則表達式抽取參數：以 $1/$5 等群組取得 slug 等路由參數 (優先級: 中)
- 配置結構化：使用 include 拆分 NGINX 設定，提升可維護性 (優先級: 中)
- 部署圖思維：用 UML 部署圖規劃，容器化使設計與實作對齊 (優先級: 低)
- 效能與擴充考量：Nginx 本身高效，映射量適中可不必過度最佳化 (優先級: 中)
- 災難復原與回滾：Volume 備份、容器重建、DNS 切換預案 (優先級: 高)
- 本機快速驗證：可用 Windows 版 NGINX 測設定與規則後再上線 (優先級: 低)
- 漸進式遷移策略：先行小規模導流監測 404/301 命中，再全面切換 (優先級: 中)