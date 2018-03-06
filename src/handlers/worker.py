import json
from aiohttp import web

###################
# Worker handlers #
###################

async def queue_read(request):
    '''Claim a job and redirect the user to that job'''
    queue_id = request.match_info['queue_id']

    async with request.app['db'].acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                '''
                WITH claimed_job AS (
                    SELECT id
                    FROM job
                    WHERE queue = %(queue_id)s
                    AND state = 'open'
                    LIMIT 1
                    FOR UPDATE SKIP LOCKED
                )
                UPDATE job
                SET state = 'claimed'
                FROM claimed_job
                WHERE job.id = claimed_job.id
                RETURNING job.id;
                ''',
                dict(queue_id=queue_id)
            )

            async for row in cur:
                (job_id, ) = row


            return web.HTTPFound('/queue/{queue_id}/{job_id}'.format(
                queue_id=queue_id,
                job_id=job_id
            ))

    raise web.HTTPInternalServerError(
        text='Could not claim job'
    )

async def job_read(request):
    '''Return the job description'''
    queue_id = request.match_info['queue_id']
    job_id = request.match_info['job_id']

    async with request.app['db'].acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                '''SELECT row_to_json(row)
                    FROM (
                        SELECT *
                        FROM job
                        WHERE queue = %(queue_id)s
                        AND id = %(job_id)s
                    ) row;
                ''',
                dict(
                    queue_id=queue_id,
                    job_id=job_id
                )
            )

            async for row in cur:
                (status, ) = row

            return web.HTTPOk(
                content_type='application/json',
                text=json.dumps(status)
            )

    return web.HTTPOk(
        content_type='application/json',
        text=json.dumps(dict())
    )

async def job_update(request):
    '''Updates job progress, success or error'''

    queue_id = request.match_info['queue_id']
    job_id = request.match_info['job_id']

    assert request.content_type == 'application/json'
    body = await request.json()
    print("Got body:", body)

    async with request.app['db'].acquire() as conn:
        async with conn.cursor() as cur:
            if 'success' in body:
                q = '''
                    UPDATE job
                    SET state = 'done'
                    WHERE queue = %(queue_id)s
                    AND id = %(job_id)s
                    RETURNING 'done';
                '''
            elif 'progress' in body:
                q = '''
                    UPDATE job
                    SET state = 'working'
                    WHERE queue = %(queue_id)s
                    AND id = %(job_id)s
                    RETURNING 'working';
                '''
            elif 'error' in body:
                q = '''
                    UPDATE job
                    SET state = 'error'
                    WHERE queue = %(queue_id)s
                    AND id = %(job_id)s
                    RETURNING 'error';
                '''
            await cur.execute(q,
                dict(
                    queue_id=queue_id,
                    job_id=job_id
                )
            )

            async for row in cur:
                (status, ) = row

            return web.HTTPOk(
                content_type='application/json',
                text=json.dumps({
                    'state': status
                })
            )

    raise web.HTTPInternalServerError(
        text='Error updating job'
    )
