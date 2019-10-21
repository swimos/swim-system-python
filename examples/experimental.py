import asyncio
from swimai.warp.warp import Envelope


async def run():
    # request = CommandMessage('foo/bar', 'info')
    # request1 = SyncRequest('foo/bar', 'info')
    # value = request.to_value()
    # value1 = request1.to_value()
    # t = await asyncio.gather(request.to_recon(), request1.to_recon())
    # print(t[0])
    # print(t[1])

    message = '@synced(node: "foo/bar", lane: "/uri/test")34'
    # message = '@event(node:"/unit/foo",lane:info)"Hello from Python"'
    requests = await asyncio.gather(Envelope.parse_recon(message))
    request = requests[0]

    texts = await asyncio.gather(request.to_recon())
    print(texts[0])


if __name__ == '__main__':
    asyncio.run(run())
