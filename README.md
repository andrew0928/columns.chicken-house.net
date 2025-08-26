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
│   └── pages/              # 靜態頁面
├── _embedding/             # AI 生成的內容分析資料
├── _migration/             # 內容遷移和批次處理工作區
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

### `/_embedding` - AI 內容分析
- **用途**: 存放從原始文章生成的結構化內容
- **格式**: 每篇文章對應一個 embedding 檔案
- **功能**: 支援 AI 檢索、摘要、問答對生成等

### `/_migration` - 工作區
- **用途**: 批次處理任務的工作目錄
- **內容**: 任務記錄、處理日誌、臨時檔案
- **功能**: 協助內容遷移和結構調整

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