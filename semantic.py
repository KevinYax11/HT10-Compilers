from parser import parse
from typing import Dict, List, Set

class SemanticError(Exception):
    pass

class SemanticWarning:
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return f"ADVERTENCIA: {self.msg}"

class SymbolTable:
    def __init__(self):
        self.symbols: Dict[str, dict] = {}

    def declare(self, name: str, scope: str = "global", value=None, conditional: bool = False):
        if name not in self.symbols:
            self.symbols[name] = {
                "type": "entero",
                "scope": scope,
                "value": value,
                "conditional": conditional,
            }
        else:
            if value is not None:
                self.symbols[name]["value"] = value

    def lookup(self, name: str) -> dict:
        return self.symbols.get(name, None)

    def print_table(self):
        print(f"\n{'VARIABLE':<12} {'TIPO':<8} {'ÁMBITO':<20} {'VALOR':<12} {'CONDICIONAL'}")
        print("-" * 65)
        for name, info in self.symbols.items():
            cond = "Sí" if info["conditional"] else "No"
            val  = str(info["value"]) if info["value"] is not None else "desconocido"
            print(f"{name:<12} {info['type']:<8} {info['scope']:<20} {val:<12} {cond}")

class SemanticAnalyzer:
    def __init__(self):
        self.table = SymbolTable()
        self.warnings: List[SemanticWarning] = []
        self.errors: List[SemanticError] = []
        self.definitely_defined: Set[str] = set()

    def analyze(self, ast: dict):
        self._visit_program(ast)
        return self.table

    def _visit_program(self, node: dict):
        for stmt in node["body"]:
            self._visit_stmt(stmt, in_conditional=False)

    def _visit_stmt(self, node: dict, in_conditional: bool):
        t = node["type"]
        if t == "Assign":
            self._visit_assign(node, in_conditional)
        elif t == "Print":
            self._visit_print(node)
        elif t == "If":
            self._visit_if(node)
        else:
            raise SemanticError(f"Nodo desconocido: {t}")

    def _visit_assign(self, node: dict, in_conditional: bool):
        val = self._eval_expr(node["value"])
        name = node["name"]
        self.table.declare(name, scope="global", value=val, conditional=in_conditional)
        if not in_conditional:
            self.definitely_defined.add(name)

    def _visit_print(self, node: dict):
        name = self._get_var_name(node["expr"])
        if name and name not in self.definitely_defined:
            entry = self.table.lookup(name)
            if entry is None:
                self.errors.append(SemanticError(f"Variable '{name}' usada sin definir."))
            elif entry["conditional"]:
                self.warnings.append(
                    SemanticWarning(
                        f"'{name}' puede no estar inicializada en escribir({name}) "
                        f"— solo se define dentro de un bloque 'si'."
                    )
                )

    def _visit_if(self, node: dict):
        self._eval_expr(node["condition"])
        for stmt in node["body"]:
            self._visit_stmt(stmt, in_conditional=True)

    def _eval_expr(self, node: dict):
        t = node["type"]
        if t == "Num":
            return node["value"]
        elif t == "Var":
            entry = self.table.lookup(node["name"])
            if entry:
                return entry["value"]
            return None
        elif t == "BinOp":
            left  = self._eval_expr(node["left"])
            right = self._eval_expr(node["right"])
            if left is None or right is None:
                return None
            op = node["op"]
            ops = {'+': left+right, '-': left-right, '*': left*right,
                   '>': left>right, '<': left<right, '>=': left>=right,
                   '<=': left<=right, '==': left==right}
            return ops.get(op, None)
        return None

    def _get_var_name(self, node: dict):
        if node["type"] == "Var":
            return node["name"]
        return None

PROGRAMA = """\
inicio
    a = 10
    b = 20
    c = a + b * 2
    si (c > 30) entonces
        escribir(c)
        d = c - 10
    finsi
    escribir(d)
fin
"""

if __name__ == '__main__':
    ast = parse(PROGRAMA)
    analyzer = SemanticAnalyzer()
    table = analyzer.analyze(ast)

    print("=== TABLA DE SÍMBOLOS ===")
    table.print_table()

    if analyzer.warnings:
        print("\n=== ADVERTENCIAS SEMÁNTICAS ===")
        for w in analyzer.warnings:
            print(w)
    else:
        print("\nSin advertencias semánticas.")

    if analyzer.errors:
        print("\n=== ERRORES SEMÁNTICOS ===")
        for e in analyzer.errors:
            print(f"ERROR: {e}")
    else:
        print("Sin errores semánticos.")