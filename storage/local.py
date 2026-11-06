import asyncio
from pathlib import Path

from .base import StorageBackend


class LocalStorage(StorageBackend):
    """Storage su filesystem locale con isolamento per tenant.

    Layout: <base_dir>/<tenant_id>/<path>
    Sicurezza: blocca path traversal con resolve() + is_relative_to().
    """

    def __init__(self, base_dir: str | Path = "data"):
        self.base_dir = Path(base_dir).resolve()

    def _tenant_root(self, tenant_id: str) -> Path:
        if not tenant_id or not all(c.isalnum() or c in "-_" for c in tenant_id):
            raise ValueError(f"tenant_id non valido: {tenant_id!r}")
        return self.base_dir / tenant_id

    def _safe_path(self, path: str, tenant_id: str) -> Path:
        root = self._tenant_root(tenant_id)
        target = (root / path).resolve()
        if not target.is_relative_to(root):
            raise PermissionError(f"Path traversal bloccato: {path!r}")
        return target

    async def list_files(self, prefix: str, tenant_id: str) -> list[str]:
        root = self._safe_path(prefix, tenant_id)
        if not root.exists():
            return []
        tenant_root = self._tenant_root(tenant_id)
        return await asyncio.to_thread(
            lambda: [
                str(p.relative_to(tenant_root))
                for p in root.rglob("*")
                if p.is_file()
            ]
        )

    async def read_file(self, path: str, tenant_id: str) -> bytes:
        target = self._safe_path(path, tenant_id)
        if not target.is_file():
            raise FileNotFoundError(f"File non trovato: {path!r} (tenant={tenant_id})")
        return await asyncio.to_thread(target.read_bytes)

    async def write_file(self, path: str, content: bytes, tenant_id: str) -> None:
        target = self._safe_path(path, tenant_id)
        target.parent.mkdir(parents=True, exist_ok=True)
        await asyncio.to_thread(target.write_bytes, content)

    async def exists(self, path: str, tenant_id: str) -> bool:
        try:
            return self._safe_path(path, tenant_id).is_file()
        except PermissionError:
            return False
