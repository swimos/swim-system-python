import asyncio

from swimai.reacon.reacon import Recon
from swimai.structure.structs import Text
from swimai.warp.command_message import CommandMessage
from swimai.warp.sync_request import SyncRequest


async def run():
    # request = CommandMessage('foo/bar', 'info')
    # request1 = SyncRequest('foo/bar', 'info')
    # value = request.to_value()
    # value1 = request1.to_value()
    # t = await asyncio.gather(request.to_recon(), request1.to_recon())
    # print(t[0])
    # print(t[1])

    message = '@synced(node: "foo/bar", lane: "lane/uri/test")'
    t = await asyncio.gather(Recon.parse(message))
    t = t[0]
    # print(await Recon.to_string(value))
    print(await Recon.to_string(t))


if __name__ == '__main__':
    asyncio.run(run())
