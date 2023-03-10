import base64
import subprocess
import time
import io
from PIL import Image, ImageDraw, ImageFont


FLAG = "ugra_airgaps_can_be_bypassed_6m2amyh2xtwm"


def show_jab():
    f = io.BytesIO()
    im = Image.new("RGBA", (600, 64), "white")
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype("Ubuntu-R.ttf", size=30)
    draw.text((15, 15), FLAG, "black", font=font)
    im.save(f, "png")
    f.seek(0)
    data = base64.b64encode(f.read())

    for i in range(0, len(data), 100):
        subprocess.run(["jabcode/src/jabcodeWriter/bin/jabcodeWriter", "--input", data[i:i + 100], "--color-number", "4", "--output", "/tmp/frame.png"], check=True)

        im = Image.open("/tmp/frame.png")
        w, h = im.size
        pix = im.load()
        text = ""
        for y in range(6, h, 12):
            text += " " * (60 - w // 12)
            for x in range(6, w, 12):
                r, g, b, _ = pix[x, y]
                text += f"\x1b[48;2;{r};{g};{b}m  "
            text += "\x1b[0m\n"

        print("\x1b[H\x1b[J\n\n\n" + text, flush=True)
        time.sleep(0.2)


# show_jab()


print("\x1b[H\x1b[J")

print("LOGON TO MAINFRAME")
print("\x1b[31mAll unauthorized actions will be logged\nand the cause will be eliminated.\x1b[0m")
print()
input("Login: ")
input("Password: ")
print()
print(end="", flush=True)
time.sleep(2)
print("Authorization successful!")
print()


curdir = "/root"


while True:
    cmd = input(f"\x1b[32m{curdir}$\x1b[0m ")

    if cmd == "ls":
        if curdir == "/root":
            print("\x1b[34msecrets\x1b[0m")
        elif curdir == "/root/secrets":
            print("flag.png")
        print()
    elif cmd == "cd secrets":
        curdir = "/root/secrets"
        print()
    elif cmd == "jab --help":
        print("jab: JAB code encoder")
        print("Usage: jab <file>")
        print("Encodes the file via base64, splits it into chunks and outputs the chunks one by one to stdout")
        print()
    elif cmd == "jab flag.png":
        show_jab()

        print("\x1b[H\x1b[J")
        print("File transmitted successfully")
        print()

        print(f"\x1b[32m{curdir}$\x1b[0m ", end="", flush=True)

        time.sleep(1)
        print()
        print()
        while True:
            print("\x1b[G\x1b[31mPROBLEM DETECTED BETWEEN USER AND KEYBOARD\x1b[0m", end="", flush=True)
            time.sleep(0.5)
            print("\x1b[G\x1b[41mPROBLEM DETECTED BETWEEN USER AND KEYBOARD\x1b[0m", end="", flush=True)
            time.sleep(0.5)
