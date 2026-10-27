# Ficha 6.7 — Limitaciones y amenazas a la validez

Archivo: `Chapters/06-Discusion/07-limitaciones.tex`. Label: `sec:disc_limitaciones`.

## Hilo conductor

Pregunta: ¿hasta dónde valen las conclusiones?
Viene de: 6.6 (lo que la restricción deja fuera). Deja instalado: el alcance con que el Cap. 7 enuncia conclusiones.

```
P1  Condiciones de validez; orden de la sección                                                  organiza
L1  Amenazas (lista): interna (TTA/una vista, dos GPU, 400 imágenes); conclusión estadística
    (unidad imagen, ejecución de referencia, DF 17, sin prueba del ensamble); constructo
    (consistencia, Nivel 1, cobertura, diferencial ≠ exactitud); externa (HIBA −40 %, mapeo AKIEC) limita
P2  Alcance: sin especialistas, sin validez clínica ni producto; solo dermatoscopía                limita
P3  Ancla de una ejecución (7/10 melanomas, sobre la media)                                       limita
L2  Decisiones sin evaluar (lista): umbral de melanoma en el ancla; plantilla diferencial y piloto
    con 17 imágenes de prueba; otros anclajes y generadores; errores compartidos                 abre
P4  Respaldo: independiente (validación, prueba por lesión, HIBA, ruteo sin umbral) o exploratorio
    (fallas, ejemplos) → Cap. 7                                                                   delimita
```

Integra 4.6 p3 y 5.6 p5–p6, y las limitaciones de alcance que el esqueleto recibía del Cap. 1.

## Decisiones

- El costo experimental (cola del clúster) del documento de experimentación no entra: es un dato interno; queda solo
  su efecto (ablaciones sobre 400 imágenes).
- La SVM sobre DermLIP no se presenta como «mejor que Swin» (lo era en v3); en la partición por lesión queda por
  debajo, así que la limitación se enuncia como «tres fuentes y no un barrido».
