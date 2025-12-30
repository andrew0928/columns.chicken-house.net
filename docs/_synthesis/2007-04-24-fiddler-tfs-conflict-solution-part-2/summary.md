---
layout: synthesis
title: "Fiddler 跟 TFS 相衝的問題解決 - II"
synthesis_type: summary
source_post: /2007/04/24/fiddler-tfs-conflict-solution-part-2/
redirect_from:
  - /2007/04/24/fiddler-tfs-conflict-solution-part-2/summary/
---

# Fiddler 跟 TFS 相衝的問題解決 - II

## 摘要提示
- 問題背景: Fiddler 與 TFS 衝突導致操作不便，需自動化調整 IE/WinINET Proxy 設定與 bypass 清單
- 目標流程: 啟用 Capture 時自動改 Proxy 並加入自訂 bypass；停止時還原設定
- 多網卡情境: 不同網卡各自 Proxy 設定導致 Fiddler 常失效，需一併解決
- A 計劃（內部欄位）: 企圖讀寫 Fiddler.Proxy 私有欄位失敗，因為是 private 且無法反射存取
- B 計劃（直接呼叫 API）: 以 WinINETProxyInfo 直接改 Proxy 成功於 Console App，嵌入 Fiddler Script 失敗
- AppDomain 隔離: Fiddler Script 的動態載入/編譯與獨立 AppDomain 限制了型別存取
- C 計劃（反射繞道）: 以反射從 Fiddler.exe 載入型別仍失敗，與 B 計劃同樣受限
- D 計劃（外部程式）: 以外掛 Console EXE 寫入 Proxy 設定並由 Script 啟動，最終可行
- 實作重點: CustomRules.js 於 OnAttach 呼叫 myproxycfg.exe，Fiddler 停止時由其內建機制還原設定
- 經驗總結: 面對 AppDomain 與可見性限制，實務上以外部工具繞過環境隔離更穩定

## 全文重點
作者面臨 Fiddler 與 TFS 的使用衝突：在以 Fiddler 擷取流量時，IE/WinINET 的 Proxy 設定需要切換至 127.0.0.1:8888，並加入特定 Proxy bypass 清單，否則 TFS 操作（例如 Get Latest Version）會受影響。為了讓切換無痛自動化，作者設計流程：Fiddler 啟用 Capture 時自動修改 Proxy 並加入自訂 bypass，停止 Capture 時還原原本設定。此舉也能順便解決多網卡（如家用 VPN、公司無線網路）導致 Fiddler 只改「區域連線」而失效的問題。

技術上，作者首先檢視 Fiddler 的擴充點：可在 CustomRules.js 的 OnAttach 事件插入自訂腳本，並仰賴 Fiddler 內建在啟停時自動備份/還原 WinINET 設定。A 計劃嘗試深入 Fiddler 程式內部，以 Reflector 追查主程式 Fiddler.frmViewer 與其中 oProxy 靜態欄位，找到 WinINETProxyInfo 的 piPrior（先前設定）與 piThis（目前設定），但因均為 private 欄位，無法直接存取或以反射操作而放棄。

B 計劃改走公開 API 路徑：將 Fiddler.exe 改名為 dll 供參考，寫一個 Console App 使用 Fiddler 的 WinINETProxyInfo，呼叫 GetFromWinINET、修改 sHostsThatBypass、再 SetToWinINET，測試證實有效。然而，將同樣邏輯嵌入 Fiddler 的 Script 後，編譯/載入報錯。推測原因在於 Fiddler 的 Script 是動態載入並在獨立 AppDomain 執行，導致腳本無法直接存取那些型別或組件。

C 計劃嘗試以反射繞路：在 Script 內以 Assembly.LoadFrom 載入 Fiddler.exe，CreateInstance 取得 Fiddler.WinINETProxyInfo，再反射呼叫相關方法與屬性，理論上可避開編譯期參考問題。但實作結果仍因 AppDomain 與可見性或載入內容限制而失敗，與 B 計劃遭遇相同錯誤。

最終的 D 計劃採取實務取捨：保留已驗證可行的 Console App（myproxycfg.exe）置於 Fiddler 目錄，並在 CustomRules.js 的 OnAttach 以 Process.Start 啟動它。此法成功在 Capture 開始時寫入所需 Proxy 與 bypass 設定；而當 Fiddler 停止捕捉時，沿用其原生機制自動還原先前設定。雖然在目錄多了一個外掛 EXE 顯得不夠優雅，但穩定有效，解決了 TFS 衝突與多網卡下的 Proxy 切換痛點。作者以「懶惰驅動自動化」做結，肯定此務實方案。

## 段落重點
### 前言與計劃流程設計
作者針對 Fiddler 與 TFS 衝突擬定自動化流程：啟用 Capture 時自動備份目前 Proxy 設定、切換至本機代理 127.0.0.1:8888 並加入自訂 bypass；停止 Capture 時自動還原。Fiddler 支援以 .NET 語言編寫 CustomRules.js，OnAttach 在開始擷取時觸發，理應可注入自訂邏輯。此方法同時能解決多網卡各自 Proxy 設定導致 Fiddler 在 VPN/無線網路下失效的附帶問題，減少手動切換的繁瑣。

### A 計劃：存取內部欄位失敗
透過 Reflector 反編譯，找到主程式 Fiddler.frmViewer 與 oProxy 靜態欄位，進而定位到 Fiddler.Proxy 與內含的 WinINETProxyInfo。關鍵的 piPrior（備份）與 piThis（現行）皆為 private 欄位，無法以一般或反射方式存取，因而中止此途徑。此路線本意是直接讀寫 Fiddler 內部的 Proxy 狀態，但受限於可見性，缺乏改造空間。

### B 計劃：直接用 WinINETProxyInfo，Script 內失效
改用公開 API 實作：將 Fiddler.exe 參考進 Console App，呼叫 WinINETProxyInfo.GetFromWinINET，修改 sHostsThatBypass，並以 SetToWinINET 寫回，實測可直接更動 IE/WinINET 的 Proxy 設定。然而，將相同程式碼搬進 CustomRules.js 之後，Fiddler 的 Script 編譯與載入流程回報錯誤。推論 Script 被動態載入並在另一個 AppDomain 內執行，導致型別解析或安全界線限制，腳本端無法直接使用該型別。

### C 計劃：反射載入 Fiddler.exe 仍受限
為繞過編譯期參考與可見性問題，改在 Script 內以反射動態載入 Fiddler.exe，CreateInstance Fiddler.WinINETProxyInfo，並以反射呼叫其方法與屬性，邏輯等同於 Console App。儘管技術上看似可行，實測仍失敗，錯誤情境與 B 計劃相同。顯示 AppDomain 隔離、型別可見性或組件載入上下文仍構成阻礙，腳本環境無法順利呼叫該類別。

### D 計劃：以外部 EXE 落地實作
採取務實解法：保留已驗證有效的 Console App（myproxycfg.exe），放在 Fiddler 目錄，並於 CustomRules.js 的 OnAttach 以 Process.Start 啟動它。此法在 Capture 啟用時成功寫入 Proxy 與 bypass；停止時則仰賴 Fiddler 內建的還原機制，整體流程如預期運作，亦解決多網卡情境下的設定問題。雖然外掛 EXE 不夠「優雅」，但穩定可靠、維護成本低，實用性高。

### 結語：隔離限制下的務實選擇
綜觀四種嘗試：直接操作私有欄位不可行；在 Script 內用內部型別或反射皆被 AppDomain/型別可見性限制攔下；最終採用外部流程控制（Console EXE）繞過隔離層，達到自動化 Proxy 切換與 bypass 設定的目的。此解法減少手動切換與因網路環境變動造成的失效，解決了 Fiddler 與 TFS 的衝突，也印證在受限環境下「簡單可行」往往優於「優雅但受限」的實作。

## 資訊整理

### 知識架構圖
1. 前置知識：學習本主題前需要掌握什麼？
- 基本 .NET/C# 語法與反射機制
- Windows/IE 的 WinINET Proxy 概念與設定位置
- Fiddler 的工作原理（系統代理 127.0.0.1:8888）與 CustomRules.js 腳本機制
- AppDomain 的隔離特性與動態載入/編譯腳本的限制
- 在多網卡/多連線環境下的代理設定差異

2. 核心概念：本文的 3-5 個核心概念及其關係
- Fiddler 與 WinINET Proxy 互動：Fiddler 啟用時覆寫 IE/WinINET Proxy，停用時還原
- CustomRules.js 與 OnAttach：在 Fiddler 開始擷取流量時觸發可插入客製化邏輯
- AppDomain 隔離限制：腳本在獨立 AppDomain 內，對 Fiddler 內部型別/成員的可見性受限
- 反射與動態載入：嘗試用反射或動態載入 Fiddler 型別操作 Proxy 設定
- 外部程序權衡：用外部 exe 直接呼叫 WinINET API（或封裝類）成為務實解

3. 技術依賴：相關技術之間的依賴關係
- Fiddler CustomRules.js → 由 Fiddler 動態載入/編譯 → 受 AppDomain 限制
- WinINETProxyInfo（Fiddler 內部類）→ 操作系統層的 WinINET 設定
- 反射 Assembly.LoadFrom → 取型別/呼叫方法 → 若在隔離域中仍可能受存取限制
- System.Diagnostics.Process.Start → 呼叫外部 Console 應用 → 間接更改 WinINET 設定

4. 應用場景：適用於哪些實際場景？
- Fiddler 與 TFS 同時使用造成 Proxy/連線衝突時的自動化解法
- 在 VPN/無線網路/非預設網卡環境下，自動統一各網卡的 Proxy 設定
- 需在 Fiddler 開啟/關閉時自動注入/還原特定 Proxy 規則與繞行清單
- 在腳本沙盒限制下無法直接存取內部型別時的替代方案設計

### 學習路徑建議
1. 入門者路徑：零基礎如何開始？
- 了解 Fiddler 基本用途與代理原理（127.0.0.1:8888）
- 熟悉 IE/Windows 中的 Proxy 設定與每個網卡的獨立設定
- 開啟並閱讀 Fiddler 的 CustomRules.js，理解 OnAttach/OnBeforeRequest 的觸發點
- 嘗試以最簡單方式在 OnAttach 中寫入日誌/顯示訊息以驗證流程

2. 進階者路徑：已有基礎如何深化？
- 研究 AppDomain 基本概念與腳本執行環境隔離
- 練習用反射載入組件、取型別、呼叫方法/屬性
- 了解內部/私有成員的存取限制與安全性邊界
- 練習以 Console 應用操作 WinINET 設定，並由 Fiddler 腳本觸發

3. 實戰路徑：如何應用到實際專案？
- 在 CustomRules.js 的 OnAttach 中，判斷環境（如網卡、VPN）後自動統一代理設定
- 將 WinINET 設定邏輯封裝成獨立 exe（或 PowerShell/原生 API 封裝），由腳本呼叫
- 驗證 Fiddler 啟停時代理設定的覆寫與還原，避免遺留設定
- 擴充繞行清單（Bypass List），兼顧 TFS/內網站台/常見網域需求

### 關鍵要點清單
- Fiddler 與 WinINET 的關係: Fiddler 透過修改 WinINET（IE）系統代理來攔截流量，停用時會還原設定 (優先級: 高)
- CustomRules.js 與 OnAttach: 在 Fiddler 開始擷取時觸發，可放入自動化調整代理的邏輯 (優先級: 高)
- TFS 衝突根因: 當代理被改為本機 Fiddler 時，TFS 或其他工具可能連線異常，需正確配置繞行或代理 (優先級: 高)
- 多網卡代理問題: IE/WinINET 允許每個網卡各自的代理設定，非預設 NIC 常導致 Fiddler 失效 (優先級: 高)
- AppDomain 隔離限制: Fiddler 腳本在獨立 AppDomain 中執行，對內部類（如 WinINETProxyInfo）可見性受限 (優先級: 高)
- 內部/私有成員存取限制: private/internal 成員（如 piPrior/piThis）無法直接由腳本或外部程式碼安全存取 (優先級: 中)
- 反射與動態載入風險: 即使 Assembly.LoadFrom 和反射可行，仍會受 AppDomain 與存取修飾詞限制 (優先級: 中)
- 外部程序權衡解: 以 Console 應用封裝 WinINET 設定並由腳本啟動，是繞過腳本沙盒限制的務實方案 (優先級: 高)
- WinINET 設定流程: 取得現有設定、調整繞行清單（sHostsThatBypass）、套用新設定 (優先級: 中)
- 啟停一致性: 確保 Fiddler 開啟時覆寫、關閉時還原，避免殘留代理影響其他應用 (優先級: 高)
- 繞行清單策略: 對內網/TFS/VPN 相關網域加到 bypass，提高連線成功率與效率 (優先級: 中)
- 自動化與可維護性: 將代理調整流程版本化（腳本+小工具），避免手動切換的易錯與耗時 (優先級: 中)
- 例外處理與回復機制: 外部 exe 失敗時的錯誤處理、回復原始代理配置是必要防護 (優先級: 中)
- 安全性考量: 僅在可信環境下執行外部程式與反射；避免暴露敏感設定或打開過寬的存取 (優先級: 高)
- 環境偵測: 依當前網卡/VPN 狀態調整代理目標與繞行清單，提高方案通用性 (優先級: 低)