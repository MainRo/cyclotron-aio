import asyncio
from unittest import TestCase

from rx import Observable
import cyclotron_aio.dispose as dispose


class DisposeTestCase(TestCase):

    def test_make_driver(self):
        self.assertIsNotNone(dispose.make_driver())

    def test_stop_default_loop(self):
        stopped = False
        observer = None

        def on_subscribe(o):
            nonlocal observer
            observer = o

        observable = Observable.create(on_subscribe)

        def stop_loop():
            nonlocal stopped, observer
            stopped = True
            observer.on_next(True)

        loop = asyncio.get_event_loop()
        loop.call_soon(stop_loop)

        driver = dispose.make_driver()
        driver.call(dispose.Sink(dispose=observable))

        loop.run_forever()
        loop.close()
        self.assertEqual(True, stopped)


    def test_stop_custom_loop(self):
        stopped = False
        observer = None

        def on_subscribe(o):
            nonlocal observer
            observer = o

        observable = Observable.create(on_subscribe)

        def stop_loop():
            nonlocal stopped, observer
            stopped = True
            observer.on_next(True)

        loop = asyncio.new_event_loop()
        self.assertNotEqual(asyncio.get_event_loop(), stopped)
        loop.call_soon(stop_loop)

        driver = dispose.make_driver(loop=loop)
        driver.call(dispose.Sink(dispose=observable))

        loop.run_forever()
        loop.close()
        self.assertEqual(True, stopped)
