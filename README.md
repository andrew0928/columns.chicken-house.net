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
├── service/
│   ├── compose-preview.yaml # 完整內容預覽環境
│   └── compose-draft.yaml   # 草稿快速預覽環境
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

參考 COMMAND.md 的 [完整內容預覽](./COMMAND.md#完整內容預覽) 說明

預覽與 DevContainer 共用 `service/Dockerfile`：Ruby 3.3.12、Bundler 2.5.22，
以及 `github-pages 232` 所指定的 Jekyll 3.10.0 與外掛版本。
容器基底以 digest 固定；`docs/Gemfile.lock` 納入版本控制，並以 frozen 模式安裝，
避免每次重建時重新選擇套件版本。請使用 `bundle exec` 執行 Jekyll。

正式網站仍由 GitHub Pages 從 `master:/docs` 建置；GitHub 管理其建置環境，
本機 lockfile 不會固定 GitHub 託管服務的 Ruby 版本。









# DevContainer 使用方式

在 VS Code 執行 **Dev Containers: Rebuild and Reopen in Container**。
映像建置時會安裝 lockfile 中的套件，開啟容器後會自動執行 `bundle check`。
如果曾在此 repo 設定本機 Bundler path，先移除 `docs/.bundle/config` 中舊的
`BUNDLE_PATH` 設定，使用容器預先安裝的 `/usr/local/bundle`。

```shell
cd /workspaces/columns.chicken-house.net/docs/
bundle exec jekyll serve --host 0.0.0.0 --destination /tmp/columns-site
```

## 更新依賴

在獨立分支更新 `docs/Gemfile` 的版本限制，使用指定 Ruby 環境重新解析
`Gemfile.lock`（更新時暫設 `BUNDLE_FROZEN=false`），再重建容器。
將 Gemfile 與 lockfile 一起提交，並執行 [正式模式建置檢查](./COMMAND.md#正式模式建置檢查)、
抽查文章網址、分頁、程式碼上色與 RSS。不要直接升級單一 Jekyll 套件而跳過
`github-pages` 的相依版本限制。
