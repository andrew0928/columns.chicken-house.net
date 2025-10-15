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



# 本機預覽環境

參考 COMMAND.md 的 [start preview environment](./COMMAND.md#start-preview-environment) 說明









# DevContainer 使用方式 (beta)

初次使用，請先 bundle install 更新初始環境

```shell

# 切換到 Gemfile 目錄
cd /workspaces/columns.chicken-house.net/docs/

# 設定 bundle 安裝路徑，避免權限問題
bundle config set --local path '/home/vscode/.bundle'

# 安裝相依套件
bundle install

# 就地啟動 Jekyll serve

cd /workspaces/columns.chicken-house.net/docs/
bundle exec jekyll s -d ~/_site

```