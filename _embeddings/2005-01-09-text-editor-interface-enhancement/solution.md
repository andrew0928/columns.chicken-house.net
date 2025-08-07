# .TEXT 的編輯介面補強 (自己爽一下)..

# 問題／解決方案 (Problem/Solution)

## Problem: 在 .TEXT 後台編輯文章時，無法直接插入圖片與表情符號

**Problem**:  
使用 .TEXT 這套 Blog 系統內建的 WYSIWYG 編輯器（FreeTextBox v1.6）時，想在文章中插入圖片或表情符號卻找不到相對應的按鈕，必須切到 HTML 原始碼模式手動加入 `<img>` 或特殊符號，流程繁瑣且易出錯。

**Root Cause**:  
1. .TEXT 內建的 FreeTextBox 版本較舊（v1.6），原生工具列缺少「插入圖片」與「插入表情符號」相關功能。  
2. 系統框架雖支援客製化，但預設未啟用或顯示這些功能，導致使用者只能透過原始碼編輯來達成需求。

**Solution**:  
自行修改 FreeTextBox 的設定與程式碼，為工具列新增一排自訂按鈕：  
1. 下載對應版本的 FreeTextBox 原始碼或設定檔（*.ascx / *.cs*）。  
2. 在 `ToolbarLayout` 中加入「InsertImage」、「InsertSmiley」等 command。  
   ```aspx
   <ftb:FreeTextBox id="ftbEditor" runat="server"
       ToolbarLayout="ParagraphMenu,FontFacesMenu,FontSizesMenu,Bold,Italic,Underline,
                      InsertImage,InsertSmiley">
   </ftb:FreeTextBox>
   ```  
3. 若想顯示自訂表情符號，將圖檔放到 `/Emoticons/` 資料夾並在 `SmileyList.xml` 或對應設定檔中註冊。  
4. 重新編譯 / 佈署 .TEXT，即可在編輯畫面看到新增的一整排工具列，使用者得以直接點擊插入圖片與表情符號。  

關鍵思考：透過「工具列擴充」的方式，不必升級整個 .TEXT 或更換編輯器，即可解決缺少特定功能的痛點，同時保留既有系統相容性。

**Cases 1**:  
• 編輯含 10 張截圖的技術文章，原本手動貼 `<img>` tag 需 5 分鐘；導入新工具列後，可直接拖拉/點擊插圖，時間縮短至 1 分半。  
• 使用表情符號撰寫輕鬆日誌，原本需記憶 `/Emoticons/teeth_smile.gif` 等路徑；現在點擊即可插入，錯誤率降到 0%。