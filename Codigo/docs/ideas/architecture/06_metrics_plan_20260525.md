# RFC 06 — Capa de evaluación unificada con puertos para NER y BERTScore

**Fecha:** 2026-05-25
**Estado:** Propuesta arquitectónica
**Alcance:** `Codigo/src/evaluation/`

## Problema

`src/evaluation/` mezcla cómputo puro (BLEU, ROUGE, METEOR, CIDEr, accuracy, F1) con dependencias externas pesadas (spaCy + ScispaCy NER ≈200 MB cada uno; BERTScore RoBERTa ≈1.3 GB) sin un seam claro. Síntomas concretos:

- **Modelos pesados se cargan en cada llamada**: `clinical_ner.py` y `generation.py` invocan `spacy.load(...)` y `BERTScorer(...)` por evaluación. En sweeps que evalúan N checkpoints, esto cuesta minutos extra por iteración.
- **Errores silenciados**: cada métrica está envuelta en `try/except` que loggea y retorna `None`/0. Un OOM de BERTScore o un modelo de spaCy faltante pasa inadvertido — el JSON de métricas final queda con métricas faltantes que el usuario no nota.
- **Diccionario de sinónimos hardcodeado**: `_DIAGNOSIS_SYNONYMS` y `DERMATOLOGY_TERMS` viven en código. Cualquier ajuste de terminología clínica requiere edit + commit.
- **No corre en CI**: cualquier import de `evaluation.clinical_ner` dispara `spacy.load` → CI tiene que descargar modelos o saltar todo el módulo.
- **Sin caché entre llamadas**: aún dentro de un mismo proceso, las cargas no se amortizan.

## Interfaz propuesta

**Puertos y adaptadores** (categoría 4 para NER + BERTScore; categoría 1 para BLEU/ROUGE/etc).

```python
# Codigo/src/evaluation/ports.py
from dataclasses import dataclass
from typing import Protocol, Sequence, runtime_checkable

@dataclass(frozen=True)
class Entity:
    text: str
    label: str            # "DISEASE", "ANATOMY", ...
    start: int
    end: int

@runtime_checkable
class NERPort(Protocol):
    def extract(self, text: str) -> Sequence[Entity]: ...
    def extract_batch(self, texts: Sequence[str]) -> Sequence[Sequence[Entity]]: ...

@runtime_checkable
class SemanticSimilarityPort(Protocol):
    def score(self, candidates: Sequence[str], references: Sequence[str]
              ) -> tuple[Sequence[float], Sequence[float], Sequence[float]]:
        """Devuelve (precision, recall, F1) por par."""
```

```python
# Codigo/src/evaluation/api.py
from typing import Literal, TypedDict, Sequence
from pathlib import Path

Task = Literal["report", "classification"]

class ReportMetrics(TypedDict, total=False):
    bleu4: float
    rouge_l: float
    bertscore_f1: float
    meteor: float
    cider: float
    ner_f1: float
    _meta: dict

class ClassificationMetrics(TypedDict, total=False):
    accuracy: float
    f1_macro: float
    auc_roc: float
    sensitivity: float
    specificity: float
    _meta: dict

def evaluate(
    predictions: str | Path | Sequence[dict],
    references: str | Path | Sequence[dict],
    *,
    task: Task,
    ner: NERPort | None = None,
    sim: SemanticSimilarityPort | None = None,
    strict: bool = False,
) -> ReportMetrics | ClassificationMetrics: ...
```

Las métricas puras (BLEU, ROUGE, METEOR, CIDEr, accuracy, F1, AUC) siempre corren. Las que dependen de NER/BERTScore se ejecutan **sólo si** se inyecta el puerto correspondiente. Si `task="report"` y `ner=None`, la métrica `ner_f1` simplemente no aparece (no se loggea como error — es una decisión explícita del caller).

### Ejemplo de uso

```python
# scripts/evaluate_reports.py
from src.evaluation.api import evaluate
from src.evaluation.adapters import ScispaCyNER, BERTScoreSimilarity

metrics = evaluate(
    predictions="outputs/generated_reports/mini_vlm/v2/ham10000/all.json",
    references="data/ham10000/references.json",
    task="report",
    ner=ScispaCyNER(synonyms_path="configs/derm_synonyms.yaml"),
    sim=BERTScoreSimilarity(device="cuda"),
)
```

```python
# scripts/evaluate_classify.py — no necesita NER ni BERTScore
metrics = evaluate(
    predictions="outputs/results/swin/v4/predictions.json",
    references="data/ham10000/labels.json",
    task="classification",
)
```

```python
# CI / smoke tests — sin descargas
from src.evaluation.adapters import FakeNER, FakeSimilarity
metrics = evaluate(preds, refs, task="report",
                   ner=FakeNER(fixtures={}), sim=FakeSimilarity(f1=0.8))
```

### Complejidad que oculta

- Carga única de modelos pesados (los adaptadores construyen el modelo en `__init__`, no por llamada).
- Diccionario de sinónimos cargado desde YAML configurable.
- Normalización del schema de predictions/references (acepta `{id: {pred, ref}}`, `[{id, pred, ref}]`, o dos listas paralelas).
- Routing por `task` a las métricas correspondientes.
- Política de errores: con `strict=False`, cada métrica fallida queda registrada en `metrics["_meta"]["errors"][nombre]`; con `strict=True` se relanza.

## Estrategia de dependencias

**Categoría 4 (Mock) para los puertos externos; 1 (in-process) para el resto.**

- **Puerto `NERPort`** + adaptadores:
  - `ScispaCyNER(model_name, synonyms_path)`: carga `spacy.load(...)` en `__init__`, usa `nlp.pipe` para batch.
  - `FakeNER(fixtures: dict[str, list[Entity]])`: lookup en dict para tests.
- **Puerto `SemanticSimilarityPort`** + adaptadores:
  - `BERTScoreSimilarity(model_type, device)`: construye `BERTScorer` una vez.
  - `FakeSimilarity(f1=0.85)`: retorna constante para tests.

Imports de `spacy` y `bert_score` quedan **adentro** de los adaptadores. El módulo `api.py` y las métricas puras no los importan, así que `evaluate(...)` con adaptadores fake corre en CI sin descargar modelos.

## Estrategia de testing

**Nuevos tests** (todos con `FakeNER` + `FakeSimilarity`, sin red):

- `evaluate(preds, refs, task="classification")` retorna `accuracy`, `f1_macro`, `auc_roc`, `sensitivity`, `specificity` con valores correctos sobre dataset sintético.
- `evaluate(preds, refs, task="report", ner=FakeNER({...}), sim=FakeSimilarity(0.9))` retorna `bleu4`, `rouge_l`, `bertscore_f1=0.9`, `meteor`, `cider`, `ner_f1` calculado sobre las entidades fixture.
- `evaluate(..., task="report")` sin `ner` ni `sim`: el resultado **no** contiene `bertscore_f1` ni `ner_f1` (no es error, es opt-out explícito).
- `evaluate(..., strict=True)` con un `FakeNER` que lanza `RuntimeError`: el error se propaga.
- `evaluate(..., strict=False)` con error: `metrics["_meta"]["errors"]["ner_f1"]` contiene la traza.
- Normalización de schema: las tres formas de entrada (dict-por-id, list de dicts, dos listas) producen el mismo resultado.
- `ScispaCyNER` con `synonyms_path` apuntando a un YAML personalizado canonicaliza correctamente (test de integración, gated por marker `requires_models`).

**Tests viejos a borrar:** ninguno.

**Necesidades de entorno:** sólo `pytest`. Los tests "requires_models" se ejecutan localmente, no en CI.

## Recomendaciones de implementación

Lo que `src/evaluation/` debe **poseer**:

- Métricas puras (BLEU, ROUGE, METEOR, CIDEr, accuracy, F1, AUC).
- Política de errores con `strict`.
- Routing por task.
- Normalización del schema de entrada.
- Carga del YAML de sinónimos clínicos.

Lo que debe **ocultar**:

- Detalles de spaCy, BERTScore.
- Caché de modelos cargados (vive en `__init__` del adaptador, no como singleton global).

Lo que debe **exponer**:

- `evaluate(preds, refs, *, task, ner=None, sim=None, strict=False)` como entry point.
- `NERPort`, `SemanticSimilarityPort` como contracts.
- `ScispaCyNER`, `BERTScoreSimilarity`, `FakeNER`, `FakeSimilarity` como adaptadores.

**Migración recomendada:**

1. Crear `src/evaluation/ports.py` y `adapters/`.
2. Mover `_DIAGNOSIS_SYNONYMS` y `DERMATOLOGY_TERMS` a `configs/derm_synonyms.yaml`.
3. Reimplementar `clinical_ner.py` como adaptador (`ScispaCyNER`); eliminar el `spacy.load` en imports.
4. Reimplementar `generation.py` con métricas puras + `bertscore_f1` opcional vía `sim` argumento.
5. Crear `src/evaluation/api.py` con `evaluate(...)`.
6. Migrar `evaluate_reports.py` y `evaluate_classify.py`.
7. Documentar el YAML de sinónimos en `docs/USAGE.md` y registrar su versión actual en el repo.

**Líneas estimadas ahorradas:** ≈60-80 netas, pero el beneficio principal es **eliminar errores silenciosos** y **habilitar CI sin GPU ni modelos descargados**.

## Sincronización con clústeres

Mueve `_DIAGNOSIS_SYNONYMS` a `configs/derm_synonyms.yaml` y agrega `src/evaluation/ports.py` + `adapters/`. Antes del primer `submit`:

1. `python scripts/mendieta/sync_up.py` y `python scripts/toko/sync_up.py` (el nuevo YAML viene incluido).
2. Las evaluaciones suelen correrse localmente, así que el riesgo de desincronización es bajo. Pero si algún script de cluster invoca `evaluate(...)` (por ejemplo, en un job de generación que también evalúa), confirmar que los adaptadores nuevos estén disponibles en el remoto.
3. Validación 100% local: re-correr `evaluate_reports.py` contra `predictions_v1.json` ya descargado y comparar con `metrics_v1.json`.
