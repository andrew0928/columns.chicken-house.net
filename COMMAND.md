## overview

寫完文章, preview 沒問題後, 就可以開始 build 了.

1. 用 LLM (GPT5) 生成摘要等資訊 (sync-post synthesis:true, 更新 artifects/synthesis)
2. 啟動 build env, 匯入資料庫 (sync-post import:true, 更新 services/_storage_volumes/*)
3. 產生 seed (columns-seed)
4. 驗證 product env
5. 推送 seed, github-pages


## .env file
以下都需要透過 service/.env 來指定 AzureOpenAI 的 endpoint, apikey 設定才能正常使用
執行的工作目錄統一在 repo:/ 下

## start preview environment
docker compose -f service/compose-preview.yaml up -d

## start build environment (qdrant + kernelmemoryservice)
docker compose -f service/compose-build.yaml up -d

## start production environment (init with columns-seed)
docker compose -f service/compose-prod.yaml up -d

## build columns-seed
docker build -f service/dockerfile-seed -t andrew0928.azurecr.io/columns-seed:develop -t andrew0928.azurecr.io/columns-seed:$(date +%Y%m%d) .
docker push andrew0928.azurecr.io/columns-seed:$(date +%Y%m%d)


## run sync-post (synthesis)
docker run --rm -it --user 1000:1000 -v $PWD:/workspaces/columns.chicken-house.net/ --env-file service/.env blogindex-syncpost:develop --postname 2025-09-16 --synthesis true --forcesync true

## run sync-post (import)
> 注意 network host, 這樣才能在 container 內連到 kernelmemoryservice ( localhost:9001 )
docker run --rm --network host -it --user 1000:1000 -v $PWD:/workspaces/columns.chicken-house.net/ --env-file service/.env blogindex-syncpost:develop --postname 2025 --import true --forcesync true

## archive service volumes
tar -czvf ../service-storage-volumes-$(date +%Y%m%d).tgz service/_storage_volumes

## extract service volumes
tar -zxvf ../service-storage-volumes-20261016.tgz service/_storage_volumes
