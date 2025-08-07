# Vista Day 4...

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 升級到 Windows Vista 的第四天，作者最不能適應的五大改動是哪些？
1. 內建工具列無法再從工作列獨立拉出。  
2. 內建注音輸入法大幅改版，使用習慣被打亂。  
3. 在 Console 視窗裡已經不能用滑鼠將檔案拖放進去，必須打完整路徑。  
4. 兩款常用的影像 PowerToys ── Image Resizer 與 RAW Image Viewer ── 無法在 Vista 上使用。  
5. UAC（使用者帳戶控制）動不動就跳出確認視窗，十分囉唆。

## Q: Vista 內建的注音輸入法與舊版相比，具體有哪些差異讓作者困擾？
1. 最陽春的注音模式被拿掉，畫面底部不再顯示一排按鍵提示。  
2. 從 DOS 時代就能用的「Alt + 數字鍵盤」輸入 ASCII 碼功能被移除。  
3. 在中文模式下按住 Shift 雖然仍可直接輸入英文，但輸出變成大寫而非以往的小寫。  
4. 注音仍停在選字狀態（字底下有虛線）時無法按 Backspace 取消，導致打字常被卡住。

## Q: 為什麼 Image Resizer、RAW Image Viewer 以及作者自寫的歸檔程式在 Vista 上都失效了？
Vista 從過去使用的 GDI+（System.Drawing）全面改為 WPF 與 WIC（Windows Imaging Component）架構，所有影像處理都改走「Codec」機制。舊版程式依賴的 GDI+ 或舊 RAW viewer wrapper 在 Vista 無法運作，因此相關工具全部失效，連帶作者的歸檔程式也跟著不能用了。

## Q: Canon 的 CRW（RAW）檔案在 Vista 下有對應的 WIC Codec 嗎？
目前還沒有。Nikon 已經推出 NEF 格式的 WIC Codec，但 Canon 方面尚未發佈 CRW/CR2 的 Codec，因此作者只能等官方釋出或自行改寫程式以支援 WIC。

## Q: 作者為何最終選擇關閉 Vista 的 UAC？他更偏好的權限管理方式是什麼？
作者認為 UAC 跳出確認視窗的頻率過高，對懂得系統運作的人反而是干擾；而一般使用者多半也是習慣性點選「Yes」，實際防護效果有限。他更習慣 UNIX 系統的 sudo 模式，或在 Windows 2000/XP 時期使用 runas 指令，在需要時才臨時提權。由於不習慣頻繁的彈窗，他試用不久後就把 UAC 關閉了。