: call jekyll s --watch --unpublished --future --drafts
docker run -d --name columns --platform linux -v %CD%:/srv/jekyll -p 4000:4000 jekyll/jekyll:2.4.0
