FROM python:3.8.3-alpine

RUN apk update && apk add build-base postgresql-dev jpeg-dev zlib-dev

RUN mkdir /service
WORKDIR /service/recommendations
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8100
ENTRYPOINT ["python", "recommendations.py"]
