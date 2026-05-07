import re
from dataclasses import dataclass

TOKENS = [
    ('KW', r'\b(int|float|void|escribir)\b'),
    ('FLOAT', r'\d+\.\d+'),
    ('NUM', r'\d+'),
    ('ID', r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('OP_ASSIGN', r'='),
    ('OP_PLUS', r'\+'),
    ('OP_MULT', r'\*'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LBRACE', r'\{'),
    ('RBRACE', r'\}'),
    ('SEMI', r';'),
    ('SKIP', r'[ \t\n]+')
]

@dataclass
class Token:
    kind: str
    value: str
    line: int
    col: int

def tokenize(source: str):
    tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKENS)
    result = []
    line_num = 1
    line_start = 0
    for m in re.finditer(tok_regex, source):
        kind = m.lastgroup
        value = m.group()
        if kind == 'SKIP':
            line_num += value.count('\n')
            continue
        if kind == 'KW':
            kind = 'KW_' + value.upper()
        result.append(Token(kind, value, line_num, m.start() - line_start))
    result.append(Token('EOF', '', line_num, 0))
    return result