# 修改 Community Server 的 blog editor

# 問題／解決方案 (Problem/Solution)

## Problem: 社群平台（Community Server）無法直接在文章中插入圖片與表情符號

**Problem**:  
當作者將部落格平台切換到 Community Server (CS) 時，發現預設的文章編輯器無法滿足「貼圖」與「貼表情符號」的需求。若要維持既有的寫作流程（隨手插圖、即時加入表情），勢必要先對編輯器做客製化。

**Root Cause**:  
1. CS 採用 FreeTextBox (FTB) 做為核心編輯器，但 CS 又額外包了一層自家的 Editor Wrapper。  
2. 官方釋出的 CS 原始碼，恰好缺少了這一層 Wrapper 的程式碼，導致開發者無法直接在 FTB 內部工具列上做擴充或修改。  
3. 因此任何想加入的新功能（貼圖、貼表情符號）都只能「外掛」在 Wrapper 之外，使得新舊工具列分離、版面顯得格格不入。

**Solution**:  
1. 先在不動到 Wrapper 的前提下，將自製的「貼圖／貼表情工具列」獨立切成一段 HTML/JS，直接置放於編輯器畫面最上方。  
2. 透過 JavaScript 與 FTB 的 API 進行溝通：  
   - 使用 `FTB_InsertImage(url)` 把上傳完的圖片插入文章內容。  
   - 使用 `FTB_InsertHTML('<img src="/Emoticons/emotion-2.gif" />')` 快速插入表情符號。  
3. 即使工具列無法併入 FTB 既有 UI，也可用 CSS 讓整體外觀盡量貼近原生樣式。

> 為什麼能解決問題？  
> • 直接避開缺失的 Wrapper 原始碼，改以「外掛」方式與 FTB 互動。  
> • 保留 FTB 核心功能，同時新增圖片、表情插入能力，滿足實務寫作需求。  

**Cases 1**:  
• 改動後，作者在撰寫文章時可一鍵插入圖片與表情符號，省去改寫 HTML 的時間。  
• 雖然工具列被迫獨立在最上方，仍讓使用者在同一頁面完成所有編輯動作，體驗大幅改善。