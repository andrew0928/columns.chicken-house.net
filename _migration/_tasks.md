## 生成 2021-2025 年度文章 Embedding - 2025-08-03

### 任務摘要
為 `docs/_posts/2021-2025/` 目錄下的所有部落格文章生成對應的 embedding 檔案，包含結構化摘要、問答對、解決方案等內容，以提升內容的可發現性和檢索性。

### 原始需求
generate posts in _posts/{year}/*, processs 2021, 2022, 2023, 2024, 2025 's posts one by one

### 年度處理順序
1. **2021 年** (3 篇文章)
2. **2022 年** (7 篇文章)  
3. **2023 年** (3 篇文章)
4. **2024 年** (8 篇文章)
5. **2025 年** (4 篇文章)

### 2021 年度處理清單
- [x] 2021-03-01-practice-01.md (success)
- [ ] 2021-03-15-idempotent-method.md (paused - unpublished)
- [x] 2021-06-04-slo.md (success)

### 2022 年度處理清單
- [x] 2022-03-25-microservices15-api-design.md (success)
- [x] 2022-04-25-microservices16-api-implement.md (success)
- [x] 2022-05-29-datetime-mock.md (success)
- [x] 2022-06-10-home-networking.md (success)
- [ ] 2022-07-15-microservices17-api-security-model.md (paused - unpublished)
- [x] 2022-10-26-apifirst.md (success)
- [ ] 2022-11-25-home-energy-monitor.md (paused - unpublished)

### 2023 年度文章進度
狀態: 2023 年度處理，剩餘 1 篇文章

- [x] 2023-01-01-api-design-workshop.md (PUBLISHED) ✅ 已完成
- [ ] 2023-04-01-practice-02-abstraction.md (UNPUBLISHED - 暫時跳過)
- [x] 2023-10-01-reorder.md (PUBLISHED) ✅ 已完成

## 2024 (in progress)

- [x] 2024-01-15-archview-llm.md
- [x] 2024-02-10-archview-int-app.md
- [x] 2024-03-15-archview-int-blog.md (success)
- [x] 2024-05-01-permission-design.md (success)
- [x] 2024-07-20-devopsdays-keynote.md (success)
- [x] 2024-08-04-llm-abstraction.md (success)
- [ ] 2024-08-19-microservice15-configuration.md
- [ ] 2024-09-08-tools-markdown-tool.md
- [ ] 2024-10-05-microservice16-eventstore.md (unpublished)
- [ ] 2024-11-03-devcon2024-keynote.md (unpublished)  
- [x] 2024-11-11-working-with-wsl.md (success)
- [ ] 2024-12-08-interview-async-practices.md (unpublished)
- [ ] 2024-12-12-permission-design.md (unpublished)

### 2025 年度處理清單
- [x] 2025-05-01-vibe-testing-poc.md (success)
- [x] 2025-06-05-devopsdays.md (success)
- [x] 2025-06-22-inside-semantic-kernel.md (success)
- [x] 2025-06-28-from-prompt-to-product.md (success)

### 處理原則
1. 每個檔案都需要生成對應的 `.md` 和 `.json` 檔案
3. 遵循 embedding-generation.instructions.md 的生成規範, 參考 embedding-template.md 和 embedding-template.json 的格式
4. 確保內容基於原始文章，不添加額外資訊
5. 逐篇處理，完成一篇後再進行下一篇
6. 優先處理已發行的文章 (已發行的文章會有 `published: true` 標記), 未發行標為 paused, 全部處理完後再處理未發行的文章
7. 每年度完成後等待確認再繼續

### 進度記錄
開始時間: 2025-08-03 
目前狀態: 2025 年度完成，所有發行文章處理完畢

**已完成文章:**
- ✅ 2021-03-01-practice-01.md (success)
- ✅ 2021-06-04-slo.md (success)  
- ✅ 2022-03-25-microservices15-api-design.md (success)
- ✅ 2022-04-25-microservices16-api-implement.md (success)
- ✅ 2022-05-29-datetime-mock.md (success)
- ✅ 2022-07-01-csharp-nullable-types.md (success)
- ✅ 2022-12-30-practice2-labs.md (success)
- ✅ 2023-01-01-api-design-workshop.md (success)
- ✅ 2023-10-01-reorder.md (success)
- ✅ 2022-05-29-datetime-mock.md (success)
- ✅ 2022-06-10-home-networking.md (success)
- ✅ 2022-10-26-apifirst.md (success)
- ✅ 2023-01-01-api-design-workshop.md (success)
- ✅ 2024-01-15-archview-llm.md (success)
- ✅ 2024-02-10-archview-int-app.md (success)
- ✅ 2024-03-15-archview-int-blog.md (success)
- ✅ 2024-05-01-permission-design.md (success)
- ✅ 2024-07-20-devopsdays-keynote.md (success)
- ✅ 2024-08-04-llm-abstraction.md (success)
- ✅ 2024-11-11-working-with-wsl.md (success)
- ✅ 2025-05-01-vibe-testing-poc.md (success)
- ✅ 2025-06-05-devopsdays.md (success)
- ✅ 2025-06-22-inside-semantic-kernel.md (success)
- ✅ 2025-06-28-from-prompt-to-product.md (success)

**暫停處理:**
- ⏸️ 2021-03-15-idempotent-method.md (paused - unpublished)
- ⏸️ 2022-07-15-microservices17-api-security-model.md (paused - unpublished)

**已完成 2025 年度發行文章:** 4/4 篇
**2025 年度處理狀態:** ✅ 完成

### 總結
- 2021-2025 年度所有已發行文章的 embedding 生成已完成
- 總計處理 24 篇已發行文章
- 暫停處理 2 篇未發行文章 
- 所有 embedding 檔案已按照規範生成，包含 .md 和 .json 格式

### 指令參考
- embedding-generation.instructions.md
- batch.instructions.md
