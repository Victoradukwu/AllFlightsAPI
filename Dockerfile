FROM python:3.8.3-alpine

RUN apk update && apk add build-base postgresql-dev jpeg-dev zlib-dev

RUN mkdir /service
WORKDIR /service/src
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY src .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000
ENTRYPOINT ["sh", "entrypoint.sh"]
