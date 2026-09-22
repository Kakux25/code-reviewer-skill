import copy
import importlib.util
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('validator', ROOT/'scripts/validate_assurance.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class Contracts(unittest.TestCase):
    def setUp(self):
        self.case = json.loads((ROOT/'examples/assurance/insufficient-evidence.json').read_text())

    def test_schema_and_abstention(self):
        Draft202012Validator.check_schema(json.loads(module.SCHEMA.read_text()))
        self.assertTrue(module.validate(self.case))

    def test_reject_unsupported_acceptance(self):
        self.case['decision'] = 'ACCEPT'
        with self.assertRaises(ValueError): module.validate(self.case)

    def test_reject_missing_claim(self):
        self.case['top_claim'] = 'missing'
        with self.assertRaises(ValueError): module.validate(self.case)

    def test_reject_scope_mismatch(self):
        self.case['claims'][0]['scope']['context_id'] = 'different'
        with self.assertRaises(ValueError): module.validate(self.case)

    def test_reject_cycle(self):
        self.case['claims'][0]['dependencies'] = ['TOP-001']
        with self.assertRaises(ValueError): module.validate(self.case)

    def test_reject_duplicate_id(self):
        self.case['claims'].append(copy.deepcopy(self.case['claims'][0]))
        with self.assertRaises(ValueError): module.validate(self.case)

    def test_reject_authorization(self):
        self.case['authorization'] = 'granted'
        with self.assertRaises(Exception): module.validate(self.case)

    def _graph_case(self, n, fanout):
        base = copy.deepcopy(self.case['claims'][0])
        self.case['claims'] = []
        for i in range(n):
            c = copy.deepcopy(base)
            c['id'] = 'C%d' % i
            c['dependencies'] = ['C%d' % j
                                 for j in range(i + 1, min(n, i + fanout + 1))]
            self.case['claims'].append(c)
        self.case['top_claim'] = 'C0'

    def test_accepts_deep_acyclic_chain(self):
        self._graph_case(1100, 1)
        self.assertTrue(module.validate(self.case))

    def test_accepts_shared_dag_without_blowup(self):
        self._graph_case(64, 2)
        self.assertTrue(module.validate(self.case))

    def test_reject_cycle_in_large_graph(self):
        self._graph_case(64, 2)
        self.case['claims'][63]['dependencies'] = ['C0']
        with self.assertRaises(ValueError): module.validate(self.case)
