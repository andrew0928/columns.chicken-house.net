# CS Control: Recent Comments

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼在 CS 2.0 中要自行新增「最新回應」功能會卡關？
CS 2.0 資料存取全面改為 Provider Model，除非自行改寫 Data Provider，否則只能透過官方 API 取得資料；另外 2.0 新增的 Theme Model 也改變了版面組成方式，必須先找出正確的插入位置後才能動工，因此在研究階段花了不少時間。

## Q: 作者最後是如何取出「最新回應」資料的？
作者利用 CS 提供的 DataProvider 取得 Post 物件，再以 WeblogPost 型態取回所需的 comment 資料，並結合自訂 Theme Control 將結果呈現在畫面上。

## Q: CS 的 Post 物件可以代表哪些資料型態？
Post 物件在 CS 中是一個通用型別，可同時代表：
1. Blog 文章
2. Blog comment
3. Forum 討論串
4. 相簿中的相片
等多種內容。

## Q: 在 Theme 層要放入自訂控制項，需要注意哪些檔案對應關係？
每個 Theme Control 都必須對應同名的 Skin-#####.ascx 檔，Theme 檔案會引用這些 user control；在 user control 內需先定義好 child control，其餘功能則透過對應的 dll 程式碼來完成。

## Q: 作者是否最終成功讓自家 CS 站台重新擁有與眾不同的「最新回應」特色？
是的，經過研究與實作後，作者已成功完成新版「最新回應」功能，讓自家的 CS 站台再次呈現與眾不同的特色。