from collections import namedtuple
from cyclotron import Component
import asyncio

Sink = namedtuple('Sink', ['dispose'])


def make_driver(loop=None):
    ''' Returns a dispose driver function. The optional loop argument can be
    provided to use the driver in another loop than the default one.
    '''

    def dispose(i = None):
        if loop is not None:
            loop.stop()
        else:
            asyncio.get_event_loop().stop()

    def driver(sink):
        ''' The dispose driver stops the asyncio event loop as soon as an
        event is received on the dispose stream or when it completes (both
        in case of success or error).

        arguments:
        - sink: A DisposeSink object.
        '''
        sink.dispose.subscribe(
            on_next=dispose,
            on_error=dispose,
            on_completed=dispose)
        return None

    return Component(call=driver, input=Sink)
