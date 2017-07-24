import asyncio
import json
import os

from aiohttp import web
from environconfig import EnvironConfig
from environconfig import StringVar, IntVar
import rethinkdb as r


class Config(EnvironConfig):
    RETHINKDB_PORT_28015_TCP_ADDR = StringVar(default="rethinkdb")
    RETHINKDB_PORT_28015_TCP_PORT = IntVar(default=28015)

    DATABASE_NAME = StringVar(default="pantrydefender")
    TABLE_NAME = StringVar(default="batches")


r.set_loop_type('asyncio')


async def get_connection():
    return await r.connect(
        db=Config.DATABASE_NAME,
        host=Config.RETHINKDB_PORT_28015_TCP_ADDR,
        port=Config.RETHINKDB_PORT_28015_TCP_PORT)


async def list_with_changes(user, filter):
    connection = await get_connection()
    feed = await r.table(Config.TABLE_NAME
        ).filter(filter
        ).changes(include_initial=True
        ).run(connection)

    while (await feed.fetch_next()):
        change = await feed.next()
        print('Got a change for user "{}": {}'.format(user, change))
        yield change


async def websocket_handler(request):
    user = request.match_info.get("user")
    filter = json.loads(request.rel_url.query.get("filter", "{}"))

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async def send_changes():
        async for change in list_with_changes(user, filter):
            await ws.send_json(change)

    change_sender = asyncio.get_event_loop().create_task(send_changes())
    try:
        async for msg in ws:
            pass
    except asyncio.CancelledError:
        print('websocket cancelled')
    finally:
         change_sender.cancel()

    await ws.close()
    return ws


app = web.Application()
app.router.add_get('/list/{user}', websocket_handler)
web.run_app(app, host='0.0.0.0', port=3002)
