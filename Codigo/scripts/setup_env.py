"""Setup del entorno: instala PyTorch con CUDA o CPU según el hardware disponible.

Uso:
    python scripts/setup_env.py                    # instala todo
    python scripts/setup_env.py --torch-only       # solo PyTorch (sin requirements.txt)
    python scripts/setup_env.py --dry-run          # muestra comandos sin ejecutar

Detecta automáticamente:
- Si hay GPU NVIDIA con nvidia-smi → instala PyTorch+CUDA (elige versión por driver)
- Si no hay GPU → instala PyTorch CPU

Compatibilidad de CUDA:
    Driver >= 550  → CUDA 12.8 (cu128)
    Driver >= 525  → CUDA 12.4 (cu124)
    Driver >= 450  → CUDA 11.8 (cu118)
    Sin GPU        → CPU
"""

import argparse
import subprocess
import sys


def run(cmd: list[str], dry_run: bool = False) -> int:
    print(f">>> {' '.join(cmd)}")
    if dry_run:
        return 0
    result = subprocess.run(cmd)
    return result.returncode


def get_cuda_index_url() -> tuple[str, str]:
    """Detecta la versión de CUDA del driver y retorna el index-url correcto de PyTorch.

    Returns:
        (index_url, descripcion)
    """
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0 or not result.stdout.strip():
            return None, "Sin GPU detectada"

        driver_str = result.stdout.strip().split("\n")[0].strip()
        # El número principal del driver (ej: "591.86" → 591)
        driver_major = int(float(driver_str))

        if driver_major >= 550:
            return "https://download.pytorch.org/whl/cu128", f"CUDA 12.8 (driver {driver_str})"
        elif driver_major >= 525:
            return "https://download.pytorch.org/whl/cu124", f"CUDA 12.4 (driver {driver_str})"
        elif driver_major >= 450:
            return "https://download.pytorch.org/whl/cu118", f"CUDA 11.8 (driver {driver_str})"
        else:
            return "https://download.pytorch.org/whl/cpu", f"Driver {driver_str} muy antiguo → CPU"

    except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
        return None, "nvidia-smi no encontrado → Sin GPU"


def install_torch(index_url: str | None, dry_run: bool = False) -> bool:
    """Instala torch y torchvision."""
    packages = ["torch", "torchvision"]

    if index_url is not None:
        cmd = [sys.executable, "-m", "pip", "install"] + packages + ["--index-url", index_url]
    else:
        cmd = [sys.executable, "-m", "pip", "install"] + packages + [
            "--index-url", "https://download.pytorch.org/whl/cpu"
        ]

    rc = run(cmd, dry_run)
    return rc == 0


def install_requirements(dry_run: bool = False) -> bool:
    """Instala el resto de dependencias desde requirements.txt."""
    from pathlib import Path
    req_file = Path(__file__).resolve().parent.parent / "requirements.txt"
    cmd = [sys.executable, "-m", "pip", "install", "-r", str(req_file)]
    rc = run(cmd, dry_run)
    return rc == 0


def verify_installation() -> bool:
    """Verifica que torch esté correctamente instalado con CUDA."""
    try:
        import torch
        cuda_ok = torch.cuda.is_available()
        print(f"\n✓ torch {torch.__version__}")
        print(f"  CUDA disponible: {cuda_ok}")
        if cuda_ok:
            print(f"  GPU: {torch.cuda.get_device_name(0)}")
            cap = torch.cuda.get_device_capability(0)
            print(f"  Compute capability: {cap[0]}.{cap[1]}")
            print(f"  VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        return True
    except ImportError:
        print("✗ torch no pudo importarse")
        return False


def main():
    parser = argparse.ArgumentParser(description="Setup de entorno DermVLM")
    parser.add_argument("--torch-only", action="store_true",
                        help="Solo instalar PyTorch (omitir requirements.txt)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostrar comandos sin ejecutar")
    args = parser.parse_args()

    print("=" * 60)
    print("DermVLM — Setup de entorno")
    print("=" * 60)

    # 1. Detectar CUDA
    index_url, desc = get_cuda_index_url()
    print(f"\nHardware detectado: {desc}")
    if index_url:
        print(f"PyTorch index URL: {index_url}")
    else:
        print("PyTorch index URL: https://download.pytorch.org/whl/cpu (fallback)")

    # 2. Instalar PyTorch
    print("\n--- Instalando PyTorch ---")
    ok = install_torch(index_url, args.dry_run)
    if not ok:
        print("ERROR: falló la instalación de PyTorch")
        sys.exit(1)

    # 3. Instalar resto de dependencias
    if not args.torch_only:
        print("\n--- Instalando dependencias (requirements.txt) ---")
        ok = install_requirements(args.dry_run)
        if not ok:
            print("ERROR: falló la instalación de requirements.txt")
            sys.exit(1)

    # 4. Verificar
    if not args.dry_run:
        print("\n--- Verificación ---")
        verify_installation()

    print("\n✓ Setup completo")


if __name__ == "__main__":
    main()
