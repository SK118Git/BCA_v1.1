# make_help.ps1
Get-Content $args[0].trim() |
  Select-String '^[a-zA-Z_-]+:.*?## .*$$' |
  Sort-Object |
  ForEach-Object {
    $parts = $_ -split ':.*?## '
    Write-Host ('  ' + $parts[0].PadRight(15) + $parts[1]) -ForegroundColor Cyan
  }
