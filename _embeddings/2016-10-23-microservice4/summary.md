# API & SDK Design #2, 設計專屬的 SDK

## 摘要提示
- API 與 SDK 定義: API 是溝通介面，SDK 是協助開發者使用 API 的工具與函式庫
- 硬體介面類比: 以插座、USB 說明「介面」的重要性與契約精神
- 雲端情境差異: 在雲端時代 API 多為 HTTP/REST，SDK 目的是簡化呼叫流程
- 範例程式架構: 以 Demo.ApiWeb、Demo.Client.ConsoleApp、Demo.SDK 說明三層關係
- SDK 重構重點: 封裝 HttpClient、資料序列化、分頁處理，讓主程式專注業務邏輯
- 版本衝突風險: API 更新→SDK 更新→APP 更新三階段須妥善管理
- 契約專案: 以 Demo.Contracts 將資料與介面定義集中，確保前後端一致
- SDK 契約: 介面化 ISDKClient + Factory Pattern，穩定 APP 與 SDK 相依
- 相容性策略: 依需求分為 DLL 熱換、重新編譯、不相容大改版三種層級
- 架構師觀點: 先手動「土炮」理解設計，再評估 Swagger、ODATA、JWT 等框架

## 全文重點
本文是在「API & SDK Design」系列的第二篇，作者首先澄清許多開發者容易混淆的 API 與 SDK 差異。API（Application Programming Interface）只是“介面”本身，像 USB、插座一樣屬於約定文檔；SDK（Software Development Kit）則是讓他人更容易調用 API 的程式包，通常包含函式庫、範例、工具。

在雲端時代，HTTP/REST API 無須安裝本機套件即可呼叫，但撰寫 HttpClient 仍需不少樣板程式碼，因此作者以 C# 範例展示如何把呼叫邏輯封裝成 SDK。最初的 console app 寫了 150 行程式處理連線、分頁、JSON 反序列化等細節；重構後新增 Demo.SDK 專案，只要一行 `Demo.SDK.Client client = ...` 即可取得資料，使業務碼（篩選、顯示）更清晰。

接著作者討論版本維護問題：API 與 SERVER 由原廠即時更新，SDK 發行後仍需應用程式自行升級；若 API 結構改動（如欄位 SerialNo→BirdNo）而 APP 未同步更新，就會出現錯誤或空資料。為降低風險，作者引入「契約」(contracts) 的概念，將資料物件與介面定義獨立成 Demo.Contracts 專案，由編譯器確保前後端一致；並為 SDK 再定義 `ISDKClient` 介面，以 Factory Pattern 隔離 APP 和 SDK 版本差異。

相容性管理分為三層：單純換 DLL、不需改碼；更新後須重新編譯；大版本破壞性變動需調整程式。透過 contracts、介面化與嚴謹版本控管，可以在 CI/CD 流程中自動檢測錯誤，降低線上事故。作者最後提醒，文中故意不倚賴 Swagger、ODATA 等現成框架，是讓讀者深刻理解設計原理，再視實務選擇合適工具。

## 段落重點
### 什麼是 "API"?
將焦點放在 Interface，API 像 USB、插座等硬體介面，是供應方與使用方的溝通約定。只有清楚規範，服務端 (SERVER) 才能正確提供功能，客戶端 (APP) 才能正確取用。

### 什麼是 "SDK"?
SDK 著重在 Kit，目的是「讓開發者更容易使用 API」。在傳統本機開發時 SDK 常包含 redistributable、範例、工具；雲端時代則多為 Library + 文件，例如 Azure、Flickr 均提供多語言 SDK 以簡化 HTTP 呼叫、快取與效能最佳化。

### YOUR FIRST SDK!
以 Demo 專案說明：原始 console app 需手動設定 HttpClient、處理分頁、JSON 解析，程式冗長。重構後抽出 Demo.SDK，封裝上述細節，主程式僅管業務邏輯。SDK 內提供 `GetBirdInfos`、`GetBirdInfo` 方法，並透過 `yield` 實作分頁，達到程式碼重用。

### SDK / API 的更新及維護問題?
呈現 APP、SDK、API、SERVER 四者時序差異：API/Server 可立即更新，SDK 需發佈後由 APP 取用；若 APP 落後新版，可能呼叫失敗。案例示範欄位更名導致查詢失效，強調需預先設計版本相容策略。

### API: APP 與 Service 之間簽訂的合同
引入 Demo.Contracts 專案，將 `BirdInfo` 等資料與 service interface 抽出，統一 namespace 後所有專案共用。透過編譯器檢查確保「合約」一致，一旦 contract 改動即代表 API 版號升級，須經嚴格控管。

### SDK client interface: APP 與 SDK 之間簽訂的合同
再為 SDK 增加 `ISDKClient` 介面，並以 Factory Pattern 產生實例。APP 只依賴 contract，不再直接 new 具體類別。如此 APP 更新 SDK DLL 即可，若介面未變可免重編；若介面變動則編譯階段即抓到不相容。

### 結論
透過 contracts、介面化與清楚的版本策略，API 團隊可持續交付並降低上線風險。下一篇將討論 API 版本控制與向前相容的進階議題。作者並提醒新手工程師先動手實作「土炮」以理解設計原理，再考慮導入 Swagger、ODATA、JWT 等成熟框架，避免迷失於快速迭代的工具洪流。