$zipfile = "$env:USERPROFILE\Desktop\pycharm_config_work_extract.zip"
Remove-Item $zipfile -ErrorAction SilentlyContinue

Add-Type -AssemblyName 'System.IO.Compression.FileSystem'

# Step 1: Create the initial zip from codestyles/
[System.IO.Compression.ZipFile]::CreateFromDirectory(
  "$env:APPDATA\JetBrains\PyCharm2025.1\codestyles",
  $zipfile
)

# Step 2: Add specific XML files to existing zip
$xmlFiles = @(
  "$env:APPDATA\JetBrains\PyCharm2025.1\options\ide.general.xml",
  "$env:APPDATA\JetBrains\PyCharm2025.1\options\editor.xml",
  "$env:APPDATA\JetBrains\PyCharm2025.1\options\project.default.xml",
  "$env:APPDATA\JetBrains\PyCharm2025.1\options\other.xml"
)

$zip = [System.IO.Compression.ZipFile]::Open($zipfile, 'Update')
foreach ($f in $xmlFiles) {
  if (Test-Path $f) {
    [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(
      $zip, $f, "options/" + [System.IO.Path]::GetFileName($f)
    )
  }
}
$zip.Dispose()

Write-Output "✅ Archive created at: $zipfile"
