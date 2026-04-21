import json
from lexer import tokenize, Token
from typing import List, Optional, Any, Dict

class ParseError(Exception):
    pass

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def current(self) -> Token:
        return self.tokens[self.pos]

    def peek(self, offset=1) -> Token:
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]

    def consume(self, expected_kind: Optional[str] = None) -> Token:
        tok = self.current()
        if expected_kind and tok.kind != expected_kind:
            raise ParseError(
                f"Línea {tok.line}: Se esperaba '{expected_kind}', "
                f"se encontró '{tok.kind}' ({tok.value!r})"
            )
        self.pos += 1
        return tok

    def match(self, *kinds) -> bool:
        return self.current().kind in kinds

    def parse_program(self) -> Dict:
        self.consume('KW_INICIO')
        body = self.parse_stmt_list()
        self.consume('KW_FIN')
        self.consume('EOF')
        return {"type": "Program", "body": body}

    def parse_stmt_list(self) -> List[Dict]:
        stmts = []
        stop = {'KW_FIN', 'KW_FINSI', 'KW_FINFUNCION', 'EOF'}
        while not self.match(*stop):
            stmts.append(self.parse_stmt())
        return stmts

    def parse_stmt(self) -> Dict:
        tok = self.current()
        if tok.kind == 'KW_ESCRIBIR':
            return self.parse_print()
        elif tok.kind == 'KW_SI':
            return self.parse_if()
        elif tok.kind == 'ID':
            return self.parse_assign()
        else:
            raise ParseError(f"Línea {tok.line}: Sentencia inesperada: {tok.value!r}")

    def parse_assign(self) -> Dict:
        name = self.consume('ID').value
        self.consume('OP_ASSIGN')
        value = self.parse_expr()
        return {"type": "Assign", "name": name, "value": value}

    def parse_print(self) -> Dict:
        self.consume('KW_ESCRIBIR')
        self.consume('LPAREN')
        expr = self.parse_expr()
        self.consume('RPAREN')
        return {"type": "Print", "expr": expr}

    def parse_if(self) -> Dict:
        self.consume('KW_SI')
        self.consume('LPAREN')
        condition = self.parse_cond()
        self.consume('RPAREN')
        self.consume('KW_ENTONCES')
        body = self.parse_stmt_list()
        self.consume('KW_FINSI')
        return {"type": "If", "condition": condition, "body": body}

    def parse_cond(self) -> Dict:
        left = self.parse_expr()
        rel_ops = {'OP_GT', 'OP_LT', 'OP_GTE', 'OP_LTE', 'OP_EQ'}
        if not self.match(*rel_ops):
            raise ParseError(f"Línea {self.current().line}: Operador relacional esperado")
        op = self.consume().value
        right = self.parse_expr()
        return {"type": "BinOp", "op": op, "left": left, "right": right}

    def parse_expr(self) -> Dict:
        node = self.parse_term()
        while self.match('OP_PLUS', 'OP_MINUS'):
            op = self.consume().value
            right = self.parse_term()
            node = {"type": "BinOp", "op": op, "left": node, "right": right}
        return node

    def parse_term(self) -> Dict:
        node = self.parse_factor()
        while self.match('OP_MULT', 'OP_DIV'):
            op = self.consume().value
            right = self.parse_factor()
            node = {"type": "BinOp", "op": op, "left": node, "right": right}
        return node

    def parse_factor(self) -> Dict:
        tok = self.current()
        if tok.kind == 'NUM':
            self.consume()
            return {"type": "Num", "value": int(tok.value)}
        elif tok.kind == 'ID':
            self.consume()
            return {"type": "Var", "name": tok.value}
        elif tok.kind == 'LPAREN':
            self.consume('LPAREN')
            node = self.parse_expr()
            self.consume('RPAREN')
            return node
        else:
            raise ParseError(f"Línea {tok.line}: Factor inesperado: {tok.value!r}")

def parse(source: str) -> Dict:
    tokens = tokenize(source)
    parser = Parser(tokens)
    return parser.parse_program()

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
    print("AST (JSON):")
    print(json.dumps(ast, indent=2, ensure_ascii=False))