# Disqus URL Map Requirement


## 目的

我的部落格異動，從中文檔名 -> 英文檔名, 會影響到外部存取的 URL
因此需要在 Disqus 上設定 URL 映射，讓舊的 URL 可以正確導向到新的 URL。

這次 URL 遷移過後，我需要對照新舊的 URL, 按照 Disqus 的格式，建立一個 URL 映射檔案, 並且匯入 到 Disqus, 以確保所有舊的連結都能正常運作。

## 步驟

1. 收集所有舊的 URL 和對應的新 URL。
2. 根據 Disqus 的格式，建立一個 CSV 檔案，包含舊的 URL 和新的 URL。
3. 登入 Disqus，進入管理後台。
4. 尋找 URL 映射的設定選項，並匯入剛剛建立的 CSV 檔案。
5. 測試舊的 URL 是否能正確導向到新的 URL。
6. 確認所有映射都已成功建立，並且沒有錯誤。

## 作法說明

1. **收集 URL**: 使用網站分析工具或手動檢查，列出所有舊的 URL 和對應的新 URL。

按照 #file .github/instructions/content-format.instructions.md 的說明:
- 檔案路徑: _posts/{year}/{year}-{month}-{day}-{slug}.md
- 發布網址: https://columns.chicken-house.net/{year}/{month}/{day}/{slug}/
- 所有會自動轉導的網址: 存放在 .md 內的 yaml front matter 的 `redirect_from` 欄位 (相對路徑, 從 / 開始)

第一步需要寫 python script, 匯出 csv 檔案。第一個欄位是舊網址 (也就是 redirect_from 欄位的內容)，第二個欄位是新的網址 (發布網址)。所有文章的資訊收到同一個 csv 內即可


2. **合併 Disqus URL 映射檔案**: 

Disqus 後臺即可匯出。包含舊網址 (新網址空白，讓你自己填)。
我會手動操作這步驟，提供給你一個已有所有舊網址的 .csv 檔案，然後你可以根據這個檔案，將新的網址填入。

csv 片段內容如下:

```csv
https://columns.chicken-house.net/2015/12/27/dnxcore50_02_memfrag_test/,
https://columns.chicken-house.net/2005/03/06/%e6%96%b0-17-lcd-monitor/,
https://columns.chicken-house.net/2004/12/15/%e4%b8%89%e5%80%8b%e5%a5%bd%e7%94%a8%e7%9a%84-asp-net-httphandler/,
https://columns.chicken-house.net/2004/12/31/%e9%90%b5%e5%bc%97%e9%be%8d%e8%86%a0%e5%b8%b6/,
https://columns.chicken-house.net/2005/01/09/text-%e7%9a%84%e7%b7%a8%e8%bc%af%e4%bb%8b%e9%9d%a2%e8%a3%9c%e5%bc%b7-%e8%87%aa%e5%b7%b1%e7%88%bd%e4%b8%80%e4%b8%8b/,https://columns.chicken-house.net/2005/01/09/spam-information/
https://columns.chicken-house.net/2005/01/08/%e5%9e%83%e5%9c%be%e8%b3%87%e8%a8%8a/,
```

較為麻煩的是:
1. Disqus 的 URL 映射檔案，網址若包含中文字元，可能會用 url encoding 方式處理。
2. Disqus 提供的舊網址 old_url2, 與步驟 (1) 的 old_url1 其中可能會有 +-5 天的誤差 (當時發布可能手動調整過時間)，因此需要對照新網址的發布時間，找出對應的舊網址。old_url1 / old_url2 配對的條件是:
   - old_url1 的發布時間 (year, month, day) 與 old_url2 的發布時間差距在 5 days 以內。
   - old_url1 的 slug 與 old_url2 的 slug 相同。


這步驟你需要寫第二個 python script，執行下列步驟 (我用 psuedo code 說明):

```psuedo

for each row in csv:
    old_url = row[0]
    new_url = row[1]
    
    # 從 (1) 的 csv, 解碼處理 url encoding 後，按照 old_url 找到對應的新網址 target_url
    # 將對應出來的 new_url 填入 csv 檔案第二欄位


```