"""
setup.py — Configuracion inicial del entorno en TOKO (ejecutar una sola vez).

Pasos:
  1. Configura clave SSH para evitar ingresar contrasena cada vez
  2. Crea directorios necesarios en el cluster
  3. Verifica/instala Miniconda en TOKO
  4. Crea entorno conda 'dermvlm' con Python 3.10
  5. Instala PyTorch para Ada Lovelace (CUDA 12.6)
  6. Verifica GPU y CUDA

Uso:
  python scripts/toko/setup.py
  python scripts/toko/setup.py --skip-ssh-key   # si ya configuraste la clave SSH
"""
import sys
import subprocess
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.toko.config import TOKO_USER, TOKO_HOST, REMOTE_BASE, SSH_OPTS, check_tools, ssh, unix_script


SETUP_SCRIPT = r"""
set -e

echo "--- [1/5] Creando directorios ---"
mkdir -p "${HOME}/scratch/dermvlm/logs/mini_vlm"
mkdir -p "${HOME}/scratch/dermvlm/logs/llava_med"
mkdir -p "${HOME}/scratch/dermvlm/logs/shared"
mkdir -p "${HOME}/scratch/dermvlm/data/processed"
mkdir -p "${HOME}/scratch/dermvlm/outputs/checkpoints"
mkdir -p "${HOME}/scratch/dermvlm/outputs/results/mini_vlm"
mkdir -p "${HOME}/scratch/dermvlm/outputs/results/llava_med"
mkdir -p "${HOME}/scratch/dermvlm/outputs/results/shared"
mkdir -p "${HOME}/scratch/dermvlm/outputs/generated_reports"
echo "OK: directorios creados"

echo ""
echo "--- [2/5] Verificando GPU ---"
nvidia-smi 2>/dev/null && echo "OK: GPU detectada" || echo "ADVERTENCIA: nvidia-smi no disponible"

echo ""
echo "--- [3/5] Verificando Miniconda ---"
if ! command -v conda &>/dev/null; then
    if [ -f "${HOME}/miniconda3/bin/conda" ]; then
        export PATH="${HOME}/miniconda3/bin:${PATH}"
    else
        echo "Instalando Miniconda3..."
        wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh
        bash /tmp/miniconda.sh -b -p "${HOME}/miniconda3"
        rm /tmp/miniconda.sh
        export PATH="${HOME}/miniconda3/bin:${PATH}"
        conda init bash
        echo "OK: Miniconda instalado"
    fi
else
    echo "OK: $(conda --version)"
fi

CONDA_BIN="${HOME}/miniconda3/bin"
[ -d "${CONDA_BIN}" ] && export PATH="${CONDA_BIN}:${PATH}"

echo ""
echo "--- [4/5] Creando entorno dermvlm ---"
source "${HOME}/miniconda3/etc/profile.d/conda.sh" 2>/dev/null || true

echo "Aceptando Terminos de Servicio de los canales de conda..."
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main 2>/dev/null || true
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r 2>/dev/null || true

if conda env list 2>/dev/null | grep -q "dermvlm"; then
    echo "OK: entorno 'dermvlm' ya existe"
else
    conda create -n dermvlm python=3.10 -y
    echo "OK: entorno creado"
fi

# Usar ruta absoluta al entorno para evitar problemas con conda activate en SSH
PIP="${HOME}/miniconda3/envs/dermvlm/bin/pip"
PYTHON="${HOME}/miniconda3/envs/dermvlm/bin/python"

echo ""
echo "--- [5/5] Instalando PyTorch (cu126, RTX 4080 Ada Lovelace) ---"
# Fijar numpy<2: PyTorch 2.1.x fue compilado con NumPy 1.x y falla con NumPy 2.x
${PIP} install "numpy<2" --quiet
if ${PYTHON} -c "import torch" 2>/dev/null; then
    echo "OK: PyTorch ya instalado ($(${PYTHON} -c 'import torch; print(torch.__version__)'))"
else
    ${PIP} install torch torchvision \
        --index-url https://download.pytorch.org/whl/cu126 --quiet
    echo "OK: PyTorch instalado"
fi

echo ""
echo "--- Verificacion final ---"
${PYTHON} -c "
import torch
print(f'  Python:           {__import__(\"sys\").version.split()[0]}')
print(f'  PyTorch:          {torch.__version__}')
print(f'  CUDA disponible:  {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'  GPU:              {torch.cuda.get_device_name(0)}')
    vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
    cap  = torch.cuda.get_device_capability(0)
    print(f'  VRAM:             {vram:.1f} GB')
    print(f'  Compute cap:      {cap[0]}.{cap[1]}')
"
echo ""
echo "=== Setup completado. Proximo paso: python scripts/toko/sync_up.py ==="
"""


def setup_ssh_key():
    """Copia la clave SSH publica a TOKO para evitar ingresar contrasena."""
    ssh_dir = Path.home() / ".ssh"
    pub_key = ssh_dir / "id_rsa.pub"

    if not pub_key.exists():
        print("Generando par de claves SSH...")
        subprocess.run(["ssh-keygen", "-t", "rsa", "-b", "4096", "-N", "", "-f", str(ssh_dir / "id_rsa")], check=True)
        print("OK: clave generada")

    print(f"Copiando clave publica a {TOKO_USER}@{TOKO_HOST}...")
    print("(Se pedira la contrasena del cluster una ultima vez)")
    pub_key_content = pub_key.read_text().strip()

    # En Windows no hay ssh-copy-id; lo hacemos manualmente via SSH
    cmd = (
        f'mkdir -p ~/.ssh && chmod 700 ~/.ssh && '
        f'echo "{pub_key_content}" >> ~/.ssh/authorized_keys && '
        f'chmod 600 ~/.ssh/authorized_keys && '
        f'echo "OK: clave SSH configurada"'
    )
    result = subprocess.run(["ssh", *SSH_OPTS, f"{TOKO_USER}@{TOKO_HOST}", cmd])
    if result.returncode == 0:
        print("OK: SSH key configurada. Las proximas conexiones no pediran contrasena.")
    else:
        print("ADVERTENCIA: no se pudo configurar SSH key automaticamente.")
        print(f"Puedes hacerlo manualmente copiando el contenido de {pub_key}")


def main():
    parser = argparse.ArgumentParser(description="Configura el entorno en TOKO")
    parser.add_argument("--skip-ssh-key", action="store_true",
                        help="Omitir configuracion de clave SSH")
    args = parser.parse_args()

    check_tools()

    print(f"=== Configurando entorno en TOKO ===")
    print(f"Host: {TOKO_USER}@{TOKO_HOST}")
    print(f"Dir remoto: {REMOTE_BASE}")
    print()

    if not args.skip_ssh_key:
        print("--- Configurando clave SSH ---")
        setup_ssh_key()
        print()

    print("--- Ejecutando setup remoto (puede tardar varios minutos) ---")
    result = subprocess.run(
        ["ssh", *SSH_OPTS, f"{TOKO_USER}@{TOKO_HOST}", "bash", "-s"],
        input=unix_script(SETUP_SCRIPT),
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
