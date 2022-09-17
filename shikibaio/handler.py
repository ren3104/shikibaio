from typing import Any, Callable, Iterable, Optional, Union

from shikibaio.filters import AndFilter, Filter
from shikibaio.types import Event


class Handler:
    def __init__(
        self,
        callback: Callable,
        filters: Optional[Union[Iterable[Filter], Filter]] = None,
        blocking: bool = True,
    ) -> None:
        self.callback = callback
        if isinstance(filters, Iterable):
            filters = AndFilter(*filters)
        self.filters = filters
        self.blocking = blocking

    async def filter(self, event: Event) -> bool:
        if self.filters is None:
            return True
        return await self.filters(event)

    async def handle(self, event: Event) -> Any:
        return await self.callback(event)

    def __eq__(self, obj: object) -> bool:
        if callable(obj):
            return self.callback == obj
        return super().__eq__(obj)
