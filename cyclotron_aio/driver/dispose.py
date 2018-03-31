from collections import namedtuple
from cyclotron import Component
import asyncio

DisposeSink = namedtuple('DisposeSink', ['dispose'])

def make_dispose_driver(loop=None):
    ''' Returns a dispose driver function. The optional loop argument can be
    provided to use the driver in another loop than the default one.
    '''

    def dispose(i):
        if i is not True:
            return

        if loop is not None:
            loop.stop()
        else:
            asyncio.get_event_loop().stop()

    def dispose_driver(sink):
        ''' The dispose driver stops the asyncio event loop as soon as a True
        event is received on the dispose stream.

        arguments:
        - sink: A DisposeSink object.
        '''
        sink.dispose.subscribe(lambda i: dispose(i))
        return None

    return Component(call=dispose_driver, output=DisposeSink)
