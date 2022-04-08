FROM python:3.9-alpine as builder

ENV DEBIAN_FRONTEND=noninteractive 
ARG DEBIAN_FRONTEND=noninteractive

# Create working directory
RUN mkdir -p /usr/app/ /outputs /static
WORKDIR /usr/app/

COPY . /usr/app/

RUN python3.9 -m pip install --upgrade pip setuptools distlib
RUN python3.9 -m pip install -r requirements.txt

RUN python3.9 setup.py install

RUN python3.9 setup.py sdist && \
    python3.9 -m pip install --no-cache-dir dist/*.tar.gz

ENTRYPOINT []
