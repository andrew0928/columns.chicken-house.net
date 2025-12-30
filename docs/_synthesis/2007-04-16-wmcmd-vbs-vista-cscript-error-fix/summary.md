---
layout: synthesis
title: "WMCmd.vbs 在 VISTA 下執行會導至 cscript.exe 發生錯誤..."
synthesis_type: summary
source_post: /2007/04/16/wmcmd-vbs-vista-cscript-error-fix/
redirect_from:
  - /2007/04/16/wmcmd-vbs-vista-cscript-error-fix/summary/
---

# WMCmd.vbs 在 VISTA 下執行會導至 cscript.exe 發生錯誤...

## 摘要提示
- 環境組合: 在 Windows Vista 上使用 Windows Media Encoder 9 附帶的 WMCmd.vbs。
- 錯誤症狀: 執行腳本時 cscript.exe 因 DEP 機制被攔截並發生錯誤。
- 觸發原因: 程式流程觸及「資料區被執行」的情境，導致 DEP 啟動保護。
- 系統限制: 在 Vista 中，cscript.exe 被強制必須啟用 DEP，無法透過關閉 DEP 規避。
- 問題範疇: 顯示連微軟自家元件也可能存在與 DEP 相容性的地雷。
- 排障策略: 透過 Google 與 Microsoft Support 尋找官方修補方案。
- 官方解法: 安裝微軟 KB929182 修補程式以修正在 Vista 使用 WME9 的相容性問題。
- 來源連結: https://support.microsoft.com/kb/929182/en-us
- 修補結果: 安裝後即恢復正常，既有批次轉檔腳本可繼續運作。
- 待解事項: 仍待 Canon 補齊 .CRW 的解碼器（codec）。

## 全文重點
作者在 Windows Vista 環境使用 Windows Media Encoder 9（WME9）所附的 WMCmd.vbs 腳本時，遭遇 cscript.exe 被資料執行防護（DEP）攔截而出錯的問題。DEP 用於防止惡意程式在資料區域執行指令，但這次情況顯示連微軟自家工具鏈在 Vista 上也可能觸發資料區執行的情境，導致 DEP 啟動保護並終止執行流程。作者原想以關閉 DEP 作為權宜措施，然而在 Vista 中 cscript.exe 被系統強制要求啟用 DEP，無法藉由停用 DEP 來繞過。於是改以搜尋官方支援資源的方式尋求解法。

經過查找，作者於微軟知識庫發現針對「在 Vista 上使用 Windows Media Encoder 9 可能遇到問題」的修補方案（KB929182）。安裝該修補程式後，問題即告排除，WMCmd.vbs 在 Vista 上可正常透過 cscript.exe 執行。隨之而來的成果是，作者先前撰寫的「批次轉換影片」腳本得以無縫延續使用，不需改碼或更動流程。文章最後補充目前唯一尚待解決的缺口，是 Canon 的 .CRW 原始檔格式仍缺乏對應的解碼器（codec），待官方或合適的第三方方案補上後，整體轉檔與處理流程才能更臻完善。

總結而言，這是一則 Vista 時代常見的相容性案例：系統層級的安全機制（DEP）與舊版多媒體編碼工具之間出現摩擦，導致腳本執行被中斷；最終藉由安裝微軟官方修補程式，恢復工具鏈在新系統上的可用性。案例同時提醒，當關鍵可執行檔受到安全策略強制（如 cscript.exe 必須啟用 DEP）時，應優先尋找官方相容性修補，而非試圖關閉保護機制。

## 段落重點
### 問題描述：WMCmd.vbs 在 Vista 觸發 DEP 導致 cscript.exe 出錯
作者在 Vista 執行 WME9 附帶的 WMCmd.vbs 時，cscript.exe 被 DEP 攔下而報錯。DEP 檢測到疑似「資料區被執行」的行為，屬於安全防護自動介入的典型情境，也反映出即便是微軟自家組件，在新系統的安全規範下仍可能存在相容性問題。

### 系統限制與排查：無法關閉 cscript.exe 的 DEP，只能尋找官方解法
作者原考慮關閉 DEP 以測試或暫時繞過，但在 Vista 環境中 cscript.exe 被強制啟用 DEP，無法以關閉保護機制來解決。於是轉向 Google 與 Microsoft Support 查找既有案例與官方修補，尋求正規且持久的解法。

### 官方修補與結果：安裝 KB929182 後恢復正常，流程可續用
在微軟知識庫找到針對 Vista 與 WME9 相容性的修補（KB929182，https://support.microsoft.com/kb/929182/en-us）。安裝後，WMCmd.vbs 於 Vista 執行恢復正常，先前撰寫的批次轉檔腳本也可繼續使用。最後指出仍待補上的環節是 Canon .CRW 的 codec，完整工作流尚差此一塊。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 基本 Windows 作業系統與版本差異（特別是 Windows Vista）
   - DEP（Data Execution Prevention）概念與安全性機制
   - Windows Script Host（cscript.exe/wscript.exe）與 VBScript 基礎
   - Windows Media Encoder 9（WME 9）與 WMCmd.vbs 的用途與基本參數
   - 編解碼器（Codec）基礎觀念（含相機原始檔如 Canon .CRW）

2. 核心概念：
   - DEP 與相容性：DEP 會阻擋可疑的執行行為，Vista 中對 cscript.exe 強制開啟
   - WMCmd.vbs 與 WME 9：以指令列自動化進行媒體轉檔的腳本
   - Vista 相容性問題：WME 9 與其附帶腳本在 Vista 可能引發 DEP 錯誤
   - 官方修補（KB929182）：安裝 Microsoft 修補即可恢復 WME 9/WMCmd.vbs 正常運作
   - 編碼流程與 Codec 依賴：轉檔成功仰賴來源格式對應的解碼器（例如 Canon .CRW）

   彼此關係：在 Vista 環境中執行 WMCmd.vbs → 觸發 DEP 對 cscript.exe 的防護 → 程式被阻擋 → 透過安裝 KB929182 修補解決 → 如需處理特定來源格式仍需安裝相應解碼器。

3. 技術依賴：
   - WMCmd.vbs 依賴：cscript.exe（Windows Script Host）+ Windows Media Encoder 9
   - 轉檔流程依賴：來源格式的解碼器（如相機 RAW 格式 .CRW）+ 目標格式的編碼器（WME 9 內建 WMV/WMA）
   - 作業系統層級：Vista 的 DEP 設定與相容性修補（KB929182）

4. 應用場景：
   - 視訊/音訊批次轉檔自動化（例如大量 DV AVI 轉 WMV）
   - 伺服器或工作站定時任務批次處理
   - 舊專案或舊工作流程在 Vista 環境下的延續與維護
   - 需依賴特定舊編碼工具或腳本的相容性修復

### 學習路徑建議
1. 入門者路徑：
   - 了解 DEP 是什麼與其在 Vista 的預設行為
   - 安裝 Windows Media Encoder 9 與認識 WMCmd.vbs 的用途
   - 確認並安裝 Microsoft KB929182 修補，驗證腳本能在 Vista 正常執行
   - 嘗試以簡單指令使用 WMCmd.vbs 進行單一檔案轉檔

2. 進階者路徑：
   - 熟悉 WMCmd.vbs 常見參數（來源、目標、編碼設定、品質/位元率）
   - 設計與撰寫批次轉檔腳本，加入錯誤處理與日誌
   - 管理與安裝所需編解碼器（如相機 RAW、特定視訊格式）
   - 研究 DEP 例外處理策略與相容性調整（在受限下採官方修補為主）

3. 實戰路徑：
   - 以既有大量視訊素材（如 DV AVI）建立完整批次轉檔流程
   - 部署於 Vista 環境（或相容模式）並整合排程器（Task Scheduler）
   - 監控失敗案例，根據來源格式補齊相應 Codec（如 Canon .CRW）
   - 產出最佳化編碼設定的範本，平衡品質與檔案大小

### 關鍵要點清單
- Vista 下的 DEP 強制性：cscript.exe 在 Vista 被強制開啟 DEP，無法簡單關閉（優先級: 高）
- 問題症狀：執行 WMCmd.vbs 會導致 cscript.exe 因 DEP 被攔截（優先級: 高）
- 官方修補 KB929182：安裝後可解決 WME 9/WMCmd.vbs 在 Vista 的相容性問題（優先級: 高）
- WMCmd.vbs 用途：透過指令列自動化 Windows Media Encoder 9 的轉檔工作（優先級: 高）
- Windows Media Encoder 9：微軟舊版編碼器，常用於 WMV/WMA 轉檔與自動化（優先級: 中）
- 來源格式依賴 Codec：如需處理 Canon .CRW 等格式，必須安裝對應解碼器（優先級: 中）
- 批次轉檔腳本實務：可用 WMCmd.vbs 建立大量檔案的自動轉檔流程（優先級: 高）
- 錯誤排除策略：遇到 DEP 阻擋優先尋找官方相容性修補，而非關閉 DEP（優先級: 高）
- 參考資源：Microsoft 支援文件與知識庫連結（KB929182）（優先級: 中）
- 相容性維運：舊工具在新系統上的相容性需測試與修補（優先級: 中）
- 安全與功能平衡：在保留 DEP 安全性的前提下解決工具運作問題（優先級: 高）
- 腳本執行環境：確保以 cscript.exe 執行並檢查系統權限與路徑設定（優先級: 中）
- 轉碼品質設定：依需求調整位元率、解析度、編碼參數以達到最佳平衡（優先級: 中）
- 自動化與排程：搭配 Windows 工作排程器定期執行批次轉檔（優先級: 低）
- 替代方案評估：必要時考慮更新到較新工具或編碼器以改善相容性與效能（優先級: 低）