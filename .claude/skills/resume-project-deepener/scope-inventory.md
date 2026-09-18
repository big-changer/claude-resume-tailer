# Scope Inventory

What a senior engineer on a project like this one plausibly touched, layer by layer, with
the questions that would turn each item into evidence.

**Read this as a question generator, never as a fact source.** Every line below is a
hypothesis about work that may have happened. `input/projects.md` records only the ones the
candidate confirms. An item nobody was asked about, or answered vaguely, stays out.

**How to use it.** Take one project entry. Read its `Skills used` line. Each recorded
technology implies a set of neighbouring work that nobody wrote down, listed under
**Implied by** below. Ask about the implications with the highest resume value first, per
Step 2 of the skill.

---

## 1. API surface and contract

**Implied by:** FastAPI, Django REST Framework, REST APIs, any service with a client.

- Versioning: was there a `/v1` or any breaking-change path for existing consumers?
- Pagination, filtering and sorting on the list endpoints, and the shape chosen.
- An error taxonomy: consistent codes and messages, or per-endpoint ad hoc?
- Request validation and the schema layer (Pydantic models, DRF serializers).
- OpenAPI or schema docs generated and published to consumers.
- Idempotency on the write endpoints, especially anything a retry could double-apply.
- Rate limiting or throttling, and who asked for it.
- Backwards-compatible deprecation of an endpoint that other teams were using.

## 2. Data model and migrations

**Implied by:** PostgreSQL, SQL, any persisted entity.

- Who designed the schema: the candidate, a DBA, or inherited?
- Migration tooling (Alembic, Django migrations) and who wrote them.
- A migration run against production data, and how downtime or locking was handled.
- Constraints, foreign keys and uniqueness chosen deliberately, and a bug one prevented.
- Soft deletes, history tables, or an audit trail of row changes.
- Normalisation decisions, or a deliberate denormalisation for read performance.
- Table sizes: the largest table's row count, and its growth rate.
- Partitioning, archiving or retention on anything that grew without bound.

## 3. Async work, jobs and queues

**Implied by:** Celery, Redis, background jobs and task queues, scheduled batch imports.

- The broker behind Celery: Redis, RabbitMQ, Amazon SQS, something else.
- The result backend, and whether results were actually read.
- Concurrency model: worker count, prefetch, queues split by priority or by tenant.
- Retry policy: attempt counts, backoff, and what happened on final failure.
- A dead-letter path, a replay tool, or a manual requeue procedure.
- Scheduling: Celery beat, cron, an external scheduler.
- Long-running versus short tasks, and any splitting done to keep a queue moving.
- Throughput: messages or records a day, and the worst backlog ever seen.

## 4. Caching and performance

**Implied by:** Redis, caching, query tuning and indexing, performance profiling.

- What was cached, at what layer, and the invalidation rule.
- TTLs chosen, and a stale-data incident that changed them.
- The profiling tool or method: `EXPLAIN`, a profiler, logs, an APM.
- N+1 queries found and removed.
- Connection pooling, pool sizing, or a pool-exhaustion incident.
- Load or soak testing, the tool, and the load level the system was proven to.
- The slowest endpoint's before and after numbers, beyond the one already recorded.

## 5. Auth, access control and secrets

**Implied by:** role-based access control, audit logging, secrets and configuration
management, PHI handling.

- The authentication mechanism: session, JWT, OAuth 2.0, SSO, an internal provider.
- Where roles and permissions were defined, and how many roles existed.
- Row-level or record-level scoping, not just endpoint-level.
- Where secrets lived: environment, a vault, a cloud secret store, and rotation.
- Token or session expiry and refresh behaviour.
- An access-review or least-privilege exercise the candidate did or was audited on.
- Security review, threat modelling, dependency scanning, or a pen-test finding fixed.

## 6. Reliability and failure handling

**Implied by:** third-party system integration, scheduled data exchange, retries and
idempotency checks, production support.

- Timeouts and retry behaviour against the third party, and what a partner outage did.
- Circuit breaking or a degraded mode when a dependency was down.
- Data reconciliation after a partial failure, and who noticed first.
- A real incident: what broke, what the fix was, what changed afterwards to prevent it.
- Feature flags or a kill switch on a risky path.
- Rollback: a release actually rolled back, and what made it possible.
- Backups and whether a restore was ever tested.

## 7. Observability and production support

**Implied by:** application log analysis, deployment monitoring, background job failure
investigation, API error investigation.

- Where logs went, and whether they were structured.
- Metrics or dashboards, and the tool if there was one.
- Alerting: what paged or emailed anyone, and the threshold.
- Error tracking (Sentry or similar) and the error volume at baseline.
- Tracing or request IDs carried across services.
- Support rotation shape: informal triage, a queue, a rota. Describe it exactly; a formal
  on-call rotation is barred by `input/soft-skills.md` unless it genuinely existed.
- Mean time to diagnose the common failure, if it was ever measured.

## 8. Testing

**Implied by:** pytest, React Testing Library, unit testing, integration testing, branch
coverage figures.

- Coverage numbers beyond the one recorded, per module or overall.
- Integration tests against a real database or a container (Testcontainers or similar).
- Contract tests or mocks against the third-party integrations.
- End-to-end or browser tests, and the tool.
- Fixtures and factories, and test data for PHI-shaped records.
- A test that caught a real production-bound bug.
- Flaky tests dealt with, and how.

## 9. Build, release and environments

**Implied by:** GitHub Actions, CI/CD pipelines, Docker, Docker Compose, AWS (EC2, S3).

- Pipeline stages, and which ones could block a merge or a release.
- Environments: local, dev, staging, production, and who promoted between them.
- Release cadence, and whether the candidate could ship without a gatekeeper.
- Container image build and registry, base image and size work.
- Infrastructure provisioning: console, scripts, or code. Be precise here; the record
  currently states no infrastructure-as-code work exists.
- Database or long-running migrations in the release path.
- Secrets in CI, and artefact or dependency caching.

## 10. Frontend, where the project has one

**Implied by:** React, Next.js, React Hooks, Context API, React Router, accessible forms,
responsive design, reusable component libraries.

- State management approach as the app grew, and what was rejected.
- Data fetching: a client, caching, optimistic updates, loading and error states.
- Form validation shared with the backend rules, or duplicated.
- Accessibility: keyboard paths, screen-reader labels, a WCAG level anyone checked.
- Bundle size, code splitting, or a measured load-time improvement.
- Component documentation or a storybook, and who else consumed the library.
- Browser support constraints imposed by the client's users.

## 11. Integration boundaries

**Implied by:** ERP and accounting system integration, scheduled data exchange, order entry,
inventory records, claims and provider data.

- The transport: REST, SFTP, flat files, a message queue, a vendor SDK.
- The formats: JSON, XML, CSV, EDI, a fixed-width file, HL7.
- Volumes per exchange and the schedule.
- Mapping and transformation: where field mapping lived and who maintained it.
- Partner error handling: rejected records, a reconciliation report, a manual fix queue.
- Onboarding a new partner or client, and how long it took.
- The named vendor platforms, if the candidate can name them. The record currently says
  none are recorded, and naming one honestly is high value.

## 12. Compliance and sensitive data

**Implied by:** protected health information (PHI) handling, audit logging, healthcare plan
operations, role-based access control.

- The regime named by the people who set the requirements: HIPAA, SOC 2, an internal policy.
- What the audit log captured, how long it was retained, and who read it.
- De-identification, masking or minimisation in logs, tests or lower environments.
- Access reviews, training, or a control the candidate implemented to satisfy an auditor.
- An audit or assessment the system passed while the candidate owned it.

## 13. AI work, where the project has it

**Implied by:** LLM APIs, retrieval-augmented generation (RAG), embeddings, semantic search,
structured outputs, prompt evaluation.

The single most expensive gap in the current record. Every item here is currently listed
with nothing behind it:

- The model provider and model, and whether it changed over the project.
- The embedding model and the vector store, or whether retrieval ran in PostgreSQL.
- Chunking strategy, chunk size, and retrieval depth (top-k).
- Reranking, hybrid search, or metadata filtering.
- Evaluation: a golden set, human review, an accuracy or helpfulness figure.
- Guardrails: refusal behaviour, citation enforcement, PHI redaction before the call.
- Cost and latency per query, and any token or cost control.
- Adoption: users, queries a week, or time saved as measured by anyone.

## 14. Metrics to hunt

Ask for these shapes, in this order. The record is strong on before-and-after and weak on
volume, which is what a scale-oriented posting reads for. Only a figure the candidate states
may be written.

| Shape | Question form |
|---|---|
| Volume | How many records, rows, files or documents, and over what period? |
| Throughput | Requests or jobs a second, a minute, a day, at peak? |
| Latency | p50 and p95 before and after, under what load? |
| Footprint | Users, tenants, clients or internal teams served? |
| Error rate | Failures per thousand, before and after? |
| Time | Hours of manual work removed, cycle time, time to onboard a client? |
| Money | Cost saved or avoided, if anyone put a figure on it? |
| Adoption | Teams or people who took up the thing that was built? |
| Quality | Coverage, defect counts, escaped-bug counts? |
| Scale of team | People on the project, and what the candidate owned inside it |

## 15. Unrecorded projects

Seven entries across seven years understates the work. Per employer, ask:

- What else shipped in that role that is not in this file at all?
- The thing the candidate is proudest of, and the thing that was hardest.
- Anything internal: a tool, a script, a library, a migration, a decommissioning.
- A project that failed or was cancelled, and what came out of it anyway.
- Work inherited from someone leaving, and what state it was in.
- The oldest system touched, and what modernising it involved.

Each one that survives becomes a full entry per Step 5, inheriting `Company` and `Period`
from `input/profile.md`.

---

## What not to propose

- **Leadership, mentoring, line management, hiring.** `input/soft-skills.md` lists these as
  not claimable. If the candidate volunteers real leadership, it belongs in Section 4 of the
  track files, not in a project's `Skills used`.
- **Certifications, degrees, clearances.** Credentials are `input/profile.md` and Section 2
  of the track files, and the missing-certification rule stands.
- **Anything the candidate has already declined once.** Asked and skipped means staged and
  dropped, not asked again next session.
- **A technology because a posting wants it.** The gaps logs decide what to ask about; they
  never decide the answer. A question phrased to invite a yes ("you must have used Kafka for
  that, right?") is the failure mode this whole skill exists to avoid.
