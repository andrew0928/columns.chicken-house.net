# Andrew's Blog
>
> C#, .NET, OOP, Docker
>

URL: http://columns.chicken-house.net

樣板來源: http://mazhuang.org/



# Branch Notes

Branch **master**:  
正式發布的版本, protected branch

Branch **develop**:  
開發，修改版面用的 branch, 調整完成後 merge to master 就能發布版面

Branch **draft**:  
撰寫文章用的 branch, 文章撰寫完成後 merge to master 就能發布文章





# 本機預覽環境

* 啟動 (build 時會將目前的 . 部落格內容都複製到 container 的 /home/source, 用以加速 jekyll build)
```
docker-compose build
docker-compose up -d jekyll --force-recreate
```

或是將上述兩道指令合併:
```
docker-compose up -d jekyll --build --force-recreate
```

成功後即可從 http://localhost:4000 看到 github pages 預覽結果


* 開啟 console:
```
docker-compose exec -w /home jekyll bash
```

* 更新檔案:
```
cp -Ru columns/* source
```

* 觀察 jekyll build logs:
```
docker-compose logs -t --tail 300 -f jekyll
```