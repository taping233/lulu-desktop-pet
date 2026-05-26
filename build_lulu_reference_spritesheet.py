from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter


CELL_W = 192
CELL_H = 208
COLS = 6
ROWS = 21
SCALE = 3

REFERENCE = Path(r"C:\Users\太平\Downloads\俺们猪猪每一帧都好可爱啊🥰_2_LuluKitty酱_来自小红书网页版.jpg")

OUTLINE = (151, 76, 35, 255)
PINK = (255, 209, 198, 255)
SNOUT = (232, 116, 105, 255)
CREAM = (255, 246, 218, 255)
BLUE = (107, 198, 217, 255)
CAT = (255, 220, 173, 255)
GREEN = (164, 210, 92, 255)
YELLOW = (255, 227, 101, 255)
RED = (239, 95, 88, 255)
WHITE = (255, 255, 255, 255)


def s(v: float) -> int:
    return round(v * SCALE)


def pt(x: float, y: float) -> tuple[int, int]:
    return s(x), s(y)


def box(x0: float, y0: float, x1: float, y1: float) -> tuple[int, int, int, int]:
    return s(x0), s(y0), s(x1), s(y1)


def lw(v: float) -> int:
    return max(1, s(v))


def cell() -> Image.Image:
    return Image.new("RGBA", (CELL_W * SCALE, CELL_H * SCALE), (0, 0, 0, 0))


def curve(draw: ImageDraw.ImageDraw, points: list[tuple[float, float]], fill=OUTLINE, width=3) -> None:
    draw.line([pt(x, y) for x, y in points], fill=fill, width=lw(width), joint="curve")


def remove_blue_background(img: Image.Image) -> Image.Image:
    rgba = img.convert("RGBA")
    px = rgba.load()
    w, h = rgba.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            blue_bg = b > 145 and g > 105 and r < 180 and (b - r) > 40
            if blue_bg:
                px[x, y] = (0, 0, 0, 0)
    alpha = rgba.getchannel("A").filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
    rgba.putalpha(alpha)
    bbox = rgba.getbbox()
    if not bbox:
        return rgba
    return rgba.crop(bbox)


def load_reference_poses() -> dict[str, Image.Image]:
    src = Image.open(REFERENCE).convert("RGB")
    w, h = src.size
    crops = {
        "front": (0, 0, w // 2, h // 2),
        "hold": (w // 2, 0, w, h // 2),
        "upside": (0, h // 2, w // 2, h),
        "side": (w // 2, h // 2, w, h),
    }
    poses = {}
    for name, rect in crops.items():
        cut = remove_blue_background(src.crop(rect))
        cut = ImageEnhance.Color(cut).enhance(1.03)
        poses[name] = cut
    return poses


def fit_pose(pose: Image.Image, max_w: float = 132, max_h: float = 170, angle: float = 0, flip: bool = False) -> Image.Image:
    img = pose.copy()
    if flip:
        img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    if angle:
        img = img.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True, fillcolor=(0, 0, 0, 0))
    scale = min((max_w * SCALE) / img.width, (max_h * SCALE) / img.height)
    return img.resize((max(1, round(img.width * scale)), max(1, round(img.height * scale))), Image.Resampling.LANCZOS)


def paste_center(base: Image.Image, sprite: Image.Image, cx: float, cy: float) -> None:
    x = s(cx) - sprite.width // 2
    y = s(cy) - sprite.height // 2
    base.alpha_composite(sprite, (x, y))


def draw_heart(d: ImageDraw.ImageDraw, cx: float, cy: float, size: float) -> None:
    r = size / 3
    d.ellipse(box(cx - r * 1.6, cy - r * 1.3, cx, cy + r * 0.3), fill=RED, outline=OUTLINE, width=lw(2))
    d.ellipse(box(cx, cy - r * 1.3, cx + r * 1.6, cy + r * 0.3), fill=RED, outline=OUTLINE, width=lw(2))
    d.polygon([pt(cx - size * 0.62, cy), pt(cx + size * 0.62, cy), pt(cx, cy + size * 0.75)], fill=RED)
    d.line([pt(cx - size * 0.62, cy), pt(cx, cy + size * 0.75), pt(cx + size * 0.62, cy)], fill=OUTLINE, width=lw(2))


def draw_battery(d: ImageDraw.ImageDraw, x: float, y: float, level: float) -> None:
    d.rounded_rectangle(box(x, y, x + 46, y + 18), radius=s(4), fill=WHITE, outline=OUTLINE, width=lw(3))
    d.rounded_rectangle(box(x + 46, y + 5, x + 51, y + 13), radius=s(2), fill=WHITE, outline=OUTLINE, width=lw(2))
    if level > 0:
        d.rounded_rectangle(box(x + 5, y + 5, x + 5 + 34 * level, y + 13), radius=s(2), fill=GREEN if level > 0.35 else RED)


def draw_fish(d: ImageDraw.ImageDraw, cx: float, cy: float) -> None:
    d.ellipse(box(cx - 25, cy - 14, cx + 21, cy + 14), fill=BLUE, outline=OUTLINE, width=lw(3))
    d.polygon([pt(cx + 20, cy), pt(cx + 36, cy - 12), pt(cx + 34, cy + 12)], fill=BLUE, outline=OUTLINE)
    d.ellipse(box(cx - 12, cy - 5, cx - 8, cy - 1), fill=OUTLINE)


def draw_boba(d: ImageDraw.ImageDraw, cx: float, cy: float, sip: float) -> None:
    d.rounded_rectangle(box(cx - 19, cy - 20, cx + 19, cy + 27), radius=s(7), fill=(235, 201, 139, 255), outline=OUTLINE, width=lw(3))
    d.rounded_rectangle(box(cx - 22, cy - 24, cx + 22, cy - 16), radius=s(3), fill=CREAM, outline=OUTLINE, width=lw(2))
    curve(d, [(cx + 2, cy - 22), (cx + 1 + sip, cy - 48), (cx + 5 + sip, cy - 61)], width=4)
    for ox, oy in [(-10, 12), (0, 18), (10, 11), (-3, 5)]:
        d.ellipse(box(cx + ox - 3, cy + oy - 3, cx + ox + 3, cy + oy + 3), fill=(87, 66, 49, 255))


def draw_cat(d: ImageDraw.ImageDraw, cx: float, cy: float, scale: float = 1.0, asleep: bool = False) -> None:
    w = 42 * scale
    h = 55 * scale
    d.rounded_rectangle(box(cx - w / 2, cy - h / 2 + 9 * scale, cx + w / 2, cy + h / 2), radius=s(17 * scale), fill=CAT, outline=OUTLINE, width=lw(3))
    d.polygon([pt(cx - 17 * scale, cy - 13 * scale), pt(cx - 8 * scale, cy - 27 * scale), pt(cx - 2 * scale, cy - 9 * scale)], fill=CAT, outline=OUTLINE)
    d.polygon([pt(cx + 17 * scale, cy - 13 * scale), pt(cx + 8 * scale, cy - 27 * scale), pt(cx + 2 * scale, cy - 9 * scale)], fill=CAT, outline=OUTLINE)
    if asleep:
        curve(d, [(cx - 9 * scale, cy - 3 * scale), (cx - 5 * scale, cy - 7 * scale), (cx - 1 * scale, cy - 3 * scale)], width=2)
        curve(d, [(cx + 1 * scale, cy - 3 * scale), (cx + 5 * scale, cy - 7 * scale), (cx + 9 * scale, cy - 3 * scale)], width=2)
    else:
        d.ellipse(box(cx - 8 * scale, cy - 4 * scale, cx - 5 * scale, cy - 1 * scale), fill=OUTLINE)
        d.ellipse(box(cx + 5 * scale, cy - 4 * scale, cx + 8 * scale, cy - 1 * scale), fill=OUTLINE)
    d.rounded_rectangle(box(cx - 6 * scale, cy + 2 * scale, cx + 6 * scale, cy + 10 * scale), radius=s(4 * scale), fill=SNOUT, outline=OUTLINE, width=lw(2))


def draw_phone(d: ImageDraw.ImageDraw, x: float, y: float) -> None:
    d.rounded_rectangle(box(x, y, x + 25, y + 37), radius=s(4), fill=(242, 246, 250, 255), outline=OUTLINE, width=lw(3))
    d.ellipse(box(x + 10, y + 30, x + 14, y + 34), fill=OUTLINE)


def draw_yarn(d: ImageDraw.ImageDraw, cx: float, cy: float, r: float) -> None:
    d.ellipse(box(cx - r, cy - r, cx + r, cy + r), fill=(142, 218, 211, 255), outline=OUTLINE, width=lw(3))
    for off in [-13, -3, 7, 16]:
        curve(d, [(cx - r + 5, cy + off), (cx - 2, cy + off - 8), (cx + r - 5, cy + off - 3)], width=2)
    curve(d, [(cx - 9, cy + r - 1), (cx - 34, cy + r + 12), (cx - 60, cy + r + 7)], width=2)


def draw_hotpot(d: ImageDraw.ImageDraw, cx: float, cy: float, steam: float) -> None:
    d.rounded_rectangle(box(cx - 41, cy + 27, cx + 41, cy + 47), radius=s(6), fill=YELLOW, outline=OUTLINE, width=lw(3))
    d.rounded_rectangle(box(cx - 31, cy + 47, cx + 31, cy + 67), radius=s(5), fill=(243, 196, 77, 255), outline=OUTLINE, width=lw(3))
    d.ellipse(box(cx - 44, cy - 7, cx + 44, cy + 31), fill=CREAM, outline=OUTLINE, width=lw(3))
    for ox, color in [(-22, GREEN), (-7, RED), (10, (250, 112, 78, 255)), (23, GREEN)]:
        d.ellipse(box(cx + ox - 7, cy + 2, cx + ox + 7, cy + 14), fill=color, outline=OUTLINE, width=lw(2))
    for ox in [-20, 4, 24]:
        curve(d, [(cx + ox, cy - 12), (cx + ox + 5, cy - 24 - steam), (cx + ox - 1, cy - 35 - steam)], width=2)


def add_paw_caps(d: ImageDraw.ImageDraw, points: list[tuple[float, float]]) -> None:
    for x, y in points:
        d.ellipse(box(x - 8, y - 7, x + 8, y + 8), fill=PINK, outline=OUTLINE, width=lw(3))


def render(row: int, frame: int, poses: dict[str, Image.Image]) -> Image.Image:
    im = cell()
    d = ImageDraw.Draw(im)
    t = frame / (COLS - 1)
    bob = math.sin(t * math.tau)

    if row == 0:
        paste_center(im, fit_pose(poses["front"], 126, 168), 96, 113 + bob * 2)
    elif row == 1:
        paste_center(im, fit_pose(poses["front"], 126, 168, angle=-3 + bob * 2), 92, 114 + bob)
        draw_phone(d, 124, 74 + bob)
        add_paw_caps(d, [(126, 111 + bob)])
    elif row == 2:
        paste_center(im, fit_pose(poses["front"], 119, 158, angle=bob * 5), 96, 116 - abs(bob) * 18)
        draw_heart(d, 143, 61 - abs(bob) * 10, 14)
        add_paw_caps(d, [(62, 100 - abs(bob) * 15), (130, 100 - abs(bob) * 15)])
    elif row == 3:
        paste_center(im, fit_pose(poses["front"], 124, 166, angle=5 + bob * 5), 96 + bob * 6, 116 + (frame % 2) * 3)
    elif row == 4:
        paste_center(im, fit_pose(poses["front"], 124, 166, angle=-5 - bob * 5), 96 - bob * 6, 116 + (frame % 2) * 3)
    elif row == 5:
        paste_center(im, fit_pose(poses["hold"], 132, 172), 96, 112 + bob)
        draw_fish(d, 96, 137 + bob)
        add_paw_caps(d, [(67, 135 + bob), (124, 132 + bob)])
    elif row == 6:
        paste_center(im, fit_pose(poses["hold"], 132, 172), 96, 112 + bob)
        draw_boba(d, 98, 137, bob * 4)
        add_paw_caps(d, [(76, 134), (120, 133)])
    elif row == 7:
        paste_center(im, fit_pose(poses["front"], 126, 168), 85, 115)
        draw_cat(d, 133 + bob * 3, 124, 0.78)
    elif row == 8:
        draw_battery(d, 70, 35, max(0.04, 0.22 - frame * 0.03))
        paste_center(im, fit_pose(poses["front"], 150, 104, angle=88 + bob * 2), 96, 137 + frame * 1.2)
        d.rounded_rectangle(box(132, 139, 172, 159), radius=s(4), fill=(139, 96, 60, 255), outline=OUTLINE, width=lw(2))
    elif row == 9:
        paste_center(im, fit_pose(poses["front"], 126, 168), 96, 114)
        d.rounded_rectangle(box(49, 91 + bob * 2, 58, 144), radius=s(6), fill=(121, 198, 237, 230))
        d.rounded_rectangle(box(134, 91 - bob * 2, 143, 144), radius=s(6), fill=(121, 198, 237, 230))
    elif row == 10:
        paste_center(im, fit_pose(poses["front"], 126, 168), 96, 114 + bob)
        for ox in (-18, 18):
            d.ellipse(box(96 + ox - 8, 60 - abs(bob) * 5, 96 + ox + 8, 74 - abs(bob) * 5), fill=WHITE, outline=OUTLINE, width=lw(2))
    elif row == 11:
        paste_center(im, fit_pose(poses["side"], 138, 170, angle=-12 + frame * 4), 57 + frame * 15, 116)
    elif row == 12:
        draw_battery(d, 70, 34, 0.55 + frame * 0.07)
        paste_center(im, fit_pose(poses["hold"], 134, 174), 103, 113)
        draw_cat(d, 70, 126 + bob * 2, 0.82, asleep=True)
        add_paw_caps(d, [(84, 124 + bob)])
    elif row == 13:
        d.rounded_rectangle(box(58, 126 + bob, 146, 177 + bob), radius=s(18), fill=(255, 237, 129, 255), outline=OUTLINE, width=lw(3))
        paste_center(im, fit_pose(poses["side"], 142, 104, angle=-4), 103, 126 + bob)
    elif row == 14:
        paste_center(im, fit_pose(poses["front"], 126, 168), 96, 116 + (frame % 2) * 2)
        for x, color, lean in [(50, (116, 207, 181, 255), -frame), (128, (255, 220, 93, 255), frame)]:
            y = 133 + (frame % 2) * 2
            d.polygon([pt(x - 15 + lean, y - 25), pt(x + 16 + lean, y - 31), pt(x + 19 + lean, y + 18), pt(x - 16 + lean, y + 24)], fill=color, outline=OUTLINE)
            curve(d, [(x - 8 + lean, y - 24), (x, y - 39), (x + 9 + lean, y - 25)], width=2.5)
    elif row == 15:
        paste_center(im, fit_pose(poses["hold"], 135, 174, angle=-7 + bob * 5), 90, 114)
        draw_yarn(d, 128, 134 + bob * 3, 25)
        draw_cat(d, 119, 92 + bob * 2, 0.62, asleep=True)
    elif row == 16:
        paste_center(im, fit_pose(poses["front"], 125, 165), 96, 104 + bob)
        draw_hotpot(d, 96, 103, abs(bob) * 6)
        add_paw_caps(d, [(58, 133), (134, 133)])
    elif row == 17:
        draw_battery(d, 70, 34, 0.03)
        paste_center(im, fit_pose(poses["front"], 150, 104, angle=88 + bob * 2), 96, 139)
    elif row == 18:
        paste_center(im, fit_pose(poses["front"], 118 - abs(bob) * 6, 158 + abs(bob) * 8, angle=bob * 4), 96, 121 - abs(bob) * 19)
        add_paw_caps(d, [(58, 96 - abs(bob) * 12), (134, 96 - abs(bob) * 12)])
    elif row == 19:
        paste_center(im, fit_pose(poses["hold"], 134, 174), 96, 113 + bob)
        draw_heart(d, 142, 74, 12)
    elif row == 20:
        paste_center(im, fit_pose(poses["front"], 124, 166), 96, 114 + bob * 2)
        add_paw_caps(d, [(58, 95), (134, 95)])
        for i, (x, y, color) in enumerate([(50, 83, RED), (139, 77, BLUE), (61, 61, YELLOW), (126, 58, GREEN)]):
            d.rectangle(box(x + bob * 3, y + ((frame + i) % 3) * 4, x + 7 + bob * 3, y + 7 + ((frame + i) % 3) * 4), fill=color, outline=OUTLINE, width=lw(1))

    return im.resize((CELL_W, CELL_H), Image.Resampling.LANCZOS)


def main() -> None:
    poses = load_reference_poses()
    out = Image.new("RGBA", (CELL_W * COLS, CELL_H * ROWS), (0, 0, 0, 0))
    for row in range(ROWS):
        for col in range(COLS):
            out.alpha_composite(render(row, col, poses), (col * CELL_W, row * CELL_H))
    out.save("spritesheet.reference_lulu.webp", "WEBP", lossless=True, quality=100, method=6)
    contact = Image.new("RGBA", out.size, (126, 158, 231, 255))
    contact.alpha_composite(out)
    contact.save("spritesheet_reference_lulu_contact.png")
    print("wrote spritesheet.reference_lulu.webp")
    print("wrote spritesheet_reference_lulu_contact.png")


if __name__ == "__main__":
    main()
