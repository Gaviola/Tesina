"""
mendieta_download_models.py — Pre-descarga modelos de HuggingFace en el nodo de login.

Los nodos de computo de Mendieta NO tienen acceso a internet, asi que los modelos
deben estar en el cache de HuggingFace (~/.cache/huggingface/) ANTES de enviar jobs.

Este script se ejecuta localmente y corre la descarga via SSH en el login node.

Uso:
  python scripts/mendieta_download_models.py              # descarga todos
  python scripts/mendieta_download_models.py --model mini  # solo Mini-VLM
  python scripts/mendieta_download_models.py --model llava # solo LLaVA-Med
"""
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.mendieta_config import check_tools, ssh, unix_script, MENDIETA_USER, MENDIETA_HOST, SSH_OPTS

import subprocess

# Modelos a pre-descargar (repo_id, trust_remote_code)
MODELS = {
    "mini": {
        "repo_id": "microsoft/Phi-3.5-vision-instruct",
        "trust_remote_code": True,
    },
    "llava": {
        "repo_id": "chaoyinshe/llava-med-v1.5-mistral-7b-hf",
        "trust_remote_code": False,
    },
}

DOWNLOAD_SCRIPT_TEMPLATE = """
set -e
PYTHON="${{HOME}}/miniconda3/envs/dermvlm/bin/python"

if [ ! -f "${{PYTHON}}" ]; then
    echo "ERROR: entorno conda 'dermvlm' no encontrado."
    echo "Ejecutar primero: python scripts/mendieta_setup.py"
    exit 1
fi

echo "=== Pre-descargando modelos de HuggingFace ==="
echo "Cache: $(${{PYTHON}} -c 'from huggingface_hub import constants; print(constants.HF_HUB_CACHE)' 2>/dev/null || echo '~/.cache/huggingface/hub')"
echo ""

{download_commands}

echo ""
echo "=== Descarga completada ==="
"""

DOWNLOAD_ONE_MODEL = """
echo "--- Descargando {name} ({repo_id}) ---"
${{PYTHON}} -c "
from huggingface_hub import snapshot_download
print('Descargando {repo_id}...')
path = snapshot_download('{repo_id}')
print(f'OK: {{path}}')
"
echo ""
"""


def download_models(models: list[str]) -> int:
    """Ejecuta la descarga de modelos via SSH en el login node."""
    download_commands = ""
    for name in models:
        info = MODELS[name]
        download_commands += DOWNLOAD_ONE_MODEL.format(
            name=name,
            repo_id=info["repo_id"],
        )

    script = DOWNLOAD_SCRIPT_TEMPLATE.format(download_commands=download_commands)

    print(f"=== Descargando modelos en {MENDIETA_USER}@{MENDIETA_HOST} (login node) ===")
    print(f"Modelos: {', '.join(models)}")
    print()

    result = subprocess.run(
        ["ssh", *SSH_OPTS, f"{MENDIETA_USER}@{MENDIETA_HOST}", "bash", "-s"],
        input=script.replace("\r\n", "\n").encode("utf-8"),
    )
    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description="Pre-descarga modelos de HuggingFace en Mendieta (login node)"
    )
    parser.add_argument(
        "--model", choices=["mini", "llava", "all"], default="all",
        help="Modelo a descargar (default: all)",
    )
    args = parser.parse_args()

    check_tools()

    if args.model == "all":
        models = list(MODELS.keys())
    else:
        models = [args.model]

    rc = download_models(models)
    if rc != 0:
        print(f"\nERROR: descarga fallo (codigo {rc})")
        sys.exit(rc)


if __name__ == "__main__":
    main()
