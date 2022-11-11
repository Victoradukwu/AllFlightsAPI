FROM python:3.8.3-alpine

RUN apk update && apk add build-base postgresql-dev jpeg-dev zlib-dev

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENTRYPOINT ["sh", "entrypoint.sh"]
