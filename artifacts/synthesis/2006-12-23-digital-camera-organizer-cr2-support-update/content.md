CR2-Supported.aspx/
  - /post/2006/12/23/e6adb8e6aa94e5b7a5e585b7e69bb4e696b0---CR2-Supported.aspx/
  - /post/e6adb8e6aa94e5b7a5e585b7e69bb4e696b0---CR2-Supported.aspx/
  - /columns/2006/12/23/e6adb8e6aa94e5b7a5e585b7e69bb4e696b0---CR2-Supported.aspx/
  - /columns/e6adb8e6aa94e5b7a5e585b7e69bb4e696b0---CR2-Supported.aspx/
  - /blogs/chicken/archive/2006/12/23/2020.aspx/
wordpress_postid: 197
---

嗯, 我沒 Canon DSLR 的人, 跟人家在湊什麼熱鬧... 前陣子聽說小熊子買了 5D, 真是夢幻機種啊... 被問到支不支援 .CR2 .. 阿災, 我也沒 sample file 可以試...

後來公司大老闆剛好有帶他的相機 20D, 拍了幾張當 sample, 就回來改 code 了... 結果還挺樂觀的, Microsoft 包的那套 wrapper 通通都吃, 而且 library 的用法也都一樣, 唯獨 .CR2 的檔案不會附帶一個 .thm 的縮圖檔案, 因此 RAW file 轉存的 .JPG 就沒有包含完整的 exif 了.

不過高級的相機還存什麼縮圖? 當然不會這麼小家子氣... 哈哈, 需要的話, Canon DSLR 就直接再幫你存一張原圖大小的 .JPG 檔了. 這麼一來, 再自己做一次 .CR2 -> .JPG 好像也沒意義了, 因此這個工就省下來, 不理它...

這次修改沒動到多少地方, 簡單列一下 update:

1. MediaFilerFileExtensionAttribute 對應的 file extension 格式調整, 改為可以用 , 來指定多個副檔名. 調整後同時也調整 Factory Patterns 的 Create( ), 讓一個 MediaFiler 可以同時處理一個以上的副檔名.
2. 因應新的副檔名支援, configuration file 也多了一段: pattern.cr2
3. 沒了...

最後感謝小熊子買了新相機讓我更崇拜了一下, 哈哈... 公司老大提供 sample 檔也是要感謝一下啦.. 更新的檔案下載: [[HERE](http://www.chicken-house.net/files/chicken/ChickenHouse.Tools.DigitalCameraFiler.Binary.zip)]

---

小抱怨一下, 不知道是我的 G2 搞怪還是怎樣, 想不通到底是啥原因... 我的 G2 拍 RAW file 時, 如果接了外閃, 同時拍照時外閃又剛好來不及回電沒有打出來.. 那麼拍出來曝光不足的 RAW file, 在相機裡 preview 就正常, 傳到電腦用 Microsoft Raw Image Viewer 就解不出來, 當然用它的 library 也不行, 會有 exception ... 是怎樣? :@ 嫌我相機 & 閃光燈太爛嘛...