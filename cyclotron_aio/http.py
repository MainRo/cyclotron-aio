import traceback
import asyncio
from collections import namedtuple
from cyclotron import Component

from rx import Observable
from rx.subjects import Subject

import aiohttp

Sink = namedtuple('Sink', ['request'])
Source = namedtuple('Source', ['response'])

# sink events

Request = namedtuple('Request', [
    'id', 'method', 'url', 'params', 'data', 'headers',
    'allow_redirects', 'max_redirects'
])

Request.__new__.__defaults__ = ('GET', None, None, None, None, True, 10,)


# source events
Response = namedtuple('Response', ['id', 'response'])

HttpResponse = namedtuple('HttpResponse', [
    'status', 'reason',
    'method', 'url',
    'data', 'cookies',
    'headers', 'content_type'])


def make_driver(loop=None):
    def driver(sink):
        '''
            Routes must be configured before starting the server.
        '''
        session = None

        def on_response_subscribe(observer):
            async def _request(request):
                nonlocal session

                if session is None:
                    session = aiohttp.ClientSession()

                try:
                    response = await session.request(
                        request.method,
                        request.url,
                        params=request.params,
                        data=request.data,
                        headers=request.headers,
                        allow_redirects=request.allow_redirects,
                        max_redirects=request.max_redirects
                    )

                    data = await response.read()
                    observer.on_next(Response(
                        id=request.id,
                        response=Observable.just(HttpResponse(
                            status=response.status, reason=response.status,
                            method=response.method, url=response.url,
                            data=data, cookies=response.cookies,
                            headers=response.headers,
                            content_type=response.content_type
                        ))
                    ))

                except Exception as e:
                    print("exception: {}".format(e))
                    observer.on_next(Response(
                        id=request.id,
                        response=Observable.throw(e)))

            def on_request_item(i):
                if type(i) is Request:
                    asyncio.ensure_future(_request(i), loop=loop)
                else:
                    print("received unknown item: {}".format(type(i)))

            def on_request_error(e):
                print("http sink error: {}, {}".format(
                    e, traceback.format_exc()))

            return sink.request.subscribe(
                on_next=on_request_item,
                on_error=on_request_error)

        return Source(
            response=Observable.create(on_response_subscribe)
        )

    return Component(call=driver, input=Sink)


ClientSink = namedtuple('ClientSink', ['http_request'])
ClientSource = namedtuple('ClientSource', ['http_response'])

Api = namedtuple('Api', ['request'])
Client = namedtuple('Client', ['sink', 'api'])


def client(sources):
    http_request = Subject()

    def request(method, url, **kwargs):
        def on_subscribe(observer):
            response = (
                sources.http_response
                .filter(lambda i: i.id is response_observable)
                .take(1)
                .flat_map(lambda i: i.response)
            )

            dispose = response.subscribe(observer)
            http_request.on_next(Request(
                id=response_observable,
                url=url,
                method=method,
                **kwargs
            ))

            return dispose

        response_observable = Observable.create(on_subscribe)
        return response_observable

    return Client(
        sink=ClientSink(
            http_request=http_request,
        ),
        api=Api(
            request=request,
        )
    )
