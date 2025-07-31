---
applyTo: '_posts/*/*.md'
---

收到批次作業需求，請按這步驟建立任務清單並隨時更新進度。
請勿違背這處理原則，不要因為要加速就一次處理多個步驟。我要確保進行中的步驟都有正確在 _tasks.md 上記載，以防處理到一半中斷下次能接續處理，或是知道停在哪邊。

_tasks.md, _tasks.log, 這兩個檔案統一放置於 _site 目錄下。

# 批次作業任務規則

若任務中斷或重新啟動，請以這檔案的內容為準接續處理。
若單一步驟做到一半就不明原因中斷，請重新執行該步驟。確認已完成的不用重作。
任何要求的批次作業，在 _tasks.md 建立完成, 開始處理第一筆之前請先跟我確認無誤後再開始。

步驟以單一部落格文章檔案的處理為單位。用檔名當作 id，請勿加上其他我沒有提及的 todo items.

1. 建立 _tasks.md, 每次批次作業任務都用一個新的段落 ( ## ) 開始，摘要這次任務當作 title, 並且標上目前時間
2. 紀錄原始 requirement / instructions / prompt
3. 先展開所有需要處理的步驟, 建立 checklist: `- [ ] {filename}`
4. 當處理每個檔案時，請依照以下規則更新 checklist：
   - 當開始處理時, 將 checklist 改為 `- [ ] {filename}` (processing )
   - 當處理失敗時, 將 checklist 改為 `- [ ] {filename} (failed)`
   - 當處理成功時, 將 checklist 改為 `- [x] {filename} (success)`
5. 處理過程, 請記錄流水帳至 _tasks.log, 標記時間跟 filename

若下次不明原因重新處理, 請沿用同樣的 instructions, 及同樣的檔案清單, 從第一個非 success 的檔案開始處理。
