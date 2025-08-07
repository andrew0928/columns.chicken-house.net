# [實戰] 十分鐘搞定! 在 Azure 上面佈署 Docker Container! - Docker Cloud 託管服務體驗

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 若想在 Microsoft Azure 上快速部署 Docker Container，整體流程是什麼？
1. 先註冊／登入 Docker Cloud，並將帳號與 Azure 進行授權綁定（下載憑證→上傳至 Azure「管理憑證」→回填 Subscription ID）。  
2. 在 Docker Cloud 的 Nodes 區域選擇 Microsoft Azure，設定機房、VM 規格與磁碟大小後建立 Node（即 Docker Host）。  
3. 到 Stacks 建立 Stackfile，例如 WordPress 需要 web 與 db 兩個 service。  
4. 按「Save and Deploy」，Docker Cloud 會自動在 Azure VM 上拉取映像並啟動容器。  
5. 佈署完成後，到 Stack 的 Endpoints 分頁取得自動產生的 FQDN，網站即對外可用。

## Q: Docker Cloud 與自行 Hosting 的差異是什麼？
Docker Cloud 提供的是「託管（管理）服務」：  
• 它負責節點佈署、容器排程、DNS、Redeploy 等管理工作。  
• 實際的運算與儲存資源（VM、磁碟）仍在使用者自選的雲端或實體主機上，相關費用需向雲端供應商（如 Azure）支付。  

## Q: Docker Cloud 的免費方案有哪些限制？
免費帳號僅可管理 1 個 Node；若要額外節點，每個 Node 每月收費 15 美元（約 0.02 美元/小時）。雲端 VM、磁碟等資源費用則由 Azure 另行計費。

## Q: 在大型部署中，哪些官方工具可以搭配 Docker 使用以簡化管理？
1. Docker Machine：大量快速建立 Docker Host。  
2. Docker Compose：用單一設定檔一次佈署多個互相關聯的容器。  
3. Docker Swarm：負責多主機間的排程、資源調度、自動擴充與高可用。

## Q: 建立 Docker Cloud Node 前，需要在 Azure 做哪些授權設定？
必須先從 Docker Cloud 下載管理憑證，至 Azure 舊版管理入口「設定 → 管理憑證」上傳該憑證，再將 Azure Subscription ID 填回 Docker Cloud；出現綠色勾勾即代表授權成功。

## Q: 服務佈署完成後要如何連到自己的 WordPress 部落格？
在 Stack 的 Endpoints 分頁可看到 Docker Cloud 自動配置的 FQDN（例如 `xxxxxx.cloudapp.docker.com`），直接以此網址存取即可；若想用自有網域，只需在 DNS 加一筆 CNAME 指向該 FQDN。

## Q: 如果想修改容器的 Port 或環境變數，要怎麼操作？
編輯 Stackfile 後按「Save」，Docker Cloud 會標示需更新的 Service；點擊「Redeploy」即可刪除舊容器並依新設定重建，過程簡單且可選擇只重建特定 Service。

## Q: 想做到多節點高可用該怎麼實現？
將 Service 的容器數量調高並分散到不同 Nodes；若 80 port 已被占用，可改用動態 Port Mapping，再由前端 Reverse Proxy 做流量導向。當有多個容器同時提供服務時，可採「逐一 Redeploy」的方式避免中斷。

## Q: 作者實際花了多久就把多個服務搬到自家 MINI-PC 上？
從開始研究 Docker Cloud 到所有服務（Blog、GitLab、Redmine 等）建立完畢，作者花不到一天時間。

## Q: 為什麼作者強烈推薦大家試用 Docker Cloud？
因為 Docker Cloud 介面直覺、佈署快速，免費方案即可享有過去只有大型雲端平台才具備的自動化管理、DNS 整合與 Stack/Redeploy 能力，省錢又省去專職維運人力，非常適合個人或小型專案嘗鮮與使用。