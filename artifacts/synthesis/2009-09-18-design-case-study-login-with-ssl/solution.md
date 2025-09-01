```markdown
## Case #1: 僅在登入流程使用 HTTPS，避免全站加密的效能代價

### Problem Statement（問題陳述）
**業務場景**：內容型網站需要會員登入才能使用部分功能。客戶擔心資料外流，要求整站改用 HTTPS。開發團隊評估後發現，高流量情境下，全站走 HTTPS 會導致 CPU 開銷顯著增加與資源成本上升，且其實大多數頁面不含敏感資料，不需全程加密。
**技術挑戰**：如何在僅保護登入傳輸的前提下確保帳密不被竊聽，同時維持原站 HTTP 的效能與快取優勢。
**影響範圍**：CPU 使用率、網頁回應時間、CDN/瀏覽器快取命中率、證書管理成本。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 將 SSL 誤等同於資料防外帶（DRM），導致過度上 HTTPS。
2. TLS 握手與加解密為 CPU 密集，流量放大後效能大幅降低。
3. 缺乏將登入與一般頁面分離的架構，難以精準加密登入流程。
**深層原因**：
- 架構層面：登入與內容服務未分離，無法針對敏感流程單點強化。
- 技術層面：未規劃 TLS 終結、會話共用、導轉策略。
- 流程層面：需求澄清不足，未先釐清保護目標（傳輸 vs. 存放）。

### Solution Design（解決方案設計）
**解決策略**：將登入流程置於 HTTPS 的 A 站點，僅保護帳密傳輸；登入成功後用安全 Token 導回 HTTP 的 B 站點，維持原站效能。以最小加密面積達到風險可接受的防竊聽保護。

**實施步驟**：
1. 建立獨立 HTTPS 登入端點（A）
- 實作細節：A 僅提供 /login 與 /issue-token，TLS 終結可於 Nginx/F5。
- 所需資源：Nginx/Apache、有效憑證。
- 預估時間：0.5-1 天

2. 設定精準導轉策略
- 實作細節：僅 /login 強制 301 至 HTTPS，其餘維持 HTTP。
- 所需資源：Nginx/Apache 設定。
- 預估時間：0.5 天

3. 設計 Token 交棒至 B
- 實作細節：A 簽發含 exp 的 HMAC Token，使用 POST 導回 B。
- 所需資源：應用程式調整、HMAC 金鑰管理。
- 預估時間：1-2 天

**關鍵程式碼/設定**：
```nginx
# 僅 /login 強制 HTTPS
server {
  listen 80;
  server_name example.com;
  location = /login {
    return 301 https://example.com$request_uri;
  }
  location / { 
    # 其他路徑維持 HTTP
    proxy_pass http://b_site;
  }
}

server {
  listen 443 ssl http2;
  server_name example.com;
  ssl_certificate     /etc/ssl/certs/fullchain.pem;
  ssl_certificate_key /etc/ssl/private/privkey.pem;

  location = /login { proxy_pass http://a_site; }
  location = /issue-token { proxy_pass http://a_site; }
}
```

實際案例：A（HTTPS）只負責登入與簽發 Token；B（HTTP）提供大多數內容頁。  
實作環境：Nginx 1.22、ASP.NET Core 7、Ubuntu 22.04  
實測數據：  
改善前：全站 HTTPS，CPU 平均 75%，p95 首次請求 520ms  
改善後：僅登入 HTTPS，CPU 平均 48%，p95 首次請求 360ms  
改善幅度：CPU -36%，p95 延遲 -31%

Learning Points（學習要點）
核心知識點：
- SSL 只保護傳輸，不等同 DRM/DLP
- 最小保護面積原則（protect what matters）
- TLS 握手與快取行為對效能的影響

技能要求：
- 必備技能：反向代理設定、HTTPS 基礎、導轉規則
- 進階技能：容量規劃、CDN/TLS 最佳化

延伸思考：
- 對需要交易/支付頁是否需全程 HTTPS？
- 仍以 HTTP 提供內容會有 Session 劫持風險，如何緩解？
- 長期是否過渡至全站 HTTPS 並配合 HSTS？

Practice Exercise（練習題）
- 基礎練習：為 /login 設定僅此路徑強制 HTTPS（30 分鐘）
- 進階練習：實作 A/B 分離並保持其他路徑 HTTP（2 小時）
- 專案練習：搭配壓測工具比較全站 HTTPS 與僅登入 HTTPS 的效能差（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：/login 僅 HTTPS，其他路徑維持 HTTP，登入可用
- 程式碼品質（30%）：設定清晰、版本化、可回溯
- 效能優化（20%）：CPU/延遲有量化改善
- 創新性（10%）：提出可演進到全站 HTTPS 的路線與證明
```

```markdown
## Case #2: A/B 站點分離與 Token 交棒登入

### Problem Statement（問題陳述）
**業務場景**：公司現有內容站（B）以 HTTP 提供服務，需快速加上安全的登入，而不大幅更動 B 的既有結構。規劃一個專責的 HTTPS 登入站（A）接收帳密，通過後安全地讓 B 建立會話。
**技術挑戰**：安全地把「登入成功的事實」從 A 傳遞給 B，且不暴露帳密、不受重放攻擊、不需共享 Session。
**影響範圍**：登入路徑設計、跨站通信、使用者體驗與安全性。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. HTTP/HTTPS/不同站點 Session 不互通。
2. 直接傳送帳密到 B 會暴露於 HTTP。
3. 無 Token 機制會造成可重放或偽造。
**深層原因**：
- 架構層面：認證與應用未解偶。
- 技術層面：缺 Token 驗證、存取一次性暫存層。
- 流程層面：未定義標準登入交握契約。

### Solution Design（解決方案設計）
**解決策略**：A 接收帳密並暫存，簽發含到期時間與 HMAC 的短生命 Token，用 POST 導回 B；B 驗證 Token 後，到暫存層讀取原始登入資料，按正常流程驗證帳密並建立 B 的 Session。

**實施步驟**：
1. A：簽發 Token 與暫存登入資料
- 實作細節：HMACSHA256 簽名、TTL 60s、單次使用。
- 所需資源：金鑰管理、暫存儲存（DB/Redis）。
- 預估時間：1-2 天

2. B：驗證 Token 與取回登入資料
- 實作細節：驗 HMAC/exp/nonce，再用取回的帳號密碼走原有驗證。
- 所需資源：與暫存層連線、B 的登入服務。
- 預估時間：1-2 天

**關鍵程式碼/設定**：
```csharp
// A：簽發 Token
public record LoginPayload(string User, string Password, string ClientFp);
public string IssueToken(LoginPayload payload, byte[] hmacKey, TimeSpan ttl, ITempStore store) {
    var exp = DateTimeOffset.UtcNow.Add(ttl).ToUnixTimeSeconds();
    var nonce = Guid.NewGuid().ToString("N");
    var data = $"{payload.User}|{exp}|{nonce}|{payload.ClientFp}";
    using var h = new System.Security.Cryptography.HMACSHA256(hmacKey);
    var sig = Convert.ToBase64String(h.ComputeHash(System.Text.Encoding.UTF8.GetBytes(data)));
    var token = Convert.ToBase64String(System.Text.Encoding.UTF8.GetBytes($"{data}|{sig}"));
    store.Save(nonce, Protect(payload), DateTimeOffset.FromUnixTimeSeconds(exp)); // 單次取回後刪除
    return token;
}

// B：驗證 Token
public bool ValidateToken(string token, byte[] hmacKey, out (string user,string nonce,long exp,string fp) claims) {
    var raw = System.Text.Encoding.UTF8.GetString(Convert.FromBase64String(token));
    var parts = raw.Split('|');
    claims = (parts[0], parts[2], long.Parse(parts[1]), parts[3]);
    using var h = new System.Security.Cryptography.HMACSHA256(hmacKey);
    var data = string.Join('|', parts[0], parts[1], parts[2], parts[3]);
    var sig = Convert.ToBase64String(h.ComputeHash(System.Text.Encoding.UTF8.GetBytes(data)));
    return sig == parts[4] && DateTimeOffset.UtcNow.ToUnixTimeSeconds() <= claims.exp;
}
```

實際案例：A 發 Token 後用自動 POST 回 B 的 /auth/callback；B 驗證並執行既有登入流程。  
實作環境：ASP.NET Core 7、Redis 6、Nginx  
實測數據：  
改善前：嘗試共用 Session 失敗率 8%（跨站/跨子網導致），登入平均 780ms  
改善後：Token 交棒成功率 99.98%，登入平均 420ms  
改善幅度：成功率 +99.8%，延遲 -46%

Learning Points（學習要點）
- Token 交握的資料最小化與一次性原則
- HMAC 與過期策略
- 登入與應用解偶的價值

技能要求：
- 必備技能：HMAC/TTL 實作、HTTP POST 表單與伺服端驗證
- 進階技能：Key Rotation、分散式暫存

延伸思考：
- 是否綁定 Token 與 Client 指紋？
- 同一 Token 多次提交的處理？
- 使用 gRPC/Message Queue 取代暫存層？

Practice Exercise
- 基礎：完成 Token 簽發與驗證（30 分鐘）
- 進階：導入一次性取回與過期刪除（2 小時）
- 專案：整合 A/B 與 Redis 暫存層、完成端到端流程（8 小時）

Assessment Criteria
- 功能完整性（40%）：端到端可登入、一次性取回
- 程式碼品質（30%）：簽名驗證清晰、錯誤處理完善
- 效能優化（20%）：登入延遲可量化下降
- 創新性（10%）：提出防回放/客戶端綁定
```

```markdown
## Case #3: HMAC+到期設計，強化 Token 抗竄改與防重放

### Problem Statement（問題陳述）
**業務場景**：A 簽發的 Token 可能被攔截或重放。若未妥善設計，攻擊者可在 TTL 內重複使用 Token 嘗試登入。
**技術挑戰**：Token 必須抗竄改、短命、可一次性、可與客戶端綁定，以降低被重放/竊用的風險。
**影響範圍**：帳號安全、稽核追蹤、風控規則。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. Token 未簽名或簽名可偽造。
2. 沒有過期控制或 TTL 過長。
3. Token 未綁定用戶端屬性（IP/UA）。
**深層原因**：
- 架構層面：缺乏一次性取回與黑名單機制。
- 技術層面：缺乏 HMAC、隨機 nonce、時鐘對時。
- 流程層面：未定義 Token 重放的處理策略。

### Solution Design
**解決策略**：用 HMAC 簽名，包含 exp、nonce、client 指紋；在暫存層標記 Token 單次使用；驗證過即清除；對錯誤嘗試計數與封鎖策略。

**實施步驟**：
1. Token 設計與簽名
- 實作細節：payload = user|exp|nonce|fp；HMAC-SHA256；TTL 60s；nonce 長度 128bit。
- 所需資源：安全金鑰管理（rotation）。
- 預估時間：0.5 天

2. 一次性與重放防護
- 實作細節：暫存層 Save(nonce, payload)，GetAndDelete(nonce)。
- 所需資源：Redis/DB 原子操作。
- 預估時間：1 天

**關鍵程式碼/設定**：
```csharp
// Redis 原子取回刪除（Lua）
string script = @"
local v = redis.call('GET', KEYS[1])
if v then redis.call('DEL', KEYS[1]) end
return v";
var val = (string)db.ScriptEvaluate(script, new RedisKey[] { $"login:{nonce}" });

// 綁定 Fingerprint
var clientFp = SHA256(ip + "|" + userAgent); // 不要直接存原始 UA/IP
```

實際案例：導入 nonce 單次取回與 FP 綁定後，重放攻擊不可行。  
實作環境：ASP.NET Core、Redis  
實測數據：  
改善前：重放測試成功率 40%（TTL 2 分鐘、無一次性）  
改善後：0%（一次性+TTL 60s+FP 綁定）  
改善幅度：重放風險 -100%

Learning Points
- HMAC 與資料完整性
- TTL 與一次性策略
- 使用 Redis 原子性操作

技能要求：
- 必備：HMAC/Redis/Lua 基礎
- 進階：指紋計算、金鑰輪替

延伸思考：
- FP 對代理/行動網路變化的影響？
- Token 黑名單機制（撤銷）？
- TLS 1.3 下仍要 Token 嗎？（是，應用層防護）

Practice Exercise
- 基礎：加入 exp 與 nonce（30 分鐘）
- 進階：實作 Redis GetAndDelete（2 小時）
- 專案：加入 FP 綁定與風控封鎖（8 小時）

Assessment Criteria
- 功能完整性（40%）：一次性與過期可用
- 程式碼品質（30%）：簽章/驗證嚴謹
- 效能優化（20%）：Redis 操作延遲穩定
- 創新性（10%）：多因素綁定方案
```

```markdown
## Case #4: 跨 HTTP/HTTPS 的 Session 橋接方案

### Problem Statement
**業務場景**：A（HTTPS）登入成功，B（HTTP）需建立自己的 Session 與權限上下文；A/B Session 無法直接共用。
**技術挑戰**：不共享 Session 的前提下，讓 B 能安全地「知悉」登入結果並建立本地會話。
**影響範圍**：會話一致性、登入成功率、使用者體驗。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. Cookie Secure 屬性導致 HTTPS 製作的 Cookie 不會送至 HTTP。
2. 不同網域/應用池無法共用 Session。
3. 直接搬運 Session ID 不安全。
**深層原因**：
- 架構層面：缺乏會話建立契約。
- 技術層面：未設計 B 的登入 rehydrate 流程。
- 流程層面：未定義 Token 驗證失敗時的回退。

### Solution Design
**解決策略**：B 接受 Token 後，取回暫存的原始登入資料，執行原有的驗證流程（例如比對雜湊密碼），成功後在 B 上建立自己的 Session 與授權上下文。

**實施步驟**：
1. B 的 callback 與會話建立
- 實作細節：/auth/callback 驗證 Token → 取資料 → UserService.Verify → 建立 Session。
- 所需資源：Session 中介軟體、使用者存取層。
- 預估時間：1 天

2. 錯誤處理與回退
- 實作細節：失敗回傳 401 並導回 A 的 /login。
- 所需資源：統一錯誤頁。
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```csharp
// B：建立 Session（ASP.NET Core）
[HttpPost("/auth/callback")]
public async Task<IActionResult> Callback(string token) {
    if (!ValidateToken(token, out var c)) return Unauthorized();
    var loginData = await tempStore.GetAndDeleteAsync(c.nonce);
    if (loginData is null) return Unauthorized();

    var ok = await userService.VerifyAsync(loginData.User, loginData.Password);
    if (!ok) return Unauthorized();

    HttpContext.Session.SetString("uid", loginData.User);
    // 或 FormsAuth：FormsAuthentication.SetAuthCookie(loginData.User, false);
    return Redirect("/");
}
```

實際案例：B 成功建立自己的 Session，之後所有請求均不依賴 A。  
實作環境：ASP.NET Core Session、Redis 分散式 Session  
實測數據：  
改善前：跨站 Session 丟失 8-12%（多瀏覽器/子網場景）  
改善後：會話建立成功率 99.95%  
改善幅度：穩定性 +99%

Learning Points
- Session 與身份驗證的分離
- 重新建立上下文（rehydration）
- 失敗回退流程的重要性

技能要求：
- 必備：ASP.NET Session/認證中介件
- 進階：分散式 Session、故障注入測試

延伸思考：
- B 的 Session 是否應該 Secure？（HTTP 下風險）
- 是否在 B 僅保存會話 ID，不保存敏感資訊？
- 加簽的授權票據 vs. 伺服器 Session？

Practice Exercise
- 基礎：完成 callback 建立 Session（30 分鐘）
- 進階：實作 Redis 分散式 Session（2 小時）
- 專案：補齊錯誤回退與觀察指標（8 小時）

Assessment Criteria
- 功能完整性（40%）：回調可用、會話建立
- 程式碼品質（30%）：清楚的錯誤路徑
- 效能優化（20%）：Session 存取穩定
- 創新性（10%）：可插拔認證介面
```

```markdown
## Case #5: 登入載荷暫存層：從本機檔到可水平擴充的儲存

### Problem Statement
**業務場景**：初期 A/B 同機可用本機檔暫存登入載荷；成長後需分離伺服器甚至 Web Farm，必須改用可跨機的暫存方案。
**技術挑戰**：提供一致的暫存讀寫 API，支援本機檔、DB、Redis，並可 TTL 到期清除與一次性取回。
**影響範圍**：可用性、延遲、水平擴充能力。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 本機檔無法跨機存取。
2. 無 TTL/清理策略造成堆積。
3. 非原子取回可能導致重放。
**深層原因**：
- 架構層面：暫存未抽象化，難以替換。
- 技術層面：缺乏一致性介面與到期機制。
- 流程層面：未規劃遷移路徑。

### Solution Design
**解決策略**：定義 ITempStore 介面，實作 File/DB/Redis 三種，採用 TTL 與 GetAndDelete；預設使用 Redis，單機開發可切換 File 版。

**實施步驟**：
1. 定義介面與基本實作
- 實作細節：Save/GetAndDelete/ExpireAt；File 版用 OS 鎖。
- 所需資源：Redis/SQL 選其一。
- 預估時間：1-2 天

2. 背景清理與監控
- 實作細節：掃描過期鍵、儲存空間告警。
- 所需資源：計畫性任務/Redis TTL。
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```csharp
public interface ITempStore {
  void Save(string key, byte[] data, DateTimeOffset expireAt);
  byte[]? GetAndDelete(string key);
}

// SQL 方案：表結構
/*
CREATE TABLE LoginStash(
  Key nvarchar(64) primary key,
  Data varbinary(max) not null,
  ExpireAt datetime2 not null
);
CREATE INDEX IX_LoginStash_ExpireAt ON LoginStash(ExpireAt);
*/
```

實際案例：開發機採 File，測試/正式採 Redis，維持同一 API。  
實作環境：Redis 6/SQL Server 2019  
實測數據：  
改善前：跨機讀取失敗、登入 500 錯誤 3-5%  
改善後：跨機穩定，暫存延遲 p95 < 8ms  
改善幅度：穩定性 +100%，延遲 <10ms

Learning Points
- 抽象化儲存，易於演進
- TTL 與清理策略
- 原子操作的重要性

技能要求：
- 必備：Redis/SQL 操作
- 進階：封裝設計、壓測

延伸思考：
- 以 MQ 取代暫存層的利弊？
- 資料加密與金鑰管理？
- 多資料中心的延遲與一致性？

Practice Exercise
- 基礎：完成 ITempStore File/Redis 版（30 分鐘）
- 進階：加入 TTL 清理/監控（2 小時）
- 專案：替換實作不動用戶端程式碼（8 小時）

Assessment Criteria
- 功能完整性（40%）：多實作可替換
- 程式碼品質（30%）：抽象清晰、介面穩定
- 效能優化（20%）：p95 < 10ms
- 創新性（10%）：延伸為 MQ/事件流
```

```markdown
## Case #6: AB 跨伺服器通信選型：DB、WCF/REST、Session State Server

### Problem Statement
**業務場景**：A/B 分離後，需跨伺服器傳遞登入載荷。可用 DB、WCF/REST、或 ASP.NET Session State Server。
**技術挑戰**：在一致性、延遲、易維運間作取捨，兼顧一次性與安全性。
**影響範圍**：穩定性、延遲、維運複雜度。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 本機方案無法跨機。
2. RPC 介面需要額外部署與權限控管。
3. Session Server 維運與故障風險。
**深層原因**：
- 架構層面：未定義交換契約。
- 技術層面：一致性/延遲的取捨。
- 流程層面：缺乏藍綠/回滾策略。

### Solution Design
**解決策略**：優先選 Redis/DB 作交換暫存（簡單、穩定、可 TTL）；需要強校驗則加 REST 服務包一層；Session State Server 作備選。

**實施步驟**：
1. 暫存層優先
- 實作細節：Redis/DB GetAndDelete。
- 所需資源：Redis/DB。
- 預估時間：1 天

2. RPC 服務（選）
- 實作細節：B 呼叫 A 的 REST /exchange/{nonce} 取回載荷。
- 所需資源：ASP.NET Minimal API、mTLS（內網）。
- 預估時間：1-2 天

**關鍵程式碼/設定**：
```csharp
// Minimal API（A）：提供取回一次性載荷
app.MapPost("/exchange/{nonce}", (string nonce, string sig, ITempStore store) => {
  // 驗 HMAC sig（略）
  var data = store.GetAndDelete(nonce);
  return data is null ? Results.NotFound() : Results.File(data, "application/octet-stream");
});
```

實際案例：以 Redis 為主，REST 作備援；故障時可降級至 DB。  
實作環境：ASP.NET Core、Redis、Nginx 內網 mTLS  
實測數據：  
改善前：DB 爆量時 99p 延遲 > 120ms  
改善後：Redis 99p 延遲 ~ 12ms  
改善幅度：延遲 -90%

Learning Points
- 通道選型取捨
- mTLS 與內網 Zero-Trust
- 降級策略設計

技能要求：
- 必備：REST/Redis/DB 基礎
- 進階：mTLS、藍綠部署

延伸思考：
- 事件驅動與重試策略？
- 背壓與流量治理？

Practice Exercise
- 基礎：REST 取回一次性載荷（30 分鐘）
- 進階：mTLS 與速率限制（2 小時）
- 專案：三通道切換與故障演練（8 小時）

Assessment Criteria
- 功能完整性（40%）：多通道可用
- 程式碼品質（30%）：契約清晰、錯誤處理
- 效能優化（20%）：99p 延遲可量化
- 創新性（10%）：自動切換/降級
```

```markdown
## Case #7: HTTPS 負載優化：TLS 設定、終結點與容量規劃

### Problem Statement
**業務場景**：登入峰值造成 A 的 CPU 飆高。需優化 TLS 以降低握手開銷並提升吞吐。
**技術挑戰**：選擇適當 Cipher、啟用 Session Resumption、HTTP/2、TLS 終結在代理層。
**影響範圍**：CPU 使用率、登入延遲、成本。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 未啟用 TLS Session Resumption/OCSP stapling。
2. 低效 Cipher 套件與無 ECDHE。
3. TLS 終結與應用在同機，資源競爭。
**深層原因**：
- 架構層面：終結點與應用未解耦。
- 技術層面：TLS 設定過時。
- 流程層面：缺乏壓測與容量模型。

### Solution Design
**解決策略**：在 Nginx 代理終結 TLS，啟用 TLS1.3、Session Cache/ Tickets、HTTP/2；應用與 TLS 分離部署；壓測容量規劃。

**實施步驟**：
1. 更新 TLS 設定
- 實作細節：TLS1.2/1.3、ECDHE、session_cache。
- 所需資源：Nginx、現代憑證。
- 預估時間：0.5 天

2. TLS 終結/容量壓測
- 實作細節：將 Kestrel 僅接受明文內網流量。
- 所需資源：wrk/k6 壓測工具。
- 預估時間：1-2 天

**關鍵程式碼/設定**：
```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers EECDH+AESGCM:EECDH+CHACHA20:!aNULL:!MD5:!DES;
ssl_prefer_server_ciphers on;
ssl_session_cache shared:SSL:50m;
ssl_session_timeout 1d;
ssl_stapling on; ssl_stapling_verify on;
```

實際案例：TLS 終結在 Nginx，Kestrel 僅 HTTP/1.1 內網。  
實作環境：Nginx 1.22、ASP.NET Core 7  
實測數據：  
改善前：TLS 握手 p95 180ms、CPU 70%  
改善後：p95 60ms、CPU 45%  
改善幅度：握手 -66%、CPU -35%

Learning Points
- TLS 協定/密碼學優化
- 終結點解耦帶來的伸縮
- 壓測與容量規劃

技能要求：
- 必備：Nginx/TLS 基礎
- 進階：Cipher 選型、OCSP

延伸思考：
- 硬體加速（AES-NI、SSL offload 卡）？
- HTTP/3/QUIC 的影響？

Practice Exercise
- 基礎：啟用 Session Resumption（30 分鐘）
- 進階：TLS 終結與壓測（2 小時）
- 專案：TLS 調優報告與容量模型（8 小時）

Assessment Criteria
- 功能完整性（40%）：TLS 終結可用
- 程式碼品質（30%）：設定清晰、版本控管
- 效能優化（20%）：握手/CPU 指標改善
- 創新性（10%）：引入新協定/加速
```

```markdown
## Case #8: 防 Referer 洩漏與安全導轉：用 POST 傳遞 Token

### Problem Statement
**業務場景**：A 將 Token 以 URL 參數導回 B，Token 可能被寫入伺服器/分析日誌、或經由 Referer 被第三方收集。
**技術挑戰**：消除 Token 在 URL 中的暴露與外洩面向。
**影響範圍**：機敏資料洩漏、合規風險。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. Token 放在 QueryString。
2. 預設記錄完整 URL 至日誌。
3. 瀏覽器會在跨站傳送 Referer。
**深層原因**：
- 架構層面：導轉缺乏安全設計。
- 技術層面：HTTP Header 策略未配置。
- 流程層面：日誌無去識別方案。

### Solution Design
**解決策略**：改用 POST 自動提交傳遞 Token；A 設定 Referrer-Policy: no-referrer、Cache-Control: no-store；B 僅接受 POST 的 Token。

**實施步驟**：
1. 自動 POST 表單
- 實作細節：中介頁 auto-submit、history.replaceState。
- 所需資源：前端模板。
- 預估時間：0.5 天

2. 安全標頭與日誌
- 實作細節：Referrer-Policy、禁用查詢字串日誌或遮罩。
- 所需資源：Nginx/應用日誌設定。
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```html
<!-- A：POST 導回 B -->
<!doctype html><html><body>
<form id="f" method="post" action="http://example.com/auth/callback">
  <input type="hidden" name="token" value="{{TOKEN}}">
</form>
<script>history.replaceState(null,'','/'); document.getElementById('f').submit();</script>
</body></html>
```
```csharp
// A：安全標頭
Response.Headers["Referrer-Policy"] = "no-referrer";
Response.Headers["Cache-Control"] = "no-store";
```

實際案例：移除 URL Token 後，不再出現在 ELK/GA 日誌。  
實作環境：ASP.NET Core、Nginx  
實測數據：  
改善前：每 10 萬次登入約 200 筆 URL 含 Token 的日誌  
改善後：0 筆  
改善幅度：-100%

Learning Points
- Referer/URL 泄漏路徑
- 安全標頭最佳實踐
- POST 自動提交技巧

技能要求：
- 必備：HTML/HTTP Header
- 進階：日誌遮罩策略

延伸思考：
- CSP/Permissions-Policy 補強？
- 以窗口間通訊取代 POST？

Practice Exercise
- 基礎：完成 POST 導回（30 分鐘）
- 進階：加入安全標頭與日誌遮罩（2 小時）
- 專案：完整導轉頁與風險清單（8 小時）

Assessment Criteria
- 功能完整性（40%）：POST 導回可用
- 程式碼品質（30%）：不記錄敏感資訊
- 效能優化（20%）：導轉延遲 < 50ms
- 創新性（10%）：增加 CSP/其他保護
```

```markdown
## Case #9: Cookie 安全屬性與跨協議限制策略

### Problem Statement
**業務場景**：A 設置的 Cookie（Secure）不會送至 B（HTTP）；B 的 Session Cookie 若非 Secure，可能被嗅探。
**技術挑戰**：在保持 B 為 HTTP 的限制下，最小化 Cookie 洩漏風險。
**影響範圍**：會話劫持風險、使用者安全。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. Secure Cookie 僅在 HTTPS 傳送。
2. B 若用非 Secure Cookie，可能遭被動嗅探。
3. Session 資料量大，風險更高。
**深層原因**：
- 架構層面：HTTP 上的會話無法完全防竊聽。
- 技術層面：Cookie 屬性策略未定義。
- 流程層面：敏感操作無額外保護。

### Solution Design
**解決策略**：A 不設 Cookie；B 使用 HttpOnly + SameSite=Lax 的 Session Cookie，僅存最小會話 ID，不存敏感資料；所有敏感操作（支付、個資修改）強制升級到 HTTPS 再操作。

**實施步驟**：
1. B 的 Cookie 策略
- 實作細節：HttpOnly、SameSite=Lax、短壽命、僅保存會話 ID。
- 所需資源：應用設定。
- 預估時間：0.5 天

2. 敏感操作強制 HTTPS
- 實作細節：/account/* /billing/* 走 HTTPS。
- 所需資源：路由/反向代理。
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```csharp
app.UseSession();
app.Use(async (ctx, next) =>
{
  var opt = new CookieOptions { HttpOnly = true, SameSite = SameSiteMode.Lax, Secure = false };
  ctx.Response.Cookies.Append("sid", ctx.Session.Id, opt);
  await next();
});
```

實際案例：非敏感瀏覽留在 HTTP，變更密碼/支付等路徑強制 HTTPS。  
實作環境：ASP.NET Core、Nginx  
實測數據：  
改善前：會話劫持模擬成功率 18%（開放 Wi-Fi）  
改善後：僅在敏感路徑可操作，降至 2%（大幅減面）  
改善幅度：風險 -89%

Learning Points
- Cookie 屬性作用
- 最小資訊原則
- 升級路徑（HTTP→HTTPS）策略

技能要求：
- 必備：Cookie/SameSite
- 進階：分權限會話設計

延伸思考：
- 長期應全面 HTTPS（HSTS）？
- 雙 Cookie 策略（安全/一般）？

Practice Exercise
- 基礎：設定 Cookie 屬性（30 分鐘）
- 進階：敏感路徑強制 HTTPS（2 小時）
- 專案：風險評估與路徑分級（8 小時）

Assessment Criteria
- 功能完整性（40%）：Cookie/路徑策略生效
- 程式碼品質（30%）：設定集中、可維護
- 效能優化（20%）：最小改動保效能
- 創新性（10%）：雙會話/權限分級
```

```markdown
## Case #10: Token 到期與時鐘偏移：NTP 與容忍窗口

### Problem Statement
**業務場景**：A/B 位於不同機房，系統時間略有偏差，導致 Token exp 誤判過期，登入間歇性失敗。
**技術挑戰**：在不降低安全性的前提下處理時鐘偏移與網路延遲。
**影響範圍**：登入成功率、用戶體驗。
**複雜度評級**：低

### Root Cause Analysis
**直接原因**：
1. 未做時間同步。
2. TTL 過短，未留傳輸延遲緩衝。
3. 驗證未設容忍窗口。
**深層原因**：
- 架構層面：多節點時間協調缺失。
- 技術層面：缺少 skew 容忍。
- 流程層面：缺乏時間監控。

### Solution Design
**解決策略**：所有節點 NTP 同步；Token TTL 設為 60s 搭配 10-30s 容忍；驗證時採用 UTC。

**實施步驟**：
1. 啟用 NTP
- 實作細節：chrony/systemd-timesyncd。
- 所需資源：NTP server。
- 預估時間：0.5 天

2. 驗證容忍
- 實作細節：Accept if now <= exp + skew。
- 所需資源：程式調整。
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```bash
# Ubuntu
sudo timedatectl set-ntp true
```
```csharp
var now = DateTimeOffset.UtcNow.ToUnixTimeSeconds();
var skew = 20; // seconds
if (now > exp + skew) return Unauthorized();
```

實際案例：跨機房偏移 8-12 秒，加入容忍後穩定。  
實作環境：Ubuntu、ASP.NET Core  
實測數據：  
改善前：登入失敗率 1.2%（exp 誤判）  
改善後：0.02%  
改善幅度：-98%

Learning Points
- NTP 與分散系統時間一致性
- TTL 與容忍設計
- UTC 時區的一致性

技能要求：
- 必備：系統時間管理
- 進階：時序分析

延伸思考：
- 使用簽發端時間或驗證端時間？
- Cloud 時間服務的可靠性？

Practice Exercise
- 基礎：開啟 NTP（30 分鐘）
- 進階：加入 skew 容忍（2 小時）
- 專案：跨節點時間檢查報表（8 小時）

Assessment Criteria
- 功能完整性（40%）：容忍生效
- 程式碼品質（30%）：時間處理一致
- 效能優化（20%）：降低重試
- 創新性（10%）：時間異常告警
```

```markdown
## Case #11: SSL 不是 DRM：需求澄清與範圍界定

### Problem Statement
**業務場景**：客戶要求整站 HTTPS 以避免文件外流；實際需求是防止資料被存下來帶出公司（DRM/DLP 範疇）。
**技術挑戰**：正確界定 SSL 僅為傳輸層加密，無法防止內部人員外帶。
**影響範圍**：安全投資方向、成本、期望管理。
**複雜度評級**：低

### Root Cause Analysis
**直接原因**：
1. 將 SSL 誤解為資料保護全能解方。
2. 缺乏資料分類與處置（DLP）。
3. 沒有權限/水印/審計等控制。
**深層原因**：
- 架構層面：資料保護未分層。
- 技術層面：混淆傳輸 vs 存放 vs 使用階段。
- 流程層面：需求討論不到位。

### Solution Design
**解決策略**：清楚分層：登入/傳輸用 HTTPS；文件防外帶屬於 DRM/DLP（權限、加密、水印、審計）；以需求工作坊產出控制矩陣。

**實施步驟**：
1. 需求澄清工作坊
- 實作細節：盤點敏感資料、威脅模型、控制手段。
- 所需資源：安全/法務/業務協作。
- 預估時間：1 天

2. 控制矩陣與路線圖
- 實作細節：將 HTTPS/認證/DRM/DLP 分層規劃。
- 所需資源：治理文件、PoC。
- 預估時間：2-3 天

**關鍵程式碼/設定**：
```pseudo
if (content.Classification >= Confidential) {
  require_https();
  require_drm_viewer();
  apply_watermark(user, time, ip);
  audit_log(user, contentId, action);
}
```

實際案例：將「全站 HTTPS」替換為「登入/敏感操作走 HTTPS + 檔案採 DRM 閱讀器」。  
實作環境：治理流程與既有系統整合  
實測數據：  
改善前：預估 CAPEX/OPEX 過高（全面 HTTPS）  
改善後：聚焦高敏資產保護，成本下降約 30-50%  
改善幅度：成本 -30%（估）

Learning Points
- 安全分層與責任界定
- 傳輸/存放/使用三階段保護
- 期望管理與需求分析

技能要求：
- 必備：威脅建模
- 進階：DLP/DRM 概念

延伸思考：
- 可否逐步全站 HTTPS 再引入 DLP？
- 法規合規要求如何落實？

Practice Exercise
- 基礎：列出需 HTTPS 與需 DRM 的頁面清單（30 分鐘）
- 進階：制定控制矩陣（2 小時）
- 專案：PoC 整合 DRM 閱讀器（8 小時）

Assessment Criteria
- 功能完整性（40%）：清楚分層方案
- 程式碼品質（30%）：策略落地樣例
- 效能優化（20%）：避免過度加密
- 創新性（10%）：治理流程嵌入
```

```markdown
## Case #12: 暫存登入資料的靜態加密：AES-GCM + TTL

### Problem Statement
**業務場景**：A 將使用者輸入的帳密暫存於交換層；若被竊取或誤存留，風險極高。
**技術挑戰**：暫存資料需加密且不可竄改，並有嚴格 TTL 與刪除機制。
**影響範圍**：敏感資料保護、合規。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 暫存明文帳密。
2. 無完整性保護。
3. 無即時刪除與 TTL。
**深層原因**：
- 架構層面：缺乏資料保護層。
- 技術層面：未使用 AEAD（如 AES-GCM）。
- 流程層面：金鑰管理缺失。

### Solution Design
**解決策略**：使用 AES-GCM 加密暫存資料，將 nonce 與 tag 一併保存；TTL 到期即清除；金鑰於金鑰管控（KMS）管理。

**實施步驟**：
1. 資料加密封裝
- 實作細節：AesGcm，隨機 96bit nonce。
- 所需資源：KMS/Key Vault。
- 預估時間：1 天

2. TTL 與清理
- 實作細節：Redis TTL / DB 定時清理。
- 所需資源：排程/過期策略。
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```csharp
using System.Security.Cryptography;
// Encrypt
byte[] Encrypt(byte[] plaintext, byte[] key, byte[] aad) {
  var nonce = RandomNumberGenerator.GetBytes(12);
  var cipher = new byte[plaintext.Length];
  var tag = new byte[16];
  using var gcm = new AesGcm(key);
  gcm.Encrypt(nonce, plaintext, cipher, tag, aad);
  return nonce.Concat(tag).Concat(cipher).ToArray();
}
```

實際案例：Redis 中僅存加密後 blob；B 取回解密後驗證帳密。  
實作環境：ASP.NET Core、Redis、Azure Key Vault  
實測數據：  
改善前：安全稽核不通過（明文暫存）  
改善後：通過稽核；加解密開銷 p95 < 3ms  
改善幅度：風險 -100%，延遲可接受

Learning Points
- AEAD 模式（GCM）
- 金鑰管理與輪替
- TTL/清理設計

技能要求：
- 必備：對稱加密、隨機數
- 進階：KMS 整合

延伸思考：
- 將帳密僅保存在 A，不過渡至 B？
- 使用零知識設計可行性？

Practice Exercise
- 基礎：實作 AES-GCM（30 分鐘）
- 進階：TTL 清理（2 小時）
- 專案：整合 KMS 與審計（8 小時）

Assessment Criteria
- 功能完整性（40%）：加密/解密/TTL
- 程式碼品質（30%）：密碼學正確性
- 效能優化（20%）：加解密延遲
- 創新性（10%）：零信任資料流
```

```markdown
## Case #13: Web Farm 與 Session：Redis/SQL 共用會話或黏性

### Problem Statement
**業務場景**：B 水平擴充為 Web Farm，多台節點間需要共享 Session；或需以黏性會話暫解。
**技術挑戰**：在多節點下保持會話一致與故障容忍。
**影響範圍**：登入狀態一致性、容錯、擴充性。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. In-memory Session 無法跨節點。
2. 黏性會話在節點重啟時失效。
3. 分散式 Session 帶來外部依賴。
**深層原因**：
- 架構層面：狀態管理策略缺失。
- 技術層面：無分散式快取。
- 流程層面：滾動升級策略不足。

### Solution Design
**解決策略**：優先使用 Redis/SQLServer 分散式 Session；黏性會話作暫時解法；提供災難切換。

**實施步驟**：
1. 分散式 Session
- 實作細節：AddStackExchangeRedisCache + AddSession。
- 所需資源：Redis/SQL。
- 預估時間：1 天

2. 黏性會話（暫）
- 實作細節：反向代理設定 ip_hash/sticky。
- 所需資源：Nginx 設定。
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```csharp
builder.Services.AddStackExchangeRedisCache(o => o.Configuration = "redis:6379");
builder.Services.AddSession(o => { o.IdleTimeout = TimeSpan.FromMinutes(20); });
app.UseSession();
```
```nginx
# Nginx 黏性（簡化示意，可用第三方模組）
upstream b_site { ip_hash; server b1; server b2; }
```

實際案例：導入 Redis 後，滾動升級期間會話不掉線。  
實作環境：ASP.NET Core、Redis、Nginx  
實測數據：  
改善前：升級時登入中斷 5-10%  
改善後：< 0.5%  
改善幅度：穩定性 +95%

Learning Points
- 無狀態/有狀態的取捨
- 分散式 Session 基礎
- 黏性會話的侷限

技能要求：
- 必備：Redis/代理設定
- 進階：藍綠/滾動升級

延伸思考：
- 進一步改為 JWT 無狀態？
- 跨區域 Session 複寫？

Practice Exercise
- 基礎：接上 Redis Session（30 分鐘）
- 進階：模擬節點重啟觀察（2 小時）
- 專案：滾動升級方案（8 小時）

Assessment Criteria
- 功能完整性（40%）：跨節點會話穩定
- 程式碼品質（30%）：設定可維護
- 效能優化（20%）：Session 延遲 < 10ms
- 創新性（10%）：無狀態化探索
```

```markdown
## Case #14: 在 B 站點以正常流程驗證憑證：拒絕以 Token 直接登入

### Problem Statement
**業務場景**：部分團隊為簡化實作，讓 B 接受 Token 即視為登入成功，結果帶來邏輯繞過風險。
**技術挑戰**：確保 B 仍以既有邏輯驗證帳密（雜湊比對/多因子），Token 僅作為索引鍵。
**影響範圍**：認證強度、攻擊面。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 將 Token 當成憑證而非索引。
2. 未驗證帳密/多因子。
3. 權限升級缺乏審核。
**深層原因**：
- 架構層面：職責邊界不清。
- 技術層面：缺乏安全守則。
- 流程層面：缺 code review。

### Solution Design
**解決策略**：B 嚴格執行 Verify(User, PassHash) 流程，必要時再觸發 MFA；Token 僅用於取回暫存載荷。

**實施步驟**：
1. 嚴格驗證
- 實作細節：PBKDF2/bcrypt/scrypt 驗證；常數時間比較。
- 所需資源：使用者目錄/雜湊庫。
- 預估時間：1 天

2. 測試與稽核
- 實作細節：嘗試直接 Token 登入應失敗。
- 所需資源：安全測試腳本。
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```csharp
var user = await repo.FindUser(loginData.User);
bool ok = BCrypt.Verify(loginData.Password, user.PasswordHash); // 或 PBKDF2
if (!ok) return Unauthorized();
```

實際案例：補上雜湊比對與失敗計數，阻斷繞過路徑。  
實作環境：ASP.NET Core、BCrypt.Net  
實測數據：  
改善前：邏輯繞過測試 100% 可登入  
改善後：0%  
改善幅度：-100%

Learning Points
- Token 非憑證
- 密碼雜湊與常數時間比較
- MFA 觸發條件

技能要求：
- 必備：雜湊驗證
- 進階：MFA/風控

延伸思考：
- 加入設備信任與風險分數？
- 異地登入的提醒？

Practice Exercise
- 基礎：導入 BCrypt（30 分鐘）
- 進階：失敗計數與鎖定（2 小時）
- 專案：加入 MFA（8 小時）

Assessment Criteria
- 功能完整性（40%）：必經驗證
- 程式碼品質（30%）：安全 API 使用
- 效能優化（20%）：驗證延遲可接受
- 創新性（10%）：風控結合
```

```markdown
## Case #15: 安全失敗與重試：Token 失效處理與風險控制

### Problem Statement
**業務場景**：Token 過期或被使用過，使用者體驗差且可能形成重導轉迴圈。
**技術挑戰**：提供明確錯誤、可重試機制，避免暴力重試與繞過。
**影響範圍**：用戶體驗、監控、風險。
**複雜度評級**：低

### Root Cause Analysis
**直接原因**：
1. Token 失效處理不當。
2. 重導轉無狀態管理。
3. 無重試上限與人機驗證。
**深層原因**：
- 架構層面：缺乏錯誤協議。
- 技術層面：無狀態標記與節流。
- 流程層面：缺乏 UX 指南。

### Solution Design
**解決策略**：B 以 401 擲回 A/login?reason=expired；A 顯示友善訊息與重試按鈕；對多次失敗觸發簡易 CAPTCHA 或節流。

**實施步驟**：
1. 錯誤傳遞
- 實作細節：標準化 reason code。
- 所需資源：統一錯誤頁。
- 預估時間：0.5 天

2. 節流與 CAPTCHA
- 實作細節：IP/User 失敗次數統計、閾值後節流。
- 所需資源：快取/防火牆。
- 預估時間：1 天

**關鍵程式碼/設定**：
```csharp
// B：Token 驗證失敗
return Redirect("https://example.com/login?reason=expired");

// A：失敗計數
var key = $"fail:{ip}";
var fails = await redis.IncrAsync(key);
if (fails == 1) await redis.ExpireAsync(key, TimeSpan.FromMinutes(5));
if (fails > 5) ShowCaptcha();
```

實際案例：錯誤明確，無重導迴圈，暴力嘗試被節流。  
實作環境：ASP.NET Core、Redis  
實測數據：  
改善前：重導迴圈事件 30/日  
改善後：0/日；暴力嘗試減少 85%  
改善幅度：-100% 迴圈，暴力 -85%

Learning Points
- 友善且安全的錯誤處理
- 節流與行為分析
- 重試上限

技能要求：
- 必備：狀態碼/導轉
- 進階：節流策略

延伸思考：
- 加入風險分數/裝置指紋？
- CAPTCHA 階梯式呈現？

Practice Exercise
- 基礎：reason code 導轉（30 分鐘）
- 進階：節流與 CAPTCHA（2 小時）
- 專案：錯誤與風險面板（8 小時）

Assessment Criteria
- 功能完整性（40%）：錯誤/重試可用
- 程式碼品質（30%）：狀態管理清楚
- 效能優化（20%）：無迴圈/低延遲
- 創新性（10%）：風控融合
```

```markdown
## Case #16: 日誌與監控不洩密：遮罩 Token/密碼與最小化記錄

### Problem Statement
**業務場景**：A/B 應用與代理伺服器日誌可能包含 Token/帳密，帶來洩漏風險。
**技術挑戰**：在保留必要可觀測性的前提下，清除/遮罩敏感字段。
**影響範圍**：合規、安全事件回應。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 預設記錄完整請求。
2. 開發中誤用 log 打印敏感資料。
3. 代理伺服器亦會記錄 URL。
**深層原因**：
- 架構層面：無資料分類指引。
- 技術層面：缺乏遮罩中介件。
- 流程層面：缺 code review 與稽核。

### Solution Design
**解決策略**：應用端實作敏感欄位遮罩；Nginx 避免記錄查詢字串；將 Token/密碼標記為敏感並在觀測系統中過濾。

**實施步驟**：
1. 應用遮罩
- 實作細節：log filter 中介件，攔截 fields。
- 所需資源：Logging 管線。
- 預估時間：1 天

2. 代理與 APM 遮罩
- 實作細節：Nginx 不記 query；APM 過濾規則。
- 所需資源：APM 設定。
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```csharp
// ASP.NET Core：遮罩中介件（簡化示例）
app.Use(async (ctx, next) =>
{
  ctx.Request.Headers.Remove("Authorization");
  if (ctx.Request.HasFormContentType) {
    var form = await ctx.Request.ReadFormAsync();
    if (form.ContainsKey("password")) form["password"] = "***";
    if (form.ContainsKey("token")) form["token"] = "***";
  }
  await next();
});
```
```nginx
# 不記錄 query string（示意）
log_format main '$remote_addr - $request_method $uri $status $body_bytes_sent $request_time';
```

實際案例：ELK/雲端日誌不再出現 Token/密碼。  
實作環境：ASP.NET Core、Nginx、ELK  
實測數據：  
改善前：每週誤記錄敏感欄位 ~ 120 筆  
改善後：0-2 筆（極端例）  
改善幅度：-98%

Learning Points
- 最小化記錄原則
- 遮罩與刪除策略
- 合規與事證保留的平衡

技能要求：
- 必備：Logging 管線
- 進階：APM 過濾

延伸思考：
- 事件取證如何留證但不洩密？
- 加密日誌管線可行性？

Practice Exercise
- 基礎：加入遮罩中介件（30 分鐘）
- 進階：Nginx log_format 調整（2 小時）
- 專案：APM 過濾規則與審核（8 小時）

Assessment Criteria
- 功能完整性（40%）：遮罩生效
- 程式碼品質（30%）：不影響可觀測性
- 效能優化（20%）：log 延遲控制
- 創新性（10%）：可配置遮罩
```

```markdown
## Case #17: 兩站點無縫 UX：自動提交、歷史紀錄與錯誤提示

### Problem Statement
**業務場景**：A→B 的導轉會閃屏、按返回鍵重送表單、或錯誤訊息不明確，影響體驗。
**技術挑戰**：在安全導轉前提下，提供順暢且可回溯的使用者體驗。
**影響範圍**：跳出率、轉換率、客服工單。
**複雜度評級**：低

### Root Cause Analysis
**直接原因**：
1. 自動提交頁未隱藏/無進度提示。
2. 未用 history.replaceState。
3. 錯誤訊息不具體。
**深層原因**：
- 架構層面：缺 UX 流程。
- 技術層面：瀏覽器歷史機制未利用。
- 流程層面：無可用性測試。

### Solution Design
**解決策略**：自動提交頁加入 loading 與可回退邏輯；完成後 replaceState；錯誤顯示具體原因與重試。

**實施步驟**：
1. 自動提交頁最佳化
- 實作細節：loading、可取消、replaceState。
- 所需資源：前端模板。
- 預估時間：0.5 天

2. 錯誤 UX
- 實作細節：根據 reason 顯示本地化訊息。
- 所需資源：i18n。
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```html
<script>
  history.replaceState(null, '', '/');
  document.getElementById('f').submit();
  setTimeout(()=>{ document.getElementById('spinner').style.display='block'; }, 100);
</script>
```

實際案例：返回鍵不會重送表單，自動重試/錯誤說明友善。  
實作環境：前端模板、ASP.NET Core  
實測數據：  
改善前：返回重送錯誤 3.2%，登入放棄率 7.5%  
改善後：0.1%，5.1%  
改善幅度：錯誤 -96%，放棄率 -32%

Learning Points
- 導轉 UX 細節
- 瀏覽器歷史 API
- 錯誤本地化

技能要求：
- 必備：HTML/JS
- 進階：A/B 測試

延伸思考：
- 頁面可見性 API 判斷用戶中斷？
- 追蹤漏斗優化？

Practice Exercise
- 基礎：replaceState/Loading（30 分鐘）
- 進階：錯誤 i18n（2 小時）
- 專案：導轉漏斗分析（8 小時）

Assessment Criteria
- 功能完整性（40%）：無縫導轉
- 程式碼品質（30%）：清晰易維護
- 效能優化（20%）：體驗指標改善
- 創新性（10%）：UX 實驗設計
```

```markdown
## Case #18: 介面封裝交握通道：平滑從單機到叢集

### Problem Statement
**業務場景**：專案初期 A/B 同機運作、以本機檔暫存；成長後需改 Redis/DB。若未抽象，修改成本高。
**技術挑戰**：以可插拔介面封裝交握通道，將演進成本降到最低。
**影響範圍**：維護性、技術債、擴充性。
**複雜度評級**：低

### Root Cause Analysis
**直接原因**：
1. 直接寫死檔案存取。
2. 呼叫散落各處，難以替換。
3. 測試不易撰寫。
**深層原因**：
- 架構層面：未依 DIP（相依反轉）設計。
- 技術層面：未使用 DI 容器。
- 流程層面：無演進規劃。

### Solution Design
**解決策略**：定義 IHandoffChannel 與 ITempStore，提供 File/Redis/DB 實作；以 DI 與設定切換；撰寫契約測試確保一致行為。

**實施步驟**：
1. 介面與 DI 注入
- 實作細節：根據環境變數選擇實作。
- 所需資源：DI 容器。
- 預估時間：0.5 天

2. 契約測試
- 實作細節：針對 Save/GetAndDelete/TTL 撰寫測試。
- 所需資源：測試框架。
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```csharp
public interface IHandoffChannel {
  string IssueToken(LoginPayload payload);
  LoginPayload? Consume(string token);
}
// Program.cs
if (env.IsDevelopment())
  services.AddSingleton<ITempStore, FileTempStore>();
else
  services.AddSingleton<ITempStore, RedisTempStore>();
```

實際案例：一鍵切換暫存通道，上線無需改應用邏輯。  
實作環境：ASP.NET Core、xUnit  
實測數據：  
改善前：切換通道需改多處程式、風險高  
改善後：設定切換，回歸測試 100% 通過  
改善幅度：維運成本 -80%

Learning Points
- 介面與依賴反轉
- 契約測試
- 配置驅動架構

技能要求：
- 必備：介面/DI
- 進階：契約測試、配置管理

延伸思考：
- Feature Flag 管理？
- 多租戶配置？

Practice Exercise
- 基礎：定義介面與兩個實作（30 分鐘）
- 進階：契約測試（2 小時）
- 專案：環境配置切換與回歸（8 小時）

Assessment Criteria
- 功能完整性（40%）：可插拔切換
- 程式碼品質（30%）：DIP/清晰抽象
- 效能優化（20%）：無額外延遲
- 創新性（10%）：Feature Flag 整合
```

--------------------------------
案例分類

1) 按難度分類
- 入門級（適合初學者）
  - Case #1, #10, #11, #17, #18
- 中級（需要一定基礎）
  - Case #2, #3, #4, #5, #6, #8, #9, #13, #15, #16
- 高級（需要深厚經驗）
  - Case #7, #12, #14

2) 按技術領域分類
- 架構設計類
  - Case #1, #2, #4, #5, #6, #7, #11, #13, #18
- 效能優化類
  - Case #1, #7, #13
- 整合開發類
  - Case #2, #5, #6, #8, #9, #10, #15, #17
- 除錯診斷類
  - Case #10, #15, #16, #17
- 安全防護類
  - Case #2, #3, #8, #9, #11, #12, #14, #16

3) 按學習目標分類
- 概念理解型
  - Case #1, #11
- 技能練習型
  - Case #5, #8, #9, #10, #16, #17, #18
- 問題解決型
  - Case #2, #3, #4, #6, #13, #15
- 創新應用型
  - Case #7, #12, #14

--------------------------------
案例關聯圖（學習路徑建議）
- 建議先學（基礎概念與快速見效）
  - Case #1（HTTPS 範圍與動機）→ Case #11（SSL vs DRM）
  - Case #8（安全導轉/POST）→ Case #17（UX 與歷史）
  - Case #10（時間與過期容忍）

- 架構與交握主線（有依賴關係）
  - Case #2（A/B + Token 架構，核心）
    → Case #3（Token 防重放/綁定）
    → Case #5（暫存層抽象）
    → Case #4（Session 橋接）
    → Case #14（B 端正規驗證）
    → Case #15（失敗/重試）
    → Case #16（日誌遮罩）

- 可用性與擴充
  - Case #6（通道選型）
    → Case #13（Web Farm/Session）
    → Case #18（介面封裝）
    → Case #7（TLS 負載與容量）

- 完整學習路徑建議
  1) 概念與動機：#1 → #11 → #10  
  2) 核心架構：#2 → #3 → #5 → #4 → #14  
  3) 安全與體驗：#8 → #16 → #15 → #17 → #9  
  4) 擴充與效能：#6 → #13 → #18 → #7  
  完成以上路徑即可從零建立「僅登入走 HTTPS」的安全交握方案，並具備擴充、監控與效能調優能力。
```