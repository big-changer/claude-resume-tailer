"""Condense input/skill-map.json: fewer, shorter values per category.

FINAL is the value list each category keeps, in render order. ABSORBED records
which older values each surviving value now stands for, so nothing is dropped
silently - every value currently in the file must appear in one or the other,
and the script refuses to write if any is unaccounted for.

Run: python scripts/condense_skill_map.py
"""

import json
import os
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "input", "skill-map.json")

FINAL = OrderedDict([
    ("Programming Languages", [
        "Java (8, 11, 17)", "TypeScript", "JavaScript", "SQL", "HTML", "CSS", "SCSS", "Bash",
    ]),
    ("Frameworks & Libraries", [
        "Spring Boot", "Spring MVC", "Spring Data JPA", "Spring Batch", "Spring Security",
        "Hibernate", "Resilience4j", "React", "Next.js", "Angular", "RxJS", "Bootstrap",
        "Bean Validation",
    ]),
    ("Databases", [
        "PostgreSQL", "MySQL", "Redis", "Database schema design", "Query optimization",
        "Execution-plan analysis", "Indexing", "Caching", "Hibernate fetch tuning", "JPQL",
        "N+1 query elimination", "Pagination and result streaming", "Transaction management",
        "Staging tables",
    ]),
    ("Cloud & DevOps", [
        "AWS (EC2, S3)", "CI/CD pipelines", "Container build and image packaging",
        "Deployment monitoring and rollbacks", "Release gates and migration checks",
        "Dependency and container scanning", "Structured logging",
        "Metrics, health checks and alerts", "Operational dashboards", "Batch job monitoring",
        "Linux administration", "Nginx configuration",
    ]),
    ("Tools & Platforms", [
        "Git", "Maven", "Docker", "Docker Compose", "GitHub Actions", "Jenkins", "Flyway",
        "OpenAPI/Swagger",
    ]),
    ("Testing", [
        "JUnit", "Mockito", "Spring Boot Test", "Testcontainers", "Jest", "Jasmine/Karma",
        "React Testing Library", "Angular Testing Library", "Unit testing",
        "Integration testing", "End-to-end browser testing", "Regression testing",
        "REST contract testing", "Test pyramid design", "Coverage analysis",
        "Test-data management",
    ]),
    ("Architecture & Design", [
        "REST API design", "Versioned API contracts", "Pagination and filtering",
        "Domain modelling", "Canonical data models", "Third-party system integration",
        "Core banking system integration", "Payments system integration",
        "Retries and idempotency", "Circuit breakers and bulkheads",
        "Dead-letter handling and replay", "Optimistic locking and concurrency control",
        "Transaction boundary design", "Workflow and state-machine design",
        "Notification and reminder workflows", "Time-zone handling",
        "Role-based access control", "OAuth 2.0", "OpenID Connect", "JWT",
        "Backend-enforced authorization", "Least-privilege access", "Audit logging",
        "Sensitive-data masking", "Database migration planning",
        "Expand-and-contract migrations", "Internal business tools",
        "Reusable component libraries", "Responsive design", "WCAG accessibility",
        "Form validation and messaging", "UI state handling", "Server-side rendering",
        "Static site generation",
    ]),
    ("Data & AI", [
        "ETL pipelines", "Batch and scheduled jobs", "Restartable batch processing",
        "CSV and spreadsheet ingestion", "Data validation",
        "Duplicate detection and record deduplication", "Data reconciliation",
        "Data normalization", "Reference-data matching", "Report automation",
        "LLM API integration", "Retrieval-augmented generation (RAG)",
        "Summarization and classification", "Structured extraction",
        "Anomaly scoring and prioritization", "Prompt filtering", "PII masking",
        "Human-in-the-loop review",
    ]),
    ("Methodologies", [
        "Code review", "CI/CD checks", "Design reviews", "Production support",
        "Incident investigation and root-cause analysis", "Troubleshooting runbooks",
        "Release coordination", "End-to-end feature ownership",
        "Collaboration with business and operations teams", "Technical mentoring",
        "Defect triage", "Requirements and acceptance criteria refinement",
        "Technical documentation",
    ]),
])

# Surviving value -> older values it now covers.
ABSORBED = {
    "React": ["React Hooks", "Context API"],
    "Indexing": ["Composite indexing", "Index write-cost tradeoff analysis"],
    "Query optimization": ["Join optimization"],
    "Hibernate fetch tuning": [
        "DTO projections", "Entity graphs", "Batch fetching", "Persistence-context tuning",
    ],
    "Database schema design": ["Normalized schema design"],
    "Staging tables": ["Staging data models"],
    "Container build and image packaging": [
        "Standardized container builds", "Artifact and image packaging",
    ],
    "Release gates and migration checks": [
        "Flyway migration checks and release gates", "Jenkins quality gates",
    ],
    "Structured logging": ["Correlation IDs and structured logging"],
    "Batch job monitoring": [
        "Scheduled job failure investigation", "Spring Batch job monitoring",
    ],
    "CI/CD pipelines": ["Build and release troubleshooting"],
    "Spring Boot Test": ["Spring MVC Test", "Spring Batch Test"],
    "Jasmine/Karma": ["Jasmine", "Karma"],
    "Unit testing": ["Component testing"],
    "Integration testing": [
        "Authorization-boundary testing", "Database migration testing", "Batch restart testing",
    ],
    "End-to-end browser testing": ["Usability testing"],
    "Regression testing": ["Automated test gates in deployment checks", "Flaky test triage"],
    "Coverage analysis": ["Performance baselines"],
    "Third-party system integration": [
        "REST API integration", "Notification system integration",
    ],
    "Retries and idempotency": [
        "Retries and idempotency checks", "Idempotency keys",
        "Idempotent notification processing", "Partial-success handling",
    ],
    "Backend-enforced authorization": [
        "Service-layer authorization", "Separation of access by user type",
    ],
    "Audit logging": [
        "Tamper-resistant audit events", "Audit records for changes to customer information",
        "Support for internal control and compliance reviews",
        "File-level and row-level audit records",
    ],
    "Internal business tools": [
        "Customer profile and account servicing requests", "Internal case handling",
        "Order records and team order administration", "Event registration",
        "Status tracking and deadline reminders", "Approval and reporting periods",
        "Internal business tools for branch and back-office staff",
    ],
    "Workflow and state-machine design": [
        "State transition rules", "Approval rules and escalation",
    ],
    "Notification and reminder workflows": ["Configurable reminder windows"],
    "Reusable component libraries": [
        "Component composition patterns", "Versioned component APIs",
        "Design-system principles",
    ],
    "WCAG accessibility": ["Accessible forms", "Keyboard navigation"],
    "Form validation and messaging": [
        "Inline form validation", "Validation messaging",
        "Configuration-driven form architecture",
    ],
    "UI state handling": [
        "Loading and empty states", "Confirmation flows", "Status tables and report filters",
    ],
    "Pagination and filtering": [],
    "Batch and scheduled jobs": ["Scheduled jobs and scheduled data exchange"],
    "Restartable batch processing": [
        "Restartable batch jobs", "Checkpointing", "Chunk processing",
    ],
    "CSV and spreadsheet ingestion": ["Configurable column mappings", "Data-type conversion"],
    "Data validation": ["Structural and required-field validation", "Missing-field detection"],
    "Duplicate detection and record deduplication": ["Composite duplicate keys"],
    "Report automation": [
        "Reporting queries", "Operational and management reporting",
        "Monthly and quarterly reporting cycles", "Exception reporting",
    ],
    "Retrieval-augmented generation (RAG)": ["Semantic retrieval"],
    "Production support": [
        "Production issue investigation", "Production defect resolution",
    ],
    "Incident investigation and root-cause analysis": ["Failure-mode reviews"],
    "Release coordination": [
        "Release verification with operations staff", "Release sequencing across system owners",
    ],
    "Technical mentoring": ["Developer enablement"],
}


def main():
    with open(PATH, encoding="utf-8") as fh:
        doc = json.load(fh, object_pairs_hook=OrderedDict)

    current = [v for c in doc["categories"] for v in c["values"]]
    kept = {v for vals in FINAL.values() for v in vals}
    absorbed = {old for olds in ABSORBED.values() for old in olds}

    missing = [v for v in current if v not in kept and v not in absorbed]
    if missing:
        raise SystemExit("unaccounted values:\n  " + "\n  ".join(missing))
    for canonical in ABSORBED:
        if canonical not in kept:
            raise SystemExit(f"ABSORBED key not in FINAL: {canonical}")

    labels = [c["label"] for c in doc["categories"]]
    if labels != list(FINAL):
        raise SystemExit("category labels changed; FINAL is out of date")

    for cat in doc["categories"]:
        cat["values"] = FINAL[cat["label"]]

    doc["version"] = doc.get("version", 1) + 1
    doc["updated"] = "2026-09-12"

    with open(PATH, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    new_values = [v for vals in FINAL.values() for v in vals]
    print(f"values: {len(current)} -> {len(new_values)}")
    for label, vals in FINAL.items():
        was = len([v for c in doc["categories"] if c["label"] == label for v in FINAL[label]])
        print(f"  {len(vals):3d}  {label}")
    print(f"\nnew values covering older wording: "
          f"{sum(len(v) for v in ABSORBED.values())} absorbed")


if __name__ == "__main__":
    main()
