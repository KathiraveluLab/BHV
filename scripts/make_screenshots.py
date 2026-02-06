#!/usr/bin/env python
"""Run the demo runner, capture output, and render screenshots (PNG) from key sections.

Produces files under `scripts/screenshots/`:
- `initial_and_edit.png` - initial upload + edited upload outputs
- `history.png` - JSON history output
- `diff.png` - unified diff output

This script installs Pillow if missing.
"""
import os
import subprocess
import sys
import textwrap

OUT_DIR = os.path.join(os.path.dirname(__file__), 'screenshots')
os.makedirs(OUT_DIR, exist_ok=True)

def ensure_pillow():
    try:
        from PIL import Image
    except Exception:
        print('Pillow not found, installing...')
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'Pillow'])

def run_demo():
    proc = subprocess.run([sys.executable, 'scripts/demo_run.py'], capture_output=True, text=True)
    return proc.stdout

def render_text_to_png(text, outpath, width=1000, padding=12, title=None):
    from PIL import Image, ImageDraw, ImageFont

    # Try to load a monospace font (Consolas on Windows, DejaVuSansMono otherwise)
    font = None
    title_font = None
    try:
        font = ImageFont.truetype(r'C:\Windows\Fonts\consola.ttf', 14)
    except Exception:
        try:
            font = ImageFont.truetype('DejaVuSansMono.ttf', 14)
        except Exception:
            font = ImageFont.load_default()

    try:
        title_font = ImageFont.truetype(r'C:\Windows\Fonts\consola.ttf', 16)
    except Exception:
        try:
            title_font = ImageFont.truetype('DejaVuSans.ttf', 16)
        except Exception:
            title_font = font

    # estimate char width and line height
    try:
        bbox = font.getbbox('A')
        avg_char_width = bbox[2] - bbox[0]
        line_h = bbox[3] - bbox[1] + 4
    except Exception:
        try:
            size = font.getsize('A')
            avg_char_width = size[0]
            line_h = size[1] + 4
        except Exception:
            avg_char_width = 8
            line_h = 18

    max_chars = max(40, (width - 2 * padding) // max(1, avg_char_width))
    wrapped = []
    for line in text.splitlines():
        wrapped.extend(textwrap.wrap(line, max_chars) or [''])

    # account for title height if present
    title_h = 0
    if title:
        try:
            tbbox = title_font.getbbox(title)
            title_h = tbbox[3] - tbbox[1] + 6
        except Exception:
            title_h = line_h + 6

    img_h = padding * 2 + title_h + line_h * len(wrapped)
    img = Image.new('RGB', (width, img_h), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    y = padding

    if title:
        draw.text((padding, y), title, fill=(0, 0, 0), font=title_font)
        y += title_h

    for line in wrapped:
        draw.text((padding, y), line, fill=(0, 0, 0), font=font)
        y += line_h

    # trim whitespace border by cropping to content bbox
    mask = Image.new('1', img.size)
    pixels = img.load()
    mw, mh = img.size
    mpix = mask.load()
    for yy in range(mh):
        for xx in range(mw):
            if pixels[xx, yy] != (255, 255, 255):
                mpix[xx, yy] = 1
    bbox = mask.getbbox()
    if bbox:
        img = img.crop(bbox)

    img.save(outpath)
    print('Wrote', outpath)

def main():
    ensure_pillow()
    out = run_demo()
    # split into sections
    # find indexes
    init_idx = out.find('Uploading initial file...')
    edit_idx = out.find('Uploading edited file', init_idx)
    hist_idx = out.find('Fetching history...', edit_idx)
    diff_idx = out.find('Diff from', hist_idx)

    initial_section = out[init_idx:hist_idx] if init_idx!=-1 and hist_idx!=-1 else out
    history_section = ''
    diff_section = ''
    if hist_idx != -1 and diff_idx != -1:
        history_section = out[hist_idx:diff_idx]
        diff_section = out[diff_idx:]
    elif hist_idx != -1:
        history_section = out[hist_idx:]

    # render
    render_text_to_png(initial_section, os.path.join(OUT_DIR, 'initial_and_edit.png'))
    if history_section:
        render_text_to_png(history_section, os.path.join(OUT_DIR, 'history.png'))
    if diff_section:
        render_text_to_png(diff_section, os.path.join(OUT_DIR, 'diff.png'))

if __name__ == '__main__':
    main()
