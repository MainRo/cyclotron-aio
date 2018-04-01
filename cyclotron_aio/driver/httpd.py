import os
from enum import Enum
import asyncio
from collections import namedtuple
from cyclotron import Component

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

AddRoute = namedtuple('AddRoute', ['method', 'path', 'id'])
Response = namedtuple('Response', ['context', 'data', 'status'])
Response.__new__.__defaults__ = (200,)

# source events
ServerStarted = namedtuple('ServerStarted', [])
ServerStopped = namedtuple('ServerStopped', [])
RouteAdded = namedtuple('RouteAdded', ['method', 'path', 'id', 'request'])
Request = namedtuple('Request', [
    'method', 'path', 'data', 'context'
])

''' Httpd source. The server stream is a stream of
    - route is a stream of RouteAdded.
'''
Source = namedtuple('Source', ['server', 'route'])


def make_driver(loop=None):
    def driver(sink):
        '''
            Routes must be configured before starting the server.
        '''
        app = None
        runner = None
        server_observer = None
        route_observer = None

        def add_route(app, method, path, id):
            request_observer = None

            def on_request_subscribe(observer):
                nonlocal request_observer
                request_observer = observer

            async def on_request_data(request, path):
                nonlocal request_observer
                data = await request.read()
                response_future = asyncio.Future()
                request_observer.on_next(Request(
                    method=method,
                    path=path,
                    data=data,
                    context=response_future
                ))
                await response_future
                data, status = response_future.result()

                response = web.StreamResponse(status=status, reason=None)
                await response.prepare(request)
                await response.write(data)
                return response

            if(method == "PUT"):
                app.router.add_put(path, lambda r: on_request_data(r, path))
                app.router.add_route("OPTIONS", path, lambda r: on_request_data(r, path))
            elif(method == "POST"):
                app.router.add_post(path, lambda r: on_request_data(r, path))
                app.router.add_route("OPTIONS", path, lambda r: on_request_data(r, path))
            elif(method == "GET"):
                app.router.add_get(path, lambda r: on_request_data(r, path))
            else:
                # todo error handling
                pass

            if route_observer is not None:
                route_observer.on_next(RouteAdded(
                    method=method,
                    path=path,
                    id=id,
                    request=Observable.create(on_request_subscribe)
                ))

        def create_server_observable():
            def on_server_subscribe(observer):
                nonlocal server_observer
                server_observer = observer

            return Observable.create(on_server_subscribe)

        def create_route_observable():
            def on_route_subscribe(observer):
                nonlocal route_observer
                route_observer = observer

            return Observable.create(on_route_subscribe)

        def start_server(host, port, app):
            runner = web.AppRunner(app)

            async def _start_server(runner):
                await runner.setup()
                site = web.TCPSite(runner, host, port)
                await site.start()
                if server_observer is not None:
                    server_observer.on_next(ServerStarted())


            asyncio.ensure_future(_start_server(runner), loop=loop)
            return runner

        def stop_server(runner):
            async def _stop_server():
                await runner.cleanup()
                server_observer.on_next(ServerStopped())

            asyncio.ensure_future(_stop_server())

        def on_sink_item(i):
            nonlocal app
            nonlocal runner
            if type(i) is Response:
                response_future = i.context
                response_future.set_result((i.data, i.status))
            elif type(i) is AddRoute:
                add_route(app, i.method, i.path, i.id)
            elif type(i) is StartServer:
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

        sink.control.subscribe(on_sink_item)
        return Source(
            server=create_server_observable(),
            route=create_route_observable())

    return Component(call=driver, output=Sink)
