cls
docker restart columns

:loop
docker logs columns -t
sleep 5
goto loop