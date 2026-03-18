import math
import random
import time
import hashlib
import os


WIDTH = 80
HEIGHT = 28
STAR_COUNT = 140
CONSTELLATION_POINTS = 10
FRAME_DELAY = 0.05
FRAMES = 220


def make_seed(text):
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def lerp(a, b, t):
    return a + (b - a) * t


def distance(a, b):
    return math.sqrt((a["x"] - b["x"]) ** 2 + (a["y"] - b["y"]) ** 2)


def make_stars(seed_text):
    rng = random.Random(make_seed(seed_text))
    stars = []

    for _ in range(STAR_COUNT):
        star = {
            "x": rng.uniform(0, WIDTH - 1),
            "y": rng.uniform(0, HEIGHT - 1),
            "size": rng.choice([1, 1, 1, 2, 2, 3]),
            "twinkle_speed": rng.uniform(0.03, 0.15),
            "twinkle_offset": rng.uniform(0, math.pi * 2),
            "drift_x": rng.uniform(-0.03, 0.03),
            "drift_y": rng.uniform(-0.015, 0.015),
        }
        stars.append(star)

    return stars


def pick_constellation_nodes(stars, seed_text):
    rng = random.Random(make_seed(seed_text) + 999)
    chosen = rng.sample(stars, CONSTELLATION_POINTS)
    chosen = sorted(chosen, key=lambda s: (s["x"], s["y"]))
    return chosen


def build_constellation_lines(nodes):
    lines = []
    remaining = nodes[:]
    current = remaining.pop(0)

    while remaining:
        next_star = min(remaining, key=lambda s: distance(current, s))
        lines.append((current, next_star))
        remaining.remove(next_star)
        current = next_star

    return lines


def draw_line(canvas, x1, y1, x2, y2, char="."):
    dx = x2 - x1
    dy = y2 - y1
    steps = int(max(abs(dx), abs(dy)))

    if steps == 0:
        return

    for i in range(steps + 1):
        t = i / steps
        x = round(lerp(x1, x2, t))
        y = round(lerp(y1, y2, t))

        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            if canvas[y][x] == " ":
                canvas[y][x] = char


def star_char(size, brightness):
    if size == 3:
        return "@" if brightness > 0.65 else "O"
    if size == 2:
        return "*" if brightness > 0.5 else "+"
    return "." if brightness > 0.45 else "·"


def render_frame(stars, lines, frame, title):
    canvas = [[" " for _ in range(WIDTH)] for _ in range(HEIGHT)]

    for star in stars:
        x = star["x"] + math.sin(frame * 0.02 + star["twinkle_offset"]) * star["drift_x"] * 12
        y = star["y"] + math.cos(frame * 0.018 + star["twinkle_offset"]) * star["drift_y"] * 12

        brightness = (
            math.sin(frame * star["twinkle_speed"] + star["twinkle_offset"]) + 1
        ) / 2

        px = int(x)
        py = int(y)

        if 0 <= px < WIDTH and 0 <= py < HEIGHT:
            canvas[py][px] = star_char(star["size"], brightness)

    for a, b in lines:
        ax = int(a["x"])
        ay = int(a["y"])
        bx = int(b["x"])
        by = int(b["y"])
        draw_line(canvas, ax, ay, bx, by, char=":")

    header = " seeded galaxy // " + title[: WIDTH - 20]
    for i, ch in enumerate(header):
        if i < WIDTH:
            canvas[0][i] = ch

    return "\n".join("".join(row) for row in canvas)


def animate(seed_text):
    stars = make_stars(seed_text)
    nodes = pick_constellation_nodes(stars, seed_text)
    lines = build_constellation_lines(nodes)

    for frame in range(FRAMES):
        clear()
        print(render_frame(stars, lines, frame, seed_text))
        time.sleep(FRAME_DELAY)


if __name__ == "__main__":
    phrase = input("Name your galaxy: ").strip()

    if phrase == "":
        phrase = "untitled sky"

    try:
        animate(phrase)
    except KeyboardInterrupt:
        print("\nClosed by user.")
