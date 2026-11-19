"""Draw the public example with Pillow. This script has no external image or font inputs."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
SCALE = 3
INK = "#442d31"
SHELL = "#c65f39"
CAP = "#ffcb80"
PINK = "#ef8e7a"
LEAF = "#457863"
MINT = "#a9d7a9"
PAPER = "#fff4de"

POSES = ("hello", "sprint", "rain", "sleep", "love", "peek", "cheer", "read")
Point = tuple[float, float]
Box = tuple[float, float, float, float]


class Canvas:
    def __init__(self, size: tuple[int, int], color: str | None = None):
        self.size = size
        self.image = Image.new("RGBA", (size[0] * SCALE, size[1] * SCALE), color)
        self.draw = ImageDraw.Draw(self.image)

    def oval(self, box: Box, color: str, outline: str | None = None, width: float = 1):
        self.draw.ellipse([round(n * SCALE) for n in box], color, outline, round(width * SCALE))

    def path(self, points: list[Point], color: str, width: float = 4):
        coords = [(round(x * SCALE), round(y * SCALE)) for x, y in points]
        self.draw.line(coords, fill=color, width=round(width * SCALE), joint="curve")
        r = width / 2
        for x, y in (points[0], points[-1]):
            self.oval((x - r, y - r, x + r, y + r), color)

    def shape(self, points: list[Point], color: str, outline: str | None = None, width: float = 4):
        self.draw.polygon([(round(x * SCALE), round(y * SCALE)) for x, y in points], color)
        if outline:
            self.path([*points, points[0]], outline, width)

    def curve(self, start: Point, *segments: tuple[Point, Point, Point]) -> list[Point]:
        points = [start]
        for a, b, end in segments:
            for step in range(1, 19):
                t = step / 18
                u = 1 - t
                points.append(tuple(
                    u**3 * p + 3 * u**2 * t * q + 3 * u * t**2 * r + t**3 * s
                    for p, q, r, s in zip(start, a, b, end)
                ))
            start = end
        return points

    def finish(self) -> Image.Image:
        return self.image.resize(self.size, Image.Resampling.LANCZOS)


def sparkle(c: Canvas, x: int, y: int, r: int, color: str):
    c.shape([(x, y-r), (x+r*.28, y-r*.3), (x+r, y),
             (x+r*.28, y+r*.3), (x, y+r), (x-r*.28, y+r*.3),
             (x-r, y), (x-r*.28, y-r*.3)], color)


def heart(c: Canvas, x: int, y: int, r: int):
    points = c.curve((x, y-r*.35),
                     ((x-r*.65, y-r*1.4), (x-r*1.7, y-r*.3), (x-r*.7, y+r*.4)),
                     ((x-r*.45, y+r*.7), (x-r*.1, y+r*.92), (x, y+r)),
                     ((x+r*.4, y+r*.7), (x+r*.6, y+r*.5), (x+r*.75, y+r*.32)),
                     ((x+r*1.6, y-r*.55), (x+r*.48, y-r*1.3), (x, y-r*.35)))
    c.shape(points, PINK, INK, 2.5)


def character(pose: str) -> Image.Image:
    c = Canvas((240, 240))
    # Limbs sit behind the shell; silhouette and props distinguish the actions.
    legs = {
        "sprint": [[(101,177),(85,191),(64,182)], [(140,177),(153,194),(177,183)]],
        "sleep": [[(102,176),(88,188),(75,188)], [(138,176),(150,189),(166,189)]],
        "cheer": [[(104,176),(88,192),(74,187)], [(139,175),(152,189),(164,178)]],
    }.get(pose, [[(102,177),(98,197),(84,197)], [(137,177),(143,197),(157,197)]])
    for leg in legs:
        c.path(leg, INK, 8)
    arms = {
        "hello": [[(76,137),(55,130),(50,107)], [(165,136),(179,147),(188,143)]],
        "sprint": [[(78,127),(55,120),(47,106)], [(164,135),(180,120),(189,126)]],
        "rain": [[(76,136),(62,147),(53,145)], [(162,137),(182,143),(189,130)]],
        "sleep": [[(83,148),(63,161),(51,156)], [(158,147),(172,161),(183,157)]],
        "love": [[(81,136),(64,145)], [(159,135),(177,144)]],
        "peek": [[(76,134),(63,111),(56,112)], [(166,133),(180,109),(188,111)]],
        "cheer": [[(82,131),(59,118),(48,88)], [(159,131),(180,114),(191,87)]],
        "read": [[(78,138),(61,149)], [(165,138),(178,148)]],
    }.get(pose, [[(80,135),(64,148),(56,142)], [(160,135),(175,148),(183,142)]])
    for arm in arms:
        c.path(arm, INK, 7)
    body = c.curve((118,48),
        ((116,71),(76,72),(58,113)), ((32,171),(78,187),(116,187)),
        ((160,191),(197,177),(189,140)), ((182,95),(139,85),(131,64)),
        ((126,56),(124,49),(118,48)))
    c.shape(body, SHELL, INK, 4.5)
    base = c.curve((57,152), ((76,145),(90,155),(109,155)),
                   ((137,159),(159,143),(184,151)), ((176,177),(156,184),(122,185)),
                   ((82,185),(64,177),(57,152)))
    c.shape(base, CAP)
    for x,y in [(76,161),(90,168),(108,164),(131,168),(146,160),(159,166)]:
        c.path([(x,y),(x+2,y+3)], "#bf854f", 2)
    c.path(c.curve((78,105), ((84,97),(93,91),(100,87))), "#ed9861", 3.5)
    for x in (90, 151):
        c.oval((x-8,134,x+6,139), PINK)
    for x in (98, 140):
        if pose in ("sleep","love","cheer"):
            sign = 1 if pose == "sleep" else -1
            c.path(c.curve((x-6,127), ((x-3,127+sign*7),(x+3,127+sign*7),(x+6,127))), INK, 3.5)
        else:
            shift = 3 if pose in ("peek","sprint") else 0
            c.oval((x-3+shift,120,x+3+shift,130), INK)
    if pose == "sleep":
        c.oval((116,136,122,142), INK)
    elif pose == "cheer":
        c.oval((112,130,128,143), INK)
    else:
        c.path(c.curve((115,134), ((117,139),(122,140),(126,134))), INK, 3)

    if pose == "hello":
        for k in range(3):
            c.path([(27+7*k,105-5*k),(20+8*k,99-8*k)], LEAF, 3.5)
    elif pose == "sprint":
        c.path([(25,115),(53,115)], LEAF, 4)
        c.path([(21,129),(43,129)], LEAF, 4)
        c.path([(33,144),(49,144)], LEAF, 4)
    elif pose == "rain":
        c.path([(188,132),(186,66)], INK, 3.5)
        canopy = c.curve((145,74), ((151,40),(197,29),(220,65)),
                         ((212,62),(201,63),(195,71)), ((185,64),(176,66),(168,75)),
                         ((160,69),(151,71),(145,74)))
        c.shape(canopy, MINT, INK, 3.5)
        for x,y in [(70,55),(49,73),(62,88),(102,36)]:
            c.path([(x,y),(x-4,y+7)], "#6eacbd", 3)
    elif pose == "sleep":
        c.oval((160,61,190,91), CAP, INK, 2.5)
        # Cut a crescent out of the transparent canvas.
        c.draw.ellipse([v*SCALE for v in (172,54,198,82)], fill=(0,0,0,0))
        sparkle(c, 192, 99, 5, LEAF)
    elif pose == "love":
        heart(c,120,152,31)
        c.oval((82,145,98,154), SHELL, INK, 3)
        c.oval((142,145,158,154), SHELL, INK, 3)
    elif pose == "peek":
        c.shape(c.curve((32,181), ((59,150),(89,152),(113,175)),
                        ((147,146),(186,147),(208,177)), ((173,212),(67,215),(32,181))),
                LEAF, INK, 3.5)
        c.path(c.curve((54,182), ((98,199),(165,194),(192,174))), MINT, 3.5)
    elif pose == "cheer":
        for x,y,r in [(32,75,9),(206,69,12),(164,44,7)]:
            sparkle(c,x,y,r,"#eaa94b")
    elif pose == "read":
        c.shape([(72,139),(99,139),(120,148),(142,138),(168,138),(163,170),
                 (141,170),(120,179),(99,169),(76,170)], MINT, INK, 3.5)
        c.path([(120,149),(120,177)], INK, 2.5)
        c.oval((65,147,80,157), SHELL, INK, 3)
        c.oval((161,146,177,156), SHELL, INK, 3)
    result = c.finish()
    if pose == "sprint":
        result = result.rotate(-14, Image.Resampling.BICUBIC)
    elif pose == "sleep":
        result = result.rotate(13, Image.Resampling.BICUBIC)
    return result


def place(canvas: Image.Image, art: Image.Image, center: Point, size: int):
    resized = art.resize((size, size), Image.Resampling.LANCZOS)
    canvas.alpha_composite(resized, (int(center[0]-size/2), int(center[1]-size/2)))


def landscape(size: tuple[int, int], theme: str) -> Image.Image:
    w,h = size
    colors = {"banner": ("#f6c98a","#86b59b"), "guide": ("#9ccbc0","#e4ae73"),
              "thanks": ("#f1bdaf","#92b292")}
    sky,hill = colors[theme]
    c = Canvas(size, sky)
    sun = int(w*.12)
    c.oval((w*.76-sun,h*.3-sun,w*.76+sun,h*.3+sun), PAPER)
    c.oval((-w*.4,h*.63,w*.86,h*1.5), hill)
    c.oval((w*.31,h*.77,w*1.4,h*1.5), LEAF)
    for x,y in [(w*.08,h*.62),(w*.14,h*.8),(w*.82,h*.82),(w*.89,h*.7)]:
        c.path([(x-5,y-5),(x,y),(x+5,y-8)], LEAF, 3)
    if theme == "guide":
        for x,y,r in [(155,119,14),(521,182,12),(611,223,8)]:
            sparkle(c,x,y,r,PAPER)
    if theme == "thanks":
        for x,y,r in [(130,206,20),(613,280,29),(529,131,16)]:
            heart(c,x,y,r)
    scene = c.finish()
    if theme == "banner":
        place(scene,character("read"),(w*.29,h*.69),int(h*.84))
        place(scene,character("sprint"),(w*.66,h*.64),int(h*.94))
    else:
        place(scene,character("cheer" if theme == "guide" else "love"),(w*.50,h*.59),int(min(w,h)*.98))
    return scene.convert("RGB")


def icon() -> Image.Image:
    c = Canvas((160,160), "#263f37")
    c.shape([(30,47),(104,27),(126,109),(51,128)], "#91bda3")
    c.shape([(43,44),(124,44),(124,100),(101,124),(43,124)], PAPER)
    c.shape([(100,101),(124,100),(101,124)], CAP)
    c.oval((62,63,102,97), SHELL)
    c.oval((72,74,76,80), INK)
    c.oval((87,74,91,80), INK)
    c.path(c.curve((77,84), ((80,87),(83,87),(86,84))), INK, 2)
    return c.finish().convert("RGB")


def main() -> None:
    stickers = ROOT / "stickers"
    supplementary = ROOT / "supplementary"
    stickers.mkdir(exist_ok=True)
    supplementary.mkdir(exist_ok=True)
    preview = Image.new("RGB", (960,480))
    backgrounds = ("#fcf2dc","#e0ecdb","#e3eef0","#e9e2ef","#f5ded7","#e0ecdb","#fcf2dc","#e3eef0")
    for index,(pose,bg) in enumerate(zip(POSES,backgrounds), 1):
        art = character(pose)
        art.save(stickers / f"{index:02d}-{pose}.png", optimize=True)
        tile = Image.new("RGBA",art.size,bg)
        tile.alpha_composite(art)
        preview.paste(tile,(((index-1)%4)*240,((index-1)//4)*240))
    preview.save(ROOT / "preview.png", optimize=True)
    neutral = character("neutral")
    neutral.save(supplementary / "cover.png", optimize=True)
    neutral.crop((40,49,199,208)).resize((50,50), Image.Resampling.LANCZOS).save(
        supplementary / "icon.png", optimize=True)
    landscape((750,400),"banner").save(supplementary / "banner.png", optimize=True)
    landscape((750,560),"guide").save(supplementary / "appreciation-guide.png", optimize=True)
    landscape((750,750),"thanks").save(supplementary / "appreciation-thanks.png", optimize=True)
    icon().save(ROOT / "toolkit-icon.png", optimize=True)


if __name__ == "__main__":
    main()
