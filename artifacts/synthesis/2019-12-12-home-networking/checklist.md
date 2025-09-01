## 內容品質檢核表

### Summary 品質檢核
- [x] 涵蓋所有核心技術點
  - 已涵蓋 UniFi AP/Controller、EdgeRouter-X SFP、GS116E、VLAN/Trunk、PoE、LACP、PPPoE、硬體 offloading、效能實測與設計哲學。
- [x] 建立清晰的知識架構
  - 提供「知識架構圖」「技術依賴」「應用場景」，脈絡清楚。
- [x] 提供明確的學習路徑
  - 有分入門/進階/實戰的學習路徑與索引，順序合理。
- [x] 包含可量化的成效指標
  - 列出 LAN-LAN 約 986 Mbps、WAN 91/39.84 Mbps、offload 近 1Gbps等數據。
- [x] 適合不同程度的學習者
  - 以優先級、難度標註與不同層級路徑照顧新手到進階者。

### FAQ 品質檢核
- [x] 問題涵蓋廣度（概念/原理/實作/問題）
  - 概念（VLAN/PoE/PPPoE）、原理（offload/rkv/LACP）、實作（Docker/Trunk/ACL）、問題解決（採納/撥接/診斷）均有。
- [x] 答案層次分明（簡答/詳答）
  - 每題皆有「A簡/ A詳」，層次分明。
- [x] 難度標註準確
  - 难度與學習階段標註普遍恰當（初級/中級/進階）。
- [x] 知識點關聯性明確
  - 每題列出關聯概念，交叉引用清楚。
- [x] 學習順序合理
  - 提供分層次學習建議（初學/中級/高級），順序由基礎到實作到進階。

### Solution 品質檢核
- [x] 問題描述具體且真實
  - 案例均對應原文情境（WiFi 黏著、VLAN 切割、PPPoE 測試、溫度與電容）。
- [x] 根因分析深入透徹
  - 多層次（直接/深層）原因分析完整。
- [x] 解決方案步驟清晰
  - 各案均有步驟、所需資源與時間估算（大多數案例）。
- [x] 包含可執行的範例
  - 提供 CLI/compose/設定參考、拓撲原則與指令。
- [x] 提供練習題與評估標準
  - 每案皆有練習與評估規準（功能/品質/效能/創新）。
- [x] 標註學習難度與所需時間
  - 每案有「複雜度評級」，步驟含多處「預估時間」。建議補齊個別案例未標時程者以更一致。

### 整體一致性檢核
- [ ] 三份文件的技術術語一致
  - 大多一致；少數細節需修正：
    - 防火牆方向一致性：Solution Case #10 於綁定規則使用「firewall local」與文字敘述的「in」不一致；建議改為 on-interface in/out，以符合 inter-VLAN 控制意圖。
    - PoE 規格描述：文件同時提及 802.3af 與 24V passive 可能性；UAP-AC-Lite 新版多為 802.3af，ER‑X SFP 為 24V passive passthrough（條件式）。建議在 Solution Case #6 明確標示實際機型/供電模式與是否需 PoE 注入器或 PoE switch，避免誤用。
- [x] 知識點交叉引用正確
  - FAQ、Solution、Summary 的主題與相互引用基本一致（VLAN/Trunk/PPPoE/Controller）。
- [x] 學習路徑邏輯連貫
  - 從基礎（Controller/交換器概念/角色分離）→ VLAN 與防火牆 → 無線優化 → 效能測試 → 維運可靠性，遞進合理。
- [x] 難度評級標準統一
  - FAQ 與 Solution 的難度分級口徑一致；題組與案例分類清晰。

補充建議
- 對應原文的設備與規格差異處，集中一小節「相容性備註」：UAP-AC-Lite 版本對應 PoE 標準、ER‑X SFP PoE 輸出模式、若不相容時的替代（PoE 注入器/PoE 交換器）。
- 防火牆示例修正：將 Case #10 的介面方向由 local 改為 in/out 綁定於 switch0.vifX（例如 set interfaces switch switch0 vif 10 firewall in name HOME-2-SERVER），與 C-Q7 的原則一致。
- 時間預估一致性：少數案例未列各步驟時間，建議補上以達到全案一致的「所需時間」展示。