: call jekyll s --watch --unpublished --future --drafts
docker run -v %CD%:/srv/jekyll -it -p 4000:4000 jekyll/jekyll