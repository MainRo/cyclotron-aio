import asyncio
from cyclotron.rx_runner import setup

def run(main, drivers, source_factory=None, loop = None):

    program = setup(main, drivers, source_factory)
    dispose = program.run()
    loop.run_forever()
    dispose()
