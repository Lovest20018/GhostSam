#!/usr/bin/env python3
"""Reject stale or extra payloads in the dedicated S23 APK."""

import argparse
import hashlib
from pathlib import Path
import struct
import sys
import zipfile


KSUD_ASSET = "assets/payloads/ksud/ksud"
DFR_ASSET = "assets/payloads/dirtyfrag/dfr_lkm-android13-5.15.ko"


def check_elf(data: bytes, elf_type: int, name: str) -> None:
    if (
        len(data) < 64
        or data[:6] != b"\x7fELF\x02\x01"
        or struct.unpack_from("<HH", data, 16) != (elf_type, 183)
    ):
        raise ValueError(f"{name}: expected little-endian AArch64 ELF64 type {elf_type}")


def verify(apk: Path, ksud: Path, dfr_module: Path) -> dict[str, str]:
    expected = {KSUD_ASSET: ksud.read_bytes(), DFR_ASSET: dfr_module.read_bytes()}
    check_elf(expected[KSUD_ASSET], 3, "ksud")
    if b"(uapi: 5)" not in expected[KSUD_ASSET]:
        raise ValueError("ksud: missing UAPI 5 build marker")
    check_elf(expected[DFR_ASSET], 1, "DFR module")
    if len(expected[DFR_ASSET]) < 4096 or len(expected[DFR_ASSET]) % 4:
        raise ValueError("DFR module: expected >=4096 bytes and four-byte alignment")
    with zipfile.ZipFile(apk) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError("APK contains duplicate ZIP entries")
        payloads = {name for name in names if name.startswith("assets/payloads/") and not name.endswith("/")}
        if payloads != set(expected):
            raise ValueError(f"unexpected APK payload set: {sorted(payloads)}")
        if any(name.startswith("assets/companion/") for name in names):
            raise ValueError("S23 standalone APK must not include a companion APK")
        if "lib/arm64-v8a/libgsdfr_app.so" not in names:
            raise ValueError("APK is missing the arm64 standalone JNI library")
        for name, data in expected.items():
            if archive.read(name) != data:
                raise ValueError(f"{name}: APK differs from the checked build input")
    return {name: hashlib.sha256(data).hexdigest() for name, data in expected.items()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("apk", type=Path)
    parser.add_argument("--ksud", type=Path, required=True)
    parser.add_argument("--dfr-module", type=Path, required=True)
    args = parser.parse_args()
    try:
        hashes = verify(args.apk, args.ksud, args.dfr_module)
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        print(f"S23 APK verification failed: {error}", file=sys.stderr)
        return 1
    for name, digest in hashes.items():
        print(f"{digest}  {name}")
    print("S23 APK payload verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
