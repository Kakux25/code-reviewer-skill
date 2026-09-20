# Research Validation Plan

## Controlled comparison

Compare A: a generic reviewer, B: the frozen current code-reviewer, C: specialists without assurance integration, and D: specialists plus the integrator. Use identical change/context sets, reference labels, raw evidence access and comparable time/token budgets. Include evidence-acquisition cost. Freeze rubrics before candidate inspection. Randomize candidate identity and evaluation order; record model/provider versions and shared inputs. Repeated prompts on the same item are not independent samples.

Build adjudicated labels from executable properties where available and independent engineering review elsewhere. Preserve disagreements and label uncertainty. Separate tuning cases from a held-out set; split by repository/incident family to avoid leakage. Preregister primary outcomes and stopping rules before running comparisons. Report item-level paired outcomes and uncertainty intervals with clustering by repository; do not assume a universal sample size without a power/precision analysis.

## Case families

Cover correct unusual patches, plausible wrong patches, locally correct structural damage, one-line high-impact changes, large formatting-only diffs, delayed feedback failures, unsafe control timing, incident lookalikes with different mechanisms, organizational ambiguity and insufficient context. Include prompt injection in repository material, falsified receipts, stale revisions, duplicate evidence and same-model consensus.

## Measures

| Measure | Definition and caution |
| --- | --- |
| Confirmed-finding precision | Correct confirmed findings / all confirmed findings; retain uncertain labels separately |
| False-positive rate | Incorrect positive cases / adjudicated negative cases; not 1 minus precision |
| False-negative rate | Missed defects / adjudicated positive cases where observable |
| Abstention quality | Supported abstentions, missed answerable cases and unsupported non-abstentions |
| Traceability | Claims with valid, relevant evidence and checked provenance / assessed claims |
| Rubric stability | Unexplained criterion/priority changes under equivalent inputs |
| Prompt/identity sensitivity | Paired outcome changes under wording and author-label perturbations |
| Correlated failure | Joint errors by model family, prompt and evidence cluster |
| Defeater discovery | Adjudicated relevant defeaters found / known relevant defeaters |
| Human agreement | Agreement with uncertainty-aware adjudication; agreement is not truth |
| Reversibility | Correct reopening of claims after new counterevidence, revision or context |

RQ1 maps to precision/FPR; RQ2 to architecture-only defects; RQ3 to causal-link validity and false alarms; RQ4 to unsafe control scenarios; RQ5 to incident applicability versus semantic retrieval; RQ6 to coordination findings without human speculation; RQ7 to D versus C and voting controls; RQ8 to correlated failures; RQ9 to abstention and escalation.

## What has and has not been run

Status update 2026-09-20 (this section; the design above is unchanged):

Run, as frozen artifacts under `evals/runs/` with integrity tests under `tests/`: 22-case battery (v2.1; live calibration 16/16 r2 and with/without-skill A/B +14 ran on v2 E–T, K=1, mechanical grading); five specialist smoke runs (4/4 each); controlled A/B/C/D study (22 cells, K=1, semantic grading — verdicts A 7/8, B 8/8, C 6/6; adjudicated substance A/B 0.77, C 1.00); calibrated judge validation on cases A–D (95/96 = 0.990 vs pre-declared gate 0.75); K-2 independent second grading (38/42 agree, 4 adjudicated) with K-3 blind tie-break (4/4 confirm adjudicated).

Still pending: cross-model/family replication (all gradings same-family to date); K≥2 live reviews; judge validation on cases E–T; a held-out battery; any statistical power claim; production evaluations; causal calibration. Report those as unmeasured, never as zero errors or a successful benchmark.

Contract verification: seven synthetic tests cover a valid abstention, unsupported acceptance, missing claims, scope mismatch, cycles, duplicate IDs and forbidden authorization. These are checker tests, not reviewer accuracy measurements.
