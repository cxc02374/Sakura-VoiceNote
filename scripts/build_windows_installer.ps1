param(
  [string]$Python = "python",
  [string]$AppVersion = "0.1.0",
  [switch]$SkipModelDownload
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$BuildStamp = Get-Date -Format "yyyyMMdd_HHmmss"
$DistPath = Join-Path $ProjectRoot ("dist\windows\" + $BuildStamp)
$WorkPath = Join-Path $ProjectRoot ("build\windows\" + $BuildStamp)
$SpecPath = Join-Path $ProjectRoot ("build\windows\" + $BuildStamp)
$RequirementsBuild = Join-Path $ProjectRoot "requirements-build.txt"
$EntryScript = Join-Path $ProjectRoot "run_voicenote.py"
$EnvTemplate = Join-Path $ProjectRoot ".env.template"
$ReadmePath = Join-Path $ProjectRoot "README.md"
$ReadmeTextPath = Join-Path $ProjectRoot "README.txt"
$AppIconPath = Join-Path $ProjectRoot "assets\voicenote_icon.ico"
$InstallerScript = Join-Path $ProjectRoot "installer\SakuraVoiceNote.iss"
$ModelDir = Join-Path $ProjectRoot "resources\models\faster-whisper-tiny"
$DistAppDir = Join-Path $DistPath "SakuraVoiceNote"

if (-not (Test-Path $EntryScript)) {
  throw "エントリースクリプトが見つかりません: $EntryScript"
}

Write-Host "[Sakura VoiceNote] Installing build dependencies..."
& $Python -m pip install -r $RequirementsBuild
if ($LASTEXITCODE -ne 0) {
  throw "pip install failed with exit code $LASTEXITCODE"
}

if (-not $SkipModelDownload) {
  Write-Host "[Sakura VoiceNote] Prefetching Whisper tiny model..."
  New-Item -ItemType Directory -Force -Path $ModelDir | Out-Null
  $DownloadCode = @"
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='Systran/faster-whisper-tiny',
    local_dir=r'$($ModelDir.Replace("\", "\\"))',
    local_dir_use_symlinks=False
)
print('model downloaded')
"@
  & $Python -c $DownloadCode
  if ($LASTEXITCODE -ne 0) {
    throw "Model prefetch failed with exit code $LASTEXITCODE"
  }
}

Write-Host "[Sakura VoiceNote] Building Windows executable..."
New-Item -ItemType Directory -Force -Path $DistPath | Out-Null
New-Item -ItemType Directory -Force -Path $WorkPath | Out-Null
New-Item -ItemType Directory -Force -Path $SpecPath | Out-Null

$PyInstallerArgs = @(
  "-m", "PyInstaller",
  "--noconfirm",
  "--clean",
  "--name", "SakuraVoiceNote",
  "--console",
  "--distpath", $DistPath,
  "--workpath", $WorkPath,
  "--specpath", $SpecPath,
  "--collect-all", "faster_whisper",
  "--collect-all", "ctranslate2",
  "--collect-all", "tokenizers",
  "--collect-all", "av",
  "--add-data", "$EnvTemplate;.",
  "--add-data", "$ReadmePath;."
)

if (Test-Path $ReadmeTextPath) {
  $PyInstallerArgs += @("--add-data", "$ReadmeTextPath;.")
}

if (Test-Path $ModelDir) {
  $PyInstallerArgs += @("--add-data", "$ModelDir;resources/models/faster-whisper-tiny")
}

if (Test-Path $AppIconPath) {
  $PyInstallerArgs += @("--icon", $AppIconPath)
}

$PyInstallerArgs += $EntryScript

& $Python @PyInstallerArgs
if ($LASTEXITCODE -ne 0) {
  throw "PyInstaller build failed with exit code $LASTEXITCODE"
}

if (Test-Path $EnvTemplate) {
  Copy-Item -Path $EnvTemplate -Destination (Join-Path $DistAppDir '.env.template') -Force
}

if (Test-Path $ReadmePath) {
  Copy-Item -Path $ReadmePath -Destination (Join-Path $DistAppDir 'README.md') -Force
}

if (Test-Path $ReadmeTextPath) {
  Copy-Item -Path $ReadmeTextPath -Destination (Join-Path $DistAppDir 'README.txt') -Force
}

$Iscc = Join-Path ${env:ProgramFiles(x86)} "Inno Setup 6\ISCC.exe"
if (-not (Test-Path $Iscc)) {
  Write-Warning "Inno Setup (ISCC.exe) が見つかりません。EXE配布のみ完成: $DistAppDir"
  Write-Host "[Sakura VoiceNote] Build completed (no installer): $DistAppDir"
  exit 0
}

Write-Host "[Sakura VoiceNote] Building installer (.exe)..."
& $Iscc "/DAppVersion=$AppVersion" "/DSourceDir=$DistAppDir" "/DProjectRoot=$ProjectRoot" "/DInstallerIconFile=$AppIconPath" $InstallerScript
if ($LASTEXITCODE -ne 0) {
  throw "Installer build failed with exit code $LASTEXITCODE"
}

Write-Host "[Sakura VoiceNote] Installer build completed."
Write-Host "- App folder: $DistAppDir"
Write-Host "- Installer output: $(Join-Path $ProjectRoot 'dist\installer')"
