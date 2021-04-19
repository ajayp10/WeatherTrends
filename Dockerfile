FROM python:3

ENV PYTHONUNBUFFERED 1

RUN mkdir /flask

WORKDIR /flask

COPY . /flask/

RUN pip install -r requirements.txt

EXPOSE 5000