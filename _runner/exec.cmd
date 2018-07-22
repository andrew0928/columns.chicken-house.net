SET CONTAINER_NAME=demo

docker build -t jekyll:test .
docker run --name %CONTAINER_NAME% -d -p 4000:4000 jekyll:test



docker exec -w /home         %CONTAINER_NAME% git clone https://github.com/andrew0928/columns.chicken-house.net columns
docker exec -w /home         %CONTAINER_NAME% chmod 777 columns
docker exec -w /home/columns %CONTAINER_NAME% git co draft
docker exec -w /home/columns %CONTAINER_NAME% git pull --all
docker exec -w /home/columns %CONTAINER_NAME% -i -t b9 jekyll s --watch --drafts --incremental --destination /tmp --unpublished