import asyncio
from collections import namedtuple
from datetime import datetime, timedelta
from typing import List, Optional

from shikibaio.types import Event

Handler = namedtuple("Handler", ["event_type", "callback", "check"])


class IterHandler:
    def __init__(
        self, number: Optional[int] = None, timeout: Optional[int] = None
    ) -> None:
        self._finished = False
        self._events: List[Event] = []

        self._number = number
        self._timeout = (
            None if timeout is None else datetime.now() + timedelta(seconds=timeout)
        )

    def is_finished(self) -> bool:
        return (self._timeout is not None and datetime.now() > self._timeout) or (
            self._number is not None and self._number < 1
        )

    async def __aiter__(self):
        while True:
            await asyncio.sleep(0.2)

            if self.is_finished():
                break

            if len(self._events) > 0:
                for e in self._events:
                    yield e
                    self._events.remove(e)

                    if self._number is not None:
                        self._number -= 1
