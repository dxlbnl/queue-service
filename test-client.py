from urllib.parse import urljoin
import yaml

import aiohttp
import asyncio

server_url = 'http://service-web-1.queue.dock'

async def process(method, uri, *args, **kwargs):
    '''Calls the server with the method'''
    response = await method(urljoin(server_url, uri), *args, **kwargs)

    if response.content_type == 'application/json':
        data = await response.json()
        print("###\n{method}: {uri} -> ({status})\n---\n{response}===".format(
            method = method.__name__,
            uri = uri,
            status = response.status,
            content_type = response.content_type,
            response = yaml.dump(data, default_flow_style=False)
        ))
        return data
    else:
        print("{method}: {uri} -> ({status}) [{content_type}]\n\t{response}".format(
            method = method.__name__,
            uri = uri,
            status = response.status,
            content_type = response.content_type,
            response = await response.text()
        ))
        

async def main():
    async with aiohttp.ClientSession() as session:
        # Create a queue
        queue = await process(session.post, 'queue')

        # Create the queue items
        n = 10
        print("Adding {} items to the queue".format(n))
        await asyncio.wait([
            process(session.post, 'queue/{id}'.format(**queue))
            for i in range(n)
        ])

        # Work on the queue items.
        # Get the job
        job = await process(session.get, 'queue/{id}/job'.format(**queue)) # Redirects to queue item
        print('job:', job)
        await process(
            session.put,
            'queue/{queue}/{id}'.format(**job),
            json={
                'success': True
            }
        ) # Job finished

        # Check the queue progress
        await process(session.get, 'queue/{id}/status'.format(**queue))

loop = asyncio.get_event_loop()
loop.run_until_complete(main())