from typing import Any, Dict, Hashable

from shikibaio.storages import BaseStorage


class MemoryStorage(BaseStorage):
    def __init__(self) -> None:
        self._data: Dict[Hashable, Any] = {}

    async def get(self, key: Hashable, default: Any = None) -> Any:
        if await self.contains(key):
            return self._data[key]
        return default

    async def put(self, key: Hashable, value: Any) -> None:
        self._data[key] = value

    async def delete(self, key: Hashable) -> None:
        if not await self.contains(key):
            raise KeyError("Storage doesn't contain this key.")
        del self._data[key]

    async def contains(self, key: Hashable) -> bool:
        return key in self._data
