# Ficha 6.5 — Lecciones metodológicas

Archivo: `Chapters/06-Discusion/05-lecciones-metodologicas.tex`. Label: `sec:disc_lecciones`.

## Hilo conductor

Pregunta: ¿qué decisiones de evaluación pesan tanto como el modelo en las cifras?
Viene de: 6.4 (lo que miden las métricas). Deja instalado: cómo leer las comparaciones con la literatura.

```
P1  La arquitectura pesa menos que partición, regla, variación y métrica                          organiza
P2  Partición: +0.07 con fuga; del orden de la distancia a la literatura                          interpreta
P3  Regla de decisión en melanoma: 3/5 → 4/5 sin cambiar el AUC; umbral en validación (vs. yao)    interpreta
P4  Variación entre ejecuciones > 0.1 en minoritarias → media de tres; ensamble estabiliza         justifica
P5  McNemar frente a bootstrap: probar la métrica que selecciona                                  interpreta
P6  Texto: estilo (Nivel 1, BLEU de SkinVL) y enumeración (consistencia de LLaVA-Med sin anclaje)  limita
→ Transición: la comparación con la literatura en costo.
```

Integra 4.6 p2. La «inestabilidad entre semillas» del esqueleto pasa a «variación entre ejecuciones».
Citas: `kim2025skinsavvy2`, `yao2022single`.
