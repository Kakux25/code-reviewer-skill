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
