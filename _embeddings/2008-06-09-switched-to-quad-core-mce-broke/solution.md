# 換了四核心，MCE就掛了...

# 問題／解決方案 (Problem/Solution)

## Problem: 升級為四核心 CPU 後，MCE / WMP / MPC 全面當機，無法播放任何受 DRM 保護的電視節目或錄影檔

**Problem**:  
將桌機的雙核心 Intel E6300 CPU 更換為四核心 Q9300 之後，一啟動 Windows Vista Media Center (MCE) 觀看電視或播放既有的 *.dvr-ms 錄影檔，就立即跳出「美化過的 General Protection Failure」畫面；即使改用 Windows Media Player (WMP) 或 Media Player Classic (MPC) 也同樣閃退，完全無法觀看受保護的媒體內容。

**Root Cause**:  
1. 每台 Windows 電腦在第一次播放受保護媒體時，會根據「當時的硬體組態」產生一把專屬的 DRM 私鑰（Indiv01.key）。  
2. CPU 由 2 核變 4 核後，硬體指紋改變，Indiv01.key 與現有硬體不再匹配。  
3. Windows Media DRM 系統判定目前的媒體播放屬「疑似非法複製」，因此直接阻斷所有含 DRM 的影音播放。  
4. 錯誤訊息只顯示「錯誤模組：Indiv01.key」，未明確說明硬體變更導致授權失效，導致診斷困難。

**Solution**:  
依照 Microsoft KB891664「如果您的電腦硬體經過變更，Windows Media Digital Rights Management 系統可能會無法運作」中的流程，將舊的 DRM 金鑰/授權全部清除並重新產生。  
Workflow：  
1. 關閉所有播放程式 (MCE、WMP、MPC…)。  
2. 以系統管理員身份開啟檔案總管或命令提示字元，進入  
   `%ALLUSERSPROFILE%\Microsoft\Windows\DRM`  
3. 將整個 DRM 目錄重新命名 (例如 `DRMbackup`) 或刪除其中的 `Indiv01.key`。  
4. 重新啟動 Windows Media Player，系統會自動連線至 Microsoft 授權伺服器並依「新的硬體組態」重新產生 Indiv01.key。  
5. 再次啟動 MCE / WMP 測試播放，確認一切正常。  

為何有效：  
• 清除舊 DRM 金鑰可迫使系統重新以「新的四核心硬體指紋」產生合法授權，消除 DRM 誤判。  
• 不必重灌 OS 或還原映像，10 分鐘內即可恢復所有播放功能。  

**Cases 1**:  
背景：作者因測試伺服器 CPU，將 Q9300 暫裝至桌機。  
採取措施：依 KB891664 流程重置 DRM Store。  
成效：  
- MCE、WMP、MPC 皆恢復正常播放；錯誤畫面完全消失。  
- 轉檔時間由 30 min → 18 min，約縮短 40%；同時錄影＋轉檔時平均 CPU 使用率降低 35%。  
- 連續兩週穩定運作未再出現相同錯誤。