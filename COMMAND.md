# 部落格預覽指令

## 完整內容預覽

完整載入已發布文章、草稿、未來文章與未發布內容：

```shell
docker compose -f service/compose-preview.yaml up -d --force-recreate --remove-orphans
```

預覽網址：<http://localhost:4000>

## 草稿快速預覽

只處理最新 20 篇文章，適合撰寫與調整新文章時使用：

```shell
docker compose -f service/compose-draft.yaml up -d --force-recreate --remove-orphans
```

預覽網址：<http://localhost:4000>
