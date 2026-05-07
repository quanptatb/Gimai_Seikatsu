$ErrorActionPreference = 'Stop'
$vol16 = "c:\Users\Cua\Desktop\proj\Gimai_Seikatsu\Vol16"
$templateFile = "c:\Users\Cua\Desktop\proj\Gimai_Seikatsu\Vol15\Gimai15_C1.html"

# Read template
$tpl = Get-Content $templateFile -Raw -Encoding UTF8

# Extract CSS block (between <style> and </style>)
if ($tpl -match '(?s)(<style>.*?</style>)') { $cssBlock = $Matches[1] } else { throw "CSS not found" }

# Extract theme init script
$themeInit = '<script>(function(){var t=localStorage.getItem(''gimai-theme'');if(t&&t!==''default'')document.body.classList.add(''theme-''+t);})()</script>'

# Extract first JS block (scroll, nav, word count)
if ($tpl -match '(?s)(<script>\s*\(function\(\)\s*\{\s*// .{1,30}Scroll Progress.*?</script>)') { $jsBlock1 = $Matches[1] } else { throw "JS1 not found" }

# Extract theme picker JS block
if ($tpl -match '(?s)(<script>\s*\(function\(\)\s*\{\s*var themes.*?</script>)') { $jsBlock2 = $Matches[1] } else { throw "JS2 not found" }

# Define file order for navigation
$files = @(
    @{ file="gimai_seikatsu_v16_prolog_vi.html"; title="Gimai Seikatsu Volume 16 - M&#7903; &#273;&#7847;u"; prev="../Vol15/Gimai15_Epi.html"; next="gimai_seikatsu_v16_c1_vi.html" },
    @{ file="gimai_seikatsu_v16_c1_vi.html"; title="Gimai Seikatsu Volume 16 - Ch&#432;&#417;ng 1"; prev="gimai_seikatsu_v16_prolog_vi.html"; next="gimai_seikatsu_v16_c2_vi.html" },
    @{ file="gimai_seikatsu_v16_c2_vi.html"; title="Gimai Seikatsu Volume 16 - Ch&#432;&#417;ng 2"; prev="gimai_seikatsu_v16_c1_vi.html"; next="gimai_seikatsu_v16_OpenC3_vi.html" },
    @{ file="gimai_seikatsu_v16_OpenC3_vi.html"; title="Gimai Seikatsu Volume 16 - Ch&#432;&#417;ng &#273;&#7879;m"; prev="gimai_seikatsu_v16_c2_vi.html"; next="gimai_seikatsu_v16_c3_vi.html" },
    @{ file="gimai_seikatsu_v16_c3_vi.html"; title="Gimai Seikatsu Volume 16 - Ch&#432;&#417;ng 3"; prev="gimai_seikatsu_v16_OpenC3_vi.html"; next="gimai_seikatsu_v16_c4_vi.html" },
    @{ file="gimai_seikatsu_v16_c4_vi.html"; title="Gimai Seikatsu Volume 16 - Ch&#432;&#417;ng 4"; prev="gimai_seikatsu_v16_c3_vi.html"; next="gimai_seikatsu_v16_c5_vi.html" },
    @{ file="gimai_seikatsu_v16_c5_vi.html"; title="Gimai Seikatsu Volume 16 - Ch&#432;&#417;ng 5"; prev="gimai_seikatsu_v16_c4_vi.html"; next="" }
)

foreach ($f in $files) {
    $path = Join-Path $vol16 $f.file
    if (-not (Test-Path $path)) { Write-Host "SKIP: $($f.file) not found"; continue }

    $raw = Get-Content $path -Raw -Encoding UTF8

    # Build nav links
    $prevLink = if ($f.prev) { "        <a href=`"$($f.prev)`">&larr; Ch&#432;&#417;ng tr&#432;&#7899;c</a>" } else { "        <span class=`"nav-disabled`">&larr; Ch&#432;&#417;ng tr&#432;&#7899;c</span>" }
    $nextLink = if ($f.next) { "        <a href=`"$($f.next)`">Ch&#432;&#417;ng sau &rarr;</a>" } else { "        <span class=`"nav-disabled`">Ch&#432;&#417;ng sau &rarr;</span>" }

    $nav = @"
    <div class="chapter-nav">
$prevLink
        <a href="../index.html">Trang ch&#237;nh</a>
$nextLink
    </div>
"@

    $html = @"
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Noto+Serif:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
    <title>$($f.title)</title>
    $cssBlock
</head>
<body>
$themeInit

$nav

$raw

$nav

    $jsBlock1

    $jsBlock2
</body>
</html>
"@

    [System.IO.File]::WriteAllText($path, $html, [System.Text.UTF8Encoding]::new($false))
    Write-Host "OK: $($f.file)"
}

Write-Host "`nDone! All Vol16 files synchronized."
