---
applyTo: 'docs/_posts/*/*.md'
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
- `{title}`: 建議用英文標題，多個單字之間用 `-` 連接
- 副檔名: `.md` (推薦) 或 `.html` (舊格式)

舊格式 .html 檔案仍然可以存在，但新文章應使用 `.md` 格式。
這邊標示只是為了向前相容, 不允許新增新的 `.html` 檔案。


### 標題規範
- **使用英文**: 避免中英文混雜, 除既有文章外, 新的文章一律使用英文標題, 並符合建議命名規則
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
docs/_posts/
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
  - /原始路徑1/ (若瀏覽器使用此路徑，會自動導轉到新路徑)
  - /原始路徑2/
wordpress_postid: 數字ID（如適用）
---
```

   
### 內容格式轉換: 將 HTML 轉換為 Markdown 的程序


#### 轉換規則

只轉換格式, 不轉換內容, 也不改變文章標題及檔案名稱 (只改副檔名, 從 .html → .md)。
除了格式之外，所有內容以及程式碼請完全照舊。
請勿翻譯內文，也不要對內容做任何修飾。

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

完成轉換後的提交, 請勿直接 git add . 無條件地加入所有檔案。
請按下列程序明確的只加入這次修改的相關檔案。


```bash
# 加入新的 Markdown 檔案
git add {yyyy}-{MM}-{dd}-{title}.md

# 加入已移除的 HTML 檔案
git add {yyyy}-{MM}-{dd}-{title}.html

# 提交變更，包含轉換資訊和驗證清單
git commit -m "convert post_id: {yyyy}-{MM}-{dd}-{title} from HTML to Markdown format"
