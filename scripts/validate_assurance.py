"""Check record structure and consistency; never grant deployment authority."""
import argparse
import json
from pathlib import Path
from jsonschema import Draft202012Validator

SCHEMA = Path(__file__).resolve().parents[1] / 'schemas/v0.1.0/assurance.schema.json'


def validate(case):
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator(schema).validate(case)
    groups = {}
    all_ids = set()
    for group in ('evidence', 'claims', 'findings', 'defeaters', 'uncertainties', 'reviews'):
        groups[group] = {}
        for item in case[group]:
            if item['id'] in all_ids:
                raise ValueError('Duplicate identifier: ' + item['id'])
            all_ids.add(item['id'])
            groups[group][item['id']] = item
    def refs(ids, group):
        if any(i not in groups[group] for i in ids):
            raise ValueError('Dangling reference to ' + group)
    refs([case['top_claim']], 'claims')
    for c in case['claims']:
        if c['scope'] != case['scope']:
            raise ValueError('Claim scope mismatch')
        for key, target in [('supporting_evidence','evidence'),('counterevidence','evidence'),('defeaters','defeaters'),('dependencies','claims'),('residual_doubts','uncertainties')]:
            refs(c[key], target)
    # Iterative DFS with a shared done set: O(V+E), no recursion
    # limit, no exponential re-walks on shared DAGs. Dependencies were
    # resolved to existing claims by the refs() checks above.
    done = set()
    for root in groups['claims']:
        if root in done:
            continue
        visiting = {root}
        stack = [(root, iter(groups['claims'][root]['dependencies']))]
        while stack:
            cid, it = stack[-1]
            advanced = False
            for dep in it:
                if dep in visiting:
                    raise ValueError('Claim dependency cycle')
                if dep not in done:
                    visiting.add(dep)
                    stack.append(
                        (dep, iter(groups['claims'][dep]['dependencies'])))
                    advanced = True
                    break
            if not advanced:
                visiting.discard(cid)
                done.add(cid)
                stack.pop()
    for f in case['findings']:
        refs([f['claim_id']], 'claims')
        refs(f['evidence'] + f['refutation']['evidence'], 'evidence')
        refs(f['uncertainty'], 'uncertainties')
        if f['status'] == 'confirmed' and (not f['refutation']['attempted'] or f['refutation']['result'] != 'survived' or not any(groups['evidence'][e]['kind'] != 'inferential' for e in f['evidence'])):
            raise ValueError('Confirmed finding lacks refutation or observation')
    for d in case['defeaters']:
        refs([d['claim_id']], 'claims'); refs(d['evidence'], 'evidence')
    for r in case['reviews']:
        if r['scope'] != case['scope']:
            raise ValueError('Review scope mismatch')
        for target in ('evidence','claims','findings'):
            refs(r[target], target)
    for group in ('causal_links','incident_cases','safety_constraints'):
        for item in case[group]:
            refs(item['evidence'], 'evidence')
    if case['decision'] in ('ACCEPT','CONDITIONAL_ACCEPT'):
        if not case['required_reviewers'] or not case['evidence']:
            raise ValueError('Acceptance without coverage or evidence')
        completed = {r['module'] for r in case['reviews'] if r['status'] == 'complete' and not r['missing_evidence']}
        if not set(case['required_reviewers']) <= completed:
            raise ValueError('Required reviews incomplete')
        if any(c['status'] != 'supported' or c['assumptions'] or c['residual_doubts'] or not c['supporting_evidence'] for c in case['claims']):
            raise ValueError('Unclosed claims')
        if any(e['integrity'] != 'verified' for e in case['evidence']):
            raise ValueError('Unverified evidence')
        if any(d['blocking'] and d['status'] != 'refuted' for d in case['defeaters']) or any(u['blocking'] and u['status'] != 'resolved' for u in case['uncertainties']):
            raise ValueError('Blocking doubt')
        if any(f['status'] == 'confirmed' for f in case['findings']):
            raise ValueError('Unresolved confirmed finding')
        if case['decision'] == 'CONDITIONAL_ACCEPT' and not case['conditions']:
            raise ValueError('Missing conditions')
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('case', type=Path)
    args = parser.parse_args()
    validate(json.loads(args.case.read_text()))
    print('Contract checks passed; engineering truth and authorization are not established.')
