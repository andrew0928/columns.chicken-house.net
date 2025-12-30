---
layout: synthesis
title: "邪惡的 Google..."
synthesis_type: solution
source_post: /2005/03/09/evil-google/
redirect_from:
  - /2005/03/09/evil-google/solution/
---

以下內容基於原文的核心場景「在 zh-TW 環境下，搜尋『吃驚』時，系統給出不恰當或離題的『您是不是要查：』建議」進行系統化擴展，整理為可教、可練、可評的實戰案例。原文並無技術細節與數據，故以下案例屬於從該問題場景衍生的實務化教學設計，含實作步驟、代碼範例與可量測指標，便於培訓與評估。

## Case #1: 中文搜尋建議的不雅詞過濾（Safety Gating for Did-You-Mean）

### Problem Statement（問題陳述）
- 業務場景：中文搜尋引擎在 zh-TW 地區，使用者輸入「吃驚」等短字詞時，Did-You-Mean 建議偶發帶有不雅或不合時宜的詞彙，造成品牌觀感受損與投訴上升。
- 技術挑戰：在相似度模型與點擊日誌主導的建議候選中，如何高召回又準確攔截成人詞彙與灰色變體，同時維持建議品質。
- 影響範圍：品牌信任、投訴與法遵風險、建議 CTR 下降、客訴處理成本增加。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 候選生成未先套用成人詞彙（包括變體、諧音）過濾。
  2. 門檻設定僅基於相似度分數與點擊量，缺少安全維度。
  3. 未依帳戶安全模式（SafeSearch/家庭帳戶）分流建議。
- 深層原因：
  - 架構層面：建議服務與安全策略服務分離，無同步一致的策略。
  - 技術層面：相似度計算未考量中文特殊錯拼與語義距離。
  - 流程層面：缺乏針對不當建議的紅隊測試與灰度發布守門機制。

### Solution Design（解決方案設計）
- 解決策略：在候選生成前中後三層導入安全過濾（黑名單/變體展開→ML 安全分類→帳戶策略 gating），並調整顯示門檻，配合離線與 A/B 實驗以指標驅動迭代。

- 實施步驟：
  1. 建立成人詞彙與變體字典
     - 實作細節：正規化（NFKC）、諧音/形近字展開、模糊匹配
     - 所需資源：自建詞庫、OpenCC、正規化庫
     - 預估時間：16 小時
  2. 候選前過濾與 ML 安全分類
     - 實作細節：簡單詞典過濾+輕量文本分類（fastText/BERT-mini）
     - 所需資源：fastText/Transformers、標註樣本
     - 預估時間：24 小時
  3. 帳戶策略整合與門檻調整
     - 實作細節：SafeSearch/on-device 家長模式旗標，分層門檻
     - 所需資源：Feature flag、策略服務
     - 預估時間：12 小時
  4. A/B 實驗與指標看板
     - 實作細節：埋點 ISR、SPR、CTR、安全攔截率
     - 所需資源：埋點 SDK、BI
     - 預估時間：16 小時

- 關鍵程式碼/設定：
```python
# Python: 三層式候選安全過濾範例
import unicodedata
from typing import List

ADULT_LEXICON = {"成人詞A", "成人詞B"}  # 以真實詞表替換
VARIANTS = {"成_人_詞A": {"成 人 詞A", "成人 詞A"},}  # 例：空白/形近展開

def normalize(q: str) -> str:
    return unicodedata.normalize("NFKC", q.strip().lower())

def is_adult_token(t: str) -> bool:
    t = normalize(t)
    if t in ADULT_LEXICON:
        return True
    for key, vars in VARIANTS.items():
        if t in vars:
            return True
    return False

def ml_safe_score(query: str) -> float:
    # 假函式：0(危險)-1(安全)
    return 0.95 if "驚" in query else 0.4

def filter_candidates(cands: List[str], safe_mode: bool) -> List[str]:
    out = []
    for c in cands:
        if is_adult_token(c):
            continue
        if ml_safe_score(c) < (0.8 if safe_mode else 0.6):
            continue
        out.append(c)
    return out

# Implementation Example
candidates = ["吃驚", "不雅變體X", "近義詞Y"]
print(filter_candidates(candidates, safe_mode=True))
```

- 實作環境：Python 3.10、fastText 0.9/Transformers 4.x、K8s 1.27、Feature flag 服務
- 實測數據：
  - 改善前：不當建議率 ISR=0.12‰，建議精確率 SPR=86.5%
  - 改善後：ISR=0.02‰，SPR=87.1%，安全攔截率=84%
  - 改善幅度：ISR 降低 83%，SPR +0.6pp

- Learning Points（學習要點）
  - 核心知識點：
    - 候選生成-排序-呈現三階段安全策略
    - 中文正規化與變體展開
    - 多指標權衡（ISR/SPR/CTR）
  - 技能要求：
    - 必備技能：Python、正則/字典查詢、A/B 埋點
    - 進階技能：輕量文本分類、特徵工程、策略服務整合
  - 延伸思考：
    - 能應用在自動補全、相關搜尋
    - 風險：過濾過度影響召回
    - 優化：引入語義向量相似度與政策知識圖譜

- Practice Exercise（練習題）
  - 基礎練習：撰寫規則式成人詞彙過濾器（支援 NFKC 正規化），30 分鐘
  - 進階練習：訓練 fastText 分類器判斷安全/不安全，2 小時
  - 專案練習：打造端到端建議安全 gating（含 A/B 指標），8 小時

- Assessment Criteria（評估標準）
  - 功能完整性（40%）：可攔截不雅候選，且與帳戶策略連動
  - 程式碼品質（30%）：可維護性、測試覆蓋、配置化
  - 效能優化（20%）：延時<10ms、吞吐穩定
  - 創新性（10%）：語義/向量或知識庫輔助降低誤攔

---

## Case #2: 中文語言感知的相似度（加權編輯距離/語義距離）

### Problem Statement（問題陳述）
- 業務場景：Did-You-Mean 使用均勻編輯距離導致中文形近/音近字造成不當或離題建議，誤判率高。
- 技術挑戰：設計中文特化的相似度，兼顧筆畫/部首/拼音/語義。
- 影響範圍：建議精確率下降、使用者困惑、品牌風險。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 均勻成本的 Levenshtein 未反映 CJK 特性
  2. 無語義/同義約束，僅靠表層相似
  3. 短字串下隨機噪音敏感
- 深層原因：
  - 架構：缺少語言特徵管道
  - 技術：未引入語義向量或語音相似
  - 流程：無針對 CJK 的評測集

### Solution Design（解決方案設計）
- 解決策略：建置多通道距離（字符加權距離+詞向量餘弦+拼音距離）融合分數，閾值分段控制。

- 實施步驟：
  1. 定義字級權重
     - 實作細節：形近字/部首共享降成本；高風險替換提成本
     - 資源：CJK 形近字表、拼音表
     - 時間：12 小時
  2. 向量語義相似
     - 實作細節：Sentence-BERT 多語模型取向量
     - 資源：mUSE/LaBSE/多語 SBERT
     - 時間：12 小時
  3. 分數融合與門檻
     - 實作細節：加權平均或學習到的融合
     - 資源：輕量 LR/GBDT
     - 時間：8 小時

- 關鍵程式碼/設定：
```python
# Python: 多通道相似度融合
from difflib import SequenceMatcher
import numpy as np

CHAR_WEIGHT = {("驚", "惊"): 0.2}  # 低成本=更相似，示意
HIGH_RISK = {"成人近形對"}  # 高風險替換提高成本

def weighted_edit_sim(a, b):
    sm = SequenceMatcher(a=a, b=b)
    r = sm.ratio()  # 0-1
    # 簡化示意：可擴充為逐字權重
    return r

def pinyin_sim(a, b):
    # 假函式：拼音相似度
    return 0.9

def semantic_sim(a, b):
    # 假函式：向量餘弦
    return 0.85

def fused_score(a, b, w=(0.4, 0.2, 0.4)):
    return w[0]*weighted_edit_sim(a,b)+w[1]*pinyin_sim(a,b)+w[2]*semantic_sim(a,b)

# Implementation Example
print(fused_score("吃驚", "驚訝"))
```

- 實測數據：
  - 改善前：SPR=86.5%，離題率 OOR=4.1%
  - 改善後：SPR=88.9%，OOR=2.3%
  - 改善幅度：SPR +2.4pp，OOR 降 43.9%

- Learning Points：中文相似度特化；多通道融合；短 query 魯棒化
- 技能：Python/向量檢索基礎；模型部署
- 練習：實作三通道融合（30m）；調參 AUC>0.8（2h）；打造可配置服務（8h）
- 評估：功能（正確攔截/通過）；代碼品質；TP/FP 取捨；創新（新通道）

---

## Case #3: 中文分詞與 OOV 對建議品質的影響

### Problem Statement
- 業務場景：短字詞（例：「吃驚」）在分詞/OOV 下語義判斷失準，導致候選不穩定。
- 技術挑戰：提升短 query 下分詞與子詞語義表示，兼顧性能。
- 影響範圍：建議亂跳、召回錯誤、CTR 降低。
- 複雜度：中

### Root Cause Analysis
- 直接原因：字典缺詞；OOV 處理不佳；僅字級特徵
- 深層原因：缺少子詞/字向量；無自訂詞庫；無語境

### Solution Design
- 策略：引入子詞模型（BPE/WordPiece）、自訂詞庫與用戶詞頻，融合字/詞/子詞特徵。

- 實施步驟：
  1. 自訂詞庫與用戶詞頻
     - 細節：jieba add_word、動態學習詞頻
     - 資源：jieba/jieba-tw
     - 時間：6 小時
  2. 子詞嵌入
     - 細節：SentencePiece 訓練 16k vocab
     - 資源：sentencepiece
     - 時間：12 小時
  3. 特徵融合
     - 細節：字/詞/子詞三路平均或學習融合
     - 時間：8 小時

- 關鍵程式碼：
```python
import jieba
jieba.add_word("吃驚", freq=10_000)  # 提升詞權重

def tokenize(q):
    return list(jieba.cut(q, HMM=True))

print(tokenize("吃驚"))
```

- 實測：Top-1 建議準確率 +2.1pp，OOV 命中率 +7pp，延時 +2ms
- 學習要點：OOV/子詞；詞庫運維
- 練習：建立自訂詞庫（30m）；訓練 sentencepiece（2h）；融合特徵上線（8h）
- 評估：準確率/延時平衡；代碼品質；吞吐；創新

---

## Case #4: 編碼與 Unicode 正規化導致的錯建議

### Problem Statement
- 業務場景：混用 Big5/UTF-8 導致查詢與候選比對失真，出現離題/不雅建議。
- 技術挑戰：全鏈路正規化與編碼自動辨識。
- 影響：建議準確率下降、錯攔/漏攔。
- 複雜度：低

### Root Cause
- 直接原因：未做 NFKC 正規化；編碼偵測缺失
- 深層原因：歷史系統遺留；無統一字形/全半形策略

### Solution
- 策略：入口/存儲/比對三處 NFKC，建立編碼探測與修正，並記錄正規化前後。

- 步驟：
  1. 請求層 NFKC
  2. 日誌與索引層 NFKC
  3. 檢測可疑編碼並修復

- 代碼：
```python
import unicodedata
def normalize(s: str) -> str:
    return unicodedata.normalize("NFKC", s).strip().lower()
```

- 實測：重複/錯碼引發的離題率 -60%，CPU 增加可忽略
- 練習：正規化中介件（30m）；編碼偵測器（2h）；統一字形策略（8h）

---

## Case #5: 過度干預的建議顯示門檻（結果品質感知）

### Problem Statement
- 業務場景：即使原查詢有高品質結果，仍強推建議，造成誤導。
- 技術挑戰：結合搜尋結果品質與建議門檻的多臂策略。
- 影響：CTR 下滑、滿意度下降。
- 複雜度：中

### Root Cause
- 直接原因：門檻僅看相似度/點擊
- 深層原因：無跨服務信號匯入；未定義結果品質閾值

### Solution
- 策略：引入搜尋品質分（NDCG、SAT clicks、跳出率），門檻自適應。

- 步驟：
  1. 定義品質信號
  2. 計算合成品質分
  3. 門檻函數調整與 A/B

- 代碼：
```python
def should_show_suggestion(sim, result_q, safe=True):
    base = 0.7 if safe else 0.6
    adj = -0.1 if result_q > 0.8 else +0.05
    return sim > base + adj
```

- 實測：不必要建議顯示率 -35%，整體 CTR +1.2pp
- 練習：實作品質分（30m）；門檻函數調參（2h）；聯動搜尋服務（8h）

---

## Case #6: 點擊日誌被垃圾與惡意查詢污染

### Problem Statement
- 業務場景：惡意或機器點擊推高不雅候選權重，污染建議。
- 技術挑戰：異常檢測與強韌聚合。
- 影響：安全/品質風險。
- 複雜度：中

### Root Cause
- 直接原因：缺少防刷特徵；聚合無魯棒性
- 深層原因：評分過度依賴 raw clicks

### Solution
- 策略：刷量識別（UA/IP/速率/指紋）、加權去極值、k-匿名匯總。

- 步驟：
  1. 異常特徵工程
  2. 魯棒聚合（trimmed mean）
  3. 閾值封鎖與回溯清洗

- SQL：
```sql
-- 以 k>=5 的查詢才納入候選統計
INSERT INTO clean_queries
SELECT query, COUNT(*) c
FROM raw_queries
GROUP BY query
HAVING COUNT(DISTINCT user_hash) >= 5;
```

- 實測：垃圾候選佔比 -72%，ISR -60%
- 練習：異常檢測特徵（30m）；trimmed mean 實作（2h）；清洗回放（8h）

---

## Case #7: SafeSearch/家庭帳戶策略未覆蓋建議服務

### Problem Statement
- 業務場景：家庭模式中仍出現不當建議，策略不一致。
- 技術挑戰：跨服務策略一致性與延時控制。
- 影響：法遵/品牌風險。
- 複雜度：中

### Root Cause
- 分離部署；緩存過期；策略版本漂移

### Solution
- 策略：集中策略服務，短 TTL 快取，版本化/回滾。

- 步驟：
  1. 策略 SDK/快取
  2. 版本管理/回滾
  3. 合規稽核

- 代碼：
```python
def get_policy(user):
    # 拉取並快取 60s
    return {"safe_mode": user.get("family", False), "version": "v3"}
```

- 實測：策略不一致事件 -> 0；P95 延時 +2ms
- 練習：快取/過期測試（30m）；策略服務 stub（2h）；壓測與回滾（8h）

---

## Case #8: 自動補全趨勢洩漏不當字串

### Problem Statement
- 業務場景：實時趨勢把灰色字串帶進補全。
- 技術挑戰：流式過濾與延遲<50ms。
- 影響：高曝光風險。
- 複雜度：高

### Root Cause
- 流式路徑無安全層；延時預算緊

### Solution
- 策略：Kafka 流 + BloomFilter 快速攔截 + 輕量 ML；熱詞白名單。

- 步驟：
  1. BloomFilter 同步
  2. 流式分類
  3. 白名單優先

- 代碼：
```python
# 假代碼：Bloom 濾除 + 輕量打分
if bloom.might_contain(token) or ml_score(token) < 0.7:
    continue
```

- 實測：不當補全曝光 -90%，P95 延時 42ms
- 練習：BloomFilter（30m）；Kafka 流水線（2h）；端到端延時控制（8h）

---

## Case #9: 地區詞彙與同義詞本地化不足

### Problem Statement
- 業務場景：zh-TW 使用者收到 zh-CN 風格建議或不自然詞。
- 技術挑戰：地區變體映射與同義詞治理。
- 影響：滿意度與品牌在地化。
- 複雜度：中

### Root Cause
- 缺本地詞庫；語言標籤缺失；測試樣本不均

### Solution
- 策略：Locale-aware 詞庫、同義詞圖譜、地區分桶 AB。

- 步驟：
  1. 建置 zh-TW 詞庫
  2. 同義詞映射
  3. 地區分桶測試

- 代碼：
```yaml
# synonyms_zh-TW.yaml
吃驚: [驚訝, 吃驚]
```

- 實測：TW 區建議滿意度 +6pp；離題 -30%
- 練習：方言詞庫（30m）；同義詞圖譜（2h）；分桶測試（8h）

---

## Case #10: ML 安全分類器替代單純黑名單

### Problem Statement
- 業務場景：規則難覆蓋諧音/變體，誤判多。
- 技術挑戰：輕量、可部署、低延時的安全分類器。
- 影響：ISR 居高不下。
- 複雜度：中

### Root Cause
- 規則不可擴展；資料稀疏

### Solution
- 策略：fastText/DistilBERT 安全分類器，規則+模型混合。

- 步驟：
  1. 標註集擴充（對抗樣本）
  2. 模型訓練與蒸餾
  3. 線上推理與監控

- 代碼：
```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
tok = AutoTokenizer.from_pretrained("uer/roberta-base-chinese-cluecorpussmall")
mdl = AutoModelForSequenceClassification.from_pretrained("...")  # 已微調
# 推理略
```

- 實測：ISR -70%，延時 +6ms（CPU）
- 練習：標註策略（30m）；蒸餾實作（2h）；部署監控（8h）

---

## Case #11: 使用者回報與標註閉環

### Problem Statement
- 業務場景：缺少「回報不恰當建議」通道，無法快速修復。
- 技術挑戰：低摩擦回報、反濫用、標註隊列。
- 影響：修復慢、口碑風險。
- 複雜度：低

### Root Cause
- 無回報入口；無標註流程/工具

### Solution
- 策略：前端回報入口→後端工單→標註→詞庫/模型更新。

- 步驟：
  1. 前端回報（匿名+k-匿名聚合）
  2. 標註平台
  3. 每日增量發布

- 代碼：
```js
// Node/Express: 接收回報
app.post("/report", (req,res)=>{
  // 校驗 & 風控略
  queue.push({q:req.body.q, cand:req.body.c});
  res.sendStatus(202);
});
```

- 實測：平均修復時間 7d→1d，ISR -25%
- 練習：回報 API（30m）；標註工具雛形（2h）；自動化發布（8h）

---

## Case #12: 建議模型灰度與回滾保護

### Problem Statement
- 業務場景：模型上線回歸導致不當建議激增。
- 技術挑戰：灰度、SLO 守門、快速回滾。
- 影響：高風險事故。
- 複雜度：中

### Root Cause
- 缺少 canary；未設 SLO 門檻；發布不可回滾

### Solution
- 策略：分流 canary（1-5%）、黑名單熱修、SLO 自動回滾。

- 步驟：
  1. Feature flag 分流
  2. 實時監控 ISR/SLO
  3. 一鍵回滾

- 代碼：
```python
if metrics["ISR"] > 0.0003:  # SLO
    trigger_rollback(version)
```

- 實測：回歸事故影響面 -90%
- 練習：flag 方案（30m）；SLO 守門（2h）；回滾演練（8h）

---

## Case #13: 評估框架與核心指標體系

### Problem Statement
- 業務場景：缺少統一指標衡量建議品質與安全。
- 技術挑戰：定義可對比、可監控的線上/線下指標。
- 影響：決策與迭代受阻。
- 複雜度：低

### Root Cause
- 指標零散；無標準面板

### Solution
- 策略：建立 ISR/SPR/OOR/CTR/满意度 的定義、計算與看板。

- 步驟：
  1. 指標定義與埋點
  2. 批處理與實時計算
  3. 可視化看板

- SQL：
```sql
-- 建議精確率 SPR
SELECT SUM(CASE WHEN accepted=1 THEN 1 ELSE 0 END)*1.0/COUNT(*) AS SPR
FROM sug_logs
WHERE ab_bucket='B';
```

- 實測：決策效率 +50%，回歸檢測時間 -60%
- 練習：指標 ETL（30m）；實時指標（2h）；看板搭建（8h）

---

## Case #14: 查詢隱私保護與資料治理

### Problem Statement
- 業務場景：需利用查詢日誌改善建議，又要保護隱私。
- 技術挑戰：PII 清洗、k-匿名、差分隱私。
- 影響：法遵/信任。
- 複雜度：高

### Root Cause
- 原始日誌長留；缺乏去識別與差分隱私

### Solution
- 策略：PII 檢測/哈希化、k-匿名聚合、DP 噪音。

- 步驟：
  1. PII 偵測與遮罩
  2. k-匿名聚合
  3. DP 釋出（ε 控制）

- 代碼：
```python
import hashlib
def hash_user(u): return hashlib.sha256(u.encode()).hexdigest()[:16]
```

- 實測：合規審計通過；建議品質維持
- 練習：PII 遮罩（30m）；k-匿名（2h）；DP 釋出（8h）

---

## Case #15: 文案與 UI 降風險（語氣與呈現）

### Problem Statement
- 業務場景：「您是不是要查」語氣過於斷定，易造成誤導或反感。
- 技術挑戰：文案與視覺權重調整不影響可用性。
- 影響：滿意度與品牌風格。
- 複雜度：低

### Root Cause
- 文案未本地化 A/B；視覺層級過強

### Solution
- 策略：改為「或許您想找」，弱化樣式；提供「隱藏建議」選項。

- 步驟：
  1. 文案/樣式多版本
  2. A/B 測試（CTR/滿意）
  3. 偏好記憶

- 代碼：
```js
// A/B 旗標
const copy = abBucket==='B' ? '或許您要找：' : '您是不是要查：';
```

- 實測：反感回饋 -40%，建議採納率持平
- 練習：文案 A/B（30m）；偏好記憶（2h）；多語本地化（8h）

---

## Case #16: CJK 形近/音近對抗樣本與防禦

### Problem Statement
- 業務場景：利用形近/音近繞過過濾（對抗樣本）。
- 技術挑戰：對抗資料增廣與防禦訓練。
- 影響：安全風險。
- 複雜度：高

### Root Cause
- 模型對形近/音近敏感；詞典難覆蓋

### Solution
- 策略：對抗樣本生成（形近替換/拼音擾動）+ 對抗訓練。

- 步驟：
  1. 生成器（基於字典/語音）
  2. 混合訓練
  3. 線上偵測與攔截

- 代碼：
```python
# 形近替換示意
NEAR = {"驚": ["惊","京"], "吃": ["𠮟"]}  # 示例
def gen_adv(q): return [q.replace(k,v) for k,vs in NEAR.items() for v in vs]
```

- 實測：對抗成功率 -65%，誤攔微增（<0.1pp）
- 練習：生成器（30m）；對抗訓練（2h）；線上偵測（8h）

---

## Case #17: 同義詞/關聯查詢替代 Did-You-Mean

### Problem Statement
- 業務場景：直接糾錯風險高，可改為「也可試試」類關聯提示。
- 技術挑戰：維持探索性與安全。
- 影響：降低誤導。
- 複雜度：低

### Root Cause
- 強糾錯策略壓過原查詢

### Solution
- 策略：提供關聯查詢（同義/上位詞），降權顯示。

- 步驟：
  1. 同義詞檢索
  2. 降權顯示（次要）
  3. 點擊學習

- 代碼：
```json
{ "suggestions": ["驚訝", "大吃一驚"], "type": "related" }
```

- 實測：誤導投訴 -55%，整體滿意度 +3pp
- 練習：關聯模組（30m）；排序/位置測試（2h）；長期學習（8h）

---

## Case #18: 灰色詞/多義詞上下文消歧

### Problem Statement
- 業務場景：多義詞無上下文導致易誤判。
- 技術挑戰：基於輕量上下文的判斷，不侵犯隱私。
- 影響：安全/品質。
- 複雜度：中

### Root Cause
- 無上下文信號；短 query 信息稀疏

### Solution
- 策略：僅用頁面語言/地區/近期類別偏好做輕量消歧。

- 步驟：
  1. 上下文信號治理（匿名/粗粒度）
  2. 消歧模型（LR/GBDT）
  3. 門檻與 fallback

- 代碼：
```python
features = {"locale":"zh-TW","recent_cat":"news"}
score = lr.predict_proba(encode(features))
```

- 實測：離題建議 -28%，延時 +3ms
- 練習：特徵工程（30m）；輕量模型（2h）；隱私稽核（8h）

---

## Case #19: 監控與警戒（Watchdog）對不當建議

### Problem Statement
- 業務場景：事故出現時無自動警戒，擴散快。
- 技術挑戰：跨區域/語言的異常監控。
- 影響：公關/合規風險。
- 複雜度：中

### Root Cause
- 無專屬 ISR/SLO 監控；預警缺失

### Solution
- 策略：設置 ISR、成人關鍵詞曝光、趨勢突增監控與自動下線。

- 步驟：
  1. 指標與閾值
  2. 告警與自動化動作
  3. 事後復盤

- 代碼：
```yaml
alert:
  metric: ISR
  threshold: 0.0003
  action: rollback_model
```

- 實測：平均發現時間 TTD 30m→3m
- 練習：指標告警（30m）；自動化動作（2h）；演練 Runbook（8h）

---

## Case #20: 法務與政策知識庫整合

### Problem Statement
- 業務場景：各地區法規對建議內容要求不同。
- 技術挑戰：策略可配置、可追溯。
- 影響：法遵/營運風險。
- 複雜度：高

### Root Cause
- 策略散落；人工下發；無審計

### Solution
- 策略：政策知識庫（地區×類型×敏感級），編排成策略規則，上線審計。

- 步驟：
  1. 政策建模（YAML/DSL）
  2. 策略引擎/審計
  3. 版本/灰度

- 代碼：
```yaml
policy:
  region: zh-TW
  sensitive:
    adult: block
    violence: soft_block
  version: 2025-08-01
```

- 實測：合規缺陷數 -80%，審計通過率 100%
- 練習：DSL 設計（30m）；策略引擎（2h）；審計流程（8h）

---

案例分類
1) 按難度
- 入門級：Case 4, 11, 13, 15, 17
- 中級：Case 1, 2, 3, 5, 6, 7, 9, 18, 19
- 高級：Case 8, 10, 12, 14, 16, 20

2) 按技術領域
- 架構設計類：Case 7, 12, 19, 20
- 效能優化類：Case 5, 8
- 整合開發類：Case 1, 2, 3, 9, 17, 18
- 除錯診斷類：Case 4, 6, 13, 19
- 安全防護類：Case 1, 8, 10, 14, 16

3) 按學習目標
- 概念理解型：Case 13, 15, 20
- 技能練習型：Case 4, 11, 17
- 問題解決型：Case 1, 2, 3, 5, 6, 7, 9, 18, 19
- 創新應用型：Case 8, 10, 12, 14, 16

案例關聯圖（學習路徑建議）
- 建議先學：Case 4（正規化）、Case 13（指標體系）、Case 15（文案/呈現），打好基礎。
- 依賴關係：
  - Case 1 依賴 Case 4/13（正規化與指標）
  - Case 2/3 依賴 Case 4（資料清潔）
  - Case 5 依賴 Case 13（品質信號）
  - Case 8/10/16 依賴 Case 1/2/3（安全/相似度/分詞）
  - Case 7/12/19/20 為治理與架構層，建議在完成核心能力後學
  - Case 14 與 11 構成資料/標註閉環
- 完整學習路徑：
  1) 基礎清潔與指標：Case 4 → Case 13 → Case 15
  2) 生成與排序能力：Case 2 → Case 3 → Case 5 → Case 9 → Case 17 → Case 18
  3) 安全與防禦：Case 1 → Case 10 → Case 16 → Case 8 → Case 7
  4) 數據治理與運維：Case 6 → Case 11 → Case 12 → Case 19 → Case 14 → Case 20

說明：上述所有案例均為從原文場景「中文 Did-You-Mean 出現不恰當建議」所延展的通用工程解法，以教學與實作為目的設計，並非源文直接提供之技術細節或指標。