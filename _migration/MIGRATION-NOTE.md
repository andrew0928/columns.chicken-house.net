# 2025-08 部落格遷移

1. [X] HTML -> Markdown
2. [X] Blog Root 從 / 轉移到 /docs
3. [X] 文章圖片從 /wp-content/images/ 轉移到 /docs/assets/images/
4. [X] 中文檔名 -> 英文檔名 (修正連結, 轉移 Disqus Comments)
5. [X] 從 GitHub Pages 直接發布 -> 改為透過 Azure Front Door + CDN 發布
6. [X] 文章摘要生成 ( _embeddings , chat with blog 的功能基礎 )


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


## 轉移完成

預計收尾:
- [X] 移除 /docs/wp-content
- [ ] 擴充 docker-compose.yml, 除了 jekyll 之外, 加入 mcp, km, qdrant (run and build image), 而 application image 則由 BlogIndex 來 build
- [ ] 壓縮 git repo (https://chatgpt.com/share/68ad898b-aaf0-800d-94ed-be67cd609576)
- [X] 將 github pages 的發行 branch 從 develop 改回 master

這些動作都完成後, 會刪除這份紀錄檔案, 以及 _migration 資料夾.