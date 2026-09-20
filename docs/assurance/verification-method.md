# Verification Method: Double-Hand, Oracle, Trapped Hash

Status: PROPOSED — working definitions inferred from practice; pending
user ratification of the three terms before this becomes normative.
Until ratified, treat this document as a record of what was done, not
as a rulebook.

## 1. Double-Hand (doble mano)

Every deliverable passes through two independent hands: the hand that
builds and the hand that challenges. The challenger works from
independent criteria (never derived from the deliverable under review),
records a verdict (accept / changes requested / incomplete), and no
deliverable is committed while a challenge verdict is open.

Applied in this repo (evidence, not aspiration): gap-analysis,
registry S17–S19, ADR-0002, and the CI job each received an isolated
skill-review agent verdict before commit; the merge was reviewed
post-commit with fixes in a child commit. Four of five reviews
returned Changes requested and were fixed first (`/tmp/*-review.md`
reports, fixes recorded in each commit message).

## 2. Oracle (oráculo)

Verification must come from an instrument independent of the
construction path. Self-checks do not count. Accepted oracles:

- a separate agent re-deriving results (re-fetching URLs, re-running
  suites, reproducing counts) without access to answer keys;
- a separate tool or gate (mechanical grader vs hand scores;
  integrity gate vs contract tests);
- an external record (GitHub API, library catalogs, command exit
  codes).

A check built from the assumption under test proves nothing: the
oracle and the artifact must be able to disagree, and disagreements
are resolved by evidence, never by editing the oracle to fit.

## 3. Trapped Hash (hash atrapado)

Every input and output is pinned immutably so silent drift is
impossible: frozen keys and manifests, blind bundles staged per run,
external revisions pinned by SHA, commits as immutable tree states.
Any change after an observation re-opens validation for everything
downstream of it; nothing is re-interpreted in place.

Consequence: a "passing" result names the exact pinned inputs it
passed on. A result whose inputs moved is not passing — it is stale.

## Non-goals

This method does not establish ground truth (oracles here are
same-model-family unless stated), statistical significance (K=1
throughout unless stated), or cross-environment reproducibility.
It establishes exactly this: no claim entered the record unchallenged,
unchallenged-by-an-independent-instrument, or attached to moving inputs.

## Ratification

To ratify: confirm, correct, or replace each of the three definitions
above; on confirmation this document moves to Status: accepted and
gains a traceability entry. Until then, new work SHOULD follow it but
a deviation needs no waiver — it needs a note saying what was done
instead.
