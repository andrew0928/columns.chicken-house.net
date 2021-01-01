SET CONTAINER_NAME=columns
SET IMAGE_TAG=20180723-jekyll-3.8.1


::: launch daemon
docker run --name columns -v %CD%:/home/columns -d -p 4000:4000 -v %CD%:/home/columns andrew0928/columns:20180723-jekyll-3.8.1
start docker logs -t -f columns

::: enter shell, update file(s)
echo "cp -Ru columns/* source"
docker exec -t -i -w /home columns bash
::: cp -Ru columns/* source

::: remove dead containers, use "run as administrator" mode
@REM net stop docker
@REM rd /s /q c:\ProgramData\Docker\containers
@REM net start docker
