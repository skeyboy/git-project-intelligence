# Contributor Engineering Analysis

Use this reference when the request concerns contributor skills, technical thinking, coding or engineering style, module modification approach, solution feasibility, or an engineering persona.

## Evidence standard

Treat Git as a record of observable decisions, not direct access to thought or complete work history.

1. Normalize aliases conservatively and separate humans, bots, AI-assisted identities, merges, generated code, vendor churn, and mechanical edits.
2. Select at least three substantive change episodes per contributor when history allows. Cover more than one change type or lifecycle stage, such as feature, refactor, defect, incident, test, migration, or operations.
3. Inspect the commit, relevant parent state, current code, tests, follow-up fixes, reversions, and adjacent commits. A subject line alone is insufficient evidence.
4. Prefer survived code and repeated decisions across time. Treat a single episode as a case study, not a stable pattern.
5. Record sample size, date range, exclusions, counterexamples, alternative explanations, and confidence.

## Reconstruct one change episode

Capture these fields:

- **Problem:** user-visible failure, requirement, operational need, or technical constraint evidenced in history or code.
- **Known constraints:** contracts, state invariants, compatibility, platforms, dependencies, deadlines only when explicit, and ownership boundaries.
- **Chosen boundary:** entry point and modules changed; note nearby modules intentionally or apparently left unchanged.
- **Change sequence:** preparation, contract/data changes, implementation, integration, tests, deployment or migration, and follow-up fixes.
- **Decision evidence:** explicit rationale from docs or messages; inferred rationale from code shape; unresolved unknowns.
- **Failure strategy:** validation, errors, retries, fallback, rollback, observability, and cleanup.
- **Outcome:** runtime effect, current-code survival, regressions, reversions, or later replacement.
- **Alternatives:** only technically plausible options supported by repository context. Label them as analysis, not rejected ideas unless history says so.

## Infer the module modification playbook

Compare episodes across these dimensions:

| Dimension | Questions |
|---|---|
| Entry-point discovery | Does work begin at UI/API triggers, domain state, failing adapters, tests, logs, or persistence? |
| Scope and boundaries | Are changes localized, vertical across layers, or preceded by boundary extraction? |
| Change sequencing | Does the contributor prepare contracts/refactors first, ship one integrated commit, or converge through follow-up patches? |
| State and contracts | How are schemas, events, APIs, caches, concurrency, and generated artifacts handled? |
| Compatibility | Are old clients, data, platforms, feature flags, fallbacks, and migrations preserved? |
| Failure and operations | Are errors propagated, retried, logged, measured, alerted, cleaned up, or made reversible? |
| Validation | Are tests paired, boundaries mocked, builds run, manual probes documented, or regressions fixed later? |
| Abstraction threshold | When is shared code extracted, and when are explicit local changes preferred? |

Describe repeated behavior as an observable hypothesis: “Across 5 payment episodes, changes usually start at the RPC contract and proceed through service and persistence layers.” Do not write “thinks top-down” unless the evidence and meaning are made explicit.

## Assess feasibility of representative solutions

Evaluate the solution at two points:

- **Then:** Was it reasonable under the architecture, dependencies, requirements, and knowledge visible at the time?
- **Now:** Does it remain suitable in current code, or has scale, platform coverage, ownership, or architecture changed?

Check:

- architecture and module-boundary fit;
- correctness, state invariants, concurrency, and data consistency;
- API, data, client, platform, and operational compatibility;
- reliability, failure containment, observability, and recovery;
- security and privacy where applicable;
- performance and resource behavior where material;
- testability and strength of actual validation evidence;
- maintainability, duplication, coupling, and generated-code impact;
- delivery complexity, migration, rollout, rollback, and reversibility.

Use one verdict per representative solution:

- `sound`: evidence supports the approach and validation for its context;
- `viable with tradeoffs`: workable, with explicit bounded weaknesses;
- `fragile or context-dependent`: success relies on weak validation, hidden coupling, manual sequencing, or narrow assumptions;
- `superseded`: reasonable historically but replaced or no longer aligned with current code;
- `insufficient evidence`: implementation or outcome evidence cannot support a verdict.

State confidence and what evidence would change the verdict. Feasibility is not authorship quality and must not become a contributor ranking.

## Build the engineering profile

For each contributor report:

1. **Demonstrated skills:** technologies, domains, lifecycle stages, and current coverage.
2. **Technical reasoning hypotheses:** problem decomposition, diagnosis, abstraction, compatibility, failure handling, validation, and iteration patterns.
3. **Module modification playbook:** typical entry point, boundary, sequence, dependencies, tests, rollout, and follow-up.
4. **Representative solution feasibility:** 1-3 episodes with verdict, strengths, limitations, and present status.
5. **Observable code and change style:** naming, component/function shape, commit decomposition, documentation, test pairing, and generated-code handling.
6. **Counterevidence and uncertainty:** exceptions, sparse samples, shared authorship, branch duplication, or missing review context.
7. **Collaboration implications:** useful review pairing, areas needing a second owner, evidence to request in design review, and onboarding paths. Always include this field, even when the only defensible result is `insufficient evidence`.

Distinguish historical knowledge, current-code ownership, organizational responsibility, and present availability. Do not recommend someone as a reviewer or owner solely because they authored old code; frame the result as an evidence-based expertise lead unless current responsibility is confirmed.

Never infer personality, intelligence, seniority, motives, emotions, protected traits, health, or off-repository performance. Avoid labels such as “careless,” “brilliant,” “conservative,” or “aggressive.” Replace them with precise observations such as “3 of 4 sampled changes required follow-up fixes for platform-specific behavior.”

## Compact output contract

Lead with a contributor-by-area matrix. Then use one compact block per contributor:

```text
Contributor — observed repository knowledge (confidence)
Skills: ...
Reasoning pattern: hypothesis + episode evidence + counterexample.
Module change playbook: entry -> boundary -> sequence -> validation -> rollout.
Feasibility: commit/episode, verdict then/now, tradeoffs.
Collaboration: expertise lead, reviewer or pairing implication; current ownership/availability status.
```

End with cross-team knowledge concentration, solution risks, unknowns, and reproducibility details.
