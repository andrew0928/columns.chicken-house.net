# Canon Raw Codec 1.3 Released !

# 問答集 (FAQ, frequently asked questions and answers)

## Q: Canon RAW Codec 1.3 主要新增了哪些相機機種的支援？
它新增了對 EOS Kiss X2 / EOS DIGITAL REBEL XSi / EOS 450D 的 RAW 檔 (.CR2) 解析支援。

## Q: 這次 1.3 版是否有提到效能提升或 x64 系統的支援？
沒有。更新說明中既未提到效能改進，也未提及何時會提供 64 bit（x64）支援。

## Q: 要到哪裡下載 Canon RAW Codec 1.3？下載時需要注意什麼？
請到 Microsoft Pro Photo 官方下載頁  
http://www.microsoft.com/prophoto/downloads/tools.aspx  
在「OS」下拉選單選擇「Windows Vista」，就會看到 Canon RAW Codec 1.3 的下載連結。

## Q: Canon RAW Codec 1.3 與 Microsoft Pro Photo Tools 相容嗎？
不相容。更新說明明確指出 1.3 版會與 Microsoft Pro Photo Tools 衝突，使用該工具的用戶不建議升級。

## Q: 如果安裝 1.3 版後出現程式無法運作，該怎麼辦？
作者實測後已將系統還原回 1.2 版，並指出只有最早的 1.2 安裝檔（檔名 RC120UPD_7L.EXE）能與其歸檔程式正常運作；新版 1.2（CRC120UPD_7L.EXE）及 1.3 皆會出現問題。

## Q: 使用 .NET 3.0 + WPF 應用程式的使用者是否建議更新到 1.3？
不建議。由於 1.3 版與 Microsoft Pro Photo Tools（以 .NET 開發）不相容，任何大量使用 .NET 3.0 + WPF 的環境都可能出現衝突，建議暫時不要升級。