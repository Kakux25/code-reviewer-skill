# Case I — Review (brief)

## Decision

`Changes requested` — candidate breaks the stable public `greet(name, punct)` signature; every documented call shape fails.

## Findings

- P1, candidate/greeter.py:1 (breaks candidate/app.py:5, tests/test_greeter.py:7,10): `greet(first, last, punct="!")` adds a required positional and shifts `punct` to third place, so `greet("Ada")` raises `TypeError` and `greet("Ada", "?")` silently reinterprets `"?"` as `last`. Proof: execution — suite 0/2 pass (`TypeError: missing 'last'`; `'Hello, Ada ?!' != 'Hello, Ada?'`). Smallest fix: restore `greet(name, punct="!")` and add any name extension as an optional parameter. Confidence: high. (Single root cause; the `welcome(user)` caller at app.py:5 fails via the same break, not a separate defect.)

## Verdicts

- Architecture: `Low` — primary axis (stable public signature `greet(name, punct="!")` per base ARCHITECTURE.md + base greeter.py:1) violated by a required-parameter/boundary break affecting all consumers; change type: feature addition; rubric v1 frozen from base before candidate inspection.
- Soul: `Unverifiable` — no essence/manifesto/canon documented in the provided base; nothing to assess against.

## Checks and limits

- Ran: `trace_callers.py greet` on candidate and base (candidate def at greeter.py:1, single-arg caller at app.py:5) — static leads only.
- Ran: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=<candidate> python3 -m unittest discover -s blind/case-i/tests -v` — FAILED (1 error + 1 failure, quoted above).
- Static: `diff base/greeter.py candidate/greeter.py` confirms only the signature/format-string change; app.py unchanged and therefore broken.
- Limits: reviewed only base/candidate/tests + ARCHITECTURE.md as scoped; no other callers, docs, or history available; no fix applied.
