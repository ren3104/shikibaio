<p align="center">
  <a href="https://github.com/ren3104/shikibaio/blob/main/LICENSE"><img alt="GitHub license" src="https://img.shields.io/github/license/ren3104/shikibaio"></a>
  <a href="https://pypi.org/project/shikibaio"><img src="https://img.shields.io/pypi/v/shikibaio?color=blue&logo=pypi&logoColor=FFE873" alt="PyPi package version"></a>
  <a href="https://pypi.org/project/shikibaio"><img src="https://img.shields.io/pypi/pyversions/shikibaio.svg?logo=python&logoColor=FFE873" alt="Supported python versions"></a>
  <img src="https://img.shields.io/github/repo-size/ren3104/shikibaio" alt="GitHub repo size">
  <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black"></a>
</p>

~~Shikimori bot asyncio~~ Shikibaio - это асинхронный python фреймворк разработки ботов для [shikimori](https://shikimori.one).

- [Установка](#установка)
- [Поддерживаемые клиенты](#поддерживаемые-клиенты)
- [Пример эхо бота](#пример-эхо-бота)
- [Зависимости](#зависимости)

## Установка
```bash
pip install -U shikibaio
```

## Поддерживаемые клиенты
| Логотип | Название | Версии |
| --- | --- | --- |
| [<img src="https://raw.githubusercontent.com/SecondThundeR/shikithon/main/assets/logo.png" alt="shikithon" height="50">](https://github.com/SecondThundeR/shikithon) | [Shikithon](https://github.com/SecondThundeR/shikithon) | >=2.0.0 |
| [<img src="https://raw.githubusercontent.com/ren3104/Shiki4py/main/assets/shiki4py_logo_v2.jpg" alt="shiki4py" height="50">](https://github.com/ren3104/Shiki4py) | [Shiki4py](https://github.com/ren3104/Shiki4py) | >=2.1.0 |

Если вы разработчик и хотите добавить свой клиет в эту таблицу, то можете сделать это несколькими способами:
1. Добавить [сюда](https://github.com/ren3104/shikibaio/tree/main/shikibaio/adapt_clients) файл с классом переопределившим методы класса [BaseAdapt](https://github.com/ren3104/shikibaio/blob/main/shikibaio/adapt_clients/base.py) и добавить себя в таблицу выше.
2. Написать мне в shikimori ([тык](https://shikimori.one/Ren3104)), чтобы я помог с этим.

## Пример эхо бота
В этом примере я буду использовать клиент shikithon, но вы можете использовать любой другой поддерживаемый клиент.
```python
from shikithon import ShikimoriAPI
from shikibaio import Dispatcher
from shikibaio.types import Event


# Создаем клиент
# Если ваш бот будет отвечать на комментарии, то нужно указать api ключи с доступом к comments ресурсу
# (про это можно почитать подробнее в документации используемого вами клиента и https://shikimori.one/api/doc)
client = ShikimoriAPI()
# Создаем диспетчер
dp = Dispatcher(client)


# Создаем функцию, которая будет получать новые комментарии и отвечать на них
@dp.on_event()
async def echo(event: Event):
    await event.answer(event.text)


# Подписываемся на обновления топика профиля
dp.subscribe_topic(topic_id=555400, is_user_topic=True)
# Запускаем бота
dp.run()
```

## Зависимости
- [aiocometd](https://github.com/robertmrk/aiocometd) - для взаимодействия с faye сервером по веб сокету.
