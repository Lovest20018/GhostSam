#!/usr/bin/env python3
"""Prepare the pinned Samsung KernelSU source for Manager 3.3.1 (UAPI 5)."""

import argparse
from pathlib import Path
import subprocess
import sys


KERNELSU_REPOSITORY = "https://github.com/snothin/KernelSU.git"
KERNELSU_REF = "abbd7be7fb5e0af607c2a85e02efae03044bba86"
KERNELSU_BRANCH = "samsung"
UAPI_VERSION = 5
HEADER = "uapi/supercall.h"
OLD_DECLARATION = (
    "// TEMP (samsung): pinned to 2 to pair with the official v3.3.0 Manager (uapi 2).\n"
    "static const __u32 KERNEL_SU_UAPI_VERSION = 2;"
)
NEW_DECLARATION = "static const __u32 KERNEL_SU_UAPI_VERSION = 5;"


def git(source: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(source), *args], capture_output=True, check=False
    )
    if result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout


def read_source(source: Path, relative: str) -> str:
    return (source / relative).read_text(encoding="utf-8")


def validate_other_changes(source: Path) -> None:
    # Inspect both index and worktree; comparing only HEAD can hide staged changes.
    changes = set()
    for args in (("diff", "--name-only", "-z"), ("diff", "--cached", "--name-only", "-z")):
        changes.update(git(source, *args).split(b"\0"))
    changes.discard(b"")
    changes.discard(HEADER.encode("ascii"))
    if changes:
        paths = ", ".join(sorted(p.decode("utf-8", errors="replace") for p in changes))
        raise RuntimeError(f"Refusing modified KernelSU source outside {HEADER}: {paths}")


def prepare(source: Path) -> None:
    source = source.resolve(strict=True)
    root = Path(git(source, "rev-parse", "--show-toplevel").decode().strip()).resolve()
    if source != root:
        raise RuntimeError("Pass the KernelSU repository root, not a subdirectory")
    actual_ref = git(source, "rev-parse", "HEAD").decode().strip()
    if actual_ref != KERNELSU_REF:
        raise RuntimeError(f"Expected KernelSU HEAD {KERNELSU_REF}, found {actual_ref}")

    validate_other_changes(source)
    original = git(source, "show", f"HEAD:{HEADER}").decode("utf-8")
    if original.count(OLD_DECLARATION) != 1:
        raise RuntimeError("Pinned source does not contain the expected UAPI declaration")
    prepared = original.replace(OLD_DECLARATION, NEW_DECLARATION, 1)
    current = read_source(source, HEADER)
    if current not in (original, prepared):
        raise RuntimeError(f"Refusing unexpected modifications to {HEADER}")

    # These capabilities are already implemented at the pin. Never label an older
    # kernel UAPI 5 merely to suppress the Manager's compatibility warning.
    required = {
        "kernel/supercall/supercall.c": ("[ksu_driver_su]", "ksu_install_su_fd"),
        "kernel/supercall/dispatch.c": ("case EVENT_SERVICES:", "services_started"),
        "userspace/ksud/src/ksucalls.rs": ("pub fn report_services()", "SU_DRIVER_FD_NAME"),
        "uapi/app_profile.h": ("#define KSU_APP_PROFILE_VER 4",),
    }
    for relative, markers in required.items():
        text = read_source(source, relative)
        if any(marker not in text for marker in markers):
            raise RuntimeError(f"Missing required UAPI 5 source support in {relative}")

    patch = Path(__file__).resolve().parent / "patches" / "kernelsu-uapi5.patch"
    if current == original:
        git(source, "apply", "--check", str(patch))
        git(source, "apply", str(patch))
        action = "applied"
    else:
        git(source, "apply", "--reverse", "--check", str(patch))
        action = "already applied"

    validate_other_changes(source)
    if read_source(source, HEADER) != prepared:
        raise RuntimeError("Prepared UAPI header does not match the expected patch")
    print(f"KernelSU source: {KERNELSU_REPOSITORY} ({KERNELSU_BRANCH}) @ {actual_ref}")
    print(f"KernelSU UAPI: {UAPI_VERSION}; compatibility patch {action}")
    print("Rebuild ksud and every embedded kernelsu.ko from this prepared source.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="KernelSU repository root")
    args = parser.parse_args()
    try:
        prepare(args.source)
    except (OSError, RuntimeError, UnicodeError) as error:
        print(f"prepare-kernelsu: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
