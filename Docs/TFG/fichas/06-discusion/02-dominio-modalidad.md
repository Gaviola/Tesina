# Ficha 6.2 — Especialización de dominio frente a modalidad

Archivo: `Chapters/06-Discusion/02-dominio-modalidad.tex`. Label: `sec:disc_especializacion`.

## Hilo conductor

Pregunta: ¿qué separa a los VLM que distinguen las clases de los que colapsan?
Viene de: 6.1 (PI1 negativa para los VLM usados como tales). Deja instalado: la representación especializada sirve
para recuperar; el diagnóstico, de un supervisado.

```
P1  Dos explicaciones (modalidad / dominio) y qué predice cada una en SkinCAP                     define
     ↓ consecuencia
P2  SkinCAP y gris → especialización, sin excluir del todo la modalidad                          interpreta
     ↓ ampliación
P3  Control de la representación: DermLIP > Swin ImageNet con tres cabezas; conjetura: el paso
    por el modelo de lenguaje                                                                     interpreta
     ↓ contraste
P4  SkinVL: la especialización generativa depende del formato (0.001 aquí, 51.3 % en su protocolo) limita
     ↓ comparación
P5  Literatura (zeng, jiang, DermFM-Zero) y consecuencia para el diseño                           justifica
→ Transición: la división del trabajo.
```

Citas: `zeng2025mmskin`, `jiang2026multimodal`, `yan2026dermfmzero`.

## Decisiones

- «Dominio frente a modalidad» se enuncia con el alcance del control (no excluye del todo la modalidad), como en 4.3.2.
- La explicación del contraste generativo/contrastivo va marcada como conjetura.
