# Case L review

Decision: No actionable findings

## Findings

None

## Architecture verdict

Architecture verdict: High

## Soul verdict

Soul verdict: Preserved

## Checks and limits

- Read `request.md`, then `base/ARCHITECTURE.md`, `base/dedup.py`, `candidate/dedup.py`, and `tests/test_dedup.py` under `blind/case-l/` only.
- Base (`base/dedup.py:1-6`) is an O(n^2) first-seen-order dedup via `x not in out`; candidate (`candidate/dedup.py:1-2`) is `list(dict.fromkeys(xs))`, O(n) for hashable inputs and order-preserving on first-seen order in Python 3.7+.
- Contract check: request states inputs are hashable and unhashable behavior is not contracted; `base/ARCHITECTURE.md:3-4` explicitly says the quadratic scan is an implementation detail, not a guaranteed property. The candidate therefore stays within the stated architecture and contract.
- Ran: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="evals/runs/2026-09-20-battery-noskill/blind/case-l/candidate" python3 -m unittest discover -s "evals/runs/2026-09-20-battery-noskill/blind/case-l/tests" -v` — result: 2 tests ran, OK (`test_order_kept`, `test_empty_and_single`).
- Ran: `diff -u base/dedup.py candidate/dedup.py` — result: confirmed the only change is the loop-to-`dict.fromkeys` replacement shown above.
- Limits: did not test unhashable inputs because explicitly out of contract (candidate would raise `TypeError` where base would dedup by equality); did not run performance benchmarks, only reasoned O(n^2) -> O(n); did not read any files outside `blind/case-l/`.
