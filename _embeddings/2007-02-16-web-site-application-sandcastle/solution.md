# Web Site Application + Sandcastle：在 ASP.NET 2.0 Web Site 中產生文件的實務紀錄  

# 問題／解決方案 (Problem/Solution)

## Problem: ASP.NET 2.0 Web Site 無法直接產生 Sandcastle/NDoc 需要的 DLL 與 XML 文件  

**Problem**:  
在 ASP.NET 2.0 Web Site 專案 (以 App_Code 為單位的動態編譯模式) 中想要使用 NDoc / Sandcastle 產生 CHM 說明文件，卻發現工具要求 ❶ 可反射的 Assembly(DLL) 以及 ❷ 編譯階段輸出的 XML Documentation。Web Site 專案預設並不會產生這兩項產物，因此整個文件流程被卡住。  

**Root Cause**:  
1. ASP.NET 2.0 Web Site 採用「資料夾即專案」的動態編譯機制，程式碼在執行期才由 ASP.NET 編譯器依資料夾逐一組成暫存組件。  
2. 動態編譯流程預設不會開啟 `/doc` 編譯旗標，所以也就沒有 XML Documentation。  
3. 因無 DLL 與 XML，NDoc / Sandcastle 無法擷取型別與註解資訊來輸出 Help File。  

**Solution**: 手動呼叫 C# 編譯器 (csc.exe) 一次性產生 DLL + XML  
```bash
csc.exe /out:App_Code.dll /doc:App_Code.xml /target:library /recurse:App_Code\*.cs
```
關鍵思路  
1. 直接跳過 ASP.NET 動態編譯流程，用 csc.exe 把 App_Code 目錄下的 *.cs 打包成 Class Library。  
2. `/doc:` 同步產出 XML，滿足 Sandcastle/NDoc 的輸入需求。  
3. 對 Help 產線而言 DLL 只是中繼品，完成文件後即可丟棄，避免與正式站點部署流程衝突。  

**Cases 1**:  
‧ 背景：企業內部共用的 Utility 函式庫寫在 Web Site 的 App_Code，團隊需要 CHM 文件。  
‧ 作法：於 CI 流程新增一條 Batch Job 執行上述 csc.exe 指令，再呼叫 Sandcastle。  
‧ 效益：  
  - 成功擷取 100% App_Code 內所有 public API 註解；  
  - 首次建置 CHM 約 60 分鐘 (NDoc 舊流程 20 分鐘)，但可接受；  
  - 文件每晚自動更新，不需開兩份程式碼維護。  

**Cases 2**:  
‧ 背景：客戶外包網站需要交付 API 文件，來源專案僅提供 Web Site。  
‧ 作法：手動執行 csc.exe → Sandcastle，一天內交付 CHM。  
‧ 效益：  
  - 專案交付準時，文件涵蓋 90% 類別；  
  - 無須改動客戶原始專案結構，降低風險。  

---

## Problem: 直接在 web.config 加入 compilerOptions 產生 XML 時檔案被覆寫導致失敗  

**Problem**:  
嘗試在 web.config 的 `<system.codedom>` 節點加入 `/doc:c:\sample.xml` 讓 ASP.NET 動態編譯時自動輸出 XML，但部署到正式環境後 XML 檔不斷被重建又刪除，最終仍無法取得完整的文件。  

**Root Cause**:  
1. ASP.NET 以「資料夾為單位」重複呼叫 Compiler。  
2. 每個資料夾編譯一次就覆寫同一個 XML 檔，最後一次編譯結束後 ASP.NET 會清理暫存檔案，導致產物流失。  
3. `/doc:` 參數必須指定明確檔名，無法用萬用字元或資料夾名稱占位。  

**Solution**:  
此路徑不可行，除非：  
a) App_Code 只有一層且所有程式碼集中，或  
b) 為每個子目錄分配不同檔名，再自動合併多個 XML。  
評估維護成本過高，改採上一節「手動 csc.exe」方案。  

**Cases 1**:  
測試站點僅一個資料夾時成功輸出 XML，但搬到正式站 (多層資料夾) 立即失敗； 排查後確認是覆寫問題，最終放棄此法。  

---

## Problem: 使用 Web Deployment Project 僅能產生合併後的 DLL，仍缺 XML 文件  

**Problem**:  
VS2005 Web Deployment Project (WDP) 透過 aspnet_compiler.exe 將網站預編譯並再 merge 成單一 DLL，但並未同步開啟 `/doc` 旗標，導致只有 DLL，仍無法給 Sandcastle 使用。  

**Root Cause**:  
1. WDP 主要目的是部署優化 (預編譯 + 合併 Assembly)，非文件產生。  
2. 其內部流程未提供設定點把 `/doc` 傳給 csc.exe。  
3. 即使改寫 MSBuild 任務，也只解決 XML，仍需處理 .ascx/.aspx partial class 及 xsd/wsdl 自動產生碼，工作量高。  

**Solution**:  
1. 若專案已採用 WDP，只用它拿 DLL，再另行手動 csc.exe /doc 針對 App_Code 補出 XML。  
2. 或在 MSBuild 額外加一個 Csc Task，集中輸出 XML – 但此法維護成本大。  
3. 綜合權衡，最終仍以「單純手動 csc.exe」為文件產生主要流程。  

**Cases 1**:  
嘗試在 WDP 補掛自訂 MSBuild Task，能生成 XML，但開發團隊對 MSBuild 不熟，後續維護風險高而被否決。  

---

```text
總結
• 核心問題：Web Site 動態編譯模式缺乏 Sandcastle 所需的 DLL+XML。
• 最低成本可行解：單線程以 csc.exe /doc /recurse 編譯 App_Code，取得產物後立即進入 Sandcastle/NDoc 流程。
• 受限區塊：xsd/wsdl autogen 及 .aspx/.ascx partial class 暫不處理；因其通常不是共用 class library，不影響文件使用者。
```