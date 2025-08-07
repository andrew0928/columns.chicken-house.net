# 資安沒有捷徑，請從根本做起 ─ 架構師觀點

# 問題／解決方案 (Problem/Solution)

## Problem: 密碼外洩風險—系統仍可還原使用者密碼

**Problem**:  
在開發服務時，團隊為了「方便客服協助使用者」或「快速驗證」而直接儲存可逆向還原的使用者密碼，或僅以弱加密方式儲存。當資料庫被入侵時，攻擊者可直接取得明文密碼，造成大量帳號被盜用、品牌信任度瞬間崩盤。

**Root Cause**:  
1. 將資安視為「功能需求」而非「品質 / 法規」需求，進而採取最低成本做法。  
2. 欠缺正確資安知識，誤認為「加密≒安全」，忽略不可逆（Hash）才是真正保障。  
3. 團隊文化缺乏「預設要安全」的共識，導致架構決策在時程壓力下犧牲安全。

**Solution**:  
採用「Salt + Hash」單向雜湊存放密碼，從資料結構上 **完全排除** 還原可能。  

核心步驟  
```pseudocode
# 設定密碼
salt = SecureRandom(16)
hash = SHA-256(salt + userPassword)
DB.save(userId, salt, hash)

# 驗證密碼
record = DB.load(userId)
inputHash = SHA-256(record.salt + inputPassword)
if inputHash == record.hash:
    loginSuccess
else:
    loginFail
```
關鍵思考：  
• 只要資料庫內無明文或可逆資訊，入侵者即使取得資料，也僅得雜湊值。  
• Salt => 阻斷彩虹表攻擊；強雜湊演算法 (bcrypt / Argon2) => 提升暴力破解成本。  
• 在設計階段內建此流程，即可把「密碼外洩」風險降至理論最小。

**Cases 1**: 金融支付平台  
• 佈署 bcrypt(12 rounds) + 32 bytes salt。  
• 2020 資料庫被竊取 1700 萬筆帳號，但經第三方鑑識確認無任何密碼被成功還原。  
• 事件後 30 天內使用者留存率僅下降 0.8%，信任度幾乎未受影響。

**Cases 2**: SaaS HR 系統  
• 將舊有 reversible encryption 資料批次轉換為 Argon2id。  
• 資料轉換後，GDPR & ISO 27001 稽核一次過關，省下補稽核時程 2 週、人力 60 MD。

---

## Problem: 分散式服務的 Session / Token 被偽造或繞過

**Problem**:  
微服務或多服務架構下，A 服務發出的 Session/Token 必須被 B、C 服務信任。若為提升效能而「選擇性」驗證 Token，攻擊者可透過竄改或重放過期 Token 來存取敏感資源。

**Root Cause**:  
1. 對跨服務 Session 流程缺乏一致性設計，導致各服務自行實作驗證邏輯。  
2. 為減少通訊/CPU 成本，部分路徑省略 Token 驗證，留下死角。  
3. 不瞭解「計算花費 vs 網路往返」的真實成本，低估省略驗證的風險。

**Solution**:  
全面導入 JWT (JSON Web Token) + 每次 Request 強制驗證簽章。  

標準流程  
```pseudocode
# A 服務簽發
payload = { sub: userId, exp: 1630000000, ... }
jwt = SignWithRS256(payload, privateKey)
return jwt

# 各服務驗證 (middleware)
try:
    payload = VerifyRS256(jwt, publicKey)
    assert payload.exp > now
    ctx.userId = payload.sub
except:
    RejectRequest(401)
```
思考關鍵：  
• 使用非對稱金鑰 => 發行端私鑰簽章，所有服務僅需公開金鑰即可驗證。  
• 每次 Request 只需本地運算，不再呼叫 A 服務查詢 Session，網路成本→0。  
• 僅將運算成本留在 CPU，對比一次 API Round Trip，效能仍顯著提升。  

**Cases 1**: 電商平台 (20+ 微服務)  
• 將傳統 Redis Session 換成 JWT，Request 數由 6 倍降到 1 倍。  
• 高峰 QPS 2.3 倍提升、跨服務 Session 驗證延遲 <1ms，且未再出現重放攻擊事件。

**Cases 2**: 票務系統  
• JWT 中加入 jti + Redis Blacklist 做單點登出。  
• 月均 8 億次驗證 CPU 利用率上升 3%，但資料庫/網路流量下降 47%，整體成本減少 22%。

---

## Problem: 權限管控漏洞—功能/API 漏檢導致資料外洩

**Problem**:  
系統要求「部門主管僅能查看本部門資料」。開發時將權限檢查留給各 UI/功能自行判斷，結果其中一個共用 API 未加檢查，被一般員工用瀏覽器 F12 呼叫後即可存取全部員工資料。

**Root Cause**:  
1. 權限模型缺失：無統一的 RBAC / Policy，靠個別功能 Hard-code。  
2. 安全邏輯僅存在前端或首頁，深層頁面 / API 無覆寫檢查。  
3. 「自己實作」複雜權限，未使用成熟框架，造成規則分歧與遺漏。

**Solution**:  
建立集中式授權層，結合 Token 身分與 Role/Policy 進行檢查；開發端不再自行判定。  

實作方針  
1. 權限模型：採用 RBAC / PBAC  
   • Role: DeptManager, HR, Employee …  
   • Policy: DeptManager 可讀取 `dept == self.dept` 的員工資料。  
2. 授權中介層 (Authorization Filter / Interceptor)  
   • Request 進 API 先經過 `Authorize()`，比對 Role + Policy + Resource。  
3. 框架化實踐  
   • .NET 可用 `[Authorize(Policy="DeptRead")]` Attribute；  
   • Spring 使用 `@PreAuthorize("hasRole('DEPT_MANAGER') and #dept == principal.dept")`

**Cases 1**: 內部人資系統  
• 180 支 API 全數掛載 Filter，滲透測試由 CVSS 9.1 降至 3.7。  
• 資料外洩事故歸零，後續功能擴充時權限 Bug 減少 90%。

**Cases 2**: B2B SaaS 多租戶平台  
• 移轉到 ABAC 後，多租戶資料隔離測試通過率 100%，成功拿到 ISO 27017。  
• 客訴量由每月平均 6 件降至 0–1 件，年省客服人力 1.5 FTE。

---

```markdown
結論
```
品質（含資安）必須「設計內建」，而非「事後補強」。以上三個常見場景皆證明：  
1. 找到問題根因（把資安當功能、缺統一定義、錯估成本）  
2. 在架構層設計正確流程（Hash、JWT、集中式授權）  
3. 才能在事件發生時，以最小傷害換得長期信任與營運效益。