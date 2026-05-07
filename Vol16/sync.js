const fs = require('fs');
const path = require('path');

const vol16 = __dirname;
const tpl = fs.readFileSync(path.join(__dirname, '..', 'Vol15', 'Gimai15_C1.html'), 'utf8');

// Extract CSS
const cssMatch = tpl.match(/<style>[\s\S]*?<\/style>/);
if (!cssMatch) throw new Error('CSS not found');
const css = cssMatch[0];

// Extract JS blocks
const js1Match = tpl.match(/<script>\s*\(function\(\)\s*\{\s*\/\/ ── Scroll[\s\S]*?<\/script>/);
if (!js1Match) throw new Error('JS1 not found');
const js1 = js1Match[0];

const js2Match = tpl.match(/<script>\s*\(function\(\)\s*\{\s*var themes[\s\S]*?<\/script>/);
if (!js2Match) throw new Error('JS2 not found');
const js2 = js2Match[0];

const themeInit = `<script>(function(){var t=localStorage.getItem('gimai-theme');if(t&&t!=='default')document.body.classList.add('theme-'+t);})()</script>`;

const files = [
  { file: 'gimai_seikatsu_v16_prolog_vi.html', title: 'Gimai Seikatsu Volume 16 - Mở đầu', prev: '../Vol15/Gimai15_Epi.html', next: 'gimai_seikatsu_v16_c1_vi.html' },
  { file: 'gimai_seikatsu_v16_c1_vi.html', title: 'Gimai Seikatsu Volume 16 - Chương 1', prev: 'gimai_seikatsu_v16_prolog_vi.html', next: 'gimai_seikatsu_v16_c2_vi.html' },
  { file: 'gimai_seikatsu_v16_c2_vi.html', title: 'Gimai Seikatsu Volume 16 - Chương 2', prev: 'gimai_seikatsu_v16_c1_vi.html', next: 'gimai_seikatsu_v16_OpenC3_vi.html' },
  { file: 'gimai_seikatsu_v16_OpenC3_vi.html', title: 'Gimai Seikatsu Volume 16 - Chương đệm', prev: 'gimai_seikatsu_v16_c2_vi.html', next: 'gimai_seikatsu_v16_c3_vi.html' },
  { file: 'gimai_seikatsu_v16_c3_vi.html', title: 'Gimai Seikatsu Volume 16 - Chương 3', prev: 'gimai_seikatsu_v16_OpenC3_vi.html', next: 'gimai_seikatsu_v16_c4_vi.html' },
  { file: 'gimai_seikatsu_v16_c4_vi.html', title: 'Gimai Seikatsu Volume 16 - Chương 4', prev: 'gimai_seikatsu_v16_c3_vi.html', next: 'gimai_seikatsu_v16_c5_vi.html' },
  { file: 'gimai_seikatsu_v16_c5_vi.html', title: 'Gimai Seikatsu Volume 16 - Chương 5', prev: 'gimai_seikatsu_v16_c4_vi.html', next: '' },
];

for (const f of files) {
  const fp = path.join(vol16, f.file);
  if (!fs.existsSync(fp)) { console.log('SKIP:', f.file); continue; }
  const raw = fs.readFileSync(fp, 'utf8');

  const prevLink = f.prev
    ? `        <a href="${f.prev}">&larr; Chương trước</a>`
    : `        <span class="nav-disabled">&larr; Chương trước</span>`;
  const nextLink = f.next
    ? `        <a href="${f.next}">Chương sau &rarr;</a>`
    : `        <span class="nav-disabled">Chương sau &rarr;</span>`;

  const nav = `    <div class="chapter-nav">
${prevLink}
        <a href="../index.html">Trang chính</a>
${nextLink}
    </div>`;

  const html = `<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Noto+Serif:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
    <title>${f.title}</title>
    ${css}
</head>
<body>
${themeInit}

${nav}

${raw}

${nav}

    ${js1}

    ${js2}
</body>
</html>`;

  fs.writeFileSync(fp, html, 'utf8');
  console.log('OK:', f.file);
}
console.log('\\nDone! All Vol16 files synchronized.');
