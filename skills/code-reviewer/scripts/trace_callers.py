#!/usr/bin/env python3
"""List definitions and call sites of a Python symbol (read-only).

Walks a directory tree and reports, per file, where SYMBOL is defined,
imported, referenced, or called. Targets are parsed with the standard
library `ast` module; they are never imported or executed.

Limits: bare-name matching only. No type resolution (a method call on
an instance is reported by method name alone), no dynamic calls
(getattr, eval), no cross-language search, undecodable files and files
with syntax errors are skipped with a warning. Treat output as leads
for review, not proof.

Usage:
    trace_callers.py SYMBOL ROOT [--json]

Exit status: 0 on success (even with zero matches), 2 on usage errors.
"""

import argparse
import ast
import json
import os
import sys

SKIP_DIRS = {
    ".git", ".hg", ".svn", "__pycache__", ".venv", "venv",
    "node_modules", ".tox",
}


def iter_py_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(
            d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")
        )
        for name in sorted(filenames):
            if name.endswith(".py"):
                yield os.path.join(dirpath, name)


class Collector(ast.NodeVisitor):
    def __init__(self, symbol, lines):
        self.symbol = symbol
        self.lines = lines
        self.calls = set()  # ids of Name/Attribute nodes used as call funcs
        self.hits = []

    def visit_Call(self, node):
        # Runs before descending, so func ids are known when reached.
        self.calls.add(id(node.func))
        self.generic_visit(node)

    def _record(self, node, kind):
        lineno = getattr(node, "lineno", 0)
        if 0 < lineno <= len(self.lines):
            context = self.lines[lineno - 1].strip()
        else:
            context = ""
        self.hits.append({
            "line": lineno,
            "col": getattr(node, "col_offset", 0),
            "kind": kind,
            "context": context[:120],
        })

    def visit_FunctionDef(self, node):
        if node.name == self.symbol:
            self._record(node, "def")
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node):
        if node.name == self.symbol:
            self._record(node, "class")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            if (alias.asname or alias.name).split(".")[0] == self.symbol:
                self._record(alias, "import")
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            if (alias.asname or alias.name).split(".")[0] == self.symbol:
                self._record(alias, "import")
        self.generic_visit(node)

    def visit_Name(self, node):
        if node.id == self.symbol and isinstance(node.ctx, ast.Load):
            self._record(node, "call" if id(node) in self.calls else "ref")

    def visit_Attribute(self, node):
        if node.attr == self.symbol and isinstance(node.ctx, ast.Load):
            self._record(node, "call" if id(node) in self.calls else "ref")
        self.generic_visit(node)


def search(root, symbol):
    results = []
    errors = []
    for path in iter_py_files(root):
        try:
            with open(path, "r", encoding="utf-8") as fh:
                source = fh.read()
        except (OSError, UnicodeDecodeError) as exc:
            errors.append("%s: unreadable (%s), skipped" % (path, exc))
            continue
        try:
            tree = ast.parse(source, filename=path)
        except SyntaxError as exc:
            errors.append("%s:%s: syntax error, skipped" % (path, exc.lineno))
            continue
        collector = Collector(symbol, source.splitlines())
        collector.visit(tree)
        for hit in collector.hits:
            results.append({"file": os.path.relpath(path, root), **hit})
    results.sort(key=lambda h: (h["file"], h["line"], h["col"]))
    return results, errors


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("symbol", help="bare symbol name to search for")
    parser.add_argument("root", help="directory tree to search")
    parser.add_argument("--json", action="store_true", help="emit JSON list")
    args = parser.parse_args(argv)
    if not os.path.isdir(args.root):
        parser.error("not a directory: %s" % args.root)
    results, errors = search(args.root, args.symbol)
    for message in errors:
        print("warning: " + message, file=sys.stderr)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for hit in results:
            print("%s:%d:%d %s :: %s" % (
                hit["file"], hit["line"], hit["col"], hit["kind"], hit["context"],
            ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
