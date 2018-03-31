import asyncio
from unittest import TestCase

from rx import Observable
from cyclotron_aio.driver.dispose import make_dispose_driver, DisposeSink


class DisposeTestCase(TestCase):

    def test_make_driver(self):
        self.assertIsNotNone(make_dispose_driver())

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

        driver = make_dispose_driver()
        driver.call(DisposeSink(dispose=observable))

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

        driver = make_dispose_driver(loop=loop)
        driver.call(DisposeSink(dispose=observable))

        loop.run_forever()
        loop.close()
        self.assertEqual(True, stopped)
