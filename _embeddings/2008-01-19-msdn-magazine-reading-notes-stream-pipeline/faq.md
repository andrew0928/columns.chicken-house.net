# MSDN Magazine 閱讀心得: Stream Pipeline

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 什麼是本文介紹的 Stream Pipeline 作法？
Stream Pipeline 是一種將「串流」(Stream) 依工作階段切開，讓各個階段在不同執行緒 (threads) 上並行運作的技巧。以壓縮＋加密為例，第一個執行緒負責 Gzip 壓縮，第二個執行緒負責 Crypto 加密，形成「生產線」式的流程來同時利用多核心 CPU。

## Q: 為什麼把 GzipStream 和 CryptoStream 拆到兩個執行緒上可以提升效能？
壓縮與加密都屬於 CPU-bound 工作，若只用單一執行緒就只能吃到一顆核心的運算力。透過 Pipeline 方式，壓縮與加密可同時進行，各自佔用不同核心，使整體處理時間縮短；實測在文章範例中大約提升了 20% 的效能。

## Q: BlockingStream 在 Pipeline 中扮演什麼角色？
BlockingStream 是 Stephen Toub 為解決「生產者 / 消費者」協調問題而寫的橋接元件。它負責在前一階段 (生產者) 與下一階段 (消費者) 之間緩衝資料，必要時會阻塞 (block) 生產者或消費者，以避免資料過量或不足。

## Q: 與 TPL 或 ThreadPool 把大量工作分散處理相比，Stream Pipeline 有哪些優點？
1. 每個階段只做單一明確的工作，程式碼簡潔、切換成本低。  
2. 執行緒數量固定，避免 ThreadPool 動態建／殺執行緒造成的額外開銷。  
3. 適合必須保持「處理順序」的流程，不用額外費工在結果排序。

## Q: Pipeline 模式存在哪些缺點與限制？
1. 整體速度受最慢階段限制，效能未必能線性倍增。  
2. 可切割的階段數有限，無法像 ThreadPool 那樣隨人手數量無限擴充；四核心 CPU 仍可能只能用到兩核心。  
3. 啟動與結束時只有首尾階段在工作，Pipeline 切得越細，這段「暖機 / 收尾」成本越高。

## Q: 什麼情況下應該考慮使用 Pipeline 而非傳統的 ThreadPool 人海戰術？
當工作本身必須依固定順序進行，或分割成多個「先後相依」的處理階段時 (如壓縮後才能加密、折信後才能貼郵票)，就適合用 Pipeline；若工作彼此獨立、可任意排序，則用 ThreadPool 分散處理較單純高效。