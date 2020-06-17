@ECHO OFF

IF NOT EXIST "..\app\logs\" MD "..\app\logs\"
ECHO #Edit this file>>"..\app\pylib\ad_settings.py"
ECHO Install requirements for the app? (y/n)
SET /P C=
IF %C%==y GOTO y
IF %C%==Y (GOTO Y) ELSE GOTO n

:Y
PYTHON -m pip install python_ldap-3.2.0-cp37-cp37m-win_amd64.whl
PYTHON -m pip install -r requirements.txt
ECHO Installed all requirements.
PAUSE
EXIT


:n
ECHO No changes will be made.
PAUSE
EXIT
