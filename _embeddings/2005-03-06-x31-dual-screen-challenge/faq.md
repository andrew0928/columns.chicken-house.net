# X31 + 雙螢幕的挑戰 @_@

# 問答集 (FAQ, frequently asked questions and answers)

## Q: ThinkPad X31 可以透過 Dock 的 DVI 連接埠輸出 DVI 訊號嗎？
不行。雖然 Dock 上有 DVI 接頭，但 X31 本身不支援 DVI 輸出，因此該接頭只能當裝飾用。

## Q: 作者最後挑選哪一款 17 吋 LCD？為什麼會選它？
作者選了 Sxxxxxx 720T。主要原因是這台螢幕隨附 Pivot Pro 軟體，可在不受顯示卡限制的情況下將畫面旋轉 90°，正好滿足作者需要直立顯示的需求。

## Q: 如果 ATI 驅動程式預設沒有旋轉功能，該怎麼手動開啟？
可以修改登錄機碼  
HKEY_LOCAL_MACHINE\SOFTWARE\ATI Technologies\Desktop\{GUID}\Rotation  
把原來的 00 00 00 00 改成 01 00 00 00，顯示卡設定就會出現「旋轉」選項。

## Q: 32 MB 影像記憶體能同時跑 1024×768×32bits 與 1280×1024×32bits 的雙螢幕嗎？
不能。32 MB VRAM 撐不住這兩組 32-bit 色深的解析度，必須把其中一個螢幕降成 16-bit 色彩才行。

## Q: 作者最終是怎麼讓 X31 與直立式 17 吋 LCD 順利運作雙螢幕的？
先用登錄檔 hack 開出旋轉選項，但因驅動在 1280×1024×16bits 模式下仍不支援旋轉，最後改用 Pivot Pro 軟體進行 90° 旋轉，並把其中一個螢幕降成 16-bit 色彩，終於成功使用直立雙螢幕。