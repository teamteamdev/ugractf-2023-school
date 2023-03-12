import requests

CAT_ART_3 = "／l、\n（ﾟ､ ｡７\nl、ﾞ~ヽ\nじしf_, )ノ\n"
CAT_ART_4 = "ฅ^•ﻌ•^ฅ\n"

def ror(value, count):
    mask = (8 - 1)
    count &= mask
    return (value >> count) | (value << ((-count) & mask))&0xff

def rol(value, count):
    mask = (8 - 1)
    count &= mask
    return ((value << count)&0xff) | (value >> ((-count) & mask))&0xff

def encrypt_1(str, key):
    dest = []
    for i in range(len(str)):
        dest.append((str[i] ^ key[i % len(key)])&0xff)
        if i % 2 == 0:
            dest[i] = ror(dest[i], 1)
        else:
            dest[i] = rol(dest[i], 1)
    return dest

def encrypt_2(str, key):
    dest = []
    for i in range(len(str)):
        dest.append((str[i] ^ key[i % len(key)])&0xff)
        if i % 2 == 0:
            dest[i] = rol(dest[i], 3)
        else:
            dest[i] = ror(dest[i], 2)
    return dest

def decrypt_1(str, key):
    dest = []
    for i in range(len(str)):
        if i % 2 == 0:
            dest.append(rol(str[i], 1))
        else:
            dest.append(ror(str[i], 1))
        dest[i] = (dest[i] ^ key[i % len(key)])&0xff
    return dest

def decrypt_2(str, key):
    dest = []
    for i in range(len(str)):
        if i % 2 == 0:
            dest.append(ror(str[i], 3))
        else:
            dest.append(rol(str[i], 2))
        dest[i] = (dest[i] ^ key[i % len(key)])&0xff
    return dest


b = """EB 1F 5E CC DE 63 49 AD 46 79 DE 8D 68 6E 42 B3 7E AA EB 15 6D D8 ED BF C8 BF 47 71 69 71 C8 DC EB""".replace(" ", "") # take it from 0x5160 offset in binary
b = bytes.fromhex(b)
dec = decrypt_1(b, CAT_ART_4.encode())
req_str = "".join(map(chr, dec))
print(req_str)

b = encrypt_2(req_str.encode(), CAT_ART_3.encode())
b = "".join(map(lambda x: f"{x:02X} ", b))

resp = requests.post("https://msr.s.2023.ugractf.ru/check", data={"check": b})
print(resp.text)

