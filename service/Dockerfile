# Ruby 3.3.12 / Bundler 2.5.22; pin the multi-platform image digest.
FROM mcr.microsoft.com/devcontainers/ruby:3.3-bookworm@sha256:27a84d7bd892379a888263a1f16d0b071ffdf00a35ee72c36bf3cc177c99726b

# github-pages includes CoffeeScript support, which needs a JavaScript runtime.
RUN apt-get update \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

ENV BUNDLE_FROZEN=true
COPY docs/Gemfile docs/Gemfile.lock /opt/jekyll/
RUN --mount=type=cache,id=columns-jekyll-gems,target=/usr/local/bundle/cache \
    cd /opt/jekyll && bundle install

WORKDIR /usr/src/app
