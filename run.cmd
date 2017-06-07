: call jekyll s --watch --unpublished --future --drafts
docker run --name columns -d -v %CD%:/srv/jekyll -it -p 4000:4000 jekyll/jekyll:2.4.0 