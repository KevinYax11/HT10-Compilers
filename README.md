```markdown
# Mini-Compilador Pseudo-C

## Autores
- Ivan Alexander Ordoñez Lopez - 1567523
- Kevin Miguel Yax Puác - 1529422

## Requisitos del Sistema
- **Python 3.x**: Necesario para ejecutar el código fuente del compilador.
- **Java**: Indispensable para correr el simulador MARS.

---

## Instrucciones de Uso

### 1. Ejecución del Flujo Completo

Para ejecutar todo el proceso de compilación de una sola vez (desde el análisis léxico hasta la generación de código ensamblador):

1. **Descomprimir** el archivo ZIP proporcionado.
2. Abrir una terminal o línea de comandos.
3. Ingresar a la carpeta principal del proyecto:
   ```bash
   cd repo/
   ```
4. Ejecutar el script principal:
   ```bash
   python compilador.py
   ```

> Este comando ejecutará las 6 fases de manera secuencial y mostrará los detalles de cada etapa directamente en la consola.

---

### 2. Ejecución de Fases Individuales

Si se requiere visualizar el comportamiento o la salida de una fase en específico, es posible ejecutar los módulos de forma independiente:

- **Analizador Léxico**: Muestra los tokens generados.
  ```bash
  python lexer.py
  ```

- **Analizador Sintáctico**: Muestra la estructura del AST en formato JSON.
  ```bash
  python parser.py
  ```

- **Analizador Semántico**: Muestra la tabla de símbolos, advertencias y errores.
  ```bash
  python semantic.py
  ```

- **Generación de Código de 3 Direcciones**: Muestra el código intermedio (con y sin optimizar).
  ```bash
  python codegen.py
  ```

---

### 3. Visualización del AST (Abstract Syntax Tree)

Para obtener una representación gráfica e interactiva del árbol generado por el analizador sintáctico:

1. Ejecuta `parser.py` o `compilador.py`.
2. **Copia** el bloque de texto en formato JSON que se imprime en la consola.
3. Ingresa al sitio web: [https://jsoncrack.com/editor](https://jsoncrack.com/editor)
4. **Pega** el código JSON en el panel izquierdo del editor.
5. El sitio generará automáticamente un diagrama visual estructurado del AST.

---

### 4. Prueba y Ejecución del Código Ensamblador (.asm)

Al finalizar su ejecución, el compilador genera un archivo llamado `programa.asm` que contiene el código objeto en lenguaje ensamblador MIPS. Para probar que el código funciona correctamente:

1. Descargar **MARS** (MIPS Assembler and Runtime Simulator), el cual es un simulador gratuito.
2. Abrir la aplicación MARS.
3. Cargar el archivo `programa.asm` generado en la carpeta del proyecto.
4. Ensamblar el código yendo a la opción **Run -> Assemble** (o presionando `F3`).
5. Ejecutar el programa yendo a la opción **Run -> Go** (o presionando `F5`).
6. Observar la pestaña **Run I/O** en la parte inferior de MARS; la salida del programa de prueba por defecto debería imprimir los valores `50` y `40` en líneas separadas.
```
