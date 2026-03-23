"""
toko_sync_up.py — Sincroniza el codigo local hacia TOKO.
Excluye data/, outputs/, __pycache__, *.pyc, .git, etc.

Usa rsync si esta disponible (Git Bash / Linux / Mac).
En Windows nativo empaqueta con tarfile (stdlib) y transfiere via scp.

Uso:
  python scripts/toko_sync_up.py
  python scripts/toko_sync_up.py --install-deps   # tambien instala requirements.txt
"""
import sys
import io
import tarfile
import tempfile
import subprocess
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.toko_config import (
    TOKO_USER, TOKO_HOST, REMOTE_BASE, CODIGO_DIR, SSH_OPTS,
    check_tools, has_rsync, unix_script, ssh
)

# Directorios y archivos a incluir en la sincronizacion
INCLUDE_DIRS  = ["src", "scripts", "configs", "slurm", "notebooks"]
INCLUDE_FILES = ["requirements.txt", "setup_env.py"]

# Directorios a excluir solo en el nivel raiz (no dentro de src/)
EXCLUDE_ROOT_DIRS = {"data", "outputs"}
# Directorios a excluir a cualquier nivel de profundidad
EXCLUDE_ANY_DIRS = {"__pycache__", ".git", ".ipynb_checkpoints", "wandb"}
EXCLUDE_EXTS = {".pyc", ".pyo", ".env"}

# Patrones a excluir para rsync
RSYNC_EXCLUDES = [
    "--exclude=/data/",        # solo raiz (no src/data/)
    "--exclude=/outputs/",     # solo raiz
    "--exclude=__pycache__/",  # a cualquier nivel
    "--exclude=*.pyc",
    "--exclude=.git/",
    "--exclude=*.egg-info/",
    "--exclude=wandb/",
    "--exclude=.env",
    "--exclude=.ipynb_checkpoints/",
]

INSTALL_SCRIPT = """
set -e
# Usar ruta absoluta al entorno conda para evitar problemas en sesiones SSH no-interactivas
PIP="${HOME}/miniconda3/envs/dermvlm/bin/pip"
PYTHON="${HOME}/miniconda3/envs/dermvlm/bin/python"

if [ ! -f "${PIP}" ]; then
    echo "ERROR: entorno conda 'dermvlm' no encontrado en ${HOME}/miniconda3/envs/dermvlm"
    echo "Ejecutar primero: python scripts/toko_setup.py --skip-ssh-key"
    exit 1
fi

echo "Python: $(${PYTHON} --version)"
echo "Pip:    ${PIP}"
cd """ + REMOTE_BASE + """
echo "Limpiando bytecode corrupto de scipy..."
find ${HOME}/miniconda3/envs/dermvlm -name "__pycache__" -path "*/scipy/*" -exec rm -rf {} + 2>/dev/null
echo "Reinstalando scipy (fix UnicodeDecodeError en _tanhsinh.pyc)..."
${PIP} install --force-reinstall scipy --quiet
echo "Instalando requirements.txt..."
${PIP} install -r requirements.txt --quiet

# Reinstalar torch exacto despues de requirements.txt para evitar que
# dependencias transitorias (accelerate, evaluate, etc.) lo actualicen
echo "Fijando PyTorch cu126 (RTX 4080 Ada Lovelace)..."
${PIP} install torch torchvision \
    --index-url https://download.pytorch.org/whl/cu126 --quiet

echo "OK: dependencias instaladas"
${PYTHON} -c "
import torch, transformers, peft, datasets
print(f'  torch:        {torch.__version__}')
print(f'  transformers: {transformers.__version__}')
print(f'  peft:         {peft.__version__}')
print(f'  datasets:     {datasets.__version__}')
print('OK: imports verificados')
"
"""


# Extensiones de archivos de texto que necesitan conversion CRLF -> LF
TEXT_EXTS = {".sh", ".py", ".yaml", ".yml", ".txt", ".md", ".cfg", ".ini", ".json"}


def _exclude(tarinfo: tarfile.TarInfo) -> tarfile.TarInfo | None:
    """Filtro para tarfile: excluye __pycache__, .pyc, data/, outputs/, etc."""
    parts = Path(tarinfo.name).parts
    # Excluir data/ y outputs/ solo en el nivel raiz (no src/data/)
    if parts[0] in EXCLUDE_ROOT_DIRS:
        return None
    # Excluir __pycache__, .git, etc. a cualquier nivel
    if any(p in EXCLUDE_ANY_DIRS or p.endswith(".egg-info") for p in parts):
        return None
    if Path(tarinfo.name).suffix in EXCLUDE_EXTS:
        return None
    if Path(tarinfo.name).name == ".env":
        return None
    return tarinfo


def _add_text_lf(tar: tarfile.TarFile, local_path: Path, arcname: str) -> None:
    """Agrega un archivo de texto al tar con line endings LF (normaliza CRLF->LF).
    Necesario porque los archivos .sh creados en Windows tienen CRLF y
    SLURM (bash) rechaza scripts con \\r\\n.
    """
    content = local_path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    info = tarfile.TarInfo(name=arcname)
    info.size = len(content)
    # Preservar permisos ejecutables para .sh
    if local_path.suffix == ".sh":
        info.mode = 0o755
    else:
        info.mode = 0o644
    tar.addfile(info, io.BytesIO(content))


def sync_with_rsync() -> int:
    print("Usando rsync para sincronizacion incremental...")
    cmd = [
        "rsync", "-av", "--progress",
        "-e", f"ssh {' '.join(SSH_OPTS)}",
        *RSYNC_EXCLUDES,
        f"{CODIGO_DIR}/",
        f"{TOKO_USER}@{TOKO_HOST}:{REMOTE_BASE}/"
    ]
    return subprocess.run(cmd).returncode


def sync_with_tar() -> int:
    """
    Empaqueta los directorios/archivos relevantes en un tar.gz (excluyendo
    __pycache__, *.pyc, etc.) y lo transfiere via scp. Luego lo extrae en TOKO.
    """
    print("rsync no disponible. Empaquetando con tar y transfiriendo via scp...")

    with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as _f:
        tmp_tar = Path(_f.name)
    try:
        print("  Creando archivo tar (excluyendo __pycache__, *.pyc, etc.)...")
        with tarfile.open(tmp_tar, "w:gz") as tar:
            for d in INCLUDE_DIRS:
                local_dir = CODIGO_DIR / d
                if not local_dir.exists():
                    continue
                # Recorrer manualmente para aplicar filtro + conversion CRLF
                for file_path in sorted(local_dir.rglob("*")):
                    rel = file_path.relative_to(CODIGO_DIR)
                    arcname = rel.as_posix()
                    ti = _exclude(tarfile.TarInfo(name=arcname))
                    if ti is None:
                        continue
                    if file_path.is_dir():
                        ti.type = tarfile.DIRTYPE
                        ti.mode = 0o755
                        tar.addfile(ti)
                    elif file_path.suffix in TEXT_EXTS:
                        _add_text_lf(tar, file_path, arcname)
                    else:
                        tar.add(file_path, arcname=arcname)
                print(f"  + {d}/")
            for f in INCLUDE_FILES:
                local_path = CODIGO_DIR / f
                if not local_path.exists():
                    continue
                if local_path.suffix in TEXT_EXTS:
                    _add_text_lf(tar, local_path, f)
                else:
                    tar.add(local_path, arcname=f)
                print(f"  + {f}")

        size_mb = tmp_tar.stat().st_size / 1024 / 1024
        print(f"  Archivo: {tmp_tar} ({size_mb:.1f} MB)")
        print("  Subiendo a TOKO via scp...")

        remote_tar = f"{REMOTE_BASE}/_sync.tar.gz"
        result = subprocess.run([
            "scp", *SSH_OPTS,
            str(tmp_tar),
            f"{TOKO_USER}@{TOKO_HOST}:{remote_tar}"
        ])
        if result.returncode != 0:
            print("ERROR: fallo la transferencia scp")
            return result.returncode

        print("  Extrayendo en TOKO...")
        result = ssh(f"cd {REMOTE_BASE} && tar xzf _sync.tar.gz && rm _sync.tar.gz")
        if result.returncode != 0:
            print("ERROR: fallo la extraccion en TOKO")
            return result.returncode

        print("  OK: codigo extraido en TOKO")
        return 0

    finally:
        if tmp_tar.exists():
            tmp_tar.unlink()


def install_deps() -> int:
    print()
    print("--- Instalando dependencias en TOKO ---")
    result = subprocess.run(
        ["ssh", *SSH_OPTS, f"{TOKO_USER}@{TOKO_HOST}", "bash", "-s"],
        input=unix_script(INSTALL_SCRIPT),
    )
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Sincroniza codigo hacia TOKO")
    parser.add_argument("--install-deps", action="store_true",
                        help="Instalar requirements.txt en TOKO despues de sincronizar")
    args = parser.parse_args()

    check_tools()

    print(f"=== Sincronizando codigo hacia TOKO ===")
    print(f"Local:  {CODIGO_DIR}/")
    print(f"Remoto: {TOKO_USER}@{TOKO_HOST}:{REMOTE_BASE}/")
    print()

    if has_rsync():
        rc = sync_with_rsync()
    else:
        rc = sync_with_tar()

    if rc != 0:
        print(f"\nERROR: sincronizacion fallo (codigo {rc})")
        sys.exit(rc)

    print("\n=== Codigo sincronizado ===")

    if args.install_deps:
        rc = install_deps()
        if rc != 0:
            sys.exit(rc)
        print("=== Dependencias instaladas ===")
    else:
        print("Para instalar dependencias: python scripts/toko_sync_up.py --install-deps")


if __name__ == "__main__":
    main()
