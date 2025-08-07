# FlickrProxy #4 - 修正同步上傳的問題

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 這次 FlickrProxy 改版主要解決了什麼 Bug？
當同一張照片第一次被要求下載時，如果上傳到 Flickr 尚未完成又來第二個相同的下載 Request，程式會把同一張照片上傳兩次。此次改版就是為了修正這個「同步上傳造成的重複上傳」問題。

## Q: 作者最初採用的解法是什麼？為何仍有疑慮？
作者先將「是否需要上傳」與「建立 Flickr 副本檔」兩段核心程式碼包在  
```csharp
lock(this.GetType()) { ... }
```  
裡，確保同一時間只有一個執行緒能執行這段程式碼。雖然可避免重複上傳，但鎖定範圍過大，連下載不同照片的 Request 也被阻塞，導致效能不佳。

## Q: 改善後如何只鎖定同一張照片的 Request？
作者為每張照片動態產生「專屬鎖物件」，做法是在 LockHandle 屬性中用檔案的雜湊值 (hash) 當索引，將 object 實例存進 Dictionary，再對該 object 做 lock：  
```csharp
lock(this.LockHandle) { ... }
```  
如此只有同一張照片的 Request 彼此等待，不同照片可同時處理。

## Q: 如果同一頁面一次要上傳許多新照片，還會遇到什麼問題？
多張照片同時上傳會佔用大量頻寬，也可能因瞬間開出過多連線而被 Flickr 關切，因此需要限制「同時上傳」的數量。

## Q: 程式如何限制同時上傳的數量？
作者示範使用 Semaphore：  
```csharp
public static Semaphore FlickrUploaderSemaphore = new Semaphore(2, 2); // 只允許 2 個並行上傳
...
FlickrUploaderSemaphore.WaitOne();
photoID = flickr.UploadPicture(this.FileLocation);
FlickrUploaderSemaphore.Release();
```  
如此可保證任一時間最多僅有 2 個上傳動作進行。

## Q: 為什麼 lock 不適合用來限制「允許 2 個以上」的並行上傳？
lock 只能保證「一次僅 1 個執行緒」進入臨界區；若需求是「同時允許 N 個執行緒」(例如 2 個上傳) 就必須使用能計數的同步物件，而 Semaphore 正好提供這項功能。