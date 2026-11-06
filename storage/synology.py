from .base import StorageBackend


class SynologyStorage(StorageBackend):
    """Placeholder — implementazione quando un cliente avra' il NAS."""

    def __init__(self, host: str, user: str, password: str):
        raise NotImplementedError(
            "SynologyStorage verra' implementato quando ci sara' un cliente con NAS."
        )

    async def list_files(self, prefix, tenant_id): ...
    async def read_file(self, path, tenant_id): ...
    async def write_file(self, path, content, tenant_id): ...
    async def exists(self, path, tenant_id): ...
