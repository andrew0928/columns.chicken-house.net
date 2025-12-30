---
layout: synthesis
title: "人生ｵﾜﾀ＼(^o^)／の大冒険"
synthesis_type: solution
source_post: /2007/02/14/life-owata-adventure/
redirect_from:
  - /2007/02/14/life-owata-adventure/solution/
---

說明
- 來源文章僅提供遊戲連結與玩家體驗感想（高難度、滿滿陷阱、容易挫折），未包含可直接提取的技術細節、根因、解法與指標。
- 為滿足教學、實作與評估需求，以下 15 個案例為根據該遊戲的核心特性（極高難度、處處陷阱、容易讓玩家抓狂）所延伸的實戰型案例，內容包含可實作的設計、程式碼、流程與評估指標。實測數據為示意性的內部測試範例，用於教學與演練。

## Case #1: 高難度陷阱遊戲的挫折管理與難度曲線設計

### Problem Statement（問題陳述）
業務場景：一款以「惡意陷阱」著稱的 2D 平台遊戲上線後，玩家大量反映太難、太機車，社群出現負評與流失。團隊希望保留遊戲的殘酷幽默風格，但降低早期流失，讓玩家願意多嘗試幾次並進入「痛並快樂著」的狀態。
技術挑戰：在不改變核心關卡構想下，建立可調整的難度曲線與挫折管理機制（例如緩衝、提示、微型教學）。
影響範圍：新手留存、遊玩時長、負評比例、退款率。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 難度峰值太早、陷阱不可預期，玩家在認知尚未建立時就連續死亡。
2. 缺乏新手引導與可學習的安全區，玩家無法快速歸納規則。
3. 重試成本高（讀取時間、回到很遠處），使挫折感成倍增加。

深層原因：
- 架構層面：沒有難度參數化與可調的關卡節奏層。
- 技術層面：無「土狼時間」（Coyote Time）、輸入緩衝、動態輔助等基礎能力。
- 流程層面：缺乏系統性的可用性測試與數據驅動調整迭代。

### Solution Design（解決方案設計）
解決策略：建立可配置的挫折管理框架：在前期加入微型教學與安全區、導入「土狼時間」與輸入緩衝、死亡後提供短暫保護或節奏放緩、降低重試成本。透過遙測監測死亡點、重試時間與流失點，逐步微調。

實施步驟：
1. 導入移動與跳躍的容錯
- 實作細節：加入 Coyote Time（離地後短時間仍可起跳）、Jump Input Buffer（提早按跳躍可緩存到著地執行）
- 所需資源：TypeScript/JS、遊戲主迴圈
- 預估時間：1-2 天

2. 微型教學與安全區
- 實作細節：前 30 秒僅出現單一新機制；關鍵陷阱前設立可重試的短區段
- 所需資源：關卡編輯能力、文案
- 預估時間：1-2 天

3. 遙測與難度參數化
- 實作細節：記錄死亡座標、重試耗時；將陷阱密度、觸發延遲參數化
- 所需資源：Analytics SDK（如 PostHog/Amplitude）
- 預估時間：2-3 天

關鍵程式碼/設定：
```ts
// Coyote Time + Input Buffer（實作範例）
class JumpAssist {
  private lastGroundedAt = 0;
  private lastJumpPressedAt = -Infinity;
  constructor(
    private coyoteMs = 100,   // 離地後仍可起跳的時間
    private bufferMs = 120    // 提前按鍵緩衝時間
  ) {}

  onGrounded(now: number) { this.lastGroundedAt = now; }
  onJumpPressed(now: number) { this.lastJumpPressedAt = now; }

  shouldJump(now: number) {
    const coyoteOk = (now - this.lastGroundedAt) <= this.coyoteMs;
    const bufferOk = (now - this.lastJumpPressedAt) <= this.bufferMs;
    return coyoteOk && bufferOk;
  }
}
```

實際案例：以某 2D 惡意陷阱平台遊戲內部測試為例
實作環境：HTML5 Canvas + TypeScript
實測數據：
- 改善前：第一關完成率 22%，3 分鐘內流失率 58%
- 改善後：第一關完成率 53%，3 分鐘內流失率 31%
- 改善幅度：完成率 +140%，早期流失 -27pp

Learning Points（學習要點）
核心知識點：
- 土狼時間與輸入緩衝的體感影響
- 新手引導與難度曲線的參數化
- 用遙測閉環驅動關卡微調

技能要求：
- 必備技能：JS/TS、遊戲主迴圈與輸入處理
- 進階技能：遙測設計、關卡節奏設計

延伸思考：
- 可應用於動作、射擊、節奏遊戲的容錯設計
- 風險：過度輔助稀釋品牌「惡意」風格；需設計開關

Practice Exercise（練習題）
- 基礎練習：為角色加入 Coyote Time 與 Buffer（30 分）
- 進階練習：以配置檔切換三種輔助強度並量測完成率（2 小時）
- 專案練習：設計含 3 種新機制的「安全教學關卡」並做 A/B 測試（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：輔助開關與參數可用
- 程式碼品質（30%）：可測試、可配置
- 效能優化（20%）：輔助不增加卡頓
- 創新性（10%）：符合遊戲風格的創意輔助

---

## Case #2: 即時重試與檢查點系統

### Problem Statement（問題陳述）
業務場景：玩家頻繁死亡且需要回到很遠的起點，導致重試間隔過長，情緒升溫。希望保留關卡難度，但縮短「從死亡到再次嘗試」的時間。
技術挑戰：在不破壞關卡節奏下設置合理檢查點，實作快速、乾淨的重生流程。
影響範圍：重試頻率、黏著度、負評。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 缺乏檢查點，死亡需重走長距離。
2. 重生流程載入資源與重置邏輯不乾淨，耗時。
3. UI/動畫冗長，延長重試延遲。

深層原因：
- 架構層面：沒有關卡狀態快照/恢復機制。
- 技術層面：重置未集中管理，資源釋放與復用不足。
- 流程層面：未將「時間到重試」列為關鍵 KPI。

### Solution Design（解決方案設計）
解決策略：加入細粒度檢查點、將重生流程資源化與模組化，統一重置與恢復邏輯；縮短 UI 過場，保留可跳過。

實施步驟：
1. 定義檢查點資料結構與保存
- 實作細節：存角色座標/狀態、已觸發機關的最小必要集
- 所需資源：序列化工具（JSON）
- 預估時間：1 天

2. 建立統一的 Respawn Pipeline
- 實作細節：關閉事件、回收物件、還原狀態、淡入
- 所需資源：物件池、事件匯流排
- 預估時間：1-2 天

關鍵程式碼/設定：
```ts
interface Checkpoint {
  id: string; pos: {x:number;y:number}; flags: Record<string, boolean>;
}
let currentCheckpoint: Checkpoint | null = null;

function saveCheckpoint(cp: Checkpoint) {
  currentCheckpoint = cp;
  localStorage.setItem('cp', JSON.stringify(cp));
}

function respawn() {
  const cp = currentCheckpoint || JSON.parse(localStorage.getItem('cp') || 'null');
  if (!cp) return reloadLevelHard();
  cleanupTransient(); // 關閉事件/計時器，回收物件
  restoreFlags(cp.flags);
  player.setPosition(cp.pos.x, cp.pos.y);
  fadeIn(200);
}
```

實作環境：HTML5 Canvas + TS
實測數據：
- 改善前：死亡→可控角色平均 4.2s
- 改善後：0.7s
- 改善幅度：-83%

Learning Points：檢查點粒度、還原最小充分狀態、重生體驗與心流
技能要求：序列化、生命週期管理；進階：物件池
練習題：為一張地圖放置 3 個檢查點並量測重試時間；擴充為可熱更新配置

---

## Case #3: 碰撞箱與精準跳躍的「不公平死亡」修正

### Problem Statement（問題陳述）
業務場景：玩家回報「明明沒碰到陷阱也死了」，影片顯示精靈圖與碰撞箱對不齊，造成體感不公平。
技術挑戰：對齊精靈與碰撞、提供可視化偵錯、在效能可接受下提高精準度。
影響範圍：體驗可信度、負評、留存。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 碰撞箱大於/錯位於精靈。
2. 原點（anchor）與縮放導致偏移。
3. 動畫切換時碰撞箱未同步。

深層原因：
- 架構層面：渲染與碰撞資料來源不一致。
- 技術層面：缺乏碰撞可視化與單元測試。
- 流程層面：缺少針對碰撞的 QA 清單。

### Solution Design（解決方案設計）
解決策略：建立統一的對齊規約與工具：以單一來源（sprite meta）生成碰撞、內建可視化疊圖、關鍵動畫切換時更新碰撞。

實施步驟：
1. 對齊規約與工具
- 實作細節：從 spritesheet meta 產生 collider，設計檢視熱鍵
- 所需資源：spritesheet 工具（TexturePacker）
- 預估時間：1-2 天

2. 自動化檢查
- 實作細節：單元測試檢查 collider 與 sprite 邊界差距
- 所需資源：Jest/Vitest
- 預估時間：1 天

關鍵程式碼/設定：
```ts
// 碰撞可視化（偵錯）繪製
function drawDebugCollider(ctx: CanvasRenderingContext2D, entity: Entity) {
  const c = entity.collider; const s = entity.sprite;
  ctx.save(); ctx.strokeStyle = 'rgba(255,0,0,0.6)';
  ctx.strokeRect(c.x, c.y, c.w, c.h);
  ctx.strokeStyle = 'rgba(0,255,0,0.6)';
  ctx.strokeRect(s.x, s.y, s.w, s.h);
  ctx.restore();
}
```

實測數據：
- 改善前：碰撞相關投訴 23% 的工單
- 改善後：降至 5%
- 幅度：-78%

Learning Points：單一來源原則、可視化偵錯的重要性
技能要求：Canvas 繪製、動畫與碰撞同步；進階：像素/多邊形碰撞
練習題：為 3 種陷阱加入可視化；撰寫 5 個碰撞對齊單測

---

## Case #4: 固定時間步進避免跨設備跳躍高度差異

### Problem Statement（問題陳述）
業務場景：不同電腦/瀏覽器中，同一跳躍按鍵卻有不同高度，造成關卡難度不一致。
技術挑戰：遊戲邏輯對時間步長敏感；需要 decouple 更新與渲染。
影響範圍：公平性、可預測性、QA 成本。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 物理更新與渲染共用可變 dt。
2. 高刷新螢幕導致更多次更新，積分誤差不同。
3. 裝置性能差造成掉幀，影響跳躍曲線。

深層原因：
- 架構層面：無固定步進與補償架構。
- 技術層面：缺失 accumulator 與插值。
- 流程層面：未在多刷新率設備上測試。

### Solution Design（解決方案設計）
解決策略：實作固定時間步（如 1/120s），使用 accumulator 執行多次更新；渲染使用插值；限制單幀最大更新次數避免螺旋死亡。

實施步驟：
1. 重構主迴圈
- 實作細節：accumulator、clamp、插值
- 所需資源：rAF、效能計
- 預估時間：2-3 天

2. 多設備 QA
- 實作細節：60/120/144Hz、低規裝置
- 所需資源：測試機台
- 預估時間：1-2 天

關鍵程式碼/設定：
```ts
const STEP = 1/120; // 固定步進
let acc = 0, last = performance.now()/1000;

function loop(nowMs: number) {
  const now = nowMs/1000; acc += Math.min(0.25, now - last); last = now;
  let updates = 0;
  while (acc >= STEP && updates < 10) {
    update(STEP); acc -= STEP; updates++;
  }
  render(acc/STEP); // 插值
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);
```

實測數據：
- 改善前：跳躍頂點標準差（跨設備）0.18
- 改善後：0.02
- 幅度：-89%

Learning Points：固定步進、插值、幀率獨立
技能要求：主迴圈設計；進階：時間同步與重播
練習題：將現有遊戲改為固定步進並比較跳躍曲線

---

## Case #5: 鍵盤輸入延遲與輸入緩衝最佳化

### Problem Statement（問題陳述）
業務場景：玩家反映按下跳躍有明顯延遲，特別在低配裝置或多聲效情境。
技術挑戰：降低輸入到反應時間（Input-to-Photon），避免事件丟失與抖動。
影響範圍：體感、精準操作關卡通關率。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 僅依賴 keypress/keyup 事件，未在更新迴圈輪詢。
2. 音效解碼或 GC 導致卡頓。
3. IME/瀏覽器焦點造成事件延遲。

深層原因：
- 架構層面：輸入層與主迴圈未整合。
- 技術層面：缺乏輸入緩衝與去抖。
- 流程層面：未使用輸入延遲量測。

### Solution Design（解決方案設計）
解決策略：採用 keydown 狀態 + 每步輪詢、加入輸入緩衝、音效預解碼、避免在更新中創建物件。

實施步驟：
1. 輸入層重構
- 實作細節：狀態表、緩衝時間窗
- 所需資源：TS/JS
- 預估時間：1 天

2. 音效/記憶體優化
- 實作細節：預解碼、物件池
- 所需資源：WebAudio
- 預估時間：1 天

關鍵程式碼/設定：
```ts
class Input {
  down = new Set<string>(); lastPressed: Record<string, number> = {};
  onKey(e: KeyboardEvent, isDown: boolean) {
    const k = e.code; isDown ? this.down.add(k) : this.down.delete(k);
    if (isDown) this.lastPressed[k] = performance.now();
  }
  buffered(k: string, ms=120) { return performance.now() - (this.lastPressed[k]||-1e9) <= ms; }
}
```

實測數據：
- 改善前：輸入至動作中位延遲 115ms
- 改善後：54ms
- 幅度：-53%

Learning Points：事件 vs 輪詢、輸入緩衝窗口
技能要求：輸入系統；進階：延遲量測
練習題：以 requestAnimationFrame 量測輸入延遲曲線並提出優化

---

## Case #6: 陷阱前提示（Telegraphing）與公平性設計

### Problem Statement（問題陳述）
業務場景：關卡常在「以為通關」的瞬間設置致命陷阱，玩家覺得被戲弄而非被挑戰。
技術挑戰：保留驚喜與惡趣味的同時，提供足量訊號讓高手能讀到。
影響範圍：滿意度、口碑、重玩價值。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 陷阱零預兆，違反預期。
2. 視覺與音訊提示不足或被遮蔽。
3. 與關卡語言不一致。

深層原因：
- 架構層面：沒有狀態機與提示系統。
- 技術層面：特效與碰撞觸發拆分不良。
- 流程層面：未建立「提示足量」的設計規範。

### Solution Design（解決方案設計）
解決策略：為高殺傷機關增加前搖（pre-warn）與視聽提示；建立統一的陷阱狀態機（warning→active→cooldown）。

實施步驟：
1. 狀態機與提示
- 實作細節：前搖期間播放微光、抖動、音效
- 所需資源：VFX/SFX
- 預估時間：1-2 天

2. 關卡審查清單
- 實作細節：每個致命點需至少兩種提示
- 所需資源：設計文檔
- 預估時間：0.5 天

關鍵程式碼/設定：
```ts
enum TrapState { Idle, Warning, Active, Cooldown }
class SpikeTrap {
  state = TrapState.Idle; timer = 0;
  update(dt:number) {
    this.timer += dt;
    if (this.state===TrapState.Warning && this.timer>0.6) this.activate();
  }
  warn(){ this.state=TrapState.Warning; this.timer=0; playSfx('warn'); flashAt(this.pos); }
  activate(){ this.state=TrapState.Active; damageOnContact=true; playSfx('snap'); }
}
```

實測數據：
- 改善前：該區段死亡率 78%、負面評語集中
- 改善後：死亡率 49%、正向評論「雖坑但公平」增加
- 幅度：-29pp

Learning Points：可讀性提示、狀態機設計
技能要求：FSM、VFX/SFX 觸發；進階：UX 研究
練習題：為 3 種陷阱建立不同的前搖提示與調整時間窗

---

## Case #7: 資料驅動關卡與內建編輯器

### Problem Statement（問題陳述）
業務場景：陷阱位置硬編碼，調整一次需改程式且易出錯，迭代成本高。
技術挑戰：建立資料驅動（JSON）與所見即所得的小編輯器。
影響範圍：開發效率、可維護性、設計創造力。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 固定常數座標、缺乏資產管理。
2. 無關卡版本與驗證，易誤提交。
3. 反覆打包耗時。

深層原因：
- 架構層面：邏輯與內容耦合。
- 技術層面：缺少 Loader/Validator。
- 流程層面：無關卡審查流程。

### Solution Design（解決方案設計）
解決策略：關卡使用 JSON/CSV，啟動時載入；提供簡易編輯器與驗證器；加入版本控制與 CI 驗證。

實施步驟：
1. 定義關卡 Schema 與 Loader
- 實作細節：座標、類型、參數、觸發邏輯
- 所需資源：JSON、Zod 驗證
- 預估時間：2 天

2. 編輯器與驗證
- 實作細節：拖拉、對齊、即時檢查
- 所需資源：Electron/網頁工具
- 預估時間：3-4 天

關鍵程式碼/設定：
```ts
type TrapDef = { type:'spike'|'gun'; x:number;y:number; params?:any };
type LevelDef = { width:number;height:number; traps:TrapDef[] };

function loadLevel(json: string): LevelDef {
  const def = JSON.parse(json);
  // TODO: 驗證省略，實務中請導入 schema validator
  return def;
}
```

實測數據：
- 改善前：單次關卡調整平均 45 分鐘
- 改善後：8 分鐘
- 幅度：-82%

Learning Points：資料驅動、Schema 驗證、工具內建化
技能要求：序列化、簡易 UI；進階：Editor 內嵌
練習題：實作一個可拖拉的陷阱編輯器，支援匯入/匯出 JSON

---

## Case #8: 遙測與 A/B 測試調整關卡殘酷度

### Problem Statement（問題陳述）
業務場景：無法量化玩家在哪裡崩潰、何時離開，難以精準調難度。
技術挑戰：設計事件、指標、實驗框架，遠端配置參數。
影響範圍：留存、轉化、口碑。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 未蒐集死亡座標、重試時間。
2. 無分組測試工具。
3. 難度參數硬寫死。

深層原因：
- 架構層面：無遙測層與遠端配置。
- 技術層面：事件緩衝與重送缺失。
- 流程層面：無實驗設計與分析 SOP。

### Solution Design（解決方案設計）
解決策略：建立事件 SDK、關鍵指標（D1 留存、Level 完成率、Time-to-Retry）、遠端參數與 A/B 分流；用熱點圖定位死亡聚集。

實施步驟：
1. 事件蒐集與上報
- 實作細節：緩衝、失敗重試、匿名化
- 所需資源：Analytics 服務
- 預估時間：2 天

2. 遠端配置與分流
- 實作細節：參數拉取、hash 分組
- 所需資源：CDN/Config 服務
- 預估時間：1 天

關鍵程式碼/設定：
```ts
function emit(event:string, props:any) {
  navigator.sendBeacon('/events', JSON.stringify({event, props, t:Date.now()}));
}
const config = await fetch('/config.json').then(r=>r.json());
// 例：config.spikeWarningMs = 600
```

實測數據：
- A/B：前搖 400ms vs 600ms
- 完成率：+9pp；早期流失：-6pp

Learning Points：事件設計、A/B 基礎
技能要求：網路 API、資料分析；進階：因果推斷
練習題：定義 5 個關鍵事件並產出死亡熱點圖

---

## Case #9: 資源載入與效能卡頓導致「不公平死亡」的優化

### Problem Statement（問題陳述）
業務場景：關鍵跳躍處偶發掉幀導致失誤；玩家誤以為是操作問題。
技術挑戰：降低 GC/IO 抖動，平滑主迴圈。
影響範圍：體驗、公平性、投訴。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 大圖頻繁分配/釋放造成 GC。
2. 音效即時解碼。
3. 精靈散圖過多導致切換成本高。

深層原因：
- 架構層面：缺乏物件池與資源生命週期管理。
- 技術層面：未使用 Atlas、預解碼。
- 流程層面：無效能門檻測試。

### Solution Design（解決方案設計）
解決策略：Sprite Atlas、物件池、音效預解碼、預載關鍵資源、分幀工作。

實施步驟：
1. 物件池化常見拋射物
- 實作細節：get/release、最大池大小
- 所需資源：TS/JS
- 預估時間：1 天

2. 資產優化
- 實作細節：Atlas、WebAudio decodeAudioData 預解碼
- 所需資源：資產管線
- 預估時間：2 天

關鍵程式碼/設定：
```ts
class Pool<T> {
  private free:T[]=[]; constructor(private factory:()=>T){}
  get(){ return this.free.pop() || this.factory(); }
  release(obj:T){ this.free.push(obj); }
}
```

實測數據：
- 改善前：p95 幀時間 28ms
- 改善後：16ms
- 幅度：-43%

Learning Points：GC 友善設計、Atlas/音效預解碼
技能要求：效能分析；進階：分幀任務
練習題：將一類投射物改為物件池並量測 p95 幀時間變化

---

## Case #10: 從 Flash 遷移至 HTML5 Canvas/WebGL

### Problem Statement（問題陳述）
業務場景：老作品基於 Flash，現代瀏覽器無法運行，導致完全流失。
技術挑戰：行為一致性、資產轉換、輸入與時間系統差異。
影響範圍：可用性、維護、商業化。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. Flash runtime 停止支援。
2. 資產格式與 API 不相容。
3. 事件模型差異。

深層原因：
- 架構層面：引擎耦合於 Flash API。
- 技術層面：無抽象層。
- 流程層面：無遷移計畫。

### Solution Design（解決方案設計）
解決策略：建立渲染/輸入/時間抽象，選用 Canvas 或 PixiJS；資產批次轉換；以回歸測試確保行為一致。

實施步驟：
1. 抽象層與核心循環
- 實作細節：統一 update/render 與輸入
- 所需資源：PixiJS/Canvas
- 預估時間：1 週

2. 資產轉換與回歸測試
- 實作細節：腳本轉檔、錄製基準重播
- 所需資源：ffmpeg、腳本
- 預估時間：1 週

關鍵程式碼/設定：
```js
// 簡化版 Canvas 主迴圈
function loop(ts){ update(1/60); render(); requestAnimationFrame(loop); }
requestAnimationFrame(loop);
```

實測數據：
- 兼容率：關鍵關卡行為一致 95%+
- p95 幀時間：< 16.7ms

Learning Points：抽象層、回歸測試
技能要求：渲染基礎；進階：引擎移植
練習題：用 Canvas 重現一個 Flash 關卡的核心機制

---

## Case #11: 重置與事件未清理導致記憶體洩漏與越玩越卡

### Problem Statement（問題陳述）
業務場景：多次死亡/重生後越來越卡，甚至崩潰。
技術挑戰：找出未釋放的監聽器/計時器/資源，建立統一清理機制。
影響範圍：穩定性、評價。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 多個 addEventListener 未 remove。
2. setInterval/timeout 遺留。
3. 紋理/音效未釋放。

深層原因：
- 架構層面：場景生命週期不完整。
- 技術層面：缺乏資源追蹤。
- 流程層面：無壓力測試。

### Solution Design（解決方案設計）
解決策略：場景化管理、集中註冊與自動清理（AbortController/Disposables），開發期加入資源計數面板。

實施步驟：
1. 可處置介面與容器
- 實作細節：IDisposable、onDispose
- 所需資源：TS
- 預估時間：1 天

2. 壓力測試
- 實作細節：自動重生 1000 次觀察記憶體
- 所需資源：性能面板
- 預估時間：0.5 天

關鍵程式碼/設定：
```ts
interface Disposable { dispose():void }
class Scene implements Disposable {
  private disposables: Disposable[] = [];
  track<T extends Disposable>(d:T){ this.disposables.push(d); return d; }
  dispose(){ this.disposables.forEach(d=>d.dispose()); this.disposables=[]; }
}
```

實測數據：
- 改善前：100 次重生後記憶體 +180MB
- 改善後：+12MB
- 幅度：-93%

Learning Points：生命週期、資源追蹤
技能要求：事件/資源管理；進階：Leak 檢測工具
練習題：實作自動重生壓力測試與資源儀表板

---

## Case #12: 可重播的錄製/回放除錯與 CI 自動通關驗證

### Problem Statement（問題陳述）
業務場景：玩家回報偶發陷阱判定錯誤，難以重現。
技術挑戰：建立決定性（Deterministic）重播，錄製輸入/種子，於 CI 跑驗證。
影響範圍：缺陷修復效率、回歸風險。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 無重播機制。
2. 使用非決定性亂數或時間。
3. 版本差異造成偏移。

深層原因：
- 架構層面：無決定性抽象。
- 技術層面：缺乏可序列化的遊戲狀態。
- 流程層面：無自動化驗證。

### Solution Design（解決方案設計）
解決策略：封裝 RNG、記錄輸入與步進、重播時鎖定版本與參數；建立「黃金路徑」通關回放於 CI 執行。

實施步驟：
1. RNG 與輸入錄製
- 實作細節：種子化 PRNG、輸入時間戳
- 所需資源：TS、CI
- 預估時間：3 天

2. CI 驗證
- 實作細節：以無頭環境回放，檢查位置與事件
- 所需資源：Puppeteer
- 預估時間：2 天

關鍵程式碼/設定：
```ts
// 線性同餘 PRNG 範例
let seed=1234567; function rnd(){ seed=(seed*1664525+1013904223)|0; return (seed>>>0)/2**32; }
```

實測數據：
- 重現率：從 <10% 提升至 100%（回放）
- 缺陷修復時間：-60%

Learning Points：決定性、重播系統
技能要求：序列化、CI；進階：同步/回放引擎
練習題：錄一段 30 秒通關並在 CI 驗證位移誤差 < 1px

---

## Case #13: 進度保存與雲端同步降低流失

### Problem Statement（問題陳述）
業務場景：玩家卡關離開後回不來，因進度未保存或跨裝置不同步。
技術挑戰：設計可靠的本地/雲端存檔，避免破檔與作弊。
影響範圍：留存、回流。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 未保存檢查點/成就。
2. 本地存儲破損無備援。
3. 無雲同步。

深層原因：
- 架構層面：存檔格式未版本化。
- 技術層面：未校驗/壓縮。
- 流程層面：未設計回復流程。

### Solution Design（解決方案設計）
解決策略：本地 LocalStorage/IndexedDB + 雲端備份，存檔加版本與校驗，提供回滾。

實施步驟：
1. 存檔格式與版本
- 實作細節：schema、校驗碼（CRC/HMAC）
- 所需資源：TS、後端 API
- 預估時間：1-2 天

2. 雲同步
- 實作細節：登入後自動上傳/合併
- 所需資源：API、Auth
- 預估時間：2 天

關鍵程式碼/設定：
```ts
function saveProgress(data:any){
  localStorage.setItem('save', JSON.stringify({v:1,data}));
}
function loadProgress(){ const s=localStorage.getItem('save'); return s?JSON.parse(s):null; }
```

實測數據：
- 回流率：+12pp
- 負評提及「進度不見」：-90%

Learning Points：存檔可靠性、版本化
技能要求：Web 存儲；進階：合併策略
練習題：實作存檔備援與版本升級遷移

---

## Case #14: 反作弊與排行榜可信度

### Problem Statement（問題陳述）
業務場景：排行榜出現不可能的通關時間，傷害公平與社群。
技術挑戰：在客戶端環境驗證通關資料真實性，偵測異常。
影響範圍：競爭完整性、口碑。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 客端可篡改時間與資料。
2. 通關記錄缺乏簽章。
3. 伺服器未做異常檢測。

深層原因：
- 架構層面：信任邊界設計欠缺。
- 技術層面：無簽章/回放驗證。
- 流程層面：無反作弊政策。

### Solution Design（解決方案設計）
解決策略：通關提交加簽（HMAC）+ 伺服器重播驗證；異常行為偵測與封鎖策略。

實施步驟：
1. 簽章與提交
- 實作細節：不可逆雜湊、隨機鹽
- 所需資源：Crypto API、Server
- 預估時間：2 天

2. 伺服器驗證與回放
- 實作細節：以輸入流重播確認
- 所需資源：Replay 引擎
- 預估時間：3-5 天

關鍵程式碼/設定：
```ts
// 客端簽章（示意）
async function signRun(payload) {
  const enc = new TextEncoder().encode(JSON.stringify(payload));
  const digest = await crypto.subtle.digest('SHA-256', enc);
  return btoa(String.fromCharCode(...new Uint8Array(digest)));
}
```

實測數據：
- 偽造提交攔截率：>99%
- 黑名單重犯率：-85%

Learning Points：信任邊界、回放驗證
技能要求：密碼學 API；進階：異常偵測
練習題：為排行榜建立簽章與簡易伺服器驗證

---

## Case #15: 可近用性與舒適度（閃爍/音量/輔助模式）

### Problem Statement（問題陳述）
業務場景：高對比閃爍與刺耳音效加劇挫折，部份玩家不適。
技術挑戰：提供減少閃爍、音量限制、慢動作練習等選項，維持風格又兼顧健康。
影響範圍：可近用性、留存、評價。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 強烈閃爍與爆音無選項。
2. 無動作輔助模式。
3. 設定不可保存。

深層原因：
- 架構層面：設定系統不足。
- 技術層面：特效未加節流。
- 流程層面：未考慮可近用性規範。

### Solution Design（解決方案設計）
解決策略：加入「降低閃爍」「音量上限」「練習慢動作」選項並可保存；特效檢查通過再播放。

實施步驟：
1. 設定 UI 與持久化
- 實作細節：LocalStorage 保存
- 所需資源：UI
- 預估時間：1 天

2. 特效守門
- 實作細節：檢查閃爍頻率與亮度
- 所需資源：特效參數
- 預估時間：1 天

關鍵程式碼/設定：
```ts
const settings = { reduceFlashes:true, maxVolume:0.6, practiceSlowmo:false };
function playFlash(intensity:number){
  if (settings.reduceFlashes && intensity>0.5) return; // 阻擋強閃
  // 播放...
}
```

實測數據：
- 負面評語中「刺眼/刺耳」提及：-70%
- 回流率：+8pp

Learning Points：可近用性、設定持久化
技能要求：UI/存儲；進階：特效參數化
練習題：為遊戲加入「練習慢動作模式」並測試其對通關率影響

---

案例分類

1) 按難度分類
- 入門級（適合初學者）
  - Case #2 即時重試與檢查點系統
  - Case #5 鍵盤輸入延遲最佳化
  - Case #13 進度保存與雲端同步
  - Case #15 可近用性與舒適度
  - Case #3 碰撞箱修正（入門/中級之間）
- 中級（需要一定基礎）
  - Case #1 挫折管理與難度曲線
  - Case #6 陷阱前提示與公平性
  - Case #7 資料驅動關卡與編輯器
  - Case #8 遙測與 A/B 測試
  - Case #9 資源載入與效能優化
  - Case #11 記憶體洩漏與生命週期
- 高級（需要深厚經驗）
  - Case #4 固定時間步進
  - Case #10 Flash → HTML5 遷移
  - Case #12 錄製/回放與 CI 驗證
  - Case #14 反作弊與排行榜

2) 按技術領域分類
- 架構設計類
  - Case #1, #4, #6, #7, #10, #12, #15
- 效能優化類
  - Case #5, #9, #11
- 整合開發類
  - Case #2, #7, #8, #10, #13
- 除錯診斷類
  - Case #3, #11, #12
- 安全防護類
  - Case #14

3) 按學習目標分類
- 概念理解型
  - Case #1（難度曲線/挫折管理）、#6（Telegraphing）、#15（可近用性）
- 技能練習型
  - Case #2（檢查點/重生）、#3（碰撞可視化）、#5（輸入緩衝）、#7（Loader/Editor）
- 問題解決型
  - Case #4（幀率獨立）、#9（卡頓消除）、#11（記憶體洩漏）
- 創新應用型
  - Case #8（A/B 遙測）、#10（平台遷移）、#12（重播 CI）、#14（反作弊）

案例關聯圖（學習路徑建議）
- 建議先學：
  1) Case #2（檢查點/重試）→ 立即改善體感，為後續調整提供基礎
  2) Case #5（輸入層）與 Case #3（碰撞對齊）→ 建立公平可控的操作與判定
- 依賴關係：
  - Case #4（固定步進）依賴 Case #5/3 的穩定輸入與碰撞
  - Case #1（挫折管理）依賴 Case #2/4 的穩定性與 Case #8 的數據
  - Case #6（提示）建立在 Case #1 的難度策略與 Case #7 的資料驅動上
  - Case #8（遙測）是 Case #1、#6 調參的數據基礎
  - Case #11（資源生命週期）與 Case #9（效能）彼此支援，兩者是 #12（重播 CI）的穩定性前置
  - Case #13（存檔）與 Case #14（反作弊）分別支援玩家長期體驗與競賽公信力
  - Case #10（遷移）受益於前述的抽象分層與自動化驗證（#12）
- 完整學習路徑：
  - 入門穩定三件事：#2 → #5 → #3
  - 打底架構與公平性：#4 → #1 → #6
  - 工具化與資料化：#7 → #8
  - 效能與穩定：#9 → #11
  - 自動化與長期營運：#12 → #13 → #14
  - 平台演進與回歸驗證：#10（期間反覆用 #12 驗證）

備註
- 上述「實測數據」為示意性內部測試指標，目的是提供教學用的量化目標與評估方式，實際成效需以你的專案遙測與 A/B 結果為準。