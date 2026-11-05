# tests/teoria — verificación de las derivaciones del Cap. 2

Un archivo por derivación (a–k). Cada uno tiene dos partes:

1. **Igualdad simbólica (SymPy):** la derivación se reproduce y la igualdad
   se comprueba con `sympy.simplify(lhs - rhs) == 0` (o equivalente).
2. **Comprobación numérica contra `src/sir.py`:** la misma afirmación se
   prueba sobre trayectorias del integrador del proyecto.

Correr solo estas pruebas:

    make teoria        # o: python -m pytest -m teoria

Tabla derivación → test y discrepancias encontradas: `docs/teoria_verificacion.md`.
