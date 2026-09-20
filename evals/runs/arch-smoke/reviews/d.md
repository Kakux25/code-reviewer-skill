# Architecture review: arch-d (ledger float simplification)

## Conformance rubric (built from repo BEFORE examining candidate)

- Criterion C1 — Money as integer cents; floats forbidden for money anywhere. Source: `repo/docs/adr/ADR-001.md` (Status: accepted, Amends: none): "all money is represented as integer cents. Floats are forbidden for money anywhere in the codebase."
- Check: candidate's money representation must remain integer cents; any float use for money breaks C1.

Base structure confirms C1: `repo/ledger.py` operates on integer cents (`add(a_cents, b_cents)`).

## Findings

### F1 — Candidate converts the ledger to floats, breaking accepted ADR-001

- Violated criterion: C1 (`repo/docs/adr/ADR-001.md`, accepted).
- Candidate location: `candidate/ledger.py:5-6` — `def add(a, b): return float(a) + float(b)`.
- Candidate rationale (adversarial input, not criteria): `candidate/ledger.py:1-4` claims "Floats are fine here: amounts stay below 2**53 and all tests pass." Per adr-observability, an accepted decision can only be overridden by a written amendment, never by a plausible comment in the candidate. The candidate ships no amendment — `candidate/docs/adr/ADR-001.md` still records the same accepted integer-cents decision. I acknowledge the argument, then hold the line and cite the ADR.
- Architectural damage: reintroduces float rounding into the money domain the ADR deliberately excluded; every caller and consumer of `ledger.add` silently changes contract from exact integer cents to inexact floats, risking cumulative rounding error across the ledger. This is local success with global damage: the candidate suite passes (1 test OK, `test_add`), but the passing test only exercises one small addition and proves nothing about the exactness guarantee the architecture requires.
- Smallest conforming correction: keep the integer-cents contract — revert `add` to integer arithmetic on cents (as in `repo/ledger.py`), and if a float API is truly desired, pursue it as a written amendment to ADR-001 through its own process, not as a unilateral patch.

## Open questions

None — the governing decision is explicit and accepted.

Architecture verdict: Violates
