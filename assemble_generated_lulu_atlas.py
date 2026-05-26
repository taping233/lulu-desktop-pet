from __future__ import annotations

from pathlib import Path

from PIL import Image


CELL_W = 192
CELL_H = 208
COLS = 6
ROWS = 31
FRAME_INSET_RATIO = 0.035
FRAME_VERTICAL_INSET_RATIO = 0.055
CELL_EDGE_CLEAR = 8


# Indices are from all generated PNGs sorted by modified time. Index 10 is the
# accepted fish-hug sample; 11 onward are the integrated action strips.
ROW_SOURCES: dict[int, tuple[int, int, int]] = {
    0: (11, 0, 1),   # idle
    1: (12, 0, 1),   # selfie wave
    2: (13, 0, 1),   # happy jump
    3: (14, 0, 1),   # move right
    4: (15, 0, 1),   # move left
    5: (10, 0, 1),   # fish work
    6: (16, 0, 1),   # boba
    7: (17, 0, 1),   # waiting cat
    8: (18, 0, 1),   # low battery collapse
    9: (19, 0, 1),   # crying
    10: (20, 0, 1),  # angry
    11: (21, 0, 1),  # peek
    12: (22, 0, 1),  # cat charging
    13: (23, 0, 1),  # blanket sleep
    14: (24, 0, 1),  # shopping
    15: (25, 0, 1),  # yarn ball
    16: (29, 0, 1),  # hotpot
    17: (28, 0, 1),  # fully drained
    18: (30, 0, 3),  # surprise bounce, row 0 of 3-row source
    19: (30, 1, 3),  # shy cover face, row 1 of 3-row source
    20: (30, 2, 3),  # celebration confetti, row 2 of 3-row source
}

EXTRA_ROW_SOURCES: dict[int, tuple[str, int, int, int]] = {
    21: ("generated_actions_21_25.png", 0, 5, 6),  # water reminder
    22: ("generated_actions_21_25.png", 1, 5, 6),  # tiny cake
    23: ("generated_actions_21_25.png", 2, 5, 6),  # stretch
    24: ("generated_action_24_umbrella.png", 0, 1, 6),  # umbrella rain
    25: ("generated_actions_21_25.png", 4, 5, 6),  # pillow nap
    26: ("generated_actions_26_30.png", 0, 5, 7),  # tea break
    27: ("generated_actions_26_30.png", 1, 5, 7),  # laptop work
    28: ("generated_actions_26_30.png", 2, 5, 7),  # sun basking
    29: ("generated_actions_26_30.png", 3, 5, 7),  # clapping
    30: ("generated_actions_26_30.png", 4, 5, 7),  # little dance
}


def generated_pngs() -> list[Path]:
    root = Path.home() / ".codex" / "generated_images"
    return sorted(root.rglob("*.png"), key=lambda path: path.stat().st_mtime)


def remove_green_background(image: Image.Image) -> Image.Image:
    image = image.convert("RGBA")
    pixels = image.load()
    for y in range(image.height):
        for x in range(image.width):
            r, g, b, a = pixels[x, y]
            if a == 0:
                continue
            green_score = g - max(r, b)
            if g > 115 and green_score > 35:
                pixels[x, y] = (255, 208, 196, 0)
            elif g > 100 and green_score > 18:
                alpha = max(0, min(255, 255 - green_score * 5))
                pixels[x, y] = (r, g, b, min(a, alpha))
    return image


def fit_into_cell(frame: Image.Image) -> Image.Image:
    frame = remove_green_background(frame)
    bbox = frame.getbbox()
    cell = Image.new("RGBA", (CELL_W, CELL_H), (0, 0, 0, 0))
    if not bbox:
        return cell

    sprite = frame.crop(bbox)
    max_w = int(CELL_W * 0.88)
    max_h = int(CELL_H * 0.88)
    scale = min(max_w / sprite.width, max_h / sprite.height, 1.0)
    sprite = sprite.resize(
        (max(1, round(sprite.width * scale)), max(1, round(sprite.height * scale))),
        Image.Resampling.LANCZOS,
    )
    x = (CELL_W - sprite.width) // 2
    y = CELL_H - sprite.height - 10
    if y < 4:
        y = (CELL_H - sprite.height) // 2
    cell.alpha_composite(sprite, (x, y))
    if CELL_EDGE_CLEAR:
        alpha = cell.getchannel("A")
        for x0 in range(CELL_EDGE_CLEAR):
            for yy in range(CELL_H):
                alpha.putpixel((x0, yy), 0)
                alpha.putpixel((CELL_W - 1 - x0, yy), 0)
        for y0 in range(CELL_EDGE_CLEAR):
            for xx in range(CELL_W):
                alpha.putpixel((xx, y0), 0)
                alpha.putpixel((xx, CELL_H - 1 - y0), 0)
        cell.putalpha(alpha)
    return cell


def extract_row_frames(source: Image.Image, source_row: int, source_rows: int, source_cols: int = COLS) -> list[Image.Image]:
    source = source.convert("RGBA")
    row_h = source.height // source_rows
    row_top = source_row * row_h
    vertical_inset = max(4, round(row_h * FRAME_VERTICAL_INSET_RATIO))
    row = source.crop((0, row_top + vertical_inset, source.width, row_top + row_h - vertical_inset))

    frame_w = row.width // source_cols
    inset = max(6, round(frame_w * FRAME_INSET_RATIO))
    frames = []
    for col in range(COLS):
        crop = row.crop((col * frame_w + inset, 0, (col + 1) * frame_w - inset, row.height))
        frames.append(fit_into_cell(crop))
    return frames


def main() -> None:
    files = generated_pngs()
    atlas = Image.new("RGBA", (CELL_W * COLS, CELL_H * ROWS), (0, 0, 0, 0))
    for atlas_row in range(21):
        source_index, source_row, source_rows = ROW_SOURCES[atlas_row]
        source = Image.open(files[source_index]).convert("RGBA")
        frames = extract_row_frames(source, source_row, source_rows)
        for col, frame in enumerate(frames):
            atlas.alpha_composite(frame, (col * CELL_W, atlas_row * CELL_H))

    for atlas_row in range(21, ROWS):
        filename, source_row, source_rows, source_cols = EXTRA_ROW_SOURCES[atlas_row]
        source = Image.open(filename).convert("RGBA")
        frames = extract_row_frames(source, source_row, source_rows, source_cols)
        for col, frame in enumerate(frames):
            atlas.alpha_composite(frame, (col * CELL_W, atlas_row * CELL_H))

    atlas.save("spritesheet.generated_lulu.png")
    atlas.save("spritesheet.generated_lulu.webp", "WEBP", lossless=True, quality=100, method=6)
    atlas.save("spritesheet.webp", "WEBP", lossless=True, quality=100, method=6)
    atlas.crop((0, 0, CELL_W, CELL_H)).save("startup_frame.webp", "WEBP", lossless=True, quality=100, method=6)

    contact = Image.new("RGBA", atlas.size, (126, 158, 231, 255))
    contact.alpha_composite(atlas)
    contact.save("spritesheet_generated_lulu_contact.png")
    print("wrote spritesheet.generated_lulu.webp")
    print("wrote spritesheet.webp")
    print("wrote spritesheet_generated_lulu_contact.png")


if __name__ == "__main__":
    main()
