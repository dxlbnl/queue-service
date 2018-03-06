import json
import uuid

from aiohttp import web

#######################
# Controller handlers #
#######################
async def queue_create(request):
    # Create a queue, for now no config required :)

    async with request.app['db'].acquire() as conn:
        async with conn.cursor() as cur:
            queue_id = uuid.uuid4()
            await cur.execute(
                'INSERT INTO queue (id) VALUES (%s)',
                (queue_id, )
            )

            return web.HTTPCreated(
                content_type='application/json',
                text=json.dumps(dict(
                    id=queue_id.hex
                ))
            )

    raise web.HTTPInternalServerError(
        content_type='application/json',
        text=json.dumps(dict(
            error='Error creating queue'
        ))
    )

async def job_create(request):
    queue_id = request.match_info['queue_id']

    async with request.app['db'].acquire() as conn:
        async with conn.cursor() as cur:
            job_id = uuid.uuid4()

            await cur.execute(
                '''
                INSERT INTO job (id, queue) 
                VALUES (%(id)s, %(queue)s)''',
                dict(id=job_id, queue=queue_id)
            )

            return web.HTTPCreated(
                content_type='application/json',
                text=json.dumps(dict(
                    queue=queue_id,
                    id=job_id.hex
                ))
            )

    raise web.HTTPInternalServerError(
        content_type='application/json',
        text=json.dumps(dict(
            error='Error creating queue'
        ))
    )

async def queue_status(request):
    queue_id = request.match_info['queue_id']
    async with request.app['db'].acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                '''SELECT json_build_object(
                    'total', (
                        SELECT count(*) FROM job j
                        WHERE j.queue = %(queue_id)s
                    ),
                    'open', (
                        SELECT count(*) FROM job j
                        WHERE j.queue = %(queue_id)s
                        AND j.state = 'open'
                    ),
                    'claimed', (
                        SELECT count(*) FROM job j
                        WHERE j.queue = %(queue_id)s
                        AND j.state = 'claimed'
                    ),
                    'working', (
                        SELECT count(*) FROM job j
                        WHERE j.queue = %(queue_id)s
                        AND j.state = 'working'
                    ),
                    'done', (
                        SELECT count(*) FROM job j
                        WHERE j.queue = %(queue_id)s
                        AND j.state = 'done'
                    ),
                    'error', (
                        SELECT count(*) FROM job j
                        WHERE j.queue = %(queue_id)s
                        AND j.state = 'error'
                    )
                );''',
                dict(
                    queue_id=queue_id
                )
            )

            async for row in cur:
                (status, ) = row

            return web.HTTPOk(
                content_type='application/json',
                text=json.dumps(status)
            )


    raise web.HTTPInternalServerError(
        text='Could not get status'
    )


