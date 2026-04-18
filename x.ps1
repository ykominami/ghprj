$yaml = @"
name: app
port: 8080
"@

$obj = $yaml | ConvertFrom-Yaml

$obj.name   # app
$obj.port   # 8080