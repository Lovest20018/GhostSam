#!/usr/bin/env python3
"""Prepare the pinned Samsung KernelSU source for Manager 3.3.1 (UAPI 5)."""

import argparse
import hashlib
from pathlib import Path
import subprocess
import sys


KERNELSU_REPOSITORY = "https://github.com/snothin/KernelSU.git"
KERNELSU_REF = "abbd7be7fb5e0af607c2a85e02efae03044bba86"
KERNELSU_BRANCH = "samsung"
UAPI_VERSION = 5
HEADER = "uapi/supercall.h"
# Full-file hashes prevent unrelated edits inside the allowed files from
# silently entering a build. The observer backport is the upstream 3.3.1 file.
PATCHES = {
    HEADER: (
        "kernelsu-uapi5.patch",
        "6ccaeeb883d700ee14a4792429ce47013d12a3c580028510a24b91947b403c00",
    ),
    "kernel/manager/pkg_observer.c": (
        "kernelsu-manager-observer.patch",
        "1d5d6e37c111f724eab1166c73184ad1163851e4b769160689163e98c9e21598",
    ),
}


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
    changes.difference_update(relative.encode("ascii") for relative in PATCHES)
    if changes:
        paths = ", ".join(sorted(p.decode("utf-8", errors="replace") for p in changes))
        raise RuntimeError(f"Refusing modified KernelSU source outside audited patches: {paths}")


def prepare(source: Path) -> None:
    source = source.resolve(strict=True)
    root = Path(git(source, "rev-parse", "--show-toplevel").decode().strip()).resolve()
    if source != root:
        raise RuntimeError("Pass the KernelSU repository root, not a subdirectory")
    actual_ref = git(source, "rev-parse", "HEAD").decode().strip()
    if actual_ref != KERNELSU_REF:
        raise RuntimeError(f"Expected KernelSU HEAD {KERNELSU_REF}, found {actual_ref}")

    validate_other_changes(source)
    patch_dir = Path(__file__).resolve().parent / "patches"
    pending = []
    for relative, (filename, expected_digest) in PATCHES.items():
        original = git(source, "show", f"HEAD:{relative}").decode("utf-8")
        current = read_source(source, relative)
        if current == original:
            pending.append(str(patch_dir / filename))
        elif hashlib.sha256(current.encode("utf-8")).hexdigest() != expected_digest:
            raise RuntimeError(f"Refusing unexpected modifications to {relative}")

    # These capabilities are already implemented at the pin. Never label an older
    # kernel UAPI 5 merely to suppress the Manager's compatibility warning.
    required = {
        "kernel/supercall/supercall.c": ("[ksu_driver_su]", "ksu_install_su_fd"),
        "kernel/supercall/dispatch.c": ("case EVENT_SERVICES:", "services_started"),
        "userspace/ksud/src/ksucalls.rs": ("pub fn report_services()", "SU_DRIVER_FD_NAME"),
        "uapi/app_profile.h": ("#define KSU_APP_PROFILE_VER 4",),
        "kernel/hook/syscall_hook_manager.c": (
            "CONFIG_KSU_SAMSUNG_RKP", "samsung_setresuid_hook_init",
        ),
    }
    for relative, markers in required.items():
        text = read_source(source, relative)
        if any(marker not in text for marker in markers):
            raise RuntimeError(f"Missing required UAPI 5 source support in {relative}")

    if pending:
        # Check the complete set before modifying anything; apply is atomic.
        git(source, "apply", "--check", *pending)
        git(source, "apply", *pending)
        action = "applied"
    else:
        action = "already applied"

    validate_other_changes(source)
    for relative, (_, expected_digest) in PATCHES.items():
        digest = hashlib.sha256(read_source(source, relative).encode("utf-8")).hexdigest()
        if digest != expected_digest:
            raise RuntimeError(f"Prepared {relative} does not match the audited patch")
    print(f"KernelSU source: {KERNELSU_REPOSITORY} ({KERNELSU_BRANCH}) @ {actual_ref}")
    print(f"KernelSU UAPI: {UAPI_VERSION}; compatibility patch {action}")
    print("Manager installation observer: upstream 3.3.1 task_work backport")
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
