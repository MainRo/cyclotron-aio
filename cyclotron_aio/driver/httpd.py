import os
from enum import Enum
import asyncio
from collections import namedtuple
from rx import Observable
from rx.concurrency import AsyncIOScheduler

from aiohttp import web
from aiohttp import helpers
from aiohttp.log import access_logger

from multidict import MultiDict

Sink = namedtuple('Sink', ['control'])

# sink events
Initialize = namedtuple('Initialize', [
    'request_max_size'
])
Initialize.__new__.__defaults__ = (1024**2,)

StartServer = namedtuple('StartServer', [
    'host', 'port'
])

StopServer = namedtuple('StopServer', [])

# source events
ServerStarted = namedtuple('ServerStarted', [])
ServerStopped = namedtuple('ServerStopped', [])

''' Httpd source. The server stream is a stream of
'''
Source = namedtuple('Source', ['server'])

def make_driver(loop=None):

    def driver(sink):
        app = None
        runner = None
        request_observer = None

        def add_route(type, path):
            print("add route {} on path {}".format(type, path))
            async def on_request_data(request, path):
                nonlocal request_observer
                data = await request.read()
                response_future = asyncio.Future()
                request_observer.on_next({
                    "what": "data",
                    "type": type,
                    "path": path,
                    "data": data,
                    "context": response_future
                })
                await response_future

                response = web.StreamResponse(
                    status=200, reason=None,
                    headers=MultiDict([
                        ("Access-Control-Allow-Origin", "*"),
                        ("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept"),
                        ("Access-Control-Allow-Methods", "GET, POST, PUT, OPTIONS"),
                    ]))
                await response.prepare(request)
                await response.write(bytearray(response_future.result(), 'utf8'))
                return response


            if(type == "PUT"):
                app.router.add_put(path, lambda r: on_request_data(r, path))
                app.router.add_route("OPTIONS", path, lambda r: on_request_data(r, path))
            elif(type == "POST"):
                app.router.add_post(path, lambda r: on_request_data(r, path))
                app.router.add_route("OPTIONS", path, lambda r: on_request_data(r, path))
            elif(type == "GET"):
                app.router.add_get(path, lambda r: on_request_data(r, path))

        def create_server_observable():
            def on_server_subscribe(observer):
                nonlocal request_observer
                request_observer = observer

            #scheduler = AsyncIOScheduler()
            return Observable.create(on_server_subscribe)

        def start_server(host, port, app):
            runner = web.AppRunner(app)

            async def _start_server(runner):
                await runner.setup()
                site = web.TCPSite(runner, host, port)
                await site.start()
                request_observer.on_next(ServerStarted())

            asyncio.ensure_future(_start_server(runner), loop=loop)
            return runner

        def stop_server(runner):
            async def _stop_server():
                await runner.cleanup()
                request_observer.on_next(ServerStopped())

            asyncio.ensure_future(_stop_server())

        def on_sink_item(i):
            nonlocal app
            nonlocal runner
            if type(i) is StartServer:
                runner = start_server(i.host, i.port, app)
            elif type(i) is StopServer:
                stop_server(runner)
            elif type(i) is Initialize:
                app_args = {
                    "client_max_size": i.request_max_size
                }
                app = web.Application(**app_args)
            else:
                print("received unknown item: {}".format(type(i)))

            '''
            if i["what"] == "response":
                response_future = i["context"]
                response_future.set_result(i["data"])

            elif i["what"] == "add_route":
                add_route(i["type"], i["path"])
            '''

        sink.control.subscribe(on_sink_item)
        return Source(server=create_server_observable())

    return driver


# loop.create_task()
