import re
from dataclasses import dataclass
from typing import List, Tuple

TOKENS = [
    ('KW',        r'\b(inicio|fin|si|entonces|finsi|escribir|funcion|finfuncion|retornar)\b'),
    ('NUM',       r'\d+'),
    ('ID',        r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('OP_ASSIGN', r'=(?!=)'),
    ('OP_GTE',    r'>='),
    ('OP_LTE',    r'<='),
    ('OP_EQ',     r'=='),
    ('OP_GT',     r'>'),
    ('OP_LT',     r'<'),
    ('OP_PLUS',   r'\+'),
    ('OP_MINUS',  r'-'),
    ('OP_MULT',   r'\*'),
    ('OP_DIV',    r'/'),
    ('LPAREN',    r'\('),
    ('RPAREN',    r'\)'),
    ('COMMA',     r','),
    ('SKIP',      r'[ \t]+'),
    ('NEWLINE',   r'\n'),
    ('COMMENT',   r'#[^\n]*'),
]

@dataclass
class Token:
    kind: str
    value: str
    line: int
    col: int

    def __repr__(self):
        return f"Token({self.kind}, {self.value!r}, line={self.line})"

def tokenize(source: str) -> List[Token]:
    tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKENS)
    result: List[Token] = []
    line_num = 1
    line_start = 0

    for m in re.finditer(tok_regex, source):
        kind = m.lastgroup
        value = m.group()
        col = m.start() - line_start

        if kind == 'SKIP' or kind == 'COMMENT':
            continue
        elif kind == 'NEWLINE':
            line_num += 1
            line_start = m.end()
            continue
        elif kind == 'KW':
            kind = 'KW_' + value.upper()

        result.append(Token(kind, value, line_num, col))

    result.append(Token('EOF', '', line_num, 0))
    return result

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
    tokens = tokenize(PROGRAMA)
    print(f"{'LÍNEA':<6} {'TOKEN':<16} {'LEXEMA'}")
    print("-" * 40)
    for tok in tokens:
        print(f"{tok.line:<6} {tok.kind:<16} {tok.value!r}")