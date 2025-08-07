# Spam Comments And CAPTCHA...

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 作者為什麼最後決定自己開發一個「問答式 CAPTCHA」元件？
Community Server 內建的 spam rule 擋不住所有垃圾留言，現成的影像型 CAPTCHA 又難以辨識、使用體驗不佳。為了既能阻擋機器人、又能讓讀者覺得有趣並且安裝簡便，作者選擇自行撰寫一個小巧的問答式元件。

## Q: CAPTCHA 這個詞到底是什麼縮寫？  
CAPTCHA 是 “Completely Automated Public Turing test to tell Computers and Humans Apart” 的縮寫，意指「完全自動化的公開圖靈測試，用來區分電腦與人類」。

## Q: 只靠扭曲文字圖片的傳統 CAPTCHA，真的足以分辨人和機器嗎？  
未必。垃圾留言程式已可透過 OCR 技術達到約 80% 的辨識率，而剩下 20% 中還包含連真人都看不清的圖片；因此僅靠影像與 OCR 的對抗並不可靠，應加入對「理解能力」的考驗才更有效。

## Q: 作者自製的問答式 CAPTCHA 目前提供哪三種題目？  
1. 簡單的兩個一位數數學運算。  
2. Echo 題型：要求使用者逐字輸入指定句子。  
3. 靜態題庫：由 XML 檔隨機載入腦筋急轉彎等題目並比對正確答案。

## Q: 相較於影像型 CAPTCHA，作者認為問答式做法有哪些優點？  
題目可設計得有趣、易讀，不必反覆嘗試難辨認的扭曲文字；同時仍能有效阻擋機器人，提升讀者留言意願與互動樂趣。

## Q: 文中提到過哪些 ASP.NET CAPTCHA 相關的元件或參考資源？  
1. Community Server 官方提供的 CAPTCHA 控制項  
2. Clearscreen 的 SharpHIP HIP-CAPTCHA Control for ASP.NET  
3. darkthread 網站上的相關討論串 (http://blog.darkthread.net/forums/thread/575.aspx)