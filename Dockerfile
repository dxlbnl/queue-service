FROM alpine:latest

ENV PACKAGES " \
  postgresql-client postgresql-dev postgresql-libs \
  nginx \
  bash \
  git \
  python2 python3 python3-dev \
  ffmpeg \
  curl \
  jq \
  gcc \
  musl-dev \
"
RUN apk add --no-cache --update $PACKAGES && rm -rf /var/cache/apk/* \
  && python3 -m ensurepip \
  && python2 -m ensurepip \
  && rm -r /usr/lib/python*/ensurepip \
  && pip3 install --upgrade pip setuptools \
  && pip install --upgrade pip supervisor \
  && rm -r /root/.cache

# For nginx
RUN mkdir -p /run/nginx
EXPOSE 80

RUN mkdir /app
WORKDIR /app

COPY nginx.conf /etc/nginx/nginx.conf
COPY supervisord.conf /etc/supervisord.conf

COPY src/requirements.txt ./
RUN pip3 install -r requirements.txt --no-cache-dir

ADD . /app
RUN chmod +x /app/src/main.py


CMD ["supervisord"]
