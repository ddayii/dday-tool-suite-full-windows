$exe = Get-ChildItem installer\*.exe | Select-Object -First 1

# --target creates the tag at this commit when it does not exist yet,
# which is what lets a manual run cut a release.
gh release create $env:RELEASE_TAG $exe.FullName `
  --title $env:RELEASE_TAG `
  --target $env:RELEASE_SHA `
  --generate-notes `
  --draft
