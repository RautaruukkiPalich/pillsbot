FROM python:3-alpine

RUN apk update && apk add libpq
RUN apk update && apk add --virtual .build-deps gcc g++ linux-headers python3-dev \
musl-dev libffi-dev postgresql-dev openssl-dev postgresql-client gettext-dev

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "${HOST_ADD}", "--port", "${HOST_PORT}"]
