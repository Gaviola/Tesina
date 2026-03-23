"""
mendieta_setup.py — Configuracion inicial del entorno en Mendieta (ejecutar una sola vez).

Pasos:
  1. (Opcional) Configura clave SSH
  2. Crea directorios necesarios en el cluster
  3. Muestra particiones disponibles (sinfo)
  4. Verifica/instala Miniconda en Mendieta
  5. Crea entorno conda 'dermvlm' con Python 3.10
  6. Instala PyTorch para Ampere (CUDA 12.1, A30 24GB)
  7. Verifica GPU y CUDA

Uso:
  python scripts/mendieta_setup.py
  python scripts/mendieta_setup.py --skip-ssh-key   # si ya configuraste la clave SSH (default)
"""
import sys
import subprocess
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.mendieta_config import (
    MENDIETA_USER, MENDIETA_HOST, REMOTE_BASE, SSH_OPTS, SSH_KEY_PATH,
    check_tools, ssh, unix_script
)


SETUP_SCRIPT = r"""
set -e

echo "--- [1/6] Creando directorios ---"
mkdir -p "${HOME}/dermvlm/logs"
mkdir -p "${HOME}/dermvlm/data/processed"
mkdir -p "${HOME}/dermvlm/outputs/checkpoints"
mkdir -p "${HOME}/dermvlm/outputs/results"
mkdir -p "${HOME}/dermvlm/outputs/generated_reports"
echo "OK: directorios creados"

echo ""
echo "--- [2/6] Particiones disponibles ---"
sinfo --format="%12P %5a %10l %6D %8c %10m %25G %N" || echo "ADVERTENCIA: sinfo no disponible"

echo ""
echo "--- [3/6] Verificando GPU ---"
# En Mendieta las GPUs estan en nodos de computo, no en el nodo de login.
# Intentamos nvidia-smi pero es normal que no este disponible aqui.
if nvidia-smi 2>/dev/null; then
    echo "OK: GPU detectada en nodo de login"
else
    echo "INFO: nvidia-smi no disponible en nodo de login (normal en Mendieta)."
    echo "      Las GPUs (A30 24GB) estan en los nodos de computo."
    echo "      Verificar con: srun --gres=gpu:1 --pty nvidia-smi"
fi

echo ""
echo "--- [4/6] Verificando Miniconda ---"
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
echo "--- [5/6] Creando entorno dermvlm ---"
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
echo "--- [6/6] Instalando PyTorch (cu121, A30 Ampere) ---"
# Fijar numpy<2: PyTorch 2.1.x fue compilado con NumPy 1.x y falla con NumPy 2.x
${PIP} install "numpy<2" --quiet
if ${PYTHON} -c "import torch" 2>/dev/null; then
    echo "OK: PyTorch ya instalado ($(${PYTHON} -c 'import torch; print(torch.__version__)'))"
else
    ${PIP} install torch torchvision \
        --index-url https://download.pytorch.org/whl/cu121 --quiet
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
else:
    print('  INFO: CUDA no disponible en nodo de login (normal en Mendieta).')
    print('        Las GPUs A30 24GB estan en nodos de computo.')
"

echo ""
echo "--- Modulos disponibles ---"
module av 2>&1 | head -30 || echo "(module system no disponible)"

echo ""
echo "=== Setup completado. Proximo paso: python scripts/mendieta_sync_up.py ==="
"""


def setup_ssh_key():
    """Genera clave ed25519 en Windows y muestra instrucciones para registrarla en Mendieta.

    Mendieta (CCAD) solo acepta claves ed25519. Como no podemos conectar desde Windows
    sin una clave ya registrada, mostramos instrucciones para que el usuario registre
    la clave nueva desde MobaXterm (que si tiene acceso).
    """
    ssh_dir = Path.home() / ".ssh"
    ssh_dir.mkdir(exist_ok=True)
    priv_key = SSH_KEY_PATH
    pub_key = priv_key.with_suffix(".pub")

    if not priv_key.exists():
        print("Generando par de claves ed25519 (requerido por Mendieta/CCAD)...")
        subprocess.run([
            "ssh-keygen", "-t", "ed25519", "-N", "", "-f", str(priv_key)
        ], check=True)
        print(f"OK: clave generada en {priv_key}")
    else:
        print(f"OK: clave ed25519 ya existe en {priv_key}")

    if not pub_key.exists():
        print(f"ERROR: no se encontro {pub_key}")
        return

    pub_key_content = pub_key.read_text().strip()
    print()
    print("=" * 60)
    print("CLAVE PUBLICA (copiar esto):")
    print(pub_key_content)
    print("=" * 60)
    print()

    # Intentar registrar directamente (funciona si ya hay otra clave autorizada)
    print("Intentando registrar la clave automaticamente...")
    cmd = (
        f'mkdir -p ~/.ssh && chmod 700 ~/.ssh && '
        f'grep -qF "{pub_key_content}" ~/.ssh/authorized_keys 2>/dev/null && '
        f'echo "OK: clave ya registrada" || '
        f'(echo "{pub_key_content}" >> ~/.ssh/authorized_keys && '
        f'chmod 600 ~/.ssh/authorized_keys && '
        f'echo "OK: clave registrada exitosamente")'
    )
    result = subprocess.run(["ssh", *SSH_OPTS, f"{MENDIETA_USER}@{MENDIETA_HOST}", cmd])

    if result.returncode == 0:
        print("OK: clave SSH configurada para Windows.")
    else:
        print()
        print("No se pudo registrar automaticamente (Permission denied).")
        print("Registra la clave manualmente desde MobaXterm:")
        print()
        print(f"  1. Abri MobaXterm y conectate:")
        print(f"     ssh {MENDIETA_USER}@{MENDIETA_HOST}")
        print()
        print(f"  2. Ejecuta este comando en Mendieta:")
        print(f'     echo "{pub_key_content}" >> ~/.ssh/authorized_keys')
        print()
        print(f"  3. Verifica que funcione desde Windows:")
        print(f"     ssh -i {priv_key} {MENDIETA_USER}@{MENDIETA_HOST} hostname")
        print()
        print(f"  4. Volve a ejecutar:")
        print(f"     python scripts/mendieta_setup.py")


def main():
    parser = argparse.ArgumentParser(description="Configura el entorno en Mendieta")
    parser.add_argument("--skip-ssh-key", action="store_true", default=True,
                        help="Omitir configuracion de clave SSH (default: True, clave ya enviada)")
    parser.add_argument("--setup-ssh-key", action="store_true",
                        help="Configurar clave SSH (solo si es necesario)")
    args = parser.parse_args()

    check_tools()

    print(f"=== Configurando entorno en Mendieta ===")
    print(f"Host: {MENDIETA_USER}@{MENDIETA_HOST}")
    print(f"Dir remoto: {REMOTE_BASE}")
    print()

    if args.setup_ssh_key:
        print("--- Configurando clave SSH (ed25519) ---")
        setup_ssh_key()
        print()

    # Verificar conexion antes de ejecutar setup remoto
    print("--- Verificando conexion SSH ---")
    test = subprocess.run(
        ["ssh", *SSH_OPTS, f"{MENDIETA_USER}@{MENDIETA_HOST}", "echo OK"],
        capture_output=True, text=True, timeout=30,
    )
    if test.returncode != 0:
        print(f"ERROR: no se pudo conectar a {MENDIETA_USER}@{MENDIETA_HOST}")
        print(f"  stderr: {test.stderr.strip()}")
        print()
        if not SSH_KEY_PATH.exists():
            print("No se encontro clave ed25519. Ejecuta primero:")
            print("  python scripts/mendieta_setup.py --setup-ssh-key")
        else:
            print(f"Clave encontrada en {SSH_KEY_PATH} pero no esta autorizada en Mendieta.")
            print("Registrala desde MobaXterm:")
            pub_key = SSH_KEY_PATH.with_suffix(".pub")
            if pub_key.exists():
                print(f"  1. ssh {MENDIETA_USER}@{MENDIETA_HOST}  (desde MobaXterm)")
                print(f'  2. echo "{pub_key.read_text().strip()}" >> ~/.ssh/authorized_keys')
        sys.exit(1)
    print(f"OK: conexion exitosa ({test.stdout.strip()})")
    print()

    print("--- Ejecutando setup remoto (puede tardar varios minutos) ---")
    result = subprocess.run(
        ["ssh", *SSH_OPTS, f"{MENDIETA_USER}@{MENDIETA_HOST}", "bash", "-s"],
        input=unix_script(SETUP_SCRIPT),
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
