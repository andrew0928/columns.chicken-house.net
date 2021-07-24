FROM jekyll/jekyll:3.8.1
ENV JEKYLL_ENV=development

COPY . /home/source
WORKDIR /srv/jekyll

ENTRYPOINT [ "jekyll", "s", "--watch", "--source", "/home/source", "--destination", "/tmp" ]