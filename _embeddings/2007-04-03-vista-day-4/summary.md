# Vista Day 4…

## 摘要提示
- 升級衝擊: 作者列出五項在 Vista 上最令人氣餒的改變。
- 工具列限制: 工作列無法再自由拉出常用工具列，使用效率降低。
- 注音輸入法改版: 介面與行為大幅變動，打字習慣被迫改變。
- Console 拖曳失效: 無法再將檔案拖進命令視窗，自動補完路徑功能消失。
- 影像 PowerToys 失效: Image Resizer 與 RAW Image Viewer 在 Vista 全面失效。
- WIC 架構: Vista 影像處理遷移到 WPF／WIC，走向 codec 模式與 HD Photo 佈局。
- RAW 支援缺口: Nikon 已釋出 WIC codec，Canon 尚未跟進，影響自製歸檔程式。
- UAC 囉唆: 頻繁跳窗造成干擾，使用者往往直接點選同意。
- sudo 對比: 作者認為 UNIX 的 sudo／XP 的 runas 更為順手。
- 結語自嘲: 發完牢騷後承諾下一篇寫些正面心得。

## 全文重點
作者在升級到 Windows Vista 的第四天，列舉五個最令他崩潰的變動：1) 內建工具列無法再獨立拖出，打斷日常操作流程；2) 注音輸入法徹底改寫，拿掉 DOS 時代延續的 ALT+KEYPAD 輸入、Shift 英文改成大寫、無法以 Backspace 取消選字，導致長年肌肉記憶全面失靈；3) Console 視窗不再接受檔案拖放，必須手動輸入完整路徑；4) Image Resizer、RAW Image Viewer 等兩套 PowerToys 在 Vista 全面報廢，連帶讓他利用 RAW Image Viewer wrapper 開發的歸檔工具不能用。調查後得知 Vista 改以 WPF／WIC 做影像處理，採 codec 架構並導入 HD Photo，Nikon 已發布 WIC codec，Canon 仍缺席；5) UAC 雖具保護目的，卻屢屢跳窗干擾，對懂的人多此一舉，對不懂的人只是新一輪「全部按 YES」。作者回顧自己在 UNIX 使用 sudo、在 Windows 2000/XP 透過 runas 的經驗，認為 UAC 仍不如 sudo 簡潔；他最終乾脆把 UAC 關閉。全文帶著吐槽口吻，透露對新系統的無奈，同時也看見 Vista 背後新架構的技術脈絡與未來方向。

## 段落重點
### 升級四日，五大不爽
作者先點名五件最破壞日常工作流程的變動：無法拉出工具列、注音輸入法大改、Console 拖曳失效、影像 PowerToys 失能與 UAC 囉唆。這些看似小事卻涵蓋他絕大部分操作習慣，使得家庭機尚能容忍，若在工作環境恐怕當場抓狂。

### 注音輸入法大改帶來的衝擊
傳統「笨注音」被抽換，只剩陽春模式；ALT+KEYPAD 輸入 ASCII 碼功能遭移除；中文模式下按住 Shift 只能輸出大寫英文；選字狀態下無法以 Backspace 取消。十餘年肌肉記憶頓時失效，連打線上遊戲聊天都因卡字而滅團，讓作者哀嘆 Vista 正在拔掉他最熟悉的輸入法。

### 影像 PowerToys 全滅與 WIC 架構
Image Resizer、RAW Image Viewer 兩大工具無法安裝，直接導致作者自製依賴其 wrapper 的 RAW 歸檔程式也癱瘓。深入查證後發現 Vista 改以 WPF／WIC 處理影像，改走 codec 架構並推 HD Photo，象徵微軟想取代 JPEG。Nikon 已發佈 NEF codec，Canon 的 CRW/CR2 仍未釋出，作者只得等待或自行改寫程式以支援 WIC。

### UAC 的愛恨情仇
UAC 旨在防止管理者無意間執行危險操作，但實務上頻繁跳窗，讓人聯想過去防毒軟體不斷誤報 script 的經驗。賽門鐵克甚至公開批評 UAC。作者回憶自己在 UNIX 使用 sudo、在 2000/XP 借 runas 達成最小權限原則的做法，認為 UAC 既打斷流程又無法真正教育使用者；搞不定的結果就是他把 UAC 關閉。

### 牢騷後的收尾
作者自嘲「牢騷發完」並感謝讀者收看，表示下回會嘗試從正面角度評價 Vista。整篇文章在抱怨之餘，也揭露 Vista 轉向新影像架構與安全模式的技術背景，只是變動過大、預設體驗不佳，對老用戶而言仍需時間適應。