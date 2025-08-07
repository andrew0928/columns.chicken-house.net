# 微服務架構 #1, WHY Microservices?

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼近年來微服務 (Microservices) 搭配 Container 技術會迅速普及？
微服務能把過大的應用切割成多個獨立服務，Container 則把最小佈署單位從「Server → VM」再縮小到「Container」，大幅降低佈署門檻與成本；兩者相輔相成，使得開發、佈署、DevOps 流程都更敏捷，因而快速成為顯學。

## Q: 微服務架構與單體式 (Monolithic) 架構在「應用程式組成方式」上的核心差異是什麼？
單體式架構在開發階段就把所有元件以相同語言／平台編譯成一個大型 Process；微服務則將應用切成多個獨立 Service，透過 API／Protocol 在執行階段（Runtime）串接，可使用不同語言或平台，各服務最終以多個獨立 Process 運行。

## Q: 從開發團隊的角度，兩種架構在「程式碼重用 (reuse)」上的差異為何？
1. 單體式應用多半靠 Source Code 或 Binary Library 形式重用，重用層級發生在 Compile/Develop Time。  
2. 微服務則將重用層級提升到 Runtime，以獨立 Service 供其他服務或應用透過 API 存取，個別服務內部再決定要用 Source Code 或 Binary Library。

## Q: 從維運 (Operating) 團隊的角度，微服務帶來哪些優勢？
維運可：
• 針對單一服務做監控、升級、備援與重啟，故障影響範圍小。  
• 依各服務負載作精細化 Scale-out，資源使用更有效率。  
• 進行分區維修或功能關閉，把使用者影響降到最低。

## Q: 微服務導入後，佈署流程為何反而需要 Container 協助？
微服務把原本「Web + DB」的簡單佈署拆成多項服務，環境變複雜；Container 能封裝服務執行所需的依賴與設定，讓佈署、升級、回滾流程標準化並自動化，剛好補足微服務在佈署層面的複雜度。

## Q: 若想深入了解本文作者在研討會中的實作與投影片，可從哪裡取得資源？
作者提供的資源如下：  
1. 投影片 Slides: http://www.slideshare.net/chickenwu/community-open-camp  
2. Session 影片 (Channel 9): https://channel9.msdn.com/Events/Community-Open-Camp/Community-Open-Camp-2016/ComOpenCamp018  
3. Demo 原始碼與腳本: https://github.com/andrew0928/CommunityOpenCampDemo