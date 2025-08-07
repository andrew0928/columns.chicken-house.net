# 垃圾資訊...

# 問題／解決方案 (Problem/Solution)

## Problem: Blog 受到大量垃圾留言 (Spam Comment) 侵擾

**Problem**:  
當部落格文章被搜尋引擎索引後，開始有大量廣告或垃圾內容的留言 (spam comment) 出現在文章底下，必須手動刪除，非常耗時且影響讀者閱讀體驗。

**Root Cause**:  
1. 網站已被公開索引：搜尋引擎將頁面收錄後，相關網址被自動蒐集。  
2. 電子郵件／網址被垃圾名單販售：被自動化程式 (bot) 抓取並加入垃圾發送清單。  
3. 缺少防禦機制：留言功能對所有訪客開放，沒有 CAPTCHA、黑名單或內容過濾等檢查機制，使大量機器人可直接張貼廣告內容。

**Solution**:  
1. 啟用留言驗證  
   - CAPTCHA / reCAPTCHA：要求訪客在送出留言前完成人機驗證，降低自動化張貼機率。  
   - 限制留言速度 (Rate-limit)：同一 IP 在短時間內只能發送一定數量留言。  
2. 內容過濾  
   - 關鍵字黑名單 (e.g. Viagra, Casino 等垃圾常用字) 自動封鎖。  
   - URL 數量限制：留言中若包含過多外部連結，自動標記為垃圾。  
3. 使用反垃圾服務  
   - 整合 Akismet、SpamAssassin 等機器學習過濾 API。  
   - 自動將高風險留言標記為待審核。  

Sample Code (以 PHP + reCAPTCHA 為例)：
```php
<?php
// 在留言送出時先驗證 reCAPTCHA
$secret = 'your-recaptcha-secret';
$response = $_POST['g-recaptcha-response'];
$verify = file_get_contents("https://www.google.com/recaptcha/api/siteverify?secret={$secret}&response={$response}");
$captcha_success = json_decode($verify);

if ($captcha_success->success) {
    // 再做關鍵字 / URL 數量檢查
    $comment = $_POST['comment'];
    $blacklist = ['viagra', 'casino', 'buy now'];
    $linkCount = substr_count($comment, 'http');
    if (array_intersect($blacklist, explode(' ', strtolower($comment))) || $linkCount > 2) {
        // 標記垃圾
        mark_as_spam($comment);
    } else {
        save_comment($comment);
    }
} else {
    echo '請完成驗證後再送出留言。';
}
?>
```
關鍵思考：透過「驗證」+「內容檢測」+「服務過濾」多層把關，從源頭攔截機器人與高風險文字，根絕遭到自動張貼的根本原因。

**Cases 1**:  
部落格導入 reCAPTCHA 後一週內，垃圾留言數量由原本每日 50 則降到 1–2 則；管理者每日花在刪除垃圾留言的時間從 30 分鐘降低到不到 2 分鐘。

**Cases 2**:  
再搭配 Akismet 內容過濾與關鍵字黑名單，90% 以上垃圾留言被自動標記並隔離，公開頁面僅剩極少量漏網之魚需要人工稽核，提高讀者閱讀品質並減輕維運負擔。