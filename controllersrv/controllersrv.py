import json

from aiohttp import web
from oauth2client import client, crypt
import aiohttp

CLIENT_ID = "109000862034-kn654663dt4jg7hpc9ugj5ldddhousl7.apps.googleusercontent.com"


async def websocket_handler(request):

    logged_in = False
    user_id = None

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            obj = json.loads(msg.data)

            action = obj.get("action", None)

            if not logged_in:
                if action == "login":
                    token = obj.get("args", {}).get("token", "")
                    
                    try:
                        idinfo = client.verify_id_token(token, CLIENT_ID)

                        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                            raise crypt.AppIdentityError("Wrong issuer.")
                    except crypt.AppIdentityError:
                        await ws.send_json({"uuid": obj.get("uuid", ""),
                                            "data": {"logged": False,
                                                     "reason": "Identity Error"},
                                            "end": True})
                    else:
                        user_id = idinfo['sub']
                        await ws.send_json({"uuid": obj.get("uuid", ""),
                                            "data": {"logged": True},
                                            "end": True})
                else:
                    await ws.send_json({"uuid": obj.get("uuid", ""),
                                        "error": {"reason": "Protocol Error"},
                                        "end": True})
            else:
                pass

        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' %
                  ws.exception())

    print('websocket connection closed')

    return ws


app = web.Application()
app.router.add_get('/controller', websocket_handler)
web.run_app(app, host='0.0.0.0', port=3001)
