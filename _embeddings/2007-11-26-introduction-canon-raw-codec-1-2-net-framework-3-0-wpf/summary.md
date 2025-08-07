# 前言: Canon Raw Codec 1.2 + .NET Framework 3.0 (WPF)

## 摘要提示
- Canon Raw Codec 1.2: 新版 Codec 讓 G9 拍攝的 .CR2 能在 XP/Vista 直接預覽，跨出相容性關鍵一步。  
- WPF 與 Metadata: WPF 只暴露 Frame 層級 Metadata，BitmapSource.Metadata 取回皆為 null，成為開發第一道障礙。  
- Metadata Query Language: 必須透過 GetQuery/SetQuery 以路徑字串存取欄位，但官方未提供完整對照表。  
- 列舉技巧: BitmapMetadata 其實實作 IEnumerable<string>，可用 foreach 列出所有既有 Query。  
- Metadata 寫入困境: 文件推薦 InPlaceMetadataWriter，實測仍無法成功改寫，暫以 clone-modify-reencode 規避。  
- EXIF 差異: CR2 與 JPG 採用不同 Query 名稱，需分開處理才能正確讀寫。  
- 效能瓶頸: 4000×3000、15 MB CR2 全幅解碼＋JPEG 編碼需 80 秒，雙核心僅 50–60 % 利用率。  
- 多執行緒落差: Canon Codec 很難吃滿 CPU，反觀 Microsoft 內建 Codec 可在 ThreadPool 下跑滿核心。  
- 解決策略: 以工作排程方式把非關鍵 Job 併排執行，盡量填滿空閒運算資源。  
- 後續計畫: 完成 Image Resizer 與歸檔工具兩個專案後，將撰寫系列文章詳述實作心得。

## 全文重點
作者為了解決 Canon G9 相機 .CR2 檔在 Windows 環境下的管理與自動化需求，開始研究 Canon Raw Codec 1.2 與 WPF 結合的可行性。新版 Codec 雖已能在 XP / Vista 直接顯示 RAW，卻帶來一連串與 Metadata 相關的技術難題。首先，WPF 僅在 BitmapFrame 暴露 Metadata，BitmapSource.Metadata 永遠為 null；其次，官方只提供不到十個屬性，完全不足以覆蓋 EXIF 上百個欄位。再加上 Canon 的 CR2 與一般 JPG 在 Metadata Query 名稱上並不一致，使得讀寫過程更形複雜。  
為了找出解法，作者翻遍 MSDN 仍無所得，只能靠「土法煉鋼」反覆嘗試。最終發現 BitmapMetadata 其實實作 IEnumerable<string>，只要用 foreach 便能列舉所有現存 Query，進而找出欄位對應關係；而修改 Metadata 則先以 clone() 取得副本、更新後再塞回 Encoder，以規避 InPlaceMetadataWriter 的限制。  
除了 Metadata，效能亦是一大痛點。一張 4000×3000、15 MB 的 CR2 全幅解碼並以最高品質轉成 JPG，在 Core2Duo E6300 + 2 GB RAM 的機器上需 80 秒，且雙核心僅能發揮六成效能；就算手動開兩條 Thread 亦無改善，顯示 Canon Codec 在多執行緒優化不足。相較之下，Microsoft 內建 Codec 能在 ThreadPool 下跑滿核心，速度與併發性都優於 Canon。  
歷經兩週摸索，主要問題已陸續拆解；接下來作者將把經驗整理成系列文章，並同步完成兩個示範專案—Image Resizer 與記憶卡歸檔工具—分享給有相同需求的開發者。

## 段落重點
### 整合背景與動機
Canon 推出 Raw Codec 1.2 後，G9 的 .CR2 檔終於能在 XP／Vista 原生預覽，作者遂著手研究以 WPF 建立自動化處理流程。雖然 WPF 開發體驗良好，但官方文件對 RAW 與 Metadata 的描述零散，導致在實務整合時不斷碰壁。文章首先交代研究動機、環境與先前踩過的坑，說明為何必須深入剖析 Canon Codec 與 WPF Metadata 機制。

### Metadata 疑惑與技術難題
核心難題集中於 Metadata：BitmapSource.Metadata 取回為 null、官方僅揭露少數欄位、需使用類似 XPath 的 Metadata Query Language 存取、文件未列舉現成 Query、InPlaceMetadataWriter 無法如宣稱般改寫資料，以及 CR2 與 JPG 不同的 Query 對應。這些問題讓作者在 EXIF 讀寫上寸步難行，只能透過試誤法逐一拆解。

### 效能與多執行緒問題
Canon Codec 在效能與併發性上表現不佳：單張 15 MB CR2 解碼加轉檔耗時 80 秒，雙核心僅 50–60 % 使用率；開多 Thread 效益亦有限。與此相比，Microsoft 內建 Codec 於 ThreadPool 下可完全吃滿 CPU，速度顯著較快。作者暫以「將不相干 Job 併排」的方式，把空閒核心利用率最大化，同時期待 Canon 未來版本改進。

### 暫行解法與未來方向
經反覆測試後，作者找到數個 workaround：透過 BitmapMetadata 實作的 IEnumerable<string> 列舉現有 Query；利用 metadata.clone() 改寫再重編碼取代 InPlaceMetadataWriter；隨機搜尋與社群範例拼湊出 CR2 與 JPG 的 Query 對照表。主要障礙已排除，後續將撰寫詳細教學並發布 Image Resizer 與記憶卡歸檔工具兩項專案，延伸並整合既有的多篇舊文與範例，供讀者下載試用。