e7b582e696bce6909ee5ae9ae5a4a7e59c96e7b6b2e59d80e98cafe8aaa4e79a84e5958fe9a18c.aspx/
  - /post/2008/05/21/FlickrProxy-3---e7b582e696bce6909ee5ae9ae5a4a7e59c96e7b6b2e59d80e98cafe8aaa4e79a84e5958fe9a18c.aspx/
  - /post/FlickrProxy-3---e7b582e696bce6909ee5ae9ae5a4a7e59c96e7b6b2e59d80e98cafe8aaa4e79a84e5958fe9a18c.aspx/
  - /columns/2008/05/21/FlickrProxy-3---e7b582e696bce6909ee5ae9ae5a4a7e59c96e7b6b2e59d80e98cafe8aaa4e79a84e5958fe9a18c.aspx/
  - /columns/FlickrProxy-3---e7b582e696bce6909ee5ae9ae5a4a7e59c96e7b6b2e59d80e98cafe8aaa4e79a84e5958fe9a18c.aspx/
  - /blogs/chicken/archive/2008/05/21/3245.aspx/
wordpress_postid: 104
---

由於在使用 Flickr API 時, 老是碰到上傳成功後, 結果拿到的照片 URL 不能看的問題... 被它整了好久, 不過總算解決了 @_@... 原來 API 拿到的資料是錯的, 嘖...

說來話長, 不過既然花時間解決了就要記錄一下... 問題大概是這樣. 上傳照片完成之後可以拿到 photoId, 代表某一張放在 Flickr 上的照片. 之後透過 PhotosGetInfo(photoId) 這個 API 可以取得這張照片的相關資訊, 當然也有 MediumUrl, LargeUrl... 等等 properties 可以用.

很直覺嘛, 要秀大圖我就直接拿 LargeUrl 就好, 偏偏有時是好的, 有時是壞的... API 傳回來的東西應該不會錯吧? 我心裡是這樣想的. 不過跟 Flickr 網站的 url 對照一下才發現, 竟然有時是不同的... 一路追下去, google 跟作者在 codeplex 網站上的 forums 都找了, 才發現...

PhotosGetInfo( ) 抓到的只是一堆 ID, 然後用 Flickr 公布的網址格式 "湊" 出各種 URL. 然而過去 Flickr 層經有一次改變部份網址的格式, 當你的圖檔不是很大時, Flickr 判定沒有另外存一張大圖的需要了, 就直接跳到原圖 (original size). 而原圖的網址格式又不一樣, 因此當圖檔太小時, API 抓到的 LargeUrl 就會是錯的...

My God,.... 為了這種鳥問題害我多白了好幾根頭髮... 找到原因後找 solution 就簡單了. 因應這個問題, 也多了一組 API: PhotosGetSizes( ), 直接連回 Flickr 明確的查詢可用的 size 有幾種, 連同它的網址及一堆相關資訊一起傳回來... 改用這個 API 傳回的資訊, 結果就正確了, 沒有圖掛掉的問題... Orz

不能怪人家 API 寫的不好, 只能怪自己功課沒作足... 不看文件直接拿 API 就用, 看名字猜用法才會這樣.. code 改一改就 ok 了, 少了這個不確定性, 原本畫蛇添足加上去的確認圖檔的動作也不用了.. 貼一下修改前跟修改後的 code:

**使用 PhotoInfo 物件 (可能會出現 photo not available)**

```csharp
PhotoInfo pi = flickr.PhotosGetInfo(photoID);
string flickrURL = null;
string size = null;
try
{
    flickrURL = this.CheckFlickrUrlAvailability(pi.MediumUrl);
    size = "medium";
    flickrURL = this.CheckFlickrUrlAvailability(pi.LargeUrl);
    size = "large";
    flickrURL = this.CheckFlickrUrlAvailability(pi.OriginalUrl);
    size = "original";
}
catch { }
```

**改用 PhotosGetSizes( ) API**

```csharp
foreach (Size s in flickr.PhotosGetSizes(photoID).SizeCollection)
{
    XmlElement elem = null;
    elem = cacheInfoDoc.CreateElement("size");
    elem.SetAttribute("label", s.Label);
    elem.SetAttribute("source", s.Source);
    elem.SetAttribute("url", s.Url);
    elem.SetAttribute("width", s.Width.ToString());
    elem.SetAttribute("height", s.Height.ToString());
    cacheInfoDoc.DocumentElement.AppendChild(elem);
}
```

嗯, 終於搞定. FlickrProxy 正式邁入實用的階段... 收工!