# 同場加映: 用 Synology NAS 的 Docker 環境，執行 .NET Core CLR Console App

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 在 Synology NAS 上執行 .NET Core CLR Console App 時，應該下載哪一個 Docker image 與 tag？
作者使用的 image 為 「microsoft/aspnet」，並指定 tag「1.0.0-beta8-coreclr」。

## Q: 建立 Container 時，作者把 NAS 的哪個資料夾掛載到 Container 內的哪個路徑？
把 NAS 上的「/docker/netcore」資料夾以可寫入 (ReadOnly 取消) 方式掛載到 Container 內的「/home」路徑。

## Q: 部署完成後，要在 Container 內啟動 Console App 需要執行哪兩個主要指令？
1. dnu restore (下載並還原相依套件)  
2. dnx HelloCoreCLR.dll (實際執行程式)

## Q: 整個 .NET Core CLR Docker 環境大約佔用多少記憶體？
作者實測只佔用約 6 MB 記憶體，非常省資源。

## Q: 不是所有 Synology 機種都支援 Docker，官方指出哪些系列（以 Intel CPU 為主）可使用？
根據文中引用的官方清單，16-、15-、14-、13-、12-、11-、10-系列中搭載 Intel CPU 的 Plus／xs／xs+／RP 型號才支援 Docker，例如 DS1815+、RS3614xs、DS3615xs、DS1513+ 等。購買前建議先到 Synology 官網確認支援名單。