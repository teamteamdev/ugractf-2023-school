#!/usr/bin/env python3
import random
import hmac
import json
import os
import sys
from pathlib import Path


PREFIX = "ugra_wow_that_was_a_cool_cat_"
SECRET = b"baraBereIWANTTOEATYOU_but_you_are_a_cat"


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

def generate_secret_number(seed):
    random.seed(seed)
    return random.randint(100000, 10000000000)

def generate_string(SECRET_NUMBER):

    random.seed(SECRET_NUMBER)

    total_ram = random.randint(1337, 31337)
    ram = random.randint(0, total_ram)
    cpu_count = random.randint(30, 100)
    day = random.randint(0, 100)
    current_day = random.choice(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

    req_str = f"{ram}_{total_ram}_{current_day}_{cpu_count}_{day}_{SECRET_NUMBER}"

    return req_str


def generate_checksum(req_str):
    return encrypt_1(req_str.encode(), CAT_ART_4.encode())


def check_server_param(decrypted_req):
    try:
        string = "".join([chr(i) for i in decrypted_req])
        ram, total_ram, current_day, cpu_count, day, SECRET_NUMBER = string.split("_")
        ram = int(ram)
        total_ram = int(total_ram)
        cpu_count = int(cpu_count)
        day = int(day)
        SECRET_NUMBER = int(SECRET_NUMBER)
    except:
        return False, None
   
    
    real_string = generate_string(SECRET_NUMBER)
    if real_string != string:
        print(real_string, file=sys.stderr)
        return False, None
    
    return True, SECRET_NUMBER

def get_flag(num):
    num_enc = str(num).encode()
    suffix = hmac.new(SECRET, num_enc, "sha256").hexdigest()
    flag = PREFIX + suffix[:16]
    return flag

def generate(argv):
    try:
        user_id = argv[1]
        workdir = argv[2]
    except:
        print("Usage: generate.py user_id target_dir", file=sys.stderr)
        sys.exit(1)
    
    with open("msr.c", "r") as sf:
        source = sf.read()
    
    SECRET_NUMBER = generate_secret_number(user_id)
    req_str = generate_string(SECRET_NUMBER)
    checksum = generate_checksum(req_str)
    #c char array
    checksum_placeholder = ""
    for i in checksum:
        checksum_placeholder += f"{i},"
    checksum_placeholder = checksum_placeholder[:-1]
    source = source.replace("/*CHECKSUM_PLACEHOLDER*/", checksum_placeholder)

    checksum_len = len(checksum)
    source = source.replace("/*CHECKSUM_LEN_PLACEHOLDER*/0", str(checksum_len))
    
    os.makedirs(os.path.join(workdir, "attachments"), exist_ok=True)

    with open(os.path.join(workdir, "msr.c"), "w") as df:
        df.write(source)
    
    #Make with gcc
    rpath = os.path.join("attachments", "msr.elf")
    os.system(f"cd {workdir} && gcc -Wall -s msr.c -o {rpath} -lncurses")
    
    #delete c file
    os.system(f"cd {workdir} && rm msr.c")

    output = {
        "flags": [ get_flag(SECRET_NUMBER) ],
    }
    json.dump(output, sys.stdout)

if __name__ == "__main__":
    generate(sys.argv)
