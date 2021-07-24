FROM jekyll/jekyll:3.8.1

ENV JEKYLL_ENV=development

ARG GIT_URL
ARG GIT_BRANCH=master

WORKDIR /home

# RUN git clone --branch $GIT_BRANCH $GIT_URL source; chmod 777 source;

# RUN mkdir source; chmod -R 777 source;
# RUN git clone --branch develop https://github.com/andrew0928/columns.chicken-house.net source
COPY . /home/source

# WORKDIR /home/source
# RUN git init; git remote add origin $GIT_URL;
# RUN git pull origin master;


WORKDIR /srv/jekyll


# ENTRYPOINT [ "jekyll", "s", "--watch", "--drafts", "--incremental", "--source", "/home/source", "--destination", "/tmp", "--unpublished" ]
ENTRYPOINT [ "jekyll", "s", "--watch", "--drafts", "--future", "--unpublished", "--source", "/home/source", "--destination", "/tmp" ]
# ENTRYPOINT [ "ping", "127.0.0.1" ]