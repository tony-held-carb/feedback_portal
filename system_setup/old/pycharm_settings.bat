
@echo off
set "SOURCE=%APPDATA%\Roaming\JetBrains\PyCharm2025.1"
set "DEST=%USERPROFILE%\Desktop\pycharm_config_work_extract.zip"

:: Clean up old zip
if exist "%DEST%" del "%DEST%"

:: Create a zip with only key settings
powershell -nologo -noprofile -command ^
  "Add-Type -A 'System.IO.Compression.FileSystem'; ^
   $zipfile = '%DEST%'; ^
   $files = @(
     '%SOURCE%\options\ide.general.xml',
     '%SOURCE%\options\editor.xml',
     '%SOURCE%\options\project.default.xml',
     '%SOURCE%\options\other.xml',
     '%SOURCE%\codestyles'
   ); ^
   [System.IO.Compression.ZipFile]::CreateFromDirectory($files[4], $zipfile); ^
   foreach ($f in $files[0..3]) { ^
     if (Test-Path $f) { ^
       [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile( ^
         [System.IO.Compression.ZipFile]::Open($zipfile, 'Update'), $f, ^
         ('options/' + [System.IO.Path]::GetFileName($f)) ^
       ) ^
     } ^
   }"

echo Done! Archive created at: %DEST%
pause
