from abc import ABC, abstractmethod


class StorageBackend(ABC):
    """Interfaccia astratta per lo storage.

    Oggi: LocalStorage. Domani: SynologyStorage.
    Il resto di iCrawler parla SOLO con questa interfaccia.
    """

    @abstractmethod
    async def list_files(self, prefix: str, tenant_id: str) -> list[str]: ...
    @abstractmethod
    async def read_file(self, path: str, tenant_id: str) -> bytes: ...
    @abstractmethod
    async def write_file(self, path: str, content: bytes, tenant_id: str) -> None: ...
    @abstractmethod
    async def exists(self, path: str, tenant_id: str) -> bool: ...
