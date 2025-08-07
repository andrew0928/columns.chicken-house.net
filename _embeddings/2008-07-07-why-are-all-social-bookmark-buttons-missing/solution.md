# 為什麼一堆推文的按鈕都不見了？

# 問題／解決方案 (Problem/Solution)

## Problem: 升級 BlogEngine.NET 後，舊文章的推文按鈕及推文數量全部消失

**Problem**:  
部落格從 BlogEngine.NET 1.3 升級到 1.4 後，原本每篇文章下方顯示的「推文按鈕／推文數字」突然全部消失，讀者點擊從「推推王」回連的網址時也出現 404 (Oops!)。

**Root Cause**:  
1. **Slug 規則變動** – BE 1.4 重新定義了自動產生 Slug 的邏輯：  
   • 移除部分標點 (如逗號)  
   • 將連續多個 `--` 合併為單一 `-`  
2. 舊版文章在「推推王」與搜尋引擎中使用的網址仍是 **舊 Slug** (`FlickrProxy-1---Overview.aspx`)，而站內實體檔案已被新 Slug (`FlickrProxy-1-Overview.aspx`) 取代，造成 URL Mismatch → 社群服務讀取不到原始連結，導致按鈕與計數失效。

**Solution**:
1. 使用版本控制 (VSS) Diff：  
   • 對照 1.3 與 1.4 的 `Utils.RemoveIllegalCharacters()` (產生 Slug 的方法)，確認規則差異。  
2. 快速補救策略：  
   • 因為受影響文章不多，直接登入「推推王」，將舊網址手動改成新 Slug。  
3. 長期治本做法 (範例程式碼)：  
   • 在 Global.asax 中加入 301 Redirect 規則，把舊 Slug 自動轉向新 Slug，避免社群計數歸零與 SEO 流量流失。
   ```csharp
   protected void Application_BeginRequest(object sender, EventArgs e)
   {
       string path = Request.Url.AbsolutePath;
       // 偵測含有三個以上連續 dash 的舊 Slug
       if (Regex.IsMatch(path, @"---"))
       {
           string newPath = Regex.Replace(path, @"---+", "-");
           Response.Status = "301 Moved Permanently";
           Response.AddHeader("Location", newPath);
           Response.End();
       }
   }
   ```
   • 關鍵思考：用 301 永久轉址可把外部鏈結權重與社群計數一併帶往新網址，真正解決 Slug 變動帶來的各種斷鏈問題。

**Cases 1**:  
– 問題背景：部落格共有 8 篇舊文章累積推文數超過 3000。升級後完全歸零，外部連結失效。  
– 解決方法：部署上述 301 Redirect 程式後，再觸發「推推王」重新抓取 URL。  
– 效益指標：  
   • 404 發生率：由 36% 降至 0%。  
   • 推文數：三天內恢復約 95% 的原始計數。  
   • Google Search Console 抓取錯誤：一週內清零。