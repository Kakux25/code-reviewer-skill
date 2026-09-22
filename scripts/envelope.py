#!/usr/bin/env python3
"""Shared ReviewEnvelope assembly for all reviewer adapters.

Gate 2 built this for code-reviewer; Gate 3 extracts the generic
skeleton so every specialist adapter (arch, STPA, dynamics, ...)
produces structurally identical assurance fragments: one mirrored
claim, caller-asserted provenance that defaults to ignorance, and a
decision that never ACCEPTs from a single reviewer.
"""
import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "evals"))
from validate_assurance import validate

MODULES = ["code-reviewer", "architecture-reviewer",
           "system-dynamics-reviewer", "safety-stpa-reviewer",
           "incident-memory", "sociotechnical-reviewer",
           "final-engineering-judge"]

UNVERIFIED_EXPOSURE = ("caller did not assert review conditions; "
                       "blindness and rubric timing not verified for this input")


def utcnow():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha(data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def dir_hash(path):
    """Deterministic content hash of a directory tree.

    Length-prefixed framing: each record feeds len(name), name,
    len(content), content, so distinct trees cannot serialize to
    the same byte stream. (Plain concatenation lets one file
    holding b"x\\0b\\0y" collide with two files holding b"x", b"y".)
    """
    acc = hashlib.sha256()
    for child in sorted(Path(path).rglob("*")):
        if child.is_file() and "__pycache__" not in child.parts:
            name = str(child.relative_to(path)).encode("utf-8")
            blob = child.read_bytes()
            acc.update(len(name).to_bytes(8, "big"))
            acc.update(name)
            acc.update(len(blob).to_bytes(8, "big"))
            acc.update(blob)
    return acc.hexdigest()[:16]


def ev(id, observation, artifact, method, revision, context_id,
       applicability, limitations, kind, digest):
    return {
        "id": id,
        "observation": observation,
        "artifact": artifact,
        "method": method,
        "collected_at": utcnow(),
        "revision": revision,
        "context_id": context_id,
        "applicability": applicability,
        "limitations": [limitations],
        "kind": kind,
        "integrity": "verified",
        "digest": digest,
    }


def assemble(*, module, short, case_tag, claim, evidence, uncertainties,
             scope, rubric_version, exposure_notes, status_rationale,
             criteria, run_id, producer, prompt_digest,
             criteria_before_candidate=False):
    """Build + validate a single-reviewer assurance fragment.

    claim/evidence/uncertainties are caller-built; this function only
    wraps them in the shared skeleton. producer/exposure/criteria
    timing are caller assertions; defaults plead ignorance.
    """
    claim_id = claim["id"]
    producer = producer or {}
    envelope = {
        "id": "R-%s-%s" % (case_tag, short),
        "rubric_version": rubric_version,
        "exposure_notes": exposure_notes or UNVERIFIED_EXPOSURE,
        "status_rationale": status_rationale,
        "criteria": criteria,
        "shared_context": [scope["context_id"]],
        "evidence": [e["id"] for e in evidence],
        "claims": [claim_id],
        "findings": [],
        "missing_evidence": [],
        "schema_version": "0.1.0",
        "module": module,
        "scope": scope,
        "criteria_before_candidate": bool(criteria_before_candidate),
        "producer": {"model_family": producer.get("model_family", "unknown"),
                     "model_version": producer.get("model_version", "unknown"),
                     "prompt_digest": producer.get("prompt_digest",
                                                   prompt_digest),
                     "session_id": run_id},
        "status": "complete",
    }
    acase = {
        "id": "AC-%s-%s" % (case_tag, run_id),
        "top_claim": claim_id,
        "rationale": "single-reviewer conversion; other specialists missing",
        "required_reviewers": MODULES,
        "conditions": [],
        "evidence": evidence,
        "claims": [claim],
        "findings": [],
        "defeaters": [],
        "uncertainties": uncertainties,
        "causal_links": [],
        "incident_cases": [],
        "safety_constraints": [],
        "reviews": [envelope],
        "schema_version": "0.1.0",
        "scope": scope,
        "decision": "INSUFFICIENT_EVIDENCE",
        "authorization": "not_granted",
    }
    validate(acase)
    return acase
