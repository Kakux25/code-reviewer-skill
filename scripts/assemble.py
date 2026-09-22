#!/usr/bin/env python3
"""Gate 8: assurance integrator (deterministic assembly + defeaters).

Merges single-reviewer assurance fragments into one case. The
integrator judges structure, not substance: ACCEPT requires
coverage (every required reviewer complete), scope agreement, all
claims supported and closed, verified evidence, no blocking doubts,
and no confirmed findings. Anything else yields
INSUFFICIENT_EVIDENCE with one blocking defeater per reason.

Structural merge failures (scope mismatch, identifier collision,
dependency cycle, empty input) yield a refusal case carrying no
fragment items, never a crash. Shared evidence is counted once
(deduped by digest with reference aliasing), so no finding is
double-counted.

Usage:
    python3 scripts/assemble.py --in a.json b.json --out merged.json
        [--required code-reviewer,architecture-reviewer]
"""
import argparse
import copy
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
from envelope import MODULES, sha, utcnow
from validate_assurance import validate

GROUPS = ("evidence", "claims", "findings", "defeaters",
          "uncertainties", "reviews")

REF_EVIDENCE = [("claims", "supporting_evidence"),
                ("claims", "counterevidence"),
                ("reviews", "evidence"),
                ("findings", "evidence"),
                ("defeaters", "evidence"),
                ("causal_links", "evidence"),
                ("incident_cases", "evidence"),
                ("safety_constraints", "evidence")]

RESERVED_IDS = ("CTOP", "E-ASM")
RESERVED_PREFIX = "D-ASM-"


def _reserved(i):
    return i in RESERVED_IDS or i.startswith(RESERVED_PREFIX)

EMPTY_SCOPE = {"base_revision": "none", "candidate_revision": "none",
               "context_id": "no-input", "operation": "integration",
               "risk_class": "low"}


def _canon(obj):
    return json.dumps(obj, sort_keys=True)


def _has_cycle(claims):
    deps = {c["id"]: c.get("dependencies", []) for c in claims}
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {cid: WHITE for cid in deps}
    for root in deps:
        if color[root] != WHITE:
            continue
        color[root] = GRAY
        stack = [(root, iter(deps.get(root, [])))]
        while stack:
            cid, it = stack[-1]
            advanced = False
            for dep in it:
                if color.get(dep, BLACK) == GRAY:
                    return True
                if color.get(dep, BLACK) == WHITE:
                    color[dep] = GRAY
                    stack.append((dep, iter(deps.get(dep, []))))
                    advanced = True
                    break
            if not advanced:
                color[cid] = BLACK
                stack.pop()
    return False


def _integration_evidence(scope, observation):
    return {
        "id": "E-ASM",
        "observation": observation,
        "artifact": "scripts/assemble.py",
        "method": "deterministic structural integration",
        "collected_at": utcnow(),
        "revision": scope["candidate_revision"],
        "context_id": scope["context_id"],
        "applicability": "assembly record for this decision",
        "limitations": ["structure only; substance belongs to reviewers"],
        "kind": "static",
        "integrity": "verified",
        "digest": sha(observation),
    }


def _defeater(n, statement):
    return {
        "id": "D-ASM-%d" % n,
        "claim_id": "CTOP",
        "statement": statement,
        "investigation": "resolve and re-run assemble.py",
        "evidence": ["E-ASM"],
        "blocking": True,
        "status": "unresolved",
    }


def _ctop(scope, status, defeater_ids, hard, subclaims=()):
    return {
        "id": "CTOP",
        "statement": "Required assurance complete for %s" % scope["context_id"],
        "warrant": "mechanical integration (assemble.py): coverage, "
                   "agreement, and closure checks over reviewer fragments",
        "independence_notes": "integrator is deterministic; it judges "
                              "structure, not substance",
        "assumptions": [],
        "supporting_evidence": ["E-ASM"] if status == "supported" else [],
        "counterevidence": ["E-ASM"] if hard else [],
        "defeaters": list(defeater_ids),
        "dependencies": list(subclaims),
        "residual_doubts": [],
        "scope": copy.deepcopy(scope),
        "status": status,
    }


def _case(id, scope, required, claims, evidence, reviews, defeaters,
          uncertainties, findings, causal, incident, safety, rationale,
          decision):
    return {
        "id": id,
        "top_claim": "CTOP",
        "rationale": rationale,
        "required_reviewers": list(required),
        "conditions": [],
        "evidence": evidence,
        "claims": claims,
        "findings": findings,
        "defeaters": defeaters,
        "uncertainties": uncertainties,
        "causal_links": causal,
        "incident_cases": incident,
        "safety_constraints": safety,
        "reviews": reviews,
        "schema_version": "0.1.0",
        "scope": copy.deepcopy(scope),
        "decision": decision,
        # Schema const: authorization is never granted by this
        # machinery. ACCEPT means assurance complete, not authorized.
        "authorization": "not_granted",
    }


def assemble(fragments, required_reviewers=None, run_id="asm"):
    required = list(required_reviewers) if required_reviewers else list(MODULES)
    reasons = []
    hard = False

    def refuse(why):
        scope = copy.deepcopy(fragments[0]["scope"]) if fragments else \
            copy.deepcopy(EMPTY_SCOPE)
        reasons_all = reasons + [why] if why else reasons
        ev = _integration_evidence(
            scope, "refused %d fragment(s): %s" %
            (len(fragments), "; ".join(r[1] for r in reasons_all) or "?"))
        defeaters = [_defeater(n + 1, r[1])
                     for n, r in enumerate(reasons_all)]
        out = _case("AC-ASM-%s" % run_id, scope, required,
                    [_ctop(scope, "defeated" if hard else "unresolved",
                           [d["id"] for d in defeaters], hard)],
                    [ev], [], defeaters, [], [], [], [], [],
                    "refusal: %s" % "; ".join(r[1] for r in reasons_all),
                    "INSUFFICIENT_EVIDENCE")
        validate(out)
        return out

    if not fragments:
        return refuse(("empty", "no fragments supplied"))
    scopes = {_canon(f["scope"]) for f in fragments}
    if len(scopes) > 1:
        revs = sorted({(f["scope"]["base_revision"],
                        f["scope"]["candidate_revision"]) for f in fragments})
        return refuse(("scope",
                       "scope mismatch across fragments (refusing merge): %s"
                       % revs))
    scope = copy.deepcopy(fragments[0]["scope"])
    merged_claims = [c for f in fragments for c in f["claims"]]
    if _has_cycle(merged_claims):
        hard = True
        return refuse(("cycle", "claim dependency cycle across fragments"))
    seen = {}
    for f in fragments:
        for group in GROUPS:
            for item in f[group]:
                if _reserved(item["id"]):
                    hard = True
                    return refuse(("reserved",
                                   "reserved identifier used by fragment: %s"
                                   % item["id"]))
                if item["id"] in seen and seen[item["id"]] != _canon(item):
                    hard = True
                    return refuse(("collision",
                                   "identifier collision: %s" % item["id"]))
                seen[item["id"]] = _canon(item)
    for group in ("causal_links", "incident_cases", "safety_constraints"):
        for f in fragments:
            for item in f[group]:
                if _reserved(item["id"]):
                    hard = True
                    return refuse(("reserved",
                                   "reserved identifier used by fragment: %s"
                                   % item["id"]))
                # Same rule as the main groups: a repeated id with
                # different bytes is a conflict to refuse, never a
                # record to drop silently during the merge.
                if item["id"] in seen and seen[item["id"]] != _canon(item):
                    hard = True
                    return refuse(("collision",
                                   "identifier collision: %s" % item["id"]))
                seen[item["id"]] = _canon(item)

    # Merge with evidence dedupe by digest + reference aliasing.
    # Null digests never dedupe (absence of identity is not identity).
    # A shared digest with conflicting integrity/kind is contradictory
    # provenance: refuse instead of letting fragment order decide
    # which record survives (first-wins would hide unverified
    # evidence behind whichever fragment arrived first).
    kept, kept_ids, alias, by_digest = [], set(), {}, {}
    for f in fragments:
        for e in f["evidence"]:
            if e["id"] in kept_ids:
                # Byte-identical (collisions already refused): skip.
                continue
            if e["digest"] is not None and e["digest"] in by_digest:
                first_id = by_digest[e["digest"]]
                first = next(x for x in kept if x["id"] == first_id)
                if (first["integrity"] != e["integrity"]
                        or first["kind"] != e["kind"]):
                    hard = True
                    return refuse(("collision",
                                   "digest %s shared by %s and %s with "
                                   "conflicting integrity/kind"
                                   % (e["digest"], first_id, e["id"])))
                alias[e["id"]] = first_id
            else:
                if e["digest"] is not None:
                    by_digest[e["digest"]] = e["id"]
                kept_ids.add(e["id"])
                kept.append(copy.deepcopy(e))
    n_ev_in = sum(len(f["evidence"]) for f in fragments)

    def alias_ev(ids):
        return [alias.get(i, i) for i in ids]

    merged = {e["id"] for e in kept}
    buckets = {"claims": [], "reviews": [], "findings": [],
               "defeaters": [], "uncertainties": [],
               "causal_links": [], "incident_cases": [],
               "safety_constraints": []}
    for f in fragments:
        for group, items in buckets.items():
            for item in f[group]:
                # Same id here means byte-identical (real collisions
                # already refused above): skip instead of duplicating.
                if item["id"] in merged:
                    continue
                merged.add(item["id"])
                item = copy.deepcopy(item)
                for gname, key in REF_EVIDENCE:
                    if gname == group:
                        item[key] = alias_ev(item[key])
                if group == "findings":
                    item["refutation"]["evidence"] = alias_ev(
                        item["refutation"]["evidence"])
                items.append(item)
    claims = buckets["claims"]
    reviews = buckets["reviews"]
    findings = buckets["findings"]
    defeaters = buckets["defeaters"]
    uncertainties = buckets["uncertainties"]
    causal = buckets["causal_links"]
    incident = buckets["incident_cases"]
    safety = buckets["safety_constraints"]

    completed = {r["module"] for r in reviews
                 if r["status"] == "complete" and not r["missing_evidence"]}
    for r in reviews:
        if r["status"] != "complete" or r["missing_evidence"]:
            reasons.append(("incomplete", "incomplete review: %s (%s)" %
                            (r["module"], r["id"])))
    for m in required:
        if m not in completed:
            reasons.append(("missing", "missing required reviewer: %s" % m))
    for c in claims:
        if c["status"] == "defeated":
            hard = True
            reasons.append(("defeated", "defeated claim: %s" % c["id"]))
        elif c["status"] != "supported":
            reasons.append(("open", "claim not supported: %s (%s)" %
                            (c["id"], c["status"])))
        if c["assumptions"] or c["residual_doubts"]:
            reasons.append(("unclosed", "unclosed claim %s "
                            "(assumptions/residual doubts)" % c["id"]))
        if c["status"] == "supported" and not c["supporting_evidence"]:
            reasons.append(("unclosed", "supported claim without evidence: %s"
                            % c["id"]))
    for e in kept:
        if e["integrity"] != "verified":
            reasons.append(("evidence", "unverified evidence: %s" % e["id"]))
    for d in defeaters:
        if d["blocking"] and d["status"] != "refuted":
            reasons.append(("doubt", "blocking defeater carried: %s" % d["id"]))
    for u in uncertainties:
        if u["blocking"] and u["status"] != "resolved":
            reasons.append(("doubt", "blocking uncertainty carried: %s"
                            % u["id"]))
    for x in findings:
        if x["status"] == "confirmed":
            reasons.append(("finding", "confirmed finding: %s" % x["id"]))

    decision = "ACCEPT" if not reasons else "INSUFFICIENT_EVIDENCE"
    status = "supported" if not reasons else ("defeated" if hard else
                                              "unresolved")
    ev = _integration_evidence(
        scope, "integrated %d fragment(s) from %s: %d evidence items "
        "deduped to %d unique digests; %d blocking reason(s)" %
        (len(fragments), sorted({r["module"] for r in reviews}), n_ev_in,
         len(kept), len(reasons)))
    new_defeaters = [_defeater(n + 1, r[1]) for n, r in enumerate(reasons)]
    ctop = _ctop(scope, status, [d["id"] for d in new_defeaters],
                 hard and bool(reasons),
                 subclaims=[c["id"] for c in claims])
    out = _case("AC-ASM-%s" % run_id, scope, required,
                claims + [ctop], kept + [ev], reviews,
                defeaters + new_defeaters, uncertainties, findings,
                causal, incident, safety,
                "mechanical integration of %d fragment(s)" % len(fragments),
                decision)
    validate(out)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="integrate assurance fragments")
    ap.add_argument("--in", dest="ins", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--required", default=None,
                    help="comma-separated required reviewers (default: all 7)")
    ap.add_argument("--run-id", default="asm")
    args = ap.parse_args(argv)
    frags = [json.loads(Path(p).read_text(encoding="utf-8")) for p in args.ins]
    required = None
    if args.required:
        required = [m.strip() for m in args.required.split(",") if m.strip()]
        if not required:
            required = None
    out = assemble(frags, required_reviewers=required, run_id=args.run_id)
    Path(args.out).write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print("decision: %s (%d defeaters)" % (out["decision"],
                                           len(out["defeaters"])))


if __name__ == "__main__":
    main()
