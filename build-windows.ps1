param(
    [string]$ToolchainRoot = "C:\Program Files\Microsoft Visual Studio\2022\BuildTools",
    [string]$BuildDir = "$env:TEMP\VSP-Chinese-build",
    [string]$OutputDir = "$PSScriptRoot\dist\OpenVSP-3.51.2-zh-CN-win64",
    [ValidateRange(1, 8)][int]$Jobs = 1
)

$ErrorActionPreference = "Stop"

$cmake = Join-Path $ToolchainRoot "Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe"
if (-not (Test-Path -LiteralPath $cmake)) {
    throw "未找到 Visual Studio CMake: $cmake"
}

$source = Join-Path $PSScriptRoot "source\OpenVSP"
$superProject = Join-Path $source "SuperProject"
$translation = Join-Path $PSScriptRoot "translations\zh-CN.json"
foreach ($path in @($source, $superProject, $translation)) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "缺少必需路径: $path"
    }
}
$installDir = Join-Path $BuildDir "install"

& $cmake -S $superProject -B $BuildDir -G "Visual Studio 17 2022" -A x64 `
    -DCMAKE_INSTALL_PREFIX=$installDir `
    -DVSP_NO_DOC=ON -DVSP_NO_PYDOC=ON -DVSP_NO_HELP=OFF
if ($LASTEXITCODE) { exit $LASTEXITCODE }

& $cmake --build $BuildDir --config Release --parallel $Jobs
if ($LASTEXITCODE) { exit $LASTEXITCODE }

$innerBuild = Join-Path $BuildDir "OpenVSP-prefix\src\OpenVSP-build"
& $cmake --install $innerBuild --config Release --prefix $installDir
if ($LASTEXITCODE) { exit $LASTEXITCODE }

New-Item -ItemType Directory -Force $OutputDir | Out-Null
Copy-Item (Join-Path $installDir "*") $OutputDir -Recurse -Force
$translationDir = Join-Path $OutputDir "translations"
New-Item -ItemType Directory -Force $translationDir | Out-Null
Copy-Item $translation $translationDir -Force
Copy-Item (Join-Path $PSScriptRoot "LICENSE") $OutputDir -Force
Copy-Item (Join-Path $PSScriptRoot "NOTICE.md") $OutputDir -Force
Copy-Item (Join-Path $PSScriptRoot "README.md") $OutputDir -Force

Write-Host "汉化版已生成: $(Join-Path $OutputDir 'vsp.exe')"
