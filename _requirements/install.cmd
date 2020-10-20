@ECHO OFF
CLS

IF NOT EXIST "..\app\logs\" MD "..\app\logs\"
IF NOT EXIST "..\app\static\uploads\images\cars" MD "..\app\static\uploads\images\cars"
IF NOT EXIST "..\app\static\uploads\images\members" MD "..\app\static\uploads\images\members"
IF NOT EXIST "..\app\static\uploads\images\posts" MD "..\app\static\uploads\images\posts"
ECHO #Edit this file>>"..\app\pylib\ad_settings.py"

ECHO Setup self-signed SSL certificates? (OpenSSL is required for this!) (y/n)
SET /P SSL=
IF %SSL%==y (
    GOTO yssl
    CLS
)
IF %SSL%==n (
    GOTO nssl
    CLS
)

:yssl
ECHO Follow the instructions to setup SSL certificates.
IF NOT EXIST "%PROGRAMFILES%\OpenSSL-Win64" Win64OpenSSL.exe /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /RESARTAPPLICATIONS
PAUSE
"%PROGRAMFILES%\OpenSSL-Win64\bin\OPENSSL" req -x509 -newkey rsa:4096 -nodes -out ..\cert.pem -keyout ..\key.pem -days 365
:nssl
CLS

ECHO Install requirements for the app? (y/n)
SET /P C=
IF %C%==y GOTO pickldap
IF %C%==Y (GOTO Y) ELSE GOTO n

:pickldap
CLS
ECHO Pick which version of python_ldap to use. for Python 3.7x use version 3.2.0 or 3.3.1 and 3.3.1 for Python 3.8.x/3.9.x.
ECHO 1 for: Python 3.7.x with ldap 3.2.0
ECHO 2 for: Python 3.7.x with ldap 3.3.1
ECHO 3 for: Python 3.8.x with ldap 3.3.1
ECHO 4 for: Python 3.9.x with ldap 3.3.1
SET /p LDAP=
IF %LDAP%==1 (
    SET LDAPVER="python_ldap-3.2.0-cp37-cp37m-win_amd64.whl"
    GOTO y
)
IF %LDAP%==2 (
    SET LDAPVER="python_ldap-3.3.1-cp37-cp37m-win_amd64.whl"
    GOTO y
)
IF %LDAP%==3 (
    SET LDAPVER="python_ldap-3.3.1-cp38-cp38-win_amd64.whl"
    GOTO y
)
IF %LDAP%==4 (
    SET LDAPVER="python_ldap-3.3.1-cp39-cp39-win_amd64.whl"
    GOTO y
) ELSE (
    CLS
    ECHO Please pick one of the options.
    GOTO pickldap
)

:Y
CLS
ECHO Setting up VSBuild Tools... Wait for install to finish.
vs_buildtools.exe --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended --wait
PAUSE
PYTHON -m pip install %LDAPVER%
PYTHON -m pip install -r requirements.txt --upgrade
ECHO Installed all requirements.
PAUSE
EXIT

:n
ECHO No changes will be made.
PAUSE
EXIT
