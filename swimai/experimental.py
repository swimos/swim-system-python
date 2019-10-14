import asyncio

from swimai.reacon.recon import Recon
from swimai.warp.sync_request import SyncRequest


async def run():
    request = SyncRequest('foo/bar', 'info')
    value = request.to_value()
    t = await asyncio.gather(Recon.to_string(value))
    print(t[0])

if __name__ == '__main__':
    asyncio.run(run())
