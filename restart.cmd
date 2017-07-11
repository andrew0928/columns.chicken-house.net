cls
:start
docker restart columns

:wait
docker logs columns -t --tail 100
@echo --
@choice /T 5 /D N /C YNC /M "Press Y for re-generate web site. (N: do not re-gen, C: cancel looping)"
if %ERRORLEVEL% EQU 1 goto start
if %ERRORLEVEL% EQU 3 goto end
goto wait

:end