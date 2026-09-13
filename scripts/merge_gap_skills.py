"""Merge the gap skills in data/skills-categorized/other-skills.md into
input/skill-map.json as real values, under the nine closed labels.

These skills came from job descriptions, not from input/projects.md, so they are
NOT evidenced by a `Skills used` line. They were added on explicit instruction.
`evidence_still_applies` still governs bullets: a value here may be listed in a
Technical Skills row, but no bullet may claim it without project evidence.

Category rulings for the ambiguous groups (user decisions):
  domain knowledge          -> Architecture & Design
  compliance frameworks     -> Methodologies; technical controls -> Architecture & Design
  marketing / growth tools  -> Tools & Platforms
  BI and analytics products -> Data & AI

Run: python scripts/merge_gap_skills.py [--dry-run]
"""

import json
import os
import re
import sys
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_MAP = os.path.join(ROOT, "input", "skill-map.json")
GAPS = os.path.join(ROOT, "data", "skills-categorized", "other-skills.md")

# Gap skills already covered by an existing value under a different wording.
SKIP = {
    "angular", "docker", "next.js", "code review", "structured logging",
    "technical documentation", "json web tokens (jwt)", "data masking", "wcag",
    "accessibility standards", "linux", "monitoring", "rest api development",
    "mentoring engineers", "incident response",
}

# Explicit placements: the four rulings, plus anything the patterns get wrong.
OVERRIDES = {
    # --- domain knowledge -> Architecture & Design
    "Architecture & Design": [
        "healthcare domain", "healthcare APIs", "FHIR", "telehealth domain",
        "digital health domain", "behavioral health domain", "ABA therapy domain",
        "CMS data systems", "claims data", "ICD-10", "CPT", "HCPCS",
        "insurance domain", "EdTech domain", "higher education domain",
        "student success domain", "defense domain", "aerospace domain",
        "robotics domain", "safety-critical systems", "treasury domain",
        "clearing and settlements domain", "satellite subsystems",
        "spacecraft operations", "ground station operations", "orbital maneuvers",
        "station-keeping", "ITU satellite regulations", "FCC satellite regulations",
        "DHS Public Trust clearance", "TSA clearance",
        "electronic court filing standards (ECF/EFM)",
        "data structures and algorithms",
        # technical security controls
        "single sign-on (SSO)", "SAML", "token management", "encryption", "SSL/TLS",
        "network security", "firewall configuration",
    ],
    # --- compliance frameworks and security practice -> Methodologies
    "Methodologies": [
        "SOC 2 compliance", "GDPR compliance", "HIPAA", "patient data privacy",
        "cybersecurity practices", "secure coding", "DevSecOps",
    ],
    # --- marketing, growth and commerce platforms -> Tools & Platforms
    "Tools & Platforms": [
        "Google Ads", "Meta Ads", "HubSpot CRM", "Google Tag Manager", "tracking pixels",
        "conversion tracking", "event tagging", "marketing automation", "RevOps tooling",
        "growth engineering", "client intake funnels", "digital acquisition", "Stripe",
        "usage-based billing", "subscription billing", "invoicing", "CRM integration",
        "field mapping", "form building", "iOS development", "Android development",
        "Tyler Technologies",
        # Oracle application products are platforms, not the database engine
        "Oracle BI Publisher", "Oracle Forms", "Oracle Reports", "Oracle E-Business Suite",
        "Oracle ASCP", "Oracle Workflow", "Oracle public APIs",
    ],
    "Frameworks & Libraries": ["front-end build tooling"],
    # --- BI and analytics products -> Data & AI
    "Data & AI": [
        "Tableau", "Looker", "Sigma", "Hex", "AWS QuickSight", "Google Analytics (GA4)",
        "BI tooling", "reporting dashboards", "data visualization",
        "automated visualization", "data catalog management", "data retention policy",
        "data transformation tooling", "analytic development life cycle", "conversion rate optimization",
    ],
    "Cloud & DevOps": ["Amazon S3", "Microsoft Azure"],
}

# Pattern fallback, first match wins. Order matters.
RULES = [
    ("Databases", r"postgre|mysql|mariadb|sybase|db2|^oracle|cassandra|redis|snowflake|"
                  r"redshift|teradata|bigquery|nosql|graph databases|elasticsearch|"
                  r"data warehous|data lake|delta lake|sql server|pl/sql|indexing|"
                  r"schema governance|data vault|dimensional modeling|medallion|"
                  r"semantic layer|large-scale databases|change data capture"),
    ("Data & AI", r"airflow|dbt|spark|hadoop|hbase|druid|kafka|parquet|iceberg|databricks|"
                  r"informatica|etl|pipeline orchestration|distributed data processing|"
                  r"data quality|anomaly detection|record linkage|reference-data|"
                  r"analytics|attribution|segmentation|experimental design|a/b testing|"
                  r"statsig|experimentation|unity catalog|spreadsheet modeling|excel|"
                  r"google sheets|kpi development|okr development|metric definition|"
                  r"measurement frameworks|user behavior|campaign performance|"
                  r"marketing spend|channel |customer acquisition|\bSAS\b"),
    ("Cloud & DevOps", r"^aws |^azure|google cloud|openshift|kubernetes|terraform|terragrunt|"
                       r"bicep|cloudformation|argocd|gitops|spinnaker|circleci|gitlab ci|"
                       r"github actions|jenkins|vagrant|vercel|nginx|haproxy|load balancing|"
                       r"unix|server provisioning|container|infrastructure as code|"
                       r"platform engineering|observability|alerting|prometheus|grafana|"
                       r"datadog|kibana|distributed tracing|on-call|site reliability|"
                       r"sla definition|slo definition|post-incident|log analysis|telemetry|"
                       r"oci image|service discovery|artifactory|nexus|bazel|build tooling|"
                       r"gitflow|version control policy|disaster recovery|high-availability|"
                       r"pipeline observability|health monitoring"),
    ("Testing", r"selenium|playwright|cucumber|gherkin|behavior-driven|test plan|test case|"
                r"test automation|defect tracking|system testing|software testing|"
                r"test progress|coverage"),
    ("Frameworks & Libraries", r"node\.js|webpack|vite|front-end build|graphql|grpc|"
                               r"soap web services|angular|next\.js"),
    ("Tools & Platforms", r"jira|confluence|salesforce|slack|supabase|webflow|"
                          r"google workspace|apollo\.io|lusha|data enrichment|dbt cloud|"
                          r"oracle bi publisher|oracle forms|oracle reports|"
                          r"oracle e-business|oracle ascp|oracle workflow|oracle public"),
    ("Architecture & Design", r"microservice|event-driven|distributed systems|"
                              r"service-oriented|cloud-native|multi-tenant|middleware|"
                              r"message queue|rabbitmq|zeromq|api rate limiting|"
                              r"retry and backoff|fault-tolerant|concurrency|parallel|"
                              r"cpu and memory|performance profiling|high-load|"
                              r"service orchestration|software architecture|"
                              r"technical design|architecture|responsive|wireframe|"
                              r"conversational interfaces|slack bot|embedded systems|"
                              r"real-time control|autonomous systems|sensor fusion|"
                              r"command and control|software networking|json|xml|xslt|"
                              r"third-party|ARIA"),
    ("Methodologies", r"agile|scrum|sprint|standup|retrospective|hiring|leadership|"
                      r"stakeholder|roadmap|coding best practices|risk mitigation|"
                      r"client services|consulting|training|report automation"),
]


def classify(skill):
    for label, items in OVERRIDES.items():
        if skill in items:
            return label
    for label, pattern in RULES:
        if re.search(pattern, skill, re.I):
            return label
    return None


def main():
    dry = "--dry-run" in sys.argv
    gaps = [l[2:].strip() for l in open(GAPS, encoding="utf-8") if l.startswith("- ")]

    with open(SKILL_MAP, encoding="utf-8") as fh:
        doc = json.load(fh, object_pairs_hook=OrderedDict)
    by_label = {c["label"]: c for c in doc["categories"]}
    taken = {v.lower() for c in doc["categories"] for v in c["values"]}

    added, skipped, unplaced = OrderedDict(), [], []
    for skill in gaps:
        if skill.lower() in SKIP or skill.lower() in taken:
            skipped.append(skill)
            continue
        label = classify(skill)
        if label is None:
            unplaced.append(skill)
            continue
        added.setdefault(label, []).append(skill)
        taken.add(skill.lower())

    if unplaced:
        print(f"UNPLACED ({len(unplaced)}):")
        for s in unplaced:
            print("   ", s)

    print(f"\nskipped as already covered: {len(skipped)}")
    print(f"to add: {sum(len(v) for v in added.values())}\n")
    for label in [c["label"] for c in doc["categories"]]:
        new = added.get(label, [])
        print(f"  {len(by_label[label]['values']):3d} + {len(new):3d}  {label}")

    if dry or unplaced:
        print("\n(dry run - nothing written)" if dry else "\n(unplaced values - nothing written)")
        return

    for label, new in added.items():
        by_label[label]["values"].extend(sorted(new, key=str.lower))

    doc["rules"]["no_invention"] = (
        "Values fall in two groups. Those from input/projects.md and the track files are "
        "evidenced. Those added from job-description gap analysis "
        "(data/skills-categorized/other-skills.md) are NOT: they may be listed in a "
        "Technical Skills row, but never claimed in a bullet. Never add a value here to "
        "match a single posting."
    )
    doc["version"] = doc.get("version", 1) + 1
    doc["updated"] = "2026-09-12"

    with open(SKILL_MAP, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    total = sum(len(c["values"]) for c in doc["categories"])
    print(f"\nwritten. total values: {total}")


if __name__ == "__main__":
    main()
