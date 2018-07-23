SET CONTAINER_NAME=demo
SET IMAGE_TAG=jekyll-3.8.1

: can build under windows container, but can not push (don't know why)
docker build -t andrew0928/columns:%IMAGE_TAG% .

: before push, need to switch to linux container
docker push andrew0928/columns:jekyll-3.8.1

docker run --name %CONTAINER_NAME% -d -p 4000:4000 andrew0928/columns:%IMAGE_TAG%
: docker run --name %CONTAINER_NAME% -d -p 4000:4000 --entrypoint jekyll andrew0928/columns:%IMAGE_TAG%  s --watch --drafts --incremental --source /home/columns --destination /tmp --unpublished



: docker exec -w /home         %CONTAINER_NAME% git clone https://github.com/andrew0928/columns.chicken-house.net columns
: docker exec -w /home         %CONTAINER_NAME% chmod 777 columns

pause

: repeat run this command
: docker exec -w /home/columns %CONTAINER_NAME% rm -f .jekyll-metadata
docker exec -w /home/columns %CONTAINER_NAME% git pull origin develop
: docker exec -w /home/columns %CONTAINER_NAME% chmod 777 .jekyll-metadata
: docker exec -w /home/columns %CONTAINER_NAME% git checkout draft


pause

: docker exec -w /home/columns %CONTAINER_NAME% git pull --all
: docker exec -w /home/columns %CONTAINER_NAME% chmod 777 .jekyll-metadata
docker exec -w /home/columns -i -t  %CONTAINER_NAME% jekyll s --watch --drafts --incremental --source /home/columns --destination /tmp --unpublished
