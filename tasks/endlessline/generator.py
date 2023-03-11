#!/usr/bin/env python3
import hmac
import json
import sys

SECRET = "helloWORLDthisISaSUPERsecureSECRETseed"
SUFFIX_SIZE = 12
PREFIX = "ugra_spasibo_za_ozhidaniye_"

TOKEN_SECRET = "ooooThisIsADifferentOneHowFancy"
TOKEN_SALT_SIZE = 16

import hashlib

def get_flag(token):
    suffix = hashlib.sha256((SECRET + token).encode()).hexdigest()[:SUFFIX_SIZE]
    return PREFIX + suffix

def get_token(user_id):
    token = hmac.new(TOKEN_SECRET.encode(), str(user_id).encode(), "sha256").hexdigest()[:TOKEN_SALT_SIZE]
    return token

def generate(argv):
    try:
        user_id, workdir = argv[1:]
    except:
        print("Usage: generate.py user_id target_dir", file=sys.stderr)
        sys.exit(1)

    token = get_token(user_id)
    flag = get_flag(token)
    
    return {
        "flags": [ flag ],
        "substitutions": {},
        "urls": [f"https://endlessline.{{hostname}}/{token}/"]
    }



def main():
    json.dump(generate(sys.argv), sys.stdout)

if __name__ == "__main__":
    main()