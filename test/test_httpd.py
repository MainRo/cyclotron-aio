import asyncio
from unittest import TestCase

from rx import Observable
from rx.subjects import Subject
from cyclotron_aio.driver.dispose import make_dispose_driver, DisposeSink
import cyclotron_aio.driver.httpd as httpd


class HttpdServerTestCase(TestCase):

    def test_start_server_item(self):
        self.assertRaises(TypeError, httpd.StartServer)

        item = httpd.StartServer("localhost", 80)
        self.assertEqual("localhost", item.host)
        self.assertEqual(80, item.port)


    def test_start_server(self):
        loop = asyncio.new_event_loop()
        loop.set_debug(True)
        asyncio.set_event_loop(loop)

        sink = httpd.Sink(
            control = Subject()
        )

        def on_httpd_item(i):
            if type(i) is httpd.ServerStarted:
                sink.control.on_next(httpd.StopServer())
            elif type(i) == httpd.ServerStopped:
                asyncio.get_event_loop().stop()

        def control_stream(sink):
            sink.control.on_next(httpd.Initialize())
            sink.control.on_next(httpd.StartServer("localhost", 9999))

        loop.call_soon(control_stream, sink)
        source = httpd.make_driver(loop)(sink)
        source.server.subscribe(on_httpd_item)

        loop.run_forever()
        loop.close()
