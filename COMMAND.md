# 部落格預覽指令

## 完整內容預覽

完整載入已發布文章、草稿、未來文章與未發布內容：

```shell
docker compose -f service/compose-preview.yaml up -d --build --force-recreate --remove-orphans
```

預覽網址：<http://localhost:4000>

## 草稿快速預覽

只處理最新 20 篇文章，適合撰寫與調整新文章時使用：

```shell
docker compose -f service/compose-draft.yaml up -d --build --force-recreate --remove-orphans
```

預覽網址：<http://localhost:4000>

## 正式模式建置檢查

使用與 GitHub Pages 相同的 `github-pages` 建置入口，不包含草稿、未來文章與未發布內容：

```shell
docker compose -f service/compose-preview.yaml build
docker compose -f service/compose-preview.yaml run --rm --no-deps -e JEKYLL_ENV=production -e PAGES_REPO_NWO=andrew0928/columns.chicken-house.net github-pages bundle exec github-pages build --source /usr/src/app --destination /tmp/columns-site
```

產物位於一次性容器的 `/tmp/columns-site`，容器結束後即移除；此指令不會部署網站。
