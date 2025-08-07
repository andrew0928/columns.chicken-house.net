# [RUN! PC] 2008 十一月號

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 在介紹完基本的多執行緒程式設計後，作者接下來打算談些什麼主題？
作者打算開始介紹「應用層級的多執行緒設計模式」，說明如何透過不同的設計方式來真正發揮多核心硬體的效益。

## Q: 為什麼 .NET Framework 4.0 / Visual Studio 2010 的 Roadmap 會把重點放在平行處理？
因為硬體端（例如 Intel 即將推出的四核心 + HT CPU，Windows 會視為 8 個處理器）已經準備就緒，軟體若能支援平行處理就能充分利用多核心資源。

## Q: 「生產線模式」簡化後對應到哪一種常見的多執行緒模式？
它可以視為「Producer–Consumer（生產者–消費者）模式」的延伸與實作。

## Q: 若要更深入地應用「生產線模式」，作者建議可採用哪一種架構？
作者提到可以進一步採用「Stream Pipeline」的方式來串接處理流程，提升整體效能與可讀性。

## Q: 本文的範例程式以何種形式提供，讀者可以在哪裡下載？
範例程式是以 Console Application 形式發佈，讀者可至 `/admin/Pages/wp-content/be-files/RUNPC-2008-11.zip` 下載。