"""Métricas de generación de texto para Fase 2, Nivel 1.

Métricas automáticas con referencia: BLEU-4, ROUGE-L, BERTScore F1, METEOR, CIDEr.
Cada métrica falla de forma independiente (try/except) para que las demás sigan funcionando.
"""

import logging
import math
from collections import Counter
from typing import Optional

logger = logging.getLogger(__name__)

_DEFAULT_METRICS = ["bleu_4", "rouge_l", "bertscore_f1", "meteor", "cider"]


# ---------------------------------------------------------------------------
# Métricas individuales
# ---------------------------------------------------------------------------

def _compute_bleu(predictions: list[str], references: list[str]) -> Optional[float]:
    try:
        import evaluate
        bleu = evaluate.load("bleu")
        result = bleu.compute(
            predictions=predictions,
            references=[[r] for r in references],
            max_order=4,
        )
        return float(result["bleu"])
    except Exception as e:
        logger.warning("BLEU-4 no disponible: %s", e)
        return None


def _compute_rouge_l(predictions: list[str], references: list[str]) -> Optional[float]:
    try:
        import evaluate
        rouge = evaluate.load("rouge")
        result = rouge.compute(predictions=predictions, references=references)
        return float(result["rougeL"])
    except Exception as e:
        logger.warning("ROUGE-L no disponible: %s", e)
        return None


def _compute_bertscore(predictions: list[str], references: list[str]) -> Optional[float]:
    # distilbert-base-uncased primero: ligero y compatible con transformers>=5.x
    # deberta-xlarge-mnli falla con "int too big to convert" en transformers>=5.0
    for model_type in ("distilbert-base-uncased", "microsoft/deberta-xlarge-mnli"):
        try:
            import evaluate
            bertscore = evaluate.load("bertscore")
            result = bertscore.compute(
                predictions=predictions,
                references=references,
                model_type=model_type,
                lang="en",
                batch_size=32,
            )
            return float(sum(result["f1"]) / len(result["f1"]))
        except Exception as e:
            logger.warning("BERTScore con %s no disponible: %s", model_type, e)
    return None


def _compute_meteor(predictions: list[str], references: list[str]) -> Optional[float]:
    try:
        import evaluate
        meteor = evaluate.load("meteor")
        result = meteor.compute(predictions=predictions, references=references)
        return float(result["meteor"])
    except Exception as e:
        logger.warning("METEOR no disponible: %s", e)
        return None


# --- CIDEr (implementación propia basada en TF-IDF de n-gramas) ---

def _get_ngrams(tokens: list[str], n: int) -> Counter:
    return Counter(tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1))


def _cider_score_pair(
    pred_tokens: list[str],
    ref_tokens: list[str],
    corpus_df: dict,
    n_docs: int,
    max_n: int = 4,
) -> float:
    """CIDEr para un par predicción-referencia usando TF-IDF sobre n-gramas 1..max_n."""
    score = 0.0
    for n in range(1, max_n + 1):
        pred_ngrams = _get_ngrams(pred_tokens, n)
        ref_ngrams = _get_ngrams(ref_tokens, n)

        if not pred_ngrams or not ref_ngrams:
            continue

        # TF normalizado
        pred_norm = sum(pred_ngrams.values())
        ref_norm = sum(ref_ngrams.values())

        numerator = 0.0
        pred_mag = 0.0
        ref_mag = 0.0

        all_ngrams = set(pred_ngrams) | set(ref_ngrams)
        for ng in all_ngrams:
            df = corpus_df.get(ng, 1)
            idf = math.log(max(n_docs / df, 1.0) + 1.0)

            pred_tf = pred_ngrams.get(ng, 0) / max(pred_norm, 1)
            ref_tf = ref_ngrams.get(ng, 0) / max(ref_norm, 1)

            pred_w = pred_tf * idf
            ref_w = ref_tf * idf

            numerator += pred_w * ref_w
            pred_mag += pred_w ** 2
            ref_mag += ref_w ** 2

        denom = math.sqrt(pred_mag) * math.sqrt(ref_mag)
        if denom > 0:
            score += numerator / denom

    return score / max(max_n, 1)


def _compute_cider(predictions: list[str], references: list[str]) -> Optional[float]:
    # Intentar pycocoevalcap primero
    try:
        from pycocoevalcap.cider.cider import Cider
        gts = {i: [r] for i, r in enumerate(references)}
        res = {i: [p] for i, p in enumerate(predictions)}
        scorer = Cider()
        score, _ = scorer.compute_score(gts, res)
        return float(score)
    except ImportError:
        pass
    except Exception as e:
        logger.warning("pycocoevalcap CIDEr falló: %s. Usando implementación propia.", e)

    # Fallback: implementación TF-IDF propia
    try:
        all_tokens = [text.lower().split() for text in predictions + references]
        n_docs = len(all_tokens)
        corpus_df: dict = Counter()
        for tokens in all_tokens:
            for n in range(1, 5):
                for ng in set(_get_ngrams(tokens, n)):
                    corpus_df[ng] += 1

        scores = []
        for pred, ref in zip(predictions, references):
            pred_tokens = pred.lower().split()
            ref_tokens = ref.lower().split()
            scores.append(_cider_score_pair(pred_tokens, ref_tokens, corpus_df, n_docs))

        return float(sum(scores) / max(len(scores), 1))
    except Exception as e:
        logger.warning("CIDEr (implementación propia) falló: %s", e)
        return None


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

def evaluate_generation(
    predictions: list[str],
    references: list[str],
    metrics: Optional[list[str]] = None,
) -> dict:
    """Calcula métricas de generación de texto automáticas con referencia.

    Args:
        predictions: Textos generados por el modelo.
        references: Textos de referencia (ground truth).
        metrics: Lista de métricas a calcular. Default: todas.
            Opciones: "bleu_4", "rouge_l", "bertscore_f1", "meteor", "cider".

    Returns:
        Dict con cada métrica calculada. Las métricas no disponibles no aparecen.

    Raises:
        ValueError: Si predictions y references tienen distinto tamaño o están vacíos.
    """
    if metrics is None:
        metrics = _DEFAULT_METRICS

    if len(predictions) != len(references):
        raise ValueError(
            f"predictions ({len(predictions)}) y references ({len(references)}) "
            "deben tener el mismo tamaño."
        )
    if len(predictions) == 0:
        raise ValueError("La lista de predicciones está vacía.")

    results = {}

    _compute_fns = {
        "bleu_4": _compute_bleu,
        "rouge_l": _compute_rouge_l,
        "bertscore_f1": _compute_bertscore,
        "meteor": _compute_meteor,
        "cider": _compute_cider,
    }

    for metric_name in metrics:
        fn = _compute_fns.get(metric_name)
        if fn is None:
            logger.warning("Métrica desconocida: %s", metric_name)
            continue
        value = fn(predictions, references)
        if value is not None:
            results[metric_name] = value
            logger.info("%-14s: %.4f", metric_name, value)

    return results
