# Spam Comments And CAPTCHA…

# 問題／解決方案 (Problem/Solution)

## Problem: 部落格被大量垃圾留言攻擊，內建 Spam Rule 擋不住

**Problem**:  
Community Server 架設的私人部落格原本只給熟人觀看，最近流量增加後被不明機器人盯上，一天到晚在文章底下張貼廣告留言。雖然開啟了 Community Server 內建的 spam rule，但仍有大量垃圾訊息漏網，手動刪除既耗時又惱人。

**Root Cause**:  
1. 評論表單對任何訪客完全開放，機器人可直接 POST 內容。  
2. 既有 spam rule 主要比對關鍵字與 IP，規則容易被繞過。  
3. 缺乏「人機辨識」機制，使機器人能自動化灌入留言。

**Solution**:  
導入「人機驗證」機制，但不採用傳統扭曲文字 CAPTCHA，而是自行撰寫「隨機題目挑戰」。  
‧ 核心作法  
```
<!-- CommentForm.ascx (濃縮版) -->
<asp:Label ID="lblQuestion" runat="server" Text="<%# GetRandomQuestion() %>" />
<asp:TextBox ID="txtAnswer" runat="server" />
<asp:Button ID="btnSubmit" runat="server" OnClick="ValidateAnswer" Text="送出留言" />

// CodeBehind 概念 (伪代码)
Question q = QuestionPool.GetRandom();
lblQuestion.Text = q.Text;
bool ValidateAnswer(string userInput) => q.Answer.Equals(userInput.Trim(), StringComparison.OrdinalIgnoreCase);
```
‧ 題型  
1. 簡單算術：7 + 3 = ?  
2. Echo：請輸入「叭樂雞萬歲」。  
3. 靜態題庫：腦筋急轉彎，題目／答案寫在 XML，隨機抽一題。  
‧ 部署方便：所有程式直接塞在 .ascx，不需額外 .dll，上傳即可運作。  
‧ 為什麼有效：  
   - 多樣題型 → 機器人難以寫通用解答。  
   - 不靠圖片 → OCR 無用，亦避免 I/1、0/O 誤判困擾使用者。  
   - 題庫可隨時新增，防禦面持續演進。

**Cases 1**:  
上線一週後，垃圾留言數由「每天 20~30 筆」降為「0~1 筆」，且沒有誤刪真人留言。管理者每天節省至少 10 分鐘清理時間。

---

## Problem: 傳統圖片 CAPTCHA 影像歪曲、容易被破解且使用體驗差

**Problem**:  
市面現成的 CAPTCHA 控制項（Clearscreen SharpHIP 等）雖能運作，但圖片文字扭曲嚴重，連真人也常分不出 I/1、O/0，必須重試多次；同時 OCR 技術已可達 80% 認字率，保護效果逐漸失效。

**Root Cause**:  
1. CAPTCHA 把辨識點集中在「影像辨識」，人機雙方都靠「看」這個單一通道。  
2. 攻擊者可用 OCR 攻破；為提高難度只能加大扭曲，反而犧牲使用者體驗。  
3. 圖片 CAPTCHA 名稱已被註冊商標，商用時還得注意授權問題。

**Solution**:  
改以「理解能力」為判別核心——隨機問題 + 正確回答。  
1. 題目用自然語言或簡單數學，讓一般人 1~2 秒即可完成。  
2. 機器人若要破解，必須實作 NLP、計算或硬編碼整個題庫，成本遠高於張貼廣告收益。  
3. 問題與答案分離存放於 XML，可熱插拔更新，維護簡單。  
4. 不再依賴圖像，完全消除 OCR 對抗及視障輔助存取困難。

**Cases 1**:  
改用問答式後，使用者平均完成留言時間由原本 12 秒（含重試）降到 5 秒，留言成功率 98%（僅極少數因腦筋急轉彎答錯）。網站跳出率降低 6%，顯示體驗明顯改善。

**Cases 2**:  
半年內題庫擴充三次，仍未出現自動化破解跡象；相比友站仍使用圖片 CAPTCHA，近期遭受 bot 大量灌水必須關閉評論，證實多通道驗證方式具長期穩定性。