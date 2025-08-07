# CS Control: Recent Comments

## 摘要提示
- CS 2.0 升級: 升級後缺少「最新回應」功能，引發使用者抱怨。  
- Provider Model: CS 2.0 改用 Provider Model 存取資料，必須透過官方 API 取得資料。  
- 資料物件 Post: CS 的 Post 物件同時代表 Blog 文章、留言、論壇討論串與相片等多種型態。  
- DataProvider: 利用 DataProvider 取得 WeblogPost 物件，以取得所需原始資料。  
- Theme Model: 2.0 新增 Theme Model，畫面修改需在正確的 Theme Control 與 Skin-#####.ascx 中著手。  
- User Control 對應: 每個 Theme Control 對應同名的 .ascx，並需由 DLL 定義並處理 Child Controls。  
- 自行擴充: 作者經研究後，成功實作顯示「最新回應」功能，差異化網站特色。  
- 技術難點: 最棘手的是找出正確修改位置與繞過 Data Provider 的限制。  
- 官方討論區支援: 研究過程大量參考 CS 官方網站討論串。  
- 成果展示: 最後貼出截圖，證明功能已順利運作。  

## 全文重點
作者將 Community Server (CS) 升級到 2.0 版後，舊有的「最新回應 (Recent Comments)」外掛失效，引起使用者批評。原因在於 CS 2.0 以 Provider Model 重新設計資料存取機制，若不重寫 Data Provider，開發者只能借助官方 API 來抓取資料；同時 2.0 新增的 Theme Model 也讓介面調整變得複雜，任何文字或控制項的加入都必須在正確的 Theme Control 與對應的 Skin-#####.ascx 中進行。  
經過一段時間摸索與參考官方論壇，作者確定解法：先弄清 Post 物件在 CS 中是一個統一的資料抽象，可代表 Blog 文章、留言、論壇主題與相片等；因此，只要利用 DataProvider 取得回傳型別為 WeblogPost 的集合，再篩選 comment 類型即可取得最新留言。介面層則需在對應的 Theme Control 中建立使用者控制項，並於 DLL 端為其註冊與生成 Child Controls，以確保在各 Theme 之間能呼叫同名 .ascx 執行。  
透過上述方法，作者不僅復原「最新回應」功能，還讓自家 CS 站台具備獨特風格，並在文末附上截圖證明成果。

## 段落重點
### 換用 CS 2.0 後的困境與需求
作者自述自從網站升級為 CS 2.0 後，因缺乏「最新回應」顯示而備受抱怨；回顧 1.0 時代曾自行改寫擴充，但 2.0 完全不同的 Provider Model 讓原有程式失效，加上 Theme Model 讓 UI 位置難找，成為最初的技術瓶頸。

### Provider Model 與 Post 物件解析
說明 CS 2.0 改以 Provider Model 取代舊有直接存取資料庫方式，若不重寫 Data Provider，就只能透過官方 API；進一步指出 Post 物件是系統核心，涵蓋 Blog 文章、留言、論壇文章及相片，使得只要抓到 Post，再分辨類型即可。

### Theme Model 與 Control 結構
分析 Theme Model 的運作：每個 Theme Control 必須對應一支同名 Skin-#####.ascx；在該 .ascx 裡再宣告 Child Controls，並在後端 DLL 處理其邏輯，否則難以將自訂內容插入畫面。找到正確檔案後，後續修改反而簡單。

### 完整實作與成果展示
作者結合 DataProvider 取得 WeblogPost 集合、篩選 comment 資料，並於 Theme Control 加入自訂 User Control，最終成功顯示「最新回應」；文末以截圖佐證，並強調網站因而煥發新特色。