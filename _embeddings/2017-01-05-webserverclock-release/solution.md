# 網路搶票小幫手 ‑ WebServerClock v1.0

# 問題／解決方案 (Problem/Solution)

## Problem: 線上搶票時，本機時鐘與售票網站時鐘不一致

**Problem**:
在限時搶購或線上訂票時，許多使用者必須於「00:00:00」這一秒按下「購買／訂票」的按鈕。但本機電腦時鐘常與售票網站伺服器的時鐘產生秒級甚至分鐘級的落差，導致即使看似「準時」點擊，仍可能因時間誤差而錯失購票機會。

**Root Cause**:
1. 售票網站通常不提供 NTP 伺服器供外部校時，且網站後端也可能未開啟 NTP Client。  
2. 公網環境下，使用者僅能透過 HTTP 存取網站，無其他精準對時管道。  
3. 本機系統預設的時間同步頻率（Windows Time Service, 週期以小時計）不足以應付秒級需求。

**Solution**:
開發「WebServerClock」工具，利用 HTTP/1.1 Response Header 中強制存在的 `Date` 欄位來推算伺服器時間，計算伺服器與本機之時間差 (offset)，並即時顯示「模擬後的伺服器時鐘」。

核心流程／Sample Code（C#）:
```csharp
HttpClient client = new HttpClient();
client.BaseAddress = new Uri(this.textWebSiteURL.Text);
HttpRequestMessage req = new HttpRequestMessage(HttpMethod.Head, "/");

DateTime t0 = DateTime.Now;                       // 封包送出時間
HttpResponseMessage rsp = await client.SendAsync(
    req, HttpCompletionOption.ResponseHeadersRead);
DateTime t3 = DateTime.Now;                       // 封包收到時間
TimeSpan duration = t3 - t0;                      // 往返時間 RTT

DateTime t1p = DateTime.Parse(
    rsp.Headers.GetValues("Date").First());       // 伺服器回傳的 Date
this.Offset = t1p - t0.AddMilliseconds(duration.TotalMilliseconds / 2);

this.labelOffset.Text = string.Format(
    @"時間差: {0} msec, 最大誤差值: {1} msec",
    this.Offset.TotalMilliseconds,
    duration.TotalMilliseconds / 2);
```
關鍵思考點  
• HTTP `Date` 為 RFC2616 必備欄位，幾乎任何 Web Server 均會回傳，可視為唯一可靠的對時資訊。  
• 將伺服器回覆時刻假設落在往返過程的中點 `t0 + RTT/2`，可在未知實際傳輸延遲的前提下，將最大誤差限定為 `RTT/2`。  
• 計算得出的 offset 僅執行一次，不造成伺服器額外負擔；本地 UI 以 30 ms 週期重畫並顯示「伺服器時鐘」。

**Cases 1**:  
• 背景：作者一家人需於開放購票秒殺時段購買花東火車票。  
• 做法：事先以 WebServerClock 同步伺服器時間，確認誤差約 ±XXX ms。  
• 成效：作者成功搶得車票，而未使用工具的家人因時間差未能完成訂票，顯示工具確實提高成功率。


## Problem: 網路延遲不對稱，難以精準推算伺服器時間點

**Problem**:
即便取得伺服器回覆的 `Date` 欄位，仍無法得知該時間點在傳輸過程中的確切位置；網路延遲的雙向不對稱 (uplink ≠ downlink) 進一步影響推算準確度。

**Root Cause**:
1. Client 僅能量測 `t0`（送出）與 `t3`（接收）兩個時間戳，其餘 `t1`, `t2` 不可觀測。  
2. 實際網路延時 `(t1 - t0)` 與 `(t3 - t2)`，常因 ISP 路由、封包擁塞而差異不一。  
3. Server 實際寫入 `Date` 的時刻 `t1'` 可能落在 `t1`~`t2` 任一時間點。

**Solution**:
以「中點假設」(mid-point assumption) 將 `t1'` 視為 `(t0 + t3) / 2`，並計算最大可容忍誤差 `RTT/2`。  
• 同步時顯示「最大誤差」提示使用者。  
• 若需更高精度，可重複多次取樣並取平均／中位數以減少隨機網路抖動影響。  
• 在 UI 中以 30 ms 更新，確保人眼觀察之連續性。

**Cases 1**:  
• 背景：跨國伺服器 (RTT ≈ 220 ms) 之限時折扣活動。  
• 誤差估算：最大誤差 ≈ 110 ms。  
• 透過多次取樣(5 次)後取平均 offset，誤差降低至 <50 ms，成功在活動開放首波即完成下單，避免因時差錯過。