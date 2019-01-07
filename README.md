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





# Notes for testing @ local env




: call jekyll s --watch --unpublished --future --drafts

: using windows container
: docker run -d --name column3 --platform=linux -v %CD%:/srv/jekyll -p 4001:4000 jekyll/jekyll:3.8.1 jekyll s --watch --drafts
: docker logs --tail 100 -t -f column3

: docker run -d --name columns -v %CD%:/srv/jekyll -p 4000:4000 jekyll/jekyll:2.4.0


docker run --name columns -d -v %CD%:/srv/jekyll -p 4000:4000 jekyll/jekyll:latest jekyll s --watch --drafts --incremental  --destination /tmp --unpublished
:: docker run --platform linux --name columns -d -p 4000:4000 --entrypoint jekyll wcshub.azurecr.io/columns:20180723-jekyll-3.8.1 s --watch --drafts --incremental --source /home/source --destination /tmp --unpublished

:: docker run --name columns -d -p 4000:4000 --entrypoint jekyll andrew0928/columns:20180723-jekyll-3.8.1 s --watch --drafts --incremental --source /home/source --destination /tmp --unpublished





:: start command
docker run --name columns -d -v %CD%:/srv/source -p 4000:4000 jekyll/jekyll:3.8.1 ping 127.0.0.1

: jekyll s --watch --unpublished --trace --incremental --draft

:: watch 
docker logs -t -f columns


:: reload command
docker exec -t -i -w /srv/source columns cp -Ru . ../jekyll
cp -Rfu /srv/source/* /srv/jekyll/



cp -rfu /srv/source /tmp
chmod -R 777 /tmp/source
jekyll s --watch --unpublished --trace --incremental --draft --future