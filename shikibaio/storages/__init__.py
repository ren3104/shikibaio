from typing import Any, Hashable


class BaseStorage:
    async def get(self, key: Hashable, default: Any = None) -> Any:
        raise NotImplementedError

    async def put(self, key: Hashable, value: Any) -> None:
        raise NotImplementedError

    async def delete(self, key: Hashable) -> None:
        raise NotImplementedError

    async def contains(self, key: Hashable) -> bool:
        raise NotImplementedError
