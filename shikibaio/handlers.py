import asyncio
from collections import namedtuple
from datetime import datetime, timedelta
from typing import List, Optional, Union

from shikibaio.types import Event

Handler = namedtuple("Handler", ["event_type", "callback", "check"])


class IterHandler:
    def __init__(
        self,
        number: Optional[int] = None,
        timeout: Optional[Union[int, datetime]] = None,
    ) -> None:
        self._queue: asyncio.Queue = asyncio.Queue()
        self._number = number
        if isinstance(timeout, int):
            timeout = datetime.now() + timedelta(seconds=timeout)
        self._timeout = timeout

    async def put(self, event: Event) -> None:
        await self._queue.put(event)

    def is_finished(self) -> bool:
        return (self._timeout is not None and datetime.now() > self._timeout) or (
            self._number is not None and self._number < 1
        )

    async def __aiter__(self):
        while True:
            if self._number is None and self._timeout is None:
                yield await self._queue.get()
            else:
                if self.is_finished():
                    break

                try:
                    yield await self._queue.get_nowait()

                    if self._number is not None:
                        self._number -= 1
                except asyncio.QueueEmpty:
                    pass

                await asyncio.sleep(0.2)
