---
applyTo: 'docs/_posts/*/*.md'
---

收到批次作業需求，請按這步驟建立任務清單並隨時更新進度。
請勿違背這處理原則，不要因為要加速就一次處理多個步驟。我要確保進行中的步驟都有正確在 _tasks.md 上記載，以防處理到一半中斷下次能接續處理，或是知道停在哪邊。

_tasks.md, _tasks.log, 這兩個檔案統一放置於 /_migration 目錄下。

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

# 整體任務處理原則

請先判定 terminal 環境是 Linux 還是 Windows, 並且依照以下原則處理。
我觀察到你的習性常常會在 wsl 下嘗試使用 \\wsl.local\Ubuntu\home\{username} 的路徑, 這是錯誤的, 請不要這樣做。

在 Linux 環境下, 請使用 /home/{username} 的路徑。
在 Windows 環境下, 請使用 C:\Users\{username} 的路徑。

若下次不明原因重新處理, 請沿用同樣的 instructions, 及同樣的檔案清單, 從第一個非 success 的檔案開始處理。若碰到 processing 的項目, 請先將其改為 failed 後再重新處理。

你可以把 _tasks.md 當作任務筆記, 如果你處理過程中除了 checklist 外還有其他需要記錄的事項, 請在 _tasks.md 中新增段落 (##) 記錄。

若批次作業順利全部完成, 或是決定放棄重新建立新的批次作業, 請用 requirement 的意圖 (縮減至 3 個英文單字內) 當作 title 將 _tasks.md 重新命名為 _tasks_{title}_{date}.md, 重新啟動新的批次作業。

我知道要處理的檔案很多，這些內容我都確認過無法用自動化工具處理 (或是產生 python code 處理也一樣)，請務必依照這些步驟手動處理。