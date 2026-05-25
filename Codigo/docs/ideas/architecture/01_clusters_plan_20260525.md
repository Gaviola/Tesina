# RFC 01 — Consolidación de gestión de clústeres (Mendieta + TOKO)

**Fecha:** 2026-05-25
**Estado:** Propuesta arquitectónica (no se ejecutan jobs)
**Alcance:** `Codigo/scripts/mendieta/`, `Codigo/scripts/toko/`

## Problema

Los directorios `scripts/mendieta/` (≈1875 líneas) y `scripts/toko/` (≈1793 líneas) implementan las mismas siete operaciones (`setup`, `submit`, `sync_up`, `sync_down`, `monitor`, `clean_remote`, más helpers) con ≈80% de duplicación. Las diferencias reales entre clústeres son pocas y caben en datos:

- Host SSH, usuario, ruta remota raíz.
- GPU + versión de CUDA (informativo, salvo en setup).
- Almacenamiento persistente (Mendieta NFS) vs. scratch (TOKO).
- Política de `--delete` en `sync_up` (segura en NFS, peligrosa en scratch).
- Tabla de alias de jobs (`all_vlm_v2`, `mini_vlm`, etc.).

Hoy ambas diferencias y la lógica compartida (fallback rsync → tar+scp en Windows, parseo de rangos `--logs 12345 12350`, escritura de `outputs/jobs_log.txt`, tail de logs por job ID) están entremezcladas en cada par de scripts. Consecuencias observadas:

- Cada fix se aplica dos veces (riesgo de divergencia silenciosa).
- No hay tests: todo shellea contra SSH real.
- Agregar un tercer clúster implica copiar ≈1800 líneas más.
- La elección rsync/tar+scp no es introspectable.

## Interfaz propuesta

Híbrido de las propuestas "mínima" y "común caso optimizado":

```python
# Codigo/scripts/cluster/__init__.py
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Literal, Protocol

@dataclass(frozen=True)
class ClusterProfile:
    name: str                              # "mendieta" | "toko"
    ssh_host: str
    ssh_user: str
    remote_root: PurePosixPath
    cuda: str
    default_partition: str
    persistent_storage: bool               # define el default de --delete
    queue_days: int
    job_aliases: dict[str, list[str]]      # alias → [scripts sbatch]

class Transport(Protocol):                 # puerto único
    def run(self, argv: list[str], *, remote: bool = False) -> tuple[int, str, str]: ...
    def push(self, local: Path, remote: PurePosixPath, *, delete: bool) -> None: ...
    def pull(self, remote: PurePosixPath, local: Path, *, patterns: list[str] = ()) -> None: ...

class Cluster:
    def __init__(self, profile: ClusterProfile, transport: Transport,
                 jobs_log: Path = Path("outputs/jobs_log.txt")): ...

    def submit(self, alias: str, *, dry_run: bool = False) -> list["JobRef"]: ...
    def sync_up(self, *, delete: bool | None = None,
                extra_excludes: list[str] = ()) -> None: ...
    def sync_down(self, *, reports: bool = False, checkpoints: bool = False,
                  logs: list[int] | None = None) -> None: ...
    def monitor(self, *, tail_job: int | None = None, lines: int = 100) -> str: ...
    def setup(self) -> None: ...
    def clean(self, *, older_than_days: int = 7, dry_run: bool = True) -> None: ...

def get(name: Literal["mendieta", "toko"]) -> Cluster: ...   # factory por defecto
```

Los scripts CLI quedan reducidos a ≈8 líneas:

```python
# scripts/mendieta/submit.py
import sys
from cluster import get
get("mendieta").submit(sys.argv[1])
```

```python
# scripts/toko/sync_down.py
import argparse
from cluster import get
ap = argparse.ArgumentParser()
ap.add_argument("--logs", nargs="+", type=int)
ap.add_argument("--reports", action="store_true")
ap.add_argument("--checkpoints", action="store_true")
args = ap.parse_args()
get("toko").sync_down(reports=args.reports, checkpoints=args.checkpoints, logs=args.logs)
```

### Complejidad que oculta

- Sondeo rsync (WSL/cygwin) → fallback tar+scp dentro de `LocalSubprocessTransport`.
- `delete=None` se resuelve a `profile.persistent_storage` (True en Mendieta, False en TOKO).
- Resolución de alias: `submit("all_vlm_v2")` expande a N `sbatch` y registra cada `JobRef` en `outputs/jobs_log.txt`.
- Mapeo de paths remotos por clúster (NFS vs scratch).
- Expansión de rangos `logs=[12345, 12350]`.

## Estrategia de dependencias

**Categoría 3 — Remoto pero propio (puertos y adaptadores).**

- **Puerto:** `Transport` (3 primitivas: `run`, `push`, `pull`). Es el único punto de salida al SO.
- **Adaptador de producción:** `LocalSubprocessTransport`. Wrappea `subprocess.run` con `ssh`/`rsync` preferido y fallback a `tar | ssh | tar -x`. SCP queda como último recurso para archivos sueltos.
- **Adaptador de tests:** `RecordingTransport` (≈50 líneas). Captura tuplas `(verb, args)`, reproduce stdout canónica (`Submitted batch job 12345`, filas de `squeue`), usa `tmp_path` para `push`/`pull`. Los tests aseveran sobre el log de llamadas, sin red ni SSH.

Se descarta la propuesta "máxima flexibilidad" (registries + entry-points + capability negotiation): es overengineering para dos clústeres. Si llega un tercero, se agrega un `ClusterProfile` y opcionalmente una segunda implementación de `Transport`, sin tocar el core.

## Estrategia de testing

**Nuevos tests de borde a escribir** (todos contra `RecordingTransport`):

- `submit("all_vlm_v2")` resuelve el alias correcto y emite los `sbatch` esperados.
- `sync_up()` usa `--delete` en Mendieta y NO lo usa en TOKO (regresión: bug del scratch).
- `sync_up()` cae a tar+scp cuando el transport reporta que rsync no está disponible.
- `sync_down(logs=[12345, 12350])` expande el rango inclusivo.
- `monitor(tail_job=12345)` arma el `tail -f` con la ruta correcta por clúster (`logs/<model>/` vs `logs/shared/`).
- `JobRef` se persiste en `outputs/jobs_log.txt` con campos `(job_id, alias, cluster, script, timestamp)`.

**Tests viejos a borrar:** ninguno (no existían).

**Necesidades de entorno:** ninguna — el `RecordingTransport` vive en memoria. CI puede ejecutar el suite en cualquier máquina sin acceso a clúster.

## Recomendaciones de implementación

Lo que el módulo `cluster/` debe **poseer**:

- Resolución de alias de jobs.
- Política `--delete` por persistencia del clúster.
- Fallback de transporte (rsync ↔ tar+scp).
- Registro de jobs (`jobs_log.txt`) y mapeo `job_id → ruta de log remoto`.
- Mapeo entre `outputs/` local y rutas remotas por clúster.

Lo que debe **ocultar**:

- El comando `subprocess` concreto que se ejecuta.
- Detección de WSL/cygwin.
- Diferencias de partición SLURM, módulos `module load` por CUDA, paths NFS vs scratch.

Lo que debe **exponer**:

- `Cluster.submit/sync_up/sync_down/monitor/setup/clean` con defaults razonables.
- `ClusterProfile` como única fuente de verdad por clúster (data, no código).
- `get(name)` como factory de conveniencia.

**Migración recomendada:**

1. Crear `Codigo/scripts/cluster/` con `profile.py`, `transport.py`, `cluster.py`, `profiles/mendieta.py`, `profiles/toko.py`.
2. Migrar `submit.py` primero (riesgo bajo, alta visibilidad). Mantener los scripts viejos como wrappers `deprecation warning`.
3. Migrar `sync_up`/`sync_down`/`monitor` en una segunda PR.
4. Borrar `scripts/mendieta/*.py` y `scripts/toko/*.py` excepto los stubs CLI (≈8 líneas).
5. Documentar en `docs/USAGE.md` el nuevo punto de entrada.

**Líneas estimadas ahorradas:** ≈1600 (de ≈3700 a ≈2100, incluyendo tests).

## Sincronización con clústeres

Este RFC es **el** RFC que cambia los scripts de sync, así que la coordinación es sensible:

- El primer merge debe mantener los stubs viejos (`scripts/mendieta/sync_up.py` etc.) como wrappers que delegan al nuevo módulo. Sólo así un `sync_up` desde una checkout vieja sigue funcionando contra el cluster.
- Recién en una segunda PR borrar los stubs originales, una vez verificado que el wrapper nuevo está copiado en ambos clústeres.
- Mientras la migración esté en curso, evitar `sync_up.py --delete`: el árbol remoto puede tener archivos transitorios que no queremos perder.
