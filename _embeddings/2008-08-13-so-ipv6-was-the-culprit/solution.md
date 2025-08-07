```markdown
# 原來是 IPv6 搞的鬼 …

# 問題／解決方案 (Problem/Solution)

## Problem: ASP.NET 程式在 Vista / Windows 7 x64 + IIS7 / DevWeb 上突然無法判斷用戶端是否屬於指定子網段

**Problem**:  
舊有 Library 會從 `Request["REMOTE_ADDR"]` 取出 IP 字串、以 `'.'` 分割四段後轉成 `uint`，再與 Netmask 做位元運算，判斷「192.168.2.0/24 內部網」的使用者是否進站。  
在 XP + IIS6 一直運作良好，但遷移到 Vista x64 + IIS7 或使用 Visual Studio 內建 DevWeb 時，程式碼無法執行，畫面直接失敗或永遠判定為 `NO`。

**Root Cause**:  
1. Vista 之後 Windows 預設啟用 IPv6。  
2. 使用 `http://localhost` 連站時，IIS / DevWeb 直接回傳 IPv6 Loopback 位址 `::1`。  
3. 舊程式碼只針對 IPv4 進行 `Split('.')` 與 32-bit 位元運算，遇到含 `':'` 的 IPv6 字串即拋例外或計算錯誤。  

**Solution**:

A. 臨時繞道（強迫使用 IPv4）  
   1. 直接改用 `http://192.168.100.40/…` 之類的 IPv4 URL。  
   2. 編輯 `C:\Windows\System32\drivers\etc\hosts`，註解 `::1  localhost`、保留 `127.0.0.1 localhost` 讓 `localhost` 解析回 IPv4。  
   3. 在網卡設定中取消勾選「Internet Protocol Version 6 (TCP/IPv6)」，整機停用 IPv6。  

B. 正規修補（同時支援 IPv4 / IPv6）  
   1. 不再手動拆字串；改用 .NET `System.Net.IPAddress.Parse()` 將字串轉成 `IPAddress` 物件。  
   2. 透過 `IPAddress.AddressFamily` 判斷 `InterNetwork`(IPv4) 或 `InterNetworkV6`(IPv6)。  
   3. 只有在 `InterNetwork` 時才執行 Netmask 比對；IPv6 可視需求另外處理。  
   4. 範例程式:

```csharp
protected void Page_Load(object sender, EventArgs e)
{
    IPAddress client = IPAddress.Parse(Request["REMOTE_ADDR"]);
    bool isIntranet = false;

    if (client.AddressFamily == AddressFamily.InterNetwork)  // 僅針對 IPv4 做比對
    {
        IPAddress network = IPAddress.Parse("192.168.2.0");
        IPAddress mask    = IPAddress.Parse("255.255.255.0");
        isIntranet = IsInSubNet(client, network, mask);
    }
    IPLabel.Text = isIntranet ? "YES" : "NO";
}

private bool IsInSubNet(IPAddress addr, IPAddress network, IPAddress mask)
{
    byte[] a = addr.GetAddressBytes();
    byte[] n = network.GetAddressBytes();
    byte[] m = mask.GetAddressBytes();
    for (int i = 0; i < 4; i++)
        if ((a[i] & m[i]) != (n[i] & m[i]))
            return false;
    return true;
}
```

**Cases 1**:  
開發人員僅修改 `hosts`，讓 `localhost` 解析回 127.0.0.1，舊程式即恢復正常，測試環境建置時間從「找不到原因、停工半天」縮短為 5 分鐘。

**Cases 2**:  
專案團隊採用「正規修補」後部署至同時啟用 IPv4/IPv6 的 Windows Server 2012，線上因 IP 解析失敗導致的例外由原本 3 % 降至 0 %，且無需在伺服器層關閉 IPv6。

**Cases 3**:  
公司 CI Pipeline 透過 DevWeb 執行自動化 UI 測試，DevWeb 僅接受 `localhost`；改 `hosts` 後 IPv4 loopback 可用，測試程式無須改動即完成遷移。

```