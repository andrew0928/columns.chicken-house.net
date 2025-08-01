---
applyTo: '_posts/*/*.md'
---

# 部落格檔案結構規範

## 1. 檔案結構規範說明

### 檔名格式
所有部落格文章檔案必須遵循以下格式：
```
{yyyy}-{MM}-{dd}-{title}.{md|html}
```

- `{yyyy}`: 四位數年份 (例: 2004, 2016, 2024)
- `{MM}`: 兩位數月份 (例: 01, 05, 12)
- `{dd}`: 兩位數日期 (例: 01, 15, 28)
- `{title}`: 英文標題，多個單字之間用 `-` 連接
- 副檔名: `.md` (推薦) 或 `.html` (舊格式)

### 標題規範
- **必須使用英文**: 避免中英文混雜
- **小寫字母**: 全部使用小寫
- **連字符分隔**: 多個單字用 `-` 連接
- **簡潔明確**: 能清楚表達文章主題

### 範例對照表

| ❌ 錯誤格式 | ✅ 正確格式 | 說明 |
|------------|------------|------|
| `2004-12-14-thinkpad-聯想墊子-my-god.html` | `2004-12-14-thinkpad-lenovo-acquisition-shock.html` | 移除中文，使用描述性英文 |
| `2004-12-15-三個好用的-asp-net-httphandler.html` | `2004-12-15-three-useful-asp-net-httphandlers.html` | 完全英文化，保持技術術語 |
| `2004-12-17-任意放大縮小網頁的內容.html` | `2004-12-17-zoom-webpage-content-with-css.html` | 技術功能描述性命名 |
| `2024-07-11-LLM_APP_開發經驗分享.md` | `2024-07-11-llm-app-development-experience-sharing.md` | 移除底線，全小寫，英文化 |

### 目錄結構
```
_posts/
├── 2004/
│   ├── 2004-12-14-thinkpad-lenovo-acquisition-shock.html
│   ├── 2004-12-15-three-useful-asp-net-httphandlers.html
│   └── ...
├── 2016/
│   ├── 2016-04-29-rancher-on-azure-lab.md
│   └── ...
└── 2024/
    ├── 2024-07-11-llm-app-development-experience-sharing.md
    └── ...
```

### YAML Frontmatter 規範
```yaml
---
layout: post
title: "文章標題（可包含中文）"
categories: 
tags: ["標籤1", "標籤2"]
published: true
comments: true
redirect_from:
  - /原始路徑1/
  - /原始路徑2/
wordpress_postid: 數字ID（如適用）
---
```

## 2. 異動時需要連帶變更的動作

### 2.1 異動 MD 檔名流程

當需要變更檔案名稱時，必須按照以下順序執行：

0. **確認新檔名**:  
確認新的檔名符合上述規範。
若需要將中文檔名翻譯成英文，你可能需要內文當作 context.
請最多只讀取內文的第一段，前 50 行，或是前 1000 字的內文來判定就好。
這些範圍不包括 yaml frontmatter 的內容，請從 HTML / MD 的部分開始。


1. **加入舊檔名轉導**
   ```yaml
   redirect_from:
     - /yyyy/mm/dd/舊標題/
   ```

2. **加入原 permalink 轉導**
   ```yaml
   redirect_from:
     - /yyyy/mm/dd/舊標題/
     - /原有permalink路徑/
   ```

3. **移除 permalink 行**
   ```yaml
   # 刪除這行
   permalink: "/原有路徑/"
   ```

4. **儲存並重新命名檔案**
   ```bash
   mv "舊檔名.md" "新檔名.md"
   ```

5. **準備 disqus 轉移網址對應**
   輸出 /_migration/url-mapping.txt 檔案，附加新舊網址對應, 附加一行, 用逗號分隔, 格式為: {舊網址},{新網址}
   新網址從檔名解析, 例如 2024-07-11-llm-app-development-experience-sharing.md 對應的網址是 /2024/07/11/llm-app-development-experience-sharing/

   範例如下:
   ```txt
   /2024/07/11/llm-app-開發經驗分享/,/2024/07/11/llm-app-development-experience-sharing/
   ```
   
### 2.2 HTML 轉換為 Markdown 格式

#### 變數定義
```
post_id = 檔案名稱（不含副檔名）
year = 從路徑取得的年份
publish_date = yyyy-mm-dd 格式
```

#### 轉換規則
1. **保留 YAML frontmatter** - 維持 `---` 之間的內容不變
2. **HTML 標籤轉換**:
   - 移除所有 HTML 標籤 (`<p>`, `<div>`, `<span>` 等)
   - 程式碼區塊: `<code>` → Markdown ` ```language `
   - 連結轉換: HTML `<a>` 標籤 → Markdown 連結格式
   - 標題轉換: `<h1>`, `<h2>` 等 → `#`, `##` 等
   - 列表轉換: `<ul>`, `<ol>`, `<li>` → Markdown 列表格式

3. **輸出格式**:
   - 輸入: `/_posts/2016/2016-04-29-example.html`
   - 輸出: `/_posts/2016/2016-04-29-example.md`

### 2.4 Git 版本控制

完成轉換後的提交流程：
```bash
# 加入新的 Markdown 檔案
git add 新檔案.md

# 加入已移除的 HTML 檔案
git add 原檔案.html

# 提交變更，包含轉換資訊和驗證清單
git commit -m "convert post_id: 檔案名稱
- 轉換 HTML 到 Markdown
- 更新轉導設定"
```