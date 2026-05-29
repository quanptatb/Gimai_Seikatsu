#!/usr/bin/env python3
"""
Convert Kumo Desu ga, Nani ka? EPUB to styled HTML chapters.
"""

import zipfile
import re
import os
import html as html_mod
import json

EPUB_PATH = r'c:\Users\Cua\Desktop\proj\Gimai_Seikatsu\kumo\259.epub'
OUTPUT_DIR = r'c:\Users\Cua\Desktop\proj\Gimai_Seikatsu\kumo'

def parse_toc(z):
    """Parse toc.ncx with regex to avoid XML namespace issues."""
    toc = z.read('toc.ncx').decode('utf-8')
    chapters = []
    for m in re.finditer(r'<navPoint[^>]*>.*?<text>(.*?)</text>.*?<content\s+src="([^"]+)"', toc, re.DOTALL):
        title = m.group(1).strip()
        src = m.group(2).strip()
        if src != 'index.html' and title:
            chapters.append({'title': title, 'src': src})
    return chapters

def parse_spine(z):
    """Parse content.opf with regex."""
    opf = z.read('content.opf').decode('utf-8')
    
    # Build id->href map
    id_to_href = {}
    for m in re.finditer(r'<item\s+[^>]*id="([^"]+)"[^>]*href="([^"]+)"', opf):
        item_id, href = m.group(1), m.group(2)
        if href.endswith('.html') or href.endswith('.xhtml'):
            id_to_href[item_id] = href
    # Also match reversed attribute order
    for m in re.finditer(r'<item\s+[^>]*href="([^"]+)"[^>]*id="([^"]+)"', opf):
        href, item_id = m.group(1), m.group(2)
        if href.endswith('.html') or href.endswith('.xhtml'):
            id_to_href[item_id] = href
    
    # Get spine order
    spine = []
    for m in re.finditer(r'<itemref\s+idref="([^"]+)"', opf):
        idref = m.group(1)
        if idref in id_to_href:
            spine.append(id_to_href[idref])
    
    return spine

def extract_body_content(html_content):
    """Extract text content from chapter HTML."""
    body_match = re.search(r'<body[^>]*>(.*?)</body>', html_content, re.DOTALL | re.IGNORECASE)
    body = body_match.group(1) if body_match else html_content
    
    # Remove script/style
    body = re.sub(r'<script[^>]*>.*?</script>', '', body, flags=re.DOTALL | re.IGNORECASE)
    body = re.sub(r'<style[^>]*>.*?</style>', '', body, flags=re.DOTALL | re.IGNORECASE)
    # Remove nav
    body = re.sub(r'<div[^>]*class="[^"]*chapter-nav[^"]*"[^>]*>.*?</div>', '', body, flags=re.DOTALL | re.IGNORECASE)
    
    elements = []
    
    # Match paragraphs, headers, hr, img
    pattern = r'<(p|h[1-4])(?:\s[^>]*)?>(.+?)</\1>|<hr\s*/?>'
    
    for m in re.finditer(pattern, body, re.DOTALL | re.IGNORECASE):
        full = m.group(0)
        
        if full.strip().lower().startswith('<hr'):
            elements.append({'type': 'hr'})
            continue
        
        tag = m.group(1).lower()
        content = m.group(2).strip()
        
        # Handle images inside paragraphs
        img_matches = re.findall(r'<img[^>]+src="([^"]+)"[^>]*>', content, re.IGNORECASE)
        if img_matches:
            for img_src in img_matches:
                elements.append({'type': 'img', 'src': img_src})
            # Remove img tags and check remaining
            remaining = re.sub(r'<a[^>]*>\s*<img[^>]*>\s*</a>', '', content)
            remaining = re.sub(r'<img[^>]*>', '', remaining)
            remaining = re.sub(r'<a[^>]*>\s*</a>', '', remaining)
            remaining = re.sub(r'<[^>]+>', '', remaining).strip()
            if remaining:
                elements.append({'type': tag, 'content': content})
            continue
        
        # Keep <b>, <i>, <em>, <strong>, <br> but remove other tags
        clean = re.sub(r'<(?!/?(?:b|i|em|strong|br)\b)[^>]+>', '', content)
        clean = clean.strip()
        
        if clean:
            elements.append({'type': tag, 'content': clean})
    
    return elements

def generate_chapter_html(elements, title, prev_link, next_link):
    """Generate styled HTML for a chapter."""
    content_parts = []
    for elem in elements:
        if elem['type'] == 'hr':
            content_parts.append('<hr>')
        elif elem['type'] == 'img':
            content_parts.append(f'<p class="illustration"><img src="{elem["src"]}" alt="minh họa" loading="lazy"></p>')
        elif elem['type'] in ('h1', 'h2', 'h3', 'h4'):
            content_parts.append(f'<{elem["type"]}>{elem["content"]}</{elem["type"]}>')
        else:
            content_parts.append(f'<p>{elem["content"]}</p>')
    
    body_content = '\n\n'.join(content_parts)
    
    prev_html = f'<a href="{prev_link}">&larr; Chương trước</a>' if prev_link else '<span class="nav-disabled">&larr; Chương trước</span>'
    next_html = f'<a href="{next_link}">Chương sau &rarr;</a>' if next_link else '<span class="nav-disabled">Chương sau &rarr;</span>'
    
    escaped_title = html_mod.escape(title)
    
    return f'''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Noto+Serif:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../kumo-style.css">
    <title>Kumo Desu ga, Nani ka? — {escaped_title}</title>
</head>
<body>

    <div class="chapter-nav">
        {prev_html}
        <a href="../index.html">Trang chính</a>
        {next_html}
    </div>

<h1>{escaped_title}</h1>

{body_content}

    <div class="chapter-nav bottom-nav">
        {prev_html}
        <a href="../index.html">Trang chính</a>
        {next_html}
    </div>

<script src="../kumo-script.js"></script>
</body>
</html>'''

def smart_group(chapters):
    """Group chapters into arcs."""
    arcs = []
    current_name = None
    current_chapters = []
    
    arc_ranges = [
        (1, 10, 'Khởi Đầu'),
        (11, 30, 'Mê Cung Hạ Tầng'),
        (31, 60, 'Mê Cung Trung Tầng'),
        (61, 100, 'Mê Cung Thượng Tầng'),
        (101, 140, 'Ra Khỏi Mê Cung'),
        (141, 180, 'Ma Vương Trỗi Dậy'),
        (181, 220, 'Chuẩn Bị Chiến Tranh'),
        (221, 260, 'Đại Chiến'),
        (261, 300, 'Cuộc Chiến Ở Làng Elf'),
        (301, 330, 'Hồi Kết'),
    ]
    
    def get_arc(num):
        for s, e, name in arc_ranges:
            if s <= num <= e:
                return name
        return None
    
    special_group = []
    
    for ch in chapters:
        title = ch['title']
        
        # Skip illustration volumes
        if re.match(r'^Tập \d+', title):
            special_group.append(ch)
            continue
        
        # Extract chapter number
        m = re.search(r'[Cc]h(?:ương|ap|uong)\s*(\d+)', title)
        if m:
            num = int(m.group(1))
            arc_name = get_arc(num)
        else:
            arc_name = None
        
        if arc_name and arc_name != current_name:
            if current_chapters:
                arcs.append({'name': current_name or 'Ngoại Truyện', 'chapters': current_chapters})
            current_name = arc_name
            current_chapters = [ch]
        else:
            if not arc_name and not current_name:
                current_name = 'Ngoại Truyện'
            current_chapters.append(ch)
    
    if current_chapters:
        arcs.append({'name': current_name or 'Ngoại Truyện', 'chapters': current_chapters})
    
    if special_group:
        arcs.insert(0, {'name': 'Minh Họa Light Novel', 'chapters': special_group})
    
    return arcs

def main():
    z = zipfile.ZipFile(EPUB_PATH, 'r')
    
    toc_chapters = parse_toc(z)
    spine = parse_spine(z)
    
    print(f"TOC: {len(toc_chapters)} entries, Spine: {len(spine)} items")
    
    # Build title map from TOC
    title_map = {}
    for ch in toc_chapters:
        title_map[ch['src']] = ch['title']
        # Also map split base
        base = re.sub(r'_split_\d+\.html$', '', ch['src'])
        if base != ch['src']:
            if base not in title_map:
                title_map[base] = ch['title']
    
    # Use spine order, skip titlepage/index
    ordered = []
    for src in spine:
        if src in ('titlepage.xhtml', 'index.html'):
            continue
        title = title_map.get(src, '')
        if not title:
            base = re.sub(r'_split_\d+\.html$', '', src)
            title = title_map.get(base, '')
        if not title:
            name = re.sub(r'^c\d+-', '', os.path.splitext(src)[0])
            title = name.replace('-', ' ').replace('_', ' ').strip().title()
        ordered.append({'src': src, 'title': title})
    
    # Merge split files
    merged = []
    i = 0
    while i < len(ordered):
        ch = ordered[i]
        src = ch['src']
        
        if '_split_' in src:
            base = re.sub(r'_split_\d+\.html$', '', src)
            splits = [ch]
            j = i + 1
            while j < len(ordered) and re.sub(r'_split_\d+\.html$', '', ordered[j]['src']) == base:
                splits.append(ordered[j])
                j += 1
            
            parts = []
            for s in splits:
                try:
                    parts.append(z.read(s['src']).decode('utf-8'))
                except:
                    pass
            
            merged.append({
                'src': splits[0]['src'],
                'title': splits[0]['title'],
                'raw_parts': parts
            })
            i = j
        else:
            try:
                raw = z.read(src).decode('utf-8')
                ch['raw_parts'] = [raw]
                merged.append(ch)
            except:
                i += 1
                continue
            i += 1
    
    print(f"After merge: {len(merged)} chapters")
    
    # Generate output filenames
    for idx, ch in enumerate(merged):
        safe = re.sub(r'[^\w\-]', '_', ch['src'].replace('.html', '').replace('_split_000', ''))
        safe = re.sub(r'_+', '_', safe).strip('_')
        ch['output_file'] = f'{safe}.html'
        ch['idx'] = idx
    
    # Create chapters dir
    chapters_dir = os.path.join(OUTPUT_DIR, 'chapters')
    os.makedirs(chapters_dir, exist_ok=True)
    
    # Write chapter files
    for idx, ch in enumerate(merged):
        elements = []
        for raw in ch.get('raw_parts', []):
            elements.extend(extract_body_content(raw))
        
        if not elements:
            elements = [{'type': 'p', 'content': '<i>(Nội dung chương này chỉ gồm hình ảnh minh họa)</i>'}]
        
        prev_link = merged[idx-1]['output_file'] if idx > 0 else None
        next_link = merged[idx+1]['output_file'] if idx < len(merged)-1 else None
        
        chapter_html = generate_chapter_html(elements, ch['title'], prev_link, next_link)
        
        path = os.path.join(chapters_dir, ch['output_file'])
        with open(path, 'w', encoding='utf-8') as f:
            f.write(chapter_html)
        
        if (idx + 1) % 20 == 0:
            print(f"  Written {idx+1}/{len(merged)} chapters...")
    
    print(f"Written {len(merged)} chapter files")
    
    # Group into arcs
    arc_input = [{'title': ch['title'], 'src': ch['src'], 'file': ch['output_file']} for ch in merged]
    arcs = smart_group(arc_input)
    
    print(f"\nOrganized into {len(arcs)} arcs:")
    for arc in arcs:
        print(f"  {arc['name']}: {len(arc['chapters'])} chapters")
    
    # Save arc data
    with open(os.path.join(OUTPUT_DIR, 'arc_data.json'), 'w', encoding='utf-8') as f:
        json.dump(arcs, f, ensure_ascii=False, indent=2)
    
    print("\nDone!")
    z.close()

if __name__ == '__main__':
    main()
