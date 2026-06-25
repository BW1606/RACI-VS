# Generates AppFiles.wxs for WiX 4 from the PyInstaller output directory.
# Run after build.bat, before wix build.
param(
    [string]$Source = "dist\RACI-VS",
    [string]$Output = "AppFiles.wxs"
)

$absSource = (Resolve-Path $Source).Path.TrimEnd('\')

function SafeId([string]$prefix, [string]$rel) {
    $safe = $rel.ToLower() -replace '[^a-z0-9]', '_' -replace '_+', '_' -replace '^_|_$', ''
    return "${prefix}_${safe}"
}

$allDirs = @(Get-ChildItem -Path $absSource -Recurse -Directory | Sort-Object FullName | ForEach-Object {
    $rel      = $_.FullName.Substring($absSource.Length + 1)
    $parentFn = $_.Parent.FullName
    [PSCustomObject]@{
        Rel       = $rel
        Name      = $_.Name
        ParentRel = if ($parentFn -eq $absSource) { "" } else { $parentFn.Substring($absSource.Length + 1) }
        Id        = SafeId "D" $rel
    }
})

$allFiles = @(Get-ChildItem -Path $absSource -Recurse -File | ForEach-Object {
    $rel    = $_.FullName.Substring($absSource.Length + 1)
    $dirFn  = $_.DirectoryName
    $dirRel = if ($dirFn -eq $absSource) { "" } else { $dirFn.Substring($absSource.Length + 1) }
    [PSCustomObject]@{
        Rel    = $rel
        Source = "$Source\$rel"
        DirId  = if ($dirRel -eq "") { "INSTALLDIR" } else { SafeId "D" $dirRel }
        CompId = SafeId "C" $rel
        FileId = SafeId "F" $rel
    }
})

$script:xml = [System.Collections.Generic.List[string]]::new()

function AddDirXml([string]$parentRel, [int]$depth) {
    $pad = "    " + ("  " * $depth)
    foreach ($d in @($allDirs | Where-Object { $_.ParentRel -eq $parentRel })) {
        $script:xml.Add("$pad<Directory Id=`"$($d.Id)`" Name=`"$($d.Name)`">")
        AddDirXml $d.Rel ($depth + 1)
        $script:xml.Add("$pad</Directory>")
    }
}

$script:xml.Add('<?xml version="1.0" encoding="UTF-8"?>')
$script:xml.Add('<Wix xmlns="http://wixtoolset.org/schemas/v4/wxs">')
$script:xml.Add('  <Fragment>')
$script:xml.Add('    <DirectoryRef Id="INSTALLDIR">')
AddDirXml "" 0
$script:xml.Add('    </DirectoryRef>')

foreach ($f in $allFiles) {
    $script:xml.Add("    <Component Id=`"$($f.CompId)`" Directory=`"$($f.DirId)`" Guid=`"*`">")
    $script:xml.Add("      <File Id=`"$($f.FileId)`" Source=`"$($f.Source)`" KeyPath=`"yes`" />")
    $script:xml.Add("    </Component>")
}

$script:xml.Add('    <ComponentGroup Id="AppFiles">')
foreach ($f in $allFiles) {
    $script:xml.Add("      <ComponentRef Id=`"$($f.CompId)`" />")
}
$script:xml.Add('    </ComponentGroup>')
$script:xml.Add('  </Fragment>')
$script:xml.Add('</Wix>')

[System.IO.File]::WriteAllLines($Output, $script:xml)
Write-Host "Generated ${Output}: $($allFiles.Count) files across $($allDirs.Count) directories"
