# Ficha del Capítulo 1 — Introducción

Contrato vigente del capítulo. El historial de las revisiones anteriores (plan del 28/09, revisión del
tutor y decisiones de esa fecha) está en `historial.md`; lo que de ahí sigue rigiendo está consolidado
abajo, en «Decisiones vigentes».

## Estructura vigente: tercera revisión del tutor (2026-10-09)

Según el tutor, el capítulo «más o menos está bien» y faltan algunas cuestiones: los comentarios de las p26–27
y el pedido de reforzar las conexiones de 1.1 para que la argumentación lleve a las preguntas y a los
objetivos (`feedback/cap1_2/feedback_cap1_y_2_v3.md`).

| Sección | Archivo | Qué hace | Cambios pendientes |
|---|---|---|---|
| Introducción del capítulo | `00-capitulo.tex` | Qué contiene el capítulo y cómo se organiza | Nombrar primero las preguntas y después los objetivos (p26) |
| 1.1 Contexto y motivación | `01-contexto-motivacion.tex` | Del problema clínico a las dos cuestiones abiertas | Ficha `01-contexto-motivacion.md` |
| 1.2 Objetivos | `02-objetivos.tex` | PI1 y PI2, objetivo general, OE1–OE3, tabla objetivo–pregunta–capítulo | Primera oración que retome las dos cuestiones de 1.1; revisar OE3 (decisión 6) |
| 1.3 Organización del documento | `03-organizacion.tex` | Un párrafo por capítulo | Revisar al final, cuando el Cap. 2 tenga sus secciones nuevas |

### Hilo del capítulo

```
Intro  qué contiene el capítulo y cómo se organiza
1.1    magnitud del problema → gravedad del melanoma → detección temprana → acceso e interpretación
       → documentación → dos tareas → métodos computacionales → dificultades de cada tarea
        ↓ consecuencia: quedan dos cuestiones abiertas
1.2    PI1 y PI2 → objetivo general → OE1–OE3 → tabla que los relaciona con los capítulos
        ↓ cierre
1.3    organización del resto del documento
```

### Orden de trabajo

1.1 → introducción del capítulo (va en el mismo commit que 1.1) → 1.2 → 1.3.

## Decisiones vigentes

Consolidadas el 10/10/2026 a partir de `historial.md`.

1. **Sin hipótesis.** El capítulo formula solo dos preguntas de investigación, PI1 y PI2, dentro de 1.2 y
   antes de los objetivos. La redacción vigente de las preguntas es la del `.tex` (revisión del autor,
   2026-10-04), que no usa términos que el capítulo no presentó.
2. **La introducción del capítulo** dice qué contiene y cómo se organiza, sin detalle técnico ni figuras.
   La antigua Figura 1.1 está en el Cap. 2 (generación de reportes).
3. **Nada de metodología.** No se nombran conjuntos de datos ni algoritmos, «detección» se usa en su
   sentido corriente, sin definición operativa, y el hardware entra en una sola oración. Los 12–36 GB de
   memoria de GPU, LoRA y los conjuntos de datos van al Cap. 3, y las limitaciones al Cap. 6.
4. **Cifras verificadas** que no se vuelven a verificar:
   - GLOBOCAN 2024 (`sung2026global`, publicado el 08/07/2026, que reemplazó a `bray2024global`): 58 398 muertes por melanoma y 58 721 por el resto de los cánceres de piel. El melanoma es menos de una cuarta parte de los casos, y el cáncer de piel no melanoma es el quinto tumor más frecuente (*fact sheet* de la IARC).
   - Supervivencia por estadio (`nci2026melanoma`).
   - Densidad de dermatólogos (`freeman2026global`).
   - Registro argentino (`loria2020cutaneous`).
   - Campaña de la SAD (`sad2023campana`).
   - Historia clínica electrónica (`arndt2017tethered`): son datos de atención primaria general, y el texto lo aclara.
   - Dermatoscopía (`dinnes2018dermoscopy`).
5. **Variabilidad entre observadores** sin una cifra de concordancia: solo que el desempeño depende de la
   formación y varía entre observadores (`tschandl2019comparison`). Las referencias anteriores a 2020 van
   fechadas, como punto de partida y no como el desempeño alcanzable hoy.
6. **OE3 sin «utilidad práctica»** (decisión del 28/09), porque no hubo evaluación con especialistas. El
   `.tex` todavía la menciona; se corrige en 1.2.
7. **Vocabulario.** «Acá» se reemplaza por «en este trabajo». «Preciso» queda reservado para *precision*.

## Claves de cita del capítulo

`sung2026global`, `ervik2026cancertoday`, `loria2020cutaneous`, `nci2026melanoma`, `freeman2026global`,
`sad2023campana`, `dinnes2018dermoscopy`, `tschandl2019comparison`, `arndt2017tethered`,
`esteva2017dermatologistlevel`, `radford2021learning`, `liu2023visual`, `li2023llavamed`,
`magalhaes2024systematic`, `kreouzi2024learning`, `jones2022intelligence`, `daneshjou2022disparities`,
`groh2021neural`, `riccilara2023dataset`, `bai2024hallucination`. Todas están en el `.bib`.
