from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw


CELL_W = 192
CELL_H = 208
COLS = 6
ROWS = 21
SCALE = 4

OUTLINE = (142, 83, 45, 255)
PIG = (255, 213, 202, 255)
PIG_SHADE = (255, 188, 178, 255)
SNOUT = (243, 137, 123, 255)
BLUSH = (255, 167, 153, 120)
EAR_INNER = (255, 178, 168, 255)
CREAM = (255, 246, 218, 255)
BLUE = (118, 199, 217, 255)
CAT = (255, 222, 174, 255)
GREEN = (164, 210, 92, 255)
YELLOW = (255, 230, 104, 255)
RED = (239, 98, 92, 255)
WHITE = (255, 255, 255, 255)


def s(v: float) -> int:
    return round(v * SCALE)


def pt(x: float, y: float) -> tuple[int, int]:
    return s(x), s(y)


def box(x0: float, y0: float, x1: float, y1: float) -> tuple[int, int, int, int]:
    return s(x0), s(y0), s(x1), s(y1)


def line_width(v: float) -> int:
    return max(1, s(v))


def make_cell() -> Image.Image:
    return Image.new("RGBA", (CELL_W * SCALE, CELL_H * SCALE), (0, 0, 0, 0))


def draw_curve(draw: ImageDraw.ImageDraw, points: list[tuple[float, float]], fill=OUTLINE, width=4) -> None:
    draw.line([pt(x, y) for x, y in points], fill=fill, width=line_width(width), joint="curve")


def draw_heart(draw: ImageDraw.ImageDraw, cx: float, cy: float, size: float, fill=RED) -> None:
    r = size / 3
    draw.ellipse(box(cx - r * 1.6, cy - r * 1.3, cx, cy + r * 0.3), fill=fill, outline=OUTLINE, width=line_width(2.2))
    draw.ellipse(box(cx, cy - r * 1.3, cx + r * 1.6, cy + r * 0.3), fill=fill, outline=OUTLINE, width=line_width(2.2))
    draw.polygon([pt(cx - size * 0.62, cy), pt(cx + size * 0.62, cy), pt(cx, cy + size * 0.75)], fill=fill)
    draw.line([pt(cx - size * 0.62, cy), pt(cx, cy + size * 0.75), pt(cx + size * 0.62, cy)], fill=OUTLINE, width=line_width(2.2))


def draw_star(draw: ImageDraw.ImageDraw, cx: float, cy: float, size: float, fill=YELLOW) -> None:
    pts = []
    for i in range(8):
        ang = -math.pi / 2 + i * math.pi / 4
        rr = size if i % 2 == 0 else size * 0.42
        pts.append(pt(cx + math.cos(ang) * rr, cy + math.sin(ang) * rr))
    draw.polygon(pts, fill=fill)


def draw_battery(draw: ImageDraw.ImageDraw, x: float, y: float, level: float) -> None:
    draw.rounded_rectangle(box(x, y, x + 46, y + 18), radius=s(4), fill=WHITE, outline=OUTLINE, width=line_width(3))
    draw.rounded_rectangle(box(x + 46, y + 5, x + 51, y + 13), radius=s(2), fill=WHITE, outline=OUTLINE, width=line_width(2))
    fill = GREEN if level > 0.35 else RED
    if level > 0:
        draw.rounded_rectangle(box(x + 5, y + 5, x + 5 + 34 * level, y + 13), radius=s(2), fill=fill)


def pig_layer(
    *,
    cx: float = 96,
    cy: float = 112,
    w: float = 118,
    h: float = 140,
    angle: float = 0,
    squash: float = 1,
    eyes: str = "dot",
    mouth: str = "small",
    arm: str = "down",
    blush: bool = True,
    back: bool = False,
    side: int = 0,
) -> Image.Image:
    layer = make_cell()
    d = ImageDraw.Draw(layer)
    hh = h * squash
    top = cy - hh / 2
    left = cx - w / 2
    right = cx + w / 2
    bottom = cy + hh / 2

    if side == 0:
        body = box(left + 3, top + 18, right - 3, bottom)
    else:
        body = box(left + side * 6, top + 18, right + side * 6, bottom)
    d.rounded_rectangle(body, radius=s(44), fill=PIG, outline=OUTLINE, width=line_width(4.4))

    if back:
        ear_y = top + 11
        d.rounded_rectangle(box(left + 8, ear_y, left + 41, ear_y + 38), radius=s(11), fill=PIG, outline=OUTLINE, width=line_width(4.4))
        d.rounded_rectangle(box(right - 41, ear_y, right - 8, ear_y + 38), radius=s(11), fill=PIG, outline=OUTLINE, width=line_width(4.4))
        draw_curve(d, [(cx + 28, cy - 7), (cx + 18, cy + 10), (cx + 26, cy + 18)], width=3)
        draw_curve(d, [(cx - 2, cy + 24), (cx - 9, cy + 31), (cx + 0, cy + 37)], width=3)
    else:
        ear_y = top + 2
        left_ear = [pt(left + 9, ear_y + 25), pt(left + 12, ear_y + 3), pt(left + 43, ear_y + 6), pt(left + 50, ear_y + 29), pt(left + 35, ear_y + 43)]
        right_ear = [pt(right - 9, ear_y + 25), pt(right - 12, ear_y + 3), pt(right - 43, ear_y + 6), pt(right - 50, ear_y + 29), pt(right - 35, ear_y + 43)]
        d.polygon(left_ear, fill=PIG)
        d.line(left_ear + [left_ear[0]], fill=OUTLINE, width=line_width(4.4), joint="curve")
        d.polygon(right_ear, fill=PIG)
        d.line(right_ear + [right_ear[0]], fill=OUTLINE, width=line_width(4.4), joint="curve")
        d.polygon([pt(left + 19, ear_y + 15), pt(left + 38, ear_y + 16), pt(left + 31, ear_y + 31)], fill=EAR_INNER)
        d.polygon([pt(right - 19, ear_y + 15), pt(right - 38, ear_y + 16), pt(right - 31, ear_y + 31)], fill=EAR_INNER)

        if blush:
            d.ellipse(box(cx - 46, cy - 12, cx - 18, cy + 18), fill=BLUSH)
            d.ellipse(box(cx + 18, cy - 12, cx + 46, cy + 18), fill=BLUSH)

        if eyes == "dot":
            d.ellipse(box(cx - 22, cy - 25, cx - 16, cy - 19), fill=OUTLINE)
            d.ellipse(box(cx + 16, cy - 25, cx + 22, cy - 19), fill=OUTLINE)
        elif eyes == "happy":
            draw_curve(d, [(cx - 25, cy - 21), (cx - 18, cy - 26), (cx - 11, cy - 21)], width=3)
            draw_curve(d, [(cx + 11, cy - 21), (cx + 18, cy - 26), (cx + 25, cy - 21)], width=3)
        elif eyes == "sad":
            draw_curve(d, [(cx - 27, cy - 28), (cx - 19, cy - 23), (cx - 12, cy - 22)], width=3)
            draw_curve(d, [(cx + 12, cy - 22), (cx + 19, cy - 23), (cx + 27, cy - 28)], width=3)
        elif eyes == "shy":
            draw_curve(d, [(cx - 27, cy - 22), (cx - 15, cy - 22)], width=3)
            draw_curve(d, [(cx + 15, cy - 22), (cx + 27, cy - 22)], width=3)
            for off in (-30, -25, 25, 30):
                draw_curve(d, [(cx + off, cy + 5), (cx + off + 4, cy - 2)], width=1.5)

        d.rounded_rectangle(box(cx - 20, cy - 18, cx + 20, cy + 8), radius=s(11), fill=SNOUT, outline=OUTLINE, width=line_width(3.5))
        d.ellipse(box(cx - 10, cy - 8, cx - 6, cy - 3), fill=OUTLINE)
        d.ellipse(box(cx + 6, cy - 8, cx + 10, cy - 3), fill=OUTLINE)

        if mouth == "small":
            draw_curve(d, [(cx - 6, cy + 18), (cx, cy + 22), (cx + 6, cy + 18)], width=2.5)
        elif mouth == "open":
            d.ellipse(box(cx - 8, cy + 17, cx + 8, cy + 31), fill=(133, 70, 55, 255))
        elif mouth == "flat":
            draw_curve(d, [(cx - 9, cy + 20), (cx + 9, cy + 20)], width=2.5)

    # Arms.
    if arm == "down":
        draw_curve(d, [(left + 9, cy + 22), (left - 8, cy + 35), (left + 0, cy + 47)], width=6)
        draw_curve(d, [(right - 9, cy + 22), (right + 8, cy + 35), (right - 0, cy + 47)], width=6)
    elif arm == "wave":
        draw_curve(d, [(left + 7, cy + 12), (left - 18, cy - 7), (left - 11, cy - 32)], width=8)
        draw_curve(d, [(right - 8, cy + 22), (right + 4, cy + 34), (right - 1, cy + 45)], width=6)
    elif arm == "hold":
        draw_curve(d, [(left + 10, cy + 15), (cx - 31, cy + 35), (cx - 16, cy + 52)], width=7)
        draw_curve(d, [(right - 10, cy + 15), (cx + 31, cy + 35), (cx + 16, cy + 52)], width=7)
    elif arm == "face":
        draw_curve(d, [(left + 12, cy + 17), (cx - 28, cy + 6), (cx - 18, cy - 7)], width=8)
        draw_curve(d, [(right - 12, cy + 17), (cx + 28, cy + 6), (cx + 18, cy - 7)], width=8)
    elif arm == "up":
        draw_curve(d, [(left + 11, cy + 17), (left - 13, cy - 7), (left - 3, cy - 31)], width=8)
        draw_curve(d, [(right - 11, cy + 17), (right + 13, cy - 7), (right + 3, cy - 31)], width=8)

    d.rounded_rectangle(box(cx - 30, bottom - 12, cx - 12, bottom + 7), radius=s(8), fill=PIG_SHADE, outline=OUTLINE, width=line_width(3))
    d.rounded_rectangle(box(cx + 12, bottom - 12, cx + 30, bottom + 7), radius=s(8), fill=PIG_SHADE, outline=OUTLINE, width=line_width(3))

    if angle:
        layer = layer.rotate(angle, resample=Image.Resampling.BICUBIC, center=pt(cx, cy), fillcolor=(0, 0, 0, 0))
    return layer


def composite_pig(cell: Image.Image, **kwargs) -> None:
    cell.alpha_composite(pig_layer(**kwargs))


def draw_phone(cell: Image.Image, x: float, y: float, angle: float = 0) -> None:
    tmp = make_cell()
    td = ImageDraw.Draw(tmp)
    td.rounded_rectangle(box(x, y, x + 24, y + 36), radius=s(4), fill=(242, 246, 250, 255), outline=OUTLINE, width=line_width(3))
    td.ellipse(box(x + 10, y + 29, x + 14, y + 33), fill=OUTLINE)
    if angle:
        tmp = tmp.rotate(angle, resample=Image.Resampling.BICUBIC, center=pt(x + 12, y + 18), fillcolor=(0, 0, 0, 0))
    cell.alpha_composite(tmp)


def draw_fish(d: ImageDraw.ImageDraw, cx: float, cy: float, flip: int = 1) -> None:
    d.ellipse(box(cx - 24, cy - 14, cx + 20, cy + 14), fill=BLUE, outline=OUTLINE, width=line_width(3))
    tail = [(cx + 20 * flip, cy), (cx + 34 * flip, cy - 12), (cx + 32 * flip, cy + 12)]
    d.polygon([pt(x, y) for x, y in tail], fill=BLUE, outline=OUTLINE)
    d.ellipse(box(cx - 13 * flip, cy - 5, cx - 9 * flip, cy - 1), fill=OUTLINE)
    draw_curve(d, [(cx - 1 * flip, cy - 10), (cx + 5 * flip, cy - 13), (cx + 10 * flip, cy - 8)], width=2)


def draw_cat(d: ImageDraw.ImageDraw, cx: float, cy: float, scale: float = 1.0, asleep: bool = False) -> None:
    w = 43 * scale
    h = 58 * scale
    d.rounded_rectangle(box(cx - w / 2, cy - h / 2 + 9 * scale, cx + w / 2, cy + h / 2), radius=s(18 * scale), fill=CAT, outline=OUTLINE, width=line_width(3))
    d.polygon([pt(cx - 18 * scale, cy - 14 * scale), pt(cx - 8 * scale, cy - 28 * scale), pt(cx - 2 * scale, cy - 10 * scale)], fill=CAT, outline=OUTLINE)
    d.polygon([pt(cx + 18 * scale, cy - 14 * scale), pt(cx + 8 * scale, cy - 28 * scale), pt(cx + 2 * scale, cy - 10 * scale)], fill=CAT, outline=OUTLINE)
    if asleep:
        draw_curve(d, [(cx - 9 * scale, cy - 3 * scale), (cx - 5 * scale, cy - 7 * scale), (cx - 1 * scale, cy - 3 * scale)], width=2)
        draw_curve(d, [(cx + 1 * scale, cy - 3 * scale), (cx + 5 * scale, cy - 7 * scale), (cx + 9 * scale, cy - 3 * scale)], width=2)
    else:
        d.ellipse(box(cx - 8 * scale, cy - 4 * scale, cx - 5 * scale, cy - 1 * scale), fill=OUTLINE)
        d.ellipse(box(cx + 5 * scale, cy - 4 * scale, cx + 8 * scale, cy - 1 * scale), fill=OUTLINE)
    d.rounded_rectangle(box(cx - 6 * scale, cy + 2 * scale, cx + 6 * scale, cy + 10 * scale), radius=s(4 * scale), fill=SNOUT, outline=OUTLINE, width=line_width(2))
    for off in (-14, 14):
        draw_curve(d, [(cx + off * scale, cy + 2 * scale), (cx + (off + 8) * scale, cy + 0 * scale)], width=1.6)
        draw_curve(d, [(cx + off * scale, cy + 8 * scale), (cx + (off + 8) * scale, cy + 10 * scale)], width=1.6)


def draw_boba(d: ImageDraw.ImageDraw, cx: float, cy: float, sip: float = 0) -> None:
    d.rounded_rectangle(box(cx - 19, cy - 21, cx + 19, cy + 28), radius=s(7), fill=(238, 205, 140, 255), outline=OUTLINE, width=line_width(3))
    d.rounded_rectangle(box(cx - 22, cy - 24, cx + 22, cy - 16), radius=s(3), fill=CREAM, outline=OUTLINE, width=line_width(2))
    draw_curve(d, [(cx + 2, cy - 22), (cx + 1 + sip, cy - 48), (cx + 5 + sip, cy - 61)], width=4)
    for ox, oy in [(-10, 13), (0, 18), (10, 12), (-3, 6)]:
        d.ellipse(box(cx + ox - 3, cy + oy - 3, cx + ox + 3, cy + oy + 3), fill=(92, 72, 54, 255))


def draw_blanket(d: ImageDraw.ImageDraw, x: float, y: float, w: float, h: float) -> None:
    d.rounded_rectangle(box(x, y, x + w, y + h), radius=s(18), fill=(255, 237, 129, 255), outline=OUTLINE, width=line_width(3))
    draw_curve(d, [(x + 8, y + 15), (x + w - 8, y + 5)], fill=(255, 247, 182, 255), width=5)


def draw_shopping_bags(d: ImageDraw.ImageDraw, frame: int) -> None:
    for x, color, lean in [(50, (116, 207, 181, 255), -frame), (126, (255, 220, 93, 255), frame)]:
        y = 132 + (frame % 2) * 3
        d.polygon([pt(x - 16 + lean, y - 26), pt(x + 15 + lean, y - 32), pt(x + 18 + lean, y + 18), pt(x - 16 + lean, y + 24)], fill=color, outline=OUTLINE)
        draw_curve(d, [(x - 8 + lean, y - 24), (x, y - 39), (x + 9 + lean, y - 25)], width=2.5)


def draw_yarn(d: ImageDraw.ImageDraw, cx: float, cy: float, r: float) -> None:
    d.ellipse(box(cx - r, cy - r, cx + r, cy + r), fill=(142, 218, 211, 255), outline=OUTLINE, width=line_width(3))
    for off in [-13, -3, 7, 16]:
        draw_curve(d, [(cx - r + 5, cy + off), (cx - 2, cy + off - 8), (cx + r - 5, cy + off - 3)], width=2)
    draw_curve(d, [(cx - 9, cy + r - 1), (cx - 34, cy + r + 12), (cx - 60, cy + r + 7)], width=2)


def draw_hotpot(d: ImageDraw.ImageDraw, cx: float, cy: float, steam: int) -> None:
    d.rounded_rectangle(box(cx - 41, cy + 27, cx + 41, cy + 47), radius=s(6), fill=YELLOW, outline=OUTLINE, width=line_width(3))
    d.rounded_rectangle(box(cx - 31, cy + 47, cx + 31, cy + 67), radius=s(5), fill=(243, 196, 77, 255), outline=OUTLINE, width=line_width(3))
    d.ellipse(box(cx - 44, cy - 7, cx + 44, cy + 31), fill=CREAM, outline=OUTLINE, width=line_width(3))
    d.arc(box(cx - 37, cy - 18, cx + 37, cy + 29), 0, 180, fill=OUTLINE, width=line_width(3))
    for ox, color in [(-22, GREEN), (-7, RED), (10, (250, 112, 78, 255)), (23, GREEN)]:
        d.ellipse(box(cx + ox - 7, cy + 2, cx + ox + 7, cy + 14), fill=color, outline=OUTLINE, width=line_width(2))
    for ox in [-22, 0, 22]:
        draw_curve(d, [(cx + ox, cy - 14), (cx + ox + 5, cy - 25 - steam), (cx + ox - 1, cy - 36 - steam)], fill=(181, 116, 76, 255), width=2)


def action_cell(row: int, frame: int) -> Image.Image:
    cell = make_cell()
    d = ImageDraw.Draw(cell)
    phase = frame / (COLS - 1)
    bob = math.sin(phase * math.tau)
    alt = -1 if frame % 2 else 1

    if row == 0:
        composite_pig(cell, cy=114 + bob * 2, h=112 + bob * 2, eyes="happy" if frame in (2, 3) else "dot")
    elif row == 1:
        composite_pig(cell, cx=91, cy=115 + bob * 2, arm="wave", eyes="happy")
        draw_phone(cell, 126, 76 + bob, angle=-8 + frame * 2)
    elif row == 2:
        composite_pig(cell, cy=118 - abs(bob) * 16, h=108 - abs(bob) * 8, arm="up", eyes="happy", mouth="open")
        draw_heart(d, 143, 63 - abs(bob) * 12, 14)
    elif row == 3:
        composite_pig(cell, cx=76 + frame * 9, cy=116 + (frame % 2) * 4, side=1, arm="down")
    elif row == 4:
        composite_pig(cell, cx=126 - frame * 9, cy=116 + (frame % 2) * 4, side=-1, arm="down")
    elif row == 5:
        composite_pig(cell, cy=115 + bob * 2, arm="hold")
        draw_fish(d, 96, 139 + bob * 2, flip=1)
    elif row == 6:
        composite_pig(cell, cy=113 + bob * 1.5, arm="hold", eyes="happy")
        draw_boba(d, 96, 138, sip=bob * 4)
        if frame in (1, 4):
            draw_star(d, 56, 72, 6)
            draw_star(d, 136, 76, 5)
    elif row == 7:
        composite_pig(cell, cx=82, cy=119, eyes="sad", mouth="flat", arm="down")
        draw_cat(d, 132 + bob * 4, 122, 0.75)
    elif row == 8:
        draw_battery(d, 71, 35, max(0.04, 0.25 - frame * 0.035))
        composite_pig(cell, cx=94, cy=132 + frame * 2, w=120, h=72, angle=-2 + frame, eyes="sad", mouth="flat", arm="down")
        d.rounded_rectangle(box(130, 137, 170, 157), radius=s(4), fill=(139, 96, 60, 255), outline=OUTLINE, width=line_width(2))
    elif row == 9:
        composite_pig(cell, cy=115, eyes="sad", mouth="flat", arm="face")
        d.rounded_rectangle(box(50, 93 + bob * 2, 59, 144), radius=s(6), fill=(121, 198, 237, 230))
        d.rounded_rectangle(box(133, 93 - bob * 2, 142, 144), radius=s(6), fill=(121, 198, 237, 230))
    elif row == 10:
        composite_pig(cell, cy=115 + bob, eyes="sad", mouth="flat", arm="down")
        for ox in (-17, 17):
            d.ellipse(box(96 + ox - 8, 61 - abs(bob) * 5, 96 + ox + 8, 75 - abs(bob) * 5), fill=WHITE, outline=OUTLINE, width=line_width(2))
        draw_curve(d, [(122, 80), (128, 74), (134, 78), (130, 84), (136, 86)], fill=OUTLINE, width=2)
    elif row == 11:
        composite_pig(cell, cx=54 + frame * 14, cy=117, angle=-12 + frame * 4, eyes="dot", arm="down")
        d.rectangle(box(0, 0, 25, CELL_H), fill=(0, 0, 0, 0))
    elif row == 12:
        draw_battery(d, 71, 34, 0.55 + frame * 0.07)
        composite_pig(cell, cx=106, cy=119, arm="hold", eyes="happy")
        draw_cat(d, 72, 125 + bob * 2, 0.78, asleep=True)
        if frame in (0, 3):
            draw_heart(d, 53, 78, 12)
    elif row == 13:
        draw_blanket(d, 58, 125 + bob, 88, 51)
        composite_pig(cell, cx=101, cy=124 + bob, w=108, h=78, angle=-3, eyes="happy", mouth="small", arm="down")
    elif row == 14:
        composite_pig(cell, cy=118 + (frame % 2) * 3, arm="hold")
        draw_shopping_bags(d, alt * 3)
    elif row == 15:
        composite_pig(cell, cx=92, cy=118, angle=-8 + bob * 6, arm="hold", eyes="happy")
        draw_yarn(d, 127, 133 + bob * 3, 25)
        draw_cat(d, 121, 91 + bob * 2, 0.62, asleep=True)
    elif row == 16:
        composite_pig(cell, cy=105 + bob, arm="hold", eyes="happy")
        draw_hotpot(d, 96, 103, int(abs(bob) * 6))
    elif row == 17:
        draw_battery(d, 71, 34, 0.03)
        composite_pig(cell, cx=94, cy=137, w=126, h=66, angle=1 + bob, eyes="sad", mouth="flat")
    elif row == 18:
        composite_pig(cell, cy=121 - abs(bob) * 20, w=92 - abs(bob) * 8, h=119 + abs(bob) * 12, eyes="sad", mouth="open", arm="up")
    elif row == 19:
        composite_pig(cell, cy=116 + bob, eyes="shy", mouth="small", arm="face")
        if frame in (1, 4):
            draw_heart(d, 142, 74, 12)
    elif row == 20:
        composite_pig(cell, cy=115 + bob * 2, eyes="happy", mouth="open", arm="up")
        for i, (x, y, color) in enumerate([(50, 83, RED), (139, 77, BLUE), (61, 61, YELLOW), (126, 58, GREEN)]):
            d.rectangle(box(x + bob * 3, y + ((frame + i) % 3) * 4, x + 7 + bob * 3, y + 7 + ((frame + i) % 3) * 4), fill=color, outline=OUTLINE, width=line_width(1))
    else:
        composite_pig(cell)

    return cell.resize((CELL_W, CELL_H), Image.Resampling.LANCZOS)


def main() -> None:
    out = Image.new("RGBA", (CELL_W * COLS, CELL_H * ROWS), (0, 0, 0, 0))
    for row in range(ROWS):
        for col in range(COLS):
            out.alpha_composite(action_cell(row, col), (col * CELL_W, row * CELL_H))

    out_path = Path("spritesheet.lulu_v2.webp")
    out.save(out_path, "WEBP", lossless=True, quality=100, method=6)

    contact = Image.new("RGBA", out.size, (212, 238, 237, 255))
    contact.alpha_composite(out)
    contact.save("spritesheet_lulu_v2_contact.png")
    print(f"wrote {out_path.resolve()} {out.size}")
    print(f"wrote {(Path('spritesheet_lulu_v2_contact.png')).resolve()}")


if __name__ == "__main__":
    main()
