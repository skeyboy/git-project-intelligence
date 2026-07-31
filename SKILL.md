---
name: git-project-intelligence
description: Analyze a Git repository to reconstruct project evolution, architecture, business workflows, contributor knowledge, technical decision-making, module change strategies, and engineering approaches; assess the feasibility and tradeoffs of observed or proposed solutions; discover business entry points from product keywords; and turn findings into validated development guidance. Use when asked to analyze Git history, explain business behavior, locate code or owners, profile contributor skills or engineering style, infer evidence-backed technical thinking, compare how people modify modules, build an engineering persona, evaluate solution or product feasibility, draw execution flows, identify validation gaps, or help developers implement changes in an unfamiliar repository.
---

# Git Project Intelligence

Build an evidence-backed map from repository history to current code and developer action. Treat Git as historical evidence, not complete truth.

## Operating rules

- Run read-only commands unless the user separately asks for implementation.
- Inspect repository instructions and current worktree status first. Preserve uncommitted changes.
- Separate facts, inferences, and unknowns. Attach commit hashes, paths, symbols, or commands to material claims.
- Never equate commit count with value, productivity, seniority, or actual comprehension.
- Describe observable engineering tendencies, not personality or psychological traits.
- Treat a contributor "persona" as an evidence-bounded engineering profile: demonstrated domains, recurring decision patterns, tradeoffs, validation habits, and collaboration implications. Never infer identity, character, intelligence, intent, or private traits.
- Account for bots, merges, rebases, squashes, renamed authors, generated files, vendored code, bulk formatting, and incomplete history.
- Prefer current code for present behavior and Git history for intent/evolution. Resolve disagreement explicitly.
- Treat keywords as discovery seeds, not proof of business meaning. Confirm matches through runtime flow and state changes.
- Evaluate product ideas against repository evidence and explicit assumptions; do not manufacture product strategy from code alone.
- Use Mermaid for requested sequence and flow diagrams. Keep node labels short and quote punctuation-heavy labels.

## Workflow

### 1. Establish scope

Determine the repository root, requested revision/range, time window, paths, contributors, output language, and whether the goal is audit, onboarding, planning, or implementation. If unspecified, analyze the current branch across all available history, but start with summaries before expanding expensive queries.

Read repository-level instructions and identify shallow or partial clones:

```bash
git rev-parse --show-toplevel
git status --short
git rev-parse --is-shallow-repository
git log -1 --format='%H %cI %s'
```

### 2. Collect reproducible evidence

Run `scripts/collect_git_evidence.py` for a bounded, machine-readable baseline:

```bash
python3 <skill-dir>/scripts/collect_git_evidence.py --repo . --max-commits 2000 --output /tmp/git-evidence.json
```

Use `--since`, `--until`, `--revision`, and `--path` to match scope. Supplement with targeted commands such as `git show`, `git log --follow`, `git blame -w`, `git shortlog`, and `git log -S/-G`. Do not dump thousands of commits into context; query summaries first, then inspect representative and boundary-changing commits.

### 3. Reconstruct project evolution

Cluster commits into coherent change episodes using time proximity, shared paths/symbols, issue references, and dependency order. For each episode identify trigger, enabling/refactor work, implementation, integration, tests, fixes, and current outcome. Do not assume commit order equals runtime order.

For a commit execution analysis, derive runtime behavior from the changed code and its callers/callees. Produce:

- a commit/change timeline;
- a Mermaid `sequenceDiagram` for runtime participants;
- a Mermaid `flowchart` for decisions, state transitions, errors, and fallback paths.

### 4. Map structure to business behavior

Inventory top-level modules, build manifests, entry points, dependency wiring, domain models, persistence, external adapters, background jobs, UI/API boundaries, tests, and operational configuration. Trace user-visible workflows end to end from trigger to side effect. Use symbol-aware tools when available; otherwise combine `rg`, manifests, tests, and targeted history.

Read [report-contract.md](references/report-contract.md) before producing a full repository or team report.

### 5. Discover business context from keywords

Translate the user's wording into a keyword constellation: actors, business entities, actions, states, outcomes, errors, UI labels, API fields, events, configuration flags, and historical synonyms. Include localized labels and technical aliases when the repository suggests them.

Run the keyword discovery helper for a reproducible first pass:

```bash
python3 <skill-dir>/scripts/find_business_context.py --repo . \
  --keyword "user phrase" --keyword "domain synonym" --output /tmp/business-context.json
```

Rank candidate entry points by evidence convergence, not raw match count. A strong entry point connects several of: user-facing copy, route/UI trigger, domain state, API/event, persistence or side effect, tests, representative commits, and an active maintainer. Trace the top candidates end to end and answer with:

- what the term means in this repository;
- where the workflow starts and ends;
- relevant paths, symbols, states, APIs/events, tests, and commits;
- adjacent terms to search next;
- confirmed facts, likely interpretations, and unresolved questions.

Read [business-product-analysis.md](references/business-product-analysis.md) for keyword expansion, evidence ranking, and response contracts.

### 6. Build contributor knowledge maps

Normalize author aliases conservatively. Exclude or label bots and mechanical changes. For each contributor report evidence across:

- breadth: distinct subsystems touched;
- depth: repeated substantive changes in a subsystem;
- lifecycle coverage: design/refactor, feature, test, fix, operations, review proxies when available;
- recency and continuity;
- cross-boundary integration;
- current-code survival: whether authored lines/components still exist;
- concentration and single-owner risk.

Assign qualitative coverage (`deep`, `working`, `adjacent`, `insufficient evidence`) per subsystem with confidence and supporting commits. Call it **observed repository knowledge**, not total project understanding.

### 7. Reconstruct technical reasoning and module change strategies

For contributor-skill, style, thinking, module-ownership, or persona requests, read [contributor-engineering-analysis.md](references/contributor-engineering-analysis.md).

Sample coherent change episodes, not isolated lines or raw totals. Reconstruct the visible problem, constraints, chosen module boundary, dependency order, state or contract changes, failure handling, validation, follow-up fixes, and present outcome. Distinguish explicit rationale from inferred rationale and plausible alternatives. Do not claim access to a contributor's private thought process.

Describe the recurring module modification playbook: how the contributor finds entry points, scopes changes, sequences cross-module work, chooses local edits versus abstractions, preserves compatibility, handles generated code and external systems, validates behavior, and contains rollout risk. Include counterexamples, sample size, time range, and confidence.

### 8. Assess solution feasibility and build engineering profiles

Evaluate representative solutions both in their historical context and against the current code. Check architecture fit, correctness and invariants, compatibility, reliability, security/privacy where relevant, operability, testability, maintainability, performance, delivery cost, and reversibility. Use qualitative verdicts from the contributor analysis reference; do not collapse tradeoffs into an unexplained numeric score.

For each contributor, synthesize demonstrated skills, observed technical reasoning, module modification strategy, solution strengths and limitations, recurring risks, current-code survival, and practical collaboration implications. State every pattern as a hypothesis with evidence, counterevidence or alternative explanations, sample size, and confidence. Never infer intelligence, motives, temperament, health, protected traits, or performance ratings.

### 9. Evaluate product requirements against the project

Normalize the idea into actor, problem, trigger, proposed behavior, expected outcome, constraints, and measurable success. Reconstruct the current workflow before judging the proposal. Compare the requirement with existing capabilities, architecture, data/state contracts, UX conventions, platform coverage, security/privacy, operations, compatibility, testability, and team ownership.

Return one verdict with confidence:

- `fits`: existing concepts and extension points support it with bounded change;
- `fits with adjustments`: the goal fits but the proposed interaction or implementation should change;
- `validate first`: critical product or technical assumptions lack evidence;
- `conflicts`: it violates a current invariant, product boundary, contract, or operational constraint.

Support the verdict with repository evidence, counterevidence, assumptions, and conditions that would change it. Suggest the smallest reversible experiment, acceptance criteria, telemetry or manual observations, regression surface, rollout/rollback boundary, and the likely code entry points. Do not use an unexplained numeric score.

### 10. Turn findings into development guidance

For a requested feature or bug, provide a development navigation packet:

- likely entry points and owning modules;
- end-to-end call/data flow;
- analogous commits and implementations;
- invariants and compatibility constraints;
- tests to extend and commands to run;
- likely reviewers or subject-matter contacts, framed as evidence-based suggestions;
- a minimal implementation sequence with risk checkpoints.

Only edit code when explicitly asked to implement or when the request clearly includes implementation. Verify changes using repository-native checks.

## Output modes

- **Quick orientation:** architecture map, one core flow, hotspots, first files to read.
- **Commit flow:** selected change episode, timeline, sequence diagram, flowchart, risks.
- **Business map:** domains, capabilities, entry-to-outcome workflows, supporting code.
- **Keyword brief:** business meaning, evidence graph, entry points, related concepts, next searches.
- **Product fit review:** verdict, current/proposed flow delta, constraints, corrections, experiment, acceptance criteria.
- **Team knowledge map:** contributor-by-subsystem matrix, evidence, confidence, bus-factor risks.
- **Contributor engineering profile:** demonstrated skills, technical reasoning patterns, module change playbook, representative-solution feasibility, counterevidence, and collaboration guidance.
- **Developer packet:** concrete file/symbol/test navigation for the next task.
- **Full report:** follow every section in [report-contract.md](references/report-contract.md).

End reports with limitations and reproducibility details: repository revision, range, filters, exclusions, and commands/script arguments used.
