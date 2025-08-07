# [架構師觀點] LLM 的抽象化介面設計

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼作者在設計 LLM 服務時，會把 LLM 想像成「真人」來思考 API？
把 LLM 想像成真人，可以自然地以「對話（Prompt）」方式與它溝通，進而把整個系統抽象成「有人在後端回答問題的服務」。這種具象化的想像能幫助釐清：  
1. 前端其實只需要一個「問答」介面。  
2. 後端可以用「媒合真工人」或「AI Model」來實作同一套介面。  
3. UI/UX、Session State、計費等設計，就能沿用真實客服系統／Uber 式派工平台已有的成熟經驗。  

## Q: 作者給 LLM（或人類工人）定義的最小核心介面長什麼樣子？
作者提出的極簡核心介面如下：  
```csharp
interface IChatBot
{
    IEnumerable<string> Ask(string question);
}
```  
特點與理由：  
1. `Ask` 方法只對外呈現「輸入一句話 → 可能得到多段回覆」的行為本質。  
2. 回傳 `IEnumerable<string>` 允許流式傳輸、多人協作或工具插入等彈性。  
3. 這個介面已足以開發一個前端聊天程式，也能在後端接不同「Worker」（真人、OpenAI、Ollama…）的實作。  

## Q: 「重新發明輪子」對架構師的價值是什麼？  
作者強調，自己動手做一遍（POC）有兩大收穫：  
1. 能精準理解大廠框架的設計脈絡，日後使用官方方案時不會「拿槌子釘螺絲」。  
2. 累積自己設計 Framework／API 的能力；當市場還沒有統一標準時，也能先行驗證、甚至發現更好的做法，讓未來版本演進時可以無痛對接。  

## Q: 如果要把聊天應用程式水平擴充（Scale-out），SessionState 需要考量哪些額外資訊？  
除了對話歷史（History），作者建議 SessionState 至少還要攜帶：  
1. 可用的工具清單與呼叫接口（Tool Registry）。  
2. 能被 Dispatcher / Load Balancer 識別的 Session ID，以便在多台 Worker 間正確路由。  
3. 可序列化／可轉移的狀態，確保 Worker 無狀態（Stateless），方便動態切換真人或 AI Model。  

## Q: 面對 OpenAI、LangChain、Semantic Kernel 等百家爭鳴的 API／SDK，作者建議的學習策略是什麼？  
先用抽象化思考把「LLM 要做的事」歸納成自己能控制的最小介面，做出 POC 並踩過主要坑。等理解「為何要這樣設計」後，再去對照各家 SDK 的細節，只需查語法就能快速上手，避免被頻繁的版本差異綁死。