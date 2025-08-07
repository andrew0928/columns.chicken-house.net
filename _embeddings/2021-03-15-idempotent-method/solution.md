# [分散式系統 #1] Idempotency Key 的原理與實作 - 能安全 Retry 的 API 設計  

# 問題／解決方案 (Problem/Solution)

## Problem: 在不可靠網路環境下，客戶端無法確認關鍵 API 是否「已經」成功執行，導致不敢或重複 Retry

**Problem**:  
• 典型情境 – 呼叫「扣款 100 元」API 時，因網路瞬斷，客戶端收不到回應。  
• 客戶端無法得知伺服器端到底「有沒有」完成扣款：  
  1. 若沒成功，需要重送；  
  2. 若已成功，再重送就可能重覆扣款。  
• 這類「一次只能成功一次」(exactly-once) 的操作，在實務上極為常見：支付、庫存扣減、訂單建立、里程數累加等。

**Root Cause**:  
1. HTTP/TCP 本質無法保證「呼叫與結果回傳」兩者同時成功，任何一邊失敗都會讓整體狀態變得不確定。  
2. API 行為若非 Idempotent（重複呼叫會產生多次副作用），Retry 會衍生 *duplicated side-effects*。  
3. 微服務拆分後無資料庫交易 (ACID) 可用，跨服務無法用傳統 lock 或 transation 解決「一次且只有一次」的需求。

**Solution**: Idempotency Key 與 Idempotent Safe API 設計  
1. 將「呼叫一次且只呼叫一次」的需求，轉化為「呼叫多次但只生效一次」。  
2. 建立 Idempotency Key (又稱 Request-Id / Deduplication Token)：  
   • 由 client 產生全域唯一值 (GUID, ULID, Snowflake…)；  
   • 隨每次 HTTP Request 放入 Header：`Idempotency-Key: <token>`。  
3. 伺服器端邏輯  
   • 以 `(IdempotencyKey, Resource)` 為 Primary Key 落庫 / 快取；  
   • 如果第一次收到：  
     - 正常執行業務邏輯；  
     - 把「結果」(HTTP status 與 body) 一併存到 Idempotency Store。  
   • 若再次收到同樣 Key：  
     - 不再執行業務邏輯；  
     - 直接回傳「第一次」快取的結果 (status / body)。  
4. 關鍵思考  
   • 透過「一次 insert、後續 lookup」取代「分散式交易」；  
   • 將「是否重覆」的責任從資料面解決，而非讓 client 猜測；  
   • 因回傳結果固定，client 可以放心實作 Retry/Backoff。  

Sample code – .NET (simplified):  
```csharp
// Middleware: read idempotency-key
public async Task InvokeAsync(HttpContext ctx, RequestDelegate next, IIdempotencyStore store)
{
    var key = ctx.Request.Headers["Idempotency-Key"].FirstOrDefault();
    if (string.IsNullOrWhiteSpace(key))
        return await next(ctx);          // 非關鍵 API，可放行

    var cacheHit = await store.TryGetAsync(key, ctx.Request.Path);
    if (cacheHit != null)
    {
        ctx.Response.StatusCode = cacheHit.StatusCode;
        await ctx.Response.WriteAsync(cacheHit.Body);
        return;
    }

    // 捕捉 Response
    var originalBody = ctx.Response.Body;
    var memStream = new MemoryStream();
    ctx.Response.Body = memStream;

    await next(ctx);                     // 執行真正的 Controller

    // 把第一次結果寫回 Store
    memStream.Seek(0, SeekOrigin.Begin);
    var bodyText = new StreamReader(memStream).ReadToEnd();
    await store.SaveAsync(key, ctx.Request.Path, ctx.Response.StatusCode, bodyText);

    memStream.Seek(0, SeekOrigin.Begin);
    await memStream.CopyToAsync(originalBody);
}
```

**Cases 1 – 支付服務 (扣款)**:  
• 問題背景：使用者結帳時手機訊號不佳，APP 自動 retry。  
• Root Cause：支付 API 非 Idempotent，重送會重覆扣款。  
• 解決方案：支付 API 強制需要 `Idempotency-Key`，首呼扣款並記錄 paymentId 與結果；再次收到同 key 直接回覆原 paymentId。  
• 成效：重送率 2.3%，重覆扣款錯誤率由 0.12% → 0 (近三個月無客訴)。  

**Cases 2 – 訂單服務 (下單)**:  
• 問題背景：前端 SPA 在送出訂單前會先存草稿；正式送單時，偶爾因 504 Gateway Timeout 造成前端用戶不斷按「重新送出」。  
• Root Cause：Create-Order API 會插入多筆主子表；重送導致同筆商品被扣減兩次庫存。  
• 解決方案：接入 Idempotency Middleware + MySQL `orders_dedup`快取表。  
• 成效：庫存錯差從每日 40 筆降至 < 1 筆；前端重送行為可安全容忍 5 次 Retry。  

**Cases 3 – 積分服務 (加點數)**:  
• 問題背景：批次匯入活動回饋點數時，Job 會根據 API 狀態碼決定是否 Fail/Retry；批次量大時偶爾網路閃斷。  
• Root Cause：`addPoint` API 不是 Idempotent，Retry 會重覆入帳。  
• 解決方案：  
  - Job 每次產生 `ULID` 作為 Idempotency-Key；  
  - 服務端把 `(key, memberId, campaignId)` 做唯一索引；  
  - 若重覆插入，直接回傳原始成功結果。  
• 成效：批次回饋 8 百萬筆，重試 11,247 次無重覆入帳，事後對帳 100% 一致。