---
layout: synthesis
title: "CaseStudy: 網站重構, NGINX (REVERSE PROXY) + 文章連結轉址 (Map)"
synthesis_type: faq
source_post: /2015/12/04/casestudy-nginx-as-reverseproxy/
redirect_from:
  - /2015/12/04/casestudy-nginx-as-reverseproxy/faq/
postid: 2015-12-04-casestudy-nginx-as-reverseproxy
---

# CaseStudy: 網站重構, NGINX (REVERSE PROXY) + 文章連結轉址 (Map)

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 Reverse Proxy（反向代理）？
- A簡: 位於用戶與後端之間的代理層，統一對外入口，轉發請求、進行路由、轉址、緩存與安全強化。
- A詳: 反向代理是部署在客戶端與後端應用之間的中介層。它接收外部請求，依據路徑或主機名路由到對應的後端服務，並可於此層執行 SSL 終結、URL 轉址/重寫、快取、壓縮與存取控制。本案例用於將多個 Docker 容器（WordPress、其他服務）透過單一 IP/Port 對外提供，並將大量舊網址轉址集中處理，減輕後端應用負擔。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q3, B-Q1, C-Q1

A-Q2: 為什麼本案例需要 Reverse Proxy？
- A簡: 多容器共享單一 80 埠，集中管理路由與大量舊連結轉址，避免將複雜度推給 WordPress。
- A詳: 同一台主機上跑多個 Docker 容器時，需以單一對外入口承載多個後端網站/服務。反向代理可依路徑或主機名分流請求，並集中實作 301 轉址與 Rewrite Map，避免在 WordPress 內部混入複雜規則，維持清楚的關注點分離。也提升維運彈性，讓後端應用可獨立調整、升級與替換。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q8, B-Q12, C-Q7

A-Q3: 什麼是 NGINX？為何選擇它？
- A簡: 高效能、事件驅動的 Web/反向代理伺服器，設定簡潔，擅長高併發與靜態資源服務。
- A詳: NGINX 是以事件驅動架構設計的 Web 伺服器/反向代理。相較 Apache 的進程/執行緒模型，NGINX 以非阻塞 I/O 與少量工作進程處理大量連線，對高併發負載表現優異。其設定語法簡潔，具 map、rewrite、include 等功能，適合集中管理轉址與多後端路由。本案例在 Ubuntu Server 上以 NGINX 取代受 NAS 限制的 Apache 前端。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, B-Q6, C-Q1

A-Q4: NGINX 與 Apache 有何差異？
- A簡: 架構不同；Nginx 事件驅動、設定精簡；Apache 模組豐富、歷史悠久；效能與資源使用各有優劣。
- A詳: Apache 以進程/執行緒處理請求，模組生態完整；NGINX 以事件驅動與非阻塞 I/O 取得更佳併發與記憶體效率。重寫/轉址：Apache 用 mod_rewrite/RewriteMap，NGINX 用 rewrite/return 與 map。設定風格：NGINX 更簡潔，常被用作前端反向代理；Apache 在動態模組與 .htaccess 有優勢。選擇取決於場景與運維習慣。
- 難度: 中級
- 學習階段: 基礎
- 關聯概念: B-Q6, B-Q22, C-Q3

A-Q5: 什麼是 URL 重寫與 301 轉址？
- A簡: 重寫為內部改寫路徑；301 為永久轉址，回應新位置給瀏覽器/搜尋引擎並可被快取。
- A詳: URL 重寫（rewrite）在伺服器內部改寫請求路徑，對用戶不可見，用於框架路由或靜態化。301 轉址（永久移動）則回傳狀態碼與 Location，新位置由瀏覽器重新請求，搜尋引擎會更新索引並傳遞權重。本案例將舊部落格連結以 301 指向新 WordPress 連結，兼顧 SEO 與使用者體驗。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, B-Q17, A-Q17

A-Q6: 什麼是 NGINX 的 map 指令？
- A簡: 依輸入變數值查表並產生對應輸出變數，用於高效映射與轉址決策。
- A詳: map 定義在 http 區塊，語法為 map $key $val { ... }。當請求期評估 $key 值時，NGINX 依定義的表格（靜態鍵值、萬用字元、正則）賦值給 $val。可 include 外部檔管理大量對照。於案例中，將解析出的 slug 以 map 查得對應 WordPress 文章 ID，配合 return 301 產生新 URL。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q7, C-Q2

A-Q7: 什麼是 slug 與 slugwpid 對映？
- A簡: slug 為舊文網址中的標題片段；slugwpid 為 map 查得的 WordPress 文章 ID。
- A詳: 舊系統 BlogEngine.NET 的文章網址包含以編碼標題形成的 slug。新系統 WordPress 內部識別則以文章 ID（?p=ID）為主。透過正則擷取舊網址中的 slug，將其作為 map 鍵查表，得到對應的 WordPress 文章 ID（slugwpid），再以 301 導向新位置，確保所有舊鏈結正確落點。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q3, C-Q2

A-Q8: 為何將轉址邏輯放在反向代理而非 WordPress？
- A簡: 降低後端負擔、統一規則管理、與應用解耦，提升維運與效能。
- A詳: 反向代理層執行轉址可：1) 將大量正則與表格查找從應用程式移除，節省 PHP/應用資源；2) 規則集中於 NGINX，可用 include 管理、版本控管、熱更新；3) 將 URL 治理與內容渲染分離，後端升級與擴展更安全。本案例採此策略以處理 2400 組轉址組合。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q15, C-Q1, C-Q2

A-Q9: 什麼是 Docker？
- A簡: 容器化平台，封裝應用與相依，跨環境一致部署，啟動快速、資源效率高。
- A詳: Docker 以 Linux 容器技術隔離應用與環境，將程式、設定與依賴打包成映像檔，運行為容器。相較傳統 VM，容器更輕量、啟動快，利於微服務與持續交付。本案例用 Docker 執行 WordPress/MySQL，前端以 NGINX 匯聚流量，並採用資料卷（Volume）隔離持久資料。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, B-Q13, C-Q6

A-Q10: 什麼是 Docker Volume 與 Volume-Container？
- A簡: Volume 為持久化存放區；Volume-Container 專責掛載並供其他容器共用資料。
- A詳: Volume 將資料獨立於容器生命週期之外，避免容器刪除導致資料遺失。Volume-Container 是只掛載資料卷、幾乎不執行應用的容器，其他容器以 --volumes-from 共用，此設計提升資料管理、一致性與備份便利。本案例將 Web 與 DB 資料分離至 Volume-Container，符合官方建議。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q13, C-Q6

A-Q11: NAS 與專屬伺服器（NB/Ubuntu）有何差異？
- A簡: NAS 便捷但硬體受限；專屬伺服器可調整性與效能高，適合承載多容器與高併發。
- A詳: NAS 內建服務豐富、易用，但 CPU/RAM 較弱、前置服務占用 Port（如內建 Apache），限制自由度。專屬伺服器（如舊 NB + Ubuntu）可完全掌控套件、網路與服務，具更佳運算資源與效能。本案例因 NAS 併發瓶頸與 Port 限制，遷移至 Ubuntu 取得更高彈性與效能。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, B-Q14, C-Q10

A-Q12: 為何從 Synology NAS 轉到 Ubuntu Server？
- A簡: 解決效能瓶頸與前端綁定限制，改用 NGINX 反向代理與更彈性佈署。
- A詳: Synology 412+（Atom + 2GB）在多容器情境下回應變慢，且內建 Apache 占用 80 埠不易更換。遷移至 Ubuntu Server 可自由安裝與設定 NGINX、Docker 網路與卷，消除硬體與軟體束縛，並透過 Volume-Container 與反向代理優化整體架構與維運。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, C-Q1, C-Q10

A-Q13: 什麼是部署圖（Deployment Diagram）？與容器化有何關聯？
- A簡: 描述軟硬體節點與元件部署關係；容器使圖上設計與實作更一致。
- A詳: 部署圖刻劃節點（伺服器、網路）與軟體元件（服務、資料庫）的配置與連線。過去實作與圖示差距大，細節繁雜。容器技術讓元件封裝與連線更「模組化」，可依圖配置服務、網路與卷，實作與設計一致性更高，維護與擴展更直觀。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q27, C-Q7, C-Q10

A-Q14: 什麼是 WordPress 的 /?p=ID 連結？
- A簡: WordPress 以文章 ID 作為內部查詢鍵，/?p=ID 導向對應文章頁面。
- A詳: WordPress 文章默認有唯一 ID，/?p=ID 是其核心查詢參數格式。即使使用自訂永久連結，/?p=ID 仍能正確定位文章。本案例以 map 將舊 slug 對映到 WordPress 文章 ID，並用 return 301 導向 /?p=ID 確保正確落點與簡化轉址實作。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, B-Q20, C-Q2

A-Q15: 什麼是正規表達式擷取群組（$1..$n）在 NGINX？
- A簡: 以括號捕捉匹配片段，於後續變數（$1...）引用，用於重寫與轉址。
- A詳: 在 NGINX 的 if、location 或 rewrite 判斷中，正則以括號()將匹配片段捕捉，對應變數 $1、$2...。本案例以 if 比對 $uri，將第 5 群組（$5）擷取為 slug，後續用於 map 查表與轉址。正確擷取能簡化規則與避免重複計算。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, C-Q2, D-Q2

A-Q16: 什麼是 NGINX return 指令？與 rewrite 有何差異？
- A簡: return 直接回應狀態碼與內容/位置；rewrite 進行內部或外部改寫，流程更複雜。
- A詳: return 更直截了當，適合純轉址（301/302）或回應固定內容；rewrite 支援條件判斷與內部重寫，可鏈式處理但成本與複雜度較高。對單純舊連結轉到新連結，建議使用 return 301，清楚、效能好，且避免多次內部跳轉。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q22, C-Q2

A-Q17: 301 與 302 轉址差異與 SEO 影響？
- A簡: 301 永久移動並傳遞權重；302 臨時移動不傳遞。遷站/改網址宜用 301。
- A詳: 301 告知資源永久移動，搜尋引擎更新索引並將權重轉移到新網址；瀏覽器可能長期快取。302 表示暫時移動，原網址仍保留權重，適合短期 A/B 或維護導流。本案例屬永久遷移舊鏈結，選用 301 才能維護 SEO 與用戶體驗。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, B-Q17, D-Q9

A-Q18: 什麼是 NGINX for Windows？可做什麼？
- A簡: Windows 平台的 NGINX 版本，適合本機快速測試與驗證設定，不建議重載生產。
- A詳: 官方提供 Windows 版 NGINX，便於在熟悉的環境快速驗證配置、正則與 map 表格，不必先搭建 Linux。但其 I/O 與效能不及 Linux 版，且在高併發與模組支援上有限，建議僅用於開發/測試，正式環境仍以 Linux 版為佳。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q5, D-Q8

A-Q19: 什麼是 include maps/slugmap.txt 外部對照表？
- A簡: 將大量鍵值對映獨立存檔，以 include 引用，利於維護與版本控管。
- A詳: 大量映射（如 400+ 篇文章）若直接寫在主配置，維護困難。將 key/value 一行一筆，置於外部檔（支援註解 #），於 map 區塊 include 引用，可簡化規則並支援熱更新。此做法也可共用於多 server 區塊或環境。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, C-Q4, D-Q4

A-Q20: 什麼是「單一 IP + 80 port 發布多個服務」？
- A簡: 透過反向代理在同一入口做主機名/路徑分流，將請求分派到不同後端容器。
- A詳: 一台機器通常只有少數對外端口。以 NGINX 匯聚所有 HTTP 請求，根據 Host（多網域）或 URI 路徑（單網域多應用）路由到對應容器。這能充分利用單一 IP 與 80/443 入口，同時對外提供多個服務。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q12, C-Q7

A-Q21: .NET Core 跨平台與 Linux 有何關聯？
- A簡: .NET Core 支援 Linux，開發者需理解 Linux 部署與運維以落地跨平台。
- A詳: 隨 .NET Core 跨至 Linux/容器，ASP.NET 應用可運行在 NGINX 反向代理與 Kestrel 組合上。理解 Linux 套件管理、檔案系統、服務管理與網路，能讓原本在 Windows 的程式順利搬遷並最佳化部署。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q28, C-Q1

A-Q22: 為何大型部署偏好 Linux + 開源方案？
- A簡: 穩定、高效、成本與生態優勢，且便於自動化、容器化與彈性擴展。
- A詳: Linux 在伺服器場域具備穩定與高性能記錄，開源軟體（如 NGINX、Docker）生態繁盛、可觀成本效益並易於自動化與基礎設施即程式化（IaC）。在雲端環境更能發揮彈性與可移植性，符合現代服務的可擴展需求。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q21, B-Q28

### Q&A 類別 B: 技術原理類

B-Q1: NGINX 作為反向代理如何運作？
- A簡: 接收請求→匹配 server/location→應用規則→proxy_pass 到後端→回傳響應。
- A詳: 請求進入 NGINX 後，依 Host 與端口匹配到 server，再以 URI 匹配 location。過程中可評估變數與 map、執行重寫或 return。若需轉發則由 proxy_pass 與 upstream 傳遞至後端容器，維持必要標頭（Host、X-Forwarded-*）。回應返回時可經過壓縮、快取與標頭調整後送回用戶。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q1, A-Q3, C-Q1

B-Q2: NGINX map 變數綁定機制是什麼？
- A簡: 以輸入變數值動態查表，將結果賦值至輸出變數，於請求期延遲求值。
- A詳: map 在 http 階段建好查表規則，於請求處理時當輸入變數（如 $slug）首次被使用或更新時，才將匹配規則求值並賦值至輸出變數（如 $slugwpid）。支持字面量、萬用字元（hostnames）與正則規則，並可 include 外部檔。未命中時可使用 default 或自訂預設值。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q7, B-Q8

B-Q3: $slug 與 $slugwpid 在案例中的執行流程？
- A簡: if 正則擷取 slug→set $slug→map 查表→得到 $slugwpid→return 301 新連結。
- A詳: 先以 if 對 $uri 做正則匹配，將第 5 擷取群組（文章 slug）以 set 指派給 $slug。map 已預先定義 $slug→$slugwpid 的對映（外部檔 include）。當 $slug 賦值後，map 即時查表，得出對應 ID 存入 $slugwpid。最後用 return 301 導向 /?p=$slugwpid 完成永久轉址。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, C-Q2, D-Q1

B-Q4: NGINX 的配置結構與核心組件？
- A簡: 分為全域、events、http（含 server/location）、stream 等層級與模組。
- A詳: NGINX 配置頂層為全域與 events（連線/工作程序），HTTP 協定相關在 http 區塊，下含 server（虛擬主機）與 location（路由）。反向代理、重寫、map、gzip、快取等皆為 http 模組設定。理解層級有助於正確放置指令與控制作用範圍。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q1, C-Q2

B-Q5: 為何用 return 301 做轉址？流程與特性？
- A簡: 單指令直接回應，耗資源少，避免多重內部跳轉，適合純轉址場景。
- A詳: return 在匹配到條件後立即回應狀態碼與 Location，不再進入後續處理流程。對大量且固定的舊→新網址映射，return 301 更清晰與高效，減少 rewrite 內部改寫與再解析的成本，也降低配置錯誤導致的跳轉迴圈機率。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, A-Q17, C-Q2

B-Q6: NGINX 與 Apache 的請求處理模型差異？
- A簡: NGINX 事件驅動、非阻塞；Apache 多為進程/執行緒模型，資源用量較高。
- A詳: NGINX 以 epoll/kqueue 等事件迴圈處理大量連線，少量工作進程即可承載高併發，記憶體與 context switch 成本低。Apache 則依 MPM 運行（prefork/worker/event），傳統模式對高併發較吃資源。對反向代理與靜態檔案場景，NGINX 更具優勢。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, C-Q1

B-Q7: map 檔解析與 include 機制如何運作？
- A簡: 啟動/重載時讀取 include 檔，編譯匹配規則，請求期按需查表賦值。
- A詳: NGINX 啟動或 reload 會解析配置並讀入 include 的外部 map 檔，將字面量、萬用字元與正則規則建構為查找結構。請求期當輸入變數被更新或使用時才進行查表，原生支援註解與基本格式檢查。路徑需正確且權限允許讀取。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q19, D-Q4

B-Q8: map 的預設值與未命中策略？
- A簡: 可用 default 指定未命中值；亦可自訂匹配規則順序以覆蓋。
- A詳: 若輸入值未匹配任何條目，建議在 map 內使用 default <value> 設定預設輸出，避免空值造成後續錯誤。本案例可將 default 設為 0 或空白並在邏輯中處理。部分寫法會用萬用字元條目，惟建議以 default 更直觀且跨版本兼容。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q1, D-Q2

B-Q9: 大量映射的效能考量與調優？
- A簡: 控制 map hash 桶大小與最大值，避免衝突；精簡正則，優先用字面量鍵。
- A詳: 對大量鍵值對映，優先用字面量以便 hash 加速；減少正則條目數。可調整 map_hash_bucket_size 與 map_hash_max_size，以降低碰撞與提高查找性能。將映射拆分成多個 map 或依前綴分區亦有效。監看 reload 與錯誤日誌確認 hash 佈局提示。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: C-Q2, D-Q5

B-Q10: 在 if 中用正則 set 變數的評估順序與風險？
- A簡: if 適用於簡單條件；複雜邏輯應以 map/location；避免誤用導致不可預期行為。
- A詳: NGINX 的 if 在不同上下文有特殊語義，建議僅用於變數賦值與 return 等簡單操作。複雜重寫應在 server/location 或以 map 前置計算。錯誤的 if 可能導致條件短路或與其他指令交互不當，建議遵循官方 If Is Evil 指南。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: D-Q2, C-Q2

B-Q11: 正則比對與擷取群組在 NGINX 的原理？
- A簡: 基於 PCRE/Oniguruma（視版本）解析，匹配後輸出 $1..$n 供後續引用。
- A詳: NGINX 內建正則引擎支援常見語法，於 if/location/rewrite 進行匹配時，括號群組會依序賦值到 $1...變數。匹配成本與規則複雜度相關，需避免過度回溯與貪婪匹配；適時使用非貪婪或明確字元類別以提效。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, D-Q2

B-Q12: 多容器共用單一入口的路由策略？
- A簡: 以 Host 為主機名路由或以路徑前綴分流，結合 upstream 定義後端群組。
- A詳: 多域名站點用 server_name 區分；單域多應用以 location /app1、/app2 分流。後端定義 upstream 並以 proxy_pass 指向。需維護原始 Host 與 X-Forwarded-*，確保應用端感知真實協定與客戶端地址。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q20, C-Q7

B-Q13: Docker Volume-Container 的設計理念與資料流？
- A簡: 將持久資料抽離應用容器，以共享卷掛載實現解耦與獨立備份。
- A詳: Volume-Container 僅負責掛載與提供資料卷，應用容器以 --volumes-from 共用相同卷。資料實際存在宿主或專用卷驅動，應用容器銷毀重建不影響資料。此模式支援單機多容器場景的資料一致與生命週期管理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, C-Q6

B-Q14: NAS 硬體瓶頸如何影響容器效能？
- A簡: CPU 與 RAM 限制導致併發處理與 IO 受阻，多容器時延遲顯著上升。
- A詳: NAS 常見低功耗 CPU 與有限記憶體，在多容器並行（Web、DB、反向代理）下造成排隊、換頁與 IO 爭用。網路與儲存性能也可能限制響應時間。本案例多開容器後明顯變慢，反向代理與 DB 均受影響，遷移至更強硬體可解決。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, D-Q10

B-Q15: 轉址邏輯外移的架構優勢？
- A簡: 關注點分離、部署解耦、規則集中化、可熱更新與可觀測性提升。
- A詳: 在反向代理實作轉址與重寫可統一治理 URL，減少應用侵入。結合 include 與 map，規則可版本控管並於 reload 生效。存取/錯誤日誌在同層集中，利於觀測與排障。後端應用可專注業務邏輯。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, C-Q2

B-Q16: NGINX Windows 與 Linux 版本差異？
- A簡: Linux 版性能與生態較佳；Windows 版適合測試，生產不建議。
- A詳: Linux 版靠高效事件機制（epoll/kqueue）與成熟模組提供最佳性能與穩定性；Windows 版在 IO 模型、檔案鎖與計時器上有差异，吞吐與延遲較差。路徑分隔與權限模型不同，配置需調整。建議只在 Windows 做配置驗證。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q18, D-Q8

B-Q17: 301 轉址的快取與搜尋引擎處理機制？
- A簡: 瀏覽器與搜尋引擎皆可長期快取 301；權重轉移至新網址需時間。
- A詳: 瀏覽器常記憶 301 導致日後自動跳轉；搜尋引擎在爬取與評估後逐步將舊索引與權重轉移到新址。測試時可暫用 302 或清快取。大規模遷站宜維持穩定且一致的 301 規則，避免震盪。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q17, D-Q9

B-Q18: NGINX 配置熱載入原理？
- A簡: 發送 reload 訊號，主進程驗證新配置，平滑替換工作進程，無需中斷。
- A詳: 執行 nginx -t 驗證後，以 nginx -s reload 或 systemctl reload 讓主進程讀入新配置，若語法正確則啟動新工作進程並優雅關閉舊進程中的連線。確保無損切換，設定生效即刻可觀測。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q8, D-Q7

B-Q19: 反向代理標頭傳遞（Host、X-Forwarded-*）原理？
- A簡: 保留原始主機名與協定/來源 IP，供後端正確生成 URL 與記錄。
- A詳: proxy_set_header Host $host 保持主機名；X-Forwarded-Proto 告知原協定（http/https）；X-Forwarded-For 附加客戶端 IP。後端（如 WordPress）依此決定產生的絕對 URL、跳轉協定與日誌來源，避免錯誤鏈結或重定向迴圈。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q6, C-Q1

B-Q20: slug→ID 的設計取捨（固定映射 vs 查 DB）？
- A簡: 固定對照表查找快且穩定；DB 查詢彈性高但每請求成本高。
- A詳: 將 slug→ID 固化於 map 檔能以 O(1) 方式查找，效能高且便於版本控管；若以應用層查 DB，雖彈性佳但增加每次請求延遲與後端負載。本案例選擇 map 檔以滿足高效且穩定的遷移需求。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, A-Q14, C-Q2

B-Q21: map 中正則與萬用字元的優先順序？
- A簡: 精確字面量優先於萬用與正則；正則用於最後手段避免覆蓋過廣。
- A詳: NGINX 先匹配字面量鍵，再處理萬用字元（需 hostnames）與正則；正則規則成本高且難維護。建議：大多數條目用字面量，僅用少量正則處理特殊模式，並確保順序與覆蓋範圍正確。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q9, C-Q3

B-Q22: return 與 rewrite 的機制差異與適用性？
- A簡: return 直接回應更高效；rewrite 適合內部改寫或需複雜條件的情境。
- A詳: return 省去重寫與再解析成本，僅需回傳狀態碼與目標，適合大量固定轉址。rewrite 可鏈式處理、支援標誌（last、break、redirect），適用於複雜內部路由或多階段轉換。根據目標選擇最簡指令。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, B-Q5

B-Q23: 2400 組轉址如何抽象化與簡化？
- A簡: 以正則抽取關鍵鍵（slug）統一化，再用單一 map 檔集中對映。
- A詳: 舊系統有 6 種網址格式，若逐條列規則會暴增。透過正則擷取共同核心——文章 slug，將多樣網址歸一化為鍵，再於 map 以 slug→ID 對映。如此只需維護一份對照表即可涵蓋所有變體。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, C-Q2

B-Q24: 日誌在除錯重寫/轉址中的作用？
- A簡: 存取與錯誤日誌顯示匹配、變數值與錯誤行，有助快速定位問題。
- A詳: 啟用較高等級 error_log 或 debug，可觀察正則匹配結果與變數賦值；access_log 可驗證狀態碼（301/302）與 Location。結合 map 與 if 的問題常藉由日誌快速定位未命中或路徑不符。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q2, D-Q7

B-Q25: 對照表外部化的工程效益？
- A簡: 版本控管、權限隔離、熱更新與多環境共享，降低風險。
- A詳: 將映射從主配置剝離，git 追蹤更易審核與回滾；權限可僅賦予讀取；更新映射不需改動核心配置；不同站點可共享同一份對照檔。這些皆提升維運品質與可追溯性。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q19, C-Q4

B-Q26: 單機多容器的網路與安全原理？
- A簡: 以 bridge 網路隔離容器，僅對外暴露 NGINX 入口，減少攻擊面。
- A詳: Docker 預設 bridge 網路提供容器間隔離與 DNS 解析。僅 NGINX 映射對外端口，其他後端容器僅在內網可達，強化安全。亦可用 user-defined network 管理服務間通訊與別名。必要時加上防火牆規則。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q7, D-Q6

B-Q27: 用部署圖思維落實到容器對映？
- A簡: 將每個元件對應為容器，網路為虛擬網路，資料為卷，布線即代理路由。
- A詳: 部署圖中的節點→宿主機，構件→容器，連線→proxy_pass/網路連接，儲存→Volume。這種一一對映讓設計與落地一致，便於討論、審核與自動化生成（如 Compose）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, C-Q1

B-Q28: 為何選 Ubuntu Server 作宿主？
- A簡: 套件生態成熟、文件豐富、與 Docker/NGINX 相容最佳，維運社群活躍。
- A詳: Ubuntu LTS 提供穩定與長期維護，apt 生態完整，與 Docker、NGINX、監控工具整合順暢。文件/社群資源多，有利於快速排障與持續更新，適合作為自架主機宿主 OS。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, C-Q1

B-Q29: 用 NB 當伺服器之電力/可靠性機制？
- A簡: 低功耗，內建電池可充當簡易 UPS，斷電時提供短時保護。
- A詳: 舊 NB 維持個人站台足夠，省電且安靜。電池在市電掉電時可短期供電，避免瞬斷導致資料損壞，配合自動關機腳本可進一步保護。不過長期可靠性與散熱需留意。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, D-Q10

B-Q30: 何時在 map 用正則、何時交給應用？
- A簡: 常規鍵值優先 map；複雜語意或需查庫時交由應用以維持可控性。
- A詳: map 的正則適合少量模式化規則；一旦條件複雜、多層判斷或需業務資料，應在應用層處理，以避免 NGINX 配置膨脹與可觀測性下降。維持簡單明確的 map 有助於性能與維護。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q21, A-Q8

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何在 Ubuntu 以 NGINX 建立反向代理到 Docker WordPress？
- A簡: 建立 WordPress/MySQL 容器，配置 NGINX server/location 與 proxy_pass，設定標頭與超時。
- A詳: 
  - 步驟：安裝 Docker/NGINX；啟動 MySQL、WordPress 容器；建立 bridge 網路；撰寫 NGINX server 區塊與 location / 指向 WordPress。
  - 範例： 
    server_name blog.example.com;
    location / {
      proxy_set_header Host $host;
      proxy_set_header X-Forwarded-Proto $scheme;
      proxy_pass http://wordpress:80;
    }
  - 注意：容器使用同一自訂網路；開啟 gzip/快取視需要；nginx -t 後 reload。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q19

C-Q2: 如何用 NGINX map 實作 slug→ID 的 301 轉址？
- A簡: 正則擷取 slug→set 變數→map 查得 ID→return 301 指向 /?p=ID，對照表外部化。
- A詳: 
  - 步驟：在 http 區塊定義 map 並 include 檔；在 server 中以 if 正則擷取 slug；return 301。
  - 範例：
    map $slug $slugwpid { include maps/slugmap.txt; default 0; }
    if ($uri ~* ^(/columns)?/post(?:/\d+){3}/(.*)\.aspx$) { set $slug $2; return 301 /?p=$slugwpid; }
  - 注意：default 指定未命中；測試前先以 302 驗證；nginx -t 與日誌檢查。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q3, B-Q8

C-Q3: 如何把 Apache RewriteMap 轉成 NGINX map？
- A簡: 將 key value 以空白分隔、一行一筆，去除 Apache 語法與結尾，改用 include 引入。
- A詳: 
  - 步驟：整理原 TXT，把 key/value 留下，以空白分隔，行尾加分號；保留 # 註解。
  - 範例（maps/slugmap.txt）：
    GoodProgrammer1 65;
    IBM-ThinkPad-X111- 252;
  - 注意：Nginx 支援 default，而非依賴萬用；確保編碼與無 BOM；大量條目時考慮 hash 參數調整。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q21, D-Q4

C-Q4: 如何外部化對照表並 include？
- A簡: 新建 maps/slugmap.txt，放 key value 與註解，map 區塊以 include 引用並設 default。
- A詳: 
  - 步驟：建立目錄與檔案；寫入鍵值與分號；在 http 區塊 map 中 include；權限設定為 nginx 可讀。
  - 片段：
    map $slug $slugwpid {
      include /etc/nginx/maps/slugmap.txt;
      default 0;
    }
  - 注意：路徑用絕對；權限 0644；更新後 reload；版本控管該檔案。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q19, B-Q25

C-Q5: 如何在 Windows 快速測試 NGINX 設定？
- A簡: 下載 Windows 版 Nginx，放置配置與 map 檔，啟動驗證正則與轉址行為。
- A詳: 
  - 步驟：下載 zip、解壓；在 conf 中加入 server/map；maps 目錄放對照檔；cmd 啟動 nginx.exe。
  - 測試：用 curl -I 檢查 301 與 Location；修改配置後 nginx -s reload。
  - 注意：Windows 僅供測試；路徑分隔為反斜線，確保權限與編碼一致。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q18, B-Q16

C-Q6: 如何建置 WordPress/MySQL 的 Volume-Container 佈署？
- A簡: 建立資料卷容器，MySQL/WordPress 以 --volumes-from 共用，確保資料持久化。
- A詳: 
  - 步驟：
    docker create -v /var/lib/mysql --name dbdata mysql:8
    docker run -d --name mysql --volumes-from dbdata -e MYSQL_ROOT_PASSWORD=... mysql:8
    docker create -v /var/www/html --name wpdata wordpress:php8.2-apache
    docker run -d --name wp --volumes-from wpdata --link mysql:mysql wordpress:php8.2-apache
  - 注意：改用同網路；定期備份卷；版本與時區設定妥當。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q13

C-Q7: 如何以同一主機發佈多個容器服務（路徑分流）？
- A簡: 使用多個 location 前綴分流到不同 upstream，保留 Host 與協定標頭。
- A詳: 
  - 片段：
    upstream wp { server wp:80; }
    upstream redmine { server redmine:3000; }
    location /blog/ { proxy_pass http://wp/; }
    location /pm/ { proxy_pass http://redmine/; }
    proxy_set_header Host $host; proxy_set_header X-Forwarded-Proto $scheme;
  - 注意：正確處理尾斜線；必要時子路徑重寫；靜態資源快取策略分開。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, B-Q26

C-Q8: 如何安全測試與套用 NGINX 設定變更？
- A簡: 先 nginx -t 驗證，再 reload；灰度用 302 測試轉址，確認後改 301。
- A詳: 
  - 步驟：編輯配置→nginx -t→systemctl reload nginx；觀察 error_log、access_log。
  - 測試：先以 302 驗證行為與無迴圈；確認後改 301；設置短 TTL 的 DNS 方便切換。
  - 注意：版本控管配置；回滾計畫；在低峰時段套用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q18, B-Q17, D-Q7

C-Q9: 如何評估新架構效能？
- A簡: 使用 wrk/ab 壓測、docker stats/top 觀察資源、Nginx/應用日誌分析延遲。
- A詳: 
  - 步驟：以 wrk -t4 -c100 -d30s http://site/ 壓測；記錄 QPS/延遲；同時監控 CPU/RAM/IO。
  - 指標：Nginx 499/timeout、後端 5xx、平均/尾延遲。
  - 注意：逐步增加併發；分離網頁/靜態測試；調整 keepalive、worker_processes 與 map hash。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q9, D-Q10

C-Q10: 如何在 NAS→Ubuntu 遷移時降停機？
- A簡: 預先同步資料、雙機並行、切換 DNS（短 TTL）、完成後回收舊環境。
- A詳: 
  - 步驟：建立新環境並導入資料卷備份；於測試網域驗證；調低 DNS TTL（例如 300s）；排程切換時間；更新 DNS 指向新 IP；監控 24–48 小時；確認後關閉舊系統。
  - 注意：301 規則一致；備份回滾預案；同步最後增量資料。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q27

### Q&A 類別 D: 問題解決類（10題）

D-Q1: 遇到 $slugwpid 總是空白怎麼辦？
- A簡: 檢查 map default、對照檔鍵是否存在、$slug 是否被正確 set 與評估時機。
- A詳: 
  - 症狀：return 301 指向 /?p=（空）或未轉址。
  - 可能原因：map 未命中（缺條目/鍵不符）、未設 default、$slug 未賦值或變數名拼錯。
  - 解法：用 error_log 調高等級；在 return 前加 log 變數；檢查 map include 路徑與權限；加 default 0 或保底邏輯。
  - 預防：建立校驗腳本檢測鍵存在；PR 流程審核對照檔。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, B-Q24

D-Q2: 正則抓不到 $5 導致不轉址怎麼診斷？
- A簡: 確認樣式與實際 URI 符合、群組序號正確、避免貪婪匹配與路徑變體。
- A詳: 
  - 症狀：if 不觸發或 $slug 空。
  - 原因：樣式不匹配（多/少斜線、大小寫）、括號群組位置錯誤、.aspx 結尾不一致。
  - 解法：用 location ~* 測試；改用非貪婪 (.*?)；打印 $uri；用測試工具驗證正則。
  - 預防：以單元化樣本集回歸測試正則；將關鍵擷取改為 map 正則。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, B-Q11

D-Q3: 出現 301 轉址迴圈怎麼辦？
- A簡: 確認目標 URL 不再觸發相同規則，使用排除條件或拆分 server/location。
- A詳: 
  - 症狀：瀏覽器或 curl 顯示多次 301/302，最終失敗。
  - 原因：新 URL 又被相同條件匹配；proxy_redirect/應用層也重定向。
  - 解法：在規則加入條件排除（如不匹配 /?p=），或拆分 location；關閉不必要 rewrite；檢查應用層設定。
  - 預防：先以 302 測試；加入防護計數與日誌觀察。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q8

D-Q4: include 的對照檔讀不到怎麼辦？
- A簡: 確認路徑正確、權限允許、語法正確且無 BOM；nginx -t 驗證。
- A詳: 
  - 症狀：reload 失敗或 map 空值。
  - 原因：路徑錯誤、檔案權限不足、行尾分號缺失、BOM/編碼問題。
  - 解法：用絕對路徑；chown/chmod 調整；去除 BOM；nginx -t 找行號。
  - 預防：CI 中加入語法檢查；統一 UTF-8 無 BOM。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, C-Q4

D-Q5: 大型 map 導致延遲怎麼優化？
- A簡: 優先字面量鍵、減少正則、調整 map_hash_*、拆分映射、預熱測試。
- A詳: 
  - 症狀：高併發下 P95 延遲上升。
  - 原因：hash 衝突、正則過多或順序不當。
  - 解法：調 map_hash_bucket_size/max_size；把熱鍵前置；正則改字面量；拆多 map；觀察啟動日誌提示。
  - 預防：壓測前評估；持續監測與容量規劃。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q9, C-Q9

D-Q6: 反向代理後 WordPress 產生錯誤網址或重複跳轉？
- A簡: 設定 X-Forwarded-Proto/Host，修正 site_url/home，避免協定/主機錯亂。
- A詳: 
  - 症狀：跳回 http、URL 不含子路徑或 302 來回。
  - 原因：後端誤判協定與主機名；未讀取代理標頭。
  - 解法：proxy_set_header Host/$scheme；wp-config 設定 $_SERVER['HTTPS'] 或 WP_HOME/WP_SITEURL；必要時用插件處理代理。
  - 預防：部署前確認標頭；固定絕對 URL 策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q19, C-Q1

D-Q7: NGINX reload 失敗該怎麼排查？
- A簡: 先 nginx -t 取得行號與原因，修正語法或檔案路徑，重試 reload。
- A詳: 
  - 症狀：systemctl reload 回傳失敗。
  - 原因：語法錯誤、include 檔缺失、權限不足。
  - 解法：nginx -t；根據錯誤行修正；確認使用者/群組與 SELinux/AppArmor；必要時回滾上一版。
  - 預防：在 CI 做語法驗證；變更小步快跑。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q18, C-Q8

D-Q8: 在 Windows 測通過，Linux 上失敗怎麼辦？
- A簡: 檢查路徑分隔、大小寫敏感、編碼/BOM、權限與模組差異。
- A詳: 
  - 症狀：相同配置行為不同。
  - 原因：Linux 大小寫敏感；路徑不同；Windows 行尾 CRLF/BOM；I/O 差異。
  - 解法：轉換行尾 LF、移除 BOM、用絕對路徑、校正大小寫；依 Linux 環境重新驗證。
  - 預防：以容器化開發環境接近生產；自動化檢查。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q18, B-Q16

D-Q9: 瀏覽器快取舊 301 導致測試不準怎麼處理？
- A簡: 清快取、改用 302 暫測、換不同瀏覽器/加隨機參數，或調整 Cache-Control。
- A詳: 
  - 症狀：配置更改後仍跳轉到舊目標。
  - 原因：瀏覽器本地快取 301。
  - 解法：清除快取；暫用 302 驗證；加上 no-store/短 max-age；換 UA 測試；curl -I 直接觀察頭。
  - 預防：上線前先 302 小流量驗證；公告切換窗口。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q17, B-Q17, C-Q8

D-Q10: 多開容器後反應變慢如何診斷？
- A簡: 檢查 CPU/RAM/IO、容器限額、資料庫瓶頸與網路，必要時升級硬體或拆分。
- A詳: 
  - 症狀：延遲升高、超時。
  - 原因：資源競爭、NAS 硬體不足、IO 瓶頸。
  - 解法：top/docker stats；調整限制；分離 DB/快取；遷移至更好硬體；啟用快取與壓縮；優化 NGINX worker 與 map hash。
  - 預防：容量規劃與壓測；監控告警。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q14, C-Q9

### 學習路徑索引

- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 Reverse Proxy（反向代理）？
    - A-Q2: 為什麼本案例需要 Reverse Proxy？
    - A-Q3: 什麼是 NGINX？為何選擇它？
    - A-Q4: NGINX 與 Apache 有何差異？
    - A-Q5: 什麼是 URL 重寫與 301 轉址？
    - A-Q9: 什麼是 Docker？
    - A-Q10: 什麼是 Docker Volume 與 Volume-Container？
    - A-Q11: NAS 與專屬伺服器（NB/Ubuntu）有何差異？
    - A-Q12: 為何從 Synology NAS 轉到 Ubuntu Server？
    - A-Q14: 什麼是 WordPress 的 /?p=ID 連結？
    - B-Q1: NGINX 作為反向代理如何運作？
    - B-Q4: NGINX 的配置結構與核心組件？
    - B-Q18: NGINX 配置熱載入原理？
    - C-Q1: 如何在 Ubuntu 以 NGINX 建立反向代理到 Docker WordPress？
    - C-Q8: 如何安全測試與套用 NGINX 設定變更？

- 中級者：建議學習哪 20 題
    - A-Q6: 什麼是 NGINX 的 map 指令？
    - A-Q7: 什麼是 slug 與 slugwpid 對映？
    - A-Q8: 為何將轉址邏輯放在反向代理而非 WordPress？
    - A-Q15: 正規表達式擷取群組在 NGINX
    - A-Q16: NGINX return 與 rewrite 差異
    - A-Q17: 301 與 302 轉址差異
    - B-Q2: NGINX map 變數綁定機制
    - B-Q3: $slug 與 $slugwpid 的流程
    - B-Q5: 為何用 return 301 做轉址
    - B-Q7: map 檔解析與 include
    - B-Q12: 多容器共用單一入口的路由策略
    - B-Q19: 反向代理標頭傳遞原理
    - B-Q25: 對照表外部化的工程效益
    - C-Q2: 用 NGINX map 實作 slug→ID 的 301
    - C-Q3: Apache RewriteMap 轉 NGINX map
    - C-Q4: 外部化對照表並 include
    - C-Q6: 建置 Volume-Container 佈署
    - C-Q7: 同主機發佈多容器服務
    - D-Q3: 301 轉址迴圈怎麼辦？
    - D-Q6: 反向代理後 WordPress 錯誤網址/跳轉

- 高級者：建議關注哪 15 題
    - B-Q6: NGINX 與 Apache 處理模型差異
    - B-Q8: map 的預設值與未命中策略
    - B-Q9: 大量映射的效能考量與調優
    - B-Q10: if 使用風險與評估順序
    - B-Q11: 正則比對/擷取群組原理
    - B-Q21: map 正則/萬用字元優先順序
    - B-Q22: return vs rewrite 機制差異
    - B-Q23: 2400 組轉址的抽象化
    - B-Q26: 單機多容器網路與安全
    - B-Q27: 部署圖思維落實至容器
    - B-Q30: map 正則 vs 應用層取捨
    - C-Q9: 評估新架構效能
    - C-Q10: 遷移降停機策略
    - D-Q5: 大型 map 延遲優化
    - D-Q10: 多容器變慢的診斷與解法