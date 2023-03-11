#!/usr/bin/env python3
import random
import hmac
import json
import os
import sys
import private.disker
from pathlib import Path

SECRET = b"pepeKITTYsockMIDNIGHTstupid"
PREFIX = "ugra_you_are_a_power_macintosh_user_"


def get_flag(user_id):
    user_id_enc = str(user_id).encode()
    suffix = hmac.new(SECRET, user_id_enc, "sha256").hexdigest()
    flag = PREFIX + suffix[:8]
    return flag


def generate(argv):
    try:
        user_id, workdir = argv[1:]
    except:
        print("Usage: generate.py user_id target_dir", file=sys.stderr)
        sys.exit(1)

    flag = get_flag(user_id)
    private.disker.generate(
        src_file=(Path("private") / "release-004.img"),
        dst_file=(Path(workdir) / "attachments" / "Ugra Classic.dsk"),
        app_name="Ugra Classic",
        flag=flag
    )

    return {
        "flags": [ flag ],
    }


def main():
    json.dump(generate(sys.argv), sys.stdout)

if __name__ == "__main__":
    main()
