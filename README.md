# 安德魯的部落格專案

> C#, .NET, OOP, Docker, AI, Architecture

URL: https://columns.chicken-house.net

## 專案結構

```
columns.chicken-house.net/
├── docs/                    # Jekyll 部落格根目錄 (GitHub Pages 發布來源)
│   ├── _config.yml         # Jekyll 設定檔
│   ├── _posts/             # 部落格文章
│   ├── _data/              # 資料檔案
│   ├── _includes/          # 模板片段
│   ├── _layouts/           # 版面配置
│   ├── assets/             # 靜態資源
│   ├── images/             # 文章附加圖檔
│   └── pages/              # 靜態頁面
├── artifacts/
│   └── synthesis/          # AI 生成的內容分析 (原 /_embedding)
├── .github/
│   ├── instructions/       # GitHub Copilot 規範檔案
│   └── prompts/            # AI 提示詞模板
└── README.md               # 本檔案
```

## 目錄說明

### `/docs` - Jekyll 部落格
- **用途**: GitHub Pages 發布的 Jekyll 網站根目錄
- **內容**: 所有部落格相關的檔案和配置
- **發布**: GitHub Pages 直接從此目錄發布網站

### `/artifacts/synthesis` - AI 內容分析
- **用途**: 儲存從原始文章生成的結構化內容 (embedding / 摘要 / FAQ / metadata)
- **來源**: 透過 blogindex.syncpost 指令同步產出
- **功能**: 支援 AI 檢索、摘要、問答、向量資料庫索引

### `/.github` - 開發規範
- **instructions/**: GitHub Copilot 智能提示規範
- **prompts/**: AI 內容生成提示詞模板



# Branch Notes

Branch **master**:  
正式發布的版本, protected branch

Branch **develop**:  
開發，修改版面用的 branch, 調整完成後 merge to master 就能發布版面

Branch **draft**:  
撰寫文章用的 branch, 文章撰寫完成後 merge to master 就能發布文章


# 文章異動後的同步 / 發布規則

文章發布:
- create tag: publish-20250916
- 更新 /artifacts/synthesis
- 更新並部署 MCP server


1. 僅更新 AI 內容分析 (生成 /artifacts/synthesis 對應檔案)
```
blogindex.syncpost --postname {postid} --synthesis true --forcesync true
```

2. 僅更新 MCP storage (vector DB + knowledge file store)
```
blogindex.syncpost --postname {postid} --import true --forcesync true
```

3. 同步兩者 (建議直接執行此整合步驟)
```
blogindex.syncpost --postname {postid} --synthesis true --import true --forcesync true
```



建議流程:
- 編輯或新增文章 (draft branch)
- 本機預覽確認無誤
- 執行整合同步指令 (step 3)
- PR -> merge 到 master 觸發 GitHub Pages 發布

# 本機預覽環境

* 啟動 (build 時會將目前的 ./docs 部落格內容掛載到 container 的 /usr/src/app)

```
docker-compose up -d --force-recreate
```


成功後即可從 http://localhost:4000 看到 github pages 預覽結果


* 開啟 console:
```
docker-compose exec -w /usr/src/app github-pages bash
```

* 觀察 jekyll build logs:
```
docker-compose logs -t --tail 300 -f --no-log-prefix github-pages
```