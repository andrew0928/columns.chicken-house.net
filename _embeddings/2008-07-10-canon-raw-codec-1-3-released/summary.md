# Canon Raw Codec 1.3 Released !

## 摘要提示
- 新版釋出: Canon RAW Codec 更新至 1.3 版，作者驚訝於竟然有新版可下載。
- 支援機種: 新增 EOS Kiss X2／EOS DIGITAL REBEL XSi／EOS 450D 等相機的 .CR2 檔支援。
- Vista 支援: 官方文件宣稱「正式」支援 Windows Vista SP1。
- 效能與 x64: 更新說明未提到效能提升或 x64 版本推出時間。
- 下載途徑: 必須在 Microsoft Pro Photo Tools 網站中選擇 Windows Vista 才會顯示下載項目。
- 相容性疑慮: 1.3 版與 1.2 版在某些情況下不相容，導致作者的歸檔程式無法執行。
- 與 MS 工具衝突: 官方指出 1.3 版與 Microsoft Pro Photo Tools 軟體不相容，建議使用者暫緩升級。
- 版本混亂: 1.2 版同時存在 RC120UPD_7L.EXE 與 CRC120UPD_7L.EXE 兩支安裝檔，易混淆。
- 測試結果: 作者實測只有最早的 RC120UPD_7L.EXE 能與其歸檔程式及 .NET 3.0 + WPF 應用正常協作。
- 更新建議: 使用 .NET 3.0／WPF 或需與 Pro Photo Tools 協同工作的環境，最好維持在 1.2 版以免出包。

## 全文重點
作者偶然發現 Canon RAW Codec 已由 1.2 升級到 1.3，雖然官方更新記錄僅列出「支援新機種」與「正式支援 Vista SP1」，並未提到效能改善或 x64 支援，但作者仍決定下載試用。新版帶來對 EOS Kiss X2／EOS 450D 等機種 .CR2 檔的解碼能力，使用者需到 Microsoft Pro Photo Tools 網站並在作業系統下拉選擇「Windows Vista」才會看見下載連結。  
不過作者在 7 月 12 日補充指出，1.3 版與 1.2 版存在相容性缺口：安裝後其自製歸檔程式無法運作，且官方亦明確標註與 Microsoft Pro Photo Tools 軟體不相容。進一步檢查還發現 1.2 版竟有兩個檔案名稱（RC120UPD_7L.EXE 與 CRC120UPD_7L.EXE），新版 1.3 則為 RC130UPD_7L.EXE。實測顯示唯有最早期的 RC120UPD_7L.EXE 能與其歸檔程式及其他 .NET 3.0 + WPF 應用正常協同；其餘版本都會發生錯誤。  
綜合上述，若使用者依賴 .NET 3.0／WPF 應用或 Microsoft Pro Photo Tools，建議暫停升級並繼續使用舊版 1.2，否則可能面臨軟體衝突或功能中斷。

## 段落重點
### 版本 1.3 釋出初感
作者無意間發現 Canon RAW Codec 推出 1.3 版，雖然更新內容僅列出「支援新機種與 Vista SP1」，且未提及效能或 x64 強化，但仍決定安裝測試。新版的主要亮點是支援 EOS Kiss X2／Digital Rebel XSi／EOS 450D 等新相機 RAW 檔案，並標榜「正式」相容於 Vista SP1。下載方法稍微隱晦：必須進入 Microsoft Pro Photo Tools 官方網站，並將 OS 選單設為 Windows Vista 才會顯示 Canon RAW Codec 1.3 的下載連結。

### 2008-07-12 補充：相容性問題
裝完 1.3 後作者發現部分歸檔程式無法啟動，推測新版與舊版在 API 或 COM 介面上不完全一致。官方說明亦提醒 1.3 與 Microsoft Pro Photo Tools 不相容，使用該工具者勿升級。進一步檢視版本編號，1.2 版同時存在 RC120UPD_7L.EXE（較早）與 CRC120UPD_7L.EXE（較新）兩種安裝檔，而 1.3 版則為 RC130UPD_7L.EXE。作者測試結果顯示，只有「最古早」的 RC120UPD_7L.EXE 能與其歸檔程式及其他依賴 .NET 3.0 + WPF 的應用正常協作，因此建議需要這類環境支援的使用者維持在 1.2 版，避免因升級導致軟體衝突或工作流程中斷。