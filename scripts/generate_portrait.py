#!/usr/bin/env python3
"""Generate ASCII portrait SVG from a photo.

Output matches the style of andriidrok1's ascii.svg:
  - grayscale photo mapped through a character ramp
  - SMIL reveal animation (left-to-right per row)
  - transparent background, grey ink
  - color-aware (light/dark mode)
"""
import base64
import os
import sys
from PIL import Image

RAMP = " .`-:=+*cs#%@"
INK_LIGHT = "#6e7681"
INK_DARK = "#c9d1d9"
FONT_SIZE = 12.9
CHAR_W = 7.74
CHAR_H = 15.0
LEFT = 14
TOP = 14
CURSOR_W = 6
ROW_S = 0.09
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(HERE, "fonts", "jbmono-ramp.woff2")
FONT_FAMILY = ("JBMono,ui-monospace,SFMono-Regular,Menlo,Consolas,"
               "&apos;Liberation Mono&apos;,monospace")


def font_face():
    with open(FONT_PATH, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return (f"@font-face{{font-family:JBMono;font-style:normal;"
            f"font-weight:400;font-display:block;"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}")


def image_to_text(path, cols=90):
    img = Image.open(path).convert("L")
    aspect = img.height / img.width
    rows = round(aspect * cols * (CHAR_W / CHAR_H))
    img = img.resize((cols, rows), Image.LANCZOS)
    pixels = list(img.getdata())
    ramp_max = len(RAMP) - 1
    lines = []
    for r in range(rows):
        row_pixels = pixels[r * cols:(r + 1) * cols]
        line = "".join(RAMP[round(p / 255 * ramp_max)] for p in row_pixels)
        lines.append(line)
    return lines


def build_svg(lines):
    rows = len(lines)
    cols = max(len(l) for l in lines)
    svg_w = LEFT + cols * CHAR_W + LEFT
    svg_h = TOP + rows * CHAR_H + TOP
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w:.0f}" height="{svg_h:.0f}" '
        f'viewBox="0 0 {svg_w:.0f} {svg_h:.0f}" '
        f'font-family="{FONT_FAMILY}">',
        f"<style>{font_face()}.a{{fill:{INK_LIGHT}}}@media(prefers-color-scheme:dark){{.a{{fill:{INK_DARK}}}</style>",
    ]
    for i, line in enumerate(lines):
        t = i * ROW_S
        line_w = len(line.rstrip()) * CHAR_W
        # clip-path reveal
        cid = f"c{i}"
        parts.append(
            f'<clipPath id="{cid}">'
            f'<rect x="{LEFT}" y="{TOP + i * CHAR_H}" height="{CHAR_H}" width="0">'
            f'<animate attributeName="width" from="0" to="{line_w:.1f}" '
            f'begin="{t:.2f}s" dur="{ROW_S}s" fill="freeze"/>'
            f"</rect></clipPath>"
        )
        parts.append(
            f'<g clip-path="url(#{cid})">'
            f'<text xml:space="preserve" x="{LEFT}" y="{TOP + i * CHAR_H + FONT_SIZE * 0.95}" '
            f'class="a" font-size="{FONT_SIZE}">{line}</text></g>'
        )
        # cursor
        cursor_x = LEFT + line_w + 1
        parts.append(
            f"<rect y=\"{TOP + i * CHAR_H + 1}\" width=\"{CURSOR_W}\" height=\"{CHAR_H - 2}\" "
            f'class="a" opacity="0">'
            f'<animate attributeName="x" from="{LEFT}" to="{cursor_x:.1f}" '
            f'begin="{t:.2f}s" dur="{ROW_S}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0.8" begin="{t:.2f}s"/>'
            f'<set attributeName="opacity" to="0" begin="{t + ROW_S:.2f}s"/>'
            f"</rect>"
        )
    parts.append("</svg>")
    return "\n".join(parts)


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "/tmp/nutriandrea-avatar.png"
    out = sys.argv[2] if len(sys.argv) > 2 else "ascii.svg"
    cols = int(sys.argv[3]) if len(sys.argv) > 3 else 90
    lines = image_to_text(src, cols=cols)
    svg = build_svg(lines)
    with open(out, "w") as f:
        f.write(svg)
    print(f"portrait: {out} ({len(lines)} rows, {max(len(l) for l in lines)} cols)")


if __name__ == "__main__":
    main()
