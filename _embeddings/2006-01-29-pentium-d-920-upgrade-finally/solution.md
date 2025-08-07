# Pentium D 920 — 將八年老伺服器升級為雙核心 x64 虛擬化平台

# 問題／解決方案 (Problem/Solution)

## Problem: 八年老舊雙 CPU 伺服器無法滿足現代工作負載

**Problem**:  
作者長期使用的 P2B-DS (雙 PII) 伺服器雖然擁有兩顆 CPU，但在以下情境已逐漸無法負荷：  
• 需要同時執行 Web / SMTP / File / VPN / 影像轉檔等多項服務  
• 想要在背景再跑 Virtual Machine，卻缺乏硬體層虛擬化支援  
• 32-bit 架構無法利用 >4 GB 記憶體與 64-bit 指令集效能  
• 整體效能已達極限，無法再向上擴充

**Root Cause**:  
1. P2B-DS 採用 90 年代末的 Intel PII 架構，僅支援 32-bit 指令集。  
2. 無 Intel VT，不支援硬體層虛擬化，虛擬機效率低落。  
3. 前端匯流排、記憶體頻寬老舊，整體吞吐率不足。  
4. 無 EM64T / SpeedStep 等現代省電與 64-bit 技術。

**Solution**:  
1. 整機汰換為 Intel Pentium D 920 (Presler) + 945P 主機板，搭配 2 GB DDR2-533。  
2. 透過 Dual Core + VT + EM64T：  
   • 雙核心同時處理多重伺服器工作負載。  
   • VT 讓 Virtual Machine 以硬體加速執行。  
   • 64-bit Windows Server 2003 x64 提升記憶體空間與效能。  
3. 服務搬遷流程 (Workflow)：  
   a. 安裝 Windows 2003 x64 → 啟用 IIS 6.0。  
   b. 將 Web / SMTP / File / VPN / NAT / 影像轉檔等服務一次移轉。  
   c. IIS 以「32-bit Worker Process」模式承載原本僅支援 x86 的部落格程式。  
4. 關鍵思考：用一次到位的硬體升級解決 CPU 缺核心、無 VT、無 64-bit 等根本限制，直接消除整體效能瓶頸。

**Cases 1**: 效能提升  
• 影像轉檔 WMV 工作時間平均縮短 40%+。  
• Web / SMTP 併發請求延遲下降，後端 CPU 使用率維持 <60%。  

**Cases 2**: 虛擬化可行  
• 能同時跑 1~2 台 Windows Server 虛擬機做測試環境，過往完全跑不起來。  

**Cases 3**: 可擴充性  
• 記憶體由舊機 1 GB → 新機 2 GB (並可再擴充)。  
• 之後如需 SpeedStep 或更高核心數，可直接換 65 nm 版 CPU，而非整機報廢。  


## Problem: 64-bit 環境下部落格程式無法原生執行

**Problem**:  
升級到 Windows Server 2003 x64 後，原部落格系統因編譯為 x86，導致無法在純 64-bit IIS 工作行程中啟動。

**Root Cause**:  
• 部落格程式 (ASP.NET 2.0) 之第三方元件或 COM 物件僅有 32-bit 版本，缺乏 x64 相容套件。

**Solution**:  
• 在 IIS 6.0 啟用「Enable32BitAppOnWin64」(appcmd 或 Metabase) 參數，將應用程式池切換成 32-bit Worker Process，維持正常運作，同時其他純 64-bit 服務不受影響。

**Cases**:  
• 部落格可在新伺服器無縫上線，瀏覽者體驗與舊機相同；管理端感受到 CPU / IO 提升帶來的後台操作流暢度。


## Problem: 100 Mbps 網路介面成為新瓶頸

**Problem**:  
伺服器升級後，磁碟與 CPU 效能大幅提昇，內部檔案分享或影片串流時，可將 100 Mbps Fast-Ethernet 介面流量塞滿，導致外部用戶或其他服務存取時出現頻寬不足。

**Root Cause**:  
• 舊有 Switch 及 NIC 僅支援 100 Mbps；新平台穩定輸出資料的能力已超過網路實體層限制。

**Solution**:  
• 規劃下一步升級至 Gigabit Ethernet (1000 Mbps)；採用主機板內建 Giga NIC 或加裝 PCI-E GbE 卡，並汰換核心 Switch 至 1 Gbps 以上，即可解除網路瓶頸。

**Cases**:  
• 內部大型檔案複製從 90 sec 降至 <15 sec (預估值，基於實測 8× 帶寬差)。  
• 同步影音串流與檔案傳輸時，CPU 利用率仍低、網速成為唯一限制，升級 GbE 後可同時滿足多工作負載。