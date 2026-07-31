# Business And Product Analysis

Use this reference for keyword-driven business questions and product requirement reviews.

## Keyword-to-business workflow

### 1. Normalize the question

Extract the user's exact phrase, intended actor, desired outcome, and context. Preserve the original wording so later expansion remains auditable.

### 2. Build a keyword constellation

Expand only with repository-supported language:

- actor and role names;
- business entities and identifiers;
- actions and commands;
- lifecycle states, status codes, errors, and fallbacks;
- UI labels and localization keys;
- API routes, request/response fields, events, topics, and IPC messages;
- feature flags, environment variables, configuration keys, and persisted fields;
- historical names, renamed symbols, issue references, and commit terminology.

Search exact phrases first, then stems/synonyms. Search localization resources to bridge product language to code identifiers. Search Git history when current code no longer contains the term.

### 3. Rank evidence

Prefer converging evidence in this order:

1. current runtime code and state transitions;
2. tests and executable examples;
3. API/schema/configuration contracts;
4. current product documentation and UI copy;
5. representative Git commits and blame;
6. names and directory placement alone.

Increase confidence when independent layers agree. Lower confidence for generated files, copied constants, stale docs, dead code, broad localization churn, or branch-only history.

### 4. Find the business entry point

Identify the smallest set of files/symbols that explains the workflow:

- trigger: route, button, scheduled job, event, API, or command;
- policy: validation, permission, feature flag, pricing, or eligibility;
- orchestration: service, store, controller, hook, or use case;
- state/data: model, persistence, cache, status, or protocol;
- side effect: external API, message, file, notification, billing, or device action;
- result: visible outcome, failure, retry, cancellation, and cleanup;
- verification: tests, logs, metrics, or reproducible manual path.

Return 3-7 ranked entry points with why each matters and what to inspect next. Do not return a flat list of keyword matches.

## Product fit review

### 1. Normalize the proposal

Rewrite the request without solution bias:

- actor and segment;
- problem or unmet job;
- current trigger and pain;
- proposed behavior;
- desired outcome;
- constraints and non-goals;
- measurable success and guardrails.

Mark missing items as assumptions rather than silently filling them in.

### 2. Establish the current baseline

Trace the existing user and system workflow. Identify current invariants, extension points, known alternatives, platform differences, ownership, and why the current behavior exists when history provides evidence.

### 3. Evaluate fit dimensions

Use qualitative evidence for each dimension:

- problem overlap: does the project already serve this actor and job?
- capability reuse: can existing workflows, components, services, and contracts support it?
- architecture/data fit: are states, identity, persistence, events, and APIs compatible?
- interaction fit: does it follow current terminology, navigation, permissions, and failure behavior?
- platform/operations fit: build, deployment, offline behavior, observability, support, and rollback;
- trust fit: privacy, security, abuse, accessibility, localization, and compliance;
- delivery fit: test surface, migration, backward compatibility, maintainers, and knowledge concentration.

Use `strong`, `partial`, `weak`, or `unknown` per dimension. Never average these into a score unless the user supplies explicit weights and thresholds.

### 4. Challenge the idea

Actively look for counterevidence:

- an existing feature already solves the job;
- the proposal treats a symptom rather than the root workflow;
- it creates a second source of truth or conflicting state;
- it bypasses permissions, billing, lifecycle, or platform boundaries;
- success cannot be observed;
- adoption cost exceeds the user benefit;
- a smaller interaction or policy change achieves the same outcome.

State what evidence would falsify the current verdict.

### 5. Correct and validate

Recommend `keep`, `change`, `split`, `defer`, or `drop` for each important part. Define the smallest reversible slice that tests the riskiest assumption, not merely the easiest code to build.

Specify:

- target users and scenario;
- exact behavior and non-goals;
- acceptance criteria, including errors and recovery;
- telemetry or manual observations;
- technical spike or prototype boundary;
- regression checks and platform matrix;
- rollout, rollback, and decision threshold.

## Response contracts

### Keyword brief

Return: repository meaning, keyword constellation, current workflow, ranked entry points, related commits/owners, adjacent concepts, unknowns, and next investigation steps.

### Product fit review

Return: normalized idea, current baseline, fit matrix, verdict and confidence, supporting/counter evidence, corrected proposal, minimal experiment, acceptance criteria, risks, implementation entry points, and conditions that change the verdict.

Always distinguish product desirability, technical feasibility, and repository evidence. Code can establish behavior and constraints; it cannot by itself prove user demand or business value.
