"""
sync_data.py — Sube los datos necesarios hacia TOKO.

Por defecto sube MM-SkinQA (stage1) + HAM10000 (clasificacion y generacion reportes).
Con --all sube todos los datasets procesados.
Con --files sube archivos o directorios individuales (paths relativos a data/).

Si los datos no estan disponibles localmente, el script imprime
instrucciones para descargarlos directamente en el cluster.

Uso:
  python scripts/toko/sync_data.py           # MM-SkinQA + HAM10000
  python scripts/toko/sync_data.py --all     # todos los datasets
  python scripts/toko/sync_data.py --remote  # descarga en TOKO directamente
  python scripts/toko/sync_data.py --files processed/HAM10000/HAM10000_metadata
  python scripts/toko/sync_data.py --files splits/ham10000_splits.json processed/HAM10000/
"""
import sys
import subprocess
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.toko.config import (
    TOKO_USER, TOKO_HOST, REMOTE_BASE, LOCAL_DATA, SSH_OPTS,
    check_tools, has_rsync, unix_script
)

REMOTE_DATA = f"{REMOTE_BASE}/data"

DOWNLOAD_ON_TOKO_SCRIPT = f"""
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
        cmd = ["scp", *SSH_OPTS, "-O", "-r", str(local), remote_dest]
    return subprocess.run(cmd).returncode


def scp_file(local: Path, remote_dest: str) -> int:
    """Sube un archivo individual al cluster."""
    if has_rsync():
        cmd = ["rsync", "-av", "--progress", "-e", f"ssh {' '.join(SSH_OPTS)}",
               str(local), remote_dest]
    else:
        cmd = ["scp", *SSH_OPTS, str(local), remote_dest]
    return subprocess.run(cmd).returncode


def main():
    parser = argparse.ArgumentParser(description="Sube datasets a TOKO")
    parser.add_argument("--all", action="store_true",
                        help="Subir todos los datasets procesados")
    parser.add_argument("--remote", action="store_true",
                        help="Descargar MM-Skin directamente en TOKO (sin subir desde local)")
    parser.add_argument("--files", nargs="+", metavar="PATH",
                        help="Archivos o directorios individuales a subir (relativos a data/)")
    args = parser.parse_args()

    check_tools()

    # Opcion: subir archivos individuales
    if args.files:
        host = f"{TOKO_USER}@{TOKO_HOST}"
        errors = 0
        for rel_path in args.files:
            local = LOCAL_DATA / rel_path
            if not local.exists():
                print(f"ERROR: No se encontro {local}")
                errors += 1
                continue
            remote_dest = f"{host}:{REMOTE_DATA}/{rel_path}"
            if local.is_dir():
                print(f"Subiendo {rel_path}/ ...")
                # Crear directorio PADRE (no el destino): scp -r crea el directorio
                # destino por sí mismo; si ya existe, anida la carpeta dentro.
                remote_dest_dir = f"{REMOTE_DATA}/{rel_path}"
                remote_parent_dir = f"{REMOTE_DATA}/{Path(rel_path).parent}"
                subprocess.run(["ssh", *SSH_OPTS, host, "mkdir", "-p", remote_parent_dir])
                rc = scp_dir(local, f"{host}:{remote_dest_dir}")
            else:
                print(f"Subiendo {rel_path} ...")
                remote_parent = f"{REMOTE_DATA}/{Path(rel_path).parent}"
                subprocess.run(["ssh", *SSH_OPTS, host, "mkdir", "-p", remote_parent])
                rc = scp_file(local, remote_dest)
            errors += rc
        sys.exit(1 if errors else 0)

    # Opcion: descargar directamente en el cluster
    if args.remote:
        print("=== Descargando MM-Skin directamente en TOKO ===")
        result = subprocess.run(
            ["ssh", *SSH_OPTS, f"{TOKO_USER}@{TOKO_HOST}", "bash", "-s"],
            input=unix_script(DOWNLOAD_ON_TOKO_SCRIPT),
        )
        sys.exit(result.returncode)

    # Verificar que existan datos locales
    if not LOCAL_DATA.exists():
        print(f"ERROR: No se encontro el directorio de datos local: {LOCAL_DATA}")
        print()
        print("Opciones:")
        print("  1. Descargar en TOKO directamente:")
        print("     python scripts/toko/sync_data.py --remote")
        print()
        print("  2. Preparar datos localmente primero:")
        print("     python scripts/prepare_data.py --dataset mmskin")
        print("     python scripts/toko/sync_data.py")
        sys.exit(1)

    print(f"=== Subiendo datos hacia TOKO ===")
    print(f"Local:  {LOCAL_DATA}/")
    print(f"Remoto: {TOKO_USER}@{TOKO_HOST}:{REMOTE_DATA}/")
    print()

    errors = 0

    if args.all:
        # Subir todos los datasets procesados
        processed_dir = LOCAL_DATA / "processed"
        if processed_dir.exists():
            print("Subiendo data/processed/ completo...")
            rc = scp_dir(processed_dir, f"{TOKO_USER}@{TOKO_HOST}:{REMOTE_DATA}/processed")
            errors += rc
        splits_dir = LOCAL_DATA / "splits"
        if splits_dir.exists():
            print("Subiendo data/splits/...")
            rc = scp_dir(splits_dir, f"{TOKO_USER}@{TOKO_HOST}:{REMOTE_DATA}/splits")
            errors += rc
    else:
        # MM-SkinQA + HAM10000 (necesarios para stage1, clasificacion y generacion)
        mmskin_dir = LOCAL_DATA / "processed" / "MM-SkinQA"
        if not mmskin_dir.exists():
            print(f"ERROR: No se encontro {mmskin_dir}")
            print("Ejecutar primero: python scripts/prepare_data.py --dataset mmskin")
            print("O descargar en TOKO: python scripts/toko/sync_data.py --remote")
            sys.exit(1)

        print("Subiendo data/processed/MM-SkinQA/ (necesario para stage1)...")
        rc = scp_dir(mmskin_dir,
                     f"{TOKO_USER}@{TOKO_HOST}:{REMOTE_DATA}/processed/MM-SkinQA")
        errors += rc

        # HAM10000 processed (clasificacion + generacion reportes)
        ham_processed = LOCAL_DATA / "processed" / "HAM10000"
        if ham_processed.exists():
            print("Subiendo data/processed/HAM10000/ (clasificacion + generacion reportes)...")
            rc = scp_dir(ham_processed,
                         f"{TOKO_USER}@{TOKO_HOST}:{REMOTE_DATA}/processed/HAM10000")
            errors += rc
        else:
            print(f"AVISO: No se encontro {ham_processed} (necesario para clasificacion y generacion)")

        # Subir splits si existen
        splits_dir = LOCAL_DATA / "splits"
        if splits_dir.exists():
            print("Subiendo data/splits/...")
            rc = scp_dir(splits_dir, f"{TOKO_USER}@{TOKO_HOST}:{REMOTE_DATA}/splits")
            errors += rc

    if errors:
        print(f"\nERROR: algunos archivos no se pudieron subir")
        sys.exit(1)

    print("\n=== Datos sincronizados ===")


if __name__ == "__main__":
    main()
