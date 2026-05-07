import json
from parser import parse
from semantic import SemanticAnalyzer

CODIGO_PRUEBA = """
int x = 10;
void test(int a) {
    int y = a * 2;
    {
        float x = 5.5; 
        y = y + x;
    }
    x = y + 1;
    escribir(z);
}
"""

if __name__ == '__main__':
    ast = parse(CODIGO_PRUEBA)
    
    print("\n--- AST PARA JSON CRACK ---")
    print(json.dumps(ast, indent=2, ensure_ascii=False))
    
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)