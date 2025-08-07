# [RUN! PC] 2010 四月號 - 生產者 vs 消費者─執行緒的供需問題

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 這篇「生產者 vs 消費者」文章的主題是什麼？
文章聚焦在多執行緒中的「生產者 / 消費者」問題，說明如何協調兩個處理階段之間的進度，並示範以 BlockQueue 來簡化同步與資料交換的實作方式。

## Q: 它與先前「生產線模式 (Pipeline Pattern)」文章的關係是什麼？
「生產線模式」主要談如何用 Pipe 把工作拆成多個階段並行處理；而本篇則接續該概念，探討當兩個階段彼此供需不一致時，應如何透過生產者 / 消費者模型來協調與平衡。

## Q: 什麼是 BlockQueue？為何作者要實作它？
BlockQueue 是一種阻塞佇列 (blocking queue) 的實作，可在生產者與消費者之間自動處理同步與流量控制；當應用場景無法直接採用 Stream 模式時，透過包裝成 Queue 可更簡單地套用於各式工作流程。

## Q: 作者認為比 BlockQueue 更「漂亮」的做法是什麼？適用在什麼情境？
作者提到在 MSDN Magazine 看到的 BlockingStream 作法，將阻塞機制封裝成 System.IO.Stream 的衍生類別。凡是原本就採 Stream 介面的資料處理，如壓縮、加密或 Socket 通訊，都非常適合直接改用 BlockingStream。

## Q: 什麼時候會選擇 BlockQueue 而不是 BlockingStream？
當應用程式本身並非以 Stream 為核心，或無法輕易套用 Stream 架構時，以 Queue 形式封裝的 BlockQueue 會比 BlockingStream 更實際、容易整合。

## Q: 如何取得本文範例程式與延伸閱讀資料？
文章末尾提供多個連結，可下載範例程式並參考作者相關 Blog 文章，包括「MSDN Magazine: Stream Pipeline 閱讀心得」、「生產線模式的多執行緒應用」及「BlockQueue 實作」等。