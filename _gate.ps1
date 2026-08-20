$expected = $env:RELEASE_TAG -replace '^v', ''

$sources = [ordered]@{
  'dday_controls_common.py' = 'APP_VERSION\s*=\s*"([\d.]+)"'
  'installer.iss'           = '#define AppVersion\s+"([\d.]+)"'
  'build_all.bat'           = 'Setup ([\d.]+)\.exe'
  'README.md'               = '\*\*Version:\*\* ([\d.]+)'
}

$mismatched = $false
foreach ($file in $sources.Keys) {
  $hit = Select-String -Path $file -Pattern $sources[$file] | Select-Object -First 1
  if (-not $hit) {
    Write-Host "::error file=$file::no version string found"
    $mismatched = $true
    continue
  }

  $found = $hit.Matches[0].Groups[1].Value
  if ($found -ne $expected) {
    Write-Host "::error file=$file::states $found but the tag is $env:RELEASE_TAG"
    $mismatched = $true
  } else {
    Write-Host "$file -> $found"
  }
}

if ($mismatched) { exit 1 }
