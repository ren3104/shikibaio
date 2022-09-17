<p align="center">
  <a href="https://github.com/ren3104/shikibaio/blob/main/LICENSE"><img alt="GitHub license" src="https://img.shields.io/github/license/ren3104/shikibaio"></a>
  <a href="https://pypi.org/project/shikibaio"><img src="https://img.shields.io/pypi/v/shikibaio?color=blue" alt="PyPi package version"></a>
  <a href="https://pypi.org/project/shikibaio"><img src="https://img.shields.io/pypi/pyversions/shikibaio.svg" alt="Supported python versions"></a>
  <img src="https://img.shields.io/github/repo-size/ren3104/shikibaio" alt="GitHub repo size">
  <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black"></a>
  <a href="https://hits.seeyoufarm.com"><img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fren3104%2FShiki4py&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false"/></a>
</p>

> Данный пакет находится в стадии разработки, потому может содержать баги и недоработки!

~~Shikimori bot asyncio~~ Shikibaio - это асинхронный python фреймворк разработки ботов для [shikimori](https://shikimori.one).

- [Особенности](#особенности)
- [Установка](#установка)
- [Пример эхо бота](#пример-эхо-бота)
- [Тестирование](#тестирование)
- [Зависимости](#зависимости)

## Особенности
- Асинхронность
- Типизированность

## Установка
```bash
pip install -U shikibaio
```

## Пример эхо бота
```python
from shikibaio import Dispatcher
from shikibaio.types import Event
from shiki4py import Shikimori


api = Shikimori("Api Test")
dp = Dispatcher(api)

dp.subscribe_topic(topic_id=555400, is_user_topic=True)


@dp.topic_handler()
async def echo(event: Event):
    await api.comments.create(event.text, event.chat_id, "User")


dp.run()
```

## Тестирование
В shikibaio предусмотрены специальные классы для тестирования ваших проектов, чтобы не спамить в топиках шикимори.

Для этого изменим код в примере эхо бота:
```python
from shikibaio import Dispatcher
from shikibaio.types import Event
from shikibaio.testing import Topic
import asyncio


dp = Dispatcher()


@dp.topic_handler()
async def echo(event: Event):
    print(event.text)


async def main():
    topic = Topic(dp)
    await topic.create_comment("test")


asyncio.run(main())
```

## Зависимости
- [aiocometd](https://github.com/robertmrk/aiocometd) - для взаимодействия с faye сервером по веб сокету.
- [shiki4py]() - для взаимодействия c api shikimori.
