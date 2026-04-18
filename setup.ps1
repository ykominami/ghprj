# setup.ps1
# Install-Module powershell-yaml
param(
    [string]$Config = "links.yaml",
    [switch]$Force
)
Import-Module powershell-yaml

function Expand-Home($path) {
    return $path -replace "^~", $HOME
}

function Load-Yaml {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Path
    )
    # PowerShell 7以降
    # return ConvertFrom-Yaml (Get-Content $file -Raw)
    $content = Get-Content -Path $Path -Raw
    # return ConvertFrom-Yaml $content
    return ConvertFrom-Yaml $content
}
function Read-YamlFile {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Path
    )

    # パスの存在確認
    if (-not (Test-Path $Path)) {
        throw "File not found: $Path"
    }

    # 拡張子確認
    if ($Path -notmatch '\.(yaml|yml)$') {
        throw "Not a YAML file: $Path"
    }

    Import-Module powershell-yaml -ErrorAction Stop

    $content = Get-Content -Path $Path -Raw -Encoding UTF8
    return ConvertFrom-Yaml $content
}

$hash = Load-Yaml -Path $Config
$hash.links

# $c = Get-Content $Config -Raw
# Write-output $c
# $hash = ConvertFrom-Yaml (Get-Content "links.yaml" -Raw)
# $hash["links"][1]

# $config = Load-Yaml -Path $Config
# $config['links'] | Format-Table
# $config.links | ConvertTo-Json
# Write-Output $config
# $config.GetEnumerator() | Format-Table -AutoSize
# $config.links
# Write-Output "--"

foreach ($item in $hash.links) {

    $targetPath = Expand-Home $item.target
    $target = (Resolve-Path -LiteralPath $targetPath).Path
    $link   = Expand-Home $item.link

    Write-Host "Link: $link -> $target"

    if (Test-Path $link) {
        if ($Force) {
            Remove-Item $link -Force -Recurse
        } else {
            Write-Host "  skip (exists)"
            continue
        }
    }

    New-Item -ItemType SymbolicLink -Path $link -Target $target | Out-Null
}