# Risk and Escalation Policy

Set risk class and required coverage from the change objective, system context and base before detailed candidate assessment. Record who set the scope and why. Do not infer low risk from a small diff or a small repository.

| Trigger | Required response |
| --- | --- |
| Missing base, contract, significant context or failed collector | INSUFFICIENT_EVIDENCE; identify missing artifact and collection owner |
| Contradictory credible evidence or unresolved blocking assumption | ESCALATE; retain both records and assign a discriminating check |
| Confirmed unacceptable behavior or violated binding constraint | REJECT with traceable triggering conditions |
| Destructive/privileged control, critical harm or autonomous actions | Require STPA and responsible human safety/operational review |
| Queues, retries, scaling, rate limits or feedback materially affected | Require dynamics analysis and operating-range evidence |
| New service/team handoff or deployment/on-call changes | Require sociotechnical responsibility and escalation evidence |
| Known relevant incident mechanism | Require applicability/disanalogy assessment; missing corpus is a declared limitation |
| No documented essence or absent optional ADR | Preserve uncertainty; absence alone is not a defect or automatic veto |

For a bounded low-risk integration, behavior and architectural coverage may suffice if exclusions are justified. Moderate and critical scopes require explicit coverage decisions for all six specialists. Critical deployment recommendations always require an independent authorized human decision; no schema output grants authority.

Acceptance is a conjunction of obligations, not votes. Repeated same-model outputs do not add independent support. Expired or context-mismatched evidence reopens the relevant claim. A new candidate or operating context requires reassessment, including previously accepted conditions.

Incident retention, destructive tests, production data access and external publication remain separately authorized actions. Nothing in an assurance case implicitly grants those permissions.
