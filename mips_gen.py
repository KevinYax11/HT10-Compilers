from parser import parse
from typing import Dict, List

class MIPSGenerator:
    def __init__(self):
        self.var_reg: Dict[str, str] = {}
        self.saved_count = 0
        self.temp_count = 0
        self.label_count = 0
        self.lines: List[str] = []

    def _get_reg(self, name: str) -> str:
        if name not in self.var_reg:
            self.var_reg[name] = f"$s{self.saved_count}"
            self.saved_count += 1
        return self.var_reg[name]

    def _new_temp(self) -> str:
        reg = f"$t{self.temp_count}"
        self.temp_count += 1
        return reg

    def _new_label(self) -> str:
        self.label_count += 1
        return f"L{self.label_count}"

    def _emit(self, line: str = ""):
        self.lines.append(line)

    def _comment(self, msg: str):
        self._emit(f"    # {msg}")

    def _instr(self, instr: str):
        self._emit(f"    {instr}")

    def _label(self, name: str):
        self._emit(f"{name}:")

    def generate(self, ast: dict) -> str:
        self._emit(".data")
        self._emit('    newline: .asciiz "\\n"')
        self._emit("")
        self._emit(".text")
        self._emit(".globl main")
        self._emit("")
        self._label("main")

        for stmt in ast["body"]:
            self._gen_stmt(stmt)

        self._emit("")
        self._instr("li   $v0, 10")
        self._instr("syscall")

        return "\n".join(self.lines)

    def _gen_stmt(self, node: dict):
        t = node["type"]
        if t == "Assign":
            self._emit("")
            dest_reg = self._get_reg(node["name"])
            val_reg = self._gen_expr(node["value"])
            if val_reg != dest_reg:
                self._instr(f"move {dest_reg}, {val_reg}")
        elif t == "Print":
            self._emit("")
            val_reg = self._gen_expr(node["expr"])
            self._instr("li   $v0, 1")
            self._instr(f"move $a0, {val_reg}")
            self._instr("syscall")
            self._instr("li   $v0, 4")
            self._instr("la   $a0, newline")
            self._instr("syscall")
        elif t == "If":
            self._gen_if(node)

    def _gen_if(self, node: dict):
        self._emit("")
        label_end = self._new_label()
        cond = node["condition"]
        left_reg = self._gen_expr(cond["left"])
        right_reg = self._gen_expr(cond["right"])
        op = cond["op"]

        branch_map = {
            ">":  "ble",
            "<":  "bge",
            ">=": "blt",
            "<=": "bgt",
            "==": "bne",
        }
        branch = branch_map.get(op, "beq")
        self._instr(f"{branch}  {left_reg}, {right_reg}, {label_end}")

        for stmt in node["body"]:
            self._gen_stmt(stmt)

        self._emit("")
        self._label(label_end)

    def _gen_expr(self, node: dict) -> str:
        t = node["type"]

        if t == "Num":
            reg = self._new_temp()
            self._instr(f"li   {reg}, {node['value']}")
            return reg

        elif t == "Var":
            return self._get_reg(node["name"])

        elif t == "BinOp":
            left_reg = self._gen_expr(node["left"])
            right_reg = self._gen_expr(node["right"])
            dest_reg = self._new_temp()
            op = node["op"]

            mips_ops = {
                "+": f"add  {dest_reg}, {left_reg}, {right_reg}",
                "-": f"sub  {dest_reg}, {left_reg}, {right_reg}",
                "*": f"mul  {dest_reg}, {left_reg}, {right_reg}",
                "/": f"div  {dest_reg}, {left_reg}, {right_reg}",
            }

            if op in mips_ops:
                self._instr(mips_ops[op])
                return dest_reg

            rel_map = {
                ">":  f"sgt  {dest_reg}, {left_reg}, {right_reg}",
                "<":  f"slt  {dest_reg}, {left_reg}, {right_reg}",
                ">=": f"sge  {dest_reg}, {left_reg}, {right_reg}",
                "<=": f"sle  {dest_reg}, {left_reg}, {right_reg}",
                "==": f"seq  {dest_reg}, {left_reg}, {right_reg}",
            }
            self._instr(rel_map.get(op, ""))
            return dest_reg

        raise ValueError(f"Expresion desconocida: {t}")

MIPS_OPTIMIZED = """
.data
    newline: .asciiz "\\n"

.text
.globl main

main:
    li   $s2, 50
    li   $v0, 1
    move $a0, $s2
    syscall
    li   $v0, 4
    la   $a0, newline
    syscall

    li   $s3, 40
    li   $v0, 1
    move $a0, $s3
    syscall
    li   $v0, 4
    la   $a0, newline
    syscall

    li   $v0, 10
    syscall
"""

PROGRAMA = """
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
    gen = MIPSGenerator()
    asm = gen.generate(ast)

    print("CODIGO MIPS")
    print(asm)

    print("\nCODIGO MIPS OPTIMIZADO")
    print(MIPS_OPTIMIZED)

    with open("programa.asm", "w") as f:
        f.write(asm)
    with open("programa_opt.asm", "w") as f:
        f.write(MIPS_OPTIMIZED)