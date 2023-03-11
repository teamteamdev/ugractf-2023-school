from re import TEMPLATE
import macresources as rsrc
from PIL import Image, ImageDraw, ImageFont
import machfs as hfs
import subprocess
import tempfile
import io
import os

FONT = ImageFont.truetype("private/sysfont.ttf", size=14)
TEMPLATE = Image.open("private/template.png")

DISKETTE = 1440 * 1024 # bytes
PICT_HEADER = b'\x00' * 512
MAGICK = "magick"


def open_volume(path) -> hfs.Volume:
    v = hfs.Volume()
    with open(path, 'rb') as img:
        v.read(img.read())
    return v


def save_volume(path: str, vol: hfs.Volume, size=DISKETTE) -> int:
    with open(path, 'wb') as img:
        return img.write(vol.write(
            size=size,
            align=512,
            desktopdb=True,
            bootable=False
        ))


def dump(data, path):
    with open(path, 'wb') as f:
        return f.write(data)

# dumper = lambda file: lambda data: dump(data, file)
# p = dumper(tempfile.TemporaryFile())


def ensure_run(args):
    try:
        return subprocess.check_output(args)
    except subprocess.CalledProcessError as e:
        print(e.output)
        raise e


def pict_unpack(rsrc):
    with tempfile.TemporaryDirectory() as cwd:
        pict_path = cwd + "/p.pict"
        png_path  = cwd + "/p.png"
        dump(PICT_HEADER + x, pict_path)
        ensure_run([MAGICK, pict_path, png_path])
        with open(png_path, 'rb') as png:
            return png.read()


def png_to_pict(png):
    with tempfile.TemporaryDirectory() as cwd:
        pict_path = cwd + "/p.pict"
        png_path = cwd + "/p.png"
        with open(png_path, 'wb') as png_file:
            png_file.write(png)
        ensure_run([MAGICK, png_path, pict_path])
        with open(pict_path, 'rb') as pict_file:
            pict = pict_file.read()
            return pict


def pict_pack(png, id, name=None):
    pict = png_to_pict(png)
    return rsrc.Resource(
        type=b'PICT',
        id=id,
        name=name,
        data=pict[512:] # sans header
    )


def hfs_file_context(volume_path, file_name):
    disk = open_volume(volume_path)
    app = disk[file_name]
    app_rsrc = list(rsrc.parse_file(app.rsrc))
    return disk, app, app_rsrc


def write(text, im, fill, deltas = (0, 0)):
    draw = ImageDraw.Draw(im)
    draw.fontmode = '1'
    txt_w = FONT.getlength(text)
    dx, dy = deltas
    draw.text(
        (((im.width - txt_w) // 2) + dx, 15 + dy),
        text, font=FONT, fill=fill
    )


def draw_flag(flag):
    im = Image.new("RGB", (400, 300), "black")
    # drawing
    im.paste(TEMPLATE, (0, 0))
    write(flag, im, "white")
    write("hang up.", im, "black", (-4, 300 - 64 - 15))
    # saving
    new_png = io.BytesIO()
    im.save(new_png, format="PNG")
    return new_png.getvalue()


def generate(src_file, dst_file, app_name, flag):
    disk, app, app_rsrc = hfs_file_context(src_file, app_name)
    png = draw_flag(flag)
    flag_pict = pict_pack(png, 1337)

    new_disk = hfs.Volume()
    new_disk.name = 'Ugra Classic'
    new_disk[app_name] = app
    new_disk[app_name].rsrc = rsrc.make_file(app_rsrc + [flag_pict])

    return save_volume(
        dst_file,
        new_disk
    )
