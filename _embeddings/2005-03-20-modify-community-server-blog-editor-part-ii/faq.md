# 修改 Community Server 的 blog editor ( Part II )

# 問答集 (FAQ, frequently asked questions and answers)

## Q: Community Server 1.0 的原始碼大量採用了哪一種設計模式？
Community Server 1.0 在許多元件（如 TextEditor Wrapper、membership、roles、authentication 等）都大量使用了 Provider Pattern（提供者模式）。

## Q: 若想將 Community Server 切換到新的 Provider，需要做什麼？
只要撰寫好新的 Provider，並在 communityserver.config 中調整對應設定，即可立即切換到新的 Provider，不必變動其他程式碼。

## Q: 作者這次主要修改了 Community Server 的哪一個元件？
作者這次繼承並修改了 TextEditorWrapper。

## Q: 對 TextEditorWrapper 的修改帶來了哪些具體功能改進？
1. 將表情符號（Emoticons）加入了編輯器的 Toolbar。  
2. 啟用了原本 FreeTextBox 中被關閉的一些進階功能，提升了編輯器的使用體驗。

## Q: 作者下一步的打算是什麼？
作者計畫之後再嘗試修改 Community Server 的其他部分，進一步擴充或優化系統功能。