
# pip install aiohttp cchardet aiodns
import os
import aiopg
from aiohttp import web

from handlers import controller, worker

# Manages db access & file copy
# Nginx receives files in tmp -> move to permanent location
# 

# Getting the DB
#     async with aiopg.create_pool(dsn) as pool:
#         async with pool.acquire() as conn:
#             async with conn.cursor() as cur:
#                 await cur.execute("SELECT 1")
#                 ret = []
#                 async for row in cur:
#                     ret.append(row)
#                 assert ret == [(1,)]


async def init_pg(app):
    print("Starting pg")
    conf = app['config']['postgres']
    dsn = 'host={host} dbname={database} user={user}'.format(**conf)
    print(dsn)
    pool = await aiopg.create_pool(
        dsn,
        # minsize=conf['minsize'],
        # maxsize=conf['maxsize'],
        loop=app.loop
    )
    app['db'] = pool


    # Setup an empty table for now

    q = '''
      DROP TABLE IF EXISTS queue CASCADE;
      DROP TABLE IF EXISTS job CASCADE;
      DROP TYPE IF EXISTS job_state;

      CREATE TABLE queue (
        id UUID PRIMARY KEY
      );

      CREATE TYPE job_state AS ENUM ('open', 'claimed', 'working', 'done', 'error');
      CREATE TABLE job (
        id UUID PRIMARY KEY,
        queue UUID REFERENCES queue(id),
        state job_state DEFAULT 'open',
        file_hash BYTEA
      );
    '''

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            assert await cur.execute(q) is None

async def close_pg(app):
    print("Stopping pg")
    app['db'].close()
    await app['db'].wait_closed()
    print("Db stopped")


async def upload_handle(request):
    print("Got request:", request, request.content_type)
    print("Got request:forwarded", request.forwarded)
    print("Got request:headers", request.headers)

    assert request.content_type == 'multipart/form-data'

    print("Not handling multipart right now")
    # reader = await request.multipart()
    
    return web.Response(text='Not handling multipart right now: {}'.format(
        os.path.getsize(request.headers['X-File-Name'])
    ))

    # /!\ Don't forget to validate your inputs /!\

    # reader.next() will `yield` the fields of your form

    # field = await reader.next()
    # print("Got field", field )
    # assert field.name == 'filename'
    # name = await field.read(decode=True)
    # print("Name:", name)
    # field = await reader.next()
    # assert field.name == 'file'
    # filename = field.filename

    # print("Filename:", filename)
    # # You cannot rely on Content-Length if transfer is chunked.
    # size = 0
    # with open(os.path.join('/spool/yarrr-media/mp3/', filename), 'wb') as f:
    #     while True:
    #         chunk = await field.read_chunk()  # 8192 bytes by default.
    #         if not chunk:
    #             break
    #         size += len(chunk)
    #         f.write(chunk)


async def handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name
    return web.Response(text=text)

def setup_handlers(app):

    app.on_startup.append(init_pg)
    app.on_cleanup.append(close_pg)

    app.router.add_get('/', handle)
    app.router.add_post('/upload', upload_handle)

    # Controller
    app.router.add_post('/queue', controller.queue_create)
    app.router.add_post('/queue/{queue_id}', controller.job_create)
    app.router.add_get('/queue/{queue_id}/status', controller.queue_status)

    # Worker
    app.router.add_get('/queue/{queue_id}/job', worker.queue_read)
    app.router.add_get('/queue/{queue_id}/{job_id}', worker.job_read)
    app.router.add_put('/queue/{queue_id}/{job_id}', worker.job_update)
    app.router.add_get('/{name}', handle)