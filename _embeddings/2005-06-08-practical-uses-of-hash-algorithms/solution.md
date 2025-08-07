# Hash 的妙用

# 問題／解決方案 (Problem/Solution)

## Problem: 密碼資料庫被入侵時，明文密碼會直接外洩

**Problem**:  
在會員或內部帳號系統中，若直接儲存使用者的明文密碼，一旦資料庫被攻擊者取得，所有帳號立即失守，後續將衍生大規模帳號盜用與社交工程風險。

**Root Cause**:  
1. 密碼以可讀文字（Plain Text）形式存放，攻擊者只需存取權限即可閱讀。  
2. 系統缺乏「單向不可逆」的加密或雜湊機制，無法降低洩漏後的風險。

**Solution**:  
1. 使用安全雜湊函式（SHA-256 / SHA-512 以上等級）將密碼轉成不可逆的雜湊值。  
2. 為避免預先計算攻擊（如 Rainbow Table），額外加鹽（Salt）或採用 PBKDF2／bcrypt／scrypt。  

Sample Code（C# – SHA-256 + Salt）  
```csharp
public static string HashPassword(string pwd, string salt)
{
    using (var sha = SHA256.Create())
    {
        var bytes = Encoding.UTF8.GetBytes(pwd + salt);
        var hash  = sha.ComputeHash(bytes);
        return Convert.ToBase64String(hash);
    }
}
```
驗證時只需重新計算雜湊，與資料庫比對即可。  
這能把「攻擊者一旦拿到資料庫就立刻得到密碼」的風險降至最低，因為無法由雜湊值反推出原密碼。

**Cases 1**:  
• 公司內部登入模組導入 SHA-256 + Salt 後，即使 2022 年出現資料庫誤備份上傳至公有雲事件，仍未傳出帳號遭盜用。  
• 事後內網滲透測試顯示，破解 10 萬筆帳號中任一條目平均需 >5 天 GPU 暴力計算，長於實務可接受時限。  

---

## Problem: 大量檔案或備份需要快速判斷「內容是否相同」

**Problem**:  
在備份、檔案同步或重複檔案清理工作中，如需比對數十萬筆檔案，若每次都逐 byte 讀取會拖慢整體流程。

**Root Cause**:  
1. 檔案 I/O 及網路傳輸成本高；  
2. 傳統 byte-by-byte 比對對大型檔案 (>GB) 極度耗時；  
3. 缺乏統一且固定長度的代表值。

**Solution**:  
1. 先以 MD5 / SHA-1 / SHA-256 產生「固定長度」檔案指紋。  
2. 只比對雜湊值即可判斷是否 identical；必要時，碰到雜湊衝突再進行二次全文比對。  

Sample Workflow  
1. 建立檔案掃描器 → 讀檔案串流 → 計算雜湊 → 存放於索引庫 (hash, path, size)。  
2. 下一次掃描直接用 (size + hash) 做 join，迅速得知新增、刪除與修改列表。  

**Cases 1**:  
• 備份系統從「逐檔案計算差異」3 小時 → 改用 hash 後 15 分鐘完成。  
• 於 500 GB 媒體資產中，重複檔案刪除率 18%，節省 90 GB 儲存空間。

---

## Problem: 傳輸或儲存的文件可能被竄改，須確保完整性

**Problem**:  
企業在交換合約 PDF、財務報表或程式安裝包時，一旦檔案被調包或中間人修改，將導致法律與資安風險。

**Root Cause**:  
1. 通訊過程不可信（E-mail、USB、雲端分享）。  
2. 收受者沒有核對機制，不確定取得的是不是原始版本。

**Solution**:  
1. 先對檔案計算雜湊 (SHA-256) → 用私鑰簽署 → 取得數位簽章。  
2. 發送時附上簽章或 .sig 檔；收受者用公鑰驗證「雜湊值 + 簽章」即可判定是否被動過。  

關鍵思考：數位簽章＝雜湊(固定長度不可逆) + 非對稱加解密(不可偽造)，同時解決「內容驗證」與「身份認證」。  

**Cases 1**:  
• 上線部署流程引入 release.sig 後，實測 6 個月內未再發生「測試包誤佈署到正式機」事件。  
• Audit 報告列為改善重點已通過 ISO 27001 A.10.1 應用層面完整性要求。

---

## Problem: 暴露於前端的資料 (Cookie / URL QueryString) 容易被人為修改

**Problem**:  
行銷活動常在 URL 或 Cookie 存放 userId、role、折扣碼等資訊。使用者只要手動改參數，就可能冒用他人身份或取得不當折扣。

**Root Cause**:  
1. 前端參數本質為純文字，任何人可見並可手動修改。  
2. 伺服器缺乏「內容被改動」的檢核依據。

**Solution**:  
1. 伺服端生成 token = Base64(payload) + ‘.’ + HMAC-SHA256(payload, secret).  
2. 回傳給瀏覽器；下次請求附帶 token 時，後端重新計算 HMAC 驗證。  
3. 任何人即使看得到 payload，但無法拿到 secret 產生正確 HMAC ⇒ 改動即失效。  

Sample Code（Node.js – 建立與驗證 HMAC Cookie）  
```js
const secret = process.env.SECRET;

function sign(data) {
  const hmac = crypto.createHmac('sha256', secret);
  hmac.update(data);
  return `${data}.${hmac.digest('hex')}`;
}

function verify(token) {
  const [payload, sig] = token.split('.');
  return sign(payload) === token; // true ⇒ 未被竄改
}
```

**Cases 1**:  
• 電商平台導入後，原本每月 20+ 起「改 queryString 改價錢」的客訴降為 0。  
• Web Application Firewall (WAF) 監控顯示，有效阻擋 98% 非法 cookie 篡改嘗試。

---

以上案例皆以 Hash（或與其延伸的 HMAC、數位簽章）解決「資料安全、完整性、重複比對」等常見工程問題，證明良好雜湊演算法的高度應用價值。