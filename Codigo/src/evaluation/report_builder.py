"""Generador de tablas comparativas de resultados.

Consolida métricas de diferentes modelos y fases en tablas formateadas.
Se implementa completo en Fase 3.
"""

import pandas as pd


def build_comparison_table(
    results: dict[str, dict],
    metrics: list[str],
    output_path: str | None = None,
) -> pd.DataFrame:
    """Genera tabla comparativa modelo × métricas.

    Args:
        results: Dict {nombre_modelo: {metrica: valor}}.
        metrics: Lista de métricas a incluir.
        output_path: Si se pasa, guarda como CSV.

    Returns:
        DataFrame con la tabla comparativa.
    """
    rows = []
    for model_name, model_metrics in results.items():
        row = {"model": model_name}
        for metric in metrics:
            row[metric] = model_metrics.get(metric, None)
        rows.append(row)

    df = pd.DataFrame(rows)

    if output_path:
        df.to_csv(output_path, index=False)

    return df
