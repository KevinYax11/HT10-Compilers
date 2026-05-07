from lexer import tokenize

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self): return self.tokens[self.pos]
    
    def consume(self, expected=None):
        tok = self.current()
        if expected and tok.kind != expected:
            raise Exception(f"Error sintáctico: Se esperaba {expected}, se obtuvo {tok.kind}")
        self.pos += 1
        return tok

    def match(self, *kinds): 
        return self.current().kind in kinds

    def parse_program(self):
        body = []
        while not self.match('EOF'):
            body.append(self.parse_decl())
        return {"type": "Program", "body": body}

    def parse_decl(self):
        if self.match('KW_INT', 'KW_FLOAT', 'KW_VOID'):
            var_type = self.consume().value
            name = self.consume('ID').value
            if self.match('OP_ASSIGN', 'SEMI'):
                return self.parse_var_decl_rest(var_type, name)
            elif self.match('LPAREN'):
                return self.parse_func_decl(var_type, name)
        raise Exception(f"Declaración inválida: {self.current().value}")

    def parse_var_decl_rest(self, var_type, name):
        val = None
        if self.match('OP_ASSIGN'):
            self.consume()
            val = self.parse_expr()
        self.consume('SEMI')
        return {"type": "VarDecl", "var_type": var_type, "name": name, "value": val}

    def parse_func_decl(self, ret_type, name):
        self.consume('LPAREN')
        params = []
        if not self.match('RPAREN'):
            ptype = self.consume().value
            pname = self.consume('ID').value
            params.append({"type": ptype, "name": pname})
        self.consume('RPAREN')
        body = self.parse_block()
        return {"type": "FuncDecl", "ret_type": ret_type, "name": name, "params": params, "body": body}

    def parse_block(self):
        self.consume('LBRACE')
        stmts = []
        while not self.match('RBRACE', 'EOF'):
            stmts.append(self.parse_stmt())
        self.consume('RBRACE')
        return {"type": "Block", "body": stmts}

    def parse_stmt(self):
        if self.match('LBRACE'): 
            return self.parse_block()
        if self.match('KW_INT', 'KW_FLOAT'):
            t = self.consume().value
            n = self.consume('ID').value
            return self.parse_var_decl_rest(t, n)
        if self.match('KW_ESCRIBIR'):
            self.consume()
            self.consume('LPAREN')
            e = self.parse_expr()
            self.consume('RPAREN')
            self.consume('SEMI')
            return {"type": "Print", "expr": e}
        if self.match('ID'):
            n = self.consume('ID').value
            self.consume('OP_ASSIGN')
            e = self.parse_expr()
            self.consume('SEMI')
            return {"type": "Assign", "name": n, "value": e}
        raise Exception(f"Sentencia inválida: {self.current().value}")

    def parse_expr(self):
        left = self.parse_term()
        while self.match('OP_PLUS'):
            op = self.consume().value
            right = self.parse_term()
            left = {"type": "BinOp", "op": op, "left": left, "right": right}
        return left

    def parse_term(self):
        left = self.parse_factor()
        while self.match('OP_MULT'):
            op = self.consume().value
            right = self.parse_factor()
            left = {"type": "BinOp", "op": op, "left": left, "right": right}
        return left

    def parse_factor(self):
        if self.match('NUM'): 
            return {"type": "Num", "value": int(self.consume().value)}
        if self.match('FLOAT'): 
            return {"type": "NumFloat", "value": float(self.consume().value)}
        if self.match('ID'): 
            return {"type": "Var", "name": self.consume().value}
        raise Exception("Factor inválido")

def parse(source):
    return Parser(tokenize(source)).parse_program()