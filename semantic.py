class SymbolTable:
    def __init__(self):
        self.ambitos = [{}]
        self.historial = []

    def push_scope(self, scope_name):
        self.ambitos.append({"_name": scope_name})

    def pop_scope(self):
        self.historial.append(list(self.ambitos))
        self.ambitos.pop()

    def declare(self, name, var_type):
        self.ambitos[-1][name] = {"type": var_type}

    def lookup(self, name):
        for scope in reversed(self.ambitos):
            if name in scope:
                return scope[name]
        return None

    def obtener_tipo_variable(self, name):
        entry = self.lookup(name)
        return entry["type"] if entry else None

    def imprimir_resumen_final(self):
        print("\n--- HISTORIAL DE ÁMBITOS (imprimir_resumen_final) ---")
        for i, snapshot in enumerate(self.historial):
            print(f"Estado antes de cerrar el ámbito {i+1}:")
            for j, scope in enumerate(snapshot):
                print(f"  Nivel {j}: {scope}")

class SemanticAnalyzer:
    def __init__(self):
        self.table = SymbolTable()
        self.errors = []

    def analyze(self, ast):
        self.table.ambitos[0]["_name"] = "Global"
        self._visit(ast)
        self.table.imprimir_resumen_final()
        if self.errors:
            print("\nERRORES SEMÁNTICOS:")
            for e in self.errors: 
                print(f"- {e}")
        return self.table

    def _visit(self, node):
        t = node["type"]
        if t == "Program":
            for stmt in node["body"]: 
                self._visit(stmt)
        elif t == "VarDecl":
            name = node["name"]
            if name in self.table.ambitos[-1] and name != "_name":
                self.errors.append(f"Redeclaración en el mismo ámbito de '{name}'")
            if len(self.table.ambitos) > 1 and self.table.lookup(name):
                self.errors.append(f"Shadowing: Variable local '{name}' oculta una declaración superior")
                
            self.table.declare(name, node["var_type"])
            if node["value"]:
                val_type = self._get_expr_type(node["value"])
                if node["var_type"] == "int" and val_type == "float":
                    self.errors.append(f"Incompatibilidad de tipos: asignando float a int en '{name}'")
        elif t == "FuncDecl":
            self.table.declare(node["name"], node["ret_type"])
            self.table.push_scope(f"Func_{node['name']}")
            for p in node["params"]:
                self.table.declare(p["name"], p["type"])
            self._visit(node["body"])
            self.table.pop_scope()
        elif t == "Block":
            self.table.push_scope("Block")
            for stmt in node["body"]: 
                self._visit(stmt)
            self.table.pop_scope()
        elif t == "Assign":
            name = node["name"]
            var_type = self.table.obtener_tipo_variable(name)
            if not var_type:
                self.errors.append(f"Variable '{name}' usada sin ser declarada")
            else:
                val_type = self._get_expr_type(node["value"])
                if var_type == "int" and val_type == "float":
                    self.errors.append(f"Incompatibilidad de tipos: asignando float a int en '{name}'")
        elif t == "Print":
            self._get_expr_type(node["expr"])

    def _get_expr_type(self, node):
        t = node["type"]
        if t == "Num": return "int"
        if t == "NumFloat": return "float"
        if t == "Var":
            var_type = self.table.obtener_tipo_variable(node["name"])
            if not var_type:
                self.errors.append(f"Variable '{node['name']}' no declarada usada en una expresión")
                return "error"
            return var_type
        if t == "BinOp":
            lt = self._get_expr_type(node["left"])
            rt = self._get_expr_type(node["right"])
            if lt == "float" or rt == "float": 
                return "float"
            return "int"
        return "error"