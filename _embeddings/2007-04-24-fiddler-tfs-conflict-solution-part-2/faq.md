# Fiddler 跟 TFS 相衝的問題解決 - II

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 作者最後是如何成功在 Fiddler 啟動時自動修改 IE Proxy 設定、並在停止時恢復原狀？
透過「D 計劃」：  
1. 先將能修改 WinINET Proxy 的程式碼包成一支主控台程式 `myproxycfg.exe`，放在 Fiddler 安裝目錄。  
2. 在 `CustomRules.js` 的 `OnAttach()` 事件中以  
```csharp
System.Diagnostics.Process.Start("myproxycfg.exe");
```  
呼叫這支程式。  
如此一來 Fiddler 開始擷取 (Capture) 時會執行 `myproxycfg.exe` 來調整 Proxy；停止擷取時 Fiddler 會自動把先前備份的 Proxy 設定復原，TFS 便不再與 Fiddler 衝突。

## Q: 直接在 `CustomRules.js` 內存取 `Fiddler.WinINETProxyInfo` 類別為何會編譯失敗？
Fiddler 外掛 Script 會被動態載入並編譯到另一個獨立的 AppDomain。  
由於該 AppDomain 並未參考 Fiddler 主程式所在的 Assembly，Script 便無法直接存取 `Fiddler.WinINETProxyInfo`，因此在編譯階段就會拋出錯誤。

## Q: 作者嘗試的各種方案 (A～C) 分別失敗的原因是什麼？
A 計劃：試圖以 Reflection 直接存取 `Fiddler.Proxy` 內的 `piPrior / piThis` 欄位，但兩者為 `private`，無法外部存取。  
B 計劃：把修改 Proxy 的四行程式碼直接貼進 `CustomRules.js`，因 AppDomain 隔離導致編譯階段找不到 `Fiddler.WinINETProxyInfo`。  
C 計劃：改用 Reflection 在 Script 內動態 `Assembly.LoadFrom("Fiddler.exe")` 後再操作 `WinINETProxyInfo`，但同樣因 AppDomain 限制而失敗。  

## Q: Fiddler 預設為何常在使用 VPN 或無線網路時失效？
Fiddler 只會修改「區域連線 (Local Area Connection)」的 Proxy 設定；若使用者透過其他網路介面卡 (如 VPN、無線網卡) 上網，IE 允許各介面卡獨立設定 Proxy，導致這些連線並未被設成 `127.0.0.1:8888`，Fiddler 因而無法擷取流量。  

## Q: Fiddler 在開始與停止擷取流量時，對 IE Proxy 設定會做哪些動作？
開始擷取時：  
1. 先備份當前的 Proxy 設定 (存入 `piPrior`)。  
2. 將 Proxy 改成 `127.0.0.1:8888`，以導流到 Fiddler。  
停止擷取時：  
把先前備份的設定 ( `piPrior` ) 完整寫回 IE，使環境恢復原狀。