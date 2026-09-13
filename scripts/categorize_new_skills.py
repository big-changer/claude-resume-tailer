import re, json, glob, os, collections, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skill_atoms import ATOMS, MERGE, DROP_LANGUAGES

ROOT = "F:/Work/Applications/claude-resume-tailer-washington"

PY_AI = [
    r"\bpython\b", r"\bdjango\b", r"\bfastapi\b", r"\bflask\b", r"\bbottle\b", r"\baiohttp\b",
    r"\bcelery\b", r"\bsqlalchemy\b", r"\bpandas\b", r"\bnumpy\b", r"\bscipy\b", r"scikit",
    r"tensorflow", r"pytorch", r"\bpyspark\b", r"pyzeebe", r"\bjupyter\b",
    r"\bai\b", r"\ba\.i\.", r"\bllm", r"\bml\b", r"\bmlops\b", r"machine learning",
    r"generative ai", r"artificial intelligence", r"\bnlp\b", r"neural network",
    r"\bagent", r"agentic", r"prompt", r"\brag\b", r"retrieval-augmented",
    r"langchain", r"\bmcp\b", r"anthropic", r"openai", r"claude", r"copilot", r"cursor",
    r"bedrock", r"gemini", r"llama", r"mistral", r"vector database", r"embedding",
    r"model drift", r"predictive model", r"statistic", r"causal inference",
    r"data scien", r"segmentation modeling", r"evals", r"computational linguistics",
    r"semantic search", r"\bcuda\b", r"\bgpu\b",
]
JAVA = [
    r"\bjava\b", r"\bjvm\b", r"\bj2ee\b", r"jakarta ee", r"\bejb\b", r"\bspring\b",
    r"hibernate", r"\bstruts\b", r"\bjsp\b", r"\bjboss\b", r"\bgroovy\b", r"\bgradle\b",
    r"\bmaven\b", r"\bjms\b", r"activemq", r"\bjaxb\b", r"\bcxf\b", r"\bcamel\b",
    r"intellij idea", r"\beclipse\b", r"\bkotlin\b", r"\bjwt\b", r"json web token",
    r"design patterns, data structures and collections",
]

def hits(pats, text):
    return [p for p in pats if re.search(p, text, re.I)]

OVERRIDES = {
    "json web tokens (jwt)": "other",
    "jwt and token management": "other",
    "swift, kotlin, native ios and android": "other",   # mobile, not JVM back end
    "orchestration for scheduled model runs": "python_ai",
    "fairness and subgroup performance evaluation": "python_ai",
    "model drift monitoring in production": "python_ai",
    "statsig or another experimentation platform": "other",
}

def classify(name, body):
    """Classify on the SKILL NAME only. Bodies always say "Nearest recorded: Java/Spring ...",
    which is the candidate's existing stack, not the skill being detected."""
    key = name.lower().strip()
    if key in OVERRIDES:
        return OVERRIDES[key], ["manual override"]
    jn, pn = hits(JAVA, name), hits(PY_AI, name)
    if jn and pn: return "java", jn + pn
    if jn:        return "java", jn
    if pn:        return "python_ai", pn
    return "other", []

entries = []
for path in sorted(glob.glob(os.path.join(ROOT, "data/*/new-skills.md"))):
    slug = os.path.basename(os.path.dirname(path))
    lines = open(path, encoding="utf-8").read().splitlines()
    company = role = posted = track = None
    buf = None
    def flush():
        global buf
        if buf:
            raw = " ".join(x.strip() for x in buf["lines"]).strip()
            m = re.match(r"-\s*\*\*(.+?)\*\*\s*[-–—:]?\s*(.*)$", raw, re.S)
            if m:
                name, body = m.group(1).strip(), m.group(2).strip()
            else:
                name, body = re.sub(r"^-\s*\*\*", "", raw).strip(), ""
            name = re.sub(r"\s+", " ", name).lstrip("- ").strip()
            body = re.sub(r"\s+", " ", body)
            cat, sig = classify(name, body)
            entries.append(dict(skill=name, category=cat, matched_signals=sig,
                                slug=buf["slug"], posted=buf["posted"], company=buf["company"],
                                role=buf["role"], track=buf["track"], detail=body))
        buf = None
    for ln in lines:
        if ln.startswith("## "):
            flush()
            parts = [x.strip() for x in ln[3:].split("|")]
            posted = parts[0] if parts else None
            company = parts[1] if len(parts) > 1 else None
            role = parts[2] if len(parts) > 2 else None
            track = None
        elif ln.startswith("### "):
            flush(); track = ln[4:].strip()
        elif ln.startswith("- "):
            flush()
            buf = dict(lines=[ln], slug=slug, posted=posted, company=company, role=role, track=track)
        elif buf is not None and ln.strip() and ln.startswith(("  ", "\t")):
            buf["lines"].append(ln)
        elif not ln.strip():
            flush()
    flush()

# --- canonicalize name variants so one skill never lands in two files -------
def canon(n):
    """Canonical key so name variants of one skill merge into a single record."""
    n = n.lower()
    n = re.sub(r"\([^)]*\)", " ", n)          # drop parentheticals
    n = re.sub(r"[^a-z0-9+#./ -]", " ", n)
    n = re.sub(r"\b\d+\+?\b", " ", n)     # version / year numbers
    n = re.sub(r"\b(?:as a|named|stated|generally|specific|preferred|modern|"
               r"advanced|comparable|equivalent|or|and|the|an|a|practices|practice|"
               r"tooling|tools|platforms|platform|frameworks|framework|design|"
               r"development|experience|competency)\b", " ", n)
    return re.sub(r"[\s./-]+", " ", n).strip()

# Assignment precedence: a skill goes to the FIRST bucket that claims it.
PRECEDENCE = ["other", "java", "python_ai"]

groups = collections.OrderedDict()
for e in entries:
    key = canon(e["skill"]) or e["skill"].lower()
    g = groups.setdefault(key, dict(canonical_key=key, skill=e["skill"], aliases=[],
                                    categories=set(), matched_signals=[], occurrences=[]))
    if len(e["skill"]) < len(g["skill"]):
        g["skill"] = e["skill"]                 # shortest variant is the canonical label
    if e["skill"] not in g["aliases"]:
        g["aliases"].append(e["skill"])
    g["categories"].add(e["category"])
    for sig in e["matched_signals"]:
        if sig not in g["matched_signals"]:
            g["matched_signals"].append(sig)
    g["occurrences"].append(dict(slug=e["slug"], posted=e["posted"], company=e["company"],
                                 role=e["role"], track=e["track"], detail=e["detail"],
                                 as_written=e["skill"]))

for g in groups.values():
    g["category"] = next(c for c in PRECEDENCE if c in g["categories"])
    g["also_matched"] = sorted(g["categories"] - {g["category"]})
    g["aliases"] = [a for a in g["aliases"] if a != g["skill"]]
    del g["categories"]

outdir = os.path.join(ROOT, "data/skills-categorized")
os.makedirs(outdir, exist_ok=True)
files = {"other": "other-skills.md", "java": "java-skills.md",
         "python_ai": "python-ai-skills.md"}
titles = {"other": "Other skills", "java": "Java-relevant skills",
          "python_ai": "Python / AI-relevant skills"}

# Buckets whose compound phrases are split into individual skills via ATOMS.
ATOMIZE = {"other"}
unmapped = []

def atomize(label):
    """Split one compound JD phrase into its individual skills."""
    atoms = ATOMS.get(label)
    if atoms is None:
        unmapped.append(label)
        atoms = [label]
    atoms = [MERGE.get(a, a) for a in atoms]
    return [a for a in atoms if a.lower() not in DROP_LANGUAGES]

counts, seen = {}, {}
for cat, fn in files.items():
    items = [v for v in groups.values() if v["category"] == cat]
    if cat in ATOMIZE:
        names, order = {}, []
        for v in sorted(items, key=lambda v: v["skill"].lower()):
            for atom in atomize(v["skill"]):
                key = atom.lower()
                if key not in names:
                    names[key] = atom
                    order.append(key)
        labels = sorted((names[k] for k in order), key=str.lower)
    else:
        labels = sorted((v["skill"] for v in items), key=str.lower)
    for lab in labels:
        assert lab.lower() not in seen, f"duplicate skill: {lab}"
        seen[lab.lower()] = cat
    counts[cat] = len(labels)
    with open(os.path.join(outdir, fn), "w", encoding="utf-8") as fh:
        fh.write(f"# {titles[cat]}\n\n")
        fh.write(f"Priority {PRECEDENCE.index(cat) + 1} of {len(PRECEDENCE)} "
                 f"({' > '.join(PRECEDENCE)}). {len(labels)} skills. "
                 f"Generated from data/*/new-skills.md by "
                 f"scripts/categorize_new_skills.py.\n\n")
        for lab in labels:
            fh.write(f"- {lab}\n")

with open(os.path.join(outdir, "README.md"), "w", encoding="utf-8") as fh:
    fh.write("# Categorized new skills\n\n")
    fh.write("Skill names pulled from every `data/*/new-skills.md`, de-duplicated, and "
             "split into three lists. A skill appears in exactly one list, assigned to "
             "the first bucket that claims it: " + " > ".join(PRECEDENCE) + ".\n\n")
    for cat, fn in files.items():
        fh.write(f"- [{titles[cat]}]({fn}) - {counts[cat]} skills\n")
    fh.write(f"\nTotal unique skills: {len(groups)}. "
             f"Regenerate with `python scripts/categorize_new_skills.py`.\n")

print(counts, "| source phrases:", len(groups), "| listed skills:", len(seen))
if unmapped:
    print("unmapped phrases (passed through, add to scripts/skill_atoms.py):")
    for u in sorted(set(unmapped)):
        print("   ", u)
