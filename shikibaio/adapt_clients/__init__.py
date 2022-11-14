from typing import Any

from shikibaio.adapt_clients.base import BaseAdapt
from shikibaio.adapt_clients.shiki4py import Shiki4pyAdapt
from shikibaio.adapt_clients.shikithon import ShikithonAdapt

__all__ = ["get_adapt_client"]

CLIENTS = {"shiki4py": Shiki4pyAdapt, "shikithon": ShikithonAdapt}


def get_adapt_client(client: Any) -> BaseAdapt:
    module_path: str = type(client).__module__
    library_name = module_path.split(".")[0].lower()
    if library_name not in CLIENTS:
        raise RuntimeError(f"Получен неизвестный клиент {library_name}!")
    return CLIENTS[library_name](client)
