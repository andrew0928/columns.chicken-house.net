: call jekyll s --watch --unpublished --future --drafts

: using windows container
: docker run -d --name column3 --platform=linux -v %CD%:/srv/jekyll -p 4001:4000 jekyll/jekyll:3.8.1 jekyll s --watch --drafts
: docker logs --tail 100 -t -f column3

: docker run -d --name columns -v %CD%:/srv/jekyll -p 4000:4000 jekyll/jekyll:2.4.0


::::: docker run --name columns -d --platform=linux -v %CD%:/srv/jekyll -p 4000:4000 jekyll/jekyll jekyll s --watch --drafts --incremental  --destination /tmp --unpublished

docker run --name columns -d -p 4000:4000 --entrypoint jekyll andrew0928/columns:20180723-jekyll-3.8.1 s --watch --drafts --incremental --source /home/source --destination /tmp --unpublished
