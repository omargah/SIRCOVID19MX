# Verificación de las derivaciones del Cap. 2 (a–k)

Cada derivación tiene un archivo en `tests/teoria/` con (1) la igualdad
simbólica en SymPy y (2) una comprobación numérica contra `src/sir.py`.

```
make teoria            # equivale a: python -m pytest -m teoria
```

Estado tras la integración (rama `integracion/pt1-v2`, con el `src/sir.py`
actual en personas): **87 pasan, 3 xfail estrictos** (discrepancias
documentadas abajo; si se corrigen, pytest avisa con XPASS → fallo).
Antes de la integración, contra el `sir.py` viejo (fracciones): 87 pasaban y
2 eran xfail. Los 2 xfail originales **siguen siendo errores reales** con el
`sir.py` actual (error 1.5e-9 > 1e-9; error relativo 3.2 % > 1e-5) y ahora
declaran `raises=AssertionError` para que un error de llamada no los tape.

> **Adaptación a la firma actual (2026-11-05).** `src/sir.py` cambió de
> `integrar_sir(R0, gamma, s0, i0, t) -> (s, i)` a
> `integrar_sir(R0, D, S0, I0, N, t) -> (S, I, R)`, y `s0` de
> `incidencia_semanal` ahora es (S0+I0)/N. Las pruebas llaman a
> `tests/teoria/firma_sir.py`, que solo traduce (N = 1, D = 1/γ). No se
> cambió `src/sir.py` ni ninguna tolerancia. Los casos con `s0 = 1.0` e
> `i0 > 0` (S0 + I0 > N, que el `sir.py` actual rechaza) se pasaron a
> `s0 = 1 − i0` en la propia prueba.

> **Advertencia de alcance.** El texto del Cap. 2 todavía no está en el
> repositorio (F2 abierta). Las afirmaciones verificadas son las enunciadas
> en el docstring de cada archivo, en su forma estándar. Al escribir el
> capítulo hay que comprobar que las ecuaciones coinciden con esos
> docstrings (mismas variables, misma rama de W, misma definición de D).

## Tabla derivación → test

| | Derivación | Archivo | Igualdad simbólica (SymPy) | Comprobación numérica (sir.py) |
|---|---|---|---|---|
| a | Adimensionalización | `test_a_adimensionalizacion.py` | campo(N s, N i) = Nγ·campo adim. con β = R0γ; regla de la cadena τ = γt; R0 sin unidades | Trayectorias con γ distintas coinciden en τ; `incidencia_semanal` lineal en N y ρ (la versión exacta rtol=1e-12 es xfail, ver discrepancia 9) |
| b | Conservación de N y positividad | `test_b_conservacion_positividad.py` | Σ campo = 0; S = S0 e^{−(β/N)∫I} e I = I0 e^{∫(βS/N−γ)} satisfacen las EDO | s, i > 0; s ↓, r ↑; r(t)−r(0) = γ∫i (cuadratura independiente); rechaza s0, i0 ≤ 0 |
| c | Integral primera H | `test_c_integral_primera.py` | dH/dt = 0 (fracciones y dimensional); `dsolve` de di/ds da H | max\|H − H0\| < 1e-8 en 3 regímenes |
| d | Equilibrios, sin endémico | `test_d_equilibrios.py` | `solve` → solo I = 0; sin solución con I > 0; autovalores {0, γ(R0 s*−1)}; control: con demografía sí hay endémico | i → 0 con s∞ < 1/R0; si R0 s0 < 1, i decrece desde t = 0 |
| e | R_eff, pico en S = N/R0, I_max | `test_e_reff_pico_imax.py` | dI/dt = γ(R_eff−1)I; pico en S = N/R0 (máximo); I_max desde H | i_max numérico vs fórmula (< 1e-8); s(pico) = 1/R0; signo de di/dt = signo(R_eff−1) |
| f | Tamaño final y W de Lambert | `test_f_tamano_final_lambert.py` | ecuación implícita desde H; s∞ = −W0(−R0 s0 e^{−R0(s0+i0)})/R0 la resuelve; caso z = 1 − e^{−R0 z} | s(5000 d) vs W0 (< 1e-8); argumento ∈ (−1/e, 0); la rama W−1 da la raíz no física |
| g | R0 S0/N = 1 + rD vs exp(rD) | `test_g_crecimiento_1_mas_rD.py` | linealización r = γ(R0 s0 − 1) ⇒ 1 + rD; exp(x) − (1+x) = x²/2 + … > 0 | 1 + rD recupera R0 s0 (< 1e-6); exp(rD) sobrestima +9.9 % con R_eff(0) = 1.5, D = 7 d; misma r en la incidencia semanal |
| h | Intervalo de generación gamma | `test_h_intervalo_generacion_gamma.py` | Euler–Lotka con Gamma(k, media T) ⇒ R = (1 + rT/k)^k; k = 1 → 1 + rT; k → ∞ → e^{rT}; R crece con k | k = 1 contra sir.py; k = 1, 2, 3, 5, 10 con cadena lineal (autovalor dominante, **no sir.py**) |
| i | Casos = ρ × incidencia | `test_i_casos_incidencia.py` | incidencia = −ds/dt = βsi; pico de incidencia antes que el de i; γ∫i = tamaño final | μ_k = ρN∫βsi (cuadratura); argmax incidencia < argmax i; Σ prevalencia / Σ casos ≈ D |
| j | β(t) por tramos, R_t | `test_j_beta_por_tramos.py` | dI/dt = γ(R_t−1)I para β(t) arbitraria; H_j conservada por tramo; salto de H en el corte | sir.py encadenado vs DOP853 independiente; d ln i/dt = γ(R_t−1); i ↓ en tramo con R_t < 1; salto de H medido = fórmula |
| k | Conexiones físicas | `test_k_conexiones_fisicas.py` | k1 acción de masas (ν·v = SIR, (1,1,1) ∈ nulo izq.); k2 campo = J∇H, J antisimétrica; k3 z = 2ε − 8ε²/3 cerca de R0 = 1 | J∇H y ν·v vs derivada numérica de la trayectoria; z(R0 = 1+ε) vs W0 y vs serie; sin ola para R0 < 1 |

## Discrepancias encontradas

Ninguna derivación resultó falsa. Las discrepancias son entre lo que
`src/sir.py` documenta o puede hacer y lo que hace:

1. **Error global de LSODA mayor al documentado** (b; xfail estricto
   `test_sir_py_cumple_su_tolerancia_documentada_en_ola_explosiva`).
   `sir.py` dice que con RTOL = 1e-10 el error es "~1e-10 relativo". Eso
   vale para el error *local* por paso. En una ola explosiva (R0 = 15) el
   error *global* en s cerca del pico es ~1e-8. No es la interpolación de
   `t_eval`: integrando hasta ese instante como punto final el error es el
   mismo. DOP853 o Radau con la misma rtol quedan en ~1e-10.
   `tests/test_sir.py` no lo detectaba porque solo mira s(t → ∞), que es un
   atractor (el error se contrae al terminar la ola). Con los valores del
   proyecto (R0 = 2.5) el error es ~4e-10: despreciable frente al ruido.
2. **Cancelación en `incidencia_semanal` con i0 diminuto** (i; xfail
   estricto `test_incidencia_precisa_con_i0_diminuto`). μ_k = ρN(s_k − s_{k+1})
   resta dos números O(1) con error ~RTOL·s. Al inicio de una ola con i0
   muy chico, Δs es comparable a ese error. Error relativo medido de μ_k:
   i0 = 1e-10 → 5 %, 1e-8 → 0.35 %, 1e-6 → 4e-5, 1e-5 → 2e-6.
   Impacto: nulo con i0 = 1e-5. Si el optimizador explora i0 ≪ 1e-8, la
   verosimilitud puede volverse rugosa. Arreglo posible: integrar la
   incidencia acumulada c(t) como tercera variable.
3. **sir.py no implementa β(t)** (j) — *RESUELTA en el `sir.py` actual*:
   existe `integrar_sir_tramos`. La prueba (j) sigue encadenando `integrar_sir`
   tramo por tramo (verifica el empalme de forma independiente); falta
   agregar una prueba contra `integrar_sir_tramos` directamente.
4. **(g) 1 + rD frente a exp(rD)** no es un error del código. Para el SIR
   la relación correcta es 1 + rD, y es la que usan `sir.py` y el código
   anterior (`v0-anterior/analisis_montecarlo.py`). exp(rD) corresponde a
   un intervalo de generación fijo (k → ∞ en h) y sobrestima R_eff(0)
   para cualquier r ≠ 0 (+9.9 % con R_eff(0) = 1.5, D = 7 d).
   Si el Cap. 2 usa exp(rD) con un modelo SIR, es inconsistente.
5. **(h) solo k = 1 se puede probar contra sir.py**, porque el SIR tiene
   intervalo de generación exponencial. Para k > 1 la comprobación numérica
   usa una cadena lineal independiente (autovalor dominante), no sir.py.
6. **(i) Supuesto no verificable aquí:** la SSA fecha los casos por inicio
   de síntomas y μ_k usa la fecha de infección; el desfase (incubación) no
   está en el modelo. Es una limitación del modelo, no de la derivación.
7. **(k) La interpretación es mía.** "Conexiones físicas" se tomó como
   acción de masas, estructura de Poisson y umbral transcrítico; hay que
   ajustarla al texto del Cap. 2 cuando exista.
8. **Tolerancia ampliada a propósito** en un caso de
   `test_sir_py_positivo_monotono_y_conserva` (R0 = 15: 5e-8 en vez de
   1e-9), por la discrepancia 1. Está anotada en el código.
9. **Escala exacta en N y ρ ya no se cumple (a; xfail estricto
   `test_sir_py_N_y_rho_solo_escalan`).** Con el `sir.py` viejo (fracciones)
   `incidencia_semanal` era exactamente lineal en N y ρ (rtol = 1e-12). Con el
   actual integra en personas y el error de LSODA depende de N: la diferencia
   medida es ~9e-9 relativo. La linealidad matemática sigue valiendo; la
   implementación solo la cumple al nivel del integrador. La prueba original
   (1e-12) quedó como xfail; se agregó
   `test_sir_py_N_y_rho_solo_escalan_al_nivel_del_integrador` (rtol = 1e-7,
   ~10 veces el error medido).
