$ErrorActionPreference = 'Stop'
# Derive the display from the actual project and the verified vendor manifest.
[xml]$project = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'HEIC2JPG.csproj')
$nugetRoot = if ($env:NUGET_PACKAGES) { $env:NUGET_PACKAGES } else { Join-Path $env:USERPROFILE '.nuget\packages' }
$licenses = @($project.Project.ItemGroup.PackageReference | Where-Object { $_.Include } | ForEach-Object {
    $id = [string]$_.Include; $version = [string]$_.Version
    # Read the license declared by the restored package instead of assuming one.
    $nuspecPath = Join-Path $nugetRoot ("{0}\{1}\{0}.nuspec" -f $id.ToLowerInvariant(), $version.ToLowerInvariant())
    $type = 'UNKNOWN'; $url = "https://www.nuget.org/packages/$id/$version"
    if (Test-Path -LiteralPath $nuspecPath) {
        [xml]$nuspec = Get-Content -Raw -Encoding UTF8 -LiteralPath $nuspecPath
        $license = $nuspec.package.metadata.license
        if ($license -and $license.type -eq 'expression') {
            $type = [string]$license.'#text'; $url = "https://licenses.nuget.org/$type"
        } elseif ($nuspec.package.metadata.licenseUrl) {
            $url = [string]$nuspec.package.metadata.licenseUrl
        }
    } else {
        Write-Warning "License metadata not found for $id $version ($nuspecPath)"
    }
    [ordered]@{ PackageName = $id; Version = $version; LicenseUrl = $url; LicenseType = $type }
})
$manifest = Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot 'wwwroot/vendor-manifest.json') | ConvertFrom-Json
$licenses += @($manifest.packages | ForEach-Object {
    [ordered]@{ PackageName = $_.name; Version = $_.version; LicenseUrl = $_.licenseUrl; LicenseType = $_.license }
})
$json = ConvertTo-Json -InputObject $licenses -Depth 4
$encoding = New-Object System.Text.UTF8Encoding($false)
[IO.File]::WriteAllText((Join-Path $PSScriptRoot 'wwwroot/licenses.json'), $json + "`n", $encoding)
Write-Host "Generated licenses.json with $($licenses.Count) licenses."