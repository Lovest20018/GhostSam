#!/usr/bin/env python3
"""Read independent S23 version metadata and validate an optional publication tag."""

import argparse
import json
from pathlib import Path
import re
import sys


VERSION = re.compile(r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:-(?:dev|(?:alpha|beta|rc)\.[1-9]\d*))?")


def metadata(root: Path, tag: str | None = None) -> dict[str, str]:
    config = json.loads((root / "maintenance/s23-baseline.json").read_text(encoding="utf-8"))
    product = config["product"]
    properties = {}
    for line in (root / product["version_file"]).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith(("#", "!")):
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key in properties:
            raise ValueError(f"Duplicate S23 version property: {key}")
        properties[key] = value.strip()
    name = properties["versionName"]
    if not VERSION.fullmatch(name):
        raise ValueError(f"Invalid independent S23 version: {name}")
    code = properties["versionCode"]
    if not re.fullmatch(r"[1-9]\d*", code) or not product["latest_published"]["version_code"] < int(code) <= 2100000000:
        raise ValueError("S23 versionCode must exceed the latest published build and fit Android's limit")
    expected_tag = product["tag_prefix"] + name
    notes = f"docs/releases/{expected_tag}.zh.md"
    if tag is not None:
        if tag != expected_tag:
            raise ValueError(f"Release tag must match the S23 version file: {expected_tag}")
        if name.endswith("-dev"):
            raise ValueError("Development versions produce artifacts only; choose a release candidate first")
        if not (root / notes).is_file() or not (root / notes).read_text(encoding="utf-8").strip():
            raise ValueError(f"Release notes required: {notes}")
    return {
        "product_name": product["name"],
        "application_id": product["application_id"],
        "version_name": name,
        "version_code": code,
        "release_tag": expected_tag,
        "release_notes": notes,
        "prerelease": "true",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", help="Validate this publication tag against the S23 version and notes")
    parser.add_argument("--github-output", type=Path, help="Append metadata to a GitHub Actions output file")
    args = parser.parse_args()
    try:
        result = metadata(Path(__file__).resolve().parents[1], args.tag)
        if args.github_output:
            with args.github_output.open("a", encoding="utf-8") as output:
                output.writelines(f"{key}={value}\n" for key, value in result.items())
    except (KeyError, OSError, ValueError) as error:
        print(f"s23-release: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
