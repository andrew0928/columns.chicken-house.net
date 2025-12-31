---
layout: synthesis
title: "[設計案例] 清除Cache物件 #1. 問題與作法"
synthesis_type: faq
source_post: /2009/12/19/design-case-study-cache-object-cleanup-1-problem-and-approach/
redirect_from:
  - /2009/12/19/design-case-study-cache-object-cleanup-1-problem-and-approach/faq/
postid: 2009-12-19-design-case-study-cache-object-cleanup-1-problem-and-approach
---

# [設計案例] 清除Cache物件：問題與作法 FAQ

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 ASP.NET 的 Cache 物件？
- A簡: ASP.NET 的記憶體快取容器，透過鍵值存取資料，支援到期與相依性，常用於提升重複讀取的效能。
- A詳: Cache 是 ASP.NET 提供的應用程式層級記憶體快取，常見以 HttpRuntime.Cache 存取。它以鍵值對儲存物件，支援絕對/滑動到期、相依性（檔案、其他鍵、資料庫），並可設定優先權與移除回呼。典型應用包含暫存外部資源（例如 HTTP 下載內容），避免重複 I/O 或昂貴運算。它近似 Dictionary，但具備自動淘汰與相依性等進階快取行為。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, B-Q1

A-Q2: HttpRuntime.Cache 有什麼用途與特性？
- A簡: 應用程式範圍的共享快取，跨請求存取，執行緒安全，提供自動淘汰與移除回呼等功能。
- A詳: HttpRuntime.Cache 是 ASP.NET 中可全域使用的 Cache 實體，具備跨請求存取特性，適合儲存重複讀取但可再生的資料。它提供執行緒安全的存取、項目到期（Absolute、Sliding）、依賴機制（CacheDependency）、優先權管理，以及項目移除時觸發的回呼。相較 Session/User cache，HttpRuntime.Cache 更適用於全站共享的資料項目與結果快取。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, B-Q12

A-Q3: Cache 與 Dictionary 有何差異？
- A簡: 都用鍵值存取，但 Cache 具到期、相依、淘汰與回呼；Dictionary 僅是靜態集合，不會自動移除。
- A詳: 表面上兩者都以鍵值對存取，但 Dictionary 僅提供集合操作，不具備到期機制、相依清除或記憶體壓力下淘汰。Cache 有自動回收策略、可設定到期與依賴、移除回呼，以及跨請求全域共享。而且 Cache 的列舉行為不保證一致性，項目可能在列舉期間被移除或加入，使用上需考量快取的不確定性與併發。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, A-Q7

A-Q4: 為什麼需要手動從 Cache 移除物件？
- A簡: 當資料過時、業務條件變更、需立即失效或群組清除時，必須手動移除指定或一群快取項目。
- A詳: 雖然 Cache 會依到期或記憶體壓力自動淘汰，但遇到資料更新（如後端內容修改）、合規需求（立即失效）、功能操作（使用者清空部分快取）或避免讀取舊資料等情境，需主動移除指定鍵或一群相關條目。特別是分群清除（如依網域、Content-Type、Protocol）時，更需設計可控的失效策略，避免全域掃描造成效能與一致性問題。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, C-Q3

A-Q5: 什麼是 Cache Key？為何重要？
- A簡: 快取項目的唯一識別字串，決定存取與清除策略；良好命名可支援分群與版本化。
- A詳: Key 是快取項目的主索引，常以字串代表唯一性，如以 URL 作為鍵儲存下載內容。鍵設計直接影響查找、清除與分群策略。良好實務包含加入命名空間/前綴（domain、type、protocol）、版本片段，以及避免碰撞的可預期格式。命名一致性讓後續群組清除（正則、前綴、版本化）與統計分析更容易且可靠。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q18, C-Q8

A-Q6: 為何直接列舉所有 Cache 鍵有風險？
- A簡: 列舉期間資料可能被移除或新增，導致不一致、例外與效能負擔，特別在大型快取下更明顯。
- A詳: Cache 的內容非靜態，列舉時其他執行緒可能同時插入或移除，造成鍵集不穩定。這會帶來資料競態、NullReference/InvalidOperation 例外，以及大型快取全掃描的效能成本。若以列舉配正則篩鍵清除，會在每次操作付出 O(N) 掃描代價，不利高流量環境。應透過分群設計、反向索引或依賴機制降低全掃描需求。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, D-Q3

A-Q7: 什麼是 Cache 的「不確定性」？
- A簡: 快取項目可隨時因到期、淘汰或外部清除消失，任何時點存取都需容忍不存在。
- A詳: 不確定性指快取並非可靠儲存，項目可能因到期策略、資源壓力回收、依賴失效或手動移除而在任意時刻消失。因此使用快取時，必須隨時檢查存在性，對 miss 具備補救流程（重建或回源），並避免依賴列舉結果的強一致操作。這也影響 API 設計，需以冪等與可重試為原則。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, D-Q2

A-Q8: 什麼是 CacheDependency？
- A簡: 一種相依性設定，當檔案或其他鍵變更時，關聯的快取項目會自動失效並被移除。
- A詳: CacheDependency 允許快取項目依賴外部資源或其他快取鍵，例如檔案、資料夾、其他 Cache 條目或資料庫。當相依目標發生變動（檔案更新、依賴鍵移除等），快取項目會被自動清除。這特別適合「分群清除」：把同群資料綁定到同一相依目標，透過觸發一次變動達到整群失效的效果。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, C-Q6

A-Q9: 檔案相依性如何用於分群清除？
- A簡: 為同群快取綁定同一個檔案相依，變更或 touch 該檔案，即可一次清除整群資料。
- A詳: 群組需求（如同網站網域、同 Content-Type）可透過指定一個群組代表檔案，所有該群的快取項目在插入時附上同一個 CacheDependency（指向該檔）。當需要清除此群時，更新該檔案（修改時間）即可讓相依的快取條目自動失效。此法設計簡單、清除一致，不用掃描快取；但引入檔案 I/O 延遲與部署環境權限需求。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q6, D-Q4

A-Q10: 用正則篩鍵與自建索引清除的差異？
- A簡: 正則掃描簡單但每次 O(N)；索引需維護成本，但清除快、可精準定位與避免全掃描。
- A詳: 正則篩鍵直接列舉快取鍵再比對，開發簡單但需遍歷所有鍵，對大型快取耗時且不穩定。自建索引（反向索引、群組表）在插入時就紀錄群組到鍵的映射，清除時透過索引快速取得受影響鍵，避免全域掃描；缺點是維護同步、處理鍵意外被淘汰與併發控制的複雜度較高。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, C-Q9

A-Q11: 刪除部分 Cache 的常見情境有哪些？
- A簡: 依網域、內容類型或通訊協定分群，針對指定群組手動清除，以控制快取一致性。
- A詳: 常見需求包括：刪除某網站來源的所有下載內容（按網域分群）、清除特定類型（如 image/jpeg）的資料、清除特定協定（如 https）下載的內容。這些用例反映業務上的一致性要求，期望一次性讓相同語義的資料失效，避免逐鍵移除。設計良好的鍵策略與依賴機制可優雅支持這些行為。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q3, C-Q4, C-Q5

A-Q12: 為何「檔案相依清除」既聰明又愚蠢？
- A簡: 聰明在於群組清除漂亮一致；愚蠢在於引入不必要的檔案 I/O 與環境相依。
- A詳: 其聰明之處是用單一變更事件（檔案時間戳）驅動整群快取失效，避免掃描、程式碼簡潔且高度一致。缺點是額外檔案 I/O 會拉高延遲，需處理檔案鎖與存取權限，亦增加部署複雜度。在 I/O 成本敏感或無檔案寫入權限的環境，應評估替代方案如鍵依賴或版本化命名空間。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q22, C-Q7, C-Q8

A-Q13: 什麼是「群組清除」（Group Invalidation）？
- A簡: 將多個相關快取項目歸為一組，透過單一事件或標記讓整組同時失效。
- A詳: 群組清除的核心是「一次動作，整組失效」。可藉由共享相依目標（檔案、鍵）、共享版本標記或借助反向索引，快速找出並清除群組內容。適用於語義一致性要求較高的場景，如來源站點、內容類型或權限變更。它提升維護性與一致性，並避免 O(N) 掃描開銷。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, C-Q6

A-Q14: Cache 的 GetEnumerator 是什麼？
- A簡: 供列舉快取內容的介面，通常回傳 IDictionaryEnumerator，用於巡覽鍵與值。
- A詳: Cache 實作了可列舉介面，可用 foreach 遍歷項目。實際上會取得 IDictionaryEnumerator，再從 DictionaryEntry 的 Key/Value 讀取。不過列舉不保證一致性，過程中項目可能變化，應在使用前檢查存在、處理例外，並避免在熱路徑中頻繁全域列舉，以免效能下降。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, C-Q2, D-Q1

A-Q15: 用 URL 當 Cache Key 有何利弊？
- A簡: 直觀唯一、易追蹤；但需處理大小寫、查詢字串、標準化與安全編碼問題。
- A詳: 以 URL 作鍵可直觀對應下載內容，天然唯一性高；但不同形式（大小寫、尾斜線、查詢參數順序）可能導致重複或碰撞。應統一標準化（LowerCase、規範化查詢序列）、必要時 Hash 或 URL 編碼，並在鍵前綴加入語義資訊（domain/type/protocol/版本）以利維運與清除。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q18, C-Q3

A-Q16: 為什麼不建議每次都掃描整個 Cache？
- A簡: O(N) 成本高、期間不一致風險大，易造成延遲尖峰與鎖競爭，影響整體效能。
- A詳: 全域掃描會線性耗時，隨快取成長延遲增加，並與併發請求競爭資源。列舉期間遇到項目變動也會產生額外重試或例外處理成本。更好的做法是透過分群（依賴或版本）、反向索引與精準鍵設計，讓清除與查找在次線性或近常數時間完成。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q16

A-Q17: 什麼是版本化命名空間清除？
- A簡: 以版本標記組成鍵，清除時只要遞增版本，舊鍵即時失效於讀取路徑。
- A詳: 在鍵中嵌入群組版本號（如 v:domain:x），讀取與寫入時都包含版本。當需清除群組，遞增版本鍵即可。舊資料仍在快取但不再被命中，隨時間自然淘汰。優點是零 I/O、常數時間清除；缺點是未即時釋放記憶體，且需務必統一透過封裝 API 存取，以免遺漏版本片段。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q15, C-Q8

A-Q18: Key 前綴與 CacheDependency 有何差異？
- A簡: 前綴便於命名與篩選；依賴可原子整組失效。前者輕量，後者一致性更高。
- A詳: 前綴法透過命名規約支持搜尋與人工辨識，搭配反向索引或正則可分群操作；但清除時仍可能需掃描。CacheDependency 透過事件驅動原子失效，確保整組一致清除，不需掃描；但引入依賴目標管理成本（檔案或鍵）。實務上常混合使用，以兼顧識別性與操作效率。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q6, C-Q9

A-Q19: ASP.NET Cache 與 MemoryCache 有何不同？
- A簡: 前者屬 System.Web、支援 CacheDependency；後者通用於非 Web，但相依機制不同。
- A詳: System.Web.Caching.Cache 是 ASP.NET 專用，支援 CacheDependency（檔案、鍵、SQL）等 Web 場景。System.Runtime.Caching.MemoryCache 可用於一般 .NET 應用，提供變更監視（ChangeMonitor）與類似到期模型，但 API 與相依性用法不同。在 .NET Core/ASP.NET Core 常使用 IMemoryCache 或 MemoryCache，需選擇等價機制替代。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q25, C-Q10

A-Q20: 快取設計的核心價值是什麼？
- A簡: 以最小代價換取高命中率與一致性，兼顧效能、可維護性與清除的可控性。
- A詳: 快取的目的在減少重複成本與延遲，同時確保資料語義的正確。良好設計包含：合理鍵策略、清除可預期（依賴/版本/索引）、避免全掃描、容忍不確定性、良好的併發控制與監控。清除策略是快取設計的靈魂，應優先考量如何「安全有效地失效一群資料」。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q16


### Q&A 類別 B: 技術原理類

B-Q1: Cache.Remove 如何運作？
- A簡: 依鍵移除單一項目，若存在則刪除並觸發移除回呼；不存在則安全返回 null。
- A詳: Remove(key) 會嘗試從快取刪除指定鍵的項目。若項目存在，先從內部索引移除，再執行已註冊的移除回呼（含原因如 Removed、Expired、DependencyChanged），最後釋放資源。不存在時返回 null，不拋例外。該操作執行緒安全，但不影響其他與其相依的項目，除非使用鍵依賴機制。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, B-Q13

B-Q2: GetEnumerator 的回傳與列舉流程是什麼？
- A簡: 回傳 IDictionaryEnumerator，逐一提供 DictionaryEntry，含 Key 與 Value。
- A詳: Cache 實作 IEnumerable，GetEnumerator() 回傳 IDictionaryEnumerator。foreach 時實際遍歷 DictionaryEntry，從中取得 Key、Value。由於 Cache 會變動，列舉非快照，期間項目可能被增加或移除。實務上常先複製鍵清單再操作，以降低競態與一致性風險，或限制在管理工具場景使用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, C-Q2, D-Q1

B-Q3: CacheDependency 的機制原理是什麼？
- A簡: 監聽依賴來源變化，來源變更時發送失效通知，讓相依的快取項目被清除。
- A詳: CacheDependency 接受一或多個依賴目標（檔案、資料夾、其他 Cache 鍵、SQL 等）。系統在背景監聽這些目標的變化（檔案系統通知、鍵移除事件），一旦有變更，即標記依賴失效並移除快取項目。此為典型觀察者模式應用，提供事件驅動的群組清除能力，避免主動掃描。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, C-Q6

B-Q4: 檔案相依如何觸發清除？
- A簡: 透過檔案變更通知（時間戳變動等），被依賴項目收到通知後移除自身。
- A詳: 建立 CacheDependency 時指定檔案路徑。底層使用檔案監控（如 FileSystemWatcher），監聽變動事件（修改時間、內容變更）。當檔案被 touch 或更新，快取收到通知，所有依賴該檔案的項目會被同步移除。需注意檔案路徑有效、權限與網路檔案系統延遲等細節。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, D-Q5

B-Q5: 列舉快取鍵的執行流程與風險？
- A簡: 迭代取得每個 DictionaryEntry，期間資料可能變更，需防護例外與一致性問題。
- A詳: 遍歷流程為：取得 enumerator → MoveNext → 讀取 Entry.Key/Value → 繼續。風險在於列舉非快照，項目可能於遍歷時被移除，導致 Value 為 null 或 InvalidOperation。建議先取出鍵清單副本，或限於管理情境低頻使用，避免在請求熱路徑執行 O(N) 掃描。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, D-Q2

B-Q6: Cache 項目何時會自動淘汰？
- A簡: 到期時間到、滑動期限未刷新、依賴變更、記憶體壓力與優先權策略等情況。
- A詳: 自動淘汰觸發於：AbsoluteExpiration 到達、SlidingExpiration 長時間未存取、CacheDependency 失效、系統記憶體壓力高於門檻時按優先權回收。這些機制確保快取不無限制成長，同時維持資料新鮮度。設計時需搭配清除策略，避免誤以為項目永久存在。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, D-Q9

B-Q7: 多條件分群清除如何設計？
- A簡: 以群組維度建立依賴或索引（網域、類型、協定），清除時觸發對應群組事件。
- A詳: 為每個維度（domain/type/protocol）建立群組單位：可用檔案依賴、鍵依賴或版本鍵。插入時附上對應群組依賴；清除時只需更新特定群組目標（touch 檔案、移除群組鍵、遞增版本）。若需交集清除，可組合多重依賴或在索引層維護交集映射。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: C-Q3, C-Q4, C-Q5

B-Q8: 用正則掃描鍵的流程與成本？
- A簡: 先列舉全鍵再 Regex.IsMatch 比對，屬 O(N) 操作，對大快取成本高且不穩定。
- A詳: 正則清除步驟：列舉 Cache → 對每鍵執行正則比對 → 命中則 Remove。此法開發容易，但在大型快取中線性成本明顯，且易受列舉不一致影響。適合管理工具、離峰維護，不建議在請求路徑或高頻操作中使用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, D-Q3

B-Q9: 自建 URL 反向索引應怎麼運作？
- A簡: 維持群組→鍵的映射集合，插入同步更新，清除時讀映射批次移除。
- A詳: 建立資料結構（如 ConcurrentDictionary<string, HashSet<string>>），鍵為群組標識（domain/type/protocol），值為對應快取鍵集合。插入快取時，同步更新群組集合；清除時，取出集合並逐鍵 Remove。需處理併發、安全移除與快取內鍵可能已被淘汰的情況，並定期壓縮集合。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: C-Q9, D-Q7

B-Q10: 分類檔（群組檔）設計要點？
- A簡: 每群一檔、可快速 touch、具寫入權限與唯一識別，避免共享鎖競爭。
- A詳: 檔案命名包含群組識別（如 group-domain-example.com.token），存放於可寫入目錄。每個群組對應一檔案，插入時建立對該檔案的 CacheDependency。清除時更新檔案時間。需避免放在高延遲或無權限的路徑，亦可集中至單一目錄以便管理與監控。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q6, D-Q4

B-Q11: 列舉期間項目消失如何處理？
- A簡: 使用存在性檢查、try-catch 包覆、或先複製鍵清單快照，避免例外中斷。
- A詳: 因不確定性，列舉到的鍵下一刻可能已失效。建議做法：先建立鍵清單快照再操作；取值時再次判空；對 Remove 包覆 try-catch；以批次方式記錄失敗項並重試；對關鍵邏輯增加重試與退避，確保整體流程穩健。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q2, C-Q2

B-Q12: 插入快取並附帶相依性的流程？
- A簡: 建立依賴→設定到期→Insert/Add 鍵值→可選移除回呼與優先權。
- A詳: 典型流程：先組裝鍵與值，建立 CacheDependency（檔案/鍵/SQL），決定 Absolute/SlidingExpiration 與 CacheItemPriority，必要時提供 CacheItemRemovedCallback。最後使用 Cache.Insert(key, value, dependency, abs, sliding, priority, callback) 插入。這讓後續清除可透過依賴自動進行。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q6, C-Q7

B-Q13: 依賴其他 Cache 鍵的清除機制？
- A簡: 以鍵作為依賴來源，被依賴鍵移除或變更時，相依項目會一併失效。
- A詳: CacheDependency 可指定 cacheKeys 陣列，表示當這些鍵被移除或失效時，當前項目同步清除。可用「群組控制鍵」做中心點，清除時只需 Remove 該群組鍵，即使其值為占位符，也能連帶移除所有依賴它的項目，避免檔案 I/O。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q7, A-Q12

B-Q14: 自訂 Tagging 與反向索引的原理？
- A簡: 為項目標記多個標籤，建立標籤到鍵的映射，清除時依標籤取鍵批次移除。
- A詳: 將群組語義抽象為標籤（如 domain:example.com、type:image/jpeg），在插入時把鍵加入每個標籤的集合（反向索引）。清除時查詢標籤集合，選擇性做交集或聯集，批次移除命中鍵。需處理集合併發、鍵消失同步、集合清理與一致性。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: C-Q9, B-Q9

B-Q15: 版本化命名空間的機制與影響？
- A簡: 以版本鍵管理群組版本，鍵組合含版本；清除為遞增版本，舊鍵自然失效。
- A詳: 為群組建立「版本鍵」（如 v:domain:example.com），讀取與寫入鍵時都讀取當前版本並組合實際鍵（k:domain:ver:...）。清除時只遞增版本鍵。優勢：常數時間、無掃描、無 I/O；權衡：舊資料殘留、需封裝 API 強制使用版本化鍵，並具備背景清理策略。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: C-Q8, A-Q17

B-Q16: 清除整群與逐鍵移除的效能比較？
- A簡: 整群清除為一次事件觸發，成本固定；逐鍵需多次操作，隨群組大小線性增加。
- A詳: 整群清除（依賴/版本）只需一次動作，系統內部批量失效，避免多次鎖競爭與迭代。逐鍵移除需要對每個鍵呼叫 Remove，造成累積延遲、鎖競爭與更高失敗率。對大型群組，整群方案能顯著降低延遲尖峰並提升一致性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, C-Q6

B-Q17: Cache 的併發與執行緒安全如何保障？
- A簡: 內部採鎖與原子操作保證基本安全，但高階操作仍需外部協調與去重建。
- A詳: Cache 的基本存取（Get/Insert/Remove）是執行緒安全。但高層流程如列舉＋移除、建構昂貴物件的「單航班」控制，仍需額外同步（如 Lazy、雙重檢查、鎖或記號鍵）來避免重複建構與競態清除。設計需考慮失敗重試與冪等行為，確保在多執行緒下穩健。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q7, C-Q10

B-Q18: 以 URL 作鍵的技術考量？
- A簡: 需規範化、編碼與長度管理，避免碰撞與不一致，建議加前綴分類。
- A詳: URL 應統一小寫、移除無意義片段、排序查詢參數並標準化。過長鍵可用雜湊縮短並保留可辨識前綴。對不同語義維度加前綴（domain/type/protocol/版本），以支援後續清除與維運。注意安全：避免原始 URL 含敏感資訊落入鍵名與日誌。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q3, A-Q15

B-Q19: 以 Content-Type 建群的機制？
- A簡: 下載時判斷內容類型，鍵加入 type 標籤或依賴，使同類型可一鍵清除。
- A詳: 於取得內容時解析 HTTP Header 的 Content-Type，將鍵寫入 type 對應的群組（檔案依賴、鍵依賴或索引集合）。清除該類型時只需觸發目標依賴或讀索引批次移除。這實現橫切維度的分群，對圖片、CSS、JSON 等類別管理很有效。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q4, B-Q7

B-Q20: 以 Protocol 建群的機制？
- A簡: 根據 http/https 等通訊協定設群組標籤或依賴，便於按協定範圍清除。
- A詳: 解析 URL 的 Scheme，於鍵設計加上 protocol 前綴或登記至 protocol 群組集合。同 Content-Type 類似，可用檔案依賴、鍵依賴、版本化或索引方式組織。用於安全策略變更（如憑證更新）或針對特定協定的清除作業。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q5, B-Q7

B-Q21: 快取項目大小與枚舉開銷的關係？
- A簡: 項目數量與鍵長影響列舉成本；項目越多、鍵越長，掃描與比對越慢。
- A詳: 列舉成本與項目數量呈線性，且每次比對（尤其正則）受鍵長影響。大量小鍵也會增加 GC 與迭代負擔。儘可能避免頻繁全掃描，必要時限制鍵集合大小、採分群清除或離線維護，減少在線路徑的枚舉操作。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, D-Q3

B-Q22: 檔案 I/O 成本與替代方案？
- A簡: I/O 延遲與權限是風險；可改用鍵依賴、版本化命名空間或索引以避開 I/O。
- A詳: 檔案相依需磁碟存取與事件監聽，受硬碟性能、網路檔案系統與權限影響。替代：鍵依賴（移除群組鍵）、版本鍵（遞增版本即失效）、反向索引（快速列出受影響鍵），皆可避免 I/O，同時保持群組清除語義；選擇取決於釋放記憶體的即時性與實作複雜度。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, C-Q7, C-Q8

B-Q23: 用觀察者模式看 CacheDependency？
- A簡: 依賴來源是主體，快取項目是觀察者；來源變更通知觀察者失效並移除。
- A詳: CacheDependency 建立起來源（檔案/鍵/SQL）到快取項目的通知通道。當來源狀態改變，通知傳遞至依賴者，依賴者執行清除。此設計解耦清除邏輯與項目管理，令群組失效自然、原子且一致，符合事件驅動架構思維。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, A-Q13

B-Q24: 快取清除與一致性如何保障？
- A簡: 以依賴或版本實現原子失效，避免掃描；對讀路徑做二次驗證與重建。
- A詳: 一致性來自「失效的可預測與原子性」。依賴或版本鍵確保整群同時失效；讀路徑發現 miss 或版本不符時重建資料。避免列舉＋逐鍵的中間態不一致。必要時搭配單航班鎖，避免同時多次重建造成壓力尖峰。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: D-Q6, B-Q17

B-Q25: ASP.NET 與 .NET Core 的替代技術對應？
- A簡: ASP.NET 用 Cache/CacheDependency；Core 使用 IMemoryCache、IChangeToken 或 MemoryCache。
- A詳: 在 ASP.NET 使用 System.Web.Caching.Cache 與 CacheDependency。於 ASP.NET Core，改用 Microsoft.Extensions.Caching.Memory.IMemoryCache，並以 IChangeToken/ChangeToken 或自訂監視達成相依失效。概念一致，但 API 與生命週期差異，需用對等機制重構。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q19, C-Q10


### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何用 Remove 移除指定鍵？
- A簡: 以精確鍵呼叫 HttpRuntime.Cache.Remove，項目存在即刪除並觸發移除回呼。
- A詳: 
  - 實作步驟: 準備確切鍵→呼叫 Remove→檢查返回。
  - 程式碼:
    ```csharp
    var removed = HttpRuntime.Cache.Remove("cache-key");
    if (removed == null) { /* 不存在或已被移除 */ }
    ```
  - 注意事項: 確保鍵一致化；移除無法保證其他相依項；可搭配移除回呼記錄原因。避免誤刪可採前綴限制或白名單。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, A-Q5

C-Q2: 如何安全列舉所有快取鍵？
- A簡: 使用 IDictionaryEnumerator 建快照再操作，過程中檢查存在並妥善處理例外。
- A詳: 
  - 步驟: 取得 enumerator→收集鍵至 List→針對快照逐一處理→對每次存取再判空。
  - 程式碼:
    ```csharp
    var keys = new List<string>();
    var e = HttpRuntime.Cache.GetEnumerator();
    while (e.MoveNext())
    {
        var de = (DictionaryEntry)e.Current;
        keys.Add((string)de.Key);
    }
    foreach (var k in keys)
    {
        var val = HttpRuntime.Cache[k];
        if (val != null) { /* do work */ }
    }
    ```
  - 注意: 避免熱路徑頻繁使用；控制批次大小；包覆 try-catch 避免中斷。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, D-Q1

C-Q3: 如何依網站網域分群並清除？
- A簡: 以網域為群組，插入時綁定網域依賴；清除時觸發該群組依賴或遞增版本。
- A詳:
  - 步驟: 解析 URL 網域→產生鍵前綴與群組目標→插入附依賴→清除時觸發。
  - 程式碼（鍵依賴法）:
    ```csharp
    string domain = new Uri(url).Host;
    string groupKey = $"g:domain:{domain}";
    HttpRuntime.Cache.Insert(groupKey, 1);
    var dep = new CacheDependency(null, new[] { groupKey });
    HttpRuntime.Cache.Insert($"k:{domain}:{url}", content, dep);
    // 清除該網域
    HttpRuntime.Cache.Remove(groupKey);
    ```
  - 注意: 鍵命名一致；處理多子網域；避免依賴鏈過深。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q13

C-Q4: 如何依 Content-Type 分群清除？
- A簡: 以 type 建群組鍵或檔案依賴，插入時綁定；清除時移除群組鍵或 touch 檔案。
- A詳:
  - 步驟: 取得 Content-Type→生成 type 群組→插入附依賴→清除。
  - 程式碼（檔案相依）:
    ```csharp
    string type = contentType.ToLowerInvariant();
    string token = HttpContext.Current.Server.MapPath($"~/cache-tokens/type-{type}.token");
    File.WriteAllText(token, "x"); // 確保存在
    var dep = new CacheDependency(token);
    HttpRuntime.Cache.Insert($"k:type:{type}:{url}", content, dep);
    // 清除該類型
    File.SetLastWriteTimeUtc(token, DateTime.UtcNow);
    ```
  - 注意: 檔案路徑權限；Type 正規化；或改用鍵依賴避免 I/O。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q19, B-Q22

C-Q5: 如何依 Protocol 分群清除？
- A簡: 以 http/https 協定建立群組，插入綁定依賴；清除時觸發該協定群組。
- A詳:
  - 步驟: 解析 URL Scheme→建立群組鍵→插入附依賴→移除群組鍵。
  - 程式碼（鍵依賴）:
    ```csharp
    string scheme = new Uri(url).Scheme; // http or https
    string groupKey = $"g:proto:{scheme}";
    HttpRuntime.Cache.Insert(groupKey, 1);
    var dep = new CacheDependency(null, new[] { groupKey });
    HttpRuntime.Cache.Insert($"k:proto:{scheme}:{url}", content, dep);
    // 清除該協定
    HttpRuntime.Cache.Remove(groupKey);
    ```
  - 注意: 限定語義一致；避免與其他群組鍵衝突；可搭配版本鍵。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q20, A-Q11

C-Q6: 如何實作檔案相依的一鍵群組清除？
- A簡: 每群對應一個 token 檔，插入附檔案依賴；清除時更新檔案時間戳。
- A詳:
  - 步驟: 建立群組 token 檔→插入快取時附 CacheDependency(token)→清除時 touch。
  - 程式碼:
    ```csharp
    string token = Server.MapPath("~/cache-tokens/domain-example.com.token");
    if (!File.Exists(token)) File.WriteAllText(token, "x");
    var dep = new CacheDependency(token);
    HttpRuntime.Cache.Insert("k:domain:example.com:...", content, dep);
    // 清除整群
    File.SetLastWriteTimeUtc(token, DateTime.UtcNow);
    ```
  - 注意: I/O 成本與權限；集中管理 token；監控失敗重試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q4

C-Q7: 如何用鍵依賴實作群組清除？
- A簡: 建立群組控制鍵，項目依賴該鍵；清除時 Remove 控制鍵觸發連帶失效。
- A詳:
  - 步驟: Insert 群組鍵→插入項目附 CacheDependency(cacheKeys: groupKey)→清除時 Remove(groupKey)。
  - 程式碼:
    ```csharp
    var groupKey = "g:type:image-jpeg";
    HttpRuntime.Cache.Insert(groupKey, 1);
    var dep = new CacheDependency(null, new[] { groupKey });
    HttpRuntime.Cache.Insert("k:type:image-jpeg:...", content, dep);
    // 清除整群
    HttpRuntime.Cache.Remove(groupKey);
    ```
  - 注意: 群組鍵需常駐；避免過度巢狀依賴；清除語義清楚。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q13, A-Q12

C-Q8: 如何實作版本化命名空間清除？
- A簡: 使用版本鍵管理群組版本，鍵組合包含版本；清除時只需遞增版本鍵。
- A詳:
  - 步驟: 建立版本鍵→讀取版本→組合實際鍵→插入/讀取均附版本→清除時遞增。
  - 程式碼:
    ```csharp
    string vKey = "v:domain:example.com";
    int ver = (int?)HttpRuntime.Cache[vKey] ?? 1;
    HttpRuntime.Cache.Insert(vKey, ver);
    string key = $"k:domain:{ver}:{url}";
    HttpRuntime.Cache.Insert(key, content);
    // 清除整群
    HttpRuntime.Cache.Insert(vKey, ver + 1);
    ```
  - 注意: 封裝 API 嚴格使用版本鍵；殘留舊資料需自然淘汰；可定期清理。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q15, A-Q17

C-Q9: 如何建立反向索引避免全域掃描？
- A簡: 維護群組到鍵集合的並行字典，清除時從集合取鍵逐一移除。
- A詳:
  - 步驟: 建立 ConcurrentDictionary<string, ConcurrentDictionary<string, byte>>→插入時加入→清除時取集合並 Remove。
  - 程式碼:
    ```csharp
    static ConcurrentDictionary<string, ConcurrentDictionary<string, byte>> idx = new();
    void Index(string group, string key) {
        var set = idx.GetOrAdd(group, _ => new());
        set.TryAdd(key, 0);
    }
    void Clear(string group){
        if (idx.TryGetValue(group, out var set))
            foreach (var k in set.Keys) HttpRuntime.Cache.Remove(k);
    }
    ```
  - 注意: 同步與清理；鍵已失效需忽略；避免集合無界成長。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q9, B-Q14

C-Q10: 如何設計可測試的 Cache 包裝器？
- A簡: 以介面抽象快取操作，注入實作（HttpRuntime 或 MemoryCache），便於單元測試。
- A詳:
  - 步驟: 定義 ICache（Get/Set/Remove）→實作 AspNetCacheAdapter → 測試時注入 Fake/MemoryCache。
  - 程式碼:
    ```csharp
    public interface ICache { object Get(string k); void Set(string k, object v); object Remove(string k); }
    public class AspNetCache : ICache {
      public object Get(string k)=>HttpRuntime.Cache[k];
      public void Set(string k, object v)=>HttpRuntime.Cache.Insert(k, v);
      public object Remove(string k)=>HttpRuntime.Cache.Remove(k);
    }
    ```
  - 注意: 包含依賴、到期與回呼擴充；確保執行緒安全；易於替換於 Core 環境。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q25, B-Q17


### Q&A 類別 D: 問題解決類（10題）

D-Q1: 列舉鍵時出現型別或轉型錯誤怎麼辦？
- A簡: 使用 IDictionaryEnumerator 讀取 DictionaryEntry，再取 Key/Value，避免直接轉型字串。
- A詳:
  - 症狀: foreach 時 InvalidCastException 或取得非預期型別。
  - 可能原因: 直接將 Current 轉 string；未使用 DictionaryEntry。
  - 解決步驟: 改用 IDictionaryEnumerator；以 DictionaryEntry 讀 Key/Value；建立鍵快照再用。
  - 預防: 封裝列舉工具方法；避免在業務程式直接列舉。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, C-Q2

D-Q2: 列舉時項目瞬間消失導致 NullReference？
- A簡: 快取不確定性所致，對每次取值做判空，採快照與重試機制避免中斷。
- A詳:
  - 症狀: 取值為 null 或操作中拋 NullReference/InvalidOperation。
  - 原因: 列舉期間項目到期/被移除。
  - 解決: 快照鍵清單；每次取值再檢查；失敗記錄並跳過；必要時重試。
  - 預防: 避免熱路徑列舉；採群組清除或索引替代掃描。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q11

D-Q3: 用 Regex 掃描鍵效能不佳怎麼辦？
- A簡: 降低掃描頻率與範圍，改用依賴、版本或反向索引，避免 O(N) 列舉。
- A詳:
  - 症狀: 清除操作耗時長、偶發延遲尖峰。
  - 原因: 全域列舉＋正則比對成本高。
  - 解決: 改群組清除（檔案/鍵依賴、版本鍵）；或維護反向索引。
  - 預防: 鍵命名含前綴與群組語義；管理工具離峰執行掃描。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, B-Q22

D-Q4: 檔案相依引發過多 I/O 怎麼優化？
- A簡: 改鍵依賴或版本鍵；若仍用檔案，集中目錄、合併群組與批量操作。
- A詳:
  - 症狀: 清除或插入時磁碟 IO 高、延遲上升。
  - 原因: token 檔過多、頻繁 touch、網路檔案系統延遲。
  - 解決: 改用鍵依賴/版本鍵；或將 token 合併、集中本機磁碟。
  - 預防: 限制群組數量；監控 IO；權限與鎖控妥善配置。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, C-Q6, C-Q7

D-Q5: 觸發 CacheDependency 卻未清除？
- A簡: 檢查相依目標是否正確與可達，權限、路徑與監聽是否生效，重建依賴測試。
- A詳:
  - 症狀: 更新檔案或移除群組鍵後，快取仍存在。
  - 原因: 檔案路徑錯誤/無權限；依賴未綁定；群組鍵未先插入；監聽失效。
  - 解決: 驗證路徑與權限；檢查 Insert 是否附依賴；重新建立依賴；加上記錄與回呼檢查。
  - 預防: 封裝依賴建立；部署測試；加健康檢查。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q13

D-Q6: 移除鍵仍讀到舊資料的原因？
- A簡: 有其他副本、版本鍵未更新、讀路徑未統一使用封裝，導致命中不同鍵。
- A詳:
  - 症狀: Remove 之後仍取得舊值。
  - 原因: 多鍵指向相同資料；鍵不一致（未含版本）；讀寫未經相同 API。
  - 解決: 統一鍵規則；導入版本鍵；清理相關群組；檢查回呼與日誌。
  - 預防: 封裝存取；加測試覆蓋多情境；監控命中率變化。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q24, C-Q8

D-Q7: 多執行緒下清除與重建產生競態？
- A簡: 使用單航班與記號鍵協調，確保同群組只重建一次，清除與建構分離。
- A詳:
  - 症狀: 清除後同時多線程重建，造成壓力尖峰。
  - 原因: 未控管重建臨界區；缺乏去重建機制。
  - 解決: 用 Lazy 或鎖保護建構；用「建構中」記號鍵；超時與重試策略。
  - 預防: 封裝讀寫 API；壓力測試；設定優先權與到期減輕壓力。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q17, C-Q10

D-Q8: 鍵命名碰撞或重複如何處理？
- A簡: 規範化與前綴區隔，必要時加雜湊與版本片段，並加入防重測試。
- A詳:
  - 症狀: 不同資料覆蓋同鍵、清除誤傷。
  - 原因: 未標準化 URL；缺少命名空間/前綴；鍵長限制導致截斷。
  - 解決: 加入明確前綴與版本；URL 正規化與雜湊；鍵生成封裝。
  - 預防: 靜態分析與單元測試；日誌追蹤鍵映射。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q18, C-Q8

D-Q9: 快取佔用過多記憶體導致頻繁回收？
- A簡: 限制項目數與大小，設定適當到期與優先權，必要時改群組清除釋放空間。
- A詳:
  - 症狀: 命中率下降、延遲升高、頻繁淘汰。
  - 原因: 無界快取；到期策略不當；大型項目過多。
  - 解決: 加上大小/數量限制（邏輯層）；縮短到期或用滑動；群組清除非熱資料。
  - 預防: 監控記憶體與命中率；調整優先權；分層快取。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q16

D-Q10: 生產環境權限不足無法使用檔案相依？
- A簡: 改用鍵依賴或版本鍵；若必用檔案，相容地配置可寫目錄與最小權限。
- A詳:
  - 症狀: 建立 CacheDependency(檔案) 失敗或無法監聽。
  - 原因: 應用帳號無寫入或監聽權限；路徑不允許。
  - 解決: 切換到鍵依賴或版本鍵；或調整目錄與 ACL。
  - 預防: 部署前檢查權限；提供降級方案；封裝依賴策略可切換。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q22, C-Q7, C-Q8


### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 ASP.NET 的 Cache 物件？
    - A-Q2: HttpRuntime.Cache 有什麼用途與特性？
    - A-Q3: Cache 與 Dictionary 有何差異？
    - A-Q4: 為什麼需要手動從 Cache 移除物件？
    - A-Q5: 什麼是 Cache Key？為何重要？
    - A-Q11: 刪除部分 Cache 的常見情境有哪些？
    - A-Q14: Cache 的 GetEnumerator 是什麼？
    - B-Q1: Cache.Remove 如何運作？
    - B-Q2: GetEnumerator 的回傳與列舉流程是什麼？
    - B-Q6: Cache 項目何時會自動淘汰？
    - C-Q1: 如何用 Remove 移除指定鍵？
    - C-Q2: 如何安全列舉所有快取鍵？
    - D-Q1: 列舉鍵時出現型別或轉型錯誤怎麼辦？
    - D-Q2: 列舉時項目瞬間消失導致 NullReference？
    - D-Q3: 用 Regex 掃描鍵效能不佳怎麼辦？

- 中級者：建議學習哪 20 題
    - A-Q6: 為何直接列舉所有 Cache 鍵有風險？
    - A-Q7: 什麼是 Cache 的「不確定性」？
    - A-Q8: 什麼是 CacheDependency？
    - A-Q9: 檔案相依性如何用於分群清除？
    - A-Q10: 用正則篩鍵與自建索引清除的差異？
    - A-Q16: 為什麼不建議每次都掃描整個 Cache？
    - B-Q3: CacheDependency 的機制原理是什麼？
    - B-Q4: 檔案相依如何觸發清除？
    - B-Q7: 多條件分群清除如何設計？
    - B-Q8: 用正則掃描鍵的流程與成本？
    - B-Q13: 依賴其他 Cache 鍵的清除機制？
    - B-Q16: 清除整群與逐鍵移除的效能比較？
    - B-Q17: Cache 的併發與執行緒安全如何保障？
    - B-Q18: 以 URL 作鍵的技術考量？
    - B-Q19: 以 Content-Type 建群的機制？
    - B-Q20: 以 Protocol 建群的機制？
    - C-Q3: 如何依網站網域分群並清除？
    - C-Q4: 如何依 Content-Type 分群清除？
    - C-Q5: 如何依 Protocol 分群清除？
    - D-Q5: 觸發 CacheDependency 卻未清除？

- 高級者：建議關注哪 15 題
    - A-Q12: 為何「檔案相依清除」既聰明又愚蠢？
    - A-Q17: 什麼是版本化命名空間清除？
    - B-Q9: 自建 URL 反向索引應怎麼運作？
    - B-Q14: 自訂 Tagging 與反向索引的原理？
    - B-Q15: 版本化命名空間的機制與影響？
    - B-Q22: 檔案 I/O 成本與替代方案？
    - B-Q24: 快取清除與一致性如何保障？
    - B-Q25: ASP.NET 與 .NET Core 的替代技術對應？
    - C-Q6: 如何實作檔案相依的一鍵群組清除？
    - C-Q7: 如何用鍵依賴實作群組清除？
    - C-Q8: 如何實作版本化命名空間清除？
    - C-Q9: 如何建立反向索引避免全域掃描？
    - C-Q10: 如何設計可測試的 Cache 包裝器？
    - D-Q4: 檔案相依引發過多 I/O 怎麼優化？
    - D-Q7: 多執行緒下清除與重建產生競態？