"""Normalize input/skill-map.json: merge near-duplicate values, then place every
value in exactly one category.

Placement precedence is the order categories appear in the file, which is the
file's own documented tie-break. PLACEMENT overrides that where file order would
put a value in the wrong home - notably keeping tool names in "Tools & Platforms"
and the practices built on them in "Cloud & DevOps", so neither row goes thin.

Run: python scripts/normalize_skill_map.py
"""

import json
import os
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "input", "skill-map.json")

# Near-duplicate wording -> the single value that survives.
MERGE = {
    "Bash scripting": "Bash",
    "Schema design": "Database schema design",
    "Flyway database migrations": "Flyway",
    "Basic Linux administration": "Linux administration",
    "Linux": "Linux administration",
    "Nginx": "Nginx configuration",
    "Operational dashboards and filters": "Operational dashboards",
    "Role-based access control in the UI layer": "Role-based access control",
    "OpenID Connect sign-in flows": "OpenID Connect",
    "Data validation checks": "Data validation",
}

# Value -> category that owns it, overriding file order.
PLACEMENT = {
    "SQL": "Programming Languages",
    "PostgreSQL": "Databases",
    "MySQL": "Databases",
    "Redis": "Databases",
    "Database schema design": "Databases",
    "AWS (EC2, S3)": "Cloud & DevOps",
    "Git": "Tools & Platforms",
    "Maven": "Tools & Platforms",
    "Docker": "Tools & Platforms",
    "Docker Compose": "Tools & Platforms",
    "GitHub Actions": "Tools & Platforms",
    "Jenkins": "Tools & Platforms",
    "Flyway": "Tools & Platforms",
    "OpenAPI/Swagger": "Tools & Platforms",
    "Linux administration": "Cloud & DevOps",
    "Nginx configuration": "Cloud & DevOps",
    "Jenkins quality gates": "Cloud & DevOps",
    "Dependency and container scanning": "Cloud & DevOps",
    "Database migration planning": "Architecture & Design",
    "Data validation": "Data & AI",
}

RULE_TEXT = (
    "A value appears in exactly ONE category in this file, so the rendered rows "
    "cannot repeat it. Place it where it is listed; never copy it into a second "
    "row because the JD uses that wording."
)


def main():
    with open(PATH, encoding="utf-8") as fh:
        doc = json.load(fh, object_pairs_hook=OrderedDict)

    order = [c["label"] for c in doc["categories"]]
    rank = {label: i for i, label in enumerate(order)}

    # First pass: merge wording variants, then pick one owning category per value.
    owner, merged, dropped = {}, [], []
    for cat in doc["categories"]:
        for raw in cat["values"]:
            value = MERGE.get(raw, raw)
            if value != raw:
                merged.append((raw, value, cat["label"]))
            want = PLACEMENT.get(value)
            if want is not None:
                owner[value] = want
            elif value not in owner or rank[cat["label"]] < rank[owner[value]]:
                owner[value] = cat["label"]

    # Second pass: rebuild each category, keeping the original value order.
    for cat in doc["categories"]:
        kept, seen = [], set()
        for raw in cat["values"]:
            value = MERGE.get(raw, raw)
            if owner[value] != cat["label"]:
                dropped.append((raw, cat["label"], owner[value]))
                continue
            if value.lower() in seen:
                continue
            seen.add(value.lower())
            kept.append(value)
        # Values relocated into this category by PLACEMENT.
        for value, label in owner.items():
            if label == cat["label"] and value.lower() not in seen:
                seen.add(value.lower())
                kept.append(value)
        cat["values"] = kept

    doc["rules"]["no_duplicate_values"] = RULE_TEXT
    doc["version"] = doc.get("version", 1) + 1
    doc["updated"] = "2026-09-12"

    with open(PATH, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    total = sum(len(c["values"]) for c in doc["categories"])
    print(f"values: {total} | categories: {len(doc['categories'])}")
    for cat in doc["categories"]:
        print(f"  {len(cat['values']):3d}  {cat['label']}")
    print(f"\nmerged wording variants: {len(merged)}")
    for raw, value, label in merged:
        print(f"  [{label}] {raw} -> {value}")
    print(f"\nremoved as cross-category duplicates: {len(dropped)}")
    for raw, label, kept_in in dropped:
        print(f"  [{label}] {raw} (kept in {kept_in})")

    seen_all = {}
    for cat in doc["categories"]:
        for v in cat["values"]:
            assert v.lower() not in seen_all, f"{v} in both {seen_all[v.lower()]} and {cat['label']}"
            seen_all[v.lower()] = cat["label"]
    print("\nno value appears in two categories: True")


if __name__ == "__main__":
    main()
