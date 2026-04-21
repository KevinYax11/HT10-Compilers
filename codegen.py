from parser import parse
from typing import List, Optional, Tuple, Dict

class Instr:
    pass

class Assign3(Instr):
    def __init__(self, dest, src):
        self.dest = dest
        self.src  = src
    def __str__(self):
        return f"{self.dest} = {self.src}"

class BinOp3(Instr):
    def __init__(self, dest, left, op, right):
        self.dest  = dest
        self.left  = left
        self.op    = op
        self.right = right
    def __str__(self):
        return f"{self.dest} = {self.left} {self.op} {self.right}"

class IfFalse(Instr):
    def __init__(self, cond, label):
        self.cond  = cond
        self.label = label
    def __str__(self):
        return f"if_false {self.cond} goto {self.label}"

class Goto(Instr):
    def __init__(self, label):
        self.label = label
    def __str__(self):
        return f"goto {self.label}"

class Label(Instr):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return f"{self.name}:"

class Print3(Instr):
    def __init__(self, var):
        self.var = var
    def __str__(self):
        return f"escribir {self.var}"

class CodeGen:
    def __init__(self):
        self.code: List[Instr] = []
        self.temp_count = 0
        self.label_count = 0

    def new_temp(self) -> str:
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self) -> str:
        self.label_count += 1
        return f"L{self.label_count}"

    def emit(self, instr: Instr):
        self.code.append(instr)

    def generate(self, ast: dict) -> List[Instr]:
        for stmt in ast["body"]:
            self._gen_stmt(stmt)
        return self.code

    def _gen_stmt(self, node: dict):
        t = node["type"]
        if t == "Assign":
            val = self._gen_expr(node["value"])
            self.emit(Assign3(node["name"], val))
        elif t == "Print":
            val = self._gen_expr(node["expr"])
            self.emit(Print3(val))
        elif t == "If":
            cond = self._gen_expr(node["condition"])
            label_end = self.new_label()
            self.emit(IfFalse(cond, label_end))
            for stmt in node["body"]:
                self._gen_stmt(stmt)
            self.emit(Label(label_end))

    def _gen_expr(self, node: dict) -> str:
        t = node["type"]
        if t == "Num":
            return str(node["value"])
        elif t == "Var":
            return node["name"]
        elif t == "BinOp":
            left  = self._gen_expr(node["left"])
            right = self._gen_expr(node["right"])
            temp  = self.new_temp()
            self.emit(BinOp3(temp, left, node["op"], right))
            return temp
        raise ValueError(f"Expresión desconocida: {t}")

class Optimizer:
    def optimize(self, code: List[Instr]) -> List[Instr]:
        code = self._constant_folding(code)
        code = self._dead_code_elimination(code)
        return code

    def _constant_folding(self, code: List[Instr]) -> List[Instr]:
        env: Dict[str, object] = {}
        result = []

        for instr in code:
            if isinstance(instr, BinOp3):
                lv = self._val(instr.left,  env)
                rv = self._val(instr.right, env)
                if lv is not None and rv is not None:
                    folded = self._apply_op(lv, instr.op, rv)
                    env[instr.dest] = folded
                    result.append(Assign3(instr.dest, str(folded)))
                else:
                    result.append(instr)

            elif isinstance(instr, Assign3):
                sv = self._val(instr.src, env)
                if sv is not None:
                    env[instr.dest] = sv
                    result.append(Assign3(instr.dest, str(sv)))
                else:
                    result.append(instr)

            elif isinstance(instr, IfFalse):
                cv = self._val(instr.cond, env)
                if cv is not None:
                    instr._folded_cond = bool(cv)
                result.append(instr)

            else:
                result.append(instr)

        return result

    def _val(self, operand: str, env: dict):
        if operand in env:
            return env[operand]
        try:
            return int(operand)
        except (ValueError, TypeError):
            return None

    def _apply_op(self, l, op, r):
        ops = {
            '+': l + r, '-': l - r, '*': l * r,
            '>': int(l > r), '<': int(l < r),
            '>=': int(l >= r), '<=': int(l <= r), '==': int(l == r),
        }
        if op == '/' and r != 0:
            return l // r
        return ops.get(op)

    def _dead_code_elimination(self, code: List[Instr]) -> List[Instr]:
        result = []
        skip_until: Optional[str] = None

        i = 0
        while i < len(code):
            instr = code[i]

            if skip_until:
                if isinstance(instr, Label) and instr.name == skip_until:
                    skip_until = None
                i += 1
                continue

            if isinstance(instr, IfFalse) and hasattr(instr, '_folded_cond'):
                if instr._folded_cond:
                    skip_until = instr.label
                    i += 1
                    continue
                else:
                    skip_until = instr.label
                    i += 1
                    continue

            result.append(instr)
            i += 1

        return result

def print_code(title: str, code: List[Instr]):
    print(f"\n{'═'*50}")
    print(f"  {title}")
    print('═'*50)
    for instr in code:
        indent = "  " if not isinstance(instr, Label) else ""
        print(f"  {indent}{instr}")

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

    gen = CodeGen()
    raw_code = gen.generate(ast)
    print_code("CÓDIGO 3 DIRECCIONES - SIN OPTIMIZAR", raw_code)

    opt = Optimizer()
    optimized = opt.optimize(raw_code)
    print_code("CÓDIGO 3 DIRECCIONES - OPTIMIZADO", optimized)

    print(f"\nInstrucciones: {len(raw_code)} -> {len(optimized)}")
    print("  Optimizaciones: Plegado de constantes + Eliminación de código muerto")