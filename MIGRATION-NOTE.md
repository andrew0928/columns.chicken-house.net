# 2025-08 部落格遷移

1. [ ] HTML -> Markdown
2. [ ] Blog Root 從 / 轉移到 /docs
3. [ ] 文章圖片從 /wp-content/images/ 轉移到 /docs/assets/images/
4. [ ] 中文檔名 -> 英文檔名 (修正連結, 轉移 Disqus Comments)
5. [ ] 從 GitHub Pages 直接發布 -> 改為透過 Azure Front Door + CDN 發布
6. [ ] 文章摘要生成 ( _embeddings , chat with blog 的功能基礎 )


# 工作日誌

## 圖片轉移

2025-08-15, 實驗結果:

**可以正確遷移的指令** (但是產生的 .md 是相對路徑)
md-img m --rootPath "docs" --relativePath "docs" --local "../../images/<filename>" docs/_posts/2005/2005-01-01-teflon-tape.md

**批次處理全部的文章**
find docs/_posts -type f -name "*.md" -exec md-img m --rootPath "docs" --relativePath "docs" --local "../../images/<filename>" "{}" \;

**修正路徑, 移除備份檔**
perl -0777 -i -pe 's{(!\[[^\]]*\]\()\.\./(?:\.\./)*images/}{${1}/images/}g' docs/_posts/**/*.md
find docs/_posts -type f -name "*_mvBK.md" -exec rm "{}" \;

**已知問題**
1. 同一圖檔出現兩次參照, 第一次已經搬走, 第二次參照的處理就會失敗, 不會修改 md, 造成破圖
=> 列 error 清單手動處理
2. logo 不會處理