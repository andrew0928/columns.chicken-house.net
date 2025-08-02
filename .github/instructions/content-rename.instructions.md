---
applyTo: 'docs/_posts/*/*.md'
---

# 部落格檔案結構規範

參考 #file: content-format.instructions.md


## 2. 異動檔案名稱時需要連帶變更的動作

### 2.1 異動 MD 檔名流程

當需要變更檔案名稱時，必須按照以下順序執行。共六個步驟，請勿忽略任何一個步驟。
項目如下:

```yaml
1. 從文章內容確認新檔名
2. 加入舊檔名轉導 -> redirect_from
3. 加入原 permalink 轉導 -> redirect_from (若已存在同路徑則可略過)
4. 移除 permalink 行
5. 儲存並重新命名檔案
```


1. **確認新檔名**:  
確認新的檔名符合上述規範。
若需要將中文檔名翻譯成英文，你可能需要內文當作 context.
請最多只讀取內文的第一段, 前 30 行, 或是前 500 字的內文來判定。


2. **加入舊檔名轉導** 範例 (若已存在同路徑則可略過):
   ```yaml
   redirect_from:
     - /yyyy/mm/dd/舊標題/
   ```

3. **加入原 permalink 轉導** 範例 (若已存在同路徑則可略過):
   ```yaml
   redirect_from:
     - /yyyy/mm/dd/舊標題/
     - /原有permalink路徑/
   ```

4. **移除 permalink 行** 範例:
   ```yaml
   # 刪除這行
   permalink: "/原有路徑/"
   ```

5. **儲存並重新命名檔案** 範例:
   ```bash
   mv "舊檔名.md" "新檔名.md"
   ```

6. **準備 disqus 轉移網址對應** 範例:
   輸出 /_migration/url-mapping.txt 檔案，附加新舊網址對應, 附加一行, 用逗號分隔, 格式為: {舊網址},{新網址}
   新網址從檔名解析, 例如 2024-07-11-llm-app-development-experience-sharing.md 對應的網址是 /2024/07/11/llm-app-development-experience-sharing/

   範例如下:
   ```txt
   /2024/07/11/llm-app-開發經驗分享/,/2024/07/11/llm-app-development-experience-sharing/
   ```

7. 提交變更內容:
   ```bash
   git add {舊檔名}.md
   git add {新檔名}.md
   git commit -m "Rename file from '舊檔名.md' to '新檔名.md' and update redirects"
   ```