```markdown
# 「總算搬完了」—Home Server & 桌機主機板對調 DIY 升級實戰

# 問題／解決方案 (Problem/Solution)

## Problem: Server 噪音大、耗電高，想升級卻遲遲未動手

**Problem**:  
家中 Server 一直採用 Pentium D 920，長時間運轉噪音明顯、用電量高；反而另一台 MCE（Media Center）電腦已有 Core 2 Duo，兼具效能與省電。想把兩台電腦的主機板／CPU 對調，卻因「懶」一拖數月。

**Root Cause**:  
Pentium D 架構本身 TDP 高 + 老舊機殼散熱差 → 噪音、耗電居高不下；而 DIY 升級需要拆兩台機器，工序多、時間長，導致遲遲未執行。

**Solution**:  
1. 規劃 Downtime：挑選週末家人外出的 3.5 小時空檔動工。  
2. 一次性拆裝：  
   ```bash
   # Step1：Backup server data
   rsync -av /srv/ /backup/srv_$(date +%F)
   # Step2：Shutdown both machines
   shutdown -h now
   # Step3：對調主機板 & CPU
   # Step4：重新接線、開機自測
   ```  
3. 完成後在 Server BIOS 啟用 EIST / C1E 等省電機制。

**Cases 1**:  
‧ Server CPU 溫度由 65 °C → 42 °C；整機功耗 160 W → 90 W，風扇轉速降 30%，客廳明顯安靜。  
‧ 客廳機動力 (Pentium D) 轉去看電視錄影即可，重度運算交給新 Server，硬體投資 0 元完成升級。

---

## Problem: 顯示卡散熱片卡住機殼 12 吋大風扇，機殼蓋不起來

**Problem**:  
組裝時發現顯示卡散熱鰭片與機殼頂部 12" 風扇高度衝突，側板無法闔上。

**Root Cause**:  
1. 顯示卡採高規散熱器 (兩槽高度)。  
2. Tower 機殼頂部裝了超大 12" 風扇，未事先量測空間。

**Solution**:  
A. 改用低風阻薄型 12 cm 風扇 + 移位：  
   1. 去除 12" 風扇，改裝 12 cm PWM 風扇。  
   2. 利用風扇減震墊片將風扇略往機殼外側偏移 3 mm。  
B. 若仍干涉 → 更換 Low-Profile VGA Cooler。

**Cases 1**:  
風扇改裝後 CPU 溫度僅 +2 °C，機殼可正常關閉，室內再無「開盒機」噪音。

---

## Problem: 12" 機殼風扇長期靜置竟吸入蚊蟲

**Problem**:  
機殼長時間待機，風扇在低轉速狀態下形成負壓，把蚊子、灰塵吸進去。

**Root Cause**:  
無防塵網 + 機殼進氣孔面積大 → 昆蟲可直接進入。

**Solution**:  
1. 安裝可拆洗式 Nylon 防塵／防蟲網。  
2. 風扇改以「正壓」配置：前進風 > 後排風，降低外部雜物吸入。

**Cases 1**:  
半個月後開箱檢查，無再見蚊蟲屍體，CPU/MB 落塵量 ↓ 70%。

---

## Problem: 機內積塵嚴重，吸塵器臨時沒電

**Problem**:  
拆機時發現散熱片、電源供應器積滿灰；家用無線吸塵器又因電池耗盡無法使用。

**Root Cause**:  
‧ 長期未定期保養 → 灰塵累積；  
‧ 使用無線吸塵器但平常未充電，導致關鍵時刻無法工作。

**Solution**:  
A. 預備 Plan-B：  
   1. 隨手備兩瓶氣體除塵罐。  
   2. 小號油畫刷配合家用有線吸塵器濾塵袋。  
B. 建立每季保養 SOP：Google Calendar 設「PC Dust-Clean」提醒。

**Cases 1**:  
每次保養 10 分鐘即可完成，風扇 PWM 轉速維持 <1,200 RPM，噪音穩定。

---

## Problem: SATA 接頭一碰就掉，導致重複拆裝

**Problem**:  
拆裝過程中 SATA 線鬆脫，HDD 無法被 BIOS 偵測，被迫多次開關機。

**Root Cause**:  
早期 SATA 無金屬扣；線材老化、接頭鬆弛 → 接觸不良。

**Solution**:  
1. 換用「帶金屬鎖扣」的 SATA II/III 線。  
2. 線材走背板，減少張力。  
3. BIOS 開啟 SMART 提示失連告警。

**Cases 1**:  
重開機 50+ 次無再掉盤；CrystalDiskInfo 無 Error-Count 新增。

---

## Problem: Windows XP Media Center Edition 硬體大變動觸發重新啟用

**Problem**:  
MCE 開機提示偵測到硬體變更，要求重新 Activation，影音功能暫停。

**Root Cause**:  
WinXP 以主機板序號 + CPU ID 作為硬體指紋；主機板更換判定為「新電腦」，需重新認證。

**Solution**:  
1. 連網自動啟用；若失敗 → 電話啟用流程。  
2. 建議升級至 Windows 10 LTSB / Linux + Kodi，解除老舊 OS 綁定。

**Cases 1**:  
電話啟用 10 分鐘完成，MCE 功能恢復；後續改裝 LibreELEC 後不再受限。

---

## Problem: 前面板 LED / USB 線未標示正負，導致燈不亮、USB 失效

**Problem**:  
接線後電源 LED、讀卡機燈及前置 USB 均無法使用。

**Root Cause**:  
前面板跳線 (HD LED / POWER LED / USB) 無清晰 +/- 標示，誤插方向。

**Solution**:  
1. 查閱主機板 Front Panel Header Pinout。  
2. 用萬用電表量測線序 & 自行貼標籤。  
3. 建立「拍照記錄 → Evernote」流程，未來維護方便。

**Cases 1**:  
重插後全部恢復；日後再拆裝花費 <1 分鐘即可辨識。

---

## Problem: BIOS 抓不到 USB 鍵盤，無法按確認鍵

**Problem**:  
開機必須按 Enter，但 USB 鍵盤在 POST 階段無作用，只好翻箱倒櫃找 PS/2 鍵盤。

**Root Cause**:  
部分舊版 BIOS「USB Legacy Support」預設關閉，POST 階段不初始化 HID 裝置。

**Solution**:  
1. 臨時方案：接 PS/2 鍵盤完成首次開機。  
2. 永久方案：進 BIOS → Advanced → Enable USB Legacy Support。  
3. 如 BIOS 太舊無此功能 → 使用 PS/2-to-USB 轉接晶片鍵盤。

**Cases 1**:  
開啟後 USB 鍵盤在 POST 階段正常；再也不用囤老式鍵盤。

```
