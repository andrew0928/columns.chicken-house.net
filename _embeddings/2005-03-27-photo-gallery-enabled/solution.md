以下整理說明：原文僅明確指出「現有 Photo Gallery 只能逐張上傳，面對大量照片時操作成本過高，因此作者自建了簡單的批次上傳工具」。為滿足實戰教學、專案練習與評估的需求，以下案例從該核心痛點出發，拆解為 16 個可落地的典型問題—解決方案。除「原文提及」之外的流程、程式碼與數據為通用實務化設計與教學用測試數據（非原文測得），用於訓練與評估。

## Case #1: 批次上傳 MVP：從逐張上傳到資料夾上傳

### Problem Statement（問題陳述）
業務場景：個人/團隊需分享數百至上千張活動照片，原使用的 Gallery 僅支援逐張上傳，導致每次整理與上傳耗費大量時間，人員常因流程冗長而中途放棄，最終影響內容產出與社群互動。
技術挑戰：提供可靠的批次上傳介面（UI/CLI/API），支援多檔案並行與中斷保護，同時保留必要的照片中繼資料（EXIF/檔名/路徑）與相簿分類。
影響範圍：內容更新頻率降低、上傳錯誤率偏高、營運成本上升、用戶體驗不佳。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Gallery 無批次上傳介面：只能逐張手動上傳，操作時間線性累積。
2. 上傳處理同步阻塞：縮圖/寫檔在請求內完成，導致逾時與效能差。
3. 無 CLI 自動化：缺乏能掃描資料夾並批次上傳的工具。

深層原因：
- 架構層面：未採用非同步工作隊列與暫存機制，耦合導致脆弱。
- 技術層面：未提供 REST/批次 API；缺乏並行與重試友善設計。
- 流程層面：依賴人工操作，無法標準化/自動化。

### Solution Design（解決方案設計）
解決策略：建立批次上傳 API（支援多檔案），後端僅落地暫存並排入工作隊列；前端提供拖放批上傳，另提供 Python CLI 掃描資料夾並限速並行上傳；後台工作者非同步產生縮圖與寫入媒體存儲。

實施步驟：
1. 定義批次上傳 API
- 實作細節：Express + Multer 接收多檔案，存至暫存區，回傳批次任務 ID
- 所需資源：Node.js 18, Express, Multer, MongoDB
- 預估時間：0.5~1 天

2. 建立工作隊列與縮圖處理
- 實作細節：BullMQ + Sharp，非同步生成多尺寸縮圖並寫入 S3/本地
- 所需資源：Redis, Sharp, BullMQ, S3/MinIO
- 預估時間：1 天

3. 開發 CLI 工具
- 實作細節：Python requests + concurrent.futures，支援資料夾掃描、多執行緒與失敗重試
- 所需資源：Python 3.11, requests
- 預估時間：0.5 天

關鍵程式碼/設定：
```js
// server.js (Node.js/Express)
import express from 'express';
import multer from 'multer';
import { Queue } from 'bullmq';
import crypto from 'crypto';

const upload = multer({ dest: '/tmp/uploads' });
const app = express();
const q = new Queue('photo-jobs', { connection: { host: 'localhost', port: 6379 } });

app.post('/api/batch-upload', upload.array('files', 100), async (req, res) => {
  const batchId = crypto.randomUUID();
  const jobs = req.files.map(f => ({
    name: 'process-photo',
    data: { batchId, tmpPath: f.path, originalName: f.originalname }
  }));
  await q.addBulk(jobs);
  res.json({ batchId, count: req.files.length });
});

app.listen(3000);
```

```py
# uploader.py (Python CLI)
import os, sys, concurrent.futures, requests
URL = 'http://localhost:3000/api/batch-upload'
def upload_files(files):
    with requests.Session() as s:
        m = [('files', (os.path.basename(p), open(p, 'rb'))) for p in files]
        r = s.post(URL, files=m, timeout=120)
        r.raise_for_status()
        return r.json()

if __name__ == '__main__':
    folder = sys.argv[1]
    files = [os.path.join(folder, f) for f in os.listdir(folder)]
    # 分批上傳，避免單次 multipart 過大
    size = 50
    for i in range(0, len(files), size):
        print(upload_files(files[i:i+size]))
```

實際案例：原文提及：已有大量照片，逐張上傳成本過高，作者自建簡單批次上傳工具；本案例將其落實為 API + CLI + 工作隊列架構。
實作環境：Node.js 18、Express、Multer、Redis 7、BullMQ、Sharp、MongoDB、MinIO（S3 相容）
實測數據：
改善前：500 張手動上傳約 90 分鐘（含縮圖處理與人工分類）
改善後：500 張經 CLI 批次上傳與後台處理約 14 分鐘完成
改善幅度：約 6.4 倍（以實驗網路 100 Mbps 為基準）

Learning Points（學習要點）
核心知識點：
- 批次 API 設計與多檔案處理
- 前後台非同步解耦（上傳與處理分離）
- CLI 自動化與並行控制

技能要求：
- 必備技能：HTTP 基礎、Node.js/Express、Python requests
- 進階技能：工作隊列、雲端物件儲存、非同步架構

延伸思考：
- 如何支援斷點續傳與重試安全？
- 大檔案/大量小檔案的最優批次大小如何選擇？
- 如何與現有 Gallery 資料模型對接？

Practice Exercise（練習題）
- 基礎練習：將 API 的檔案數量限制調整為 200，並驗證返回資訊（30 分鐘）
- 進階練習：為 CLI 增加重試與並行度參數（2 小時）
- 專案練習：將縮圖產生改為三種尺寸並寫 S3，提供查詢批次處理狀態 API（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：可批次上傳、任務建立、處理完成回報
- 程式碼品質（30%）：錯誤處理、結構清晰、可測試性
- 效能優化（20%）：並行與批次大小合理、避免阻塞
- 創新性（10%）：有額外進度顯示或自動分類能力

---

## Case #2: 斷點續傳與分片上傳（Chunked/Resumable Upload）

### Problem Statement（問題陳述）
業務場景：外勤或旅遊場景網路不穩，批次上傳中常中斷，重新上傳耗時，且易導致重複檔與資料不一致，影響使用者信心與效率。
技術挑戰：可靠的分片上傳、續傳、合併與重試機制，且需控制服務端資源占用與確保資料完整性。
影響範圍：中斷導致的失敗率、用戶重試成本、服務端重複寫入與儲存浪費。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 單請求大檔上傳易逾時：網路抖動造成連線中斷。
2. 無續傳協議：中斷後只能重來，造成浪費。
3. 缺乏分片完整性校驗：重組風險高。

深層原因：
- 架構層面：未定義上傳會話（upload session）與狀態管理。
- 技術層面：缺乏 Content-Range/ETag 等校驗流程。
- 流程層面：無重試與冪等策略。

### Solution Design（解決方案設計）
解決策略：導入上傳會話，客戶端將檔案切片上傳；服務端記錄已收片段與校驗，允許隨時續傳未完成片段；所有片段上傳完成後進行合併並觸發後續處理。

實施步驟：
1. 上傳會話管理
- 實作細節：POST /upload/sessions 建立 sessionId，記錄檔名/大小/片大小
- 所需資源：MongoDB/Redis
- 預估時間：0.5 天

2. 分片上傳與校驗
- 實作細節：PUT /upload/sessions/:id/chunks，Header 帶 Content-Range 與 SHA256
- 所需資源：Express、中介軟體、雜湊函式庫
- 預估時間：1 天

3. 合併與完成回報
- 實作細節：當所有 chunk 到齊，合併檔案並產生工作隊列任務
- 所需資源：Node.js 檔案串流、BullMQ
- 預估時間：0.5 天

關鍵程式碼/設定：
```js
// resumable.js (Node)
app.post('/upload/sessions', async (req, res) => {
  const session = { id: crypto.randomUUID(), size: req.body.size, chunkSize: req.body.chunkSize, received: {} };
  await db.sessions.insertOne(session);
  res.json(session);
});

app.put('/upload/sessions/:id/chunks', async (req, res) => {
  const range = req.headers['content-range']; // bytes start-end/total
  const [start, end] = range.match(/bytes (\d+)-(\d+)\//).slice(1).map(Number);
  const session = await db.sessions.findOne({ id: req.params.id });
  const tmp = fs.createWriteStream(`/tmp/${session.id}-${start}`, { flags: 'w' });
  req.pipe(tmp).on('finish', async () => {
    await db.sessions.updateOne({ id: session.id }, { $set: { [`received.${start}`]: true } });
    res.json({ ok: true });
  });
});

app.post('/upload/sessions/:id/complete', async (req, res) => {
  const s = await db.sessions.findOne({ id: req.params.id });
  // 檢查所有 chunk 是否齊
  // 合併檔案省略細節
  res.json({ ok: true });
});
```

實際案例：原文指出需批次上傳；此案例針對不穩網路時的可靠性延伸。
實作環境：Node.js 18、MongoDB、Redis、BullMQ
實測數據：
改善前：遇 5% 網路中斷重傳整檔，500 張共重傳 25 張，額外耗時 ~20 分鐘
改善後：僅續傳缺片段，額外耗時 ~4 分鐘
改善幅度：約 5 倍節省中斷重試成本

Learning Points：
- 續傳協議與會話狀態管理
- Content-Range、校驗與合併
- 與後台處理的解耦

技能要求：
- 必備：HTTP/Range、檔案串流
- 進階：冪等與一致性設計

延伸思考：
- 如何用 tus 協議或 S3 Multipart 提升標準化？
- 合併過程如何零拷貝以降 I/O？
- 續傳資訊如何安全儲存？

Practice Exercise：
- 基礎：為 chunk 上傳加入 SHA256 校驗（30 分）
- 進階：支援查詢缺片段清單與續傳（2 小時）
- 專案：包裝 Python/JS 客戶端 SDK（8 小時）

Assessment Criteria：
- 功能完整性（40%）：可續傳、可查詢狀態
- 程式碼品質（30%）：嚴謹校驗、邊界處理
- 效能優化（20%）：合併與 I/O 最小化
- 創新性（10%）：協議化/標準化實作

---

## Case #3: 後台縮圖與非同步處理，避免請求逾時

### Problem Statement（問題陳述）
業務場景：批次上傳時每張照片需要產生多種尺寸縮圖，若在請求流程同步處理，容易逾時與失敗，並拖垮伺服器資源。
技術挑戰：建立可靠的工作隊列、可水平擴充的影像處理器、失敗重試與監控。
影響範圍：上傳成功率、用戶等待時間、服務穩定度。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 縮圖在請求中同步完成：導致逾時。
2. 多尺寸輸出 CPU/IO 密集：資源競爭。
3. 無重試/排程：偶發錯誤無法自癒。

深層原因：
- 架構層面：缺乏任務隊列與工作者角色。
- 技術層面：未使用高效影像庫、未採並行策略。
- 流程層面：無監控/告警，問題晚被發現。

### Solution Design（解決方案設計）
解決策略：前端/CLI 僅提交檔案與建立任務；後台工作者（多實例）使用 Sharp 產生縮圖，任務狀態落庫，支援重試與死信佇列；以儀表板監控吞吐與失敗率。

實施步驟：
1. 建立任務隊列與 worker
- 實作細節：BullMQ Worker 消費任務，使用 Sharp 產生 3 種尺寸
- 所需資源：Redis, Sharp
- 預估時間：0.5 天

2. 任務狀態與重試策略
- 實作細節：maxAttempts=3、指數退避、死信佇列
- 所需資源：BullMQ options
- 預估時間：0.5 天

3. 監控與調校
- 實作細節：Prometheus 指標與儀表板，觀察每秒處理量與失敗率
- 所需資源：prom-client, Grafana
- 預估時間：0.5 天

關鍵程式碼/設定：
```js
// worker.js
import { Worker } from 'bullmq';
import sharp from 'sharp';
new Worker('photo-jobs', async job => {
  const { tmpPath, originalName } = job.data;
  const base = `/data/photos/${job.id}`;
  await sharp(tmpPath).resize(2048).toFile(`${base}-xl.jpg`);
  await sharp(tmpPath).resize(1280).toFile(`${base}-md.jpg`);
  await sharp(tmpPath).resize(320).toFile(`${base}-sm.jpg`);
}, {
  connection: { host: 'localhost', port: 6379' },
  concurrency: 4
});
```

實際案例：原文目標是批次上傳可用；此為確保穩定與可擴展之關鍵。
實作環境：Node.js、Redis、Sharp、Prometheus
實測數據：
改善前：同步處理 500 張，失敗率 7%，平均完成 65 分鐘
改善後：非同步處理並擴 2 個 worker，失敗率 <1%，完成 18 分鐘
改善幅度：時間縮短 ~2.6 倍，失敗率降低 7 倍

Learning Points：
- 非同步任務與失敗重試
- 影像處理並行與資源控制
- 監控與調校

技能要求：
- 必備：Node.js、佇列基礎
- 進階：SLA/SLI 指標化

延伸思考：
- 如何根據 CPU 核心動態調整 concurrency？
- 死信佇列如何自動修復？
- 圖像處理能否改為 serverless？

Practice：
- 基礎：加入 maxAttempts 與退避策略（30 分）
- 進階：導入處理時間指標與告警（2 小時）
- 專案：加上 Webhook 回報處理完成（8 小時）

Assessment：
- 功能（40%）：穩定處理與回報
- 品質（30%）：重試/錯誤處理完善
- 效能（20%）：吞吐提升
- 創新（10%）：自動化調參

---

## Case #4: EXIF 方向與自動旋轉

### Problem Statement（問題陳述）
業務場景：手機/相機拍攝的照片常有 EXIF Orientation，若不處理，畫面顯示旋轉錯誤，影響展示體驗與人工修正成本。
技術挑戰：正確讀取 EXIF 並在縮圖/顯示時自動旋轉與寫回標準化輸出。
影響範圍：用戶體驗、內容品質、人工後製成本。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 未處理 EXIF Orientation：顯示錯向。
2. 縮圖時忽略旋轉：產出不一致。
3. 顯示端不統一：某些瀏覽器不讀 EXIF。

深層原因：
- 架構層面：缺乏標準化影像流程。
- 技術層面：未使用支援 EXIF 的影像庫。
- 流程層面：無自動驗證步驟。

### Solution Design（解決方案設計）
解決策略：在後台處理階段統一 read metadata 並 rotate，再輸出各尺寸；或將 EXIF 去除並以正確方向輸出，確保前端一致顯示。

實施步驟：
1. 讀取與旋轉
- 實作細節：Sharp 的 rotate() 自動依 EXIF 旋轉
- 所需資源：Sharp
- 預估時間：0.25 天

2. 移除 EXIF（選擇）
- 實作細節：toFormat 與 withMetadata 控制
- 所需資源：Sharp
- 預估時間：0.25 天

關鍵程式碼/設定：
```js
import sharp from 'sharp';
await sharp(tmpPath)
  .rotate() // 根據 EXIF 自動旋轉
  .resize(1280)
  .withMetadata({ orientation: 1 }) // 可選：標準化
  .toFile(outPath);
```

實際案例：照片方向顯示錯誤是批次導入常見問題。
實作環境：Sharp
實測數據：
改善前：500 張中約 18% 顯示錯向，人工修正 1~2 秒/張
改善後：自動旋轉 100% 修正
改善幅度：節省 ~150 秒以上/500 張

Learning Points：
- EXIF 與影像處理
- 標準化輸出
- 前後端一致性

技能要求：
- 必備：影像處理基礎
- 進階：EXIF 欄位理解

延伸思考：
- GPS/時間等 metadata 如何保留/匿名化？
- RAW 檔處理策略？
- WebP/AVIF 格式是否保留 EXIF？

Practice：
- 基礎：加入 auto-rotate（30 分）
- 進階：提供保留/移除 EXIF 的選項（2 小時）
- 專案：寫批次檢查器，報告錯向比例（8 小時）

Assessment：
- 功能（40%）：方向正確
- 品質（30%）：程式結構與測試
- 效能（20%）：處理時間可控
- 創新（10%）：自動報告/可視化

---

## Case #5: 重複照片檢測（內容與檔案層級）

### Problem Statement（問題陳述）
業務場景：大量照片中常出現重複或相近照片，若重複上傳將浪費儲存與造成相簿雜訊，降低瀏覽體驗。
技術挑戰：快速判斷重複（byte-level）與近似（perceptual-level）照片，並在上傳流程中即時攔截或提示合併。
影響範圍：儲存成本、索引效率、使用者體驗。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 無檔案雜湊：難以偵測完全相同檔案。
2. 無感知雜湊：相近照片無法辨別。
3. 上傳流程缺乏去重節點：事後清理成本高。

深層原因：
- 架構層面：無去重策略與資料模型欄位。
- 技術層面：缺雜湊存放與索引。
- 流程層面：無人機審核/自動合併規則。

### Solution Design（解決方案設計）
解決策略：上傳時計算 SHA-256 判斷檔案重複；背景計算 pHash（感知雜湊）找近似，提供管理介面合併或標記。

實施步驟：
1. 檔案雜湊與攔截
- 實作細節：計算 SHA-256，DB 以雜湊做唯一索引
- 所需資源：Node crypto, Mongo 索引
- 預估時間：0.5 天

2. 感知雜湊與相似查詢
- 實作細節：使用 imghash/pHash，設定距離閾值
- 所需資源：image-hash 套件
- 預估時間：1 天

關鍵程式碼/設定：
```js
import crypto from 'crypto';
function sha256File(path) {
  const hash = crypto.createHash('sha256');
  return new Promise(res => fs.createReadStream(path).on('data', d => hash.update(d)).on('end', () => res(hash.digest('hex'))));
}
// MongoDB: 建立唯一索引 db.photos.createIndex({ sha256: 1 }, { unique: true })
```

實際案例：批次上傳大量照片時最常見的冗餘問題。
實作環境：Node.js、MongoDB、image-hash
實測數據：
改善前：重複率約 6%，儲存浪費顯著
改善後：完全重複攔截 100%，近似建議 70% 命中（pHash 距離閾值 10）
改善幅度：儲存節省 6%+，清理成本大幅降低

Learning Points：
- 雜湊與唯一索引
- 感知雜湊與距離
- 去重策略與介面

技能要求：
- 必備：雜湊/索引
- 進階：相似度演算法

延伸思考：
- 視頻/連拍如何處理？
- 近似閾值如何 A/B 校準？
- 去重與權限的交互？

Practice：
- 基礎：加上 SHA-256 去重（30 分）
- 進階：導入 pHash 與相似查詢（2 小時）
- 專案：管理 UI 合併與忽略機制（8 小時）

Assessment：
- 功能（40%）：準確攔截
- 品質（30%）：可維護性
- 效能（20%）：計算與索引效率
- 創新（10%）：相似度調優工具

---

## Case #6: 依 EXIF 日期與地點自動建立相簿

### Problem Statement（問題陳述）
業務場景：每次活動後需快速按日期/地點分相簿，手動分類耗時且易誤；自動化能大幅提升整理效率。
技術挑戰：穩定抽取 EXIF 日期、GPS，處理缺失/異常與時區，並建立相簿規則。
影響範圍：整理效率、相簿一致性、瀏覽體驗。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 手動分類耗時：易錯且難規模化。
2. EXIF 抽取缺乏：資料不可用。
3. 無規則引擎：無法自動歸檔。

深層原因：
- 架構層面：無 metadata pipeline。
- 技術層面：時區/格式差異處理不足。
- 流程層面：缺少自動化規範。

### Solution Design（解決方案設計）
解決策略：工作者抽取 EXIF（拍攝日期/位置），應用規則（如同日同地），自動建立相簿與關聯照片；缺失則回退至檔名/上傳時間。

實施步驟：
1. EXIF 抽取
- 實作細節：exifr 套件讀取，寫入 DB
- 所需資源：exifr, MongoDB
- 預估時間：0.5 天

2. 規則歸檔
- 實作細節：日期聚簇 + GPS 距離閾值（例如 500m）
- 所需資源：geolib
- 預估時間：1 天

關鍵程式碼/設定：
```js
import exifr from 'exifr';
const meta = await exifr.parse(tmpPath);
const taken = meta?.DateTimeOriginal || meta?.CreateDate;
const gps = meta?.latitude && meta?.longitude ? { lat: meta.latitude, lon: meta.longitude } : null;
// 根據規則建立/關聯相簿
```

實際案例：批次工具常見增值功能，降低後續整理成本。
實作環境：Node.js、exifr、MongoDB
實測數據：
改善前：500 張手動分相簿 ~30 分鐘
改善後：自動分相簿 <2 分鐘，人工微調 ~3 分鐘
改善幅度：整理效率提升 ~5 倍

Learning Points：
- EXIF 抽取與清洗
- 規則引擎與回退策略
- 地理距離聚合

技能要求：
- 必備：EXIF/日期處理
- 進階：地理計算與聚簇

延伸思考：
- 如何處理多時區旅行？
- 缺 GPS 如何推斷（如地標庫）？
- 使用者自訂規則 UI？

Practice：
- 基礎：抽取日期寫入 DB（30 分）
- 進階：GPS 聚簇建立相簿（2 小時）
- 專案：規則化介面與回測（8 小時）

Assessment：
- 功能（40%）：正確歸檔
- 品質（30%）：規則可擴充
- 效能（20%）：聚簇效率
- 創新（10%）：自訂規則

---

## Case #7: 並行與背壓（Backpressure）控制

### Problem Statement（問題陳述）
業務場景：批次上傳需並行處理提升吞吐，但無節制的並行會壓垮伺服器或網路，導致錯誤與整體變慢。
技術挑戰：找到最佳並行度、實作背壓與自適應調整。
影響範圍：吞吐、穩定性、成本。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 客戶端無並行上限：壅塞。
2. 伺服器無佇列與流控：資源爭用。
3. 無度量回饋：無法調整。

深層原因：
- 架構層面：缺乏 backpressure 設計。
- 技術層面：無限度 Thread/Promise 同步。
- 流程層面：未以數據調參。

### Solution Design（解決方案設計）
解決策略：客戶端設定並行上限與速率，伺服器端使用工作隊列吸收尖峰；以指標（RTT/失敗率/CPU）自動調整並行度。

實施步驟：
1. 客戶端並行控制
- 實作細節：ThreadPool/Promise pool 上限、退避
- 所需資源：Python concurrent.futures
- 預估時間：0.5 天

2. 服務端流控
- 實作細節：隊列長度監控，超閾值回傳 429 提示
- 所需資源：Express、Redis
- 預估時間：0.5 天

關鍵程式碼/設定：
```py
from concurrent.futures import ThreadPoolExecutor, as_completed
def worker(path): return upload_one(path)
with ThreadPoolExecutor(max_workers=4) as ex:
    futures = [ex.submit(worker, p) for p in files]
    for f in as_completed(futures):
        pass
```

實測數據：
改善前：無上限並行（~50）導致失敗率 12%，總時長 28 分
改善後：並行 4~8 自適應，失敗率 <1%，總時長 16 分
改善幅度：穩定性大幅提升，耗時 -43%

Learning Points：
- 並行上限與退避
- 429/隊列信號
- 自適應調參

技能要求：
- 必備：並行程式設計
- 進階：反壅塞策略

延伸思考：
- 依網速自適應如何實作？
- 多客戶端公平排程？
- 背壓與重試交互？

Practice：
- 基礎：加 --concurrency 參數（30 分）
- 進階：觀測失敗率自動調整（2 小時）
- 專案：服務端 429 + 指標驅動客端調參（8 小時）

Assessment：
- 功能（40%）：並行可控
- 品質（30%）：穩定性
- 效能（20%）：吞吐提升
- 創新（10%）：自適應

---

## Case #8: 上傳安全：認證與簽名 URL

### Problem Statement（問題陳述）
業務場景：開放批次上傳若未妥善控管權限，可能被濫用、注入惡意檔案或佔用資源，造成資安風險。
技術挑戰：實作認證授權、短時效簽名上傳 URL、防止橫向越權。
影響範圍：資料安全、資源濫用、法規合規。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 未驗證用戶身份：匿名上傳風險高。
2. 直傳儲存沒有簽名：外部濫用。
3. 權限模型缺失：相簿/組織界線模糊。

深層原因：
- 架構層面：缺少 IAM 與角色模型。
- 技術層面：未使用短時效簽名 URL。
- 流程層面：無審計與配額。

### Solution Design（解決方案設計）
解決策略：JWT/Session 驗證，後端生成短時效簽名 URL（如 S3 pre-signed），僅允許已授權的相簿/路徑；加上審計日誌與配額。

實施步驟：
1. 認證中介層
- 實作細節：JWT 驗證、角色檢查
- 所需資源：express-jwt
- 預估時間：0.5 天

2. 簽名直傳
- 實作細節：Get pre-signed PUT URL，5 分鐘有效
- 所需資源：AWS SDK/MinIO
- 預估時間：0.5 天

關鍵程式碼/設定：
```js
// 產生 S3 pre-signed URL
import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3';
import { getSignedUrl } from '@aws-sdk/s3-request-presigner';
const s3 = new S3Client({ region: 'ap-northeast-1' });
app.post('/api/upload-url', auth, async (req, res) => {
  const key = `albums/${req.user.org}/${req.body.album}/${crypto.randomUUID()}.jpg`;
  const url = await getSignedUrl(s3, new PutObjectCommand({ Bucket: 'photos', Key: key, ContentType: 'image/jpeg' }), { expiresIn: 300 });
  res.json({ url, key });
});
```

實測數據：
改善前：匿名端點曾遭濫用，單日 10GB 無效流量
改善後：簽名 URL + 配額限制，無異常上傳
改善幅度：濫用事件 0，成本下降可觀

Learning Points：
- JWT 與授權
- 簽名 URL 與最小權限
- 審計與配額

技能要求：
- 必備：Web 安全、JWT
- 進階：雲端 IAM

延伸思考：
- 團隊/相簿層級 ACL 如何建模？
- 簽名 URL 泄漏風險？
- 審計日誌如何保存與合規？

Practice：
- 基礎：保護 /api/batch-upload（30 分）
- 進階：改為簽名上傳 S3（2 小時）
- 專案：配額與審計儀表板（8 小時）

Assessment：
- 功能（40%）：權限正確
- 品質（30%）：安全邊界清晰
- 效能（20%）：簽名延遲可控
- 創新（10%）：審計視覺化

---

## Case #9: 檔案驗證與惡意檔掃描

### Problem Statement（問題陳述）
業務場景：攻擊者可能以圖片外觀包裝惡意檔，或上傳巨型圖造成資源耗盡，需在上傳流程嚴格驗證。
技術挑戰： MIME 檢測、內容掃描、尺寸限制與早期拒絕。
影響範圍：資安事件、服務可用性、法規風險。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 僅靠副檔名判斷：可被偽裝。
2. 無掃毒：風險未控。
3. 尺寸/像素未限制：資源耗盡。

深層原因：
- 架構層面：缺少安全閘道。
- 技術層面：未進行 MIME sniff 與 AV 掃描。
- 流程層面：缺乏拒絕機制與告警。

### Solution Design（解決方案設計）
解決策略：使用 file-type 檢測真實 MIME、限制尺寸/像素/大小、整合 ClamAV 掃描，於暫存區完成驗證後才入庫與後處理。

實施步驟：
1. MIME/尺寸驗證
- 實作細節：file-type 讀取頭資訊，Sharp metadata 讀像素
- 所需資源：file-type、Sharp
- 預估時間：0.5 天

2. 反病毒掃描
- 實作細節：clamdscan 掃描暫存檔，陽性即拒絕
- 所需資源：ClamAV
- 預估時間：0.5 天

關鍵程式碼/設定：
```js
import { fileTypeFromFile } from 'file-type';
import sharp from 'sharp';
const ft = await fileTypeFromFile(tmpPath);
if (!['image/jpeg','image/png','image/webp'].includes(ft?.mime)) throw new Error('Unsupported type');
const meta = await sharp(tmpPath).metadata();
if (meta.width * meta.height > 50e6) throw new Error('Too many pixels');
```

實測數據：
改善前：發現多起偽裝檔與巨型圖攻擊
改善後：全部攔截，無入庫
改善幅度：高風險事件歸零

Learning Points：
- MIME sniff 與頭資訊
- 尺寸/像素閾值
- AV 掃描流程

技能要求：
- 必備：安全基礎
- 進階：安全閘道設計

延伸思考：
- 使用雲端掃描 API 的取捨？
- 對隱私敏感照片如何處理？
- 安全事件通報流程？

Practice：
- 基礎：加入 MIME 驗證（30 分）
- 進階：整合 ClamAV（2 小時）
- 專案：安全策略可配置化（8 小時）

Assessment：
- 功能（40%）：準確拒絕
- 品質（30%）：錯誤訊息與記錄
- 效能（20%）：延遲最小化
- 創新（10%）：策略化配置

---

## Case #10: 儲存架構與 S3 Multipart Upload

### Problem Statement（問題陳述）
業務場景：大量照片需可靠、可擴充且成本可控的儲存；本地磁碟難以擴容與備援。
技術挑戰：採用 S3 相容儲存，支援大型檔案與高併發；路徑規劃避免熱點與名稱衝突。
影響範圍：可用性、擴充性、成本。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 本地磁碟擴容困難：風險高。
2. 單檔上傳不穩：大檔易失敗。
3. 目錄熱點：單目錄過多檔名。

深層原因：
- 架構層面：未雲端化。
- 技術層面：未用 Multipart。
- 流程層面：無命名與佈局規範。

### Solution Design（解決方案設計）
解決策略：採 S3/MinIO，使用 Multipart Upload；命名以日期/雜湊分桶（如 prefix 分散），Cache-Control 設置。

實施步驟：
1. 命名與路徑規劃
- 實作細節：albums/{org}/{album}/{sha256[0:2]}/{id}.jpg
- 所需資源：設計規範
- 預估時間：0.5 天

2. Multipart 上傳
- 實作細節：CreateMultipart → UploadPart → Complete
- 所需資源：AWS SDK
- 預估時間：0.5 天

關鍵程式碼/設定：
```js
// AWS SDK v3 Multipart（簡化示意）
const create = await s3.send(new CreateMultipartUploadCommand({ Bucket, Key }));
// 客戶端並行上傳 parts...
await s3.send(new CompleteMultipartUploadCommand({ Bucket, Key, UploadId: create.UploadId, MultipartUpload: { Parts }}));
```

實測數據：
改善前：單檔 >100MB 失敗率 8%
改善後：Multipart 失敗率 <1%，可續傳
改善幅度：可靠性顯著提升

Learning Points：
- S3 與 Multipart
- 命名與熱點分散
- 快取與版本化

技能要求：
- 必備：雲端儲存
- 進階：資料佈局設計

延伸思考：
- 版本化/刪除保護策略？
- 冷熱分層儲存？
- 加密 at-rest/in-transit？

Practice：
- 基礎：用 SDK 完成 multipart（30 分）
- 進階：實作續傳與合併（2 小時）
- 專案：清單與清理工具（8 小時）

Assessment：
- 功能（40%）：成功上傳與讀取
- 品質（30%）：錯誤處理
- 效能（20%）：吞吐與並行
- 創新（10%）：路徑策略

---

## Case #11: 冪等（Idempotency）與重試安全

### Problem Statement（問題陳述）
業務場景：網路重傳或 CLI 重跑可能造成重複上傳或狀態錯亂；需保證多次呼叫結果一致。
技術挑戰：Idempotency-Key 設計、去重與狀態機設計。
影響範圍：資料一致性、使用者信任。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 重試多次導致重複資源。
2. 狀態不一致（半完成）。
3. 無去重與狀態鎖。

深層原因：
- 架構層面：無冪等鍵表。
- 技術層面：未處理重入。
- 流程層面：CLI 無標識請求。

### Solution Design（解決方案設計）
解決策略：客戶端為每檔產生 Idempotency-Key；服務端以鍵值鎖與結果快取，重複請求回傳同結果，避免重複寫入。

實施步驟：
1. 定義 Idempotency-Key
- 實作細節：sha256(檔案內容+路徑+目標相簿)
- 所需資源：crypto
- 預估時間：0.25 天

2. 服務端結果快取
- 實作細節：Redis setnx 鎖與結果儲存
- 所需資源：Redis
- 預估時間：0.5 天

關鍵程式碼/設定：
```js
// 中介層示意
app.use('/api/batch-upload', async (req, res, next) => {
  const key = req.header('Idempotency-Key');
  if (!key) return res.status(400).send('Missing key');
  const exists = await redis.get(`idem:${key}`);
  if (exists) return res.json(JSON.parse(exists));
  res.locals.idemKey = key;
  next();
});
// 完成後：await redis.set(`idem:${key}`, JSON.stringify(result), { EX: 3600 });
```

實測數據：
改善前：重複檔上傳率 ~3%
改善後：降至 ~0%
改善幅度：一致性顯著提升

Learning Points：
- 冪等鍵設計
- 分散式鎖/結果快取
- 一致性 vs 可用性

技能要求：
- 必備：Redis/鎖
- 進階：一致性設計

延伸思考：
- 分片上傳如何定義冪等？
- 與去重雜湊的關係？
- 鍵過期策略？

Practice：
- 基礎：加入 Idempotency-Key（30 分）
- 進階：鎖與結果快取（2 小時）
- 專案：CLI 支援自動帶鍵（8 小時）

Assessment：
- 功能（40%）：重入安全
- 品質（30%）：邊界完善
- 效能（20%）：鎖衝突少
- 創新（10%）：鍵生成策略

---

## Case #12: 前端拖放多檔上傳與進度條

### Problem Statement（問題陳述）
業務場景：非技術使用者偏好可視化操作，拖放上傳並查看每檔進度與錯誤，是提升採用率的關鍵。
技術挑戰：實作拖放、XHR 進度回報、錯誤提示與重試。
影響範圍：使用者體驗、上傳成功率。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 僅 CLI/表單：體驗差。
2. 無進度回饋：易誤以為卡住。
3. 錯誤不明確：用戶放棄。

深層原因：
- 架構層面：缺 UI 元件與事件處理。
- 技術層面：未用 XHR upload.onprogress。
- 流程層面：無重試機制。

### Solution Design（解決方案設計）
解決策略：提供拖放區，顯示每檔進度、速度與 ETA；失敗可重試或匯出錯誤清單。

實施步驟：
1. 拖放與列隊
- 實作細節：Dropzone → 列隊 → 限並行
- 所需資源：原生 JS 或套件
- 預估時間：0.5 天

2. 進度與重試
- 實作細節：XHR onprogress、失敗項目重送
- 所需資源：原生 XHR/fetch
- 預估時間：0.5 天

關鍵程式碼/設定：
```html
<input type="file" id="files" multiple />
<div id="list"></div>
<script>
const input = document.getElementById('files');
input.onchange = async () => {
  for (const f of input.files) {
    const form = new FormData(); form.append('files', f);
    const xhr = new XMLHttpRequest();
    xhr.upload.onprogress = e => { /* 更新進度條 */ };
    xhr.open('POST', '/api/batch-upload'); xhr.send(form);
  }
};
</script>
```

實測數據：
改善前：新手完成上傳需教學與多次嘗試
改善後：拖放與進度顯示，成功率 +15%，投入時間 -30%
改善幅度：顯著提升採用率

Learning Points：
- XHR 進度事件
- UI 列隊與並行
- 錯誤回饋

技能要求：
- 必備：HTML/JS
- 進階：可用性設計

延伸思考：
- 大檔/多檔的 UX 細節？
- 可接續上一批上傳？
- 錯誤可匯出 CSV？

Practice：
- 基礎：加入進度條（30 分）
- 進階：重試按鈕（2 小時）
- 專案：可續傳 UI（8 小時）

Assessment：
- 功能（40%）：可用且清晰
- 品質（30%）：易維護
- 效能（20%）：不阻塞
- 創新（10%）：細節體驗

---

## Case #13: 流量控制：Rate Limit 與配額

### Problem Statement（問題陳述）
業務場景：公開服務可能遭暴力上傳或誤用，需保護後端與儲存成本。
技術挑戰：依使用者/組織限制速率與每日配額，提供友善錯誤回饋。
影響範圍：穩定性、成本、安全。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 無速率限制：尖峰壓垮系統。
2. 無配額：成本不可控。
3. 無回饋：用戶誤以為故障。

深層原因：
- 架構層面：缺少 API Gatekeeper。
- 技術層面：未用中介層計量。
- 流程層面：無配額政策。

### Solution Design（解決方案設計）
解決策略：express-rate-limit + Redis，按使用者/組織 key 限制；配額儲存與重置，超限回 429 並帶建議等待時間。

實施步驟：
1. 速率限制
- 實作細節：每分鐘/每秒限制
- 所需資源：express-rate-limit、Redis
- 預估時間：0.5 天

2. 配額管理
- 實作細節：每日/每月配額，儀表板顯示
- 所需資源：DB schema
- 預估時間：0.5 天

關鍵程式碼/設定：
```js
import rateLimit from 'express-rate-limit';
app.use('/api/', rateLimit({ windowMs: 60*1000, max: 120, standardHeaders: true, legacyHeaders: false }));
```

實測數據：
改善前：尖峰時 API 錯誤率 20%
改善後：穩定在 <1%
改善幅度：可靠性大幅提升

Learning Points：
- 速率限制模式
- 配額策略
- 回饋 UX

技能要求：
- 必備：API 管理
- 進階：多層限流

延伸思考：
- Nginx 層限流 vs 應用層？
- 窗口滑動演算法？
- 企業客製配額？

Practice：
- 基礎：加 rate limit（30 分）
- 進階：配額重置批次（2 小時）
- 專案：限流儀表板（8 小時）

Assessment：
- 功能（40%）：限流有效
- 品質（30%）：錯誤提示
- 效能（20%）：低延遲
- 創新（10%）：策略化

---

## Case #14: 可觀測性：結構化日誌與指標

### Problem Statement（問題陳述）
業務場景：批次上傳牽涉多節點，需快速定位失敗與瓶頸，否則維運成本高。
技術挑戰：統一日誌格式、鏈路關聯、核心指標與告警。
影響範圍：MTTR、可靠性、團隊效率。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 日誌零散難檢索。
2. 缺指標：吞吐/失敗率未知。
3. 無告警：異常晚發現。

深層原因：
- 架構層面：無 observability 設計。
- 技術層面：未導入 APM/metrics。
- 流程層面：無 SLO/SLA。

### Solution Design（解決方案設計）
解決策略：pino 結構化日誌，prom-client 指標（qps、錯誤率、處理時間、queue 深度），Grafana 儀表板與告警。

實施步驟：
1. 日誌與追蹤
- 實作細節：requestId/ batchId 串接
- 所需資源：pino
- 預估時間：0.5 天

2. 指標與告警
- 實作細節：/metrics 暴露，Grafana 告警
- 所需資源：Prometheus/Grafana
- 預估時間：1 天

關鍵程式碼/設定：
```js
import client from 'prom-client';
const registry = new client.Registry();
const uploads = new client.Counter({ name: 'uploads_total', help: 'uploaded files' });
registry.registerMetric(uploads);
app.get('/metrics', async (_, res) => res.end(await registry.metrics()));
```

實測數據：
改善前：故障平均定位 45 分
改善後：縮短至 10 分
改善幅度：MTTR -78%

Learning Points：
- 結構化日誌
- 指標化運維
- 告警策略

技能要求：
- 必備：日誌/metrics
- 進階：SLO 設計

延伸思考：
- 分散追蹤（OpenTelemetry）？
- 成本指標（S3/流量）？
- 看板與輪值制度？

Practice：
- 基礎：暴露 /metrics（30 分）
- 進階：加入 queue 深度指標（2 小時）
- 專案：完整儀表板與告警（8 小時）

Assessment：
- 功能（40%）：指標完整
- 品質（30%）：日誌可查
- 效能（20%）：低開銷
- 創新（10%）：自動診斷

---

## Case #15: 備份與還原（媒體與中繼資料）

### Problem Statement（問題陳述）
業務場景：相簿為重要資產，需防止誤刪/硬體故障；可快速還原。
技術挑戰：媒體（S3）與中繼資料（DB）的點合一致備份與驗證。
影響範圍：資料安全、合規、營運風險。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 僅單一副本：風險高。
2. 僅備份媒體/或 DB：不一致。
3. 無還原演練：可靠性未知。

深層原因：
- 架構層面：無備援策略。
- 技術層面：無版本化/快照。
- 流程層面：缺乏演練與紀錄。

### Solution Design（解決方案設計）
解決策略：S3 版本化 + 週期性 sync；DB 定期快照；備份清單簽名驗證；季度演練還原。

實施步驟：
1. 媒體備份
- 實作細節：aws s3 sync 到歸檔桶
- 所需資源：AWS CLI
- 預估時間：0.5 天

2. DB 備份
- 實作細節：mongodump + 加密儲存
- 所需資源：Mongo 工具
- 預估時間：0.5 天

關鍵程式碼/設定：
```sh
aws s3 sync s3://photos s3://photos-archive --storage-class STANDARD_IA
mongodump --uri="mongodb://..." --out=/backups/`date +%F`
```

實測數據：
改善前：無還原流程，風險未量化
改善後：演練還原 <30 分鐘
改善幅度：可恢復性大幅提升

Learning Points：
- 備份策略
- 還原流程
- 一致性驗證

技能要求：
- 必備：S3/DB 備份
- 進階：災備演練

延伸思考：
- 跨區/跨雲備援？
- 加密與金鑰管理？
- RPO/RTO 設定？

Practice：
- 基礎：完成一次備份（30 分）
- 進階：自動化 cron 與報告（2 小時）
- 專案：還原演練腳本（8 小時）

Assessment：
- 功能（40%）：可備可還原
- 品質（30%）：腳本可靠
- 效能（20%）：時間可控
- 創新（10%）：驗證報告

---

## Case #16: CDN 快取與格式最佳化（WebP/AVIF）

### Problem Statement（問題陳述）
業務場景：訪客瀏覽相簿流量大，需降低延遲與頻寬成本，提升用戶體驗。
技術挑戰：多尺寸快取、內容協商（Accept）、快取失效與邊緣節點策略。
影響範圍：性能、成本、SEO。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 全由原點供應：延遲高。
2. 未用現代格式：頻寬浪費。
3. 快取頭錯誤：命中低。

深層原因：
- 架構層面：未前置 CDN。
- 技術層面：未設 Cache-Control/ETag。
- 流程層面：無失效策略。

### Solution Design（解決方案設計）
解決策略：產出多尺寸與 WebP/AVIF，前端依 DPR/容器自動選擇；CDN 以長效快取與版本化 URL；變更發佈即失效。

實施步驟：
1. 多格式產出
- 實作細節：Sharp toFormat('webp'/'avif')，品質參數
- 所需資源：Sharp
- 預估時間：0.5 天

2. CDN 設置
- 實作細節：Cache-Control: public, max-age=31536000, immutable；版本化路徑
- 所需資源：CDN/CloudFront
- 預估時間：0.5 天

關鍵程式碼/設定：
```nginx
location /images/ {
  add_header Cache-Control "public, max-age=31536000, immutable";
  try_files $uri $uri.webp $uri.avif =404;
}
```

實測數據：
改善前：首屏 LCP ~2.8s，流量 100GB/月
改善後：LCP ~1.5s，流量 ~58GB/月
改善幅度：LCP -46%，頻寬 -42%

Learning Points：
- 現代圖像格式
- CDN 快取頭
- 版本化與失效

技能要求：
- 必備：HTTP 快取
- 進階：影像壓縮調優

延伸思考：
- 按裝置/網速自適應格式？
- 動態轉碼 vs 預先轉碼？
- SEO 與圖片 Sitemap？

Practice：
- 基礎：輸出 WebP（30 分）
- 進階：CDN 快取頭（2 小時）
- 專案：格式自動選擇與 A/B（8 小時）

Assessment：
- 功能（40%）：快取命中提升
- 品質（30%）：正確頭與版本化
- 效能（20%）：LCP/流量改善
- 創新（10%）：自適應策略

---

案例分類
1. 按難度分類
- 入門級（適合初學者）：Case 4, 12, 13
- 中級（需要一定基礎）：Case 1, 3, 5, 6, 7, 8, 9, 10, 11, 14, 15, 16
- 高級（需要深厚經驗）：Case 2

2. 按技術領域分類
- 架構設計類：Case 1, 2, 3, 10, 11, 14, 15, 16
- 效能優化類：Case 3, 7, 10, 14, 16
- 整合開發類：Case 1, 6, 8, 10, 12, 15
- 除錯診斷類：Case 3, 7, 9, 14
- 安全防護類：Case 8, 9, 11, 13, 15

3. 按學習目標分類
- 概念理解型：Case 4, 10, 13, 14, 16
- 技能練習型：Case 1, 3, 5, 6, 7, 12
- 問題解決型：Case 2, 8, 9, 11, 15
- 創新應用型：Case 6, 14, 16

案例關聯圖（學習路徑建議）
- 建議起點：Case 1（批次上傳 MVP），打好 API + CLI + 非同步的基礎。
- 依賴關係與順序：
  1) Case 1 → Case 3（後台處理）→ Case 14（可觀測性）
  2) Case 1 → Case 7（並行/背壓）→ Case 2（分片/續傳，高級）
  3) Case 1 → Case 4（EXIF 方向）→ Case 6（自動相簿）
  4) Case 1 → Case 5（去重）→ Case 11（冪等）
  5) Case 1 → Case 8（認證/簽名）→ Case 9（檔驗證/掃描）→ Case 13（限流/配額）
  6) Case 10（儲存/Multipart）可與 Case 2/3 並行學習
  7) 收尾與營運：Case 15（備份還原）→ Case 16（CDN/格式）
- 完整學習路徑建議：
  - 基礎階段：Case 1 → 3 → 4 → 7 → 12
  - 可靠性與安全：Case 8 → 9 → 11 → 13 → 14
  - 可擴充與效能：Case 2 → 10 → 16
  - 營運與保護：Case 5 → 6 → 15
  如此 4 條主線交織，最終可建立「可批次上傳、可靠、安全、可觀測、可擴充」的完整相片庫解決方案。

說明再次強調：上述案例為基於原文核心痛點延展的教學型案例與參考實測，供實戰練習與評估，不代表原文作者實際實作細節或數據。