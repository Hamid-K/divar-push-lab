#!/usr/bin/env python3
"""Combine source-linked app version observations without inventing releases."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
AGENTS = ROOT / "agents"
FIELDS = [
    "app", "package_id", "version_name", "version_code", "variant",
    "observed_date", "date_type", "source", "source_url", "artifact_type",
    "sha256", "record_scope", "notes",
]
APPS = [
    "Divar", "Rubika", "Eitaa", "Snapp", "Neshan", "Telewebion",
    "Balad", "Digikala", "Aparat", "Baam",
]
INPUTS = [
    "divar_versions.csv", "media_versions.csv", "mobility_versions.csv",
    "commerce_versions.csv",
]


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def bytes_in_hand(row: dict[str, str]) -> bool:
    """A listed checksum alone does not establish possession of the APK."""
    return bool(row["sha256"]) and row["artifact_type"] in {
        "exact APK", "APK verified from exact bytes", "base APK extracted from XAPK",
    }


def main() -> None:
    rows: list[dict[str, str]] = []
    for name in INPUTS:
        path = AGENTS / name
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != FIELDS:
                raise ValueError(f"{path}: expected {FIELDS}, got {reader.fieldnames}")
            for line_no, row in enumerate(reader, start=2):
                row = {key: (value or "").strip() for key, value in row.items()}
                if not row["app"] or not row["package_id"] or not row["version_name"]:
                    raise ValueError(f"{path}:{line_no}: missing app, package, or version")
                if row["app"] not in APPS:
                    raise ValueError(f"{path}:{line_no}: unexpected app {row['app']!r}")
                if not row["source_url"].startswith("https://"):
                    raise ValueError(f"{path}:{line_no}: source URL must be HTTPS")
                if row["sha256"] and (
                    len(row["sha256"]) != 64
                    or any(char not in "0123456789abcdef" for char in row["sha256"].lower())
                ):
                    raise ValueError(f"{path}:{line_no}: invalid SHA-256")
                rows.append(row)

    # Two independent sources for the same version are evidence, not duplicates.
    # Collapse only byte-for-byte identical observation records.
    seen: set[tuple[str, ...]] = set()
    unique: list[dict[str, str]] = []
    for row in rows:
        key = tuple(row[field] for field in FIELDS)
        if key not in seen:
            seen.add(key)
            unique.append(row)
    unique.sort(key=lambda row: (
        APPS.index(row["app"]), row["package_id"],
        row["observed_date"] or "9999", row["version_name"],
        row["version_code"], row["sha256"],
    ))
    write_csv(ROOT / "observed_versions.csv", FIELDS, unique)

    summary = []
    by_track: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in unique:
        by_track[row["app"], row["package_id"]].append(row)
    for app, package in sorted(by_track, key=lambda key: (APPS.index(key[0]), key[1])):
        group = by_track[app, package]
        dates = sorted(row["observed_date"][:10] for row in group if row["observed_date"])
        in_window = [row for row in group if row["record_scope"] == "in_window"]
        summary.append({
            "app": app,
            "package_id": package,
            "observation_rows": str(len(group)),
            "distinct_version_names": str(len({row["version_name"] for row in group})),
            "distinct_version_code_pairs": str(len({(row["version_name"], row["version_code"]) for row in group})),
            "version_names_with_in_window_observation": str(len({row["version_name"] for row in in_window})),
            "pre_2023_version_names": str(len({row["version_name"] for row in group if row["record_scope"] == "pre_2023_baseline"})),
            "undated_version_names": str(len({row["version_name"] for row in group if row["record_scope"] == "undated_unknown"})),
            "rows_with_sha256": str(sum(bool(row["sha256"]) for row in group)),
            "rows_with_local_bytes": str(sum(bytes_in_hand(row) for row in group)),
            "earliest_observation": dates[0] if dates else "",
            "latest_observation": dates[-1] if dates else "",
        })
    summary_fields = [
        "app", "package_id", "observation_rows", "distinct_version_names",
        "distinct_version_code_pairs", "version_names_with_in_window_observation",
        "pre_2023_version_names", "undated_version_names",
        "rows_with_sha256", "rows_with_local_bytes",
        "earliest_observation", "latest_observation",
    ]
    write_csv(ROOT / "coverage_summary.csv", summary_fields, summary)

    yearly = []
    for app, package in sorted(by_track, key=lambda key: (APPS.index(key[0]), key[1])):
        group = by_track[app, package]
        for year in range(2023, 2027):
            matched = [row for row in group if row["observed_date"].startswith(str(year))]
            yearly.append({
                "app": app, "package_id": package, "observation_year": str(year),
                "observation_rows": str(len(matched)),
                "distinct_version_names": str(len({row["version_name"] for row in matched})),
                "distinct_version_code_variant_keys": str(len({
                    (row["version_name"], row["version_code"], row["variant"])
                    for row in matched
                })),
                "rows_with_local_bytes": str(sum(bytes_in_hand(row) for row in matched)),
            })
    year_fields = [
        "app", "package_id", "observation_year", "observation_rows",
        "distinct_version_names", "distinct_version_code_variant_keys",
        "rows_with_local_bytes",
    ]
    write_csv(ROOT / "observation_years.csv", year_fields, yearly)

    # A target is one package/version/code/variant identity. This is still a
    # lower bound on APKs: a target can have more than one architecture or hash.
    by_target: dict[tuple[str, str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in unique:
        by_target[(
            row["app"], row["package_id"], row["version_name"],
            row["version_code"], row["variant"],
        )].append(row)
    targets = []
    for key in sorted(by_target, key=lambda item: (APPS.index(item[0]), item[1], item[2], item[3], item[4])):
        group = by_target[key]
        dates = sorted(row["observed_date"][:10] for row in group if row["observed_date"])
        hashes = sorted({row["sha256"] for row in group if row["sha256"]})
        local_hashes = sorted({row["sha256"] for row in group if bytes_in_hand(row)})
        # A 2025 archive reupload of a version observed in 2022 must not be
        # counted as a newly observed 2025 version target.
        first_scope = (
            "pre_2023_baseline" if dates and dates[0] < "2023-01-01"
            else "in_window" if dates else "undated_unknown"
        )
        status = "local_sample" if local_hashes else ("published_hash_only" if hashes else "catalog_only")
        targets.append({
            "app": key[0], "package_id": key[1], "version_name": key[2],
            "version_code": key[3], "variant": key[4],
            "first_observed_date": dates[0] if dates else "",
            "last_observed_date": dates[-1] if dates else "",
            "record_scope": first_scope,
            "observation_count": str(len(group)),
            "known_sha256_count": str(len(hashes)),
            "local_sample_count": str(len(local_hashes)),
            "acquisition_status": status,
            "representative_source_url": group[0]["source_url"],
        })
    target_fields = [
        "app", "package_id", "version_name", "version_code", "variant",
        "first_observed_date", "last_observed_date", "record_scope",
        "observation_count", "known_sha256_count", "local_sample_count",
        "acquisition_status", "representative_source_url",
    ]
    targets.sort(key=lambda row: (
        APPS.index(row["app"]), row["package_id"],
        row["first_observed_date"] or "9999", row["version_name"],
        row["version_code"], row["variant"],
    ))
    write_csv(ROOT / "version_targets.csv", target_fields, targets)
    write_csv(
        ROOT / "in_window_acquisition_targets.csv", target_fields,
        [row for row in targets if row["record_scope"] == "in_window" and row["acquisition_status"] != "local_sample"],
    )

    hashes_by_version = defaultdict(set)
    local_by_version = defaultdict(set)
    for row in unique:
        if row["sha256"]:
            hashes_by_version[row["app"], row["package_id"], row["version_name"]].add(row["sha256"])
        if bytes_in_hand(row):
            local_by_version[row["app"], row["package_id"], row["version_name"]].add(row["sha256"])
    queue = []
    seen_queue = set()
    for row in unique:
        if bytes_in_hand(row):
            continue
        key = (
            row["app"], row["package_id"], row["version_name"],
            row["version_code"], row["variant"], row["source_url"],
        )
        if key in seen_queue:
            continue
        seen_queue.add(key)
        queue.append({
            "app": row["app"], "package_id": row["package_id"],
            "version_name": row["version_name"],
            "version_code": row["version_code"], "variant": row["variant"],
            "observed_date": row["observed_date"],
            "date_type": row["date_type"], "source_url": row["source_url"],
            "artifact_type": row["artifact_type"],
            "published_sha256": row["sha256"],
            "hash_known_for_same_displayed_version": (
                "yes" if hashes_by_version[row["app"], row["package_id"], row["version_name"]] else "no"
            ),
            "local_bytes_for_same_displayed_version": (
                "yes" if local_by_version[row["app"], row["package_id"], row["version_name"]] else "no"
            ),
            "record_scope": row["record_scope"], "notes": row["notes"],
        })
    queue_fields = [
        "app", "package_id", "version_name", "version_code", "variant",
        "observed_date", "date_type", "source_url", "artifact_type",
        "published_sha256", "hash_known_for_same_displayed_version",
        "local_bytes_for_same_displayed_version", "record_scope", "notes",
    ]
    write_csv(ROOT / "acquisition_queue.csv", queue_fields, queue)
    print(f"{len(unique)} observations, {len(targets)} version targets, {len(summary)} package tracks, {len(queue)} acquisition leads without local bytes")
    print("By app:", dict(Counter(row["app"] for row in unique)))


if __name__ == "__main__":
    main()
