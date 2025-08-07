# 換了四核心，MCE就掛了...

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼把桌機的 CPU 換成四核心 Q9300 之後，Windows Media Center (MCE) 一開就當掉？
更換 CPU 會改變電腦的硬體組態，包括「可用核心數」。Windows Media Digital Rights Management (DRM) 會依據硬體組態計算並產生一支專屬於該機器的授權金鑰檔 (Indiv01.key)。當硬體變動而舊的金鑰仍在時，DRM 會判定為「媒體被非法複製到另一台電腦」，於是阻擋播放並讓 MCE/Media Player 直接閃退。

## Q: Indiv01.key 是什麼檔案？它跟這次的當機有何關係？
Indiv01.key 是 Windows Media DRM 系統為每一台電腦產生的「個別化金鑰」。播放受保護的影音時，DRM 會檢查這個金鑰是否符合目前的硬體指紋；若硬體變動 (如 CPU 核心數改變) 而金鑰未重新產生，就會觸發保護機制，造成 MCE 或 Media Player 無法播放並跳錯。

## Q: 該怎麼解決因為硬體變更導致的 DRM / MCE 播放失敗？
依照 Microsoft Knowledge Base KB891664 的指示，先清除舊的 DRM 授權與 Indiv01.key，再重新啟動系統，讓 Windows 重新個別化並產生新的金鑰。完成後，MCE 和各種播放器即可正常播放受保護的影像。

## Q: 這問題是 Microsoft 的 codec 與四核心 CPU 不相容嗎？
不是。最初看似 codec 與多核心不相容，但實際根因是 DRM 金鑰與硬體指紋不一致；與使用幾核心的 CPU 無關。

## Q: 從這次事件可得到什麼教訓？
在 Windows 平台上，任何硬體大幅變動 (尤其會改變硬體指紋的項目) 都可能讓 DRM 系統誤判為「換機非法複製」。升級硬體前需有耐心並預期可能得重設 DRM 或重灌系統，才能避免類似問題。