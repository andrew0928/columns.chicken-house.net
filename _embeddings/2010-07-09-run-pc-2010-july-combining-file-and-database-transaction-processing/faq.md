# [RUN! PC] 2010 七月號 - 結合檔案及資料庫的交易處理

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 要如何把檔案系統的異動與資料庫的異動整合成同一個交易？
透過 Transactional NTFS (TxF) 搭配 .NET 的 TransactionScope，就能把檔案與資料庫的操作納入單一交易流程中。

## Q: Transactional NTFS (TxF) 目前是否已被 .NET Framework 原生支援？
尚未被 .NET Framework 正式納入原生支援，因此需要額外工具或函式庫才能在 .NET 中使用。

## Q: 如果想在 .NET 程式中簡化 TxF 的使用，有什麼現成函式庫可協助？
可以使用 AlphaFS，這個函式庫已將 TxF 的相關操作封裝，降低整合難度。

## Q: AlphaFS 的定位與功能特色是什麼？
AlphaFS 旨在取代 System.IO.*，並額外支援多項 NTFS 進階功能，例如 VSS、HardLink 以及 TxF 等。

## Q: 相較於自行撰寫 P/Invoke，使用 AlphaFS 整合 TxF 有何優點？
使用 AlphaFS 不必再手動撰寫繁瑣的 P/Invoke 程式碼，能夠更快速、簡潔地在 .NET 中使用 TxF。

## Q: 文中範例程式碼可以在哪裡下載？
範例程式可從以下網址取得：/wp-content/be-files/RunPC-201007.zip