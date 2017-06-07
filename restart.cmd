cls
:start
docker restart columns

:wait
docker logs columns -t
@choice /T 5 /D N /C YN /M "Press Y for re-generate web site."
: @echo %ERRORLEVEL%
if %ERRORLEVEL% EQU 1 goto start
: @pause
goto wait