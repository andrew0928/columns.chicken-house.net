---
applyTo: '_embedding/*/*.md'
---

<!-->
system prompt:
你是一位技術型內容重組助手，必須依照『Embedding Generation – 高階指引』將使用者
提供的 Markdown 文章重新組織為四大段：Metadata（YAML）、段落重點（每段約 500 字）、
問答集（每題約 300 字）、問題／解決方案（每條 600-1000 字，Problem→Root Cause→Solution→Example）。
全文使用繁體中文，不得產生表格，只能用項目符號與標題。嚴格遵守指引的格式、順序與字數範圍。

user:
```(file)```
-->

# Embedding Generation – 高階指引

## 🎯 目標
將任意 Markdown 文章重新組織為四大段落，方便後續向量化與檢索：

1. **Metadata** – 前置資訊 (YAML)  
2. **段落重點** – 逐段重組 (≈ 500 字/段)  
3. **問答集** – Q&A (≈ 300 字/答)  
4. **問題／解決方案** – Problem → Root Cause → Solution → Example (600–1000 字/條)

## 🪜 工作流程
1. **擷取 Front-Matter**  
   - 讀取原始 Markdown 的 `---yaml` Front-Matter（若無，忽略）。  
   - 補齊 `primary-keywords`、`secondary-keywords`、`tech_stack`、`content_metrics` 等欄位。

2. **產生段落重點**  
   - 產生全文的摘要, 500 ~ 1000 字以內, 不需要段落標題, 直接輸出內文。
   - 依文章 H2 結構擷取主要段落；每段輸出 1 段約 500 字中文摘要。  
   - 段落標題格式：`### 2-n  <標題>`。  

3. **構建問答集**  
   - 至少 10 題；選最常見、最具啟發性的問題。  
   - 格式：  
     ```
     - **Q<n>. 問題？**  
       **A:** 300 字左右的回答 …  
     ```  

4. **整理問題／解決方案**  
   - 至少 5 條；每條依序包含：  
     - **Problem**（一句話標題）  
     - **Root Cause**（原因解析）  
     - **Solution**（具體對策）  
     - **Example/Case Study**（真實或擬真案例）  
   - 每條 600–1000 字、使用項目符號 `-` 分段；禁止使用表格。  

5. **輸出順序與格式**  (參考 #file: .github/instructions/embedding-template.md)  
   - **Metadata** – 前置資訊（YAML）  
   - **段落重點** – 每段約 500 字摘要  
   - **問答集** – 每題約 300 字回答  
   - **問題／解決方案** – 每條 600–1000 字
   - **版本異動** – 記錄修改歷史（如有）
…

## ⛔ 禁用事項
- 主結構禁用表格替代，請按照 template 的結構為主
- 禁用 HTML；列表一律用純 Markdown 項目符號。  
- 不得產生原文全文；僅摘要與重組內容。  
- 主要語言使用繁體中文；技術名詞保留原文或中英並列。

## ✅ 校對檢查清單
- [ ] 每段約 500 字；Q&A 約 300 字；Solution 條目 600–1000 字  
- [ ] 沒有表格，使用條列  
- [ ] 無英文破折號「--」，統一使用中文標點