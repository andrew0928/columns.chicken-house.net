# Canon RAW Codec for Vista 出來了..

# 問題／解決方案 (Problem/Solution)

## Problem: WPF/WIC 在 Vista 中無法讀取 Canon 相機 RAW 檔 (.CR2)

**Problem**:  
在 Windows Vista 上開發以 WPF 為基礎的相片瀏覽／編輯工具時，只要開啟或顯示 Canon DSLR 產生的 .CR2（RAW）檔案便會失敗；檔案總管也無法產生縮圖。所有依賴 Windows Imaging Component (WIC) 的應用程式皆面臨同樣困境，導致工作流程被迫先將 RAW 轉成 JPEG/TIFF，既耗時又破壞無失真的編輯鏈。

**Root Cause**:  
1. WIC 本身只提供影像解碼框架，實際格式支援需透過外掛 Codec。  
2. Canon 遲至 2007/3/30 才針對 Vista 發佈「Canon RAW Codec for Vista」，在此之前 Vista 並無可用的 .CR2 解碼器，因此任何 WIC-based App 均無法開啟 .CR2。  

**Solution**:  
安裝「Canon RAW Codec for Vista」。安裝完成後：  
• WIC 會自動註冊該 Codec，所有 WPF / Win32 / .NET 應用不需任何程式碼變更即可讀取 .CR2。  
• Windows Explorer 能生成縮圖及預覽，搜尋索引亦可擷取 EXIF。  

Sample Code (WPF)：  
```csharp
// 只要系統已安裝 Codec，下列程式即可直接載入 .CR2
string path = @"C:\Photo\IMG_1234.CR2";
BitmapSource src = BitmapFrame.Create(
        new Uri(path),
        BitmapCreateOptions.PreservePixelFormat,
        BitmapCacheOption.OnLoad);
// 之後可直接繫結至 <Image> 或進行後製
```
關鍵思考：把解碼職責前移至 OS Layer (WIC)，App Side 零變動即可解除格式限制。

**Cases 1**:  
某影像管理軟體（約 12 萬行 C#/WPF）在安裝 Codec 之後，無需重新編譯就能一次性導入超過 1,000 張 .CR2；初次匯入時間由 18 分鐘降至 6 分鐘（省去批次轉檔）。  

**Cases 2**:  
攝影工作室原先每日批次將 RAW 轉 JPEG 再進行色彩分級。安裝 Codec 後，直接於 WPF 工具中開啟 .CR2，省下約 30 % 前處理時間，並保留 14-bit 原生動態範圍。  


## Problem: 仍無法讀取較舊機種使用的 .CRW 檔

**Problem**:  
使用 Canon G2／D60 等早期機種的使用者在 Vista 上依舊無法查看或編輯 .CRW 檔；即便安裝了新的 Canon RAW Codec，系統仍顯示「不支援的檔案格式」。

**Root Cause**:  
1. Canon 釋出的 Vista Codec 僅支援第二代 RAW 容器 (.CR2)，並未包含較舊的 .CRW 規格。  
2. .CRW 與 .CR2 檔頭與資料結構差異大，須獨立實作解碼邏輯；Canon 尚未提供對應版本。  

**Solution**:  
短期避險  
A. 使用 Adobe DNG Converter 或第三方批次工具（ex: IrfanView + Plugins）將 .CRW 轉為 DNG/TIFF，再由 WPF 載入。  
B. 若需程式內立即顯示，可引用開源 dcraw 並以 C++/CLI 或 P/Invoke 包裝成 WIC-Compatible Codec，讓系統層即可解碼。  

Sample 批次轉檔流程 (PowerShell)：  
```powershell
Get-ChildItem "C:\OldRAW\*.crw" | %{
    &"C:\Program Files\Adobe\Adobe DNG Converter.exe" $_.FullName `
        --outputDirectory "C:\Converted\"
}
```  
關鍵思考：以「格式轉換」或「自製 Codec」兩條路徑補齊官方支援空缺，避免長期被舊格式鎖定。  

**Cases 1**:  
攝影師存有約 5,000 張 .CRW。批次轉檔為 DNG 後，一次性釋放重複 JPEG 備份 4 GB 空間，並可在 Vista 搜尋中直接依 EXIF 檢索。  

**Cases 2**:  
某開發團隊以 dcraw + C# Wrapper 實作自家 Codec，在 WPF 即時解碼 .CRW，雖然效能較官方 .CR2 Codec 慢 2 倍，但成功支援 2002–2004 年機種，避免舊客戶流失。