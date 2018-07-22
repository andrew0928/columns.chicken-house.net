SET CONTAINER_NAME=demo
SET IMAGE_TAG=jekyll-3.8.1

docker build -t andrew0928/columns:%IMAGE_TAG% .
docker run --name %CONTAINER_NAME% -d -p 4000:4000 andrew0928/columns:%IMAGE_TAG%

docker exec -w /home         %CONTAINER_NAME% git clone https://github.com/andrew0928/columns.chicken-house.net columns
docker exec -w /home         %CONTAINER_NAME% chmod 777 columns
docker exec -w /home/columns %CONTAINER_NAME% git checkout draft
docker exec -w /home/columns %CONTAINER_NAME% git pull --all
docker exec -w /home/columns -i -t  %CONTAINER_NAME% jekyll s --watch --drafts --incremental --destination /tmp --unpublished