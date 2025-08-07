# Memory Management (II) ‑ Test Result

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼測試 #03 (原生 x64 執行) 可以連續配置 27 個 72 MB 區塊，而兩個 x86 測試 (#01、#02) 只能配置 2 個就失敗?
因為 64-bit 行程擁有約 8 TB 的使用者模式位址空間，而測試機實際可用的實體記憶體加分頁檔只有 6 GB 左右，遠遠不足以把位址空間塞滿，也就不會因為過度分散 (fragment) 而找不到足夠大的連續空間。  
相反地，x86 行程的使用者位址空間至多 2 GB (或開啟 /LARGEADDRESSAWARE 時為 4 GB)，很快就因為碎片化而找不到 72 MB 以上的連續空間，即使系統總體仍有可用記憶體，配置仍會失敗。

## Q: 在 32-bit Windows 上，為什麼一般應用程式只能使用 2 GB 位址空間？可以把上限提高嗎？
Windows 會把 4 GB 的 32-bit 位址空間一分為二：2 GB 給核心、2 GB 給使用者行程。  
若在 32-bit Windows 啟動時加上 /3GB 開機參數，並且將程式以 /LARGEADDRESSAWARE 編譯連結，核心與行程的比例可調成 1 GB : 3 GB。  
在 64-bit Windows 上執行經 /LARGEADDRESSAWARE 標記的 x86 程式，則可取得完整的 4 GB 使用者位址空間。

## Q: /LARGEADDRESSAWARE 連結器選項是做什麼用的？
此選項把可執行檔標示為「能處理 2 GB 以上位址」。  
• 在 32-bit Windows + /3GB 開機參數時，行程最多可用到 3 GB。  
• 在 64-bit Windows 上執行時，可用到完整 4 GB 的 x86 使用者位址空間。  
若未加此選項，x86 行程不論在 32 或 64-bit OS 上，仍只能使用 2 GB。

## Q: 作業系統為什麼不能幫 C/C++ 程式做記憶體重組 (defragment)？
C/C++ 允許程式直接持有記憶體位址 (pointer)。  
若 OS 私自搬動已配置的區塊，所有先前返回給程式的指標都會失效，程式勢必當場崩潰。因此 OS 只能等待程式自行釋放區塊，無法主動重排。

## Q: 明明系統還有大量可用實體記憶體與分頁檔，為什麼程式仍然收到 Out Of Memory？
當行程的虛擬位址空間本身很小 (如 2 GB) 又被配置得七零八落時，可能已經找不到足夠大的連續區段來滿足新的配置請求，導致 malloc/new 失敗。即使整體空間總量還夠，只要沒有「一大塊連續空間」，就會出現 Out Of Memory。

## Q: .NET、Java 這類有 Garbage Collection 的執行環境會遇到同樣的碎片問題嗎？
機率大幅降低。  
GC 執行時可以搬動存活物件並壓縮 (compact) 堆，因此比較不容易因位址空間碎片而配置失敗。作者表示將在下一篇文章實際驗證。