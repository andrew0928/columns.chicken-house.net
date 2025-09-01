e8a898e686b6e58da1e6adb8e6aa94e5b7a5e585b7.aspx/
  - /post/2006/11/03/Canon-Digital-Camera-e79bb8e6a99fe78da8e4baab---e8a898e686b6e58da1e6adb8e6aa94e5b7a5e585b7.aspx/
  - /post/Canon-Digital-Camera-e79bb8e6a99fe78da8e4baab---e8a898e686b6e58da1e6adb8e6aa94e5b7a5e585b7.aspx/
  - /columns/2006/11/03/Canon-Digital-Camera-e79bb8e6a99fe78da8e4baab---e8a898e686b6e58da1e6adb8e6aa94e5b7a5e585b7.aspx/
  - /columns/Canon-Digital-Camera-e79bb8e6a99fe78da8e4baab---e8a898e686b6e58da1e6adb8e6aa94e5b7a5e585b7.aspx/
  - /blogs/chicken/archive/2006/11/03/1914.aspx/
wordpress_postid: 213
---

用數位相機的人或多或少都有這困擾吧? 不用底片錢, 也不用洗出來, 相機拿起來就是拼命拍... 拍完後, 不要說後製作了, 光是把相片檔案歸檔就有點麻煩...

"我久久才 copy 一次照片, 要照日期分目錄真麻煩"

"video 檔歸檔也麻煩"

"直拍的照片要轉 90' 得一張一張看.."

"兩台相機檔名重覆... " <--- 這個大概只有我會碰到吧, 我家的相機都是 canon ...

"...."

這些問題, 其實都有很好的工具可以解決, Google 的那套 Picasa 就很棒, 不然 Adobe 的 Album, AcdSee 也都有 solution ...

不過我就是不想裝一些五四三的啊... 看照片我都只用 windows xp 內建的 image viewer, 我只缺一個很簡單的工具, 把記憶卡的照片檔案自動搬到我要的目錄就好... 可以的話我甚至不要 windows 介面的, 可以用命令列執行的更棒... (我果然是老人.. :~~~~)

最後是自己寫一個來用... 過去是寫簡單的批次檔就搞定, 也用了兩年了, 成效很好, 我就直接把內容貼出來, 有需要的人可以拿去用...

```batch
set DATETEXT=%DATE:~0,4%-%DATE:~5,2%%DATE:~8,2%
if not "%2"=="" set DATETEXT=%2 

set TRGDIR="c:\Photos\%DATETEXT% [%1]\"
md %TRGDIR% 

@echo "處理 F:\DCIM 的照片..."
@ for /R F:\DCIM %%f in (*.jpg) do @echo 移動照片中... %%f && @move /-Y %%f %TRGDIR% > nul
@ for /R F:\DCIM %%f in (*.crw) do @echo 移動照片中... %%f && @move /-Y %%f %TRGDIR% > nul
@ for /R F:\DCIM %%f in (*.avi) do @echo 移動影片中... %%f && @move /-Y %%f "c:\videos\input [dc-avi]\%DATETEXT% [%1 #%%~nf].avi" > nul
@ for /R F:\DCIM %%f in (*.thm) do @echo 刪除影片縮圖... %%f && @del /f /q %%f > nul
```

批次檔的方式已經可以解決這些問題:

1. 依日期命名, 像這樣的格式:  
   c:\photos\2006-0101 [去公園]\IMG_9999.jpg
   
2. 因為我有另外處理 video file 的動作, 因此 avi 檔會另外分開放, 格式為:  
   c:\videos\2006-0101 [去公園 #MVI_9999].avi
   
3. 只要執行這指令, 檔案就都歸好了:  
   copypic.cmd 去公園  
   或是自己指定日期...  
   copypic.cmd 去公園 2006-0101

不過用起來還是有一點小缺點:

1. 日期判定不精確, 因為只寫批次檔的話, 我找不到方法把檔案日期切一段出來... 因此歸檔的檔名只能用 copy 時的日期來算... 常常白天拍, 晚上過十二點哄完小孩才來 copy, 日期就差一天

2. 因為 (1), 累積了好幾天的照片只能混在一起, 分不開

3. 沒辦法以相機名稱命名, 兩台相機照出來的檔名常打架

4. 要自動轉正

像是要讀取 EXIF 的部份, 要光靠批次檔真的是太勉強了... 本來想寫個小工具搭配批次檔用, 不過發現花的工夫跟本差不多... 就直接寫了一個小工具 [DigitalCameraFiler.exe], 取代掉上面的批次檔了..

需要的人可以下載去用, 不過喜歡用命令列的人應該不多吧... 哈哈... 用法很簡單... 請先確定你的電腦有安裝 Microsoft .Net Framework 2.0... 安裝設定的方式:

1. 編輯設定檔: DigitalCameraFiler.exe.config

```xml
<?xml version="1.0" encoding="utf-8" ?>
<configuration>
 <appSettings>
  <add key="default.title" value="未定標題"/>
  <add key="video.targetPattern" 
   value="c:\video\{0:yyyy-MMdd} [{1} #{4}].avi" />
  <add key="general.targetPattern" 
   value="c:\photos\{0:yyyy-MMdd} [{1}]\{3}" />
  <add key="photo.targetPattern" 
   value="c:\photos\{0:yyyy-MMdd} [{1}]\{2} #{3}" />
  <add key="arguments" 
   value="LastWriteTime,Title,Model,Name,FileNameWithoutExtension"/>
 </appSettings>
</configuration>
```

default.title: 預設的主題, 執行時沒給 title 的話就用這個代替  
video.targetPattern: 放 *.avi 檔的位置, 其中 {0} {1} .. 會用最後面的 arguments 依序代替  
general.targetPattern: 放 *.crw 檔的位置  
photo.targetPattern: 放 *.jpg 檔的位置

2. 執行時, 打開 DOS Prompt, 切到目錄下, 執行:  
   DigitalCameraFilter.exe F:\ 公園外拍  
   其中, F:\ 是指你記憶卡的路逕, "公園外拍" 是主題

photo 為例, 最後檔案會被歸到:

c:\photos\2006-1102 [公園外拍]\Canon PowerShot G2 #IMG_1234.jpg

大概就是這樣, 自己寫來用的, 覺的好用的話就鼓勵一下吧 :D

[下載程式](http://www.chicken-house.net/files/chicken/ChickenHouse.Tools.DigitalCameraFiler.Binary.zip)