from shikibaio.types import Event


class Filter:
    async def check(self, event: Event) -> bool:
        raise NotImplementedError

    async def __call__(self, event: Event) -> bool:
        return await self.check(event)

    def __invert__(self):
        return NotFilter(self)

    def __and__(self, other):
        if isinstance(self, AndFilter):
            self.filters.append(other)
            return self
        return AndFilter(self, other)

    def __or__(self, other):
        if isinstance(self, OrFilter):
            self.filters.append(other)
            return self
        return OrFilter(self, other)


class NotFilter(Filter):
    def __init__(self, filter) -> None:
        self.filter = filter

    async def check(self, event: Event) -> bool:
        return not await self.filter(event)


class AndFilter(Filter):
    def __init__(self, *filters) -> None:
        self.filters = list(filters)

    async def check(self, event: Event) -> bool:
        for filter in self.filters:
            result = await filter(event)
            if not result:
                return False
        return True


class OrFilter(Filter):
    def __init__(self, *filters) -> None:
        self.filters = list(filters)

    async def check(self, event: Event) -> bool:
        for filter in self.filters:
            result = await filter(event)
            if result:
                return True
        return False
