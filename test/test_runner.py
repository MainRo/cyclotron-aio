from unittest import TestCase

from collections import namedtuple
from rx import Observable
from cyclotron_aio.runner import run


class RunnerTestCase(TestCase):

    def test_run(self):
        ''' Creates a cycle with one sink driver.
        '''
        '''
        MainDrivers = namedtuple('MainDrivers', ['drv1'])
        MainSink = namedtuple('MainSink', ['drv1'])
        test_values = []

        def drv1(sink):
            sink.values.subscribe(lambda i: test_values.append(i))
            return None
        Drv1Sink = namedtuple('Drv1Sink', ['values'])
        Drv1Driver = Driver(call=drv1, sink=Drv1Sink)

        def main(sources):
            val = Observable.from_([1, 2, 3])
            return MainSink(drv1=Drv1Sink(values=val))

        drivers = MainDrivers(drv1=Drv1Driver)
        run(main, drivers)

        self.assertEqual(3, len(test_values))
        self.assertEqual(1, test_values[0])
        self.assertEqual(2, test_values[1])
        self.assertEqual(3, test_values[2])
        '''
