---
layout: synthesis
title: "Vista Day 4..."
synthesis_type: summary
source_post: /2007/04/03/vista-day-4/
redirect_from:
  - /2007/04/03/vista-day-4/summary/
---

# Vista Day 4...

## 摘要提示
- 工具列變動: Vista 內建工具列無法再拉出工作列，影響既有操作習慣。
- 注音輸入法改版: 內建注音大改，取消底部選字條與多項舊習慣，導致大量不適應。
- Console 拖拉限制: 命令列視窗無法拖曳檔案取得路徑，需手打完整路徑，降低效率。
- PowerToys 失效: Image Resizer、RAW Image Viewer 無法在 Vista 使用，影響影像工作流程。
- 影像架構更動: Vista 以 WPF/WIC 取代 GDI+，影像處理改用 codec 模式並引入 HD Photo。
- RAW 支援落差: Nikon 已提供 WIC codec；Canon RAW（CRW/CR2）仍未見官方 WIC codec。
- UAC 體驗: UAC 雖強化安全但提示頻繁，對熟悉者成干擾、對不熟者恐成「一律按是」。
- 權限觀念對比: 作者偏好類 sudo 的按需提權；Windows 早期需 Admin，後來以 runas 改善。
- 使用決策: 因不習慣與干擾，作者最終關閉 UAC，待後續再談正面面向。
- 影響評估: 注音改動與 PowerToys 失效對日常使用衝擊最大，娛樂機尚可，工作機會抓狂。

## 全文重點
作者升級到 Windows Vista 的第四天，列出多項令人不爽的變動，直指其對日常操作流程的衝擊。首先是介面與操作上的不便：內建工具列無法像以往那樣拉出工作列，命令列視窗不再接受拖曳檔案以自動填入路徑，迫使使用者手動輸入完整路徑，降低效率。其次，內建注音輸入法大幅改版，取消傳統底部選字列與既有手感，並移除從 DOS 時代沿用的 ALT+小鍵盤輸入 ASCII 功能；中文模式下按住 Shift 輸入改為大寫（非以往小寫），選字時無法以 Backspace 取消，導致遊戲與聊天情境中常被卡住。多年累積的輸入習慣被打亂，使中文輸入體驗顯著惡化。

更大影響在影像處理工作流。兩個常用的 PowerToys（Image Resizer、RAW Image Viewer）在 Vista 不再可用。追究原因在於 Vista 全面改用 WPF 與 Windows Imaging Component（WIC）處理影像，捨棄過去 GDI+（System.Drawing）的方式，並採 codec 架構支援各種影像格式，同時藉 WPF 首次引入 HD Photo（Windows Media Photo），意在長期挑戰 JPEG 標準。這代表原先仰賴舊元件的自製歸檔程式無法運作；雖然未來可望透過 WIC 以較正規的 API 存取 RAW，但目前僅見 Nikon 已提供 NEF 的 WIC codec，Canon 的 CRW/CR2 尚未跟上，讓作者的 Canon 工作流陷入停擺，需等待官方 codec 釋出後再改寫程式。

安全性方面，UAC（使用者帳戶控制）雖能防止在管理者權限下無意進行危險操作，實務上卻顯得囉嗦。作者回憶以往被防毒軟體過度警示的經驗，認為 UAC 對熟悉系統的人反增干擾；對不熟者則可能流於「全部按是」的習慣，安全性效益打折。並吐槽某防毒大廠批評 UAC 的發言，覺得欠缺說服力。從權限管理哲學來看，作者更傾向類 Unix 的 sudo：平時低權限，需時再提權。雖然 Windows 自 2000/XP 起已有 runas 改善，能以捷徑指定管理者身分啟動工具，讓使用者可用 Power Users 身分順暢工作；但 Vista 的 UAC 仍讓他不耐，最後選擇關閉 UAC。

總結而言，對作者的日常使用影響最大的是注音輸入法的改動與 PowerToys 失效；若發生在工作機上恐難以接受。雖然他理解 Vista 在影像架構與安全性上的設計初衷，認可其長期方向（如 WIC 帶來的 RAW 正規存取、HD Photo 的布局），但在短期過渡期的相容性、可用性與習慣衝擊，造成顯著不便。文末表示先發洩一波，之後再寫些正面觀察。

## 段落重點
### 升級 Vista 第四天：總體抱怨與影響
作者列出五項主要不滿：工具列無法拉出工作列、注音輸入法大改、Console 無法拖曳檔案、兩個影像 PowerToys 失效、UAC 囉嗦。雖看似瑣碎，卻覆蓋他日常大部分操作，特別是中文輸入與影像處理，若在工作機上會崩潰；目前尚屬家用娛樂機，勉強可忍。

### 注音輸入法的全面改動與實際痛點
內建注音取消底部選字條，破壞既有視覺與節奏；移除 ALT+小鍵盤 ASCII 輸入（如 ALT-4=逗號）導致中英混打成本上升；中文狀態按住 Shift 改為大寫，不符舊習；選字階段按 Backspace 無法取消，影響遊戲聊天的流暢度。多年形成的肌肉記憶被徹底打斷，作者感嘆從 Windows 2000 起就擔心的「傳統笨注音被拿掉」在 Vista 出現了第一步。

### PowerToys 失效與影像架構轉向 WPF/WIC
Image Resizer、RAW Image Viewer 不能用，使作者依賴其 wrapper 讀取 Canon RAW 的自製歸檔程式報廢。技術原因在於 Vista 將影像處理從 GDI+（System.Drawing）遷至 WPF 與 WIC（System.Media.Imaging），採 codec 架構支援各種影像格式，並引入 HD Photo，試圖長期替代 JPEG。長遠看，WIC 將提供較正規的 RAW 存取 API；短期內相容性斷層顯著。當下 Nikon 已提供 NEF 的 WIC codec，但 Canon（CRW/CR2）尚未釋出，作者只得等待並計畫將歸檔程式改寫為基於 WIC。

### UAC 的理念與使用者體驗落差
UAC 旨在阻止管理者無意進行危險操作，流程上要求使用者確認。但作者覺得提示過多，彷彿當年被防毒軟體誤報自家腳本為病毒的困擾再現；更吐槽防毒廠商批評 UAC 的立場。對懂的人形成阻礙，對不懂的人可能淪為機械性「全部按是」。理念可取，落地體驗打折。

### 權限管理習慣：sudo 與 runas 的偏好
作者自承早於接觸 Windows 前就用 UNIX，偏好 sudo 的按需提權與平時低權限模型。Windows NT 年代非 Admin 難以工作；至 2000/XP 後有 runas 與捷徑指定執行身分改善，他可用 Power Users 身分順暢工作（如以 admin 開 MMC、命令列）。然而 Vista 的 UAC 仍讓他不耐，最終選擇關閉 UAC，期待日後再談 Vista 的正面面。

### 結語：先發洩，後續再談正面觀察
作者以自嘲口吻收束，表示本篇重在抱怨與發洩；未來將撰寫 Vista 的優點或正面改變。但當前就使用層面而言，注音與影像工具斷層是最嚴重痛點，安全性機制則在理念與實務之間仍需更佳的體驗設計與相容性銜接。

## 資訊整理

### 知識架構圖
1. 前置知識
- Windows Vista 的基本特色與與 Windows 2000/XP 的差異
- 中文輸入法（注音）基本操作觀念與 ALT+數字 ASCII 輸入
- Windows 安全性模型與權限升級（Administrator、RunAs、UAC）
- 圖像處理技術基礎：GDI+、WPF、WIC、影像編解碼器（codec）、RAW/HD Photo

2. 核心概念
- Vista 相容性與使用體驗變更：工作列/工具列、Console 拖曳、PowerToys 失效
- 注音輸入法大改：介面與快捷鍵行為改變，影響長年使用習慣
- 影像管線革新：由 GDI+ 轉向 WPF/WIC，以 codec 模式支援各影像格式與 RAW
- RAW 與 codec 生態：需安裝廠商 WIC codec 才能讀寫特定 RAW（NEF/CRW/CR2）
- UAC 安全模型：以提示控管危險操作；與 sudo/runas 模式之比較

3. 技術依賴
- WPF 依賴 .NET 3.0，並透過 WIC 處理影像；應用轉移需改寫由 GDI+ 到 WIC
- WIC 對各影像格式的支援仰賴對應 codec（第三方或相機廠商提供）
- RAW 應用（檢視/歸檔）依賴對應 WIC codec；缺 codec 導致舊流程中斷
- UAC 基於最小權限與動態提升權限；舊式以 Administrator 常駐的習慣需調整
- Console 行為調整導致舊式拖放輸入路徑的流程失效，需替代方案

4. 應用場景
- 作業系統升級評估：使用者日常操作與舊工具（PowerToys、腳本）的相容性檢視
- 開發者遷移：影像應用由 GDI+ 遷移至 WIC/WPF，新增 RAW/HD Photo 支援
- 攝影工作流：以 WIC codec 建置 RAW 檢視/歸檔流程，等待或選擇合適廠商 codec
- 安全性與生產力平衡：UAC 使用策略、RunAs/捷徑預設權限設定、是否關閉 UAC

### 學習路徑建議
1. 入門者路徑
- 認識 Vista 新增/變更功能與對日常操作的影響（工具列、Console、輸入法）
- 了解 UAC 的目的與基本操作（提示、允許/拒絕的意義）
- 學會中文輸入法在 Vista 下的新操作邏輯與替代快捷鍵

2. 進階者路徑
- 系統相容性檢查：替代 PowerToys 工具、Console 操作替代（如路徑貼上、Tab 補全）
- 深入理解 WPF 與 WIC 的關係，學會以 WIC 讀寫常見格式
- 研究 RAW 生態：安裝與使用相機廠商提供之 WIC codec，測試應用支援度
- 安全性實務：以標準使用者帳號搭配 RunAs/UAC 提升權限的日常工作法

3. 實戰路徑
- 將既有基於 GDI+ 的影像處理/檢視程式改寫為 WIC（讀寫、轉檔、縮圖）
- 為目標相機型號部署/偵測對應的 WIC codec，建立可落地的 RAW 歸檔流程
- 建立系統捷徑與管理工具以特定權限啟動（取代長駐 Administrator）
- 設計升級檢核清單：逐項驗證輸入法、Console、常用工具、腳本在 Vista 的可用性

### 關鍵要點清單
- Vista 工具列/工作列行為變更: 內建工具列無法像以往方式拉出工作列，影響桌面操作習慣 (優先級: 中)
- Console 拖放取消: 無法將檔案直接拖放到命令列視窗，需手動輸入完整路徑 (優先級: 高)
- PowerToys 相容性問題: Image Resizer、RAW Image Viewer 等舊工具在 Vista 不相容 (優先級: 高)
- 注音輸入介面改動: 最陽春注音不再有底下一排候選列的舊模式，影響打字節奏 (優先級: 中)
- ALT+數字 ASCII 輸入取消: 傳統 ALT+數字（如 ALT-44 輸入逗號）在中文模式下不再可用 (優先級: 中)
- SHIFT 行為改變: 中文模式按住 SHIFT 輸入英文變成大寫，與以往小寫習慣不符 (優先級: 中)
- 候選狀態 Backspace 限制: 注音選字期間無法以 Backspace 取消，易造成卡鍵情況 (優先級: 中)
- 影像堆疊轉向 WPF/WIC: Vista 改以 WPF 與 WIC 處理影像，取代 GDI+ (System.Drawing) (優先級: 高)
- WIC codec 模型: 各影像/RAW 格式需安裝對應 WIC codec 才能支援（如 NEF、CRW/CR2） (優先級: 高)
- RAW 工作流影響: 依賴 RAW Image Viewer wrapper 的程式在 Vista 失效，需重構至 WIC (優先級: 高)
- HD Photo 目標: 透過 WPF 首次引入 HD Photo（Windows Media Photo），長期目標挑戰 JPEG (優先級: 低)
- UAC 的目的與體驗: 以提示控管高風險操作，理想提升安全但易造成打擾與“習慣性全按允許” (優先級: 高)
- sudo vs runas vs UAC: 舊有以 Administrator 常駐與 runas 的工作流，與 UAC 的差異與折衷 (優先級: 中)