# Memory Management (III) ‑ .NET CLR ?

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 在 .NET 上執行同樣的記憶體配置/釋放實驗，預設的 CLR 垃圾回收是否能解決記憶體破碎 (fragment) 問題？
不行。作者實測在 .NET 2.0 (x86) 預設設定下，釋放掉的 768 MB 記憶體只回收了 72 MB，仍無法再配置較大的 72 MB 連續區塊，顯示破碎問題依舊存在。

## Q: 問題的根源為什麼在「指標 (pointer)」？
因為只要程式握有物件的絕對位址，執行期就無法任意搬移記憶體區塊 (relocation)；一旦位置改變，所有指標都會失效。C/C++ 必須保留物件原位，導致容易產生破碎。若拿掉指標、只留下「參考 (reference)」，執行期便能安全地移動物件並重新定址。

## Q: 什麼是 compact collection？
它是一種垃圾回收模式：在回收時不僅釋放無用物件，還會把存活物件搬移並集中擺放，以消除破碎並釋放出較大的連續可用區塊。

## Q: .NET CLR 什麼時候會做 compact collection？  
在啟用 Server GC (設定檔 `<gcServer enabled="true"/>`) 時，CLR 會進行 compact collection；作者的測試證實 Server GC 能成功消除破碎並重新配置更大的記憶體區塊。

## Q: 關閉 Concurrent GC (`<gcConcurrent enabled="false"/>`) 是否能改善破碎？  
沒有。作者測試關閉後效果仍然不佳，可用記憶體幾乎沒有增加，證明破碎問題與 Concurrent GC 無直接關係。

## Q: 要如何在應用程式中啟用 Server GC？  
在應用程式的組態檔 (app.config 或 web.config) 的 `<runtime>` 區段加入：  
```xml
<gcServer enabled="true" />
```
重新啟動程式後即可使用 Server GC。

## Q: 啟用 Server GC 後測試結果有何改善？  
釋放 576 MB 後，便能重新配置 648 MB 的 72 MB 連續區塊；記憶體破碎問題消失，符合 compact collection 的預期效果。