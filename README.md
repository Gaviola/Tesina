# Detección, diagnóstico y generación automática de reportes para lesiones de piel utilizando modelos de lenguajes de visión

Tesina de grado de Facundo Gaviola. El trabajo compara clasificadores supervisados, modelos visión–lenguaje
generativos y un modelo visión–lenguaje especializado en dermatología sobre *HAM10000*, y propone un *pipeline* que
encadena un clasificador, la recuperación de casos parecidos y un generador para escribir el reporte clínico de una
lesión, en una sola GPU de consumo.

## Contenido

| Carpeta | Qué contiene |
|---|---|
| [`Docs/TFG/`](Docs/TFG/) | La tesina: fuentes LaTeX (`tesina.tex`, `Chapters/`, `Figures/`) y el PDF compilado, [`tesina.pdf`](Docs/TFG/tesina.pdf) |
| [`Codigo/src/`](Codigo/src/) | Paquete Python: carga de datos, modelos, entrenamiento y métricas |
| [`Codigo/scripts/`](Codigo/scripts/) | Scripts de cada etapa: entrenamiento, evaluación, generación de reportes y figuras |
| [`Codigo/configs/`](Codigo/configs/) | Hiperparámetros (YAML) |
| [`Codigo/slurm/`](Codigo/slurm/) | Trabajos enviados a los clústeres TOKO y Mendieta |

Los conjuntos de datos, los pesos y los resultados no se incluyen en el repositorio.

## Reproducir los experimentos

La guía de uso, [`Codigo/docs/USAGE.md`](Codigo/docs/USAGE.md), detalla la instalación, la descarga de los datos y
los comandos de cada etapa. El Apéndice B de la tesina relaciona cada etapa con sus scripts.

## Compilar la tesina

Desde `Docs/TFG/`, con XeLaTeX, Biber y `minted`:

```bash
latexmk -xelatex -shell-escape tesina.tex
```
