# HTTP Queue service

## Image setup: (https://github.com/justanr/aiohttp_docker_webapp)
- Python 3.6
- nginx proxy
- supervisor



- Http service

- controller - job | pre/post processing
  - sets up queue (table)
  - http:
    - GET /queue/{framehash}
      302: redirect -> queue item | 
      410 Gone: queue finished
    - PUT /queue/{framehash}
      201: created
    - create item logic

- worker - job | gets file and starts processing
  - image
  - command -- arguments to configure and point to the service:queue endpoint
  - runs in a loop until the queue is empty



# Queue Description

## Controller

- POST `/queue`
  - request
    - image
    - tasks
  - response
    - id

- POST `/queue/:id`
  - request
    - file
    - filename
    - json

- GET `/queue/:id`
  - response
    - status
    - progress

## Worker
- GET `/queue/:id`
  - response
    - 302:
      location -> item

- PUT `/queue/:id/:job`
  - request
    - progress
    - error
    - result
  - response
    - stop
    - continue
