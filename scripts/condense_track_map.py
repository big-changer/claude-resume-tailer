"""Rewrite input/track-map.json as data only.

The selection algorithm is documented in .claude/skills/resume-jd-optimizer/SKILL.md
Step 3. This file previously restated it in `rules.matching`, `rules.order` and
`rules.step_1..step_4`, so the two could drift apart. Those keys are dropped, along
with `strength`, `max_tracks`, `primary_supplies` and `secondary_supplies`, which
nothing reads. Every key SKILL.md and manifest.json reference is preserved:

  tracks[].file / .label / .titles / .keywords / .default_secondary / .caveats
  caveats[].when / .always / .action / .log
  global_caveats, domain_boost, no_fit.keywords / .fallback_track / .log
  rules.min_keyword_hits, rules.secondary_threshold

`caveats[].action` is "select_anyway" for every entry and SKILL.md documents that
meaning, so it stays on each entry rather than becoming an implicit default.

Run: python scripts/condense_track_map.py
"""

import json
import os
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "input", "track-map.json")

# Caveat log texts, shortened. Each still names what is missing and what to do.
LOGS = {
    "devops_iac": (
        "No infrastructure-as-code or cluster work is recorded. devops is the closest "
        "track; claim none of this. Needs real infrastructure work in input/projects.md."
    ),
    "enterprise_vendor": (
        "No named ERP or CRM vendor platform is recorded, only generic ERP and accounting "
        "integration over REST APIs and scheduled data exchange. Add real platform names "
        "to Section 1 if the candidate has used them."
    ),
    "ai_always": (
        "AI-Assisted Case Servicing Copilot and AI-Assisted Reconciliation Triage in "
        "input/projects.md evidence LLM API integration, RAG, semantic retrieval, "
        "summarization, classification, anomaly scoring and their safeguards, at First "
        "Horizon Bank from July 2022. Neither records a model provider, vector store, "
        "embedding model, framework, evaluation method, or any accuracy, adoption or "
        "time-saved figure. Claim the capability and the guardrails, never a named tool "
        "and never an AI number."
    ),
    "ai_python_ml": (
        "Recorded AI work is Java and Spring Boot applied-AI integration only. Python and "
        "its AI ecosystem, model training and fine-tuning, MLOps, agentic tool-calling and "
        "formal evaluation harnesses are recorded nowhere. If the posting makes one a hard "
        "bar, report a structural mismatch rather than bridging to it."
    ),
    "years": (
        "Record supports 7+ years, March 2019 to present. Do not inflate the headline or "
        "summary. If the JD makes the year count a hard bar, log a structural mismatch."
    ),
    "profile_links": (
        "No LinkedIn or GitHub URL is recorded in Sections 5 and 6 of input/profile.md, so "
        "those fields are omitted from the contact line. Add real URLs to close this."
    ),
    "no_fit": (
        "JD is outside every track the record covers. Generated from master-resume-fs.md "
        "as the general software engineering fallback."
    ),
}


NL = "\n"


def fmt(obj, indent=0, width=94):
    """Pretty JSON, but arrays of scalars wrap inline instead of one item per line."""
    pad = " " * indent
    if isinstance(obj, dict):
        if not obj:
            return "{}"
        parts = [f"{pad}  {json.dumps(k, ensure_ascii=False)}: {fmt(v, indent + 2, width)}"
                 for k, v in obj.items()]
        return "{" + NL + ("," + NL).join(parts) + NL + pad + "}"
    if isinstance(obj, list):
        if not obj:
            return "[]"
        if all(not isinstance(x, (dict, list)) for x in obj):
            items = [json.dumps(x, ensure_ascii=False) for x in obj]
            one = "[" + ", ".join(items) + "]"
            if indent + len(one) <= width:
                return one
            lines, cur = [], ""
            for i, it in enumerate(items):
                piece = it + ("," if i < len(items) - 1 else "")
                candidate = (cur + " " + piece) if cur else piece
                if cur and indent + 2 + len(candidate) > width:
                    lines.append(cur)
                    cur = piece
                else:
                    cur = candidate
            if cur:
                lines.append(cur)
            return "[" + NL + pad + "  " + (NL + pad + "  ").join(lines) + NL + pad + "]"
        parts = [f"{pad}  {fmt(x, indent + 2, width)}" for x in obj]
        return "[" + NL + ("," + NL).join(parts) + NL + pad + "]"
    return json.dumps(obj, ensure_ascii=False)


def caveat(when, log, always=False):
    entry = OrderedDict()
    if always:
        entry["always"] = True
    else:
        entry["when"] = when
    entry["action"] = "select_anyway"
    entry["log"] = log
    return entry


def main():
    with open(PATH, encoding="utf-8") as fh:
        old = json.load(fh, object_pairs_hook=OrderedDict)

    doc = OrderedDict()
    doc["_comment"] = (
        "Maps job-description text to input/master-resume-{track}.md files. The 'tracks' "
        "object is authoritative: a track absent from it has no file and cannot be "
        "selected. Data only - the selection algorithm lives in Step 3 of "
        ".claude/skills/resume-jd-optimizer/SKILL.md."
    )
    doc["version"] = old.get("version", 1) + 1
    doc["updated"] = "2026-09-12"

    doc["rules"] = OrderedDict([
        ("min_keyword_hits", 2),
        ("secondary_threshold", 0.5),
    ])

    tracks = OrderedDict()
    src = old["tracks"]
    for key in ("fs", "data", "devops", "enterprise", "ai"):
        t = src[key]
        entry = OrderedDict()
        entry["file"] = t["file"]
        entry["label"] = t["label"]
        entry["default_secondary"] = t["default_secondary"]
        entry["titles"] = t["titles"]
        entry["keywords"] = t["keywords"]
        if key == "devops":
            entry["caveats"] = [caveat(t["caveats"][0]["when"], LOGS["devops_iac"])]
        elif key == "enterprise":
            entry["caveats"] = [caveat(t["caveats"][0]["when"], LOGS["enterprise_vendor"])]
        elif key == "ai":
            entry["caveats"] = [
                caveat(None, LOGS["ai_always"], always=True),
                caveat(t["caveats"][1]["when"], LOGS["ai_python_ml"]),
            ]
        else:
            entry["caveats"] = []
        tracks[key] = entry
    doc["tracks"] = tracks

    doc["domain_boost"] = OrderedDict([
        ("_comment", "Healthcare delivery is recorded behind these tracks, so a healthcare "
                     "posting favours them. Adds 'points' to each track's keyword score."),
        ("keywords", old["domain_boost"]["keywords"]),
        ("boost_tracks", old["domain_boost"]["boost_tracks"]),
        ("points", old["domain_boost"]["points"]),
    ])

    doc["global_caveats"] = [
        caveat(old["global_caveats"][0]["when"], LOGS["years"]),
        caveat(old["global_caveats"][1]["when"], LOGS["profile_links"]),
    ]

    doc["no_fit"] = OrderedDict([
        ("_comment", "No track file covers these. Use fallback_track as primary with no "
                     "secondary, and log the mismatch at Step 8."),
        ("fallback_track", old["no_fit"]["fallback_track"]),
        ("log", LOGS["no_fit"]),
        ("keywords", old["no_fit"]["keywords"]),
    ])

    doc["examples"] = OrderedDict([
        ("_comment", "Primary comes from the title; secondary is scored against the whole "
                     "posting body, so these assume a full JD."),
        ("cases", [
            OrderedDict([("jd", e["jd"]), ("primary", e["primary"]),
                         ("secondary", e["secondary"]), ("why", e["why"])])
            for e in old["examples"] if "jd" in e
        ]),
    ])

    with open(PATH, "w", encoding="utf-8") as fh:
        fh.write(fmt(doc) + "\n")

    print("top-level keys:", list(doc))
    print("tracks:", list(doc["tracks"]))
    print("examples:", len(doc["examples"]["cases"]))


if __name__ == "__main__":
    main()
