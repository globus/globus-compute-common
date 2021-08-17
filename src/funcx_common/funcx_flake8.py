# type: ignore
"""
A Flake8 Plugin for use in FuncX

Catches log calls which do eager string formatting and imports of the `typing`
module which don't match our preferred form.
"""

import ast

CODEMAP = {
    "FX001": "FX001 log call uses string.format() on first arg",
    "FX002": "FX002 log call uses string.join() on first arg",
    "FX003": "FX003 log call uses %-formatting in first arg",
    "FX004": "FX004 log call uses '+' operator in first arg",
    "FX005": "FX005 log call uses f-string in first arg",
    "FX010": "FX010 bare import of typing module",
    "FX011": "FX011 import of typing module with an alias other than 't'",
}
LOG_METHODS = {"debug", "info", "warn", "warning", "error", "critical", "exception"}


class Plugin:
    name = "funcx-flake8"
    version = "0.1.0"

    # args to init determine plugin behavior. see:
    # https://flake8.pycqa.org/en/latest/internal/utils.html#flake8.utils.parameters_for
    def __init__(self, tree):
        self.tree = tree

    # Plugin.run() is how checks will run. For detail, see implementation of:
    # https://flake8.pycqa.org/en/latest/internal/checker.html#flake8.checker.FileChecker.run_ast_checks
    def run(self):
        visitors = (LogMethodVisitor(), ImportVisitor())
        for visitor in visitors:
            visitor.visit(self.tree)
            for lineno, col, code in visitor.collect:
                yield lineno, col, CODEMAP[code], type(self)


class ErrorRecordingVisitor(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.collect = []

    def _record(self, node, code):
        self.collect.append((node.lineno, node.col_offset, code))


class LogMethodVisitor(ErrorRecordingVisitor):
    def __init__(self):
        super().__init__()
        self.in_call = False
        self.in_firstarg = False

    def visit_Call(self, node):
        try:
            current_func = node.func.attr
        except AttributeError:
            self.generic_visit(node)
            return

        # in a log call, in the first arg of the call, in a call to format()
        if self.in_call and self.in_firstarg:
            if current_func == "format":
                self._record(node, "FX001")
                self.generic_visit(node)
                return
            elif current_func == "join":
                self._record(node, "FX002")
                self.generic_visit(node)
                return

        if current_func not in LOG_METHODS:
            self.generic_visit(node)
            return

        self.in_call = True

        for i, child in enumerate(ast.iter_child_nodes(node)):
            if i == 1:
                self.in_firstarg = True
            self.visit(child)
            self.in_firstarg = False

        self.in_call = False

    def visit_BinOp(self, node):
        if self.in_call and self.in_firstarg:
            if isinstance(node.op, ast.Mod):
                self._record(node, "FX003")
                self.generic_visit(node)
            elif isinstance(node.op, ast.Add):
                self._record(node, "FX004")
                self.generic_visit(node)

    def visit_JoinedStr(self, node):
        if self.in_call and self.in_firstarg:
            self._record(node, "FX005")
            self.generic_visit(node)


class ImportVisitor(ErrorRecordingVisitor):
    def visit_Import(self, node):  # an `import foo` clause
        for alias in node.names:
            if alias.name == "typing":
                if alias.asname is None:
                    self._record(node, "FX010")
                elif alias.asname != "t":
                    self._record(node, "FX011")
