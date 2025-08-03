---
source_file: "_posts/2018/2018-03-25-interview01-transaction.md"
generated_date: "2025-08-03 13:45:00 +0800"
version: "1.0"
tools:
  - github_copilot
model: "github-copilot"
---

# 架構面試題 #1, 線上交易的正確性 - 生成內容

## Metadata

### 原始 Metadata
```yaml
layout: post
title: "架構面試題 #1, 線上交易的正確性"
categories:
- "系列文章: 架構師觀點"
- "系列文章: 架構面試題"
tags: ["架構師", "面試經驗", "microservices"]
published: true
comments: true
redirect_from:
logo: /wp-content/uploads/2018/03/whiteboard-interviews.png
```

### 自動識別關鍵字
keywords:
  primary:
    - 架構面試
    - 線上交易
    - 交易正確性
    - ACID
    - 分散式鎖定
  secondary:
    - Racing Condition
    - Critical Section
    - SQL Transaction
    - Distributed Lock
    - 微服務架構

### 技術堆疊分析
tech_stack:
  languages:
    - C#
    - SQL
  frameworks:
    - .NET
    - Dapper
  tools:
    - Visual Studio
    - SQL Server
    - MongoDB
    - Redis
    - Docker
  platforms:
    - Windows
    - Linux Container

### 參考資源
references:
  internal_links:
    - 系列文章: 架構師觀點
    - 系列文章: 架構面試題
  external_links:
    - https://github.com/donnemartin/system-design-primer
    - https://zh.wikipedia.org/wiki/ACID
    - https://en.wikipedia.org/wiki/Race_condition
    - https://redis.io/topics/distlock
    - https://github.com/samcook/RedLock.net
    - https://github.com/andrew0928/InterviewQuiz
  mentioned_tools:
    - Dapper
    - RedLock.net
    - MongoDB
    - Redis

### 內容特性
content_metrics:
  word_count: 4800
  reading_time: "24 分鐘"
  difficulty_level: "高級"
  content_type: "教學"

## 摘要 (Summaries)

### 文章摘要 (Article Summary)
作者從面試官的角度出發，設計了一個經典的線上交易正確性考題，用來評估後端工程師在微服務架構下的技術能力。文章透過一個簡單的銀行帳戶交易系統，從單機版、SQL 交易版，到分散式鎖定版，逐步展示了不同規模下解決交易正確性問題的三種方案。作者強調金錢守恆定律的重要性，要求在任何情況下都不能讓錢憑空產生或消失。透過具體的 C# 程式碼範例和測試結果，作者詳細說明了 Racing Condition 的成因、ACID 原則的應用，以及如何運用 Lock、SQL Transaction 和 Distributed Lock 等技術來確保交易的正確性。這篇文章不僅是面試考題的分享，更是一個完整的分散式系統交易處理教學案例。

### 關鍵要點 (Key Points)
- 金錢守恆定律：在封閉系統內，錢只會轉移不會憑空產生或消失
- Racing Condition 是導致交易錯誤的主要原因
- 三種解決方案對應不同系統規模：Lock (單機)、SQL Transaction (多機)、Distributed Lock (微服務)
- ACID 原則是確保交易正確性的核心概念
- 分散式環境下需要運用 Redis 等外部儲存實現分散式鎖定

### 段落摘要 (Section Summaries)

1. **前言 & 導讀**：作者說明了設計這個面試考題的動機和思維過程。不同於 LeetCode 式的標準答案題型，作者更重視應試者解決問題的思考過程和在不同規模環境下的適應能力。作者期望找到能以微服務或 Cloud Native 角度思考問題的工程師，而非只會背誦標準答案的人。文章強調「沒有最完美的架構，只有最合適的架構」這個核心概念，並說明如何透過應用題來測試應試者找出最合適架構的能力。這種面試方式能夠有效評估工程師在面對不同系統規模時的技術深度和廣度。

2. **考題定義與測試框架**：作者定義了一個抽象的銀行帳戶類別 AccountBase，包含 GetBalance() 和 ExecTransaction() 兩個核心方法。測試重點在於確保多執行緒環境下的交易正確性，遵循金錢守恆定律。作者設計了一個嚴格的測試案例：使用 N 個執行緒，每個執行緒執行 M 次交易，每次存入 1 元，最終帳戶餘額必須精確增加 N × M × 1 元。這個測試框架能夠有效檢驗各種實作方式在並行環境下的正確性，同時也能比較不同方案的效能表現。測試結果的準確性是判斷實作是否合格的唯一標準。

3. **解法1：單機版 Lock 機制**：針對單機環境，作者展示了使用 C# lock 語句來解決 Racing Condition 問題的方法。透過將交易紀錄新增和餘額更新包裝在 Critical Section 內，確保這兩個操作的原子性。作者特別準備了一個對照組（移除 lock 的版本），結果顯示沒有 lock 保護的版本會損失約 20% 的金額，充分證明了 lock 機制的重要性。這個解法的關鍵概念包括 Lock、Critical Section 和 Racing Condition，是所有並行程式設計的基礎。雖然效能略有影響，但正確性是不可妥協的首要條件。

4. **解法2：SQL Transaction 應用**：當系統規模擴大到需要資料庫支援時，作者展示了如何運用 SQL Server 的交易機制來確保資料一致性。透過將插入交易紀錄和更新帳戶餘額包裝在同一個 SQL 交易中，讓 DBMS 負責確保 ACID 原則。這種方法的優點是程式碼相對簡潔，交易處理完全委託給成熟的資料庫系統。作者使用 Dapper 作為資料存取框架，並提供了完整的資料表 Schema。雖然這種方法能有效解決多機環境下的交易問題，但受限於單一 DBMS 的處理能力，在超大規模的微服務環境下仍有其限制。

5. **解法3：分散式鎖定機制**：面對微服務架構下的挑戰，作者選擇 MongoDB（不支援交易）配合 Redis 實現分散式鎖定機制。透過 RedLock.net 套件，將原本單機版的 lock 概念擴展到分散式環境。這個方案展示了如何在不支援交易的 NoSQL 環境下，仍能確保交易的正確性。作者特別強調實作分散式鎖定的複雜性，包括鎖定失敗的重試機制、超時處理等細節。透過實際的多程序測試（10 個程序、20 個執行緒並行處理 200,000 筆交易），證明了這種方法在大規模分散式環境下的可行性和準確性。

## 問答集 (Q&A Pairs)

### Q1: 什麼是金錢守恆定律？
Q: 在交易系統設計中，什麼是金錢守恆定律？
A: 金錢守恆定律是指在一個封閉系統內，錢只會從某個地方轉移到另一個地方，整個系統的所有金額總和一定是不變的，除非有錢從外部系統轉移進來或轉出去。錢不應該憑空產生出來，也不會憑空消失。無論任何情況都不允許交易只做一半，一邊扣了錢，另一邊卻沒有拿到錢。

### Q2: 什麼是 Racing Condition？
Q: Racing Condition 是如何導致交易錯誤的？
A: Racing Condition 發生在多個執行緒同時執行「讀取-計算-寫入」的操作時，兩個動作重疊會導致某些運算結果被別的執行緒覆蓋掉。例如兩個執行緒同時讀取餘額 100 元，分別加上 50 元後寫回，最終結果可能是 150 元而非正確的 200 元，造成 50 元憑空消失。

### Q3: 如何使用 C# 的 lock 機制解決單機交易問題？
Q: 在單機環境下如何使用 lock 確保交易正確性？
A: 將交易紀錄新增和餘額更新這兩個操作包裝在 lock 語句內，建立 Critical Section。在 Critical Section 範圍內不允許並行狀態，確保「讀取-計算-寫入」這組動作的原子性。使用方式如：lock (this._syncroot) { /* 交易操作 */ }。

### Q4: SQL Transaction 如何確保交易正確性？
Q: 為什麼 SQL Transaction 能解決多機環境下的交易問題？
A: SQL Transaction 透過 DBMS 的 ACID 原則來確保交易正確性。將多個 SQL 操作包裝在 BEGIN TRAN 和 COMMIT 之間，DBMS 會確保這些操作要麼全部成功，要麼全部失敗。交易處理完全委託給成熟的資料庫系統，程式碼相對簡潔且可靠。

### Q5: 什麼是分散式鎖定？
Q: 在微服務架構下如何實現分散式鎖定？
A: 分散式鎖定是將單機 lock 的概念擴展到多個服務實例之間。常見做法是使用 Redis 等高速共享儲存，讓所有服務實例透過同一個鎖定資源來達到互斥效果。需要處理鎖定失敗重試、超時釋放等機制，可使用 RedLock 等成熟套件實現。

### Q6: 為什麼大規模系統較少使用 RDBMS？
Q: 在微服務架構下，RDBMS 有什麼限制？
A: RDBMS 強調關聯性和 schema 正規化，在需要靈活變化 schema、處理結構化資料（JSON/XML）或需要 CAP 定理中的 AP 特性時，NoSQL 更適合。微服務架構需要各服務獨立選擇合適的儲存技術，面對跨 DB 的分散式交易問題時，需要在應用層面處理。

### Q7: 如何驗證分散式交易的正確性？
Q: 如何測試分散式環境下的交易正確性？
A: 可以透過多程序並行測試來驗證。例如啟動 10 個程序，每個程序 20 個執行緒，總共處理 200,000 筆交易，最後檢查資料庫中的最終餘額是否與預期值完全一致。任何金額差異都表示交易實現有問題。

### Q8: 實現分散式鎖定需要注意哪些細節？
Q: 在實作分散式鎖定時有哪些重要考量？
A: 主要包括：1) 鎖定失敗的重試機制和等待時間；2) 鎖定超時自動釋放，避免死鎖；3) 選擇可靠的共享儲存（如 Redis）；4) 使用成熟的套件（如 RedLock）而非自行實作；5) 需要有 compare-and-swap 等原子操作支援。

## 解決方案 (Solutions)

### P1: 多執行緒環境下的交易錯誤
Problem: 在多執行緒環境下執行交易操作時，會發生 Racing Condition 導致交易金額計算錯誤，違反金錢守恆定律。
Root Cause: 多個執行緒同時執行「讀取餘額-計算新值-寫入餘額」的操作，當這些操作交錯執行時，後執行的寫入操作會覆蓋前面的計算結果，導致部分交易被遺失。
Solution: 
- 使用 lock 機制建立 Critical Section
- 將讀取、計算、寫入包裝為原子操作
- 確保同一時間只有一個執行緒能執行交易操作
Example: 
```csharp
lock (this._syncroot)
{
    this._history.Add(new TransactionItem() { Amount = transferAmount });
    return this._balance += transferAmount;
}
```

### P2: 多機環境下的資料一致性問題
Problem: 當系統擴展到多台機器時，單機的 lock 機制無法跨機器作用，需要在資料庫層面確保交易一致性。
Root Cause: 應用程式層面的鎖定機制僅能在單一程序內生效，無法控制多台機器上的並行操作，需要依賴資料庫的交易機制。
Solution:
- 使用 SQL Transaction 將多個資料庫操作包裝成一個原子交易
- 透過 DBMS 的 ACID 原則確保資料一致性
- 將交易邏輯委託給成熟的資料庫系統處理
Example:
```sql
BEGIN TRAN
INSERT [transactions] ([userid], [amount]) VALUES (@name, @transfer);
UPDATE [accounts] SET [balance] = [balance] + @transfer WHERE userid = @name;
COMMIT
```

### P3: 微服務架構下的跨服務交易問題
Problem: 在微服務架構中，服務可能使用不同的資料庫（包括 NoSQL），無法依賴單一 DBMS 的交易機制，需要實現分散式交易控制。
Root Cause: 微服務強調服務獨立性，各服務可能選擇不同的儲存技術，跨服務的交易無法透過傳統的資料庫交易機制解決，需要在應用層實現分散式協調。
Solution:
- 使用分散式鎖定機制（如 Redis + RedLock）
- 透過外部共享儲存實現跨服務的互斥控制
- 處理鎖定失敗重試和超時釋放機制
- 選擇可靠的分散式鎖定套件
Example:
```csharp
using (var redLock = this._redlock.CreateLock(resource, expiry, wait, retry))
{
    if (redLock.IsAcquired)
    {
        // 執行交易操作
        // 更新 MongoDB 資料
        // 記錄交易歷史
    }
}
```

### P4: 鎖定機制的可靠性問題
Problem: 自行實作的鎖定機制可能不夠可靠，在分散式環境下更容易出現問題，需要基於成熟的理論和實作。
Root Cause: 實作可靠的鎖定機制需要深厚的作業系統和分散式系統知識，包括原子操作、死鎖避免、網路分區處理等複雜問題。
Solution:
- 基於 CPU 提供的原子指令（compare-and-swap）
- 使用經過驗證的開源套件（如 RedLock.net）
- 了解分散式鎖定的理論基礎
- 避免自行實作底層的鎖定機制
Example:
- 選擇 RedLock.net 基於 Redis 實現分散式鎖定
- 配置適當的超時和重試參數
- 參考 Redis 官方的分散式鎖定文件

### P5: 系統規模擴展時的架構選擇問題
Problem: 隨著系統規模的增長，需要選擇合適的技術架構，從單機到多機再到微服務，每個階段都有不同的最佳實踐。
Root Cause: 不同規模的系統面臨不同的技術挑戰，沒有一體適用的解決方案，需要根據具體情境選擇最合適的技術棧。
Solution:
- 單機版（1 host）：使用程式語言內建的 lock 機制
- 多機版（10+ hosts）：使用 SQL Transaction 和 RDBMS
- 微服務版（100+ hosts）：使用分散式鎖定和 NoSQL
- 根據系統規模和需求選擇合適的技術組合
Example:
- 評估系統的並行需求和規模預期
- 選擇對應層級的技術解決方案
- 設計可擴展的架構，支援未來的成長需求

## 版本異動紀錄

### v1.0 (2025-08-03)
- 初始版本，基於原始文章生成 embedding content
- 包含完整的 metadata、摘要、問答對和解決方案
- 遵循 embedding-structure.instructions.md 規範
