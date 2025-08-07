# Azure Labs: Windows Container Swarm

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 在 Azure 上自行土炮一個 Windows Container Swarm Mode 叢集大概要花多久時間？
只要先準備三部「Windows Server 2016 Datacenter – with Containers」VM，整個 Swarm 叢集大約五分鐘就能建完。

## Q: Azure Container Registry 的計費方式是什麼？  
服務本身完全免費，只要支付存放映像檔所占的 Azure Storage 費用；如果還沒 push 任何映像檔，基本上就是 0 元成本。

## Q: Windows Container Host 目前支援 Docker Swarm 的 Routing Mesh 嗎？  
尚未支援。官方文件提到「Routing mesh for Windows docker hosts is not yet supported, but will be coming soon」，目前只能使用 DNSRR（DNS Round-Robin）或自行建外部 Load Balancer。

## Q: 如果要在 Docker Swarm 中使用放在 Azure Container Registry 的私有映像檔，該注意哪些事？  
1. 每一台 Swarm 節點都必須先 `docker login` 到該 Registry。  
2. 建立服務時要加 `--with-registry-auth`，例如  
   ```
   docker service create --name mysvc --with-registry-auth wcshub.azurecr.io/myimg:latest
   ```

## Q: 為什麼用 `-p 80:80` 發佈埠號後，瀏覽器卻連不到服務？該如何解？  
因為 Windows 版 Docker 目前沒有 Routing Mesh，只宣告 `-p 80:80` 不會自動把埠號對外開放。  
解法是在 `docker service create` 時改用  
```
--publish mode=host,target=80,published=80
```  
明確指定 host mode 的埠號對映後即可正常連線。

## Q: 目前在 Windows Swarm 上想做負載平衡有哪些替代方案？  
• 使用 DNSRR (Docker Native DNS Round-Robin)，再搭配自行架設的 NGINX、HAProxy 等外部 Load Balancer。  
• 等待 Microsoft 把 Routing Mesh 功能補上（官方說「coming soon」）。

## Q: 建立實驗環境前需要哪些 Azure 資源？  
一個可用的 Azure Subscription 即可。新註冊的帳號有約新台幣 6,300 元的免費額度，足夠完成本文所有練習。

## Q: 本文主要分享哪兩大重點？  
1. 在 Azure 上部署 Windows Container + Swarm Mode 的實務流程。  
2. Windows Container 目前仍然「慢半拍」的限制與踩雷心得，幫讀者避開常見陷阱。

## Q: Docker Overlay Network 在 Swarm 裡扮演什麼角色？  
Swarm 會自動建立 `ingress` Overlay Network，讓跨主機的 Container 能在同一條虛擬私網中彼此通訊；沒有它，多主機間就無法做到服務發現與內部連線。

## Q: 什麼時候最適合開始學 Docker？  
作者給的答案是：「最好的時間是四年前，或是現在！」