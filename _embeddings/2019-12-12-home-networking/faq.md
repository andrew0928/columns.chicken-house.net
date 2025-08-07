# 水電工日誌 #7．事隔 12 年的家用網路架構大翻新

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 這次為什麼會動手整修 12 年沒動的家用網路？
一次台電計畫性停電後，家中 router 與 24 埠 Gigabit switch 先後掛點。檢修後發現真正原因並非停電，而是設備內部電容鼓包老化，於是作者決定趁勢全面翻新家用網路。

## Q: 這次汰換設備的兩大目標是什麼？
1. 徹底解決長期困擾的 Wi-Fi 連線不穩問題。  
2. 重新規畫網路基礎設備（Router／Switch），讓架構更彈性、可切 VLAN，也方便日後擴充。

## Q: 最終選用哪一款無線基地台 (AP)，一次買了幾台？
作者選了 Ubiquiti UniFi AP AC Lite，直接一次購入兩台。

## Q: 為什麼會選 UniFi AP AC Lite？
它屬於企業級 AP，支援單一 SSID 無縫漫遊、PoE 供電、訊號穩定且可由 UniFi Controller 統一管理；加上吸頂式外型與高 CP 值，十分符合全屋部署需求。

## Q: 若不想額外購買 UniFi Cloud Key，要怎麼跑 UniFi Controller？
作者在 NAS 上以 Docker 版本安裝 UniFi Controller，省去購買硬體控制器的費用。

## Q: 取代舊 MikroTik RB450G 的新 Router 是哪一台？主要考量為何？
新 Router 為 Ubiquiti EdgeRouter-X SFP。主要考量包含：
1. 內建硬體 Switch，可在 Router 端直接切 VLAN。  
2. 支援 PoE，可直接供電給 UniFi AP。  
3. 溫度低、不再動輒 90 °C。  
4. Web UI 較易上手，必要時仍可用 CLI 進階設定。

## Q: 全新 16 埠 Switch 選了什麼型號？為何不再使用無網管 Switch？
改用 Netgear GS116E v2 智慧型 Switch。它支援 VLAN、QoS、LAG 等基本網管功能，可讓作者把三個獨立網段（Server LAN、Home LAN、VDSL/MOD）用 VLAN 方式集中在同一台 Switch 上，節省實體線路與埠口。

## Q: 文中出現的「亂入」敗家品是什麼？用途為何？
是 Intel i350-T4 四埠 Gigabit Server NIC。作者在工作用 PC 上安裝它，方便同時接多條網路線、做 LACP 或直接用 PPPoE 測試外線，不怕驅動相容問題。

## Q: 作者對新網路環境提出了哪些具體需求？
1. NAS 與 Server 需獨立網段並由防火牆隔離。  
2. Wi-Fi AP 必須能用 PoE 直接供電。  
3. 關鍵線路要直接 Router。  
4. 工作 PC 隨插即能 PPPoE 撥接。  
5. NAS 需以 LACP 聚合兩埠，提高頻寬。  
這些需求最終透過 EdgeRouter-X SFP + GS116E 的 VLAN 配置全部達成。

## Q: 新架構實際測得的效能如何？
1. LAN ↔ LAN（經 Router 轉發、未做 NAT）：搬檔可達 986 Mbps，接近 Gigabit 極限。  
2. 經 NAT 上網（100/40 M HiNet）：實測 91.03 / 39.84 Mbps，已接近 ISP 上限。  
在開啟 EdgeRouter 硬體 Offloading 時，官方與多數實測皆可達近 1 Gbps LAN→WAN 滿速。

## Q: 從這次經驗，作者得到哪些軟體開發上的啟發？
網路設備能藉由「Rule + Priority」與標準化協定（如 VLAN Tag）在複雜環境下僅靠設定就解決問題，顯示「領域知識抽象化」與「規則引擎」的威力；這種思維同樣可套用在一般軟體系統設計上，減少硬改程式碼、提高彈性。