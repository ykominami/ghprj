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

# 基本的な使い方
$hash = Read-YamlFile -Path "links.yaml"

# 2番目の要素にアクセス
$hash["links"][1]
$hash["links"][1]["target"]  # GEMINI.md