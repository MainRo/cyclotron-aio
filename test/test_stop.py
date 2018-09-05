import asyncio
from unittest import TestCase

from rx import Observable
from rx.subjects import Subject
import cyclotron_aio.stop as stop


class StopTestCase(TestCase):

    def test_make_driver(self):
        self.assertIsNotNone(stop.make_driver())

    def test_stop_default_loop_on_item(self):
        stopped = False
        stop_control = Subject()

        def stop_loop():
            nonlocal stopped
            stopped = True
            stop_control.on_next(True)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.call_soon(stop_loop)

        driver = stop.make_driver()
        driver.call(stop.Sink(control=stop_control))

        loop.run_forever()
        loop.close()
        self.assertEqual(True, stopped)


    def test_stop_custom_loop_on_item(self):
        stopped = False
        stop_control = Subject()

        def stop_loop():
            nonlocal stopped
            stopped = True
            stop_control.on_next(True)

        loop = asyncio.new_event_loop()
        loop.call_soon(stop_loop)

        driver = stop.make_driver(loop)
        driver.call(stop.Sink(control=stop_control))

        loop.run_forever()
        loop.close()
        self.assertEqual(True, stopped)

    def test_stop_custom_loop_on_completed(self):
            stopped = False
            stop_control = Subject()

            def stop_loop():
                nonlocal stopped
                stopped = True
                stop_control.on_completed()

            loop = asyncio.new_event_loop()
            loop.call_soon(stop_loop)

            driver = stop.make_driver(loop)
            driver.call(stop.Sink(control=stop_control))

            loop.run_forever()
            loop.close()
            self.assertEqual(True, stopped)

    def test_stop_custom_loop_on_error(self):
            stopped = False
            stop_control = Subject()

            def stop_loop():
                nonlocal stopped
                stopped = True
                stop_control.on_error("error")

            loop = asyncio.new_event_loop()
            loop.call_soon(stop_loop)

            driver = stop.make_driver(loop)
            driver.call(stop.Sink(control=stop_control))

            loop.run_forever()
            loop.close()
            self.assertEqual(True, stopped)        