#!/usr/bin/env python3
"""Run the shareable Divar YARA rules on raw DEX or DEX members of APKs."""

import argparse
import csv
import hashlib
import re
import sys
import zipfile
from pathlib import Path

import yara


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def inputs(paths):
    seen = set()
    for item in paths:
        path = Path(item)
        if not path.exists():
            raise FileNotFoundError(path)
        candidates = path.rglob("*") if path.is_dir() else [path]
        for candidate in candidates:
            if not candidate.is_file():
                continue
            if path.is_dir() and candidate.suffix.lower() not in {".apk", ".dex", ""}:
                continue
            if path.is_dir() and candidate.suffix == "":
                with candidate.open("rb") as stream:
                    if stream.read(4) not in {b"dex\n", b"PK\x03\x04"}:
                        continue
            resolved = candidate.resolve()
            if resolved not in seen:
                seen.add(resolved)
                yield candidate


def scan(path, rules, max_dex_bytes):
    with path.open("rb") as stream:
        sample_sha256 = hashlib.file_digest(stream, "sha256").hexdigest()
    base = {"sample": path.name, "sample_sha256": sample_sha256}
    with path.open("rb") as stream:
        is_dex = stream.read(4) == b"dex\n"
    if is_dex:
        if path.stat().st_size > max_dex_bytes:
            yield {**base, "member": "(raw DEX)", "dex_sha256": sample_sha256,
                   "rules": "", "error": "DEX exceeds size limit"}
            return
        sample = path.read_bytes()
        yield {**base, "member": "(raw DEX)", "dex_sha256": base["sample_sha256"],
               "rules": ";".join(sorted(m.rule for m in rules.match(data=sample))), "error": ""}
        return

    try:
        with zipfile.ZipFile(path) as archive:
            names = [name for name in archive.namelist()
                     if re.fullmatch(r"classes\d*\.dex", Path(name).name)]
            if not names:
                yield {**base, "member": "", "dex_sha256": "", "rules": "", "error": "no DEX member"}
            for name in names:
                info = archive.getinfo(name)
                if info.file_size > max_dex_bytes:
                    yield {**base, "member": name, "dex_sha256": "", "rules": "",
                           "error": "DEX exceeds size limit"}
                    continue
                data = archive.read(name)
                yield {**base, "member": name, "dex_sha256": sha256(data),
                       "rules": ";".join(sorted(m.rule for m in rules.match(data=data))), "error": ""}
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        yield {**base, "member": "", "dex_sha256": "", "rules": "",
               "error": f"{type(exc).__name__}: {exc}"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="APK/DEX files or directories to scan")
    parser.add_argument("--rules", type=Path,
                        default=Path(__file__).resolve().parents[1] / "rules/divar_dex_hunt.yar")
    parser.add_argument("--output", type=Path, help="CSV output; stdout if omitted")
    parser.add_argument("--max-dex-mib", type=int, default=128)
    args = parser.parse_args()
    if args.max_dex_mib < 1:
        parser.error("--max-dex-mib must be positive")
    for raw_path in args.paths:
        if not Path(raw_path).exists():
            parser.error(f"input does not exist: {raw_path}")
    compiled = yara.compile(filepath=str(args.rules))
    fields = ["sample", "sample_sha256", "member", "dex_sha256", "rules", "error"]
    destination = args.output.open("w", newline="") if args.output else sys.stdout
    try:
        writer = csv.DictWriter(destination, fieldnames=fields)
        writer.writeheader()
        for path in inputs(args.paths):
            writer.writerows(scan(path, compiled, args.max_dex_mib * 1024 * 1024))
    finally:
        if args.output:
            destination.close()


if __name__ == "__main__":
    main()
