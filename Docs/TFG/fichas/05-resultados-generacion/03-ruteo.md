# Ficha 5.3 — Ruteo por concordancia y pipeline completo

**Estado (24/10/2026): redactada sin aprobación previa** (ver `00-capitulo.md`).

Archivo: `Chapters/05-Resultados-Generacion/03-ruteo.tex`. Label: `sec:res_gen_incertidumbre` (se conserva el del
esqueleto). Subsecciones: `sec:res_gen_concordancia`, `sec:res_gen_pipeline`, `sec:res_gen_cualitativos`. Figuras:
`fig:res_gen_ruteo` (`ruteo-niveles.pdf`), `fig:res_gen_ejemplos` (`Figures/.../ejemplos-reportes.tex`, flota con
`[!t]` porque ocupa media página). Tabla: `tab:res_gen_pipeline`.

## Hilo conductor

Pregunta: ¿la concordancia entre Swin-Tiny y el kNN reconoce los casos dudosos, y qué cambia en los reportes?
Viene de: 5.2, la cascada afirma también los errores. Deja instalado: la concordancia separa, el par cubre más, la
ganancia es del ruteo; los errores compartidos se afirman.

```
P1  Retoma 5.2; qué evalúa                                                                      orienta
5.3.1
P2  80 / 16.5 / 3.4 %; Swin acierta 0.915 frente a ~0.57: prueba la hipótesis del Cap. 3       describe/interpreta
P3  Diferencial: el par cubre 0.847 frente a 0.573; cada acierto del kNN es un error de Swin    interpreta
P4  Errores compartidos: 102 de 230; 38 de 167 melanomas afirmados (31 como NV)                 limita
P5  Por clase (fig b): NV y VASC afirmados; DF y AKIEC no; MEL: par contiene MEL en 52/54       describe
P6  Derivación: evita 20 errores (Mini) y descarta 29 aciertos                                  interpreta
5.3.2
P7  tab:res_gen_pipeline                                                                        describe
P8  Mini: +0.043 sobre la cascada, = línea base sin generador → ganancia del ruteo              interpreta
P9  LLaVA: no mejora; 144/248 <think> sin cerrar con la plantilla diferencial                   interpreta
P10 No es una exactitud; cohorte completa 0.849 → 0.870                                         limita
P11 Diagnóstico incorrecto 13.6 → 9.0 % (Mini), 9.4 → 7.1 % (LLaVA); repetición 7 → 48           describe
5.3.3
P12 Ejemplo (a) afirmativo                                                                      ejemplo
P13 (b) diferencial con eco de la instrucción; (c) error compartido con descripción verosímil    ejemplo
P14 Cierre → comparación de generadores                                                         cierra
```

## Fuentes

- `cap5_derivados.json` (`ruteo`): acierto por nivel, errores compartidos, por clase, melanoma.
- `ensemble_bootstrap{,_llava_med}_les_report_only_strict.json` (`tab_incertidumbre_e2e`).
- `uncertainty_analysis{,_llava_med}_les.json` (taxonomía por nivel; abstenidas: 20 y 17 diagnósticos incorrectos).
- `ejecuciones.md`, 18/10/2026: 144 de 248 reportes diferenciales de LLaVA-Med con `<think>` sin cerrar.
- Ejemplos: `generated_reports/mini_vlm/{full_swin_les,full_differential_les}/ISIC_00{29473,31194,33452}_report.json`.

## Decisiones y preguntas

- La cohorte completa se calcula con los aciertos del pipeline (0.901 × 1 452 = 1 308) sobre 1 503, como la
  experimentación.
- La taxonomía por nivel es la de `uncertainty_analysis.py` (cuenta el par correcto como acierto en el diferencial);
  solo se usa la fila de diagnóstico incorrecto, que coincide en definición con 5.2.4.
- Ejemplo (b) elegido con el defecto de la instrucción repetida (pregunta 5 de `00-capitulo.md`).
