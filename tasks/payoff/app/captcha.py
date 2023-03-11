import math
from random import sample, randint, choice
from itertools import product

from PIL import Image, ImageDraw, ImageFont, ImageOps

font = ImageFont.truetype('./AlumniSansCollegiateOne-Regular.ttf', 50)
size = 600


class WaveDeformer:

    def transform(self, x, y):
        y = y + 7 * math.sin(x / 40)
        return x, y

    def transform_rectangle(self, x0, y0, x1, y1):
        return (
            *self.transform(x0, y0),
            *self.transform(x0, y1),
            *self.transform(x1, y1),
            *self.transform(x1, y0),
        )

    def getmesh(self, img):
        self.w, self.h = img.size
        gridspace = 20

        target_grid = []
        for x in range(self.w // 8, 7 * self.w // 8, gridspace):
            for y in range(self.h // 8, 7 * self.h // 8, gridspace):
                target_grid.append((x, y, x + gridspace, y + gridspace))

        source_grid = [self.transform_rectangle(*rect) for rect in target_grid]

        return [t for t in zip(target_grid, source_grid)]


def generate(text: str) -> Image:
    im = Image.new('RGBA', (size, size), '#ffffffff')
    draw = ImageDraw.Draw(im)
    all_places = [
        list(p)
        for p in product(range(2 * size // 8, 6 * size // 8, 30), repeat=2)
    ]
    places = sample(all_places, len(text))
    for letter, hue, (x, y) in zip(text, range(0, 360, 360 // len(text)),
                                   places):
        color = f'hsv({hue}, 100%, 100%)'
        x += randint(-10, 10)
        y += randint(-10, 10)
        draw.text((x, y), letter, fill=color, anchor='mm', font=font)

    def draw_circle():
        x, y = choice(all_places)
        for _ in range(randint(0, 3)):
            r = randint(10, 100)
            bb = [x - r, y - r, x + r, y + r]
            color = f'hsv({randint(0, 360)}, {randint(0, 100)}%, {randint(0, 100)}%)'
            draw.arc(bb, 0, 360, fill=color, width=randint(3, 6))

    for _ in range(randint(len(text) // 4, len(text) // 2)):
        draw_circle()

    deformed = ImageOps.deform(im, WaveDeformer())
    return deformed
