---
layout: synthesis
title: "歸檔工具更新 - .CR2 Supported"
synthesis_type: summary
source_post: /2006/12/23/digital-camera-organizer-cr2-support-update/
redirect_from:
  - /2006/12/23/digital-camera-organizer-cr2-support-update/summary/
---

# 歸檔工具更新 - .CR2 Supported

## 摘要提示
- .CR2 支援: 新版歸檔工具已加入 Canon DSLR 的 .CR2 RAW 檔支援
- Microsoft Wrapper: 透過 Microsoft 提供的 RAW 影像存取 wrapper/library 成功讀取各類格式
- 無 .THM 縮圖: .CR2 檔不附帶 .thm 縮圖，導致轉存 .JPG 不含完整 EXIF
- 原尺寸 JPG 搭配: Canon 高階機可同時存原尺寸 JPG，降低自行轉檔 .CR2 -> .JPG 的必要
- 多副檔名機制: MediaFilerFileExtensionAttribute 改為支援以逗號指定多個副檔名
- Factory 更新: Factory Pattern 的 Create() 調整以支援同一 MediaFiler 處理多種副檔名
- 設定檔擴充: 新增 pattern.cr2 的設定節點以支援 .CR2
- 輕量更新: 本次代碼改動範圍小，集中在擴充副檔名與設定
- 下載更新: 提供新版二進位下載連結供測試與使用
- G2 相容性問題: Canon G2 外閃未觸發導致曝光不足之 RAW，Microsoft 工具/Library 會解碼失敗

## 全文重點
作者在沒有自備 Canon DSLR 的情況下，因友人與公司老闆提供的 Canon 5D 與 20D 之 .CR2 影像樣本而著手更新自家歸檔工具，實測後發現利用 Microsoft 打包的 RAW 影像存取 wrapper/library 能順利讀取包括 .CR2 在內的多種格式，且呼叫方式與既有流程一致。唯一差異是 .CR2 檔不會像某些機種那樣附帶 .thm 縮圖檔，因此直接從 RAW 轉出的 .JPG 無法保有完整 EXIF。考量 Canon 高階機身多能選擇同時存一張原尺寸 JPG，實務上直接使用機身生成的 JPG 比自行轉檔更有意義，故本次不特別實作 .CR2 -> .JPG 的轉檔流程。

程式面更新相對精簡，核心在於擴充副檔名的對應與建立流程。MediaFilerFileExtensionAttribute 的格式改為支援以逗號分隔的多副檔名，對應的 Factory Pattern 中 Create() 也同步調整，讓單一 MediaFiler 可處理多種延伸檔名。配合此改動，設定檔新增 pattern.cr2 節點，以啟用 .CR2 的處理路徑。除此之外並無大幅改動。作者同時致謝提供樣本檔的同事與友人，並附上新版二進位檔下載連結，供使用者測試與更新。

文末作者提到一個相容性疑點：以 Canon G2 拍 RAW 時若外接閃光燈未及回電而未觸發，雖然相機內預覽看似正常，但將檔案傳至電腦後以 Microsoft Raw Image Viewer 或相同 library 解析會失敗並拋出例外。此現象推測與該組 RAW 的曝光/標記或特定廠商解碼器在邊界條件下的處理有關，顯示在某些特殊拍攝條件下，第三方解碼鏈可能仍存在兼容性或健壯性問題。

整體而言，本次更新完成了 .CR2 支援並優化了副檔名對應的彈性與維護性，對使用 Canon DSLR RAW 檔工作流程的使用者更為友善；同時提醒使用者在極端拍攝情境下，某些解碼工具仍可能無法正確處理 RAW，需留意備援方案或改用機身同步輸出的 JPG。

## 段落重點
### 加入 .CR2 支援的背景與動機
作者原無 Canon DSLR，可因朋友購入 5D 與公司老闆的 20D 提供 .CR2 樣本，得以測試並更新工具。透過 Microsoft 的 RAW 圖像處理 wrapper/library，確認各格式皆可讀取，接口用法與既有流程一致，顯示導入 .CR2 的技術門檻不高、整合順利。實測中唯一差異在於 .CR2 不附帶 .thm 縮圖檔，導致從 RAW 直接轉存的 JPG 缺少完整 EXIF。考量高階 Canon 機身可同時輸出原尺寸 JPG，此配置能自然滿足瀏覽與分享需求，自行再做 .CR2 -> .JPG 的轉檔價值有限，因此本次未投入此功能。

### 程式更新內容與設定變更
本次改動聚焦在提升副檔名對應與工廠建立流程的彈性。首先，MediaFilerFileExtensionAttribute 改為允許以逗號列出多個副檔名，解決一對一對應的限制；其次，Factory Pattern 的 Create() 方法同步更新，使同一個 MediaFiler 能處理多種副檔名，提高元件複用性並簡化擴充成本。為支援 .CR2，設定檔新增 pattern.cr2 節點，形成從設定驅動的擴展方式，便於後續再加入其他 RAW 格式。整體屬輕量更新，變更面向清晰集中，利於維護。文末提供新版二進位下載連結，方便使用者直接試用與更新現有流程。

### 相容性問題與實務觀察
作者分享一則 Canon G2 的特例：於拍 RAW 時若外接閃燈未及回電而未觸發，雖相機內預覽正常，但在電腦端使用 Microsoft Raw Image Viewer 或其同套 library 解析會拋出例外，無法解碼。此現象暗示特定曝光或中斷閃燈狀態下，RAW 檔的內部標記或數據分佈可能讓解碼器出現邊界條件處理不足，反映第三方解碼鏈在非典型拍攝情境的穩定性限制。對使用者而言，若拍攝任務關鍵，建議啟用相機同步存 JPG 以備援，或在後製工具上準備不同解碼器/軟體交叉驗證，以降低資料不可讀的風險。作者也以此提醒使用者，高階機身的原尺寸 JPG 選項在實務流程中相當實用，可避免因 RAW 解碼相容性問題造成的瓶頸。

## 資訊整理

### 知識架構圖
1. 前置知識
   - 數位相機 RAW 格式基礎（特別是 Canon .CR2 與早期相機的 .THM 縮圖檔）
   - EXIF/Metadata 基本概念與在 JPG/RAW 中的差異
   - .NET 開發基礎（Attribute、Factory Pattern、組態檔）
   - 使用 Microsoft Raw Image Viewer/Library 的基本方式與限制

2. 核心概念
   - RAW 格式支援擴充：工具新增對 Canon .CR2 的支援
   - Microsoft 包裝的 RAW 函式庫：統一用法，能處理多數 RAW 格式，但存在邊界案例
   - 檔案與縮圖策略差異：.CR2 不附 .THM；Canon DSLR 可另存原尺寸 JPG
   - 擴展性設計：透過 Attribute 指定多副檔名與 Factory 改造支援多格式
   - 組態驅動：新增 pattern.cr2 讓支援可設定化
   彼此關係：以組態與擴展性設計接上 Microsoft RAW 函式庫，完成對 .CR2 的支援，同時考量不同相機的檔案/縮圖策略與 EXIF 保留問題。

3. 技術依賴
   - 應用程式（歸檔工具）
     -> 依賴 Microsoft RAW Image Library/Viewer（解析與轉檔）
     -> 使用 .NET Attribute（MediaFilerFileExtensionAttribute）宣告可支援的副檔名
     -> 使用 Factory Pattern 依副檔名建立對應處理器
     -> 由組態 pattern.cr2 提供延伸支援
   - 相機端檔案策略影響應用端流程（是否有 .THM、是否另存 JPG 影響 EXIF/縮圖與轉檔必要性）

4. 應用場景
   - 攝影檔案歸檔與管理工具，需支援多種 RAW 格式
   - 需決策是否自行做 RAW->JPG（在相機已另存 JPG 時可省略）
   - 多副檔名一致處理的媒體管線（擴充新相機/新格式）
   - 針對特定相機與拍攝情境（如外閃失誤）導致的解析失敗之除錯與相容性測試

### 學習路徑建議
1. 入門者路徑
   - 瞭解 RAW、JPG、EXIF 與縮圖檔（.THM）的基本概念與差異
   - 安裝並嘗試使用 Microsoft Raw Image Viewer/Library 解析常見 RAW
   - 練習在 .NET 中使用 Attribute 與簡單 Factory，依副檔名路由到處理器
   - 以少量 sample（如 20D/5D 所拍）驗證基本讀取流程

2. 進階者路徑
   - 將 MediaFilerFileExtensionAttribute 擴充為支援逗號分隔多副檔名
   - 改造 Factory 的 Create() 讓單一 MediaFiler 能處理多副檔名
   - 將新格式支援抽到組態（新增/維護 pattern.cr2）
   - 研究 EXIF 保留策略與縮圖來源（無 .THM 時如何處置；相機另存 JPG 的取用邏輯）
   - 建立異常處理與相容性分析（針對解析失敗情境記錄與 fallback）

3. 實戰路徑
   - 在現有歸檔工具中加入 .CR2 支援：更新 Attribute、Factory、組態 pattern.cr2
   - 以多機種 sample 驗證（20D/5D/G2 等），測試讀取、縮圖、EXIF 保留與轉檔流程
   - 設計策略：若相機已另存原圖 JPG，則跳過 RAW->JPG 轉檔以節省流程與避免 EXIF 流失
   - 建立錯誤回報與記錄：對 Microsoft Library 解析例外（如 G2 外閃未觸發情境）做紀錄與提示
   - 撰寫文件與維運流程，說明新增副檔名支援與組態變更方法

### 關鍵要點清單
- .CR2 支援新增：歸檔工具已能處理 Canon .CR2 RAW 格式（依賴 Microsoft RAW 函式庫） (優先級: 高)
- Microsoft RAW Library 一致用法：相同 API 可處理多數 RAW，降低實作成本 (優先級: 高)
- .THM 縮圖缺席：.CR2 通常不帶 .THM，影響縮圖/EXIF 流程設計 (優先級: 高)
- 相機另存原圖 JPG：Canon DSLR 可同時存 RAW+JPG，實務上可省略自行 RAW->JPG (優先級: 中)
- EXIF 保留議題：由 RAW 轉 JPG 可能導致 EXIF 不完整，需評估保留策略 (優先級: 高)
- 多副檔名 Attribute：MediaFilerFileExtensionAttribute 支援逗號分隔多副檔名 (優先級: 中)
- Factory 改造：Factory Create() 支援單一處理器對應多副檔名，提升擴展性 (優先級: 高)
- 組態擴充：新增 pattern.cr2，讓格式支援以組態驅動 (優先級: 中)
- 相容性測試：需以實機 sample（如 20D/5D）驗證讀取、縮圖與 EXIF 行為 (優先級: 高)
- 例外處理案例：Canon G2 在外閃未觸發造成的低曝光 RAW 可能使 Microsoft Library 拒讀 (優先級: 中)
- 錯誤記錄與回報：解析失敗時需記錄例外，利於除錯與相容性追蹤 (優先級: 中)
- 轉檔流程決策：在已有原圖 JPG 情境下，應評估關閉自動 RAW->JPG (優先級: 中)
- 測試檔來源管理：建立多機型、多情境的 sample 片庫以回歸測試 (優先級: 中)
- 使用者溝通：文件化支援範圍、限制與已知問題（如 G2 特例） (優先級: 低)
- 未來擴展準備：設計讓新增其他 RAW 格式僅需更新組態與對應處理器 (優先級: 中)