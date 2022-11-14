from typing import Any, Dict


class BaseAdapt:
    async def open(self):
        raise NotImplementedError

    async def close(self) -> None:
        raise NotImplementedError

    async def my_info(self) -> Any:
        raise NotImplementedError

    async def get_comment(self, comment_id: int) -> Any:
        raise NotImplementedError

    async def create_comment(
        self,
        body: str,
        commentable_id: int,
        commentable_type: str,
        is_offtopic: bool = False,
        broadcast: bool = False,
    ) -> Any:
        raise NotImplementedError

    def to_dict(self, model: Any) -> Dict[str, Any]:
        return model
