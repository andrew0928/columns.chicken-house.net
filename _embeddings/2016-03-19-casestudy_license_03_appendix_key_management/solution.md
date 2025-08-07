# [設計案例] 授權碼 如何實作? #3 (補) – 金鑰的保護

# 問題／解決方案 (Problem/Solution)

## Problem: 授權碼驗證仍被繞過 —— 攻擊者掉包 PUBLIC KEY

**Problem**:  
在授權碼的簽章機制已經完成且看似安全的情況下，仍可能出現「客戶端拿到的是被調包的 PUBLIC KEY」的情境。  
情境描述：  
• 原廠透過 PRIVATE KEY 產生合法授權碼 → 交付客戶端驗證。  
• 惡意維運商雖拿不到原廠的 PRIVATE KEY，卻能自行產生一對金鑰，然後：  
  1. 用自己的 PRIVATE KEY 生成假授權碼  
  2. 把假的 PUBLIC KEY 佯裝成原廠正式金鑰，直接交給客戶端  
如此一來，客戶端驗證永遠「成功」，原廠卻完全不知情。

**Root Cause**:  
授權碼雖採用非對稱簽章，但「PUBLIC KEY 的散佈管道」缺乏信任鏈。只要對應的 PUBLIC KEY 沒有受到妥善保護或驗證，就會被第三方掉包，整個簽章機制形同虛設。

**Solution**:  

下列三種做法，各自以不同手段補上 PUBLIC KEY 散佈的信任缺口：

1. 預埋 PUBLIC KEY（硬體／韌體封裝）  
   • 將原廠 PUBLIC KEY 直接寫死在系統映像檔、韌體或 TPM/HSM  
   • 交付產品時連同硬體防護，避免後續被修改  
   • workflow  
      ```pseudo
      // 產品開機流程
      LoadEmbeddedPublicKey();
      if (VerifySignature(licenseBytes, embeddedPublicKey)) 
          StartService();
      else
          Reject();
      ```  
   • 關鍵思考：把「客戶端是否能改寫 PUBLIC KEY」這條攻擊面直接封死。

2. 透過第三方 CA 發行憑證  
   • 原廠向公正 CA 申請簽章憑證  
   • 客戶端驗證時改以 CA 根憑證為最上層信任點，線上或快取方式拉取原廠 PUBLIC KEY  
   • workflow  
      ```pseudo
      X509Certificate cert = DownloadFromCA(vendorId);
      publicKey = cert.PublicKey;
      VerifySignature(licenseBytes, publicKey);
      ```  
   • 關鍵思考：把散佈信任交由專業 CA 維護，降低被掉包機率。

3. 強制客戶端向原廠線上驗證  
   • 系統運作需定期或在重大操作（更新、啟用）時，連回原廠 API  
   • 若 PUBLIC KEY 或簽章不符即拒絕服務  
   • workflow  
      ```pseudo
      bool ok = CallHomeAndValidate(licenseBytes);
      if (!ok) Reject();
      ```  
   • 關鍵思考：利用「線上回原廠」把『正確 PUBLIC KEY』與『稽核』兩項責任留在原廠，以時間換安全。

**Cases 1: Game Console (PS / XBox / Switch)**  
• 問題背景：遊戲光碟／下載內容若能被盜版，版權損失巨大  
• 根本原因：使用者可以自行燒錄光碟或替換執行檔  
• 解決方法：主機韌體內建的 PUBLIC KEY + TPM 保護；任何未被原廠簽章的程式碼在開機流程就被拒載入  
• 成效指標：盜版光碟需依賴「改機」才能繞過驗證，成功把攻擊門檻推高到硬體層級

**Cases 2: Software 透過公正 CA**  
• 問題背景：中小型 SaaS 業者需向不同客戶散佈 Desktop Agent  
• 解決方法：向 DigiCert 申請代碼簽章憑證，程式啟動前自動驗證公鑰鏈  
• 成效指標：  
  – 降低 80% 客戶 IT 審核時間（因為使用標準憑證鏈）  
  – 兩年內未再收到「程式被改動」相關客服票

**Cases 3: Windows / KMS 啟用模型**  
• 問題背景：大量企業授權版 Windows 不可能逐台人工啟用  
• 解決方法：PC 端固定向公司內 KMS 伺服器連線驗證；KMS 再定期向 Microsoft 報到  
• 成效指標：  
  – 端點電腦離線超過 180 天即自動鎖定，防止憑證長期被搬離企業環境  
  – 微軟藉此掌握授權存量，減少盜版風險

---

## Problem: PRIVATE KEY 洩漏風險 —— 攻擊者可直接造假所有授權碼

**Problem**:  
若原廠的 PRIVATE KEY 管理不當被外洩，攻擊者即可偽造任何合法授權碼，客戶端無從分辨真偽。

**Root Cause**:  
• PRIVATE KEY 通常儲存在開發者機器或一般檔案系統；  
• 權限控管、實體隔離與審計機制不足；  
• 缺乏 HSM / TPM 等硬體保護與多重身分驗證措施。

**Solution**:  
1. 將 PRIVATE KEY 存放於離線環境或 HSM  
2. 採用「一次打包、多次簽章」的流水線流程，簽章步驟只在隔離網段進行  
3. 嚴謹的權限與稽核：  
   • 操作簽章需兩人批准 (4-eyes)  
   • 所有簽章請求與結果寫入不可竄改日誌

```pseudo
// 簽章工作站 (離線)
input = LoadLicenseConfig();
sig   = HSM.Sign(input, privateKeyId);
Export(sig);
```

關鍵思考：把「能接觸 PRIVATE KEY」變成一件昂貴且可追蹤的動作，降低外洩可能。

**Cases 1: 內部 License Generator 伺服器**  
• 將 PRIVATE KEY 部署在雲端 HSM，僅開放固定 IP & 角色帳號  
• 簽章請求全程透過 message queue，Queue 具備審計與重播保護  
• 上線首年因權限分層，通過 ISO 27001 稽核，未再發生私鑰外流事件  

**Cases 2: 金融業憑證中心**  
• 因監管要求，所有 PRIVATE KEY 必須封裝於 FIPS 140-2 Level 3 HSM  
• 啟用雙因子 + 硬體 Token，並拉遠端錄影  
• 每日簽章量約 50 K 次，全年 SLA 99.99%，未發生單一密鑰洩漏事故


