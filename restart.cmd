cls
:start
docker restart columns

:wait
docker logs columns -t
@echo --
@choice /T 5 /D N /C YN /M "Press Y for re-generate web site."
if %ERRORLEVEL% EQU 1 goto start
goto wait