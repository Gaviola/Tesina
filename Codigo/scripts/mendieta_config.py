"""
mendieta_config.py — Configuracion centralizada para scripts de Mendieta (CCAD UNC).
Importado por todos los scripts mendieta_*.py

Credenciales: se leen desde Codigo/.env (nunca hardcodeadas en el codigo).
Crear el archivo .env con:
    MENDIETA_USER=fgaviola
    MENDIETA_HOST=mendieta.ccad.unc.edu.ar
    MENDIETA_SSH_KEY=~/.ssh/id_ed25519   (opcional, default)
"""
import sys
import shutil
import subprocess
from pathlib import Path

# ─── Paths locales ────────────────────────────────────────────────────────────
SCRIPTS_DIR = Path(__file__).resolve().parent
CODIGO_DIR  = SCRIPTS_DIR.parent
LOCAL_DATA    = CODIGO_DIR / "data"
LOCAL_OUTPUTS = CODIGO_DIR / "outputs"


def _load_env() -> dict:
    """Lee Codigo/.env y retorna un dict con las variables."""
    env_file = CODIGO_DIR / ".env"
    env = {}
    if not env_file.exists():
        return env
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        env[key.strip()] = val.strip()
    return env


_env = _load_env()

# ─── Credenciales y paths remotos ────────────────────────────────────────────
MENDIETA_USER = _env.get("MENDIETA_USER", "fgaviola")
MENDIETA_HOST = _env.get("MENDIETA_HOST", "mendieta.ccad.unc.edu.ar")
# Mendieta usa home NFS persistente (no scratch como TOKO)
REMOTE_BASE = f"/home/{MENDIETA_USER}/dermvlm"
REMOTE_DATA    = f"{REMOTE_BASE}/data"
REMOTE_OUTPUTS = f"{REMOTE_BASE}/outputs"
REMOTE_LOGS    = f"{REMOTE_BASE}/logs"

# ─── Clave SSH ────────────────────────────────────────────────────────────────
# Mendieta requiere claves ed25519. Si MENDIETA_SSH_KEY esta en .env, se usa esa ruta.
# Default: ~/.ssh/id_ed25519
_ssh_key_raw = _env.get("MENDIETA_SSH_KEY", "~/.ssh/id_ed25519")
SSH_KEY_PATH = Path(_ssh_key_raw).expanduser()

# ─── Opciones SSH comunes ─────────────────────────────────────────────────────
# StrictHostKeyChecking=accept-new: acepta automaticamente hosts nuevos (primera conexion)
# -i: usa la clave ed25519 especifica para Mendieta
SSH_OPTS = ["-o", "StrictHostKeyChecking=accept-new"]
if SSH_KEY_PATH.exists():
    SSH_OPTS.extend(["-i", str(SSH_KEY_PATH)])


def unix_script(script: str) -> bytes:
    """Normaliza a LF y codifica a bytes para subprocess en modo binario.

    En Windows, subprocess.run(..., text=True) abre la pipe en modo texto y
    re-introduce \\r\\n al escribir, rompiendo bash en el cluster Linux.
    Pasar bytes directamente evita esa traduccion automatica.
    """
    return script.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def ssh(cmd: str, capture: bool = False) -> subprocess.CompletedProcess:
    """Ejecuta un comando remoto en Mendieta via SSH.
    Antepone '. /etc/profile' para cargar el PATH completo (SLURM, modules, etc.)
    igual que hacen los scripts .sh del cluster.
    """
    full_cmd = ["ssh", *SSH_OPTS, f"{MENDIETA_USER}@{MENDIETA_HOST}", f". /etc/profile; {cmd}"]
    if capture:
        return subprocess.run(full_cmd, capture_output=True, text=True)
    return subprocess.run(full_cmd)


def check_tools():
    """Verifica que ssh y scp esten disponibles."""
    missing = [t for t in ("ssh", "scp") if not shutil.which(t)]
    if missing:
        print(f"ERROR: {missing} no encontrado(s) en PATH.")
        print("En Windows 10/11 OpenSSH debe estar instalado.")
        print("Verificar: Configuracion > Aplicaciones > Caracteristicas opcionales > OpenSSH Client")
        sys.exit(1)

    if not (CODIGO_DIR / ".env").exists():
        print("ADVERTENCIA: no se encontro Codigo/.env")
        print("Crea el archivo con:")
        print("  MENDIETA_USER=fgaviola")
        print("  MENDIETA_HOST=mendieta.ccad.unc.edu.ar")


def has_rsync() -> bool:
    return shutil.which("rsync") is not None


def remote_path(subpath: str = "") -> str:
    if subpath:
        return f"{REMOTE_BASE}/{subpath.lstrip('/')}"
    return REMOTE_BASE
