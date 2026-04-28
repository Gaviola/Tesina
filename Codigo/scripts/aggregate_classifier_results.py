"""Agrega resultados de clasificadores Fase 1 en tabla resumen.

Recorre ``outputs/results/*_test_results.json`` (HAM10000) y
``outputs/results/*_test_results_hiba.json`` (HIBA OOD), extrae métricas
clave y emite:

  * Tabla Markdown a stdout (lectura humana).
  * Filas LaTeX listas para pegar en
    ``Codigo/docs/resul/tablas_estado_del_arte_v2.tex`` (filas
    "este trabajo": (a), (b), (a$'$), (b$'$)).

Uso::

    python scripts/aggregate_classifier_results.py
    python scripts/aggregate_classifier_results.py --results-dir outputs/results
    python scripts/aggregate_classifier_results.py --tex-only > rows.tex
"""

import argparse
import json
import sys
from pathlib import Path

# Mapeo run_name → fila tabla SOTA. Ajustar tras decisiones de Fase 4-5.
ROW_LABELS = {
    "densenet_modern":      "(a)",
    "densenet_legacy":      "(a) [legacy]",
    "vit_modern":           "(b)",
    "vit_legacy":           "(b) [legacy]",
    "convnext_tiny_modern": "(a$')",
    "swin_tiny_modern":     "(b$')",
}

ARCH_NAME = {
    "densenet":      "DenseNet121",
    "vit":           "ViT-B/16",
    "convnext_tiny": "ConvNeXt-Tiny",
    "swin_tiny":     "Swin-Tiny",
}


def fmt_pct(x):
    return "—" if x is None else f"{100 * x:.2f}"


def fmt_num(x, digits=4):
    return "—" if x is None else f"{x:.{digits}f}"


def load_results(results_dir: Path) -> list[dict]:
    """Carga todos los _test_results.json y _test_results_hiba.json del dir."""
    out = []
    for path in sorted(results_dir.glob("*_test_results.json")):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        run_name = data.get("run_name") or data.get("model") or path.stem.replace("_test_results", "")
        # Buscar el correspondiente HIBA si existe
        hiba_path = results_dir / f"{run_name}_test_results_hiba.json"
        hiba = None
        if hiba_path.exists():
            with open(hiba_path, encoding="utf-8") as f:
                hiba = json.load(f)
        out.append({
            "run_name":    run_name,
            "model":       data.get("model", run_name),
            "recipe":      data.get("recipe"),
            "ham":         data,
            "hiba":        hiba,
            "path":        path,
        })
    return out


def emit_markdown(rows: list[dict]) -> str:
    lines = [
        "| Run | Modelo | Recipe | Acc HAM | F1 HAM | AUC HAM | Acc HIBA | F1 HIBA |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        ham = r["ham"]
        hiba = r["hiba"]
        lines.append(
            f"| {r['run_name']} | {ARCH_NAME.get(r['model'], r['model'])} | "
            f"{r.get('recipe') or '—'} | "
            f"{fmt_pct(ham.get('accuracy'))} | "
            f"{fmt_num(ham.get('f1_weighted'))} | "
            f"{fmt_num(ham.get('auc_roc_macro'))} | "
            f"{fmt_pct(hiba.get('accuracy')) if hiba else '—'} | "
            f"{fmt_num(hiba.get('f1_weighted')) if hiba else '—'} |"
        )
    return "\n".join(lines)


def emit_latex_rows(rows: list[dict]) -> str:
    """Emite las filas LaTeX para reemplazar en tablas_estado_del_arte_v2.tex.

    Sólo emite filas cuyo run_name aparece en ROW_LABELS.
    """
    out = []
    for r in rows:
        label = ROW_LABELS.get(r["run_name"])
        if label is None:
            continue
        ham = r["ham"]
        arch = ARCH_NAME.get(r["model"], r["model"])
        out.append(r"\rowcolor{thiswork}")
        out.append(
            f"{label} & {arch}\n"
            f"  & HAM10000$^{{(\\zeta)}}$\n"
            f"  & FT & 7\n"
            f"  & {fmt_pct(ham.get('accuracy'))} "
            f"& {fmt_num(ham.get('auc_roc_macro'), 3)} "
            f"& {fmt_num(ham.get('f1_weighted'), 3)} "
            f"& {fmt_num(ham.get('sensitivity_macro'), 3)} "
            f"& {fmt_num(ham.get('specificity_macro'), 3)} \\\\"
        )
        out.append("")
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description="Agrega resultados clasificadores Fase 1")
    parser.add_argument("--results-dir", type=str, default="outputs/results")
    parser.add_argument("--tex-only", action="store_true",
                        help="Emitir solo las filas LaTeX (para pipe a archivo).")
    parser.add_argument("--md-only", action="store_true",
                        help="Emitir solo la tabla Markdown.")
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    if not results_dir.exists():
        print(f"ERROR: {results_dir} no existe", file=sys.stderr)
        sys.exit(1)

    rows = load_results(results_dir)
    if not rows:
        print(f"ADVERTENCIA: ningún _test_results.json encontrado en {results_dir}",
              file=sys.stderr)
        sys.exit(0)

    if args.tex_only:
        print(emit_latex_rows(rows))
    elif args.md_only:
        print(emit_markdown(rows))
    else:
        print("# Resumen de resultados clasificadores Fase 1")
        print()
        print(f"Fuente: `{results_dir}` ({len(rows)} runs encontrados)")
        print()
        print("## Tabla Markdown")
        print()
        print(emit_markdown(rows))
        print()
        print("## Filas LaTeX (pegar en tablas_estado_del_arte_v2.tex)")
        print()
        print(emit_latex_rows(rows))


if __name__ == "__main__":
    main()
