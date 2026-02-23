FROM python:3.12

RUN pip install uv==0.10.4

COPY ./src /src/
WORKDIR /src

RUN uv sync