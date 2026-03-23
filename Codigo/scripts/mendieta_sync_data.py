"""
mendieta_sync_data.py — Sube los datos procesados necesarios para stage1 hacia Mendieta.

Por defecto sube solo MM-SkinQA (requerido por train_vlm_stage1.py).
Con --all sube todos los datasets procesados.

Si los datos no estan disponibles localmente, el script imprime
instrucciones para descargarlos directamente en el cluster.

Uso:
  python scripts/mendieta_sync_data.py           # solo MM-SkinQA
  python scripts/mendieta_sync_data.py --all     # todos los datasets
  python scripts/mendieta_sync_data.py --remote  # descarga en Mendieta directamente
"""
import sys
import subprocess
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.mendieta_config import (
    MENDIETA_USER, MENDIETA_HOST, REMOTE_BASE, LOCAL_DATA, SSH_OPTS,
    check_tools, has_rsync, unix_script
)

REMOTE_DATA = f"{REMOTE_BASE}/data"

DOWNLOAD_ON_MENDIETA_SCRIPT = f"""
set -e
cd {REMOTE_BASE}
echo "--- Clonando MM-Skin desde GitHub ---"
if [ -d "data/raw/MM-SkinQA" ]; then
    echo "OK: MM-SkinQA ya existe, actualizando..."
    cd data/raw/MM-SkinQA && git pull && cd {REMOTE_BASE}
else
    mkdir -p data/raw
    git clone https://github.com/ZwQ803/MM-Skin data/raw/MM-SkinQA
    echo "OK: MM-Skin clonado"
fi

echo ""
echo "--- Preprocesando MM-Skin ---"
source "${{HOME}}/miniconda3/etc/profile.d/conda.sh" 2>/dev/null || true
source activate dermvlm 2>/dev/null || true
python scripts/prepare_data.py --dataset mmskin
echo "OK: datos procesados"
"""


def scp_dir(local: Path, remote_dest: str) -> int:
    if has_rsync():
        cmd = ["rsync", "-av", "--progress", "-e", f"ssh {' '.join(SSH_OPTS)}",
               f"{local}/", f"{remote_dest}/"]
    else:
        cmd = ["scp", *SSH_OPTS, "-r", str(local), remote_dest]
    return subprocess.run(cmd).returncode


def main():
    parser = argparse.ArgumentParser(description="Sube datasets a Mendieta")
    parser.add_argument("--all", action="store_true",
                        help="Subir todos los datasets procesados")
    parser.add_argument("--remote", action="store_true",
                        help="Descargar MM-Skin directamente en Mendieta (sin subir desde local)")
    args = parser.parse_args()

    check_tools()

    # Opcion: descargar directamente en el cluster
    if args.remote:
        print("=== Descargando MM-Skin directamente en Mendieta ===")
        result = subprocess.run(
            ["ssh", *SSH_OPTS, f"{MENDIETA_USER}@{MENDIETA_HOST}", "bash", "-s"],
            input=unix_script(DOWNLOAD_ON_MENDIETA_SCRIPT),
        )
        sys.exit(result.returncode)

    # Verificar que existan datos locales
    if not LOCAL_DATA.exists():
        print(f"ERROR: No se encontro el directorio de datos local: {LOCAL_DATA}")
        print()
        print("Opciones:")
        print("  1. Descargar en Mendieta directamente:")
        print("     python scripts/mendieta_sync_data.py --remote")
        print()
        print("  2. Preparar datos localmente primero:")
        print("     python scripts/prepare_data.py --dataset mmskin")
        print("     python scripts/mendieta_sync_data.py")
        sys.exit(1)

    print(f"=== Subiendo datos hacia Mendieta ===")
    print(f"Local:  {LOCAL_DATA}/")
    print(f"Remoto: {MENDIETA_USER}@{MENDIETA_HOST}:{REMOTE_DATA}/")
    print()

    errors = 0

    if args.all:
        # Subir todos los datasets procesados
        processed_dir = LOCAL_DATA / "processed"
        if processed_dir.exists():
            print("Subiendo data/processed/ completo...")
            rc = scp_dir(processed_dir, f"{MENDIETA_USER}@{MENDIETA_HOST}:{REMOTE_DATA}/processed")
            errors += rc
        splits_dir = LOCAL_DATA / "splits"
        if splits_dir.exists():
            print("Subiendo data/splits/...")
            rc = scp_dir(splits_dir, f"{MENDIETA_USER}@{MENDIETA_HOST}:{REMOTE_DATA}/splits")
            errors += rc
    else:
        # Solo MM-SkinQA
        mmskin_dir = LOCAL_DATA / "processed" / "MM-SkinQA"
        if not mmskin_dir.exists():
            print(f"ERROR: No se encontro {mmskin_dir}")
            print("Ejecutar primero: python scripts/prepare_data.py --dataset mmskin")
            print("O descargar en Mendieta: python scripts/mendieta_sync_data.py --remote")
            sys.exit(1)

        print("Subiendo data/processed/MM-SkinQA/ (necesario para stage1)...")
        rc = scp_dir(mmskin_dir,
                     f"{MENDIETA_USER}@{MENDIETA_HOST}:{REMOTE_DATA}/processed/MM-SkinQA")
        errors += rc

        # Subir splits si existen
        splits_dir = LOCAL_DATA / "splits"
        if splits_dir.exists():
            print("Subiendo data/splits/...")
            rc = scp_dir(splits_dir, f"{MENDIETA_USER}@{MENDIETA_HOST}:{REMOTE_DATA}/splits")
            errors += rc

    if errors:
        print(f"\nERROR: algunos archivos no se pudieron subir")
        sys.exit(1)

    print("\n=== Datos sincronizados ===")


if __name__ == "__main__":
    main()
