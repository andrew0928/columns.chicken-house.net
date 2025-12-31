---
layout: synthesis
title: "不只是 TDD #1, 單元測試, 寫出高品質 code 的基本功夫"
synthesis_type: faq
source_post: /2017/01/30/leetcode1-tdd/
redirect_from:
  - /2017/01/30/leetcode1-tdd/faq/
postid: 2017-01-30-leetcode1-tdd
---

# 不只是 TDD #1, 單元測試, 寫出高品質 code 的基本功夫

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是寫出高品質 code 的「基本功」？
- A簡: 資料結構與演算法、單元測試與TDD、穩健流程與工具運用，兼顧可讀性、正確性與效能。
- A詳: 基本功包含三支柱：一是資料結構與演算法，決定正確性與時間複雜度；二是單元測試與TDD，透過先寫測試、後實作來降低缺陷與回歸風險；三是開發流程與工具（如Visual Studio、CI/CD）讓開發-測試-提交摩擦更小、迭代更快。透過像LeetCode的題庫和隱藏測試案例，你能聚焦於問題本質，鍛鍊以測試驅動的思維與效能敏感度，逐步養成可讀、可測、可維護且跑得快的程式風格。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, B-Q1, B-Q4

A-Q2: 什麼是 Online Judge（OJ）服務？
- A簡: 以題庫與自動測試驗證程式正確性與效能的線上評測平台。
- A詳: OJ提供演算法、資料庫、腳本等題庫，並附已知正確答案的測試案例。使用者上傳程式後，平台會自動編譯、以多組測試資料執行、比對結果，最後回報正確性、CPU時間與相對排名。由於測試資料部分隱藏，唯有滿足完整規格的通用解法才能通過，避免刷測或硬編對答案。這與TDD「先測後碼」的精神一致，是練習基礎功與測試思維的理想場域。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q10, B-Q2

A-Q3: LeetCode 是什麼？為何適合練功？
- A簡: LeetCode是面向軟體工程師的OJ平台，題庫與測試完善，聚焦演算法與資料結構。
- A詳: LeetCode收錄大量面試常見與經典題，語言支援廣、社群討論活躍。它的環境把框架與周邊雜訊去除，讓你專注在演算法、資料結構與時間/空間複雜度。提交後會給出正確性與效能排名，促使你在通過之後再優化。配合本機單元測試（例如Visual Studio + MSTest），可快速建立「先測後碼、持續重構」的良好迭代節奏。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q10, B-Q4

A-Q4: 什麼是 TDD（測試驅動開發）？
- A簡: 先寫失敗測試，再寫最小可行程式使其通過，最後重構的循環。
- A詳: TDD遵循紅-綠-重構（Red-Green-Refactor）循環：先據需求撰寫失敗的單元測試（紅），再寫最少程式讓測試通過（綠），最後在測試保護下重構改善設計與效能。TDD的價值是用測試定義需求，可量化的完成標準、快速回饋與防回歸，促使設計可測、介面清晰，並鼓勵小步快跑、循序優化的開發方式。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q5, A-Q6, B-Q1

A-Q5: 什麼是單元測試（Unit Test）？
- A簡: 對最小可測單元（函式/類別）行為進行自動化驗證的測試。
- A詳: 單元測試透過程式碼（如MSTest、NUnit、xUnit）自動化驗證單一單元的輸入輸出是否符合規格；具快速、可重複、可定位的特性。它是TDD的實施工具，也是持續整合中「回歸防護網」的核心。良好的單元測試應獨立、可重現，清楚驗證業務規格與邊界條件，並以最少外部依賴確保穩定。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, B-Q5, C-Q5

A-Q6: TDD 與單元測試有何差異與關係？
- A簡: 單元測試是技術手段；TDD是以測試驅動設計與開發的流程方法。
- A詳: 單元測試指自動化驗證程式行為的測試案例本身；TDD則是「測試先行」的開發方法論，規定先寫會失敗的測試，再寫實作與重構。你可有單元測試而非TDD（開發後補測試），也可用單元測試實施TDD（先測再碼）。TDD強化需求澄清、設計可測性與小步迭代，單元測試則提供具體落地工具。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q4, A-Q5, B-Q1

A-Q7: 為何導入 Microservices 前要先建立測試能力？
- A簡: 微服務拆分提高複雜度；若無完善測試，除錯與維運成本會暴增。
- A詳: 微服務把單體拆為多個獨立服務，帶來版本控制、API相容性、部署與監控等工程管理挑戰。一旦品質與流程不到位，問題跨服務擴散、難以定位，排障代價高。先建立單元/整合/契約測試與CI/CD，才能在服務化後維持變更的安全與速度。正如文中所述「要上雲端/導入微服務，要先測試」。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q14, D-Q5

A-Q8: 什麼是 Microservices（微服務）？
- A簡: 以小而自治的服務組成系統，各自獨立部署、擴展與演進。
- A詳: 微服務架構將系統依界限脈絡切成多個小服務，每個服務聚焦單一職責，擁有獨立資料與部署管線，透過API協作。優點是彈性、擴展性與團隊自治，但成本是分散式系統的複雜度上升，需強化自動化測試、監測、版本/相容性管理與DevOps流程，以確保變更速度與系統穩定。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, A-Q15, B-Q14

A-Q9: 為何演算法與資料結構比學框架更關鍵？
- A簡: 框架易迭代淘汰；基礎能力通用長久，決定效率與可擴展性。
- A詳: 市面框架更替快，熟悉用法短期奏效，卻難以跨技術棧遷移；而演算法與資料結構是語言與框架無關的核心，決定正確性、時間/空間複雜度與可擴展性。LeetCode等平台刻意剝離框架，讓你專注於問題本質，長期最能提高工程師的「可遷移競爭力」與系統設計能力。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q11, B-Q25(=B-Q3)

A-Q10: LeetCode 對解答的評估包含哪些面向？
- A簡: 正確性（通過測試）、效能（CPU時間）、相對排名（百分比）。
- A詳: 提交後，平台會以多組（含隱藏）測試案例驗證結果是否一致（正確性），並量測執行的CPU時間；相對於同題其他通過者計算百分位排名。由於重點是演算法，運行時間主要反映時間複雜度與資料結構選擇的優劣。這激勵「先正確、再優化」的開發節奏。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, B-Q2, D-Q6

A-Q11: 什麼是時間複雜度？為何影響OJ結果？
- A簡: 演算法隨輸入規模的時間成長率；決定是否超時及效能排名。
- A詳: 時間複雜度以Big-O表示，如O(n)、O(n log n)、O(n^2)。輸入規模大時，高次複雜度將急遽放大運行時間，導致超時（TLE）或排名偏低。OJ以相同硬體環境跑多組測試，效能差異主要由複雜度與實作細節（如記憶體存取、容器選擇）決定，因此需優先改善演算法級別。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, B-Q3, D-Q5

A-Q12: 為何把開發環境搬到 Visual Studio？
- A簡: 提升生產力：更好的編輯、偵錯、單元測試與本地效能回饋。
- A詳: 相較線上編輯器，Visual Studio提供強大的IDE能力：重構、偵錯器、測試總管、資料驅動測試、測試輸出與時間量測。以MSTest模擬OJ的多測試資料驅動，可快速在本地重現與定位問題，並將「貼到LeetCode」的摩擦降到最低。這符合CI/CD「降低手動步驟」的理念，提高迭代速度與品質。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q5, C-Q1

A-Q13: 什麼是資料驅動測試（Data-Driven Test）？
- A簡: 以外部資料表（XML/CSV等）批次餵入測試，重複執行同一測試邏輯。
- A詳: 資料驅動測試把測試邏輯與測試資料分離，透過資料來源（如MSTest的DataSource）逐列讀入欄位，驅動相同的Assert邏輯。優點是易擴充測資、覆蓋邊界情境、測試輸出更聚焦。對OJ題型尤為合適，能快速加入反例並回歸驗證，形成穩固的測試保護網。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q6, D-Q1

A-Q14: 為何OJ不公開全部測試案例？
- A簡: 防止針對測資硬編，迫使依規格寫出通用且健壯的解法。
- A詳: 若完整測資公開，容易誘發「對答案」或特殊分支硬處理，失去演算法訓練價值。隱藏測資能驗證你是否真正理解題意、處理邊界與例外，並鼓勵以一般化方法求解。這與TDD精神一致：用測試定義正確性標準，讓設計與實作在「無法作弊」的情境下自然提升品質。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, B-Q2, D-Q4

A-Q15: 雲端 PaaS/SaaS 與微服務的關係是什麼？
- A簡: 雲端服務普遍採微服務式拆分；容器技術普及後，微服務更易落地。
- A詳: 多數雲端PaaS/SaaS內部早以微服務思維設計，服務自治、可獨立部署與水平擴展。近年容器與自動化部署技術成熟，使企業/團隊也能以相似模式構建內部系統。這也帶來更高的工程要求：測試先行、版本/相容性治理、監控與DevOps，否則複雜度只會堆疊出技術債。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q7, A-Q8, B-Q14


### Q&A 類別 B: 技術原理類

B-Q1: TDD 的紅—綠—重構循環如何運作？
- A簡: 先寫會失敗的測試，再讓它通過，最後在測試保護下重構。
- A詳: 流程包含三步：Red寫出依規格設計的失敗測試（定義完成條件）；Green撰寫最小實作讓測試通過（避免過度設計）；Refactor在測試保護下調整設計、命名與結構、優化效能。每輪小步迭代都可驗證行為未退化，累積出穩定且可演進的程式碼基底。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q4, A-Q6, C-Q5

B-Q2: LeetCode 的評測流程如何運作？
- A簡: 編譯程式、以多組測資執行、比對答案、量測CPU時間、回報排名。
- A詳: 你提交後平台會在統一環境編譯程式，依序以題庫與隱藏案例呼叫指定API（如Solution.Method），比對輸出與期望答案以判定正確性；同時計算運行CPU時間並與全部通過者比較，產生百分位排名。Run Code僅以樣例測資快速驗證，Submit才跑完整測資集。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q10, A-Q14, B-Q15

B-Q3: 為何時間複雜度會直接影響CPU時間與排名？
- A簡: 高次複雜度在大輸入上爆炸，導致超時或排名落後。
- A詳: OJ的測資常涵蓋大規模數據，O(n^2)與O(n log n)在n很大時差距巨大。相同語言/環境下，CPU時間主要由演算法級別決定；常數級微調（如少量函式呼叫差異）影響有限。先以正確的演算法級別求解，再以資料結構與實作細節進一步優化。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q11, D-Q5, D-Q6

B-Q4: 如何在 Visual Studio 模擬OJ解題流程？
- A簡: 建Class Library放Solution類，建MSTest專案撰寫測試驅動多組資料。
- A詳: 建立題目對應的Class Library，實作OJ要求的Solution類與方法簽名；另建Unit Test專案參考該Library，用[TestClass]/[TestMethod]搭配Assert驗證樣例與自建測資。可用Data-Driven Test讀取XML/CSV，批次餵入多筆資料，觀察通過與運行時間，再貼回OJ提交。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q5, C-Q1

B-Q5: MSTest 的核心組件有哪些？
- A簡: TestClass、TestMethod、TestInitialize、Assert、TestContext、DataSource等。
- A詳: [TestClass]標註測試類，[TestMethod]標註測試方法；[TestInitialize]在每個測試前執行初始化；Assert提供各種斷言（如AreEqual）；TestContext可存取測試環境與輸出；DataSource則讓測試連接外部資料來源（XML/CSV/DB）以資料驅動方式重複執行同一測試邏輯。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q5, C-Q6, D-Q2

B-Q6: 資料驅動測試的機制與流程是什麼？
- A簡: 以DataSource綁定外部資料表，逐列讀入欄位，重複執行測試。
- A詳: 以MSTest為例，在[TestMethod]上加上[DataSource(provider, connection, table, accessMethod)]，測試會為資料表的每列執行一次。以XML為例，透過TestContext.DataRow["欄位"]取得值，傳入被測方法，再Assert比對。此方式把測試資料擴充與維護交給外部檔案，隔離邏輯與數據。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, C-Q6, D-Q1

B-Q7: TestInitialize 在測試生命週期中扮演什麼角色？
- A簡: 每個測試前執行初始化，建立一致、隔離的測試前置狀態。
- A詳: [TestInitialize]標註的方法會在每次[TestMethod]執行前呼叫，常用來產生新Solution實例、重設共享狀態或準備測資。其作用是確保測試之間互不汙染，提升可重現性與穩定度，避免測試順序或共享變數造成的偶發失敗。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q4, D-Q2

B-Q8: TestContext.WriteLine 的原理與用途？
- A簡: 在測試輸出管道紀錄訊息，用於診斷失敗個案與重現步驟。
- A詳: TestContext提供每次測試的上下文，WriteLine寫入的內容會顯示在測試結果中。配合資料驅動測試，能在失敗時輸出given/expected/actual等關鍵資訊，快速定位哪一筆資料導致錯誤，並把該反例加入測試資料檔中，形成回歸防護。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q7, D-Q10, D-Q4

B-Q9: 為何用Unit Test專案優於Console App驗證解答？
- A簡: 測試框架提供發現、並行、資料驅動、報表與整合CI的能力。
- A詳: Console App需手寫輸入/輸出與比對邏輯，不易批次、缺少報表與整合；Unit Test專案可自動發現測試、以資料驅動多筆執行、集中顯示結果與時間，便於CI自動化。也能精細控制前置/釋放，與測試輸出整合，降低人為錯誤與操作成本。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q1, C-Q5

B-Q10: 如何設計可直接貼到 LeetCode 的程式碼？
- A簡: 僅保留Solution類與指定方法，避免外部依賴與多餘程式碼。
- A詳: 依題目提供的class與方法簽名實作，避免使用專案特定依賴（檔案I/O、日誌、外部套件）。封裝在單一類別/檔案內，命名與存取修飾符匹配OJ要求。確保編譯期錯誤（如NotImplementedException拼寫）已排除，貼到OJ即可編譯與執行。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q8, D-Q3, B-Q2

B-Q11: 如何以測試驅動覆蓋邊界情境？
- A簡: 將樣例與反例加入資料檔，設計空值、極端長度與特殊模式。
- A詳: 先以題目樣例建立最小測試，再針對規格列出邊界：空字串、單字元、重複元素、最大輸入、異常模式等。每發現反例即加入測試資料檔，確保回歸。TDD促使你從測試出發定義規格，以案例細化需求，迭代中不斷擴充覆蓋。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, C-Q6, D-Q4

B-Q12: VS Test Runner 如何顯示測試時間？有何意義？
- A簡: 測試結果含每筆執行時間，利於本地粗估效能與追蹤回歸。
- A詳: Test Runner會記錄每個[TestMethod]執行時長，資料驅動時亦可觀察整體與單筆趨勢。雖與OJ硬體不同、不可直接對比排名，但可用於比較不同演算法/實作相對表現，監控重構後是否變慢，輔助迭代優化。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: D-Q6, C-Q9, B-Q3

B-Q13: 如何在測試保護下重構以提升效能？
- A簡: 先維持行為等價，再替換更優演算法/資料結構，持續跑回歸。
- A詳: 從綠燈出發，調整內部結構、命名，或改用更低複雜度的方式（如雙迴圈→雜湊、字串拼接→StringBuilder）。每步小改後立刻跑全部測試，確保行為不變。若要大改，先以測試鎖定外部行為，拆小步進行，避免一次性風險。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q11, D-Q6, C-Q9

B-Q14: 微服務中的測試與版本/相容性的關聯是什麼？
- A簡: 契約測試與CI把關API相容性，避免服務間變更破壞。
- A詳: 微服務間以API協作，需確保介面與語義的相容性。透過契約測試驗證請求/回應模式與邊界，配合CI在合併前自動跑單元/整合/契約測試，防止破壞性變更進入主幹。版本策略（如語意化版本）與回滾機制也需配套，以維持整體穩定。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q7, A-Q8, C-Q10

B-Q15: OJ 的 Run Code 與 Submit 有何技術差異？
- A簡: Run僅跑樣例快速檢查；Submit跑完整（含隱藏）測資並評分。
- A詳: Run Code把頁面上的範例資料餵入你的程式，適合快速檢視基本正確；Submit會以更大量、覆蓋更廣的隱藏測資運行，回傳正確性、CPU時間與排名。兩者使用同一編譯/執行環境，差別在資料集規模與回饋內容。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, A-Q14, D-Q4


### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何在 Visual Studio 建立 LeetCode 題目的解題專案？
- A簡: 建Class Library放解答；建MSTest專案撰寫測試並參考該Library。
- A詳: 步驟：1) 新增Class Library（.NET）專案，命名對應題號/名稱；2) 建立Solution類與題目方法簽名；3) 新增MSTest測試專案，加入對解題專案的參考；4) 在[TestClass]中撰寫測試方法，用Assert驗證樣例。注意事項：統一命名、避免外部依賴、Release組態下執行測試。最佳實踐：專案一題一夾，保持簡潔。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, C-Q5, C-Q8

C-Q2: 如何建立 Solution 類與方法骨架？
- A簡: 依OJ要求建立public class Solution與指定方法簽名。
- A詳: 例如C#：建立public class Solution，內含public返回型別與參數簽名的方法（如public string ShortestPalindrome(string s)）。先以throw new NotImplementedException()標示未實作，確保編譯通過。提交前移除例外並填入實作，保持與OJ完全一致的簽名與可見性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q10, D-Q3, C-Q5

C-Q3: 如何建立 MSTest 專案並參考解題專案？
- A簡: 新增MSTest（Test Project），以專案參考連結解題Library。
- A詳: 步驟：1) 新增MSTest Test Project；2) 右鍵References→Add Reference→選擇解題專案；3) 加入using命名空間；4) 撰寫[TestClass]/[TestMethod]。注意：測試方法需public與無回傳；確保TargetFramework相容。最佳實踐：每題建立對應[TestClass]。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, C-Q5, D-Q8

C-Q4: 如何用 TestInitialize 建立每次測試的新 Solution 實例？
- A簡: 以[TestInitialize]方法new Solution，存放至欄位供測試使用。
- A詳: 程式碼：
  ```
  private Solution _sut;
  [TestInitialize]
  public void Init() { _sut = new Solution(); }
  ```
  之後在[TestMethod]中使用_sut呼叫方法。注意：避免跨測試共用狀態；若需要昂貴初始化，才考慮[TestInitialize]與快取策略。最佳實踐：命名_sut（System Under Test）。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q7, C-Q5, D-Q2

C-Q5: 如何撰寫基本測試方法與斷言？
- A簡: 使用[TestMethod]與Assert.AreEqual比對expected與actual。
- A詳: 範例：
  ```
  [TestMethod]
  public void SampleCases() {
    var actual = _sut.ShortestPalindrome("aacecaaa");
    Assert.AreEqual("aaacecaaa", actual);
  }
  ```
  注意：1測試1主旨；名稱描述行為；避免複雜邏輯。最佳實踐：Given/When/Then結構、Arrange-Act-Assert清晰分段。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, C-Q4, A-Q5

C-Q6: 如何改造成資料驅動測試批次驗證多筆資料？
- A簡: 在[TestMethod]加DataSource屬性，從XML讀取given/expected欄位。
- A詳: 1) 建parameters.xml：
  ```
  <tests>
    <add><given>aacecaaa</given><expected>aaacecaaa</expected></add>
    <add><given>abcd</given><expected>dcbabcd</expected></add>
  </tests>
  ```
  2) 設檔案屬性：Build Action=Content, Copy to Output=Copy always；3) 測試：
  ```
  [DataSource("Microsoft.VisualStudio.TestTools.DataSource.XML","parameters.xml","add",DataAccessMethod.Sequential)]
  public void Cases(){
    var g = (string)TestContext.DataRow["given"];
    var e = (string)TestContext.DataRow["expected"];
    Assert.AreEqual(e, _sut.ShortestPalindrome(g));
  }
  ```
  注意路徑與欄位名對應。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, D-Q1, C-Q7

C-Q7: 如何在測試中輸出given/expected/actual便於診斷？
- A簡: 透過TestContext.WriteLine輸出關鍵值，失敗時可快速比對。
- A詳: 程式碼：
  ```
  public TestContext TestContext { get; set; }
  ...
  TestContext.WriteLine($"given: {g}");
  TestContext.WriteLine($"expected: {e}");
  TestContext.WriteLine($"actual: {_sut.ShortestPalindrome(g)}");
  ```
  注意：宣告public TestContext屬性以便框架注入；避免大量噪音輸出。最佳實踐：只輸出定位所需關鍵字段。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q8, D-Q10, D-Q2

C-Q8: 如何讓程式碼「一字不漏」貼到OJ即可執行？
- A簡: 保持單檔單類（Solution），精準簽名，避免任何專案相依。
- A詳: 準則：1) 僅使用標準庫；2) 方法名稱與參數型別與OJ一致；3) 避免日誌/檔案I/O；4) 移除測試專用程式碼；5) 以Release產出驗證；6) 內部輔助方法設為private。提交前在本地用相同輸入跑一次確認。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q10, D-Q3, B-Q2

C-Q9: 如何在本機評估效能並指引優化方向？
- A簡: 觀察測試執行時間；在Release/不附加偵錯下比較不同實作。
- A詳: 建議：1) 切到Release；2) 關閉偵錯器（Ctrl+F5或命令列執行dotnet test）；3) 以相同測資比較不同實作的相對時間；4) 優先調整演算法級別，再改善資料結構與配置。注意：本機時間與OJ排名不可直接對比，只用於相對趨勢判讀。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q12, B-Q13, D-Q6

C-Q10: 如何把此流程接入CI/CD（如GitHub Actions/Azure DevOps）？
- A簡: 在管線中執行dotnet test，作為合併前必經檢查與報表來源。
- A詳: 步驟：1) 專案根新增CI設定（如GitHub Actions的yml）；2) 邏輯：還原→建置→dotnet test（含資料驅動測試）；3) 啟用測試失敗阻擋合併；4) 產出測試報表供檢視。最佳實踐：分支策略+PR檢查，維持主幹穩定。注意：避免上傳OJ完整答案到公開庫以維持公正性。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q9, B-Q14, A-Q7


### Q&A 類別 D: 問題解決類（10題）

D-Q1: DataSource 讀不到parameters.xml怎麼辦？
- A簡: 檢查檔案屬性、相對路徑、資料表節點名與DataSource設定一致。
- A詳: 症狀：測試找不到資料或拋例外。原因：1) 檔案未複製到輸出（Build Action非Content、Copy to Output未設定）；2) 相對路徑錯誤（測試執行目錄與專案目錄不同）；3) XML節點/table名不符；4) 欄位名拼錯。解法：設Build Action=Content、Copy=Copy always；用相對路徑；校對DataSource第三參數(table)與XML節點。預防：以測試輸出列印ApplicationBase確認路徑。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q6, B-Q6, B-Q8

D-Q2: TestContext為null或WriteLine失敗怎麼辦？
- A簡: 宣告public TestContext屬性，確保使用MSTest對應版本與命名。
- A詳: 症狀：NullReference或輸出未出現。原因：1) 未宣告public TestContext {get; set;}；2) 測試框架版本不符（MSTest V2命名空間不同）；3) 在靜態方法中使用。解法：加入public屬性、確認引用Microsoft.VisualStudio.TestTools.UnitTesting；避免static測試方法。預防：範本化測試類，持續驗證輸出面板。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, C-Q7, B-Q8

D-Q3: 出現NotImplementException編譯錯誤怎麼辦？
- A簡: 更正為標準的NotImplementedException或移除暫時例外。
- A詳: 症狀：編譯失敗；原因：拼寫錯誤（NotImplementException不存在）。解法：使用throw new NotImplementedException(); 或在開始實作後移除；OJ提交前確認程式可編譯。預防：用IDE自動完成，避免手打拼寫錯誤；以最小可編譯骨架開始。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, B-Q10

D-Q4: 本機通過，OJ提交Wrong Answer怎麼診斷？
- A簡: 尋找反例、加入資料檔、重現與修正；覆蓋邊界與規格缺口。
- A詳: 症狀：Run Code通過、Submit失敗。原因：隱藏測資觸發邊界情況未處理。解法：1) 重新審題；2) 以可能的邊界（空/極端長度/特殊字元）構造反例；3) 加入parameters.xml重現；4) 修正演算法；5) 回歸全部測試。預防：先覆蓋常見邊界，再提交。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q11, C-Q6

D-Q5: 出現Time Limit Exceeded（TLE）怎麼辦？
- A簡: 降低時間複雜度與常數因子，改用更合適資料結構/演算法。
- A詳: 症狀：提交超時。原因：演算法複雜度過高（如O(n^2)）、不必要的重複計算、昂貴操作（字串拼接）。解法：1) 分析複雜度；2) 以雜湊、雙指標、分治等降低級別；3) 減少配置與拷貝（用StringBuilder等）；4) 在本地比較前後時間。預防：提交前針對大輸入做壓力試驗。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q3, C-Q9

D-Q6: 測試通過但效能排名偏低如何優化？
- A簡: 分析瓶頸、優先調整演算法級別，再微調資料結構與實作細節。
- A詳: 症狀：正確性OK、排名落後。原因：複雜度或常數因子偏高。解法：1) 審視核心路徑與資料結構選擇（如用Dictionary替代線性搜尋）；2) 減少不必要分配與拷貝；3) 批量處理；4) Release與不附加偵錯測試比較。預防：先求正確，再設計可重構的清晰結構以便後續優化。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q12, B-Q13, C-Q9

D-Q7: 字串比較Assert失敗的常見原因與解法？
- A簡: 空白/換行/大小寫差異；OJ需精確比對，避免多餘格式處理。
- A詳: 症狀：預期與實際看似相同仍失敗。原因：隱藏空白/換行/Unicode差異；或以不當Trim/ToLower破壞規格。解法：輸出長度與字元碼位診斷；精確遵循題意，僅在規格允許時正規化。預防：測試覆蓋含空白、特殊字元案例。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q7, B-Q11, D-Q4

D-Q8: 測試找不到方法（Not discoverable）怎麼辦？
- A簡: 確認[TestClass]/[TestMethod]、public、無參數與框架版本正確。
- A詳: 症狀：測試總管未顯示測試。原因：缺少屬性標註、方法非public/有參數、回傳非void、使用錯誤命名空間。解法：加上正確標註與簽名；確認引用Microsoft.VisualStudio.TestTools.UnitTesting。預防：從範本建立，避免自定不支援的特性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, C-Q3

D-Q9: 本機與OJ環境差異導致錯誤如何避免？
- A簡: 避免區域性行為；使用標準庫、確保與OJ相容的語言特性。
- A詳: 症狀：本機通過、OJ異常。原因：依賴區域設定（大小寫/文化）、非標準API或版本差異。解法：使用與OJ相容的語言版本與標準庫；避免文化相依格式化；明確字串比較規則（Ordinal）。預防：保持解答純粹、無外部依賴與環境假設。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, C-Q8, D-Q4

D-Q10: 多筆測試失敗時難以定位，怎麼處理？
- A簡: 在資料驅動測試中輸出索引與關鍵欄位；採二分法縮小問題。
- A詳: 症狀：批量測試多筆失敗，難以追查。解法：1) 以TestContext輸出資料列索引、given/expected/actual；2) 將資料拆分、以二分法縮小集合定位特定失敗；3) 抽出最小可重現輸入加入專用測試。預防：保持測試資料可讀、分組與註解清晰。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q8, C-Q6, C-Q7


### 學習路徑索引

- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是寫出高品質 code 的「基本功」？
    - A-Q2: 什麼是 Online Judge（OJ）服務？
    - A-Q3: LeetCode 是什麼？為何適合練功？
    - A-Q4: 什麼是 TDD（測試驅動開發）？
    - A-Q5: 什麼是單元測試（Unit Test）？
    - A-Q6: TDD 與單元測試有何差異與關係？
    - A-Q10: LeetCode 對解答的評估包含哪些面向？
    - A-Q11: 什麼是時間複雜度？為何影響OJ結果？
    - A-Q12: 為何把開發環境搬到 Visual Studio？
    - B-Q1: TDD 的紅—綠—重構循環如何運作？
    - B-Q2: LeetCode 的評測流程如何運作？
    - B-Q5: MSTest 的核心組件有哪些？
    - C-Q1: 如何在 Visual Studio 建立 LeetCode 題目的解題專案？
    - C-Q5: 如何撰寫基本測試方法與斷言？
    - C-Q6: 如何改造成資料驅動測試批次驗證多筆資料？

- 中級者：建議學習哪 20 題
    - A-Q7: 為何導入 Microservices 前要先建立測試能力？
    - A-Q8: 什麼是 Microservices（微服務）？
    - A-Q13: 什麼是資料驅動測試（Data-Driven Test）？
    - A-Q14: 為何OJ不公開全部測試案例？
    - B-Q3: 為何時間複雜度會直接影響CPU時間與排名？
    - B-Q4: 如何在 Visual Studio 模擬OJ解題流程？
    - B-Q6: 資料驅動測試的機制與流程是什麼？
    - B-Q7: TestInitialize 在測試生命週期中扮演什麼角色？
    - B-Q8: TestContext.WriteLine 的原理與用途？
    - B-Q9: 為何用Unit Test專案優於Console App驗證解答？
    - B-Q10: 如何設計可直接貼到 LeetCode 的程式碼？
    - B-Q11: 如何以測試驅動覆蓋邊界情境？
    - B-Q12: VS Test Runner 如何顯示測試時間？有何意義？
    - C-Q2: 如何建立 Solution 類與方法骨架？
    - C-Q3: 如何建立 MSTest 專案並參考解題專案？
    - C-Q4: 如何用 TestInitialize 建立每次測試的新 Solution 實例？
    - C-Q7: 如何在測試中輸出given/expected/actual便於診斷？
    - D-Q1: DataSource 讀不到parameters.xml怎麼辦？
    - D-Q2: TestContext為null或WriteLine失敗怎麼辦？
    - D-Q4: 本機通過，OJ提交Wrong Answer怎麼診斷？

- 高級者：建議關注哪 15 題
    - A-Q15: 雲端 PaaS/SaaS 與微服務的關係是什麼？
    - B-Q13: 如何在測試保護下重構以提升效能？
    - B-Q14: 微服務中的測試與版本/相容性的關聯是什麼？
    - B-Q15: OJ 的 Run Code 與 Submit 有何技術差異？
    - C-Q8: 如何讓程式碼「一字不漏」貼到OJ即可執行？
    - C-Q9: 如何在本機評估效能並指引優化方向？
    - C-Q10: 如何把此流程接入CI/CD（如GitHub Actions/Azure DevOps）？
    - D-Q5: 出現Time Limit Exceeded（TLE）怎麼辦？
    - D-Q6: 測試通過但效能排名偏低如何優化？
    - D-Q7: 字串比較Assert失敗的常見原因與解法？
    - D-Q8: 測試找不到方法（Not discoverable）怎麼辦？
    - D-Q9: 本機與OJ環境差異導致錯誤如何避免？
    - D-Q10: 多筆測試失敗時難以定位，怎麼處理？
    - A-Q9: 為何演算法與資料結構比學框架更關鍵？
    - A-Q7: 為何導入 Microservices 前要先建立測試能力？