---
layout: synthesis
title: "前言: Canon Raw Codec 1.2 + .NET Framework 3.0 (WPF)"
synthesis_type: summary
source_post: /2007/11/26/introduction-canon-raw-codec-1-2-net-framework-3-0-wpf/
redirect_from:
  - /2007/11/26/introduction-canon-raw-codec-1-2-net-framework-3-0-wpf/summary/
postid: 2007-11-26-introduction-canon-raw-codec-1-2-net-framework-3-0-wpf
---

# 前言: Canon Raw Codec 1.2 + .NET Framework 3.0 (WPF)

## 摘要提示
- Canon Raw Codec 1.2 更新: 解決 G9 .CR2 在 XP/Vista 的基礎顯示問題，為自動化與後續處理鋪路。
- WPF 與 EXIF Metadata 困境: BitmapSource.Metadata 為 null、可用欄位稀少、官方文件細節匱乏。
- Metadata Query Language: 以 Query 語法操作影像中繼資料，但缺少可列舉現存鍵值的方法。
- InPlaceMetadataWriter 失效: 文件建議的就地修改方式實測不可行，需改採替代流程。
- CR2 與 JPG 差異: 相同 EXIF 概念下，兩者對應的 Metadata Query 鍵值完全不同。
- 效能瓶頸: Canon Codec 解碼 + JPEG 編碼耗時高，多核心效益不彰。
- 相容性問題: WPF 讀取 G2 .CRW 例外，與 Microsoft Viewer 表現不一致。
- 解法一：列舉 Query: BitmapMetadata 實作 IEnumerable<string>，可直接 foreach 取得鍵值。
- 解法二：修改流程繞道: 以 metadata.Clone() 修改後再交給 Encoder，有效避開寫入問題。
- 後續計畫: 將推出 Image Resizer 與記憶卡歸檔工具新版，完整分享實作與最佳化經驗。

## 全文重點
作者在 Canon 推出 Raw Codec 1.2 後，終於能在 XP/Vista 直接顯示 Canon G9 的 .CR2 檔，並著手探究如何在 .NET 3.0 WPF 環境下自動化處理。然而實作過程遭遇多重挑戰，尤其是 EXIF/Metadata 相關：BitmapSource.Metadata 一直是 null，WPF 內建可用的 Metadata 欄位極少，且官方文件缺乏對 Metadata Query 語言與鍵值列表的說明，導致既無法列舉已存在的中繼資料鍵，也難以對齊 EXIF 標準；此外，文件建議的 InPlaceMetadataWriter 在實測中無法順利修改資料。更棘手的是 CR2 與 JPG 雖同樣攜帶 EXIF，但在 WPF 下對應到完全不同的 Query 路徑，增添對應成本。

除 metadata 外，還有效能與相容性問題。以 G9 4000x3000 約 15MB 的檔案為例，全幅解碼後再以 JPEG Encoder 100% 品質輸出，在 Core2Duo E6300（2GB RAM, XP MCE2005 SP2）上需時約 80 秒，明顯偏慢；而雙核心 CPU 也無法充分利用，CPU 使用率多在 50%~60%，即便以兩個 Thread 併行亦然。相較之下，Microsoft 內建的 Codec 與 ThreadPool 配合可發揮全速。此外，Microsoft 的 Viewer 能正常開啟 G2 的 .CRW，但透過 WPF 則會丟出例外，顯示有額外的格式或管線相容性問題待釐清。

在缺乏 MSDN 直接答案的情況下，作者以實驗法逐步找到可行解法。首先，列舉 Metadata Query 的關鍵在於 BitmapMetadata 其實實作了 IEnumerable<string>，可用 foreach 取得所有既有鍵值，填補文件空白；其次，修改 Metadata 可改走 clone-and-encode 流程，即 metadata.Clone() 後修改，最後加回 Encoder，避免 InPlaceMetadataWriter 的不確定性；再次，結合列舉 Query 與社群範例，成功摸索出 EXIF 對應鍵值，包含 CR2 與 JPG 不同的 Query 路徑。效能層面雖無法從 Codec 本身突破，但可藉由重排工作與併行策略，讓非相干工作填滿空閒 CPU 時段，盡量拉高整體吞吐。作者接下來將釋出兩個相關專案（Image Resizer 與記憶卡歸檔工具新版），並在後續文章中整理實作細節與最佳化心得，同時附上既有工具與原始碼連結以供讀者參考。

## 段落重點
### 前言與背景：Canon Raw Codec 1.2 與 WPF 的交會
Canon 釋出 Raw Codec 1.2 後，終於在 Windows XP/Vista 原生殼層中可直接預覽 G9 的 .CR2，長久以來的支援缺口向前邁進。作者希望再更進一步，將這項能力引入 .NET Framework 3.0 的 WPF 工作流程，達成自動化與工具化，應用於影像歸檔與尺寸轉換等場景。雖然 WPF 開發體驗相對友善，但當深入到影像 metadata（尤其是 EXIF）便開始遇到阻礙，主因是官方文件在細節與範例的闕如。此外，Canon Codec 本身的效能疑慮、以及不同格式（CR2、JPG、CRW）在管線中的行為差異，也讓整體整合難度提升。這篇文章作為系列開場，先交代問題樣貌、實驗過程、與初步解法，後續將透過兩個專案逐步完整化整體方案。

### WPF 與 EXIF/Metadata 的實作挑戰
作者遭遇的第一個關卡是 WPF 中的 BitmapSource.Metadata 讀取為 null，事後才發現 WPF 當前版本不提供此屬性實際內容，而是把 Metadata 掛在各 Frame 之上；其次，WPF 內建僅提供少數欄位（如 ApplicationName、CameraModel 等），與 EXIF 實際龐大的欄位集相距甚遠。WPF 引入了「Metadata Query Language」，以類似 XPath 的語法對影像中繼資料讀寫（例如 /ifd/{ushort=1000}），但文件既未提供完整鍵值對照，也未說明如何列舉現有鍵，導致開發者無從下手。更進一步，InPlaceMetadataWriter 名義上可修改 metadata，但作者反覆嘗試無果。最後，CR2 與 JPG 雖同樣承載 EXIF，卻在 Query 鍵值上呈現兩套不相容路徑，讓跨格式的一致化讀寫更為棘手。

### 效能與相容性：慢速解碼、多核未滿載與 CRW 例外
在效能方面，作者以 G9 的 4000x3000（約 15MB）檔案實測，Canon Codec 全幅解碼後經 JPEG Encoder 以 100% 品質輸出，整體花費約 80 秒，對於大量影像處理而言相當吃力。另一方面，多核心處理器未能獲益：在雙核環境中，CPU 使用率約 50%~60%，即便手動開兩個執行緒仍無明顯改善。對照之下，Microsoft 內建 Codec 在 ThreadPool 下能有效跑滿，顯示 Canon Codec 的多工利用仍有空間。相容性上，Microsoft 的 Viewer 可正常檢視 G2 的 .CRW，但 WPF 管線卻丟出例外，暗示在特定舊格式與 WPF 影像解碼堆疊之間存在未解的相容性或解碼器選擇問題，尚待更深入的診斷與回報。

### 解法總結：列舉 Query、繞道修改、對應表摸索與吞吐調度
面對文件不足，作者以實作驗證取得突破。關鍵之一是發現 BitmapMetadata 實作了 IEnumerable<string>，可以直接 foreach 列舉所有現存 Metadata Query 鍵值，快速盤點可用項目，成為後續對應的基礎。針對就地修改失敗的問題，作者改走 metadata.Clone() 後修改，再將結果掛回 Encoder 的流程，成功避開 InPlaceMetadataWriter 的不穩定性。藉由列舉與社群範例的拼湊，作者逐步建立 EXIF 對應關係，包含 CR2 與 JPG 不同 Query 路徑的實務清單。效能上雖無法改善 Canon Codec 的核心速度，但可藉由工作重排、將非相干任務並行、盡量填滿 CPU 空檔來提升整體吞吐，形成「不求單張最快、但求批次完工時間更短」的策略。

### 後續規劃與相關資源：工具發佈與系列文章
本文作為系列前言，紀錄兩週來的踩雷與突破，正式內容將在後續文章與專案釋出中完整呈現。作者計畫同步維護兩個專案：其一是 Image Resizer，聚焦在尺寸轉換、壓縮與批次處理；其二是既有「記憶卡歸檔工具」的新版，將整合 CR2 支援、Metadata 操作與更友善的自動化流程。文末附上多篇既有文章與原始碼連結，包含 CR2 支援更新、Source Code 發布、Release Notes 與 RAW 支援更新等，方便讀者先行參考現有功能與設計脈絡。隨著程式碼調整到可發布的節點，作者將陸續分享細節、最佳實務、以及在 WPF/Codec/Metadata 之間取得平衡的取捨與經驗。

## 資訊整理

### 知識架構圖
1. 前置知識：
- .NET Framework 3.0 與 WPF 影像處理基礎（WIC 概念、BitmapSource/BitmapFrame）
- EXIF/Metadata 基礎知識與常見欄位
- 影像編解碼器（Codec）安裝與系統相依性（XP/Vista）
- 多執行緒與效能調校的基本觀念

2. 核心概念：
- Canon Raw Codec 1.2：在 XP/Vista 啟用 CR2 檢視與解碼的關鍵
- WPF Metadata Query Language：以查詢語法讀寫影像中繼資料（GetQuery/SetQuery）
- BitmapMetadata 與 Frame 級 Metadata：Metadata 不在 BitmapSource，而存在於各 Frame
- CR2 與 JPG EXIF 差異：同一項 EXIF 在兩者的 Query 路徑不同
- 效能與多執行緒限制：第三方 Codec（Canon）效能瓶頸與多核利用率不足

3. 技術依賴：
- 作業系統：Windows XP/Vista
- .NET/WPF 影像架構：Windows Imaging Component（WIC）
- 外部編解碼器：Canon Raw Codec 1.2（啟用 CR2）
- 影像編碼器：JpegBitmapEncoder（輸出 JPG）
- 類別/介面：BitmapFrame、BitmapMetadata（IEnumerable<string>）、GetQuery/SetQuery、InPlaceMetadataWriter（實務不穩）

4. 應用場景：
- 在 WPF 中直接預覽/讀取 Canon CR2 檔案與其 EXIF
- 批次影像縮圖（Image Resizer）與加值性中繼資料處理
- 相機記憶卡歸檔工具：自動化整理、寫入/對齊必要 EXIF
- 建立跨格式（CR2/JPG）相容的 Metadata 讀寫流程

### 學習路徑建議
1. 入門者路徑：
- 安裝 Canon Raw Codec 1.2，確認在 XP/Vista 能瀏覽 CR2
- 在 WPF 載入影像：用 BitmapDecoder 取得 BitmapFrame
- 從 Frame.Metadata 讀取基本欄位，嘗試 GetQuery 基本語法
- 用 JpegBitmapEncoder 輸出基本 JPG，熟悉 I/O 流程

2. 進階者路徑：
- 了解 BitmapMetadata 實作 IEnumerable<string>，學會列舉既有 Query
- 建立 EXIF 對應表：針對 CR2 與 JPG 的 Query 差異設計抽象層
- 評估 InPlaceMetadataWriter 的限制，以 clone+encoder 流程替代
- 建立錯誤處理與降級策略（例如 CRW 無法由 WPF 正常處理時）

3. 實戰路徑：
- 實作批次 Image Resizer：讀 Frame.Metadata → 調整 → clone Metadata → 寫入 Encoder
- 建立多執行緒工作佇列：I/O 與 CPU 工作分離，盡量填滿空閒 CPU
- 效能量測與優化：控制解碼尺寸、平行處理非相依工作、避免不必要全幅解碼
- 建立跨格式（CR2/JPG）一致的 Metadata 讀寫工具組與自動化歸檔流程

### 關鍵要點清單
- Canon Raw Codec 1.2 啟用 CR2 支援：在 XP/Vista 可直接顯示 CR2，為 WPF 處理前提 (優先級: 高)
- Metadata 存在於 Frame 而非 BitmapSource：BitmapSource.Metadata 會是 null，需從每個 BitmapFrame 取用 (優先級: 高)
- WPF Metadata Query Language：以字串路徑（如 /ifd/{ushort=1000}）進行 GetQuery/SetQuery (優先級: 高)
- 列舉既有 Metadata Query：BitmapMetadata 實作 IEnumerable<string>，可直接 foreach 掃描 (優先級: 高)
- CR2 與 JPG EXIF Query 路徑差異：相同 EXIF 欄位在不同格式的 Query 不同，需建立對應表 (優先級: 高)
- InPlaceMetadataWriter 不穩或不可用：實務上改用 metadata.Clone() 後修改再交給 Encoder (優先級: 高)
- JpegBitmapEncoder 融合影像與 Metadata：輸出前將修改後的 Metadata 附加到 Encoder (優先級: 中)
- Canon Codec 效能瓶頸：4000x3000、約15MB 全幅解+100% JPG 可能需數十秒等級 (優先級: 中)
- 多核心利用度不足：Canon Codec 僅約 50-60% CPU 使用率，開多執行緒亦難以線性加速 (優先級: 中)
- 工作佇列與任務分離：將不相依工作並行安排，盡量填滿 CPU 空檔提升整體吞吐 (優先級: 中)
- MS 內建 Codec 表現較佳：在同環境下更快且能從 ThreadPool 受益 (優先級: 低)
- CRW 在 WPF 可能拋例外：MS Viewer 可看 CRW，但 WPF 解時可能異常，需特判或降級處理 (優先級: 中)
- 官方文件不足：多數細節（Query 對應、列舉方式）未明載，需實測與範例佐證 (優先級: 中)
- 專案實踐方向：Image Resizer 與記憶卡歸檔工具，檢驗上述流程與效能 (優先級: 中)
- 自動化目標：在導入 Canon Codec 後，完成 CR2 的讀取、轉檔、Metadata 對齊與批次處理 (優先級: 中)