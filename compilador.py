import sys
import json
from lexer import tokenize
from parser import parse
from semantic import SemanticAnalyzer
from codegen import CodeGen, Optimizer, print_code
from mips_gen import MIPSGenerator

SEPARADOR = "-" * 60

def compilar(source: str, verbose: bool = True):
    print(f"\n{SEPARADOR}")
    print(" MINI-COMPILADOR PSEUDO-C")
    print(SEPARADOR)

    if verbose:
        print(f"\n{'-'*60}")
        print(" FASE 1 - ANALISIS LEXICO")
        print(f"{'-'*60}")
    tokens = tokenize(source)
    if verbose:
        print(f" {'LINEA':<6} {'TOKEN':<18} {'LEXEMA'}")
        print(" " + "-" * 40)
        for tok in tokens:
            print(f" {tok.line:<6} {tok.kind:<18} {tok.value!r}")

    if verbose:
        print(f"\n{'-'*60}")
        print(" FASE 2 - ARBOL DE SINTAXIS ABSTRACTA (AST)")
        print(f"{'-'*60}")
    ast = parse(source)
    if verbose:
        print(json.dumps(ast, indent=2, ensure_ascii=False))

    if verbose:
        print(f"\n{'-'*60}")
        print(" FASE 3 - ANALISIS SEMANTICO")
        print(f"{'-'*60}")
    analyzer = SemanticAnalyzer()
    table = analyzer.analyze(ast)
    if verbose:
        table.print_table()
        for w in analyzer.warnings:
            print(w)
        for e in analyzer.errors:
            print(f"ERROR: {e}")

    gen = CodeGen()
    raw_code = gen.generate(ast)
    if verbose:
        print_code("FASE 4 - CODIGO 3 DIRECCIONES (sin optimizar)", raw_code)

    opt = Optimizer()
    opt_code = opt.optimize(raw_code)
    if verbose:
        print_code("FASE 5 - CODIGO 3 DIRECCIONES (optimizado)", opt_code)
        print(f"\n {len(raw_code)} instrucciones -> {len(opt_code)} instrucciones")

    mips_gen = MIPSGenerator()
    asm = mips_gen.generate(ast)
    if verbose:
        print(f"\n{'-'*60}")
        print(" FASE 6 - CODIGO ENSAMBLADOR MIPS")
        print(f"{'-'*60}")
        print(asm)

    print(f"\n{SEPARADOR}")
    print(" Compilacion completada sin errores criticos.")
    print(SEPARADOR)

    return {
        "tokens":   tokens,
        "ast":      ast,
        "symbols":  table,
        "raw_code": raw_code,
        "opt_code": opt_code,
        "asm":      asm,
    }

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
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            source = f.read()
    else:
        source = PROGRAMA

    compilar(source)