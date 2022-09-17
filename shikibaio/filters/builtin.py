import re
from typing import List, Pattern, Union

from shikibaio.enums import DataType, EventType
from shikibaio.filters.filters import Filter
from shikibaio.types import Event

DEFAULT_PREFIXES = ["!", "/"]


class CommandFilter(Filter):
    def __init__(
        self,
        commands: Union[List[str], str],
        prefixes: Union[List[str], str] = DEFAULT_PREFIXES,
        ignore_case: bool = True,
    ) -> None:
        if isinstance(commands, str):
            commands = [commands]

        if isinstance(prefixes, str):
            prefixes = [prefixes]

        self.commands = list(map(str.lower, commands)) if ignore_case else commands
        self.prefixes = prefixes
        self.ignore_case = ignore_case

    async def check(self, event: Event) -> bool:
        text = event.text.lower() if self.ignore_case else event.text

        cmd_prefix = None
        for prefix in self.prefixes:
            if text.startswith(prefix):
                cmd_prefix = prefix

        if cmd_prefix == None:
            return False

        if text.lstrip(cmd_prefix) in self.commands:
            return True

        return False


class RegexFilter(Filter):
    def __init__(self, pattern: Union[Pattern, str]) -> None:
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        self.pattern = pattern

    async def check(self, event: Event) -> bool:
        return self.pattern.search(event.text) != None


class EventTypeFilter(Filter):
    def __init__(self, event_type: Union[str, EventType]) -> None:
        if isinstance(event_type, EventType):
            event_type = event_type.value
        self.event_type = event_type

    async def check(self, event: Event) -> bool:
        event_type = event.event_type

        if isinstance(event_type, EventType):
            event_type = event_type.value

        return event_type == self.event_type


class DataTypeFilter(Filter):
    def __init__(self, data_type: Union[str, DataType]) -> None:
        if isinstance(data_type, DataType):
            data_type = data_type.value
        self.data_type = data_type

    async def check(self, event: Event) -> bool:
        data_type = event.data_type

        if isinstance(data_type, DataType):
            data_type = data_type.value

        return data_type == self.data_type
