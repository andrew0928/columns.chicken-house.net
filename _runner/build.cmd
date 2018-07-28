SET CONTAINER_NAME=columns
SET IMAGE_TAG=20180723-jekyll-3.8.1


docker rm -f %CONTAINER_NAME%

: can build under windows container, but can not push (don't know why)
docker build -t andrew0928/columns:%IMAGE_TAG% -t wcshub.azurecr.io/columns:%IMAGE_TAG% --build-arg GIT_URL=https://github.com/andrew0928/columns.chicken-house.net --build-arg GIT_BRANCH=develop .

: before push, need to switch to linux container

: docker push wcshub.azurecr.io/columns:%IMAGE_TAG%

: docker run --name %CONTAINER_NAME% -d -p 4000:4000 wcshub.azurecr.io/columns:%IMAGE_TAG%


: docker run --name %CONTAINER_NAME% -d -p 4000:4000 --entrypoint jekyll andrew0928/columns:%IMAGE_TAG%  s --watch --drafts --incremental --source /home/source --destination /tmp --unpublished



: docker exec -w /home         %CONTAINER_NAME% git clone https://github.com/andrew0928/columns.chicken-house.net columns
: docker exec -w /home         %CONTAINER_NAME% chmod 777 columns

: pause

: repeat run this command
: docker exec -w /home/source %CONTAINER_NAME% rm -f .jekyll-metadata
: docker exec -w /home/source %CONTAINER_NAME% git pull origin develop
: docker exec -w /home/source %CONTAINER_NAME% chmod 777 .jekyll-metadata
: docker exec -w /home/source %CONTAINER_NAME% git checkout draft


: pause

: docker exec -w /home/source %CONTAINER_NAME% git pull --all
: docker exec -w /home/source %CONTAINER_NAME% chmod 777 .jekyll-metadata
: docker exec -w /home/source -i -t  %CONTAINER_NAME% jekyll s --watch --drafts --incremental --source /home/source --destination /tmp --unpublished
